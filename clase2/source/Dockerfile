# =====================================================================================
# ETAPA 1: Construcción (Build Stage)
# =====================================================================================
FROM gradle:8.4.0-jdk21 AS build

WORKDIR /home/gradle/src

#Copia del código fuente
COPY . .

#compilación y empaquetado de la aplicación
RUN gradle clean bootJar --no-daemon

# =====================================================================================
# ETAPA 2: Ejecución (Runtime Stage)
# =====================================================================================
FROM eclipse-temurin:21-jre-alpine

# Establecer el directorio de trabajo
WORKDIR /app

# Crear un usuario no root para ejecutar la aplicación
RUN addgroup -S spring && adduser -S spring -G spring

# Cambiar la propiedad del directorio de trabajo al usuario no root
RUN chown -R spring:spring /app

# Cambiar al usuario no root
USER spring

# Copiar el archivo JAR desde la etapa de construcción
COPY --from=build /home/gradle/src/build/libs/*.jar app.jar

# Exponer el puerto en el que la aplicación escuchará
EXPOSE 8080

# Comando para ejecutar la aplicación
ENTRYPOINT ["java", "-jar", "app.jar"]