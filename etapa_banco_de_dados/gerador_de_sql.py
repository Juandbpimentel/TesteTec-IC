import polars as pl
import os
import argparse
import time
import concurrent.futures
import contextlib
import lz4.frame
from firebase_admin import credentials, initialize_app, storage, delete_app


# Funções de carregamento e salvamento de dados
def carrega_csv(caminho_arquivo: str) -> pl.DataFrame:
    try:
        return pl.read_csv(caminho_arquivo, separator=";", encoding="utf-8")
    except Exception as e:
        print(f"Erro ao carregar o arquivo {caminho_arquivo}: {e}")
        return None


def salva_csv(dataframe: pl.DataFrame, caminho_arquivo: str) -> bool:
    try:
        dataframe.write_csv(caminho_arquivo, separator=";")
        return True
    except Exception as e:
        print(f"Erro ao salvar o arquivo {caminho_arquivo}: {e}")
        return False


def copiar_arquivo(origem: str, destino: str):
    try:
        # Lê o conteúdo do arquivo de origem
        with open(origem, "r", encoding="utf-8") as arquivo_origem:
            conteudo = arquivo_origem.read()

        # Escreve o conteúdo no arquivo de destino
        os.makedirs(
            os.path.dirname(destino), exist_ok=True
        )  # Garante que o diretório existe
        with open(destino, "w", encoding="utf-8") as arquivo_destino:
            arquivo_destino.write(conteudo)
    except Exception as e:
        print(f"Erro ao copiar o arquivo '{origem}' para '{destino}': {e}")


# Funções auxiliares e de tratamento de dados
def para_lower_case(column_name: str) -> str:
    return column_name.lower()


def corrigir_valores_numericos(
    df: pl.DataFrame, colunas_numericas: list[str]
) -> pl.DataFrame:
    for coluna in colunas_numericas:
        if coluna in df.columns:
            df = df.with_columns(pl.col(coluna).str.replace(",", ".").cast(pl.Float64))
    return df


def converter_datas(df: pl.DataFrame, coluna: str) -> pl.DataFrame:
    if coluna in df.columns:
        df = df.with_columns(
            pl.when(pl.col(coluna).str.contains(r"^\d{2}/\d{2}/\d{4}$", strict=False))
            .then(pl.col(coluna).str.replace(r"(\d{2})/(\d{2})/(\d{4})", r"$3-$2-$1"))
            .otherwise(pl.col(coluna))
            .alias(coluna)
        )
    return df


def tratar_descricoes_de_demonstracoes(df: pl.DataFrame):
    if "descricao" in df.columns:
        df = df.with_columns(
            pl.col("descricao")
            .str.replace_all(r"\t", " ")
            .str.replace_all(r"\s*\(\s*-\s*\)\s*", "")
            .str.replace_all(r"\s*/\s*", "/")
            .str.replace_all(r"(\S)\s*-\s*(\S)", r"$1 - $2")
            .str.replace_all(r"\s+", " ")
            .str.strip_chars()
            .str.to_uppercase()
            .str.replace_all("MÉDICOR -", "MÉDICO -")
            .str.replace_all(r"MÉDICO -\s*$", "MÉDICO")
            .str.replace_all(r"MEDICO", r"MÉDICO")
        )

    return df


def tratar_os_dados_operadoras_ativas(df: pl.DataFrame) -> pl.DataFrame:
    return df.rename({col: para_lower_case(col) for col in df.columns}).rename(
        {"registro_ans": "registro_operadora"}
    )


