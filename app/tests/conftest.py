import os
import pytest
from cryptography.fernet import Fernet

# Force SQLite test URL globally for all tests BEFORE any app models/modules are imported
os.environ["DATABASE_URL"] = "sqlite:///./test_temp.db"
os.environ["INTERNAL_DATABASE_URL"] = "sqlite:///./test_temp.db"
os.environ["ENVIRONMENT"] = "testing"
os.environ["JWT_SECRET_KEY"] = "TEST_SECRET_KEY"
os.environ["VIBRANIUM_ENCRYPTION_KEY"] = Fernet.generate_key().decode()
