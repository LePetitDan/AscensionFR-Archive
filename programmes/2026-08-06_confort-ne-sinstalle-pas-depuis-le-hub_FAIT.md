# Demande de code → Claude Code

# 🧩 « Le zip ne contient pas AscensionFR-Confort.toc » — l'addon Confort refuse de s'installer

**Date :** 2026-08-06

---

## Le problème, en une phrase

Un joueur sur **Steam Deck (SteamOS, donc Linux)** installe le Hub sans souci, puis clique pour
installer **AscensionFR-Confort** et reçoit :

```
ValueError: le zip ne contient pas AscensionFR-Confort.toc
```

C'est le **premier signalement** de cette erreur, et il est **exploitable tel quel** : message
exact, addon nommé, plateforme connue.

⚠️ **Ce qui n'est PAS établi** : on ne sait pas si c'est propre à Linux ou si **tout le monde**
est concerné. Aucun joueur Windows ne l'a signalé, mais personne ne prouve qu'un joueur Windows a
installé Confort depuis le Hub cette semaine. **Ne pas conclure avant d'avoir mesuré.**

---

## Ce que j'ai déjà vérifié (pour ne pas te le refaire)

- `WorkFlow/compagnon/interface_hub.py` l. 519 : la comparaison est **déjà insensible à la casse**
  (`n.lower() == dossier.lower()`). Ce n'est donc **pas** un problème de majuscules Linux.
- `dossiers_addon_du_zip` (l. 477) exige qu'un dossier **porte son propre `.toc`**
  (`AscensionFR-Confort/AscensionFR-Confort.toc`). Si le zip livre les fichiers **à plat**, ou dans
  un dossier nommé autrement (`AscensionFR-Confort-main/`, typique d'un zip de sources GitHub),
  la liste revient vide et le garde-fou lève exactement cette erreur.
- Le catalogue (`assets/hub/catalogue_hub.json`) pointe vers
  `releases/latest/download/AscensionFR-Confort.zip` — un **asset de release**, pas le zip de
  sources.
- Dans `WorkFlow/depot_forks/AscensionFR-Confort/`, le `.toc` est **à la racine du dépôt**. Donc si
  l'asset de release est fabriqué en zippant *le contenu* du dépôt plutôt que *le dossier*, on
  obtient un zip à plat → l'erreur du joueur.
- ❌ Je **n'ai pas pu** lire la release sur GitHub (lecture web revenue vide). C'est le point à
  mesurer en premier, et je ne tire aucune conclusion sans ça.

---

## Objectif (le QUOI, pas le comment)

1. **Mesurer** : télécharger réellement les 4 assets du catalogue (Confort, Équipement, Pêche,
   DragonUI) et dire, pour chacun, **ce qu'il y a à l'intérieur** — dossier racine ou fichiers à
   plat, et si le `.toc` attendu est trouvable par `dossiers_addon_du_zip`.
2. **Réparer la cause** là où elle est : soit la fabrication de l'asset (le zip doit contenir le
   dossier), soit le déballage (accepter un zip à plat et le re-raciner sous le nom de la fiche).
   Mon avis, à confirmer par la mesure : **corriger les deux** — l'asset pour que ce soit propre,
   le déballage pour que ça ne casse plus jamais si un dépôt tiers change son emballage.
3. **Que l'erreur affichée au joueur soit utile.** « le zip ne contient pas X.toc » ne dit pas quoi
   faire. Elle doit dire ce qui a été trouvé dans le zip et vers quoi se rabattre.

---

## Ce à quoi il faut faire attention

- **Le garde-fou existe pour une bonne raison** : ne rien poser dans `Interface\AddOns` plutôt que
  n'importe quoi. Si tu assouplis le déballage, garde une règle stricte : on ne pose qu'un dossier
  qui contient bien un `.toc`, jamais un contenu inconnu.
- **DragonUI se livre en deux dossiers frères** (DragonUI + DragonUI_Options). Ne pas casser ça en
  corrigeant Confort — c'est un bug déjà payé une fois (26/07).
- **Linux/SteamOS est une plateforme réelle maintenant** : le Hub Linux existe depuis le 02/08
  (PROGRAMME 21). Si tu ajoutes une vérification, elle doit valoir sur les deux systèmes.
- Vérifie aussi `WorkFlow/depot_github/compagnon/interface_hub.py` — le **jumeau de publication**
  a la même ligne 523, et il a déjà divergé par le passé.

---

## « Terminé » veut dire

1. Tu me dis, asset par asset, **ce que contient réellement chaque zip du catalogue** aujourd'hui.
2. Tu me dis si le défaut touche **Linux seulement** ou **tout le monde** — et sur quelle mesure tu
   t'appuies pour le dire.
3. Installer Confort depuis le Hub fonctionne, testé, sur au moins un des deux systèmes.
4. L'erreur affichée en cas d'échec dit **ce qui a été trouvé** dans le zip.
5. Tu me dis si les 3 autres fiches du catalogue étaient dans le même cas — c'est-à-dire combien de
   joueurs ont pu buter là-dessus sans le dire.

---

## Fichiers / dossiers concernés

- `WorkFlow/compagnon/interface_hub.py` (`dossiers_addon_du_zip` l. 477, `installer_addon_zip` l. 494)
- `WorkFlow/depot_github/compagnon/interface_hub.py` (le jumeau)
- `WorkFlow/compagnon/assets/hub/catalogue_hub.json`
- La fabrication des assets de release des 3 dépôts `AscensionFR-*`

---

## Validation

**Autonome pour la mesure et la correction du code.**
⛔ **Pas de publication sans le go de Dan** : si ça débouche sur une nouvelle version du Hub ou sur
un asset de release refabriqué, tu prépares et tu t'arrêtes là.

---
## Réponse de Claude Code

**FAIT le 2026-08-09, dans le bloc E du programme 32** —
[`2026-08-08_PROGRAMME-32-solder-l-arriere_FAIT.md`](2026-08-08_PROGRAMME-32-solder-l-arriere_FAIT.md).

En bref : **les 4 assets du catalogue sont correctement formés aujourd'hui** (Confort,
Équipement, Pêche, DragonUI+Options — `.toc` trouvé sur chacun, Windows ET Linux, 0
backslash). L'asset Confort **n'a jamais été re-téléversé** (2 061 téléchargements du même
zip bien formé) : **la piste « fabriqué à la main → à plat » est démolie par la mesure.** Le
défaut n'est pas dans l'asset — donc pas « Linux-seulement », il n'est reproductible ni ici
ni ailleurs ; les causes restantes (Hub plus ancien chez le joueur, téléchargement tronqué,
extraction SteamOS) demandent sa machine, non-réponse honnête assumée. Réparé quand même,
défense en profondeur : le **déballage** accepte un zip à plat / un wrapper `-main/` et
re-racine sous le nom de la fiche, l'erreur **dit ce qui a été trouvé**, le **jumeau**
`depot_github` re-synchronisé, 5 formes + 4 assets réels au banc. **Aucun asset à
re-téléverser — le geste public à Dan n'a pas lieu d'être.** Détail dans le programme 32.
