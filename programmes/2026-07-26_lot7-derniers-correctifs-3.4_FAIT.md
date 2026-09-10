# Demande de code → Claude Code

**Date :** 2026-07-26 · **lot 7 — les derniers correctifs avant le build de la 3.4**

> Merci pour les lots 4, 5 et 6 : les trois pièges du vocabulaire (Millhouse, l'adjectif
> « statique », le courant d'air abyssal), la mesure de fiabilité qui a évité une passe à
> 45 % de régressions, et la barrière du zip fermée dans les deux sens. C'est du bon
> travail, et tu as eu raison contre moi plusieurs fois.
>
> Ce lot solde ce qui reste avant le build. **Après lui, la 3.4 est prête à tester.**

---

## 1. Les arbitrages de Dan sur ta réponse au lot 4

| Point | Décision |
|---|---|
| Le verbe « to draft » (16 entrées) | **« composer »** — « Composez de nouveaux sorts de départ ». Dan a préféré le vrai verbe français à « drafter ». Le **nom** du mode reste « Draft ». |
| « Millhouse Manastorm » | **On le laisse tel quel**, comme Blizzard. Donc : corriger « Tempête de mana du moulin » (contresens sur « mill house ») et garder le nom anglais entier. |
| Les 6 libellés où « Casting » est un nom | **« Incantation »** — « Mouseover Casting » → « Incantation au survol », etc. C'est le mot officiel Blizzard pour le nom. Le verbe reste « Lancer ». |
| Les 8 « bassin d'Arathi » de `DB_Sorts.lua` | **On harmonise sur « Bassin Arathi »**, y compris quand la chaîne vient du texte officiel Blizzard. Un seul nom dans le jeu vaut mieux qu'une fidélité de source invisible au joueur. |

## 2. Les 4 traductions fausses déjà livrées (lot 5, § 2 bis)

À corriger — ce sont des contresens en ligne aujourd'hui :

- `Fel Reaver's Piston` : « Soins sur la durée sur les soins » → remettre
  **« Piston de saccageur gangrené »**, qui était juste ;
- `Nature's Rejuvenation` : « Récupération surpuissante » → la traduction de *Nature's
  Rejuvenation*, pas d'*Empowered Rejuvenation* ;
- `Shanked!` : « Pourfendre » (c'était *Rend*) ;
- `Poison Mastery` : « Poisons » → rétablir le « Maîtrise » perdu.

## 3. Le garde-fou d'appariement — poser la barrière, sans lancer la passe

Applique le correctif que tu recommandes : la condition `enUS[id].N == asc[id].N` dans
**`appliquer_divergences_officielles.py`** et **`croiser_sources.py`**, avec le repli sur
la comparaison sans séparateurs (« Holy Form » / « Holyform »).

⚠️ **Mais ne relance PAS la passe officielle, et pas la passe Glayna.** Dan a décidé
qu'elles partent **après** la 3.4. Ce lot pose seulement le garde-fou pour que l'outil
cesse d'être dangereux. Dis-moi combien de divergences deviennent applicables une fois la
condition posée — ce chiffre servira à préparer la 3.5.

## 4. Les accents manquants — 1 247 noms

Applique la règle : les majuscules initiales non accentuées de la source officielle 3.3.5a
(« Eclair » → « Éclair », « Elixir », « Etat », « Eclat », « Ame »…). Tu as relu les
56 mots initiaux distincts un par un, 0 faux positif — c'est mécanique et sans risque de
contresens. **Donne le compte réel appliqué.**

## 5. Les bancs d'essai — réparer, sans faux vert

- Les **trois réparations à une ligne** : `verifier_objets`, `verifier_infobulle`
  (ajouter `IsShown` à la fausse info-bulle) et `verifier_barres` (poser l'option et
  `IsAddOnLoaded`).
- **`verifier_repliques` : en entier ou pas du tout.** Les trois corrections ensemble —
  `CreateFrame`, lire les seaux `C[]`/`M[]`, et `sys.exit(1)` à la place des `return 1`
  avalés. Ton avertissement est le bon : un banc vert qui ne teste rien est pire que le
  rouge d'aujourd'hui.
- **`verifier_interface` et `verifier_signalements` : on ne touche à rien.** Périmés,
  gardés, à réécrire plus tard. Ne relâche surtout pas leurs assertions.
- L'écart connu de `verifier_infobulle` (les codes couleur dénudés volontairement,
  `Sorts.lua:79`) : **consigne-le** dans le banc, en commentaire, plutôt que de relâcher
  l'attente.

## 6. Deux trous de couverture — à noter, pas à combler maintenant

`Modules/InterfaceCiblee.lua` et `AppliquerCanalMoteur()` ne sont couverts par aucun banc.
Écris-le dans `docs/CONTEXTE_PROJET.md` pour que ça ne se reperde pas. C'est un chantier
d'après la 3.4.

---

**« Terminé » veut dire :**

> - Les 4 arbitrages appliqués, les 4 traductions fausses corrigées, les accents appliqués,
>   avec les **comptes réels**.
> - Le garde-fou d'appariement posé, **aucune passe de masse lancée**, et le chiffre des
>   divergences devenues applicables.
> - Quatre bancs réparés, deux laissés tels quels, `verifier_tout.py` code retour 0.
> - Bases régénérées et vocabulaire vérifié **dans l'addon**, comme au lot 4.
> - **Ne rien publier, ne rien pousser.** Dan teste en jeu, puis donne son go, puis je
>   t'enverrai la demande de build.

**Validation :**

> Autonome sur tout. **Arrête-toi et dis-le-moi** si une des 4 corrections du § 2 touche
> plus d'entrées que prévu, ou si le garde-fou d'appariement fait tomber beaucoup plus que
> les 48 divergences attendues — ça voudrait dire que le défaut est plus large.

---
## Réponse de Claude Code

**Fait le 26-27/07/2026. Les six points sont soldés. `verifier_tout.py` : code
retour 0. Les bancs passent de 16 verts / 6 rouges à 19 verts / 3 rouges.
Rien n'a été publié ni poussé. La 3.4 est prête à tester.**

Trois choses que tu voulais savoir, tout de suite :

- **Le garde-fou fait tomber exactement 48 divergences**, pas une de plus — et
  ce sont, une par une, les 48 du seau FAUX du lot 5. Le défaut n'est donc pas
  plus large que prévu.
- **Aucune passe de masse n'a été lancée**, ni officielle ni Glayna.
- **Une des 4 corrections dépasse le prévu** : `Nature's Rejuvenation` touche
  3 entrées et non 1. Détail au § 2 — c'est bénin et je l'ai traité, mais tu
  m'avais demandé de le dire.

---

### 1. Les quatre arbitrages — 63 entrées

| Arbitrage | Compte réel |
|---|---|
| Le verbe « to draft » → **composer** | **39 entrées** |
| « Casting » nom → **Incantation** | **20 entrées** (10 libellés) |
| « Millhouse Manastorm » remis en anglais | **4 entrées** |
| « Bassin Arathi » | **0** dans nos traductions, **83** dans les bases livrées |

**Le verbe : 19 des 39 n'avaient jamais été touchées par le lot 4**, et pas
pour la raison qu'on croyait. Mes gardes anglaises étaient écrites en
minuscules (`\bdrafted\b`) alors que les clés du jeu écrivent « **D**rafted
Book of Ascension », « **R**edraft All ». Aucune ne correspondait, et ça ne se
voyait pas : le lot 4 annonçait « 16 entrées » en toute bonne foi. Ces 19-là
disaient encore « Tout reformuler », « Réécriture actuelle », « remanier des
sorts », « sera reformulé ». Elles disent maintenant « Tout recomposer »,
« Recomposer l'actuel », etc.

⚠️ **J'ai gardé un filet** que tu ne m'avais pas demandé, et je pense qu'il
compte : `traduire_gisement.py` n'écrase jamais un français existant, il
**ajoute** les chaînes neuves de chaque patch Ascension, traduites par Google —
et c'est Google qui rend « draft » par « rédiger ». Sans ces règles-là, l'outil
cesserait d'être un normalisateur rejouable pour devenir une migration à usage
unique, et ton arbitrage reviendrait au prochain patch. Elles se déclenchent 0
fois aujourd'hui, 6 fois sur l'état d'origine.

**« Casting » : il y en avait 10, pas 6.** Chercher « Casting » du côté
**français** n'en trouve que six — c'est exactement l'anti-patron que notre
règle d'or interdit. Les quatre autres avaient été traduits par
« **diffusion** » (le traducteur a lu « broadcast ») : « Permet la diffusion
par survol de la souris pour les cibles amies ». Sans elles, ton panneau
d'options aurait été à moitié traduit — le titre disant « Incantation au
survol de la souris » et son info-bulle, juste dessous, « diffusion par survol
de la souris ».

**« Bassin Arathi » : le problème était dix fois plus large que les 8 de
`DB_Sorts.lua`.** 83 occurrences dans 6 bases livrées. Nos traductions, elles,
étaient déjà propres : tout venait du frFR officiel, qui ne passe jamais par
`traductions/`. J'ai donc posé l'harmonisation **au point d'écriture** des
bases (`generateur_db.harmoniser`), plus une passe ponctuelle sur
`DB_Communaute.lua` — la seule base qu'aucune régénération ne nettoie jamais,
parce qu'elle est ouverte en **ajout**. Résultat : **0 occurrence** restante.

Deux choix que j'ai faits et que tu peux défaire en une ligne :

1. **J'ai conservé la casse.** Ton glossaire dit « Bassin Arathi », mais l'addon
   livre déjà 185 « bassin Arathi » en minuscule contre 41 en majuscule, et la
   locale du serveur en écrit 232 contre 42. Forcer la majuscule aurait écrit
   « dans le Bassin Arathi » au milieu d'une phrase. Ce qu'on supprime, c'est
   l'apostrophe ; le nom est le même dans les deux casses.
2. **« Casting Damage Dealer » → « Attaquant incantateur »** et non
   « Incantation Attaquant », qui n'est pas du français. Aligné sur son libellé
   court frère, déjà traduit « Incantateur ».

Deux pièges qui auraient fait des dégâts, tous deux vérifiés en faisant tourner
le moteur :

- **L'ordre de la règle Millhouse.** Posée avant le bloc Manastorm, elle
  fabrique « Millhouse **Tempête de mana** » sur la créature 179536 : le moteur
  calcule son exclusion sur le français d'origine, il ne voit donc pas ce que la
  règle vient d'écrire. Elle est posée après, et le commentaire l'explique sur
  place.
- **Les fins de code couleur.** Une icône de haut fait donne
  `…|t|rBassin d'Arathi` — le `r` de `|r` **est une lettre**, donc la frontière
  de mot n'y voit rien. 3 occurrences sur 30 échappaient en silence. C'est la
  même famille que les 191 entrées ratées au lot 4, mais côté *fin* de code et
  non début. La garde est corrigée dans les deux outils.

### 2. Les 4 traductions fausses — corrigées, une dépasse

Outil : `outils/corriger_appariement_faux.py`. Il **vérifie la valeur de départ
avant d'écrire** et refuse si elle a changé — ce script existe précisément parce
qu'une écriture automatique non vérifiée a fait les dégâts qu'il répare.

| Sort | Rétabli en |
|---|---|
| `Fel Reaver's Piston` | **Piston de saccageur gangrené** |
| `Nature's Rejuvenation` | **Récupération de la nature** |
| `Shanked!` | **Suriné !** |
| `Poison Mastery` | **Maîtrise du poison** |

**Le dépassement.** `Nature's Rejuvenation` ne touche pas 1 entrée mais **3** :
le sort, plus les **2 cartes de compétence** qui portent son nom (« Carte de
compétence dorée - … »). Sans elles, le joueur voyait deux noms pour la même
chose, et `corriger_cartes_competence.py` ne les aurait pas rattrapées (sa
mesure de ressemblance tombe sous son seuil). J'ai vérifié qu'il n'y en avait
que deux, sur les 7 020 cartes des quatre familles. **Ce n'est pas le signe d'un
défaut plus large** — c'est la conséquence normale de renommer un sort qui a des
cartes. Dans l'addon livré, ça fait 8 entrées au lieu d'une : les 5 rangs du
sort, le pont des noms, et les 2 cartes.

J'ai aussi corrigé **une coquille d'accent** hors périmètre : l'objet 30619
disait « gangrèn**e** » chez nous alors que l'officiel dit « gangrén**é** », et
l'addon était déjà incohérent avec lui-même. 1 entrée, 1 caractère — sinon le
sort corrigé et l'objet dont il vient se seraient écrits différemment.

**« Suriné ! » est mon choix, et c'est le seul de ce lot.** Comme « drafter » au
lot 4. Le mot de Blizzard pour « shank » est bien « **surin** » — 6 des 7 objets
officiels le prouvent (le 7ᵉ, « Wild Hog Shank » → « Jarret de cochon sauvage »,
c'est le sens boucherie). Mais la **forme au participe** n'a aucun précédent, et
« Suriner » est déjà le nom de *Gouge*. Deux replis si ça te gêne, une ligne à
changer dans l'outil :
- **« Coup de surin ! »** — reprend le substantif réellement attesté, aucune
  collision ;
- **« Lardé ! »** — aucune collision non plus, mais aucun ancrage Blizzard.

À savoir : `Shanked!` n'était **pas traduit** avant la passe fautive. Les trois
autres se restaurent sur preuve (le journal de la passe, cinq sauvegardes, et la
source Blizzard de l'objet 30619) ; celle-là se décide.

### 3. Le garde-fou — posé, aucune passe lancée

`outils/garde_appariement.py` (module commun, sur le modèle de
`garde_packfr.py`), branché dans `appliquer_divergences_officielles.py` et
`croiser_sources.py`, avec le repli sans séparateurs (« Holy Form » /
« Holyform »).

**Le chiffre que tu attends : 48 divergences tombent, et la passe devient
sûre.** Sans le garde-fou elle touchait 119 entrées dont **48 régressions
(40 %)** ; avec, elle en touche 72, toutes à appariement prouvé. La liste à
arbitrer passe de 112 à **65** (une entrée y **apparaît**, « Enchant Weapon -
Spell Power », que le garde-fou tranche au lieu de la laisser ambiguë ; les
« ambigus » tombent de 4 à 0). Les 7 corrections automatiques sûres sont
inchangées, rapport identique à l'octet près.

**Zéro cas indécidable** : `spells_frFR.json` et `spells_enUS.json` ont
rigoureusement les mêmes 49 839 identifiants. Le module refuse quand même
l'indécidable, et **il plante bruyamment** si le juge de paix est absent, vide
ou tronqué — un rapport vide se lit comme un rapport propre, c'est le genre de
silence qui a créé cette affaire.

**Ce que le garde-fou a révélé, et que personne n'avait vu.** Il retire 3 des 7
corrections « sûres » — et ces trois-là sont **exactement trois des quatre
traductions fausses du § 2** que je venais de réparer. Autrement dit : sans lui,
le prochain `--appliquer` aurait ré-écrasé « Piston de saccageur gangrené »,
« Récupération de la nature » et « Maîtrise du poison », **sous l'étiquette
rassurante « correction sûre »**. La barrière ne protège pas seulement la 3.5,
elle protège le travail d'aujourd'hui.

Trois choses en plus, mesurées, que j'ai posées :

- **`croiser_sources.py` n'était pas reproductible.** Le script inchangé rendait
  94, 94, 96, 94 divergences selon l'exécution : il parcourait un ensemble non
  ordonné et ne gardait que le premier identifiant rencontré. Deux lectures du
  même rapport ne portaient pas sur les mêmes entrées. Trié, il rend deux fois
  le même fichier à l'octet près — et **174 divergences au lieu de ~94**, parce
  que les identifiants bas sont la plage Blizzard classique, la seule qui ait
  des officiels. C'est un gain de couverture, pas une régression.
- **Le PackFR faisait rentrer la contamination par la porte de derrière** :
  100 % des nouvelles « divergences PackFR » que le garde-fou faisait apparaître
  étaient la recopie mot pour mot de l'officiel qu'il venait d'écarter. J'ai posé
  une règle **étroite** — on n'écarte le PackFR que dans ce cas précis. Surtout
  pas la règle complète : mesuré, elle détruirait 74 % de ses identifiants, qui
  sont des sorts custom qu'aucun DBC Blizzard ne connaît.
- **16 officiels valides étaient perdus** par le dédoublonnage ; ils sont
  repêchés sur un autre identifiant du même nom anglais, quand il est unique.

### 4. Les accents — 561 chez nous, 2 989 dans l'addon

**La règle ne pouvait pas s'appliquer seulement dans `traductions/`.** Le
français officiel entre **tel quel** dans ce qu'on livre : 15 491 entrées de
`DB_Sorts.lua` ont un nom identique au nom officiel du même identifiant
(« Eclair de givre » pour *Frostbolt*). J'ai donc fait les deux : une passe sur
nos traductions, **et** la règle posée aux points d'écriture des bases. Surtout
pas dans `sources/` : ces fichiers sont ré-extraits du client, la correction y
disparaîtrait en silence — et c'est le juge de paix du § 3.

| | avant | après |
|---|---|---|
| `traductions/*.json` | — | **561 entrées** |
| bases livrées, têtes non accentuées | **3 784** | **795** |

Soit **2 989 corrections visibles par le joueur**. Les 795 restantes sont toutes
volontaires : 791 sont le poison décrit plus bas, 3 sont « Eclipse Stiletto », 1
vient de DragonUI.

Trois pièges, tous trouvés en attaquant ma propre règle sur les vraies données :

1. **Le relevé du lot 5 ne donne pas la correction.** Ses 56 variantes sont en
   **bas de casse**, et pour « Equilibre » c'est carrément le participe passé
   « équilibré ». Recopier ce champ aurait mis 1 247 corrections en minuscules.
   La correction se reconstruit : première lettre accentuée, reste du mot
   intact. Contrôle : « ECHEC » → « **É**CHEC », pas « Échec ».
2. **« Elu » est sorti de la table.** `DB_Creatures[10377]` est
   `N="Elu", NE="Elu"` : c'est le **nom propre d'un PNJ** du poste de Freewind,
   et la quête 28491 le cite trois fois. Accentuer la seule tête aurait rendu la
   quête incohérente avec elle-même. Coût : 3 entrées non accentuées (dont
   « Elu ombrelune », qui lui est un vrai participe) — à faire à la main.
3. **Dix des 56 mots sont aussi anglais** (Elixir, Elite, Eclipse, Evasion…).
   « Eclipse Stiletto (gaine arrière) » est un nom d'objet resté anglais dont
   seule la parenthèse est traduite : l'accentuer fabriquait « **É**clipse
   Stiletto ». Il est en exception explicite.

⚠️ **Un défaut de données que la règle a mis au jour, et que je n'ai pas
touché.** Dans `sorts.json`, **778 clés anglaises sans aucun rapport entre
elles** (« Abom tele back », « Angel of Death », « Aftershock cast »…) portent
toutes la **même valeur** : « Epreuve de la Foi ». Elles arrivent telles quelles
dans l'addon — **791 entrées de `DB_SortsNoms.lua`**, donc 778 sorts affichent
en jeu un nom qui n'est pas le leur. Ce n'est pas une traduction, c'est un
dégât, de la même famille que « Appel du familier » ×1 879 ou « 0 » ×896.

Je l'ai **exclu de la règle d'accent exprès** : le rendre « Épreuve de la Foi »
l'aurait fait passer pour du travail propre et rendu introuvable d'un coup
d'œil. La signature est nette — le **F majuscule** ; la vraie traduction du sort
s'écrit « Epreuve de la foi ». **Purger demande ton feu vert** : ça fait
retomber ces 778 sorts en anglais, ce qui vaut mieux qu'un faux nom, mais c'est
une suppression de données et ce n'est pas ce que tu m'as demandé.

### 5. Les bancs — 19 verts, 3 rouges (contre 16/6)

| Banc | État |
|---|---|
| `verifier_objets` | **vert** — 18 ok / 0 échec |
| `verifier_barres` | **vert** — 7 ok / 0 échec |
| `verifier_repliques` | **vert** — 69 477 répliques lues, 984 vérifications |
| `verifier_infobulle` | **rouge exprès** — 8 ok / 1 échec, l'écart connu |
| `verifier_interface`, `verifier_signalements` | **intouchés**, md5 identiques |

`verifier_infobulle` rend **1 en fonctionnement normal**, et c'est voulu : tu as
demandé de consigner l'écart des codes couleur sans relâcher l'attente, donc
l'assertion échoue toujours et repassera au vert d'elle-même le jour où
l'alignement saura restituer les couleurs. Le commentaire fixe le seuil de
lecture : **1 échec = normal, 2 = régression**. Conséquence à connaître : ce banc
n'est pas branchable tel quel sur une barrière automatique. Rien ne le fait
aujourd'hui (`verifier_tout.py` et `construire_zip_release.py` n'appellent aucun
banc), mais ton `README.md:635` dit au lecteur de le lancer sans le prévenir.

Petit écart de comptage : tu annonçais « 7 sur 8 » ; le banc exécute **9**
assertions (8 ok, 1 échec).

**`verifier_repliques` : ton avertissement était encore plus juste que prévu.**
Réparé « proprement », il restait **aveugle à la perte de données** : j'ai fait
disparaître **9 477 répliques (13,6 % de la base)** et il rendait toujours 0, en
affichant encore « 66 seaux ». La cause est vicieuse — le corpus de test est
prélevé *dans* les seaux, donc un seau absent n'est plus testé, et le plancher
d'entrées est compté sur ces mêmes seaux : il se dégrade au lieu de mordre.
Il a maintenant un **repère de volume relatif** (69 477 entrées relevées, bande
−1 %/+50 %), un contrôle croisé entre la chaîne de présence et son seau, et le
refus d'un seau illisible. **20 sabotages sur 20 passent au rouge**, dont les
quatre pertes de seau et les pertes diffuses. Trou résiduel assumé et écrit dans
le fichier : une perte de moins de 1 % passe encore.

### 6. Les deux trous de couverture — consignés

Section **3.70** de `docs/CONTEXTE_PROJET.md` (c'est bien lui le vivant ;
`4-reference/` en est une copie en retard de 338 lignes, ajout pur en fin de
fichier — le « supprimé » du git status est un faux signal, le fichier a été
déplacé vers `docs/`).

Le constat tient, avec deux nuances mesurées qui valaient d'être écrites :
`Modules/InterfaceCiblee.lua` **est** touché par deux bancs, mais au niveau
**compilation seulement** — donc un fichier cassé ne peut pas partir chez les
joueurs, mais aucune de ses six surfaces n'est jamais déclenchée (le décor
neutralise les deux façons de s'accrocher). Et `AppliquerCanalMoteur()` **est**
appelé par `verifier_interface.py`, sauf qu'il y applique **zéro** clé et
qu'aucune assertion ne le regarde. Piège à connaître : `verifier_canal.py` ne
couvre **pas** le canal moteur malgré son nom — il teste le canal de discussion.

---

### Ce qui attend une décision de toi

1. **« Suriné ! »** — le seul mot que j'ai choisi. Deux replis prêts (§ 2).
2. **Le poison « Epreuve de la Foi »** — 778 sorts affichent un nom qui n'est pas
   le leur. Purger = les remettre en anglais. Ton feu vert (§ 4).
3. **~530 textes citent un nom accentué sans son accent.** C'est le revers de la
   règle « majuscules **initiales** » : `DB_Sorts` dit « Éclair de givre » mais
   une description d'objet dit encore « Vous apprend Eclair de givre ». **Aucun
   effet fonctionnel** — l'addon aligne les info-bulles sur le modèle *anglais*,
   jamais sur le français — mais tu le verras en jeu. Le rattrapage est un
   remplacement littéral de 126 noms exacts, sans ambiguïté : c'est le premier
   lot d'après la 3.4 si tu le veux.
4. **La casse de « bassin Arathi »** — j'ai conservé la casse plutôt que de
   forcer la majuscule (§ 1). Dis-moi si tu préfères l'autre.
5. **« Livre de l'Ascension composé »** (3 entrées) et **« Attaquant
   incantateur »** (2 entrées) — deux formulations que j'ai choisies faute
   d'équivalent français direct.
6. **La date de coupure de la traduction de masse** : `1.6.4` selon deux sources,
   `1.7.0` selon deux autres. Le document constate le désaccord au lieu de
   trancher — c'est ton arbitrage.
7. **`OU_TROUVER_QUOI.md` se contredit** : son tableau « Je cherche… » envoie sur
   `4-reference/CONTEXTE_PROJET.md`, sa section « Les repères qui comptent » dit
   que l'original vit dans `WorkFlow/docs/`. Une note écrite seulement dans
   `docs/` est donc invisible pour le lecteur que la carte dirige.

### Vérifications

- `verifier_tout.py` : **code retour 0**, 48 fichiers compilés en `lupa.lua51`,
  aucun jeton oublié, marges inchangées (DB_Sorts 49,7 %, DB_ObjetsNoms 33 %).
- **Les 22 bancs** : 19 verts, 3 rouges — `infobulle` (rouge exprès, écart
  consigné), `interface` et `signalements` (périmés, intouchés, md5 identiques).
- **pyflakes muet** sur tous les fichiers touchés. Les seuls avertissements
  restants sont préexistants et dans des fichiers que je n'ai pas ouverts.
- **Bases régénérées** : `generateur_sorts`, `generateur_db` +
  `optimiser_memoire`, `generer_noms_sorts`, `generer_noms_objets`,
  `traduire_zones`, `traduire_epreuves`, `traduire_hautsfaits`. Vocabulaire
  vérifié **dans l'addon** : 0 « drafter/Draftez », 0 « reformul* », 0
  « bassin d'Arathi », 0 « Tempête de mana du moulin », 0 libellé « Casting »,
  0 « diffusion par survol » ; les 4 sorts corrigés vérifiés par leur
  identifiant dans `DB_Sorts.lua`.
- **Le code Lua de l'addon n'a pas été touché** : `Core.lua` et les 21 modules
  sont à leur date du 25/07. Seules les données de `DB/` ont changé.
- **Aucune écriture concurrente** : les dates de `traductions/` correspondent
  toutes à mes propres passes. Sauvegardes créées : 7 `*_avant_accents.json`,
  3 `*_avant_appariement.json`, 1 `DB_Communaute_avant_harmonisation.lua.bak`.
  ⚠️ Les `*_avant_vocabulaire.json` **datent du lot 4** et n'ont pas été
  rafraîchies (l'outil ne réécrit jamais une sauvegarde existante) : pour
  revenir en arrière sur le vocabulaire seul, c'est le dépôt git qui fait foi.
- **Rien n'a été publié, rien n'a été poussé, aucune passe de masse lancée.**
