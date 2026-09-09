import os
import sys
import traceback

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

# Ensure Hosteva app is on PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def import_models():
    # Explicitly import all database models so they register on Base and relationships are mapped
    import app.db_models
    import app.models.memory
    import app.models.host
    import app.models.property
    import app.models.zoning
    import app.models.job
    import app.models.compliance
    import app.models.swarm
    import app.models.oauth

# Run import mapping
import_models()

from app.database import SessionLocal
from app.models.compliance import MunicipalCode

# SP-012 / Richard Tampa Bay GO: Curated marketing must-list jurisdictions.
# PCB city is absent from Complete.xlsx — this pack is the Curated source for PCB.
# Broward may exist as FL seed but is NOT Tampa Bay marketing.
# Runtime SoT is app.services.curated_coverage.FL_CURATED_ALLOWLIST (Option B).
# This set is the corridor/pack names this seed script reinforces.
# PL-13 / US-021: Pasco Tax Registration primary (Tourist Express). Not DR-15 PDF.
PASCO_TAX_REGISTRATION_URL = "https://pasco.county-taxes.com/tourist"
PASCO_TAX_INFO_URL = "https://www.pascotaxes.com/taxes/tdt/"  # info-only secondary; not primary
PASCO_MUNICIPAL_SOURCE_URL = "https://www.pascocountyfl.gov/"
DR15_TDT_PDF_URL = "https://floridarevenue.com/Forms_library/current/dr15tdt.pdf"

CURATED_NAMES = {
    "Tampa",
    "St. Petersburg",
    "City of St. Petersburg",
    "Clearwater",
    "Hillsborough County",
    "Pinellas County",
    "Pasco County",
    "Panama City Beach",
    "Bay County",
    "Kissimmee",
    "Orlando",
}


def _norm(value):
    return (value or "").strip().lower()


def _is_pasco_county(rule):
    return _norm(rule.get("municipality_name")) == "pasco county"


def _is_county_fl(rule):
    state = _norm(rule.get("state") or "FL")
    return _norm(rule.get("jurisdiction_type")) == "county" and state in {"fl", "florida"}


def _name_filter(name):
    return func.lower(MunicipalCode.municipality_name) == _norm(name)


def find_existing_municipal_code(db, rule):
    """Match an existing municipal row without inserting a duplicate name+type.

    Order:
    1. municipality_name + ordinance_number
    2. municipality_name + jurisdiction_type + state (NULL/blank state treated as FL)
    3. municipality_name alone for County FL (prod Pasco is JURISDICTION-RULES)
    """
    name = rule["municipality_name"]
    ordinance = rule.get("ordinance_number")
    jtype = rule.get("jurisdiction_type")
    state = (rule.get("state") or "FL").strip() or "FL"

    if ordinance:
        existing = db.query(MunicipalCode).filter(
            _name_filter(name),
            MunicipalCode.ordinance_number == ordinance,
        ).first()
        if existing:
            return existing

    if jtype:
        existing = db.query(MunicipalCode).filter(
            _name_filter(name),
            func.lower(func.coalesce(MunicipalCode.jurisdiction_type, "")) == _norm(jtype),
            func.lower(func.coalesce(MunicipalCode.state, "FL")) == state.lower(),
        ).first()
        if existing:
            return existing

    if _is_county_fl(rule):
        existing = db.query(MunicipalCode).filter(_name_filter(name)).first()
        if existing:
            return existing

    return None


def find_existing_by_name(db, rule):
    return db.query(MunicipalCode).filter(_name_filter(rule["municipality_name"])).first()


