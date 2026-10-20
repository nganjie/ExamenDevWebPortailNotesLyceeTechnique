# Plan — Étape 05 : espace élève

- Date : 2026-10-20
- Spec : [../specs/2026-10-20_etape05-espace-eleve.md](../specs/2026-10-20_etape05-espace-eleve.md)

## Étapes

1. `app.py` : `sequences_notees(classe_id)`, `donnees_bulletin(eleve, sequence)`, `evolution_eleve(eleve)`,
   routes `/eleve`, `/eleve/bulletin/<sequence>`, `/api/eleves/<id>/evolution`, réponse JSON 403.
2. Gabarit `eleve/bulletin.html` (sélecteur de séquence, indicateurs, tableau adaptatif, historique,
   graphique, en-tête et signatures pour l'impression).
3. `static/css/impression.css` ; CSS du tableau adaptatif ; `static/js/graphique.js` (fetch + Chart.js).
4. Tests `tests/test_eleve.py` : moyenne recalculée à la main, rang, 404, API (propriétaire, autre élève, enseignant).
5. Captures ordinateur, téléphone et aperçu d'impression (PDF Playwright).

## Commits prévus

1. `docs: spec et plan de l'étape 05`
2. `feat: bulletin de l'élève, historique, graphique et impression (étape 05)`
