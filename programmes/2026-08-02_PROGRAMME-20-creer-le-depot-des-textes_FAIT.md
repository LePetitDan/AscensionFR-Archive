# Demande de code → Claude Code

# 📖 PROGRAMME 20 — créer le dépôt des textes

**Date :** 2026-08-02
**Dan a donné le GO.** C'est la suite directe du programme 19, qui a tout mesuré et tout éprouvé.

**Les trois décisions de Dan, déjà prises — ne les rouvre pas :**

1. on publie **les textes**, **pas les outils** ;
2. **dépôt séparé** — `LePetitDan/AscensionFR-Textes`, comme tu l'as recommandé ;
3. **licence MIT**, avec la phrase d'honnêteté que tu as rédigée.

🛑 **C'est un programme irréversible.** Un dépôt public est cloné et indexé en quelques heures.
On ne « dépublie » pas 46 Mo de textes.

---

## 🛑 BLOC 0 — les deux règles qui ne se discutent pas

1. **`WorkFlow` n'a pas de remote et n'en aura pas.** Le nouveau dépôt se construit **à neuf** :
   dossier vide, `git init`, premier commit. **Pas de clone, pas de `filter-repo`, pas de greffe
   d'historique.** Il porte le webhook dans son passé.
2. **Contribuer n'est pas publier.** Le nouveau dépôt n'est branché à **aucun** chemin de mise à
   jour. Ce que les 274 machines téléchargent ne bouge pas d'un octet dans ce programme.

---

## BLOC A — l'arbre à publier

Le programme 19 a établi la liste. **Revérifie-la plutôt que de la recopier** — c'est deux
minutes et ça vaut mieux qu'une confiance.

**Ce qui part :**

- **les 22 stores** retenus au bloc B du 19 (463 494 textes, 46,6 Mo) ;
- ⚠️ **`gisement_brut.json` en fait partie et c'est capital** — c'est la couche amont de
  l'interface. Sans elle, une correction d'interface serait effacée à la prochaine
  reconstruction ; tu l'as reproduit en laboratoire ;
- **les 5 stores reconstruits à neuf** (`interface_maison`, `sorts_references`, `emotes`,
  `interieurs`, `taxinodes`) **ne partent PAS** — confirme-le, une inversion ici fabriquerait
  exactement le piège qu'on évite ;
- **`4-reference/GLOSSAIRE.md`** à la racine — tu l'as balayé et déclaré publiable tel quel.
  Sans lui un contributeur produira du travail à refaire ;
- **ton mode d'emploi** (`scratchpad/LISEZMOI_textes_projet.md`) → `LISEZMOI.md` à la racine.
  Ses 4 avertissements sont le cœur de la valeur : la règle « l'officiel gagne », les codes de
  format, l'interface qui se corrige en amont, et **la chaîne sur sept qui ne sert à rien** ;
- **`LICENSE`** — MIT au nom de Dan — et la phrase d'honnêteté dans le `README.md` :

> Les textes de ce dépôt sont des traductions dérivées du contenu de World of Warcraft et
> d'Ascension. La licence MIT porte sur **notre travail de traduction** ; elle ne prétend
> accorder aucun droit sur le texte d'origine, qui appartient à ses ayants droit.

**Un `.gitignore` dès le premier commit**, pour que rien de fabriqué ne s'invite jamais.

---

## 🛑 BLOC B — le balayage, juste avant de pousser

Pas celui du programme 19 : **un neuf, sur l'arbre exact qui part**, y compris les fichiers
ajoutés depuis (`LISEZMOI`, `GLOSSAIRE`, `LICENSE`, `README`).

- `balayer_secrets.py` ;
- **les pseudonymes**, avec le dictionnaire des 47 noms de `noms_recolteurs.local.txt` ;
- **les chemins de disque**, avec ton motif resserré — pas celui qui rapportait 88 faux à cause
  de `\r\n`.

**Donne le dénominateur.** « N fichiers sur N réellement ouverts ». Un « 0 motif » sans
dénominateur ne vaut rien, c'est la leçon de la semaine.

🛑 **Un seul motif trouvé = tu t'arrêtes et tu rapportes.** On ne publie pas derrière un doute.

---

## BLOC C — créer, pousser, et se méfier de soi

- crée `LePetitDan/AscensionFR-Textes`, **public**, description courte en français ;
- pousse ;
- **vérifie que le push est arrivé** : `git rev-list --count origin/main..main` = **0**, et
  `git ls-remote` pour l'entendre dire par le distant lui-même. `git status --short` ne dit rien
  d'un commit non poussé — c'est le trou qui a mordu hier soir ;
