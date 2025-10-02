# Criminal Record Hiring Bias Research

A research platform analyzing AI model attitudes toward job applicants with criminal records. This study evaluates bias patterns across multiple large language models in employment screening scenarios.

The system processes resume evaluations using standardized prompts to measure hiring preferences, workplace stereotypes, and policy attitudes across OpenAI, Claude, and Mistral models.

## Files

- **`main.py`** - Main processing script for OpenAI and Claude models
- **`cleanup.py`** - CSV cleaning utility (combines OpenAI and Claude cleaning)
- **`pdf_utils.py`** - PDF processing utilities
- **`requirements.txt`** - Python dependencies

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
   ```bash
   # Copy the example template
   cp .env.example .env
   
   # Edit .env with your actual API keys
   nano .env  # or use your preferred editor
   ```
   
   Required API keys in `.env`:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_BACKUP_KEY=your_backup_openai_api_key
   CLAUDE_API_KEY=your_claude_api_key
   MISTRAL_API_KEY_2=your_mistral_api_key
   ```

## Usage

### Process Resumes
```bash
python main.py
```

### Clean CSV Outputs
```bash
python cleanup.py
```

## Input/Output

- **Input**: Resume text files in `resumes/txt_extracted/`

## Models Used

- **OpenAI**: gpt-3.5-turbo-16k, gpt-4o, gpt-4o-mini,o1,o3-mini,o4-mini
- **Claude**: claude-3-5-sonnet-latest, claude-3-5-haiku-latest, claude-3-sonnet-20240229
- **Mistral**: ministral-3b-latest, ministral-8b-latest, mistral-large-latest, mistral-small-latest


## Backup Files

Original files are preserved in the `backup/` directory:
- `main_fix.py` - Alternative version with different models
- `cleanup_claude.py` - Claude-specific cleaning utility
