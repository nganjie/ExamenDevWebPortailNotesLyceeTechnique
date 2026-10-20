# Plan — Feuille de route de la réalisation

- Date : 2026-10-20
- Référence : [cahier des charges](../cahier_des_charges.md), [maquettes validées](../designs/2026-10-20_maquettes-application.md)

L'application est construite par étapes, dans l'ordre conseillé par le sujet (base → pages qui lisent
la base → formulaires → administration → JavaScript et finitions). Pour chaque étape :

1. une spec `docs/specs/2026-10-20_etapeNN-sujet.md` et un plan `docs/plans/2026-10-20_etapeNN-sujet.md`
   (commit `docs:`) ;
2. l'implémentation, testée (commit `feat:` / `test:` / `style:`) ;
3. le push sur `develop`.

| Étape | Sujet | Exigences principales |
|---|---|---|
| 01 | Base de données, données de test, export | `P3-BD-*`, `P3-DT-*`, `G-TECH-1`, `G-TECH-9` |
| 02 | Charte graphique, icônes, gabarits, accueil | `G-TECH-2..4`, maquette écran 1 |
| 03 | Calculs : moyenne coefficientée, rangs ex æquo, appréciations | `P3-RG-1..2`, `P3-BON-2` |
| 04 | Authentification élève / enseignant / administrateur | `P3-PUB-1`, `P3-ADM-1`, `G-TECH-7`, `P3-EXT-5` |
| 05 | Espace élève : bulletin, historique, graphique, impression | `P3-PUB-2..3`, `P3-JS-3`, `P3-API-2`, `P3-BON-1`, `P3-RG-4` |
| 06 | Évaluations, saisie des notes, correction | `P3-EXT-4`, `P3-ADM-2..3`, `P3-JS-1..2`, `P3-RG-3`, `P3-RG-5` |
| 07 | Liste de classe, fiche de notes d'un élève, API moyennes | `P3-ADM-4`, `P3-API-1` |
| 08 | Statistiques et API | `P3-STAT-1..4` |
| 09 | Administration : classes et élèves, export CSV | `P3-EXT-1`, `P3-EXT-2`, `P3-EXT-6` |
| 10 | Import d'élèves CSV / XLSX / XLS / ODS | `P3-EXT-3` |
| 11 | Finitions : validation HTML, accessibilité, README, export, checklist | `G-TECH-3`, `G-LIV-2`, checklist |

## Choix techniques transverses

- `app.py` contient la configuration et toutes les routes (c'est le fichier attendu sur la clé) ;
  deux modules d'appui gardent `app.py` lisible : `calculs.py` (moyennes, rangs) et
  `importation.py` (lecture des fichiers d'élèves).
- Aucune ressource chargée depuis internet : polices (Inter, Manrope, licence OFL) et Chart.js
  (licence MIT) sont copiées dans `static/` ; l'enseignant peut tester hors connexion.
- Icônes : SVG en ligne dessinés au trait (style « Lucide », licence ISC), regroupés dans une macro
  Jinja `icone(nom)`.
- Tests automatiques avec le module standard `unittest` (`python -m unittest`) : pas de dépendance en plus.
