#!/usr/bin/env python3
"""Database setup script for Buddi Tokenization PoC."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine
from app.db.models import Base
from app.core.config import settings


def setup_database():
    """Create all database tables."""
    print(f"Setting up database: {settings.database_url}")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Test connection
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection test successful!")
            
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    setup_database()
