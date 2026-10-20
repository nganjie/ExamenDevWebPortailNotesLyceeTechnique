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

from flask import (Flask, abort, flash, g, jsonify, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import check_password_hash

import calculs

# --- Configuration -----------------------------------------------------------

DOSSIER = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
# La variable PORTAIL_BASE permet de travailler sur une autre base (copie de test)
app.config["CHEMIN_BASE"] = os.environ.get("PORTAIL_BASE", os.path.join(DOSSIER, "projet.db"))
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
LIGNES_PAR_PAGE = 20

MOTIF_MATRICULE = re.compile(r"^LT[0-9]{2}-F[0-9]-[0-9]{4}$")
MOTIF_CODE = re.compile(r"^[0-9]{6}$")
MOTIF_NOTE = re.compile(r"^[0-9]{1,2}([.,][0-9]{1,2})?$")

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


@app.template_filter("zip")
def associer(premiere, seconde):
    """Associe deux listes deux à deux (options des listes déroulantes)."""
    return list(zip(premiere, seconde))


@app.template_filter("libelle_sequence")
def libelle_sequence(numero):
    """« Séquence 3 »."""
    return f"Séquence {numero}"


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


# --- Bulletins : données communes à l'élève et aux enseignants --------------

def sequences_notees(classe_id):
    """Numéros des séquences pour lesquelles la classe a au moins une note."""
    lignes = get_db().execute(
        "SELECT DISTINCT n.sequence FROM notes n JOIN eleves e ON e.id = n.eleve_id "
        "WHERE e.classe_id = ? ORDER BY n.sequence", (classe_id,)).fetchall()
    return [ligne["sequence"] for ligne in lignes]


def donnees_bulletin(eleve, sequence):
    """Toutes les données du bulletin d'un élève pour une séquence."""
    db = get_db()
    classe = calculs.bulletin_classe(db, eleve["classe_id"], sequence)
    ligne_eleve = next(e for e in classe if e["id"] == eleve["id"])
    moyennes_classe = [e["moyenne"] for e in classe if e["moyenne"] is not None]

    matieres = db.execute(
        "SELECT m.id, m.nom, m.coefficient, en.nom AS enseignant FROM matieres m "
        "JOIN enseignants en ON en.id = m.enseignant_id ORDER BY m.coefficient DESC, m.nom").fetchall()
    lignes = []
    total_points = 0
    total_coefficients = 0
    for matiere in matieres:
        note = ligne_eleve["notes"].get(matiere["id"])
        notes_matiere = [e["notes"].get(matiere["id"]) for e in classe]
        if note is not None:
            total_points += note * matiere["coefficient"]
            total_coefficients += matiere["coefficient"]
        lignes.append({
            "matiere": matiere["nom"],
            "enseignant": matiere["enseignant"],
            "coefficient": matiere["coefficient"],
            "note": note,
            "points": None if note is None else note * matiere["coefficient"],
            "moyenne_classe": calculs.moyenne_simple(notes_matiere),
            "appreciation": calculs.appreciation(note) if note is not None else "Non noté",
        })

    moyenne_classe = calculs.moyenne_simple(moyennes_classe)
    return {
        "sequence": sequence,
        "lignes": lignes,
        "total_points": total_points,
        "total_coefficients": total_coefficients,
        "moyenne": ligne_eleve["moyenne"],
        "appreciation": ligne_eleve["appreciation"],
        "rang": ligne_eleve["rang"],
        "ex_aequo": ligne_eleve["ex_aequo"],
        "effectif": len(classe),
        "classes": len(moyennes_classe),
        "moyenne_classe": moyenne_classe,
        "ecart": None if ligne_eleve["moyenne"] is None or moyenne_classe is None
        else calculs.arrondir(ligne_eleve["moyenne"] - moyenne_classe),
        "plus_forte": max(moyennes_classe) if moyennes_classe else None,
        "plus_faible": min(moyennes_classe) if moyennes_classe else None,
    }


def evolution_eleve(eleve):
    """Moyenne, rang et moyenne de la classe de l'élève pour chaque séquence notée."""
    evolution = []
    for sequence in sequences_notees(eleve["classe_id"]):
        classe = calculs.bulletin_classe(get_db(), eleve["classe_id"], sequence)
        ligne = next(e for e in classe if e["id"] == eleve["id"])
        evolution.append({
            "sequence": sequence,
            "moyenne": ligne["moyenne"],
            "rang": ligne["rang"],
            "effectif": len(classe),
            "moyenne_classe": calculs.moyenne_simple([e["moyenne"] for e in classe]),
        })
    return evolution


# --- Espace élève ---------------------------------------------------------------

@app.route("/eleve")
@eleve_requis
def espace_eleve():
    """Page d'arrivée de l'élève : le bulletin de la dernière séquence notée."""
    sequences = sequences_notees(g.eleve["classe_id"])
    return redirect(url_for("bulletin_eleve", sequence=sequences[-1] if sequences else 1))


@app.route("/eleve/bulletin/<int:sequence>")
@eleve_requis
def bulletin_eleve(sequence):
    """Bulletin de l'élève connecté (jamais celui d'un autre : l'identifiant vient de la session)."""
    if not 1 <= sequence <= NOMBRE_SEQUENCES:
        abort(404)
    sequences = sequences_notees(g.eleve["classe_id"])
    bulletin = donnees_bulletin(g.eleve, sequence) if sequence in sequences else None
    return render_template("eleve/bulletin.html", bulletin=bulletin, sequence=sequence,
                           sequences=sequences, historique=evolution_eleve(g.eleve),
                           nombre_sequences=NOMBRE_SEQUENCES)


# --- API JSON -----------------------------------------------------------------------

def erreur_json(message, code):
    """Réponse d'erreur au format JSON pour les routes de l'API."""
    return jsonify({"erreur": message}), code


@app.route("/api/eleves/<int:eleve_id>/evolution")
def api_evolution_eleve(eleve_id):
    """Moyennes d'un élève par séquence (l'élève lui-même ou un enseignant uniquement)."""
    if g.enseignant is None and (g.eleve is None or g.eleve["id"] != eleve_id):
        return erreur_json("Accès refusé.", 403)
    eleve = get_db().execute("SELECT * FROM eleves WHERE id = ?", (eleve_id,)).fetchone()
    if eleve is None:
        return erreur_json("Élève introuvable.", 404)
    return jsonify({"eleve_id": eleve_id, "matricule": eleve["matricule"],
                    "evolution": evolution_eleve(eleve)})


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


# --- Lecture et vérification des saisies -------------------------------------

def lire_note(texte):
    """Convertit une saisie (« 12,5 ») en note ; renvoie (note ou None, message d'erreur ou None)."""
    texte = (texte or "").strip()
    if texte == "":
        return None, None
    if not MOTIF_NOTE.match(texte):
        return None, "Saisissez un nombre, par exemple 12,5."
    note = float(texte.replace(",", "."))
    if not 0 <= note <= 20:
        return None, "La note doit être comprise entre 0 et 20."
    return note, None


def lire_entier(texte):
    """Convertit une saisie en entier, ou None si ce n'est pas un entier."""
    try:
        return int(texte)
    except (TypeError, ValueError):
        return None


def lire_date(texte):
    """Vérifie une date AAAA-MM-JJ ; renvoie la date ISO ou None."""
    try:
        return date.fromisoformat((texte or "").strip()).isoformat()
    except ValueError:
        return None


def paginer(nombre_total, par_page=LIGNES_PAR_PAGE):
    """Calcule la page demandée (?page=N) : numéro, nombre de pages, bornes des lignes affichées."""
    pages = max(1, -(-nombre_total // par_page))  # division arrondie vers le haut
    page = min(max(lire_entier(request.args.get("page")) or 1, 1), pages)
    debut = (page - 1) * par_page
    return {"page": page, "pages": pages, "total": nombre_total,
            "debut": debut, "fin": min(debut + par_page, nombre_total)}


def adresse_de_retour(defaut):
    """Adresse de retour fournie dans l'URL, acceptée seulement si elle reste sur le site."""
    retour = request.values.get("retour", "")
    if retour.startswith("/") and not retour.startswith("//"):
        return retour
    return defaut


# --- Évaluations, saisie et correction des notes ------------------------------

def est_admin():
    """Vrai si l'enseignant connecté est administrateur."""
    return g.enseignant is not None and g.enseignant["role"] == "administrateur"


def charger_evaluation(evaluation_id):
    """Évaluation demandée, si elle existe (404) et si l'enseignant y a droit (403)."""
    trouvees = evaluations_avec_progression("AND ev.id = ?", (evaluation_id,))
    if not trouvees:
        abort(404)
    evaluation = trouvees[0]
    if not est_admin() and evaluation["enseignant_id"] != g.enseignant["id"]:
        abort(403)
    return evaluation


def matieres_autorisees():
    """Matières que l'enseignant connecté peut évaluer (toutes pour l'administrateur)."""
    if est_admin():
        return get_db().execute("SELECT * FROM matieres ORDER BY nom").fetchall()
    return get_db().execute("SELECT * FROM matieres WHERE enseignant_id = ? ORDER BY nom",
                            (g.enseignant["id"],)).fetchall()


ETATS_EVALUATION = {
    "planifiee": "Planifiée", "a_saisir": "À saisir", "en_cours": "En cours",
    "complete": "Complète", "cloturee": "Clôturée",
}


@app.route("/enseignant/evaluations", methods=["GET", "POST"])
@connexion_requise
def evaluations():
    """Liste filtrable des évaluations et création d'une nouvelle évaluation."""
    db = get_db()
    classes = db.execute("SELECT * FROM classes ORDER BY niveau, nom").fetchall()
    matieres = matieres_autorisees()
    erreurs = {}
    saisie = {}

    if request.method == "POST":
        saisie = request.form.to_dict()
        classe_id = lire_entier(saisie.get("classe_id"))
        matiere_id = lire_entier(saisie.get("matiere_id"))
        sequence = lire_entier(saisie.get("sequence"))
        intitule = saisie.get("intitule", "").strip()
        date_evaluation = lire_date(saisie.get("date_evaluation"))
        if classe_id not in [c["id"] for c in classes]:
            erreurs["classe_id"] = "Choisissez une classe."
        if matiere_id not in [m["id"] for m in matieres]:
            erreurs["matiere_id"] = "Choisissez une de vos matières."
        if sequence is None or not 1 <= sequence <= NOMBRE_SEQUENCES:
            erreurs["sequence"] = "La séquence va de 1 à 6."
        if not 3 <= len(intitule) <= 80:
            erreurs["intitule"] = "L'intitulé doit faire entre 3 et 80 caractères."
        if date_evaluation is None:
            erreurs["date_evaluation"] = "Saisissez une date valide."
        if not erreurs:
            try:
                with db:
                    db.execute(
                        "INSERT INTO evaluations (classe_id, matiere_id, sequence, intitule, date_evaluation) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (classe_id, matiere_id, sequence, intitule, date_evaluation))
                flash("Évaluation créée.", "succes")
                return redirect(url_for("evaluations"))
            except sqlite3.IntegrityError:
                erreurs["sequence"] = ("Cette classe a déjà une évaluation de cette matière "
                                       "pour cette séquence.")
        flash("L'évaluation n'a pas été créée : corrigez les champs signalés.", "erreur")

    # Filtres de la liste (paramètres GET)
    filtre_classe = lire_entier(request.args.get("classe"))
    filtre_sequence = lire_entier(request.args.get("sequence"))
    filtre_statut = request.args.get("statut", "")
    filtre_matiere = lire_entier(request.args.get("matiere"))
    conditions = ""
    parametres = []
    if not est_admin():
        conditions += " AND m.enseignant_id = ?"
        parametres.append(g.enseignant["id"])
    toutes = evaluations_avec_progression(conditions, tuple(parametres))
    if filtre_classe:
        conditions += " AND ev.classe_id = ?"
        parametres.append(filtre_classe)
    if filtre_sequence:
        conditions += " AND ev.sequence = ?"
        parametres.append(filtre_sequence)
    if filtre_matiere:
        conditions += " AND ev.matiere_id = ?"
        parametres.append(filtre_matiere)
    liste = evaluations_avec_progression(conditions, tuple(parametres))
    if filtre_statut in ETATS_EVALUATION:
        liste = [e for e in liste if e["etat"] == filtre_statut]
    pagination = paginer(len(liste))
    liste = liste[pagination["debut"]:pagination["fin"]]

    # Bande des six séquences : état global de chaque séquence
    bande = []
    for numero in range(1, NOMBRE_SEQUENCES + 1):
        de_la_sequence = [e for e in toutes if e["sequence"] == numero]
        if de_la_sequence and all(e["etat"] == "cloturee" for e in de_la_sequence):
            etat = ("cloturee", "Clôturée")
        elif any(e["etat"] in ("en_cours", "complete", "a_saisir") for e in de_la_sequence):
            etat = ("en_cours", "En cours")
        elif de_la_sequence:
            etat = ("planifiee", "Planifiée")
        else:
            etat = ("vide", "À venir")
        bande.append({"numero": numero, "etat": etat[0], "libelle": etat[1], "nombre": len(de_la_sequence)})

    return render_template(
        "enseignant/evaluations.html", evaluations=liste, classes=classes, matieres=matieres,
        bande=bande, etats=ETATS_EVALUATION, erreurs=erreurs, saisie=saisie,
        filtres={"classe": filtre_classe, "sequence": filtre_sequence, "statut": filtre_statut,
                 "matiere": filtre_matiere},
        pagination=pagination,
        aujourdhui=date.today().isoformat(), nombre_sequences=NOMBRE_SEQUENCES,
    ), 400 if erreurs else 200


@app.route("/enseignant/evaluations/<int:evaluation_id>/saisie", methods=["GET", "POST"])
@connexion_requise
def saisie_notes(evaluation_id):
    """Saisie des notes d'une matière pour toute une classe, sur une seule page."""
    evaluation = charger_evaluation(evaluation_id)
    db = get_db()
    eleves = db.execute(
        "SELECT e.id, e.matricule, e.nom, e.prenom, n.id AS note_id, n.note "
        "FROM eleves e LEFT JOIN notes n "
        "  ON n.eleve_id = e.id AND n.matiere_id = ? AND n.sequence = ? "
        "WHERE e.classe_id = ? ORDER BY e.nom, e.prenom",
        (evaluation["matiere_id"], evaluation["sequence"], evaluation["classe_id"])).fetchall()
    date_atteinte = evaluation["date_evaluation"] <= date.today().isoformat()
    saisie_ouverte = evaluation["statut"] == "ouverte" and date_atteinte
    erreurs = {}
    valeurs = {}

    if request.method == "POST":
        if not saisie_ouverte:
            flash("La saisie n'est pas ouverte pour cette évaluation.", "erreur")
            return redirect(url_for("saisie_notes", evaluation_id=evaluation_id))
        nouvelles = []
        for eleve in eleves:
            if eleve["note"] is not None:
                continue  # une note existante ne se modifie que par une correction
            texte = request.form.get(f"note_{eleve['id']}", "")
            valeurs[eleve["id"]] = texte
            note, erreur = lire_note(texte)
            if erreur:
                erreurs[eleve["id"]] = erreur
            elif note is not None:
                nouvelles.append((eleve["id"], evaluation["matiere_id"], evaluation["sequence"],
                                  note, date.today().isoformat()))
        if erreurs:
            flash(f"{len(erreurs)} note(s) refusée(s) : aucune note n'a été enregistrée.", "erreur")
        elif not nouvelles:
            flash("Aucune nouvelle note à enregistrer.", "info")
        else:
            try:
                with db:  # tout ou rien : une transaction pour toutes les notes
                    db.executemany(
                        "INSERT INTO notes (eleve_id, matiere_id, sequence, note, date_saisie) "
                        "VALUES (?, ?, ?, ?, ?)", nouvelles)
                flash(f"{len(nouvelles)} note(s) enregistrée(s).", "succes")
            except sqlite3.IntegrityError:
                flash("Une de ces notes a déjà été saisie entre-temps : rien n'a été enregistré.", "erreur")
            return redirect(url_for("saisie_notes", evaluation_id=evaluation_id))

    existantes = [e["note"] for e in eleves if e["note"] is not None]
    synthese = {
        "moyenne": calculs.moyenne_simple(existantes),
        "saisies": len(existantes),
        "plus_forte": max(existantes) if existantes else None,
        "plus_faible": min(existantes) if existantes else None,
    }
    return render_template("enseignant/saisie.html", evaluation=evaluation, eleves=eleves,
                           erreurs=erreurs, valeurs=valeurs, synthese=synthese,
                           saisie_ouverte=saisie_ouverte, date_atteinte=date_atteinte), \
        400 if erreurs else 200


@app.route("/enseignant/evaluations/<int:evaluation_id>/cloturer", methods=["POST"])
@connexion_requise
def cloturer_evaluation(evaluation_id):
    """Clôture une évaluation dont toutes les notes sont saisies."""
    evaluation = charger_evaluation(evaluation_id)
    if evaluation["saisies"] < evaluation["effectif"]:
        flash("Toutes les notes doivent être saisies avant la clôture.", "erreur")
    else:
        with get_db() as db:
            db.execute("UPDATE evaluations SET statut = 'cloturee' WHERE id = ?", (evaluation_id,))
        flash("Évaluation clôturée : les notes ne se modifient plus que par correction.", "succes")
    return redirect(url_for("saisie_notes", evaluation_id=evaluation_id))


@app.route("/enseignant/evaluations/<int:evaluation_id>/rouvrir", methods=["POST"])
@admin_requis
def rouvrir_evaluation(evaluation_id):
    """Rouvre une évaluation clôturée (administrateur uniquement)."""
    charger_evaluation(evaluation_id)
    with get_db() as db:
        db.execute("UPDATE evaluations SET statut = 'ouverte' WHERE id = ?", (evaluation_id,))
    flash("Évaluation rouverte.", "succes")
    return redirect(url_for("saisie_notes", evaluation_id=evaluation_id))


@app.route("/enseignant/evaluations/<int:evaluation_id>/supprimer", methods=["POST"])
@connexion_requise
def supprimer_evaluation(evaluation_id):
    """Supprime une évaluation qui n'a encore aucune note."""
    evaluation = charger_evaluation(evaluation_id)
    if evaluation["saisies"] > 0:
        flash("Impossible de supprimer une évaluation qui contient des notes.", "erreur")
        return redirect(url_for("saisie_notes", evaluation_id=evaluation_id))
    with get_db() as db:
        db.execute("DELETE FROM evaluations WHERE id = ?", (evaluation_id,))
    flash("Évaluation supprimée.", "succes")
    return redirect(url_for("evaluations"))


@app.route("/enseignant/notes/<int:note_id>/correction", methods=["GET", "POST"])
@connexion_requise
def corriger_note(note_id):
    """Correction motivée d'une note déjà saisie ; l'historique est conservé."""
    db = get_db()
    note = db.execute(
        "SELECT n.*, e.nom, e.prenom, e.matricule, e.classe_id, c.nom AS classe_nom, "
        "       m.nom AS matiere_nom, m.enseignant_id "
        "FROM notes n JOIN eleves e ON e.id = n.eleve_id JOIN classes c ON c.id = e.classe_id "
        "JOIN matieres m ON m.id = n.matiere_id WHERE n.id = ?", (note_id,)).fetchone()
    if note is None:
        abort(404)
    if not est_admin() and note["enseignant_id"] != g.enseignant["id"]:
        abort(403)
    evaluation = db.execute(
        "SELECT id FROM evaluations WHERE classe_id = ? AND matiere_id = ? AND sequence = ?",
        (note["classe_id"], note["matiere_id"], note["sequence"])).fetchone()
    retour = adresse_de_retour(url_for("saisie_notes", evaluation_id=evaluation["id"])
                               if evaluation else url_for("evaluations"))
    erreurs = {}
    saisie = {}

    if request.method == "POST":
        saisie = request.form.to_dict()
        nouvelle, erreur = lire_note(saisie.get("nouvelle_note"))
        motif = saisie.get("motif", "").strip()
        if erreur:
            erreurs["nouvelle_note"] = erreur
        elif nouvelle is None:
            erreurs["nouvelle_note"] = "Saisissez la nouvelle note."
        elif nouvelle == note["note"]:
            erreurs["nouvelle_note"] = "La nouvelle note est identique à l'ancienne."
        if not 5 <= len(motif) <= 200:
            erreurs["motif"] = "Le motif doit faire entre 5 et 200 caractères."
        if not erreurs:
            with db:
                db.execute(
                    "INSERT INTO corrections (note_id, ancienne_note, nouvelle_note, motif, "
                    "enseignant_id, date_correction) VALUES (?, ?, ?, ?, ?, ?)",
                    (note_id, note["note"], nouvelle, motif, g.enseignant["id"], date.today().isoformat()))
                db.execute("UPDATE notes SET note = ?, date_saisie = ? WHERE id = ?",
                           (nouvelle, date.today().isoformat(), note_id))
            flash(f"Note de {note['nom']} {note['prenom']} corrigée : "
                  f"{format_note(note['note'])} → {format_note(nouvelle)}.", "succes")
            return redirect(retour)
        flash("La correction n'a pas été enregistrée.", "erreur")

    historique = db.execute(
        "SELECT co.*, en.nom AS auteur FROM corrections co JOIN enseignants en ON en.id = co.enseignant_id "
        "WHERE co.note_id = ? ORDER BY co.id DESC", (note_id,)).fetchall()
    return render_template("enseignant/correction.html", note=note, historique=historique,
                           erreurs=erreurs, saisie=saisie, retour=retour), 400 if erreurs else 200


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
