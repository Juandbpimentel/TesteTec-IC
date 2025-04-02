# **Etapa de Tratamento de Dados**

Este projeto realiza a extração de tabelas de arquivos PDF e a geração de um arquivo CSV compactado em um ZIP. Ele foi desenvolvido utilizando o Python, aproveitando suas ferramentas robustas para manipulação de dados e arquivos.

---

## **Resumo do Projeto**

### **Objetivo**
- Extrair tabelas de arquivos PDF fornecidos.
- Gerar um arquivo CSV consolidado e compactado em um ZIP.
- Automatizar o processo de tratamento e organização dos dados extraídos.

### **Objetivos Técnicos Realizados**
- **Extração de Dados:** Uso do `pdfplumber` para extrair tabelas diretamente de arquivos PDF.
- **Manipulação de Dados:** Uso do `pandas` para tratar e transformar os dados extraídos.
- **Compactação:** Geração de arquivos CSV compactados em formato ZIP para facilitar o armazenamento e compartilhamento.
- **Automação Completa:** Processo automatizado para descompactar arquivos ZIP, processar PDFs e gerar o resultado final.

---

## **Etapas do Projeto**

### **1. Extração de PDFs**
Os arquivos PDF são extraídos de um arquivo ZIP utilizando a biblioteca `zipfile`. Apenas os arquivos com extensão `.pdf` são processados.

### **2. Processamento de Tabelas**
As tabelas são extraídas de cada página dos PDFs utilizando o `pdfplumber`. Em seguida, os dados são tratados com o `pandas`:
- Renomeação de colunas para padronização.
- Substituição de quebras de linha por espaços.
- Consolidação de todas as tabelas em um único DataFrame.

### **3. Geração do CSV Compactado**
O DataFrame consolidado é salvo em um arquivo CSV, que é então compactado em um arquivo ZIP utilizando a biblioteca `zipfile`.

---

## **Execução do Script**

### **1. Instalação de Dependências**
Instale as dependências do projeto com o comando:
```bash
pip install -r requirements.txt
```

### **2. Execução**
Execute o script principal com o comando:
```bash
python tratamento_de_dados.py
```

### **3. Resultado**
- O script irá gerar um arquivo ZIP contendo o CSV consolidado.
- O arquivo ZIP será salvo na pasta do projeto com o nome especificado no script.

---

## **Como o Script Funciona**

### **1. Importação de PDFs do ZIP**
Os PDFs são extraídos do arquivo ZIP e carregados em memória:
```python
def importar_pdfs_do_zip(zip_file):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        nomes = zip_ref.namelist()
        pdfs = [
            {'nome': arquivo, 'conteudo': zip_ref.read(arquivo)}
            for arquivo in nomes if arquivo.lower().endswith('.pdf')
        ]
    return pdfs
```

### **2. Extração de Tabelas**
As tabelas são extraídas de cada página dos PDFs utilizando o `pdfplumber`:
```python
def processar_paginas_e_extrair_tabelas(pdfs, arquivo_das_tabelas):
    pdf_stream = filtrar_e_carregar_arquivo(pdfs, arquivo_das_tabelas)
    with pdfplumber.open(pdf_stream) as pdf_doc:
        todas_tabelas = [
            pd.DataFrame(pagina.extract_table()[1:], columns=pagina.extract_table()[0])
            for pagina in pdf_doc.pages if pagina.extract_table()
        ]
    return pd.concat(todas_tabelas, ignore_index=True) if todas_tabelas else None
```

### **3. Tratamento dos Dados**
Os dados extraídos são tratados para padronização:
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

### **4. Geração do CSV Compactado**
O DataFrame tratado é salvo em um arquivo CSV e compactado em um ZIP:
```python
def salvar_csv_zip(df, nome_zip):
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    with zipfile.ZipFile(nome_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('tabela.csv', csv_buffer.getvalue())
```

---

## **Estrutura do Projeto**
```
etapa_transformacao_de_dados/
├── tratamento_de_dados.py
├── arquivos_baixados.zip
├── requirements.txt
└── README.md
```

---

## **Destaques de Práticas de Otimização**
- **Automação Completa:** Processo automatizado para extração, tratamento e compactação de dados.
- **Manipulação de PDFs:** Uso do `pdfplumber` para extração eficiente de tabelas.
- **Flexibilidade:** Tratamento de dados com o `pandas` para atender diferentes formatos de tabelas.
- **Compactação:** Geração de arquivos compactados para facilitar o armazenamento e compartilhamento.

---