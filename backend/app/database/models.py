import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()

def utcnow():
    return datetime.now(timezone.utc)

class Profile(Base):
    __tablename__ = "profiles"
    
    # Terikat langsung dengan auth.users milik Supabase
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    threads = relationship("ChatThread", back_populates="profile")


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    file_metadata = Column(JSONB, default=dict)  # contoh: year, ticker
    full_markdown = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("source_documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    chunk_metadata = Column(JSONB, default=dict) # contoh: section, headers
    
    # Semantic Search (AI Embeddings)
    embedding = Column(Vector(1536))
    
    # Lexical Search (Postgres Full-Text Search)
    fts_vector = Column(TSVECTOR)
    
    created_at = Column(DateTime(timezone=True), default=utcnow)

    document = relationship("SourceDocument", back_populates="chunks")


class ChatThread(Base):
    __tablename__ = "chat_threads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    profile = relationship("Profile", back_populates="threads")
    messages = relationship("ChatMessage", back_populates="thread", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("chat_threads.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    thread = relationship("ChatThread", back_populates="messages")
    citations = relationship("MessageCitation", back_populates="message", cascade="all, delete-orphan")


class MessageCitation(Base):
    __tablename__ = "message_citations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("document_chunks.id", ondelete="CASCADE"), nullable=False)
    
    message = relationship("ChatMessage", back_populates="citations")
    chunk = relationship("DocumentChunk")
