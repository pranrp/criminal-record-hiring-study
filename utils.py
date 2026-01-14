"""Utility functions."""
import tiktoken
import logging
from prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def get_response_schema():
    """Get JSON schema for structured outputs."""
    return {
        "type": "object",
        "properties": {
            "scores": {
                "type": "array",
                "items": {"type": "integer"},
                "minItems": 17,
                "maxItems": 17,
                "description": "Array of exactly 17 scores for questions Q1-Q17"
            },
            "manipulation_check": {
                "type": "string",
                "enum": ["YES", "NO"],
                "description": "Does the resume mention any criminal record information?"
            },
            "thought_process": {
                "type": "string",
                "description": "Brief 2-3 sentence explanation of evaluation reasoning"
            }
        },
        "required": ["scores", "manipulation_check", "thought_process"],
        "additionalProperties": False
    }


def get_claude_response_schema():
    """Get JSON schema for Claude API (removes minItems/maxItems from arrays)."""
    return {
        "type": "object",
        "properties": {
            "scores": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Array of exactly 17 scores for questions Q1-Q17"
            },
            "manipulation_check": {
                "type": "string",
                "enum": ["YES", "NO"],
                "description": "Does the resume mention any criminal record information?"
            },
            "thought_process": {
                "type": "string",
                "description": "Brief 2-3 sentence explanation of evaluation reasoning"
            }
        },
        "required": ["scores", "manipulation_check", "thought_process"],
        "additionalProperties": False
    }


def get_mistral_response_schema():
    """Get JSON schema for Mistral API with explicit per-question score constraints.
    
    Question ranges:
    - Q1: 1-7
    - Q2-Q6: 1-5  
    - Q7-Q16: 1-6
    - Q17: 1-2
    """
    return {
        "type": "object",
        "properties": {
            "q1": {"type": "integer", "minimum": 1, "maximum": 7, "description": "Score for Q1 (1-7)"},
            "q2": {"type": "integer", "minimum": 1, "maximum": 5, "description": "Score for Q2 (1-5)"},
            "q3": {"type": "integer", "minimum": 1, "maximum": 5, "description": "Score for Q3 (1-5)"},
            "q4": {"type": "integer", "minimum": 1, "maximum": 5, "description": "Score for Q4 (1-5)"},
            "q5": {"type": "integer", "minimum": 1, "maximum": 5, "description": "Score for Q5 (1-5)"},
            "q6": {"type": "integer", "minimum": 1, "maximum": 5, "description": "Score for Q6 (1-5)"},
            "q7": {"type": "integer", "minimum": 1, "maximum": 6, "description": "Score for Q7 (1-6)"},
            "q8": {"type": "integer", "minimum": 1, "maximum": 6, "description": "Score for Q8 (1-6)"},
            "q9": {"type": "integer", "minimum": 1, "maximum": 6, "description": "Score for Q9 (1-6)"},
            "q10": {"type": "integer", "minimum": 1, "maximum": 6, "description": "Score for Q10 (1-6)"},
            "q11": {"type": "integer", "minimum": 1, "maximum": 6, "description": "Score for Q11 (1-6)"},
            "q12": {"type": "integer", "minimum": 1, "maximum": 6, "description": "Score for Q12 (1-6)"},
            "q13": {"type": "integer", "minimum": 1, "maximum": 6, "description": "Score for Q13 (1-6)"},
            "q14": {"type": "integer", "minimum": 1, "maximum": 6, "description": "Score for Q14 (1-6)"},
            "q15": {"type": "integer", "minimum": 1, "maximum": 6, "description": "Score for Q15 (1-6)"},
            "q16": {"type": "integer", "minimum": 1, "maximum": 6, "description": "Score for Q16 (1-6)"},
            "q17": {"type": "integer", "minimum": 1, "maximum": 2, "description": "Score for Q17 (1-2)"},
            "manipulation_check": {
                "type": "string",
                "enum": ["YES", "NO"],
                "description": "Does the resume mention any criminal record information?"
            },
            "thought_process": {
                "type": "string",
                "description": "Brief 2-3 sentence explanation of evaluation reasoning"
            }
        },
        "required": ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", 
                     "q11", "q12", "q13", "q14", "q15", "q16", "q17", 
                     "manipulation_check", "thought_process"],
        "additionalProperties": False
    }


def calculate_token_count(prompt: str, model: str = "gpt-4o") -> int:
    """Calculate token count for a prompt."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logger.warning(f"Encoding not found for model {model}, using cl100k_base")
        encoding = tiktoken.get_encoding("cl100k_base")
    
    tokens = encoding.encode(prompt)
    return len(tokens)


def process_txt_files_and_attach_to_prompt(file_path: str, global_prompt_template: str) -> str:
    """Read resume text and construct prompt."""
    with open(file_path, 'r', encoding='utf-8') as file:
        extracted_text = file.read().strip()
    
    full_prompt = f"""RESUME:
{extracted_text}

---

EVALUATION QUESTIONS:
{global_prompt_template}"""
    
    return full_prompt

