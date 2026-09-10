# Demande de code → Claude Code

# 🩹 PROGRAMME 28 — sortir la 3.4.3, et répéter la délégation

**Date :** 2026-08-07
**Dan a donné le GO.**

**Pourquoi cette version, et pourquoi maintenant :** tu as confirmé au programme 27 que **dix
textes portent un code de format que le jeu n'attend pas**, que ça fait planter les add-ons qui
les composent, et que **c'est dans le zip de la 3.4.2 téléchargé par tout le monde**. Emzime l'a
signalé le 25 juillet.

**Dan part en vendanges dans quelques jours et sera INJOIGNABLE pendant trois à quatre semaines,
peut-être plus.** On ne le laisse pas partir en laissant un plantage connu chez 274 personnes
que personne ne pourra corriger.

🛑 **C'est le programme irréversible.** Une release publiée est vue immédiatement par les Hubs
installés.

---

## 🛑 BLOC 0 — la question qui dépasse cette version

**Les dix corrections sont dans l'add-on, pas dans le Compagnon.** Donc en principe **seul le
zip a besoin de changer** : l'exe Windows et le binaire Linux resteraient rigoureusement ceux
de la 3.4.2, déjà éprouvés.

**Réponds à ça AVANT de corriger quoi que ce soit, parce que ça décide bien plus que cette
version.**

Si une release « zip seul » est mécaniquement propre, alors **on peut publier des traductions
sans jamais toucher à l'application** — et c'est exactement la limite de sécurité dont les
remplaçants de Dan ont besoin pendant son absence : publier des corrections de texte sans
hériter du pouvoir d'envoyer du code neuf sur 274 machines.

**Ce que je veux que tu établisses, en lisant le code et pas en supposant :**

- si la release passe en `v3.4.3` et que l'exe reste celui de la 3.4.2, **que voit un Hub
  installé ?** `appli_en_retard` compare quoi à quoi, exactement ?
- **le joueur se verrait-il proposer une mise à jour de l'application vers un exe identique à
  celui qu'il a déjà ?** Si oui, c'est inacceptable : on ne dérange pas 274 personnes pour rien ;
- l'add-on et l'application portent-ils **le même numéro de version**, ou deux numéros
  distincts ? Va lire, ne déduis pas ;
- **existe-t-il une façon propre de ne republier que le zip ?** Si oui, laquelle. Si non,
  pourquoi — et alors on reconstruit tout comme d'habitude, sans discuter.

🛑 **Écris la réponse noir sur blanc, quelle qu'elle soit.** Un « oui » mal fondé ici coûterait
274 notifications inutiles ; un « non » honnête coûte une reconstruction, ce qui n'est rien.

---

## BLOC A — les corrections

**1. Les dix qui font planter.** Ta table du programme 27, avec le français officiel de
Blizzard mot pour mot. **Aucun arbitrage de vocabulaire** — si tu te surprends à choisir un mot,
c'est que tu t'es écarté de l'officiel, arrête-toi.

**2. Les quatre inverses** (`DAYS_ABBR`, `HOURS_ABBR`, `MINUTES_ABBR`, `SECONDS_ABBR`) : chez
nous le nombre manque, les minuteries affichent l'unité toute seule. Pas de plantage, mais
visiblement cassé, même fichier, même famille.

**3. Les 48 globales custom Ascension à spécificateurs**, que tu n'as pas su juger faute de
référence : **ne les touche pas.** Note-les pour le retour de Dan, c'est tout.

⚠️ **Le « bois sauvage » de volther11 n'est PAS dans cette version.** Dan ne l'a pas tranché, et
la règle du projet est de ne pas mêler des modifications de traduction à une version
correctrice. **Prépare-la quand même** — l'arbitrage écrit, la ligne de glossaire, la commande
de la passe de vocabulaire — pour qu'elle parte en un geste au retour, ou tout de suite si Dan
te le dit.

---

## 🛑 BLOC B — la preuve que ça ne plante plus

Tu as démontré le plantage **en vrai Lua 5.1**, celui du client. **Démontre la guérison de la
même façon**, sur les dix, dans le zip reconstruit :

```
format('Durabilité')  -> doit passer
```

Et **le contrôle automatique** (`verifier_formats_glue.py`) : branche-le dans les bancs
**après** le correctif, et **montre-le mordre** en cassant une valeur exprès. Un garde-fou qu'on
n'a pas vu refuser ne prouve rien — c'est la leçon du programme 16.

