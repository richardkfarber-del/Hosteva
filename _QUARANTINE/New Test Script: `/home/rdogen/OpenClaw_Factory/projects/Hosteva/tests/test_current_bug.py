import pytest

def test_sqlalchemy_dependency():
    with open('requirements.txt', 'r') as file:
        requirements = file.read()
    
    assert 'SQLAlchemy' in requirements, "SQLAlchemy dependency is missing from requirements.txt"
