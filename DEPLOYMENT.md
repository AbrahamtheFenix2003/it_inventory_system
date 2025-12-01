# Guía de Despliegue - Sistema de Inventario IT

Esta guía detalla cómo desplegar la aplicación en un servidor Linux (VPS) usando Docker Compose.

## Requisitos Previos

1.  **Servidor VPS**: Una instancia en AWS EC2, DigitalOcean Droplet, Google Compute Engine, etc. (Ubuntu 20.04/22.04 recomendado).
2.  **Dominio (Opcional)**: Si deseas acceder por un nombre de dominio (ej. `inventario.tuempresa.com`).
3.  **Docker y Docker Compose**: Instalados en el servidor.

## Pasos de Instalación en el Servidor

### 1. Instalar Docker y Docker Compose
Conéctate a tu servidor vía SSH y ejecuta:

```bash
# Actualizar paquetes
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Instalar Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Transferir el Código
Puedes clonar tu repositorio git o copiar los archivos directamente.
Asegúrate de copiar:
- Carpetas: `database`, `frontend`, `gateway`, `services`
- Archivos: `docker-compose.yml`, `docker-compose.prod.yml`

### 3. Configurar Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto en el servidor:

```bash
nano .env
```

Contenido del archivo `.env`:
```env
DB_PASSWORD=UnaContraseñaMuySegura123
SERVER_IP=tu_ip_publica_o_dominio
```

### 4. Iniciar la Aplicación
Ejecuta el siguiente comando para construir e iniciar los contenedores en modo producción:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Esto aplicará la configuración base y sobrescribirá con la configuración de producción (reinicios automáticos, sin volúmenes de desarrollo, contraseñas seguras).

### 5. Verificar
Accede a `http://tu_ip_publica:8501` para ver la aplicación.

## Consideraciones de Seguridad Adicionales (Recomendado)

### Proxy Inverso con Nginx y SSL (HTTPS)
Para producción real, no deberías exponer los puertos 8000 y 8501 directamente y deberías usar HTTPS.

1.  Instala Nginx: `sudo apt install nginx`
2.  Configura un bloque de servidor para redirigir el tráfico del puerto 80 al 8501 (frontend) y /api al 8000.
3.  Usa **Certbot** para obtener certificados SSL gratuitos de Let's Encrypt.

### Backups de Base de Datos
Configura un cron job para respaldar la base de datos periódicamente:

```bash
# Ejemplo de backup diario
docker exec it_inventory_db pg_dump -U admin it_inventory > /path/to/backups/backup_$(date +%F).sql
```
