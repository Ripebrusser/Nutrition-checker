#!/usr/bin/env python3
"""
Unit tests for IFCT 2017 extraction.
Run: python -m pytest tests/test_ifct_extraction.py -v
"""

import json
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INTERIM_DIR = PROJECT_ROOT / "data" / "interim" / "ifct_extracted"
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "nutrition" / "IFCT_2017"


class TestIFCTRawFiles:
    """Tests for raw IFCT files."""

    def test_ifct_pdf_exists(self):
        assert (RAW_DIR / "IFCT2017.pdf").exists()

    def test_ifct_pdf_hash(self):
        import hashlib
        with open(RAW_DIR / "IFCT2017.pdf", "rb") as f:
            h = hashlib.md5(f.read()).hexdigest()
        assert h == "ef7664ce5d9ae114de6f34aafdf4ca9d"

    def test_decrypted_pdf_exists(self):
        assert (RAW_DIR / "IFCT2017_decrypted.pdf").exists()


class TestIFCTTable1Extraction:
    """Tests for Table 1 (Proximate Principles) extraction."""

    @pytest.fixture(scope="class")
    def table1_chunks(self):
        path = INTERIM_DIR / "table1_raw_chunks.json"
        assert path.exists()
        with open(path) as f:
            return json.load(f)

    @pytest.fixture(scope="class")
    def table1_parsed(self):
        path = INTERIM_DIR / "table1_parsed.csv"
        assert path.exists()
        return pd.read_csv(path)

    def test_chunks_exist(self, table1_chunks):
        assert len(table1_chunks) == 33

    def test_chunks_have_data(self, table1_chunks):
        for chunk in table1_chunks:
            assert "page" in chunk
            assert "data" in chunk
            assert len(chunk["data"]) > 0

    def test_parsed_rows(self, table1_parsed):
        # Should have ~427 rows (deduplicated)
        assert len(table1_parsed) >= 400
        assert len(table1_parsed) <= 450

    def test_parsed_columns(self, table1_parsed):
        expected_cols = {
            'food_code', 'food_name', 'regions', 'food_group',
            'source_page', 'source_table', 'moisture_g', 'protein_g',
            'ash_g', 'fat_g', 'fibre_total_g', 'fibre_insoluble_g',
            'fibre_soluble_g', 'carb_available_g', 'energy_kj'
        }
        assert set(table1_parsed.columns) == expected_cols

    def test_food_code_format(self, table1_parsed):
        # All food codes should match pattern Letter + 3 digits
        codes = table1_parsed['food_code'].dropna()
        for code in codes:
            assert len(code) == 4
            assert code[0].isalpha()
            assert code[1:].isdigit()

    def test_food_codes_unique(self, table1_parsed):
        codes = table1_parsed['food_code'].dropna()
        assert codes.nunique() == len(codes)

    def test_core_nutrients_present(self, table1_parsed):
        # Core nutrients should have 100% coverage
        for col in ['moisture_g', 'protein_g', 'fat_g', 'ash_g', 'energy_kj']:
            non_null = table1_parsed[col].notna().sum()
            coverage = non_null / len(table1_parsed)
            assert coverage >= 0.99, f"{col} coverage {coverage:.1%} < 99%"

    def test_fibre_carb_coverage(self, table1_parsed):
        # Fibre and carb only for foods with full table (~50-55%)
        for col in ['fibre_total_g', 'fibre_insoluble_g', 'fibre_soluble_g', 'carb_available_g']:
            non_null = table1_parsed[col].notna().sum()
            coverage = non_null / len(table1_parsed)
            assert 0.4 <= coverage <= 0.6, f"{col} coverage {coverage:.1%} unexpected"

    def test_food_groups_identified(self, table1_parsed):
        groups = table1_parsed['food_group'].dropna().unique()
        expected_groups = {
            'CEREALS AND MILLETS', 'MARINE FISH', 'ANIMAL MEAT',
            'EGG AND EGG PRODUCTS', 'CONDIMENTS AND SPICES-DRY',
            'MILK AND MILK PRODUCTS'
        }
        for g in expected_groups:
            assert g in groups, f"Missing food group: {g}"

    def test_no_negative_nutrients(self, table1_parsed):
        # Nutrient values should be non-negative (allow ± notation in strings)
        for col in ['moisture_g', 'protein_g', 'fat_g', 'ash_g', 'energy_kj']:
            vals = table1_parsed[col].dropna()
            for v in vals:
                if isinstance(v, str):
                    num_part = v.split('±')[0]
                    try:
                        assert float(num_part) >= 0
                    except ValueError:
                        pass  # Skip non-numeric


