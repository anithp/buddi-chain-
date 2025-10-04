"""Database models for the Buddi Tokenization PoC."""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.database import Base


class Conversation(Base):
    """Model for storing tokenized conversations."""
    
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    anchor_id = Column(String(255), unique=True, nullable=False, index=True)
    token_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Raw data
    summary = Column(Text, nullable=False)
    actions = Column(Text)  # JSON string of actions
    conversation_metadata = Column(Text)  # JSON string of metadata
    
    # Analytics data
    sentiment = Column(Float)  # Sentiment score (-1 to 1)
    sentiment_label = Column(String(50))  # positive, negative, neutral
    topics = Column(Text)  # JSON string of extracted topics
    keywords = Column(Text)  # JSON string of keywords
    quality_score = Column(Float)  # Quality score (0 to 1)
    engagement_score = Column(Float)  # Engagement score (0 to 1)
    
    # Blockchain data
    merkle_root = Column(String(255), nullable=False)
    token_uri = Column(String(500))  # IPFS or storage URI
    contract_address = Column(String(255))  # AccessNFT contract address
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Status
    is_processed = Column(Boolean, default=False)
    is_exported = Column(Boolean, default=False)


class Dataset(Base):
    """Model for storing exported datasets for LLM buyers."""
    
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Dataset configuration
    conversation_ids = Column(Text)  # JSON string of conversation IDs
    filters = Column(Text)  # JSON string of applied filters
    quality_threshold = Column(Float, default=0.5)
    
    # Export data
    export_format = Column(String(50), default="json")  # json, csv, parquet
    file_path = Column(String(500))
    file_size = Column(Integer)  # Size in bytes
    
    # Metadata
    total_conversations = Column(Integer, default=0)
    avg_sentiment = Column(Float)
    avg_quality_score = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    exported_at = Column(DateTime(timezone=True))
    
    # Status
    is_ready = Column(Boolean, default=False)
