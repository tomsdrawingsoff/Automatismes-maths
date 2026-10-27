# L’automatisme du jour — 3e & 1ère · Instagram + Facebook

Kit **gratuit**, sans service d’IA payant, pour générer chaque jour quatre images carrées (1080 × 1080), puis tenter leur publication sur un compte Instagram professionnel et une Page Facebook via l’API officielle Meta. Aucune publication n’est activée par défaut.

## Ce qui est personnalisé

- **Seulement deux niveaux : 3e et 1ère spécialité mathématiques**, en alternance un jour sur deux.
- **20 familles d’automatismes paramétriques** (10 pour chaque niveau) avec réponses calculées dans le code, sans IA générative.
- **Quatre diapositives :** 1. question ; 2. indice ; 3. correction ; **4. invitation à acheter les fiches** en cliquant sur le lien du profil.
- Visuel inspiré des **fiches de révision** : fond bleu/rose pastel, encadrés roses et bleus, pictogrammes mathématiques dans les coins, petite calculatrice, titre « L’automatisme du jour ».
- **Aucun QR code, aucun motif décoratif à trois traits.** Signature `@tomsdrawingsoff` partout.
- Légende du post avec appel à découvrir les fiches sur le profil.

La quatrième diapositive utilise le texte configuré dans `config.json` :

> Clique sur le lien sur mon profil →

**À vérifier :** le lien dans les profils Instagram/Facebook doit réellement mener vers les fiches adaptées (3e et 1ère). Le programme ne crée pas ton lien commercial ni ta boutique.

## Installation initiale (obligatoire)

1. **GitHub.** Crée un dépôt **public** sur https://github.com/new. Décompresse ce kit et ajoute à sa racine tous les fichiers et dossiers, **dont `.github/workflows/`**. Ne mets jamais de mots de passe ou de jetons d’accès dans le dépôt.
2. **Autorisation des workflows.** Ouvre `Settings → Actions → General → Workflow permissions` et accorde, si nécessaire, `Read and write permissions` au `GITHUB_TOKEN` ; sinon les enregistrements automatiques peuvent échouer.
3. **GitHub Pages.** Ouvre `Settings → Pages` et sélectionne la source `GitHub Actions`. Une fois le premier workflow lancé, les images seront accessibles publiquement sous `https://UTILISATEUR.github.io/DEPOT/posts/DATE/1.jpg`. Pour un domaine personnalisé, renseigne `site_base_url` dans `config.json`.
4. **Compte Meta.** Utilise un compte Instagram professionnel relié à une **Page Facebook** administrée par toi, et crée une application compatible dans https://developers.facebook.com/ pour obtenir les permissions de publication. Le jeton et les ID doivent correspondre à tes comptes. Selon le statut de l’application et les permissions, Meta peut refuser la publication tant que la configuration n’est pas validée.
5. **Secrets GitHub.** Sous `Settings → Secrets and variables → Actions`, crée :

   | Type | Nom | Contenu |
   | --- | --- | --- |
   | Secret | `FB_PAGE_ACCESS_TOKEN` | Jeton d’accès de Page autorisé à publier sur la Page et Instagram |
   | Secret | `FB_PAGE_ID` | ID de ta Page Facebook |
   | Secret | `IG_USER_ID` | ID du compte Instagram professionnel associé |
   | Variable | `PUBLISH_ENABLED` | **Laisser vide pendant les tests.** Passer à `true` pour publier |

6. **Teste d’abord sans publier.** Dans `Actions`, lance manuellement `01 - Préparer le carrousel et les images`. Vérifie le site Pages et les quatre images. Lance `02 - Publier sur Instagram et Facebook` avec `PUBLISH_ENABLED` absent : ce workflow ne publiera rien.
7. **Autorise la première publication.** Une fois les autorisations Meta vérifiées, crée la variable `PUBLISH_ENABLED=true` et lance `02 - Publier` manuellement. **Cette action publie réellement** sur les comptes associés. Vérifie l’apparence sur les deux plateformes.

## Horaires (heure de Paris)

- **11 h 25** : génération, sauvegarde et mise en ligne des quatre images.
- **12 h 07** : publication automatique Instagram + Facebook.

GitHub Actions permet le champ `timezone: Europe/Paris`, mais une exécution planifiée peut être **retardée ou omise** (aucune garantie de publication à la minute). Les workflows planifiés peuvent être désactivés sur les dépôts publics après une longue période sans activité. Les jetons Meta expirent ou peuvent être révoqués. Prévois donc une vérification périodique.

Instagram reçoit un **carrousel** ; Facebook reçoit une **publication multiphoto sur Page**, dont la présentation peut être différente.

## Personnaliser

Modifie `config.json` pour le pseudonyme, le texte d’appel à l’action ou l’URL GitHub Pages. Les couleurs, polices, dispositions et contenus automatiques se trouvent dans `src/generate.py`. Le programme limite volontairement `levels` à `3e` et `1ère`.

Pour modifier l’orientation pédagogique, les vingt modèles sont dans la fonction `exercise()` : ne publie pas une nouvelle famille sans en vérifier la correction.

## Tester sur ordinateur

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python src/generate.py --date 2026-10-27  # exemple 3e
python src/generate.py --date 2026-10-28  # exemple 1ère
python src/publish.py --date 2026-10-27   # inactif tant que PUBLISH_ENABLED != true
```

Tu trouveras les images sous `docs/posts/YYYY-MM-DD/1.jpg`, `2.jpg`, `3.jpg`, `4.jpg` et les textes dans `post.json`.

## Fiabilité et limites

- **Gratuité :** GitHub Actions avec des exécuteurs standards sur dépôt public + hébergement GitHub Pages ; aucune API d’IA payante. Sous réserve de l’évolution des offres et quotas des services.
- **Maths :** modèles calculés par Python et testés automatiquement ; fais une relecture des familles avant toute mise en production. Le niveau 1ère est orienté spécialité mathématiques.
- **Confidentialité :** n’enregistre pas de secrets dans des fichiers, commits publics, captures ou discussions.
- **Gestion des doublons :** `data/publish_state.json` enregistre les identifiants déjà publiés ; en cas de coupure après publication mais avant sauvegarde, un doublon est possible lors d’une relance. Contrôle les comptes avant de relancer.
- **Connexions Meta :** les trois informations de secrets et les permissions doivent être configurées par toi ; le kit n’est **pas relié à tes comptes**. Aucun réseau ne sera publié tant que l’activation n’est pas effectuée.
- **Sécurité par défaut :** `PUBLISH_ENABLED` absent ou différent de `true` bloque la publication réelle.

### Documentations officielles

- https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onschedule
- https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site
- https://developers.facebook.com/docs/instagram-platform/instagram-api-with-facebook-login/content-publishing
- https://developers.facebook.com/docs/graph-api/reference/page/photos
