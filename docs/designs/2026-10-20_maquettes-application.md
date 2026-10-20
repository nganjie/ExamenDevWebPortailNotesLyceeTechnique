# Maquettes de l'application — Portail de notes

- Date : 2026-10-20
- Canevas interactif : https://claude.ai/artifact/JcbmAFaLJXMij3v626AXHa (privé : à partager depuis le menu « Share »)
- Sources des maquettes : [`2026-10-20_maquettes-sources/`](2026-10-20_maquettes-sources/)
- Exigences illustrées : `P3-PUB-1..3`, `P3-ADM-1..4`, `P3-JS-1..3`, `P3-STAT-1..4`, `P3-RG-1..4`, `P3-BON-1..2`, `G-TECH-4`

## Inspiration

- Conventions des vrais bulletins et portails scolaires (Pronote, ÉcoleDirecte) : coefficients,
  note × coefficient, moyenne de la classe par matière, rang, appréciation.
- Tableaux de bord SaaS actuels (Stripe, Linear) : menu latéral sombre, cartes d'indicateurs,
  tableaux denses et lisibles, chiffres alignés (`tabular-nums`).
- Aucun modèle de site récupéré : tout est dessiné pour le projet.

## Charte graphique

| Rôle | Valeur |
|---|---|
| Couleur principale | `#1D4ED8` (bleu) |
| Accent | `#B45309` / fond `#FEF3C7` (ambre : podium, seuil de 10, ex æquo) |
| Erreur | `#B91C1C` / fond `#FEE2E2` |
| Succès | `#047857` |
| Texte / texte secondaire | `#0F172A` / `#475569` |
| Fond / bordures | `#F5F7FB` / `#E2E8F0` |
| Titres | Manrope 800 |
| Texte courant | Inter 400-700 |

Rayons 8-16 px, zones cliquables d'au moins 44 px, contrastes ≥ 4,5:1.
Le bleu et l'orange se distinguent aussi par la luminosité (lisibles par les daltoniens).

## Écrans

| # | Écran | Format | Points clés |
|---|---|---|---|
| 1 | Accueil et connexion | ordinateur | onglets Élève / parent ↔ Enseignant (interactif), formulaire matricule + code |
| 2 | Bulletin de séquence | ordinateur | sélecteur S1-S6 (interactif), moyenne coefficientée calculée, rang, moyenne classe, tableau des notes, historique, graphique d'évolution, bouton imprimer |
| 3 | Connexion élève | téléphone | message d'erreur de vérification JS (format du matricule) |
| 4 | Bulletin | téléphone | version empilée : synthèse, notes en liste, graphique |
| 5 | Saisie des notes d'une classe | ordinateur | 30 élèves sur une page, refus immédiat hors 0-20, moyenne de la classe en direct, enregistrement bloqué tant qu'il y a une erreur (interactif) |
| 6 | Liste de classe | ordinateur | moyennes et rangs avec ex æquo (5, 5 puis 7 ; 8, 8 puis 10), formulaire de correction d'une note |
| 7 | Statistiques | ordinateur | moyenne et taux de réussite par classe, répartition par tranches, 3 premiers par classe, moyenne de chaque matière par classe |

## Données fictives cohérentes

Les chiffres sont cohérents d'un écran à l'autre (ils serviront de base à `donnees_test.py`) :

- élève témoin : **NGO BASSA Aline**, matricule `LT24-F3-0017`, 2e année F3 ;
  séquence 1 : 12,04 (9e) ; séquence 2 : 12,98 (7e / 30) ;
- 8 matières, total des coefficients 24 (Électrotechnique 5, Mathématiques 4, Technologie 4,
  Sciences physiques 3, Dessin technique 3, Français 2, Anglais 2, EPS 1) ;
- 2e année F3, séquence 2 : moyenne 10,92, réussite 63,3 % (19 / 30) ;
- 120 élèves répartis par tranches : 11 / 37 / 36 / 24 / 12.

## Décisions à valider par le groupe

- Format du matricule `LT24-F3-0017` et code d'accès à 6 chiffres.
- Bornes des appréciations automatiques (< 8 Insuffisant, 8-10 Médiocre, 10-12 Passable,
  12-14 Assez bien, 14-16 Bien, ≥ 16 Très bien).
- Correction d'une note avec un motif (colonne supplémentaire à prévoir dans `notes` ou une table d'historique).
