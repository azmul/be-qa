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

# test model
context = "Monstarlab is a global digital consulting firm and software firm that specializes in strategy, design, and technology. Originating from Japan, the company has expanded its reach with offices around the world. Monstarlab has 1000 employees? Monstarlab offers a wide array of services, ranging from digital product development, UX/UI design, and digital transformation strategies, to name a few. Their team consists of engineers, designers, and consultants who collaborate to create innovative digital solutions tailored to their clients' unique challenges. As digital transformation continues to be a priority for businesses across industries, Monstarlab's expertise positions them as a notable player in the global market, helping brands navigate the complexities of the digital landscape"

# GET Answer by User ID
@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.ShowUser)
async def get_answer_by_user(id: int, db: db_dependency, current_user: schemas.User = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.post("/")
async def get_answer(params: schemas.Question):
    q_translation = translator.translate(params.question, dest="en")
    qa_response = qa_model(question = q_translation.text, context = context)
    translation = translator.translate(qa_response["answer"], dest=params.lang)
    return {"answer": translation.text, "lang": params.lang, "score": qa_response["score"]}

@router.post("/translate")
async def translate(params: schemas.Sentence):
    translation = translator.translate(params.sentence, dest=params.lang)
    return {"translate": translation.text, "src": translation.src}