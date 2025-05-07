from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from data.models import Base, UserCreate, UserResponse, UserUpdate, UserWithTasks
from data.models import TaskCreate, TaskResponse, TaskUpdate
import operations.operations_db as ops
from utils.connection_db import engine, get_db

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="User Tasks API",
    description="API for managing users and tasks - Partial Project",
    version="1.0.0",
    docs_url="/docs"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the User Tasks API"}


# User endpoints
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user with the provided information
    """
    db_user_by_username = ops.get_user_by_username(db, username=user.username)
    if db_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    db_user_by_email = ops.get_user_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    return ops.create_user(db=db, user_data=user)


@app.get("/users/", response_model=List[UserResponse], tags=["Users"])
def read_users(
        skip: int = 0,
        limit: int = 100,
        active: Optional[bool] = None,
        premium: Optional[bool] = None,
        db: Session = Depends(get_db)
):
    """
    Get all users with optional filtering by active and premium status
    """
    if active is True:
        users = ops.get_active_users(db, skip=skip, limit=limit)
    elif premium is True:
        users = ops.get_premium_users(db, skip=skip, limit=limit)
    else:
        users = ops.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by ID
    """
    db_user = ops.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


@app.get("/users/{user_id}/details", response_model=UserWithTasks, tags=["Users"])
def read_user_with_tasks(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by ID with all their tasks
    """
    db_user = ops.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


@app.put("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user's information
    """
    db_user = ops.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if username or email would cause conflict
    if user.username and user.username != db_user.username:
        existing_user = ops.get_user_by_username(db, username=user.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    if user.email and user.email != db_user.email:
        existing_user = ops.get_user_by_email(db, email=user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    return ops.update_user(db=db, user_id=user_id, user_data=user)


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user
    """
    db_user = ops.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    result = ops.delete_user(db=db, user_id=user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user"
        )
    return None


# Task endpoints
@app.post("/users/{user_id}/tasks/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
def create_task_for_user(user_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new task for a specific user
    """
    db_user = ops.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return ops.create_task(db=db, task_data=task, user_id=user_id)


@app.get("/tasks/", response_model=List[TaskResponse], tags=["Tasks"])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all tasks
    """
    tasks = ops.get_tasks(db, skip=skip, limit=limit)
    return tasks


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
def read_task(task_id: int, db: Session = Depends(get_db)):
    """
    Get a specific task by ID
    """
    db_task = ops.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return db_task


@app.get("/users/{user_id}/tasks/", response_model=List[TaskResponse], tags=["Tasks"])
def read_user_tasks(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all tasks for a specific user
    """
    db_user = ops.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    tasks = ops.get_user_tasks(db, user_id=user_id, skip=skip, limit=limit)
    return tasks


@app.put("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    """
    Update a task
    """
    db_task = ops.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return ops.update_task(db=db, task_id=task_id, task_data=task)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Delete a task
    """
    db_task = ops.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    result = ops.delete_task(db=db, task_id=task_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting task"
        )
    return None


# Run with uvicorn
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    # Usar 127.0.0.1 en lugar de 0.0.0.0 para desarrollo local
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)