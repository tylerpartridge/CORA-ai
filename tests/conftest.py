"""
Pytest Configuration and Fixtures
Central configuration for all tests
"""

import os
import sys
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# FastAPI and database imports
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Import your app and models
from app import app
from models import Base, User, Expense, Job, BusinessProfile
from dependencies.database import get_db
from services.auth_service import create_access_token, get_password_hash
from config import Config as Settings

# Test database URL - using in-memory SQLite for speed
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine with check_same_thread=False for SQLite
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Use StaticPool for in-memory database
)

# Create test session
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# -------------- Pytest Configuration --------------

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as a security test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "auth: mark test as authentication related"
    )
    config.addinivalue_line(
        "markers", "database: mark test as database related"
    )


# -------------- Database Fixtures --------------

@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """Create a fresh database for each test"""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    db = TestSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def override_get_db(test_db: Session):
    """Override the get_db dependency with test database"""
    def _override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


# -------------- Client Fixtures --------------

@pytest.fixture(scope="function")
def client(override_get_db) -> TestClient:
    """Create test client with overridden database"""
    return TestClient(app)


@pytest.fixture(scope="function")
def authenticated_client(client: TestClient, test_user: dict) -> TestClient:
    """Create authenticated test client"""
    client.headers = {
        "Authorization": f"Bearer {test_user['access_token']}"
    }
    return client


# -------------- User Fixtures --------------

@pytest.fixture
def test_user_data() -> dict:
    """Test user data"""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "company_name": "Test Construction Co",
        "full_name": "Test User"
    }


@pytest.fixture
def test_user(test_db: Session, test_user_data: dict) -> dict:
    """Create a test user in database"""
    # Hash password
    hashed_password = get_password_hash(test_user_data["password"])
    
    # Create user
    user = User(
        email=test_user_data["email"],
        hashed_password=hashed_password,
        company_name=test_user_data["company_name"],
        full_name=test_user_data["full_name"],
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow()
    )
    
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "user": user,
        "password": test_user_data["password"],
        "access_token": access_token
    }


@pytest.fixture
def test_admin_user(test_db: Session) -> dict:
    """Create a test admin user"""
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("AdminPassword123!"),
        company_name="Admin Co",
        full_name="Admin User",
        is_active=True,
        is_verified=True,
        is_admin=True,
        created_at=datetime.utcnow()
    )
    
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "user": user,
        "access_token": access_token
    }


# -------------- Business Data Fixtures --------------

@pytest.fixture
def test_job(test_db: Session, test_user: dict) -> Job:
    """Create a test job"""
    job = Job(
        name="Test Job Site",
        address="123 Test St, Test City, TS 12345",
        budget=50000.00,
        user_id=test_user["user"].id,
        created_at=datetime.utcnow(),
        status="active"
    )
    
    test_db.add(job)
    test_db.commit()
    test_db.refresh(job)
    
    return job


@pytest.fixture
def test_expense(test_db: Session, test_user: dict, test_job: Job) -> Expense:
    """Create a test expense"""
    expense = Expense(
        description="Test Materials",
        amount=500.00,
        vendor="Test Vendor",
        category="materials",
        job_id=test_job.id,
        user_id=test_user["user"].id,
        created_at=datetime.utcnow(),
        expense_date=datetime.utcnow().date()
    )
    
    test_db.add(expense)
    test_db.commit()
    test_db.refresh(expense)
    
    return expense


@pytest.fixture
def test_business_profile(test_db: Session, test_user: dict) -> BusinessProfile:
    """Create a test business profile"""
    profile = BusinessProfile(
        user_id=test_user["user"].id,
        business_name="Test Construction LLC",
        business_type="LLC",
        tax_id="12-3456789",
        address="456 Business Ave",
        city="Test City",
        state="TS",
        zip_code="12345",
        phone="555-0100",
        created_at=datetime.utcnow()
    )
    
    test_db.add(profile)
    test_db.commit()
    test_db.refresh(profile)
    
    return profile


# -------------- Mock External Services --------------

@pytest.fixture
def mock_stripe(monkeypatch):
    """Mock Stripe API calls"""
    class MockStripe:
        @staticmethod
        def create_customer(**kwargs):
            return {"id": "cus_test123", "email": kwargs.get("email")}
        
        @staticmethod
        def create_subscription(**kwargs):
            return {"id": "sub_test123", "status": "active"}
        
        @staticmethod
        def create_payment_intent(**kwargs):
            return {"id": "pi_test123", "status": "succeeded"}
    
    monkeypatch.setattr("services.stripe_service.stripe", MockStripe())
    return MockStripe()


@pytest.fixture
def mock_plaid(monkeypatch):
    """Mock Plaid API calls"""
    class MockPlaid:
        @staticmethod
        def create_link_token(**kwargs):
            return {"link_token": "link_test123"}
        
        @staticmethod
        def exchange_public_token(public_token):
            return {"access_token": "access_test123"}
        
        @staticmethod
        def get_accounts(access_token):
            return {
                "accounts": [
                    {
                        "account_id": "acc_test123",
                        "name": "Test Checking",
                        "balances": {"current": 1000.00}
                    }
                ]
            }
    
    monkeypatch.setattr("services.plaid_service.plaid_client", MockPlaid())
    return MockPlaid()


# -------------- Utility Fixtures --------------

@pytest.fixture
def temp_upload_dir():
    """Create temporary directory for file uploads"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_csv_file(temp_upload_dir):
    """Create a sample CSV file for testing"""
    import csv
    
    file_path = Path(temp_upload_dir) / "test_expenses.csv"
    
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Description", "Amount", "Vendor", "Category"])
        writer.writerow(["2024-01-01", "Materials", "500.00", "Home Depot", "materials"])
        writer.writerow(["2024-01-02", "Labor", "1000.00", "Contractor", "labor"])
    
    return file_path


@pytest.fixture
def sample_receipt_image(temp_upload_dir):
    """Create a sample receipt image for testing"""
    from PIL import Image
    
    file_path = Path(temp_upload_dir) / "test_receipt.png"
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='white')
    img.save(file_path)
    
    return file_path


# -------------- Settings Override --------------

@pytest.fixture
def test_settings():
    """Override settings for testing"""
    # Set test environment variables
    os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["DEBUG"] = "True"
    os.environ["JWT_EXPIRATION_HOURS"] = "1"
    os.environ["RATE_LIMIT_ENABLED"] = "False"
    os.environ["EMAIL_ENABLED"] = "False"
    
    # Return the Config class itself (not an instance)
    return Settings


@pytest.fixture(autouse=True)
def override_settings(test_settings, monkeypatch):
    """Automatically override settings for all tests"""
    for key, value in test_settings.__dict__.items():
        monkeypatch.setenv(key, str(value))


# -------------- Async Fixtures --------------

@pytest.fixture
async def async_client(override_get_db):
    """Async test client for async endpoints"""
    from httpx import AsyncClient
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# -------------- Cleanup Fixtures --------------

@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Clean up any test files created during tests"""
    yield
    
    # Clean up test database files if they exist
    test_db_files = [
        "test.db",
        "test_models.db",
        ":memory:"
    ]
    
    for db_file in test_db_files:
        if Path(db_file).exists():
            try:
                Path(db_file).unlink()
            except:
                pass