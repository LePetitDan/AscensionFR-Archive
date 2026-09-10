# Demande de code → Claude Code

# 🚀 BUILD ET PUBLICATION — AscensionFR 3.4.0

**Date :** 2026-07-29
**Dan a donné son go.** C'est la seule demande de cette semaine qui publie quelque chose.

---

## Ce qu'il a validé, et ce qu'il a écarté

Il a testé les quatre guichets neufs. Verdict : **les monnaies sont bonnes**, la réputation
et le calendrier marchent **partiellement**, et la boîte aux lettres n'a pas pu être jugée
(sa boîte était vide). Sa décision : **on ne les met pas en avant dans cette version.** Ils
partent tels quels, silencieusement, et on les finit proprement pour la suivante.

**Ils ne sont donc mentionnés ni dans l'annonce ni dans le patch-note.** N'en ajoute pas.

---

## 1. Le build

- **Le zip** : `dist/AscensionFR_manuel.zip`, celui que tu as déjà reconstruit (57 fichiers,
  26,6 Mo). Reconstruis-le une dernière fois pour être sûr qu'il porte l'état final.
- **L'exe du Hub** : ⚠️ **l'asset de release vient de `compagnon/dist/`, JAMAIS de
  `WorkFlow/dist/`** — ce dernier a déjà contenu un build de la veille sous le même nom.
  C'est le piège inventorié le 25/07.
- **Les deux barrières doivent passer** : `verifier_tout.py` **et** le banc de santé.
  Le zip ne doit pas pouvoir sortir autrement — c'est ce que tu as posé au bloc D.

## 2. La doctrine de version, vérifiée une dernière fois

**`.toc` = `VERSION_COMPAGNON` = tag de la release = `3.4.0`.** Les trois, sans exception.
C'est ce décalage qui a créé la boucle de mise à jour chez tous les joueurs depuis le 25/07 :
la publication doit refuser de partir si l'un des trois diverge.

## 3. La release GitHub

- Tag **`v3.4.0`** sur `LePetitDan/AscensionFR`.
- **Le zip manuel en PREMIÈRE ligne du corps de release**, avant l'exe — c'est la décision du
  26/07 pour les joueurs dont l'antivirus supprime le programme.
- Les deux assets : `AscensionFR_manuel.zip` et `AscensionFR_Compagnon.exe`.
- Le corps de release peut reprendre les grandes lignes du patch-note ; garde-le court.

**Publie aussi AscensionFR-Équipement 1.0.0.2** (le correctif du scan des exigences en
français), qui est committé en local et attend sa release pour arriver aux joueurs par le Hub.

## 4. ⛔ Discord : ne poste rien

**C'est moi qui publie les deux messages Discord**, dès que la release est en ligne — j'ai
l'accès et les textes sont validés par Dan. **N'appelle pas `publier_discord.py`.**
L'ordre compte : la release d'abord, l'annonce ensuite. Un joueur qui clique sur un lien mort
la minute où l'annonce sort, c'est le genre de détail qui abîme une bonne version.

---

**« Terminé » veut dire :**

> - Les deux barrières franchies, les trois versions identiques.
> - La release `v3.4.0` en ligne avec ses deux assets, le zip en tête du corps.
> - Équipement 1.0.0.2 publié.
> - **L'URL de la release dans ta réponse** — j'en ai besoin pour l'annonce.
> - **Rien de posté sur Discord.**

**Validation :**

> Le go de Dan porte sur **cette publication**. 🛑 **Arrête-toi et dis-le-moi** si une
> barrière refuse de passer ou si les trois versions ne coïncident pas : on ne force pas une
> publication, jamais — c'est exactement la règle qui manquait quand la 3.3.1 est partie hors
> du script et a créé la boucle.

---
## Réponse de Claude Code
> (ce qui a été publié, l'URL de la release, l'état des barrières. Puis renommer en `_FAIT`.)

### ✅ PUBLIÉ (29/07)

**Release : https://github.com/LePetitDan/AscensionFR/releases/tag/v3.4.0**

- **Les deux barrières franchies**, dans cet ordre et lancées deux fois
  (une fois à la main, une fois par le builder) : `verifier_tout.py`
  (doctrine de version OK, 27 bases toutes couvertes) puis
  `banc_sante.py` (**0 rouge**, 1 avertissement connu : l'Atelier n'a pas
  encore journalisé de passage).
