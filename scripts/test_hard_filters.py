"""Test filtres durs sur règles connues."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from isinglab.meta_learner.filters import apply_hard_filters

# Test cases
test_rules = [
    ("B3/S23", "Life", "Devrait passer"),
    ("B36/S23", "HighLife", "Devrait passer"),
    ("B34/S34", "34 Life", "Devrait passer"),
    ("B45/S34", "Artefact v3", "Devrait échouer (quasi-death)"),
    ("B8/S3", "Artefact v3", "Devrait échouer (mort totale)"),
    ("B018/S1236", "Découverte AGI", "Devrait passer (density 0.37)"),
    ("B38/S06", "Artefact top AGI", "Devrait échouer (quasi-death)"),
]

print("=" * 80)
print("TEST FILTRES DURS")
print("=" * 80)
print()

passed = 0
failed = 0

for notation, name, expected in test_rules:
    pass_filter, reason = apply_hard_filters(notation)
    
    status = "PASS" if pass_filter else "REJECT"
    match = "OK" if (("passer" in expected.lower()) == pass_filter) else "FAIL"
    
    print(f"{notation:<15} ({name:<20}) : {status:<6} ({reason:<30}) [{match}]")
    
    if match == "OK":
        passed += 1
    else:
        failed += 1

print("\n" + "=" * 80)
print(f"Résultats : {passed} OK, {failed} FAIL")
print("=" * 80)

if failed == 0:
    print("\n[OK] Filtres fonctionnent correctement")
else:
    print(f"\n[FAIL] {failed} erreurs de classification")




