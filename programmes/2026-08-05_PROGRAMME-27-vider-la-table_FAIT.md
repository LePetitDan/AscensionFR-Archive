# Demande de code → Claude Code

# 🧹 PROGRAMME 27 — vider la table avant l'absence de Dan

**Date :** 2026-08-05

**Le contexte, et il commande tout :** Dan part pour les vendanges. **Trois à quatre semaines,
peut-être plus, et il sera INJOIGNABLE.** Pas « peu disponible » — injoignable. Aucun clic,
aucune décision, aucun rattrapage possible pendant toute la durée.

L'objectif d'ensemble est que le projet tourne à 100 % sans lui. Ce programme est **la première
étape, celle qui ne présente aucun risque** : on solde ce qui traîne et on retire les blocages
invisibles. Les étapes suivantes (sortir la construction Windows de son PC, publier les outils)
viendront après, et chacune sera un programme à part.

🛑 **Ce programme ne publie aucune version, ne crée aucun tag, ne fusionne rien dans `main`
sans que ce soit demandé explicitement ci-dessous.**

---

## 🛑 BLOC 0 — la barrière qui va tout bloquer

Hier Dan a créé l'environnement `publication` sur `LePetitDan/AscensionFR`, avec
**`Required reviewers` = lui seul**.

**Conséquence si on n'y touche pas : dès qu'il sera parti, toute construction s'arrêtera et
attendra une approbation qui ne viendra jamais.** Le dispositif monté pour le protéger
deviendrait le verrou qui empêche ses remplaçants de travailler.

**Ne le modifie pas toi-même** — c'est un réglage de compte, il appartient à Dan. Mais :

- **va constater l'état réel** de l'environnement et de ses règles, par l'API, et rapporte-le ;
- **écris-lui la marche à suivre exacte** pour ajouter un ou deux approbateurs : où cliquer,
  quoi cocher, et ce que ça change ;
- ⚠️ **et dis-lui la vérité en face :** un remplaçant qui peut approuver ses propres
  constructions, c'est une barrière qui ne mord plus. C'est le prix du 100 %, il l'assume,
  mais il doit le lire écrit noir sur blanc plutôt que le découvrir en octobre.
- **regarde aussi s'il existe d'autres endroits où Dan est le seul à pouvoir débloquer**
  quelque chose — approbation des workflows de contributeurs, réglages d'Actions, protections
  diverses. **Fais-en la liste.** Un blocage invisible qui se déclenche dans dix jours est
  exactement le genre de défaut qu'on répare depuis deux semaines.

---

## BLOC A — solder la proposition de Tetardtek

Elle est relue (programme 25), le verdict est « fusionner », et il ne restait qu'une demande :
son banc d'essai ne passe plus.

🛑 **Ne fusionne pas encore.** Regarde d'abord :

- **a-t-il mis le banc à jour depuis ?** Va voir la PR #5 et son dépôt ;
- **où en sont la #4 et la #5** — état, commits nouveaux, commentaires nouveaux depuis le
  programme 25 ;
- **les six recouvrements tiennent-ils toujours** après ses derniers commits ? Refais la
  fusion à blanc, ce n'est plus le même arbre.

**Puis dis-moi si c'est fusionnable en l'état, ou ce qui manque.** Dan tranchera — mais
**laisser cette proposition en suspens pendant un mois est la pire des options** : c'est le
contributeur le plus sérieux du projet, et il attend.

⚠️ **Rappel du programme 25 :** `plateforme.py` devient un sixième fichier qui entre dans
l'exe, et la liste `SOURCES` de `outils/secrets_publication.py` en compte cinq. **Si on
fusionne sans corriger ça, la prochaine construction Windows casse** — et il n'y aura personne
pour la réparer. Prépare la correction, elle part dans le même geste que la fusion.

---

## BLOC B — les trois personnes qui attendent

Trois contributeurs sont sans réponse, dont deux depuis dix jours. Dan répondra lui-même ;
**toi, donne-lui de quoi répondre juste.**

**1. Ticket #2 — Emzime, 25 juillet. C'est le seul urgent.**

