from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated
from transformers import pipeline
from googletrans import Translator
from oauth2 import get_current_user
import models, schemas, database
from cdifflib import CSequenceMatcher

router = APIRouter(
    prefix="/api/v1/answers",
    tags=["Answers"],
)

db_dependency = Annotated[Session, Depends(database.get_db)]

translator = Translator()

# Define the property of interest (in this case, "age")
property_of_interest = "answer"

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
    qa_response_distilbert = qa_model_distilbert(question = q_translation.text, context = user_context)
    qa_response_deepset_bert = qa_model_deepset_bert(question = q_translation.text, context = user_context)

    results = [qa_response_deepset_bert,  qa_response_roberta, qa_response_distilbert]
    # print(results)
    
    # Find the minimum value of the property using the min() function
    min_value = min(results, key=lambda x: len(x[property_of_interest]))[property_of_interest]
 
    # Filter out objects with the minimum property value
    filtered_results = [obj for obj in results if obj[property_of_interest] != min_value]
    
    calculated_results = []
    
    if not filtered_results:
        calculated_results = results
    else:
        calculated_results = filtered_results
    
    max_result = max(calculated_results, key=lambda x: len(x[property_of_interest]))
    min_result = min(calculated_results, key=lambda x: len(x[property_of_interest]))
    
    s = CSequenceMatcher(None, max_result["answer"], min_result["answer"])
    ratio = round(s.ratio(), 3) * 100
    
    text = ""
    if ratio < 60:
        text = max_result["answer"] + ". " + min_result["answer"]
    else:
        text = max_result["answer"]

    translation = translator.translate(text, dest=params.lang)
    return {"answer": translation.text, "lang": params.lang}

@router.post("/translate")
async def translate(params: schemas.Sentence):
    translation = translator.translate(params.sentence, dest=params.lang)
    return {"translate": translation.text, "src": translation.src}