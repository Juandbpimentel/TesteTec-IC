from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from google.cloud.sql.connector import Connector
import os



# URL de conexão padrão
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgresjuandbpimentel@localhost:5432/postgres")
INSTANCE_CONNECTION_NAME_GCLOUD = os.getenv("INSTANCE_CONNECTION_NAME_GCLOUD", "testetec-ic:southamerica-east1:testetec-id-postgres")
USERNAME = os.getenv("USER_NAME", "postgres")
PASSWORD = os.getenv("PASSWORD", "senha")
DB_NAME = os.getenv("DB_NAME", "nome_do_banco")

# Inicializa o conector do Google Cloud SQL
connector = Connector()

def get_connection():
    """
    Retorna uma conexão com o banco de dados usando o conector do Google Cloud SQL.
    """
    print("Conectando ao banco de dados usando o conector do Google Cloud SQL...")
    print(f"Conexão: {INSTANCE_CONNECTION_NAME_GCLOUD}")
    print(f"Usuário: {USERNAME}")
    print(f"Banco de dados: {DB_NAME}")
    print(f"Senha: {PASSWORD}")
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME_GCLOUD,  # Substitua pelo nome da conexão do Cloud SQL
        "pg8000",  # Driver para PostgreSQL
        user=f"{USERNAME}",  # Substitua pelo nome de usuário do banco
        password=f"{PASSWORD}",  # Substitua pela senha do banco
        db=f"{DB_NAME}",  # Substitua pelo nome do banco de dados
    )
    return conn

# Tenta criar o engine usando a URL de conexão
try:
    engine = create_engine(DATABASE_URL, echo=True)
    # Testa a conexão
    with engine.connect() as conn:
        print("Conexão com o banco de dados via DATABASE_URL bem-sucedida.")
except Exception as e:
    print(f"Falha ao conectar usando DATABASE_URL: {e}")
    print("Tentando conectar usando o conector do Google Cloud SQL...")
    try:
        engine = create_engine(
            "postgresql+pg8000://",  # Driver para PostgreSQL com pg8000
            creator=get_connection,  # Função para criar a conexão
            echo=True
        )
        # Testa a conexão
        with engine.connect() as conn:
            print("Conexão com o banco de dados via Google Cloud SQL bem-sucedida.")
    except Exception as e:
        print(f"Falha ao conectar usando o conector do Google Cloud SQL: {e}")
        raise

# Configuração do SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()