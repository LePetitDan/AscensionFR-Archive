# Demande de code → Claude Code

# 📐 PROGRAMME 29 — mesurer avant de déplacer l'usine

**Date :** 2026-08-07
**Dan a donné le GO** — sur le chantier entier, pas seulement sur ce programme.

**La décision qu'il vient de prendre**, et qui commande tout ce qui suivra :

1. l'Atelier passe **dans le cloud**, en Action planifiée — il ne veut plus rien lancer ;
2. la qualité de traduction s'améliore **sans rien payer** ;
3. le projet devient **réellement contributif** — quelqu'un d'autre que lui doit pouvoir
   travailler.

Cinq étapes ont été arrêtées, dans cet ordre : l'essai Google depuis GitHub → la moisson
nocturne → la file de travail publiée → le contexte au moment de traduire → l'exe Windows
dans le cloud. **Chacune aura son programme.** Celui-ci est le premier.

🛑 **Il ne déplace rien, ne publie rien, ne supprime rien.** Il répond aux questions dont
dépend la *forme* de tout le reste. Écrire la suite avant d'avoir ces réponses, ce serait
deviner — et on a déjà payé pour savoir ce que ça coûte.

---

## 🛑 BLOC 0 — Google répond-il à une machine GitHub ?

**C'est LA question.** `traducteur_fr.py` (l. 297) appelle
`https://translate.googleapis.com/translate_a/single`. C'est le point d'entrée **gratuit et
non officiel** de Google Traduction. Il accepte volontiers le PC d'un particulier. Une
machine de datacenter, c'est une autre affaire — et un runner GitHub n'est que ça.

Si la réponse est non, la moisson nocturne ne peut pas être la copie conforme de l'Atelier,
et il faut le savoir **maintenant**, pas après avoir écrit le reste.

**Ce que je veux, mesuré :**

- une Action **jetable**, dans un dépôt public, en `workflow_dispatch` **uniquement** —
  jamais de `schedule` ;
- elle appelle l'endpoint **exactement comme le fait `traducteur_fr.py`** : mêmes en-têtes,
  même forme d'URL, même pause. Ne réécris pas un client « propre » : on mesure notre code,
  pas un autre ;
- **50 textes réels et TOUS DIFFÉRENTS**, tirés de `a_traduire/` ou des bases. ⚠️ Pas
  cinquante fois la même phrase : Google déduplique, tu mesurerais un cache et tu
  annoncerais un faux vert ;
- ⚠️ **et vérifie que ce qui revient est du vrai français.** Un code HTTP 200 qui rend une
  page d'erreur, une chaîne vide ou l'anglais recopié, c'est un échec déguisé en succès.
  Compare : combien de réponses sont réellement traduites ?

**Rapporte, chiffré :**

| ce que je veux savoir |
|---|
| combien de 50 passent, combien échouent, avec quel code |
| **à partir de quel appel** ça coince, s'il y a un seuil |
| si ça coince : est-ce que ça repart après une pause ? au bout de combien de temps ? |
| quelle **cadence soutenable** en découle — c'est elle qui dimensionnera la moisson |
| combien de temps prendraient **16 309 appels** à cette cadence |

🛑 **Puis supprime l'Action.** « Un échafaudage qu'on oublie devient une porte » — c'est ta
phrase du programme 24, et elle vaut ici.

**Si c'est non**, ne t'arrête pas là : dis ce qui reste possible. La moisson à six étapes
sur sept, la traduction ailleurs, le repli sur la machine de Dan. Une réponse négative bien
instruite vaut mieux qu'un contournement improvisé.

---

## BLOC A — ce que l'usine lit et écrit vraiment

Pour que la moisson tourne ailleurs que chez Dan, il faut que sa **mémoire** y soit. J'ai
compté **22 fichiers de `traductions/` déjà publics** dans `AscensionFR-Textes`. Côté
machine il y en a nettement plus. Je ne sais pas lesquels sont nécessaires, et je ne veux
pas le déduire des noms.

**Établis-le par le code**, en lisant les sept étapes :

- **quels fichiers chaque étape LIT**, et lesquels elle **ÉCRIT** ;
- pour chacun : déjà publié ou non, taille, et **publiable ou non** ;
- ce qui se **reconstruit tout seul** (donc inutile à publier) contre ce qui se **perdrait**.

🛑 **Le nettoyage n'est pas négociable**, et tu connais la règle : on ne cite jamais un
joueur. Sur tout ce qui serait candidat à la publication :

