# Stage 3: Quality Assurance Plan

## Overview

Quality assurance framework for Stage 3 manual mapping verification. Ensures accuracy, consistency, and traceability of verified mappings.

---

## 1. Quality Objectives

| Objective | Metric | Target |
|-----------|--------|--------|
| **Accuracy** | False acceptance rate | < 1% |
| **Consistency** | Inter-reviewer agreement (Cohen's κ) | ≥ 0.85 |
| **Completeness** | Review coverage | 100% of review units |
| **Traceability** | Provenance linkage | 100% |
| **Timeliness** | Review throughput | ≥ 30 units/hour/reviewer |
| **Auditability** | Decision log completeness | 100% |

---

## 2. Quality Gates

### Gate 1: Review Unit Generation (Automated)
- [ ] 100% of Stage 2.3 candidate pairs → review units
- [ ] 7,165 review units generated
- [ ] Schema validation passes
- [ ] Priority scores computed correctly
- [ ] Checksums match manifest

### Gate 2: Reviewer Calibration (Per Reviewer)
- [ ] Complete 5-unit calibration exercise
- [ ] 100% accuracy on calibration set
- [ ] Protocol acknowledgment signed

### Gate 3: In-Session Quality (Real-time)
- [ ] Minimum 60s evidence review per unit
- [ ] Rationale ≥ 50 characters
- [ ] Confidence 1–5 recorded
- [ ] No forced AMBIGUOUS decisions
- [ ] Break compliance (10min/hr, 30min/4hr)

### Gate 4: Post-Session (Automated)
- [ ] All locks released
- [ ] Session log complete
- [ ] Decision log append-only verified
- [ ] No orphan decisions

### Gate 5: Post-Review Audit (Automated + Manual)
- [ ] Stratified sample drawn (fixed seed)
- [ ] Second review completed
- [ ] Agreement measured
- [ ] Disagreements resolved
- [ ] Final dataset exported with checksums

---

## 3. Sampling Strategy

### Stratified Random Sampling

| Stratum | Population | Rate | Method |
|---------|------------|------|--------|
| ACCEPTED (EXACT) | ~46 | 20% | Stratified random |
| ACCEPTED (SYNONYM) | ~0 | 20% | All if any |
| REVIEW_REQUIRED (TOKEN_EQUIVALENT) | ~149 | 10% | Stratified random |
| REVIEW_REQUIRED (TOKEN_SIMILARITY) | ~6,949 | 10% | Stratified random |
| REVIEW_REQUIRED (SYNONYM) | ~21 | 10% | Stratified random |
| REVIEW_REQUIRED (EXACT) | ~46 | 10% | Stratified random |
| REJECTED | ~0 | 5% | All if any |
| AMBIGUOUS | ~0 | 100% | All |
| UNMATCHED | ~0 | 5% | All if any |

**Sampling Implementation:**
```python
def draw_audit_sample(review_units: pd.DataFrame, decisions: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    
    # Merge decisions with review units
    merged = review_units.merge(decisions, on='review_unit_id', how='inner')
    
    samples = []
    for stratum_name, (rate, min_n) in STRATA_CONFIG.items():
        stratum = merged[merged['status'] == stratum_name]
        n = max(int(len(stratum) * rate), min_n)
        n = min(n, len(stratum))
        if n > 0:
            sample = stratum.sample(n=n, random_state=seed)
            samples.append(sample)
    
    return pd.concat(samples, ignore_index=True)
```

**Fixed seed:** `42` (documented, reproducible)

---

## 4. Second Review Process

### Procedure
1. **Sample drawn** → audit sample table populated
2. **Second reviewer assigned** → different from first reviewer
3. **Blind review** → second reviewer sees evidence panel only (not first decision)
4. **Decision recorded** → second decision logged
5. **Agreement computed** → status match = agreement

### Agreement Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| **Raw Agreement** | (Agreements) / (Total) | ≥ 90% |
| **Cohen's κ** | κ = (Po − Pe) / (1 − Pe) | ≥ 0.85 |
| **Per-Status κ** | κ per status | ≥ 0.80 each |

**Disagreement Resolution:**
- If status differs → CONFLICT
- Auto-escalate to senior reviewer
- Senior reviewer makes final decision with documented rationale
- Resolution recorded in `audit_samples.resolution_timestamp`

---

## 5. Quality Metrics Dashboard

### Real-Time Metrics (Per Session)
| Metric | Threshold | Action if Breached |
|--------|-----------|-------------------|
| Units/hour | ≥ 30 | Reviewer coaching |
| Evidence time | ≥ 60s | Alert reviewer |
| Rationale length | ≥ 50 chars | Block submission |
| Break compliance | 100% | Auto-lock session |

### Daily Metrics
| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Review throughput | ≥ 200 units/day | < 150 |
| Inter-reviewer κ | ≥ 0.85 | < 0.80 |
| False acceptance rate | < 1% | > 0.5% |
| Decision reversal rate | < 5% | > 10% |

### Cumulative Metrics
| Metric | Target | Reporting |
|--------|--------|-----------|
| Total units reviewed | 7,165 | Daily |
| False acceptance rate | < 1% | Weekly |
| Inter-reviewer agreement | ≥ 0.85 | Weekly |
| Audit coverage | Per stratum targets | Per stratum |
| Decision log completeness | 100% | Real-time |

---

## 6. Error Detection & Correction

### Automated Checks (Real-time)
| Check | Frequency | Action |
|-------|-----------|--------|
| Duplicate review_unit_id | Per batch | Block |
| Missing required fields | Per decision | Block |
| Rationale < 50 chars | Per decision | Block |
| Confidence out of range | Per decision | Block |
| Status transition invalid | Per decision | Block |
| Lock TTL exceeded | Continuous | Auto-release |

### Batch Checks (Post-Session)
| Check | Method | Resolution |
|-------|--------|------------|
| Orphan decisions | SQL query | Link or delete |
| Unreleased locks | Lock table | Force-release |
| Orphan provenance | Join check | Repair/flag |
| Checksum mismatch | Manifest verify | Regenerate |

### Audit Checks (Weekly)
| Check | Method | Threshold |
|-------|--------|-----------|
| Inter-reviewer agreement | κ calculation | κ < 0.80 → investigate |
| False acceptance audit | Manual re-review | > 1% → halt |
| Decision reversal rate | Status change log | > 5% → investigate |
| Rationale quality | NLP + manual | < 80% meaningful → coach |

---

## 7. Issue Management

### Issue Classification
| Severity | Definition | SLA |
|----------|------------|-----|
| **Critical** | Data loss, safety issue, systematic error | 1 hour |
| **High** | Reviewer blocked, data inconsistency | 4 hours |
| **Medium** | Minor bug, usability issue | 1 day |
| **Low** | Cosmetic, enhancement | 1 week |

### Issue Workflow
1. **Report** → GitHub issue / internal tracker
2. **Triage** → Severity assigned, owner assigned
3. **Fix** → Code/config change
4. **Verify** → Regression test
4. **Deploy** → Hotfix or next release
5. **Close** → Confirm resolution

---

## 8. Documentation & Reporting

### Required Reports
| Report | Frequency | Audience |
|--------|-----------|----------|
| Session summary | Per session | Reviewer, Lead |
| Daily quality report | Daily | QA Lead, Project Lead |
| Weekly QA summary | Weekly | Project Lead, Stakeholders |
| Audit results | Per audit cycle | QA Lead, Project Lead |
| Final QA sign-off | End of Stage 3 | All stakeholders |

### Report Templates

**Daily Quality Report:**
```markdown
# Daily QA Report - YYYY-MM-DD

## Session Summary
- Sessions: N
- Reviewers: N
- Units reviewed: N
- Throughput: N units/hr

## Quality Metrics
- Inter-reviewer κ: X.XX
- Avg evidence time: XXs
- Avg rationale length: XX chars
- Break compliance: XX%

## Issues
- Critical: N
- High: N
- Medium: N

## Decisions
- ACCEPTED: N
- REVIEW_REQUIRED: N
- REJECTED: N
- UNMATCHED: N
- AMBIGUOUS: N

## Actions
- [ ] Action items...
```

**Final QA Sign-Off Report:**
```markdown
# Stage 3 QA Sign-Off

## Summary
- Total review units: 7,165
- Units reviewed: 7,165 (100%)
- Reviewers: N
- Total review hours: N

## Quality Metrics
- Inter-reviewer agreement (κ): X.XX
- Raw agreement: XX%
- False acceptance rate: X.XX%
- Decision reversal rate: X.XX%

## Audit Results
- Samples audited: N
- Agreements: N
- Disagreements: N (resolved: N)
- Escalations: N

## Known Limitations
1. ...
2. ...

## Sign-Off
- QA Lead: _______________ Date: _______
- Project Lead: ___________ Date: _______
- Technical Lead: _________ Date: _______
```

---

## 9. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Reviewer fatigue | High | Medium | Mandatory breaks, 4hr max |
| Low inter-reviewer agreement | Medium | High | Calibration, senior escalation |
| Systematic bias | Medium | High | Blind second review, diverse reviewers |
| Data loss | Low | Critical | Append-only logs, daily backup |
| Protocol drift | Medium | Medium | Calibration refresh weekly |
| Reviewer unavailability | Medium | Medium | Cross-training, buffer capacity |
| Protocol ambiguity | Low | High | Clear protocol, examples, calibration |

---

## 10. Sign-Off Criteria

### Stage 3 QA Complete When:
- [ ] 100% review units have decisions
- [ ] Audit sampling complete per strata
- [ ] Inter-reviewer κ ≥ 0.85
- [ ] False acceptance rate < 1%
- [ ] All disagreements resolved
- [ ] All locks released
- [ ] Decision log 100% complete
- [ ] Provenance links 100% intact
- [ ] Checksums verified
- [ ] Final dataset exported with manifest
- [ ] QA sign-off report signed by QA Lead & Project Lead

---

## 11. Appendix: Audit Sample Size Calculation

For 95% CI ± 5% on agreement rate:
```
n = (Z² × p × (1−p)) / E²
n = (1.96² × 0.9 × 0.1) / 0.05² ≈ 139
```

With stratification and finite population correction, total audit samples ≈ 200–250.

---

## 12. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-18 | QA Lead | Initial plan |

---

*End of Quality Assurance Plan*