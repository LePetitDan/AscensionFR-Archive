# Demande de code → Claude Code

# 🐧 PROGRAMME 15 — la PR #4 (support Linux) : mesurer avant de décider

**Date :** 2026-08-01
**Origine :** https://github.com/LePetitDan/AscensionFR/pull/4 — auteur : Tetardtek, 31/07.

Dan veut l'intégrer **maintenant**, quitte à reporter la 3.4.1. Il a raison de pousser : j'ai
annoncé des conflits **sans les mesurer**, en confondant « les mêmes fichiers » et « le même
code ». Ce programme mesure ce que j'ai supposé.

🛑 **Ne fusionne rien, ne porte rien.** Tu mesures, tu audites, tu chiffres. La décision
d'intégrer vient après, avec les chiffres.

---

## BLOC A — le conflit réel, fonction par fonction

La PR touche `compagnon.py` (l. 40, 117, 297-300) et `interface_hub.py` (l. 44, 796-811). Le
programme 9 a réécrit `reference_asset`, `telecharger_fichier`, `lancer_remplacement`, `travail`,
l'en-tête, et `_maj_appli_fond`. **À première vue ça ne se recouvre presque pas** — mais c'est
justement ce qu'il faut vérifier au lieu de le croire.

Récupère la branche de la PR, et donne-moi :

- **le recouvrement exact** : quelles lignes du programme 9 et de la PR se disputent le même
  endroit ? Compte-les.
- **ce que `git` dit vraiment** : combien de conflits réels sur une fusion à blanc ?
- **le temps que ça demande**, honnêtement. Une heure, une journée ? Dan a accepté le travail,
  pas un chèque en blanc.

---

## 🛑 BLOC B — `plateforme.py`, ligne à ligne

218 lignes de code neuf qui partiront dans **un exécutable non signé qui se met à jour tout seul
sur 274 machines**. Ce n'est pas une revue de style, c'est une revue de chaîne d'approvisionnement.

Lis **chaque ligne**. Je veux, nommément :

- tout appel réseau — il ne devrait y en avoir **aucun** ;
- tout `subprocess`, `exec`, `eval`, `os.system` : quoi, avec quels arguments, et **d'où vient
  chaque argument**. Un chemin lu dans un fichier de configuration tiers et passé à un
  lancement de processus, c'est le motif à regarder deux fois ;
- toute lecture hors du dossier de l'application — la PR lit
  `~/.config/faugus-launcher/games.json`, dis-moi ce qu'elle en fait exactement ;
- tout ce qui s'exécute **sous Windows**. En théorie `plateforme.py` est inerte hors Linux :
  vérifie-le, ne le suppose pas.

**Si quelque chose te gêne, dis-le sans le corriger.** Ce n'est pas notre code : on décide avec
l'auteur, on ne le réécrit pas dans son dos.

---

## 🛑 BLOC C — prouver que Windows ne bouge pas. C'est le cœur.

Le danger n'est pas que Linux marche mal. **C'est que Windows casse pour 274 personnes à cause
d'un remaniement fait pour Linux.**

Trois points, et je veux une **preuve**, pas une lecture :

