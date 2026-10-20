# Spec — Étape 01 : base de données et données de test

- Date : 2026-10-20
- Exigences couvertes : `P3-BD-1..5`, `P3-DT-1..6`, `P3-EXT-1`, `P3-EXT-4`, `P3-EXT-5`, `G-TECH-1`, `G-TECH-9`

## Besoin

Créer la base SQLite du portail (`schema.sql`), la remplir de données réalistes et reproductibles
(`donnees_test.py`), et pouvoir l'exporter en SQL lisible (`exporter.py` → `export_projet.sql`).

## Tables

| Table | Colonnes | Contraintes |
|---|---|---|
| `enseignants` | id, nom, login, empreinte, role | login `UNIQUE`, role `CHECK IN ('enseignant','administrateur')` |
| `classes` | id, nom, niveau, filiere, effectif_max, professeur_principal_id | nom `UNIQUE`, `CHECK niveau BETWEEN 1 AND 4`, `CHECK effectif_max BETWEEN 1 AND 60`, FK → enseignants (`ON DELETE SET NULL`) |
| `matieres` | id, nom, coefficient, enseignant_id | nom `UNIQUE`, `CHECK coefficient BETWEEN 1 AND 10`, FK → enseignants |
| `eleves` | id, matricule, nom, prenom, classe_id, date_naissance, code_empreinte, code_remis | matricule `UNIQUE`, FK → classes, `CHECK code_remis IN (0,1)` |
| `evaluations` | id, classe_id, matiere_id, sequence, intitule, date_evaluation, statut | `CHECK sequence BETWEEN 1 AND 6`, `CHECK statut IN ('ouverte','cloturee')`, **`UNIQUE (classe_id, matiere_id, sequence)`** |
| `notes` | id, eleve_id, matiere_id, sequence, note, date_saisie | `CHECK sequence BETWEEN 1 AND 6`, `CHECK note BETWEEN 0 AND 20`, **`UNIQUE (eleve_id, matiere_id, sequence)`**, FK (`ON DELETE CASCADE` sur l'élève) |
| `corrections` | id, note_id, ancienne_note, nouvelle_note, motif, enseignant_id, date_correction | FK → notes (`CASCADE`), FK → enseignants, `CHECK nouvelle_note BETWEEN 0 AND 20` |

Toutes les colonnes métier sont `NOT NULL` (sauf `professeur_principal_id`).
Les dates sont stockées au format ISO `AAAA-MM-JJ`.

## Données de test (`random.seed(42)`)

- 8 enseignants (un par matière) ; `admin` (M. Fotso, Électrotechnique) a le rôle `administrateur`.
- 8 matières, total des coefficients 24 : Électrotechnique 5, Mathématiques 4, Technologie 4,
  Sciences physiques 3, Dessin technique 3, Français 2, Anglais 2, Éducation physique 1.
- 4 classes (effectif maximal 35) : 1re année F4, 2e année F3, 3e année F2, 4e année F1.
- 120 élèves (30 par classe), noms et prénoms camerounais, matricule `LTAA-Fx-NNNN`
  (AA = année d'entrée), code d'accès à 6 chiffres haché.
- 64 évaluations (4 classes × 8 matières × séquences 1 et 2) : séquence 1 clôturée, séquence 2 ouverte ;
  quelques évaluations planifiées en séquence 3.
- 1 920 notes (120 × 8 × 2), au quart de point, réalistes (niveau propre à chaque élève, difficulté propre
  à chaque matière).
- Les codes d'accès en clair des élèves de test sont écrits dans `codes_eleves_test.csv`
  (fichier de test uniquement, pour que l'enseignant puisse se connecter).

## Critères d'acceptation

- [ ] `python donnees_test.py` recrée `projet.db` et affiche le nombre de lignes par table.
- [ ] Volumes : 4 classes, 120 élèves, 8 matières, 1 920 notes au minimum.
- [ ] Une deuxième note pour le même élève, la même matière et la même séquence est refusée par la base.
- [ ] Une note de 21 ou une séquence 7 sont refusées par la base.
- [ ] `python exporter.py` produit `export_projet.sql`, qui recrée une base identique.
