// statistiques.js : graphiques de la page des statistiques,
// alimentés par un appel fetch sur /api/statistiques.

"use strict";

const BLEU = "#1D4ED8";
const AMBRE = "#B45309";

function graphiqueTranches(canevas, repartition) {
    return new Chart(canevas, {
        type: "bar",
        data: {
            labels: repartition.map(function (t) { return t.tranche; }),
            datasets: [{
                label: "Élèves",
                data: repartition.map(function (t) { return t.effectif; }),
                backgroundColor: ["#F87171", "#FDBA74", BLEU, BLEU, BLEU],
                borderRadius: 8,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: "#EEF2F7" } },
                x: { grid: { display: false } },
            },
        },
    });
}

function graphiqueClasses(canevas, classes) {
    return new Chart(canevas, {
        data: {
            labels: classes.map(function (c) { return c.nom; }),
            datasets: [
                { type: "bar", label: "Moyenne générale (sur 20)", data: classes.map(function (c) { return c.moyenne_generale; }),
                  backgroundColor: BLEU, borderRadius: 6, yAxisID: "moyenne" },
                { type: "line", label: "Taux de réussite (%)", data: classes.map(function (c) { return c.taux_reussite; }),
                  borderColor: AMBRE, backgroundColor: AMBRE, borderWidth: 3, pointRadius: 5, yAxisID: "taux" },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: "bottom", labels: { boxWidth: 14 } } },
            scales: {
                moyenne: { position: "left", min: 0, max: 20, grid: { color: "#EEF2F7" } },
                taux: { position: "right", min: 0, max: 100, grid: { display: false },
                        ticks: { callback: function (v) { return v + " %"; } } },
                x: { grid: { display: false } },
            },
        },
    });
}

const canevasClasses = document.getElementById("graphique-classes");
if (canevasClasses) {
    const message = document.querySelector("[data-message-graphique]");
    fetch(canevasClasses.dataset.source, { headers: { "Accept": "application/json" } })
        .then(function (reponse) {
            if (!reponse.ok) {
                throw new Error("Réponse " + reponse.status);
            }
            return reponse.json();
        })
        .then(function (stats) {
            graphiqueClasses(canevasClasses, stats.classes);
            graphiqueTranches(document.getElementById("graphique-tranches"), stats.repartition);
        })
        .catch(function () {
            message.textContent = "Les graphiques n'ont pas pu être chargés ; les tableaux restent à jour.";
            message.classList.add("texte-rouge");
        });
}
