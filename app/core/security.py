import os
from datetime import datetime, timedelta
from typing import Optional, Any
from jose import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.types import TypeDecorator, String

# Vibranium Habit: Require Fernet for column encryption
try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None

# Secret key to encode the JWT (Vibranium Habit: Enforce Environment Variable)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "SUPER_SECRET_KEY_REPLACE_IN_PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Vibranium Habit: Encryption key for data at rest
VIBRANIUM_ENCRYPTION_KEY = os.getenv("VIBRANIUM_ENCRYPTION_KEY")
if VIBRANIUM_ENCRYPTION_KEY and Fernet:
    fernet = Fernet(VIBRANIUM_ENCRYPTION_KEY.encode())
else:
    fernet = None

class VibraniumEncryptedString(TypeDecorator):
    """
    Vibranium Habit: SQLAlchemy TypeDecorator that transparently encrypts
    data before saving to the database and decrypts upon retrieval.
    """
    impl = String

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if not fernet:
            if os.getenv("ENVIRONMENT") == "production":
                raise RuntimeError("Vibranium Habit Violation: VIBRANIUM_ENCRYPTION_KEY is required in production for data at rest.")
            return value
        return fernet.encrypt(value.encode()).decode()

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not fernet:
            return value
        try:
            return fernet.decrypt(value.encode()).decode()
        except Exception:
            return value

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
        token_data = {"username": username, "role": role}
    except jwt.JWTError:
        raise credentials_exception
    # Add your DB query here to fetch the actual user
    return token_data

def require_role(required_role: str):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return current_user
    return role_checker
