# Demande de code → Claude Code

# 🌉 PROGRAMME 22 — le pont entre l'atelier et le dépôt des textes

**Date :** 2026-08-02

**Le problème, en une phrase :** le programme 20 a publié une **photo** des textes. Dès que Dan
relance l'atelier, sa copie et celle de GitHub s'éloignent — et **recopier un fichier entier dans
un sens ou dans l'autre détruit le travail de l'autre côté.**

**Ce que ça donnerait concrètement, si on ne fait rien :**

- Dan lance l'atelier : 800 quêtes nouvelles arrivent dans son `quetes.json` ;
- un contributeur corrige une faute dans ce fichier, **sur la version de GitHub** ;
- Dan pose le fichier du contributeur par-dessus le sien → **les 800 quêtes disparaissent.**
- Et dans l'autre sens, Dan renvoie ses fichiers → **la correction du contributeur disparaît.**

🛑 **Tant que ce pont n'existe pas, on n'annonce rien aux joueurs.** Perdre la contribution d'un
bénévole, ça ne se rattrape pas : il ne revient pas.

---

## BLOC 0 — les règles du décor

- **`WorkFlow` n'a pas de remote et n'en aura jamais.** Le clone du dépôt des textes vit dans son
  propre dossier, avec son propre `.git`. Range-le où ça ne pollue pas l'arbre privé, et
  **assure-toi qu'il ne peut pas être commité dans `WorkFlow`.**
- **Contribuer n'est pas publier.** Ce pont ne touche ni l'add-on livré, ni le Compagnon, ni les
  5 fichiers surveillés, ni aucune release.
- **Les 5 stores reconstruits à neuf** (`interface_maison`, `sorts_references`, `emotes`,
  `interieurs`, `taxinodes`) **ne sont pas concernés** — ils ne sont pas publiés. `gisement_brut.json`,
  lui, l'est. Revérifie-le, une inversion ici est le pire des bugs.

---

## BLOC A — l'ordre des opérations, et pourquoi il rend le problème facile

Je te propose une règle qui évite la quasi-totalité des conflits. **Éprouve-la, et dis-moi si tu
vois mieux** — mais si tu la gardes, elle doit être imposée par le code, pas par la mémoire de Dan :

> **1. récupérer** (les corrections des contributeurs) → **2. atelier** → **3. publier**

