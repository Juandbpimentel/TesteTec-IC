from app import app as application  # Nome 'application' é obrigatório

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:fastapi_app", host="0.0.0.0", port=8080)