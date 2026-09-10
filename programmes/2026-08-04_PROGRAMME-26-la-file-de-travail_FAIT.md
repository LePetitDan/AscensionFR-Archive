# Demande de code → Claude Code

# 📋 PROGRAMME 26 — donner aux contributeurs quelque chose à corriger

**Date :** 2026-08-04

**Le constat, c'est le tien** (programme 19, bloc D) :

> *« Un contributeur n'a aujourd'hui aucun moyen de savoir quoi corriger. […] C'est le vrai
> goulot : la boucle technique marche, mais sans file de travail visible, l'ouverture produira
> quelques corrections opportunistes et rien de systématique. »*

Depuis, tout le reste est en place : les textes sont publics, le pont fait circuler les
corrections sans rien écraser, et l'ouverture a été annoncée aux 274 joueurs. **Il ne manque
que ça.** Un contributeur motivé ouvre `sorts.json`, voit 135 604 textes, et referme.

🛑 **Ce programme ne publie rien.** Il mesure, il éprouve le nettoyage, il propose. Dan
tranchera avec les chiffres devant lui — comme au programme 19.

---

## BLOC A — ce qu'il y a vraiment dans les rapports

**7 532 fichiers dans `rapports/`.** Je ne sais pas ce qu'ils contiennent et je ne veux pas le
deviner.

- **qu'est-ce qu'un rapport, concrètement ?** Montre-m'en un, entier, anonymisé ;
- **combien sont exploitables ?** Un rapport qui dit « ce texte est en anglais » est une tâche ;
  un rapport vide ou en double n'en est pas une. Donne le compte des deux ;
- **est-ce qu'un rapport dit dans quel fichier et sous quelle clé** se trouve le texte fautif —
  ou faut-il le retrouver ? Si c'est retrouvable par programme, dis comment et à quel taux ;
- **`traductions/propositions_joueurs.json`** — 7 entrées, les propositions des joueurs
  eux-mêmes. C'est le matériau au signal le plus fort du lot : regarde-le en premier ;
- **et `#rapports-auto`** : est-ce que le salon Discord contient des choses qui ne sont pas
  dans `rapports/` ? Si les deux divergent, je veux le savoir.

---

## 🛑 BLOC B — le nettoyage, et il n'est pas négociable

Ces rapports viennent de joueurs. Ils peuvent porter un pseudonyme, un nom de personnage, un
nom de compte Windows, un chemin de disque, une adresse.

**Règle du projet, sans exception : on ne cite jamais un joueur.** La purge du 21/07 portait
précisément là-dessus — 47 noms, 241 textes.

Donc, sur tout ce qui pourrait devenir public :

1. `balayer_secrets.py` ;
2. **les pseudonymes**, avec le dictionnaire de `noms_recolteurs.local.txt` ;
3. **les chemins de disque**, avec ton motif resserré — pas celui qui rapportait 88 faux ;
4. ⚠️ **et ce que ces trois-là ne savent pas attraper.** Un nom de personnage inventé n'est
   dans aucun dictionnaire. **Dis-moi ce qui reste après le nettoyage automatique, et ce qui
   demanderait un œil humain.** Ne me réponds pas « c'est propre » : réponds « voilà ce que je
   sais attraper, voilà ce que je ne sais pas ».

**Avec le dénominateur.** N fichiers sur N réellement ouverts, comme aux programmes 19, 20, 22.

🛑 **Un seul doute = tu t'arrêtes et tu le nommes.** Publier le pseudo d'un joueur qui nous
faisait confiance, ça ne se rattrape pas.

---

## BLOC C — la forme : ce qui fait qu'un contributeur commence vraiment

C'est la partie où je veux ton jugement, pas de l'exécution.

**Le regroupement d'abord.** Une liste plate de 7 532 lignes est aussi décourageante qu'un
fichier de 135 604 textes. **Le même texte manquant est sûrement signalé par beaucoup de
monde.** Regroupe par clé, compte les occurrences — et tu obtiens un ordre de priorité qui ne
vient pas de nous mais des joueurs. *« Ce texte a été signalé 47 fois »* est une file de
travail ; *« voici 7 532 rapports »* n'en est pas une.

**Puis la forme. Pèse les trois, tranche, et justifie :**

