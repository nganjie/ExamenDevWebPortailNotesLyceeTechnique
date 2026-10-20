"""Tests du module calculs : moyennes, rangs ex æquo, appréciations, statistiques."""

import sqlite3
import unittest

import calculs
from app import app


class TestCalculs(unittest.TestCase):
    """Règles de calcul de la spec de l'étape 03."""

    def test_moyenne_coefficientee(self):
        # (12 x 4 + 15 x 5 + 9 x 1) / 10 = 13,2
        self.assertEqual(calculs.moyenne_coefficientee([(12, 4), (15, 5), (9, 1)]), 13.2)

    def test_matiere_non_notee_exclue(self):
        self.assertEqual(calculs.moyenne_coefficientee([(12, 4), (None, 5)]), 12.0)

    def test_aucune_note(self):
        self.assertIsNone(calculs.moyenne_coefficientee([(None, 4), (None, 2)]))

    def test_arrondi_cinq_vers_le_haut(self):
        self.assertEqual(calculs.arrondir(12.345), 12.35)
        self.assertEqual(calculs.arrondir(12.344), 12.34)

    def test_rangs_ex_aequo(self):
        rangs = calculs.classer({"a": 15, "b": 12.5, "c": 12.5, "d": 11, "e": None})
        self.assertEqual(rangs, {"a": 1, "b": 2, "c": 2, "d": 4, "e": None})

    def test_ex_aequo_en_tete(self):
        rangs = calculs.classer({"a": 14, "b": 14, "c": 14, "d": 9})
        self.assertEqual([rangs[c] for c in "abcd"], [1, 1, 1, 4])

    def test_ex_aequo_sur_moyennes_arrondies(self):
        rangs = calculs.classer({"a": 12.4999999, "b": 12.5})
        self.assertEqual(rangs["a"], rangs["b"])

    def test_appreciations_aux_bornes(self):
        self.assertEqual(calculs.appreciation(7.99), "Insuffisant")
        self.assertEqual(calculs.appreciation(8), "Médiocre")
        self.assertEqual(calculs.appreciation(10), "Passable")
        self.assertEqual(calculs.appreciation(12), "Assez bien")
        self.assertEqual(calculs.appreciation(14), "Bien")
        self.assertEqual(calculs.appreciation(16), "Très bien")
        self.assertEqual(calculs.appreciation(None), "Non classé")

    def test_tranches(self):
        self.assertEqual(calculs.tranche(7.99), "moins de 8")
        self.assertEqual(calculs.tranche(10), "10 à 12")
        self.assertEqual(calculs.tranche(20), "14 et plus")

    def test_taux_reussite_et_repartition(self):
        moyennes = [7, 9.5, 10, 12, 15, None]
        self.assertEqual(calculs.taux_reussite(moyennes), 60.0)
        effectifs = [t["effectif"] for t in calculs.repartition(moyennes)]
        self.assertEqual(effectifs, [1, 1, 1, 1, 1])


class TestBulletinClasse(unittest.TestCase):
    """bulletin_classe sur la base de test."""

    def setUp(self):
        self.db = sqlite3.connect(app.config["CHEMIN_BASE"])
        self.db.row_factory = sqlite3.Row

    def tearDown(self):
        self.db.close()

    def test_classe_complete(self):
        eleves = calculs.bulletin_classe(self.db, 1, 1)
        self.assertEqual(len(eleves), 30)
        self.assertEqual(eleves[0]["rang"], 1)
        # rangs croissants quand la moyenne décroît
        for avant, apres in zip(eleves, eleves[1:]):
            self.assertGreaterEqual(avant["moyenne"], apres["moyenne"])
            if avant["moyenne"] == apres["moyenne"]:
                self.assertEqual(avant["rang"], apres["rang"])
                self.assertTrue(avant["ex_aequo"] and apres["ex_aequo"])
            else:
                self.assertEqual(apres["rang"], eleves.index(apres) + 1)
        self.assertEqual(len(eleves[0]["notes"]), 8)

    def test_sequence_sans_notes(self):
        eleves = calculs.bulletin_classe(self.db, 1, 5)
        self.assertTrue(all(e["moyenne"] is None and e["rang"] is None for e in eleves))


if __name__ == "__main__":
    unittest.main()
