#!/usr/bin/env python3
"""
Create Assessment Rubrics
Generate customizable rubrics for various assessment types
"""

import json
import argparse
from typing import List, Dict
import sys

class RubricGenerator:
    """Generate assessment rubrics for different types of assignments"""
    
    def __init__(self):
        self.performance_levels = ["Exemplary", "Proficient", "Developing", "Beginning"]
        self.point_distributions = {
            "4-level": [100, 85, 70, 50],
            "3-level": [100, 75, 50],
            "5-level": [100, 90, 80, 70, 60]
        }
    
    def create_criterion(self, name: str, description: str, weight: int = 25, 
                        criteria_type: str = "quality") -> Dict:
        """
        Create a single rubric criterion
        
        Args:
            name: Name of the criterion
            description: What is being assessed
            weight: Percentage weight of this criterion
            criteria_type: Type of criterion (quality, quantity, process, product)
        
        Returns:
            Dictionary containing the criterion definition
        """
        criterion = {
            "name": name,
            "description": description,
            "weight": weight,
            "type": criteria_type,
            "levels": {}
        }
        
        # Generate level descriptors based on criterion type
        if criteria_type == "quality":
            descriptors = self._generate_quality_descriptors(name)
        elif criteria_type == "quantity":
            descriptors = self._generate_quantity_descriptors(name)
        elif criteria_type == "process":
            descriptors = self._generate_process_descriptors(name)
        else:  # product
            descriptors = self._generate_product_descriptors(name)
        
        for level, descriptor in zip(self.performance_levels, descriptors):
            criterion["levels"][level] = descriptor
        
        return criterion
    
    def _generate_quality_descriptors(self, criterion_name: str) -> List[str]:
        """Generate quality-based descriptors"""
        return [
            f"Exceptional {criterion_name.lower()} that exceeds all expectations with innovative insights",
            f"Strong {criterion_name.lower()} that meets all requirements with clear understanding",
            f"Adequate {criterion_name.lower()} that meets most requirements with some gaps",
            f"Minimal {criterion_name.lower()} that attempts to meet requirements but has significant gaps"
        ]
    
    def _generate_quantity_descriptors(self, criterion_name: str) -> List[str]:
        """Generate quantity-based descriptors"""
        return [
            f"All required {criterion_name.lower()} elements present plus additional relevant content",
            f"All required {criterion_name.lower()} elements present and complete",
            f"Most required {criterion_name.lower()} elements present (75-90%)",
            f"Some required {criterion_name.lower()} elements present (50-74%)"
        ]
    
    def _generate_process_descriptors(self, criterion_name: str) -> List[str]:
        """Generate process-based descriptors"""
        return [
            f"Exemplary {criterion_name.lower()} process with consistent best practices throughout",
            f"Effective {criterion_name.lower()} process with good practices applied",
            f"Developing {criterion_name.lower()} process with inconsistent application",
            f"Beginning {criterion_name.lower()} process with limited understanding"
        ]
    
    def _generate_product_descriptors(self, criterion_name: str) -> List[str]:
        """Generate product-based descriptors"""
        return [
            f"Professional-quality {criterion_name.lower()} ready for public presentation",
            f"High-quality {criterion_name.lower()} with minor refinements needed",
            f"Acceptable {criterion_name.lower()} requiring some revision",
            f"Draft-quality {criterion_name.lower()} requiring substantial revision"
        ]
    
    def create_rubric(self, assignment_type: str, criteria: List[Dict] = None) -> Dict:
        """
        Create a complete rubric for an assignment type
        
        Args:
            assignment_type: Type of assignment (essay, presentation, project, etc.)
            criteria: Optional list of criteria dictionaries
        
        Returns:
            Complete rubric dictionary
        """
        if criteria is None:
            criteria = self._get_default_criteria(assignment_type)
        
        rubric = {
            "title": f"{assignment_type.title()} Assessment Rubric",
            "type": assignment_type,
            "total_points": 100,
            "performance_levels": self.performance_levels,
            "criteria": criteria,
            "grading_scale": self._generate_grading_scale()
        }
        
        # Validate weights sum to 100
        total_weight = sum(c.get("weight", 0) for c in criteria)
        if total_weight != 100:
            # Normalize weights
            for c in criteria:
                c["weight"] = int(c["weight"] * 100 / total_weight)
        
        return rubric
    
    def _get_default_criteria(self, assignment_type: str) -> List[Dict]:
        """Get default criteria for common assignment types"""
        
        defaults = {
            "essay": [
                self.create_criterion("Content & Ideas", "Quality of arguments and evidence", 30, "quality"),
                self.create_criterion("Organization", "Structure and flow of ideas", 25, "process"),
                self.create_criterion("Writing Style", "Clarity, grammar, and mechanics", 25, "quality"),
                self.create_criterion("Citations", "Proper use of sources and citations", 20, "quantity")
            ],
            "presentation": [
                self.create_criterion("Content Knowledge", "Understanding of topic", 30, "quality"),
                self.create_criterion("Delivery", "Speaking skills and engagement", 25, "process"),
                self.create_criterion("Visual Aids", "Quality and use of visuals", 20, "product"),
                self.create_criterion("Organization", "Logical flow and timing", 25, "process")
            ],
            "project": [
                self.create_criterion("Project Scope", "Completeness and ambition", 25, "quantity"),
                self.create_criterion("Technical Quality", "Implementation and functionality", 30, "product"),
                self.create_criterion("Documentation", "Clarity and completeness", 20, "product"),
                self.create_criterion("Process", "Planning and execution", 25, "process")
            ],
            "lab_report": [
                self.create_criterion("Hypothesis", "Clear and testable hypothesis", 20, "quality"),
                self.create_criterion("Methods", "Detailed and replicable procedures", 25, "process"),
                self.create_criterion("Results", "Data presentation and analysis", 30, "product"),
                self.create_criterion("Discussion", "Interpretation and conclusions", 25, "quality")
            ],
            "discussion": [
                self.create_criterion("Participation", "Frequency and consistency", 25, "quantity"),
                self.create_criterion("Quality", "Depth of contributions", 35, "quality"),
                self.create_criterion("Interaction", "Response to others", 20, "process"),
                self.create_criterion("Evidence", "Use of sources and examples", 20, "quantity")
            ]
        }
        
        return defaults.get(assignment_type, [
            self.create_criterion("Quality", "Overall quality of work", 40, "quality"),
            self.create_criterion("Completeness", "All requirements addressed", 30, "quantity"),
            self.create_criterion("Process", "Approach and methodology", 30, "process")
        ])
    
    def _generate_grading_scale(self) -> Dict:
        """Generate a standard grading scale"""
        return {
            "A": "90-100 points",
            "B": "80-89 points",
            "C": "70-79 points",
            "D": "60-69 points",
            "F": "Below 60 points"
        }
    
    def export_rubric(self, rubric: Dict, format_type: str = "json") -> str:
        """
        Export rubric in various formats
        
        Args:
            rubric: Rubric dictionary
            format_type: Export format (json, html, markdown, text)
        
        Returns:
            Formatted rubric string
        """
        if format_type == "json":
            return json.dumps(rubric, indent=2)
        
        elif format_type == "markdown":
            output = f"# {rubric['title']}\n\n"
            output += f"**Total Points:** {rubric['total_points']}\n\n"
            
            for criterion in rubric['criteria']:
                output += f"## {criterion['name']} ({criterion['weight']}%)\n"
                output += f"*{criterion['description']}*\n\n"
                
                for level in self.performance_levels:
                    if level in criterion['levels']:
                        output += f"**{level}:** {criterion['levels'][level]}\n\n"
                output += "---\n\n"
            
            output += "## Grading Scale\n"
            for grade, points in rubric['grading_scale'].items():
                output += f"- **{grade}:** {points}\n"
            
            return output
        
        elif format_type == "html":
            output = f"<h1>{rubric['title']}</h1>\n"
            output += f"<p><strong>Total Points:</strong> {rubric['total_points']}</p>\n"
            output += "<table border='1' cellpadding='5'>\n"
            output += "<tr><th>Criterion</th>"
            
            for level in self.performance_levels:
                output += f"<th>{level}</th>"
            output += "<th>Weight</th></tr>\n"
            
            for criterion in rubric['criteria']:
                output += f"<tr><td><strong>{criterion['name']}</strong><br/>{criterion['description']}</td>"
                for level in self.performance_levels:
                    output += f"<td>{criterion['levels'].get(level, '')}</td>"
                output += f"<td>{criterion['weight']}%</td></tr>\n"
            
            output += "</table>\n"
            return output
        
        else:  # text format
            output = f"{rubric['title']}\n"
            output += "=" * 60 + "\n\n"
            output += f"Total Points: {rubric['total_points']}\n\n"
            
            for criterion in rubric['criteria']:
                output += f"{criterion['name']} ({criterion['weight']}%)\n"
                output += f"Description: {criterion['description']}\n"
                output += "-" * 40 + "\n"
                
                for level in self.performance_levels:
                    if level in criterion['levels']:
                        output += f"  {level}:\n    {criterion['levels'][level]}\n"
                output += "\n"
            
            output += "Grading Scale:\n"
            for grade, points in rubric['grading_scale'].items():
                output += f"  {grade}: {points}\n"
            
            return output

