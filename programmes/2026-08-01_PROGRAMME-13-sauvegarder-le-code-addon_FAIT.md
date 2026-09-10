# Demande de code → Claude Code

# 💾 PROGRAMME 13 — mettre le code de l'addon à l'abri

**Date :** 2026-08-01
**Accord de Dan donné.** À faire pendant que la 3.4.1 se construit — c'est indépendant.

---

## Le problème

`WOW_Priv\resources\ascension-live\Interface\AddOns\AscensionFR\` — `Core.lua`, le `.toc` et les
24 fichiers de `Modules\` — **n'est dans aucun dépôt**. Le dépôt du projet couvre `WorkFlow\`,
pas ça.

**Ce code n'existe donc qu'en un seul exemplaire, sans historique.** Au programme 10, `Perf.lua` a
été réécrit une dizaine de fois : aucune version intermédiaire n'est récupérable. C'est ~600 Ko
qui représentent des mois de travail.

---

## 🛑 BLOC A — chercher des secrets AVANT toute chose

**Ne crée aucun dépôt tant que ce bloc n'est pas rendu.**

L'addon parle au Hub, et le Hub parle à un webhook. Si une URL, un jeton ou une clé traîne dans un
fichier Lua de l'addon, il ne faut pas qu'il entre dans un historique — un historique, ça ne
s'efface pas, ça se réécrit.

Passe **`balayer_secrets.py`** (posé au programme 6) sur tout le dossier de l'addon, et
dis-moi ce qu'il trouve. Regarde en particulier `Modules\Signaler.lua`, qui est le module
d'envoi. **Si quelque chose sort, arrête-toi et dis-le-moi** : on décidera avant, pas après.

---

## 🛑 BLOC B — le dossier du jeu n'est pas un endroit sûr

Le code vit **à l'intérieur de l'installation du jeu**. Or un patch de **2 Go** vient de tomber
(Saison 10). Les dossiers `AddOns` survivent normalement à une mise à jour — **normalement**.
Mettre un `.git` là-dedans, c'est confier l'unique sauvegarde à un dossier qu'un lanceur tiers
peut réécrire ou nettoyer sans prévenir.

**Dis-moi quelle forme tu recommandes**, avec ses inconvénients :

- un dépôt **dans** le dossier de l'addon, simple mais logé chez le jeu ;
- un dépôt **ailleurs** (par exemple sous `WorkFlow\`), avec un geste de recopie — plus sûr, mais
  il faut que ce geste soit lancé, sinon il ne protège rien ;
- une autre disposition si tu vois mieux.

**Le critère : qu'est-ce qui survit à quelqu'un qui oublie de faire quelque chose ?** Une
sauvegarde qui dépend d'un geste manuel régulier n'en est pas vraiment une.

---

## BLOC C — ce qui entre, ce qui reste dehors

| | |
|---|---|
| ✅ **entre** | `Core.lua`, `AscensionFR.toc`, `Bindings.xml`, tout `Modules\` |
| ❌ **reste dehors** | `DB\` (**101,7 Mo**) et `DB_sauvegarde_build\` — **régénérés par le pipeline, jetables**. Les versionner ferait exploser le dépôt pour rien. |
| ❓ **à trancher, dis-moi** | `AscensionFR_Repliques\` — c'est un second addon, avec 17 Mo de base. Son code est-il, lui aussi, sans sauvegarde ? |

Le `.gitignore` doit être écrit **avant** le premier commit, pas après : un fichier de 27 Mo entré
par erreur reste dans l'historique même si on le retire ensuite.

---

## 🛑 BLOC D — ne pas confondre avec le dépôt privé existant

**Règle permanente du projet :** le dépôt privé de `WorkFlow\` **porte le webhook dans son
historique et ne doit JAMAIS recevoir de distant.** Celui-ci est un **dépôt différent**, il ne
doit ni le rejoindre, ni en hériter, ni être poussé à sa place.

Et **ne pousse rien nulle part.** Crée le dépôt, fais le premier commit, et dis-moi :

- ce qu'il pèse ;
- combien de fichiers il suit ;
- si le BLOC A est propre, **ce qu'il faudrait pour l'envoyer sur un dépôt privé distant** — parce
  qu'un dépôt local protège d'une mauvaise modification, **pas d'un disque qui meurt**. Le geste
  reste à Dan.

---

**« Terminé » veut dire :**

> - Le résultat du balayage de secrets, avant tout le reste.
> - Ta recommandation sur l'emplacement, et ce qu'elle coûte quand on oublie.
> - Le dépôt créé, le `.gitignore` écrit avant le premier commit, `DB\` exclu.
> - Le poids réel et le nombre de fichiers suivis.
> - Le sort d'`AscensionFR_Repliques`.
> - Ce qu'il reste à faire pour une copie hors de cette machine.

🛑 **Rien de poussé. Aucun distant ajouté. Le dépôt privé de `WorkFlow` n'est pas touché.**

---
## Réponse de Claude Code

### BLOC A — balayage de secrets : **propre**, et l'instrument mord

`balayer_secrets.py` sur tout `AddOns\AscensionFR\` (20 familles de motifs + l'heuristique
d'entropie) : **0 motif trouvé.**

**Je n'ai pas pris ce zéro pour argent comptant.** Un zéro peut vouloir dire « rien à
trouver » ou « rien n'a été lu ». J'ai donc vérifié les deux :

**1. Le balayage a-t-il vraiment lu ?** Instrumenté, il rend :

| | |
|---|---|
| fichiers réellement lus | **84** |
| caractères réellement lus | **217 286 724** (les 212 Mo de bases comprises) |
| fichiers sautés | **0** |
| temps | 62 s |

**2. Le balayage mord-il ?** J'ai fait une copie de contrôle, planté un faux webhook Discord
dans `Signaler.lua` et un faux jeton GitHub **au fond** d'un gros fichier de base, et relancé :

```
🛑 3 SECRET(S) — REFUS DE PUBLIER
   DB/DB_Quetes.lua:326        jeton GitHub : ghp_AbCdEfGh…ab
   Modules/Signaler.lua:577    webhook Discord : https://disc…89
   Modules/Signaler.lua:577    webhook Discord (forme nue) : discord.com/…89
