# Demande de code → Claude Code

**Date :** 2026-07-26 · **lot 6 — refermer la barrière avant le build de la 3.4**

> À faire **avant** la demande de build. Petit lot, mais c'est celui qui évite de
> republier la panne qu'on vient d'éviter de justesse.

---

## Pourquoi

Ta réponse au lot 3 a montré qu'on est passé près de publier un addon **mort au
chargement**, et que le contrôle de l'Atelier disait « Syntaxe Lua : OK » sur exactement
cette panne (il compilait en Lua 5.5). Tu l'as réparé — merci. Mais tu as signalé toi-même
deux trous qui restent, et je ne veux pas les laisser ouverts au moment où on construit
une version :

1. `construire_zip_release.py` **relit** chaque `.lua` du zip (pseudos, webhook, version)
   mais **n'en compile aucun**. C'est le dernier endroit où un fichier cassé peut passer.
2. `verifier_tout.py` n'est appelé par **aucun code** — uniquement par le rituel manuel de
   Dan. Une barrière qu'on peut oublier de lancer n'est pas une barrière.

Et un troisième, de mon côté : il y a **22 scripts `verifier_*.py`** dans `outils/`, dont
plusieurs sont au rouge depuis longtemps (infobulle, objets, options, répliques,
signalements, barres, interface). Un banc d'essai rouge que personne ne lance donne une
**illusion de couverture** — c'est pire que pas de banc du tout.

## Objectif (le QUOI, pas le comment)

**1. Fermer le zip.** `construire_zip_release.py` doit **compiler en `lupa.lua51`** chaque
`.lua` qu'il embarque, seaux des bases paresseuses compris, et **refuser d'écrire le zip**
si un seul échoue. Même logique que ton garde-fou d'`ecrire_db` : mieux vaut pas de zip
qu'un zip mort.

**2. Rendre la barrière inévitable.** `construire_zip_release.py` appelle `verifier_tout.py`
au début et s'arrête si le code retour n'est pas 0. Dan ne doit plus pouvoir construire une
release sans que la barrière soit passée.

**3. Faire le tri dans les 22 bancs.** Lance-les tous, une fois, et rends-moi un tableau :
lesquels passent, lesquels échouent, et pour chaque échec **une ligne** disant si c'est un
vrai problème ou un banc périmé (qui teste une structure qui n'existe plus). **Ne répare
rien** — je veux d'abord savoir ce qu'on a. Ensuite on décidera : réparer ou supprimer.

---

**« Terminé » veut dire :**

> - Un zip impossible à produire si un `.lua` ne compile pas en Lua 5.1 — testé dans les
>   deux sens (un cas qui passe, un cas volontairement cassé qui bloque).
> - `verifier_tout.py` déclenché automatiquement par la construction du zip.
> - Le tableau des 22 bancs : vert / rouge / périmé, une ligne de raison par rouge.
> - Rien de publié, rien de poussé, aucune traduction modifiée.

**Validation :**

> Entièrement autonome sur les points 1 et 2. Le point 3 est une mesure : ne répare aucun
> banc sans me le demander — supprimer un banc périmé est une décision, pas un nettoyage.

---
## Réponse de Claude Code

**Fait le 26/07/2026. La barrière est fermée et testée dans les deux sens. Le
tableau des 22 bancs est plus bas. Aucun banc n'a été réparé, comme demandé.
Rien n'a été publié ni poussé.**

---

### 1 et 2. Le zip ne peut plus sortir sans passer la barrière

Trois changements dans `outils/construire_zip_release.py` :

**a) `verifier_tout.py` est lancé d'abord**, et un code retour non nul arrête
tout. **Sans échappatoire** — tu m'as dit que tu ne devais plus pouvoir
construire une release sans ça, je n'ai donc pas mis d'option pour la sauter.

