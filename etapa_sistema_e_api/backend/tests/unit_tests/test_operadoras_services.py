import pytest
from unittest.mock import MagicMock
from services.operadoras_service import get_operadoras, get_ufs, get_modalidades, OperadorasResponse

def test_get_operadoras():
    session = MagicMock()
    session.query.return_value.count.return_value = 0
    session.query.return_value.filter.return_value.all.return_value = []
    response = get_operadoras(session, limit=10, registro_operadora=None, cnpj=None, razao_social=None, nome_fantasia=None, modalidade=None, regiao_de_comercializacao=None, start_cursor=None, cidade=None, uf=None)
    assert response.operadoras == []
    assert response.total_elementos == 0

def test_get_ufs():
    session = MagicMock()
    session.query.return_value.distinct.return_value.order_by.return_value.all.return_value = [("SP",), ("RJ",)]
    response = get_ufs(session)
    assert response == ["SP", "RJ"]

def test_get_modalidades():
    session = MagicMock()
    session.query.return_value.distinct.return_value.order_by.return_value.all.return_value = [("Medicina de Grupo",), ("Odontologia",)]
    response = get_modalidades(session)
    assert response == ["Medicina de Grupo", "Odontologia"]