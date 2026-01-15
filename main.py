"""Main entry point."""
import os
import sys
import logging
import concurrent.futures

from config import OPENAI_MODELS_MAIN, CLAUDE_MODELS, MISTRAL_MODELS, CONFIG
from prompts import GLOBAL_PROMPT_TEMPLATE
from file_processor import process_file

log_dir = os.getenv('OUTPUT_DIR', '.')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'llm_processing.log')),
        logging.StreamHandler(sys.stdout)  # Use stdout (white) instead of stderr (red)
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Orchestrate resume processing with LLM models."""
    logger.info("Starting processing...")
    logger.info(f"OpenAI models to process: {OPENAI_MODELS_MAIN}")
    logger.info(f"Claude models to process: {CLAUDE_MODELS}")
    logger.info(f"Mistral models to process: {MISTRAL_MODELS}")

    # Use OUTPUT_DIR env var for cloud, or local directories
    output_base = os.getenv('OUTPUT_DIR', '.')
    openai_output_directory = os.path.join(output_base, 'output_csvs_openai')
    anthropic_output_directory = os.path.join(output_base, 'output_csvs_anthropic')
    mistral_output_directory = os.path.join(output_base, 'output_csvs_mistral')

    os.makedirs(openai_output_directory, exist_ok=True)
    os.makedirs(anthropic_output_directory, exist_ok=True)
    os.makedirs(mistral_output_directory, exist_ok=True)

    directory = 'resumes/md_extracted'
    files = os.listdir(directory)

    tasks = []
    for file_name in files:
        for i, model in enumerate(OPENAI_MODELS_MAIN):
            tasks.append({
                'file_name': file_name,
                'model': model,
                'directory': directory,
                'output_directory': openai_output_directory,
                'provider': 'openai',
                'group': i % 3
            })
        
        for model in CLAUDE_MODELS:
            tasks.append({
                'file_name': file_name,
                'model': model,
                'directory': directory,
                'output_directory': anthropic_output_directory,
                'provider': 'anthropic',
                'group': 0
            })
        
        for model in MISTRAL_MODELS:
            tasks.append({
                'file_name': file_name,
                'model': model,
                'directory': directory,
                'output_directory': mistral_output_directory,
                'provider': 'mistral',
                'group': 0
            })
    
    logger.info(f"Created {len(tasks)} tasks for processing")
    
    if not tasks:
        logger.warning("No tasks to process. Exiting.")
        return
    
    logger.info(f"Starting execution of {len(tasks)} tasks with max_workers={CONFIG['max_workers']}")
    
    def execute_task(task):
        """Execute a single processing task."""
        try:
            logger.info(f"Starting task: {task['file_name']} with {task['model']} ({task['provider']})")
            process_file(
                task['file_name'],
                task['model'],
                task['directory'],
                task['output_directory'],
                GLOBAL_PROMPT_TEMPLATE
            )
            logger.info(f"Completed task: {task['file_name']} with {task['model']} ({task['provider']})")
            return True
        except Exception as e:
            logger.error(f"Error processing task {task['file_name']} with {task['model']}: {e}", exc_info=True)
            return False
    
    # Execute tasks in parallel using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONFIG['max_workers']) as executor:
        futures = {executor.submit(execute_task, task): task for task in tasks}
        
        completed = 0
        failed = 0
        
        for future in concurrent.futures.as_completed(futures):
            task = futures[future]
            try:
                success = future.result()
                if success:
                    completed += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Unexpected error in task {task['file_name']} with {task['model']}: {e}", exc_info=True)
                failed += 1
            
            logger.info(f"Progress: {completed + failed}/{len(tasks)} tasks completed ({completed} successful, {failed} failed)")
    
    logger.info(f"All tasks completed. Successful: {completed}, Failed: {failed}, Total: {len(tasks)}")


if __name__ == "__main__":
    main()
