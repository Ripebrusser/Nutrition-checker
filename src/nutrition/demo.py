#!/usr/bin/env python
"""Controlled Demonstration - Nutrition Calculation Engine.

This script demonstrates the nutrition calculation engine using:
A. Synthetic examples (clearly labeled) for calculation correctness
B. Real-data examples using genuinely approved mappings and resolved weights

Run with: python -m src.nutrition.demo
"""

import pandas as pd
import numpy as np
from pathlib import Path

from src.nutrition import (
    NutrientCalculator,
    NutrientValidator,
    EdiblePortionCalculator,
    StrictMappingInterface,
    ApprovedMappingStore,
    ApprovedMapping,
    IngredientWeightInfo,
    IngredientNutritionInput,
    RecipeAggregator,
    MappingStatus,
    CalculationStatus,
    RecipeCalculationStatus,
    MappingDecision,
    MappingReviewRecord,
    IFCTNutrientRecord,
    NUTRIENT_NAMES,
    KJ_TO_KCAL,
    calculate_nutrient_contribution,
    generate_coverage_report,
    CoverageAnalyzer,
    CoverageReport,
    load_approved_mappings_from_jsonl,
    create_weight_infos_from_parsed,
)


def run_synthetic_demonstration():
    """A. Synthetic calculation demonstration."""
    print("=" * 70)
    print("A. SYNTHETIC CALCULATION DEMONSTRATION")
    print("=" * 70)
    print("Using clearly labeled synthetic test data (NOT real IFCT records)\n")
    
    # Synthetic IFCT data - clearly labeled
    synthetic_ifct = pd.DataFrame({
        'food_code': ['SYNTH_001', 'SYNTH_002', 'SYNTH_003'],
        'food_name': ['Synthetic Rice', 'Synthetic Dal', 'Synthetic Spinach'],
        'food_group': ['Cereals', 'Pulses', 'Leafy vegetables'],
        'protein_g': [7.5, 22.0, 2.9],
        'fat_g': [0.5, 1.5, 0.4],
        'carb_available_g': [78.0, 47.0, 2.0],
        'energy_kj': [350.0, 1200.0, 120.0],
        'moisture_g': [12.0, 10.0, 91.0],
        'ash_g': [0.6, 2.8, 1.7],
        'fibre_total_g': [1.0, 15.0, 2.2],
        'fibre_insoluble_g': [0.8, 12.0, 1.8],
        'fibre_soluble_g': [0.2, 3.0, 0.4],
        'source_page': [999, 999, 999],
        'source_table': [999, 999, 999],
        'verification_status': ['SYNTHETIC_TEST'] * 3,
    })
    
    calc = NutrientCalculator(synthetic_ifct)
    approved_store = ApprovedMappingStore()
    mapping_interface = StrictMappingInterface(approved_store, synthetic_ifct)
    ep_calc = EdiblePortionCalculator()
    
    # Add synthetic approved mappings
    mappings = [
        ApprovedMapping(
            recipe_id=1, ingredient_record_id="syn_1",
            original_ingredient="100g rice", normalized_ingredient="rice",
            ifct_food_code="SYNTH_001", ifct_food_name="Synthetic Rice", ifct_food_group="Cereals",
            mapping_status=MappingStatus.APPROVED, preparation_state="RAW",
            reviewer_id="demo", review_timestamp="2026-01-01", confidence=1.0, evidence="SYNTHETIC"
        ),
        ApprovedMapping(
            recipe_id=1, ingredient_record_id="syn_2",
            original_ingredient="50g dal", normalized_ingredient="dal",
            ifct_food_code="SYNTH_002", ifct_food_name="Synthetic Dal", ifct_food_group="Pulses",
            mapping_status=MappingStatus.APPROVED, preparation_state="RAW",
            reviewer_id="demo", review_timestamp="2026-01-01", confidence=1.0, evidence="SYNTHETIC"
        ),
        ApprovedMapping(
            recipe_id=1, ingredient_record_id="syn_3",
            original_ingredient="50g spinach", normalized_ingredient="spinach",
            ifct_food_code="SYNTH_003", ifct_food_name="Synthetic Spinach", ifct_food_group="Leafy vegetables",
            mapping_status=MappingStatus.APPROVED, preparation_state="RAW",
            reviewer_id="demo", review_timestamp="2026-01-01", confidence=1.0, evidence="SYNTHETIC"
        ),
    ]
    for m in mappings:
        approved_store.add_mapping(m)
    
    # Test 1: Basic calculation - 100g rice
    print("Test 1: 100g Synthetic Rice")
    input_data = IngredientNutritionInput(
        recipe_id=1, ingredient_record_id="syn_1",
        original_ingredient="100g rice", normalized_ingredient="rice",
        ifct_food_code="SYNTH_001", ifct_food_name="Synthetic Rice", ifct_food_group="Cereals",
        mapping_status=MappingStatus.APPROVED, preparation_state="RAW",
        edible_weight_g=100.0,
        nutrient_values={'protein_g': 7.5, 'fat_g': 0.5, 'carb_available_g': 78.0, 'energy_kj': 350.0},
        source_provenance="SYNTHETIC_DEMO"
    )
    output = calc.calculate_ingredient_nutrition(input_data)
    output = calc.add_kcal_to_output(output)
    print(f"  Protein: {output.calculated_nutrients['protein_g']} g (expected: 7.5)")
    print(f"  Fat: {output.calculated_nutrients['fat_g']} g (expected: 0.5)")
    print(f"  Carbs: {output.calculated_nutrients['carb_available_g']} g (expected: 78.0)")
    print(f"  Energy: {output.calculated_nutrients['energy_kj']} kJ / {output.calculated_nutrients['energy_kcal']} kcal")
    print(f"  Status: {output.calculation_status.value}")
    
    # Test 2: 50g dal (half weight)
    print("\nTest 2: 50g Synthetic Dal (half weight)")
    input_data = IngredientNutritionInput(
        recipe_id=1, ingredient_record_id="syn_2",
        original_ingredient="50g dal", normalized_ingredient="dal",
        ifct_food_code="SYNTH_002", ifct_food_name="Synthetic Dal", ifct_food_group="Pulses",
        mapping_status=MappingStatus.APPROVED, preparation_state="RAW",
        edible_weight_g=50.0,
        nutrient_values={'protein_g': 22.0, 'fat_g': 1.5, 'carb_available_g': 47.0, 'energy_kj': 1200.0},
        source_provenance="SYNTHETIC_DEMO"
    )
    output = calc.calculate_ingredient_nutrition(input_data)
    output = calc.add_kcal_to_output(output)
    print(f"  Protein: {output.calculated_nutrients['protein_g']} g (expected: 11.0)")
    print(f"  Fat: {output.calculated_nutrients['fat_g']} g (expected: 0.75)")
    print(f"  Carbs: {output.calculated_nutrients['carb_available_g']} g (expected: 23.5)")
    print(f"  Energy: {output.calculated_nutrients['energy_kj']} kJ / {output.calculated_nutrients['energy_kcal']} kcal")
    print(f"  Status: {output.calculation_status.value}")
    
    # Test 3: Recipe aggregation
    print("\nTest 3: Recipe Aggregation (Rice + Dal + Spinach)")
    weight_infos = [
        IngredientWeightInfo(recipe_id=1, ingredient_record_id="syn_1",
                            original_ingredient="100g rice", normalized_ingredient="rice",
                            gram_weight=100.0, conversion_status="RESOLVED",
                            preparation_state="RAW", is_edible_weight=True),
        IngredientWeightInfo(recipe_id=1, ingredient_record_id="syn_2",
                            original_ingredient="50g dal", normalized_ingredient="dal",
                            gram_weight=50.0, conversion_status="RESOLVED",
                            preparation_state="RAW", is_edible_weight=True),
        IngredientWeightInfo(recipe_id=1, ingredient_record_id="syn_3",
                            original_ingredient="50g spinach", normalized_ingredient="spinach",
                            gram_weight=50.0, conversion_status="RESOLVED",
                            preparation_state="RAW", is_edible_weight=True),
    ]
    
    aggregator = RecipeAggregator(calc, mapping_interface, ep_calc)
    result = aggregator.aggregate_recipe(1, weight_infos)
    result = calc.add_kcal_to_recipe(result)
    
    print(f"  Recipe Status: {result.calculation_status.value}")
    print(f"  Mapped ingredients: {result.mapped_ingredient_count}/{result.total_ingredient_count}")
    print(f"  Total Protein: {result.total_nutrients.get('protein_g', 0):.2f} g")
    print(f"  Total Fat: {result.total_nutrients.get('fat_g', 0):.2f} g")
    print(f"  Total Carbs: {result.total_nutrients.get('carb_available_g', 0):.2f} g")
    print(f"  Total Energy: {result.total_nutrients.get('energy_kj', 0):.1f} kJ / {result.total_nutrients.get('energy_kcal', 0):.1f} kcal")
    print(f"  Nutrient completeness: {result.nutrient_completeness}")
    
    # Test 4: Edible portion calculation
    print("\nTest 4: Edible Portion Calculation (Real IFCT codes)")
    # Use real IFCT codes that have edible portion data
    real_ifct = pd.DataFrame({
        'food_code': ['C001', 'D001'],
        'food_name': ['Spinach', 'Potato'],
        'food_group': ['Leafy vegetables', 'Roots and tubers'],
        'protein_g': [2.9, 1.6],
        'fat_g': [0.4, 0.1],
        'carb_available_g': [2.0, 17.0],
        'energy_kj': [120.0, 320.0],
        'moisture_g': [91.0, 79.0],
        'ash_g': [1.7, 0.8],
        'fibre_total_g': [2.2, 1.7],
        'fibre_insoluble_g': [1.8, 1.2],
        'fibre_soluble_g': [0.4, 0.5],
        'source_page': [1, 1],
        'source_table': [1, 1],
        'verification_status': ['verified'] * 2,
    })
    
    ep_calc2 = EdiblePortionCalculator()
    
    # 100g raw spinach -> 85g edible (15% waste)
    weight, info, msg = ep_calc2.calculate_edible_weight(100.0, "C001")
    print(f"  100g raw spinach -> {weight}g edible ({msg})")
    
    # 100g raw potato -> 80g edible (20% waste)
    weight, info, msg = ep_calc2.calculate_edible_weight(100.0, "D001")
    print(f"  100g raw potato -> {weight}g edible ({msg})")
    
    # Already edible weight
    weight, info, msg = ep_calc2.calculate_edible_weight(50.0, "C001", is_already_edible=True)
    print(f"  50g already-edible spinach -> {weight}g edible ({msg})")
    
    print("\n✅ Synthetic demonstration complete")


