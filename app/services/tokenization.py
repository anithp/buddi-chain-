"""Service for tokenizing conversations (mock implementation for PoC)."""

import hashlib
import json
import uuid
from typing import Dict, Optional, Tuple
from app.core.config import settings


class MockContract:
    """Mock contract class for PoC demonstration."""
    
    def __init__(self, contract_id: str):
        self.contract_id = contract_id
        self.anchor_count = 0
        self.token_count = 0
        self.anchors = {}
        self.tokens = {}
        # Use a base ID to ensure uniqueness across instances
        self.base_id = int(contract_id[-8:], 16) if len(contract_id) > 8 else 1000
    
    def anchor(self, merkle_root: str, manifest: str, policy: str, storage_hint: str, options: dict = None):
        """Mock anchor method."""
        self.anchor_count += 1
        anchor_id = self.base_id + self.anchor_count
        self.anchors[anchor_id] = {
            "merkle_root": merkle_root,
            "manifest": manifest,
            "policy": policy,
            "storage_hint": storage_hint
        }
        
        class MockResult:
            def __init__(self, value):
                self.return_value = value
        
        return MockResult(anchor_id)
    
    def mint(self, to: str, anchor_id: int, token_uri: str, options: dict = None):
        """Mock mint method."""
        self.token_count += 1
        token_id = self.base_id + self.token_count
        self.tokens[token_id] = {
            "owner": to,
            "anchor_id": anchor_id,
            "token_uri": token_uri
        }
        
        class MockResult:
            def __init__(self, value):
                self.return_value = value
        
        return MockResult(token_id)
    
    def verify_anchor(self, anchor_id: int, merkle_root: str, options: dict = None):
        """Mock verify_anchor method."""
        if anchor_id in self.anchors:
            stored_root = self.anchors[anchor_id]["merkle_root"]
            is_valid = stored_root == merkle_root
        else:
            is_valid = False
        
        class MockResult:
            def __init__(self, value):
                self.return_value = value
        
        return MockResult(is_valid)
    
    def owner_of(self, token_id: int, options: dict = None):
        """Mock owner_of method."""
        if token_id in self.tokens:
            owner = self.tokens[token_id]["owner"]
        else:
            owner = None
        
        class MockResult:
            def __init__(self, value):
                self.return_value = value
        
        return MockResult(owner)


class TokenizationService:
    """Service for tokenizing conversations (mock implementation for PoC)."""
    
    def __init__(self):
        self.network_id = settings.aeternity_network_id
        self.node_url = settings.aeternity_node_url
        self.private_key = settings.aeternity_private_key
        
        # Mock contract addresses (in real implementation, these would be deployed)
        self.anchor_registry_contract = None
        self.access_nft_contract = None
    
    async def deploy_contracts(self) -> Tuple[str, str]:
        """
        Deploy the AnchorRegistry and AccessNFT contracts (mock implementation).
        
        Returns:
            Tuple of (anchor_registry_address, access_nft_address)
        """
        try:
            # Mock contract deployment - generate fake addresses
            anchor_registry_address = f"ct_{uuid.uuid4().hex[:32]}"
            access_nft_address = f"ct_{uuid.uuid4().hex[:32]}"
            
            # Set mock contract instances
            self.anchor_registry_contract = MockContract(anchor_registry_address)
            self.access_nft_contract = MockContract(access_nft_address)
            
            print(f"✅ Mock contracts deployed:")
            print(f"   AnchorRegistry: {anchor_registry_address}")
            print(f"   AccessNFT: {access_nft_address}")
            
            return anchor_registry_address, access_nft_address
            
        except Exception as e:
            raise Exception(f"Failed to deploy contracts: {e}")
    
    def calculate_merkle_root(self, conversation_data: Dict) -> str:
        """
        Calculate Merkle root hash for conversation data.
        
        Args:
            conversation_data: Dictionary containing conversation data
            
        Returns:
            Hex string of the Merkle root hash
        """
        # Convert conversation data to JSON string
        json_str = json.dumps(conversation_data, sort_keys=True)
        
        # Calculate SHA256 hash
        hash_obj = hashlib.sha256(json_str.encode('utf-8'))
        return hash_obj.hexdigest()
    
    async def tokenize_conversation(
        self,
        conversation_data: Dict,
        user_wallet: str,
        token_uri: str = ""
    ) -> Dict[str, str]:
        """
        Tokenize a conversation by anchoring it and minting an NFT (mock implementation).
        
        Args:
            conversation_data: Dictionary containing conversation data
            user_wallet: The wallet address to mint the NFT to
            token_uri: Optional URI for token metadata
            
        Returns:
            Dictionary containing anchor_id, token_id, and merkle_root
        """
        try:
            # Calculate Merkle root
            merkle_root = self.calculate_merkle_root(conversation_data)
            
            # Create manifest and policy
            manifest = json.dumps({
                "type": "conversation_summary",
                "version": "1.0",
                "created_at": conversation_data.get("fetched_at", ""),
                "conversation_id": conversation_data.get("conversation_id", "")
            })
            
            policy = json.dumps({
                "access_control": "nft_ownership",
                "data_retention": "permanent",
                "export_allowed": True
            })
            
            storage_hint = f"conversation_{conversation_data.get('conversation_id', 'unknown')}"
            
            # Ensure contracts are deployed
            if not self.anchor_registry_contract:
                await self.deploy_contracts()
            
            # Anchor the data
            anchor_result = self.anchor_registry_contract.anchor(
                merkle_root=merkle_root,
                manifest=manifest,
                policy=policy,
                storage_hint=storage_hint
            )
            
            anchor_id = anchor_result.return_value
            
            # Mint NFT
            mint_result = self.access_nft_contract.mint(
                to=user_wallet,
                anchor_id=anchor_id,
                token_uri=token_uri
            )
            
            token_id = mint_result.return_value
            
            print(f"✅ Mock tokenization completed:")
            print(f"   Anchor ID: {anchor_id}")
            print(f"   Token ID: {token_id}")
            print(f"   Merkle Root: {merkle_root[:16]}...")
            
            return {
                "anchor_id": str(anchor_id),
                "token_id": str(token_id),
                "merkle_root": merkle_root,
                "anchor_registry_address": self.anchor_registry_contract.contract_id,
                "access_nft_address": self.access_nft_contract.contract_id
            }
            
        except Exception as e:
            raise Exception(f"Tokenization failed: {e}")
    
    async def verify_conversation(self, anchor_id: int, merkle_root: str) -> bool:
        """
        Verify that a conversation is properly anchored (mock implementation).
        
        Args:
            anchor_id: The anchor ID to verify
            merkle_root: The expected Merkle root
            
        Returns:
            True if verification succeeds, False otherwise
        """
        try:
            if not self.anchor_registry_contract:
                return False
                
            result = self.anchor_registry_contract.verify_anchor(
                anchor_id=anchor_id,
                merkle_root=merkle_root
            )
            return result.return_value
        except Exception as e:
            print(f"Verification failed: {e}")
            return False
    
    def get_token_owner(self, token_id: int) -> Optional[str]:
        """
        Get the owner of a specific token (mock implementation).
        
        Args:
            token_id: The token ID to query
            
        Returns:
            Wallet address of the token owner, or None if not found
        """
        try:
            if not self.access_nft_contract:
                return None
                
            result = self.access_nft_contract.owner_of(token_id=token_id)
            return result.return_value
        except Exception as e:
            print(f"Failed to get token owner: {e}")
            return None
