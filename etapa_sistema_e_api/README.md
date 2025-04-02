# **Etapa de Desenvolvimento do Sistema e API**

Este projeto implementa um sistema e uma API RESTful para gerenciar e consultar dados de operadoras de saúde e suas demonstrações contábeis. Ele foi desenvolvido utilizando boas práticas de design de software, com foco em escalabilidade, organização e facilidade de uso.

---

## **Resumo do Projeto**

### **Objetivo**
- Criar uma API RESTful para expor os dados das operadoras de saúde e suas demonstrações contábeis.
- Implementar endpoints para consultas específicas e análises de dados.
- Garantir a escalabilidade e a organização do sistema.

### **Destaques**
- **Arquitetura Limpa:** Separação clara entre camadas de controle, serviço e modelo.
- **Deploy Automatizado:** Deploy contínuo no **Google App Engine** (backend) e **Vercel** (frontend).
- **Banco de Dados na Nuvem:** Uso do **Google Cloud SQL** para armazenar os dados de forma segura e escalável.
- **CI/CD com Testes Automatizados:** Integração contínua configurada com GitHub Actions para rodar testes antes de cada deploy.
- **Documentação:** API documentada utilizando ferramentas como Swagger e Postman.
- **Postman Collection:** Uma collection foi criada para facilitar o teste e a documentação da API. O arquivo está disponível em `juandbpimentel_teste_tec_ic.postman_collection.json`.
- **Validação de Dados:** Uso de validações robustas para garantir a integridade das informações.
- **Desempenho:** Foco em otimização para consultas rápidas e eficientes.

---

## **Estrutura do Projeto**

```
etapa_sistema_e_api/
├── backend/
│   ├── .env
│   ├── .env.example
│   ├── api_test.py
│   ├── app.yaml
│   ├── app.yaml.template
│   ├── credentials.json
│   ├── database.py
│   ├── deploy.sh
│   ├── Dockerfile.dev
│   ├── Dockerfile.prod
│   ├── error_response.py
│   ├── logging_config.py
│   ├── logs.log
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   ├── routes/
│   │   ├── operadoras_routes.py
│   │   ├── demonstracoes_routes.py
│   ├── schemas.py
│   ├── services/
│   │   ├── operadoras_service.py
│   │   ├── demonstracoes_service.py
├── database/
│   ├── Dockerfile
│   ├── scripts/
│   │   ├── init.sql
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── plugins/
│   │   ├── services/
│   │   ├── stores/
│   │   ├── styles/
│   │   ├── pages/
│   │   │   ├── index.vue
│   │   │   ├── Operadoras/
│   │   │   │   ├── [registro_operadora].vue
├── docker-compose.yml
├── start_local.sh
├── juandbpimentel_teste_tec_ic.postman_collection.json
```

---

## **Componentes do Projeto**

### **1. Backend**
O backend foi desenvolvido utilizando **FastAPI** e **PostgreSQL**. Ele é responsável por expor os dados das operadoras de saúde e suas demonstrações contábeis por meio de uma API RESTful.

#### **Principais Arquivos**
- **`main.py`**: Configuração principal do FastAPI, incluindo middlewares e rotas.
- **`models.py`**: Definição dos modelos de dados utilizando SQLAlchemy.
- **`routes/`**: Contém as rotas da API, como:
  - `operadoras_routes.py`: Endpoints para gerenciar operadoras.
  - `demonstracoes_routes.py`: Endpoints para gerenciar demonstrações contábeis.
- **`services/`**: Contém a lógica de negócios, como:
  - operadoras_service.py: Lógica para consultas e manipulação de operadoras.
  - demonstracoes_service.py: Lógica para consultas e manipulação de demonstrações contábeis.
- **`database.py`**: Configuração do banco de dados PostgreSQL.
- **`logging_config.py`**: Configuração de logs para monitoramento e depuração.

#### **Principais Funcionalidades**
- Endpoints para listar, filtrar e consultar operadoras e demonstrações contábeis.
- Integração com **Google Cloud SQL** para persistência de dados.
- Suporte a paginação e filtros avançados.

---

### **2. Frontend**
O frontend foi desenvolvido utilizando **Vue.js** e **Vuetify**. Ele fornece uma interface amigável para interação com a API.

#### **Principais Arquivos**
- **`App.vue`**: Componente principal do Vue.js.
- **`pages/`**: Contém as páginas principais da aplicação, como:
  - index.vue: Página inicial para listagem de operadoras.
  - [registro_operadora].vue: Página de detalhes de uma operadora.
- **`services/`**: Contém os serviços para comunicação com a API.
- **`components/`**: Componentes reutilizáveis, como:
  - `CustomDataTable.vue`: Tabela genérica para exibir dados.

#### **Principais Funcionalidades**
- Listagem de operadoras com filtros e paginação.
- Visualização de detalhes de uma operadora.
- Integração com a API para exibir dados em tempo real.

---

### **3. Banco de Dados**
O banco de dados foi configurado utilizando **Google Cloud SQL** com PostgreSQL. Ele contém as tabelas para armazenar os dados das operadoras e suas demonstrações contábeis.

#### **Principais Arquivos**
- **`init.sql`**: Script para inicializar o banco de dados com as tabelas necessárias.
- **`models.py`**: Definição das tabelas utilizando SQLAlchemy.

#### **Principais Funcionalidades**
- Armazenamento de dados das operadoras e demonstrações contábeis.
- Suporte a consultas analíticas para identificar operadoras com maiores despesas.

---

### **4. Deploy**

#### **Backend**
- O backend foi implantado no **Google App Engine** utilizando o arquivo `app.yaml` e o `Dockerfile.prod`.
- O deploy é automatizado com GitHub Actions, que executa testes antes de enviar o código para produção.

#### **Frontend**
- O frontend foi implantado no **Vercel**, que oferece integração contínua com o repositório GitHub.

---

### **5. CI/CD**
O projeto utiliza **GitHub Actions** para integração e entrega contínuas. O pipeline inclui:

1. **Testes Automatizados**:
   - Testes são executados automaticamente antes de cada deploy.
   - Utiliza `pytest` para o backend.

2. **Deploy Automatizado**:
   - O backend é implantado no Google App Engine após a aprovação dos testes.
   - O frontend é implantado no Vercel automaticamente após cada push para o branch principal.

---

### **6. Postman Collection**
Uma collection foi criada para facilitar o teste e a documentação da API. Ela inclui exemplos de requisições para todos os endpoints do backend. O arquivo está disponível em `juandbpimentel_teste_tec_ic.postman_collection.json`.

---

## **Execução do Projeto**

### **1. Backend**
1. Instale as dependências:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Execute o backend:
   ```bash
   uvicorn backend.main:app --reload
   ```

### **2. Frontend**
1. Instale as dependências:
   ```bash
   npm install
   ```
2. Execute o frontend:
   ```bash
   npm run dev
   ```

### **3. Banco de Dados**
1. Suba o banco de dados com Docker:
   ```bash
   docker-compose up postgres
   ```

---

## **Destaques Técnicos**
- **FastAPI**: Framework rápido e eficiente para desenvolvimento de APIs.
- **Vue.js**: Framework progressivo para construção de interfaces de usuário.
- **Google Cloud SQL**: Banco de dados relacional robusto e escalável na nuvem.
- **Docker**: Facilita a execução e o isolamento do ambiente de desenvolvimento.
- **Google App Engine**: Plataforma de deploy escalável para o backend.
- **Vercel**: Plataforma de deploy para o frontend com integração contínua.

---

Se precisar de mais detalhes ou ajustes, é só avisar! 😊