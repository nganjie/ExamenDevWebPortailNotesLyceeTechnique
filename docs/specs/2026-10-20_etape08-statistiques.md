# Spec — Étape 08 : statistiques

- Date : 2026-10-20
- Exigences couvertes : `P3-STAT-1..4`, `G-TECH-5` (fetch), `G-TECH-6` (deuxième route JSON)
- Maquette : écran 7

## Statistiques (pour une séquence choisie, par défaut la dernière notée)

1. **Moyenne générale et taux de réussite par classe** (moyenne ≥ 10), avec le nombre d'élèves admis.
2. **Moyenne de chaque matière par classe** : tableau matières × classes, cases colorées
   (< 10 rouge ; 10 à 12 ; 12 à 14 ; ≥ 14 de plus en plus bleu), légende lisible sans couleur (valeurs écrites).
3. **Les 3 premiers de chaque classe** : rangs 1 à 3, ex æquo inclus (on peut donc avoir plus de 3 noms).
4. **Répartition des moyennes par tranches** sur tout l'établissement : moins de 8, 8 à 10, 10 à 12,
   12 à 14, 14 et plus (bornes de la spec de l'étape 03).

## API

`GET /api/statistiques?sequence=N` (enseignant connecté, sinon 403 JSON) :
`{sequence, classes: [{id, nom, moyenne_generale, taux_reussite, admis, effectif}],
  matieres: [{id, nom, coefficient, moyennes: {classe_id: moyenne}}], premiers: [{classe, eleves: [...]}],
  repartition: [{tranche, effectif}], effectif_total}`

La page appelle cette route par `fetch` pour dessiner deux graphiques (Chart.js) : moyenne et taux de
réussite par classe, répartition par tranches. Les mêmes chiffres restent lisibles dans des tableaux.

## Route

| Adresse | Méthode | Rôle | Gabarit |
|---|---|---|---|
| `/enseignant/statistiques` | GET | statistiques d'une séquence (`?sequence=`) | `enseignant/statistiques.html` |
| `/api/statistiques` | GET | mêmes données en JSON | — |

## Critères d'acceptation

- [ ] La somme des effectifs des tranches est égale au nombre d'élèves classés.
- [ ] La moyenne d'une matière dans une classe est égale à la moyenne des notes de cette matière.
- [ ] En cas d'ex æquo au 3ᵉ rang, tous les élèves concernés apparaissent.