```

Il attrape les deux, y compris celui noyé dans un fichier généré. **Le zéro est donc un vrai
zéro.**

**`Signaler.lua` en particulier : aucune URL, aucun jeton, aucune clé.** Et c'est structurel,
pas une chance : le Lua de WoW **n'a aucune API réseau**. Un addon 3.3.5a ne *peut pas* parler
à un webhook. Il écrit dans ses SavedVariables, et c'est le Compagnon — du Python, hors du jeu —
qui poste. Le secret ne peut donc vivre que côté Compagnon, où il est déjà connu et déjà
neutralisé à la publication.

**Les deux seules URL de tout l'addon**, toutes deux publiques et voulues :

- `Options.lua:30` → `https://buymeacoffee.com/lepetitdan`
- `Options.lua:34` → `https://discord.gg/kFJGDJbeay`

Elles s'affichent déjà dans le panneau d'options sur les 274 machines. Rien à cacher.

> ⚠️ Une réserve honnête : le balayage cherche des **motifs connus**. Il ne prouve pas
> l'absence d'un secret d'une forme qu'aucun des 20 motifs ne décrit. Sur ce dossier c'est
> peu inquiétant — il n'y a que 2 URL en tout, et je les ai lues.

**→ Feu vert pour la suite.**

---

### BLOC B — emplacement : ni dans le jeu, ni avec un geste de recopie

#### D'abord, j'ai voulu mesurer plutôt que supposer

Le projet fait **déjà** tourner le modèle « dépôt ailleurs + recopie » : `AscensionFR-Confort`,
`-Equipement` et `-Peche` sont trois dépôts git sous `WorkFlow\depot_forks\` (avec distants
GitHub), doublés d'une copie vivante dans le jeu. J'ai comparé les six copies.

Résultat brut : Pêche montrait 664 + 764 lignes divergentes. **C'était faux** — c'est
entièrement du CRLF contre LF. À contenu comparé, **0 différence réelle** partout.

**Je ne peux donc pas m'en servir comme preuve** : ces trois addons n'ont pas bougé depuis
9 jours. Le geste de recopie n'a rien eu à protéger — il n'a pas tenu, il n'a pas été
éprouvé. (Et : `grep` sur tout le pipeline, **aucun script ne recopie `depot_forks` vers le
jeu**. C'est un geste de mémoire pure.)

#### Ce que j'ai trouvé à la place, et qui tranche

Le jeu n'est pas « dans un dossier de jeu ». Il est **à l'intérieur du dossier `resources\`
d'une application Electron qui se met à jour toute seule** :

```
WOW_Priv\
  Ascension Launcher.exe          ← application Electron
  resources\
    app.asar                      ← le code du lanceur
    app-update.yml                ← provider: generic
                                     url: https://cdn-launcher.ascension-patch.com/update
    ascension-live\               ← LE JEU. Et notre addon dedans.
