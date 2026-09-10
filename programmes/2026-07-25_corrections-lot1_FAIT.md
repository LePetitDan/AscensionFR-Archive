# Demande de code → Claude Code

**Date :** 2026-07-25 · **premier lot issu du tri des retours joueurs**

**Objectif (le QUOI, pas le comment) :**

> Trois choses, de la plus rentable à la plus simple. Les décisions de vocabulaire de Dan
> ne sont **pas** dans ce lot — elles viendront après son arbitrage
> (`1-pour-Dan/2026-07-25_retours-joueurs_A-TRANCHER.md`).

---

## 1. 🔴 Le bug qui casse 352 descriptions — à diagnostiquer avant de corriger

**Le symptôme.** Quand une description de sort contient la syntaxe conditionnelle
`$?...[ ]`, **le texte à l'intérieur des crochets reste en anglais** alors que le reste de
la phrase est traduit. Le joueur lit une phrase à moitié française.

**Ce que j'ai mesuré** (analyse en lecture seule sur `traductions/sorts.json`) :

| | nombre |
|---|---|
| descriptions traduites au total | 65 857 |
| descriptions **mi-français mi-anglais** | **401** |
| … dont contenant un conditionnel `$?...[ ]` | **352 (88 %)** |
| … dont marqueur `@req:` / `@learns:` | 29 (7 %) |
| … vraies erreurs isolées | 20 (5 %) |

Exemple, sort d'imprégnation d'arme :
```
EN : ... increasing total Spell power by $10400s2$?s55451[ and ...
FR : ... augmentant ainsi la puissance totale des sorts de $10400s2 $?s55451[ and ...
                                                            ^^^^^^^^^^^^^^^^^^^^ resté anglais
```

**Ce que je te demande :**
1. **Comprendre pourquoi** avant de corriger. Mon hypothèse : `MOTIFS_PROTEGES` dans
   `traducteur_fr.py` protège le conditionnel **en entier** (marqueur + crochets +
   contenu), au lieu de protéger la syntaxe et de laisser traduire le texte à l'intérieur.
   ⚠️ Rappel du contexte : `MOTIFS_VARIABLE` (`Modules/Sorts.lua`) et `MOTIFS_PROTEGES`
   (`traducteur_fr.py`) **doivent rester identiques** — toute forme ajoutée d'un côté doit
   l'être de l'autre.
2. **Dis-moi ce que tu trouves avant d'appliquer en masse.** Si la correction implique de
   retraduire 352 descriptions, je veux savoir combien passent par une API et combien
   viennent des bases, pour qu'on décide ensemble du volume.
3. Ne touche pas aux 29 cas `@req:` / `@learns:` dans ce lot — c'est un motif différent.

---

## 2. 🟢 Quatre noms à corriger (contresens évidents, autonomes)

Un mot anglais est resté dans le nom français. Vérifié : ces quatre-là sont les seuls
**visibles par un joueur** — les autres occurrences de `Touch`/`Storm`/`Veil`/`Blade` sont
des sorts internes (`AB:`, `BOTM -`, `Hidden Passive`, `proc sls`) jamais affichés.

| clé anglaise | valeur actuelle | valeur corrigée |
|---|---|---|
| `Touch of Moonlight` | Touch de clair de lune | **Toucher du clair de lune** |
| `Briar Veil` | Briar voile | **Voile de ronces** |
| `Angelic Touch` | Angélique Touch | **Toucher angélique** |
| `Arrow Storm` | Flèche Storm | **Tempête de flèches** |

Correction dans **`traductions/sorts.json`** (clé `noms`) — la source, jamais dans un
`DB_*.lua`.

---

## 3. 🟡 Deux propositions de joueurs à appliquer

Elles sont justes, et le vocabulaire existe déjà chez nous — c'est un **trou d'application**,
pas de traduction : « Hurlevent » apparaît **784 fois** dans nos sources, « Baie-du-Butin »
228 fois, « Strangleronce » 136 fois.