def apply_pack_update(existing, rule):
    """Apply pack fields. Pasco tax-only live rows only get URL / soft updates."""
    if rule.get("source_url"):
        existing.source_url = rule["source_url"]
    if "tax_registration_url" in rule:
        existing.tax_registration_url = rule.get("tax_registration_url")
    if rule.get("state") and not (existing.state or "").strip():
        existing.state = rule["state"]
    if rule.get("jurisdiction_type") and not (existing.jurisdiction_type or "").strip():
        existing.jurisdiction_type = rule["jurisdiction_type"]
    existing.is_ai_scraped = False
    if rule.get("is_expert_verified") is not None:
        existing.is_expert_verified = rule["is_expert_verified"]
    if rule.get("source_kind") and hasattr(existing, "source_kind"):
        existing.source_kind = rule["source_kind"]

    pack_requires_permit = bool(rule.get("requires_permit"))
    existing_is_tax_only = existing.requires_permit is False
    if _is_pasco_county(rule) and existing_is_tax_only and pack_requires_permit:
        print(
            f"Soft-updated Pasco County URLs only "
            f"(preserving tax-only live row {existing.ordinance_number})"
        )
        return "soft"

    existing.str_prohibited = rule["str_prohibited"]
    existing.stay_restriction_days = rule["stay_restriction_days"]
    existing.max_rentals_per_year = rule["max_rentals_per_year"]
    existing.requires_permit = rule["requires_permit"]
    existing.permit_name = rule["permit_name"]
    existing.tax_rate = rule["tax_rate"]
    if rule.get("is_allowed") is not None:
        existing.is_allowed = rule["is_allowed"]
    elif rule.get("str_prohibited"):
        existing.is_allowed = False
    if rule.get("jurisdiction_type"):
        existing.jurisdiction_type = rule["jurisdiction_type"]
    if rule.get("state"):
        existing.state = rule["state"]
    return "full"


def _new_municipal_record(rule):
    return MunicipalCode(
        municipality_name=rule["municipality_name"],
        ordinance_number=rule["ordinance_number"],
        str_prohibited=rule["str_prohibited"],
        stay_restriction_days=rule["stay_restriction_days"],
        max_rentals_per_year=rule["max_rentals_per_year"],
        requires_permit=rule["requires_permit"],
        permit_name=rule["permit_name"],
        source_url=rule["source_url"],
        tax_registration_url=rule.get("tax_registration_url"),
        tax_rate=rule["tax_rate"],
        jurisdiction_type=rule.get("jurisdiction_type"),
        state=rule.get("state") or "FL",
        is_ai_scraped=False,
        is_expert_verified=bool(rule.get("is_expert_verified")),
        source_kind=rule.get("source_kind") or "manual_pack",
        is_allowed=False if rule.get("str_prohibited") else True,
    )


def upsert_one_municipal_rule(db, rule):
    """Upsert a single pack rule. Never inserts a second same-name County FL row."""
    existing = find_existing_municipal_code(db, rule)
    if existing:
        apply_pack_update(existing, rule)
        return "updated"

    try:
        # Savepoint so UniqueViolation does not abort the rest of the pack.
        with db.begin_nested():
            db.add(_new_municipal_record(rule))
            db.flush()
        return "seeded"
    except IntegrityError:
        existing = find_existing_municipal_code(db, rule) or find_existing_by_name(db, rule)
        if existing:
            apply_pack_update(existing, rule)
            return "updated"
        raise


