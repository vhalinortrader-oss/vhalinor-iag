# 14_Dockerfile
"""
Dockerfile para VhalinorTrade
"""

# Build stage
FROM python:3.9-slim as builder

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Instala TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install

# Copia requirements
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Production stage
FROM python:3.9-slim

WORKDIR /app

# Copia TA-Lib do builder
COPY --from=builder /usr/lib/libta_lib* /usr/lib/
COPY --from=builder /usr/include/ta-lib /usr/include/ta-lib
COPY --from=builder /root/.local /root/.local

# Instala dependências runtime
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copia código
COPY . .

# Path
ENV PATH=/root/.local/bin:$PATH

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Cria diretórios
RUN mkdir -p /app/data /app/models /app/logs

# Expõe porta do monitor
EXPOSE 8501

# Comando de execução
CMD ["python", "run.py"]