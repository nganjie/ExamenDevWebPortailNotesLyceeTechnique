# Plan — Squelette initial de l'application

- Date : 2026-10-20
- Spec : [../specs/2026-10-20_squelette-initial.md](../specs/2026-10-20_squelette-initial.md)

## Étapes

1. Créer l'arborescence `projet/` et `captures/` (fichiers `.gitkeep` pour les dossiers vides).
2. Écrire `requirements.txt` (Flask) et le `README.md` d'installation du projet.
3. Écrire `app.py` : création de l'application, clé secrète, connexion SQLite (`get_db` / `close_db`
   avec `PRAGMA foreign_keys = ON`), décorateur `connexion_requise` (à brancher plus tard),
   route `/`, gestionnaire d'erreur 404, `app.run(debug=False)`.
4. Écrire les gabarits `base.html`, `index.html`, `404.html`.
5. Écrire `static/css/style.css` (mobile d'abord, 2 points de rupture) et `static/js/main.js`.
6. Créer `schema.sql`, `donnees_test.py`, `exporter.py` en version minimale commentée.
7. Tester le lancement et la 404.

## Fichiers créés

```
projet/
├── README.md
├── requirements.txt
├── app.py
├── schema.sql
├── donnees_test.py
├── exporter.py
├── static/{css/style.css, js/main.js, images/}
└── templates/{base.html, index.html, 404.html, eleve/, enseignant/}
captures/{ordinateur/, telephone/}
```

## Tests à réaliser

- `python app.py` → accueil en 200 ; `/inexistant` → 404 personnalisée.
- Vérification visuelle sur largeur téléphone et ordinateur.

## Commits prévus

1. `docs: spec et plan du squelette initial`
2. `feat: squelette de l'application Flask (arborescence, gabarits, CSS, JS)`
