from typing import Dict, List, Optional, Any, Union
import uuid
from datetime import datetime

from src.database.models.schemas import Users
from src.database.db_connection import db
from src.utils.logger.custom_logging import LoggerMixin

class UserORMRepository(LoggerMixin):
    """Repository for User operations using SQLAlchemy ORM"""
    
    def __init__(self):
        super().__init__()
        
    def is_exist_user(self, username: str) -> bool:
        """Check if a user with the given username exists"""
        with db.session_scope() as session:
            return session.query(session.query(Users).filter(Users.username == username).exists()).scalar()
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user information by username"""
        with db.session_scope() as session:
            user = session.query(Users).filter(Users.username == username).first()
            if not user:
                return None
            
            return {
                "id": str(user.id),
                "username": user.username,
                "full_name": user.full_name,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "enabled": user.enabled
            }
    
    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """Get all users as a dictionary indexed by username"""
        users_dict = {}
        
        with db.session_scope() as session:
            all_users = session.query(Users).all()
            
            # Chuyển đổi đối tượng ORM thành dict trong phạm vi session
            for user in all_users:
                # Truy cập tất cả thuộc tính trong session
                users_dict[user.username] = {
                    "id": str(user.id),
                    "username": user.username,
                    "password": user.password,
                    "full_name": user.full_name,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "enabled": user.enabled
                }
        
        # Trả về dict là an toàn vì không phụ thuộc vào session
        return users_dict
    
    def create_user(self, username: str, password: str, email: str, 
                   full_name: str = '', first_name: str = '', 
                   last_name: str = '', role: str = 'USER') -> str:
        """Create a new user and return the username"""
        with db.session_scope() as session:
            new_user = Users(
                id=uuid.uuid4(),
                username=username,
                password=password,
                email=email,
                full_name=full_name,
                first_name=first_name,
                last_name=last_name,
                role=role,
                enabled=1,
                created=datetime.now()
            )
            
            session.add(new_user)
            session.commit()
            return username
    
    def get_user_role(self, username: str) -> Optional[str]:
        """Get the role of a user by username"""
        with db.session_scope() as session:
            user = session.query(Users).filter(Users.username == username).first()
            return user.role if user else None
    
    def change_password(self, username: str, new_hashed_password: str) -> bool:
        """Change a user's password"""
        with db.session_scope() as session:
            user = session.query(Users).filter(Users.username == username).first()
            if not user:
                return False
                
            user.password = new_hashed_password
            session.commit()
            return True
    
    def get_sessions_from_user(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get chat sessions for a user"""
        with db.session_scope() as session:
            user = session.query(Users).filter(Users.id == user_id).first()
            if not user:
                return []
                
            # Cần eager loading để tránh lỗi detached
            sessions = user.chat_sessions[:limit]
            
            # Chuyển đổi thành dict trong phạm vi session
            return [{"id": str(s.id), "title": s.title} for s in sessions]