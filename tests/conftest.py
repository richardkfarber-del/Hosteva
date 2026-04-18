import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_TEST_DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/hosteva"

# Create a global DB engine
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create tables once for the test session."""
    # Tollbooth enforced: No try/except bypass. Fail loudly.
    Base.metadata.create_all(bind=engine)
    yield
    # No drop_all! Perfect teardown is handled via rollback.

@pytest.fixture(scope="function")
def db_session():
    """
    Implements state isolation logic:
    For each test, yields a connection wrapped in session.begin_nested() 
    and physically calls session.rollback() in the finally block.
    """
    connection = engine.connect()
    transaction = connection.begin()
    
    session = TestingSessionLocal(bind=connection)
    session.begin_nested()
    
    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            session.begin_nested()
            
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """
    Configures an override_get_db FastAPI dependency that points to the test database.
    """
    def override_get_db():
        yield db_session
        
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
