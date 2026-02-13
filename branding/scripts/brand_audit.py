#!/usr/bin/env python3
"""
Brand Audit Tool
Analyzes brand consistency across digital assets and generates compliance reports.
"""

import os
import json
import re
from typing import Dict, List, Set, Tuple
from pathlib import Path
import argparse


class BrandAuditor:
    """Performs comprehensive brand audits across file types."""
    
    def __init__(self, brand_config: Dict):
        """Initialize with brand configuration."""
        self.config = brand_config
        self.results = {
            'total_files': 0,
            'compliant_files': 0,
            'issues': [],
            'summary': {}
        }
    
    def audit_colors(self, content: str, file_path: str) -> List[Dict]:
        """Check for approved color usage."""
        issues = []
        approved_colors = set(self.config.get('colors', {}).values())
        
        # Find all hex colors in content
        hex_pattern = r'#[0-9A-Fa-f]{6}\b'
        found_colors = set(re.findall(hex_pattern, content.upper()))
        
        # Check for unapproved colors
        unapproved = found_colors - {c.upper() for c in approved_colors}
        
        if unapproved:
            issues.append({
                'file': file_path,
                'type': 'color',
                'severity': 'warning',
                'message': f"Unapproved colors found: {', '.join(unapproved)}"
            })
        
        return issues
    
    def audit_typography(self, content: str, file_path: str) -> List[Dict]:
        """Check for approved font usage."""
        issues = []
        approved_fonts = self.config.get('fonts', [])
        
        # Common font declaration patterns
        font_patterns = [
            r'font-family:\s*([^;]+);',
            r"font-family:\s*'([^']+)'",
            r'font-family:\s*"([^"]+)"',
        ]
        
        found_fonts = set()
        for pattern in font_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Clean and split font stacks
                fonts = [f.strip().strip('"\'') for f in match.split(',')]
                found_fonts.update(fonts)
        
        # Check for unapproved fonts (excluding generic fallbacks)
        generic_fonts = {'serif', 'sans-serif', 'monospace', 'cursive', 'fantasy'}
        found_fonts = {f for f in found_fonts if f.lower() not in generic_fonts}
        
        unapproved = set()
        for font in found_fonts:
            if not any(approved.lower() in font.lower() for approved in approved_fonts):
                unapproved.add(font)
        
        if unapproved:
            issues.append({
                'file': file_path,
                'type': 'typography',
                'severity': 'warning',
                'message': f"Unapproved fonts found: {', '.join(unapproved)}"
            })
        
        return issues
    
    def audit_terminology(self, content: str, file_path: str) -> List[Dict]:
        """Check for consistent terminology usage."""
        issues = []
        terminology = self.config.get('terminology', {})
        
        for incorrect, correct in terminology.items():
            pattern = r'\b' + re.escape(incorrect) + r'\b'
            if re.search(pattern, content, re.IGNORECASE):
                issues.append({
                    'file': file_path,
                    'type': 'terminology',
                    'severity': 'info',
                    'message': f"Found '{incorrect}' - should be '{correct}'"
                })
        
        return issues
    
    def audit_file(self, file_path: str) -> Dict:
        """Audit a single file for brand compliance."""
        self.results['total_files'] += 1
        file_issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Run different audit checks based on file type
            if file_path.endswith(('.css', '.scss', '.sass', '.html', '.jsx', '.tsx')):
                file_issues.extend(self.audit_colors(content, file_path))
                file_issues.extend(self.audit_typography(content, file_path))
            
            if file_path.endswith(('.md', '.txt', '.html', '.jsx', '.tsx')):
                file_issues.extend(self.audit_terminology(content, file_path))
            
            if not file_issues:
                self.results['compliant_files'] += 1
            else:
                self.results['issues'].extend(file_issues)
            
        except Exception as e:
            file_issues.append({
                'file': file_path,
                'type': 'error',
                'severity': 'error',
                'message': f"Could not process file: {str(e)}"
            })
        
        return {'file': file_path, 'issues': file_issues}
    
    def audit_directory(self, directory: str, extensions: List[str] = None) -> Dict:
        """Audit all files in a directory."""
        directory = Path(directory)
        
        if not extensions:
            extensions = ['.html', '.css', '.scss', '.jsx', '.tsx', '.md', '.txt']
        
        for ext in extensions:
            for file_path in directory.rglob(f'*{ext}'):
                # Skip node_modules and other common directories
                if any(part in file_path.parts for part in ['node_modules', '.git', 'dist', 'build']):
                    continue
                
                self.audit_file(str(file_path))
        
        # Generate summary
        self.generate_summary()
        
        return self.results
    
    def generate_summary(self):
        """Generate audit summary statistics."""
        issue_types = {}
        severity_counts = {}
        
        for issue in self.results['issues']:
            # Count by type
            issue_type = issue['type']
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
            
            # Count by severity
            severity = issue['severity']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        self.results['summary'] = {
            'compliance_rate': f"{(self.results['compliant_files'] / max(self.results['total_files'], 1) * 100):.1f}%",
            'issue_types': issue_types,
            'severity_counts': severity_counts
        }


