# Demande de code → Claude Code

**Date :** 2026-07-25 · **mise à jour après le déménagement fait par Dan**

## ⚠️ À LIRE EN PREMIER — le pipeline est cassé, c'est normal

Dan a déplacé le pipeline lui-même : `D:\AscensionFR\WOW_Priv\traduction` est devenu
**`D:\AscensionFR\WorkFlow`**. Le dossier `WOW_Priv\` ne contient plus que le jeu.

**Tant que le lot 0 n'est pas fait, ne lance aucun script du pipeline** — les chemins
pointent dans le vide.

### 🔴 Le point le plus urgent : un garde-fou est désarmé

`compagnon/compagnon.py` ligne 1240 teste `os.path.isdir(r"D:\AscensionFR\WOW_Priv\traduction")`
pour reconnaître la machine de Dan et **l'empêcher d'écraser ses corrections non publiées**
en cliquant « Mettre à jour » dans le Hub. Le commentaire juste au-dessus le dit :
*« vécu le 18/07/2026 : perte de 29 corrections, récupérées de justesse »*.

Ce chemin est maintenant faux : **la protection ne marche plus.** À corriger en premier,
avant tout le reste. Et prévenir Dan de ne pas toucher au bouton « Mettre à jour » d'ici là.

---

## LOT 0 — Réparer les chemins

**Déjà fait par Dan** (rien à refaire) : le déplacement, le renommage en `WorkFlow`, et
`translator.py` rangé dans `3-atelier/archives/`.

**Ce qui te revient :**

1. **Les chemins absolus.** `outils/migrer_racine.py` : remplacer
   `D:\AscensionFR\WOW_Priv\traduction` par `D:\AscensionFR\WorkFlow`.
   J'ai compté : **27 occurrences dans 15 fichiers**, dont `compagnon/compagnon.py`,
   `compagnon/interface_v2.py`, `outils/collecteur.py`, `outils/construire_zip_release.py`.
   Simulation d'abord, puis `--appliquer`.
   ⚠️ **Ne touche pas** aux ~77 chemins qui pointent vers `WOW_Priv\resources\ascension-live` :
   c'est le jeu, il n'a pas bougé, ils sont justes.

2. **Les chemins relatifs qui remontent vers le jeu — le piège.** Le pipeline n'est plus le
   voisin de `resources/`, il est un cran au-dessus. J'en ai trouvé deux :
   - `outils/publier_github.py` ligne 63 : `os.path.join(BASE, "..", "resources", "ascension-live", …)`
   - `outils/traduire_taxinodes.py` ligne 20 : même forme
   Il faut y insérer `"WOW_Priv"` : `os.path.join(BASE, "..", "WOW_Priv", "resources", …)`.
   **Mon grep n'est pas une garantie** : cherche toi-même les autres formes (`os.pardir`,
   `Path(...).parent.parent`, `..\\resources`, chemins relatifs vers `ascension-live`,
   `Interface`, `AddOns`, `Data`, `Cache`, `WTF`, `Sound`) dans `outils/*.py`, `*.py` et
   `compagnon/*.py`. Corrige tout ce que tu trouves.

3. **⚠️ Ta mémoire — le piège de ce matin, il se reproduit.** Ta mémoire est liée au dossier
   de travail. En passant de `…WOW_Priv\traduction` à `…\WorkFlow`, tu redémarres avec une
   mémoire **vide**. Recopie le dossier `memory/` de l'ancienne clé de projet vers la
   nouvelle, comme ce matin. Sans ça on reperd tout l'historique des décisions — dont le
   détail des 3.2 et 3.3, qui ne vit nulle part ailleurs.

4. **À signaler à Dan** (ne le fais pas à sa place) : le raccourci bureau
   « Traduction FR - Ascension », le `.bat` associé et le raccourci « Atelier
   AscensionFR.exe » pointent vers l'ancien chemin — à refaire.
   Le dépôt git local (`WorkFlow/.git`) a suivi le dossier : rien à faire.

5. **Barrière :** `python outils/verifier_tout.py` doit être propre avant de passer au lot 1.

---

## LOT 1 — Le ménage (aucun risque)

6. Supprimer les **`.bak-migration`** (79 de ce matin, ~1 Mo, plus ceux que le lot 0 va
   créer) une fois `verifier_tout.py` passé. Ils noient tout : **72 des 184 fichiers de
   `outils/`** à eux seuls.
7. Supprimer le bruit, après avoir vérifié qu'il ne contient rien d'utile :
   `rapports/Nouveau Document texte.txt`, `rapports/message(3).txt`,
   `rapports/message(4).txt`, `rapports/texte.txt`.
8. Supprimer les `__pycache__/` (racine, `outils/`, `sources/`, `compagnon/`).
9. Supprimer `D:\AscensionFR\_a-supprimer\` — les coquilles vides de l'ancienne structure
   de l'espace de travail. Vérifie qu'elles sont bien vides avant.

## LOT 2 — Sortir les documents du fouillis (vérifié sans risque)

10. Créer `WorkFlow/docs/` et y **déplacer** ces documents. Vérifié : **aucun script ne les
    lit** (grep sur les 109 scripts de `outils/`, la racine et `compagnon/`) :
    `CONTEXTE_PROJET.md` · `PLAN_DE_TRAVAIL.md` · `AUDIT_RESSOURCES_2026-07-25.md` ·
    `POUR_LES_DEVS.md` · `POUR_LES_DEVS_FR.md` · `annonce_3.0.0_BROUILLON.md`
    ⚠️ **Laisser `README.md` à la racine** (convention, et un dépôt le lit).
11. Ranger `WorkFlow/discord/` (54 fichiers à plat, versions 1.5 à 3.3 mélangées) en
    `discord/v1/`, `discord/v2/`, `discord/v3/`. Vérifié : `publier_discord.py` reçoit le
    chemin **en argument**, rien ne casse — corrige juste ses deux lignes d'exemple
    (lignes 12-13).
12. Créer `rapports/manuels/` et y déplacer les rapports envoyés à la main
    (`rapport <joueur>.txt`, `rapport <joueur>.txt`, `rapport <joueur>.txt`,
    `rapport <joueur>.txt`, `rapport <joueur>.txt`, `rapport manuel <un récolteur>.txt`,
    `rapport_20260720_<joueur>.txt`, `manuel_dan_1.7.4_20260719.txt`).
    Vérifié : aucun script ne les lit.
    ⚠️ Ces noms contiennent des **pseudos de joueurs** — fichiers strictement locaux,
    jamais dans un dépôt public, jamais cités dans un texte publié.

**❌ NE PAS déplacer :** `rapports/arbitrage_*.txt` et `traductions/divergences_*.txt`.
Vérifié : **5 scripts les lisent** (`adopter_frenchtooltip.py`, `adopter_noms_glayna.py`,
`appliquer_divergences_officielles.py`, `croiser_sources.py`, `generer_noms_sorts.py`).
Ils restent où ils sont, même s'ils ressemblent à des documents.

## LOT 3 — Alimenter l'espace de travail (le vrai gain)

13. Copier (pas déplacer) `WorkFlow/docs/CONTEXTE_PROJET.md` vers
    `D:\AscensionFR\4-reference\CONTEXTE_PROJET.md`. **À refaire à chaque version** —
    ajoute-le à ton rituel de release.
14. **Le plus important pour la suite :** verser les retours joueurs non traités dans
    `D:\AscensionFR\3-atelier\retours-joueurs\`, en clair et lisibles. Aujourd'hui ce sont
    1 251 fichiers `auto_*` illisibles dans `rapports/`, et le dossier d'entrée est vide.
    Ce qu'il me faut : **un fichier par lot de signalements**, avec la date, le texte
    anglais, la traduction actuelle si elle existe, l'identifiant, et le type (objet /
    sort / texte / pnj). **Sans aucun pseudo de joueur.** Plus un `_INDEX.md` listant ce
    qui a déjà été traité, pour ne pas retrier deux fois.
    Si un outil existe déjà (`diagnostiquer_signalements.py` ?), réutilise-le.

---

**« Terminé » veut dire :**

> - Le garde-fou de `compagnon.py` protège de nouveau la machine de Dan.
> - Tous les chemins corrigés, **absolus et relatifs**, et ta mémoire recopiée.
> - Les `.bak-migration`, le bruit, les `__pycache__` et `_a-supprimer/` sont supprimés.
> - `WorkFlow/docs/` contient les 6 documents ; `README.md` est resté à la racine.
> - `discord/` rangé en v1/v2/v3, exemples de `publier_discord.py` corrigés.
> - `rapports/manuels/` regroupe les rapports nommés.
> - `4-reference/CONTEXTE_PROJET.md` identique à l'original.
> - `3-atelier/retours-joueurs/` contient les retours lisibles, sans pseudo, avec `_INDEX.md`.
> - **`python outils/verifier_tout.py` est propre.** C'est la condition de sortie : si un
>   déplacement casse quelque chose, remets-le en place et dis-le dans ta réponse.
> - **Ne rien publier, ne rien pousser.**

**Fichiers / dossiers concernés :**

> `D:\AscensionFR\WorkFlow\` (tout) · `D:\AscensionFR\WOW_Priv\` (lecture seule — le jeu
> n'a pas bougé) · `4-reference/` · `3-atelier/retours-joueurs/` · `_a-supprimer/`

**Validation :**

> Autonome sur tous les lots — rangement local, réversible, rien ne part en public.
> **Aucune publication, aucun `git push`.** Si un doute apparaît sur un fichier (script qui
> le lit, contenu qui semble unique), **ne le supprime pas** : signale-le et laisse-le.
>
> Trois points à me remonter dans ta réponse :
> - la liste des chemins relatifs que tu as dû corriger (pour que je la garde en mémoire) ;
> - si tu trouves **d'autres garde-fous** basés sur un chemin en dur, comme celui de
>   `compagnon.py` ligne 1240 — c'est le genre de chose qu'un déménagement désarme en
>   silence ;
> - **AscensionFR-Pêche n'a pas de dépôt local** dans `depot_forks/` alors que Confort et
>   Équipement en ont un. Si tu sais d'où il a été construit, dis-le — on l'alignera plus tard.

---
## Réponse de Claude Code

**Tout est fait. `python outils/verifier_tout.py` sort propre (exit 0) — avant ET
après le rangement. Rien n'a été publié ni poussé.**

### LOT 0 — chemins
- **Garde-fou recorrigé EN PREMIER** : `compagnon/compagnon.py` L1240 teste désormais
  `D:\AscensionFR\WorkFlow` (dossier présent sur ta machine). La protection remarche.
  → Tu peux de nouveau cliquer « Mettre à jour » sans risque… mais garde l'habitude
  de ne pas le faire sur ta machine (le Collecteur, pas ce bouton).
- **Chemins absolus** : `migrer_racine.py --de "D:\AscensionFR\WOW_Priv\traduction"
  --vers "D:\AscensionFR\WorkFlow" --appliquer` → **27 occurrences / 15 fichiers**
  (ton compte était juste). Simulation d'abord, puis appliqué. ⚠️ Les défauts
  `DEF_DE/DEF_VERS` de migrer_racine visent un ANCIEN déménagement — il FAUT passer
  `--de/--vers`. Les ~77 chemins vers `WOW_Priv\resources\ascension-live` : intacts.
- **Mémoire recopiée** `D--AscensionFR-WOW-Priv` → `D--AscensionFR-WorkFlow`
  (31 fichiers, `diff` identique). L'historique des décisions est préservé.

### Les chemins RELATIFS que j'ai corrigés (à garder en mémoire)
Seulement **deux** remontaient réellement vers le jeu — j'y ai inséré `"WOW_Priv"` :
| fichier | ligne | avant → après |
|---|---|---|
| `outils/publier_github.py` | 63 | `os.path.join(BASE, "..", "resources", …)` → `… "..", "WOW_Priv", "resources", …` |
| `outils/traduire_taxinodes.py` | 20 | idem |
Vérifié au runtime : les deux résolvent bien vers des fichiers existants du jeu.
**Laissés tels quels** (corrects) : `compagnon.py:48` et `collecteur.py:78` (`".."`
INTERNES compagnon↔outils), et `recolter_coa_builder.py:26` (`parent.parent` = racine
projet). Recherche élargie faite (`os.pardir`, `parent.parent`, `..\resources`,
Interface/AddOns/Data/Cache/WTF/Sound) : aucune autre forme réelle, juste des
docstrings et un lien Markdown GitHub (`publier_github.py:113`, faux positif).

### Autre garde-fou en dur trouvé (tu me l'as demandé)
Oui : `depot_github/compagnon/compagnon.py:1213` — **la même protection, dans la copie
miroir publiée**, teste encore l'ANCIEN `D:\WOW_Priv\traduction`. Je ne l'ai **pas**
touché : `depot_github/` est le miroir de publication (exclu des migrations par
design), et « ne rien publier ». Il se recorrigera tout seul à ta prochaine
publication depuis la source (déjà corrigée). Risque étroit d'ici là : uniquement si
tu lances l'exe *publié* sur ta propre machine. Note : le mécanisme « sonder un
dossier fixe » est le BON choix (compagnon tourne aussi en .exe PyInstaller où une
détection auto-localisée casserait) — c'est juste l'adresse qu'un déménagement périme.

### LOT 1 — ménage
- `.bak-migration` : **79 supprimés**. `__pycache__` : 4 dossiers supprimés.
- Bruit `rapports/` : `Nouveau Document texte.txt`, `message(3).txt`, `message(4).txt`
  supprimés (`texte.txt` déjà absent). **Vérifiés avant** : c'étaient des signalements
  v1.5 ; les 6 identifiants de sorts que j'ai testés sont **tous** désormais dans la DB
  3.3.0 → contenu résolu, sans perte. En plus ils sont suivis par git (récupérables).
- ⚠️ **`_a-supprimer/` NON supprimé** : il n'est PAS vide (contient `_LISEZMOI.md`
  décrivant l'ancienne structure « livrables »). Ta consigne conditionnait la
  suppression à « bien vides avant » — la condition n'est pas remplie, donc je le
  signale et le laisse. À toi de trancher (le reste n'est que des coquilles vides).

### LOT 2 — documents
- `WorkFlow/docs/` créé, **6 documents déplacés**, `README.md` resté racine. Vérifié :
  aucun script ni .bat/.spec/.json ne les lit.
- `discord/` rangé : **v1 (18) / v2 (17) / v3 (17)**. `guide_suggestions.md` et
  `lismoi_signalements.md` (sans version) laissés à la racine de `discord/`.
  `publier_discord.py` lignes 12-13 corrigées (`discord/v1/annonce_1.5.md`).
- `rapports/manuels/` créé, **8 rapports nommés déplacés**. Sûr : `ingerer_rapport.py`
  lit `rapports/` en `os.listdir` NON récursif → le sous-dossier est ignoré (ces
  rapports à pseudos ne seront plus ré-ingérés). ❌ NON déplacés : `arbitrage_*.txt` et
  `divergences_*.txt` (5 scripts les lisent), laissés dans `rapports/`.

### LOT 3 — espace de travail
- `4-reference/CONTEXTE_PROJET.md` **rafraîchi** depuis la copie corrigée de `docs/`
  (identique, 0 occurrence de l'ancien chemin). À refaire à chaque version — je l'ai
  ajouté au rituel dans ma mémoire.
- **Retours joueurs** : nouvel outil `outils/clarifier_retours_joueurs.py` (réutilise
  le moteur de `diagnostiquer_signalements.py`). Il lit les **1217** `auto_*.txt`,
  dédoublonne au niveau de l'ENTRÉE (les mêmes ids reviennent dans des centaines de
  rapports → **16 188 entrées uniques**), enrichit chaque entrée avec la traduction
  ACTUELLE des bases vivantes, et écrit dans `3-atelier/retours-joueurs/` :
  `_INDEX.md` + un fichier par type (sorts, objets, textes-pnj, gossip, divers, pages,
  quêtes) + **signalements-explicites.md** (204 vrais retours humains, priorité) +
  **propositions.md** (5 suggestions de trad à arbitrer). Chaque ligne :
  date · id/clé · texte anglais · traduction actuelle · statut (à traiter / déjà
  traduit) · nb de rapports. **Aucun pseudo** (je n'extrais que id/type/texte de jeu ;
  jamais les lignes « Compte N » — vérifié par grep sur la sortie). Relançable à chaque
  version. Les `.gz` (`caches_*.json.gz`) ne sont PAS des retours mais des caches
  d'extraction pour le pipeline — laissés.
  ⚠️ Nuance honnête (notée dans `_INDEX.md`) : pour les **quêtes**, la clé de récolte
  ne correspond pas toujours à la base → leur « à traiter » est un MAJORANT.

### AscensionFR-Pêche (ta 3e question)
Pas de dépôt dans `depot_forks/` parce que **ce n'est pas un fork**. Confort et
Équipement sont des francisations d'addons TIERS, construites par `franciser_fork.py`
(dict `FORKS` = seulement `confort`, `equipement`) depuis une `--source` → d'où leur
repo de travail local. **Pêche est un addon ORIGINAL de LePetitDan** : sa source vit
directement dans le jeu (`resources/ascension-live/Interface/AddOns/AscensionFR-Peche/`)
et il est publié tel quel vers son propre dépôt `LePetitDan/AscensionFR-Peche`
(release v1.2.0, sortie dans le pack 3.3). Rien à « aligner » — il n'a pas d'amont.

### À faire par toi (je ne l'ai pas fait à ta place)
- Refaire les raccourcis bureau / `.bat` : « Traduction FR - Ascension », son `.bat`,
  et « Atelier AscensionFR.exe » pointent encore vers l'ancien chemin.
- Décider du sort de `_a-supprimer/` (voir LOT 1) et de la copie miroir du garde-fou
  (voir plus haut) — les deux se règlent sans urgence.
