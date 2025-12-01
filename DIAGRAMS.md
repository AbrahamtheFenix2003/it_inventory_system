# Diagramas del Sistema de Inventario IT

## 1. Diagrama de Arquitectura
Este diagrama muestra la estructura de microservicios contenerizados del sistema.

```mermaid
graph TD
    subgraph "Cliente"
        Browser[Navegador Web]
    end

    subgraph "Docker Host"
        subgraph "Frontend Container"
            Streamlit[Streamlit App\n(Puerto 8501)]
        end

        subgraph "Backend Network"
            Gateway[API Gateway\n(FastAPI - Puerto 8000)]
            
            subgraph "Microservicios"
                Prov[Providers Service]
                Equip[Equipment Service]
                Maint[Maintenance Service]
                Rep[Reports Service]
            end
            
            DB[(PostgreSQL Database\nPuerto 5432)]
        end
    end

    Browser -->|HTTP| Streamlit
    Streamlit -->|HTTP/REST| Gateway
    Gateway -->|Route /providers| Prov
    Gateway -->|Route /equipment| Equip
    Gateway -->|Route /maintenance| Maint
    Gateway -->|Route /reports| Rep

    Prov -->|SQL| DB
    Equip -->|SQL| DB
    Maint -->|SQL| DB
    Rep -->|SQL| DB
```

## 2. Diagrama de Flujo de Datos e Iteraciones

### Flujo de Datos General
Cómo viaja la información desde el usuario hasta la persistencia.

```mermaid
sequenceDiagram
    participant User as Usuario
    participant FE as Frontend (Streamlit)
    participant GW as API Gateway
    participant SVC as Microservicio (Ej. Equipment)
    participant DB as Base de Datos

    User->>FE: Ingresa datos (Ej. Nuevo Equipo)
    FE->>GW: POST /equipment (JSON)
    GW->>SVC: Forward Request
    SVC->>SVC: Validar Datos
    SVC->>DB: INSERT INTO equipment
    DB-->>SVC: Confirmación (ID generado)
    SVC-->>GW: 200 OK + JSON Objeto
    GW-->>FE: 200 OK + JSON Objeto
    FE-->>User: Muestra mensaje de éxito
```

### Iteraciones (Ciclo de Vida del Equipo)
Este diagrama de estado muestra las iteraciones o estados por los que pasa un equipo en el sistema.

```mermaid
stateDiagram-v2
    [*] --> Disponible: Compra/Registro
    
    Disponible --> Asignado: Asignar a Usuario/Ubicación
    Asignado --> Disponible: Devolución
    
    Asignado --> Mantenimiento: Reporte de Falla
    Disponible --> Mantenimiento: Mantenimiento Preventivo
    
    Mantenimiento --> Disponible: Reparación Exitosa
    Mantenimiento --> Baja: Reparación Fallida/Costosa
    
    Asignado --> Baja: Obsolescencia/Daño Irreparable
    Disponible --> Baja: Obsolescencia
    
    Baja --> [*]: Eliminación/Venta
```

## 3. Diagrama de Modelo de Datos (Entidad-Relación)

```mermaid
erDiagram
    PROVIDERS ||--o{ EQUIPMENT : supplies
    EQUIPMENT ||--o{ MAINTENANCE : undergoes
    EQUIPMENT ||--o{ EQUIPMENT_HISTORY : has

    PROVIDERS {
        int id PK
        string name
        string contact_name
        string email
        string phone
        string address
        timestamp created_at
    }

    EQUIPMENT {
        int id PK
        string name
        string serial_number UK
        string type
        string brand
        string model
        date purchase_date
        string status
        string location
        int provider_id FK
        timestamp created_at
    }

    MAINTENANCE {
        int id PK
        int equipment_id FK
        string type
        string description
        decimal cost
        date date
        string technician
        string status
        timestamp created_at
    }

    EQUIPMENT_HISTORY {
        int id PK
        int equipment_id FK
        string previous_location
        string new_location
        string previous_status
        string new_status
        timestamp changed_at
        string reason
    }
```
