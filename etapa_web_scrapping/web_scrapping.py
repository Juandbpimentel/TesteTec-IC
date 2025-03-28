import os
import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import zipfile

def obter_html(url):
    resposta = requests.get(url)
    return resposta.text

def manipular_titulo(texto):
    titulo = texto.replace('.', '')
    return titulo[:-1] + titulo[-1].upper()

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

def armazenar_em_zip(arquivos, nome):
    with zipfile.ZipFile(f'{nome}', 'w') as arquivo_zip:
        for arquivo in arquivos:
            nome_arquivo = f"{arquivo['titulo']}.pdf"
            arquivo_zip.writestr(nome_arquivo, arquivo['arquivo'])

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