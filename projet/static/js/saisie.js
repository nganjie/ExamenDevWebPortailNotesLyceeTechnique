// saisie.js : saisie des notes d'une classe.
// - refus immédiat d'une note hors de 0 à 20 (case en rouge + message) ;
// - moyenne de la classe, nombre de notes, note max. et min. recalculés en direct ;
// - bouton « Enregistrer » désactivé tant qu'une erreur subsiste.
// Le serveur revérifie chaque note : ce script n'est qu'un confort.

"use strict";

const MOTIF_NOTE = /^[0-9]{1,2}([.,][0-9]{1,2})?$/;

// Analyse une saisie : { vide }, { erreur: "..." } ou { valeur: 12.5 }
function analyserNote(texte) {
    const saisie = texte.trim();
    if (saisie === "") {
        return { vide: true };
    }
    if (!MOTIF_NOTE.test(saisie)) {
        return { erreur: "Saisissez un nombre, par exemple 12,5." };
    }
    const valeur = Number(saisie.replace(",", "."));
    if (valeur < 0 || valeur > 20) {
        return { erreur: "Note refusée : elle doit être comprise entre 0 et 20." };
    }
    return { valeur: valeur };
}

function formater(nombre) {
    return nombre.toFixed(2).replace(".", ",");
}

const formulaire = document.querySelector("[data-saisie]");
if (formulaire) {
    const cases = Array.from(formulaire.querySelectorAll("[data-case-note]"));
    const existantes = Array.from(formulaire.querySelectorAll("[data-note-existante]")).map(function (element) {
        return Number(element.dataset.noteExistante);
    });
    const zoneMoyenne = document.querySelector("[data-moyenne-direct]");
    const zoneSaisies = document.querySelector("[data-nombre-saisies]");
    const zoneErreurs = document.querySelector("[data-nombre-erreurs]");
    const cadreErreurs = document.querySelector("[data-zone-erreurs]");
    const zoneMax = document.querySelector("[data-note-max]");
    const zoneMin = document.querySelector("[data-note-min]");
    const bouton = document.querySelector("[data-bouton-enregistrer]");
    const messageBouton = document.querySelector("[data-message-bouton]");

    // Affiche ou efface l'erreur d'une case
    function marquer(caseNote, resultat) {
        const zone = document.getElementById(caseNote.id + "-erreur");
        const ligne = caseNote.closest("tr");
        if (resultat.erreur) {
            caseNote.setAttribute("aria-invalid", "true");
            zone.querySelector(".champ-erreur-texte").textContent = resultat.erreur;
            zone.hidden = false;
            ligne.classList.add("ligne-en-erreur");
        } else {
            caseNote.removeAttribute("aria-invalid");
            zone.hidden = true;
            ligne.classList.remove("ligne-en-erreur");
        }
    }

    // Recalcule la synthèse à partir des notes existantes et des cases valides
    function recalculer() {
        const valeurs = existantes.slice();
        let erreurs = 0;
        let nouvelles = 0;
        cases.forEach(function (caseNote) {
            const resultat = analyserNote(caseNote.value);
            if (resultat.erreur) {
                erreurs += 1;
            } else if (!resultat.vide) {
                valeurs.push(resultat.valeur);
                nouvelles += 1;
            }
        });

        const somme = valeurs.reduce(function (total, v) { return total + v; }, 0);
        zoneMoyenne.textContent = valeurs.length ? formater(somme / valeurs.length) : "—";
        zoneSaisies.textContent = valeurs.length;
        zoneErreurs.textContent = erreurs;
        cadreErreurs.classList.toggle("mini-indicateur-erreur", erreurs > 0);
        zoneMax.textContent = valeurs.length ? formater(Math.max.apply(null, valeurs)) : "—";
        zoneMin.textContent = valeurs.length ? formater(Math.min.apply(null, valeurs)) : "—";

        if (bouton) {
            bouton.disabled = erreurs > 0 || nouvelles === 0;
            if (erreurs > 0) {
                messageBouton.textContent = "Corrigez les " + erreurs + " note(s) en rouge pour enregistrer.";
            } else if (nouvelles === 0) {
                messageBouton.textContent = "Saisissez au moins une note.";
            } else {
                messageBouton.textContent = nouvelles + " nouvelle(s) note(s) prête(s) à être enregistrée(s).";
            }
        }
    }

    cases.forEach(function (caseNote) {
        caseNote.addEventListener("input", function () {
            marquer(caseNote, analyserNote(caseNote.value));
            recalculer();
        });
        // Entrée passe à la case suivante au lieu d'envoyer le formulaire
        caseNote.addEventListener("keydown", function (evenement) {
            if (evenement.key === "Enter") {
                evenement.preventDefault();
                const suivante = cases[cases.indexOf(caseNote) + 1];
                if (suivante) {
                    suivante.focus();
                }
            }
        });
    });

    formulaire.addEventListener("submit", function (evenement) {
        const invalides = cases.filter(function (caseNote) {
            const resultat = analyserNote(caseNote.value);
            marquer(caseNote, resultat);
            return Boolean(resultat.erreur);
        });
        if (invalides.length > 0) {
            evenement.preventDefault();
            invalides[0].focus();
        }
    });

    recalculer();
}
