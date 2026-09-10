# Demande de code → Claude Code

**Date :** 2026-07-28 · **lot 12 — la passe UX du Hub, et un seul Hub pour la 3.4**

> À faire **après le lot 11**. À coordonner avec la demande
> `2026-07-28_boucle-mise-a-jour-3.3.1.md` : **c'est le même Hub qui sort**, une seule fois,
> avec la 3.4.

**Objectif (le QUOI, pas le comment) :**

> Rendre le Hub lisible. L'audit du 26/07 a mesuré les contrastes : **tout texte posé sur la
> texture de bois est illisible** (1,4 à 3,2 pour 1 ; seuil 4,5), **tout texte sur panneau
> parchemin est parfait** (6,7 à 10). C'est la règle que WoW s'applique à lui-même : jamais
> d'encre sur le bois, une plaque glissée dessous.

---

## Pourquoi ça n'est pas cosmétique

Trois mesures qui expliquent des semaines de messages Discord :

- **« Vérifier mon installation ↗ » : 1,4 pour 1.** C'est le lien écrit exprès pour les
  12 joueurs bloqués à l'installation. Il est **invisible**.
- **« Tout désinstaller ↗ » : 1,7 pour 1.** Les 3 joueurs qui l'ont cherché ne cherchaient
  pas mal.
- **Le verdict d'accueil « Tout est à jour » : 1,4 pour 1**, distingué du fond par la seule
  teinte — donc nul pour un joueur daltonien.

## Les deux arbitrages de Dan (28/07)

1. **Les titres : or vif + contour noir, PAS de plaque.** C'est le traitement du jeu, et la
   plaque recouvrait le fronton gravé « ASCENSION FR ». C'est l'exception assumée à la règle
   de la plaque : elle vaut pour les textes courants, pas pour les titres.
2. **Le rouge appartient à l'action principale.** « Mettre à jour » garde son rouge ;
   **« Couper les voix » devient neutre.** Le joueur ouvre le Hub pour mettre à jour, pas
   pour couper ses voix — l'œil doit tomber sur la bonne chose.

## Les 9 points de la passe

1. **Plaque sous tout texte posé sur le bois** (`Tooltips/UI-Tooltip-Background` + les
   8 bords). C'est la règle n° 1 — 15 textes concernés.
2. **Verdict d'accueil sur plaque + pastille** (`COMMON/Indicator-*`) : la forme avant la
   couleur, pour que ça marche sans distinguer les teintes.
3. **Titres** : or vif + contour noir (voir arbitrage). Et **décoller les sous-titres** :
   aujourd'hui +30 px pour une police de 30 px, ils se chevauchent sur Addons et Voix.
4. **Le `%` des jauges** est en encre sur le rail sombre : **1,2 pour 1** pendant les 1,4 Go
   de téléchargement des voix. À remonter au-dessus de la jauge.
5. **`txt_etat` n'a pas de `width`** : les messages longs (une erreur avec un chemin) sortent
   de la boîte crème et se font trancher — précisément quand le joueur a besoin de lire.
6. **Hiérarchie de l'onglet Voix** : « Voix installées » et « Tu es à jour » sont des **états
   déguisés en boutons** (images cuites inertes). Un état ne doit pas ressembler à un bouton.
7. **`catalogue[:6]` sans défilement** : plafond à 6 addons (5 aujourd'hui, des icônes pour
   8). Le 7ᵉ disparaîtra **sans un mot**.
8. **Les fenêtres secondaires sont en Tk gris/moutarde**, hors univers — et ce sont
   justement les deux moments d'inquiétude du joueur.
9. **La case « envoi automatique »** ressemble à une note de bas de page alors qu'elle
   commande un envoi de données par défaut. La vraie case existe :
   `Buttons/UI-CheckBox-Up` + `-Check`.

**Annexes repérées :** descriptions d'addons qui chevauchent leur bouton (« module manquant :
DragonUI_Options ») · « Tout lire ↗ » est le seul lien sans survol ni curseur main ·
`trad_verse` est un élément mort jamais renseigné.

## Ce qu'il faut savoir avant de commencer

- Le fichier est `WorkFlow/compagnon/interface_hub.py` (**2 211 lignes**).
- ⚠️ **Les décors sont cuits** : `fabriquer_decor_hub.py` génère les PNG. **Changer un
  libellé de bouton oblige à recuire.** C'est pour ça que des états sont devenus des boutons.
- Les assets officiels sont dans `WorkFlow/Ajouter par Dan/wow-ui-textures/`.
- ⚠️ **Les captures de `Design/captures_hub/` sont de millésimes mélangés** — seule
  `hub_addons.png` correspond au code actuel. Vérifier tout constat visuel **sur le code**.
