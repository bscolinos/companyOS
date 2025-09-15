from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import logging
from backend.database.connection import get_database
from backend.database.models import User
from backend.database.operations import UserOperations
from backend.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str
    phone: str = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    is_admin: bool
    created_at: datetime

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    with get_database() as conn:
        user = UserOperations.get_user_by_id(conn, int(user_id))
        if user is None:
            raise credentials_exception
        
        return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    try:
        with get_database() as conn:
            # Check if user already exists
            existing_user = UserOperations.get_user_by_email(conn, user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered"
                )
            
            # Hash password
            hashed_password = get_password_hash(user_data.password)
            
            # Create new user
            new_user = User(
                email=user_data.email,
                username=user_data.username,
                hashed_password=hashed_password,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                phone=user_data.phone
            )
            
            user_id = UserOperations.create_user(conn, new_user)
            created_user = UserOperations.get_user_by_id(conn, user_id)
            
            return UserResponse(
                id=created_user.id,
                email=created_user.email,
                username=created_user.username,
                first_name=created_user.first_name,
                last_name=created_user.last_name,
                is_active=created_user.is_active,
                is_admin=created_user.is_admin,
                created_at=created_user.created_at
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=Token)
async def login_user(user_data: UserLogin):
    """Login user and return access token"""
    try:
        with get_database() as conn:
            # Find user by email
            user = UserOperations.get_user_by_email(conn, user_data.email)
            
            if not user or not verify_password(user_data.password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is inactive"
                )
            
            # Create access token
            access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
            access_token = create_access_token(
                data={"sub": str(user.id)}, expires_delta=access_token_expires
            )
            
            return Token(
                access_token=access_token,
                token_type="bearer",
                expires_in=settings.access_token_expire_minutes * 60
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at
    )

@router.post("/refresh")
async def refresh_token(current_user: User = Depends(get_current_active_user)):
    """Refresh access token"""
    try:
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(current_user.id)}, expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
        
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")
