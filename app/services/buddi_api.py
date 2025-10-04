"""Service for fetching data from the Buddi API."""

import json
import os
from typing import Dict, List, Optional
import requests
from datetime import datetime
from app.core.config import settings


class BuddiAPIService:
    """Service for interacting with the Buddi API."""
    
    def __init__(self):
        self.base_url = settings.buddi_api_base_url
        self.api_key = settings.buddi_api_key
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        } if self.api_key else {"Content-Type": "application/json"}
    
    async def fetch_conversation_summaries(self, user_id: str = None, limit: int = 100) -> List[Dict]:
        """
        Fetch conversation summaries (memories) from Buddi API.
        
        Args:
            user_id: Optional user ID (not used in current API)
            limit: Maximum number of summaries to fetch
            
        Returns:
            List of conversation summary dictionaries
        """
        try:
            # Use the get_memories endpoint
            url = f"{self.base_url}/get_memories"
            params = {
                "date": "2025-08-10",  # You can make this dynamic
                "limit": limit
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            # The API might return data in different formats, let's handle it
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'memories' in data:
                return data['memories']
            elif isinstance(data, dict) and 'data' in data:
                return data['data']
            else:
                return [data] if data else []
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching conversation summaries: {e}")
            return []
    
    async def fetch_conversation_details(self, conversation_id: str) -> Optional[Dict]:
        """
        Fetch detailed conversation data from Buddi API.
        Since Buddi API returns memories directly, we'll use the conversation_id as a filter.
        
        Args:
            conversation_id: The conversation ID to fetch
            
        Returns:
            Dictionary containing conversation details or None if not found
        """
        try:
            # For now, we'll fetch all memories and filter by conversation_id
            # In a real implementation, you might have a specific endpoint for individual conversations
            url = f"{self.base_url}/get_memories"
            params = {
                "date": "2025-08-10",  # You can make this dynamic
                "conversation_id": conversation_id
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, list):
                memory_data = data[0] if data else {}
            elif isinstance(data, dict) and 'memories' in data:
                memory_data = data['memories'][0] if data['memories'] else {}
            elif isinstance(data, dict) and 'data' in data:
                memory_data = data['data'][0] if data['data'] else {}
            else:
                memory_data = data
            
            if not memory_data:
                return None
            
            # Transform Buddi memory data to our expected format
            return {
                "conversation_id": conversation_id,
                "summary": {
                    "text": memory_data.get("content", ""),
                    "content": memory_data.get("content", "")
                },
                "actions": memory_data.get("actions", []),
                "conversation_metadata": {
                    "user_id": memory_data.get("user_id", "unknown"),
                    "created_at": memory_data.get("created_at", ""),
                    "memory_type": memory_data.get("type", ""),
                    "tags": memory_data.get("tags", [])
                },
                "fetched_at": datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching conversation details for {conversation_id}: {e}")
            return None
    
    def save_raw_data(self, data: Dict, filename: str) -> str:
        """
        Save raw API data to the data/raw directory.
        
        Args:
            data: The data to save
            filename: The filename to save as
            
        Returns:
            Path to the saved file
        """
        os.makedirs("data/raw", exist_ok=True)
        filepath = f"data/raw/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filepath
    
    async def fetch_and_save_conversations(self, user_id: str, limit: int = 100) -> List[str]:
        """
        Fetch conversations and save them as raw data files.
        
        Args:
            user_id: The user ID to fetch conversations for
            limit: Maximum number of conversations to fetch
            
        Returns:
            List of file paths where data was saved
        """
        summaries = await self.fetch_conversation_summaries(user_id, limit)
        saved_files = []
        
        for summary in summaries:
            conversation_id = summary.get("conversation_id")
            if conversation_id:
                details = await self.fetch_conversation_details(conversation_id)
                if details:
                    filename = f"conversation_{conversation_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                    filepath = self.save_raw_data(details, filename)
                    saved_files.append(filepath)
        
        return saved_files
