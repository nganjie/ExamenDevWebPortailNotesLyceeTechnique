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

Les instructions d'installation, de lancement, les comptes de test et le tableau des routes sont dans
[`projet/README.md`](projet/README.md).

## État d'avancement

L'application est complète : les 11 étapes de la [feuille de route](docs/plans/2026-10-20_feuille-de-route.md)
sont réalisées, chacune avec sa spec et son plan. La [matrice de suivi](docs/cahier_des_charges.md#18-matrice-de-suivi)
indique ce qui reste à faire par le groupe : rapport PowerPoint, vidéo et préparation de la clé USB.

## Méthode de travail

Avant toute implémentation d'une fonctionnalité, on rédige :

1. un fichier dans `docs/specs/` : **ce qui** doit être fait (besoin, règles, critères d'acceptation) ;
2. un fichier dans `docs/plans/` : **comment** on va le faire (étapes, fichiers touchés, tests).

Les deux fichiers portent le même nom, qui commence par la date complète de réalisation
puis décrit le travail, par exemple `2026-10-20_squelette-initial.md`.
Chaque étape fait l'objet d'un commit clair (voir [`docs/README.md`](docs/README.md)).
