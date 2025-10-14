FROM python:3.13-alpine

# Establecer directorio de trabajo del servicio 1
WORKDIR /app

# Instalar dependencias del sistema
RUN apk update && apk add --no-cache \
    gcc \
    libpq \
    && adduser -D -u 1000 appuser

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python sin cache
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del servicio1
COPY main.py .

# Cambiar a usuario no root
USER appuser

# Exponer el puerto
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s \
  CMD node -e "require('http').get('http://localhost:8000/api/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

LABEL maintainer="daniel.zerin" \
      version="1.0-optimizado" \
      description="Servicio de Productos" \
      security.scan="trivy" \
      security.non-root="true"

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]