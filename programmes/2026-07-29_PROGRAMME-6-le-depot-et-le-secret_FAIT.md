# Demande de code → Claude Code

# 🛑 PROGRAMME 6 — un secret vivant sur le chemin de la publication

**Date :** 2026-07-29 · fait suite au programme 5.

> **Le programme 5 est du très bon travail, et il faut le dire avant le reste.**
>
> Tu as prouvé la propriété additive en rejouant **une seule réponse de Google dans les deux
> versions du module** — parce que Google n'est pas déterministe et qu'une double interrogation
> aurait fabriqué exactement les faux rouges qu'on traque. C'est de la méthode, pas de la
> mesure : tu as conçu l'instrument avant de mesurer.
>
> Tu as rendu la déconsignation **automatique** au lieu de la faire à la main. « Un conseil à
> mémoriser est un conseil perdu » — c'est la bonne façon de penser, et elle vaut bien au-delà
> de ce cas.
>
> Tu as mesuré, montré, puis **écarté** la ressemblance au caractère près, alors qu'elle
> rattrapait tes deux derniers cas. Une piste séduisante tuée par la mesure.
>
> Et tu t'es contredit trois fois, en le disant : les 65 artefacts qui n'en étaient que 8, les
> 69 % qui font 57 %, et surtout **le chemin de retour qui inventait 4 298 entrées** alors que
> ses compteurs étaient parfaitement symétriques. Cette troisième erreur justifie à elle seule
> qu'on ait exigé le retour *éprouvé* et pas seulement écrit — et tu l'as vue parce que tu as
> comparé des empreintes au lieu de croire des compteurs.
>
> **Blocs A, B, C, D : acceptés.** Rien à reprendre.

---

## 🛑 BLOC E — ne lance pas la séquence. Elle publierait un secret.

**Ton plan est juste sur le fond et je le suivrai. Mais son geste n° 1, exécuté tel qu'il est
écrit, rend public un identifiant vivant.**

### Ce que j'ai trouvé

`compagnon/compagnon.py`, ligne 71, dans l'arbre **privé** :

```python
WEBHOOK_RAPPORTS = "<l'URL du webhook des rapports — retiree de cette archive>"
```

Et dans l'arbre **publié**, aujourd'hui :

```python
WEBHOOK_RAPPORTS = ""      # ← le secret n'est PAS public. Vérifié sur GitHub.
```

Ton geste n° 1 dit : *« synchroniser `compagnon.py`, `interface_hub.py`,
`fabriquer_decor_hub.py` du privé vers `depot_github/` »*. Une copie fidèle **écrase le `""` par
le webhook**. Geste n° 4, `git push`, et il est public.

**Ce que ça coûte concrètement** : une URL de webhook Discord *est* le droit d'écrire dans le
salon. Il n'y a ni compte, ni mot de passe, ni révocation partielle — qui a l'URL poste ce qu'il
veut, autant qu'il veut, sous l'apparence du webhook. Les dépôts publics sont balayés en
permanence par des robots qui cherchent précisément ce motif. La question n'est pas *si* le
salon des rapports serait inondé, mais quand.

### Pourquoi aucun de nos garde-fous ne l'aurait vu

C'est la partie qui devrait t'intéresser le plus, parce qu'elle dit quelque chose sur notre
manière de poser des barrières.