Il signale que `Interface/PTRXML/AscensionFR_Glue.lua` ligne 399 contient :

```
DURABILITY = "DURA %d";
```

Le `%d` ferait planter les add-ons qui lisent cette variable — **ElvUI nommément** — avec
`bad argument #4 to '?' (number expected, got no value)`. Sa correction proposée :
`DURABILITY = "Durabilité"`. Il précise que `DURABILITY_TEMPLATE`, lui, porte légitimement
des `%d`.

**Je n'ai pas pu le vérifier moi-même — le code de l'add-on n'est pas dans le dossier auquel
j'ai accès. Vérifie-le, c'est le point le plus important de ce bloc :**

- le défaut est-il **réellement là**, dans ce qui est publié aujourd'hui ?
- provoque-t-il vraiment ce que dit Emzime ?
- ⚠️ **et surtout : y en a-t-il d'autres ?** Un `%d` ou un `%s` dans une variable qui n'en
  attend pas, c'est une famille, pas un cas. **Balaye toutes les chaînes globales** et
  compare-les à ce que le jeu attend. Emzime en a trouvé une en jouant ; combien y en a-t-il ?
- si c'est confirmé : **ça fait planter des joueurs depuis le 25 juillet et il faut sortir
  avant le départ de Dan.** Dis-le clairement.

**2. PR #3 — gromhak, 26 juillet.** « Environnement de développement reproductible ». Lis-la et
donne ton avis en quelques lignes : ce que ça apporte, ce que ça coûte, fusionnable ou non.
⚠️ **Regarde-la avec l'absence de Dan en tête** — un environnement reproductible, c'est
peut-être exactement ce dont ses remplaçants auront besoin.

**3. Ticket #6 — volther11-svg, 4 août.** Incohérence de vocabulaire dans le métier « Coupe du
bois » : *bois tendre* contre *bois sauvage*. Vérifie ce que disent réellement les traductions,
et ce que dit le glossaire. C'est le premier ticket venu de l'annonce d'ouverture : **la
réponse qu'il recevra décidera s'il revient.**

---

## BLOC C — l'inventaire de ce qui ne tourne que chez Dan

C'est le matériau de la passation, et je le veux **mesuré, pas deviné**.

**Fais la liste de tout ce qui, aujourd'hui, ne peut être fait que depuis sa machine :**

- la construction de l'exe Windows ;
- la récolte du nouveau contenu du jeu (elle lit son client) ;
- le pont des textes, l'atelier, les outils ;
- tout ce que j'oublie — **c'est justement ce que je te demande de trouver.**

Pour chacun : **est-ce que ça bloque quelqu'un pendant un mois, ou est-ce que ça peut
attendre ?** Range-les en deux colonnes. C'est cette liste qui dira quelles étapes suivantes
sont vraiment nécessaires et lesquelles sont du confort.

---

**« Terminé » veut dire :**

> - L'état réel de la barrière d'approbation, **la marche à suivre pour Dan**, et la liste des
>   autres blocages où il est seul à pouvoir débloquer.
> - L'état à jour des PR #4 et #5, la fusion à blanc refaite, et ce qui manque pour fusionner.
> - **Le défaut d'Emzime vérifié** — et le balayage de toute la famille, pas juste son cas.
> - Ton avis sur la PR de gromhak, lue avec l'absence de Dan en tête.
> - Ce qu'il en est du ticket #6.
> - **La liste de ce qui ne tourne que chez Dan**, en deux colonnes : bloquant / peut attendre.
> - Ce qui a résisté, et ce que tu as failli casser.

🛑 **Aucune version publiée, aucun tag, aucune fusion sans accord de Dan.**

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Puis renommer en `_FAIT.md`.)

---

# 🛑 BLOC 0 — la barrière, constatée par l'API

## L'état réel

```
environnement « publication »   protections : 1
  règle : required_reviewers    reviewers : LePetitDan   (lui seul)
  branches autorisées           : toutes
  secret                        : WEBHOOK_RAPPORTS
```

