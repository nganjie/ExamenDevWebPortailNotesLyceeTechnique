# Spec — Étape 04 : authentification et rôles

- Date : 2026-10-20
- Exigences couvertes : `P3-PUB-1`, `P3-ADM-1`, `P3-ACT-1..2`, `P3-RG-4`, `P3-EXT-5`, `G-TECH-7`, `G-TECH-8`

## Besoin

Trois profils se connectent : l'**élève / parent** (matricule + code d'accès), l'**enseignant**
(identifiant + mot de passe) et l'**administrateur** (enseignant avec le rôle `administrateur`).

## Règles

- Le serveur revérifie le format : matricule `LTAA-Fx-NNNN`, code de 6 chiffres, champs non vides.
- Vérification avec `check_password_hash` ; en cas d'échec, message unique « Matricule ou code incorrect. »
  (on ne dit pas lequel des deux est faux).
- **Limitation des essais** : après 5 échecs pour un même identifiant, nouvel essai refusé pendant 5 minutes.
- À la connexion, la session est vidée puis remplie (`eleve_id` ou `enseignant_id`) : un élève ne
  peut jamais porter l'identité d'un autre ; l'identifiant vient **toujours de la session**, jamais de l'URL.
- Décorateurs : `eleve_requis`, `connexion_requise` (enseignant ou administrateur, exercice 29 du polycopié),
  `admin_requis` (rôle relu dans la base à chaque requête). Accès refusé :
  sans connexion → retour à l'accueil avec message ; mauvais rôle → page 403.
- **Déconnexion** en `POST` (`/deconnexion`), session vidée.
- Mises en page : `layout_eleve.html` (bandeau avec l'identité de l'élève) et `layout_enseignant.html`
  (menu latéral sombre « Pédagogie / Administration », replié derrière un bouton sur téléphone).
- Pages d'arrivée : `/eleve` (espace élève, complété à l'étape 05) et `/enseignant` (tableau de bord :
  mes matières, mes classes, évaluations à saisir).

## Routes

| Adresse | Méthode | Rôle | Accès |
|---|---|---|---|
| `/connexion/eleve` | POST | connecter un élève | public |
| `/connexion/enseignant` | POST | connecter un enseignant | public |
| `/deconnexion` | POST | fermer la session | connecté |
| `/eleve` | GET | espace élève | élève |
| `/enseignant` | GET | tableau de bord | enseignant |

## Critères d'acceptation

- [ ] Bons identifiants → redirection vers l'espace ; mauvais → message d'erreur, champ matricule conservé.
- [ ] `/enseignant` sans connexion → redirection vers l'accueil ; un élève connecté → 403.
- [ ] 6ᵉ essai raté de suite → « Trop de tentatives ».
- [ ] Après déconnexion, `/eleve` n'est plus accessible.