| garde-fou | pourquoi il est aveugle ici |
|---|---|
| `construire_zip_release.py` | cherche bien `discord.com/api/webhooks`… mais **seulement dans les `.lua/.toc/.txt/.md/.xml`** — il passe explicitement les `.py` |
| `verifier_hub.py` | vérifie que le **relevé de diagnostic** ne contient pas le webhook. Rien sur les sources |
| `verifier_arbre_publie.py` **(le tien, d'hier)** | **aucun contrôle de secret** — et pire, voir ci-dessous |

**Le tien a un défaut de conception, pas un oubli.** Il exige que l'arbre publié soit
**identique** à l'arbre privé. Or l'arbre publié doit être *délibérément différent* sur cette
ligne. Les deux exigences sont incompatibles :

- si on synchronise fidèlement → il sort **✅** et le secret part ;
- si on neutralise le webhook dans la copie publique → il sort **⚠ DIVERGE** pour toujours, et
  devient un **faux rouge permanent** — la maladie qu'on soigne depuis une semaine.

Un garde-fou qui ne peut être vert qu'au prix d'une fuite est pire qu'absent : il donne raison
au geste dangereux.

---

## Ce qu'il faut poser avant de toucher au dépôt

### 1. La notion de **différence déclarée**

`verifier_arbre_publie.py` doit comparer *modulo une liste explicite de secrets injectés*. Un
fichier déclaratif, par exemple `outils/secrets_injectes.json` :

```json
{
  "compagnon/compagnon.py": {
    "WEBHOOK_RAPPORTS": {
      "valeur_publique_attendue": "",
      "pourquoi": "URL du salon des rapports — vaut droit d'écriture, jamais publiée"
    }
  }
}
```

Et le garde-fou devient **bilatéral** :

- l'arbre publié doit être identique au privé **partout sauf** sur les entrées déclarées ;
- sur chaque entrée déclarée, la valeur publique doit être **exactement** la valeur neutre
  attendue — pas « différente », **égale au `""`**. Une valeur inattendue est un refus ;
- une divergence **non déclarée**, où que ce soit, reste un refus, comme aujourd'hui.

Ainsi le vert redevient atteignable et honnête.

### 2. Le filet qui ne dépend pas de la liste

La déclaration ci-dessus suppose qu'on ait **pensé** à déclarer le bon secret. C'est exactement
l'hypothèse qui a lâché aujourd'hui. Ajoute donc un contrôle **indépendant** :

> **aucun fichier de l'arbre publié, quelle que soit son extension, ne doit contenir de motif de
> secret** — URL de webhook Discord, `ghp_…`, `github_pat_…`, `AIza…`, `xox…`, chaîne façon
> jeton. Un seul motif trouvé = refus de taguer, sans dérogation.

Ce contrôle-là attrape le secret que personne n'a déclaré. C'est le seul qui protège contre
notre propre inattention future. **Étends-le aussi à `construire_zip_release.py`**, qui ne
regarde aujourd'hui que cinq extensions et laisserait passer un `.py`.

### 3. La synchronisation devient un **outil**, pas un copier-coller

Le geste n° 1 ne doit pas être « copier les trois fichiers ». Il doit être un script qui copie
**et applique la neutralisation** depuis le fichier déclaratif, de façon reproductible. Un
humain qui recopie à la main réintroduira le webhook au prochain passage — et cette fois sans
que personne regarde.

### 4. Vérifie s'il y a d'autres secrets que celui-là

J'ai balayé les `.py/.json/.md/.toc/.lua/.spec` du dépôt et je n'ai trouvé que ce webhook. Mais
je n'ai pas ouvert `depot_github/` fichier par fichier, ni regardé l'historique git. **Avant de
pousser : refais le balayage sur l'intégralité de ce qui partira**, y compris ce qui est déjà
commité, et dis-moi ce que tu trouves.

---

## Une question à part, à ne pas confondre avec celle-ci

Le webhook est **déjà dans l'exe distribué** — quiconque passe un `strings` sur le binaire de
37,9 Mo peut l'extraire. Ce n'est donc pas un secret parfait aujourd'hui.

**Mais ce n'est pas une raison de le publier.** Extraire une chaîne d'un binaire est un geste
volontaire ; un dépôt public est indexé, balayé, archivé, sans que personne s'y intéresse.
L'écart entre les deux est celui qui sépare « quelqu'un pourrait » de « quelqu'un le fera cette
semaine ».

Cela dit, ça pose une vraie question de fond que je te laisse trancher, plus tard et à froid :
**vaut-il mieux un webhook en dur dans l'exe, ou un envoi de rapport qui passe par autre chose ?**
Ne traite pas ça maintenant. Dis-moi seulement, en une ligne, si tu vois une solution simple.

---

## Ce qui ne change pas dans ton plan

Le reste tient, et j'y ai regardé :

- **le déplacement de tag est sûr** — le Hub interroge `releases/latest`, aucune URL de tag n'est
  figée chez le joueur ; les assets sont attachés à la release, pas au commit ;
- **ne jamais supprimer le tag** — ta démonstration (release repassée en brouillon → 404 sur les
  deux assets → `latest` retombe sur `v3.3.1` → chaque Hub propose une mise à jour *vers
  l'arrière*) est le genre de conséquence qu'on ne découvre pas en la vivant. Bien vu ;
- **la répétition à blanc sur `v0.0.0-essai`** : oui, fais-la. Trente secondes contre un risque
  sur la release que les joueurs utilisent ;
- **laisser `3.3.0` et `3.3.1`** : d'accord, et pour ta raison — fabriquer un arbre qui n'a jamais
  existé serait mentir dans l'historique. Ajoute la ligne d'honnêteté au corps des deux releases ;
- **le commit des 4 fichiers ne suffit pas** : d'accord aussi. ~5 200 lignes de sources du Hub
  n'ont jamais été publiées. J'ai vérifié de mon côté : le `compagnon.py` public fait 1 272
  lignes contre 2 234 en privé, et annonce encore `VERSION_COMPAGNON = "3.1.0"`.

---

**« Terminé » veut dire :**

> - `verifier_arbre_publie.py` sait faire la **différence déclarée**, et exige la valeur neutre
>   exacte — pas seulement « différent ».
> - Le **balayage de secrets** existe, indépendant de toute liste, bloquant, et couvre **toutes**
>   les extensions — dans le garde-fou de publication **et** dans `construire_zip_release.py`.
> - La synchronisation privé → publié est un **outil reproductible** qui neutralise tout seul.
> - Le balayage complet de ce qui partira a été fait, et tu me dis ce qu'il a trouvé.
> - Les deux garde-fous tournent sur l'état réel et me montrent leur sortie.

🛑 **Toujours rien de commité, rien de tagué, rien de poussé.** Montre-moi les garde-fous verts
sur un arbre préparé — Dan donnera le go sur la séquence complète ensuite.

---
## Réponse de Claude Code
> (au fil de l'eau. Puis renommer en `_FAIT.md`.)

---

### Tu as raison, et la séquence n'a pas été lancée

**Rien n'est commité, tagué ni poussé.** J'ai vérifié ton constat par lecture directe avant de
toucher à quoi que ce soit, puis j'ai posé les quatre pièces que tu demandes. Le balayage complet
a trouvé **un second secret vivant** dont tu ne parlais pas — voir plus bas.

#### La vérification de ton constat

| | |
|---|---|
| `compagnon/compagnon.py:71` (privé) | webhook Discord vivant, **confirmé** |
| `depot_github/compagnon/compagnon.py:67` (publié) | `WEBHOOK_RAPPORTS = ""`, **confirmé** |
| `construire_zip_release.py:277` | `if not n.endswith((".lua",".toc",".txt",".md",".xml")): continue` — **saute bien les `.py`** |
| `verifier_hub.py:159` | ne regarde que le **relevé** de diagnostic, **confirmé** |
| `verifier_arbre_publie.py` (le mien) | aucun contrôle de secret, et le conflit de conception que tu décris, **confirmé** |

Un détail que j'ai relevé en passant et qui en dit long : la ligne publique porte son commentaire
**en double** —

```python
WEBHOOK_RAPPORTS = ""    # renseigné uniquement dans l'exe distribué    # renseigné uniquement dans l'exe distribué
```

C'est la trace d'une neutralisation faite à la main, une fois, par une substitution approximative.
Exactement ce que ton point 3 veut supprimer.

*(Une correction sans importance pour la décision : le `compagnon.py` public fait **1 409** lignes,
pas 1 272. L'écart avec les 2 234 du privé reste entier.)*

---

### 1. La différence déclarée

`outils/secrets_injectes.json` déclare, par fichier, quelles affectations doivent être neutralisées
et **par quelle valeur exacte**.

Mais je ne l'ai pas branchée comme trois règles séparées. Le garde-fou ne compare plus
« privé == publié » ; il compare **« privé NEUTRALISÉ == publié »**. Cette seule comparaison porte
tes trois exigences à la fois :

- identité partout où rien n'est déclaré ✓
- sur une entrée déclarée, la valeur publique doit être **égale** à la valeur neutre — pas
  « différente du secret ». « REDACTED », « à remplir » ou un webhook de test sont tous différents
  du secret et tous refusés ✓
- toute divergence non déclarée, où que ce soit, reste un refus ✓

Et un contrôle explicite double la comparaison pour **dire lequel des trois** a lâché : « diverge »
n'aide personne, « `WEBHOOK_RAPPORTS` vaut une valeur inattendue de 34 caractères, on exige `""` »
si.

⚠️ **La même fonction `neutraliser()` sert au garde-fou et à l'outil de synchronisation.** Deux
implémentations dériveraient, et le jour de la dérive le garde-fou validerait un arbre que l'outil
ne sait plus produire.

### 2. Le filet qui ne dépend d'aucune liste

`outils/balayer_secrets.py` + `outils/secrets_publication.py` : **21 familles de motifs**
(webhook Discord sous ses deux formes, jeton de bot, GitHub classique et à portée fine, Google,
Slack, AWS, Stripe, clés de modèles, clé privée, URL à identifiants, webhooks Slack/Teams/Google
Chat, SendGrid, npm, PyPI, Telegram, Sentry, JWT) **plus une heuristique d'entropie** pour les
formes qu'on ne connaît pas. **Toutes extensions.** Bloquant, sans dérogation.
*(11 familles au premier jet — les 10 autres viennent de la relecture adversariale, plus bas.)*

**Le seuil d'entropie est mesuré, pas décrété.** Mon premier jet était à 3,6 bits — et **le banc
l'a pris en faute** : `AscensionFR_Compagnon` (3,69) et `docs/CONTRIBUER.md` (3,95) déclenchaient
l'alerte. J'ai donc mesuré la séparation réelle sur un corpus de valeurs du projet et de jetons de
chaque famille :

```
valeur de configuration la plus désordonnée : 4,09   (« https://buymeacoffee.com/lepetitdan »)
jeton le plus ordonné                       : 4,62   (une clé Stripe)
```

Seuil posé à **4,3**, dans l'écart, avec marge des deux côtés — plus une condition structurelle
(mélange de casses et de chiffres, ou 32 caractères). Effet secondaire heureux : l'hexadécimal est
plafonné à 4,0 bits par construction, donc **nos empreintes djb2 et MD5, dont les rapports sont
pleins, ne peuvent pas déclencher de fausse alerte.**

Un garde-fou bloquant qui crie au loup finit désactivé — on aurait remplacé une fuite par un faux
rouge permanent, la maladie qu'on soigne depuis une semaine.

**Étendu à `construire_zip_release.py`** comme demandé : le balayage s'applique désormais avant le
filtre des cinq extensions, donc à tout membre lisible du zip. Vérifié : `lisible("a.py") = True`,
et un `.py` empoisonné est vu.

**Le secret n'est jamais rendu en clair** dans les relevés — ils finissent dans des rapports et des
journaux qui, eux, se partagent. `https://disc…B5 (121 car.)` : assez pour reconnaître, pas assez
pour s'en servir.

### 3. La synchronisation est un outil

`outils/synchroniser_depot_public.py`. Il copie **et neutralise** depuis le fichier déclaratif.
Trois refus, dont le troisième est le vrai :

1. une déclaration qui vise un nom absent du privé (périmée ou renommée) → refus, jamais un silence ;
2. rien à faire → ce n'est pas un échec, il le dit et sort en 0 ;
3. **après écriture, l'arbre public est balayé ; au moindre motif, tout est remis en place et
   l'outil refuse.**

Le troisième compte parce que sans lui, l'outil ne ferait que déplacer la confiance de l'humain
vers un fichier JSON.

**Et je l'ai éprouvé plutôt que déclaré.** J'ai retiré la déclaration et lancé la synchronisation
pour de vrai :

```
   écrit : compagnon/compagnon.py
   écrit : compagnon/interface_hub.py
   écrit : compagnon/fabriquer_decor_hub.py
--- balayage de l'arbre public après écriture ---
🛑 2 MOTIF(S) DE SECRET dans l'arbre public :
   compagnon/compagnon.py:71 — webhook Discord : https://disc…B5 (121 car.)
TOUT A ÉTÉ REMIS EN PLACE. Le dépôt public n'a pas bougé.
```

Empreintes avant / après le refus, sur les trois fichiers : **identiques**
(`3c58caa9…`, `4134c96d…`, `d35b1401…`). Le balayage de l'arbre juste après : **0 motif**. Le
secret n'est pas resté sur le disque.

C'est la leçon du programme 5 appliquée à un autre outil : les compteurs symétriques rassurent,
seule l'empreinte dit la vérité.

### 4. Le banc — parce qu'un garde-fou qu'on n'a pas vu refuser est une intention

`outils/banc_secrets.py`, **24 épreuves, toutes passées.** Il fabrique les situations dangereuses
au lieu d'espérer.

```
  ok      le webhook est vu dans un .py (l'extension que le zip sautait)
  ok      le webhook est vu dans un .json, un .md, un .yml, un sans-extension
  ok      le webhook est vu même coupé de son https://
  ok      les jetons GitHub / Google / Slack / AWS / Stripe sont vus
  ok      une clé privée en bloc est vue
  ok      une URL à identifiants est vue
  ok      le secret n'est JAMAIS rendu en clair dans le relevé
  ok      PAS de fausse alerte sur des valeurs de configuration ordinaires
  ok      l'entropie sépare bien un jeton d'une valeur de configuration
  ok      la neutralisation remplace la valeur et PRÉSERVE le commentaire
  ok      un nom déclaré mais absent du privé est SIGNALÉ, pas ignoré
  ok      🛑 une valeur publique DIFFÉRENTE mais pas neutre est refusée
  ok      une divergence AILLEURS reste un refus (privé neutralisé ≠ public)
  ok      le privé neutralisé est EXACTEMENT ce qu'on attend du public
  ok      un secret RETIRÉ de l'arbre reste vu dans l'historique git
  … + les 9 épreuves nées de la relecture adversariale (ci-dessous)
```

**Les deux garde-fous sont entrés au banc de santé quotidien** (`banc_secrets.py` et
`balayer_secrets.py`, code 0 attendu). Un garde-fou que personne ne lance n'est pas un garde-fou.

---

### ⚠️ Ce que la relecture adversariale a trouvé — et je dois corriger ce que je m'apprêtais à écrire

J'ai fait attaquer ces garde-fous par une relecture indépendante avant de te les livrer. **Elle a
trouvé des trous réels, prouvés à l'exécution.** J'allais te présenter le balayage comme un filet
solide ; il ne l'était pas.

#### Le pire, et c'est le même piège que le projet connaît déjà

```
  token                -> VU
  DISCORD_TOKEN        -> >>> RATÉ <<<
  SMTP_PASSWORD        -> >>> RATÉ <<<
  ANTHROPIC_API_KEY    -> >>> RATÉ <<<
  CLIENT_SECRET        -> >>> RATÉ <<<
```

Mon gabarit commençait par `\b(secret|token|…)`, ce qui exige que le mot-clé **ouvre** le nom.
Dans `DISCORD_TOKEN`, le souligné qui précède `TOKEN` est un caractère de mot : **`\b` n'y voit
aucune frontière.** Or `NOM_TYPE` est justement la convention dominante des constantes Python.

**C'est exactement le piège des codes couleur collés** — `|cFFB5FFFF` + `Starcaller`, où `\b`
ratait déjà en silence sur 191 entrées. Le même piège, la même semaine, dans un fichier dont le
rôle est de protéger contre l'inattention. Il est noté dans nos propres mémoires et je l'ai refait.

La démonstration de bout en bout était sans appel : un arbre portant trois secrets réalistes
(`ANTHROPIC_API_KEY`, `SMTP_PASSWORD`, `DB_PASSWORD`) sortait **code 0 — feu vert de publication**.
La seule différence avec un arbre refusé : l'ordre des mots dans le nom de la variable.

#### Le second, aussi grave

La valeur devait être **entre guillemets et collée au séparateur**. Passaient donc au travers :
`.env`, YAML, `.ini`, `.netrc`, une ligne de commande, un en-tête `Authorization` — **et la paire
JSON `{"jeton": "…"}`**, parce que le guillemet fermant de la clé s'intercale entre le mot-clé et
le `:`.

Ce dernier point pique : **ce dépôt range précisément son jeton de bot dans un JSON à clé
« jeton »**. Il n'était vu que par un motif nommé, jamais par le filet générique. Et mon épreuve
« le webhook est vu dans un `.json` » passait — parce qu'elle testait une valeur *qui a un motif*.
**Elle donnait au filet une confiance qu'il n'avait pas gagnée.**

#### Corrigé, et repayé en mesure

| trou confirmé | correctif |
|---|---|
| mot-clé devant ouvrir le nom | préfixe explicite, plus de `\b` |
| valeur devant être quotée et collée | séparateur `:`/`=`/espace, guillemets optionnels |
| clés de modèles `sk-ant-` / `sk-proj-` | motif propre (le motif Stripe emploie le souligné, elles le tiret) |
| 3 en-têtes de clé privée sur 5 | motif élargi (`PRIVATE KEY`, `ENCRYPTED`, `… BLOCK`) |
| URL à mot de passe sans nom d'utilisateur | nom d'utilisateur rendu facultatif |
| Slack app, SendGrid, npm, PyPI, Telegram, Sentry, JWT, webhooks Slack/Teams | 8 motifs ajoutés (**11 → 21 familles**) |
| `NOM = """secret"""` → neutralisation **silencieuse**, annoncée « 1 secret neutralisé » | on vérifie le **résultat**, plus les tentatives |
| concaténation implicite, seconde affectation du même nom | idem — toute ligne non conforme = refus |
| exclusion du balayage par **nom de base**, à n'importe quelle profondeur | comparaison sur le **chemin relatif** |

La correction du gabarit élargit la surface, donc **elle devait être payée en taux de fausse
alerte mesuré, pas décrété.** Re-mesure sur les arbres réels :

```
depot_github  : plus haute forme suspecte 3,58 bits
compagnon     : 3,97 · 3,92 · 3,58 · 3,08 …   et le VRAI secret à 5,50
outils        : 3,98 bits au plus haut
```

Seuil à **4,3**. Toutes les nouvelles correspondances tombent en dessous ; le seul au-dessus est le
webhook. **Zéro fausse alerte, marge intacte des deux côtés.**

Vérification finale sur un arbre empoisonné des deux façons :

```
arbre EMPOISONNÉ (copie fidèle + DISCORD_TOKEN dans un .md) -> code 1
   compagnon/compagnon.py:71  webhook Discord : https://disc…B5 (121 car.)
   docs/FAQ.md:78             affectation à forte entropie (TOKEN, 5.0 bits) : aZ7qK2mR9tX4…fC
```

**Les neuf trous ont chacun leur épreuve au banc**, pour qu'une régression future les fasse
ressortir au lieu de repasser inaperçus.

Ce qui a été **écarté** après vérification : le retour arrière de la synchronisation (réfuté sur
plusieurs angles), le chemin « rien à faire », le plancher d'entropie face aux secrets courts et
hexadécimaux, la désynchronisation `SOURCES` / déclarations, le fichier privé absent. Chacun a été
attaqué puis réfuté code en main.

---

### Le balayage complet — et ce qu'il a trouvé

Tu demandais l'intégralité de ce qui partira, y compris ce qui est déjà commité et l'historique.

| périmètre | lu | motifs |
|---|---|---|
| `depot_github/` — arbre de travail, **toutes extensions** | 26 fichiers | **0** |
| `depot_github/` — **historique git**, tous objets, tous commits | 102 blobs texte | **0** |
| `AscensionFR_manuel.zip` (celui qui part) | 57 membres texte | **0** |
| `AscensionFR_manuel_3.4.0.zip` | 82 membres | **0** |
| `AscensionFR-Peche.zip` | 4 membres | **0** |
| arbre **privé** (code et config, 277 fichiers) | | **2 secrets réels** |

**Le dépôt public est propre, arbre et historique.** Rien de ce qui est déjà commité ne porte de
secret — c'était la question qui pouvait faire mal, et la réponse est bonne.

#### ⚠️ Le second secret, que ton balayage n'avait pas vu

```
./discord_aspirateur.json:2   jeton de bot Discord : MTUyODAwMDE1…g0 (72 car.)
```

Un **jeton de bot Discord**, qui vaut bien plus qu'un webhook : un webhook n'écrit que dans un
salon, un jeton de bot agit comme le bot, partout où il est invité.

**La bonne nouvelle, vérifiée :** il n'est pas sur le chemin de la publication.

- `.gitignore:11` le couvre explicitement ✓
- non suivi par git, absent de tout l'historique privé ✓
- absent de `depot_github/`, absent de la liste des sources synchronisées ✓
- et si jamais il entrait dans un zip, le balayage étendu le verrait désormais ✓

Il ne demande donc **aucune action**. Je te le signale parce que tu m'as demandé ce que je
trouvais, et parce que ta phrase « je n'ai trouvé que ce webhook » méritait d'être corrigée : la
protection ici ne vient pas de la chance, elle vient d'une ligne de `.gitignore` que quelqu'un a
eu la présence d'esprit d'écrire.

#### ⚠️ Et une chose à savoir sur le dépôt privé

L'historique du dépôt **privé** contient le webhook (`compagnon/compagnon.py`, 2 objets). Il n'a
**aucun distant** — vérifié, `git remote -v` ne rend rien — donc rien ne fuit aujourd'hui. Mais
cela veut dire une règle simple : **ce dépôt-là ne doit jamais recevoir de distant, ni être poussé
nulle part.** Le retirer de l'historique demanderait une réécriture complète ; tant qu'il reste
local, ce n'est pas nécessaire.

---

### Les deux garde-fous sur l'arbre préparé

L'arbre public est préparé : les trois sources synchronisées **et neutralisées**, `VERSION_COMPAGNON`
passé à `3.4.0`, la ligne 71 remise en forme (commentaire **non** dupliqué, cette fois) :

```python
WEBHOOK_RAPPORTS = ""    # renseigné uniquement dans l'exe distribué
```

Sur le dépôt réel, le garde-fou **refuse — et il a raison** :

```
2. les sources ... comparées au privé NEUTRALISÉ
   compagnon/compagnon.py            conforme (1 secret(s) neutralisé(s))
   compagnon/compagnon_hub.py        conforme
   compagnon/interface_hub.py        conforme
   compagnon/fabriquer_decor_hub.py  conforme
   compagnon/AscensionFR_Hub.spec    conforme
3. VERSION_COMPAGNON : privé 3.4.0 | PUBLIÉ 3.4.0 | demandée 3.4.0
4. balayage de secrets (toutes extensions, sans liste) : 0 motif(s)

🛑 REFUS DE TAGUER — 1 point(s) :
   - 6 fichier(s) non commité(s) dans le dépôt public
```

Le seul rouge restant est **« tu n'as pas commité »** — c'est-à-dire précisément ce que tu m'as
interdit de faire. Le contenu, lui, est conforme sur tous les points.

Pour te le montrer **vert** sans rien commiter dans le vrai dépôt, j'ai fait la **répétition à
blanc** : une copie jetable, commitée là-bas, jamais poussée.

```
1. dépôt public propre : rien en attente
2. les cinq sources                          conformes (1 secret neutralisé)
3. VERSION_COMPAGNON  privé 3.4.0 | PUBLIÉ 3.4.0 | demandée 3.4.0
4. balayage de secrets dans l'arbre public   0 motif(s)
5. balayage de l'HISTORIQUE git              110 blob(s) lu(s), 0 motif(s)

✅ l'arbre publié correspond à ce qui a été construit, et ne porte aucun secret.
```

Les deux barrières de publication restent vertes par ailleurs : `verifier_tout.py` (doctrine de
version 3.4.0 OK, 27 bases couvertes) et `banc_sante.py` — **0 rouge, 0 avertissement**.

---

### Ta question sur l'exe, en une ligne

**Oui : faire poster l'exe vers un petit relais (une fonction serverless en offre gratuite) qui
détient le webhook côté serveur — le secret quitte le disque de chaque joueur, devient révocable
sans reconstruire l'exe, et le relais peut limiter le débit.** À froid, plus tard, comme tu dis.

---

### La séquence, corrigée

Le geste n° 1 devient un outil, et un geste n° 0 apparaît :

| | |
|---|---|
| **0.** | `python outils/banc_secrets.py` — les garde-fous mordent |
| **1.** | `python outils/synchroniser_depot_public.py --appliquer` — **jamais à la main** |
| **2.** | `python outils/verifier_arbre_publie.py --version 3.4.0 --avec-historique` → **✅** |
| 3. | commit unique dans `depot_github/` (3 sources + 4 fichiers en attente) |
| 4. | `git push origin main` |
| 5. | répétition à blanc du déplacement de tag sur `v0.0.0-essai`, puis suppression de l'essai |
| 6. | `git push --force origin <sha>:refs/tags/v3.4.0` — **jamais** de suppression de tag |
| 7. | relire la page de release : deux assets, lien « Source code » sur le nouveau commit |
| 8. | ligne d'honnêteté au corps des releases `3.3.0` et `3.3.1` |
| 9. | brancher le garde-fou dans `publier_github.py` |

Les étapes 0 à 2 sont faites et vertes. **Les étapes 3 à 9 attendent ton go.**

---

### Bilan

| ce que « terminé » demandait | état |
|---|---|
| différence déclarée, valeur neutre **exacte** exigée | ✅ une seule comparaison porte les trois règles |
| balayage indépendant, bloquant, **toutes** extensions, dans les deux garde-fous | ✅ 21 familles + entropie, dans `verifier_arbre_publie` **et** `construire_zip_release` |
| synchronisation = **outil reproductible** qui neutralise seul | ✅ + filet après écriture, retour arrière **prouvé par empreinte** |
| balayage complet de ce qui partira, et ce qu'il a trouvé | ✅ dépôt public **propre**, arbre et historique ; **un second secret** trouvé côté privé |
| les deux garde-fous verts sur l'état réel, sortie montrée | ✅ répétition à blanc **✅ code 0**, banc de santé **0 rouge** |
| rien de commité, tagué, poussé | ✅ |

**Trois choses que je dois te dire :**

1. **J'ai refait un piège que le projet connaît déjà.** Le `\b` qui ne voit aucune frontière après
   un souligné — celui des codes couleur collés — a rendu `DISCORD_TOKEN` et `SMTP_PASSWORD`
   invisibles au filet censé nous protéger de notre inattention. Il est écrit noir sur blanc dans
   nos mémoires. Le connaître n'a pas suffi ; c'est la relecture adversariale qui l'a rattrapé.
2. **Une de mes épreuves se validait toute seule.** « Le webhook est vu dans un `.json` » testait
   une valeur qui a un motif nommé — elle ne prouvait rien du filet générique, et lui donnait une
   confiance imméritée. Une épreuve doit tester ce qu'elle prétend tester.
3. **Le second secret n'a pas été trouvé par prudence mais par outil.** `discord_aspirateur.json`
   est protégé par une ligne de `.gitignore`, pas par un contrôle. Aujourd'hui ça suffit ; ça ne
   se remarquerait pas le jour où ça ne suffirait plus.

**Ce qui attend une décision :** le go sur les étapes 3 à 9, et — plus tard, à froid — le relais
pour sortir le webhook de l'exe.
