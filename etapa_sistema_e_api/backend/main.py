# backend/main.py
from fastapi import FastAPI
from database import engine, Base
from routes import router as api_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Backend FastAPI com PostgreSQL")

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao backend FastAPI com PostgreSQL!"}