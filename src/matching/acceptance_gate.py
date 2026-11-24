"""Central Acceptance Gate for Stage 2.3 - Enforces safety criteria for auto-acceptance."""

from dataclasses import dataclass
from typing import List, Dict, Optional, Set
from enum import Enum
import logging

from .name_disambiguation import PreparationState

logger = logging.getLogger(__name__)


class RejectionReason(Enum):
    """Reasons for requiring manual review."""
    NON_RAW_PREP_STATE = "NON_RAW_PREP_STATE"
    PREP_STATE_CONFLICT = "PREP_STATE_CONFLICT"
    PREP_COMPAT_BELOW_THRESHOLD = "PREP_COMPAT_BELOW_THRESHOLD"
    MULTIPLE_IFCT_CODES = "MULTIPLE_IFCT_CODES"
    MISSING_PROVENANCE = "MISSING_PROVENANCE"
    PREPARATION_CONFLICT = "PREPARATION_CONFLICT"
    UNKNOWN_PREP_STATE = "UNKNOWN_PREP_STATE"
    NOT_SPECIFIED_NO_EVIDENCE = "NOT_SPECIFIED_NO_EVIDENCE"
    MISSING_COMPATIBILITY_EVIDENCE = "MISSING_COMPATIBILITY_EVIDENCE"
    TOKEN_EQUIVALENT = "TOKEN_EQUIVALENT"
    TOKEN_SIMILARITY = "TOKEN_SIMILARITY"
    FUZZY = "FUZZY"
    SYNONYM_LOW_CONFIDENCE = "SYNONYM_LOW_CONFIDENCE"
    SYNONYM_TOKEN_MATCH = "SYNONYM_TOKEN_MATCH"


@dataclass
class AcceptanceDecision:
    """Result of acceptance gate evaluation."""
    auto_accept: bool
    reasons: List[RejectionReason]
    evidence: Dict
    
    def to_dict(self) -> dict:
        return {
            'auto_accept': self.auto_accept,
            'reasons': [r.value for r in self.reasons],
            'evidence': self.evidence
        }