- **des tickets GitHub** — un contributeur en prend un, dit qu'il le fait, le referme par sa
  proposition. C'est natif et ça évite que deux personnes fassent la même chose. Mais 7 532
  tickets serait absurde : combien après regroupement ?
- **un fichier engendré** dans le dépôt des textes — simple, mais rien n'empêche deux
  personnes de travailler sur la même ligne ;
- **autre chose** que je ne vois pas.

**Trois exigences, quelle que soit ta réponse :**

1. chaque entrée doit dire **quel fichier et quelle clé** modifier — sinon le contributeur
   repart chercher, et c'est là qu'il abandonne ;
2. ⚠️ **ça doit se régénérer tout seul.** Si Dan doit l'entretenir à la main, ce sera abandonné
   en trois semaines — il sera de moins en moins disponible, c'est tout le point du chantier.
   Où ça se branche : dans le pont ? dans l'atelier ? Dis-le ;
3. **rappelle-toi le piège du programme 19** : une chaîne d'interface sur sept (838 sur 5 974)
   ne sert à rien parce que l'officiel Blizzard l'emporte. **Une file de travail qui envoie les
   gens corriger des textes qui ne sortent jamais est pire qu'une file vide.** Filtre-les.

---

## BLOC D — éprouve-la sur toi-même

Ne me livre pas une liste : **prends-en une entrée et fais le trajet en entier.**

- va au fichier et à la clé qu'elle indique ;
- corrige ;
- fais tourner la chaîne ;
- **montre-moi le texte corrigé dans l'add-on fabriqué**, avant / après.

Si une entrée de la file ne mène pas à une correction possible, **la file ment**, et c'est ce
qu'on cherche à savoir maintenant plutôt que par un contributeur déçu.

⚠️ **Puis remets l'arbre de Dan en état**, et vérifie-le sur GitHub, pas en local.

---

## BLOC E — les rapports perdus

Il y a une vieille note dans les affaires en attente : **54 rapports de joueurs perdus**.
Pendant que tu as les mains dedans, regarde si ça veut encore dire quelque chose — perdus
comment, récupérables ou non. **Ne les répare pas**, dis-moi juste ce qu'il en est.

---

**« Terminé » veut dire :**

> - Ce qu'est un rapport, **montré**, et combien sont exploitables.
> - Le nettoyage, **avec son dénominateur** — et surtout **ce qu'il ne sait pas attraper**.
> - Le regroupement, et **combien d'entrées** il reste après.
> - Ta recommandation de forme, justifiée, et **où ça se régénère**.
> - **Une entrée de la file parcourue en entier**, jusqu'au texte corrigé dans l'add-on.
> - Ce qu'il en est des 54 rapports perdus.
> - Ce qui a résisté, et ce que tu as failli casser.

🛑 **Rien de publié, aucun ticket créé, aucune fusion, aucun tag. `WorkFlow` sans remote.**

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Puis renommer en `_FAIT.md`.)

---

# BLOC A — ce qu'il y a vraiment dans les rapports

## Le compte, d'abord — il a changé depuis ta note

`rapports/` contient **9 900 fichiers**, pas 7 532 : les rapports continuent d'arriver.
Et ce ne sont pas 9 900 rapports :

| ce que c'est | combien |
|---|---|
| **rapports de joueurs** (`auto_*_rapport_*.txt`) | **4 957** |
| **caches WDB joints** (`auto_*_caches_*.json.gz`) | 4 850 |
| sorties d'outils à nous (`.txt`, `.json`, `.lua`, `.md`) | 93 |

**Dénominateur : 4 957 vus, 4 957 réellement ouverts et analysés, 0 illisible, 0 vide.**

## Un rapport, entier

Voici le plus petit rapport complet (401 octets), tel quel. C'est la forme de tous :

```
Signalement Ascension FR — via le Compagnon
AscensionFR 3.3.0

=== Compte 1 ===
--- Récolte : rencontrés sans traduction (1) ---
[TextesPNJ] Well, if it isn't a young, bristling cultist, no doubt drawn here by talk of
my exploits in fields of battle!

No time for stories now, for there are great, important deeds that need doing!  So if
you're looking for glory, then luck shines on you today...
```

