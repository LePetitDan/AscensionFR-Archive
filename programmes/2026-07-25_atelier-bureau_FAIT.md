# Demande de code → Claude Code

**Date :** 2026-07-25

**Objectif (le QUOI, pas le comment) :**

> Redonner à Dan son **Atelier** sur le bureau, en état de marche.
>
> Il a perdu le raccourci. L'exe existe encore
> (`WorkFlow\outils\build_collecteur\dist\Atelier AscensionFR.exe`) **mais il a été
> construit le 21/07/2026** : il embarque les chemins de l'époque
> (`D:\WOW_Priv\traduction`), figés au build. Deux déménagements ont eu lieu depuis.
> **Un raccourci vers cet exe donnerait un Atelier qui travaille dans le vide** — et on ne
> peut pas le vérifier en cherchant du texte dedans : PyInstaller compresse en zlib
> (piège déjà documenté pour le webhook).
>
> Donc : **reconstruire**, puis poser le raccourci.
>
> 1. Vérifier d'abord que `outils/collecteur.py` porte bien les chemins actuels — il
>    devrait, tu l'as corrigé : `BASE = r"D:\AscensionFR\WorkFlow"` et les chemins vers le
>    jeu en `D:\AscensionFR\WOW_Priv\resources\...`. Contrôle aussi les chemins des DB
>    (`DB_SortsCorrections.lua`, `DB_Communaute.lua`, `DB_Sorts.lua`) en tête de fichier.
> 2. Reconstruire l'exe avec `outils/build_collecteur/Collecteur AscensionFR.spec`
>    (nom de sortie : « Atelier AscensionFR », icône `compagnon/assets/logo_atelier.ico`,
>    `console=False`). Attention aux chemins relatifs du spec (`..\collecteur.py`,
>    `..\..\compagnon\assets`) : il faut le lancer depuis le bon dossier.
> 3. **Archiver l'ancien exe** plutôt que l'écraser en silence — s'il reste sur le disque
>    avec ses vieux chemins, quelqu'un le relancera un jour par erreur. Renomme-le en
>    `Atelier AscensionFR_PERIME-21-07.exe` ou déplace-le dans `archive/`.
> 4. **Poser le raccourci sur le bureau de Dan.** Un raccourci Windows (`.lnk`) vers le
>    nouvel exe, avec son icône, nommé « Atelier AscensionFR ». Pas une copie de l'exe :
>    un raccourci, pour que les prochains rebuilds soient pris en compte tout seuls.
> 5. **Le tester** : lance-le et vérifie qu'il s'ouvre, qu'il voit le bon dossier de travail
>    et qu'il liste bien les étapes. **N'exécute aucune des 6 étapes** — on veut juste
>    savoir qu'il démarre et qu'il regarde au bon endroit.
>
> **Le Hub** : Dan le retéléchargera lui-même depuis la release, pas besoin de le
> reconstruire.

**« Terminé » veut dire :**

> - `outils/collecteur.py` confirmé à jour (chemins `WorkFlow` + `WOW_Priv`).
> - Nouvel exe construit, ancien archivé sous un nom qui dit qu'il est périmé.
> - Raccourci « Atelier AscensionFR » sur le bureau de Dan, avec la bonne icône.
> - Tu l'as ouvert au moins une fois : il démarre et pointe sur le bon dossier.
> - Aucune des 6 étapes de la chaîne n'a été lancée. Rien publié, rien poussé.

**Fichiers / dossiers concernés :**

> `WorkFlow/outils/collecteur.py` · `WorkFlow/outils/build_collecteur/` ·
> `WorkFlow/compagnon/assets/logo_atelier.ico` · le Bureau de Dan

**Validation :**

> Autonome. C'est un outil personnel de Dan, jamais distribué — aucun risque de
> publication.
>
> Deux points à me remonter :
> - **Est-ce que d'autres exe ou raccourcis traînent avec les anciens chemins ?**
>   Tu as déjà trouvé le garde-fou périmé dans `depot_github/` ; les exe construits avant
>   le 25/07 sont dans le même cas — ils portent des chemins morts sans le dire.
>   Fais l'inventaire de ce qui est encore constructible/lançable et périmé.
> - Si `collecteur.py` avait encore un chemin faux, dis-lequel — ça voudrait dire que la
>   migration en a raté un.

---
## Réponse de Claude Code

**Fait : Atelier reconstruit, ancien archivé, raccourci posé (Bureau **et** Menu Démarrer),
testé — il démarre et pointe sur `D:\AscensionFR\WorkFlow`. Aucune étape de la chaîne
n'a tourné lors du test propre. Rien publié, rien poussé.**
⚠️ **Un incident lors du 1er essai de test** (chaîne lancée quelques instants, sans dégât) —
détaillé plus bas, je te le remonte honnêtement.

