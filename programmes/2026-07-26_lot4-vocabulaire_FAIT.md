# Demande de code → Claude Code

**Date :** 2026-07-26 · **lot 4 — application des arbitrages de vocabulaire**
*(mis à jour le 26/07 au soir : trois termes ajoutés, issus de ta réponse au lot 3)*

> ✅ Le lot 3 est fait, la 3.4 est débloquée. **Dan a décidé que le vocabulaire part dans
> la 3.4** : ce lot passe donc avant le build.

**Objectif (le QUOI, pas le comment) :**

> Dan a soldé neuf arbitrages. Ils sont inscrits dans `4-reference/GLOSSAIRE.md`, qui fait
> foi. Applique-les dans `traductions/*.json`.

---

## ⭐ D'abord, la règle par défaut (elle change ta marge de manœuvre)

> **Quand notre traduction et l'officiel Blizzard divergent, l'officiel gagne — SAUF
> quand l'officiel perd une information** (couleur d'une monture, mention « (Animal) »,
> précision d'un effet) ou se trompe de sort.

Tu n'as plus besoin de faire remonter chaque divergence à Dan : tu appliques la règle et
tu me signales seulement les cas où l'officiel perd du sens.

⚠️ **Mais pas de passe de masse avant le lot 5.** Le lot 5 mesure la fiabilité de
l'appariement avec la source officielle — j'y ai trouvé des lignes où « l'officiel »
retenu n'a rien à voir avec l'entrée anglaise. Les **121 divergences** et les **1 762
conflits Glayna** attendent ce résultat.

## Les termes à appliquer

