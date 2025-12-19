from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import List, Optional, Dict
from app.core.config import settings
import urllib.parse


class AzureSQLService:
    """Servicio para interactuar con Azure SQL Database"""
    
    def __init__(self):
        if not all([settings.AZURE_SQL_SERVER, settings.AZURE_SQL_DATABASE, 
                   settings.AZURE_SQL_USERNAME, settings.AZURE_SQL_PASSWORD]):
            self.engine = None
            self.Session = None
            return
        
        # Construir connection string
        params = urllib.parse.quote_plus(
            f"Driver={settings.AZURE_SQL_DRIVER};"
            f"Server=tcp:{settings.AZURE_SQL_SERVER},1433;"
            f"Database={settings.AZURE_SQL_DATABASE};"
            f"Uid={settings.AZURE_SQL_USERNAME};"
            f"Pwd={settings.AZURE_SQL_PASSWORD};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"Connection Timeout=30;"
        )
        
        connection_string = f"mssql+pyodbc:///?odbc_connect={params}"
        
        try:
            self.engine = create_engine(connection_string, pool_pre_ping=True)
            self.Session = sessionmaker(bind=self.engine)
            self._create_tables()
        except Exception as e:
            raise Exception(f"Error conectando a SQL: {str(e)}")
    
    def _create_tables(self):
        """Crea las tablas necesarias si no existen"""
        if not self.engine:
            return
        
        create_tables_sql = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'users')
        CREATE TABLE users (
            id INT PRIMARY KEY IDENTITY(1,1),
            email NVARCHAR(255) NOT NULL UNIQUE,
            username NVARCHAR(100) NOT NULL UNIQUE,
            hashed_password NVARCHAR(255) NOT NULL,
            role NVARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'user')),
            created_at DATETIME2 DEFAULT GETDATE(),
            is_active BIT DEFAULT 1
        );
        
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'documents')
        CREATE TABLE documents (
            id INT PRIMARY KEY IDENTITY(1,1),
            filename NVARCHAR(255) NOT NULL,
            blob_url NVARCHAR(500),
            file_size BIGINT,
            upload_date DATETIME2 DEFAULT GETDATE(),
            chunks_count INT DEFAULT 0,
            status NVARCHAR(50) DEFAULT 'processed'
        );
        
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'question_history')
        CREATE TABLE question_history (
            id INT PRIMARY KEY IDENTITY(1,1),
            question NVARCHAR(MAX) NOT NULL,
            answer NVARCHAR(MAX),
            created_at DATETIME2 DEFAULT GETDATE(),
            user_id INT,
            response_time_ms INT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'search_history')
        CREATE TABLE search_history (
            id INT PRIMARY KEY IDENTITY(1,1),
            query NVARCHAR(MAX) NOT NULL,
            results_count INT,
            created_at DATETIME2 DEFAULT GETDATE(),
            user_id INT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(create_tables_sql))
                conn.commit()
        except Exception as e:
            print(f"Advertencia: Error creando tablas SQL: {str(e)}")
    
    def save_document_metadata(self, filename: str, blob_url: str, file_size: int, chunks_count: int):
        """Guarda metadata de un documento"""
        if not self.Session:
            return
        
        try:
            session = self.Session()
            session.execute(
                text("""
                    INSERT INTO documents (filename, blob_url, file_size, chunks_count, status)
                    VALUES (:filename, :blob_url, :file_size, :chunks_count, 'processed')
                """),
                {
                    "filename": filename,
                    "blob_url": blob_url,
                    "file_size": file_size,
                    "chunks_count": chunks_count
                }
            )
            session.commit()
            session.close()
        except Exception as e:
            print(f"Error guardando metadata: {str(e)}")
    
    def save_question(self, question: str, answer: str, response_time_ms: int = None, user_id: str = None):
        """Guarda historial de preguntas"""
        if not self.Session:
            return
        
        try:
            session = self.Session()
            session.execute(
                text("""
                    INSERT INTO question_history (question, answer, response_time_ms, user_id)
                    VALUES (:question, :answer, :response_time_ms, :user_id)
                """),
                {
                    "question": question,
                    "answer": answer,
                    "response_time_ms": response_time_ms,
                    "user_id": user_id
                }
            )
            session.commit()
            session.close()
        except Exception as e:
            print(f"Error guardando pregunta: {str(e)}")
    
    def save_search(self, query: str, results_count: int, user_id: str = None):
        """Guarda historial de búsquedas"""
        if not self.Session:
            return
        
        try:
            session = self.Session()
            session.execute(
                text("""
                    INSERT INTO search_history (query, results_count, user_id)
                    VALUES (:query, :results_count, :user_id)
                """),
                {
                    "query": query,
                    "results_count": results_count,
                    "user_id": user_id
                }
            )
            session.commit()
            session.close()
        except Exception as e:
            print(f"Error guardando búsqueda: {str(e)}")
    
    def get_documents_list(self) -> List[Dict]:
        """Obtiene lista de documentos con metadata"""
        if not self.Session:
            return []
        
        try:
            session = self.Session()
            result = session.execute(
                text("SELECT filename, blob_url, file_size, upload_date, chunks_count FROM documents ORDER BY upload_date DESC")
            )
            documents = []
            for row in result:
                documents.append({
                    "filename": row[0],
                    "blob_url": row[1],
                    "file_size": row[2],
                    "upload_date": str(row[3]) if row[3] else None,
                    "chunks_count": row[4]
                })
            session.close()
            return documents
        except Exception as e:
            print(f"Error obteniendo documentos: {str(e)}")
            return []
    
    def get_question_history(self, limit: int = 10) -> List[Dict]:
        """Obtiene historial de preguntas"""
        if not self.Session:
            return []
        
        try:
            session = self.Session()
            result = session.execute(
                text("SELECT TOP :limit question, answer, created_at FROM question_history ORDER BY created_at DESC"),
                {"limit": limit}
            )
            history = []
            for row in result:
                history.append({
                    "question": row[0],
                    "answer": row[1][:200] + "..." if row[1] and len(row[1]) > 200 else row[1],
                    "created_at": str(row[2]) if row[2] else None
                })
            session.close()
            return history
        except Exception as e:
            print(f"Error obteniendo historial: {str(e)}")
            return []
    
    # Authentication methods
    def create_user(self, email: str, username: str, hashed_password: str, role: str = "user") -> Optional[int]:
        """Crea un nuevo usuario y retorna su ID"""
        if not self.Session:
            return None
        
        try:
            session = self.Session()
            result = session.execute(
                text("""
                    INSERT INTO users (email, username, hashed_password, role)
                    OUTPUT INSERTED.id
                    VALUES (:email, :username, :hashed_password, :role)
                """),
                {
                    "email": email,
                    "username": username,
                    "hashed_password": hashed_password,
                    "role": role
                }
            )
            user_id = result.scalar()
            session.commit()
            session.close()
            return user_id
        except Exception as e:
            print(f"Error creando usuario: {str(e)}")
            session.rollback()
            session.close()
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Obtiene un usuario por email"""
        if not self.Session:
            return None
        
        try:
            session = self.Session()
            result = session.execute(
                text("SELECT id, email, username, hashed_password, role, created_at, is_active FROM users WHERE email = :email"),
                {"email": email}
            )
            row = result.fetchone()
            session.close()
            
            if row:
                return {
                    "id": row[0],
                    "email": row[1],
                    "username": row[2],
                    "hashed_password": row[3],
                    "role": row[4],
                    "created_at": row[5],
                    "is_active": bool(row[6]) if row[6] is not None else True
                }
            return None
        except Exception as e:
            print(f"Error obteniendo usuario: {str(e)}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Obtiene un usuario por ID"""
        if not self.Session:
            return None
        
        try:
            session = self.Session()
            result = session.execute(
                text("SELECT id, email, username, role, created_at, is_active FROM users WHERE id = :user_id"),
                {"user_id": user_id}
            )
            row = result.fetchone()
            session.close()
            
            if row:
                return {
                    "id": row[0],
                    "email": row[1],
                    "username": row[2],
                    "role": row[3],
                    "created_at": row[4],
                    "is_active": bool(row[5]) if row[5] is not None else True
                }
            return None
        except Exception as e:
            print(f"Error obteniendo usuario: {str(e)}")
            return None
    
    def email_exists(self, email: str) -> bool:
        """Verifica si un email ya existe"""
        if not self.Session:
            return False
        
        try:
            session = self.Session()
            result = session.execute(
                text("SELECT COUNT(*) FROM users WHERE email = :email"),
                {"email": email}
            )
            count = result.scalar()
            session.close()
            return count > 0
        except Exception as e:
            print(f"Error verificando email: {str(e)}")
            return False
    
    def username_exists(self, username: str) -> bool:
        """Verifica si un username ya existe"""
        if not self.Session:
            return False
        
        try:
            session = self.Session()
            result = session.execute(
                text("SELECT COUNT(*) FROM users WHERE username = :username"),
                {"username": username}
            )
            count = result.scalar()
            session.close()
            return count > 0
        except Exception as e:
            print(f"Error verificando username: {str(e)}")
            return False
    
    def create_admin_user(self, email: str, username: str, password: str) -> Optional[int]:
        """Crea un usuario administrador (solo para setup inicial)"""
        from app.services.auth_service import get_password_hash
        return self.create_user(email, username, get_password_hash(password), role="admin")