def trata_os_dados_demonstracoes_contabeis(dados: list[dict]) -> pl.DataFrame:
    dataframes = []
    for dado in dados:
        df: pl.DataFrame = dado["dataframe"].rename(
            {col: para_lower_case(col) for col in dado["dataframe"].columns}
        )

        if "data" in df.columns:
            df = converter_datas(df, "data")
            df = df.with_columns(
                pl.col("data")
                .cast(pl.Utf8)
                .str.strip_chars()
                .alias("data_demonstracao")
            )

            df = df.drop("data")

        df = df.with_columns(
            [
                pl.lit(dado["trimestre"]).alias("trimestre"),
                pl.lit(dado["ano"]).alias("ano"),
            ]
        )

        df = df.rename({"reg_ans": "registro_operadora"})

        colunas_numericas = [
            "vl_saldo_inicial",
            "vl_saldo_final",
        ]
        df = corrigir_valores_numericos(df, colunas_numericas)
        df = tratar_descricoes_de_demonstracoes(df)

        dataframes.append(df)

    return pl.concat(dataframes)


# Funções de carregamento de dados
def carregar_dados_operadoras_ativas(caminho_do_csv: str) -> pl.DataFrame:
    try:
        dataframe = carrega_csv(caminho_do_csv)
        return dataframe if dataframe is not None else pl.DataFrame()
    except Exception as e:
        print(f"Erro ao processar o arquivo {caminho_do_csv}: {e}")
        return pl.DataFrame()


def carregar_dados_demonstracoes_contabeis(caminho_base: str) -> list[dict]:
    dados = []
    for ano in os.listdir(caminho_base):
        caminho_ano = os.path.join(caminho_base, ano)
        if os.path.isdir(caminho_ano):
            for arquivo in os.listdir(caminho_ano):
                if arquivo.endswith(".csv"):
                    try:
                        caminho_arquivo = os.path.join(caminho_ano, arquivo)
                        df = carrega_csv(caminho_arquivo)
                        if df is not None:
                            dados.append(
                                {"dataframe": df, "ano": ano, "trimestre": arquivo[0]}
                            )
                    except Exception as e:
                        print(f"Erro ao processar {arquivo}: {e}")

    return dados


# Função para verificar e tratar as demonstrações contábeis com operadoras inativas
def verifica_e_trata_demonstracoes_com_operadoras_inativas(
    df_demonstracoes: pl.DataFrame, df_operadoras: pl.DataFrame
) -> pl.DataFrame:
    if "registro_operadora" not in df_demonstracoes.columns:
        print("Coluna 'registro_operadora' não encontrada nas demonstrações contábeis.")
        return df_demonstracoes

    demonstracoes_sem_operadoras = df_demonstracoes.filter(
        ~pl.col("registro_operadora").is_in(df_operadoras["registro_operadora"])
    )
    if demonstracoes_sem_operadoras.is_empty():
        return df_demonstracoes
    return df_demonstracoes.filter(
        ~pl.col("registro_operadora").is_in(
            demonstracoes_sem_operadoras["registro_operadora"]
        )
    )


# Funções de upload e geração de comandos SQL Bulk Load
def gerar_csv_otimizado(df: pl.DataFrame, caminho_saida: str, compressao: bool = True):
    try:
        if compressao:
            caminho_temp = f"{caminho_saida}.tmp"
            df.write_csv(caminho_temp, separator=";")
            with (
                open(caminho_temp, "rb") as f_in,
                lz4.frame.open(caminho_saida, "wb") as f_out,
            ):
                f_out.write(f_in.read())
            os.remove(caminho_temp)
        else:
            df.write_csv(caminho_saida, separator=";")
        return True
    except Exception as e:
        print(f"Erro ao gerar CSV: {e}")
        return False


def upload_para_storage(caminho_local: str, caminho_remoto: str) -> str:
    try:
        bucket = storage.bucket()
        blob = bucket.blob(caminho_remoto)
        blob.upload_from_filename(caminho_local)
        blob.make_public()
        return blob.public_url
    except Exception as e:
        print(f"Erro ao fazer upload para o Firebase Storage: {e}")
        return None


def gerar_comandos_upload(caminho_dados: str, tabela: str) -> str:
    return f"SELECT load_from_gcs_{tabela}('{caminho_dados}');"


