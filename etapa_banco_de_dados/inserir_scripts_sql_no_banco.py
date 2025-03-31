import os
import argparse
from concurrent.futures import ThreadPoolExecutor
import psycopg2  # Biblioteca para conexão com PostgreSQL


def executar_script_sql(caminho_arquivo, conexao):
    try:
        cursor = conexao.cursor()
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            sql_script = f.read()
            print(f"Executando script: {os.path.basename(caminho_arquivo)}")
            cursor.execute(sql_script)
        conexao.commit()
        print(f"Script {os.path.basename(caminho_arquivo)} executado com sucesso.")
    except Exception as e:
        print(f"Erro ao executar o script {os.path.basename(caminho_arquivo)}: {e}")
        conexao.rollback()
    finally:
        cursor.close()


def executar_scripts_sql_paralelo(diretorio_sql, conexao_params, max_workers=4):
    if not os.path.exists(diretorio_sql):
        print(f"Diretório {diretorio_sql} não encontrado. Pulando...")
        return

    arquivos_sql = [
        os.path.join(diretorio_sql, arquivo)
        for arquivo in os.listdir(diretorio_sql)
        if arquivo.endswith(".sql") and not arquivo.startswith("queriesRelatorio")
    ]

    if not arquivos_sql:
        print(f"Nenhum arquivo SQL encontrado no diretório {diretorio_sql}.")
        return

    falhas = []

    def worker(caminho_arquivo):
        conexao = psycopg2.connect(**conexao_params)
        try:
            executar_script_sql(caminho_arquivo, conexao)
        except Exception as e:
            falhas.append(caminho_arquivo)
            print(f"Erro ao executar o script {caminho_arquivo}: {e}")
        finally:
            conexao.close()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(worker, arquivos_sql)

    if falhas:
        print("Os seguintes scripts falharam:")
        for falha in falhas:
            print(f"- {falha}")


def trata_argumentos_do_script(modo_de_geracao: str, modo_de_utilizacao: str) -> dict:
    if modo_de_geracao not in ["bulk_load", "sem_bulk_load"]:
        raise ValueError(
            "Modo de geração inválido. Use 'bulk_load' ou 'sem_bulk_load'."
        )

    if modo_de_utilizacao not in ["vizualizacao", "docker"]:
        raise ValueError("Modo de utilização inválido. Use 'vizualizacao' ou 'docker'.")

    if modo_de_utilizacao == "docker":
        caminho_saida_base = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "database/scripts"
        )
    else:
        caminho_saida_base = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "arquivos_sql_gerados"
        )

    if modo_de_geracao == "bulk_load":
        caminho_operadoras = (
            os.path.join(caminho_saida_base, "operadoras_bulk_load")
            if modo_de_utilizacao == "vizualizacao"
            else caminho_saida_base
        )
        caminho_demonstracoes = (
            os.path.join(caminho_saida_base, "demonstracoes_bulk_load")
            if modo_de_utilizacao == "vizualizacao"
            else caminho_saida_base
        )
    else:
        caminho_operadoras = (
            os.path.join(caminho_saida_base, "operadoras_sem_bulk_load")
            if modo_de_utilizacao == "vizualizacao"
            else caminho_saida_base
        )
        caminho_demonstracoes = (
            os.path.join(caminho_saida_base, "demonstracoes_sem_bulk_load")
            if modo_de_utilizacao == "vizualizacao"
            else caminho_saida_base
        )

    return {
        "caminho_operadoras": caminho_operadoras,
        "caminho_demonstracoes": caminho_demonstracoes,
    }


def configurar_argumentos(parser: argparse.ArgumentParser) -> argparse.Namespace:
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
        help="Tipos de utilização: 'vizualizacao' ou 'docker'.",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host do banco de dados (padrão: localhost).",
    )
    parser.add_argument(
        "--database",
        type=str,
        default="testetec-ic",
        help="Nome do banco de dados (padrão: testetec-ic).",
    )
    parser.add_argument(
        "--user",
        type=str,
        default="admin",
        help="Usuário do banco de dados (padrão: admin).",
    )
    parser.add_argument(
        "--password",
        type=str,
        default="senhasegura",
        help="Senha do banco de dados (padrão: senhasegura).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5432,
        help="Porta do banco de dados (padrão: 5432).",
    )
    return parser.parse_args()


def __main__():
    # Configura o parser de argumentos
    parser = argparse.ArgumentParser(
        description="Script para inserir scripts SQL no banco de dados."
    )

    args = configurar_argumentos(parser)

    # Trata os argumentos para definir os caminhos
    configuracoes = trata_argumentos_do_script(
        args.modo_de_geracao, args.modo_de_utilizacao
    )

    # Parâmetros de conexão com o banco de dados
    conexao_params = {
        "host": args.host,
        "database": args.database,
        "user": args.user,
        "password": args.password,
        "port": args.port,
    }

    print("Iniciando a execução dos scripts SQL...")

    # Executa os scripts SQL nos diretórios configurados
    executar_scripts_sql_paralelo(
        configuracoes["caminho_operadoras"], conexao_params, max_workers=4
    )
    executar_scripts_sql_paralelo(
        configuracoes["caminho_demonstracoes"], conexao_params, max_workers=4
    )

    print("Todos os scripts foram executados com sucesso.")


if __name__ == "__main__":
    __main__()
