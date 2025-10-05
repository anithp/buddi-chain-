"""API routes for conversation management."""

import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models import Conversation, Dataset
from app.services.buddi_api import BuddiAPIService
from app.services.tokenization import create_tokenization_service
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


class ConversationResponse(BaseModel):
    """Response model for conversation data."""
    id: int
    user_id: str
    anchor_id: str
    token_id: str
    sentiment: Optional[float]
    sentiment_label: Optional[str]
    topics: Optional[List[str]]
    quality_score: Optional[float]
    engagement_score: Optional[float]
    created_at: str
    is_processed: bool


class StructuredConversationResponse(BaseModel):
    """Structured response model for detailed conversation data."""
    id: int
    user_id: str
    token_id: str
    anchor_id: str
    merkle_root: Optional[str]
    contract_address: Optional[str]
    token_uri: Optional[str]
    
    # Parsed summary data
    summary: dict
    title: Optional[str]
    content: Optional[str]
    emoji: Optional[str]
    category: Optional[str]
    
    # Actions
    actions: List[dict]
    
    # Analytics
    sentiment: Optional[float]
    sentiment_label: Optional[str]
    topics: List[str]
    keywords: List[str]
    quality_score: Optional[float]
    engagement_score: Optional[float]
    
    # Metadata
    created_at: str
    updated_at: Optional[str]
    is_processed: bool
    is_exported: bool


class TokenizeRequest(BaseModel):
    """Request model for tokenizing conversations."""
    user_id: str
    conversation_ids: Optional[List[str]] = None
    limit: int = 100


class TokenizeResponse(BaseModel):
    """Response model for tokenization results."""
    success: bool
    message: str
    tokenized_count: int
    failed_count: int
    results: List[dict]


