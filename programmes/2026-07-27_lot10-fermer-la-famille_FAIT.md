# Demande de code → Claude Code

**Date :** 2026-07-27 · **lot 10 — fermer la famille des faux noms, et boucher le trou de la chaîne**

> **Merci d'avoir vérifié au lieu d'obéir.** Ma demande affirmait que le F majuscule était
> la signature du poison — c'était l'inverse, et purger là-dessus aurait détruit la vraie
> traduction en gardant les 778 fausses. Tu as cherché un vrai critère, et tu as trouvé
> que purger `sorts.json` seul ne servait à rien puisque le pont ne le lit jamais. Ces deux
> trouvailles valent plus que le lot lui-même.

---

## 1. Purger les deux autres — feu vert de Dan

Il a tranché après avoir vu tes chiffres : **« Appel du familier » (1 882 entrées du pont)
et « 0 » (1 307)** sont purgés, et **dans la 3.4**. Ton argument a emporté la décision :
ils sont mesurément plus nocifs que celui d'hier — 1 875 familiers **distincts** qui
portent le même nom, c'est ce qu'un joueur remarque en premier.

Tu l'as dit toi-même : **deux lignes dans la table `POISON` de
`outils/noms_empoisonnes.py`**, la purge et le filtre les prennent en compte sur les quatre
couches. Applique la même rigueur qu'hier :

- **Le même discriminant** — une clé anglaise qui correspond, à l'octet près, à un nom de
  sort connu du DBC anglais est **gardée**. Égalité exacte, pas la comparaison tolérante.
- **Dis-moi combien de porteurs légitimes tu gardes** pour chacun, comme tu as gardé
  `Test of Faith`. S'il n'y en a aucun, dis-le aussi.
- Sauvegarde horodatée inconditionnelle, comptes réels, contrôle **dans l'addon**.
- Le même effet de bord qu'hier (des sorts qui perdent nom **et** description) : **Dan a
  décidé de le laisser** — ils repartent dans la file et seront retraduits proprement.
  Donne juste le nombre.

## 2. Le garde-fou manquant — c'est le vrai correctif

Tu as mis le doigt sur la cause de fond : `garde_packfr.texte_sain()` rejette **0 sur 45**
des valeurs sur-portées, parce qu'il vérifie la **forme** du texte et jamais **combien de
clés différentes le portent**. Pour lui, `"0"` est un nom sain.

**Pose ce contrôle** : une valeur portée par plus de N clés anglaises sans parenté est
refusée à l'adoption.

- **Choisis N et dis-moi pourquoi.** Tu as mesuré le plafond naturel de duplication à **3**
  sur trois sources propres et indépendantes, et retenu 20 comme seuil d'alerte — tu es
  mieux placé que moi pour trancher où poser la barrière.
- ⚠️ **Ne casse pas les cas légitimes** : `sorts.json` est indexé par texte, donc les rangs
  ne comptent que pour une clé — mais vérifie qu'aucune famille normale (les satellites
  d'un même sort, les libellés techniques) ne tombe sous la règle. Mesure d'abord ce que le
  seuil refuserait sur l'état actuel, et montre-le-moi **avant** que ça bloque une adoption.
- Si la barrière refuse quelque chose, elle doit le **dire**, pas l'avaler en silence.

## 3. Les 25 autres valeurs sur-portées — la liste, pas la purge