class AcceptanceGate:
    """Central acceptance gate for candidate auto-acceptance."""
    
    # Preparation states that are compatible with IFCT raw basis
    RAW_COMPATIBLE_STATES = {PreparationState.RAW, PreparationState.FRESH}
    
    # Preparation states that are explicitly incompatible with raw-basis IFCT
    INCOMPATIBLE_STATES = {
        PreparationState.DRIED, PreparationState.POWDERED, PreparationState.GROUND,
        PreparationState.ROASTED, PreparationState.FRIED, PreparationState.BOILED,
        PreparationState.COOKED, PreparationState.FERMENTED, PreparationState.PICKLED,
        PreparationState.SPROUTED, PreparationState.BLANCHED, PreparationState.FRIED,
        PreparationState.PICKLED, PreparationState.MARINATED
    }
    
    # States that are debatable/unknown
    AMBIGUOUS_STATES = {
        PreparationState.SOAKED, PreparationState.UNKNOWN, PreparationState.NOT_SPECIFIED
    }
    
    MIN_PREP_COMPAT_THRESHOLD = 0.8
    
    def __init__(self):
        self.stats = {
            'total_evaluated': 0,
            'auto_accepted': 0,
            'rejected': 0,
            'rejection_reasons': {}
        }
    
    def evaluate(self, 
                 candidate,
                 parsed_data: Dict,
                 all_candidates_for_ingredient: List) -> AcceptanceDecision:
        """
        Evaluate whether a candidate should be auto-accepted.
        
        Args:
            candidate: The candidate to evaluate
            parsed_data: Parsed ingredient data including preparation state
            all_candidates_for_ingredient: All candidates for this ingredient (for multi-code check)
            
        Returns:
            AcceptanceDecision with auto_accept boolean and reasons
        """
        self.stats['total_evaluated'] += 1
        reasons = []
        evidence = {}
        
        # 1. Check if candidate has valid match method for auto-accept
        if not self._has_valid_match_method(candidate):
            reasons.append(RejectionReason.MISSING_COMPATIBILITY_EVIDENCE)
            evidence['match_method'] = candidate.match_method
        
        # 2. Check preparation state compatibility
        prep_result = self._check_preparation_compatibility(candidate, parsed_data)
        if not prep_result['compatible']:
            reasons.extend(prep_result['reasons'])
            evidence.update(prep_result['evidence'])
        
        # 3. Check preparation state conflict
        conflict_result = self._check_preparation_conflict(candidate, parsed_data)
        if conflict_result['has_conflict']:
            reasons.append(RejectionReason.PREPARATION_CONFLICT)
            evidence['conflict_details'] = conflict_result['details']
        
        # 4. Check prep_state_compat threshold
        if candidate.prep_state_compat < self.MIN_PREP_COMPAT_THRESHOLD:
            reasons.append(RejectionReason.PREP_COMPAT_BELOW_THRESHOLD)
            evidence['prep_state_compat'] = candidate.prep_state_compat
            evidence['threshold'] = self.MIN_PREP_COMPAT_THRESHOLD
        
        # 5. Check multi-code ambiguity
        if self._has_multi_code_ambiguity(candidate, all_candidates_for_ingredient):
            reasons.append(RejectionReason.MULTIPLE_IFCT_CODES)
            evidence['competing_codes'] = self._get_competing_codes(
                candidate, all_candidates_for_ingredient)
        
        # 6. Check provenance
        if not self._has_sufficient_provenance(candidate):
            reasons.append(RejectionReason.MISSING_PROVENANCE)
            evidence['missing_fields'] = self._get_missing_provenance_fields(candidate)
        
        # 7. Check for NOT_SPECIFIED without evidence
        prep_state = parsed_data.get('disambiguated_preparation')
        if (prep_state is None or 
            prep_state == 'NOT_SPECIFIED' or 
            prep_state == 'NOT_SPECIFIED' or
            (hasattr(prep_state, 'value') and prep_state.value == 'NOT_SPECIFIED')):
            # NOT_SPECIFIED requires explicit compatibility evidence
            if not self._has_compatibility_evidence(candidate):
                reasons.append(RejectionReason.NOT_SPECIFIED_NO_EVIDENCE)
                evidence['prep_state'] = 'NOT_SPECIFIED'
        
        # 8. Check for UNKNOWN prep state
        if prep_state and (
            prep_state == 'UNKNOWN' or 
            prep_state == 'UNKNOWN' or
            (hasattr(prep_state, 'value') and prep_state.value == 'UNKNOWN')):
            reasons.append(RejectionReason.UNKNOWN_PREP_STATE)
            evidence['prep_state'] = 'UNKNOWN'
        
        # 9. Method-specific rejections
        method_reason = self._get_method_specific_reason(candidate)
        if method_reason:
            reasons.append(method_reason)
        
        # Final decision
        auto_accept = len(reasons) == 0
        
        if auto_accept:
            self.stats['auto_accepted'] += 1
        else:
            self.stats['rejected'] += 1
            for r in reasons:
                self.stats['rejection_reasons'][r.value] = self.stats['rejection_reasons'].get(r.value, 0) + 1
        
        evidence['candidate_ifct_code'] = candidate.ifct_food_code
        evidence['match_method'] = candidate.match_method
        evidence['prep_state_compat'] = candidate.prep_state_compat
        
        return AcceptanceDecision(auto_accept=auto_accept, reasons=reasons, evidence=evidence)
    
    def _has_valid_match_method(self, candidate) -> bool:
        """Check if match method is eligible for auto-accept."""
        return candidate.match_method in {'EXACT', 'SYNONYM'}
    
    def _check_preparation_compatibility(self, candidate, parsed_data: Dict) -> dict:
        """Check if candidate's preparation state is compatible with IFCT raw basis."""
        prep_state = parsed_data.get('disambiguated_preparation')
        prep_confidence = parsed_data.get('preparation_confidence', 0.0)
        
        reasons = []
        evidence = {'prep_state': str(prep_state), 'prep_confidence': prep_confidence}
        
        if prep_state is None or prep_state == 'NOT_SPECIFIED':
            # NOT_SPECIFIED - conservative: require explicit evidence
            return {
                'compatible': False,
                'reasons': [RejectionReason.NOT_SPECIFIED_NO_EVIDENCE],
                'evidence': evidence
            }
        
        if prep_state == 'UNKNOWN':
            return {
                'compatible': False,
                'reasons': [RejectionReason.UNKNOWN_PREP_STATE],
                'evidence': evidence
            }
        
        # Convert string to enum if needed
        if isinstance(prep_state, str):
            try:
                prep_state_enum = PreparationState(prep_state)
            except ValueError:
                return {
                    'compatible': False,
                    'reasons': [RejectionReason.UNKNOWN_PREP_STATE],
                    'evidence': {**evidence, 'error': 'invalid_prep_state'}
                }
        else:
            prep_state_enum = prep_state
        
        # Check if prep state is compatible with raw-basis IFCT
        if prep_state_enum in self.RAW_COMPATIBLE_STATES:
            # RAW or FRESH - compatible with raw-basis IFCT
            return {'compatible': True, 'reasons': [], 'evidence': evidence}
        
        if prep_state_enum in self.INCOMPATIBLE_STATES:
            # Explicitly incompatible with raw-basis IFCT
            return {
                'compatible': False,
                'reasons': [RejectionReason.NON_RAW_PREP_STATE],
                'evidence': {**evidence, 'incompatible_state': prep_state_enum.value}
            }
        
        if prep_state_enum in self.AMBIGUOUS_STATES:
            # SOAKED, NOT_SPECIFIED, UNKNOWN - require evidence
            return {
                'compatible': False,
                'reasons': [RejectionReason.NOT_SPECIFIED_NO_EVIDENCE],
                'evidence': evidence
            }
        
        return {
            'compatible': False,
            'reasons': [RejectionReason.UNKNOWN_PREP_STATE],
            'evidence': evidence
        }
    
    def _check_preparation_conflict(self, candidate, parsed_data: Dict) -> dict:
        """Check for conflicting preparation states."""
        ambiguity_flags = parsed_data.get('ambiguity_flags', [])
        if isinstance(ambiguity_flags, str):
            try:
                import ast
                ambiguity_flags = ast.literal_eval(ambiguity_flags)
            except:
                ambiguity_flags = []
        
        has_conflict = 'CONFLICTING_PREPARATION' in str(ambiguity_flags)
        
        if has_conflict:
            return {
                'has_conflict': True,
                'details': 'CONFLICTING_PREPARATION flag detected'
            }
        
        return {'has_conflict': False, 'details': None}
    
    def _has_multi_code_ambiguity(self, candidate, all_candidates: List) -> bool:
        """Check if source ingredient maps to multiple IFCT codes."""
        if not all_candidates:
            return False
        
        # Group by primary ingredient (source)
        primary_ingredient = getattr(candidate, 'primary_ingredient', None)
        if not primary_ingredient:
            return False
        
        # Count unique IFCT codes for this primary ingredient
        codes = set()
        for c in all_candidates:
            if getattr(c, 'primary_ingredient', None) == primary_ingredient:
                codes.add(c.ifct_food_code)
        
        return len(codes) > 1
    
    def _get_competing_codes(self, candidate, all_candidates: List) -> List[str]:
        """Get list of competing IFCT codes for the same primary ingredient."""
        primary_ingredient = getattr(candidate, 'primary_ingredient', None)
        if not primary_ingredient:
            return []
        
        codes = set()
        for c in all_candidates:
            if getattr(c, 'primary_ingredient', None) == primary_ingredient:
                codes.add(c.ifct_food_code)
        
        return sorted(codes)
    
    def _has_sufficient_provenance(self, candidate) -> bool:
        """Check if candidate has sufficient provenance information."""
        required_fields = ['ifct_food_code', 'ifct_food_name', 'ifct_food_group', 
                          'match_method', 'similarity_score', 'evidence']
        
        for field in required_fields:
            if not hasattr(candidate, field) or getattr(candidate, field) is None:
                return False
        
        # Evidence must be non-empty dict
        evidence = getattr(candidate, 'evidence', None)
        if not evidence or (isinstance(evidence, dict) and len(evidence) == 0):
            return False
        
        return True
    
    def _get_missing_provenance_fields(self, candidate) -> List[str]:
        """Get list of missing provenance fields."""
        required_fields = ['ifct_food_code', 'ifct_food_name', 'ifct_food_group', 
                          'match_method', 'similarity_score', 'evidence']
        missing = []
        for field in required_fields:
            if not hasattr(candidate, field) or getattr(candidate, field) is None:
                missing.append(field)
        evidence = getattr(candidate, 'evidence', None)
        if not evidence or (isinstance(evidence, dict) and len(evidence) == 0):
            missing.append('evidence (empty)')
        return missing
    
    def _has_compatibility_evidence(self, candidate) -> bool:
        """Check if candidate has explicit compatibility evidence for NOT_SPECIFIED."""
        evidence = getattr(candidate, 'evidence', {})
        if not evidence:
            return False
        
        # Check for explicit compatibility indicators
        compat_keys = ['prep_state_compat', 'ifct_is_raw', 'prep_state_warning']
        for key in compat_keys:
            if key in evidence:
                return True
        
        # Check if IFCT food name indicates raw/fresh
        ifct_name = getattr(candidate, 'ifct_food_name', '').lower()
        if any(w in ifct_name for w in ['raw', 'fresh']):
            return True
        
        return False
    
    def _get_method_specific_reason(self, candidate) -> Optional[RejectionReason]:
        """Get method-specific rejection reason."""
        method = candidate.match_method
        
        if method == 'TOKEN_EQUIVALENT':
            return RejectionReason.TOKEN_EQUIVALENT
        elif method == 'TOKEN_SIMILARITY':
            return RejectionReason.TOKEN_SIMILARITY
        elif method == 'FUZZY':
            return RejectionReason.FUZZY
        elif method == 'SYNONYM':
            # Check if synonym match was via token fallback
            evidence = getattr(candidate, 'evidence', {})
            match_source = evidence.get('match_source', '')
            if match_source == 'token_match':
                return RejectionReason.SYNONYM_TOKEN_MATCH
            if evidence.get('confidence', 1.0) < 0.95:
                return RejectionReason.SYNONYM_LOW_CONFIDENCE
        
        return None
    
    def get_stats(self) -> dict:
        return self.stats.copy()


# Global acceptance gate instance
acceptance_gate = AcceptanceGate()


def evaluate_candidate_acceptance(candidate, parsed_data: Dict, all_candidates: List = None) -> dict:
    """Convenience function to evaluate candidate acceptance."""
    if all_candidates is None:
        all_candidates = [candidate]
    decision = acceptance_gate.evaluate(candidate, parsed_data, all_candidates)
    return decision.to_dict()