# Funções de geração de comandos SQL para inserção
def gerar_comandos_query_simples(linhas: list[dict], tabela: str) -> str:
    comandos = [
        f"INSERT INTO {tabela} (registro_operadora, cnpj, razao_social, nome_fantasia, modalidade, logradouro, numero, complemento, bairro, cidade, uf, cep, ddd, telefone, fax, endereco_eletronico, representante, cargo_representante, regiao_de_comercializacao, data_registro_ans) VALUES\n"
        if tabela == "operadoras_ativas"
        else f"INSERT INTO {tabela} (registro_operadora,cd_conta_contabil,descricao,vl_saldo_inicial,vl_saldo_final,data_demonstracao,trimestre,ano) VALUES\n"
    ]
    for linha in linhas:
        valores = ", ".join(
            [
                f"'{str(v).replace("'", "''")}'" if v is not None else "NULL"
                for v in linha.values()
            ]
        )
        comandos.append(f"({valores}),\n")
    comandos[-1] = comandos[-1].rstrip(",\n") + ";\n"
    return "".join(comandos)


def processar_chunk_query_simples(
    df: pl.DataFrame,
    caminho_base: str,
    idx: int,
    tabela: str,
    ordem_de_insercao: int = 1,
):
    print(f"Processando chunk {idx}...")
    linhas = df.to_dicts()
    comandos_sql = gerar_comandos_query_simples(linhas, tabela)

    # Corrige o nome do arquivo
    caminho_arquivo_sql = os.path.join(
        caminho_base, f"{ordem_de_insercao:02d}-{idx:04d}-{tabela}.sql"
    )
    try:
        with open(caminho_arquivo_sql, "w", encoding="utf-8") as f:
            f.write(comandos_sql)
        print(f"Chunk {idx} processado com sucesso.")
    except Exception as e:
        print(f"Erro ao salvar o arquivo SQL para o chunk {idx}: {e}")


def processar_chunk_bulk_load(
    df: pl.DataFrame,
    caminho_base: str,
    idx: int,
    tabela: str,
    comandos: list,
):
    print(f"Processando chunk {idx}...")
    caminho_chunk_local = os.path.join(caminho_base, f"part-{idx:04d}.csv.lz4")
    gerar_csv_otimizado(df, caminho_chunk_local)

    caminho_chunk_remoto = f"{tabela}/part-{idx:04d}.csv.lz4"
    if url_remota := upload_para_storage(caminho_chunk_local, caminho_chunk_remoto):
        comandos.append(gerar_comandos_upload(url_remota, tabela))

    os.remove(caminho_chunk_local)
    print(f"Chunk {idx} processado com sucesso.")


def processar_chunk_paralelo(
    df: pl.DataFrame,
    caminho_base: str,
    idx: int,
    tabela: str,
    comandos: list,
    modo: str,
    ordem_de_insercao: int = 1,
):
    try:
        if modo == "bulk_load":
            processar_chunk_bulk_load(df, caminho_base, idx, tabela, comandos)
        elif modo == "sem_bulk_load":
            processar_chunk_query_simples(
                df, caminho_base, idx, tabela, ordem_de_insercao
            )
        else:
            raise ValueError(f"Modo desconhecido: {modo}")
    except Exception as e:
        print(f"Erro no chunk {idx}: {e}")