Un rapport est donc : un en-tête, un bloc par compte de jeu, et des **sections**.
Sur les 4 957 :

| section | dans combien de rapports |
|---|---|
| **Récolte : rencontrés sans traduction** | 4 751 |
| Échecs d'alignement S (sorts) | 4 156 |
| Échecs d'alignement O (objets) | 2 389 |
| **Signalements** (le joueur a cliqué pour signaler) | 67 |
| **Propositions** (le joueur a écrit une traduction) | 4 |

## Combien sont exploitables

La récolte donne **118 277 entrées brutes** — mais **32 190 couples (catégorie, texte)
distincts**. C'est ton intuition, chiffrée : **chaque texte manquant est signalé 3,7 fois en
moyenne**, et jusqu'à 553 fois pour le pire.

⚠️ **Ma première mesure était fausse et je l'ai jetée.** Je comparais aux `traductions/*.json`
et j'annonçais « 23 107 à traduire (71,8 %) ». Or `outils/ingerer_recolte.py` **existe déjà**
et verse ces récoltes dans `DB_Communaute.lua` — un fichier de 3 Mo qui contient **3 360
gossips, 3 798 textes de PNJ et 4 499 champs de quête déjà traités**. Mon dénominateur ignorait
tout le travail déjà fait.

Contre les bases **réelles** (générées + `DB_Communaute`), voici l'état honnête :

