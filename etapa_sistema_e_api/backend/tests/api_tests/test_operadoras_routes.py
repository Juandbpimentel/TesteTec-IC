import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from services.operadoras_service import OperadorasResponse
from main import app

client = TestClient(app)


@patch("routes.operadoras_routes.get_operadoras")
def test_read_operadoras(mock_get_operadoras):
    mock_get_operadoras.return_value = OperadorasResponse(
        operadoras=[],
        next_cursor=None,
        total_elementos=0
    )
    response = client.get("/api/operadoras/?limit=5")
    assert response.status_code == 200
    assert response.json() == {"operadoras": [], "next_cursor": None, "total_elementos": 0}

@patch("routes.operadoras_routes.get_maiores_despesas_trimestre")
def test_maiores_despesas_trimestre(mock_get_maiores_despesas_trimestre):
    mock_get_maiores_despesas_trimestre.return_value = []
    response = client.get("/api/operadoras/maiores_despesas_trimestre?descricao=despesa&trimestre=1&ano=2023")
    assert response.status_code == 200
    assert response.json() == []

@patch("routes.operadoras_routes.get_maiores_despesas_ano")
def test_maiores_despesas_ano(mock_get_maiores_despesas_ano):
    mock_get_maiores_despesas_ano.return_value = []
    response = client.get("/api/operadoras/maiores_despesas_ano?descricao=despesa&ano=2023")
    assert response.status_code == 200
    assert response.json() == []

@patch("routes.operadoras_routes.get_ufs")
def test_select_ufs(mock_get_ufs):
    mock_get_ufs.return_value = ["SP", "RJ"]
    response = client.get("/api/operadoras/select_ufs")
    assert response.status_code == 200
    assert response.json() == ["SP", "RJ"]

@patch("routes.operadoras_routes.get_modalidades")
def test_select_modalidades(mock_get_modalidades):
    mock_get_modalidades.return_value = ["Medicina de Grupo", "Odontologia"]
    response = client.get("/api/operadoras/select_modalidades")
    assert response.status_code == 200
    assert response.json() == ["Medicina de Grupo", "Odontologia"]