Pourquoi ça marche : l'atelier **n'ajoute que des clés absentes**, il ne réécrit jamais une valeur
existante (tu l'as établi au programme 19, `traducteur_fr.py` l. 491 et 756). Donc si les
corrections rentrent **avant**, la publication qui suit ne peut rien écraser : la copie de Dan
contient tout ce que GitHub contient, plus le nouveau.

🛑 **Et le garde-fou qui va avec :** l'outil doit **refuser de publier** s'il existe sur GitHub des
commits que Dan n'a pas récupérés. C'est exactement le trou « commité mais pas poussé » du
programme 14, vu à l'envers — et il a mordu deux fois cette semaine.

---

## BLOC B — ce que l'outil doit faire, vraiment

**Récupérer.** Ce n'est pas une copie de fichiers, c'est une **fusion clé par clé** :

- ce qui a changé sur GitHub **depuis ce que Dan a publié la dernière fois** est une correction de
  contributeur → elle rentre ;
- le reste ne bouge pas ;
- **si les deux côtés ont modifié la même clé différemment : tu ne devines pas.** Tu t'arrêtes,
  tu nommes le fichier, la clé, les deux valeurs, et tu laisses Dan trancher. Un outil qui choisit
  tout seul dans ce cas finira un jour par choisir mal, en silence.

Note que git te donne la référence « ce que Dan a publié la dernière fois » gratuitement, dans le
clone. **Sers-t'en plutôt que d'inventer un fichier de suivi** — un état stocké à côté finit
toujours par mentir.

**Détecte aussi ce qui ne devrait pas arriver, et rapporte-le au lieu de l'appliquer :**

- une **clé ajoutée** ou **supprimée** par un contributeur (le mode d'emploi dit « corrige la
  valeur, jamais la clé ») ;
- un **code de format cassé** (`$s1`, `%s`, `|cff…|r`) : un `%s` en trop fait planter le jeu, et
  tu as noté que `fusionner_gisement.py` sait déjà rejeter pour ça. **Ne réinvente pas ce
  contrôle : va lire le sien et réutilise-le.**

**Publier.** Copier vers le clone, commiter, pousser, **et vérifier que le push est arrivé**
(`git rev-list --count origin/main..main` = 0). Pas `git status`.

🛑 **Et avant chaque publication, le balayage.** Ce n'est pas une formalité : l'atelier ingère des
textes **récoltés chez les joueurs**, et la purge du 21/07 portait précisément sur 47 pseudonymes
retrouvés dedans. Un texte nouveau peut en porter un nouveau. Donc, sur ce qui part :

- `balayer_secrets.py`, les pseudonymes (dictionnaire de `noms_recolteurs.local.txt`), les chemins
  de disque — **avec le dénominateur**, comme aux programmes 19 et 20 ;
- **un seul motif = refus de publier.** Pas d'avertissement qu'on peut ignorer : un refus.

---

## BLOC C — une décision que je te laisse

**Est-ce que ça doit être une étape de l'atelier, ou un geste séparé ?**

- dans l'atelier : Dan ne peut pas oublier, mais son double-clic quotidien **pousserait alors du
  contenu public tout seul**, sans qu'il regarde ;
- à part : un double-clic de plus, mais il voit le rapport avant que quoi que ce soit parte.

**Tranche et justifie.** Mon inclinaison va au geste séparé — Dan garde la clé, c'est la règle du
projet depuis le début — mais tu as les mains dans le cambouis, pas moi. Ce qui compte : **que ce
soit UN geste**, pas six. Dan sera de moins en moins disponible ; un pont qui demande de la
discipline sera abandonné en trois semaines.

---

## 🛑 BLOC D — les quatre preuves, et la dernière est la plus importante

« Le script tourne » ne prouve rien. Éprouve-le en le mettant en difficulté :

1. **Une vraie correction de contributeur.** Modifie une ligne **sur GitHub**, lance
   « récupérer », et montre-la arrivée dans `traductions/` — **et prouve que rien d'autre n'a
   bougé** (compte les clés avant/après).
2. **L'atelier qui ajoute.** Simule des clés nouvelles côté Dan, publie, et prouve que GitHub les
   a reçues **et que la correction du contributeur y est toujours**.
3. **Le garde-fou.** Essaie de publier avec des commits non récupérés : **il doit refuser.**
   Montre-le refuser, pas seulement le code qui refuse.
4. 🛑 **Le conflit, fabriqué exprès.** Modifie la même clé des deux côtés, différemment. L'outil
   doit **s'arrêter et le dire**, pas choisir. **C'est la preuve qui compte** : c'est le seul cas
   où l'on peut perdre du travail sans s'en apercevoir.

Et remets tout en état après : les corrections de démonstration ne doivent rester ni chez Dan, ni
sur GitHub. **Vérifie-le sur GitHub, pas en local.**

---

## BLOC E — le mode d'emploi de Dan

Trois lignes dans `1-pour-Dan/`, en français simple : quand lancer le pont, dans quel ordre, et
**quoi faire quand il refuse**. Pas de jargon. S'il refuse et que Dan ne sait pas quoi faire, il
contournera — et un garde-fou contourné est pire qu'absent.

---

**« Terminé » veut dire :**

> - L'outil écrit, et **l'ordre imposé par le code** — pas par la mémoire.
> - Une correction venue de GitHub, **arrivée chez Dan sans rien déplacer d'autre**.
> - Des clés nouvelles publiées, **sans effacer la correction**.
> - **Le refus de publier vu mordre** quand des commits n'ont pas été récupérés.
> - **Un conflit fabriqué exprès, et l'outil qui s'arrête au lieu de choisir.**
> - Le balayage intégré, avec son dénominateur, et **le refus sur un seul motif**.
> - Ta décision : étape de l'atelier ou geste séparé, et pourquoi.
> - Le mode d'emploi de Dan.
> - Ce qui a résisté, et ce que tu as failli casser.

🛑 **`WorkFlow` sans remote. Aucun tag, aucune release, aucun des 5 fichiers surveillés touché.**

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Puis renommer en `_FAIT.md`.)

---

## ✅ BLOC 0 — le décor, vérifié

