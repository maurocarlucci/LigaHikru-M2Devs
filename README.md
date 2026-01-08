Hikru Insight

Sistema de búsqueda y consulta de documentos internos usando Azure AI Services.

## 🎯 Problema Resuelto

Los equipos (soporte, RRHH, operaciones) pierden tiempo buscando respuestas en documentos internos. Este sistema permite:
- **Preguntar** y obtener respuestas con citas a documentos
- **Buscar** documentos y obtener fragmentos relevantes con links

## 🏗️ Arquitectura

### Servicios Azure Utilizados

1. **Azure OpenAI / Azure AI Foundry**
   - Chat completions (GPT-5.2-chat o compatible)
   - Embeddings (text-embedding-3-small o text-embedding-ada-002)

2. **Azure AI Search**
   - Índice vectorial para búsqueda semántica
   - Búsqueda híbrida (texto + vectorial)

3. **Azure Blob Storage**
   - Almacenamiento de documentos fuente
   - URLs para acceso directo

4. **Azure SQL Database**
   - Base de datos para usuarios y autenticación
   - Almacenamiento de metadata de documentos
   - Historial de preguntas y búsquedas

5. **Azure Functions** (Opcional)
   - Para automatizar ingestión/actualización del índice

## 📁 Estructura del Proyecto

```
LigaHikru/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py          # Configuración y settings
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   ├── schemas.py          # Modelos Pydantic
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── azure_openai_service.py
│   │   │   ├── azure_search_service.py
│   │   │   ├── azure_blob_service.py
│   │   │   ├── azure_sql_service.py
│   │   │   ├── auth_service.py
│   │   │   ├── document_processor.py
│   │   │   ├── rag_service.py
│   │   │   └── __init__.py
│   │   ├── routers/
│   │   │   ├── auth.py              # Endpoints: /signup, /login
│   │   │   ├── chat.py             # Endpoints: /ask, /search
│   │   │   ├── documents.py         # Endpoints: /upload, /list, /delete
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   ├── dependencies.py      # Dependencias de autenticación
│   │   ├── main.py                 # FastAPI app
│   │   └── __init__.py
│   ├── requirements.txt
│   ├── create_index.py      # Script para crear el índice en Azure AI Search
│   ├── create_admin.py      # Script para crear usuario administrador
│   ├── env.example
│   └── .env                  # Configuración (no versionado)
├── frontend/
│   └── react-app/                  # UI profesional en React
│       ├── src/
│       │   ├── components/         # Componentes React
│       │   │   ├── LoginView.jsx   # Vista de login/signup
│       │   │   ├── ChatView.jsx    # Vista de chat (Flujo 1)
│       │   │   ├── SearchView.jsx  # Vista de búsqueda (Flujo 2)
│       │   │   ├── UploadView.jsx  # Vista de subida (Flujo 3)
│       │   │   ├── Header.jsx
│       │   │   ├── TabNavigation.jsx
│       │   │   └── Spinner.jsx
│       │   ├── services/
│       │   │   └── api.js          # Capa de integración con API
│       │   ├── App.jsx
│       │   ├── main.jsx
│       │   └── index.css
│       ├── package.json
│       ├── vite.config.js
│       ├── tailwind.config.js
│       └── .env.example
└── README.md
```

## 🚀 Instalación y Configuración

### 1. Requisitos Previos

- Python 3.9+
- Node.js 18+ (para el frontend React)
- ODBC Driver 18 for SQL Server (para conectar a Azure SQL)
- Cuenta de Azure con:
  - Azure OpenAI (con deployments de chat y embeddings configurados)
  - Azure AI Search
  - Azure Blob Storage
  - Azure SQL Database (para autenticación y usuarios)

### 2. Configuración Backend

**Primero, activa el entorno virtual:**

