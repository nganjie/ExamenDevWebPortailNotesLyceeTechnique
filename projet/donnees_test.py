"""donnees_test.py : crée la base projet.db et la remplit de données de test réalistes.

Volumes : 8 enseignants, 8 matières, 4 classes, 120 élèves, 64 évaluations
et les notes des séquences 1 et 2 pour tous les élèves (1 920 notes).

Lancement :  python donnees_test.py
"""

import csv
import os
import random
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash

DOSSIER = os.path.dirname(os.path.abspath(__file__))
CHEMIN_BASE = os.path.join(DOSSIER, "projet.db")
CHEMIN_SCHEMA = os.path.join(DOSSIER, "schema.sql")
CHEMIN_CODES = os.path.join(DOSSIER, "codes_eleves_test.csv")

# Mots de passe des comptes de test (repris dans le README)
MOT_DE_PASSE_ADMIN = "Admin!2026"
MOT_DE_PASSE_PROFS = "Prof!2026"

NOMS = ["ABENA", "ATANGANA", "BELLO", "DJOMO", "EKANE", "ESSOMBA", "ETOA", "FOUDA",
        "KAMGA", "KENFACK", "MANGA", "MBALLA", "MBARGA", "NANA", "NDJOCK", "NGO BASSA",
        "NGUEMA", "NJOYA", "NKOULOU", "NOAH", "ONANA", "OWONA", "SADOU", "TABI",
        "TCHAMENI", "TCHOUPO", "WAMBA", "YAMDJEU", "ZANG", "MVONDO", "NDZANA", "FOKOU",
        "ELOUNDOU", "ATEBA", "KOUAM", "MOUSSA", "NGONO", "TAMO", "ABOUBAKAR", "BIKOE"]
PRENOMS = ["Aline", "Paul", "Kevin", "Marie", "Ibrahim", "Sandra", "Rose", "Moussa",
           "Christelle", "Franck", "Yannick", "Brice", "Marcelle", "Hervé", "Ulrich",
           "Estelle", "Cédric", "Vanessa", "Arnaud", "Patricia", "Samuel", "Joël", "Grâce",
           "Steve", "Aïcha", "Michelle", "Loïc", "Diane", "Carine", "Rodrigue", "Linda",
           "Sylvie", "Thierry", "Nadège", "Clarisse", "Didier", "Mireille", "Arthur"]

# (nom affiché, login, matière enseignée, coefficient, difficulté de la matière)
ENSEIGNANTS_MATIERES = [
    ("M. Fotso Jean", "admin", "Électrotechnique", 5, 0.8),
    ("M. Atangana Pierre", "p.atangana", "Mathématiques", 4, -0.6),
    ("M. Kamga Victor", "v.kamga", "Technologie", 4, 0.0),
    ("Mme Ekane Brigitte", "b.ekane", "Sciences physiques", 3, -1.2),
    ("M. Njoya Salomon", "s.njoya", "Dessin technique", 3, 0.4),
    ("Mme Mballa Odile", "o.mballa", "Français", 2, -0.8),
    ("Mme Tabi Grace", "g.tabi", "Anglais", 2, 0.2),
    ("M. Bello Amadou", "a.bello", "Éducation physique", 1, 2.5),
]

# (nom, niveau, filière, indice du professeur principal dans ENSEIGNANTS_MATIERES)
CLASSES = [
    ("1re année F4", 1, "F4", 4),
    ("2e année F3", 2, "F3", 0),
    ("3e année F2", 3, "F2", 3),
    ("4e année F1", 4, "F1", 2),
]

ELEVES_PAR_CLASSE = 30
EFFECTIF_MAX = 35
ANNEE_RENTREE = 2026

# Dates des évaluations de chaque séquence (année scolaire 2026-2027)
DATES_SEQUENCES = {
    1: [date(2026, 9, 21), date(2026, 9, 30)],
    2: [date(2026, 10, 12), date(2026, 10, 19)],
    3: [date(2026, 11, 23), date(2026, 11, 27)],
}


def arrondir_quart(valeur):
    """Arrondit une note au quart de point et la garde entre 0 et 20."""
    return min(20.0, max(0.0, round(valeur * 4) / 4))


def date_entre(debut, fin):
    """Tire une date au hasard entre deux dates."""
    return date.fromordinal(random.randint(debut.toordinal(), fin.toordinal()))


def creer_enseignants(db):
    """Crée les comptes enseignants ; le premier est administrateur."""
    ids = []
    for indice, (nom, login, _, _, _) in enumerate(ENSEIGNANTS_MATIERES):
        role = "administrateur" if indice == 0 else "enseignant"
        mot_de_passe = MOT_DE_PASSE_ADMIN if indice == 0 else MOT_DE_PASSE_PROFS
        curseur = db.execute(
            "INSERT INTO enseignants (nom, login, empreinte, role) VALUES (?, ?, ?, ?)",
            (nom, login, generate_password_hash(mot_de_passe), role))
        ids.append(curseur.lastrowid)
    return ids


def creer_matieres(db, ids_enseignants):
    """Crée les 8 matières, chacune confiée à son enseignant."""
    matieres = []
    for (_, _, nom, coefficient, difficulte), enseignant_id in zip(ENSEIGNANTS_MATIERES, ids_enseignants):
        curseur = db.execute(
            "INSERT INTO matieres (nom, coefficient, enseignant_id) VALUES (?, ?, ?)",
            (nom, coefficient, enseignant_id))
        matieres.append({"id": curseur.lastrowid, "difficulte": difficulte})
    return matieres


