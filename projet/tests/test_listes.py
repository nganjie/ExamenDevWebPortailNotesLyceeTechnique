"""Tests des listes de classe, de la fiche élève et de l'API des moyennes."""

import unittest

import app as application
from app import app
from tests.test_authentification import ClientAvecJeton, connecter_eleve, connecter_enseignant


class TestListes(unittest.TestCase):

    def setUp(self):
        application.TENTATIVES.clear()
        self.client = connecter_enseignant()

    def test_choix_des_classes(self):
        html = self.client.get("/enseignant/classes").get_data(as_text=True)
        for nom in ("1re année F4", "2e année F3", "3e année F2", "4e année F1"):
            self.assertIn(nom, html)

    def test_liste_de_classe(self):
        reponse = self.client.get("/enseignant/classes/2?sequence=1")
        self.assertEqual(reponse.status_code, 200)
        self.assertIn("Classement", reponse.get_data(as_text=True))

    def test_sequence_invalide(self):
        self.assertEqual(self.client.get("/enseignant/classes/2?sequence=9").status_code, 404)
        self.assertEqual(self.client.get("/enseignant/classes/99").status_code, 404)

    def test_api_moyennes(self):
        donnees = self.client.get("/api/classe/1/moyennes?sequence=2").get_json()
        self.assertEqual(donnees["classe"]["id"], 1)
        self.assertEqual(len(donnees["eleves"]), 30)
        rangs = [e["rang"] for e in donnees["eleves"]]
        self.assertEqual(rangs, sorted(rangs))
        self.assertEqual(sum(t["effectif"] for t in donnees["repartition"]), 30)

    def test_api_rang_egal_au_bulletin(self):
        # le rang donné par l'API pour l'élève n°1 est celui de son propre bulletin
        donnees = self.client.get("/api/classe/1/moyennes?sequence=1").get_json()
        rang_api = next(e["rang"] for e in donnees["eleves"] if e["id"] == 1)
        evolution = connecter_eleve().get("/api/eleves/1/evolution").get_json()["evolution"]
        self.assertEqual(rang_api, evolution[0]["rang"])

    def test_api_refusee_aux_eleves_et_visiteurs(self):
        self.assertEqual(connecter_eleve().get("/api/classe/1/moyennes").status_code, 403)
        self.assertEqual(ClientAvecJeton().get("/api/classe/1/moyennes").status_code, 403)
        self.assertEqual(self.client.get("/api/classe/99/moyennes").status_code, 404)

    def test_fiche_eleve_avec_correction(self):
        html = self.client.get("/enseignant/eleves/1?sequence=1").get_data(as_text=True)
        self.assertIn("Notes par matière", html)
        self.assertIn("Corriger", html)

    def test_fiche_sans_correction_pour_les_autres_matieres(self):
        prof = connecter_enseignant("p.atangana", "Prof!2026")
        html = prof.get("/enseignant/eleves/1?sequence=1").get_data(as_text=True)
        self.assertEqual(html.count("Corriger la note de"), 1)  # seulement les mathématiques


if __name__ == "__main__":
    unittest.main()
