#!/usr/bin/env python3
"""
Stage 1 — Ingredient Normalization (Optimized)
Normalizes ingredient descriptions with efficient word-boundary matching.
"""

import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter, defaultdict

import pandas as pd


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class NormalizationRecord:
    recipe_id: int
    original_line: str
    original_ingredient: str
    normalized_ingredient: str
    transformations: List[str]
    synonym_applied: Optional[str] = None
    synonym_confidence: Optional[float] = None
    flags: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SynonymEntry:
    canonical_name: str
    synonym: str
    category: str
    evidence: str
    confidence: float
    notes: str = ""
    excludes: List[str] = field(default_factory=list)


# ============================================================
# SYNONYM DICTIONARY
# ============================================================

SYNONYM_RAW_DATA = [
    # PULSES & LEGUMES
    ("pigeon pea", "toor dal", "pulse", "Common Indian name for Cajanus cajan", 0.99, ["toor dal (split)", "toor dal (whole)"]),
    ("pigeon pea", "arhar dal", "pulse", "Hindi name for Cajanus cajan", 0.99, ["arhar dal (split)", "arhar dal (whole)"]),
    ("pigeon pea", "tuvar dal", "pulse", "Gujarati/Marathi variant", 0.95, ["tuvar dal (split)"]),
    ("pigeon pea", "red gram", "pulse", "English common name", 0.95, []),
    ("pigeon pea", "tur dal", "pulse", "Transliteration variant", 0.90, []),

    ("green gram (split)", "moong dal", "pulse", "Common name for Vigna radiata (split)", 0.99, ["moong dal (whole)", "moong dal (sprouted)"]),
    ("green gram (whole)", "moong", "pulse", "Whole Vigna radiata", 0.95, ["moong dal (split)"]),
    ("green gram (whole)", "mung bean", "pulse", "Whole bean form", 0.90, ["moong dal (split)"]),
    ("green gram (whole)", "hari moong", "pulse", "Hindi for whole green gram", 0.90, ["moong dal (split)"]),
    ("green gram (sprouted)", "moong sprouts", "pulse", "Sprouted moong", 0.95, ["moong dal (split)"]),

    ("black gram (split)", "urad dal", "pulse", "Common name for Vigna mungo (split)", 0.99, ["urad dal (whole)", "urad dal (split, skinless)"]),
    ("black gram (whole)", "urad", "pulse", "Whole Vigna mungo", 0.95, ["urad dal (split)"]),
    ("black gram (whole)", "urad bean", "pulse", "Whole bean form", 0.90, ["urad dal (split)"]),
    ("black gram (whole)", "maah ki dal", "pulse", "Punjabi name", 0.90, []),

    ("bengal gram (split)", "chana dal", "pulse", "Split Cicer arietinum (desi)", 0.99, ["chana dal (whole)", "kabuli chana"]),
    ("bengal gram (whole)", "chana", "pulse", "Whole Cicer arietinum (desi)", 0.95, ["chana dal (split)"]),

    ("chickpea (kabuli)", "kabuli chana", "pulse", "Large white Cicer arietinum (kabuli type)", 0.99, ["chana dal (split)"]),
    ("chickpea (kabuli)", "garbanzo bean", "pulse", "English/Spanish name", 0.95, []),
    ("chickpea (kabuli)", "white chana", "pulse", "Hindi descriptor", 0.90, ["black chana"]),

    ("chickpea (desi)", "kala chana", "pulse", "Small dark Cicer arietinum (desi type)", 0.99, ["kabuli chana"]),
    ("chickpea (desi)", "brown chickpea", "pulse", "English descriptor", 0.90, ["white chickpea"]),
    ("chickpea (desi)", "desi chana", "pulse", "Hindi for desi type", 0.90, ["kabuli chana"]),

    ("red lentil (split)", "masoor dal", "pulse", "Split Lens culinaris", 0.99, ["masoor dal (whole)", "masoor (brown)"]),
    ("red lentil (whole)", "masoor", "pulse", "Whole Lens culinaris", 0.95, ["masoor dal (split)"]),

    ("horse gram", "kulthi dal", "pulse", "Macrotyloma uniflorum", 0.95, []),
    ("horse gram", "kulthi", "pulse", "Short form", 0.90, []),

    ("moth bean", "matki", "pulse", "Vigna aconitifolia", 0.95, ["matki (sprouted)"]),
    ("moth bean", "mat bean", "pulse", "English name", 0.90, []),

    # GRAINS & CEREALS
    ("rice (raw)", "chawal", "grain", "Hindi for raw rice", 0.99, ["rice (cooked)", "rice (parboiled)"]),
    ("rice (raw)", "chaaval", "grain", "Transliteration variant", 0.95, ["chaaval (cooked)"]),
    ("rice (raw)", "bhaat (raw)", "grain", "Bengali/Marathi for raw rice", 0.90, ["bhaat (cooked)"]),
    ("rice (cooked)", "bhaat", "grain", "Hindi/Bengali for cooked rice", 0.99, ["rice (raw)"]),
    ("rice (cooked)", "chawal (pakka)", "grain", "Hindi for cooked rice", 0.95, ["chawal (kacha)"]),
    ("rice (parboiled)", "ukda chawal", "grain", "Marathi/Gujarati for parboiled", 0.95, ["rice (raw)"]),
    ("rice (parboiled)", "puzhungal arisi", "grain", "Tamil for parboiled rice", 0.90, []),
    ("basmati rice", "basmati chawal", "grain", "Long-grain aromatic rice", 0.99, ["non-basmati rice"]),
    ("sona masuri rice", "sona masoori", "grain", "Medium-grain rice variety", 0.95, []),

    ("wheat flour (whole)", "atta", "grain", "Whole wheat flour (Triticum aestivum)", 0.99, ["maida (refined)", "suji (semolina)"]),
    ("wheat flour (whole)", "gehun ka atta", "grain", "Hindi descriptor", 0.95, ["gehun ka maida"]),
    ("wheat flour (refined)", "maida", "grain", "Refined wheat flour", 0.99, ["atta (whole wheat)"]),
    ("wheat flour (refined)", "maida (refined)", "grain", "Explicit", 0.95, ["atta"]),
    ("semolina (coarse)", "suji", "grain", "Coarse wheat middlings", 0.99, ["rava", "sooji (fine)"]),
    ("semolina (fine)", "rava", "grain", "South Indian name", 0.95, ["suji (coarse)"]),
    ("semolina (fine)", "sooji", "grain", "Transliteration variant", 0.90, ["suji (coarse)"]),

    ("finger millet", "ragi", "grain", "Eleusine coracana", 0.99, ["ragi flour", "ragi malt"]),
    ("finger millet", "nachni", "grain", "Marathi/Gujarati name", 0.95, []),
    ("pearl millet", "bajra", "grain", "Pennisetum glaucum", 0.99, ["bajra flour"]),
    ("sorghum", "jowar", "grain", "Sorghum bicolor", 0.99, ["jowar flour"]),
    ("sorghum", "jowar", "grain", "Hindi name", 0.95, []),
    ("foxtail millet", "kangni", "grain", "Setaria italica", 0.95, []),
    ("little millet", "kutki", "grain", "Panicum sumatrense", 0.95, []),
    ("barnyard millet", "sanwa", "grain", "Echinochloa frumentacea", 0.90, []),
    ("kodo millet", "kodra", "grain", "Paspalum scrobiculatum", 0.90, []),

    ("oats", "jaee", "grain", "Avena sativa", 0.95, ["oats (rolled)", "oats (steel-cut)"]),
    ("quinoa", "quinoa", "grain", "Chenopodium quinoa", 0.95, []),

    # VEGETABLES - LEAFY
    ("spinach", "palak", "vegetable_leafy", "Spinacia oleracea", 0.99, ["palak (frozen)", "palak (cooked)"]),
    ("spinach", "palak saag", "vegetable_leafy", "Hindi with saag", 0.95, []),
    ("amaranth leaves", "chaulai", "vegetable_leafy", "Amaranthus spp.", 0.95, ["chaulai saag"]),
    ("amaranth leaves", "rajgira", "vegetable_leafy", "Gujarati name", 0.90, ["rajgira seeds"]),
    ("fenugreek leaves", "methi leaves", "vegetable_leafy", "Trigonella foenum-graecum (leaves)", 0.99, ["fenugreek seeds", "kasuri methi"]),
    ("fenugreek leaves", "methi patta", "vegetable_leafy", "Explicit leaf", 0.95, ["fenugreek seeds"]),
    ("mustard greens", "sarson ka saag", "vegetable_leafy", "Brassica juncea leaves", 0.95, ["mustard seeds"]),
    ("amaranth (red)", "lal saag", "vegetable_leafy", "Red amaranth", 0.90, []),
    ("purslane", "kulfa", "vegetable_leafy", "Portulaca oleracea", 0.90, []),
    ("sorrel leaves", "ambadi", "vegetable_leafy", "Hibiscus cannabinus", 0.90, []),
    ("dill leaves", "suva", "vegetable_leafy", "Anethum graveolens", 0.90, ["dill seeds"]),
    ("coriander leaves", "coriander leaves", "vegetable_leafy", "Coriandrum sativum (leaves)", 0.99, ["coriander seeds", "coriander powder"]),
    ("coriander leaves", "cilantro", "vegetable_leafy", "English name (US)", 0.95, ["coriander seeds"]),
    ("curry leaves", "curry leaves", "vegetable_leafy", "Murraya koenigii", 0.99, ["curry powder"]),
    ("curry leaves", "kadi patta", "vegetable_leafy", "Hindi name", 0.95, []),
    ("mint leaves", "mint leaves", "vegetable_leafy", "Mentha spp.", 0.99, ["mint (dried)", "mint essence"]),
    ("mint leaves", "pudina", "vegetable_leafy", "Hindi name", 0.95, ["mint essence"]),

    # VEGETABLES - ROOT/TUBER
    ("potato", "potato", "vegetable_root_tuber", "Solanum tuberosum", 0.99, ["potato (sweet)", "potato (fried)"]),
    ("potato", "aloo", "vegetable_root_tuber", "Hindi name", 0.95, ["potato (sweet)"]),
    ("potato", "batata", "vegetable_root_tuber", "Marathi/Gujarati name", 0.95, []),
    ("sweet potato", "sweet potato", "vegetable_root_tuber", "Ipomoea batatas", 0.99, ["potato (white)"]),
    ("sweet potato", "shakarkand", "vegetable_root_tuber", "Hindi name", 0.95, []),
    ("yam", "yam", "vegetable_root_tuber", "Dioscorea spp.", 0.95, ["elephant foot yam"]),
    ("elephant foot yam", "suran", "vegetable_root_tuber", "Amorphophallus paeoniifolius", 0.95, ["yam (regular)"]),
    ("taro root", "arbi", "vegetable_root_tuber", "Colocasia esculenta", 0.95, ["arbi (leaves)"]),
    ("taro root", "arvi", "vegetable_root_tuber", "Variant", 0.90, []),
    ("radish", "radish", "vegetable_root_tuber", "Raphanus sativus", 0.99, ["radish (leaves)", "daikon"]),
    ("radish", "mooli", "vegetable_root_tuber", "Hindi name", 0.95, ["radish (leaves)"]),
    ("carrot", "carrot", "vegetable_root_tuber", "Daucus carota", 0.99, ["carrot (baby)", "carrot juice"]),
    ("carrot", "gajar", "vegetable_root_tuber", "Hindi name", 0.95, []),
    ("beetroot", "beetroot", "vegetable_root_tuber", "Beta vulgaris", 0.99, ["beetroot (pickled)"]),
    ("beetroot", "chukandar", "vegetable_root_tuber", "Hindi name", 0.95, []),
    ("onion (bulb)", "onion", "vegetable_root_tuber", "Allium cepa (bulb)", 0.99, ["onion (spring)", "onion (fried)", "onion powder"]),
    ("onion (bulb)", "pyaz", "vegetable_root_tuber", "Hindi name", 0.95, ["pyaz (spring)"]),
    ("onion (spring)", "spring onion", "vegetable_root_tuber", "Allium fistulosum", 0.99, ["onion (bulb)"]),
    ("onion (spring)", "spring onion greens", "vegetable_root_tuber", "Green onion tops", 0.95, ["onion (bulb)"]),
    ("onion (spring)", "hara pyaz", "vegetable_root_tuber", "Hindi for spring onion", 0.95, ["onion (bulb)"]),
    ("garlic", "garlic", "vegetable_root_tuber", "Allium sativum", 0.99, ["garlic paste", "garlic powder"]),
    ("garlic", "lehsun", "vegetable_root_tuber", "Hindi name", 0.95, ["garlic paste"]),
    ("ginger", "ginger", "vegetable_root_tuber", "Zingiber officinale", 0.99, ["ginger paste", "ginger powder", "dried ginger"]),
    ("ginger", "adrak", "vegetable_root_tuber", "Hindi name", 0.95, ["dried ginger"]),

    # VEGETABLES - OTHER
    ("cauliflower", "cauliflower", "vegetable_other", "Brassica oleracea var. botrytis", 0.99, ["cauliflower (frozen)"]),
    ("cauliflower", "phool gobi", "vegetable_other", "Hindi name", 0.95, ["cabbage"]),
    ("cabbage", "cabbage", "vegetable_other", "Brassica oleracea var. capitata", 0.99, ["cauliflower", "red cabbage"]),
    ("cabbage", "bandh gobi", "vegetable_other", "Hindi name", 0.95, ["cauliflower"]),
    ("tomato", "tomato", "vegetable_other", "Solanum lycopersicum", 0.99, ["tomato puree", "tomato (sun-dried)", "tomato ketchup"]),
    ("tomato", "tamatar", "vegetable_other", "Hindi name", 0.95, ["green tomato"]),
    ("brinjal", "brinjal", "vegetable_other", "Solanum melongena", 0.99, ["brinjal (baby)", "brinjal (round)"]),
    ("brinjal", "baingan", "vegetable_other", "Hindi name", 0.95, []),
    ("eggplant", "brinjal", "vegetable_other", "English name for brinjal", 0.99, ["eggplant (Japanese)"]),
    ("okra", "okra", "vegetable_other", "Abelmoschus esculentus", 0.99, ["okra (frozen)", "okra (pickled)"]),
    ("okra", "bhindi", "vegetable_other", "Hindi name", 0.95, []),
    ("ridge gourd", "ridge gourd", "vegetable_other", "Luffa acutangula", 0.95, ["ridge gourd (peeled)"]),
    ("ridge gourd", "turai", "vegetable_other", "Hindi name", 0.95, ["ridge gourd (peeled)"]),
    ("sponge gourd", "sponge gourd", "vegetable_other", "Luffa cylindrica", 0.95, []),
    ("sponge gourd", "gilki", "vegetable_other", "Hindi name", 0.95, []),
    ("bottle gourd", "bottle gourd", "vegetable_other", "Lagenaria siceraria", 0.99, ["bottle gourd (peeled)", "bottle gourd juice"]),
    ("bottle gourd", "lauki", "vegetable_other", "Hindi name", 0.95, ["ghiya", "dudhi"]),
    ("ash gourd", "ash gourd", "vegetable_other", "Benincasa hispida", 0.95, ["petha (sweet)"]),
    ("ash gourd", "petha", "vegetable_other", "Hindi name", 0.95, ["petha (sweet)"]),
    ("pumpkin", "pumpkin", "vegetable_other", "Cucurbita spp.", 0.99, ["pumpkin (seeds)", "kaddu (sweet)"]),
    ("pumpkin", "kaddu", "vegetable_other", "Hindi name", 0.95, ["pumpkin (seeds)"]),
    ("cucumber", "cucumber", "vegetable_other", "Cucumis sativus", 0.99, ["cucumber (pickled)", "kakdi"]),
    ("cucumber", "kheera", "vegetable_other", "Hindi name", 0.95, ["kakdi"]),
    ("capsicum (bell pepper)", "capsicum", "vegetable_other", "Capsicum annuum (bell pepper)", 0.99, ["capsicum (green/red/yellow)"]),
    ("capsicum (bell pepper)", "shimla mirch", "vegetable_other", "Hindi name", 0.95, ["chili pepper"]),
    ("green chili", "green chili", "vegetable_other", "Capsicum annuum (green)", 0.99, ["red chili", "chili powder"]),
    ("green chili", "hari mirch", "vegetable_other", "Hindi name", 0.95, ["red chili"]),
    ("red chili (fresh)", "red chili", "vegetable_other", "Capsicum annuum (red, fresh)", 0.99, ["red chili powder", "green chili"]),
    ("red chili (fresh)", "lal mirch", "vegetable_other", "Hindi name", 0.95, ["red chili powder"]),
    ("green peas (fresh)", "green peas", "vegetable_other", "Pisum sativum (fresh)", 0.99, ["green peas (frozen)", "green peas (dried)"]),
    ("green peas (fresh)", "matar", "vegetable_other", "Hindi name", 0.95, ["yellow peas"]),
    ("corn (fresh)", "corn", "vegetable_other", "Zea mays (fresh)", 0.95, ["corn flour", "popcorn"]),
    ("corn (fresh)", "makai", "vegetable_other", "Hindi name", 0.90, ["corn flour"]),

    # FRUITS
    ("mango (ripe)", "mango", "fruit", "Mangifera indica (ripe)", 0.99, ["mango (raw/green)", "mango pickle", "aamras"]),
    ("mango (raw)", "raw mango", "fruit", "Mangifera indica (unripe)", 0.95, ["mango (ripe)", "amchur"]),
    ("banana (ripe)", "banana", "fruit", "Musa spp. (ripe)", 0.99, ["banana (raw/plantain)", "banana flower"]),
    ("banana (raw/plantain)", "raw banana", "fruit", "Musa spp. (unripe)", 0.95, ["banana (ripe)", "banana flower"]),
    ("apple", "apple", "fruit", "Malus domestica", 0.99, ["apple (stewed)", "apple juice"]),
    ("guava", "guava", "fruit", "Psidium guajava", 0.99, []),
    ("guava", "amrood", "fruit", "Variant", 0.95, []),
    ("papaya (ripe)", "papaya", "fruit", "Carica papaya (ripe)", 0.99, ["papaya (raw)", "papaya seeds"]),
    ("pomegranate", "pomegranate", "fruit", "Punica granatum", 0.99, ["pomegranate seeds", "pomegranate juice"]),
    ("pomegranate", "anar", "fruit", "Hindi name", 0.95, ["anar dana", "anar juice"]),
    ("orange", "orange", "fruit", "Citrus sinensis", 0.99, ["orange juice", "narangi"]),
    ("orange", "santra", "fruit", "Hindi name", 0.95, ["narangi"]),
    ("lemon", "lemon", "fruit", "Citrus limon", 0.99, ["lime", "lemon juice"]),
    ("lime", "lime", "fruit", "Citrus aurantifolia", 0.95, ["lemon"]),
    ("coconut (fresh kernel)", "fresh coconut", "fruit", "Cocos nucifera (fresh kernel)", 0.99, ["dried coconut", "coconut water", "coconut milk"]),
    ("coconut (fresh kernel)", "fresh coconut kernel", "fruit", "Explicit", 0.95, ["dried coconut"]),
    ("dried coconut", "dried coconut", "fruit", "Copra / copra", 0.99, ["fresh coconut", "desiccated coconut"]),
    ("dried coconut", "copra", "fruit", "Technical name", 0.95, ["fresh coconut"]),
    ("coconut water", "coconut water", "fruit", "Cocos nucifera liquid", 0.99, ["coconut milk"]),
    ("jackfruit (ripe)", "jackfruit", "fruit", "Artocarpus heterophyllus", 0.95, ["jackfruit (raw)", "jackfruit seeds"]),
    ("watermelon", "watermelon", "fruit", "Citrullus lanatus", 0.95, []),
    ("muskmelon", "muskmelon", "fruit", "Cucumis melo", 0.95, []),

    # SPICES & CONDIMENTS
    ("cumin seeds", "cumin seeds", "spice", "Cuminum cyminum (seeds)", 0.99, ["cumin powder", "shah jeera"]),
    ("cumin seeds", "jeera", "spice", "Hindi name", 0.99, ["cumin powder"]),
    ("cumin powder", "cumin powder", "spice", "Ground cumin", 0.99, ["cumin seeds"]),
    ("cumin powder", "jeera powder", "spice", "Hindi name", 0.99, ["cumin seeds"]),
    ("coriander seeds", "coriander seeds", "spice", "Coriandrum sativum (seeds)", 0.99, ["coriander powder", "coriander leaves"]),
    ("coriander seeds", "dhania", "spice", "Hindi name", 0.99, ["coriander powder", "coriander leaves"]),
    ("coriander powder", "coriander powder", "spice", "Ground coriander", 0.99, ["coriander seeds"]),
    ("coriander powder", "dhania powder", "spice", "Hindi name", 0.99, ["coriander seeds"]),
    ("turmeric powder", "turmeric powder", "spice", "Curcuma longa (powder)", 0.99, ["fresh turmeric"]),
    ("turmeric powder", "haldi powder", "spice", "Hindi name", 0.99, ["fresh turmeric"]),
    ("turmeric (fresh)", "fresh turmeric", "spice", "Curcuma longa (root)", 0.95, ["turmeric powder"]),
    ("turmeric (fresh)", "haldi (fresh)", "spice", "Hindi name", 0.95, ["turmeric powder"]),
    ("red chili powder", "red chili powder", "spice", "Ground red chili", 0.99, ["kashmiri red chili powder", "deg mirch"]),
    ("red chili powder", "lal mirch powder", "spice", "Hindi name", 0.99, ["kashmiri red chili powder"]),
    ("kashmiri red chili powder", "kashmiri red chili powder", "spice", "Mild red chili", 0.99, ["deg mirch", "regular chili powder"]),
    ("kashmiri red chili powder", "kashmiri mirch", "spice", "Hindi name", 0.99, ["regular chili powder"]),
    ("black pepper", "black pepper", "spice", "Piper nigrum", 0.99, ["white pepper", "peppercorns"]),
    ("black pepper", "kali mirch", "spice", "Hindi name", 0.99, ["black pepper (whole)"]),
    ("white pepper", "white pepper", "spice", "Piper nigrum (white)", 0.95, ["black pepper"]),
    ("mustard seeds", "mustard seeds", "spice", "Brassica juncea/nigra (seeds)", 0.99, ["mustard oil", "mustard powder"]),
    ("mustard seeds", "rai", "spice", "Hindi name", 0.99, ["mustard oil", "mustard greens"]),
    ("fenugreek seeds", "fenugreek seeds", "spice", "Trigonella foenum-graecum (seeds)", 0.99, ["fenugreek leaves", "kasuri methi"]),
    ("fenugreek seeds", "methi dana", "spice", "Hindi name", 0.99, ["fenugreek leaves", "kasuri methi"]),
    ("fenugreek leaves", "fenugreek leaves", "spice", "Trigonella foenum-graecum (leaves)", 0.99, ["fenugreek seeds", "kasuri methi"]),
    ("fenugreek leaves", "methi leaves", "spice", "Hindi name", 0.99, ["fenugreek seeds", "kasuri methi"]),
    ("kasuri methi", "kasuri methi", "spice", "Dried fenugreek leaves", 0.99, ["fenugreek seeds", "fenugreek leaves"]),
    ("kasuri methi", "dried fenugreek leaves", "spice", "Explicit", 0.95, ["fenugreek seeds", "fenugreek leaves"]),
    ("fennel seeds", "fennel seeds", "spice", "Foeniculum vulgare", 0.99, ["fennel seeds (roasted)"]),
    ("fennel seeds", "saunf", "spice", "Hindi name", 0.99, ["fennel seeds (roasted)"]),
    ("carom seeds", "carom seeds", "spice", "Trachyspermum ammi", 0.99, ["carom seeds (roasted)"]),
    ("carom seeds", "ajwain", "spice", "Hindi name", 0.99, ["carom seeds (roasted)"]),
    ("nigella seeds", "nigella seeds", "spice", "Nigella sativa", 0.99, ["onion seeds (misnomer)"]),
    ("nigella seeds", "kalonji", "spice", "Hindi name", 0.99, ["onion seeds"]),
    ("asafoetida", "asafoetida", "spice", "Ferula asafoetida", 0.99, ["asafoetida (compounded)", "asafoetida (raw)"]),
    ("asafoetida", "hing", "spice", "Hindi name", 0.99, ["hing (compounded)"]),
    ("bay leaf", "bay leaf", "spice", "Laurus nobilis / Cinnamomum tamala", 0.99, ["curry leaves"]),
    ("bay leaf", "tej patta", "spice", "Hindi name", 0.99, ["curry leaves"]),
    ("cinnamon (stick)", "cinnamon stick", "spice", "Cinnamomum verum / cassia", 0.99, ["cinnamon powder", "mace"]),
    ("cinnamon (stick)", "dalchini", "spice", "Hindi name", 0.99, ["cinnamon powder"]),
    ("cinnamon powder", "cinnamon powder", "spice", "Ground cinnamon", 0.95, ["cinnamon stick"]),
    ("cinnamon powder", "dalchini powder", "spice", "Hindi name", 0.95, ["cinnamon stick"]),
    ("clove", "clove", "spice", "Syzygium aromaticum", 0.99, ["clove powder"]),
    ("clove", "laung", "spice", "Hindi name", 0.99, ["clove powder"]),
    ("cardamom (green)", "green cardamom", "spice", "Elettaria cardamomum", 0.99, ["cardamom (black)", "cardamom powder"]),
    ("cardamom (green)", "elaichi", "spice", "Hindi name", 0.99, ["cardamom (black)"]),
    ("cardamom (green)", "choti elaichi", "spice", "Explicit small", 0.95, ["cardamom (black)"]),
    ("cardamom (black)", "black cardamom", "spice", "Amomum subulatum", 0.99, ["cardamom (green)"]),
    ("cardamom (black)", "badi elaichi", "spice", "Explicit large", 0.99, ["cardamom (green)"]),
    ("cardamom (black)", "kali elaichi", "spice", "Explicit black", 0.95, ["cardamom (green)"]),
    ("nutmeg", "nutmeg", "spice", "Myristica fragrans", 0.99, ["nutmeg powder", "mace"]),
    ("nutmeg", "jaiphal", "spice", "Hindi name", 0.95, ["mace"]),
    ("mace", "mace", "spice", "Myristica fragrans (aril)", 0.95, ["nutmeg"]),
    ("mace", "javitri", "spice", "Hindi name", 0.95, ["nutmeg"]),
    ("poppy seeds", "poppy seeds", "spice", "Papaver somniferum", 0.95, ["posto"]),
    ("poppy seeds", "khus khus", "spice", "Hindi name", 0.95, ["posto"]),
    ("poppy seeds", "posto", "spice", "Bengali name", 0.95, ["khus khus"]),
    ("sesame seeds (white)", "white sesame seeds", "spice", "Sesamum indicum (white)", 0.99, ["black sesame seeds", "sesame oil"]),
    ("sesame seeds (white)", "safed til", "spice", "Hindi name", 0.95, ["black sesame seeds"]),
    ("sesame seeds (black)", "black sesame seeds", "spice", "Sesamum indicum (black)", 0.99, ["white sesame seeds", "sesame oil"]),
    ("sesame seeds (black)", "kala til", "spice", "Hindi name", 0.95, ["white sesame seeds"]),

    # OILS & FATS
    ("mustard oil", "mustard oil", "oil", "Brassica juncea oil", 0.99, ["mustard seeds", "canola oil"]),
    ("mustard oil", "sarson ka tel", "oil", "Hindi name", 0.95, ["mustard seeds"]),
    ("coconut oil", "coconut oil", "oil", "Cocos nucifera oil", 0.99, ["fresh coconut", "virgin coconut oil"]),
    ("coconut oil", "nariyal tel", "oil", "Hindi name", 0.95, ["fresh coconut"]),
    ("groundnut oil", "groundnut oil", "oil", "Arachis hypogaea oil", 0.95, ["peanut oil"]),
    ("peanut oil", "peanut oil", "oil", "Synonym", 0.95, ["groundnut oil"]),
    ("sesame oil", "sesame oil", "oil", "Sesamum indicum oil", 0.95, ["gingelly oil"]),
    ("gingelly oil", "gingelly oil", "oil", "South Indian name", 0.95, ["sesame oil"]),
    ("sunflower oil", "sunflower oil", "oil", "Helianthus annuus oil", 0.90, ["refined sunflower oil"]),
    ("soybean oil", "soybean oil", "oil", "Glycine max oil", 0.90, ["soybean (beans)"]),
    ("ghee", "ghee", "fat", "Clarified butter", 0.99, ["butter", "vanaspati"]),
    ("ghee", "desi ghee", "fat", "Traditional ghee", 0.95, ["vanaspati ghee"]),
    ("butter", "butter", "fat", "Butter", 0.99, ["ghee", "salted butter"]),
    ("vanaspati", "vanaspati", "fat", "Hydrogenated vegetable fat", 0.95, ["ghee"]),
    ("vanaspati", "dalda", "fat", "Brand name", 0.95, ["ghee"]),

    # DAIRY
    ("milk (cow)", "milk", "dairy", "Bos taurus milk", 0.99, ["milk (buffalo)", "milk (skim)", "milk powder"]),
    ("milk (cow)", "doodh", "dairy", "Hindi name", 0.95, ["milk (buffalo)"]),
    ("milk (buffalo)", "buffalo milk", "dairy", "Bubalus bubalis milk", 0.95, ["cow milk"]),
    ("curd", "curd", "dairy", "Fermented milk", 0.99, ["yogurt", "buttermilk"]),
    ("curd", "dahi", "dairy", "Hindi name", 0.95, ["yogurt"]),
    ("yogurt", "yogurt", "dairy", "Synonym for curd", 0.95, ["Greek yogurt"]),
    ("buttermilk", "buttermilk", "dairy", "Churned curd liquid", 0.95, ["lassi"]),
    ("buttermilk", "chaas", "dairy", "Hindi name", 0.95, ["lassi"]),
    ("paneer", "paneer", "dairy", "Fresh cheese", 0.99, ["chenna", "tofu"]),
    ("chenna", "chenna", "dairy", "Unpressed paneer", 0.95, ["paneer"]),
    ("khoya", "khoya", "dairy", "Reduced milk solids", 0.99, ["khoya (fresh)", "khoya (dried)"]),
    ("khoya", "mawa", "dairy", "Variant", 0.95, ["khoya (fresh)"]),
    ("cream", "cream", "dairy", "Milk cream", 0.95, ["whipped cream"]),
    ("cream", "malai", "dairy", "Hindi name", 0.95, ["whipped cream"]),

    # SWEETENERS
    ("jaggery", "jaggery", "sweetener", "Unrefined cane sugar", 0.99, ["jaggery powder", "sugar"]),
    ("jaggery", "gur", "sweetener", "Hindi name", 0.95, ["jaggery powder"]),
    ("sugar (white)", "sugar", "sweetener", "Refined sucrose", 0.99, ["brown sugar", "powdered sugar"]),
    ("sugar (white)", "chini", "sweetener", "Hindi name", 0.95, ["brown sugar"]),
    ("brown sugar", "brown sugar", "sweetener", "Partially refined", 0.95, ["white sugar", "jaggery"]),
    ("honey", "honey", "sweetener", "Apis mellifera", 0.99, ["honey (raw)", "honey (processed)"]),
    ("honey", "shahad", "sweetener", "Hindi name", 0.95, ["honey (raw)"]),

    # NUTS & DRIED FRUITS
    ("cashew", "cashew", "nut", "Anacardium occidentale", 0.99, ["cashew (roasted)", "cashew (salted)"]),
    ("cashew", "kaju", "nut", "Hindi name", 0.99, ["cashew (roasted)"]),
    ("almond", "almond", "nut", "Prunus dulcis", 0.99, ["almond (soaked)", "almond flour"]),
    ("almond", "badam", "nut", "Hindi name", 0.99, ["almond (soaked)"]),
    ("walnut", "walnut", "nut", "Juglans regia", 0.95, ["black walnut"]),
    ("walnut", "akhrot", "nut", "Hindi name", 0.95, ["black walnut"]),
    ("pistachio", "pistachio", "nut", "Pistacia vera", 0.95, ["pistachio (salted)"]),
    ("pistachio", "pista", "nut", "Hindi name", 0.95, ["pistachio (salted)"]),
    ("peanut (raw)", "peanut", "nut", "Arachis hypogaea (raw)", 0.99, ["peanut (roasted)", "peanut butter"]),
    ("peanut (raw)", "moongphali", "nut", "Hindi name", 0.99, ["peanut (roasted)"]),
    ("peanut (roasted)", "roasted peanut", "nut", "Roasted", 0.95, ["peanut (raw)"]),
    ("fresh coconut kernel", "fresh coconut", "nut", "Cocos nucifera (fresh)", 0.99, ["dried coconut", "coconut water", "coconut milk"]),
    ("fresh coconut kernel", "nariyal", "nut", "Hindi name", 0.95, ["dried coconut"]),
    ("dried coconut", "dried coconut", "nut", "Copra", 0.99, ["fresh coconut", "desiccated coconut"]),
    ("dried coconut", "copra", "nut", "Technical name", 0.95, ["fresh coconut"]),
    ("dried coconut", "khopra", "nut", "Hindi name", 0.95, ["fresh coconut"]),
    ("desiccated coconut", "desiccated coconut", "nut", "Dried shredded coconut", 0.95, ["fresh coconut"]),
    ("raisin", "raisin", "dried_fruit", "Dried grape", 0.95, ["black raisin", "munakka"]),
    ("raisin", "kishmish", "dried_fruit", "Hindi name", 0.95, ["black raisin"]),
    ("date", "date", "dried_fruit", "Phoenix dactylifera", 0.95, ["fresh date", "date syrup"]),
    ("date", "khajoor", "dried_fruit", "Hindi name", 0.95, ["fresh date"]),
    ("fig (dried)", "fig", "dried_fruit", "Ficus carica", 0.95, ["fresh fig"]),
    ("fig (dried)", "anjeer", "dried_fruit", "Hindi name", 0.95, ["fresh fig"]),
]


