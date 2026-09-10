# Demande de code → Claude Code

# 📦 PROGRAMME 12 — sortir la 3.4.1

**Date :** 2026-08-01
**Décision de Dan :** une **3.4.1 correctrice tout de suite**, la 3.5 sera une version de contenu.

🛑 **Aucun nouveau correctif.** Cette version ne contient que ce qui est **déjà fait** aux
programmes 9, 10 et 11. Pas de `DB_Sorts` paresseuse, pas de nettoyage des `_MEI*`, pas de témoin
de lancement, pas de `Sorts.lua`, pas de gardes de cadence, **pas une ligne de `Plaques.lua`**.
On solde, on ne rajoute pas.

---

## Ce que la 3.4.1 contient

**Le Compagnon** (programme 9)

- les **chemins accentués** — un joueur nommé Jérôme n'a peut-être jamais réussi une mise à jour ;
- le relais qui ne peut plus laisser quelqu'un **sans Compagnon du tout** ;
- le contrôle d'intégrité du téléchargement (`MZ`, taille, empreinte GitHub) ;
- le Hub qui dit **pourquoi** un téléchargement a échoué.

**L'addon** (programmes 10 et 11)

- `DetecterFenetres` — **13 fois moins de travail**, module actif par défaut ;
- `PorteUnTitre` et `BarresDeVie` — allocations retirées ;
- `Perf.lua` — l'instrument `/afr perf`.

**Sur `Perf.lua` : oui, il part avec la version.** Il est éteint par défaut et absent quand il est
éteint. Et c'est **la seule façon d'obtenir les relevés de CODEX**, dont la machine porte le
symptôme fort des 300→45. Sans ça, cette panne reste ouverte indéfiniment.

---

## 🛑 BLOC A — la Saison 10 : « ça a l'air de marcher » n'est pas une vérification

Dan a appliqué le patch de 2 Go et l'addon se charge. **Ça ne prouve rien sur les accroches.**

Une greffe posée sur une fonction que le client a renommée ou retirée ne fait pas planter le jeu :
selon qu'elle est gardée ou non, elle **échoue au chargement** ou **ne fait simplement plus rien**.
Dans les deux cas, l'addon « a l'air de marcher » — jusqu'au jour où un joueur ouvre sa fenêtre
d'entraîneur et la trouve en anglais.

**Ce que je te demande :**

1. **Recense toutes les greffes** de l'addon (`hooksecurefunc`, `HookScript`, et les fonctions
   globales du client qu'on appelle) et dis-moi **lesquelles sont gardées** par un
   `if type(x) == "function"` et lesquelles ne le sont pas. Les non gardées sont les fragiles.
2. **Fabrique une vérification en jeu** — une commande, ou un simple `/run` que Dan colle — qui
   liste **les fonctions accrochées qui n'existent plus** sur le client actuel. Courte, lisible,
   sans rien modifier.
3. Vérifie que `## Interface: 30300` est toujours la bonne valeur après le patch.

**Si une greffe est tombée, dis-le et arrête-toi là** : ça change la nature de la version, et
c'est à Dan de trancher. Ne répare rien de ta propre initiative.

---

## BLOC B — la barrière avant publication

Rien ne part tant que les trois passent :

- **le banc de santé complet** — il était à 19 bancs verts au programme 11 ;
- **`verifier_tout.py`** ;
- **la synchronisation du dépôt public.** Au programme 9, `compagnon.py` et `interface_hub.py`
  divergeaient encore, et le garde-fou **refusait de taguer**. C'est le geste 1 de la séquence de
  publication et **il appartient à Dan** — mais dis-moi précisément ce qu'il reste à synchroniser
  pour qu'il puisse le lancer.

**Rappel de la règle du projet :** `VERSION_COMPAGNON` = `.toc` = **tag de release**. Les trois
passent à **3.4.1** ensemble, et `verifier_tout.py` refuse si ce n'est pas le cas.

