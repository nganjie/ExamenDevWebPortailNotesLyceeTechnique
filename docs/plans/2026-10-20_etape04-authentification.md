# Plan — Étape 04 : authentification et rôles

- Date : 2026-10-20
- Spec : [../specs/2026-10-20_etape04-authentification.md](../specs/2026-10-20_etape04-authentification.md)

## Étapes

1. `app.py` : `charger_utilisateur` (`before_request` → `g.eleve`, `g.enseignant`), décorateurs,
   limitation des essais, routes de connexion / déconnexion, `/eleve`, `/enseignant`, page 403.
2. Gabarits `layout_eleve.html`, `layout_enseignant.html` (menu complété au fil des étapes),
   `eleve/accueil.html`, `enseignant/tableau_de_bord.html`, `403.html`.
3. CSS : cartes du tableau de bord.
4. `tests/test_authentification.py` : connexions réussies et ratées, accès refusés, limitation, déconnexion.
5. Captures téléphone / ordinateur de l'espace enseignant.

## Commits prévus

1. `docs: spec et plan de l'étape 04`
2. `feat: connexion des élèves et des enseignants, rôles (étape 04)`
