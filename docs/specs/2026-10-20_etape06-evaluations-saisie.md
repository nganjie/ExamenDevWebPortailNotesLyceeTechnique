# Spec — Étape 06 : évaluations, saisie et correction des notes

- Date : 2026-10-20
- Exigences couvertes : `P3-EXT-4`, `P3-ADM-2`, `P3-ADM-3`, `P3-JS-1`, `P3-JS-2`, `P3-RG-3`, `P3-RG-5`,
  `P3-EXT-5` (droits), `G-TECH-5`, `G-TECH-8`
- Maquettes : écrans 5 (saisie) et 11 (évaluations), panneau de correction de l'écran 6

## Règles métier

- **Droits** : un enseignant ne voit et ne gère que les évaluations de **ses** matières ; l'administrateur
  voit et gère toutes les évaluations.
- **Création** d'une évaluation : classe, matière, séquence (1 à 6), intitulé (3 à 80 caractères), date valide.
  Une seule évaluation par classe, matière et séquence (contrainte `UNIQUE` → message clair).
- **Statuts affichés** : Planifiée (date future, aucune note), À saisir, En cours, Complète, Clôturée.
- **Suppression** (POST) d'une évaluation possible seulement si aucune note n'a été saisie.
- **Saisie** : une seule page pour toute la classe. Une note est un nombre de 0 à 20 (virgule ou point,
  au plus 2 décimales). Les cases vides sont ignorées. Les notes déjà saisies sont affichées en lecture seule
  avec un lien « Corriger » : la saisie n'écrase jamais une note (la contrainte
  `UNIQUE (eleve, matiere, sequence)` reste la vraie protection). Si **une** note est invalide, **rien**
  n'est enregistré et les erreurs sont affichées sous les cases (tout ou rien, transaction).
  Saisie refusée pour une évaluation clôturée ou dont la date n'est pas encore arrivée.
- **JavaScript** (`saisie.js`) : refus immédiat d'une note hors de 0 à 20 (case en rouge + message),
  **moyenne de la classe recalculée en direct** (notes existantes + nouvelles), nombre de notes saisies,
  plus forte et plus faible note, bouton « Enregistrer » désactivé tant qu'une erreur subsiste.
- **Clôture** (POST) quand toutes les notes sont saisies ; **réouverture** réservée à l'administrateur.
- **Correction** d'une note (POST) : nouvelle note de 0 à 20 différente de l'ancienne + motif obligatoire
  (5 à 200 caractères). L'ancienne valeur, la nouvelle, le motif, l'auteur et la date sont gardés dans
  `corrections` ; l'historique des corrections est affiché. La correction reste possible après clôture
  (c'est la seule façon de modifier une note clôturée).

## Routes

| Adresse | Méthode | Rôle | Gabarit |
|---|---|---|---|
| `/enseignant/evaluations` | GET | liste filtrable + formulaire de création | `enseignant/evaluations.html` |
| `/enseignant/evaluations` | POST | créer une évaluation | idem |
| `/enseignant/evaluations/<id>/saisie` | GET / POST | saisir les notes de la classe | `enseignant/saisie.html` |
| `/enseignant/evaluations/<id>/cloturer` | POST | clôturer | — |
| `/enseignant/evaluations/<id>/rouvrir` | POST | rouvrir (administrateur) | — |
| `/enseignant/evaluations/<id>/supprimer` | POST | supprimer si aucune note | — |
| `/enseignant/notes/<id>/correction` | GET / POST | corriger une note | `enseignant/correction.html` |

## Critères d'acceptation

- [ ] Saisir « 22 » : la case devient rouge immédiatement et l'enregistrement est bloqué ; envoyé quand même
  (JavaScript désactivé), le serveur refuse et n'enregistre aucune note.
- [ ] La moyenne affichée en direct correspond à la moyenne des notes présentes.
- [ ] Un enseignant ne peut pas ouvrir la saisie d'une matière qui n'est pas la sienne (403).
- [ ] Une correction met à jour la note et ajoute une ligne dans `corrections`.
