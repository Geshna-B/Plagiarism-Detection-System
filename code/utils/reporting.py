import json
from datetime import datetime
from typing import Dict, List, Any

class ReportGenerator:
    """Generate comprehensive plagiarism reports"""
    
    @staticmethod
    def generate_report(results: Dict[str, Any], suspicious_text: str, sources: List[Dict]) -> Dict:
        """Generate a detailed plagiarism report"""
        
        report = {
            "analysis_date": datetime.now().isoformat(),
            "suspicious_text_preview": suspicious_text[:200] + "..." if len(suspicious_text) > 200 else suspicious_text,
            "sources_checked": len(sources),
            "overall_similarity": results.get("similarity_score", 0),
            "risk_level": ReportGenerator._assess_risk_level(results.get("similarity_score", 0)),
            "detailed_matches": results.get("matches", []),
            "sources_used": sources,
            "statistics": {
                "total_matches": len(results.get("matches", [])),
                "unique_patterns_matched": len(set(match['pattern'] for match in results.get("matches", []))),
                "average_match_length": sum(len(match['pattern']) for match in results.get("matches", [])) / max(1, len(results.get("matches", [])))
            }
        }
        
        return report
    
    @staticmethod
    def _assess_risk_level(similarity: float) -> str:
        """Assess plagiarism risk level"""
        if similarity >= 0.8:
            return "HIGH"
        elif similarity >= 0.5:
            return "MEDIUM"
        elif similarity >= 0.2:
            return "LOW"
        else:
            return "VERY LOW"
    
    @staticmethod
    def print_summary(report: Dict):
        """Print a user-friendly summary"""
        print("\n" + "="*60)
        print("📊 PLAGIARISM DETECTION REPORT")
        print("="*60)
        print(f"📅 Analysis Date: {report['analysis_date']}")
        print(f"🔍 Sources Checked: {report['sources_checked']}")
        print(f"📈 Overall Similarity: {report['overall_similarity']:.2%}")
        print(f"⚠️  Risk Level: {report['risk_level']}")
        #print(f"🔢 Total Matches Found: {report['statistics']['total_matches']}")
        #print(f"📏 Average Match Length: {report['statistics']['average_match_length']:.1f} chars")
        print("="*60)
        
        # Print detailed matches
        if report['detailed_matches example']:
            print("\n📋 DETAILED MATCHES:")
            for i, match in enumerate(report['detailed_matches'][10:13], 1):  # Show top 5
                print(f"{i}. Pattern: '{match['pattern']}'")
                print(f"   Source: {match['source']}")
                print(f"   Position: {match['position']}")
                print()
