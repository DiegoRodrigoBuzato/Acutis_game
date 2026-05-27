FROM python:3.10-slim

# Instalar dependências do sistema necessárias para compilação (ex: Pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    zlib1g-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependências Python
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar resto do projeto
COPY . .

# Expor a porta 5000
EXPOSE 5000

# Usar Gunicorn com worker Eventlet (necessário para WebSockets)
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "app:app"]
