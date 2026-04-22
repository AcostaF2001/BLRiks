# Assessment Técnico Full Stack / DevOps

## Descripción general

Este proyecto implementa una solución web para el procesamiento de archivos Excel bajo un flujo multi-organización, con autenticación, reglas de negocio configurables, procesamiento asíncrono y persistencia en múltiples motores de base de datos.

La solución fue construida con:

- **Django** como framework principal del backend
- **PostgreSQL** para usuarios, organizaciones, archivos cargados, reglas y trazabilidad
- **MongoDB Atlas** para almacenar resultados procesados por versión
- **Redis** como broker y backend de resultados para Celery
- **Celery** para el procesamiento asíncrono
- **Docker Compose** para levantar el entorno local
- **Swagger / OpenAPI** para documentación de endpoints API

---

## Funcionalidades implementadas

### 1. Autenticación y contexto de usuario

- Login con el sistema nativo de Django
- Registro de usuarios desde interfaz web
- Asociación de usuarios a organizaciones
- Tipos de usuario funcionales:
  - `ADMIN_ORG`
  - `ANALYST`
- Gestión de usuarios y organizaciones desde interfaz
- Restricción de datos por organización

### 2. Carga de archivos Excel

- Carga de archivos `.xlsx`
- Registro de archivos en PostgreSQL
- Asociación automática con usuario y organización
- Estados del proceso:
  - `PENDING`
  - `PROCESSING`
  - `FINISHED`
  - `ERROR`

### 3. Procesamiento asíncrono

- El procesamiento se ejecuta en segundo plano con Celery
- El worker:
  - lee el Excel
  - valida encabezados
  - limpia datos
  - aplica reglas dinámicas
  - guarda resultados en MongoDB
  - actualiza estado y métricas en PostgreSQL

### 4. Reglas dinámicas

- Reglas configurables por organización
- Operaciones soportadas:
  - `SUM`
  - `SUBTRACT`
  - `MEAN`
- Solo puede existir una regla activa por organización

### 5. Reprocesamiento y versionamiento

- Un archivo no se vuelve a subir para reprocesarse
- Cada reproceso crea una nueva **versión de ejecución**
- Se mantiene historial de versiones
- Los resultados se guardan en MongoDB asociados a:
  - archivo
  - ejecución
  - versión
- Se evita duplicidad entre ejecuciones

### 6. Consulta de resultados

- Se pueden ver los resultados por archivo
- Se pueden consultar resultados por versión
- Se puede navegar el historial de ejecuciones

### 7. Filtros y paginación

#### Usuarios
- filtro por nombre
- filtro por tipo de usuario
- filtro por correo
- paginación
- búsqueda ignorando mayúsculas/minúsculas y acentos

#### Archivos
- filtro por nombre de archivo
- filtro por nombre de usuario
- paginación
- búsqueda ignorando mayúsculas/minúsculas y acentos

### 8. Documentación API

- Swagger UI protegido por login
- OpenAPI generado con `drf-spectacular`
- Endpoints documentados para:
  - accounts
  - uploads
  - rules
  - results

---

## Arquitectura general

### PostgreSQL
Se utiliza para almacenar información estructurada del sistema:

- usuarios
- organizaciones
- archivos cargados
- reglas de procesamiento
- historial de ejecuciones

### MongoDB Atlas
Se utiliza para almacenar resultados procesados por fila y por versión:

- datos originales
- datos transformados
- regla aplicada
- metadata del procesamiento

### Redis
Se utiliza como:

- broker de Celery
- backend de resultados de Celery

### Celery
Se utiliza para:

- desencolar tareas de procesamiento
- ejecutar el procesamiento fuera del request HTTP
- actualizar estados en segundo plano

---

## Estructura del proyecto

```text
BLRiks/
├── docker-compose.yml
├── .env
├── Backend/
│   ├── Dockerfile
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── celery.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── settings/
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── local.py
│   │       └── production.py
│   ├── apps/
│   │   ├── core/
│   │   ├── accounts/
│   │   ├── uploads/
│   │   ├── rules/
│   │   ├── PROCESSING/
│   │   ├── results/
│   │   └── audit/
│   └── templates/
└── Frontend/
```

---

## Requisitos previos

Antes de iniciar, debes tener instalado:

- **Docker Desktop** o Docker Engine + Docker Compose
- **Git**
- Opcional: **DBeaver** para inspeccionar PostgreSQL
- Opcional: acceso a **MongoDB Atlas**

---

## Variables de entorno

Archivo: `.env` en la raíz del proyecto.

Ejemplo:

```env
# =========================
# DJANGO
# =========================
DJANGO_SECRET_KEY=django-insecure-change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# =========================
# POSTGRES
# =========================
POSTGRES_DB=assessment_db
POSTGRES_USER=Felipe2001
POSTGRES_PASSWORD=Felipe2001
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# =========================
# MONGODB ATLAS
# =========================
MONGO_DB=assessment_results
MONGO_URI=mongodb+srv://USER:PASSWORD@cluster.mongodb.net/assessment_results?retryWrites=true&w=majority

# =========================
# REDIS
# =========================
REDIS_HOST=redis
REDIS_PORT=6379

# =========================
# CELERY
# =========================
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# =========================
# APP
# =========================
APP_ENV=local
```

