import requests

def test_status():
    response = requests.get("http://localhost:8080/")
    assert response.status_code == 201
    assert response.json() == {"message": "Bem-vindo ao backend FastAPI com PostgreSQL!"}