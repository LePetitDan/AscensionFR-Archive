# Demande de code → Claude Code

# 🔍 PROGRAMME 25 — relire la proposition Linux, sans rien fusionner

**Date :** 2026-08-03
**Décision de Dan :** on relit d'abord, on fusionnera après.

🛑 **Ce programme ne fusionne rien, ne pousse rien, ne touche pas à la branche de Tetardtek.**
Tu lis, tu éprouves, tu donnes ton avis. Dan tranchera avec ton rapport devant lui.

---

## Ce qu'il faut avoir en tête avant d'ouvrir le premier fichier

C'est **le code le plus dangereux du projet** : celui qui remplace l'application pendant
qu'elle tourne, sur la machine des joueurs. C'est celui qu'on a réparé au programme 9 après
avoir découvert qu'il pouvait laisser quelqu'un sans rien.

Et en même temps : **ce contributeur a prouvé plus que la plupart.** Il a éprouvé le cycle
complet sur une vraie release, deux fois — une fois avec son binaire, une fois avec celui de
**notre** workflow. Il a trouvé six recouvrements que nous n'avions pas vus, dont trois où il
tranche **en notre faveur**. Il a documenté ses propres erreurs de protocole.

**Relis-le comme du code dangereux, pas comme du code suspect.** Ce n'est pas la même chose,
et confondre les deux est une façon de perdre un contributeur qui vaut de l'or.

**Lis d'abord ses trois commentaires sur la PR #5** — ils nomment exactement où chaque
recouvrement atterrit. **Puis vérifie-les au lieu de les croire.**

---

## 🛑 BLOC A — les six recouvrements, un par un

GitHub affiche « aucun conflit, la fusion peut être automatique ». **C'est vrai et ça ne prouve
rien** : deux de ces six sont précisément celles que git ne sait pas voir.

**Fais une fusion à blanc, dans un clone jetable**, et va lire ce que chacune donne **après**
fusion — pas ce que la PR contient, ce que l'arbre fusionné dirait :

| # | zone | ce qui doit gagner | git le voit ? |
|---|---|---|---|
| 1 | `remplacement_possible` / `peut_remplacer_sur_place` | notre décision, élargie par un `or` | ❌ |
| 2 | `_fenetre` / le grab | **notre reprise bornée** ; `wait_visibility()` doit avoir disparu | ✅ |
| 3 | `_candidats_registre` | **notre `try: import winreg`** | ✅ |
| 4 | `CONFIG_DIR` | le sien, **avec notre repli emprunté** | ✅ |
| 5 | `lancer_jeu` | le sien, par un `or` — sinon notre message devient un mensonge | ❌ |
| 6 | l'entrée de `lancer_remplacement` | il dit l'avoir corrigé en rebasant | ❌ |

**Le n°6 est celui que je veux que tu regardes le plus attentivement**, parce que c'est le seul
que nous n'avons pas trouvé nous-mêmes et que personne n'a vérifié. D'après lui, notre garde
d'entrée — celle écrite pour **mordre** — se serait retrouvée désarmée pour la plateforme
qu'elle protège, et elle teste maintenant `os.name != "nt"`. **Vérifie que c'est bien le cas,
et que sous Windows elle mord toujours.**

Pour chacun : dis-moi **ce que l'arbre fusionné ferait**, pas ce que le commentaire annonce.

---

## 🛑 BLOC B — Windows, la non-régression qui compte

**274 machines.** Il affirme « ton relais Windows n'est pas touché — pas une ligne ».

**Ne le crois pas : mesure-le.** Un `git diff` du chemin Windows entre `main` et l'arbre
fusionné, fonction par fonction. Si une seule ligne du relais a bougé, **je veux le savoir
avant tout le reste.**

Et au-delà du relais :

- l'asset choisi sous Windows est-il **mot pour mot** celui d'avant ?
- le contrôle « ça commence par MZ » est-il **inchangé** ? (Il dit avoir passé `bloc[:2]` à
  `bloc[:4]` pour reconnaître un ELF — vérifie que ça ne change rien au cas Windows.)
- `reference_asset()` et `verifier_telechargement()` rendent-ils la même chose qu'avant, sous
  Windows ?

---

## BLOC C — le banc, et surtout ce qu'il ne teste pas

Son banc est sur le disque : `D:\AscensionFR\4-reference\test-autoupdate-linux.py`.
21 contrôles, 21 verts d'après lui.

**Lance-le** — il est écrit pour Linux, donc via le workflow en mode diagnostic si tu ne peux
pas autrement. Si tu ne peux pas du tout, **dis-le au lieu de faire semblant.**

