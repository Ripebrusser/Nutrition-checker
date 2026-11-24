#!/usr/bin/env python3
"""
Smoke validation script for NHANES 2019-2020 datasets.
Run: python -m src.data.validate_nhanes
Outputs JSON report to data/interim/validation_reports/nhanes_validation.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd


def validate_nhanes_datasets(data_dir: Path) -> dict:
    """Run smoke validation checks on NHANES datasets."""
    report = {
        "dataset": "NHANES_2019_2020",
        "source_dir": str(data_dir),
        "validation_timestamp": datetime.utcnow().isoformat() + "Z",
        "checks": {}
    }

    files = {
        "BMX_L.xpt": "body_measures",
        "DEMO_L.xpt": "demographics",
        "DIQ_L.xpt": "diabetes_questionnaire",
        "DR1TOT_L.xpt": "dietary_recall_day1",
        "PAQ_L.xpt": "physical_activity"
    }

    for filename, key in files.items():
        path = data_dir / filename
        if path.exists():
            try:
                df = pd.read_sas(path, format="xport", encoding="infer")
                missing = df.isnull().sum().to_dict()
                report["checks"][key] = {
                    "file": filename,
                    "rows": int(len(df)),
                    "columns": int(len(df.columns)),
                    "column_names": list(df.columns),
                    "seqn_unique": int(df["SEQN"].nunique()) if "SEQN" in df.columns else None,
                    "missing_top10": {k: int(v) for k, v in sorted(missing.items(), key=lambda x: -x[1])[:10]}
                }
            except Exception as e:
                report["checks"][key] = {"file": filename, "error": str(e)}
        else:
            report["checks"][key] = {"file": filename, "error": "File not found"}

    # Cross-file SEQN overlap check
    seqn_sets = {}
    # Reverse mapping: key -> filename
    key_to_file = {v: k for k, v in files.items()}
    for key in ["body_measures", "demographics", "diabetes_questionnaire", "dietary_recall_day1", "physical_activity"]:
        if key in report["checks"] and "seqn_unique" in report["checks"][key] and report["checks"][key]["seqn_unique"]:
            filename = key_to_file[key]
            path = data_dir / filename
            df = pd.read_sas(path, format="xport", encoding="infer")
            seqn_sets[key] = set(df["SEQN"].dropna().astype(int))

    if len(seqn_sets) >= 2:
        keys = list(seqn_sets.keys())
        base = seqn_sets[keys[0]]
        overlap = {}
        for k in keys[1:]:
            overlap[k] = len(base & seqn_sets[k])
        report["checks"]["seqn_overlap"] = overlap

    report["overall_passed"] = all("error" not in v for v in report["checks"].values() if isinstance(v, dict))

    return report


def main():
    project_root = Path(__file__).resolve().parents[2]
    data_dir = project_root / "datasets"
    output_dir = project_root / "data" / "interim" / "validation_reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Validating NHANES datasets in {data_dir}...")
    report = validate_nhanes_datasets(data_dir)

    output_path = output_dir / "nhanes_validation.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Validation report written to {output_path}")
    print(f"Overall passed: {report['overall_passed']}")

    for check_name, result in report["checks"].items():
        if "error" in result:
            print(f"  ❌ {check_name}: {result['error']}")
        else:
            print(f"  ✅ {check_name}: {result.get('rows', 'N/A')} rows, {result.get('columns', 'N/A')} cols")

    if not report["overall_passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()