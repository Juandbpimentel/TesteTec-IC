from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func, text
from models import OperadoraAtiva
from schemas import OperadoraAtivaListagemDTO, OperadoraAtivaDespesaDTO, OperadoraAtivaDTO
from typing import List, Optional


class OperadorasResponse(BaseModel):
    operadoras: List[OperadoraAtivaListagemDTO]
    next_cursor: Optional[str]
    total_elementos: int

def get_operadoras(
    session: Session,
    limit: int,
    registro_operadora: Optional[str],
    cnpj: Optional[str],
    razao_social: Optional[str],
    nome_fantasia: Optional[str],
    modalidade: Optional[str],
    regiao_de_comercializacao: Optional[int],
    start_cursor: Optional[str],
    cidade: Optional[str],
    uf: Optional[str]
) -> OperadorasResponse:
    base_query = session.query(OperadoraAtiva)

    if registro_operadora:
        base_query = base_query.filter(func.unaccent(OperadoraAtiva.registro_operadora).ilike(func.unaccent(f"%{registro_operadora}%")))
    if cnpj:
        base_query = base_query.filter(func.unaccent(OperadoraAtiva.cnpj).ilike(func.unaccent(f"%{cnpj}%")))
    if razao_social:
        base_query = base_query.filter(func.unaccent(OperadoraAtiva.razao_social).ilike(func.unaccent(f"%{razao_social}%")))
    if nome_fantasia:
        base_query = base_query.filter(func.unaccent(OperadoraAtiva.nome_fantasia).ilike(func.unaccent(f"%{nome_fantasia}%")))
    if modalidade:
        base_query = base_query.filter(func.unaccent(OperadoraAtiva.modalidade).ilike(func.unaccent(f"%{modalidade}%")))
    if regiao_de_comercializacao:
        base_query = base_query.filter(OperadoraAtiva.regiao_de_comercializacao == regiao_de_comercializacao)
    if cidade:
        base_query = base_query.filter(func.unaccent(OperadoraAtiva.cidade).ilike(func.unaccent(f"%{cidade}%")))
    if uf:
        base_query = base_query.filter(func.unaccent(OperadoraAtiva.uf).ilike(func.unaccent(f"%{uf}%")))
    
    total_elementos = base_query.count()

    if start_cursor:
        base_query = base_query.filter(OperadoraAtiva.registro_operadora > start_cursor)

    query = base_query.order_by(OperadoraAtiva.registro_operadora)
    if limit > 0:
        query = query.limit(limit)

    operadoras = query.all()

    next_cursor = operadoras[-1].registro_operadora if len(operadoras) == limit else None

    return OperadorasResponse(
        operadoras=[OperadoraAtivaListagemDTO.model_validate(op) for op in operadoras],
        next_cursor=next_cursor,
        total_elementos=total_elementos
    )


def get_operadora_by_registro(session: Session, registro_operadora: str):
    operadora = session.query(OperadoraAtiva).options(
        joinedload(OperadoraAtiva.demonstracoes_contabeis)
    ).filter(OperadoraAtiva.registro_operadora == registro_operadora).first()

    if operadora:
        demonstracoes_ids = [demonstracao.id for demonstracao in operadora.demonstracoes_contabeis]
        
        operadora_data = operadora.__dict__.copy()
        operadora_data["demonstracoes_contabeis"] = demonstracoes_ids
        
        return OperadoraAtivaDTO(**operadora_data)

    return None


def get_maiores_despesas_trimestre(
    session: Session,
    descricao: str,
    trimestre: Optional[int],
    ano: Optional[int],
) -> List[OperadoraAtivaDespesaDTO]:
    if not trimestre or not ano:
        trimestre_ano_query = session.execute(text("SELECT * FROM obter_trimestre_anterior()")).fetchone()
        trimestre = trimestre or trimestre_ano_query[0]
        ano = ano or trimestre_ano_query[1]

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
        GROUP BY oi.registro_operadora
        ORDER BY total_de_despesa ASC
        LIMIT 10;
    """)
    result = session.execute(query, {"descricao": f"%{descricao}%", "trimestre": trimestre, "ano": ano}).fetchall()

    return [OperadoraAtivaDespesaDTO.model_validate(row) for row in result]


def get_maiores_despesas_ano(
    session: Session,
    descricao: str,
    ano: Optional[int],
) -> List[OperadoraAtivaDespesaDTO]:
    if not ano:
        ano = session.execute(text("SELECT obter_ano_anterior()")).scalar()

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
    result = session.execute(query, {"descricao": f"%{descricao}%", "ano": ano}).fetchall()
    return [OperadoraAtivaDespesaDTO.model_validate(row) for row in result]


def get_ufs(session: Session) -> List[str]:
    query = session.query(OperadoraAtiva.uf).distinct().order_by(OperadoraAtiva.uf)
    return [uf for uf, in query.all()]

def get_modalidades(session: Session) -> List[str]:
    query = session.query(OperadoraAtiva.modalidade).distinct().order_by(OperadoraAtiva.modalidade)
    return [modalidade for modalidade, in query.all()]

def get_regioes_de_comercializacao(session: Session) -> List[int]:
    query = session.query(OperadoraAtiva.regiao_de_comercializacao).distinct().order_by(OperadoraAtiva.regiao_de_comercializacao)
    return [regiao for regiao, in query.all()]