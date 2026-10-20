"""Tests de l'espace élève : bulletin, historique et API d'évolution."""

import sqlite3
import unittest

import app as application
from app import app
from tests.test_authentification import connecter_eleve, connecter_enseignant, premier_eleve


def moyenne_attendue(matricule, sequence):
    """Recalcule « à la main » la moyenne coefficientée d'un élève."""
    db = sqlite3.connect(app.config["CHEMIN_BASE"])
    points, coefficients = db.execute(
        "SELECT SUM(n.note * m.coefficient), SUM(m.coefficient) FROM notes n "
        "JOIN matieres m ON m.id = n.matiere_id JOIN eleves e ON e.id = n.eleve_id "
        "WHERE e.matricule = ? AND n.sequence = ?", (matricule, sequence)).fetchone()
    db.close()
    return application.calculs.arrondir(points / coefficients)


class TestEspaceEleve(unittest.TestCase):

    def setUp(self):
        application.TENTATIVES.clear()
        self.client = connecter_eleve()

    def test_arrivee_sur_la_derniere_sequence(self):
        reponse = self.client.get("/eleve")
        self.assertTrue(reponse.headers["Location"].endswith("/eleve/bulletin/2"))

    def test_bulletin_moyenne_juste(self):
        matricule, _ = premier_eleve()
        html = self.client.get("/eleve/bulletin/1").get_data(as_text=True)
        attendue = f"{moyenne_attendue(matricule, 1):.2f}".replace(".", ",")
        self.assertIn(attendue, html)
        self.assertIn("Notes par matière", html)

    def test_sequence_sans_notes(self):
        html = self.client.get("/eleve/bulletin/4").get_data(as_text=True)
        self.assertIn("Aucune note n'a encore été saisie", html)

    def test_sequence_inexistante(self):
        self.assertEqual(self.client.get("/eleve/bulletin/7").status_code, 404)

    def test_api_evolution_de_soi(self):
        reponse = self.client.get("/api/eleves/1/evolution")
        self.assertEqual(reponse.status_code, 200)
        donnees = reponse.get_json()
        self.assertEqual([ligne["sequence"] for ligne in donnees["evolution"]], [1, 2])

    def test_api_evolution_d_un_autre_eleve_refusee(self):
        reponse = self.client.get("/api/eleves/2/evolution")
        self.assertEqual(reponse.status_code, 403)
        self.assertIn("erreur", reponse.get_json())

    def test_api_evolution_pour_un_enseignant(self):
        self.assertEqual(connecter_enseignant().get("/api/eleves/2/evolution").status_code, 200)

    def test_api_sans_connexion(self):
        self.assertEqual(app.test_client().get("/api/eleves/1/evolution").status_code, 403)


if __name__ == "__main__":
    unittest.main()
