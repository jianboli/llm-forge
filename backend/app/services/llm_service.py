import httpx # Use httpx for async requests
import openai
import os
from typing import Dict, Any, List
from fastapi import HTTPException, status

from app.core.config import settings # Import settings
from app.schemas.evaluation import EvaluationConfig # Import the config schema
from app.schemas.model import ModelInfo # Import ModelInfo schema

# Initialize OpenAI client (consider doing this once, maybe in main.py or via dependency injection)
# Ensure OPENAI_API_KEY is loaded via settings
if settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY
else:
    print("Warning: OPENAI_API_KEY not found in settings. OpenAI models will not work.")

# --- Hugging Face Helper ---
async def call_huggingface_inference_api(model_id: str, prompt: str, config: EvaluationConfig, client: httpx.AsyncClient) -> str:
    """Calls the Hugging Face Inference API asynchronously."""
    if not settings.HUGGINGFACE_API_TOKEN:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="HuggingFace API token not configured.")

    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}"}

    # Map config to HF API parameters
    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": config.temperature,
            "max_new_tokens": config.maxTokens,
            # Add other mapped parameters here
            "return_full_text": False,
        },
        "options": {"wait_for_model": True}
    }

    try:
        response = await client.post(api_url, headers=headers, json=payload, timeout=60.0) # Add timeout
        response.raise_for_status() # Raise HTTPStatusError for bad responses (4xx or 5xx)

        result = response.json()
        if isinstance(result, list) and len(result) > 0 and 'generated_text' in result[0]:
            return result[0]['generated_text']
        else:
            print(f"Unexpected HuggingFace response format: {result}")
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Could not parse HuggingFace response.")

    except httpx.HTTPStatusError as e:
        # Provide more specific error feedback
        err_detail = f"HuggingFace API Error for {model_id}: {e.response.status_code}"
        try: # Try to get error message from HF response
            hf_error = e.response.json().get('error', 'Unknown error detail')
            err_detail += f" - {hf_error}"
        except Exception:
             err_detail += f" - {e.response.text}" # Fallback to raw text
        print(f"HTTPStatusError calling HuggingFace: {err_detail}")
        raise HTTPException(status_code=e.response.status_code, detail=err_detail) from e
    except httpx.RequestError as e:
        # Handle network-related errors (timeout, DNS, connection refused)
        print(f"RequestError calling HuggingFace: {e}")
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=f"Network error contacting HuggingFace: {e}") from e


# --- Main Evaluation Service Function ---
async def evaluate_model(model_id: str, prompt: str, config: EvaluationConfig) -> str:
    """
    Evaluates a prompt using the specified model ID and configuration.
    Dispatches the request to the appropriate LLM backend.
    """
    print(f"Evaluating model: {model_id} with temp: {config.temperature}, maxTokens: {config.maxTokens}") # Logging

    if model_id.startswith('openai/'):
        if not settings.OPENAI_API_KEY:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="OpenAI API key not configured.")
        try:
            openai_model_name = model_id.split('/', 1)[1]
            # NOTE: openai library v1+ is synchronous by default.
            # For a truly async app, call this using asyncio.to_thread or run_in_threadpool
            # Example: loop = asyncio.get_running_loop(); await loop.run_in_executor(None, lambda: openai.chat.completions.create(...))
            # Or use an async OpenAI client if available. Sticking to sync for simplicity here.
            completion = openai.chat.completions.create(
                model=openai_model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.temperature,
                max_tokens=config.maxTokens,
                # Map other config parameters if needed
            )
            response_text = completion.choices[0].message.content.strip()
            return response_text
        except openai.APIError as e:
            print(f"OpenAI API Error: {e}")
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"OpenAI API Error: {e}") from e
        except Exception as e: # Catch other potential OpenAI client errors
            print(f"Unexpected OpenAI Error: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal error during OpenAI call: {e}") from e

    elif model_id.startswith('huggingface/'):
        hf_model_name = model_id.split('/', 1)[1]
        async with httpx.AsyncClient() as client: # Use a client session
             return await call_huggingface_inference_api(hf_model_name, prompt, config, client)

    elif model_id.startswith('local/'):
        local_model_name = model_id.split('/', 1)[1]
        # --- Placeholder for Local Model Interaction (e.g., Ollama) ---
        # Replace with actual async call using httpx
        ollama_url = settings.OLLAMA_BASE_URL # Assumes you add OLLAMA_BASE_URL to settings
        if not ollama_url:
             raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Ollama base URL not configured.")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{ollama_url.rstrip('/')}/api/generate",
                    json={
                        "model": local_model_name,
                        "prompt": prompt,
                        "stream": False, # Get full response at once
                        "options": {
                            "temperature": config.temperature,
                            "num_predict": config.maxTokens # Ollama uses num_predict
                            # Map other options
                        }
                    },
                    timeout=120.0 # Longer timeout for local models maybe
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "Error: 'response' key missing from Ollama result.")
        except httpx.HTTPStatusError as e:
             print(f"HTTPStatusError calling Ollama: {e}")
             raise HTTPException(status_code=e.response.status_code, detail=f"Ollama API Error ({local_model_name}): {e.response.text}") from e
        except httpx.RequestError as e:
             print(f"RequestError calling Ollama: {e}")
             raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=f"Network error contacting Ollama ({ollama_url}): {e}") from e
        # --- End Placeholder ---

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported or unknown model ID format: {model_id}"
        )


