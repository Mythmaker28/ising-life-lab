# Bridge arrest-molecules

**Projet** : arrest-molecules  
**GitHub** : https://github.com/Mythmaker28/arrest-molecules  
**Statut** : 🔴 **Spéculatif (Données Énergétiques Nécessaires)**

---

## Vue d'Ensemble

**arrest-molecules** propose un **framework théorique** pour molécules d'arrêt (dampening compounds) en régulation biologique.

**Integration ising-life-lab** : Métriques stabilité attracteurs (`basin`, `stability`) appliquées aux paysages énergétiques moléculaires (si données ΔG/Ea disponibles).

---

## État Actuel des Connaissances

### Informations Disponibles (via README Atlas)

**Contenu** : 10 compounds catalogués, 44 predictions  
**Framework** : FAIR² compliant (Findable, Accessible, Interoperable, Reusable + Reproducible)  
**Zenodo** : DOI 10.5281/zenodo.17420685 (dataset)

**Vocabulaire partagé avec qubits** (mentionné README Atlas) :
- Energy landscapes
- Arrest kinetics ↔ Decoherence
- Tunneling vs activation barriers ↔ Quantum vs classical transitions

### Informations Manquantes (À Explorer)

❓ **Format dataset** : CSV ? JSON ? .xyz (structures moléculaires) ?  
❓ **Nature 44 predictions** : Ki ? ΔΔG ? Constantes d'arrêt ? Temps caractéristiques ?  
❓ **Données énergétiques** : ΔG (énergies libres), Ea (barrières activation), paysages complets ?  
❓ **Modèles computationnels** : MD ? DFT ? Docking ? Cinétique chimique ?  
❓ **Scripts disponibles** : Calculs ΔG, analyse paysages ?

---

## Actions Nécessaires (Exploration)

### Phase 1 : Clone & Téléchargement Dataset

```bash
# Clone local arrest-molecules
cd ..
git clone https://github.com/Mythmaker28/arrest-molecules.git
cd arrest-molecules

# Télécharger dataset Zenodo
# DOI: 10.5281/zenodo.17420685
# URL: https://zenodo.org/record/17420685/files/arrest_molecules_dataset.zip ?

# Lister structure
ls -R

# Identifier fichiers clés
find . -name "*.csv" -o -name "*.json" -o -name "*.xyz" -o -name "*.pdb"
```

**Objectifs** :
1. Comprendre format 10 compounds (SMILES, structures 3D ?)
2. Identifier nature 44 predictions (énergies, constantes ?)
3. Localiser données paysages énergétiques (ΔG, Ea)
4. Vérifier modèles computationnels disponibles

### Phase 2 : Évaluer Applicabilité Métriques ising-life-lab

**Prérequis** : Données ΔG/Ea disponibles pour états moléculaires

**Métriques transposables** (si données OK) :

| Métrique ising-lab | Application arrest-molecules | Validation Nécessaire |
|--------------------|------------------------------|------------------------|
| **basin** (diversité attracteurs) | Diversité états d'arrêt vs oscillation | Données conformations multiples |
| **stability** (cohérence multi-échelles) | Stabilité paysage énergétique (variance ΔG) | Paysages complets (ΔG vs coordonnées réaction) |
| **robustness** (résistance bruit) | Robustesse cinétique (perturbations température, pH) | Données cinétiques expérimentales |

**Attention** : Connexion **hautement spéculative** sans données ΔG/Ea. Ne pas extrapoler.

---

## Hypothèses sur Format Données

### Compounds (10 molécules)

**Format hypothétique** :

| Colonne | Type | Description |
|---------|------|-------------|
| `compound_id` | str | Identifiant unique |
| `name` | str | Nom molécule |
| `smiles` | str | Structure SMILES |
| `molecular_weight` | float | Masse moléculaire |
| `arrest_type` | str | Type d'arrêt (oscillation, bistable, etc.) |
| `target_pathway` | str | Voie biologique ciblée |

### Predictions (44 valeurs)

**Hypothèses possibles** :

**Hypothèse 1 : Constantes d'interaction**
- Ki (constante inhibition)
- Kd (constante dissociation)
- ΔΔG (énergie liaison)

**Hypothèse 2 : Propriétés dynamiques**
- Temps arrêt caractéristique (τ_arrest)
- Constantes cinétiques (k_on, k_off)
- Barrières activation (Ea)

**Hypothèse 3 : Prédictions multi-conditions**
- 10 compounds × 4-5 conditions (pH, température) = 40-50 predictions

---

## Usage avec ising-life-lab (Hypothétique)

### Scénario 1 : Stabilité Paysages Énergétiques

**Prérequis** : Paysages ΔG disponibles (ex: ΔG vs coordonnée réaction)

```python
import numpy as np
from design_space.metrics import stability_energy_landscape  # À créer

# Charger paysage énergétique compound
# Hypothèse : CSV avec colonnes 'reaction_coord', 'delta_g_kcal_mol'
landscape = pd.read_csv("../arrest-molecules/data/compound_001_landscape.csv")

# Calculer stabilité (inverse variance ΔG)
stability = 1 / (1 + landscape['delta_g_kcal_mol'].var())

print(f"Stability score: {stability:.3f}")
# Score élevé = paysage plat (métastable)
# Score faible = paysage rugueux (instable)
```

### Scénario 2 : Diversité États (Basin)

**Prérequis** : Conformations multiples avec ΔG

