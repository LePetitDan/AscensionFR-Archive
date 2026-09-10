# Demande de code → Claude Code

**Date :** 2026-07-28 · **lot 14 — les trous d'application, les libellés de cartes, et la matière CoA**

> **Le lot 13 est excellent.** Les pertes réelles à 51 au lieu de 487 (la projection comptait
> les copies d'identifiants que le générateur rattrape), `Whirlpool` réintégré aux porteurs
> légitimes avec le pourquoi, `Ice Breath` désambiguïsé par la retraduction, et la vigie
> objets corrigée **avant** de me donner son chiffre parce que le comptage naïf était gonflé
> d'un facteur dix. C'est exactement la façon de travailler qui a rendu ces cinq jours utiles.
>
> ⚠️ **Nouvelle consigne de Dan (28/07) : plus d'urgence de sortie.** « On fait tout avant de
> sortir une 3.4, je déciderai le moment venu. » Prends le temps de bien faire. Si un point
> demande une journée de plus, dis-le au lieu de le rogner.

---

## Le constat de départ : deux captures de Dan, deux maladies différentes

**Capture 1 — sort 3599, « Totem incendiaire » (Rang 1).** Le jeu affiche la description en
**anglais**. Or elle est **complète en français dans `DB_Sorts.lua`**, nom compris. Sa
particularité : son `D` commence par **`@learns:92159@`** — et les cas `@learns:`/`@req:` ont
été mis **hors périmètre** au lot 3.

**Capture 2 — carte de compétence « Pure Shadow (Rank 1) » (royaume Wildcard).** L'info-bulle
affiche bien **« Ombre pure »** en titre — la traduction existe (`"Pure Shadow": "Ombre
pure"`). Mais le **libellé sous l'icône reste en anglais**. Et la **description** de ce talent
n'est, elle, **dans aucune de nos sources** (phrase cherchée, absente).

Donc : d'un côté des traductions qui existent et ne s'appliquent pas, de l'autre une matière
qui manque. Les deux sont à traiter, mais pas de la même façon.

---

## 1. Les trous d'application côté sorts — mesurer avant de réparer

Ce que j'ai compté dans `DB_Sorts.lua` (54 463 entrées, 47 920 avec description) :

| suspect | combien |
|---|---:|
| `D` commençant par `@learns:` (dont le totem de Dan) | **28** |
| `D` contenant `@req:` | **370** |
| `D` et `DE` en désaccord sur les retours à la ligne (`\r\n` vs `\n`) | **1 257** |
| entrées **sans aucune description**, ni FR ni EN | 6 543 |

**Ce sont des suspects, pas un diagnostic.** La seule preuve qui compte est celle que tu as
utilisée aux lots 3 et 7 : **faire tourner le vrai moteur de l'addon** sur l'info-bulle que le
client afficherait, et comparer avant/après. « Être dans la base ≠ s'afficher. »

**Ce que je te demande :**

1. **Combien de sorts, réellement, affichent l'anglais alors que leur français est en base ?**
   C'est le chiffre qui manque à tout le monde depuis le début. Mesure-le en rejouant le
   moteur, pas en lisant les fichiers.
2. **Classe les causes** et donne le compte de chacune. Mes trois suspects en font peut-être
   partie, peut-être pas — et il y en a sûrement d'autres.
3. **Répare ce qui est réparable sans risque**, en commençant par le cas de Dan (`@learns:`).
   Montre-moi le rendu à l'écran avant/après sur le sort 3599, comme tu l'as fait pour les
   conditionnels.
4. Les **6 543 sans description** : dis-moi juste ce que c'est (des sorts internes ? des
   entrées de nom seul ?) — ça peut être normal, je veux savoir.

## 2. Les libellés des cartes de compétence et des talents

