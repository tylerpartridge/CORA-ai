import os, pytest
if os.getenv('CORA_DB_TESTS','0') != '1':
    pytest.skip('DB-backed tests disabled (set CORA_DB_TESTS=1 to enable)', allow_module_level=True)
"""
Expense Management Tests
Tests for expense CRUD operations and business logic
"""

import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
# Fix import paths


import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models import Expense, Job, User


class TestExpenseCreation:
    """Test expense creation functionality"""
    
    @pytest.mark.database
    def test_create_expense_success(self, authenticated_client: TestClient, test_job: Job):
        """Test successful expense creation"""
        expense_data = {
            "description": "Construction Materials",
            "amount": 750.50,
            "vendor": "Home Depot",
            "category": "materials",
            "job_id": test_job.id,
            "expense_date": str(date.today())
        }
        
        response = authenticated_client.post(
            "/api/expenses",
            json=expense_data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["description"] == "Construction Materials"
        assert float(data["amount"]) == 750.50
        assert data["vendor"] == "Home Depot"
        assert data["job_id"] == test_job.id
    
    @pytest.mark.database
    def test_create_expense_without_job(self, authenticated_client: TestClient):
        """Test creating expense without job assignment"""
        expense_data = {
            "description": "Office Supplies",
            "amount": 50.00,
            "vendor": "Staples",
            "category": "office",
            "expense_date": str(date.today())
        }
        
        response = authenticated_client.post(
            "/api/expenses",
            json=expense_data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["job_id"] is None
    
    @pytest.mark.database
    @pytest.mark.parametrize("invalid_amount", [-100, 0, "not_a_number", None])
    def test_create_expense_invalid_amount(self, authenticated_client: TestClient, invalid_amount):
        """Test expense creation with invalid amounts"""
        expense_data = {
            "description": "Test Expense",
            "amount": invalid_amount,
            "vendor": "Test Vendor",
            "category": "materials"
        }
        
        response = authenticated_client.post(
            "/api/expenses",
            json=expense_data
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.database
    def test_create_expense_invalid_job(self, authenticated_client: TestClient):
        """Test expense creation with non-existent job"""
        expense_data = {
            "description": "Test Expense",
            "amount": 100.00,
            "vendor": "Test Vendor",
            "category": "materials",
            "job_id": 99999  # Non-existent job
        }
        
        response = authenticated_client.post(
            "/api/expenses",
            json=expense_data
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestExpenseRetrieval:
    """Test expense retrieval functionality"""
    
    @pytest.mark.database
    def test_get_all_expenses(self, authenticated_client: TestClient, test_expense: Expense):
        """Test retrieving all user expenses"""
        response = authenticated_client.get("/api/expenses")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert any(e["id"] == test_expense.id for e in data)
    
    @pytest.mark.database
    def test_get_expense_by_id(self, authenticated_client: TestClient, test_expense: Expense):
        """Test retrieving specific expense"""
        response = authenticated_client.get(f"/api/expenses/{test_expense.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_expense.id
        assert data["description"] == test_expense.description
    
    @pytest.mark.database
    def test_get_nonexistent_expense(self, authenticated_client: TestClient):
        """Test retrieving non-existent expense"""
        response = authenticated_client.get("/api/expenses/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.database
    def test_get_expenses_by_job(self, authenticated_client: TestClient, test_expense: Expense, test_job: Job):
        """Test filtering expenses by job"""
        response = authenticated_client.get(f"/api/expenses?job_id={test_job.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(e["job_id"] == test_job.id for e in data)
    
    @pytest.mark.database
    def test_get_expenses_by_date_range(self, authenticated_client: TestClient, test_expense: Expense):
        """Test filtering expenses by date range"""
        start_date = (date.today() - timedelta(days=7)).isoformat()
        end_date = date.today().isoformat()
        
        response = authenticated_client.get(
            f"/api/expenses?start_date={start_date}&end_date={end_date}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # All expenses should be within date range
        for expense in data:
            expense_date = datetime.fromisoformat(expense["expense_date"]).date()
            assert expense_date >= date.fromisoformat(start_date)
            assert expense_date <= date.fromisoformat(end_date)


class TestExpenseUpdate:
    """Test expense update functionality"""
    
    @pytest.mark.database
    def test_update_expense_success(self, authenticated_client: TestClient, test_expense: Expense):
        """Test successful expense update"""
        update_data = {
            "description": "Updated Description",
            "amount": 900.00,
            "vendor": "Updated Vendor"
        }
        
        response = authenticated_client.put(
            f"/api/expenses/{test_expense.id}",
            json=update_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated Description"
        assert float(data["amount"]) == 900.00
        assert data["vendor"] == "Updated Vendor"
    
    @pytest.mark.database
    def test_update_nonexistent_expense(self, authenticated_client: TestClient):
        """Test updating non-existent expense"""
        update_data = {"description": "Updated"}
        
        response = authenticated_client.put(
            "/api/expenses/99999",
            json=update_data
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.database
    def test_update_expense_other_user(self, client: TestClient, test_expense: Expense, test_db: Session):
        """Test that users cannot update other users' expenses"""
        # Create another user
        from services.auth_service import get_password_hash, create_access_token
        other_user = User(
            email="other@example.com",
            hashed_password=get_password_hash("Password123!"),
            company_name="Other Co"
        )
        test_db.add(other_user)
        test_db.commit()
        
        # Authenticate as other user
        token = create_access_token(data={"sub": other_user.email})
        client.headers = {"Authorization": f"Bearer {token}"}
        
        update_data = {"description": "Hacked!"}
        response = client.put(
            f"/api/expenses/{test_expense.id}",
            json=update_data
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestExpenseDeletion:
    """Test expense deletion functionality"""
    
    @pytest.mark.database
    def test_delete_expense_success(self, authenticated_client: TestClient, test_expense: Expense, test_db: Session):
        """Test successful expense deletion"""
        response = authenticated_client.delete(f"/api/expenses/{test_expense.id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify expense is deleted
        deleted_expense = test_db.query(Expense).filter(Expense.id == test_expense.id).first()
        assert deleted_expense is None
    
    @pytest.mark.database
    def test_delete_nonexistent_expense(self, authenticated_client: TestClient):
        """Test deleting non-existent expense"""
        response = authenticated_client.delete("/api/expenses/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestExpenseCalculations:
    """Test expense calculation and aggregation"""
    
    @pytest.mark.database
    def test_total_expenses_by_job(self, authenticated_client: TestClient, test_job: Job, test_db: Session, test_user: dict):
        """Test calculating total expenses for a job"""
        # Create multiple expenses
        expenses = [
            Expense(
                description=f"Expense {i}",
                amount=100.00 * i,
                vendor="Vendor",
                category="materials",
                job_id=test_job.id,
                user_id=test_user["user"].id,
                expense_date=date.today()
            )
            for i in range(1, 4)
        ]
        test_db.add_all(expenses)
        test_db.commit()
        
        response = authenticated_client.get(f"/api/jobs/{test_job.id}/total-expenses")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert float(data["total"]) == 600.00  # 100 + 200 + 300
    
    @pytest.mark.database
    def test_expenses_by_category(self, authenticated_client: TestClient, test_db: Session, test_user: dict):
        """Test grouping expenses by category"""
        # Create expenses in different categories
        categories = ["materials", "labor", "equipment", "materials"]
        for i, category in enumerate(categories):
            expense = Expense(
                description=f"Expense {i}",
                amount=100.00,
                vendor="Vendor",
                category=category,
                user_id=test_user["user"].id,
                expense_date=date.today()
            )
            test_db.add(expense)
        test_db.commit()
        
        response = authenticated_client.get("/api/expenses/by-category")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["materials"] == 200.00
        assert data["labor"] == 100.00
        assert data["equipment"] == 100.00


class TestExpenseBulkOperations:
    """Test bulk expense operations"""
    
    @pytest.mark.database
    def test_bulk_create_expenses(self, authenticated_client: TestClient, test_job: Job):
        """Test creating multiple expenses at once"""
        expenses_data = [
            {
                "description": f"Bulk Expense {i}",
                "amount": 100.00 * i,
                "vendor": "Bulk Vendor",
                "category": "materials",
                "job_id": test_job.id,
                "expense_date": str(date.today())
            }
            for i in range(1, 4)
        ]
        
        response = authenticated_client.post(
            "/api/expenses/bulk",
            json=expenses_data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert len(data) == 3
    
    @pytest.mark.database
    def test_bulk_delete_expenses(self, authenticated_client: TestClient, test_db: Session, test_user: dict):
        """Test deleting multiple expenses at once"""
        # Create expenses to delete
        expenses = [
            Expense(
                description=f"To Delete {i}",
                amount=100.00,
                vendor="Vendor",
                category="materials",
                user_id=test_user["user"].id,
                expense_date=date.today()
            )
            for i in range(3)
        ]
        test_db.add_all(expenses)
        test_db.commit()
        
        expense_ids = [e.id for e in expenses]
        
        response = authenticated_client.delete(
            "/api/expenses/bulk",
            json={"ids": expense_ids}
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify all deleted
        remaining = test_db.query(Expense).filter(Expense.id.in_(expense_ids)).count()
        assert remaining == 0


class TestExpenseValidation:
    """Test expense validation rules"""
    
    @pytest.mark.database
    def test_expense_amount_precision(self, authenticated_client: TestClient):
        """Test that expense amounts handle decimal precision correctly"""
        expense_data = {
            "description": "Precision Test",
            "amount": 123.456789,  # More than 2 decimal places
            "vendor": "Test Vendor",
            "category": "materials"
        }
        
        response = authenticated_client.post(
            "/api/expenses",
            json=expense_data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        # Should be rounded to 2 decimal places
        assert float(data["amount"]) == 123.46
    
    @pytest.mark.database
    def test_expense_category_validation(self, authenticated_client: TestClient):
        """Test that only valid categories are accepted"""
        expense_data = {
            "description": "Category Test",
            "amount": 100.00,
            "vendor": "Test Vendor",
            "category": "invalid_category"
        }
        
        response = authenticated_client.post(
            "/api/expenses",
            json=expense_data
        )
        
        # Depending on your validation, this might be 422 or 400
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST
        ]
