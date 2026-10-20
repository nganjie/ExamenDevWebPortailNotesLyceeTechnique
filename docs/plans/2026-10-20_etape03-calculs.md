# Plan — Étape 03 : moyennes, rangs et appréciations

- Date : 2026-10-20
- Spec : [../specs/2026-10-20_etape03-calculs.md](../specs/2026-10-20_etape03-calculs.md)

## Étapes

1. Écrire `projet/calculs.py` (fonctions pures + `bulletin_classe` avec une seule requête SQL paramétrée).
2. Écrire `projet/tests/test_calculs.py` : moyenne simple, matière non notée, aucune note, arrondi,
   ex æquo au milieu et en tête, appréciations aux bornes, tranches, taux de réussite,
   `bulletin_classe` sur la base de test (30 élèves classés, rangs cohérents).
3. Lancer toute la suite de tests.

## Commits prévus

1. `docs: spec et plan de l'étape 03`
2. `feat: module de calcul des moyennes et des rangs (étape 03)`
