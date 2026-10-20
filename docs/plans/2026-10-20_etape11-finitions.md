# Plan — Étape 11 : finitions et préparation du rendu

- Date : 2026-10-20
- Spec : [../specs/2026-10-20_etape11-finitions.md](../specs/2026-10-20_etape11-finitions.md)

## Étapes

1. Script de vérification (hors projet) qui parcourt les pages principales connecté en élève, en enseignant et
   en administrateur : HTML envoyé au validateur Nu (W3C), axe-core injecté avec Playwright, largeur à 360 px.
2. Corriger chaque erreur relevée.
3. Écrire le README complet ; mettre à jour `docs/` (matrice de suivi).
4. Régénérer `projet.db`, `codes_eleves_test.csv` et `export_projet.sql`.
5. Captures ordinateur (1440 px) et téléphone (390 px) dans `captures/`.
6. Test du README dans un dossier neuf (copie + nouvel environnement virtuel).

## Commits prévus

1. `docs: spec et plan de l'étape 11`
2. `fix: corrections de validation HTML et d'accessibilité` (si nécessaire)
3. `docs: README complet, routes et matrice de suivi`
4. `chore: base de données, export et captures d'écran du rendu`
