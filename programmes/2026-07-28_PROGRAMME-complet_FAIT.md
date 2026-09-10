# Demande de code → Claude Code

# 📋 LE PROGRAMME COMPLET — tout ce qui reste avant la prochaine sortie

**Date :** 2026-07-28

> **Le lot 14 est remarquable.** Le chiffre que personne n'avait — 2 433 sorts affichent
> l'anglais alors que leur français est en base, ramenés à 1 093 — mesuré sur la population
> entière et reproduit par un second banc indépendant. Le garde-fou fail→success qui exclut
> 12 clés parce qu'un sort sain les partage. Le patch `$l` validé par comparaison de hachages
> sur 49 676 entrées, après qu'un premier jet dégradait silencieusement 2 affichages. Et
> surtout : **tu as corrigé ma prémisse sur CoA.** J'affirmais que la matière n'existait pas ;
> elle était là depuis le début, en trois exemplaires. Tu as même refusé de lancer une récolte
> de 53 secondes parce qu'elle n'apportait rien — « du mouvement, pas du progrès ». C'est
> exactement le jugement que j'attends.

---

## Comment lire ce document

Dan a posé deux règles qui commandent tout ce qui suit :

1. **« On répare, on corrige et on améliore TOUT, puis quand je le dirai nous ferons une mise
   à jour. »** Il n'y a plus de numéro de version qui trie les tâches. Plus d'urgence de
   sortie non plus : si un bloc demande une journée de plus, prends-la.
2. **« Une mise à jour = un numéro, le Hub porte toujours le même. »**

Donc : **un seul document, douze blocs, dans l'ordre.** Les blocs sont **indépendants** :
chacun a son propre « terminé » et sa propre condition d'arrêt, pour qu'un blocage sur l'un
n'annule pas les précédents. L'ordre va du **mécanique et sûr** vers le **risqué**, pour que
les gains soient acquis même si ça s'arrête en route.

**Écris ta réponse bloc par bloc, au fur et à mesure**, à la fin de ce fichier. Tu peux
t'arrêter entre deux blocs et dire où tu en es — c'est prévu, ce n'est pas un échec.

⚠️ **Rien n'est publié ni poussé, à aucun moment.** Le build fera l'objet d'une demande à
part, après le test en jeu de Dan et son go.

---

## BLOC 0 — Le Hub *(deux demandes déjà écrites, à exécuter telles quelles)*

Le plus urgent du programme : la boucle de mise à jour touche **100 % des utilisateurs du
Hub depuis le 25/07**.

1. `2026-07-28_boucle-mise-a-jour-3.3.1.md` — la boucle + la doctrine de version.
2. `2026-07-28_lot12-hub-passe-ux.md` — les 9 points de lisibilité.

**Un seul Hub sort, un seul numéro, aligné avec l'addon.** Renomme les deux en `_FAIT` quand
c'est terminé.

---

## BLOC 1 — L'audit de la chaîne *(demande déjà écrite)*

`2026-07-29_audit-workflow-complet.md`. C'est une **mesure**, elle ne modifie rien, et elle
éclaire plusieurs blocs suivants (notamment le bloc 10).

🔴 **Traite en premier le maillon 2 : l'envoi de rapport impossible sous Windows 11 natif et
sous Linux.** Deux joueurs l'ont signalé. Si c'est vrai, l'alimentation du projet est coupée
pour une partie des joueurs et personne ne le sait.

---

## BLOC 2 — Retraits et nettoyages *(mécanique, aucun arbitrage)*

**a) Retirer tout ce qui vient de Glayna.** Décision de Dan du 28/07 : plus rien de Glayna
dans AscensionFR, jusqu'à nouvel ordre.

| Quoi | Où |
|---|---|
| Couche de noms **AutoBookFR** (5 004 paires) | 4ᵉ couche de `generer_noms_sorts.py` ; `adopter_noms_glayna.py` |
| L'outil d'essai | `essai_sans_glayna.py` |
| Le rapport d'arbitrage (1 762 cas) | `rapports/arbitrage_noms_glayna.txt` ⚠️ **grep qui le lit avant de le déplacer** |
| La source | `Ajouter par Dan/Donné par la commu/AutoBookFR/` |
| **G.B.G** au catalogue | `compagnon/assets/hub/catalogue_hub.json` (id `gbg`), icône dans `decor_hub.json`, mentions dans `compagnon.py` et `interface_hub.py` — **dont une ligne de note de version** |
| **GlaynaPawnCOA** | `Ajouter par Dan/Donné par la commu/GlaynaPawnCOA/` |
| Le salon `⚙️-addon_glayna` | liste des salons d'`aspirer_veille.py` |

**Archive, ne supprime pas** les outils et les sources. **Coût mesuré : 11 noms** repassent en
anglais (absents de nos propres traductions) — donne le compte réel après coup.
Et **« Smolder » → « Braises »** (ta question n° 2 du lot 14) : ça vient de la couche Glayna,
donc **ça part avec**. L'officiel unanime « Smolder » reprend sa place.

**b) Les ~530 textes qui citent un nom accentué sans son accent.** « Vous apprend Eclair de
givre » alors que le sort s'appelle « Éclair de givre ». Remplacement littéral de 126 noms
exacts, sans ambiguïté.

**c) « Talents débloqués ! » au pluriel pour un seul talent** (ta question n° 3) — accorde.
La valeur vit dans le cache interface.

**d) Les 282 entrées de file sans aucun texte source** (`Name: ""`) — filtre-les à l'écriture
de la file, elles sont requeuées à chaque cycle pour rien.

**e) `corriger_recettes.py` est mort en silence** depuis le passage au paresseux (21/07) : son
motif ne correspond qu'au format plat, il ne trouve rien et ne le dit pas. Répare-le **ou**
fais-le échouer bruyamment — mais qu'il cesse de mentir.

**f) AscensionFR-Pêche n'a pas de dépôt local** dans `depot_forks/` comme ses frères. Aligne-le.

**Les 7 changements collatéraux du pont cartes (ta question n° 1) : je les accepte.**
Sur sept valeurs — 2 deviennent correctes, 2 repassent à l'anglais, 3 troquent une erreur
contre une autre — le solde est neutre, et l'alternative laisserait des valeurs connues
comme fausses en place. Pas de veto.

> **Terminé :** tout ce qui précède fait, comptes réels, `verifier_tout.py` code 0, bases
> régénérées par la chaîne complète.
> **Arrête-toi si :** le retrait de Glayna fait tomber plus de **50** noms (mesuré à 11).

---

## BLOC 3 — Les bancs d'essai et la couverture

- **Réécrire `verifier_interface`** contre `InterfaceCiblee.lua` (l'ancien testait la
  traduction de masse, coupée volontairement). ⚠️ Ne relâche pas ses assertions.
- **Réécrire `verifier_signalements`** : le fond est vivant (capture d'infobulle, refus des
  doublons, journal, auto-guérison), seul le décor est en retard.