def main():
    parser = argparse.ArgumentParser(description='Generate assessment rubrics')
    parser.add_argument('assignment_type', 
                       choices=['essay', 'presentation', 'project', 'lab_report', 'discussion', 'custom'],
                       help='Type of assignment')
    parser.add_argument('-c', '--criteria', nargs='+', 
                       help='Custom criteria names (for custom type)')
    parser.add_argument('-w', '--weights', nargs='+', type=int,
                       help='Weights for custom criteria (must sum to 100)')
    parser.add_argument('-o', '--output', choices=['json', 'markdown', 'html', 'text'],
                       default='markdown', help='Output format')
    parser.add_argument('-f', '--file', help='Output file (optional)')
    
    args = parser.parse_args()
    
    generator = RubricGenerator()
    
    # Create custom criteria if specified
    if args.assignment_type == 'custom' and args.criteria:
        if args.weights and len(args.weights) == len(args.criteria):
            weights = args.weights
        else:
            # Distribute weights equally
            weights = [100 // len(args.criteria)] * len(args.criteria)
            weights[-1] += 100 - sum(weights)  # Adjust last weight for rounding
        
        criteria = []
        for name, weight in zip(args.criteria, weights):
            criteria.append(generator.create_criterion(name, f"Assessment of {name}", weight))
        
        rubric = generator.create_rubric("custom", criteria)
    else:
        rubric = generator.create_rubric(args.assignment_type)
    
    # Export rubric
    output = generator.export_rubric(rubric, args.output)
    
    if args.file:
        with open(args.file, 'w') as f:
            f.write(output)
        print(f"Rubric saved to {args.file}")
    else:
        print(output)

if __name__ == "__main__":
    main()
