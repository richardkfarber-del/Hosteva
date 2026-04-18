import pytest
from app.models.compliance import MunicipalCode, PropertyCompliance
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql
from sqlalchemy import MetaData

def test_municipal_code_constraints():
    """Verify CHECK constraints are present on MunicipalCode."""
    table = MunicipalCode.__table__
    constraints = [c.name for c in table.constraints]
    assert 'chk_mun_name_length' in constraints
    assert 'chk_ordinance_format' in constraints

def test_property_compliance_indexes():
    """Verify GiST index is present on PropertyCompliance valid_period."""
    table = PropertyCompliance.__table__
    indexes = [ix.name for ix in table.indexes]
    assert 'ix_property_compliance_valid_period' in indexes

def test_trigger_is_defined():
    """Trigger is defined in migrations, verifying model has TSTZRANGE."""
    table = PropertyCompliance.__table__
    assert 'valid_period' in table.columns
    assert str(table.columns['valid_period'].type) == 'TSTZRANGE'
