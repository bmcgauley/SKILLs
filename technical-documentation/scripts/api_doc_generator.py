#!/usr/bin/env python3
"""
API Documentation Generator
Generates OpenAPI/Swagger documentation from code comments and annotations.
"""

import json
import re
import ast
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml


class APIDocGenerator:
    """Generates API documentation from source code."""
    
    def __init__(self, base_url: str = "https://api.example.com", version: str = "1.0.0"):
        """Initialize the API documentation generator."""
        self.base_url = base_url
        self.version = version
        self.endpoints = []
        self.schemas = {}
        self.tags = set()
    
    def parse_python_file(self, file_path: str) -> List[Dict]:
        """Parse Python file for API endpoint definitions."""
        endpoints = []
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Look for route decorators
                    for decorator in node.decorator_list:
                        endpoint = self.extract_endpoint_info(node, decorator, content)
                        if endpoint:
                            endpoints.append(endpoint)
        
        except SyntaxError as e:
            print(f"Error parsing {file_path}: {e}")
        
        return endpoints
    
    def extract_endpoint_info(self, func_node: ast.FunctionDef, 
                            decorator: ast.AST, content: str) -> Optional[Dict]:
        """Extract endpoint information from function and decorator."""
        endpoint_info = None
        
        # Check if this is a route decorator (Flask/FastAPI style)
        if isinstance(decorator, ast.Call):
            if hasattr(decorator.func, 'attr'):
                method = decorator.func.attr.upper()
                
                # Extract path from decorator arguments
                if decorator.args and isinstance(decorator.args[0], ast.Str):
                    path = decorator.args[0].s
                elif decorator.args and isinstance(decorator.args[0], ast.Constant):
                    path = decorator.args[0].value
                else:
                    return None
                
                # Extract function docstring
                docstring = ast.get_docstring(func_node) or ""
                
                endpoint_info = self.parse_docstring(docstring)
                endpoint_info.update({
                    'path': path,
                    'method': method,
                    'function_name': func_node.name,
                    'parameters': self.extract_parameters(func_node, docstring)
                })
        
        return endpoint_info
    
    def parse_docstring(self, docstring: str) -> Dict:
        """Parse docstring for API documentation."""
        info = {
            'summary': '',
            'description': '',
            'tags': [],
            'responses': {},
            'request_body': None
        }
        
        lines = docstring.split('\n')
        
        # Extract summary (first line)
        if lines:
            info['summary'] = lines[0].strip()
        
        # Parse structured docstring
        current_section = None
        current_content = []
        
        for line in lines[1:]:
            line = line.strip()
            
            # Check for section headers
            if line.startswith('Args:') or line.startswith('Parameters:'):
                current_section = 'parameters'
            elif line.startswith('Returns:'):
                current_section = 'returns'
            elif line.startswith('Responses:'):
                current_section = 'responses'
            elif line.startswith('Tags:'):
                current_section = 'tags'
            elif line.startswith('Body:'):
                current_section = 'body'
            elif line and not line.startswith(' '):
                if current_section == 'description' or current_section is None:
                    current_content.append(line)
        
        # Join description
        if current_content:
            info['description'] = ' '.join(current_content)
        
        return info
    
    def extract_parameters(self, func_node: ast.FunctionDef, docstring: str) -> List[Dict]:
        """Extract parameters from function signature and docstring."""
        parameters = []
        
        # Get function arguments
        args = func_node.args.args
        defaults = func_node.args.defaults
        
        # Parse parameter descriptions from docstring
        param_docs = self.parse_parameter_docs(docstring)
        
        for i, arg in enumerate(args):
            if arg.arg in ['self', 'cls', 'request']:
                continue
            
            param = {
                'name': arg.arg,
                'in': 'query',  # Default, should be determined from route
                'required': i < len(args) - len(defaults),
                'schema': {'type': 'string'}  # Default type
            }
            
            # Add description from docstring if available
            if arg.arg in param_docs:
                param['description'] = param_docs[arg.arg]
            
            # Try to infer type from annotation
            if arg.annotation:
                param['schema'] = self.annotation_to_schema(arg.annotation)
            
            parameters.append(param)
        
        return parameters
    
    def parse_parameter_docs(self, docstring: str) -> Dict[str, str]:
        """Parse parameter descriptions from docstring."""
        param_docs = {}
        
        # Simple regex pattern for parameter documentation
        pattern = r'(\w+)\s*\([^)]*\):\s*(.+)'
        matches = re.findall(pattern, docstring)
        
        for param_name, description in matches:
            param_docs[param_name] = description.strip()
        
        return param_docs
    
    def annotation_to_schema(self, annotation: ast.AST) -> Dict:
        """Convert Python type annotation to OpenAPI schema."""
        schema = {'type': 'string'}  # Default
        
        if isinstance(annotation, ast.Name):
            type_map = {
                'str': 'string',
                'int': 'integer',
                'float': 'number',
                'bool': 'boolean',
                'dict': 'object',
                'list': 'array'
            }
            schema['type'] = type_map.get(annotation.id, 'string')
        
        return schema
    
    def generate_openapi_spec(self, title: str = "API Documentation") -> Dict:
        """Generate complete OpenAPI specification."""
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': title,
                'version': self.version,
                'description': 'Auto-generated API documentation'
            },
            'servers': [
                {'url': self.base_url}
            ],
            'paths': {},
            'components': {
                'schemas': self.schemas,
                'securitySchemes': {
                    'bearerAuth': {
                        'type': 'http',
                        'scheme': 'bearer',
                        'bearerFormat': 'JWT'
                    },
                    'apiKey': {
                        'type': 'apiKey',
                        'in': 'header',
                        'name': 'X-API-Key'
                    }
                }
            }
        }
        
        # Group endpoints by path
        for endpoint in self.endpoints:
            path = endpoint['path']
            method = endpoint['method'].lower()
            
            if path not in spec['paths']:
                spec['paths'][path] = {}
            
            spec['paths'][path][method] = {
                'summary': endpoint.get('summary', ''),
                'description': endpoint.get('description', ''),
                'operationId': endpoint.get('function_name', ''),
                'tags': endpoint.get('tags', []),
                'parameters': endpoint.get('parameters', []),
                'responses': endpoint.get('responses', {
                    '200': {'description': 'Successful response'},
                    '400': {'description': 'Bad request'},
                    '500': {'description': 'Server error'}
                })
            }
            
            # Add request body if present
            if endpoint.get('request_body'):
                spec['paths'][path][method]['requestBody'] = endpoint['request_body']
        
        # Add tags if any
        if self.tags:
            spec['tags'] = [{'name': tag} for tag in sorted(self.tags)]
        
        return spec
    
    def generate_markdown_docs(self) -> str:
        """Generate markdown documentation from endpoints."""
        lines = []
        lines.append("# API Documentation")
        lines.append(f"\nVersion: {self.version}")
        lines.append(f"Base URL: {self.base_url}")
        lines.append("\n## Endpoints\n")
        
        # Group by tags or paths
        grouped = {}
        for endpoint in self.endpoints:
            tags = endpoint.get('tags', ['General'])
            for tag in tags:
                if tag not in grouped:
                    grouped[tag] = []
                grouped[tag].append(endpoint)
        
        for tag in sorted(grouped.keys()):
            lines.append(f"### {tag}\n")
            
            for endpoint in grouped[tag]:
                lines.append(f"#### {endpoint['method']} {endpoint['path']}")
                
                if endpoint.get('summary'):
                    lines.append(f"\n{endpoint['summary']}")
                
                if endpoint.get('description'):
                    lines.append(f"\n{endpoint['description']}")
                
                # Parameters
                if endpoint.get('parameters'):
                    lines.append("\n**Parameters:**")
                    for param in endpoint['parameters']:
                        required = "required" if param.get('required') else "optional"
                        lines.append(f"- `{param['name']}` ({param['schema']['type']}, {required}): "
                                   f"{param.get('description', 'No description')}")
                
                # Request body
                if endpoint.get('request_body'):
                    lines.append("\n**Request Body:**")
                    lines.append("```json")
                    lines.append(json.dumps(endpoint['request_body'].get('example', {}), indent=2))
                    lines.append("```")
                
                # Responses
                lines.append("\n**Responses:**")
                for code, response in endpoint.get('responses', {}).items():
                    lines.append(f"- `{code}`: {response.get('description', 'No description')}")
                
                lines.append("\n---\n")
        
        return '\n'.join(lines)
    
    def scan_directory(self, directory: str, pattern: str = "*.py") -> None:
        """Scan directory for API definitions."""
        path = Path(directory)
        
        for file_path in path.rglob(pattern):
            endpoints = self.parse_python_file(str(file_path))
            self.endpoints.extend(endpoints)
            
            # Collect tags
            for endpoint in endpoints:
                self.tags.update(endpoint.get('tags', []))


