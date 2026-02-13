#!/usr/bin/env python3
"""
Test Case Generator
Generate comprehensive test cases from requirements
"""

import json
import argparse
from typing import List, Dict, Tuple
from enum import Enum
import random

class TestType(Enum):
    """Types of test cases"""
    FUNCTIONAL = "Functional"
    BOUNDARY = "Boundary"
    NEGATIVE = "Negative"
    PERFORMANCE = "Performance"
    SECURITY = "Security"
    USABILITY = "Usability"
    INTEGRATION = "Integration"
    REGRESSION = "Regression"

class TestPriority(Enum):
    """Test case priority levels"""
    HIGH = 1      # Must test - critical functionality
    MEDIUM = 2    # Should test - important features
    LOW = 3       # Nice to test - edge cases

class TestCaseGenerator:
    """Generate test cases from requirements"""
    
    def __init__(self):
        self.test_cases = []
        self.test_id_counter = 1000
        
        # Test data patterns
        self.boundary_values = {
            'numeric': [0, -1, 1, 999999, -999999, 0.1, -0.1],
            'string': ['', ' ', 'a', 'A'*255, 'A'*256, '!@#$%^&*()'],
            'date': ['1900-01-01', '2099-12-31', '2000-02-29', '2001-02-29'],
            'email': ['a@b.c', 'test@test', 'test@.com', '@test.com', 'test@test.c'],
            'phone': ['0', '123', '1234567890', '12345678901', '+1234567890']
        }
        
        # Common test scenarios
        self.common_scenarios = {
            'login': [
                ('Valid credentials', 'positive'),
                ('Invalid username', 'negative'),
                ('Invalid password', 'negative'),
                ('Empty username', 'negative'),
                ('Empty password', 'negative'),
                ('SQL injection attempt', 'security'),
                ('XSS attempt', 'security'),
                ('Concurrent login', 'performance')
            ],
            'data_entry': [
                ('Valid data', 'positive'),
                ('Required field empty', 'negative'),
                ('Invalid format', 'negative'),
                ('Boundary values', 'boundary'),
                ('Special characters', 'negative'),
                ('Maximum length exceeded', 'boundary'),
                ('Duplicate entry', 'negative')
            ],
            'search': [
                ('Exact match', 'positive'),
                ('Partial match', 'positive'),
                ('No results', 'negative'),
                ('Special characters', 'negative'),
                ('Case sensitivity', 'functional'),
                ('Performance with large dataset', 'performance')
            ]
        }
    
    def generate_test_case(self, requirement: str, test_type: TestType,
                          priority: TestPriority = TestPriority.MEDIUM) -> Dict:
        """
        Generate a single test case from requirement
        
        Args:
            requirement: Requirement description
            test_type: Type of test case
            priority: Test priority level
        
        Returns:
            Test case dictionary
        """
        test_case = {
            'id': f"TC_{self.test_id_counter:04d}",
            'requirement': requirement,
            'type': test_type.value,
            'priority': priority.value,
            'title': self._generate_title(requirement, test_type),
            'description': self._generate_description(requirement, test_type),
            'preconditions': self._generate_preconditions(requirement),
            'test_steps': self._generate_steps(requirement, test_type),
            'expected_result': self._generate_expected_result(requirement, test_type),
            'test_data': self._generate_test_data(requirement, test_type),
            'automation_candidate': self._is_automatable(test_type)
        }
        
        self.test_id_counter += 1
        self.test_cases.append(test_case)
        
        return test_case
    
    def generate_from_requirement(self, requirement: str, 
                                 comprehensive: bool = False) -> List[Dict]:
        """
        Generate multiple test cases from a requirement
        
        Args:
            requirement: Requirement description
            comprehensive: Generate all test types if True
        
        Returns:
            List of test cases
        """
        test_cases = []
        
        # Always generate functional test
        test_cases.append(
            self.generate_test_case(requirement, TestType.FUNCTIONAL, TestPriority.HIGH)
        )
        
        # Analyze requirement for specific test needs
        requirement_lower = requirement.lower()
        
        # Add boundary tests for numeric/limit requirements
        if any(word in requirement_lower for word in ['maximum', 'minimum', 'limit', 'range', 'between']):
            test_cases.append(
                self.generate_test_case(requirement, TestType.BOUNDARY, TestPriority.HIGH)
            )
        
        # Add negative test
        test_cases.append(
            self.generate_test_case(requirement, TestType.NEGATIVE, TestPriority.MEDIUM)
        )
        
        # Add performance test for processing requirements
        if any(word in requirement_lower for word in ['process', 'calculate', 'generate', 'load', 'response']):
            test_cases.append(
                self.generate_test_case(requirement, TestType.PERFORMANCE, TestPriority.MEDIUM)
            )
        
        # Add security test for data handling
        if any(word in requirement_lower for word in ['password', 'login', 'authentication', 'authorization', 'data', 'input']):
            test_cases.append(
                self.generate_test_case(requirement, TestType.SECURITY, TestPriority.HIGH)
            )
        
        if comprehensive:
            # Add remaining test types
            for test_type in TestType:
                if not any(tc['type'] == test_type.value for tc in test_cases):
                    test_cases.append(
                        self.generate_test_case(requirement, test_type, TestPriority.LOW)
                    )
        
        return test_cases
    
    def _generate_title(self, requirement: str, test_type: TestType) -> str:
        """Generate test case title"""
        prefix = {
            TestType.FUNCTIONAL: "Verify",
            TestType.BOUNDARY: "Test boundary values for",
            TestType.NEGATIVE: "Verify error handling for",
            TestType.PERFORMANCE: "Test performance of",
            TestType.SECURITY: "Test security of",
            TestType.USABILITY: "Verify usability of",
            TestType.INTEGRATION: "Test integration of",
            TestType.REGRESSION: "Regression test for"
        }
        
        # Truncate requirement for title
        req_summary = requirement[:50] + "..." if len(requirement) > 50 else requirement
        return f"{prefix[test_type]} {req_summary}"
    
    def _generate_description(self, requirement: str, test_type: TestType) -> str:
        """Generate test case description"""
        descriptions = {
            TestType.FUNCTIONAL: f"Verify that {requirement} works as expected with valid inputs",
            TestType.BOUNDARY: f"Test {requirement} with boundary and edge case values",
            TestType.NEGATIVE: f"Verify that {requirement} handles invalid inputs gracefully",
            TestType.PERFORMANCE: f"Verify that {requirement} meets performance requirements",
            TestType.SECURITY: f"Test {requirement} for security vulnerabilities",
            TestType.USABILITY: f"Verify that {requirement} provides good user experience",
            TestType.INTEGRATION: f"Test that {requirement} integrates correctly with other components",
            TestType.REGRESSION: f"Verify that {requirement} still works after changes"
        }
        
        return descriptions[test_type]
    
    def _generate_preconditions(self, requirement: str) -> List[str]:
        """Generate test preconditions"""
        preconditions = []
        
        requirement_lower = requirement.lower()
        
        # Common preconditions based on requirement keywords
        if 'login' in requirement_lower or 'authenticated' in requirement_lower:
            preconditions.append("User is logged in with valid credentials")
        
        if 'database' in requirement_lower or 'data' in requirement_lower:
            preconditions.append("Test data is available in the database")
        
        if 'permission' in requirement_lower or 'authorization' in requirement_lower:
            preconditions.append("User has appropriate permissions")
        
        if 'network' in requirement_lower or 'connection' in requirement_lower:
            preconditions.append("System has active network connection")
        
        if not preconditions:
            preconditions.append("System is in ready state")
        
        return preconditions
    
    def _generate_steps(self, requirement: str, test_type: TestType) -> List[Dict]:
        """Generate test steps"""
        steps = []
        
        if test_type == TestType.FUNCTIONAL:
            steps = [
                {"step": 1, "action": "Navigate to the relevant feature/page", 
                 "expected": "Feature/page loads successfully"},
                {"step": 2, "action": f"Perform action: {requirement}", 
                 "expected": "Action initiated without errors"},
                {"step": 3, "action": "Verify the result", 
                 "expected": "Expected outcome is achieved"},
                {"step": 4, "action": "Check for any side effects", 
                 "expected": "No unexpected side effects"}
            ]
        
        elif test_type == TestType.BOUNDARY:
            steps = [
                {"step": 1, "action": "Test with minimum valid value", 
                 "expected": "System accepts the value"},
                {"step": 2, "action": "Test with maximum valid value", 
                 "expected": "System accepts the value"},
                {"step": 3, "action": "Test with value just below minimum", 
                 "expected": "System rejects with appropriate error"},
                {"step": 4, "action": "Test with value just above maximum", 
                 "expected": "System rejects with appropriate error"}
            ]
        
        elif test_type == TestType.NEGATIVE:
            steps = [
                {"step": 1, "action": "Attempt action with invalid input", 
                 "expected": "System rejects the input"},
                {"step": 2, "action": "Verify error message displayed", 
                 "expected": "Clear, helpful error message shown"},
                {"step": 3, "action": "Verify system state unchanged", 
                 "expected": "No data corruption or state change"},
                {"step": 4, "action": "Retry with valid input", 
                 "expected": "System recovers and works normally"}
            ]
        
        elif test_type == TestType.PERFORMANCE:
            steps = [
                {"step": 1, "action": "Measure baseline performance", 
                 "expected": "Baseline metrics recorded"},
                {"step": 2, "action": "Execute action under normal load", 
                 "expected": "Response time within limits"},
                {"step": 3, "action": "Execute action under peak load", 
                 "expected": "System remains responsive"},
                {"step": 4, "action": "Monitor resource usage", 
                 "expected": "Resource usage within acceptable limits"}
            ]
        
        elif test_type == TestType.SECURITY:
            steps = [
                {"step": 1, "action": "Test with SQL injection patterns", 
                 "expected": "Input sanitized, no injection"},
                {"step": 2, "action": "Test with XSS patterns", 
                 "expected": "Input escaped, no script execution"},
                {"step": 3, "action": "Test authorization bypass attempts", 
                 "expected": "Access properly restricted"},
                {"step": 4, "action": "Verify data encryption", 
                 "expected": "Sensitive data encrypted"}
            ]
        
        else:
            # Generic steps
            steps = [
                {"step": 1, "action": "Setup test environment", 
                 "expected": "Environment ready"},
                {"step": 2, "action": f"Execute test for: {requirement}", 
                 "expected": "Test executes successfully"},
                {"step": 3, "action": "Verify results", 
                 "expected": "Results match expectations"},
                {"step": 4, "action": "Clean up test environment", 
                 "expected": "Environment restored"}
            ]
        
        return steps
    
    def _generate_expected_result(self, requirement: str, test_type: TestType) -> str:
        """Generate expected result"""
        if test_type == TestType.FUNCTIONAL:
            return f"The system successfully {requirement}"
        elif test_type == TestType.NEGATIVE:
            return "The system handles invalid input gracefully with appropriate error messages"
        elif test_type == TestType.BOUNDARY:
            return "The system correctly handles boundary values"
        elif test_type == TestType.PERFORMANCE:
            return "The system meets performance requirements (response time < 3s, throughput > 100 tps)"
        elif test_type == TestType.SECURITY:
            return "The system is secure against common vulnerabilities"
        else:
            return f"The requirement '{requirement}' is satisfied"
    
    def _generate_test_data(self, requirement: str, test_type: TestType) -> List:
        """Generate test data based on requirement and test type"""
        test_data = []
        
        if test_type == TestType.BOUNDARY:
            # Add boundary test data
            test_data.extend(self.boundary_values.get('numeric', []))
            test_data.extend(self.boundary_values.get('string', []))
        
        elif test_type == TestType.NEGATIVE:
            # Add negative test data
            test_data.extend(['', None, -1, 'Invalid@#$%', '../../etc/passwd'])
        
        elif test_type == TestType.SECURITY:
            # Add security test data
            test_data.extend([
                "' OR '1'='1",  # SQL injection
                "<script>alert('XSS')</script>",  # XSS
                "../../../etc/passwd",  # Path traversal
                "admin' --",  # SQL comment injection
            ])
        
        elif test_type == TestType.FUNCTIONAL:
            # Add valid test data
            test_data.extend(['ValidData123', 'test@example.com', '2024-01-01'])
        
        return test_data
    
    def _is_automatable(self, test_type: TestType) -> bool:
        """Determine if test case is good candidate for automation"""
        # High automation candidates
        if test_type in [TestType.FUNCTIONAL, TestType.BOUNDARY, TestType.REGRESSION]:
            return True
        # Medium automation candidates  
        elif test_type in [TestType.NEGATIVE, TestType.INTEGRATION]:
            return random.choice([True, False])
        # Low automation candidates
        else:
            return False
    
    def generate_test_suite(self, requirements: List[str], 
                           suite_name: str = "Test Suite") -> Dict:
        """
        Generate complete test suite from requirements list
        
        Args:
            requirements: List of requirement descriptions
            suite_name: Name of the test suite
        
        Returns:
            Test suite dictionary
        """
        suite = {
            'name': suite_name,
            'total_requirements': len(requirements),
            'test_cases': [],
            'coverage_matrix': [],
            'statistics': {}
        }
        
        for req in requirements:
            test_cases = self.generate_from_requirement(req)
            suite['test_cases'].extend(test_cases)
            
            # Add to coverage matrix
            suite['coverage_matrix'].append({
                'requirement': req,
                'test_case_ids': [tc['id'] for tc in test_cases],
                'test_types': list(set(tc['type'] for tc in test_cases))
            })
        
        # Calculate statistics
        suite['statistics'] = {
            'total_test_cases': len(suite['test_cases']),
            'by_type': {},
            'by_priority': {},
            'automation_candidates': 0
        }
        
        for tc in suite['test_cases']:
            # Count by type
            tc_type = tc['type']
            suite['statistics']['by_type'][tc_type] = \
                suite['statistics']['by_type'].get(tc_type, 0) + 1
            
            # Count by priority
            priority = f"Priority_{tc['priority']}"
            suite['statistics']['by_priority'][priority] = \
                suite['statistics']['by_priority'].get(priority, 0) + 1
            
            # Count automation candidates
            if tc['automation_candidate']:
                suite['statistics']['automation_candidates'] += 1
        
        return suite
    
    def export_test_cases(self, format_type: str = 'markdown') -> str:
        """Export test cases in various formats"""
        if format_type == 'json':
            return json.dumps(self.test_cases, indent=2)
        
        elif format_type == 'markdown':
            output = "# Test Cases\n\n"
            
            for tc in self.test_cases:
                output += f"## {tc['id']}: {tc['title']}\n\n"
                output += f"**Type:** {tc['type']} | "
                output += f"**Priority:** {tc['priority']}\n\n"
                output += f"**Description:** {tc['description']}\n\n"
                
                output += "**Preconditions:**\n"
                for precond in tc['preconditions']:
                    output += f"- {precond}\n"
                output += "\n"
                
                output += "**Test Steps:**\n"
                for step in tc['test_steps']:
                    output += f"{step['step']}. {step['action']}\n"
                    output += f"   - Expected: {step['expected']}\n"
                output += "\n"
                
                output += f"**Expected Result:** {tc['expected_result']}\n\n"
                
                if tc['test_data']:
                    output += f"**Test Data:** {', '.join(map(str, tc['test_data']))}\n\n"
                
                output += f"**Automation Candidate:** {'Yes' if tc['automation_candidate'] else 'No'}\n\n"
                output += "---\n\n"
            
            return output
        
        else:  # text format
            output = "TEST CASES\n" + "=" * 50 + "\n\n"
            
            for tc in self.test_cases:
                output += f"ID: {tc['id']}\n"
                output += f"Title: {tc['title']}\n"
                output += f"Type: {tc['type']}\n"
                output += f"Priority: {tc['priority']}\n"
                output += f"Description: {tc['description']}\n"
                output += "-" * 30 + "\n\n"
            
            return output

