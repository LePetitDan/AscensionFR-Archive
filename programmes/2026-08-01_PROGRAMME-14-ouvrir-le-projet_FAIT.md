# Demande de code → Claude Code

# 🤝 PROGRAMME 14 — ouvrir le projet à d'autres : ce qu'il faut VRAIMENT

**Date :** 2026-08-01
**À faire après les programmes 12 et 13.**

Dan sera de moins en moins disponible. Il veut ouvrir **trois** choses à des gens de confiance :
**traduire**, **arbitrer**, **écrire du code**. Il garde la publication — c'est la seule clé
sensible, un exe non signé qui se met à jour tout seul sur 274 machines.

🛑 **Ce programme ne construit RIEN.** Il mesure et il propose. On a passé la semaine à découvrir
que la moitié de ce qu'on croyait était faux ; je ne veux pas faire bâtir un atelier de
contribution avant de savoir ce qu'il doit contenir.

---

## BLOC A — combien de décisions restent VRAIMENT à prendre ?

C'est la mesure la plus rentable du programme.

Depuis la règle de Dan du 26/07 — **« l'officiel Blizzard gagne par défaut, sauf quand il perd du
sens »** — une grande partie des arbitrages en attente se tranche mécaniquement. Applique la règle
et compte :

| en attente | combien la règle tranche seule | combien demandent un humain |
|---|---|---|
| **1 762 conflits Glayna** | ? | ? |
| **121 divergences** | ? | ? |
| **204 signalements explicites** | ? | ? |

**Et donne-moi un échantillon d'une trentaine de cas « demandent un humain »**, tirés au hasard,
pas choisis. Je veux voir à quoi ressemble une vraie décision restante — c'est ça qui dira si un
bénévole peut la prendre, ou s'il faut le jugement de Dan.

**Si le compte tombe à quelques dizaines, on n'a pas besoin d'un atelier d'arbitrage du tout.**
Dis-le franchement si c'est le cas.

---

## BLOC B — la traduction : découper 12 000 entrées en lots qu'on puisse confier

Le tri du 25/07 donne : **4 087 quêtes, 2 878 dialogues, 2 831 sorts, 1 717 textes PNJ,
1 102 divers, 95 pages.** ⚠️ Il date de **sept jours** et il périme en un jour — **relance
`clarifier_retours_joueurs.py` avant de compter quoi que ce soit.**

Ce que je veux savoir :

- **Peut-on découper par thème plutôt que par paquet de N ?** Une zone entière, une classe
  entière, un donjon entier. **C'est décisif** : traduire des phrases isolées hors contexte
  produit de mauvaises traductions, et c'est le premier reproche qu'on nous ferait.
- **Combien de lots, de quelle taille ?** Un lot doit tenir dans une soirée de bénévole, pas dans
  un été.
- **Sous quel format sortent-ils, et comment reviennent-ils ?** Il faut que quelqu'un qui n'est
  pas informaticien puisse travailler dedans.
- **Deux personnes peuvent-elles prendre le même lot sans le savoir ?** Dis comment on l'empêche.

---

## 🛑 BLOC C — le vrai risque n'est pas la malveillance, c'est l'incohérence

Cinq traducteurs sans vocabulaire commun produisent cinq traductions différentes du même mot. À
12 000 entrées, ça devient irrattrapable — et ça se voit tout de suite en jeu.

- Le `GLOSSAIRE.md` et la règle « l'officiel gagne par défaut » doivent **voyager avec le lot**,
  pas dormir dans un dossier que personne n'ouvre. Comment ?
- **Qu'est-ce qu'une contribution doit franchir avant d'entrer ?** Le projet a déjà des
  vérifications — dis lesquelles s'appliquent, et ce qu'il manque. Une contribution doit passer
  **par** le contrôle existant, jamais le contourner.
- **Comment on annule un lot entier** si quelqu'un a mal compris la consigne ? Si la réponse est
  « on ne peut pas », c'est un défaut à corriger avant d'ouvrir, pas après.

---

## BLOC D — le code : ce que ça suppose

Le dépôt public ne contient aujourd'hui que **les fichiers du Compagnon**. Le code de l'addon
n'y est pas du tout. Ouvrir la contribution au code veut donc dire **y publier le code de
l'addon**.

- Le **balayage de secrets du programme 13** est le préalable : rien ne part avant lui.
- Que devrait contenir le dépôt public pour qu'une contribution soit possible — et **que doit-il
  continuer à ne pas contenir** ?
- Un contributeur peut-il **éprouver son travail** sans la machine de Dan ? Le banc de santé
  tourne-t-il sur un poste nu, sans le jeu, sans les bases, sans les secrets ? Si non, il ne peut
  rien vérifier avant de proposer, et Dan hérite de tout le travail de contrôle.
- Que faudrait-il écrire pour qu'un nouveau venu comprenne le projet ? **Le `README.md` du
  pipeline est périmé** — il décrit le Compagnon et ignore le Hub.

---

## 🛑 BLOC E — la séquence de publication (ajouté après le programme 12)

**Ce bloc vient de ce que tu as trouvé en préparant la 3.4.1**, et il change la donne.

Tu as failli publier l'exe du 28/07 — celui qui ne contenait **rien** du programme 9 — parce que
le renommage `AscensionFR_Hub.exe → AscensionFR_Compagnon.exe` **n'est scripté nulle part**. Le
`.spec` produit un nom, `publier_github.py` en publie un autre, et la copie entre les deux est un
geste de mémoire. Le garde-fou de fraîcheur mordait, mais son conseil (« reconstruis ») ramenait au
même point : on tournait en rond.

Tant que Dan publie seul, ça tient — parce que c'est dans sa tête. **Le jour où quelqu'un d'autre
touche à la chaîne, ce piège devient une régression livrée à 274 machines**, en silence.

Dan garde la clé de publication, ce n'est pas ce qui est en question. Ce que je veux savoir :

- **Quelle part de la séquence est scriptée, et quelle part n'existe que dans sa tête ?** Liste les
  gestes de bout en bout, et marque chacun : automatique, semi-automatique, ou mémoire pure.
- **Combien de ces gestes de mémoire peuvent livrer une régression silencieuse** s'ils sont
  oubliés ou faits dans le désordre ?
- **Lesquels seraient scriptables sans risque**, et lesquels doivent rester manuels *exprès* ?

**Ne script rien ici.** Je veux la carte, pas la réparation — les correctifs iront dans la 3.5.

> **Un modèle à réutiliser, et il vient de toi.** `verifier_greffes.py` compare sa propre liste de
> noms aux greffes réellement posées, et **passe au rouge si elles divergent** — tu l'as éprouvé en
> retirant un nom. C'est exactement ce qu'il faut à un contrôle de contribution : une liste qui se
> vérifie elle-même contre la réalité, au lieu d'une liste qu'on croit à jour. Dis-moi où ce motif
> s'applique dans ce que tu proposeras aux blocs C et D.

---

## Ce que je ne veux PAS

