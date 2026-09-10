# Demande de code → Claude Code

**Date :** 2026-07-26 · **lot 5 — fiabilité de l'appariement « officiel Blizzard »**

> ✅ **Sans risque, exécutable tout de suite** — cette demande ne modifie **aucun** fichier
> de traduction. Elle mesure. Elle n'attend ni le lot 3 (DB_Objets) ni le lot 4.
> Mais son résultat **conditionne** la passe de masse prévue au lot 4.

---

## Pourquoi cette demande

Dan a tranché le 26/07 une règle par défaut : **quand notre traduction et l'officiel
Blizzard divergent, l'officiel gagne** (sauf quand l'officiel perd du sens). C'est ce qui
doit permettre de traiter en masse les **121 divergences** et les **1 762 conflits Glayna**.

En relisant `traductions/divergences_officielles_a_arbitrer.txt`, j'ai trouvé des entrées
où la colonne « officiel » ne correspond **pas** à l'entrée anglaise :

| EN | « officiel » retenu | ce qui cloche |
|---|---|---|
| `Armor (Light)` | Armure **+8** | sans rapport |
| `Axe and Fist Weapons Specialization` | Spécialisation **Hache** | perd « et à poing » |
| `Armored Spectral Tiger` | Tigre spectral | perd « blindé » |
| `Black War Bear (Brown)` | Ours de guerre noir | perd la couleur |

Les **45 déjà appliquées** sont bonnes — elles réparaient du demi-anglais
(« Bénédiction de Kings » → « Bénédiction des rois »). Le problème n'est donc pas la règle,
c'est la **fiabilité de l'appariement** entre nos entrées et la source officielle.

Appliquer la règle en masse sur un appariement qui se trompe **créerait des régressions**,
et sur 1 762 lignes on ne les verrait pas passer.

---

## Objectif (le QUOI, pas le comment)

**1. Dire comment l'appariement est fait aujourd'hui.**
Lire `outils/appliquer_divergences_officielles.py` et répondre en une phrase : l'officiel
est-il retrouvé **par ID** (sort/objet), **par nom anglais exact**, ou **par ressemblance
approximative** ? C'est la question qui décide de tout le reste.

**2. Classer les 121 divergences en attente en trois seaux, avec les comptes.**

- **SÛR** — même ID Blizzard, ou nom anglais identique caractère pour caractère.
- **À VÉRIFIER** — appariement plausible mais non prouvé.
- **FAUX** — l'appariement est démontrablement mauvais.

Signaux de mauvais appariement à détecter (tirés des cas réels ci-dessus) :

- un qualificatif **entre parenthèses** présent côté EN et absent côté FR — `(Brown)`, `(Light)` ;
- un EN qui **énumère** (`and`, virgules) contre un FR nettement plus court ;
- un FR officiel qui contient un **chiffre** absent de l'EN — « Armure +8 » ;
- un **rapport de longueur** EN/FR anormal (à toi de fixer le seuil, dis lequel).

**3. Estimer le même taux sur les 1 762 conflits Glayna**, sur un échantillon de 200 tiré
au hasard. On veut savoir à quoi s'attendre **avant** de lancer la passe, pas après.

**4. Mesure annexe, à chiffrer seulement (ne rien corriger) :** combien d'entrées de la
source officielle 3.3.5a commencent par une **majuscule non accentuée** qui devrait l'être
(« Equilibre de la puissance » → « Équilibre »). Blizzard ne les accentuait pas à l'époque.
Si le nombre est significatif, ça vaudra une règle à part.

---

**« Terminé » veut dire :**

> - Un fichier `rapports/fiabilite_appariement_officiel.txt` contenant :
>   la réponse au point 1, les trois seaux chiffrés pour les 121, l'estimation sur
>   l'échantillon Glayna, le compte des majuscules non accentuées.
> - Pour chaque entrée classée **FAUX** ou **À VÉRIFIER** : la ligne complète + la raison.
> - **Aucun** fichier de `traductions/` modifié. Aucune correction appliquée. Rien de publié.
> - Si l'appariement s'avère fait **par ID** et que les 4 cas ci-dessus s'expliquent
>   autrement (sort Ascension modifié réutilisant un ID Blizzard, par exemple), dis-le :
>   ça change complètement la conclusion, et c'est une bonne nouvelle.

**Validation :**

> Entièrement autonome — c'est une mesure, elle ne casse rien.
> Le résultat revient à Dan avant toute passe de masse.

**Fichiers / dossiers concernés :**

> `outils/appliquer_divergences_officielles.py` ·
> `traductions/divergences_officielles_a_arbitrer.txt` · `divergences_121_decisions.txt` ·
> `divergences_sources.txt` · `divergences_officielles_appliquees.txt` ·
> sources officielles : `sources/dbc/spells_frFR.json`, `Spell_frFR.dbc`,
> `sources/frFR/*.json`

---
## Réponse de Claude Code

**Rapport complet :** `rapports/fiabilite_appariement_officiel.txt` (941 lignes)
**Outil de mesure (lecture seule, rejouable) :** `outils/mesurer_fiabilite_appariement.py`

### 1. Comment l'appariement est fait — en une phrase

**Par ID**, et c'est exactement le problème : le script croise **deux bases différentes**
au même identifiant. Le nom anglais vient de `Spell_Ascension.dbc`, le français de
`Spell_frFR.dbc` (Blizzard 3.3.5a), et **rien ne vérifie que Blizzard nommait ce sort
comme Ascension le nomme**. Ni par nom anglais, ni par ressemblance (zéro bibliothèque
de comparaison floue dans tout le dépôt).

