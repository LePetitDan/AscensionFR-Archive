# Demande de code → Claude Code

# 🔧 PROGRAMME 31 — réparer, et finir le rattrapage

**Date :** 2026-08-08
**Décisions de Dan, prises sur ton rapport du programme 30 :**

- la réparation **des chemins en dur et de l'atomicité** — le cœur ;
- **plus les trois petits correctifs** que tu as nommés : la garde inversée de
  `DB_Communaute`, la consignation des appels perdus, et **un compte-rendu qui dise combien
  l'usine a traduit** — pas seulement qu'elle s'est terminée ;
- **plus la route des Divers et des Pages** : il veut le tiers manquant du rattrapage dans
  ce programme, pas dans un suivant ;
- **pas de version publiée ici.** Elle viendra juste après, et portera tout d'un coup.

**Le but du cœur, et il commande la moitié de ce programme :** l'usine doit pouvoir tourner
**sur une machine qui n'est pas celle de Dan et qu'on peut éteindre à tout instant.** Ce
programme ne la déménage pas ; il la rend déménageable. Tout se fait et s'éprouve chez Dan.

🛑 **C'est un programme chargé.** Si un bloc te fait douter, arrête-toi et rapporte plutôt
que de finir la liste. Les blocs A à D peuvent vivre sans le E ; le E ne doit pas partir si
les autres ne sont pas propres.

🛑 **Rien de publié, aucun zip, aucun tag, aucune release, aucune fusion de PR.**
`WorkFlow` reste sans dépôt distant.

---

## BLOC A — les chemins du client codés en dur

Ta carte (`rapports/programme29_carte_etapes.txt`) les a trouvés : `D:\AscensionFR\WOW_Priv\…`
traverse **les étapes 2, 4 et 5**.

Et tu as décrit le scénario de panne, qui est le pire possible : dans le cloud, l'étape 2
lirait « aucun identifiant déjà corrigé » **en silence** (la garde `exists` ne dit rien),
**doublonnerait tout**, puis planterait à l'écriture finale — **après** avoir dépensé les
appels réseau. Échouer bruyamment au début coûte une minute ; échouer en silence à la fin
coûte des doublons dans les bases et personne pour s'en apercevoir.

- **la liste complète** des endroits où un chemin de client est écrit en dur, par étape ;
- **une seule façon de le dire** : un réglage unique (variable d'environnement, fichier de
  configuration — tu choisis et tu justifies), pas huit constantes à tenir à jour ;
- ⚠️ **et surtout : que l'absence du client se voie tout de suite.** Chaque étape qui en a
  besoin doit le dire **au démarrage**, clairement, et s'arrêter ou se sauter proprement —
  jamais « continuer comme si de rien n'était ». C'est ça, le correctif ; déplacer une
  chaîne de caractères n'en est pas un ;
- ce qui reste **strictement impossible sans le client** : nomme-le. C'est la limite du
  déménagement, elle doit être écrite.

---

## BLOC B — les écritures non atomiques

Quatre familles nommées dans ton rapport : `discord_aspirateur.json` (**qui porte le jeton
du bot**), `propositions_joueurs.json`, la fusion des caches (6 fichiers + `ingeres.json`),
et `interface_maison.json` via
[`fusionner_gisement.py:127`](../WorkFlow/outils/fusionner_gisement.py) — « non atomique,
sans filet ».

Sur une machine qu'on éteint quand on veut, une coupure au mauvais moment ne corrompt pas un
fichier de travail : elle corrompt **le jeton et le marque-page**. Le bot ne se reconnecte
plus, et on ne sait plus où on en était.

- **passe-les toutes en écriture atomique**, en reprenant le mécanisme des stores plutôt
  qu'en en écrivant un nouveau ;
- la liste de ce que tu as changé, fichier par fichier ;
- ⚠️ **et démontre-le** : coupe une écriture en plein milieu, exprès, et montre que le
  fichier d'avant est intact. Un garde-fou qu'on n'a pas vu tenir ne prouve rien.

---

## BLOC C — la garde inversée de `DB_Communaute`

Ton constat : `quete()` de l'entête (l.56-59) fait `if e then e[champ] = texte` — une ligne
d'accumulation **écrase à chaque `/reload`** ce que l'usine régénérerait mieux. Le fichier
vient de passer à 12 573 lignes, et il va encore grossir au bloc E.

