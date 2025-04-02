import os
import zipfile
import pdfplumber
import pandas as pd
import io


def importar_pdfs_do_zip(zip_file):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        nomes = zip_ref.namelist()
        pdfs = []
        for arquivo in nomes:
            if arquivo.lower().endswith('.pdf'):
                conteudo = zip_ref.read(arquivo)
                pdfs.append({'nome': arquivo, 'conteudo': conteudo})
    return pdfs

def filtrar_e_carregar_arquivo(pdfs, arquivo_das_tabelas):
    arquivos_filtrados = [pdf for pdf in pdfs if pdf['nome'] == arquivo_das_tabelas]

    if not arquivos_filtrados:
        print(f"Arquivo '{arquivo_das_tabelas}' não encontrado no zip.")
        return

    arquivo = arquivos_filtrados[0]

    return io.BytesIO(arquivo['conteudo'])


def processar_paginas_e_extrair_tabelas(pdfs, arquivo_das_tabelas):
    pdf_stream = filtrar_e_carregar_arquivo(pdfs, arquivo_das_tabelas)
    with pdfplumber.open(pdf_stream) as pdf_doc:
        todas_tabelas = []
        for pagina in pdf_doc.pages:
            tabela = pagina.extract_table()
            if tabela:
                df_tabela = pd.DataFrame(tabela[1:], columns=tabela[0])
                todas_tabelas.append(df_tabela)
        if not todas_tabelas:
            print("Nenhuma tabela encontrada no arquivo")
            return None
        return pd.concat(todas_tabelas, ignore_index=True)

def trata_dados_tabela(df):
    df = df.rename(columns={
        'RN\n(alteração)': 'RN (Alteração)',
        'OD': 'Seg. Odontológica',
        'AMB': 'Seg. Ambulatorial'
    })
    df = df.replace(r'\n', ' ', regex=True)
    return df

def salvar_csv_zip(df, nome_zip):
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=True)
    csv_buffer.seek(0)
    with zipfile.ZipFile(nome_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('tabela.csv', csv_buffer.getvalue())

def __main__():
    nome_do_zip = 'arquivos_baixados.zip'
    arquivo_das_tabelas = 'Anexo I.pdf'

    print(f"Processando '{nome_do_zip}' e '{arquivo_das_tabelas}'")
    pdfs = importar_pdfs_do_zip(nome_do_zip)
    df_todas_tabelas = processar_paginas_e_extrair_tabelas(pdfs, arquivo_das_tabelas)

    if df_todas_tabelas is not None:
        df_final = trata_dados_tabela(df_todas_tabelas)
        salvar_csv_zip(df_final, arquivo_das_tabelas.replace('.pdf', '.zip'))
        caminho_completo = os.path.abspath(f'{arquivo_das_tabelas.replace('.pdf', '.zip')}')
        print(f"Arquivo 'Anexo I.zip' gerado com sucesso, você pode abri-lo para ver a tabela utilizando o seguinte caminho: {caminho_completo}")
    else:
        print("Nenhuma tabela encontrada no arquivo")


if __name__ == '__main__':
    __main__()
