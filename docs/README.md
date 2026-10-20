# Documentation du projet

| Dossier / fichier | Rôle |
|---|---|
| [`cahier_des_charges.md`](cahier_des_charges.md) | récapitulatif de **toutes** les exigences du sujet (référence unique) |
| [`designs/`](designs/) | plan du site, maquettes (téléphone et ordinateur), schéma de la base, charte graphique |
| [`specs/`](specs/) | **ce qui** doit être fait : besoin, règles, routes, critères d'acceptation |
| [`plans/`](plans/) | **comment** on le fait : étapes, fichiers touchés, tests à réaliser |

## Règles de travail

1. **Pas d'implémentation sans spec ni plan.** Avant toute nouvelle fonctionnalité, on crée un fichier
   dans `specs/` **et** un fichier dans `plans/`.
2. **Nommage :** `AAAA-MM-JJ_sujet-du-travail.md` — la date complète de réalisation, un tiret bas, puis
   le sujet en minuscules, sans accents ni espaces (mots séparés par des tirets).
   Exemple : `2026-10-20_squelette-initial.md`. La spec et le plan d'un même travail portent le même nom.
3. Chaque spec cite les identifiants d'exigences (`G-…`, `P3-…`) du cahier des charges qu'elle couvre,
   et la matrice de suivi du cahier des charges est mise à jour.
4. **Commits clairs à chaque étape**, au format `type: description` :
   - `docs:` documentation (spec, plan, design) ;
   - `feat:` nouvelle fonctionnalité ;
   - `fix:` correction ;
   - `style:` CSS / présentation ;
   - `test:` tests et données de test ;
   - `chore:` configuration, outillage.
5. **Branches :** `main` pour les versions stables, `develop` pour l'intégration,
   `feature/<sujet>` pour chaque fonctionnalité.
