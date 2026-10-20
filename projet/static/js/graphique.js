// graphique.js : graphique de l'évolution d'un élève (Chart.js),
// alimenté par un appel fetch sur /api/eleves/<id>/evolution.

"use strict";

const NOMBRE_SEQUENCES = 6;

function dessinerEvolution(canevas, donnees) {
    const etiquettes = [];
    const eleve = [];
    const classe = [];
    for (let sequence = 1; sequence <= NOMBRE_SEQUENCES; sequence += 1) {
        const ligne = donnees.evolution.find(function (l) { return l.sequence === sequence; });
        etiquettes.push("S" + sequence);
        eleve.push(ligne ? ligne.moyenne : null);
        classe.push(ligne ? ligne.moyenne_classe : null);
    }

    return new Chart(canevas, {
        type: "line",
        data: {
            labels: etiquettes,
            datasets: [
                { label: "Élève", data: eleve, borderColor: "#1D4ED8", backgroundColor: "#FFFFFF",
                  borderWidth: 3, pointRadius: 6, pointBorderWidth: 3, tension: 0.25 },
                { label: "Classe", data: classe, borderColor: "#94A3B8", backgroundColor: "#94A3B8",
                  borderWidth: 3, pointRadius: 4, tension: 0.25 },
                { label: "Seuil de réussite", data: etiquettes.map(function () { return 10; }),
                  borderColor: "#B45309", borderDash: [6, 5], borderWidth: 2, pointRadius: 0 },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            spanGaps: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (contexte) {
                            const valeur = contexte.parsed.y;
                            return contexte.dataset.label + " : " + valeur.toFixed(2).replace(".", ",");
                        },
                    },
                },
            },
            scales: {
                y: { min: 0, max: 20, ticks: { stepSize: 4 }, grid: { color: "#EEF2F7" } },
                x: { grid: { display: false } },
            },
        },
    });
}

const canevas = document.getElementById("graphique-evolution");
if (canevas) {
    const message = document.querySelector("[data-message-graphique]");
    fetch(canevas.dataset.source, { headers: { "Accept": "application/json" } })
        .then(function (reponse) {
            if (!reponse.ok) {
                throw new Error("Réponse " + reponse.status);
            }
            return reponse.json();
        })
        .then(function (donnees) {
            if (typeof Chart === "undefined") {
                throw new Error("Chart.js absent");
            }
            dessinerEvolution(canevas, donnees);
        })
        .catch(function () {
            message.textContent = "Le graphique n'a pas pu être chargé. L'historique ci-contre reste disponible.";
            message.classList.add("texte-rouge");
        });
}
