"""Candidate Generation - Multiple methods for generating IFCT match candidates."""

from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import re
import pandas as pd
import numpy as np
from difflib import SequenceMatcher
from rapidfuzz import fuzz, process
import logging

from .ingredient_taxonomy import MatchCategory, MatchStatus, classify_ingredient, taxonomy

logger = logging.getLogger(__name__)


class MatchMethod(Enum):
    """Candidate generation method."""
    EXACT = "EXACT"
    SYNONYM = "SYNONYM"
    TRANSLITERATION = "TRANSLITERATION"
    REGIONAL = "REGIONAL"
    TOKEN_EQUIVALENT = "TOKEN_EQUIVALENT"
    TOKEN_SIMILARITY = "TOKEN_SIMILARITY"
    FUZZY = "FUZZY"
    FOOD_GROUP_FILTER = "FOOD_GROUP_FILTER"


@dataclass
class Candidate:
    """Candidate match from IFCT."""
    ifct_food_code: str
    ifct_food_name: str
    ifct_food_group: str
    match_method: str
    similarity_score: float
    evidence: Dict[str, any] = field(default_factory=dict)
    food_group_compat: float = 0.0
    prep_state_compat: float = 0.0
    taxonomy_category: str = ""
    provisional_confidence: str = "LOW"
    requires_review: bool = True