- **puis clone le dépôt depuis GitHub, dans un dossier neuf**, et compare les fichiers en
  SHA-256 à la source privée. Le dépôt tourne avec `core.autocrlf` : un JSON qui revient avec
  d'autres fins de ligne serait un désastre silencieux. **0 écart, ou tu le dis.**

---

## 🛑 BLOC D — la boucle, éprouvée depuis le vrai dépôt cette fois

Le programme 19 a prouvé la boucle depuis une copie locale. **Refais-la depuis le clone GitHub** :
c'est exactement la leçon du programme 17, où un clone local ne prouvait pas ce qu'un clone
distant prouve.

Prends une ligne dans le clone, corrige-la, fais tourner la chaîne de Dan, **et montre-moi le
texte modifié dans l'add-on fabriqué** — avant et après, comme tu l'as fait au 19.

⚠️ **Puis remets tout en état** : cette correction de démonstration ne doit pas rester dans
`traductions/`. Vérifie-le et dis-le.

---

## BLOC E — le lien qui manque

Ajoute dans `docs/CONTRIBUER.md` du dépôt principal la section que tu avais rédigée et laissée
en attente — le dépôt cible existe maintenant, le lien n'est plus mort. Commit, push, vérifié.

🛑 **Aucun tag, aucune release, aucun des 5 fichiers surveillés touché.** `verifier_arbre_publie.py`
doit rester vert.

---

**« Terminé » veut dire :**

> - Le dépôt en ligne, **le push vérifié depuis le distant**, pas seulement commité.
> - La liste exacte de ce qui est parti, et **la confirmation que les 5 stores reconstruits n'y
>   sont pas** et que `gisement_brut.json` y est.
> - Le balayage neuf, **avec son dénominateur**.
> - **Un clone GitHub comparé octet par octet** à la source : 0 écart.
> - **La boucle éprouvée depuis ce clone**, et l'arbre de Dan remis en état après.
> - Le lien posé dans `docs/CONTRIBUER.md`.
> - Ce qui a résisté, et ce que tu as failli casser.

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Puis renommer en `_FAIT.md`.)

---

## ✅ BLOC 0 — vérifié avant de commencer

```
remotes de WorkFlow : 0        ← inchangé, et rien n'en a été ajouté
LePetitDan/AscensionFR-Textes  ← n'existait pas ("Could not resolve to a Repository")
```

Le dépôt a été bâti **à neuf** : dossier vide, copie de fichiers, `git init`,
premier commit. **Aucun clone, aucun `filter-repo`, aucune greffe d'historique.**
L'historique de `WorkFlow` — qui porte le webhook — n'a pas été lu, pas filtré, pas
approché.

**Emplacement choisi : `D:\AscensionFR\depot_textes`**, à côté de `depot_addon.git`, et
**hors de `WorkFlow`**. C'est délibéré : `depot_github` vit à l'intérieur et n'y échappe
que par une ligne de `.gitignore`. Un dépôt public n'a rien à faire à l'intérieur du
dépôt privé, même ignoré.

---

## ✅ BLOC A — l'arbre à publier, recalculé et non recopié

Je n'ai pas repris la liste du 19 : je l'ai **recalculée** depuis les mêmes règles. Elle
retombe exactement sur les mêmes chiffres — ce qui est le vrai contrôle.

**22 fichiers, 463 494 textes, 46,59 Mo :**

| fichier | textes | | fichier | textes |
|---|---:|---|---|---:|
| `objets_dbc.json` | 184 123 | | `divers.json` | 317 |
| `sorts.json` | 135 604 | | `gossip.json` | 285 |
| `objets.json` | 98 425 | | `libelles.json` | 257 |
| `creatures.json` | 13 170 | | `fenetres_perso.json` | 183 |
| `quetes.json` | 9 787 | | `pages.json` | 170 |
| `objets_monde.json` | 6 518 | | `chrspecs.json` | 153 |
| **`gisement_brut.json`** | **5 141** | | `glue_classes_manuel.json` | 51 |
| `vanity_obtention.json` | 3 524 | | `fetes.json` | 49 |
| `enchantements.json` | 2 053 | | `boss.json` | 315 |
| `textes_pnj.json` | 2 023 | | `poi_carte.json` | 406 |
| `ensembles.json` | 473 | | `sorts_recoltes.json` | 467 |

