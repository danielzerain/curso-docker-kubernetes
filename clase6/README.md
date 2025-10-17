# Servidor WEB-NGINX

**Curso:** Docker & Kubernetes - Clase 6
**Estudiante:** Daniel Zerain Medinaceli

Despliegue de servidor web NGINX con 3 replicas

## Stack

- **Aplicación:** Nginx 
- **Kubernetes:** minikube
- **Réplicas:** 3


## Ejecución

1. Clonar:
   ```bash
   git clone https://github.com/danielzerain/curso-docker-kubernetes.git
   
   cd curso-docker-kubernetes/clase6
   ```

2. Desplegar:
   ```bash
   kubectl apply -f deployment.yaml

   kubectl apply -f service.yaml
   ```

3. Acceder:
   - URL: http://<MINIKUBE-IP>:30200