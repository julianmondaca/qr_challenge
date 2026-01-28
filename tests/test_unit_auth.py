import pytest
from unittest.mock import MagicMock
from app.src.services.auth_service import AuthService
from app.src.schemas.auth import UserCreate
from fastapi import HTTPException

def test_sign_up_user_already_exists():
    # 1. Setup Mock Repository
    mock_db = MagicMock()
    mock_repo = MagicMock()
    
    # Simulate that get_by_email returns a user (meaning email is taken)
    mock_repo.get_by_email.return_value = {"email": "taken@example.com"}
    
    # 2. Inject the mock repository into the service
    service = AuthService(mock_db)
    service.user_repo = mock_repo
    
    # 3. Test and Assert
    user_data = UserCreate(email="taken@example.com", password="password123")
    
    with pytest.raises(HTTPException) as excinfo:
        service.sign_up(user_data)
    
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Email already registered"
    # Verify the repo was indeed called
    mock_repo.get_by_email.assert_called_once_with("taken@example.com")

def test_authenticate_user_success():
    mock_db = MagicMock()
    mock_repo = MagicMock()
    service = AuthService(mock_db)
    service.user_repo = mock_repo
    
    # Create a dummy user with a known password hash
    password = "secretpassword"
    hashed = service.get_password_hash(password)
    mock_user = MagicMock()
    mock_user.email = "test@example.com"
    mock_user.password_hash = hashed
    mock_user.uuid = "some-uuid"
    
    mock_repo.get_by_email.return_value = mock_user
    
    # Test
    result = service.authenticate_user("test@example.com", password)
    
    assert "access_token" in result
    assert result["token_type"] == "bearer"
