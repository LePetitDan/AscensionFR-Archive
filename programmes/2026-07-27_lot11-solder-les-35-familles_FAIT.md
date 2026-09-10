# Demande de code → Claude Code

**Date :** 2026-07-27 · **lot 11 — solder les 35 familles, et le même mal côté objets**

> **La simulation à blanc du lot 10 est la trouvaille de ces trois jours.** « Sans la
> barrière, une seule commande annulait les deux purges » — 3 941 paires ré-adoptées. Ni
> toi ni moi ne l'avions vu, et personne ne l'aurait vu venir. Le fait de l'avoir mesuré
> **avant** de laisser la barrière bloquer quoi que ce soit est exactement ce que je
> demandais et exactement ce qu'il fallait.
>
> Le trou de chaîne trouvé à trois endroits au lieu d'un, et l'Atelier réparé sans
> reconstruire l'exe : très bien vu aussi.

---

## La décision de Dan : **les 35 familles, d'un coup**

Il a vu ton tableau et il a choisi de tout solder plutôt que de garder l'outillage pour la
3.5. Sa raison : ne plus avoir à y revenir. Donc : **les 35, dans la 3.4.**

Le mode d'emploi est le tien : une ligne par valeur dans la table `POISON`, la purge, le
filtre des quatre couches et la barrière d'adoption suivent d'eux-mêmes.

## Les garde-fous — c'est le cœur de la demande

Ce lot est le plus risqué des trois : on ne purge plus des valeurs manifestement absurdes
(« 0 », « HOT PATCHING PLACEHOLDER ») mais des **vrais noms de sorts** — « Frénésie »,
« Enrager », « Tourbillon », « Rénovation ». Certains porteurs sont légitimes, et tu l'as
écrit toi-même (« certains *enrage* sont plausibles »).

1. **Le même discriminant qu'au lot 10, sans exception** : la **paire officielle**
   (`enUS × frFR`) doit correspondre pour qu'une entrée soit gardée. Une clé connue de
   Blizzard qui porte une valeur qui n'est pas la sienne reste du poison.
2. **Nomme les porteurs légitimes gardés pour chacune des 35.** C'est la colonne que je
   lirai en premier.
3. 🛑 **Arrête-toi et dis-le-moi** si une famille garde **plus de 5 porteurs légitimes** :
   ça voudrait dire que ce n'est pas une famille empoisonnée mais une traduction
   réellement partagée, et il ne faut pas la purger.
4. 🛑 **Arrête-toi aussi** si le total des sorts perdant leur **entrée entière** dépasse
   **400** (89 pour deux familles au lot 10). Au-delà, Dan doit le savoir avant, pas après.
5. **Avant/après dans l'addon, famille par famille.** Comme tu l'as fait pour
   « Appel du familier » : 1 882 → 1, et le 1 nommé.

## Le même mal côté objets

