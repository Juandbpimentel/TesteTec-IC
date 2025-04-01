from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from database import Base

class OperadoraAtiva(Base):
    __tablename__ = 'operadoras_ativas'

    registro_operadora = Column(String(6), primary_key=True)
    cnpj = Column(String(14), unique=True, nullable=False)
    razao_social = Column(String(140))
    nome_fantasia = Column(String(140))
    modalidade = Column(String(40))
    logradouro = Column(String(40))
    numero = Column(String(20))
    complemento = Column(String(40))
    bairro = Column(String(30))
    cidade = Column(String(30))
    uf = Column(String(2))
    cep = Column(String(8))
    ddd = Column(String(4))
    telefone = Column(String(20))
    fax = Column(String(20))
    endereco_eletronico = Column(String(255))
    representante = Column(String(50))
    cargo_representante = Column(String(40))
    regiao_de_comercializacao = Column(Integer)
    data_registro_ans = Column(Date)

    demonstracoes_contabeis = relationship("DemonstracaoContabil", back_populates="operadora", cascade="all, delete-orphan", lazy="noload")


class DemonstracaoContabil(Base):
    __tablename__ = 'demonstracoes_contabeis'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    data_demonstracao = Column(Date, nullable=False)
    trimestre = Column(Integer, nullable=False)
    ano = Column(Integer, nullable=False)
    registro_operadora = Column(String(6), ForeignKey('operadoras_ativas.registro_operadora', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    cd_conta_contabil = Column(Integer, nullable=False)
    descricao = Column(String(255))
    vl_saldo_inicial = Column(Numeric(15, 2))
    vl_saldo_final = Column(Numeric(15, 2))

    operadora = relationship("OperadoraAtiva", back_populates="demonstracoes_contabeis", lazy="noload")