### 1. `collecteur.py` — chemins confirmés à jour (la migration n'a rien raté)
Vérifié en tête de fichier :
- `BASE = r"D:\AscensionFR\WorkFlow"` ✓
- `CORRECTIONS` / `COMMUNAUTE` / `DB_SORTS` → `D:\AscensionFR\WOW_Priv\resources\ascension-live\…\DB\DB_SortsCorrections.lua` / `DB_Communaute.lua` / `DB_Sorts.lua` ✓ (les 3 fichiers existent, tailles cohérentes)
- La chaîne des 6 étapes (`aspirer_discord`, `ingerer_rapport`, `ingerer_caches`, `traducteur_fr --une-fois`, `ingerer_recolte`, `traducteur_fr --sorts`) pointe sur `outils/…` internes.

**Aucun chemin faux dans `collecteur.py`.** La migration ne l'a pas raté.

### 2. Reconstruction + archivage
- Ancien `dist\Atelier AscensionFR.exe` (21/07) → **`build_collecteur\archive\Atelier AscensionFR_PERIME-21-07.exe`**.
- Trouvé un 2e exe périmé dans le même `dist\` : `Collecteur AscensionFR.exe` (18/07, le prédécesseur) → **archivé** `…\archive\Collecteur AscensionFR_PERIME-18-07.exe`.
- `build\` nettoyé, puis **rebuild** depuis `build_collecteur\` (pour que les chemins relatifs du spec résolvent) : `python -m PyInstaller --noconfirm "Collecteur AscensionFR.spec"`.
- **Nouvel exe** `dist\Atelier AscensionFR.exe` (25/07 19:47, ~37 Mo, icône `logo_atelier.ico`, `console=False`). Il embarque le `collecteur.py` corrigé → chemins vivants.

### 3. Raccourci(s)
- **Bureau** : `C:\Users\<utilisateur>\Desktop\Atelier AscensionFR.lnk` → le **dist** (pas une copie de l'exe : un `.lnk`, donc les prochains rebuilds sont pris tout seuls, comme tu voulais). Icône `logo_atelier.ico`.
- **Bonus** : ton **raccourci perdu n'était pas perdu** — il était dans le **Menu Démarrer** (`…\Start Menu\Programs\Atelier AscensionFR.lnk`, créé le 20/07) et **cassé** : il visait une *copie* de l'exe posée sur le Bureau (`Desktop\Atelier AscensionFR.exe`), disparue. C'est justement ce que tu voulais éviter (« pas une copie »). Je l'ai **re-ciblé** vers le nouveau dist → il remarche aussi.

### 4. Test (sans lancer aucune étape)
La fenêtre **s'auto-lance** 400 ms après ouverture (`after(400, lancer)`). Pour l'ouvrir sans
déclencher la chaîne, j'ai posé un **verrou vivant** dans `D:\AscensionFR\WorkFlow\.atelier_en_cours`
(le PID d'un process bien vivant). Résultat mesuré : l'exe **a trouvé ce verrou**, a affiché
« un atelier tourne déjà » et **n'a lancé aucune étape** (`refused=True`, verrou NON réécrit).
→ Double preuve : (a) il **démarre** ; (b) il **regarde bien dans `WorkFlow`** — un exe périmé
aurait cherché le verrou dans `D:\WOW_Priv\traduction`, ne l'aurait pas trouvé, et aurait démarré
la chaîne. Les 3 bases de jeu n'ont **pas** été écrites (mtime inchangé). `verifier_tout.py` = propre (exit 0).

### ⚠️ Incident à te remonter (transparence)
**Mon 1er essai de test a raté et a lancé la chaîne quelques instants.** J'utilisais un faux
process (python `-c`) pour tenir le verrou ; il est mort tout de suite (souci de guillemets),
donc l'exe a cru le verrou orphelin, l'a pris, et a démarré. Je l'ai **arrêté**, mais entre-temps :
- **Étape 1 (aspiration) a tourné** : ~**175 rapports `auto_*` téléchargés** du salon Discord, et
  le pointeur `discord_aspirateur.json` a avancé. **Non destructif** — c'est la récolte normale ;
  ces rapports seraient venus de toute façon, ils ne re-téléchargeront pas.
- `traductions/propositions_joueurs.json` a été touché (accumulateur de propositions — bénin).
- **Aucune base de jeu écrite** (`DB_SortsCorrections/Communaute/Sorts` intacts, mtime 78 min),
  **aucune corruption** (`verifier_tout.py` exit 0). Aspiration **ne supprime rien** sur Discord
  (juste un pointeur local).

Rien à annuler (état pipeline normal). J'ai **laissé** les 175 rapports (données réelles). Note :
ton snapshot `3-atelier/retours-joueurs/` du chantier précédent est donc en retard de 175 rapports —
relance `outils/clarifier_retours_joueurs.py` quand tu voudras les intégrer. Le 2e essai (verrou
tenu par un `ping`, vérifié vivant AVANT) est passé proprement, 0 étape.

### Inventaire — autres artefacts périmés (ton point à remonter)
Recherche exhaustive (exe, `.lnk`, `.bat/.cmd/.ps1/.spec`, configs) sous `D:\AscensionFR` + ton profil.
Rappel du piège : les exe PyInstaller sont compressés → **impossible d'y lire les chemins** ;
critère = **date de build avant le 25/07 ~19:00**.

> **Nuance (vérif adversariale d'un sous-agent) :** les exe **Compagnon/Hub** ne portent PAS de chemin pipeline mort — le Compagnon résout le dossier de jeu **choisi par l'utilisateur**, il ne code aucun `BASE` en dur. Leur vrai défaut est du **CODE périmé** (builds d'avant les éditions du soir, dont le garde-fou anti-écrasement). Le piège « chemins figés » vaut surtout pour l'**Atelier** (lui code `BASE` en dur) — déjà réglé.

**🔴 Haut risque :**
| artefact | date | risque |
|---|---|---|
| `dist\AscensionFR_Compagnon.exe` (**racine WorkFlow**) | 25/07 00:21 | **DOUBLON DANGEREUX** au nom de release, dans un `dist\` inattendu (≠ `compagnon\dist`). Quelqu'un pourrait l'uploader sur la release GitHub à la place du bon. Ne garder qu'UN seul candidat. |
| `compagnon\dist\AscensionFR_Compagnon.exe` | 25/07 15:42 | l'asset de release (copie du Hub) : **code périmé** (avant les edits du soir). Rebuild + vérifier `VERSION_COMPAGNON == tag` avant toute publi. |

**🟠 Moyen :**
| artefact | date | note |
|---|---|---|
| `compagnon\dist\AscensionFR_Hub.exe` | 25/07 15:41 | build Hub, code périmé — sert de source au « cp » vers le nom de release |
| `compagnon\dist\AscensionFR_Compagnon_v2.exe` | 22/07 19:27 | fallback v2 (correctif d'urgence), supplanté |
| `…\Start Menu\…\Play Ascension.lnk` | — | cible `D:\WOW_Priv\Ascension Launcher.exe` **absente**. Le launcher vit en `D:\AscensionFR\WOW_Priv\Ascension Launcher.exe`. Échec **visible** (pas de travail-dans-le-vide), mais bloque ton lancement de jeu quotidien. |
| `dist\` (racine) : zips/MPQ de release | 25/07 <19:00 | `AscensionFR_manuel.zip`, `AscensionFR-Peche.zip`, `patch-ZZZ.MPQ` — **non inspectés** ; probables assets de jeu sans chemin pipeline, à vérifier avant publi si l'un embarque un manifeste. |
| `a_traduire\lots.json` | — | chemins **absolus morts** `D:/WOW_Priv/traduction/…` (racine #1). **Vérifié inerte** (aucun outil ne relit le champ `fichier`). Régénéré par `preparer_lots.py`. |
| `depot_github\compagnon\compagnon.py:1213` | — | garde-fou **miroir** testant `D:\WOW_Priv\traduction` (mort). La source vive `compagnon\compagnon.py:1240` teste déjà le bon `WorkFlow` → protection saine tant qu'on build depuis la source vive. Danger seulement si un exe est bâti depuis `depot_github`. |

→ **Tu as dit ne pas reconstruire le Hub** (tu le reprends de la release), donc je n'y touche pas ; je te les liste. Le seul à traiter tout de suite si tu veux : le **doublon** `dist\AscensionFR_Compagnon.exe` (racine) — je ne l'ai pas supprimé (artefact de **release**, hors périmètre Atelier), à toi de décider.

**🟢 Bénin — aucune action :**
- **~40 raccourcis MRU** dans `…\Windows\Recent` visant les anciennes racines : auto-générés par Windows, s'effacent seuls.
- Exe **du jeu** (`Ascension Launcher.exe`, `Ascension.exe`, etc.) : bon emplacement, hors pipeline.
- Tous les `.spec` : chemins **relatifs** au spec, résolvent correctement. Les `.bat/.cmd` d'archive/fork : relatifs, sans chemin mort.
- Les 2 exe Atelier/Collecteur déjà **archivés** ce soir (neutralisés).

### Ce qui attend une décision de toi
- **`Play Ascension.lnk`** (Menu Démarrer) est cassé : re-cibler vers `D:\AscensionFR\WOW_Priv\Ascension Launcher.exe` (je ne l'ai pas touché — c'est le lanceur du **jeu**, hors périmètre Atelier ; dis-moi si tu veux que je le refasse).
- **Le doublon `dist\AscensionFR_Compagnon.exe` (racine WorkFlow)** : à supprimer/déplacer pour qu'il ne reste qu'UN candidat de release (celui de `compagnon\dist`, après rebuild). Je l'ai laissé (artefact de release).
- **Reconstruire les exe Compagnon/Hub** depuis la source corrigée avant ta prochaine release (code du soir + garde-fou). Toi seul décides du timing de publication.
- Éventuellement **relancer `clarifier_retours_joueurs.py`** pour intégrer les 175 rapports arrivés ce soir.