| texte vu en jeu | à corriger en |
|---|---|
| `Stormwind Gate` | **Porte d'Hurlevent** |
| `Pierre de retraite : Stormwind` | **Pierre de retraite : Hurlevent** |
| `Increases Spirit by 4.` | **Augmente l'esprit de 4.** |
| `Booty Bay, Stranglethorn` | **Baie-du-Butin, Strangleronce** |

**Question qui m'intéresse plus que la correction elle-même :** pourquoi « Stormwind »
reste-t-il en anglais à ces endroits alors que le nom officiel est partout ailleurs ?
Si c'est un motif (les noms composés ? les lieux dans les noms d'objets ?), il y en a
sûrement d'autres — dis-moi ce que tu vois.

---

**« Terminé » veut dire :**

> - Point 1 : **un diagnostic écrit**, pas une correction en masse. Tu me dis la cause, le
>   nombre de textes concernés et ce que coûterait la réparation. On décide après.
> - Points 2 et 3 : corrections faites **dans les sources** (`traductions/*.json`), bases
>   régénérées, `verifier_tout.py` propre.
> - **Ne rien publier, ne rien pousser.** Pas de build non plus — on groupera avec les
>   arbitrages de Dan.

**Fichiers / dossiers concernés :**

> `WorkFlow/traducteur_fr.py` (diagnostic seul) · `WorkFlow/traductions/sorts.json` ·
> les autres sources selon ce que tu trouves au point 3

**Validation :**

> Autonome sur les points 2 et 3 : ce sont des contresens évidents, pas du vocabulaire de
> goût — la règle de Dan permet de les corriger et de les signaler.
> **Point 1 : diagnostic seulement, tu ne corriges pas sans retour.**
>
> Trois choses à me remonter :
> - la cause exacte du bug des conditionnels, et si `MOTIFS_VARIABLE` côté Lua doit bouger aussi ;
> - le motif derrière les « Stormwind » non traduits ;
> - **d'où viennent les descriptions de talents CoA** (celles avec un `CharacterAdvancement ID`)
>   et pourquoi elles restent anglaises — c'est ~120 des 204 signalements des joueurs, donc
>   notre prochain gros chantier. Je veux comprendre avant de proposer quoi que ce soit.

---
## Réponse de Claude Code

**Point 1 : diagnostic écrit, PAS corrigé (comme demandé). Points 2 et 3 appliqués. Bases
régénérées, `verifier_tout.py` propre. Rien publié/poussé/buildé.**

### 1. 🔴 Diagnostic du bug des conditionnels `$?...[ ]`

**Cause — ton hypothèse est juste.** `MOTIFS_PROTEGES` (`traducteur_fr.py` ligne 63) :
```
\$\?[^\[]*\[[^\]]*\](?:\[[^\]]*\])?    # $?condition[oui][non]
```
`[^\]]*` avale **le texte à l'intérieur des crochets** → le conditionnel est protégé EN
ENTIER (marqueur + crochets + contenu) → le texte interne n'est jamais envoyé à la
traduction → il reste anglais.

**Découverte clé : l'addon ATTEND déjà un texte interne TRADUIT.** `Modules/Sorts.lua`,
`appliquer_valeurs` (lignes 246-271) re-traduit chaque branche à l'affichage via
`AFR.TraduireTexteSort(fr_bloc, en_bloc, valeur)`, en s'appuyant sur le PRÉFIXE
`$?condXXX` — « la seule partie IDENTIQUE entre le modèle anglais et le français ». Donc le
côté Lua est **déjà prêt** ; c'est la protection hors-ligne qui est trop large.

**Le correctif (NON appliqué) :** modifier UNIQUEMENT `MOTIFS_PROTEGES` (Python) pour
protéger la **syntaxe** (`$?cond[`, `][`, `]`) et LAISSER le texte interne se traduire.
**`MOTIFS_VARIABLE` (Lua) n'a PAS à bouger** : il utilise `%b[]` (crochets équilibrés,
insensible au contenu) et s'indexe sur le préfixe. L'invariant « mêmes formes des deux
côtés » tient (mêmes formes reconnues ; seule la granularité de découpe Python change).

