import os
import sys
import pandas as pd
import re
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session

# Ensure Hosteva app is on PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Explicitly import all database models so they register on Base
def import_models():
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

import_models()

from app.database import SessionLocal
from app.models.compliance import MunicipalCode, HOARule

COMPLETE_REL = os.path.join("Hosteva Phase III", "Hosteva Jurisdictional Rules DB (Complete).xlsx")
PHASE1_REL = "Hosteva Jurisdictional Rules DB - Florida Counties (Phase 1).xlsx"
HOA_V5_REL = "Hosteva HOA STR Rules Database (Complete v5).xlsx"
HOA_POC_REL = "Hosteva HOA STR Rules POC Database.xlsx"


def parse_days(val):
    if pd.isna(val) or not isinstance(val, str):
        return None
    val_lower = val.lower()
    match = re.search(r'(\d+(?:\.\d+)?)\s*(?:night|day)', val_lower)
    if match:
        return int(float(match.group(1)))
    match_months = re.search(r'(\d+(?:\.\d+)?)\s*month', val_lower)
    if match_months:
        months = float(match_months.group(1))
        return int(months * 30)
    return None


def parse_max_occupancy(val):
    if pd.isna(val) or not isinstance(val, str):
        return None
    val_lower = val.lower()
    match = re.search(r'(?:max|limit of)\s*(\d+(?:\.\d+)?)', val_lower)
    if match:
        return int(float(match.group(1)))
    return None


def parse_tax_rate(val):
    if pd.isna(val) or not isinstance(val, str):
        return None
    match = re.search(r'(\d+(?:\.\d+)?)\s*%', val)
    if match:
        return float(match.group(1))
    return None