| ce qui change | ce que je veux prouvé |
|---|---|
| `CONFIG_DIR` → `plateforme.dossier_config("AscensionFR")` | que le chemin rendu est **exactement** `%APPDATA%\AscensionFR`, caractère pour caractère, y compris quand `APPDATA` est absent (l'ancien code se rabattait sur `"."`) |
| `os.startfile()` → `plateforme.lancer()` | que sous Windows **le même appel** est fait, avec le même argument, et que les erreurs se comportent pareil |
| `_pistes_launcher()` + `pistes_jeu_linux()` | que sous Windows la nouvelle piste rend **une liste vide** et ne change ni l'ordre ni le résultat de la détection |

**Écris un banc qui mord** : il doit passer au rouge si l'un de ces trois chemins dévie. Éprouve-le
en cassant exprès, comme tu l'as fait pour `BarresDeVie` et `DetecterFenetres`. Un banc qu'on n'a
pas vu échouer ne prouve rien.

**Le cas `APPDATA` absent m'intéresse particulièrement** : c'est le genre de repli qu'on récrit
sans y penser, et qui ne se voit que chez le joueur dont l'environnement est bizarre.

---

## BLOC D — ce qu'on ne peut PAS éprouver

Ni toi ni moi ne pouvons lancer le jeu sous Proton. **Dis clairement ce qui partirait sans avoir
été essayé par nous**, et ce qui, dans ce code, ne peut être validé que par un joueur Linux réel.

C'est une information pour Dan, pas un reproche à l'auteur : il faut juste qu'on sache ce qu'on
signe. Et propose une manière de le faire éprouver par Tetardtek lui-même avant publication.

---

## BLOC E — le verdict

À la fin, dis-moi :

- **intégrable maintenant, oui ou non**, et à quel prix en travail ;
- si oui, **dans quel ordre** : avant la 3.4.1, ou juste après en 3.4.2 ;
- ce que ça oblige à refaire — la 3.4.1 est **déjà construite et vérifiée** (empreinte
  `a63c717b…`), l'intégrer veut dire reconstruire et repasser toute la barrière ;
- **ce que tu ferais à la place de Dan**, franchement.

---

**« Terminé » veut dire :**

> - Le nombre exact de conflits réels, et le temps que ça demande.
> - L'audit ligne à ligne de `plateforme.py`, avec ce qui te gêne s'il y a lieu.
> - **Le banc qui prouve que Windows ne bouge pas** — et que tu as vu échouer.
> - Ce qui partirait sans avoir été éprouvé par nous.
> - Ton verdict, et ce que tu ferais.

🛑 **Rien de fusionné, rien de porté, rien de reconstruit. Aucune modification du travail de
Tetardtek.**

---
## Réponse de Claude Code

### En deux lignes

**Tu avais raison de pousser : il n'y a aucun conflit.** Zéro. Ni ligne
disputée, ni conflit git — mesuré, pas supposé.

Le code est propre : **aucun appel réseau, aucune écriture, un seul
`subprocess` et il est inatteignable sous Windows** — prouvé. Une seule chose
change côté Windows, elle est cernée, et c'est à toi de trancher.

---

## BLOC A — le conflit réel : il n'y en a pas

### Ce que j'ai fait

Cloné le dépôt public dans un bac à sable, appliqué **ce que le geste 1
écrirait** (les sources privées neutralisées = l'état « programme 9 publié »),
puis fusionné la PR par-dessus. C'est la situation exacte d'après-synchronisation.

### Les chiffres

| | `compagnon.py` | `interface_hub.py` |
|---|---|---|
| zones touchées par le **programme 9** | 15 | 3 |
| zones touchées par la **PR** | 3 | 5 |
| **lignes disputées** | **0** | **0** |
| distance la plus courte entre les deux | **17 lignes** | **516 lignes** |

**Ce que `git` dit :**

```
Auto-merging compagnon/compagnon.py
Auto-merging compagnon/interface_hub.py
Automatic merge went well; stopped before committing as requested
```

**Zéro conflit.** Et pas seulement « ça compile » : j'ai vérifié que le résultat
est sémantiquement juste — les 5 apports de la PR sont présents *et* les 4
fonctions du programme 9 (`reference_asset`, `telecharger_fichier`,
`lancer_remplacement`, `_maj_appli_fond`) sont intactes. `pyflakes` propre
(les 2 avertissements restants sont dans `parser_wdb.py`, préexistants).

**Pourquoi ça ne se recouvre pas.** La PR touche l'en-tête (imports), la
définition de `CONFIG_DIR`, et le début de `_pistes_launcher`. Le programme 9
touche le téléchargement, le relais de mise à jour et le travail de fond. Ce
sont deux régions différentes du fichier.

### Le temps que ça demande, honnêtement

| | |
|---|---|
| la fusion elle-même | **quelques minutes** — git la fait seul |
| l'audit du code tiers | **fait, ici** |
| le banc de non-régression Windows | **fait, ici** |
| reconstruire l'exe + repasser la barrière | ~15 minutes de machine |
| **vérifier que l'exe démarre** (voir plus bas) | 5 minutes, à la main |
| l'épreuve Linux par un joueur réel | **hors de notre portée** — jours |

**Ma part est faite.** Ce qui reste, c'est une reconstruction et une épreuve
Linux qu'aucun de nous deux ne peut faire.

---

## 🛑 BLOC B — `plateforme.py`, ligne à ligne

218 lignes, lues en entier, puis vérifiées mécaniquement.

### Réseau : aucun

Aucun `urllib`, `requests`, `socket`, `http`, `urlopen`, `ftplib`, `smtplib`.
**Zéro.** Les imports sont : `glob`, `json`, `os`, `subprocess`, `sys`, et
`shutil.which` (import différé). **Bibliothèque standard uniquement.**

### Écriture : aucune

Pas un `open(..., "w")`, pas un `makedirs`, pas un `remove`, pas un `shutil.*`
d'écriture. **Le module est strictement en lecture seule.**

### Exécution : un seul point

```python
subprocess.Popen(cmd, env=env, stdout=DEVNULL, stderr=DEVNULL)   # ligne 162
```

**Pas de `shell=True`** — les arguments passent en liste, aucune interprétation
par un shell. C'est le point le plus important de tout l'audit.

Les quatre appels, et d'où vient chaque argument :

| commande | origine de l'argument |
|---|---|
| `["xdg-open", chemin]` | `chemin` vient de l'appelant, testé par `os.path.exists` |
| `[faugus]` | `shutil.which("faugus-launcher")` — résolution par le `PATH`, **lancé sans argument** |
| `[umu, chemin]` + `WINEPREFIX` | `umu` est un chemin **écrit en dur** (`~/.local/share/faugus-launcher/umu-run`), testé `isfile` |
| `[wine, chemin]` | `shutil.which("wine")` |

### Le motif à regarder deux fois — je l'ai suivi jusqu'au bout

Tu as raison de le nommer : **un chemin lu dans un fichier de configuration
tiers peut-il finir dans un lancement de processus ?**

La chaîne complète :

```
~/.config/faugus-launcher/games.json
   → jeu["path"] / jeu["prefix"]          (filtrés : « ascension » ou « wow »)
   → pistes candidates
   → compagnon.chercher_jeu → racine_jeu(...)      ← LA BARRIÈRE
   → self.jeu
   → os.path.join(self.jeu, "Ascension.exe")
   → plateforme.lancer(...) → Popen([wine, exe])
```

**Trois choses limitent ça sérieusement :**

1. `racine_jeu` exige un vrai dossier `Interface/` **et** (`Data/` ou un fichier
   marqueur de racine). Un chemin arbitraire ne passe pas.
2. Ce qui est lancé n'est **pas** le chemin du JSON : c'est ce chemin **plus un
   nom de fichier fixe** (`Ascension.exe` / `Ascension Launcher.exe`).
3. Aucun shell, donc aucune injection de commande possible via le chemin.

**Mon appréciation :** pour en abuser, il faudrait déjà pouvoir écrire dans
`~/.config` de la victime **et** y planter un faux arbre de jeu complet.
Quelqu'un qui a cet accès peut faire bien pire directement (modifier
`~/.bashrc`, par exemple). **Ce n'est pas une surface d'attaque nouvelle
significative** — mais c'est réel, et tu avais raison de demander à le voir.

Même raisonnement pour `which("faugus-launcher")` et `which("wine")` : qui
contrôle votre `PATH` vous contrôle déjà.

### Lectures hors du dossier de l'application

| quoi | ce qu'il en fait |
|---|---|
| `~/.config/faugus-launcher/games.json` | lu, parsé en JSON, **4 clés utilisées** (`gameid`, `title`, `path`, `prefix`), filtré sur « ascension »/« wow ». Erreurs avalées (`OSError`, `ValueError`) |
| 8 racines de prefixes en dur (`~/Games`, `~/.steam/...`, Bottles, Heroic…) | `listdir` **borné à 300 entrées**, puis `glob` jusqu'à 4 niveaux pour `ascension-live` |

Tout en lecture seule, tout sous le dossier personnel, tout borné.

### Ce qui s'exécute sous Windows : rien — et c'est prouvé

Voir le BLOC C. Le résumé : `pistes_jeu_linux()` et `prefixe_de()` sortent sur
leur garde **sans toucher un seul fichier** (0 accès disque, compté), et
`lancer()` sort sur `os.startfile` **sans jamais atteindre le `subprocess`**
(0 processus lancé, compté).

### Ce qui me gêne — je le dis, je ne corrige rien

**1. Le `.spec` n'est pas mis à jour.** `hiddenimports = ['parser_wdb']` ;
`plateforme` n'y est pas. **Si le module n'était pas embarqué, le Compagnon ne
démarrerait pas du tout** — l'import est au niveau du module.

J'ai vérifié le mécanisme plutôt que de spéculer : dans le paquet de la 3.4.1,
`compagnon.py`, `interface_hub.py` et `parser_wdb.py` sont tous présents,
résolus **automatiquement comme voisins du script d'entrée**. `plateforme.py`
le sera par le même chemin. *(`parser_wdb` est dans `hiddenimports` pour une
autre raison : il vit dans `../outils`.)*

**Donc ça devrait aller — mais « devrait » ne suffit pas quand le coût de
l'erreur est « l'application ne démarre pas ».** C'est le premier point à
vérifier après reconstruction, et c'est une ligne de commande :

```bash
python -c "import io,re;print('plateforme' in io.open(r'compagnon\build\AscensionFR_Hub\Analysis-00.toc',encoding='utf-8').read())"
```

**2. `lancer-linux.sh` démarre la MAUVAISE interface.** Le script fait
`exec .venv/bin/python compagnon.py` — or `compagnon.py` lance l'ancien
Compagnon v2, tandis que l'exe Windows est construit depuis `compagnon_hub.py`
et lance le **Hub v3**.

Conséquence directe : **la partie la plus complexe de `plateforme.py` — tout le
bloc `lancer()` / `_essayer()` / umu / wine, c'est-à-dire le seul `subprocess`
— n'est jamais atteinte** par le chemin que la PR documente. Le bouton
« lancer le jeu » vit dans `interface_hub.py`, que `lancer-linux.sh` ne démarre
pas.

Ça réduit le risque réel, mais ça veut dire que les joueurs Linux auraient une
interface différente des joueurs Windows. **Question pour Tetardtek, pas
correction de ma part.**

**3. `requirements.txt` n'épingle rien** (`customtkinter>=5.2`, etc.) : chaque
installation Linux tire la dernière version disponible ce jour-là. Sans effet
sur l'exe Windows, qui est figé. C'est l'usage courant pour un script lancé
chez soi — je le signale par honnêteté, pas par inquiétude.

**4. `_essayer` avale toutes les exceptions** (`except Exception: return False`).
Sous Windows ce chemin est inatteignable ; sous Linux, une panne est donc
silencieuse. Cohérent avec le but affiché du module (« ne jamais planter »),
mais un joueur Linux dont le lancement échoue n'aura aucune explication.

**Rien de tout cela n'est un défaut de sécurité.** Le code est sobre, commenté,
et manifestement écrit par quelqu'un qui a réfléchi au fait de ne pas casser
Windows — les gardes sont là où il faut.

---

## 🛑 BLOC C — la preuve que Windows ne bouge pas

`outils/verifier_pr4_windows.py` — **18 assertions, toutes vertes.**

Le banc compare au comportement **d'origine recopié mot pour mot** dans le
fichier, pas à une reformulation.

### Les trois chemins

**1. Le dossier de configuration**

| cas | ancien code | la PR | identique ? |
|---|---|---|---|
| `APPDATA` normal | `C:\Users\<utilisateur>\AppData\Roaming\AscensionFR` | idem | **oui, caractère pour caractère** |
| `APPDATA` forcé | `C:\Users\<utilisateur>\AppData\Roaming\AscensionFR` | idem | **oui** |
| **`APPDATA` absent** | `.\AscensionFR` *(relatif !)* | `C:\Users\<utilisateur>\AscensionFR` | **NON** |
| **`APPDATA` vide** | `AscensionFR` *(relatif !)* | `C:\Users\<utilisateur>\AscensionFR` | **NON** |

**2. Le lancement** — `os.startfile` espionné :
un seul appel, **le même argument inchangé**, `True` quand ça part, `False` sur
`OSError` (l'ancien code faisait `except OSError: pass` puis passait au
candidat suivant — comportement identique), et le prefixe passé en second
argument est **ignoré**.

**3. La détection du jeu** — `pistes_jeu_linux()` rend `[]`, `prefixe_de()`
rend `None`, et la passe 0 (`pistes.extend([])`) ne change **ni l'ordre ni le
contenu** de la liste.

**Bonus, et c'est le point de chaîne d'approvisionnement :** j'ai espionné
`subprocess.Popen` et lancé `lancer()` sur un `.exe`, un `.txt` et un dossier.
**Zéro processus lancé.** Le seul `subprocess` du module est hors d'atteinte
sous Windows.

### 🛑 Le banc mord — et il m'a repris deux fois

J'ai cassé les trois chemins exprès, un par un :

| défaut introduit | résultat |
|---|---|
| le dossier de config dévie | **5 assertions rouges** |
| `lancer()` modifie l'argument | **2 assertions rouges** |
| la garde `if not EST_LINUX` retirée | **1 assertion rouge** |

**Mais la troisième ne mordait pas au premier essai — et c'est la leçon.**
En retirant la garde, `pistes_jeu_linux()` *tourne* sous Windows… et rend
quand même `[]`, parce que `~/Games` et `~/.config/faugus-launcher` n'existent
pas sur cette machine. Mon assertion était satisfaite **pour la mauvaise
raison** : elle ne distinguait pas « inerte par conception » de « vide par
chance ».

Ce n'est pas théorique : un joueur Windows qui aurait un dossier
`C:\Users\<utilisateur>\Games\quelquechose\drive_c` ferait mordre le balayage.

**J'ai donc changé ce que je mesure** : au lieu du résultat, je compte les
**accès au disque**. Sous Windows la fonction doit en faire **zéro**. Avec la
garde : 0. Sans la garde : **8**. Là, ça mord.

*(Et une correction que je me suis faite : ma première version affirmait
« les deux chemins DOIVENT différer » pour le cas `APPDATA` absent — une
assertion qui serait passée au rouge le jour où quelqu'un corrigerait la
divergence. Une assertion qui interdit la correction du défaut qu'elle signale
est pire qu'inutile. C'est devenu un signalement, pas une assertion.)*

### Le seul changement Windows, et ce que j'en pense

Quand `APPDATA` est **absent ou vide**, la configuration ne va plus dans
`.\AscensionFR` (relatif au dossier de lancement) mais dans
`C:\Users\<toi>\AscensionFR`.

- Sur une machine Windows saine, `APPDATA` est **toujours** posé : ce cas ne
  concerne qu'un environnement abîmé.
- Le nouveau comportement est **plus sain** — l'ancien éparpillait la config au
  gré du dossier depuis lequel l'exe était lancé.
- Mais c'est **un changement** : un joueur dans ce cas retrouverait une
  configuration vierge (dossier du jeu à re-sélectionner).

**Je ne tranche pas.** Le banc l'épingle et le dit en toutes lettres à chaque
passage.

---

## BLOC D — ce qui partirait sans avoir été éprouvé

Sois clair là-dessus avant de signer : **tout ce qui est spécifique à Linux
partirait sans qu'aucun de nous deux ne l'ait vu fonctionner.**

| ce qui est éprouvé par nous | comment |
|---|---|
| aucun conflit de fusion | mesuré, fusion à blanc |
| Windows ne bouge pas | 18 assertions, banc vu échouer 3 fois |
| aucun réseau, aucune écriture | vérifié mécaniquement sur les 218 lignes |
| le `subprocess` est inatteignable sous Windows | compté : 0 processus |
| le code compile et passe `pyflakes` | oui, arbre fusionné |

| ce qui partirait NON éprouvé | pourquoi |
|---|---|
| la **détection du jeu dans un prefixe** Wine/Proton | il faudrait un vrai prefixe avec un vrai client |
| la lecture de `games.json` de **Faugus** | aucun de nous n'a Faugus |
| le **lancement** du jeu via umu / wine / xdg-open | ni Linux, ni runner |
| `lancer-linux.sh` (venv, pip, tkinter) | script bash, jamais exécuté ici |
| les **8 racines de prefixes** en dur | on ne sait pas si elles couvrent les installations réelles |
| le comportement quand `~/Games` contient **des centaines** de prefixes | la borne de 300 n'a jamais été atteinte pour de vrai |

**En clair : la moitié Linux de cette PR repose entièrement sur la parole de
son auteur.** Ce n'est pas un reproche — c'est exactement la situation normale
quand quelqu'un contribue pour une plateforme qu'on n'a pas. Mais il faut le
savoir avant de publier.

### Comment le faire éprouver par Tetardtek — ma proposition

Ne lui demande pas « est-ce que ça marche ? ». Demande-lui **des sorties
copiées**, sur lesquelles on peut raisonner :

1. **La détection** — dans le dossier `compagnon` de sa branche :
   ```
   python3 -c "import plateforme,json;print(json.dumps(plateforme.pistes_jeu_linux(),indent=1))"
   ```
   → doit lister son dossier de jeu. S'il est vide, la détection ne marche pas
   chez lui non plus.

2. **Le Compagnon complet** : `./lancer-linux.sh`, puis une capture de l'onglet
   Traduction montrant le dossier du jeu **trouvé tout seul**, et une
   installation de l'addon menée jusqu'au bout.

3. **La vérification en jeu** : `/afr` en jeu, et la fenêtre du panneau qui
   montre la traduction active. C'est la seule preuve que la chaîne complète
   fonctionne.

4. **Sur quel runner** exactement (Faugus ? Lutris ? Steam Proton ?) et **quelle
   distribution**. Une seule combinaison éprouvée vaut mieux qu'un « ça marche »
   sans contexte — et ça dit aux autres joueurs Linux ce qui est connu pour
   marcher.

5. **La question de `lancer-linux.sh`** : lui demander si viser `compagnon.py`
   (interface v2) plutôt que `compagnon_hub.py` (le Hub, celui de l'exe
   Windows) est **voulu**. C'est peut-être délibéré — mais si ça ne l'est pas,
   c'est mieux de le savoir avant publication qu'après.

---

## BLOC E — le verdict

### Intégrable maintenant ? **Oui.**

Pas de conflit, pas de dette, pas de risque Windows démontrable. Le prix en
travail de mon côté est **déjà payé** : l'audit et le banc sont faits. Ce qui
reste est mécanique — fusionner, reconstruire, repasser la barrière.

### Dans quel ordre ? **En 3.4.2, pas dans la 3.4.1.**

Et je vais argumenter contre l'envie, parce que c'est la partie qui compte.

**Ce qui plaide pour l'inclure tout de suite :** aucun conflit, donc aucun coût
de portage ; Tetardtek attend une réponse depuis le 31/07 ; et une contribution
qu'on laisse mûrir est une contribution qui refroidit.

**Ce qui plaide contre, et qui l'emporte à mon avis :**

1. **La 3.4.1 est déjà construite, vérifiée, empreinte `a63c717b…`.** L'intégrer
   veut dire tout refaire : reconstruire, repasser 20 bancs, revérifier
   l'empreinte. Ce n'est pas long, mais **on jette un état prouvé.**

2. **La 3.4.1 corrige des pannes qui touchent des joueurs maintenant** — les
   micro-lags d'`Epreuves` (97-99 % du coût mesuré, actif par défaut, tout le
   monde) et les chemins accentués. Les faire attendre une épreuve Linux qui
   dépend d'un tiers, c'est faire payer aux joueurs Windows un travail qui ne
   les concerne pas.

