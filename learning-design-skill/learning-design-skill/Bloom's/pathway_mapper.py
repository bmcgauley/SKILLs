#!/usr/bin/env python3
"""
Learning Pathway Mapper
Visualize and plan learning sequences with prerequisites
"""

import json
import argparse
from typing import List, Dict, Set, Tuple

class PathwayMapper:
    """Map and visualize learning pathways with prerequisites"""
    
    def __init__(self):
        self.nodes = {}  # topic_id -> topic_info
        self.edges = []  # (from_id, to_id) tuples
        self.levels = {}  # topic_id -> level in hierarchy
    
    def add_topic(self, topic_id: str, name: str, 
                  duration: int = 10, 
                  difficulty: str = "medium",
                  bloom_level: str = "Understand") -> None:
        """
        Add a topic to the learning pathway
        
        Args:
            topic_id: Unique identifier for topic
            name: Human-readable topic name
            duration: Estimated learning time in minutes
            difficulty: easy, medium, hard
            bloom_level: Bloom's taxonomy level
        """
        self.nodes[topic_id] = {
            "name": name,
            "duration": duration,
            "difficulty": difficulty,
            "bloom_level": bloom_level,
            "prerequisites": [],
            "leads_to": []
        }
    
    def add_prerequisite(self, topic_id: str, prereq_id: str) -> None:
        """Add a prerequisite relationship"""
        if topic_id in self.nodes and prereq_id in self.nodes:
            self.nodes[topic_id]["prerequisites"].append(prereq_id)
            self.nodes[prereq_id]["leads_to"].append(topic_id)
            self.edges.append((prereq_id, topic_id))
    
    def calculate_levels(self) -> None:
        """Calculate hierarchical levels for topics"""
        # Find topics with no prerequisites (level 0)
        level = 0
        current_level = [tid for tid, info in self.nodes.items() 
                        if not info["prerequisites"]]
        
        while current_level:
            for topic_id in current_level:
                self.levels[topic_id] = level
            
            # Find next level (topics whose prereqs are all assigned)
            next_level = []
            for tid, info in self.nodes.items():
                if tid not in self.levels:  # Not yet assigned
                    if all(p in self.levels for p in info["prerequisites"]):
                        next_level.append(tid)
            
            current_level = next_level
            level += 1
    
    def find_learning_path(self, start: str = None, end: str = None) -> List[str]:
        """
        Find optimal learning path between topics
        
        Args:
            start: Starting topic (or None for beginning)
            end: Target topic (or None for complete path)
        
        Returns:
            Ordered list of topic IDs
        """
        if not self.levels:
            self.calculate_levels()
        
        if start is None:
            # Start from level 0 topics
            path = [tid for tid, level in self.levels.items() if level == 0]
        else:
            path = [start]
        
        if end is None:
            # Include all topics in topological order
            remaining = set(self.nodes.keys()) - set(path)
            while remaining:
                # Add topics whose prerequisites are satisfied
                for tid in list(remaining):
                    prereqs = self.nodes[tid]["prerequisites"]
                    if all(p in path for p in prereqs):
                        path.append(tid)
                        remaining.remove(tid)
        else:
            # Find path to specific topic
            path = self._find_path_to_topic(end)
        
        return path
    
    def _find_path_to_topic(self, target: str) -> List[str]:
        """Find all topics needed to reach target"""
        required = set()
        to_process = [target]
        
        while to_process:
            current = to_process.pop()
            if current not in required:
                required.add(current)
                to_process.extend(self.nodes[current]["prerequisites"])
        
        # Sort by level
        if not self.levels:
            self.calculate_levels()
        
        return sorted(required, key=lambda x: self.levels.get(x, 999))
    
    def estimate_total_time(self, path: List[str]) -> Dict[str, int]:
        """Estimate total time for learning path"""
        total_minutes = sum(self.nodes[tid]["duration"] for tid in path)
        
        return {
            "total_minutes": total_minutes,
            "hours": total_minutes // 60,
            "remaining_minutes": total_minutes % 60,
            "sessions_recommended": (total_minutes + 44) // 45  # 45-min sessions
        }
    
    def identify_critical_path(self) -> List[str]:
        """Identify the critical path (longest duration path)"""
        if not self.levels:
            self.calculate_levels()
        
        # Find all paths from start to end nodes
        start_nodes = [tid for tid, level in self.levels.items() if level == 0]
        end_nodes = [tid for tid in self.nodes if not self.nodes[tid]["leads_to"]]
        
        critical_path = []
        max_duration = 0
        
        for start in start_nodes:
            for end in end_nodes:
                path = self._find_path_between(start, end)
                duration = sum(self.nodes[tid]["duration"] for tid in path)
                if duration > max_duration:
                    max_duration = duration
                    critical_path = path
        
        return critical_path
    
    def _find_path_between(self, start: str, end: str) -> List[str]:
        """Find path between two specific nodes"""
        # Simple BFS implementation
        from collections import deque
        
        if start == end:
            return [start]
        
        visited = {start}
        queue = deque([(start, [start])])
        
        while queue:
            current, path = queue.popleft()
            
            for next_node in self.nodes[current]["leads_to"]:
                if next_node == end:
                    return path + [end]
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, path + [next_node]))
        
        return []  # No path found
    
    def generate_scaffolding_plan(self, topic_id: str) -> Dict:
        """Generate scaffolding plan for a topic"""
        if topic_id not in self.nodes:
            return {}
        
        topic = self.nodes[topic_id]
        
        return {
            "topic": topic["name"],
            "scaffolding_stages": [
                {
                    "stage": "I Do (Demonstration)",
                    "description": f"Instructor demonstrates {topic['name']}",
                    "duration": f"{topic['duration'] // 4} minutes",
                    "support_level": "Full support"
                },
                {
                    "stage": "We Do (Guided Practice)",
                    "description": f"Practice {topic['name']} with instructor guidance",
                    "duration": f"{topic['duration'] // 3} minutes",
                    "support_level": "Partial support"
                },
                {
                    "stage": "You Do Together (Collaborative)",
                    "description": f"Peers work together on {topic['name']}",
                    "duration": f"{topic['duration'] // 3} minutes",
                    "support_level": "Peer support"
                },
                {
                    "stage": "You Do Alone (Independent)",
                    "description": f"Independent practice of {topic['name']}",
                    "duration": f"{topic['duration'] - (topic['duration'] // 4 + topic['duration'] // 3 + topic['duration'] // 3)} minutes",
                    "support_level": "Minimal support"
                }
            ]
        }
    
    def export_pathway(self, format_type: str = "json") -> str:
        """Export pathway in various formats"""
        if not self.levels:
            self.calculate_levels()
        
        if format_type == "json":
            export_data = {
                "nodes": self.nodes,
                "edges": self.edges,
                "levels": self.levels
            }
            return json.dumps(export_data, indent=2)
        
        elif format_type == "mermaid":
            # Generate Mermaid diagram syntax
            output = "```mermaid\ngraph TD\n"
            
            # Add nodes
            for tid, info in self.nodes.items():
                label = f"{info['name']}\\n({info['duration']} min)"
                output += f"    {tid}[\"{label}\"]\n"
            
            # Add edges
            for from_id, to_id in self.edges:
                output += f"    {from_id} --> {to_id}\n"
            
            # Style by difficulty
            output += "\n    %% Styling\n"
            for tid, info in self.nodes.items():
                if info["difficulty"] == "hard":
                    output += f"    style {tid} fill:#ffcccc\n"
                elif info["difficulty"] == "easy":
                    output += f"    style {tid} fill:#ccffcc\n"
            
            output += "```"
            return output
        
        elif format_type == "text":
            output = "LEARNING PATHWAY STRUCTURE\n"
            output += "=" * 50 + "\n\n"
            
            # Group by level
            max_level = max(self.levels.values()) if self.levels else 0
            
            for level in range(max_level + 1):
                topics_at_level = [tid for tid, l in self.levels.items() if l == level]
                if topics_at_level:
                    output += f"LEVEL {level}:\n"
                    for tid in topics_at_level:
                        info = self.nodes[tid]
                        output += f"  - {info['name']} ({info['duration']} min, {info['difficulty']})\n"
                        if info['prerequisites']:
                            prereq_names = [self.nodes[p]['name'] for p in info['prerequisites']]
                            output += f"    Prerequisites: {', '.join(prereq_names)}\n"
                    output += "\n"
            
            # Add critical path
            critical = self.identify_critical_path()
            if critical:
                output += "CRITICAL PATH:\n"
                for tid in critical:
                    output += f"  -> {self.nodes[tid]['name']}\n"
                
                time_est = self.estimate_total_time(critical)
                output += f"\nTotal Time: {time_est['hours']}h {time_est['remaining_minutes']}min\n"
            
            return output
        
        else:  # markdown
            output = "# Learning Pathway\n\n"
            
            # Summary
            output += "## Summary\n"
            output += f"- Total Topics: {len(self.nodes)}\n"
            output += f"- Levels: {max(self.levels.values()) + 1 if self.levels else 0}\n"
            all_topics = list(self.nodes.keys())
            time_est = self.estimate_total_time(all_topics)
            output += f"- Total Duration: {time_est['hours']}h {time_est['remaining_minutes']}min\n"
            output += f"- Recommended Sessions: {time_est['sessions_recommended']}\n\n"
            
            # Topics by level
            output += "## Topics by Level\n\n"
            max_level = max(self.levels.values()) if self.levels else 0
            
            for level in range(max_level + 1):
                topics_at_level = [tid for tid, l in self.levels.items() if l == level]
                if topics_at_level:
                    output += f"### Level {level}\n\n"
                    for tid in topics_at_level:
                        info = self.nodes[tid]
                        output += f"#### {info['name']}\n"
                        output += f"- Duration: {info['duration']} minutes\n"
                        output += f"- Difficulty: {info['difficulty']}\n"
                        output += f"- Bloom's Level: {info['bloom_level']}\n"
                        
                        if info['prerequisites']:
                            prereq_names = [self.nodes[p]['name'] for p in info['prerequisites']]
                            output += f"- Prerequisites: {', '.join(prereq_names)}\n"
                        
                        output += "\n"
            
            # Critical path
            critical = self.identify_critical_path()
            if critical:
                output += "## Critical Path\n\n"
                output += "The longest duration path through the content:\n\n"
                for i, tid in enumerate(critical, 1):
                    output += f"{i}. {self.nodes[tid]['name']} ({self.nodes[tid]['duration']} min)\n"
            
            return output

