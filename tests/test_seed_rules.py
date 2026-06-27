import os
import sys
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd

# Ensure Hosteva app is on PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import Base
from app.models.compliance import MunicipalCode, HOARule
from scripts.seed_rules import (
    parse_days,
    parse_max_occupancy,
    parse_tax_rate,
    parse_date,
    seed_rules
)

def test_parse_days():
    assert parse_days("7 nights") == 7
    assert parse_days("7.0 nights") == 7
    assert parse_days("30 days") == 30
    assert parse_days("6.0 months") == 180
    assert parse_days(None) is None
    assert parse_days("No minimum") is None

def test_parse_max_occupancy():
    assert parse_max_occupancy("max 10 total") == 10
    assert parse_max_occupancy("2 guests per bedroom + 2 extra, max 10") == 10
    assert parse_max_occupancy("limit of 8") == 8
    assert parse_max_occupancy(None) is None
    assert parse_max_occupancy("Standard capacity limits") is None

def test_parse_tax_rate():
    assert parse_tax_rate("6.0% Tourist Development Tax") == 6.0
    assert parse_tax_rate("5% Tax") == 5.0
    assert parse_tax_rate(None) is None
    assert parse_tax_rate("N/A") is None

def test_parse_date():
    assert parse_date("2026-06-05") == date(2026, 6, 5)
    assert parse_date(pd.Timestamp("2026-06-05")) == date(2026, 6, 5)
    assert parse_date(None) is None

@pytest.fixture
def mock_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

def test_seed_rules_upsert(mock_db, tmp_path):
    # Setup mock data structure
    jur_data = {
        'Jurisdiction Name': ['Orange County', 'Orange County', 'Miami Beach'],
        'Jurisdiction Type': ['County', 'County', 'City'],
        'STR Permitted?': ['Yes', 'Yes', 'Banned'],
        'Permit/License Required?': ['No', 'Yes', 'Yes'],
        'Minimum Stay Requirement': ['30 days', '30 days', 'NaN'],
        'Occupancy Limits': ['max 10', 'max 12', 'NaN'],
        'Tax Rate / Registration Fee': ['6.0% Tourist Development Tax', '6.0%', 'NaN'],
        'Source URL': ['http://url1', 'http://url1_updated', 'http://url2'],
        'Last Verified Date': ['2026-06-05', '2026-06-05', '2026-06-05']
    }
    
    hoa_data = {
        'HOA Name': ['Solara Resort', 'Solara Resort', 'Ave Maria'],
        'Location (City/County)': ['Osceola County', 'Osceola County', 'Collier County'],
        'STR Permitted?': ['Yes', 'Yes', 'No'],
        'Minimum Lease/Stay': ['None (Nightly)', 'Nightly', '30 days'],
        'Rules Available Y/N': ['Yes', 'Yes', 'Yes'],
        'Official Website': ['http://solara', 'http://solara_new', 'http://avemaria'],
        'Last Confirmed Date': ['2026-06-07', '2026-06-07', '2026-06-07'],
        'Key Rules & STR Restrictions (Notes)': ['Notes 1', 'Notes 1 updated', 'Notes 2']
    }
    
    # Save first version (Row 0 and Row 2)
    df_jur_1 = pd.DataFrame({k: [v[0], v[2]] for k, v in jur_data.items()})
    df_hoa_1 = pd.DataFrame({k: [v[0], v[2]] for k, v in hoa_data.items()})
    
    jur_file = tmp_path / "Hosteva Jurisdictional Rules DB - Florida Counties (Phase 1).xlsx"
    hoa_file = tmp_path / "Hosteva HOA STR Rules POC Database.xlsx"
    
    df_jur_1.to_excel(jur_file, index=False)
    df_hoa_1.to_excel(hoa_file, index=False)
    
    # 1. First run - Inserts
    seed_rules(mock_db, str(tmp_path))
    
    assert mock_db.query(MunicipalCode).count() == 2
    assert mock_db.query(HOARule).count() == 2
    
    orange_county = mock_db.query(MunicipalCode).filter_by(municipality_name="Orange County", jurisdiction_type="County").first()
    assert orange_county is not None
    assert orange_county.requires_permit is False
    assert orange_county.max_occupancy_limit == 10
    assert orange_county.source_url == "http://url1"
    
    solara_resort = mock_db.query(HOARule).filter_by(hoa_name="Solara Resort", location="Osceola County").first()
    assert solara_resort is not None
    assert solara_resort.official_website == "http://solara"
    assert solara_resort.key_rules_notes == "Notes 1"
    
    # 2. Second run - Updates (Upsert)
    df_jur_2 = pd.DataFrame(jur_data)
    df_hoa_2 = pd.DataFrame(hoa_data)
    
    df_jur_2.to_excel(jur_file, index=False)
    df_hoa_2.to_excel(hoa_file, index=False)
    
    seed_rules(mock_db, str(tmp_path))
    
    # Total unique count is still 2 because row 1 matches row 0 unique keys
    assert mock_db.query(MunicipalCode).count() == 2
    assert mock_db.query(HOARule).count() == 2
    
    orange_county_updated = mock_db.query(MunicipalCode).filter_by(municipality_name="Orange County", jurisdiction_type="County").first()
    assert orange_county_updated.requires_permit is True
    assert orange_county_updated.max_occupancy_limit == 12
    assert orange_county_updated.source_url == "http://url1_updated"
    
    solara_resort_updated = mock_db.query(HOARule).filter_by(hoa_name="Solara Resort", location="Osceola County").first()
    assert solara_resort_updated.official_website == "http://solara_new"
    assert solara_resort_updated.key_rules_notes == "Notes 1 updated"
