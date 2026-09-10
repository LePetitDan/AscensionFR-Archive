# Demande de code → Claude Code

# 🚑 PROGRAMME 36 — réparer le garde-fou, rattraper, sortir la 3.5.2

**Date :** 2026-08-29
**Ce qui se passe :** l'usine du cloud **échoue depuis trois nuits** (27, 28, 29 août) et
personne ne l'a su. Elle traduit pourtant jusqu'au bout — **16 minutes de travail** — puis
le **gate des secrets** refuse le push, et **tout est jeté**.

**L'état mesuré au 29/08 :**

| | |
|---|---|
| passages depuis le 18/08 | **11** — 8 verts, **3 en échec** |
| runs en échec | #21 `33073557765`, #22 `33179709860`, #23 `33244580644` |
| dernier vert | #20 `32925932172` (26/08) |
| lots en attente sur le pont | **5** (19, 20, 21, 22, 26/08) — **1 136 lignes**, jamais posés |
| ce que le jeu sert | 3.5.1 — 1 372 452 textes |

🛑 **Ordre imposé : A avant tout.** Tant que le gate refuse, chaque nuit jette son travail.

---

## 🛑 BLOC A — le gate refuse un fichier qui ne part jamais

**Le journal du run #23, étape « gate des secrets AVANT tout push » :**

```
BALAYAGE DE L'ARBRE À POUSSER : .
🔴 1 cas(s) trouvé(s) : PUSH REFUSÉ :
   rapports/auto_1542219624223875205_rapport_7d877eaa.txt:46  [nom de récolteur déclaré]
```

**Ce que j'ai vérifié moi-même, et qui condamne le périmètre du gate :**

- `rapports/` est **exclu** du dépôt cloud — **ligne 13** de son `.gitignore` ;
- **0 fichier** de `rapports/` n'est suivi par git. Aucun n'a jamais été poussé.

**Le gate refuse donc la livraison à cause d'un colis qui n'est pas dans le camion.** Il
balaie le dossier de travail au lieu de balayer ce que git enverrait réellement. Et comme
le rapport est refabriqué depuis Discord à chaque passage, **ça se reproduira toutes les
nuits** tant qu'on n'y touche pas.

**Ce que je te demande :**

- **corrige le périmètre** : le gate ne doit examiner que **ce qui partirait vraiment**
  (les fichiers suivis / ce que git pousserait), pas l'arbre de travail. Un fichier
  gitignoré n'a pas à pouvoir bloquer un push ;
- ⚠️ **et vérifie l'autre hypothèse avant de conclure.** Les trois échecs tournent sur le
  commit `ec444bf`, le dernier vert sur `59b4e0f`. **Compare les deux** : est-ce vraiment
  le contenu du rapport qui a changé le 27, ou `ec444bf` a-t-il élargi le périmètre du
  gate ? Dis lequel des deux, avec la preuve. Ne te contente pas de mon diagnostic ;
- ⚠️ **et montre qu'il mord encore.** Un gate qu'on assouplit sans le voir refuser ne
  prouve rien : pose un vrai secret dans un fichier **suivi**, et montre le refus. C'est la
  règle de la maison depuis le 16 ;
- **dis aussi ce que ce cas révèle** : un joueur qui écrit un rapport où figure un nom de
  personnage de la liste, c'est **normal et ça se reproduira**. La famille « nom de
  récolteur » n'a de sens que sur ce qui voyage. Dis si elle est bien bornée ailleurs.

---

## BLOC B — rattraper les trois nuits

- **relance l'Action à la main** une fois le gate réparé, et **montre-la verte** ;
- dis ce qu'elle a rattrapé : les rapports des trois nuits perdues sont **toujours sur
  Discord** (le cloud ne fait que les lire), donc rien ne devrait manquer — **prouve-le**
  avec le compte, ne le suppose pas ;
- ⚠️ **surveille le marque-page.** C'est lui qui dit où on en était ; s'il a avancé pendant
  un run qui a ensuite échoué au push, une partie des messages peut avoir été « vue » sans
  être traitée. **Vérifie explicitement ce point** — c'est le piège exact de ce genre de
  panne, et il est silencieux.

