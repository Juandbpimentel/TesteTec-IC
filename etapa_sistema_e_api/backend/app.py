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

fastapi_app = FastAPI(title="Backend FastAPI com PostgreSQL")

setup_logging()

fastapi_app.middleware("http")(log_exceptions_middleware)
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fastapi_app.include_router(operadoras_routes.router)
fastapi_app.include_router(demonstracoes_routes.router)

@fastapi_app.get("/")
def read_root():
    return {"message": "Bem-vindo ao backend FastAPI com PostgreSQL!"}

app = WSGIMiddleware(fastapi_app)
