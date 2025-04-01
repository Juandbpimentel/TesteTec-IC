from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas import DemonstracaoContabilDTO
from services.demonstracoes_service import (
    get_demonstracoes,
    get_descricoes,
    get_demonstracao_by_id,
    get_trimestres_e_anos,
    DemonstracoesResponse
)
from error_response import ErrorResponse
from typing import Optional, List

router = APIRouter(
    prefix="/api/demonstracoes",
    tags=["Demonstrações"],
)

@router.get("/", response_model=DemonstracoesResponse)
def read_demonstracoes(
    session: Session = Depends(get_db),
    limit: int = Query(10, ge=0),
    start_cursor: Optional[int] = Query(None),
    trimestre: Optional[int] = Query(None),
    ano: Optional[int] = Query(None),
    descricao: Optional[str] = Query(None),
    registro_operadora: Optional[str] = Query(None),
):
    """
    Lista demonstrações contábeis com paginação baseada em cursor e filtros opcionais.
    """
    try:
        demonstracoes_dto = get_demonstracoes(
            session, limit, start_cursor, trimestre, ano, descricao, registro_operadora
        )
        next_cursor = demonstracoes_dto[-1].id if demonstracoes_dto else None
        return DemonstracoesResponse(demonstracoes=demonstracoes_dto, next_cursor=next_cursor)
    except Exception as e:
        raise ErrorResponse(500, f"Erro ao listar demonstrações contábeis: {str(e)}")


@router.get("/select_descricoes", response_model=List[str])
def select_descricoes(session: Session = Depends(get_db)):
    """
    Retorna a lista de descrições distintas das demonstrações contábeis.
    """
    try:
        return get_descricoes(session)
    except Exception as e:
        raise ErrorResponse(500, f"Erro ao buscar descrições: {str(e)}")


@router.get("/select_trimestres_e_anos", response_model=List[dict])
def select_trimestres_e_anos(session: Session = Depends(get_db)):
    """
    Retorna os pares distintos de trimestres e anos disponíveis no sistema.
    """
    try:
        return get_trimestres_e_anos(session)
    except Exception as e:
        raise ErrorResponse(500, f"Erro ao buscar trimestres e anos: {str(e)}")


@router.get("/{id}", response_model=DemonstracaoContabilDTO)
def read_demonstracao(
    id: int,
    session: Session = Depends(get_db),
):
    """
    Retorna uma demonstração contábil pelo ID.
    """
    try:
        demonstracao = get_demonstracao_by_id(session, id)
        if not demonstracao:
            raise ErrorResponse(404, f"Demonstração contábil com ID {id} não encontrada.")
        return demonstracao
    except ErrorResponse as e:
        raise e
    except Exception as e:
        raise ErrorResponse(500, f"Erro ao buscar demonstração contábil: {str(e)}")