import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.src.main import app
from app.src.database import Base, get_db, DATABASE_URL

# Build test URL dynamically: replacement 'qr_challenge' with 'qr_challenge_test'
# or use what's in TEST_DATABASE_URL environment variable.
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    if "qr_challenge" in DATABASE_URL:
        TEST_DATABASE_URL = DATABASE_URL.replace("qr_challenge", "qr_challenge_test")
    else:
        # Generic fallback if the main URL doesn't follow the pattern
        TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/qr_challenge_test"

# Setup engine for testing
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Session-level fixture to create and drop tables.
    Requires the database specified in TEST_DATABASE_URL to exist.
    """
    try:
        # Drop and recreate to ensure schema changes are applied
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        pytest.exit(f"Could not connect to test database: {e}. Please ensure it exists.")
    
    yield
    
    # Base.metadata.drop_all(bind=engine) # Optional: comment out if you want to inspect after tests

@pytest.fixture
def db_session():
    """
    Function-level fixture that provides a transactional database session.
    Rolls back changes after each test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """
    Fixture that provides a TestClient with the database dependency overridden.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
