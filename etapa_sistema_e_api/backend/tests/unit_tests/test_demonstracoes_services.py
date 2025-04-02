import pytest
from unittest.mock import MagicMock
from services.demonstracoes_service import get_demonstracoes, get_descricoes, get_trimestres_e_anos, DemonstracoesResponse

def test_get_demonstracoes():
    session = MagicMock()
    session.query.return_value.count.return_value = 0
    session.query.return_value.filter.return_value.all.return_value = []
    response = get_demonstracoes(session, limit=10, start_cursor=None, trimestre=None, ano=None, descricao=None, registro_operadora=None)
    assert response.demonstracoes == []
    assert response.total_elementos == 0

def test_get_descricoes():
    session = MagicMock()
    session.query.return_value.distinct.return_value.order_by.return_value.all.return_value = [("Receita",), ("Despesa",)]
    response = get_descricoes(session)
    assert response == ["Receita", "Despesa"]

def test_get_trimestres_e_anos():
    session = MagicMock()
    session.query.return_value.distinct.return_value.order_by.return_value.all.return_value = [(1, 2023), (2, 2023)]
    response = get_trimestres_e_anos(session)
    assert response == [{"trimestre": 1, "ano": 2023}, {"trimestre": 2, "ano": 2023}]