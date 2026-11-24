# Stage 3: Review Data Schema

## Overview

Complete schema definitions for all Stage 3 review data structures. All schemas are versioned and frozen upon Stage 3 design approval.

**Version:** 1.0  
**Frozen:** 2026-11-18  
**Serialization:** Parquet (primary), CSV (interchange), JSON (API)

---

## 1. Review Unit Schema (`review_units`)

### Parquet Schema
```python
review_unit = {
    # Identity
    'review_unit_id': 'string',           # UUID v4
    'primary_ingredient': 'string',       # Cleaned ingredient name
    'ifct_food_code': 'string',           # IFCT code (e.g., G025)
    'ifct_food_name': 'string',           # Full IFCT food name
    'ifct_food_group': 'string',          # IFCT food group
    
    # Matching
    'match_method': 'string',             # EXACT/SYNONYM/TOKEN_EQUIVALENT/TOKEN_SIMILARITY/FUZZY
    'max_similarity': 'float64',          # Max similarity score across candidates
    
    # Aggregation
    'recipe_count': 'int64',              # Unique recipes
    'candidate_count': 'int64',           # Total candidate rows
    
    # Disambiguation
    'preparation_state': 'string',        # RAW/FRESH/DRIED/POWDERED/GROUND/ROASTED/FRIED/BOILED/COOKED/FERMENTED/PICKLED/SPROUTED/SOAKED/BLANCHED/MARINATED/NOT_SPECIFIED/UNKNOWN
    'preparation_confidence': 'float64',  # 0.0–1.0
    'ambiguity_flags': 'string',          # JSON array of flags
    'extracted_aliases': 'string',        # JSON array of alias objects
    
    # Stage 2.3 Evidence
    'acceptance_evidence': 'string',      # JSON of Stage 2.3 gate decision
    
    # Scheduling
    'priority_score': 'float64',          # Numeric priority (higher = earlier)
    
    # Status
    'status': 'string',                   # PENDING/ACCEPTED/REVIEW_REQUIRED/REJECTED/UNMATCHED/AMBIGUOUS
    
    # Metadata
    'created_at': 'timestamp[us]',        # Generation timestamp
    'updated_at': 'timestamp[us]',        # Last update timestamp
}
```

### Alias Object (in `extracted_aliases` JSON array)
```json
{
  "text": "string",           // Alias text
  "type": "string",           // QUANTITY/SIZE/PREPARATION/HINDI_NAME/EDIBLE_PART/VARIETY/ALTERNATE_NAME/SYNONYM/EXPLANATORY/UNCLASSIFIED
  "confidence": "float",      // 0.0–1.0
  "start_pos": "int",         // Start position in source text
  "end_pos": "int"            // End position in source text
}
```

### Ambiguity Flags (in `ambiguity_flags` JSON array)
```json
[
  "GENERIC_AMBIGUOUS_TERM",
  "MULTIPLE_SYNONYMS",
  "CONFLICTING_PREPARATION",
  "UNBALANCED_PARENTHESES",
  "COMPOSITE_INGREDIENT",
  "PREPARATION_STATE_MISMATCH"
]
```

### Acceptance Evidence (in `acceptance_evidence` JSON)
```json
{
  "auto_accept": true,
  "reasons": ["NON_RAW_PREP_STATE", "PREP_COMPAT_BELOW_THRESHOLD"],
  "evidence": {
    "prep_state": "POWDERED",
    "incompatible": true
  }
}
```

### Status Enum
| Value | Meaning |
|-------|---------|
| `PENDING` | Not yet reviewed |
| `ACCEPTED` | Identity, prep, species confirmed |
| `REVIEW_REQUIRED` | Plausible but evidence gap |
| `REJECTED` | Incorrect mapping |
| `UNMATCHED` | No defensible IFCT equivalent |
| `AMBIGUOUS` | Multiple equally plausible IFCT codes |
| `CONFLICT` | Reviewer disagreement (audit only) |

---

## 2. Decision Schema (`decisions`)

### Parquet Schema
```python
decision = {
    'decision_id': 'string',              # UUID v4
    'review_unit_id': 'string',           # FK to review_units
    'reviewer_id': 'string',              // Reviewer identifier
    'timestamp': 'timestamp[us]',         // Decision timestamp
    'status': 'string',                   // ACCEPTED/REVIEW_REQUIRED/REJECTED/UNMATCHED/AMBIGUOUS
    'rationale': 'string',                // Min 50 chars, max 2000
    'confidence': 'int8',                 // 1–5 scale
    'alternative_ifct_code': 'string',    // Nullable
    'evidence_references': 'string',      // JSON array of field names cited
    'session_id': 'string',               // UUID v4
    'duration_seconds': 'int32',          // Time spent on this unit
    'created_at': 'timestamp[us]'         // Record creation timestamp
}
```

