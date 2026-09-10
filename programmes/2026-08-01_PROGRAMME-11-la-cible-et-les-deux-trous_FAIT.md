# Demande de code → Claude Code

# 🎯 PROGRAMME 11 — la cible est confirmée, et l'instrument a deux trous

**Date :** 2026-08-01
**Suite du PROGRAMME 10.** Dan a rapporté trois relevés. Ils tranchent, et ils dérangent.

---

## Ce que la mesure a prouvé

Deux relevés, Hurlevent, hors combat :

| | Valley of Heroes (67 IPS) | Trade District (49 IPS) |
|---|---|---|
| **Epreuves** | **7,47 ms/s** — pire tic **13,38 ms** | **10,11 ms/s** — pire tic **13,10 ms** |
| Plaques | 0,05 | 0,04 |
| BarresDeVie | 0,12 | 0,06 |
| Recolte | 0,05 | 0,03 |
| Metiers / CanalFrancais | 0,00 | 0,00 |
| **total instrumenté** | 7,69 ms/s | 10,24 ms/s |

**`Epreuves` pèse 97 à 99 % de tout ce qui a été mesuré.** Ta cible n° 0 est confirmée : ce n'est
pas `Plaques.lua`. Et le **pire tic vaut 13 ms, deux fois par seconde** — presque une image
entière avalée, régulièrement. **C'est la description exacte d'un micro-lag.**

L'instrument, lui, tient : graduation d'horloge à 0,0002 ms (aucun repli sur `GetTickCount`),
coût propre de 0,2 à 0,5 % du total. Pas d'avertissement « À JETER ». Il est sain.

---

## 🛑 TROU N° 1 — le relevé du ramassage n'est pas une mesure, c'est une panne

```
tas avant .............. 227.5 Mo
tas après .............. 227.5 Mo
libéré ................. 0.0 Mo
DURÉE .................. 0 ms
```

**Un ramassage complet sur un tas de 227 Mo ne peut pas durer 0 ms et ne rien libérer.** Ce
relevé ne dit pas « tout va bien » : il dit que l'appel n'a rien fait du tout.

**Conséquence directe, et elle est lourde :** ta conclusion « l'à-coup Proton est expliqué, c'est
le ramasse-miettes » **n'est plus soutenue**. Elle reposait entièrement sur des mesures faites
**hors du jeu**, dans un autre Lua, en 64 bits. La seule vérification en jeu vient d'échouer.
Je ne dis pas que tu as tort — je dis qu'on ne le sait plus.

Trouve pourquoi. Pistes à éprouver, pas à supposer :

- `collectgarbage("collect")` est-il **neutralisé** dans ce client ? Vérifie-le comme tu as
  vérifié `debugprofilestop` : en lisant ce que fait réellement la fonction.
- Le chronomètre est-il branché autour du bon appel ?
- Le ramassage venait-il **juste** de tourner (rien à libérer) ? Alors le relevé doit le dire,
  au lieu d'afficher un zéro qui ressemble à un résultat.
- Est-ce que `collectgarbage("count")` reflète bien le tas réel ici ?

**Et corrige l'affichage :** un relevé qui rend 0 ms doit écrire **« MESURE INVALIDE »** en toutes
lettres, exactement comme la sonde d'horloge. Un zéro silencieux qui passe pour une bonne
nouvelle, c'est précisément le piège qu'on répare depuis dix jours.

---

## 🛑 TROU N° 2 — « TOTAL addon » n'est pas le total de l'addon

C'est le total de **six boucles `OnUpdate`**. Ça n'inclut ni les `hooksecurefunc`, ni les
gestionnaires d'événements. Or **un addon de traduction est fait de ça** : bulles d'aide, dialogues
PNJ, journal de quêtes, menus déroulants, plaques de nom, entraîneurs, métiers, courrier…

Donc quand le relevé affiche « part du temps réel : 1,02 % », **c'est un plancher, pas un total**,
et l'étiquette laisse croire l'inverse. Un joueur qui promène sa souris sur son sac déclenche des
dizaines d'accroches qui ne sont comptées nulle part.

**Ce que je te demande :**

1. **Renomme** la ligne pour qu'elle dise ce qu'elle mesure (« total des boucles », pas « total
   addon »). Un chiffre mal étiqueté est pire que pas de chiffre.
2. **Étends la mesure aux accroches.** Au minimum les plus chaudes : `GameTooltip`,
   `UIDropDownMenu_AddButton`, `GossipFrameUpdate`, `SpellButton_UpdateButton`, et les accroches
   de `Tooltips.lua` / `Sorts.lua`.
3. Même exigence qu'au programme 10 : **moyenne et pire appel**, coût nul quand la mesure est
   éteinte, et le coût de la mesure elle-même chiffré.

Sans ça, on ne peut pas dire si notre code est innocent des 300→45 — on peut seulement dire que
nos **boucles** le sont.

---

## BLOC A — corriger `DetecterFenetres` (feu vert, enfin)

`Epreuves.lua:1567-1591`. Le défaut est mesuré, la cible est nommée : vas-y.

Rappel du défaut : `suivi[c] = true` n'est écrit **qu'en cas de succès**, donc un cadre qui échoue
est refouillé toutes les 0,5 s, indéfiniment, avec une descente récursive qui alloue une fermeture
et une table à chaque nœud.

### 🛑 Le piège de la correction — ne troque pas une panne contre une autre

Mémoriser les échecs (`suivi[c] = false`) est la correction évidente. **Elle peut casser la
fonctionnalité** : une fenêtre créée vide puis remplie plus tard — titre posé après coup, onglet
construit à la demande — échouerait au premier test et **ne serait plus jamais retestée**. On
gagnerait des images et on perdrait des traductions, en silence. Ce serait exactement le
troisième commentaire menteur de ce fichier, mais écrit par nous.

