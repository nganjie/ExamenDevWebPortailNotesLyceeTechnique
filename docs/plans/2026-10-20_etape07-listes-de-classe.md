# Plan — Étape 07 : listes de classe, fiche élève, API des moyennes

- Date : 2026-10-20
- Spec : [../specs/2026-10-20_etape07-listes-de-classe.md](../specs/2026-10-20_etape07-listes-de-classe.md)

## Étapes

1. `app.py` : `synthese_classe(classe, sequence)` (réutilisée par la page et l'API), routes de la spec,
   `donnees_bulletin` enrichie de l'identifiant de chaque note.
2. Gabarits `enseignant/classes.html`, `enseignant/liste_classe.html`, `enseignant/fiche_eleve.html` ;
   menu « Listes de classe ».
3. `static/js/liste_classe.js` : recherche instantanée + histogramme de répartition (Chart.js via fetch).
4. `tests/test_listes.py` : liste, rangs = bulletin, API (forme, droits, 404), fiche et lien de correction.

## Commits prévus

1. `docs: spec et plan de l'étape 07`
2. `feat: listes de classe, fiche élève et API des moyennes (étape 07)`
