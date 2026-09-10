# Demande de code → Claude Code

# 🌍 PROGRAMME 19 — préparer l'ouverture des traductions

**Date :** 2026-08-02

**Ce que veut Dan, dans ses mots :** « l'idée finale est que la communauté crée l'outil, moi je
me contente de le publier ».

**Ce qu'il a tranché :** on publie **les textes**, **pas les outils**. Les contributeurs
proposent des traductions ; les programmes qui fabriquent l'add-on restent chez lui.

🛑 **Ce programme ne publie rien** (sauf un petit nettoyage au bloc F). Il prépare, il éprouve,
il mesure — et il s'arrête pour que Dan décide avec des chiffres réels devant lui. Publier des
traductions ne se défait pas.

---

## Le constat qui déclenche tout

Le dépôt public `LePetitDan/AscensionFR` contient **124 fichiers : le Hub, des images, de la
doc. Zéro traduction. Zéro Lua.**

Autrement dit : depuis qu'on a ouvert le projet aux contributeurs au programme 14, **personne
n'a jamais pu aider, même en le voulant.** Il n'y a rien sur quoi travailler. C'est le mur, et
il passe avant Linux.

---

## 🛑 BLOC 0 — la règle qui ne se discute pas

Le dépôt privé `WorkFlow` **porte le webhook dans son historique**. Il ne doit **jamais** avoir
de remote, jamais être poussé, jamais être filtré pour être publié.

**Le nouvel arbre public se construit à neuf :** on copie des fichiers dans un dossier vide, on
fait un `git init`, on fait un premier commit. **Pas de clone, pas de `filter-repo`, pas de
greffe d'historique.** Un historique filtré laisse des objets récupérables ; on ne joue pas à ça
avec un jeton.

Et le rappel de cadre : **contribuer n'est pas publier.** Dan garde la clé. Le nouvel arbre ne
doit être branché à **aucun** chemin de mise à jour automatique — ce que les 274 machines
téléchargent ne change pas d'un pouce dans ce programme.

---

## BLOC A — cartographier, et choisir la bonne couche

**Ne copie rien. Lis et mesure.**

Le dossier `WorkFlow` contient au moins `a_traduire/`, `traductions/`, `sources/`, `extraits/`,
`hautsfaits/`, `dragonui/`, `paquet/`, `epreuves/` et `traducteur_fr.py`. Je ne sais pas ce que
chacun fait, et je ne veux pas le deviner.

**Explique-moi la chaîne :** qu'est-ce qui entre, qu'est-ce qui sort, qu'est-ce qui est
**écrit à la main** et qu'est-ce qui est **fabriqué**.

Puis réponds à la seule question qui compte :

> **Quel est le fichier qu'un humain modifie quand il veut corriger un texte français ?**

C'est cette couche-là qu'on publie. Pas celle d'avant, pas celle d'après.

🛑 **Et le piège qui rendrait tout inutile :** si un contributeur corrige ce fichier, est-ce que
la chaîne de Dan **le relit** — ou est-ce qu'elle **l'écrase** à la prochaine exécution depuis
une autre source ? Si les contributions se font effacer, on aura fabriqué du théâtre. **Vérifie
ça avant tout le reste**, et si c'est le cas, dis-le et arrête-toi là.

**Mesure aussi :** combien de fichiers, quel poids, combien d'entrées de traduction. Les
« seaux » et les 35 familles dont on parle depuis une semaine : est-ce l'unité de travail
naturelle pour un contributeur, ou est-ce interne à la chaîne ?

**Enfin, une recommandation, chiffres en main :** ces textes vont-ils dans le dépôt public
existant (`LePetitDan/AscensionFR`, dans un nouveau dossier) ou dans **un dépôt séparé** ?
Pèse les deux — un seul endroit où l'on trouve tout, contre un dépôt qui reste léger et des
garde-fous de publication qu'on ne perturbe pas. **Tranche et justifie.**

---

## 🛑 BLOC B — ce qui ne doit surtout pas partir

Établis la liste de ce qui part, **et surtout de ce qui ne part pas.** Ce qui reste privé, au
minimum, et vérifie-le au lieu de me croire sur parole :

- `traducteur_fr.py` et `outils/` — **décision de Dan : les outils restent chez lui** ;
- `rapports/` — les rapports des joueurs ;
- `discord/` et `discord_aspirateur.json` — **il y a un jeton de robot là-dedans** ;
- `noms_recolteurs.local.txt` — d'après son nom, une liste de personnes. **Regarde ce que c'est
  et confirme que ça reste privé** ;
- `cache_db/`, `paquet/`, `dist/`, `archive/`, `forks/`, `depot_forks/`, `etat_client.json`.

Puis, sur ce qui part **et seulement sur ce qui part** :

1. **`balayer_secrets.py`**, plus **le balayage des binaires que tu as écrit au programme 17** —
   on sait maintenant que le balayeur officiel écarte les binaires par extension et qu'il n'avait
   ouvert que 2 fichiers sur 98. Cette cécité est prouvée, ne repasse pas dessus.
2. **Les pseudonymes de joueurs.** Règle du projet : on ne cite jamais un joueur dans les textes
   du projet. Des fichiers de traduction peuvent porter des notes du genre « signalé par … ».
   **Cherche-les explicitement**, ce n'est pas la même recherche qu'un secret.
3. **Les chemins de disque en clair** (`D:\AscensionFR\…`), comme au 17.

**Compte les fichiers que tu as réellement ouverts, et dis-le.** « Balayage propre » sans le
dénominateur ne vaut rien — c'est la leçon du 17.

---

## 🛑 BLOC C — la boucle de retour : c'est ce bloc qui décide de tout

Le reste n'a aucune valeur si ce bloc échoue.

**Éprouve le trajet complet, pour de vrai :**