Il faut donc un moyen de **revenir sur un échec**. À toi de choisir et de justifier :

- réessayer un cadre quand il passe de caché à affiché ;
- purger le cache d'échecs à `PLAYER_ENTERING_WORLD` (et peut-être à l'ouverture d'une fenêtre) ;
- retester les échecs à cadence très basse (une fois toutes les N secondes plutôt que 2×/s) ;
- autre chose, si tu vois mieux.

**Dis-moi lequel tu prends et ce qu'il ne couvre pas.**

### Ce que je veux comme preuve

- **Un banc qui mord** : il doit passer au rouge si on réintroduit le défaut, comme tu l'as fait
  pour `BarresDeVie`. Un banc qui reste vert des deux côtés ne protège rien — tu l'as démontré
  toi-même la semaine dernière.
- **Un banc de non-régression fonctionnelle** : une fenêtre qui n'obtient son titre qu'après
  coup doit quand même finir traduite. C'est ce banc-là qui garde le piège ci-dessus fermé.
- **Avant/après avec le même instrument** : je veux les deux relevés `Epreuves` côte à côte,
  moyenne et pire tic. Aujourd'hui : **7,47 et 10,11 ms/s, pire tic ~13 ms**. Dis-moi où ça tombe.
  Si tu ne peux pas reproduire la scène de Dan, dis-le et je lui redemande un relevé.

Les autres cibles nommées au programme 10 (`Sorts.lua`, les gardes de cadence, les bases
paresseuses) **restent hors sujet** : une correction à la fois, et celle-ci se prouve.

---

## BLOC B — la mémoire, et un écart que je veux compris

Le relevé donne :

| | |
|---|---|
| tas Lua du jeu entier | **226,1 → 229,1 Mo** |
| dont AscensionFR | **156,6 → 160,6 Mo (69-70 %)** |

**Tu estimais 85 à 100 Mo côté client. C'est 156.** L'écart est de 60 %, dans le mauvais sens.
Ton raisonnement (Lua 64 bits → pointeurs deux fois plus gros → surestimation hors jeu) allait
dans la bonne direction et t'a mené au mauvais chiffre. **Explique l'écart** — je préfère
comprendre pourquoi une estimation a raté que la voir corrigée en silence.

Et deux questions que le relevé pose sans y répondre :

1. **Le tas a grossi de 3 Mo entre deux relevés à quelques minutes d'intervalle**, dont 4 Mo pour
   nous. Est-ce le réveil normal des bases paresseuses, qui se stabilisera — ou est-ce que ça
   monte sans plafond ? **Mesure-le sur une session longue**, ne le déduis pas.
2. **229 Mo de tas Lua dans un processus 32 bits**, en plus des textures et du moteur. Quelle
   marge reste-t-il avant l'espace d'adressage ? Si la réponse est « peu », c'est une panne d'un
   autre genre — des plantages, pas des lags — et elle mérite d'être posée.

**Ne refonds rien.** Tu mesures, tu expliques, tu dis ce que tu ferais. On décidera après.

---

## Ce que la mesure NE dit pas, et qu'il ne faut pas lui faire dire

- **`Plaques.lua` n'a jamais été mis à l'épreuve.** `WorldFrame` avait **3 puis 10 enfants** — en
  ville il n'y a pas de plaques hostiles. Son 0,04 ms/s ne vaut que pour cette scène-là. Il faut
  le relevé en **donjon ou champ de bataille** pour le blanchir, et Dan ne l'a pas encore fait.
- **Dan tourne à 67 puis 49 IPS**, pas à 300. Sa machine n'est pas celle de CODEX. Entre ses deux
  points, l'image est passée de 14,93 à 20,27 ms (+5,34 ms) et notre part de 0,115 à 0,207 ms
  (+0,09 ms) : **nos boucles expliquent 1,7 % de son ralentissement.** C'est un fait solide sur
  les boucles — et ça ne dit rien des accroches (trou n° 2).
- **Aucun de ces relevés ne teste les 300→45 de CODEX.** Tant qu'on n'a pas les siens, cette
  panne-là reste ouverte.

---

**« Terminé » veut dire :**

> - Pourquoi le relevé de ramassage rend 0 ms / 0 Mo — **et l'affichage qui refuse de faire passer
>   un échec pour un résultat**.
> - La mesure étendue aux accroches, et la ligne « total » renommée pour dire ce qu'elle mesure.
> - `DetecterFenetres` corrigé, **avec le moyen de revenir sur un échec** et ce qu'il ne couvre pas.
> - Deux bancs qui mordent : un sur le coût, un sur la traduction qui ne doit pas se perdre.
> - L'avant/après `Epreuves`, chiffré.
> - L'écart 85-100 Mo → 156 Mo expliqué, et la marge restante en 32 bits.
> - Ce que tu as failli casser, s'il y a lieu.

🛑 **Une seule correction fonctionnelle : `DetecterFenetres`. Pas de refonte des bases, pas de
`Sorts.lua`, pas de gardes de cadence. Rien construit pour publication.**

---
## Réponse de Claude Code

### En deux lignes

Les deux trous sont traités, `DetecterFenetres` est corrigé avec le moyen de
revenir sur un échec, et les deux bancs mordent — **y compris l'un contre
l'autre**, ce qui est le vrai résultat de la journée.

Sur le ramassage : tu avais raison de retirer ma conclusion. Le « 0,0 Mo » est
maintenant **expliqué** — et l'explication ouvre une piste sérieuse pour les
300→45 de CODEX. Le « 0 ms », lui, reste ouvert.

---

## 🛑 TROU N° 1 — le relevé de ramassage