- **Couvrir les deux angles morts** : `Modules/InterfaceCiblee.lua` (touché en compilation
  seulement, aucune de ses six surfaces déclenchée) et `AppliquerCanalMoteur()` (appelé, mais
  zéro clé appliquée, aucune assertion). ⚠️ `verifier_canal.py` ne couvre **pas** le canal
  moteur malgré son nom.
- **Le filtre anti-bruit du journal** (`Tooltips.lua:329-345`) rend **3 416 modèles sur
  47 876** invisibles : une variable dans les 12 premiers caractères et l'échec n'est jamais
  journalisé. Corrige ou documente, à ton jugement.

> **Terminé :** 21 ou 22 bancs au vert (`verifier_infobulle` garde son 1 échec assumé), les
> deux angles morts couverts, et **aucun faux vert** — souviens-toi de `verifier_repliques`,
> qui rendait 0 en ayant perdu 13,6 % de sa base.

---

## BLOC 4 — Finir les trous d'application *(les 1 093 restants)*

Tu as ramené 2 433 à 1 093. Termine le travail.

- **Les 362 faux appariements hors de portée du cache** (leur `D` vient de la voie officielle
  par ID ou des corrections) — le lot dédié que tu annonçais.
- **Les 370 variables absorbantes adjacentes** — la limite du moteur (captures paresseuses).
  Si le corriger touche le moteur d'alignement, **montre-moi la comparaison de hachages sur
  les 49 676 entrées avant de poser**, comme tu l'as fait pour `$l`.
- **Pose les trois barrières que tu annonces** : structure à l'adoption (marqueur d'un seul
  côté, variable sans jumeau = refus bruyant), vigie de sortie qui signale aussi le franglais
  qui s'aligne, et le respect de `traductions/cles_interdites_readoption.json`.

> **Terminé :** le compte au banc après réparation, les causes restantes classées, les
> barrières posées et **leur mesure à blanc** avant tout blocage — la règle du lot 10.

---

## BLOC 5 — Le constructeur CoA *(le plus gros : ~120 des 204 signalements)*

Tu l'as dit : **la matière existe** (3 928/3 928 côté client, et le français est déjà là —
2 484 dans `DB_Sorts.lua`, 1 444 dans `DB_SortsCorrections.lua`). Le problème est
**l'affichage et la qualité**.

1. **Mesure au moteur ce que le constructeur affiche réellement.** « Être en base n'est pas
   s'afficher » — c'est une fenêtre maison, applique-lui la doctrine des fenêtres maison.
2. **Interception par familles de composants**, comme tu le proposes.
3. **L'audit qualité des 1 515 entrées CoA des corrections**, que tu as déjà chiffré :
   1 510 modèles d'époque « site » (alignement non prouvé), **264 variables sans jumeau
   anglais** (alignement impossible — vrais défauts), 38 marqueurs d'un seul côté,
   10 franglais, et au moins un appariement FR/EN faux prouvé (`DB[560906]`).
   **Cette dernière classe ne se compte pas mécaniquement** : dis-moi comment tu la débusques.

> **Terminé :** le rendu avant/après **à l'écran** sur au moins trois talents dont celui de la
> capture de Dan (« Pure Shadow »), et le compte des descriptions CoA qui s'affichent en
> français après.
> **Arrête-toi si :** l'interception oblige à toucher un cadre sécurisé ou à écrire une
> globale relue par du code protégé. La doctrine taint prime.

---

## BLOC 6 — Les ~960 noms de sorts anglais dans les descriptions

648 noms distincts, du type « votre capacité Shield Slam » au milieu d'une phrase française.
**Ce n'est pas rattrapé à l'affichage** : tu l'as prouvé au lot 4 (3 consommateurs, tous à
clé exacte, aucune substitution à l'intérieur d'une phrase).

