# Spec — Étape 05 : espace élève (bulletin, historique, graphique, impression)

- Date : 2026-10-20
- Exigences couvertes : `P3-PUB-2`, `P3-PUB-3`, `P3-RG-1..2`, `P3-RG-4`, `P3-JS-3`, `P3-API-2`,
  `P3-BON-1`, `P3-BON-2`
- Maquettes : écrans 2 (ordinateur) et 4 (téléphone)

## Besoin

L'élève (ou son parent) consulte le bulletin d'une séquence, l'historique de ses moyennes et un
graphique de son évolution comparée à la classe ; il peut imprimer proprement le bulletin.

## Règles

- Le bulletin affiché est **toujours** celui de l'élève de la session (aucun identifiant d'élève dans l'URL).
- Séquences 1 à 6 ; une séquence sans aucune note pour la classe est grisée (non cliquable). Une
  séquence hors de 1 à 6 → 404.
- Bulletin : pour chaque matière, enseignant, coefficient, note, note × coefficient, moyenne de la classe
  dans la matière, appréciation ; total des coefficients et des points ; moyenne coefficientée,
  appréciation générale, rang / effectif (mention « ex æquo »), moyenne de la classe et écart,
  plus forte et plus faible moyenne de la classe.
- Historique : pour chaque séquence notée, moyenne, rang et moyenne de la classe.
- **API** `GET /api/eleves/<id>/evolution` (JSON) : `[{sequence, moyenne, rang, moyenne_classe}]`.
  Accès : l'élève lui-même ou un enseignant connecté ; tout autre → 403 (JSON).
- **Graphique** (Chart.js, copié dans `static/js/vendor`) chargé par `fetch` sur cette route : courbe
  de l'élève, courbe de la classe, ligne du seuil de 10. Si le chargement échoue, un message remplace le graphique.
- **Impression** (`static/css/impression.css`, `@media print`) : en-tête officiel (lycée, année, élève),
  tableau lisible en noir et blanc, sans menu ni boutons ni graphique, zone de signatures.
- Sur téléphone, le tableau des notes devient une liste de cartes (une par matière).

## Routes

| Adresse | Méthode | Rôle | Gabarit |
|---|---|---|---|
| `/eleve` | GET | redirige vers la dernière séquence notée | — |
| `/eleve/bulletin/<sequence>` | GET | bulletin de la séquence | `eleve/bulletin.html` |
| `/api/eleves/<id>/evolution` | GET | moyennes par séquence (JSON) | — |

## Critères d'acceptation

- [ ] La moyenne affichée est égale à Σ(note × coef) / Σ(coef) et le rang à celui de la liste de classe.
- [ ] Un élève qui appelle l'API avec l'identifiant d'un autre élève reçoit 403.
- [ ] L'aperçu avant impression ne montre ni menu ni bouton.
- [ ] Le bulletin est lisible à 390 px sans défilement horizontal.