---

## BLOC C — le journal des changements

Écris-moi le **relevé technique** de ce qui change réellement entre 3.4.0 et 3.4.1 : fichier par
fichier, en une ligne chacun, avec ce que ça répare **du point de vue du joueur**.

Pas de texte d'annonce, pas de mise en forme Discord — **c'est moi qui l'écris**. Je veux la
matière exacte, pas une rédaction.

Et dis-moi franchement, pour chaque correctif : **est-ce que le joueur le verra ?** Certains sont
invisibles (l'intégrité du téléchargement), d'autres se sentent tout de suite (les accents, les
images gagnées). Ça détermine ce que j'annonce et ce que je tais.

---

## BLOC D — construire, sans publier

Construis l'exe, passe la barrière, **et arrête-toi.** Dan dit quand on publie — il l'a toujours
dit et ça ne change pas.

Donne-moi à la fin :

- l'empreinte et la taille de l'exe construit ;
- la confirmation que l'exe du dépôt et celui de `dist/` sont **identiques** (c'est le doublon qui
  peut faire publier une régression, voir les artefacts de build) ;
- ce qui reste à faire **à la main** par Dan, dans l'ordre.

---

## Ce qu'on ne fait PAS dans cette version

Écrit noir sur blanc pour qu'on ne se laisse pas emporter :

- ❌ aucun contenu, aucune traduction, aucun arbitrage — c'est la 3.5 ;
- ❌ pas de refonte des bases, `DB_Sorts` reste comme elle est ;
- ❌ pas de nettoyage des `_MEI*` ni de témoin de lancement — ils attendent toujours les réponses
  des joueurs sur l'antivirus ;
- ❌ rien sur les 300→45, l'enquête n'est pas close.

---

**« Terminé » veut dire :**

> - Le recensement des greffes, et **lesquelles ne survivraient pas** à un renommage.
> - La vérification en jeu, prête à coller.
> - `## Interface` confirmé.
> - Les trois numéros à 3.4.1, la barrière passée, ce qui reste à synchroniser.
> - Le relevé technique des changements, avec « le joueur le verra / ne le verra pas ».
> - L'empreinte de l'exe, et la preuve que dépôt et `dist/` coïncident.
> - Ce que tu as failli casser, s'il y a lieu.

🛑 **Rien de publié, rien de tagué, rien de poussé.**

---
## Réponse de Claude Code

### En deux lignes

**Aucune greffe n'est tombée à cause de la Saison 10.** La version peut sortir.
Tout est construit et vérifié ; rien n'est publié, tagué ni poussé.

Une seule greffe ne répond pas — et elle était déjà morte **avant** le patch,
donc ce n'est pas une victime de la Saison 10.

---

## 🛑 BLOC A — les greffes après le patch

### D'abord : ma première mesure disait « 12 greffes tombées ». Elle avait tort.

Je le raconte parce que c'est le résultat le plus utile du bloc. J'ai failli
t'annoncer une catastrophe qui n'existait pas :

