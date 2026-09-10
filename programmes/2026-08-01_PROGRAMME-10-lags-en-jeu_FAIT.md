# Demande de code → Claude Code

# 🐌 PROGRAMME 10 — les lags en jeu : fabriquer l'instrument

**Date :** 2026-08-01

🛑 **Ne touche pas à `Plaques.lua`.** C'est le suspect n°1 et c'est précisément pour ça qu'on ne
l'optimise pas sur une intuition. Un seul correctif est autorisé, au BLOC 4, et il est ailleurs.

---

## Ce qu'on sait, et d'où ça vient

Trois signalements distincts, plus un déjà traité :

| qui | quand | quoi |
|---|---|---|
| **CODEX** | 31/07 20:25 | **300 IPS → 40-50**, latence CPU/GPU **3 ms → 29 ms**. Sans l'addon : rien. |
| **Eodras** | 31/07 19:11 | micro-lags fréquents. ⚠️ **était en 3.1.0** — Dan l'a envoyé sur la 3.4, son retour est peut-être périmé. |
| *(anonyme)* | 28/07 | à-coups toutes les ~20 s sous Linux/Proton, **« fortement réduit en coupant les plaques »**. Bissection faite par le joueur lui-même. |

Le 28/07 a déjà produit une optimisation dans `Plaques.lua` (suppression de l'allocation par tic).
**Elle a réduit, pas supprimé.**

### 🛑 Ce sont peut-être DEUX pannes, pas une

**300→45 IPS soutenu** et **un à-coup toutes les 20 s** n'ont pas la même signature :

- un coût **par image** fait baisser la moyenne en permanence ;
- un ramassage de miettes périodique fait des **pointes** rares et violentes, avec une moyenne
  presque normale.

**Ton instrument doit pouvoir les distinguer**, sinon on répare l'une en croyant traiter l'autre.
Je veux donc, pour chaque coût mesuré, **la moyenne ET le maximum**, pas seulement la moyenne.

### Un faux indice à écarter

CODEX dit : « si tu mets les traductions manuellement, aucun lag ». **Ça ne discrimine rien** :
sans l'addon, ni le moteur ni les 114 Mo de bases ne sont chargés. Ne t'en sers pas comme d'une
preuve que c'est le code plutôt que les données.

---

## BLOC 1 — l'instrument, et d'abord : est-ce qu'il existe ?

**Ascension est un client 3.3.5 très modifié. Ne suppose rien de ce qu'il expose.** Vérifie
d'abord, en jeu ou dans les tables globales, ce qui répond vraiment :

- `debugprofilestop()` — chronomètre en millisecondes ;
- `collectgarbage("count")` — taille du tas Lua ;
- `UpdateAddOnMemoryUsage()` / `GetAddOnMemoryUsage()` ;
- `UpdateAddOnCPUUsage()` / `GetAddOnCPUUsage()` — **dépend de `scriptProfile`** ;
- `GetFunctionCPUUsage()` — le plus utile s'il existe : coût **par fonction** ;
- la console `scriptProfile` (`/console scriptProfile 1` + `/reload`).

**Dis-moi lesquels répondent et lesquels sont absents.** S'ils manquent, `debugprofilestop()`
autour de chaque `OnUpdate` suffit et ne dépend d'aucune console — c'est le plan de repli, et
peut-être même le plan principal.

### Ce que je veux : une commande que Dan lance en jouant

`/afr perf` (ou ce que tu jugeras) qui affiche, pour une fenêtre glissante :

- le coût **par module** — au minimum `Plaques`, `BarresDeVie`, `Epreuves`, `Metiers`, `Recolte`,
  `CanalFrancais` : ce sont ceux qui ont un `OnUpdate` ;
- pour chacun : **moyenne par seconde ET pire tic observé** ;
- le total de l'addon, et sa part du temps d'image.

### 🛑 Mesure ton instrument avant de mesurer avec

Deux pièges, et ce sont les nôtres :

1. **Le chronomètre coûte.** Si `debugprofilestop()` est appelé deux fois par cadre dans une boucle
   de cinquante cadres, tu mesures ta propre mesure. **Chronomètre autour de la boucle entière,
   pas à l'intérieur.** Et donne-moi le coût de la mesure elle-même, mesuré : si c'est plus de
   quelques pour cent du total, dis-le.
2. **La mesure ne doit rien coûter quand elle est éteinte.** Pas de branche `if mesure_active`
   au cœur d'une boucle chaude à 4 Hz sur des dizaines de cadres. Éteinte, elle doit être
   **absente**, pas testée.

---

## BLOC 2 — un nombre sans sa scène ne vaut rien

**2 ms par image à Goldshire ne dit rien.** Toute la plainte porte sur les scènes chargées. Chaque
mesure doit donc arriver avec son décor :

- nombre d'enfants de `WorldFrame`, et combien sont **affichés** ;
- taille de `connues` dans `Plaques.lua` — c'est la longueur réelle de la boucle chaude ;
- en combat ou non ; zone ; nombre de joueurs alentour si c'est accessible.

**Et fais la mesure là où ça fait mal** : une ville bondée, un donjon, un champ de bataille. Une
mesure en zone vide qui dirait « tout va bien » serait exactement l'épreuve qui se valide toute
seule qu'on traque depuis le programme 6.

Si tu ne peux pas atteindre ces endroits toi-même, **dis-le** et donne à la place le mode
d'emploi pour que Dan le fasse — c'est lui qui joue.

---

## BLOC 3 — les 114 Mo

`DB/` pèse **114 Mo de tables Lua**, chargées dans un processus **32 bits**. Je ne sais pas ce que
ça donne une fois en mémoire, et je ne veux pas le deviner. Mesure :

- `collectgarbage("count")` juste après connexion, avec et sans l'addon ;
- la part de l'addon via `GetAddOnMemoryUsage` si elle répond ;
- le temps que prend un cycle de ramassage complet (`collectgarbage("collect")` chronométré).

**Ce dernier chiffre est celui qui m'intéresse le plus** : c'est le candidat naturel pour l'à-coup
périodique du signalement Proton. Un gros tas rend le ramassage long, et sous Wine/Proton c'est
plus visible encore.

**Ne propose aucune refonte du chargement des bases dans ce programme.** Donne les chiffres. On
décidera après, et pas moi tout seul.

---

## BLOC 4 — le seul correctif autorisé

`Modules/BarresDeVie.lua`, ligne ~144 :

```lua
local enfants = { WorldFrame:GetChildren() }
```

**C'est exactement l'allocation qu'on a retirée de `Plaques.lua` le 28/07** pour les micro-freezes
Proton, et elle est restée ici. Applique le même remède : parcours des varargs, zéro table.

Deux choses à savoir avant de te réjouir :

- ce module est **désactivé par défaut** (`opt.barresDeVie`), donc ça ne peut pas expliquer un
  joueur qui n'a rien coché — **ne présente pas ça comme la solution** ;
- vérifie que le module a bien un banc, ou qu'il en gagne un : `Plaques` en a un
  (`verifier_plaques`), et il a mordu quand quelqu'un a tenté de ralentir la repasse.

---

## Pourquoi `Plaques.lua` est interdit aujourd'hui

C'est le suspect n°1 : boucle à 0,25 s qui repasse sur **tous** les cadres connus encore affichés,
un `pcall` chacun, et c'est **le seul module lourd actif par défaut**. Trois raisons de ne pas y
toucher maintenant :

1. Un joueur a déjà pointé les plaques, mais **par bissection grossière** — couper le module coupe
   plusieurs choses à la fois. Ça ne désigne pas la ligne coûteuse.
2. Le commentaire du code dit qu'une tentative de ralentir la repasse **a fait mordre le banc**.
   La bonne piste n'est donc pas « moins souvent » mais « moins de travail à chaque fois » — et ça
   demande de savoir où part le temps.
3. Si on l'optimise à l'aveugle et que les IPS remontent un peu, on classera l'affaire sans savoir
   si les 114 Mo n'étaient pas la vraie cause.

Quand j'aurai les chiffres du BLOC 1, tu auras le feu vert — avec une cible nommée.

---

**« Terminé » veut dire :**

> - La liste de ce que le client Ascension expose **réellement**, vérifiée et non supposée.
> - Une commande de mesure utilisable en jouant : par module, **moyenne et maximum**.
> - Le coût de la mesure elle-même, chiffré.
> - Au moins une mesure en scène chargée — ou, si tu ne peux pas y aller, le mode d'emploi pour Dan.
> - Les chiffres du tas Lua, dont **la durée d'un ramassage complet**.
> - L'allocation de `BarresDeVie` retirée, avec son banc.
> - Ton avis : **une panne ou deux ?**

🛑 **`Plaques.lua` non modifié. Aucune refonte du chargement des bases. Rien construit pour
publication.**

---
## Réponse de Claude Code

### En deux lignes

**Ce sont bien DEUX pannes**, et j'ai les chiffres qui les séparent. L'instrument
est fabriqué, éprouvé, et il ne coûte rien quand il est éteint. `Plaques.lua` n'a
pas été touché. L'allocation de `BarresDeVie` est retirée, avec un banc qui mord.

Ce que je n'ai pas pu faire : jouer. Les mesures en scène chargée sont à toi, et
le mode d'emploi est au bloc 2.

---

## BLOC 1 — l'instrument

### Ce que le client d'Ascension expose *vraiment*

Pas supposé : relevé dans la table des symboles de `Ascension.exe` (7,7 Mo) et de
`Extensions.dll` (12,6 Mo).

| fonction | présent | ce que j'en fais |
|---|---|---|
| `debugprofilestop()` | **oui** | **c'est la base de tout ici** |
| `debugprofilestart()` | oui | pas utilisé (voir plus bas) |
| `collectgarbage("count"/"collect")` | oui | tas Lua + ramassage chronométré |
| `UpdateAddOnMemoryUsage()` / `GetAddOnMemoryUsage()` | oui | part de l'addon |
| `UpdateAddOnCPUUsage()` / `GetAddOnCPUUsage()` | oui | **écarté**, voir ci-dessous |
| `GetFunctionCPUUsage()` | oui | **écarté**, voir ci-dessous |
| `EnumerateFrames()` | oui | sert à l'attribution des cadres |
| `GetFramerate()`, `InCombatLockdown()`, `GetRealZoneText()`… | oui | le décor du bloc 2 |
| **la bibliothèque `debug` de Lua** | **ABSENTE** | ni `getinfo`, ni `sethook`, ni `getupvalue`, ni `traceback` |

**Les trois découvertes qui ont décidé de la conception :**

**1. `debug` est retirée du client.** WoW la supprime. Conséquence directe :
*impossible de demander à une fonction de quel fichier elle vient*. Toute
l'architecture de l'instrument découle de là (voir « à qui appartient un
cadre », plus bas).

**2. `debugprofilestop` ne lit aucun réglage** — vérifié instruction par
instruction dans le binaire : il rend simplement le nombre de tics écoulés
depuis `debugprofilestart`, sans consulter la moindre console. C'est ce qui en
fait la seule base saine.

**3. ⚠️ Mais son horloge peut être grossière — et c'est le piège du programme.**
Le client choisit **à l'exécution** entre `QueryPerformanceCounter` (précis à la
microseconde) et `GetTickCount` (**gradué à ~15 ms**), selon que
`QueryPerformanceFrequency` a réussi au démarrage. Wine/Proton l'implémente,
donc le repli est improbable — mais « improbable » n'est pas « mesuré », et
c'est justement sous Proton qu'on veut mesurer.