---

## Instalación y arranque del proyecto

## Opción recomendada: Docker Compose

### 1. Ubicarse en la raíz del proyecto

```bash
cd BLRiks
```

### 2. Construir y levantar servicios

```bash
docker compose up --build -d
```

Esto levanta:

- `postgres`
- `redis`
- `web` (Django)
- `worker` (Celery)

### 3. Verificar contenedores

```bash
docker compose ps
```

### 4. Aplicar migraciones

```bash
docker compose exec web python manage.py migrate
```

### 5. Crear superusuario

```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Acceder a la aplicación

```text
http://127.0.0.1:8000/
```

Comportamiento:

- si no hay sesión iniciada, redirige a `/login/`
- si ya hay sesión iniciada, redirige a `/uploads/`

---

## Arranque de servicios individualmente

### Levantar entorno completo

```bash
docker compose up --build
```

### Levantar en segundo plano

```bash
docker compose up --build -d
```

### Detener servicios

```bash
docker compose down
```

### Detener y eliminar volúmenes

```bash
docker compose down -v
```

---

## Logs y monitoreo

### Logs generales

```bash
docker compose logs
```

### Logs del backend Django

```bash
docker compose logs -f web
```

### Logs del worker Celery

```bash
docker compose logs -f worker
```

### Logs de PostgreSQL

```bash
docker compose logs -f postgres
```

### Logs de Redis

```bash
docker compose logs -f redis
```

### Ver solo las últimas líneas

```bash
docker compose logs --tail=100 worker
```

---

## Comandos útiles de administración

### Crear migraciones

```bash
docker compose exec web python manage.py makemigrations
```

### Crear migraciones de una app específica

```bash
docker compose exec web python manage.py makemigrations uploads
docker compose exec web python manage.py makemigrations rules
docker compose exec web python manage.py makemigrations accounts
```

### Aplicar migraciones

```bash
docker compose exec web python manage.py migrate
```

### Abrir shell de Django

```bash
docker compose exec web python manage.py shell
```

### Revisar migraciones aplicadas

```bash
docker compose exec web python manage.py showmigrations
```

### Ejecutar validaciones de proyecto

```bash
docker compose exec web python manage.py check
```

### Abrir bash dentro del contenedor web

```bash
docker compose exec web bash
```

### Abrir bash dentro del worker

```bash
docker compose exec worker bash
```

---

## Accesos principales

### Aplicación web

- Inicio: `http://127.0.0.1:8000/`
- Login: `http://127.0.0.1:8000/login/`
- Registro: `http://127.0.0.1:8000/accounts/register/`
- Archivos: `http://127.0.0.1:8000/uploads/`
- Usuarios: `http://127.0.0.1:8000/accounts/users/`
- Organizaciones: `http://127.0.0.1:8000/accounts/organizations/`
- Reglas: `http://127.0.0.1:8000/rules/`
- Swagger: `http://127.0.0.1:8000/api/docs/`

### Admin Django

- `http://127.0.0.1:8000/admin/`

---

## Roles y permisos

### SUPERUSER
Tiene acceso global:

- todas las organizaciones
- todos los usuarios
- todas las reglas
- administración completa del sistema

### ADMIN_ORG
Tiene acceso restringido a su organización:

- puede ver usuarios de su organización
- puede gestionar usuarios dentro de su organización
- puede gestionar reglas de su organización
- no puede administrar organizaciones globalmente

### ANALYST
Tiene acceso operativo:

- carga de archivos
- consulta de resultados
- reprocesamiento
- sin acceso a módulos administrativos

---

## Flujo funcional del sistema

### 1. Registro o login
El usuario puede:

- crear una cuenta
- elegir tipo de usuario funcional
- crear una organización nueva o unirse a una existente

### 2. Carga de archivo
Desde `/uploads/new/` el usuario sube un archivo `.xlsx`.

El sistema:

- guarda el archivo en disco
- crea un registro `UploadedFile`
- crea una ejecución inicial `PROCESSING` versión 1
- envía la tarea a Celery

### 3. Procesamiento asíncrono
El worker:

- lee el archivo Excel
- valida encabezados
- limpia datos
- identifica la regla activa de la organización
- aplica la regla
- guarda resultados versionados en MongoDB
- actualiza el estado en PostgreSQL

### 4. Reprocesamiento
Desde la lista de archivos, el botón **Reprocesar**:

- no vuelve a subir el archivo
- crea una nueva ejecución/version
- relanza el procesamiento sobre el mismo archivo físico

### 5. Consulta de resultados
Desde **Ver resultados** se puede:

- ver la versión actual
- navegar el historial de versiones
- consultar resultados por ejecución/version

---

## Estructura esperada del Excel

Columnas esperadas por el sistema:

- `identificador`
- `nombre`
- `valor_base`
- `categoria`
- `fecha`

