import os
from pydantic import BaseModel
from dotenv import load_dotenv

# Automatically load environment variables from .env file when running locally
load_dotenv()

def get_valid_gemini_model(env_model: str) -> str:
    raw_model = (env_model or "").strip()
    valid_prefixes = ("gemini-2.5", "gemini-2.0", "gemini-1.5", "gemini-3.1")
    if raw_model and any(raw_model.startswith(p) for p in valid_prefixes):
        return raw_model
    return "gemini-2.5-flash"

class Settings(BaseModel):
    PROJECT_NAME: str = "AMA-System"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    GEMINI_MODEL: str = get_valid_gemini_model(os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    UPSTASH_REDIS_REST_URL: str = os.getenv("UPSTASH_REDIS_REST_URL", "")
    UPSTASH_REDIS_REST_TOKEN: str = os.getenv("UPSTASH_REDIS_REST_TOKEN", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "")

settings = Settings()