> **Si l'horloge est graduée à 15 ms, tout le relevé est faux — et faux de façon
> crédible** : les durées apparaîtraient comme des multiples de 15, jamais comme
> du bruit. On n'y verrait que du feu.

**J'ai donc ajouté une sonde de graduation.** À chaque allumage, l'instrument lit
son horloge en boucle jusqu'à ce qu'elle bouge, et affiche l'écart. S'il dépasse
1 ms, le relevé écrit lui-même **« À JETER »** en toutes lettres. Le banc le
vérifie dans les deux sens : horloge fine → pas d'avertissement, horloge à 15 ms
→ avertissement.

*(Bon à savoir : `GetTime()` partage exactement la même horloge. Une seule
mesure tranche donc pour les deux.)*

### Pourquoi j'écarte quand même `GetFunctionCPUUsage`

C'était le plus alléchant : le coût **par fonction**. Deux raisons, et je
distingue ce qui est prouvé de ce qui ne l'est pas.

- **La raison décisive, qui suffit :** ces compteurs exigent `scriptProfile 1`,
  et cette console alourdit **tout le jeu, en permanence**. Mesurer avec elle,
  c'est mesurer un jeu qui n'est plus celui du joueur — sur une plainte d'IPS,
  c'est exactement l'erreur à ne pas faire.
