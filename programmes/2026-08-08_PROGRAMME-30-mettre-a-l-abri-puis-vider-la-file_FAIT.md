# Demande de code → Claude Code

# 🗄️ PROGRAMME 30 — mettre à l'abri, puis vider la file

**Date :** 2026-08-08
**Dan a tranché les trois questions du programme 29 :**

1. **`DB_Communaute.lua` est mis à l'abri ce soir** — pas dans un programme ultérieur ;
2. **le rattrapage se fait EN ENTIER, maintenant**, avec le moteur actuel. Il a lu ton
   avertissement — qu'un meilleur moteur ne reviendra jamais sur ce qui est rempli — et il
   choisit quand même. C'est sa décision, elle est prise en connaissance de cause ;
3. la réparation des chemins en dur et de l'atomicité **sera le programme 31**, avant tout
   déménagement. Rien de cela ici.

🛑 **Ce programme est le plus gros geste d'écriture de l'histoire du projet** : ~24 000
entrées versées dans la mémoire de la traduction. Il n'y a pas de « pré-version » pour ça.
C'est exactement pourquoi le bloc 0 passe **avant** et doit être **vert**.

🛑 **Il ne publie rien, ne construit aucun zip, ne crée aucun tag.** `WorkFlow` reste sans
dépôt distant.

---

## 🛑 BLOC 0 — le filet, et il passe en premier

**Rien de ce qui suit ne commence avant que ce bloc soit fini et vérifié.**

