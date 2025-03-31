FROM postgres:17

# Instala dependências básicas e ferramentas de compilação
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-server-dev-17 \
    wget \
    curl \
    liblz4-dev \
    lz4 \
    libselinux1-dev \
    libzstd-dev \
    libpam0g-dev \
    libkrb5-dev \
    zlib1g-dev \
    libreadline-dev \
    unzip \
    git \
    libcurl4-openssl-dev \
    libjson-c-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala pg_bulkload (versão 1.1.21 ou outra compatível)
RUN wget https://github.com/ossc-db/pg_bulkload/archive/refs/tags/VERSION3_1_22.tar.gz \
    && tar -xzf VERSION3_1_22.tar.gz \
    && cd pg_bulkload-VERSION3_1_22 \
    && make \
    && make install \
    && cd .. && rm -rf pg_bulkload-VERSION3_1_22 VERSION3_1_22.tar.gz

# Instala a extensão "http" (postgresql-http)
RUN git clone https://github.com/pramsey/pgsql-http.git \
    && cd pgsql-http \
    && make \
    && make install \
    && cd .. && rm -rf pgsql-http

# Habilita extensões e configura acesso (opcional: ajuste conforme necessário)
RUN echo "host all all all trust" >> /usr/share/postgresql/pg_hba.conf.sample \
    && echo "shared_preload_libraries = 'pg_bulkload'" >> /usr/share/postgresql/postgresql.conf.sample

# Copia scripts de inicialização e carga
COPY scripts/*.sql /docker-entrypoint-initdb.d/
