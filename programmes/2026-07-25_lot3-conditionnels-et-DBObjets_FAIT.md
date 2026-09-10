# Demande de code → Claude Code

**Date :** 2026-07-25 · **suite des lots 1 et 2 — deux sujets, dont un bloquant**

**Objectif (le QUOI, pas le comment) :**

> Merci pour les deux lots : tes vérifications ont rattrapé une erreur de ma part sur
> « Unleash » (le glossaire est corrigé, voir plus bas) et tu as remonté un blocage réel.
> Deux choses maintenant, dans cet ordre.

---

## 1. 🔴 BLOQUANT — `DB_Objets` ne peut plus être régénéré

C'est le point le plus important : **tant qu'il n'est pas réglé, la 3.4 ne peut pas
embarquer les nouveaux objets.**

Tu as constaté qu'un `generateur_db` sur `DB_Objets` fait déborder la limite de constantes
de Lua (*constant table overflow*), à cause des ~5 000 objets accumulés. Tu as restauré la
version valide — bien joué, et merci de l'avoir dit plutôt que de livrer un fichier cassé.

**Ce que je te demande :**
1. **Comprendre la vraie structure avant de corriger.** J'ai regardé le fichier : il
   commence par « Fichier PARESSEUX généré par `outils/optimiser_memoire.py` » et contient
   déjà **4 601 sous-tables numérotées**. Il n'est donc pas « une seule table » au sens
   naïf — le découpage existe mais ne suffit plus. Dis-moi où la limite est réellement
   atteinte : nombre de constantes par fonction ? par seau ? taille d'un seau devenu trop
   gros ?
2. **Corriger le générateur, pas le fichier.** Un `DB_Objets` réparé à la main serait
   écrasé au prochain passage de l'Atelier. La correction doit vivre dans
   `generateur_db.py` / `optimiser_memoire.py`.
3. **Vérifier le voisinage.** `DB_ObjetsNoms` tient avec ses 58 seaux, mais il grossit
   aussi. Est-ce que d'autres bases sont proches de la limite ? Je préfère savoir
   maintenant que le découvrir à la prochaine version.
4. **Barrière :** `verifier_tout.py` propre **et** compilation `lupa.lua51` de `DB_Objets`
   régénéré — c'est la seule preuve qui compte, la taille du fichier ne dit rien.

## 2. 🟢 Le correctif des conditionnels `$?...[ ]` — feu vert

Ton diagnostic est net et je le suis : `MOTIFS_PROTEGES` (`traducteur_fr.py` l.63) avale le
contenu des crochets ; l'addon côté Lua est **déjà prêt** (`appliquer_valeurs` re-traduit
chaque branche via le préfixe `$?condXXX`) ; `MOTIFS_VARIABLE` n'a pas à bouger.

**Applique-le**, avec ces garde-fous :
- **Un échantillon d'abord.** Traduis **20 phrases internes** et montre-moi le résultat
  avant de lancer les ~292. Si le rendu est bon, enchaîne.
- **En jeu, pas seulement en base.** « Être dans la base ≠ s'afficher » — vérifie qu'une
  description conditionnelle corrigée s'affiche bien, branches comprises.
- Les 29 cas `@req:` / `@learns:` restent hors périmètre.

---

## Deux points que tu m'as remontés et que j'ai tranchés

**Ta correction sur « Unleash » était juste, et le glossaire est à jour.** J'avais lu
« Unleash: » (le mot-clé, avec deux-points) dans les signalements des joueurs et généralisé
la règle à toutes les occurrences — alors qu'elles étaient **toutes des verbes** dans
`sorts.json`. « Déchaînement : un Brise-Serment dévastateur » aurait été du charabia.
`4-reference/GLOSSAIRE.md` distingue désormais les deux cas explicitement. **Ta forme
« Déchaînez / Déchaîner » est la bonne, on la garde.**

**La majuscule des Parchemins : tu as bien fait d'étendre.** J'avais annoncé 4 occurrences,
tu en as trouvé 55 (dont 51 dans `sorts.json`, `objets_dbc.json`, `gossip.json`). C'est le
même nom partout, et le glossaire dit minuscule — **on garde ta correction**, pas de retour
en arrière. Vérifié de mon côté : **0 « Parchemin du Gardien » restant.**