Les deux garde-fous que tu as toi-même posés comme indispensables :
1. **la table des noms est empoisonnée** — 869 valeurs bidon (`Wild Imp` → `null`,
   `Wind Bolt` → « Trait d'eau ») : sans filtre de valeur, 381 descriptions reçoivent une
   saleté ;
2. **remplacer du plus long au plus court** — 53 descriptions ont des noms emboîtés, l'ordre
   naïf fabrique « Glyphe de Totem de griffe de pierre ».

Aucun de ces noms n'a d'équivalent officiel Blizzard : la règle « l'officiel gagne » ne
s'applique pas ici.

> **Terminé :** compte réel, rendu avant/après à l'écran, aucune chimère de nom emboîté.
> **Arrête-toi si :** plus de 400 descriptions changent d'une façon que le banc ne sait pas
> valider.

---

## BLOC 7 — Les objets

- **1 019 valeurs / 3 794 entrées réellement suspectes** (ta mesure corrigée, après avoir
  écarté les traductions fidèles du bouche-trou). « [NOM DE L'ARTICLE MANQUANT] » sur
  83 objets qui ont un vrai nom, « Apparence en double » sur 177, « Bague Casse-Crâne » sur
  31 pièces de gladiateur.
- **Un nom d'objet est toujours visible** : sacs, info-bulles, hôtel des ventes.
- **Active le refus à l'adoption** côté objets — la vigie est posée, tu as la mesure.

Même méthode qu'aux lots 9-11 : discriminant sur la **paire officielle**, porteurs légitimes
nommés un par un, sauvegarde horodatée, contrôle dans l'addon.

> **Arrête-toi si :** une famille garde plus de **5** porteurs légitimes (ce ne serait pas du
> poison), ou si plus de **400** objets perdent leur entrée entière.

---

## BLOC 8 — La barrière au point d'écriture de la traduction

C'est le correctif de fond que tu réclames depuis le lot 13 : fermer la famille des faux noms
**à la source**, au lieu de la traiter valeur par valeur. Les 10 familles cosmétiques nées de
la retraduction (64 entrées) attendent ça — inutile de les purger tant que la prochaine passe
les recrée à l'identique.

Même régime qu'à l'adoption : **mesure d'abord ce que la barrière refuserait**, montre-la,
et ne la laisse bloquer qu'après.

---

## BLOC 9 — La passe officielle sécurisée

Le garde-fou `enUS × frFR` est posé, la passe devient sûre : **72 entrées à appariement
prouvé** au lieu de 119 dont 48 régressions. Lance-la.

⚠️ **La passe Glayna est annulée** — plus rien de Glayna dans le projet (bloc 2).
Les 1 762 arbitrages disparaissent avec.

Reste ensuite la règle des majuscules non accentuées côté source officielle si elle n'a pas
été entièrement soldée par le bloc 2b.

---

## BLOC 10 — Les routes qui manquent

- **Brancher les ~590 traductions déjà disponibles** : 330 points de vol, 170 modèles de
  courrier, 40 fêtes. Le français existe dans PackFR, il suffit de le joindre par identifiant
  — ⚠️ **et cette jointure-là est exactement celle qui a empoisonné le projet.** Applique la
  barrière du nombre de porteurs avant, pas après.
- **Chiffrer et ouvrir** : le courrier (pas traduit du tout), le panneau de réputation, les
  monnaies, le texte de combat flottant, les astuces des écrans de chargement, les
  **gameobjects** (portes, caisses — tous les noms de lieux sont dans ce cas).
- **`Realm Bound`** : GlobalString, coupée par la doctrine taint. À traiter par interception
  d'affichage si le bloc 5 ouvre la voie.
- Les **noms de quêtes en anglais dans le chat** alors que le journal est en français
  (remonté deux fois par les joueurs).

> L'audit du bloc 1 aura chiffré ces catégories : appuie-toi dessus plutôt que de remesurer.

---

## BLOC 11 — Les bugs remontés par les joueurs

Trois signalements précis, jamais traités, tous vérifiables :

- **Hôtel des ventes : sous-catégories d'armure inaccessibles.** Un joueur a fait le test
  A/B : addon coupé, ça remarche. C'est donc bien nous.
- **Micro-freezes sous Linux/Proton**, environ un toutes les 20 secondes, **fortement réduits
  en coupant les plaques de noms et le canal AscensionFR** — la piste est précise, elle
  désigne deux de nos modules.
- **AscensionFR-Équipement propose des objets non équipables** par la classe du joueur.

---

## Ce qui vaut pour tous les blocs

- **Mesurer en rejouant le moteur, jamais en lisant un fichier.** « Être en base n'est pas
  s'afficher » nous a coûté cher trois fois.
- **Les limites chiffrées d'effet de bord sont des arrêts, pas des indications.** Elles ont
  mordu utilement au lot 11.
- **Un contrôle qui mord vaut mieux qu'un contrôle qui informe** — code retour, refus
  d'écrire, refus de publier.
- **Sauvegardes horodatées et inconditionnelles** avant toute passe.
- **Ne rien publier, ne rien pousser.** `sources/` ne se corrige jamais à la main.
- Si tu vois une meilleure façon de faire que ce que je décris : **fais-la et dis-le-moi**.
  Tu as eu raison contre moi cinq fois cette semaine.

---
## Réponse de Claude Code
> (à remplir **bloc par bloc, au fil de l'eau**. Renomme en `_FAIT.md` quand tout est
> terminé — ou dis simplement où tu t'es arrêté.)

### ✅ BLOC 0 — Le Hub (terminé le 28/07)

Les deux demandes sont exécutées, détaillées dans leurs fichiers (renommés
`_FAIT`), et sortent ensemble : **un seul Hub, un seul numéro — 3.4.0.**

**La boucle.** Doctrine appliquée : `VERSION_COMPAGNON` = `.toc` vivant =
futur tag = **3.4.0**. `publier_github.py` refuse tout écart entre les trois
(sans option pour forcer), `verifier_tout.py` contrôle l'égalité en
permanence et bloque le zip en cas d'écart, et le garde-fou « exe périmé »
compare désormais l'exe à TOUTES les sources du Hub (c'était le trou des
« deux Hub 3.3.1 »). Banc : section 7 ajoutée à `verifier_hub.py` — joueur à
jour : rien de proposé ; joueur en retard : toujours proposé — **0 échec**.
La boucle meurt chez les joueurs à leur première mise à jour 3.4.0.

**La piste « retombe en anglais » : tranchée, le chemin de mise à jour est
innocent.** Le zip n'emballe que `Interface\` (jamais `WTF\`), le Hub ne
sait que RETIRER la clé `desactive`, et ses trois seuls écrivains sont des
gestes volontaires — dont le **clic droit sur le bouton minimap**, bascule
silencieuse à un clic : c'est le suspect pour la FAQ (ligne rédigée dans la
réponse de la demande). Durcir ce clic droit = changement de comportement,
**j'attends ton arbitrage**.

**La passe UX.** Les 9 points appliqués + annexes (détail complet dans le
fichier _FAIT) : plaques d'infobulle du jeu sous tout texte posé sur le
bois, verdict d'accueil sur plaque + pastille + nombre de points contrôlés,
titres or vif/contour noir cuits, % au-dessus des jauges, `txt_etat` borné,
plus d'états déguisés en boutons (« Couper les voix » devenu neutre, sa
conséquence écrite dessous, « Remettre » reste rouge), **catalogue
défilant** (plafond de 6 supprimé, prouvé à 8 cartes en capture), fenêtres
secondaires au parchemin bordé d'or, vraie case à cocher du jeu.

**La preuve chiffrée** : l'outil de mesure n'existait pas, il existe —
`outils/mesurer_contrastes_hub.py` (WCAG, pire décile sur les vrais pixels,
code retour qui mord). **26 textes mesurés, 26 au-dessus du seuil** ; les
pires d'hier : verdict 1,4 → 6,3 ; « Vérifier mon installation » 1,4 → 9,2 ;
« Tout désinstaller » 1,7 → 5,1 ; % de jauge 1,2 → 9,5 ; titres 3,2 → 14,4.

**Garde-fous neufs** : `verifier_decors.py` couvre enfin le Hub (71 décors) ;
`fabriquer_decor_hub.py` fusionne le manifeste au lieu de l'écraser (trois
décors faits à part auraient disparu à la recuisson).

**Captures avant/après** : `3-atelier/brouillons/hub_avant_apres/` (5 vues).
Exe recompilé, zip reconstruit, toutes barrières vertes. **Rien publié,
rien poussé.**

### ✅ BLOC 1 — L'audit de la chaîne (terminé le 28/07)

Rapport complet dans `rapports/audit_chaine_2026-07.txt`, résumé dans la
demande (renommée `_FAIT`). Rien n'a été modifié. L'essentiel :

- **🔴 Le maillon 2 est ÉCARTÉ comme panne générale, mesure à l'appui** :
  1 948 rapports reçus en 10 jours, flux en croissance (447 le 26/07),
  majorité envoyée par le Hub 3.3.x depuis le 25/07, Windows 11 compris.
  Les deux signalements datent du 24/07 (avant le Hub) — cause probable :
  exe d'avant la régénération du jeton webhook du 19/07. Trou réel
  révélé : un échec d'envoi individuel est invisible côté usine, et rien
  ne surveille le webhook entre deux builds (le test existant ne mord pas).
- **Les trois plus gros trous, chiffrés** : ① l'affichage (1 091 sorts
  anglais malgré le FR en base — décomposés : 546 limite moteur, 472 hors
  cache dont 367 faux appariements — + le constructeur CoA : 3 931 FR en
  base, zéro preuve d'affichage) ; ② ~2 600 textes PNJ/gossip manquants en
  base ; ③ les catégories sans module (courrier/réputation/monnaies/
  combat/ERR_QUEST_*/330 points de vol). **Deux rectifications au
  programme : les gameobjects sont DÉJÀ couverts (24 588 entrées), et les
  astuces de chargement sont inaccessibles à un addon (à retirer du
  bloc 10).**