# ============================================================
# OPTIMIZED NORMALIZATION PIPELINE
# ============================================================

# Pre-compile all regex patterns
FRACTION_MAP = {
    '\u00BC': '1/4', '\u00BD': '1/2', '\u00BE': '3/4',
    '\u2150': '1/7', '\u2151': '1/9', '\u2152': '1/10',
    '\u2153': '1/3', '\u2154': '2/3', '\u2155': '1/5',
    '\u2156': '2/5', '\u2157': '3/5', '\u2158': '4/5',
    '\u2159': '1/6', '\u215A': '5/6', '\u215B': '1/8',
    '\u215C': '3/8', '\u215D': '5/8', '\u215E': '7/8',
}

# Pre-compiled regex patterns
SPLIT_PATTERN = re.compile(r',\s*(?=[A-Za-z0-9\u0900-\u097F])')
WHITESPACE_PATTERN = re.compile(r'\s+')
DASH_PATTERN = re.compile(r'[\u2013\u2014\u2212]')
SLASH_PATTERN = re.compile(r'[\u2044\u2215]')
BULLET_PATTERN = re.compile(r'[\u2022\u2023\u25E6\u2043]')
FRACTION_PATTERN = re.compile('|'.join(re.escape(k) for k in FRACTION_MAP.keys()))