### Ce que j'ai fait : lire le code du client, pas raisonner

Tu demandais de vérifier `collectgarbage` comme j'avais vérifié
`debugprofilestop`. C'est fait, en remontant la chaîne complète dans le
binaire : `luaB_collectgarbage → lua_gc → luaC_fullgc → markroot/singlestep`.

**Verdict : `collectgarbage` est SAIN.** Rien de bouché, rien de neutralisé, ni
dans `Ascension.exe` ni dans `Extensions.dll`. C'est du Lua 5.1.4 d'origine,
instruction pour instruction. Et `count` ne ment pas : il rend le nombre exact
d'octets que Lua détient.

Les deux moitiés du relevé ne se valent donc pas.

### Le « 0,0 Mo libéré » : EXPLIQUÉ, et ce n'est pas une panne

Deux découvertes dans le binaire, et elles changent la lecture de tout le
dossier :

| ce que fait le client | où |
|---|---|
| pose `lua_gc(SETPAUSE, **110**)` au démarrage — Lua d'origine est à **200** | VA `0x00819c6b` |
| appelle `lua_gc(GCSTEP, 1)` dans sa boucle principale | VA `0x0052aff2` |

**Je les ai revérifiées moi-même**, sans faire confiance au rapport : le motif
`6a 6e 6a 06` (`push 110 ; push 6`, et 6 est le code de `SETPAUSE`) existe **une
seule fois dans tout l'exécutable**, suivi de `push ecx` et d'un appel. Idem
pour `6a 01 6a 05` (`push 1 ; push 5`, 5 = `GCSTEP`).

**Le jeu ramasse donc en permanence, tout seul, avec un réglage très serré.**
Quand on lui demande un `collect` explicite, il n'y a presque plus rien à faire —
le travail a déjà été fait, morceau par morceau.

> **Une nuance que je dois reporter, parce que je l'ai vue en relisant les
> octets.** L'appel à `GCSTEP` est gardé par **deux** conditions, pas une :
> `test esi,esi ; je` d'abord, puis `shr ecx,19 ; test cl,1 ; jnz`. Ce n'est
> donc pas « à chaque image sans condition », c'est « à chaque image, sauf si
> l'un de ces deux drapeaux le dit ». L'appel est réel et sur un chemin par
> image ; sa fréquence exacte, non.
>
> Ça ne change rien à la conclusion, parce que **l'instrument lit maintenant le
> réglage en jeu** : `collectgarbage("setpause", x)` rend l'ancienne valeur, donc
> on peut la lire en la reposant aussitôt. Le relevé affichera la vraie valeur
> chez toi, et tranchera sans moi.

Le « 0,0 Mo » n'était donc pas un échec : c'est le résultat attendu. Et le
format `%.1f Mo` écrasait à « 0.0 » tout ce qui était sous 51 Ko, alors que le
compteur est exact à l'octet. On jetait la précision à l'affichage.

### 🛑 Et voilà pourquoi ça compte pour les 300→45 IPS

Si le client fait un pas de ramassage **à chaque image**, alors :

> **le coût de ce pas est payé à chaque image, et il grandit avec la taille du
> tas.**

Notre addon fait passer le tas de ~70 Mo à ~227 Mo. Avec `pause = 110`, les
cycles se relancent presque continûment. **C'est un coût par image, permanent,
proportionnel au tas — exactement la signature qui manquait**, et il est
totalement invisible à mon instrument puisqu'il vit dans la boucle du client, pas
dans notre code.

Ça expliquerait aussi pourquoi « sans l'addon, aucun lag » : sans nous, le tas
est trois fois plus petit.

**Je le pose comme hypothèse, pas comme conclusion** — je viens de me faire
reprendre pour avoir conclu trop vite, je ne vais pas recommencer. Mais elle est
mécaniquement étayée par deux adresses dans le binaire, et surtout **elle est
testable en une ligne** (voir plus bas).

### Le « 0 ms » : PAS expliqué — et voici l'argument qui le rend grave

Tu avais raison de ne pas t'en contenter. Et il y a mieux qu'un ordre de
grandeur : un argument **de structure**, lu dans le binaire.

> **Le coût d'un ramassage complet suit le nombre d'objets VIVANTS, pas la
> quantité de déchet.** La phase de marquage parcourt tout ce qui est
> atteignable ; la phase de balayage parcourt la liste entière, de 0 à la taille
> de la table des chaînes. **Il n'y a aucun raccourci** quand il n'y a rien à
> libérer.

**Conséquence, et elle est décisive : « le jeu tenait déjà son tas propre »
explique le 0,0 Mo, et ZÉRO POUR CENT du 0 ms.** Un tas propre rend un ramassage
*plus cher par octet libéré*, pas plus rapide.

Les chiffres exacts, mesurés sur du vrai Lua 5.1 :

| | |
|---|---|
| `%.0f ms` écrit « 0 » | si et seulement si la durée est **< 0,5 ms** |
| `%.1f Mo` écrit « 0.0 » | si et seulement si le libéré est **< 51,2 Ko** |
| point de bascule sous 0,5 ms | **~24 000 objets dans tout le tas** |
| ce que notre addon charge à lui seul | **~837 000 objets** |

**Le 0 ms est donc arithmétiquement impossible** si nos bases étaient chargées
et si `collectgarbage` a réellement tourné. L'anomalie est du côté du relevé, pas
du client.

> Correction d'un chiffre que j'allais te donner : ma première estimation
> (12 000 objets/ms) venait d'un banc qui tournait sur le mauvais Lua — `lupa`
> rend du 5.5 par défaut, pas du 5.1, et le ramasseur moderne est **3× plus
> rapide**. Refait sur du vrai Lua 5.1 : **~8 000 objets/ms**. L'erreur allait
> dans le sens qui affaiblissait ma thèse ; corrigée, elle la renforce. C'est le
> même piège que `verifier_tout.py` documente depuis le 25/07 — *toujours*
> `lupa.lua51`.

