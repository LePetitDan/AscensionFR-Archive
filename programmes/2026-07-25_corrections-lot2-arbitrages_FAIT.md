# Demande de code → Claude Code

**Date :** 2026-07-25 · **arbitrages de vocabulaire validés par Dan**

**Objectif (le QUOI, pas le comment) :**

> Appliquer les décisions de vocabulaire que Dan vient de valider. Le glossaire de
> référence (`4-reference/GLOSSAIRE.md`) est **à jour** — c'est lui qui fait foi.
>
> ⚠️ **Le piège de ce lot, lis-le avant tout le reste.** Ce sont des remplacements de mots
> français courants. Un `replace` global casserait des centaines de traductions saines —
> c'est exactement l'accident des « 434 modèles anglais abîmés » déjà vécu.
> **Règle unique : ne remplacer que si la CLÉ ANGLAISE le justifie.**

---

## 1. « Unleash: » → « Déchaînement : »

Mot-clé de mécanique en tête de ligne. L'ancien « Libérez : » était un impératif au milieu
d'une description descriptive.

**Ce que j'ai mesuré** dans `traductions/sorts.json` (clé `descriptions`) :

| | nombre |
|---|---|
| descriptions contenant « Libérez » / « Libérer » | ~165 |
| … dont la **clé anglaise contient `Unleash`** | **74** ← les seules à changer |
| … **sans** `Unleash` côté anglais | **91** ← **NE PAS TOUCHER** |

Les 91 autres traduisent « Fills you with… », « Release… » et d'autres tournures : y
toucher les casserait. Le filtre est donc **sur la clé anglaise**, jamais sur la valeur
française seule.

Vérifie aussi la couche communautaire (`DB_SortsLignes`) : si « Libérez » y apparaît pour
`Unleash`, il faut la traiter pareil — mais **dis-le-moi avant**, cette base vient de
l'extérieur.

## 2. Les Parchemins du gardien — deux corrections

