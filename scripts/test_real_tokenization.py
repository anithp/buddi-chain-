#!/usr/bin/env python3
"""Script to test real æternity blockchain tokenization."""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.real_tokenization import RealTokenizationService
from app.core.config import settings

async def test_real_tokenization():
    """Test real æternity blockchain tokenization."""
    print("🚀 Testing Real æternity Blockchain Tokenization")
    print("=" * 60)
    
    # Check if private key is configured
    if not settings.aeternity_private_key:
        print("❌ AETERNITY_PRIVATE_KEY not configured in .env file")
        print("   Please add your æternity private key to .env file:")
        print("   AETERNITY_PRIVATE_KEY=your_private_key_here")
        return False
    
    try:
        # Initialize tokenization service
        print("🔧 Initializing æternity tokenization service...")
        tokenization_service = RealTokenizationService()
        
        # Test connection to æternity node
        print(f"🌐 Connecting to æternity node: {settings.aeternity_node_url}")
        print(f"🔗 Network: {settings.aeternity_network_id}")
        
        # Create test conversation data
        test_conversation = {
            "conversation_id": "test_conv_001",
            "summary": {
                "text": "This is a test conversation for æternity blockchain tokenization.",
                "content": "Test conversation content",
                "title": "Test Conversation",
                "emoji": "🧪",
                "category": "test"
            },
            "actions": [
                {"type": "test_action", "description": "Test action item"}
            ],
            "conversation_metadata": {
                "buddi_id": "test_conv_001",
                "user_id": "test_user",
                "created_at": datetime.utcnow().isoformat(),
                "language": "en",
                "source": "test"
            },
            "fetched_at": datetime.utcnow().isoformat()
        }
        
        print("📝 Test conversation data:")
        print(json.dumps(test_conversation, indent=2))
        
        # Deploy contracts
        print("\n🚀 Deploying smart contracts...")
        anchor_registry_address, access_nft_address = await tokenization_service.deploy_contracts()
        
        print(f"✅ Contracts deployed successfully!")
        print(f"   AnchorRegistry: {anchor_registry_address}")
        print(f"   AccessNFT: {access_nft_address}")
        
        # Tokenize conversation
        print("\n🔗 Tokenizing conversation...")
        tokenization_result = await tokenization_service.tokenize_conversation(
            conversation_data=test_conversation,
            user_wallet=tokenization_service.account.get_address(),
            token_uri="https://buddi.ai/memory/test_conv_001"
        )
        
        print("✅ Tokenization completed successfully!")
        print("📊 Tokenization Results:")
        for key, value in tokenization_result.items():
            print(f"   {key}: {value}")
        
        # Verify anchor
        print("\n🔍 Verifying anchor...")
        is_verified = await tokenization_service.verify_anchor(
            anchor_id=tokenization_result["anchor_id"],
            merkle_root=tokenization_result["merkle_root"]
        )
        
        if is_verified:
            print("✅ Anchor verification successful!")
        else:
            print("❌ Anchor verification failed!")
        
        # Get token owner
        print("\n👤 Getting token owner...")
        owner = await tokenization_service.get_token_owner(
            token_id=tokenization_result["token_id"]
        )
        
        if owner:
            print(f"✅ Token owner: {owner}")
        else:
            print("❌ Failed to get token owner")
        
        print("\n🎉 Real æternity tokenization test completed successfully!")
        print("\nNext steps:")
        print("1. Update your tokenization service to use RealTokenizationService")
        print("2. Deploy to æternity mainnet for production")
        print("3. Set up proper error handling and retry logic")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during real tokenization test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🧪 æternity Real Tokenization Test")
    print("=" * 40)
    
    # Check if æternity SDK is installed
    try:
        import aeternity
        print("✅ æternity SDK is available")
    except ImportError:
        print("❌ æternity SDK not found. Please run install_aeternity_sdk.py first")
        return False
    
    # Run the test
    success = asyncio.run(test_real_tokenization())
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
