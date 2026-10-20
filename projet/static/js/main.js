// main.js : comportements communs à toutes les pages
// (onglets de l'accueil, fermeture des messages, menu mobile, confirmations).

"use strict";

// Onglets accessibles : sans JavaScript, tous les panneaux restent visibles.
function initialiserOnglets(liste) {
    const onglets = Array.from(liste.querySelectorAll('[role="tab"]'));

    function activer(ongletChoisi, donnerFocus) {
        onglets.forEach(function (onglet) {
            const actif = onglet === ongletChoisi;
            onglet.setAttribute("aria-selected", actif ? "true" : "false");
            onglet.tabIndex = actif ? 0 : -1;
            document.getElementById(onglet.getAttribute("aria-controls")).hidden = !actif;
        });
        if (donnerFocus) {
            ongletChoisi.focus();
        }
    }

    onglets.forEach(function (onglet, indice) {
        onglet.addEventListener("click", function () {
            activer(onglet, false);
        });
        // Flèches gauche / droite pour passer d'un onglet à l'autre au clavier
        onglet.addEventListener("keydown", function (evenement) {
            if (evenement.key === "ArrowRight" || evenement.key === "ArrowLeft") {
                const pas = evenement.key === "ArrowRight" ? 1 : -1;
                activer(onglets[(indice + pas + onglets.length) % onglets.length], true);
            }
        });
    });

    liste.hidden = false;
    activer(onglets.find(function (o) { return o.getAttribute("aria-selected") === "true"; }) || onglets[0], false);
}

// Bouton « fermer » des messages flash
function initialiserMessages() {
    document.querySelectorAll("[data-fermer-message]").forEach(function (bouton) {
        bouton.addEventListener("click", function () {
            bouton.closest(".message").remove();
        });
    });
}

// Menu latéral de l'espace enseignant, replié sur téléphone
function initialiserMenu() {
    const bouton = document.querySelector("[data-bascule-menu]");
    if (!bouton) {
        return;
    }
    const menu = document.getElementById(bouton.getAttribute("aria-controls"));
    bouton.addEventListener("click", function () {
        const ouvert = menu.classList.toggle("ouverte");
        bouton.setAttribute("aria-expanded", ouvert ? "true" : "false");
    });
}

// Demande de confirmation avant une action sensible (formulaire data-confirmer="…")
function initialiserConfirmations() {
    document.querySelectorAll("form[data-confirmer]").forEach(function (formulaire) {
        formulaire.addEventListener("submit", function (evenement) {
            if (!window.confirm(formulaire.dataset.confirmer)) {
                evenement.preventDefault();
            }
        });
    });
}

// Envoi automatique d'un formulaire de filtres quand une liste change (data-envoi-auto)
function initialiserEnvoiAuto() {
    document.querySelectorAll("form[data-envoi-auto] select").forEach(function (liste) {
        liste.addEventListener("change", function () {
            liste.form.submit();
        });
    });
}

document.querySelectorAll("[data-onglets]").forEach(initialiserOnglets);
initialiserMessages();
initialiserMenu();
initialiserConfirmations();
initialiserEnvoiAuto();
