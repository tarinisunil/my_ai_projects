from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional


app = FastAPI()


@app.post("/add/", response_model=int, tags=["add"], operation_id="add")
async def add(a: int, b: int):
    """
    Add two integers
    """
    return a+b