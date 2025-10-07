# Tarea 1 - Configuración de Repositorio y Primer Desafío

## Despliegue de  Apache HTTP Server (httpd)

### Comandos Ejecutados
```docker pull httpd```

Comando que se ejecuto para obtener la imagen de httpd desde docker hub

![Imagen de contenedor descargada](screenshots/captura1.png)

```docker run -d --name mi-apache -p 8081:80 httpd:latest```

Comando que se ejecuto para correr el contenedor

```docker ps```

Comando para verificar que se encuentre corriendo

![Imagen de contenedor descargada](screenshots/captura2.png)

```docker logs mi-apache```

Comando para ver los logs del contenedor

![Imagen de contenedor descargada](screenshots/captura3.png)

![Imagen de contenedor descargada](screenshots/captura4.png)

```docker stop mi-apache```

Comando para detener el contenedor

```docker ps -a```

Comando para ver todos los cotenedores incluidos los que no se encuentran corriendo

![Imagen de contenedor descargada](screenshots/captura5.png)

```docker rm mi-apache```

Comando para eliminar el contenedor mi-apache

![Imagen de contenedor descargada](screenshots/captura6.png)

```docker images```

Comando para ver las imagenes descargadas

```docker rmi httpd:latest```

Comando para eliminar la imagen httpd:latest

![Imagen de contenedor descargada](screenshots/captura7.png)