En PowerShell:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
```

Si obtienes un error de política de ejecución, ejecuta primero:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

En CMD o Git Bash:
```bash
cd backend
.\venv\Scripts\activate
```

**Luego, instala las dependencias:**

```bash
pip install -r requirements.txt
```

Copiar `env.example` a `.env` y configurar las variables:

```bash
cp env.example .env
# Editar .env con tus credenciales de Azure
```

**📋 Las credenciales de Azure están en el documento entregado.** Copia las credenciales del documento a tu archivo `.env`.

**⚠️ IMPORTANTE:** El archivo `.env` contiene credenciales sensibles y **NO debe versionarse** en Git. El archivo está incluido en `.gitignore` para proteger tus credenciales.

**Nota:** Asegúrate de que el entorno virtual esté activado (verás `(venv)` en tu prompt) antes de ejecutar cualquier comando de Python o pip.

**Variables de entorno requeridas en `.env`:**
- Azure OpenAI (endpoint, API key, deployment names)
- Azure AI Search (endpoint, API key, index name)
- Azure Blob Storage (connection string, container name)
- Azure SQL Database (server, database, username, password) - para autenticación
- Authentication (JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES)

Ver `backend/env.example` para ver todas las variables necesarias.

### 3. Crear Usuario Administrador

**IMPORTANTE:** Antes de usar la aplicación, debes crear al menos un usuario administrador.

**Asegúrate de tener el entorno virtual activado** (verás `(venv)` en tu prompt), luego ejecuta:

```bash
cd backend
python create_admin.py
```

El script te pedirá:
- Email del administrador
- Username
- Contraseña (mínimo 6 caracteres, máximo 72)

**Nota:** Solo los administradores pueden subir y eliminar documentos. Los usuarios normales pueden ver documentos y hacer consultas.

### 4. Crear Índice en Azure AI Search

**IMPORTANTE:** Antes de usar la aplicación, debes crear el índice en Azure AI Search.

**Asegúrate de tener el entorno virtual activado** (verás `(venv)` en tu prompt), luego ejecuta:

```bash
cd backend
python create_index.py
```

Este script creará automáticamente el índice `documentos-index` con el esquema correcto.

**Esquema del índice:**

```json
{
  "name": "documentos-index",
  "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "key": true
    },
    {
      "name": "documentName",
      "type": "Edm.String",
      "searchable": true
    },
    {
      "name": "content",
      "type": "Edm.String",
      "searchable": true
    },
    {
      "name": "contentVector",
      "type": "Collection(Edm.Single)",
      "dimensions": 1536,
      "vectorSearchProfile": "default-vector-profile"
    },
    {
      "name": "chunkIndex",
      "type": "Edm.Int32"
    },
    {
      "name": "pageNumber",
      "type": "Edm.Int32",
      "filterable": true
    },
    {
      "name": "sourceUrl",
      "type": "Edm.String"
    }
  ],
  "vectorSearch": {
    "profiles": [
      {
        "name": "default-vector-profile",
        "algorithm": "default-algorithm"
      }
    ],
    "algorithms": [
      {
        "name": "default-algorithm",
        "kind": "hnsw",
        "parameters": {
          "m": 4,
          "efConstruction": 400,
          "efSearch": 500,
          "metric": "cosine"
        }
      }
    ]
  }
}
```

### 5. Ejecutar Backend

**Asegúrate de tener el entorno virtual activado** (verás `(venv)` en tu prompt):

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

La API estará disponible en: `http://localhost:8000`
Documentación Swagger: `http://localhost:8000/docs`

**Alternativa:** Puedes usar el script `start.bat` que activa el entorno virtual y ejecuta el servidor automáticamente:
```bash
cd backend
.\start.bat
```

### 6. Ejecutar Frontend

El frontend profesional está construido con React, Vite y TailwindCSS.

```bash
cd frontend/react-app

# Instalar dependencias
npm install

# Configurar URL del backend (opcional, por defecto usa localhost:8000)
cp .env.example .env
# Editar .env si el backend está en otra URL

# Iniciar servidor de desarrollo
npm run dev
```

La aplicación estará disponible en: `http://localhost:3000`

#### Características del Frontend React

- **Autenticación**: Sistema de login/signup con diseño moderno
- **Roles**: Administradores y usuarios con permisos diferenciados
- **Preguntar**: Chat con IA que responde basándose en tus documentos, con citas agrupadas por documento
- **Buscar**: Búsqueda semántica de fragmentos relevantes con scores de relevancia
- **Subir**: Drag & drop para subir documentos PDF, TXT o MD (solo administradores)

#### Build para Producción

```bash
npm run build
# Los archivos se generan en dist/
```

## 📡 API Endpoints

### Autenticación

- `POST /api/auth/signup` - Registro de nuevo usuario
  ```json
  {
    "email": "usuario@ejemplo.com",
    "username": "usuario123",
    "password": "contraseña123"
  }
  ```
  Retorna: `{ "access_token": "...", "token_type": "bearer", "user": {...} }`

