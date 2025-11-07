import os
from dotenv import load_dotenv
from nltk.tokenize import word_tokenize
load_dotenv()

class Config:
    """Configuration settings for the plagiarism detector"""
    
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "paste_your_key_here")
    
    # Wikipedia Settings
    WIKIPEDIA_MAX_RESULTS = 5
    WIKIPEDIA_MAX_CHARS = 2000
    
    # Detection Parameters
    NGRAM_SIZE = 6
    SIMILARITY_THRESHOLD = 0.7
    MIN_MATCH_LENGTH = 10
    
    # LLM Settings
    LLM_MODEL = "qwen2-7b-instruct"  # Free model that works well
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configurations are set"""
        if not cls.GROQ_API_KEY or cls.GROQ_API_KEY == "your-groq-api-key-here":
            raise ValueError("Please set your GROQ_API_KEY in environment variables or .env file")
