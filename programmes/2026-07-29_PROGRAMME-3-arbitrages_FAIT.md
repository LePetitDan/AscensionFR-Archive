# Demande de code → Claude Code

# 📋 PROGRAMME 3 — les arbitrages sont rendus, il n'y a plus qu'à appliquer

**Date :** 2026-07-29

> **Le bloc G a fait exactement ce que je te demandais depuis le premier jour : transformer
> des cas en règles.** 81 divergences ramenées à 7 questions, dont 6 se tranchent avec ce que
> Dan avait déjà décidé — il n'a eu qu'UNE décision à prendre. Et les 5 696 divergences
> structurelles ramenées à **270 qui servent l'écran**, avec zéro arbitrage de vocabulaire
> dedans : c'est le genre de mesure qui change un chantier en tâche.
>
> Deux choses que tu as dites de toi-même et que je veux relever, parce qu'elles valent plus
> que les chiffres : **les fêtes n'étaient pas dans le PackFR** contrairement à l'audit, tu
> l'as écrit au lieu de le maquiller — et l'heure passée à « aligner » JcE avant de découvrir
> que la règle allait dans l'autre sens. Un rapport qui ne raconte que les succès n'est pas
> un rapport.

---

## BLOC A — Les 81 divergences : les 7 règles, tranchées

| Règle | Décision | Qui a tranché |
|---|---|---|
| **1** — nos accents sur majuscules internes / apostrophe courbe (18) | **On garde le nôtre.** Et **élargis le filtre** pour que ces 18 ne remontent plus jamais. | Dan, le 26/07 (les 402 déjà écartés) |
| **2** — l'« officiel » n'est pas du français (5) | **On garde le nôtre.** Adopter reviendrait à retirer du français. | évident |
| **3** — JcJ contre PvP (5) | **PvP**, décision projet. | Dan, le 26/07 |
| **4** — « Ench. d'arme » (2) | **On adopte l'officiel.** Abréviation Blizzard employée par tous les autres enchantements, et contrainte de largeur réelle. | ta recommandation, je la suis |
| **5** — catégorie grammaticale (8) | **On adopte l'officiel.** Pure convention de forme, aucun sens ne change. | ta recommandation |
| **6** — faux amis (8) | **On adopte l'officiel.** « Rétribution » → **Vindicte**, « Défiance » → **Défi**, « Exécuteur » → **Bourreau**… Garder le nôtre entretiendrait de vrais contresens. | ta recommandation |
| **7** — synonyme ou image, les deux correctes (35) | **Dan a tranché : l'officiel par défaut**, avec **veto sur deux cas** — « Phase Out » reste chez nous (« Phase terminée » est plus faible) et « Insanity » reste chez nous (« Insanité » est un anglicisme). | **Dan, le 29/07** |

Si en appliquant la règle 7 tu tombes sur un autre cas où l'officiel est manifestement plus
faible que le nôtre : **ne l'applique pas, note-le.** Le veto de Dan porte sur le principe
« l'officiel sauf quand il est moins bon », pas sur une liste fermée de deux.

---

## BLOC B — Les 43 contresens CoA : purge

Ce sont des **faux appariements prouvés** — le français d'un autre talent. Un contresens se
corrige sans arbitrage, c'est la règle du projet. **Purge leur `D`** : l'anglais juste
revient, et la file de traduction fait le reste.

**Les 8 « douteux » : ne les touche pas.** Mets-les dans une liste courte que Dan vérifiera
en jeu — avec, pour chacun, ce qu'il doit regarder et où.

Les deux paires de doublons que tu as repérées (520686/520809 et 521211/521219 portant le
même faux texte) : dis-moi si elles désignent un mécanisme, ou si c'est le hasard.

---

## BLOC C — Les franglais : les deux règles

- **Les 150 vrais** (mots-outils anglais purs : `and` ×62, `the` ×42, `damage` ×11…), dont
  **124 servent l'écran aujourd'hui** : purge du `D` fautif + retour en file. La voie du
  lot 13.