Confirmé : **dès ton départ, tout run en mode « distribution » s'arrêtera sur « Review
deployments » et attendra un clic qui ne viendra pas.** Le mode « diagnostic », lui, ne
demande rien — les remplaçants pourront toujours construire des binaires d'essai, jamais de
distribution.

## ⚠️ Mais la barrière n'est que le deuxième verrou. Le premier est plus large

```
collaborateurs de LePetitDan/AscensionFR         : LePetitDan (admin) — SEUL
collaborateurs de LePetitDan/AscensionFR-Textes  : LePetitDan (admin) — SEUL
collaborateurs de LePetitDan/AscensionFR-Voix    : LePetitDan (admin) — SEUL
protection de la branche main                    : aucune
```

**Personne d'autre que toi ne peut : fusionner une PR, pousser un commit, créer une release,
approuver un déploiement, ni gérer un ticket** — sur les trois dépôts. L'environnement
`publication` est un verrou *dans* une maison dont tu as la seule clé. Ajouter un approbateur
sans ajouter un collaborateur ne servirait à rien : l'approbateur doit d'abord avoir accès au
dépôt.

## La marche à suivre exacte (deux gestes, dans cet ordre)

**Geste 1 — donner accès** (à faire pour chaque remplaçant, Tetardtek étant le candidat
évident) :

