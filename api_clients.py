"""
API client functions for OpenAI, Claude, and Mistral.
Handles structured outputs, retries, and error handling.
"""
import time
import threading
import logging
import anthropic
import requests
from openai import OpenAI, OpenAIError
from mistralai import Mistral

from config import (
    OPENAI_API_KEYS, ANTHROPIC_API_KEY, MISTRAL_API_KEY,
    OPENAI_MODELS_MAIN, CLAUDE_MODELS, MISTRAL_MODELS,
    CONFIG
)
from prompts import SYSTEM_PROMPT
from utils import get_response_schema, get_claude_response_schema, get_mistral_response_schema

logger = logging.getLogger(__name__)

# Global OpenAI client state
openai_client = OpenAI(api_key=OPENAI_API_KEYS[0])
current_key_index = 0
openai_key_lock = threading.Lock()  # Lock for thread-safe key switching


def switch_openai_key():
    """Switch to the next available OpenAI API key (thread-safe)."""
    global current_key_index, openai_client
    with openai_key_lock:
        current_key_index = (current_key_index + 1) % len(OPENAI_API_KEYS)
        openai_client = OpenAI(api_key=OPENAI_API_KEYS[current_key_index])
        logger.info(f"Switched to OpenAI API key {current_key_index + 1}")


def get_json_structure_instruction():
    """JSON format instructions for models without schema enforcement."""
    return """

IMPORTANT: You must respond in valid JSON format with the following exact structure:
{
  "scores": [array of exactly 17 integers representing your answers to Q1-Q17],
  "manipulation_check": "YES" or "NO" (for Q18),
  "thought_process": "your 2-3 sentence explanation here" (for Q19)
}

Example format:
{
  "scores": [4, 3, 2, 4, 3, 2, 5, 4, 3, 2, 1, 5, 4, 3, 2, 4, 1],
  "manipulation_check": "NO",
  "thought_process": "I evaluated the applicant based on their qualifications and experience. The resume showed strong technical skills and relevant work history. I did not notice any mention of criminal record information."
}

Remember:
- "scores" must be an array of exactly 17 integers (one for each question Q1-Q17)
- "manipulation_check" must be either "YES" or "NO" (for question 18)
- "thought_process" must be a string with your 2-3 sentence explanation (for question 19)
"""


def get_openai_score(prompt: str, model: str) -> str:
    """Get score from OpenAI API."""
    global current_key_index, openai_client
    
    response_schema = get_response_schema()
    
    try:
        schema_support_models = ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.1-mini", "gpt-5.1", "o1", "o3-mini", "o4-mini"]
        use_schema = model in schema_support_models
        
        # Models that require max_completion_tokens instead of max_tokens
        new_token_param_models = ["gpt-5.1", "o1", "o3-mini", "o4-mini"]
        
        if model in ['o1', 'o3-mini', 'o4-mini']:
            messages = [
                {"role": "developer", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            create_kwargs = {
                "model": model,
                "messages": messages,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "evaluation_response",
                        "strict": True,
                        "schema": response_schema
                    }
                }
            }
            response = openai_client.chat.completions.create(**create_kwargs)
        elif model == "gpt-5.1":
            # gpt-5.1 uses developer role and max_completion_tokens
            messages = [
                {"role": "developer", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            create_kwargs = {
                "model": model,
                "messages": messages,
                "max_completion_tokens": 4096,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "evaluation_response",
                        "strict": True,
                        "schema": response_schema
                    }
                }
            }
            response = openai_client.chat.completions.create(**create_kwargs)
        else:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            create_kwargs = {
                "model": model,
                "messages": messages,
                "temperature": 0,
                "max_tokens": 4096
            }
            
            if use_schema:
                create_kwargs["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "evaluation_response",
                        "strict": True,
                        "schema": response_schema
                    }
                }
            else:
                json_instruction = get_json_structure_instruction()
                create_kwargs["response_format"] = {"type": "json_object"}
                messages[-1]["content"] = messages[-1]["content"] + json_instruction
            
            response = openai_client.chat.completions.create(**create_kwargs)
        
        result = response.choices[0].message.content
        logger.debug(f"OpenAI API call successful for model {model}")
        return result
        
    except OpenAIError as e:
        error_str = str(e).lower()
        if "insufficient_quota" in error_str or "billing_hard_limit_reached" in error_str:
            with openai_key_lock:
                key_index = current_key_index
            if key_index < len(OPENAI_API_KEYS) - 1:
                logger.warning(f"API key {key_index + 1} exhausted, switching to next key...")
                switch_openai_key()
                return get_openai_score(prompt, model)
            else:
                logger.error("All OpenAI API keys exhausted!")
                raise
        logger.error(f"OpenAI API error for model {model}: {e}")
        raise


