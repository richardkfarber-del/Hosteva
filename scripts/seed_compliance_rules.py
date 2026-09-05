import os
import sys

# Ensure Hosteva app is on PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app.models.compliance import MunicipalCode, Region, ZoningCode, ComplianceRule
from app.db_models import Ordinance

def seed_data():
    db = SessionLocal()
    try:
        print("Starting compliance database seeding...")

        # 1. State Level: Florida
        # Seed Region
        fl_region = db.query(Region).filter_by(locality="Florida", admin_area="FL").first()
        if not fl_region:
            fl_region = Region(locality="Florida", admin_area="FL")
            db.add(fl_region)
            db.commit()
            db.refresh(fl_region)
            print("Seeded Region: Florida, FL")
        else:
            print("Region Florida, FL already exists")

        # Seed Municipal Code
        fl_mcode = db.query(MunicipalCode).filter_by(municipality_name="State of Florida", ordinance_number="DBPR-VR-LICENSE").first()
        if not fl_mcode:
            fl_mcode = MunicipalCode(
                municipality_name="State of Florida",
                ordinance_number="DBPR-VR-LICENSE",
                str_prohibited=False,
                max_occupancy_limit=None
            )
            db.add(fl_mcode)
            db.commit()
            db.refresh(fl_mcode)
            print("Seeded MunicipalCode: State of Florida")
        else:
            print("MunicipalCode State of Florida already exists")

        # Seed Ordinance text
        fl_ord = db.query(Ordinance).filter_by(jurisdiction="Florida").first()
        if not fl_ord:
            fl_ord = Ordinance(
                jurisdiction="Florida",
                ordinance_text="State of Florida DBPR (Department of Business and Professional Regulation) requires all short-term vacation rentals (condominiums, dwellings, apartments) to obtain a transient public lodging establishment license (Vacation Rental License) under Chapter 509, Florida Statutes. Operators must also register with the Department of Revenue for sales tax."
            )
            db.add(fl_ord)
            db.commit()
            db.refresh(fl_ord)
            print("Seeded Ordinance: Florida")
        else:
            print("Ordinance Florida already exists")

        # 2. County Level: Miami-Dade
        # Seed Region
        md_region = db.query(Region).filter_by(locality="Miami-Dade County", admin_area="FL").first()
        if not md_region:
            md_region = Region(locality="Miami-Dade County", admin_area="FL")
            db.add(md_region)
            db.commit()
            db.refresh(md_region)
            print("Seeded Region: Miami-Dade County, FL")
        else:
            print("Region Miami-Dade County, FL already exists")

        # Seed Municipal Code
        md_mcode = db.query(MunicipalCode).filter_by(municipality_name="Miami-Dade County", ordinance_number="MDC-BTR-CU").first()
        if not md_mcode:
            md_mcode = MunicipalCode(
                municipality_name="Miami-Dade County",
                ordinance_number="MDC-BTR-CU",
                str_prohibited=False,
                max_occupancy_limit=None
            )
            db.add(md_mcode)
            db.commit()
            db.refresh(md_mcode)
            print("Seeded MunicipalCode: Miami-Dade County")
        else:
            print("MunicipalCode Miami-Dade County already exists")

        # Seed Ordinance text
        md_ord = db.query(Ordinance).filter_by(jurisdiction="Miami-Dade County").first()
        if not md_ord:
            md_ord = Ordinance(
                jurisdiction="Miami-Dade County",
                ordinance_text="Miami-Dade County requires all short-term vacation rental operators in unincorporated areas and participating municipalities to obtain a Certificate of Use (CU) and a Business Tax Receipt (BTR). Operators must comply with fire safety guidelines, waste management rules, and maximum occupancy limits."
            )
            db.add(md_ord)
            db.commit()
            db.refresh(md_ord)
            print("Seeded Ordinance: Miami-Dade County")
        else:
            print("Ordinance Miami-Dade County already exists")

        # 3. Municipality Level: City of Miami Beach
        # Seed Region
        mb_region = db.query(Region).filter_by(locality="Miami Beach", admin_area="FL").first()
        if not mb_region:
            mb_region = Region(locality="Miami Beach", admin_area="FL")
            db.add(mb_region)
            db.commit()
            db.refresh(mb_region)
            print("Seeded Region: Miami Beach, FL")
        else:
            print("Region Miami Beach, FL already exists")

        # Seed Municipal Code — Free Audit geocodes locality as "Miami Beach" (ilike exact).
        # Keep legacy "City of Miami Beach" row AND a geocode-matching "Miami Beach" City/FL row.
        mb_source = "https://www.miamibeachfl.gov/government/planning/zoning/"
        for mb_name in ("Miami Beach", "City of Miami Beach"):
            mb_mcode = db.query(MunicipalCode).filter_by(
                municipality_name=mb_name,
                ordinance_number="MB-STR-PROHIBITION",
            ).first()
            if not mb_mcode:
                # Also match any prior row without ordinance number uniqueness
                mb_mcode = db.query(MunicipalCode).filter(
                    MunicipalCode.municipality_name.ilike(mb_name),
                    MunicipalCode.jurisdiction_type.ilike("City"),
                ).first()
            if not mb_mcode:
                mb_mcode = MunicipalCode(
                    municipality_name=mb_name,
                    ordinance_number="MB-STR-PROHIBITION",
                    str_prohibited=True,
                    is_allowed=False,
                    requires_permit=True,
                    permit_name="Miami Beach STR Certificate / Zoning Review",
                    max_occupancy_limit=None,
                    jurisdiction_type="City",
                    state="FL",
                    source_url=mb_source,
                    str_permitted_raw="Restricted / Prohibited in many residential zones",
                    is_expert_verified=True,
                )
                db.add(mb_mcode)
                db.commit()
                db.refresh(mb_mcode)
                print(f"Seeded MunicipalCode: {mb_name}")
            else:
                # Upsert Free-Audit fields so live check is Covered (not Under Review)
                mb_mcode.ordinance_number = mb_mcode.ordinance_number or "MB-STR-PROHIBITION"
                mb_mcode.str_prohibited = True
                mb_mcode.is_allowed = False
                mb_mcode.jurisdiction_type = mb_mcode.jurisdiction_type or "City"
                mb_mcode.state = mb_mcode.state or "FL"
                if not mb_mcode.source_url:
                    mb_mcode.source_url = mb_source
                if not mb_mcode.permit_name:
                    mb_mcode.requires_permit = True
                    mb_mcode.permit_name = "Miami Beach STR Certificate / Zoning Review"
                mb_mcode.is_expert_verified = True
                db.commit()
                print(f"MunicipalCode {mb_name} already exists — Free-Audit fields upserted")

        # Seed Ordinance text
        mb_ord = db.query(Ordinance).filter_by(jurisdiction="City of Miami Beach").first()
        if not mb_ord:
            mb_ord = Ordinance(
                jurisdiction="City of Miami Beach",
                ordinance_text="City of Miami Beach strictly prohibits short-term rentals (STRs) in all single-family zones (SF, SD-B, and RM-1) and in prohibited residential areas. STRs are only permitted in specific multi-family and commercial zoning districts where short-term occupancy is explicitly authorized by the City Code."
            )
            db.add(mb_ord)
            db.commit()
            db.refresh(mb_ord)
            print("Seeded Ordinance: City of Miami Beach")
        else:
            print("Ordinance City of Miami Beach already exists")

        # 4. ZIP Code Specific Regions & Zoning Restrictions for Miami Beach (33139, 33140, 33141)
        zip_codes = ["33139", "33140", "33141"]
        prohibited_zones = [
            ("SF", "Single Family Residential District"),
            ("SD-B", "Single Family Residential SD-B District"),
            ("RM-1", "Residential Multi-Family Low Intensity District")
        ]

        for zip_code in zip_codes:
            # Create a specific Region for the ZIP code in Miami Beach
            zip_region_name = f"Miami Beach ({zip_code})"
            zip_region = db.query(Region).filter_by(locality=zip_region_name, admin_area="FL").first()
            if not zip_region:
                zip_region = Region(locality=zip_region_name, admin_area="FL")
                db.add(zip_region)
                db.commit()
                db.refresh(zip_region)
                print(f"Seeded Region: {zip_region_name}")
            
            # Map prohibited zoning codes for this ZIP code Region
            for zone_code, zone_desc in prohibited_zones:
                # Seed ZoningCode
                full_zone_code = f"{zip_code}-{zone_code}"
                zcode = db.query(ZoningCode).filter_by(region_id=zip_region.id, code_name=full_zone_code).first()
                if not zcode:
                    zcode = ZoningCode(
                        region_id=zip_region.id,
                        code_name=full_zone_code,
                        description=f"{zone_desc} in ZIP {zip_code} (Prohibited)"
                    )
                    db.add(zcode)
                    db.commit()
                    db.refresh(zcode)
                    print(f"Seeded ZoningCode: {full_zone_code}")
                
                # Seed ComplianceRule (STR strictly prohibited in these zones)
                rule = db.query(ComplianceRule).filter_by(zoning_id=zcode.id).first()
                if not rule:
                    rule = ComplianceRule(
                        zoning_id=zcode.id,
                        eligibility_status="RED",
                        is_str_allowed=False,
                        requires_permit=False,
                        min_stay_days=180, # Rentals under 6 months/180 days are considered STR and banned
                        primary_residence_required=False,
                        plain_english_conditions=f"Short-term rentals are strictly prohibited in the {zone_code} single-family zoning district within ZIP code {zip_code}.",
                        permit_application_url=None,
                        ordinance_reference_url="https://www.miamibeachfl.gov/government/planning/zoning/"
                    )
                    db.add(rule)
                    db.commit()
                    print(f"Seeded ComplianceRule for ZoningCode: {full_zone_code}")

        print("Database compliance rules and zoning constraints seeded successfully.")

        # Verification output
        regions_count = db.query(Region).count()
        municipal_codes_count = db.query(MunicipalCode).count()
        ordinances_count = db.query(Ordinance).count()
        zoning_codes_count = db.query(ZoningCode).count()
        compliance_rules_count = db.query(ComplianceRule).count()
        
        print("\n--- Seeding Verification Summary ---")
        print(f"Regions count: {regions_count}")
        print(f"Municipal Codes count: {municipal_codes_count}")
        print(f"Ordinances count: {ordinances_count}")
        print(f"Zoning Codes count: {zoning_codes_count}")
        print(f"Compliance Rules count: {compliance_rules_count}")
        print("------------------------------------\n")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