🛑 **Puis fais la chose qui compte vraiment : relis le banc lui-même.**

Un banc écrit par l'auteur du code est un banc qui peut être complice **sans le vouloir** —
il éprouve ce que son auteur a pensé, pas ce qu'il a oublié. **Qu'est-ce qu'il ne teste pas ?**

Quelques pistes, complète-les :

- que se passe-t-il si le téléchargement est interrompu **au milieu** ?
- si le disque est plein au moment de l'échange ?
- si `plateforme.py` est absent (quelqu'un qui lance les sources sans la PR #4) ?
- le `.ancien` est-il **toujours** créé avant le remplacement, ou seulement dans le chemin
  nominal ?
- que devient un joueur dont la nouvelle version ne démarre pas ? Il a un `.ancien` — **le
  sait-il ?** Quelque chose le lui dit-il ?

---

## BLOC D — la lecture adverse, dite honnêtement

Sans supposer la mauvaise foi, mais sans supposer la bonne non plus :

- quoi que ce soit touche-t-il **au webhook, au secret, ou au chemin de publication** ?
- une **dépendance** est-elle ajoutée ? Il affirme « uniquement la bibliothèque standard » et
  s'appuie sur la taille identique du binaire — **vérifie autrement que par la taille** ;
- quelque chose appelle-t-il le réseau ailleurs que là où on l'attend ?
- le code s'exécute-t-il **hors application figée** ? Il dit ne rien tenter sur les sources
  (`sys.executable` désignerait l'interpréteur) — c'est le genre de garde qu'on vérifie.

---

## BLOC E — ton avis, et ce que tu ne peux pas savoir

- **fusionner tel quel, ou demander quelque chose ?** S'il faut demander, écris-le en une
  phrase que Dan puisse recopier ;
- **la #4 vient avec la #5** (elle s'empile dessus). Est-ce que ça change quelque chose à ton
  avis ?
- **ce qu'il reste non prouvé**, et il le dit lui-même : le cas où `/tmp` et le dossier du
  joueur sont sur la **même** partition, les autres bureaux, les distributions plus anciennes.
  Ajoute ce que tu vois d'autre ;
- ⚠️ **la réserve sur le presse-papiers** : sous Linux, « Copier mon rapport » — notre
  nouveauté de la 3.4.2 — dépend d'un outil du bureau. Sur GNOME, qui n'en a pas par défaut,
  un joueur qui copie puis ferme pourrait ne rien retrouver. **Ne le corrige pas ici**, dis-moi
  seulement ce que tu ferais et ce que ça coûte.

---

**« Terminé » veut dire :**

> - Les **six** recouvrements vérifiés **sur l'arbre fusionné à blanc**, pas sur les
>   commentaires — et le n°6 en particulier.
> - **Windows mesuré**, pas cru : le relais, l'asset, le contrôle MZ.
> - Le banc lancé (ou l'aveu franc que tu ne peux pas), **et ce qu'il ne teste pas**.
> - La lecture adverse : dépendances, réseau, secret, exécution hors figé.
> - Ton avis : fusionner, ou demander quoi.
> - Ce qui reste non prouvé, y compris ce qu'il n'a pas listé.
> - Ce qui a résisté, et ce que tu as failli casser.

🛑 **Rien de fusionné, rien de poussé, aucun tag, aucune release. Sa branche n'est pas touchée.**

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Puis renommer en `_FAIT.md`.)

---

# 🛑 BLOC A — les six recouvrements, sur l'arbre fusionné

## La fusion à blanc

Clone jetable, `pr5` et `pr4` récupérées par `pull/N/head`, puis
`git merge --no-commit --no-ff pr5` dans `main`.

```
Automatic merge went well; stopped before committing as requested
fichiers en conflit : AUCUN
7 fichiers, +593 / −49   (dont plateforme.py, 388 lignes, qui vient de la #4)
```

**Aucun conflit du tout** — pas même les deux que la table annonce comme visibles par git.
La raison est simple et elle est à son crédit : **il a déjà retiré ses versions** de `_fenetre`
et `_candidats_registre` en rebasant. Ce que la table décrit était vrai de son état d'avant ;
ce n'est plus l'état d'aujourd'hui. J'ai donc lu l'arbre, pas les commentaires.

## Les six, un par un — ce que l'arbre fusionné FERAIT

| # | verdict | ce que j'ai lu dans l'arbre fusionné |
|---|---|---|
| 1 | ✅ conforme | `return os.name == "nt" or plateforme.peut_remplacer_sur_place()` |
| 2 | ✅ conforme | `prendre_la_main(reste=20)` + reprise à 50 ms — **`wait_visibility` a disparu du fichier** (0 occurrence) |
| 3 | ✅ conforme | `try: import winreg / except ImportError: return []` — notre version, mot pour mot |
| 4 | ✅ conforme | `CONFIG_DIR = plateforme.dossier_config("AscensionFR")`, et notre repli `"~"` repris chez lui |
| 5 | ✅ conforme | `if not hasattr(os, "startfile") and not plateforme.EST_LINUX:` |
| 6 | ✅ **corrigé, et bien** | `if os.name != "nt": raise RuntimeError(…)` |

### Le n°6 en détail — celui que personne n'avait vérifié

C'est le seul qui aurait pu faire un dégât réel, et il est **traité correctement**.

`main` gardait l'entrée du relais avec `if not remplacement_possible()`. C'était juste tant
que cette fonction voulait dire « on est sous Windows ». Après la fusion elle veut dire
« l'auto-mise à jour est praticable », **et elle répond oui sous Linux**. Le garde serait donc
devenu inerte *pour la plateforme même qu'il protège* : un chemin d'appel imprévu aurait pu
écrire un `.bat` et le passer à `cmd` sur une machine Linux.

L'arbre fusionné teste maintenant **`os.name != "nt"` en direct**, avec un commentaire qui
explique exactement ce piège. C'est le bon choix : un garde-fou doit tester **le fait**, pas
une décision qui peut changer de sens sous lui.

**Et je ne l'ai pas cru sur parole — je l'ai fait mordre :**

```
sous Linux figé, remplacement_possible() répond OUI          OK
…et le relais .bat REFUSE quand même                          OK
```

C'est-à-dire : j'ai mis le code dans l'état exact où l'ancien garde aurait été désarmé, et le
nouveau tient.

### Ce que la table du programme annonçait, et ce que j'ai trouvé

Deux écarts, tous deux **en sa faveur** :

- les n°2 et n°3 sont donnés « ✅ git le voit ». **Git ne voit plus rien** : il a fait le
  ménage lui-même. Il n'y a plus de choix à faire à la fusion ;
- le n°1 est donné « notre décision, élargie par un `or` » — c'est exactement ce qui est écrit.

## Le doublon de nom, qui était le vrai danger

Le point de départ de tout ceci — `remplacement_possible()` des deux côtés, dans deux fichiers,
répondant **l'inverse** sous Linux — **n'existe plus** : sa fonction s'appelle
`peut_remplacer_sur_place()`. J'ai vérifié qu'il n'y a **aucune** autre définition
`remplacement_possible` ailleurs dans l'arbre fusionné.

La séparation qu'il propose est juste, et elle vaut d'être notée : `compagnon.remplacement_possible()`
est une **décision** (doit-on proposer ?), `plateforme.peut_remplacer_sur_place()` est une
**capacité** (le système sait-il ?). La décision interroge la capacité. C'est la bonne
direction de dépendance.

---

# 🛑 BLOC B — Windows, mesuré et pas cru

## ⚠️ Il dit « pas une ligne ». C'est faux — et c'est une bonne nouvelle

Le corps de la PR affirme : *« `lancer_remplacement` : intouché »*. **Mesuré fonction par
fonction, il a changé.** La différence exacte, et rien d'autre :

```diff
-    if not remplacement_possible():
+    if os.name != "nt":
         raise RuntimeError(
-            "l'auto-mise à jour de l'application n'existe que sous Windows "
-            "(le relais est un .bat, et l'asset publié est un .exe)")
+            "ce relais de remplacement n'existe que sous Windows (c'est un "
+            ".bat lancé par cmd) — sous Linux, l'échange passe par
+            plateforme.remplacer_application")
```

**C'est le n°6, et c'était nécessaire.** L'affirmation du corps de la PR est simplement
**périmée** : elle date d'avant le rebase, et le commentaire n°1 dit lui-même l'avoir corrigé.
Je le signale parce que c'est exactement le genre d'écart entre le texte et le code qui
mérite d'être nommé — pas parce que c'est suspect.

## Le corps du relais, lui, est intact — prouvé, pas lu

Le `.bat` est *généré* : le comparer par le source ne suffit pas. Je l'ai donc **fait produire
par les deux versions** avec les mêmes arguments, `subprocess.Popen` remplacé par un mouchard :

```
le .bat du relais est IDENTIQUE                1633 octets
même commande                                   ['cmd', '/c']
même drapeau CREATE_NO_WINDOW                   0x08000000
même environnement passé à cmd                  AFR_CIBLE, AFR_NOUVEAU, AFR_ANCIEN, AFR_JOURNAL
```

Le « mettre de côté plutôt que supprimer », le retour arrière, l'attente-nettoyage, les
chemins par l'environnement : **rien n'a bougé d'un octet.**

## Le reste du chemin Windows

Banc écrit pour ça (`banc_windows_pr5.py`) : les deux arbres chargés **côte à côte dans le
même interpréteur**, sous deux noms de modules, et on compare ce qu'ils **rendent**.
**33 affirmations, toutes vertes.**

| ce qui a été mesuré | résultat |
|---|---|
| `ASSET_APPLICATION` sous Windows | `AscensionFR_Compagnon.exe` — **mot pour mot** `EXE_ATTENDU` |
| `SUFFIXE_APPLICATION` | `.exe` |
| contrôle MZ : exe / HTML / vide / 1 octet | **même verdict qu'avant sur les quatre** |
| `bloc[:2]` → `bloc[:4]` | `debut[:2]` identique pour un bloc de 1, 2, 3, 4 et 100 octets |
| `reference_asset` | **pas une ligne de changée**, et le nom demandé est le même |
| `remplacement_possible()` | `True` avant et après (court-circuit sur `os.name`) |
| `CONFIG_DIR` | identique au caractère près |
| `_pistes_launcher` | même résultat ; la passe Linux rend `[]` **et ne fait aucun accès disque** |
| `plateforme.lancer()` | passe par `os.startfile`, rend `True` ; rend `False` sur `OSError` — équivalent exact de l'ancien `except OSError: pass` |
| `_fenetre`, `_candidats_registre`, `mettre_a_jour_appli`, `_maj_appli_proposable`, `relancer_admin`, `copier_rapport`, `montrer_plantage`, `jeu_ouvert`, `chercher_jeu`, `diagnostic`, `_est_admin`, `installer_zip` | **identiques, caractère pour caractère** |

Sur le point 8, je suis allé plus loin que « ça rend `[]` » : c'est la leçon de mon audit de la
PR #4, où cette même assertion **ne mordait pas** (elle rendait `[]` parce que `~/Games`
n'existe pas *sur cette machine*, pas parce qu'une garde l'empêchait). J'ai donc **compté les
accès disque** : **0**. Inerte par conception, pas vide par chance.

## ⚠️ Un faux vert dans MON banc, attrapé de justesse

Mon premier passage affichait quatre `OK` sur le contrôle MZ :

```
un vrai exe (MZ)   avant=TypeError   après=TypeError   OK
```

Les deux côtés levaient `TypeError`… parce que **j'appelais la fonction avec le mauvais nombre
d'arguments**. L'égalité était parfaite et ne mesurait rien. Corrigé, et le banc **refuse
désormais un `TypeError` des deux côtés** comme preuve d'équivalence.

---

# BLOC C — le banc, et surtout ce qu'il ne teste pas

## Je l'ai lancé. Il ne passe pas — et c'est instructif

```
A. Non-régression Windows (plateforme simulée)
  ✅ l'asset reste AscensionFR_Compagnon.exe
  ✅ le suffixe reste .exe
AttributeError: module 'plateforme' has no attribute 'remplacement_possible'
```

**Le banc s'arrête au troisième contrôle sur vingt-et-un.** Il appelle
`plateforme.remplacement_possible()` — le nom **qu'il a lui-même supprimé** au commit
`c01b5d0`, en le renommant `peut_remplacer_sur_place()` pour lever le doublon. Le fichier
posé dans `4-reference/` date d'**avant** ce renommage.

Ce n'est pas un défaut du code : c'est que **« 21 contrôles, 21 verts » décrit un état de la
PR qui n'existe plus.** Personne n'a rejoué le banc après le rebase — et c'est précisément le
genre de dérive qu'un banc est censé empêcher.

*(Détail au passage : il meurt aussi sous Windows sur le `✅` en cp1252 — le piège maison de
`piege-console-cp1252`. Contournable par `PYTHONIOENCODING=utf-8`, mais il faudrait la ligne
`sys.stdout.reconfigure(...)` en tête, comme nos bancs.)*

## Ce que je n'ai PAS pu lancer, dit franchement

**La famille C (le remplacement réel) n'a pas tourné.** Pas de WSL sur cette machine
(`wsl --list` : « le Sous-système Windows pour Linux n'est pas installé »), et la faire tourner
par le workflow demanderait de **pousser une branche** — ce que ce programme interdit.

Ce que j'ai pu faire à la place : lire `plateforme.remplacer_application` et `_relancer` ligne
à ligne, et **mesurer tout le côté Windows** (bloc B). La famille C reste éprouvée par lui
seul — sur une machine, un bureau, une distribution.

## 🛑 Ce que le banc ne teste pas

Un banc écrit par l'auteur éprouve ce qu'il a pensé. Voici ce que j'y cherche et n'y trouve pas.

### Les trous que le programme nommait

| question | réponse |
|---|---|
| téléchargement interrompu au milieu | **partiellement**. Le banc éprouve une *taille annoncée* fausse et une *empreinte* fausse — pas une coupure réelle. Et surtout : voir le trou majeur ci-dessous |
| disque plein pendant l'échange | **non testé**. Le code s'en sort bien à la lecture (`except BaseException: os.remove(provisoire); raise`, l'ancien reste intact), mais rien ne le démontre |
| `plateforme.py` absent | **sans objet après fusion** — la #5 apporte la #4. Mais voir le point « couture » du bloc E : côté **privé**, ce fichier n'existe pas encore |
| le `.ancien` est-il toujours créé avant ? | **oui, et c'est bien fait** : `os.link` (instantané) avant l'unique `os.replace`, avec repli `copy2` si les liens durs sont refusés. Le repli, lui, **n'est jamais exercé** |
| le joueur sait-il qu'il a un `.ancien` ? | **non. Rien ne le lui dit** — voir ci-dessous, c'est le trou que je trouve le plus sérieux |

### Le trou majeur : quand GitHub ne répond pas sur les métadonnées

`_maj_appli_fond` fait `sha, taille = reference_asset(...)`, et `reference_asset` rend
**`(None, None)` sans lever** quand l'API est injoignable — c'est écrit, c'est délibéré
(« on ne bloque pas la mise à jour pour autant »). Or dans `verifier_telechargement`, les
contrôles de taille et d'empreinte sont **conditionnels** :

```python
if taille_attendue and taille != taille_attendue:   ...
if sha256_attendu and empreinte != sha256_attendu:  ...
```

Donc si les métadonnées manquent, **la seule protection restante est le nombre magique**.
Un téléchargement coupé en cours de route commence toujours par `\x7fELF` (ou `MZ`) : il
**passe**. Le joueur remplace son application par un binaire tronqué.

⚠️ **Ce trou est ANTÉRIEUR à la PR** — il existe à l'identique sur le chemin Windows depuis le
programme 9. La PR ne l'aggrave pas ; elle l'**étend à Linux**, où il fait un peu plus mal :
sous Windows le relais relance l'ancien si le neuf ne démarre pas, tandis que sous Linux
`os.execve` d'un ELF tronqué échoue → et là, heureusement, `_relancer` **remet bien
`.ancien` en place**. Le filet joue. Mais on l'aura frôlé pour rien.

### Le trou que je trouve le plus sérieux : le `.ancien` muet

`_relancer` gère bien le cas « la nouvelle version ne se lance pas » : `os.execve` échoue,
`.ancien` est remis, message clair. **Mais il ne gère pas « elle se lance et meurt juste
après »** — bibliothèque manquante, plantage au démarrage, décor absent. Dans ce cas `execve`
a réussi, il n'y a plus personne pour restaurer, et le joueur se retrouve avec :

- une application qui ne démarre plus ;
- un fichier `.ancien` à côté, qui est exactement son salut ;
- **et rien, nulle part, qui lui dise qu'il existe.**

Ce n'est pas propre à la PR : c'est vrai du relais Windows depuis le programme 9. Mais la PR
double la population concernée, et la 3.4.2 vient justement d'apprendre au Hub à parler quand
ça rate. **Une ligne dans la note de version, ou dans le message d'échec, suffirait.**

### Les autres manques, plus petits

- **le câblage n'est pas éprouvé** : le banc appelle `plateforme.remplacer_application`
  directement, jamais `interface_hub._remplacer_appli` — donc l'aiguillage lui-même
  (`if plateforme.peut_remplacer_sur_place()`) n'est couvert que par son essai à la main ;
- **le repli `shutil.copy2`** quand `os.link` est refusé (montages FUSE, `/home` en NFS) :
  documenté, jamais exercé ;
- **l'ancien `.ancien` est supprimé AVANT** que le nouveau soit créé. Si `link` **et** `copy2`
  échouent, le joueur perd aussi le filet de la mise à jour précédente. L'application courante
  reste intacte, donc ce n'est pas grave — mais ce n'est pas gratuit non plus ;
- **le `.neuf` orphelin** : si le processus est tué entre `shutil.move` et `os.replace`, un
  fichier caché de 39 Mo reste à côté du binaire, et **rien ne le nettoie au lancement
  suivant** ;
- **deux mises à jour en même temps** (double-clic sur le lien, deux Hubs ouverts) : non
  testé, et `_remplacer_appli` n'a pas de verrou ;
- **`os.execve(cible, [cible] + sys.argv[1:], env)`** rejoue les arguments : un Hub lancé avec
  `--demo` redémarre en démo après mise à jour. Anecdotique, mais c'est un comportement ;
- **même partition** : le banc ne *saute* que l'assertion EXDEV ; le reste de la famille C
  s'exécuterait bien sur une telle machine. Sa formulation est donc un peu sévère envers
  lui-même — c'est **sa machine** qui ne couvre pas ce cas, pas son banc.

---

# BLOC D — la lecture adverse

Mesurée par l'arbre syntaxique et par le diff, pas par la taille du binaire.

| question | réponse |
|---|---|
| touche-t-il au **webhook / au secret / au chemin de publication** ? | **0 ligne.** Recherche de `WEBHOOK`, `webhook`, `discord`, `token`, `secret`, `API_RELEASE` dans le diff complet de `compagnon/` : aucune occurrence ajoutée ni retirée |
| ajoute-t-il une **dépendance** ? | **non.** Il s'appuie sur la taille identique du binaire ; j'ai vérifié autrement — par les imports. `plateforme.py` importe `glob, json, os, shutil, subprocess, sys` : **six modules, tous de la bibliothèque standard**. Aucun import ajouté dans `compagnon.py` ni `interface_hub.py` |
| **réseau** ailleurs qu'attendu ? | **aucun.** `plateforme.py` ne contient ni `urllib`, ni `socket`, ni `requests`, ni `urlopen`, ni `webbrowser`. Le réseau reste entièrement dans `compagnon.py`, aux endroits d'avant |
| s'exécute-t-il **hors application figée** ? | **non, et c'est gardé deux fois.** `peut_remplacer_sur_place()` = `EST_LINUX and sys.frozen` — mesuré : `False` non figé, `True` figé. Et `remplacer_application` **re-vérifie** en entrée, avec un message qui renvoie à `git pull` |

Ce qui exécute quelque chose, exhaustivement — trois points, tous lus :

| ligne | appel | ce qu'il lance |
|---|---|---|
| 172 | `subprocess.Popen` | `xdg-open`, `faugus-launcher`, `umu-run` ou `wine`, **en liste d'arguments** |
| 210 | `os.startfile` | le chemin, **sous Windows uniquement** — le comportement d'origine, `except OSError` compris |
| 380 | `os.execve` | la cible qu'on vient d'installer, avec l'environnement **nettoyé** des `_PYI*` |

**`shell=True` : zéro occurrence.** Aucune chaîne de commande construite par concaténation.

`requirements.txt` et `lancer-linux.sh` sont nouveaux et ne servent qu'à lancer **depuis les
sources** ; l'ajout au `.gitignore` est `.venv/`. Rien de tout cela n'entre dans l'exe.

`pyflakes` sur l'arbre fusionné : **0 remarque**. Compilation : OK.

---

# BLOC E — mon avis

## Fusionner, oui — et une seule chose à demander

**Le code est bon, et il est meilleur que le mien sur deux points** (le doublon de nom levé
proprement, et le garde d'entrée du relais qu'il a trouvé seul). Les six recouvrements
atterrissent comme annoncé, Windows ne bouge pas d'un octet là où ça compte, il n'y a ni
dépendance, ni réseau, ni secret, ni exécution hors figé.

**La phrase à recopier, s'il faut demander quelque chose :**

> Le banc `test-autoupdate-linux.py` appelle encore `plateforme.remplacement_possible()`, que
> le commit c01b5d0 a renommé — il s'arrête au 3ᵉ contrôle sur 21. Peux-tu le remettre à jour
> et l'ajouter à la PR ? On le prendra volontiers dans le dépôt.

Ce n'est **pas** un blocage : le code ne dépend pas du banc. Mais un banc qui ne passe plus
est un banc mort, et c'est le seul qui couvre la famille C — celle que je ne peux pas éprouver.

## ⚠️ Une couture qui nous concerne, NOUS — à faire avant de reconstruire

`plateforme.py` devient un **sixième fichier source qui construit l'exe**. Or il n'est pas
dans `SOURCES` de `outils/secrets_publication.py`, la liste des cinq fichiers surveillés :

```python
SOURCES = ["compagnon/compagnon.py", "compagnon/compagnon_hub.py",
           "compagnon/interface_hub.py", "compagnon/fabriquer_decor_hub.py",
           "compagnon/AscensionFR_Hub.spec"]
```

Conséquences si on fusionne sans y toucher :

1. le fichier vivra dans le dépôt **public** et **pas dans le privé** — et c'est le privé qui
   construit l'exe. **`import plateforme` échouera à la prochaine construction Windows** ;
2. `synchroniser_depot_public.py` ne le synchronisera pas, et `verifier_arbre_publie.py` ne le
   comparera pas : un fichier qui entre dans l'exe **sans être surveillé**.

*(Le balayage de secrets, lui, lit toutes les extensions : ce point-là reste couvert.)*

C'est trois lignes de travail, mais c'est de notre côté et ça doit être fait **dans le même
geste que la fusion**, sinon la prochaine construction casse.

## La #4 vient avec la #5 — ça ne change pas mon avis, ça le renforce

`git rev-list --count pr5..pr4` = **0** : tous les commits de la #4 sont déjà dans la #5.
Fusionner la #5 fusionne la #4 entière — et la #4, seule, est marquée `CONFLICTING`, donc
c'est de toute façon par là qu'il faut passer.

Ce que ça change concrètement : **tout ce que j'ai mesuré au bloc B portait déjà sur les
deux**. Mon audit de la #4 (programme 15) avait laissé deux réserves ; les deux sont levées ici,
et mesurées cette fois plutôt qu'affirmées :

- `pistes_jeu_linux()` sous Windows : **0 accès disque** — inerte par conception, pas vide par
  chance (c'était exactement l'assertion qui ne mordait pas dans mon banc de l'époque) ;
- le repli d'`APPDATA` : `CONFIG_DIR` identique au caractère près sous Windows.

Une fois fusionnée, la **#4 pourra être fermée comme incluse**.

## Ce qui reste non prouvé

Ce qu'il liste lui-même : `/tmp` et le dossier du joueur sur la **même** partition, les autres
bureaux, les distributions plus anciennes. J'ajoute :

1. **Sa famille C n'a été rejouée par personne d'autre que lui** — et pas par moi, faute de
   Linux. Un seul bureau (KDE/kwin), une seule distribution (Pop!_OS 24.04), un seul
   `glibc` (2.39).
2. **Le banc actuel ne passe plus** : ce qui est « prouvé » l'a été sur l'état d'avant le
   rebase. Les deux états sont probablement équivalents — mais « probablement » n'est pas
   « mesuré ».
3. **Le repli `copy2`** quand les liens durs sont refusés.
4. **Le disque plein**, et le `.neuf` orphelin après un arrêt brutal.
5. **La nouvelle version qui démarre puis meurt** — le seul cas où le filet existe et ne sert
   à personne, faute d'être annoncé.
6. **Le comportement à deux mises à jour simultanées.**
7. **La construction Windows après fusion** : personne n'a encore reconstruit l'exe avec
   `plateforme.py` dans l'arbre. Tant que la couture ci-dessus n'est pas faite, elle échouera.

## ⚠️ La réserve sur le presse-papiers — ce que je ferais, et ce que ça coûte

Il a raison, et il rejoint ce que ma propre contre-épreuve avait sorti au programme 23. Sous
X11 le presse-papiers appartient à l'**application vivante** : chez lui Klipper le rattrape,
sur GNOME nu personne ne le fait.

**Ce que je ferais, par ordre de coût croissant :**

1. **Rien dans le code, une ligne dans le message** (~10 minutes). Après une copie réussie sous
   Linux : « Rapport copié — colle-le **tout de suite**, avant de fermer le Hub. » Honnête,
   nul risque, et ça couvre 90 % du désagrément.
2. **Le contrôle qu'il propose** (~30 minutes) : un `clipboard_get()` juste après le
   `clipboard_append` pour vérifier que la sélection a bien été prise, et n'afficher « copié »
   que dans ce cas. Coût : une lecture de sélection en plus, et un cas de plus à éprouver —
   mais **sans vrai bureau Linux, je ne peux pas l'éprouver**, seulement le lire.
3. **Écrire aussi le rapport dans un fichier** (~1 heure) : `AscensionFR_rapport.txt` à côté du
   programme, et le message donne le chemin — exactement comme le journal d'incident de la
   3.4.2. Ça règle le problème pour de bon, sur les deux systèmes, et ça réutilise
   `dossier_journal()` qui existe déjà. **C'est ce que je recommanderais**, mais c'est une
   décision d'interface, donc la tienne.

**Ce que je ne ferais pas** : un gestionnaire de presse-papiers maison, ou garder le Hub ouvert
de force. Les deux inventent un comportement pour contourner le système.

---

# Ce qui a résisté, et ce que j'ai failli casser

## Ce qui a résisté

- **Le banc de Tetardtek ne passe plus**, et ça ne se voit ni dans la PR ni dans ses trois
  commentaires — tous écrits, très soigneusement, autour d'un état antérieur au renommage
  qu'il a lui-même fait.
- **Git ne signale plus aucun conflit**, alors que la table du programme en annonce deux
  visibles. Rien ne clochait : il avait déjà fait le ménage. Mais si j'avais fait confiance à
  la table, j'aurais cherché des conflits inexistants et conclu que la fusion était cassée.
- **Pas de Linux, pas de WSL, et le workflow demande un push.** La famille C reste non rejouée.

## Ce que j'ai failli casser

- **Un faux vert dans mon propre banc, et il était parfait.** Le contrôle MZ affichait
  `avant=TypeError après=TypeError → OK` sur les quatre cas : j'appelais la fonction avec un
  argument de trop, les deux côtés levaient donc la même erreur, et l'égalité était vraie.
  **J'aurais annoncé « le contrôle de forme est inchangé » sans avoir jamais appelé le
  contrôle de forme.** Le banc refuse désormais un `TypeError` des deux côtés comme preuve.
- **Comparer un chemin de fichier temporaire.** Ma première assertion sur le relais comparait
  les arguments passés à `cmd` — dont le nom du `.bat`, que `mkstemp` tire au hasard. Rouge
  pour une différence qui n'en est pas une : le genre de faux rouge qui fait désactiver un
  garde-fou.
- **Conclure « le relais n'a pas bougé » sur le source.** Le `.bat` est *généré* : lire la
  fonction ne dit rien de ce qu'elle produit. Il a fallu la faire tourner des deux côtés et
  comparer les 1633 octets.
- **Croire « pas une ligne ».** Le corps de la PR l'affirme du relais ; c'est faux depuis son
  propre rebase. Si je ne l'avais pas mesuré, j'aurais validé une affirmation périmée sur
  **le code le plus dangereux du projet**.

🛑 **Rien n'a été fusionné, rien poussé, aucun tag, aucune release. Sa branche n'a pas été
touchée** — tout s'est passé dans un clone jetable.


---

# « Terminé », point par point

| ce que tu demandais | fait ? | où |
|---|---|---|
| les **six** recouvrements vérifiés **sur l'arbre fusionné à blanc** | ✅ | bloc A — les six conformes, lus dans l'arbre et non dans les commentaires |
| le n°6 en particulier | ✅ | garde passé à `os.name != "nt"`, **et fait mordre** : j'ai mis le code dans l'état où l'ancien garde aurait été désarmé, le nouveau tient |
| **Windows mesuré** : le relais, l'asset, le contrôle MZ | ✅ | bloc B — 33 affirmations, le `.bat` **identique à l'octet** (1633), 12 fonctions inchangées caractère pour caractère |
| le banc lancé, **ou l'aveu franc** | ⚠️ | **lancé, il ne passe pas** (3ᵉ contrôle sur 21). Famille C **non rejouée** : pas de Linux, pas de WSL, et le workflow demanderait un push |
| ce que le banc ne teste pas | ✅ | bloc C — 5 réponses aux pistes du programme + 6 manques que j'ajoute, dont **le trou des métadonnées absentes** |
| lecture adverse : dépendances, réseau, secret, hors figé | ✅ | bloc D — 0 dépendance (par l'AST), 0 réseau, **0 ligne** touchant le secret, `shell=True` nulle part |
| mon avis : fusionner, ou demander quoi | ✅ | bloc E — **fusionner**, une phrase à recopier pour le banc, et **une couture de notre côté** |
| ce qui reste non prouvé | ✅ | bloc E — les 3 qu'il liste + 7 que j'ajoute |
| ce qui a résisté, ce que j'ai failli casser | ✅ | fin du bloc E |

🛑 **Rien fusionné, rien poussé, aucun tag, aucune release.** Vérifié après coup : le dépôt
public est sur `185cc13`, 0 fichier en attente, la branche de Tetardtek n'existe même pas en
local — tout s'est passé dans un clone jetable. **PR #5 : OPEN, MERGEABLE**, intacte.