```
remotes de WorkFlow                    : 0
le clone est-il DANS WorkFlow ?        : NON — D:\AscensionFR\depot_textes, à côté
git de WorkFlow le voit-il ?           : 0 ligne — il est hors du dépôt, pas ignoré
le clone a son propre .git et remote   : origin -> AscensionFR-Textes, branche main
```

**Le clone ne peut pas être commité dans `WorkFlow`** : il n'est pas sous son
arbre. C'est plus solide qu'une ligne de `.gitignore`, qui peut être retirée.

**Les 5 stores reconstruits à neuf** sont revérifiés **par le code, à chaque
passage** — pas une fois pour toutes :

- à la récupération, un fichier dérivé qui apparaîtrait dans le dépôt est
  signalé comme anomalie de structure ;
- à la publication, sa seule présence dans le dépôt fait **refuser** l'outil.

`gisement_brut.json`, lui, est bien publié (c'est la couche amont de
l'interface).

---

## ✅ BLOC A — l'ordre, imposé par le code

**Je garde ta règle**, et je n'ai pas trouvé mieux :

> **1. récupérer → 2. atelier → 3. publier**

Ton raisonnement tient : `traducteur_fr.py` l. 491 et 756 ne traitent que
`cle not in cible`. Une clé existante n'est jamais réécrite. Donc si les
corrections rentrent **avant**, la copie de Dan contient tout ce que GitHub
contient, plus le nouveau — et la publication qui suit ne peut rien perdre.

**Le garde-fou qui l'impose**, et c'est lui qui fait que Dan n'a rien à
retenir :

```python
retard = int(git("rev-list", "--count", "main..origin/main"))
if retard:
    REFUS  # + la liste des commits, + la commande exacte à lancer
```

C'est bien le trou du programme 14 vu à l'envers : `git status` serait
**propre** dans ce cas, et ne dirait rien. Seul le compteur de commits le voit.

**Une chose que je n'ai PAS faite, et qui mérite d'être dite :** je n'ai pas
inventé de fichier de suivi pour « ce que Dan a publié la dernière fois ».
`git merge-base main origin/main` le donne gratuitement dans le clone. Un état
stocké à côté survit à un retour arrière, à une restauration, à une
manipulation manuelle — et il ment alors **en silence**, ce qui est le pire
des mensonges.

---

## ✅ BLOC B — ce que l'outil fait

**`outils/pont_textes.py`**, ~430 lignes, `pyflakes` propre.

### Une fusion à trois voies, feuille par feuille

Les stores n'ont pas tous la même forme — `sorts.json` est
`{"descriptions": {…}, "noms": {…}}`, `quetes.json` est
`{id: {"T":…, "OT":[…]}}`, `gisement_brut.json` est `{anglais: français}`.
Plutôt que de connaître chaque forme, l'outil **aplatit** en chemins de
feuille et compare ces chemins. Une seule mécanique couvre les 22 fichiers.

| base | eux (GitHub) | nous (Dan) | décision |
|---|---|---|---|
| = | = | — | le contributeur n'a rien touché → on garde |
| ≠ | changé | = base | **correction de contributeur → elle rentre** |
| ≠ | changé | = eux | déjà d'accord → rien à faire |
| ≠ | changé | changé ≠ eux | 🛑 **CONFLIT — on s'arrête** |

### Ce qu'il détecte et rapporte au lieu d'appliquer

- **clé ajoutée / supprimée** par un contributeur (le mode d'emploi dit
  « corrige la valeur, jamais la clé ») ;
- **clé corrigée sur GitHub mais absente chez Dan** ;
- **code de format abîmé** — et je n'ai réinventé aucun contrôle, j'ai
  réutilisé **les deux qui existent** :

| contrôle | d'où il vient | ce qu'il tient |
|---|---|---|
| `signature_compatible` | `outils/generateur_glue.py` l. 183 | la famille `%s` / `%1$s` — **rangs ET types**, dans les deux sens |
| `codes_perdus` | `outils/fusionner_lots.py` l. 48 | la famille `$n $b $c $g…;` `|cffffffff` `|r` `|T…|t` |

Les deux se complètent exactement : le premier ne connaît pas `$s1` ni les
codes couleur, le second ne vérifie pas les rangs de `%s`. Aucun des deux seul
n'aurait suffi.

### Publier

Copie vers le clone → **balayage** → commit → push → **vérification depuis le
distant** (`rev-list --count origin/main..main` = 0, puis `ls-remote`).

**Le balayage n'est pas une formalité**, et il est intégré : sur ce qui part,
`balayer_secrets` + les **47 pseudonymes** de `noms_recolteurs.local.txt` + les
chemins de disque (motif resserré du programme 19), **avec le dénominateur**.

**Un seul motif = refus**, pas un avertissement. Et le refus **remet le clone
en état** (`git checkout -- traductions/`) avant de sortir : on ne laisse pas
un arbre à moitié écrit derrière soi.

Ton argument était le bon : l'atelier ingère des textes **récoltés chez les
joueurs**, et la purge du 21/07 portait sur 47 pseudonymes trouvés dedans. Un
texte neuf peut en porter un nouveau **n'importe quand**.

---

## ✅ BLOC C — geste séparé, et voici pourquoi

**Je tranche pour le geste séparé**, comme ton inclination — mais pas pour la
raison que tu donnes.

Ton argument (« Dan garde la clé ») est juste et suffirait. Mais il y en a un
plus dur, que le programme 20 a rendu visible : **l'atelier publierait alors
sans que le balayage ait un humain devant lui.** Or le balayage est le seul
contrôle qui protège d'un pseudonyme de joueur nouvellement récolté — et un
refus qu'on lit trois jours plus tard dans un journal, c'est un refus qui n'a
servi à rien.

**Un contre-argument que je dois donner honnêtement :** dans l'atelier, Dan ne
peut pas oublier. Séparé, il peut. Ma réponse est que **l'oubli est sans
gravité ici** — le pont rattrape toujours le retard, dans les deux sens, et
c'est justement ce que la fusion à trois voies garantit. Alors qu'une
publication automatique qui part de travers ne se rattrape pas.

**Et sur « UN geste, pas six » :** c'est tenu. Deux commandes, dont la seconde
**dit elle-même** quoi faire quand elle refuse. `pont_textes.py` sans argument
donne l'état et la commande suivante. Dan n'a rien à retenir.

---

## ✅ BLOC D — les quatre preuves

### 1. Une vraie correction de contributeur

Un clone séparé, une identité différente (« Contributeur d'essai »), un vrai
défaut : `'Félicitations! Vous avez été promu…'` — l'espace insécable manquait
devant le premier `!` alors que le second l'avait.

```
base (dernière publication de Dan) : fb9f44b2
dépôt distant aujourd'hui          : 34e4be87
corrections entrantes  : 1
   divers.json   Congratulations! You have been promoted to a new rank!
       avant : 'Félicitations! Vous avez été promu à un nouveau rang\xa0!'
       après : 'Félicitations\xa0! Vous avez été promu à un nouveau rang\xa0!'
```

**Et rien d'autre n'a bougé** — compté, pas supposé :

```
feuilles avant : 318   après : 318
feuilles MODIFIÉES : 1     ← exactement la clé du contributeur
```

### 2. L'atelier qui ajoute

Deux clés neuves posées côté Dan, puis `--publier --appliquer`. Lu **sur
GitHub** ensuite :

```
a) les clés nouvelles sont-elles arrivées ?
   ESSAI-PONT-22 A wild Murloc appears!    OUI
   ESSAI-PONT-22 Your bags are full.       OUI

b) la correction du CONTRIBUTEUR y est-elle toujours ?
   'Félicitations\xa0! Vous avez été promu à un nouveau rang\xa0!'
   -> INTACTE ✅
```

> ⓘ **Cette épreuve a publié bien plus que mes deux clés** : `objets.json`
> +4 498 feuilles, `sorts.json` +282, `quetes.json` +232… **Dan a lancé son
> Atelier pendant que j'écrivais le pont** (`rapports/atelier_sante.json`
> daté de 14:37:48). Le pont a donc publié du vrai contenu neuf — c'est
> exactement son travail, le balayage est passé (28/28 fichiers, 0 motif), et
> ce contenu **reste** : il est légitime et rend le dépôt plus à jour. Je le
> signale parce que ça s'est produit **pendant un essai**, et qu'une
> publication réelle déclenchée par un test mérite d'être dite.

### 3. Le garde-fou, vu mordre

Le contributeur pousse une seconde correction. Dan tente de publier sans avoir
récupéré :

```
🛑 REFUS — le dépôt distant porte 1 commit(s) que tu n'as pas récupéré(s).
      10c2548 Deuxieme correction de contributeur (essai du garde-fou)

Publier maintenant écraserait ces contributions.
Lance d'abord :  python outils/pont_textes.py --recuperer --appliquer
                                                      (code de sortie : 1)
```

### 4. 🛑 Le conflit, fabriqué exprès

La **même clé**, modifiée des deux côtés, différemment.

```
🛑 1 CONFLIT(S) — LES DEUX CÔTÉS ONT MODIFIÉ LA MÊME CLÉ.
   fichier : divers.json
   clé     : All Nameplates Turned Off
     base (dernière publication) : 'Toutes les plaques signalétiques désactivées'
     chez Dan                    : 'Plaques signalétiques : toutes masquées (…côté Dan)'
     sur GitHub                  : 'Toutes les plaques signalétiques désactivées (ESSAI…)'

Je ne devine pas. RIEN n'a été appliqué.                (code de sortie : 1)
```

**Et « rien appliqué » est vérifié, pas affirmé :**

```
la clé en conflit, chez Dan : la valeur de Dan, INTACTE ✅
le clone a-t-il avancé malgré le conflit ? 78368ab  ← non, il est resté en arrière
```

Le second point compte autant que le premier : si le clone avait avancé, le
conflit aurait **disparu** du prochain passage et la correction du
contributeur aurait été perdue en silence.

### Tout remis en état — et vérifié sur GitHub

```
côté Dan     : sha256sum -c  →  divers.json OK, quetes.json OK
côté GitHub  : 318 feuilles, 0 trace d'essai,
               les deux clés revenues à leur valeur d'origine
état du pont : 0 commit non récupéré, 0 non publié — les deux côtés au même point
```

> ⚠️ **Une correction à ce que j'ai écrit au programme 20.** J'y recommandais
> `raw.githubusercontent.com` comme point de vérification fiable. **Il
> ment** — il m'a rendu l'état d'avant le nettoyage (320 feuilles, les clés
> d'essai encore là) alors que le dépôt était déjà propre. C'est un CDN, il
> cache plusieurs minutes. **Le point fiable pour un état qui vient de
> changer, c'est l'API** (`gh api …/contents/…`), qui a bien rendu 318 et
> 0 trace. Je serais passé à côté si je n'avais pas recoupé.

---

## ✅ BLOC E — le mode d'emploi de Dan

`1-pour-Dan/Le pont des textes — mode d'emploi.md`.

L'ordre en tête, les trois commandes, **et surtout la moitié du document
consacrée à « quand il refuse »** — parce que tu as raison : un garde-fou que
Dan ne sait pas satisfaire sera contourné, et un garde-fou contourné est pire
qu'absent.

Les cinq refus possibles, chacun avec **le geste exact** :

| il dit | Dan fait |
|---|---|
| « commits que tu n'as pas récupérés » | `--recuperer --appliquer`, puis relance. C'est tout |
| « CONFLIT » | il choisit, écrit la valeur qu'il garde dans le fichier nommé, relance |
| « N motif(s) » au balayage | **il ne contourne pas** — si c'est un pseudonyme, il l'ajoute à `noms_recolteurs.local.txt` ; s'il ne comprend pas, il demande |
| « clé AJOUTÉE / SUPPRIMÉE » | il va lire la pull request : c'est peut-être une bonne idée, mais ça se décide |
| « code(s) perdu(s) » | il répond au contributeur — celui-ci ne pouvait pas savoir |

Et la phrase de sortie de secours : *« En cas de doute, lance
`python outils/pont_textes.py` tout court. Il te dit où en sont les deux côtés
et ce qu'il faut faire ensuite. Il n'écrit rien. »*

---

## 🛑 Terminé — l'état exact

| « Terminé » veut dire | état |
|---|---|
| l'outil écrit, **l'ordre imposé par le code** | ✅ `outils/pont_textes.py`, `pyflakes` propre ; `--publier` refuse tant qu'on n'a pas récupéré |
| une correction de GitHub **arrivée sans rien déplacer d'autre** | ✅ **318 → 318 feuilles, exactement 1 modifiée** |
| des clés nouvelles publiées **sans effacer la correction** | ✅ vérifié **sur GitHub** : les 2 clés arrivées, la correction intacte |
| **le refus de publier vu mordre** | ✅ code de sortie 1, le commit nommé, la commande donnée |
| **un conflit fabriqué exprès, l'outil qui s'arrête** | ✅ les 3 valeurs affichées, **rien appliqué**, et **le clone n'a pas avancé** |
| le balayage intégré, dénominateur, **refus sur un seul motif** | ✅ 28/28 fichiers ouverts, 0 motif ; le refus remet le clone en état |
| ta décision : atelier ou geste séparé | ✅ **geste séparé** — et la vraie raison est le balayage, pas seulement la clé |
| le mode d'emploi de Dan | ✅ `1-pour-Dan/`, moitié consacrée aux refus |

**Contrôles de fin :**

```
remotes de WorkFlow                       : 0
depot_textes visible du git privé ?       : 0 ligne — il est hors de l'arbre
dépôt principal, commits non poussés      : 0
tags                                      : 33      ← aucun ajouté
latest                                    : v3.4.1  ← inchangé
les 5 fichiers surveillés                 : aucun touché
```

🛑 **`WorkFlow` sans remote. Aucun tag, aucune release, aucun des 5 fichiers
surveillés touché.**

### Ce qui a résisté

- **Le motif `cle not in cible` de la chaîne.** Toute l'architecture du pont
  en dépend : c'est parce que l'atelier n'écrase jamais une valeur existante
  que « récupérer d'abord » suffit à tout protéger. Un atelier qui réécrivait
  aurait demandé un pont dix fois plus compliqué.
- **Les deux contrôles de format existants**, qui se complètent exactement :
  `signature_compatible` ne connaît pas `$s1` ni les codes couleur,
  `codes_perdus` ne vérifie pas les rangs de `%s`. Aucun des deux seul
  n'aurait suffi — et je n'ai eu à en écrire aucun.
- **`git merge-base`** a rendu la base de fusion sans qu'on ait à inventer un
  fichier de suivi. Le meilleur état est celui qu'on n'a pas à tenir.
- **Le balayage** est passé à 28/28 sur une publication qui portait
  ~5 000 feuilles de contenu neuf, réellement produit par l'atelier de Dan
  pendant l'épreuve. Il a travaillé pour de vrai, pas sur un cas d'école.

### Ce que j'ai failli casser, et ce que j'ai eu faux

1. **🛑 Mon premier jet condamnait le garde-fou à refuser pour toujours.**
   Quand il n'y avait **rien à intégrer**, `--recuperer` sortait sans faire
   avancer le clone. La base de la fusion suivante restait donc l'ancienne
   publication : les mêmes commits étaient réexaminés indéfiniment, et
   `--publier` refusait éternellement en réclamant une récupération **déjà
   faite**. Dan aurait fini par contourner — exactement ce que le bloc E
   cherche à éviter. **Trouvé au contrôle final**, pas par les quatre
   preuves : elles portaient toutes sur des cas où il y avait quelque chose à
   faire. Le cas « rien à faire » est celui qu'on n'éprouve pas.
2. **J'ai publié du vrai contenu pendant un essai.** Dan avait lancé son
   Atelier pendant que j'écrivais le pont ; `--publier --appliquer` a donc
   poussé ~5 000 feuilles réelles avec mes deux clés d'essai. Sans danger — le
   balayage est passé, le contenu est légitime et y reste — mais je ne l'avais
   pas prévu, et j'ai dû comprendre l'écart avant de continuer plutôt que de
   le prendre pour un bug du pont.
3. **`raw.githubusercontent.com` m'a menti**, et je l'avais recommandé au
   programme 20 comme point fiable. Il m'a rendu l'état d'avant nettoyage.
   Le point fiable pour un état qui vient de changer est l'API.
4. **J'ai failli ne pas vérifier que le clone n'avait pas avancé** après le
   conflit. « Rien appliqué chez Dan » ne suffisait pas : si le clone avait
   avancé, le conflit aurait disparu du passage suivant et la correction du
   contributeur aurait été perdue **en silence**. C'est le scénario le plus
   coûteux du programme, et il ne se voit que sur un contrôle qu'on n'a pas
   forcément l'idée de faire.