1. un contributeur récupère l'arbre publié ;
2. il corrige **une** ligne de traduction ;
3. Dan récupère cette correction ;
4. **la correction se retrouve dans l'add-on fabriqué.**

Fais-le concrètement : prends une ligne, change-la dans une copie de l'arbre destiné à la
publication, fais tourner la chaîne de Dan, et **montre-moi le texte modifié dans l'add-on en
sortie**. Pas un raisonnement — la ligne, avant et après.

**Si la chaîne ne sait pas relire depuis un arbre extérieur : dis-le franchement et décris ce
qu'il faudrait.** Ne bricole pas un contournement pour faire passer le test ; c'est exactement
le genre de garde-fou menteur qu'on répare depuis une semaine.

Et dis-moi combien de gestes ça demande à Dan pour intégrer **une** contribution. S'il en faut
douze, l'ouverture ne tiendra pas trois semaines — il sera de moins en moins disponible, c'est
tout le point de ce chantier.

---

## BLOC D — de quoi un contributeur a besoin pour ne pas abandonner

- **Un mode d'emploi à la racine** de l'arbre publié : ce que c'est, comment proposer une
  correction, ce qu'on attend. Court.
- ⚠️ **Les règles de vocabulaire et les arbitrages existent déjà** (les lots « vocabulaire » et
  « arbitrages » de la semaine dernière). Un contributeur qui ne les connaît pas produira du
  travail que Dan devra refaire. **Retrouve-les et dis-moi ce qui peut être publié.**
- **Comment un contributeur sait-il quoi corriger ?** Aujourd'hui les rapports des joueurs sont
  dans un salon Discord fermé (`#rapports-auto`, visible de Dan seul). **Note le manque, ne le
  résous pas** — c'est le programme suivant.
- **Mets à jour `docs/CONTRIBUER.md`** dans le dépôt public existant pour pointer vers le
  nouvel endroit. Sinon personne ne le trouvera.

---

## BLOC E — la licence : je veux ton avis, pas une décision

Aujourd'hui le projet n'a **aucune licence**. Publier des traductions sans licence, c'est
publier quelque chose dont personne ne sait ce qu'il a le droit d'en faire — **y compris le
contributeur dont on veut fusionner la PR.**

Mais le sujet est trouble et je ne veux pas de réponse péremptoire : ces textes sont dérivés du
texte du jeu, sur un serveur privé.

- Qu'est-ce que ça change **en pratique**, pour Dan et pour un contributeur ?
- Que font les projets comparables (les autres add-ons de traduction WoW) ? **Va regarder**,
  ne suppose pas.
- Que ferais-tu, et pourquoi ?

**N'ajoute aucun fichier de licence.** C'est une décision de Dan.

---

## BLOC F — le petit nettoyage (celui-là part pour de bon)

Trois fichiers `compagnon/__pycache__/*.pyc` sont suivis par git dans le dépôt public. J'ai
ouvert le premier : il contient en clair
`D:\AscensionFR\WorkFlow\depot_github\compagnon\compagnon.py` et `D:\AscensionFR\WorkFlow`.

Ce sont des fichiers fabriqués, sans aucune valeur, et **le `.gitignore` les interdit déjà** —
ils ont été commités avant que la règle existe. **Retire-les du suivi et pousse** (Dan
l'autorise), puis vérifie le push avec `git rev-list --count origin/main..main` = 0.

⚠️ **Ne réécris PAS l'historique pour les purger.** Ce chemin n'est pas un secret — il est déjà
visible dans `compagnon.py:2227` (le garde-fou ATELIER) — et réécrire l'historique d'un dépôt
public casse tous les clones et tous les forks existants, **dont celui de Tetardtek**. Le jeu
n'en vaut pas la chandelle.

Et note le vrai enseignement : **le balayeur de secrets n'a jamais ouvert ces fichiers.** Un
`.pyc` porte toujours le chemin absolu de sa source. Ça fait deux fois que cette cécité mord.
Dis-moi ce que tu proposes — je ne te demande pas de le corriger ici.

---

**« Terminé » veut dire :**

> - La chaîne expliquée, et **la couche qu'un humain modifie**, nommée.
> - La réponse au piège du bloc A : est-ce que la chaîne **relit** ou **écrase** ?
> - La liste de ce qui part et de ce qui reste, avec **le nombre de fichiers réellement ouverts**
>   au balayage — secrets, pseudonymes, chemins.
> - **La boucle de retour éprouvée pour de vrai** : une ligne changée, retrouvée dans l'add-on.
>   Et le nombre de gestes que ça coûte à Dan.
> - Ta recommandation : dépôt existant ou dépôt séparé, chiffres à l'appui.
> - Ton avis sur la licence.
> - Les 3 `.pyc` retirés et le push vérifié.
> - Ce qui a résisté, et ce que tu as failli casser.

🛑 **Rien d'autre n'est publié. Aucun nouveau dépôt créé, aucune traduction poussée, aucun tag,
aucune release. `WorkFlow` n'a toujours pas de remote.**

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Puis renommer en `_FAIT.md`.)

---

## ✅ BLOC 0 — vérifié avant de commencer

`git remote -v` dans `WorkFlow` : **aucun remote configuré** (0). Rien n'a été ajouté, rien ne
sera ajouté. Tout ce qui suit se passe soit en lecture, soit dans un banc jetable sous
`%TEMP%`, soit — pour le seul bloc F — dans `depot_github`, qui est un dépôt séparé.

---

## ✅ BLOC A — la chaîne, et la couche qu'un humain modifie

### Ce qui entre, ce qui sort

La chaîne a **quatre entrées** et deux sorties. Elle est orchestrée par
`outils/collecteur.py` — c'est lui, l'« Atelier AscensionFR.exe » du bureau de Dan.