**Les six contrôles de non-inversion, passés :**

```
gisement_brut.json  est-il DEDANS ?  OUI ✅   ← la couche amont de l'interface
interface_maison    est-il DEHORS ?  OUI ✅
sorts_references    est-il DEHORS ?  OUI ✅
emotes              est-il DEHORS ?  OUI ✅
interieurs          est-il DEHORS ?  OUI ✅
taxinodes           est-il DEHORS ?  OUI ✅
```

Une inversion ici aurait fabriqué exactement le piège qu'on évite : un contributeur
corrigeant `interface_maison.json` verrait son travail effacé sans un mot à la
prochaine reconstruction du gisement. **`gisement_brut.json` est publié, les 5
reconstruits ne le sont pas.**

**Écartés :** 77 fichiers — 59 sauvegardes `_avant_*`, 5 reconstruits, 13 de service
(listes noires, décisions d'arbitrage, caches, `propositions_joueurs.json`).

**Les six fichiers d'accompagnement :**

| fichier | quoi |
|---|---|
| `LISEZMOI.md` | le mode d'emploi (une page, 4 avertissements) |
| `GLOSSAIRE.md` | copié tel quel de `4-reference/` — balayé et déclaré publiable au 19 |
| `LICENSE` | MIT au nom de LePetitDan, **avec la phrase d'honnêteté en français ET en anglais** |
| `README.md` | présentation courte + la phrase d'honnêteté |
| `.gitignore` | dès le premier commit — et il **nomme les 5 stores reconstruits**, pour qu'une copie distraite ne les fasse jamais entrer |
| `.gitattributes` | voir ci-dessous |

### Le `.gitattributes`, et pourquoi il n'était pas dans le plan

En vérifiant les fins de ligne j'ai trouvé un désaccord que personne n'avait vu :

```
les 22 JSON   : CRLF   (647 020 au total — écrits par la chaîne, Python mode texte sous Windows)
les 4 .md      : LF     (374)
core.autocrlf  : true   ← réglage SYSTÈME de la machine, pas un choix du projet
```

Avec la conversion, les JSON auraient fait l'aller-retour sans dommage (CRLF → LF →
CRLF) **mais pas les `.md`** : écrits en LF, ils seraient revenus d'un clone en CRLF.
Un contributeur aurait vu des différences fantômes sur des fichiers qu'il n'a pas
touchés.

