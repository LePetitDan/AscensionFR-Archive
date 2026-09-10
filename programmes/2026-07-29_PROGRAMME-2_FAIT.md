# Demande de code → Claude Code

# 📋 PROGRAMME 2 — les arbitrages rendus, et ce que l'audit a ouvert

**Date :** 2026-07-29

> **Le programme 1 est un travail remarquable, et je veux dire pourquoi précisément.**
> Les deux arrêts sur limite ont mordu **contre toi**, et tu les as respectés au lieu de les
> contourner — c'est exactement à ça qu'ils servaient. Tu as établi la provenance des
> 367 faux appariements par **preuve positive** et non par élimination. Tu as mesuré pour la
> première fois ce que le constructeur CoA affiche réellement (73,7 %) et posé un plancher
> qui passera au rouge si ça recule. Tu as **refusé ton propre correctif** quand
> `verifier_plaques` a mordu sur le ralentissement du repeint. Et tu as dit spontanément que
> ta première purge cosmétique attrapait 575 traductions légitimes, rattrapée par la
> sauvegarde. C'est cette dernière phrase qui vaut le plus : un rapport qui ne raconte que
> les succès n'est pas un rapport.
>
> Deux corrections que tu m'as apportées et que j'acte : **les gameobjects sont déjà
> couverts** (24 588 entrées) et **les astuces de chargement sont hors de portée d'un addon**.
> Elles sortent des listes.

---

## Les trois arbitrages de Dan

Mêmes règles que le programme 1 : **blocs indépendants, dans l'ordre, du sûr vers le
risqué**, chacun avec son « terminé » et sa condition d'arrêt. Réponse **bloc par bloc au fil
de l'eau**. **Rien de publié, rien de poussé.**

---

## BLOC A — Glayna, en deux temps *(l'arrêt du bloc 2a est levé, autrement)*

**Dan a choisi la troisième voie : on retraduit d'abord, on retire ensuite.**
Son raisonnement : « plus rien de Glayna » sans dégrader 788 noms pour ses joueurs. Et il a
levé l'urgence de sortie, donc le temps que ça prend n'est pas un argument.