- ❌ pas d'atelier, pas de plateforme, pas de script d'export construit dans ce programme ;
- ❌ **rien de scripté au BLOC E** — on cartographie, on ne répare pas ;
- ❌ rien qui touche au **droit** de publier : Dan garde cette clé, ce n'est pas le sujet ;
- ❌ aucun secret déplacé, aucun distant ajouté nulle part.

---

**« Terminé » veut dire :**

> - Les trois comptes du BLOC A, et **l'échantillon de trente cas réels**.
> - Le découpage en lots que tu recommandes, avec sa taille et son format.
> - Ce qu'une contribution doit franchir, et **comment on annule un lot**.
> - Ce que l'ouverture du code suppose de publier, et si un contributeur peut s'éprouver seul.
> - **La carte de la séquence de publication**, geste par geste, avec ce qui n'est que mémoire.
> - **Ton avis franc** : par quoi commencer, et qu'est-ce qui ne vaut pas le coup ?

---
## Réponse de Claude Code

> **Comment j'ai travaillé.** Chaque bloc a été mesuré par un agent séparé, puis **attaqué par
> deux sceptiques** chargés de réfuter les résultats. Ils ont trouvé de vraies erreurs — elles
> sont intégrées ci-dessous, pas cachées. Rien n'a été construit, aucun fichier du projet
> modifié, aucun distant ajouté. J'ai revérifié moi-même les deux découvertes les plus graves.

### BLOC A — combien de décisions restent VRAIMENT ?

| en attente | annoncé | **mesuré** | la règle tranche seule | **demandent un humain** |
|---|---|---|---|---|
| conflits Glayna | 1 762 | **1 761** | 2 | **≈ 1 750** ⚠️ voir plus bas |
| divergences | 121 | **121** | 121 | **0** |
| signalements explicites | 204 | **333** | 285 | **12** |

**Deux des trois colonnes s'effondrent. La troisième ne s'effondre pas — mais elle ne contient
pas ce que son nom dit.**

#### Les 121 divergences : **il n'en reste aucune**

Décomposées, état d'aujourd'hui, reproduit à l'unité près par le sceptique :

- **64** : notre version est devenue identique à l'officiel — ce n'est plus une divergence ;
- **48** : l'officiel est **écarté par le garde-fou** — Ascension avait renommé le sort, le
  français récupéré traduisait l'ancien nom. La règle « l'officiel gagne » ne peut même pas
  être invoquée ;
- **8** : décision « on garde le nôtre », enregistrée ;
- **1** : ne diffère que par un accent.

> **Correction que je dois faire à mon propre tableau.** Dire « la règle tranche 121 » est
> faux et efface ton travail : **56 de ces 121 portent une décision humaine que tu as prise le
> 28/07**. La formulation juste est « **0 en attente** ». Vérifié : les 49 décisions
> « adopter » sont bien les 49 déjà écrites dans `sorts.json`.

Un piège de lecture à noter, parce qu'il t'attendra la prochaine fois : **il y a deux « 48 »
différents** — 48 officiels disqualifiés par le garde-fou, et 48 verdicts renversés le 28/07.
Leur intersection est **vide** (mesuré). Ce ne sont pas les mêmes.

#### Les signalements : **12**, sur 333

Le chiffre de 204 était juste — c'était le fichier du 25/07. Les rapports bruts en contiennent
**338**, dont 333 distincts.

- **déjà réglé aujourd'hui** ou tranché par un officiel : **285** ;
- **pas une traduction** (cadres protégés, coquilles d'Ascension) : **21** ;
- **demandent vraiment un humain** : **12**.

Et ces 12 se ressemblent tous : ce sont des **familles de mécaniques inventées par Ascension** —
`Weapon Engravings`, `Animate`, `Mandates`, `Rites`, `Thresh`. Aucun sort Blizzard ne porte ces
noms (vérifié sur les 49 839). **Le mot doit être identique dans tous les sorts de la famille,
donc il faut le fixer une fois pour toutes.** Ce ne sont pas 12 décisions, c'est **5 mots de
vocabulaire à arrêter**.

> ⚠️ **Un défaut trouvé au passage, et il te coûte des retours de joueurs.** Le fichier de
> signalements que tu lis perd de la matière, deux fois :
> - **54 signalements distincts sont écrasés** (16 %). L'outil dédoublonne sur
>   `(type, identifiant, minute)` — mais **les signalements de type « texte » n'ont pas
>   d'identifiant**, donc tous ceux d'une même minute s'effondrent en un seul. Pire cas mesuré :
>   le 19/07 à 19h11, **25 signalements différents réduits à 1** ;
> - **la moitié des 274 lignes conservées est tronquée** (180 caractères dans le fichier,
>   400 au parsing). Le mot « Bloodshatter », que je te cite plus bas, **n'existe nulle part
>   dans le fichier que tu lis** — seulement dans le rapport brut.
>
> Ce sont des joueurs qui ont pris le temps de signaler. C'est le plus petit correctif de tout
> ce programme, et le plus rentable.

#### Les 1 761 Glayna : le chiffre tient, mais l'étiquette est fausse

**2 seulement** ont un officiel Blizzard — **0,11 %**. Et ce n'est pas un défaut de lecture :
sur les 1 761 clés, **1 469 n'existent que sous des identifiants Ascension** (≥ 500000). La
base Glayna est une base de sorts **custom** ; Blizzard n'a jamais traduit ces noms. **Il n'y a
rien à adopter.** (L'instrument a été éprouvé : six vrais noms Blizzard injectés, six retrouvés
avec leur français officiel.)

Trois autres sources ont été testées et écartées, chiffres à l'appui : le **PackFR** (1 588 des
1 761 clés couvertes, mais empoisonné — « Holy Light » y ramène « Heroic Cleave », « Perpetual
Fury » ramène « Colère de Tichondrius ») et le **`.loc` officiel d'Ascension** (traduit à la
machine : « Heroic Strike » → « Grève Héroïque », une grève de travailleurs).

**Mais « 1 759 arbitrages » est faux, et voici pourquoi.** Le fichier prétend ne contenir que
des cas « où nous et Glayna sommes tous deux du français propre ». Le sceptique a trouvé la
faille dans le filtre qui l'a produit (`adopter_noms_glayna.py`, ligne 94) :

```python
if (i > 0 and mot[:1].isupper() and len(mot) >= 4 and mot.lower() in mots_en):
```

Le `i > 0` **laisse passer tout mot anglais en tête de nom**. D'où, classés « français propre à
arbitrer » : « **Guarded** du lumière », « **Buy** temps », « **Feasting** gueule »,
« **Araignée sens** », « Grâce de **earthmother** ». Ce ne sont pas des arbitrages, ce sont des
réparations. Plancher indiscutable mesuré : **28** cas portent une faute de français objective.

Et surtout : **265 des 1 759 ne diffèrent que par la casse, un accent, un trait d'union ou un
article** — « Bière du dieu-roi » contre « Bière du Dieu-Roi », « Faux de moissonneur » contre
« Faux du moissonneur ». **Une seule règle typographique de ta part en règle 265 d'un coup.**

---

#### 🛑 La réponse franche à ta question

Tu écris : *« Si le compte tombe à quelques dizaines, on n'a pas besoin d'un atelier
d'arbitrage du tout. »*

