// import.js : zone de dépôt du fichier d'élèves (glisser-déposer) et affichage du nom choisi.

"use strict";

const zoneDepot = document.querySelector("[data-zone-depot]");
if (zoneDepot) {
    const champFichier = document.getElementById(zoneDepot.getAttribute("for"));
    const nomFichier = zoneDepot.querySelector("[data-nom-fichier]");

    function afficherNom() {
        const fichier = champFichier.files[0];
        nomFichier.hidden = !fichier;
        if (fichier) {
            nomFichier.textContent = "Fichier choisi : " + fichier.name + " (" + Math.ceil(fichier.size / 1024) + " Ko)";
            zoneDepot.classList.add("zone-depot-remplie");
        }
    }

    champFichier.addEventListener("change", afficherNom);

    ["dragenter", "dragover"].forEach(function (type) {
        zoneDepot.addEventListener(type, function (evenement) {
            evenement.preventDefault();
            zoneDepot.classList.add("zone-depot-active");
        });
    });
    ["dragleave", "drop"].forEach(function (type) {
        zoneDepot.addEventListener(type, function (evenement) {
            evenement.preventDefault();
            zoneDepot.classList.remove("zone-depot-active");
        });
    });
    zoneDepot.addEventListener("drop", function (evenement) {
        if (evenement.dataTransfer.files.length > 0) {
            champFichier.files = evenement.dataTransfer.files;
            afficherNom();
        }
    });
}
