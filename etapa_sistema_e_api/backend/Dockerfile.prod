# backend/Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Copia o requirements.txt e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baixa o Cloud SQL Auth Proxy
RUN apt-get update && apt-get install -y wget \
    && wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy \
    && chmod +x cloud_sql_proxy

# Copia o restante do código
COPY . .

EXPOSE 8080

# CMD: inicia o Cloud SQL Auth Proxy e, em seguida, o backend
# Substitua <INSTANCE_CONNECTION_NAME> pelo nome da sua instância no formato: projeto:região:instância
CMD ./cloud_sql_proxy -instances=testetec-ic:southamerica-east1:testetec-id-postgres=tcp:5432 -credential_file=/app/credentials.json & \
    uvicorn main:app --host 0.0.0.0 --port 8080