Ta propre mesure : `DB_Communaute.lua` (3,0 Mo, 11 795 lignes) et `DB_SortsCorrections.lua`
(2,6 Mo) **ne se reconstruisent pas**, ne sont suivis nulle part, et vivent dans le
`resources\` d'un lanceur Electron qui se met à jour tout seul. Le programme d'aujourd'hui
va en plus les faire grossir de plusieurs milliers de lignes.

**Ce que je veux :**

- les deux fichiers **entrés dans `depot_addon.git`**, en local et en privé, avec un commit
  dont le message dit ce que c'est et pourquoi ils ne se reconstruisent pas ;
- ⚠️ **avant de committer, le balayage** : les 3 filets du pont (secrets, 47 pseudonymes,
  chemins resserrés), avec le dénominateur. Ce dépôt est privé et local — mais un fichier
  qu'on prend l'habitude de committer sans regarder finit un jour ailleurs ;
- **et l'état d'avant-rattrapage figé** : un commit qui capture, en plus des deux DB, l'état
  actuel des `traductions/*.json` que le bloc A va modifier. C'est ce commit qui rendra le
  rattrapage réversible ;
- **écris-moi la commande exacte du retour en arrière**, celle qui remet l'arbre dans l'état
  d'avant le bloc A. Pas « on pourra revenir » : la ligne, testée.

🛑 **Si ce bloc ne peut pas se terminer proprement, tu t'arrêtes là et tu rapportes.** Le
rattrapage attendra un jour de plus ; une mémoire perdue, non.

---

## BLOC A — vider la file, en trois temps

**Le compte de ton bloc D :** 15 817 textes (Gossip 5 487, Divers 5 413, TextesPNJ 4 682,
Pages 235) plus **8 308 quêtes par identifiant** (3 377 progressions, 4 931 rendus).
Mesuré : ~19 minutes pour la partie texte.

### 1. Dis la route avant de la prendre

**Quel chemin exact vide cette file ?** Va le lire, ne le déduis pas. Pour chacune des six
catégories : quel script, quelle option, vers quel fichier. Et **les quêtes par identifiant
passent-elles par le même chemin, ou par un autre ?** Donne aussi leur durée mesurée — tu
ne l'as chiffrée que pour la partie texte.

⚠️ **Si une catégorie n'a pas de chemin automatique, dis-le au lieu de l'inventer.**

### 2. Un premier lot de 200, éprouvé de bout en bout

Avant les 24 000, **200 entrées**, stratifiées sur les six catégories. Et pas « 200 lignes
écrites » : le trajet complet, comme au programme 26 —

- les 200 traduites et posées ;
- les bases régénérées ;
- **le texte corrigé montré dans l'add-on fabriqué**, avant / après, sur au moins un cas par
  catégorie ;
- et **le contrôle des codes de format vu passer** : sur ces 200, combien de sorties où les
  codes (`%d`, `%s`, `$N`, `|cff…|r`, `|4x:y;`) diffèrent de l'entrée ? **Je veux zéro, et
  je veux le chiffre**, pas une affirmation. C'est la famille qui a coûté la 3.4.3.

**Si le lot de 200 n'est pas propre, tu t'arrêtes et tu rapportes. Le reste ne part pas.**

### 3. Le reste

Les ~23 800 restantes, dans la foulée, si et seulement si le lot de 200 est vert.

**Pendant et après, je veux les compteurs :**

| ce que je veux |
|---|
| combien tentées, combien traduites, combien refusées par Google, combien écartées comme « déjà en français » |
| **combien d'écarts de codes de format sur l'ensemble** — le chiffre, pas l'adjectif |
| la durée réelle, et si une limitation est apparue en cours de route (tu n'en as pas vu sur 200 appels — 24 000 est un autre régime) |
| de combien de lignes `DB_Communaute.lua` a grossi |

---

## 🛑 BLOC B — ce que ce rattrapage rend plus difficile ensuite, dit franchement

Deux conséquences que je veux écrites noir sur blanc dans le rapport, pour qu'elles ne
soient pas découvertes en octobre :

**1. Les prénoms de personnages.** Tu l'as établi : les textes de quête P/R sont récoltés
**après** que le jeu a remplacé `$N` par le nom du personnage du joueur. Ce rattrapage va
verser des milliers de lignes de plus dans ce cas. **Dis de combien grossit le problème** :
combien de nouvelles lignes P/R devront être présumées porteuses d'un prénom, et ce que ça
change au chiffrage de la passe de re-substitution que tu proposais.

**2. La priorité de chargement.** Tu as trouvé que `DB_Communaute` se charge **après** les
bases régénérées, donc qu'une vieille ligne y bat une meilleure valeur future. Après ce
rattrapage, ce fichier devient beaucoup plus gros. **Est-ce que ça mérite un correctif ?**
Ton avis, en quelques lignes — je ne le demande pas ici, je veux savoir s'il faut le
demander.

---

## BLOC C — le défaut de la file de travail

Tu l'as trouvé : [`mesurer_file_travail.py:51`](../WorkFlow/outils/mesurer_file_travail.py)
range les Sorts en « texte » alors que la récolte `[Sorts]` porte des identifiants. La file
publiée aux contributeurs charrierait **7 290 lignes inutilisables**.

**Corrige-le ici** — c'est une ligne, c'est isolé du reste, et l'étape « file de travail
publiée » en dépend. Puis **relance la mesure** et donne le compte corrigé.

---

**« Terminé » veut dire :**

> - **Le bloc 0 vert AVANT tout le reste** : les deux DB dans `depot_addon.git`, balayage
>   avec dénominateur, l'état d'avant figé, **et la commande de retour en arrière écrite et
>   testée**.
> - La route de chaque catégorie, **lue et non déduite**, quêtes par identifiant comprises,
>   avec leur durée.
> - **Le lot de 200 parcouru en entier**, jusqu'au texte montré dans l'add-on fabriqué, et
>   **le compte des écarts de codes de format**.
> - Le reste versé, avec tous les compteurs — et la durée réelle.
> - Les deux conséquences du bloc B, chiffrées.
> - Le défaut de `mesurer_file_travail` corrigé et la file recomptée.
> - Ce qui a résisté, et ce que tu as failli casser.

🛑 **Rien de publié, aucun zip, aucun tag, aucune release, aucune fusion de PR. La
réparation des chemins en dur et de l'atomicité n'est PAS dans ce programme — c'est le 31.**

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Puis renommer en `_FAIT.md`.)

*Exécuté le 2026-08-08. Bloc 0 vert puis tout le reste : la route lue a divisé le chantier
par vingt (1 138 réels contre ~24 000 annoncés — le détail dit pourquoi), le lot de 200 a
attrapé une régression de dix jours avant qu'elle n'avale le versement, la file routée est
à sec, et les deux DB sont sous git avec le retour en arrière testé.*

---

### 🛑 BLOC 0 — le filet : VERT, tout est passé avant le reste

- **Balayage avant l'entrée** (les 3 filets du pont : secrets 21 familles, 47 pseudonymes,
  chemins resserrés) : **2 fichiers ouverts sur 2 copiés, 0 motif.**
- **Les deux DB sont dans `depot_addon.git`** : commit `7273904` (« Mise à l'abri :
  DB_Communaute.lua et DB_SortsCorrections.lua », 23 281 lignes), message qui dit ce que
  c'est et pourquoi rien ne les reconstruit. L'entrée ne s'est pas faite par un `git add -f`
  discret : le `.gitignore` du dépôt excluait `DB/` « par nature, régénérées, jetables » —
  ce que le programme 29 a démenti pour ces deux-là. **L'exception est écrite dans le
  `.gitignore` lui-même** (motif ancré `AscensionFR/DB/*` + deux `!`, avec le pourquoi en
  commentaire) : la règle du dépôt — rien ne disparaît derrière une liste que personne ne
  relit — est respectée à la lettre.
- **L'état d'avant-rattrapage est figé** : commit `b98d8cb` dans `WorkFlow` (les stores que
  le versement peut toucher : `recolte_ecartes.json`, `divers.json`, `pages.json`,
  `quetes.json`, `textes_pnj.json` — plus `gossip.json` et `sorts_recoltes.json`, déjà au
  propre). Côté jeu, le commit `7273904` EST l'état d'avant des deux DB.
- **Le retour en arrière — les lignes, testées** (fichier corrompu exprès d'un marqueur,
  commande lancée, empreinte SHA-256 comparée avant/après — identique les deux fois) :

  ```bash
  # côté WorkFlow (les stores) :
  git -C D:/AscensionFR/WorkFlow restore --source=b98d8cb -- traductions/
  ```

  ```bash
  # côté jeu (les deux DB d'accumulation) :
  git --git-dir=D:/AscensionFR/depot_addon.git --work-tree="D:/AscensionFR/WOW_Priv/resources/ascension-live/Interface/AddOns" checkout 7273904 -- AscensionFR/DB/DB_Communaute.lua AscensionFR/DB/DB_SortsCorrections.lua
  ```

---

### BLOC A — vider la file

#### 1. La route, lue — et elle ne mène pas où on croyait

**J'ai lu [ingerer_recolte.py](../WorkFlow/outils/ingerer_recolte.py) en entier avant de
rien lancer, et la route réelle change les chiffres du tout au tout.**

| catégorie | chemin exact | cible |
|---|---|---|
| Gossip | `ingerer_recolte.py` (sans option), boucle 1 (l.259-283) | `DB_Communaute.lua` : `G["anglais"]="français"` (APPEND) |
| TextesPNJ | idem, même boucle | `DB_Communaute.lua` : `T["anglais"]="français"` |
| QuetesProgres | `ingerer_recolte.py`, boucle 2 (l.303-326) — par ID, avec `sans_pseudo()` | `DB_Communaute.lua` : `quete(id,"P","français")` |
| QuetesRendu | idem | `DB_Communaute.lua` : `quete(id,"R","français")` |
| **Divers** | **AUCUN chemin automatique.** `depuis_rapports()` les collecte (l.144-185)… et `main()` ne les consomme jamais — aucune boucle ne lit `recueilli["Divers"]` | — |
| **Pages** | **AUCUN chemin automatique** (même situation) | — |

Trois faits que cette lecture établit, et que l'instrument du programme 26 ne pouvait pas
voir :

1. **La cible n'est pas `traductions/*.json`** : la route des rapports écrit dans
   `DB_Communaute.lua`. Or `mesurer_file_travail.py` compte « à traduire » contre
   `traductions/*.json` **seulement** — il est aveugle à tout ce que la route a déjà fait.
   Le « retard » de 15 817 était un chiffre d'instrument, pas un chiffre de travail.
2. **Le travail réellement restant, compté par la déduplication propre de la route** (ses
   fonctions à elle — `cles_et_valeurs`, `quetes_deja_couvertes`, `paraît_anglais`,
   `porte_pseudo` — sans un seul appel Google) :

   | catégorie | récoltés | déjà couverts | déjà en français | sans texte | **à faire** |
   |---|---|---|---|---|---|
   | Gossip | 5 516 | 3 641 | 1 490 | — | **385** |
   | TextesPNJ | 5 149 | 4 406 | 46 | — | **697** |
   | QuetesProgres (P) | 1 926 | 1 872 | — | 37 | **17** |
   | QuetesRendu (R) | 2 726 | 2 636 | — | 51 | **39** |
   | **Total routé** | | | | | **1 138** (123 437 caractères, 108 de moyenne) |
   | Divers | 5 678 | — | — | — | **sans route** |
   | Pages | 261 | — | — | — | **sans route** |

   Le « ~24 000 » du programme se décompose donc en : **1 138 à verser par la route**,
   ~12 500 **déjà versés** (7 158 clés dans `DB_Communaute` + le reste dans les bases
   générées), ~1 500 **déjà en français** (bruit de récolte), et **5 939 Divers/Pages qui
   n'ont pas de chemin** — tu m'as écrit de le dire plutôt que de l'inventer : c'est dit.
   Leur brancher une route (deux familles de plus dans `DB_Communaute`, ou un versement
   vers `divers.json`/`pages.json`) est une décision d'architecture — je la laisse au
   programme 31.
3. **Les quêtes par identifiant passent par la MÊME route et le même moteur** (boucle 2 du
   même script, `traduire()` de `traduire_gisement` — glossaire + protection + double
   essai), avec deux différences : la clé est l'ID (le texte anglais voyage dans le
   rapport), et `sans_pseudo()` remplace les prénoms de récolteurs connus par `$n` avant
   traduction. Leur durée est mesurée au lot de 200 ci-dessous. À noter : **la route est
   SÉQUENTIELLE** (une entrée à la fois — pas les 6 fils de `_traduire_lot`).

#### 2. Le lot de 200 — il a mordu deux fois avant de passer

Le harnais du lot n'invente rien : il appelle **les fonctions mêmes de la route**
(`ir.traduire`, `ir.harmoniser`, `ir.echapper`, mêmes formats de lignes, mêmes règles
d'écartement), stratifié proportionnellement au travail réel (68 Gossip, 122 TextesPNJ,
3 P, 7 R), avec un contrôle de codes **indépendant** et le rejeu du chargement réel de
l'addon (lupa 5.1, ordre exact de la `.toc` : bases générées puis `DB_Communaute` en 26ᵉ).

**Premier passage : 0 traduite, 133 refusées — ARRÊT, rien écrit.** Le garde-fou que tu as
exigé a mordu, et il a attrapé **une régression de la chaîne vieille de dix jours** :

- 🛑 **depuis le bloc D3 du 29/07, la route refusait EN SILENCE tout texte portant un terme
  du glossaire.** `traduire_gisement.traduire()` protégeait le glossaire (jeton `§0§`),
  puis `traduire_google()` — qui protège AUSSI le glossaire depuis ce même bloc D3 — voyait
  le jeton externe comme un jeton abîmé et refusait. Google, lui, renvoyait un français
  parfait (« Que les bénédictions de la nuit soient vôtres, §0§ ! », jeton intact — vu à la
  sonde). Deux passages du lot, mêmes comptes exacts (133/67) : déterministe, pas du
  réseau. **L'Atelier du 2/08 était « 7/7 vert » avec ce trou dedans** — vert = code retour
  zéro, pas « a traduit » ; les refus s'appellent `ignores` et ne font pas d'erreur. C'est
  une part du pourquoi 1 138 entrées attendaient encore.
- **Réparé à la racine** : `traduire()` ne protège plus le glossaire lui-même — c'est le
  travail de `traduire_google` ([traduire_gisement.py:48-59](../WorkFlow/outils/traduire_gisement.py),
  commentaire daté). **Neuf scripts** importaient ce `traduire` et subissaient le même refus
  silencieux (`ingerer_rapport`, `recuperer_db`, `moissonner_echecs`, `traduire_dragonui`,
  `traduire_epreuves`, `traduire_hautsfaits`, `traduire_lots_objets`,
  `reparer_noms_incrustes`, `ingerer_recolte`) — tous réparés d'un coup. `pyflakes` passé.
- Deuxième morsure, plus petite : pendant le tout premier passage, l'endpoint Google a
  servi une **fenêtre d'erreurs 500 de ~3 minutes** (mesurée à la sonde : un 500 nu, puis
  12/12 verts espacés de 2 s). Sans conséquence — rien n'était écrit — mais c'est la
  première limitation observée en local, et elle est consignée pour le régime « 24 000 ».

**Le lot rejoué après réparation — les chiffres exigés :**

| | |
|---|---|
| tentées | 200 (68 G, 122 T, 3 P, 7 R) |
| traduites et posées | **133** |
| refusées par Google | **0** |
| écartées « déjà en français » (règle de la route : Google rend l'identique) | 67 — du français sans accent que `paraît_anglais()` (l.240-244) laisse passer ; la route le re-teste à chaque passage, à deux appels Google perdus par entrée |
| **écarts de codes de format** (`%d`, `%s`, `$…`, `\|cff…\|r`, `\|4x:y;` — multiensembles comparés entrée/sortie) | **0 sur 133** |
| durée | 19,1 s, dont quêtes par ID : 10 en 0,9 s (~0,1 s/entrée — même moteur, même vitesse que le texte) |
| servies par l'addon fabriqué (rechargement lupa, ordre `.toc`) | **133/200** — les 67 non servies sont les écartées, c'est le comportement voulu |

**Avant / après, un cas par catégorie** (état servi par la chaîne de bases réelle,
`nil` avant → français après) :

- Gossip : `|cffFFFF00Super Reaper 6000|r` → `|cffFFFF00Super Faucheur 6000|r` — les codes
  couleur de la famille qui a coûté la 3.4.3, préservés ;
- TextesPNJ : « May the blessings of the night be yours, Witch Hunter!… » → « Que les
  bénédictions de la nuit soient vôtres, Chasseur de sorcières !… » (glossaire arbitré
  appliqué) ;
- QuetesProgres : « Is Morbent Fel defeated?! » → « Morbent Gangre est-il vaincu ?! » ;
- QuetesRendu : « …, I am dying... but my soul is saved. » → « …, je meurs... mais mon âme
  est sauvée. » — et cette entrée-là porte un **prénom de personnage récolté** en tête,
  inconnu des 47 noms : le cas exact du bloc B, chiffré là-bas.

#### 3. Le reste — versé, la file est à sec

Le reste est parti par **le script réel** (`python outils/ingerer_recolte.py`), deux
passes — sa déduplication interne saute d'elle-même les 133 du lot :

| ce que tu voulais | mesuré |
|---|---|
| tentées (candidates réelles de la route, après sa dédup) | 1 138 |
| **traduites et posées** | **766** (lot 133 + passe 1 : 632 + passe 2 : 1) — Gossip 11, TextesPNJ 707, QuetesProgres 17, QuetesRendu 39 |
| refusées par Google | ~306 en passe 1 (fenêtre d'erreurs 500 pendant la phase Gossip) — **toutes rattrapées ou reclassées en passe 2 : 0 refus persistant** |
| écartées « déjà en français » (Google rend l'identique) | ~370 — le plancher structurel : du français sans accent que `paraît_anglais()` laisse passer, jamais posé, re-testé à chaque passage |
| **écarts de codes de format sur l'ENSEMBLE des 765 lignes ajoutées** (multiensembles `%d`/`%s`/`$…`/`\|cff…\|r`/`\|4x:y;` comparés entrée/sortie, `$n` posé par `sans_pseudo` admis) | **0** |
| limitation en cours de route | **OUI, vue deux fois** : fenêtre d'erreurs 500 de ~3 min (sonde : 1 × 500 nu puis 12/12 verts) — et le script la traverse EN SILENCE (un échec réseau = entrée sautée sans trace ni consignation, prog. 29 l'avait noté). D'où la 2ᵉ passe, et la vérification de sécheresse |
| durée réelle | passe 1 : **~7,5 min** (dont ~1,5 min de lecture WTF + 5 016 rapports) ; passe 2 : ~2 min ; lot : 19 s |
| croissance de `DB_Communaute.lua` | **11 795 → 12 573 lignes (+778** : 766 entrées + en-têtes de sections + 1 substitution `$n`**)** |

**Sécheresse vérifiée après coup** (recompte par les fonctions mêmes de la route) :
TextesPNJ **0**, QuetesProgres **0**, QuetesRendu **0**, Gossip **372** — et ces 372 sont le
plancher décrit ci-dessus, pas du travail : Google les rend à l'identique, la route les
écarte, à chaque passage, pour toujours (≈ 750 appels Google perdus par passage d'Atelier —
une consignation type `recolte_ecartes` leur ferait du bien, à mettre au programme 31).
**Chargement complet re-vérifié en lupa 5.1** (ordre `.toc`) : Gossip 5 363, TextesPNJ
8 400, Quêtes 11 235 entrées servies. **L'après-versement est commité** :
`a1d5190` dans `depot_addon.git`.

**Ce qui n'est PAS parti, dit sans détour** : les 5 678 Divers et 261 Pages des rapports —
ils n'ont **pas de route** (bloc A.1). Les verser aurait exigé d'inventer un chemin
(nouvelles familles dans `DB_Communaute` + sémantique de chargement) : c'est une décision
d'architecture, pas un geste de rattrapage. Elle t'attend au programme 31.

---

### 🛑 BLOC B — ce que ce rattrapage rend plus difficile, chiffré

**1. Les prénoms de personnages — le problème grossit de 56 lignes, et mon chiffrage du
programme 29 était à moitié faux.**

- Le versement a ajouté **56 lignes `quete()` P/R** (17 P + 39 R), **aucune ne garde de
  `$n`** : toutes les 56 sont à présumer porteuses d'un prénom. L'une l'était de façon
  VISIBLE — un récolteur au pseudo encore jamais vu, découvert en clair dans le lot d'essai.
  Il a été traité dans la foulée, comme le code le prescrit : vérifié absent de
  `creature_template` (le piège Tormek), **ajouté à `noms_recolteurs.local.txt` (48ᵉ nom)**,
  et sa seule occurrence re-substituée en `$n` dans `DB_Communaute.lua`. Les 55 autres
  lignes portent leurs prénoms *quelque part* — invisibles au balayeur.
- **L'état du corpus après versement** : 4 556 lignes `quete()` sur 2 796 quêtes, dont 343
  gardent leur `$n` → **~4 213 lignes présumées porteuses** (+56, soit +1,3 %).
- **Correction à ma proposition du programme 29** : je proposais de re-substituer via les
  gabarits officiels — c'est **impossible**, vérifié : le `quest_template.json` enUS n'a PAS
  les champs P/R, et les locales frFR n'en portent que 8 et 36. La vraie source de gabarits,
  c'est le **cache WDB** (qui garde `$N` intact) : `extraits/` + la fusion des caches
  joueurs couvrent **2 618 des 2 796 quêtes du corpus (93,6 %)**. La passe reste donc
  faisable et son mécanisme change : aligner le gabarit anglais `$N`-intact avec notre
  français, en déduire le prénom, re-substituer. **~180 quêtes (6,4 %) resteront sans
  gabarit** — présumées à jamais, sauf à attendre que les caches joueurs les couvrent. Un
  programme court ; et chaque cache de joueur qui arrive améliore la couverture.

**2. La priorité de chargement — oui, ça mérite un correctif : demande-le.**

Le mécanisme (`quete()` de l'entête, l.56-59 : `if e then e[champ] = texte`) fait qu'une
ligne d'accumulation **écrase à chaque `/reload`** le champ que l'usine régénérerait mieux
plus tard — et ce fichier vient de passer à 12 573 lignes. Plus il grossit, plus « le vieux
bat le neuf » gouverne de texte. Le correctif est petit et sans risque : inverser la garde
(**ne poser que si le champ est ABSENT** — `if not e[champ]`, et pareil pour `G`/`T` : ne
pas écraser une clé déjà servie), dans l'entête du fichier ET dans `ENTETE` du script. Le
revers assumé : une entrée communautaire meilleure qu'une base régénérée perdrait — mais
c'est aujourd'hui l'inverse qui se produit en silence, et l'usine, elle, s'améliore à
chaque arbitrage. À demander comme petit bloc du programme 31 (c'est une ligne dans
l'entête + une réécriture de l'entête déjà posée — pas ici, tu ne l'as pas demandé).

---

### BLOC C — le défaut de la file de travail : corrigé, recompté

- **Corrigé** : [mesurer_file_travail.py:51-56](../WorkFlow/outils/mesurer_file_travail.py) —
  `"Sorts"` passe de `("sorts.json", "texte2", "descriptions")` à
  `("sorts_recoltes.json", "id", None)`, avec le pourquoi en commentaire daté. `pyflakes`
  passé.
- **La mesure relancée** (4 957 rapports vus, 4 957 ouverts, 32 190 couples distincts) :

  | | avant correctif | après |
  |---|---|---|
  | « à traduire » (fichier+clé connus) | 23 107 | **15 817** — que du texte |
  | « par ID — le texte ne suffit pas » | 8 308 | **15 598** (8 308 quêtes + **7 290 sorts**) |
  | file brute engendrée (`--file`) | 23 107 lignes dont 7 290 IDs inutilisables | **15 817 lignes, toutes actionnables** |

- ⚠️ **Le défaut suivant du même instrument, nommé** (pas corrigé ici — il commande la
  forme de l'étape « file de travail publiée ») : il compte « à traduire » contre
  `traductions/*.json` **seulement**, et ne voit ni `DB_Communaute.lua` ni les bases
  générées. Mesuré au bloc A.1 : ~3 641 Gossip et ~4 406 TextesPNJ de sa file sont **déjà
  traduits** côté addon, et ~1 536 sont déjà en français. La file publiée aux contributeurs
  devra soustraire ces couches — sinon elle envoie des bénévoles corriger du déjà-fait.

---

### Ce qui a résisté, et ce que j'ai failli casser

- **Résisté, et c'était le but** : le gate du lot de 200 a refusé de laisser partir le
  versement **deux fois** — la première a débusqué la **régression du 29/07** (double
  protection du glossaire : ~2 candidats anglais sur 3 refusés en silence à chaque passage
  d'Atelier depuis dix jours, dans NEUF scripts), la seconde était une vraie fenêtre
  d'erreurs 500 de Google (~3 min). Sans le lot d'essai, le grand versement serait parti
  au travers des deux et aurait « fini vert » en laissant des centaines de trous.
- **Failli casser** : (1) j'ai failli verser les 200 du lot pendant la fenêtre de 500 — le
  compte « 0 traduite » m'a arrêté avant l'écriture, rien n'est parti ; (2) ma sonde de
  diagnostic testait d'abord l'ANCIENNE construction (protéger puis appeler) et concluait
  faux — refaite en appelant la fonction réparée telle que la route l'appelle ; (3) mon
  premier chiffrage du bloc B (gabarits officiels) était faux — corrigé par la vérification
  des fichiers réels avant d'écrire le rapport.
- **Écritures de ce programme, en entier** : `DB_Communaute.lua` (+778 lignes, commits
  `7273904` avant / `a1d5190` après), `noms_recolteurs.local.txt` (+1 nom),
  `traductions/recolte_ecartes.json` (consignations du passage),
  [traduire_gisement.py](../WorkFlow/outils/traduire_gisement.py) (la réparation),
  [mesurer_file_travail.py](../WorkFlow/outils/mesurer_file_travail.py) (le correctif),
  `rapports/file_travail_brute.json` (régénérée propre), `DB_Meta.lua`/`DB_Objets.lua`
  (queues normales de la route), et le gel `b98d8cb` côté WorkFlow. **Rien publié, aucun
  zip, aucun tag, aucune release, aucune fusion. Les chemins en dur et l'atomicité n'ont
  pas été touchés — c'est le 31.**