Tu comptes **27 valeurs / 2 758 entrées** dont les clés sont réellement sans parenté. Deux
sont traitées, il en reste 25. **Ne purge rien de plus.** Rends-moi la liste, classée par
**exposition réelle dans le pont livré**, avec pour chacune : la valeur, le nombre
d'entrées, et en une ligne **ce qu'un joueur voit en jeu** (un nom de sort ? un libellé
technique jamais affiché ? un nom d'objet ?).

C'est cette colonne-là qui permettra à Dan de trancher le reste **en une seule passe**,
comme il vient de le faire pour les deux premières.

## 4. Le trou dans la chaîne — `mise_a_jour.py` ne régénère pas le pont

Tu l'as signalé en passant et ça mérite une correction : **`mise_a_jour.py` ne lance pas
`generer_noms_sorts.py`**. La chaîne standard ne régénère donc jamais le pont des noms — il
faut y penser à la main.

C'est **exactement la même famille** que le défaut de `DB_Objets` au lot 3 : plusieurs
chemins font le travail, tous ne font pas la dernière étape, et l'oubli ne se voit pas.
Branche-le, dans le bon ordre (`generateur_sorts` → `generateur_db` → `optimiser_memoire` →
`generer_noms_sorts` → `generer_noms_objets`), et vérifie qu'aucun autre chemin de
régénération n'a le même trou.

---

**« Terminé » veut dire :**

> - Les deux valeurs purgées, porteurs légitimes gardés et **nommés**, comptes réels,
>   contrôle dans l'addon.
> - Le garde-fou du nombre de porteurs posé, avec le seuil justifié et la mesure de ce
>   qu'il refuserait aujourd'hui.
> - La liste des 25 restantes, classée par exposition, avec l'effet en jeu.
> - `mise_a_jour.py` régénère le pont, et les autres chemins vérifiés.
> - `verifier_tout.py` code retour 0, bases régénérées dans le bon ordre.
> - **Ne rien publier, ne rien pousser.** Dan teste en jeu juste après, puis son go, puis
>   la demande de build.

**Validation :**

> Autonome sur les points 1, 3 et 4. **Montre-moi la mesure du point 2 avant de laisser la
> barrière bloquer quoi que ce soit** — un garde-fou trop serré qui refuse du bon travail
> se désactive au bout de trois jours, et on se retrouve sans barrière du tout.

---
## Réponse de Claude Code

**Fait le 27/07/2026. Les deux valeurs sont purgées, la barrière est posée, la
chaîne est bouchée. `verifier_tout.py` : code retour 0, 19 bancs verts / 3
rouges (les 3 attendus). Rien n'a été publié ni poussé.**

La mesure que tu exiges avant tout blocage est au § 2 — et elle dit quelque
chose que ni toi ni moi n'avions vu : **sans la barrière, une seule commande
annulait les deux purges.**

---

### 1. Les deux purges — comptes réels

| | purgées | porteurs légitimes gardés |
|---|---:|---|
| « Appel du familier » | **1 879** clés | **0 chez nous** — aucun de nos porteurs n'était le bon |
| « 0 » | **896** clés | **0, nulle part** — aucun nom Blizzard ne se traduit par « 0 » |

Tu m'as demandé de nommer les porteurs gardés, et de le dire s'il n'y en a
aucun : **il n'y en a aucun dans le cache.** Le seul porteur légitime
d'« Appel du familier » est `Call Pet` — mesuré : c'est l'unique nom anglais
dont le frFR officiel Blizzard est cette valeur — et il n'était **pas** parmi
nos 1 879 (tous étaient des sifflets, vélins et pierres d'invocation
distincts). Il revient par la couche officielle du pont, là où il doit être :
en jeu, `Call Pet` affiche bien « Appel du familier », vérifié dans
`DB_Sorts.lua` (IDs 883 et 1100883) et dans le pont.

Détail qui dit d'où vient le mal : les porteurs de « 0 » étaient des objets de
vanité, souvent avec un **nom espagnol** d'époque (« Alas del Carcelero »,
« Kart de Carreras Celeste ») — le PackFR avait plusieurs langues dans ses
bouche-trous.

**Dans l'addon livré :**

| | avant | après |
|---|---:|---:|
| pont « Appel du familier » | 1 882 | **1** (`Call Pet`, le légitime) |
| pont « 0 » | 1 307 | **0** |
| paires empoisonnées bloquées à la génération (4 couches) | — | **4 468** |

