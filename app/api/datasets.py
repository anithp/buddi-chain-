"""API routes for dataset management and export."""

import json
import os
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import pandas as pd

from app.db.database import get_db
from app.db.models import Conversation, Dataset

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


class DatasetCreateRequest(BaseModel):
    """Request model for creating a dataset."""
    name: str
    description: Optional[str] = None
    conversation_ids: Optional[List[int]] = None
    filters: Optional[dict] = None
    quality_threshold: float = 0.5
    export_format: str = "json"


class DatasetResponse(BaseModel):
    """Response model for dataset data."""
    id: int
    name: str
    description: Optional[str]
    total_conversations: int
    avg_sentiment: Optional[float]
    avg_quality_score: Optional[float]
    export_format: str
    is_ready: bool
    created_at: str


class ExportRequest(BaseModel):
    """Request model for exporting a dataset."""
    dataset_id: int
    format: str = "json"  # json, csv, parquet


@router.get("/", response_model=List[DatasetResponse])
async def get_datasets(
    skip: int = 0,
    limit: int = 100,
    is_ready: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get list of datasets."""
    query = db.query(Dataset)
    
    if is_ready is not None:
        query = query.filter(Dataset.is_ready == is_ready)
    
    datasets = query.offset(skip).limit(limit).all()
    
    return [
        DatasetResponse(
            id=dataset.id,
            name=dataset.name,
            description=dataset.description,
            total_conversations=dataset.total_conversations,
            avg_sentiment=dataset.avg_sentiment,
            avg_quality_score=dataset.avg_quality_score,
            export_format=dataset.export_format,
            is_ready=dataset.is_ready,
            created_at=dataset.created_at.isoformat()
        )
        for dataset in datasets
    ]


@router.post("/", response_model=DatasetResponse)
async def create_dataset(
    request: DatasetCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new dataset."""
    try:
        # Apply filters to get conversations
        query = db.query(Conversation).filter(Conversation.is_processed == True)
        
        if request.conversation_ids:
            query = query.filter(Conversation.id.in_(request.conversation_ids))
        
        if request.filters:
            if "user_id" in request.filters:
                query = query.filter(Conversation.user_id == request.filters["user_id"])
            
            if "sentiment_label" in request.filters:
                query = query.filter(Conversation.sentiment_label == request.filters["sentiment_label"])
            
            if "min_quality_score" in request.filters:
                query = query.filter(Conversation.quality_score >= request.filters["min_quality_score"])
        
        # Apply quality threshold
        query = query.filter(Conversation.quality_score >= request.quality_threshold)
        
        conversations = query.all()
        conversation_ids = [conv.id for conv in conversations]
        
        # Calculate statistics
        avg_sentiment = sum(conv.sentiment for conv in conversations if conv.sentiment) / len(conversations) if conversations else 0
        avg_quality_score = sum(conv.quality_score for conv in conversations if conv.quality_score) / len(conversations) if conversations else 0
        
        # Create dataset
        dataset = Dataset(
            name=request.name,
            description=request.description,
            conversation_ids=json.dumps(conversation_ids),
            filters=json.dumps(request.filters or {}),
            quality_threshold=request.quality_threshold,
            export_format=request.export_format,
            total_conversations=len(conversations),
            avg_sentiment=avg_sentiment,
            avg_quality_score=avg_quality_score,
            is_ready=True
        )
        
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        
        # Schedule export in background
        background_tasks.add_task(export_dataset, dataset.id, db)
        
        return DatasetResponse(
            id=dataset.id,
            name=dataset.name,
            description=dataset.description,
            total_conversations=dataset.total_conversations,
            avg_sentiment=dataset.avg_sentiment,
            avg_quality_score=dataset.avg_quality_score,
            export_format=dataset.export_format,
            is_ready=dataset.is_ready,
            created_at=dataset.created_at.isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create dataset: {str(e)}")


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Get a specific dataset by ID."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    return DatasetResponse(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        total_conversations=dataset.total_conversations,
        avg_sentiment=dataset.avg_sentiment,
        avg_quality_score=dataset.avg_quality_score,
        export_format=dataset.export_format,
        is_ready=dataset.is_ready,
        created_at=dataset.created_at.isoformat()
    )


@router.post("/{dataset_id}/export")
async def export_dataset_endpoint(
    dataset_id: int,
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Export a dataset to a file."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    background_tasks.add_task(export_dataset, dataset_id, db, request.format)
    
    return {"message": "Export started", "dataset_id": dataset_id}


@router.get("/{dataset_id}/download")
async def download_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Download a dataset file."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if not dataset.is_ready or not dataset.file_path:
        raise HTTPException(status_code=400, detail="Dataset not ready for download")
    
    if not os.path.exists(dataset.file_path):
        raise HTTPException(status_code=404, detail="Dataset file not found")
    
    return {"file_path": dataset.file_path, "file_size": dataset.file_size}


async def export_dataset(dataset_id: int, db: Session, export_format: str = "json"):
    """Background task to export dataset."""
    try:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            return
        
        # Get conversations
        conversation_ids = json.loads(dataset.conversation_ids)
        conversations = db.query(Conversation).filter(Conversation.id.in_(conversation_ids)).all()
        
        # Prepare data for export
        export_data = []
        for conv in conversations:
            export_data.append({
                "id": conv.id,
                "user_id": conv.user_id,
                "anchor_id": conv.anchor_id,
                "token_id": conv.token_id,
                "summary": json.loads(conv.summary),
                "actions": json.loads(conv.actions),
                "conversation_metadata": json.loads(conv.conversation_metadata),
                "sentiment": conv.sentiment,
                "sentiment_label": conv.sentiment_label,
                "topics": json.loads(conv.topics) if conv.topics else [],
                "keywords": json.loads(conv.keywords) if conv.keywords else [],
                "quality_score": conv.quality_score,
                "engagement_score": conv.engagement_score,
                "merkle_root": conv.merkle_root,
                "created_at": conv.created_at.isoformat()
            })
        
        # Create export directory
        os.makedirs("data/processed", exist_ok=True)
        
        # Export based on format
        filename = f"dataset_{dataset_id}_{dataset.name.replace(' ', '_')}.{export_format}"
        filepath = f"data/processed/{filename}"
        
        if export_format == "json":
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
        
        elif export_format == "csv":
            df = pd.DataFrame(export_data)
            df.to_csv(filepath, index=False)
        
        elif export_format == "parquet":
            df = pd.DataFrame(export_data)
            df.to_parquet(filepath, index=False)
        
        # Update dataset
        from sqlalchemy.sql import func
        dataset.file_path = filepath
        dataset.file_size = os.path.getsize(filepath)
        dataset.exported_at = func.now()
        dataset.is_ready = True
        
        db.commit()
        
    except Exception as e:
        print(f"Export failed for dataset {dataset_id}: {e}")
        # Update dataset to mark as failed
        dataset.is_ready = False
        db.commit()