| Terme | Ce qu'on écrit | Volume repéré |
|---|---|---|
| PvP / PvE | **PvP / PvE** (jamais JcJ/JcE) | ~510 textes à aligner |
| Build Draft / Draft Mode | **Draft** (on garde l'anglais) | 730 occurrences |
| Manastorm | **Tempête de mana** | 266 textes à basculer |
| Starcaller | **Mande-étoiles** | 185 en anglais + 39 « Héraut stellaire » |
| Light Lash | **Fouet de Lumière** | 6 textes |
| **Static** *(ressource de classe)* | **Statique**, avec majuscule | *Décidé le 26/07.* « Génère 20 Statique ». La majuscule dit que c'est une ressource, pas un adjectif. Corrige « 20 statiques ». |
| **Arathi Basin** | **Bassin Arathi** | *Réglé par la règle par défaut* — nom officiel. Corrige « bassin d'Arathi ». |
| **Warsong Gulch** | **Goulet des Warsong** | *Réglé par la règle par défaut* — nom officiel, aujourd'hui resté en anglais. |

## Les précautions qui ont déjà évité des dégâts

1. **Filtrer sur la clé anglaise, jamais sur la valeur française seule.** Sur 165
   « Libérez », 73 seulement traduisaient `Unleash` — un remplacement global en aurait
   cassé 91.
2. **Mot entier.** « Unleash » en sous-chaîne attrape « Unleash**ing** » : 143 faux
   positifs au lieu de 73.
3. **Chiffrer avant de remplacer**, et me donner le compte réel si mes chiffres sont faux
   (tu as déjà eu raison contre moi : j'annonçais 4 « Parchemin du Gardien », il y en
   avait 55).
4. **Vérifier la fonction du mot.** Sur « Draft » en particulier : il est parfois **verbe**
   (« draft new starting spells ») et il a été traduit par **« rédiger »** — contresens à
   corriger, mais ce n'est pas le même traitement que le nom du mode.

## Les contresens confirmés à corriger au passage

- **« Cils légers » / « Cils clairs »** pour `Light Lash` : « lash » compris comme un cil
  d'œil au lieu d'un coup de fouet.
- **« rédiger de nouveaux sorts »** pour « draft new starting spells ».
- **« Génère 20 statiques »** → « Génère 20 Statique ».
- À vérifier : *« Utilisable uniquement dans le temps de recharge de Manastorm.Shares avec
  des effets similaires »* — la phrase anglaise « Only usable in the Manastorm. Shares
  cooldown… » a été recollée de travers (un point manquant a fusionné deux phrases).
  Cherche s'il y en a d'autres au même endroit.

## Une mesure que je te demande en plus (ne corrige pas encore)

Tu as signalé une **incohérence sur les noms de sorts** : « Shield Slam » et « Blessed
Vengeance » restent en anglais alors que « Demonic Brutality » est traduit. Avant de
décider quoi que ce soit, je veux savoir **si c'est un vrai trou ou un rattrapage à
l'affichage** :

- Combien de noms de sorts sont dans ce cas (anglais dans nos sources) ?
- Le pont des noms de sorts en rattrape-t-il une partie **à l'écran** ? Vérifie sur
  « Shield Slam » comme tu l'as fait pour les conditionnels : ce qui s'affiche, pas ce
  qu'il y a dans la base.
- S'il existe un nom officiel Blizzard pour ces sorts, la règle par défaut s'applique —
  mais **chiffre d'abord**, ne lance rien.

---

**« Terminé » veut dire :**

> - Les huit termes appliqués, avec le **compte réel** de ce qui a été touché pour chacun.
> - Les contresens corrigés.
> - La mesure sur les noms de sorts rendue (chiffres + ce qui s'affiche à l'écran).
> - `verifier_tout.py` propre, marges des bases affichées.
> - **Ne rien publier, ne rien pousser.** Le build de la 3.4 fera l'objet d'une demande à
>   part, après le test en jeu de Dan.
> - Si tu tombes sur un cas où l'officiel Blizzard **perd du sens**, ne tranche pas :
>   note-le et rends-le-moi, c'est l'exception prévue par la règle.

**Validation :**

> Autonome sur les huit termes et sur la mesure. **Arrête-toi et dis-le-moi** avant toute
> passe globale sur les 1 762 conflits Glayna ou les 121 divergences — c'est le lot 5 qui
> décide si elle est faisable.

---
## Réponse de Claude Code

**Fait le 26/07/2026. Les huit termes sont appliqués, les contresens corrigés, la
mesure rendue. `verifier_tout.py` : code retour 0. Rien n'a été publié ni poussé.**

Outil : `outils/appliquer_vocabulaire.py` (simulation par défaut, `--appliquer`
pour écrire, sauvegarde `*_avant_vocabulaire.json`). Détail ligne à ligne dans
`rapports/vocabulaire_lot4.txt`.

**948 entrées corrigées**, en trois passes (671, puis 191 après correction d'un
défaut de mon moteur, puis 86 pour les verbes et les recollages).

---

### Les comptes réels

Tu demandais le compte réel quand tes chiffres seraient faux. Ils le sont
souvent — parce que tu comptais des **occurrences** là où je compte des
**entrées**, ce qui n'est pas la même chose.

| Terme | Ton estimation | Réel (règles appliquées) |
|---|---|---|
| Manastorm | 266 textes | **626** |
| PvP / PvE | ~510 textes | **159** entrées (mais 674 entrées ont « PvP » côté anglais) |
| Draft (nom) | 730 occurrences | **52** entrées (274 ont « draft » côté anglais, 76 étaient polluées) |
| Draft (verbe) | — | **16** |
| Recollages | 1 cas connu | **60** |
| Starcaller | 185 + 39 | **49** |
| Static | — | **45** |
| Arathi Basin | — | **25** |
| Warsong Gulch | — | **11** |
| Light Lash | 6 textes | **4** |
| Abyssal Draft | — | **1** *(voir plus bas)* |

---

### Trois pièges qui auraient fait des dégâts

**1. « Millhouse Manastorm » est un PERSONNAGE, pas le donjon.** C'est le gnome
de l'Arcatraz. Un remplacement en masse l'aurait transformé en « Millhouse
Tempête de mana ». Il est exclu de la règle — exclusion qui porte sur l'anglais
**et** sur le français, parce que certaines entrées n'ont plus leur anglais.

⚠️ **Mais le mal était déjà fait** : `Millhouse Manastorm` est traduit
aujourd'hui par **« Tempête de mana du moulin »** — « mill house », la maison du
moulin. C'est un nom propre, donc je n'y touche pas : **ça t'appartient.**

**2. « statique » est presque toujours un vrai adjectif français.** Sur 146
emplois de « Static » côté anglais, **la moitié seulement est la ressource**.
« Charge statique en arc », « équilibre statique », « électricité statique »
sont corrects. La règle ne touche donc que les formes chiffrées
(« Génère 20 Statique ») et « All Static ». Un remplacement global aurait abîmé
73 textes justes.

**3. « Abyssal Draft » n'est pas la mécanique — et c'était déjà faux.**
C'est un réactif d'artisanat, et « draft » y veut dire **courant d'air**. La
famille le prouve : Droplet → Eau, Spark → Feu, Fragment → Terre, **Draft →
Air**. Le français livré disait « Draft abyssal », qui ne veut rien dire.
Vérifié : c'était déjà l'état **avant** ce lot, ce n'est pas une régression.
Corrigé en **« Souffle abyssal »**, et toutes les règles Draft l'excluent
désormais explicitement.

---

### Un défaut de mon propre moteur, trouvé et réparé

Ma première passe a raté **191 entrées**. Cause : les codes couleur du jeu se
**collent** au mot suivant — `|cFFB5FFFFStarcaller`. Entre le `F` du code et le
`S` du mot, il n'y a aucune frontière de mot : `\b` ne voit rien. 38 occurrences
de Starcaller et 53 de Manastorm passaient ainsi sous le radar.

Réparé des deux côtés : la garde anglaise lit désormais un texte **dénudé** de
ses codes, et les motifs français acceptent la fin d'un code couleur comme début
de mot. C'est corrigé dans l'outil, donc ça ne se reproduira pas.

---

### Les contresens

- **« Cils légers » / « Cils clairs » → « Fouet de Lumière »** : 4 entrées, plus
  3 dans le pont des noms d'objets (`DB_ObjetsNoms.lua`), que j'ai régénéré.
- **« Génère 20 statiques » → « Génère 20 Statique »** : fait.
- **« rédiger » → le verbe drafter** : 16 entrées. ⚠️ **C'est le seul endroit de
  ce lot où j'ai choisi un mot, et pas toi.** Ton glossaire dit « Draft — on
  garde l'anglais » pour la mécanique ; j'ai suivi la même logique pour le verbe
  (« drafter », « redrafter », « Draftez »), qui est ce que disent les joueurs.
  Si tu préfères « piocher » / « composer », c'est **une seule table à changer**
  dans l'outil et la sauvegarde est à côté.
- **Les phrases recollées de travers : 60 corrigées.** Ta piste était bonne et il
  y en avait bien d'autres. Trois familles :
  - le cas que tu citais (coquille `Manastorm.Shares` dans la source anglaise) —
    le libellé de remplacement n'est pas inventé, c'est celui des **250 entrées
    sœurs** dont la source est correcte ;
  - **« Casting »** resté en tête de 9 descriptions (« Casting Heurtoir vous
    accorde… ») → « Lancer », le mot déjà employé ailleurs dans le même fichier ;
  - **« Restores »** resté en tête de 39 descriptions → « Rend », plus
    « points de vie **over** $d » → « en $d » et « mana **or** » → « ou ».

---

### La mesure que tu demandais sur les noms de sorts

**Réponse : c'est un vrai trou, pas un rattrapage à l'affichage.** Vérifié en
faisant tourner le moteur de l'addon, pas en lisant la base.

- **Le pont ne peut pas rattraper.** `AFR.DB.SortsNoms` n'a que **3
  consommateurs**, et tous les trois cherchent la chaîne **entière** comme clé
  exacte (`Epreuves.lua:103`, `Epreuves.lua:1165`, `Sorts.lua:866`). Il n'y a
  nulle part de substitution d'un nom **à l'intérieur** d'une phrase — et
  structurellement il ne peut pas y en avoir : `AFR.ParesseuxTexte` est une table
  à clé exacte, sans `pairs()`.
- **Preuve à l'écran.** Info-bulle réelle simulée sur le sort 18498, moteur
  complet chargé : le rendu final affiche **« …avec Shield Bash une chance de
  100 % … votre capacité Shield Slam de 5 % »**. Les deux noms restent anglais,
  alors que le pont les connaît (`Shield Slam` → `Heurt de bouclier`).
- **Combien.** 597 noms dont le français est identique à l'anglais (dont ~145 ne
  sont pas des noms de sorts et ~204 sont techniques). Surtout :
  **~1 662 descriptions** portent un nom de sort anglais, **~960** sur des sorts
  qu'un joueur voit vraiment, pour **648 noms distincts** à remplacer.
