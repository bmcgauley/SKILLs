#!/usr/bin/env python3
"""
Audit Checklist Generator
Generate comprehensive audit checklists for quality audits
"""

import json
import argparse
from typing import List, Dict
from datetime import datetime
from enum import Enum

class AuditType(Enum):
    """Types of quality audits"""
    PROCESS = "Process Audit"
    PRODUCT = "Product Audit"
    COMPLIANCE = "Compliance Audit"
    SYSTEM = "System Audit"
    PERFORMANCE = "Performance Audit"

class AuditChecklistGenerator:
    """Generate customizable audit checklists"""
    
    def __init__(self):
        self.checklists = {
            AuditType.PROCESS: self._get_process_audit_items(),
            AuditType.PRODUCT: self._get_product_audit_items(),
            AuditType.COMPLIANCE: self._get_compliance_audit_items(),
            AuditType.SYSTEM: self._get_system_audit_items(),
            AuditType.PERFORMANCE: self._get_performance_audit_items()
        }
    
    def generate_checklist(self, audit_type: AuditType, 
                         scope: str = "General",
                         custom_items: List[str] = None) -> Dict:
        """
        Generate audit checklist
        
        Args:
            audit_type: Type of audit
            scope: Audit scope description
            custom_items: Additional custom checklist items
        
        Returns:
            Complete audit checklist
        """
        checklist = {
            'type': audit_type.value,
            'scope': scope,
            'date_created': datetime.now().isoformat(),
            'version': '1.0',
            'sections': [],
            'summary': {
                'total_items': 0,
                'critical_items': 0,
                'major_items': 0,
                'minor_items': 0
            }
        }
        
        # Get base checklist items
        base_items = self.checklists.get(audit_type, [])
        
        # Organize into sections
        sections = {}
        for item in base_items:
            section = item['section']
            if section not in sections:
                sections[section] = {
                    'name': section,
                    'items': []
                }
            sections[section]['items'].append(item)
        
        # Add custom items if provided
        if custom_items:
            custom_section = {
                'name': 'Custom Requirements',
                'items': [self._create_checklist_item(item, 'Custom') 
                         for item in custom_items]
            }
            sections['Custom Requirements'] = custom_section
        
        # Convert to list and calculate summary
        for section_name, section_data in sections.items():
            checklist['sections'].append(section_data)
            for item in section_data['items']:
                checklist['summary']['total_items'] += 1
                if item['severity'] == 'Critical':
                    checklist['summary']['critical_items'] += 1
                elif item['severity'] == 'Major':
                    checklist['summary']['major_items'] += 1
                else:
                    checklist['summary']['minor_items'] += 1
        
        return checklist
    
    def _create_checklist_item(self, description: str, section: str,
                             severity: str = "Major",
                             reference: str = None) -> Dict:
        """Create a single checklist item"""
        return {
            'description': description,
            'section': section,
            'severity': severity,
            'reference': reference or "Internal requirement",
            'status': 'Not Checked',
            'findings': '',
            'evidence': '',
            'corrective_action': ''
        }
    
    def _get_process_audit_items(self) -> List[Dict]:
        """Get process audit checklist items"""
        return [
            # Planning
            self._create_checklist_item(
                "Process documentation is current and approved",
                "Process Documentation", "Critical", "ISO 9001:2015 7.5"
            ),
            self._create_checklist_item(
                "Process flow diagrams are accurate and complete",
                "Process Documentation", "Major"
            ),
            self._create_checklist_item(
                "Process objectives and KPIs are defined",
                "Process Planning", "Critical"
            ),
            self._create_checklist_item(
                "Risk assessment has been conducted",
                "Process Planning", "Major", "ISO 31000"
            ),
            
            # Execution
            self._create_checklist_item(
                "Process is being followed as documented",
                "Process Execution", "Critical"
            ),
            self._create_checklist_item(
                "Required tools and resources are available",
                "Process Execution", "Major"
            ),
            self._create_checklist_item(
                "Personnel are trained on the process",
                "Process Execution", "Critical"
            ),
            self._create_checklist_item(
                "Process inputs meet specified requirements",
                "Process Execution", "Major"
            ),
            
            # Monitoring
            self._create_checklist_item(
                "Process monitoring is performed as planned",
                "Process Monitoring", "Major"
            ),
            self._create_checklist_item(
                "Process metrics are collected and analyzed",
                "Process Monitoring", "Major"
            ),
            self._create_checklist_item(
                "Non-conformances are identified and addressed",
                "Process Monitoring", "Critical"
            ),
            
            # Improvement
            self._create_checklist_item(
                "Continuous improvement activities are documented",
                "Process Improvement", "Minor"
            ),
            self._create_checklist_item(
                "Lessons learned are captured and shared",
                "Process Improvement", "Minor"
            ),
            self._create_checklist_item(
                "Process efficiency targets are met",
                "Process Improvement", "Major"
            )
        ]
    
    def _get_product_audit_items(self) -> List[Dict]:
        """Get product audit checklist items"""
        return [
            # Requirements
            self._create_checklist_item(
                "Product meets all functional requirements",
                "Requirements Compliance", "Critical"
            ),
            self._create_checklist_item(
                "Product meets performance requirements",
                "Requirements Compliance", "Critical"
            ),
            self._create_checklist_item(
                "Product meets quality standards",
                "Requirements Compliance", "Critical"
            ),
            
            # Design
            self._create_checklist_item(
                "Design documentation is complete and approved",
                "Design Verification", "Major"
            ),
            self._create_checklist_item(
                "Design reviews have been conducted",
                "Design Verification", "Major"
            ),
            self._create_checklist_item(
                "Design changes are controlled and documented",
                "Design Verification", "Critical"
            ),
            
            # Testing
            self._create_checklist_item(
                "All required tests have been performed",
                "Testing & Validation", "Critical"
            ),
            self._create_checklist_item(
                "Test results meet acceptance criteria",
                "Testing & Validation", "Critical"
            ),
            self._create_checklist_item(
                "Test documentation is complete",
                "Testing & Validation", "Major"
            ),
            
            # Documentation
            self._create_checklist_item(
                "User documentation is complete and accurate",
                "Documentation", "Major"
            ),
            self._create_checklist_item(
                "Technical documentation is complete",
                "Documentation", "Major"
            ),
            self._create_checklist_item(
                "Release notes are prepared",
                "Documentation", "Minor"
            )
        ]
    
    def _get_compliance_audit_items(self) -> List[Dict]:
        """Get compliance audit checklist items"""
        return [
            # Regulatory
            self._create_checklist_item(
                "All regulatory requirements are identified",
                "Regulatory Compliance", "Critical"
            ),
            self._create_checklist_item(
                "Regulatory approvals are obtained",
                "Regulatory Compliance", "Critical"
            ),
            self._create_checklist_item(
                "Regulatory reporting is current",
                "Regulatory Compliance", "Major"
            ),
            
            # Standards
            self._create_checklist_item(
                "Industry standards are identified and met",
                "Standards Compliance", "Major"
            ),
            self._create_checklist_item(
                "Internal standards are followed",
                "Standards Compliance", "Major"
            ),
            self._create_checklist_item(
                "Certification requirements are maintained",
                "Standards Compliance", "Critical"
            ),
            
            # Policies
            self._create_checklist_item(
                "Organizational policies are followed",
                "Policy Compliance", "Major"
            ),
            self._create_checklist_item(
                "Security policies are implemented",
                "Policy Compliance", "Critical"
            ),
            self._create_checklist_item(
                "Data privacy requirements are met",
                "Policy Compliance", "Critical", "GDPR/CCPA"
            ),
            
            # Contracts
            self._create_checklist_item(
                "Contractual obligations are met",
                "Contractual Compliance", "Critical"
            ),
            self._create_checklist_item(
                "SLAs are achieved",
                "Contractual Compliance", "Major"
            ),
            self._create_checklist_item(
                "Deliverables meet contract specifications",
                "Contractual Compliance", "Critical"
            )
        ]
    
    def _get_system_audit_items(self) -> List[Dict]:
        """Get system audit checklist items"""
        return [
            # Architecture
            self._create_checklist_item(
                "System architecture is documented",
                "System Architecture", "Major"
            ),
            self._create_checklist_item(
                "System components are properly integrated",
                "System Architecture", "Critical"
            ),
            self._create_checklist_item(
                "System interfaces are defined and tested",
                "System Architecture", "Major"
            ),
            
            # Security
            self._create_checklist_item(
                "Security controls are implemented",
                "System Security", "Critical"
            ),
            self._create_checklist_item(
                "Access controls are properly configured",
                "System Security", "Critical"
            ),
            self._create_checklist_item(
                "Security vulnerabilities are addressed",
                "System Security", "Critical"
            ),
            
            # Performance
            self._create_checklist_item(
                "System meets performance requirements",
                "System Performance", "Major"
            ),
            self._create_checklist_item(
                "System capacity is adequate",
                "System Performance", "Major"
            ),
            self._create_checklist_item(
                "System availability meets SLA",
                "System Performance", "Critical"
            ),
            
            # Maintenance
            self._create_checklist_item(
                "Backup and recovery procedures are tested",
                "System Maintenance", "Critical"
            ),
            self._create_checklist_item(
                "System monitoring is in place",
                "System Maintenance", "Major"
            ),
            self._create_checklist_item(
                "Maintenance procedures are documented",
                "System Maintenance", "Major"
            )
        ]
    
    def _get_performance_audit_items(self) -> List[Dict]:
        """Get performance audit checklist items"""
        return [
            # Efficiency
            self._create_checklist_item(
                "Resource utilization is optimized",
                "Efficiency", "Major"
            ),
            self._create_checklist_item(
                "Process cycle time meets targets",
                "Efficiency", "Major"
            ),
            self._create_checklist_item(
                "Waste is minimized",
                "Efficiency", "Minor"
            ),
            
            # Effectiveness
            self._create_checklist_item(
                "Objectives are achieved",
                "Effectiveness", "Critical"
            ),
            self._create_checklist_item(
                "Quality targets are met",
                "Effectiveness", "Critical"
            ),
            self._create_checklist_item(
                "Customer satisfaction targets are achieved",
                "Effectiveness", "Major"
            ),
            
            # Productivity
            self._create_checklist_item(
                "Productivity metrics meet targets",
                "Productivity", "Major"
            ),
            self._create_checklist_item(
                "Output quality is maintained",
                "Productivity", "Major"
            ),
            self._create_checklist_item(
                "Rework is minimized",
                "Productivity", "Major"
            ),
            
            # Financial
            self._create_checklist_item(
                "Budget targets are met",
                "Financial Performance", "Critical"
            ),
            self._create_checklist_item(
                "ROI targets are achieved",
                "Financial Performance", "Major"
            ),
            self._create_checklist_item(
                "Cost reduction targets are met",
                "Financial Performance", "Major"
            )
        ]
    
    def export_checklist(self, checklist: Dict, format_type: str = 'markdown') -> str:
        """Export checklist in various formats"""
        if format_type == 'json':
            return json.dumps(checklist, indent=2)
        
        elif format_type == 'markdown':
            output = f"# {checklist['type']}\n\n"
            output += f"**Scope:** {checklist['scope']}\n"
            output += f"**Date:** {checklist['date_created'][:10]}\n"
            output += f"**Version:** {checklist['version']}\n\n"
            
            output += "## Summary\n"
            output += f"- Total Items: {checklist['summary']['total_items']}\n"
            output += f"- Critical: {checklist['summary']['critical_items']}\n"
            output += f"- Major: {checklist['summary']['major_items']}\n"
            output += f"- Minor: {checklist['summary']['minor_items']}\n\n"
            
            for section in checklist['sections']:
                output += f"## {section['name']}\n\n"
                output += "| # | Item | Severity | Status | Findings |\n"
                output += "|---|------|----------|--------|----------|\n"
                
                for i, item in enumerate(section['items'], 1):
                    output += f"| {i} | {item['description']} | "
                    output += f"{item['severity']} | ☐ | |\n"
                
                output += "\n"
            
            output += "## Audit Sign-off\n\n"
            output += "| Role | Name | Signature | Date |\n"
            output += "|------|------|-----------|------|\n"
            output += "| Auditor | | | |\n"
            output += "| Auditee | | | |\n"
            output += "| Reviewer | | | |\n"
            
            return output
        
        elif format_type == 'html':
            output = f"<h1>{checklist['type']}</h1>\n"
            output += f"<p><strong>Scope:</strong> {checklist['scope']}</p>\n"
            output += f"<p><strong>Date:</strong> {checklist['date_created'][:10]}</p>\n"
            
            for section in checklist['sections']:
                output += f"<h2>{section['name']}</h2>\n"
                output += "<table border='1'>\n"
                output += "<tr><th>Item</th><th>Severity</th><th>Pass</th><th>Fail</th><th>N/A</th><th>Notes</th></tr>\n"
                
                for item in section['items']:
                    output += f"<tr><td>{item['description']}</td>"
                    output += f"<td>{item['severity']}</td>"
                    output += "<td>☐</td><td>☐</td><td>☐</td><td></td></tr>\n"
                
                output += "</table>\n"
            
            return output
        
        else:  # text format
            output = f"{checklist['type'].upper()}\n"
            output += "=" * 60 + "\n\n"
            output += f"Scope: {checklist['scope']}\n"
            output += f"Date: {checklist['date_created'][:10]}\n\n"
            
            for section in checklist['sections']:
                output += f"{section['name']}\n"
                output += "-" * 40 + "\n"
                
                for i, item in enumerate(section['items'], 1):
                    output += f"{i}. {item['description']}\n"
                    output += f"   Severity: {item['severity']}\n"
                    output += f"   Status: [ ] Pass  [ ] Fail  [ ] N/A\n"
                    output += f"   Findings: _______________________\n\n"
            
            return output

def main():
    parser = argparse.ArgumentParser(description='Generate audit checklists')
    parser.add_argument('audit_type', 
                       choices=['process', 'product', 'compliance', 'system', 'performance'],
                       help='Type of audit')
    parser.add_argument('-s', '--scope', default='General Audit',
                       help='Audit scope description')
    parser.add_argument('-c', '--custom', nargs='+',
                       help='Custom checklist items to add')
    parser.add_argument('-o', '--output', choices=['json', 'markdown', 'html', 'text'],
                       default='markdown', help='Output format')
    
    args = parser.parse_args()
    
    generator = AuditChecklistGenerator()
    
    # Generate checklist
    audit_type = AuditType[args.audit_type.upper()]
    checklist = generator.generate_checklist(
        audit_type,
        args.scope,
        args.custom
    )
    
    # Export
    print(generator.export_checklist(checklist, args.output))

if __name__ == "__main__":
    main()