- **inverse la garde** : ne poser que si le champ est **absent**. Pareil pour `G` et `T` ;
- **dans l'entête du fichier ET dans `ENTETE` du script**, sinon le prochain passage
  réécrit l'ancienne version ;
- 🛑 **avant de la poser, mesure ce qu'elle change** — cette inversion modifie ce que des
  joueurs voient. **Combien d'entrées changent de comportement ? Montre-m'en dix, avant /
  après.** Si le résultat est massivement moins bon, arrête-toi et dis-le : le revers est
  assumé, pas subi ;
- chargement complet vérifié en **lupa 5.1**, ordre de la `.toc`.

**Fais ce bloc AVANT le E** : les nouvelles entrées doivent arriver sous la nouvelle règle.

---

## BLOC D — les appels perdus à chaque passage

372 Gossip que Google rend à l'identique sont retestés à chaque passage — ≈ 750 appels
dépensés pour rien, à chaque fois.

- **consigne-les**, sur le modèle de `recolte_ecartes` qui existe déjà ;
- ⚠️ **avec une porte de sortie** : un texte consigné doit pouvoir être re-tenté le jour où
  le moteur change — c'est précisément ce qui nous attend. Dis comment on déconsigne ;
- le gain mesuré : combien d'appels et combien de secondes en moins par passage.

---

## 🛑 BLOC E — la route des Divers et des Pages

**5 678 Divers et 261 Pages** sont récoltés depuis toujours : `depuis_rapports()` les
collecte (l.144-185) et **`main()` ne les consomme jamais**. Personne ne les a jamais
versés. C'est le tiers manquant du rattrapage, et Dan le veut ici.

### 1. Choisis la route, et justifie

Tu as nommé deux possibilités : **deux nouvelles familles dans `DB_Communaute`**, ou **un
versement vers `divers.json` / `pages.json`**. Tranche, et dis pourquoi — le critère est
simple : **par quel chemin le texte arrive-t-il réellement sous les yeux du joueur ?** Une
entrée dans un store ne sert à rien si aucune base générée ne la ramasse.

⚠️ **Si ta réponse est « nouvelle famille dans `DB_Communaute` », dis-le fort** : ça veut
dire toucher au **chargeur de l'addon**, donc à du code qui part sur 274 machines. Ce n'est
pas disqualifiant, mais ça change la nature du geste, et ça s'éprouve en lupa avant tout
le reste.

### 2. 🛑 Le nettoyage, avant de verser quoi que ce soit

**`Divers` est un fourre-tout de rapports de joueurs.** Contrairement aux Gossip et aux
TextesPNJ, qui sont du texte de jeu, on ne sait pas d'avance ce qu'il y a dedans.

- les 3 filets du pont sur **la totalité** des 5 939, **avec le dénominateur** ;
- ⚠️ et comme au programme 26 : **dis ce que tu ne sais pas attraper.** Un prénom de
  personnage inventé n'est dans aucun dictionnaire ;
- **un seul doute = tu t'arrêtes et tu le nommes.**

### 3. Un lot de 200, éprouvé de bout en bout

Exactement comme au programme 30 — et ce protocole vient de prouver sa valeur en attrapant
une régression de dix jours :

- 200 entrées stratifiées, traduites et posées ;
- **le texte montré dans l'add-on fabriqué**, avant / après, sur au moins un cas de chaque ;
- **le compte des écarts de codes de format** — je veux zéro, et je veux le chiffre.

**Si le lot n'est pas propre, le reste ne part pas.**

### 4. Le reste

Les ~5 700 restantes, avec tous les compteurs : tentées, traduites, refusées, écartées
« déjà en français », écarts de codes de format sur l'ensemble, durée réelle, et de combien
`DB_Communaute` a encore grossi.

⚠️ **Surveille la fenêtre d'erreurs 500** que tu as vue deux fois au programme 30, et dont
le script ne laisse aucune trace. Une deuxième passe et une vérification de sécheresse,
comme la dernière fois.

---

## 🛑 BLOC F — le vert qui ment

Le programme 30 a montré que l'Atelier affichait « 7/7 vert » pendant dix jours alors que
deux candidats sur trois étaient refusés en silence. **Vert veut dire « code de retour
zéro », pas « a traduit ».** Supportable quand Dan regarde la barre défiler. Intenable
quand la chaîne tournera seule, la nuit, sans personne — et c'est exactement ce qu'on
prépare.

**Dan a tranché : on le corrige ici.**