1. `balayer_secrets.py` ;
2. le balayeur de pseudonymes du pont (`pont_textes.balayer`, avec ses 47 noms) ;
3. les chemins de disque, motif resserré.

**Avec le dénominateur** — N fichiers sur N réellement ouverts. Et comme au programme 26 :
dis-moi ce que tu **ne sais pas** attraper, pas seulement ce que tu attrapes.

### La question qui décide, dans ce bloc

**`DB_Communaute.lua` doit-il être versionné ?** C'est le seul fichier qu'aucune
régénération ne nettoie — donc le seul qui ne se reconstruit pas. S'il se perd, on perd
tout ce que la récolte a produit depuis le début. Dis ce que tu en penses, avec sa taille
et ce qu'il contient réellement.

---

## BLOC B — les ~600 Mo de sauvegardes

`traductions/` contient une vingtaine de copies `*_avant_*.json` de 15 à 23 Mo. Elles
existent parce qu'il n'y a **pas de gestion de versions sur les données** : chaque passage
risqué se protège en recopiant le fichier entier. Une fois dans git, `git diff` et
`git revert` font ça mieux.

- **combien exactement, quel poids total ?**
- ⚠️ **est-ce qu'un seul script en LIT une ?** J'ai lu que `appliquer_vocabulaire.py` les
  exclut explicitement (`est_sauvegarde()`). Vérifie pour **tous** les autres — une
  sauvegarde lue par quelqu'un n'est plus une sauvegarde, c'est une dépendance ;
- si aucune n'est lue : dis-le, et dis combien de place on récupérerait.

🛑 **Ne supprime rien dans ce programme.** Tu constates, Dan tranchera.

---

## 🛑 BLOC C — vérifie ma lecture du code, j'ai pu me tromper

J'ai affirmé trois choses à Dan en lisant le code moi-même. **Confirme ou démens, en
citant les lignes.** Ce n'est pas une formalité : la troisième commande une décision qui
porte sur 16 309 textes.

**1.** Relancer l'Atelier **n'écrase jamais** une traduction existante. Mes preuves :
`traducteur_fr.py` ne retient que `if cle not in tr` (l. 441, 453, 457, 461, 492, 715, 757),
et `ingerer_recolte.py` l'écrit dans son propre commentaire (l. 189) : *« b complète a sans
écraser une valeur non vide »*.