class TestIFCTOtherTables:
    """Tests for Tables 2-12 raw extraction."""

    @pytest.mark.parametrize("table_num", range(2, 13))
    def test_table_raw_chunks_exist(self, table_num):
        path = INTERIM_DIR / f"table{table_num}_raw_chunks.json"
        assert path.exists(), f"Missing raw chunks for Table {table_num}"

    @pytest.mark.parametrize("table_num", range(2, 13))
    def test_table_has_chunks(self, table_num):
        path = INTERIM_DIR / f"table{table_num}_raw_chunks.json"
        with open(path) as f:
            chunks = json.load(f)
        assert len(chunks) > 0, f"Table {table_num} has no chunks"


class TestIFCTValidationSample:
    """Tests for the validation sample foods."""

    @pytest.fixture(scope="class")
    def table1_parsed(self):
        path = INTERIM_DIR / "table1_parsed.csv"
        return pd.read_csv(path)

    def test_amaranth_seed(self, table1_parsed):
        row = table1_parsed[table1_parsed['food_code'] == 'A001'].iloc[0]
        assert row['food_name'] == 'Amaranth seed, black (Amaranthus cruentus)'
        assert str(row['moisture_g']) == '9.89'
        assert str(row['protein_g']) == '14.59'

    def test_bajra(self, table1_parsed):
        row = table1_parsed[table1_parsed['food_code'] == 'A003'].iloc[0]
        assert 'Bajra' in row['food_name']
        assert str(row['regions']) in ['6', '6.0']

    def test_rice_parboiled(self, table1_parsed):
        row = table1_parsed[table1_parsed['food_code'] == 'A014'].iloc[0]
        assert 'Rice, parboiled, milled' in row['food_name']

    def test_lentil_brown(self, table1_parsed):
        row = table1_parsed[table1_parsed['food_code'] == 'B014'].iloc[0]
        assert 'Lentil whole, brown' in row['food_name']

    def test_bathua_leaves(self, table1_parsed):
        row = table1_parsed[table1_parsed['food_code'] == 'C008'].iloc[0]
        assert 'Bathua leaves' in row['food_name']

    def test_button_mushroom(self, table1_parsed):
        row = table1_parsed[table1_parsed['food_code'] == 'J001'].iloc[0]
        assert 'Button mushroom' in row['food_name']
        # Mushrooms have fibre/carb in this table
        assert pd.notna(row['fibre_total_g'])
        assert pd.notna(row['carb_available_g'])

    def test_chicken_leg(self, table1_parsed):
        row = table1_parsed[table1_parsed['food_code'] == 'N001'].iloc[0]
        assert 'Chicken, poultry, leg' in row['food_name']

    def test_allathi_fish(self, table1_parsed):
        row = table1_parsed[table1_parsed['food_code'] == 'P001'].iloc[0]
        assert 'Allathi' in row['food_name']

    def test_crab(self, table1_parsed):
        row = table1_parsed[table1_parsed['food_code'] == 'Q001'].iloc[0]
        assert 'Crab' in row['food_name']


class TestIFCTOtherTables:
    """Tests for Tables 2-12 raw extraction."""

    @pytest.mark.parametrize("table_num", range(2, 13))
    def test_table_raw_chunks_exist(self, table_num):
        path = INTERIM_DIR / f"table{table_num}_raw_chunks.json"
        assert path.exists(), f"Missing raw chunks for Table {table_num}"

    @pytest.mark.parametrize("table_num", range(2, 13))
    def test_table_has_chunks(self, table_num):
        path = INTERIM_DIR / f"table{table_num}_raw_chunks.json"
        with open(path) as f:
            chunks = json.load(f)
        assert len(chunks) > 0, f"Table {table_num} has no chunks"


class TestExtractionCoverage:
    """Tests for extraction coverage metrics."""

    @pytest.fixture(scope="class")
    def table1_parsed(self):
        path = INTERIM_DIR / "table1_parsed.csv"
        return pd.read_csv(path)

    def test_extraction_rate(self, table1_parsed):
        # Should extract at least 80% of 528 expected foods
        extracted = len(table1_parsed)
        expected = 528
        rate = extracted / expected
        assert rate >= 0.80, f"Extraction rate {rate:.1%} < 80%"

    def test_food_codes_sequential(self, table1_parsed):
        # Check that food codes follow expected letter prefixes
        codes = table1_parsed['food_code'].dropna().unique()
        prefixes = set(c[0] for c in codes)
        expected_prefixes = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'M', 'N', 'O', 'P', 'Q', 'R'}
        for p in expected_prefixes:
            assert p in prefixes, f"Missing prefix {p}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])