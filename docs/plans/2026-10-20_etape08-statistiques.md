# Plan — Étape 08 : statistiques

- Date : 2026-10-20
- Spec : [../specs/2026-10-20_etape08-statistiques.md](../specs/2026-10-20_etape08-statistiques.md)

## Étapes

1. `app.py` : `statistiques(sequence)` (réutilise `synthese_classe`, une requête `AVG` groupée pour les
   matières), routes page + API ; menu « Statistiques ».
2. Gabarit `enseignant/statistiques.html` ; `static/js/statistiques.js` (fetch + 2 graphiques).
3. CSS : cartes par classe, podiums, tableau coloré.
4. `tests/test_statistiques.py` : cohérence tranches / effectif, moyenne matière recalculée, ex æquo du podium, droits.

## Commits prévus

1. `docs: spec et plan de l'étape 08`
2. `feat: statistiques et API /api/statistiques (étape 08)`
