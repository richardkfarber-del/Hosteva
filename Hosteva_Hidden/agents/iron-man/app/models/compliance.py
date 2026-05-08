from sqlalchemy import Column, Integer, String, CheckConstraint, Index, ForeignKey, text, DDL, event
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import TSTZRANGE
from sqlalchemy.sql import func

Base = declarative_base()

class MunicipalCode(Base):
    __tablename__ = 'municipal_codes'

    id = Column(Integer, primary_key=True, index=True)
    code_identifier = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "code_identifier ~ '^[A-Z0-9]{3,10}-[A-Z0-9]{2,10}$'", 
            name='ck_municipal_code_format'
        ),
        CheckConstraint(
            "length(code_identifier) <= 50",
            name='ck_municipal_code_length'
        ),
    )


class PropertyCompliance(Base):
    __tablename__ = 'property_compliance'

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, nullable=False)
    municipal_code_id = Column(Integer, ForeignKey('municipal_codes.id'), nullable=False)
    status = Column(String(20), nullable=False)
    valid_period = Column(TSTZRANGE, nullable=False)

    __table_args__ = (
        Index('ix_property_compliance_prop_period', 'property_id', 'valid_period', postgresql_using='gist'),
        CheckConstraint(
            "status IN ('COMPLIANT', 'NON_COMPLIANT', 'PENDING')",
            name='ck_property_compliance_status'
        ),
    )

# Physically implement the trg_close_expired_compliance trigger
trigger_ddl = DDL('''
CREATE OR REPLACE FUNCTION trg_close_expired_compliance_func()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        -- Prevent overwrites to anything but valid_period (allowing closure of the period)
        IF OLD.status != NEW.status OR OLD.property_id != NEW.property_id OR OLD.municipal_code_id != NEW.municipal_code_id THEN
            RAISE EXCEPTION 'Historical overwrite operation prevented by trg_close_expired_compliance. Append-only allowed.';
        END IF;
    END IF;
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'Historical overwrite operation prevented by trg_close_expired_compliance. Deletes not allowed.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_close_expired_compliance ON property_compliance;
CREATE TRIGGER trg_close_expired_compliance
BEFORE UPDATE OR DELETE ON property_compliance
FOR EACH ROW
EXECUTE FUNCTION trg_close_expired_compliance_func();
''')

event.listen(
    PropertyCompliance.__table__,
    'after_create',
    trigger_ddl.execute_if(dialect='postgresql')
)