```python
# États identifiés : arrest, oscillation, transition
states = {
    'arrest': {'delta_g': -10.0, 'rmsd': 0.0},    # État stable, énergie faible
    'oscillation': {'delta_g': -2.0, 'rmsd': 3.2}, # État métastable
    'transition': {'delta_g': 5.0, 'rmsd': 5.8}    # Barrière
}

def basin_diversity_score(states_dict):
    """
    Diversité bassins = variance énergies + variance RMSD
    Analogie: basin metric ising-lab (diversité attracteurs CA)
    """
    energies = [s['delta_g'] for s in states_dict.values()]
    rmsds = [s['rmsd'] for s in states_dict.values()]
    
    energy_var = np.var(energies)
    rmsd_var = np.var(rmsds)
    
    return energy_var + rmsd_var

basin_score = basin_diversity_score(states)
print(f"Basin diversity: {basin_score:.2f}")
```

### Scénario 3 : Robustesse Cinétique

**Prérequis** : Constantes cinétiques à différentes températures

```python
# Constantes d'arrêt à différentes températures
k_arrest = {
    295: 0.5,  # s^-1
    298: 0.48,
    301: 0.42,
    310: 0.30
}

def robustness_kinetics(k_dict):
    """
    Robustesse = inverse coefficient variation
    Analogie: robustness ising-lab (résistance bruit)
    """
    k_values = list(k_dict.values())
    cv = np.std(k_values) / np.mean(k_values)  # Coefficient variation
    return 1 / (1 + cv)

robustness = robustness_kinetics(k_arrest)
print(f"Robustness score: {robustness:.3f}")
# Score élevé = robuste à température
# Score faible = sensible à température
```

---

## Connexion Conceptuelle (Non Technique)

**README Atlas mentionne vocabulaire partagé** arrest-molecules ↔ qubits :

| Concept arrest-molecules | Analogue quantique | Limite |
|--------------------------|-------------------|--------|
| Energy landscapes | Hamiltonien, états propres | Métaphore, pas équivalence |
| Arrest kinetics | Decoherence | Échelles temps différentes |
| Tunneling vs activation | Quantum tunneling vs thermique | Régimes physiques différents |

**Attention** : Connexion **métaphorique**, pas technique. **Ne pas extrapoler** au-delà sans modèle rigoureux.

---

## Roadmap Integration

### 🔄 v8.2-v8.3 (Exploration)

**Actions immédiates** :
1. [ ] Clone local arrest-molecules
2. [ ] Télécharger dataset Zenodo (DOI: 10.5281/zenodo.17420685)
3. [ ] Identifier format (compounds, predictions, paysages ΔG ?)
4. [ ] Évaluer disponibilité données énergétiques

**Decision gate** : Si **pas de données ΔG/Ea** → Documenter comme **non applicable** et passer à autre chose (kill switch).

**Deadline** : Fin semaine 2 v8.2

### 🔮 v8.4+ (Si données OK)

**Implémentation** :
1. [ ] Créer `design_space/metrics_energy.py` (stability, basin pour paysages ΔG)
2. [ ] Tester métriques sur 10 compounds
3. [ ] Valider vs données cinétiques expérimentales (si disponibles)
4. [ ] Comparer à baseline (variance simple, sans métriques ising-lab)

**Deadline** : Mois 3

---

## Risques & Mitigation

### Risque 1 : Données ΔG Absentes

**Impact** : **Bloque intégration** (métriques ising-lab inapplicables)

**Mitigation** :
- Vérifier dataset Zenodo
- Contacter auteur si format ambigu
- **Accepter limitation** : documenter comme "non applicable", archiver

**Kill switch** : Si pas de ΔG après exploration (3-4h) → Clôturer cette branche, documenter échec.

### Risque 2 : Connexion Purement Métaphorique

**Impact** : Métriques ising-lab non pertinentes (faux signaux)

**Mitigation** :
- **Toujours valider vs baseline** (variance simple sans métriques)
- Comparer à données cinétiques expérimentales
- Si corrélation < 0.3 → Rejeter connexion

### Risque 3 : Domaines Incompatibles

**Impact** : Petites molécules ≠ CA/Ising (échelles, mécanismes différents)

**Mitigation** :
- Rester honnête : "exploration conceptuelle", pas "modèle prédictif"
- Pas de généralisation abusive
- Documenter limites clairement

---

## Principes Directeurs (Rappel)

### Pas de Spéculation Sans Données

- **Données manquantes** : Noter "unknown", ne pas inventer
- **Connexions** : Seulement si testables avec données réelles
- **Métriques** : Seulement si validation baseline possible

### Kill Switch

- **Si après 3-4h exploration** : Pas de données ΔG/Ea → Documenter échec, archiver
- **Pas de "peut-être avec autre approche"**
- **Accepter** : Certaines connexions sont non réalisables

---

## Contact & Contribution

**Issues arrest-molecules** : https://github.com/Mythmaker28/arrest-molecules/issues  
**Issues ising-life-lab** : (votre repo)

**Suggestions** :
- Clarifier format dataset Zenodo
- Partager paysages énergétiques (si disponibles)
- Documenter unités/conventions (ΔG, Ea)

---

**Bridge arrest-molecules ↔ ising-life-lab : Spéculatif (Données Nécessaires) 🔴**

**Exploration conditionnelle : Si ΔG/Ea disponibles → Tester métriques. Sinon → Archiver.**