def creer_classes(db, ids_enseignants):
    """Crée les 4 classes avec leur professeur principal."""
    classes = []
    for nom, niveau, filiere, indice_pp in CLASSES:
        curseur = db.execute(
            "INSERT INTO classes (nom, niveau, filiere, effectif_max, professeur_principal_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (nom, niveau, filiere, EFFECTIF_MAX, ids_enseignants[indice_pp]))
        classes.append({"id": curseur.lastrowid, "niveau": niveau, "filiere": filiere})
    return classes


def creer_eleves(db, classes):
    """Crée 30 élèves par classe ; renvoie leur niveau scolaire et la liste des codes en clair."""
    combinaisons = [(n, p) for n in NOMS for p in PRENOMS]
    random.shuffle(combinaisons)
    eleves, codes = [], []
    for classe in classes:
        annee_entree = ANNEE_RENTREE - (classe["niveau"] - 1)
        naissance_min = date(annee_entree - 16, 1, 1)
        naissance_max = date(annee_entree - 14, 12, 31)
        for numero in range(1, ELEVES_PAR_CLASSE + 1):
            nom, prenom = combinaisons.pop()
            matricule = f"LT{annee_entree % 100:02d}-{classe['filiere']}-{numero:04d}"
            code = f"{random.randint(0, 999999):06d}"
            curseur = db.execute(
                "INSERT INTO eleves (matricule, nom, prenom, classe_id, date_naissance, "
                "code_empreinte, code_remis) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (matricule, nom, prenom, classe["id"],
                 date_entre(naissance_min, naissance_max).isoformat(),
                 generate_password_hash(code), 1 if random.random() < 0.85 else 0))
            eleves.append({"id": curseur.lastrowid, "classe_id": classe["id"],
                           "niveau": random.gauss(11, 2.3), "progres": random.gauss(0.3, 0.8)})
            codes.append((matricule, nom, prenom, code))
    return eleves, codes


def creer_evaluations(db, classes, matieres):
    """Crée les évaluations : séquence 1 clôturée, séquence 2 ouverte, quelques-unes en séquence 3."""
    for classe in classes:
        for matiere in matieres:
            for sequence, numero in ((1, 1), (2, 2)):
                debut, fin = DATES_SEQUENCES[sequence]
                db.execute(
                    "INSERT INTO evaluations (classe_id, matiere_id, sequence, intitule, "
                    "date_evaluation, statut) VALUES (?, ?, ?, ?, ?, ?)",
                    (classe["id"], matiere["id"], sequence, f"Devoir surveillé n°{numero}",
                     date_entre(debut, fin).isoformat(),
                     "cloturee" if sequence == 1 else "ouverte"))
        # deux évaluations planifiées pour la séquence 3 (sans notes)
        for matiere in matieres[:2]:
            debut, fin = DATES_SEQUENCES[3]
            db.execute(
                "INSERT INTO evaluations (classe_id, matiere_id, sequence, intitule, "
                "date_evaluation, statut) VALUES (?, ?, ?, ?, ?, 'ouverte')",
                (classe["id"], matiere["id"], 3, "Devoir surveillé n°3", date_entre(debut, fin).isoformat()))


def creer_notes(db, eleves, matieres):
    """Crée les notes des séquences 1 et 2 pour tous les élèves et toutes les matières."""
    crees = 0
    for eleve in eleves:
        for matiere in matieres:
            for sequence in (1, 2):
                base = eleve["niveau"] + matiere["difficulte"]
                if sequence == 2:
                    base += eleve["progres"]
                note = arrondir_quart(random.gauss(base, 2.0))
                debut, fin = DATES_SEQUENCES[sequence]
                try:
                    db.execute(
                        "INSERT INTO notes (eleve_id, matiere_id, sequence, note, date_saisie) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (eleve["id"], matiere["id"], sequence, note, fin.isoformat()))
                    crees += 1
                except sqlite3.IntegrityError:
                    pass  # note déjà présente : la contrainte UNIQUE la refuse
    return crees


def ecrire_codes(codes, chemin):
    """Écrit les codes d'accès en clair des élèves de test (fichier de test uniquement)."""
    with open(chemin, "w", newline="", encoding="utf-8") as fichier:
        ecrivain = csv.writer(fichier, delimiter=";")
        ecrivain.writerow(["matricule", "nom", "prenom", "code_acces"])
        ecrivain.writerows(codes)


def creer_base(chemin_base=CHEMIN_BASE, chemin_codes=CHEMIN_CODES, graine=42):
    """Recrée entièrement la base et la remplit ; renvoie le nombre de lignes par table."""
    random.seed(graine)  # mêmes données à chaque lancement
    db = sqlite3.connect(chemin_base)
    db.execute("PRAGMA foreign_keys = ON")
    with open(CHEMIN_SCHEMA, encoding="utf-8") as fichier:
        db.executescript(fichier.read())
    ids_enseignants = creer_enseignants(db)
    matieres = creer_matieres(db, ids_enseignants)
    classes = creer_classes(db, ids_enseignants)
    eleves, codes = creer_eleves(db, classes)
    creer_evaluations(db, classes, matieres)
    creer_notes(db, eleves, matieres)
    db.commit()
    ecrire_codes(codes, chemin_codes)
    volumes = {}
    for table in ("enseignants", "matieres", "classes", "eleves", "evaluations", "notes", "corrections"):
        volumes[table] = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    db.close()
    return volumes


if __name__ == "__main__":
    for table, nombre in creer_base().items():
        print(f"{table:12} : {nombre} lignes")
    print("Base projet.db créée ; codes d'accès des élèves dans codes_eleves_test.csv")