| ce que je regardais | ce que ça disait | pourquoi c'était faux |
|---|---|---|
| le FrameXML extrait le 22/07 | — | **antérieur au patch du 01/08 01:57** : il ne pouvait rien prouver |
| seulement `Interface\FrameXML\` | 12 tombées | la moitié des fonctions vit dans les **addons Blizzard chargés à la demande**, dont les dossiers sur disque ne contiennent qu'un `.pub` de 257 octets |
| seulement `function Nom(...)` | 6 tombées | une globale se déclare aussi `Nom = function(...)` |
| seulement `Data\*.MPQ` | 1 tombée | **le FrameXML de base est dans `Data\enUS\*.MPQ`** |

**Un outil de vérification qui crie au loup est plus dangereux que pas
d'outil** : soit on arrête une version pour rien, soit on prend l'habitude
d'ignorer ses rouges. Il a fallu descendre 12 → 6 → 1 avant d'avoir un signal
utilisable.

La référence finale : **381 fichiers d'interface du client actuel** (FrameXML +
addons Blizzard), extraits des MPQ **dans l'ordre de priorité de chargement** —
parce qu'un correctif peut réécrire un fichier et *retirer* une fonction ; en
prenant l'union des archives on dirait « présente » pour une fonction disparue.

### Le recensement : 27 greffes

Toutes vérifiées contre le client d'après le patch. `outils/verifier_greffes.py`.

**25 répondent.** Les greffes du courrier, de la réputation, des monnaies, du
calendrier, de l'entraîneur, des métiers, du grimoire, des quêtes, du butin, du
marchand, des menus déroulants, des dialogues, du vol, des raccourcis, du
tchat — toutes présentes.

**Les 2 fragiles — non gardées :**

| | |
|---|---|
| `Quetes.lua:462` | `QuestInfo_Display` |
| `Quetes.lua:463` | `QuestLog_Update` |

Elles n'ont **aucun** `if type(x) == "function"`. Si l'une disparaissait un jour,
`hooksecurefunc` lèverait une erreur **au chargement** de l'addon. Les deux
existent aujourd'hui, donc **aucun risque immédiat** — mais ce sont les seules
qui casseraient bruyamment. Je ne les touche pas : ce serait un correctif, et
tu n'en veux aucun dans cette version.

### 🛑 La seule qui ne répond pas — et pourquoi ça ne change PAS la version

```
Metiers.lua:300   SpellBookFrame_UpdateSpells   gardée   *** ABSENTE ***
```

Le client actuel définit `SpellBookFrame_Update`, `_HideSpells`, `_ShowSpells`,
`_UpdatePages`, `_OnLoad`, `_OnEvent`, `_OnShow`, `_OnHide`, `_SetTabType`,
`_PlayOpenSound`, `_PlayCloseSound` — **mais pas `_UpdateSpells`**. Ascension a
son propre grimoire (`Ascension_Spellbook.lua`).

**Ce n'est pas une victime de la Saison 10.** J'ai comparé avec l'extraction du
**22/07, antérieure au patch** : elle ne définissait pas `_UpdateSpells` non
plus. Cette greffe est morte depuis longtemps — probablement depuis toujours sur
ce client.

Elle est **gardée**, donc elle ne se pose simplement pas : aucune erreur, aucun
effet de bord. Et `SpellBookFrame_Update` (ligne 297), qui elle répond, couvre
le même besoin.

**Conclusion du bloc : rien n'est tombé à cause du patch. Je ne m'arrête pas.**
Je signale la ligne 300 comme du code mort à nettoyer — dans la 3.5, pas ici.

### La vérification en jeu : `/afr greffes`

Un `/run` ne tenait pas : 27 noms dépassent la limite de 255 caractères du chat.
C'est donc une commande, et elle sort dans la fenêtre copiable habituelle.

```
/afr greffes
```

Elle interroge le **vrai `_G`** du client en cours — le seul juge de paix. Lire
les fichiers d'interface hors du jeu ne dit pas ce que le moteur expose, ni ce
qu'un addon d'Ascension ajoute au chargement.

Elle distingue trois cas, et le troisième compte :

- **répondent** — rien à dire ;
- **ABSENTES** — la traduction correspondante ne se pose pas ;
- **pas encore jugeables** — les fenêtres qui se chargent à la demande
  (entraîneur, métiers, monnaies, calendrier, raccourcis). Tant que le joueur ne
  les a pas ouvertes une fois, elles n'existent pas encore : les compter comme
  absentes serait un faux rouge, et **un faux rouge qu'on apprend à ignorer,
  c'est un banc perdu**.

> **Le piège que j'ai fermé.** Cette sonde lit une liste de noms écrite à la
> main. Une greffe ajoutée sans y être inscrite ne serait jamais vérifiée — et
> la sonde dirait « tout va bien » en regardant à côté. `verifier_greffes.py`
> compare donc cette liste aux greffes réellement posées dans les modules et
> **passe au rouge si elles divergent**. Éprouvé : j'ai retiré un nom de la
> liste, le banc est tombé en rouge.

### `## Interface: 30300` — confirmé

