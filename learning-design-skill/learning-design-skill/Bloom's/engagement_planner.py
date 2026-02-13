#!/usr/bin/env python3
"""
Engagement Activity Planner
Generate engagement activities based on ARCS model and active learning principles
"""

import json
import random
import argparse
from typing import List, Dict, Tuple

class EngagementPlanner:
    """Generate engagement activities for different learning contexts"""
    
    def __init__(self):
        # ARCS Model Components
        self.arcs_strategies = {
            "Attention": {
                "strategies": [
                    "Surprising statistics or facts",
                    "Thought-provoking questions", 
                    "Real-world problem scenarios",
                    "Contradictory examples",
                    "Visual demonstrations",
                    "Interactive polls",
                    "Short videos or animations",
                    "Personal anecdotes"
                ],
                "timing": "beginning",
                "duration": "2-3 minutes"
            },
            "Relevance": {
                "strategies": [
                    "Connect to career goals",
                    "Use familiar examples",
                    "Show practical applications",
                    "Link to personal interests",
                    "Present role models",
                    "Highlight future usefulness",
                    "Address 'why this matters'",
                    "Use case studies from their field"
                ],
                "timing": "throughout",
                "duration": "integrated"
            },
            "Confidence": {
                "strategies": [
                    "Start with simple tasks",
                    "Provide clear expectations",
                    "Offer scaffolded practice",
                    "Give immediate feedback",
                    "Create success opportunities",
                    "Provide examples and non-examples",
                    "Offer choice in difficulty",
                    "Use self-assessment tools"
                ],
                "timing": "middle",
                "duration": "5-10 minutes"
            },
            "Satisfaction": {
                "strategies": [
                    "Immediate application opportunities",
                    "Recognition of achievement",
                    "Peer sharing of work",
                    "Real-world project completion",
                    "Portfolio development",
                    "Celebration of milestones",
                    "Reflection activities",
                    "Certificate or badge earning"
                ],
                "timing": "end",
                "duration": "5-10 minutes"
            }
        }
        
        # Active Learning Techniques
        self.active_techniques = {
            "Think-Pair-Share": {
                "description": "Individual reflection, partner discussion, group sharing",
                "duration": "5-10 minutes",
                "group_size": "2-4",
                "best_for": ["concept review", "problem solving", "opinion sharing"],
                "materials": ["prompts", "timer"],
                "online_adaptation": "Breakout rooms with timed returns"
            },
            "Minute Paper": {
                "description": "Quick written response to prompt",
                "duration": "2-3 minutes",
                "group_size": "individual",
                "best_for": ["comprehension check", "reflection", "feedback"],
                "materials": ["paper/digital form", "prompt"],
                "online_adaptation": "Digital form or chat response"
            },
            "Jigsaw": {
                "description": "Expert groups study parts, then teach others",
                "duration": "20-30 minutes",
                "group_size": "4-6",
                "best_for": ["complex topics", "cooperative learning", "peer teaching"],
                "materials": ["divided materials", "expert sheets"],
                "online_adaptation": "Breakout rooms for expert groups"
            },
            "Gallery Walk": {
                "description": "Rotate through stations to view and discuss work",
                "duration": "15-20 minutes",
                "group_size": "3-5",
                "best_for": ["peer review", "multiple perspectives", "movement"],
                "materials": ["posted work", "feedback forms"],
                "online_adaptation": "Virtual rooms or shared documents"
            },
            "Case Study": {
                "description": "Analyze real-world scenario and propose solutions",
                "duration": "15-30 minutes",
                "group_size": "3-6",
                "best_for": ["application", "critical thinking", "decision making"],
                "materials": ["case description", "analysis framework"],
                "online_adaptation": "Shared document collaboration"
            },
            "Polling/Quizzing": {
                "description": "Real-time response to questions",
                "duration": "2-5 minutes",
                "group_size": "any",
                "best_for": ["engagement", "assessment", "discussion starter"],
                "materials": ["polling tool", "questions"],
                "online_adaptation": "Built-in platform polls or external tools"
            },
            "Concept Mapping": {
                "description": "Visual representation of concept relationships",
                "duration": "10-15 minutes",
                "group_size": "individual or small group",
                "best_for": ["organization", "connections", "review"],
                "materials": ["paper/digital tool", "concept list"],
                "online_adaptation": "Collaborative mind-mapping tools"
            },
            "Role Play": {
                "description": "Act out scenarios or perspectives",
                "duration": "10-20 minutes",
                "group_size": "2-6",
                "best_for": ["empathy", "application", "communication skills"],
                "materials": ["role cards", "scenario description"],
                "online_adaptation": "Video breakout rooms"
            }
        }
        
        # Learning Style Accommodations
        self.learning_styles = {
            "Visual": ["diagrams", "infographics", "videos", "color coding", "mind maps", "charts"],
            "Auditory": ["discussions", "podcasts", "verbal explanations", "music/rhythm", "recordings"],
            "Kinesthetic": ["hands-on activities", "simulations", "movement", "building", "experiments"],
            "Reading/Writing": ["note-taking", "journaling", "research", "lists", "written exercises"]
        }
    
    def generate_activity_plan(self, topic: str, duration: int, 
                              learning_objective: str = None,
                              group_size: str = "small") -> Dict:
        """
        Generate a complete activity plan
        
        Args:
            topic: Subject matter for the activity
            duration: Available time in minutes
            learning_objective: Optional specific objective
            group_size: Class size (individual, small, large)
        
        Returns:
            Complete activity plan dictionary
        """
        plan = {
            "topic": topic,
            "duration": f"{duration} minutes",
            "objective": learning_objective or f"Engage learners with {topic}",
            "group_size": group_size,
            "activities": []
        }
        
        # Select appropriate activities based on duration
        if duration <= 5:
            # Quick engagement
            plan["activities"].append(self._create_quick_activity(topic))
        elif duration <= 15:
            # Single main activity
            plan["activities"].append(self._create_medium_activity(topic, group_size))
        else:
            # Multiple activities with ARCS progression
            plan["activities"] = self._create_activity_sequence(topic, duration, group_size)
        
        # Add learning style accommodations
        plan["accommodations"] = self._generate_accommodations(topic)
        
        # Add materials list
        plan["materials"] = self._compile_materials(plan["activities"])
        
        return plan
    
    def _create_quick_activity(self, topic: str) -> Dict:
        """Create a 2-5 minute engagement activity"""
        techniques = ["Polling/Quizzing", "Minute Paper", "Think-Pair-Share"]
        selected = random.choice(techniques)
        technique = self.active_techniques[selected]
        
        return {
            "name": selected,
            "type": "quick_engagement",
            "description": technique["description"],
            "duration": technique["duration"],
            "instructions": self._generate_instructions(selected, topic),
            "arcs_component": "Attention"
        }
    
    def _create_medium_activity(self, topic: str, group_size: str) -> Dict:
        """Create a 10-15 minute activity"""
        # Filter techniques by group size
        appropriate = [name for name, tech in self.active_techniques.items()
                      if group_size == "individual" and tech["group_size"] == "individual"
                      or group_size != "individual" and tech["group_size"] != "individual"]
        
        if not appropriate:
            appropriate = list(self.active_techniques.keys())
        
        selected = random.choice(appropriate)
        technique = self.active_techniques[selected]
        
        return {
            "name": selected,
            "type": "main_activity",
            "description": technique["description"],
            "duration": technique["duration"],
            "instructions": self._generate_instructions(selected, topic),
            "materials": technique["materials"],
            "arcs_component": "Confidence",
            "online_adaptation": technique.get("online_adaptation", "")
        }
    
    def _create_activity_sequence(self, topic: str, duration: int, 
                                 group_size: str) -> List[Dict]:
        """Create a sequence of activities following ARCS model"""
        activities = []
        remaining_time = duration
        
        # Attention grabber (2-3 min)
        attention_activity = {
            "name": "Attention Grabber",
            "type": "opener",
            "description": random.choice(self.arcs_strategies["Attention"]["strategies"]),
            "duration": "2-3 minutes",
            "arcs_component": "Attention",
            "instructions": f"Start with {random.choice(self.arcs_strategies['Attention']['strategies']).lower()} related to {topic}"
        }
        activities.append(attention_activity)
        remaining_time -= 3
        
        # Main activity with relevance (50-60% of time)
        main_duration = int(duration * 0.5)
        main_activity = self._create_medium_activity(topic, group_size)
        main_activity["arcs_component"] = "Relevance & Confidence"
        activities.append(main_activity)
        remaining_time -= main_duration
        
        # Application/practice (remaining time minus 5 for wrap-up)
        if remaining_time > 10:
            practice = {
                "name": "Practice Application",
                "type": "practice",
                "description": "Guided practice with immediate feedback",
                "duration": f"{remaining_time - 5} minutes",
                "arcs_component": "Confidence",
                "instructions": self._generate_practice_instructions(topic)
            }
            activities.append(practice)
        
        # Satisfaction wrap-up (5 min)
        wrap_up = {
            "name": "Celebration & Reflection",
            "type": "closure",
            "description": random.choice(self.arcs_strategies["Satisfaction"]["strategies"]),
            "duration": "5 minutes",
            "arcs_component": "Satisfaction",
            "instructions": f"Close with {random.choice(self.arcs_strategies['Satisfaction']['strategies']).lower()}"
        }
        activities.append(wrap_up)
        
        return activities
    
    def _generate_instructions(self, technique: str, topic: str) -> List[str]:
        """Generate step-by-step instructions for an activity"""
        base_instructions = {
            "Think-Pair-Share": [
                f"Pose question about {topic}",
                "Give 1 minute for individual thinking",
                "Pair up for 2-minute discussion",
                "Share highlights with full group"
            ],
            "Minute Paper": [
                f"Display prompt about {topic}",
                "Set 2-minute timer",
                "Collect responses",
                "Share themes or examples"
            ],
            "Polling/Quizzing": [
                f"Prepare 3-5 questions about {topic}",
                "Launch poll one question at a time",
                "Display results immediately",
                "Discuss surprising or split results"
            ],
            "Case Study": [
                f"Present case related to {topic}",
                "Form analysis groups",
                "Provide analysis framework",
                "Groups present solutions",
                "Debrief key learnings"
            ]
        }
        
        return base_instructions.get(technique, [
            f"Introduce {technique} activity",
            f"Explain connection to {topic}",
            "Facilitate activity",
            "Debrief and connect to objectives"
        ])
    
    def _generate_practice_instructions(self, topic: str) -> List[str]:
        """Generate practice activity instructions"""
        return [
            f"Present practice problem related to {topic}",
            "Model solution approach",
            "Provide similar problem for pairs",
            "Circulate and provide feedback",
            "Share solutions and variations"
        ]
    
    def _generate_accommodations(self, topic: str) -> Dict:
        """Generate learning style accommodations"""
        return {
            "Visual": f"Use diagrams or concept maps for {topic}",
            "Auditory": f"Include verbal explanation and discussion of {topic}",
            "Kinesthetic": f"Incorporate movement or hands-on elements for {topic}",
            "Reading/Writing": f"Provide note-taking template for {topic}"
        }
    
    def _compile_materials(self, activities: List[Dict]) -> List[str]:
        """Compile materials list from activities"""
        materials = set()
        for activity in activities:
            if "materials" in activity:
                materials.update(activity["materials"])
        return sorted(list(materials))
    
    def export_plan(self, plan: Dict, format_type: str = "markdown") -> str:
        """Export activity plan in various formats"""
        if format_type == "json":
            return json.dumps(plan, indent=2)
        
        elif format_type == "markdown":
            output = f"# Engagement Plan: {plan['topic']}\n\n"
            output += f"**Duration:** {plan['duration']}\n"
            output += f"**Objective:** {plan['objective']}\n"
            output += f"**Group Size:** {plan['group_size']}\n\n"
            
            output += "## Activities\n\n"
            for i, activity in enumerate(plan['activities'], 1):
                output += f"### {i}. {activity['name']} ({activity['duration']})\n"
                output += f"**Type:** {activity['type']}\n"
                output += f"**ARCS Component:** {activity['arcs_component']}\n"
                output += f"**Description:** {activity['description']}\n\n"
                
                if 'instructions' in activity:
                    output += "**Instructions:**\n"
                    if isinstance(activity['instructions'], list):
                        for step in activity['instructions']:
                            output += f"1. {step}\n"
                    else:
                        output += f"- {activity['instructions']}\n"
                    output += "\n"
                
                if 'online_adaptation' in activity and activity['online_adaptation']:
                    output += f"**Online Adaptation:** {activity['online_adaptation']}\n\n"
            
            output += "## Learning Style Accommodations\n\n"
            for style, accommodation in plan['accommodations'].items():
                output += f"- **{style}:** {accommodation}\n"
            
            output += "\n## Materials Needed\n\n"
            for material in plan['materials']:
                output += f"- {material}\n"
            
            return output
        
        else:  # text format
            output = f"ENGAGEMENT PLAN: {plan['topic']}\n"
            output += "=" * 50 + "\n\n"
            output += f"Duration: {plan['duration']}\n"
            output += f"Objective: {plan['objective']}\n"
            output += f"Group Size: {plan['group_size']}\n\n"
            
            output += "ACTIVITIES\n"
            output += "-" * 30 + "\n"
            for i, activity in enumerate(plan['activities'], 1):
                output += f"\n{i}. {activity['name']} ({activity['duration']})\n"
                output += f"   Type: {activity['type']}\n"
                output += f"   ARCS: {activity['arcs_component']}\n"
                output += f"   Description: {activity['description']}\n"
            
            output += "\nMATERIALS NEEDED\n"
            output += "-" * 30 + "\n"
            for material in plan['materials']:
                output += f"  - {material}\n"
            
            return output

def main():
    parser = argparse.ArgumentParser(description='Generate engagement activity plans')
    parser.add_argument('topic', help='Topic for the activity')
    parser.add_argument('-d', '--duration', type=int, default=15,
                       help='Duration in minutes (default: 15)')
    parser.add_argument('-g', '--group-size', choices=['individual', 'small', 'large'],
                       default='small', help='Group size')
    parser.add_argument('-obj', '--objective', help='Learning objective')
    parser.add_argument('-o', '--output', choices=['json', 'markdown', 'text'],
                       default='markdown', help='Output format')
    
    args = parser.parse_args()
    
    planner = EngagementPlanner()
    plan = planner.generate_activity_plan(
        args.topic, 
        args.duration,
        args.objective,
        args.group_size
    )
    
    print(planner.export_plan(plan, args.output))

if __name__ == "__main__":
    main()