**Tu n'en as pas besoin.** Voilà ce qui reste réellement à décider :

| ce qui reste | volume | qui |
|---|---|---|
| divergences | **0** | — |
| signalements | **5 mots** (familles Ascension) | Dan |
| Glayna — règle typographique | **1 décision** → règle 265 cas | Dan |
| Glayna — les franglais évidents | **≥ 28**, correction auto | personne, c'est mécanique |
| Glayna — vrais choix de vocabulaire | **~1 466** | ⚠️ |

Les 1 466 restants ne sont pas 1 466 décisions à prendre. **C'est une question unique :
« adopte-t-on le vocabulaire de Glayna en bloc, ou garde-t-on le nôtre ? »** Ce sont deux
traductions concurrentes du même corpus de sorts custom, toutes deux du français correct, sans
arbitre extérieur possible. Les traiter un par un, c'est 1 466 fois la même hésitation.

**Ce qu'il faut, ce n'est pas un atelier d'arbitrage. C'est une règle de départage** — par
exemple « à qualité égale, on garde le nôtre, sauf sur les 265 cas typographiques où la règle
tranche ». Une soirée de ta part, pas un chantier collectif.

#### L'échantillon de trente cas réels, tirés au sort

**34 cas au total**, graine fixe, aucun choisi. Les voici tels quels — c'est là qu'on voit à
quoi ressemble une décision restante.

**Glayna (15 tirés sur 1 759, graine 20260801)**

| clé anglaise | nous | Glayna | un bénévole ? |
|---|---|---|---|
| Demon's Breath | Souffle du démon | Souffle démoniaque | **non — Dan** (les deux impeccables et équivalents) |
| Shadowblast | Déflagration d'ombre | Explosion d'ombre | **non — Dan** (engage tout le glossaire sur « blast ») |
| Crimson Quickness | Vivacité cramoisie | Célérité cramoisie | **non — Dan** (Blizzard dit « Rapidité » : contredit les deux) |
| Shadowfang Ritual | Rituel du croc-d'ombre | Rituel de Croc-d'ombre | **non — Dan** (Blizzard dit « Ombrecroc » ailleurs) |
| Falcon Caller | Faucon invocateur | Appeleur de faucon | **non — Dan** (les deux mauvais, il faut inventer) |
| Splash Potion | Potion éclaboussante | Potion à éclaboussures | **douteux** (il faut voir le sort en jeu) |
| Ashen Priest | Prêtre des cendres | Prêtre cendré | **douteux** (un seul précédent Blizzard) |
| Ramhorn Rage | Rage de corne-de-bélier | Rage de Corne-de-bélier | **oui** — typographie pure |
| Harvester's Scythe | Faux de moissonneur | Faux du moissonneur | **oui** — un article |
| Pouch of Stardust | …poussière d'étoile | …poussière d'étoiles | **oui** — un pluriel |
| Perpetual Fury | Furie perpétuelle | Fureur perpétuelle | **oui** — Blizzard dit « Fureur » sur 83 noms |
| Spider Senses | **Araignée sens** | Sens d'araignée | **oui** — réparation, pas arbitrage |
| Feasting Maw | **Feasting gueule** | Gueule vorace | **oui** — réparation |
| Buy Time | **Buy temps** | Gagner du temps | **oui** — réparation |
| Earthmother's Grace | **Grâce de earthmother** | Grâce de la Terre-Mère | **oui** — réparation |

**Sur 15 tirages au hasard : 8 sont mécaniques ou typographiques, 5 demandent Dan, 2 sont
douteux.** C'est la mesure la plus parlante du bloc.

**Signalements (12 sur 12 — la population entière)**