---

## BLOC C — publier

Selon la réponse du bloc 0 : soit le zip seul, soit la reconstruction complète.

**Les pièges, tous connus :**

1. **`gh release create` n'a aucun mode simulation.**
2. **Ne supprime JAMAIS un tag.** On le déplace en `--force`.
3. **Tout essai en pré-version.**
4. **Les noms d'assets ne changent pas** — va les relire sur la `v3.4.2` avant d'envoyer.
   ⚠️ Le binaire Linux s'appelle `AscensionFR_Hub-linux-x86_64` et **ce nom ne bouge jamais** :
   c'est celui que cherche la mise à jour automatique Linux à venir.

**Puis vérifier depuis l'extérieur, sans se faire confiance :**

- `releases/latest` sert bien **v3.4.3** ;
- **télécharge le zip depuis le lien public**, ouvre-le, et **relis les dix valeurs dedans** —
  c'est la seule preuve que les joueurs reçoivent le correctif ;
- **la `v3.4.2` et la `v3.4.1` intactes**, assets compris — la 3.4.1 porte le binaire Linux sur
  lequel Tetardtek travaille.

> ⚠️ Pour ce qui vient de changer, l'API — pas `raw.githubusercontent.com`, il t'a menti au
> programme 22.

---

## BLOC D — les textes

Écris-moi, séparément du rapport :

- **le corps de la note de version** ;
- **trois lignes pour l'annonce Discord**, en français simple : ce que ça change pour un joueur ;
- **la réponse finale à Emzime**, avec le numéro de version où son correctif est sorti. Il
  attend depuis le 25 juillet et **c'est lui qui a trouvé la famille** — que ça se voie.

---

**« Terminé » veut dire :**

> - **La réponse du bloc 0**, fondée sur le code : zip seul possible ou non, et pourquoi.
> - Les dix corrections, plus les quatre inverses.
> - **La guérison démontrée en Lua**, et **le contrôle vu mordre**.
> - `v3.4.3` en ligne, **le zip téléchargé depuis le lien public et relu**.
> - Les **v3.4.1 et v3.4.2 intactes**.
> - Le « bois sauvage » **préparé, pas publié**.
> - Les trois textes du bloc D.
> - Ce qui a résisté, et ce que tu as failli casser.

🛑 **Aucun autre tag que `v3.4.3`. La proposition de Tetardtek n'est pas fusionnée.**

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Puis renommer en `_FAIT.md`.)

---

# 🛑 BLOC 0 — le « zip seul » : NON, et voici pourquoi, ligne par ligne

**Réponse courte : non, une release « zip seul » n'est pas propre aujourd'hui — pour des
raisons cousues dans l'exe. On reconstruit tout, comme d'habitude.** Le détail, lu dans le
code et pas supposé :

## Ce que compare un Hub installé

`interface_hub.py:1567` :

```python
self.appli_en_retard = (logique.en_tuple(version)          # le TAG de la release
                        > logique.en_tuple(logique.VERSION_COMPAGNON))  # cuit dans l'exe
```

**L'add-on et l'application portent UN SEUL numéro** — pas deux. C'est la doctrine du 28/07
(« une mise à jour = UN numéro »), née de la boucle infinie de la 3.3.1. Le Hub compare donc
le tag `v3.4.3` au `3.4.2` cuit dans son exe, et conclut « l'application est en retard » —
**alors que seul l'add-on a changé.**

## Les deux façons de publier « zip seul », et pourquoi chacune casse

**Cas 1 — on attache l'exe 3.4.2 (identique) à la v3.4.3.** `url_exe` est rempli, donc les
274 voient « une nouvelle version de l'application est disponible ». Un joueur clique :
36 Mo téléchargés, le relais échange, l'application redémarre… **toujours en 3.4.2 interne**
— et le lien revient. **C'est mot pour mot la boucle infinie du 25-28/07.** Inacceptable,
comme tu l'écris.

**Cas 2 — on n'attache PAS d'exe.** Côté Hub, le lien reste caché (`_maj_appli_proposable`
exige `url_exe`). Mais :

- le **Compagnon v2** des anciens (`compagnon.py:2353`) affiche son étiquette « mise à jour »
  sur la seule comparaison de numéros, **sans regarder `url_exe`** — cliquer ouvre une page
  de releases où il n'y a pas d'exe : une invite permanente vers rien ;
