import psycopg2
import uuid
from datetime import datetime
from src.database.repository.user_orm_repository import UserORMRepository
from src.helpers.qdrant_connection_helper import QdrantConnection
from src.utils.config import settings
from src.utils.constants import  TypeDatabase
from src.utils.logger.custom_logging import LoggerMixin

class FileProcessingVecDB(LoggerMixin):
    def __init__(self):
        super().__init__()
        self.qdrant_client = QdrantConnection()

    async def delete_document_by_file_name(self, file_name: str,
                        type_db: str = TypeDatabase.Qdrant.value):
        if not file_name:
            self.logger.error('event=delete-document-by-file-name '
                              'message="Delete document by file name Failed. '
                              f'error="file_name is None. Please check your input again." ')
        else:
            self.logger.info('event=delete-document-in-vector-database '
                         'message="Start delete ..."')
            # if type_db == TypeDatabase.Solr.value:
            #     await self.solr_client.delete_document_by_file_name(document_name=file_name, collection_name=settings.SOLR_COLLECTION_NAME)
            # elif type_db == TypeDatabase.Chroma.value:
            #     await self.chroma_client.delete_document_by_file_name(document_name=file_name, collection_name=settings.CHROMA_COLLECTION_NAME)
            if type_db == TypeDatabase.Qdrant.value:
                await self.qdrant_client.delete_document_by_file_name(document_name=file_name, collection_name=settings.QDRANT_COLLECTION_NAME)
    
    async def delete_document_by_batch_ids(self, document_ids: list[str],
                        type_db: str = TypeDatabase.Qdrant.value,
                        collection_name: str = settings.QDRANT_COLLECTION_NAME):
        
        if not document_ids:
            self.logger.error('event=delete-document-by-batch-ids '
                              'message="Delete document by batch ids Failed. '
                              f'error="document_ids is None. Please check your input again." ')
        else: 
            self.logger.info('event=delete-document-in-vector-database '
                         'message="Start delete ..."')
            # if type_db == TypeDatabase.Solr.value:
            #     await self.solr_client.delete_document_by_batch_ids(document_ids=document_ids, collection_name=settings.SOLR_COLLECTION_NAME)
            # elif type_db == TypeDatabase.Chroma.value:
            #     await self.chroma_client.delete_document_by_batch_ids(document_ids=document_ids, collection_name=settings.CHROMA_COLLECTION_NAME)
            if type_db == TypeDatabase.Qdrant.value:
                await self.qdrant_client.delete_document_by_batch_ids(document_ids=document_ids, collection_name=settings.QDRANT_COLLECTION_NAME)

class FileProcessingRepository(UserORMRepository):
    def create_file_records(self, file_name, extension, file_url, uploaded_by, size, sha256, source=''):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """INSERT INTO documents  
                     (id, created_at, extension, file_name, miniourl, rooturl, size, status, type, updated_at, created_by, token_number, sha256) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, true, NULL, NULL, %s, NULL, %s)"""
            id_ = str(uuid.uuid4())
            created_at = datetime.now()
            cursor.execute(sql, (id_, created_at, extension, file_name, file_url, source, size, uploaded_by, sha256))
            conn.commit()
            return id_
        except (Exception, psycopg2.Error) as error:
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()


    def check_duplicates(self, sha256, file_name):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """SELECT id FROM documents WHERE sha256 = %s AND file_name = %s"""
            cursor.execute(sql, (sha256, file_name))
            result = cursor.fetchone()
            return result is not None
        except (Exception, psycopg2.Error) as error:
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()

    
    def get_files_by_search_engine(self, key_word=None, extension=None, created_at=None, limit=10, offset=0):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            base_sql = """
                SELECT id, file_name, extension, size, created_by, miniourl
                FROM documents
                WHERE 1=1
            """
            count_sql = """
                SELECT COUNT(id)
                FROM documents
                WHERE 1=1
            """
            filters = ""
            if key_word is not None:
                filters += f" AND LOWER(file_name) LIKE LOWER(\'%{key_word}%\')"

            if extension is not None:
                filters += " AND extension LIKE '{}'".format(extension)
                # params.append(extension)

            if created_at is not None:
                filters += " AND DATE(created_at) = '{}'".format(created_at)
                # params.append(created_at)
            count_sql += filters
            
            base_sql += filters 
            base_sql += " LIMIT {} OFFSET {}".format(limit, offset)

            cursor.execute(count_sql)
            total_count = cursor.fetchone()[0]
            cursor.execute(base_sql)
            results = cursor.fetchall()
            files = [dict(zip(('id', 'file_name', 'extension', 'size', 'created_by', 'miniourl'), r)) for r in results]
            return {
                'total_count': total_count,
                'files': files
                }
        except (Exception, psycopg2.Error) as error:
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()

    
    def delete_document_by_batch_ids(self, document_ids: list[str]):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            ids_list = ', '.join(['%s'] * len(document_ids))
            sql = f"DELETE FROM documents WHERE id IN ({ids_list})"
            cursor.execute(sql, tuple(document_ids))
            conn.commit()
            return None
        except (Exception, psycopg2.Error) as error:
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()

    def delete_document_by_file_name(self, file_name):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """DELETE FROM documents WHERE file_name = %s"""
            cursor.execute(sql, (file_name,))
            conn.commit()
            return None
        except (Exception, psycopg2.Error) as error:
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()

    def get_document_by_id(self, document_id):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """SELECT file_name, rooturl, miniourl FROM documents WHERE id = %s limit 1"""
            cursor.execute(sql, (document_id,))
            result = cursor.fetchone()
            if result:
                return result[0], result[1], result[2]
            return None
        except (Exception, psycopg2.Error) as error:
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()