Tu as trouvé **5 descriptions `D="0"`** dans `DB_Objets.lua` (« Le chasseur : Hawk Eye »,
« L'Œil : Arcanes Résistance »…). L'espace des objets est indexé par identifiant, donc il a
la même maladie par construction.

- **Corrige ces 5.**
- Et surtout : **mesure l'ampleur** dans l'espace des objets, comme tu l'as fait pour les
  sorts — combien de valeurs sont portées par un nombre anormal de clés d'objets sans
  parenté, combien d'entrées, et ce qu'un joueur en voit. **Ne purge rien d'autre** : c'est
  le même schéma que le § 3 du lot 10, une mesure pour que Dan tranche en une passe.
- Si la barrière du nombre de porteurs a du sens là aussi, dis-le — mais ne la pose pas
  sans me le dire.

## Après ce lot

La 3.4 est complète. Dan teste en jeu, donne son go, et je t'envoie la demande de build.
Ne prépare rien du build ici.

---

**« Terminé » veut dire :**

> - Les 35 familles purgées, **porteurs légitimes nommés un par un**, avant/après dans
>   l'addon, et le nombre de sorts ayant perdu leur entrée entière.
> - Les 5 descriptions d'objets corrigées, et la **mesure** de l'ampleur côté objets.
> - `verifier_tout.py` code retour 0, bancs 19/3, bases régénérées **par la nouvelle
>   chaîne** (c'est aussi son premier vrai essai).
> - Les corrections des lots 7, 9 et 10 vérifiées intactes dans l'addon régénéré.
> - **Ne rien publier, ne rien pousser.**

**Validation :**

> Autonome, **sauf les deux arrêts du § garde-fous** (plus de 5 porteurs légitimes gardés
> sur une famille, ou plus de 400 sorts perdant leur entrée). Dans ces deux cas : tu
> t'arrêtes, tu me montres, et Dan tranche.

---
## Réponse de Claude Code

🛑 **Je me suis arrêté sur la purge des 35 : ton deuxième garde-fou a mordu.**
Les pertes projetées d'entrées entières font **487, au-dessus de la limite de
400**. Rien n'a été purgé de ce volet — la mesure complète est plus bas, avec
trois options chiffrées pour que Dan tranche.

Le premier garde-fou, lui, n'a pas mordu : **aucune famille ne garde plus de
2 porteurs légitimes** (la limite était 5).

Tout le reste du lot est fait : les 5 descriptions d'objets sont corrigées,
la mesure côté objets est rendue — et elle est grosse —, et la nouvelle chaîne
a fait son premier vrai essai de bout en bout. `verifier_tout.py` : code
retour 0, bancs 19/3, lots 7/9/10 intacts. Rien publié, rien poussé.

---

### 1. La mesure des 35 — et pourquoi je me suis arrêté

Méthode, la même qu'aux lots 9 et 10, avec deux précautions nouvelles :

- **le piège des accents** : l'officiel écrit « Eclair de feu », nous
  « Éclair de feu » (règle du lot 7). La paire officielle se compare donc
  modulo notre règle d'accent — sans ça, `Firebolt` aurait été purgé de sa
  propre traduction ;
- **les variantes de graphie** : « Tempête divine ! » vit en deux versions
  (espace normale et insécable), toutes deux comptées.

**Les porteurs légitimes, famille par famille** (la colonne que tu voulais en
premier) — et la projection des pertes d'entrées entières :

| famille | pertes | porteur(s) légitime(s) — paire officielle exacte |
|---|---:|---|
| Chaîne d'éclairs | **144** | `Chain Lightning`, `Chain Bolt` |
| Tourbillon | **97** | `Whirlwind`, `Whirwind` *(sic — la coquille est de Blizzard)* |
| HOT PATCHING PLACEHOLDER | 43 | aucun |
| Éclair de feu | 28 | `Firebolt` |
| Trait de feu | 21 | `Fire Blast` |
| Trait de l'ombre | 20 | `Shadow Bolt` |
| Rénovation | 17 | `Renew` |
| Tempête de lames | 17 | `Bladestorm` |
| Frénésie impie | 15 | `Unholy Frenzy` |
| Exorcisme | 12 | `Exorcism` |
| Javelot de glace | 11 | `Ice Lance` |
| Souffle de givre | 10 | `Frost Breath` |
| Pourfendre | 10 | `Rend` |
| Enrager | 9 | `Enrage` |
| Frénésie | 7 | `Frenzy` |
| Ascension HPP | 6 | aucun |
| Faux sort | 6 | `Dummy Spell` |
| Maître de la discrétion | 5 | `Master of Subtlety` |
| Tempête divine ! | 4 | `Divine Storm!` |
| Soins inférieurs | 3 | `Lesser Heal` |
| Cannibalisme | 2 | `Cannibalize` |
| les 14 autres (outillage invisible) | **0** | `Fel Inferno`, `100% Block`, `Shadow Bolt Volley`, `Poisoned Fangs Proc`, `Noggenfogger Elixir` — et 9 familles sans aucun porteur légitime |

**Total : 487 pertes projetées.** Ta limite disait 400, et ta consigne était
claire : au-delà, tu le sais avant, pas après.

**Ce que sont ces 487** : des entrées de `DB_Sorts.lua` dont le nom actuel est
le poison et dont l'identifiant n'est pas couvert par le chemin officiel —
purgées, elles perdent nom ET description française, et repartent dans la
file du Compagnon. Ce sont très majoritairement des lignes d'info-dégâts de
boss (« Anomalus - Arcane Spark - Damage Info ») et des sorts custom : leurs
descriptions françaises sont peut-être bonnes, mais **leur nom actuel ment**.

**Les trois options, chiffrées :**

| option | pertes | ce que ça laisse |
|---|---:|---|
| (a) les 35 d'un coup, comme tu l'avais décidé | **487** | plus rien à arbitrer ; 487 sorts en file, retraduits proprement au fil des cycles |
| (b) 33 familles, en gardant « Chaîne d'éclairs » et « Tourbillon » pour la 3.5 | **246** | les deux plus grosses familles restent (elles portent à elles seules la moitié des pertes) |
| (c) seulement les 14 familles à 0 perte | **0** | l'outillage invisible disparaît, tous les noms visibles restent à traiter |

Mon avis, si tu le veux : **(a)**. Ces 487 entrées affichent aujourd'hui un nom
faux — c'est ton propre raisonnement des lots 9 et 10 — et la mécanique de
rattrapage par la file a déjà fait ses preuves (89 au lot 10, revenus
proprement). Mais 487 > 400, donc c'est ta décision, pas la mienne.
**Techniquement, quel que soit ton choix : c'est une ligne par famille dans la
table `POISON`, tout le reste suit.**

### 2. Le même mal côté objets — corrigé pour les 5, mesuré pour le reste

**Les 5 `D="0"` : corrigés, et ce n'était pas la maladie du PackFR.** La
description **anglaise d'origine** de ces objets vaut littéralement « 0 » dans
l'ItemAddon.dbc — le marqueur « pas de description » d'Ascension. Le moulin
avait fidèlement « traduit » « 0 » par « 0 », et cette **unique paire de
cache** produisait les cinq lignes livrées (et en aurait produit d'autres).
`outils/corriger_description_zero.py` l'a retirée : `DB_Objets.lua` compte
maintenant **0** `D="0"`. Les 34 autres paires sans lettre du fichier sont des
échos volontaires (bornes `@10-19@`, l'objet-blague Fibonacci) : pas touchées.

**L'ampleur, mesurée dans les deux espaces :**

- **L'espace par texte est SAIN** : `objets_dbc.json/noms` (159 728 paires) et
  le pont livré `DB_ObjetsNoms.lua` — **0 valeur anormale**. Une jointure par
  texte ne peut pas étaler une valeur sur des clés sans rapport, et ça se voit.
- **L'espace par identifiant a la maladie, en grand** : sur 720 valeurs
  portées par ≥ 5 identifiants dans `objets.json`, **636 sont suspectes** —
  leurs identifiants portent des noms anglais multiples et sans parenté. Les
  pires, avec ce qu'un joueur voit :

| ids | valeur | en jeu |
|---:|---|---|
| 107 | [NOM DE L'ARTICLE MANQUANT] | 77 objets anglais distincts affichent ce texte comme nom |
| 53 | \*\*\*Nom non disponible\*\*\* | 49 objets distincts |
| 37+18 | apparence en double / Apparence en double | des vraies pièces d'équipement nommées comme un marqueur |
| 31 | Bague Casse-Crâne | posée sur des robes et jambières de gladiateur |
| 26 | Les Dreadblades | sur des brassards et capes sans rapport |
| 25 | Éclat du mépris | sur 8 pièces Bloodforged distinctes |
| 24 | Strom'kar, le briseur de guerre | sur des brassards et capes |
| 24 | Chercheur de serment | sur du matériel de Hellscream et autres |

  Un nom d'objet est **toujours visible** — sacs, info-bulles, hôtel des
  ventes. C'est l'équivalent objets des familles de sorts, par le même
  mécanisme : une jointure par identifiant sur des données d'époque.

- **La barrière y aurait du sens, et je ne l'ai pas posée**, comme demandé.
  Le bon endroit n'est pas le même que pour les sorts : l'espace par texte
  étant sain, c'est au point où du français entre **par identifiant** dans
  `objets.json` qu'il faudrait compter les porteurs (en joignant leurs noms
  anglais). Dis-moi si tu la veux, et je la pose comme celle des sorts :
  refus à l'adoption, vigie à la génération.

### 3. La nouvelle chaîne — premier vrai essai réussi

`python outils/mise_a_jour.py`, client inchangé : elle a sauté l'extraction et
déroulé **ses six maillons dans l'ordre** — WDB → `generateur_sorts` →
`generateur_db` → `optimiser_memoire` → `generer_noms_sorts` →
`generer_noms_objets` — jusqu'à « Mise à jour terminée ». Le filtre du poison
(4 468 écartés) et la vigie (307 valeurs, `rapports/porteurs_pont.txt`)
apparaissent dans sa propre sortie : les protections tournent maintenant
**dans la chaîne standard**, plus seulement quand on y pense.

### Ce qui attend une décision de toi

1. **L'arbitrage des 35** — option (a), (b) ou (c) du § 1. C'est le seul
   morceau de la 3.4 encore ouvert.
2. **Les 636 valeurs suspectes côté objets** — chantier jumeau, même
   mécanisme ; je peux préparer la purge par identifiant avec les mêmes
   garde-fous quand tu veux (3.5 ?).
3. **La barrière côté objets** — d'accord pour la poser, ou pas ?

### Vérifications

- `verifier_tout.py` : **code retour 0**. **Bancs : 19 verts / 3 rouges**
  (les 3 attendus).
- Bases régénérées **par la nouvelle chaîne elle-même** — c'était son premier
  vrai essai, réussi.
- Lots 7, 9 et 10 **vérifiés intacts** dans l'addon régénéré : « Coup de
  surin ! », « Piston de saccageur gangrené », « Récupération de la nature »,
  « Maîtrise du poison » ; pont « Appel du familier » toujours à 1 (`Call
  Pet`), « Epreuve de la Foi » 0, « 0 » 0.
- `DB_Objets.lua` : **0** description « 0 » (5 avant).
- Sauvegarde horodatée : `objets_dbc_avant_zero_20260728-115039.json`.
- pyflakes muet sur les deux outils du lot.
- **Rien n'a été publié, rien n'a été poussé.** Aucune passe de masse au-delà
  de ce que ce bon de commande autorisait — et le § 1, arrêté net sur ta
  limite.
