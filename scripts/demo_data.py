#!/usr/bin/env python3
"""Script to create demo data for testing the system."""

import sys
import os
import json
import asyncio
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import Conversation
from app.services.analytics import AnalyticsService


def create_demo_conversations():
    """Create demo conversation data for testing."""
    print("📝 Creating demo conversation data...")
    
    demo_conversations = [
        {
            "conversation_id": "demo_001",
            "summary": {
                "text": "User discussed API integration issues with our new payment system. They mentioned problems with webhook handling and error responses. The conversation covered troubleshooting steps and potential solutions.",
                "content": "API integration discussion focusing on payment system webhooks and error handling."
            },
            "actions": [
                {"type": "api_call", "endpoint": "/payments/webhook", "status": "failed"},
                {"type": "error_log", "message": "Webhook timeout after 30 seconds"},
                {"type": "retry", "attempt": 1, "status": "pending"}
            ],
            "conversation_metadata": {
                "user_id": "user_123",
                "session_duration": 1800,
                "language": "en",
                "platform": "web"
            }
        },
        {
            "conversation_id": "demo_002",
            "summary": {
                "text": "Customer support conversation about account billing. User was confused about recent charges and wanted to understand their subscription plan. We provided detailed billing breakdown and offered to adjust their plan.",
                "content": "Billing inquiry and subscription plan discussion with customer support."
            },
            "actions": [
                {"type": "billing_lookup", "account_id": "acc_456"},
                {"type": "plan_recommendation", "suggested_plan": "premium"},
                {"type": "follow_up", "scheduled": "2024-01-15"}
            ],
            "conversation_metadata": {
                "user_id": "user_456",
                "session_duration": 2400,
                "language": "en",
                "platform": "mobile"
            }
        },
        {
            "conversation_id": "demo_003",
            "summary": {
                "text": "Technical discussion about implementing OAuth 2.0 authentication. Developer asked about best practices for token refresh and security considerations. We provided code examples and security guidelines.",
                "content": "OAuth 2.0 implementation guidance and security best practices discussion."
            },
            "actions": [
                {"type": "code_review", "file": "auth.js"},
                {"type": "security_audit", "findings": 2},
                {"type": "documentation", "created": "oauth_guide.md"}
            ],
            "conversation_metadata": {
                "user_id": "user_789",
                "session_duration": 3600,
                "language": "en",
                "platform": "desktop"
            }
        }
    ]
    
    # Save demo data
    os.makedirs("data/raw", exist_ok=True)
    for conv in demo_conversations:
        filename = f"conversation_{conv['conversation_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = f"data/raw/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(conv, f, indent=2)
        
        print(f"✅ Created demo data: {filename}")
    
    return demo_conversations


async def analyze_demo_conversations(conversations):
    """Analyze demo conversations and save to database."""
    print("🔍 Analyzing demo conversations...")
    
    analytics_service = AnalyticsService()
    db = SessionLocal()
    
    try:
        for conv_data in conversations:
            # Perform analytics
            analytics = analytics_service.analyze_conversation(conv_data)
            
            # Create conversation record (without blockchain data for demo)
            conversation = Conversation(
                user_id=conv_data["conversation_metadata"]["user_id"],
                anchor_id=f"demo_anchor_{conv_data['conversation_id']}",
                token_id=f"demo_token_{conv_data['conversation_id']}",
                summary=json.dumps(conv_data["summary"]),
                actions=json.dumps(conv_data["actions"]),
                conversation_metadata=json.dumps(conv_data["conversation_metadata"]),
                sentiment=analytics["sentiment"],
                sentiment_label=analytics["sentiment_label"],
                topics=json.dumps(analytics["topics"]),
                keywords=json.dumps(analytics["keywords"]),
                quality_score=analytics["quality_score"],
                engagement_score=analytics["engagement_score"],
                merkle_root=f"demo_merkle_{conv_data['conversation_id']}",
                token_uri=f"https://demo.com/token/{conv_data['conversation_id']}",
                contract_address="demo_contract_address",
                is_processed=True
            )
            
            db.add(conversation)
        
        db.commit()
        print("✅ Demo conversations analyzed and saved to database!")
        
    except Exception as e:
        print(f"❌ Error analyzing conversations: {e}")
        db.rollback()
    finally:
        db.close()


async def main():
    """Main function to create and analyze demo data."""
    print("🎭 Buddi Tokenization PoC - Demo Data Creator")
    print("=" * 50)
    
    # Create demo conversations
    conversations = create_demo_conversations()
    
    # Analyze and save to database
    await analyze_demo_conversations(conversations)
    
    print("\n🎉 Demo data creation completed!")
    print("You can now:")
    print("- View conversations at http://localhost:8000/conversations")
    print("- Create datasets at http://localhost:8000/datasets")
    print("- Check the API documentation at http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(main())
