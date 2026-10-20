"""donnees_test.py : crée la base projet.db et la remplit de données de test.

Volumes minimum du sujet : 4 classes, 120 élèves, 8 matières avec coefficients,
les notes de 2 séquences pour tous les élèves, et un compte enseignant de test.
Le remplissage sera écrit après la spec « base de données ».
"""

import random
import sqlite3


def remplir(db):
    """Remplit la base (à compléter une fois le schéma défini)."""
    pass


if __name__ == "__main__":
    random.seed(42)  # mêmes données à chaque lancement
    db = sqlite3.connect("projet.db")
    with open("schema.sql", encoding="utf-8") as f:
        db.executescript(f.read())
    remplir(db)
    db.commit()
    db.close()
    print("Base projet.db créée.")
