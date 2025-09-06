import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or 'your-gemini-api-key'
    DEBUG = True
    
    # Curriculum generation settings
    MAX_TASK_DURATION = 30  # minutes
    MIN_TASK_DURATION = 5   # minutes
    DEFAULT_TASKS_PER_BREAK = 2
    
    # Academic performance thresholds
    WEAK_SUBJECT_THRESHOLD = 60  # Below this percentage is considered weak
    STRONG_SUBJECT_THRESHOLD = 80 # Above this is considered strong
