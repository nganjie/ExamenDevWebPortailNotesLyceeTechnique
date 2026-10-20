# Plan — Étape 01 : base de données et données de test

- Date : 2026-10-20
- Spec : [../specs/2026-10-20_etape01-base-de-donnees.md](../specs/2026-10-20_etape01-base-de-donnees.md)

## Étapes

1. Écrire `schema.sql` : `DROP TABLE IF EXISTS` (ordre inverse des dépendances), puis `CREATE TABLE`
   avec clés étrangères et contraintes, puis index utiles (`eleves.classe_id`, `notes.eleve_id`).
2. Écrire `donnees_test.py` :
   - listes de noms, prénoms, filières ;
   - `creer_enseignants`, `creer_matieres`, `creer_classes`, `creer_eleves`, `creer_evaluations`,
     `creer_notes` (tables indépendantes d'abord) ;
   - `generate_password_hash` pour les mots de passe et les codes d'accès ;
   - écriture de `codes_eleves_test.csv` ; affichage des volumes.
3. Garder `exporter.py` (déjà conforme au modèle du sujet).
4. Ajouter un test `tests/test_base.py` qui vérifie volumes et contraintes sur une base temporaire.
5. Générer `projet.db` et `export_projet.sql`.

## Fichiers créés / modifiés

- `projet/schema.sql`, `projet/donnees_test.py`, `projet/tests/__init__.py`, `projet/tests/test_base.py`
- `projet/projet.db`, `projet/export_projet.sql`, `projet/codes_eleves_test.csv` (générés)

## Tests à réaliser

- `python donnees_test.py` puis `python -m unittest discover tests`.
- Insertion manuelle d'un doublon de note → `IntegrityError`.

## Commits prévus

1. `docs: spec et plan de l'étape 01 (base de données)` (+ feuille de route)
2. `feat: schéma SQLite et données de test (étape 01)`
