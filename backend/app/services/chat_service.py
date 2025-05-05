# backend/app/services/chat_service.py
import logging
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer, AutoModelForCausalLM
from ..core.config import get_model_config
import asyncio

# Simple cache for loaded models/pipelines to avoid reloading on every request
# Warning: This is a basic in-memory cache. For production, consider LRU cache
# or more sophisticated model serving solutions (like BentoML, Ray Serve).
# Also, this can consume significant memory if many models are loaded.
_loaded_pipelines = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_pipeline(model_id: str):
    """Loads or retrieves a cached Hugging Face pipeline."""
    if model_id in _loaded_pipelines:
        logger.info(f"Using cached pipeline for {model_id}")
        return _loaded_pipelines[model_id]

    model_config = get_model_config(model_id)
    if not model_config:
        raise ValueError(f"Configuration for model {model_id} not found.")

    # Basic check for model type based on name (can be improved)
    task = "text2text-generation" # Default for T5 style
    model_class = AutoModelForSeq2SeqLM
    if "gpt" in model_id.lower() or "causal" in model_id.lower():
         task = "text-generation"
         model_class = AutoModelForCausalLM

    try:
        logger.info(f"Loading model {model_id} for task {task}...")
        # Specify device_map="auto" or device=0 for GPU if available and configured
        # For CPU explicitly: device=-1 (default usually)
        model = model_class.from_pretrained(model_id)
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        pipe = pipeline(task, model=model, tokenizer=tokenizer) # Add device=0 for GPU
        _loaded_pipelines[model_id] = pipe
        logger.info(f"Pipeline for {model_id} loaded successfully.")
        return pipe
    except Exception as e:
        logger.error(f"Error loading model {model_id}: {e}", exc_info=True)
        raise RuntimeError(f"Failed to load model {model_id}") from e

async def generate_response(model_id: str, prompt: str) -> str:
    """Generates a response using the specified model."""
    logger.info(f"Generating response for model {model_id}")
    model_config = get_model_config(model_id)
    if not model_config:
         raise ValueError(f"Model {model_id} not found or configured.")

    # Handle API models later (placeholder)
    # if model_config.get("type") == "api":
    #    pass

    # --- Local Hugging Face Model ---
    try:
        # Get the pipeline (which knows its task internally)
        pipe = get_pipeline(model_id)
        pipeline_kwargs = model_config.get("pipeline_kwargs", {})

        logger.info(f"Running pipeline (task: {pipe.task}) for {model_id} with prompt: '{prompt[:50]}...'")

        # Use asyncio.to_thread to run the potentially blocking pipeline call
        # in a separate thread, preventing it from blocking the FastAPI event loop.
        results = await asyncio.to_thread(pipe, prompt, **pipeline_kwargs)

        # Extract text based on the pipeline's task attribute
        response_text = ""
        if isinstance(results, list) and results:
            # Access the task type directly from the pipeline object
            if pipe.task == "text-generation":
                 # Typically [{'generated_text': '...'}]
                 # Remove the input prompt if the model includes it in the output
                 full_text = results[0].get('generated_text', '')
                 # Check if prompt is at the beginning and remove it
                 if full_text.startswith(prompt):
                     response_text = full_text[len(prompt):].strip()
                 else:
                      response_text = full_text.strip() # Otherwise take the whole generated text
            elif pipe.task == "text2text-generation":
                 # Typically [{'generated_text': '...'}]
                 response_text = results[0].get('generated_text', '').strip()
            else:
                 logger.warning(f"Pipeline for {model_id} has unknown task type '{pipe.task}'. Attempting default extraction.")
                 # Fallback attempt for common output format
                 response_text = results[0].get('generated_text', '').strip()


        if not response_text:
             logger.warning(f"Pipeline for {model_id} returned empty or unexpected result structure: {results}")
             return "Model returned no response or failed to parse."

        logger.info(f"Model {model_id} generated response: '{response_text[:50]}...'")
        return response_text

    except Exception as e:
        logger.error(f"Error during generation with {model_id}: {e}", exc_info=True)
        # Attempt to clear the pipeline from cache if it caused an error during generation
        if model_id in _loaded_pipelines:
            try:
                # Try to delete gracefully, handle potential issues during cleanup
                del _loaded_pipelines[model_id]
                logger.info(f"Removed potentially problematic pipeline {model_id} from cache.")
            except Exception as cleanup_err:
                 logger.error(f"Error removing pipeline {model_id} from cache: {cleanup_err}")
        return f"Error generating response: Check backend logs for details." # Don't expose raw exception message to user