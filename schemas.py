from __future__ import annotations
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    password: str
    
class ShowArticleUser(BaseModel):
    name: str
    email: str

class Article(BaseModel):
    title: str
    content: str
    user_id: int
    
class ArticleEdit(BaseModel):
    title: str
    content: str
    
class ShowUserArticle(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    
class ShowUser(BaseModel):
    id: int
    name: str
    email: str
    articles: list[ShowUserArticle]
    
class ShowArticle(BaseModel):
    id: int
    title: str
    content: str
    user: ShowArticleUser
    
class Login(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
    
class Question(BaseModel):
    id: int
    question: str
    lang: str
    
class Sentence(BaseModel):
    sentence: str
    lang: str