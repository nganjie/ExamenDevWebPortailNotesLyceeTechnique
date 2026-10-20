# Plan — Étape 06 : évaluations, saisie et correction des notes

- Date : 2026-10-20
- Spec : [../specs/2026-10-20_etape06-evaluations-saisie.md](../specs/2026-10-20_etape06-evaluations-saisie.md)

## Étapes

1. `app.py` : `lire_note(texte)` (validation commune), `evaluation_autorisee(id)`, routes de la spec,
   transaction pour la saisie et la correction.
2. Gabarits `enseignant/evaluations.html`, `enseignant/saisie.html`, `enseignant/correction.html` ;
   menu « Évaluations » ; liens depuis le tableau de bord.
3. `static/js/saisie.js` (contrôle immédiat, moyenne en direct, blocage du bouton).
4. CSS : bande des séquences, case de note, panneau de synthèse.
5. `tests/test_evaluations.py` : création (+ doublon), droits, saisie valide / invalide (tout ou rien),
   date future, clôture, correction et historique, suppression.
6. Captures et essai de la saisie en direct dans le navigateur.

## Commits prévus

1. `docs: spec et plan de l'étape 06`
2. `feat: évaluations, saisie des notes en direct et corrections (étape 06)`
