#!/usr/bin/env python3
"""
Readability Scorer - Analyzes script complexity for spoken delivery
Evaluates whether scripts are appropriate for their target audience.
"""

import re
import json
import argparse
from typing import Dict, List, Tuple
import sys


class ReadabilityScorer:
    """Analyzes script readability and complexity for spoken delivery."""
    
    def __init__(self):
        """Initialize with syllable patterns and complexity rules."""
        # Common syllable patterns for English
        self.vowels = set('aeiouAEIOU')
        self.diphthongs = ['ai', 'au', 'ay', 'ea', 'ee', 'ei', 'ey', 'oa', 'oe', 'oi', 'oo', 'ou', 'oy']
        
        # AI clichés and complex phrases to flag
        self.ai_patterns = {
            'delve': 'Look at/Explore',
            'delving': 'Looking at/Exploring', 
            'comprehensive': 'Complete/Full',
            'leverage': 'Use',
            'utilize': 'Use',
            'implement': 'Put in place/Start',
            'facilitate': 'Help/Make easier',
            'optimize': 'Improve',
            'innovative': 'New/Creative',
            'robust': 'Strong/Solid',
            'paradigm': 'Approach/Model',
            'synergy': 'Working together',
            'ecosystem': 'System/Environment',
            'cutting-edge': 'Latest/Advanced',
            'game-changer': 'Important change',
            'revolutionize': 'Change completely',
            'transformative': 'Changed/Changing',
            'holistic': 'Complete/Whole',
            'seamless': 'Smooth/Easy',
            'scalable': 'Can grow'
        }
        
        # Complex transitions to simplify
        self.complex_transitions = {
            "It's important to note that": "Note:",
            "In light of this": "So",
            "With regard to": "About",
            "In order to": "To",
            "Due to the fact that": "Because",
            "At this point in time": "Now",
            "In the event that": "If",
            "For the purpose of": "To",
            "In accordance with": "Following",
            "As a consequence of": "Because of"
        }
    
    def analyze_script(self, script_text: str) -> Dict:
        """Perform complete readability analysis."""
        # Clean script for analysis
        cleaned_text = self.clean_for_analysis(script_text)
        
        # Basic metrics
        sentences = self.get_sentences(cleaned_text)
        words = self.get_words(cleaned_text)
        syllables = sum(self.count_syllables(word) for word in words)
        
        # Calculate readability scores
        scores = self.calculate_readability_scores(
            len(sentences),
            len(words),
            syllables
        )
        
        # Analyze complexity factors
        complexity = self.analyze_complexity(script_text)
        
        # Check for spoken delivery issues
        delivery_issues = self.check_delivery_issues(cleaned_text)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(scores, complexity, delivery_issues)
        
        return {
            'readability_scores': scores,
            'complexity_analysis': complexity,
            'delivery_issues': delivery_issues,
            'recommendations': recommendations,
            'statistics': {
                'sentences': len(sentences),
                'words': len(words),
                'syllables': syllables,
                'avg_words_per_sentence': round(len(words) / max(len(sentences), 1), 1),
                'avg_syllables_per_word': round(syllables / max(len(words), 1), 1)
            }
        }
    
    def clean_for_analysis(self, text: str) -> str:
        """Clean script text for readability analysis."""
        # Remove stage directions and production notes
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'\(.*?\)', '', text)
        
        # Remove speaker labels
        text = re.sub(r'^[A-Z\s]+:', '', text, flags=re.MULTILINE)
        
        # Handle two-column format
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            if '|' in line:
                parts = line.split('|')
                if len(parts) > 1:
                    cleaned_lines.append(parts[1].strip())
            else:
                cleaned_lines.append(line)
        
        return ' '.join(cleaned_lines)
    
    def get_sentences(self, text: str) -> List[str]:
        """Extract sentences from text."""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def get_words(self, text: str) -> List[str]:
        """Extract words from text."""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return words
    
    def count_syllables(self, word: str) -> int:
        """Estimate syllable count for a word."""
        word = word.lower()
        count = 0
        previous_was_vowel = False
        
        for i, char in enumerate(word):
            is_vowel = char in self.vowels
            if is_vowel and not previous_was_vowel:
                count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent e
        if word.endswith('e') and count > 1:
            count -= 1
        
        # Ensure at least 1 syllable
        return max(1, count)
    
    def calculate_readability_scores(self, sentences: int, words: int, syllables: int) -> Dict:
        """Calculate various readability scores."""
        if sentences == 0 or words == 0:
            return {
                'flesch_reading_ease': 0,
                'flesch_grade_level': 0,
                'interpretation': 'Insufficient content for analysis'
            }
        
        # Flesch Reading Ease
        # Higher scores = easier to read
        # 90-100: Very Easy (5th grade)
        # 80-90: Easy (6th grade)
        # 70-80: Fairly Easy (7th grade)  
        # 60-70: Standard (8th-9th grade)
        # 50-60: Fairly Difficult (10th-12th grade)
        # 30-50: Difficult (College)
        # 0-30: Very Difficult (Graduate)
        
        avg_sentence_length = words / sentences
        avg_syllables_per_word = syllables / words
        
        flesch_ease = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        flesch_ease = max(0, min(100, flesch_ease))  # Clamp to 0-100
        
        # Flesch-Kincaid Grade Level
        grade_level = (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59
        grade_level = max(0, grade_level)
        
        # Interpretation for spoken delivery
        if flesch_ease >= 80:
            interpretation = "Very easy - Good for all audiences"
            spoken_suitability = "Excellent"
        elif flesch_ease >= 70:
            interpretation = "Easy - Good for general audiences"
            spoken_suitability = "Very good"
        elif flesch_ease >= 60:
            interpretation = "Standard - Good for educated audiences"
            spoken_suitability = "Good"
        elif flesch_ease >= 50:
            interpretation = "Moderate complexity - May need simplification"
            spoken_suitability = "Fair - Consider simplifying"
        else:
            interpretation = "Complex - Difficult for spoken delivery"
            spoken_suitability = "Poor - Simplify for speech"
        
        return {
            'flesch_reading_ease': round(flesch_ease, 1),
            'flesch_grade_level': round(grade_level, 1),
            'interpretation': interpretation,
            'spoken_suitability': spoken_suitability
        }
    
    def analyze_complexity(self, text: str) -> Dict:
        """Analyze specific complexity factors."""
        complexity_issues = []
        
        # Check for AI patterns
        ai_found = []
        for pattern, replacement in self.ai_patterns.items():
            if re.search(r'\b' + pattern + r'\b', text, re.IGNORECASE):
                ai_found.append(f"'{pattern}' → '{replacement}'")
        
        if ai_found:
            complexity_issues.append({
                'type': 'AI Clichés',
                'severity': 'high',
                'found': ai_found,
                'impact': 'Sounds artificial and generic'
            })
        
        # Check for complex transitions
        transitions_found = []
        for complex, simple in self.complex_transitions.items():
            if complex.lower() in text.lower():
                transitions_found.append(f"'{complex}' → '{simple}'")
        
        if transitions_found:
            complexity_issues.append({
                'type': 'Complex Transitions',
                'severity': 'medium',
                'found': transitions_found,
                'impact': 'Slows down delivery and comprehension'
            })
        
        # Check for long sentences
        sentences = self.get_sentences(text)
        long_sentences = [s for s in sentences if len(s.split()) > 20]
        
        if long_sentences:
            complexity_issues.append({
                'type': 'Long Sentences',
                'severity': 'high',
                'count': len(long_sentences),
                'examples': [s[:50] + '...' for s in long_sentences[:3]],
                'impact': 'Difficult to deliver naturally, loses audience'
            })
        
        # Check for passive voice
        passive_patterns = [
            r'\b(is|are|was|were|been|being)\s+\w+ed\b',
            r'\b(is|are|was|were|been|being)\s+\w+en\b'
        ]
        
        passive_count = 0
        for pattern in passive_patterns:
            passive_count += len(re.findall(pattern, text, re.IGNORECASE))
        
        if passive_count > len(sentences) * 0.2:  # More than 20% passive
            complexity_issues.append({
                'type': 'Excessive Passive Voice',
                'severity': 'medium',
                'count': passive_count,
                'impact': 'Less engaging and harder to follow'
            })
        
        return {
            'issues_found': len(complexity_issues),
            'issues': complexity_issues
        }
    
    def check_delivery_issues(self, text: str) -> List[Dict]:
        """Check for issues that affect spoken delivery."""
        issues = []
        
        # Check for tongue twisters
        words = self.get_words(text)
        for i in range(len(words) - 2):
            if len(words[i]) > 2 and len(words[i+1]) > 2:
                # Check for similar starting sounds
                if words[i][0] == words[i+1][0] == words[i+2][0]:
                    phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
                    issues.append({
                        'type': 'Potential Tongue Twister',
                        'phrase': phrase,
                        'suggestion': 'Rephrase for easier delivery'
                    })
        
        # Check for difficult pronunciations
        difficult_words = []
        for word in set(words):
            if len(word) > 12 or self.count_syllables(word) > 4:
                difficult_words.append(word)
        
        if difficult_words:
            issues.append({
                'type': 'Complex Words',
                'words': difficult_words[:5],  # Show first 5
                'suggestion': 'Consider simpler alternatives'
            })
        
        # Check for missing breathing points
        sentences = self.get_sentences(text)
        for sentence in sentences:
            word_count = len(sentence.split())
            if word_count > 15 and ',' not in sentence and ';' not in sentence:
                issues.append({
                    'type': 'No Breathing Points',
                    'sentence': sentence[:50] + '...',
                    'suggestion': 'Add commas or break into shorter sentences'
                })
        
        return issues
    
    def generate_recommendations(self, scores: Dict, complexity: Dict, 
                                delivery_issues: List) -> List[str]:
        """Generate specific recommendations for improvement."""
        recommendations = []
        
        # Based on readability scores
        if scores['flesch_reading_ease'] < 60:
            recommendations.append("Simplify language - aim for 60+ reading ease score for spoken delivery")
        
        if scores['flesch_grade_level'] > 10:
            recommendations.append("Reduce complexity - target 8th-10th grade level for broad appeal")
        
        # Based on complexity analysis
        if complexity['issues_found'] > 0:
            for issue in complexity['issues']:
                if issue['severity'] == 'high':
                    if issue['type'] == 'AI Clichés':
                        recommendations.append("Replace AI clichés with natural language")
                    elif issue['type'] == 'Long Sentences':
                        recommendations.append("Break long sentences into shorter ones (max 15-20 words)")
                elif issue['severity'] == 'medium':
                    if issue['type'] == 'Complex Transitions':
                        recommendations.append("Simplify transitions for natural flow")
                    elif issue['type'] == 'Excessive Passive Voice':
                        recommendations.append("Convert passive voice to active for engagement")
        
        # Based on delivery issues
        if delivery_issues:
            for issue in delivery_issues:
                if issue['type'] == 'Complex Words':
                    recommendations.append("Replace complex words with simpler alternatives")
                elif issue['type'] == 'No Breathing Points':
                    recommendations.append("Add natural pauses and breathing points")
                elif issue['type'] == 'Potential Tongue Twister':
                    recommendations.append("Rephrase tongue twisters for smooth delivery")
        
        # If no major issues
        if not recommendations:
            recommendations.append("Script is well-optimized for spoken delivery!")
        
        return recommendations


def main():
    parser = argparse.ArgumentParser(description="Analyze script readability and complexity")
    parser.add_argument('script_file', help='Path to script file')
    parser.add_argument('--format', choices=['json', 'text'], default='text',
                       help='Output format')
    parser.add_argument('--verbose', action='store_true',
                       help='Show detailed analysis')
    
    args = parser.parse_args()
    
    # Read script file
    try:
        with open(args.script_file, 'r', encoding='utf-8') as f:
            script_text = f.read()
    except FileNotFoundError:
        print(f"Error: Script file '{args.script_file}' not found")
        sys.exit(1)
    
    # Analyze script
    scorer = ReadabilityScorer()
    results = scorer.analyze_script(script_text)
    
    # Output results
    if args.format == 'json':
        print(json.dumps(results, indent=2))
    else:
        # Text format output
        print("\n" + "=" * 60)
        print("SCRIPT READABILITY ANALYSIS")
        print("=" * 60)
        
        # Readability scores
        scores = results['readability_scores']
        print(f"\n📊 READABILITY SCORES:")
        print("-" * 40)
        print(f"Flesch Reading Ease: {scores['flesch_reading_ease']}/100")
        print(f"Grade Level: {scores['flesch_grade_level']}")
        print(f"Interpretation: {scores['interpretation']}")
        print(f"Spoken Suitability: {scores['spoken_suitability']}")
        
        # Statistics
        stats = results['statistics']
        print(f"\n📈 STATISTICS:")
        print("-" * 40)
        print(f"Sentences: {stats['sentences']}")
        print(f"Words: {stats['words']}")
        print(f"Avg Words/Sentence: {stats['avg_words_per_sentence']}")
        print(f"Avg Syllables/Word: {stats['avg_syllables_per_word']}")
        
        # Complexity issues
        if args.verbose and results['complexity_analysis']['issues_found'] > 0:
            print(f"\n⚠️  COMPLEXITY ISSUES:")
            print("-" * 40)
            for issue in results['complexity_analysis']['issues']:
                print(f"\n{issue['type']} (Severity: {issue['severity']})")
                print(f"Impact: {issue['impact']}")
                if 'found' in issue:
                    for item in issue['found'][:3]:
                        print(f"  • {item}")
                if 'examples' in issue:
                    for example in issue['examples'][:2]:
                        print(f"  • {example}")
        
        # Delivery issues
        if args.verbose and results['delivery_issues']:
            print(f"\n🎤 DELIVERY ISSUES:")
            print("-" * 40)
            for issue in results['delivery_issues'][:5]:
                print(f"\n{issue['type']}")
                if 'phrase' in issue:
                    print(f"  Found: {issue['phrase']}")
                if 'words' in issue:
                    print(f"  Words: {', '.join(issue['words'][:3])}")
                print(f"  Suggestion: {issue['suggestion']}")
        
        # Recommendations
        print(f"\n✅ RECOMMENDATIONS:")
        print("-" * 40)
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"{i}. {rec}")


if __name__ == "__main__":
    main()
