from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    email = Column(String(100), unique=True)
    password = Column(String(100))
    
    articles = relationship("Article", back_populates="user")
    
    
class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500))
    content = Column(String(3500))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="articles")