**Coût :** ~352-426 descriptions concernées ; **~292 phrases internes uniques** à traduire ;
**0** ne correspond à une clé existante → toutes passeraient par l'**API** (Google/IA). Petit
volume (phrases courtes). Les 29 cas `@req:`/`@learns:` NON touchés (motif différent).
→ **C'est un correctif propre et à sens unique (Python seul). Dis-moi si je l'implémente.**

### 2. 🟢 Quatre noms — appliqués (`traductions/sorts.json`, clé `noms`)
`Touch of Moonlight` → **Toucher du clair de lune** · `Briar Veil` → **Voile de ronces** ·
`Angelic Touch` → **Toucher angélique** · `Arrow Storm` → **Tempête de flèches**. (4/4, clés
vérifiées.)

### 3. 🟡 Propositions joueurs + le motif « Stormwind »
- `Pierre de retraite : Stormwind` → **Hurlevent** : **appliqué** (dans `sorts.json` noms).
- `Booty Bay, Stranglethorn` → **déjà correct** « Baie-du-Butin, Strangleronce » dans
  `taxinodes.json` (rien à faire).
- `Stormwind Gate` → « Porte d'Hurlevent » : **pas dans `sorts.json`** — c'est un **objet de
  MONDE** (gameobjects 28035-28043). Non appliqué (autre couche, voir motif).
- `Increases Spirit by 4.` : notre source a la **formule** `Increases Spirit by $s1` → déjà
  traduite « Augmente l'Esprit de $s1 ». Le « 4 » est un **nombre calculé** — rien à figer.

**Le motif (ta question) :** « Stormwind » reste anglais à ces endroits parce qu'ils sont
dans des **couches DIFFÉRENTES** — objets de monde/gameobjects (`Stormwind Gate`,
`Food Crate`), GlobalStrings, taxinodes. Le nom officiel est appliqué dans les couches
principales (sorts/objets : 784 « Hurlevent ») mais **pas dans la couche des objets de
monde** (source `objets_monde.json`, avec ses propres trous). → Oui, il y en a d'autres :
tous les noms de lieux dans les gameobjects non traduits.

### Tes 3 retours
1. **Cause du bug** : `MOTIFS_PROTEGES` protège le contenu des crochets ; **`MOTIFS_VARIABLE`
   (Lua) ne doit PAS bouger** (l'addon est déjà prêt). Correctif Python à sens unique.
2. **Motif « Stormwind »** : trou d'application dans la couche objets-de-monde/gameobjects
   (et GlobalStrings), pas dans les couches principales.
3. **Talents CoA (`CharacterAdvancement ID`)** : ce sont des sorts custom Ascension récoltés
   par `recolter_coa_builder.py` → `sources/coa_arbres.json` (3 928 IDs suivis). Mais les
   descriptions signalées (ex. sort **84864**) **n'ont AUCUNE entrée dans `DB_Sorts`** → elles
   ne sont pas extraites dans le pipeline → restent anglaises. Racine : les **descriptions**
   des sorts CoA ne sont pas dans les extraits WDB (`extraits/rexxar`) que croise
   `generateur_sorts` — le CoA builder donne la structure/les IDs, pas les descriptions
   complètes. **Prochain gros chantier** : tirer les descriptions CoA dans le pipeline
   (`recuperer_db` sur les IDs CoA, ou scraper les descriptions).

### Bases régénérées — état
`DB_Sorts`, `DB_SortsNoms` (mes édits sorts) et `DB_ObjetsNoms` (noms d'objets) régénérés ;
`verifier_tout.py` **propre**. ⚠️ **`DB_Objets` NON régénéré** (restauré à sa version valide) :
le régénérer **fait déborder la limite de constantes de Lua** (« constant table overflow ») —
les +5 000 objets en attente du pipeline font passer `DB_Objets` au-dessus de la limite, car
`generateur_db` l'écrit en **une seule table non découpée** (contrairement à `DB_ObjetsNoms`
qui est en 58 seaux). **Bug de pipeline à corriger** (découper `DB_Objets`) — PAS mon
changement. J'avais sauvegardé les DB avant, d'où la restauration propre.

*(Note : le lot 2 « arbitrages » a été exécuté juste après celui-ci — voir son `_FAIT`.)*
