# Plan — Étape 10 : import d'élèves

- Date : 2026-10-20
- Spec : [../specs/2026-10-20_etape10-import-eleves.md](../specs/2026-10-20_etape10-import-eleves.md)

## Étapes

1. `importation.py` : `lire_fichier` (CSV, XLSX, XLS, ODS), `deviner_correspondance`, `normaliser_date`,
   `analyser_lignes` (sans Flask, testable), modèles CSV / XLSX.
2. `app.py` : dossier temporaire, routes de la spec, réutilisation de `generer_matricule` et `generer_code`.
3. Gabarits `admin/import.html` (étapes 1 et 2) et `admin/import_resultat.html` (étape 3) ;
   `static/js/import.js` (zone de dépôt par glisser-déposer, nom du fichier choisi) ; menu.
4. `requirements.txt` : `openpyxl`, `xlrd`, `odfpy` ; fichiers d'exemple dans `exemples_import/`.
5. `tests/test_import.py` : lecture des formats, correspondance devinée, dates, doublons, classe pleine,
   parcours complet (aperçu → import → connexion), code téléchargeable une seule fois.

## Commits prévus

1. `docs: spec et plan de l'étape 10`
2. `feat: import d'élèves CSV, XLSX, XLS et ODS (étape 10)`
