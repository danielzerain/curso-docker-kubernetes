# Tarea 3 - Aplicación Multi-Contenedor con Docker Compose

# Tienda Virtual de Hardware

**Curso:** Docker & Kubernetes - Clase 3

**Estudiante:** Daniel Zerain

La aplicacion lista los componentes de hardware detallando sus caracteristicas, precios y cantidad en stock

* Nota: *Se versiono el archivo .env solo para fines de pruebas* 

## Stack

- **App:** Python

- **Base de datos:** PostgreSQL

- **Front :** HTML, Javascript desplegado en nginx

## Ejecución
1. Clonar el proyecto:
   ```bash
   git clone https://github.com/danielzerain/curso-docker-kubernetes.git
   cd curso-docker-kubernetes/clase3

2. Levantar servicios:
   ```bash
   docker compose up -d

![Levantar servicios](screenshots/captura4.png)

3. Acceder a la aplicacion:
   - API: http://localhost:8000
   - WEB: http://localhost

4. Pruebas:

## Verificación

1. Servicios corriendo:
   ```bash
   docker compose ps

![Servicosp Corriendo](screenshots/captura3.png)

2. Acceder a la pagina web: http://localhost

![Servicosp Corriendo](screenshots/captura5.png)

2. Acceder a los servicios: http://localhost:8000/api/productos

![Servicosp Corriendo](screenshots/captura6.png)

3. Verificacion de Volumenes persistentes:

   ```bash
   docker compose down
   ```

![Parar Servicios](screenshots/captura2.png)

   ```bash
   docker compose up -d

   docker volume ls 
   ```

![Volumen Servicios](screenshots/captura3.png)

3. Verificacion de Red:

   ```bash
   docker network ls
   ```
![Red Servicios](screenshots/captura1.png)

   ```bash
   docker exec -it tienda_db /bin/bash
   ```

![Ping Servicios](screenshots/captura10.png)