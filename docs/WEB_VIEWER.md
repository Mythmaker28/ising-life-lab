# CA VIEWER WEB — Guide Utilisateur

**Version :** v2.3  
**Port :** localhost:8000

---

## DÉMARRAGE

```bash
python -m isinglab.server
# Ouvrir: http://localhost:8000
```

---

## UTILISATION

### 1. Charger une Règle

**Option A : Input manuel**
```
B3/S23          # Game of Life
B018/S1236      # diverse_memory
B08/S068        # chaotic_probe
```

**Option B : Dropdown**
- "Charger HoF" : Hall of Fame (7 règles)
- "Charger Memory" : Top 50 meta_memory

### 2. Paramètres

- **Taille grille :** 16, 32, 64, 128
- **Densité init :** 0.0-1.0 (défaut 0.3)
- **Bruit init :** 0.0-0.5 (défaut 0.0)

### 3. Contrôles

- **Appliquer Règle** : Génère grille initiale
- **Start** : Animation continue
- **Pause** : Arrête animation
- **Step** : Avance d'1 itération
- **Reset** : Réinitialise grille (nouveau pattern aléatoire)

### 4. Stats Live

- **Steps** : Nombre d'itérations
- **Densité** : Fraction cellules vivantes
- **FPS** : Vitesse animation
- **Règle Active** : Notation actuelle

---

## EXEMPLES

### Exemple 1 : Game of Life
```
Règle: B3/S23
Taille: 32x32
Densité: 0.3
Bruit: 0.0
→ Observer gliders, blinkers, structures stables
```

### Exemple 2 : Diverse Memory
```
Règle: B018/S1236
Taille: 64x64
Densité: 0.4
Bruit: 0.1
→ Observer robustesse au bruit
```

### Exemple 3 : Chaotic Probe
```
Règle: B08/S068
Taille: 32x32
Densité: 0.2
Bruit: 0.0
→ Observer dynamiques chaotiques
```

---

## ARCHITECTURE

**Backend :**
- `isinglab/server.py` : HTTP server (http.server)
- API REST : `/api/hof`, `/api/memory`

**Frontend :**
- `isinglab/static/viewer.html` : HTML + CSS + JS vanilla
- Canvas 2D pour affichage grille
- Pas de frameworks lourds

---

## LIMITATIONS

- Pas de save/load états
- Pas de metrics live (entropy, edge, capacity)
- Pas de comparaison côte-à-côte

**Suffisant pour exploration basique.**

---

**VIEWER OPÉRATIONNEL — EXPLORATION TEMPS RÉEL DISPONIBLE**

