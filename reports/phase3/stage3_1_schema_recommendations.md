# Stage 3.1: Schema Recommendations

**Date:** 2026-11-18  
**Based on:** Stage 3.1 Design Audit findings

---

## 1. Review Unit Schema — Revised

### 1.1 Primary Key Change

**Current (Flawed):**
```sql
PRIMARY KEY (primary_ingredient, ifct_food_code)
```

**Revised (Required):**
```sql
PRIMARY KEY (primary_ingredient, ifct_food_code, preparation_state)
```

### 1.2 Complete Revised Schema

```python
review_unit = {
    # Identity (Composite PK)
    'review_unit_id': 'string',           # UUID v4 (surrogate key for FKs)
    'primary_ingredient': 'string',       # Cleaned ingredient name
    'ifct_food_code': 'string',           # IFCT code (e.g., G025)
    'ifct_food_name': 'string',           # Full IFCT food name
    'ifct_food_group': 'string',          # IFCT food group
    'preparation_state': 'string',        # RAW/FRESH/DRIED/POWDERED/GROUND/ROASTED/FRIED/BOILED/COOKED/FERMENTED/PICKLED/SPROUTED/SOAKED/BLANCHED/MARINATED/NOT_SPECIFIED/UNKNOWN
    
    # Matching
    'match_method': 'string',             # EXACT/SYNONYM/TOKEN_EQUIVALENT/TOKEN_SIMILARITY/FUZZY
    'max_similarity': 'float64',          # Max similarity score across candidates
    
    # Aggregation
    'recipe_count': 'int64',              # Unique recipes
    'candidate_count': 'int64',           # Total candidate rows
    
    # Disambiguation
    'preparation_confidence': 'float64',  # 0.0–1.0
    'ambiguity_flags': 'string',          # JSON array of flags
    'extracted_aliases': 'string',        # JSON array of alias objects
    
    # Stage 2.3 Evidence
    'acceptance_evidence': 'string',      # JSON of Stage 2.3 gate decision
    
    # Scheduling
    'priority_score': 'float64',          # Numeric priority (higher = earlier)
    
    # Status
    'status': 'string',                   # PENDING/DRAFT/REVIEW_REQUIRED/ACCEPTED/REJECTED/UNMATCHED/AMBIGUOUS
    
    # Metadata
    'created_at': 'timestamp[us]',
    'updated_at': 'timestamp[us]',
}
```

### 1.3 New Fields Added

| Field | Type | Purpose |
|-------|------|---------|
| `preparation_state` | string (PK component) | Distinguishes raw/cooked/dried forms |
| `review_unit_id` | UUID (surrogate) | Stable FK target for decisions/provenance |
| `status` | enum | Includes DRAFT, PENDING, ESCALATED |

---

## 2. Decision Schema — Revised

### 2.1 Status Enum Extension

**Current:**
```python
valid_statuses = {'PENDING', 'ACCEPTED', 'REVIEW_REQUIRED', 'REJECTED', 'UNMATCHED', 'AMBIGUOUS', 'CONFLICT'}
```

**Revised:**
```python
valid_statuses = {
    'DRAFT',              # Reviewer working on it, not submitted
    'PENDING',            # Submitted, awaiting review
    'REVIEW_REQUIRED',    # Submitted, needs more evidence
    'ACCEPTED',           # Terminal: mapping confirmed
    'REJECTED',           # Terminal: mapping rejected
    'UNMATCHED',          # Terminal: no IFCT equivalent
    'AMBIGUOUS',          # Revisitable: multiple codes plausible
    'UNMATCHED',          # Revisitable: no IFCT equivalent found
    'CONFLICT',           # Audit: reviewer disagreement
    'ESCALATED',          # Senior review pending
}
```

### 2.2 Valid State Transitions