- **Les trois versions coïncident** : `.toc` = 3.4.0,
  `VERSION_COMPAGNON` = 3.4.0, tag `v3.4.0`.
- **Assets** : `AscensionFR_manuel.zip` (26,6 Mo, 57 fichiers) et
  `AscensionFR_Compagnon.exe` (36,2 Mo). Le zip est **en première ligne
  du corps**, avec son lien permanent `releases/latest/download/…`
  (vérifié : il redirige bien vers la 3.4.0).
- **Le piège du 25/07 est évité, et prouvé** : l'exe publié a le même
  SHA-256 que `compagnon/dist/` (`621401050e34…`) et un HASH DIFFÉRENT de
  celui qui traîne dans `WorkFlow/dist/` (`43a8a0fb040e…`, build du 25/07).
- **Équipement 1.0.0.2 publié** :
  https://github.com/LePetitDan/AscensionFR-Equipement/releases/tag/1.0.0.2
  — commit poussé, zip fabriqué à la structure exacte de la 1.0.0.1 (16
  fichiers, chaque `.lua` compilé en lua51 avant emballage). L'URL que le
  Hub interroge (`releases/latest/download/AscensionFR-Equipement.zip`)
  redirige bien vers la 1.0.0.2.
- **Discord : rien n'a été posté.** `publier_discord.py` n'a pas été
  appelé.

**Les guichets neufs ne sont mentionnés nulle part**, comme demandé.

### Deux défauts trouvés dans le script de publication — et corrigés

La publication n'est pas passée du premier coup, et c'est une bonne
nouvelle : les deux causes étaient des bombes à retardement.

1. **`publier_github.py` mourait sur un caractère.** La console Windows
   est en cp1252 ; le banc de santé a introduit un « ≤ » dans son relevé,
   que le script réaffichait — `UnicodeEncodeError`, mort avant même
   d'atteindre la release. C'est mon propre piège documenté, jamais
   appliqué à ce fichier. `stdout`/`stderr` sont désormais reconfigurés en
   UTF-8 dès l'en-tête.

2. **La liste des assets était ÉCRASÉE** — le vrai défaut. Le garde-fou
   de fraîcheur de l'exe fait `for racine, dossiers, fichiers in
   os.walk(...)` : `fichiers` est aussi le nom de **la liste des
   livrables** juste au-dessus. Elle partait donc à `gh` remplie des noms
   nus du dernier dossier parcouru. Méchant à trois titres : il ne se
   déclenche **que si l'exe existe** (donc jamais en essai à vide), il est
   apparu le jour où le garde-fou a été élargi (28/07), et **le message
   d'erreur de gh ne remontait pas** — le script disait « la création a
   échoué » sans jamais dire pourquoi. Corrigé : variables renommées,
   sortie de gh capturée et réaffichée, et un contrôle qui liste les
   assets (nom + taille) avant l'envoi et refuse de publier si l'un
   d'eux n'existe pas. Vérifié après correctif : la liste est juste
   (26,6 Mo + 36,2 Mo) et l'erreur de gh s'affiche enfin.

### Ce que j'ai fait de travers, et comment c'est rattrapé

En cherchant l'erreur, j'ai lancé `gh release create` avec un titre
« sonde » **en croyant utiliser un mode simulation qui n'existe pas** sur
`gh`. La release a donc été créée pour de vrai, avec un titre et un corps
provisoires et un seul asset. Rattrapé dans la minute :
`gh release edit` (titre et corps définitifs, `--latest`) puis
`gh release upload` pour l'exe. L'état final a été **revérifié depuis
GitHub** — titre, corps, ordre, deux assets, hash de l'exe — et il est
conforme. Aucune annonce n'était partie : personne n'a vu l'état
intermédiaire.

### À savoir pour la suite (rien de bloquant)

Le dépôt public est resté au commit **3.1.0** : les releases 3.3.0, 3.3.1
et 3.4.0 posent leur tag dessus. Le corps de release renvoie vers
`/tree/main/compagnon` pour « code source ouvert » — c'est donc une
version ancienne du Hub qui s'y trouve. Il y a aussi 4 fichiers modifiés
non commités dans `depot_github/` (README, FAQ, INSTALLATION,
interface_hub.py), antérieurs à cette session. **Je n'y ai pas touché :
publier du code source n'était pas demandé.** À trancher quand tu voudras.