« Pure Shadow (Rank 1) » s'affiche en anglais alors que **« Ombre pure » est connu**. Trouve
le chemin d'affichage de ce libellé et applique la traduction — y compris le « (Rank 1) », qui
devrait être « (Rang 1) » comme ailleurs.

🛑 **Arrête-toi et dis-le-moi** si l'appliquer oblige à écrire une globale relue par du code
protégé, ou à toucher un cadre sécurisé. La doctrine taint prime sur ce libellé : un joueur
qui ne peut plus lancer ses sorts est infiniment pire qu'un nom anglais.

## 3. La matière des descriptions CoA — la question qui décide du reste

~120 des 204 signalements des joueurs sont des talents dont **la description n'existe nulle
part chez nous** (`sources/coa_arbres.json` : 3 928 identifiants, structure seule).

**La question : cette matière est-elle récupérable ?** Piste sérieuse — le pipeline garde un
cache complet de **db.ascension.gg** (`cache_db/`, 11 189 fiches) et `recuperer_db.py` sait
l'interroger. Si le site publie les descriptions de talents, tout le chantier s'ouvre.

Regarde, dans cet ordre, et dis-moi ce que chacune donne :
1. le cache `cache_db/` — contient-il déjà des descriptions de talents ?
2. le site db.ascension.gg — les publie-t-il, et sous quelle forme ?
3. le client lui-même (DBC, caches WDB, le constructeur CoA) — y a-t-il un gisement qu'on
   n'a pas encore lu ?