| | quoi | fabriqué ou écrit à la main ? |
|---|---|---|
| **entrée 1** | `sources/frFR/`, `sources/enUS/`, `sources/dbc/` | **fabriqué** — extrait de Blizzard et des DBC d'Ascension. Jamais édité. |
| **entrée 2** | `extraits/rexxar/` | **fabriqué** — les caches WDB du client, ce qu'Ascension sert vraiment |
| **entrée 3** | `rapports/caches/` | **fabriqué** — les caches envoyés par les joueurs |
| **entrée 4** | **`traductions/*.json`** | ⭐ **la couche humaine** — écrite par la machine, **relue et corrigeable à la main** |
| file d'attente | `a_traduire/*.json` | **fabriqué** — ce qui est encore en anglais, produit par le générateur |
| **sortie 1** | `…\AddOns\AscensionFR\DB\*.lua` | **fabriqué** — 51,4 Mo de bases Lua |
| **sortie 2** | rapports de couverture | **fabriqué** |

Le cycle : le générateur croise sources + extraits + `traductions/` → écrit les `DB\*.lua` **et**
remplit `a_traduire/` avec ce qui manque ; le traducteur vide `a_traduire/` vers `traductions/`.
Les deux se relancent en boucle, et `traductions/` grossit.

### La réponse à la question qui compte

> **Quel est le fichier qu'un humain modifie quand il veut corriger un texte français ?**

**`traductions/*.json`.** C'est la seule couche que la chaîne relit sans la refabriquer, et c'est
donc elle qu'on publie. Ni `a_traduire/` (regénéré à chaque cycle), ni les `DB\*.lua` (sortie).

**Mesuré :**

| | fichiers | clés | textes traduits | poids |
|---|---:|---:|---:|---:|
| `traductions/` **vivants** | **40** | 151 669 | **515 231** | **50,5 Mo** |
| `traductions/` sauvegardes `_avant_*`, `.bak` | 61 | — | — | 644 Mo |
| `a_traduire/` (la file, fabriquée) | 17 | 236 670 | 295 468 | 15,3 Mo |

Les 5 plus gros stores portent 86 % du texte : `objets_dbc.json` (184 123), `sorts.json`
(135 604), `objets.json` (98 425), `objets_interdits.json` (24 989), `creatures.json` (13 170).

### 🛑 Le piège : la chaîne relit-elle, ou écrase-t-elle ?

**Réponse : elle relit — à 96,3 %. Et il y a une exception réelle, que je nomme.**

**Le motif de la chaîne courante** (`traducteur_fr.py`, l. 491 et 756) est sans ambiguïté :

```python
restants = [(cle, source) for cle, source in textes if cle not in cible and source]
```

> « Traduit chaque texte **absent** de `cible` et l'y ajoute. »

Une clé déjà présente n'est **jamais** retraduite ni réécrite. C'est structurel, pas un hasard :
la traduction automatique coûte du réseau, donc le code a toujours été écrit pour ne pas refaire
ce qui est fait.

**J'ai passé les 24 scripts qui écrivent dans `traductions/` à l'AST**, en classant **par cible**
(et non par script — mon premier jet classait `fusionner_gisement` en « relit » parce qu'il charge
*un* fichier de `traductions/`, mais pas celui qu'il écrit). Verdict :

**5 stores sont RECONSTRUITS À NEUF — une correction y est perdue :**

| store | reconstruit par | textes |
|---|---|---:|
| `interface_maison.json` | `fusionner_gisement.py --ecrire` | 5 974 |
| `sorts_references.json` | `extraire_sorts_references.py` | 9 276 |
| `emotes.json` | `recolter_emotes.py` | 2 208 |
| `interieurs.json` | `joindre_interieurs.py` | 863 |
| `taxinodes.json` | `traduire_taxinodes.py` | 495 |
| | **total** | **18 816 — 3,7 %** |

**Les 35 autres stores (496 415 textes, 96,3 %) sont relus et complétés.**

**Et pour les 5 reconstruits, il y a une couche amont qui, elle, est humaine.** Pour l'interface —
de loin la plus visible en jeu — c'est **`traductions/gisement_brut.json`** (anglais → français,
5 141 entrées). Le code de Dan le sait déjà : `appliquer_vocabulaire.py` dit en toutes lettres
« *on corrige les deux, sinon la correction serait écrasée au prochain passage* ».

**Donc : je ne déclenche pas l'arrêt.** La chaîne ne mange pas les contributions. Mais publier
`interface_maison.json` **sans** `gisement_brut.json` fabriquerait exactement le théâtre que tu
crains — et c'est vérifié plus bas, pas déduit.

### Les « seaux » et les « 35 familles » : ni l'un ni l'autre n'est une unité de contributeur

- **Les seaux** sont une contrainte de sortie Lua : `AFR.Paresseux` range par
  `identifiant // 512` pour tenir sous les 262 143 constantes de Lua 5.1 (`DB_Repliques.lua` :
  69 477 entrées, **66 seaux**). C'est **interne à la fabrication**, invisible dans `traductions/`.
- **Les 35 familles** étaient un diagnostic PackFR (valeurs sur-portées), **interne** aussi.

**L'unité naturelle d'un contributeur, c'est l'entrée** — une clé, une ligne. Et le regroupement
qui lui parle, c'est **le fichier** : « je corrige des quêtes » = `quetes.json`. Il ne faut lui
imposer ni seau ni famille.

### Recommandation : un **dépôt séparé**, et voici les chiffres

| | dépôt existant (`LePetitDan/AscensionFR`) | **dépôt séparé** |
|---|---|---|
| poids ajouté | 50,5 Mo sur un arbre de **6,2 Mo** (124 fichiers, `.git` de 12 Mo) → **×9,1** | 50,5 Mo, seuls |
| clone du Hub | passe de quelques secondes à ~1 min pour qui ne veut que le Hub | inchangé |
| garde-fous | `verifier_arbre_publie` et `balayer_secrets` balayent **tout l'arbre** à chaque publication de version | intacts, non perturbés |
| gros fichiers | `sorts.json` **21,9 Mo** et `objets_dbc.json` **14,3 Mo** dans le même dépôt que l'exe | isolés |
| « un seul endroit » | ✅ | ❌ — à compenser par un lien dans `docs/CONTRIBUER.md` |