**b) Chaque `.lua` embarqué est compilé en `lupa.lua51`**, la version du client.
Jamais le lupa par défaut : il est en Lua 5.5 et accepte ce que 5.1 refuse
(c'était le piège du lot 3). **Les seaux des bases paresseuses sont compilés
aussi** — le jeu les recompile un par un à l'exécution, et un seau trop gros
échoue en silence, sans message, en laissant des textes anglais toute la
session.

**c) Le zip est fabriqué sous un nom provisoire** (`.neuf`) et n'est mis en
place qu'une fois **tous** les contrôles passés. C'était le défaut de fond :
l'ancien script écrivait le zip officiel **en premier** et le vérifiait
ensuite — quand les garde-fous se réveillaient, le zip mort avait déjà pris la
place du bon. L'archivage de la version précédente a été déplacé au même
endroit : archiver avant les contrôles gardait une copie même quand le neuf
est refusé.

**Testé dans les deux sens**, sur un arbre de jeu fabriqué pour l'occasion
(le vrai `dist/` n'a pas été touché) :

| | résultat |
|---|---|
| **Arbre sain** | zip produit, **code retour 0** |
| **Un seul `.lua` cassé** (une parenthèse) | **refus**, code retour 1, message exact de Lua 5.1 : `Core.lua:2: <name> or '...' expected near 'return'` |

Et le point qui compte : après le refus, **le zip officiel était intact à
l'octet près** (2 246 octets avant, 2 246 après). Le zip refusé est laissé en
`.neuf` pour que tu puisses l'ouvrir.

Ça a aussi servi pour de vrai aujourd'hui : la même doctrine, appliquée à
`generer_noms_objets.py` au lot 3, a posé `DB_ObjetsNoms.lua` (18,7 Mo,
195 467 entrées) en écrivant à côté, en vérifiant 97 734 clés sur 97 734 en
Lua 5.1, puis en déplaçant. Aucun fichier plat n'est resté derrière.

---

### 3. Le tri des 22 bancs

**16 verts, 6 rouges.** Journal complet des sorties :
`rapports/bancs_essai.txt`.

Bonne nouvelle d'entrée : **`verifier_options.py` est passé au vert** — il
était dans ta liste des rouges, il ne l'est plus.

**Les 16 verts :** `addon`, `canal`, `deplie`, `fiches`, `globalstrings`,
`glue`, `hdv`, `hub`, `metiers`, `motifs`, `options`, `plaques`, `quetes`,
`sorts`, `suivi`, `tout`.

**Les 6 rouges.** Chaque verdict a été posé puis **attaqué par une seconde
lecture indépendante** chargée de le réfuter ; les six ont tenu.

| Banc | Verdict | En une ligne | Risque joueur | Coût |
|---|---|---|---|---|
| `verifier_barres.py` | **à réparer** | Le banc oublie de cocher l'option : depuis la 1.7.5 la traduction des noms au-dessus des monstres est **désactivée par défaut**, donc l'addon se tait — et c'est voulu. | aucun | petit |
| `verifier_infobulle.py` | **à réparer** | Il plante sur son propre simulateur (fausse info-bulle sans `IsShown`) ; une ligne ajoutée et 7 vérifications sur 8 passent. | faible | petit |
| `verifier_objets.py` | **à réparer** | Même trou exactement : `IsShown` manque à la fausse info-bulle. Une ligne, et c'est **18 ok / 0 échec**. | aucun | petit |
| `verifier_repliques.py` | **à réparer** | Il lui manque `CreateFrame`, **et** il lit la base des répliques dans un format qu'elle n'a plus (paresseux par texte depuis la 2.0.1). | aucun | moyen |
| `verifier_interface.py` | **périmé** | Il vérifie la traduction en masse de l'interface, que tu as **coupée volontairement** (doctrine taint) : `TRADUIRE_INTERFACE = false`. | aucun | moyen |
| `verifier_signalements.py` | **périmé** | Il rejoue le `/afr signaler` **d'avant la fenêtre de propositions** : l'addon ouvre désormais une fenêtre que son décor ne sait pas construire. | aucun | moyen |

**Aucun des six ne dénonce un vrai défaut de l'addon.** Quatre sont des
simulateurs en retard sur le jeu, deux testent une mécanique que le projet a
changée depuis. Vérifié à chaque fois en faisant tourner le code, pas en le
lisant : par exemple pour `verifier_repliques`, 250 couples anglais → français
rejoués sur la **vraie** base livrée, à travers les 4 événements de chat —
0 échec.

#### Trois choses que le tri a sorties, et qui comptent plus que le tri

**a) `verifier_repliques.py` deviendrait un FAUX VERT si on le réparait à moitié.**
En ajoutant seulement le `CreateFrame` manquant, il affiche « aucune réplique
lue dans la base » et **rend quand même 0**. Deux `return 1` (lignes 75 et 90)
sont avalés parce que `main()` est appelé ligne 136 sans que sa valeur soit
utilisée. Un banc qui passe au vert en ne testant rien est pire que le rouge
d'aujourd'hui : au moins le rouge se voit.