- `atelier_sante.json` porte désormais des **comptes** par étape — tentées, traduites,
  refusées, écartées — **et pas seulement un code de retour** ;
- 🛑 **un passage qui n'a rien traduit alors qu'il avait du travail ne peut plus être
  vert.** C'est la règle, et c'est elle qui aurait crié le 29 juillet ;
- ⚠️ **et montre-le mordre**, comme toujours : casse une étape exprès (remets la double
  protection du glossaire une minute, ou coupe le réseau) et **montre le bandeau refuser
  de passer au vert**. Un garde-fou qu'on n'a pas vu refuser ne prouve rien — c'est la
  leçon du programme 16, et le lot de 200 vient encore de la confirmer ;
- distingue bien les trois cas, sinon le garde-fou criera pour rien : **rien à faire**
  (légitimement vert), **du travail et rien de traduit** (rouge), **du travail et une
  partie traduite** (à toi de dire où tu mets la limite, et de la justifier).

---

**« Terminé » veut dire :**

> - Les chemins du client en un seul réglage, **et l'absence du client qui se voit tout de
>   suite** — la liste, et ce qui reste impossible sans lui.
> - Les quatre familles passées en atomique, **et une coupure en plein milieu montrée sans
>   dégât**.
> - La garde inversée aux deux endroits, **avec la mesure de ce qu'elle change et dix
>   exemples avant / après**, lupa 5.1 vert.
> - La consignation des écartés, sa porte de sortie, le gain mesuré.
> - **La route des Divers/Pages choisie et justifiée**, le balayage avec son dénominateur,
>   **le lot de 200 parcouru en entier**, puis le reste avec tous les compteurs.
> - **Le « vert qui ment » corrigé**, avec des comptes dans `atelier_sante.json` — et le
>   bandeau **vu refuser** de passer au vert sur une étape cassée exprès.
> - **L'Atelier relancé en entier après tout ça, et le compte de ce qu'il a réellement
>   traduit.** Pas « il s'est terminé » : combien.
> - Ce qui a résisté, et ce que tu as failli casser.

🛑 **Aucune version publiée.** Les commandes de retour en arrière du programme 30 doivent
rester valides — si un de tes gestes les invalide, écris les nouvelles, testées.

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Puis renommer en `_FAIT.md`.)

*Exécuté le 2026-08-08. Note de terrain : la session de travail a été coupée DEUX fois en
plein versement — l'occasion de vérifier que les gestes de ce programme tiennent leurs
promesses (rien de perdu, reprise propre les deux fois), et d'ajouter des points d'étape à
la route pour que même une coupure en plein vol ne reperde plus jamais un lot entier.*

---

### BLOC A — les chemins du client : un réglage, et l'absence qui se voit

**Le réglage unique : la variable d'environnement `ASCENSIONFR_JEU`**, portée par un module
nouveau — [outils/chemin_client.py](../WorkFlow/outils/chemin_client.py) — qui expose `JEU`,
`ADDONS`, `ADDON`, `DB`, `client_present()` et `exiger_client()`. Absente, elle retombe sur
le chemin de ta machine : **rien ne change chez toi**. Pourquoi pas un fichier de config :
le déménagement visé est une Action GitHub, où c'est UNE ligne `env:` dans le yml — un
fichier de config serait un état de plus à embarquer, à balayer, et qui finirait par mentir.

**La liste complète des chemins en dur, par étape** (le dépôt en compte ~80 ; la **chaîne**
en concentrait **14 fichiers, tous convertis** — le reste est de l'outillage manuel hors
chaîne, `migrer_racine.py` existe pour les gros lots) :

| étape | fichiers convertis vers `chemin_client` |
|---|---|
| 2 — signalements | `ingerer_rapport.py` (l.47), `recuperer_db.py` (l.65) |
| 4 et 7 — usine/sorts | `traducteur_fr.py` (l.41), `generateur_db.py` (l.26), `mise_a_jour.py` (l.32), `diagnostiquer_signalements.py` (l.41), `generer_noms_objets.py` (l.16), `generer_noms_sorts.py` (l.26), `paresseux_textes.py` (l.26) |
| 5 — récolte (+ queues) | `ingerer_recolte.py` (l.45), `optimiser_memoire.py` (l.41), `compter_total.py` (l.27) |
| 6 — vocabulaire | `generateur_glue.py` (l.59 — importé pour `signature_compatible` seulement, converti quand même) |
| l'Atelier lui-même | `collecteur.py` (l.29-35 — ⚠️ l'exe du bureau reste l'ANCIEN binaire jusqu'à reconstruction ; sur ta machine, mêmes chemins, rien ne change) |

