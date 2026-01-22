FROM python:3.13-slim

# Instalar dependencias del sistema para Firefox y herramientas de compilación
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    firefox \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libnss3 \
    libcups2 \
    libxss1 \
    libasound2 \
    libxtst6 \
    libxrandr2 \
    libatk1.0-0 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    libxshmfence1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar geckodriver para Firefox
RUN GECKODRIVER_VERSION=$(curl -s "https://api.github.com/repos/mozilla/geckodriver/releases/latest" | grep -Po '"tag_name": "\K.*?(?=")') && \
    wget -O /tmp/geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz" && \
    tar -xzf /tmp/geckodriver.tar.gz -C /tmp && \
    mv /tmp/geckodriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/geckodriver && \
    rm /tmp/geckodriver.tar.gz

# Instalar uv para gestión de dependencias
RUN pip install uv

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración
COPY pyproject.toml uv.lock ./

# Instalar dependencias con uv
RUN uv sync --frozen

# Copiar código fuente
COPY src/ ./src/
COPY test/ ./test/

# Crear directorio para resultados
RUN mkdir -p /app/results

# Exponer puerto (opcional, para futuras APIs)
EXPOSE 8000

# Comando por defecto
CMD ["uv", "run", "python", "-m", "src.job.occ.scraper"]