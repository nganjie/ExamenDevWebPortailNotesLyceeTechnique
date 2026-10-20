"""Tests de la page et de l'API des statistiques."""

import sqlite3
import unittest

import app as application
from app import app
from tests.test_authentification import connecter_eleve, connecter_enseignant


class TestStatistiques(unittest.TestCase):

    def setUp(self):
        application.TENTATIVES.clear()
        self.client = connecter_enseignant("p.atangana", "Prof!2026")

    def test_page(self):
        html = self.client.get("/enseignant/statistiques?sequence=1").get_data(as_text=True)
        self.assertIn("Résultats de la séquence 1", html)
        self.assertIn("Les 3 premiers de chaque classe", html)

    def test_api_coherente(self):
        stats = self.client.get("/api/statistiques?sequence=2").get_json()
        self.assertEqual(stats["sequence"], 2)
        self.assertEqual(sum(t["effectif"] for t in stats["repartition"]), stats["effectif_total"])
        self.assertEqual(stats["effectif_total"], 120)
        self.assertEqual(len(stats["classes"]), 4)
        self.assertEqual(len(stats["matieres"]), 8)

    def test_moyenne_matiere_recalculee(self):
        stats = self.client.get("/api/statistiques?sequence=1").get_json()
        db = sqlite3.connect(app.config["CHEMIN_BASE"])
        attendue = db.execute(
            "SELECT AVG(n.note) FROM notes n JOIN eleves e ON e.id = n.eleve_id "
            "WHERE n.sequence = 1 AND n.matiere_id = 1 AND e.classe_id = 1").fetchone()[0]
        db.close()
        matiere = next(m for m in stats["matieres"] if m["id"] == 1)
        self.assertEqual(matiere["moyennes"]["1"], application.calculs.arrondir(attendue))

    def test_podium(self):
        stats = self.client.get("/api/statistiques?sequence=1").get_json()
        for groupe in stats["premiers"]:
            self.assertGreaterEqual(len(groupe["eleves"]), 3)
            self.assertTrue(all(e["rang"] <= 3 for e in groupe["eleves"]))

    def test_droits(self):
        self.assertEqual(connecter_eleve().get("/api/statistiques").status_code, 403)
        self.assertEqual(self.client.get("/enseignant/statistiques?sequence=8").status_code, 404)


if __name__ == "__main__":
    unittest.main()
