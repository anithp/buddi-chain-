#!/usr/bin/env python3
"""Script to create datasets from the fetched conversations."""

import sys
import os
import asyncio
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import Conversation, Dataset
from app.api.datasets import export_dataset


async def create_sample_datasets():
    """Create sample datasets from the conversations."""
    print("📊 Creating datasets from conversations...")
    
    db = SessionLocal()
    
    try:
        # Get all conversations
        conversations = db.query(Conversation).all()
        print(f"📝 Found {len(conversations)} conversations in database")
        
        if not conversations:
            print("❌ No conversations found. Please run fetch_real_conversations.py first.")
            return
        
        # Create different types of datasets
        datasets_to_create = [
            {
                "name": "High Quality Conversations",
                "description": "Conversations with quality score >= 0.8",
                "filters": {"min_quality_score": 0.8},
                "quality_threshold": 0.8
            },
            {
                "name": "Positive Sentiment Dataset",
                "description": "Conversations with positive sentiment",
                "filters": {"sentiment_label": "positive"},
                "quality_threshold": 0.5
            },
            {
                "name": "Technology Topics",
                "description": "Conversations related to technology topics",
                "filters": {"topics": "technology"},
                "quality_threshold": 0.6
            },
            {
                "name": "All Conversations",
                "description": "Complete dataset of all conversations",
                "filters": {},
                "quality_threshold": 0.0
            }
        ]
        
        created_datasets = []
        
        for dataset_config in datasets_to_create:
            print(f"\n🔨 Creating dataset: {dataset_config['name']}")
            
            # Apply filters to get conversations
            query = db.query(Conversation).filter(Conversation.is_processed == True)
            
            if "min_quality_score" in dataset_config["filters"]:
                query = query.filter(Conversation.quality_score >= dataset_config["filters"]["min_quality_score"])
            
            if "sentiment_label" in dataset_config["filters"]:
                query = query.filter(Conversation.sentiment_label == dataset_config["filters"]["sentiment_label"])
            
            # For topic filtering, we need to check the JSON content
            if "topics" in dataset_config["filters"]:
                target_topic = dataset_config["filters"]["topics"]
                # This is a simplified filter - in production you'd want more sophisticated topic matching
                conversations_with_topic = []
                for conv in query.all():
                    topics = json.loads(conv.topics) if conv.topics else []
                    if target_topic in topics:
                        conversations_with_topic.append(conv)
                query_results = conversations_with_topic
            else:
                query_results = query.all()
            
            # Apply quality threshold
            filtered_conversations = [conv for conv in query_results if conv.quality_score >= dataset_config["quality_threshold"]]
            
            print(f"   📊 Found {len(filtered_conversations)} conversations matching criteria")
            
            if not filtered_conversations:
                print(f"   ⚠️  No conversations found for {dataset_config['name']}, skipping...")
                continue
            
            # Calculate statistics
            avg_sentiment = sum(conv.sentiment for conv in filtered_conversations if conv.sentiment) / len(filtered_conversations)
            avg_quality_score = sum(conv.quality_score for conv in filtered_conversations if conv.quality_score) / len(filtered_conversations)
            
            # Create dataset
            dataset = Dataset(
                name=dataset_config["name"],
                description=dataset_config["description"],
                conversation_ids=json.dumps([conv.id for conv in filtered_conversations]),
                filters=json.dumps(dataset_config["filters"]),
                quality_threshold=dataset_config["quality_threshold"],
                export_format="json",
                total_conversations=len(filtered_conversations),
                avg_sentiment=avg_sentiment,
                avg_quality_score=avg_quality_score,
                is_ready=True
            )
            
            db.add(dataset)
            db.commit()
            db.refresh(dataset)
            
            created_datasets.append(dataset)
            
            print(f"   ✅ Created dataset ID {dataset.id}: {len(filtered_conversations)} conversations")
            print(f"   📈 Avg sentiment: {avg_sentiment:.2f}, Avg quality: {avg_quality_score:.2f}")
            
            # Export the dataset
            print(f"   📤 Exporting dataset...")
            await export_dataset(dataset.id, db, "json")
            print(f"   ✅ Dataset exported successfully")
        
        print(f"\n🎉 Dataset creation completed!")
        print(f"✅ Created {len(created_datasets)} datasets")
        
        # Show summary
        print(f"\n📊 Dataset Summary:")
        for dataset in created_datasets:
            print(f"   - {dataset.name}: {dataset.total_conversations} conversations")
            print(f"     Quality: {dataset.avg_quality_score:.2f}, Sentiment: {dataset.avg_sentiment:.2f}")
        
    except Exception as e:
        print(f"❌ Error creating datasets: {e}")
        db.rollback()
    finally:
        db.close()


async def main():
    """Main function."""
    print("🎯 Buddi Tokenization PoC - Dataset Creator")
    print("=" * 50)
    
    await create_sample_datasets()
    
    print("\n🌐 You can now view the datasets at:")
    print("   - Dashboard: http://localhost:8000")
    print("   - Datasets API: http://localhost:8000/datasets/")
    print("   - API Docs: http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(main())