## Trois choses laissées de côté volontairement (je les note pour plus tard)

- **`Realm Bound`** est une GlobalString, pas un objet — et l'application en masse des
  GlobalStrings est coupée par la doctrine taint. À traiter par interception d'affichage,
  comme le reste : c'est un chantier, pas une correction. On verra après la 3.4.
- **`Stormwind Gate` / `Food Crate`** sont des objets de monde (gameobjects). Ta réponse
  ouvre une vraie piste : **tous les noms de lieux dans les gameobjects** sont dans le même
  cas. Chiffre-le quand tu auras un moment — si c'est cent noms, ça vaut un lot à soi seul.
- **Talents CoA** : merci pour la racine (les descriptions ne sont pas dans les extraits
  WDB ; le CoA builder ne donne que la structure). C'est le gros chantier d'après —
  ~120 des 204 signalements. On l'attaque une fois la 3.4 sortie.

---

**« Terminé » veut dire :**

> - `DB_Objets` régénérable, correction **dans le générateur**, compilation `lupa.lua51`
>   vérifiée, et un mot sur les autres bases proches de la limite.
> - Correctif des conditionnels appliqué après validation de l'échantillon de 20.
> - `verifier_tout.py` propre.
> - **Ne rien publier, ne rien pousser.** Le build de la 3.4 fera l'objet d'une demande à
>   part, une fois que Dan aura relu les textes.

**Validation :**

> Autonome sur les deux points. **Arrête-toi et dis-le-moi** si le correctif de `DB_Objets`
> demande de changer le format des bases livrées — ça toucherait l'addon, donc les joueurs,
> et ça mérite que Dan le sache avant.

---
## Réponse de Claude Code

**Fait le 26/07/2026. Les deux points sont réglés. Rien n'a été publié ni poussé.**

---

### 1. 🔴 `DB_Objets` — régénérable

**Où la limite est réellement atteinte : ni « par seau », ni « une seule table ».**
Lua 5.1 — donc le client de WoW 3.3.5a — n'accepte que **262 143 constantes par
PROTOTYPE de fonction** (`MAXARG_Bx`, `lcode.c addk`). Une constante, c'est une
chaîne **distincte** ou un nombre **distinct** : Lua dédoublonne, mais chaque
identifiant d'objet reste un nombre distinct.

