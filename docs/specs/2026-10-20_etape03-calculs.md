# Spec — Étape 03 : moyennes, rangs et appréciations

- Date : 2026-10-20
- Exigences couvertes : `P3-RG-1` (moyenne coefficientée juste), `P3-RG-2` (rang avec ex æquo),
  `P3-STAT-1..4` (fonctions de base des statistiques), `P3-BON-2` (appréciation automatique)

## Règles de calcul

1. **Moyenne coefficientée** d'un élève pour une séquence : `Σ(note × coefficient) / Σ(coefficients)`,
   sur les seules matières notées (hypothèse H4 : une matière sans note est exclue du numérateur
   **et** du dénominateur). Aucune note → pas de moyenne (`None`), pas de rang.
2. **Arrondi** : au centième, « au plus proche, 5 vers le haut » (`Decimal`, `ROUND_HALF_UP`), pour éviter
   les surprises des nombres à virgule (`12,345` → `12,35`).
3. **Rang** (classement « olympique ») calculé sur les moyennes **arrondies** : même moyenne = même rang,
   le suivant prend le rang égal à 1 + le nombre d'élèves devant lui. Exemple : 15,00 ; 12,50 ; 12,50 ; 11,00
   → rangs 1, 2, 2, 4.
4. **Appréciation** : < 8 Insuffisant ; 8 à < 10 Médiocre ; 10 à < 12 Passable ; 12 à < 14 Assez bien ;
   14 à < 16 Bien ; ≥ 16 Très bien.
5. **Tranches** des statistiques : « moins de 8 » `[0 ; 8[`, « 8 à 10 » `[8 ; 10[`, « 10 à 12 » `[10 ; 12[`,
   « 12 à 14 » `[12 ; 14[`, « 14 et plus » `[14 ; 20]`.
6. **Réussite** : moyenne ≥ 10.

## Interface du module `calculs.py`

| Fonction | Rôle |
|---|---|
| `arrondir(valeur)` | arrondi au centième (ou `None`) |
| `moyenne_coefficientee(notes)` | `notes` = liste de `(note, coefficient)` |
| `classer(moyennes)` | `{clé: moyenne}` → `{clé: rang}` avec ex æquo |
| `appreciation(moyenne)`, `tranche(moyenne)` | libellés |
| `taux_reussite(moyennes)`, `repartition(moyennes)` | statistiques sur une liste |
| `bulletin_classe(db, classe_id, sequence)` | moyennes, rangs et notes de tous les élèves d'une classe |

## Critères d'acceptation

- [ ] Les cas de la spec (ex æquo, matière non notée, arrondi) sont couverts par des tests qui passent.
- [ ] `bulletin_classe` renvoie pour chaque élève la moyenne, le rang, l'indicateur ex æquo et ses notes.