`* -text` désactive toute conversion, dans les deux sens, sur toutes les plateformes.
Le `diff` continue de fonctionner (ce n'est pas `binary`). **Vérifié plus bas : les 28
fichiers reviennent octet pour octet.**

---

## ✅ BLOC B — le balayage, neuf, avec son dénominateur

Lancé **deux fois** : une première fois sur l'arbre, puis **refait après l'ajout de
`.gitattributes`** — parce qu'un balayage qui ne couvre pas le fichier ajouté depuis ne
couvre rien.

```
BALAYAGE DE D:\AscensionFR\depot_textes
dictionnaire de pseudonymes : 47 nom(s)
fichiers dans l'arbre       : 28
dont binaires (non lisibles): 0

FICHIERS RÉELLEMENT OUVERTS ET LUS : 28 / 28   (45,3 Mo de texte)
  1. motifs de secret       : 0
  2. chemins de disque      : 0
  3. pseudonymes de joueurs : 0
```

**28 sur 28.** Aucune cécité aux binaires ici : il n'y a **aucun binaire** dans cet
arbre, rien que du texte — donc le trou du programme 17 ne s'applique pas, et je le dis
plutôt que de lancer un balayage de binaires pour la forme.

Les pseudonymes ont été cherchés **mot entier, insensible à la casse, sur les 47 noms de
`noms_recolteurs.local.txt`** — le dictionnaire que la chaîne applique déjà, pas une
recherche au jugé. Les chemins de disque avec le **motif resserré** du 19, pas celui qui
rapportait 88 faux sur des `s:\r\n`.

**Second avis, avec l'outil officiel :**

```
$ python outils/balayer_secrets.py --racine D:/AscensionFR/depot_textes --sans-historique
✅ aucun motif de secret       (code de sortie 0)
```

**Zéro motif. Je publie.**

---

## ✅ BLOC C — créé, poussé, et vérifié depuis le distant

**Le dépôt est en ligne :** https://github.com/LePetitDan/AscensionFR-Textes

```
nom        : AscensionFR-Textes
visibilité : PUBLIC
branche    : main
commit     : fb9f44b   « Les textes français d'AscensionFR — 22 fichiers, 463 494 textes »
28 fichiers suivis
```

**Le push, vérifié — et pas avec `git status` :**

```
git rev-list --count origin/main..main  =  0     ✅
git rev-list --count main..origin/main  =  0

$ git ls-remote origin refs/heads/main            ← entendu du DISTANT lui-même
fb9f44b23b124ac01c25bfd22359ae2920843577   refs/heads/main
HEAD local                                  fb9f44b23b124ac01c25bfd22359ae2920843577
```

> Un détail qui a demandé une décision : `git commit` a refusé, « *Author identity
> unknown* ». L'identité n'est pas définie globalement sur cette machine, seulement
> **par dépôt**. J'ai **repris à l'identique** celle de `depot_github`
> (`LePetitDan <275523253+…@users.noreply.github.com>`), **en local à ce dépôt** —
> rien de global n'a été modifié. Inventer une identité aurait signé le premier commit
> du projet avec un nom qui n'est pas le tien.

### Le clone GitHub, comparé octet par octet

```
$ git clone https://github.com/LePetitDan/AscensionFR-Textes.git
fb9f44b   28 fichiers suivis

comparaison SHA-256 avec la source privée :
   les 22 JSON de traductions/          →  0 écart
   les 6 fichiers d'accompagnement      →  0 écart
```

Et le contrôle qui justifiait le `.gitattributes` :

| fichier | source | clone |
|---|---:|---:|
| `.gitattributes`, `.gitignore`, `GLOSSAIRE.md`, `LICENSE`, `LISEZMOI.md`, `README.md` | 0 CRLF | **0 CRLF** |

**Les `.md` sont revenus en LF, comme ils sont partis.** Sans `* -text`, `core.autocrlf
= true` les aurait rendus en CRLF et le clone aurait différé de la source dès le premier
jour. **0 écart sur 28 fichiers.**

---

## ✅ BLOC D — la boucle, éprouvée depuis le vrai dépôt

Le trajet complet d'un contributeur réel, en cinq étapes, chacune faite pour de vrai.

**1. Il clone** `github.com/LePetitDan/AscensionFR-Textes` — le clone du bloc C.

**2. Il corrige une ligne.** J'ai cherché un défaut réel dans le clone : 8 titres de
quête portent une ponctuation double collée, faute de typographie française que la
traduction automatique recopie de l'anglais.

```
traductions/quetes.json, quête 175141
   avant : 'AVERTISSEMENT! DANGER!'
   après : 'AVERTISSEMENT ! DANGER !'
```

**3. Dan récupère.** Le banc est remis à l'état exact de l'arbre de Dan, puis les
**22 fichiers du clone** sont posés par-dessus — c'est le geste réel : on ne copie pas
un fichier, on pose ce que le contributeur a rendu.

**4. La chaîne de Dan tourne** — `generateur_db.py`, sortie détournée vers le banc,
12,5 s, 51,4 Mo de Lua.

**5. La correction est dans l'add-on fabriqué :**

```
BANC  …station Metantenna.",T="AVERTISSEMENT ! DANGER !",TE="WARNING! DANGER!"} DB[175142]=…
      l'ancienne forme « AVERTISSEMENT! DANGER! » : ABSENTE du Lua regénéré

RÉEL  add-on de Dan, non régénéré :  'AVERTISSEMENT! DANGER!'
```

**La boucle tient depuis le dépôt public.** Ce n'est plus une copie locale comme au
programme 19 : la correction a fait l'aller-retour par GitHub.

### Tout est remis en état — vérifié, pas supposé

```
D:\AscensionFR\WorkFlow\traductions\quetes.json[175141][T] = 'AVERTISSEMENT! DANGER!'
   -> INCHANGÉ ✅

dépôt publié : git status = 0 ligne,  0 commit d'avance
la quête 175141 lue sur raw.githubusercontent.com : 'AVERTISSEMENT! DANGER!'
```

La correction de démonstration n'a existé que dans **le clone jetable** et **le banc
jetable**. Ni l'arbre de Dan, ni le dépôt public ne la portent. Je suis allé la relire
**sur GitHub** plutôt que de me fier à mon `git status` local — c'est la même leçon que
le push : la seule réponse qui compte vient du distant.

---

## ✅ BLOC E — le lien posé

`docs/CONTRIBUER.md` du dépôt principal s'adressait aux **joueurs** (« envoie ton
rapport »). Il ne disait rien à quelqu'un qui voudrait corriger le texte lui-même — et
pour cause, il n'y avait rien à corriger.