3. **La moitié Linux n'est pas éprouvée** (bloc D). Attendre les sorties de
   Tetardtek coûte quelques jours ; publier sans elles engage l'exe de 274
   personnes sur du code qu'aucun de nous n'a vu tourner.

4. **Deux questions ouvertes méritent une réponse de l'auteur avant publication**
   — l'entrée de `lancer-linux.sh`, et si le changement de comportement
   `APPDATA` lui convient. Ce sont des échanges de quelques heures, pas des
   semaines.

### Ce que ça oblige à refaire, si tu décides l'inverse

- synchroniser le dépôt public (geste 1, déjà en attente pour la 3.4.1) ;
- fusionner la PR — quelques minutes, sans conflit ;
- **reconstruire l'exe** et refaire la copie `Hub.exe → Compagnon.exe` *(qui
  n'est toujours scriptée nulle part — voir programme 12)* ;
- vérifier que **`plateforme` est bien dans le paquet** (la ligne de commande
  est au bloc B) ;
- repasser les 20 bancs + `verifier_pr4_windows.py` ;
- refaire le zip manuel, nouvelles empreintes.

Compte **20 à 30 minutes**, pas une journée. Le coût n'est pas le travail :
c'est de jeter un état prouvé.

### Ce que je ferais à ta place, franchement

