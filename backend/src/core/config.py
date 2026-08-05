import os
from pydantic import BaseModel
from dotenv import load_dotenv

# Automatically load environment variables from .env file when running locally
load_dotenv()

def get_valid_google_model(env_model: str) -> str:
    raw_model = (env_model or "").strip()
    valid_prefixes = (
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.1-flash",
        "gemini-3-flash",
        "gemini-2.5-flash",
        "gemini-flash",
        "gemma-4",
    )
    if raw_model and any(raw_model.startswith(p) for p in valid_prefixes):
        return raw_model
    return "gemini-3.5-flash"

# Backwards compatibility alias
get_valid_gemini_model = get_valid_google_model

DEFAULT_WATERFALL_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3-flash",
    "gemini-2.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemma-4-31b-it",
    "gemma-4-26b-it",
]

def get_google_model_chain(primary_model: str | None = None) -> list[str]:
    chain = []
    if primary_model:
        chain.append(primary_model)
    for model in DEFAULT_WATERFALL_MODELS:
        if model not in chain:
            chain.append(model)
    return chain

# Backwards compatibility alias
get_gemini_model_chain = get_google_model_chain

class Settings(BaseModel):
    PROJECT_NAME: str = "AMA-System"
    GEMINI_API_KEY: str = ""
    LLM_MODEL: str = ""
    GEMINI_MODEL: str = ""
    ROUTER_LLM_MODEL: str = ""
    SCRAPER_LLM_MODEL: str = ""
    INSIGHT_LLM_MODEL: str = ""
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    UPSTASH_REDIS_REST_URL: str = ""
    UPSTASH_REDIS_REST_TOKEN: str = ""
    REDIS_URL: str = ""

    def model_post_init(self, __context):
        if not self.GEMINI_API_KEY:
            self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
        if not self.LLM_MODEL:
            self.LLM_MODEL = get_valid_google_model(
                os.getenv("LLM_MODEL") or os.getenv("GEMINI_MODEL") or "gemini-3.5-flash"
            )
        if not self.GEMINI_MODEL:
            self.GEMINI_MODEL = self.LLM_MODEL
        if not self.ROUTER_LLM_MODEL:
            self.ROUTER_LLM_MODEL = get_valid_google_model(
                os.getenv("ROUTER_LLM_MODEL") or self.LLM_MODEL
            )
        if not self.SCRAPER_LLM_MODEL:
            self.SCRAPER_LLM_MODEL = get_valid_google_model(
                os.getenv("SCRAPER_LLM_MODEL") or "gemma-4-31b-it"
            )
        if not self.INSIGHT_LLM_MODEL:
            self.INSIGHT_LLM_MODEL = get_valid_google_model(
                os.getenv("INSIGHT_LLM_MODEL") or self.LLM_MODEL
            )
        if not self.SUPABASE_URL:
            self.SUPABASE_URL = os.getenv("SUPABASE_URL", "")
        if not self.SUPABASE_KEY:
            self.SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
        if not self.SUPABASE_SERVICE_ROLE_KEY:
            self.SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        if not self.UPSTASH_REDIS_REST_URL:
            self.UPSTASH_REDIS_REST_URL = os.getenv("UPSTASH_REDIS_REST_URL", "")
        if not self.UPSTASH_REDIS_REST_TOKEN:
            self.UPSTASH_REDIS_REST_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN", "")
        if not self.REDIS_URL:
            self.REDIS_URL = os.getenv("REDIS_URL", "")

settings = Settings()



