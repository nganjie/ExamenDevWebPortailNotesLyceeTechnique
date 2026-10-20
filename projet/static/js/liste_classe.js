// liste_classe.js : recherche instantanée dans la liste de classe et
// histogramme de la répartition des moyennes (fetch sur /api/classe/<id>/moyennes).

"use strict";

// Filtre les lignes du tableau pendant la frappe, sans recharger la page
document.querySelectorAll("[data-recherche]").forEach(function (champ) {
    const lignes = Array.from(document.querySelectorAll(champ.dataset.recherche + " tbody tr"));
    const messageVide = document.querySelector("[data-aucun-resultat]");
    champ.addEventListener("input", function () {
        const recherche = champ.value.trim().toLowerCase();
        let visibles = 0;
        lignes.forEach(function (ligne) {
            const correspond = ligne.dataset.texte.indexOf(recherche) !== -1;
            ligne.hidden = !correspond;
            if (correspond) {
                visibles += 1;
            }
        });
        if (messageVide) {
            messageVide.hidden = visibles > 0;
        }
    });
});

const canevasRepartition = document.getElementById("graphique-repartition");
if (canevasRepartition) {
    const message = document.querySelector("[data-message-graphique]");
    fetch(canevasRepartition.dataset.source, { headers: { "Accept": "application/json" } })
        .then(function (reponse) {
            if (!reponse.ok) {
                throw new Error("Réponse " + reponse.status);
            }
            return reponse.json();
        })
        .then(function (donnees) {
            new Chart(canevasRepartition, {
                type: "bar",
                data: {
                    labels: donnees.repartition.map(function (t) { return t.tranche; }),
                    datasets: [{
                        label: "Élèves",
                        data: donnees.repartition.map(function (t) { return t.effectif; }),
                        backgroundColor: ["#F87171", "#FDBA74", "#1D4ED8", "#1D4ED8", "#1D4ED8"],
                        borderRadius: 6,
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
        })
        .catch(function () {
            message.textContent = "La répartition n'a pas pu être chargée.";
            message.classList.add("texte-rouge");
        });
}
