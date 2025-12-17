# LigaHikru - Documentos AI

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

4. **Azure Functions** (Opcional)
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
│   │   │   ├── document_processor.py
│   │   │   ├── rag_service.py
│   │   │   └── __init__.py
│   │   ├── routers/
│   │   │   ├── chat.py             # Endpoints: /ask, /search
│   │   │   ├── documents.py         # Endpoints: /upload, /list, /delete
│   │   │   └── __init__.py
│   │   ├── main.py                 # FastAPI app
│   │   └── __init__.py
│   ├── requirements.txt
│   ├── create_index.py      # Script para crear el índice en Azure AI Search
│   ├── env.example
│   └── .env                  # Configuración (no versionado)
├── frontend/
│   └── react-app/                  # UI profesional en React
│       ├── src/
│       │   ├── components/         # Componentes React
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
- Cuenta de Azure con:
  - Azure OpenAI (con deployments de chat y embeddings configurados)
  - Azure AI Search
  - Azure Blob Storage

### 2. Configuración Backend

```bash
cd backend
pip install -r requirements.txt
```

Copiar `env.example` a `.env` y configurar las variables:

```bash
cp env.example .env
# Editar .env con tus credenciales de Azure
```

**⚠️ IMPORTANTE:** El archivo `.env` contiene credenciales sensibles y **NO debe versionarse** en Git. El archivo está incluido en `.gitignore` para proteger tus credenciales.

### 3. Crear Índice en Azure AI Search

**IMPORTANTE:** Antes de usar la aplicación, debes crear el índice en Azure AI Search.

Ejecuta el script de creación del índice:

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

### 4. Ejecutar Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

La API estará disponible en: `http://localhost:8000`
Documentación Swagger: `http://localhost:8000/docs`

### 5. Ejecutar Frontend

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

- **Preguntar**: Chat con IA que responde basándose en tus documentos, con citas agrupadas por documento
- **Buscar**: Búsqueda semántica de fragmentos relevantes con scores de relevancia
- **Subir**: Drag & drop para subir documentos PDF, TXT o MD

#### Build para Producción

```bash
npm run build
# Los archivos se generan en dist/
```

## 📡 API Endpoints

### Chat

- `POST /api/chat/ask` - Hacer una pregunta
  ```json
  {
    "question": "¿Cuál es la política de vacaciones?",
    "max_results": 5,
    "temperature": 0.7
  }
  ```
  
  **Nota:** El parámetro `temperature` se acepta en la API pero algunos modelos (como gpt-5.2-chat) solo soportan el valor por defecto (1.0).

- `POST /api/chat/search` - Buscar documentos
  ```json
  {
    "query": "política de vacaciones",
    "max_results": 10
  }
  ```

### Documentos

- `POST /api/documents/upload` - Subir y procesar documento
- `GET /api/documents/list` - Listar documentos
- `DELETE /api/documents/{filename}` - Eliminar documento

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

- ✅ Búsqueda semántica con embeddings
- ✅ Búsqueda híbrida (texto + vectorial)
- ✅ RAG (Retrieval Augmented Generation)
- ✅ Citas a documentos fuente con páginas agrupadas
- ✅ Frontend profesional en React con TailwindCSS
- ✅ Soporte para formato **bold** en respuestas de IA
- ✅ API REST con Swagger
- ✅ Soporte para PDF, TXT, MD
- ✅ Drag & drop para subir documentos

## 🔧 Próximos Pasos (Opcional)

- [ ] Implementar Azure Functions para ingestión automática
- [ ] Agregar autenticación/autorización
- [ ] Mejorar chunking (overlap inteligente)
- [ ] Agregar más formatos de archivo
- [ ] Implementar cache de respuestas
- [ ] Agregar métricas y logging
- [ ] Deploy a Azure App Service

## 📝 Notas

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

## 🤝 Contribuir

Este es un proyecto de demostración. Para producción, considerar:
- Validación de inputs más robusta
- Manejo de errores mejorado
- Rate limiting
- Autenticación
- Logging estructurado

## 📄 Licencia

Este proyecto es una demostración técnica.
