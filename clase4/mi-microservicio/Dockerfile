FROM python:3.11-slim

<<<<<<< HEAD
# Establecer directorio de trabajo del servicio 1
WORKDIR /service1
=======
# Establecer directorio de trabajo
WORKDIR /app
>>>>>>> 08de200b8dc6dc88ca63825ba26d41f9df339881

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
<<<<<<< HEAD
COPY /service1/requirements.txt .

# Instalar dependencias de Python sin cache
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del servicio1
COPY /service1/main.py .

# Exponer el puerto
EXPOSE 8000
=======
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY /app/main.py .

# Exponer el puerto
EXPOSE 8001
>>>>>>> 08de200b8dc6dc88ca63825ba26d41f9df339881

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]