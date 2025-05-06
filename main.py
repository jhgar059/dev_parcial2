from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from operations.operations_db import User
from utils.connection_db import get_db
from data.models import UserCreate, UserResponse, UserUpdate, MakePremiumRequest, UserStatus, UserType
from datetime import datetime
import uvicorn
import hashlib

app = FastAPI(
    title="API de Usuarios",
    description="API para gestionar usuarios con soporte para usuarios Premium e Inactivos",
    version="1.0.0"
)


def hash_password(password: str) -> str:
    """Simple función para hashear contraseñas"""
    return hashlib.sha256(password.encode()).hexdigest()


@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Usuarios"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo usuario en el sistema.

    - **name**: Nombre del usuario
    - **email**: Correo electrónico (debe ser único)
    - **age**: Edad del usuario
    - **password**: Contraseña (será hasheada)
    - **status**: Estado del usuario (ACTIVE por defecto)
    - **user_type**: Tipo de usuario (REGULAR por defecto)
    """
    # Verificar si el email ya existe
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    # Crear nuevo usuario
    hashed_password = hash_password(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        age=user.age,
        password=hashed_password,
        status=user.status.value,
        user_type=user.user_type.value,
        created_at=datetime.now()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        age=new_user.age,
        status=UserStatus(new_user.status),
        user_type=UserType(new_user.user_type),
        created_at=new_user.created_at,
        updated_at=new_user.updated_at
    )


@app.get("/users/", response_model=List[UserResponse], tags=["Usuarios"])
def get_all_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """
    Obtiene una lista de todos los usuarios registrados.

    - **skip**: Número de registros a saltar (para paginación)
    - **limit**: Número máximo de registros a devolver
    """
    users = db.query(User).offset(skip).limit(limit).all()

    return [
        UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            age=user.age,
            status=UserStatus(user.status),
            user_type=UserType(user.user_type),
            created_at=user.created_at,
            updated_at=user.updated_at
        ) for user in users
    ]


@app.get("/users/inactive", response_model=List[UserResponse], tags=["Usuarios"])
def get_inactive_users(db: Session = Depends(get_db)):
    """
    Obtiene todos los usuarios con estado inactivo.
    """
    users = db.query(User).filter(User.status == UserStatus.INACTIVE.value).all()

    return [
        UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            age=user.age,
            status=UserStatus(user.status),
            user_type=UserType(user.user_type),
            created_at=user.created_at,
            updated_at=user.updated_at
        ) for user in users
    ]


@app.get("/users/premium", response_model=List[UserResponse], tags=["Usuarios"])
def get_premium_users(
        inactive: Optional[bool] = Query(None, description="Filtrar por usuarios inactivos")
):
    """
    Obtiene todos los usuarios premium, opcionalmente filtrados por estado inactivo.

    - **inactive**: Si se establece a True, devuelve sólo usuarios premium inactivos
    """
    db = next(get_db())
    query = db.query(User).filter(User.user_type == UserType.PREMIUM.value)

    if inactive is not None:
        status_value = UserStatus.INACTIVE.value if inactive else UserStatus.ACTIVE.value
        query = query.filter(User.status == status_value)

    users = query.all()

    return [
        UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            age=user.age,
            status=UserStatus(user.status),
            user_type=UserType(user.user_type),
            created_at=user.created_at,
            updated_at=user.updated_at
        ) for user in users
    ]


@app.get("/users/{user_id}", response_model=UserResponse, tags=["Usuarios"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un usuario específico por su ID.

    - **user_id**: ID único del usuario a consultar
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        age=user.age,
        status=UserStatus(user.status),
        user_type=UserType(user.user_type),
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@app.put("/users/{user_id}", response_model=UserResponse, tags=["Usuarios"])
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    Actualiza los datos de un usuario existente.

    - **user_id**: ID único del usuario a actualizar
    - **user_update**: Datos a actualizar (solo se actualizarán los campos proporcionados)
    """
    # Verificar que el usuario existe
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Actualizar campos si están presentes
    user_data = user_update.dict(exclude_unset=True)

    if "password" in user_data and user_data["password"]:
        user_data["password"] = hash_password(user_data["password"])

    if "status" in user_data and user_data["status"]:
        user_data["status"] = user_data["status"].value

    if "user_type" in user_data and user_data["user_type"]:
        user_data["user_type"] = user_data["user_type"].value

    for key, value in user_data.items():
        setattr(db_user, key, value)

    db_user.updated_at = datetime.now()
    db.commit()
    db.refresh(db_user)

    return UserResponse(
        id=db_user.id,
        name=db_user.name,
        email=db_user.email,
        age=db_user.age,
        status=UserStatus(db_user.status),
        user_type=UserType(db_user.user_type),
        created_at=db_user.created_at,
        updated_at=db_user.updated_at
    )


@app.patch("/users/{user_id}/premium", response_model=UserResponse, tags=["Usuarios"])
def make_user_premium(user_id: int, db: Session = Depends(get_db)):
    """
    Actualiza un usuario a estado Premium.

    - **user_id**: ID único del usuario a actualizar
    """
    # Verificar que el usuario existe
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Actualizar a premium
    db_user.user_type = UserType.PREMIUM.value
    db_user.updated_at = datetime.now()

    db.commit()
    db.refresh(db_user)

    return UserResponse(
        id=db_user.id,
        name=db_user.name,
        email=db_user.email,
        age=db_user.age,
        status=UserStatus(db_user.status),
        user_type=UserType(db_user.user_type),
        created_at=db_user.created_at,
        updated_at=db_user.updated_at
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)