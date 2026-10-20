# Spec — Étape 02 : charte graphique, icônes, gabarits et accueil

- Date : 2026-10-20
- Exigences couvertes : `G-TECH-2` (base.html, flash, 404), `G-TECH-3` (HTML sémantique, labels),
  `G-TECH-4` (CSS séparé, mobile d'abord, 2 points de rupture), `G-TECH-5` (vérification JS des formulaires)
- Maquette : écran 1 (accueil et connexion)

## Besoin

Mettre en place l'identité visuelle validée dans les maquettes et les briques réutilisées par toutes les
pages : feuille de style, polices, icônes, gabarits, vérification des formulaires en JavaScript.

## Règles

- **Charte** (reprise de `docs/designs/2026-10-20_maquettes-application.md`) : bleu `#1D4ED8`, ambre
  `#B45309`, erreur `#B91C1C`, succès `#047857`, fond `#F5F7FB`, Manrope (titres) et Inter (texte),
  copiées dans `static/fonts/` (licence OFL) — aucune ressource externe.
- **Icônes** : un fichier `static/images/icones.svg` de symboles (`<symbol id="…">`) appelés par
  `<use>` à travers la macro `icone(nom)` ; elles sont décoratives (`aria-hidden="true"`), les boutons
  qui n'ont qu'une icône portent un `aria-label`.
- **CSS** mobile d'abord, points de rupture **600 px** (tablette) et **1024 px** (ordinateur) ;
  zones cliquables d'au moins 44 px ; contour de focus visible ; `prefers-reduced-motion` respecté.
- **Gabarits** : `base.html` (structure, messages flash avec icône et bouton de fermeture), `macros.html`
  (icône, champ de formulaire avec erreur), `index.html` (accueil), `404.html`, `500.html`.
- **Accueil** : présentation, carte de connexion à deux onglets (Élève / parent, Enseignant), étapes d'aide.
  Sans JavaScript, les deux formulaires restent utilisables (onglets = amélioration progressive).
- **Vérification JS** générique (`validation.js`) pour tout formulaire `data-valider` : champs requis,
  motif (`pattern`), bornes numériques, messages en français sous le champ, envoi bloqué tant qu'il y a
  une erreur. Le serveur revérifie toujours.
- Les deux routes `POST /connexion/eleve` et `POST /connexion/enseignant` existent déjà mais ne
  connectent pas encore (étape 04).

## Critères d'acceptation

- [ ] L'accueil reprend la maquette 1 sur ordinateur et s'empile sur téléphone (360 px) sans défilement horizontal.
- [ ] Une adresse inconnue renvoie la page 404 personnalisée (code 404).
- [ ] Un matricule au mauvais format est signalé sous le champ avant l'envoi.
- [ ] Aucun appel réseau externe (polices, scripts) dans le code des pages.