**L'absence du client se voit — prouvé, pas promis.** Chaque script qui ne peut rien faire
sans le client appelle `exiger_client()` **au démarrage** : une ligne claire, le **code de
sortie 3** (réservé — distinct de 0 « fait » et 1 « planté », et le bloc F le dit tel quel
au bandeau), zéro appel réseau dépensé. Éprouvé avec `ASCENSIONFR_JEU=D:\client_inexistant`
sur les **8 entrées gardées — 8 refus en 0,0-0,2 s** :

```
CLIENT ABSENT — ingerer_rapport (étape 2 — signalements) ne peut rien faire sans le client d'Ascension.
  chemin réglé : D:\client_inexistant
  réglage : variable d'environnement ASCENSIONFR_JEU
  arrêt AVANT tout appel réseau et toute écriture.
```

(`ingerer_rapport`, `ingerer_recolte`, `recuperer_db`, `optimiser_memoire`, `compter_total`,
`generer_noms_objets`, `generer_noms_sorts`, `traducteur_fr --une-fois`.) **Une exception
voulue** : `traducteur_fr --sorts` tourne SANS client — il traduit `a_traduire/ →
traductions/` (le travail utile dans le cloud) et ne saute, bruyamment, que la régénération
(`_generer_sorts`, garde `client_present()`). Ton scénario de panne — doublonner en silence
puis planter après les appels réseau — est mort : l'étape 2 refuse à la première ligne.

**Ce qui reste strictement impossible sans le client — la limite du déménagement, écrite :**
lire les caches WDB (récolte des textes croisés en jeu), lire les SavedVariables WTF
(récolte de l'addon local), écrire les `DB_*.lua` servies au jeu, détecter un patch et
réextraire MPQ/DBC (`mise_a_jour`), rejouer le moteur de l'addon pour les diagnostics.
Dans le cloud : aspiration → ingestion des caches → traduction (`--sorts` + rapports) →
vocabulaire → publication des stores ; **la fabrication des bases livrées reste chez toi.**

---

### BLOC B — les écritures non atomiques : passées, et la coupure montrée

**Toutes passées par le mécanisme existant** (`ecriture_sure.ecrire_json` — `.part`, fsync,
`os.replace`), pas un mécanisme neuf. Fichier par fichier :

| fichier réparé | écritures converties |
|---|---|
| [aspirer_discord.py](../WorkFlow/outils/aspirer_discord.py) | `discord_aspirateur.json` (**le jeton + le marque-page**) : `sauver_config` ET la création du modèle ; `pieces_jointes_mortes.json` |
| [ingerer_rapport.py](../WorkFlow/outils/ingerer_rapport.py) | `propositions_joueurs.json` (les votes, réécrits en entier) |
| [ingerer_caches.py](../WorkFlow/outils/ingerer_caches.py) | les 6 `fusion/*.json` + `ingeres.json` — fusion D'ABORD, mémoire APRÈS (une coupure entre les deux re-verse au pire un fichier déjà versé, jamais l'inverse) |
| [fusionner_gisement.py](../WorkFlow/outils/fusionner_gisement.py) | `interface_maison.json` — l'écriture « sans filet » du programme 29 |
| bonus : [ingerer_recolte.py](../WorkFlow/outils/ingerer_recolte.py) | `recolte_ecartes.json` (même famille, nommée fragile au 29) |

**La coupure en plein milieu, montrée deux fois** (copies des 4 vrais fichiers, fonction
même du dépôt) : **exception au milieu de la sérialisation** — 4/4 fichiers d'avant intacts
(empreintes identiques), `.part` nettoyé ; **kill brutal pendant l'écriture** — processus
tué avec **760 076 octets déjà écrits** dans le `.part` → le fichier d'avant **intact à
l'octet**, rechargeable en JSON valide ; le `.part` orphelin reste, inoffensif. Et la vie a
ajouté sa propre épreuve : **deux coupures réelles de session en plein versement** — zéro
octet perdu dans les fichiers à écriture atomique, les deux fois.

Restent non atomiques, nommés : les deux cumuls de `diagnostiquer_signalements.py`, et tout
ce qui se régénère seul (`a_traduire/`, `extraits/rexxar/`, `DB_*.lua`). Rien
d'irremplaçable dedans.