- **Les 112 sur-signalés** : retire **`gain`/`gains`** de la liste des mots-outils de la
  vigie. Ton échantillon est net — 10 sur 10 étaient du français légitime.

---

## BLOC D — Les 270 divergences structurelles servies : les deux passes mécaniques

**Autorisées, toutes les deux.** Il n'y a aucun arbitrage de vocabulaire dedans, tu l'as
montré.

1. **114 blocs `@ext:` inégaux** + **73 marqueurs orphelins** → réparation mécanique sous le
   garde-fou fail→success du lot 14.
2. **83 variables `$` inconnues de la clé** → purge de la paire + retour en file (voie du
   lot 13).

**Les 5 426 dormantes : on n'y touche pas.** Ta mesure dit qu'aucune base ne les consomme.
Mais **note-les quelque part de vivant** — le jour où le serveur en réveille une, il ne
faudrait pas redécouvrir le problème de zéro.

> Preuve par hachages population entière avant pose, comme au bloc F. 🛑 **Arrête-toi sur une
> seule sortie dégradée non prévue.**

---

## BLOC E — Les perles vues en passant

- **« Build: Claw Bot » → « Build: Mechanolift »** au pont des noms : faux appariement pur.
  Corrige.
- **La famille « Fracasser »** : 7 clés sans parenté portent cette valeur, du Google pur.
  C'est la famille qui a fait refuser « Sunder » au bloc A. Traite-la comme les autres
  familles de poison — et regarde si « Sunder » peut alors reprendre sa place.
- **« Jambières de magistère » sur des torses « @Mythique 6/7@ »** : faux appariement par
  variantes de palier au moulin des objets, **sous** le seuil de la vigie. **Chiffre-le** —
  combien de familles, combien d'entrées, combien servent l'écran. Ne purge rien : si c'est
  gros, ça mérite sa propre passe avec ses propres garde-fous.

---

## Après ces quatre blocs

**Il ne reste plus rien entre nous et la sortie, sauf le test de Dan.**

Prépare-lui une **liste courte de ce qu'il doit regarder en jeu** — les surfaces neuves
surtout (courrier, réputation, monnaies, calendrier), les 8 CoA douteux, et le clic droit de
la minicarte. C'est le seul juge que ni toi ni moi ne pouvons remplacer.

**Ne rien publier, ne rien pousser.** Le build fera l'objet d'une demande à part, après son go.

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Puis renommer en `_FAIT.md`.)

### ✅ BLOC A — terminé : 49 adoptés, 32 gardés, 0 restant à arbitrer

**La partition d'abord, l'application ensuite.** Les 81 sont répartis nom
par nom entre tes 7 règles dans un fichier lisible et rejouable,
`traductions/divergences_officielles_decisions.json` (chaque entrée porte
sa règle, notre valeur, l'officiel, et le motif quand c'est un veto).
Contrôle : **81 couverts, 0 manquant, 0 doublon**. Répartition :
18 + 5 + 5 = **28 gardés** (règles 1-3), 2 + 8 + 8 + 35 = **53 adoptés**
(règles 4-7) **moins 4 vetos = 49 adoptés**.

**Le filtre est élargi, les 18 ne remonteront plus.** `corriger_tete()`
ne regardait que le PREMIER mot : « Apparition d'**É**tendard de
bataille » et « Échec d'**É**quilibre de la nature » portent leur accent
au deuxième — voilà pourquoi ces 18 avaient échappé aux 402 autres.
Nouveau `corriger_toutes_majuscules()` : la même règle appliquée à
CHAQUE mot de la table, plus la normalisation de l'apostrophe (l'officiel
écrit « Echantillon d’eau », courbe). La sûreté ne bouge pas d'un pouce —
c'est toujours une comparaison CONSTRUCTIVE (on fabrique notre graphie à
partir de l'officiel, on compare à l'identique), jamais la comparaison
accent-aveugle contre laquelle le fichier met en garde. Mesure : les
concordances passent de 402 à 421, et **les 18 sont dedans, 0 adoption
avalée au passage** (vérifié explicitement — une adoption absorbée par
le filtre aurait disparu en silence).