```python
VALID_TRANSITIONS = {
    'DRAFT': ['PENDING', 'REVIEW_REQUIRED'],
    'PENDING': ['ACCEPTED', 'REVIEW_REQUIRED', 'REJECTED', 'UNMATCHED', 'AMBIGUOUS'],
    'REVIEW_REQUIRED': ['ACCEPTED', 'REJECTED', 'UNMATCHED', 'AMBIGUOUS', 'ESCALATED'],
    'ESCALATED': ['ACCEPTED', 'REVIEW_REQUIRED', 'REJECTED', 'UNMATCHED', 'AMBIGUOUS'],
    'AMBIGUOUS': ['REVIEW_REQUIRED'],           # Revisitable
    'UNMATCHED': ['REVIEW_REQUIRED'],           # Revisitable
    'REJECTED': ['REVIEW_REQUIRED'],            # Re-review if new evidence
    'ACCEPTED': [],                             # Terminal
    'CONFLICT': ['ACCEPTED', 'REVIEW_REQUIRED', 'REJECTED', 'UNMATCHED', 'AMBIGUOUS'],
}
```

### 2.3 Decision Schema — Revised

```python
decision = {
    'decision_id': 'string',              # UUID v4
    'review_unit_id': 'string',           # FK to review_units
    'reviewer_id': 'string',              # Reviewer identifier
    'timestamp': 'timestamp[us]',         # Decision timestamp
    'status': 'string',                   # ACCEPTED/REVIEW_REQUIRED/REJECTED/UNMATCHED/AMBIGUOUS
    'previous_status': 'string',          # For audit trail
    'rationale': 'string',                # Min 50 chars, max 2000
    'confidence': 'int8',                 # 1–5 scale
    'alternative_ifct_code': 'string',    # Nullable
    'evidence_references': 'string',      # JSON array (MANDATORY for ACCEPTED)
    'uncertainty_notes': 'string',        # Nullable: limitations, caveats
    'session_id': 'string',               # UUID v4
    'duration_seconds': 'int32',          # Time spent
    'created_at': 'timestamp[us]',
    'updated_at': 'timestamp[us]',        # For DRAFT updates
}
```

### 2.4 Evidence References — Mandatory for ACCEPTED

```json
{
  "evidence_references": [
    "ifct_food_code",
    "ifct_food_name", 
    "ifct_food_group",
    "match_method",
    "similarity_score",
    "preparation_state",
    "preparation_confidence",
    "prep_state_compat",
    "extracted_aliases",
    "ambiguity_flags",
    "ifct_source_page",
    "ifct_table_number",
    "species_verification",
    "edible_part_verification",
    "prep_compatibility_evidence"
  ]
}
```

---

## 3. Review Unit Generation — Revised Algorithm

### 3.1 Current (Flawed)
```python
# Groups by (primary_ingredient, ifct_food_code) only
# Loses preparation_state dimension
```

### 3.2 Revised Algorithm

```python
def generate_review_units(
    candidates: pd.DataFrame,
    disambiguated: pd.DataFrame,
    ifct: pd.DataFrame
) -> pd.DataFrame:
    """
    Generate review units with preparation_state dimension.
    Deterministic, pure function.
    """
    # Merge candidates with disambiguated prep state
    merged = candidates.merge(
        disambiguated[['recipe_id', 'normalized_ingredient', 'primary_ingredient', 
                       'preparation_state', 'preparation_confidence', 
                       'extracted_aliases', 'ambiguity_flags']],
        on=['recipe_id', 'normalized_ingredient'],
        how='left'
    )
    
    # Fill missing prep state from disambiguated
    merged['preparation_state'] = merged['preparation_state'].fillna('NOT_SPECIFIED')
    merged['preparation_confidence'] = merged['preparation_confidence'].fillna(0.5)
    
    # Group by (primary_ingredient, ifct_food_code, preparation_state)
    grouped = merged.groupby(['primary_ingredient', 'ifct_food_code', 'preparation_state']).agg(
        recipe_count=('recipe_id', 'nunique'),
        candidate_count=('recipe_id', 'count'),
        match_method=('match_method', 'first'),
        max_similarity=('similarity_score', 'max'),
        preparation_confidence=('preparation_confidence', 'max'),
        ambiguity_flags=('ambiguity_flags', lambda x: list(set().union(*[eval(v) if isinstance(v, str) else [] for v in x]))),
        extracted_aliases=('extracted_aliases', 'first'),
        acceptance_evidence=('evidence', 'first'),  # JSON
    ).reset_index()
    
    # Compute priority score
    grouped['priority_score'] = grouped.apply(compute_priority_score, axis=1)
    
    # Add surrogate key
    grouped['review_unit_id'] = [uuid.uuid4().hex for _ in range(len(grouped))]
    
    # Initial status
    grouped['status'] = 'PENDING'
    
    return grouped
```

