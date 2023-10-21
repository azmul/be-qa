from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated
from transformers import pipeline
from googletrans import Translator
from oauth2 import get_current_user
import models, schemas, database

router = APIRouter(
    prefix="/api/v1/answers",
    tags=["Answers"],
)

db_dependency = Annotated[Session, Depends(database.get_db)]

translator = Translator()

model_name = "deepset/roberta-base-squad2"

# download model
qa_model = pipeline('question-answering', model=model_name, tokenizer=model_name)

# GET Answer by User ID
@router.post("/", status_code=status.HTTP_200_OK)
async def get_answer(params: schemas.Question, db: db_dependency):
    articles = db.query(models.Article).filter(models.Article.user_id == params.id).all()
    if articles is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Articles not found")
    
    user_context = ""
    for article in articles:
       user_context += article.content  
       
    if not user_context:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User context not found") 
    
    q_translation = translator.translate(params.question, dest="en")
    qa_response = qa_model(question = q_translation.text, context = user_context)
    translation = translator.translate(qa_response["answer"], dest=params.lang)
    return {"answer": translation.text, "lang": params.lang, "score": qa_response["score"]}

@router.post("/translate")
async def translate(params: schemas.Sentence):
    translation = translator.translate(params.sentence, dest=params.lang)
    return {"translate": translation.text, "src": translation.src}