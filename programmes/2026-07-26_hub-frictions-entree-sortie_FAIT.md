# Demande de code → Claude Code

**Date :** 2026-07-26
**Sujet :** Hub — supprimer les 3 causes qui bloquent les joueurs à l'entrée, et celle
qui les bloque à la sortie

---

## D'où ça vient

Première veille Discord (1 202 messages du 18 au 26/07, `3-atelier/veille-discord/`).
Ce ne sont pas des suppositions : ce sont des joueurs comptés, un par un, sur 9 jours.
Dan a validé les quatre chantiers ci-dessous le 26/07.

---

## Objectif A — « J'ai installé, le jeu reste en anglais » (12 joueurs)

Douze joueurs distincts en neuf jours, et **toujours les trois mêmes causes** :

1. **Mauvais dossier d'installation** — le joueur descend jusqu'à `Interface\AddOns` au
   lieu de s'arrêter à `ascension-live`.
2. **La case « charger les addons non liés au launcher » n'est pas cochée** côté jeu
   (« Allow tier addons » dans la liste des addons).
3. **La case « Activer la traduction » est décochée** dans `/afr`.

**Ce qu'on veut :** le Hub ne dit plus « c'est bon » tant qu'il n'a pas vérifié ces trois
points. Pour chacun : **le réparer tout seul si c'est réparable**, sinon **dire au joueur
exactement quoi cliquer**, en une phrase, dans le Hub — pas dans un fichier d'aide.

- Cause 1 : c'est le Hub qui écrit, il sait où il installe. S'il détecte un chemin qui
  descend trop bas (ou un `Interface\AddOns\Interface\AddOns`), il corrige ou refuse
  d'installer là en expliquant pourquoi.
- Cause 3 : le réglage vit dans les `SavedVariables` d'AscensionFR (jeu fermé). Le Hub
  peut le lire, et proposer de le réactiver.
- Cause 2 : **je ne sais pas si c'est atteignable depuis le Hub** — à toi de regarder.
  Si oui, on la coche ; si non, on l'affiche comme la seule action manuelle restante,
  avec une capture ou un texte sans ambiguïté.

⚠️ **Ne devine pas à ma place** : si un des trois points n'est pas vérifiable de façon
fiable, dis-le dans ta réponse et affiche-le au joueur plutôt que de bricoler un test
approximatif. Un faux « tout est bon » coûte plus cher que pas de test du tout.

## Objectif B — Windows Defender bloque le Hub (5 joueurs)

Apparu avec la **2.2.1**. Un joueur n'a **jamais** réussi à lancer le Hub (« même si je
l'exécute il le supprime »). L'exe n'est pas signé : Defender le prend pour un trojan.