def main():
    parser = argparse.ArgumentParser(description="Generate API documentation from source code")
    parser.add_argument("path", help="Path to source file or directory")
    parser.add_argument("--output", default="api-docs", help="Output file name (without extension)")
    parser.add_argument("--format", choices=["openapi", "markdown", "both"], default="both",
                       help="Output format")
    parser.add_argument("--base-url", default="https://api.example.com",
                       help="API base URL")
    parser.add_argument("--version", default="1.0.0", help="API version")
    parser.add_argument("--title", default="API Documentation", help="API title")
    
    args = parser.parse_args()
    
    # Create generator
    generator = APIDocGenerator(base_url=args.base_url, version=args.version)
    
    # Scan for endpoints
    if Path(args.path).is_file():
        endpoints = generator.parse_python_file(args.path)
        generator.endpoints.extend(endpoints)
    else:
        generator.scan_directory(args.path)
    
    # Generate documentation
    if args.format in ["openapi", "both"]:
        spec = generator.generate_openapi_spec(title=args.title)
        
        # Write OpenAPI spec as YAML
        with open(f"{args.output}.yaml", 'w') as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
        print(f"Generated OpenAPI specification: {args.output}.yaml")
        
        # Also write as JSON
        with open(f"{args.output}.json", 'w') as f:
            json.dump(spec, f, indent=2)
        print(f"Generated OpenAPI specification: {args.output}.json")
    
    if args.format in ["markdown", "both"]:
        markdown = generator.generate_markdown_docs()
        with open(f"{args.output}.md", 'w') as f:
            f.write(markdown)
        print(f"Generated Markdown documentation: {args.output}.md")


if __name__ == "__main__":
    main()
