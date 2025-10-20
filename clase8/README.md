**a) Descripción del proyecto:**
- Stack desplegado (frontend + backend)
- Conceptos aplicados (Ingress, health probes, HPA)

**b) Instrucciones de despliegue:**
1. Habilitar addons (ingress, metrics-server)
```bash
minikube addons enable ingress
```
![alt text](<screenshots/captura1 (2).png>)

2. Aplicar manifests
```bash
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f  backend-service.yaml
kubectl apply -f  frontend-service.yaml
```
3. Verificar recursos
```bash
kubectl get all
```
![alt text](<screenshots/captura2 (2).png>)

Verificacion de **Liveness**

```bash
kubectl describe pod
```
![alt text](<screenshots/captura3 (2).png>)

4. Probar Ingress
```bash
kubectl apply -f ingress.yaml
kubectl get ingress
```
5. Probar HPA con carga
```bash
 minikube addons enable metrics-server
```
![alt text](<screenshots/captura6 (2).png>)

```bash
 kubectl get pods -n kube-system | grep metrics-server

 kubectl top nodes
```

![alt text](<screenshots/captura8 (2).png>)

![alt text](screenshots/top.png)

```bash
 kubectl get pods -l app=php-apache

 ```

 ```bash
kubectl describe hpa php-apache
 ```
 ![alt text](<screenshots/captura9 (2).png>)

 Con carga

 ![alt text](screenshots/carga.png)


**Verificar carga**
 ```bash
watch kubectl get pods -l app=php-apache
 ```
 ![alt text](screenshots/carga2.png)