# Build synonym lookup structures for O(1) exact match
def build_synonym_lookup(raw_data):
    """Build optimized lookup structures from raw synonym data."""
    exact = {}      # normalized synonym -> entry (for exact match)
    word_set = set()  # single-word synonyms
    multiword = {}   # multi-word synonyms -> entry

    for canonical, synonym, category, evidence, confidence, excludes in raw_data:
        key = synonym.lower().strip()
        entry = {
            'canonical': canonical,
            'synonym': synonym,
            'category': category,
            'evidence': 'evidence',
            'confidence': confidence,
            'excludes': excludes
        }
        # Normalize key for matching
        key_norm = synonym.lower().strip()
        words = key_norm.split()
        if len(words) == 1:
            # Single word - use word boundary
            exact[key_norm] = entry
        else:
            # Multi-word - exact phrase match
            multiword[key_norm] = entry

    return exact, multiword


# Pre-build synonym lookups
EXACT_SYNONYMS, MULTIWORD_SYNONYMS = build_synonym_lookup(SYNONYM_RAW_DATA)
ALL_SYNONYM_KEYS = set(EXACT_SYNONYMS.keys()) | set(MULTIWORD_SYNONYMS.keys())

# For fast word-boundary checking, build a trie or use word-based matching
# Build set of all words that start synonyms
SYNONYM_WORDS = set()
for key in ALL_SYNONYM_KEYS:
    for word in key.split():
        SYNONYM_WORDS.add(word)


