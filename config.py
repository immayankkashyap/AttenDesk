import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DEBUG = True
    
    # Ollama settings
    OLLAMA_MODEL = 'llama3.2:3b'  # Can be changed to other models
    OLLAMA_HOST = 'http://localhost:11434'  # Default Ollama host
    
    # Curriculum generation settings
    MAX_TASK_DURATION = 30  # minutes
    MIN_TASK_DURATION = 5   # minutes
    DEFAULT_TASKS_PER_BREAK = 2
    
    # Academic performance thresholds
    WEAK_SUBJECT_THRESHOLD = 60  # Below this percentage is considered weak
    STRONG_SUBJECT_THRESHOLD = 80 # Above this is considered strong
