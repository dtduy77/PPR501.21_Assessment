import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

load_dotenv()


class ModelConfig:
    """Configuration for LLM models with automatic provider detection"""

    # OpenAI GPT Models
    OPENAI_MODELS = {
        "gpt-4o": {
            "name": "gpt-4o",
            "temperature": 0.0,
            "max_tokens": 800,
            "description": "GPT-4 Optimized",
        },
        "gpt-4o-mini": {
            "name": "gpt-4o-mini",
            "temperature": 0.0,
            "max_tokens": 800,
            "description": "GPT-4 Optimized Mini",
        },
        "gpt-4-turbo": {
            "name": "gpt-4-turbo",
            "temperature": 0.0,
            "max_tokens": 800,
            "description": "GPT-4 Turbo",
        },
        "gpt-3.5-turbo": {
            "name": "gpt-3.5-turbo",
            "temperature": 0.0,
            "max_tokens": 800,
            "description": "GPT-3.5 Turbo",
        },
    }

    # Google Gemini Models
    GOOGLE_MODELS = {
        "gemini-pro": {
            "name": "gemini-pro",
            "temperature": 0.0,
            "max_output_tokens": 800,
            "description": "Gemini Pro",
        },
        "gemini-pro-preview": {
            "name": "gemini-pro-preview",
            "temperature": 0.0,
            "max_output_tokens": 800,
            "description": "Gemini Pro Preview",
        },
        "gemini-1.5-pro": {
            "name": "gemini-1.5-pro",
            "temperature": 0.0,
            "max_output_tokens": 800,
            "description": "Gemini 1.5 Pro",
        },
        "gemini-2.5-flash": {
            "name": "gemini-2.5-flash",
            "temperature": 0.0,
            "max_output_tokens": 800,
            "description": "Gemini 2.5 Flash",
        },
    }

    # Categories for bill items
    ALLOWED_CATEGORIES = {"food", "coffee", "transport", "shopping", "other"}

    def __init__(self):
        """Initialize ModelConfig with auto-detected provider"""
        self.provider = self.detect_provider()
        self.api_keys = self.get_api_keys()

    @property
    def current_model_config(self) -> Dict[str, Any]:
        """Get configuration for current provider"""
        if self.provider == "openai":
            return self.get_openai_config()
        elif self.provider == "google":
            return self.get_google_config()
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    @classmethod
    def check_openai_available(cls) -> bool:
        """Check if OpenAI is available (has API key and package)"""
        try:
            api_key = os.environ.get("OPENAI_API_KEY")
            return api_key is not None and api_key.strip() != ""
        except Exception:
            return False

    @classmethod
    def check_google_available(cls) -> bool:
        """Check if Google is available (has API key)"""
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        return api_key is not None and api_key.strip() != ""

    @classmethod
    def detect_provider(cls) -> str:
        """Detect which provider to use based on available API keys"""
        if cls.check_openai_available():
            return "openai"
        elif cls.check_google_available():
            return "google"
        else:
            raise ValueError(
                "No API key found. Please set either OPENAI_API_KEY or GOOGLE_API_KEY/GEMINI_API_KEY"
            )

    @classmethod
    def get_openai_config(cls, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get OpenAI model configuration"""
        model_name = model_name or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        return cls.OPENAI_MODELS.get(model_name, cls.OPENAI_MODELS["gpt-4o-mini"])

    @classmethod
    def get_google_config(cls, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get Google model configuration"""
        model_name = model_name or os.environ.get("GOOGLE_MODEL", "gemini-2.5-flash")
        return cls.GOOGLE_MODELS.get(model_name, cls.GOOGLE_MODELS["gemini-2.5-flash"])

    @classmethod
    def get_api_keys(cls) -> Dict[str, Optional[str]]:
        """Get API keys from environment"""
        return {
            "openai": os.environ.get("OPENAI_API_KEY"),
            "google": os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("GEMINI_API_KEY"),
        }


def get_model_config() -> ModelConfig:
    """Get the model configuration with auto-detected provider"""
    return ModelConfig()