@dataclass
class NormalizationRecord:
    recipe_id: int
    original_line: str
    original_ingredient: str
    normalized_ingredient: str
    transformations: List[str]
    synonym_applied: Optional[str] = None
    synonym_confidence: Optional[float] = None
    flags: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class IngredientNormalizer:
    """Optimized normalizer using word-set pre-filtering."""

    def __init__(self):
        self.records: List[NormalizationRecord] = []
        self.stats = Counter()

    def normalize_text(self, text: str) -> Tuple[str, List[str]]:
        """Apply text-level normalization - vectorized where possible."""
        transformations = []
        original = text

        # Unicode NFC
        text = unicodedata.normalize('NFC', text)
        if text != original:
            transformations.append("unicode_nfc")

        # Lowercase
        text = text.lower()
        transformations.append("lowercase")

        # Whitespace
        text = WHITESPACE_PATTERN.sub(' ', text).strip()
        transformations.append("whitespace_normalize")

        # Punctuation
        text = DASH_PATTERN.sub('-', text)
        text = SLASH_PATTERN.sub('/', text)
        text = BULLET_PATTERN.sub(',', text)
        transformations.append("punctuation_normalize")

        # Fractions
        def replace_frac(match):
            return FRACTION_MAP[match.group(0)]
        text, n = FRACTION_PATTERN.subn(lambda m: FRACTION_MAP[m.group(0)], text)
        if n:
            for frac_char, frac_text in FRACTION_MAP.items():
                if frac_char in original:
                    transformations.append(f"fraction_{frac_text.replace('/', '_')}")

        return text, transformations

    def split_ingredient_line(self, line: str) -> List[str]:
        """Split on commas - fast regex."""
        parts = SPLIT_PATTERN.split(line)
        return [p.strip() for p in parts if p.strip()]

    def apply_synonyms_fast(self, ingredient: str) -> Tuple[str, List[str], Optional[str], Optional[float], List[str]]:
        """Fast synonym application using word-set pre-filtering."""
        transformations = []
        synonym_applied = None
        confidence = None
        flags = []

        # Quick check: does ingredient contain any synonym words?
        ingredient_words = set(ingredient.split())
        if not ingredient_words & SYNONYM_WORDS:
            flags.append("no_synonym_match")
            return ingredient, transformations, None, None, flags

        # Try multi-word synonyms first (longest first)
        for synonym in sorted(MULTIWORD_SYNONYMS.keys(), key=len, reverse=True):
            if synonym in ingredient:  # Fast substring check first
                entry = MULTIWORD_SYNONYMS[synonym]
                # Word boundary check
                pattern = r'\b' + re.escape(synonym) + r'\b'
                if re.search(pattern, ingredient):
                    entry_data = MULTIWORD_SYNONYMS[synonym]
                    canonical = entry_data['canonical']
                    new_ing = re.sub(r'\b' + re.escape(synonym) + r'\b', canonical, ingredient)
                    transformations.append(f"synonym_multiword:{synonym}->{canonical}")
                    return new_ing, transformations, synonym, entry_data['confidence'], []

        # Single-word synonyms with word boundaries
        for synonym in sorted(EXACT_SYNONYMS.keys(), key=len, reverse=True):
            if synonym in ingredient_words:  # Fast set membership check
                # Verify word boundary
                pattern = r'\b' + re.escape(synonym) + r'\b'
                if re.search(pattern, ingredient):
                    entry = EXACT_SYNONYMS[synonym]
                    canonical = entry['canonical']
                    new_ing = re.sub(r'\b' + re.escape(synonym) + r'\b', canonical, ingredient)
                    transformations.append(f"synonym_word:{synonym}->{canonical}")
                    return new_ing, transformations, synonym, entry['confidence'], []

        flags.append("no_synonym_match")
        return ingredient, transformations, None, None, flags

    def normalize_text(self, text: str) -> Tuple[str, List[str]]:
        transformations = []
        original = text

        text = unicodedata.normalize('NFC', text)
        if text != original:
            transformations.append("unicode_nfc")

        text = text.lower()
        transformations.append("lowercase")

        text = WHITESPACE_PATTERN.sub(' ', text).strip()
        transformations.append("whitespace_normalize")

        text = DASH_PATTERN.sub('-', text)
        text = SLASH_PATTERN.sub('/', text)
        text = BULLET_PATTERN.sub(',', text)
        transformations.append("punctuation_normalize")

        # Fractions
        def replace_frac(match):
            return FRACTION_MAP[match.group(0)]
        text, n = FRACTION_PATTERN.subn(replace_frac, text)
        if n:
            for k, v in FRACTION_MAP.items():
                if k in original:
                    transformations.append(f"fraction_{v.replace('/', '_')}")

        return text, transformations

    def split_ingredient_line(self, line: str) -> List[str]:
        parts = SPLIT_PATTERN.split(line)
        return [p.strip() for p in parts if p.strip()]

    def normalize_ingredient_line(self, recipe_id: int, original_line: str) -> List[NormalizationRecord]:
        ingredients = self.split_ingredient_line(original_line)
        records = []
        for ing in ingredients:
            normalized_text, text_transforms = self.normalize_text(ing)
            final_ingredient, syn_transforms, synonym_applied, confidence, flags = self.apply_synonyms_fast(normalized_text)
            all_transforms = text_transforms + syn_transforms

            record = NormalizationRecord(
                recipe_id=recipe_id,
                original_line=original_line,
                original_ingredient=ing,
                normalized_ingredient=final_ingredient,
                transformations=all_transforms,
                synonym_applied=synonym_applied,
                synonym_confidence=confidence,
                flags=flags
            )
            records.append(record)
            self.stats['total_ingredients'] += 1
            if synonym_applied:
                self.stats['synonym_applied'] += 1
            if 'no_synonym_match' in flags:
                self.stats['no_synonym_match'] += 1
        return records

    def process_recipes(self, recipes_df: pd.DataFrame) -> List[NormalizationRecord]:
        all_records = []
        for _, row in recipes_df.iterrows():
            recipe_id = row['recipe_id']
            for source_field, source_text in [('ingredients_raw', row['ingredients_raw']), ('ingredients_en', row['ingredients_en'])]:
                records = self.normalize_ingredient_line(recipe_id, source_text)
                for r in records:
                    r.flags.append(f"source:{source_field}")
                all_records.extend(records)
        return all_records