Le fichier que tu as regardé était déjà le paresseux (2 184 seaux — le « 4 601 »
devait venir d'un état intermédiaire). **Ce n'est pas lui qui débordait.** Ce qui
débordait, c'est la version **PLATE** que `generateur_db.py` écrit d'abord :

| | |
|---|---|
| entrées | 355 320 |
| constantes réclamées | **587 415** |
| limite Lua 5.1 | 262 143 |
| dépassement | **× 2,24** |
| tiennent dans un chunk plat | 156 424 seulement (dichotomie, k = 262 143 pile à la rupture) |

Le point important : **les 355 320 identifiants SEULS dépassent déjà la limite.**
Aucun réglage de texte ne pouvait sauver ce format — il fallait changer de forme.
Et la taille du fichier ne dit effectivement rien : 26 Mo au format paresseux se
compilent en 0,1 seconde.

**La vraie panne était ailleurs, et plus grave.** `optimiser_memoire.py` n'est
accroché qu'à la **fin d'`ingerer_recolte.py`**. Or **quatre** chemins régénèrent
cette base, et trois ne le rappellent jamais :

- `mise_a_jour.py` étape « 6/6 Régénération des bases » ;
- `traducteur_fr._generer()` (mode `--une-fois`) ;
- l'étape « Sorts en attente » de l'Atelier, qui est la **dernière** ;
- `generateur_db.py` lancé seul.

Chacun laissait derrière lui un `DB_Objets.lua` plat, donc un addon **mort au
chargement**, sans un mot. Et la vérification finale de l'Atelier ne regardait
même pas ce fichier.

**Correctif — dans le générateur, et le format livré n'a pas bougé.**
`ecrire_db(..., paresseux=True)` produit DB_Objets directement en seaux : le
fichier plat **n'existe plus jamais sur le disque**. Les quatre chemins sont
réparés d'un coup, sans toucher à l'orchestration (ce qui compte, l'exe de
l'Atelier étant figé : lui appelle les `.py`, qui sont bien relus).

Preuve que je n'ai rien changé pour les joueurs : le Lua produit est **ligne pour
ligne identique** à celui d'aujourd'hui (2 187 lignes utiles, comparaison faite) —
seules les 4 lignes de commentaire d'en-tête diffèrent. **Il n'y a donc aucune
décision à prendre de ton côté** : l'addon n'a rien à savoir.

**Barrière (la seule preuve qui compte) :**
- `DB_Objets.lua` régénéré compile en `lupa.lua51` : **OK, k = 4 372 (1,7 %)** ;
- les **2 184 seaux** compilent aussi un par un, comme le jeu le fait à
  l'exécution — pire seau : 1 632 constantes, soit **0,62 %** ;
- `verifier_tout.py` : **code retour 0**, 48 fichiers, aucun jeton oublié ;
- `verifier_motifs.py` (verrou addon/traducteur) : **0 échec** ;
- pyflakes muet sur tout ce que j'ai touché.

**Garde-fou, pour ne plus jamais le découvrir en jeu.** `ecrire_db` compte les
constantes en écrivant : alerte à 80 %, et **au-delà de la limite il n'écrit
pas** — l'ancienne base, elle, se charge encore. Mieux vaut un contenu d'hier
qu'un addon mort. `generateur_db.main()` et `generateur_sorts.py` rendent 1 dans
ce cas, donc la chaîne s'arrête au lieu d'annoncer une réussite.

---

### 2. Le voisinage — deux surprises, plus sérieuses que la question posée

Nouvel outil `outils/mesurer_constantes.py` : il **mesure** au lieu d'estimer
(il compile, prend `string.dump`, lit `sizek` dans le bytecode). Branché dans
`verifier_tout.py`, la marge est désormais affichée à chaque passage.

| base | constantes | part | remarque |
|---|---|---|---|
| **DB_Sorts** | 130 318 | **49,7 %** | plat, le plus chargé — ~55 000 sorts de marge |
| DB_Creatures | 96 928 | 37,0 % | plat, grossit avec la TDB et les royaumes |
| **DB_ObjetsNoms** | 86 507 | **33,0 %** | ← pas 0,1 %, voir ci-dessous |
| DB_HautsFaits | 58 626 | 22,4 % | plat |
| DB_Quetes | 49 522 | 18,9 % | plat |
| DB_Objets | 1 632 | 0,6 % | paresseux, borné par construction |

**Surprise n° 1 — deux garde-fous compilaient en Lua 5.5, pas 5.1.**
Le danger que le doc annonçait en 3.44 (« une grammaire plus récente peut aussi
ACCEPTER ce que 5.1 refuserait ») s'est réalisé. `outils/collecteur.py`
(vérification finale de l'Atelier) et `outils/paresseux_textes.py` (le contrôle
qui **autorise l'écriture**) utilisaient le lupa par défaut. Mesuré : un chunk à
300 000 constantes **passe en 5.5 et échoue en 5.1**. Autrement dit, l'Atelier
affichait « Syntaxe Lua : OK — rien de cassé » sur exactement la panne qui
bloquait la 3.4. Les deux sont passés en `lupa.lua51`. (`ingerer_recolte.py` et
`compagnon.py` gardent le défaut : ils *lisent* des SavedVariables, ce n'est pas
une barrière.)

**Surprise n° 2 — `DB_ObjetsNoms` n'est pas à 0,1 %, il est à 33 %.**
Tu avais raison de t'en inquiéter. Deux choses :

- Sur une base paresseuse, le jeu **recompile chaque seau à l'exécution**
  (`loadstring`, Core.lua). Chaque seau est un prototype soumis au même plafond.
  Regarder le fichier seul est un angle mort **total** : un seau trop gros ne
  compile pas, Core.lua avale l'échec (`if not usine then return nil end`), et
  tous les noms de ce seau restent anglais **pour toute la session, sans un
  message**. `mesurer_constantes.py` mesure donc aussi les seaux.
- `paresseux_textes` range par **premier octet de la clé**, sans rééquilibrer :
  le seau « B » porte 43 464 noms à lui seul, soit 22 % de la base. Les seaux de
  512 identifiants d'`optimiser_memoire`, eux, sont bornés d'avance. Si le
  méga-lot ItemAddon triple, **c'est ce seau-là qui cassera**.

**Et le même défaut que DB_Objets, en pire.** `generer_noms_objets.py` et
`generer_noms_sorts.py` posaient leur version **plate sur le chemin livré**, puis
la convertissaient dans un `try/except` dont personne ne lisait le résultat — or
`transformer()` rend `False` **sans lever**. Le plat de DB_ObjetsNoms pèse
~388 000 constantes, soit **148 % de la limite** : à la moindre conversion ratée,
ce fichier mort restait en place sous le message *« la base plate reste
valable »*, qui était faux. Nouveau `paresseux_textes.poser()` : on écrit à côté,
on convertit, **on ne déplace qu'en cas de succès**, et on sort en erreur sinon.
Testé dans les deux sens (succès et échec).

---

### 3. 🟢 Les conditionnels `$?...[ ]` — appliqué

**Ton diagnostic était juste, mais le correctif ne pouvait pas être « changer la
ligne 63 ».** `MOTIFS_PROTEGES` est lue par quatre outils, dont
`verifier_motifs.py`, qui la **verrouille contre `MOTIFS_VARIABLE` de l'addon** —
et l'addon, lui, a besoin du conditionnel **entier** (`interieur_crochets` va
chercher la branche dedans). La toucher cassait le verrou.

J'ai donc laissé `MOTIFS_PROTEGES` **rigoureusement inchangée** (vérifié par
empreinte) et ajouté à côté `MOTIF_BOUCLIER` : ce qu'on cache réellement au
traducteur, où seul le **sélecteur** `$?s118174` est protégé.

Deux détails qui auraient tout fait échouer si je les avais manqués :

- **`codes_intacts()` devait passer au bouclier aussi.** Elle comparait le
  conditionnel entier avant/après : `[ and reducing…]` contre
  `[ et réduisant…]` → toute traduction **réussie** aurait été rejetée comme
  « code perdu », et les descriptions seraient restées anglaises.
- **Une branche purement numérique est indiscernable d'un jeton.** Le texte du
  jeu contient de vrais `[2]` (« $?s118174[6][5] ») ; exposés tels quels, ils
  auraient été remplacés par le mauvais code à la restauration. Le bouclier
  avale donc les branches sans lettre, et met `[12]` à l'abri.

**Contrôle sur tout le corpus : 1 566 104 textes passés en aller-retour
protéger → restaurer, 0 abîmé.** (Avec la première version du motif, il y en
avait 1 — la description de « Gore ».)

**Échantillon, puis vérification EN JEU.** J'ai fait les 20 demandés, le rendu
était bon, j'ai enchaîné. Mais « être dans la base ≠ s'afficher » : j'ai chargé
`Core.lua` + `Modules/Sorts.lua` dans lupa et fait tourner **le vrai moteur de
l'addon** sur l'info-bulle que le client afficherait, branche par branche.
Avant / après, même sort, même affichage client :

```
client : Increases your block value by 42%. While active your Shield Slam has…
AVANT  : Increases your block value by 42%. While active your Shield Slam has…
APRÈS  : Augmente votre valeur de blocage de 42%. Lorsqu'il est actif, votre…
```

```
client : …Generates 1 stack of |cffffffffSoif|r.
AVANT  : …Generates 1 stack of Soif.
APRÈS  : …Génère 1 pile de Soif.
```

**Résultat : 420 descriptions concernées** (plus que les ~292 estimés),
**411 réparées**. Sur les 9 restantes : **5 n'avaient rien à traduire**
(« [10 sec.][30 sec.] », « [2min][3min] » — déjà du français) et **4 ont été
gardées en anglais volontairement**, parce que Google y abîmait un code
(il a transformé le jeton `[1]` en `1]`, et déplacé des crochets). Le garde-fou
a préféré l'anglais à un texte cassé, ce qui est la bonne décision.

Après régénération, sur **1 433 sorts à conditionnel dans `DB_Sorts.lua`**, il
reste **14 entrées** en anglais — ce sont ces 4 textes, réutilisés par plusieurs
sorts. L'anglais restant ailleurs est dans le champ `DE` (le modèle), où il doit
être.

Nouvel outil : `outils/retraduire_conditionnels.py` (`--echantillon N` pour
regarder sans rien écrire). Il est **chirurgical** : il ne retraduit que le
conditionnel figé, jamais la description entière — ton français déjà relu n'est
pas touché. Sauvegarde dans `traductions/sorts_avant_conditionnels.json`.

Les 29 cas `@req:` / `@learns:` n'ont pas été touchés.

---

### Ce qui attend une décision de toi

**Vocabulaire** (je ne tranche pas là-dessus) — trois choses vues dans les
traductions produites :

- « Generates 20 **Static** » → « Génère 20 **statiques** ». *Static* est une
  ressource de classe d'Ascension, pas un adjectif.
- « Arathi Basin » → « bassin d'Arathi » (le nom officiel Blizzard est
  **Bassin Arathi**), et « Warsong Gulch » est resté anglais (**Goulet des
  Warsong**).
