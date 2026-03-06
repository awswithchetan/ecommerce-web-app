from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    cognito_sub: str
    email: EmailStr
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class User(BaseModel):
    id: int
    cognito_sub: str
    email: str
    name: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    created_at: datetime
