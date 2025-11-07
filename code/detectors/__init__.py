"""
Plagiarism Detection Modules
"""

from .text_processor import TextProcessor
from .automata_detector import AhoCorasickAutomaton, PlagiarismDetector
from .llm_integration import LLMIntegration

__all__ = [
    'TextProcessor',
    'AhoCorasickAutomaton', 
    'PlagiarismDetector',
    'LLMIntegration'
]