**Deux pistes pour ce 0 ms, dans l'ordre :**

1. **Le relevé ne vient pas du code qu'on croit** — *vraisemblance forte*.
   `Perf.lua` a été réécrit plusieurs fois aujourd'hui. Indice indépendant et
   solide : ton relevé n'a pas la ligne « soit … image(s) à … IPS », qui ne
   s'affiche que si `GetFramerate()` rend autre chose que 0 — ce qui n'arrive pas
   en jeu normal.
2. Autre chose qu'on ne voit pas encore, et que la nouvelle sonde nommera.

> Sur le défaut de format : il est **plausible mais pas prouvé**. Le fichier a
> changé depuis, rien sur le disque n'établit ce qu'il contenait au moment de ton
> relevé. Je ne le compte donc pas comme une explication acquise — seulement
> comme un défaut réel, corrigé.

### Un bon point pour le chargement paresseux, au passage

En comptant les objets, une chose agréable est apparue : **52 Mo de nos ~118 Mo
sont rangés en longues chaînes** (2 348 pour `DB_Objets`, 58 pour `ObjetsNoms`,
73 pour `SortsNoms`). Cette forme-là **se ramasse quasi gratuitement** — 0,04 ms,
contre 240 ms pour la même matière en petits objets.

Le chargement paresseux ne fait donc pas qu'économiser de la mémoire : il range
la matière sous la forme la moins chère à ramasser. C'est un acquis à ne pas
casser, et ça renforce la cible n° 4 du programme 10 (`DB_Sorts`, 19 Mo, plate,
interrogée par identifiant, jamais convertie).

### Ce que j'ai corrigé dans l'affichage

**Un zéro ne peut plus passer pour un résultat.** La sonde s'auto-éprouve
maintenant, et met chaque pièce à la question :

```
L'INSTRUMENT S'EST MIS À L'ÉPREUVE
  1. chronomètre : 200000 tours mesurés à 1.284 ms  -> répond
  2. compteur de tas : 20000 tables font monter le tas de 3072 Ko  -> répond
  3. ramassage : rend 3050 Ko sur 3072 Ko en 84.211 ms  -> libère

LES RÉGLAGES DU RAMASSEUR DU CLIENT
  pause .................. 110 %   (Lua d'origine : 200)
  multiplicateur de pas .. 200 %
  -> réglage SERRÉ : ...
```

- **Le chronomètre** est éprouvé sur une boucle de travail connu. S'il rend
  zéro, c'est l'horloge, pas le ramassage.
- **Le compteur de tas** est éprouvé en fabriquant exprès quelques mégaoctets de
  déchet. S'il ne monte pas, c'est lui qui ment.
- **Le ramassage** est éprouvé en relâchant ce déchet. S'il ne redescend pas,
  `collect` est neutralisé — et ce serait majeur.
- **Les réglages du ramasseur sont LUS en jeu** (`setpause` rend l'ancienne
  valeur, on la repose aussitôt) : plus besoin de me croire sur parole.

À la moindre pièce muette, le relevé écrit **« ** MESURE INVALIDE ** »** en
toutes lettres et ajoute *« Ne tire AUCUNE conclusion des chiffres ci-dessus »*.
Et si les trois répondent alors que la durée est petite, il écrit que **la durée
est vraie** et que cela veut dire que le jeu tenait déjà son tas propre — pas
que la mesure a raté.

Les durées sont désormais en `%.3f ms` et les tailles en Ko en clair.

### L'expérience à faire, et elle vaut le détour

Si l'hypothèse du pas-par-image est juste, **relâcher le ramasseur doit rendre
des images**. Une ligne, réversible, sans rien installer :

```
/run print(collectgarbage("setpause", 400))
```

Ça remonte la pause de 110 à 400 : le ramasseur attend que le tas quadruple
avant de relancer un cycle, donc il travaille beaucoup moins à chaque image.
Note tes IPS avant et après.

- **Si les IPS montent franchement** → l'hypothèse tient, et on sait quoi viser.
- **Si rien ne bouge** → elle tombe, et c'est une bonne nouvelle aussi.

Pour revenir en arrière : `/run collectgarbage("setpause", 110)` ou simplement
`/reload`. **Contrepartie à connaître** : pendant l'essai, la mémoire montera
plus haut avant d'être rendue. C'est un essai de quelques minutes, pas un
réglage à garder.

---

## 🛑 TROU N° 2 — « TOTAL addon » n'était pas le total de l'addon

### L'étiquette est corrigée

Le relevé a maintenant **deux tableaux** au lieu d'un, et ne prétend plus rien
qu'il ne mesure :

```
LES BOUCLES (OnUpdate) — sur les 10 dernières secondes
  module            ms par seconde     PIRE tic      tics/s
  ...
  total des boucles     7.69 ms/s     13.380 ms

LES GREFFES (accroches sur les fonctions du jeu)
  accroche          ms par seconde   PIRE appel    appels/s
  ...
  total des greffes     X.XX ms/s

TOTAL MESURÉ .........    X.XX ms/s
  ⚠ Ce n'est PAS le total de l'addon : c'est le total de ce qui
    est instrumenté (les 6 boucles + les greffes déclarées).
    Ne sont comptés NULLE PART : les gestionnaires d'événements,
    les filtres de tchat, les greffes non déclarées, et le
    chargement des bases. C'est un PLANCHER, pas un plafond.
```

### Les greffes instrumentées

Onze relais posés, sur les plus chaudes :

