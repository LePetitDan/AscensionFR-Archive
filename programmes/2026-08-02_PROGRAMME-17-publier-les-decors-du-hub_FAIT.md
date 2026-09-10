# Demande de code → Claude Code

# 🎨 PROGRAMME 17 — mettre les décors du Hub dans le dépôt public

**Date :** 2026-08-02
**Décision de Dan :** tout dans le dépôt public, directement.

---

## Pourquoi

Tetardtek a testé la PR #4 sous Proton. Le Hub **plante au démarrage** :

```
File "interface_hub.py", line 545, in __init__
    self.decor = Decor()
File "interface_hub.py", line 268, in __init__
    with open(os.path.join(self.dossier, MANIFESTE), …
FileNotFoundError: '.../compagnon/assets/hub/decor_hub.json'
```

`Decor.__init__` ouvre le manifeste **sans garde**, et `assets/hub/` n'est pas versionné.

**Ce n'est pas une exclusion voulue, c'est un oubli** — et il l'a démontré :
`assets/banner.png` et `assets/vitrine/*` **sont** versionnés, **aucune règle du `.gitignore`
n'exclut `assets/hub/`**, et `AscensionFR_Hub.spec` (l. 12) le déclare embarqué au build.

Sous Windows ça ne se voit pas : PyInstaller déploie `assets/` à l'exécution. Sous Linux il n'y a
pas d'exe. **Un clone sous Windows produit exactement le même plantage.**

Et le point qui rend ça urgent : **les joueurs Linux ne recevront jamais le Hub par la mise à
jour automatique**, puisqu'il n'y a pas d'exe chez eux. Sans ces fichiers, ils resteraient sur la
v2 indéfiniment.

---

## BLOC A — ce qu'il faut, et d'où ça vient

Tetardtek a extrait **98 fichiers** de l'exe 3.4.1 : `decor_hub.json`, **`catalogue_hub.json`**,
les PNG et les polices. Il ne les a **pas** commités — il a laissé la décision à Dan.

Sa liste te fait gagner du temps, mais **vérifie-la plutôt que de la recopier** :

- lance le Hub depuis un arbre sans `assets/hub/` et regarde ce qu'il réclame réellement ;
- **sépare clairement trois familles**, parce qu'elles n'ont pas le même statut :
  1. **les créations du projet** — `decor_hub.json`, les images faites pour le Hub ;
  2. **`catalogue_hub.json`** — ce n'est pas une texture, c'est **la liste des addons que le Hub
     propose d'installer**. Regarde ce qu'il y a dedans avant de le publier : URL, chemins,
     quoi que ce soit qui ne devrait pas être public ;
  3. **les fichiers du jeu** — les polices `Morpheus`, `FRIZQT`. Dan sait qu'il les publie, mais
     je veux que la liste soit écrite quelque part.
- combien de fichiers au total, quel poids.

Si le Hub réclame plus que `assets/hub/`, **dis-le avant de copier**.

---

## BLOC B — le balayage de secrets

`balayer_secrets.py` sur tout ce qui va partir, **avant** de copier. Ce sont surtout des images,
mais `decor_hub.json` et `catalogue_hub.json` sont des fichiers texte — exactement le genre
d'endroit où un chemin de disque ou une URL se cache.

Le programme 14 signalait déjà que le dépôt public expose `D:\AscensionFR\WorkFlow` en clair dans
du code. **Regarde si la même chose traîne ici.**

---

## BLOC C — copier, commiter, pousser

- ne touche **pas** aux 5 fichiers surveillés par `synchroniser_depot_public.py` ;
- vérifie que `verifier_arbre_publie.py` **passe toujours** après coup ;
- ⚠️ **pousse, puis vérifie que le push est arrivé.** Le garde-fou lit `git status --short`, qui
  **ne dit rien d'un commit non poussé** — c'est le trou du programme 14, et il a failli mordre
  hier soir. `git rev-list --count origin/main..main` doit valoir **0**.

🛑 **Aucun tag, aucune release.** La 3.4.1 est publiée et n'est pas concernée : on ajoute des
fichiers au dépôt, on ne sort pas de version.

---

## 🛑 BLOC D — la seule preuve qui compte

« Les fichiers sont là » ne prouve rien. **Clone le dépôt public dans un dossier temporaire, à
partir de zéro, et lance le Hub depuis ce clone.**