- un **nouveau joueur** qui suit la note de release (« 2 — Le Hub : AscensionFR_Compagnon.exe »)
  ne trouve pas le fichier ;
- et surtout **`publier_github.py` REFUSE** (l. 70-105) : tag = `## Version:` du .toc =
  `VERSION_COMPAGNON`, sans option pour forcer. C'est la barrière que tu as durcie toi-même
  après la 3.3.1.

## Ce que ça veut dire pour la délégation — la vraie question

**En l'état, publier des traductions implique de reconstruire l'application**, donc le
pouvoir d'envoyer du code neuf sur 274 machines. La limite de sécurité que tu cherches —
« corriger des textes sans toucher au code » — **n'existe pas encore mécaniquement.**

Elle est constructible, et c'est un chantier pour après ton retour, pas pour la veille d'un
départ : séparer les deux décisions dans le Hub — l'add-on continue de se comparer au tag,
mais **l'application se comparerait au `digest` de l'asset** (que `reference_asset()` sait
déjà lire) au lieu du tag. Un exe inchangé d'une release à l'autre = pas de proposition. Ce
jour-là, « zip seul » deviendra propre, et tes remplaçants pourront publier du texte sans
jamais fabriquer de code. **Noté pour ton retour ; rien de tout ça dans la 3.4.3.**

---

# BLOC A — les corrections

## Les 14, appliquées — et un refus par construction

