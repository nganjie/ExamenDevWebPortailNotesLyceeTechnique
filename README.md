# Projet 3 : Portail de notes d'un lycée technique

Évaluation finale du cours **Technologies Web et applications** (enseignant : FOTSO T. Valdez W.).

Application Web (HTML, CSS, JavaScript, Flask, SQLite) où les enseignants saisissent les notes
et où chaque élève (ou parent) consulte son bulletin avec son matricule et un code personnel.

## Organisation du dépôt

```
.
├── docs/                 documentation du projet
│   ├── cahier_des_charges.md   récapitulatif de toutes les exigences
│   ├── designs/          maquettes, plan du site, schémas
│   ├── plans/            plans de réalisation (AAAA-MM-JJ_sujet.md)
│   └── specs/            spécifications fonctionnelles et techniques (AAAA-MM-JJ_sujet.md)
├── projet/               l'application Flask (dossier copié tel quel sur la clé USB)
└── captures/             captures d'écran pour le rapport
    ├── ordinateur/
    └── telephone/
```

Les instructions d'installation et de lancement de l'application sont dans
[`projet/README.md`](projet/README.md).

## Méthode de travail

Avant toute implémentation d'une fonctionnalité, on rédige :

1. un fichier dans `docs/specs/` : **ce qui** doit être fait (besoin, règles, critères d'acceptation) ;
2. un fichier dans `docs/plans/` : **comment** on va le faire (étapes, fichiers touchés, tests).

Les deux fichiers portent le même nom, qui commence par la date complète de réalisation
puis décrit le travail, par exemple `2026-10-20_squelette-initial.md`.
Chaque étape fait l'objet d'un commit clair (voir [`docs/README.md`](docs/README.md)).
