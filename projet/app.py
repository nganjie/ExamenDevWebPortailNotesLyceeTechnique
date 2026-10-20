"""Portail de notes d'un lycée technique : application Flask principale.

Lancement :  python app.py   puis ouvrir http://127.0.0.1:5000
"""

import os
import re
import secrets
import sqlite3
import time
from datetime import date
from functools import wraps

from flask import (Flask, abort, flash, g, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash

import calculs

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
NOMBRE_SEQUENCES = 6

MOTIF_MATRICULE = re.compile(r"^LT[0-9]{2}-F[0-9]-[0-9]{4}$")
MOTIF_CODE = re.compile(r"^[0-9]{6}$")

# Limitation des essais de connexion : {identifiant: [nombre d'échecs, heure du premier échec]}
ESSAIS_MAX = 5
DUREE_BLOCAGE = 5 * 60  # secondes
TENTATIVES = {}


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


@app.template_filter("date_fr")
def format_date(valeur):
    """Affiche une date ISO à la française : 2026-10-20 -> « 20/10/2026 »."""
    if not valeur:
        return "—"
    annee, mois, jour = valeur[:10].split("-")
    return f"{jour}/{mois}/{annee}"


@app.template_filter("initiales")
def initiales(nom_complet):
    """Initiales affichées dans la pastille de l'utilisateur : « NGO BASSA Aline » -> « NA »."""
    civilites = {"M", "MME", "MLLE", "MRS", "MR"}
    mots = [m for m in nom_complet.replace(".", " ").split() if m.upper() not in civilites]
    return (mots[0][0] + mots[-1][0]).upper() if len(mots) > 1 else nom_complet[:2].upper()


# --- Utilisateur connecté et protection des pages ---------------------------

@app.before_request
def charger_utilisateur():
    """Relit dans la base l'élève ou l'enseignant de la session (rôle toujours à jour)."""
    g.eleve = None
    g.enseignant = None
    if "eleve_id" in session:
        g.eleve = get_db().execute(
            "SELECT e.*, c.nom AS classe_nom, c.filiere FROM eleves e "
            "JOIN classes c ON c.id = e.classe_id WHERE e.id = ?",
            (session["eleve_id"],)).fetchone()
    elif "enseignant_id" in session:
        g.enseignant = get_db().execute(
            "SELECT id, nom, login, role FROM enseignants WHERE id = ?",
            (session["enseignant_id"],)).fetchone()


def eleve_requis(vue):
    """Décorateur : réserve une page à l'élève connecté."""
    @wraps(vue)
    def vue_protegee(*args, **kwargs):
        if g.eleve is None:
            flash("Connectez-vous avec votre matricule et votre code d'accès.", "info")
            return redirect(url_for("accueil"))
        return vue(*args, **kwargs)
    return vue_protegee


def connexion_requise(vue):
    """Décorateur : réserve une page aux enseignants connectés (exercice 29 du polycopié)."""
    @wraps(vue)
    def vue_protegee(*args, **kwargs):
        if g.eleve is not None:
            abort(403)
        if g.enseignant is None:
            flash("Cet espace est réservé aux enseignants : connectez-vous.", "info")
            return redirect(url_for("accueil", onglet="enseignant"))
        return vue(*args, **kwargs)
    return vue_protegee


def admin_requis(vue):
    """Décorateur : réserve une page aux enseignants qui ont le rôle administrateur."""
    @wraps(vue)
    @connexion_requise
    def vue_protegee(*args, **kwargs):
        if g.enseignant["role"] != "administrateur":
            abort(403)
        return vue(*args, **kwargs)
    return vue_protegee


def est_bloque(identifiant):
    """Vrai si l'identifiant a dépassé le nombre d'essais autorisés récemment."""
    essai = TENTATIVES.get(identifiant)
    if essai is None:
        return False
    if time.time() - essai[1] > DUREE_BLOCAGE:
        del TENTATIVES[identifiant]
        return False
    return essai[0] >= ESSAIS_MAX


def noter_echec(identifiant):
    """Compte un essai de connexion raté."""
    essai = TENTATIVES.setdefault(identifiant, [0, time.time()])
    essai[0] += 1


def ouvrir_session(**valeurs):
    """Vide la session puis y enregistre l'utilisateur connecté."""
    session.clear()
    session.update(valeurs)


# --- Pages publiques et connexion ---------------------------------------------

@app.route("/")
def accueil():
    """Page d'accueil : présentation et formulaires de connexion."""
    if g.eleve is not None:
        return redirect(url_for("espace_eleve"))
    if g.enseignant is not None:
        return redirect(url_for("tableau_de_bord"))
    return render_template("index.html", saisie={}, onglet=request.args.get("onglet", "eleve"))


@app.route("/connexion/eleve", methods=["POST"])
def connexion_eleve():
    """Connexion d'un élève (ou de son parent) avec le matricule et le code d'accès."""
    matricule = request.form.get("matricule", "").strip().upper()
    code = request.form.get("code", "").strip()
    erreur = None
    if not MOTIF_MATRICULE.match(matricule):
        erreur = "Le matricule doit avoir la forme LT25-F3-0017."
    elif not MOTIF_CODE.match(code):
        erreur = "Le code d'accès comporte 6 chiffres."
    elif est_bloque("eleve:" + matricule):
        erreur = "Trop de tentatives : réessayez dans quelques minutes."
    else:
        eleve = get_db().execute("SELECT id, code_empreinte FROM eleves WHERE matricule = ?",
                                 (matricule,)).fetchone()
        if eleve is None or not check_password_hash(eleve["code_empreinte"], code):
            noter_echec("eleve:" + matricule)
            erreur = "Matricule ou code incorrect."
        else:
            TENTATIVES.pop("eleve:" + matricule, None)
            ouvrir_session(eleve_id=eleve["id"])
            return redirect(url_for("espace_eleve"))
    flash(erreur, "erreur")
    return render_template("index.html", saisie={"matricule": matricule}, onglet="eleve"), 400


@app.route("/connexion/enseignant", methods=["POST"])
def connexion_enseignant():
    """Connexion d'un enseignant avec son identifiant et son mot de passe."""
    login = request.form.get("login", "").strip().lower()
    mot_de_passe = request.form.get("mot_de_passe", "")
    erreur = None
    if not login or not mot_de_passe:
        erreur = "Saisissez votre identifiant et votre mot de passe."
    elif est_bloque("enseignant:" + login):
        erreur = "Trop de tentatives : réessayez dans quelques minutes."
    else:
        enseignant = get_db().execute("SELECT id, empreinte FROM enseignants WHERE login = ?",
                                      (login,)).fetchone()
        if enseignant is None or not check_password_hash(enseignant["empreinte"], mot_de_passe):
            noter_echec("enseignant:" + login)
            erreur = "Identifiant ou mot de passe incorrect."
        else:
            TENTATIVES.pop("enseignant:" + login, None)
            ouvrir_session(enseignant_id=enseignant["id"])
            return redirect(url_for("tableau_de_bord"))
    flash(erreur, "erreur")
    return render_template("index.html", saisie={"login": login}, onglet="enseignant"), 400


@app.route("/deconnexion", methods=["POST"])
def deconnexion():
    """Ferme la session (élève ou enseignant)."""
    session.clear()
    flash("Vous êtes déconnecté.", "succes")
    return redirect(url_for("accueil"))


# --- Espace élève ---------------------------------------------------------------

@app.route("/eleve")
@eleve_requis
def espace_eleve():
    """Page d'arrivée de l'élève."""
    return render_template("eleve/accueil.html")


# --- Espace enseignant ----------------------------------------------------------

def statut_evaluation(evaluation):
    """Statut affiché d'une évaluation : (clé, libellé)."""
    if evaluation["statut"] == "cloturee":
        return "cloturee", "Clôturée"
    if evaluation["effectif"] and evaluation["saisies"] >= evaluation["effectif"]:
        return "complete", "Complète"
    if evaluation["saisies"] > 0:
        return "en_cours", "En cours"
    if evaluation["date_evaluation"] > date.today().isoformat():
        return "planifiee", "Planifiée"
    return "a_saisir", "À saisir"


def evaluations_avec_progression(conditions="", parametres=()):
    """Évaluations avec leur classe, leur matière, l'effectif et le nombre de notes saisies."""
    lignes = get_db().execute(
        "SELECT ev.*, c.nom AS classe_nom, m.nom AS matiere_nom, m.coefficient, m.enseignant_id, "
        "  (SELECT COUNT(*) FROM eleves e WHERE e.classe_id = ev.classe_id) AS effectif, "
        "  (SELECT COUNT(*) FROM notes n JOIN eleves e ON e.id = n.eleve_id "
        "   WHERE e.classe_id = ev.classe_id AND n.matiere_id = ev.matiere_id "
        "   AND n.sequence = ev.sequence) AS saisies "
        "FROM evaluations ev "
        "JOIN classes c ON c.id = ev.classe_id "
        "JOIN matieres m ON m.id = ev.matiere_id "
        "WHERE 1 = 1 " + conditions + " "
        "ORDER BY ev.sequence DESC, ev.date_evaluation DESC, c.niveau, c.nom",
        parametres).fetchall()
    evaluations = []
    for ligne in lignes:
        evaluation = dict(ligne)
        evaluation["etat"], evaluation["etat_libelle"] = statut_evaluation(evaluation)
        evaluations.append(evaluation)
    return evaluations


@app.route("/enseignant")
@connexion_requise
def tableau_de_bord():
    """Tableau de bord de l'enseignant : ses matières et les évaluations à traiter."""
    db = get_db()
    matieres = db.execute("SELECT * FROM matieres WHERE enseignant_id = ? ORDER BY nom",
                          (g.enseignant["id"],)).fetchall()
    evaluations = evaluations_avec_progression("AND m.enseignant_id = ?", (g.enseignant["id"],))
    a_traiter = [e for e in evaluations if e["etat"] in ("a_saisir", "en_cours")]
    a_venir = sorted((e for e in evaluations if e["etat"] == "planifiee"), key=lambda e: e["date_evaluation"])
    chiffres = db.execute(
        "SELECT (SELECT COUNT(*) FROM classes) AS classes, (SELECT COUNT(*) FROM eleves) AS eleves").fetchone()
    return render_template("enseignant/tableau_de_bord.html", matieres=matieres,
                           a_traiter=a_traiter, a_venir=a_venir, chiffres=chiffres,
                           nombre_evaluations=len(evaluations))


# --- Pages d'erreur ----------------------------------------------------------

@app.errorhandler(403)
def acces_interdit(erreur):
    """Page affichée quand l'utilisateur n'a pas le droit d'accéder à une page."""
    return render_template("403.html"), 403


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