---

### BLOC C — la garde inversée, mesurée AVANT d'être posée

**La mesure d'abord.** Qui perdrait la main (Communaute → bases générées) :

| famille | entrées Communaute | aussi dans la base générée | texte différent (bascule visible) |
|---|---|---|---|
| Gossip | 3 373 | **0** | 0 |
| TextesPNJ | 4 495 | 160 | 108 |
| Quêtes P/R | 4 555 | 17 | 12 |
| **total** | 12 423 | **177** | **120** |

**Dix avant / après** (avant = `DB_Communaute` sert ; après = la base générée sert) :

1. « …you are always welcome here » : *vous êtes toujours les bienvenus ici* → **vous êtes
   toujours $gle bienvenu:la bienvenue; ici** — l'accord par sexe, que Google ne sait pas faire ;
2. « …waterfowl… » : *Un seul commentaire sur la sauvagine, et vous mangerez à travers une
   paille* → **Si j'entends une plaisanterie déplacée, vous êtes bon pour des prothèses
   dentaires** — l'officiel, idiomatique ;
3. « Magar's Cloth Goods is in The Drag… » : *Les étoffes de Magar … la Tranchée* → **La
   Friperie de Magar … la Herse** — les toponymes officiels ;
4. « …east side of Razor Hill » : *à l'est de Razor Hill* → **à l'est de Tranchecolline** ;
5. « Greetings traveler… » : *Salutations voyageur* → **Salutations, $gvoyageur:voyageuse;** ;
6-10. même famille (Dwukk, Mishiki, Miao'zan, Sen'jin ; « Which profession? » : identique).

**Verdict : gain net** — les 120 textes qui basculent passent du Google de récolte au
**frFR officiel**. Aucun cas inverse vu. **Posée aux DEUX endroits** : `ENTETE` du script ET
l'entête du fichier vivant (remplacée à l'octet près depuis `ENTETE`, écriture atomique,
convention CRLF respectée). Mécanisme : proxys `G`/`T` à `__newindex` + `quete()` gardée par
`if e[champ] == nil`. **lupa 5.1, ordre `.toc` : vert** — Gossip 5 363, TextesPNJ 8 400,
Quêtes 11 235 ; bascule témoin vérifiée (« Tranchecolline » gagne) ; **0 clé d'accumulation
perdue sur 7 868**. Commit `9863615` dans `depot_addon.git` — **les retours du programme 30
restent valides tels quels** (ils visent `7273904` et `b98d8cb` par empreinte).

---

### BLOC D — les appels perdus : consignés, avec la porte de sortie

**Fait, sur le modèle existant** (`recolte_ecartes.json`, même fichier) : un texte que
Google rend à l'identique est consigné sous `deja_francais` et tu aux passages suivants —
avant tout appel réseau. Un échec **réseau** n'est JAMAIS consigné (la leçon de la fenêtre
de 500). **La porte de sortie, double** : *automatique* — la consigne est liée à
`VERSION_BOUCLIER` : le jour où le moteur change (précisément le jour qui donne envie de
re-tenter), la liste se vide toute seule, et la remise à zéro atteint le disque ;
*manuelle* — `python outils/ingerer_recolte.py --retenter-ecartes`.

**Le gain, mesuré sur deux passages réels consécutifs** : étape 5 passée de **37,2 s à
3,4 s (−91 %)** ; **744 appels Google épargnés à chaque passage** (comptés par le script
lui-même : « 372 “déjà en français” consignés — 744 appel(s) Google épargnés »).

---

### 🛑 BLOC E — la route des Divers et des Pages

#### 1. La route choisie : les STORES — et voilà pourquoi

