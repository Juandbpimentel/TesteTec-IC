from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas import OperadoraAtivaDTO, OperadoraAtivaDespesaDTO
from services.operadoras_service import (
    get_operadoras,
    get_operadora_by_registro,
    get_maiores_despesas_trimestre,
    get_maiores_despesas_ano,
    get_ufs,
    get_modalidades,
    get_regioes_de_comercializacao,
    OperadorasResponse
)
from error_response import ErrorResponse
from typing import Optional, List

router = APIRouter(
    prefix="/api/operadoras",
    tags=["Operadoras"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=OperadorasResponse)
def read_operadoras(
    session: Session = Depends(get_db),
    limit: int = Query(10, ge=0),
    start_cursor: Optional[str] = Query(None),
    registro_operadora: Optional[str] = Query(None),
    cnpj: Optional[str] = Query(None),
    razao_social: Optional[str] = Query(None),
    nome_fantasia: Optional[str] = Query(None),
    modalidade: Optional[str] = Query(None),
    regiao_de_comercializacao: Optional[int] = Query(None),
    cidade: Optional[str] = Query(None),
    uf: Optional[str] = Query(None),
):
    try:
        operadoras_response = get_operadoras(
            session=session,
            limit=limit,
            start_cursor=start_cursor,
            registro_operadora=registro_operadora,
            cnpj=cnpj,
            razao_social=razao_social,
            nome_fantasia=nome_fantasia,
            modalidade=modalidade,
            regiao_de_comercializacao=regiao_de_comercializacao,
            cidade=cidade,
            uf=uf,
        )
        next_cursor = operadoras_response.operadoras[-1].registro_operadora if operadoras_response.operadoras else None
        return OperadorasResponse(
            operadoras=operadoras_response.operadoras,
            next_cursor=next_cursor,
            total_elementos=operadoras_response.total_elementos,
        )
    except Exception as e:
        raise ErrorResponse(500, f"Erro ao listar operadoras: {str(e)}")


@router.get("/maiores_despesas_trimestre", response_model=List[OperadoraAtivaDespesaDTO])
def maiores_despesas_trimestre(
    descricao: Optional[str] = None,
    trimestre: Optional[int] = None,
    ano: Optional[int] = None,
    session: Session = Depends(get_db),
):
    try:
        if not descricao:
            raise ErrorResponse(400, "O parâmetro 'descricao' é obrigatório.")
        return get_maiores_despesas_trimestre(session, descricao, trimestre, ano)
    except ErrorResponse as e:
        raise e
    except Exception as e:
        raise ErrorResponse(500, f"Erro ao buscar maiores despesas no trimestre: {str(e)}")


@router.get("/maiores_despesas_ano", response_model=List[OperadoraAtivaDespesaDTO])
def maiores_despesas_ano(
    descricao: Optional[str] = None,
    ano: Optional[int] = None,
    session: Session = Depends(get_db),
):
    try:
        if not descricao:
            raise ErrorResponse(400, "O parâmetro 'descricao' é obrigatório.")
        return get_maiores_despesas_ano(session, descricao, ano)
    except ErrorResponse as e:
        raise e
    except Exception as e:
        raise ErrorResponse(500, f"Erro ao buscar maiores despesas no ano: {str(e)}")


@router.get("/select_ufs", response_model=List[str])
def select_ufs(session: Session = Depends(get_db)):
    try:
        return get_ufs(session)
    except Exception as e:
        raise ErrorResponse(500, f"Erro ao buscar UFs: {str(e)}")


@router.get("/select_modalidades", response_model=List[str])
def select_modalidades(session: Session = Depends(get_db)):
    try:
        return get_modalidades(session)
    except Exception as e:
        raise ErrorResponse(500, f"Erro ao buscar modalidades: {str(e)}")


@router.get("/{registro_operadora}", response_model=OperadoraAtivaDTO)
def read_operadora(registro_operadora: str, session: Session = Depends(get_db)):
    try:
        operadora = get_operadora_by_registro(session, registro_operadora)
        if not operadora:
            raise ErrorResponse(404, f"Operadora com registro {registro_operadora} não encontrada.")
        return OperadoraAtivaDTO.model_validate(operadora)
    except ErrorResponse as e:
        raise e
    except Exception as e:
        raise ErrorResponse(500, f"Erro ao buscar operadora: {str(e)}")
