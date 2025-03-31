-- Habilita extensões necessárias
CREATE EXTENSION IF NOT EXISTS pg_bulkload;
CREATE EXTENSION IF NOT EXISTS http;

SET datestyle = 'ISO, YMD';

CREATE TABLE IF NOT EXISTS operadoras_ativas (
    registro_operadora VARCHAR(6) NOT NULL PRIMARY KEY,
    cnpj VARCHAR(14) NOT NULL UNIQUE, -- CNPJ da operadora
    razao_social VARCHAR(140), -- Razão social da operadora
    nome_fantasia VARCHAR(140), -- Nome fantasia da operadora
    modalidade VARCHAR(40), -- Modalidade da operadora
    logradouro VARCHAR(40), -- Endereço da Sede da Operadora
    numero VARCHAR(20), -- Número do Endereço da Sede da Operadora
    complemento VARCHAR(40), -- Complemento do Endereço da Sede da Operadora
    bairro VARCHAR(30), -- Bairro do Endereço da Sede da Operadora
    cidade VARCHAR(30), -- Cidade do Endereço da Sede da Operadora
    uf CHAR(2), -- Estado do Endereço da Sede da Operadora
    cep VARCHAR(8), -- CEP do Endereço da Sede da Operadora
    ddd VARCHAR(4), -- Código de DDD da Operadora
    telefone VARCHAR(20), -- Número de Telefone da Operadora
    fax VARCHAR(20), -- Número de Fax da Operadora
    endereco_eletronico VARCHAR(255), -- e-mail da Operadora
    representante VARCHAR(50), -- Representante Legal da Operadora
    cargo_representante VARCHAR(40), -- Cargo do Representante Legal da Operadora
    regiao_de_comercializacao INT, -- Área de comercialização da operadora
    data_registro_ans DATE -- Data do Registro da Operadora na ANS (formato AAAA-MM-DD)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_operadoras_cnpj ON public.operadoras_ativas (cnpj);
CREATE INDEX IF NOT EXISTS idx_operadoras_uf ON public.operadoras_ativas (uf);


CREATE TABLE IF NOT EXISTS demonstracoes_contabeis (
    id BIGSERIAL PRIMARY KEY, -- ID auto-incrementável
    data_demonstracao DATE NOT NULL, -- Data da demonstração
    trimestre INT NOT NULL, -- Trimestre da demonstração
    ano INT NOT NULL, -- Ano da demonstração
    registro_operadora VARCHAR NOT NULL, -- Registro da operadora (chave estrangeira)
    cd_conta_contabil INT NOT NULL, -- Código da conta contábil
    descricao VARCHAR(255), -- Descrição da conta contábil
    vl_saldo_inicial NUMERIC(15, 2), -- Valor do saldo inicial (em reais)
    vl_saldo_final NUMERIC(15, 2), -- Valor do saldo final (em reais)
    CONSTRAINT fk_operadora FOREIGN KEY (registro_operadora) REFERENCES operadoras_ativas (registro_operadora) ON DELETE CASCADE ON UPDATE CASCADE
);