Dan s'occupe lui-même du signalement du faux positif à Microsoft. **Toi, tu prépares le
secours :** à chaque version, publier **aussi** une **archive .zip d'installation
manuelle** (l'addon seul, sans exe), et faire en sorte qu'elle soit visible sur la page de
téléchargement — pas cachée dans les fichiers de la release.

`outils/construire_zip_release.py` existe déjà : réutilise-le plutôt que d'en écrire un
autre. Le but est qu'un joueur bloqué par son antivirus ait **une solution à un clic**,
sans avoir à demander sur Discord.

## Objectif C — Désinstaller proprement (3 joueurs, dont un en colère aujourd'hui)

Le 26/07, un joueur a retiré le dossier du jeu **et** le contenu de `%appdata%` : son jeu
est **toujours en français** et il enchaîne les erreurs. Un autre : « ça le laisse actif ».
Aujourd'hui, **la seule sortie propre n'est écrite nulle part**.

**Ce qu'on veut :** un bouton **« Tout désinstaller »** dans le Hub qui retire vraiment
tout — les dossiers d'addon posés par le Hub, les `SavedVariables` d'AscensionFR, les voix
si elles sont installées (le dossier `Sound`) — en **listant ce qu'il va supprimer avant
de le faire**, et en disant à la fin « ton jeu est revenu en anglais ».

Si un élément ne peut pas être supprimé (jeu ouvert, fichier verrouillé), le dire
explicitement plutôt que d'échouer en silence.

## Objectif D — Le paquet DragonUI livré par le Hub est incomplet (2 joueurs)

Installé via le Hub, DragonUI affiche « le module des options n'est pas installé » : le
dossier `options` manque dans ce qu'on distribue. Un joueur s'en est sorti en allant le
chercher sur le dépôt d'origine (`https://github.com/NeticSoul/DragonUI`) — ce n'est pas à
lui de faire ça. **Compléter le paquet** et vérifier qu'une installation neuve via le Hub
donne bien les options accessibles en jeu.

## Tâche rapide — 125 rapports attendent

En vérifiant l'aspirateur hier, tu as téléchargé **125 fichiers** dans `WorkFlow/rapports/`
qui ne sont **pas encore ingérés**. Passe `ingerer_rapport.py` puis `ingerer_caches.py`
(ou l'Atelier) et dis-moi combien de textes nouveaux ça a apporté.

---

## « Terminé » veut dire

1. **A** — Sur une installation volontairement cassée (mauvais dossier, traduction
   désactivée), le Hub **détecte les trois points** et, pour chacun, soit répare, soit
   affiche l'action à faire. Aucun « tout est bon » affiché alors qu'un des trois est
   faux. Tu me dis lesquels sont réparables automatiquement et lesquels ne le sont pas.
2. **B** — La release contient un `.zip` d'installation manuelle **en plus** de l'exe, et
   la page de téléchargement le mentionne. Rien n'est publié : tu prépares, Dan donne le go.
3. **C** — Après « Tout désinstaller » sur une machine de test, le jeu redémarre **en
   anglais**, et il ne reste ni dossier d'addon, ni `SavedVariables` AscensionFR. La liste
   de ce qui va être supprimé s'affiche **avant** la suppression.
4. **D** — Installation neuve de DragonUI via le Hub : le message « module des options
   non installé » n'apparaît plus, les options s'ouvrent en jeu.
5. La barrière habituelle passe, et **rien n'est publié** (ni GitHub, ni Discord).

## Fichiers / dossiers concernés

Le Hub et son empaquetage, `outils/construire_zip_release.py`, `outils/ingerer_rapport.py`,
`outils/ingerer_caches.py`. Rien dans les traductions.

## Validation

**Autonome jusqu'au paquet.** Publication = feu vert explicite de Dan, comme d'habitude.
Si un des quatre objectifs demande une décision de sa part (ex. supprimer ou non le dossier
`Sound` par défaut), **arrête-toi sur ce point-là**, fais le reste, et écris la question
dans ta réponse — je la lui poserai en questionnaire.

---
## Réponse de Claude Code

**Fait le 26/07/2026. Rien n'est publié** — ni GitHub, ni Discord. Le paquet
attend ton go.

---

### D'abord, la tâche rapide : les rapports en attente

| | résultat |
|---|---|
| `ingerer_caches.py` | **61 fichiers** de caches lus → **567 textes de jeu inédits** versés à l'usine (créatures +178, objets +338, quêtes +19, textes PNJ +19, objets de monde +7, pages +6) |
| `ingerer_rapport.py` | **93 sorts** neufs corrigés et ajoutés à `DB_SortsCorrections.lua` (1 928 → 2 021 entrées), 0 échec de traduction |

`DB_SortsCorrections.lua` recompile en Lua : vérifié avec `lupa` avant de te le
dire. Prochaine étape quand tu veux : lancer l'usine pour traduire les 567
nouveautés.

---

### Objectif A — « j'ai installé, le jeu reste en anglais »

Le Hub a maintenant un lien **« Vérifier mon installation ↗ »** sur l'Accueil
et sur l'onglet Traduction. Il ouvre une fenêtre qui passe cinq points en
revue, répare d'un bouton ce qui est réparable, et se copie en un clic pour le
Discord.

**Ta question : lesquels sont réparables automatiquement ?**

| point | vérifiable ? | réparable ? |
|---|---|---|
| **1. Mauvais dossier** | **oui** | **oui** — corrigé tout seul |
| **2. Case « Allow Non-Launcher AddOns »** | **NON** | **NON** |
| 2 bis. AscensionFR coché dans la liste | oui | oui |
| **3. « Activer la traduction » dans /afr** | **oui** | **oui** |

**Cause 1 — réparée toute seule.** Le test historique était trop faible : il
suffisait qu'un dossier contienne un sous-dossier `Interface`. Sur une
installation **propre**, trois dossiers passaient ce test — la vraie racine,
mais aussi `Data\enUS` et `Sound`, qui contiennent chacun un « Interface ».
Et le piège se refermait : quand un joueur avait déjà mal extrait le zip à la
main dans `Interface\AddOns`, ce dossier-là passait le test **pour toujours**,
le Hub y installait, y relisait un vrai `.toc`, et affichait **« tu es à
jour »** pendant que le jeu ne chargeait rien. Ton diagnostic Ctrl+D sortait
entièrement vert. Désormais on exige `Interface` **et** `Data` (ou
`Ascension.exe` / `Wow.ini`) — trois marqueurs qui n'existent qu'à la racine.
Le Hub descend tout seul si tu lui donnes le dossier du launcher, **remonte**
tout seul si tu es descendu trop bas, refuse en expliquant sinon, repère les
restes imbriqués et propose de les retirer. Et il rattrape au démarrage les
mauvais chemins déjà écrits dans le `compagnon.json` des joueurs par les
versions précédentes — sans ça, durcir le bouton « Changer… » n'aurait protégé
que ceux qui recliquent dessus.

**Cause 2 — je ne peux pas, et je le dis.** Tu l'appelais « Allow tier addons »
sur le Discord ; son vrai nom est **« Allow Non-Launcher AddOns »** (VF :
« Autoriser les modules complémentaires sans lanceur »). C'est la CVar
`loadUnknownAddOns`, lue et écrite **uniquement en jeu**
(`Ascension_AddonPanel\AddonPanel.xml:189` et `:193`). J'ai cherché partout sur
le disque, la case étant COCHÉE : elle n'est ni dans `Config.wtf` (qui a
`checkAddonVersion` et `allowAddonMemoryUsage` — à ne pas confondre), ni dans
les `config-cache.wtf`, ni dans `Wow.ini`, ni dans les réglages du launcher.
**État ON, disque muet.** Le Hub ne peut donc ni la lire ni la cocher. Il
l'affiche en « à vérifier toi-même » avec l'endroit exact (bouton **AddOns** en
bas à gauche de l'écran des personnages → la case **juste au-dessus** de
« Load out of date AddOns ») et le témoin visuel : si la ligne AscensionFR
affiche **« Not a Launcher AddOn »**, c'est qu'elle est décochée.
Au passage : AscensionFR n'a pas de `.pub` et n'est pas dans les
`managed_roots` d'`Ascension.ok` — **cette case est obligatoire pour 100 % des
joueurs**, ce n'est pas un cas limite.

En revanche, l'autre moitié de ta phrase (« regarde qu'il soit bien coché »)
**est** lisible, dans `AddOns.txt`, par personnage. Le Hub la contrôle et la
répare. Sur ton installation, il a trouvé deux personnages avec l'addon
décoché : **<joueur>** et **Jhsgsgsg**.