Ta question « et si les 4 cas s'expliquaient autrement ? » : **non**. Ce n'est pas un ID
Blizzard réutilisé pour un sort sans rapport — c'est un sort Blizzard **renommé en place**
par Ascension. L'ID 2831 s'appelait « Armor +8 » (→ « Armure +8 »), Ascension l'a rebaptisé
« Armor (Light) ». Le français récupéré traduit l'**ancien** nom.

Le juge de paix était déjà là : `sources/dbc/spells_enUS.json` a exactement les mêmes
49 839 IDs que le frFR. Test : `enUS[id].N == asc[id].N` → appariement prouvé bon, sinon
prouvé mauvais.

### 2. Les 121 divergences

| seau | nombre | |
|---|---|---|
| **SÛR** | **73** (60,3 %) | nom anglais Blizzard identique (71 caractère pour caractère) |
| **À VÉRIFIER** | **0** | toutes tranchables : chaque entrée a un ID présent chez Blizzard |
| **FAUX** | **48** (39,7 %) | Blizzard nommait cet ID autrement |

**Le test retrouve 121/121 de tes décisions manuelles.** Tes 14 `[OFFICIEL]` sont 14/14
dans le seau SÛR ; les 48 FAUX sont tous des `[GARDER]`. Ton arbitrage à la main avait
attrapé 100 % de la contamination.

Les signaux mécaniques que tu proposais n'attrapent que **21 des 48** — 27 passent sous le
radar (« Resolve » → « Vitalité », « Firm Grip » → « Résistance »). Seuil de longueur retenu :
**1,60** (9/48 pour 1 faux positif ; même au meilleur réglage on plafonne à 44 % de rappel).

### 2 bis. Ce que tu ne savais pas : 4 des 45 « déjà appliquées » sont fausses, et livrées

- `Fel Reaver's Piston` → **« Soins sur la durée sur les soins »** (ID 38299 = « HoTs on
  Heals », un sort technique). Contresens total ; notre « Piston de saccageur gangrené »
  était correct.
- `Nature's Rejuvenation` → « Récupération surpuissante » (Blizzard : « Empowered Rejuvenation »)
- `Shanked!` → « Pourfendre » (Blizzard : « Rend »)
- `Poison Mastery` → « Poisons » — même sort, seul le « Mastery » est perdu. Bénin.

Elles sont dans `sorts.json` **aujourd'hui**. Rien n'a été corrigé (la demande l'interdit).

### 3. Glayna — 200 tirés au hasard (graine 20260726)

Glayna n'a **pas** le problème d'appariement : sa clé est le **nom anglais exact** des deux
côtés. 0/200 ont un équivalent officiel Blizzard, 0/200 d'homonymie. Répondre « 100 % SÛR »
serait exact et inutile — le risque réel est sémantique, c'est lui qui a été mesuré, par
deux relectures indépendantes (fidélité au sens / risque de régression).

| seau | échantillon | extrapolé aux 1 763 |
|---|---|---|
| SÛR | 105 (52,5 %) | ~926 |
| À VÉRIFIER | 74 (37,0 %) | ~652 |
| **FAUX** | **21 (10,5 %)** | **185** (IC 95 % : 110 à 260) |

Plancher confirmé par les deux relectures : 12/200 (6 %) → ~106. Les régressions se
concentrent sur les **noms propres et le vocabulaire déjà canonique** (« Terres de Feu »,
« Mot de l'ombre », « Seigneur de couvée »).

### 4. Majuscules non accentuées

**1 247 noms officiels** concernés (2,6 % du corpus), **56 mots initiaux distincts**,
relus un par un : **56/56 confirmés, 0 faux positif**. Très concentré — « Eclair » à lui
seul en fait 457 (37 %). Puis « Elixir » 121, « Etat » 83, « Eclat » 52, « Ame » 30…
Oui, ça vaut une règle à part : mécanique, isolée, sans risque de contresens.

### Recommandation

**Passe « l'officiel gagne » : ne pas la lancer en l'état.** Sur l'état actuel elle
toucherait 107 entrées dont **48 régressions (44,9 %)** — presque une sur deux, et 27
invisibles à toute relecture rapide.

**Le correctif est petit et déjà écrit ailleurs dans le dépôt.** `generer_noms_sorts.py:51-57`
et `generateur_sorts.py:209-218` partent de `enUS.items()` : la clé anglaise vient de
Blizzard, l'appariement est structurellement juste. **Le cœur du pipeline est sain** — le
défaut est confiné à deux outils d'arbitrage : `appliquer_divergences_officielles.py` et
`croiser_sources.py` (43 de ses 144 divergences contaminées, 30 %). Il suffit d'y ajouter la
même condition, avec un repli sur la comparaison sans séparateurs (« Holy Form » / « Holyform »).

**Passe Glayna : possible, pas à l'aveugle.** Garder `casse()` comme porte (ne pas la
contourner pour la passe de masse) et protéger les noms propres.

**Ordre suggéré :** 1) corriger les 4 lignes fausses livrées (ton accord) · 2) poser le
garde-fou enUS dans les deux scripts · 3) relancer la passe officielle, elle devient sûre ·
4) Glayna avec les deux garde-fous · 5) la règle d'accent peut partir seule.

### Contrôle

Aucun fichier de `traductions/` modifié, aucune correction appliquée, rien de publié.
**Signalement :** `traductions/sorts.json` porte une modification à 20:19:13 pendant
l'analyse (+8 Ko). Ce n'est pas cette mesure — audit des journaux : 0 ouverture en écriture,
0 appel `--appliquer`, aucun outil d'édition sur `traductions/`. Aucun autre fichier du
dossier n'a bougé. Ressemble à une exécution de l'Atelier de ton côté ; à vérifier.