**Je tranche pour le dépôt séparé**, et la raison décisive n'est pas le poids : c'est que
**`balayer_secrets.py` et `verifier_arbre_publie.py` tournent sur l'arbre entier à chaque
publication de version**. Y verser 50 Mo de JSON, c'est allonger et fragiliser le seul chemin de
publication qui marche — celui qui a mordu deux fois cette semaine et qu'on vient de réparer. Une
traduction ratée ne doit jamais pouvoir bloquer la sortie d'un correctif du Compagnon.

Deuxième raison, plus prosaïque : **GitHub n'affiche pas le diff d'un JSON de 21,9 Mo**. Une PR
sur `sorts.json` serait illisible dans les deux sens. Ça ne se règle pas en changeant de dépôt,
mais ça se règle mieux dans un dépôt dédié où l'on peut découper les fichiers sans toucher au
`.spec` ni aux garde-fous du Compagnon.

Nom proposé : **`LePetitDan/AscensionFR-Textes`**.

---

## ✅ BLOC C — la boucle de retour, éprouvée pour de vrai

### Le banc, et pourquoi il ne pouvait pas écrire chez toi

`generateur_db.py` lit tout sous `--base`, mais **écrit dans une constante de module en dur** :

```python
ADDON = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns\AscensionFR"
```

Le lancer tel quel aurait régénéré ton addon de jeu. J'ai donc monté un banc :
`traductions/` en **copie réelle** (50,6 Mo, les `_avant_*` écartés), `a_traduire/`, `extraits/`
et `rapports/caches/` en **copies** aussi — parce que le générateur **écrit** dans les deux
premiers — et `sources/` (998 Mo) en jonction, en lecture seule. Sortie détournée vers le banc.

> ⚠️ J'avais d'abord mis `a_traduire/` en jonction. Ça aurait fait écrire le générateur dans ton
> arbre réel. Rattrapé avant le premier lancement ; les jonctions ont été retirées avec
> `Directory.Delete(path, false)` — qui supprime le lien, pas la cible — et les 3 dossiers
> recomptés après coup (127, 7 532, 24 fichiers : intacts).

Le générateur tourne sur ce banc en **13,5 s** et produit **51,4 Mo** de Lua. **Ton addon réel
n'a pas été touché** — ses fichiers sont toujours datés des 29 et 30/07.

### Les deux lignes, avant et après

J'ai pris **deux vrais défauts**, pas des marqueurs, dans deux couches de nature différente.

**1. Store rédigé — `traductions/quetes.json`, quête 100033**
Typographie française : pas de majuscule après un deux-points.

```
avant : "Arène : Inscription"
après : "Arène : inscription"
```

**Dans l'addon fabriqué :**

```
BANC  …3v3 terminées",""},T="Arène : inscription",TE="Arena: Registration"
RÉEL  …3v3 terminées",""},T="Arène : Inscription",TE="Arena: Registration"
        (ton DB_Quetes.lua actuel, non régénéré)
```

**2. Store dérivé — `traductions/interface_maison.json`, clé `ARMOR_COLON`**
En français, le deux-points prend une espace devant ; la traduction automatique avait recopié la
ponctuation anglaise de « Armor: ».

```
avant : "Armure:"
après : "Armure :"
```

**Dans l'addon fabriqué :**

```
BANC  ARMOR_COLON"]="Armure :"
RÉEL  ARMOR_COLON"]="Armure:"
```

**La boucle fonctionne.** Une ligne changée dans `traductions/` se retrouve dans l'addon.

### 🛑 Le faux départ, qui vaut plus que la réussite