def format_audit_report(results: Dict, format_type: str = "text") -> str:
    """Format audit results for output."""
    if format_type == "json":
        return json.dumps(results, indent=2)
    
    # Text format
    output = []
    output.append("=" * 60)
    output.append("BRAND AUDIT REPORT")
    output.append("=" * 60)
    
    output.append(f"\nFiles Audited: {results['total_files']}")
    output.append(f"Compliant Files: {results['compliant_files']}")
    output.append(f"Compliance Rate: {results['summary']['compliance_rate']}")
    
    if results['summary']['issue_types']:
        output.append("\n\nISSUES BY TYPE:")
        output.append("-" * 40)
        for issue_type, count in results['summary']['issue_types'].items():
            output.append(f"  {issue_type.capitalize()}: {count}")
    
    if results['summary']['severity_counts']:
        output.append("\n\nISSUES BY SEVERITY:")
        output.append("-" * 40)
        for severity, count in results['summary']['severity_counts'].items():
            output.append(f"  {severity.upper()}: {count}")
    
    if results['issues']:
        output.append("\n\nDETAILED ISSUES:")
        output.append("-" * 40)
        
        # Group issues by file
        files_with_issues = {}
        for issue in results['issues']:
            file_path = issue['file']
            if file_path not in files_with_issues:
                files_with_issues[file_path] = []
            files_with_issues[file_path].append(issue)
        
        for file_path, issues in files_with_issues.items():
            output.append(f"\n{file_path}")
            for issue in issues:
                severity_icon = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}.get(issue['severity'], '•')
                output.append(f"  {severity_icon} [{issue['type']}] {issue['message']}")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Audit brand consistency across files")
    parser.add_argument("directory", type=str, help="Directory to audit")
    parser.add_argument("--config", type=str, required=True,
                       help="JSON string or file path with brand configuration")
    parser.add_argument("--extensions", nargs="+", 
                       help="File extensions to audit (default: html, css, scss, jsx, tsx, md, txt)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format")
    
    args = parser.parse_args()
    
    # Load configuration
    if os.path.isfile(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        try:
            config = json.loads(args.config)
        except json.JSONDecodeError:
            print("Error: Invalid JSON configuration")
            sys.exit(1)
    
    # Run audit
    auditor = BrandAuditor(config)
    results = auditor.audit_directory(args.directory, args.extensions)
    
    # Output results
    print(format_audit_report(results, args.format))
    
    # Exit with error code if compliance is low
    compliance_rate = float(results['summary']['compliance_rate'].rstrip('%'))
    if compliance_rate < 80:
        sys.exit(1)


if __name__ == "__main__":
    main()
