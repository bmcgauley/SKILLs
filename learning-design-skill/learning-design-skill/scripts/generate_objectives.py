#!/usr/bin/env python3
"""
Generate Learning Objectives from Topics
Automatically creates SMART learning objectives using Bloom's Taxonomy
"""

import json
import sys
from typing import List, Dict, Tuple
import argparse

# Bloom's Taxonomy action verbs by level
BLOOMS_VERBS = {
    "Remember": {
        "verbs": ["identify", "list", "name", "recognize", "recall", "state", "describe", "match", "select", "label"],
        "question_stems": ["What is...", "Who was...", "When did...", "How many...", "Which one..."],
        "products": ["list", "definition", "fact", "label", "workbook", "quiz", "test"]
    },
    "Understand": {
        "verbs": ["explain", "summarize", "interpret", "classify", "compare", "contrast", "discuss", "distinguish", "predict", "paraphrase"],
        "question_stems": ["How would you explain...", "What is the main idea...", "What differences exist...", "Can you provide an example..."],
        "products": ["summary", "explanation", "diagram", "outline", "presentation", "report"]
    },
    "Apply": {
        "verbs": ["apply", "demonstrate", "solve", "implement", "use", "execute", "carry out", "practice", "calculate", "complete"],
        "question_stems": ["How would you use...", "What would result if...", "How would you solve...", "What approach would you use..."],
        "products": ["demonstration", "simulation", "presentation", "calculation", "solution", "model"]
    },
    "Analyze": {
        "verbs": ["analyze", "examine", "compare", "contrast", "differentiate", "organize", "deconstruct", "investigate", "categorize", "critique"],
        "question_stems": ["What are the components...", "How is ___ related to...", "Why do you think...", "What evidence can you find..."],
        "products": ["report", "chart", "diagram", "survey", "database", "spreadsheet", "checklist"]
    },
    "Evaluate": {
        "verbs": ["evaluate", "assess", "judge", "justify", "critique", "defend", "recommend", "prioritize", "rate", "decide"],
        "question_stems": ["What is your opinion...", "How would you prioritize...", "What criteria would you use...", "Do you agree with..."],
        "products": ["recommendation", "evaluation", "critique", "justification", "assessment", "editorial"]
    },
    "Create": {
        "verbs": ["create", "design", "develop", "construct", "produce", "generate", "formulate", "compose", "invent", "devise"],
        "question_stems": ["What would you create...", "How would you design...", "What new solution...", "Can you develop..."],
        "products": ["model", "product", "plan", "proposal", "project", "composition", "solution"]
    }
}

def generate_objective(topic: str, level: str, context: str = "") -> Dict[str, str]:
    """
    Generate a learning objective for a given topic and Bloom's level
    
    Args:
        topic: The subject matter or concept
        level: Bloom's Taxonomy level
        context: Optional context or conditions
    
    Returns:
        Dictionary containing the formatted objective and components
    """
    if level not in BLOOMS_VERBS:
        raise ValueError(f"Invalid Bloom's level: {level}")
    
    verbs = BLOOMS_VERBS[level]["verbs"]
    verb = verbs[hash(topic) % len(verbs)]  # Deterministic selection based on topic
    
    # Build SMART objective
    objective = {
        "topic": topic,
        "level": level,
        "verb": verb,
        "condition": context if context else "After completing this module",
        "audience": "learners",
        "behavior": f"{verb} {topic}",
        "degree": "with 80% accuracy" if level in ["Remember", "Understand", "Apply"] else "meeting all rubric criteria"
    }
    
    # Format complete objective
    objective["full_text"] = f"{objective['condition']}, {objective['audience']} will {objective['behavior']} {objective['degree']}"
    
    # Add assessment suggestion
    products = BLOOMS_VERBS[level]["products"]
    objective["suggested_assessment"] = products[hash(topic + "assessment") % len(products)]
    
    return objective