Le script de correction refuse de remplacer si la valeur actuelle n'est pas celle attendue
(pas de remplacement à l'aveugle). **14/14 écrites** dans
`Interface/PTRXML/AscensionFR_Glue.lua` : les dix de la famille A et les quatre inverses,
toutes au frFR officiel **mot pour mot** — aucun choix de mot n'a été fait, conformément à
la consigne.

| famille | avant | après (officiel frFR) |
|---|---|---|
| A (×10) | `DURA %d`, `BLOC %.2f`, `ESQU %.2f`, `PARAD %.2f`, `DÉF %d`, `RÉSIL %d`, `B.DÉG %d`, `B.SOIN %d`, `%d min`, `%d sec.` | `Durabilité`, `Blocage`, `Esquive`, `Parade`, `Défense`, `Résilience`, `Bon. dégâts`, `Bon. soins`, `\|4minute:minutes;`, `\|4seconde:secondes;` |
| C (×4) | `\|4jour:jours;`, `h`, `min`, `sec.` | `%d \|4jour:jours;`, `%d \|4h:h;`, `%d \|4min:min;`, `%d \|4sec:sec;` |

## ⚠️ Une vérification que je n'avais pas prévue, et qui valait la peine

Avant de restaurer les 4 inverses, j'ai vérifié que **notre propre add-on** ne composait pas
ces globales. Trouvaille : `Modules/InterfaceCiblee.lua` et `InterfaceUI.lua` documentent un
piège précisément là — **le client d'Ascension injecte `SECONDS_ABBR` dans un `%s`**
(`CAMP_TIMER = "%d %s until logout"`), ce qui fait ressortir un « %d » parasite… **avec les
valeurs officielles aussi, en anglais comme en français** (c'est leur défaut, pas le nôtre).
L'add-on le répare déjà en réécrivant les deux fenêtres concernées (`FORCEES` : CAMP, QUIT)
**sans toucher aux globales**. Restaurer l'officiel est donc sûr : le seul cas de composition
dangereux connu est déjà réécrit par nos soins, et tous les autres consommateurs retrouvent
le comportement Blizzard standard.

## Ce qui n'est PAS touché

- **les 48 globales custom Ascension** à spécificateurs : aucune référence pour les juger,
  listées par l'outil (`famille D`), **intactes** — pour ton retour ;
- **une 49ᵉ trouvée en passant** : le `GlobalStrings.lua` du client d'Ascension lui-même
  porte un `WORLD_PVP_ENTER` modifié (un `%s` ajouté à la chaîne Blizzard). **C'est LEUR
  fichier**, il ne part pas dans notre zip — le balayeur l'exclut désormais explicitement,
  avec le pourquoi en commentaire ;
- **le « bois sauvage »** : pas dans cette version — préparé plus bas.

---

# 🛑 BLOC B — la preuve

## La guérison, démontrée comme le plantage : en vrai Lua 5.1

Les valeurs sont lues **dans le fichier corrigé** et passées en arguments à une fonction Lua
fixe (jamais interpolées dans du code) :

```
les 10 :  format(valeur) SANS argument — le geste qui plantait
  DURABILITY  'Durabilité'          -> passe
  MINUTES     '|4minute:minutes;'   -> passe        (…les 10 passent)

les 4  :  format(valeur, 14) — le nombre doit revenir
  SECONDS_ABBR '%d |4sec:sec;'      -> '14 |4sec:sec;'   (…les 4 rendent le 14)

GUÉRISON DÉMONTRÉE — 14/14.
```

## Le garde-fou, branché ET vu mordre

`verifier_formats_glue.py` est entré dans `BANCS_ATTENDUS` du banc de santé (code 0 attendu),
avec son pourquoi en commentaire. Et parce qu'un garde-fou qu'on n'a pas vu refuser ne prouve
rien :

```
valeur cassée exprès (DURABILITY -> 'DURA %d')  ->  code 1   VERDICT : 1 cas pouvant PLANTER
valeur restaurée                                 ->  code 0
LE GARDE-FOU MORD, puis repasse au vert.
```

## ⚠️ Ce que j'ai failli faire mal, et qui aurait été le pire de la semaine

Le premier exe 3.4.3 a été construit **depuis le mauvais arbre**. Mon `cd compagnon` partait
de `depot_github` — l'arbre PUBLIC, où `WEBHOOK_RAPPORTS = ""`. L'exe sortait à 35,6 Mo au
lieu de 36,2, **sans webhook** (bouton « Envoyer » gris chez tout le monde) et sans
`parser_wdb` (le `pathex` du .spec pointe vers un dossier absent du public). **Détecté par la
ligne « results available in …depot_github… » du journal de PyInstaller**, détruit, reconstruit
depuis l'arbre privé, et vérifié par l'intérieur : 1 flux zlib porte le webhook, 1 porte la
3.4.3. Le smoke-test a suivi : démarrage propre, aucun journal d'incident.

---

# BLOC C — publier

## La release

**`v3.4.3` est en ligne et `latest`** — créée par `publier_github.py` après ses barrières
(trois numéros ACCORD, arbre publié + historique verts, zip reconstruit derrière ses
garde-fous, banc de santé **0 rouge** — avec le nouveau `verifier_formats_glue.py` dedans,
vert au passage).

👉 https://github.com/LePetitDan/AscensionFR/releases/tag/v3.4.3

| asset | taille | sha256 (digest GitHub) |
|---|---|---|
| `AscensionFR_manuel.zip` | 28 423 911 | `80810d5e…697f4c` |
| `AscensionFR_Compagnon.exe` | 37 962 920 | `f20c3188…e1984f` |
| `AscensionFR_Hub-linux-x86_64` | 39 044 616 | `2833d022…40862f` — **attaché après ton clic**, empreinte identique à celle du coureur, HTTP 200 |

## ⚠️ Le binaire Linux : construit à ton approbation, attaché dans la foulée

Le run de distribution attend **« Review deployments »** depuis le début du programme :

👉 https://github.com/LePetitDan/AscensionFR/actions/runs/31204225617

**J'ai choisi de ne pas bloquer la publication dessus, et je le dis clairement** : les dix
plantages sont côté add-on, donc côté zip — c'est lui qui protège les 274. Le binaire Linux
ne sert aujourd'hui qu'à l'essai de Tetardtek, et sa 3.4.2 reste intacte et téléchargeable.
Une veille tourne : dès ton clic, le binaire sera récupéré, renommé
**`AscensionFR_Hub-linux-x86_64`** (le nom qui ne bouge jamais) et attaché à la v3.4.3,
empreinte comparée à celle du coureur.

## Les pièges, tenus

| piège | tenu comment |
|---|---|
| pas de simulation | chaque barrière éprouvée à la main AVANT l'appel |
| jamais supprimer un tag | aucun supprimé, aucun déplacé — v3.4.3 était libre (vérifié release ET `ls-remote`) |
| essais en pré-version | aucun essai créé |
| noms d'assets | relus sur la v3.4.2 par l'API avant l'envoi — identiques |
| l'encodage console | note par fichier UTF-8 posée dans `sys.argv` |

## Vérifié depuis l'extérieur, sans me faire confiance

- **`releases/latest` (API)** : `v3.4.3`, ni brouillon ni pré-version ;
- **le zip TÉLÉCHARGÉ par le lien public** : taille et sha256 **identiques au digest
  GitHub**, `.toc` en 3.4.3, et **les 14 valeurs relues une à une dedans — 14/14
  conformes** (c'est la sortie ci-dessus, la seule preuve qui compte) ;
- l'exe : le digest annoncé par l'API (`f20c3188…`) est celui calculé sur mon build local
  après construction — même fichier ;
- **v3.4.2 et v3.4.1 intactes**, leurs trois assets présents — dont le binaire Linux de la
  3.4.1 sur lequel Tetardtek travaille.

---

# BLOC D — les trois textes

## 1. Le corps de la note de version

**Publié tel quel sur la release** (fichier UTF-8, jamais par la console — le piège de la
3.4.0) :

> Version corrective : **dix textes pouvaient faire planter vos add-ons, et quatre
> minuteries n'affichaient plus le nombre.** Rien d'autre ne change.
>
> ### Des add-ons qui plantaient à cause de dix textes
>
> Dix textes de l'interface (durabilité, esquive, parade, blocage, défense, résilience,
> bonus de dégâts et de soins, minutes, secondes) portaient un code de mise en forme — un
> `%d` — que le jeu n'attend pas à cet endroit. Un add-on qui affiche ces textes, ElvUI par
> exemple, pouvait planter avec une erreur du genre *« bad argument … (number expected, got
> no value) »*.
>
> Les dix reprennent maintenant le texte français officiel de Blizzard, mot pour mot :
> « Durabilité », « Esquive », « Parade »…
>
> ### Des minuteries qui n'affichaient plus le nombre
>
> Le défaut inverse sur quatre abréviations de durée (jours, heures, minutes, secondes) :
> le nombre manquait, et certaines durées s'affichaient « min » ou « sec. » tout court. Le
> nombre est de retour.
>
> ### Un contrôle automatique pour que ça ne revienne pas
>
> Les 1 238 textes de ce fichier sont désormais comparés automatiquement à ce que le jeu
> attend, à chaque construction : cette famille de défauts ne peut plus repasser inaperçue.
>
> ---
>
> *Merci à **Emzime**, qui a trouvé le premier de ces dix textes et signalé le problème avec
> le diagnostic exact — c'est son signalement qui a permis de découvrir toute la famille.*

*(Il est nommé : c'est son pseudo GitHub, sur son propre ticket public, et ton programme
demande « que ça se voie ». Si tu préfères le remerciement collectif, `gh release edit
v3.4.3 --notes-file …` corrige sans toucher aux assets.)*

## 2. L'annonce Discord — trois lignes

> **3.4.3 — des add-ons qui plantaient à cause de nos textes : corrigé.**
> Dix textes de l'interface portaient un code de format qui pouvait faire planter ElvUI et
> d'autres add-ons. Ils reprennent le français officiel, et quatre minuteries qui
> n'affichaient plus le nombre le raffichent.
> Le Hub vous propose la mise à jour tout seul — ou `releases/latest` pour le zip.

*(Rituel : résumé + `@everyone` dans #annonces, le détail dans #patch-note. C'est toi qui
postes.)*

## 3. La réponse finale à Emzime

> Corrigé en **3.4.3**, en ligne aujourd'hui. Ta correction est appliquée à la lettre
> (`DURABILITY = "Durabilité"`, le frFR officiel) — et ton signalement valait plus que sa
> ligne : en balayant les 1 238 globales du fichier avec ton diagnostic comme signature,
> on a trouvé **dix** textes du même type (BLOCK, DODGE, PARRY, MINUTES, SECONDS…), plus
> quatre inverses où le `%d` officiel manquait. Les quatorze sont corrigés, et un contrôle
> automatique compare désormais chaque globale à l'officiel du client à chaque
> construction : la famille que tu as découverte ne peut plus revenir sans déclencher un
> refus. `DURABILITY_TEMPLATE`, comme tu l'avais noté, était légitime et n'a pas bougé.
> Merci — c'est le signalement le plus utile que le projet ait reçu, et la release te
> crédite.

---

# Ce qui a résisté, et ce que j'ai failli casser

## Ce qui a résisté

- **Ton clic d'approbation.** Le run de distribution attend depuis le début du programme ;
  plutôt que de bloquer le correctif des 274 dessus, la release est partie zip+exe et le
  binaire Linux suivra ton geste. C'est la barrière du programme 18 qui fonctionne — pas un
  défaut.
- **Le client d'Ascension lui-même** : son `GlobalStrings.lua` porte un `WORLD_PVP_ENTER`
  modifié (un `%s` ajouté). Leur fichier, pas le nôtre — exclu du balayage avec le pourquoi
  écrit.
- **Le heredoc de Git Bash**, encore : deux vérifications parties en fumée sur un
  antislash. Tout script à expression régulière va dans un fichier, sans exception.

## Ce que j'ai failli casser

- **🛑 Un exe sans webhook chez 274 personnes.** Le premier build 3.4.3 est parti du
  MAUVAIS arbre : mon `cd compagnon` s'appuyait sur le dossier courant, resté dans
  `depot_github` — l'arbre public, webhook vide, `parser_wdb` absent. **Un exe qui démarre,
  s'installe, et dont le bouton « Envoyer » reste gris pour toujours** — le pire genre de
  défaut, celui qui ne plante pas. Attrapé sur la ligne « results available in … » de
  PyInstaller ; détruit, reconstruit du privé, prouvé par décompression de la PYZ (1 flux
  porte le webhook, 1 porte la 3.4.3). La leçon rejoint le renommage jamais scripté : **la
  construction de l'exe dépend du dossier courant et d'un renommage manuel — deux pièges
  humains sur le chemin le plus critique.** À scripter, pour tes remplaçants.
- **Restaurer les 4 ABBR sans lire notre propre add-on.** `InterfaceCiblee.lua` documente un
  parasite `%d` précisément sur `SECONDS_ABBR` — j'aurais pu le réintroduire. Lecture
  faite : le parasite vient du client d'Ascension, existe AUSSI avec les valeurs
  officielles, et l'add-on réécrit déjà les deux fenêtres concernées (`FORCEES`). Restaurer
  l'officiel est sûr, et c'est écrit au bloc A.
- **Conclure « code 0 » sur le code de `tail`.** Mon premier contrôle du balayeur lisait
  `$?` après un tube — c'était le code de `tail`, pas de l'outil. Refait proprement : le
  vrai code était 1, et c'est ce qui a fait trouver le `WORLD_PVP_ENTER` du client.

---

# « Terminé », point par point

| ce que tu demandais | fait ? | où |
|---|---|---|
| **la réponse du bloc 0**, fondée sur le code | ✅ | NON au zip seul — `appli_en_retard` compare le tag au numéro cuit dans l'exe (un seul numéro, doctrine du 28/07) ; les deux variantes cassent (boucle infinie / étiquette v2 vers rien + refus du publieur) ; le chemin vers un vrai canal « texte seul » est nommé pour ton retour |
| les dix corrections + les quatre inverses | ✅ | 14/14, frFR officiel mot pour mot, remplacement refusé si la valeur ne correspond pas |
| **la guérison démontrée en Lua** | ✅ | 14/14 en Lua 5.1 — les 10 passent sans argument, les 4 rendent le nombre |
| **le contrôle vu mordre** | ✅ | valeur cassée exprès → code 1 ; restaurée → 0 ; branché dans `BANCS_ATTENDUS` et vert dans la chaîne de publication |
| `v3.4.3` en ligne, **zip public relu** | ✅ | latest = v3.4.3 ; zip téléchargé du lien public, sha256 = digest GitHub, **14 valeurs relues dedans** |
| **v3.4.1 et v3.4.2 intactes** | ✅ | leurs trois assets présents (API) |
| le « bois sauvage » préparé, pas publié | ✅ | `1-pour-Dan/2026-08-07_arbitrage-wildwood-PRET.md` — l'arbitrage, la ligne de glossaire, la commande |
| les trois textes | ✅ | bloc D — note (en ligne), Discord, réponse à Emzime avec le numéro |
| ce qui a résisté / failli casser | ✅ | ci-dessus — dont l'exe sans webhook attrapé de justesse |

**Reste UNE chose, et elle t'attend :** 👉 **approuver le run Linux**
(https://github.com/LePetitDan/AscensionFR/actions/runs/31204225617 → Review deployments →
`publication` → Approve). La veille attachera le binaire à la v3.4.3 dès que c'est fait —
sous son nom immuable, empreinte vérifiée.

🛑 **Aucun autre tag que `v3.4.3`. La PR de Tetardtek n'est pas fusionnée.**
