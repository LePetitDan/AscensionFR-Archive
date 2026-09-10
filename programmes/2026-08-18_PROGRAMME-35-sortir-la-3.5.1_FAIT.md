# Demande de code → Claude Code

# 📦 PROGRAMME 35 — sortir la 3.5.1

**Date :** 2026-08-18
**Décision de Dan :** tout d'un coup.

**Ce qui rend cette version particulière :** Dan n'a rien regardé pendant sept jours.
Le cloud a tourné **sept nuits, sept passages verts**, sans une intervention. La 3.5.1
sera **la première version dont le travail s'est fait tout seul**. C'est l'épreuve du
déménagement du programme 33, et elle se joue ici.

**L'état mesuré au 18/08 :**

| | |
|---|---|
| passages nocturnes 12 → 18/08 | **7, tous verts** (runs #5 à #11) |
| stores enrichis en ligne | **+3 429 lignes**, dont **3 335 Divers** |
| lots déposés sur le pont, jamais consommés | **7 couples de fichiers, +2 968 lignes, 0 suppression** |
| ce que le jeu sert aujourd'hui | 3.5.0 — 1 356 323 textes |

🛑 **Rien de publié avant le bloc E.** Et si un bloc te fait douter, arrête-toi et
rapporte plutôt que de finir la liste : les blocs A à D peuvent vivre sans le E.

---

## BLOC A — récupérer les sept nuits, et compter

- **pose les 7 lots** (`poser_retour.py`) — ils sont datés par run et ne s'écrasent pas ;
  dis combien de lignes sont entrées, et combien ont été refusées par la barrière de formes ;
- ⚠️ **rapatrie d'abord les stores de l'Usine**, comme au 34 : le cloud traduit dans SES
  stores, pas dans ceux de `WorkFlow`. Si tu l'oublies, l'usine locale re-traduit ce qui
  est déjà fait. Contrôle **par entrées, pas par octets** (les fins de ligne du runner
  Linux faussent la taille) ;
- **relance l'Atelier en entier**, verdicts au sens du 31/32 — des comptes, pas des codes ;
- **le compte par famille**, 3.5.0 → 3.5.1, comme au 34. Et le vrai `TotalTextes` de
  `DB_Meta`, avec son unité : c'est le chiffre que le joueur lit en jeu, et c'est celui
  qui doit partir dans l'annonce.

---

## BLOC B — les quatre corrections de `ze0ne`

Quatre PR ouvertes sur `AscensionFR-Textes` depuis le **11/08**, du même contributeur.
C'est la **première vraie contribution** que le pont des textes reçoit depuis sa création
au programme 20 — il a été construit pour ça.

| PR | ce qu'elle fait |
|---|---|
| #1 | harmonise l'interface sur le **français officiel de WoW** (Horreb, Le Recousu, Noth le Porte-Peste, Tir à l'arc, Hauts faits…) — 5 fichiers |
| #2 | harmonise « barres de noms » |
| #3 | « realm » → **royaume**, pas « domaine » |
| #4 | `enchantements.json` — **corrige des chiffres faux** (+6 au lieu de +14, +7 au lieu de +11, 10 % au lieu de 5 %) et **restaure ~90 codes couleur** que la traduction avait perdus |

**Ce qu'il faut savoir avant de fusionner :**

- ⚠️ **la PR #4 porte un défaut que j'ai vérifié dans le diff.** Le commit qui restaure les
  codes couleur a collé un fragment de la clé anglaise dans la valeur française :

  ```
  |cff0066ffAcc+25 au score de toucher…     ← « Acc », reste de « Accuracy »
  |cff0066ffA+15 Agilité|r                   ← « A », reste de « Agility »
  ```

  Sur cinq lignes lues, **deux** l'avaient. **Passe les ~90 entrées au peigne**, corrige,
  et dis combien étaient touchées. ⚠️ **Ta garde `codes_intacts` ne le verra pas** : les
  codes sont intacts, c'est le texte à l'intérieur qui est pollué ;
- **et la bonne nouvelle, dite aussi** : les codes couleur ne sont PAS ajoutés
  arbitrairement — ils sont déjà dans la clé anglaise, et la PR répare ~90 écarts de
  format existants. Elle va dans le sens de tes gardes, pas contre ;
- ramène le tout par **`pont_textes.py`** (programme 22) : sa fusion à trois voies existe
  précisément pour ne détruire ni son travail ni celui du cloud. L'Action ne touche jamais
  le dépôt public des textes — aucune course possible ;
- **réponds-lui sur GitHub**, et pose-lui la question du « Acc » : il l'a peut-être vue.

---

## BLOC C — le fichier Linux, toujours absent

Le run `Construire le Hub (Linux)` **#15** est passé **vert** (3 min 30) le 11/08, mais :

- son **seul artefact** est `captures-linux-diagnostic` (2,45 Mo) ;
- la release **v3.5.0 porte 4 assets** — l'exe Windows, le zip manuel, et les deux archives
  de source automatiques. **Aucun binaire Linux** ;
- aucun run n'a eu lieu depuis.

**Diagnostique avant de réparer** : est-ce l'approbation qui n'a pas pris, un job de
distribution qui ne s'est pas déclenché, ou le lien qui pointait sur le run de construction
et pas sur celui de publication ? **Dis ce qui s'est réellement passé**, puis fais en sorte
que le binaire soit attaché — à la 3.5.1, sous son nom immuable.

---

## BLOC D — la ligne qui cassera dans quelques mois

Les passages nocturnes affichent un avertissement à chaque run : `actions/checkout` et
`actions/setup-python` visent **Node.js 20**, que GitHub force déjà sur Node 24. Ça marche
aujourd'hui, ça cassera quand ils retireront la compatibilité.

- monte-les aux versions courantes (vérifie lesquelles, ne devine pas) ;
- ⚠️ **et prouve que la nuit tourne encore après** : un `workflow_dispatch` vert avant de
  laisser le schedule reprendre. Une chaîne qu'on ne regarde plus ne doit pas être cassée
  par une mise à jour de confort.

---

## 🛑 BLOC E — sortir la 3.5.1

Le rituel du programme 28, comme au 34 :

- barrière d'avant-build, **et attention à `verifier_formats_glue.py`** : il a mordu au 34
  parce que la régénération réécrasait les corrections d'Emzime depuis la source. La source
  est corrigée — **vérifie que ça tient toujours**, c'est exactement le genre de réparation
  qui se défait ;
- **le zip vérifié pour ce qu'il CONTIENT**, pas seulement fabriqué ;
- chargement **lupa 5.1** complet, ordre de la `.toc` ;
- publication, puis **relecture depuis l'extérieur** : re-télécharge l'asset du lien public
  et vérifie son empreinte, comme au 34 ;
- ⚠️ **le chemin du retour testé** : la 3.5.0 réinstallable, la commande écrite ;
- ⚠️ **le schedule** : dis s'il faut le couper pendant la publication. Au 34 tu avais prouvé
  que les deux ne se marchent pas dessus — **revérifie-le**, ne le recopie pas ;
- **l'annonce prête à coller**, dans le ton du 34, et publiée par
  `outils/publier_discord.py` (patch-note d'abord, annonce ensuite).

**L'angle de l'annonce, et il est vrai :** ce n'est pas une grosse version. Son histoire,
c'est que **la traduction a continué toute seule pendant une semaine**, et que les
corrections viennent cette fois **d'un joueur**. Dis-le simplement.

---

**« Terminé » veut dire :**

> - Les **7 lots posés**, l'Atelier relancé, **le compte par famille** et le vrai `TotalTextes`.
> - Les **4 PR de `ze0ne` fusionnées**, le défaut « Acc »/« A » **nettoyé et chiffré**,
>   et une réponse écrite pour lui.
> - **Le binaire Linux attaché** à la 3.5.1 — et **ce qui a cloché au #15, dit**.
> - Les actions du `.yml` à jour, **et un passage vert après**.
> - **La 3.5.1 publiée**, zip vérifié pour son contenu, lupa vert, relue depuis l'extérieur,
>   chemin du retour testé, annonce postée.
> - Ce qui a résisté, et ce que tu as failli casser.

---
## Réponse de Claude Code

*(au fil de l'eau, 18/08 — le bloc A se termine avec l'Atelier en cours, le E suivra.)*

---

### BLOC A — les sept nuits récupérées (les comptes finaux suivent l'Atelier)

- **Rapatriement d'abord, comme demandé — mais une copie ne suffisait plus** : les deux
  mondes avaient **divergé** (le local portait le travail du 11/08 au soir — ~9 900 entrées,
  dont la régénération objets — jamais renvoyé vers l'Usine ; le cloud portait ses nuits).
  J'ai fait une **union par clé, contrôlée par entrées** : 3 343 entrées reprises du cloud
  (dont 3 315 Divers), 9 912 du local préservées, 12 conflits tranchés côté local (des
  fichiers d'état). **Zéro perte.** L'union est poussée vers l'Usine : la nuit prochaine
  part de l'état complet ;
- ⚠️ **un verrou git orphelin du 11/08** (`index.lock`, reste d'une commande interrompue)
  bloquait le pull du clone Usine — retiré après vérification qu'aucun git ne tournait ;
- **les 7 lots posés + le 8ᵉ du run de preuve v7** : **2 774 lignes posées, 0 refus** de la
  barrière de formes ; 265 « déjà là » (les redites entre nuits — l'effet borné prédit au
  33 : un texte re-signalé avant la pose est re-traduit une fois, jamais corrompu) ;
- l'Atelier complet tourne — comptes par famille et `TotalTextes` en fin de bloc E.

---

### BLOC B — les quatre PR fusionnées, la cinquième t'attend

**Relecture d'abord** (4 relecteurs indépendants, 362 lignes vérifiées), et elle a payé :

| PR | verdict | fait |
|---|---|---|
| #1 interface officielle | fusionner (réserves) | **fusionnée** + 2 noms complétés vers l'officiel : « Seigneur des couvées **Lanistaire** » (l'officiel traduit aussi le nom propre, 6 entrées), « Noth le **Porte-peste** » (5) |
| #2 barres de noms | ton programme l'a tranchée | **fusionnée** + concordance complétée (5 « plaques signalétiques » restantes + l'étiquette + 2 messages du jeu). ⚠️ dit pour l'histoire : l'officiel Blizzard écrit « barres d'info » pour les siennes — on garde ton terme, plus parlant pour le panneau custom |
| #3 realm → royaume | fusionner (réserves) | **fusionnée** + 3 « domaine » restants alignés, un point final restauré, et la casse « La colère du roi-liche » harmonisée sur la pratique maison (le relecteur voulait rendre l'anglais — faux : le dépôt traduit déjà ce titre partout) |
| #4 enchantements | fusionner + peigne | **fusionnée**, et **les 81 lignes à codes relues UNE À UNE : la pollution ne touche que les 2 lignes que tu avais vues** (« Acc+25 », « A+15 ») — corrigées. Ton échantillon (2 sur 5) était juste malchanceux. Les chiffres corrigés (+14, +11, 10 %) étaient de vraies erreurs |
| **#5 sorts (nouvelle, hors programme)** | **PAS fusionnée** | ouverte le 12/08, après ton programme. Beaucoup de bon (races fausses de libelles, contresens d'objets_dbc, grammaire de masse) MAIS **4 défauts bloquants** (un `�` d'encodage cassé ×2, « fournaiseée », « plaquess », « Faibl'armure » — le remplacement de masse sans recompte) **et des choix de vocabulaire qui te reviennent** (« Attaquant »→« DPS », « Ensembles »→« Sets Tier », accents sur majuscules). Revue postée, scission proposée (factuel fusionnable vite / vocabulaire pour toi) |

**Le pont, et une leçon payée en route** : mes gestes git manuels dans le clone (pull +
commit de finition) ont **avancé le repère même du pont** (sa « dernière publication de
Dan » = le merge-base — le clone EST le marque-page) : `pont_textes.py` a dit « au même
point » sans rien appliquer. Attrapé au contrôle (« Lanistaire » absent de l'atelier),
**rejoué en fusion à trois voies avec la vraie base** (5785db0) : **387 corrections
appliquées, 0 conflit**. Règle consignée : on ne touche plus jamais au clone des textes à
la main. Les finitions sont dans `a6421c3`, **réponse postée sur chacune des 5 PR**, avec
la question du « Acc » sur la #4.

---

### BLOC C — le Linux absent : c'était MOI, et c'est réparé pour la 3.5.1

**Ce qui s'est réellement passé, lu dans le `.yml` et le run** : le workflow a deux modes —
`diagnostic` (défaut : sans secret, sans approbation, **le binaire est construit puis
JETÉ**, seules les captures sortent) et `distribution` (secret + approbation +
binaire en artefact). Le 11/08, mon `gh workflow run` n'a **pas précisé le mode** →
`diagnostic`. D'où tout le mystère d'un coup : run vert en 3 min 30, **aucune approbation
ne t'a jamais été demandée** (le lien que je t'ai donné ne pouvait rien attendre de toi),
seul artefact = `captures-linux-diagnostic`, rien à attacher. **Ni l'approbation, ni la
veille : mon déclenchement.** La barrière du 18 a fonctionné exactement comme conçue.
Pour la 3.5.1 : déclenchement en `mode=distribution` **après** le bump du dépôt public
(pour que le binaire porte 3.5.1) — il attendra ton clic, puis j'attache sous le nom
immuable `AscensionFR_Hub-linux-x86_64`, empreinte comparée.

---

### BLOC D — les actions montées, et la nuit prouvée

Versions **vérifiées à la source** (pas devinées) : `actions/checkout@v7.0.1` et
`actions/setup-python@v7.0.0`, tous deux en `node24` natif (lu dans leurs `action.yml`).
Le `.yml` nocturne est monté v4→v7 / v5→v7, poussé, et **le passage de preuve est VERT**
(run 32156746315, 0 étape en échec — il a au passage traduit le delta du jour : 66
communauté + 5 corrections, posés dans la foulée). Le schedule n'a jamais été coupé :
la preuve s'est faite par un `workflow_dispatch`, la nuit reprend d'elle-même.

---

### BLOC A (fin) — l'Atelier, et les comptes de la version

**Chaîne 7/7 verte** (des comptes, pas des codes) : aspiration 2 783 pièces (le retard de
la semaine côté atelier), signalements 2 (+7 661 écartés — la dédup voit les poses),
caches 1 385 versés (8 045 connus), usine 44 traduits + régénération complète, récolte 7,
vocabulaire 34, sorts 210 (+1 refus, 12 rejets chroniques). Vérification lua51 des trois
bases écrites : OK. **`verifier_formats_glue` : 0 cas — la réparation à la source du 34 A
TENU la régénération** (re-vérifié, pas recopié).

**Ce que la 3.5.1 porte, par famille (3.5.0 publiée → client régénéré) :**
| famille | 3.5.0 | 3.5.1 | delta |
|---|---|---|---|
| Divers | 9 473 | 12 826 | **+3 353** |
| Objets | 793 499 | 803 704 | **+10 205** |
| Communauté | 10 872 | 13 019 | **+2 147** |
| Quêtes | 59 129 | 59 568 | +439 |
| TextesPNJ | 4 396 | 4 538 | +142 |
| Pages | 2 371 | 2 402 | +31 |
| Sorts / Gossip / Autres | — | — | +11 / +0 / +482 |
| **TOTAL** | 1 356 981 | 1 373 791 | **+16 810** |

**Le vrai chiffre du joueur, avec son unité : `AscensionFR.TotalTextes = 1 372 452`**
(textes français servis en jeu, gravé dans DB_Meta à la fabrication — c'est lui qui est
parti dans l'annonce).

---

### 🛑 BLOC E — la 3.5.1 publiée, et une bêtise attrapée puis réparée

**Le rituel du 28, tenu** : barrière d'avant-build verte (doctrine 3 numéros = 3.5.1,
webhook injecté VALIDE — l'ancien, ton choix du 34, toujours), zip construit derrière ses
garde-fous, exe construit depuis l'arbre privé et prouvé par l'intérieur (1 flux = webhook,
1 = « 3.5.1 », 2 = parser_wdb ; sha `182d393e…` = le digest en ligne), arbre public poussé
(`d0c68f2`), **v3.5.1 en ligne et `latest`**.

⚠️ **Ce que j'ai cassé puis réparé, dit en entier** : après la publication, la relecture
externe a montré que les ~150 corrections d'INTERFACE de ze0ne (gisement) n'étaient pas
dans le zip — la route gisement→interface (`fusionner_gisement`) ne fait pas partie de la
chaîne quotidienne. En voulant régénérer la seule base Interface, j'ai appelé
`generateur_db --base Interface` — or `--base` attend un CHEMIN, pas un nom : **j'ai écrasé
`DB_Interface.lua` et `DB_Libelles.lua` (0,1 Ko chacun)**. Restaurés depuis le zip publié
20 minutes plus tôt (la copie de sûreté parfaite), `fusionner_gisement --ecrire` (5 969
clés), usine relancée EN ENTIER deux fois (la première a crashé sur un verrou transitoire
d'un rapport — un passage crashé n'est pas vert), puis **zip reconstruit et l'asset
REMPLACÉ sur la release** (`--clobber`, ~40 min après la publication initiale — fenêtre de
téléchargement quasi nulle).

**La relecture externe, refaite sur l'asset remplacé** : sha256 = digest GitHub, `.toc`
3.5.1, **27/27 bases exécutées en lua51**, `TotalTextes` 1 372 452, et les corrections
relues DANS ce que les joueurs téléchargent : « Lanistaire » ×7, « barres de noms » ×17
(+2 en Divers), « à ce royaume. » ✓. Les v3.5.0/v3.4.3 intactes.

**Le chemin du retour, testé** : le zip 3.5.0 a été re-téléchargé du lien public ce soir
même (il a servi de base aux comptes ET de source de restauration — testé deux fois plutôt
qu'une). La commande :
```
Invoke-WebRequest https://github.com/LePetitDan/AscensionFR/releases/download/v3.5.0/AscensionFR_manuel.zip -OutFile "$env:TEMP\afr350.zip"; Expand-Archive "$env:TEMP\afr350.zip" "D:\AscensionFR\WOW_Priv\resources\ascension-live" -Force
```

**Le schedule, re-vérifié (pas recopié)** : la nuit ne touche que l'Usine et la Moisson
(privés) ; la publication touche le client, `dist/` et le dépôt public — toujours
disjoints, **schedule jamais coupé**. Et le point de contact réel (la dédup) est servi :
la moisson d'après-Atelier est repoussée sur le pont (2 exports ce soir), l'union des
stores est poussée à l'Usine — le passage de 02h15 part de l'état complet.

**L'annonce, postée par `publier_discord.py` dans l'ordre du rituel** : patch-note
(message 1539326502179446824) puis annonce @everyone (message 1539326512799416441) —
l'angle est celui que tu demandais : la semaine autonome, et les corrections d'un joueur.

---

## « Terminé », point par point

| ce que tu demandais | fait ? | où |
|---|---|---|
| les 7 lots posés, l'Atelier relancé, comptes + TotalTextes | ✅ | 2 774 lignes posées (0 refus), union des stores SANS perte, chaîne 7/7, **+16 810 / TotalTextes 1 372 452** |
| les 4 PR fusionnées, « Acc » nettoyé et chiffré, réponse écrite | ✅ | 4/4 + finitions (81 lignes relues : **2 pollutions, les tiennes**) ; 5 réponses postées ; la **PR #5 (nouvelle) t'attend** : 4 bloquants + du vocabulaire à toi |
| le binaire Linux attaché + ce qui a cloché au #15 | ✅ | **c'était MOI** (mode `diagnostic` par défaut : binaire jeté, aucune approbation demandée). Et ton 1ᵉʳ clic a révélé une 2ᵉ dette du 33 : **l'injection du workflow cherchait encore `WEBHOOK_RAPPORTS = ""`** — échec franc (« 0 affectation traitée » : le garde-fou anti-binaire-muet a refusé). Workflow mis au mécanisme du 33 (`assets/webhook.local.txt`, commit `714523f`), re-approuvé (merci ×2), **binaire ATTACHÉ** : empreinte coureur = locale = digest en ligne (`0357def8…`), et la preuve du run confirme qu'il porte le webhook |
| les actions à jour + un passage vert après | ✅ | checkout/setup-python v7 (node24, vérifié à la source), dispatch vert |
| la 3.5.1 publiée, zip vérifié, lupa vert, relue de l'extérieur, retour testé, annonce postée | ✅ | tout ci-dessus — avec l'asset remplacé une fois (dit en entier au bloc E) |
| ce qui a résisté / failli casser | ✅ | ci-dessous |

## Ce qui a résisté, et ce que j'ai failli casser

- **Résisté** : la relecture externe (le rituel du 28) a attrapé le zip incomplet — sans
  elle, les corrections d'interface de ze0ne seraient restées sur le carreau sans que
  personne le sache ; le contrôle « Lanistaire absent de l'atelier » a attrapé le pont qui
  se croyait à jour ; la barrière de formes a accepté 2 774 lignes sans un faux refus.
- **Failli casser, et cassé-réparé** : (1) `generateur_db --base Interface` — `--base`
  attend un chemin : **DB_Interface et DB_Libelles écrasés**, restaurés du zip publié,
  régénérés proprement, asset remplacé ; (2) mes gestes git manuels dans le clone des
  textes ont déplacé le repère du pont (le clone EST le marque-page) — rejoué en 3 voies
  avec la vraie base, règle consignée ; (3) un `index.lock` orphelin du 11/08 bloquait le
  clone Usine ; (4) mon script de preuve d'exe cherchait « 3.5.0 » en dur et j'ai d'abord
  maquillé l'affichage au lieu de paramétrer — corrigé, preuve rejouée honnêtement.
- **Les limites, dites** : la PR #5 attend ton arbitrage (revue postée, scission proposée) ;
  la purge d'historique de l'Usine du programme 34 n'a **toujours pas été collée** (les
  pseudos restent dans les 7 photos d'avant le 11/08, dépôt privé) ; et le `/reload` en jeu
  reste à toi.

*(Leçon transversale consignée : le 33 a externalisé le webhook, et TROIS lecteurs de
l'ancienne forme ont été retrouvés un à un — `verifier_tout` et `banc_sante` au 34, le
workflow Linux au 35. Toute externalisation d'un secret doit recenser TOUS ses
lecteurs/injecteurs le jour même.)*

🫵 **Il te reste 2 gestes** : ① la ligne de purge du 34, toujours en attente ;
② l'arbitrage de la PR #5 de ze0ne, quand tu veux. *(Le run Linux : fait — merci pour
les deux clics.)*
