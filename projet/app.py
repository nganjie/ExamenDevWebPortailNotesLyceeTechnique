"""Portail de notes d'un lycée technique : application Flask principale.

Squelette initial : configuration, connexion à la base SQLite, page d'accueil
et page d'erreur 404. Les fonctionnalités (bulletins, saisie des notes, API)
seront ajoutées étape par étape.
"""

import os
import sqlite3
from functools import wraps

from flask import Flask, g, redirect, render_template, session, url_for

# Chemin absolu de la base, pour que le site fonctionne quel que soit le dossier de lancement
DOSSIER = os.path.dirname(os.path.abspath(__file__))
CHEMIN_BASE = os.path.join(DOSSIER, "projet.db")

app = Flask(__name__)
# Clé secrète nécessaire aux sessions et aux messages flash
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "changer-cette-cle-portail-notes")


# --- Base de données ---------------------------------------------------------

def get_db():
    """Renvoie la connexion SQLite de la requête en cours (créée si besoin)."""
    if "db" not in g:
        g.db = sqlite3.connect(CHEMIN_BASE)
        g.db.row_factory = sqlite3.Row          # accès aux colonnes par leur nom
        g.db.execute("PRAGMA foreign_keys = ON")  # SQLite ignore les clés étrangères sans cela
    return g.db


@app.teardown_appcontext
def close_db(exception):
    """Ferme la connexion à la fin de chaque requête."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


# --- Protection des pages ----------------------------------------------------

def connexion_requise(vue):
    """Décorateur : réserve une page aux enseignants connectés."""
    @wraps(vue)
    def vue_protegee(*args, **kwargs):
        if "enseignant_id" not in session:
            return redirect(url_for("accueil"))
        return vue(*args, **kwargs)
    return vue_protegee


# --- Pages -------------------------------------------------------------------

@app.route("/")
def accueil():
    """Page d'accueil du portail."""
    return render_template("index.html")


@app.errorhandler(404)
def page_introuvable(erreur):
    """Page d'erreur 404 personnalisée."""
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=False)
