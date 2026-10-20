# Plan — Étape 09 : administration des classes et des élèves

- Date : 2026-10-20
- Spec : [../specs/2026-10-20_etape09-administration.md](../specs/2026-10-20_etape09-administration.md)

## Étapes

1. `app.py` : `verifier_classe(formulaire, classe)`, `verifier_eleve(formulaire, eleve)`,
   `generer_matricule(classe)`, `generer_code()`, routes de la spec, export CSV (`csv`, `io`).
2. Gabarits `admin/classes.html`, `admin/classe_formulaire.html`, `admin/eleves.html`,
   `admin/eleve_formulaire.html` ; groupe « Administration » du menu.
3. `tests/test_administration.py` (sur une copie de la base) : droits, création / doublon / modification
   de classe, effectif maximal, ajout d'élève puis connexion avec le code, classe pleine, nouveau code,
   suppression, export CSV.
4. Captures ordinateur et téléphone.

## Commits prévus

1. `docs: spec et plan de l'étape 09`
2. `feat: administration des classes et des élèves (étape 09)`
