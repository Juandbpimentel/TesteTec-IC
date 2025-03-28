# Etapa de Web Scrapping
Para realizar esta tarefa que envolve carregar uma página e baixar os arquivos eu resolvi utilizar o python pois ele tem ótimas ferramentas para acesso de páginas e coleta de conteúdo delas, e também tem ferramentas simples de usar para implementar assincronismo e paralelismo, e também porque eu já tinha utilizado ele antes para fazer essas tarefas em estudos acadêmicos e pessoais.

## Ferramentas Utilizadas
- `os`  
  - Utilizei para obter o caminho do arquivo zip gerado, para facilitar de quem utilizar o script encontrar o arquivo.

- `requests`  
  - Utilizei para realizar a requisição HTTP iniciais, pois ele oferece uma forma muito simples de acessar o conteúdo.

- `BeautifulSoup`  
  - Utilizei para extrair os links dos arquivos que precisavam ser baixados da página HTML, pois ele simplifica muito a busca e manipulação de dados no código HTML.

- `asyncio`  
  - Utilizei para trabalhar de forma assíncrona com o cliente HTTP aiohttp, assim tendo mais desempenho e eficiência em atividades que se fossem feitas de forma síncrona demorariam bastante tempo.

- `aiohttp`  
  - Utilizei como cliente http para efetuar requisições HTTP de maneira assíncrona, fazendo com que aumentasse a eficiência do script usando paralelismo.

- `zipfile`  
  - Utilizei para compactar os arquivos baixados em um arquivo ZIP.
## Passos para executar o script
1. Instale as dependências do projeto com o comando:  
```bash
pip install -r requirements.txt
```
2. Execute o script com o comando:  
```bash
python web_scrapping.py
```
3. Aguarde o script baixar os arquivos e compactar em um arquivo ZIP.
4. Verifique o arquivo ZIP gerado na pasta do projeto.
5. Pronto, você baixou os arquivos da página e compactou em um arquivo ZIP.

## Como o script funciona
1. O script faz uma requisição HTTP para a página que contém os links dos arquivos que precisam ser baixados.
```python
def obter_html(url):
    resposta = requests.get(url)
    return resposta.text
```

2. O script utiliza o BeautifulSoup para extrair os links dos arquivos que precisam ser baixados.
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

3. O script utiliza o asyncio e o aiohttp para fazer as requisições HTTP de forma assíncrona e paralela.
```python
async def carregar_arquivo(session, link):
    async with session.get(link['link']) as resposta:
        conteudo = await resposta.read()
        return {
            'titulo': link['titulo'],
            'arquivo': conteudo
        }

async def carregar_arquivos_de_links(links):
    arquivos = []
    async with aiohttp.ClientSession() as session:
        tarefas = [carregar_arquivo(session, link) for link in links]
        resultados = await asyncio.gather(*tarefas)
        arquivos.extend(resultados)
    return arquivos
```
4. O script utiliza o zipfile para compactar os arquivos baixados em um arquivo ZIP.
```python
def armazenar_em_zip(arquivos, nome):
    with zipfile.ZipFile(f'{nome}', 'w') as arquivo_zip:
        for arquivo in arquivos:
            nome_arquivo = f"{arquivo['titulo']}.pdf"
            arquivo_zip.writestr(nome_arquivo, arquivo['arquivo'])
```

5. O script principal coordena todas as etapas e exibe o caminho do arquivo ZIP gerado.
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

if __name__ == "__main__":
    print('Iniciando o processo de web scrapping...')
    asyncio.run(__main__())
```

