#!/usr/bin/env python3
"""
Script Timer - Calculate reading time and pace for scripts
Provides accurate timing estimates for different delivery speeds and script types.
"""

import re
import argparse
from typing import Dict, List, Tuple
import json


class ScriptTimer:
    """Analyzes script timing and pacing."""
    
    # Words per minute for different delivery speeds
    PACE_SETTINGS = {
        'slow': 120,         # Thoughtful, dramatic
        'moderate': 150,     # Standard narration
        'conversational': 160,  # Natural speech
        'fast': 180,         # Energetic delivery
        'rapid': 200        # Time-constrained
    }
    
    # Pause durations in seconds
    PAUSE_DURATIONS = {
        '[PAUSE]': 1.0,
        '[SHORT PAUSE]': 0.5,
        '[LONG PAUSE]': 2.0,
        '[BEAT]': 0.5,
        '...': 0.5,
        '--': 0.3,
        ':': 0.2,
        ';': 0.15,
        '.': 0.3,
        '?': 0.3,
        '!': 0.3
    }
    
    def __init__(self, pace: str = 'moderate'):
        """Initialize with specified pace."""
        self.wpm = self.PACE_SETTINGS.get(pace, 150)
        self.pace = pace
    
    def analyze_script(self, script_text: str) -> Dict:
        """Analyze complete script for timing and statistics."""
        # Clean script of production notes
        cleaned_text = self.clean_script(script_text)
        
        # Calculate basic metrics
        word_count = self.count_words(cleaned_text)
        sentence_count = self.count_sentences(cleaned_text)
        pause_time = self.calculate_pauses(script_text)
        
        # Calculate reading time
        reading_time = (word_count / self.wpm) * 60  # in seconds
        total_time = reading_time + pause_time
        
        # Section analysis
        sections = self.analyze_sections(script_text)
        
        # Pacing analysis
        pacing = self.analyze_pacing(cleaned_text)
        
        return {
            'total_time_seconds': round(total_time, 1),
            'total_time_formatted': self.format_time(total_time),
            'word_count': word_count,
            'sentence_count': sentence_count,
            'average_sentence_length': round(word_count / max(sentence_count, 1), 1),
            'reading_time_seconds': round(reading_time, 1),
            'pause_time_seconds': round(pause_time, 1),
            'pace_setting': self.pace,
            'words_per_minute': self.wpm,
            'sections': sections,
            'pacing_analysis': pacing
        }
    
    def clean_script(self, text: str) -> str:
        """Remove production notes and markers from script."""
        # Remove content in brackets except dialogue markers
        text = re.sub(r'\[(?!PAUSE|SHORT PAUSE|LONG PAUSE|BEAT)[^\]]*\]', '', text)
        
        # Remove stage directions in parentheses
        text = re.sub(r'\([^)]*\)', '', text)
        
        # Remove speaker labels
        text = re.sub(r'^[A-Z\s]+:', '', text, flags=re.MULTILINE)
        
        # Remove visual column if in two-column format
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            if '|' in line:
                # Assume audio is after the pipe
                parts = line.split('|')
                if len(parts) > 1:
                    cleaned_lines.append(parts[1].strip())
            else:
                cleaned_lines.append(line)
        
        return ' '.join(cleaned_lines)
    
    def count_words(self, text: str) -> int:
        """Count words in text."""
        # Remove extra spaces and count
        text = re.sub(r'\s+', ' ', text).strip()
        words = text.split(' ') if text else []
        # Filter out empty strings and punctuation-only
        words = [w for w in words if w and re.search(r'\w', w)]
        return len(words)
    
    def count_sentences(self, text: str) -> int:
        """Count sentences in text."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        # Filter out empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        return len(sentences)
    
    def calculate_pauses(self, text: str) -> float:
        """Calculate total pause time in seconds."""
        total_pause = 0.0
        
        for marker, duration in self.PAUSE_DURATIONS.items():
            if marker in ['...', '--', ':', ';', '.', '?', '!']:
                # Count punctuation marks
                count = text.count(marker)
                total_pause += count * duration
            else:
                # Count specific pause markers
                count = len(re.findall(re.escape(marker), text, re.IGNORECASE))
                total_pause += count * duration
        
        return total_pause
    
    def analyze_sections(self, text: str) -> List[Dict]:
        """Analyze individual sections of the script."""
        sections = []
        
        # Try to identify sections by headers or double newlines
        parts = re.split(r'\n\n+', text)
        
        for i, part in enumerate(parts):
            if not part.strip():
                continue
            
            cleaned = self.clean_script(part)
            word_count = self.count_words(cleaned)
            
            if word_count > 0:
                reading_time = (word_count / self.wpm) * 60
                pause_time = self.calculate_pauses(part)
                
                sections.append({
                    'section_number': i + 1,
                    'preview': part[:50] + '...' if len(part) > 50 else part,
                    'word_count': word_count,
                    'time_seconds': round(reading_time + pause_time, 1),
                    'time_formatted': self.format_time(reading_time + pause_time)
                })
        
        return sections
    
    def analyze_pacing(self, text: str) -> Dict:
        """Analyze pacing characteristics of the script."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return {
                'variety': 'N/A',
                'rhythm': 'N/A',
                'recommendation': 'Add content to analyze'
            }
        
        # Calculate sentence length variety
        lengths = [self.count_words(s) for s in sentences]
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        
        # Calculate standard deviation for variety
        if len(lengths) > 1:
            variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
            std_dev = variance ** 0.5
            variety_score = std_dev / max(avg_length, 1)
        else:
            variety_score = 0
        
        # Determine variety level
        if variety_score < 0.2:
            variety = 'Monotonous - vary sentence lengths'
        elif variety_score < 0.4:
            variety = 'Moderate - could use more variety'
        else:
            variety = 'Good - natural rhythm'
        
        # Check for rhythm patterns
        short_sentences = sum(1 for l in lengths if l < 10)
        medium_sentences = sum(1 for l in lengths if 10 <= l <= 20)
        long_sentences = sum(1 for l in lengths if l > 20)
        
        total = len(sentences)
        rhythm = {
            'short_percent': round(short_sentences / total * 100, 1),
            'medium_percent': round(medium_sentences / total * 100, 1),
            'long_percent': round(long_sentences / total * 100, 1)
        }
        
        # Recommendation based on script type
        if avg_length > 20:
            recommendation = 'Sentences too long for spoken delivery. Aim for 15 words average.'
        elif avg_length < 8:
            recommendation = 'Sentences very short. May sound choppy unless intentional.'
        else:
            recommendation = 'Good average length for spoken delivery.'
        
        return {
            'average_sentence_length': round(avg_length, 1),
            'variety': variety,
            'rhythm': rhythm,
            'recommendation': recommendation
        }
    
    def format_time(self, seconds: float) -> str:
        """Format seconds into readable time."""
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        
        if minutes > 0:
            return f"{minutes}:{remaining_seconds:02d}"
        else:
            return f"0:{remaining_seconds:02d}"
    
    def estimate_video_length(self, script_text: str, include_visuals: bool = True) -> Dict:
        """Estimate final video length including visual considerations."""
        base_analysis = self.analyze_script(script_text)
        
        if include_visuals:
            # Add time for visual elements
            b_roll_time = base_analysis['word_count'] * 0.1  # 10% additional for B-roll
            transition_time = base_analysis['sentence_count'] * 0.2  # 0.2s per transition
            
            total_video_time = base_analysis['total_time_seconds'] + b_roll_time + transition_time
            
            return {
                'script_time': base_analysis['total_time_formatted'],
                'estimated_video_time': self.format_time(total_video_time),
                'b_roll_allowance': self.format_time(b_roll_time),
                'transition_allowance': self.format_time(transition_time),
                'notes': 'Includes estimates for B-roll and transitions'
            }
        
        return {
            'script_time': base_analysis['total_time_formatted'],
            'estimated_video_time': base_analysis['total_time_formatted'],
            'notes': 'Audio only - no visual timing included'
        }