### 3.3 Expected Output Change

| Metric | Current | Revised (Estimated) |
|--------|---------|---------------------|
| Review units | 7,165 | ~8,200–8,500 |
| Auto-accepted units | 3 | ~3–4 |
| Multi-code units | 1,255 | Similar (by ingredient) |

---

## 4. Provenance Links — Revised Schema

### 4.1 Primary Key Extension

```sql
PRIMARY KEY (review_unit_id, recipe_id, preparation_state)
```

### 4.2 Schema

```python
provenance_link = {
    'review_unit_id': 'string',           # FK to review_units
    'recipe_id': 'int64',                 # Recipe identifier
    'preparation_state': 'string',        # PK component
    'original_line': 'string',            # Full original ingredient line
    'source_field': 'string',             # ingredients_raw / ingredients_en
    'original_ingredient': 'string',      # Original ingredient text
    'normalized_ingredient': 'string',    # Normalized text
    'source_line': 'string',              # Full source line
    'extracted_aliases': 'string',        # JSON array
    'preparation_state': 'string',        # Prep state
    'preparation_confidence': 'float64',  # Confidence
    'quantity': 'string',                 # JSON of parsed quantity
    'unit': 'string',                     # JSON of parsed unit
    'preparation': 'string',              # Parsed preparation
    'size_descriptor': 'string',          # Size descriptor
    'timestamp': 'timestamp[us]',         # Disambiguation timestamp
}
```

---

## 4. Decision Schema — Revised (Continued)

### 4.1 Evidence References — Mandatory Fields

| Evidence Field | Description | Required for ACCEPTED |
|----------------|-------------|----------------------|
| `ifct_food_code` | IFCT code | Yes |
| `ifct_food_name` | Official IFCT food name | Yes |
| `ifct_food_group` | IFCT food group | Yes |
| `ifct_source_page` | IFCT 2017 page number | Yes |
| `ifct_table_number` | IFCT table number | Yes |
| `match_method` | EXACT/SYNONYM/etc | Yes |
| `similarity_score` | 0.0–1.0 | Yes |
| `ifct_food_name` | Full IFCT name with scientific name | Yes |
| `species_verification` | Species match confirmation | Yes |
| `edible_part_verification` | Edible part match | Yes |
| `prep_compatibility_evidence` | How prep state matches IFCT basis | Yes |
| `match_method` | EXACT/SYNONYM/etc | Yes |
| `similarity_score` | 0.0–1.0 | Yes |
| `preparation_state` | RAW/FRESH/etc | Yes |
| `preparation_confidence` | 0.0–1.0 | Yes |
| `prep_state_compat` | 0.0/0.5/1.0 | Yes |
| `extracted_aliases` | JSON array | Yes |
| `ambiguity_flags` | JSON array | Yes |
| `species_verification` | Scientific name match | Yes |
| `edible_part_verification` | Edible part match | Yes |
| `prep_compatibility_evidence` | How prep state matches IFCT basis | Yes |

---

## 4. Provenance Links — Revised (Continued)

### 4.2 Recipe-Level Provenance Enhancement

```python
# Add to provenance_links for full traceability
provenance_link = {
    # ... existing fields ...
    'match_method_at_recipe': 'string',      # Method for this specific recipe
    'similarity_at_recipe': 'float64',       # Similarity for this recipe
    'prep_state_at_recipe': 'string',        # Prep state for this recipe
    'auto_accept_at_recipe': 'boolean',      # Was this recipe auto-accepted?
}
```

---

## 5. Audit Samples Schema — Revised

### 5.1 Enhanced Audit Sample Schema

```python
audit_sample = {
    'sample_id': 'string',                # UUID v4
    'review_unit_id': 'string',           # FK to review_units
    'first_decision_id': 'string',        # FK to decisions
    'second_reviewer_id': 'string',       # Nullable
    'second_decision_id': 'string',       # Nullable, FK to decisions
    'agreement': 'boolean',               # True if statuses match
    'agreement_type': 'string',           # FULL / PARTIAL / NONE
    'escalated': 'boolean',               # Default false
    'resolved_by': 'string',              # Nullable
    'resolution_timestamp': 'timestamp[us]', # Nullable
    'resolution_rationale': 'string',     # Required if escalated
    'kappa_contribution': 'float64',      # For weighted kappa
    'created_at': 'timestamp[us]',
}
```

