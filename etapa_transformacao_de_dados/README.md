# Etapa de Tratamento de Dados
Para realizar esta tarefa que envolve a extração de tabelas de arquivos PDF e a geração de um arquivo CSV compactado em um ZIP, eu resolvi utilizar o Python, pois ele tem ótimas ferramentas para manipulação de dados e arquivos.

## Ferramentas Utilizadas
- `zipfile`
  - Utilizei para descompactar o arquivo ZIP contendo os PDFs e para compactar o arquivo CSV gerado.

- `pdfplumber`
  - Utilizei para abrir e extrair tabelas dos arquivos PDF, pois ele oferece uma interface simples e eficiente para manipulação de PDFs.

- `pandas`
  - Utilizei para manipulação e transformação das tabelas extraídas dos PDFs, pois ele oferece uma estrutura de dados poderosa e flexível.

- `io`
  - Utilizei para manipulação de streams em memória, evitando a necessidade de gravar arquivos temporários no disco.

- `os`
  - Utilizei para obter o caminho do arquivo ZIP gerado, para facilitar de quem utilizar o script encontrar o arquivo.


## Passos para executar o script
1. Instale as dependências do projeto com o comando:
```bash
pip install -r requirements.txt
```
2. Execute o script com o comando:
```bash
python tratamento_de_dados.py
```
3. Aguarde o script extrair as tabelas dos PDFs e gerar o arquivo CSV compactado em um ZIP.
4. Verifique o arquivo ZIP gerado na pasta do projeto.
5. Pronto, você extraiu as tabelas dos PDFs e gerou um arquivo CSV compactado em um ZIP.

## Como o script funciona
1. O script descompacta o arquivo ZIP contendo os PDFs.
```python
def importar_pdfs_do_zip(zip_file):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        nomes = zip_ref.namelist()
        pdfs = []
        for arquivo in nomes:
            if arquivo.lower().endswith('.pdf'):
                conteudo = zip_ref.read(arquivo)
                pdfs.append({'nome': arquivo, 'conteudo': conteudo})
    return pdfs
```

2. O script filtra e carrega o conteúdo do PDF desejado em um stream de memória.
```python
def filtrar_e_carregar_arquivo(pdfs, arquivo_das_tabelas):
    arquivos_filtrados = [pdf for pdf in pdfs if pdf['nome'] == arquivo_das_tabelas]

    if not arquivos_filtrados:
        print(f"Arquivo '{arquivo_das_tabelas}' não encontrado no zip.")
        return

    arquivo = arquivos_filtrados[0]
    return io.BytesIO(arquivo['conteudo'])
```

3. O script utiliza o pdfplumber para abrir o PDF e extrair as tabelas de cada página.
```python
def processar_paginas_e_extrair_tabelas(pdfs, arquivo_das_tabelas):
    pdf_stream = filtrar_e_carregar_arquivo(pdfs, arquivo_das_tabelas)

    print(f"Tabelas extraídas do {arquivo_das_tabelas}:")
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
```

4. O script trata os dados das tabelas extraídas, renomeando colunas e substituindo quebras de linha.
```python
def trata_dados_tabela(df):
    df = df.rename(columns={
        'RN\n(alteração)': 'RN (Alteração)',
        'OD': 'Seg. Odontológica',
        'AMB': 'Seg. Ambulatorial'
    })
    df = df.replace(r'\n', ' ', regex=True)
    return df
```

5. O script salva o DataFrame resultante em um arquivo CSV e o compacta em um arquivo ZIP.
```python
def salvar_csv_zip(df, nome_zip):
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=True)
    csv_buffer.seek(0)
    with zipfile.ZipFile(nome_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('tabela.csv', csv_buffer.getvalue())
```

6. O script principal coordena todas as etapas e exibe o DataFrame final.
```python
def __main__():
    nome_do_zip = 'arquivos_baixados.zip'
    arquivo_das_tabelas = 'Anexo I.pdf'

    pdfs = importar_pdfs_do_zip(nome_do_zip)
    df_todas_tabelas = processar_paginas_e_extrair_tabelas(pdfs, arquivo_das_tabelas)

    if df_todas_tabelas is not None:
        df_final = trata_dados_tabela(df_todas_tabelas)
        salvar_csv_zip(df_final, 'Anexo I.zip')
    else:
        print("Nenhuma tabela encontrada no arquivo")

if __name__ == '__main__':
    __main__()
```