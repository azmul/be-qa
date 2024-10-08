from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated
from oauth2 import get_current_user
from database import engine
import models, schemas, database

router = APIRouter(
    prefix="/api/v1/articles",
    tags=['Articles']
)

db_dependency = Annotated[Session, Depends(database.get_db)]

# CREATE Article
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_article(article: schemas.Article, db: db_dependency):
    new_article = models.Article(user_id=article.user_id, title=article.title, content=article.content)
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    return new_article 

# GET All Article
@router.get("/", status_code=status.HTTP_200_OK, response_model=list[schemas.ShowArticle])
async def read_all_articles(db: db_dependency, current_user: schemas.User = Depends(get_current_user)):
    articles = db.query(models.Article).all()
    return articles
   
# GET Article by ID 
@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.ShowArticle)
async def read_article(id: int, db: db_dependency):
    article = db.query(models.Article).filter(models.Article.id == id).first()
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return article

# UPDATE Article by ID 
@router.patch("/{id}", status_code=status.HTTP_202_ACCEPTED)
async def update_article(id:int, article: schemas.ArticleEdit, db: db_dependency): 
    with Session(engine) as session:
        db_article = session.get(models.Article, id)
        if not db_article:
           raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
        article_data = article.dict(exclude_unset=True)
        for key, value in article_data.items():
            setattr(db_article, key, value)
        session.add(db_article)
        session.commit()
        session.refresh(db_article)
        return db_article

# DELETE Article by ID 
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(id: int, db: db_dependency):
    article = db.query(models.Article).filter(models.Article.id == id).first()
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    db.delete(article)
    db.commit()
    return article