import uuid
import psycopg2
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from src.database.db_connection import get_connection
# from src.repository.abstr_repository import Repository
from src.utils.logger.custom_logging import LoggerMixin


class VectorStoreDAL(LoggerMixin):
    """
    Data Access Layer for vector store collections management in PostgreSQL database.
    Handles CRUD operations for Qdrant collections and their metadata.
    """

    def __init__(self):
        super().__init__()
        self.connection = get_connection()
        print(f"self.connection {get_connection()}")

    def _get_cursor(self):
        """Get a cursor from the connection pool"""
        return self.connection.cursor()

    def create_vector_store_collection(self, user_id: str, collection_name: str) -> bool:
        """
        Create a new vector store collection record in the database
        Returns True if successful, False otherwise
        """
        cursor = self._get_cursor()
        try:
            # Check if collection already exists for this user
            check_sql = """
                SELECT id FROM vector_store_collections 
                WHERE user_id = %s AND collection_name = %s
            """
            cursor.execute(check_sql, (user_id, collection_name))
            if cursor.fetchone():
                self.logger.warning(f"Collection {collection_name} already exists for user {user_id}")
                return False

            # Insert new collection
            sql = """
                INSERT INTO vector_store_collections (
                    id, user_id, collection_name, created_at, status
                ) VALUES (%s, %s, %s, %s, %s)
            """
            
            collection_id = str(uuid.uuid4())
            created_at = datetime.now()
            status = True  # Active status
            
            cursor.execute(
                sql, 
                (collection_id, user_id, collection_name, created_at, status)
            )
            
            self.connection.commit()
            self.logger.info(f"Created vector store collection {collection_name} for user {user_id}")
            return True
            
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Error creating vector store collection: {str(e)}")
            return False
        finally:
            cursor.close()

    def get_collection_by_name(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """
        Get collection information by name
        """
        cursor = self._get_cursor()
        try:
            sql = """
                SELECT id, user_id, collection_name, created_at, updated_at, status 
                FROM vector_store_collections
                WHERE collection_name = %s
            """
            
            cursor.execute(sql, (collection_name,))
            result = cursor.fetchone()
            
            if not result:
                return None
                
            return {
                "id": result[0],
                "user_id": result[1],
                "collection_name": result[2],
                "created_at": result[3],
                "updated_at": result[4],
                "status": result[5]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting collection by name {collection_name}: {str(e)}")
            return None
        finally:
            cursor.close()

    def collection_own_by_user(self, user_id: str, collection_name: str) -> bool:
        """
        Check if a collection is owned by a specific user
        """
        cursor = self._get_cursor()
        try:
            sql = """
                SELECT id FROM vector_store_collections 
                WHERE user_id = %s AND collection_name = %s AND status = TRUE
            """
            
            cursor.execute(sql, (user_id, collection_name))
            result = cursor.fetchone()
            
            return result is not None
            
        except Exception as e:
            self.logger.error(f"Error checking collection ownership: {str(e)}")
            return False
        finally:
            cursor.close()

    def get_collections_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all collections belonging to a user
        """
        cursor = self._get_cursor()
        try:
            sql = """
                SELECT id, collection_name, created_at, updated_at
                FROM vector_store_collections
                WHERE user_id = %s AND status = TRUE
                ORDER BY created_at DESC
            """
            
            cursor.execute(sql, (user_id,))
            results = cursor.fetchall()
            
            collections = []
            for result in results:
                collections.append({
                    "id": result[0],
                    "collection_name": result[1],
                    "created_at": result[2],
                    "updated_at": result[3]
                })
                
            return collections
            
        except Exception as e:
            self.logger.error(f"Error getting collections for user {user_id}: {str(e)}")
            return []
        finally:
            cursor.close()

    def update_collection(self, collection_name: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing collection record
        Returns True if successful, False otherwise
        """
        if not updates:
            return False
            
        cursor = self._get_cursor()
        try:
            set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
            values = list(updates.values())
            
            sql = f"""
                UPDATE vector_store_collections
                SET {set_clause}, updated_at = %s
                WHERE collection_name = %s
            """
            
            values.append(datetime.now())  # updated_at
            values.append(collection_name)
            
            cursor.execute(sql, values)
            self.connection.commit()
            
            rows_affected = cursor.rowcount
            return rows_affected > 0
            
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Error updating collection {collection_name}: {str(e)}")
            return False
        finally:
            cursor.close()

    def delete_vector_store_collection(self, user_id: str, collection_name: str) -> bool:
        """
        Delete a collection record
        Returns True if successful, False otherwise
        """
        cursor = self._get_cursor()
        try:
            # First check if user owns the collection
            if not self.collection_own_by_user(user_id, collection_name):
                self.logger.warning(f"User {user_id} does not own collection {collection_name}")
                return False
                
            # Delete the collection
            sql = """
                DELETE FROM vector_store_collections 
                WHERE user_id = %s AND collection_name = %s
            """
            
            cursor.execute(sql, (user_id, collection_name))
            self.connection.commit()
            
            rows_affected = cursor.rowcount
            self.logger.info(f"Deleted collection {collection_name} for user {user_id}")
            return rows_affected > 0
            
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Error deleting collection {collection_name}: {str(e)}")
            return False
        finally:
            cursor.close()

    def set_collection_status(self, collection_name: str, status: bool) -> bool:
        """
        Set the status of a collection (active/inactive)
        Returns True if successful, False otherwise
        """
        cursor = self._get_cursor()
        try:
            sql = """
                UPDATE vector_store_collections
                SET status = %s, updated_at = %s
                WHERE collection_name = %s
            """
            
            cursor.execute(sql, (status, datetime.now(), collection_name))
            self.connection.commit()
            
            rows_affected = cursor.rowcount
            self.logger.info(f"Set collection {collection_name} status to {status}")
            return rows_affected > 0
            
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Error setting collection status: {str(e)}")
            return False
        finally:
            cursor.close()

    def get_all_collections(self) -> List[Dict[str, Any]]:
        """
        Get all collections in the system
        """
        cursor = self._get_cursor()
        try:
            sql = """
                SELECT vsc.id, vsc.user_id, vsc.collection_name, vsc.created_at, 
                       vsc.updated_at, vsc.status, u.username
                FROM vector_store_collections vsc
                JOIN users u ON vsc.user_id = u.id
                ORDER BY vsc.created_at DESC
            """
            
            cursor.execute(sql)
            results = cursor.fetchall()
            
            collections = []
            for result in results:
                collections.append({
                    "id": result[0],
                    "user_id": result[1],
                    "collection_name": result[2],
                    "created_at": result[3],
                    "updated_at": result[4],
                    "status": result[5],
                    "owner_username": result[6]
                })
                
            return collections
            
        except Exception as e:
            self.logger.error(f"Error getting all collections: {str(e)}")
            return []
        finally:
            cursor.close()
            
    def search_collections(
        self, 
        keyword: Optional[str] = None,
        user_id: Optional[str] = None,
        active_only: bool = True,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search for collections based on various criteria
        """
        cursor = self._get_cursor()
        try:
            conditions = []
            params = []
            
            if active_only:
                conditions.append("vsc.status = TRUE")
                
            if keyword:
                conditions.append("LOWER(vsc.collection_name) LIKE %s")
                params.append(f"%{keyword.lower()}%")
                
            if user_id:
                conditions.append("vsc.user_id = %s")
                params.append(user_id)
                
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            # Count query
            count_sql = f"""
                SELECT COUNT(*) FROM vector_store_collections vsc
                WHERE {where_clause}
            """
            cursor.execute(count_sql, params)
            total_count = cursor.fetchone()[0]
            
            # Data query
            data_sql = f"""
                SELECT vsc.id, vsc.user_id, vsc.collection_name, vsc.created_at, 
                       vsc.updated_at, vsc.status, u.username
                FROM vector_store_collections vsc
                JOIN users u ON vsc.user_id = u.id
                WHERE {where_clause}
                ORDER BY vsc.created_at DESC
                LIMIT %s OFFSET %s
            """
            
            cursor.execute(data_sql, params + [limit, offset])
            results = cursor.fetchall()
            
            collections = []
            for result in results:
                collections.append({
                    "id": result[0],
                    "user_id": result[1],
                    "collection_name": result[2],
                    "created_at": result[3],
                    "updated_at": result[4],
                    "status": result[5],
                    "owner_username": result[6]
                })
                
            return {
                "total_count": total_count,
                "collections": collections
            }
            
        except Exception as e:
            self.logger.error(f"Error searching collections: {str(e)}")
            return {"total_count": 0, "collections": []}
        finally:
            cursor.close()

    def create_db_tables_if_not_exist(self):
        """
        Create database tables if they don't exist yet
        This is useful for initial setup
        """
        cursor = self._get_cursor()
        try:
            # Create vector_store_collections table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vector_store_collections (
                    id UUID PRIMARY KEY,
                    user_id UUID NOT NULL,
                    collection_name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP,
                    status BOOLEAN NOT NULL DEFAULT TRUE,
                    CONSTRAINT unique_user_collection UNIQUE (user_id, collection_name)
                );
            """)
            
            # Create index for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_vsc_user_id ON vector_store_collections(user_id);
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_vsc_collection_name ON vector_store_collections(collection_name);
            """)
            
            self.connection.commit()
            self.logger.info("Vector store collection tables created or already exist")
            return True
            
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Error creating database tables: {str(e)}")
            return False
        finally:
            cursor.close()