**Tes deux vetos sont posés, et j'en ai ajouté deux — tu m'as dit de le
faire, les voici pour que tu tranches :**
- **« Beatdown »** : je garde « Passage à tabac » contre « Massue ».
  L'officiel nomme un OBJET là où l'anglais nomme une ACTION — le sens
  se perd entièrement.
- **« Primal Instinct »** : je garde « Instinct primordial » contre
  « Instinct primal ». Deux raisons qui se cumulent : « primal » sent
  l'anglicisme (même famille que ton veto sur « Insanité »), et surtout
  **le registre `primal → primordial` a été posé au bloc A du programme 2
  et appliqué à ~15 noms** — adopter ici fabriquerait la seule exception.

**Un détail que j'ai tranché seul, dis-moi si c'était bien.** La règle 5
adopte « Crush » → officiel « Ecraser » — un E majuscule NON accentué,
c'est-à-dire exactement ce que ta règle 1 refuse. J'ai donc adopté la
FORME officielle avec NOTRE accent : **« Écraser »**. Le mot ne figure
pas dans la table des 55 accents (« Ecraseur » y est, pas
« Ecraser »/« Écrasement ») — c'est un petit trou de cette table, sans
conséquence ailleurs aujourd'hui, mais autant que tu le saches.

**Sept corrections en plus, hors des 81** : la famille « Bassin Arathi »
→ « bassin d'Arathi » (il nous manquait le « d' »), reconnue par
l'heuristique de défaut mécanique qui existait déjà. Total appliqué :
**56**. La passe est **idempotente** (deuxième passage : 0 sûre, 0 à
arbitrer) et le fichier d'arbitrage de Dan est **vide pour la première
fois**. Bases régénérées : DB_Sorts + le pont des noms (72 872 paires).

### ✅ BLOC B — terminé : 43 purgés, 8 gardés, et les doublons ont parlé

**La purge, et pourquoi ce geste-là.** `outils/purger_contresens_coa.py` :
42 entrées `DB[id]={…}` perdent leur **D seul** — elles gardent N et DE,
donc le module n'a plus de français pour cette description et le client
affiche son anglais, qui est juste. La 43ᵉ est une ligne `aura()` : mise
en **commentaire** avec sa raison, jamais supprimée.

**Et c'est ce détail qui rend la purge définitive.** `ingerer_rapport`
reconnaît un identifiant déjà corrigé en cherchant `DB[id]=` et
`aura(id,` dans le texte BRUT du fichier. Tant que la trace est là — y
compris en commentaire — un rapport joueur qui reproposerait la même
fausse correction ne peut pas la réécrire. **La barrière EST la trace** :
c'est la leçon du lot 13 appliquée sans écrire une ligne de code en
plus. L'outil refuse d'écrire si un seul identifiant perdait sa trace,
et compile en lua51 avant de poser. Résultat : **43/43 purgés, 43/43
traces conservées, 0 introuvable**.

**Les 8 douteux ne sont pas touchés** — ils sont dans la liste de fin
avec, pour chacun, quoi regarder et où.

**Les doublons : c'est un MÉCANISME, et il est mesurable.** J'ai compté
les valeurs `D` partagées par plusieurs identifiants sur toute la base
(1 570 entrées, 1 544 valeurs distinctes) : **23 partages, dont 9 où le
français est SPÉCIFIQUE** (il nomme un sort, codes couleur inclus). Ces
9 ont tous leurs porteurs à **moins de 2 000 d'écart d'identifiant** ;
**aucun** partage de texte spécifique entre identifiants éloignés. Sur
un espace d'identifiants qui va de 15 000 à 2,1 millions, ce n'est pas
le hasard : **les porteurs d'un même faux texte sont toujours voisins,
c'est-à-dire du même arbre de talents, donc de la même page du
constructeur.** La capture en jeu a lu l'info-bulle du VOISIN.

