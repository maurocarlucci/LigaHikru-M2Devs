"""
Script para crear el índice en Azure AI Search.
Ejecutar una vez antes de usar la aplicación.
"""
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
    SearchFieldDataType
)
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "documentos-index")

def create_index():
    """Crea el índice en Azure AI Search"""
    client = SearchIndexClient(
        endpoint=SEARCH_ENDPOINT,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    # Configuración de búsqueda vectorial
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="default-algorithm",
                kind="hnsw",
                parameters={
                    "m": 4,
                    "efConstruction": 400,
                    "efSearch": 500,
                    "metric": "cosine"
                }
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="default-vector-profile",
                algorithm_configuration_name="default-algorithm"
            )
        ]
    )
    
    # Definir campos del índice
    # Para campos vectoriales, usar SearchField con vector_search_dimensions y vector_search_profile_name
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="documentName", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchField(
            name="contentVector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            vector_search_dimensions=1536,  # Dimensiones para text-embedding-ada-002
            vector_search_profile_name="default-vector-profile"
        ),
        SimpleField(name="chunkIndex", type=SearchFieldDataType.Int32),
        SimpleField(name="pageNumber", type=SearchFieldDataType.Int32, filterable=True),
        SimpleField(name="sourceUrl", type=SearchFieldDataType.String),
    ]
    
    # Crear índice
    index = SearchIndex(
        name=INDEX_NAME,
        fields=fields,
        vector_search=vector_search
    )
    
    try:
        result = client.create_or_update_index(index)
        print(f"✅ Índice '{INDEX_NAME}' creado/actualizado exitosamente")
        print(f"   Nombre: {result.name}")
        return result
    except Exception as e:
        print(f"❌ Error creando índice: {str(e)}")
        raise

if __name__ == "__main__":
    print(f"Creando índice '{INDEX_NAME}' en Azure AI Search...")
    create_index()