def main():
    parser = argparse.ArgumentParser(description='Generate test cases from requirements')
    parser.add_argument('requirements', nargs='*', help='Requirement descriptions')
    parser.add_argument('-f', '--file', help='File containing requirements (one per line)')
    parser.add_argument('-t', '--type', choices=['functional', 'boundary', 'negative', 'all'],
                       default='functional', help='Type of test cases to generate')
    parser.add_argument('-o', '--output', choices=['json', 'markdown', 'text'],
                       default='markdown', help='Output format')
    parser.add_argument('-c', '--comprehensive', action='store_true',
                       help='Generate comprehensive test coverage')
    
    args = parser.parse_args()
    
    # Get requirements
    requirements = []
    if args.file:
        with open(args.file, 'r') as f:
            requirements = [line.strip() for line in f if line.strip()]
    elif args.requirements:
        requirements = args.requirements
    else:
        print("Please provide requirements as arguments or via -f file")
        return
    
    generator = TestCaseGenerator()
    
    # Generate test cases
    for req in requirements:
        if args.type == 'all' or args.comprehensive:
            generator.generate_from_requirement(req, comprehensive=True)
        else:
            test_type = TestType[args.type.upper()]
            generator.generate_test_case(req, test_type)
    
    # Export results
    print(generator.export_test_cases(args.output))

if __name__ == "__main__":
    main()
