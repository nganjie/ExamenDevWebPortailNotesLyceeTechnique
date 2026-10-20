"""Tests des pages publiques et des gabarits communs."""

import re
import unittest

from app import app


class TestPages(unittest.TestCase):
    """Accueil, page 404, jeton CSRF."""

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_accueil(self):
        reponse = self.client.get("/")
        self.assertEqual(reponse.status_code, 200)
        html = reponse.get_data(as_text=True)
        self.assertIn('<html lang="fr">', html)
        # chaque champ visible a un label associé
        for identifiant in re.findall(r'<input id="([^"]+)"', html):
            self.assertIn(f'for="{identifiant}"', html)

    def test_page_404_personnalisee(self):
        reponse = self.client.get("/page-qui-n-existe-pas")
        self.assertEqual(reponse.status_code, 404)
        self.assertIn("Page introuvable", reponse.get_data(as_text=True))

    def test_post_sans_jeton_refuse(self):
        reponse = self.client.post("/connexion/eleve", data={"matricule": "LT25-F3-0001", "code": "123456"})
        self.assertEqual(reponse.status_code, 400)

    def test_aucune_ressource_externe(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertNotRegex(html, r'(src|href)="https?://')


if __name__ == "__main__":
    unittest.main()
