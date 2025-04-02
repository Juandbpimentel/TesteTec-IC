# **Etapa de Web Scrapping**

Este projeto realiza o download de arquivos PDF a partir de uma página web e os compacta em um arquivo ZIP. Ele foi desenvolvido utilizando o Python, aproveitando suas ferramentas robustas para acesso a páginas web, coleta de conteúdo e execução assíncrona para maior eficiência.

---

## **Resumo do Projeto**

### **Objetivo**
- Realizar o download de arquivos PDF de uma página web específica.
- Compactar os arquivos baixados em um único arquivo ZIP.
- Automatizar o processo de coleta e organização dos arquivos.

### **Objetivos Técnicos Realizados**
- **Extração de Links:** Uso do `BeautifulSoup` para localizar e filtrar os links dos arquivos na página HTML.
- **Execução Assíncrona:** Uso de `asyncio` e `aiohttp` para realizar downloads simultâneos, otimizando o tempo de execução.
- **Compactação:** Geração de um arquivo ZIP contendo os PDFs baixados.
- **Automação Completa:** Processo automatizado para acessar a página, baixar os arquivos e compactá-los.

---

## **Etapas do Projeto**

### **1. Extração de Links**
Os links dos arquivos PDF são extraídos da página HTML utilizando o `BeautifulSoup`. Apenas os links que atendem aos filtros especificados são selecionados.

### **2. Download Assíncrono**
Os arquivos PDF são baixados de forma assíncrona utilizando `aiohttp` e `asyncio`, permitindo maior eficiência e paralelismo.

### **3. Compactação dos Arquivos**
Os arquivos baixados são compactados em um único arquivo ZIP utilizando a biblioteca `zipfile`.

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
python web_scrapping.py
```

### **3. Resultado**
- O script irá gerar um arquivo ZIP contendo os PDFs baixados.
- O arquivo ZIP será salvo na pasta do projeto com o nome especificado no script.

---

## **Como o Script Funciona**

### **1. Extração de Links**
O script faz uma requisição HTTP para a página e utiliza o `BeautifulSoup` para localizar os links dos arquivos:
```python
def obter_links_do_html(filtros, html):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)
    links_filtrados = []
    for filtro in filtros:
        for link in links:
            if filtro["palavra_chave_titulo"] in link.text and filtro["palavra_chave_link"] in link['href']:
                titulo = manipular_titulo(link.text)
                if titulo not in [lf['titulo'] for lf in links_filtrados]:
                    links_filtrados.append({
                        'titulo': titulo,
                        'link': link['href']
                    })
    return links_filtrados
```

### **2. Download Assíncrono**
Os arquivos são baixados de forma assíncrona utilizando `aiohttp`:
```python
async def carregar_arquivos_de_links(links):
    arquivos = []
    async with aiohttp.ClientSession() as session:
        tarefas = [carregar_arquivo(session, link) for link in links]
        resultados = await asyncio.gather(*tarefas)
        arquivos.extend(resultados)
    return arquivos
```

### **3. Compactação dos Arquivos**
Os arquivos baixados são compactados em um arquivo ZIP:
```python
def armazenar_em_zip(arquivos, nome):
    with zipfile.ZipFile(f'{nome}', 'w') as arquivo_zip:
        for arquivo in arquivos:
            nome_arquivo = f"{arquivo['titulo']}.pdf"
            arquivo_zip.writestr(nome_arquivo, arquivo['arquivo'])
```

### **4. Coordenação do Processo**
O script principal coordena todas as etapas e exibe o caminho do arquivo ZIP gerado:
```python
async def __main__():
    url = 'https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos'
    nome_arquivo_zip = 'arquivos_baixados.zip'
    filtros_arquivos = [
        {"palavra_chave_titulo": "Anexo I", "palavra_chave_link": ".pdf"},
        {"palavra_chave_titulo": "Anexo II", "palavra_chave_link": ".pdf"}
    ]
    html = obter_html(url)
    links = obter_links_do_html(filtros_arquivos, html)
    arquivos = await carregar_arquivos_de_links(links)
    armazenar_em_zip(arquivos, nome_arquivo_zip)
    caminho_completo = os.path.abspath(f'{nome_arquivo_zip}')
    print(f'Processo de web scrapping finalizado com sucesso! Arquivos baixados e armazenados no arquivo zip {caminho_completo}')
```

---

## **Estrutura do Projeto**
```
etapa_web_scrapping/
├── web_scrapping.py
├── requirements.txt
└── README.md
```

---

## **Destaques de Práticas de Otimização**
- **Execução Assíncrona:** Uso de `asyncio` e `aiohttp` para downloads simultâneos, otimizando o tempo de execução.
- **Extração de Links:** Uso do `BeautifulSoup` para localizar e filtrar links de forma eficiente.
- **Compactação:** Geração de arquivos compactados para facilitar o armazenamento e compartilhamento.
- **Automação Completa:** Processo automatizado para acessar a página, baixar os arquivos e compactá-los.

---