1. **Retraduire les 788 noms** que seule la couche Glayna couvre encore — les **194 trous**
   (sinon anglais) et les **594 réparations** (sinon retour à « Un Pit de Snakes »,
   « Acid brûle », « Aeon d'Oblivion »). Par **notre** chaîne, avec :
   - le **normalisateur du glossaire derrière** (`appliquer_vocabulaire.py`) — c'est le moment
     où ce choix paie, comme au lot 13 ;
   - la **barrière du poison** en garde : aucune valeur sur-portée ne doit naître de cette
     passe ;
   - **un échantillon de 20 montré avant les 768 autres**, comme d'habitude.
2. **Puis retirer la couche** et tout ce qui va avec : `generer_noms_sorts.py` (4ᵉ couche),
   `adopter_noms_glayna.py`, `essai_sans_glayna.py`, `rapports/arbitrage_noms_glayna.txt`
   (⚠️ **grep qui le lit avant de le déplacer**), la source `AutoBookFR/`. **Archive, ne
   supprime pas.**
3. **« Smolder » reprend l'officiel** une fois la couche partie.

> **Terminé :** les 788 retraduits, comptes réels, la couche retirée, et **le compte des noms
> qui repassent malgré tout en anglais** (il devrait être proche de zéro — c'est la mesure qui
> prouve que l'opération a réussi).
> 🛑 **Arrête-toi si** plus de **50** noms restent en anglais après la retraduction : ça
> voudrait dire que notre chaîne n'a pas su faire ce que faisait la leur, et Dan doit le savoir
> avant de perdre la couche.

---

## BLOC B — Les objets : la limite est levée

**Dan a tranché : purge tout.** Son raisonnement, celui qu'il a déjà appliqué deux fois aux
sorts : un joueur qui lit un **faux** nom se trompe d'objet ; un joueur qui lit l'anglais sait
seulement que ce n'est pas encore traduit. Et un nom d'objet se voit partout — sacs,
info-bulles, hôtel des ventes.

Applique le plan que tu as préparé et arrêté : **3 109 `N` à retirer** dans `objets.json`
(958 familles), **105 paires fautives** au moulin, **1 065 entrées** qui perdent leur nom.
Garde des légitimes aux accents près, règle des 5, sauvegarde horodatée, contrôle **dans
l'addon**.

- La famille **« PH » (9 légitimes)** : tranche-la toi-même si tu es sûr, dis-le sinon.
- **Les 305 « hors source »** (officiel / récolte) : c'est le point d'écriture de la
  **génération** qui doit les refuser — la mécanique des interdits du bloc 4 s'y prête, tu
  l'as écrit toi-même. Pose-la.

> 🛑 **Arrête-toi si** une famille garde plus de **5** porteurs légitimes, ou si le total des
> entrées perdues dépasse **1 500** (mesuré à 1 065).

---

## BLOC C — Le clic droit de la minicarte

**Dan veut une confirmation.** Le clic droit ouvre une petite question — « Couper la
traduction ? » — avant de basculer. Le raccourci reste pour qui le connaît, mais on ne coupe
plus par accident. C'est le suspect n° 1 des joueurs qui « retombent en anglais ».

> Affichage pur, aucune globale écrite. 🛑 Si ça oblige à toucher un cadre protégé, **arrête**.

---

## BLOC D — Les trois propositions de ton audit

Tu les as chiffrées, Dan a dit « on améliore tout ». Fais-les.

1. **Le banc de santé qui mord**, branché sur la release. C'est la réponse au défaut
   structurel que tu as nommé : **les pannes de ce pipeline sont silencieuses**.
2. **La purge du poids mort.** **42 % du zip publié est un dossier de sauvegarde mort —
   19,5 Mo, déjà livré aux joueurs en 3.3.0.** Plus la file et les compteurs.
3. **Le vocabulaire arbitré branché sur le moteur principal.** Aujourd'hui le moteur ignore le
   glossaire : c'est ce qui fait revenir « rédiger » ou « Cils légers » à chaque passe neuve,
   et qui oblige à repasser le normalisateur derrière à la main.

---

## BLOC E — Ce que l'audit a trouvé de plus grave

- **9 bases ne sont régénérées par aucun chemin**, dont **`DB_LuesClient`** — la base
  anti-taint. C'est la même famille que le trou du pont des noms, en pire : celle-là protège
  les joueurs contre l'impossibilité de lancer leurs sorts. Branche-les, et vérifie qu'aucune
  autre n'est orpheline.
- **L'Atelier ignore les codes retour de ses 6 étapes** — un crash peut finir sur un bandeau
  vert. C'est exactement ce qui nous a fait croire pendant des jours que tout allait bien.
- **Les entrées de traduction partielles ne sont jamais retentées** — elles se perdent.
- **293 des 300 entrées de la barre « à traduire » sont insolubles** : le compteur ment.
- **Rien ne surveille le webhook entre deux versions**, et un échec d'envoi individuel est
  invisible côté usine. C'est l'alimentation du projet : rends-la observable.

---

## BLOC F — Le moteur d'alignement *(le chantier que tu as différé)*

Les **~457 échecs à la limite du moteur** (captures paresseuses qui absorbent le voisin quand
deux variables sont adjacentes). Tu as dit que tu n'y toucherais qu'avec la comparaison de
hachages sur la population entière comme condition de pose : **c'est le moment, et cette règle
tient.**

> 🛑 **Arrête-toi** si la comparaison de hachages montre **une seule** sortie dégradée qui
> n'était pas prévue. On ne troque pas 457 réparations contre une régression invisible.

---

## BLOC G — Les listes à trier *(classer, ne rien corriger)*

Quatre listes attendent l'arbitrage de Dan. **Ne les corrige pas — rends-les décidables.**
Sa règle : il tranche des **règles**, pas des cas. Groupe donc par familles, avec pour chaque
famille le nombre touché et un exemple.

1. **Les 81 divergences de vocabulaire** (bloc 9) — combien de règles générales couvriraient
   la majorité ? (« Battle Rush » vs « Ivresse de la bataille » : y a-t-il une famille
   « expression imagée officielle » contre « traduction littérale » ?)
2. **Les 51 corrections CoA suspectes** — ta détection par ancres numériques partagées est
   bonne. Mets-les en liste courte lisible, avec l'anglais, notre français, et pourquoi c'est
   suspect.
3. **Les 270 franglais du pont** — combien sont de vrais franglais et combien sont du
   sur-signalement (« gain » est aussi français) ?
4. **Les 5 705 divergences structurelles héritées** — c'est le plus gros nombre du projet.
   Classe-le : combien sont réparables mécaniquement, combien demandent un arbitrage, combien
   sont sans conséquence à l'écran ?

---

## BLOC H — Le courrier, la réputation, les monnaies

Tu as bien fait de ne pas les brancher en fin de bloc : **la matière existe, la surface
n'existe pas** — zéro handler `MAIL_*` dans l'addon. C'est un module d'interception à écrire,
doctrine des fenêtres maison.

Dan a dit qu'on faisait tout : **écris-le.** Le courrier d'abord (170 modèles, le français
attend dans le PackFR), puis la réputation (391 factions), puis les monnaies. Les 40 fêtes
suivent le même chemin que le courrier.

> 🛑 **La doctrine taint prime**, comme toujours : aucune globale relue par du code protégé.

---

## Après ces blocs

Dan teste en jeu, donne son go, et je t'enverrai la demande de build. **Ne rien publier,
ne rien pousser.**

Et la règle qui vaut depuis le début : **si tu vois une meilleure façon de faire que ce que je
décris, fais-la et dis-le-moi.**

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Renomme en `_FAIT.md` quand tout est terminé — ou dis
> simplement où tu t'es arrêté.)

### BLOC A — en cours (29/07) : la mesure, le plan, l'échantillon

**La liste est reproduite à l'identique : 194 trous + 594 réparations =
788.** Et j'ai retrouvé l'origine du « mesuré à 11 » du programme 1 :
**11 des 788 n'ont AUCUN identifiant porteur dans le dump Ascension** —
huit clés mortes (« Flamecastingd »…) et trois à apostrophe COURBE dont
le vrai nom (apostrophe droite) est déjà couvert par nos couches 1-3
(« Forgefiend's Bulwark » → « Rempart du démon des forges »). Ces 11
n'ont jamais rien affiché en jeu : la base de Glayna les portait pour
rien. Restent **777 noms réels**, dont **4 se règlent gratuitement par
l'officiel par TEXTE** (le chemin « réutilisé » de `resoudre` : « Rain
of Chaos » → « Pluie du chaos »…). **773 à traduire à la main.**

**Où la retraduction atterrit.** Le store `sorts.json["noms"]` contient
DÉJÀ 779 de ces clés — avec la valeur Google cassée (« Un Pit de
Snakes ») ou refusée par les gardes. Ma passe ÉCRASE ces valeurs à la
même clé : réparation à la source, pas d'ajout parallèle. L'écriture
passera par **la même barrière que `cycle_sorts`** (poison + seuil des
porteurs + parenté, refus bruyant), puis le normalisateur du
vocabulaire (`appliquer_vocabulaire.corriger`) repasse derrière, et
`polir()` s'applique de toute façon à l'entonnoir du pont.

**Les registres établis que je suis** (relevés dans le pont vivant,
pas inventés) : « Build: x » → « Construire : x » ; Mechsuit →
« méca-armure » ; Tithe → « dîme » ; Eldritch → « surnaturel » ;
Primal → « primordial » ; Aeon → « éon » ; noms propres intouchés
(Elune, N'Zoth, Yogg-Saron…) ; capitalisation française (majuscule au
premier mot, pas de Title Case) ; apostrophe droite.

**L'échantillon de 20, avant les 753 autres** (t = trou, r = réparation ;
la valeur cassée actuelle est entre parenthèses) :

| EN | Notre français |
|---|---|
| A Pit of Snakes (r : « Un Pit de Snakes ») | Une fosse aux serpents |
| A Pointed Death (r : « Un Pointed mort ») | Une mort acérée |
| Acid Burns (r : « Acid brûle ») | Brûlures d'acide |
| Aeon of Oblivion (r : « Aeon d'Oblivion ») | Éon d'oubli |
| Aeons of Conflict (r : « Aeons de Conflict ») | Éons de conflit |
| Absolute Power (r : « Absolute puissance ») | Pouvoir absolu |
| Adrenal Venom (r : « Adrenal venin ») | Venin adrénal |
| Adaptive Combatant (t) | Combattant adaptatif |
| Alacrity (t) | Alacrité |
| Ancient of War (t) | Ancien de la guerre |
| Ancestral Keg (t) | Fût ancestral |
| Abyssal Covenant Passive (t) | Pacte abyssal passif |
| Blood Rush (t) | Afflux de sang |
| Bomb Builder (r) | Artificier |
| Build: Sentry Turret (r) | Construire : tourelle sentinelle |
| Build: Spider Bomb Factory (r) | Construire : fabrique de bombes-araignées |
| Mechsuit: Artillery Rush (r) | Méca-armure : ruée d'artillerie |
| Primal Rush (r) | Ruée primordiale |
| Scythe Rush (r) | Ruée de la faux |
| Bulwark Rush (r) | Ruée du rempart |

Note sur la famille « Rush » : je m'en tiens à « ruée » (mouvement) et
« afflux » (montée de sang) SANS préempter ton arbitrage « Battle Rush /
Ivresse de la bataille » du bloc G — si tu tranches pour « ivresse » en
règle générale, une passe du normalisateur alignera ces noms-là.

Une perle vue en passant, HORS périmètre (ni 788 ni Glayna) : « Build:
Claw Bot » → « Build: Mechanolift » dans le pont vivant — un faux
appariement pur (le nom anglais d'un AUTRE sort comme « français »).
Je le note pour la liste des divergences du bloc G.

### ✅ BLOC A — terminé (29/07) : 770/788, la couche est partie

**La retraduction.** Les 773 restants traduits en éventail (16 lots de
~50, style et lexique imposés, exemples validés en tête de chaque lot),
puis TROIS gardes derrière : les valeurs PROPRES déjà présentes dans les
CORRECTIONS ont PRIMÉ sur mes traductions (68 cas — c'est notre chaîne
relue main, elle passe devant moi) ; ma relecture intégrale des 778
paires ; et la pose par un outil durable neuf,
`outils/poser_retraduction_noms.py` : sauvegarde horodatée,
normalisateur du vocabulaire, MÊME barrière que `cycle_sorts` (poison +
porteurs + parenté, refus bruyant). Bilan de pose : **745 remplacés, 1
refus de barrière** (« Sunder » → « Fracasser » : la valeur porte déjà
7 clés SANS parenté — du pur Google : « Shield Tossing » → « Fracasser » ;
la barrière a eu raison, la famille part au bloc G), 2 identités
écartées (Mak'Gora, Highlander), et **le verrou par clé a arrêté
« Smolder »** que l'éventail avait traduit « Incandescence » — attrapé à
la relecture AVANT la pose, le verrou servait de filet.

**Le vocabulaire m'a corrigé, deux fois.** D'abord « Alacrity » : j'avais
mis « Alacrité », la correction en jeu disait « Empressement » — elle a
primé. Ensuite un aveu : j'ai passé une heure à « aligner » « Mode JcE »
avant de découvrir que la règle arbitrée va DANS L'AUTRE SENS (JcJ/JcE →
PvP/PvE — tu gardes les termes que les joueurs emploient), et que mon
propre outil de pose l'avait appliquée correctement dès le départ. Tout
est revenu dans le sens de ton arbitrage : « PvE Mode » → « Mode PvE »,
partout (store, deux fiches de correction, récolte, liste relue).

**Deux correctifs mécaniques au passage, qui rapportent plus que le
bloc.** En diagnostiquant les restes un par un, deux défauts du PONT
lui-même :
1. **les divergences de pure casse** (« Bénédiction de vol'jin » vs
   « de Vol'jin ») neutralisaient ~20 noms — deux graphies du MÊME nom ne
   sont pas une divergence : la couche la plus haute garde la sienne
   (règle posée dans `poser()`, et dans le simulateur de
   `purger_pont_cartes.py` pour qu'il ne mente pas) ;
2. **18 noms dont les identifiants sont hors des cibles** de
   `generateur_sorts` n'avaient AUCUN chemin vers le pont → nouvelle
   couche 2bis : `traductions/noms_pont_retraduits.json`, la liste
   FERMÉE et relue du bloc A, jointe par texte, restreinte aux noms du
   dump — pas une porte pour le store entier et sa qualité Google.

**Le retrait.** Couche 4 retirée de `generer_noms_sorts.py` (elle posait
ses valeurs en CONTOURNANT poser() et ses gardes — c'est ainsi que
« Smolder » → « Braises » avait survécu au verrou) ; archivés dans
`archive/glayna/` : `adopter_noms_glayna.py`, `essai_sans_glayna.py`,
`arbitrage_noms_glayna.txt`, la source `AutoBookFR/`. Le grep préalable
a trouvé DEUX lecteurs à recâbler : le simulateur de
`purger_pont_cartes.py` (couche retirée de la simulation aussi) et
`mesurer_fiabilite_appariement.py` (regarde dans l'archive, saute
proprement si absent). **« Smolder » a repris l'officiel** (= identité,
donc absent du pont, comme Annihilation et les 31 autres).

**La mesure qui prouve. Pont régénéré SANS la couche : 72 827 paires —
PLUS qu'avec elle** (72 488), grâce aux deux correctifs. Sur les 788 :
**770 couverts, 18 « anglais » dont 11 clés mortes jamais affichées**
(Glayna les portait pour rien) — **7 restes réels, tous voulus** :
- Smolder, Highlander : identités officielles (leur français EST
  l'anglais) ;
- Bane, Blight, Rain of Chaos, Rocket Launcher : l'OFFICIEL Blizzard
  lui-même traduit ces noms différemment selon le sort (« Fléau »/
  « Plaie », « Lanceur de fusée »/« Lance-roquettes ») — un pont par
  TEXTE qui choisirait tromperait un sort sur deux ;
- Sunder : bloqué par la famille poison « Fracasser » (bloc G).

Le seuil d'arrêt (50) n'est pas approché. `verifier_addon` et
`verifier_tout` : **0 échec**. La vigie des porteurs : 270, INCHANGÉE —
la passe n'a créé aucune famille.

### ✅ BLOC B — terminé (29/07) : purge totale, et la porte est fermée

**Le plan s'est appliqué au chiffre près** : 3 109 N retirés
d'`objets.json` (958 familles), 105 paires fautives retirées du moulin,
1 065 entrées perdues en entier (< 1 500), sauvegardes horodatées à
chaque écriture. Les objets purgés repartent en file de traduction — la
voie du lot 13.

**« PH » : tranché, et je suis sûr.** Les 9 porteurs légitimes sont des
objets placeholder RÉELLEMENT nommés « PH » des deux côtés (aux espaces
parasites près — `plat()` les blanchit) : ils GARDENT leur nom. Un vrai
objet qui affichait « PH » à la place de son nom était précisément le
bug : ses minoritaires sont purgés comme les autres. La règle est posée
dans l'outil (`FAMILLES_TRANCHEES`), avec ta nouvelle limite (1 500) et
un arrêt dur si une famille > 5 légitimes NON tranchée se présente — il
ne s'en est présenté aucune.

**Les 305 « hors source » : refusés au point d'écriture de la
GÉNÉRATION**, comme tu l'as demandé — `traductions/objets_interdits.json`
(paires identifiant → valeur, donc une future traduction DIFFÉRENTE du
même objet passe sans obstacle), consulté par `generateur_db` en
balayage final AVANT l'écriture, quelle que soit la source qui re-pose.
L'outil de purge alimente ce fichier lui-même désormais.

**Le contrôle dans l'addon a mordu deux fois, utilement les deux.**
1. Premier contrôle : une paire purgée était REVENUE dans la base — une
   graphie voisine re-posée par une autre source que `polir()`
   transformait à l'écriture en la valeur interdite exacte. Le refus
   compare désormais aux accents/casse près (la doctrine même de la
   purge) et le cycle purge → régénération → contrôle a été REJOUÉ
   jusqu'au point fixe : **316 paires refusées à chaque génération, 0
   revenante, 0 échec** (60 identifiants purgés au hasard, les 9 PH, le
   témoin aux accents « Éclat du mépris »).
2. Deuxième leçon, à l'intérieur du contrôle lui-même : mon premier
   lecteur de la base paresseuse débordait sur les entrées VOISINES et
   inventait 17 fausses revenantes — borné à l'entrée exacte, il en
   restait 6 vraies (des variantes « @Mythique N@ » du même objet).
   Un compteur qui ment dans les DEUX sens en une seule soirée : c'est
   exactement pourquoi tes règles exigent de RECOMPTER après chaque
   passe.

**La vigie de la génération est passée de 1 019 familles / 3 794
minoritaires à UNE famille : « PH » (les 9 identités arbitrées).**
`verifier_addon` et `verifier_tout` : 0 échec.

Reste une queue de comète, notée pour le bloc G : des familles SOUS le
seuil de la vigie portent encore des appariements faux par variantes
(« Jambières de magistère » sur des torses « @Mythique 6/7@ » — même
objet, paliers différents). C'est la maladie de la jointure par texte du
moulin, pas celle de la sur-portée — un autre chantier, que je chiffre
au bloc G.

### ✅ BLOC C — terminé (29/07) : le clic droit demande avant de couper

Fenêtre MAISON dans `Modules/Minimap.lua` — pas StaticPopup, pour ne
rien écrire dans les tables du client : aucun nom global, aucun cadre
protégé, affichage pur. « Couper la traduction ? », deux boutons
(« Couper » / « Garder »), une ligne d'explication (« Tout repassera en
anglais, un /reload complète »).

**Asymétrie voulue** : seule la direction DANGEREUSE demande
confirmation. Rétablir la traduction (clic droit quand elle est coupée)
reste DIRECT — aucune friction pour revenir au français. L'infobulle du
bouton dit désormais « couper/rétablir la traduction » au lieu du flou
« activer/désactiver ».

Nouveau banc `outils/verifier_minimap.py` (moteur lua51 réel,
environnement factice) — le contrat en 12 assertions : la question
s'affiche SANS basculer, « Garder » ne coupe pas, « Couper » coupe,
le rétablissement est direct, le clic gauche ouvre les options sans
question, et le contrôle négatif : **la bascule silencieuse d'avant a
disparu — sans « Couper », jamais coupé**. 12/12, 0 échec.

### ✅ BLOC D — terminé (29/07) : les trois propositions sont posées

**1. Le banc de santé qui mord — `outils/banc_sante.py`, branché sur la
release ET sur l'horloge.** Six contrôles, un seul code retour honnête :
le banc MOTEUR population entière (seuil 1 200 — mesuré à 745 ; nouvelle
entrée `--banc-seul` dans l'outil de réparation, car la seule preuve
population entière vivait hors de toute routine) ; `verifier_addon` (le
seul test d'EXÉCUTION, qu'aucune release n'imposait) ; **la suite des 12
bancs, chacun avec son code retour ATTENDU** — l'infobulle attend 1 (le
rouge assumé du bloc 3) : un rouge NOUVEAU est enfin mécaniquement
distinguable d'un rouge connu ; le webhook des rapports (GET descriptif
sans rien poster : 401/404 = mort = ROUGE) ; la fraîcheur de la veille
(avertissement > 30 h, rouge > 78 h) ; et la santé du dernier passage de
l'Atelier (le fichier arrive au bloc E). Branché en DEUXIÈME BARRIÈRE de
`construire_zip_release` (verifier_tout compile, le banc de santé
EXÉCUTE), et sur l'horloge : tâche planifiée quotidienne 19 h 15,
relevé écrit sur disque (`rapports/banc_sante_dernier.txt`) — sous
pythonw il n'y a pas de console, le relevé fait foi. Premier passage
réel : 32 s, et il a MORDU du premier coup — webhook « HTTP 403 »… qui
s'est révélé être Cloudflare rejetant l'agent http par défaut sur un
webhook VIVANT : corrigé (User-Agent posé), et c'est exactement le genre
de faux-rouge qu'il fallait purger avant de crier pour de vrai.

**2. Le poids mort est purgé — le zip perd 43 %.** Nouveau garde dans
`construire_zip_release` : dans un arbre d'ADDON, seul entre ce que son
`.toc` déclare (+ le `.toc` et Bindings.xml) ; chaque écart est listé.
Écartés : les 26 fichiers de `DB_sauvegarde_build/` (les 19,5 Mo servis
aux joueurs depuis la 3.3.0), un vieux `.bak`, et mes propres
sauvegardes du jour. **46,8 → 26,6 Mo, 82 → 55 fichiers.** Les 31
quêtes-bruit : consignées UNE fois dans
`traductions/recolte_ecartes.json` (liste persistante, nouvelle
mécanique dans `ingerer_recolte`) — l'ingestion se tait dessus et ne
signale plus que le NEUF, qui lui est une vraie anomalie. Le filtre
`Name==""` de la file, lui, vit déjà depuis le bloc 2 du programme 1
(273 écartées à chaque génération). Les entrées PARTIELLES et les 15
rejets chroniques : bloc E, avec la mesure à blanc que tu imposes.

**3. Le vocabulaire arbitré gouverne le moteur principal.** Le
glossaire (jetons protégés avant Google, refus si jeton abîmé) est
extrait dans son module `outils/glossaire_jeu.py` — il vivait dans
`traduire_gisement`, que `traducteur_fr` ne pouvait pas importer sans
cycle — et `traducteur_fr.traduire_google` le passe désormais AVANT
chaque appel : « Haste » ne peut plus revenir « rapidité », « Mail » ne
peut plus revenir « courrier », sur AUCUN des six flux. Gain gratuit au
passage : un texte fait uniquement de termes protégés rend leur français
au lieu de rester anglais (« Haste » seul → « hâte »). Le cache existant
ne bouge pas d'un octet — la comparaison population entière n'a donc
rien à comparer : le branchement ne gouverne que les traductions
FUTURES. L'étape Atelier d'`appliquer_vocabulaire` arrive avec la
chirurgie du compagnon au bloc E (codes retour), pour ne l'ouvrir qu'une
fois.

### ✅ BLOC E — terminé (29/07) : les cinq trous graves sont bouchés

**1. Les 9 orphelines sont branchées — et plus AUCUNE ne peut naître.**
`mise_a_jour.py` porte désormais LA CARTE (`REGENERATEURS`) : les 26
bases du `.toc`, chacune avec son chemin de régénération — les deux
bases d'ACCUMULATION (corrections, communauté) y sont marquées comme
décision explicite, pas comme oubli. **`DB_LuesClient` — l'anti-taint —
est dans la section CRITIQUE**, juste après la liste noire dont elle
partage le danger (blocage des barres d'action) : son échec ANNULE la
mise à jour. Les autres (Reglages, Zones, Emotes, Épreuves, HautsFaits,
QuetesObjectifs, SortsLignes, AddonsTiers) tournent en fin de chaîne ;
leurs échecs n'interrompent pas le critique mais font échouer la mise à
jour À LA FIN, bruyamment. `verifier_tout` confronte la carte au `.toc`
et MORD sur toute orpheline ou entrée fantôme (« 26 bases, toutes
couvertes — OK »). Preuve par l'exécution : **les 10 chemins ont tourné
aujourd'hui, 10 × code 0** — les 9 orphelines sont régénérées fraîches.

**2. L'Atelier ne peut plus mentir.** `executer_flux` rend le CODE
RETOUR de chaque étape ; un échec est journalisé, versé dans
`rapports/atelier_sante.json` (que le banc de santé lit — la boucle du
bloc D1 est fermée), et **le bandeau final ne peut plus être vert
au-dessus d'un crash** — les regex du résumé ne décident plus que du
détail du texte, jamais de la couleur. Au passage, l'étape
« Vocabulaire arbitré » (D3) est entrée dans la chaîne, avant la
traduction des sorts. **L'exe du bureau de Dan est reconstruit** avec
tout ça (`Atelier AscensionFR.exe`, 20 h 38).

**3. Les partielles : mesurées à blanc… à ZÉRO.** La mesure champ par
champ sur les six files : 0 entrée vide (le filtre du bloc 2d a tari la
source — les « 278 » ont disparu aux régénérations du jour), 0 entrée
partielle, 0 doublon déjà traduit. Le chantier redouté (« potentiellement
des milliers de champs ») n'existe plus : la porte d'entrée était le
défaut, elle est fermée. Les 1 054 objets en file sont la purge du bloc
B repartie en traduction — le circuit prévu.

**4. Le compteur ne ment plus.** Les vides sont partis (point 3) ; les
**15 rejets déterministes** (Google fusionne `$b$b`, `codes_intacts`
refuse, mêmes textes depuis le 25/07) sont désormais CONSIGNÉS après 3
échecs dans `traductions/rejets_chroniques.json`, sortis de la file et
comptés à part (« +N insolubles consignés ») — `--retenter` leur redonne
leur chance. Un échec devient une INFORMATION, plus du bruit répété.

**5. Le webhook est observable de bout en bout.** Le GET du banc de
santé dit qu'il EXISTE (et il a fallu apprendre au banc le User-Agent —
voir bloc D1) ; le nouveau contrôle « collecte » dit que des rapports
joueurs ARRIVENT vraiment (avertissement au-delà de 7 jours de silence —
jamais rouge : la cadence appartient aux joueurs). Banc complet rejoué :
**0 rouge**, 32 s.

### ✅ BLOC F — terminé (29/07) : 745 → 508 échecs, 0 régression — et ta
### règle d'arrêt a mordu en chemin, utilement

**D'abord la dissection, pas la retouche.** Trace étage par étage des
745 échecs au moteur réel : **242 « incohérence de même variable »**
(LA signature des captures paresseuses : le partage faux d'une
adjacence donne deux valeurs à la même variable), 356 en AVAL de
l'extraction (structure du modèle FRANÇAIS — l'autre maladie, pas
celle-ci), 147 sans variable du tout.

**Le correctif est ADDITIF par construction.** Le motif historique
s'essaie d'abord, à l'octet près ; le REPLI ne se déclenche que là où
il rendait déjà nil (= anglais affiché). Deux mécanismes au repli :
1. **captures TYPÉES** — une variable numérique ($s1, ${...}, $<mult>)
   ne peut capturer qu'un nombre, une durée ($d) un nombre et son
   unité : une capture paresseuse ne peut plus absorber le voisin ;
2. **marqueurs par RANG** — @s:...@, @ext:, :ext@ ne sont pas des
   variables porteuses : le client y INSÈRE du contenu, différent d'une
   occurrence à l'autre ; exiger leur « cohérence » était le refus de
   86 sorts. Leurs contenus se consomment désormais par rang, comme les
   $l/$g.

**Ta règle d'arrêt a mordu au deuxième essai — et elle a eu raison.**
La comparaison population entière a montré **17 sorties DÉGRADÉES** :
quand le français a PLUS d'occurrences d'un marqueur que l'anglais, ma
pile s'épuisait et refusait ce que l'ancienne sémantique servait très
bien. Tout s'est arrêté là, le cas a été compris (pile épuisée → retour
à la valeur par nom, l'ancien monde exactement), et la passe a été
REJOUÉE en entier.

**Le verdict final, population entière (49 308 entrées) : 237 réparés
(anglais → français), 0 sortie commune changée, 0 dégradée — 745 → 508
échecs.** Les 508 restants ne sont PAS la limite des captures : ~340
tiennent à la structure du modèle français (la famille des 5 705
divergences structurelles — classée au bloc G) et ~150 à des modèles
sans variable qui échouent sur autre chose (longueur, normalisation) —
c'est le partage honnête entre ce que le moteur pouvait rendre sans
risque et ce qui relève des DONNÉES. Suite des bancs et banc de santé :
verts.

### ✅ BLOC G — terminé (29/07) : quatre listes, un document décidable

**Tout est dans `rapports/arbitrages_blocG_2026-07.md`** — des RÈGLES,
des comptes, des exemples, une recommandation par règle. Rien n'est
corrigé. L'essentiel :

**Liste 1 — les 81 divergences officielles tiennent en 7 RÈGLES.** Les
deux grosses : « synonyme/expression imagée, les deux corrects » (35
cas — recommandation : l'officiel par défaut, avec ton veto ponctuel) et
« accents sur majuscules / apostrophe courbe » (18 cas — garder le
nôtre, c'est ta décision des 402 déjà écartés ; le filtre sera élargi
pour qu'ils ne remontent plus). Plus : 8 faux amis où l'officiel a
raison (« Rétribution » → « Vindicte »), 8 changements de catégorie
grammaticale, 5 « l'officiel n'est même pas du français » (garder le
nôtre), 5 PvP/JcJ (UNE décision projet), 2 abréviations Blizzard.
7 règles = 81 cas, somme vérifiée.

**Liste 2 — les 51 CoA suspects, relus UN PAR UN** (l'agent a rouvert
chaque fiche) : **43 CONTRESENS avérés** — presque tous des faux
appariements purs, le français d'un AUTRE talent (avec deux paires de
doublons révélateurs : 520686/520809 et 521211/521219 portent le même
faux texte) — et 8 douteux à vérifier en jeu. Liste en clair :
`blocG_coa_suspects.txt`. Règle proposée : purger le D des 43 (retour
de l'anglais juste + file de traduction), garder les 8 pour ton œil.

**Liste 3 — les « 270 franglais » : 150 vrais, 112 sur-signalés.** Les
vrais : mots-outils anglais purs (and 62, the 42, damage 11, within
10…), dont 124 servent l'écran aujourd'hui. Le sur-signalement est UNE
famille : « gain/gains » — échantillon de 10, 10/10 de français
légitime (« gains de réputation », « le gain d'âme »). Une règle
chacune : purge + refile pour les vrais ; retirer gain/gains de la
vigie pour les autres.

**Liste 4 — les 5 696 divergences structurelles : le chiffre qui
décide est 270.** J'ai croisé chaque clé avec les bases vivantes :
**seules 270 SERVENT l'écran (5 %)** — les 5 426 autres sont des
entrées de cache DORMANTES, sans conséquence tant que le serveur ne les
réveille pas. Et les 270 se ventilent en 114 blocs `@ext:` inégaux +
73 marqueurs orphelins (réparables MÉCANIQUEMENT sous le garde-fou
fail→success) + 83 variables inconnues (la voie du lot 13 : purge +
refile). **Zéro arbitrage de vocabulaire là-dedans** : la seule décision
est d'autoriser les deux passes mécaniques.

En annexe du document : les perles vues en passant (« Build: Claw Bot »
→ « Build: Mechanolift », la famille « Fracasser », les « Jambières de
magistère » sur des torses Mythique).

### ✅ BLOC H — terminé (29/07) : les guichets sont ouverts

**La matière d'abord — et une correction d'audit à t'avouer.** Les
tables anglaises VIVANTES sortent du client (le dernier patch gagne) :
MailTemplate (sujets + corps), Faction (noms + descriptions),
Holiday (24 noms, 26 descriptions). Le français du courrier et des
factions vient du PackFR par ID, comme prévu. **Mais les fêtes n'y sont
PAS** — vérifié sur les 5 archives du PackFR : l'audit des ressources se
trompait sur ce point (comme pour les gameobjects, je préfère te le dire
que le maquiller). Leur français est donc passé par NOTRE chaîne : les
24 noms officiels posés main (« Fête des Brasseurs », « Sanssaint »,
« Bombance du pèlerin »…), les 26 descriptions traduites sous lexique
imposé et relues. Les MONNAIES, elles, n'ont AUCUN texte propre
(CurrencyTypes.dbc vide — l'audit avait raison là-dessus) : leurs noms
sont des noms d'OBJETS, déjà au pont.

**`DB_Guichets.lua` : 653 paires** (185 courrier + 420 factions + 48
fêtes), générées par le nouveau `outils/generer_guichets.py` — qui
ré-extrait lui-même les tables anglaises à chaque passage : après un
patch d'Ascension, le neuf entre tout seul. Base inscrite au `.toc`, à
la carte des régénérateurs (**27 bases, toutes couvertes**) et à la
chaîne des annexes de `mise_a_jour`.

**`Modules/Guichets.lua` : la surface, méthode sûre intégrale.** Quatre
guichets, un seul geste : REPEINDRE après que le client a peint
(hooksecurefunc sur ses fonctions d'affichage), jamais une globale
écrite, texte inconnu toujours intact :
- **courrier** : sujets et corps de la boîte + de la lettre ouverte ;
  et l'EXPÉDITEUR passe par le pont des créatures (« Rexxar » →
  son nom français) ;
- **réputation** : les noms des barres + le nom et la description du
  panneau de détail ;
- **monnaies** : repeintes via le pont des noms d'objets existant —
  zéro donnée neuve, juste la surface qui manquait ;
- **fêtes** : Blizzard_Calendar se charge À LA DEMANDE — le module
  guette son arrivée (ADDON_LOADED) et raccroche alors les pastilles
  des jours.

**Banc neuf `verifier_guichets.py` : 11 assertions, 0 échec** — dont le
contrôle négatif (un texte inconnu ne bouge pas), le test « traduction
coupée : rien ne bouge », le raccrochage tardif du calendrier, et un
contrôle de DOCTRINE : le module ne contient aucune écriture `_G[...]`.
Enrôlé au banc de santé.

Comme pour toute surface neuve écrite à froid, la vraie preuve sera ta
session en jeu — le banc simule les cadres de Blizzard, il ne les
remplace pas. Si un guichet reste anglais chez toi, c'est un nom de
cadre qui diffère sur Ascension : dis-le-moi, c'est une ligne à ajuster.

---

### 🏁 Bilan de fin du programme 2 (29/07)

**Les huit blocs sont allés au bout. Rien n'est publié, rien n'est
poussé.** Zip 3.4.0 reconstruit avec tout dedans (57 fichiers, 26,6 Mo —
43 % plus léger), les DEUX barrières franchies (verifier_tout + banc de
santé), 13 bancs verts + le rouge assumé.

**Les règles du programme ont mordu deux fois, et servi deux fois :**
la comparaison population entière du bloc F a attrapé mes 17 dégradés
avant qu'ils n'existent ; et la barrière des porteurs a refusé
« Sunder » → « Fracasser » au bloc A en révélant une famille poison.

**Ce qui t'attend, toi :**
1. **Ton test en jeu** — en particulier les guichets neufs (courrier,
   réputation, monnaies, calendrier) et la question du clic droit
   minimap ; puis ton go.
2. **Le document d'arbitrage du bloc G**
   (`rapports/arbitrages_blocG_2026-07.md`) : 7 règles pour les 81
   divergences, la purge des 43 contresens CoA, les 2 règles des
   franglais, l'autorisation des 2 passes mécaniques des structures.
   Chaque « oui » se traduit en une passe outillée existante.
3. Les dossiers hérités du programme 1 restent ouverts chez toi :
   Glayna soldé ici (bloc A) ; objets soldés ici (bloc B) ; minimap
   soldée ici (bloc C) — il ne reste QUE les arbitrages du bloc G.

**Un chiffre pour finir : le pont des noms de sorts compte 72 827
paires — plus qu'avec la couche communautaire — et plus une seule ligne
de ce projet ne vient d'ailleurs que de l'officiel Blizzard, du PackFR,
ou de notre propre chaîne.**
