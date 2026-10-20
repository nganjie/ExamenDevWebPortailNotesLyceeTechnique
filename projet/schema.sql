-- schema.sql : création des tables du portail de notes du lycée technique
-- Les tables sont supprimées dans l'ordre inverse de leurs dépendances, puis recréées.

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS corrections;
DROP TABLE IF EXISTS notes;
DROP TABLE IF EXISTS evaluations;
DROP TABLE IF EXISTS eleves;
DROP TABLE IF EXISTS matieres;
DROP TABLE IF EXISTS classes;
DROP TABLE IF EXISTS enseignants;

-- Comptes du personnel : un enseignant peut aussi être administrateur
CREATE TABLE enseignants (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nom         TEXT    NOT NULL,
    login       TEXT    NOT NULL UNIQUE,
    empreinte   TEXT    NOT NULL,                      -- generate_password_hash
    role        TEXT    NOT NULL DEFAULT 'enseignant'
                CHECK (role IN ('enseignant', 'administrateur'))
);

-- Classes : « 2e année F3 », filière F1 à F4, effectif maximal
CREATE TABLE classes (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    nom                     TEXT    NOT NULL UNIQUE,
    niveau                  INTEGER NOT NULL CHECK (niveau BETWEEN 1 AND 4),
    filiere                 TEXT    NOT NULL,
    effectif_max            INTEGER NOT NULL CHECK (effectif_max BETWEEN 1 AND 60),
    professeur_principal_id INTEGER REFERENCES enseignants (id) ON DELETE SET NULL
);

-- Matières communes à toutes les classes, chacune confiée à un enseignant
CREATE TABLE matieres (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nom           TEXT    NOT NULL UNIQUE,
    coefficient   INTEGER NOT NULL CHECK (coefficient BETWEEN 1 AND 10),
    enseignant_id INTEGER NOT NULL REFERENCES enseignants (id)
);

-- Élèves : le code d'accès n'est jamais stocké en clair
CREATE TABLE eleves (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    matricule      TEXT    NOT NULL UNIQUE,
    nom            TEXT    NOT NULL,
    prenom         TEXT    NOT NULL,
    classe_id      INTEGER NOT NULL REFERENCES classes (id),
    date_naissance TEXT    NOT NULL,                  -- AAAA-MM-JJ
    code_empreinte TEXT    NOT NULL,                  -- generate_password_hash
    code_remis     INTEGER NOT NULL DEFAULT 0 CHECK (code_remis IN (0, 1))
);

-- Évaluations : une seule par classe, matière et séquence (elle donne la note de séquence)
CREATE TABLE evaluations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    classe_id       INTEGER NOT NULL REFERENCES classes (id) ON DELETE CASCADE,
    matiere_id      INTEGER NOT NULL REFERENCES matieres (id),
    sequence        INTEGER NOT NULL CHECK (sequence BETWEEN 1 AND 6),
    intitule        TEXT    NOT NULL,
    date_evaluation TEXT    NOT NULL,                 -- AAAA-MM-JJ
    statut          TEXT    NOT NULL DEFAULT 'ouverte' CHECK (statut IN ('ouverte', 'cloturee')),
    UNIQUE (classe_id, matiere_id, sequence)
);

-- Notes : une seule note par élève, matière et séquence
CREATE TABLE notes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    eleve_id    INTEGER NOT NULL REFERENCES eleves (id) ON DELETE CASCADE,
    matiere_id  INTEGER NOT NULL REFERENCES matieres (id),
    sequence    INTEGER NOT NULL CHECK (sequence BETWEEN 1 AND 6),
    note        REAL    NOT NULL CHECK (note BETWEEN 0 AND 20),
    date_saisie TEXT    NOT NULL,
    UNIQUE (eleve_id, matiere_id, sequence)
);

-- Historique des corrections de notes (qui, quand, pourquoi)
CREATE TABLE corrections (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id         INTEGER NOT NULL REFERENCES notes (id) ON DELETE CASCADE,
    ancienne_note   REAL    NOT NULL,
    nouvelle_note   REAL    NOT NULL CHECK (nouvelle_note BETWEEN 0 AND 20),
    motif           TEXT    NOT NULL,
    enseignant_id   INTEGER NOT NULL REFERENCES enseignants (id),
    date_correction TEXT    NOT NULL
);

CREATE INDEX idx_eleves_classe ON eleves (classe_id);
CREATE INDEX idx_notes_eleve ON notes (eleve_id);
CREATE INDEX idx_notes_matiere_sequence ON notes (matiere_id, sequence);
