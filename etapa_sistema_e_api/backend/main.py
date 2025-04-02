# backend/main.py
from fastapi import FastAPI

from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware

if os.getenv("ENVIRONMENT") != "production":
    load_dotenv()


from logging_config import log_exceptions_middleware, setup_logging

from database import engine, Base
from routes import (
    demonstracoes_routes,
    operadoras_routes,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Backend FastAPI com PostgreSQL")

setup_logging()

app.middleware("http")(log_exceptions_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(operadoras_routes.router)
app.include_router(demonstracoes_routes.router)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao backend FastAPI com PostgreSQL!"}

application = WSGIMiddleware(app)