- ⚠️ **Les polices du jeu n'ont ni `→` ni `↗` ni `✓`.** Tk les prend dans une police de
  secours, PIL non. Prévoir le repli, sinon on croit à un bug d'affichage qui n'existe pas.
- La maquette avant/après validée par Dan :
  `3-atelier/brouillons/2026-07-26_maquette_hub_avant_apres.html`.

## Un seul Hub, un seul numéro

Ce lot et la demande `2026-07-28_boucle-mise-a-jour-3.3.1.md` sortent **ensemble**, avec
l'addon 3.4. Aujourd'hui **deux Hub différents portent le numéro 3.3.1** : celui des joueurs,
et celui d'ici (qui contient déjà les réparations d'installation du 26/07). Le Hub qui sort
doit porter un numéro neuf, aligné avec la release, et le garde-fou de publication doit
refuser le décalage — c'est ce décalage qui a créé la boucle de mise à jour.

**Ne rien publier ici.** Le build fera l'objet d'une demande à part.

---

**« Terminé » veut dire :**

> - Les 9 points appliqués, décors recuits, le Hub s'ouvre et fonctionne.
> - **Les contrastes re-mesurés après, texte par texte** : plus aucun sous 4,5 pour 1.
>   C'est la seule preuve qui compte — pas « ça a l'air mieux ».
> - **Aucune régression** sur les réparations d'installation du 26/07 (« Vérifier mon
>   installation », correction du dossier, réactivation de la traduction, contrôle des
>   3 causes) : elles doivent toujours marcher, et être **visibles** cette fois.
> - Le catalogue défile, et un 7ᵉ addon apparaît au lieu de disparaître.
> - Des captures avant/après pour que Dan valide sans lire de code.
> - **Rien de publié, rien de poussé.**

**Validation :**

> Autonome sur les 9 points. **Arrête-toi et dis-le-moi** si un point oblige à retoucher la
> mécanique du Hub (mise à jour, installation, envoi de rapports) et pas seulement son
> affichage — on ne mélange pas une passe visuelle avec un changement de comportement juste
> avant une sortie.

---
## Réponse de Claude Code

**Fait le 28/07/2026**, en même temps que la demande boucle-mise-a-jour : un
seul Hub, numéro **3.4.0**, aligné avec l'addon.

### Les 9 points, un par un

1. **Plaque sous tout texte posé sur le bois** — la vraie plaque du jeu
   (`Tooltips/UI-Tooltip-Background` teintée du bleu nuit des infobulles +
   les 8 bords `UI-Tooltip-TL/T/…` — pas l'atlas `-Border`, qui est une
   autre pièce). Trois plaques : le **verdict d'accueil**, la **boîte à
   outils de Traduction** (dossier du jeu + « Changer… » + lien de mise à
   jour de l'appli + les deux liens de secours, regroupés à UN endroit,
   comme sur ta maquette), et la **note de bas de vue** des Voix. Les
   sous-titres de vue (Voix, Addons), eux aussi sur le bois (~3:1), sont
   cuits en beige vif + contour sombre — le traitement du jeu.
2. **Verdict d'accueil sur plaque + pastille** (`COMMON/Indicator-*`).
   Comme les 4 pastilles ont la même forme, c'est le TEXTE qui porte le
   sens (un daltonien lit la phrase, la bille n'est qu'un renfort) — et le
   lien de contrôle affiche désormais **le nombre de points contrôlés**
   (« Installation vérifiée — 5 points contrôlés ↗ »).
3. **Titres or vif + contour noir**, cuits en décors (`titre_*`), sans
   plaque — le fronton reste dégagé. **Sous-titres décollés** : +50 px
   (Voix) et +34 px sur décor cuit (Addons), plus aucun chevauchement.
4. **Le % des jauges remonté au-dessus** de la barre, en encre sur le
   parchemin : 9,5:1 (contre 1,2:1 sur le rail sombre).
5. **`txt_etat` a une largeur** : un message long passe en petite police et
   se replie sur deux lignes DANS la boîte crème au lieu d'en sortir.
6. **Les états ne sont plus des boutons** : « Tu es à jour » et « Voix
   installées » (images de bouton inertes) ont disparu — l'état vit dans le
   titre du panneau, le badge doré et la pastille. Et le rouge appartient à
   l'action principale : **« Couper les voix » est devenu un bouton neutre**
   (pierre désaturée), avec **sa conséquence écrite dessous** (« Couper
   repasse le jeu aux voix anglaises — rien n'est perdu, un clic les
   remet. »). « Remettre les voix » RESTE rouge : quand les voix sont
   coupées, c'est l'action principale.