**Je publierais la 3.4.1 telle quelle, aujourd'hui**, et je répondrais à
Tetardtek dans la foulée — avec du concret, pas un « merci, on regarde » :

> « Fusion à blanc faite : **zéro conflit**. Audit du code : aucun appel
> réseau, aucune écriture, un seul `subprocess` sans `shell=True`, et j'ai
> prouvé par un banc que Windows ne bouge pas (18 assertions). C'est du bon
> travail. Deux questions avant d'intégrer, et une demande. »

Puis **3.4.2 Linux dès qu'il a répondu** — probablement en quelques jours.

Ce n'est pas de la prudence pour la prudence : c'est que **les deux versions
n'ont pas le même public ni le même risque**. La 3.4.1 répare pour tout le
monde et elle est prouvée. La 3.4.2 ajoute pour quelques-uns et repose sur une
épreuve qu'on n'a pas encore. Les mélanger ferait porter le risque de la
seconde à la première.

Et il y a un bénéfice de fond à séparer : **si quelque chose casse dans les
jours qui suivent, on saura lequel des deux l'a causé.** Fusionnées, on ne le
saurait pas.

---

## Ce que j'ai failli casser — et ce que j'avais dit de travers

**1. J'avais annoncé des conflits sans les mesurer.** Tu as eu raison de me
reprendre : je confondais « les mêmes fichiers » et « le même code ». La mesure
dit **zéro ligne disputée**, et 17 lignes de distance au plus près. Mon
avertissement était faux, et il aurait pu coûter une contribution.

