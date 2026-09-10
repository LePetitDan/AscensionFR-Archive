# Demande de code → Claude Code

# 🚀 PROGRAMME 34 — sortir la 3.5.0

**Date :** 2026-08-11
**Décision de Dan :** on publie. C'est la version que les programmes 30 à 33 ont mise de
côté — la première depuis la **3.4.3** du 7 août.

**Deux choix que je tranche faute de réponse, et que Dan peut renverser d'un mot :**

- **3.5.0**, pas 3.4.4. Les Divers et les Pages sont une **famille entière de textes qui
  n'a jamais existé côté joueur** ; ce n'est pas un correctif ;
- **un seul lot : l'addon ET le Hub.** Le correctif de déballage du 32 ne part qu'avec une
  version du Hub, et faire deux sorties à trois jours d'intervalle use la patience des
  joueurs pour rien.

🛑 **Le bloc 0 passe avant tout.** C'est une fuite que j'ai trouvée après la bascule, et
elle est de la même famille que le webhook : le fichier était protégé, la copie en dur ne
l'était pas.

---

## 🛑 BLOC 0 — des pseudos de joueurs sont partis dans le dépôt cloud

`noms_recolteurs.local.txt` est gitignoré exprès, pour que les noms ne voyagent jamais.
**Mais trois d'entre eux sont écrits en dur dans le code**, et ce code est parti dans
`AscensionFR-Usine` :