def gerar_arquivos_bulk_load(
    df: pl.DataFrame,
    caminho_saida: str,
    tabela: str,
    tamanho_chunk: int,
    num_threads: int,
    colunas_que_podem_ser_nulas: list[str] = None,
    nome_arquivo: str = None,
):
    start_time = time.time()
    os.makedirs(caminho_saida, exist_ok=True)

    force_null_clause = ""
    if colunas_que_podem_ser_nulas:
        force_null_clause = f",FORCE_NULL ({', '.join(colunas_que_podem_ser_nulas)})"

    colunas_csv = df.columns
    colunas_clause = f"({', '.join(colunas_csv)})" if colunas_csv else ""

    comandos = [
        f"""
        CREATE OR REPLACE FUNCTION load_from_gcs_{tabela}(url TEXT) RETURNS VOID AS $$
        BEGIN
            EXECUTE format(
                $CMD$
                COPY {tabela} {colunas_clause} FROM PROGRAM 'curl -sL %s | lz4 -d'
                WITH (
                    FORMAT CSV,
                    DELIMITER ';',
                    HEADER,
                    NULL ''
                    {force_null_clause}
                )
                $CMD$,
                url
            );
        END;
        $$ LANGUAGE plpgsql;\n\n"""
    ]
    print(f"Dividindo o DataFrame em chunks de {tamanho_chunk} linhas...")
    chunks = [df[i : i + tamanho_chunk] for i in range(0, df.height, tamanho_chunk)]
    print(f"Total de chunks: {len(chunks)}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(
                processar_chunk_bulk_load,
                chunk,
                caminho_saida,
                idx,
                tabela,
                comandos,
            )
            for idx, chunk in enumerate(chunks)
        ]
        concurrent.futures.wait(futures)

    print(f"Todos os chunks processados em {time.time() - start_time:.2f} segundos.")

    caminho_comandos = os.path.join(caminho_saida, f"{nome_arquivo or f'{tabela}.sql'}")
    with open(caminho_comandos, "w", encoding="utf-8") as f:
        f.writelines(comandos)


def gerar_arquivos_query_simples(
    df: pl.DataFrame,
    caminho_saida: str,
    tabela: str,
    tamanho_chunk: int,
    num_threads: int,
    ordem_de_insercao: int = 1,
):
    start_time = time.time()
    os.makedirs(caminho_saida, exist_ok=True)

    print(f"Dividindo o DataFrame em chunks de {tamanho_chunk} linhas...")
    chunks = [df[i : i + tamanho_chunk] for i in range(0, df.height, tamanho_chunk)]
    print(f"Total de chunks: {len(chunks)}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(
                processar_chunk_query_simples,
                chunk,
                caminho_saida,
                idx,
                tabela,
                ordem_de_insercao,
            )
            for idx, chunk in enumerate(chunks)
        ]
        concurrent.futures.wait(futures)

    print(f"Todos os chunks processados em {time.time() - start_time:.2f} segundos.")


def gerar_arquivos_de_insercao(
    df: pl.DataFrame,
    caminho_saida: str,
    tabela: str,
    tamanho_chunk: int = 50_000,
    num_threads: int = 8,
    modo: str = "bulk_load",
    colunas_que_podem_ser_nulas: list[str] = None,
    nome_arquivo: str = None,
    ordem_de_insercao: int = 1,
):
    if modo == "bulk_load":
        gerar_arquivos_bulk_load(
            df,
            caminho_saida,
            tabela,
            tamanho_chunk,
            num_threads,
            colunas_que_podem_ser_nulas,
            nome_arquivo,
        )
    elif modo == "sem_bulk_load":
        gerar_arquivos_query_simples(
            df, caminho_saida, tabela, tamanho_chunk, num_threads, ordem_de_insercao
        )
    else:
        raise ValueError(f"Modo desconhecido: {modo}")


def limpar_diretorio_saida(caminho_saida_base: str):
    try:
        if os.path.exists(caminho_saida_base):
            for arquivo in os.listdir(caminho_saida_base):
                caminho_arquivo = os.path.join(caminho_saida_base, arquivo)
                if os.path.isfile(caminho_arquivo):
                    os.remove(caminho_arquivo)
                elif os.path.isdir(caminho_arquivo):
                    # Remove subdiretórios recursivamente, se necessário
                    import shutil

                    shutil.rmtree(caminho_arquivo)
        else:
            print(f"O diretório {caminho_saida_base} não existe.")
    except Exception as e:
        print(f"Erro ao limpar o diretório {caminho_saida_base}: {e}")


