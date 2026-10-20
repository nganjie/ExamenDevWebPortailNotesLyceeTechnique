# Spec — Squelette initial de l'application

- Date : 2026-10-20
- Exigences couvertes : `G-USB-5` (arborescence), `G-TECH-2` (base.html, flash, 404),
  `G-TECH-4` (CSS séparé, mobile d'abord, 2 points de rupture), `G-TECH-8` (`debug=False`),
  `G-TECH-10` (commentaires en français), `G-LIV-2` (README, requirements.txt)

## Besoin

Mettre en place la structure de départ du projet, sans fonctionnalité métier, pour que chaque membre
du groupe puisse ensuite travailler dans le bon dossier.

## Règles et contraintes

- `projet/` respecte exactement l'arborescence imposée pour la clé USB : `README.md`, `requirements.txt`,
  `app.py`, `schema.sql`, `donnees_test.py`, `exporter.py`, `static/css`, `static/js`, `static/images`,
  `templates/`.
- `captures/ordinateur` et `captures/telephone` existent.
- `app.py` démarre avec `python app.py`, sert une page d'accueil et une page 404 personnalisée, avec
  `debug=False`.
- Toutes les pages héritent de `templates/base.html` qui affiche les messages flash.
- Le CSS est dans des fichiers séparés, écrit « mobile d'abord » avec deux points de rupture
  (≥ 600 px tablette, ≥ 1024 px ordinateur).
- `schema.sql`, `donnees_test.py` et `exporter.py` sont présents mais leur contenu métier sera défini
  par des specs ultérieures (base de données, données de test).

## Hors périmètre

Tables, connexion élève/enseignant, bulletins, saisie de notes, API, statistiques.

## Critères d'acceptation

- [ ] `pip install -r requirements.txt` puis `python app.py` affiche l'accueil sur http://127.0.0.1:5000.
- [ ] Une adresse inexistante renvoie la page 404 personnalisée avec le code HTTP 404.
- [ ] Le HTML de l'accueil et de la 404 est sémantique (`header`, `nav`, `main`, `footer`).
- [ ] Aucun dossier `venv` n'est versionné.
