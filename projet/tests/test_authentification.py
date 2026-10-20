"""Tests de la connexion des élèves et des enseignants, et des accès protégés."""

import csv
import os
import unittest

import app as application
from app import app

DOSSIER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def premier_eleve():
    """Matricule et code d'un élève de test (fichier généré par donnees_test.py)."""
    with open(os.path.join(DOSSIER, "codes_eleves_test.csv"), encoding="utf-8") as fichier:
        ligne = next(csv.DictReader(fichier, delimiter=";"))
    return ligne["matricule"], ligne["code_acces"]


class ClientAvecJeton:
    """Petit utilitaire : envoie les formulaires avec le jeton CSRF de la session."""

    def __init__(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.client.get("/")

    def jeton(self):
        with self.client.session_transaction() as session:
            if "jeton_csrf" not in session:
                session["jeton_csrf"] = "jeton-test"
            return session["jeton_csrf"]

    def post(self, adresse, donnees=None, **options):
        donnees = dict(donnees or {}, jeton_csrf=self.jeton())
        return self.client.post(adresse, data=donnees, **options)

    def get(self, adresse, **options):
        return self.client.get(adresse, **options)


def connecter_enseignant(login="admin", mot_de_passe="Admin!2026"):
    client = ClientAvecJeton()
    client.post("/connexion/enseignant", {"login": login, "mot_de_passe": mot_de_passe})
    return client


def connecter_eleve():
    client = ClientAvecJeton()
    matricule, code = premier_eleve()
    client.post("/connexion/eleve", {"matricule": matricule, "code": code})
    return client


class TestAuthentification(unittest.TestCase):

    def setUp(self):
        application.TENTATIVES.clear()

    def test_connexion_eleve_reussie(self):
        client = ClientAvecJeton()
        matricule, code = premier_eleve()
        reponse = client.post("/connexion/eleve", {"matricule": matricule, "code": code})
        self.assertEqual(reponse.status_code, 302)
        self.assertTrue(reponse.headers["Location"].endswith("/eleve"))

    def test_connexion_eleve_code_faux(self):
        client = ClientAvecJeton()
        matricule, _ = premier_eleve()
        reponse = client.post("/connexion/eleve", {"matricule": matricule, "code": "000000"})
        self.assertEqual(reponse.status_code, 400)
        self.assertIn("Matricule ou code incorrect", reponse.get_data(as_text=True))

    def test_format_revérifie_par_le_serveur(self):
        client = ClientAvecJeton()
        reponse = client.post("/connexion/eleve", {"matricule": "1 OR 1=1", "code": "12"})
        self.assertIn("Le matricule doit avoir la forme", reponse.get_data(as_text=True))

    def test_limitation_des_essais(self):
        client = ClientAvecJeton()
        matricule, code = premier_eleve()
        for _ in range(5):
            client.post("/connexion/eleve", {"matricule": matricule, "code": "000000"})
        reponse = client.post("/connexion/eleve", {"matricule": matricule, "code": code})
        self.assertIn("Trop de tentatives", reponse.get_data(as_text=True))

    def test_connexion_enseignant(self):
        client = connecter_enseignant()
        reponse = client.get("/enseignant")
        self.assertEqual(reponse.status_code, 200)
        self.assertIn("Bonjour, M. Fotso Jean", reponse.get_data(as_text=True))

    def test_mot_de_passe_faux(self):
        client = ClientAvecJeton()
        reponse = client.post("/connexion/enseignant", {"login": "admin", "mot_de_passe": "faux"})
        self.assertIn("Identifiant ou mot de passe incorrect", reponse.get_data(as_text=True))

    def test_espace_enseignant_refuse_sans_connexion(self):
        reponse = ClientAvecJeton().get("/enseignant")
        self.assertEqual(reponse.status_code, 302)

    def test_espace_enseignant_refuse_a_un_eleve(self):
        self.assertEqual(connecter_eleve().get("/enseignant").status_code, 403)

    def test_deconnexion(self):
        client = connecter_eleve()
        self.assertEqual(client.get("/eleve").status_code, 200)
        client.post("/deconnexion")
        self.assertEqual(client.get("/eleve").status_code, 302)


if __name__ == "__main__":
    unittest.main()