- `POST /api/auth/login-json` - Login de usuario (JSON)
  ```json
  {
    "email": "usuario@ejemplo.com",
    "password": "contraseña123"
  }
  ```
  Retorna: `{ "access_token": "...", "token_type": "bearer", "user": {...} }`

- `POST /api/auth/login` - Login de usuario (OAuth2 form)
  - Usa `application/x-www-form-urlencoded`
  - Campos: `username` (email), `password`

**Nota:** Todos los endpoints protegidos requieren el header: `Authorization: Bearer <token>`

### Chat

- `POST /api/chat/ask` - Hacer una pregunta (público)
  ```json
  {
    "question": "¿Cuál es la política de vacaciones?",
    "max_results": 5,
    "temperature": 0.7
  }
  ```
  
  **Nota:** El parámetro `temperature` se acepta en la API pero algunos modelos (como gpt-5.2-chat) solo soportan el valor por defecto (1.0).

- `POST /api/chat/search` - Buscar documentos (público)
  ```json
  {
    "query": "política de vacaciones",
    "max_results": 10
  }
  ```

### Documentos

- `GET /api/documents/list` - Listar documentos (requiere autenticación)
  - Headers: `Authorization: Bearer <token>`
  - Disponible para: usuarios y administradores

- `POST /api/documents/upload` - Subir y procesar documento (solo administradores)
  - Headers: `Authorization: Bearer <token>`
  - Body: `multipart/form-data` con el archivo
  - Disponible para: solo administradores

- `DELETE /api/documents/{filename}` - Eliminar documento (solo administradores)
  - Headers: `Authorization: Bearer <token>`
  - Disponible para: solo administradores

## 🔄 Flujos de Trabajo

### Flujo 1: Preguntar

1. Usuario hace una pregunta
2. Sistema genera embedding de la pregunta
3. Búsqueda híbrida en Azure AI Search
4. Generación de respuesta con RAG usando el modelo de chat configurado
5. Retorna respuesta + citas a documentos

### Flujo 2: Buscar Documento

1. Usuario ingresa query de búsqueda
2. Sistema genera embedding del query
3. Búsqueda híbrida en Azure AI Search
4. Retorna fragmentos relevantes con links

### Ingestión de Documentos

1. Usuario sube documento (PDF/TXT/MD)
2. Documento se sube a Azure Blob Storage
3. Procesamiento: chunking del texto
4. Generación de embeddings para cada chunk
5. Indexación en Azure AI Search

## 🎨 Características

- ✅ **Sistema de autenticación completo**
  - Login y registro de usuarios
  - Tokens JWT para sesiones
  - Protección de rutas con roles
- ✅ **Sistema de roles**
  - Administradores: pueden subir/eliminar documentos
  - Usuarios: pueden ver documentos y hacer consultas
- ✅ Búsqueda semántica con embeddings
- ✅ Búsqueda híbrida (texto + vectorial)
- ✅ RAG (Retrieval Augmented Generation)
- ✅ Citas a documentos fuente con páginas agrupadas
- ✅ Frontend profesional en React con TailwindCSS
- ✅ Soporte para formato **bold** en respuestas de IA
- ✅ API REST con Swagger
- ✅ Soporte para PDF, TXT, MD
- ✅ Drag & drop para subir documentos
- ✅ Base de datos Azure SQL para usuarios y metadata

## 🔐 Autenticación y Roles

### Roles del Sistema

- **Administrador (admin)**
  - Puede subir documentos
  - Puede eliminar documentos
  - Puede ver todos los documentos
  - Ve la pestaña "Documentos" en el frontend

- **Usuario (user)**
  - Puede ver documentos
  - Puede hacer preguntas y búsquedas
  - No puede subir ni eliminar documentos
  - No ve la pestaña "Documentos" en el frontend

### Crear Usuarios

**Administrador:**
```bash
cd backend
python create_admin.py
```

**Usuario normal:**
- Se registran desde el frontend usando el formulario de signup
- Todos los usuarios nuevos tienen rol "user" por defecto

### Uso de Tokens

Después de hacer login, recibirás un token JWT. Inclúyelo en todas las requests protegidas:

```bash
Authorization: Bearer <tu-token-aqui>
```