def main():
    parser = argparse.ArgumentParser(description="Calculate script timing and pace")
    parser.add_argument('script_file', help='Path to script file')
    parser.add_argument('--pace', choices=['slow', 'moderate', 'conversational', 'fast', 'rapid'],
                       default='moderate', help='Delivery pace')
    parser.add_argument('--format', choices=['json', 'text'], default='text',
                       help='Output format')
    parser.add_argument('--video', action='store_true',
                       help='Include video timing estimates')
    
    args = parser.parse_args()
    
    # Read script file
    try:
        with open(args.script_file, 'r', encoding='utf-8') as f:
            script_text = f.read()
    except FileNotFoundError:
        print(f"Error: Script file '{args.script_file}' not found")
        return
    
    # Analyze script
    timer = ScriptTimer(pace=args.pace)
    
    if args.video:
        results = timer.estimate_video_length(script_text)
    else:
        results = timer.analyze_script(script_text)
    
    # Output results
    if args.format == 'json':
        print(json.dumps(results, indent=2))
    else:
        # Text format output
        print("\n" + "=" * 60)
        print("SCRIPT TIMING ANALYSIS")
        print("=" * 60)
        
        if args.video:
            print(f"\nScript Time: {results['script_time']}")
            print(f"Estimated Video Time: {results['estimated_video_time']}")
            print(f"Notes: {results['notes']}")
        else:
            print(f"\nTotal Time: {results['total_time_formatted']}")
            print(f"Word Count: {results['word_count']}")
            print(f"Pace: {results['pace_setting']} ({results['words_per_minute']} wpm)")
            print(f"Average Sentence Length: {results['average_sentence_length']} words")
            
            if results['sections']:
                print(f"\n\nSECTION BREAKDOWN:")
                print("-" * 40)
                for section in results['sections']:
                    print(f"Section {section['section_number']}: {section['time_formatted']} ({section['word_count']} words)")
            
            if results['pacing_analysis']:
                pacing = results['pacing_analysis']
                print(f"\n\nPACING ANALYSIS:")
                print("-" * 40)
                print(f"Variety: {pacing['variety']}")
                if isinstance(pacing['rhythm'], dict):
                    print(f"Sentence Distribution:")
                    print(f"  Short (<10 words): {pacing['rhythm']['short_percent']}%")
                    print(f"  Medium (10-20 words): {pacing['rhythm']['medium_percent']}%")
                    print(f"  Long (>20 words): {pacing['rhythm']['long_percent']}%")
                print(f"Recommendation: {pacing['recommendation']}")


if __name__ == "__main__":
    main()