**2. Mon banc ne mordait pas sur le troisième chemin**, et il m'a fallu casser
exprès pour m'en apercevoir. Il vérifiait un résultat (`[]`) que
l'environnement rendait vrai par accident. Corrigé : il compte maintenant les
accès disque. C'est la troisième fois cette semaine qu'une assertion « verte
pour la mauvaise raison » me passe sous le nez — **on ne sait pas qu'un banc
marche tant qu'on ne l'a pas vu échouer.**

**3. Une assertion qui interdisait sa propre correction.** J'affirmais que les
deux comportements `APPDATA` *doivent* différer : le jour où quelqu'un
corrigerait la divergence, mon banc aurait rougi. Devenu un signalement.

**4. Une mesure faussée par une liste partagée.** `noter()` gardait une
référence vivante ; un bloc ultérieur polluait une assertion antérieure et la
faisait rougir à tort. Corrigé par une copie.

🛑 **Rien de fusionné, rien de porté, rien de reconstruit. Le travail de
Tetardtek n'a pas été modifié d'un caractère** — tout s'est passé dans un bac à
sable temporaire, et le dépôt public n'a pas bougé.

**État vérifié après coup :**

| | |
|---|---|
| `depot_github` | **0 fichier modifié**, toujours sur `0226ee0` |
| exe de la 3.4.1 | `a63c717bc071caa1…` — **inchangé** |
| zip de la 3.4.1 | `92e79b7e2cc50004…` — **inchangé** |

Une seule trace subsiste : j'ai récupéré la branche `pr4` en local dans
`depot_github` (`git fetch origin pull/4/head:pr4`). C'est une **lecture**,
rien n'a été poussé — et elle te servira si tu décides d'intégrer. Pour
l'effacer : `git -C depot_github branch -D pr4`.

---

## Ce que j'ai livré

**Nouveau**
- `outils/verifier_pr4_windows.py` — 18 assertions, éprouvé en cassant les
  trois chemins. **Pas dans le banc de santé** : il porte sur du code non
  fusionné et se lance à la main, avec `--arbre <dossier compagnon de la PR>`.

**Non modifié**
- la PR de Tetardtek — pas un caractère
- le dépôt public
- la 3.4.1 construite
