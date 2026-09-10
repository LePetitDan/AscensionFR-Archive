# Demande de code → Claude Code

**Date :** 2026-07-30
**Origine :** veille Discord du 30/07 — deux signalements en 3.4.0 qui pointent
probablement vers la **même zone : le nom des sorts**.

---

## Ce qu'on a vu

**1. Conflit avec l'addon Clique** (signalement complet, 29/07 12 h 00, en 3.4.0,
1 312 479 traductions, traduction **activée**) :

> « l'addon ne fonctionne pas avec l'addon Clique. Je dois désinstaller AscensionFR,
> puis mettre mes raccourcis en jeu avec Clique, puis réinstaller AscensionFR pour que
> cela fonctionne. **La semaine dernière il n'y avait pas de problème entre les 2 addons.** »

**2. « Mes sorts sont dans une sorte de franglais chelou »** (30/07 09 h 59) — install
à jour, traduction activée, aucune réponse ne lui a été faite. C'est le 2ᵉ joueur sur le
thème « traduit à un endroit, anglais ailleurs » (le 1ᵉʳ était le 26/07 : procs et
intégrations).

## Mon hypothèse — à confirmer ou à démolir, je n'ai pas pu la vérifier

Clique mémorise ses liaisons **par nom de sort**. Si le nom rendu par `GetSpellInfo`
change entre le moment où le joueur crée sa liaison et le moment où Clique la relit,
la liaison ne retrouve plus rien. Le contournement du joueur (désinstaller → régler
Clique → réinstaller) colle exactement à ça : il configure en anglais, puis la
traduction repasse par-dessus.

Si c'est ça, ce n'est **pas propre à Clique** : toute macro, tout WeakAura, tout addon
qui stocke un nom de sort est concerné. Et le « franglais » du 2ᵉ joueur serait le même
mécanisme vu de l'autre bout — une partie des sorts traduits, l'autre non, selon le
chemin d'affichage.

**Je peux me tromper**, et je préfère le dire : je n'ai pas de trace en jeu, et la
formule « la semaine dernière ça marchait » peut aussi désigner un changement de
couverture entre la 3.3.0 et la 3.4.0 (+39 883 champs), voire une mise à jour de Clique.

---

**Objectif (le QUOI) :**
> Dire **ce qui se passe réellement**, en rejouant le moteur, pas en lisant un fichier :
> 1. Est-ce que la 3.4.0 remplace le nom d'un sort là où un autre addon peut le relire
>    (`GetSpellInfo`, cache de sorts, hook global) — ou seulement à l'affichage ?
> 2. Qu'est-ce qui a changé sur les sorts **entre la 3.3.0 et la 3.4.0** ? Un diff
>    chiffré des champs de sorts touchés suffit.
> 3. Le « franglais » : sur un sort donné, lister **tous** les chemins d'affichage
>    (barre d'action, infobulle, journal de combat, proc, talent) et dire lesquels
>    passent par la traduction et lesquels non.

**« Terminé » veut dire :**
> Une réponse écrite en bas de ce fichier : hypothèse confirmée ou écartée, avec le
> chiffre qui le prouve. **Si elle est confirmée**, une proposition de correctif et son
> coût — sans rien appliquer. **Aucune publication, aucun build.**

**Fichiers / dossiers concernés :**
> `WorkFlow/` (moteur de traduction des sorts, bases `DB_*.lua`, `traductions/*.json`),
> l'addon publié en 3.4.0.

**Validation :**
> Autonome pour l'enquête et le chiffrage. Toute correction attend le go de Dan.

---
## Réponse de Claude Code

**FAIT le 2026-08-09, dans le bloc F du programme 32** —
[`2026-08-08_PROGRAMME-32-solder-l-arriere_FAIT.md`](2026-08-08_PROGRAMME-32-solder-l-arriere_FAIT.md).

En bref : **hypothèse forte DÉMOLIE.** (1) AscensionFR ne remplace jamais
`GetSpellInfo`/`GetSpellName` — il ne traduit les noms qu'à l'**affichage** (SetText). Clique
3.3.5 stocke/lance par le **nom de l'API** (anglais sur client enUS), qu'AscensionFR ne
touche pas → la traduction ne peut ni changer ni casser une liaison Clique par ce chemin.
(2) Diff des noms : 3.3.0 = 77 765, **3.4.0 = 72 869 (−4 896)**, 3.4.3 = 72 915, **33 = 72 912
(−3)** — le pont des noms est **gelé depuis la 3.4.0**. (3) Le « franglais » est l'architecture
« affichage seulement » (barre d'action & journal de combat jamais touchés), pas un bug.
**Coût pour la 33 : nul sur l'axe Clique** — ses +6 715 traductions sont Gossip/PNJ/quêtes/
descriptions, **0 nom de sort** ; **F ne bloque pas la 33.** Porte étroite restante : un fork
de Clique qui lirait le texte **affiché** (le mécanisme qui a cassé DragonUI) — à trancher par
un test en jeu (`/run AscensionFRSaved.Options.sansInterception = true`, protocole dans le 32).
Aucun correctif appliqué. Détail dans le programme 32.
