from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database Configuration
    singlestore_host: str = os.getenv("SINGLESTORE_HOST", "localhost")
    singlestore_port: int = int(os.getenv("SINGLESTORE_PORT", "3306"))
    singlestore_user: str = os.getenv("SINGLESTORE_USER", "root")
    singlestore_password: str = os.getenv("SINGLESTORE_PASSWORD", "")
    singlestore_database: str = os.getenv("SINGLESTORE_DATABASE", "ecommerce_ai")
    
    # API Configuration
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Redis Configuration
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # External APIs
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    sendgrid_api_key: str = os.getenv("SENDGRID_API_KEY", "")
    
    # Agent Configuration
    enable_auto_pricing: bool = os.getenv("ENABLE_AUTO_PRICING", "true").lower() == "true"
    enable_auto_inventory: bool = os.getenv("ENABLE_AUTO_INVENTORY", "true").lower() == "true"
    enable_auto_recommendations: bool = os.getenv("ENABLE_AUTO_RECOMMENDATIONS", "true").lower() == "true"
    price_update_interval: int = int(os.getenv("PRICE_UPDATE_INTERVAL", "3600"))
    inventory_check_interval: int = int(os.getenv("INVENTORY_CHECK_INTERVAL", "1800"))
    
    @property
    def database_url(self) -> str:
        return f"mysql+pymysql://{self.singlestore_user}:{self.singlestore_password}@{self.singlestore_host}:{self.singlestore_port}/{self.singlestore_database}"

settings = Settings()