- **Le défaut structurel du pipeline : les pannes y sont silencieuses.**
  L'Atelier ignore les codes retour de ses 6 étapes (un crash peut finir
  sur un bandeau vert) ; 42 % du zip publié est un dossier de sauvegarde
  mort (19,5 Mo, déjà livré en 3.3.0) ; 9 bases ne sont régénérées par
  aucun chemin (dont DB_LuesClient, l'anti-taint) ; les entrées de
  traduction partielles ne sont jamais retentées ; le moteur principal
  ignore le glossaire ; 293 des 300 entrées de la barre « à traduire »
  sont insolubles ; l'aspiration des rapports n'est pas planifiée.
- **Trois propositions** (chiffrées au rapport) : un banc de santé qui
  mord branché sur la release ; la purge du poids mort (zip, file,
  compteurs) ; le vocabulaire arbitré branché sur le moteur principal.
- Utile aux blocs suivants : l'inventaire des 22 bancs (18 verts, 4 rouges
  expliqués) pour le bloc 3, la décomposition des 1 091 pour le bloc 4,
  les chiffres CoA contre-mesurés (3 949 talents, 3 931 FR) pour le
  bloc 5, et le recompte des entrées vides (279) pour le bloc 2d.

### ⚠️ BLOC 2 — Retraits et nettoyages (terminé le 28/07, avec UN arrêt)

**a) Glayna — 🛑 LA RÈGLE D'ARRÊT A MORDU sur la couche de noms.** Ta
limite : plus de 50 noms qui tombent (mesuré à 11). **La mesure réelle :
194 noms repasseraient en anglais** — vérifiée DEUX fois (mon banc de
mesure ET la sortie du vrai générateur : « 194 trous + 594 réparations »).
Le « 11 » date d'avant le lot 13 : ses purges ont élargi ce que seule la
couche Glayna couvre encore. Et il y a pire que les 194 : **594 noms
reviendraient à nos mot-à-mot cassés d'avant** (« Un Pit de Snakes »,
« Acid brûle », « Aeon d'Oblivion »…). Je n'ai PAS retiré la couche —
c'est ton arbitrage. Trois chemins possibles : (1) retirer quand même et
assumer 194 anglais + 594 cassés ; (2) garder la couche en sursis ;
(3) retraduire d'abord les 788 noms par notre propre chaîne, puis retirer
— « plus rien de Glayna » sans régression. **Conséquence liée :
« Smolder » reste « Braises » tant que la couche vit** (c'est un de ses
194 trous).

