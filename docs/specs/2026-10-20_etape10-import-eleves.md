# Spec — Étape 10 : import d'élèves depuis un fichier

- Date : 2026-10-20
- Exigences couvertes : `P3-EXT-3`, `P3-EXT-2` (codes d'accès), `G-TECH-8`
- Maquette : écran 10 (assistant en 3 étapes)

## Formats acceptés

| Format | Lecture | Bibliothèque |
|---|---|---|
| `.csv` | séparateur `;`, `,` ou tabulation détecté ; encodage UTF-8 (avec ou sans BOM) ou Windows-1252 | module standard `csv` |
| `.xlsx` | première feuille | `openpyxl` |
| `.xls` | première feuille (ancien format Excel) | `xlrd` |
| `.ods` | première feuille (LibreOffice / OpenOffice) | `odfpy` |

Taille maximale 2 Mo (`MAX_CONTENT_LENGTH`) ; 500 lignes au plus ; extension vérifiée côté serveur.

## Déroulé

1. **Fichier** : choix de la classe de destination + fichier ; modèles `modele_eleves.csv` et
   `modele_eleves.xlsx` téléchargeables. Colonnes attendues : `nom`, `prenom`, `date_naissance`
   (JJ/MM/AAAA ou AAAA-MM-JJ, ou vraie date du tableur), `matricule` (facultatif).
2. **Vérification** : la première ligne est l'en-tête ; la correspondance des colonnes est **devinée**
   (sans tenir compte des accents, majuscules, espaces : « PRÉNOMS », « Date de naissance »…) et
   **modifiable**. Chaque ligne est classée : *Valide*, *Doublon* (matricule déjà en base ou deux fois dans
   le fichier) ou *Erreur* (nom ou prénom manquant, date invalide, âge hors 10-30 ans, matricule mal formé,
   classe pleine). Résumé chiffré, lignes à problème affichées en premier.
3. **Import** : seules les lignes valides sont importées, en une transaction ; le fichier est **revérifié**
   au moment de l'import (on ne fait pas confiance à l'aperçu). Matricule généré si absent, code d'accès
   aléatoire haché. La page de confirmation affiche les codes **une seule fois** (imprimable) et propose la
   liste des codes en CSV, **téléchargeable une seule fois** puis effacée du serveur.

Le fichier envoyé est gardé dans un dossier temporaire sous un nom aléatoire (jeton gardé dans la session
de l'administrateur) entre l'aperçu et l'import, puis supprimé.

## Routes (administrateur)

| Adresse | Méthode | Rôle |
|---|---|---|
| `/admin/import` | GET | étape 1 |
| `/admin/import/analyse` | POST | envoi du fichier ou nouvelle correspondance → étape 2 |
| `/admin/import/confirmer` | POST | import des lignes valides → étape 3 |
| `/admin/import/codes.csv` | GET | codes en CSV (une seule fois) |
| `/admin/import/modele.<format>` | GET | modèle CSV ou XLSX |

## Critères d'acceptation

- [ ] Un même fichier d'élèves en CSV, XLSX et ODS donne le même aperçu.
- [ ] Une ligne avec une date invalide ou sans prénom est signalée et n'est pas importée.
- [ ] Un matricule déjà présent est signalé comme doublon.
- [ ] L'import ne dépasse jamais l'effectif maximal de la classe.
- [ ] Les élèves importés peuvent se connecter avec les codes affichés.
