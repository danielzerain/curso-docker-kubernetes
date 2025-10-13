FROM python:3.11-slim

# Establecer directorio de trabajo del servicio 1
WORKDIR /service1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY /service1/requirements.txt .

# Instalar dependencias de Python sin cache
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del servicio1
COPY /service1/main.py .

# Exponer el puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]