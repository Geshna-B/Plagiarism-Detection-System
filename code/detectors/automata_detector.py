from typing import List, Dict, Any
from collections import defaultdict
from .text_processor import TextProcessor

class AhoCorasickAutomaton:
    """Aho-Corasick algorithm for multiple pattern matching"""
    
    def __init__(self):
        self.goto = {}
        self.fail = {}
        self.output = defaultdict(list)
        self.patterns = []
    
    def build_automaton(self, patterns: List[str]):
        """Build the automaton from patterns"""
        self.patterns = patterns
        self.goto = {}
        self.fail = {}
        self.output = defaultdict(list)
        
        # Start with state 0
        self.goto[0] = {}
        state_counter = 1
        
        # Build goto function - FIXED VERSION
        for pattern in patterns:
            current_state = 0
            for char in pattern:
                if current_state not in self.goto:
                    self.goto[current_state] = {}
                
                if char in self.goto[current_state]:
                    current_state = self.goto[current_state][char]
                else:
                    # Create new state
                    new_state = state_counter
                    self.goto[current_state][char] = new_state
                    self.goto[new_state] = {}
                    current_state = new_state
                    state_counter += 1
            
            # Mark output for the final state of this pattern
            self.output[current_state].append(pattern)
        
        # Build failure function using BFS - FIXED VERSION
        queue = []
        
        # Initialize failure for depth 1 states
        for char, next_state in self.goto[0].items():
            self.fail[next_state] = 0
            queue.append(next_state)
        
        # Process states in BFS order
        while queue:
            current_state = queue.pop(0)
            
            for char, next_state in self.goto[current_state].items():
                queue.append(next_state)
                
                # Find failure state
                fail_state = self.fail[current_state]
                while fail_state != 0 and char not in self.goto[fail_state]:
                    fail_state = self.fail[fail_state]
                
                self.fail[next_state] = self.goto[fail_state].get(char, 0)
                
                # Merge outputs
                self.output[next_state].extend(self.output[self.fail[next_state]])
    
    def search(self, text: str) -> List[Dict[str, Any]]:
        """Search for patterns in text"""
        matches = []
        current_state = 0
        
        for position, char in enumerate(text):
            # Follow failure links until we find a valid transition
            while current_state != 0 and char not in self.goto[current_state]:
                current_state = self.fail[current_state]
            
            # Take the goto transition if available
            if char in self.goto[current_state]:
                current_state = self.goto[current_state][char]
            else:
                current_state = 0  # No transition, go back to start
            
            # Check for matches at current state
            if self.output[current_state]:
                for pattern in self.output[current_state]:
                    start_pos = position - len(pattern) + 1
                    matches.append({
                        'pattern': pattern,
                        'position': start_pos,
                        'length': len(pattern),
                        'end_position': position
                    })
        
        return matches

class PlagiarismDetector:
    """Main plagiarism detection engine"""
    
    def __init__(self):
        self.automaton = AhoCorasickAutomaton()
        self.text_processor = TextProcessor()
    
    def calculate_similarity(self, suspicious_text: str, matches: List[Dict]) -> float:
        """Calculate similarity score based on matches - FIXED"""
        if not suspicious_text or not matches:
            return 0.0
        
        # Use normalized text length for accurate calculation
        normalized_text = self.text_processor.normalize_text(suspicious_text)
        if not normalized_text:
            return 0.0
        
        # Count unique character positions to avoid double-counting
        matched_positions = set()
        for match in matches:
            for i in range(match['position'], match['position'] + match['length']):
                if i < len(normalized_text):
                    matched_positions.add(i)
        
        total_matched_chars = len(matched_positions)
        similarity = total_matched_chars / len(normalized_text)
        
        # Cap at 100%
        return min(similarity, 1.0)
    
    def detect_plagiarism(self, suspicious_text: str, source_texts: List[Dict]) -> Dict[str, Any]:
        """Main detection function with better error handling"""
        try:
            if not suspicious_text or not source_texts:
                return {
                    'similarity_score': 0.0,
                    'matches': [],
                    'patterns_used': 0,
                    'normalized_text_length': 0,
                    'error': 'No text or sources provided'
                }
            
            # Normalize suspicious text
            normalized_suspicious = self.text_processor.normalize_text(suspicious_text)
            if len(normalized_suspicious) < 10:  # Too short for meaningful analysis
                return {
                    'similarity_score': 0.0,
                    'matches': [],
                    'patterns_used': 0,
                    'normalized_text_length': len(normalized_suspicious),
                    'error': 'Text too short after normalization'
                }
            
            # Extract patterns from all source texts
            all_patterns = []
            source_mapping = {}
            
            for source in source_texts:
                if not source.get('content'):
                    continue
                    
                normalized_content = self.text_processor.normalize_text(source['content'])
                if len(normalized_content) < 10:
                    continue
                
                patterns = self.text_processor.create_ngrams(normalized_content, n=6)
                
                for pattern in patterns:
                    if len(pattern) >= 4:  # Minimum pattern length
                        all_patterns.append(pattern)
                        source_mapping[pattern] = source.get('topic', 'Unknown')
            
            if not all_patterns:
                return {
                    'similarity_score': 0.0,
                    'matches': [],
                    'patterns_used': 0,
                    'normalized_text_length': len(normalized_suspicious),
                    'error': 'No valid patterns extracted from sources'
                }
            
            # Remove duplicates and build automaton
            unique_patterns = list(set(all_patterns))
            print(f"🔍 Building automaton with {len(unique_patterns)} unique patterns...")
            
            self.automaton.build_automaton(unique_patterns)
            
            # Search for matches
            matches = self.automaton.search(normalized_suspicious)
            print(f"🔍 Found {len(matches)} potential matches...")
            
            # Add source information to matches
            for match in matches:
                pattern = match['pattern']
                match['source'] = source_mapping.get(pattern, "Unknown")
            
            # Calculate similarity score
            similarity = self.calculate_similarity(suspicious_text, matches)
            
            return {
                'similarity_score': similarity,
                'matches': matches[:40],  # Limit to first 20 matches for performance
                'patterns_used': len(unique_patterns),
                'normalized_text_length': len(normalized_suspicious),
                'error': None
            }
            
        except Exception as e:
            return {
                'similarity_score': 0.0,
                'matches': [],
                'patterns_used': 0,
                'normalized_text_length': 0,
                'error': f"Detection error: {str(e)}"
            }