Tous de la même nature : `Weapon Engravings` (3 fois, dont un où le sort est traduit mais pas la
mécanique dans son corps), `Animate` (2 fois, un joueur y est revenu 9 jours plus tard),
`Mandates`, `Rites`, `Thresh`/`Bloodshatter`, `Decaying Collosi` (qu'Ascension **écrit mal** —
faut-il recopier la faute ?), `Slagstone`, `Horn` (cor ? corne ? nom d'objet ? — impossible sans
voir le jeu), `Shudder Scythe` (le seul où **deux français maison** s'affrontent : la base dit
« Faux frémissante », l'écran dit « Faux de frémissement »).

**Divergences (7 sur 7 — population entière, et hors des 121)**

Ce sont les résidus vivants d'aujourd'hui, et ils sont **tous la même chose** : « bassin
Arathi » contre « bassin **d'**Arathi ». Un bénévole peut trancher — la décision est déjà au
glossaire, c'est l'outil qui ne la connaît pas. *(Détail savoureux : « Achèvemement » est une
faute de frappe des deux côtés — elle vient de l'officiel Blizzard.)*

### BLOC B — la traduction : le chiffre de départ était faux, et pas un peu

Tu avais raison d'exiger une relance avant de compter. Mais **une relance ne suffisait pas** :
l'outil lui-même compte mal. Voici ce que j'ai trouvé, dans l'ordre.

#### 1. Le mode `--apercu` rend un zéro qui ne veut rien dire

Premier passage, `clarifier_retours_joueurs.py --apercu` : **« à traiter » = 0 partout**. J'ai
failli t'annoncer que l'arriéré avait disparu.

C'est faux, et c'est structurel. En mode aperçu le code fait `g = None` et met
`statut = "?"` sans jamais ouvrir les bases (ligne 441 et 449). Or seul le statut `"absent"`
compte comme « à traiter ». **La colonne est donc toujours à zéro en aperçu, quoi qu'il
arrive.** Ce n'est pas un résultat, c'est une colonne qui ne peut pas être remplie.

#### 2. Le vrai passage donne 25 737 — le double d'il y a sept jours

| | 25/07 | 01/08 |
|---|---|---|
| rapports lus | — | **3 761** |
| entrées uniques | ~12 700 | **32 087** |
| **à traiter** | ~12 700 | **25 737** |

#### 3. Sauf que 25 737 est faux aussi — l'outil ne charge que 8 bases sur 27

`diagnostiquer_signalements.py` ligne 65 déclare la liste des bases à charger :

```python
BASES_TOUTES = ("DB_Sorts.lua", "DB_Objets.lua", "DB_Creatures.lua",
                "DB_Divers.lua", "DB_TextesPNJ.lua", "DB_Gossip.lua",
                "DB_Pages.lua", "DB_Libelles.lua")
```

Huit. Le `.toc` de l'addon en charge **vingt-sept**. Manquent notamment :

- **`DB_Communaute.lua`** — le fichier où `ingerer_recolte.py` écrit **précisément les
  traductions issues des retours joueurs**. L'outil qui compte ce qui reste à faire ne lit pas
  le fichier où l'on range ce qui est fait ;
- `DB_Quetes.lua` et `DB_QuetesObjectifs.lua` — d'où le « 7 213 quêtes / 7 213 à traiter »,
  un 100 % obtenu contre une base **jamais ouverte** ;
- `DB_SortsCorrections.lua`, `DB_SortsNoms.lua`, et 15 autres.

**J'ai refait le compte avec les 27 bases, dans l'ordre de chargement du `.toc` :**

| type | récoltés | l'outil dit | **réellement** | écart |
|---|---|---|---|---|
| Sorts | 5 974 | 5 697 | **4 395** | −1 302 |
| Divers | 4 168 | 3 852 | **3 851** | −1 |
| Gossip | 5 124 | 5 056 | **1 959** | **−3 097** |
| Textes PNJ | 4 382 | 3 542 | **1 652** | **−1 890** |
| Quêtes | 7 184 | 7 213 | **1 329** | **−5 884** |
| Pages | 202 | 196 | **196** | 0 |
| Objets | 502 | 181 | *non repris* | |
| **TOTAL** | | **25 737** | **≈ 13 382** | **−12 355** |

**L'outil surcompte de 48 %.** Près de 12 400 entrées sont annoncées « à traduire » alors
qu'elles sont déjà traduites — la plupart par les contributions déjà ingérées.

> Réserve honnête sur les quêtes : je teste « la quête porte-t-elle un texte de progression
> (champ `P`) ? ». Un joueur peut avoir signalé une *autre* ligne de la même quête. **1 329 est
> donc un minorant** pour les quêtes. Je ne sais pas de combien sans une mesure plus fine.

#### 4. Le vrai poids de travail

Sur les quatre types où la clé EST le texte anglais (donc directement traduisibles) :

| type | restants | caractères anglais | longueur médiane |
|---|---|---|---|
| Divers | 3 851 | 242 976 | 44 |
| Textes PNJ | 1 652 | 181 632 | 97 |
| Gossip | 1 959 | 58 108 | 25 |
| Pages | 196 | 24 767 | 85 |
| **TOTAL** | **7 658** | **507 483** | |

**≈ 281 pages de roman.** Et c'est court : la médiane du gossip est de **25 caractères** —
« Yes. », « <Continue> », un titre. Ce n'est pas de la littérature, c'est du volume.

Les 4 395 sorts sont à part : **4 827 des sorts signalés ne sont pas du tout dans notre base**
(seulement 870 y sont sans description française). On ne peut pas traduire un sort absent —
c'est un problème de **récolte**, pas de traduction.

---

#### Peut-on découper par THÈME ? — mesuré, et la réponse est « pas aujourd'hui »

Tu dis que c'est décisif, et je suis d'accord : traduire des phrases isolées hors contexte
donne de mauvaises traductions. J'ai donc cherché de quoi rattacher chaque entrée à une zone,
une classe, un donjon. **Il n'y a rien.**

- **Le rapport brut du joueur ne porte aucun contexte.** Une ligne de récolte, c'est
  `[Gossip] <texte anglais>` — un type et une clé. Pas de zone, pas de PNJ, pas de coordonnées.
- **`gisement_brut.json` est un dictionnaire plat** anglais → français, 5 141 entrées, **sans
  aucune provenance**.
- Une entrée de quête en base porte `A, D, O, T, TE, P, R, F, OT` — **aucun champ de zone**.

**Mais la matière existe, ailleurs et inexploitée** : `sources\` contient le
`TDB_full_world_335` (la base de données du serveur — quêtes, PNJ, zones, points d'apparition)
et les `dbc`. De quoi reconstituer quête → zone et sort → classe.

**Ma recommandation, franche : ne découpe pas par thème tout de suite.** Il faudrait d'abord
construire la jointure TDB, et ce programme dit — à raison — de ne rien construire. Mais
**c'est la première chose à bâtir si tu veux des lots thématiques**, avant l'atelier lui-même.
Sans elle, tout découpage sera arbitraire.

**Le contournement disponible tout de suite**, qui vaut mieux que rien : découper **par type**.
Un type est déjà une forme de cohérence — les menus de dialogue se ressemblent entre eux, les
textes de PNJ aussi. Et surtout **par fréquence** : la colonne « nb de rapports » existe déjà.
Les entrées vues 100 fois sont celles que tous les joueurs croisent. **Le premier lot devrait
être « les 200 phrases les plus vues », tous types confondus** — le meilleur rapport
effet-visible / effort, et un excellent lot d'essai pour un premier bénévole.

#### Combien de lots, de quelle taille ?

Une soirée de bénévole ≈ 2 heures. Sur du texte court et répétitif de jeu, avec le glossaire
sous la main, compte **150 à 250 entrées courtes**, moins si les textes sont longs.

| | |
|---|---|
| taille de lot | **200 entrées**, ou **12 000 caractères anglais** — la première limite atteinte |
| nombre de lots | **≈ 45** pour les 7 658 entrées directement traduisibles |
| les 4 395 sorts | **hors lots** — récolte d'abord |

Quarante-cinq lots, c'est un chiffre qui se tient : cinq bénévoles à un lot par semaine, c'est
**deux mois**. C'est un projet fini, pas un puits sans fond. **Dis-le aux bénévoles** — « il
reste 45 soirées de travail » recrute mieux que « il reste 12 000 entrées ».

#### Sous quel format, et comment ça revient ?

Le chemin de retour **existe déjà** et personne n'a besoin d'être informaticien :

- **il sort** ce que `clarifier_retours_joueurs.py` écrit déjà : un tableau Markdown, une ligne
  par entrée, colonnes `texte anglais | traduction`. Ça s'ouvre dans le Bloc-notes, ça se lit
  dans Discord, et ça se rend en tableau sur GitHub. Une colonne à remplir, rien d'autre ;
- **il revient** par `outils/ingerer_recolte.py`, qui écrit dans `DB/DB_Communaute.lua` — un
  fichier de surcharge qui **survit aux régénérations** des bases (même principe que
  `DB_SortsCorrections`). Il refuse déjà les doublons et écarte les textes déjà français.

Il manque une seule pièce : **`ingerer_recolte.py` lit les rapports, pas un lot rempli à la
main.** C'est la plus petite chose à écrire de tout ce programme — et je ne l'écris pas ici,
c'est un chantier 3.5.

> ⚠️ Un piège à ne pas ignorer : le Markdown utilise `|` comme séparateur de colonnes, et les
> textes de jeu contiennent des `|cFFFFFF00` (codes couleur) et des `|T...|t` (icônes) **à
> foison**. Un lot au format tableau les cassera. Le format de sortie doit soit échapper les
> barres, soit ne pas être un tableau. C'est exactement le genre de détail qui fait échouer un
> premier lot et décourage un bénévole.

#### Deux personnes peuvent-elles prendre le même lot sans le savoir ?

**Aujourd'hui, oui, et rien ne l'empêcherait.** Il n'existe aucune trace de qui travaille sur
quoi : `_INDEX.md` dit ce qui a été *trié*, jamais ce qui est *pris*.

Ce qu'il faut, et qui ne demande aucune plateforme : **un lot est réservé au moment où il est
créé, pas quand il est rendu.** Concrètement, le nom du fichier porte le preneur —
`lot-07_gossip_prenom.md`. Un lot sans preneur n'existe pas. Le dossier des lots devient alors
lui-même la liste des réservations : impossible d'oublier de la tenir à jour, puisque c'est le
même geste.

C'est le motif que tu cites au BLOC E, appliqué ici : **une liste qui est la réalité**, plutôt
qu'une liste qui la décrit et qui dérive.

---

### BLOC C — ce qu'une contribution doit franchir : **rien**. Et on ne peut pas annuler un lot.

Les deux réponses sont mauvaises, et elles sont mesurées.

#### Le glossaire ne voyage pas — il ne sort même pas de son dossier

**Aucun programme du projet n'ouvre `GLOSSAIRE.md`.** Le nom du fichier apparaît une seule fois
sur tout `D:\AscensionFR`, dans un commentaire. Le vocabulaire est **recopié à la main dans deux
endroits du code** qui ne se connaissent pas : `appliquer_vocabulaire.py` (75 règles) et
`glossaire_jeu.py` (66 paires).

Conséquence mesurée : **14 des 27 termes que tu as arbitrés ne sont appliqués par aucun outil** —
Golden, Lucky, Darkmoon, Unleash, Soulbound, Stormwind, Booty Bay, Stranglethorn…

Et ça se voit dans ce qui est livré. Sur 515 231 valeurs françaises :

| forme interdite par le glossaire | occurrences | **phrases distinctes** |
|---|---:|---:|
| Darkmoon (→ Sombrelune) | 441 | **56** |
| Stormwind (→ Hurlevent) | 285 | **176** |
| Booty Bay (→ Baie-du-Butin) | 117 | **67** |
| JcJ (→ PvP) | 26 | 26 |
| Manastorm, Stranglethorn | 34 | 26 |
| **total** | **903** | **351** |

> Correction du sceptique, importante : la première mesure annonçait « 891 textes ». Ce sont des
> **occurrences**, pas du travail. Les 441 « Darkmoon » viennent de **56 phrases** recopiées sur
> des milliers d'objets. **Le vrai travail, c'est 351 phrases.** Et ce n'est pas une découverte :
> ton `GLOSSAIRE.md` chiffre déjà lui-même ses restes (« 266 textes à basculer », « 510 textes en
> JcJ/JcE à aligner »). **Ce qui manque n'est pas la connaissance du problème, c'est un outil qui
> morde.**

**Le même jour, le banc de santé affiche « 0 ROUGE, 0 avertissement ».** Ce n'est pas un reproche
au banc — il n'a jamais été chargé de ça. C'est la démonstration que **le vocabulaire n'est
surveillé par rien.**

**Ce que je propose (décrit, pas construit) :**

1. **Renverser le sens de lecture.** Le tableau « Termes fixés » est *déjà* de la donnée : trois
   colonnes propres en Markdown. Ajoute deux colonnes que tu remplis sans effort (la **garde
   anglaise** et la **forme interdite**), et les outils lisent le `.md` au lieu d'en porter des
   copies. Tu continues d'écrire dans le seul fichier que tu écris déjà.
2. **Le lot part avec une fiche, pas avec le glossaire entier.** Uniquement les termes
   **présents dans les textes anglais de ce lot**, et pour chacun **la traduction officielle
   Blizzard déjà pré-remplie**. C'est ça, faire voyager la règle « l'officiel gagne » : pas une
   phrase à comprendre, **une case déjà remplie qu'il suffit de ne pas toucher**. Le contributeur
   ne décide que là où la case est vide.
3. **Une case « pourquoi » obligatoire dès qu'on s'écarte de l'officiel.** C'est la seule chose
   qu'il ait à rédiger, et c'est exactement ce que tu dois arbitrer. Le registre existe déjà :
   `divergences_officielles_decisions.json` porte 81 décisions au format
   `{nous, officiel, regle, verdict}`. **Il faut juste que les contributeurs écrivent dedans.**

#### Les contrôles existants regardent le produit fini, jamais la matière première

C'est **le** fait du bloc. Sur 34 bancs :

| ce qu'ils lisent | nombre |
|---|---:|
| l'addon **généré** | 25 |
| les traductions **source** (`traductions/*.json`) | **1** |
| **les deux** | **0** |
| ni l'un ni l'autre | 8 |

Une contribution modifie la matière première. **Rien ne la regarde.**

Et le seul banc qui lise la matière première — `banc_double_essai.py` — **n'est lancé par
personne** (voir plus bas).

#### La porte d'entrée d'un lot ne ferme pas

`outils/fusionner_lots.py` est **la seule porte d'entrée d'un lot**. Il :

- **écrit** les `traductions/*.json` **avant** de rapporter les problèmes ;
- n'a **aucun `return`** dans son `main()` (vérifié par analyse du code), qui est appelé nu ;
- **sort donc toujours en 0.**

Les codes techniques cassés (`$n`, `|cff…|r`, `%s`) sont **imprimés dans la console, jamais
bloquants**. Un lot avec 200 codes cassés entre exactement comme un lot propre.

**Réponse à ta question « une contribution peut-elle contourner le contrôle ? » : il n'y a rien
à contourner.** Le chemin est `lot → fusionner_lots (sort toujours 0) → traductions/*.json →
mise_a_jour → addon généré → les 25 bancs`. Les bancs arrivent **après** la génération et ne
jugent que le Lua. Les 351 phrases fautives en sont la preuve vivante.

#### 🛑 Annuler un lot : **on ne peut pas**

Tu dis que si la réponse est « on ne peut pas », c'est un défaut à corriger **avant** d'ouvrir.
C'est bien la réponse.

- **Aucune provenance, nulle part.** Les 99 fichiers `traductions/*.json` (690 Mo) ont été lus
  intégralement, en cherchant toute clé `auteur / lot / date / provenance` jusqu'à trois niveaux.
  **Zéro.** *(Ce n'est pas un zéro d'instrument : le même détecteur repère bien `auteur` et `lot`
  sur une entrée fabriquée.)* Le format est un dictionnaire plat, `{"10": {"N": "Sifflet…"}}` —
  **il n'y a physiquement pas de place** pour dire d'où vient une entrée.
- **Git ne peut pas défaire un lot, parce qu'il n'y a pas de lots dans git.** 16 commits en tout,
  8 touchent `traductions/`, et ils s'appellent « Programme 4 », « Programme 5 ». Le commit
  `b68ca06` change à lui seul **58 837 lignes** de `objets.json` et couvre cinq chantiers. Le
  défaire, c'est défaire cinq chantiers.
- **Les instantanés fins ne sont pas archivés.** 59 fichiers `*_avant_*.json` existent — et
  `.gitignore` ligne 28 les exclut. **Ils n'existent que sur ton disque.**
- Et rien de tout ça ne défait ce qui est **déjà chez les joueurs**.

**Mais le terrain est excellent, et c'est la bonne nouvelle.** `ecriture_sure.py` écrit tout le
JSON en `indent=1, sort_keys=True` : **une entrée = ses propres lignes, dans un ordre stable**.
J'ai mesuré l'interférence entre commits — un lot ultérieur a-t-il retouché les mêmes champs ?

| fichier | champs touchés par commit | **retouchés plus tard (pire cas)** |
|---|---|---|
| `quetes.json` | 233 à 1 941 | **0** |
| `sorts.json` | 83 à 8 856 | **42** |
| `objets.json` | 2 316 à 38 997 | **704** |

**Plus de 99 % d'un lot serait annulable mécaniquement.** Ce n'est pas git qui bloque, c'est
**l'absence d'une unité « lot »**.

**Et le mécanisme existe déjà — sur un seul chantier.** `purger_objets_par_entree.py` fait
exactement ce qu'il faut : il écrit un **journal nominatif suivi par git** (6,4 Mo, 23 849
entrées, `{id, en, fr_retire, raison}` — **la valeur retirée est dans le journal**), il offre
`--restaurer`, et il refuse d'écrire un journal quand rien n'a bougé. **Il suffit de le
généraliser.**

> Une faille dedans, à connaître : ce journal cite une sauvegarde de secours qui est
> **gitignorée**. Le journal, lui, est complet et versionné — c'est lui qui doit faire foi. La
> nouvelle mécanique ne doit **pas** dépendre d'une sauvegarde hors git.

#### Où s'applique le motif `verifier_greffes` (ta question)

| liste | confrontée à | rouge si |
|---|---|---|
| les 27 termes du **glossaire** | ce que les outils appliquent **et** ce qui traîne dans les données | un terme arbitré n'est appliqué par personne (**14 aujourd'hui**), ou une forme interdite survit (**351 phrases**) |
| le **journal de lot** | ce qui est vraiment dans `traductions/*.json` | le journal dit 300 et il en manque 12. *Un bouton « annuler » menteur est pire que pas de bouton.* |
| `BANCS_ATTENDUS` | les fichiers `verifier_*.py` du disque | **voir le BLOC D — c'est déjà cassé** |

---

### BLOC D — l'ouverture du code : le préalable n'est pas de publier, c'est de réparer

#### 🛑 Le banc phare du projet sort VERT en n'ayant rien mesuré

C'est la découverte la plus grave du programme, et **je l'ai revérifiée moi-même dans le code.**

Le **banc moteur** est l'étape n° 1 du banc de santé, celle au seuil de 1 200 échecs. Sa
dernière ligne (`reparer_alignement_sorts.py`) est :

```python
return 0 if n_echecs <= seuil else 1
```

| chez Dan | sur un poste sans les bases |
|---|---|
| `49283 entrées, 317 échecs` → **code 0, vert** | `0 entrées, 0 échecs` → **code 0, vert** |

**Il ne sait pas distinguer « 0 échec sur 49 283 » de « 0 échec sur rien ».** Un contributeur
lancerait le garde-fou principal du projet, verrait vert, et n'aurait mesuré **rien du tout**.
C'est exactement le piège que ce projet traque depuis une semaine, **présent dans son gardien
principal**. Une ligne de code le répare.

#### 🛑 Et deux alarmes qui crient sans rien bloquer

Vérifié dans le code : la ligne de sortie de `verifier_tout.py` est

```python
return 1 if (fautes or suspects or manquants or desaccord_version
             or orphelines or fantomes) else 0
```

La liste `serrees` — remplie aux lignes 178 et 187 — **n'y est pas**. Donc :

- **« UN SEAU NE COMPILE PAS »** s'affiche… et le code retour est **0**. C'est pourtant la pire
  panne du projet, celle que `mesurer_constantes.py` décrit ainsi : *« Core.lua avale l'échec et
  les textes de ce seau restent anglais pour toute la session, sans un mot. »*
- **« ne jamais publier ça ! »** (webhook vide côté privé) s'affiche… code retour **0**. C'est
  la panne du 19/07 — « plus aucun rapport n'arrivait, personne ne l'a vu pendant des heures ».
  **Elle repasserait aujourd'hui à l'identique.**

Le sceptique a éprouvé les trois cas avec des bases témoins : seau qui compile → 0 ; seau qui ne
compile pas → **0** ; faute de syntaxe franche → 1. *(Son instrument mord ; l'outil, non.)*

> **À décharge, et c'est important pour ne pas s'alarmer :** la **release**, elle, resterait
> bloquée — `construire_zip_release.py` recompile tout le zip, seaux compris, et refuse. **Le
> trou est dans le banc quotidien, pas dans la publication.**

#### Le banc de santé promet un contrôle qui n'existe pas

Son commentaire (lignes 59-61) annonce : *« Un banc absent de cette table qui existe sur le
disque est signalé »*. **Ce code n'existe pas** — la boucle ne parcourt que la table, il n'y a
aucun balayage du dossier.

**35 bancs sur le disque, 19 dans la table, 15 lancés par personne** — dont `verifier_objets`,
`verifier_quetes`, `verifier_sorts`, et surtout **`banc_double_essai`, le seul banc du dépôt qui
regarde la matière première.**

C'est **littéralement** le défaut « OUBLIÉES » que `verifier_greffes.py` a été écrit pour
empêcher — **présent chez le gardien lui-même.**

#### Un contributeur peut-il éprouver son travail ? — **non, à trois titres**

| ce qu'il a | bancs utilisables |
|---|---|
| **aujourd'hui** (dépôt public seul) | **0 / 19** — les bancs ne sont pas publiés |
| + le code de l'addon *et le chemin de Dan recréé à l'identique* | 13 / 19 |
| + les bases prises dans le zip de Release | 15 / 19 |
| + deux lignes décrochées de l'arbre privé | **17 / 19** — le plafond |

> **Désaccord entre mes deux mesures, et je le tranche.** Le premier agent annonce 13/19 ; le
> sceptique a redirigé le chemin vers un disque inexistant et obtenu **14 échecs sur 14**. Ils ne
> testent pas la même chose : le 13/19 suppose que le contributeur **recrée exactement**
> `D:\AscensionFR\WOW_Priv\resources\ascension-live\…`, ce qu'aucune autre machine ne peut faire.
> **Le chiffre honnête pour un vrai contributeur est 0** — et la bonne nouvelle du sceptique,
> c'est qu'ils échouent **bruyamment** (`FileNotFoundError`, code 1), pas en vert.

La serrure est une seule ligne, répétée : **15 des 19 bancs** commencent par
`ADDON = r"D:\AscensionFR\WOW_Priv\..."`. **92 fichiers sur 157** dans `outils/` portent un
chemin machine en dur. **Une variable d'environnement avec repli sur le chemin actuel règle les
15 d'un coup, sans rien casser chez toi.**

*(La PR #4 n'aide pas ici : son arbre n'a pas de dossier `outils/`. Elle rend le Hub portable,
pas le pipeline.)*

#### Et le Compagnon déjà publié n'est pas reconstructible

Trouvé par le sceptique, et c'est plus bloquant que tout le reste :

- le `.spec` public fait `datas = [('assets', 'assets')]` — il embarque le dossier entier ;
- privé : **195 fichiers** dans `compagnon/assets` (tous les décors, `catalogue_hub.json`) ;
- public : **2 fichiers** (`logo.ico`, `logo.png`) ;
- et le code publié référence `assets/hub` **8 fois**.

**Un contributeur qui suit la recette publiée obtient, au mieux, un Hub sans interface.**

#### Ce que le dépôt public devrait gagner — et ne jamais contenir

| à ajouter | pourquoi |
|---|---|
| le code de l'addon (26 fichiers, ~1 Mo) | historique **propre**, vérifié au programme 13 |
| les bancs (`verifier_*.py`, ~300 Ko) | sans eux, publier le code ne sert à rien |
| **une licence** | il n'y en a **aucune**, nulle part. Sans licence, personne n'a le droit de réutiliser le code |
| les `assets/hub` manquants | sinon rien ne se compile |

| à ne jamais publier | raison mesurée |
|---|---|
| le **webhook** | déjà neutralisé par déclaration. Et le balayage de l'historique privé rend **9 motifs, dans 6 versions successives** du même fichier — la démonstration chiffrée que `WorkFlow` ne doit jamais avoir de distant |
| les **7 439 rapports joueurs** | données reçues de tiers ; la règle « ne jamais citer les joueurs » s'applique |
| **`sources/`** (998 Mo) | extrait des archives Blizzard et Ascension — ce n'est pas notre travail |
| **`cache_db/framexml_client`** (11 192 fichiers) | c'est le code d'interface **de Blizzard** |
| les bases `DB/` (114 Mo) | générées — **et déjà publiques** : le zip de release les contient. Un contributeur les prend par la Release, pas par git |

*Deux détails : le dépôt public expose `if os.path.isdir(r"D:\AscensionFR\WorkFlow")` — ton
chemin de disque est publié (un fichier témoin ferait le même travail) ; et le `.bak` livré aux
joueurs en 3.4.0 **est déjà corrigé** dans le zip 3.4.1 (58 entrées contre 82).*

#### Ce qu'il faut écrire — le README est périmé, vérifié passage par passage

Ce n'est pas « un peu vieux », **il décrit un autre programme** :

- **le mot « Hub » apparaît 0 fois** ; « compagnon » apparaît 13 fois et désigne toujours
  `traducteur_fr.py`, le vieux démon de traduction (ligne 660 : « le compagnon utilise Google
  Translate ») ;
- **la marche à suivre quotidienne est morte** : ligne 18, double-cliquer « Traduction FR -
  Ascension » → un `.bat` qui n'existe plus que dans `archive/racine-2026-07/` ;
- **l'arborescence a la mauvaise racine** (`traduction/` au lieu de `WorkFlow`) ;
- « **les deux addons** » — il y en a cinq ;
- occurrences de `banc_sante`, « Atelier », `depot_github`, `publier_github`, « secrets »,
  « greffe », « webhook », « 3.4 » : **0 chacune** ;
- il cite **23 outils sur 155**.

Il faut : un **`CONTRIBUER-CODE.md`** (prérequis exacts — `lupa.lua51`, pas le lupa par défaut —,
la commande unique qui joue les bancs portables, et surtout **la liste des bancs qu'un
contributeur ne peut pas juger, avec la raison**), un **`ARCHITECTURE.md`** d'une page sur les
trois dépôts, une **licence**, et **archiver** le README actuel plutôt que le rafistoler.

---

### BLOC E — la carte de la séquence de publication

**23 gestes. 8 automatiques, 6 semi-automatiques, 9 de mémoire pure.** Sur les 9, **7 peuvent
livrer une régression silencieuse.**

#### Les gestes, dans l'ordre

| # | geste | nature |
|---|---|---|
| 1 | décider de sortir, et le numéro | **mémoire** *(exprès)* |
| 2 | lancer l'Atelier (7 étapes) | semi-auto |
| 3 | monter `## Version:` dans le `.toc` **vivant** | **mémoire** — aucun script ne l'écrit |
| 4 | monter `VERSION_COMPAGNON` | **mémoire** — aucun script ne l'écrit |
| 5 | reconstruire les décors du Hub | **mémoire** |
| 6 | passer `pyflakes` | **mémoire** — le mot n'apparaît nulle part dans le code |
| 7 | `PyInstaller AscensionFR_Hub.spec` | semi-auto |
| 8 | ⚠️ **copier `Hub.exe` → `Compagnon.exe`** | **mémoire** |
| 9 | vérifier que l'exe démarre, tester en jeu | **mémoire** *(exprès)* |
| 10 | `synchroniser_depot_public.py --appliquer` | semi-auto |
| 11 | commiter le dépôt public | **mémoire** *(contrôlé en aval)* |
| 12 | ⚠️ **pousser le dépôt public** | **mémoire** |
| 13 | écrire la note de version | **mémoire** *(exprès)* |
| 14 | `publier_github.py <version> "<note>"` | semi-auto |
| 15-19 | ↳ les cinq barrières : trois numéros, arbre publié, zip, fraîcheur de l'exe, existence | **automatiques** |
| 20 | ↳ `gh release create --latest` — **irréversible** | automatique |
| 21 | écrire l'annonce et le patch note | **mémoire** — *rien n'existe pour la 3.4* |
| 22 | `publier_discord.py --envoyer` — **irréversible** | semi-auto |
| 23 | vérifier les releases des 4 addons du catalogue | **mémoire** — aucun banc ne les regarde |

#### Les 7 qui peuvent livrer une régression silencieuse, du plus grave au moins grave

**1. ★★★ La copie de l'exe (geste 8)** — et c'est **pire** que ce que tu décris.

Il y a deux cas, pas un :

- **copie périmée** → *attrapée*. La barrière de fraîcheur compare les dates et refuse.
- **copie jamais faite** → **rien du tout.** `publier_github.py` fait
  `if os.path.exists(EXE_COMPAGNON)`. Sinon il affiche entre parenthèses *« (Compagnon absent —
  release avec le zip seul.) »*, la liste des livrables se réduit au zip, le contrôle d'existence
  passe (le zip existe), et **`gh release create` part quand même, code retour 0.**

**La publication réussit, sans le Compagnon, et l'outil se dit content.**

Et le garde-fou de fraîcheur compare des **dates**, pas des contenus — or **une copie rafraîchit
toujours la date** (éprouvé : un fichier daté de 2001, copié, ressort daté d'aujourd'hui). Si tu
copies le *mauvais* exe, **il est aveugle**. Rien ne lit le numéro de version **à l'intérieur**
de l'exe, nulle part.

> **Trou voisin, mesuré :** la barrière de fraîcheur ne parcourt que `compagnon/`. Or
> `outils/parser_wdb.py` est **embarqué dans l'exe**. Le modifier périme l'exe **sans que rien ne
> le voie**. *(Les deux copies sont identiques aujourd'hui — c'est une chance, pas un contrôle.)*

**2. ★★★ Le `git push` du dépôt public (geste 12)** — c'est l'incident du 29/07.

La barrière lit `git status --short`. **Cette commande ne dit rien d'un commit non poussé.**
Témoin planté : dépôt en avance d'un commit → `git status --short` rend **une chaîne vide**,
`git status -sb` rend `## main...origin/main [ahead 1]`. Et `publier_github.py` **n'appelle
jamais `git`** : le tag part nu à `gh`, sans `--target`. **Le commit sur lequel le tag atterrit
n'est ni choisi ni relu par la chaîne.**

*Le correctif tient en une ligne : `git rev-list --count origin/main..main` doit valoir 0.*

**3. ★★ `pyflakes` non passé (geste 6)** — PyInstaller compile sans broncher un nom indéfini.
C'est la panne qui a valu le hotfix 3.1.0. Aucun garde-fou automatique.

**4. ★★ L'ordre entre le numéro et la construction (3-4 contre 7)** — si l'exe est construit
avant de monter `VERSION_COMPAGNON`, il annonce l'ancien numéro face au nouveau tag →
**boucle de mise à jour infinie sur 274 machines**. Les trois barrières de version lisent les
**sources**, jamais l'exe : elles seraient toutes vertes.

**5. ★ Les décors non reconstruits (geste 5)** — `verifier_decors.py` existe et **n'est dans
aucune liste**. *Régénérer est protégé ; ne pas régénérer ne l'est pas.*

**6. ★ Les releases des 4 addons du catalogue (geste 23)** — le banc du Hub travaille sur un
catalogue **inventé**. Le catalogue réel n'est jamais confronté à GitHub. Le joueur clique
« installer » et il ne se passe rien.

**7. ★ Le lien collé dans les textes Discord (geste 21)** — atténué (le lien `releases/latest`
est permanent), mais **aucun texte n'existe pour la 3.4**.

*Et un huitième, semi-automatique : si l'Atelier n'a jamais tourné, `atelier_sante.json` absent
n'est qu'un **avertissement**. On peut publier avec des bases figées sans rien voir passer.*

#### Scriptable sans risque / manuel exprès

| à scripter | comment |
|---|---|
| **8 — la copie** | deux corrections : sortir **directement au bon nom** (`name='AscensionFR_Compagnon'` dans le `.spec` — le piège disparaît **à la racine**) ; et remplacer la date par une **comparaison de contenu** : lire le `VERSION_COMPAGNON` embarqué et exiger qu'il égale le tag. *Une date ment ; un contenu, non.* |
| **12 — le push** | une ligne : `git rev-list --count origin/main..main` = 0 |
| **6 — pyflakes** | l'ajouter au banc de santé. Coût nul, mord immédiatement |
| **3-4 — les numéros** | un `poser_version.py 3.4.2` qui écrit les deux endroits d'un coup |
| **5 / 23 / `parser_wdb`** | inscrire les décors au banc ; un banc qui interroge les 4 URL du catalogue ; ajouter `parser_wdb` à la fraîcheur |

| à laisser manuel, **exprès** | pourquoi |
|---|---|
| 1 — décider de sortir | c'est un jugement, pas un calcul. Et la règle « jamais sans le go de Dan » vit là |
| 9 — tester l'exe en jeu | aucun banc ne remplace « je l'ai lancé, ça marche ». Dernier filet avant 274 machines |
| 13 / 21 — note de version, textes Discord | ils s'adressent à des humains |
| 20 — `gh release create` | **irréversible**. Le lancement doit rester délibéré — c'est le cas, et c'est bien |
| 22 — l'annonce `@everyone` | irréversible et elle ping tout le serveur. Le double verrou actuel est le bon dosage |

#### Le mot juste sur cette chaîne

Elle a **beaucoup** de garde-fous, et ils sont bons — les trois numéros, l'arbre publié, la
double barrière du zip, la compilation Lua 5.1, le balayage de secrets, le contrôle d'intégrité
chez le joueur. **Presque tous ont été posés après une panne réelle.**

Ce qui reste ouvert n'est pas un manque de garde-fous. Ce sont **deux gestes de transport** —
copier un fichier, pousser un dépôt — qui ne portent **aucune décision, aucun jugement**, et que
personne n'aurait jamais dû avoir à retenir. **Ce sont exactement les deux qui ont déjà mordu.**

*Note utile : un garde-fou t'attend déjà. Le `.toc` et `compagnon.py` sont à 3.4.1, le dépôt
public est resté à 3.4.0 — **publier maintenant serait refusé**. Celui-là fonctionne pour de vrai.*

---

### 🛑 Mon avis franc : par quoi commencer, et ce qui ne vaut pas le coup

#### Ce qui ne vaut pas le coup

- **L'atelier d'arbitrage.** Il ne reste ni 1 762 ni 121 décisions : il reste **5 mots de
  vocabulaire, 1 règle typographique, et 1 question de fond** (adopte-t-on Glayna en bloc ?).
  C'est une soirée pour toi, pas un chantier collectif.
- **Le découpage thématique des lots**, tout de suite. La matière existe (`TDB_full_world`) mais
  la jointure est à construire. Ne commence pas par là.
- **Rafistoler le README.** Il décrit un autre programme. Archive-le et écris une page courte.
- **Ouvrir la contribution au code maintenant.** Rien ne se compile (2 fichiers d'`assets` sur
  195), rien ne s'éprouve (0 banc utilisable), et le banc phare sort vert sur du vide. On
  donnerait un dépôt inutilisable, et tu hériterais de 100 % du contrôle.

#### Par quoi commencer — quatre gestes, dans cet ordre

**1. Faire mordre trois garde-fous qui crient sans arrêter.** *Trois lignes de code.*
Le banc moteur doit **rougir sur zéro entrée** ; `verifier_tout.py` doit compter `serrees` dans
son `return` ; `banc_sante.py` doit **balayer son propre dossier** (15 bancs dorment). Sans ça,
tout le reste est bâti sur un thermomètre qui affiche toujours 37°. **C'est vrai même si tu
n'ouvres jamais le projet à personne.**

**2. Réparer les deux gestes de transport.** *Le `.spec` qui sort au bon nom, et une ligne sur le
push.* Ce sont les deux seuls qui ont déjà mordu, et ils ne portent aucune décision.

**3. Récupérer les retours de joueurs qu'on perd.** *Ajouter le texte à la clé de
dédoublonnage.* 54 signalements écrasés, la moitié des autres tronqués. Ce sont des gens qui ont
pris le temps.

**4. Ensuite seulement, la traduction** — c'est là qu'un bénévole sert vraiment. **Un seul lot
d'essai** : les 200 phrases les plus vues, tous types confondus, avec la fiche de vocabulaire
pré-remplie. Une personne. Tu regardes ce qui revient, et tu décides ensuite.

#### La chose que je retiens de tout le programme

Trois fois de suite, sur trois blocs indépendants, la même panne : **`--apercu` qui rend un zéro
impossible**, **le compteur qui ignore la base où l'on range ce qui est fait**, **le banc phare
qui sort vert sur du vide**. Et à chaque fois, l'affichage était bavard et rassurant.

**Ce projet ne manque pas de garde-fous. Il manque de garde-fous qui refusent.** Le motif que tu
as toi-même trouvé — *une liste qui se confronte à la réalité et passe au rouge* — n'est branché
qu'à deux endroits sur les cinq où il devrait l'être. C'est ça, la vraie réponse à « qu'est-ce
qu'il faut VRAIMENT pour ouvrir » : pas un atelier, **des contrôles qui disent non.**

---

**Ce que je n'ai PAS fait, comme demandé :** rien de construit, rien de scripté au BLOC E,
aucun secret déplacé, aucun distant ajouté, aucun fichier du projet modifié. Le seul écrit du
programme est la régénération de `3-atelier\retours-joueurs\` que tu demandais au BLOC B (une
copie de sûreté de l'état précédent est conservée).