- **Officiel Blizzard : 0.** Aucun de ces noms n'a d'équivalent officiel — la
  règle par défaut ne s'applique pas ici. (Vérifié par le nom anglais, pas par
  l'ID : le piège du lot 5 est respecté.)
- **L'outil existant ne voit presque rien** : `reparer_noms_incrustes.py` exige
  un fragment coloré (`if "|c" not in fr: continue`) — **3 descriptions
  réparables sur 1 662**.

**Je n'ai rien corrigé**, comme demandé. Si tu lances ce chantier, deux
garde-fous sont indispensables, et ils ne sont pas évidents :
1. **la table des noms est empoisonnée** — 869 valeurs bidon (`X-Wing` → `0`,
   `Wild Imp` → `null`, `Wind Bolt` → `Trait d'eau`). Il faut un filtre de
   valeur, sinon 381 descriptions recevraient une saleté ;
2. **remplacer du plus long au plus court** — 53 descriptions ont des noms
   emboîtés (« Mana Tide » dans « Mana Tide Totem »). L'ordre naïf fabrique des
   chimères du genre « Glyph of Totem de griffe de pierre ».

---

### Ce qui attend une décision de toi

1. **« Millhouse Manastorm » → « Tempête de mana du moulin ».** Nom propre, donc
   ton arbitrage. Blizzard le laisse tel quel en français.
