# Spec — Étape 11 : finitions et préparation du rendu

- Date : 2026-10-20
- Exigences couvertes : `G-TECH-3` (HTML valide, accessibilité), `G-TECH-4` (confort sur téléphone),
  `G-TECH-8` (`debug=False`), `G-LIV-2` (README, requirements, base remplie, export), `G-LIV-3` (captures),
  checklist de la section 16 du cahier des charges

## Attendus

1. **Validation HTML** : toutes les pages principales passent le validateur du W3C (Nu Html Checker)
   sans erreur.
2. **Accessibilité** : aucune violation « grave » ou « critique » relevée par axe-core sur les pages
   principales (contrastes, libellés, noms des boutons, structure des titres).
3. **Téléphone** : aucune page ne déborde horizontalement à 360 px de large.
4. **README** du projet qui suffit à installer, lancer et tester : installation, lancement, comptes de test,
   données de test, export, tests automatiques, structure des fichiers, tableau des routes.
5. **Base livrée** : `projet.db` régénérée par `donnees_test.py`, `export_projet.sql` à jour,
   `debug=False`, aucun `venv` versionné.
6. **Captures** d'écran des pages principales dans `captures/ordinateur` et `captures/telephone`.
7. **Documentation** : matrice de suivi du cahier des charges mise à jour.

## Critères d'acceptation

- [ ] Rapport du validateur : 0 erreur sur chaque page principale.
- [ ] Rapport axe : 0 violation grave ou critique.
- [ ] Toute la suite de tests passe.
- [ ] En suivant uniquement le README dans un dossier neuf, le site démarre.
