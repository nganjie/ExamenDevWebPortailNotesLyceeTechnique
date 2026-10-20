"""calculs.py : moyennes coefficientées, rangs avec ex æquo, appréciations et statistiques.

Les fonctions sont indépendantes de Flask pour pouvoir être testées facilement.
"""

from decimal import ROUND_HALF_UP, Decimal

SEUIL_REUSSITE = 10

# (borne inférieure incluse, libellé) du plus haut au plus bas
APPRECIATIONS = [
    (16, "Très bien"),
    (14, "Bien"),
    (12, "Assez bien"),
    (10, "Passable"),
    (8, "Médiocre"),
    (0, "Insuffisant"),
]

# Tranches des statistiques : (libellé, borne basse incluse, borne haute exclue)
TRANCHES = [
    ("moins de 8", 0, 8),
    ("8 à 10", 8, 10),
    ("10 à 12", 10, 12),
    ("12 à 14", 12, 14),
    ("14 et plus", 14, 20.01),
]


def arrondir(valeur):
    """Arrondit au centième, « 5 vers le haut » (12,345 -> 12,35) ; None reste None."""
    if valeur is None:
        return None
    return float(Decimal(str(valeur)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def moyenne_coefficientee(notes):
    """Moyenne de notes [(note, coefficient), ...] ; les notes absentes (None) sont ignorées.

    Renvoie None s'il n'y a aucune note.
    """
    total_points = 0
    total_coefficients = 0
    for note, coefficient in notes:
        if note is None:
            continue
        total_points += note * coefficient
        total_coefficients += coefficient
    if total_coefficients == 0:
        return None
    return arrondir(total_points / total_coefficients)


def classer(moyennes):
    """Calcule les rangs à partir d'un dictionnaire {clé: moyenne}.

    Même moyenne = même rang ; le suivant prend le rang d'après (1, 2, 2, 4).
    Les élèves sans moyenne (None) n'ont pas de rang.
    """
    classes = sorted(((arrondir(m), cle) for cle, m in moyennes.items() if m is not None),
                     key=lambda paire: paire[0], reverse=True)
    rangs = {cle: None for cle in moyennes}
    rang = 0
    precedente = None
    for position, (moyenne, cle) in enumerate(classes, start=1):
        if moyenne != precedente:
            rang = position
            precedente = moyenne
        rangs[cle] = rang
    return rangs


def appreciation(moyenne):
    """Appréciation automatique selon la moyenne."""
    if moyenne is None:
        return "Non classé"
    for borne, libelle in APPRECIATIONS:
        if moyenne >= borne:
            return libelle
    return "Insuffisant"


def tranche(moyenne):
    """Libellé de la tranche de la moyenne (« 10 à 12 »...)."""
    for libelle, basse, haute in TRANCHES:
        if basse <= moyenne < haute:
            return libelle
    return TRANCHES[-1][0]


def taux_reussite(moyennes):
    """Pourcentage de moyennes supérieures ou égales à 10 (None si la liste est vide)."""
    valeurs = [m for m in moyennes if m is not None]
    if not valeurs:
        return None
    return arrondir(100 * sum(1 for m in valeurs if m >= SEUIL_REUSSITE) / len(valeurs))


def moyenne_simple(valeurs):
    """Moyenne arithmétique d'une liste (None si vide)."""
    valeurs = [v for v in valeurs if v is not None]
    return arrondir(sum(valeurs) / len(valeurs)) if valeurs else None


def repartition(moyennes):
    """Nombre de moyennes par tranche : [{"tranche": ..., "effectif": ...}, ...]."""
    compte = {libelle: 0 for libelle, _, _ in TRANCHES}
    for moyenne in moyennes:
        if moyenne is not None:
            compte[tranche(moyenne)] += 1
    return [{"tranche": libelle, "effectif": compte[libelle]} for libelle, _, _ in TRANCHES]


def bulletin_classe(db, classe_id, sequence):
    """Moyennes, rangs et notes de tous les élèves d'une classe pour une séquence.

    Renvoie une liste de dictionnaires triée par rang puis par nom :
    {id, matricule, nom, prenom, moyenne, rang, ex_aequo, appreciation, notes: {matiere_id: note}}
    """
    lignes = db.execute(
        "SELECT e.id, e.matricule, e.nom, e.prenom, m.id AS matiere_id, m.coefficient, n.note "
        "FROM eleves e "
        "CROSS JOIN matieres m "
        "LEFT JOIN notes n ON n.eleve_id = e.id AND n.matiere_id = m.id AND n.sequence = ? "
        "WHERE e.classe_id = ? "
        "ORDER BY e.nom, e.prenom, m.id",
        (sequence, classe_id)).fetchall()

    eleves = {}
    for ligne in lignes:
        eleve = eleves.setdefault(ligne["id"], {
            "id": ligne["id"], "matricule": ligne["matricule"],
            "nom": ligne["nom"], "prenom": ligne["prenom"],
            "notes": {}, "_coefficients": [],
        })
        eleve["notes"][ligne["matiere_id"]] = ligne["note"]
        eleve["_coefficients"].append((ligne["note"], ligne["coefficient"]))

    moyennes = {}
    for eleve in eleves.values():
        eleve["moyenne"] = moyenne_coefficientee(eleve.pop("_coefficients"))
        moyennes[eleve["id"]] = eleve["moyenne"]

    rangs = classer(moyennes)
    nombre_par_rang = {}
    for rang in rangs.values():
        nombre_par_rang[rang] = nombre_par_rang.get(rang, 0) + 1
    for eleve in eleves.values():
        eleve["rang"] = rangs[eleve["id"]]
        eleve["ex_aequo"] = eleve["rang"] is not None and nombre_par_rang[eleve["rang"]] > 1
        eleve["appreciation"] = appreciation(eleve["moyenne"])

    return sorted(eleves.values(),
                  key=lambda e: (e["rang"] is None, e["rang"] or 0, e["nom"], e["prenom"]))
