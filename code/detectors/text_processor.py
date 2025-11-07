import re
import nltk
from typing import List, Set
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

class TextProcessor:
    """Enhanced text preprocessing and phrase extraction"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Keep basic punctuation for sentence structure
        text = re.sub(r'[^a-zA-Z0-9\s\.\,\;]', '', text)
        
        return text.strip()
    
    def extract_meaningful_phrases(self, text: str, min_words: int = 3, max_words: int = 8) -> List[str]:
        """Extract meaningful phrases instead of just n-grams"""
        phrases = []
        
        # Split into sentences
        sentences = sent_tokenize(text)
        
        for sentence in sentences:
            # Tokenize words
            words = word_tokenize(sentence.lower())
            # Remove stopwords but keep meaningful words
            meaningful_words = [word for word in words if word not in self.stop_words and len(word) > 2]
            
            # Create phrases of different lengths
            for phrase_length in range(min_words, min(max_words + 1, len(meaningful_words) + 1)):
                for i in range(len(meaningful_words) - phrase_length + 1):
                    phrase = ' '.join(meaningful_words[i:i + phrase_length])
                    if len(phrase) > 10:  # Minimum character length
                        phrases.append(phrase)
        
        return list(set(phrases))  # Remove duplicates
    
    def create_sliding_window_phrases(self, text: str, window_size: int = 5) -> List[str]:
        """Create overlapping phrases using sliding window"""
        words = word_tokenize(text.lower())
        meaningful_words = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        phrases = []
        for i in range(len(meaningful_words) - window_size + 1):
            phrase = ' '.join(meaningful_words[i:i + window_size])
            if len(phrase) >= 15:  # Ensure reasonable length
                phrases.append(phrase)
        
        return phrases
    
    def create_ngrams(self, text: str, n: int = 6) -> List[str]:
        """Create character n-grams (keep for backward compatibility)"""
        if len(text) < n:
            return [text]
        
        ngrams = []
        for i in range(len(text) - n + 1):
            ngrams.append(text[i:i+n])
        
        return ngrams