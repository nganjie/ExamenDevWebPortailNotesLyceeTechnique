"""Tests des évaluations, de la saisie des notes et des corrections."""

import sqlite3
from datetime import date, timedelta

import app as application
from app import app
from tests.outils import TestSurCopie
from tests.test_authentification import connecter_enseignant

AUJOURDHUI = date.today().isoformat()


def requete(sql, parametres=()):
    db = sqlite3.connect(app.config["CHEMIN_BASE"])
    resultat = db.execute(sql, parametres).fetchall()
    db.close()
    return resultat


class TestEvaluations(TestSurCopie):

    def setUp(self):
        application.TENTATIVES.clear()
        self.admin = connecter_enseignant()
        self.prof_maths = connecter_enseignant("p.atangana", "Prof!2026")

    def creer(self, client, sequence, matiere_id=1, classe_id=1, jour=AUJOURDHUI):
        return client.post("/enseignant/evaluations", {
            "intitule": "Devoir test", "classe_id": classe_id, "matiere_id": matiere_id,
            "sequence": sequence, "date_evaluation": jour})

    def id_evaluation(self, sequence, matiere_id=1, classe_id=1):
        return requete("SELECT id FROM evaluations WHERE classe_id = ? AND matiere_id = ? AND sequence = ?",
                       (classe_id, matiere_id, sequence))[0][0]

    def test_liste(self):
        html = self.admin.get("/enseignant/evaluations").get_data(as_text=True)
        self.assertIn("Devoir surveillé n°2", html)

    def test_creation_et_doublon(self):
        self.assertEqual(self.creer(self.admin, 5).status_code, 302)
        reponse = self.creer(self.admin, 5)
        self.assertEqual(reponse.status_code, 400)
        self.assertIn("déjà une évaluation", reponse.get_data(as_text=True))

    def test_enseignant_limite_a_ses_matieres(self):
        # le professeur de mathématiques ne peut pas créer en électrotechnique (matière 1)
        self.assertEqual(self.creer(self.prof_maths, 6, matiere_id=1).status_code, 400)
        evaluation = self.id_evaluation(1)
        self.assertEqual(self.prof_maths.get(f"/enseignant/evaluations/{evaluation}/saisie").status_code, 403)

    def test_saisie_tout_ou_rien(self):
        self.creer(self.admin, 4)
        evaluation = self.id_evaluation(4)
        donnees = {"note_1": "12,5", "note_2": "22", "note_3": "15"}
        reponse = self.admin.post(f"/enseignant/evaluations/{evaluation}/saisie", donnees)
        self.assertEqual(reponse.status_code, 400)
        self.assertIn("note(s) refusée(s)", reponse.get_data(as_text=True))
        self.assertEqual(requete("SELECT COUNT(*) FROM notes WHERE sequence = 4")[0][0], 0)

        donnees["note_2"] = "8.75"
        self.admin.post(f"/enseignant/evaluations/{evaluation}/saisie", donnees)
        notes = requete("SELECT eleve_id, note FROM notes WHERE sequence = 4 ORDER BY eleve_id")
        self.assertEqual(notes, [(1, 12.5), (2, 8.75), (3, 15.0)])

        # une note déjà saisie n'est jamais écrasée par la saisie
        self.admin.post(f"/enseignant/evaluations/{evaluation}/saisie", {"note_1": "3"})
        self.assertEqual(requete("SELECT note FROM notes WHERE sequence = 4 AND eleve_id = 1")[0][0], 12.5)

    def test_saisie_refusee_avant_la_date(self):
        demain = (date.today() + timedelta(days=3)).isoformat()
        self.creer(self.admin, 6, jour=demain)
        evaluation = self.id_evaluation(6)
        self.admin.post(f"/enseignant/evaluations/{evaluation}/saisie", {"note_1": "10"})
        self.assertEqual(requete("SELECT COUNT(*) FROM notes WHERE sequence = 6")[0][0], 0)

    def test_cloture_et_reouverture(self):
        evaluation = self.id_evaluation(2)
        self.admin.post(f"/enseignant/evaluations/{evaluation}/cloturer")
        self.assertEqual(requete("SELECT statut FROM evaluations WHERE id = ?", (evaluation,))[0][0], "cloturee")
        self.admin.post(f"/enseignant/evaluations/{evaluation}/rouvrir")
        self.assertEqual(requete("SELECT statut FROM evaluations WHERE id = ?", (evaluation,))[0][0], "ouverte")

    def test_correction(self):
        note_id, ancienne = requete("SELECT id, note FROM notes WHERE eleve_id = 5 AND matiere_id = 1 AND sequence = 1")[0]
        nouvelle = 19.5 if ancienne != 19.5 else 18
        reponse = self.admin.post(f"/enseignant/notes/{note_id}/correction",
                                  {"nouvelle_note": str(nouvelle), "motif": "Erreur de report"})
        self.assertEqual(reponse.status_code, 302)
        self.assertEqual(requete("SELECT note FROM notes WHERE id = ?", (note_id,))[0][0], nouvelle)
        self.assertEqual(requete("SELECT ancienne_note, nouvelle_note FROM corrections WHERE note_id = ?", (note_id,)),
                         [(ancienne, nouvelle)])

    def test_correction_invalide(self):
        note_id = requete("SELECT id FROM notes WHERE eleve_id = 6 AND matiere_id = 1 AND sequence = 1")[0][0]
        reponse = self.admin.post(f"/enseignant/notes/{note_id}/correction", {"nouvelle_note": "25", "motif": "x"})
        self.assertEqual(reponse.status_code, 400)
        self.assertEqual(requete("SELECT COUNT(*) FROM corrections WHERE note_id = ?", (note_id,))[0][0], 0)

    def test_correction_refusee_a_un_autre_professeur(self):
        note_id = requete("SELECT id FROM notes WHERE matiere_id = 1 LIMIT 1")[0][0]
        self.assertEqual(self.prof_maths.get(f"/enseignant/notes/{note_id}/correction").status_code, 403)

    def test_suppression(self):
        self.creer(self.admin, 3, classe_id=2, matiere_id=3)
        evaluation = self.id_evaluation(3, matiere_id=3, classe_id=2)
        self.admin.post(f"/enseignant/evaluations/{evaluation}/supprimer")
        self.assertEqual(requete("SELECT COUNT(*) FROM evaluations WHERE id = ?", (evaluation,))[0][0], 0)
