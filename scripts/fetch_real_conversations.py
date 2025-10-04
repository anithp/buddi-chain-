#!/usr/bin/env python3
"""Script to fetch real conversations from Buddi API and populate the database."""

import sys
import os
import asyncio
import json
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import Conversation
from app.services.buddi_api import BuddiAPIService
from app.services.analytics import AnalyticsService
from app.services.tokenization import TokenizationService


async def fetch_and_process_conversations():
    """Fetch real conversations from Buddi API and process them."""
    print("🚀 Fetching real conversations from Buddi API...")
    
    # Initialize services
    buddi_service = BuddiAPIService()
    analytics_service = AnalyticsService()
    tokenization_service = TokenizationService()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Fetch conversations from Buddi API
        print("📡 Fetching conversations from Buddi API...")
        conversations_data = await buddi_service.fetch_conversation_summaries(limit=50)
        
        if not conversations_data:
            print("❌ No conversations found in API response")
            return
        
        print(f"✅ Found {len(conversations_data)} conversations")
        
        processed_count = 0
        error_count = 0
        
        for i, memory_data in enumerate(conversations_data):
            try:
                print(f"📝 Processing conversation {i+1}/{len(conversations_data)}: {memory_data.get('id', 'unknown')}")
                
                # Transform Buddi memory data to our expected format
                conversation_data = {
                    "conversation_id": memory_data.get("id", f"buddi_{i}"),
                    "summary": {
                        "text": memory_data.get("structured", {}).get("overview", ""),
                        "content": memory_data.get("structured", {}).get("overview", ""),
                        "title": memory_data.get("structured", {}).get("title", ""),
                        "emoji": memory_data.get("structured", {}).get("emoji", ""),
                        "category": memory_data.get("structured", {}).get("category", "")
                    },
                    "actions": memory_data.get("structured", {}).get("action_items", []),
                    "conversation_metadata": {
                        "user_id": "buddi_user",  # You might want to extract this from the API
                        "created_at": memory_data.get("created_at", ""),
                        "finished_at": memory_data.get("finished_at", ""),
                        "language": memory_data.get("language", "en"),
                        "source": memory_data.get("source", ""),
                        "visibility": memory_data.get("visibility", ""),
                        "status": memory_data.get("status", ""),
                        "discarded": memory_data.get("discarded", False),
                        "transcript_segments": memory_data.get("transcript_segments", []),
                        "plugins_results": memory_data.get("plugins_results", [])
                    },
                    "fetched_at": datetime.utcnow().isoformat()
                }
                
                # Perform analytics
                print(f"🔍 Analyzing conversation {i+1}...")
                analytics = analytics_service.analyze_conversation(conversation_data)
                
                # Tokenize conversation (mock blockchain)
                print(f"⛓️  Tokenizing conversation {i+1}...")
                tokenization_result = await tokenization_service.tokenize_conversation(
                    conversation_data, "buddi_user"
                )
                
                # Save to database
                conversation = Conversation(
                    user_id="buddi_user",
                    anchor_id=tokenization_result["anchor_id"],
                    token_id=tokenization_result["token_id"],
                    summary=json.dumps(conversation_data["summary"]),
                    actions=json.dumps(conversation_data["actions"]),
                    conversation_metadata=json.dumps(conversation_data["conversation_metadata"]),
                    sentiment=analytics["sentiment"],
                    sentiment_label=analytics["sentiment_label"],
                    topics=json.dumps(analytics["topics"]),
                    keywords=json.dumps(analytics["keywords"]),
                    quality_score=analytics["quality_score"],
                    engagement_score=analytics["engagement_score"],
                    merkle_root=tokenization_result["merkle_root"],
                    token_uri=f"https://buddi.ai/memory/{conversation_data['conversation_id']}",
                    contract_address=tokenization_result["access_nft_address"],
                    is_processed=True
                )
                
                db.add(conversation)
                processed_count += 1
                
                print(f"✅ Processed conversation {i+1}: {analytics['sentiment_label']} sentiment, quality: {analytics['quality_score']:.2f}")
                
            except Exception as e:
                print(f"❌ Error processing conversation {i+1}: {e}")
                error_count += 1
                continue
        
        # Commit all changes
        db.commit()
        
        print(f"\n🎉 Processing completed!")
        print(f"✅ Successfully processed: {processed_count} conversations")
        print(f"❌ Errors: {error_count} conversations")
        print(f"📊 Total in database: {db.query(Conversation).count()} conversations")
        
    except Exception as e:
        print(f"❌ Error in main process: {e}")
        db.rollback()
    finally:
        db.close()


async def main():
    """Main function."""
    print("🎯 Buddi Tokenization PoC - Real Data Fetcher")
    print("=" * 50)
    
    await fetch_and_process_conversations()
    
    print("\n🌐 You can now view the conversations at:")
    print("   - Dashboard: http://localhost:8000")
    print("   - API: http://localhost:8000/conversations/")
    print("   - Docs: http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(main())
