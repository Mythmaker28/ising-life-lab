# Memory Rules Dataset

**Fichier**: `data/memory_rules_dataset.json`

## Format

Chaque règle encodée comme:
```json
{
  "notation": "B01/S3",
  "bornMask": [1,1,0,0,0,0,0,0,0],
  "surviveMask": [0,0,0,1,0,0,0,0,0],
  "isMemoryCandidate": true,
  "avgRecall": 96.7,
  "source": "hall_of_fame"
}
```

**bornMask/surviveMask**: Vecteurs binaires (9 éléments pour 0-8 voisins)  
**isMemoryCandidate**: Validé par AutoScan multi-noise  
**avgRecall**: % moyen (null si non testé)

## Usage ML

```python
import json
with open('data/memory_rules_dataset.json') as f:
    data = json.load(f)

X = [r['bornMask'] + r['surviveMask'] for r in data['rules']]  # Features (18D)
y = [r['isMemoryCandidate'] for r in data['rules']]  # Labels

# Entrainer classificateur
# Prédire si nouvelle règle est memory-like
```

Prêt pour supervised learning sur règles CA.

