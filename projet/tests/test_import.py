"""Tests de l'import d'élèves : lecture des formats, vérifications, parcours complet."""

import csv
import io
import os
import sqlite3
import unittest
from datetime import date

import app as application
import importation
from app import app
from tests.outils import TestSurCopie
from tests.test_authentification import ClientAvecJeton, connecter_enseignant

EXEMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exemples_import")


def lire_exemple(extension):
    nom = "eleves_exemple" + extension
    with open(os.path.join(EXEMPLES, nom), "rb") as fichier:
        return importation.lire_fichier(nom, fichier.read())


class TestLectureFichiers(unittest.TestCase):

    def analyser(self, lignes, places=35):
        correspondance = importation.deviner_correspondance(lignes[0])
        return importation.analyser_lignes(lignes, correspondance, {"LT25-F3-0028"}, places, date(2026, 10, 20))

    def test_trois_formats_meme_resultat(self):
        etats = [[(r["nom"], r["etat"]) for r in self.analyser(lire_exemple(ext))] for ext in (".csv", ".xlsx", ".ods")]
        self.assertEqual(etats[0], etats[1])
        self.assertEqual(etats[0], etats[2])

    def test_verifications(self):
        resultats = {r["nom"]: r for r in self.analyser(lire_exemple(".csv"))}
        self.assertEqual(resultats["MBIDA"]["message"], "Date invalide")
        self.assertEqual(resultats["OYONO"]["message"], "Prénom manquant")
        self.assertEqual(resultats["NGO BASSA"]["etat"], "doublon")
        self.assertEqual(sum(1 for r in resultats.values() if r["etat"] == "valide"), 7)

    def test_classe_pleine(self):
        resultats = self.analyser(lire_exemple(".csv"), places=5)
        self.assertEqual(sum(1 for r in resultats if r["etat"] == "valide"), 5)
        self.assertEqual(sum(1 for r in resultats if r["message"] == "Classe pleine"), 2)

    def test_correspondance_devinee(self):
        correspondance = importation.deviner_correspondance(["N°", "NOM", "PRÉNOMS", "Né(e) le", "Matricule"])
        self.assertEqual(correspondance, {"nom": 1, "prenom": 2, "date_naissance": 3, "matricule": 4})

    def test_dates(self):
        self.assertEqual(importation.normaliser_date("05/09/2011"), "2011-09-05")
        self.assertEqual(importation.normaliser_date("2011-09-05"), "2011-09-05")
        self.assertIsNone(importation.normaliser_date("31/02/2011"))

    def test_format_refuse(self):
        with self.assertRaises(importation.ErreurFichier):
            importation.lire_fichier("eleves.pdf", b"%PDF")
        with self.assertRaises(importation.ErreurFichier):
            importation.lire_fichier("eleves.xlsx", b"pas un classeur")

    def test_csv_windows_1252_virgules(self):
        lignes = importation.lire_fichier("e.csv", "nom,prénom,date\nÉTOA,Hélène,01/02/2011\n".encode("cp1252"))
        self.assertEqual(lignes[1], ["ÉTOA", "Hélène", "01/02/2011"])


class TestParcoursImport(TestSurCopie):

    def setUp(self):
        application.TENTATIVES.clear()
        self.admin = connecter_enseignant()

    def envoyer(self, extension, classe_id):
        with open(os.path.join(EXEMPLES, "eleves_exemple" + extension), "rb") as fichier:
            contenu = fichier.read()
        return self.admin.post("/admin/import/analyse",
                               {"classe_id": str(classe_id), "fichier": (io.BytesIO(contenu), "eleves" + extension)},
                               content_type="multipart/form-data")

    def test_parcours_complet(self):
        # la classe 2 (2e année F3) a 5 places : 5 élèves importés, le reste ignoré
        html = self.envoyer(".xlsx", 2).get_data(as_text=True)
        self.assertIn("Importer 5 élève(s)", html)
        html = self.admin.post("/admin/import/confirmer").get_data(as_text=True)
        self.assertIn("5 élève(s) importé(s)", html)
        db = sqlite3.connect(app.config["CHEMIN_BASE"])
        self.assertEqual(db.execute("SELECT COUNT(*) FROM eleves WHERE classe_id = 2").fetchone()[0], 35)
        db.close()

        # liste des codes : un seul téléchargement, et les codes permettent de se connecter
        reponse = self.admin.get("/admin/import/codes.csv")
        self.assertEqual(reponse.status_code, 200)
        lignes = list(csv.DictReader(io.StringIO(reponse.get_data(as_text=True).lstrip("﻿")), delimiter=";"))
        self.assertEqual(len(lignes), 5)
        self.assertEqual(self.admin.get("/admin/import/codes.csv").status_code, 404)
        eleve = ClientAvecJeton()
        reponse = eleve.post("/connexion/eleve", {"matricule": lignes[0]["matricule"], "code": lignes[0]["code_acces"]})
        self.assertEqual(reponse.status_code, 302)

    def test_mauvais_format(self):
        reponse = self.admin.post("/admin/import/analyse",
                                  {"classe_id": "1", "fichier": (io.BytesIO(b"x"), "eleves.pdf")},
                                  content_type="multipart/form-data", follow_redirects=True)
        self.assertIn("Format non accepté", reponse.get_data(as_text=True))

    def test_reserve_aux_administrateurs(self):
        prof = connecter_enseignant("p.atangana", "Prof!2026")
        self.assertEqual(prof.get("/admin/import").status_code, 403)

    def test_modeles(self):
        self.assertIn("nom;prenom", self.admin.get("/admin/import/modele.csv").get_data(as_text=True))
        self.assertEqual(self.admin.get("/admin/import/modele.xlsx").status_code, 200)
        self.assertEqual(self.admin.get("/admin/import/modele.pdf").status_code, 404)