| catégorie | déjà couvert | déjà en français (faux positif de l'addon) | **RESTE** |
|---|---|---|---|
| Gossip | 3 392 | 1 686 | **477** |
| TextesPNJ | 3 006 | 35 | **2 015** |
| Divers | 318 | 93 | **5 320** |
| Pages | 15 | 3 | **232** |
| QuetesRendu | 26 | — | **4 905** |
| QuetesProgres | 17 | — | **3 360** |
| Sorts | *(identifiants — voie `recuperer_db.py`)* | — | *7 290* |

> **RESTE À FAIRE : 16 309 entrées distinctes, totalisant 55 809 signalements de joueurs.**

## Un rapport dit-il quel fichier et quelle clé ?

**Oui pour 8 044 entrées sur 16 309, directement.** La catégorie donne le fichier, et **le texte
anglais EST la clé** :

| catégorie du rapport | fichier | clé |
|---|---|---|
| `[Gossip] <texte>` | `traductions/gossip.json` | le texte anglais |
| `[TextesPNJ] <texte>` | `traductions/textes_pnj.json` | le texte anglais |
| `[Divers] <texte>` | `traductions/divers.json` | le texte anglais |
| `[Pages] <texte>` | `traductions/pages.json` | le texte anglais |

**Non pour les deux autres familles, et il faut le dire :**

- **`[Sorts] 704154`** — 100 % des entrées Sorts sont des **identifiants**, pas du texte
  (mesuré sur 3 374 entrées d'un échantillon de 400 rapports : 3 374 numériques, 0 texte). Ils
  passent par `outils/recuperer_db.py`, pas par une file de contributeurs ;
- **`[QuetesRendu] 254008 ==> <texte>`** — la base `quetes.json` est indexée par
  **identifiant**, avec des champs `P`/`R`. Le texte anglais est là, mais après un `==>`.
  **Retrouvable par programme à 99 %** (8 265 sur 8 308 portent le `==> texte`).

## `propositions_joueurs.json` — le signal le plus fort, et il est maigre

**7 entrées.** Les voici toutes, c'est peu et ça se lit :

| type | actuel | proposé |
|---|---|---|
| texte | `Increases Spirit by 4.` | Augmente l'esprit de 4. |
| texte | `Stormwind Gate` | Porte d'Hurlevent |
| texte | `Food Crate` | Boite de nouriture |
| sort 777003 | Pierre de retraite : Stormwind | Pierre de retraite : Hurlevent |
| interface `WatchFrameHeader` | Objectives (3) | Objectifs |
| pnj 161702 | Sœur Alma | *(« The way is shut… » — un essai, pas une proposition)* |
| sort 3599 | *(description de totem)* | *(« Je teste la traduction… » — un essai)* |

**Deux des sept sont des essais de l'outil, pas des propositions.** Cinq sont utilisables, et
trois sont justes du premier coup. Ce n'est pas un gisement — c'est la preuve que **le
mécanisme marche et que personne ne s'en sert**, faute de savoir quoi corriger.

## `#rapports-auto` et `rapports/` divergent-ils ?

**Je ne peux pas interroger Discord ici** (pas de jeton de bot dans cette session) — je le dis
plutôt que de faire semblant. Ce que j'ai pu mesurer, c'est le journal d'ingestion contre le
disque :

```
ingeres.json                              4 850 entrées
notés ingérés mais ABSENTS du disque          0
sur le disque mais PAS au journal            107   <- des rapports sans cache joint
cache SANS rapport                            0
```

Le journal ne suit que les **caches**, pas les rapports. Les 107 sont des rapports envoyés sans
pièce jointe de cache (le joueur n'en avait pas à donner). **Aucune perte détectable de ce
côté** — mais la vraie comparaison, salon contre disque, reste à faire avec le jeton.

---

# 🛑 BLOC B — le nettoyage, et ce qu'il ne sait pas attraper

Je n'ai pas réécrit de balayeur : j'ai repris **celui du pont** (`pont_textes.balayer`), qui
porte déjà le dictionnaire de pseudonymes et le **motif de chemins resserré** — pas celui qui
rapportait 88 faux.

**Dénominateur : 4 957 / 4 957 rapports ouverts, 16 309 entrées de file balayées,
47 pseudonymes au dictionnaire.**

| contrôle | résultat |
|---|---|
| 1. `balayer_secrets` (21 familles) | **0 motif** sur 16 309 textes |
| 2. **pseudonymes du dictionnaire** | **454 entrées** — voir ci-dessous |
| 3. chemins de disque (motif resserré) | **0** |

## 🛑 Les 454 ne sont PAS des faux positifs. Je me suis arrêté.

J'ai instruit le doute **sans afficher un seul nom** (empreintes tronquées et longueurs). Le
verdict est net :

- le dictionnaire a **47 noms**, dont **un seul** de 4 caractères ou moins, et **aucun** qui
  soit un mot anglais courant — le risque de faux positif est donc structurellement faible ;
- **46 des 47 déclenchent au moins une fois** ;
- et voici pourquoi :

```
[QuetesProgres] 851  ==> Did you find Verog, <NOM DU JOUEUR>?
[QuetesRendu]   457  ==> You performed your duties well, <NOM DU JOUEUR>.
[QuetesProgres] 20   ==> Have you been slaying orcs, <NOM DU JOUEUR>?
```

**Le jeu substitue le nom du personnage dans le texte de quête AVANT que l'addon le récolte.**
Le texte « anglais » d'un rapport de quête porte donc, en clair, le nom du personnage du joueur
qui l'a envoyé. Ce n'est pas un accident de collecte : c'est le fonctionnement normal de `$N`.

**Une file construite sur ces textes publierait le nom de personnage de tout joueur ayant
signalé une quête.** Le dictionnaire n'en connaît que 47 — les autres passeraient.

## ⚠️ Mais il y a une source propre, et je l'ai mesurée

Les **caches WDB joints aux rapports** contiennent le texte tel que le serveur l'envoie,
c'est-à-dire **avec `$N` non substitué** :

```
caches réellement OUVERTS                          4 850 / 4 850
contenant un `$n`/`$c` NON substitué               4 846 / 4 850
contenant un pseudonyme CONNU en clair                 0 / 4 850
```

```
"Details": "$N, my scouts tell me that the kobold infestation…"
```

**C'est le dénominateur complet, pas un échantillon.** Zéro pseudonyme sur les 4 850.

> **Conséquence, et c'est la décision de conception de tout ce programme : la file de travail
> se construit à partir des CACHES, jamais du texte récolté chez le joueur.** Le rapport sert à
> savoir *quoi* est manquant et *combien de fois* ; le cache fournit *le texte*.

## ⚠️ Ce que le nettoyage automatique NE SAIT PAS attraper

Tu m'as demandé de ne pas répondre « c'est propre ». Voilà ce que je sais attraper et ce que je
ne sais pas.

| ce que je ne sais pas attraper | combien | pourquoi |
|---|---|---|
| **un nom de personnage inventé** | **inconnu, et c'est le point** | le dictionnaire ne connaît que les 47 récolteurs identifiés. Un joueur qui n'a jamais été identifié n'y est pas |
| du **français** que `paraît_anglais` laisse passer | **31 entrées** | le filtre cherche des accents et une petite liste d'articles ; « Chemin vers l'ascension : Cavalier novice » (553 signalements) n'a ni accent ni article de la liste |
| des entrées d'**un seul mot capitalisé** | **33** | `Preface`, `Arachnophobie`, `Trollemort`… la forme exacte d'un nom de personnage. Ici ce sont des mots de jeu, mais rien ne le prouve par programme |
| des entrées portant **`$n` / `$c`** | 250 | déjà normalisées — c'est le comportement souhaité, je les note pour montrer que les deux formes coexistent |
| adresses e-mail | 0 | — |
| suites de ≥ 9 chiffres | 4 | toutes des liens de jeu (`|Hquest:175052:…`), pas des identifiants de compte |

**Ce qui demanderait un œil humain :** les 33 mots isolés et les 31 entrées déjà françaises —
soit **64 lignes à relire**, une fois, avant la première publication. C'est faisable en une
demi-heure et je ne le ferai pas sans ton accord.

**Ce qui ne se règle PAS à l'œil :** les noms de personnages dans les textes de quête. Il y en a
potentiellement autant que de joueurs ayant signalé. **La seule réponse sûre est structurelle :
ne pas publier ce texte-là.** D'où la décision ci-dessus.

## Le piège du programme 19 : vérifié, il ne s'applique pas

Les 838 étiquettes inutiles sur 5 974 vivent dans `interface_maison.json`. **Aucune catégorie
de rapport ne l'alimente** — les sept catégories sont `Divers, Gossip, Pages, QuetesProgres,
QuetesRendu, Sorts, TextesPNJ`. Mesuré sur les 8 044 entrées hors quêtes : **0 est un nom de
GlobalString**, 2 coïncident avec un libellé d'interface. **La file ne peut envoyer personne
sur un texte que l'officiel écrase.**

---

# BLOC C — la forme

## Le regroupement : de 118 277 à 808

Le regroupement change tout, exactement comme tu le disais. L'ordre ne vient pas de nous :

| seuil | entrées |
|---|---|
| signalées **1 fois** ou plus | 16 309 |
| signalées **2 fois** ou plus | 5 342 |
| signalées **3 fois** ou plus | 3 603 |
| signalées **5 fois** ou plus | 2 072 |
| **signalées 10 fois ou plus** | **808** |
| signalées 20 fois ou plus | 372 |
| signalées 50 fois ou plus | 144 |

Le haut de la file, tel qu'il sortirait :

```
479 × [Divers] As group leader, you have |cFF00FF00enabled|r creature scaling…
389 × [Divers] The item has been delivered to your bags!
368 × [Divers] You have unlocked this item already. Please use the "Vanity" Collection…
254 × [Divers] Your Vanity Collection Sync has started…
197 × [Divers] You need at least 2 free slots in your inventory to use this item!
```

*« Ce texte a été vu sans traduction par 479 joueurs »* — c'est une file de travail.

## Ma recommandation : un fichier engendré, pas des tickets

**Pas de tickets GitHub.** Trois raisons, dans l'ordre où elles pèsent :

1. **Même après regroupement, c'est 808 tickets** pour le seuil raisonnable (≥ 10
   signalements), 372 pour ≥ 20. Un dépôt avec 372 tickets ouverts ne dit pas « viens
   aider », il dit « c'est ingérable ». Et il faudrait les **fermer** un par un ;
2. **ça ne se régénère pas.** C'est ton exigence n° 2, et c'est celle qui tue les tickets : le
   jour où un texte est traduit par un autre chemin (l'Atelier, `ingerer_recolte`, une PR),
   son ticket reste ouvert. Il faudrait un robot pour les refermer — un mécanisme de plus à
   entretenir, exactement ce qu'on veut éviter ;
3. **le vrai risque de collision est faible** : 16 309 entrées, et un contributeur en prend
   quelques dizaines. Deux personnes sur la même ligne, ça arrive ; deux personnes sur le même
   *lot*, beaucoup moins.

**Ce que je recommande, concrètement :**

```
AscensionFR-Textes/
  FILE-DE-TRAVAIL.md          <- lisible, le haut de la file, 200 entrées
  file-de-travail/
    lot-001.json … lot-N.json <- 50 entrées par lot, engendrés
```

- **un lot = 50 entrées**, ordonnées par nombre de signalements. Le lot 1 est le plus utile,
  le lot 40 le moins. Un contributeur prend un lot, pas une ligne ;
- **chaque entrée porte le fichier ET la clé** — ton exigence n° 1 :

```json
{ "signalements": 389,
  "fichier": "traductions/divers.json",
  "cle": "The item has been delivered to your bags!",
  "traduction": "" }
```

- **le « qui fait quoi » tient dans UN seul ticket GitHub** épinglé (« Lots en cours »), où
  chacun écrit le numéro qu'il prend. Un ticket à entretenir, pas 372. Et si deux personnes
  prennent le même lot, on l'apprend en trois lignes de commentaire, pas après le travail.

**Où ça se régénère :** dans **`outils/pont_textes.py`, à l'étape `--publier`**. C'est le seul
endroit qui touche déjà au dépôt des textes, qui balaye déjà les secrets et les pseudonymes,
et que Dan lance déjà. Rien de nouveau à retenir : *quand le pont publie les textes, il
republie la file*. Une entrée traduite disparaît du lot suivant toute seule, puisque la file
est recalculée contre les bases.

**Ce que ça n'est PAS** : un fichier que Dan édite. Il est **engendré**, et le seul geste
humain est `pont_textes.py --publier`, qui existe déjà.

## ⚠️ La contrainte du bloc B, appliquée à la forme

**Les quêtes ne rentrent pas dans cette file telle quelle** — 8 265 entrées sur 16 309, soit la
moitié, portent le nom de personnage du joueur. Deux options, et je te dois les deux :

- **(a) les exclure de la première version.** La file démarre avec **8 044 entrées**
  (Divers, Gossip, TextesPNJ, Pages), dont **environ 500 au-dessus de 10 signalements**. C'est
  déjà largement de quoi occuper les premiers contributeurs, et c'est **sûr immédiatement** ;
- **(b) les inclure, mais en prenant le texte dans les CACHES** (`$N` non substitué, 0
  pseudonyme sur 4 850 mesurés). C'est la bonne solution à terme, et c'est du travail : il faut
  apparier `(id de quête, champ)` du rapport avec le cache correspondant.

**Je recommande (a) maintenant, (b) ensuite** — parce que (a) ne demande aucune décision et
qu'une file de 8 044 entrées n'est pas un manque de matière.

---

# BLOC D — le trajet, fait en entier

J'ai pris l'entrée **la plus signalée qui soit purement anglaise et sans balise** :

```
[Divers]  "The item has been delivered to your bags!"   —  389 signalements
la file indique : traductions/divers.json, clé = le texte anglais
```

| étape | résultat |
|---|---|
| **AVANT** — `traductions/divers.json` | 318 clés, **la clé n'y est pas** |
| **AVANT** — `DB_Divers.lua` (l'add-on) | **ABSENTE** — le joueur lit l'anglais |
| **la correction** | `"The item has been delivered to your bags!" → "L'objet a été livré dans vos sacs !"` |
| **la chaîne** | `python outils/generateur_db.py` → `Divers  319  55.6 Ko`, code 0 |
| **APRÈS** — `DB_Divers.lua` | `"L'objet a été livré dans vos sacs !"` |

```
AVANT : (rien — le joueur lit l'anglais)
APRÈS : L'objet a été livré dans vos sacs !
```

**La file ne ment pas** : une entrée mène bien à une correction visible dans l'add-on fabriqué,
sans que le contributeur ait rien à chercher.

## L'arbre de Dan, remis en état — et vérifié sur GitHub

```
traductions/divers.json rendu identique : True   (empreinte SHA-256)
DB_Divers.lua rendu identique           : True   (empreinte SHA-256)
```

Et la vérification qui compte, **sur GitHub et pas en local** — le dépôt public des textes :

```
traductions/divers.json publié   sha git be342fd348b4b2dcb9c29736c0639559aa188ca1   57 167 o
le fichier LOCAL de Dan          sha git be342fd348b4b2dcb9c29736c0639559aa188ca1   57 167 o
```

**Identiques.** Mon essai n'a laissé aucune trace, ni en local ni en ligne. *(`WorkFlow` n'a
toujours pas de remote ; le pont n'a pas été lancé.)*

> Précision pour ne pas te faire sursauter : `git status` marque toujours
> `M traductions/divers.json` dans `WorkFlow`. **Ce n'est pas moi** — il l'était déjà à
> l'ouverture de la session. Le fichier de travail est identique à ce qu'il était avant mon
> essai (empreinte SHA-256) **et** identique à celui publié (sha git `be342fd348…`) ; c'est le
> `HEAD` local de `WorkFlow` qui est en retard, ce qui lui préexiste.

---

# BLOC E — les 54 rapports perdus

**La note voulait dire autre chose, et la réalité d'aujourd'hui est pire.**

La note d'origine (programme 14, 01/08) parlait de **54 signalements distincts écrasés** par un
dédoublonnage sur `(type, identifiant, minute)` : les signalements de type « texte » n'ayant pas
d'identifiant, tous ceux d'une même minute s'effondraient en un.

**Ce défaut-là est éteint.** Mesuré sur les 4 957 rapports :

```
lignes de signalement BRUTES trouvées          345
minutes portant plus d'un signalement            2
signalements qui seraient écrasés                2   (contre 54 à l'époque)
```

**Mais en cherchant, j'ai trouvé plus gros :**

```
lignes de signalement brutes                   345
dont illisibles (« <Lua table at 0x… > »)       10   (3 %)
dont EXPLOITABLES                              335

traductions/rapport_signalements.txt (ce que Dan lit) :
   SIGNALEMENTS DU JOUEUR (0)
```

**335 signalements exploitables existent dans les rapports, et le fichier que tu lis en annonce
zéro.** La cause n'est pas un dédoublonnage : `outils/diagnostiquer_signalements.py` ne lit
**que les SavedVariables locales** — la partie de jeu de Dan. Il n'a jamais regardé les
rapports des joueurs.

Ce sont des gens qui ont cliqué « signaler » sur une info-bulle fautive, avec le texte et
l'identifiant de l'objet :

```
- 54001 | Crimson Scroll / Lié / Unique / "A blood-stained scroll that pulses with dark magic…"
```

**Tu m'as dit de ne pas les réparer, je ne les répare pas.** Mais « 54 perdus » est à remplacer
par **« 335 jamais lus »**, et c'est un correctif d'une portée différente.

*(Les 10 illisibles sont un vrai défaut de l'add-on : il sérialise une table Lua au lieu de son
contenu. Ils datent tous du 18/07 — c'est probablement déjà corrigé, mais ces dix-là sont
irrécupérables.)*

---

# Ce qui a résisté, et ce que j'ai failli casser

## Ce qui a résisté

- **La moitié du travail était déjà faite et je ne le savais pas.** `ingerer_recolte.py` verse
  les récoltes dans `DB_Communaute.lua` depuis longtemps — 11 657 entrées. Mon premier
  dénominateur les ignorait toutes.
- **`git bash` casse les scripts à antislash.** Trois fois, un `python -c "…"` contenant un
  motif d'expression régulière s'est fait manger par le shell (`unterminated character set`).
  Remède : écrire le script dans un fichier, jamais en ligne.
- **Le balayage complet des 4 850 caches a dépassé les 10 minutes** — passé en tâche de fond
  plutôt que réduit à un échantillon. Le dénominateur valait l'attente.

## Ce que j'ai failli casser

- **🛑 Publier le nom de personnage de joueurs.** C'est le vrai danger de ce programme, et il
  est passé à un cheveu. Ma première file contenait les 8 265 entrées de quête *telles que
  récoltées* — c'est-à-dire avec `$N` déjà remplacé par le nom du joueur. Le balayage a rendu
  « 454 entrées portant un pseudonyme connu », et **j'ai failli les traiter comme des faux
  positifs** : 454 sur 16 309, ça ressemble à du bruit de dictionnaire. Ce n'en était pas.
  Et le pire n'est pas les 454 : c'est que **le dictionnaire ne connaît que 47 personnes**.
- **Annoncer « 71,8 % à traduire ».** J'avais le chiffre, la ventilation par catégorie et le
  tableau prêt. Il était faux d'un facteur proche de deux, parce que je comparais à la mauvaise
  base. Un chiffre bien présenté n'est pas un chiffre juste.
- **Toucher l'arbre de Dan sans filet.** Le trajet du bloc D modifie `traductions/divers.json`
  puis **relance le générateur**, qui réécrit `DB_Divers.lua`. La remise en état est dans un
  `finally` et vérifiée par empreinte des deux côtés — sans ça, un plantage au milieu laissait
  l'add-on de Dan avec une entrée en plus.
- **Croire mon propre échantillon.** J'ai d'abord mesuré les caches sur 120 fichiers et écrit
  « 0 pseudonyme ». Sur une décision de cette nature, 120/4 850 ne vaut rien : refait sur les
  4 850.

---

# Ce que je propose, en une page

**Rien n'est fait — ce programme mesure et propose, comme demandé.** Voici ce qui reste à
décider :

| # | décision | mon avis |
|---|---|---|
| 1 | **la forme** : fichier engendré en lots de 50, ou tickets GitHub ? | **fichier engendré**, un seul ticket « lots en cours ». 372 tickets ne se referment pas tout seuls |
| 2 | **les quêtes dans la première version ?** | **non** — 8 265 entrées portent un nom de personnage. On démarre avec les 8 044 autres, qui suffisent |
| 3 | **relire à la main les 64 lignes douteuses** (33 mots isolés + 31 déjà en français) | oui, une fois, avant la première publication — une demi-heure |
| 4 | **où ça se régénère** | `outils/pont_textes.py --publier`, qui balaye déjà secrets et pseudonymes |
| 5 | **les 335 signalements jamais lus** | correctif à part, hors de ce programme — mais il vaut plus que la file elle-même par signalement |
| 6 | **le filtre `paraît_anglais`** laisse passer 31 textes français | l'élargir coûte trois mots dans une expression régulière |

🛑 **Rien de publié, aucun ticket créé, aucune fusion, aucun tag. `WorkFlow` est toujours sans
remote, et le dépôt des textes est intact — vérifié par empreinte git depuis GitHub.**

---

# « Terminé », point par point

| ce que tu demandais | fait ? | où |
|---|---|---|
| ce qu'est un rapport, **montré** | ✅ | bloc A — un rapport entier, 401 octets |
| combien sont exploitables | ✅ | 4 957 rapports → 32 190 couples distincts → **16 309 restants** |
| quel fichier / quelle clé, et à quel taux | ✅ | **8 044 directement** (catégorie → fichier, texte → clé) ; quêtes retrouvables à **99 %** ; Sorts = identifiants |
| `propositions_joueurs.json` regardé en premier | ✅ | 7 entrées, **5 utilisables, 2 sont des essais** |
| `#rapports-auto` vs `rapports/` | ⚠️ | journal contre disque : **0 perte** ; la comparaison au salon demande le jeton — **non faite, et dite** |
| le nettoyage **avec son dénominateur** | ✅ | 4 957/4 957, 16 309 textes balayés : 0 secret, 0 chemin, **454 pseudonymes** |
| **ce qu'il ne sait pas attraper** | ✅ | bloc B — 5 familles nommées, dont **les noms de personnages inconnus, structurellement hors de portée** |
| le regroupement, et combien il reste | ✅ | 808 à ≥ 10 signalements, 372 à ≥ 20, 144 à ≥ 50 |
| recommandation de forme + où ça régénère | ✅ | bloc C — fichier engendré en lots, dans `pont_textes.py --publier` |
| **une entrée parcourue en entier** | ✅ | bloc D — 389 signalements → texte français dans `DB_Divers.lua` |
| arbre remis en état, **vérifié sur GitHub** | ✅ | empreintes SHA-256 locales + **sha git identique côté dépôt public** |
| les 54 rapports perdus | ✅ | bloc E — le défaut d'origine est éteint (2 au lieu de 54), mais **335 signalements ne sont lus par personne** |
| ce qui a résisté / failli casser | ✅ | ci-dessus |