### Evidence References (JSON array)
```json
[
  "preparation_state",
  "match_method",
  "similarity_score",
  "ifct_food_name",
  "extracted_aliases",
  "prep_state_compat",
  "ambiguity_flags"
]
```

### Status Constraints
| Status | Valid Transitions From |
|--------|------------------------|
| PENDING | → ACCEPTED, REVIEW_REQUIRED, REJECTED, UNMATCHED, AMBIGUOUS |
| ACCEPTED | (terminal) |
| REVIEW_REQUIRED | → ACCEPTED, REJECTED, UNMATCHED, AMBIGUOUS (re-review) |
| REJECTED | → REVIEW_REQUIRED (re-review) |
| UNMATCHED | → REVIEW_REQUIRED (re-review) |
| AMBIGUOUS | → REVIEW_REQUIRED (re-review) |

---

## 3. Audit Sample Schema (`audit_samples`)

### Parquet Schema
```python
audit_sample = {
    'sample_id': 'string',                // UUID v4
    'review_unit_id': 'string',           // FK to review_units
    'first_decision_id': 'string',        // FK to decisions
    'second_reviewer_id': 'string',       // Nullable
    'second_decision_id': 'string',       // Nullable, FK to decisions
    'agreement': 'boolean',               // Nullable (true if statuses match)
    'escalated': 'boolean',               // Default false
    'resolved_by': 'string',              // Nullable
    'resolution_timestamp': 'timestamp[us]', // Nullable
    'created_at': 'timestamp[us]'         // Creation timestamp
}
```

### Sampling Strata
| Stratum | Population | Sample Rate | Min Samples |
|---------|------------|-------------|-------------|
| ACCEPTED (EXACT) | ~46 | 20% | 10 |
| ACCEPTED (SYNONYM) | ~0 | 20% | 1 |
| REVIEW_REQUIRED (TOKEN_EQUIVALENT) | ~149 | 10% | 15 |
| REVIEW_REQUIRED (TOKEN_SIMILARITY) | ~6949 | 10% | 50 |
| REVIEW_REQUIRED (SYNONYM) | ~21 | 10% | 5 |
| REJECTED | ~0 | 5% | 5 |
| AMBIGUOUS | ~0 | 100% | All |
| UNMATCHED | ~0 | 5% | 5 |

---

## 4. Provenance Link Schema (`provenance_links`)

### Parquet Schema
```python
provenance_link = {
    'review_unit_id': 'string',           // FK to review_units
    'recipe_id': 'int64',                 // Recipe identifier
    'original_line': 'string',            // Full original ingredient line
    'source_field': 'string',             // ingredients_raw / ingredients_en
    'original_ingredient': 'string',      // Original ingredient text
    'normalized_ingredient': 'string',    // Normalized text
    'source_line': 'string',              // Full source line
    'extracted_aliases': 'string',        // JSON array
    'preparation_state': 'string',        // Prep state
    'preparation_confidence': 'float64',  // Confidence
    'quantity': 'string',                 // JSON of parsed quantity
    'unit': 'string',                     // JSON of parsed unit
    'preparation': 'string',              // Parsed preparation
    'size_descriptor': 'string',          // Size descriptor
    'timestamp': 'timestamp[us]'          // Disambiguation timestamp
}
```

### Primary Key
```sql
PRIMARY KEY (review_unit_id, recipe_id)
```

---

## 4. Session Log Schema (`session_logs`)

### Parquet Schema
```python
session_log = {
    'session_id': 'string',               // UUID v4
    'reviewer_id': 'string',              // Reviewer identifier
    'start_time': 'timestamp[us]',
    'end_time': 'timestamp[us]',          // Nullable
    'units_requested': 'int32',
    'units_completed': 'int32',
    'units_skipped': 'int32',
    'breaks_count': 'int16',
    'total_duration_seconds': 'int32',
    'status': 'string',                   // COMPLETED / INTERRUPTED / EXPIRED
    'issues_reported': 'string',          // JSON array
}
```

---

## 5. Priority Score Formula

```python
def compute_priority_score(unit: ReviewUnit) -> float:
    """
    Higher score = higher priority (reviewed first).
    Range: 0.0 – 100.0
    """
    score = 0.0
    
    # Match method (0–40)
    method_weights = {
        'EXACT': 40,
        'SYNONYM': 30,
        'TOKEN_EQUIVALENT': 20,
        'TOKEN_SIMILARITY': 10,
        'FUZZY': 0
    }
    score += method_weights.get(unit.match_method, 0)
    
    # Preparation state (0–30)
    prep_weights = {
        'FRESH': 30,
        'RAW': 30,
        'NOT_SPECIFIED': 15,
        'DRIED': 5,
        'POWDERED': 5,
        'GROUND': 5,
        'ROASTED': 5,
        'FRIED': 5,
        'BOILED': 5,
        'COOKED': 5,
        'SPROUTED': 5,
        'FERMENTED': 5,
        'PICKLED': 5,
        'SOAKED': 10,
        'ROASTED': 5,
        'BLANCHED': 5,
        'MARINATED': 5,
        'FRIED': 5,
        'UNKNOWN': 5
    }
    score += prep_weights.get(unit.preparation_state, 0)
    
    # Recipe coverage (0–20)
    score += min(unit.recipe_count * 2, 20)
    
    # Similarity (0–10)
    score += unit.max_similarity * 10
    
    return round(score, 2)
```

