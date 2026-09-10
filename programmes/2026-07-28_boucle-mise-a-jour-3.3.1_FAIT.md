# Demande de code → Claude Code

**Date :** 2026-07-28 · *mise à jour le 28/07 au soir : Dan a tranché la doctrine de version*
**Priorité :** haute — touche 100 % des joueurs qui utilisent le Hub, depuis le 25/07.

---

## ⭐ LA DOCTRINE DE VERSION — décidée par Dan le 28/07, elle prime sur tout le reste

> **Une mise à jour = un numéro. Le Hub porte TOUJOURS le même numéro que l'addon.**

Ça tranche la question que la version précédente de cette demande te laissait ouverte
(« monter le `.toc` et republier, **ou** dissocier proprement version d'addon et version de
Hub »). **La réponse est : on ne dissocie pas.** Il n'y a plus de release « Hub seul » avec
son propre numéro — c'est précisément ce qui a créé la boucle. Si seul le Hub change, la
version entière monte quand même, et les deux sortent ensemble.

**Ce que ça implique concrètement :**
- `VERSION_COMPAGNON` et le `## Version:` du `.toc` sont **toujours égaux**, et égaux au tag
  de la release.
- Le garde-fou de publication **refuse de publier** si les trois ne coïncident pas. Pas
  d'option pour passer outre.
- La comparaison de mise à jour porte sur ce numéro unique — donc un joueur à jour ne peut
  plus se voir proposer quoi que ce soit.

---

## Objectif (le QUOI, pas le comment)

**1. Casser la boucle de mise à jour infinie du Hub.**

Constat vérifié :
- le `.toc` vivant dit `## Version: 3.3.0` ;
- la dernière release GitHub porte le tag `v3.3.1` (correctif Hub seul, addon inchangé) ;
- `compagnon.py:version_installee()` lit la version dans le `.toc`, `derniere_release()` lit
  le `tag_name` → `mise_a_jour_dispo("3.3.0", "3.3.1")` rend **True à chaque ouverture, pour
  toujours**.

Le garde-fou de `outils/publier_github.py` (l. 62-77) décrit ce cas exact (« un décalage
rend la release invisible ou **crée une boucle de mise à jour** ») — il n'a pas joué, la
3.3.1 ayant été publiée hors de ce script.

Deux joueurs l'ont dit à voix haute le 27/07, mais le défaut est **mécanique** : il touche
tout le monde.

**Ce qu'il faut :** appliquer la doctrine ci-dessus. Un joueur déjà à jour ne doit plus rien
se voir proposer, et le cas ne doit plus pouvoir se reproduire.

**2. Le décalage des deux exe « 3.3.1 ».**

