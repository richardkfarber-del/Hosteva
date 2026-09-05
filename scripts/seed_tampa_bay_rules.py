import os
import sys

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
    import app.integrations.ota_models

# Run import mapping
import_models()

from app.database import SessionLocal
from app.models.compliance import MunicipalCode

def seed_tampa_bay_rules():
    db = SessionLocal()
    try:
        print("Starting Tampa Bay area compliance rules seeding...")

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
            },
            {
                "municipality_name": "Pasco County",
                "ordinance_number": "PASCO-PERMIT-REQ",
                "str_prohibited": False,
                "requires_permit": True,
                "permit_name": "Conditional Use Permit (CUP)",
                "tax_rate": 4.0,
                "source_url": "https://floridarevenue.com/Forms_library/current/dr15tdt.pdf",
                "stay_restriction_days": None,
                "max_rentals_per_year": None,
                "jurisdiction_type": "County",
                "state": "FL",
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
            },
            {
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
            },
            {
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
            },
        ]

        seeded_count = 0
        updated_count = 0

        for rule in rules:
            # Query for existing record based on municipality_name and ordinance_number
            existing = db.query(MunicipalCode).filter_by(
                municipality_name=rule["municipality_name"],
                ordinance_number=rule["ordinance_number"]
            ).first()

            if existing:
                # Update attributes (UPSERT behavior)
                existing.str_prohibited = rule["str_prohibited"]
                existing.stay_restriction_days = rule["stay_restriction_days"]
                existing.max_rentals_per_year = rule["max_rentals_per_year"]
                existing.requires_permit = rule["requires_permit"]
                existing.permit_name = rule["permit_name"]
                existing.source_url = rule["source_url"]
                if rule.get("jurisdiction_type"):
                    existing.jurisdiction_type = rule["jurisdiction_type"]
                if rule.get("state"):
                    existing.state = rule["state"]
                if rule.get("is_allowed") is not None:
                    existing.is_allowed = rule["is_allowed"]
                elif rule.get("str_prohibited"):
                    existing.is_allowed = False
                existing.tax_rate = rule["tax_rate"]
                updated_count += 1
                print(f"Updated existing MunicipalCode: {rule['municipality_name']} ({rule['ordinance_number']})")
            else:
                # Create a new record
                new_record = MunicipalCode(
                    municipality_name=rule["municipality_name"],
                    ordinance_number=rule["ordinance_number"],
                    str_prohibited=rule["str_prohibited"],
                    stay_restriction_days=rule["stay_restriction_days"],
                    max_rentals_per_year=rule["max_rentals_per_year"],
                    requires_permit=rule["requires_permit"],
                    permit_name=rule["permit_name"],
                    source_url=rule["source_url"],
                    tax_rate=rule["tax_rate"]
                )
                db.add(new_record)
                seeded_count += 1
                print(f"Seeded new MunicipalCode: {rule['municipality_name']} ({rule['ordinance_number']})")

        db.commit()
        print("\n--- Seeding Completed Successfully ---")
        print(f"New records seeded: {seeded_count}")
        print(f"Records updated: {updated_count}")
        print("--------------------------------------\n")

    except Exception as e:
        db.rollback()
        print(f"Error seeding Tampa Bay rules: {e}")
        import traceback
        traceback.print_exc()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_tampa_bay_rules()
