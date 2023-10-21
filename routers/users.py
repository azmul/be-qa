from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated
from hashing import Hash
from oauth2 import get_current_user
import models, schemas, database

router = APIRouter(
    prefix="/users",
    tags=["User"],
)

db_dependency = Annotated[Session, Depends(database.get_db)]

# CREATE User
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.User, db: db_dependency):
    new_user = models.User(name=user.name, email=user.email, password=Hash.bcrypt(user.password))
    db.add(new_user)   
    db.commit()
    db.refresh(new_user)
    return new_user

# GET User by ID
@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=schemas.ShowUser)
async def read_user(user_id: int, db: db_dependency, current_user: schemas.User = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user