Lu dans les `.toc` des addons Blizzard du **patch du 01/08** : ils déclarent
tous `30300`. Notre `.toc` aussi. *(Les archives plus anciennes portent 30000 et
30200 — c'est l'historique, pas la valeur courante.)*

---

## BLOC B — la barrière

### Les trois numéros

| | avant | après |
|---|---|---|
| `AscensionFR.toc` | 3.4.0 | **3.4.1** |
| `compagnon/compagnon.py` (privé) | 3.4.0 | **3.4.1** |
| `depot_github/compagnon/compagnon.py` | 3.4.0 | *reste 3.4.0* |
| tag de release | v3.4.0 | *à poser par toi* |

Le `compagnon.py` **public** reste volontairement en 3.4.0 : c'est la
synchronisation — **geste 1, le tien** — qui l'y portera. Le banc lit le fichier
privé, et il est vert :

```
Version de l'addon : 3.4.1
Doctrine de version : .toc = VERSION_COMPAGNON = 3.4.1 — OK
```

### Ce qu'il reste à synchroniser, précisément

Le garde-fou refuse toujours de taguer, et il a raison. **Deux fichiers**, et
voici ce qu'ils portent :

| fichier | ampleur | zones touchées |
|---|---|---|
| `compagnon/compagnon.py` | **+223 / −29** lignes | `reference_asset`, `telecharger_fichier`, `lancer_remplacement`, `travail`, et l'en-tête |
| `compagnon/interface_hub.py` | **+12 / −4** lignes | `_maj_appli_fond` |

C'est exactement le programme 9 : le contrôle d'intégrité, le téléchargement
vérifié, le relais sûr, et le Hub qui dit pourquoi ça a échoué. Plus **1 secret
neutralisé** dans `compagnon.py` (le webhook, remplacé mécaniquement).

Les trois autres sources — `compagnon_hub.py`, `fabriquer_decor_hub.py`,
`AscensionFR_Hub.spec` — sont déjà **identiques**.

La commande, quand tu voudras :

```bash
python outils/synchroniser_depot_public.py --appliquer
```

### La barrière : passée

```
0 ROUGE(S), 0 avertissement(s) — 20 bancs verts
```

`verifier_tout.py` vert (51 fichiers Lua compilés, aucun jeton oublié, doctrine
de version OK, 27 bases toutes régénérables). Deux bancs de plus qu'au
programme 11 : `verifier_greffes.py` s'y ajoute.

---

## BLOC C — le relevé technique

**Repère de départ :** le tag public `v3.4.0` pointe sur un commit du **25/07**.
Tout ce qui suit lui est postérieur — les programmes 9, 10 et 11 sont donc
**intégralement neufs** pour un joueur qui a la 3.4.0.

### Le Compagnon (programme 9)

| fichier | ce qui change | le joueur le verra ? |
|---|---|---|
| `compagnon.py` — `travail`, `lancer_remplacement` | les chemins passent par l'environnement au lieu d'être écrits dans le `.bat` — **un `.bat` est relu par cmd.exe en page de code OEM**, donc un chemin accentué y arrivait abîmé | **OUI, brutalement** — un joueur nommé Jérôme n'a peut-être *jamais* réussi une mise à jour. Pour lui c'est le jour et la nuit |
| `compagnon.py` — `lancer_remplacement` | le relais ne peut plus laisser quelqu'un **sans Compagnon du tout** (renommer un exe en cours d'exécution est permis sous Windows : on garde l'ancien jusqu'à ce que le nouveau soit en place) | **Non — sauf pour ceux à qui c'est arrivé.** C'est une panne qu'on supprime, pas une fonction qu'on ajoute |
| `compagnon.py` — `reference_asset`, `telecharger_fichier` | l'intégrité du téléchargement : en-tête `MZ`, taille et empreinte **annoncées par GitHub** — la référence vient d'ailleurs que du fichier, sinon elle se valide toute seule | **Non.** Invisible tant que rien ne tourne mal. C'est une ceinture de sécurité |
| `interface_hub.py` — `_maj_appli_fond` | le Hub dit **pourquoi** un téléchargement a échoué au lieu d'un échec muet | **OUI quand ça rate** — et c'est précisément là qu'il en a besoin |

