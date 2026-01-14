# Criminal Record Hiring Bias Research

## Research Context

This project tests the value of LLM survey respondents by replicating a study originally conducted using YouGov human respondents who assessed fictitious job candidates with various types of criminal records and racial identities. The original survey yielded an unexpected finding: respondents ranked Black applicants with criminal records more favorably than white candidates with identical resumes and criminal histories—a pattern counter to the original hypothesis and guiding literature on racial discrimination.

This replication study uses LLM-generated survey responses to evaluate whether AI models exhibit similar patterns. The system processes resume evaluations using standardized prompts to measure hiring preferences, workplace stereotypes, and policy attitudes across OpenAI, Claude, and Mistral models. 
The project addresses critical questions about how algorithmic decision-making systems encode and reproduce social hierarchies, speaking directly to law and society concerns with how legal categories are translated, transformed, and potentially undermined in everyday institutional practices.

## Project Structure

The project uses a modular architecture for better maintainability and organization:

### Core Modules

- **`main.py`** - Main entry point and orchestration
- **`config.py`** - Centralized configuration (constants, model lists, API keys, question ranges)
- **`prompts.py`** - Prompt templates (system prompt and evaluation questions)
- **`parsers.py`** - Response parsing and validation utilities
  - `parse_scores()` - Extract 17 numerical scores from responses
  - `validate_scores()` - Validate scores are in correct ranges
  - `parse_manipulation_check()` - Extract YES/NO manipulation check
  - `parse_thought_process()` - Extract thought process text
- **`utils.py`** - Utility functions
  - `get_response_schema()` - JSON schema for structured outputs
  - `calculate_token_count()` - Token counting for prompts
  - `process_txt_files_and_attach_to_prompt()` - Build prompts from resume files
- **`api_clients.py`** - API client functions for all providers
  - `get_openai_score()` - OpenAI API with structured outputs
  - `get_claude_score()` - Claude API with structured outputs (beta)
  - `get_mistral_score()` - Mistral API with structured outputs
  - Retry logic with exponential backoff for all providers
- **`file_processor.py`** - File processing and CSV writing
  - `process_file()` - Main processing function for a single file/model combination
  - Handles batch processing, retries, CSV writing with thread-safe locking

### Utility Scripts

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

- **Input**: Resume markdown files in `resumes/md_extracted/`
- **Output**: CSV files in `output_csvs_openai/`, `output_csvs_anthropic/`, and `output_csvs_mistral/`
  - Each CSV contains: Model, Iteration, Q1-Q17, ManipulationCheck, ThoughtProcess

## Models Used

- **OpenAI**: gpt-4.1, gpt-4o, gpt-4.1-mini, gpt-5.1, o3-mini, o4-mini
- **Claude**: claude-3-7-sonnet-20250219, claude-opus-4-1-20250805, claude-sonnet-4-20250514, claude-3-5-haiku-20241022
- **Mistral**: ministral-3b-latest, ministral-8b-latest, mistral-large-latest, mistral-small-latest
