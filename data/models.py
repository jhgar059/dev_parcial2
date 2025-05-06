from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class UserType(str, Enum):
    REGULAR = "regular"
    PREMIUM = "premium"

class UserBase(BaseModel):
    name: str = Field(..., description="Nombre del usuario")
    email: str = Field(..., description="Correo electrónico del usuario")
    age: int = Field(..., description="Edad del usuario")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="Estado del usuario")
    user_type: UserType = Field(default=UserType.REGULAR, description="Tipo de usuario")

class UserCreate(UserBase):
    password: str = Field(..., description="Contraseña del usuario")

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    status: Optional[UserStatus] = None
    user_type: Optional[UserType] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int = Field(..., description="ID único del usuario")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")

    class Config:
        orm_mode = True

class MakePremiumRequest(BaseModel):
    user_type: UserType = Field(UserType.PREMIUM, description="Actualiza el usuario a premium")