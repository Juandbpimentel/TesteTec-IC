import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@patch("backend.routes.demonstracoes_routes.get_demonstracoes")
def test_read_demonstracoes(mock_get_demonstracoes):
    mock_get_demonstracoes.return_value = {"demonstracoes": [], "total_elementos": 0}
    response = client.get("/api/demonstracoes/?limit=5")
    assert response.status_code == 200
    assert response.json() == {"demonstracoes": [], "total_elementos": 0}

@patch("backend.routes.demonstracoes_routes.get_descricoes")
def test_select_descricoes(mock_get_descricoes):
    mock_get_descricoes.return_value = ["Receita", "Despesa"]
    response = client.get("/api/demonstracoes/select_descricoes")
    assert response.status_code == 200
    assert response.json() == ["Receita", "Despesa"]

@patch("backend.routes.demonstracoes_routes.get_trimestres_e_anos")
def test_select_trimestres_e_anos(mock_get_trimestres_e_anos):
    mock_get_trimestres_e_anos.return_value = [{"trimestre": 1, "ano": 2023}, {"trimestre": 2, "ano": 2023}]
    response = client.get("/api/demonstracoes/select_trimestres_e_anos")
    assert response.status_code == 200
    assert response.json() == [{"trimestre": 1, "ano": 2023}, {"trimestre": 2, "ano": 2023}]