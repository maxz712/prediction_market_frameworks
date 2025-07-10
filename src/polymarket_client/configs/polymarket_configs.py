import os
from typing import Dict, Optional
from pydantic import BaseModel, Field, field_validator


class PolymarketConfig(BaseModel):
    hosts: Dict[str, str] = Field(
        default={
            "gamma": "https://gamma-api.polymarket.com",
            "clob": "https://clob.polymarket.com"
        },
        description="API host URLs for Polymarket services"
    )
    chain_id: int = Field(default=137, description="Blockchain chain ID")
    api_key: str = Field(..., description="CLOB API key")
    api_secret: str = Field(..., description="CLOB API secret")
    api_passphrase: str = Field(..., description="CLOB API passphrase")
    pk: str = Field(..., description="Private key for trading operations")
    
    @field_validator('api_key', 'api_secret', 'api_passphrase', 'pk')
    @classmethod
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Required field cannot be empty")
        return v.strip()
    
    @field_validator('hosts')
    @classmethod
    def validate_hosts(cls, v):
        required_hosts = {'gamma', 'clob'}
        if not all(host in v for host in required_hosts):
            raise ValueError(f"hosts must contain keys: {required_hosts}")
        return v
    
    @classmethod
    def from_env(cls, 
                 api_key_env: str = "POLYMARKET_API_KEY",
                 api_secret_env: str = "POLYMARKET_API_SECRET", 
                 api_passphrase_env: str = "POLYMARKET_API_PASSPHRASE",
                 private_key_env: str = "POLYMARKET_PRIVATE_KEY",
                 chain_id_env: str = "POLYMARKET_CHAIN_ID") -> 'PolymarketConfig':
        """Create config from environment variables."""
        config_data = {
            "api_key": os.getenv(api_key_env, ""),
            "api_secret": os.getenv(api_secret_env, ""),
            "api_passphrase": os.getenv(api_passphrase_env, ""),
            "pk": os.getenv(private_key_env, "")
        }
        
        # Only set chain_id if environment variable exists, otherwise use default
        chain_id_str = os.getenv(chain_id_env)
        if chain_id_str:
            config_data["chain_id"] = int(chain_id_str)
            
        return cls(**config_data)
    
    class Config:
        env_prefix = "POLYMARKET_"