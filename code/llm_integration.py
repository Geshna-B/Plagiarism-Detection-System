import wikipedia
from langchain.chat_models import init_chat_model
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from utils.config import Config

class LLMIntegration:
    """LLM-powered content collection and analysis"""
    
    def __init__(self):
        Config.validate_config()
        
        # Initialize LLM
        self.llm = init_chat_model(
            Config.LLM_MODEL, 
            model_provider="groq", 
            api_key=Config.GROQ_API_KEY
        )
        
        # Initialize Wikipedia tool
        self.wikipedia_tool = WikipediaQueryRun(
            api_wrapper=WikipediaAPIWrapper(
                top_k_results=Config.WIKIPEDIA_MAX_RESULTS,
                doc_content_chars_max=Config.WIKIPEDIA_MAX_CHARS
            )
        )
    
    def expand_topic(self, topic: str) -> list[str]:
        """Use LLM to find related topics for comprehensive checking"""
        
        prompt = f"""
        Given the main topic: "{topic}", generate a list of 5-7 closely related 
        subtopics, specific concepts, or alternative phrasings that someone might 
        use when writing about this topic. Return ONLY a Python list format.
        
        Example: 
        Input: "machine learning"
        Output: ["supervised learning", "neural networks", "deep learning", "classification algorithms", "regression analysis"]
        
        Now for topic: "{topic}"
        """
        
        try:
            response = self.llm.invoke(prompt)
            # Extract list from response
            import ast
            related_topics = ast.literal_eval(response.content)
            return [topic] + related_topics  # Include original topic
        except:
            # Fallback if LLM fails
            return [topic]
    
    def fetch_wikipedia_content(self, topics: list[str]) -> list[dict]:
        """Fetch content from Wikipedia for given topics"""
        
        sources = []
        
        for topic in topics:
            try:
                print(f"📚 Fetching Wikipedia content for: {topic}")
                content = self.wikipedia_tool.invoke({"query": topic})
                
                if content and len(content) > 100:  # Minimum content length
                    sources.append({
                        'topic': topic,
                        'content': content,
                        'source': f"Wikipedia: {topic}",
                        'length': len(content)
                    })
                    print(f"✅ Found content ({len(content)} chars)")
                else:
                    print(f"❌ Insufficient content for: {topic}")
                    
            except Exception as e:
                print(f"❌ Error fetching {topic}: {str(e)}")
                continue
        
        return sources
    
    def analyze_writing_style(self, text: str) -> dict:
        """Use LLM to analyze writing style characteristics"""
        
        prompt = f"""
        Analyze the following text and identify its key characteristics:
        "{text[:500]}..."  # First 500 chars for analysis
        
        Provide a brief analysis of:
        1. Writing style (academic, casual, technical, etc.)
        2. Likely educational level
        3. Any distinctive phrases or patterns
        
        Return analysis in 3-4 bullet points.
        """
        
        try:
            response = self.llm.invoke(prompt)
            return {'style_analysis': response.content}
        except:
            return {'style_analysis': 'Analysis unavailable'}
