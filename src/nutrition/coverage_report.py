"""Coverage Report - Generate nutrition coverage analysis reports."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from pathlib import Path

from .nutrition_models import (
    RecipeNutritionOutput, RecipeCalculationStatus, NUTRIENT_NAMES, NUTRIENT_UNITS
)
from .recipe_aggregator import RecipeAggregator


@dataclass
class CoverageReport:
    """Comprehensive coverage analysis report."""
    summary: Dict[str, Any] = field(default_factory=dict)
    recipe_details: List[Dict[str, Any]] = field(default_factory=list)
    nutrient_coverage: Dict[str, Any] = field(default_factory=dict)
    ingredient_coverage: Dict[str, Any] = field(default_factory=dict)
    limitations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class CoverageAnalyzer:
    """Analyze and report nutrition calculation coverage."""
    
    def __init__(self, aggregator: RecipeAggregator):
        self.aggregator = aggregator
    
    def analyze_results(self, results: List[RecipeNutritionOutput]) -> CoverageReport:
        """Generate comprehensive coverage report from aggregation results."""
        report = CoverageReport()
        
        # Summary statistics
        report.summary = self.aggregator.get_aggregation_summary(results)
        
        # Recipe-level details
        report.recipe_details = self._generate_recipe_details(results)
        
        # Nutrient coverage analysis
        report.nutrient_coverage = self._analyze_nutrient_coverage(results)
        
        # Ingredient coverage analysis
        report.ingredient_coverage = self._analyze_ingredient_coverage(results)
        
        # Limitations
        report.limitations = self._identify_limitations(results)
        
        # Recommendations
        report.recommendations = self._generate_recommendations(results)
        
        return report
    
    def _generate_recipe_details(self, results: List[RecipeNutritionOutput]) -> List[Dict[str, Any]]:
        """Generate detailed per-recipe information."""
        details = []
        
        for r in results:
            detail = {
                'recipe_id': r.recipe_id,
                'calculation_status': r.calculation_status.value,
                'mapped_ingredients': r.mapped_ingredient_count,
                'total_ingredients': r.total_ingredient_count,
                'unresolved_ingredients': r.unresolved_ingredient_count,
                'mapping_coverage': round(r.ingredient_mapping_coverage, 3),
                'gram_weight_coverage': round(r.gram_weight_coverage, 3),
                'nutrients_calculated': list(r.total_nutrients.keys()),
                'nutrient_completeness': {k: round(v, 3) for k, v in r.nutrient_completeness.items()},
                'total_nutrients': {k: round(v, 3) for k, v in r.total_nutrients.items()},
            }
            
            # Add kcal if present
            if 'energy_kcal' in r.total_nutrients:
                detail['energy_kcal'] = round(r.total_nutrients['energy_kcal'], 2)
            
            details.append(detail)
        
        return details
    
    def _analyze_nutrient_coverage(self, results: List[RecipeNutritionOutput]) -> Dict[str, Any]:
        """Analyze coverage for each nutrient."""
        total_recipes = len(results)
        if total_recipes == 0:
            return {}
        
        nutrient_stats = {}
        
        for nutrient in NUTRIENT_NAMES:
            present_count = sum(1 for r in results if nutrient in r.total_nutrients)
            total_value = sum(r.total_nutrients.get(nutrient, 0) for r in results)
            
            # Among recipes with this nutrient, get statistics
            values = [r.total_nutrients[nutrient] for r in results if nutrient in r.total_nutrients]
            
            nutrient_stats[nutrient] = {
                'recipes_with_nutrient': present_count,
                'coverage_rate': round(present_count / total_recipes, 3),
                'unit': NUTRIENT_UNITS.get(nutrient, ''),
                'mean_value': round(np.mean(values), 2) if values else 0,
                'median_value': round(np.median(values), 2) if values else 0,
                'min_value': round(np.min(values), 2) if values else 0,
                'max_value': round(np.max(values), 2) if values else 0,
                'total_value': round(total_value, 2),
            }
        
        # Overall completeness
        all_completeness = []
        for r in results:
            if r.nutrient_completeness:
                all_completeness.append(np.mean(list(r.nutrient_completeness.values())))
        
        nutrient_stats['overall'] = {
            'mean_completeness': round(np.mean(all_completeness), 3) if all_completeness else 0,
            'median_completeness': round(np.median(all_completeness), 3) if all_completeness else 0,
        }
        
        return nutrient_stats
    
    def _analyze_ingredient_coverage(self, results: List[RecipeNutritionOutput]) -> Dict[str, Any]:
        """Analyze ingredient mapping and weight coverage."""
        total_mapped = sum(r.mapped_ingredient_count for r in results)
        total_ingredients = sum(r.total_ingredient_count for r in results)
        total_unresolved = sum(r.unresolved_ingredient_count for r in results)
        
        # Per-recipe mapping rates
        mapping_rates = []
        weight_rates = []
        
        for r in results:
            if r.total_ingredient_count > 0:
                mapping_rates.append(r.mapped_ingredient_count / r.total_ingredient_count)
                weight_rates.append(r.gram_weight_coverage)
        
        return {
            'total_ingredients': total_ingredients,
            'total_mapped': total_mapped,
            'total_unresolved': total_unresolved,
            'overall_mapping_rate': round(total_mapped / max(total_ingredients, 1), 3),
            'per_recipe_mapping_rate': {
                'mean': round(np.mean(mapping_rates), 3) if mapping_rates else 0,
                'median': round(np.median(mapping_rates), 3) if mapping_rates else 0,
                'min': round(np.min(mapping_rates), 3) if mapping_rates else 0,
                'max': round(np.max(mapping_rates), 3) if mapping_rates else 0,
            },
            'per_recipe_weight_rate': {
                'mean': round(np.mean(weight_rates), 3) if weight_rates else 0,
                'median': round(np.median(weight_rates), 3) if weight_rates else 0,
                'min': round(np.min(weight_rates), 3) if weight_rates else 0,
                'max': round(np.max(weight_rates), 3) if weight_rates else 0,
            },
            'status_distribution': self._get_status_distribution(results),
        }
    
    def _get_status_distribution(self, results: List[RecipeNutritionOutput]) -> Dict[str, int]:
        """Get distribution of calculation statuses."""
        dist = {}
        for status in RecipeCalculationStatus:
            dist[status.value] = sum(1 for r in results if r.calculation_status == status)
        return dist
    
    def _identify_limitations(self, results: List[RecipeNutritionOutput]) -> List[str]:
        """Identify key limitations in the coverage."""
        limitations = []
        
        total_recipes = len(results)
        if total_recipes == 0:
            limitations.append("No recipes processed")
            return limitations
        
        # Mapping coverage
        mapped_recipes = sum(1 for r in results if r.mapped_ingredient_count > 0)
        if mapped_recipes / total_recipes < 0.5:
            limitations.append(
                f"Low mapping coverage: only {mapped_recipes}/{total_recipes} "
                f"recipes have any approved mappings"
            )
        
        # Gram weight coverage
        avg_weight_cov = np.mean([r.gram_weight_coverage for r in results])
        if avg_weight_cov < 0.1:
            limitations.append(
                f"Very low gram weight coverage: {avg_weight_cov:.1%} average. "
                f"Most ingredients lack resolved weights."
            )
        
        # Nutrient completeness
        avg_completeness = np.mean([
            np.mean(list(r.nutrient_completeness.values())) if r.nutrient_completeness else 0
            for r in results
        ])
        if avg_completeness < 0.5:
            limitations.append(
                f"Low nutrient completeness: {avg_completeness:.1%} average. "
                f"Many nutrients missing from IFCT data."
            )
        
        # IFCT missing nutrients
        missing_nutrients = [n for n in NUTRIENT_NAMES 
                           if all(n not in r.total_nutrients for r in results)]
        if missing_nutrients:
            limitations.append(
                f"Nutrients completely unavailable: {', '.join(missing_nutrients)}"
            )
        
        # Partial calculations presented as complete
        partial_as_complete = sum(1 for r in results 
                                   if r.calculation_status == RecipeCalculationStatus.PARTIAL)
        if partial_as_complete > 0:
            limitations.append(
                f"{partial_as_complete} recipes have PARTIAL nutrition but may be "
                f"interpreted as complete without checking completeness fields"
            )
        
        return limitations
    
    def _generate_recommendations(self, results: List[RecipeNutritionOutput]) -> List[str]:
        """Generate recommendations for improving coverage."""
        recommendations = []
        
        total_recipes = len(results)
        if total_recipes == 0:
            return recommendations
        
        # Mapping recommendations
        unmapped_recipes = sum(1 for r in results if r.mapped_ingredient_count == 0)
        if unmapped_recipes > 0:
            recommendations.append(
                f"Priority: Complete mapping review for {unmapped_recipes} recipes "
                f"with zero approved mappings"
            )
        
        # Weight recommendations
        avg_weight_cov = np.mean([r.gram_weight_coverage for r in results])
        if avg_weight_cov < 0.5:
            recommendations.append(
                f"Resolve gram weights for more ingredients. "
                f"Current coverage: {avg_weight_cov:.1%}. "
                f"Focus on household measurement conversions."
            )
        
        # Nutrient recommendations
        incomplete_nutrients = []
        for nutrient in NUTRIENT_NAMES:
            present = sum(1 for r in results if nutrient in r.total_nutrients)
            if present / total_recipes < 0.8:
                incomplete_nutrients.append(nutrient)
        
        if incomplete_nutrients:
            recommendations.append(
                f"IFCT data gaps for: {', '.join(incomplete_nutrients)}. "
                f"Consider supplementing with USDA or other validated sources."
            )
        
        # Reporting recommendations
        recommendations.append(
            "Always report nutrient_completeness alongside total_nutrients. "
            "Do not present PARTIAL results as complete recipe nutrition."
        )
        
        recommendations.append(
            "Track and report preparation-state compatibility for each mapping. "
            "IFCT data is primarily raw foods; cooked preparations need separate handling."
        )
        
        return recommendations
    
    def export_report(
        self,
        report: CoverageReport,
        output_dir: Path,
        prefix: str = "coverage"
    ) -> Dict[str, Path]:
        """Export coverage report to files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = {}
        
        # Summary JSON
        summary_path = output_dir / f"{prefix}_summary.json"
        import json
        with open(summary_path, 'w') as f:
            json.dump(report.summary, f, indent=2, default=str)
        paths['summary'] = summary_path
        
        # Recipe details CSV
        if report.recipe_details:
            details_df = pd.DataFrame(report.recipe_details)
            details_path = output_dir / f"{prefix}_recipe_details.csv"
            details_df.to_csv(details_path, index=False)
            paths['recipe_details'] = details_path
        
        # Nutrient coverage CSV
        if report.nutrient_coverage:
            nutrient_df = pd.DataFrame([
                {'nutrient': k, **v} for k, v in report.nutrient_coverage.items()
            ])
            nutrient_path = output_dir / f"{prefix}_nutrient_coverage.csv"
            nutrient_df.to_csv(nutrient_path, index=False)
            paths['nutrient_coverage'] = nutrient_path
        
        # Ingredient coverage JSON
        ingredient_path = output_dir / f"{prefix}_ingredient_coverage.json"
        with open(ingredient_path, 'w') as f:
            json.dump(report.ingredient_coverage, f, indent=2, default=str)
        paths['ingredient_coverage'] = ingredient_path
        
        # Full report markdown
        md_path = output_dir / f"{prefix}_report.md"
        self._write_markdown_report(report, md_path)
        paths['markdown'] = md_path
        
        return paths
    
    def _write_markdown_report(self, report: CoverageReport, path: Path):
        """Write coverage report as markdown."""
        with open(path, 'w') as f:
            f.write("# Nutrition Calculation Coverage Report\n\n")
            
            f.write("## Summary\n\n")
            for k, v in report.summary.items():
                f.write(f"- **{k}**: {v}\n")
            f.write("\n")
            
            f.write("## Nutrient Coverage\n\n")
            f.write("| Nutrient | Recipes | Coverage | Unit | Mean | Median |\n")
            f.write("|----------|---------|----------|------|------|--------|\n")
            for nutrient, stats in report.nutrient_coverage.items():
                if nutrient == 'overall':
                    continue
                f.write(f"| {nutrient} | {stats.get('recipes_with_nutrient', 0)} | "
                       f"{stats.get('coverage_rate', 0):.1%} | {stats.get('unit', '')} | "
                       f"{stats.get('mean_value', 0)} | {stats.get('median_value', 0)} |\n")
            f.write("\n")
            
            f.write("## Ingredient Coverage\n\n")
            ic = report.ingredient_coverage
            f.write(f"- Total ingredients: {ic.get('total_ingredients', 0)}\n")
            f.write(f"- Total mapped: {ic.get('total_mapped', 0)}\n")
            f.write(f"- Overall mapping rate: {ic.get('overall_mapping_rate', 0):.1%}\n")
            f.write(f"- Mean per-recipe mapping rate: {ic.get('per_recipe_mapping_rate', {}).get('mean', 0):.1%}\n")
            f.write("\n")
            
            f.write("## Limitations\n\n")
            for lim in report.limitations:
                f.write(f"- {lim}\n")
            f.write("\n")
            
            f.write("## Recommendations\n\n")
            for rec in report.recommendations:
                f.write(f"- {rec}\n")
            f.write("\n")


def generate_coverage_report(
    results: List[RecipeNutritionOutput],
    output_dir: Path,
    prefix: str = "coverage"
) -> CoverageReport:
    """Convenience function to generate and export coverage report."""
    # Create a minimal aggregator for summary stats
    from .nutrient_calculator import NutrientCalculator
    from .ingredient_mapping import StrictMappingInterface, ApprovedMappingStore
    from .edible_portion import EdiblePortionCalculator
    
    # Dummy objects for aggregator (only used for summary)
    dummy_calc = None
    dummy_mapping = None
    dummy_ep = None
    
    # Use the analyzer directly with a mock aggregator
    class MockAggregator:
        def get_aggregation_summary(self, results):
            return CoverageAnalyzer(None)._get_summary(results)
    
    analyzer = CoverageAnalyzer(MockAggregator())
    report = analyzer.analyze_results(results)
    analyzer.export_report(report, output_dir, prefix)
    
    return report