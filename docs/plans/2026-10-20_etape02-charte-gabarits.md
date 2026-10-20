# Plan — Étape 02 : charte graphique, icônes, gabarits et accueil

- Date : 2026-10-20
- Spec : [../specs/2026-10-20_etape02-charte-gabarits.md](../specs/2026-10-20_etape02-charte-gabarits.md)

## Étapes

1. Copier les polices Inter (400, 500, 600, 700) et Manrope (700, 800) en `woff2` + licence OFL dans `static/fonts/`.
2. Écrire `static/images/icones.svg` (≈ 30 symboles au trait 24 × 24).
3. Réécrire `static/css/style.css` : variables, base, typographie, boutons, formulaires, cartes,
   tableaux, badges, alertes, en-tête, pied de page, mise en page de l'accueil, points de rupture.
4. Écrire `templates/macros.html`, réécrire `base.html`, `index.html`, `404.html`, ajouter `500.html`.
5. Écrire `static/js/main.js` (onglets, fermeture des messages flash, menu mobile) et `static/js/validation.js`.
6. Dans `app.py` : constante `NOM_LYCEE`, gestionnaires 404 / 500, routes de connexion provisoires.
7. Tests `tests/test_pages.py` : accueil 200, 404 personnalisée, présence des labels.

## Fichiers

`static/fonts/*`, `static/images/icones.svg`, `static/css/style.css`, `static/js/main.js`,
`static/js/validation.js`, `templates/{base,macros,index,404,500}.html`, `app.py`, `tests/test_pages.py`

## Tests

- `python -m unittest discover tests`
- Vérification visuelle (capture Playwright) à 390 px et 1440 px.

## Commits prévus

1. `docs: spec et plan de l'étape 02`
2. `style: charte graphique, icônes et gabarits (étape 02)`