- s'il s'ouvre : c'est bon ;
- s'il plante sur un autre fichier manquant : **il en manquait d'autres**, et c'est exactement ce
  qu'on cherche à savoir.

C'est le test d'un contributeur qui découvre le projet. Si tu ne peux pas ouvrir de fenêtre depuis
ton environnement, va au moins jusqu'à l'appel qui plantait (`Decor()`) et prouve qu'il passe.

---

## BLOC E — une question, tu réponds sans rien corriger

Tetardtek signale qu'il n'a **pas pu éprouver l'envoi des rapports** : `WEBHOOK_RAPPORTS` est vide
dans les sources publiques, donc il retombe en mode « copier ».

**C'est structurel, et je veux ta lecture :** le webhook est neutralisé à la publication (et c'est
une règle qu'on ne change pas). Or un joueur Linux lance **les sources**, pas l'exe.

- Est-ce que ça veut dire qu'un joueur Linux ne pourra **jamais** envoyer un rapport en un clic,
  et restera à vie en mode copier-coller ?
- Si oui, quelles voies existent — sans jamais publier le webhook ?

**Ne code rien.** Dis-moi ce qu'il en est et ce que tu ferais. C'est une décision de Dan.

---

**« Terminé » veut dire :**

> - La liste exacte de ce qui part, **rangée en trois familles** (projet / catalogue / jeu).
> - Ce que contient `catalogue_hub.json`, avant publication.
> - Le balayage de secrets, propre.
> - Poussé, **et le push vérifié** — pas seulement commité.
> - **Un clone neuf où le Hub démarre**, ou le nom du fichier qui manque encore.
> - Ta réponse sur le webhook côté Linux.

🛑 **Aucun tag, aucune release, les 5 fichiers surveillés non touchés.**

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Puis renommer en `_FAIT.md`.)

---

## ✅ BLOC A — ce qu'il faut, et d'où ça vient

### Le plantage, reproduit sous Windows avant de toucher à quoi que ce soit

Je n'ai pas cru la liste sur parole : j'ai lancé le Hub depuis l'arbre public, tel qu'il est
publié aujourd'hui (`depot_github/compagnon`, 26 fichiers suivis) :

```
FileNotFoundError: [Errno 2] No such file or directory:
  'D:\AscensionFR\WorkFlow\depot_github\compagnon\assets\hub\decor_hub.json'
  interface_hub.py:544 in __init__   ->   self.decor = Decor()
  interface_hub.py:267 in __init__   ->   with open(os.path.join(self.dossier, MANIFESTE), …
```

**C'est exactement le plantage de Tetardtek, sous Windows, sans Proton, sans Linux.** Les lignes
sont décalées de 1 (544/267 chez moi, 545/268 chez lui) parce qu'il travaille sur la PR #4. Le
diagnostic du programme est donc juste sur toute la ligne : ce n'est pas un problème Linux, c'est
un dépôt incomplet que Windows masquait parce que PyInstaller déballe `assets/` à l'exécution.

Les trois preuves du « oubli, pas exclusion » se vérifient aussi :

| affirmation | vérifié |
|---|---|
| aucune règle du `.gitignore` n'exclut `assets/hub/` | ✅ `git check-ignore` sort en 1 (= non ignoré) ; le `.gitignore` public ne contient que `*.exe`, `*.zip`, `__pycache__/`, `*.pyc` |
| `AscensionFR_Hub.spec` le déclare embarqué | ✅ l. 29 `datas = [('assets', 'assets')]`, et le commentaire l. 12-13 nomme explicitement `assets/hub` |
| `assets/banner.png` et `assets/vitrine/*` sont versionnés | ✅ 9 fichiers d'illustration publiés, alors que `compagnon/assets/` public n'a que `logo.ico` + `logo.png` |

### Ce que le Hub réclame RÉELLEMENT — vérifié deux fois

**1. Statiquement.** J'ai relu le code publié à l'AST et extrait tous les noms passés au décor
(`poser` / `pil` / `photo` / `existe` / `pad`, plus les noms des `Bouton`), en résolvant les noms
construits (`"nav_" + vue`, `"etat_" + ton`, `"carte_ic_" + id`) à partir des énumérations du code
(`VUES`, `TONALITES`) et du catalogue. **51 noms exigés — aucun absent du manifeste.**