Los tokens expiran después de 24 horas (configurable en `ACCESS_TOKEN_EXPIRE_MINUTES`).

## 🌐 Despliegue Público (Demo)

¿Quieres publicar tu proyecto para que otros puedan probarlo? **¡Es súper fácil!**

📖 **Lee la guía completa de despliegue en [DEPLOY.md](DEPLOY.md)**

### Opciones Recomendadas (Gratis para Demos):

1. **Render.com** ⭐ (MÁS FÁCIL)
   - Despliega backend y frontend en minutos
   - Gratis para demos
   - Auto-deploy desde GitHub
   - [Ver guía completa →](DEPLOY.md#-opción-recomendada-rendercom-más-fácil)

2. **Railway.app**
   - Similar a Render, muy fácil de usar
   - $5 de crédito gratis al mes
   - [Ver guía →](DEPLOY.md#-alternativa-railwayapp-también-muy-fácil)

3. **Vercel (Frontend) + Render (Backend)**
   - Lo mejor de ambos mundos
   - Vercel excelente para React
   - [Ver guía →](DEPLOY.md#-alternativa-vercel-frontend--render-backend)

### Pasos Rápidos (Render.com):

1. Sube tu código a GitHub
2. Ve a [render.com](https://render.com) y crea cuenta
3. **Backend**: "New Web Service" → Conecta repo → Configura Python
4. **Frontend**: "New Static Site" → Conecta repo → Configura Node.js
5. Agrega variables de entorno
6. ¡Listo! Tu app estará pública en minutos

**Nota**: Los servicios gratuitos pueden "dormirse" después de 15 min de inactividad. La primera petición puede tardar ~30 segundos.

## 🔧 Próximos Pasos (Opcional)

- [ ] Implementar Azure Functions para ingestión automática
- [ ] Mejorar chunking (overlap inteligente)
- [ ] Agregar más formatos de archivo
- [ ] Implementar cache de respuestas
- [ ] Agregar métricas y logging
- [x] Deploy a ambiente público (ver DEPLOY.md)
- [ ] Recuperación de contraseña
- [ ] Verificación de email

## 📝 Notas

### Documentos y Búsqueda

- Los documentos deben estar en español o el idioma configurado
- El tamaño de chunks es configurable (default: 1000 caracteres)
- **Modelos soportados:**
  - Chat: `gpt-5.2-chat`, `gpt-4`, `gpt-4o`, etc.
  - Embeddings: `text-embedding-3-small` (1536 dimensiones), `text-embedding-ada-002` (1536 dimensiones)
- **Limitaciones de gpt-5.2-chat:**
  - Requiere `max_completion_tokens` en lugar de `max_tokens`
  - Solo soporta `temperature=1.0` (valor por defecto)
- El índice debe crearse antes de subir documentos (usar `create_index.py`)
- Los nombres de archivo con caracteres especiales se normalizan automáticamente para los IDs del índice

### Autenticación

- Las contraseñas se hashean con bcrypt (límite de 72 caracteres)
- Los tokens JWT expiran después de 24 horas por defecto
- Cambia `JWT_SECRET_KEY` en producción por una clave segura
- La tabla `users` se crea automáticamente al iniciar el servidor
- El historial de preguntas y búsquedas se asocia con el `user_id` del token

## 🔒 Seguridad

### Recomendaciones para Producción

- ✅ Cambiar `JWT_SECRET_KEY` por una clave segura y aleatoria
- ✅ Configurar CORS para permitir solo dominios específicos
- ✅ Usar HTTPS en producción
- ✅ Limitar reglas de firewall de Azure SQL a IPs específicas
- ✅ Considerar usar Azure Key Vault para almacenar credenciales
- ✅ Implementar rate limiting
- ✅ Agregar logging estructurado
- ✅ Considerar Azure AD authentication para empresas

### Variables de Entorno Sensibles

Nunca subas a Git:
- `.env` (contiene todas las credenciales)
- `JWT_SECRET_KEY` (debe ser única y segura)
- Credenciales de Azure SQL
- API Keys de Azure

## 🤝 Contribuir

Este es un proyecto de demostración. Para producción, considerar:
- Validación de inputs más robusta
- Manejo de errores mejorado
- Rate limiting
- Logging estructurado
- Recuperación de contraseña
- Verificación de email
- Auditoría de acciones de administradores

## 📄 Licencia

Este proyecto es una demostración técnica.