7. **Le plafond `catalogue[:6]` a sauté** : les cartes vivent sur un canvas
   défilant (molette + flèches + pouce `UI-ScrollBar-*` du jeu, visibles
   seulement quand ça déborde). Preuve en capture : la démo Addons gonfle
   le catalogue à 8 fiches, la 7ᵉ et la 8ᵉ se défilent au lieu de
   disparaître. Au passage : le libellé long (« module manquant : … ») est
   borné au couloir libre — il ne passe plus sous le bouton de la carte.
8. **Les fenêtres secondaires** (Vérifier mon installation, Tout
   désinstaller, rapport) passent au **parchemin bordé d'or**, palette du
   Hub — plus de gris/moutarde aux deux moments d'inquiétude du joueur.
9. **La vraie case à cocher** (`Buttons/UI-CheckBox-Up` + `-Check`), en
   taille lisible avec un libellé complet (« Envoyer automatiquement ma
   récolte à chaque ouverture du Hub ») — plus de « [x] » en note de bas
   de page.

**Annexes traitées** : « Tout lire ↗ » a survol + curseur et passe à
l'encre soulignée (l'or sombre ne tenait que 3,5:1 sur parchemin) ; filet
`UI-TooltipDivider` sous « Dernières nouvelles » ; `trad_verse` (élément
mort) supprimé ; une pastille double aussi le verdict du panneau Traduction
et du panneau Voix.

### La preuve : les contrastes re-mesurés, texte par texte

L'outil n'existait pas — il existe : **`outils/mesurer_contrastes_hub.py`**
(méthode de l'audit écrite noir sur blanc : WCAG (L1+0,05)/(L2+0,05),
**pire décile** sur les vrais pixels du fond des captures — le bois est
bruité, la moyenne mentirait ; les textes contourés se mesurent contre leur
contour, qui porte la lisibilité). Il **mord** : code retour 1 au premier
texte sous 4,5:1 (3:1 pour les grands titres Morpheus).

**Résultat : 26 textes mesurés, TOUS au-dessus du seuil.** Les pires d'hier :
titre de vue 3,2 → **14,4** ; verdict d'accueil 1,4 → **6,3** ; « Vérifier
mon installation » 1,4 → **9,2** ; lien appli 1,4 → **8,2** ; « Tout
désinstaller » 1,7 → **5,1** ; chemin du dossier 2,7 → **7,6** ; note de
bas de vue 3,0 → **7,8** ; % de jauge 1,2 → **9,5** ; « Tout lire » 3,5 →
**6,9**.

### Garde-fous ajoutés

- **`verifier_decors.py` couvre enfin le Hub** (71 décors cités par le code,
  contrôlés manifeste + disque ; il ne couvrait que la v2 alors que l'exe
  distribué est le Hub depuis la 3.3.0).
- **`fabriquer_decor_hub.py` fusionne le manifeste au lieu de l'écraser** :
  `carte_ic_ascensionfr_peche`, `carte_ic_gbg` et `btn_carte_desinstaller`
  existaient sur disque SANS recette — une recuisson naïve les aurait fait
  disparaître du manifeste (et une icône hors manifeste n'est plus posée).
  `btn_carte_desinstaller` a maintenant sa recette.

### Captures pour valider sans lire de code

`3-atelier/brouillons/hub_avant_apres/` : `avant_*.png` / `après_*.png`
pour les 5 vues (la démo Addons montre le défilement à 8 cartes).

### Aucune régression sur les réparations du 26/07

La mécanique (contrôle des 3 causes, correction du dossier, réactivation,
désinstallation) n'a pas bougé d'une ligne — seule la présentation change.
`verifier_hub.py` (qui rejoue ces réparations sur un faux jeu cassé) :
**0 échec**. Et les liens qui y mènent sont enfin visibles (9,2:1 et 5,1:1).

### Vérifications finales

- pyflakes propre, `verifier_decors.py` OK, `verifier_hub.py` 0 échec,
  `mesurer_contrastes_hub.py` 26/26, `verifier_tout.py` code 0 (doctrine de
  version comprise).
- Exe recompilé (`AscensionFR_Hub.spec` → copié en
  `AscensionFR_Compagnon.exe`), zip reconstruit par
  `construire_zip_release.py`. **Rien n'est publié, rien n'est poussé.**

### Point resté ouvert (mineur)

Le nom « G.B.G — Glayna Better Guild » déborde sous son badge FR — sans
objet dès le bloc 2 du programme (retrait de tout Glayna).