`VERSION_COMPAGNON` vaut toujours `"3.3.1"` alors que la source contient maintenant les
réparations du 26/07 (`corriger_dossier_jeu`, `reactiver_traduction`, contrôle des 3 causes
d'installation). **Deux Hub différents portent le même numéro** : celui des joueurs et celui
d'ici. Rien ne permet de les distinguer.

**Ce qu'il faut :** un numéro neuf, aligné sur l'addon selon la doctrine, et un garde-fou de
publication qui couvre aussi ce cas.

**3. Vérifier une piste, sans rien corriger si elle est fausse.**

Deux joueurs (27/07 21 h et 28/07 02 h 50) retombent en anglais **après une mise à jour**,
sur une installation qui marchait, et s'en sortent en recochant « Activer la traduction ».
Or `AscensionFRSaved.Options.desactive` n'existe que si le joueur a décoché lui-même.
Question : un chemin de mise à jour du Hub (ré-extraction du zip par-dessus l'installation,
écriture dans les SavedVariables, ou la boucle du point 1 qui ré-installe à chaque ouverture)
peut-il écrire `desactive = true` ou faire perdre l'état ? Si oui, corriger. **Si non,
l'écrire noir sur blanc** : ça deviendra une ligne de FAQ et pas un chantier.

## « Terminé » veut dire

- **`VERSION_COMPAGNON` = `.toc` = tag de release**, et la publication refuse tout écart.
- Un joueur à jour n'a plus aucune mise à jour proposée ; un joueur en retard en a toujours
  une (les deux cas testés).
- Le point 3 est tranché par écrit, corrigé ou écarté avec la raison.
- Zip et exe reconstruits, barrière de vérification propre. **NE PAS PUBLIER.**

## Fichiers / dossiers concernés

`WorkFlow/compagnon/compagnon.py` (`version_installee`, `derniere_release`,
`mise_a_jour_dispo`, `VERSION_COMPAGNON`, `reactiver_traduction`),
`WorkFlow/compagnon/interface_hub.py`, `WorkFlow/outils/publier_github.py`,
`WorkFlow/outils/construire_zip_release.py`,
`WOW_Priv/resources/ascension-live/Interface/AddOns/AscensionFR/AscensionFR.toc`.

⚠️ Rappel de l'inventaire du 25/07 : l'asset de release vient de `compagnon/dist/`, **jamais**
de `WorkFlow/dist/` (qui contient un build périmé du 24/07 sous le même nom).

⚠️ Cette demande et `2026-07-28_lot12-hub-passe-ux.md` sortent **ensemble** : un seul Hub,
un seul numéro, aligné avec l'addon 3.4.

## Validation

Autonome jusqu'au zip et à l'exe. **Publication = attendre le go de Dan.**

---
## Réponse de Claude Code

**Fait le 28/07/2026.** Les trois points sont traités ; le build (zip + exe)
est fait avec la passe UX du lot 12 (les deux demandes sortent ensemble).

### 1. La boucle est cassée, et elle ne peut plus se refabriquer

La doctrine est appliquée mot pour mot — un seul numéro, partout :

- **`VERSION_COMPAGNON = "3.4.0"`** (compagnon.py) et **`## Version: 3.4.0`**
  dans le .toc vivant. Les deux sont égaux dès maintenant, pas seulement au
  moment de publier.
- **`publier_github.py` refuse tout écart entre les TROIS numéros** (tag
  demandé, .toc vivant, VERSION_COMPAGNON lu dans la source). Le message
  liste les trois valeurs et il n'existe aucune option pour forcer. L'ancien
  garde-fou ne comparait que le tag au .toc — c'est exactement le trou par
  lequel la 3.3.1 « Hub seul » est passée (publiée hors du script, en plus).
- **`verifier_tout.py` contrôle l'égalité .toc = VERSION_COMPAGNON en
  permanence** et met le banc en échec sinon. Comme `construire_zip_release.py`
  lance ce banc avant d'emballer, un écart bloque le zip aussi — un contrôle
  qui mord, pas un qui informe.
- **Le garde-fou « exe périmé » est élargi** : il comparait l'exe au seul
  `compagnon.py` ; il le compare maintenant à la source la plus récente de
  tout `compagnon/` (interface_hub.py, décors, assets…) — c'est le cas
  « deux Hub différents portent le même numéro » qui devient impossible.
- **Banc : section 7 ajoutée à `verifier_hub.py`** — le joueur en retard se
  voit toujours proposer la mise à jour (3.3.0→3.3.1, 3.3.1→3.4.0), le
  joueur à jour ne se voit RIEN proposer, pas de rétrogradation, et
  l'alignement vivant VERSION_COMPAGNON = .toc est vérifié à chaque passe.
  **Résultat : 0 échec.**

Chez les joueurs : leur Hub 3.3.1 verra la release 3.4.0, installera le zip
dont le .toc dit 3.4.0, et la comparaison s'éteindra. La boucle meurt à la
première mise à jour réussie.

### 2. Les deux exe « 3.3.1 »

Réglé par le numéro neuf : la source d'ici est 3.4.0, l'exe des joueurs dit
3.3.1. Plus aucune ambiguïté. Le garde-fou élargi (source la plus récente de
tout compagnon/) empêche le cas de se reproduire : un exe qui n'embarque pas
la dernière retouche d'interface ne peut plus partir en release.

### 3. La piste « retombe en anglais après une mise à jour » — TRANCHÉE : le chemin de mise à jour est innocent

**Aucun chemin de mise à jour ne peut écrire `desactive = true` ni perdre
l'état.** Preuves, vérifiées dans le code :

- Le zip de release n'emballe QUE `Interface\…` (`construire_zip_release.py`,
  liste ESSENTIEL+OPTIONNEL) — jamais `WTF\`. L'extraction par-dessus le jeu
  (`installer_zip`) ne peut donc pas toucher les SavedVariables, même
  répétée en boucle à chaque ouverture.
- Côté Hub, la SEULE écriture dans les SavedVariables est
  `reactiver_traduction()` — qui ne sait que RETIRER la ligne
  `["desactive"] = true`, jamais l'ajouter.
- Côté addon, `desactive = true` n'a que TROIS écrivains, tous des gestes
  volontaires : `/afr off` (Recolte.lua:64), la case « Activer la
  traduction » (Options.lua:712), et **le clic droit sur le bouton de
  minimap** (Minimap.lua:70).
- `Core.lua` ne fait que LIRE la clé ; aucune migration ne réinitialise les
  Options.

**La ligne de FAQ** (à écrire telle quelle) : *« Une mise à jour ne peut pas
désactiver la traduction : elle ne touche que les fichiers de l'addon,
jamais tes réglages. Si le jeu retombe en anglais, c'est presque toujours un
clic droit involontaire sur le bouton rond près de la minimap — il bascule
la traduction, et ne le dit qu'en une ligne discrète dans le chat. Reclique
droit dessus, ou recoche "Activer la traduction" dans /afr. »*

⚠️ **Point qui attend une décision de Dan** : ce clic droit minimap est une
bascule silencieuse à un clic, sans confirmation — un réflexe naturel (on
attend un menu d'un bouton de minimap) coupe toute la traduction. Deux
options si tu veux le durcir : demander une confirmation, ou faire du clic
droit un second chemin vers les options. C'est un changement de
comportement, donc je n'y touche pas sans ton accord.

### Vérifications

- `verifier_hub.py` : **0 échec** (section 7 comprise).
- `verifier_tout.py` : code 0, « Doctrine de version : .toc =
  VERSION_COMPAGNON = 3.4.0 — OK ».
- pyflakes propre sur les quatre fichiers touchés.
- Zip et exe : reconstruits à la fin de la passe UX (voir la réponse du
  lot 12). **Rien n'est publié, rien n'est poussé.**