Le manifeste et les images se correspondent exactement : **94 entrées, 94 PNG, 0 orphelin des deux
côtés**.

**2. Dynamiquement.** J'ai reconstitué un arbre jetable à partir de `git archive HEAD` (donc
strictement ce qu'un clone donne), j'y ai ajouté `assets/hub/`, et j'ai lancé le Hub. **Il démarre
et se dessine.** J'ai capturé **les 5 vues** (accueil, traduction, voix, addons, contribuer) : les
cinq passent, images et polices du jeu comprises.

C'est important parce que le code n'est protégé qu'à moitié : `poser()` saute proprement une image
absente (le correctif de la 3.1.0), mais **`photo()` ne garde rien** — je compte 9 sites d'appel
non gardés (barre de navigation, pastilles, cases à cocher, tous les boutons via `Bouton._peindre`).
Une seule image manquante parmi celles-là aurait planté le Hub. Aucune ne manque.

### Les trois familles

| famille | fichiers | poids | quoi |
|---|---:|---:|---|
| **1. créations du projet** | **95** | 1 124,6 Ko | `decor_hub.json` (manifeste de cotes, 5,9 Ko) + **94 PNG** fabriqués pour le Hub |
| **2. catalogue** | **1** | 1,3 Ko | `catalogue_hub.json` |
| **3. fichiers du jeu** | **2** | 127,3 Ko | `fonts/MORPHEUS.TTF` (66,4 Ko), `fonts/FRIZQT__.TTF` (60,9 Ko) |
| **TOTAL** | **98** | **1 253,3 Ko (1,22 Mo)** | |

Le compte de Tetardtek est bon : **98 fichiers**. Et ce sont bien les mêmes — les 98 sont déjà
suivis par git **dans le dépôt privé** (`git ls-files compagnon/assets/hub/` = 98). Il n'y a donc
rien à extraire d'un exe : la source de vérité est ici, à jour, et c'est elle que je publie.

**Famille 3, la liste écrite noir sur blanc, comme demandé :**

- `compagnon/assets/hub/fonts/MORPHEUS.TTF` — police des titres de WoW
- `compagnon/assets/hub/fonts/FRIZQT__.TTF` — police de corps de WoW

Ce sont des fichiers Blizzard. Elles sont chargées en `FR_PRIVATE` (rien n'est installé sur la
machine du joueur, rien ne survit à la fermeture), et leur absence ne planterait pas le Hub —
`charger_polices()` teste `os.path.isfile` et le repli est Georgia. Elles partent quand même,
puisque c'est la décision de Dan, mais **c'est la seule famille dont la publication est un choix
et pas une nécessité technique.**

### Ce que contient `catalogue_hub.json`, avant publication

Ce n'est pas une texture : c'est **la liste des addons que le Hub propose d'installer**, et donc
**les URL depuis lesquelles il télécharge chez le joueur**. Contenu intégral, 4 entrées :

| id | dossier | FR | URL de téléchargement |
|---|---|---|---|
| `ascensionfr_confort` | AscensionFR-Confort | ✅ | `github.com/LePetitDan/AscensionFR-Confort/releases/latest/download/…` |
| `ascensionfr_equipement` | AscensionFR-Equipement | ✅ | `github.com/LePetitDan/AscensionFR-Equipement/releases/latest/download/…` |
| `ascensionfr_peche` | AscensionFR-Peche | ✅ | `github.com/LePetitDan/AscensionFR-Peche/releases/latest/download/…` |
| `dragonui` | DragonUI (+ DragonUI_Options) | ❌ traduit par nous | `github.com/PentSec/DragonUI/releases/latest/download/DragonUI.zip` |

**Rien de privé :** aucun jeton, aucun chemin de disque, aucune URL interne, aucun webhook. Les
quatre URL sont des `releases/latest/download` publics — trois dépôts de Dan, un dépôt tiers
(PentSec/NeticSoul, licence MIT, crédité dans le fichier). Ce sont exactement les adresses que
**chaque Compagnon installé chez un joueur appelle déjà** : les publier ne révèle rien qui ne soit
pas déjà sur le fil.

Le seul point sur lequel je veux être franc : publier ce fichier rend **lisible d'un coup d'œil**
la liste des dépôts d'addons de Dan. Ils sont publics et déjà atteignables, donc ce n'est pas une
fuite — mais c'est un choix, et il est fait sciemment.

