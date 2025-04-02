import os
import platform
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from dotenv import load_dotenv

# Carrega variáveis de ambiente no modo de desenvolvimento
if os.getenv("ENVIRONMENT") != "production":
    load_dotenv()

# Importa configurações de logging e banco de dados
from logging_config import log_exceptions_middleware, setup_logging
from database import engine, Base
from routes import demonstracoes_routes, operadoras_routes

# Configura o banco de dados
Base.metadata.create_all(bind=engine)

# Cria a aplicação FastAPI
fastapi_app = FastAPI(title="Backend FastAPI com PostgreSQL")

# Configura o logging
setup_logging()

# Adiciona middlewares
fastapi_app.middleware("http")(log_exceptions_middleware)
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui as rotas
fastapi_app.include_router(operadoras_routes.router)
fastapi_app.include_router(demonstracoes_routes.router)

# Rota raiz
@fastapi_app.get("/")
def read_root():
    return {"message": "Bem-vindo ao backend FastAPI com PostgreSQL!"}

# Adiciona suporte WSGI para Gunicorn
application = WSGIMiddleware(fastapi_app)

# Executa o servidor com base no sistema operacional
if __name__ == "__main__":
    if platform.system() == "Windows":
        # Executa com Uvicorn no Windows
        import uvicorn
        uvicorn.run("main:fastapi_app", host="0.0.0.0", port=8080)
    else:
        # Executa com Gunicorn no Linux
        os.system("gunicorn --bind :8080 --workers 1 --timeout 600 main:application")