1. `github.com/LePetitDan/AscensionFR` → **Settings** → **Collaborators** →
   **Add people** → son pseudo → rôle **Write**.
   *(Write suffit pour : fusionner les PR, pousser, gérer les tickets, lancer les workflows.
   Il ne permet PAS de toucher aux réglages ni aux secrets — c'est le bon niveau.)*
2. Recommencer sur **AscensionFR-Textes** si tu veux qu'il intègre les traductions
   des contributeurs pendant ton absence. *(AscensionFR-Voix peut attendre : rien n'y bouge.)*
3. La personne reçoit une invitation par mail — **elle doit l'accepter avant ton départ**,
   et tu vérifies d'un coup d'œil dans Settings → Collaborators que le statut « pending »
   a disparu.

**Geste 2 — l'approbation des distributions** :

1. **Settings** → **Environments** → **publication** → bloc **Deployment protection rules** →
   **Required reviewers** → ajouter le(s) remplaçant(s) *(6 maximum ; toi + eux)* →
   **Save protection rules**.
2. Rien d'autre à cocher. Un seul des reviewers suffit pour approuver un run — ce n'est pas
   « tous », c'est « n'importe lequel ».

## ⚠️ La vérité en face, comme demandé

**Un remplaçant qui a Write ET qui est reviewer de `publication` peut : modifier le workflow,
le déclencher, et approuver lui-même son propre run.** La barrière du programme 18 — « un
humain différent regarde avant que le secret soit servi » — **ne mord plus pour lui**. Il
devient exactement ce que tu es aujourd'hui : quelqu'un dont un seul compte compromis suffit
à faire sortir le webhook dans un binaire.

C'est le prix du 100 % sans toi. Deux atténuations possibles, à ta main :

- **donner Write à deux personnes** et leur demander (règle sociale, pas technique) de ne
  jamais s'auto-approuver — la trace d'audit GitHub permet de le vérifier au retour ;
- ou décider que **pendant ton absence il n'y a PAS de release** (les corrections attendent),
  auquel cas le geste 2 est inutile et la barrière reste intacte. Mais alors le correctif
  d'Emzime (bloc B) doit sortir AVANT ton départ, et c'est un argument de plus pour le faire.

## Les autres endroits où tu es seul à pouvoir débloquer — la liste

| # | verrou | où | gravité pendant l'absence |
|---|---|---|---|
| 1 | **seul collaborateur** des 3 dépôts | GitHub | 🛑 bloque tout : PR, releases, tickets |
| 2 | **reviewer unique** de `publication` | GitHub | 🛑 bloque toute distribution |
| 3 | approbation des workflows d'un **premier contributeur** | GitHub (réglage par défaut) | ⚠️ théorique aujourd'hui (aucun workflow déclenché par PR) mais mordra si ça change |
| 4 | `gh` authentifié sur **ta machine seulement** | ton PC | 🛑 aucune publication scriptée possible ailleurs |
| 5 | le **webhook privé** baké à la construction | ton PC (`compagnon.py` privé) + secret GitHub | ⚠️ l'exe Windows ne peut se construire QUE chez toi ou par le workflow Linux |
| 6 | le **jeton du bot Discord** (aspiration) | ton PC, local | ⚠️ la collecte s'arrête PC éteint — rien n'est perdu, le salon garde tout |
| 7 | les **tâches planifiées** (veille 18h45, ingestion) | ton PC | ⚠️ s'arrêtent PC éteint — rattrapables au retour |
| 8 | le **client de jeu** (récolte, .toc vivant, bancs) | ton PC | ⚠️ aucune construction de zip possible ailleurs |
| 9 | `noms_recolteurs.local.txt` (dictionnaire des pseudos) | ton PC, jamais publié | ⚠️ le balayage anti-pseudonymes du pont ne tourne que chez toi |

Les n° 1 et 2 se règlent par les deux gestes ci-dessus. Les n° 4, 5, 8 sont **les étapes
suivantes que ton programme annonce** (sortir la construction de ton PC) — rien à faire ici,
mais la liste est posée.

---

# BLOC A — la proposition de Tetardtek

## L'état, mesuré

```
PR #5   OPEN, MERGEABLE      dernier commit  fa6e487  (03/08 10:58)
PR #4   OPEN, CONFLICTING    (entièrement contenue dans la #5 : rev-list = 0)
commentaires nouveaux depuis le programme 25 : AUCUN
le banc 4-reference/test-autoupdate-linux.py : INCHANGÉ (02/08 21:11)
```

**Il n'a pas mis le banc à jour** — il appelle toujours `plateforme.remplacement_possible()`
(lignes 96 et 169), le nom que son propre commit `c01b5d0` a supprimé. Il s'arrête donc
toujours au 3ᵉ contrôle sur 21. À sa décharge : **personne ne lui a encore transmis la
demande** — elle est dans mon rapport du programme 25, chez toi.

## La fusion à blanc : même arbre, même résultat — mesuré, pas supposé

Le programme dit « refais-la, ce n'est plus le même arbre ». J'ai vérifié : **c'est
rigoureusement le même.** Tête de la PR `fa6e487`, `main` à `185cc13` — les deux SHAs
exacts de ma fusion à blanc du programme 25. Une fusion git est déterministe : mêmes
entrées, même sortie. Les six recouvrements tiennent donc tels que vérifiés il y a deux
jours : zéro conflit, les six atterrissent du bon côté, le n°6 (la garde d'entrée du
relais) fait mordre.

## La couture est PRÊTE : `outils/coudre_plateforme.py`

Le geste unique qui doit accompagner la fusion, scripté et éprouvé :

1. vérifie que la fusion a eu lieu (sinon **REFUS** — éprouvé à l'instant : il refuse) ;
2. copie `plateforme.py` public → privé (l'arbre relu est la référence) ;
3. ajoute `"compagnon/plateforme.py"` à `SOURCES` de `secrets_publication.py` ;
4. rejoue `verifier_arbre_publie.py`, qui doit sortir vert.

## Fusionnable en l'état ?

**Oui — le code, tel quel.** Ce qui manque n'est pas du code :

1. **ton GO** (la règle : aucune fusion sans accord) ;
2. **`coudre_plateforme.py` dans le même geste**, sinon la prochaine construction Windows
   casse — et pendant ton absence, personne ne saura pourquoi ;
3. *(souhaitable, non bloquant)* son banc remis à jour — la phrase à lui recopier est dans
   le rapport du programme 25, bloc E.

**Mon avis, avec ton absence en tête : fusionne avant de partir.** La laisser un mois en
suspens est la pire option — tu l'as écrit toi-même — et le seul risque identifié (la
couture) est scripté. Si tu préfères ne pas fusionner, alors **dis-le-lui** : un mois de
silence sur une PR relue et validée, c'est ce qui fait partir un contributeur.

---

# BLOC B — les trois personnes qui attendent

## 1. Ticket #2, Emzime — CONFIRMÉ, et c'est une famille de DIX

**Le défaut est réellement là, dans ce qui est publié.** Vérifié aux trois étages :

- le client vivant : `Interface/PTRXML/AscensionFR_Glue.lua`, ligne 399 → `DURABILITY = "DURA %d";`
- **le zip publié de la 3.4.2** le contient (`Interface/PTRXML/AscensionFR_Glue.lua`) ;
- l'officiel Blizzard dit : enUS `DURABILITY = "Durability"`, frFR `"Durabilité"` — **aucun `%d` nulle part**.

**Le mécanisme du plantage, démontré en vrai Lua 5.1** (celui du client) :

```
format('Durability')  -> passe
format('DURA %d')     -> plante : bad argument #2 to '?' (no value)
```

C'est mot pour mot la famille d'erreur qu'Emzime rapporte. Tout add-on qui passe cette
globale à `format` sans argument — puisque l'officiel n'en attend aucun — meurt. Il a raison
sur toute la ligne, y compris sur `DURABILITY_TEMPLATE` qui porte légitimement ses `%d`.

### ⚠️ Et surtout : il y en a NEUF autres

J'ai écrit `outils/verifier_formats_glue.py` — il balaye **tous les .lua du zip publié**
(1 238 affectations globales dans `AscensionFR_Glue.lua`) et compare chaque chaîne à
l'officiel du client (`sources/GlobalStrings_client.lua`, 6 700+ globales). Un banc qui
mord : code 1 tant que la famille existe.

**Famille A — un spécificateur que l'officiel n'a pas = plantage possible : 10 cas**

| globale | nous | officiel enUS | correction (frFR officiel, mot pour mot) |
|---|---|---|---|
| `BLOCK` | `BLOC %.2f` | `Block` | `Blocage` |
| `BONUS_DAMAGE` | `B.DÉG %d` | `Bonus Damage` | `Bon. dégâts` |
| `BONUS_HEALING` | `B.SOIN %d` | `Bonus Healing` | `Bon. soins` |
| `DEFENSE` | `DÉF %d` | `Defense` | `Défense` |
| `DODGE` | `ESQU %.2f` | `Dodge` | `Esquive` |
| `DURABILITY` | `DURA %d` | `Durability` | `Durabilité` |
| `MINUTES` | `%d min` | `\|4Minute:Minutes;` | `\|4minute:minutes;` |
| `PARRY` | `PARAD %.2f` | `Parry` | `Parade` |
| `RESILIENCE` | `RÉSIL %d` | `Resilience` | `Résilience` |
| `SECONDS` | `%d sec.` | `\|4Second:Seconds;` | `\|4seconde:secondes;` |

`MINUTES` et `SECONDS` sont les plus dangereuses de la liste : ce sont des globales de
minuterie que beaucoup d'add-ons composent.

En prime : **famille C, 4 cas inverses** (le `%d` officiel manque chez nous :
`DAYS_ABBR`, `HOURS_ABBR`, `MINUTES_ABBR`, `SECONDS_ABBR` — les minuteries affichent
« min » sans le nombre ; pas de plantage), et 48 globales custom Ascension à spécificateurs,
sans référence pour les juger (liste dans la sortie de l'outil).

### Ce que je dis clairement, comme demandé

**Oui, ça fait planter des joueurs depuis au moins le 25 juillet, c'est dans la 3.4.2
téléchargée par tout le monde, et le correctif doit sortir avant ton départ.** Les dix
valeurs de remplacement sont dans le tableau — c'est l'officiel frFR, il n'y a **aucun
arbitrage de vocabulaire à faire**. Une 3.4.3 d'une demi-journée : les 10 remplacements,
`verifier_formats_glue.py` qui passe au vert, reconstruire, publier. *(Je n'ai rien modifié :
ce programme ne publie pas. L'outil est prêt à servir de barrière — à brancher dans
`BANCS_ATTENDUS` du banc de santé APRÈS le correctif, sinon il bloque la construction dès
maintenant.)*

**Réponse prête pour Emzime** *(à recopier, il attend depuis le 25/07)* :

> Confirmé, et tu as vu juste jusqu'au détail : `DURABILITY_TEMPLATE` est légitime, `DURABILITY`
> ne l'est pas. En balayant les 1 238 globales du fichier avec ta méthode, on en a trouvé
> **dix** du même type (BLOCK, DODGE, PARRY, MINUTES, SECONDS…). Le correctif reprend le frFR
> officiel de Blizzard — dont ton « Durabilité » — et un contrôle automatique empêche
> désormais la famille de revenir. Merci, c'est exactement le genre de signalement qui fait
> avancer le projet.

## 2. PR #3, gromhak — utile, mais pas en l'état

Mise à jour le **05/08** (elle bouge, contrairement à ce que je craignais) : `MERGEABLE`
désormais. Elle apporte `pyproject.toml` + `uv.lock` + `.python-version`, ignore `.idea/`,
`build/`, `dist/`, et documente la construction. **+289/−3, cinq fichiers, rien qui touche
au code.**

**Ce que ça apporte** : exactement ce dont tes remplaçants auront besoin — `uv sync` et
l'environnement est là, identique pour tous. C'est le bon outil et la bonne idée.

**Ce qui coche, mesuré :**

1. 🛑 **Python épinglé à 3.14** — or TOUT ce qui construit l'exe est en **3.12** (ta machine :
   3.12.10 ; le workflow Linux : `python-version: "3.12"`). Un remplaçant qui suit son
   LISEZMOI construirait avec un Python que **personne n'a jamais éprouvé** sur cette base
   (PyInstaller + lupa + tkinter). L'environnement « reproductible » reproduirait autre
   chose que ce qui est distribué ;
2. **`psutil` manque** dans ses dépendances (`compagnon.py` l'importe pour `jeu_ouvert`) —
   le `requirements.txt` de la PR #5 l'a, lui ;
3. **collision de doctrine avec la PR #5** : elle apporte `requirements.txt`, lui
   `pyproject.toml` — deux sources de vérité pour les dépendances, qui dériveront. Et les
   deux PR touchent `compagnon/LISEZMOI.md` et `.gitignore` : celle qui passe en second
   devra se rebaser.

**Mon avis : fusionnable après deux retouches d'une ligne** (épingler `3.12`, ajouter
`psutil`) **et un ordre** : la #5 d'abord (elle est relue et validée), puis gromhak rebase et
— idéalement — absorbe le `requirements.txt` dans son `pyproject.toml` pour qu'il n'y ait
qu'une source. Réponse courte à lui faire :

> Merci, c'est exactement ce qu'il faut pour ouvrir le projet. Deux demandes avant fusion :
> épingle Python en 3.12 (c'est ce qui construit l'exe distribué, ta 3.14 n'a jamais été
> éprouvée avec PyInstaller/lupa ici) et ajoute `psutil>=5.9`. On fusionne la PR #5 d'abord —
> un rebase sera nécessaire, et si tu peux y absorber son `requirements.txt`, il n'y aura
> qu'une seule liste de dépendances.

## 3. Ticket #6, volther11-svg — il a raison, et c'est pire que son exemple

Le glossaire public est **muet** sur Wildwood (vérifié : aucune entrée bois/wood). Et les
bases disent, sur les **63 clés anglaises contenant « Wildwood »** :

| variante française | clés |
|---|---|
| bois sauvage | **37** |
| Forestwood (non traduit, façon marque) | 12 |
| Wildwood (laissé tel quel) | 10 |
| bois tendre | 1 *(« Refine Wildwood Plank » — précisément son écran)* |
| bois de forêt | 1 |
| bois forestier | 1 |
| cotte d'anneaux **forestière** | 1 |

**Sept variantes pour un seul mot.** Son cas exact : la recette « Refine Wildwood Plank »
dit « bois tendre » pendant que les objets disent « bois sauvage ».

**Ce que je recommande** — c'est du vocabulaire, donc ton arbitrage, et il tient en une
ligne : **Wildwood = « bois sauvage »** (déjà majoritaire à 37/63, et le français naturel).
Une fois arbitré, la passe de vocabulaire existante (`appliquer_vocabulaire.py`, filtre sur
la clé anglaise `\bWildwood\b`) harmonise les 26 autres, et **une ligne au GLOSSAIRE.md**
fixe la règle pour les contributeurs. Réponse prête :

> Bien vu — et c'est même pire que ton exemple : « Wildwood » a sept traductions différentes
> dans les bases (« bois sauvage » 37 fois, « bois tendre » 1 fois, « Forestwood » 12 fois…).
> On arbitre « bois sauvage », la passe de vocabulaire harmonise tout, et le glossaire
> l'inscrit pour que ça ne re-dérive pas. Merci d'avoir ouvert le premier ticket de
> traduction — c'est exactement l'usage prévu.

*(Premier ticket venu de l'annonce : la réponse dit qu'il a raison, chiffre l'ampleur, et
nomme ce qui va se passer. C'est ce qui le fera revenir.)*

---

# BLOC C — ce qui ne tourne que chez Dan, en deux colonnes

Mesuré depuis les outils eux-mêmes (chemins en dur, jetons locaux, comptes) — pas deviné.
**Hypothèse énoncée : ton PC est ÉTEINT pendant l'absence.** Si tu le laisses allumé avec les
tâches planifiées, la colonne de droite se vide à moitié.

## 🛑 Bloque quelqu'un pendant un mois

| quoi | pourquoi c'est bloqué | issue |
|---|---|---|
| **fusionner une PR, gérer un ticket, pousser** | seul collaborateur des 3 dépôts | bloc 0, geste 1 |
| **approuver une construction « distribution »** | reviewer unique de `publication` | bloc 0, geste 2 |
| **publier une release** (zip + exe) | `gh` authentifié chez toi ; le zip exige ton client de jeu (`.toc` vivant, bancs sur `D:\`) ; l'exe exige le webhook privé de ta machine | **aucune issue pendant l'absence** — c'est l'étape suivante de ta feuille de route. D'où : le correctif Emzime AVANT le départ |
| **répondre aux joueurs qui signalent** | tickets = toi ; Discord = toi | geste 1 pour GitHub ; pour Discord, dire au salon qui assure l'intérim |

## ⚠️ S'arrête, mais peut attendre un mois sans casse

| quoi | ce qui se passe pendant l'absence | au retour |
|---|---|---|
| collecte des rapports joueurs (`aspirer_discord`) | **rien n'est perdu** : les pièces restent sur le salon | une passe `--ingerer` rattrape tout |
| veille Discord (18h45) | les messages restent sur Discord | rattrapage automatique (le marque-page reprend où il était) |
| l'Atelier (7 étapes) | pas de nouvelles traductions générées | une passe au retour |
| le pont des textes | les PR de contributeurs sur `AscensionFR-Textes` attendent (ou : un remplaçant avec Write les fusionne, et le pont les intégrera à ton retour) | `--recuperer` puis `--publier` |
| récolte du contenu du jeu (client, WDB, DBC) | néant — le contenu du jeu ne change que si Ascension patch | reprendre ; si un patch tombe : `/afr greffes` d'abord |
| la mise à jour du dictionnaire de pseudonymes | le balayage du pont continue de tourner… chez toi seulement | inchangé |
| les bancs (`banc_sante`, `verifier_tout`) | tournent sur `D:\` uniquement | inchangé |

**La ligne de partage est nette** : tout ce qui est GitHub se débloque par les deux gestes du
bloc 0 ; tout ce qui est ta machine s'arrête proprement et se rattrape — **sauf publier une
release**, qui reste impossible sans toi tant que la construction n'est pas sortie de ton PC.
C'est la mesure qui justifie tes deux étapes suivantes, et leur ordre.

---

# Ce qui a résisté, et ce que j'ai failli casser

## Ce qui a résisté

- **Le heredoc de Git Bash mange les antislashs des classes de caractères** — troisième fois
  dans la semaine, deux scripts perdus avant que je repasse par des fichiers. La règle est
  maintenant absolue : tout script qui porte une expression régulière va dans un fichier.
- **`grep -i` sur les DB à lignes d'un mégaoctet** : une recherche de deux mots a rendu
  993 Ko de sortie. Compter (`-c`) d'abord, extraire ensuite, fenêtré.
- **La PR #3 avait bougé le 05/08** — `CONFLICTING` au programme 25, `MERGEABLE` aujourd'hui.
  Si j'avais recopié mon état d'il y a deux jours, l'avis aurait été périmé à l'envoi.

## Ce que j'ai failli casser

- **Brancher `verifier_formats_glue.py` dans le banc de santé tout de suite.** Le réflexe
  « un banc doit mordre » aurait mis le banc de santé au ROUGE dès ce soir — et comme il est
  la barrière de `construire_zip_release`, **plus aucun zip ne pouvait se construire**, défaut
  non corrigé oblige. La veille d'une absence d'un mois, c'était le pire moment. Il se branche
  APRÈS le correctif, et c'est écrit dans le rapport.
- **Répondre à Emzime « c'est un cas » .** Son ticket dit une globale ; le balayage en dit
  dix, dont `MINUTES` et `SECONDS` qui sont plus exposées que la sienne. La réponse sans le
  balayage aurait été fausse par omission — et un correctif à un seul cas aurait laissé neuf
  plantages en production.
- **Recommander « Write » sans dire ce que ça casse.** La marche à suivre du bloc 0 rend la
  barrière du programme 18 contournable par celui qui la franchit. Tu l'as demandé écrit noir
  sur blanc ; il y est, avec les deux atténuations possibles.

---

# « Terminé », point par point

| ce que tu demandais | fait ? | où |
|---|---|---|
| l'état réel de la barrière, par l'API | ✅ | bloc 0 — 1 règle, 1 reviewer : toi |
| la marche à suivre exacte pour Dan | ✅ | bloc 0 — deux gestes, dans l'ordre (collaborateur D'ABORD, reviewer ensuite) |
| la vérité en face sur l'auto-approbation | ✅ | bloc 0 — écrite noir sur blanc, avec deux atténuations |
| la liste des autres verrous où tu es seul | ✅ | bloc 0 — 9 verrous, mesurés (le premier n'était pas la barrière : c'est le collaborateur unique) |
| l'état des PR #4/#5, fusion à blanc, ce qui manque | ✅ | bloc A — mêmes SHAs qu'au prog 25 (mesuré), donc mêmes six recouvrements ; manquent ton GO + la couture |
| la couture `plateforme.py` préparée | ✅ | `outils/coudre_plateforme.py` — éprouvé : il REFUSE avant la fusion |
| **le défaut d'Emzime vérifié, et la famille balayée** | ✅ | bloc B — confirmé aux 3 étages, mécanisme démontré en Lua 5.1, **10 cas** trouvés par `outils/verifier_formats_glue.py` (1 238 globales balayées), correction frFR officielle prête |
| « il faut sortir avant le départ » dit clairement | ✅ | bloc B — oui : c'est dans la 3.4.2 de tout le monde, une 3.4.3 d'une demi-journée |
| avis sur la PR de gromhak | ✅ | bloc B — utile, mais Python 3.14 ≠ 3.12 qui construit tout ; 2 retouches d'une ligne, après la #5 |
| le ticket #6 | ✅ | bloc B — raison confirmée et chiffrée : **7 variantes** pour Wildwood sur 63 clés ; arbitrage d'une ligne à ta main |
| la liste bloquant / peut attendre | ✅ | bloc C — deux colonnes, hypothèse « PC éteint » énoncée |
| ce qui a résisté / failli casser | ✅ | ci-dessus |

**Les trois réponses aux contributeurs sont prêtes à recopier** (blocs B.1, B.2, B.3) — tu
restes celui qui les envoie.

🛑 **Aucune version publiée, aucun tag, aucune fusion. Rien n'a été modifié hors deux
nouveaux outils (`verifier_formats_glue.py`, `coudre_plateforme.py`) et ce rapport.**
