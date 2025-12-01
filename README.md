# Sistema de Gestión de Inventario TI

Este proyecto es una aplicación web basada en microservicios para la gestión de inventario de TI.

## Arquitectura

- **Frontend**: Streamlit
- **Backend**: FastAPI (Microservicios)
- **Base de Datos**: PostgreSQL
- **Gateway**: FastAPI

## Servicios

1. **Providers Service**: Gestión de proveedores.
2. **Equipment Service**: Gestión de equipos.
3. **Maintenance Service**: Gestión de mantenimientos.
4. **Reports Service**: Estadísticas y reportes.

## Cómo ejecutar

1. Asegúrate de tener Docker y Docker Compose instalados.
2. Ejecuta el siguiente comando en la raíz del proyecto:

```bash
docker-compose up --build
```

3. Accede a la aplicación en `http://localhost:8501`.
4. La API Gateway está disponible en `http://localhost:8000`.

## Estructura de Directorios

- `database/`: Scripts de inicialización de la base de datos.
- `frontend/`: Código de la aplicación Streamlit.
- `gateway/`: Código del API Gateway.
- `services/`: Código de los microservicios.