**Cause 3 — réparée d'un bouton.** Le réglage est
`AscensionFRSaved.Options.desactive`. Attention, la clé est **à l'envers** de la
case, et elle n'existe **que** si le joueur a décoché : clé absente =
traduction active. Un Hub qui crierait au problème sur une clé absente
alarmerait tout le monde pour rien. Le Hub ne signale donc que le vrai cas, il
**date** ce qu'il affiche (« d'après ta session du 25/07 à 22:18 » — ce fichier
n'est écrit qu'à la déconnexion) et il refuse d'écrire tant que le jeu tourne,
sinon WoW effacerait la correction en se fermant. La réparation ne touche que
la ligne fautive : le reste (ta récolte, tes signalements) n'est pas relu ni
réécrit.

**Le point le plus important : plus aucun faux « tout est bon ».** Dès qu'un
point est en souci, le grand panneau « Tu es à jour », sa pastille verte **et**
la barre d'état basculent ensemble sur **« Installée, mais bloquée »** en
rouge. Un seul verdict à l'écran.

---

### Objectif B — l'antivirus qui supprime le Hub

Le zip existait déjà et était déjà joint à chaque release. Le vrai manque était
ailleurs : **il était invisible**. Le README et le guide d'installation
pointaient tous sur la *page* des releases, jamais sur le fichier. Ajouté
partout le lien permanent
`…/releases/latest/download/AscensionFR_manuel.zip` : en bouton d'en-tête du
README (« 📁 ZIP SANS PROGRAMME »), dans l'encart antivirus, dans la FAQ, en
tête du guide, et en **première ligne** du corps de release (le zip passe
devant l'exe).

J'ai aussi réparé sa fabrication, comme tu le demandais, dans
`construire_zip_release.py` plutôt qu'en écrivant un nouvel outil :

- la version n'est plus écrite en dur — elle est **lue dans le `.toc` vivant**
  (il fallait éditer le script à chaque sortie, et l'oublier ne se voyait pas) ;
- la liste des dossiers à emballer est explicite : elle était **recopiée du zip
  précédent**, donc un dossier nouveau n'y serait jamais entré. `LISEZ-MOI.txt`
  était d'ailleurs perdu comme ça — il est revenu ;
- le script rend un **code de sortie**, et `publier_github.py` l'honore ;
- **deux scripts écrivaient le même fichier** avec des contenus différents
  (`empaqueter.py` et celui-ci) : `publier_github` appelait `empaqueter`, qui
  écrasait l'autre juste avant l'envoi, garde-fous compris. Un seul builder
  désormais, qui réutilise les listes d'`empaqueter`.

Et une correction de fond, dans la même veine que l'affaire DB_Objets : chaque
`.lua` du zip est maintenant **compilé en Lua 5.1** avant publication, seaux
compris, et le zip est fabriqué **sous un nom provisoire** — l'officiel n'est
remplacé qu'une fois tous les contrôles passés. Avant, on écrivait d'abord et
on vérifiait ensuite : un zip mort avait déjà pris la place du bon.

Le corps de release corrige aussi une **consigne fausse** de la 3.3.0, qui
disait d'extraire le zip dans `Interface/AddOns` — c'est exactement ce qui
fabrique le dossier imbriqué de la cause 1.

Vérifié : `python outils/construire_zip_release.py` → 81 fichiers, 45,9 Mo,
garde-fous « TOUT PROPRE », code 0.

---

### Objectif C — « Tout désinstaller »

Le lien est sur l'onglet Traduction, discret et rouge : ce n'est pas une action
qu'on propose, c'est une action qu'on doit pouvoir trouver quand on la cherche.

**Le joueur en colère du 26/07 avait raison, et son geste était logique.** Il a
retiré le dossier d'addon et vidé `%appdata%` — or `%APPDATA%\AscensionFR` ne
contient **que** `compagnon.json`. Le français vient de **quatre dépôts
indépendants, tous dans le dossier du jeu** :

1. `Interface\AddOns\AscensionFR` (+ `AscensionFR_Repliques`) ;
2. **`Interface\PTRXML`** — HORS de `AddOns`, donc jamais supprimé par celui
   qui nettoie « le dossier de l'addon ». **C'est lui** qui laisse les écrans de
   connexion en français, et ses erreurs Lua une fois son compagnon parti ;
3. `Sound\` (ou `Sound_off\` si les voix ont été coupées) ;
4. **`Wow.ini`** (`Country=FR / Language=fr`) — posé en silence par le zip des
   voix. Ce n'était écrit nulle part.

La fenêtre liste **tout** avec les tailles et les chemins **avant** de
supprimer, avec des cases décochables : les addons d'autres auteurs (DragonUI,
G.B.G) et `Wow.ini` sont **décochés par défaut**. Elle refuse net si le jeu est
ouvert, et rend un rapport ligne à ligne de ce qui n'a pas pu partir, avec la
raison. À la fin : « **Ton jeu est revenu en anglais.** » — mais uniquement si
la traduction faisait vraiment partie de ce qui a été supprimé.

Pour les voix, j'ai mesuré le contenu réel du zip (14 442 entrées) : il ne pose
que six dossiers sous `Sound\`. On ne supprime que ceux-là, et `Sound\`
lui-même ne disparaît que s'il finit **vide** — un joueur qui aurait posé ses
propres fichiers sonores les garde. Vérifié par test.

---

### Objectif D — DragonUI

**Le « dossier options » manquant, c'est un addon entier :
`DragonUI_Options`.** DragonUI se livre en deux dossiers frères
(`## LoadOnDemand: 1`, `## Dependencies: DragonUI`). L'installeur cherchait
`DragonUI.toc`, se re-racinait dessus et copiait **ce seul dossier** — le
second partait avec le dossier temporaire. En jeu, `core.lua:95` imprime le
message que voient tes joueurs, et `gamemenu.lua:204` **masque** le bouton
DragonUI du menu Échap.

L'installeur pose maintenant **tous** les dossiers d'addon du zip (un dossier
qui porte son propre `.toc` ; on ne descend pas dedans, donc les bibliothèques
Ace ne comptent pas), garde-fou inchangé si le `.toc` attendu manque, et il dit
ce qu'il a posé : « DragonUI installé (avec DragonUI_Options) ». Le catalogue
déclare le dossier compagnon, donc la désinstallation le retire aussi. Et pour
les joueurs déjà servis par l'ancien Hub, la carte repasse sur « Mettre à
jour » avec la mention « module manquant : DragonUI_Options ».

**Vérifié sur le vrai zip.** Le `DragonUI.zip` téléchargé par ton Hub le 24/07
traînait encore dans `%TEMP%` (10 883 073 octets) : il contient bien
`DragonUI/DragonUI.toc` **et** `DragonUI_Options/DragonUI_Options.toc` en
frères. Passé dans le nouvel installeur, les deux dossiers arrivent — 84
fichiers côté options, `panel/` compris.

---

### Les cinq vérifications

1. **A — passe.** Sur une installation volontairement cassée (mauvais dossier,
   addon décoché, traduction désactivée, restes imbriqués), le Hub voit
   **3 soucis + 1 « à vérifier toi-même »**, ne rend jamais « tout va bien », et
   les trois réparations remettent le compteur à zéro. Le tableau plus haut dit
   lesquelles sont automatiques.
2. **B — prêt.** `AscensionFR_manuel.zip` est reconstruit à chaque version, et
   le lien direct est visible sur le README, la FAQ, le guide d'installation et
   la première ligne du corps de release. **Rien n'est publié.**
3. **C — passe.** Après « Tout désinstaller » sur un jeu d'essai : la
   traduction, `PTRXML`, les voix et les `SavedVariables` sont partis ; le
   `Ascension.exe`, le `Wow.ini` et un pack son personnel posé par le joueur
   sont intacts ; la liste s'affiche bien **avant**.
4. **D — passe.** Installation neuve depuis le zip réel de PentSec : les deux
   dossiers arrivent, `DragonUI_Options.toc` et `panel/` compris.
5. **Barrière — passe.** `pyflakes` muet sur tout ce qui a été touché,
   `verifier_decors.py` OK (35 décors, aucun nouveau), `verifier_hub.py` OK
   (**0 échec**), `DB_SortsCorrections.lua` compile en Lua.
   **Rien n'est publié.**

J'ai aussi étendu `outils/verifier_hub.py` : il monte un faux jeu jetable dans
`%TEMP%`, y reproduit les quatre pannes, et vérifie les 21 points ci-dessus.
Ça se relance en une commande, à chaque version.

---

### Ce que je n'ai pas pu vérifier de façon fiable

- **La case « Allow Non-Launcher AddOns » : rien, et c'est définitif.** Ce
  réglage n'existe dans aucun fichier lisible. Je n'ai pas cherché à bricoler un
  test approximatif — j'ai envisagé un indice indirect (« l'addon est coché mais
  sa sauvegarde n'existe pas »), et je l'ai écarté : il est structurellement
  faux au premier lancement, donc il aurait crié au loup chez tout nouveau
  joueur.
- **Je n'ai pas lancé le jeu.** Tout ce qui touche aux `SavedVariables` et à
  `AddOns.txt` est vérifié sur les fichiers réels et sur un faux jeu, mais le
  test « le joueur relance et c'est en français » n'a pas été fait en jeu.
- **`Sound\` sur une installation neuve.** Sur ta machine, ce dossier est
  démontrablement 100 % le nôtre (dates, comptage, racines identiques au zip).
  Je n'ai qu'une machine : je ne peux pas prouver qu'un client Ascension neuf
  n'y met rien. D'où la suppression ciblée plutôt qu'en bloc.
- **Une revue adversariale a trouvé 11 vrais défauts dans mon propre code**,
  tous corrigés. Les deux plus graves méritent d'être connus, parce qu'ils
  refaisaient exactement l'erreur qu'on corrigeait : « Tout désinstaller » et
  l'installeur d'addons utilisaient encore le **vieux** test de dossier — sur un
  chemin erroné, ils n'auraient rien supprimé du jeu et auraient quand même
  annoncé « ton jeu est revenu en anglais ». Toutes les actions qui écrivent ou
  suppriment passent maintenant par la barrière stricte.

---

### Ce qui attend une décision de toi

1. **Le dossier `Sound` (les voix) coché par défaut dans « Tout désinstaller » ?**
   Aujourd'hui : **coché**, parce que « tout désinstaller » doit vouloir dire
   tout. Mais c'est **1,6 Go** et un re-téléchargement complet si le joueur
   change d'avis. Le contraire se défend. Un seul mot dans
   `compagnon.py : VOIX_COCHEES_PAR_DEFAUT` et c'est changé.
2. **Faut-il aussi cocher les addons d'autres auteurs par défaut ?**
   Aujourd'hui : **décochés** (DragonUI, G.B.G ne sont pas de nous et marchent
   sans la traduction). Je pense que c'est le bon choix, mais c'est ton
   catalogue.
3. **La version.** `AscensionFR.toc` est à 3.3.0 et `VERSION_COMPAGNON` à
   3.3.1. Ces corrections ne touchent **que le Hub** : il faudra donc soit une
   3.3.2 « Hub seul », soit monter les deux ensemble. `publier_github.py` refuse
   aujourd'hui un tag qui ne colle pas au `.toc` — dis-moi lequel des deux tu
   veux et j'adapte.
4. **Le catalogue est bâké dans l'exe** : la correction DragonUI n'atteindra les
   joueurs qu'avec une nouvelle sortie du Hub. Ceux qui ont déjà DragonUI
   verront « module manquant : DragonUI_Options » sur leur carte et n'auront
   qu'à cliquer.

---

### Fichiers touchés

| fichier | quoi |
|---|---|
| `compagnon/compagnon.py` | racine du jeu, correction de dossier, contrôle d'installation, réparations, inventaire et suppression |
| `compagnon/interface_hub.py` | les deux fenêtres, les liens, la barrière stricte sur toute action qui écrit, l'installeur multi-dossiers |
| `compagnon/assets/hub/catalogue_hub.json` | `DragonUI_Options` déclaré comme dossier compagnon |
| `outils/construire_zip_release.py` | version lue, garde-fous, compilation Lua, nom provisoire, code de sortie |
| `outils/publier_github.py` | un seul builder, corps de release refait, liens absolus |
| `outils/verifier_hub.py` | +21 contrôles sur une installation cassée |
| `outils/README_OUTILS.md` | le rituel de release remis à jour |
| `depot_github/README.md`, `docs/INSTALLATION.md`, `docs/FAQ.md` | le zip visible, les bonnes consignes, la désinstallation complète |
| `docs/CONTEXTE_PROJET.md` | le compte rendu complet, pour Antigravity |

Deux chantiers hors périmètre repérés en chemin t'attendent en tâches de côté :
les deux outils DragonUI qui s'écrasent l'un l'autre, et la section « livrables »
du README racine qui décrit des fichiers disparus.