@router.get("/", response_model=List[ConversationResponse])
async def get_conversations(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    is_processed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get list of conversations with optional filtering."""
    query = db.query(Conversation)
    
    if user_id:
        query = query.filter(Conversation.user_id == user_id)
    
    if is_processed is not None:
        query = query.filter(Conversation.is_processed == is_processed)
    
    conversations = query.offset(skip).limit(limit).all()
    
    return [
        ConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            anchor_id=conv.anchor_id,
            token_id=conv.token_id,
            sentiment=conv.sentiment,
            sentiment_label=conv.sentiment_label,
            topics=json.loads(conv.topics) if conv.topics else [],
            quality_score=conv.quality_score,
            engagement_score=conv.engagement_score,
            created_at=conv.created_at.isoformat(),
            is_processed=conv.is_processed
        )
        for conv in conversations
    ]


@router.get("/structured", response_model=List[StructuredConversationResponse])
async def get_structured_conversations(
    skip: int = 0,
    limit: int = 20,
    user_id: Optional[str] = None,
    sentiment: Optional[str] = None,
    quality_min: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Get conversations with structured, human-readable data."""
    query = db.query(Conversation)
    
    if user_id:
        query = query.filter(Conversation.user_id == user_id)
    if sentiment:
        query = query.filter(Conversation.sentiment_label == sentiment)
    if quality_min is not None:
        query = query.filter(Conversation.quality_score >= quality_min)
    
    conversations = query.offset(skip).limit(limit).all()
    
    structured_conversations = []
    for conv in conversations:
        # Parse JSON fields
        summary_data = json.loads(conv.summary) if conv.summary else {}
        actions_data = json.loads(conv.actions) if conv.actions else []
        topics_data = json.loads(conv.topics) if conv.topics else []
        keywords_data = json.loads(conv.keywords) if conv.keywords else []
        
        structured_conversations.append(StructuredConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            token_id=conv.token_id,
            anchor_id=conv.anchor_id,
            merkle_root=conv.merkle_root,
            contract_address=conv.contract_address,
            token_uri=conv.token_uri,
            
            # Parsed summary data
            summary=summary_data,
            title=summary_data.get("title", ""),
            content=summary_data.get("content", ""),
            emoji=summary_data.get("emoji", ""),
            category=summary_data.get("category", ""),
            
            # Actions
            actions=actions_data,
            
            # Analytics
            sentiment=conv.sentiment,
            sentiment_label=conv.sentiment_label,
            topics=topics_data,
            keywords=keywords_data,
            quality_score=conv.quality_score,
            engagement_score=conv.engagement_score,
            
            # Metadata
            created_at=conv.created_at.isoformat() if conv.created_at else "",
            updated_at=conv.updated_at.isoformat() if conv.updated_at else None,
            is_processed=conv.is_processed,
            is_exported=conv.is_exported
        ))
    
    return structured_conversations


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Get a specific conversation by ID."""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        anchor_id=conversation.anchor_id,
        token_id=conversation.token_id,
        sentiment=conversation.sentiment,
        sentiment_label=conversation.sentiment_label,
        topics=json.loads(conversation.topics) if conversation.topics else [],
        quality_score=conversation.quality_score,
        engagement_score=conversation.engagement_score,
        created_at=conversation.created_at.isoformat(),
        is_processed=conversation.is_processed
    )


@router.post("/tokenize", response_model=TokenizeResponse)
async def tokenize_conversations(
    request: TokenizeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Tokenize conversations from Buddi API."""
    try:
        # Initialize services
        buddi_service = BuddiAPIService()
        tokenization_service = create_tokenization_service()
        analytics_service = AnalyticsService()
        
        # Deploy contracts if not already deployed
        if not tokenization_service.anchor_registry_contract:
            await tokenization_service.deploy_contracts()
        
        # Fetch conversations from Buddi API
        if request.conversation_ids:
            conversations_data = []
            for conv_id in request.conversation_ids:
                data = await buddi_service.fetch_conversation_details(conv_id)
                if data:
                    conversations_data.append(data)
        else:
            conversations_data = await buddi_service.fetch_conversation_summaries(
                request.user_id, request.limit
            )
        
        tokenized_count = 0
        failed_count = 0
        results = []
        
        for conv_data in conversations_data:
            try:
                # Perform analytics
                analytics = analytics_service.analyze_conversation(conv_data)
                
                # Tokenize conversation
                tokenization_result = await tokenization_service.tokenize_conversation(
                    conv_data, request.user_id
                )
                
                # Save to database
                conversation = Conversation(
                    user_id=request.user_id,
                    anchor_id=tokenization_result["anchor_id"],
                    token_id=tokenization_result["token_id"],
                    summary=json.dumps(conv_data.get("summary", {})),
                    actions=json.dumps(conv_data.get("actions", [])),
                    conversation_metadata=json.dumps(conv_data.get("conversation_metadata", {})),
                    sentiment=analytics["sentiment"],
                    sentiment_label=analytics["sentiment_label"],
                    topics=json.dumps(analytics["topics"]),
                    keywords=json.dumps(analytics["keywords"]),
                    quality_score=analytics["quality_score"],
                    engagement_score=analytics["engagement_score"],
                    merkle_root=tokenization_result["merkle_root"],
                    token_uri=tokenization_result.get("token_uri", ""),
                    contract_address=tokenization_result["access_nft_address"],
                    is_processed=True
                )
                
                db.add(conversation)
                db.commit()
                
                tokenized_count += 1
                results.append({
                    "conversation_id": conv_data.get("conversation_id"),
                    "anchor_id": tokenization_result["anchor_id"],
                    "token_id": tokenization_result["token_id"],
                    "status": "success"
                })
                
            except Exception as e:
                failed_count += 1
                results.append({
                    "conversation_id": conv_data.get("conversation_id"),
                    "status": "failed",
                    "error": str(e)
                })
        
        return TokenizeResponse(
            success=True,
            message=f"Tokenized {tokenized_count} conversations, {failed_count} failed",
            tokenized_count=tokenized_count,
            failed_count=failed_count,
            results=results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tokenization failed: {str(e)}")


@router.post("/{conversation_id}/analyze")
async def analyze_conversation(
    conversation_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Re-analyze a specific conversation."""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    try:
        # Parse conversation data
        conv_data = {
            "conversation_id": conversation_id,
            "summary": json.loads(conversation.summary),
            "actions": json.loads(conversation.actions),
            "conversation_metadata": json.loads(conversation.conversation_metadata)
        }
        
        # Perform analytics
        analytics_service = AnalyticsService()
        analytics = analytics_service.analyze_conversation(conv_data)
        
        # Update conversation
        conversation.sentiment = analytics["sentiment"]
        conversation.sentiment_label = analytics["sentiment_label"]
        conversation.topics = json.dumps(analytics["topics"])
        conversation.keywords = json.dumps(analytics["keywords"])
        conversation.quality_score = analytics["quality_score"]
        conversation.engagement_score = analytics["engagement_score"]
        conversation.is_processed = True
        
        db.commit()
        
        return {"message": "Analysis completed successfully", "analytics": analytics}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/{conversation_id}/verify")
async def verify_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Verify a conversation's blockchain anchoring."""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    try:
        tokenization_service = create_tokenization_service()
        is_verified = await tokenization_service.verify_conversation(
            int(conversation.anchor_id), conversation.merkle_root
        )
        
        return {
            "conversation_id": conversation_id,
            "anchor_id": conversation.anchor_id,
            "verified": is_verified
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")