### 5.2 Agreement Type Enum

```python
agreement_type = {
    'FULL',      # Same status, same alternative code
    'PARTIAL',   # Same status category, different details
    'NONE',      # Different status
}
```

---

## 6. Session Logs — Revised

### 6.1 Enhanced Session Log

```python
session_log = {
    'session_id': 'string',               # UUID v4
    'reviewer_id': 'string',
    'start_time': 'timestamp[us]',
    'end_time': 'timestamp[us]',          # Nullable
    'units_requested': 'int32',
    'units_completed': 'int32',
    'units_reviewed': 'int32',            # Actually reviewed
    'units_skipped': 'int32',
    'breaks_count': 'int16',
    'total_active_seconds': 'int32',      # Excluding breaks
    'total_duration_seconds': 'int32',
    'status': 'string',                   # COMPLETED / INTERRUPTED / EXPIRED
    'calibration_passed': 'boolean',      # For first session
    'issues_reported': 'string',          # JSON array
    'avg_evidence_time_seconds': 'float64',
    'avg_rationale_length': 'float64',
}
```

---

## 5. Audit Samples Schema — Revised (Continued)

### 5.3 Stratified Sampling Configuration — Corrected

```python
# CORRECTED populations based on actual Stage 2.3 data
STRATA_CONFIG = {
    # Population = review units, not candidates
    'ACCEPTED_EXACT':       {'rate': 0.20, 'min_n': 10},   # pop ~25
    'ACCEPTED_SYNONYM':     {'rate': 0.20, 'min_n': 1},    # pop ~0-3
    'REVIEW_REQUIRED_EXACT': {'rate': 0.10, 'min_n': 5},  # pop ~21
    'REVIEW_REQUIRED_SYNONYM': {'rate': 0.10, 'min_n': 5}, # pop ~21
    'REVIEW_REQUIRED_TOKEN_EQUIV': {'rate': 0.10, 'min_n': 15}, # pop ~149
    'REVIEW_REQUIRED_TOKEN_SIM': {'rate': 0.10, 'min_n': 50},  # pop ~6,949
    'REJECTED':             {'rate': 0.05, 'min_n': 5},    # pop unknown
    'AMBIGUOUS':            {'rate': 1.00, 'min_n': 1},    # pop ~1,255 ingredients
    'UNMATCHED':            {'rate': 0.05, 'min_n': 5},    # pop unknown
    'CONFLICT':             {'rate': 1.00, 'min_n': 1},    # all conflicts
}

SEED = 42  # Fixed, documented, reproducible
```

### 5.4 Weighted Kappa for Imbalanced Classes

```python
# Use Gwet's AC1 or weighted Cohen's kappa for imbalanced classes
# AC1 less sensitive to prevalence
def gwet_ac1(agreements, n_categories, n_raters=2):
    """
    Gwet's AC1 agreement coefficient.
    Less sensitive to class imbalance than Cohen's kappa.
    """
    # Implementation per Gwet (2008)
    pass

def weighted_kappa_linear(ratings1, ratings2, n_categories):
    """
    Linear weighted kappa for ordinal statuses.
    """
    # statuses: REJECTED=0, UNMATCHED=1, AMBIGUOUS=2, REVIEW_REQUIRED=3, ACCEPTED=4
    pass
```

---

## 7. Provenance Links — Revised (Continued)

### 7.1 Provenance PK Revision

```sql
-- Current (flawed)
PRIMARY KEY (review_unit_id, recipe_id)

-- Revised (includes preparation_state)
PRIMARY KEY (review_unit_id, recipe_id, preparation_state)
```

### 7.2 Provenance Link Generation

