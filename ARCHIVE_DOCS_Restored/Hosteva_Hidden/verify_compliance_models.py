import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, InternalError, ProgrammingError
from app.models.compliance import MunicipalCode, PropertyCompliance
from app.models.property import Property
import uuid
import datetime

engine = create_engine("postgresql+psycopg://postgres:postgres@localhost:5432/hosteva")
Session = sessionmaker(bind=engine)
session = Session()

print("Testing constraints...")
try:
    bad_code = MunicipalCode(municipality_name="Test City", ordinance_number="bad format!")
    session.add(bad_code)
    session.commit()
    print("FAILED: Check constraint for ordinance format did not fire.")
except IntegrityError:
    session.rollback()
    print("SUCCESS: Ordinance format check constraint works.")

try:
    good_code = MunicipalCode(municipality_name="Valid City", ordinance_number="ORDINANCE-123")
    session.add(good_code)
    
    test_prop = Property(id="prop-123", address="123 Test St", city="Test", state="TS")
    # merge to ignore if exists
    session.merge(test_prop)
    session.commit()

    comp_id = uuid.uuid4()
    session.execute(text("""
        INSERT INTO property_compliance (id, property_id, municipal_code_id, is_compliant, valid_period)
        VALUES (:id, 'prop-123', :code_id, true, '[2024-01-01, 2024-12-31]')
    """), {"id": comp_id, "code_id": good_code.id})
    session.commit()
    print("SUCCESS: Property compliance inserted.")
    
    session.execute(text("UPDATE property_compliance SET is_compliant = false WHERE property_id = 'prop-123'"))
    session.commit()
    print("FAILED: Trigger did not fire on update.")
except InternalError as e:
    session.rollback()
    if "Append-only" in str(e):
        print("SUCCESS: Trigger trg_close_expired_compliance works.")
    else:
        print(f"FAILED with unexpected internal error: {e}")
except ProgrammingError as e:
    session.rollback()
    if "Append-only" in str(e):
        print("SUCCESS: Trigger trg_close_expired_compliance works.")
    else:
        print(f"FAILED with unexpected programming error: {e}")
except Exception as e:
    session.rollback()
    print(f"Error: {e}")

