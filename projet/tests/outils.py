"""Outils communs aux tests qui modifient la base : ils travaillent sur une copie temporaire."""

import os
import shutil
import tempfile
import unittest

from app import app


class TestSurCopie(unittest.TestCase):
    """Classe de base : copie projet.db avant chaque classe de tests, puis la supprime."""

    @classmethod
    def setUpClass(cls):
        cls.dossier = tempfile.TemporaryDirectory()
        cls.chemin_original = app.config["CHEMIN_BASE"]
        copie = os.path.join(cls.dossier.name, "copie.db")
        shutil.copy(cls.chemin_original, copie)
        app.config["CHEMIN_BASE"] = copie

    @classmethod
    def tearDownClass(cls):
        app.config["CHEMIN_BASE"] = cls.chemin_original
        cls.dossier.cleanup()
