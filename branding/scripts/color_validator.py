#!/usr/bin/env python3
"""
Color Validator for Brand Compliance
Validates color contrast ratios for WCAG AA/AAA compliance
and generates comprehensive accessibility reports.
"""

import json
import sys
from typing import Dict, List, Tuple, Optional
import argparse


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB values."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}"


def calculate_luminance(rgb: Tuple[int, int, int]) -> float:
    """Calculate relative luminance of a color."""
    def adjust_channel(channel: int) -> float:
        c = channel / 255.0
        if c <= 0.03928:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4
    
    r, g, b = rgb
    return 0.2126 * adjust_channel(r) + 0.7152 * adjust_channel(g) + 0.0722 * adjust_channel(b)


def calculate_contrast_ratio(color1: str, color2: str) -> float:
    """Calculate contrast ratio between two colors."""
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    
    lum1 = calculate_luminance(rgb1)
    lum2 = calculate_luminance(rgb2)
    
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    
    return (lighter + 0.05) / (darker + 0.05)


def check_wcag_compliance(ratio: float) -> Dict[str, bool]:
    """Check WCAG compliance levels for contrast ratio."""
    return {
        'aa_normal': ratio >= 4.5,      # AA for normal text
        'aa_large': ratio >= 3.0,       # AA for large text (18pt+)
        'aaa_normal': ratio >= 7.0,     # AAA for normal text
        'aaa_large': ratio >= 4.5       # AAA for large text
    }


def generate_color_report(colors: Dict[str, str], background: str = "#ffffff") -> Dict:
    """Generate comprehensive color accessibility report."""
    report = {
        'background': background,
        'colors': {},
        'combinations': [],
        'recommendations': []
    }
    
    # Check each color against background
    for name, hex_color in colors.items():
        ratio = calculate_contrast_ratio(hex_color, background)
        compliance = check_wcag_compliance(ratio)
        
        report['colors'][name] = {
            'hex': hex_color,
            'rgb': hex_to_rgb(hex_color),
            'contrast_ratio': round(ratio, 2),
            'wcag_compliance': compliance
        }
        
        # Add recommendations
        if not compliance['aa_normal']:
            if compliance['aa_large']:
                report['recommendations'].append(
                    f"{name} ({hex_color}): Use only for large text (18pt+ or 14pt+ bold)"
                )
            else:
                report['recommendations'].append(
                    f"{name} ({hex_color}): Insufficient contrast - avoid for text"
                )
    
    # Check color combinations
    color_list = list(colors.items())
    for i, (name1, color1) in enumerate(color_list):
        for name2, color2 in color_list[i+1:]:
            ratio = calculate_contrast_ratio(color1, color2)
            compliance = check_wcag_compliance(ratio)
            
            report['combinations'].append({
                'color1': {'name': name1, 'hex': color1},
                'color2': {'name': name2, 'hex': color2},
                'contrast_ratio': round(ratio, 2),
                'wcag_compliance': compliance
            })
    
    return report


def suggest_alternatives(hex_color: str, target_ratio: float = 4.5, 
                        background: str = "#ffffff") -> List[str]:
    """Suggest color alternatives that meet contrast requirements."""
    rgb = hex_to_rgb(hex_color)
    suggestions = []
    
    # Try adjusting lightness
    for factor in [0.8, 0.6, 0.4, 1.2, 1.4, 1.6]:
        adjusted = tuple(min(255, int(c * factor)) for c in rgb)
        adjusted_hex = rgb_to_hex(*adjusted)
        ratio = calculate_contrast_ratio(adjusted_hex, background)
        
        if ratio >= target_ratio:
            suggestions.append({
                'hex': adjusted_hex,
                'ratio': round(ratio, 2),
                'adjustment': f"{factor:.0%} brightness"
            })
    
    return suggestions[:3]  # Return top 3 suggestions


def format_report(report: Dict, format_type: str = "text") -> str:
    """Format report for output."""
    if format_type == "json":
        return json.dumps(report, indent=2)
    
    # Text format
    output = []
    output.append("=" * 60)
    output.append("BRAND COLOR ACCESSIBILITY REPORT")
    output.append("=" * 60)
    output.append(f"\nBackground Color: {report['background']}\n")
    
    output.append("\nCOLOR ANALYSIS:")
    output.append("-" * 40)
    
    for name, data in report['colors'].items():
        output.append(f"\n{name} ({data['hex']})")
        output.append(f"  RGB: {data['rgb']}")
        output.append(f"  Contrast Ratio: {data['contrast_ratio']}:1")
        output.append("  WCAG Compliance:")
        
        compliance = data['wcag_compliance']
        output.append(f"    Normal Text: {'✓ AA' if compliance['aa_normal'] else '✗'} "
                     f"{'✓ AAA' if compliance['aaa_normal'] else '✗'}")
        output.append(f"    Large Text:  {'✓ AA' if compliance['aa_large'] else '✗'} "
                     f"{'✓ AAA' if compliance['aaa_large'] else '✗'}")
    
    if report['recommendations']:
        output.append("\n\nRECOMMENDATIONS:")
        output.append("-" * 40)
        for rec in report['recommendations']:
            output.append(f"• {rec}")
    
    output.append("\n\nCOLOR COMBINATIONS:")
    output.append("-" * 40)
    
    for combo in report['combinations']:
        c1 = combo['color1']
        c2 = combo['color2']
        ratio = combo['contrast_ratio']
        compliance = combo['wcag_compliance']
        
        status = "✓ AA" if compliance['aa_normal'] else "✗ Insufficient"
        output.append(f"\n{c1['name']} + {c2['name']}: {ratio}:1 ({status})")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Validate brand colors for accessibility")
    parser.add_argument("--colors", type=str, required=True,
                       help="JSON string of colors, e.g., '{\"primary\": \"#0066cc\"}'")
    parser.add_argument("--background", type=str, default="#ffffff",
                       help="Background color to test against (default: white)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format")
    parser.add_argument("--suggest", action="store_true",
                       help="Suggest accessible alternatives for failing colors")
    
    args = parser.parse_args()
    
    try:
        colors = json.loads(args.colors)
    except json.JSONDecodeError:
        print("Error: Invalid JSON format for colors")
        sys.exit(1)
    
    report = generate_color_report(colors, args.background)
    
    if args.suggest:
        report['suggestions'] = {}
        for name, data in report['colors'].items():
            if not data['wcag_compliance']['aa_normal']:
                suggestions = suggest_alternatives(data['hex'], 4.5, args.background)
                if suggestions:
                    report['suggestions'][name] = suggestions
    
    print(format_report(report, args.format))


if __name__ == "__main__":
    main()