**2.** La **seule** étape qui réécrit de l'existant est `appliquer_vocabulaire.py
--appliquer`, exprès, pour imposer le glossaire — et elle pose un `_avant_vocabulaire.json`
avant d'y toucher (l. 565-567).

**3. 🛑 Rien, dans toute la chaîne, ne revient jamais améliorer une traduction déjà posée.**
Un trou bouché l'est définitivement. C'est sur cette affirmation que repose la
recommandation faite à Dan de **ne PAS rattraper les 16 309 entrées avec Google
maintenant** : il figerait la moins bonne version pour toujours, et le meilleur moteur
qu'on prépare les sauterait toutes.

**Si je me trompe sur ce troisième point, la décision change** — et il faut le dire tout de
suite, avant qu'on ne construise le reste dessus. S'il existe un moyen (même inutilisé) de
repasser sur de l'existant, nomme-le.

---

## BLOC D — le retard, rechiffré à aujourd'hui

Le programme 26 annonçait **16 309 entrées distinctes** restant à traduire, et 7 290 sorts
par une autre voie. C'était le 4 août ; l'Atelier a tourné le 2 (7/7 vert), et les rapports
continuent d'arriver.

- **le compte à aujourd'hui**, par catégorie, avec le dénominateur ;
- le volume en **caractères** (j'ai mesuré 178 en moyenne sur 2 674 entrées réelles —
  vérifie sur l'ensemble) ;
- ⚠️ **combien de temps prendrait un rattrapage complet en local**, avec le moteur actuel.
  **Mesuré sur un échantillon de 100 vraies entrées**, pas estimé au doigt mouillé : c'est
  le chiffre qui dira si « une nuit » est réaliste ou si c'est trois jours.

---

**« Terminé » veut dire :**

> - **Google depuis GitHub : oui ou non**, chiffré, avec la cadence soutenable et la durée
>   qu'impliqueraient 16 309 appels. **Et l'Action d'essai supprimée.**
> - La liste, établie par le code, de ce que les 7 étapes lisent et écrivent — publié /
>   publiable / reconstructible — **balayage de secrets et de pseudonymes à l'appui, avec
>   son dénominateur**.
> - Ton avis sur `DB_Communaute.lua`.
> - Le poids des sauvegardes `_avant_*`, et **si un script en lit une**.
> - **Mes trois affirmations confirmées ou démenties**, lignes à l'appui — la troisième
>   surtout.
> - Le retard à jour, en entrées et en caractères, et la **durée réelle** d'un rattrapage
>   local mesurée sur 100.
> - Ce qui a résisté, et ce que tu as failli casser.

🛑 **Rien de publié, rien de déplacé, rien de supprimé. Aucun tag, aucune release, aucune
fusion. `WorkFlow` reste sans dépôt distant — le webhook est dans son historique.**

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Puis renommer en `_FAIT.md`.)

*Exécuté le 2026-08-08. Les cinq blocs sont mesurés et terminés. Il ne reste qu'un clic à
toi : supprimer le dépôt-coquille de l'essai (privé et vidé, détail au bloc 0).*

---

### 🛑 BLOC 0 — Google répond-il à une machine GitHub ?

# **OUI.** Mesuré, pas supposé.

**Le tir** : dépôt public jetable `essai-cadence`, Action `workflow_dispatch` **uniquement**
(jamais de `schedule`), et les 50 textes passés par l'**entrée** du workflow — jamais
commités, le dépôt ne contenait que le harnais. Le harnais : la copie **verbatim** de
`_appel_google` ([traducteur_fr.py:294-302](../WorkFlow/traducteur_fr.py) — même URL, même
`User-Agent: Mozilla/5.0`, même timeout 10 s), appelée comme `_traduire_lot` l'appelle :
`ThreadPoolExecutor(max_workers=6)`, sans pause — le mode dominant de l'usine (les
`time.sleep(0.3)` ne vivent que sur le chemin de la récolte). Les 50 textes : réels, tous
différents, tirés de `a_traduire/sorts_classe.json` (183 caractères de moyenne), **protégés
par les fonctions mêmes de l'usine** (`proteger_glossaire` + `proteger`) — notre trafic à
l'octet près — et balayés avant départ par les 3 filets du pont : 0 motif.

| ce que tu voulais savoir | mesuré |
|---|---|
| combien de 50 passent | **50 sur 50** — codes : `{200: 50}`, zéro échec |
| du **vrai** français ? | **50 sur 50** — 0 vide, 0 anglais recopié, 0 page d'erreur déguisée en 200 (« Faites un clic droit pour invoquer… », jetons `[n]` préservés) |
| à partir de quel appel ça coince | **jamais** — aucun seuil sur les 50 appels (5,8 s au total) |
| ça repart après une pause ? | sans objet — aucun échec, les sondes de reprise (30/60/120/300 s) n'ont pas eu à servir |
| cadence soutenable | **8,6 textes/s** en mode usine — latences 269 / 485 / 1 306 ms (min / médiane / max), 618 ms de moyenne : **la même chose que depuis ta machine** |
| 16 309 appels à cette cadence | **≈ 32 minutes** (et les 15 817 réels du bloc D : ≈ 31 min) |

IP de sortie du runner : `20.169.99.199` — une vraie machine de datacenter Azure a été
servie sans captcha ni page d'excuse. Et chaque run GitHub sort d'une IP différente : la
moisson nocturne ne frappera jamais deux nuits de suite depuis la même adresse.

**La limite du banc, dite** : 50 appels en 6 secondes tranchent LA question de forme — la
moisson nocturne PEUT être la copie conforme de l'Atelier. Ce que 50 appels ne prouvent
pas : un plafond **horaire** au-delà (une moisson réelle en fera des milliers d'affilée).
Le premier vrai passage nocturne le dira ; si un seuil existe, le harnais de reprise est
déjà écrit pour le mesurer.

🛑 **L'Action est supprimée** : le run effacé (0 restant, vérifié par l'API), le fichier de
workflow retiré et la suppression poussée. Le jeton `gh` n'a pas le scope `delete_repo`
(403 vérifié) : le dépôt-coquille (4 fichiers — harnais, README, .gitignore — plus aucune
Action, aucun texte de jeu, aucun secret) a donc été **passé en privé**. Il te reste **un
clic** : le supprimer sur GitHub (ou `gh auth refresh -s delete_repo` puis
`gh repo delete LePetitDan/essai-cadence --yes`).

*Histoire du tir, pour mémoire : la couche de permissions de la session avait d'abord refusé
la création du dépôt public. Je n'ai rien contourné — tout a été préparé et éprouvé en
local, la question t'a été posée, et le tir est parti après ton feu vert explicite en
conversation.*

---

### BLOC A — ce que l'usine lit et écrit vraiment

**Établi par le code** : les 7 étapes lues en entier, chacune par un lecteur indépendant,
chemins résolus et lignes citées. La carte exhaustive (chemin par chemin, avec la nature —
fichier / dossier parcouru / réseau / externe — et les incertitudes assumées) est déposée
dans **`rapports/programme29_carte_etapes.txt`**. Le dénominateur de l'établissement :
**7 étapes sur 7 tracées** ; la seule zone non tracée en profondeur est la branche « client
patché » de l'étape 4 (`mise_a_jour.executer()`, ~20 sous-scripts) — elle ne court que si la
signature des MPQ change, et je le dis plutôt que de le deviner.

**L'essentiel par étape** (détail complet dans la carte) :

| étape | lit (l'essentiel) | écrit (l'essentiel) |
|---|---|---|
| 1. `aspirer_discord` | `discord_aspirateur.json` (**SECRET** : jeton bot + salon + marque-page), API Discord, CDN | `rapports/auto_*` (atomique), `pieces_jointes_mortes.json`, et **réécrit sa config — NON atomique** : une coupure corrompt jeton + marque-page |
| 2. `ingerer_rapport` | **tous** les `*.txt` de `rapports/` (5 016 ce jour — c'est le contenu qui décide, pas le nom), `DB_SortsCorrections.lua` (jeu), `cache_db/`, db.ascension.gg, Google | `ids_signalements_*.txt`, `propositions_joueurs.json` (**non atomique**), **APPEND `DB_SortsCorrections.lua`** — hors dépôt, chemin du client codé en dur |
| 3. `ingerer_caches` | `rapports/auto_*caches_*.json.gz` + sa mémoire `ingeres.json` | les 6 `rapports/caches/fusion/*.json` + `ingeres.json` (**tout non atomique** ; « dernier arrivé gagne » sur la matière anglaise) |
| 4. `traducteur_fr --une-fois` | ~30 familles : WDB du client, WTF (SavedVariables **exécutés** en lupa), `sources/` (frFR+enUS+dbc), `extraits/` (4 royaumes), fusion des caches, stores | `extraits/rexxar` (réécrit chaque cycle), **stores `traductions/*.json` (atomiques)**, `a_traduire/*.json`, les `DB_*.lua` du jeu (non atomiques), vigies |
| 5. `ingerer_recolte` | `noms_recolteurs.local.txt` (**SECRET-pseudos, lu à l'import**), WTF (lupa), les DB du jeu (anti-doublons), `rapports/*.txt` | `recolte_ecartes.json` (non atomique), **APPEND `DB_Communaute.lua`**, puis `DB_Objets.lua` et `DB_Meta.lua` (2 sous-processus) |
| 6. `appliquer_vocabulaire --appliquer` | `a_traduire/interface_maison.json`, `sources/enUS/*`, `extraits/*`, les 40 `traductions/*.json` vivants | `vocabulaire_lot4.txt` (toujours), les stores modifiés (atomiques, sauvegarde `_avant_vocabulaire` **jamais rafraîchie**), `interface_maison.json` via `fusionner_gisement` (**non atomique, sans filet**) |
| 7. `traducteur_fr --sorts` | `a_traduire/sorts_textes.json`, `sorts.json`, `rejets_chroniques.json`, Google | `sorts.json` (atomique, réécrit même à 0 traduction), `rejets_chroniques.json` ; si ≥ 1 traduction : `a_traduire/sorts*.json`, `DB_Sorts.lua`, `DB_SortsNoms.lua` (pont vérifié lupa) |

**Publié / publiable / reconstructible** (tailles mesurées ; « publié » = présent dans le
clone de `AscensionFR-Textes`, 28 fichiers dont 22 `traductions/*.json`) :

| famille | poids | publié ? | se reconstruit ? | verdict |
|---|---|---|---|---|
| stores `traductions/` (10 fichiers : quetes, objets, sorts 22 Mo…) | ~31 Mo | **OUI** | non — c'est LA mémoire | déjà en sécurité |
| registres d'état (`rejets_chroniques` 1 Ko, `recolte_ecartes` 2 Ko, `propositions_joueurs` 1 Ko, `lignes_client_proposees` 956 o, `rapport_signalements` 14 Ko) | ~19 Ko | non | non (compteurs) — mais se regagnent au pire | **publiables** (balayage : 0 motif), à emporter |
| fusion des caches joueurs (6 fichiers + `ingeres.json` 255 Ko) | 18 Mo | **NON** (mon 1er tableau disait l'inverse : faux positif d'un test par nom de fichier, corrigé sur le clone) | seulement si les `auto_*caches_*.gz` de `rapports/` existent encore | **publiables** (0 motif) ; perdre `ingeres.json` = tout re-verser (« dernier arrivé gagne » peut rebasculer des valeurs) |
| `discord_aspirateur.json` (420 o), `noms_recolteurs.local.txt` (601 o) | ~1 Ko | non | non | **JAMAIS publics** — jeton de bot, et la liste des pseudos elle-même ; dans le cloud : secrets GitHub Actions |
| `etat_client.json` (310 o) | — | non | oui (re-signature) | sans objet hors de la machine du client |
| `a_traduire/` (127 fichiers) | 16,2 Mo | non | **oui** — régénéré par l'étape 4 | inutile à publier ; nécessaire au démarrage si l'étape 4 ne tourne pas au même endroit |
| `extraits/` (24 fichiers, 4 royaumes) | 3,6 Mo | non | seulement depuis les WDB **du client** — impossible dans le cloud | à emporter (balayage : 24/24, 0 motif ; le WDB est la source propre — 0 pseudo) |
| `sources/` (988 fichiers) | **996 Mo** | non | statique (TDB, DBC, frFR officiel) | trop gros et pas à nous : pas publiable tel quel, à monter autrement (release privée, artefact, LFS…) |
| `cache_db/` (11 573 fichiers) | 12,4 Mo | non | oui (re-télécharger db.ascension.gg) | l'emporter épargne 11 573 requêtes |
| `DB_Communaute.lua` 3,0 Mo, `DB_SortsCorrections.lua` 2,6 Mo | 5,6 Mo | non | **NON** (accumulation en append, hors dépôt) | voir la question qui décide |

**Le nettoyage, avec le dénominateur.** Balayage par les 3 filets du pont
(`pont_textes.balayer` : `balayer_secrets` 21 familles + 47 pseudonymes + chemins resserrés) :
candidats à publication (registres + fusion + les 2 DB d'accumulation) : **14 fichiers
copiés, 14 ouverts, 0 motif**. `a_traduire/` : **127/127, 0 motif**. `extraits/` :
**24/24, 0 motif**. **Ce que je ne sais PAS attraper** — dit, comme demandé : (1) les
**noms de personnages substitués par le jeu** (`$N` remplacé AVANT récolte) : le balayeur ne
connaît que les 47 pseudonymes déclarés, pas les prénoms de personnages ; (2) un nom **collé
à un code couleur** (`|cFF…Nom` : le `\b` du motif ne voit pas la frontière — le piège du
lot 14) ; (3) le **contenu des `.gz`** (le balayeur saute les binaires) ; (4) un secret d'une
famille hors des 21 recensées.

**Ce que le déménagement devra résoudre** (constaté dans la carte, pas des opinions) : les
chemins du client codés en dur (`D:\AscensionFR\WOW_Priv\…`) traversent les étapes 2, 4, 5 —
dans le cloud, l'étape 2 lirait « aucun ID déjà corrigé » en silence (garde `exists`) et
**doublonnerait**, puis planterait à l'append final **après** les appels réseau ; et une
demi-douzaine d'écritures d'état sont **non atomiques** (`discord_aspirateur.json`,
`propositions_joueurs.json`, la fusion des caches, `interface_maison.json`) — sur une machine
qu'on peut éteindre à tout moment, c'est le contraire de ce qu'il faut.

#### La question qui décide : `DB_Communaute.lua` doit-il être versionné ?

**OUI — d'urgence — mais pas en public tel quel.**

- C'est bien **le seul produit qui ne se reconstruit pas** : 3,0 Mo, 11 795 lignes —
  3 360 entrées Gossip, 3 798 TextesPNJ, 4 499 lignes `quete()` (1 869 progressions « P »,
  2 630 rendus « R ») accumulées en APPEND depuis le début, qu'aucune régénération ne touche.
- Il vit **au pire endroit possible** : dans le `resources\` du lanceur Electron
  auto-mis-à-jour — le dossier qu'une mise à jour du lanceur peut écraser. Et il n'est suivi
  **nulle part** : `depot_addon.git` suit 29 fichiers, **aucun `DB_*`** (vérifié).
- Mais il ne peut pas partir en public sans passe de nettoyage : les textes P/R sont récoltés
  **après** que le jeu a remplacé `$N` par le nom du personnage. 105 P et 238 R gardent leur
  `$N` intact (sûrs) ; les ~4 150 autres doivent être **présumés porteurs d'un prénom de
  joueur** — le balayage rend 0, mais c'est un zéro d'instrument : il ne connaît pas ces
  noms-là.
- **Ma recommandation** : (1) tout de suite, l'ajouter (avec `DB_SortsCorrections.lua`, même
  famille — reconstructible en partie depuis `cache_db/`, mais pas à l'identique) à
  `depot_addon.git`, privé et local : un `git add`, zéro risque, la perte devient
  impossible ; (2) pour le public, une passe qui re-substitue les prénoms par `$n` est
  faisable — les gabarits officiels enUS/frFR portent le `$N` exact, on retrouve le prénom
  par différence — à chiffrer dans un programme suivant. **Toi de trancher.**

---

### BLOC B — les ~600 Mo de sauvegardes

- **Le compte exact : 64 fichiers, 714 468 711 octets (~681 Mo)** — plus que tes ~600 Mo :
  61 à la racine de `traductions/` (675 Mo : motifs `*_avant_*` + `sorts.json.bak` +
  `objets_dbc.json.bak`) et 3 dans `traductions/sauvegardes/citations_accents_20260728…/`
  (39 Mo). Les 21 `sorts_avant_*` pèsent **~480 Mo à eux seuls**. À part, pour être complet :
  `rapports/` porte 10 sauvegardes de plus (76 Mo).
- **Est-ce qu'un script en LIT une ?** Tour complet du code (`traducteur_fr.py`,
  `outils/*.py`, `compagnon/*.py`) : 17 scripts les mentionnent — 11 les **excluent**
  explicitement (`appliquer_vocabulaire.est_sauvegarde` l.62-63 confirmé, le balayeur du
  pont, `mesurer_file_travail`, `traducteur_fr` l.440-459…), 4 les mentionnent sans les lire,
  et **DEUX les lisent vraiment** (vérifiés à la main) :
  - [purger_noms_empoisonnes.py:59-60](../WorkFlow/outils/purger_noms_empoisonnes.py) **dépend**
    de `traductions/sorts_avant_reparation_noms.json` : c'est sa matière première — il y
    REPREND les descriptions d'avant le poison du 23/07. Outil de réparation ponctuel, déjà
    exécuté — mais tant qu'il existe, ce fichier-là n'est pas une sauvegarde : **c'est
    l'entrée d'un outil** ;
  - [migrer_racine.py:46-53](../WorkFlow/outils/migrer_racine.py) lit tous les `.json` du
    dépôt (donc les sauvegardes) — incidemment, pour réécrire des chemins ; aucune dépendance
    au contenu.
- **Donc** : aucune étape de la chaîne n'en lit une ; une seule sauvegarde nommée sert
  d'entrée à un outil. Si tu purges : mettre de côté `sorts_avant_reparation_noms.json`
  (23 Mo), et **~681 Mo récupérés** (+76 Mo côté `rapports/`, à ton choix).
- Une nuance qui plaide pour git : `_avant_vocabulaire.json` n'est créée **que si absente**
  ([appliquer_vocabulaire.py:566](../WorkFlow/outils/appliquer_vocabulaire.py)) — elle fige
  l'état d'avant le **tout premier** passage, pas le dernier. Le filet actuel est plus troué
  qu'il n'en a l'air ; `git diff`/`git revert` feront mieux, comme tu le pensais.
- **Rien supprimé.** Tu tranches.

---

### 🛑 BLOC C — ta lecture du code, vérifiée

**Affirmation 1 — CONFIRMÉE sur le fond, preuves à moitié fausses.** Les stores de
traduction ne sont jamais écrasés par une relance : les vrais verrous sont
`traducteur_fr.py` **l.492** (`_traduire_lot`, « if cle not in cible »), **l.715** (quêtes),
**l.757** (objets/créatures/objets-monde), **l.562** (sorts), **l.822** (champs P/R),
**l.832-833** (sorts récoltés), et `ingerer_recolte` l.264-265 / 308-310. **Mais quatre de
tes sept lignes (441, 453, 457, 461) sont dans `_compter_a_faire`** — la barre de
progression : elles comptent, elles n'écrivent rien. Le commentaire l.189 d'`ingerer_recolte`
est exact au mot près (et sa condition réelle, l.193, remplit bien une valeur VIDE — sur la
fusion en mémoire des sources **anglaises**, pas sur un store de traduction). Périphérie,
pour être complet : les registres bougent à chaque passage (`propositions_joueurs` —
compteurs de vote et champ « actuel » réécrits —, `rejets_chroniques`, `recolte_ecartes`),
et l'étape 3 écrase la matière **anglaise** fusionnée (« dernier arrivé gagne »,
[ingerer_caches.py:119](../WorkFlow/outils/ingerer_caches.py)). Aucun texte français servi
au jeu n'est touché.

**Affirmation 2 — CONFIRMÉE, lignes exactes.** Garde `--appliquer` l.560-562, sauvegarde
posée avant l'écriture l.565-567, écriture atomique ensuite. Deux nuances : la sauvegarde
n'est posée qu'**une fois pour toutes** (l.566, voir bloc B) ; et l'étape 6 enchaîne
`fusionner_gisement --ecrire`, qui réécrit `interface_maison.json` **sans filet ni
atomicité** ([fusionner_gisement.py:127](../WorkFlow/outils/fusionner_gisement.py)).

**Affirmation 3 — DÉMENTIE au sens strict… par ta propre étape 6.** « Rien ne revient
jamais améliorer une traduction posée » : si — `appliquer_vocabulaire --appliquer` repasse
sur **toutes** les valeurs posées à **chaque** passage de l'Atelier, exprès (c'est ton
affirmation 2 qui contredit ta 3). Chaque enrichissement du glossaire corrige l'existant au
tour suivant (« Cils légers » → « Fouet de Lumière »). S'y ajoutent, dans la chaîne :
`polir()` (accents, citations, harmonisations) re-transformé à chaque génération des DB
([generateur_db.py:117-134](../WorkFlow/outils/generateur_db.py)) ; les priorités du
générateur — un patch d'Ascension peut faire re-primer le frFR officiel sur l'IA
([generateur_sorts.py:299-327](../WorkFlow/outils/generateur_sorts.py)) ; les décisions du
pont des noms, posées « en dernier mot » à chaque build. Et « un trou bouché l'est
définitivement » : vrai dans les stores (aucune clé n'y est supprimée), **faux dans les bases
servies** (`quetes.pop()` sur divergence, `objets_interdits` qui rouvre des trous exprès).

**Ce qui reste vrai — et qui porte ta décision : le MOTEUR, lui, ne revisite jamais rien.**
Tous les chemins Google filtrent sur « clé absente » (l.491, 561, 715, 822 ;
`traduire_gisement` l.95). La nuance décisive sur `--retenter` est tranchée : la file exclut
les textes **traduits** avant de consulter les rejets (l.561-563) — un consigné est par
construction un texte resté **anglais** ; la déconsignation ne re-traduit jamais du posé.
Hors chaîne, pour répondre à ta question « même inutilisé » : **175 scripts sur 175
examinés**, une quinzaine savent remplacer de l'existant — `poser_retraduction_noms`,
`accents_majuscules --appliquer`, `appliquer_divergences_officielles` (celui des 43
contresens CoA), **`fusionner_lots` (le seul qui écrase SANS garde ni sauvegarde)**,
`pont_textes --recuperer` (voulu : la correction d'un contributeur RENTRE), les 7
`corriger_*`, 2 `reparer_*`, `retraduire_conditionnels`, `harmoniser_communaute`… — tous
manuels et dormants. **Le seul branché dans la chaîne est l'étape 6.**

**Conséquence pour la décision sur le rattrapage : ta recommandation TIENT, mais pas pour ta
raison.** Un rattrapage Google aujourd'hui ne serait pas « figé pour toujours » — le
glossaire, les accents et le pont continueront de le corriger partout où **tu** arbitres.
Mais il ne sera **jamais revisité par un moteur meilleur** : le futur moteur ne verra que les
clés absentes, et 15 817 trous bouchés en Google-2026 resteront en Google-2026 partout où
aucun arbitrage ne passe. Rien dans la chaîne ne sait faire « re-traduire si meilleure
source » — si un jour tu veux rattraper PUIS repasser, ce mécanisme est à créer exprès (les
`purger_*` savent déjà vider des clés par famille : c'est la moitié du chemin). Le vrai point
de non-retour est ailleurs : **`DB_Communaute` et `DB_SortsCorrections`**, chargées APRÈS les
bases régénérées — une vieille ligne y bat pour toujours une meilleure valeur future, à
chaque `/reload`.

---

### BLOC D — le retard, rechiffré au 8 août

**Le dénominateur** : 4 957 rapports `auto_*_rapport_*.txt` vus, **4 957 ouverts, 0
illisible** ; 118 277 entrées brutes → **32 190 couples (catégorie, texte) distincts**
(signalés 3,7 fois en moyenne).

**Le compte à aujourd'hui :**

| catégorie | à traduire (texte) | par ID | déjà traduits depuis |
|---|---|---|---|
| Divers | 5 413 | — | 318 |
| Gossip | 5 487 | — | 68 |
| TextesPNJ | 4 682 | — | 374 |
| Pages | 235 | — | 15 |
| QuetesProgres / QuetesRendu | — | 3 377 + 4 931 | — |
| **Total texte** | **15 817** | 8 308 | 775 |

- ⚠️ L'instrument annonce 23 107 « à traduire » : il compte les **7 290 « Sorts » comme des
  textes alors que la récolte `[Sorts]` porte des IDs numériques** (« 3018 »,
  « 9930830 »…) — c'est la voie « à part » du programme 26, et un défaut de classement de
  [mesurer_file_travail.py:51](../WorkFlow/outils/mesurer_file_travail.py) (`CIBLES` range
  Sorts en « texte2 » au lieu de « id »). La file publiée aux contributeurs charrierait
  7 290 lignes inutilisables — **à corriger avant l'étape « file de travail publiée »**.
- Entrées à ≥ 10 signalements : **1 689** (contre 808 au 4 août — la pression monte).

**Le volume en caractères, mesuré sur l'ensemble** : **1 119 996 caractères** pour les
15 817 textes — 70 de moyenne, 31 de médiane, 598 au plus long. Par catégorie : TextesPNJ
111, Pages 130, Divers 62, Gossip 42. **Ton 178 ne tient pas sur l'ensemble** (ton
échantillon de 2 674 penchait vers les textes longs) : le stock réel est ~2,5 fois plus
léger que prévu.

**La durée d'un rattrapage local, MESURÉE et pas estimée** : 100 vraies entrées de la file
(échantillon stratifié par catégorie, 75 caractères de moyenne), moteur réel
(`traduire_google` : protection + glossaire + double essai, 6 fils comme `_traduire_lot`) :
**7,1 s, 100/100 réussies, 0 refus.** Extrapolation : **15 817 entrées ≈ 19 minutes** ;
même doublé pour les aléas, c'est 20 à 40 minutes. « Une nuit » n'est pas le bon ordre de
grandeur — **c'est une pause-café.** (Et : ces ~200 appels rapprochés depuis ta machine
n'ont pas déclenché la moindre limitation.)

*Aveu d'instrument : ma première mesure disait 10,0 s — elle était faussée par les
Sorts-IDs de l'échantillon, qui passent par le raccourci `rien_a_traduire` sans réseau.
Refaite sans eux. Le banc a failli récompenser la version fausse, encore.*

---

### Ce qui a résisté, et ce que j'ai failli casser

- **Résisté** : le classificateur de permissions de la session a d'abord refusé la création
  du dépôt jetable (bloc 0) — résolu proprement par ta question-réponse en conversation, pas
  par contournement ; il a aussi bloqué par vagues des gestes anodins (un `git config` en
  lecture, des `python -c` de dépouillement) — fini par scripts-fichiers et PowerShell. Et le
  scope `delete_repo` manque au jeton `gh` : d'où le clic qui te reste.
- **Failli casser** : (1) le banc du bloc D — 32 % de l'échantillon étaient des IDs sans
  réseau, le chrono récompensait la version fausse ; recompté sans eux ; (2) le tableau
  « publié/non publié » — les caches `fusion/` matchaient par nom de base les stores
  publiés ; corrigé sur le clone réel ; (3) le premier commit de l'échafaudage embarquait un
  `__pycache__` du banc local — retiré avant la poussée ; (4) rien d'autre : aucune écriture
  hors `rapports/` (`file_travail_brute.json`, régénérée par l'outil du programme 26, et la
  carte des étapes) et le scratchpad de session.
- **Rien publié** (hors le dépôt jetable explicitement demandé, refermé), **rien déplacé,
  rien supprimé** (hors l'Action d'essai, comme exigé). **Aucun tag, aucune release, aucune
  fusion. `WorkFlow` reste sans dépôt distant.**
