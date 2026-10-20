# Cahier des charges — Projet 3 : Portail de notes d'un lycée technique

> Récapitulatif complet des exigences tirées du document *« Évaluation finale — Projets Web »*
> (FOTSO T. Valdez W., matière Technologies Web et applications).
> Il réunit les **consignes générales** (chapitres 1 et 2, valables pour tous les projets)
> et les **exigences propres au projet 3** (chapitre 3, pages 17-18).
>
> Chaque exigence porte un identifiant (`G-…` générale, `P3-…` projet 3) pour être citée
> dans les fichiers de `docs/specs/` et `docs/plans/` et cochée au fur et à mesure.

---

## Sommaire

1. [Le sujet en bref](#1-le-sujet-en-bref)
2. [Acteurs et droits](#2-acteurs-et-droits)
3. [Base de données attendue](#3-base-de-données-attendue)
4. [Fonctionnalités](#4-fonctionnalités)
5. [Statistiques attendues](#5-statistiques-attendues)
6. [Règles métier critiques](#6-règles-métier-critiques)
7. [Bonus](#7-bonus) et [extensions demandées par le groupe](#7-bis-extensions-demandées-par-le-groupe-au-delà-du-sujet)
8. [Exigences techniques communes](#8-exigences-techniques-communes)
9. [Livrables](#9-livrables)
10. [Clé USB et arborescence](#10-clé-usb-et-arborescence)
11. [Rapport PowerPoint](#11-rapport-powerpoint)
12. [Vidéo](#12-vidéo)
13. [Exposé](#13-exposé)
14. [Barème et pénalités](#14-barème-et-pénalités)
15. [Méthode et outils imposés](#15-méthode-et-outils-imposés)
16. [Checklist avant la remise](#16-checklist-avant-la-remise)
17. [Points à préciser / hypothèses de conception](#17-points-à-préciser--hypothèses-de-conception)
18. [Matrice de suivi](#18-matrice-de-suivi)

---

## 1. Le sujet en bref

**Domaine :** Éducation.

**Contexte :** un lycée technique calcule les moyennes à la main sur des feuilles de calcul, et
les parents doivent se déplacer pour connaître les résultats. Le proviseur veut un **portail** où :

- les **enseignants** saisissent les notes ;
- chaque **élève (ou parent)** consulte son **bulletin** avec son **matricule** et un **code personnel**.

**Pile imposée :** HTML5, CSS, JavaScript, Python 3 + Flask, SQLite (module `sqlite3`), gabarits Jinja2.

---

## 2. Acteurs et droits

| Acteur | Connexion | Ce qu'il peut faire |
|---|---|---|
| Visiteur (non connecté) | aucune | voir l'accueil, accéder aux pages de connexion ; aucune note visible |
| Élève / parent | matricule + code d'accès | voir **uniquement son propre** bulletin, son historique et le graphique de son évolution |
| Enseignant | login + mot de passe | saisir les notes d'une matière pour une classe entière, corriger une note, voir la liste de classe avec moyennes et rangs, consulter les statistiques |

- `P3-ACT-1` Un élève ne voit **que son propre bulletin** (contrôle côté serveur, pas seulement masquage).
- `P3-ACT-2` L'espace enseignant (administration) est **refusé sans connexion**.

---

## 3. Base de données attendue

Tables et colonnes **minimales** (on peut en ajouter si la conception le justifie) :

| Table | Colonnes minimales | Contraintes attendues / déduites |
|---|---|---|
| `classes` | nom (ex. « 2e année F3 »), filière, effectif maximal | nom `UNIQUE NOT NULL` ; `CHECK (effectif_max > 0)` |
| `eleves` | matricule, nom, prénom, classe, date de naissance, code d'accès (**empreinte**) | matricule `UNIQUE NOT NULL` ; `classe_id` → `classes` ; code stocké haché |
| `matieres` | nom, coefficient, enseignant | `CHECK (coefficient > 0)` ; `enseignant_id` → `enseignants` |
| `notes` | élève, matière, séquence (1 à 6), note sur 20 | `CHECK (sequence BETWEEN 1 AND 6)` ; `CHECK (note BETWEEN 0 AND 20)` ; **`UNIQUE (eleve_id, matiere_id, sequence)`** |
| `enseignants` | nom, login, empreinte du mot de passe | login `UNIQUE NOT NULL` ; mot de passe haché |

- `P3-BD-1` Les 5 tables ci-dessus existent avec au minimum ces colonnes.
- `P3-BD-2` Clés étrangères : `eleves → classes`, `matieres → enseignants`, `notes → eleves`, `notes → matieres`
  (au moins 3 tables liées par clés étrangères — exigence `G-TECH-1`).
- `P3-BD-3` Contraintes `NOT NULL`, `UNIQUE`, `CHECK` présentes (matricule, login, séquence, note, unicité de la note).
- `P3-BD-4` Le code d'accès élève et le mot de passe enseignant sont stockés sous forme d'**empreinte**
  (`generate_password_hash`), jamais en clair.
- `P3-BD-5` Activer `PRAGMA foreign_keys = ON` à chaque connexion (sinon SQLite ignore les clés étrangères).

---

## 4. Fonctionnalités

### 4.1 Données de test (volumes minimum) — script `donnees_test.py`

- `P3-DT-1` **4 classes**.
- `P3-DT-2` **120 élèves** (soit 30 par classe en moyenne, sans dépasser l'effectif maximal).
- `P3-DT-3` **8 matières** avec coefficients.
- `P3-DT-4` Les notes de **2 séquences pour tous** les élèves (≈ 120 × 8 × 2 = **1 920 notes**).
- `P3-DT-5` Au moins un **compte enseignant de test** dont les identifiants figurent dans le README
  (et des élèves de test avec matricule + code connus).
- `P3-DT-6` Données réalistes (noms camerounais, filières techniques F1, F2, F3, F4, G…), `random.seed(42)`
  pour la reproductibilité.

### 4.2 Partie publique (élève / parent)

- `P3-PUB-1` **Connexion élève** avec matricule et code d'accès.
- `P3-PUB-2` **Bulletin de la séquence** : notes par matière, **moyenne coefficientée**, **rang dans la classe**.
- `P3-PUB-3` **Historique des moyennes par séquence**.

### 4.3 Espace d'administration (enseignant, connexion obligatoire)

- `P3-ADM-1` **Connexion enseignant** (login + mot de passe haché).
- `P3-ADM-2` **Saisie des notes d'une matière pour toute une classe sur une seule page**.
- `P3-ADM-3` **Correction d'une note** (en POST).
- `P3-ADM-4` **Liste de classe avec moyennes et rangs**.

### 4.4 JavaScript et API JSON

- `P3-JS-1` Pendant la saisie, **refus immédiat** d'une note hors de **0 à 20**.
- `P3-JS-2` **Calcul en direct de la moyenne de la classe** pendant la saisie.
- `P3-API-1` Route **`/api/classe/<id>/moyennes`** renvoyant du JSON (`jsonify`).
- `P3-JS-3` **Graphique de l'évolution d'un élève** (bibliothèque au choix, ex. Chart.js), alimenté par `fetch`.
- `P3-API-2` Au moins **une deuxième route JSON** (exigence `G-TECH-6`), par ex. `/api/eleve/<id>/evolution`
  ou `/api/statistiques`.

---

## 5. Statistiques attendues

- `P3-STAT-1` **Moyenne générale** et **taux de réussite** (moyenne ≥ 10) **par classe**.
- `P3-STAT-2` **Moyenne de chaque matière par classe**.
- `P3-STAT-3` Les **3 premiers de chaque classe**.
- `P3-STAT-4` **Répartition des moyennes par tranches** : moins de 8, 8 à 10, 10 à 12, 12 à 14, plus de 14.

> Les bornes des tranches doivent être fixées clairement (proposition : `[0;8[`, `[8;10[`, `[10;12[`,
> `[12;14[`, `[14;20]`) et documentées dans la spec des statistiques.

---

## 6. Règles métier critiques (« Ce que j'attends de vous »)

- `P3-RG-1` **Moyenne coefficientée juste** : `moyenne = Σ(note × coefficient) / Σ(coefficients)`.
- `P3-RG-2` **Rang juste avec gestion des ex æquo** : deux élèves à 12,50 ont le **même rang**, le suivant
  prend le rang d'après (classement « 1, 2, 2, 4 »).
- `P3-RG-3` **Une note ne peut être saisie deux fois** pour le même élève, la même matière et la même séquence
  → contrainte `UNIQUE (eleve_id, matiere_id, sequence)` dans la base (la vraie protection).
- `P3-RG-4` **Un élève ne voit que son propre bulletin** (l'identifiant vient de la session, jamais de l'URL
  sans vérification).
- `P3-RG-5` Toute note est revérifiée côté serveur (0 ≤ note ≤ 20, séquence 1 à 6), le JavaScript n'étant qu'un confort.

---

## 7. Bonus (« Pour aller plus loin »)

- `P3-BON-1` **Bulletin imprimable proprement** (feuille de style `@media print`).
- `P3-BON-2` **Appréciation automatique** selon la moyenne (ex. < 8 « Insuffisant », 8-10 « Médiocre »,
  10-12 « Passable », 12-14 « Assez bien », 14-16 « Bien », ≥ 16 « Très bien »).

### 7 bis. Extensions demandées par le groupe (au-delà du sujet)

Ajoutées le 2026-10-20. Elles ne remplacent aucune exigence du sujet ; elles complètent l'espace enseignant.

- `P3-EXT-1` **Gestion des classes** : ajouter, modifier une classe (nom unique, niveau, filière,
  effectif maximal, professeur principal). Une classe contenant des élèves ne se supprime pas ;
  son effectif maximal ne descend pas sous l'effectif actuel.
- `P3-EXT-2` **Ajout d'un élève dans une classe** : nom, prénom, date de naissance, classe, matricule
  proposé automatiquement (unique). Un **code d'accès est généré**, affiché **une seule fois**, et seule
  son empreinte est enregistrée. Possibilité de générer un nouveau code.
- `P3-EXT-3` **Import d'élèves depuis un fichier** **CSV, XLSX, XLS ou ODS** (2 Mo max) :
  choix de la classe → analyse → correspondance des colonnes → aperçu avec erreurs ligne par ligne
  (champ manquant, date invalide, matricule en doublon, effectif maximal dépassé) → import des lignes
  valides → liste des codes d'accès téléchargeable une fois + rapport d'import. Modèles `.csv` / `.xlsx`
  téléchargeables. Tout est revérifié côté serveur (`G-TECH-8`).
- `P3-EXT-4` **Évaluations** : créer une évaluation (intitulé, classe, matière, séquence, date) ;
  statuts *Planifiée*, *À saisir*, *En cours*, *Complète*, *Clôturée* ; la saisie des notes
  (`P3-ADM-2`) se fait à partir d'une évaluation. Une évaluation clôturée ne se modifie plus que par
  une correction motivée (`P3-ADM-3`).
- `P3-EXT-5` **Rôle administrateur** : les pages *Classes*, *Élèves* et *Import* sont réservées aux
  comptes ayant le rôle `administrateur` (contrôle côté serveur) ; un enseignant ne crée des
  évaluations et ne saisit des notes que pour ses propres matières.
- `P3-EXT-6` **Export CSV** de la liste des élèves d'une classe.

Conséquences techniques à prévoir :

- table `evaluations` (`classe_id`, `matiere_id`, `sequence`, `intitule`, `date`, `statut`) avec
  `UNIQUE (classe_id, matiere_id, sequence)` : une évaluation = la note de séquence, ce qui garde
  la règle `P3-RG-3` (`UNIQUE (eleve_id, matiere_id, sequence)` sur `notes`) ;
- colonne `role` dans `enseignants` (`CHECK (role IN ('enseignant', 'administrateur'))`) et
  `niveau`, `professeur_principal_id` dans `classes` ;
- bibliothèques Python : `openpyxl` (XLSX), `xlrd` (XLS), `odfpy` ou `pandas` (ODS) ; le CSV utilise
  le module standard `csv` (séparateurs `,` et `;`, encodage UTF-8 et Windows-1252) ;
- ces bibliothèques s'ajoutent à `requirements.txt` (le README reste valable).

---

## 8. Exigences techniques communes (minimum obligatoire)

| Id | Exigence |
|---|---|
| `G-TECH-1` | **Serveur** : Python 3, Flask, SQLite (`sqlite3`). Au moins **3 tables liées par clés étrangères**, avec contraintes `NOT NULL`, `UNIQUE`, `CHECK`. |
| `G-TECH-2` | **Gabarits** : un `base.html` dont **héritent toutes les pages** ; **messages flash** ; **page d'erreur 404 personnalisée**. |
| `G-TECH-3` | **HTML** : balises sémantiques, un `alt` sur chaque image, un `label` sur chaque champ, pages principales **validées par le validateur du W3C**. |
| `G-TECH-4` | **CSS** : dans des **fichiers séparés**, démarche **mobile d'abord**, **au moins deux points de rupture** ; site confortable sur téléphone. |
| `G-TECH-5` | **JavaScript** : vérification d'**au moins un formulaire** avant l'envoi, et **au moins une fonctionnalité utilisant `fetch`** sur une route de l'API. |
| `G-TECH-6` | **API** : **au moins deux routes** qui renvoient du JSON (`jsonify`). |
| `G-TECH-7` | **Administration protégée** par une connexion ; mots de passe stockés en **empreinte** (`generate_password_hash`) ; décorateur `connexion_requise` (exercice 29 du polycopié). |
| `G-TECH-8` | **Sécurité** : toutes les données **revérifiées sur le serveur**, requêtes SQL **toujours paramétrées (`?`)**, **suppressions et modifications uniquement en POST**, **`debug=False`** dans la version rendue. |
| `G-TECH-9` | **Données de test** : script `donnees_test.py` qui remplit la base au moins avec les volumes du sujet. |
| `G-TECH-10` | **Code commenté en français**, fonctions aux noms clairs. |

Bonnes pratiques complémentaires déduites :

- échapper tout contenu affiché (Jinja2 échappe par défaut : ne pas utiliser `|safe` ; en JS préférer `textContent` à `innerHTML`) ;
- clé secrète Flask (`SECRET_KEY`) pour les sessions et les messages flash ;
- noms de fichiers sans espaces, accents ni caractères spéciaux, casse cohérente (`logo.png` ≠ `Logo.png`).

---

## 9. Livrables

| # | Élément | Contenu attendu |
|---|---|---|
| `G-LIV-1` | **Rapport PowerPoint** | Présentation du sujet, de la conception, des réalisations avec captures. 1re diapositive : **liste des membres**. |
| `G-LIV-2` | **Projet testable** | Code complet (Flask, gabarits, CSS, JS), base SQLite **remplie**, son **export SQL**, `README.md` d'installation, `requirements.txt`. L'enseignant doit pouvoir lancer le site **en suivant uniquement le README**. |
| `G-LIV-3` | **Captures d'écran** | Celles du rapport, sur **ordinateur** et sur **téléphone**, rangées dans un dossier. |
| `G-LIV-4` | **Vidéo** | 5 à 10 minutes, présente le projet et montre le site en fonctionnement. |

---

## 10. Clé USB et arborescence

- `G-USB-1` Clé **fonctionnelle** et **analysée par un antivirus** (clé infectée ou illisible refusée).
- `G-USB-2` Clé **renommée avec le nom du groupe** (ex. `Groupe03`).
- `G-USB-3` À la racine : **un seul dossier** au format `Filière-Niveau-NomGroupe` (ex. `GI-5-Groupe03`).
- `G-USB-4` **Ne pas copier le dossier `venv`**.
- `G-USB-5` Respecter **exactement** l'arborescence :

```
Groupe03                      <- nom de la clé USB
`-- GI-5-Groupe03/            <- Filière-Niveau-NomGroupe
    +-- rapport_Groupe03.pptx
    +-- video_demo.mp4
    +-- projet/
    |   +-- README.md         <- installation, lancement, comptes de test
    |   +-- requirements.txt  <- flask (pip freeze > requirements.txt)
    |   +-- app.py            <- l'application Flask
    |   +-- schema.sql        <- création des tables
    |   +-- donnees_test.py   <- remplit la base de données de test
    |   +-- projet.db         <- la base SQLite déjà remplie
    |   +-- export_projet.sql <- export complet de la base
    |   +-- static/
    |   |   +-- css/
    |   |   +-- js/
    |   |   `-- images/
    |   `-- templates/        <- les gabarits Jinja2
    `-- captures/
        +-- ordinateur/
        `-- telephone/
```

> Dans ce dépôt, `projet/` et `captures/` reproduisent déjà cette organisation : il suffira de les copier
> dans le dossier `Filière-Niveau-NomGroupe` avec le rapport et la vidéo.

---

## 11. Rapport PowerPoint (15 à 25 diapositives)

Doit pouvoir être **lu seul**, sans explication orale ; sert aussi de support à l'exposé.

| Diapo(s) | Contenu |
|---|---|
| 1. Page de garde | Titre et numéro du projet, nom du groupe, filière et niveau, matière, enseignant, **liste des membres** (nom, prénom, matricule, rôle). |
| 2. Contexte | Le problème à résoudre, avec nos mots. |
| 3. Objectifs | Ce que l'application permet de faire, et pour qui (élève/parent, enseignant). |
| 4. Plan du site | Schéma des pages et des liens. |
| 5-6. Base de données | Schéma des tables et liens, contraintes importantes (clés, `UNIQUE`, `CHECK`). |
| 7. Routes | Tableau des routes Flask : adresse, méthode, rôle. |
| 8-13. Réalisations | Pour chaque fonctionnalité importante : capture + extrait de code significatif si utile. |
| 14. Adaptatif | Mêmes pages sur téléphone et sur ordinateur. |
| 15. JavaScript et API | Vérification des formulaires et appel `fetch`, avec captures. |
| 16. Sécurité | Vérifications serveur, requêtes paramétrées, mots de passe hachés, suppressions en POST, **démonstration d'une saisie refusée**. |
| 17. Validation | Capture du **validateur W3C sans erreur** sur les pages principales. |
| 18. Difficultés | Problèmes rencontrés et solutions. |
| 19. Répartition du travail | Qui a fait quoi. |
| 20. Conclusion | Bilan, limites, améliorations possibles. |

- Captures **lisibles**, recadrées, accompagnées d'une phrase explicative ; pas de diapositives surchargées.

---

## 12. Vidéo

- `G-VID-1` Durée **5 à 10 minutes**, format **MP4**, **720p minimum**, son clair.
- `G-VID-2` Déroulé conseillé : présentation (1 min) ; parcours comme élève/parent puis comme enseignant (3-5 min) ;
  **démonstration d'une saisie refusée** et de l'**affichage sur téléphone** (1-2 min) ; explication d'un extrait de
  code (1-2 min) ; conclusion (30 s).
- `G-VID-3` **Plusieurs membres** du groupe prennent la parole.
- Outil : OBS Studio ou l'enregistreur intégré au système.

---

## 13. Exposé

- Présentation devant la classe à la date fixée, **tenue correcte**.
- **Démonstration en direct**.
- **Chaque membre** doit savoir lancer le site, expliquer une route, un gabarit, une règle CSS ou une fonction JS,
  et répondre aux questions sur **n'importe quelle partie** du projet.
- Note de groupe **ajustable individuellement**.

---

## 14. Barème et pénalités

| Critère | Points |
|---|---|
| Conception : plan du site, base de données, routes (cohérence et justification) | 3 |
| Fonctionnement côté serveur : toutes les fonctionnalités demandées marchent | 5 |
| Front-end : HTML valide et sémantique, CSS soigné et adaptatif, accessibilité | 3 |
| JavaScript : vérification des formulaires, `fetch` et API | 2 |
| Sécurité : vérifications serveur, requêtes paramétrées, connexion, mots de passe hachés | 2 |
| Rapport PowerPoint (structure, clarté, captures lisibles) | 2 |
| Projet testable (README, données de test, export) et arborescence de la clé | 1 |
| Vidéo explicative | 1 |
| Exposé et réponses individuelles | 1 |
| **Total** | **20** |

**Pénalités :**

- clé non conforme ou arborescence non respectée : jusqu'à **−2 points** ;
- projet qui ne démarre pas en suivant le README : jusqu'à **−3 points** ;
- rendu en retard : **−1 point par jour** ;
- code ou rapport copié, ou modèle de site récupéré **sans le déclarer** : **note nulle**.

---

## 15. Méthode et outils imposés

### 15.1 Étapes du projet

1. Comprendre le sujet (acteurs et actions).
2. Dessiner le plan du site et une maquette de chaque page (téléphone et ordinateur) → `docs/designs/`.
3. Concevoir la base, écrire `schema.sql`.
4. Lister les routes : adresse, méthode, rôle, gabarit.
5. Répartir le travail (base + données de test / gabarits + CSS / routes / JS + API), relecture croisée.
6. Construire par étapes : pages publiques en lecture → formulaires → administration → JavaScript et finitions.
7. Tester : formulaires (saisies correctes **et** fausses), chaque page sur téléphone, chaque page au validateur.
8. Préparer le rendu : export, captures, rapport, vidéo, répétition de l'exposé.

### 15.2 Outils fournis

- **`donnees_test.py`** : exécute `schema.sql`, remplit d'abord les tables indépendantes (classes, enseignants,
  matières) puis les dépendantes (élèves, notes), `random.seed(42)`, intercepte `sqlite3.IntegrityError` pour
  laisser la base faire respecter les règles, affiche le nombre de lignes par table.
- **Compte de test** créé dans `donnees_test.py` avec `generate_password_hash`, identifiants dans le README
  (exemple du document : `admin` / `Admin!2026`).
- **`exporter.py`** : `db.iterdump()` → `export_projet.sql` ; recréation via `db.executescript(...)`.
- **`README.md` du projet** : installation (`python -m venv venv`, activation, `pip install -r requirements.txt`),
  lancement (`python app.py` → http://127.0.0.1:5000), recréation des données, comptes de test.
  À **tester sur un autre ordinateur** à partir d'une copie de la clé.

---

## 16. Checklist avant la remise

- [ ] Le site se lance sur un autre ordinateur en suivant uniquement le `README.md`.
- [ ] Chaque table contient au moins le nombre de lignes demandé.
- [ ] Toutes les fonctionnalités du sujet sont présentes et fonctionnent, y compris les cas d'erreur.
- [ ] Les pages principales passent le validateur du W3C.
- [ ] Le site est confortable sur téléphone (captures dans `captures/telephone`).
- [ ] L'espace d'administration refuse l'accès sans connexion.
- [ ] `debug=False` dans `app.py` ; aucun dossier `venv` sur la clé.
- [ ] La première diapositive contient la liste complète des membres du groupe.
- [ ] La vidéo dure entre 5 et 10 minutes et le son est audible.
- [ ] La clé porte le nom du groupe, le dossier suit le format `Filière-Niveau-NomGroupe`, la clé est passée à l'antivirus.

---

## 17. Points à préciser / hypothèses de conception

Le sujet laisse certains choix ouverts ; ils seront tranchés et justifiés dans les specs correspondantes :

| # | Question | Hypothèse proposée |
|---|---|---|
| H1 | Toutes les classes suivent-elles les mêmes 8 matières ? | Oui au départ (8 matières communes) ; une table d'association `classes_matieres` pourra être ajoutée si besoin. |
| H2 | Un enseignant enseigne-t-il une ou plusieurs matières ? | `matieres.enseignant_id` : une matière a un enseignant, un enseignant peut avoir plusieurs matières. |
| H3 | Un enseignant peut-il saisir les notes de n'importe quelle matière ? | Non : seulement celles des matières dont il est responsable (contrôle serveur). |
| H4 | Comment traiter une note manquante dans le calcul de la moyenne ? | La matière est exclue du numérateur **et** du dénominateur ; le bulletin signale « non noté ». |
| H5 | Arrondi des moyennes ? | Calcul en pleine précision, affichage à 2 décimales ; le rang est calculé sur la valeur arrondie à 2 décimales pour que deux « 12,50 » soient bien ex æquo. |
| H6 | Rang : par séquence ou annuel ? | Par séquence (bulletin de séquence) ; l'historique montre la moyenne de chaque séquence. |
| H7 | Qui fournit le code d'accès à l'élève/parent ? | Généré par l'administration (données de test : code connu, listé dans le README pour quelques élèves). |
| H8 | Respect de l'effectif maximal ? | Vérifié côté serveur (et dans `donnees_test.py`) lors de l'ajout d'un élève à une classe. |
| H9 | Rôle « proviseur / administrateur » distinct ? | Oui depuis les extensions : champ `role` (`enseignant` / `administrateur`) dans `enseignants` (voir `P3-EXT-5`). |
| H10 | Plusieurs évaluations par séquence et par matière ? | Non : une évaluation par classe, matière et séquence, qui donne la note de séquence. Alternative à discuter : plusieurs évaluations dont la moyenne donne la note de séquence (le calcul se complique). |

---

## 18. Matrice de suivi

| Id | Exigence (résumé) | Spec | Statut |
|---|---|---|---|
| `G-TECH-*` | Exigences techniques communes | — | à faire |
| `P3-BD-1..5` | Schéma de base et contraintes | — | à faire |
| `P3-DT-1..6` | Données de test | — | à faire |
| `P3-PUB-1` | Connexion élève | — | à faire |
| `P3-PUB-2` | Bulletin de séquence (moyenne, rang) | — | à faire |
| `P3-PUB-3` | Historique des moyennes | — | à faire |
| `P3-ADM-1` | Connexion enseignant | — | à faire |
| `P3-ADM-2` | Saisie des notes par classe | — | à faire |
| `P3-ADM-3` | Correction d'une note | — | à faire |
| `P3-ADM-4` | Liste de classe avec moyennes et rangs | — | à faire |
| `P3-JS-1..2` | Contrôle 0-20 et moyenne en direct | — | à faire |
| `P3-JS-3` | Graphique d'évolution | — | à faire |
| `P3-API-1..2` | Routes JSON | — | à faire |
| `P3-STAT-1..4` | Statistiques | — | à faire |
| `P3-RG-1..5` | Règles métier (moyenne, rang, unicité, confidentialité) | — | à faire |
| `P3-BON-1..2` | Bonus impression et appréciation | — | optionnel |
| `P3-EXT-1` | Gestion des classes | — | maquette faite |
| `P3-EXT-2` | Ajout d'un élève + code d'accès | — | maquette faite |
| `P3-EXT-3` | Import CSV / XLSX / XLS / ODS | — | maquette faite |
| `P3-EXT-4` | Évaluations | — | maquette faite |
| `P3-EXT-5` | Rôle administrateur | — | à faire |
| `P3-EXT-6` | Export CSV des élèves | — | maquette faite |
| Squelette | Structure initiale de l'application | [`2026-10-20_squelette-initial`](specs/2026-10-20_squelette-initial.md) | fait |