### 🛑 Ce que je dois signaler AVANT de copier

Le programme demande : « si le Hub réclame plus que `assets/hub/`, dis-le avant de copier ».
**Pour le Hub qui s'exécute : non, `assets/hub/` suffit — prouvé.** Deux réserves quand même :

1. **`fabriquer_decor_hub.py` est publié, mais reste infabriquable pour un contributeur.** C'est
   l'un des 5 fichiers surveillés, donc il est dans le dépôt public — et il lit deux choses qui n'y
   sont pas : `compagnon/assets/v2ui/` (l. 774, les boutons Discord/café repris de la v2, 52
   fichiers non publiés) et **les textures du jeu extraites** (`texture("ICONS", …)`,
   `texture("Buttons", "UI-Quickslot2.PNG")`), qui ne pourront jamais être versionnées. Autrement
   dit : après ce programme, un contributeur pourra **lancer** le Hub, pas **régénérer** les
   décors. Je ne le corrige pas — ce n'est pas demandé, et ça mériterait sa propre décision.
2. **Trois images restent absentes du dépôt public et le resteront** : `discord.png`,
   `twitch.png`, `youtube.png` (et leurs variantes `_pale`) que lit la vieille interface v2 de
   `compagnon.py`. Sans conséquence : `_image()` rend `None` et le code retombe sur un lien texte.
   Je le note pour que « il manque des PNG dans `compagnon/assets/` » ne repasse pas pour un bug.

Un détail rassurant au passage : `carte_ic_dbm`, `carte_ic_adibags` et `carte_ic_lootcollector`
ne sont pas des restes morts, contrairement à ce que laissait croire ma première lecture — ce sont
les trois cartes « Bientôt… » ajoutées en dur dans `interface_hub.py`, et elles s'affichent bien
dans la capture de la vue Addons.

---

## ✅ BLOC B — le balayage de secrets

### Le balayage officiel : vert, mais il n'a lu que 2 fichiers sur 98

`balayer_secrets.py --racine <arbre jetable> --sans-historique`, lancé sur l'arbre exact qui va
être publié (HEAD + `assets/hub/`) :

```
motifs cherchés : 20 familles + l'heuristique d'entropie
--- 1. l'arbre de travail (TOUTES extensions) ---
    0 motif(s) trouvé(s)
✅ aucun motif de secret               (code de sortie 0)
```

**Mais je ne peux pas m'arrêter là.** `secrets_publication.py` l. 195 écarte les binaires par
extension, et `.png` comme `.ttf` sont de la liste. Sur les 98 fichiers, le balayeur officiel en a
donc **ouvert 2** : `decor_hub.json` et `catalogue_hub.json`. Écrire « balayage propre » en
s'arrêtant à cette ligne serait une demi-vérité — c'est le genre de silence qui fait passer un
garde-fou pour une preuve.

### Le balayage que j'ai ajouté : les 96 binaires, vraiment lus

Un PNG **peut** porter du texte : les segments `tEXt` / `iTXt` / `zTXt` sont faits pour ça, et
beaucoup d'outils y écrivent le chemin du fichier source. Une police porte sa table `name`
(copyright, auteur, parfois un chemin de compilation). J'ai donc extrait toutes les suites
imprimables des 96 binaires et je leur ai appliqué **les mêmes motifs** que le balayeur officiel
(`balayer_texte`, les 20 familles), plus une recherche de chemins de disque.

```
BALAYAGE DES BINAIRES — 96 fichier(s) que le balayeur officiel saute
suites imprimables extraites : 3434
segments de texte PNG (tEXt/iTXt/zTXt/eXIf) : 0
motifs de secret                            : 0
chemins de disque en clair                  : 0
✅ rien                                       (code de sortie 0)
```

Zéro segment de texte dans les 94 PNG : ils sortent de PIL, qui écrit des images nues. Les deux
polices ne portent que leurs tables Blizzard. **Les 98 fichiers ont maintenant tous été lus.**

### Les deux JSON, relus à la main

- `decor_hub.json` : 94 entrées, **uniquement des nombres** (`w`, `h`, `pad`). Zéro valeur texte,
  donc zéro endroit où un chemin pourrait se cacher. Vérifié par programme, pas à l'œil.
