from fastapi import APIRouter, HTTPException, Depends, status
from datetime import timedelta
from sqlalchemy.orm import Session
from typing import Annotated
from hashing import Hash
import JWTtoken
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


import models, schemas, database

router = APIRouter(
    tags=['Authentication']
)

db_dependency = Annotated[Session, Depends(database.get_db)]

@router.post("/login", response_model=schemas.Token)
async def login(request: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = db.query(models.User).filter(models.User.email == request.username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # password verify
    if not Hash.verify(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="email or password wrong")
    
    access_token_expires = timedelta(minutes=JWTtoken.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = JWTtoken.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}