**La preuve la plus jolie est une famille que la purge a laissée
intacte** : « Frappe sauvage touche un ennemi supplémentaire » était
porté par 561110 (anglais : *Cutthroat*, purgé) **et** par 560344
(anglais : *Your Wild Strike now strikes 2 additional nearby enemies*).
Wild Strike = Frappe sauvage : **560344 est le propriétaire légitime, et
il a gardé son texte.** La purge a retiré le voleur et laissé le
propriétaire — exactement ce qu'on lui demandait.

**Une queue de comète, chiffrée, non purgée** :
`rapports/blocB_queue_doublons.txt` — **5 familles** où un porteur
condamné avait un voisin qui garde le même texte. La détection par
ancres NUMÉRIQUES ne pouvait pas les voir (elle compare des nombres, le
tell ici est un texte partagé). Sur les 5, une seule a un propriétaire
légitime identifié (celle ci-dessus) ; pour les 4 autres, les restants
sont probablement faux eux aussi — mais la preuve n'y est pas de la même
qualité que pour les 43, alors je ne purge pas et je te les pose.

### ✅ BLOC C — terminé : 150 purgés, 112 faux signalements éteints

**`gain`/`gains` sont sortis de la vigie**, avec la raison écrite dans le
code : ce sont de vrais mots français, ils faisaient **112 des 262
signalements** — un compteur qui crie faux 43 % du temps ne se lit plus.
La règle posée à côté, pour la suite : n'ajouter à cette liste que des
mots qui n'existent PAS en français.

**Les 150 vrais franglais sont purgés**
(`outils/purger_franglais_descriptions.py`). Le compte tombe pile sur la
mesure du bloc G : 150, dont **112 servaient l'écran**. Répartition :
`and` ×62, `the` ×42, `damage` ×11, `within` ×10, `you` ×8, `your` ×7,
`while` ×5, et 5 isolés. Ce sont des phrases à moitié traduites, du genre
« Using |cffffffffTorpille gangrenée|r twice in a row now increases the
damage… » — le joueur lit une bouillie ; l'anglais entier vaut mieux.

**La voie du lot 13, sans inventer de mécanisme.** La purge fait DEUX
gestes, pas un : la paire sort de `sorts.json`, ET sa clé anglaise entre
dans `cles_interdites_readoption.json` — la liste que
`adopter_packfr_cache` consulte DÉJÀ (222 → 371 clés). Sans le second
geste, le PackFR réintroduit tout au passage suivant et la purge est
défaite en silence : c'est exactement ce qui était arrivé au lot 14.

Vérifications : deuxième passage à **0 franglais**, et la régénération
montre les textes **revenus en file** (15 → 127 descriptions à traduire).
Au passage, j'ai exclu du compte les clés dont la STRUCTURE diverge —
elles relèvent du bloc D, les compter deux fois aurait gonflé le chiffre.

### ✅ BLOC D — terminé : 24 sorts réparés, 0 régression — et une mesure
### qui réduit le chantier de 270 à 42

**D'abord la mesure, comme toujours.** `structure_divergente` est une
barrière d'ADOPTION prudente, pas une preuve d'échec à l'écran. J'ai donc
demandé au moteur, pas au fichier : sur les **197 divergences servies**
(la mesure a bougé depuis le bloc G, les blocs A-C sont passés par là),
**144 s'affichent parfaitement**. Il n'y avait que **42 vrais échecs** :
27 « marqueur d'un seul côté », 10 « @ext: inégaux », 5 « variable
inconnue ». Le chantier tenait dans une soirée parce qu'on a mesuré au
bon endroit.

**Passe 1 — réparation.** Règle mécanique unique et prudente : les
marqueurs que le FRANÇAIS porte en trop sont retirés du français ; on
n'invente JAMAIS un marqueur absent (on ne saurait pas où le mettre).
Chaque réparation est ensuite jugée par le MOTEUR sous le garde-fou
fail→success : **17 recettes adoptées, 15 refusées par le moteur** — les
refus restent en l'état, pas question de forcer.