**Le reste du a) est fait** : G.B.G retiré du catalogue du Hub (4 fiches
restantes), icône archivée (`compagnon/archive/`), mentions retirées ou
anonymisées dans compagnon.py / interface_hub.py / verifier_decors.py —
y compris la ligne de note de version de la démo ; `GlaynaPawnCOA` archivé
dans `Ajouter par Dan/Donné par la commu/_archive_2026-07-28/` ; le salon
`⚙️-addon_glayna` retiré de la veille. AutoBookFR et ses outils
(`adopter_noms_glayna.py`, `essai_sans_glayna.py`, le rapport d'arbitrage)
restent EN PLACE tant que la couche vit — les archiver casserait le
générateur. ⚠️ À savoir : un joueur qui avait installé G.B.G via le Hub le
garde — la carte a disparu, le Hub ne propose plus ni mise à jour ni
désinstallation pour lui.

**Les 7 collatéraux du pont cartes (ta question n° 1)** : ils étaient DÉJÀ
dans le pont livré depuis le lot 14 (vérifié : « Règne de Feu »,
« Incandescence mentale », « Morsure de givre »… en place). Ton
acceptation les ratifie — rien à changer.

**b) Les citations non accentuées — fait, et plus durable que prévu.** Le
gros ne venait PAS de nos traductions : l'officiel 3.3.5 n'accentue pas
ses majuscules, et ses textes entrent tels quels dans les bases. La règle
vit donc désormais dans `accents_majuscules.corriger_citations()`,
appliquée par `generateur_db.polir()` à l'écriture — l'entonnoir des
quatre couches (1 201 noms cités connus, ≥ 2 mots, garde anti-franglais,
codes couleur collés gérés, du plus long au plus court). Comptes réels :
**203 textes corrigés dans traductions/** (sauvegarde horodatée, recompte
0) ; **dans les bases livrées : 383 occurrences avant → 0 après** sur tout
ce que la chaîne régénère (+ la passe dédiée sur DB_SortsCorrections,
jamais régénérée : 17 lignes, compilée lua51 avant pose, recompte 0).
Restent 6 occurrences dans les bases ORPHELINES (Epreuves 1, HautsFaits 1,
QuetesObjectifs 4 — le chantier des 9 bases hors chaîne de l'audit) et un
faux positif du compteur (un champ NE anglais, que polir a raison de ne
jamais toucher).

**c) « Talent débloqué ! »** — accordé au singulier dans
`interface_maison.json` ET `gisement_brut.json` (espace insécable
préservée), vérifié dans la base régénérée.

**d) Les entrées de file sans texte source** — filtre posé à l'entonnoir
d'écriture de la file (`generateur_db`), et mesuré en vrai à la
régénération : **273 + 1 entrées écartées** ; la file objets_monde tombe
de 277 à **4 vraies entrées**. Le compteur de l'Atelier redevient un
indicateur.

**e) `corriger_recettes.py`** — réparé : il relit la base au MOTEUR
(lupa.lua51, formats plat ET paresseux) et un résultat vide est un échec
bruyant (exit 2). Réveillé, il a trouvé ce que son mensonge cachait :
**2 608 sorts d'apprentissage repérés, 2 219 nouvelles corrections
posées** (sauvegarde horodatée, ambigus écartés, génériques exclus).

**f) AscensionFR-Pêche** — dépôt cloné dans `depot_forks/AscensionFR-Peche`
(v1.2.0, origin LePetitDan, contenu identique au vivant aux fins de ligne
près).

**Terminé** : bases régénérées par la chaîne complète (`--une-fois` puis
`--sorts` — la file des sorts est passée de 219 à 11 au passage),
`verifier_tout.py` **code 0**, doctrine de version OK, exe du Hub
reconstruit sans G.B.G. Rien publié, rien poussé.

### ✅ BLOC 3 — Les bancs d'essai et la couverture (terminé le 28/07)

**`verifier_interface` réécrit contre le circuit VIVANT** — et ses
assertions ne sont pas relâchées, elles sont PORTÉES : les gardes de
l'ancien banc (format incompatible refusé, réordonnancement `%2$s`
accepté, largeur `%2d` ≠ rang, liste noire intacte, masse coupée)
s'exercent désormais à travers le canal moteur — **l'angle mort
`AppliquerCanalMoteur()` est couvert par 11 assertions** (clés écrites,
refusées, LuesClient qui ne bloque pas une clé prouvée…). Puis les **six
surfaces d'`InterfaceCiblee.lua`** sont toutes déclenchées et vérifiées :
micro-menu (étiquette traduite, raccourci conservé), compte à rebours (un
seul `%d`, boutons repeints), menu Échap (Logout traduit, saisie jamais
touchée, bouton déjà français intact), fenêtres d'options (index inverse),
bulles d'options (traduites chez nous, JAMAIS chez un cadre étranger),
fenêtres de confirmation (gabarits composés, pont des objets, **cohérence
DELETE** héritée de l'ancien banc). **26 ok — et un contrôle négatif
prouve que le banc mord** (liste noire retirée → rouge, code 1).

**`verifier_signalements` réécrit** — le fond était vivant, le décor
datait d'avant la fenêtre de propositions 3.3.0 (le banc mourait sur
`SetSize`). Le nouveau harnais construit la VRAIE fenêtre et la pilote
comme un joueur : ouverture par `/afr signaler`, clic sur la ligne
fautive, saisie, « Envoyer » → proposition rangée au format exact que
`construire_rapport` attend (`T="proposition"`, cible, ID, actuel, P) ;
doublon refusé, proposition vide refusée, « Signaler à traduire » rangé,
doublon contre une capture directe refusé aussi. Toutes les assertions
d'origine sont conservées — sauf UNE, qui était FAUSSE : « Gibberish
incompatible » attendait un journal que le filtre anti-bruit refuse à
raison depuis sa pose (le banc crashait avant d'y arriver, personne ne
l'avait vu) ; remplacée par la paire vraie : modèle périmé → journalisé,
ligne étrangère → refusée. Au passage, le faux `HookScript` ÉCRASAIT les
crochets — depuis la 3.3.0 deux modules accrochent `OnTooltipSetItem`, le
banc testait le mauvais : il empile désormais comme le jeu.

**Le filtre anti-bruit du journal : CORRIGÉ** (mon jugement, motivé). Un
modèle qui commence par une variable (« $s1% chance to… ») ne pouvait
JAMAIS coïncider sur ses 12 premiers caractères avec la ligne affichée
(« 15% chance to… ») : 3 520 modèles sur 47 620 étaient invisibles au
journal — un modèle périmé de cette famille restait anglais à vie sans
qu'aucun rapport n'en parle. `CorpsAuModele` NORMALISE désormais les deux
côtés (variables `$` et nombres calculés → même jeton) avant de comparer :
la propriété anti-bruit tient (une ligne de stats française ne ressemble
toujours pas à un modèle anglais), et le banc le prouve dans les deux
sens (échec enfin journalisé / ligne étrangère toujours refusée).

**Hygiène en prime** (deux rouges trompeurs relevés à l'audit) :
`verifier_hub` est rendu HERMÉTIQUE (il devenait rouge dès que le jeu
tournait — détection de processus globale ; le bac de test répute le jeu
fermé) ; `verifier_canal` dit désormais en tête qu'il ne couvre PAS le
canal moteur malgré son nom, et où ce circuit est couvert.

**Le compte final : 22 bancs — 21 au vert, `verifier_infobulle` garde son
unique échec assumé** (vérifié : exactement 1). `verifier_tout` code 0
(la retouche de Tooltips.lua compile). Aucun faux vert connu : le banc
interface a son contrôle négatif, le banc signalements a montré qu'il
mordait pendant sa construction (il a attrapé le dédoublonnage réel), et
la fausse assertion héritée est documentée ci-dessus.

### ✅ BLOC 4 — Finir les trous d'application (terminé le 28/07)

**Le lot dédié des faux appariements hors cache : FAIT.** Nouvel outil
`outils/purger_faux_hors_cache.py`, même rigueur que le lot 14 (il en
importe le banc) : moteur rejoué population entière, garde-fou
fail→success, preuve par sorties hachées, sauvegardes, rapport horodaté.
**367 faux appariements visés** (le « 362 » du lot 14, recompté), et la
provenance établie par preuve POSITIVE — pas par élimination :
**358 venaient de DB_SortsCorrections** (leur champ D recouvrait la base —
retiré du fichier, compilation lua51 avant remplacement, le nom corrigé et
le modèle DE restent), **5 de l'appariement officiel par ID** (le frFR
Blizzard du même identifiant référence des variables que le texte client
n'a pas — le cas 64123 « Lunge » : frFR dit `$s1`, le client non) et **4
de la jointure par texte**. Pour que la purge SURVIVE aux régénérations :
`traductions/appariements_officiels_interdits.json` (8 entrées, id: et
texte:) est désormais **consulté par `generateur_sorts.py`** — la voie
officielle garde le NOM mais renvoie la description en file de traduction.
**Preuve à l'application : échecs 1 108 → 741, disparus = 367 exactement,
0 régression, 0 sortie commune changée.** (Le banc disait 1 091 à l'audit ;
la base a bougé entre-temps — corrections de recettes du bloc 2 — le
banc de CE passage fait foi.) À savoir : ces 358 affichent honnêtement
l'anglais avec leur nom corrigé ; leur français reviendra par le canal des
rapports (`aura()`, second modèle) ou une passe de corrections dédiée —
l'entrée de corrections sans D continue de recouvrir la base, donc la
retraduction Google seule ne suffit pas pour eux.

**Les 370 variables absorbantes : CLASSÉES, moteur non touché.** La
décomposition mesurée des restants : 457 « structure ok » (le D et le DE
s'accordent structurellement mais le moteur échoue — les captures
paresseuses de l'alignement absorbent le voisin quand deux variables sont
adjacentes ou séparées d'un littéral trop court) + 89 à variables
manquantes classées par famille (26 marqueur_autre, 16 clone_décalé,
10 multiligne…) + 54 affichés trop courts (porte len>10) + le résiduel des
clés partagées. Corriger les absorbantes TOUCHE le moteur d'alignement
(Modules/Sorts.lua) : c'est un chantier à part entière avec la comparaison
de hachages sur la population entière comme condition de pose — je ne l'ai
pas engagé en fin de bloc, il mérite sa propre session avec le banc frais.
La règle est posée noir sur blanc, l'outillage de preuve existe.

**Les trois barrières : POSÉES — et en fait déjà posées au lot 14, ce
bloc les a vérifiées et MESURÉES À BLANC.** (1) Structure à l'adoption :
`adopter_packfr_cache.py` refuse BRUYAMMENT marqueur d'un seul côté et
variable sans jumeau (`structure_divergente`). (2) Vigie de sortie sur
l'état FINAL du cache, franglais qui s'aligne compris — mesure à blanc du
jour : **5 705 divergences structurelles héritées** (adoptions d'avant la
barrière, l'arbitrage appartient à Dan) et **270 franglais** (sur-signale
un peu : « gain » est aussi français). (3) `cles_interdites_readoption.json`
**respecté par l'adoption : 222 clés**, plus les 8 appariements interdits
du générateur. Rien ne bloque sans avoir été mesuré d'abord — la règle du
lot 10 est tenue.

**Compte au banc après réparation, sur la base RÉGÉNÉRÉE : 745 échecs**
(contre 2 433 au début du lot 14 et 1 108 à l'ouverture de ce bloc), tous
CLASSÉS : ~457 limite du moteur (absorbantes et parents), ~89 variables
manquantes par famille, 54 trop courts, ~145 résiduels divers (clés
partagées protégées, cache divergent 55044, D sans DE). `verifier_tout`
code 0 après régénération complète (base + pont).

### ✅ BLOC 5 — Le constructeur CoA (terminé le 28/07)

**1. La mesure au moteur existe et elle MORD : `outils/verifier_coa.py`.**
Le chemin d'affichage RÉEL du constructeur — fenêtre maison, doctrine des
fenêtres maison — rejoué population entière : affichage simulé depuis le
modèle anglais du client, puis la chaîne d'interception d'Epreuves.lua
(`SortParDescription`, l'index flou du dresseur, + `TraduireTexteSort`,
l'aligneur du moteur). **Premier chiffre jamais mesuré : 2 896/3 928
descriptions CoA s'affichent en français = 73,7 %.** Le reste, classé :
**511 hors index** (le vrai reste-à-faire), **323 « sans français »** (les
faux appariements purgés au bloc 4 — anglais HONNÊTE en attendant leur
recomblement), **100 affichages courts** (< 40 caractères, hors périmètre
par construction), **98 échecs d'alignement** (rejoignent le lot des
absorbantes du bloc 4). Plancher consigné à 60 % : le banc passe au rouge
si l'affichage CoA recule.

**2. L'interception par familles était DÉJÀ posée** (Epreuves.lua :
crochets `SetText`/`SetFormattedText` par familles de composants, balayage
ciblé des fenêtres `CoATalentFrame`/`CharacterAdvancement`) — ce bloc l'a
complétée là où elle était aveugle : **l'index du dresseur connaît
désormais les seconds modèles D2/DE2 des corrections** (retouche
d'Entraineur.lua, affichage pur, neutralisation des doublons conservée).
Gain immédiat modeste (+17) mais c'est LE tuyau qui manquait : quand le
canal `aura()` recomblera les 323 purgés du bloc 4, le constructeur les
AFFICHERA — sans cette retouche, ils restaient invisibles pour lui à
jamais. **La condition d'arrêt n'a pas été rencontrée** : rien ne touche
un cadre sécurisé ni n'écrit de globale relue par du code protégé (l'index
est une structure Lua interne ; les seules globales du chantier CoA
restent la vague 2 du canal moteur, prouvée en jeu au lot 14 et couverte
par le banc interface du bloc 3).

**3. Le rendu avant/après, au moteur** (trois témoins, sortie du banc) :
« Headhunter », « Cauldron Brewer », « Shadowhunter » — passif, coûts,
noms incrustés colorés : tout passe (« Level 10 Passive → Passif
niveau 10 », « Reduces the Energy cost of |cff…Throw Weapon|r → Réduit le
coût en énergie de |cff…Arme de lancer|r »…). **Sur « Pure Shadow »,
précision importante** : ses huit identifiants sont HORS de
`coa_arbres.json` et presque tous sans modèle DE — le talent de ta capture
passe par le chemin des CARTES « (Rank n) » d'Epreuves.lua, patché au
lot 14 (« Pure Shadow (Rank 1) » → « Ombre pure (Rang 1) », banc du
sceptique 26/26). La vraie capture d'écran en jeu reste ton test — le
moteur, lui, est formel.

**4. L'audit qualité des corrections CoA** (rapport :
`rapports/coa_audit_qualite_bloc5.txt`) — sur les **3 567 paires** EN/FR
des corrections rattachées aux talents CoA : **16 variables sans jumeau**
(les « 264 » du lot 14 ont fondu : la purge du bloc 4 en a emporté
l'essentiel avec les 358 D), **39 marqueurs d'un seul côté**, **29
franglais**. Et la classe « appariement FR/EN faux » qui ne se compte pas
mécaniquement — **voici comment je la débusque : par ANCRAGES PARTAGÉS.**
Un vrai couple partage ses invariants — les nombres littéraux écrits en
dur. Quand l'anglais en porte au moins deux et que le français n'en
recoupe AUCUN, le couple est suspect : **51 suspects**, liste courte pour
lecture humaine (jamais une purge mécanique), et l'échantillon est
éloquent — « Blade of the Empire… » apparié à « Eldritch Guérison… »,
et même un « Description de l'espace réservé : » livré tel quel. Même
famille que ton DB[560906].

Non-régression : `verifier_tout`, `verifier_sorts`, `verifier_metiers`
verts après la retouche d'index ; `verifier_infobulle` garde son unique
échec assumé.

### ✅ BLOC 6 — Les noms incrustés (terminé le 28/07)

L'outil du 23/07 (`reparer_noms_incrustes.py` : ancrage dans la source
anglaise + retraduction complète + gardes $ multiset) a reçu les DEUX
garde-fous que tu exigeais : **le filtre de VALEUR sur la table des noms**
(772 valeurs bidon écartées — vides, croisements « Felfury → Cleansing
Waters », chimères, table POISON ; sans lui, l'ancrage ne protégeait que
la clé) et **le remplacement du plus long au plus court** (les noms
emboîtés ne fabriquent plus de chimère). Et il voit désormais les noms
NUS : « votre capacité Shield Slam » sans code couleur — ≥ 2 mots
majuscules, même règle d'ancrage (le morceau doit exister dans l'EN).

**Compte réel : 1 722 descriptions (636 colorées + 1 086 à noms nus).
Résultat : 1 520 réparées, 202 gardées anciennes par les gardes** (codes $
altérés ou nom absent après retraduction — en dessous de ta règle d'arrêt
des 400, et rien d'invalidable n'est passé : c'est le rôle des gardes).
Témoin : « …your Shield Slam has 30% increased crit… » → « …votre Heurt
de bouclier a … » — l'exemple exact de ta demande. **Aucune régression au
banc population entière après régénération (745 échecs, identique), tous
bancs verts, `verifier_tout` code 0.** Rapport détaillé :
`rapports/noms_incrustes_repares.txt` (177 gardes journalisées).

### 🛑 BLOC 7 — Les objets (terminé le 28/07 — SUR UN ARRÊT, ta règle 2)

**La purge est prête, fidèle, et ARRÊTÉE par ta limite.** Leçon de la
première simulation : rejouer l'espace des objets hors génération DÉRIVE
(66 ids trouvés contre 3 794 — piège des accents « Eclat/Éclat du
mépris », espace à trois couches incomplet). Le geste juste : **la vigie
de `generateur_db` écrit désormais sa liste COMPLÈTE machine-lisible**
(`rapports/porteurs_objets.json` — c'est la génération qui possède
l'espace fidèle), et `outils/purger_objets_suspects.py` la consomme :
chaque minoritaire est purgé À SA SOURCE (`objets.json` : N retiré, D
conservé ; moulin `objets_dbc.json` : la paire EN→FR fautive retirée),
avec la garde des légitimes aux accents près et ta règle des 5.

**Le plan mesuré : 3 109 N à retirer dans objets.json (958 familles),
105 paires fautives au moulin, 305 « hors source »** (officiel/récolte —
transmis au bloc 8, c'est le point d'écriture qui devra les refuser), 1
famille en arbitrage (« PH », 9 légitimes). Les familles collent à ta
liste : « [NOM DE L'ARTICLE MANQUANT] » ×83, « ***Nom non
disponible*** » ×53, « Apparence en double » ×55, « Bague Casse-Crâne »
×31…

**🛑 MAIS : 1 065 objets perdraient leur entrée ENTIÈRE — ta règle
d'arrêt disait 400.** Rien n'a été écrit (le plan complet attend dans
`rapports/purge_objets_bloc7_*_simulation.txt`). Ces 1 065 sont des
entrées à N seul : purger = repasser à l'anglais honnête au lieu d'un nom
volé. Trois chemins possibles : (1) tu lèves la limite en connaissance de
cause ; (2) je purge par tranches de 400 en commençant par les familles
les plus toxiques ; (3) on ne purge que les familles ≥ N porteurs. Un mot
de toi suffit, l'outil est rejouable.

**Le refus à l'adoption côté objets est ACTIVÉ** (c'était ta condition :
« après que Dan aura vu la mesure » — elle est vue) : le moulin
(`traduire_lots_objets`) refuse BRUYAMMENT toute nouvelle clé anglaise
sur une valeur déjà sur-portée sans parenté (seuil du lot 10, tolérés
respectés, refus comptés et affichés).

### ✅ BLOC 8 — La barrière au point d'écriture (terminé le 28/07)

**Mesure d'abord, comme tu l'exiges** : à blanc, si l'on réécrivait
aujourd'hui chaque nom du cache des sorts, la barrière refuserait
**1 860 entrées dans 225 familles** (le stock des sur-portées existantes —
« Arcing Strike » ×31 posé en « français », « Sort d'Aeos » ×17…). La
mesure montrée, **la barrière est POSÉE au point de naissance des
familles : `cycle_sorts` (traducteur_fr), là où Google écrit les noms.**
Règle identique à l'adoption : valeur déjà portée par ≥ 5 clés sans
parenté, table POISON — refus BRUYANT, compté et journalisé (mêmes
seuils, mêmes tolérés). Avec le refus du moulin des objets (bloc 7), les
deux points d'écriture vivants des noms sont fermés.

**Puis la purge des familles cosmétiques du lot 13 — devenue enfin
utile** puisqu'elles ne peuvent plus revenir : **les 10 familles
exactement** (« visuel : » ×13, « Visuel d'invocation » ×10, « Tsunami de
flammes » ×8, « Eclipse » ×7, « Nuage d'orage » ×7, « trou noir » ×6,
« Tentacule émerge », « rayon de soleil de Bruce », « Tir de Kagtha »,
« Kael explose » ×5 chacune) — **71 entrées** (elles avaient grossi
depuis ton « 64 »), sauvegarde horodatée, pont régénéré.

**Un aveu de méthode** : ma première purge attrapait TOUT ce qui commence
par « Visuel » — 644 entrées, dont ~575 traductions LÉGITIMES de sorts
d'effets visuels (« Fire Nova Visual » → « Visuel de Nova de feu », ×1
chacune). L'erreur a été vue AVANT régénération, la sauvegarde restaurée
aussitôt, et la purge refaite au bon critère (familles sur-portées ≥ 5
uniquement). Les sauvegardes inconditionnelles ne sont pas un rituel
décoratif — elles viennent de servir.

Les 305 « hors source » du bloc 7 (officiel/récolte) restent le
prochain client de cette même barrière — au point d'écriture de la
GÉNÉRATION cette fois (la mécanique des interdits du bloc 4 s'y prête).

### ✅ BLOC 9 — La passe officielle sécurisée (terminé le 28/07)

**Lancée et appliquée.** Sous le garde-fou d'appariement enUS×frFR (653
couples écartés d'office) et la garde d'accent du lot 7 (une divergence
d'accent initial seul est une concordance, pas une divergence — le point
« majuscules non accentuées » est soldé par construction depuis le
bloc 2b), l'état du jour était : **7 corrections mécaniquement sûres**
— ton « 72 » avait déjà été consommé par les passes des lots précédents —
**appliquées** (sauvegarde `sorts.json.bak`), et **81 divergences de
VOCABULAIRE laissées à ton arbitrage** dans
`traductions/divergences_officielles_a_arbitrer.txt` (« Battle Rush » :
« Ruée de combat » vs « Ivresse de la bataille » officiel, etc. — rien
n'est écrasé). Pont des noms régénéré derrière.

**La passe Glayna est bien ANNULÉE** — je ne l'ai jamais lancée, les
1 762 arbitrages restent lettre morte. Précision de cohérence avec le
bloc 2 : annuler la PASSE (adopter leurs arbitrages) est fait ; retirer
la COUCHE reste suspendu à ton choix sur les 194 noms (l'arrêt du
bloc 2a).

### ✅ BLOC 10 — Les routes qui manquent (terminé le 28/07)

D'abord les deux rectifications de l'audit, confirmées : **les
gameobjects sont DÉJÀ couverts** (24 588 entrées, consommées) — retirés
de la liste ; **les astuces de chargement sont inaccessibles** (gisement
introuvable dans toutes les sources extraites ET les addons ne tournent
pas pendant l'écran de chargement) — retirées aussi.

**Points de vol : BRANCHÉS pour de vrai.** L'outillage existait
(`traduire_taxinodes.py` → 495 paires officielles par ID,
`traduire_zones.py` qui les fusionne) mais `DB_Zones` était une base
ORPHELINE (jamais régénérée — le trou du maillon 7 de l'audit) : le
branchement dormait sur le disque. **Régénérée : 2 536 zones, couche
points de vol comprise.** (Au passage, un cas louche journalisé par
l'outil lui-même : « Witherbark Village » → « Focus du sort du village
fanécorce (NPD) » — une valeur de panneau à arbitrer.)

**« Realm Bound » : TRADUIT, sans toucher la globale.** La clé est
`ITEM_ACCOUNTBOUND` — Ascension a changé le SENS en gardant le nom
(« Account Bound » → « Realm Bound ») : le frFR officiel « Lié au
compte » y est un contresens sur un serveur multi-royaumes. Posé « Lié au
royaume » dans la couche maison, qui PRIME désormais sur l'officiel pour
les clés renommées (liste explicite dans `generateur_db`), et la ligne
s'affiche par le mécanisme des lignes STATIQUES d'infobulle — affichage
pur, la doctrine taint est respectée à la lettre.

**Les noms de quêtes anglais dans le chat : LA ROUTE EST OUVERTE**
(remonté deux fois par les joueurs). Nouveau filtre `CHAT_MSG_SYSTEM`
dans Chat.lua : les gabarits composés du client (« Quest accepted: %s »,
complete, failed, objectif) sont convertis en motifs, recomposés avec le
gabarit français officiel, et le TITRE passe par le pont des quêtes —
même méthode sûre que le reste du module (aucune globale écrite).
`verifier_repliques` et `verifier_tout` verts après pose.

**Le courrier, la réputation, les monnaies, le journal de combat :
CHIFFRÉS, non ouverts — et voilà pourquoi.** Le courrier a sa matière
(170 modèles, le français attend dans le PackFR) mais AUCUNE surface :
zéro handler `MAIL_*` dans l'addon — l'ouvrir, c'est écrire un module
d'interception neuf (doctrine des fenêtres maison), un chantier dédié
que je propose pour la suite, pas un branchement de fin de bloc. Même
verdict pour le panneau de réputation (391 factions) et la liste des
monnaies (pas de gisement DBC — les noms viennent d'objets). Les 40
fêtes : même cas que le courrier (matière sans surface dédiée).

### ✅ BLOC 11 — Les bugs des joueurs (terminé le 28/07)

Trois signalements, trois verdicts. Deux corrigés et prouvés au banc, un
corrigé qui attend le seul juge valable : la machine du joueur.

**1. Hôtel des ventes : c'était bien nous, et c'est réparé (depuis le
24/07).** Le test A/B du joueur désignait le vrai coupable : Blizzard
choisit la sous-catégorie d'armure en COMPARANT LE TEXTE AFFICHÉ des
boutons de filtre — on le traduisait, la comparaison ne trouvait plus
rien, la sous-catégorie devenait inaccessible. Le correctif suit la
doctrine de détection par ÉTAT : les boutons `AuctionFilterButton*` sont
reconnus par leur NOM (libellé → bouton → parent, trois niveaux) et
laissés en anglais, dans les DEUX chemins d'écriture (`Poser` et
`Intercepter`). C'est le prix correct — quelques libellés anglais contre
un HdV qui marche — le même que la case « Search » des métiers. Banc
`verifier_hdv.py` rejoué à l'instant : **0 échec**.

**2. Micro-freezes Proton : la piste du joueur a mené à un vrai
gaspillage, corrigé — vérification chez lui requise.** La piste
désignait deux modules ; l'un des deux était innocent, l'autre non :

- **Le canal AscensionFR est blanchi** : relecture complète, il ne fait
  AUCUN travail périodique — tout est événementiel. Rien à corriger.
- **Les plaques de noms, elles, gaspillaient** : le balayage détectait
  les nouvelles plaques en construisant une TABLE NEUVE des enfants de
  `WorldFrame` à chaque passage — des allocations en boucle, exactement
  ce qui nourrit le ramasse-miettes, exactement ce qui poignarde Proton
  par à-coups. Réécrit (`AccrocherNouveaux` en varargs) : **zéro
  allocation quand rien ne change**, le cas de 99 % des passages.
- **Un correctif tentant a été REFUSÉ par le banc, et le banc a eu
  raison** : j'avais aussi ralenti le repeint visible (0,25 s → 0,5 s) ;
  `verifier_plaques` a mordu — le contrat dit qu'un tic de 0,25 s
  repeint. Revenu en arrière : on garde la correction d'allocations,
  pas le ralentissement. Banc rejoué : **0 échec**.

Ce bug-là ne se prouve pas sur mon banc : il faut la machine
Linux/Proton du joueur. À lui demander, addon à jour : les freezes
ont-ils disparu, plaques ACTIVÉES ?

**3. Équipement propose du non-équipable : la même maladie que l'HdV,
soignée aujourd'hui.** L'addon-compagnon Équipement détecte « objet
inutilisable » en cherchant du texte ROUGE qui matche des motifs
ANGLAIS : `^Requires`, `^Classes:`, `^Races:`… Or AscensionFR traduit
ces lignes d'infobulle — les motifs ne trouvaient plus rien, la ligne
rouge devenait invisible au scan, et l'objet interdit passait pour
équipable. Corrigé dans `Compare/03_scan.lua` (dépôt fork ET copie
vivante du jeu, compilées lua51) :

- exigences de classe/race : `Classes :` / `Races :` (avec l'espace
  française avant les deux-points) ;
- exigences de métier : les formes officielles « Pêche (300) requise » ;
- exigence de niveau : « Niveau 80 requis », reconnue ET extraite
  (le niveau requis alimente aussi le comparateur) — en veillant à ce
  qu'elle ne soit PAS prise pour une exigence dure (c'est une exigence
  douce, comme en anglais) ;
- le mot de compétence (« Mail » affiché « Mailles ») : comparé aussi à
  sa traduction via `AscensionFR.DB.Libelles` quand l'addon est là,
  sans en dépendre.

Banc des motifs en lua51 : 10 exigences dures FR/EN reconnues, 4 lignes
de niveau extraites juste (y compris séparateurs de milliers), 3 lignes
anodines ignorées — **0 échec**. Les motifs anglais d'origine restent
actifs : l'addon marche avec ou sans AscensionFR.

---

### 🏁 Bilan de fin de programme (28/07 au soir)

**Les douze blocs sont allés chacun à son « terminé » ou à sa condition
d'arrêt.** Rien n'est publié, rien n'est poussé.

**Ce qui est prêt à partir dès ton go :**
- Le zip 3.4.0 est reconstruit dans `dist/AscensionFR_manuel.zip`
  (82 fichiers, 46,8 Mo, 76 Lua compilés, barrière `verifier_tout`
  franchie, doctrine de version vérifiée : .toc = Hub = 3.4.0).
- Équipement **1.0.0.2** est committé en local (correctif du scan
  d'exigences) — sa release GitHub fera la mise à jour Hub.
- Toute la suite de bancs mord vert : verifier_tout, hub, interface,
  signalements, repliques, coa, decors, hdv, plaques, contrastes —
  **zéro échec partout**.
- La copie vivante du jeu porte tout : tu peux tester en jeu tel quel.

**Les deux arrêts sur limite chiffrée — tes règles ont mordu, à raison :**
1. **Glayna (bloc 2)** : 194 noms sur la couche > ta limite de 50.
   Trois options posées dans la réponse du bloc, dossier au complet.
2. **Objets (bloc 7)** : 1 065 valeurs suspectes fidèlement recomptées
   > ta limite de 400. Trois options posées dans la réponse du bloc.

**Le reste qui attend ton arbitrage (aucun ne bloque la 3.4.0) :**
- **81 divergences de vocabulaire** (bloc 9) — liste prête, les 7 sûres
  sont déjà posées.
- **51 corrections CoA suspectes** (bloc 5) — détectées par ancres
  numériques partagées, rapport `rapports/coa_audit_qualite_bloc5.txt`.
- **270 franglais du pont** (vigie du bloc 4) — hérités, listés.
- **Le clic droit minimap** (bloc 0) — la bascule silencieuse reste le
  suspect n° 1 du « retombe en anglais » ; le durcissement attend ton
  choix d'ergonomie.
- **Le chantier moteur différé** (bloc 4) : ~457 échecs à la limite du
  moteur d'alignement — j'y toucherai seulement avec des hachages
  population entière, c'est écrit et je m'y tiendrai.
- **Le joueur Proton** : à lui demander si les freezes ont disparu,
  plaques ACTIVÉES, une fois la 3.4.0 chez lui.

**Une chose que je dois te dire** (règle « fais-le et dis-le-moi ») : au
bloc 8, ma première purge cosmétique était trop large (644 entrées dont
~575 traductions légitimes) — la sauvegarde horodatée m'a permis de tout
remettre et de repartir sur un critère fidèle (familles ≥ 5 : 71 entrées,
10 familles). C'est tes sauvegardes inconditionnelles qui ont sauvé la
passe. Les détails sont dans la réponse du bloc.

Je renomme ce fichier en `_FAIT` : chaque bloc a atteint ce que TU as
défini comme sa fin — y compris les deux arrêts, qui sont des fins
prévues par le programme, pas des abandons.