def run_real_data_demonstration():
    """B. Real-data demonstration using genuinely approved mappings."""
    print("\n" + "=" * 70)
    print("B. REAL-DATA DEMONSTRATION")
    print("=" * 70)
    print("Using genuine IFCT data and approved mappings (if available)\n")
    
    # Load real IFCT data
    ifct_path = Path("data/interim/ifct_final_candidate/ifct_table1_candidate.parquet")
    if not ifct_path.exists():
        print(f"⚠️  IFCT data not found at {ifct_path}")
        print("   Skipping real-data demonstration")
        return
    
    ifct_df = pd.read_parquet(ifct_path)
    print(f"Loaded IFCT data: {len(ifct_df)} foods")
    
    # Check for approved mappings
    mapping_path = Path("data/processed/phase3/approved_mappings.jsonl")
    if not mapping_path.exists():
        print(f"⚠️  No approved mappings found at {mapping_path}")
        print("   This is expected - mappings require human review via the review app")
        print("   Engine will run safely with zero approved mappings")
        return
    
    # Load approved mappings
    approved_store = load_approved_mappings_from_jsonl(mapping_path)
    stats = approved_store.stats()
    print(f"Approved mappings: {stats['total_approved']}")
    print(f"Unique recipes: {stats['unique_recipes']}")
    print(f"Unique IFCT codes: {stats['unique_ifct_codes']}")
    
    if stats['total_approved'] == 0:
        print("No approved mappings available for demonstration")
        return
    
    # Initialize engine
    calc = NutrientCalculator(ifct_df)
    mapping_interface = StrictMappingInterface(approved_store, ifct_df)
    ep_calc = EdiblePortionCalculator()
    aggregator = RecipeAggregator(calc, mapping_interface, ep_calc)
    
    # Load parsed ingredients
    parsed_path = Path("data/interim/phase2/parsed_recipe_ingredients.parquet")
    if not parsed_path.exists():
        print(f"⚠️  Parsed ingredients not found at {parsed_path}")
        return
    
    parsed_df = pd.read_parquet(parsed_path)
    print(f"Loaded parsed ingredients: {len(parsed_df)} records")
    
    # Get recipes with approved mappings
    recipe_ids = list(approved_store._by_recipe.keys())[:5]  # First 5 recipes
    
    print(f"\nDemonstrating on {len(recipe_ids)} recipes with approved mappings...")
    
    results = []
    for recipe_id in recipe_ids:
        # Create weight infos for this recipe
        weight_infos = create_weight_infos_from_parsed(parsed_df, recipe_id)
        
        if not weight_infos:
            continue
        
        result = aggregator.aggregate_recipe(recipe_id, weight_infos)
        result = calc.add_kcal_to_recipe(result)
        results.append(result)
        
        print(f"\n  Recipe {recipe_id}:")
        print(f"    Status: {result.calculation_status.value}")
        print(f"    Mapped: {result.mapped_ingredient_count}/{result.total_ingredient_count}")
        print(f"    Energy: {result.total_nutrients.get('energy_kj', 0):.1f} kJ")
        if 'energy_kcal' in result.total_nutrients:
            print(f"    Energy: {result.total_nutrients['energy_kcal']:.1f} kcal")
        print(f"    Protein: {result.total_nutrients.get('protein_g', 0):.2f} g")
        print(f"    Fat: {result.total_nutrients.get('fat_g', 0):.2f} g")
        print(f"    Carbs: {result.total_nutrients.get('carb_available_g', 0):.2f} g")
    
    # Generate coverage report
    if results:
        analyzer = CoverageAnalyzer(aggregator)
        report = analyzer.analyze_results(results)
        
        print("\n" + "-" * 50)
        print("COVERAGE SUMMARY")
        print("-" * 50)
        print(f"Total recipes: {report.summary.get('total_recipes', 0)}")
        print(f"Recipes with nutrition: {report.summary.get('recipes_with_nutrition', 0)}")
        print(f"Avg mapping coverage: {report.summary.get('avg_mapping_coverage', 0):.1%}")
        print(f"Avg weight coverage: {report.summary.get('avg_gram_weight_coverage', 0):.1%}")
        print(f"Total mapped ingredients: {report.summary.get('total_mapped_ingredients', 0)}")
        print(f"Total ingredients: {report.summary.get('total_ingredients', 0)}")
        print(f"Limitations:")
        for lim in report.limitations:
            print(f"  - {lim}")
    
    print("\n✅ Real-data demonstration complete")