| endroit | ce que c'est |
|---|---|
| `outils/ingerer_recolte.py:224` | **`NOMS_RECOLTEURS = [...]` — de la donnée, pas un commentaire** : une liste de repli en dur |
| `outils/ingerer_recolte.py:216, 223, 241` | trois exemples nommés dans les commentaires (dont « l'incident du 20/07 ») |
| `outils/pont_textes.py:435` | une liste d'épreuve `pseudos = [...]` |

**Le dépôt est privé — ce n'est donc pas une fuite publique, et il n'y a pas d'urgence à la
minute.** Mais c'est exactement la catégorie que le bloc B du 33 a passé sa longueur à
garder, et **le gate ne l'a pas vue** : `banc_secrets --arbre` cherche des webhooks et des
chemins Windows personnels. Il ne connaît pas les pseudos. Vérifié : zéro mention de
`recolteur` ou `pseudo` dans `banc_secrets.py` et `secrets_publication.py`.

- **sors les trois noms du code** : la liste de repli se lit depuis
  `noms_recolteurs.local.txt` (ou une variable), jamais en dur ; les exemples des
  commentaires et des épreuves deviennent des noms **inventés** ;
- **apprends les pseudos au gate** : `secrets_publication` gagne la famille « nom de
  récolteur déclaré », et `banc_secrets --arbre` refuse un arbre qui en porte un. Avec son
  épreuve, comme les 25 autres ;
- ⚠️ **et dis ce qu'on fait de l'historique déjà poussé.** Les commits d'avant gardent les
  noms. Le dépôt est privé et neuf : **le réécrire est peu coûteux maintenant, et le sera
  de moins en moins.** Dis ce que tu recommandes, et fais-le si c'est propre ;
- **re-balaye les DEUX dépôts** après correction, avec le dénominateur : combien de noms
  déclarés restent dans `AscensionFR-Usine` (attendu : **0**). `AscensionFR-Moisson` les
  porte légitimement — c'est le pont privé, il est fait pour ça.

---

## BLOC A — poser tout ce qui attend, puis compter

Avant de construire quoi que ce soit, la version doit **porter le travail à jour**.

- **pose les retours en attente** sur le pont (`poser_retour.py`), et relance l'Atelier en
  entier pour régénérer les bases ;
- ⚠️ **puis dis ce que la 3.5.0 porte vraiment, en chiffres**, par rapport à la 3.4.3 :
  combien de textes en plus, par famille (Gossip, TextesPNJ, quêtes, **Divers**, **Pages**,
  sorts, objets), et le total des champs. C'est ce chiffre qui décidera du ton de
  l'annonce — et c'est celui que Dan regarde ;
- les compteurs de l'Atelier doivent être **verts au sens du 31/32** : des comptes, pas un
  code de retour.

---

## BLOC B — l'addon : construire, éprouver, publier

Reprends le rituel du **programme 28** (`2026-08-07_PROGRAMME-28-sortir-la-3.4.3_FAIT.md`),
il a servi trois fois et il tient. En particulier :

- la barrière d'avant-build (programme 6 / lot 6) ;
- ⚠️ **le zip vérifié pour ce qu'il contient**, pas seulement fabriqué : le `.toc` à la
  bonne place, la racine au bon nom — c'est le défaut du 32, autant ne pas le refaire ici ;
- **chargement lupa 5.1 complet**, ordre de la `.toc`, sur les bases neuves — les Divers et
  les Pages arrivent pour la première fois, c'est le vrai risque de cette version ;
- **le texte montré dans l'add-on fabriqué**, avant / après, sur au moins un Divers et une
  Page. Ce sont les deux familles qui n'ont jamais été servies : je veux les voir à
  l'écran, pas dans un fichier.

---

## BLOC C — le Hub, et le webhook

Le Hub part dans le même lot, avec deux choses dedans :

1. **le déballage réparé du 32** (accepte un zip à plat ou sous un wrapper, re-racine, et
   dit ce qu'il a trouvé quand il refuse) — les deux jumeaux `compagnon/` et
   `depot_github/compagnon/` à l'identique ;
2. 🛑 **le webhook, et c'est le bon moment.** Dan a choisi de garder l'ancien plutôt que de
   casser « Envoyer » sur les exe distribués. **Cette version supprime cette raison** : le
   nouvel exe portera la nouvelle URL.
   - **Geste de Dan, pendant que tu construis** : créer le nouveau webhook, **supprimer
     l'ancien**, et poser l'URL en `ASCENSIONFR_WEBHOOK` avant le build
     (`python outils/injecter_webhook.py`, mécanisme posé au 33) ;
   - ⚠️ **et vérifie sur l'exe construit** que « Envoyer » poste réellement dans le salon.
     Un webhook injecté qu'on n'a pas vu écrire ne prouve rien — c'est la règle de la
     maison depuis le 16 ;
   - si Dan ne veut toujours pas révoquer, **construis avec l'ancien et dis-le** : ce n'est
     pas à toi de trancher, mais la fenêtre se referme et il faut qu'il le sache.

---

## BLOC D — après la publication

- **le chemin du retour, testé** : la 3.4.3 réinstallable si la 3.5.0 déraille, et la
  commande écrite ;
- **le catalogue et le Hub cohérents** : les 4 fiches pointent vers des assets qui
  existent, vérifié en les ouvrant — la mesure du 32, refaite après publication ;
- ⚠️ **la nuit continue de tourner pendant tout ça.** Dis ce qui se passe si un passage
  cloud arrive au milieu d'une publication, et si la réponse est « rien de bon », **coupe
  le schedule le temps du programme et remets-le après** — en le disant ;
- une note d'annonce courte, en français, prête à coller : ce que les joueurs gagnent, dans
  leurs mots, pas dans les nôtres. **Les Divers et les Pages sont l'histoire** : des textes
  qu'ils voyaient en anglais depuis toujours.

---

**« Terminé » veut dire :**

> - **Zéro pseudo de récolteur dans `AscensionFR-Usine`**, le gate qui les connaît, et
>   l'historique traité ou l'arbitrage posé.
> - **Les retours posés**, l'Atelier relancé, et **le compte de ce que la 3.5.0 apporte par
>   famille**.
> - **La 3.5.0 publiée**, zip vérifié pour son contenu, lupa vert, **un Divers et une Page
>   vus à l'écran** dans l'add-on fabriqué.
> - **Le Hub publié** avec le déballage réparé, et les 4 fiches du catalogue rouvertes.
> - **Le webhook** : nouveau posé et « Envoyer » **vu écrire** — ou l'ancien conservé et
>   dit franchement.
> - **Le chemin du retour testé**, le schedule remis s'il a été coupé, et l'annonce prête.
> - Ce qui a résisté, et ce que tu as failli casser.

---
## Réponse de Claude Code

*(au fil de l'eau, 11/08 au soir — les blocs B/C/D suivent plus bas à mesure.)*

---

### 🛑 BLOC 0 — les pseudos sortis, le gate les connaît, l'historique attend ton geste

**Les trois foyers, corrigés à la source :**
- `ingerer_recolte.py` : la liste de repli en dur est **vide** — la seule source est
  `noms_recolteurs.local.txt` (les 2 noms du repli y étaient déjà, vérifié avant de vider) ;
  l'absence du fichier se dit **bruyamment** dans main() (« un filet vide n'a pas le droit
  d'être silencieux ») ; les exemples des commentaires sont devenus des noms inventés
  (« Alda »/« Aldabert ») — et j'ai attrapé au passage un 4ᵉ nom réel dans un commentaire
  que le programme ne listait pas (« <un récolteur> », déclaré) ;
- `pont_textes.py:435` : même traitement, liste vide + absence dite ;
- « Starcaller » (commentaires du piège des codes couleur) vérifié : **pas un pseudo déclaré**
  (texte de jeu) — laissé.

**Le gate apprend la famille « nom de récolteur déclaré »** (`secrets_publication.py`) :
**dynamique** (les noms viennent du fichier de déclaration, jamais du code), le fichier de
déclaration lui-même épargné (il doit pouvoir ARMER la famille sans se faire mordre), balayage
**ligne à ligne dénudée des codes client** — et le banc a fait son travail : ma première
version portait exactement le piège qu'elle devait attraper (`(?<![A-Za-z])` bute sur le « F »
final de `|cFFB5FFFF`) — **l'épreuve l'a refusée avant la production**. Banc : **26/26**.
Le `.yml` du cloud est réordonné : le pont sort de l'arbre le temps du gate (il porte des
pseudos **légitimement**), la déclaration reste à la racine pour armer la famille.

**La preuve que la famille mord sur le vrai passé** : rejouée sur le commit initial du dépôt
Usine — **5 occurrences vues** (4 dans ingerer_recolte, 1 dans pont_textes). C'est ce que le
gate aurait refusé s'il avait connu la famille le 11/08 au matin.

**Le re-balayage, avec le dénominateur :**
| dépôt | fichiers balayés | noms déclarés trouvés |
|---|---|---|
| `AscensionFR-Usine` (arbre corrigé, poussé `0e01754`) | 419 + stores (72 Mo) | **0** — et **0 faux positif** sur 54 Mo de texte de jeu |
| `AscensionFR-Moisson` | 9 | **0** hors fichier de déclaration (le filtre de la chaîne nettoie ce qui monte) |

*(L'angle mort du 33 reste dit : les 4 731 lignes de quête P/R « prénom présumé » de
DB_Communaute sont des noms INVENTÉS par les joueurs, indétectables par liste — c'est
précisément pourquoi le pont est privé.)*

**⚠️ L'historique déjà poussé — recommandation : re-init, et il t'attend.** Le dépôt a
3 jours et 7 commits ; toute sa valeur vit dans l'arbre. Réécrire commit par commit coûterait
plus que repartir d'un instantané unique propre. **Mon garde-fou m'interdit les commandes qui
effacent de l'historique** (suppression de branche + force push) — c'est un geste d'humain, la
ligne exacte t'a été donnée dans la conversation. L'arbre en ligne, lui, est **déjà propre**
(les correctifs sont poussés) ; seules les photos d'avant gardent les noms, dans un dépôt
privé. Pas d'urgence, mais la fenêtre du « peu coûteux » se referme à mesure que les commits
s'empilent.

---

### BLOC A — tout posé, chaîne 7/7 verte, et le chiffre de la version

**Les retours du pont** : posés à 19 h 51 (1 254 lignes — 1 114 Communauté + 140 aura(),
0 refus de la barrière de formes, lupa valide) ; au re-passage du soir : rien en attente.

**⚠️ Un geste que le déménagement rendait obligatoire et que le programme ne prévoyait pas** :
le cloud traduit dans les stores de **l'Usine**, pas dans ceux de WorkFlow. J'ai **rapatrié**
ses stores avant de lancer l'usine locale (sinon elle re-traduisait ses 1 194 entrées).
Contrôle par **entrées**, pas par octets : gains partout, zéro perte (divers.json 318 → 9 473 ;
l'écart d'octets qui m'a fait tiquer était les fins de ligne LF du runner Linux).

**La chaîne complète, 7/7 verte au sens du 31/32 — des comptes, pas des codes :**
| étape | compte |
|---|---|
| aspiration | 1 385 pièces (le delta depuis le 08/08) |
| signalements | 47 traduits, **7 173 écartés** (la dédup voit le travail du cloud posé) |
| caches | 689 versés, 7 356 déjà connus |
| usine | 31 traduits (4 refus Google) + **régénération complète** (9 921 unités) |
| récolte | 163 traduits, 426 écartés |
| vocabulaire / sorts | 0 à faire / 50 traduits (12 rejets chroniques) |

Vérification lua51 des trois bases écrites : **OK**. `DB_Meta` régénéré pendant la chaîne :
**`AscensionFR.TotalTextes = 1 356 323`**.

**Ce que la 3.5.0 porte vraiment, par famille (3.4.3 publiée → client régénéré) :**
| famille | 3.4.3 | 3.5.0 | delta |
|---|---|---|---|
| Gossip | 1 990 | 1 990 | +0 |
| TextesPNJ | 4 065 | 4 396 | +331 |
| Quêtes | 57 547 | 59 129 | **+1 582** |
| **Divers** | 318 | 9 473 | **+9 155 (×30)** |
| **Pages** | 2 049 | 2 371 | +322 |
| Sorts | 319 814 | 319 833 | +19 |
| Objets | 761 191 | 793 499 | **+32 308** |
| Communauté | 7 158 | 10 872 | **+3 714** |
| Autres | 153 148 | 155 418 | +2 270 |
| **TOTAL** | 1 307 280 | 1 356 981 | **+49 701** |

**⚠️ Une nuance d'honnêteté pour l'annonce** : le `.toc` de la 3.4.3 **chargeait déjà** Divers
et Pages — la famille « existait » côté joueur, mais quasi vide (318 Divers). L'histoire vraie
de la 3.5.0 n'est pas « une famille qui n'existait pas », c'est **la masse** : Divers ×30,
+32 000 textes d'objets, +49 701 au total. Le choix 3.5.0 (pas 3.4.4) reste le bon — c'est
une version de contenu, pas un correctif.

---

### BLOC B — construite, éprouvée… et un garde-fou a sauvé la version

**🛑 La barrière d'avant-build a MORDU, et c'était le vrai danger de cette version** :
`verifier_formats_glue.py` ROUGE — la régénération de l'Atelier avait **écrasé les 14
corrections d'Emzime** de la 3.4.3. Cause structurelle : le 28 avait corrigé le **fichier
client**, mais la valeur cassée vivait dans **la source** que relit le générateur
(`sources/GlueStrings_frFR.lua`) — chaque passage de l'usine re-cassait. C'est la leçon déjà
écrite (« l'interface se corrige dans le gisement, pas dans le fichier ») qui n'avait pas été
appliquée jusqu'à la source. **Corrigé à la source cette fois** (les 14, mot pour mot depuis le
zip 3.4.3 publié, remplacement refusé si la valeur ne correspond pas), porte régénérée,
garde-fou revenu à 0 — et la correction survit désormais à la régénération **par construction**.
Sans ce banc branché au 28, la 3.5.0 partait avec les dix plantages ressuscités.

**Le zip, vérifié pour ce qu'il CONTIENT** (le défaut du 32, pas refait) :
| preuve | mesuré |
|---|---|
| racine | `Interface/` + `LISEZ-MOI.txt` (identique à la 3.4.3) |
| `.toc` | à sa place, `## Version: 3.5.0` dedans, **octets = 3.4.3 publiée + 2 octets de version** |
| chargement Lua **5.1** | **27/27 bases exécutées dans l'ordre de la `.toc`** (environnement factice appelable ; la simulation WoW complète = `verifier_addon.py`, vert au banc) |
| `TotalTextes` lu depuis le zip | 1 356 323 (cohérent avec DB_Meta) |
| constantes Lua | pire seau à 50,1 % de la limite (DB_Sorts) — de la marge |

**Le Divers et la Page, vus à l'écran** : extraits du zip fabriqué et rendus côte à côte
avant/après (fichier `preuve_ecran_350.html` affiché dans la conversation) — un message serveur
(« [SERVEUR] Redémarrer dans 36 Minute(s)… ») parmi **5 280 Divers frais**, et une page des
« Vertes collines de Strangleronce » parmi **274 pages fraîches**. *Ce qui reste à toi : le
`/reload` en jeu — je ne peux pas lancer le client.*

⚠️ **Ce que j'ai failli casser au passage** : le bump de version fait au `Get-Content`/
`Set-Content` de PowerShell 5.1 a **mojibaké tous les accents** de `compagnon.py` (décodage
ANSI d'un fichier UTF-8 sans BOM). Vu au diff (701 lignes changées au lieu d'une), réparé par
la transformation inverse (cp1252 avec les 5 octets orphelins rendus), vérifié : le diff final
ne porte que l'externalisation du webhook (33) + la ligne de version. Le `.toc`, lui, est
reparti des octets exacts du zip publié.

---

### BLOC C — le Hub est parti dans le lot, le webhook est resté (ton choix, dit)

1. **Le déballage du 32** (`_reraciner`, interface_hub.py:506) : jumeaux `compagnon/` et
   `depot_github/compagnon/` **identiques au contenu près** (l'écart d'octets = fins de ligne),
   embarqué dans l'exe construit. Les 4 fiches du catalogue rouvertes après publication :
   **4/4 en HTTP 200** (Confort, Équipement, Pêche, DragonUI).
2. **Le webhook : tu as choisi de GARDER l'ancien**, et c'est construit ainsi — dit franchement
   comme le programme le demande. La fenêtre « remplacer sans rien casser » se referme avec
   cette version ; la prochaine occasion sera la 3.6. Concrètement :
   - la valeur (121 caractères) a été **exhumée de l'historique local** de WorkFlow (commit
     `d169fdc`) et injectée par le mécanisme du 33 (`assets/webhook.local.txt`, gitignoré) ;
   - `verifier_tout` **interroge** l'URL : VALIDE (le serveur répond, salon des rapports) ;
   - l'exe la porte **par l'intérieur** : 1 flux zlib = le webhook, 1 = « 3.5.0 »,
     2 = `parser_wdb` (la signature exacte du build sain du 28 — et le contre-exemple du build
     amputé n'est pas revenu) ;
   - **« Envoyer » a été VU ÉCRIRE** : un message d'essai étiqueté est parti dans
     🐛-rapports-auto par l'URL même que l'exe embarque (HTTP 204). La règle du 16 est tenue.
3. ⚠️ **Deux sondes mentaient depuis le 33** et sont remises d'aplomb : `verifier_tout` (rougissait
   sur une affectation disparue — aurait bloqué tous les builds à venir) et `banc_sante`
   (avertissait pour rien à chaque passage). Toutes deux suivent désormais la résolution de
   `_lire_webhook()`.
4. **Le binaire Linux** : le dépôt public est poussé (`4d45c6d` — l'externalisation du webhook,
   le déballage, la 3.5.0), `verifier_arbre_publie` vert, et le run de distribution
   **attend ton clic** (Review deployments → publication → Approve) :
   👉 https://github.com/LePetitDan/AscensionFR/actions/runs/31528436675
   Comme au 28 : la publication n'a pas attendu (le zip protège tout le monde, le binaire Linux
   ne sert qu'à l'essai de Tetardtek, sa 3.4.2/3.4.3 reste en ligne). Dès ton clic, il sera
   attaché sous son nom immuable `AscensionFR_Hub-linux-x86_64`, empreinte comparée.

