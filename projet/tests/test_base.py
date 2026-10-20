"""Tests de la base de données et des données de test."""

import os
import sqlite3
import tempfile
import unittest

import donnees_test


class TestBase(unittest.TestCase):
    """Vérifie les volumes demandés par le sujet et les contraintes du schéma."""

    @classmethod
    def setUpClass(cls):
        cls.dossier = tempfile.TemporaryDirectory()
        cls.chemin = os.path.join(cls.dossier.name, "test.db")
        cls.volumes = donnees_test.creer_base(cls.chemin, os.path.join(cls.dossier.name, "codes.csv"))

    @classmethod
    def tearDownClass(cls):
        cls.dossier.cleanup()

    def setUp(self):
        self.db = sqlite3.connect(self.chemin)
        self.db.execute("PRAGMA foreign_keys = ON")

    def tearDown(self):
        self.db.rollback()
        self.db.close()

    def test_volumes_minimum(self):
        self.assertGreaterEqual(self.volumes["classes"], 4)
        self.assertGreaterEqual(self.volumes["eleves"], 120)
        self.assertGreaterEqual(self.volumes["matieres"], 8)
        self.assertGreaterEqual(self.volumes["notes"], 120 * 8 * 2)

    def test_notes_des_deux_sequences_pour_tous(self):
        manquantes = self.db.execute(
            "SELECT COUNT(*) FROM eleves e CROSS JOIN matieres m CROSS JOIN (SELECT 1 AS s UNION SELECT 2) q "
            "LEFT JOIN notes n ON n.eleve_id = e.id AND n.matiere_id = m.id AND n.sequence = q.s "
            "WHERE n.id IS NULL").fetchone()[0]
        self.assertEqual(manquantes, 0)

    def test_note_en_double_refusee(self):
        eleve_id, matiere_id = self.db.execute("SELECT eleve_id, matiere_id FROM notes LIMIT 1").fetchone()
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO notes (eleve_id, matiere_id, sequence, note, date_saisie) "
                            "VALUES (?, ?, 1, 10, '2026-10-20')", (eleve_id, matiere_id))

    def test_note_hors_bornes_refusee(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO notes (eleve_id, matiere_id, sequence, note, date_saisie) "
                            "VALUES (1, 1, 4, 21, '2026-10-20')")

    def test_sequence_hors_bornes_refusee(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO notes (eleve_id, matiere_id, sequence, note, date_saisie) "
                            "VALUES (1, 1, 7, 12, '2026-10-20')")

    def test_matricule_unique(self):
        matricule = self.db.execute("SELECT matricule FROM eleves LIMIT 1").fetchone()[0]
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO eleves (matricule, nom, prenom, classe_id, date_naissance, "
                            "code_empreinte) VALUES (?, 'X', 'Y', 1, '2010-01-01', 'h')", (matricule,))

    def test_cle_etrangere_verifiee(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO eleves (matricule, nom, prenom, classe_id, date_naissance, "
                            "code_empreinte) VALUES ('LT99-F9-0001', 'X', 'Y', 999, '2010-01-01', 'h')")

    def test_codes_jamais_en_clair(self):
        empreinte = self.db.execute("SELECT code_empreinte FROM eleves LIMIT 1").fetchone()[0]
        self.assertTrue(empreinte.startswith(("scrypt:", "pbkdf2:")))


if __name__ == "__main__":
    unittest.main()