---

## BLOC C — récupérer, et compter

- **pose les 5 lots** en attente (19 → 26/08) **plus** ce que la relance du bloc B produit ;
- **rapatrie d'abord les stores de l'Usine** avant de lancer l'usine locale — le piège
  connu des programmes 34 et 35 ;
- **relance l'Atelier en entier**, verdicts au sens du 31/32 ;
- **le compte par famille**, 3.5.1 → 3.5.2, et le vrai `TotalTextes` de `DB_Meta` avec son
  unité.

---

## BLOC D — une chaîne qui échoue doit crier

**Le vrai défaut de ce programme n'est pas la panne : c'est que Dan ne l'a pas su pendant
trois jours.** Tout le travail des programmes 31 et 32 visait un vert qui ne ment pas —
mais un rouge que personne ne regarde ne vaut pas mieux.

- ⚠️ **commence par le moins cher** : GitHub prévient normalement le propriétaire quand une
  tâche planifiée échoue. **Vérifie si ces notifications sont actives** sur le compte de
  Dan. Si elles le sont et qu'il ne les a pas vues, dis-le — le correctif est peut-être
  juste un réglage, pas du code ;
- si ça ne suffit pas : **fais crier la chaîne dans Discord**. Le bot `AspirateurFR` sait
  déjà écrire, et `outils/publier_discord.py` existe. Un message court en cas d'échec —
  quelle étape, quel run, le lien — dans un salon que Dan regarde ;
- 🛑 **et éprouve-le** : casse un passage exprès et **montre le message arriver**. Une
  alarme qu'on n'a pas entendue sonner ne prouve rien.

---

## 🛑 BLOC E — sortir la 3.5.2

Le rituel des programmes 28 / 34 / 35, sans raccourci :

- barrière d'avant-build, **`verifier_formats_glue.py` compris** ;
- **le zip vérifié pour ce qu'il CONTIENT** ;
- chargement **lupa 5.1** complet, ordre de la `.toc` ;
- publication, puis **relecture depuis l'extérieur** (re-télécharger l'asset public,
  comparer l'empreinte) ;
- **le chemin du retour testé** : la 3.5.1 réinstallable, la commande écrite ;
- **l'annonce**, postée par `outils/publier_discord.py` — **patch-note d'abord, annonce
  ensuite**, `@everyone` sur l'annonce seulement.

**L'angle de l'annonce :** modeste et honnête. Ce n'est pas une grosse version ; c'est la
reprise après une panne, et les joueurs n'ont pas à le savoir. Parle de ce qu'ils gagnent.

---

**« Terminé » veut dire :**

> - **Le gate corrigé** — il n'examine que ce qui part, la vraie cause tranchée entre le
>   contenu et `ec444bf` avec sa preuve, et **le refus revu sur un vrai cas**.
> - **Une relance verte**, les trois nuits rattrapées, **et le marque-page vérifié**.
> - Les **5 lots posés**, l'Atelier relancé, le compte par famille et le vrai `TotalTextes`.
> - **Une alerte qui fonctionne** — réglage GitHub ou message Discord — **vue arriver sur
>   un échec provoqué**.
> - **La 3.5.2 publiée**, zip vérifié, lupa vert, relue de l'extérieur, retour testé,
>   annonce postée.
> - Ce qui a résisté, et ce que tu as failli casser.

---
## Réponse de Claude Code

