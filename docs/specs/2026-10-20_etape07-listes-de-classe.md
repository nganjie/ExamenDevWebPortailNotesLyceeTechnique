# Spec — Étape 07 : listes de classe, fiche de notes d'un élève, API des moyennes

- Date : 2026-10-20
- Exigences couvertes : `P3-ADM-4`, `P3-ADM-3` (accès à la correction), `P3-API-1`, `P3-RG-1..2`, `G-TECH-5`
- Maquette : écran 6

## Besoin

L'enseignant consulte, pour une classe et une séquence, la liste des élèves avec leur moyenne
coefficientée et leur rang (ex æquo compris), ouvre la fiche de notes d'un élève et corrige une note.

## Règles

- Tout enseignant connecté peut consulter les listes de toutes les classes (conseil de classe) ;
  la correction reste limitée aux matières de l'enseignant (ou à l'administrateur).
- Séquence par défaut : la dernière séquence notée de la classe ; séquence hors de 1 à 6 → 404.
- Liste triée par rang ; les trois premiers sont mis en avant ; « ex » signale les ex æquo ;
  moyenne < 10 en rouge ; recherche instantanée par nom ou matricule (JavaScript, sans rechargement).
- Indicateurs : moyenne générale, taux de réussite (≥ 10), effectif / effectif maximal.
- **API** `GET /api/classe/<id>/moyennes?sequence=N` (enseignant connecté, sinon 403 JSON ; classe inconnue → 404 JSON) :
  ```json
  {"classe": {"id": 1, "nom": "1re année F4"}, "sequence": 2, "moyenne_generale": 11.08,
   "taux_reussite": 63.33, "repartition": [{"tranche": "moins de 8", "effectif": 2}, ...],
   "eleves": [{"id": 3, "matricule": "...", "nom": "...", "prenom": "...", "moyenne": 15.2, "rang": 1, "ex_aequo": false}]}
  ```
  La page de liste l'appelle par `fetch` pour dessiner la répartition des moyennes de la classe.
- Fiche élève : mêmes données que le bulletin, avec un lien « Corriger » sur chaque note autorisée ;
  après correction, retour à la fiche.

## Routes

| Adresse | Méthode | Rôle | Gabarit |
|---|---|---|---|
| `/enseignant/classes` | GET | choix d'une classe | `enseignant/classes.html` |
| `/enseignant/classes/<id>` | GET | liste de classe (`?sequence=`) | `enseignant/liste_classe.html` |
| `/enseignant/eleves/<id>` | GET | fiche de notes (`?sequence=`) | `enseignant/fiche_eleve.html` |
| `/api/classe/<id>/moyennes` | GET | moyennes et rangs en JSON | — |

## Critères d'acceptation

- [ ] Les rangs de la liste sont identiques à ceux des bulletins des élèves.
- [ ] L'API renvoie autant d'élèves que la classe en compte, triés par rang.
- [ ] La recherche filtre les lignes sans recharger la page.