---

## 6. File Naming Conventions

| File | Pattern | Example |
|------|---------|---------|
| Review units | `review_units_v{VERSION}_{DATE}.parquet` | `review_units_v1.0_20261118.parquet` |
| Decisions | `decisions_v{VERSION}_{DATE}.parquet` | `decisions_v1.0_20261118.parquet` |
| Audit samples | `audit_samples_v{VERSION}_{DATE}.parquet` | `audit_samples_v1.0_20261118.parquet` |
| Provenance links | `provenance_links_v{VERSION}_{DATE}.parquet` | `provenance_links_v1.0_20261118.parquet` |
| Session logs | `session_logs_v{VERSION}_{DATE}.parquet` | `session_logs_v1.0_20261118.parquet` |

---

## 7. Versioning

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-11-18 | Initial design |

**Schema changes require:** Design review, migration plan, backward compatibility test.

---

## 8. Validation Rules

### Review Unit Validation
```python
def validate_review_unit(unit: dict) -> List[str]:
    errors = []
    
    # Required fields
    required = ['review_unit_id', 'primary_ingredient', 'ifct_food_code', 
                'ifct_food_name', 'ifct_food_group', 'match_method',
                'recipe_count', 'candidate_count', 'max_similarity',
                'preparation_state', 'priority_score', 'status']
    for field in required:
        if field not in unit or unit[field] is None:
            errors.append(f"Missing required field: {field}")
    
    # Enum validation
    valid_methods = {'EXACT', 'SYNONYM', 'TOKEN_EQUIVALENT', 'TOKEN_SIMILARITY', 'FUZZY'}
    if unit.get('match_method') not in valid_methods:
        errors.append(f"Invalid match_method: {unit.get('match_method')}")
    
    valid_statuses = {'PENDING', 'ACCEPTED', 'REVIEW_REQUIRED', 'REJECTED', 'UNMATCHED', 'AMBIGUOUS', 'CONFLICT'}
    if unit.get('status') not in valid_statuses:
        errors.append(f"Invalid status: {unit.get('status')}")
    
    valid_prep_states = {'RAW', 'FRESH', 'DRIED', 'POWDERED', 'GROUND', 'ROASTED', 
                         'FRIED', 'BOILED', 'COOKED', 'FERMENTED', 'PICKLED', 
                         'SPROUTED', 'SOAKED', 'BLANCHED', 'MARINATED', 'NOT_SPECIFIED', 'UNKNOWN'}
    if unit.get('preparation_state') not in valid_prep_states:
        errors.append(f"Invalid preparation_state: {unit.get('preparation_state')}")
    
    # Range checks
    if not (0.0 <= unit.get('max_similarity', -1) <= 1.0):
        errors.append("max_similarity must be in [0, 1]")
    
    if not (0.0 <= unit.get('preparation_confidence', -1) <= 1.0):
        errors.append("preparation_confidence must be in [0, 1]")
    
    if not (1 <= unit.get('recipe_count', 0)):
        errors.append("recipe_count must be >= 1")
    
    return errors
```

### Decision Validation
```python
def validate_decision(decision: dict) -> List[str]:
    errors = []
    
    if len(decision.get('rationale', '')) < 50:
        errors.append("Rationale must be at least 50 characters")
    
    if not (1 <= decision.get('confidence', 0) <= 5):
        errors.append("Confidence must be 1–5")
    
    valid_statuses = {'ACCEPTED', 'REVIEW_REQUIRED', 'REJECTED', 'UNMATCHED', 'AMBIGUOUS'}
    if decision.get('status') not in valid_statuses:
        errors.append(f"Invalid decision status: {decision.get('status')}")
    
    # Confidence constraints
    if decision.get('status') == 'ACCEPTED' and decision.get('confidence', 0) < 4:
        errors.append("ACCEPTED requires confidence >= 4")
    
    return errors
```

---

## 9. Export Formats

| Format | Use Case | Compression |
|--------|----------|-------------|
| Parquet | Primary storage, analytics | Snappy |
| CSV | Human review, interoperability | None |
| JSON | API, web UI | None |
| SQLite | Embedded review app | None |

---

## 10. Checksums

All output files include SHA-256 checksums in manifest:
```
manifest.json
{
  "files": {
    "review_units_v1.0_20261118.parquet": "sha256:...",
    "decisions_v1.0_20261118.parquet": "sha256:...",
    ...
  },
  "generated_at": "2026-11-18T...",
  "schema_version": "1.0"
}
```