**Passe 2 — purge.** 4 « variable $ inconnue » sortent du cache ET
entrent dans la liste des interdites de ré-adoption (même geste qu'au
bloc C : la voie du lot 13 en entier, pas à moitié).

**Ta règle d'arrêt a mordu, et j'avais bien un défaut.** Premier essai :
**2 sorties saines changées** (2457, 13960) → tout s'est arrêté, restauré
(store ET base régénérée — la première restauration était incomplète, la
mesure suivante me l'a dit). La cause : j'avais oublié le garde-fou du
lot 14, **« un sort SAIN partage la clé »**. Une même description
anglaise sert plusieurs sorts ; réparer pour l'un déplace l'affichage de
l'autre, qui allait très bien. Garde-fou posé : **6 clés déclarées
intouchables**. Deuxième essai, population entière (48 993 entrées) :
**0 sortie commune changée, 0 dégradée, 24 sorts passés d'anglais à
français — 419 → 392 échecs.**

**Les 5 426 dormantes sont notées « quelque part de vivant »**, comme tu
l'as demandé : ce n'est pas un rapport figé mais une **vigie de la
génération** — `generateur_sorts` recompte à CHAQUE build et écrit
`rapports/structures_dormantes.json` (aujourd'hui : **5 500 dormantes,
183 servies**). Le jour où le serveur en réveille une, elle passe toute
seule de « dormante » à « servie » et le chiffre bouge sous les yeux : on
ne redécouvrira pas le problème de zéro.

### ✅ BLOC E — terminé : les trois perles, et ce qu'elles cachaient

**Perle 1 — « Build: Claw Bot ».** Corrigé en **« Construire : robot-griffe »**
(la description dit « Summon a Claw Bot… capable of tanking »). Mais le
vrai enseignement est ailleurs : le faux « Build: Mechanolift » venait du
**PackFR**, et il tenait parce que ce sort est HORS des cibles du
générateur — notre valeur n'atteignait donc jamais le pont. Réglé par la
couche 2bis, la liste fermée et relue créée au bloc A du programme 2 :
c'est exactement le cas pour lequel elle existe.

**Perle 2 — la famille « Fracasser », et « Sunder » retrouve son nom.**
Sept clés portaient cette valeur. Preuve d'abord : l'officiel Blizzard
écrit **« Sunder Armor » → « Fracasser armure »** — « Fracasser » EST le
mot du jeu, et « Sunder » son porteur légitime. Table POISON complétée,
**6 porteurs illégitimes purgés** (« Shield Tossing », « Static Pulse »,
« Stolen Flesh »…), **« Sunder » : « Fendre » → « Fracasser »**, accepté
par la barrière qui l'avait refusé au programme 2. La boucle est fermée.

**Et « Smash » m'a corrigé au passage.** Je l'avais déclaré porteur
légitime lui aussi — l'officiel le traduit **« Choc »** (sort 18944).
Notre « Fracasser » y était une divergence, et cette divergence faisait
TOMBER la clé du pont : « Smash » s'affichait en anglais. Notre valeur
retirée, l'officiel reprend la main : **« Smash » → « Choc »**. C'est ta
règle 6 appliquée là où je ne l'attendais pas.

**Deux trous trouvés en vérifiant le pont — et c'est la vérification qui
les a trouvés, pas moi :**
1. **« Crush » s'affichait « Ecraser » sans accent.** Cause : « Ecraser »
   et « Ecrasement » manquaient à la table des 55 accents (« Ecraseur » y
   était). Sans eux, la graphie non accentuée de l'officiel passait tout
   droit, malgré ta règle 1. Ajoutés — impact mesuré avant : 6 valeurs.
   Le pont dit maintenant **« Écraser »**.
2. **Tes 32 « on garde le nôtre » n'atteignaient pas le pont.** Quand
   deux couches divergent, le pont neutralise la clé — bonne règle tant
   que personne n'a tranché, mais ici TU AS TRANCHÉ : « Déphasage »,
   « Démence », « Passage à tabac », « Instinct primordial » tombaient
   quand même, et le joueur voyait l'anglais. Le fichier de décisions est
   désormais posé **en dernier mot** dans le pont (15 noms rétablis). Tes
   vetos existent maintenant à l'écran, pas seulement sur le papier.

**Perle 3 — chiffrée, rien purgé** (`rapports/variantes_objets_blocE.txt`,
outil `chiffrer_variantes_objets.py`) : **750 familles, 1 646 entrées**,
toutes livrées aux joueurs (la mesure part de la base LIVRÉE). Elles
comptent 2 ou 3 porteurs — donc **sous le seuil de la vigie (5), qui ne
les voit jamais**.

Et il y a **deux maladies dedans, pas une** :
- **~10 %** sont bien tes « variantes de palier » : `1310013`, `210013`,
  `310013` portent tous « Manteau de prophétie » alors qu'un seul l'est —
  les identifiants partagent leur FIN, c'est un préfixe de palier collé
  devant l'identifiant de base ;
- **~90 %** sont des faux appariements ordinaires, sans lien d'identifiant.

**Ce qui interdit une purge de famille** : les familles sont MIXTES. « Dard »
est porté par « Dart » (légitime), « Stinger » (légitime aussi !) et
« Golden Skill Card - Unbridled Wrath » (faux). Baisser le seuil de la
vigie à 2 détruirait de vrais homonymes français. **Ça mérite donc bien sa
propre passe**, avec une règle par ENTRÉE (comparer chaque nom anglais à
son français via le dictionnaire du moulin), pas par famille — c'est un
chantier à part entière, pas une fin de bloc.

---

### 🏁 Bilan du programme 3

**Les cinq blocs sont appliqués.** Rien n'est publié, rien n'est poussé.
Zip 3.4.0 reconstruit avec tout dedans (57 fichiers, 26,6 Mo), les deux
barrières franchies, banc de santé **0 rouge**, `verifier_tout` vert,
comparaison population entière **0 régression**.

Le compte des cinq blocs :

| Bloc | Fait | Chiffre |
|---|---|---|
| A | 7 règles appliquées + filtre élargi | 49 adoptés, 32 gardés, **0 à arbitrer** |
| B | contresens CoA purgés, barrière par la trace | 43/43, 8 douteux intacts |
| C | franglais purgés + vigie corrigée | 150 purgés, 112 faux signalements éteints |
| D | 2 passes mécaniques sous garde-fou | **24 sorts réparés, 0 régression** |
| E | 3 perles + 2 trous trouvés en vérifiant | famille poison fermée, 750 familles chiffrées |

**Ce que la vérification a trouvé et que je n'avais pas vu** — c'est la
partie du rapport qui compte :
1. le garde-fou « un sort SAIN partage la clé » oublié au bloc D — ta
   règle d'arrêt l'a attrapé sur 2 sorties ;
2. « Ecraser » sans accent au pont : un trou dans la table des 55 accents ;
3. **tes 32 « on garde le nôtre » n'atteignaient pas le pont** — la
   neutralisation des divergences les effaçait, donc tes vetos
   n'existaient que sur le papier. Le fichier de décisions est désormais
   posé en dernier mot ;
4. « Smash » que j'avais déclaré porteur légitime de « Fracasser » alors
   que l'officiel dit « Choc » — ta règle 6 m'a corrigé.

**Ce qui reste, et qui n'est plus à moi** : `1-pour-Dan/2026-07-29_a-tester-en-jeu.md`.

**Trois dossiers chiffrés, non ouverts** (chacun mérite sa passe, aucun
ne bloque la sortie) :
- les **750 familles / 1 646 entrées** de faux appariements d'objets sous
  le seuil de la vigie — règle par ENTRÉE nécessaire, les familles sont
  mixtes ;
- les **5 familles** de la queue des doublons CoA
  (`blocB_queue_doublons.txt`) ;
- les **15 réparations de structure refusées par le moteur** et les
  **5 500 divergences dormantes**, désormais recomptées à chaque build.