class CandidateGenerator:
    """Generate IFCT match candidates for normalized ingredients."""

    def __init__(self, ifct_df: pd.DataFrame, synonym_dict: Dict, household_db: Dict):
        self.ifct_df = ifct_df
        self.synonym_dict = synonym_dict
        self.household_db = household_db
        
        # Build lookup structures
        self._build_lookup_structures()
        
        # Food group compatibility matrix
        self.food_group_compat = self._build_food_group_compat()
        
    def _build_lookup_structures(self):
        """Build lookup structures for fast candidate generation."""
        # Exact name lookup (canonically normalized food_name -> food_code)
        # Use the common name (before parentheses) for matching
        self.exact_lookup = {}
        for _, row in self.ifct_df.iterrows():
            food_name = row['food_name']
            # Extract common name (before parentheses)
            common_name = food_name.split('(')[0].strip()
            norm_name = self._normalize_canonical(common_name)
            if norm_name not in self.exact_lookup:
                self.exact_lookup[norm_name] = []
            self.exact_lookup[norm_name].append(row['food_code'])
            
            # Also add full normalized name as fallback
            full_norm = self._normalize_canonical(food_name)
            if full_norm not in self.exact_lookup:
                self.exact_lookup[full_norm] = []
            self.exact_lookup[full_norm].append(row['food_code'])
        
        # Synonym lookup (canonically normalized synonym -> canonical entries)
        self.synonym_lookup = {}
        for key, entry in self.synonym_dict.items():
            norm_key = self._normalize_canonical(key)
            if norm_key not in self.synonym_lookup:
                self.synonym_lookup[norm_key] = []
            self.synonym_lookup[norm_key].append(entry)
        
        # Token index for token-based similarity
        self.token_index = self._build_token_index()
        
        # Food code to food group mapping
        self.food_code_to_group = dict(zip(self.ifct_df['food_code'], self.ifct_df['food_group']))
        self.food_code_to_name = dict(zip(self.ifct_df['food_code'], self.ifct_df['food_name']))
        
        # Pre-compute IFCT row lookup for fast access
        self.ifct_lookup = {row['food_code']: row for _, row in self.ifct_df.iterrows()}
        
        # Pre-compute token sets for all IFCT foods
        self.ifct_token_sets = {}
        for food_code, row in self.ifct_lookup.items():
            norm_name = self._normalize_canonical(row['food_name'])
            self.ifct_token_sets[food_code] = set(self._tokenize(norm_name))
        
        # Food group compatibility matrix
        self.food_group_compat = self._build_food_group_compat()
        
        # Canonical name to IFCT food code mapping (manual overrides for known mismatches)
        self.canonical_to_ifct = self._build_canonical_to_ifct_mapping()
    
    def _build_canonical_to_ifct_mapping(self) -> Dict[str, str]:
        """Build mapping from synonym canonical names to IFCT food codes."""
        # This mapping resolves cases where canonical names don't match IFCT food names directly
        mapping = {
            # Pulses
            'pigeon pea': 'B021',  # Red gram, dal (Cajanus cajan)
            'chickpea (kabuli)': 'B022',  # Chickpea, whole - but IFCT has Rajmah
            'chickpea (desi)': 'B018',  # Rajmah, black (Phaseolus vulgaris) - closest
            'red lentil (split)': 'B013',  # Lentil dal (Lens culinaris)
            'red lentil (whole)': 'B014',  # Lentil whole, brown
            'sorghum': 'A005',  # Jowar
            'pearl millet': 'A003',  # Bajra
            'finger millet': 'A016',  # Ragi
            'foxtail millet': 'A016',  # Ragi (closest)
            'little millet': 'A016',  # Samai
            'barnyard millet': 'A016',  # Varagu
            'kodo millet': 'A016',  # Kodo
            'basmati rice': 'A015',  # Rice, raw, milled
            'sona masuri rice': 'A015',  # Rice, raw, milled
            'rice (raw)': 'A015',  # Rice, raw, milled
            'rice (cooked)': 'A015',  # Rice, raw, milled (IFCT has raw only)
            'rice (parboiled)': 'A014',  # Rice, parboiled, milled
            'wheat flour (whole)': 'A019',  # Wheat flour, atta
            'wheat flour (refined)': 'A018',  # Wheat flour, refined
            'semolina (coarse)': 'A022',  # Wheat, semolina
            'semolina (fine)': 'A022',  # Wheat, semolina
        }
        return mapping
    
    def _build_food_group_compat(self) -> Dict[Tuple[str, str], float]:
        """Build food group compatibility matrix."""
        groups = self.ifct_df['food_group'].unique()
        compat = {}
        for g1 in groups:
            for g2 in groups:
                if g1 == g2:
                    compat[(g1, g2)] = 1.0
                else:
                    # Related groups get partial compatibility
                    compat[(g1, g2)] = 0.3
        return compat
        
    def _normalize_canonical(self, text: str) -> str:
        """Normalize text for canonical comparison (EXACT matching).
        
        This is more aggressive than the tokenizer normalization:
        - Lowercase and strip
        - Remove parentheses content
        - Remove commas, hyphens, numbers, and other punctuation
        - Collapse whitespace
        """
        if not isinstance(text, str):
            return ""
        text = text.lower().strip()
        # Remove parentheses content
        text = re.sub(r'\([^)]*\)', '', text)
        # Remove punctuation: commas, hyphens, periods, numbers, etc.
        text = re.sub(r'[,\-.\d]', ' ', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def _normalize_tokenizer(self, text: str) -> str:
        """Normalize text for tokenization (less aggressive, keeps word boundaries)."""
        if not isinstance(text, str):
            return ""
        text = text.lower().strip()
        # Remove parentheses content
        text = re.sub(r'\([^)]*\)', '', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text
    
    def _build_token_index(self) -> Dict[str, Set[str]]:
        """Build inverted index: token -> set of food_codes."""
        token_index = {}
        for _, row in self.ifct_df.iterrows():
            food_code = row['food_code']
            norm_name = self._normalize_tokenizer(row['food_name'])
            tokens = self._tokenize(norm_name)
            for token in tokens:
                if token not in token_index:
                    token_index[token] = set()
                token_index[token].add(row['food_code'])
        return token_index

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize normalized text."""
        # Split on whitespace and punctuation, keep meaningful tokens
        tokens = re.findall(r'\b\w+\b', text.lower())
        # Filter out very short tokens and common stopwords
        stopwords = {'and', 'or', 'of', 'the', 'a', 'an', 'in', 'on', 'for', 'with', 'to', 'from', 'by', 'raw', 'fresh', 'dried', 'cooked', 'boiled', 'fried', 'roasted', 'steamed', 'baked', 'grilled', 'chopped', 'sliced', 'diced', 'minced', 'grated', 'ground', 'powder', 'powdered', 'fresh', 'dried', 'raw', 'cooked', 'boiled', 'fried', 'roasted', 'steamed', 'baked', 'grilled'}
        return [t for t in tokens if len(t) > 2 and t not in stopwords]

    def generate_candidates(self, normalized_ingredient: str, 
                          parsed_data: Dict,
                          ingredient_name: str,
                          source_field: str) -> List[Candidate]:
        """
        Generate all candidate matches for a normalized ingredient.
        
        Args:
            normalized_ingredient: Normalized ingredient text (parsed name)
            parsed_data: Parsed quantity/unit/prep info
            ingredient_name: Extracted ingredient name (without quantity/unit)
            source_field: 'ingredients_raw' or 'ingredients_en'
            
        Returns:
            List of Candidate objects
        """
        candidates = []
        seen_codes = set()
        
        # Method A: Exact canonical-name matches
        exact_cands = self._exact_match(normalized_ingredient)
        for c in exact_cands:
            if c.ifct_food_code not in seen_codes:
                candidates.append(c)
                seen_codes.add(c.ifct_food_code)
        
        # Method B: Verified synonym matches
        syn_cands = self._synonym_match(normalized_ingredient)
        for c in syn_cands:
            if c.ifct_food_code not in seen_codes:
                candidates.append(c)
                seen_codes.add(c.ifct_food_code)
        
        # Track if we have high-confidence exact or synonym matches
        has_high_confidence = len(exact_cands) > 0 or len(syn_cands) > 0
        
        # Method C: Transliteration matches (Hindi/Devanagari)
        trans_cands = self._transliteration_match(normalized_ingredient)
        for c in trans_cands:
            if c.ifct_food_code not in seen_codes:
                candidates.append(c)
                seen_codes.add(c.ifct_food_code)
        
        # Method D: Token-based similarity (Jaccard) - only if no high-confidence matches
        if not has_high_confidence:
            token_cands = self._token_similarity_match(normalized_ingredient)
            for c in token_cands:
                if c.ifct_food_code not in seen_codes:
                    candidates.append(c)
                    seen_codes.add(c.ifct_food_code)
        
        # Apply food group filter
        candidates = self._apply_food_group_filter(candidates, parsed_data)
        
        # Rank and assign provisional confidence (but don't set requires_review yet)
        candidates = self._rank_and_classify(candidates, parsed_data)
        
        # Apply central acceptance gate (handles prep state compatibility)
        candidates = self._apply_acceptance_gate(candidates, parsed_data)
        
        return candidates

    def _exact_match(self, normalized_ingredient: str) -> List[Candidate]:
        """Method A: Exact canonical-name matches."""
        candidates = []
        norm_ing = self._normalize_canonical(normalized_ingredient)
        
        if norm_ing in self.exact_lookup:
            for food_code in self.exact_lookup[norm_ing]:
                row = self.ifct_lookup[food_code]
                candidate = Candidate(
                    ifct_food_code=food_code,
                    ifct_food_name=row['food_name'],
                    ifct_food_group=row['food_group'],
                    match_method='EXACT',
                    similarity_score=1.0,
                    evidence={'match_type': 'exact_canonical_name'},
                    food_group_compat=1.0,
                    prep_state_compat=1.0,
                    taxonomy_category='EXACT_IDENTITY',
                    provisional_confidence='HIGH',
                    requires_review=None  # Will be set by acceptance gate
                )
                candidates.append(candidate)
        
        return candidates

    def _synonym_match(self, normalized_ingredient: str) -> List[Candidate]:
        """Method B: Verified synonym matches."""
        candidates = []
        norm_ing = self._normalize_canonical(normalized_ingredient)
        
        # Check exact synonym match
        if norm_ing in self.synonym_lookup:
            for entry in self.synonym_lookup[norm_ing]:
                canonical = entry['canonical_name']
                canon_norm = self._normalize_canonical(canonical)
                entry_confidence = entry.get('confidence', 0.95)
                
                # First try direct canonical-to-IFCT mapping
                food_code = None
                match_source = 'exact'
                match_score = 1.0
                
                if canonical in self.canonical_to_ifct:
                    food_code = self.canonical_to_ifct[canonical]
                    match_source = 'canonical_mapping'
                    match_score = entry_confidence
                elif canon_norm in self.exact_lookup:
                    # Exact match on canonical name
                    food_code = self.exact_lookup[canon_norm][0]
                    match_source = 'exact_canonical'
                    match_score = entry_confidence
                else:
                    # Find best token match for canonical name in IFCT
                    canon_tokens = set(self._tokenize(self._normalize_tokenizer(canonical)))
                    best_match = None
                    best_score = 0.0
                    
                    for fc, food_tokens in self.ifct_token_sets.items():
                        if not food_tokens:
                            continue
                        intersection = len(canon_tokens & food_tokens)
                        union = len(canon_tokens | food_tokens)
                        if union > 0:
                            jaccard = intersection / union
                            if jaccard > best_score and jaccard >= 0.4:
                                best_score = jaccard
                                best_match = fc
                    
                    if best_match:
                        food_code = best_match
                        match_source = 'token_match'
                        match_score = entry_confidence * best_score
                
                if food_code and food_code in self.ifct_lookup:
                    row = self.ifct_lookup[food_code]
                    # Scale confidence by match quality
                    if match_source == 'token_match':
                        scaled_conf = match_score
                    elif match_source in ['canonical_mapping', 'exact_canonical']:
                        scaled_conf = entry_confidence
                    else:
                        scaled_conf = entry_confidence
                    
                    # Determine review requirement: will be set by acceptance gate
                    # For now, set to None - acceptance gate will decide
                    candidate = Candidate(
                        ifct_food_code=food_code,
                        ifct_food_name=row['food_name'],
                        ifct_food_group=row['food_group'],
                        match_method='SYNONYM',
                        similarity_score=scaled_conf,
                        evidence={
                            'synonym': normalized_ingredient,
                            'canonical': entry['canonical_name'],
                            'confidence': entry_confidence,
                            'category': entry.get('category', ''),
                            'match_source': match_source,
                            'token_match_score': match_score if match_source == 'token_match' else None
                        },
                        food_group_compat=1.0 if match_source in ['canonical_mapping', 'exact_canonical'] else self._food_group_compat_score(row['food_group']),
                        prep_state_compat=1.0,
                        taxonomy_category='VERIFIED_SYNONYM',
                        provisional_confidence='HIGH' if scaled_conf >= 0.85 else 'MEDIUM',
                        requires_review=None  # Will be set by acceptance gate
                    )
                    candidates.append(candidate)
        
        return candidates

    def _transliteration_match(self, normalized_ingredient: str) -> List[Candidate]:
        """Method C: Verified Hindi-English transliteration matches."""
        candidates = []
        norm_ing = self._normalize_canonical(normalized_ingredient)
        
        # Check for Devanagari script
        if any('\u0900' <= c <= '\u097F' for c in normalized_ingredient):
            # Try to transliterate and match
            # This would use a transliteration library or mapping
            pass
        
        # Check for transliteration in synonym dict
        # (Hindi names already in synonym dict)
        return []

    def _token_similarity_match(self, normalized_ingredient: str) -> List[Candidate]:
        """Method D: Token-based similarity (Jaccard)."""
        candidates = []
        norm_ing = self._normalize_tokenizer(normalized_ingredient)
        tokens = self._tokenize(norm_ing)
        
        if not tokens:
            return []
        
        # Find candidate food codes via token index
        candidate_codes = set()
        for token in tokens:
            if token in self.token_index:
                candidate_codes.update(self.token_index[token])
        
        # Compute Jaccard similarity for each candidate using pre-computed token sets
        input_tokens = set(tokens)
        for food_code in candidate_codes:
            food_tokens = self.ifct_token_sets.get(food_code, set())
            
            # Jaccard similarity
            intersection = len(input_tokens & food_tokens)
            union = len(input_tokens | food_tokens)
            if union > 0:
                jaccard = intersection / union
                if jaccard >= 0.3:  # Minimum threshold
                    row = self.ifct_lookup[food_code]
                    
                    # Classify Jaccard=1.0 as TOKEN_EQUIVALENT, else TOKEN_SIMILARITY
                    if jaccard >= 1.0 - 1e-10:  # essentially 1.0
                        match_method = 'TOKEN_EQUIVALENT'
                        taxonomy_cat = 'TOKEN_EQUIVALENT'
                        # These are exact token-set matches but not canonical string matches
                        # They require review because token order, punctuation, or synonyms may differ
                        prov_conf = 'HIGH'
                        req_review = True
                    else:
                        match_method = 'TOKEN_SIMILARITY'
                        taxonomy_cat = 'TOKEN_SIMILARITY'
                        if jaccard >= 0.85:
                            prov_conf = 'HIGH'
                        elif jaccard >= 0.70:
                            prov_conf = 'MEDIUM'
                        else:
                            prov_conf = 'LOW'
                        req_review = True
                    
                    candidate = Candidate(
                        ifct_food_code=food_code,
                        ifct_food_name=row['food_name'],
                        ifct_food_group=row['food_group'],
                        match_method=match_method,
                        similarity_score=jaccard,
                        evidence={
                            'match_type': 'token_jaccard',
                            'input_tokens': list(input_tokens),
                            'matched_tokens': list(input_tokens & food_tokens),
                            'jaccard_score': jaccard
                        },
                        food_group_compat=self._food_group_compat_score(row['food_group']),
                        prep_state_compat=1.0,
                        taxonomy_category=taxonomy_cat,
                        provisional_confidence=prov_conf,
                        requires_review=None  # Will be set by acceptance gate
                    )
                    candidates.append(candidate)
        
        return candidates

    def _fuzzy_match(self, normalized_ingredient: str) -> List[Candidate]:
        """Method E: Fuzzy string matching using RapidFuzz."""
        candidates = []
        norm_ing = self._normalize_tokenizer(normalized_ingredient)
        
        # Use RapidFuzz for fuzzy matching
        # Limit to top 10 matches with score >= 70
        try:
            matches = process.extract(
                norm_ing, 
                {code: self._normalize_tokenizer(name) for code, name in zip(self.ifct_df['food_code'], self.ifct_df['food_name'])},
                scorer=fuzz.WRatio,
                limit=10,
                score_cutoff=70
            )
            
            for match_name, score, food_code in matches:
                if score >= 70:
                    row = self.ifct_lookup[food_code]
                    candidate = Candidate(
                        ifct_food_code=food_code,
                        ifct_food_name=row['food_name'],
                        ifct_food_group=row['food_group'],
                        match_method='FUZZY',
                        similarity_score=score / 100.0,
                        evidence={
                            'match_type': 'fuzzy_wratio',
                            'fuzz_score': score
                        },
                        food_group_compat=self._food_group_compat_score(row['food_group']),
                        prep_state_compat=1.0,
                        taxonomy_category='FUZZY',
                        provisional_confidence='LOW',
                        requires_review=None  # Will be set by acceptance gate
                    )
                    candidates.append(candidate)
        except Exception as e:
            logger.warning(f"Fuzzy matching failed: {e}")
        
        return candidates

    def _food_group_compat_score(self, food_group: str) -> float:
        """Compute food group compatibility score."""
        # This would use a pre-computed compatibility matrix
        # For now, return neutral score
        return 0.5

    def _apply_food_group_filter(self, candidates: List[Candidate], 
                                  parsed_data: Dict) -> List[Candidate]:
        """Filter or re-rank candidates by food group compatibility."""
        # For now, just return as-is with compat scores
        for c in candidates:
            c.food_group_compat = self._food_group_compat_score(c.ifct_food_group)
        return candidates

    def _apply_prep_state_compat(self, candidates: List[Candidate], 
                                  parsed_data: Dict) -> List[Candidate]:
        """Apply preparation state compatibility."""
        # Extract prep state from parsed data
        prep_desc = parsed_data.get('preparation')
        if prep_desc is None or (isinstance(prep_desc, float) and pd.isna(prep_desc)):
            prep_desc = ''
        prep_desc = str(prep_desc).lower()
        
        for c in candidates:
            # Simple heuristic: if ingredient name contains cooked/prep terms
            # and IFCT is raw, reduce compatibility
            ifct_food = c.ifct_food_name.lower()
            if any(word in c.ifct_food_name.lower() for word in ['raw', 'fresh']):
                c.prep_state_compat = 1.0
            elif any(w in c.ifct_food_name.lower() for w in ['cooked', 'boiled', 'fried', 'roasted']):
                c.prep_state_compat = 0.0
            else:
                c.prep_state_compat = 0.5  # neutral
        return candidates

    def _rank_and_classify(self, candidates: List[Candidate], 
                           parsed_data: Dict) -> List[Candidate]:
        """Rank candidates and assign provisional confidence.
        
        Note: requires_review is initially set to None and will be determined
        by the acceptance gate in _apply_acceptance_gate.
        """
        # Sort by similarity score descending
        candidates.sort(key=lambda c: c.similarity_score, reverse=True)
        
        # Assign provisional confidence based on match method and score
        for c in candidates:
            if c.match_method == 'EXACT':
                c.provisional_confidence = 'HIGH'
            elif c.match_method == 'SYNONYM':
                if c.similarity_score >= 0.95:
                    c.provisional_confidence = 'HIGH'
                else:
                    c.provisional_confidence = 'MEDIUM'
            elif c.match_method == 'TOKEN_EQUIVALENT':
                c.provisional_confidence = 'HIGH'
            elif c.match_method == 'TOKEN_SIMILARITY':
                if c.similarity_score >= 0.85:
                    c.provisional_confidence = 'HIGH'
                elif c.similarity_score >= 0.70:
                    c.provisional_confidence = 'MEDIUM'
                else:
                    c.provisional_confidence = 'LOW'
            elif c.match_method == 'FUZZY':
                if c.similarity_score >= 0.85:
                    c.provisional_confidence = 'MEDIUM'
                else:
                    c.provisional_confidence = 'LOW'
            else:
                c.provisional_confidence = 'LOW'
            
            # requires_review will be set by acceptance gate
            if c.requires_review is None:
                c.requires_review = True  # Default to review required
        
        return candidates

    def _apply_acceptance_gate(self, candidates: List[Candidate], parsed_data: Dict) -> List[Candidate]:
        """Apply central acceptance gate to determine auto-acceptance.
        
        Groups candidates by primary ingredient to check for multi-code ambiguity,
        then evaluates each candidate through the central acceptance gate.
        """
        # Group candidates by primary ingredient for multi-code check
        primary_ingredient = parsed_data.get('ingredient_name', '') or parsed_data.get('primary_ingredient', '')
        
        for c in candidates:
            # Evaluate through acceptance gate
            decision = self._evaluate_acceptance(c, parsed_data, candidates)
            
            c.requires_review = not decision['auto_accept']
            c.evidence['acceptance_decision'] = {
                'auto_accept': decision['auto_accept'],
                'reasons': decision['reasons'],
                'evidence': decision['evidence']
            }
            
            # Add acceptance reason to evidence
            if not decision['auto_accept']:
                c.evidence['rejection_reasons'] = decision['reasons']
        
        return candidates
    
    def _evaluate_acceptance(self, candidate, parsed_data: Dict, all_candidates: List) -> dict:
        """Evaluate a single candidate through the acceptance gate logic."""
        # This implements the core acceptance gate logic inline to avoid circular imports
        # The full logic is in acceptance_gate.py but we inline critical checks here
        
        reasons = []
        evidence = {}
        
        # 1. Check match method eligibility
        if candidate.match_method not in {'EXACT', 'SYNONYM'}:
            return {'auto_accept': False, 'reasons': ['INVALID_MATCH_METHOD'], 'evidence': {'match_method': candidate.match_method}}
        
        # 2. Check preparation state compatibility
        prep_state = parsed_data.get('disambiguated_preparation')
        prep_confidence = parsed_data.get('preparation_confidence', 0.0)
        
        # Handle string vs enum
        prep_state_str = str(prep_state) if prep_state else 'NOT_SPECIFIED'
        
        # Check preparation state compatibility
        if prep_state is None or prep_state == 'NOT_SPECIFIED' or str(prep_state) == 'NOT_SPECIFIED':
            # NOT_SPECIFIED - conservative: require explicit evidence
            if not self._has_compatibility_evidence(candidate):
                return {'auto_accept': False, 'reasons': ['NOT_SPECIFIED_NO_EVIDENCE'], 'evidence': {'prep_state': 'NOT_SPECIFIED'}}
        elif str(prep_state) == 'UNKNOWN':
            return {'auto_accept': False, 'reasons': ['UNKNOWN_PREP_STATE'], 'evidence': {'prep_state': 'UNKNOWN'}}
        else:
            # Check if prep state is compatible with raw-basis IFCT
            raw_compatible = {'RAW', 'FRESH'}
            incompatible = {'DRIED', 'POWDERED', 'GROUND', 'ROASTED', 'FRIED', 'BOILED', 
                           'COOKED', 'FERMENTED', 'PICKLED', 'SPROUTED', 'BLANCHED', 'MARINATED', 'SOAKED', 'GROUND'}

            prep_state_upper = str(prep_state).upper()
            if prep_state_upper in incompatible:
                return {'auto_accept': False, 'reasons': ['NON_RAW_PREP_STATE'], 
                        'evidence': {'prep_state': str(prep_state), 'incompatible': True}}

            # Explicitly allow only RAW and FRESH
            if prep_state_upper not in raw_compatible:
                # NOT_SPECIFIED, UNKNOWN, SOAKED, GROUND, etc. are not auto-accepted
                return {'auto_accept': False, 'reasons': ['NON_RAW_PREP_STATE'], 
                        'evidence': {'prep_state': str(prep_state), 'incompatible': True, 'allowed': list(raw_compatible)}}
        # 3. Check prep_state_compat threshold
        if candidate.prep_state_compat < 0.8:
            return {'auto_accept': False, 'reasons': ['PREP_COMPAT_BELOW_THRESHOLD'], 
                    'evidence': {'prep_state_compat': candidate.prep_state_compat, 'threshold': 0.8}}
        
        # 4. Check multi-code ambiguity (same primary ingredient -> multiple IFCT codes)
        # Check if this primary ingredient maps to multiple IFCT codes in auto-accept set
        # We'll check this after all candidates are evaluated
        
        # 5. Check provenance
        required_fields = ['ifct_food_code', 'ifct_food_name', 'ifct_food_group', 
                          'match_method', 'similarity_score', 'evidence']
        for field in ['ifct_food_code', 'ifct_food_name', 'ifct_food_group', 'match_method', 'similarity_score']:
            if not hasattr(candidate, field) or getattr(candidate, field) is None:
                return {'auto_accept': False, 'reasons': ['MISSING_PROVENANCE'], 
                        'evidence': {'missing_field': field}}
        
        evidence = getattr(candidate, 'evidence', None)
        if not evidence or (isinstance(evidence, dict) and len(evidence) == 0):
            return {'auto_accept': False, 'reasons': ['MISSING_PROVENANCE'], 
                    'evidence': {'missing_field': 'evidence'}}
        
        # 6. Method-specific checks
        if candidate.match_method == 'TOKEN_EQUIVALENT':
            return {'auto_accept': False, 'reasons': ['TOKEN_EQUIVALENT'], 'evidence': {}}
        elif candidate.match_method == 'TOKEN_SIMILARITY':
            return {'auto_accept': False, 'reasons': ['TOKEN_SIMILARITY'], 'evidence': {}}
        elif candidate.match_method == 'FUZZY':
            return {'auto_accept': False, 'reasons': ['FUZZY'], 'evidence': {}}
        elif candidate.match_method == 'SYNONYM':
            evidence = getattr(candidate, 'evidence', {})
            match_source = evidence.get('match_source', '')
            if match_source == 'token_match':
                return {'auto_accept': False, 'reasons': ['SYNONYM_TOKEN_MATCH'], 'evidence': {}}
            if evidence.get('confidence', 1.0) < 0.95:
                return {'auto_accept': False, 'reasons': ['SYNONYM_LOW_CONFIDENCE'], 'evidence': {}}
        
        # Check for NOT_SPECIFIED without evidence
        prep_state = parsed_data.get('disambiguated_preparation')
        if (prep_state is None or 
            str(prep_state) == 'NOT_SPECIFIED' or
            (hasattr(prep_state, 'value') and prep_state.value == 'NOT_SPECIFIED')):
            if not self._has_compatibility_evidence(candidate):
                return {'auto_accept': False, 'reasons': ['NOT_SPECIFIED_NO_EVIDENCE'], 
                        'evidence': {'prep_state': 'NOT_SPECIFIED'}}
        
        # If we reach here, candidate passes all checks
        return {'auto_accept': True, 'reasons': [], 'evidence': {}}
    
    def _has_compatibility_evidence(self, candidate) -> bool:
        """Check if candidate has explicit compatibility evidence for NOT_SPECIFIED."""
        evidence = getattr(candidate, 'evidence', {})
        if not evidence:
            return False
        
        compat_keys = ['prep_state_compat', 'ifct_is_raw', 'prep_state_warning']
        for key in compat_keys:
            if key in evidence:
                return True
        
        # Check if IFCT food name indicates raw/fresh
        ifct_name = getattr(candidate, 'ifct_food_name', '').lower()
        if any(w in ifct_name for w in ['raw', 'fresh']):
            return True
        
        return False

def create_candidate_generator(ifct_path: str,
                                 synonym_path: str,
                                 household_path: str) -> CandidateGenerator:
    """Factory function to create candidate generator."""
    ifct_df = pd.read_parquet(ifct_path)
    synonym_df = pd.read_csv(synonym_path)
    household_df = pd.read_csv(household_path)
    
    # Build synonym dict
    synonym_dict = {}
    for _, row in pd.read_csv(synonym_path).iterrows():
        key = row['synonym_key'] if 'synonym_key' in row else row['synonym']
        entry = {
            'canonical_name': row['canonical_name'],
            'synonym': row['synonym'],
            'category': row['category'],
            'confidence': row.get('confidence', 0.95),
            'excludes': str(row.get('excludes', '')).split(';') if pd.notna(row.get('excludes', '')) else []
        }
        synonym_dict[key.lower().strip()] = entry
    
    # Build household DB
    household_db = {}
    for _, row in pd.read_csv(household_path).iterrows():
        key = (row['ingredient_name'].lower().strip(), row['household_unit'].lower().strip())
        if key not in household_db or row['confidence'] > household_db[key]['confidence']:
            household_db[key] = {
                'mass_g': row['equivalent_mass_g'],
                'source': row['source'],
                'confidence': row['confidence']
            }
    
    return CandidateGenerator(
        ifct_df=pd.read_parquet(ifct_path),
        synonym_dict=synonym_dict,
        household_db=household_db
    )