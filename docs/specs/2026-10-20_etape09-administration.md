# Spec — Étape 09 : administration des classes et des élèves

- Date : 2026-10-20
- Exigences couvertes : `P3-EXT-1`, `P3-EXT-2`, `P3-EXT-5`, `P3-EXT-6`, `P3-BD-4`, `G-TECH-8`
- Maquettes : écrans 8 (classes) et 9 (élèves)

## Droits

Toutes les pages de cette étape sont réservées au rôle **administrateur** (`admin_requis`) : un enseignant
simple reçoit 403, un visiteur est renvoyé vers l'accueil.

## Classes

- Liste en cartes : nom, filière, effectif / maximum (jauge), professeur principal, liens « Élèves » et « Modifier ».
- Création / modification : nom (3 à 40 caractères, **unique**), niveau 1 à 4, filière F1 à F4,
  effectif maximal 1 à 60 (jamais **sous l'effectif actuel**), professeur principal facultatif.
- Suppression (POST + confirmation) seulement si la classe ne contient aucun élève.

## Élèves

- Liste filtrable par classe, recherche par nom, prénom ou matricule (requête `LIKE` paramétrée),
  20 élèves par page ; statut du code d'accès (« Remis » / « À remettre »).
- Ajout : nom (mis en majuscules), prénom, date de naissance (élève de 10 à 30 ans), classe (refusée si
  pleine), matricule facultatif (format `LTAA-Fx-NNNN`, unique) sinon **généré** : `LT` + année d'entrée
  sur 2 chiffres + filière + numéro suivant.
- Le **code d'accès** (6 chiffres, module `secrets`) est généré, **affiché une seule fois** dans un encadré,
  et seule son **empreinte** est enregistrée. « Nouveau code » en régénère un (l'ancien ne marche plus).
  « Marquer remis » note que le code a été donné à l'élève.
- Modification : nom, prénom, date de naissance, classe (si elle a de la place) ; le matricule ne change pas.
- Suppression (POST + confirmation) : supprime aussi ses notes (`ON DELETE CASCADE`).
- **Export CSV** de la liste (filtre de classe appliqué) : séparateur `;`, UTF-8 avec BOM (ouvrable dans Excel).

## Routes

| Adresse | Méthode | Rôle |
|---|---|---|
| `/admin/classes` | GET / POST | liste + création |
| `/admin/classes/<id>/modifier` | GET / POST | modification |
| `/admin/classes/<id>/supprimer` | POST | suppression d'une classe vide |
| `/admin/eleves` | GET / POST | liste + ajout |
| `/admin/eleves/<id>/modifier` | GET / POST | modification |
| `/admin/eleves/<id>/nouveau-code` | POST | nouveau code d'accès |
| `/admin/eleves/<id>/code-remis` | POST | code remis / à remettre |
| `/admin/eleves/<id>/supprimer` | POST | suppression |
| `/admin/eleves/export.csv` | GET | export CSV |

## Critères d'acceptation

- [ ] Un nom de classe en double est refusé avec un message sous le champ.
- [ ] Un élève ajouté peut se connecter avec le code affiché ; le code n'est plus jamais réaffiché.
- [ ] Un ajout dans une classe pleine est refusé.
- [ ] Un enseignant non administrateur reçoit 403 sur `/admin/...`.