def demonstrate_missing_handling():
    """Demonstrate missing value handling."""
    print("\n" + "=" * 70)
    print("C. MISSING VALUE HANDLING DEMONSTRATION")
    print("=" * 70)
    
    # IFCT with missing nutrients
    ifct_with_missing = pd.DataFrame({
        'food_code': ['TEST_001'],
        'food_name': ['Test Food'],
        'food_group': ['Test'],
        'protein_g': [10.0],
        'fat_g': [5.0],
        'carb_available_g': [60.0],
        'energy_kj': [350.0],
        'moisture_g': [20.0],
        'ash_g': [1.0],
        'fibre_total_g': [None],  # Missing
        'fibre_insoluble_g': [None],  # Missing
        'fibre_soluble_g': [None],  # Missing
        'source_page': [1],
        'source_table': [1],
        'verification_status': ['test'],
    })
    
    calc = NutrientCalculator(ifct_with_missing)
    
    # Test with fallback to IFCT (nutrient_values=None)
    print("Test 1: Fallback to IFCT with missing nutrients")
    input_data = IngredientNutritionInput(
        recipe_id=1, ingredient_record_id="ing_1",
        original_ingredient="test", normalized_ingredient="test",
        ifct_food_code="TEST_001", ifct_food_name="Test Food", ifct_food_group="Test",
        mapping_status=MappingStatus.APPROVED, preparation_state="RAW",
        edible_weight_g=100.0,
        nutrient_values=None,  # Fallback to IFCT
        source_provenance="DEMO"
    )
    output = calc.calculate_ingredient_nutrition(input_data)
    print(f"  Calculated: {list(output.calculated_nutrients.keys())}")
    print(f"  Missing: {output.missing_nutrients}")
    print(f"  Status: {output.calculation_status.value}")
    
    # Test with explicit nutrient_values (only protein)
    print("\nTest 2: Explicit nutrient_values (only protein provided)")
    input_data = IngredientNutritionInput(
        recipe_id=1, ingredient_record_id="ing_2",
        original_ingredient="test", normalized_ingredient="test",
        ifct_food_code="TEST_001", ifct_food_name="Test Food", ifct_food_group="Test",
        mapping_status=MappingStatus.APPROVED, preparation_state="RAW",
        edible_weight_g=100.0,
        nutrient_values={'protein_g': 10.0},  # Only protein
        source_provenance="DEMO"
    )
    output = calc.calculate_ingredient_nutrition(input_data)
    print(f"  Calculated: {list(output.calculated_nutrients.keys())}")
    print(f"  Missing: {output.missing_nutrients}")
    print(f"  Status: {output.calculation_status.value}")
    
    # Test with empty nutrient_values
    print("\nTest 3: Empty nutrient_values dict (no calculation)")
    input_data = IngredientNutritionInput(
        recipe_id=1, ingredient_record_id="ing_3",
        original_ingredient="test", normalized_ingredient="test",
        ifct_food_code="TEST_001", ifct_food_name="Test Food", ifct_food_group="Test",
        mapping_status=MappingStatus.APPROVED, preparation_state="RAW",
        edible_weight_g=100.0,
        nutrient_values={},  # Empty - explicitly no nutrients
        source_provenance="DEMO"
    )
    output = calc.calculate_ingredient_nutrition(input_data)
    print(f"  Calculated: {list(output.calculated_nutrients.keys())}")
    print(f"  Missing: {output.missing_nutrients}")
    print(f"  Status: {output.calculation_status.value}")
    
    print("\n✅ Missing value handling demonstration complete")


if __name__ == "__main__":
    print("NUTRITION CALCULATION ENGINE - CONTROLLED DEMONSTRATION")
    print("=" * 70)
    
    run_synthetic_demonstration()
    run_real_data_demonstration()
    demonstrate_missing_handling()
    
    print("\n" + "=" * 70)
    print("ALL DEMONSTRATIONS COMPLETE")
    print("=" * 70)