def get_claude_score(prompt: str, model: str) -> str:
    """Get score from Claude API."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    structured_output_models = [
        "claude-opus-4-1-20250805"     # Claude Opus 4.1 (supports structured outputs)
    ]
    
    use_structured_output = model in structured_output_models
    
    try:
        create_kwargs = {
            "model": model,
            "temperature": 0.0,
            "max_tokens": 8192,
            "system": SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                },
            ]
        }
        
        if use_structured_output:
            # Use Claude-compatible schema (without minItems/maxItems for arrays)
            claude_schema = get_claude_response_schema()
            response = client.beta.messages.create(
                betas=["structured-outputs-2025-11-13"],
                model=model,
                temperature=0.0,
                max_tokens=8192,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                output_format={
                    "type": "json_schema",
                    "schema": claude_schema
                }
            )
            result = response.content[0].text
            logger.debug(f"Claude structured output API call successful for model {model}")
            return result
        else:
            # For older Claude 3.x models: use GPT-3.5 style JSON instruction approach
            # Add JSON format instructions to prompt (same approach as GPT-3.5)
            # The parser will extract structured data from the JSON response
            json_instruction = get_json_structure_instruction()
            create_kwargs["messages"][0]["content"] = create_kwargs["messages"][0]["content"] + json_instruction
            response = client.messages.create(**create_kwargs)
            result = response.content[0].text
            logger.debug(f"Claude API call successful for model {model} (using GPT-3.5 style JSON instruction fallback)")
            return result
    except anthropic.InternalServerError as e:
        error_msg = str(e).lower()
        if 'overloaded' in error_msg:
            logger.warning(f"Claude server overloaded for model {model}")
            raise anthropic.InternalServerError("Server overloaded") from e
        else:
            logger.error(f"Claude internal server error for model {model}: {e}")
            raise
    except Exception as e:
        logger.error(f"Unexpected error in Claude API call for model {model}: {e}")
        raise


def get_mistral_score(prompt: str, model: str) -> str:
    """Get score from Mistral API."""
    client = Mistral(api_key=MISTRAL_API_KEY)
    mistral_schema = get_mistral_response_schema()
    
    try:
        full_prompt = SYSTEM_PROMPT + "\n\n" + prompt
        
        response = client.chat.complete(
            model=model,
            temperature=0.0,
            max_tokens=4096,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "evaluation_response",
                    "strict": True,
                    "schema": mistral_schema
                }
            },
            messages=[
                {
                    "role": "user",
                    "content": full_prompt,
                },
            ]
        )
        result = response.choices[0].message.content
        logger.debug(f"Mistral structured output API call successful for model {model}")
        return result
    except Exception as e:
        logger.error(f"Mistral structured output failed for {model}: {e}")
        raise


def retry_request(prompt: str, model: str, max_retries: int, retry_delay: int) -> str:
    """Retry OpenAI API request with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return get_openai_score(prompt, model)
        except OpenAIError as e:
            error_str = str(e).lower()
            
            if hasattr(e, 'http_status') and e.http_status == 429:
                wait_time = min(
                    retry_delay * (CONFIG['exponential_backoff_base'] ** attempt),
                    CONFIG['exponential_backoff_max']
                )
                logger.warning(f"OpenAI rate limit hit (attempt {attempt + 1}/{max_retries}), waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            elif "insufficient_quota" in error_str or "billing_hard_limit_reached" in error_str:
                with openai_key_lock:
                    key_index = current_key_index
                if key_index < len(OPENAI_API_KEYS) - 1:
                    switch_openai_key()
                    logger.info(f"Switched to backup API key, retrying...")
                    continue
                else:
                    logger.error("All OpenAI API keys exhausted!")
                    raise
            else:
                logger.error(f"Non-retryable OpenAI error: {e}")
                raise
        
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI retry (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise
            wait_time = min(
                retry_delay * (CONFIG['exponential_backoff_base'] ** attempt),
                CONFIG['exponential_backoff_max']
            )
            time.sleep(wait_time)
    
    raise Exception(f"Max retries ({max_retries}) exceeded for OpenAI model {model}")


def retry_request_claude(prompt: str, model: str, max_retries: int, retry_delay: int) -> str:
    """Retry Claude API request with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return get_claude_score(prompt, model)
        except anthropic.InternalServerError as e:
            error_str = str(e).lower()
            if 'rate_limit' in error_str or 'overloaded' in error_str:
                # Exponential backoff with jitter
                wait_time = min(
                    retry_delay * (CONFIG['exponential_backoff_base'] ** attempt),
                    CONFIG['exponential_backoff_max']
                )
                logger.warning(f"Claude rate limit/overload (attempt {attempt + 1}/{max_retries}), waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            logger.error(f"Non-retryable Claude error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Claude retry (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise
            wait_time = min(
                retry_delay * (CONFIG['exponential_backoff_base'] ** attempt),
                CONFIG['exponential_backoff_max']
            )
            time.sleep(wait_time)
    
    raise Exception(f"Max retries ({max_retries}) exceeded for Claude model {model}")


def retry_request_mistral(prompt: str, model: str, max_retries: int, retry_delay: int) -> str:
    """Retry Mistral API request with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return get_mistral_score(prompt, model)
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code in [429, 500, 502, 503, 504]:
                wait_time = min(
                    retry_delay * (CONFIG['exponential_backoff_base'] ** attempt),
                    CONFIG['exponential_backoff_max']
                )
                logger.warning(f"Mistral HTTP error {e.response.status_code} (attempt {attempt + 1}/{max_retries}), waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            logger.error(f"Non-retryable Mistral HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Mistral retry (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise
            wait_time = min(
                retry_delay * (CONFIG['exponential_backoff_base'] ** attempt),
                CONFIG['exponential_backoff_max']
            )
            time.sleep(wait_time)
    
    raise Exception(f"Max retries ({max_retries}) exceeded for Mistral model {model}")

