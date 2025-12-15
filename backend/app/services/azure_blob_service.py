from azure.storage.blob import BlobServiceClient
from typing import List, Optional
import io
from app.core.config import settings


class AzureBlobService:
    """Servicio para interactuar con Azure Blob Storage"""
    
    def __init__(self):
        self.blob_service_client = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME
        self._ensure_container_exists()
    
    def _ensure_container_exists(self):
        """Asegura que el contenedor existe"""
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            if not container_client.exists():
                container_client.create_container()
        except Exception as e:
            raise Exception(f"Error creando contenedor: {str(e)}")
    
    def upload_file(self, file_content: bytes, filename: str) -> str:
        """Sube un archivo al blob storage"""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=filename
            )
            blob_client.upload_blob(file_content, overwrite=True)
            return blob_client.url
        except Exception as e:
            raise Exception(f"Error subiendo archivo: {str(e)}")
    
    def download_file(self, filename: str) -> bytes:
        """Descarga un archivo del blob storage"""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=filename
            )
            return blob_client.download_blob().readall()
        except Exception as e:
            raise Exception(f"Error descargando archivo: {str(e)}")
    
    def list_files(self, prefix: Optional[str] = None) -> List[str]:
        """Lista archivos en el contenedor"""
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            blobs = container_client.list_blobs(name_starts_with=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            raise Exception(f"Error listando archivos: {str(e)}")
    
    def delete_file(self, filename: str):
        """Elimina un archivo del blob storage"""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=filename
            )
            blob_client.delete_blob()
        except Exception as e:
            raise Exception(f"Error eliminando archivo: {str(e)}")
    
    def get_file_url(self, filename: str) -> str:
        """Obtiene la URL de un archivo"""
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=filename
        )
        return blob_client.url