**Si la matière existe et que la récolte tient en moins d'une heure sans risque : enchaîne**
(Dan a dit qu'on fait tout avant de sortir). **Sinon, chiffre-la et arrête-toi** : volume,
durée, risque, et ce qu'il faudrait écrire. Je te ferai une demande dédiée.

---

**« Terminé » veut dire :**

> - Le nombre **réel** de sorts affichant l'anglais malgré une traduction en base, causes
>   classées et chiffrées.
> - Le cas de Dan (sort 3599) réparé, avec le rendu avant/après **à l'écran**.
> - Les libellés de cartes et de talents traduits — ou l'explication de pourquoi c'est
>   impossible sans risque de taint.
> - La réponse chiffrée sur la matière CoA : récupérable ou non, et à quel prix.
> - `verifier_tout.py` code retour 0, bancs 19/3, bases régénérées par la nouvelle chaîne,
>   lots 7/9/10/11/13 vérifiés intacts.
> - **Ne rien publier, ne rien pousser.**

**Validation :**

> Autonome, **sauf** : l'arrêt taint du § 2, et l'arrêt du § 3 si la récolte CoA dépasse une
> heure ou demande d'écrire un outil neuf.

---
## Réponse de Claude Code

**Fait le 28/07/2026. Le chiffre qui manquait existe, le sort de Dan est réparé
et montré sur sa propre capture, le libellé des cartes est traduit sans arrêt
taint, et la matière CoA réserve une surprise : elle était déjà là.**
`verifier_tout.py` : code 0, bancs 19/3, chaîne complète rejouée, lots
7/9/10/11/13 intacts. Rien publié, rien poussé.

---

### 1. Les trous d'application — le chiffre réel, les causes, les réparations

**Le chiffre qui manquait à tout le monde : 2 433 sorts sur 49 676 (4,9 %)
affichent l'anglais alors que leur français est en base.** Mesuré en rejouant
le VRAI moteur (lupa.lua51, `TraduireInfobulleSort` complet) sur la population
**entière** — pas d'échantillon, 16 secondes. En jeu, la couche communautaire
en rattrape 337 : **≈ 2 100 nets**, fourchette 1 600–2 200 (le simulateur a un
biais optimiste ET un biais pessimiste, tous deux chiffrés). Le chiffre a été
reproduit à l'identique par un second banc indépendant — différence
symétrique : zéro.

**Les causes, classées — et tes trois suspects jugés :**

| cause | échecs | mécanisme |
|---|---:|---|
| faux appariements PackFR (le D ne traduit PAS le DE) | **649** | encore la jointure par identifiant |
| clones décalés (+1 100 000) | **897** | le D officiel référence `$64843s2`, le DE du clone dit `$1164843s2` |
| variables absorbantes adjacentes | 370 | limite du moteur (captures paresseuses), chantier futur |
| marqueurs maison d'un seul côté (**le cas de ton totem**) | ~160 | voir ci-dessous |
| options `$l`/`$L` traduites par Blizzard | 111 | « effets magiques » ne retrouve jamais « effects » |
| divers (variables abîmées, textes courts…) | ~250 | classés au rapport |

Tes suspects : **`@learns:` coupable** (26 échecs sur 29 — le DE ne porte
jamais le marqueur), **`@req:` presque innocent** (46 sur 370 : les 352 autres
l'ont des deux côtés et s'alignent très bien), **`\r\n` symptôme et non
cause** (12 vrais cas seulement).

**Le mécanisme du cas de Dan, précisément :** `@learns:`/`@req:` sont bien
gérés par le moteur (`MOTIFS_VARIABLE`, Sorts.lua:62-64). Ce qui casse, c'est
un marqueur présent **côté français seulement** : la valeur à insérer est
indexée par les variables du modèle ANGLAIS, un marqueur FR sans jumeau EN
vaut nil, et le moteur abandonne TOUTE la description (Sorts.lua:275-276).
D'où vient ce déséquilibre ? **De la jointure PackFR par identifiant** —
prouvé : `packfr_sorts.json["3599"].D` est exactement la valeur polluée de
notre cache, rangée sous la clé DBC propre. Le poison des noms et les trous
d'alignement sont la même maladie.

**Les réparations appliquées** — par un outil durable
(`outils/reparer_alignement_sorts.py`, simulation par défaut, idempotent),
chaque entrée sous un garde-fou **fail→success** : on ne touche que ce qui
échoue au banc, on n'adopte que ce que le banc voit réussir après. Le
garde-fou a servi : **12 clés exclues** parce qu'un sort sain les partage
(dont 2 des 4 casses que l'étude avait prédites sans lui).

| réparation | posée |
|---|---:|
| resynchronisation D↔DE (marqueurs) | **97 sorts** (64 clés) |
| remap des clones +1 100 000 | **874 sorts** (653 clés) |
| purge des faux appariements atteignables + famille « Follow Up » | **291 sorts** (222 clés → file de retraduction) |
| patch `$l`/`$L`/`$g`/`$G` dans Modules/Sorts.lua | **89 sorts rescapés** |
| francisation des plages (« 11 to 14 » → « 11 à 14 ») | toutes les valeurs insérées |

**Bilan au banc : 2 433 → 1 093 échecs.** Et la preuve exigée : le patch
Sorts.lua a été validé en comparant les **sorties hachées** des 49 676 entrées
— 89 changements, tous les rescapés attendus, **zéro autre** (le premier jet
du patch dégradait silencieusement 2 affichages officiels ; le sceptique l'a
vu, le patch posé tente le sauvetage `$l` seulement quand aucun modèle D2/DE2
ne réussit déjà).

**Ton totem, sur ta propre capture** (les 8 lignes exactes de tes
SavedVariables, moteur vierge) :

> AVANT : « Summons a Searing Totem with 5 health at your feet for 45 sec… »
> APRÈS : « Invoque un Totem incendiaire avec 5 points de vie à vos pieds
> pendant 45 sec, qui attaque à plusieurs reprises un ennemi dans un rayon de
> 20 mètres pour **11 à 14** dégâts de Feu. / Cette technique peut être
> utilisée en étant transformé. »

(Et en prime, le sort 8184 — bloc `@ext:` replié « Hold SHIFT » — sort aussi
en français sur sa capture réelle. En jeu : un `/reload` suffit, le
coupe-circuit des échecs récents garde l'anglais jusque-là.)

**Les 6 543 sans description : normal.** 6 503 n'ont pas non plus de
description dans le DBC d'Ascension (sorts d'objets, glyphes, passifs DND —
des entrées de nom seul, voulues) ; les 13 restants qui en ont une sont déjà
tous dans la file de traduction.

**Ce qui reste (1 093), et où ça ira :** 362 des 649 faux appariements sont
**hors de portée du cache** (leur D vient de la voie officielle par ID ou des
corrections) — lot dédié à prévoir ; 370 tiennent à la limite des variables
absorbantes du moteur (chantier d'après) ; le reste est classé au rapport.
**Et pour que ça ne revienne pas :** barrière de structure à l'adoption
(marqueur d'un seul côté, variable sans jumeau = refus bruyant), vigie de
sortie qui signale AUSSI le franglais qui s'aligne, et les 222 clés purgées
sont **interdites de ré-adoption** (liste dans
`traductions/cles_interdites_readoption.json` — 71 d'entre elles n'ont aucun
défaut de structure, seule cette liste les arrête).

### 2. Le libellé des cartes — traduit, et l'arrêt taint n'a pas lieu

**Le chemin trouvé :** le libellé sous l'icône est **composé à l'affichage**
par la révélation Wildcard (`WildCardNameFrameButtonMixin:SetInternalID` :
`nom .. " (" .. RANK .. " " .. rang .. ")"`) — l'unique composition
« nom (Rank n) » de tout le client extrait. Aucun nom de sort ne contient
« (Rank » : la clé exacte du pont ne pouvait jamais mordre. (L'info-bulle,
elle, passe par un autre chemin — d'où ton titre « Ombre pure » déjà
français.)

**🛑 L'arrêt taint : NON, et confirmé sous attaque indépendante.** Aucune
globale écrite (le canal `Interdite()`/`DB_LuesClient` n'est pas emprunté),
zéro cadre sécurisé dans les deux addons de cartes (0 `Secure*`/`protected`),
aucun code client ne relit ce libellé, le drag passe par l'API des sorts.

**Mais le patch n'a pas été posé tel quel** — le sceptique a montré qu'il
ouvrait une surface neuve au poison du pont : **33 noms révélables** en
Wildcard portent au pont une valeur qui contredit le français officiel
unanime, dont deux **déjà corrompues aujourd'hui** (« Vendetta » →
« VenVerrouillage de la cibleetta », « Vengeance » → mojibake « FrÃ©nÃ©sie »)
et l'« Absolution » → « Le Bastion » de ta mémoire de projet. Donc, dans
l'ordre :

1. **le pont d'abord** : `outils/purger_pont_cartes.py` — 11 corrections dans
   le cache, et pour les couches qu'on ne possède pas (23 valeurs viennent du
   PackFR), un **verrou par clé** dans la table du poison : 32 des 33 sortent
   propres à la régénération, vérifié dans le pont livré. La 33ᵉ,
   « Smolder » → « Braises », vient de la couche Glayna : notée pour toi ;
2. **puis le patch** dans Epreuves.lua, chemins Composee et
   FrancaisLigneCalcul — ce dernier consulte `AFR.DB.ObjetsNoms` **avant** le
   pont (sans ça, 175 objets « … (Rank n) » étaient demi-traduits et 34
   contredits) ;
3. **la preuve après pose**, au banc du sceptique (celui qui charge
   ObjetsNoms) : 26/26 — « Pure Shadow (Rank 1) » → **« Ombre pure
   (Rang 1) »** sur les deux chemins, « Cleanse (Rank 5) » → « Purifier
   (Rang 5) » inchangé, le « (Rank 12) » du grade JcJ intouché.

En prime : les 4 messages « Talent Unlocked! » de la même carte passent au
français par le canal CHROME (affichage seul, jamais écrits — vérifié).

### 3. La matière CoA — elle existe, et elle était déjà chez nous

**Ta prémisse était fausse, dans le bon sens : `coa_arbres.json` n'est pas
« structure seule ».** Il embarque une description anglaise pour la totalité
des 3 928 identifiants. Et trois gisements se recouvrent :

| gisement | couverture |
|---|---|
| `coa_arbres.json` | 3 840/3 928 descriptions utiles (HTML, nombres calculés) |
| `cache_db/` (db.ascension.gg) | 3 853/3 928 fiches, 3 845 utiles |
| **le client** (`spells_Ascension.json`) | **3 928/3 928**, dont 3 527 en vrais gabarits `$` — la source la plus fidèle |

**Et le français existe déjà pour les 3 928** : 2 484 dans `DB_Sorts.lua`
(modèles sains, identiques au DBC) + 1 444 dans `DB_SortsCorrections.lua`.
La seule récolte restante (75 fiches de cache) tiendrait en ~53 secondes au
débit mesuré (8 sondes réseau, 0,30 s/req)… et n'apporterait **rien** que le
client n'ait déjà. Je ne l'ai pas lancée : ce serait du mouvement, pas du
progrès.

**Le vrai chantier derrière tes ~120 signalements n'est donc pas la matière —
c'est l'affichage et la qualité.** Deux mesures pour ta prochaine demande :

- le constructeur CoA est une fenêtre maison : « être en base n'est pas
  s'afficher » — il faut la mesure au moteur de ce qu'il affiche, puis
  l'interception par familles de composants (la doctrine des fenêtres
  maison) ;
- l'audit hors réseau des 1 515 entrées CoA des corrections : **1 510 ont un
  modèle d'époque « site »** (nombres calculés — leur alignement en jeu est
  non prouvé, c'est leur construction même), **264 ont des variables sans
  jumeau anglais** (alignement impossible — vrais défauts), 38 marqueurs d'un
  seul côté, 10 franglais. Et au moins un appariement FR/EN faux prouvé
  (`DB[560906]` décrit un autre sort) — cette classe-là ne se compte pas
  mécaniquement.

### Ce qui attend une décision de toi

1. **Les 7 changements collatéraux** du nettoyage du pont cartes (même
   maladie, hors périmètre — listés dans `rapports/pont_cartes_lot14.txt`,
   veto possible valeur par valeur, 2 deviennent corrects, 2 repassent à
   l'anglais, 3 troquent une erreur contre une autre).
2. **« Smolder » → « Braises »** (couche Glayna) : l'officiel unanime est
   « Smolder ». Une ligne à trancher.
3. **« Talents débloqués ! » au pluriel pour UN talent** (chrome Wildcard) —
   la valeur vit dans le cache interface.
4. **Deux lots à prévoir** : les 362 faux appariements hors de portée du
   cache, et le chantier d'affichage du constructeur CoA (avec l'audit
   qualité des 264 corrections à variables impossibles).

### Vérifications

- `verifier_tout.py` : **code 0** ; **bancs 19/3** (les trois rouges
  attendus) ; `verifier_infobulle` : 8 ok + **exactement 1** échec assumé —
  les patchs de Sorts.lua et Epreuves.lua n'ont rien déplacé ;
  `verifier_motifs` : 0 échec (`MOTIFS_VARIABLE`/`MOTIFS_PROTEGES` intacts).
- Bases régénérées **par la chaîne complète** (`mise_a_jour.py`), les deux
  vigies visibles dans sa sortie ; 3599 vérifié réparé dans la base LIVRÉE.
- Lots 7/9/10/11/13 **intacts** (vérifiés par identifiant).
- Sauvegardes horodatées : cache (×2), Sorts.lua, Epreuves.lua — chemins au
  rapport. Tout .lua posé a compilé en lupa.lua51 AVANT la pose.
- pyflakes muet sur les huit fichiers python touchés.
- **Rien n'a été publié, rien n'a été poussé.**
