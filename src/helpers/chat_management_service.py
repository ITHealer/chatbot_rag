import uuid
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional

from src.repository.chat_repository import ChatRepository
from src.utils.logger.custom_logging import LoggerMixin


class ChatService(LoggerMixin):
    def __init__(self):
        super().__init__()
        self.chat_repo = ChatRepository()
    
    # def create_chat_session(self, user_id: str) -> str:
    #     """
    #     Create a new chat session for a user
        
    #     Args:
    #         user_id: The ID of the user creating the chat session
            
    #     Returns:
    #         str: The generated session ID
    #     """
    #     try:
    #         # Create a connection to the database
    #         conn = self.chat_repo.create_connection()
    #         cursor = conn.cursor()
            
    #         # Generate a unique session ID
    #         session_id = str(uuid.uuid4())
            
    #         # Insert the new session into the database
    #         sql = """INSERT INTO chat_sessions 
    #                  (id, created_at, created_by, updated_at, updated_by, title) 
    #                  VALUES (%s, %s, %s, NULL, NULL, NULL)"""
            
    #         # Current timestamp
    #         timestamp = datetime.now()
            
    #         # Execute the SQL query
    #         cursor.execute(sql, (session_id, timestamp, user_id))
    #         conn.commit()
            
    #         self.logger.info(f"Created new chat session with ID: {session_id} for user: {user_id}")
    #         return session_id
            
    #     except Exception as e:
    #         self.logger.error(f"Failed to create chat session for user: {user_id}. Error: {str(e)}")
    #         raise
    #     finally:
    #         if conn:
    #             cursor.close()
    #             conn.close()
    def create_chat_session(self, user_id: str) -> str:
        """
        Create a new chat session for a user
        
        Args:
            user_id: The ID of the user creating the chat session
            
        Returns:
            str: The generated session ID
        """
        try:
            # Create a connection to the database
            conn = self.chat_repo.create_connection()
            cursor = conn.cursor()
            
            # Generate a unique session ID
            session_id = str(uuid.uuid4())
            
            # Insert the new session into the database
            # Match with actual table structure from alembic
            sql = """INSERT INTO chat_sessions 
                     (id, user_id, start_date, title, state) 
                     VALUES (%s, %s, %s, %s, %s)"""
            
            # Current timestamp
            timestamp = datetime.now()
            
            # Default title and state
            default_title = "New Chat"  # Default title
            default_state = 1  # Assuming 1 means 'active'
            
            # Execute the SQL query
            cursor.execute(sql, (session_id, user_id, timestamp, default_title, default_state))
            conn.commit()
            
            self.logger.info(f"Created new chat session with ID: {session_id} for user: {user_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Failed to create chat session for user: {user_id}. Error: {str(e)}")
            raise
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    def is_session_exist(self, session_id: str) -> bool:
        """
        Check if a chat session exists
        
        Args:
            session_id: The ID of the session to check
            
        Returns:
            bool: True if the session exists, False otherwise
        """
        return self.chat_repo.is_exist_session(session_id)
    
    def save_user_question(self, session_id: str, created_at: datetime, created_by: str, content: str) -> str:
        """
        Save a user's question in the database
        
        Args:
            session_id: The ID of the chat session
            created_at: When the question was created
            created_by: Who created the question
            content: The question text
            
        Returns:
            str: The ID of the saved question
        """
        try:
            question_id = self.chat_repo.save_user_question(
                session_id=session_id,
                created_at=created_at,
                created_by=created_by,
                content=content
            )
            self.logger.info(f"Saved user question in session {session_id}")
            return question_id
        except Exception as e:
            self.logger.error(f"Failed to save user question in session {session_id}. Error: {str(e)}")
            raise
    
    def save_assistant_response(self, session_id: str, created_at: datetime, question_id: str, 
                              content: str, response_time: float) -> str:
        """
        Save the assistant's response in the database
        
        Args:
            session_id: The ID of the chat session
            created_at: When the response was created
            question_id: The ID of the question being answered
            content: The response text
            response_time: How long it took to generate the response
            
        Returns:
            str: The ID of the saved response
        """
        try:
            message_id = self.chat_repo.save_assistant_response(
                session_id=session_id,
                created_at=created_at,
                question_id=question_id,
                content=content,
                response_time=response_time
            )
            self.logger.info(f"Saved assistant response in session {session_id}")
            return message_id
        except Exception as e:
            self.logger.error(f"Failed to save assistant response in session {session_id}. Error: {str(e)}")
            raise
    
    def update_assistant_response(self, updated_at: datetime, message_id: str, 
                                content: str, response_time: float) -> None:
        """
        Update an assistant's response in the database
        
        Args:
            updated_at: When the response was updated
            message_id: The ID of the message being updated
            content: The updated response text
            response_time: The updated response time
        """
        try:
            self.chat_repo.update_assistant_response(
                updated_at=updated_at,
                message_id=message_id,
                content=content,
                response_time=response_time
            )
            self.logger.info(f"Updated assistant response with ID {message_id}")
        except Exception as e:
            self.logger.error(f"Failed to update assistant response with ID {message_id}. Error: {str(e)}")
            raise
    
    def get_chat_history(self, session_id: str, limit: int = 5) -> List[Tuple[str, str]]:
        """
        Get the chat history for a session
        
        Args:
            session_id: The ID of the chat session
            limit: Maximum number of messages to retrieve
            
        Returns:
            List[Tuple[str, str]]: List of tuples containing (content, sender_role)
        """
        try:
            history = self.chat_repo.get_chat_message_history_by_session_id(
                session_id=session_id,
                limit=limit
            )
            self.logger.info(f"Retrieved chat history for session {session_id}")
            return history
        except Exception as e:
            self.logger.error(f"Failed to retrieve chat history for session {session_id}. Error: {str(e)}")
            raise
    
    def delete_chat_history(self, session_id: str) -> None:
        """
        Delete the chat history for a session
        
        Args:
            session_id: The ID of the chat session to delete
        """
        try:
            # Create a connection to the database
            conn = self.chat_repo.create_connection()
            cursor = conn.cursor()
            
            # First delete all messages associated with the session
            sql_messages = """DELETE FROM messages WHERE session_id = %s"""
            cursor.execute(sql_messages, (session_id,))
            
            # Then delete the session itself (or alternatively, mark it as closed)
            # Option 1: Delete the session
            sql_session = """DELETE FROM chat_sessions WHERE id = %s"""
            cursor.execute(sql_session, (session_id,))
            
            # Option 2: Alternatively, mark the session as closed instead of deleting
            # sql_update = """UPDATE chat_sessions SET state = 0, end_date = %s WHERE id = %s"""
            # cursor.execute(sql_update, (datetime.now(), session_id))
            
            conn.commit()
            self.logger.info(f"Deleted chat history for session {session_id}")
        except Exception as e:
            self.logger.error(f"Failed to delete chat history for session {session_id}. Error: {str(e)}")
            raise
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    def get_pageable_chat_history(self, session_id: str, page: int = 1, 
                                 size: int = 10, sort: str = 'DESC') -> List[Dict[str, Any]]:
        """
        Get paginated chat history for a session
        
        Args:
            session_id: The ID of the chat session
            page: Page number (1-based)
            size: Number of items per page
            sort: Sort order ('ASC' or 'DESC')
            
        Returns:
            List[Dict[str, Any]]: List of message dictionaries
        """
        try:
            history = self.chat_repo.get_pageable_chat_history_by_session_id(
                session_id=session_id,
                page=page,
                size=size,
                sort=sort
            )
            self.logger.info(f"Retrieved pageable chat history for session {session_id}")
            return history
        except Exception as e:
            self.logger.error(f"Failed to retrieve pageable chat history for session {session_id}. Error: {str(e)}")
            raise
    
    def save_reference_docs(self, message_id: str, document_id: str, page: int) -> None:
        """
        Save reference documents related to a message
        
        Args:
            message_id: The ID of the message
            document_id: The ID of the referenced document
            page: The page number in the document
        """
        try:
            self.chat_repo.save_reference_docs(
                message_id=message_id,
                document_id=document_id,
                page=page
            )
            self.logger.info(f"Saved reference document {document_id} for message {message_id}")
        except Exception as e:
            self.logger.error(f"Failed to save reference document {document_id} for message {message_id}. Error: {str(e)}")
            raise
    
    def get_sources_by_message(self, message_id: str) -> List[Dict[str, Any]]:
        """
        Get the sources referenced by a message
        
        Args:
            message_id: The ID of the message
            
        Returns:
            List[Dict[str, Any]]: List of source dictionaries
        """
        try:
            sources = self.chat_repo.get_sources_by_message_id(message_id)
            self.logger.info(f"Retrieved sources for message {message_id}")
            return sources
        except Exception as e:
            self.logger.error(f"Failed to retrieve sources for message {message_id}. Error: {str(e)}")
            raise