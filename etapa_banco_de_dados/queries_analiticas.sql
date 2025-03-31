CREATE OR REPLACE FUNCTION obter_trimestre_anterior() 
RETURNS TABLE (trimestre INT, ano INT) AS $$
DECLARE
    trimestre_atual INT;
    ano_atual INT;
BEGIN
    -- Obtém o trimestre e o ano atuais
    trimestre_atual := EXTRACT(QUARTER FROM CURRENT_DATE);
    ano_atual := EXTRACT(YEAR FROM CURRENT_DATE);

    -- Retorna o trimestre anterior e o ano correspondente
    RETURN QUERY 
    SELECT 
        CASE 
            WHEN trimestre_atual = 1 THEN 4  -- Se for 1º trimestre, o anterior é o 4º do ano passado
            ELSE trimestre_atual - 1
        END AS trimestre,
        CASE 
            WHEN trimestre_atual = 1 THEN ano_atual - 1  -- Se for 1º trimestre, o ano anterior
            ELSE ano_atual
        END AS ano;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION obter_ano_anterior() 
RETURNS INT AS $$
BEGIN
    RETURN EXTRACT(YEAR FROM CURRENT_DATE) - 1;
END;
$$ LANGUAGE plpgsql;

SELECT sum(dc.vl_saldo_final) as total_de_despesa,oi.*
FROM operadoras_ativas oi 
JOIN demonstracoes_contabeis dc 
    ON oi.registro_operadora = dc.registro_operadora
WHERE 
    unaccent(dc.descricao) ILIKE unaccent('%EVENTOS/SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MÉDICO HOSPITALAR%')
    AND dc.vl_saldo_final < 0
    AND dc.trimestre = (SELECT trimestre FROM obter_trimestre_anterior())
    AND dc.ano = (SELECT ano FROM obter_trimestre_anterior())
GROUP BY oi.registro_operadora, dc.vl_saldo_final
ORDER BY dc.vl_saldo_final
LIMIT 10;

SELECT sum(dc.vl_saldo_final) as total_de_despesa,oi.*
FROM operadoras_ativas oi 
JOIN demonstracoes_contabeis dc 
    ON oi.registro_operadora = dc.registro_operadora
WHERE 
    unaccent(dc.descricao) ILIKE unaccent('%EVENTOS/SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MÉDICO HOSPITALAR%')
    AND dc.vl_saldo_final < 0
    AND dc.ano = (SELECT ano FROM obter_trimestre_anterior())
GROUP BY oi.registro_operadora, dc.vl_saldo_final
ORDER BY dc.vl_saldo_final
LIMIT 10;