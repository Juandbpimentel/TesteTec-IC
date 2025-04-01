from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class DemonstracaoContabilBase(BaseModel):
    data_demonstracao: date
    trimestre: int
    ano: int
    registro_operadora: str
    cd_conta_contabil: int
    descricao: Optional[str]
    vl_saldo_inicial: Optional[float]
    vl_saldo_final: Optional[float]

class DemonstracaoContabilCreate(DemonstracaoContabilBase):
    pass

class DemonstracaoContabilDTO(DemonstracaoContabilBase):
    id: int
    operadora: "OperadoraAtivaListagemDTO"
    
    class Config:
        from_attributes = True

class DemonstracaoContabilListagemDTO(DemonstracaoContabilBase):
    id: int
    class Config:
        from_attributes = True

class OperadoraAtivaBase(BaseModel):
    registro_operadora: str
    cnpj: str
    razao_social: Optional[str]
    nome_fantasia: Optional[str]
    modalidade: Optional[str]
    logradouro: Optional[str]
    numero: Optional[str]
    complemento: Optional[str]
    bairro: Optional[str]
    cidade: Optional[str]
    uf: Optional[str]
    cep: Optional[str]
    ddd: Optional[str]
    telefone: Optional[str]
    fax: Optional[str]
    endereco_eletronico: Optional[str]
    representante: Optional[str]
    cargo_representante: Optional[str]
    regiao_de_comercializacao: Optional[int]
    data_registro_ans: Optional[date]

class OperadoraAtivaCreate(OperadoraAtivaBase):
    pass

class OperadoraAtivaListagemDTO(OperadoraAtivaBase):
    class Config:
        from_attributes = True

class OperadoraAtivaDespesaDTO(OperadoraAtivaBase):
    total_de_despesa: float
    class Config:
        from_attributes = True

class OperadoraAtivaDTO(OperadoraAtivaBase):
    demonstracoes_contabeis: List[int] = []

    class Config:
        from_attributes = True