def load_pathway_from_file(filename: str) -> PathwayMapper:
    """Load pathway configuration from JSON file"""
    with open(filename, 'r') as f:
        data = json.load(f)
    
    mapper = PathwayMapper()
    
    # Add all topics first
    for topic in data.get("topics", []):
        mapper.add_topic(
            topic["id"],
            topic["name"],
            topic.get("duration", 10),
            topic.get("difficulty", "medium"),
            topic.get("bloom_level", "Understand")
        )
    
    # Then add prerequisites
    for topic in data.get("topics", []):
        for prereq in topic.get("prerequisites", []):
            mapper.add_prerequisite(topic["id"], prereq)
    
    return mapper

def main():
    parser = argparse.ArgumentParser(description='Map and visualize learning pathways')
    parser.add_argument('-f', '--file', help='Load pathway from JSON file')
    parser.add_argument('-o', '--output', choices=['json', 'markdown', 'text', 'mermaid'],
                       default='markdown', help='Output format')
    parser.add_argument('--demo', action='store_true', 
                       help='Generate demo pathway')
    
    args = parser.parse_args()
    
    if args.demo:
        # Create demo pathway
        mapper = PathwayMapper()
        
        # Add topics
        mapper.add_topic("intro", "Introduction to Programming", 30, "easy", "Remember")
        mapper.add_topic("variables", "Variables and Data Types", 45, "easy", "Understand")
        mapper.add_topic("control", "Control Structures", 60, "medium", "Apply")
        mapper.add_topic("functions", "Functions", 60, "medium", "Apply")
        mapper.add_topic("arrays", "Arrays and Lists", 45, "medium", "Apply")
        mapper.add_topic("objects", "Object-Oriented Programming", 90, "hard", "Analyze")
        mapper.add_topic("algorithms", "Basic Algorithms", 75, "hard", "Analyze")
        mapper.add_topic("project", "Final Project", 120, "hard", "Create")
        
        # Add prerequisites
        mapper.add_prerequisite("variables", "intro")
        mapper.add_prerequisite("control", "variables")
        mapper.add_prerequisite("functions", "variables")
        mapper.add_prerequisite("arrays", "control")
        mapper.add_prerequisite("objects", "functions")
        mapper.add_prerequisite("objects", "arrays")
        mapper.add_prerequisite("algorithms", "arrays")
        mapper.add_prerequisite("algorithms", "functions")
        mapper.add_prerequisite("project", "objects")
        mapper.add_prerequisite("project", "algorithms")
        
    elif args.file:
        mapper = load_pathway_from_file(args.file)
    else:
        print("Please specify --file or --demo")
        return
    
    # Calculate levels
    mapper.calculate_levels()
    
    # Export
    print(mapper.export_pathway(args.output))

if __name__ == "__main__":
    main()