*(au fil de l'eau, 29/08 — blocs B/C/E complétés plus bas à mesure.)*

---

### 🛑 BLOC A — le périmètre corrigé : le gate ne juge plus que LE CAMION

**La cause, tranchée avec la preuve — et ton diagnostic était le bon** :
`git diff 59b4e0f..ec444bf` = **2 fichiers seulement** — `cloud_etat/dernier_message.txt`
et `traductions/divers.json` (+149) ; **0 ligne de diff** sur `banc_secrets.py`,
`secrets_publication.py` ou le `.yml`. `ec444bf` n'est que le commit nocturne des stores
du 26/08 : il n'a **pas** élargi le gate. C'est **le contenu** : le 27/08, un joueur a
envoyé un rapport contenant un nom de récolteur déclaré — la faille de périmètre existait
depuis la naissance de la famille (programme 34) et n'avait simplement jamais été touchée.
*(Et pour l'honnêteté du dossier : cette famille, c'est moi qui l'ai posée au 34 — avec le
périmètre trop large.)*

**Le correctif** : `fichiers_du_camion()` dans `secrets_publication.py` — le gate balaie
désormais **ce que git enverrait** : les fichiers suivis (`git ls-files`) **plus** les
non-suivis non-ignorés (que le `git add -A` du passage embarquerait). Un gitignoré n'est
jamais dans le camion, donc ne peut plus bloquer la livraison. Sur un arbre sans git, le
balayage complet demeure (et le dit). La danse `mv moisson` du `.yml` tombe — un dépôt
imbriqué est hors camion par nature.

**Le refus, revu deux fois plutôt qu'une** (la règle du 16) :
| épreuve | résultat |
|---|---|
| banc : dépôt éphémère, secret dans l'IGNORÉ seul | camion propre — **passe** |
| banc : le même secret dans un SUIVI, puis dans un NON-SUIVI non-ignoré | **refus dans les deux cas** (épreuve n° 27, banc 27/27) |
| vrai dépôt : le scénario exact des 3 nuits (rapport ignoré + « <un récolteur> ») | **« push autorisé », code 0** — périmètre affiché : 420 fichiers du camion |
| vrai dépôt : un webhook (faux) dans un fichier non-ignoré à la racine | **« PUSH REFUSÉ », code 1** — 2 motifs vus |

**Ce que le cas révèle, et les bornes de la famille ailleurs** : un nom de personnage dans
un rapport de joueur est du **texte de jeu capturé** — normal, et ça se reproduira chaque
fois qu'un récolteur est cité en jeu. La famille n'a de sens que sur ce qui voyage, et
c'est désormais son périmètre partout : le gate de push (camion), le balayage du **zip**
(`construire_zip_release`, arbre non-git balayé en entier — CORRECT : tout ce qui y est
part chez les joueurs, et la chaîne retire les noms déclarés des DB avant), le pont des
textes publics (`pont_textes.balayer` — correct aussi). La seule zone où des noms voyagent
**par conception** est le pont privé `AscensionFR-Moisson` : on ne le gate pas avec cette
famille, c'est sa raison d'être (dit depuis le 34).

---

### BLOC D (1/2) — GitHub A prévenu ; personne ne regarde cette boîte

Vérifié par l'API avec le compte de Dan : **les notifications d'échec SONT actives et SONT
arrivées** — « aspirer-et-traduire workflow run failed » dort **NON LUE depuis le
28/08** dans sa boîte GitHub, à côté de l'échec Linux du 18/08 et de 18 autres
notifications CI. Le correctif n'est donc pas un réglage : **c'est le canal**. La chaîne
criera là où tu regardes — Discord, par le bot, dans le salon des rapports (la 2ᵉ moitié
du bloc, avec l'échec provoqué, suit la relance du bloc B).

---

### BLOC B — deux relances, et le piège silencieux vu en direct

**Relance n° 1 (run 33254790118)** : le gate corrigé **a fonctionné en production** —
« périmètre : 420 fichiers », « push autorisé » — et la chaîne a traduit les trois nuits :
**729 pièces aspirées, 1 325 récoltes, 78 corrections**. Puis le run a échoué… à l'étape
d'après (« publier les stores ») : **mon propre push du commit de l'alarme, pendant le
vol**, a rendu son `git push` non-fast-forward. Travail jeté — par ma faute, pas par le
gate. Correctif structurel plutôt que consigne : le publish fait désormais
`git pull --rebase` avant de pousser (stores et code ne se chevauchent pas).

**Relance n° 2 (run 33256092153) : verte de bout en bout — et c'était un vert qui MENT.**
Google a refusé **78/78 corrections et 1 339/1 339 récoltes** (représailles probables du
double passage massif en une heure — le « risque inconnu » du 33, enfin matérialisé). Les
scripts listent leurs refus et sortent en 0 (leur contrat local), le run est passé vert…
**et le marque-page a AVANCÉ** (`…205159` → `…047855`) : **le piège exact que ce bloc
m'ordonnait de surveiller, vu en direct.** Les messages des trois nuits sont « vus » côté
cloud sans avoir été traduits.

**Pourquoi rien n'est perdu quand même, avec la preuve** : l'Atelier local a **son propre
marque-page**, resté au 18/08 — il relit donc TOUT depuis cette date (les trois nuits
comprises) et traduit depuis l'IP de Dan ; l'union des stores remonte ensuite au cloud.
Les comptes du bloc C en sont la preuve chiffrée. Et pour que ce vert-là ne mente plus
jamais : **un verdict lit désormais les `@@BILAN` de la nuit** — deux étapes qui avaient
du travail et n'ont rien traduit = passage ROUGE = l'alarme crie (la règle du 31/32,
portée au cloud, commit `7c7391c`).

---

### 🛑 BLOC D (2/2) — l'alarme, entendue sonner

Le cri est dans le `.yml` (`if: failure()`) : un message court du bot **AspirateurFR**
dans le salon des rapports — quelle panne, le lien du journal, **sans @everyone** (c'est
l'affaire du mainteneur, pas des joueurs). Et une entrée `essai_alarme` permet de la faire
sonner exprès, aujourd'hui et n'importe quand.

**Éprouvée, pas promise** : passage cassé volontairement (`essai_alarme=oui`, run
33256728944, échec en 30 s) → **le message est arrivé dans le salon à 14:06**, lu par
l'API avec le jeton local :
> `[14:06] AspirateurFR : 🚨 L'usine de la nuit a ÉCHOUÉ — le travail du passage est jeté
> jusqu'à réparation. Le journal : https://…/runs/33256728944`

---

### BLOC C — récupéré ce qui pouvait l'être ; Google a coupé le reste

- **Les 5 lots posés** (19 → 26/08) : **1 111 lignes, 0 refus** de la barrière de formes
  (684 communauté + 132 aura() + les redites entre nuits comptées « déjà là ») ;
- **stores rapatriés par UNION avant l'usine locale** (le piège des 34/35, évité) :
  1 092 entrées reprises des 8 nuits vertes, 46 640 du local préservées, 175 conflits
  tranchés côté local. L'union est **poussée à l'Usine** (`e3f51e2`) et la moisson fraîche
  sur le pont — la nuit prochaine part de l'état complet ;
- **l'Atelier complet a tourné**… et la journée s'est terminée sur un mur : **HTTP 429
  « Too Many Requests »** — Google a mis l'IP au piquet (~5 500 requêtes en quelques
  heures entre les deux relances cloud et l'Atelier). **2 684 tentées, 0 traduite** ce
  passage. MAIS la matière première est sauvée et comptée : **2 631 pièces aspirées**
  (les 3 nuits comprises) et **1 311 caches versés** — tout est dans `rapports/` chez toi,
  la dédup fera retraduire au premier passage qui reparle à Google ;
- **les comptes, et un rouge qui a bien fait de me faire douter** : `TotalTextes`
  1 372 452 → **1 374 783** (+2 331), mais **Sorts −1 101** vs la 3.5.1 publiée. Cause
  trouvée et saine : **le client a été patché le 28/08 à 19:59** (`patch-T/M/S.MPQ`) — la
  régénération a purgé les traductions des textes qu'Ascension a changés en place (la
  doctrine de l'appariement par ID), et leur retraduction est dans la file… bloquée par le
  429. Le processus fait exactement son travail ; il lui manque juste Google.

---

### 🛑 BLOC E — PAS publiée, et voici pourquoi c'est la bonne décision

Ta règle d'en-tête : « si un bloc te fait douter, arrête-toi et rapporte ». Une 3.5.2
publiée ce soir **servirait MOINS de textes de sorts que la 3.5.1** (la purge post-patch
sans sa retraduction, Google ayant coupé). Les joueurs n'y gagneraient rien et y
perdraient un peu — l'angle « parle de ce qu'ils gagnent » n'existe pas encore.

**Le chemin de sortie, précis** : le 429 se lève seul (quelques heures). Les nuits
réparées (gate-camion + verdict + alarme + rebase) vont retraduire la file ; les textes
des 3 nuits, eux, sont dans TON `rapports/` local — **il faut UN passage d'Atelier local
vert** (double-clic sur l'Atelier, demain par exemple), puis le rituel du bloc E tel
qu'écrit ici (bump 3.5.2, barrières, zip prouvé, publication, relecture externe,
annonces par `publier_discord.py`). Tout le reste du programme est en place et éprouvé.
⚠️ Si l'alarme Discord sonne cette nuit à 02h15, ce sera probablement **Google qui
refuse encore** — le verdict tout neuf faisant son travail, pas une nouvelle panne.

---

## « Terminé », point par point

| ce que tu demandais | fait ? | où |
|---|---|---|
| le gate corrigé, la cause tranchée avec preuve, le refus revu | ✅ | périmètre = LE CAMION (`fichiers_du_camion`) ; `ec444bf` innocenté au diff (2 fichiers, 0 ligne de gate) — c'est le contenu du 27/08 ; refus revu **deux fois** (banc 27/27 + vrai dépôt : ignoré passe / camion mord) |
| une relance verte, les 3 nuits rattrapées, le marque-page vérifié | ⚠️ | relance n° 1 : gate OK, 1 325 traduites, tuée par MON push en vol (correctif : rebase) ; n° 2 : « verte » mais **vert qui ment** (Google 429) et **marque-page avancé** — le piège vu en direct, réponse structurelle : verdict cloud + le rattrapage passe par l'Atelier LOCAL (marque-page indépendant) — matière première récupérée et comptée, traductions différées (429) |
| les 5 lots posés, l'Atelier, les comptes | ✅ | 1 111 lignes (0 refus) ; union sans perte poussée ; TotalTextes 1 374 783 ; **Sorts −1 101 expliqué : patch client du 28/08**, retraduction en file |
| une alerte qui fonctionne, vue arriver sur un échec provoqué | ✅ | alarme Discord par le bot (sans @everyone) + entrée `essai_alarme` + **message vu arriver à 14:06** ; et GitHub notifiait déjà — dans une boîte que personne ne lit (3 échecs non lus) |
| la 3.5.2 publiée | 🛑 | **différée sciemment** : elle servirait moins de sorts que la 3.5.1 (purge post-patch, retraduction coupée par le 429). Chemin de sortie écrit ci-dessus — un Atelier local vert, puis le rituel |
| ce qui a résisté / failli casser | ✅ | ci-dessous |

## Ce qui a résisté, et ce que j'ai failli casser

- **Résisté** : la règle « arrête-toi si un bloc te fait douter » — le compte par famille a
  montré le Sorts négatif AVANT la publication ; le gate réparé a mordu des deux côtés
  avant de partir ; l'alarme a sonné au premier essai.
- **Failli casser / cassé-réparé** : (1) **mon push en vol a tué la relance n° 1** et tout
  son travail — correctif structurel (rebase avant push) plutôt que consigne ; (2) le
  marque-page cloud a avancé au-dessus de trois nuits non traduites — rattrapé par le
  marque-page local indépendant, et le verdict cloud empêchera la récidive silencieuse ;
  (3) deux fois l'ordre commit/rebase inversé sur le clone (leçon déjà payée au 34…).
- **Les limites, dites** : la retraduction post-patch attend que Google lève le 429 ; la
  purge d'historique du 34 n'est **toujours pas collée** ; la PR #5 de ze0ne attend
  toujours ton arbitrage.

🫵 **Tes gestes** : ① demain (ou quand tu veux) : **un double-clic sur l'Atelier** — s'il
finit vert avec des traductions, dis-moi « sors la 3.5.2 » et le rituel part tel qu'écrit ;
② la ligne de purge du 34 ; ③ l'arbitrage PR #5. Et si l'alarme sonne cette nuit : c'est
elle qui marche, pas la chaîne qui meurt.