Ma **première** tentative portait sur `VOICEMACRO_0_Gn_1` (« *S'il vous plaît aidez-moi!* » →
« *Aidez-moi, s'il vous plaît !* »). Après régénération, l'addon affichait… **autre chose** :

```
DB_Interface.lua       VOICEMACRO_0_Gn_1"]="S'il vous plaît, aidez-moi !"
GlobalStrings_frFR.lua VOICEMACRO_0_Gn_1  = "S'il vous plaît, aidez-moi !"
```

Cette clé est l'une des **838 déjà couvertes par la traduction officielle Blizzard**. Le
générateur préfère l'officiel, et notre version automatique n'est **jamais posée**. J'avais
corrigé un texte qui ne sort pas.

**C'est un vrai piège pour un contributeur**, et il est mesurable : sur les **5 974** étiquettes
d'interface de notre gisement, **838 (14 %) ne servent à rien** parce que l'officiel gagne. Mon
compte tombe exactement sur celui qu'affiche le générateur lui-même (« 5136 chaînes d'interface
maison, 838 déjà couvertes par l'officiel ») — ce qui me fait confiance dans le chiffre.

Un contributeur qui « corrige l'interface » sans le savoir peut donc travailler pour rien une
fois sur sept. **Ça doit être écrit dans le mode d'emploi** (bloc D).

### Les corrections survivent-elles aux passes de Dan ? — éprouvé, trois fois

| passe | quand | ARMOR_COLON | quête 100033 |
|---|---|---|---|
| état de départ | — | `'Armure :'` | `'Arène : inscription'` |
| **`appliquer_vocabulaire.py --appliquer`** | **étape 6 de l'Atelier, à chaque double-clic** | ✅ `'Armure :'` | ✅ inchangée |
| `fusionner_gisement.py --ecrire`, amont corrigé aussi | à la main | ✅ `'Armure :'` | ✅ inchangée |
| `fusionner_gisement.py --ecrire`, **amont non corrigé** | à la main | ❌ **`'Armure:'`** | ✅ inchangée |

La passe qui tourne à chaque fois (`appliquer_vocabulaire`) annonce **« TOTAL 0 »** et
**« Le gisement d'interface n'a pas bougé »** : elle ne touche que les termes du glossaire
arbitré. **Les contributions ne risquent rien au quotidien.**

La dernière ligne est **le piège reproduit en laboratoire** : corriger `interface_maison.json`
sans corriger `gisement_brut.json` marche… jusqu'à la prochaine reconstruction du gisement, qui
efface la correction sans un mot. C'est pourquoi le dépôt public doit porter **`gisement_brut.json`
comme couche officielle de l'interface**, et pourquoi `interface_maison.json` ne devrait
probablement pas y être publié du tout (voir bloc B).

### Combien de gestes pour intégrer une contribution ?

En l'état, avec un dépôt séparé et **aucun outil à écrire** :

1. `git pull` dans le dépôt des textes ;
2. copier les `traductions/*.json` modifiés vers `WorkFlow\traductions\` ;
3. double-clic sur l'Atelier ;
4. `/reload` en jeu pour vérifier.

**Quatre gestes**, dont deux qu'il fait déjà tous les jours. Le geste 2 est le seul qui soit du
travail nouveau, et c'est celui qui se scripte en dix lignes (`copier_contributions.py`) — je ne
l'écris pas, ce n'est pas demandé, mais je le signale parce que c'est **le seul endroit où
l'ouverture peut s'enrayer**.

Une réserve honnête : ces 4 gestes valent pour **une PR déjà relue**. La relecture, elle, n'est
pas un geste — c'est le vrai coût, et aucun outil ne l'enlèvera.

---

## ✅ BLOC B — ce qui part, ce qui ne part pas

### Ce qui reste privé — vérifié, pas cru sur parole

| | vérification |
|---|---|
| `traducteur_fr.py`, `outils/` (155 scripts) | décision de Dan. Ils portent en plus les chemins machine en dur et la logique de publication |
| `rapports/` | **7 532 fichiers** — les rapports des joueurs |
| `discord_aspirateur.json` | ✅ **jeton de 72 caractères confirmé présent**, avec `salon` et `dernier_message`. Déjà couvert par `.gitignore:11` |
| `noms_recolteurs.local.txt` | ✅ **c'est bien une liste de personnes** : **47 pseudonymes de joueurs** dont le nom s'est retrouvé dans des textes récoltés et doit en être expurgé (purge du 21/07 : 47 noms, 241 textes). Lu par `ingerer_recolte.py` et `construire_zip_release.py`. **Reste privé, sans discussion** — c'est une liste nominative de joueurs. Déjà couvert par `.gitignore:14` |
| `cache_db/`, `paquet/`, `dist/`, `archive/`, `forks/`, `depot_forks/`, `etat_client.json` | fabriqués ou lourds, aucune valeur pour un contributeur |
| `sources/`, `extraits/`, `a_traduire/` | **fabriqués** — regénérés à chaque cycle. Les publier créerait des conflits de PR sur des fichiers que personne n'édite |

Le `.gitignore` de `WorkFlow` porte d'ailleurs déjà l'avertissement en tête : « *DÉPÔT PRIVÉ /
LOCAL UNIQUEMENT — NE JAMAIS POUSSER* ». Rien à y ajouter.

### Ce qui part : 22 fichiers, 463 494 textes, 46,6 Mo

Sur les 40 stores vivants, j'en écarte 18 pour deux raisons distinctes :

- **5 reconstruits à neuf** (`interface_maison`, `sorts_references`, `emotes`, `interieurs`,
  `taxinodes`) — une correction y serait effacée. C'est le piège du bloc A, **prouvé en
  laboratoire au bloc C**. Pour l'interface, la couche amont `gisement_brut.json` part à leur
  place : c'est elle qu'un humain doit modifier.
- **13 fichiers de service** — listes noires, décisions d'arbitrage, caches, `sorts_objet_tdb`.
  Ce ne sont pas des traductions. `propositions_joueurs.json` en fait partie : je l'ai ouvert,
  ses champs sont `actuel` / `cible` / `id` / `propositions` — **aucun champ nominatif** — mais
  il vient des joueurs et il n'a rien à faire dans un dépôt de textes.

Les 22 qui partent, par volume : `objets_dbc.json` (184 123 textes), `sorts.json` (135 604),
`objets.json` (98 425), `creatures.json` (13 170), `quetes.json` (9 787), `objets_monde.json`
(6 518), `gisement_brut.json` (5 141), `vanity_obtention.json` (3 524), puis 14 fichiers de moins
de 2 100 textes.

### Le balayage — et le dénominateur, cette fois

```
FICHIERS RÉELLEMENT OUVERTS ET LUS : 22 / 22   (45,3 Mo de texte)
  1. motifs de secret       : 0     (les 20 familles de balayer_secrets + entropie)
  2. chemins de disque      : 0
  3. pseudonymes de joueurs : 0     (dictionnaire de 47 noms)
```

**22 sur 22.** Pas de cécité aux binaires ici : ce ne sont que des JSON, le balayeur officiel les
lit tous. Le balayage des binaires du programme 17 n'avait donc rien à faire — je le dis plutôt
que de le lancer pour la forme.

**Sur les pseudonymes, la recherche n'est pas générique** : j'ai utilisé comme dictionnaire les
**47 noms de `noms_recolteurs.local.txt`** (+ les 2 en dur dans `ingerer_recolte.py`), mot entier,
insensible à la casse. C'est le meilleur filtre disponible, et il est déjà celui que la chaîne
applique. **Zéro occurrence** dans les 22 fichiers : la purge du 21/07 a tenu.

⚠️ Une limite que je dois nommer : ce dictionnaire ne connaît que les noms **déjà repérés**. Un
pseudo croisé pour la première fois demain ne serait attrapé par personne. La règle « on ne cite
jamais un joueur » reste une vigilance humaine, pas un contrôle automatique.

### Le faux rouge que j'ai failli te livrer

Mon premier motif de chemin (`[A-Za-z]:[\\/]…`) a rapporté **88 « chemins de disque »**. Tous
faux : il attrapait `s:\r\n\r\n` dans du texte de jeu — le `\r` et le `\n` d'une chaîne JSON, pas
un séparateur. Motif resserré (un vrai chemin ne commence pas par `\r`, `\n`, `\t`, et porte au
moins deux segments) : **0**. C'est exactement le piège du `\b` après un souligné, sous une autre
forme — et la seule parade est de **regarder les occurrences** avant d'annoncer un chiffre.

---

## ✅ BLOC D — de quoi un contributeur a besoin

### Le mode d'emploi — rédigé, pas publié

Il est prêt : `scratchpad/LISEZMOI_textes_projet.md`, **une page**. Il tient en quatre étapes
(trouver le fichier, corriger la valeur jamais la clé, ouvrir une PR, attendre la relecture) et
**quatre avertissements**, dont les trois derniers sortent directement de ce que ce programme a
mesuré :

1. la règle par défaut « l'officiel Blizzard gagne, sauf s'il perd une information » ;
2. **ne pas toucher aux codes de format** (`$s1`, `%s`, `|cff…|r`) — un `%s` en trop fait planter
   le jeu, et `fusionner_gisement.py` rejette déjà pour ça ;
3. **les textes d'interface se corrigent dans `gisement_brut.json`**, pas dans le fichier
   reconstruit — le piège du bloc A, écrit noir sur blanc pour qu'aucun contributeur ne le
   découvre en perdant son travail ;
4. **une chaîne d'interface sur sept (838 / 5 974) ne sert à rien** — l'officiel l'emporte. C'est
   ce sur quoi je me suis moi-même trompé au bloc C ; autant que ça serve.

Je ne le pose nulle part : aucun dépôt n'existe encore, et ce programme ne publie rien.

### Les règles de vocabulaire existent déjà, et elles sont publiables

| document | lignes | verdict |
|---|---:|---|
| `4-reference/GLOSSAIRE.md` | 125 | ✅ **publiable tel quel** — balayé : 0 secret, 0 chemin, 0 pseudonyme. C'est exactement ce qu'il faut : la règle par défaut, les termes fixés, les noms de lieux, les corrections de sorts appliquées, les principes appris |
| `4-reference/REGLES.md` | 50 | ⚠️ **pas tel quel** — c'est la consigne interne de Dan à son assistant (« ne rien publier sans son accord », le rituel Discord). Propre techniquement, mais hors sujet pour un contributeur. Trois de ses points méritent d'être repris dans le mode d'emploi : le vocabulaire est arbitré, on ne cite jamais un joueur, on explique simplement — **c'est déjà fait** |
| `rapports/arbitrages_blocG_2026-07.md` et consorts | — | à trier au cas par cas ; pas nécessaires au démarrage |

**Recommandation : publier `GLOSSAIRE.md` à la racine du dépôt de textes**, tel quel. Sans lui, un
contributeur produira du travail que Dan devra refaire — c'est exactement ce que tu craignais.

### Le manque, noté et non résolu

**Un contributeur n'a aujourd'hui aucun moyen de savoir quoi corriger.** Les signalements des
joueurs arrivent dans `#rapports-auto`, salon fermé visible de Dan seul, et le fichier
`traductions/propositions_joueurs.json` — 7 entrées — reste privé. Un contributeur motivé ouvre
`sorts.json`, 135 604 textes, et n'a aucune idée d'où commencer.

C'est le programme suivant, je ne le résous pas. Je note juste que **c'est le vrai goulot** : la
boucle technique marche (bloc C), mais sans file de travail visible, l'ouverture produira quelques
corrections opportunistes et rien de systématique.

### `docs/CONTRIBUER.md` — préparé, pas poussé

Le fichier actuel (47 lignes) s'adresse **aux joueurs** : « envoie ton rapport », « signale une
erreur sur le Discord ». Il ne parle pas du tout à quelqu'un qui voudrait *corriger le texte
lui-même*. Il lui manque une section, en fin de fichier :

```markdown
## Corriger le texte français toi-même

Les traductions vivent dans un dépôt à part :
**[AscensionFR-Textes](https://github.com/LePetitDan/AscensionFR-Textes)**.
Ce sont des fichiers JSON — un éditeur de texte suffit, aucun outil à installer.
Le mode d'emploi et le glossaire sont à la racine.
```

**Je ne l'ai pas écrit dans le dépôt**, et c'est délibéré : le dépôt cible n'existe pas. Poser un
lien mort dans la doc publique serait pire que ne rien poser — c'est le premier endroit où
quelqu'un cliquerait. **Dès que tu crées le dépôt, c'est une ligne à ajouter et un push.**

---

## ✅ BLOC E — la licence : mon avis, et ce que j'ai trouvé

### Ce que ça change en pratique — et ce n'est pas symbolique

Aujourd'hui, sans licence, le dépôt public est en **« tous droits réservés »** par défaut. Ce que
GitHub accorde alors est très étroit, et je l'ai vérifié dans leurs conditions plutôt que de me
fier à ma mémoire :

> « By making a repository public, you grant other Users a nonexclusive, worldwide license to use,
> display, perform and reproduce (by forking) Your Content **through the Service** »

Voir et forker **sur GitHub**. Rien d'autre. Pas d'usage hors du site, pas de redistribution.

Et surtout, le mécanisme qui rendrait les contributions utilisables **ne s'enclenche pas** :

> « Whenever you add Content to a repository **containing notice of a license**, you license that
> Content under the same terms »

**Il faut que le dépôt porte une licence** pour que la contribution soit couverte par elle. Sans
licence, le contributeur garde ses droits sur son texte, **et Dan n'a aucune autorisation de le
redistribuer** dans l'add-on, l'exe et les releases. Autrement dit :

> **L'absence de licence gêne d'abord Dan.** C'est lui qui redistribue. Un contributeur qui
> disparaît, change d'avis, ou dont quelqu'un conteste la contribution laisse un trou juridique
> dans un fichier livré à 274 machines.

C'est le point pratique, et il est indépendant de la question Blizzard.

### Ce que font les projets comparables — j'ai regardé

| projet | licence | dit-il quelque chose du texte dérivé ? |
|---|---|---|
| [WowUkrainizer](https://github.com/Cancri55E/WowUkrainizer) — localisation ukrainienne complète, le plus proche du nôtre | **MIT** (code) + OFL-1.1 (police) | **Non.** Dossier `Database` séparé, mais aucune licence distincte, aucun CLA, rien sur le droit d'auteur du texte de jeu |
| [WoWLang](https://github.com/DiNaSoR/WoWLang) — dépôt multilingue | MIT | non |
| [MyTranslator](https://github.com/JayStalt/MyTranslator) | MIT | non |
| [wow-translate](https://github.com/paokkerkir/wow-translate) | MIT | non |

**Le constat est net : la pratique du milieu est MIT sur tout le dépôt, et silence complet sur le
statut du texte dérivé.** Y compris chez celui qui traduit un jeu entier, comme nous. Personne ne
sépare la licence des données de celle du code, personne ne demande de CLA.

Je ne peux pas te dire que c'est juridiquement solide — c'est une pratique, pas une jurisprudence.
Mais ça veut dire qu'en posant MIT tu ne fais rien d'inhabituel, et qu'en ne posant rien tu es
**moins protégé que tous tes comparables**.

### Ce que je ferais, et pourquoi

**Poser MIT sur le dépôt de textes**, avec **une phrase d'honnêteté** dans le README plutôt qu'un
silence :

> Les textes de ce dépôt sont des traductions dérivées du contenu de World of Warcraft et
> d'Ascension. La licence MIT porte sur **notre travail de traduction** ; elle ne prétend
> accorder aucun droit sur le texte d'origine, qui appartient à ses ayants droit.

Trois raisons :

1. **Ça débloque le cas concret** : la PR d'un contributeur devient utilisable par Dan, sans CLA,
   sans paperasse, automatiquement (clause D.6 ci-dessus). C'est le problème qu'on veut résoudre.
2. **MIT est ce que le contributeur attend.** Une licence exotique fait fuir ; MIT ne se lit même
   pas, on la reconnaît.
3. **La phrase d'honnêteté ne coûte rien et ne t'engage à rien** — elle dit simplement ce qui est
   vrai, au lieu de laisser croire que tu concèdes des droits sur du texte Blizzard. Aucun de tes
   comparables ne le fait ; c'est justement la petite chose qui te met au-dessus d'eux.

**Ce que je ne ferais pas :** demander un CLA (ça tue une contribution bénévole sur deux), ni
inventer une double licence code/données (personne dans ce milieu ne le fait, et ça complique une
décision qui doit rester simple).

**Aucun fichier de licence n'a été ajouté.** C'est ta décision, et elle n'est pas urgente : elle le
devient le jour où tu crées le dépôt.

Sources : [WowUkrainizer](https://github.com/Cancri55E/WowUkrainizer),
[WoWLang](https://github.com/DiNaSoR/WoWLang), [MyTranslator](https://github.com/JayStalt/MyTranslator),
[wow-translate](https://github.com/paokkerkir/wow-translate),
[GitHub Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service).

---

## ✅ BLOC F — le constat était faux, et j'en suis la cause

**Il n'y a pas de `.pyc` suivis par git dans le dépôt public.** Vérifié de trois façons :

```
git ls-files | grep pycache          -> (rien)
git log --all --diff-filter=A -- "*.pyc"  -> (rien : jamais ajoutés à l'historique)
git check-ignore -v <chaque fichier> -> .gitignore:6:__pycache__/   (les trois, ignorés)
```

Les trois fichiers existaient bien sur le disque. Leur date le dit :

```
2026-08-02 07:43:18   compagnon.cpython-312.pyc
2026-08-02 07:43:18   interface_hub.cpython-312.pyc
2026-08-02 07:43:18   parser_wdb.cpython-312.pyc
```

**07:43 ce matin, c'est l'instant où j'ai lancé le Hub depuis l'arbre public au programme 17**
pour reproduire le plantage. Python a écrit son cache de bytecode en passant. Ce ne sont pas des
fichiers « commités avant que la règle existe » — **ce sont mes restes, vieux d'une heure**.

Ils sont supprimés (`rm -rf compagnon/__pycache__`). Le dépôt est propre :
`git status --short` = 0 ligne, 124 fichiers suivis, `origin/main..main` = **0**.

**Rien à retirer du suivi, rien à pousser, aucun historique à ne pas réécrire.** Et surtout : rien
n'a jamais fuité — le chemin `D:\AscensionFR\WorkFlow` que tu as lu dans le premier `.pyc` n'est
allé nulle part.

### Le vrai enseignement, lui, tient debout

Ton raisonnement est juste même si l'incident ne l'était pas : **`balayer_secrets.py` n'aurait
jamais ouvert ces fichiers** si quelqu'un les avait commités. `.pyc` est dans la liste `BINAIRES`
(`secrets_publication.py` l. 195-197), et **un `.pyc` porte toujours le chemin absolu de sa
source** — c'est dans le format, pas un accident.

Ce que je propose, et que je n'ai pas fait :

1. **Que le balayeur dise ce qu'il n'a pas lu.** Une ligne — « *N fichier(s) écarté(s) par
   extension* » — et la cécité cesse d'être invisible. C'est la vraie correction : le défaut n'est
   pas d'écarter les binaires, c'est de **sortir « 0 motif » sans dénominateur**. Deux fois de
   suite j'ai dû ajouter le dénominateur à la main pour que le résultat veuille dire quelque chose.
2. **Traiter à part les binaires fabriqués depuis NOTRE source** (`.pyc`, `.exe`, `.dll`) : eux
   portent nos chemins par construction, contrairement à un PNG. L'extraction de suites
   imprimables du programme 17 suffit, elle est écrite.
3. **Ne rien changer pour les autres binaires** — les 94 PNG du Hub n'avaient aucun segment de
   texte, la cécité y est sans conséquence et l'élargir ferait un balayage lent que personne ne
   lancerait.

---

## 🛑 Terminé — l'état exact

| « Terminé » veut dire | état |
|---|---|
| la chaîne expliquée, la couche humaine nommée | ✅ 4 entrées / 2 sorties ; la couche est **`traductions/*.json`** |
| la chaîne **relit** ou **écrase** ? | ✅ **elle relit à 96,3 %** ; 5 stores (3,7 %) sont reconstruits à neuf, nommés, avec leur couche amont |
| ce qui part / ce qui reste, avec le **nombre de fichiers ouverts** | ✅ **22 partent** (463 494 textes, 46,6 Mo) ; **22/22 réellement ouverts et lus**, 45,3 Mo de texte |
| balayage secrets / pseudonymes / chemins | ✅ **0 / 0 / 0** — pseudonymes cherchés sur un dictionnaire de **47 noms réels**, pas au hasard |
| **la boucle éprouvée pour de vrai** | ✅ 2 lignes changées, retrouvées dans le Lua fabriqué ; + 3 passes d'écrasement éprouvées |
| le nombre de gestes pour Dan | ✅ **4**, dont un seul nouveau (la copie, scriptable en 10 lignes) |
| dépôt existant ou séparé | ✅ **séparé** — `LePetitDan/AscensionFR-Textes` |
| avis sur la licence | ✅ **MIT + une phrase d'honnêteté** ; 4 projets comparables consultés |
| les 3 `.pyc` retirés, push vérifié | ⚠️ **le constat était faux** — jamais suivis, jamais dans l'historique, déjà ignorés. C'étaient **mes restes de 07:43**. Supprimés du disque. **Rien à pousser.** |

**Contrôles de fin :**

```
WorkFlow remotes                       : 0     ← inchangé, comme exigé au bloc 0
depot_github  origin/main..main         : 0
depot_github  git status --short        : 0 ligne
tags sur le distant                     : 33   ← aucun ajouté
fichiers suivis dans le dépôt public    : 124  ← aucun ajouté
```

🛑 **Aucun dépôt créé, aucune traduction poussée, aucun tag, aucune release.** Le seul geste
d'écriture hors banc a été la suppression de mes propres `.pyc`.

### Ce qui a résisté

- **Le motif `if cle not in cible`** de la chaîne : il tient partout où il est censé tenir, et
  c'est lui qui rend l'ouverture possible. Ce n'est pas un hasard — le code a toujours été écrit
  pour ne pas repayer une traduction déjà faite.
- **`appliquer_vocabulaire.py`**, la seule passe qui réécrit et qui tourne à chaque Atelier, a
  répondu **« TOTAL 0 »** et **« le gisement d'interface n'a pas bougé »** sur mes deux
  corrections. Il ne touche que le glossaire arbitré, exactement comme sa doc le promet.
- **Le `.gitignore` de `WorkFlow`** couvrait déjà le jeton (`l. 11`) et la liste nominative
  (`l. 14`). Rien à ajouter — c'est rare et ça mérite d'être dit.
- **Les filtres de `fusionner_gisement`** (format, anglais résiduel, non traduit) ont écarté 5
  clés sur 5 974 en reconstruisant. Ils travaillent.

### Ce que j'ai failli casser, et ce que j'ai eu faux

1. **⚠️ Le plus grave : j'avais monté `a_traduire/` en jonction vers ton arbre réel.** Le
   générateur **écrit** dans ce dossier. Le premier lancement aurait modifié
   `D:\AscensionFR\WorkFlow\a_traduire\`. Rattrapé avant d'exécuter quoi que ce soit — les
   jonctions retirées par `Directory.Delete(path, false)` (qui supprime le lien, pas la cible), et
   les trois dossiers recomptés après : 127, 7 532, 24 fichiers, intacts. **La leçon : un banc
   n'est pas en lecture seule parce qu'on l'a décidé — il faut lire où le programme écrit.**
2. **Mon classement « relit / écrase » était faux au premier jet.** Je jugeais *par script* :
   « il charge un fichier de `traductions/` » → relit. `fusionner_gisement` chargeait bien un
   fichier, mais **pas celui qu'il écrit**. Refait *par cible*. Sans ça je te disais « la chaîne
   relit tout » — faux, et faux exactement là où ça compte.
3. **88 faux chemins de disque** dans le premier balayage : mon motif attrapait `s:\r\n` dans du
   texte de jeu.
4. **Mon extraction des étiquettes officielles ratait 836 clés sur 838** — motif en majuscules
   seules, alors que `VOICEMACRO_0_Gn_1` porte des minuscules. Corrigé, mon compte tombe alors
   exactement sur celui qu'affiche le générateur (5 136 / 838), ce qui est le vrai contrôle.
5. **J'ai corrigé un texte qui ne sort pas.** Premier essai sur une clé couverte par l'officiel
   Blizzard. C'est devenu l'avertissement n° 4 du mode d'emploi — un contributeur sur sept aurait
   fait la même erreur, sans jamais comprendre pourquoi rien ne changeait en jeu.
