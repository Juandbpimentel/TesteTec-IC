
            CREATE OR REPLACE FUNCTION load_from_gcs_operadoras_ativas(url TEXT) RETURNS VOID AS $$
            BEGIN
                EXECUTE format(
                    $CMD$
                    COPY operadoras_ativas (registro_operadora, cnpj, razao_social, nome_fantasia, modalidade, logradouro, numero, complemento, bairro, cidade, uf, cep, ddd, telefone, fax, endereco_eletronico, representante, cargo_representante, regiao_de_comercializacao, data_registro_ans) FROM PROGRAM 'curl -sL %s | lz4 -d'
                    WITH (
                        FORMAT CSV,
                        DELIMITER ';',
                        HEADER,
                        NULL ''
                        ,FORCE_NULL (regiao_de_comercializacao)
                    )
                    $CMD$,
                    url
                );
            END;
            $$ LANGUAGE plpgsql;

SELECT load_from_gcs_operadoras_ativas('https://storage.googleapis.com/testetecnico-ic.firebasestorage.app/operadoras_ativas/part-0000.csv.lz4');