Section ajoutée en fin de fichier : le lien vers `AscensionFR-Textes`, le fait qu'aucun
outil n'est nécessaire, et **l'avertissement sur les 838 chaînes d'interface sur 5 974
déjà couvertes par l'officiel Blizzard**. J'ai tenu à le reprendre ici et pas seulement
dans le `LISEZMOI` : c'est l'erreur que j'ai faite moi-même au programme 18, et elle
coûte du travail pour rien sans jamais rien changer en jeu.

```
commit 19767622   « CONTRIBUER : le chemin pour corriger le texte soi-même »
git rev-list --count origin/main..main = 0
git ls-remote origin refs/heads/main   → 19767622e1aa60263ca17268251908c08af0c09a

$ python outils/verifier_arbre_publie.py --version 3.4.1
✅ l'arbre publié correspond à ce qui a été construit, et ne porte aucun secret.
```

**Un seul fichier modifié** (`docs/CONTRIBUER.md`), **aucun des 5 surveillés touché**,
**33 tags inchangés**, **`latest` toujours `v3.4.1`**.

---

## 🛑 Terminé — l'état exact

| « Terminé » veut dire | état |
|---|---|
| le dépôt en ligne, **push vérifié depuis le distant** | ✅ `fb9f44b`, `ls-remote` concordant, `origin/main..main` = 0 |
| la liste de ce qui est parti | ✅ **22 fichiers, 463 494 textes, 46,59 Mo** — recalculée, pas recopiée |
| **les 5 reconstruits absents, `gisement_brut.json` présent** | ✅ les **six** contrôles de non-inversion passés |
| le balayage neuf, **avec son dénominateur** | ✅ **28/28 fichiers ouverts**, 45,3 Mo de texte, **0 / 0 / 0** |
| **un clone GitHub comparé octet par octet** | ✅ **0 écart sur 28** — dont les `.md`, grâce au `.gitattributes` |
| **la boucle éprouvée depuis ce clone** | ✅ une ligne corrigée sur GitHub, retrouvée dans le Lua fabriqué |
| l'arbre de Dan remis en état | ✅ inchangé — et le dépôt public relu **sur GitHub**, pas en local |
| le lien dans `docs/CONTRIBUER.md` | ✅ commit `19767622`, poussé et vérifié |

🛑 **Aucun tag, aucune release, `latest` reste `v3.4.1`. Aucun des 5 fichiers surveillés
touché. `WorkFlow` n'a toujours aucun remote.**

### Ce qui a résisté

- **Le recalcul de la liste** est retombé sur les mêmes 22 fichiers et les mêmes
  463 494 textes que le programme 19. C'est le seul contrôle qui vaille quelque chose
  contre une liste vieille de trois heures.
- **Les garde-fous du dépôt principal** : `balayer_secrets` avant et après,
  `verifier_arbre_publie` vert, aucun des 5 surveillés effleuré.
- **Le mode d'emploi tenait déjà** : rédigé au programme 19 sans dépôt où le poser, il
  est parti tel quel — ses 4 avertissements sortent tous de mesures, pas d'intuitions.

### Ce que j'ai failli casser

1. **🛑 J'ai failli publier un dépôt qui diffère de son clone dès le premier jour.**
   `core.autocrlf = true` est un réglage **système** de cette machine — pas quelque
   chose que le projet a choisi, donc pas quelque chose à quoi on pense. Mes `.md` en
   LF seraient revenus en CRLF. Trouvé en comparant les fins de ligne **avant**
   `git init`, par acquit de conscience ; le `.gitattributes` n'était dans aucun plan.
2. **J'ai balayé, puis ajouté un fichier, et failli m'en tenir au premier balayage.**
   `.gitattributes` est né après le contrôle. Un balayage qui ne couvre pas ce qui a
   été ajouté depuis ne couvre rien — refait, 27 → 28 fichiers.
3. **`git commit` a refusé faute d'identité, et j'aurais pu en inventer une.** J'ai
   repris exactement celle du dépôt principal, en local. Le premier commit d'un dépôt
   public signé d'un nom inventé, ça ne se rattrape pas.
4. **Le contrôle « la correction de démonstration n'est pas partie » aurait pu se faire
   en local**, avec `git status`. Je suis allé relire la quête **sur
   `raw.githubusercontent.com`** — parce que c'est exactement le même aveuglement que
   « commité mais pas poussé », vu à l'envers.