2. **Le verbe « drafter »** (16 entrées) — le seul mot que j'ai choisi.
3. **« Bassin Arathi » : tes deux sources officielles se contredisent.**
   Le DBC du client dit **« bassin d'Arathi »** (17 fois), la locale serveur dit
   **« Bassin Arathi »** (177 fois). Ton glossaire suit la seconde, ce qui est le
   bon choix — mais il reste **8 occurrences dans `DB_Sorts.lua`** qui viennent
   du texte officiel de Blizzard lui-même, pas de nos traductions. Les corriger
   voudrait dire réécrire l'officiel dans le générateur : je ne l'ai pas fait
   sans ton accord.
4. **6 libellés d'interface où « Casting » est un NOM**, pas le verbe :
   « Mouseover Casting » → « Casting par survol de la souris »,
   « Casting Damage Dealer » → « Casting Attaquant ». Ils veulent
   « incantation », pas « lancer » — je les ai **exclus** de la règle plutôt que
   de trancher un vocabulaire d'interface à ta place.

### Un fait à connaître, qui n'a rien à voir avec ce lot

**Le pipeline a tourné sur ta machine pendant que je travaillais.**
`rapports/caches/fusion/*.json` a été réécrit à **20:56** — des caches de joueurs
ont été ingérés. C'est ce qui fait bondir les files « à traduire » entre mes deux
régénérations (objets 3 → 153, créatures 0 → 154) : **100 % des nouvelles entrées
viennent de ce versement**, aucune de ma passe (vérifié entrée par entrée). Ça
explique aussi la modification de `sorts.json` que le rapport du lot 5 signalait
sans pouvoir l'expliquer.

Rien n'a été perdu — j'ai comparé chaque fichier à sa sauvegarde, les comptes
sont identiques. Mais si l'Atelier tourne en tâche de fond pendant qu'on écrit
dans `traductions/`, deux écritures peuvent se croiser. À savoir avant le build.

### Vérifications

- `verifier_tout.py` : **code retour 0**, 48 fichiers compilés en `lupa.lua51`,
  aucun jeton oublié, marges des bases affichées (DB_Sorts 49,7 %, DB_ObjetsNoms
  33 %, le reste sous 40 %).
- `verifier_motifs.py` (verrou addon/traducteur) : **0 échec**.
- pyflakes : muet sur tout ce qui a été touché.
- Bases régénérées (`generateur_sorts.py`, `generateur_db.py`,
  `generer_noms_objets.py`), et vocabulaire vérifié **dans l'addon** :
  « Tempête de mana » ×152, « Mande-étoiles » ×22, « Statique » ×218,
  « Build Draft » ×42, « Souffle abyssal » ×1, plus aucun « Cils légers ».
- **Aucune passe de masse** sur les 121 divergences ni sur les 1 762 conflits
  Glayna — le lot 5 (déjà fait) recommande de ne pas la lancer en l'état.