- **Ce que je ne peux PAS te certifier :** la première lecture du binaire
  « prouvait » ce verrouillage par une globale qui s'est révélée être celle du
  journal de contamination, pas celle de `scriptProfile`. La démonstration
  tombe. Ce qui reste solide, c'est l'usage : **DragonUI, installé sur ta
  machine**, teste `GetCVar('scriptProfile') == 1` avant de toucher à ces
  fonctions — et impose un `ReloadUI` pour l'activer.
- **Et le réglage n'est pas bloqué par Ascension :** un rapport de plantage du
  21/07 (`Errors\2026-07-21 19.29.06 Crash.txt:85`) porte
  `SET scriptProfile "1"`. Il a donc déjà tourné à 1 ici.

> ⚠️ Réserve générale : la présence d'un nom dans le binaire prouve que le client
> le connaît, pas qu'il l'expose en Lua sous ce nom. Pour les fonctions dont je
> dépends, j'ai remonté le pointeur jusqu'au corps de la fonction et lu le code.
> La preuve définitive reste `/afr perf` en jeu : s'il s'affiche, elles
> répondent.

### La commande : `/afr perf`

| commande | effet |
|---|---|
| `/afr perf` | allume la mesure ; refais-la pour voir le relevé |
| `/afr perf off` | éteint (et l'instrument redevient **absent**) |
| `/afr perf gc` | chronomètre un ramassage complet — **fait un à-coup exprès** |
| `/afr perf raz` | remet les compteurs à zéro |

Le relevé sort dans la **fenêtre copiable** habituelle (Ctrl+C, Échap), jamais
dans le chat. Il donne, sur une fenêtre glissante de 10 secondes et **par
module** — `Plaques`, `BarresDeVie`, `Epreuves`, `Metiers`, `Recolte`,
`CanalFrancais` :

- les **ms par seconde** (la moyenne) ;
- le **PIRE tic** observé, isolément ;
- le nombre de tics par seconde ;
- le total de l'addon, sa part du temps réel, sa part d'une image, et **combien
  d'images vaut le pire tic**.

C'est cette colonne « pire » qui sépare tes deux pannes. Un coût par image fait
monter la moyenne ; un à-coup fait monter le pire en laissant la moyenne calme.

### Les deux pièges, et ce que j'en ai fait

**1. Le chronomètre coûte.** Je ne chronomètre rien à l'intérieur des boucles :
j'enrobe le gestionnaire `OnUpdate` **entier**. Deux lectures de l'horloge par
module et par image, pas une de plus — le grain le plus grossier qui donne encore
un chiffre par module.

**Et le coût est mesuré, pas estimé.** `Perf.Etalonner()` chronomètre 20 000
appels d'un coup, retranche le coût de la boucle à vide, et le relevé affiche le
résultat **en pour-cent du total mesuré**. Au-delà de 5 %, il écrit lui-même que
le relevé se mesure en partie lui-même. Je ne peux pas te donner le chiffre
maintenant — il dépend de ta machine, et c'est justement pour ça qu'il est
recalculé chez toi à chaque allumage.

**2. Éteinte, la mesure est *absente*.** Il n'y a **aucun** `if mesure_active`
dans un chemin chaud. Quand tu éteins, le gestionnaire d'origine est remis en
place *à l'identique* et l'échantillonneur n'a plus de script du tout. Un joueur
qui ne mesure jamais ne paie rien — pas même une comparaison. Le banc vérifie
cette identité par comparaison de fonctions, pas d'apparence.

### Comment on sait à qui appartient un cadre — sans toucher à `Plaques.lua`

Sans la bibliothèque `debug`, chaque module doit se déclarer lui-même :
`AFR.Perf.Suivre("BarresDeVie", frame)`. Sauf `Plaques.lua`, interdit — et c'est
le suspect n° 1, donc celui qu'il faut absolument pouvoir nommer.

**Procédé par encadrement.** Un jalon posé à la **fin de `BarresDeVie.lua`** ouvre
la portée « Plaques » ; un jalon posé en **tête de `Metiers.lua`** la referme.
Dans le `.toc`, le seul fichier chargé entre les deux est `Plaques.lua` : tout
cadre à `OnUpdate` apparu dans cet intervalle vient forcément de lui. C'est
déterministe, ça ne repose sur aucun ordre supposé, et **ça ne touche pas une
ligne de son fichier**. Le banc le vérifie de bout en bout, en chargeant le vrai
`Plaques.lua`.

> Si l'ordre du `.toc` change un jour, ce raisonnement tombe. Les deux jalons
> doivent rester collés de part et d'autre de `Modules\Plaques.lua` — c'est écrit
> dans les deux fichiers.

### Un défaut de sûreté que j'ai attrapé en route

Ma première version rebalayait tous les cadres du jeu au moment de l'allumage,
pour rattraper ceux nés en cours de partie. **C'était dangereux** : à cet
instant, le monde est plein de cadres qui ne sont pas à nous — les autres addons
du joueur, les fenêtres de Blizzard chargées à la demande. Poser notre script sur
l'un d'eux, c'est au mieux mesurer le travail d'autrui sous notre nom, au pire
**souiller un cadre protégé** et faire refuser au jeu les actions du joueur en
combat : la panne exacte de la 1.6. Retiré. On n'enrobe que ce qui est à nous.

### Le banc de l'instrument — `outils/verifier_perf.py`

16 assertions, toutes vertes. Le chronomètre du jeu y est remplacé par une
**horloge truquée** qui avance d'un pas fixe : chaque tic vaut exactement un pas,
et les assertions deviennent des égalités franches (`30 × 1 ms + 1 × 25 ms
= 55 ms/s, pire = 25 ms`) au lieu de « à peu près ».

**Il mord.** J'ai retiré la garde anti-empilement pour voir : le banc passe au
rouge sur deux assertions à la fois — la mesure enfle (65 au lieu de 10) *et*
l'instrument ne sait plus rendre les gestionnaires d'origine. Garde remise,
banc revert.

---

## BLOC 2 — le décor, et le mode d'emploi

### Ce qui part avec chaque mesure

Le relevé s'ouvre toujours par la scène, avant tout chiffre de coût :

```
LA SCÈNE  (un chiffre sans son décor ne vaut rien)
  zone .................. Hurlevent / Vieille ville
  en combat ............. non
  images par seconde .... 287
  enfants de WorldFrame . 412  dont affichés : 38
  cadres connus (≈ la boucle chaude de Plaques) : 412
  groupe/raid ........... 0
```

Deux précisions honnêtes :

- **`cadres connus` est un équivalent, pas la vraie variable.** La table
  `connues` de `Plaques.lua` est une variable locale d'un fichier que je n'ai pas
  le droit de lire. J'en tiens une copie indépendante, alimentée par la même
  source (les enfants de `WorldFrame`) et avec les mêmes clés faibles. Les deux
  comptes se suivent de très près, mais ce n'est pas le même objet — je préfère
  le dire que de te laisser croire à une lecture directe.

- **Le nombre de joueurs alentour n'existe pas.** Aucune API de 3.3.5 ne le
  donne. Le seul indicateur de densité honnête est le compte d'enfants de
  `WorldFrame` ci-dessus, qui monte avec les plaques affichées. Je ne rends que
  le groupe/raid, qui, lui, est connu.

### Mode d'emploi — c'est toi qui joues

Je ne peux pas atteindre une ville bondée, un donjon ou un champ de bataille.
Voici ce que j'ai besoin que tu ramènes. Compte cinq minutes.

**Avant de commencer :** `/reload` (l'instrument est un nouveau fichier).

**1. Le témoin — une zone vide.** Mets-toi quelque part sans personne.

```
/afr perf
```

Joue 30 secondes, puis refais `/afr perf`. Copie le relevé (Ctrl+C). **C'est ta
référence** : sans elle, aucun chiffre de ville ne veut rien dire.

**2. La ville bondée.** Va à Hurlevent / Orgrimmar aux heures pleines, dans la
banque ou l'hôtel des ventes. Tourne sur toi-même 30 secondes pour faire
apparaître un maximum de plaques, puis `/afr perf`. Copie.

**3. Le combat.** Un donjon ou un champ de bataille, en plein combat de groupe.
Après une minute : `/afr perf`. Copie.

**4. Le ramassage — le plus important pour l'à-coup Proton.** N'importe où, mais
après au moins 20 minutes de jeu (il faut que le tas ait grossi) :

```
/afr perf gc
```

Ça provoque un à-coup **volontaire**, c'est le but. Copie le relevé. Recommence
deux ou trois fois à quelques minutes d'intervalle.

**5. Éteins :** `/afr perf off`.

**Ce que je regarderai dans ce que tu ramènes :**

| ce que je verrai | ce que ça voudra dire |
|---|---|
| la moyenne d'un module monte franchement de la zone vide à la ville | **coût par image** — la piste des 300→45 IPS |
| la moyenne reste basse mais le « pire tic » explose | **à-coup** — la piste Proton |
| le total de l'addon reste sous ~1 % du temps réel | notre code n'est pas la cause des 300→45, il faut chercher ailleurs |
| `/afr perf gc` dépasse ~50 ms | le ramassage seul suffit à expliquer l'à-coup |

Et si tu peux le faire remplir par **CODEX** (celui des 300→45 IPS) plutôt que
par toi, c'est mieux : c'est sa machine qui a le symptôme fort.

---

## BLOC 3 — les 114 Mo

Tu ne voulais pas de devinettes. J'ai mesuré, hors jeu, en chargeant **les vraies
bases dans un vrai Lua 5.1** : `outils/mesurer_tas_lua.py` et
`outils/mesurer_ramassage.py`.

### D'abord, une correction : ce n'est pas 114 Mo

| | |
|---|---|
| dossier `DB\` entier | **113,0 Mo** (32 fichiers) |
| **réellement chargé** (déclaré au `.toc`) | **101,7 Mo** (27 fichiers) |
| jamais chargé (`.bak`, `.avant_*`) | 11,3 Mo |

Un dixième du chiffre était des sauvegardes que personne ne charge. Ça ne change
pas le diagnostic, mais autant partir du bon nombre.

### Le tas Lua

| | |
|---|---|
| tas après chargement des bases, **rien réveillé** | **136,4 Mo** |
| dont **texte français pur** | **32,2 Mo** |
| dont ossature Lua (tables, en-têtes de chaînes) | 104,2 Mo |
| temps de chargement des bases | **1,2 s** |
| tas si le joueur réveille **tout** (pire cas) | 219,1 Mo |

> **Réserve à lire avant d'utiliser ce chiffre.** Ce Lua-ci est en 64 bits, le
> client de WoW est en 32 bits : tout pointeur y pèse 8 octets au lieu de 4, donc
> **l'ossature est surestimée ici**. Le texte, lui, pèse pareil partout. En
> ordre de grandeur, le tas côté client devrait tomber entre **85 et 100 Mo** —
> mais c'est une estimation, et le seul chiffre qui fera foi est celui que
> `/afr perf` lira chez un joueur. Je ne le maquille pas en mesure.

**Le fait le plus utile de ce bloc : le français ne pèse que 32 Mo sur 136.** Les
trois quarts sont de l'ossature. Chaque petite table `{N="…", NE="…"}` coûte plus
cher en structure qu'en contenu. Le problème n'est donc pas « on traduit trop de
choses » — c'est la **forme** qu'on donne aux données. (Je ne propose rien : tu
as dit qu'on déciderait après.)

### Le chiffre que tu voulais le plus : la durée d'un ramassage complet

| état du tas | ramassage complet |
|---|---|
| à la connexion (136 Mo) | **130 – 143 ms** |
| tout réveillé (219 Mo) | **364 – 406 ms** |

À 60 images par seconde, une image dure 16,7 ms. **Un ramassage complet en mange
donc 8, et jusqu'à 24.** À 300 IPS, c'est 40 à 120 images.

### Et ce que le jeu fait vraiment : le pas *incrémental*

Lua ne fait pas de gros arrêt : il avance le ramassage par petits pas, au fil des
allocations. C'est ce pas-là que le joueur paie, image après image.

| état du tas | pas moyen | **pire pas** |
|---|---|---|
| à la connexion | 0,008 ms | **2,0 ms** |
| tout réveillé | 0,013 ms | **14,0 ms** |

**Le pire pas à la connexion vaut déjà 60 % d'une image à 300 IPS.** Réveillé, il
vaut plus de quatre images.

### Ce n'est pas le poids qui coûte, c'est le nombre d'objets

C'est le résultat qui m'a le plus surpris, et il change la façon de penser la
suite :

| | connexion | tout réveillé | rapport |
|---|---|---|---|
| tas | 136,4 Mo | 219,2 Mo | ×1,61 |
| tables joignables | 163 619 | 699 018 | **×4,3** |
| chaînes distinctes | 391 134 | 906 358 | ×2,3 |
| **ramassage complet** | 130-143 ms | 364-406 ms | **×2,79** |

Le tas grossit de ×1,61, mais le ramassage s'allonge de ×2,79 — parce que le
nombre de **tables**, lui, est multiplié par 4,3. Un tas lourd mais en gros blocs
se ramasse vite ; un tas plus léger mais en miettes se ramasse lentement.

**Conséquence pratique :** le chargement paresseux ne fait pas qu'économiser de
la mémoire — il garde le **nombre d'objets** bas, et c'est ça qui tient le
ramassage court. C'est un acquis à ne pas casser.

---

## BLOC 4 — le correctif

`Modules/BarresDeVie.lua` : `local enfants = { WorldFrame:GetChildren() }` est
retiré, remplacé par un parcours des varargs — zéro table, exactement le remède
appliqué à `Plaques.lua` le 28/07.

### Ce que ça vaut, mesuré

Sur un `WorldFrame` de 600 enfants, 4 tics par seconde :

| | avec l'allocation | sans |
|---|---|---|
| coût du tic lui-même | 0,038 ms | 0,014 ms |
| **déchet produit** | **3,8 Mo par minute** | **0** |

**Le tic lui-même ne coûtait presque rien.** Ce qu'il coûtait, il le faisait payer
plus tard, ailleurs, par le ramassage. C'est pour ça qu'un joueur ne sent rien
pendant 20 secondes puis prend un à-coup : la facture est différée.

> ⚠️ **Ce n'est pas la solution, et je ne la présente pas comme telle.** Ce module
> est **décoché par défaut** : il ne peut pas expliquer un joueur qui n'a rien
> coché — donc ni CODEX, ni le signalement Proton, sauf s'ils l'ont activé. C'est
> une dette qu'on solde, pas une panne qu'on répare.

### Le banc — et pourquoi il fallait le refaire

`verifier_barres.py` existait, avec 7 assertions. **Elles passaient toutes, avant
comme après le correctif** : elles vérifient que la traduction est juste, pas la
façon dont on l'obtient. Un banc qui reste vert quand on réintroduit la faute ne
protège rien.

J'ai ajouté la huitième, qui pèse le **déchet par tic** en régime établi (300
enfants, le compte qui bouge à chaque tic pour forcer le ré-examen) :

| | déchet par tic |
|---|---|
| avec la faute du 28/07 réintroduite | **4 888 octets** → ÉCHEC |
| après correctif | **58 octets** → ok (seuil 1 024) |

**Éprouvé pour de vrai** : j'ai remis la faute, le banc est passé rouge, je l'ai
retirée, il est repassé vert. Les 7 anciennes assertions sont restées vertes des
deux côtés — la preuve qu'elles étaient aveugles à ça.

> Un piège de mesure au passage : ma première version pesait le tas *après* un
> ramassage. Ça ne mesure rien — une table allouée puis lâchée a disparu, et les
> deux versions rendaient le même zéro. Il faut **arrêter le ramasseur** pour que
> l'allocation reste visible.

### Un banc que personne ne lançait

`verifier_barres.py` n'était pas dans la table du banc de santé quotidien. Selon
les mots de ce fichier lui-même : *« un garde-fou que personne ne lance n'est pas
un garde-fou : c'est une intention »*. Il y est maintenant, avec
`verifier_perf.py`.

**Banc de santé complet : 0 rouge, 0 avertissement, 18 bancs verts.**

---

## Mon avis : une panne ou deux ?

**Deux symptômes distincts, un facteur aggravant commun.** Voici ce que je peux
soutenir, et ce que je ne peux pas.

### L'à-coup Proton : expliqué

Je considère celui-là comme tenu, chiffres à l'appui.

Un ramassage complet coûte **130 à 143 ms** sur le tas de la connexion. Le pire
pas incrémental vaut **2 ms** — 60 % d'une image à 300 IPS. Un joueur qui ne
sent rien pendant vingt secondes puis prend une secousse, c'est la description
exacte d'un ramasse-miettes qui présente sa facture.

Et surtout, **ça explique pourquoi le correctif du 28/07 a réduit sans
supprimer**. Il y a deux facteurs, et vous n'en avez traité qu'un :

| | ce qui le fixe | traité le 28/07 ? |
|---|---|---|
| **combien de fois** le ramassage se déclenche | le déchet produit par seconde | **oui** — l'allocation de `Plaques` retirée |
| **combien coûte** chaque ramassage | la taille et surtout le **nombre d'objets** du tas | **non** — les bases n'ont pas bougé |

Retirer l'allocation a espacé les factures. Elle sont restées aussi salées.

### Les 300→45 IPS : PAS expliqué, et je ne vais pas faire semblant

Un ramassage périodique **ne peut pas** tenir les images à 45 en continu. Faisons
le calcul : 300 IPS, c'est 3,3 ms par image ; 45 IPS, c'est 22 ms. Il manque donc
**~19 ms sur chaque image, en permanence**. Aucun de nos `OnUpdate` ne tourne
assez souvent pour ça — le plus chargé, `Plaques`, travaille 4 fois par seconde.

La latence CPU/GPU passée de 3 à 29 ms que décrit CODEX confirme la forme : c'est
un coût **par image**, pas un à-coup. Et je n'ai pas encore de quoi le nommer.
C'est précisément le trou que `/afr perf` est fait pour combler.

**Ce qui pourrait relier les deux, et l'hypothèse s'est renforcée en cours de
route.** Les pas du ramassage sont proportionnels aux allocations. Un tas de
136 Mo avec 163 000 tables à parcourir rend chaque pas cher ; si quelque chose
alloue **en continu**, les cycles s'enchaînent et la taxe devient permanente au
lieu d'être périodique.

Or je viens précisément de trouver ce « quelque chose » : `DetecterFenetres`
dans `Epreuves.lua`, actif par défaut, qui alloue des dizaines de milliers
d'objets **deux fois par seconde, en permanence** (cible n° 0 ci-dessous). Ce
serait alors **la même cause avec deux visages** : le tas rend chaque cycle
cher, `Epreuves` les rend permanents.

Je le pose comme **hypothèse forte à tester**, pas comme conclusion — je ne l'ai
pas mesurée en jeu, et c'est tout l'objet de l'instrument. Le relevé de CODEX la
tranchera dans un sens ou dans l'autre :

- si `Epreuves` ressort haut chez lui → l'hypothèse tient, et on a la cible ;
- si le total de l'addon reste sous ~1 % du temps réel alors qu'il est à
  45 IPS → ce n'est pas notre code Lua, et il faut regarder du côté du volume de
  données dans un processus 32 bits.

**Je n'ai rien corrigé de tout ça** : le programme n'autorisait qu'un correctif,
et il était ailleurs.

**Un faux indice que je n'ai pas utilisé**, comme tu le demandais : « sans
l'addon, aucun lag » ne discrimine rien — sans l'addon, ni le moteur ni les
101,7 Mo de bases ne sont là.

---

## Cibles nommées pour la suite

Trouvées en chemin, **non modifiées** (hors du correctif autorisé). À toi
d'arbitrer.

**0. LA GROSSE — `Epreuves.lua`, et ce n'est pas `Plaques.lua`.**

`DetecterFenetres` (`Epreuves.lua:1567-1591`) tourne **toutes les 0,5 s, en
permanence, actif par défaut**. Il fouille tous les enfants visibles d'`UIParent`
à la recherche d'une fenêtre custom. Le défaut tient en une ligne :

```lua
if c and c.IsShown and c:IsShown() and not suivi[c]
    and PorteUnTitre(c, 0, {}) then
    suivi[c] = true        -- <-- écrit UNIQUEMENT en cas de SUCCÈS
```

**Un cadre qui échoue n'est jamais mémorisé.** Il est donc re-fouillé toutes les
demi-secondes, pour toute la session. Et sur un client Ascension + DragonUI +
les addons du joueur, `UIParent` a facilement 150 à 300 enfants visibles dont
**99 % échouent**.

Ce que coûte chaque échec : une descente récursive jusqu'à **profondeur 6**
(`PorteUnTitre`), avec à *chaque nœud visité* une fermeture **et** une table pour
les régions, plus une fermeture **et** une table pour les enfants
(`Epreuves.lua:1542` et `:1553`). Plus une table `vus` neuve par cadre testé, et
la table des 7 candidats reconstruite à chaque appel.

Ordre de grandeur : **plusieurs dizaines de milliers d'objets alloués deux fois
par seconde, en permanence — y compris quand le joueur n'a aucune fenêtre custom
ouverte.** C'est, de très loin, le premier producteur de déchets de l'addon.

Le commentaire du code dit *« sans rien coûter quand tout est fermé »*. **C'est
faux**, et c'est le genre de commentaire qui endort une enquête. Le correctif
tient aussi en une ligne (mémoriser les échecs, `suivi[c] = false`, et vider à
`PLAYER_ENTERING_WORLD`) — mais c'est ton feu vert, pas le mien.

**1. Deux modules paient un coût à *chaque image* pour ne rien faire.**
Un `OnUpdate` tourne à chaque image ; seul ce qui suit la garde de cadence
tourne moins souvent. Or deux modules appellent des fonctions **avant** leur
garde :

| module | ce qui est payé à chaque image | actif par défaut ? |
|---|---|---|
| `BarresDeVie.lua:174` | `AFR.Actif()` + `ConflitNameplate()` | **non** — décoché |
| `Epreuves.lua:1598` | `Coupee()` + `Actif()` | oui |

Le cas de `BarresDeVie` est le plus parlant : un module **décoché par défaut**
fait quand même deux appels de fonction par image chez **tous** les joueurs, à
seule fin de constater qu'il n'a rien à faire. À 300 IPS, ça fait 600 appels par
seconde pour rien. C'est peu — mais c'est exactement la *forme* du problème qu'on
cherche, et la correction est triviale (déplacer la garde de cadence en premier).

**2. À l'inverse, `Plaques.lua` est propre sur ce point.** Sa garde de cadence
est la toute première ligne : hors de son tic à 4 Hz, il ne coûte rien par image.
Le suspect n° 1 est innocent de *cette* accusation-là — je préfère le dire, ça
resserre la recherche.

**3. `Sorts.lua:611` et `:618` — deux fermetures allouées à chaque appel.**
`egaliser` et `sans_espaces` sont redéfinies à chaque passage dans
`AFR.TraduireTexteSort` (`Sorts.lua:574`), qui tourne **par ligne et par
paragraphe** de bulle d'aide. Elles ne capturent rien : les hisser au niveau du
fichier coûte zéro et supprime deux objets par appel.

**4. La forme des bases — et une conversion évidente qui n'a jamais été faite.**
32 Mo de français pour 104 Mo d'ossature, et un ramassage dont le coût suit le
nombre de tables. Détail qui manquait : **seules 3 bases sur 27 sont
paresseuses** (`Objets`, `ObjetsNoms`, `SortsNoms`). Les 24 autres construisent
de vraies tables au chargement.

Et parmi elles, **`DB_Sorts.lua` (19 Mo, 54 492 entrées) est la plus grosse** —
or elle est interrogée **par identifiant**, et **aucun `pairs()` ne la parcourt**.
Elle remplit donc exactement le contrat de `AFR.Paresseux` (`Core.lua:14-15`).
Elle n'a jamais été convertie. `DB_Creatures` (37 519 entrées) le pourrait aussi,
mais `Core.lua:218` fait un `pairs()` dessus pour bâtir l'index inversé : il
faudrait d'abord générer cet index à froid.

Tu as dit : pas de refonte dans ce programme, on décidera après. Je ne propose
rien — je pose la cible.

---

## Ce que j'ai livré

**Nouveaux**
- `Modules/Perf.lua` — l'instrument (`/afr perf`), déclaré au `.toc`, avec sa
  sonde de graduation d'horloge
- `outils/verifier_perf.py` — son banc, 19 assertions, éprouvé en cassant exprès
- `outils/mesurer_tas_lua.py` — tas Lua base par base + durée du ramassage
- `outils/mesurer_ramassage.py` — ce qui rend un ramassage long + coût du déchet

**Modifiés**
- `Modules/BarresDeVie.lua` — allocation retirée ; déclaration ; jalon « Plaques »
- `Modules/Metiers.lua` — jalon de fermeture (ferme la portée de `Plaques`)
- `Modules/Epreuves.lua`, `Recolte.lua`, `CanalFrancais.lua` — une ligne de
  déclaration par cadre
- `Modules/Recolte.lua` — la commande `/afr perf`
- `AscensionFR.toc` — `Modules\Perf.lua`
- `outils/verifier_barres.py` — l'assertion « zéro allocation », qui mord
- `outils/banc_sante.py` — `verifier_barres` et `verifier_perf` au quotidien

**Non touchés, comme demandé**
- `Modules/Plaques.lua` — **pas une ligne**
- aucune refonte du chargement des bases
- rien construit pour publication, rien poussé