- `catalogue_hub.json` : 4 entrées, détaillées au bloc A. 4 URL `github.com/…/releases/latest/
  download/…`, publiques, déjà appelées par tous les Compagnons installés.

### Le chemin en clair du programme 14 : il est toujours là, et je n'y touche pas

Le programme demande de regarder si `D:\AscensionFR\WorkFlow` traîne ici. **Dans les 98 fichiers
qui partent : non, aucun.** Dans le dépôt public tel qu'il est déjà en ligne : **oui, une fois**,
inchangée depuis le programme 14 —

```
compagnon/compagnon.py:2227    if os.path.isdir(r"D:\AscensionFR\WorkFlow"):
```

C'est le **garde-fou ATELIER** : sur la machine de Dan, le bouton « Mettre à jour » refuse d'agir
parce que réinstaller le zip écraserait les corrections pas encore publiées (29 perdues le
18/07/2026). Ce n'est pas un secret — ça révèle l'arborescence de disque du mainteneur, rien de
plus, et rien qui ne s'obtienne en lisant les rapports du projet. Le retirer casserait le
garde-fou ; le remplacer par un marqueur neutre (un fichier témoin dans le dossier) serait
propre, **mais ce programme ne le demande pas et ça touche l'un des 5 fichiers surveillés.**
Je le laisse tel quel et je le signale.

**Verdict du bloc B : rien ne part qui ne doive partir.** 98 fichiers sur 98 examinés, deux
balayages indépendants, zéro motif.

---

## ✅ BLOC C — copier, commiter, pousser

### Ce qui est fait

**Base de référence, avant de toucher à quoi que ce soit :**

- `verifier_arbre_publie.py --version 3.4.1` → **vert** (les 4 contrôles) ;
- empreintes SHA-256 des 5 fichiers surveillés relevées et mises de côté ;
- `git fetch` puis comparaison : local et `origin/main` **au même commit** `eae7036`, 0 en avance,
  0 en retard. Je ne suis pas parti d'un dépôt déjà décalé.

**La copie :** `compagnon/assets/hub` → `depot_github/compagnon/assets/hub`, puis vérification
**octet par octet** des 98 fichiers dans les deux sens (rien qui manque, rien qui diffère, rien en
trop) : **0 écart**.

**Les 5 fichiers surveillés n'ont pas bougé** — `sha256sum -c` sur le relevé d'avant :

```
compagnon/compagnon.py: OK          compagnon/fabriquer_decor_hub.py: OK
compagnon/compagnon_hub.py: OK      compagnon/AscensionFR_Hub.spec: OK
compagnon/interface_hub.py: OK
```

Et `git status` le confirme d'un autre angle : **1 seule entrée** (`?? compagnon/assets/hub/`),
**0 modification de fichier existant**. Après indexation : **98 ajouts, 98 « A », aucun « M »**.

**Commit `5b2d86c`** — « Décors du Hub versionnés : le dépôt se lançait sur un plantage ».

**Les garde-fous, relancés après le commit :**

| contrôle | résultat |
|---|---|
| `verifier_arbre_publie.py --version 3.4.1` | ✅ **toujours vert**, les 4 points |
| `synchroniser_depot_public.py` (simulation) | ✅ « rien à faire » — les 5 sources restent identiques au privé neutralisé |
| `balayer_secrets.py` **arbre + historique** | ✅ 0 motif, **129 blobs texte** relus, nouveau commit compris |

### Le push, et sa vérification

Un premier essai de push a été **refusé par le classificateur de permissions de Claude Code** —
pas par un garde-fou du projet ; les trois étaient vertes. Je n'ai pas contourné, j'ai rendu la
main. **Dan a autorisé explicitement**, et le push a été fait :

```
To https://github.com/LePetitDan/AscensionFR.git
   eae7036..5b2d86c  main -> main
```

**Le contrôle que réclame le programme, et qui est le seul à dire la vérité :**

```
git rev-list --count origin/main..main  =  0     ✅
git rev-list --count main..origin/main  =  0     (rien en retard non plus)
```

Et vérifié **depuis le distant lui-même**, sans passer par ma copie locale des références — parce
qu'un `origin/main` local peut mentir s'il n'a pas été rafraîchi :

```
$ git ls-remote origin refs/heads/main
5b2d86c6569859a0b3bd788242923d3727a460e2   refs/heads/main
```