def seed_tampa_bay_rules():
    db = SessionLocal()
    try:
        print("Starting Tampa Bay / corridor Curated pack seeding...")

        rules = [
            {
                "municipality_name": "State of Florida",
                "ordinance_number": "FL-STATE-LICENSE",
                "str_prohibited": False,
                "requires_permit": True,
                "permit_name": "DBPR Vacation Rental License (Dwelling or Condominium)",
                "source_url": "https://www.myfloridalicense.com/DBPR/hotels-restaurants/vacation-rentals/",
                "stay_restriction_days": None,
                "max_rentals_per_year": None,
                "tax_rate": None,
                "jurisdiction_type": "State",
                "state": "FL",
                "is_expert_verified": False,  # state row never elevates city Covered alone
                "source_kind": "manual_pack",
            },
            {
                "municipality_name": "Tampa",
                "ordinance_number": "TAMPA-STR",
                "str_prohibited": False,
                "requires_permit": True,
                "permit_name": "Tampa STR Registration / Zoning Review",
                "source_url": "https://www.tampa.gov/",
                "stay_restriction_days": None,
                "max_rentals_per_year": None,
                "tax_rate": None,
                "jurisdiction_type": "City",
                "state": "FL",
                "is_expert_verified": True,
                "source_kind": "manual_pack",
            },
            {
                "municipality_name": "Hillsborough County",
                "ordinance_number": "HILLSBOROUGH-MIN-STAY",
                "str_prohibited": False,
                "stay_restriction_days": 7,
                "tax_rate": 6.0,
                "source_url": "https://www.hillsboroughcounty.org/",
                "requires_permit": False,
                "permit_name": None,
                "max_rentals_per_year": None,
                "jurisdiction_type": "County",
                "state": "FL",
                "is_expert_verified": True,
                "source_kind": "manual_pack",
            },
            {
                "municipality_name": "St. Petersburg",
                "ordinance_number": "ST-PETE-FREQ-LIMIT",
                "str_prohibited": False,
                "max_rentals_per_year": 3,
                "source_url": "https://www.stpete.org/business/planning___zoning/zoning.php",
                "stay_restriction_days": None,
                "tax_rate": None,
                "requires_permit": False,
                "permit_name": None,
                "jurisdiction_type": "City",
                "state": "FL",
                "is_expert_verified": True,
                "source_kind": "manual_pack",
            },
            {
                "municipality_name": "City of St. Petersburg",
                "ordinance_number": "ST-PETE-FREQ-LIMIT",
                "str_prohibited": False,
                "max_rentals_per_year": 3,
                "source_url": "https://www.stpete.org/business/planning___zoning/zoning.php",
                "stay_restriction_days": None,
                "tax_rate": None,
                "requires_permit": False,
                "permit_name": None,
                "jurisdiction_type": "City",
                "state": "FL",
                "is_expert_verified": True,
                "source_kind": "manual_pack",
            },
            {
                "municipality_name": "Clearwater",
                "ordinance_number": "CLEARWATER-STR",
                "str_prohibited": False,
                "requires_permit": True,
                "permit_name": "Clearwater STR Registration",
                "source_url": "https://www.myclearwater.com/",
                "stay_restriction_days": None,
                "max_rentals_per_year": None,
                "tax_rate": None,
                "jurisdiction_type": "City",
                "state": "FL",
                "is_expert_verified": True,
                "source_kind": "manual_pack",
            },
            {
                "municipality_name": "Pinellas County",
                "ordinance_number": "PINELLAS-TDT",
                "str_prohibited": False,
                "requires_permit": False,
                "permit_name": None,
                "tax_rate": 6.0,
                "source_url": "https://www.pinellastaxcollector.gov/",
                "stay_restriction_days": None,
                "max_rentals_per_year": None,
                "jurisdiction_type": "County",
                "state": "FL",
                "is_expert_verified": True,
                "source_kind": "manual_pack",
            },
            {
                # PL-13 / US-021 / TE-013: municipal ordinance ≠ tax registration.
                # Oak Drive (10703 Oak Drive, Hudson, FL 34667) Tax Registration
                # primary = Tourist Express. Do not use DR-15 PDF as tax or muni URL.
                # Info-only secondary (not primary): https://www.pascotaxes.com/taxes/tdt/
                # Control address reality: ALLOWED_WITH_CHECKLIST tax-only
                # (requires_permit false, tax_rate 5.0). Do not force CUP onto a
                # live JURISDICTION-RULES row that is already tax-only.
                "municipality_name": "Pasco County",
                "ordinance_number": "PASCO-PERMIT-REQ",
                "str_prohibited": False,
                "requires_permit": False,
                "permit_name": None,
                "tax_rate": 5.0,
                "source_url": PASCO_MUNICIPAL_SOURCE_URL,
                "tax_registration_url": PASCO_TAX_REGISTRATION_URL,
                "stay_restriction_days": None,
                "max_rentals_per_year": None,
                "jurisdiction_type": "County",
                "state": "FL",
                "is_expert_verified": True,
                "source_kind": "manual_pack",
            },
            # US-003 / SP-001 UAT covered localities (official .gov / municipal)
            {
                "municipality_name": "Bay County",
                "ordinance_number": "BAY-STR-INSPECT",
                "str_prohibited": False,
                "requires_permit": True,
                "permit_name": "Short-Term Vacation Rental Inspection",
                "tax_rate": 5.0,
                "source_url": "https://www.baycountyfl.gov/783/Short-Term-Vacation-Rental-Inspections",
                "stay_restriction_days": None,
                "max_rentals_per_year": None,
                "jurisdiction_type": "County",
                "state": "FL",
                "is_expert_verified": True,
                "source_kind": "manual_pack",
            },
            {
                # Present in Complete / pack — NOT Tampa Bay marketing (COVERAGE_COPY §1.2)
                "municipality_name": "Broward County",
                "ordinance_number": "BROWARD-RRC",
                "str_prohibited": False,
                "requires_permit": True,
                "permit_name": "Residential Rental Certificate",
                "tax_rate": None,
                "source_url": "https://www.broward.org/Planning/CodeEnforcement/Pages/ResRentCert.aspx",
                "stay_restriction_days": None,
                "max_rentals_per_year": None,
                "jurisdiction_type": "County",
                "state": "FL",
                "is_expert_verified": True,
                "source_kind": "manual_pack",
            },
            {
                # Absent from Complete.xlsx — Curated source of truth for PCB city
                "municipality_name": "Panama City Beach",
                "ordinance_number": "PCB-STR",
                "str_prohibited": False,
                "requires_permit": True,
                "permit_name": "Panama City Beach STR Registration",
                "tax_rate": None,
                "source_url": "https://www.pcbfl.gov/",
                "stay_restriction_days": None,
                "max_rentals_per_year": None,
                "jurisdiction_type": "City",
                "state": "FL",
                "is_expert_verified": True,
                "source_kind": "manual_pack",
            },
            {
                "municipality_name": "Kissimmee",
                "ordinance_number": "KISS-STR-ZONE",
                "str_prohibited": False,
                "requires_permit": True,
                "permit_name": "Kissimmee STR Zoning / Registration",
                "tax_rate": None,
                "source_url": "https://www.kissimmee.gov/",
                "stay_restriction_days": None,
                "max_rentals_per_year": None,
                "jurisdiction_type": "City",
                "state": "FL",
                "is_expert_verified": True,
                "source_kind": "manual_pack",
            },
            {
                "municipality_name": "Orlando",
                "ordinance_number": "ORL-HOME-SHARE",
                "str_prohibited": False,
                "requires_permit": True,
                "permit_name": "Orlando Home-Sharing Registration",
                "tax_rate": 6.0,
                "source_url": "https://www.orlando.gov/Initiatives/Home-Sharing-Registration",
                "stay_restriction_days": None,
                "max_rentals_per_year": None,
                "jurisdiction_type": "City",
                "state": "FL",
                "is_expert_verified": True,
                "source_kind": "manual_pack",
            },

        ]

        seeded_count = 0
        updated_count = 0
        skipped_count = 0

        for rule in rules:
            name = rule["municipality_name"]
            ordinance = rule["ordinance_number"]
            try:
                # Per-municipality savepoint: one UniqueViolation must not
                # roll back Tampa / PCB / the rest of the pack.
                with db.begin_nested():
                    result = upsert_one_municipal_rule(db, rule)
                if result == "seeded":
                    seeded_count += 1
                    print(f"Seeded new MunicipalCode: {name} ({ordinance})")
                else:
                    updated_count += 1
                    print(f"Updated existing MunicipalCode: {name} ({ordinance})")
            except Exception as e:
                skipped_count += 1
                print(f"Warning: skipped {name} ({ordinance}): {e}")
                traceback.print_exc()

        db.commit()
        print("\n--- Seeding Completed Successfully ---")
        print(f"New records seeded: {seeded_count}")
        print(f"Records updated: {updated_count}")
        print(f"Records skipped: {skipped_count}")
        print(f"Curated must-list names reinforced: {sorted(CURATED_NAMES)}")
        print("--------------------------------------\n")

    except Exception as e:
        db.rollback()
        print(f"Error seeding Tampa Bay rules: {e}")
        traceback.print_exc()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_tampa_bay_rules()
