# backend/main.py
from fastapi import FastAPI
from database import engine, Base
from routes import (
    router_operadoras,
    router_demonstracoes,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Backend FastAPI com PostgreSQL")

app.include_router(router_operadoras)
app.include_router(router_demonstracoes)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao backend FastAPI com PostgreSQL!"}