```python
def generate_provenance_links(review_units, candidates, disambiguated):
    """
    Generate provenance links for each review unit.
    One row per (review_unit, recipe, preparation_state).
    """
    # Candidates already have preparation_state from disambiguated merge
    merged = candidates.merge(
        disambiguated[['recipe_id', 'normalized_ingredient', 
                       'preparation_state', 'preparation_confidence']],
        on=['recipe_id', 'normalized_ingredient'],
        how='left'
    )
    
    # Link to review units
    provenance = merged.merge(
        review_units[['review_unit_id', 'primary_ingredient', 'ifct_food_code', 'preparation_state']],
        on=['primary_ingredient', 'ifct_food_code', 'preparation_state'],
        how='inner'
    )
    
    return provenance[['review_unit_id', 'recipe_id', 'preparation_state',
                       'original_line', 'source_field', 'original_ingredient',
                       'normalized_ingredient', 'source_line', 'extracted_aliases',
                       'preparation_state', 'preparation_confidence',
                       'quantity', 'unit', 'preparation', 'size_descriptor',
                       'timestamp']]
```

---

## 6. Audit Samples Schema — Revised (Continued)

### 6.1 Weighted Kappa for Ordinal Statuses

```python
# Status ordinal mapping for weighted kappa
STATUS_ORDINAL = {
    'REJECTED': 0,
    'UNMATCHED': 1,
    'AMBIGUOUS': 2,
    'REVIEW_REQUIRED': 2,  # Same level as AMBIGUOUS
    'ACCEPTED': 3,
}

def weighted_kappa_linear(rater1, rater2):
    """Linear weighted kappa for ordinal statuses."""
    # Convert statuses to ordinal values
    o1 = [STATUS_ORDINAL[s] for s in rater1]
    o2 = [STATUS_ORDINAL[s] for s in rater2]
    # Linear weights: 1 - |o1 - o2| / (k-1)
    k = max(STATUS_ORDINAL.values()) + 1
    weights = 1 - np.abs(np.subtract.outer(o1, o2)) / (k - 1)
    # Weighted agreement
    po = np.mean(np.diag(weights))
    # Expected agreement
    pe = ...
    return (po - pe) / (1 - pe)
```

### 6.2 Confidence Intervals for Agreement

```python
def kappa_ci(kappa, n, alpha=0.05):
    """Approximate 95% CI for kappa."""
    se = np.sqrt((kappa * (1 - kappa)) / (n * (1 - pe)**2))
    z = 1.96
    return kappa - z * se, kappa + z * se
```

---

## 7. File Output Schema — Revised

### 7.1 Manifest Format

```json
{
  "schema_version": "1.1",
  "generated_at": "2026-11-18T...",
  "generator": "stage3_review_unit_generator_v1.1",
  "files": {
    "review_units_v1.1_20261118.parquet": {
      "sha256": "...",
      "rows": 8234,
      "schema_hash": "..."
    },
    "decisions_v1.1_20261118.parquet": {
      "sha256": "...",
      "rows": 0,
      "schema_hash": "..."
    },
    "audit_samples_v1.1_20261118.parquet": {
      "sha256": "...",
      "rows": 0,
      "schema_hash": "..."
    },
    "provenance_links_v1.1_20261118.parquet": {
      "sha256": "...",
      "rows": 119474,
      "schema_hash": "..."
    },
    "session_logs_v1.1_20261118.parquet": {
      "sha256": "...",
      "rows": 0,
      "schema_hash": "..."
    }
  },
  "frozen_inputs": {
    "stage2_3_candidates": "sha256:...",
    "stage2_3_disambiguated": "sha256:...",
    "ifct_reference": "sha256:..."
  }
}
```

---

## 8. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-11-18 | Initial design |
| 1.1 | 2026-11-18 | Added preparation_state to PK; added DRAFT/ESCALATED statuses; mandatory evidence for ACCEPTED; corrected audit sampling; added Gwet's AC1; provenance PK fix |

---

## 9. Migration Checklist

- [ ] Update review unit generator to include `preparation_state` in grouping
- [ ] Update decision schema validation
- [ ] Update audit sample drawing with corrected strata
- [ ] Update provenance link generation
- [ ] Update schema validation rules
- [ ] Update manifest format
- [ ] Regenerate all Stage 3 outputs with v1.1 schemas
- [ ] Verify backward compatibility (v1.0 readable by v1.1 parser)

---

*End of Schema Recommendations*