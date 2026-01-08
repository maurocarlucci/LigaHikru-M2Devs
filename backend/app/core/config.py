from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4"
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME: str = "text-embedding-ada-002"
    AZURE_OPENAI_API_VERSION: str = "2024-06-01"
    
    # Azure AI Search
    AZURE_SEARCH_ENDPOINT: str
    AZURE_SEARCH_API_KEY: str
    AZURE_SEARCH_INDEX_NAME: str = "documentos-index"
    
    # Azure Blob Storage
    AZURE_STORAGE_CONNECTION_STRING: str
    AZURE_STORAGE_CONTAINER_NAME: str = "documentos"
    
    # Azure SQL Database (opcional, requerido para autenticación)
    AZURE_SQL_SERVER: Optional[str] = None
    AZURE_SQL_DATABASE: Optional[str] = None
    AZURE_SQL_USERNAME: Optional[str] = None
    AZURE_SQL_PASSWORD: Optional[str] = None
    AZURE_SQL_DRIVER: str = "{ODBC Driver 18 for SQL Server}"
    
    # Authentication
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    
    # Application
    APP_NAME: str = "LigaHikru - Documentos AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # CORS (para producción, separar múltiples orígenes con comas)
    CORS_ORIGINS: str = "*"  # En producción, usar: "https://tu-frontend.com,https://otro-dominio.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
