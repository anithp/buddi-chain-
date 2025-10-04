#!/usr/bin/env python3
"""Script to deploy smart contracts to æternity blockchain."""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.tokenization import TokenizationService
from app.core.config import settings


async def deploy_contracts():
    """Deploy AnchorRegistry and AccessNFT contracts."""
    print("🚀 Deploying smart contracts to æternity blockchain...")
    print(f"Network: {settings.aeternity_network_id}")
    print(f"Node URL: {settings.aeternity_node_url}")
    
    if not settings.aeternity_private_key:
        print("❌ Error: Aeternity private key not configured!")
        print("Please set AETERNITY_PRIVATE_KEY in your environment or .env file")
        sys.exit(1)
    
    try:
        tokenization_service = TokenizationService()
        
        # Deploy contracts
        anchor_registry_address, access_nft_address = await tokenization_service.deploy_contracts()
        
        print("✅ Contracts deployed successfully!")
        print(f"AnchorRegistry Address: {anchor_registry_address}")
        print(f"AccessNFT Address: {access_nft_address}")
        
        # Save addresses to file for reference
        with open("contract_addresses.txt", "w") as f:
            f.write(f"AnchorRegistry: {anchor_registry_address}\n")
            f.write(f"AccessNFT: {access_nft_address}\n")
        
        print("📝 Contract addresses saved to contract_addresses.txt")
        
    except Exception as e:
        print(f"❌ Contract deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(deploy_contracts())
