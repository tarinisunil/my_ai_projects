from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

app = FastAPI()
OLLAMA_HOST = "http://10.42.37.169:11434"

class QuestionRequest(BaseModel):
    question: str
    
@app.post("/query/", response_model=str, tags=["ollama", "query"], operation_id="query_ollama")
async def query_ollama(req:QuestionRequest):
    """
    Query ollama with a prompt
    """
    
    question = req.question
    print(question)
    template = """You are a helpful and polite assistant that provides information to any query asked by the user.
Question:
{question}

Answer clearly and concisely. If you don’t know the answer, say so."""

    # Build the prompt
    prompt = PromptTemplate(
        template=template,
        input_variables=[ "question"]
    )

    # Initialize Ollama LLM
    llm = OllamaLLM(base_url=OLLAMA_HOST, model="gemma3")

    # Combine prompt + LLM using RunnableSequence style
    chain = prompt | llm
    response = chain.invoke({ "question": question})
    return response