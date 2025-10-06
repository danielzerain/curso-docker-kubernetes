# =====================================================================================
# ETAPA 1: Construcción (Build Stage)
# =====================================================================================
FROM gradle:8.4.0-jdk21 AS build

WORKDIR /home/gradle/src

COPY . .

RUN gradle clean bootJar --no-daemon

# =====================================================================================
# ETAPA 2: Ejecución (Runtime Stage)
# =====================================================================================
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

RUN addgroup -S spring && adduser -S spring -G spring

RUN chown -R spring:spring /app

USER spring

COPY --from=build /home/gradle/src/build/libs/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]