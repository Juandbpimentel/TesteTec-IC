from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func
from models import DemonstracaoContabil
from schemas import DemonstracaoContabilListagemDTO, DemonstracaoContabilDTO
from typing import List, Optional


class DemonstracoesResponse(BaseModel):
    demonstracoes: List[DemonstracaoContabilListagemDTO]
    next_cursor: Optional[int]

def get_demonstracoes(
    session: Session,
    limit: int,
    start_cursor: Optional[int],
    trimestre: Optional[int],
    ano: Optional[int],
    descricao: Optional[str],
    registro_operadora: Optional[str],
) -> List[DemonstracaoContabilListagemDTO]:
    query = session.query(DemonstracaoContabil).order_by(DemonstracaoContabil.id)

    if start_cursor:
        query = query.filter(DemonstracaoContabil.id > start_cursor)

    if trimestre:
        query = query.filter(DemonstracaoContabil.trimestre == trimestre)
    if ano:
        query = query.filter(DemonstracaoContabil.ano == ano)
    if descricao:
        query = query.filter(func.unaccent(DemonstracaoContabil.descricao).ilike(func.unaccent(f"%{descricao}%")))
    if registro_operadora:
        query = query.filter(DemonstracaoContabil.registro_operadora == registro_operadora)

    if limit > 0:
        query = query.limit(limit)

    demonstracoes = query.all()
    return [DemonstracaoContabilListagemDTO.model_validate(demo) for demo in demonstracoes]

def get_demonstracao_by_id(session: Session, id: int) -> Optional[DemonstracaoContabilDTO]:
    """
    Retorna uma demonstração contábil pelo ID, incluindo os dados da operadora associada.
    """
    demonstracao = session.query(DemonstracaoContabil).options(
        joinedload(DemonstracaoContabil.operadora)  # Faz o joinedload da operadora associada
    ).filter(DemonstracaoContabil.id == id).first()

    if demonstracao:
        return DemonstracaoContabilDTO.model_validate(demonstracao)
    return None


def get_descricoes(session: Session) -> List[str]:
    query = session.query(DemonstracaoContabil.descricao).distinct().order_by(DemonstracaoContabil.descricao)
    return [descricao for descricao, in query.all()]


def get_trimestres_e_anos(session: Session) -> List[dict]:
    query = session.query(
        DemonstracaoContabil.trimestre,
        DemonstracaoContabil.ano
    ).distinct().order_by(
        DemonstracaoContabil.ano,
        DemonstracaoContabil.trimestre
    )
    return [{"trimestre": trimestre, "ano": ano} for trimestre, ano in query.all()]