# Guía de Despliegue en Hetzner VPS - Arte Ideas

Este documento detalla los pasos necesarios para desplegar la aplicación "Arte Ideas" en un servidor VPS de Hetzner utilizando Docker, Nginx y Certbot.

## Pasos del Proceso de Despliegue

### 1. Preparación y Pruebas Locales

Antes de subir cualquier cambio al servidor, es fundamental asegurar la estabilidad de la aplicación.

- **Clonación:** Trabajar sobre una versión limpia del repositorio.
- **Pruebas Locales:** Ejecutar los contenedores localmente utilizando `docker-compose up --build`.
- **Verificación:** Comprobar que el frontend se comunique correctamente con el backend y que la base de datos persista la información.

### 2. Actualización del Repositorio

Una vez confirmada la estabilidad local:

- Hacer un **Commit** con los cambios realizados (correcciones de rutas, variables de entorno, etc.).
- Hacer un **Push** a la rama principal (`main`) en el repositorio remoto (GitHub/GitLab).

### 3. Acceso y Preparación del VPS

Conectarse al servidor VPS por medio de SSH para preparar el entorno de producción.

```bash
ssh root@tu_ip_vps
```

- Instalar dependencias si no están presentes (Docker, Docker Compose, Nginx, Certbot).
- Navegar al directorio de despliegue o clonar el repositorio:

```bash
git clone https://github.com/usuario/arteideas-app.git
cd arteideas-app
```

### 4. Configuración de Entorno en Producción

Actualizar el repositorio en el VPS para incluir las últimas mejoras.

- Si ya existe el repo en el VPS: `git pull origin main`.
- Configurar el archivo `.env` con las credenciales de producción (Base de datos, tokens, secretos).
- **Importante:** Asegurarse de que el DB_HOST apunte al nombre del servicio en Docker (`db`).

### 5. Lanzamiento de Contenedores

Crear y encender los servicios de la aplicación.

```bash
docker-compose up -d --build
```

- Verificar que los contenedores estén corriendo: `docker ps`.
- Comprobar los logs para detectar errores tempranos: `docker-compose logs -f`.

### 6. Configuración de Dominio y Reverse Proxy (Nginx)

Direccionar el tráfico del dominio hacia los contenedores locales.

- Modificar la configuración de Nginx en `/etc/nginx/sites-available/arteideas`.
- Cambiar las referencias de `localhost` por el dominio configurado.
- Configurar el proxy para redirigir el tráfico del puerto 80 (y luego 443) al puerto del frontend (3000) y las peticiones `/api` al backend (9000).

Ejemplo de bloque Nginx:

```nginx
server {
    server_name arteideas.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 7. Migración de datos y Limpieza de LocalStorage

Asegurar que la aplicación utilice la base de datos centralizada en lugar de almacenamiento local en el navegador.

- Validar que las funciones de persistencia apunten a los endpoints del servidor.
- Limpiar el uso innecesario de `localStorage` para datos críticos que deben ser gestionados por la BD.

### 8. Seguridad y Certificado SSL (Certbot)

Finalizar el despliegue asegurando la conexión con HTTPS.

- Ejecutar Certbot para obtener el certificado gratuito de Let's Encrypt.

```bash
sudo certbot --nginx -d arteideas.com
```

- Reiniciar Nginx para aplicar los cambios: `sudo systemctl restart nginx`.

---

**Despliegue Concluido.**
La aplicación ahora debería ser accesible de forma segura a través del dominio configurado.
