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

# download model
# qa_model_bert = pipeline('question-answering', model="bert-large-uncased-whole-word-masking-finetuned-squad")
# qa_model_timpal = pipeline('question-answering', model="timpal0l/mdeberta-v3-base-squad2")
qa_model_roberta = pipeline('question-answering', model="deepset/roberta-base-squad2")
qa_model_distilbert = pipeline('question-answering', model="distilbert-base-uncased-distilled-squad")
qa_model_deepset_bert = pipeline('question-answering', model="deepset/bert-large-uncased-whole-word-masking-squad2")

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
    
    # qa_response_timpal = qa_model_timpal(question = q_translation.text, context = user_context)
    # qa_response_bert = qa_model_bert(question = q_translation.text, context = user_context)
    qa_response_roberta = qa_model_roberta(question = q_translation.text, context = user_context)
    translation_roberta = translator.translate(qa_response_roberta["answer"], dest=params.lang)
    qa_response_roberta["translate_text"] = translation_roberta.text
    qa_response_roberta["model"] = "roberta"
    
    qa_response_distilbert = qa_model_distilbert(question = q_translation.text, context = user_context)
    translation_distilbert = translator.translate(qa_response_distilbert["answer"], dest=params.lang)
    qa_response_distilbert["translate_text"] = translation_distilbert.text
    qa_response_distilbert["model"] = "distilbert"
    
    qa_response_deepset_bert = qa_model_deepset_bert(question = q_translation.text, context = user_context)
    translation_deepset_bert = translator.translate(qa_response_deepset_bert["answer"], dest=params.lang)
    qa_response_deepset_bert["translate_text"] = translation_deepset_bert.text
    qa_response_deepset_bert["model"] = "deepset_bert"


    # translation = translator.translate(qa_response_roberta["answer"], dest=params.lang)
    # return {"answer": translation.text, "lang": params.lang}
    return { "data": [qa_response_deepset_bert,  qa_response_roberta, qa_response_distilbert]}

@router.post("/translate")
async def translate(params: schemas.Sentence):
    translation = translator.translate(params.sentence, dest=params.lang)
    return {"translate": translation.text, "src": translation.src}