**L'épisode vaut d'être noté, parce qu'il a joué le trou du programme 14 en vrai.** Entre le
commit et le push, `git status --short` sortait **propre** — 0 ligne — sur un travail que
personne n'avait. Le garde-fou qui ne lit que lui aurait dit « tout va bien » à ce moment précis.
Seul `origin/main..main` valait 1 et le disait.

🛑 **Aucun tag posé, aucune release créée.** Vérifié sur le distant après le push : les tags
restent `v3.3.0`, `v3.3.1`, `v3.4.0`, `v3.4.1` — et `v3.4.1` pointe toujours sur `eae7036`,
inchangé. Aucun des 5 fichiers surveillés touché.

---

## ✅ BLOC D — la seule preuve qui compte

Je peux ouvrir des fenêtres depuis cet environnement (écran 5120 × 1440), donc je n'ai pas eu à me
rabattre sur « je prouve que `Decor()` passe » : **j'ai vraiment lancé le Hub, depuis un clone
neuf, et je l'ai photographié.**

Le test a été fait **deux fois** : une première sur un clone du dépôt local (avant le push, qui
était alors bloqué), et une seconde — celle qui compte — **sur un clone de
`github.com/LePetitDan/AscensionFR`**, après le push. Les deux donnent le même résultat ; c'est
la seconde qui est rapportée ici.

**Le clone, tel que GitHub le rend :**

```
$ git clone https://github.com/LePetitDan/AscensionFR.git
5b2d86c Décors du Hub versionnés : le dépôt se lançait sur un plantage
fichiers suivis : 124        (26 avant, + 98)
dont assets/hub  :  98
```

**Intégrité après aller-retour par GitHub :** les 98 fichiers redescendus du distant, comparés en
SHA-256 à la source privée → **0 écart**. Ce n'est pas une formalité : le dépôt tourne avec
`core.autocrlf = true` et **sans `.gitattributes`**. Si git avait pris un PNG pour du texte, il
aurait réécrit ses fins de ligne et l'aurait corrompu au checkout. Les 94 PNG et les 2 TTF
ressortent intacts (git les détecte binaires par leurs octets nuls), et les 2 JSON reviennent
identiques eux aussi.

**Le lancement, depuis le clone GitHub :**

| vue | résultat |
|---|---|
| accueil | ✅ démarre et se dessine |
| traduction | ✅ |
| voix | ✅ |
| addons | ✅ (les 7 icônes de cartes, dont les 3 « Bientôt… ») |
| contribuer | ✅ |

**Zéro sortie d'erreur, code 0 sur les cinq.** Les polices du jeu sont chargées (les titres sont
en Morpheus, pas en repli Georgia), les 94 images sont trouvées.

Captures : `gh_accueil.png`, `gh_traduction.png`, `gh_voix.png`, `gh_addons.png`,
`gh_contribuer.png` (bloc-notes de la session).

**Réponse à la question du bloc D : il ne manquait rien d'autre.** Le seul fichier qui manquait
était bien le dossier `assets/hub/` en entier. **C'est le test du contributeur qui découvre le
projet, et il passe : `git clone`, `python compagnon_hub.py`, la fenêtre s'ouvre.**

Précision de méthode : j'ai utilisé le mode `--demo` intégré au Hub. Ce n'est pas une esquive,
c'est **plus sûr** — il court-circuite `verifier()`, les trois fils réseau et surtout le
`self.after(2500, self.envoi_auto_au_lancement)` qui expédie la récolte à l'ouverture. Lancer le
Hub « pour voir » sans ça, sur la machine de Dan, aurait pu déclencher un envoi réel.

---

## ✅ BLOC E — le webhook côté Linux (réponse seule, rien codé)

### D'abord : c'est pire que ce que Tetardtek décrit

Il dit qu'il « retombe en mode copier ». **Ce n'est vrai que du Compagnon v2. Dans le Hub, le
mode copier n'existe pas.**

- `compagnon.py` (interface v2) : le bouton **« 📋 Copier mon rapport » est affiché en
  permanence** (l. 2036), à côté de « 📨 Envoyer », lui conditionné au webhook. Le texte d'aide
  change aussi : sans webhook, il dit « Copie ton rapport et colle-le sur le Discord » (l. 2017).
  Le repli est réel et complet.
