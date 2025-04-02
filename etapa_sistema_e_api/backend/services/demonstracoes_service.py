from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func
from models import DemonstracaoContabil
from schemas import DemonstracaoContabilListagemDTO, DemonstracaoContabilDTO
from typing import List, Optional


class DemonstracoesResponse(BaseModel):
    demonstracoes: List[DemonstracaoContabilListagemDTO]
    next_cursor: Optional[int]
    total_elementos: int

def get_demonstracoes(
    session: Session,
    limit: int,
    start_cursor: Optional[int],
    trimestre: Optional[int],
    ano: Optional[int],
    descricao: Optional[str],
    registro_operadora: Optional[str],
) -> DemonstracoesResponse:
    base_query = session.query(DemonstracaoContabil)

    if trimestre:
        base_query = base_query.filter(DemonstracaoContabil.trimestre == trimestre)
    if ano:
        base_query = base_query.filter(DemonstracaoContabil.ano == ano)
    if descricao:
        base_query = base_query.filter(func.unaccent(DemonstracaoContabil.descricao).ilike(func.unaccent(f"%{descricao}%")))
    if registro_operadora:
        base_query = base_query.filter(DemonstracaoContabil.registro_operadora == registro_operadora)

    total_elementos = base_query.count()
    if start_cursor:
        base_query = base_query.filter(DemonstracaoContabil.id > start_cursor)

    query = base_query.order_by(DemonstracaoContabil.id)
    if limit > 0:
        query = query.limit(limit)

    demonstracoes = query.all()

    next_cursor = demonstracoes[-1].id if len(demonstracoes) == limit else None

    return DemonstracoesResponse(
        demonstracoes=[DemonstracaoContabilListagemDTO.model_validate(demo) for demo in demonstracoes],
        next_cursor=next_cursor,
        total_elementos=total_elementos
    )

def get_demonstracao_by_id(session: Session, id: int) -> Optional[DemonstracaoContabilDTO]:
    demonstracao = session.query(DemonstracaoContabil).options(
        joinedload(DemonstracaoContabil.operadora)
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