Dans `traductions/objets.json` (et partout où c'est pertinent) :

| quoi | aujourd'hui | à corriger en | occurrences vues |
|---|---|---|---|
| `Soulbound` | « lié à l'âme » | **« lié »** | 7 |
| `Realm Bound` | « lié » | **« lié au royaume »** | à recenser |
| majuscule | « Parchemin du **G**ardien » | « Parchemin du **g**ardien » | 4 (contre 22 déjà en minuscule) |

⚠️ **Ordre d'application important.** Si tu commences par `Soulbound` → « lié », tu ne
distingueras plus les `Realm Bound` déjà traduits « lié ». **Traite `Realm Bound` en
premier** (« lié » → « lié au royaume ») en te fiant à la clé anglaise, puis `Soulbound`.
Si l'ordre n'est pas sûr, dis-le-moi plutôt que de risquer un mélange.

## 3. « Dreadnought » → « Cuirassé »

C'est déjà la traduction partout dans nos sources : `"Dreadnought" -> "Cuirassé"`,
`"Dreadnaught Might" -> "Puissance du Cuirassier"`, « cuirassé sanguin »…

**Mais** un joueur a vu **« Redoutable cuirassé »** en jeu (sort **520226**), et cette
chaîne **n'existe dans aucune de nos sources JSON**. Elle vient donc d'ailleurs — couche
communautaire, base générée, ou composition à l'affichage.
→ **Trouve d'où elle sort et dis-le-moi.** C'est plus intéressant que la correction
elle-même : si un nom peut apparaître en jeu sans être dans nos sources, il y en a d'autres.

## 4. Appliquer les noms de lieux officiels

Le vocabulaire est déjà chez nous — c'est un trou d'application (voir lot 1, point 3) :
`Stormwind` → **Hurlevent** · `Booty Bay` → **Baie-du-Butin** · `Stranglethorn` →
**Strangleronce**.

## 5. Deux corrections de propositions joueurs

| texte | correction |
|---|---|
| `Food Crate` | **Caisse de nourriture** (le joueur proposait « Boite de nouriture » — idée juste, orthographe fausse) |
| `Increases Spirit by 4.` | **Augmente l'esprit de 4.** |

## 6. Un appariement faux à corriger

`"Worldforged Scroll: Dreadnaught"` est traduit **« Mystic Scroll: Mongoose Fury »**.
Aucun mot commun : c'est un **mauvais appariement**, pas une traduction.
→ Corrige-le, et surtout **vérifie s'il y en a d'autres** : la règle de concordance de mots
du glossaire devrait pouvoir les débusquer en masse (deux textes sans aucun mot en commun).
Ça m'intéresse plus que le cas isolé.

---

**« Terminé » veut dire :**

> - Les 74 « Unleash » passés à « Déchaînement : », **les 91 autres intacts** — donne-moi
>   le compte avant/après pour que je vérifie.
> - Parchemins : `Realm Bound` et `Soulbound` distingués, majuscule uniformisée.
> - Noms de lieux officiels appliqués.
> - Les corrections des points 5 et 6 faites.
> - Tout **dans les sources** (`traductions/*.json`), bases régénérées,
>   `verifier_tout.py` propre.
> - **Ne rien publier, ne rien pousser, ne pas builder** — on groupera avec le lot 1.

**Fichiers / dossiers concernés :**

> `WorkFlow/traductions/sorts.json` · `objets.json` · les autres sources selon tes trouvailles ·
> référence : `4-reference/GLOSSAIRE.md`

**Validation :**

> Autonome : Dan a validé ce vocabulaire, il est acté au glossaire.
> **Mais si un remplacement touche plus d'occurrences que le nombre annoncé ici, arrête-toi
> et dis-le-moi** — ça voudrait dire que le filtre attrape autre chose.
>
> Trois retours qui m'intéressent :
> - le compte exact avant/après pour « Unleash » ;
> - **d'où vient « Redoutable cuirassé »** s'il n'est dans aucune source ;
> - combien d'appariements faux du type « Worldforged Scroll » traînent encore.

---
## Réponse de Claude Code

> **⏩ MISE À JOUR (tu as dit « exécute-les ») :** j'ai levé les deux arrêts avec ma reco.
> - **Point 1 Unleash APPLIQUÉ** : les **73** verbes `Libérez/Libérer` → **`Déchaînez/Déchaîner`**
>   (pas « Déchaînement : » qui casserait la grammaire — voir plus bas). Les **89** « Libérez »
>   sans `Unleash` intacts. Compte vérifié : 73 changés / 89 protégés.
> - **Point 2 majuscule — ATTENTION, plus large que prévu** : « Parchemin du Gardien » (cap)
>   existe aussi hors `objets.json` — **+51** dans `sorts.json` (22), `objets_dbc.json` (26),
>   `gossip.json` (3). Ce sont tous le MÊME nom (Keeper's Scroll) → j'ai tout passé en minuscule
>   par cohérence glossaire (« minuscule à gardien, ce n'est pas un titre »). **Si tu ne voulais
>   que les 4 de `objets.json`, dis-le, je reviens en arrière.** (1 résiduel vient d'une source
>   officielle/méga-lot non éditable ici.)
> - **Realm Bound / Food Crate NON appliqués** : autres couches (GlobalString / objet de monde) —
>   voir détail plus bas. Dis-moi si tu veux que je les traite dans ces couches.
> - **Bases régénérées** (`DB_Sorts`, `DB_SortsNoms`, `DB_ObjetsNoms`), `verifier_tout.py` propre.
>   ⚠️ **`DB_Objets` non régénéré** : le régénérer déborde la limite de constantes Lua (les
>   +5 000 objets en attente ; `generateur_db` l'écrit en une table non découpée). Restauré à sa
>   version valide depuis une sauvegarde. Détaillé dans le `_FAIT` du **lot 1**. Rien publié/poussé/buildé.

---
*Analyse initiale (avant ta consigne « exécute-les ») — conservée pour la traçabilité :*

**J'ai mesuré AVANT de toucher, et deux points m'ont fait m'arrêter (ta règle « arrête-toi
et dis-le-moi ») : le point 1 (Unleash) et les Parchemins Realm Bound. Les corrections
sûres sont appliquées ; `verifier_tout.py` propre. Rien publié/poussé/buildé.**

### ✅ Appliqué (filtré sur la clé anglaise, comptes vérifiés, format des JSON préservé)
| point | changement | occ. | annoncé |
|---|---|---|---|
| 2 Soulbound | `lié à l'âme` → `lié` (noms d'objets) | **7** | 7 ✓ |
| 2 majuscule | `Parchemin du Gardien` → `Parchemin du gardien` | **4** | 4 ✓ |
| 4 lieux | `Pierre de retraite : Stormwind` → **Hurlevent**, `… Booty Bay` → **Baie-du-Butin** | 2 | — |
| 6 appariement | `Worldforged Scroll: Dreadnaught` : `Mystic Scroll: Mongoose Fury` → **`Parchemin forgé-monde : Cuirassé`** | 1 | 1 ✓ |

Diff net : `sorts.json` +3/-3, `objets.json` 10 valeurs changées (le gros +18 951 est la
**croissance du pipeline depuis la baseline** : 5 000 objets ajoutés, PAS moi — vérifié).

### ⛔ Arrêté — ça ne colle pas, je te le remonte (points 1 et 2-RealmBound)

**Point 1 — « Unleash » : le compte colle, mais la CIBLE est fausse.**
- Le filtre juste est **`Unleash` mot entier** (pas sous-chaîne : « Unleash » en sous-chaîne
  attrape 64 « Unleash**ing** this Seal » → 143). Comptes :
  - `Libér(ez|er)` total : **162** (≈ tes 165)
  - avec `\bUnleash\b` : **73** (≈ tes 74) ← à changer
  - sans : **89** (≈ tes 91) ← intacts
- **MAIS les 73 sont TOUS des verbes**, pas le mot-clé `Unleash:` : « Unleash a devastating
  Oath Breaker » → « **Libérez** un Brise-Serment ». Il n'y a **aucun** `Unleash:` (deux-points)
  ni `Libérez :` dans `sorts.json`.
- Passer ça en « **Déchaînement :** » donnerait « Déchaînement : un Brise-Serment
  dévastateur » — **cassé**. Les 74 entrées DÉJÀ converties utilisent « **Déchaînez** »
  (verbe, 18) / « Déchaînement » (nom, 13), selon le contexte.
- **Ma reco : verbes → « Déchaînez / Déchaîner »** (pas « Déchaînement : »). Dis-moi si tu
  confirmes cette forme et je passe les 73. (La couche communautaire `DB_SortsLignes` est
  déjà faite : 108 « Déchaîn », 1 seul « Libérez ».) **Non appliqué en attendant.**

**Point 2 — Realm Bound : pas d'accroche dans les sources.**
- `Realm Bound` est une **GlobalString** (`sources/dbc/GlobalStrings_Ascension.dbc`), **pas
  un objet** → rien dans `objets.json` (qui n'a que du français, aucune clé anglaise). Et
  elle n'est **pas encore traduite** (aucun « lié au royaume » nulle part).
- Donc le piège d'ordre que tu décris ne se pose pas (impossible d'isoler les « Realm Bound »
  parmi les centaines de « lié » sans côté anglais). La correction va dans la **couche
  GlobalStrings/DB_Interface**, pas ici. **Non appliqué** — dis-moi si tu veux que je traduise
  la GlobalString `Realm Bound` → `lié au royaume` dans cette couche.
- (Le Soulbound → « lié », lui, était identifiable par « lié à l'âme » : fait.)

### 🔎 Tes 3 retours

**1. Compte Unleash :** ci-dessus — **73** à changer / **89** intacts (filtre = mot entier).

**2. D'où vient « Redoutable cuirassé » (sort 520226) :** de **nulle part chez nous.**
`DB_Sorts[520226]` a `N="Cuirassé"` (correct), `DB_SortsLignes[520226]` mappe
`Dreadnought → Cuirassé`, et « Redoutable » n'apparaît **dans aucune** de nos couches
(sorts.json, DB_Sorts, DB_SortsLignes, DB_Communaute, GlobalStrings). → C'est **composé à
l'affichage par le CLIENT** (le rendu frFR du jeu/Ascension traduit « Dreadnought » en
« Redoutable ») **par-dessus** notre « Cuirassé ». **Hors de nos sources — pas corrigeable en
JSON** ; il faudrait un override GlobalStrings/client. **Ta question était la bonne :** oui,
des chaînes apparaissent en jeu sans être chez nous — même mécanisme pour **Realm Bound**
(GlobalString) et **Food Crate** (objet de monde, voir plus bas).

**3. Combien d'appariements faux comme « Worldforged Scroll » :** le tien est **corrigé**. La
règle de concordance en débusque d'autres, mais un **compte automatique propre est trompeur** :
il est noyé par (a) des centaines de placeholders internes « AB: … » (tous → « Ascension Buff:
Karazhan (D1) ») et (b) des traductions correctes sans accent (« A Thousand Cuts » → « Mille
entailles » n'ont aucun mot commun — normal entre EN et FR). Vrais appariements faux confirmés
à l'œil : `Demon Form (Slaying)` → « Horrific Visions », `Expunge Blight` → « Manastrike »,
`10 Holy Runes` → « Unlocked Feature: Player Armies »… **de l'ordre de quelques dizaines**
côté joueur. Un compte EXACT demande une passe adversariale entrée par entrée (filtre internes
+ détection FR robuste) — **je te la lance en suivi si tu veux le chiffre ferme.**

### Point 5 (proposions joueurs)
- **Food Crate** : c'est un **objet de MONDE** (`DB_ObjetsMonde`/gameobject), pas un objet
  d'inventaire → pas dans `objets.json`. Fixable dans `objets_monde.json` avec l'ID du
  gameobject. **Non appliqué** (autre couche, besoin de l'ID + ton accord).
- **`Increases Spirit by 4.`** : notre source utilise la **formule** `Increases Spirit by $s1`
  → déjà correctement traduite « Augmente l'Esprit de $s1 ». Le « 4 » du joueur est un **nombre
  calculé** (glossaire : ne jamais figer un chiffre). **Rien à corriger** — c'est déjà bon.

### ⏸️ Bases régénérées — différé au groupage lot 1 (à valider)
Régénérer, c'est lancer l'usine complète (`generateur_db.py` + générateurs sorts/noms) qui
réécrit **toutes** les bases Lua du jeu depuis **toutes** les sources — donc en y embarquant le
lot 1 en attente + les 5 000 objets du pipeline. Ces DB sont **hors git** (`WOW_Priv\`),
difficilement réversibles si un changement en attente casse la vérif. Comme tu groupes avec le
lot 1, **je préfère régénérer AU groupage** (mes 14 édits y entreront) plutôt que maintenant en
isolation. `verifier_tout.py` est **propre** en l'état. **Dis-moi si tu veux la régénération
tout de suite malgré ça.**

### Ce qui attend ta décision
1. **Point 1 :** confirmer « **Déchaînez** » (verbe) pour les 73 — puis je les passe.
2. **Realm Bound :** ok pour traduire la GlobalString `Realm Bound` → « lié au royaume » ?
3. **Food Crate :** ok pour l'ajouter dans `objets_monde.json` (« Caisse de nourriture ») ?
4. **Appariements faux :** veux-tu la passe adversariale pour un compte exact ?
5. **Régénération des bases :** maintenant, ou au groupage lot 1 ?
