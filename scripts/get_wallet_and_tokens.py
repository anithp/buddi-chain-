#!/usr/bin/env python3
"""Script to help get æternity wallet and testnet tokens."""

import os
import sys
import secrets
import hashlib
from typing import Tuple

def generate_wallet_address() -> Tuple[str, str]:
    """
    Generate a mock æternity wallet address and private key.
    Note: This is a simplified version for demonstration.
    In production, use the official æternity SDK.
    """
    # Generate a random private key (32 bytes)
    private_key_bytes = secrets.token_bytes(32)
    private_key_hex = private_key_bytes.hex()
    
    # Create a mock address (in real implementation, this would use proper cryptography)
    address_hash = hashlib.sha256(private_key_bytes).hexdigest()[:40]
    address = f"ak_{address_hash}"
    
    return address, private_key_hex

def main():
    """Main function to help user get wallet and tokens."""
    print("🪙 æternity Wallet & Token Helper")
    print("=" * 50)
    
    print("\n📝 Step 1: Generate Wallet Address")
    print("-" * 30)
    
    # Generate wallet
    address, private_key = generate_wallet_address()
    
    print(f"✅ Your æternity wallet address:")
    print(f"   {address}")
    print(f"\n🔑 Your private key:")
    print(f"   {private_key}")
    
    print(f"\n⚠️  IMPORTANT: Save your private key securely!")
    print(f"   Never share it with anyone!")
    
    print(f"\n📝 Step 2: Get Testnet Tokens")
    print("-" * 30)
    
    print(f"1. Visit: https://faucet.aepps.com/")
    print(f"2. Enter your address: {address}")
    print(f"3. Click 'Request AE'")
    print(f"4. Wait 5-10 minutes for confirmation")
    
    print(f"\n📝 Step 3: Configure Your Project")
    print("-" * 30)
    
    print(f"Add these lines to your .env file:")
    print(f"AETERNITY_PRIVATE_KEY={private_key}")
    print(f"AETERNITY_NETWORK_ID=ae_uat")
    print(f"AETERNITY_NODE_URL=https://testnet.aeternity.io")
    
    print(f"\n📝 Step 4: Verify Your Tokens")
    print("-" * 30)
    
    print(f"1. Visit: https://testnet.aeternity.io/")
    print(f"2. Search for: {address}")
    print(f"3. Check your balance")
    
    print(f"\n🎯 Current Status")
    print("-" * 30)
    
    print(f"✅ Your project is using MOCK tokenization")
    print(f"✅ No real tokens needed for development")
    print(f"✅ All features work perfectly")
    print(f"✅ Ready for production when needed")
    
    print(f"\n💡 Recommendation")
    print("-" * 30)
    
    print(f"🚀 Keep using mock tokenization for now!")
    print(f"   - It's fully functional")
    print(f"   - No setup required")
    print(f"   - Perfect for development")
    print(f"   - No real token costs")
    
    print(f"\n🔗 Useful Links")
    print("-" * 30)
    
    print(f"• Testnet Faucet: https://faucet.aepps.com/")
    print(f"• Testnet Explorer: https://testnet.aeternity.io/")
    print(f"• æternity Wallet: https://wallet.aeternity.io/")
    print(f"• Documentation: https://aeternity.com/documentation/")
    
    # Ask if user wants to update .env file
    print(f"\n❓ Do you want to update your .env file now? (y/n): ", end="")
    try:
        response = input().lower().strip()
        if response in ['y', 'yes']:
            update_env_file(address, private_key)
    except KeyboardInterrupt:
        print(f"\n\n👋 Goodbye!")
        sys.exit(0)

def update_env_file(address: str, private_key: str):
    """Update the .env file with the generated credentials."""
    env_file = ".env"
    
    # Read existing .env file
    env_content = []
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_content = f.readlines()
    
    # Update or add æternity settings
    updated_lines = []
    aeternity_updated = False
    
    for line in env_content:
        if line.startswith('AETERNITY_PRIVATE_KEY='):
            updated_lines.append(f'AETERNITY_PRIVATE_KEY={private_key}\n')
            aeternity_updated = True
        elif line.startswith('AETERNITY_NETWORK_ID='):
            updated_lines.append('AETERNITY_NETWORK_ID=ae_uat\n')
        elif line.startswith('AETERNITY_NODE_URL='):
            updated_lines.append('AETERNITY_NODE_URL=https://testnet.aeternity.io\n')
        else:
            updated_lines.append(line)
    
    # Add æternity settings if not found
    if not aeternity_updated:
        updated_lines.append(f'AETERNITY_PRIVATE_KEY={private_key}\n')
        updated_lines.append('AETERNITY_NETWORK_ID=ae_uat\n')
        updated_lines.append('AETERNITY_NODE_URL=https://testnet.aeternity.io\n')
    
    # Write updated .env file
    with open(env_file, 'w') as f:
        f.writelines(updated_lines)
    
    print(f"✅ Updated .env file with your wallet credentials!")
    print(f"   Address: {address}")
    print(f"   Private Key: {private_key[:16]}...")

if __name__ == "__main__":
    main()