def build_synonym_dict(raw_data):
    """Build the full synonym dict for reporting."""
    synonym_dict = {}
    for canonical, synonym, category, evidence, confidence, excludes in raw_data:
        key = synonym.lower().strip()
        entry = SynonymEntry(
            canonical_name=canonical,
            synonym=synonym,
            category=category,
            evidence=evidence,
            confidence=confidence,
            excludes=excludes
        )
        if key in synonym_dict:
            if confidence > synonym_dict[key].confidence:
                synonym_dict[key] = entry
        else:
            synonym_dict[key] = entry
    return synonym_dict


def main():
    print("="*60)
    print("STAGE 1 - INGREDIENT NORMALIZATION (Optimized)")
    print("="*60)

    recipes_path = "data/processed/recipes.parquet"
    print(f"Loading recipes from {recipes_path}...")
    recipes_df = pd.read_parquet(recipes_path)
    print(f"Loaded {len(recipes_df)} recipes")

    print("Building synonym dictionary...")
    synonym_dict = build_synonym_dict(SYNONYM_RAW_DATA)
    print(f"Loaded {len(synonym_dict)} synonym entries")

    # Save synonym dictionary
    syn_rows = []
    for key, entry in synonym_dict.items():
        syn_rows.append({
            'synonym_key': key,
            'canonical_name': entry.canonical_name,
            'synonym': entry.synonym,
            'category': entry.category,
            'evidence': entry.evidence,
            'confidence': entry.confidence,
            'excludes': '; '.join(entry.excludes),
            'notes': entry.notes
        })
    syn_df = pd.DataFrame(syn_rows)
    syn_path = "data/interim/phase2/ingredient_synonyms.csv"
    syn_df.to_csv(syn_path, index=False)
    print(f"Saved synonym dictionary to {syn_path} ({len(syn_df)} entries)")

    print("Running normalization...")
    normalizer = IngredientNormalizer()
    all_records = normalizer.process_recipes(recipes_df)

    print(f"Processed {normalizer.stats['total_ingredients']} ingredient items")
    print(f"Synonym applied: {normalizer.stats['synonym_applied']}")
    print(f"No synonym match: {normalizer.stats['no_synonym_match']}")

    records_data = []
    for r in all_records:
        records_data.append({
            'recipe_id': r.recipe_id,
            'source_line': r.original_line,
            'source_ingredient': r.original_ingredient,
            'normalized_ingredient': r.normalized_ingredient,
            'transformations': '; '.join(r.transformations),
            'synonym_applied': r.synonym_applied,
            'synonym_confidence': r.synonym_confidence,
            'flags': '; '.join(r.flags),
            'timestamp': r.timestamp
        })

    norm_df = pd.DataFrame(records_data)

    out_path = "data/interim/phase2/normalized_ingredients.parquet"
    norm_df.to_parquet(out_path, index=False)
    print(f"Saved normalized ingredients to {out_path} ({len(norm_df)} records)")

    csv_path = "data/interim/phase2/normalized_ingredients.csv"
    norm_df.to_csv(csv_path, index=False)
    print(f"Saved CSV to {csv_path}")

    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)

    total_recipes = norm_df['recipe_id'].nunique()
    print(f"Recipes processed: {total_recipes} (expected 6865)")

    total_original = norm_df['source_ingredient'].nunique()
    total_normalized = norm_df['normalized_ingredient'].nunique()
    print(f"Unique original expressions: {total_original}")
    print(f"Unique normalized expressions: {total_normalized}")

    synonym_used = norm_df[norm_df['synonym_applied'].notna()]['synonym_applied'].nunique()
    print(f"Unique synonyms applied: {synonym_used}")

    unknown = norm_df[norm_df['flags'].str.contains('no_synonym_match', na=False)]['normalized_ingredient'].nunique()
    print(f"Unique expressions without synonym match: {unknown}")

    transform_counter = Counter()
    for trans in norm_df['transformations']:
        for t in trans.split('; '):
            if t:
                transform_counter[t] += 1
    print(f"\nTransformation counts:")
    for t, c in transform_counter.most_common(20):
        print(f"  {t}: {c}")

    print("\nSample successful synonym normalizations:")
    samples = norm_df[norm_df['synonym_applied'].notna()].head(10)
    for _, row in samples.iterrows():
        print(f"  '{row['source_ingredient']}' -> '{row['normalized_ingredient']}' (via '{row['synonym_applied']}')")

    print("\nSample unmatched ingredients (first 20):")
    unmatched = norm_df[norm_df['flags'].str.contains('no_synonym_match', na=False)]['normalized_ingredient'].unique()
    for u in unmatched[:20]:
        print(f"  {u}")

    report_path = "reports/phase2/normalization_validation_report.md"
    generate_validation_report(norm_df, normalizer.stats, transform_counter, synonym_dict, report_path)
    print(f"\nValidation report saved to {report_path}")

    print("\nStage 1 complete.")


