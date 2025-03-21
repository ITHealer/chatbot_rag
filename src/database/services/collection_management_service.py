import uuid
from datetime import datetime
from typing import List, Optional

from src.database.db_connection import db
from src.database.models.schemas import Collection, Users
from src.utils.logger.custom_logging import LoggerMixin


class CollectionManagementService(LoggerMixin):
    """
    Service to manage collections metadata in the database.
    Synchronizes collection information between Qdrant and PostgreSQL.
    """

    def __init__(self):
        super().__init__()

    def create_collection(self, collection_name: str, user_id: str) -> str:
        """
        Create a new collection record in the database
        
        Args:
            collection_name: Name of the collection
            user_id: ID of the user who owns this collection
            
        Returns:
            str: ID of the created collection record
        """
        try:
            with db.session_scope() as session:
                # Check if collection already exists
                existing = session.query(Collection).filter_by(
                    collection_name=collection_name
                ).first()
                
                if existing:
                    self.logger.info(f"Collection {collection_name} already exists in database")
                    return str(existing.id)
                
                # Create new collection record
                collection_id = uuid.uuid4()
                new_collection = Collection(
                    id=collection_id,
                    user_id=user_id,
                    collection_name=collection_name
                )
                
                session.add(new_collection)
                # Session is automatically committed by session_scope
                
                self.logger.info(f"Created collection record for {collection_name} with ID {collection_id}")
                return str(collection_id)
                
        except Exception as e:
            self.logger.error(f"Error creating collection record: {str(e)}")
            raise

    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection record from the database
        
        Args:
            collection_name: Name of the collection to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            with db.session_scope() as session:
                # Delete collection record
                result = session.query(Collection).filter_by(
                    collection_name=collection_name
                ).delete()
                
                # Session is automatically committed by session_scope
                
                if result > 0:
                    self.logger.info(f"Deleted collection record for {collection_name}")
                    return True
                else:
                    self.logger.warning(f"No collection record found for {collection_name}")
                    return False
                
        except Exception as e:
            self.logger.error(f"Error deleting collection record: {str(e)}")
            return False

    def get_user_collections(self, user_id: str) -> List[str]:
        """
        Get all collections belonging to a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List[str]: List of collection names
        """
        try:
            with db.session_scope() as session:
                collections = session.query(Collection.collection_name).filter_by(
                    user_id=user_id
                ).all()
                
                # Convert from list of tuples to list of strings
                return [c[0] for c in collections]
                
        except Exception as e:
            self.logger.error(f"Error getting user collections: {str(e)}")
            return []

    def is_collection_owner(self, user_id: str, collection_name: str) -> bool:
        """
        Check if a user owns a collection
        
        Args:
            user_id: ID of the user
            collection_name: Name of the collection
            
        Returns:
            bool: True if user owns the collection, False otherwise
        """
        try:
            with db.session_scope() as session:
                collection = session.query(Collection).filter_by(
                    user_id=user_id, 
                    collection_name=collection_name
                ).first()
                
                return collection is not None
                
        except Exception as e:
            self.logger.error(f"Error checking collection ownership: {str(e)}")
            return False

    def get_all_collections(self, is_admin: bool = False) -> List[str]:
        """
        Get all collections in the database.
        Only for admin users.
        
        Args:
            is_admin: Whether the requesting user is an admin
            
        Returns:
            List[str]: List of all collection names
        """
        if not is_admin:
            return []
            
        try:
            with db.session_scope() as session:
                collections = session.query(Collection.collection_name).all()
                
                # Convert from list of tuples to list of strings
                return [c[0] for c in collections]
                
        except Exception as e:
            self.logger.error(f"Error getting all collections: {str(e)}")
            return []