### L'addon (programmes 10 et 11)

| fichier | ce qui change | le joueur le verra ? |
|---|---|---|
| `Epreuves.lua` — `DetecterFenetres` | les cadres qui échouent au test sont mémorisés, avec une attente qui double (2 → 30 s) et une reprise limitée en cadence. **15 756 → 1 212 visites** sur 20 s simulées | **OUI.** C'est le module qui pesait **97 à 99 %** de tout ce qu'on a mesuré, avec un pire tic de 13 ms deux fois par seconde. Actif par défaut, donc **tout le monde** |
| `Epreuves.lua` — `PorteUnTitre` | plus aucune table ni fermeture allouée par nœud visité (parcours des varargs) | **Indirectement** — moins de déchet, donc des à-coups plus rares |
| `BarresDeVie.lua` — `Examiner` | l'allocation par tic retirée : **4 888 → 58 octets/tic** | **Non pour la plupart** : ce module est **décoché par défaut**. Seuls ceux qui l'ont activé |
| `Perf.lua` *(nouveau)* | l'instrument `/afr perf` + `/afr greffes` | **Non** — éteint par défaut, et *absent* quand il est éteint. C'est un outil pour nous |
| `Recolte.lua`, `Metiers.lua`, `Tooltips.lua`, `Gossip.lua`, `Quetes.lua`, `InterfaceCiblee.lua` | déclarations et relais de mesure, une ligne chacun | **Non** |

### Ce que je dirais, à ta place

**Ce qui se sent tout de suite :** les micro-lags d'`Epreuves` (tout le monde,
actif par défaut) et les chemins accentués (les joueurs concernés passent de
« jamais » à « ça marche »).

**Ce que je tairais, ou mettrais en une ligne :** l'intégrité du téléchargement
et le relais sûr. Ce sont des pannes qu'on supprime — les annoncer, c'est
surtout apprendre aux joueurs qu'elles existaient.

**Ce que je ne mettrais pas dans l'annonce joueurs du tout :** `Perf.lua`. Il
n'est utile qu'à nous, et le mentionner ferait croire à une fonctionnalité.
En revanche, il faut **demander les relevés à CODEX** — c'est toute la raison
pour laquelle il part avec cette version.

---

## BLOC D — construit, non publié

### Ce qui est sur le disque

| | |
|---|---|
| `compagnon/dist/AscensionFR_Compagnon.exe` | **36,18 Mo** |
| empreinte | `a63c717bc071caa10ecf896684bcc649583dcd7ed14aaf5b084991780058f73c` |
| construit | 01/08 17:32 |
| en-tête | `MZ` — vérifié |

| | |
|---|---|
| `dist/AscensionFR_manuel.zip` | **26,9 Mo** (118,9 Mo décompressés) |
| empreinte | `92e79b7e2cc500044ffb7bb30f03eef575a74c3946ac958a3bd7b1fa3be80e8f` |
| contenu | 58 fichiers — 27 bases, 23 modules, `.toc` en **3.4.1** |

Le zip est passé par sa propre barrière : les 53 `.lua` compilés en **Lua 5.1**
(pas le lupa par défaut), fabriqué sous nom provisoire et mis en place seulement
après contrôle.

### 🛑 Le doublon dont tu parlais — j'ai trouvé pire

Il n'y a pas deux exe, il y en a **trois**, et ils ne sont pas d'accord :