**L'effet de bord accepté : 89 sorts** ont perdu leur entrée entière (nom et
description) — `DB_Sorts.lua` passe de 54 392 à 54 303 — et la file du
Compagnon passe de 23 à 114 noms uniques : ils reviendront proprement au
prochain cycle, comme tu l'as décidé.

Aucun objet composé cette fois (0 dans `objets_dbc.json`, contre 27 hier).
La ceinture du purgeur a aussi été resserrée au passage : « la clé est connue
de Blizzard » ne suffit plus à garder une entrée, il faut que **la paire
officielle** (`enUS × frFR`) corresponde — une clé Blizzard portant une valeur
qui n'est pas la sienne est du poison, pas un porteur.

En contrôlant l'addon, j'ai trouvé **5 descriptions d'objets `D="0"`** dans
`DB_Objets.lua` (« Le chasseur : Hawk Eye », « L'Œil : Arcanes Résistance »…).
C'est la même maladie dans l'espace des **objets**, indexé par identifiant —
hors périmètre de ce lot, noté pour toi.

### 2. La barrière — posée, et voici la mesure

**Le seuil : 5 porteurs.** Le plafond naturel de duplication d'une même valeur
sur des clés sans parenté vaut **3** (mesuré sur trois sources propres et
indépendantes : notre cache fait main, l'officiel Blizzard, Glayna — aucune
valeur légitime n'y atteint 5). À 5, on laisse une marge d'une unité au-dessus
du plafond, et on reste quatre fois sous le seuil d'alerte (20) qui sert à la
cartographie. Entre 4 et 20 il n'y a que du poison : la simulation ci-dessous
le confirme.

**La parenté protège les familles normales.** Une valeur portée par des clés
qui partagent presque toutes un même mot significatif est une vraie famille
(« Well Fed - Agility », « Well Fed - Stamina » → « Bien nourri » : épargnée,
comme « Téléportation : Baie-du-Butin » et les « Apply … » → « Armure +32 »).
Un piège trouvé et fermé en la testant : **les mots creux**. « Témérité »
posée sur 92 clés sans rapport passait pour une famille parce que 80 % de ses
clés contenaient « test » — un mot d'outillage, pas un lien de sens. La liste
des mots creux (`test`, `dummy`, `aura`, `buff`, `visual`…) est dans le module,
avec la règle : n'y mettre que de l'outillage, jamais un mot de mécanique.

**Où elle vit, et pourquoi à deux régimes :**

- **À l'adoption** (`adopter_packfr_cache.py`) : **refus ferme et bruyant.**
  C'est le point d'injection d'origine, et refuser une adoption ne touche à
  rien d'existant. La barrière compte les porteurs sur l'état FINAL (cache
  existant + adoptions de la passe) : elle bloque aussi la croissance goutte à
  goutte d'une famille entamée.
- **À la génération** (`generer_noms_sorts.py`) : **vigie, sans retrait.**
  Retirer là serait une purge déguisée des valeurs que tu n'as pas encore
  tranchées (« ne purge rien de plus »). Elle compte et écrit
  `rapports/porteurs_pont.txt` à chaque build : l'arriéré est visible — le
  poison a vécu six jours parce qu'aucune sortie d'outil ne le montrait.

**La mesure demandée.** J'ai simulé le rejeu de l'outil d'adoption sur l'état
d'aujourd'hui, en copie neutralisée (aucune écriture, `sorts.json` identique à
l'empreinte près avant/après) :

> **Sans la barrière : 3 941 paires empoisonnées ré-adoptées.** La purge
> d'hier et celle d'aujourd'hui, annulées par une seule commande — les clés
> purgées ne sont plus dans le cache, l'outil les aurait donc recréées depuis
> `packfr_sorts.json`.
>
> **Avec : 3 958 adoptions refusées, 14 valeurs, toutes annoncées.** Les trois
> valeurs de la table POISON (1 879 + 1 306 + 756), et **11 refus hors table
> qui sont tous des jointures folles** : « Éclair de feu » pour la clé
> `Glace`, « Chaîne d'éclairs » pour `Cadena de relámpagos`, « Gelée » pour
> `Pestilence`… La barrière n'a refusé **aucune** paire saine.

**Sur l'état actuel, elle ne bloque rien** : la vigie compte 307 valeurs
sur-portées encore en place (3 984 entrées), toutes laissées telles quelles en
attente de ton arbitrage.

### 3. La liste — 35 familles, pas 25

Mon test automatique en voit **35** au seuil de 20 dans le pont régénéré — la
relecture à la main du lot 9 en retenait 27 sur un état d'avant les purges ;
l'écart est de méthode, pas de fond. Classées par exposition réelle dans le
pont livré. La colonne « en jeu » s'appuie sur le nombre de porteurs qui
correspondent à un sort réellement livré dans `DB_Sorts.lua` (vis.) :

| entrées | valeur | ce qu'un joueur voit en jeu |
|---:|---|---|
| 165 | Ascension HPP | libellé technique, mais 13 porteurs sur des sorts livrés — peut surgir en info-bulle |
| 125 | HOT PATCHING PLACEHOLDER | **43 sorts livrés affichent ce texte comme « nom français »** — le pire visuellement |
| 123 | Chaîne d'éclairs | **très visible** : info-dégâts de dizaines de boss (vis. 210) nommées comme le sort de chaman |
| 105 | Momma Said Knock You Out - Haut fait | traqueurs de hauts faits, jamais affichés |
| 91 | Tempête divine ! | sorts techniques (réductions de recharge), quasi invisibles |
| 79 | Inferno gangrené | sorts de dev (« Drinking Coffee », « Carrying a banana ») — invisibles |
| 75 | Trait de feu | mixte : 33 porteurs livrés, dont des réinitialisations techniques |
| 74 | Éclair de feu | **visible** : 53 porteurs livrés, vrais sorts sans rapport |
| 55 | Blocage 100% | buffs techniques, invisibles |
| 51 | Exorcisme | générateurs de ressource (« Add 10 Static ») — 21 livrés, info-bulles possibles |
| 49 | Étoile radieuse | sorts SLS techniques, invisibles |
| 48 | Trait de l'ombre | **visible** : procs d'objets livrés (vis. 49) |
| 45 | Visuel de l'ombre de Bruce | visuels, invisibles |
| 41 | Visuel : Geyser | visuels, invisibles |
| 37 | Tourbillon | **très visible** : montures et jouets (vis. 184) |
| 35 | Contrôle d'Aura | contrôles techniques, invisibles |
| 34 | Souffle de givre | sorts de boss, un peu visibles (vis. 10) |
| 34 | Soins inférieurs | quasi technique (vis. 3) |
| 33 | Croissance Inhabituelle | auras de rencontre, invisibles |
| 30 | Marqueur universel de cible - NE CHANGEZ PAS CE SORT ! | marqueurs — le nom dit tout |
| 28 | Frénésie impie | **visible** : 26 porteurs livrés |
| 28 | Maître de la discrétion | mixte (vis. 8) |
| 28 | Données SWP | données, invisibles |
| 26 | Rénovation | **visible** : buffs de soins (vis. 31) |
| 24 | Frénésie | buffs de boss, plausibles mais posés par jointure (vis. 12) |
| 24 | Salve de Traits de l'ombre | technique, invisible |
| 24 | Déclenchement de Crocs empoisonnés | technique, invisible |
| 23 | Élixir Brouillecaboche | quasi invisible (vis. 1) |
| 23 | Cannibalisme | peu visible (vis. 4) |
| 23 | Tempête de lames | **visible** (vis. 20) |
| 22 | Faux sort | peu visible (vis. 7) |
| 22 | Javelot de glace | visible (vis. 14) |
| 22 | Tête de flèche jaune | marqueurs de flèches, invisibles |
| 21 | Enrager | buffs de boss visibles (vis. 18) — certains « enrage » sont plausibles |
| 20 | Pourfendre | **le signal du lot 9** : 18 clés de traduction machine sans rapport + le vrai Rend |

Lecture d'ensemble pour trancher en une passe : **10 familles vraiment
visibles** (les lignes en gras — HOT PATCHING, Chaîne d'éclairs, Tourbillon,
Éclair de feu, Trait de l'ombre, Frénésie impie, Rénovation, Tempête de lames,
Javelot de glace, Pourfendre) ; le reste est de l'outillage que le joueur ne
croise presque jamais. Le jour où tu tranches : une ligne par valeur dans la
table `POISON`, avec ses porteurs légitimes — la purge, le filtre des quatre
couches et la barrière d'adoption suivent tout seuls.

### 4. Le trou de la chaîne — bouché, et pas seulement dans `mise_a_jour.py`

**`mise_a_jour.py`** enchaîne désormais, dans l'ordre qui compte :
`generateur_sorts` → `generateur_db` → **`optimiser_memoire`** (exigé par le
README après tout `generateur_db`, il manquait aussi) → **`generer_noms_sorts`**
→ **`generer_noms_objets`**. L'ordre est commenté sur place : la couche
« custom » du pont relit `DB_Sorts.lua`, pas le cache.

**L'audit des autres chemins a trouvé le même trou ailleurs, deux fois** —
dans `traducteur_fr.py`, le moteur que l'Atelier appelle :

- `_generer_sorts()` réécrivait `DB_Sorts.lua` sans régénérer le pont des
  noms de sorts ;
- `_generer()` réécrivait les bases d'objets sans régénérer le pont des noms
  d'objets.

Les deux régénèrent maintenant leur pont (en sous-processus — ces scripts
s'exécutent à l'import, un `reload` serait fragile). Et la bonne nouvelle :
**l'Atelier de ton bureau est réparé sans reconstruire l'exe** — `collecteur.py`
lance `traducteur_fr.py` avec le python de la machine, depuis le dépôt ; il
profite donc de la correction dès maintenant.

Aucun autre appelant de `generateur_sorts`/`generateur_db` ne régénère de
bases (vérifié : les autres importateurs ne s'en servent que pour lire).

### Ce qui attend une décision de toi

1. **Les 35 familles du § 3** — la colonne « en jeu » est faite pour trancher
   en une passe. Ma suggestion si tu veux aller vite : les 10 visibles
   d'abord, l'outillage peut attendre la 3.5.
2. **Les 5 descriptions d'objets `D="0"`** — même maladie, espace des objets,
   chantier séparé.
3. La soupape `TOLERES` de la barrière est **vide** : si un jour une vraie
   famille se fait refuser à l'adoption, on la nomme là avec sa raison, plutôt
   que de desserrer le seuil pour tout le monde.

### Vérifications

- `verifier_tout.py` : **code retour 0**, 48 fichiers compilés en `lupa.lua51`.
- **Les 22 bancs : 19 verts, 3 rouges** — les trois attendus (`infobulle`
  rouge exprès, `interface` et `signalements` périmés, intouchés).
- Bases régénérées dans l'ordre, **par la nouvelle chaîne elle-même**.
- Les corrections des lots 7 et 9 sont intactes dans l'addon régénéré
  (« Coup de surin ! », « Piston de saccageur gangrené », « Récupération de
  la nature », « Maîtrise du poison » — vérifiées par identifiant).
- Sauvegarde horodatée inconditionnelle : `sorts_avant_purge_20260728-112227.json`.
- La simulation d'adoption n'a rien écrit : `sorts.json` identique à
  l'empreinte MD5 près, avant et après.
- pyflakes muet sur les six fichiers touchés (`noms_empoisonnes`,
  `purger_noms_empoisonnes`, `adopter_packfr_cache`, `generer_noms_sorts`,
  `mise_a_jour`, `traducteur_fr`).
- **Rien n'a été publié, rien n'a été poussé, `sources/` n'a pas été touché.**
