"""Tests de l'administration des classes et des élèves (sur une copie de la base)."""

import re
import sqlite3

import app as application
from app import app
from tests.outils import TestSurCopie
from tests.test_authentification import ClientAvecJeton, connecter_enseignant


def requete(sql, parametres=()):
    db = sqlite3.connect(app.config["CHEMIN_BASE"])
    resultat = db.execute(sql, parametres).fetchall()
    db.close()
    return resultat


class TestAdministration(TestSurCopie):

    def setUp(self):
        application.TENTATIVES.clear()
        self.admin = connecter_enseignant()

    def nouvelle_classe(self, nom, effectif_max=35):
        return self.admin.post("/admin/classes", {"nom": nom, "niveau": "1", "filiere": "F3",
                                                  "effectif_max": str(effectif_max), "professeur_principal_id": ""})

    def ajouter_eleve(self, classe_id, nom="MBIDA", prenom="Laure", matricule=""):
        return self.admin.post("/admin/eleves", {"nom": nom, "prenom": prenom, "date_naissance": "2011-03-14",
                                                 "classe_id": str(classe_id), "matricule": matricule},
                               follow_redirects=True)

    def test_reserve_aux_administrateurs(self):
        prof = connecter_enseignant("p.atangana", "Prof!2026")
        self.assertEqual(prof.get("/admin/classes").status_code, 403)
        self.assertEqual(prof.get("/admin/eleves").status_code, 403)
        self.assertEqual(ClientAvecJeton().get("/admin/eleves").status_code, 302)

    def test_creation_et_doublon_de_classe(self):
        self.assertEqual(self.nouvelle_classe("1re année F3").status_code, 302)
        reponse = self.nouvelle_classe("1re année F3")
        self.assertEqual(reponse.status_code, 400)
        self.assertIn("Une classe porte déjà ce nom", reponse.get_data(as_text=True))

    def test_effectif_maximal_sous_l_effectif(self):
        reponse = self.admin.post("/admin/classes/1/modifier", {"nom": "1re année F4", "niveau": "1", "filiere": "F4",
                                                               "effectif_max": "20", "professeur_principal_id": ""})
        self.assertEqual(reponse.status_code, 400)
        self.assertEqual(requete("SELECT effectif_max FROM classes WHERE id = 1")[0][0], 35)

    def test_ajout_eleve_puis_connexion_avec_le_code(self):
        html = self.ajouter_eleve(2).get_data(as_text=True)
        code = re.search(r'class="code-acces">(\d{3}) (\d{3})<', html)
        self.assertIsNotNone(code)
        matricule = requete("SELECT matricule FROM eleves WHERE nom = 'MBIDA'")[0][0]
        self.assertEqual(matricule, "LT25-F3-0031")  # numéro suivant de la classe
        eleve = ClientAvecJeton()
        reponse = eleve.post("/connexion/eleve", {"matricule": matricule, "code": code.group(1) + code.group(2)})
        self.assertEqual(reponse.status_code, 302)
        # le code n'est affiché qu'une fois
        self.assertNotIn('class="code-acces"', self.admin.get("/admin/eleves?classe=2").get_data(as_text=True))

    def test_classe_pleine(self):
        self.nouvelle_classe("Classe test pleine", effectif_max=1)
        classe_id = requete("SELECT id FROM classes WHERE nom = 'Classe test pleine'")[0][0]
        self.ajouter_eleve(classe_id, "PREMIER", "Eleve")
        html = self.ajouter_eleve(classe_id, "SECOND", "Eleve").get_data(as_text=True)
        self.assertIn("est pleine", html)
        self.assertEqual(requete("SELECT COUNT(*) FROM eleves WHERE classe_id = ?", (classe_id,))[0][0], 1)

    def test_matricule_en_double(self):
        html = self.ajouter_eleve(3, matricule="LT26-F4-0001").get_data(as_text=True)
        self.assertIn("déjà utilisé", html)

    def test_nouveau_code_et_suppression(self):
        empreinte = requete("SELECT code_empreinte FROM eleves WHERE id = 40")[0][0]
        self.admin.post("/admin/eleves/40/nouveau-code")
        self.assertNotEqual(requete("SELECT code_empreinte FROM eleves WHERE id = 40")[0][0], empreinte)
        self.admin.post("/admin/eleves/40/supprimer")
        self.assertEqual(requete("SELECT COUNT(*) FROM notes WHERE eleve_id = 40")[0][0], 0)

    def test_classe_non_vide_non_supprimee(self):
        self.admin.post("/admin/classes/1/supprimer")
        self.assertEqual(requete("SELECT COUNT(*) FROM classes WHERE id = 1")[0][0], 1)

    def test_recherche_et_export_csv(self):
        html = self.admin.get("/admin/eleves?q=LT26-F4-0001").get_data(as_text=True)
        self.assertIn("LT26-F4-0001", html)
        reponse = self.admin.get("/admin/eleves/export.csv?classe=1")
        self.assertEqual(reponse.mimetype, "text/csv")
        lignes = reponse.get_data(as_text=True).lstrip("﻿").strip().splitlines()
        self.assertEqual(lignes[0], "matricule;nom;prenom;date_naissance;classe;code_remis")
        self.assertEqual(len(lignes), 31)