| relais | ce qu'il mesure | fichier |
|---|---|---|
| **`SetText`** | **tous les écrits de texte de l'interface entière** | `Epreuves.lua:1043` |
| `Bulle:objet` / `:sort` / `:unite` | contenu des bulles d'aide | `Tooltips.lua:1184-1186` |
| `Bulle:rattrape` / `:repasse` | les deux greffes sur `GameTooltip:Show` | `Tooltips.lua:1209,1271` |
| `Bulle:ciblee` | la troisième greffe sur `GameTooltip:Show` | `InterfaceCiblee.lua:109` |
| `Grimoire` | `SpellButton_UpdateButton` | `Epreuves.lua:1403` |
| `MenuDeroulant` | `UIDropDownMenu_AddButton` | `Epreuves.lua:1752` |
| `Gossip` | `GossipFrameUpdate` | `Gossip.lua:125` |
| `SuiviQuetes` | `WatchFrame_Update` | `Quetes.lua:463` |

**La première ligne mérite qu'on s'y arrête.** `hooksecurefunc(methodes,
"SetText", Intercepter)` greffe la méthode `SetText` sur la métatable de
FAMILLES entières de composants. Elle se déclenche donc sur **chaque écriture de
texte de toute l'interface** — la nôtre, celle de Blizzard, celle des autres
addons. C'est très probablement le chemin le plus chaud de l'addon, et il
n'était mesuré nulle part. Tu ne la citais pas dans ta liste ; je l'ai trouvée
en recensant.

`Sorts.lua` n'a **aucune** greffe propre : son moteur est appelé *depuis*
`Tooltips` et `Epreuves`. Son coût apparaîtra donc dans ces lignes-là.

### Ce que je concède, et je préfère l'écrire

**Une greffe ne se démonte pas.** Une boucle `OnUpdate` se démonte — on repose
le gestionnaire d'origine et l'enrobage disparaît. `hooksecurefunc`, non : le jeu
ne sait pas retirer une greffe.

J'installe donc un **relais** : une fonction minuscule qui appelle
`courant(...)`, où `courant` est soit la vraie greffe (mesure éteinte), soit sa
version chronométrée. Éteinte, le prix est **un appel de fonction** — pas un
test, pas une lecture d'horloge, pas une branche.

**Ce n'est pas zéro.** Je ne peux pas tenir ici la promesse « éteinte, elle est
absente » que je tenais pour les boucles. Le relevé chiffre donc ce prix
séparément, sous l'étiquette « payé même éteint ».

Limite à connaître : ce relais ne convient qu'aux greffes dont le jeu **ignore
la valeur de retour** (`hooksecurefunc`, `HookScript`). Un enrobage de méthode
qui doit rendre une valeur ne doit pas passer par là — préserver un nombre
quelconque de retours demanderait une table par appel, c'est-à-dire exactement le
déchet qu'on traque.

### Le banc

`verifier_perf.py` passe de 16 à **31 assertions**. Les nouvelles tiennent :

- un relais **éteint** est transparent (les arguments passent intacts, la vraie
  fonction est appelée une fois et une seule) ;
- un relais **allumé** l'est toujours ;
- **plusieurs relais sous le même nom** comptent tous — c'est le cas réel de
  `SetText`, posé une fois par famille de composants ;
- le relevé ne dit plus « TOTAL addon », dit « total des boucles », sépare
  « total des greffes », et avertit que ce n'est pas le total de l'addon.

**Il mord** : ma première version rangeait l'interrupteur dans le seau plutôt
que dans chaque relais, si bien que seul le dernier posé savait basculer. En
réintroduisant ce défaut, le banc tombe à 1 appel compté au lieu de 2. Sans
cette assertion, l'interception des `SetText` aurait été mesurée **à un
neuvième de sa valeur**, en silence.

---

## BLOC A — `DetecterFenetres` corrigé

### La stratégie que je prends, et pourquoi

**L'attente qui double, plus une reprise limitée en CADENCE quand le cadre
disparaît.**

| | |
|---|---|
| échec n° 1 | on remet le cadre au repos **2 s** |
| puis | 4 s, 8 s, 16 s, et **30 s au plus** |
| cadre qui passe à **caché** | son minuteur est effacé → retesté **tout de suite** à sa réapparition… mais **une fois toutes les 30 s au plus** |
| cadre adopté | ardoise effacée, il passe au suivi normal |
| `PLAYER_ENTERING_WORLD` | purge complète |

> 🛑 **Cette limite de cadence, je ne l'avais pas mise dans la version que je
> t'ai d'abord annoncée. C'était un vrai défaut, et il est mesuré.** Voir « Le
> défaut que j'ai livré » ci-dessous — c'est la partie la plus utile de ce bloc.

**Pourquoi celle-là plutôt qu'une autre.** Les quatre pistes que tu listais ont
chacune un trou, et deux d'entre elles se bouchent mutuellement :

- *Mémoriser l'échec sans plus jamais y revenir* : le moins cher, et le pire.
  C'est le piège que tu décrivais, et **mon banc le prend en flagrant délit**
  (voir plus bas).
- *Purger seulement à `PLAYER_ENTERING_WORLD`* : trop faible. Une fenêtre
  ouverte en cours de session et remplie ensuite ne serait rattrapée qu'au
  prochain changement de zone — c'est-à-dire peut-être jamais de la soirée.
- *Retester à cadence très basse* : ça marche toujours, mais ça paie un coût
  fixe pour du décor qui n'a jamais rien donné. L'attente **qui double** garde
  la garantie et fait tendre le coût vers zéro pour ce qui est stable.