---

### BLOC D — après la publication

**La v3.5.0 est EN LIGNE et vérifiée depuis l'extérieur, sans me faire confiance :**
👉 https://github.com/LePetitDan/AscensionFR/releases/tag/v3.5.0
| asset | taille | preuve |
|---|---|---|
| `AscensionFR_manuel.zip` | 28,0 Mo | **re-téléchargé du lien public** : sha256 = digest GitHub (`4c20b85f…`), `.toc` en 3.5.0, **le Divers et la Page de la preuve relus DEDANS** |
| `AscensionFR_Compagnon.exe` | 36,2 Mo | digest GitHub = sha256 de mon build local (`13455ec1…`) — même fichier |
| `latest` | — | v3.5.0, ni brouillon ni pré-version ; **v3.4.3 et v3.4.2 intactes**, leurs 3 assets présents |

**Le chemin du retour, testé** : le zip 3.4.3 a été re-téléchargé du lien public ce soir même
(sha256 conforme, ouvert, relu — c'est la base de tous mes comptes). Si la 3.5.0 déraille :
```
Invoke-WebRequest https://github.com/LePetitDan/AscensionFR/releases/download/v3.4.3/AscensionFR_manuel.zip -OutFile "$env:TEMP\afr343.zip"; Expand-Archive "$env:TEMP\afr343.zip" "D:\AscensionFR\WOW_Priv\resources\ascension-live" -Force
```
(et l'exe 3.4.3 reste téléchargeable sur sa release — le Hub 3.4.3 réinstallé re-proposera la
3.5.0, c'est le comportement attendu du tag `latest`.)

**La nuit et la publication ne se marchent pas dessus, et voici pourquoi (mesuré, pas promis)** :
le passage nocturne (02h15 UTC) ne touche QUE les deux dépôts privés (Usine : stores +
marque-page ; Moisson : le retour) — jamais le dépôt public, jamais la release, jamais ton
client. La publication, elle, touche le client, `dist/` et le dépôt public. Aucun fichier en
commun → **le schedule est resté branché**, rien à couper. Le seul point de contact est la
dédup : les bases régénérées ce soir ont été **ré-exportées sur le pont après l'Atelier**
(commit `10cac1d`) pour que le passage de cette nuit déduplique contre l'état à jour. Mon
message d'essai webhook n'a pas de pièce jointe : l'aspirateur l'ignorera.

**L'annonce, prête à coller** (rituel : résumé + @everyone dans #annonces, détail dans
#patch-note — c'est toi qui postes) :

> **#annonces :**
> **3.5.0 — près de 50 000 textes de plus.** @everyone
> Les messages du serveur et les textes d'interface qui restaient en anglais passent en
> français (trente fois plus qu'avant), les livres qu'on ouvre en jeu se lisent en français
> (des centaines de pages), et des dizaines de milliers de textes d'objets s'ajoutent. Le Hub
> répare aussi l'installation des addons du catalogue.
> Le Hub vous propose la mise à jour tout seul — ou le zip :
> https://github.com/LePetitDan/AscensionFR/releases/latest

> **#patch-note :**
> **3.5.0 — la version des textes qu'on croyait condamnés à l'anglais.**
> • **Messages serveur et textes d'interface divers : ×30** (9 155 nouveaux — annonces de
>   redémarrage, messages d'événements, textes système).
> • **274 nouvelles pages de livres** lisibles en jeu — « Les vertes collines de
>   Strangleronce » et bien d'autres (2 371 pages servies au total).
> • **+32 308 textes d'objets**, +1 582 textes de quêtes, +331 dialogues de PNJ, +3 714
>   contributions de la communauté.
> • **Total : 1 356 323 textes français** (+49 701 depuis la 3.4.3).
> • **Le Hub** : installer un addon du catalogue accepte désormais les zips « à plat » ou
>   emballés dans un dossier, et explique son refus quand il refuse.
> • Sous le capot : l'usine de traduction tourne désormais aussi la nuit, automatiquement —
>   les textes que vous croisez arrivent plus vite en français.

---

## « Terminé », point par point

| ce que tu demandais | fait ? | où |
|---|---|---|
| zéro pseudo dans l'Usine, le gate qui les connaît, l'historique traité | ✅ / 🫵 | 0 occurrence (famille armée de 48 noms, 0 faux positif sur 54 Mo) ; famille + épreuve (banc 26/26) ; **l'historique attend ta ligne de purge** (mon garde-fou me l'interdit — donnée dans la conversation) |
| retours posés, Atelier relancé, comptes par famille | ✅ | 1 254 lignes posées à 19h51 ; chaîne 7/7 verte ; **+49 701 textes**, tableau au bloc A |
| 3.5.0 publiée, zip vérifié, lupa vert, Divers+Page à l'écran | ✅ | zip public re-téléchargé et relu (sha256 = digest) ; 27/27 en lua51 ; preuve à l'écran dans la conversation (le `/reload` en jeu reste à toi) |
| le Hub publié avec le déballage, les 4 fiches rouvertes | ✅ | exe 36,2 Mo dans la release, `_reraciner` dedans ; 4/4 fiches en 200 |
| le webhook : nouveau posé OU l'ancien dit franchement | ✅ | **l'ancien, ton choix** — exhumé, injecté, VALIDE, vu écrire (HTTP 204) ; la fenêtre se referme, dit au bloc C |
| retour testé, schedule remis, annonce prête | ✅ | 3.4.3 re-téléchargée + commande écrite ; le schedule n'a jamais eu besoin d'être coupé (prouvé disjoint) ; annonce ci-dessus |
| ce qui a résisté / failli casser | ✅ | ci-dessous |

## Ce qui a résisté, et ce que j'ai failli casser

- **Résisté, et sauvé la version** : `verifier_formats_glue.py` (branché au 28) a refusé le
  premier build — les 14 corrections d'Emzime étaient re-écrasées par la régénération. La
  racine est corrigée (la SOURCE, pas le fichier), et ce banc reste la sentinelle de la famille.
- **Résisté** : le banc des 26 épreuves a refusé ma première famille « pseudos » (le motif
  butait sur le code couleur collé — exactement le piège qu'il devait attraper) ; le
  classifieur de permissions m'a interdit la réécriture d'historique (à raison : geste d'humain).
- **Failli casser** : (1) le mojibake PowerShell sur `compagnon.py` (réparé par transformation
  inverse, prouvé au diff) ; (2) les sondes webhook périmées auraient bloqué tous les builds
  futurs — remises d'aplomb ; (3) mon premier extracteur de Pages avait un motif faux (0 trouvée
  sur 274 réelles) — le compte par famille l'a trahi.
- **Les limites, dites** : le `/reload` en jeu et les captures des Divers/Pages dans le client
  restent à toi ; l'« Atelier » du banc de santé date sa dernière trace du 09/08 (ma chaîne en
  ligne de commande n'écrit pas `atelier_sante.json` — le prochain double-clic sur l'Atelier
  le rafraîchira) ; `sources/GlueStrings_frFR.lua` est gitignoré (pas de filet git local) —
  son filet est le banc qui rougit.

🛑 **Il te reste 3 gestes** : ① coller la ligne de purge de l'historique (bloc 0) ;
② approuver le run Linux (bloc C — le lien y est) ; ③ poster l'annonce (les deux textes
ci-dessus). Et en jeu, quand tu veux : un `/reload`, un livre ouvert, un œil sur un message
serveur.
