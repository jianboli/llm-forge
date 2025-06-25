# backend/app/core/config.py
from pydantic_settings import BaseSettings

# Define our initial, simple list of models
# Using smaller models for easier download and lower resource usage initially
AVAILABLE_MODELS = [
    {
        "id": "google/flan-t5-small",
        "name": "Flan-T5 Small (Google)",
        "source": "huggingface",
        "pipeline_kwargs": {"max_new_tokens": 100} # Example specific args
    },
    {
        "id": "distilgpt2",
        "name": "DistilGPT-2 (Hugging Face)",
        "source": "huggingface",
        "pipeline_kwargs": {"max_new_tokens": 50}
    },
    # { # Example for later API integration (requires .env setup)
    #     "id": "openai/gpt-3.5-turbo",
    #     "name": "GPT-3.5 Turbo (OpenAI API)",
    #     "type": "api"
    # }
]

class Settings(BaseSettings):
    APP_NAME: str = "LLM-Forge"
    # Add other settings like API keys from .env later if needed
    # OPENAI_API_KEY: str | None = None

    # Allow models to be configured via environment variable later if needed
    # Example: MODELS_JSON: str = json.dumps(AVAILABLE_MODELS)

    class Config:
        env_file = ".env"

settings = Settings()

# Simple function to get model details by ID
def get_model_config(model_id: str):
    for model in AVAILABLE_MODELS:
        if model["id"] == model_id:
            return model
    return None