// validation.js : vérification des formulaires avant l'envoi.
// S'applique à tout formulaire <form data-valider novalidate>.
// Le serveur revérifie toujours : ce contrôle n'est qu'un confort pour l'utilisateur.

"use strict";

// Renvoie le message d'erreur d'un champ, ou une chaîne vide s'il est correct
function messageErreur(champ) {
    const valeur = champ.value.trim();
    const libelle = champ.labels && champ.labels[0] ? champ.labels[0].textContent.replace("*", "").trim() : "Ce champ";

    if (champ.required && valeur === "") {
        return champ.dataset.messageRequis || libelle + " est obligatoire.";
    }
    if (valeur === "") {
        return "";
    }
    if (champ.pattern && !new RegExp("^(?:" + champ.pattern + ")$").test(valeur)) {
        return champ.dataset.messageMotif || "Format incorrect.";
    }
    if (champ.type === "number" || champ.dataset.nombre !== undefined) {
        const nombre = Number(valeur.replace(",", "."));
        if (Number.isNaN(nombre)) {
            return "Saisissez un nombre.";
        }
        if (champ.min !== "" && nombre < Number(champ.min)) {
            return champ.dataset.messageBornes || "La valeur doit être au moins " + champ.min + ".";
        }
        if (champ.max !== "" && nombre > Number(champ.max)) {
            return champ.dataset.messageBornes || "La valeur doit être au plus " + champ.max + ".";
        }
    }
    if (champ.type === "date" && champ.dataset.dateFuture !== undefined) {
        const aujourdhui = new Date().toISOString().slice(0, 10);
        if (valeur < aujourdhui) {
            return "La date doit être aujourd'hui ou plus tard.";
        }
    }
    return "";
}

// Affiche (ou efface) le message sous le champ et met à jour aria-invalid
function afficherErreur(champ, message) {
    let zone = document.getElementById(champ.id + "-erreur");
    if (!zone) {
        zone = document.createElement("span");
        zone.id = champ.id + "-erreur";
        zone.className = "champ-erreur";
        zone.appendChild(document.createElement("span")).className = "champ-erreur-texte";
        champ.insertAdjacentElement("afterend", zone);
        const decrit = champ.getAttribute("aria-describedby");
        champ.setAttribute("aria-describedby", decrit ? decrit + " " + zone.id : zone.id);
    }
    const texte = zone.querySelector(".champ-erreur-texte") || zone;
    texte.textContent = message;
    zone.hidden = message === "";
    if (message) {
        champ.setAttribute("aria-invalid", "true");
    } else {
        champ.removeAttribute("aria-invalid");
    }
}

function verifierChamp(champ) {
    const message = messageErreur(champ);
    afficherErreur(champ, message);
    return message === "";
}

document.querySelectorAll("form[data-valider]").forEach(function (formulaire) {
    const champs = Array.from(formulaire.querySelectorAll("input:not([type=hidden]):not([type=file]), select, textarea"));

    champs.forEach(function (champ) {
        champ.addEventListener("blur", function () {
            if (champ.value.trim() !== "") {
                verifierChamp(champ);
            }
        });
        champ.addEventListener("input", function () {
            if (champ.getAttribute("aria-invalid") === "true") {
                verifierChamp(champ);
            }
        });
    });

    formulaire.addEventListener("submit", function (evenement) {
        const invalides = champs.filter(function (champ) {
            return !champ.disabled && !verifierChamp(champ);
        });
        if (invalides.length > 0) {
            evenement.preventDefault();
            invalides[0].focus();
        }
    });
});
