"""Portail de notes d'un lycée technique : application Flask principale.

Lancement :  python app.py   puis ouvrir http://127.0.0.1:5000
"""

import os
import secrets
import sqlite3
from datetime import date
from functools import wraps

from flask import (Flask, abort, flash, g, redirect, render_template, request,
                   session, url_for)

# --- Configuration -----------------------------------------------------------

DOSSIER = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config["CHEMIN_BASE"] = os.path.join(DOSSIER, "projet.db")
# Clé secrète des sessions : à remplacer en production par une valeur gardée secrète
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "portail-notes-cle-de-developpement-2026")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # fichiers envoyés : 2 Mo au maximum

NOM_LYCEE = "Lycée technique"
ANNEE_SCOLAIRE = "2026-2027"
FILIERES = {
    "F1": "Construction mécanique",
    "F2": "Électronique",
    "F3": "Électrotechnique",
    "F4": "Génie civil",
}


# --- Base de données ---------------------------------------------------------

def get_db():
    """Renvoie la connexion SQLite de la requête en cours (créée si besoin)."""
    if "db" not in g:
        g.db = sqlite3.connect(app.config["CHEMIN_BASE"])
        g.db.row_factory = sqlite3.Row            # accès aux colonnes par leur nom
        g.db.execute("PRAGMA foreign_keys = ON")  # SQLite ignore les clés étrangères sans cela
    return g.db


@app.teardown_appcontext
def close_db(exception):
    """Ferme la connexion à la fin de chaque requête."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


# --- Protection contre la falsification de formulaires (CSRF) ---------------

def jeton_csrf():
    """Renvoie le jeton de la session, créé au premier appel."""
    if "jeton_csrf" not in session:
        session["jeton_csrf"] = secrets.token_hex(16)
    return session["jeton_csrf"]


@app.before_request
def verifier_jeton_csrf():
    """Refuse tout envoi POST qui ne porte pas le jeton de la session."""
    if request.method == "POST":
        jeton = request.form.get("jeton_csrf") or request.headers.get("X-Jeton-CSRF")
        if not jeton or not secrets.compare_digest(jeton, session.get("jeton_csrf", "")):
            abort(400)


# --- Données communes aux gabarits ------------------------------------------

@app.context_processor
def variables_gabarits():
    """Variables disponibles dans tous les gabarits."""
    return {
        "nom_lycee": NOM_LYCEE,
        "annee_scolaire": ANNEE_SCOLAIRE,
        "annee_courante": date.today().year,
        "jeton_csrf": jeton_csrf,
        "filieres": FILIERES,
    }


@app.template_filter("note")
def format_note(valeur):
    """Affiche un nombre à la française avec deux décimales : 12.5 -> « 12,50 »."""
    if valeur is None:
        return "—"
    return f"{valeur:.2f}".replace(".", ",")


# --- Pages publiques ---------------------------------------------------------

@app.route("/")
def accueil():
    """Page d'accueil : présentation et formulaires de connexion."""
    return render_template("index.html", saisie={}, onglet=request.args.get("onglet", "eleve"))


@app.route("/connexion/eleve", methods=["POST"])
def connexion_eleve():
    """Connexion d'un élève (réalisée à l'étape 04)."""
    flash("La connexion des élèves sera disponible à la prochaine étape.", "info")
    return redirect(url_for("accueil"))


@app.route("/connexion/enseignant", methods=["POST"])
def connexion_enseignant():
    """Connexion d'un enseignant (réalisée à l'étape 04)."""
    flash("La connexion des enseignants sera disponible à la prochaine étape.", "info")
    return redirect(url_for("accueil", onglet="enseignant"))


# --- Pages d'erreur ----------------------------------------------------------

@app.errorhandler(404)
def page_introuvable(erreur):
    """Page d'erreur 404 personnalisée."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def erreur_serveur(erreur):
    """Page d'erreur 500 personnalisée."""
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=False)