El procesamiento incluye normalización de encabezados, por lo que también tolera variantes razonables en mayúsculas, tildes o separadores.

---

## Reglas de procesamiento

Las reglas se configuran por organización y pueden ser:

### SUM
```text
Resultado = Valor_base + adjustment_value
```

### SUBTRACT
```text
Resultado = Valor_base - adjustment_value
```

### MEAN
```text
Resultado = media aritmética de la columna Valor_base
```

### Restricción importante
Solo puede existir **una regla activa por organización**.

---

## Versionamiento y reproceso

Cada archivo puede tener múltiples ejecuciones.

### Modelo conceptual

- `UploadedFile` = archivo original
- `PROCESSING` = cada ejecución/version

### Ejemplo

- Carga inicial → versión 1
- Primer reproceso → versión 2
- Segundo reproceso → versión 3

### Cómo se evita la duplicidad

En MongoDB los resultados se guardan con:

- `uploaded_file_id`
- `execution_id`
- `execution_version`

Antes de insertar resultados de una ejecución, el sistema elimina solo resultados previos de esa misma ejecución/version. Esto evita duplicados sin borrar el historial anterior.

---

## Swagger / API

La documentación Swagger está disponible en:

```text
http://127.0.0.1:8000/api/docs/
```

Solo usuarios autenticados pueden acceder.

### Endpoints principales

#### Accounts
- `GET /api/accounts/me/`
- `POST /api/accounts/register/`
- `GET /api/accounts/users/`
- `GET /api/accounts/organizations/`
- `PATCH /api/accounts/users/{id}/assign-organization/`

#### Uploads
- `GET /api/uploads/files/`
- `GET /api/uploads/files/{id}/executions/`
- `POST /api/uploads/files/{id}/reprocess/`

#### Results
- `GET /api/results/files/{id}/results/`
- `GET /api/results/files/{id}/results/?version=2`

#### Rules
- `GET /api/rules/rules/`

---

## Conexión a PostgreSQL desde DBeaver

Con la configuración actual del proyecto, si PostgreSQL está expuesto por Docker en el puerto `5433`, la conexión típica sería:

```text
Host: localhost
Port: 5433
Database: assessment_db
Username: Felipe2001
Password: Felipe2001
```

> Si cambias puertos o credenciales en `.env`, debes ajustar estos valores.

---

## Solución de problemas comunes

### 1. El worker no arranca
Revisar logs:

```bash
docker compose logs -f worker
```

Verificar que todas las dependencias estén en `Backend/requirements.txt` y reconstruir:

```bash
docker compose down
docker compose up --build -d
```

### 2. El archivo queda en `PENDING`
Verificar:

- que Redis esté arriba
- que el worker esté arriba
- que la task llegue al worker

Comandos:

```bash
docker compose ps
docker compose logs -f worker
docker compose logs -f web
```

### 3. Error por columnas faltantes en Excel
Verificar encabezados del archivo. El sistema espera columnas equivalentes a:

- identificador
- nombre
- valor_base
- categoria
- fecha

### 4. Error de paquetes faltantes en worker
Si aparece algo como:

```text
ModuleNotFoundError: No module named 'drf_spectacular'
```

reconstruir imágenes:

```bash
docker compose down
docker compose up --build -d
```

### 5. El filtro no ignora acentos
Verificar que la extensión `unaccent` esté habilitada y que la migración haya corrido correctamente:

```bash
docker compose exec web python manage.py migrate
```

---

## Comandos frecuentes de desarrollo

### Reiniciar solo backend web

```bash
docker compose restart web
```

### Reiniciar solo worker

```bash
docker compose restart worker
```

### Reconstruir contenedores

```bash
docker compose up --build -d
```

### Eliminar todo y empezar limpio

```bash
docker compose down -v
docker compose up --build -d
```

---

## Consideraciones técnicas

- El proyecto está diseñado para entorno local con Docker Compose
- MongoDB se usa como almacenamiento documental para resultados
- PostgreSQL se usa como base transaccional principal
- Redis + Celery permiten desacoplar el procesamiento del request HTTP
- El versionamiento asegura trazabilidad y reproceso controlado
- Swagger permite inspeccionar la API de manera documentada

---

## Mejoras futuras sugeridas

- interfaz frontend dedicada en React
- filtros adicionales por estado y fecha
- exportación de resultados
- creación de usuarios desde `ADMIN_ORG`
- mejor sistema de permisos por módulo
- dashboard con métricas por organización
- pruebas automáticas unitarias e integración
- despliegue productivo con Gunicorn/Nginx

---

## Estado actual del proyecto

El proyecto ya permite:

- autenticación
- registro de usuarios
- gestión de organizaciones
- gestión de usuarios
- carga de archivos Excel
- reglas dinámicas por organización
- procesamiento asíncrono
- reproceso versionado
- consulta de resultados por versión
- filtros y paginación
- documentación Swagger protegida por login

---

## Autor

Proyecto desarrollado como solución para assessment técnico Full Stack / DevOps.