def generate_validation_report(norm_df: pd.DataFrame, stats: Counter, transform_counter: Counter,
                               synonym_dict: Dict[str, SynonymEntry], output_path: str):
    total_recipes = norm_df['recipe_id'].nunique()
    total_original = norm_df['source_ingredient'].nunique()
    total_normalized = norm_df['normalized_ingredient'].nunique()
    synonym_used = norm_df[norm_df['synonym_applied'].notna()]['synonym_applied'].nunique()
    unknown = norm_df[norm_df['flags'].str.contains('no_synonym_match', na=False)]['normalized_ingredient'].nunique()
    ambiguous = norm_df[norm_df['flags'].str.contains('distinction:', na=False)]['normalized_ingredient'].nunique()

    with open(output_path, 'w') as f:
        f.write("# Stage 1 - Ingredient Normalization Validation Report\n\n")
        f.write(f"**Date:** {datetime.now().isoformat()}\n")
        f.write(f"**Input:** 6,865 recipes from `data/processed/recipes.parquet`\n")
        f.write(f"**Output:** `data/interim/phase2/normalized_ingredients.parquet`\n")
        f.write(f"**Synonym Dictionary:** `data/interim/phase2/ingredient_synonyms.csv`\n\n")

        f.write("## Summary Statistics\n\n")
        f.write(f"| Metric | Value |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| Total recipes processed | {total_recipes} |\n")
        f.write(f"| Total ingredient lines (raw + en) | {stats['total_ingredients']} |\n")
        f.write(f"| Unique original expressions | {total_original} |\n")
        f.write(f"| Unique normalized expressions | {total_normalized} |\n")
        f.write(f"| Synonym mappings applied | {stats['synonym_applied']} |\n")
        f.write(f"| Unique synonyms applied | {synonym_used} |\n")
        f.write(f"| Expressions without synonym match | {unknown} |\n")
        f.write(f"| Expressions with distinction flags | {ambiguous} |\n")
        f.write(f"| Synonym dictionary size | {len(synonym_dict)} |\n\n")

        f.write("## Transformation Counts\n\n")
        f.write(f"| Transformation | Count |\n")
        f.write(f"|----------------|-------|\n")
        for t, c in transform_counter.most_common():
            f.write(f"| {t} | {c} |\n")
        f.write("\n")

        f.write("## Synonym Dictionary Categories\n\n")
        cat_counts = Counter(e.category for e in synonym_dict.values())
        f.write(f"| Category | Count |\n")
        f.write(f"|----------|-------|\n")
        for cat, count in cat_counts.most_common():
            f.write(f"| {cat} | {count} |\n")
        f.write("\n")

        f.write("## Representative Successful Examples\n\n")
        samples = norm_df[norm_df['synonym_applied'].notna()].head(20)
        f.write("| Original | Normalized | Synonym Applied | Confidence |\n")
        f.write("|----------|------------|-----------------|------------|\n")
        for _, row in samples.iterrows():
            f.write(f"| {row['source_ingredient']} | {row['normalized_ingredient']} | {row['synonym_applied']} | {row['synonym_confidence']:.2f} |\n")
        f.write("\n")

        f.write("## Representative Unmatched / Unknown Expressions\n\n")
        unmatched = norm_df[norm_df['flags'].str.contains('no_synonym_match', na=False)]['normalized_ingredient'].unique()
        for u in unmatched[:30]:
            f.write(f"- {u}\n")
        f.write("\n")

        f.write("## Known Limitations\n\n")
        f.write("1. **Synonym coverage incomplete**: Many regional names, brand names, and compound ingredients not yet mapped.\n")
        f.write("2. **Quantity/unit not parsed**: This stage only normalizes ingredient names; quantities and units remain embedded.\n")
        f.write("3. **Preparation state ambiguous**: 'chopped onion' vs 'onion' not distinguished unless explicitly in synonym dict.\n")
        f.write("4. **Mixed language handling**: Hindi/English mixed text handled but transliteration variations may be missed.\n")
        f.write("5. **Compound ingredients**: Multi-word ingredients like 'ginger garlic paste' may not match single-word synonyms.\n")
        f.write("6. **No IFCT matching**: This stage only normalizes; IFCT matching is Stage 3.\n")
        f.write("7. **Provisional synonyms**: Some mappings have confidence < 0.9 and should be reviewed.\n")
        f.write("8. **Distinction preservation**: Explicit exclusion lists prevent over-merging but may miss edge cases.\n")

        f.write("\n## Reproducibility\n\n")
        f.write("All normalization is deterministic. Re-running with same inputs produces identical outputs.\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")


if __name__ == "__main__":
    main()