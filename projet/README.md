# Projet 3 : Portail de notes d'un lycée technique

Application Web (HTML, CSS, JavaScript, Flask, SQLite) : les enseignants saisissent les notes de chaque
séquence, les élèves et les parents consultent le bulletin avec le matricule et un code personnel.

## Installation

Python 3.10 ou plus récent est nécessaire.

    python -m venv venv
    venv\Scripts\activate          (Windows)
    source venv/bin/activate       (Linux / macOS)
    pip install -r requirements.txt

## Lancement (la base projet.db est déjà remplie)

    python app.py

puis ouvrir http://127.0.0.1:5000

Le site fonctionne **sans connexion internet** : polices et bibliothèque de graphiques sont fournies dans `static/`.

## Comptes de test

| Profil | Identifiant | Mot de passe / code |
|---|---|---|
| Administrateur (et professeur d'électrotechnique) | `admin` | `Admin!2026` |
| Enseignant de mathématiques | `p.atangana` | `Prof!2026` |
| Autres enseignants | `v.kamga`, `b.ekane`, `s.njoya`, `o.mballa`, `g.tabi`, `a.bello` | `Prof!2026` |
| Élève de 1re année F4 | matricule `LT26-F4-0001` | code `638577` |
| Élève de 2e année F3 | matricule `LT25-F3-0001` | code `337145` |
| Élève de 3e année F2 | matricule `LT24-F2-0001` | code `470392` |
| Élève de 4e année F1 | matricule `LT23-F1-0001` | code `771411` |

Les codes de **tous** les élèves de test sont dans `codes_eleves_test.csv` (fichier de test uniquement :
dans la base, seules les empreintes des codes sont enregistrées).

## Recréer les données de test

    python donnees_test.py

Recrée `projet.db` à partir de `schema.sql` et la remplit (toujours les mêmes données grâce à
`random.seed(42)`) : 8 enseignants, 8 matières, 4 classes, 120 élèves, 72 évaluations et 1 920 notes
(séquences 1 et 2 pour tous les élèves). Compter une quinzaine de secondes (hachage des codes).

## Exporter la base en SQL

    python exporter.py

Produit `export_projet.sql` (toutes les tables et toutes les lignes). Pour recréer la base depuis l'export :

    python -c "import sqlite3; sqlite3.connect('projet.db').executescript(open('export_projet.sql', encoding='utf-8').read())"

## Tests automatiques

    python -m unittest discover -s tests -t .

84 tests (module standard `unittest`) : base et contraintes, calculs (moyennes, rangs ex æquo), connexion et
droits, bulletin, évaluations et saisie, listes de classe, statistiques, administration, import.
Les tests qui modifient des données travaillent sur une copie temporaire de `projet.db`.

## Essayer l'import d'élèves

Le dossier `exemples_import/` contient le même fichier de 10 élèves fictifs en CSV, XLSX et ODS
(avec une date invalide, un prénom manquant et un doublon pour voir les contrôles). Connecté en `admin` :
*Classes* → créer une classe (par ex. « 1re année F3 »), puis *Importer des élèves*.

## Fonctionnalités

**Élève / parent** : connexion (matricule + code), bulletin de chaque séquence (notes, coefficients,
moyenne coefficientée, rang avec ex æquo, moyenne de la classe, appréciations), historique des moyennes,
graphique d'évolution, bulletin imprimable sur une page A4.

**Enseignant** : tableau de bord, évaluations (création, statuts, clôture), saisie des notes de toute une
classe sur une page (note hors de 0 à 20 refusée immédiatement, moyenne de la classe calculée en direct),
correction motivée d'une note avec historique, listes de classe (moyennes, rangs, recherche instantanée),
fiche de notes d'un élève, statistiques.

**Administrateur** : en plus, gestion des classes, des élèves (codes d'accès générés et affichés une seule
fois, export CSV) et import d'élèves depuis un fichier CSV, XLSX, XLS ou ODS.

## Sécurité

- Mots de passe et codes d'accès stockés sous forme d'empreinte (`generate_password_hash`).
- Toutes les saisies sont revérifiées par le serveur ; requêtes SQL toujours paramétrées (`?`).
- Suppressions et modifications uniquement en `POST`, avec un jeton anti-falsification (CSRF).
- Un élève ne voit que son propre bulletin (identité lue dans la session, jamais dans l'adresse).
- Pages réservées par rôle (élève, enseignant, administrateur) ; 5 essais de connexion ratés → blocage 5 minutes.
- Contraintes de la base : `UNIQUE (eleve_id, matiere_id, sequence)` sur les notes, `CHECK` sur les notes (0 à 20)
  et les séquences (1 à 6), clés étrangères activées.
- `debug=False`.

## Structure des fichiers

    projet/
    ├── app.py                 l'application Flask (configuration et routes)
    ├── calculs.py             moyennes coefficientées, rangs ex æquo, statistiques
    ├── importation.py         lecture des fichiers d'élèves (CSV, XLSX, XLS, ODS)
    ├── schema.sql             création des 7 tables
    ├── donnees_test.py        remplit la base de données de test
    ├── exporter.py            export SQL de la base
    ├── projet.db              la base SQLite déjà remplie
    ├── export_projet.sql      export complet de la base
    ├── codes_eleves_test.csv  codes d'accès des élèves de test
    ├── requirements.txt
    ├── exemples_import/       fichiers d'exemple pour l'import
    ├── static/
    │   ├── css/               style.css (mobile d'abord), impression.css
    │   ├── js/                main.js, validation.js, saisie.js, graphique.js, liste_classe.js,
    │   │                      statistiques.js, import.js, vendor/chart.umd.min.js
    │   ├── fonts/             Inter et Manrope (licence OFL)
    │   └── images/            icones.svg, favicon.svg
    ├── templates/             base.html et gabarits Jinja2 (eleve/, enseignant/, admin/)
    └── tests/                 tests automatiques

## Routes

| Adresse | Méthode | Rôle | Accès |
|---|---|---|---|
| `/` | GET | accueil et formulaires de connexion | public |
| `/connexion/eleve` | POST | connexion d'un élève | public |
| `/connexion/enseignant` | POST | connexion d'un enseignant | public |
| `/deconnexion` | POST | déconnexion | connecté |
| `/eleve` | GET | redirige vers le dernier bulletin | élève |
| `/eleve/bulletin/<sequence>` | GET | bulletin d'une séquence | élève |
| `/enseignant` | GET | tableau de bord | enseignant |
| `/enseignant/evaluations` | GET, POST | liste filtrable, création d'une évaluation | enseignant |
| `/enseignant/evaluations/<id>/saisie` | GET, POST | saisie des notes de la classe | enseignant de la matière |
| `/enseignant/evaluations/<id>/cloturer` | POST | clôture | enseignant de la matière |
| `/enseignant/evaluations/<id>/rouvrir` | POST | réouverture | administrateur |
| `/enseignant/evaluations/<id>/supprimer` | POST | suppression (sans notes) | enseignant de la matière |
| `/enseignant/notes/<id>/correction` | GET, POST | correction motivée d'une note | enseignant de la matière |
| `/enseignant/classes` | GET | choix d'une classe | enseignant |
| `/enseignant/classes/<id>` | GET | liste de classe : moyennes et rangs | enseignant |
| `/enseignant/eleves/<id>` | GET | fiche de notes d'un élève | enseignant |
| `/enseignant/statistiques` | GET | statistiques d'une séquence | enseignant |
| `/admin/classes` | GET, POST | liste et création des classes | administrateur |
| `/admin/classes/<id>/modifier` | GET, POST | modification d'une classe | administrateur |
| `/admin/classes/<id>/supprimer` | POST | suppression d'une classe vide | administrateur |
| `/admin/eleves` | GET, POST | liste, recherche et ajout d'élèves | administrateur |
| `/admin/eleves/<id>/modifier` | GET, POST | modification d'un élève | administrateur |
| `/admin/eleves/<id>/nouveau-code` | POST | nouveau code d'accès | administrateur |
| `/admin/eleves/<id>/code-remis` | POST | code remis / à remettre | administrateur |
| `/admin/eleves/<id>/supprimer` | POST | suppression d'un élève | administrateur |
| `/admin/eleves/export.csv` | GET | export CSV des élèves | administrateur |
| `/admin/import` | GET | import : choix du fichier | administrateur |
| `/admin/import/analyse` | POST | import : vérification | administrateur |
| `/admin/import/confirmer` | POST | import : enregistrement | administrateur |
| `/admin/import/codes.csv` | GET | codes d'accès importés (une fois) | administrateur |
| `/admin/import/modele.<csv\|xlsx>` | GET | modèle de fichier | administrateur |
| `/api/eleves/<id>/evolution` | GET | JSON : moyennes par séquence | l'élève lui-même ou enseignant |
| `/api/classe/<id>/moyennes` | GET | JSON : moyennes et rangs d'une classe | enseignant |
| `/api/statistiques` | GET | JSON : statistiques d'une séquence | enseignant |

## Ressources tierces (déclarées)

- Polices **Inter** et **Manrope** — SIL Open Font License (`static/fonts/LICENCE-*.txt`).
- **Chart.js 4.4.6** — licence MIT (`static/js/vendor/LICENCE-Chartjs-MIT.md`).
- Icônes dessinées au trait dans le style **Lucide** (licence ISC).
- Aucun modèle de site n'a été utilisé : les maquettes sont dans `docs/designs/` du dépôt.
