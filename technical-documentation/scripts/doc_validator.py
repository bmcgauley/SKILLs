#!/usr/bin/env python3
"""
Documentation Validator - Checks documentation quality and completeness
Validates structure, links, code examples, and style compliance.
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys


class DocValidator:
    """Validates technical documentation for quality and completeness."""
    
    def __init__(self, config: Dict = None):
        """Initialize with optional configuration."""
        self.config = config or self.get_default_config()
        self.issues = []
        self.warnings = []
        self.stats = {
            'total_files': 0,
            'total_lines': 0,
            'total_words': 0,
            'code_blocks': 0,
            'links': 0,
            'images': 0,
            'tables': 0
        }
    
    def get_default_config(self) -> Dict:
        """Return default validation configuration."""
        return {
            'max_line_length': 120,
            'max_heading_length': 60,
            'required_sections': [],
            'forbidden_words': ['TBD', 'TODO', 'FIXME', 'XXX'],
            'check_spelling': False,
            'check_links': True,
            'check_code_blocks': True,
            'require_alt_text': True
        }
    
    def validate_file(self, file_path: str) -> Dict:
        """Validate a single documentation file."""
        self.stats['total_files'] += 1
        file_issues = []
        file_warnings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            self.stats['total_lines'] += len(lines)
            self.stats['total_words'] += len(content.split())
            
            # Run various validation checks
            file_issues.extend(self.check_structure(lines, file_path))
            file_issues.extend(self.check_forbidden_words(content, file_path))
            file_warnings.extend(self.check_formatting(lines, file_path))
            
            if self.config['check_links']:
                link_issues = self.check_links(content, file_path)
                file_issues.extend(link_issues)
            
            if self.config['check_code_blocks']:
                code_issues = self.check_code_blocks(content, file_path)
                file_warnings.extend(code_issues)
            
            # Check for required sections if specified
            if self.config['required_sections']:
                section_issues = self.check_required_sections(content, file_path)
                file_issues.extend(section_issues)
            
            # Check images for alt text
            if self.config['require_alt_text']:
                alt_issues = self.check_alt_text(content, file_path)
                file_issues.extend(alt_issues)
            
        except Exception as e:
            file_issues.append({
                'file': file_path,
                'type': 'error',
                'line': 0,
                'message': f"Could not read file: {str(e)}"
            })
        
        self.issues.extend(file_issues)
        self.warnings.extend(file_warnings)
        
        return {
            'file': file_path,
            'issues': file_issues,
            'warnings': file_warnings,
            'valid': len(file_issues) == 0
        }
    
    def check_structure(self, lines: List[str], file_path: str) -> List[Dict]:
        """Check document structure and heading hierarchy."""
        issues = []
        heading_levels = []
        current_line = 0
        
        for i, line in enumerate(lines, 1):
            current_line = i
            
            # Check heading structure
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                heading_text = heading_match.group(2)
                
                # Check heading length
                if len(heading_text) > self.config['max_heading_length']:
                    issues.append({
                        'file': file_path,
                        'type': 'structure',
                        'line': i,
                        'message': f"Heading too long ({len(heading_text)} chars): '{heading_text[:50]}...'"
                    })
                
                # Check heading hierarchy
                if heading_levels and level > heading_levels[-1] + 1:
                    issues.append({
                        'file': file_path,
                        'type': 'structure',
                        'line': i,
                        'message': f"Skipped heading level (h{heading_levels[-1]} to h{level})"
                    })
                
                heading_levels.append(level)
        
        # Check for missing main heading
        if not any(line.startswith('# ') for line in lines[:10]):
            issues.append({
                'file': file_path,
                'type': 'structure',
                'line': 1,
                'message': "Missing main heading (h1) at document start"
            })
        
        return issues
    
    def check_forbidden_words(self, content: str, file_path: str) -> List[Dict]:
        """Check for forbidden words like TODO, TBD, etc."""
        issues = []
        
        for word in self.config['forbidden_words']:
            pattern = r'\b' + re.escape(word) + r'\b'
            matches = re.finditer(pattern, content, re.IGNORECASE)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    'file': file_path,
                    'type': 'forbidden',
                    'line': line_num,
                    'message': f"Found forbidden word: '{word}'"
                })
        
        return issues
    
    def check_formatting(self, lines: List[str], file_path: str) -> List[Dict]:
        """Check formatting issues like line length, trailing spaces."""
        warnings = []
        
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > self.config['max_line_length']:
                warnings.append({
                    'file': file_path,
                    'type': 'formatting',
                    'line': i,
                    'message': f"Line too long ({len(line)} chars)"
                })
            
            # Check trailing whitespace
            if line != line.rstrip():
                warnings.append({
                    'file': file_path,
                    'type': 'formatting',
                    'line': i,
                    'message': "Trailing whitespace"
                })
            
            # Check for tabs (prefer spaces)
            if '\t' in line:
                warnings.append({
                    'file': file_path,
                    'type': 'formatting',
                    'line': i,
                    'message': "Tab character found (use spaces)"
                })
        
        # Check for multiple consecutive blank lines
        blank_count = 0
        for i, line in enumerate(lines, 1):
            if line.strip() == '':
                blank_count += 1
                if blank_count > 2:
                    warnings.append({
                        'file': file_path,
                        'type': 'formatting',
                        'line': i,
                        'message': "More than 2 consecutive blank lines"
                    })
            else:
                blank_count = 0
        
        return warnings
    
    def check_links(self, content: str, file_path: str) -> List[Dict]:
        """Check for broken links and link formatting."""
        issues = []
        
        # Find markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.finditer(link_pattern, content)
        
        for link in links:
            link_text = link.group(1)
            link_url = link.group(2)
            line_num = content[:link.start()].count('\n') + 1
            
            self.stats['links'] += 1
            
            # Check for empty link text
            if not link_text.strip():
                issues.append({
                    'file': file_path,
                    'type': 'link',
                    'line': line_num,
                    'message': "Empty link text"
                })
            
            # Check for placeholder links
            if link_url in ['#', 'link', 'url', 'TODO']:
                issues.append({
                    'file': file_path,
                    'type': 'link',
                    'line': line_num,
                    'message': f"Placeholder link found: '{link_url}'"
                })
            
            # Check for "click here" anti-pattern
            if link_text.lower() in ['click here', 'here', 'link']:
                issues.append({
                    'file': file_path,
                    'type': 'link',
                    'line': line_num,
                    'message': f"Non-descriptive link text: '{link_text}'"
                })
            
            # Check internal links
            if link_url.startswith('#'):
                # Validate anchor exists
                anchor = link_url[1:].lower().replace(' ', '-')
                if not re.search(r'#{1,6}.*' + re.escape(anchor), content, re.IGNORECASE):
                    issues.append({
                        'file': file_path,
                        'type': 'link',
                        'line': line_num,
                        'message': f"Broken anchor link: '{link_url}'"
                    })
        
        return issues
    
    def check_code_blocks(self, content: str, file_path: str) -> List[Dict]:
        """Check code blocks for syntax and completeness."""
        warnings = []
        
        # Find code blocks
        code_blocks = re.finditer(r'```(\w*)\n(.*?)```', content, re.DOTALL)
        
        for block in code_blocks:
            language = block.group(1)
            code = block.group(2)
            line_num = content[:block.start()].count('\n') + 1
            
            self.stats['code_blocks'] += 1
            
            # Check for language specification
            if not language:
                warnings.append({
                    'file': file_path,
                    'type': 'code',
                    'line': line_num,
                    'message': "Code block missing language specification"
                })
            
            # Check for common placeholder patterns
            placeholders = ['...', 'TODO', 'YOUR_', 'PLACEHOLDER']
            for placeholder in placeholders:
                if placeholder in code:
                    warnings.append({
                        'file': file_path,
                        'type': 'code',
                        'line': line_num,
                        'message': f"Code block contains placeholder: '{placeholder}'"
                    })
                    break
        
        return warnings
    
    def check_required_sections(self, content: str, file_path: str) -> List[Dict]:
        """Check for required sections in the document."""
        issues = []
        
        for section in self.config['required_sections']:
            pattern = r'^#{1,6}\s*' + re.escape(section)
            if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                issues.append({
                    'file': file_path,
                    'type': 'structure',
                    'line': 0,
                    'message': f"Missing required section: '{section}'"
                })
        
        return issues
    
    def check_alt_text(self, content: str, file_path: str) -> List[Dict]:
        """Check images for alt text."""
        issues = []
        
        # Find images
        image_pattern = r'!\[([^\]]*)\]\([^)]+\)'
        images = re.finditer(image_pattern, content)
        
        for image in images:
            alt_text = image.group(1)
            line_num = content[:image.start()].count('\n') + 1
            
            self.stats['images'] += 1
            
            if not alt_text.strip():
                issues.append({
                    'file': file_path,
                    'type': 'accessibility',
                    'line': line_num,
                    'message': "Image missing alt text"
                })
            elif alt_text.lower() in ['image', 'picture', 'photo']:
                issues.append({
                    'file': file_path,
                    'type': 'accessibility',
                    'line': line_num,
                    'message': f"Non-descriptive alt text: '{alt_text}'"
                })
        
        return issues
    
    def validate_directory(self, directory: str, pattern: str = "*.md") -> Dict:
        """Validate all documentation files in a directory."""
        directory_path = Path(directory)
        results = {
            'valid_files': [],
            'invalid_files': [],
            'total_issues': 0,
            'total_warnings': 0
        }
        
        for file_path in directory_path.rglob(pattern):
            result = self.validate_file(str(file_path))
            
            if result['valid']:
                results['valid_files'].append(str(file_path))
            else:
                results['invalid_files'].append(str(file_path))
            
            results['total_issues'] += len(result['issues'])
            results['total_warnings'] += len(result['warnings'])
        
        results['stats'] = self.stats
        results['issues'] = self.issues
        results['warnings'] = self.warnings
        
        return results
    
    def format_report(self, results: Dict, format_type: str = "text") -> str:
        """Format validation report for output."""
        if format_type == "json":
            return json.dumps(results, indent=2)
        
        # Text format
        output = []
        output.append("=" * 60)
        output.append("DOCUMENTATION VALIDATION REPORT")
        output.append("=" * 60)
        
        # Summary
        output.append(f"\nFiles Validated: {results['stats']['total_files']}")
        output.append(f"Valid Files: {len(results['valid_files'])}")
        output.append(f"Invalid Files: {len(results['invalid_files'])}")
        output.append(f"Total Issues: {results['total_issues']}")
        output.append(f"Total Warnings: {results['total_warnings']}")
        
        # Statistics
        output.append(f"\n📊 STATISTICS:")
        output.append("-" * 40)
        for key, value in results['stats'].items():
            if key != 'total_files':
                output.append(f"{key.replace('_', ' ').title()}: {value}")
        
        # Issues
        if results['issues']:
            output.append(f"\n❌ ISSUES (Must Fix):")
            output.append("-" * 40)
            for issue in results['issues'][:20]:  # Show first 20
                output.append(f"\n{issue['file']}:{issue['line']}")
                output.append(f"  [{issue['type']}] {issue['message']}")
        
        # Warnings
        if results['warnings']:
            output.append(f"\n⚠️  WARNINGS (Should Fix):")
            output.append("-" * 40)
            for warning in results['warnings'][:10]:  # Show first 10
                output.append(f"\n{warning['file']}:{warning['line']}")
                output.append(f"  [{warning['type']}] {warning['message']}")
        
        # Invalid files list
        if results['invalid_files']:
            output.append(f"\n📝 FILES NEEDING ATTENTION:")
            output.append("-" * 40)
            for file in results['invalid_files'][:10]:
                output.append(f"  • {file}")
        
        return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Validate technical documentation")
    parser.add_argument("path", help="Path to documentation file or directory")
    parser.add_argument("--pattern", default="*.md", help="File pattern to validate (default: *.md)")
    parser.add_argument("--config", help="JSON configuration file")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format")
    parser.add_argument("--required-sections", nargs="+",
                       help="Required sections to check")
    parser.add_argument("--no-link-check", action="store_true",
                       help="Skip link validation")
    parser.add_argument("--strict", action="store_true",
                       help="Treat warnings as errors")
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Override with command line args
    if args.required_sections:
        config['required_sections'] = args.required_sections
    if args.no_link_check:
        config['check_links'] = False
    
    # Create validator
    validator = DocValidator(config)
    
    # Validate
    if os.path.isfile(args.path):
        result = validator.validate_file(args.path)
        results = {
            'valid_files': [args.path] if result['valid'] else [],
            'invalid_files': [] if result['valid'] else [args.path],
            'total_issues': len(result['issues']),
            'total_warnings': len(result['warnings']),
            'stats': validator.stats,
            'issues': result['issues'],
            'warnings': result['warnings']
        }
    else:
        results = validator.validate_directory(args.path, args.pattern)
    
    # Output report
    print(validator.format_report(results, args.format))
    
    # Exit code
    if results['total_issues'] > 0:
        sys.exit(1)
    elif args.strict and results['total_warnings'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