```

`app-update.yml` est le fichier de configuration d'`electron-updater`. Le lanceur télécharge
et exécute un installeur pour se remplacer lui-même, et `resources\` est le dossier que cet
installeur réécrit.

**Je n'ai pas déclenché de mise à jour du lanceur pour le vérifier — et je ne le ferai pas.**
Mais c'est le point : une sauvegarde dont on ne peut pas prouver qu'elle survit n'est pas une
sauvegarde. Le patch de 2 Go de Saison 10, lui, a bien épargné `AddOns\` (les dossiers
`Blizzard_*` sont intacts au 15/07). Un patch de contenu et une mise à jour du **lanceur** ne
sont pas le même événement.

#### Ma recommandation : `git init --separate-git-dir`

Ni l'une ni l'autre des deux formes proposées. Une troisième, que git sait faire nativement :

```
D:\AscensionFR\depot_addon.git\        ← le dépôt : objets, historique, tout
…\Interface\AddOns\.git                ← un FICHIER de 3 lignes qui pointe dessus
```

On travaille normalement dans le dossier du jeu (`git add`, `git commit`, `git log` y
fonctionnent), mais **l'historique n'y est pas**. Il est hors du rayon de souffle du lanceur.

Pourquoi ça règle le critère « qu'est-ce qui survit à un oubli ? » :

- **il n'y a aucun geste de recopie à oublier** — il n'y a pas de seconde copie ;
- **rien ne peut diverger**, pour la même raison ;
- si le lanceur efface `resources\`, l'historique est intact et **l'addon se restaure d'un
  `git checkout`**.

**Ce que ça coûte, franchement.** Le fichier `.git` contient un **chemin absolu**. Si l'un des
deux dossiers déménage, ça casse. Et ce projet a déjà déménagé une fois
(`WOW_Priv\traduction` → `D:\AscensionFR\WorkFlow`).

Mais **cette panne-là est bruyante** : git refuse la première commande, immédiatement, avec le
chemin qu'il cherchait. La panne du geste de recopie est **silencieuse** : tout a l'air normal
jusqu'au jour où on a besoin de la sauvegarde. Entre deux fragilités, je prends celle qui crie.

**Pourquoi `D:\AscensionFR\` et pas `WorkFlow\`**, comme suggéré : `WorkFlow\` est lui-même un
dépôt git. Y nicher un second dépôt (même ignoré, comme l'est déjà `depot_github\`) le met à
portée d'un `git clean -xdf` — qui efface les fichiers ignorés. `depot_github\` survivrait, il
a un distant. **Notre dépôt addon n'en aura pas : il serait perdu pour de bon.** Il va donc à
côté, pas dedans.

**Un point technique décidé au passage.** `core.autocrlf` vaut `true` sur cette machine —
c'est ce qui explique le faux écart de Pêche. Je le mets à `false` sur ce dépôt, avec un
`.gitattributes` qui dit `* -text`. Raison : ce dossier est écrit par le pipeline **et** lu par
le client WoW. Git doit y être un **greffier**, pas un correcteur. S'il réécrivait les fins de
ligne, chaque fichier régénéré par l'Atelier ressortirait « modifié » à perpétuité, et
l'historique deviendrait du bruit qu'on cesserait de lire.

---

### BLOC C — le périmètre, et le sort de `Repliques`

**Correction de mesure** : `Modules\` contient **23** fichiers, pas 24.

| | |
|---|---|
| ✅ **entre** | `Core.lua`, `AscensionFR.toc`, `Bindings.xml`, les 23 `Modules\*.lua` — **613 Ko** |
| ❌ **reste dehors** | `DB\` (114 Mo) et `DB_sauvegarde_build\` (98 Mo) |

**`AscensionFR_Repliques` : la question se dissout.** Ce n'est pas « un second addon avec
17 Mo de base ». C'est **17 Mo de base, et rien d'autre** :

```
AscensionFR_Repliques.toc      222 octets   ← tout le "code"
DB_Repliques.lua            17 178 948 o   ← généré par le pipeline
```

Il n'y a aucun code à sauver, sinon un `.toc` de 222 octets. **Je le prends** — il est
gratuit, et il porte l'ordre de chargement, qui lui n'est écrit nulle part ailleurs.

**Et j'ai regardé les voisins, parce que le risque est le même.** Il y a **cinq** addons
maison, pas deux :

| addon | code | déjà sauvegardé ? |
|---|---|---|
| `AscensionFR` | 613 Ko, 26 fichiers | ❌ **nulle part** |
| `AscensionFR_Repliques` | 222 o (`.toc`) | ❌ **nulle part** |
| `AscensionFR-Confort` | 174 Ko | ✅ dépôt + distant GitHub |
| `AscensionFR-Equipement` | 96 Ko | ✅ dépôt + distant GitHub |
| `AscensionFR-Peche` | 28 Ko | ✅ dépôt + distant GitHub |

Les trois derniers sont des dépôts à part entière avec un distant. **Ils ne rentrent pas ici**
— les dupliquer créerait exactement la divergence qu'on cherche à éviter. Je les exclus
**nommément, avec un commentaire disant où ils vivent** : une exclusion documentée, pas un
trou silencieux.

**Conséquence sur la racine du dépôt.** Pour couvrir `AscensionFR` *et* le `.toc` de
`Repliques`, je enracine le dépôt sur `Interface\AddOns\` plutôt que sur `AscensionFR\`. Ça
apporte un bénéfice que je n'aurais pas eu autrement : le `.gitignore` exclut par **nature**
(les bases, les dossiers `Blizzard_*`, `DragonUI` qui est un addon tiers de PentSec/NeticSoul,
les trois dépôts voisins). Donc **un sixième addon maison créé demain apparaîtra en
« non suivi »** au lieu de rester silencieusement sans protection. C'est le motif de
`verifier_greffes.py` : une liste qui se confronte à la réalité au lieu d'une liste qu'on croit
à jour.

Le `.gitignore` est écrit **avant** `git add`, comme demandé.

---

### BLOC D — le dépôt est créé, et il est vide de tout distant

```
D:\AscensionFR\depot_addon.git\      ← l'historique, hors du jeu
…\Interface\AddOns\.git              ← "gitdir: D:/AscensionFR/depot_addon.git"
```

Commit `92f4d6a`.

| | |
|---|---|
| **fichiers suivis** | **29** |
| **poids du dépôt** | **336 Ko** |
| poids de ce qui est resté dehors | 212 Mo |
| distants | **aucun** |

Les 29 : `Core.lua`, `AscensionFR.toc`, `Bindings.xml`, les 23 modules, le `.toc` de
`Repliques`, plus le `.gitignore` et le `.gitattributes`.

**Contre-épreuve avant d'ajouter quoi que ce soit.** J'ai demandé à git, fichier par fichier,
s'il ignorait bien les gros morceaux — et lequel de ses motifs le disait :

```
✅ IGNORÉ  AscensionFR/DB/DB_Objets.lua              (.gitignore:18 DB/)
✅ IGNORÉ  AscensionFR/DB_sauvegarde_build           (.gitignore:19)
✅ IGNORÉ  AscensionFR_Repliques/DB_Repliques.lua    (.gitignore:20)
✅ IGNORÉ  DragonUI/DragonUI.toc                     (.gitignore:29)
✅ IGNORÉ  Blizzard_ArenaUI                          (.gitignore:24 Blizzard_*/)
✅ IGNORÉ  AscensionFR-Peche/Coeur.lua               (.gitignore:41)
```

**Et j'ai éprouvé la restauration, parce qu'une sauvegarde non restaurée n'est qu'une
supposition.** Cloné à blanc ailleurs sur le disque :

- 27 fichiers de code ressortent ;
- **0 différence de contenu** avec l'original ;
- les 24 `.lua` compilent en **Lua 5.1**, la version du client.

> Un faux rouge que j'ai produit moi-même, et qui vaut la peine d'être noté : mon premier
> contrôle utilisait le lupa **par défaut**, qui est en Lua **5.5**. Il refusait `Epreuves.lua`
> et `Sorts.lua` — parce qu'en 5.5 la variable d'une boucle `for` est constante, alors qu'en
> 5.1 on peut la réassigner. Le code est bon ; **c'était mon instrument qui était mal réglé.**
> Le pipeline, lui, fait déjà les choses correctement (`construire_zip_release.py` compile en
> `lupa.lua51`). Je le signale surtout pour le programme 14 : un contributeur qui vérifie son
> travail avec le lupa par défaut se fera crier dessus pour du code parfaitement valide.

**Le dépôt privé de `WorkFlow` n'a pas été touché** : `HEAD` toujours sur `7ec5cbd`, toujours
**0 distant**, et aucun fichier modifié par moi. Ce dépôt-ci est un dépôt **différent**, avec
son propre historique, sa propre identité, et rien en commun.

---

### Ce qu'il reste à faire pour une copie hors de cette machine

Un dépôt local protège d'une mauvaise modification. **Il ne protège pas d'un disque qui
meurt** — ni, ici, d'un lanceur qui réécrit son dossier, puisque le dépôt vit sur le même
disque. **Ce geste reste à Dan, je ne l'ai pas fait.**

Ce qui est déjà en place :

- ✅ **le balayage est propre** — rien dans l'historique qui interdise l'envoi ;
- ✅ **l'historique n'a qu'un commit**, donc rien d'ancien à réécrire ;
- ✅ `gh` est authentifié sur le compte `LePetitDan`, avec la portée `repo` — de quoi créer un
  dépôt privé sans rien installer.

Les deux commandes, **à lancer par Dan quand il le décidera** :

```bash
gh repo create LePetitDan/AscensionFR-Addon --private --description "Code de l'addon AscensionFR (sans les bases)"
```

```bash
git -C "D:/AscensionFR/WOW_Priv/resources/ascension-live/Interface/AddOns" remote add origin https://github.com/LePetitDan/AscensionFR-Addon.git
```

puis `git push -u origin main`. (Le `--separate-git-dir` ne change rien à ces gestes : on
travaille dans le dossier du jeu comme dans n'importe quel dépôt.)

**Trois points de vigilance :**

1. **En privé, pas en public.** Publier le code de l'addon est une décision du programme 14,
   pas un effet de bord de celui-ci.
2. **Mais l'historique qu'on vient de créer est déjà publiable** — le balayage est propre, il
   n'y a qu'un commit, et le Lua de WoW ne peut structurellement pas porter le webhook. Passer
   ce dépôt en public le jour venu ne demandera **aucune réécriture d'historique**. C'est la
   bonne nouvelle du programme 13 pour le programme 14.
3. **Ne pas confondre les trois dépôts** : `WorkFlow\` (privé, porte le webhook, jamais de
   distant), `depot_github\` (public, le Compagnon), et celui-ci (nouveau, sans distant).

---

### 🛑 Terminé — l'état exact

| demandé | fait |
|---|---|
| balayage de secrets, avant tout | ✅ **0 motif**, sur 84 fichiers et 217 Mo réellement lus, instrument éprouvé par leurre |
| recommandation d'emplacement + son coût | ✅ `--separate-git-dir` hors du jeu ; le coût est un chemin absolu qui casse **bruyamment** |
| dépôt créé, `.gitignore` avant le 1er commit, `DB\` exclu | ✅ commit `92f4d6a`, exclusion vérifiée fichier par fichier |
| poids réel et fichiers suivis | ✅ **336 Ko**, **29 fichiers** |
| sort d'`AscensionFR_Repliques` | ✅ pas de code — 17 Mo de base + un `.toc` de 222 o, pris |
| copie hors machine | ✅ prérequis réunis, **commandes listées, non lancées** |

🛑 **Rien poussé. Aucun distant ajouté. `WorkFlow` intact.**

**Deux choses que je n'avais pas prévues et qui méritent ton œil :**

1. **Il y a cinq addons maison, pas deux.** Trois avaient déjà un dépôt et un distant. La
   fragilité était plus étroite que décrite — mais elle portait sur le plus gros morceau.
2. **Le vrai risque n'est pas le patch de contenu**, qui a bien épargné `AddOns\`. C'est que
   le jeu soit installé **dans le `resources\` d'une application Electron auto-mise-à-jour**.
   C'est ça qui a décidé l'emplacement.

