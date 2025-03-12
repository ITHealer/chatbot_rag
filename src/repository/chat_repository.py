import uuid
import psycopg2
from datetime import datetime
import logging

from src.repository.abstr_repository import Repository
from src.utils.constants import MessageType
from src.utils.utils import extension_mapping


class ChatRepository(Repository):

    def __init__(self):
        super().__init__()
        from src.repository.file_repository import FileProcessingRepository
        self._data_reprocessing_repository = FileProcessingRepository()

    # def is_exist_session(self, session_id) -> bool:
    #     conn = self.create_connection()
    #     cursor = conn.cursor()
    #     try:
    #         sql = """SELECT * FROM chat_sessions WHERE id = %s"""
    #         cursor.execute(sql, (session_id,))
    #         result = cursor.fetchone()
    #         if result:
    #             return True
    #         return False
    #     except (Exception, psycopg2.Error) as error:
    #         logging.error(error)
    #         raise ValueError(error)
    #     finally:
    #         if conn:
    #             cursor.close()
    #             conn.close()
    def is_exist_session(self, session_id) -> bool:
        """
        Check if a chat session exists
        
        Args:
            session_id: The ID of the session to check
            
        Returns:
            bool: True if the session exists, False otherwise
        """
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """SELECT id FROM chat_sessions WHERE id = %s"""
            cursor.execute(sql, (session_id,))
            result = cursor.fetchone()
            if result:
                return True
            return False
        except (Exception, psycopg2.Error) as error:
            logging.error(error)
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()

    def save_user_question(self, session_id, created_at, created_by, content):
        if not self.is_exist_session(session_id):
            logging.info("Chat session not exist!")
            raise ValueError("This is a custom error message")

        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """INSERT INTO messages 
                     (id, created_at, created_by, updated_at, updated_by, content, type, question_id, session_id, sender_role, response_time) 
                     VALUES (%s, %s, %s, NULL, NULL, %s, %s, NULL, %s, %s, NULL)"""

            # Generate timestamp for created_at and updated_at
            timestamp = datetime.now()

            # Execute SQL statement
            message_id = str(uuid.uuid4())
            cursor.execute(sql, (
                message_id, created_at, created_by, content, MessageType.QUESTION, session_id, 'user'))

            # Commit the transaction
            conn.commit()
            return message_id
        except (Exception, psycopg2.Error) as error:
            logging.error(error)
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()

    def save_assistant_response(self, session_id, created_at, question_id, content, response_time):
        if not self.is_exist_session(session_id):
            logging.error("Chat session not exist!")
            raise ValueError("This is a custom error message")

        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """INSERT INTO public.messages 
                     (id, created_at, created_by, updated_at, updated_by, content, type, question_id, session_id, sender_role, response_time) 
                     VALUES (%s, %s, NULL, NULL, NULL, %s, %s, %s, %s, %s, %s)"""

            # Execute SQL statement
            message_id = str(uuid.uuid4())
            cursor.execute(sql, (
                message_id, created_at, content, MessageType.ANSWER, question_id, session_id, 'assistant',
                response_time))

            # Commit the transaction
            conn.commit()
            return message_id
        except (Exception, psycopg2.Error) as error:
            logging.error(error)
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()

    def update_assistant_response(self, updated_at, message_id, content, response_time):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """UPDATE messages 
                     SET updated_at = %s, content = %s, response_time = %s
                     WHERE id = %s"""

            # Execute SQL statement
            cursor.execute(sql, (updated_at, content, response_time, message_id))

            # Commit the transaction
            conn.commit()
        except (Exception, psycopg2.Error) as error:
            logging.error(error)
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()

    def get_document_info_by_document_id(self, document_id):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            select_query = """SELECT id, file_name, miniourl
                              FROM documents
                              WHERE id = %s
                              limit 1
                              """

            cursor.execute(select_query, (document_id,))
            result = cursor.fetchone()
            if result:
                result = {'id': result[0], 'file_name': result[1], 'miniourl': result[2]}
            return result
        except (Exception, psycopg2.Error) as error:
            logging.error("Error: "+ str(error))
        finally:
            if conn:
                cursor.close()
                conn.close()

    def get_chat_message_history_by_session_id(self, session_id, limit=5):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            select_query = """SELECT content, sender_role
                              FROM messages
                              WHERE session_id = %s 
                              ORDER BY created_at DESC
                              LIMIT %s"""
            cursor.execute(select_query, (session_id, limit))
            result = cursor.fetchall()
            return result

        except (Exception, psycopg2.Error) as error:
            logging.error("Error: "+ str(error))
        finally:
            if conn:
                cursor.close()
                conn.close()

    def get_sources_by_message_id(self, message_id):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            select_query = """SELECT r.message_id, r.document_id, d.file_name, d.miniourl, r.page
                              FROM reference_docs r
                              JOIN documents d ON r.document_id = d.id
                              WHERE r.message_id = %s 
                              ORDER BY created_at DESC
                              """
            cursor.execute(select_query, (message_id,))
            result = cursor.fetchall()
            result_dict= [dict(zip(('message_id', 'document_id', 'file_name', 'miniourl', 'page'), r)) for r in result]
            for doc in result_dict:
                file_extension = doc.get("file_name", "").split(".")[-1].lower()
                doc["extension"] = extension_mapping.get(file_extension, file_extension)
            return result_dict
        except (Exception, psycopg2.Error) as error:
            logging.error("Error: "+ str(error))
        finally:
            if conn:
                cursor.close()
                conn.close()

    def get_pageable_chat_history_by_session_id(self, session_id, page=1, size=10, sort='DESC'):
        if not self.is_exist_session(session_id):
            logging.error("Chat session does not exist!")
            raise ValueError("Chat session does not exist")

        conn = self.create_connection()
        cursor = conn.cursor()
        sort_type = "DESC" if (sort == "desc" or sort == "DESC") else "ASC"
        try:
            offset = (page - 1) * size
            query = f"""
                SELECT id, session_id, content, sender_role, created_at
                FROM messages
                WHERE session_id = %s 
                ORDER BY created_at {sort_type}
                OFFSET %s LIMIT %s
            """

            cursor.execute(query, (session_id, offset, size))
            result = cursor.fetchall()
            return [dict(zip(('id', 'session_id', 'content', 'sender_role', 'created_at'), r)) for r in result]

        except (Exception, psycopg2.Error) as error:
            logging.error(error)
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()

    def get_feedbacks_by_message_ids(self, message_ids: list):
        if not message_ids:
            return ""
        conn = self.create_connection()
        cursor = conn.cursor()

        try:
            query = f"""
                SELECT id, comment, rating, created_at, message_id FROM feedbacks
                WHERE message_id IN %s;
            """

            # cursor.execute(query, (' , '.join(map(lambda x: f"'{x}'", message_ids)),))
            cursor.execute(query, (tuple(message_ids),))
            query_result = cursor.fetchall()
            result = []
            for row in query_result:
                json_source = {
                    "id": row[0],
                    "comment": row[1],
                    "rating": row[2],
                    "created_at": row[3],
                    "message_id": row[4],
                }
                result.append(json_source)
            return result

        except (Exception, psycopg2.Error) as error:
            logging.error(error)
            raise ValueError(error)

        finally:
            if conn:
                cursor.close()
                conn.close()

    def get_reference_docs_by_message_id(self, message_id):
        conn = self.create_connection()
        cursor = conn.cursor()

        try:
            query = """
                SELECT document_id, percentage from reference_docs
                WHERE message_id = %s;
            """

            cursor.execute(query, (message_id,))
            query_result = cursor.fetchall()
            result = []
            for row in query_result:
                document_name, root_url, minio_url = self._data_reprocessing_repository.get_document_by_id(
                    row[0])
                json_source = {
                    "document_id": row[0],
                    "document_name": document_name,
                    "percentage": row[1],
                    "root_url": root_url,
                    "minio_url": minio_url
                }
                result.append(json_source)
            return result

        except (Exception, psycopg2.Error) as error:
            logging.error(error)
            raise ValueError(error)

        finally:
            if conn:
                cursor.close()
                conn.close()

    def save_reference_docs(self, message_id, document_id, page):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """INSERT INTO public.reference_docs 
                     (message_id, document_id, page) 
                     VALUES (%s, %s, %s)"""

            # Execute SQL statement
            cursor.execute(sql, (message_id, document_id, page))

            # Commit the transaction
            conn.commit()
        except (Exception, psycopg2.Error) as error:
            logging.error(error)
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()

    def update_title_chat_session(self, session_id, title):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """UPDATE chat_sessions 
                     SET title = %s
                     WHERE id = %s"""

            # Execute SQL statement
            cursor.execute(sql, (title, session_id))

            # Commit the transaction
            conn.commit()
        except (Exception, psycopg2.Error) as error:
            logging.error(error)
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()

    def is_title_by_session_id(self, session_id):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """SELECT title FROM chat_sessions WHERE id = %s"""
            cursor.execute(sql, (session_id,))
            result = cursor.fetchone()[0]
            if result:
                return True
            return False
        except (Exception, psycopg2.Error) as error:
            logging.error(error)
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()
