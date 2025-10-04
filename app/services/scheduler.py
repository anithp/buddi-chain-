"""Background scheduler for periodic tasks."""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List
from app.db.database import SessionLocal
from app.db.models import Conversation
from app.services.buddi_api import BuddiAPIService
from app.services.analytics import AnalyticsService
from app.services.tokenization import TokenizationService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConversationScheduler:
    """Scheduler for periodic conversation fetching and processing."""
    
    def __init__(self):
        self.buddi_service = BuddiAPIService()
        self.analytics_service = AnalyticsService()
        self.tokenization_service = TokenizationService()
        self.is_running = False
        self.last_fetch_time = None
        self.fetch_interval_hours = 2  # Fetch every 2 hours
        self.max_conversations_per_fetch = 50
        
    async def start_scheduler(self):
        """Start the background scheduler."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
            
        self.is_running = True
        logger.info("🚀 Starting conversation scheduler...")
        logger.info(f"⏰ Fetch interval: {self.fetch_interval_hours} hours")
        logger.info(f"📊 Max conversations per fetch: {self.max_conversations_per_fetch}")
        
        while self.is_running:
            try:
                await self.fetch_and_process_new_conversations()
                await asyncio.sleep(self.fetch_interval_hours * 3600)  # Convert hours to seconds
            except Exception as e:
                logger.error(f"❌ Error in scheduler loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    async def stop_scheduler(self):
        """Stop the background scheduler."""
        self.is_running = False
        logger.info("🛑 Stopping conversation scheduler...")
    
    async def fetch_and_process_new_conversations(self):
        """Fetch and process new conversations from Buddi API."""
        try:
            logger.info("🔄 Starting periodic conversation fetch...")
            
            # Check if we should fetch (respect rate limits)
            if self.last_fetch_time:
                time_since_last_fetch = datetime.utcnow() - self.last_fetch_time
                if time_since_last_fetch.total_seconds() < 3600:  # Don't fetch more than once per hour
                    logger.info("⏳ Rate limiting: Skipping fetch (less than 1 hour since last fetch)")
                    return
            
            # Get existing conversation IDs to avoid duplicates
            db = SessionLocal()
            try:
                existing_ids = set()
                existing_conversations = db.query(Conversation).all()
                for conv in existing_conversations:
                    # Extract Buddi ID from conversation metadata
                    try:
                        metadata = json.loads(conv.conversation_metadata)
                        if 'buddi_id' in metadata:
                            existing_ids.add(metadata['buddi_id'])
                    except:
                        pass
                
                logger.info(f"📋 Found {len(existing_ids)} existing conversations in database")
                
            finally:
                db.close()
            
            # Fetch conversations from Buddi API
            logger.info("📡 Fetching conversations from Buddi API...")
            conversations_data = await self.buddi_service.fetch_conversation_summaries(
                limit=self.max_conversations_per_fetch
            )
            
            if not conversations_data:
                logger.info("ℹ️  No conversations found in API response")
                self.last_fetch_time = datetime.utcnow()
                return
            
            logger.info(f"✅ Found {len(conversations_data)} conversations from API")
            
            # Filter out existing conversations
            new_conversations = []
            for conv_data in conversations_data:
                buddi_id = conv_data.get("id")
                if buddi_id and buddi_id not in existing_ids:
                    new_conversations.append(conv_data)
                else:
                    logger.debug(f"⏭️  Skipping existing conversation: {buddi_id}")
            
            if not new_conversations:
                logger.info("ℹ️  No new conversations found (all already in database)")
                self.last_fetch_time = datetime.utcnow()
                return
            
            logger.info(f"🆕 Found {len(new_conversations)} new conversations to process")
            
            # Process new conversations
            await self.process_conversations(new_conversations)
            
            self.last_fetch_time = datetime.utcnow()
            logger.info(f"✅ Periodic fetch completed. Processed {len(new_conversations)} new conversations")
            
        except Exception as e:
            logger.error(f"❌ Error in fetch_and_process_new_conversations: {e}")
            raise
    
    async def process_conversations(self, conversations_data: List[dict]):
        """Process a list of conversations and save to database."""
        db = SessionLocal()
        processed_count = 0
        error_count = 0
        
        try:
            # Ensure mock contracts are deployed once
            if not self.tokenization_service.anchor_registry_contract:
                await self.tokenization_service.deploy_contracts()
            
            for i, memory_data in enumerate(conversations_data):
                try:
                    buddi_id = memory_data.get("id", f"buddi_{i}")
                    logger.info(f"📝 Processing conversation {i+1}/{len(conversations_data)}: {buddi_id}")
                    
                    # Transform Buddi memory data to our expected format
                    conversation_data = {
                        "conversation_id": buddi_id,
                        "summary": {
                            "text": memory_data.get("structured", {}).get("overview", ""),
                            "content": memory_data.get("structured", {}).get("overview", ""),
                            "title": memory_data.get("structured", {}).get("title", ""),
                            "emoji": memory_data.get("structured", {}).get("emoji", ""),
                            "category": memory_data.get("structured", {}).get("category", "")
                        },
                        "actions": memory_data.get("structured", {}).get("action_items", []),
                        "conversation_metadata": {
                            "buddi_id": buddi_id,
                            "user_id": "buddi_user",
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
                    analytics = self.analytics_service.analyze_conversation(conversation_data)
                    
                    # Tokenize conversation (mock blockchain)
                    tokenization_result = await self.tokenization_service.tokenize_conversation(
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
                        token_uri=f"https://buddi.ai/memory/{buddi_id}",
                        contract_address=tokenization_result["access_nft_address"],
                        is_processed=True
                    )
                    
                    db.add(conversation)
                    processed_count += 1
                    
                    logger.info(f"✅ Processed conversation {i+1}: {analytics['sentiment_label']} sentiment, quality: {analytics['quality_score']:.2f}")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing conversation {i+1}: {e}")
                    error_count += 1
                    continue
            
            # Commit all changes
            db.commit()
            
            logger.info(f"🎉 Batch processing completed!")
            logger.info(f"✅ Successfully processed: {processed_count} conversations")
            logger.info(f"❌ Errors: {error_count} conversations")
            
        except Exception as e:
            logger.error(f"❌ Error in process_conversations: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def run_manual_fetch(self):
        """Manually trigger a conversation fetch (for testing or on-demand)."""
        logger.info("🔧 Manual fetch triggered")
        await self.fetch_and_process_new_conversations()
    
    def get_status(self):
        """Get current scheduler status."""
        return {
            "is_running": self.is_running,
            "last_fetch_time": self.last_fetch_time.isoformat() if self.last_fetch_time else None,
            "fetch_interval_hours": self.fetch_interval_hours,
            "max_conversations_per_fetch": self.max_conversations_per_fetch
        }


# Global scheduler instance
scheduler = ConversationScheduler()