def analyze_topic_complexity(topic: str) -> str:
    """
    Analyze topic to suggest appropriate Bloom's level
    
    Args:
        topic: The topic to analyze
    
    Returns:
        Suggested Bloom's Taxonomy level
    """
    # Simple heuristic based on keywords
    topic_lower = topic.lower()
    
    if any(word in topic_lower for word in ["basic", "fundamental", "introduction", "overview", "terminology"]):
        return "Remember"
    elif any(word in topic_lower for word in ["concept", "principle", "theory", "relationship", "comparison"]):
        return "Understand"
    elif any(word in topic_lower for word in ["calculate", "solve", "implement", "demonstrate", "practice"]):
        return "Apply"
    elif any(word in topic_lower for word in ["analyze", "examine", "investigate", "compare", "contrast"]):
        return "Analyze"
    elif any(word in topic_lower for word in ["evaluate", "assess", "critique", "judge", "recommend"]):
        return "Evaluate"
    elif any(word in topic_lower for word in ["create", "design", "develop", "propose", "build"]):
        return "Create"
    else:
        return "Understand"  # Default to Understand level

def create_objective_sequence(topics: List[str], progression: bool = True) -> List[Dict]:
    """
    Create a sequence of objectives with optional cognitive progression
    
    Args:
        topics: List of topics to create objectives for
        progression: Whether to apply cognitive progression
    
    Returns:
        List of objective dictionaries
    """
    objectives = []
    levels = list(BLOOMS_VERBS.keys())
    
    for i, topic in enumerate(topics):
        if progression:
            # Progress through Bloom's levels
            level_index = min(i * len(levels) // len(topics), len(levels) - 1)
            level = levels[level_index]
        else:
            # Analyze each topic individually
            level = analyze_topic_complexity(topic)
        
        obj = generate_objective(topic, level)
        obj["sequence_number"] = i + 1
        objectives.append(obj)
    
    return objectives

def format_objectives_output(objectives: List[Dict], format_type: str = "text") -> str:
    """
    Format objectives for output
    
    Args:
        objectives: List of objective dictionaries
        format_type: Output format (text, json, markdown, csv)
    
    Returns:
        Formatted string
    """
    if format_type == "json":
        return json.dumps(objectives, indent=2)
    
    elif format_type == "markdown":
        output = "# Learning Objectives\n\n"
        for obj in objectives:
            output += f"## Objective {obj.get('sequence_number', '')}: {obj['topic']}\n"
            output += f"**Bloom's Level:** {obj['level']}\n\n"
            output += f"**Objective:** {obj['full_text']}\n\n"
            output += f"**Suggested Assessment:** {obj['suggested_assessment']}\n\n"
            output += "---\n\n"
        return output
    
    elif format_type == "csv":
        output = "Sequence,Topic,Level,Verb,Full Objective,Assessment\n"
        for obj in objectives:
            output += f"{obj.get('sequence_number', '')},{obj['topic']},{obj['level']},{obj['verb']},\"{obj['full_text']}\",{obj['suggested_assessment']}\n"
        return output
    
    else:  # text format
        output = "LEARNING OBJECTIVES\n" + "=" * 50 + "\n\n"
        for obj in objectives:
            output += f"Objective {obj.get('sequence_number', '')}:\n"
            output += f"  Topic: {obj['topic']}\n"
            output += f"  Level: {obj['level']}\n"
            output += f"  Statement: {obj['full_text']}\n"
            output += f"  Assessment: {obj['suggested_assessment']}\n\n"
        return output

def main():
    parser = argparse.ArgumentParser(description='Generate learning objectives from topics')
    parser.add_argument('topics', nargs='*', help='Topics to generate objectives for')
    parser.add_argument('-f', '--file', help='File containing topics (one per line)')
    parser.add_argument('-l', '--level', help='Specific Bloom\'s level to use')
    parser.add_argument('-p', '--progression', action='store_true', 
                       help='Apply cognitive progression through Bloom\'s levels')
    parser.add_argument('-o', '--output', choices=['text', 'json', 'markdown', 'csv'],
                       default='text', help='Output format')
    
    args = parser.parse_args()
    
    # Get topics from arguments or file
    topics = []
    if args.file:
        with open(args.file, 'r') as f:
            topics = [line.strip() for line in f if line.strip()]
    elif args.topics:
        topics = args.topics
    else:
        print("Error: Please provide topics either as arguments or via -f file")
        sys.exit(1)
    
    # Generate objectives
    if args.level:
        # Use specific level for all topics
        objectives = [generate_objective(topic, args.level) for topic in topics]
        for i, obj in enumerate(objectives):
            obj['sequence_number'] = i + 1
    else:
        # Use progression or auto-detection
        objectives = create_objective_sequence(topics, args.progression)
    
    # Output results
    print(format_objectives_output(objectives, args.output))

if __name__ == "__main__":
    main()