- *Le retour à zéro sur disparition* : ça ne suffit pas seul (une fenêtre qui
  reste affichée ne serait jamais rattrapée), mais c'est **gratuit** — on lit un
  `IsShown()` qu'on lisait déjà — et ça couvre le cas réel le plus fréquent :
  le joueur ferme et rouvre un panneau.

### 🛑 Ce que ça ne couvre PAS

Un cadre qui **reste affiché sans interruption** et qui ne gagne son titre
qu'au bout d'un long moment attend **jusqu'à 30 secondes** avant d'être
traduit. Personne ne perd de traduction — mais elle peut arriver en retard, et
un joueur qui regarde l'écran à ce moment-là verra de l'anglais.

C'est l'échange que j'assume. `ATTENTE_MAX` est une constante nommée, en tête
de la zone : si tu juges que 30 s est trop, c'est un chiffre à changer, pas une
refonte.

### 🛑 Le défaut que j'ai livré — et qu'une contre-lecture a trouvé

Ma première version effaçait **tout** au masquage : le minuteur *et* la mémoire
des échecs. L'intention était bonne (« une fenêtre fermée puis rouverte doit
être retestée sans attendre »). La conséquence ne l'était pas :

> **Un cadre qui CLIGNOTE remettait son compteur à zéro sans arrêt, et repayait
> une descente complète de profondeur 6 à chaque réapparition.**

Et les cadres qui clignotent sont **les plus actifs de l'interface** :
`GameTooltip` — **à chaque survol de souris** —, `CastingBarFrame`, `LootFrame`,
`MirrorTimer1`, `DurabilityFrame`, `ComboFrame`, ceux de DragonUI. En ville,
souris en mouvement, **tout le gain annoncé fondait.**

Mesuré au banc, sur un seul cadre clignotant, 39 réapparitions :

| | fouilles |
|---|---|
| avec mon défaut | **39 sur 39** — une par réapparition |
| après correction | **1 sur 39** |

**Le bon discriminant n'est pas le nombre d'échecs, c'est la cadence.** J'ai
d'abord essayé « trois essais gratuits puis on ne rend plus rien » : ça cassait
le cas de la fenêtre rouverte, qui avait déjà épuisé son quota. Ce qui sépare
vraiment un joueur qui rouvre un panneau d'une bulle d'aide qui clignote, c'est
la **fréquence** — le joueur le fait de temps en temps, la bulle plusieurs fois
par seconde. On limite donc le rythme : **un essai gratuit toutes les 30 s au
plus**, quelle que soit la frénésie du cadre.

### 🛑 Et mon banc ne le voyait pas — deux fois

Je n'ai pas seulement raté le défaut : **mes deux premières tentatives pour le
mesurer ne pouvaient pas échouer.**

1. J'ai d'abord comparé une série à 39 battements avec une série à 78. Le
   résultat était systématiquement négatif ; l'assertion passait quoi qu'il
   arrive.
2. J'ai ensuite comparé deux séries de même forme — mais les attentes du décor
   dérivent pendant l'essai, et cette dérive écrasait complètement le signal.
   Toujours vert, défaut présent.

Ce n'est qu'en **comptant les fouilles du cadre clignotant lui-même**, à la
source, que l'assertion s'est mise à mordre. La leçon est la même que celle des
deux bancs, d'un cran plus loin : **un banc qu'on n'a pas vu échouer n'est pas
un banc, c'est une décoration.** Je l'ai désormais vu échouer sur les trois
défauts qu'il vise.

### Deuxième chose corrigée dans la même fonction

`PorteUnTitre` fabriquait **une fermeture et une table pour les régions, plus
une fermeture et une table pour les enfants, à chaque nœud visité**, jusqu'à six
niveaux de profondeur. C'est la même allocation que celle retirée de
`Plaques.lua` le 28/07 et de `BarresDeVie.lua` le 01/08, et `PorteUnTitre` n'est
appelée que depuis `DetecterFenetres` — donc bien dans le périmètre de la seule
correction autorisée.

`pcall(cadre.GetRegions, cadre)` rend « ok » **suivi de toutes les régions** :
en passant ce résultat tel quel en fin de liste d'arguments, on garde la
protection du `pcall` et on ne fabrique plus rien.

> Une différence de comportement à signaler : l'ancienne version parcourait avec
> `ipairs`, qui s'arrête au premier trou ; la nouvelle voit **toutes** les
> valeurs rendues. Elle est donc légèrement plus complète. En pratique
> `GetRegions` ne rend pas de trou, mais je préfère l'écrire.

### Les deux bancs — et le fait qui compte

`outils/verifier_detection_fenetres.py`, dans le banc de santé quotidien.

**Ils mordent, et je l'ai éprouvé dans les deux sens :**

