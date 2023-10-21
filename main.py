from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine

from routers import authentication, users, articles

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authentication.router)
app.include_router(users.router)
app.include_router(articles.router)

@app.get("/")
async def root():
    return {"message": "Hello AI Question & Answer Applications!"}