| chemin | date | publié ? |
|---|---|---|
| `compagnon/dist/AscensionFR_Hub.exe` | 01/08 17:32 | non — c'est le **produit** de PyInstaller |
| `compagnon/dist/AscensionFR_Compagnon.exe` | 01/08 17:32 | **OUI** — c'est celui-là que `publier_github.py` envoie |
| `dist/AscensionFR_Compagnon.exe` | **25/07 00:21** | non — **résidu mort** |

**Le problème : aucun script ne fait le renommage.** Le `.spec` produit
`AscensionFR_Hub.exe` ; `publier_github.py` publie `AscensionFR_Compagnon.exe` ;
et le Hub déjà installé chez les joueurs cherche ce nom exact pour se mettre à
jour (`compagnon.py:EXE_ATTENDU`). La copie entre les deux est **un geste
manuel non scripté**.

Avant que je la fasse, `AscensionFR_Compagnon.exe` datait du **28/07** — il ne
contenait donc **rien du programme 9**. Publier dans cet état aurait livré une
régression silencieuse.

Le garde-fou de fraîcheur de `publier_github.py` **aurait mordu** (« l'exe est
plus vieux qu'une de ses sources ») — je l'ai vérifié. Mais il conseille
« reconstruis-le », et reconstruire produit `AscensionFR_Hub.exe`… qui laisse
`Compagnon.exe` périmé. **On tourne en rond.**

J'ai fait la copie. Les deux sont maintenant **identiques** (même empreinte
`a63c717b…`), et le garde-fou passe.

> Je ne scripte pas ce renommage : ce serait un correctif, et tu n'en veux aucun
> dans cette version. **À faire dans la 3.5**, et c'est important.

Quant à `dist/AscensionFR_Compagnon.exe` du 25/07 : **rien ne le lit** — je l'ai
vérifié, aucun script n'y touche. C'est du poids mort qui prête à confusion.
Je ne le supprime pas de moi-même.

### Il n'y a pas d'exe dans le dépôt public

Et c'est correct : les binaires sont des **assets de release**, envoyés par
`gh release create` depuis `compagnon/dist/`. Rien à comparer de ce côté.

---

## Ce qu'il te reste à faire, dans l'ordre

**1. Synchroniser le dépôt public** *(le geste 1, qui t'appartient)*

```bash
python outils/synchroniser_depot_public.py --appliquer
```

Puis vérifier que le garde-fou accepte enfin :

```bash
python outils/verifier_arbre_publie.py
```

**2. Pousser le dépôt public**, puis **poser le tag `v3.4.1`**.

**3. Publier la release** — `publier_github.py`. ⚠️ Rappel : `gh release create`
n'a **pas** de mode simulation ; le lancer **crée** la release.

**4. Discord** : annonce brève + `@everyone` dans `#annonces`, détail dans
`#patch-note`.

**5. Demander à CODEX** ses relevés `/afr perf`. C'est la raison d'être de
`Perf.lua` dans cette version, et la panne des 300→45 reste ouverte sans eux.

🛑 **Rien de publié, rien de tagué, rien de poussé.** L'exe et le zip sont sur
le disque, c'est tout.

---

## Ce que j'ai failli casser

**1. J'ai failli t'annoncer 12 greffes tombées.** C'était ma référence qui était
fausse, trois fois de suite. Une version arrêtée pour rien, ou pire : l'habitude
d'ignorer un outil qui crie au loup.

**2. J'ai failli laisser publier l'exe du 28/07.** La copie
`Hub.exe → Compagnon.exe` n'est scriptée nulle part. Le garde-fou de fraîcheur
l'aurait attrapé — mais son conseil (« reconstruis ») ne résout pas le problème,
donc on aurait tourné en rond jusqu'à comprendre.

**3. Rien d'autre.** Aucun correctif ajouté, `Plaques.lua` toujours pas touché,
les bases inchangées.