def trata_argumentos_do_script(modo_de_geracao: str, modo_de_utilizacao: str) -> dict:
    if modo_de_utilizacao == "docker":
        caminho_saida_base = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "database/scripts"
        )
        limpar_diretorio_saida(caminho_saida_base)

        caminho_saida_tabelas = os.path.join(caminho_saida_base, "01-cria_tabelas.sql")
        caminho_saida_operadoras = caminho_saida_base
        caminho_saida_demonstracoes = caminho_saida_base
        if modo_de_geracao == "bulk_load":
            dado_de_arquivo_operadoras = "02-operadoras_ativas.sql"
            dado_de_arquivo_demonstracoes = "03-demonstracoes_contabeis.sql"
        else:
            dado_de_arquivo_operadoras = 2
            dado_de_arquivo_demonstracoes = 3

    else:
        caminho_saida_base = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "arquivos_sql_gerados"
        )
        limpar_diretorio_saida(caminho_saida_base)
        caminho_saida_tabelas = os.path.join(caminho_saida_base, "tabelas.sql")

        if modo_de_geracao == "bulk_load":
            caminho_saida_operadoras = os.path.join(
                caminho_saida_base, "operadoras_bulk_load"
            )
            dado_de_arquivo_operadoras = "operadoras_ativas.sql"

            caminho_saida_demonstracoes = os.path.join(
                caminho_saida_base, "demonstracoes_bulk_load"
            )
            dado_de_arquivo_demonstracoes = "demonstracoes_contabeis.sql"
        else:
            caminho_saida_operadoras = os.path.join(
                caminho_saida_base, "operadoras_sem_bulk_load"
            )
            dado_de_arquivo_operadoras = 2

            caminho_saida_demonstracoes = os.path.join(
                caminho_saida_base, "demonstracoes_sem_bulk_load"
            )
            dado_de_arquivo_demonstracoes = 3

    return {
        "modo_de_geracao": modo_de_geracao,
        "modo_de_utilizacao": modo_de_utilizacao,
        "caminho_saida_tabelas": caminho_saida_tabelas,
        "caminho_saida_operadoras": caminho_saida_operadoras,
        "caminho_saida_demonstracoes": caminho_saida_demonstracoes,
        "dado_de_arquivo_operadoras": dado_de_arquivo_operadoras,
        "dado_de_arquivo_demonstracoes": dado_de_arquivo_demonstracoes,
    }