| version mise à l'épreuve | banc de COÛT | banc CLIGNOTANT | banc FONCTIONNEL |
|---|---|---|---|
| le défaut d'origine (échec jamais mémorisé) | **ROUGE** — 15 756 visites | vert | vert |
| la correction naïve (« on n'y revient jamais ») | vert — **0 visite** | vert | **ROUGE** — 2 traductions perdues |
| **ma 1re correction** (tout effacé au masquage) | vert — 1 212 visites | **ROUGE** — 39 fouilles sur 39 | vert |
| la correction livrée | vert — 1 212 visites | vert — 1 fouille sur 39 | vert |

**C'est ça, le résultat de la journée.** La correction naïve obtient le
*meilleur score possible* au banc de coût — zéro visite — tout en cassant la
fonctionnalité. Un seul banc n'aurait pas seulement manqué le défaut : il
l'aurait **récompensé**.

La leçon vaut au-delà d'ici : *une correction qui échange une ressource contre
une autre a besoin d'un banc par ressource échangée.* Sinon on optimise en
aveugle vers l'extrême de la seule chose qu'on mesure.

### L'avant/après chiffré

Ce que je peux mesurer moi-même, sur un décor simulé de 200 cadres et 20
secondes de jeu :

| | visites |
|---|---|
| avant | **15 756** |
| après | **1 212** |
| | **13 fois moins** |

Et pour un cadre qui clignote, pris isolément : **39 fouilles → 1**.

**Ce que je ne peux PAS te donner : les ms/s en jeu.** Je ne peux pas
reproduire ta scène — ni le nombre réel d'enfants d'`UIParent` à Hurlevent, ni
tes addons, ni ta machine. Aujourd'hui `Epreuves` pesait **7,47 puis
10,11 ms/s, pire tic ~13 ms**.

**Il me faut donc un nouveau relevé de ta part**, même endroit, même conditions :

```
/reload
```
puis va à Valley of Heroes **et** Trade District, `/afr perf`, joue 30 s,
`/afr perf`. C'est la comparaison qui tranchera.

Attention : le relevé a changé de forme (voir TROU 2), il y a maintenant deux
tableaux au lieu d'un.

---

## BLOC B — la mémoire

### La marge en 32 bits : il y en a

J'ai lu l'en-tête PE de `Ascension.exe` :

```
  machine .......... 0x014c  x86 32 bits
  Characteristics .. 0x0123
     LARGE_ADDRESS_AWARE (0x0020) : OUI
```

**Le drapeau est posé.** Le processus dispose donc de **4 Go** d'espace
utilisateur sous un Windows 64 bits, pas 2 Go. Avec 229 Mo de tas Lua, on est à
**environ 6 %** de l'espace d'adressage. Ce n'est pas là que le danger se
trouve.

*(À noter : `Extensions.dll`, la couche Ascension, n'a pas le drapeau — mais
c'est sans effet, seul celui de l'exécutable compte.)*

### Pourquoi mon estimation a raté — deux erreurs, dans le même sens

J'annonçais 85-100 Mo. Le relevé dit 156,6. J'ai mesuré au lieu de raisonner, et
voici ce que j'ai trouvé.

**Erreur n° 1 — j'ai mesuré les DONNÉES et je les ai appelées « l'addon ».**
Ma mesure chargeait `Core.lua` et les 27 bases. Le jeu, lui, charge aussi les 23
modules, et ces modules construisent des **index dérivés qui ne sont dans aucun
fichier** et vivent du login à la déconnexion :

| | |
|---|---|
| les données seules (ce que j'avais mesuré) | 136,4 Mo |
| + le code des modules | 0,4 Mo |
| + **les index dérivés** | **16,4 Mo** |
| total | **153,2 Mo** |

Les index inversés de `Core.lua` pèsent 3,8 Mo, ceux des modules 12,7 Mo — et
ils coûtent **2,1 secondes à construire** au chargement.

**Erreur n° 2, et c'est la grosse — j'ai divisé par deux la mauvaise
quantité.** Je croyais que le tas était 32 Mo de texte et 104 Mo d'ossature, et
j'ai halvé l'ossature. La vraie répartition :

| | |
|---|---|
| **texte pur** | **81,9 Mo** — soit **60 % du tas** |
| en-têtes de chaînes | 9,0 Mo (64 bits) → 6,0 Mo (32 bits) |
| ossature des tables | 45,6 Mo (64 bits) |

**60 % du tas ne rétrécit pas d'un octet entre 64 et 32 bits.** Le texte pèse
pareil partout. Mon estimation refaite proprement donne ~113 Mo pour les bases,
~124 Mo avec les index — beaucoup plus près de 156,6.

### 🛑 Et d'où venait cette sous-estimation du texte ? Du piège que le projet connaît déjà

Mon outil comptait le texte avec `pairs()`. **`pairs()` ne voit pas une base
paresseuse** : ses morceaux de source vivent en variable locale de la fermeture
`__index`. J'ai donc raté ~50 Mo de chaînes.

C'est exactement le piège que `DB_Meta.lua` documente depuis le 24/07 — le
compte de traductions au login ratait ~770 000 textes pour cette raison précise.
**Je l'ai refait, dans un outil de mesure.** J'ai corrigé l'étiquette de
`mesurer_ramassage.py` pour qu'il ne mente plus, et `mesurer_tas_complet.py`
fait désormais le parcours complet en allant chercher les morceaux par
`debug.getupvalue`.

### Ce qui reste à établir

153,2 Mo hors jeu contre 156,6 en jeu, c'est 2 % d'écart — **suspicieusement
proche**, alors que le 32 bits devrait faire descendre le chiffre à ~124 Mo.
Deux explications possibles, et je ne veux pas trancher sans preuve :

- `GetAddOnMemoryUsage` ne compte peut-être pas ce que je crois (mémoire vivante
  ou cumul des allocations ?) ;
- ou les caches qui grossissent en jouant comblent la différence.

C'est en cours de vérification. **Je ne te donne pas de conclusion là-dessus.**

### Le tas monte-t-il sans plafond ?

**Je ne peux pas te répondre depuis ici, et je ne vais pas le déduire.** Les +3 Mo
entre tes deux relevés sont compatibles avec le réveil normal des bases
paresseuses (qui plafonne : `DB_Objets` réveillé en entier ajoute ~70 Mo, puis
plus rien) *comme* avec une croissance continue. Deux relevés à quelques minutes
ne peuvent pas les distinguer.

**La mesure qu'il faut**, et elle est simple : `/afr perf` **au login**, puis
**toutes les 20 minutes pendant deux heures de jeu normal**. Note juste les deux
chiffres de mémoire à chaque fois. Si la courbe s'aplatit, c'est le réveil ; si
elle monte tout droit, c'est une fuite et ça devient une autre affaire.

---

## Ce que j'ai cassé, et ce que j'ai failli casser

Tu le demandes, alors voici — dans l'ordre de gravité.

**0. Celui-là, je ne l'ai pas « failli » : je l'avais livré.** La reprise sans
limite de cadence sur les cadres clignotants (détaillée au BLOC A). Trouvé par
une relecture adverse de mon propre code, mesuré, corrigé, et désormais tenu par
une assertion que j'ai vue échouer. Sans cette relecture, je t'annonçais un gain
qui n'aurait pas existé en ville.

**1. J'ai failli mesurer `SetText` à un neuvième de sa valeur.** Ma première
version du mécanisme de greffe rangeait l'interrupteur dans le compteur plutôt
que dans chaque relais. Comme l'interception des `SetText` se pose **une fois par
famille de composants**, seul le dernier relais posé aurait su basculer : tous
les autres seraient restés muets, pour toujours, sans rien signaler. Le chemin
le plus chaud de l'addon aurait été mesuré presque à zéro, et j'en aurais conclu
qu'il était innocent. **Attrapé par une assertion que j'ai écrite exprès pour ce
cas**, et vérifiée en réintroduisant le défaut.

**2. J'ai failli livrer la correction naïve.** Mémoriser l'échec sans retour
possible donne le *meilleur* score au banc de coût — zéro visite. C'est ton
avertissement qui m'a fait écrire le second banc avant la correction, et c'est
lui qui a pris la version naïve en flagrant délit. Sans lui, je livrais une
optimisation qui perdait des traductions en silence.

**3. J'ai refait un piège que le projet documente déjà.** Mon compte du texte
passait par `pairs()`, qui **ne voit pas une base paresseuse** — leurs morceaux
de source vivent en variable locale d'une fermeture. J'ai raté ~50 Mo de
chaînes, et c'est cette sous-estimation qui a produit l'estimation « 85-100 Mo »
que tu as trouvée fausse. `DB_Meta.lua` existe précisément parce que ce piège
avait déjà frappé le 24/07, sur le compte des traductions. **Je l'ai refait, dans
un outil de mesure.** L'étiquette de `mesurer_ramassage.py` est corrigée pour
qu'elle ne mente plus.

**4. Deux parenthèses manquantes**, sur les deux greffes qui enveloppent une
fonction anonyme. Rattrapé par le contrôle de syntaxe avant tout le reste —
c'est exactement à ça qu'il sert.

---

## 🛑 Une chose que j'ai trouvée en chemin, et qui n'attend pas

**Le code source de l'addon n'est sous aucun contrôle de version.**

`WOW_Priv\...\AddOns\AscensionFR\` — `Core.lua`, le `.toc` et les 24 fichiers de
`Modules\` — n'est dans aucun dépôt git. Le dépôt du projet est `WorkFlow\`, qui
ne couvre pas ce dossier.

**Ce code n'existe donc qu'en un seul exemplaire, sans historique.** Aujourd'hui
j'ai réécrit `Perf.lua` une dizaine de fois : aucune version intermédiaire n'est
récupérable. Une mauvaise modification, une régénération ratée ou un disque
abîmé emporterait tout.

Ce n'est pas dans le programme et je n'y touche pas. Mais c'est ~500 Ko de code
(le dossier `DB\` de 101,7 Mo, lui, est régénérable et ne doit pas être
versionné), et **c'est le genre de chose qu'on regrette une seule fois**. J'ai
posé une tâche séparée pour que tu puisses la lancer d'un clic.

---

## Ce que j'ai livré

**Modifiés**
- `Modules/Epreuves.lua` — `DetecterFenetres` corrigé (mémoire des échecs à
  attente qui double + retour à zéro sur disparition + purge au changement de
  monde) ; `PorteUnTitre` sans allocation ; 3 relais de mesure
- `Modules/Perf.lua` — sonde de ramassage auto-éprouvée, lecture des réglages du
  ramasseur, mécanisme de greffes, étiquettes corrigées
- `Modules/Tooltips.lua`, `Gossip.lua`, `Quetes.lua`, `InterfaceCiblee.lua` —
  8 relais de mesure
- `outils/verifier_perf.py` — 16 → **31 assertions**
- `outils/banc_sante.py` — le nouveau banc au quotidien
- `outils/mesurer_ramassage.py` — étiquette corrigée (sous-estimation du texte)

**Nouveaux**
- `outils/verifier_detection_fenetres.py` — les deux bancs, éprouvés l'un contre
  l'autre
- `outils/mesurer_tas_complet.py` — bases **+ modules + index dérivés**

**Non touchés**
- `Modules/Plaques.lua` — toujours pas une ligne
- aucune refonte des bases, pas de `Sorts.lua`, pas de gardes de cadence
- rien construit pour publication, rien poussé

**Banc de santé : 0 rouge, 0 avertissement, 19 bancs verts.**

---

## Ce qu'il me faut de toi

Par ordre d'utilité :

1. **`/reload`, puis le relevé `Epreuves` refait** aux deux mêmes endroits
   (Valley of Heroes, Trade District). C'est l'avant/après que je ne peux pas
   produire. Référence : **7,47 et 10,11 ms/s, pire tic ~13 ms**.
2. **`/afr perf gc`** avec la nouvelle sonde — elle dira elle-même si la mesure
   vaut quelque chose.
3. **L'essai `setpause`** (une ligne, réversible). C'est celui qui peut faire
   basculer l'affaire des 300→45.
4. Toujours en attente depuis le programme 10 : un relevé en **donjon ou champ
   de bataille**, pour éprouver `Plaques` là où il travaille vraiment.

Et si CODEX peut faire le 2 et le 3, c'est mieux que toi : c'est sa machine qui
porte le symptôme fort.
