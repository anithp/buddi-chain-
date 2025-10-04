#!/usr/bin/env python3
"""Script to test the real Buddi API and discover available endpoints."""

import sys
import os
import asyncio
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


async def test_buddi_api():
    """Test the Buddi API to discover available endpoints."""
    print("🔍 Testing Buddi AI API...")
    print(f"Base URL: {settings.buddi_api_base_url}")
    print(f"API Key: {settings.buddi_api_key[:10]}..." if settings.buddi_api_key else "No API key")
    
    headers = {
        "api-key": settings.buddi_api_key,
        "Content-Type": "application/json"
    }
    
    # Test different possible endpoints
    endpoints_to_test = [
        "/",
        "/conversations",
        "/conversations/",
        "/api/conversations",
        "/api/v1/conversations",
        "/users",
        "/users/",
        "/api/users",
        "/api/v1/users",
        "/health",
        "/status",
        "/api/status"
    ]
    
    print("\n📡 Testing endpoints...")
    for endpoint in endpoints_to_test:
        url = f"{settings.buddi_api_base_url}{endpoint}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"✅ {endpoint}: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    if isinstance(data, dict) and 'conversations' in data:
                        print(f"   Found conversations: {len(data['conversations'])}")
                except:
                    print(f"   Response: {response.text[:100]}...")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint}: {e}")
    
    # Test with different authentication methods
    print("\n🔐 Testing different auth methods...")
    auth_methods = [
        {"api-key": settings.buddi_api_key},
        {"Authorization": f"Bearer {settings.buddi_api_key}"},
        {"X-API-Key": settings.buddi_api_key},
        {"api_key": settings.buddi_api_key},
    ]
    
    for i, auth_header in enumerate(auth_methods):
        try:
            response = requests.get(settings.buddi_api_base_url, headers=auth_header, timeout=10)
            print(f"✅ Auth method {i+1}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Auth method {i+1}: {e}")


if __name__ == "__main__":
    asyncio.run(test_buddi_api())
