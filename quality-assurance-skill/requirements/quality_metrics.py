#!/usr/bin/env python3
"""
Quality Metrics Calculator
Calculate and track quality metrics for project deliverables
"""

import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import statistics

class QualityMetrics:
    """Calculate comprehensive quality metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.thresholds = {
            'defect_density': {'excellent': 0.1, 'good': 0.5, 'acceptable': 1.0, 'poor': 2.0},
            'test_coverage': {'excellent': 95, 'good': 85, 'acceptable': 75, 'poor': 60},
            'review_coverage': {'excellent': 100, 'good': 90, 'acceptable': 80, 'poor': 70},
            'defect_removal_efficiency': {'excellent': 95, 'good': 90, 'acceptable': 85, 'poor': 80},
            'first_pass_yield': {'excellent': 95, 'good': 90, 'acceptable': 85, 'poor': 75},
            'customer_satisfaction': {'excellent': 4.5, 'good': 4.0, 'acceptable': 3.5, 'poor': 3.0}
        }
    
    def calculate_defect_density(self, defects: int, size: float, 
                                size_unit: str = "KLOC") -> Dict:
        """
        Calculate defect density
        
        Args:
            defects: Number of defects found
            size: Size of deliverable
            size_unit: Unit of size (KLOC, FP, pages, etc.)
        
        Returns:
            Defect density metrics
        """
        if size == 0:
            return {'error': 'Size cannot be zero'}
        
        density = defects / size
        rating = self._rate_metric(density, 'defect_density', reverse=True)
        
        return {
            'defects': defects,
            'size': size,
            'unit': size_unit,
            'density': round(density, 3),
            'formula': f"defects/{size_unit}",
            'rating': rating,
            'interpretation': self._interpret_defect_density(density)
        }
    
    def calculate_test_coverage(self, tested_items: int, 
                              total_items: int) -> Dict:
        """
        Calculate test coverage percentage
        
        Args:
            tested_items: Number of items tested
            total_items: Total number of items
        
        Returns:
            Test coverage metrics
        """
        if total_items == 0:
            return {'error': 'Total items cannot be zero'}
        
        coverage = (tested_items / total_items) * 100
        rating = self._rate_metric(coverage, 'test_coverage')
        
        return {
            'tested': tested_items,
            'total': total_items,
            'coverage_percent': round(coverage, 1),
            'untested': total_items - tested_items,
            'rating': rating,
            'risk_level': self._assess_coverage_risk(coverage)
        }
    
    def calculate_defect_removal_efficiency(self, defects_found_internal: int,
                                          defects_found_external: int) -> Dict:
        """
        Calculate DRE (Defect Removal Efficiency)
        
        Args:
            defects_found_internal: Defects found before release
            defects_found_external: Defects found after release
        
        Returns:
            DRE metrics
        """
        total_defects = defects_found_internal + defects_found_external
        
        if total_defects == 0:
            return {'error': 'No defects found'}
        
        dre = (defects_found_internal / total_defects) * 100
        rating = self._rate_metric(dre, 'defect_removal_efficiency')
        
        return {
            'internal_defects': defects_found_internal,
            'external_defects': defects_found_external,
            'total_defects': total_defects,
            'dre_percent': round(dre, 1),
            'rating': rating,
            'quality_level': self._interpret_dre(dre)
        }
    
    def calculate_review_metrics(self, items_reviewed: int, total_items: int,
                                defects_found: int, review_hours: float) -> Dict:
        """
        Calculate review effectiveness metrics
        
        Args:
            items_reviewed: Number of items reviewed
            total_items: Total items requiring review
            defects_found: Defects found during review
            review_hours: Hours spent on review
        
        Returns:
            Review metrics
        """
        coverage = (items_reviewed / total_items * 100) if total_items > 0 else 0
        defect_rate = (defects_found / review_hours) if review_hours > 0 else 0
        
        return {
            'items_reviewed': items_reviewed,
            'total_items': total_items,
            'review_coverage': round(coverage, 1),
            'defects_found': defects_found,
            'review_hours': review_hours,
            'defects_per_hour': round(defect_rate, 2),
            'review_effectiveness': self._assess_review_effectiveness(defect_rate),
            'coverage_rating': self._rate_metric(coverage, 'review_coverage')
        }
    
    def calculate_first_pass_yield(self, passed_first_time: int,
                                  total_tested: int) -> Dict:
        """
        Calculate first pass yield (FPY)
        
        Args:
            passed_first_time: Items that passed on first attempt
            total_tested: Total items tested
        
        Returns:
            FPY metrics
        """
        if total_tested == 0:
            return {'error': 'No items tested'}
        
        fpy = (passed_first_time / total_tested) * 100
        rating = self._rate_metric(fpy, 'first_pass_yield')
        
        return {
            'passed_first_time': passed_first_time,
            'total_tested': total_tested,
            'required_rework': total_tested - passed_first_time,
            'fpy_percent': round(fpy, 1),
            'rating': rating,
            'rework_cost_factor': self._calculate_rework_cost(fpy)
        }
    
    def calculate_mean_time_to_repair(self, defect_times: List[float]) -> Dict:
        """
        Calculate MTTR (Mean Time To Repair)
        
        Args:
            defect_times: List of times to fix defects (in hours)
        
        Returns:
            MTTR metrics
        """
        if not defect_times:
            return {'error': 'No defect repair times provided'}
        
        mttr = statistics.mean(defect_times)
        median = statistics.median(defect_times)
        stdev = statistics.stdev(defect_times) if len(defect_times) > 1 else 0
        
        return {
            'total_defects': len(defect_times),
            'mean_hours': round(mttr, 1),
            'median_hours': round(median, 1),
            'stdev_hours': round(stdev, 1),
            'min_hours': round(min(defect_times), 1),
            'max_hours': round(max(defect_times), 1),
            'efficiency': self._assess_repair_efficiency(mttr)
        }
    
    def calculate_cost_of_quality(self, prevention_cost: float,
                                 appraisal_cost: float,
                                 internal_failure_cost: float,
                                 external_failure_cost: float) -> Dict:
        """
        Calculate Cost of Quality (COQ)
        
        Args:
            prevention_cost: Cost of preventing defects
            appraisal_cost: Cost of testing/inspection
            internal_failure_cost: Cost of internal defects
            external_failure_cost: Cost of external defects
        
        Returns:
            COQ metrics
        """
        conformance_cost = prevention_cost + appraisal_cost
        nonconformance_cost = internal_failure_cost + external_failure_cost
        total_coq = conformance_cost + nonconformance_cost
        
        if total_coq == 0:
            return {'error': 'Total COQ cannot be zero'}
        
        return {
            'prevention_cost': prevention_cost,
            'appraisal_cost': appraisal_cost,
            'internal_failure_cost': internal_failure_cost,
            'external_failure_cost': external_failure_cost,
            'conformance_cost': conformance_cost,
            'nonconformance_cost': nonconformance_cost,
            'total_coq': total_coq,
            'conformance_percent': round((conformance_cost / total_coq) * 100, 1),
            'nonconformance_percent': round((nonconformance_cost / total_coq) * 100, 1),
            'coq_ratio': round(conformance_cost / nonconformance_cost, 2) if nonconformance_cost > 0 else 'N/A',
            'optimization': self._suggest_coq_optimization(conformance_cost, nonconformance_cost)
        }
    
    def calculate_process_capability(self, measurements: List[float],
                                    lower_spec: float, upper_spec: float) -> Dict:
        """
        Calculate process capability indices (Cp, Cpk)
        
        Args:
            measurements: List of process measurements
            lower_spec: Lower specification limit
            upper_spec: Upper specification limit
        
        Returns:
            Process capability metrics
        """
        if len(measurements) < 2:
            return {'error': 'Need at least 2 measurements'}
        
        mean = statistics.mean(measurements)
        stdev = statistics.stdev(measurements)
        
        if stdev == 0:
            return {'error': 'No variation in measurements'}
        
        # Calculate Cp (potential capability)
        cp = (upper_spec - lower_spec) / (6 * stdev)
        
        # Calculate Cpk (actual capability)
        cpu = (upper_spec - mean) / (3 * stdev)
        cpl = (mean - lower_spec) / (3 * stdev)
        cpk = min(cpu, cpl)
        
        # Calculate percentage within spec
        within_spec = sum(1 for m in measurements 
                         if lower_spec <= m <= upper_spec)
        within_spec_pct = (within_spec / len(measurements)) * 100
        
        return {
            'measurements': len(measurements),
            'mean': round(mean, 3),
            'stdev': round(stdev, 3),
            'lower_spec': lower_spec,
            'upper_spec': upper_spec,
            'cp': round(cp, 3),
            'cpk': round(cpk, 3),
            'within_spec_percent': round(within_spec_pct, 1),
            'sigma_level': self._calculate_sigma_level(cpk),
            'capability_rating': self._rate_process_capability(cpk)
        }
    
    def generate_quality_dashboard(self, metrics_data: Dict) -> str:
        """
        Generate quality metrics dashboard
        
        Args:
            metrics_data: Dictionary of various metrics
        
        Returns:
            Formatted dashboard
        """
        dashboard = "# Quality Metrics Dashboard\n\n"
        dashboard += f"**Report Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        # Executive Summary
        dashboard += "## Executive Summary\n\n"
        
        overall_health = self._calculate_overall_health(metrics_data)
        dashboard += f"**Overall Quality Health:** {overall_health['status']} "
        dashboard += f"({overall_health['score']}/100)\n\n"
        
        # Key Metrics
        dashboard += "## Key Metrics\n\n"
        
        if 'defect_density' in metrics_data:
            dd = metrics_data['defect_density']
            dashboard += f"### Defect Density\n"
            dashboard += f"- **Value:** {dd['density']} defects/{dd['unit']}\n"
            dashboard += f"- **Rating:** {dd['rating']}\n\n"
        
        if 'test_coverage' in metrics_data:
            tc = metrics_data['test_coverage']
            dashboard += f"### Test Coverage\n"
            dashboard += f"- **Coverage:** {tc['coverage_percent']}%\n"
            dashboard += f"- **Rating:** {tc['rating']}\n"
            dashboard += f"- **Risk Level:** {tc['risk_level']}\n\n"
        
        if 'dre' in metrics_data:
            dre = metrics_data['dre']
            dashboard += f"### Defect Removal Efficiency\n"
            dashboard += f"- **DRE:** {dre['dre_percent']}%\n"
            dashboard += f"- **Quality Level:** {dre['quality_level']}\n\n"
        
        if 'fpy' in metrics_data:
            fpy = metrics_data['fpy']
            dashboard += f"### First Pass Yield\n"
            dashboard += f"- **FPY:** {fpy['fpy_percent']}%\n"
            dashboard += f"- **Rework Required:** {fpy['required_rework']} items\n\n"
        
        if 'coq' in metrics_data:
            coq = metrics_data['coq']
            dashboard += f"### Cost of Quality\n"
            dashboard += f"- **Total COQ:** ${coq['total_coq']:,.2f}\n"
            dashboard += f"- **Conformance:** {coq['conformance_percent']}%\n"
            dashboard += f"- **Nonconformance:** {coq['nonconformance_percent']}%\n\n"
        
        # Trends (if historical data available)
        if 'trends' in metrics_data:
            dashboard += "## Trends\n\n"
            dashboard += self._generate_trend_analysis(metrics_data['trends'])
        
        # Recommendations
        dashboard += "## Recommendations\n\n"
        dashboard += self._generate_recommendations(metrics_data)
        
        return dashboard
    
    def _rate_metric(self, value: float, metric_type: str, 
                    reverse: bool = False) -> str:
        """Rate a metric based on thresholds"""
        if metric_type not in self.thresholds:
            return "Unknown"
        
        thresholds = self.thresholds[metric_type]
        
        if reverse:  # Lower is better
            if value <= thresholds['excellent']:
                return "Excellent"
            elif value <= thresholds['good']:
                return "Good"
            elif value <= thresholds['acceptable']:
                return "Acceptable"
            else:
                return "Poor"
        else:  # Higher is better
            if value >= thresholds['excellent']:
                return "Excellent"
            elif value >= thresholds['good']:
                return "Good"
            elif value >= thresholds['acceptable']:
                return "Acceptable"
            else:
                return "Poor"
    
    def _interpret_defect_density(self, density: float) -> str:
        """Interpret defect density value"""
        if density < 0.1:
            return "Exceptional quality - very low defect rate"
        elif density < 0.5:
            return "Good quality - acceptable defect rate"
        elif density < 1.0:
            return "Average quality - improvement needed"
        elif density < 2.0:
            return "Below average - significant improvement required"
        else:
            return "Poor quality - immediate action required"
    
    def _assess_coverage_risk(self, coverage: float) -> str:
        """Assess risk based on test coverage"""
        if coverage >= 95:
            return "Very Low Risk"
        elif coverage >= 85:
            return "Low Risk"
        elif coverage >= 75:
            return "Medium Risk"
        elif coverage >= 60:
            return "High Risk"
        else:
            return "Very High Risk"
    
    def _interpret_dre(self, dre: float) -> str:
        """Interpret DRE percentage"""
        if dre >= 95:
            return "Excellent - Most defects caught internally"
        elif dre >= 90:
            return "Good - Effective quality control"
        elif dre >= 85:
            return "Acceptable - Some improvement needed"
        elif dre >= 80:
            return "Below average - Review QA processes"
        else:
            return "Poor - Significant QA improvements required"
    
    def _assess_review_effectiveness(self, defects_per_hour: float) -> str:
        """Assess review effectiveness"""
        if defects_per_hour > 5:
            return "Highly effective review process"
        elif defects_per_hour > 3:
            return "Effective review process"
        elif defects_per_hour > 1:
            return "Moderately effective review"
        else:
            return "Review process needs improvement"
    
    def _calculate_rework_cost(self, fpy: float) -> float:
        """Calculate rework cost factor"""
        rework_percent = 100 - fpy
        # Exponential cost increase for rework
        return round(1 + (rework_percent / 100) ** 2, 2)
    
    def _assess_repair_efficiency(self, mttr: float) -> str:
        """Assess repair efficiency based on MTTR"""
        if mttr < 2:
            return "Excellent - Very quick resolution"
        elif mttr < 4:
            return "Good - Reasonable resolution time"
        elif mttr < 8:
            return "Average - Could be improved"
        elif mttr < 16:
            return "Below average - Too slow"
        else:
            return "Poor - Unacceptable resolution time"
    
    def _suggest_coq_optimization(self, conformance: float, 
                                 nonconformance: float) -> str:
        """Suggest COQ optimization strategy"""
        ratio = conformance / nonconformance if nonconformance > 0 else float('inf')
        
        if ratio < 0.5:
            return "Increase prevention and appraisal investment"
        elif ratio < 1.0:
            return "Moderately increase quality activities"
        elif ratio < 2.0:
            return "Good balance - maintain current approach"
        else:
            return "Consider optimizing prevention costs"
    
    def _calculate_sigma_level(self, cpk: float) -> float:
        """Calculate approximate Six Sigma level"""
        return round(cpk * 3, 1)
    
    def _rate_process_capability(self, cpk: float) -> str:
        """Rate process capability"""
        if cpk >= 2.0:
            return "World class capability"
        elif cpk >= 1.67:
            return "Excellent capability"
        elif cpk >= 1.33:
            return "Good capability"
        elif cpk >= 1.0:
            return "Acceptable capability"
        else:
            return "Poor capability - improvement needed"
    
    def _calculate_overall_health(self, metrics: Dict) -> Dict:
        """Calculate overall quality health score"""
        scores = []
        weights = {
            'defect_density': 25,
            'test_coverage': 20,
            'dre': 25,
            'fpy': 20,
            'review_coverage': 10
        }
        
        # Convert ratings to scores
        rating_scores = {
            'Excellent': 100,
            'Good': 85,
            'Acceptable': 70,
            'Poor': 50
        }
        
        total_weight = 0
        weighted_score = 0
        
        for metric, weight in weights.items():
            if metric in metrics and 'rating' in metrics[metric]:
                rating = metrics[metric]['rating']
                score = rating_scores.get(rating, 50)
                weighted_score += score * weight
                total_weight += weight
        
        if total_weight > 0:
            final_score = round(weighted_score / total_weight, 0)
        else:
            final_score = 0
        
        if final_score >= 90:
            status = "Excellent"
        elif final_score >= 75:
            status = "Good"
        elif final_score >= 60:
            status = "Acceptable"
        else:
            status = "Needs Improvement"
        
        return {'score': final_score, 'status': status}
    
    def _generate_recommendations(self, metrics: Dict) -> str:
        """Generate recommendations based on metrics"""
        recommendations = []
        
        if 'defect_density' in metrics:
            if metrics['defect_density'].get('rating') in ['Poor', 'Acceptable']:
                recommendations.append("- Increase code reviews and testing coverage")
        
        if 'test_coverage' in metrics:
            if metrics['test_coverage'].get('coverage_percent', 0) < 80:
                recommendations.append("- Improve test coverage to reduce risk")
        
        if 'dre' in metrics:
            if metrics['dre'].get('dre_percent', 0) < 90:
                recommendations.append("- Enhance internal testing to catch defects earlier")
        
        if 'fpy' in metrics:
            if metrics['fpy'].get('fpy_percent', 0) < 90:
                recommendations.append("- Focus on first-time quality to reduce rework")
        
        if not recommendations:
            recommendations.append("- Continue current quality practices")
            recommendations.append("- Monitor trends for early warning signs")
        
        return '\n'.join(recommendations)
    
    def _generate_trend_analysis(self, trends: List[Dict]) -> str:
        """Generate trend analysis from historical data"""
        analysis = "### Metric Trends\n\n"
        
        # Simplified trend analysis
        analysis += "| Metric | Last Period | Current | Trend |\n"
        analysis += "|--------|------------|---------|-------|\n"
        
        for trend in trends:
            direction = "↑" if trend['current'] > trend['previous'] else "↓"
            analysis += f"| {trend['metric']} | {trend['previous']} | "
            analysis += f"{trend['current']} | {direction} |\n"
        
        return analysis

def main():
    parser = argparse.ArgumentParser(description='Calculate quality metrics')
    parser.add_argument('--defects', type=int, help='Number of defects')
    parser.add_argument('--size', type=float, help='Size (KLOC, pages, etc)')
    parser.add_argument('--tested', type=int, help='Items tested')
    parser.add_argument('--total', type=int, help='Total items')
    parser.add_argument('--internal-defects', type=int, help='Internal defects found')
    parser.add_argument('--external-defects', type=int, help='External defects found')
    parser.add_argument('--dashboard', action='store_true', help='Generate dashboard')
    
    args = parser.parse_args()
    
    calculator = QualityMetrics()
    metrics = {}
    
    # Calculate requested metrics
    if args.defects and args.size:
        metrics['defect_density'] = calculator.calculate_defect_density(
            args.defects, args.size
        )
    
    if args.tested and args.total:
        metrics['test_coverage'] = calculator.calculate_test_coverage(
            args.tested, args.total
        )
    
    if args.internal_defects is not None and args.external_defects is not None:
        metrics['dre'] = calculator.calculate_defect_removal_efficiency(
            args.internal_defects, args.external_defects
        )
    
    if args.dashboard:
        print(calculator.generate_quality_dashboard(metrics))
    else:
        print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