def __main__():
    # Configura o parser de argumentos
    parser = argparse.ArgumentParser(description="Script python para gerar SQL.")
    parser.add_argument(
        "-mg",
        "--modo_de_geracao",
        type=str,
        default="sem_bulk_load",
        help="Modo de geração: 'bulk_load' ou 'sem_bulk_load'.",
    )

    parser.add_argument(
        "-mu",
        "--modo_de_utilizacao",
        type=str,
        default="vizualizacao",
        help="Tipos de utilização: 'vizualiacao' ou 'docker'\n Define se os diretórios para salvar o arquivo serão usados de forma para vizualização ou para geração de SQL para carregamento no Docker.\n",
    )

    args = parser.parse_args()

    modo_de_geracao = args.modo_de_geracao
    modo_de_utilizacao = args.modo_de_utilizacao

    configuracoes = trata_argumentos_do_script(modo_de_geracao, modo_de_utilizacao)

    start_time = time.time()
    diretorio_base = os.path.dirname(os.path.abspath(__file__))

    # Defina o caminho para os arquivos de entrada
    caminho_operadoras = os.path.join(
        diretorio_base, "arquivos/dados_cadastrais/Relatorio_cadop.csv"
    )
    caminho_demonstracoes = os.path.join(
        diretorio_base, "arquivos/demonstracoes_contabeis"
    )

    # Carregar os dados
    print("Carregando dados das operadoras...")
    df_operadoras = carregar_dados_operadoras_ativas(caminho_operadoras)

    if df_operadoras.is_empty():
        print("Nenhuma operadora ativa encontrada.")
        return

    print("Carregando dados das demonstrações contábeis...")
    dfs_demonstracoes = carregar_dados_demonstracoes_contabeis(caminho_demonstracoes)

    if not dfs_demonstracoes:
        print("Nenhuma demonstração contábil encontrada.")
        return

    print("Tratando os dados...")
    # Tratar os dados

    df_operadoras_final = tratar_os_dados_operadoras_ativas(df_operadoras)
    if df_operadoras_final.is_empty():
        print("Nenhuma operadora ativa encontrada após o tratamento.")
        return

    df_demonstracoes_final = trata_os_dados_demonstracoes_contabeis(dfs_demonstracoes)
    if df_demonstracoes_final.is_empty():
        print("Nenhuma demonstração contábil encontrada após o tratamento.")
        return

    # Remove entradas de operadoras inativas das demonstrações contábeis para evitar erros de integridade referencial

    df_demonstracoes_final = verifica_e_trata_demonstracoes_com_operadoras_inativas(
        df_demonstracoes_final, df_operadoras_final
    )

    # Salva o resultado tratado em CSVs para verificação ou utilização manual caso necessário
    salva_csv(
        df_operadoras_final,
        os.path.join(
            diretorio_base,
            "operadoras_ativas_tratado.csv",
        ),
    )

    salva_csv(
        df_demonstracoes_final,
        os.path.join(
            diretorio_base,
            "demonstracoes_contabeis_tratado.csv",
        ),
    )

    copiar_arquivo(
        "tabelas.sql",
        configuracoes["caminho_saida_tabelas"],
    )

    print("Dados tratados com sucesso.")
    print("Gerando arquivos de inserção...\n\n")
    # Escolha do modo de geração
    if modo_de_geracao == "bulk_load":
        try:
            with contextlib.suppress(ValueError):
                delete_app(initialize_app())
            cred = credentials.Certificate(
                "testetecnico-ic-firebase-adminsdk-fbsvc-bfa601be6c.json"
            )
            initialize_app(
                cred, {"storageBucket": "testetecnico-ic.firebasestorage.app"}
            )
            print("Firebase Storage conectado com sucesso.")
        except Exception as e:
            print(f"Erro ao conectar ao Firebase Storage: {e}")
            return

        print("Modo de geração: bulk_load\n\n")
        print("Gerando arquivos de upload para operadoras...\n\n")

        gerar_arquivos_de_insercao(
            df_operadoras_final,
            configuracoes["caminho_saida_operadoras"],
            "operadoras_ativas",
            tamanho_chunk=250_000,
            num_threads=os.cpu_count() * 2,
            modo="bulk_load",
            colunas_que_podem_ser_nulas=["regiao_de_comercializacao"],
            nome_arquivo=configuracoes["dado_de_arquivo_operadoras"],
        )

        print("Gerando arquivos de upload para demonstrações contábeis...\n\n")
        gerar_arquivos_de_insercao(
            df_demonstracoes_final,
            configuracoes["caminho_saida_demonstracoes"],
            "demonstracoes_contabeis",
            tamanho_chunk=250_000,
            num_threads=os.cpu_count() * 2,
            modo="bulk_load",
            nome_arquivo=configuracoes["dado_de_arquivo_demonstracoes"],
        )
    else:
        print("Modo de geração: sem_bulk_load\n\n")
        print("Gerando arquivos de inserção para operadoras...\n\n")
        gerar_arquivos_de_insercao(
            df_operadoras_final,
            configuracoes["caminho_saida_operadoras"],
            "operadoras_ativas",
            tamanho_chunk=50_000,
            num_threads=os.cpu_count() * 2,
            modo="sem_bulk_load",
            ordem_de_insercao=configuracoes["dado_de_arquivo_operadoras"],
        )

        print("Gerando arquivos de inserção para demonstrações contábeis...\n\n")
        gerar_arquivos_de_insercao(
            df_demonstracoes_final,
            configuracoes["caminho_saida_demonstracoes"],
            "demonstracoes_contabeis",
            tamanho_chunk=50_000,
            num_threads=os.cpu_count() * 2,
            modo="sem_bulk_load",
            ordem_de_insercao=configuracoes["dado_de_arquivo_demonstracoes"],
        )

    print("Processo concluído com sucesso!")
    print(f"Tempo total: {time.time() - start_time:.2f} segundos.")


if __name__ == "__main__":
    __main__()
