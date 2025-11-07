#!/usr/bin/env python3
"""
Main Plagiarism Detection System
Combining LLM + Wikipedia + Automata Theory
"""
# Add this at the beginning of main.py to fix import paths
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import json
from detectors.llm_integration import LLMIntegration
from detectors.automata_detector import PlagiarismDetector
from utils.reporting import ReportGenerator
from utils.config import Config
from detectors.text_processor import TextProcessor


class PlagiarismDetectionSystem:
    """Complete plagiarism detection system"""
    
    def __init__(self):
        self.llm_integration = LLMIntegration()
        self.detector = PlagiarismDetector()
        self.reporter = ReportGenerator()
    
    def analyze_text(self, suspicious_text: str, main_topic: str = None) -> dict:
        """Main analysis pipeline"""
        
        print("🚀 Starting Plagiarism Analysis...")
        
        # If no topic provided, detect it from text
        if not main_topic:
            main_topic = self._detect_topic(suspicious_text)
            print(f"🔍 Detected topic: {main_topic}")
        
        # Step 1: Expand topic and fetch Wikipedia content
        print("📖 Gathering relevant source content...")
        related_topics = self.llm_integration.expand_topic(main_topic)
        source_texts = self.llm_integration.fetch_wikipedia_content(related_topics)
        
        if not source_texts:
            print("❌ No source content found. Please try a different topic.")
            return None
        
        # Step 2: Perform automata-based plagiarism detection
        print("🤖 Running automata-based detection...")
        detection_results = self.detector.detect_plagiarism(suspicious_text, source_texts)
        
        # Step 3: Generate comprehensive report
        print("📊 Generating report...")
        report = self.reporter.generate_report(detection_results, suspicious_text, source_texts)
        
        return report
    
    def _detect_topic(self, text: str) -> str:
        """Detect main topic from text using LLM"""
        prompt = f"""
        Extract the main topic or subject from the following text. 
        Return ONLY the topic as a short phrase (2-4 words).
        
        Text: "{text[:300]}..."  # First 300 characters
        
        Topic:
        """
        
        try:
            response = self.llm_integration.llm.invoke(prompt)
            return response.content.strip()
        except:
            return "general topic"

def main():
    """Main function with example usage"""
    
    # Example suspicious text (you can replace this)
    sample_text = """
    Finite automata are fundamental computational models in computer science that 
    process input strings through a series of states. These abstract machines 
    consist of states, transitions, and acceptance criteria. They are particularly 
    useful for pattern matching and lexical analysis in compiler design. 
    The theory of finite automata forms the basis for understanding more complex 
    computational models like pushdown automata and Turing machines.
    """
    
    # Initialize the system
    try:
        system = PlagiarismDetectionSystem()
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        print("💡 Make sure you have set GROQ_API_KEY in your environment variables")
        sys.exit(1)
    
    # User interaction
    print("🤖 Welcome to the Advanced Plagiarism Detection System!")
    print("=" * 60)
    
    use_sample = input("Use sample text? (y/n): ").lower().strip()
    
    if use_sample == 'n':
        print("Enter your text (press Enter twice when done):")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        user_text = '\n'.join(lines)
        user_topic = input("Enter main topic (or press Enter for auto-detection): ").strip() or None
    else:
        user_text = sample_text
        user_topic = "finite automata"
        print("Using sample text about finite automata...")
    
    # Run analysis
    try:
        report = system.analyze_text(user_text, user_topic)
        
        if report:
            # Print summary
            system.reporter.print_summary(report)
            
            # Option to save full report
            save_report = input("\n💾 Save full report to file? (y/n): ").lower().strip()
            if save_report == 'y':
                filename = f"plagiarism_report_{report['analysis_date'][:10]}.json"
                with open(filename, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"✅ Report saved as {filename}")
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        print("💡 This might be due to API limits or network issues")

if __name__ == "__main__":
    main()
