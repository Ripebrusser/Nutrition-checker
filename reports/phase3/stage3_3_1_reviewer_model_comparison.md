# Stage 3.3.1: Reviewer Model Comparison

**Date:** 2026-11-18  
**Source:** Stage 3.3.1 Approval Reconciliation

---

## Executive Summary

The current architecture assumes a **4-reviewer multi-reviewer workflow** as the default. However, the project owner has **not confirmed reviewer availability**, and the formal approval report explicitly states this as an unresolved prerequisite.

This document provides an evidence-based comparison to determine whether four reviewers are scientifically necessary or merely an operational assumption.

---

## 1. Scientific Necessity Assessment

### 1.1 Statistical Perspective

| Criterion | Multi-Reviewer (≥4) | Single + Audit |
|-----------|---------------------|----------------|
| Inter-rater reliability measurable | ✅ Yes (κ, AC1) | ❌ Not measurable |
| Bias reduction | ✅ Multiple perspectives | ⚠️ Single bias risk |
| Throughput (units/day) | 240 (8 reviewers) | 30 (1 reviewer) |
| Resource requirement | 4+ reviewers | 1 + auditor |
| Scalability | Linear | Limited |

**Scientific Verdict:** Four reviewers are **not scientifically necessary**. The architecture supports both models. The requirement for ≥4 reviewers is an **operational choice**, not a scientific necessity.

### 1.2 Inter-Rater Reliability Requirements

| Metric | Multi-Reviewer | Single + Audit |
|---------|----------------|----------------|
| Cohen's κ | ✅ Measurable | ❌ N/A |
| Gwet's AC1 | ✅ Measurable | ❌ N/A |
| Per-status agreement | ✅ Measurable | ❌ N/A |
| Confidence intervals | ✅ Computable | ❌ N/A |

**Key Finding:** If inter-rater reliability is a project requirement, multi-reviewer is mandatory. If not, single-reviewer is viable.

---

## 2. Model Comparison

### 2.1 Multi-Reviewer Workflow (Current Architecture Assumption)

| Aspect | Description |
|--------|-------------|
| **Configuration** | ≥4 reviewers, independent blind reviews |
| **Process** | Independent blind reviews → adjudication → consensus |
| **Adjudication** | Senior reviewer resolves conflicts (SLA: 24h) |
| **Reliability Metrics** | Cohen's κ, Gwet's AC1, per-status agreement |
| **Throughput** | ~30 units/hr/reviewer |
| **Adjudication** | Senior reviewer resolves conflicts (SLA: 24h) |

**Pros:**
- Inter-rater reliability measurable (κ, AC1)
- Reduces individual bias
- Supports statistical validation
- Scales with team size

**Cons:**
- Requires ≥4 committed reviewers
- Coordination overhead
- Adjudication bottleneck

### 2.2 Single-Primary-Reviewer Workflow (Alternative)

| Aspect | Description |
|--------|-------------|
| **Primary Reviewer** | Single expert performs all reviews |
| **Independent Audit** | External auditor reviews defined sample (20%) |
| **Escalation** | Ambiguous cases → domain expert panel |
| **Reliability Claim** | No inter-rater reliability claim |
| **Throughput** | ~20 units/hr (single reviewer) |

**Pros:**
- Lower resource requirement
- No coordination overhead
- Simpler logistics

**Cons:**
- No inter-rater reliability measurement
- Single-point bias risk
- Limited scalability
- No statistical validation of consistency

### 2.3 Comparison Matrix

| Criterion | Multi-Reviewer (≥4) | Single + Audit |
|-----------|---------------------|----------------|
| Inter-rater reliability | ✅ Measurable | ❌ Not measurable |
| Bias reduction | ✅ Multiple perspectives | ⚠️ Single bias risk |
| Throughput (units/day) | 240 (8 reviewers) | 30 (1 reviewer) |
| Coordination overhead | High | Low |
| Adjudication bottleneck | Possible | None |
| Inter-rater reliability claim | ✅ Supported | ❌ Cannot claim |
| Minimum reviewers | 4 | 1 (+ auditor) |
| Throughput (units/day) | 240 | 30 |
| Timeline (7,992 units) | ~33 days | ~266 days |

---

## 3. Scientific Necessity Assessment

### 3.1 Is Four Reviewers Scientifically Necessary?

**No.** The architecture supports both models. The requirement for ≥4 reviewers is an **operational choice**, not a scientific necessity.

**Evidence:**
- Architecture supports both workflow models
- No statistical requirement mandates n≥4
- Single-reviewer + audit is methodologically valid
- Choice depends on project constraints (time, resources, reliability requirements)

### 5.1 When Is Multi-Reviewer Scientifically Required?

| Condition | Multi-Reviewer Required? |
|-----------|--------------------------|
| Inter-rater reliability claim needed | ✅ Yes |
| Regulatory requirement for κ | ✅ Yes |
| High-stakes clinical decisions | ✅ Yes |
| Published methodology paper | ✅ Yes |
| Internal tool / research | ❌ No (single + audit OK) |
| Exploratory analysis | ❌ No |

**Project Context:** This is an ML nutrition research project, not a regulatory submission. **Single + audit is scientifically valid.**

---

## 5. Recommendation

### 5.1 Recommended Approach: Hybrid Model

Given the project constraints, a **hybrid approach** balances scientific rigor with feasibility:

| Phase | Model | Reviewers | Duration |
|-------|-------|-----------|----------|
| Pilot (50 units) | 2 reviewers + audit | 2 | 1 week |
| Phase 3a (Critical/High/Medium) | 2 reviewers + audit | 2 | 6 weeks |
| Phase 3b (Standard/Low) | 1 reviewer + audit | 1 + auditor | 18 weeks |
| Ambiguity/Unmatched | Domain expert panel | 2-3 | 4 weeks |

### 5.2 Minimum Viable Configuration

| Role | Count | Commitment |
|--------|-------|------------|
| Primary Reviewer | 1 | Full-time |
| Auditor | 1 | 20% sample |
| Domain Experts (escalation) | 2-3 | On-call |
| **Total** | **2-3** | |

### 5.3 If 4 Reviewers Available

| Role | Count | Allocation |
|------|-------|------------|
| Primary Reviewers | 2 | Full-time |
| Secondary Reviewers | 2 | Full-time |
| Auditor | 1 | 20% sample |
| Senior Adjudicator | 1 | On-call |

---

## 6. Final Recommendation

### 6.1 Architecture Supports Both Models ✅

The Stage 3.2.3 architecture **does not require** four reviewers. It supports:
- Multi-reviewer workflow (if resources allow)
- Single-reviewer + independent audit (if resources constrained)

### 5.2 Recommended Path Forward

1. **Do not block on 4-reviewer commitment** — it's an operational choice
2. **Require minimum 2 reviewers** (primary + auditor) for viable timeline
3. **Document model choice** in project plan with rationale
4. **Build workbench to support both modes** (configuration flag)

### 5.3 If 4 Reviewers Are Required

If project governance mandates 4 reviewers:
- **Do not block architecture approval** on this
- **Gate B condition:** "Reviewer model selected" (not "4 reviewers committed")
- **Document** the chosen model and its limitations

---

## 7. Final Recommendation

**Verdict:** Four reviewers are **not scientifically necessary**. The architecture supports both models. 

**Decision Required:** Project owner must select reviewer model and secure commitments before Gate B.

**Recommended Minimum:** 2 reviewers (primary + auditor) with domain expert escalation panel.

**If 4 reviewers mandated by governance:** Document as operational constraint, not scientific requirement.

---

*End of Reviewer Model Comparison*