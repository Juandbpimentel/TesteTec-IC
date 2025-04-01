# backend/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import text
from database import get_db

from models import OperadoraAtiva, DemonstracaoContabil
from schemas import OperadoraAtivaCreate, DemonstracaoContabilCreate, OperadoraAtivaListagemDTO, OperadoraAtivaDTO, OperadoraAtivaDespesaDTO, DemonstracaoContabilDTO ,DemonstracaoContabilListagemDTO
from typing import List, Optional


router_operadoras = APIRouter(
    prefix="/api/operadoras",
    tags=["Operadoras"],
    responses={404: {"description": "Not found"}},
)

router_demonstracoes = APIRouter(
    prefix="/api/demonstracoes",
    tags=["Demonstracoes"],
    responses={404: {"description": "Not found"}},
)



@router_operadoras.get("/", response_model=List[OperadoraAtivaListagemDTO])
def read_operadoras(cursor: Optional[str] = None, limit: int = 10, db: Session = Depends(get_db)):

    query = db.query(OperadoraAtiva).order_by(OperadoraAtiva.registro_operadora)


    if cursor:
        query = query.filter(OperadoraAtiva.registro_operadora > cursor)


    operadoras = query.limit(limit).all()


    return [OperadoraAtivaListagemDTO.model_validate(op) for op in operadoras]




@router_demonstracoes.get("/", response_model=List[DemonstracaoContabilListagemDTO])
def read_demonstracoes(cursor: int = None, limit: int = 10, db: Session = Depends(get_db)):

    query = db.query(DemonstracaoContabil).order_by(DemonstracaoContabil.id)

    if cursor:
        query = query.filter(DemonstracaoContabil.id > cursor)

    demonstracoes = query.limit(limit).all()

    return [DemonstracaoContabilListagemDTO.model_validate(demo) for demo in demonstracoes]



@router_demonstracoes.get("/maiores_despesas_trimestre", response_model=List[OperadoraAtivaDespesaDTO])
def maiores_despesas_trimestre(
    descricao: Optional[str] = None,
    trimestre: Optional[int] = None,
    ano: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Retorna as 10 operadoras com maiores despesas no trimestre e ano especificados.
    Se trimestre e ano não forem fornecidos, usa o trimestre e ano anteriores.
    """
    # Define os valores padrão para trimestre e ano, se não forem fornecidos
    if not descricao:
        raise HTTPException(status_code=400, detail="O parâmetro 'descricao' é obrigatório.")
    
    if not trimestre or not ano:
        trimestre_ano_query = db.execute(text("SELECT * FROM obter_trimestre_anterior()")).fetchone()
        trimestre = trimestre or trimestre_ano_query[0]  # Acessa o primeiro valor da tupla
        ano = ano or trimestre_ano_query[1]  # Acessa o segundo valor da tupla

    query = text("""
        SELECT sum(dc.vl_saldo_final) as total_de_despesa, oi.*
        FROM operadoras_ativas oi 
        JOIN demonstracoes_contabeis dc 
            ON oi.registro_operadora = dc.registro_operadora
        WHERE 
            unaccent(dc.descricao) ILIKE unaccent(:descricao)
            AND dc.vl_saldo_final < 0
            AND dc.trimestre = :trimestre
            AND dc.ano = :ano
        GROUP BY oi.registro_operadora, dc.vl_saldo_final
        ORDER BY dc.vl_saldo_final
        LIMIT 10;
    """)
    result = db.execute(query, {"descricao": f"%{descricao}%", "trimestre": trimestre, "ano": ano}).fetchall()
    return [OperadoraAtivaDespesaDTO.model_validate(row) for row in result]


@router_demonstracoes.get("/maiores_despesas_ano", response_model=List[OperadoraAtivaDespesaDTO])
def maiores_despesas_ano(
    descricao: Optional[str] = None,
    ano: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Retorna as 10 operadoras com maiores despesas no ano especificado.
    Se o ano não for fornecido, usa o ano anterior.
    """
    # Define o valor padrão para o ano, se não for fornecido
    if not descricao:
        raise HTTPException(status_code=400, detail="O parâmetro 'descricao' é obrigatório.")
    
    if not ano:
        ano = db.execute(text("SELECT obter_ano_anterior()")).scalar()

    query = text("""
        SELECT sum(dc.vl_saldo_final) as total_de_despesa, oi.*
        FROM operadoras_ativas oi 
        JOIN demonstracoes_contabeis dc 
            ON oi.registro_operadora = dc.registro_operadora
        WHERE 
            unaccent(dc.descricao) ILIKE unaccent(:descricao)
            AND dc.vl_saldo_final < 0
            AND dc.ano = :ano
        GROUP BY oi.registro_operadora, dc.vl_saldo_final
        ORDER BY dc.vl_saldo_final
        LIMIT 10;
    """)
    result = db.execute(query, {"descricao": f"%{descricao}%", "ano": ano}).fetchall()
    return [OperadoraAtivaDespesaDTO.model_validate(row) for row in result]




@router_operadoras.get("/{registro_operadora}", response_model=OperadoraAtivaDTO)
def read_operadora(registro_operadora: str, db: Session = Depends(get_db)):
    operadora = db.query(OperadoraAtiva).options(joinedload(OperadoraAtiva.demonstracoes_contabeis)).filter(
        OperadoraAtiva.registro_operadora == registro_operadora
    ).first()
    
    if operadora is None:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")
    
    # Remove 'demonstracoes_contabeis' de __dict__ antes de passar para o DTO
    operadora_dict = {k: v for k, v in operadora.__dict__.items() if k != "demonstracoes_contabeis"}
    
    return OperadoraAtivaDTO(
        **operadora_dict,
        demonstracoes_contabeis=[demo.id for demo in operadora.demonstracoes_contabeis]
    )



@router_demonstracoes.get("/{id}", response_model=DemonstracaoContabilDTO)
def read_demonstracao(id: int, db: Session = Depends(get_db)):
    demonstracao = db.query(DemonstracaoContabil).options(joinedload(DemonstracaoContabil.operadora)).filter(
        DemonstracaoContabil.id == id
    ).first()
    
    if demonstracao is None:
        raise HTTPException(status_code=404, detail="Demonstração não encontrada")
    
    return DemonstracaoContabilDTO.model_validate(demonstracao)