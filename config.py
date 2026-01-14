"""Configuration settings."""
import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    'iterations_per_file': 100,
    'batch_size': 15,
    'max_workers': 5,
    'num_questions': 17,
    'retry_delay': 60,
    'max_retries': 10,
    'exponential_backoff_base': 2,
    'exponential_backoff_max': 300
}

QUESTION_RANGES = {
    1: (1, 7),
    2: (1, 5),
    3: (1, 5),
    4: (1, 5),
    5: (1, 5),
    6: (1, 5),
    7: (1, 6),
    8: (1, 6),
    9: (1, 6),
    10: (1, 6),
    11: (1, 6),
    12: (1, 6),
    13: (1, 6),
    14: (1, 6),
    15: (1, 6),
    16: (1, 6),
    17: (1, 2),
}

OPENAI_MODELS_MAIN = ["gpt-4.1", "gpt-4o", "gpt-4.1-mini", "gpt-5.1", "o3-mini", "o4-mini"]
MISTRAL_MODELS = ["ministral-3b-latest", "ministral-8b-latest", "mistral-large-latest", "mistral-small-latest"]
CLAUDE_MODELS = [
    "claude-3-7-sonnet-20250219",      # Mapped from claude-3-5-sonnet (uses GPT-3.5 style JSON instructions)
    "claude-opus-4-1-20250805",        # Mapped from claude-3-opus (supports structured outputs - Opus 4.1)
    "claude-sonnet-4-20250514",        # Mapped from claude-3-sonnet (uses GPT-3.5 style JSON instructions - Sonnet 4, not 4.5)
    "claude-3-5-haiku-20241022"        # Mapped from claude-3-haiku (uses GPT-3.5 style JSON instructions)
]
OPENAI_API_KEYS = [
    os.getenv("OPENAI_API_KEY"),
    os.getenv("OPENAI_BACKUP_KEY")
]
ANTHROPIC_API_KEY = os.getenv("CLAUDE_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY_2")