- `interface_hub.py` (le Hub) : **`copier_rapport` n'existe pas.** Les seuls usages du
  presse-papier sont `copier_diagnostic` (Ctrl+D — le relevé d'installation, pas le rapport) et
  `_copier_controle` (le contrôle d'installation). Le bouton d'envoi est simplement peint en
  `btn_envoyer_gris` et rendu inactif (l. 2282-2286), et **le texte d'aide n'est pas
  conditionnel** : il annonce « Un clic, et ton rapport part aider la traduction » (l. 2222) à
  quelqu'un qui n'a aucun bouton vivant.

**Un joueur Linux ne reste donc pas « à vie en copier-coller » : il n'a rien du tout.** Une phrase
qui lui promet un clic, un bouton gris, et aucune autre voie.

**Et il y a un mensonge dans un message d'erreur.** `interface_hub.py` l. 2379, quand un envoi
échoue :

> « Tu peux aussi copier le rapport (**bouton ci-dessous**) et le coller sur le Discord. »

Ce bouton n'existe pas dans le Hub. Le code enchaîne d'ailleurs sur `copier_diagnostic`, qui met
le **relevé d'installation** dans le presse-papier — pas le rapport. Un joueur qui suit ce message
colle la mauvaise chose sur le Discord. Ça touche **tout le monde**, pas seulement Linux : c'est
le chemin d'échec réseau de n'importe quel joueur Windows.

Je n'y touche pas — le programme dit « ne code rien » — mais tu dois le savoir.

### Réponse à ta question : oui, structurellement — et la vraie raison est ailleurs

Oui. Tant que la seule voie d'envoi est un webhook baké à la construction, **quelqu'un qui lance
les sources ne pourra jamais envoyer en un clic**, par construction. Et la règle est juste : un
webhook Discord est une **autorisation d'écriture à porteur** — qui l'a poste ce qu'il veut dans
le salon, et il n'y a ni compte, ni quota, ni identité. Publié dans un dépôt public, il est trouvé
par les robots de balayage en quelques heures. On ne le publie pas.

Mais je veux corriger le cadre, parce qu'il change les options : **le webhook baké dans l'exe
n'est pas secret non plus.** Un exe PyInstaller se déballe — Tetardtek vient précisément d'en
extraire 98 fichiers pour te les proposer. Le bytecode qui contient l'URL s'extrait de la même
façon, avec un outil public et deux commandes.

Ce qu'on protège n'est donc pas la confidentialité du webhook : **c'est sa non-indexation.** La
différence entre l'exe et le dépôt, ce n'est pas « caché » contre « visible », c'est « il faut le
vouloir » contre « un robot le trouve tout seul ». C'est une protection réelle et elle vaut la
peine — mais elle ne justifie pas de laisser les joueurs Linux sans rien, parce qu'elle ne les
protège de rien.

### Les voies, sans jamais publier le webhook

**1. Rendre au Hub le bouton « Copier mon rapport ». — à faire de toute façon, quelle que soit ta
décision.**
Le code existe déjà (`compagnon.py:2405`), et le Hub importe `compagnon` comme `logique` : c'est
un bouton à reposer, pas une fonction à écrire. Ça ne donne pas le clic unique, mais ça rend
**vraie** la phrase que le Hub affiche déjà en cas d'échec, et ça sort le joueur Linux de rien du
tout. Zéro secret, zéro risque, zéro hébergement. **C'est le minimum honnête.**

**2. Construire un binaire Linux. — la seule voie qui rend les joueurs Linux vraiment égaux.**
Si la release porte un `.AppImage` (ou un exécutable PyInstaller Linux) construit par GitHub
Actions sur un tag, le webhook s'y injecte à la construction **exactement comme sous Windows** :
il vit dans un secret d'Actions, jamais dans le dépôt, et les workflows déclenchés depuis un fork
n'y ont pas accès. La règle n'est pas entamée d'un pouce.

Et ça règle le second problème que tu soulèves en tête de programme, celui qui est plus grave que
le webhook : **sans binaire Linux, ces joueurs n'ont pas non plus la mise à jour automatique.**
Ils resteront sur ce qu'ils ont installé à la main, indéfiniment. Publier `assets/hub/` leur rend
un Hub qui démarre ; seul un binaire leur rend un Hub qui se tient à jour. C'est le vrai chantier,
et c'est une décision de budget, pas de sécurité.

**3. Un relais. — possible, mais c'est un service à tenir.**
Un petit point d'entrée public (Cloudflare Worker ou équivalent) qui détient le webhook, valide la
forme du rapport, limite le débit par IP, et reposte. Le webhook n'est jamais exposé, l'URL
publique est **révocable et limitable** — ce que le webhook n'est pas. Mais c'est un service de
plus à héberger, à surveiller et à réparer quand il tombe. **Je ne le recommande pas tant que
l'option 2 n'a pas été écartée** : elle coûte moins cher et donne davantage.

**4. Passer par GitHub. — à écarter.**
Le joueur ouvre une issue avec son rapport en pièce jointe : zéro secret, mais il faut un compte
GitHub. On perdrait la quasi-totalité des contributeurs — ceux qui contribuent aujourd'hui le font
justement parce que c'est un clic.

**5. Le joueur fournit son propre webhook. — à écarter aussi.**
Le rapport partirait dans *son* salon, pas le nôtre. Ça ne résout rien.

### Ce que je ferais, à ta place

**Option 1 tout de suite** (c'est une correction de défaut, pas une fonctionnalité : le Hub ment
déjà à ses joueurs), puis **option 2 quand tu voudras vraiment ouvrir le support Linux** — parce
que sans elle, « on supporte Linux » veut dire « on supporte une installation manuelle qui ne se
mettra jamais à jour et dont les joueurs ne peuvent pas contribuer ». C'est ta décision, et il n'y
a rien d'urgent : ce qui était urgent — un Hub qui ne démarre pas du tout — est réglé par ce
programme.

---

## 🛑 Terminé — l'état exact

| « Terminé » veut dire | état |
|---|---|
| la liste exacte de ce qui part, rangée en trois familles | ✅ 98 fichiers, 1,22 Mo — 95 créations du projet / 1 catalogue / 2 polices du jeu |
| ce que contient `catalogue_hub.json`, avant publication | ✅ 4 addons, 4 URL `releases/latest/download` publiques, rien de privé |
| le balayage de secrets, propre | ✅ **98/98 fichiers lus** (le balayeur officiel n'en ouvrait que 2), 0 motif, 0 chemin de disque |
| poussé, **et le push vérifié** | ✅ `eae7036..5b2d86c` — `rev-list --count origin/main..main` = **0**, confirmé par `git ls-remote` |
| un clone neuf où le Hub démarre | ✅ cloné **depuis GitHub**, 5 vues sur 5, 0 écart d'intégrité sur les 98 fichiers |
| la réponse sur le webhook côté Linux | ✅ et une correction : dans le Hub il n'y a **pas** de mode « copier » |

🛑 **Aucun tag, aucune release, les 5 fichiers surveillés non touchés** — vérifié par empreinte et
sur le distant, pas de mémoire.

**Ce que ça change, concrètement :** `git clone` puis `python compagnon_hub.py` ouvre maintenant
le Hub. Un joueur Linux qui part des sources a une application qui démarre — ce qui n'était pas le
cas ce matin. Ce qu'il n'a toujours pas : la mise à jour automatique (pas de binaire) et l'envoi
de ses rapports (bloc E).

**Ce que ce programme a coûté en irréversible :** un commit et un push sur le dépôt public. Rien
d'autre. Pas de version publiée, pas d'annonce, aucun joueur touché tant qu'il ne clone pas le
dépôt : les Compagnons installés continuent de tourner exactement comme avant.

**Trois choses trouvées en chemin, notées, non corrigées** (aucune n'est demandée ici) :

1. `interface_hub.py:2379` promet « copier le rapport (bouton ci-dessous) » — **ce bouton n'existe
   pas dans le Hub**, et le code copie le relevé d'installation à la place. Touche tous les
   joueurs, pas seulement Linux.
2. `fabriquer_decor_hub.py` est publié mais reste infabriquable pour un contributeur : il lit
   `assets/v2ui/` (non publié) et les textures extraites du jeu (impubliables).
3. `compagnon.py:2227` expose toujours `D:\AscensionFR\WorkFlow` en clair — c'est le garde-fou
   ATELIER, il fait son travail ; un fichier témoin ferait pareil sans nommer le disque de Dan.
