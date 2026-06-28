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

def parse_days(val):
    if pd.isna(val) or not isinstance(val, str):
        return None
    val_lower = val.lower()
    # Check for nights/days
    match = re.search(r'(\d+(?:\.\d+)?)\s*(?:night|day)', val_lower)
    if match:
        return int(float(match.group(1)))
    # Check for months
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

def seed_rules(db: Session, excel_dir: str):
    print("Starting rules database seeding...")
    
    # 1. Seed Jurisdictional Rules
    phase3_file = os.path.join(excel_dir, "Hosteva Phase III", "Hosteva Jurisdictional Rules DB (Complete).xlsx")
    jurisdictions_file = os.path.join(excel_dir, "Hosteva Jurisdictional Rules DB - Florida Counties (Phase 1).xlsx")
    
    target_file = None
    is_phase3 = False
    if os.path.exists(phase3_file):
        target_file = phase3_file
        is_phase3 = True
    elif os.path.exists(jurisdictions_file):
        target_file = jurisdictions_file
    else:
        # Try parent directory relative check just in case
        parent_phase3 = os.path.abspath(os.path.join(excel_dir, "..", "Hosteva Phase III", "Hosteva Jurisdictional Rules DB (Complete).xlsx"))
        if os.path.exists(parent_phase3):
            target_file = parent_phase3
            is_phase3 = True

    if target_file and os.path.exists(target_file):
        print(f"Reading jurisdictional rules from {target_file} (is_phase3={is_phase3})...")
        df_jur = pd.read_excel(target_file)
        jur_inserted = 0
        jur_updated = 0
        
        seen_mc = {}
        
        for _, row in df_jur.iterrows():
            jur_name = str(row['Jurisdiction Name']).strip() if not pd.isna(row['Jurisdiction Name']) else None
            jur_type = str(row['Jurisdiction Type']).strip() if not pd.isna(row['Jurisdiction Type']) else None
            
            if not jur_name or not jur_type:
                continue
                
            state = "FL"
            if is_phase3:
                state = str(row['State']).strip() if not pd.isna(row['State']) else "FL"
                
            key = (jur_name.lower(), jur_type.lower(), state.lower())
            
            str_permitted_raw = str(row['STR Permitted?']).strip() if not pd.isna(row['STR Permitted?']) else None
            permit_req_raw = str(row['Permit/License Required?']).strip() if not pd.isna(row['Permit/License Required?']) else None
            min_stay_raw = str(row['Minimum Stay Requirement']).strip() if not pd.isna(row['Minimum Stay Requirement']) else None
            occ_limits_raw = str(row['Occupancy Limits']).strip() if not pd.isna(row['Occupancy Limits']) else None
            
            if is_phase3:
                tot_rate = row.get('Transient Occupancy Tax Rate')
                one_time = row.get('One-Time Registration Fee')
                annual = row.get('Annual Renewal Fee')
                
                tot_pct = 0.0
                if not pd.isna(tot_rate):
                    if isinstance(tot_rate, (int, float)):
                        tot_pct = float(tot_rate) * 100
                    else:
                        # Extract percentage using regex
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
            
            # Map logical attributes
            is_allowed = True
            str_prohibited = False
            if str_permitted_raw:
                if "banned" in str_permitted_raw.lower() or "prohibited" in str_permitted_raw.lower() or ("no" in str_permitted_raw.lower() and "permitted" in str_permitted_raw.lower()):
                    is_allowed = False
                    str_prohibited = True
                    
            requires_permit = False
            if permit_req_raw:
                if "yes" in permit_req_raw.lower():
                    requires_permit = True
                    
            stay_days = parse_days(min_stay_raw)
            max_occ = parse_max_occupancy(occ_limits_raw)
            
            # Query in-memory dict first
            existing = seen_mc.get(key)
            if not existing:
                # Query database
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
                
                seen_mc[key] = existing
                jur_updated += 1
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
                    is_expert_verified=True
                )
                db.add(new_mc)
                seen_mc[key] = new_mc
                jur_inserted += 1
                
        db.commit()
        print(f"Jurisdictional rules seeding completed: {jur_inserted} inserted, {jur_updated} updated.")
    else:
        print(f"Jurisdictional rules file not found")
        
    # 2. Seed HOA Rules
    hoa_file = os.path.join(excel_dir, "Hosteva HOA STR Rules POC Database.xlsx")
    if os.path.exists(hoa_file):
        print(f"Reading HOA rules from {hoa_file}...")
        df_hoa = pd.read_excel(hoa_file)
        hoa_inserted = 0
        hoa_updated = 0
        
        seen_hoa = {}
        
        for _, row in df_hoa.iterrows():
            hoa_name = str(row['HOA Name']).strip() if not pd.isna(row['HOA Name']) else None
            location = str(row['Location (City/County)']).strip() if not pd.isna(row['Location (City/County)']) else None
            
            if not hoa_name or not location:
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
                
            # Query in-memory dict first
            existing = seen_hoa.get(key)
            if not existing:
                # Query database
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
                hoa_updated += 1
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
                hoa_inserted += 1
                
        db.commit()
        print(f"HOA rules seeding completed: {hoa_inserted} inserted, {hoa_updated} updated.")
    else:
        print(f"HOA rules file not found at {hoa_file}")

if __name__ == "__main__":
    db = SessionLocal()
    excel_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    try:
        seed_rules(db, excel_dir)
    finally:
        db.close()
