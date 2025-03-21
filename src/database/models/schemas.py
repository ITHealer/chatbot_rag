import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Boolean, REAL, SMALLINT
from sqlalchemy.orm import relationship

from src.database.db_connection import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    password = Column(String(255), nullable=False)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    role = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=True)
    enabled = Column(SMALLINT, nullable=True)
    created = Column(DateTime, nullable=True)
    chat_sessions = relationship("ChatSessions", back_populates="user", cascade="all, delete-orphan")

class ChatSessions(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    title = Column(String(255), nullable=False)
    final_answer = Column(String(255), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    state = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=True)
    quantity_rating = Column(Integer, nullable=True)
    total_rating = Column(Integer, nullable=True)
    avg_rating = Column(Integer, nullable=True)

    user = relationship("Users", back_populates="chat_sessions")
    messages = relationship("Messages", back_populates="session", cascade="all, delete-orphan")

class Documents(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    file_name = Column(String(255), nullable=False)
    collection_name = Column(String(255), nullable=False)
    extension = Column(String(255), nullable=False)
    size = Column(Integer, nullable=True)
    status = Column(Boolean, nullable=True)
    created_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=True)
    sha256 = Column(String, nullable=False)
    reference_docs = relationship("ReferenceDocs", back_populates="document")

class Messages(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    content = Column(String(10000), nullable=True)
    created_by = Column(String(255), nullable=True)
    question_id = Column(UUID(as_uuid=True), nullable=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('chat_sessions.id'), nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)  
    updated_by = Column(String(255), nullable=True)
    type = Column(String(255), nullable=True)
    sender_role = Column(String(255), nullable=True)
    response_time = Column(REAL, nullable=True)

    session = relationship("ChatSessions", back_populates="messages")
    reference_docs = relationship("ReferenceDocs", back_populates="message")

class ReferenceDocs(Base):
    __tablename__ = "reference_docs"

    message_id = Column(UUID(as_uuid=True), ForeignKey('messages.id'), primary_key=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id'), primary_key=True)
    page = Column(Integer, nullable=True)

    message = relationship("Messages", back_populates="reference_docs")
    document = relationship("Documents", back_populates="reference_docs")

class Collection(Base):
    __tablename__ = "vectorstore_collection"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    collection_name = Column(String(), nullable=True)