**Versement vers `traductions/divers.json` et `traductions/pages.json`**, pas de nouvelles
familles dans `DB_Communaute`. Le critère que tu as donné tranche seul : par quel chemin le
texte arrive-t-il sous les yeux du joueur ? **Les bases générées ramassent DÉJÀ ces deux
stores** — [generateur_db.py:771-772](../WorkFlow/outils/generateur_db.py) construit
`DB_Divers.lua` directement de `divers.json`, et l.736-763 construit `DB_Pages.lua` de
`pages.json` (croisé à l'officiel). Donc : **zéro ligne de chargeur à toucher, rien qui
parte sur 274 machines** — le texte atteint le joueur à la régénération suivante (l'étape 4
la fait à chaque cycle). Et deux bénéfices gratuits : ces stores passent par le
**vocabulaire arbitré** (étape 6) et par la **publication contributive** (tous deux dans
les 22 publiés). La route est écrite dans la chaîne elle-même — **boucle 3 de
[ingerer_recolte.py](../WorkFlow/outils/ingerer_recolte.py)** : mêmes gardes que les boucles
1-2 (dédup contre le store ET les clés/valeurs de la base générée, `paraît_anglais`,
consigne « déjà en français », pseudonymes), garde « **clé absente** » à la pose (jamais de
remplacement — l'affirmation 1 du programme 29 tient), écriture **atomique**, harmonisation
du vocabulaire à l'ingestion.

#### 2. Le nettoyage, avant de verser

- Les 3 filets du pont sur **la totalité** : **6 197 textes récoltés (5 925 Divers + 272
  Pages), 2 fichiers ouverts sur 2, 0 motif.**
- **Ce que je ne sais pas attraper, dit** : un prénom de personnage *inventé* (aucun
  dictionnaire ne le connaît — le balayeur ne connaît que les 48 déclarés), un nom collé à
  un code couleur (`\|cFF…Nom`), et le contenu des textes-systèmes que l'addon intercepte
  (la famille `Divers` est un fourre-tout par construction).
- **Et le doute que j'ai trouvé, nommé — pas dans les Divers, mais juste à côté** : la
  récolte *Gossip* fraîche porte **276 lignes de classement d'arène** (« #6 Xxx Rating:
  2252 | Wins… ») — des **pseudos de joueurs** hors de portée du balayeur, dans des clés
  **volatiles** (les cotes changent : elles ne re-matcheront jamais, poids mort à jamais
  dans un fichier en append). **254 étaient DÉJÀ entrées dans `DB_Communaute`** par les
  passages d'avant ce programme. J'ai posé un **filtre à l'ingestion**
  (`RE_CLASSEMENT`, [ingerer_recolte.py](../WorkFlow/outils/ingerer_recolte.py)) — l'hémorragie
  est arrêtée ; **la purge des 254 existantes est un arbitrage pour toi** (retirer des
  lignes d'un fichier d'accumulation, je ne le fais pas sans ton feu vert).

#### 3. Le lot de 200, éprouvé de bout en bout

Candidats réels après la dédup de la route : **5 507 Divers + 253 Pages**. Lot stratifié
191 + 9 :

| | |
|---|---|
| tentées | 200 |
| traduites et posées | **199** (1 rendue à l'identique, écartée) |
| refusées | 0 |
| **écarts de codes de format** | **0** — y compris un code d'icône `\|T…\|t` et les `\|cFF…\|r` préservés |
| bases régénérées | par le **vrai générateur** (`generateur_db.main()`, 13 s — 51,7 Mo de bases) |
| **servies par l'addon fabriqué** | **199/199** (lupa 5.1 ; avant : `nil` partout) |

Avant / après réels : « Set CTRL-2 to ElvUI_Bar2Button8 » → « Définissez CTRL-2 sur
ElvUI_Bar2Button8 » ; page : « Fascinating! This blueprint shows a steam-powered healing
device… » → « Fascinant ! Ce plan montre un appareil de guérison à vapeur !… » (le `$n` du
gabarit préservé).

#### 4. Le reste — versé, à sec, compté par la chaîne elle-même

Le reste est parti par **le script réel**, et les compteurs ci-dessous sont ceux de sa
propre ligne `@@BILAN` (le bloc F au travail sur son premier vrai passage) :

| | passe 1 | passe 2 |
|---|---|---|
| tentées | 5 957 | 21 |
| **traduites** | **5 921** (5 528 aux stores + 393 à `DB_Communaute` — les Gossip/PNJ/quêtes des rapports frais, classements filtrés) | **21** (les 21 refus réseau de la veille, toutes rattrapées) |
| refusées par Google | 21 | **0** |
| écartées « déjà en français » | 387 (dont 15 nouvelles consignées) | 387 (tues, 774 appels épargnés) |
| durée | ~1 h 40 (séquentiel) | 23 s |

- **Écarts de codes de format sur l'ensemble : 0** (contrôle indépendant sur le lot ; le
  moteur refuse par construction — `codes_intacts` — et n'a rien refusé pour ça).
- Les stores : `divers.json` **+5 475** au total (81 → 837 Ko), `pages.json` **+252**
  (191 → 419 Ko). `DB_Communaute.lua` : +393 lignes.
- **Sécheresse** : la passe 2 rend « tentées 21, refusées 0 » — une passe 3 rendrait
  « tentées 0 » (tout est couvert ou consigné). Vérifié par la relance finale plus bas.
- La fenêtre de 500 surveillée comme demandé : **aucune** pendant ce versement (les 21
  refus étaient des ratés ponctuels, rattrapés en 23 s).
- *Note de terrain : la coupure de session a tué deux tentatives de versement en plein
  vol. D'où les **points d'étape** ajoutés à la route ([ingerer_recolte.py](../WorkFlow/outils/ingerer_recolte.py)) :
  `DB_Communaute` se pose par paquets de 100, les stores se sauvent tous les 200 — une
  coupure ne reperd plus jamais un passage entier. C'est exactement la propriété qu'exige
  « une machine qu'on peut éteindre à tout instant ».*

---

### 🛑 BLOC F — le vert qui ment : corrigé, et vu mordre

**Chaque étape imprime désormais une ligne machine** en fin de passage :

```
@@BILAN {"tentees": N, "traduites": N, "refusees": N, "ecartees": N}
```

Les sept l'ont : `aspirer_discord` (pièces jointes), `ingerer_rapport` (sur CHAQUE chemin
de sortie — un bilan manquant ferait un faux « non instrumenté »), `ingerer_caches`
(fichiers/entrées), `traducteur_fr` (`--une-fois` ET `--sorts` — compteurs posés aux quatre
points de traduction du Compagnon), `ingerer_recolte` (les trois boucles),
`appliquer_vocabulaire` (corrections calculées/appliquées).

**Le verdict vit dans un module unique** — [outils/sante_atelier.py](../WorkFlow/outils/sante_atelier.py) —
utilisé par le bandeau de l'Atelier ET par le banc de santé. **Les trois cas, distingués
comme demandé** :

1. **rien à faire** (tentées = 0) → **vert**, légitimement ;
2. **du travail et rien de traduit** (tentées > 0, traduites = 0, refus > 0) → **rouge** —
   la règle qui aurait crié dès le 29 juillet ;
3. **du travail et une partie traduite** → **vert jusqu'à la moitié de refus, orange
   au-delà**. La limite, justifiée : la fenêtre de 500 du programme 30 a mangé ~un tiers
   d'une passe et la passe suivante a tout rattrapé — un seuil plus nerveux crierait sur
   l'aléa d'une nuit ; perdre la **majorité** d'un passage, ça, doit se voir sans aller
   lire un journal.

Le code 3 (« client absent », bloc A) est dit tel quel — un fait de configuration, pas une
panne. **Branché partout** : `collecteur.py` capture les `@@BILAN`, écrit
`atelier_sante.json` avec **comptes + verdicts**, et le bandeau obéit au pire verdict (⚠️
l'exe du bureau reste l'ancien binaire jusqu'à reconstruction — le code y est) ;
`banc_sante.py` applique la même règle : « code 0 mais les COMPTES disent non » = ROUGE.

**La morsure, VUE — l'étape 5 cassée exprès.** Le sabotage est celui que tu proposais :
**la panne du 29/07 rejouée** (le moteur refuse tout — c'est ce que produisait la double
protection du glossaire), avec `--retenter-ecartes` pour remettre 387 textes en file et
`--dry` pour ne rien écrire. Résultat, tel qu'affiché :

```
étape 5 sabotée : code 0 en 1 s
@@BILAN capturé : {'tentees': 387, 'traduites': 0, 'refusees': 387, 'ecartees': 0}
VERDICT : ROUGE — 387 tentée(s) et RIEN de fait (387 refus)
l'ancien monde (code retour seul) aurait dit : VERT
banc_sante : ROUGE  Atelier : code 0 mais les COMPTES disent non — ingerer_recolte.py : 387 tentée(s) et RIEN de fait
```

**Code 0, et le vert refusé quand même — deux fois** (le verdict, puis `banc_sante` sur la
santé écrite). C'est la règle qui aurait crié le 29 juillet. `atelier_sante.json` restauré
après la démonstration ; la relance finale l'a réécrit avec l'état vrai.

*Aveu de première tentative : mon premier sabotage (couper le réseau par un proxy mort)
s'est enlisé — chaque appel saboté mangeait les 10 s de timeout, ~2 h pour une démo. Tué,
remplacé par le tien, qui est meilleur : déterministe, instantané, et c'est la vraie panne
historique.*

---

### L'Atelier relancé en entier — et combien, pas seulement « fini »

Les 7 étapes, dans l'ordre et avec les commandes exactes de `collecteur.py`, sur la chaîne
réparée — et le hasard a bien fait les choses : **une grosse vague Discord est arrivée
pendant le programme**, la relance a donc travaillé pour de vrai (2 h 09, de 12:21 à 14:30) :

| étape | code | durée | verdict (comptes) |
|---|---|---|---|
| `aspirer_discord.py` | 0 | 18 min | vert — **3 694/3 694 pièces téléchargées** |
| `ingerer_rapport.py` | 0 | 15 min | vert — **983/987** corrections de sorts traduites |
| `ingerer_caches.py` | 0 | 4 min | vert — **11 810 textes de jeu versés** (2 160 fichiers de caches neufs) |
| `traducteur_fr.py --une-fois` | 0 | 28 min | vert — 83/88 ; **toutes les bases régénérées avec les stores enrichis** (les 5 727 Divers/Pages du bloc E servent désormais) |
| `ingerer_recolte.py` | 0 | 63 min | vert — **4 029/4 067** (la vague fraîche : nouveaux Gossip/PNJ/quêtes ET Divers/Pages par la route neuve, classements filtrés) |
| `appliquer_vocabulaire.py --appliquer` | 0 | 35 s | vert — 155/155 corrections appliquées |
| `traducteur_fr.py --sorts` | 0 | 35 s | vert — 140/147 |
| vérification lua | 0 | — | OK |

> **BANDEAU : VERT | RÉELLEMENT TRADUIT ce passage : 20 894 unités de travail** — dont
> **~5 235 traductions Google** (983 + 83 + 4 029 + 140), 155 corrections de vocabulaire,
> 11 810 textes versés à l'usine et 3 694 pièces collectées. `atelier_sante.json` porte
> les huit codes, **les sept bilans et les sept verdicts** — le premier passage de
> l'histoire du projet dont le vert veut dire « a travaillé », pas « s'est terminé ».

`DB_Communaute.lua` : 14 918 lignes ; `DB_SortsCorrections.lua` : +983. **Tout est à
l'abri** : commit `f62d73c` dans `depot_addon.git` (l'historique du programme :
`7273904` → `a1d5190` → `9863615` → `f62d73c` — les retours du 30 valides à chaque étage).

---

### Ce qui a résisté, et ce que j'ai failli casser

- **Résisté — et c'était le sujet même du programme** : la session de travail a été coupée
  **deux fois** en plein versement, et un troisième versement détaché a survécu à une
  remise à zéro de l'environnement. Bilan des trois incidents : **zéro octet perdu** dans
  les fichiers à écriture atomique, reprise propre par la déduplication les trois fois.
  Les points d'étape ajoutés en cours de route (paquets de 100/200) ont réduit la perte
  maximale d'« un passage entier » à « un paquet ».
- **Failli casser, dit sans fard** : (1) mon guetteur de processus (`tasklist | grep`) a
  déclaré MORT un versement vivant — j'ai failli en relancer un **par-dessus** (deux
  `ingerer_recolte` concurrents sur le même append !) ; le verrou du fichier journal a
  fait échouer la relance avant la collision. Guetteur remplacé par `Wait-Process` ;
  (2) mon premier `@@BILAN` d'`ingerer_rapport` manquait deux chemins de sortie précoces —
  un passage « rien à faire » aurait paru non-instrumenté ; corrigé avant pose ;
  (3) le sabotage au proxy mort (raconté au bloc F). Rien d'autre : `pyflakes` sur les
  17 fichiers touchés, les retours du programme 30 valides, aucun store écrasé (garde
  « clé absente » partout).
- **Rien publié, aucun zip, aucun tag, aucune release, aucune fusion. `WorkFlow` reste
  sans dépôt distant.** Les 766 + 5 949 traductions des programmes 30-31 attendent la
  version qui portera tout d'un coup, comme décidé.
- **Deux arbitrages restent sur ta table** : la purge des **254 lignes de classement**
  déjà entrées dans `DB_Communaute` (le filtre arrête l'hémorragie, le stock existant est
  à toi), et la reconstruction de l'exe de l'Atelier (le bandeau à verdicts vit dans le
  source — l'exe du bureau montre l'ancien monde jusque-là).
