"""Configuration settings for the Buddi Tokenization PoC."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = "sqlite:///./buddi_chain.db"
    
    # æternity Blockchain Configuration
    aeternity_network_id: str = "ae_uat"
    aeternity_node_url: str = "https://testnet.aeternity.io"
    aeternity_private_key: Optional[str] = None
    
    # Buddi API Configuration
    buddi_api_base_url: str = "https://apis.getbuddi.ai/v1/dev"
    buddi_api_key: Optional[str] = None
    
    # Application Configuration
    secret_key: str = "your-secret-key-change-in-production"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Analytics Configuration
    huggingface_api_token: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
