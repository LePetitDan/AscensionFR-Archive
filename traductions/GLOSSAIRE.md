# Glossaire AscensionFR — les arbitrages de vocabulaire

Ce fichier recense les termes que le projet a **tranchés**, et pourquoi. Il ne
décrit pas un goût : chaque ligne a été appliquée aux fichiers de
`traductions/`, la plupart par une règle mécanique de
`chaine/outils/appliquer_vocabulaire.py`, qui est la source de vérité de ce
document.

Il s'adresse à qui reprend ces traductions pour un autre serveur WoW 3.3.5a.
L'essentiel du corpus n'est pas propre à Ascension — ce sont les textes de
WotLK. Les sections marquées **(Ascension)** ne vous serviront que si votre
serveur a les mêmes systèmes maison ; le reste vaut pour n'importe quel
serveur de la même version.

## La règle-mère

> **Quand notre traduction et le frFR officiel de Blizzard divergent,
> l'officiel gagne — sauf quand l'officiel perd une information.**
>
> *(arbitrage du 26/07/2026)*

On prend le mot de Blizzard quand c'est le même sort, le même lieu, le même
titre. On garde le nôtre quand l'officiel fait disparaître une précision utile
(couleur d'une monture, mention « (Animal) », détail d'un effet), quand il se
trompe de sort, ou quand il porte un artefact de rang (« Armure +8 » pour un
sort qu'Ascension a renommé « Armor (Light) »).

Corollaire pratique : **on ne pose de question qu'aux termes propres au
serveur**, ceux qui n'ont aucun équivalent officiel. Pour tout le reste, la
règle tranche seule.

Cette règle a été déclinée en sept règles d'application sur les 81 divergences
relevées entre nos noms de sorts et l'officiel. Le détail nom par nom vit dans
`traductions/divergences_officielles_decisions.json` : chaque entrée y porte
notre valeur, l'officielle, la règle appliquée et le verdict.

| # | Cas | Verdict |
|---|---|---|
| 1 | La divergence disparaît si on retire nos accents sur les majuscules et qu'on normalise l'apostrophe | **garder le nôtre** (18 cas) |
| 2 | L'« officiel » n'est pas une traduction (chaîne technique restée en anglais, ou texte d'un autre sort) | **garder le nôtre** (5 cas) |
| 3 | L'officiel écrit « JcJ » là où nous écrivons « PvP » | **garder le nôtre** (5 cas) |
| 4 | L'officiel abrège par contrainte de largeur (« Ench. d'arme ») | **adopter** (2 cas) |
| 5 | Même sens, même racine, seule la catégorie grammaticale change | **adopter** (8 cas) |
| 6 | L'officiel corrige un faux ami, ou emploie le terme exact du jeu | **adopter** (8 cas) |
| 7 | Les deux sont correctes, seul le synonyme ou l'image diffère | **adopter par défaut** (35 cas) |

Quatre adoptions ont fait l'objet d'un **veto** motivé (par exemple
*Beatdown* : l'officiel « Massue » nomme un objet là où l'anglais nomme une
action ; on garde « Passage à tabac »). Un veto se documente, il ne s'improvise
pas.

---

## 1. Termes propres à Ascension

Sans équivalent officiel : ce sont des choix, pas des restitutions. Vérifiez
d'abord si votre serveur a la même mécanique avant de reprendre la ligne.

| Anglais | Français retenu | Pourquoi / d'où il vient |
|---|---|---|
| Draft *(Build Draft, Draft Mode, draft cards, draft options)* | **Draft** *(on garde l'anglais)* | Nom de la mécanique, comme au jeu de cartes. Avait été rendu par « brouillon », « construction », « version préliminaire », « projet », « ébauche », « repêchage » — six mots pour une mécanique. Figé sur ~730 occurrences le 26/07/2026. |
| to draft *(le verbe)* | **composer** *(recomposer pour `redraft`)* | Seul le **verbe** se traduit ; le nom du mode reste « Draft ». Corrige « rédiger », « reformuler », « remanier », « réécrire », « redessiner » — tous des contresens produits par la traduction automatique. |
| Abyssal Draft | **Souffle abyssal** | ⚠️ **Rien à voir avec le mode Draft** : réactif d'artisanat où *draft* veut dire **courant d'air**. Sa famille le prouve : Droplet→Eau, Spark→Feu, Fragment→Terre, Draft→**Air**. Était livré « Draft abyssal ». Exclu de toutes les règles Draft. |
| Manastorm | **Tempête de mana** | Majoritaire dans nos propres bases (574 contre 266) et cohérent avec les autres lieux traduits (Stormwind → Hurlevent). ⚠️ « tempête » est **féminin** : « le Manastorm » donne « **la** Tempête de mana ». |
| Millhouse Manastorm | **Millhouse Manastorm** *(inchangé)* | ⚠️ C'est un **personnage** (le gnome de l'Arcatraz), pas le lieu. Blizzard le laisse tel quel. Corrige « Tempête de mana du moulin » — quelqu'un avait lu « mill house ». **Exclu de la règle Manastorm**, et la règle qui le restaure doit passer **après** elle, sinon on obtient « Millhouse Tempête de mana ». |
| Static *(ressource de classe)* | **Statique** *(majuscule)* | « Génère 20 **Statique** ». La majuscule dit que c'est une ressource et pas un adjectif. ⚠️ Sur 146 emplois de « Static » côté anglais, la **moitié seulement** est la ressource : le reste est un vrai adjectif français (« charge statique en arc »). On ne touche donc que les formes chiffrées et « All Static ». |
| Skill Card | **Carte de compétence** | |
| Golden *(Skill Card)* | **dorée** | « Golden Skill Card » → « Carte de compétence dorée ». |
| Lucky *(Skill Card)* | **chanceuse** | |
| Ability Essence | **Essence d'aptitude** | |
| Mystic Enchant | **Enchantement mystique** | |
| Wildcard | **Joker** | |
| Realm Bound | **lié au royaume** | Mécanique propre à Ascension, à **distinguer de** `Soulbound`. |
| Soulbound | **lié** | L'usage WoW habituel. |
| Keeper's Scroll | **Parchemin du gardien** | Minuscule à « gardien » : ce n'est pas un titre. |
| Azzar Faire / Faire Azzar | **Foire d'Azzar** | Nom propre de la fête foraine. Sans entrée de glossaire, la traduction automatique en produisait six formes (« foire Azzar », « Faire Azzar » inversé, ou l'anglais laissé). Les **deux ordres** sont protégés pour attraper la forme inversée. |
| Wildwood | **bois sauvage** | ⚠️ **Arbitré, jamais appliqué.** Signalé par un joueur (ticket #6) : sur 63 clés anglaises portant « Wildwood », les bases donnaient **sept** variantes — bois sauvage ×37, « Forestwood » ×12, « Wildwood » tel quel ×10, bois tendre ×1, bois de forêt ×1, bois forestier ×1, « forestière » ×1. La décision « bois sauvage » était prête et chiffrée (`programmes/2026-08-05_PROGRAMME-27-vider-la-table_FAIT.md`, bloc B.3) ; la fermeture des royaumes est arrivée avant la passe. **Les sept variantes sont encore dans les fichiers livrés.** |

### Classes et spécialisations *(Ascension)*

Le système d'Ascension est sans classes ; ces noms désignent ses archétypes.
Source : `chaine/outils/glossaire_jeu.py`.

| Anglais | Français | | Anglais | Français |
|---|---|---|---|---|
| Templar | Templier | | Stormbringer | Porte-tempête |
| Reaper | Faucheur | | Venomancer | Vénomancien |
| Primalist | Primaliste | | Chronomancer | Chronomancien |
| Wildwalker | Primaliste | | Necromancer | Nécromancien |
| Starcaller | Mande-étoiles | | Pyromancer | Pyromancien |
| Sun Cleric | Clerc du soleil | | Barbarian | Barbare |
| Tinker | Bricoleur | | Witch Doctor | Féticheur |
| Runemaster | Maître des runes | | Witch Hunter | Chasseur de sorcières |
| Felsworn | Gangrelige | | Knight of Xoroth | Chevalier de Xoroth |
| Bloodmage | Mage de sang | | | |

*Notes :* **Starcaller = Mande-étoiles** est le titre **officiel** Blizzard
(remplace « Héraut stellaire » / « Appelant des étoiles ») — premier cas réglé
par la règle-mère sans arbitrage. **Felsworn = Gangrelige** rejoint aussi
l'officiel : les créatures *Felsworn* de Blizzard sont déjà « Gangrelige de
Xavian ». Anciennement « Assermenté du Gangre » ; lors du remplacement, il a
fallu **protéger** « assermenté par la mort » (*Deathsworn*) et « assermenté à
la lame » (*Bladesworn*) en exigeant la phrase complète dans le motif.

⚠️ Un renommage de ce genre casse les **élisions** et les **pluriels** :
« de l'Appelant » → « du Mande-étoiles », « Les Appelants des étoiles » →
« Les Mande-étoiles ». Les pluriels ont été oubliés au premier passage et
rattrapés par un audit.

---

## 2. Vocabulaire WoW que la traduction automatique casse

Ces termes sortent du texte **avant** traduction (sous jeton `§n§`) et
rentrent en français arbitré après — sinon un moteur générique rend « Rage »
par « colère » et « Focus » par « se concentrer ». Implémentation :
`chaine/outils/glossaire_jeu.py` (`proteger_glossaire` /
`restaurer_glossaire`).

**Ordre obligatoire : les expressions longues d'abord**, sinon « Spell Power »
se fait manger par « Power ».

| Anglais | Français | | Anglais | Français |
|---|---|---|---|---|
| Runic Power | Puissance runique | | Holy | Sacré |
| Spell Power | puissance des sorts | | Shadow | Ombre |
| Attack Power | puissance d'attaque | | Frost | Givre |
| Critical Strike | Critique | | Arcane | Arcanes |
| Damage Dealer | Attaquant | | Fel | Gangre |
| Tank | Tank | | Armor | Armure |
| Healer | Soigneur | | Plate / plate | Plaques / plaques |
| Rage | Rage | | Mail / mail | Mailles / mailles |
| Mana | Mana | | Haste / haste | Hâte / hâte |
| Focus | Focalisation | | Resilience | Résilience |
| Energy | Énergie | | spell pushback, pushback | retard d'incantation |
| Stamina | Endurance | | near you | près de vous |
| Spirit | Esprit | | feared | apeuré |
| Strength | Force | | a stack of | une charge de |
| Agility | Agilité | | stacks of | charges de |
| Intellect | Intelligence | | stacking up to | se cumule jusqu'à |
| Felfury | Gangrefurie | | Hellfire Imp / Imps | lutin / lutins gouffre-feu |
| Demonfire | Feu démoniaque | | Hellfire Form | Forme gouffre-feu |

⚠️ **Le motif de protection est sensible à la casse.** « Mail » était protégé,
« mail » minuscule passait au travers, et la traduction automatique rendait
« courrier » / « envois postaux ». Les entrées en minuscules ci-dessus
existent pour cette seule raison — ne les supprimez pas en les prenant pour
des doublons.

⚠️ **Ne protégez pas les noms propres qui s'écrivent pareil dans les deux
langues** (Ascension, Azeroth, Elune, Manastorm). Un moteur les laisse déjà
tranquilles, et les mettre sous jeton l'empêche d'élider : on obtient
« le royaume principal **du** Ascension » au lieu de « d'Ascension ».

---

## 3. Termes rétablis vers l'officiel (valable pour tout serveur 3.3.5a)

| Anglais | Français retenu | Pourquoi |
|---|---|---|
| Arathi Basin | **bassin Arathi** *(sans apostrophe)* | Nom officiel. Ce qu'on supprime, c'est **l'apostrophe** de « bassin **d'**Arathi ». ⚠️ **On ne force pas la majuscule** : l'usage livré était à 185 minuscules contre 41, et « dans le Bassin Arathi » au milieu d'une phrase serait fautif. Le nom est le même dans les deux casses. Voir aussi le piège des deux officiels, plus bas. |
| Warsong Gulch | **Goulet des Warsong** | Nom officiel ; était resté en anglais. Attention à l'ordre des règles : « de Warsong Gulch » → « **du** Goulet des Warsong », « à Warsong Gulch » → « **au** Goulet des Warsong ». Le générique passe en dernier, sinon on écrit « de Goulet des Warsong ». |
| Stormwind | **Hurlevent** | Officiel ; 784 occurrences déjà présentes dans nos sources. |
| Booty Bay | **Baie-du-Butin** | Officiel ; 228 occurrences. |
| Stranglethorn | **Strangleronce** | Officiel ; 136 occurrences. |
| Darkmoon | **Sombrelune** | Officiel (la Foire de Sombrelune). Sert aussi aux cartes de compétence de Sombrelune. |
| Dreadnought / Dreadnaught | **Cuirassé** | Acté par cohérence : c'était déjà la traduction dans toutes nos sources. « Redoutable cuirassé » vu en jeu était une anomalie isolée. |
| Shanked! | **Coup de surin !** | Blizzard traduit *shank* par **surin** (6 objets officiels sur 7), mais jamais au participe — et « Suriner » est déjà le nom de *Gouge*. On reprend donc le substantif attesté. Avant : « Pourfendre », qui est la traduction de *Rend*. |
| Light Lash | **Fouet de Lumière** | ⚠️ Corrige un **contresens** : c'était « Cils légers » / « Cils clairs » — *lash* compris comme un cil d'œil au lieu d'un coup de fouet. Aligné sur la série existante : Lava Lash = Fouet de lave, Wind Lash = Fouet des vents, Ice Lash = Fouet de glace. |
| Unleash: *(mot-clé, suivi de deux-points)* | **Déchaînement :** | Mot-clé de mécanique en tête de ligne : un **nom**, comme en anglais. |
| Unleash *(verbe dans une phrase)* | **Déchaînez / Déchaîner** | ⚠️ **Les deux cas ne se traduisent pas pareil.** « Unleash a devastating Oath Breaker » → « **Déchaînez** un Brise-Serment dévastateur ». Y appliquer « Déchaînement : » casse la phrase. Dans `sorts.json`, les 73 occurrences étaient **toutes** des verbes. |
| stack *(nom)* | **charge** | Le provisoire « cumul » a été converti partout (642 remplacements, accords compris). Le **verbe** « cumulable / se cumule » reste correct et inchangé. |
| realm | **royaume** | Pas « domaine ». Correction apportée par un contributeur (PR #3 du dépôt des textes). |
| nameplate | **barre d'info** *(barres de noms pour le panneau maison)* | On n'a pas créé un second terme quand la base en avait déjà un. ⚠️ Pour l'histoire : l'officiel Blizzard écrit « barres d'info » pour les siennes ; le projet a gardé « barres de noms » pour son panneau custom, jugé plus parlant. Ne pas laisser cohabiter « plaques signalétiques ». |
| Food Crate | **Caisse de nourriture** | Proposé par un joueur (« Boite de nouriture ») — idée juste, orthographe corrigée. |
| Casting *(nom, dans l'interface)* | **Incantation** | « Mouseover Casting » → « Incantation au survol ». Le **verbe** reste « Lancer ». Exception : « Casting Damage Dealer » → « **Attaquant incantateur** », aligné sur son libellé court frère déjà traduit « Incantateur ». Voir le piège correspondant plus bas. |
| PvP / PvE | **PvP / PvE** *(on n'écrit pas JcJ/JcE)* | **Décision contre l'officiel** (règle 3 ci-dessus). Écriture déjà majoritaire dans nos bases (3 254 + 983 contre 507) et mot employé par les joueurs entre eux. |

### Registres de traduction établis

Relevés dans le corpus existant, pas inventés. Ils servent à ne pas fabriquer
une exception isolée le jour où un nom neuf arrive.

| Anglais | Français | | Anglais | Français |
|---|---|---|---|---|
| Build: *(préfixe)* | Construire : | | Primal | primordial |
| Mechsuit | méca-armure | | Aeon | éon |
| Tithe | dîme | | Rush *(mouvement)* | ruée |
| Eldritch | surnaturel | | Rush *(de sang)* | afflux |

Noms propres intouchés (Elune, N'Zoth, Yogg-Saron…). Capitalisation
française : majuscule au premier mot seulement, **pas de Title Case**.
Apostrophe droite.

### Contresens de sorts corrigés — la logique à reproduire

Ce ne sont pas des choix de goût. Un mot anglais resté dans un nom français,
ou un mot mal compris, **est un contresens** : il se corrige sans arbitrage.

| Anglais | Avant (cassé) | Corrigé |
|---|---|---|
| Holy Light | Sacré Lumière | Lumière sacrée |
| Life Tap | Vie Tap | Connexion |
| Soul Tap | Âme Tap | Connexion d'âme |
| Corrupted Blood | Corrompu sang | Sang vicié |
| Bash *(druide)* | Coup | Sonner |
| Lifeblood | Sang vital | Sang-de-vie |
| Touch of Moonlight | Touch de clair de lune | Toucher du clair de lune |
| Briar Veil | Briar voile | Voile de ronces |
| Angelic Touch | Angélique Touch | Toucher angélique |
| Arrow Storm | Flèche Storm | Tempête de flèches |
| Light Lash | Cils légers / Cils clairs | Fouet de Lumière |

Signature du défaut : la traduction automatique a traité la phrase mot à mot
et laissé un mot anglais en place, souvent avec l'ordre anglais
(« Corrompu sang »).

---

## 4. Les règles qui ne se voient pas dans un tableau

### 4.1 Filtrer sur la clé ANGLAISE, jamais sur le français seul

C'est la règle d'or du projet, et elle est écrite en tête de
`chaine/outils/appliquer_vocabulaire.py`.

> Sur 165 occurrences de « Libérez », **73 seulement** traduisaient *Unleash*.
> Un remplacement global sur le français en aurait cassé 91.

Chaque substitution porte **sa propre garde anglaise**, et au besoin une
exclusion. Une règle sans garde n'est admissible que si le motif français est
à lui seul une preuve (nom propre anglais resté dans la valeur française, ou
fichier indexé par identifiant dont on n'a plus l'anglais) — et alors il faut
l'avoir vérifié entrée par entrée.

### 4.2 Mot entier, toujours

« Unleash » en sous-chaîne attrape « Unleash**ing** this Seal » :
**143 faux positifs au lieu de 73**.

### 4.3 Vérifier la FONCTION du mot, pas seulement sa présence

Un même mot anglais peut être un mot-clé de mécanique ou un verbe de phrase,
et les deux ne se traduisent pas pareil (*Unleash*, *Casting*, *Draft*).
Regarder les textes réels avant de fixer une règle.

### 4.4 Concordance de mots obligatoire

Avant de remplacer une traduction par une autre : si les deux versions n'ont
**aucun mot en commun**, méfiance — c'est presque toujours un mauvais
appariement, pas une divergence de vocabulaire.

> Cas réel : `Worldforged Scroll: Dreadnaught` apparié à « Mystic Scroll:
> Mongoose Fury ». Aucun rapport.

Un détecteur de mot-à-mot cassé (`casse(fr, en)`) sert de garde : chimère,
sigle interne, mot capitalisé en milieu de phrase identique à un mot de
l'anglais source. ⚠️ Sa liste anglaise doit **exclure les cognats français** —
« abyssal », « arcane », « astral », « divine » sont du bon français ; les
inclure ferait passer un changement de **vocabulaire** pour une réparation.

### 4.5 L'ordre des règles est porteur de sens

Elles s'appliquent dans l'ordre sur une même valeur : **le plus précis
d'abord**.

- « de Warsong Gulch » doit passer avant « Warsong Gulch », sinon on écrit
  « de Goulet des Warsong ».
- La règle qui restaure « Millhouse Manastorm » doit passer **après** le bloc
  Manastorm : posée avant, le « Manastorm » qu'elle vient d'écrire serait
  retraduit et donnerait « Millhouse Tempête de mana ».
- Les phrases entières passent avant les mots génériques.

### 4.6 Accents sur les majuscules

Blizzard n'accentuait pas les majuscules initiales en 3.3.5a. **Le projet les
accentue** (« Eclair » → « Éclair »), à toutes les positions du nom, y compris
en milieu (« Apparition d'**É**tendard »). Trois pièges mesurés :

1. **La correction se reconstruit, elle ne se recopie pas** : première lettre
   accentuée, reste du mot intact. Contrôle : « ECHEC » → « ÉCHEC », pas
   « Échec ».
2. **Les noms propres sont hors table.** « Elu » est le nom d'un PNJ, pas le
   participe. Règle générale : tout mot dont une entrée a `N == NE` (nom
   français identique au nom anglais) passe en relecture manuelle.
3. **Certains mots sont aussi anglais** (Elixir, Elite, Eclipse, Evasion…).
   « Eclipse Stiletto » est un nom d'objet resté anglais dont seule la
   parenthèse est traduite : exception explicite.

### 4.7 Typographie

- **Apostrophe droite** (`'`), pas courbe. L'officiel écrit parfois
  « Echantillon d’eau » : normaliser à la comparaison, sinon on croit à une
  divergence.
- **Espace insécable** (U+00A0) avant la ponctuation double, selon l'usage
  français. Elle est présente dans une bonne part du corpus livré.
- ⚠️ **Toute source web doit passer par une normalisation `\xa0` → espace.**
  Le site de référence écrivait « 10&nbsp;sec » ; le `%s` de Lua ne reconnaît
  pas l'insécable → **1 259 modèles seraient restés muets en silence**.
  Certaines familles de noms existent en deux graphies pour cette seule
  raison : comparer modulo l'espace.

### 4.8 Ne jamais casser ce que le client va lire

Ces éléments ne sont pas du texte : ce sont des instructions au moteur de jeu.
Les altérer va du mot faux au **plantage chez le joueur**.

**Variables de format `%s` / `%d`.** Une traduction n'est sûre que si elle
consomme **exactement** les mêmes arguments, aux mêmes rangs. Un `format()`
incompatible fait planter le client. Le français réordonne avec `%2$s` : c'est
la **position** qui compte, pas l'ordre d'apparition.

⚠️ **Ne jamais écrire un « % » nu dans une traduction.** « le % de vie » : le
pourcent suivi d'un « d » est lu comme le code `%d`. Trois traductions étaient
dans ce cas. Corrigées en écrivant « pourcentage ».

**Variables de texte `$n`, `$c`, `$g`, `$s1`, `$a1`.** `$n` est le nom du
personnage, substitué à l'affichage. ⚠️ Les caches WDB des joueurs livrent ces
textes avec le nom **déjà résolu** (« Merci, <un récolteur>. ») : les ingérer tels
quels publie le pseudo d'un joueur et fait voir ce nom-là à tous les autres.
Il faut les remettre en `$n` (17 textes purgés le 20/07/2026) ou écarter
l'entrée. Chercher les vocatifs répétés (« Merci, X ! ») lors de tout audit.

**Codes couleur et icônes.** `|cAARRGGBB…|r` (couleur), `|T…|t` (icône),
`|H…|h` (lien). Ils doivent traverser la traduction intacts.

**Nombres calculés.** Ascension envoie des formules, pas des `$s1` figés : le
client calcule le nombre affiché. L'alignement des nombres se fait avec
**tolérance**, en protégeant les codes couleur et les icônes. Ne jamais
inventer un chiffre.

**Popups à mot de confirmation.** La fenêtre `DELETE_GOOD_ITEM` compare la
saisie à la globale `DELETE_ITEM_CONFIRM_STRING`, que l'addon n'écrit pas —
donc `DELETE`. La traduction officielle dit « Tapez "EFFACER" » : affichée
telle quelle, elle fait taper le mauvais mot et le bouton reste gris. La
phrase française doit dire `DELETE`. Même vigilance pour toute popup à saisie.

**GlobalStrings lues par du code sécurisé.** Traduire certaines globales de
combat provoque du *taint* et bloque des actions protégées. Ne pas y toucher.

---

## 5. Les pièges payés

Ce que le projet a réellement cassé, et ce que ça a coûté.

### 5.1 Apparier par identifiant quand le serveur renomme des sorts en place

**Le plus cher de tous, et il s'est produit trois fois.**

Un outil croisait le nom anglais d'Ascension avec le français officiel **au
même numéro de sort, sans vérifier que Blizzard nommait ce sort pareil**. Or
Ascension renomme des sorts en place : l'ID 2831 s'appelait « Armor +8 » chez
Blizzard, Ascension l'a rebaptisé « Armor (Light) » — et on récupérait
« Armure +8 ».

- **Coût mesuré : 45 % de régressions** si la passe était partie en l'état
  (119 entrées touchées dont 48 fausses).
- Le garde-fou (`garde_appariement.py`) n'adopte le frFR officiel d'un
  identifiant que si le juge de paix `spells_enUS.json` confirme que Blizzard
  nommait bien ce sort ainsi. Après garde : 72 entrées, **toutes prouvées**.
- Il **plante bruyamment** si le juge de paix est absent, vide ou tronqué.
  C'est délibéré : sans ça, il rendrait un rapport vide, et un rapport vide se
  lit comme un rapport propre.

Le **même défaut sur une autre source** a produit les noms empoisonnés : un
pack de traduction d'époque joint par identifiant a posé un nom bouche-trou
sur des milliers d'IDs. Résultat en jeu :

- « Epreuve de la Foi » sur **791 entrées** de sorts sans rapport entre eux ;
- « Appel du familier » sur **1 882** ;
- « 0 » sur **1 307**.

Des centaines de sorts affichaient donc le nom d'un autre. Décision : purger,
quitte à revenir à l'anglais — un nom absent vaut mieux qu'un nom faux.

> **La leçon générale :** une règle juste appliquée par un outil faux fait
> plus de dégâts que pas de règle du tout.

### 5.2 La casse n'est pas un discriminant

On a d'abord cru que le « F majuscule » de « Epreuve de la **F**oi » signait
le poison. **C'est l'inverse** : Blizzard écrit « Epreuve de la Foi » (talent
*Test of Faith*) ; la graphie à f minuscule était produite par notre propre
règle d'accent. S'y fier aurait **protégé le poison et détruit la vraie
traduction**.

Le bon discriminant : **la clé anglaise est-elle, à l'octet près, un nom de
sort de `spells_enUS.json` ?** Et il faut l'égalité exacte — un comparateur
tolérant (fait pour ne pas jeter d'officiels valides) laisse passer 7 clés de
poison de plus.

### 5.3 Les codes couleur collés au mot

Les codes du jeu se **collent** au mot suivant : `|cFFB5FFFFStarcaller`. Entre
le « F » du code et le « S » du mot, `\b` **ne voit aucune frontière**.

- Coût : **38 occurrences de Starcaller et 53 de Manastorm** ont échappé au
  premier passage, en silence.
- Les **fins** de code comptent aussi : une icône de haut fait donne
  « …`|t|r`Bassin d'Arathi », et le `r` de `|r` comme le `t` de `|t` sont des
  **lettres**. La garde d'origine ne voyait que `|c` : 3 cas sur 30 ratés dans
  un seul fichier.

Le remède, dans `appliquer_vocabulaire.py` :

```python
DEBUT = r"(?:(?<=\|[rt])|(?<=\|c[0-9A-Fa-f]{8})|(?<![0-9A-Za-zÀ-ÿ]))"
FIN   = r"(?![0-9A-Za-zÀ-ÿ])"
```

…et une fonction `denuder()` qui ôte les codes **avant** de tester la garde
anglaise : sinon `|cFFB5FFFFStarcaller` ne contient aucun « Starcaller »
délimité. **Recompter après chaque passe** : c'est le recompte qui a révélé
les occurrences manquées.

### 5.4 Chercher le mot du côté français rend un compte faux

Sur la famille « Casting » de l'interface : chercher « Casting » **côté
français** n'en trouvait que **six**. Il y en avait **dix**. Les quatre autres
avaient été traduits par « **diffusion** » — le moteur avait lu *broadcast* —
et le filtre français leur était aveugle.

Coût si on s'était arrêté à six : un panneau d'options à moitié traduit, où le
titre dit « Incantation au survol de la souris » pendant que son info-bulle,
juste en dessous, dit encore « diffusion par survol ».

Même mécanisme sur le verbe *draft* : les gardes anglaises étaient écrites en
minuscules (`\bdrafted\b`) alors que le jeu écrit « **D**rafted Book of
Ascension », « **R**edraft All ». **19 entrées n'ont jamais été touchées** par
le premier lot. Les gardes ont dû être rendues insensibles à la casse.

### 5.5 Les noms de sorts incrustés : un trou, pas un rattrapage

~1 662 descriptions de sorts contiennent un nom de sort **anglais incrusté au
milieu de la phrase** (« Shield Slam », « Shield Bash »), dont ~960 sur des
sorts visibles, pour 648 noms distincts.

Le pont des noms les connaît, et pourtant **ils restent anglais à l'écran** —
vérifié en faisant tourner le moteur sur une info-bulle réelle. Raison
structurelle : la table des noms est à **clé exacte**, ses consommateurs
cherchent la chaîne entière, et aucune substitution à l'intérieur d'une phrase
n'est possible. **Aucun rattrapage à l'affichage ne sauvera ce cas** : il faut
traduire la description à la source.

Deux garde-fous obligatoires si vous reprenez ce chantier :

1. **La table des noms est empoisonnée** (869 valeurs bidon : `X-Wing`→`0`,
   `Wild Imp`→`null`). La filtrer d'abord.
2. **Remplacer du plus long au plus court** : 53 descriptions ont des noms
   emboîtés (« Mana Tide » à l'intérieur de « Mana Tide Totem »).

### 5.6 Accentuer contre un officiel non accentué

Depuis qu'on accentue les majuscules, notre français diffère de l'officiel sur
**~400 noms par le seul accent**. Un outil d'arbitrage portait une règle
« mêmes mots que l'officiel (réordonné / accentué) → adopter l'officiel » qui
ne les ratait **que** parce que sa fonction de comparaison gardait les
accents.

**Un seul `--appliquer` après une « simplification » de cette fonction aurait
réécrasé tous nos accents avec la version non accentuée de Blizzard.** Le
piège a été désamorcé : une différence d'accent seule est désormais traitée
comme une **concordance**, dans les deux outils d'arbitrage.

Corollaire : un filtre de divergence qui ne regarde que le **premier** mot
laisse passer les accents en milieu de nom (« Apparition d'**É**tendard »,
« Échec d'**É**quilibre ») — 18 faux signalements sur 81.

### 5.7 Les deux sources « officielles » de Blizzard se contredisent

Pour *Arathi Basin* : le DBC du client dit « bassin **d'**Arathi » (17 fois),
la locale serveur dit « **b**assin Arathi » (177 fois). Le glossaire suit la
seconde. Conséquence assumée : quelques occurrences de l'autre graphie
subsistent dans les bases livrées, **venues du texte officiel lui-même** et
pas de nos traductions.

> La règle « l'officiel gagne » suppose qu'il n'y ait **qu'un** officiel. Ce
> n'est pas toujours vrai. Décidez laquelle des deux sources fait foi, et
> écrivez-le.

### 5.8 Un remplacement de masse sans recompte

Une contribution extérieure a produit « fournaiseée », « plaquess »,
« Faibl'armure » — signature du remplacement global appliqué sans revérifier
le résultat. Elle a été refusée pour cette raison.

Une autre contribution, en restaurant ~90 codes couleur perdus, avait collé un
fragment de la **clé anglaise** dans la valeur française (« Acc+25 »,
« A+15 »). Trouvée par relecture ligne à ligne des 81 lignes à codes.

**Toujours recompter après une passe, et relire un échantillon à la main.**

---

## 6. Ce que ce glossaire ne dit pas

Par honnêteté envers qui reprend :

- **Wildwood n'a jamais été harmonisé.** Sept variantes sont encore dans les
  fichiers livrés (voir section 1). C'est le chantier de vocabulaire le plus
  visible qui reste ouvert.
- **Des « JcJ » subsistent** malgré la décision PvP — la passe n'a pas tout
  attrapé.
- **Les noms de sorts incrustés** (~1 662 descriptions) sont un trou connu,
  non comblé.
- Deux choix de vocabulaire proposés par un contributeur ont été **laissés en
  l'état faute d'arbitrage** : « Attaquant » → « DPS » et « Ensembles » →
  « Sets Tier ». Le corpus livré dit donc **Attaquant** et **Ensembles**.
- Certains termes sont listés **sans justification** parce que les sources du
  projet n'en donnent aucune : *Skill Card*, *Golden*, *Lucky*, *Wildcard*,
  *Ability Essence*, *Mystic Enchant*, et la plupart des noms de classes de la
  section 1. Ils sont donnés tels qu'appliqués, pas commentés au jugé.
- Les noms des **arbres de spécialisation** (validés en bloc le 21/07/2026 —
  « Mande-lutins », « Gangrefrappe »…) n'ont pas de table complète retrouvable
  dans les sources publiées : ils ne figurent pas ici.
- La **table des 55 mots** de la règle d'accent vit dans le code
  (`chaine/outils/accents_majuscules.py`), pas dans ce document.

---

## Sources

Ce fichier a été reconstruit à partir de :

- `chaine/outils/appliquer_vocabulaire.py` — les règles réellement appliquées,
  avec leurs gardes anglaises, leurs exclusions et leurs commentaires. **La
  source de vérité.**
- `chaine/outils/glossaire_jeu.py` — les termes protégés avant traduction.
- `traductions/divergences_officielles_decisions.json` — les 81 divergences
  avec l'officiel, nom par nom, avec règle et verdict.
- `traductions/appariements_officiels_interdits.json` — les appariements
  prouvés faux au banc.
- `programmes/` — les documents de conception, dont
  `2026-07-26_lot4-vocabulaire_FAIT.md`, `2026-07-29_PROGRAMME-3-arbitrages_FAIT.md`,
  `2026-08-05_PROGRAMME-27-vider-la-table_FAIT.md` (Wildwood) et
  `2026-08-18_PROGRAMME-35-sortir-la-3.5.1_FAIT.md` (contributions extérieures).