def parse_date(val):
    if pd.isna(val):
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, pd.Timestamp):
        return val.date()
    if isinstance(val, str):
        try:
            return datetime.strptime(val.strip(), "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def resolve_jurisdictional_file(excel_dir: str):
    """Prefer Drive Complete.xlsx when present; else Phase 1 FL sheet."""
    candidates = [
        os.path.join(excel_dir, COMPLETE_REL),
        os.path.abspath(os.path.join(excel_dir, "..", COMPLETE_REL)),
        os.path.join(excel_dir, PHASE1_REL),
    ]
    for path in candidates:
        if os.path.exists(path):
            is_complete = os.path.basename(path).endswith("(Complete).xlsx") or "Complete).xlsx" in path
            return path, is_complete
    return None, False


def complete_xlsx_present(excel_dir: str) -> bool:
    path, is_complete = resolve_jurisdictional_file(excel_dir)
    return bool(path and is_complete)


def resolve_hoa_file(excel_dir: str):
    """Prefer HOA Complete v5 over POC (SP-013)."""
    for rel in (HOA_V5_REL, HOA_POC_REL):
        path = os.path.join(excel_dir, rel)
        if os.path.exists(path):
            return path, "v5" if "Complete v5" in rel else "poc"
    return None, None


def _set_source_kind(obj, kind: str):
    if hasattr(obj, "source_kind"):
        obj.source_kind = kind


def seed_rules(db: Session, excel_dir: str):
    """
    Upsert municipal + HOA rules from Drive/repo Excel.

    SP-010: Prefer Complete.xlsx; import ALL states present in Complete.
    Covered / curated Free Audit gate remains FL-only at runtime — non-FL rows
    are Thin/research seed (is_expert_verified=False, source_kind=excel_seed).
    SP-013: Prefer HOA Complete v5; assistive only.
    """
    print("Starting rules database seeding...")
    stats = {
        "municipal_inserted": 0,
        "municipal_updated": 0,
        "municipal_fl": 0,
        "municipal_non_fl": 0,
        "municipal_skipped": 0,
        "hoa_inserted": 0,
        "hoa_updated": 0,
        "hoa_skipped": 0,
        "source_file": None,
        "is_complete": False,
        "hoa_source": None,
    }

    target_file, is_complete = resolve_jurisdictional_file(excel_dir)
    stats["source_file"] = target_file
    stats["is_complete"] = is_complete

    if target_file and os.path.exists(target_file):
        print(f"Reading jurisdictional rules from {target_file} (is_complete={is_complete})...")
        df_jur = pd.read_excel(target_file)
        seen_mc = {}

        for _, row in df_jur.iterrows():
            jur_name = str(row['Jurisdiction Name']).strip() if not pd.isna(row.get('Jurisdiction Name', row.iloc[0] if len(row) else None)) else None
            if 'Jurisdiction Name' in row.index:
                jur_name = str(row['Jurisdiction Name']).strip() if not pd.isna(row['Jurisdiction Name']) else None
            jur_type = str(row['Jurisdiction Type']).strip() if not pd.isna(row['Jurisdiction Type']) else None

            if not jur_name or not jur_type or jur_name.lower() in ("nan", "none"):
                stats["municipal_skipped"] += 1
                continue

            # Complete has State column; Phase 1 is FL-only (hardcode).
            if is_complete and 'State' in row.index and not pd.isna(row['State']):
                state = str(row['State']).strip().upper()
            else:
                state = "FL"

            if not state or state in ("NAN", "NONE", ""):
                stats["municipal_skipped"] += 1
                continue

            key = (jur_name.lower(), jur_type.lower(), state.lower())
            is_fl = state == "FL"

            str_permitted_raw = str(row['STR Permitted?']).strip() if not pd.isna(row['STR Permitted?']) else None
            permit_req_raw = str(row['Permit/License Required?']).strip() if not pd.isna(row['Permit/License Required?']) else None
            min_stay_raw = str(row['Minimum Stay Requirement']).strip() if not pd.isna(row['Minimum Stay Requirement']) else None
            occ_limits_raw = str(row['Occupancy Limits']).strip() if not pd.isna(row['Occupancy Limits']) else None

            if is_complete:
                tot_rate = row.get('Transient Occupancy Tax Rate')
                one_time = row.get('One-Time Registration Fee')
                annual = row.get('Annual Renewal Fee')

                tot_pct = 0.0
                if not pd.isna(tot_rate):
                    if isinstance(tot_rate, (int, float)):
                        # Sheet often stores 0.06 style fractions OR already-percent ints
                        tot_pct = float(tot_rate) * 100 if float(tot_rate) <= 1.0 else float(tot_rate)
                    else:
                        parsed = parse_tax_rate(str(tot_rate))
                        if parsed is not None:
                            tot_pct = parsed
                        else:
                            match = re.search(r'(\d+(?:\.\d+)?)', str(tot_rate))
                            if match:
                                tot_pct = float(match.group(1))

                one_time_val = one_time if not pd.isna(one_time) else 0
                annual_val = annual if not pd.isna(annual) else 0
                tax_rate_raw = f"Tax: {str(tot_rate).strip()}, Registration: ${one_time_val}, Renewal: ${annual_val}"
                tax_val = tot_pct
            else:
                tax_rate_raw = str(row['Tax Rate / Registration Fee']).strip() if not pd.isna(row['Tax Rate / Registration Fee']) else None
                tax_val = parse_tax_rate(tax_rate_raw)

            src_url = str(row['Source URL']).strip() if not pd.isna(row['Source URL']) else None
            last_ver = parse_date(row['Last Verified Date'])

            is_allowed = True
            str_prohibited = False
            if str_permitted_raw:
                low = str_permitted_raw.lower()
                if "banned" in low or "prohibited" in low or ("no" in low and "permitted" in low):
                    is_allowed = False
                    str_prohibited = True

            requires_permit = False
            if permit_req_raw and "yes" in permit_req_raw.lower():
                requires_permit = True

            stay_days = parse_days(min_stay_raw)
            max_occ = parse_max_occupancy(occ_limits_raw)

            # FL Complete/Phase1: expert_verified spreadsheet seed for Covered gate.
            # Non-FL Complete: Thin/research seed — never Covered until Curated pack.
            expert_verified = bool(is_fl)
            source_kind = "excel_seed"

            existing = seen_mc.get(key)
            if not existing:
                existing = db.query(MunicipalCode).filter(
                    func.lower(MunicipalCode.municipality_name) == jur_name.lower(),
                    func.lower(MunicipalCode.jurisdiction_type) == jur_type.lower(),
                    func.lower(MunicipalCode.state) == state.lower()
                ).first()

            if existing:
                existing.str_prohibited = str_prohibited
                existing.is_allowed = is_allowed
                existing.requires_permit = requires_permit
                existing.stay_restriction_days = stay_days
                existing.max_occupancy_limit = max_occ
                existing.tax_rate = tax_val
                existing.source_url = src_url
                existing.str_permitted_raw = str_permitted_raw
                existing.permit_required_raw = permit_req_raw
                existing.minimum_stay_requirement = min_stay_raw
                existing.occupancy_limits = occ_limits_raw
                existing.tax_rate_registration_fee = tax_rate_raw
                existing.last_verified_date = last_ver
                existing.state = state
                # Denser Complete wins: always refresh verification flags from this pass
                existing.is_expert_verified = expert_verified
                existing.is_ai_scraped = False
                _set_source_kind(existing, source_kind)
                seen_mc[key] = existing
                stats["municipal_updated"] += 1
            else:
                new_mc = MunicipalCode(
                    municipality_name=jur_name,
                    jurisdiction_type=jur_type,
                    ordinance_number="JURISDICTION-RULES",
                    str_prohibited=str_prohibited,
                    is_allowed=is_allowed,
                    requires_permit=requires_permit,
                    stay_restriction_days=stay_days,
                    max_occupancy_limit=max_occ,
                    tax_rate=tax_val,
                    source_url=src_url,
                    str_permitted_raw=str_permitted_raw,
                    permit_required_raw=permit_req_raw,
                    minimum_stay_requirement=min_stay_raw,
                    occupancy_limits=occ_limits_raw,
                    tax_rate_registration_fee=tax_rate_raw,
                    last_verified_date=last_ver,
                    state=state,
                    is_ai_scraped=False,
                    is_expert_verified=expert_verified,
                )
                _set_source_kind(new_mc, source_kind)
                db.add(new_mc)
                seen_mc[key] = new_mc
                stats["municipal_inserted"] += 1

            if is_fl:
                stats["municipal_fl"] += 1
            else:
                stats["municipal_non_fl"] += 1

        db.commit()
        print(
            f"Jurisdictional rules seeding completed: "
            f"{stats['municipal_inserted']} inserted, {stats['municipal_updated']} updated "
            f"(FL keys={stats['municipal_fl']}, non-FL keys={stats['municipal_non_fl']})."
        )
    else:
        print("Jurisdictional rules file not found")

    # 2. Seed HOA Rules (assistive only — never elevates Covered)
    hoa_file, hoa_kind = resolve_hoa_file(excel_dir)
    stats["hoa_source"] = hoa_file
    if hoa_file:
        print(f"Reading HOA rules from {hoa_file} (kind={hoa_kind})...")
        df_hoa = pd.read_excel(hoa_file)
        seen_hoa = {}

        for _, row in df_hoa.iterrows():
            hoa_name = str(row['HOA Name']).strip() if not pd.isna(row['HOA Name']) else None
            location = str(row['Location (City/County)']).strip() if not pd.isna(row['Location (City/County)']) else None

            if not hoa_name or not location or hoa_name.lower() in ("nan", "none"):
                stats["hoa_skipped"] += 1
                continue

            key = (hoa_name.lower(), location.lower())
            str_permitted = str(row['STR Permitted?']).strip() if not pd.isna(row['STR Permitted?']) else "Restricted"
            min_lease = str(row['Minimum Lease/Stay']).strip() if not pd.isna(row['Minimum Lease/Stay']) else None
            rules_avail_raw = str(row['Rules Available Y/N']).strip() if not pd.isna(row['Rules Available Y/N']) else "No"
            website = str(row['Official Website']).strip() if not pd.isna(row['Official Website']) else None
            last_conf = parse_date(row['Last Confirmed Date'])
            notes = str(row['Key Rules & STR Restrictions (Notes)']).strip() if not pd.isna(row['Key Rules & STR Restrictions (Notes)']) else None

            rules_available = True
            if "no" in rules_avail_raw.lower():
                rules_available = False

            existing = seen_hoa.get(key)
            if not existing:
                existing = db.query(HOARule).filter(
                    func.lower(HOARule.hoa_name) == hoa_name.lower(),
                    func.lower(HOARule.location) == location.lower()
                ).first()

            if existing:
                existing.str_permitted = str_permitted
                existing.minimum_lease_stay = min_lease
                existing.rules_available = rules_available
                existing.official_website = website
                existing.last_confirmed_date = last_conf
                existing.key_rules_notes = notes
                seen_hoa[key] = existing
                stats["hoa_updated"] += 1
            else:
                new_hoa = HOARule(
                    hoa_name=hoa_name,
                    location=location,
                    str_permitted=str_permitted,
                    minimum_lease_stay=min_lease,
                    rules_available=rules_available,
                    official_website=website,
                    last_confirmed_date=last_conf,
                    key_rules_notes=notes
                )
                db.add(new_hoa)
                seen_hoa[key] = new_hoa
                stats["hoa_inserted"] += 1

        db.commit()
        print(
            f"HOA rules seeding completed: {stats['hoa_inserted']} inserted, "
            f"{stats['hoa_updated']} updated (skipped empty={stats['hoa_skipped']})."
        )
    else:
        print("HOA rules file not found")

    return stats


if __name__ == "__main__":
    db = SessionLocal()
    excel_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    try:
        seed_rules(db, excel_dir)
    finally:
        db.close()