**b) Les 7 « ok » de `verifier_interface.py` sont creux.** Ils passent parce que
**rien n'est écrit du tout**, pas parce que les garde-fous fonctionnent — et 7
d'entre eux passeraient aussi avec le drapeau remis à `true`. Ce banc n'a plus
de signal dans aucun sens.

**c) Deux trous de couverture, que personne ne surveille :**
- `Modules/InterfaceCiblee.lua` n'est couvert par **aucun** banc ;
- `AppliquerCanalMoteur()`, le seul circuit d'écriture encore **vivant** de
  `InterfaceUI.lua`, n'est couvert par aucun banc non plus (il s'exécute
  pourtant en jeu : ses clés sont bien dans `DB_Interface.lua`).

C'est peut-être le vrai enseignement : la couverture ne manque pas là où les
bancs sont rouges, elle manque là où il n'y en a pas.

---

### Ce qui attend ta décision

**Je n'ai réparé aucun banc** — tu as dit que supprimer un banc périmé est une
décision, pas un nettoyage. Voici comment je les rangerais :

1. **Trois réparations à une ligne**, sans risque et sans arbitrage :
   `verifier_objets` et `verifier_infobulle` (ajouter `IsShown` à la fausse
   info-bulle, exactement comme `verifier_signalements.py:64` le fait déjà) et
   `verifier_barres` (poser l'option et `IsAddOnLoaded`). Trois bancs vivants
   récupérés pour presque rien.
2. **`verifier_repliques` : à réparer, mais pas à moitié** — sinon faux vert.
   Trois corrections : `CreateFrame`, lire les seaux `C[]`/`M[]` au lieu des
   lignes `DB[]`, et remplacer les `return 1` par `sys.exit(1)`.
3. **`verifier_interface` et `verifier_signalements` : périmés, mais je ne les
   supprimerais pas.** Pour `signalements`, le fond est toujours vivant
   (capture d'infobulle, refus des doublons, journal des échecs, auto-guérison)
   et tout repasse une fois le décor modernisé. Pour `interface`, la seule
   réparation honnête serait de le réécrire contre `InterfaceCiblee.lua` —
   surtout pas de relâcher ses assertions actuelles, ça détruirait le peu qui
   lui reste.

**Un écart connu à consigner, pas à corriger** : `verifier_infobulle` garde une
8ᵉ attente en échec après réparation du stub. Elle n'est pas fausse — l'addon
**dénude volontairement** les codes couleur pendant l'alignement
(`Sorts.lua:79`, décision documentée qui a débloqué 3 646 sorts). Le bloc
inséré par `@s:` ressort donc sans ses `|cffFFFFFF…|r`. C'est cosmétique et
assumé ; il faut le noter comme écart connu plutôt que relâcher l'attente.

**Un angle mort mesuré au passage** : le filtre anti-bruit du journal
(`Tooltips.lua:329-345`) compare les 12 premiers caractères de l'affiché au
modèle anglais **brut**. Quand une variable tombe dans ces 12 caractères, un
vrai échec d'alignement n'est jamais journalisé — **3 416 modèles sur 47 876**,
soit 7,1 % de `DB_Sorts.lua`. Aucun effet pour le joueur (le journal n'affiche
rien), mais quelques ratés restent invisibles au Compagnon.

### Vérifications

- `verifier_tout.py` : **code retour 0**, 48 fichiers compilés en `lupa.lua51`.
- Barrière du zip testée dans les deux sens (voir le tableau).
- pyflakes muet sur `construire_zip_release.py` et `mesurer_constantes.py`.
- Le vrai `dist/AscensionFR_manuel.zip` **n'a pas été touché** : les essais ont
  tourné sur un arbre et un `dist/` fabriqués dans un bac à sable.
- Aucune traduction modifiée par ce lot.