# --- Service Function to Get Models ---
async def get_available_models() -> List[ModelInfo]:
    """
    Retrieves the list of available/deployed models.
    TODO: Replace static list with dynamic logic (read from config, DB, etc.)
    """
    # IN A REAL APP: Query your model sources here!
    # This should reflect the *actual* configurable/deployable state.
    all_models = [
        ModelInfo(id="openai/gpt-4", name="GPT-4", source="OpenAI", deployed=True), # Assume deployed=True means 'configured'
        ModelInfo(id="openai/gpt-3.5-turbo", name="GPT-3.5 Turbo", source="OpenAI", deployed=True),
        ModelInfo(id="huggingface/google/gemma-7b-it", name="Gemma 7B Instruct", source="Hugging Face", deployed=False),
        ModelInfo(id="huggingface/mistralai/Mistral-7B-Instruct-v0.2", name="Mistral 7B Instruct v0.2", source="Hugging Face", deployed=False),
        # Check if Ollama URL is configured before listing local models?
        ModelInfo(id="local/llama2", name="Llama 2 (Local Ollama)", source="Local", deployed=bool(settings.OLLAMA_BASE_URL)), # Example: Deployed if Ollama is configured
        ModelInfo(id="local/my-finetuned-model", name="My Custom Model (Local Ollama)", source="Local", deployed=bool(settings.OLLAMA_BASE_URL)),
    ]
    # Filter or adjust based on actual deployment status/configuration checks
    # For now, we return the list as defined, but the 'deployed' flag should be dynamic
    return all_models


# --- Service Function to Deploy/Undeploy (Placeholder) ---
async def set_model_deployment_status(model_id: str, deploy: bool) -> ModelInfo:
    """
    Placeholder for changing a model's deployment status.
    TODO: Implement actual logic (update config, DB, provision resources)
    """
    # 1. Find the model (this should come from a central registry/config)
    # 2. Perform deployment/undeployment actions
    # 3. Update the status in the central registry/config
    # 4. Return the updated ModelInfo
    print(f"Simulating {'deploy' if deploy else 'undeploy'} for {model_id}")
    # Fetch current models again (or from cache/registry)
    models = await get_available_models()
    target_model = next((m for m in models if m.id == model_id), None)
    if not target_model:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Model '{model_id}' not found in configuration.")

    # Simulate update
    target_model.deployed = deploy
    print(f"Simulated status for {model_id}: deployed={target_model.deployed}")

    # In real app: Persist this change!

    return target_model