- « Shield Slam » est resté anglais ; « Blessed Vengeance » aussi, alors que
  « Demonic Brutality » a été traduit — c'est incohérent. Le pont des noms de
  sorts en rattrape peut-être une partie à l'affichage, mais ça mérite ton œil.

**Un outil silencieusement mort, hors périmètre** (j'ai posé une tâche à part) :
`outils/corriger_recettes.py` lit `DB_Objets.lua` avec un motif qui n'existe que
dans le format plat. Depuis le passage au paresseux (21/07), il ne trouve **rien**
et ne le dit pas. Je ne l'ai pas réparé : ça changerait des traductions que tu
n'as pas demandé de toucher.

**Deux angles morts que je te signale sans les avoir corrigés :**
`construire_zip_release.py` relit chaque `.lua` du zip (pseudos, webhook,
version) mais n'en **compile aucun** ; et `verifier_tout.py` n'est appelé par
aucun code — uniquement par ton rituel de build. La barrière repose donc
entièrement sur toi qui la lances.

---

### Fichiers touchés

| fichier | ce qui change |
|---|---|
| `outils/generateur_db.py` | `paresseux=True` pour DB_Objets ; compteur de constantes (alerte 80 %, refus au-delà) ; `SATURATIONS` remis à zéro |
| `outils/optimiser_memoire.py` | découpé en `enseauter()` / `poser` réutilisables ; reste appelable seul (filet) |
| `outils/generateur_sorts.py` | sort en erreur si DB_Sorts sature |
| `traducteur_fr.py` | `MOTIF_BOUCLIER` ; `proteger()` et `codes_intacts()` l'utilisent. `MOTIFS_PROTEGES` **inchangée** |
| `outils/verifier_tout.py` | affiche la marge de chaque base, seaux compris |
| `outils/collecteur.py`, `outils/paresseux_textes.py` | `lupa.lua51` au lieu du défaut (5.5) |
| `outils/generer_noms_objets.py`, `outils/generer_noms_sorts.py` | ne posent plus le format plat sur le chemin livré |
| `outils/mesurer_constantes.py` | **nouveau** — mesure exacte, fichiers et seaux |
| `outils/retraduire_conditionnels.py` | **nouveau** — dégèle les conditionnels |
| `traductions/sorts.json` | 411 descriptions réparées (sauvegarde à côté) |
| `docs/CONTEXTE_PROJET.md` | section 3.67, le piège complet |

Les bases de l'addon ont été régénérées (`generateur_sorts.py` puis
`generateur_db.py`, code retour 0). Le dossier `DB/` d'avant a été sauvegardé
avant toute manipulation. **Rien n'a été publié, rien n'a été poussé.**
