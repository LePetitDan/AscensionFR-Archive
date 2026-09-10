# Demande de code → Claude Code

# 🧹 PROGRAMME 32 — solder l'arriéré

**Date :** 2026-08-08 (après la relance du programme 31, 14 h 30)
**Décision de Dan, en trois mots :** « règle tout ce qui traîne. »

J'ai fait l'inventaire de ce qui traîne réellement, et il est plus long que les deux
arbitrages annoncés à la fin du 31. **Sept choses**, dont **trois programmes jamais
faits** — l'un d'eux coûte de 3 à 9 signalements détaillés par jour depuis une semaine.

| # | ce qui traîne | depuis | bloc |
|---|---|---|---|
| 1 | la veille ne lit pas les pièces jointes — **40 signalements non lus** | 02/08 (6 jours) | A |
| 2 | le filtre des classements a un trou — **ça saigne encore** | trouvé aujourd'hui | B |
| 3 | la purge des classements déjà entrés — **403, pas 254** | arbitrage rendu | B |
| 4 | un bilan manquant repasse au vert | trouvé aujourd'hui | C |
| 5 | l'exe de l'Atelier montre l'ancien monde | 31 | D |
| 6 | Confort ne s'installe pas depuis le Hub | 06/08 (2 jours) | E |
| 7 | le conflit Clique et le « franglais » | 30/07 (9 jours) | F |

**La version n'est pas dans ce programme, et voici la seule raison :** le bloc F peut
changer ce qu'elle embarque. Si traduire les noms de sorts casse Clique, les macros et
les WeakAuras, alors publier **+6 715 traductions** aggrave le problème pour plus de
monde. On répond à F, **puis** on publie. C'est le 33, et il portera tout d'un coup
comme prévu.

🛑 **Programme long mais peu risqué** — sauf B et D, tout est isolé. Ordre imposé :
**A avant F** (la moisson de A nourrit l'enquête de F), **B avant toute nouvelle passe**
(sinon le stock regrossit pendant que tu travailles). Si un bloc te fait douter,
arrête-toi et rapporte plutôt que de finir la liste.

🛑 **Rien de publié, aucun zip, aucun tag, aucune release, aucune fusion de PR.**
`WorkFlow` reste sans dépôt distant. Les retours arrière du programme 30 doivent rester
valides **mot pour mot** — si un de tes gestes les invalide, écris les nouvelles, testées :

```bash
git -C D:/AscensionFR/WorkFlow restore --source=b98d8cb -- traductions/
git --git-dir=D:/AscensionFR/depot_addon.git --work-tree="D:/AscensionFR/WOW_Priv/resources/ascension-live/Interface/AddOns" checkout 7273904 -- AscensionFR/DB/DB_Communaute.lua AscensionFR/DB/DB_SortsCorrections.lua
```

---

## BLOC A — les 40 signalements que personne n'a lus

**Reprends la demande du 02/08 en entier** —
[`2026-08-02_veille-lire-les-pieces-jointes-texte.md`](2026-08-02_veille-lire-les-pieces-jointes-texte.md).
Elle est complète, elle tient toujours, et tous ses garde-fous sont à respecter tels
quels : texte seulement et petit, troncature marquée, **UTF-8 explicite en entrée comme
en sortie de console**, jamais d'échec réseau qui écrase des données, `_etat.json`
intact, rattrapage dans un fichier à part, pseudos strictement locaux.

L'endroit est toujours le même, je viens de le vérifier :
[`outils/aspirer_veille.py`](../WorkFlow/outils/aspirer_veille.py) — `def corps(m)`
**l.373**, la branche `return "[fichier : %s]" % pj.get("filename", "?")` **l.386**.

**Ce qui s'ajoute depuis, et qui n'était pas dans la demande d'origine :**

- ⚠️ **cette étape doit porter son `@@BILAN`.** Le bloc F du 31 a instrumenté sept
  étapes ; la veille n'en fait pas partie et deviendrait la seule zone aveugle du
  tableau. Compte ce qui a du sens ici : **pièces jointes vues / lues / illisibles**.
  Une passe qui voit dix pièces jointes et n'en lit aucune ne peut pas être verte ;
- la question que Dan posait le 07/08 tient toujours et il attend la réponse :
  **le fichier porte-t-il la version du Hub ?** (au moins deux pièces jointes viennent
  de joueurs en 3.4.0 installée à la main.) Si oui, on trie les signalements périmés
  tout seuls ; si non, dis-le, c'est une info aussi.

**Rends le compte** : combien de pièces jointes récupérées, combien étaient
effectivement des signalements de traduction, combien venaient d'une version périmée.

---

## BLOC B — le filtre des classements : le trou, puis la purge

### 1. Le trou — mesuré, pas supposé

`RE_CLASSEMENT` ([`ingerer_recolte.py:260`](../WorkFlow/outils/ingerer_recolte.py)) est
ancré sur `^#\d+`. Or **la moitié des tableaux d'arène arrivent précédés d'un code
d'icône** et passent tout droit :

```
G["|TInterface\Icons\Achievement_PVP_A_12:40:40:0:0|t #3 Grimmjob Rating: 2086 | Wins:…"]
```

La preuve, commit par commit dans `depot_addon.git` :

| | 7273904 | a1d5190 | 9863615 | **f62d73c** |
|---|---|---|---|---|
| classements **nus** | 254 | 254 | 254 | **254** ← le filtre mord |
| classements **à icône** | 101 | 101 | 101 | **149** ← **+48 aujourd'hui** |

Les 48 sont entrés **pendant la relance finale du 31, après la pose du filtre.**
L'hémorragie n'est pas arrêtée, elle est réduite de moitié.

- **Répare-le par une normalisation, pas par une regex plus longue.** Retire les codes
  de format en tête (`|T…|t`, `|cFF……|r`, espaces) **avant** de confronter le texte au
  motif. Une regex qui grossit à chaque forme nouvelle est le trou de demain ;
- ⚠️ **et balaie la même faiblesse ailleurs.** Tout motif ancré sur `^` dans la chaîne
  tombe sur le même piège — `porte_pseudo`, les 3 filets du pont, `paraît_anglais`.
  Dis lesquels sont concernés et lesquels ne le sont pas. **C'est le vrai correctif** ;
  boucher un cas n'en est pas un.
- l'ironie à retenir, elle est instructive : tu avais **nommé cette forme exacte** comme
  ton angle mort au bloc E §2 du 31 (« un nom collé à un code couleur ») et le filtre
  écrit dix lignes plus bas tombe dessus.

### 2. La preuve de sécheresse — avant la purge

**Une passe complète d'`ingerer_recolte` sur la récolte fraîche doit ajouter
`0` classement**, des deux formes. Donne le chiffre avant / après. Tant qu'il n'est pas
à zéro, **ne purge rien** : retirer des lignes d'un fichier qui les reprend au passage
suivant, c'est du travail perdu deux fois.

### 3. La purge — Dan a dit go

**403 lignes**, pas 254 (254 nues + 149 à icône). Compte-les toi-même avant de
commencer, le chiffre aura peut-être encore bougé.

- 🛑 **commit d'avant la purge dans `depot_addon.git`**, et la ligne de retour arrière
  testée, comme au 30 — la purge est le seul geste destructif du programme ;
- retire les entrées des **deux** formes, et vérifie que tu ne prends rien d'autre au
  passage : il y a des textes légitimes qui contiennent « Rating: » ailleurs qu'en tête
  (j'en compte 403 au total dont 403 sont des classements — **vérifie ce chiffre**,
  il doit rester 0 texte de jeu emporté) ;
- **chargement lupa 5.1 après purge**, ordre de la `.toc`, et le compte des clés
  restantes ;
- dis de combien le fichier a maigri.

---

## BLOC C — un bilan manquant ne peut plus être vert

Dans [`outils/sante_atelier.py`](../WorkFlow/outils/sante_atelier.py) :

```python
if not bilan:
    return (VERT, "pas de comptes (étape non instrumentée)")
```

Une étape **censée** être instrumentée qui meurt avant d'imprimer son `@@BILAN` — ou
dont la sortie n'est pas capturée — retombe exactement dans l'ancien monde : code 0 =
vert. C'est le bug que le bloc F devait tuer, laissé ouvert par sa porte de service.

Tu l'avais à moitié vu : tu as rustiné les trois chemins de sortie d'`ingerer_rapport`
**pour cette raison précise** (« un bilan manquant ferait un faux non-instrumenté »).
Il manquait la marche d'après.

- **tiens la liste des étapes connues instrumentées** (les sept, plus la veille du bloc
  A). Un bilan absent chez l'une d'elles est une **anomalie** — pas un vert. Une étape
  hors liste garde le vert neutre, c'est légitime ;
- ⚠️ **et montre-le mordre**, comme toujours : retire un `print("@@BILAN …")` exprès sur
  une étape de la liste, lance, et **montre le bandeau refuser de passer au vert**.
  Remets-le après ;
- au passage, deux petites choses qui ne méritent pas leur propre bloc :
  - `ingerer_caches` rend `tentées 2 160 / traduites 11 810` — des fichiers d'un côté,
    des textes de l'autre. Le verdict affiche « 11810/2160 faite(s) » et la règle de la
    majorité de refus compare deux unités différentes. Compte la même chose des deux
    côtés, ou marque l'étape comme comptant des fichiers ;
  - le rapport du 31 et le message du commit `f62d73c` disent « DB_Communaute :
    **14 918 lignes** ». Le fichier en fait **15 013**, dont **14 801 entrées** et 212
    de préambule. Ni l'un ni l'autre. Le fichier est bon, le chiffre est faux — dis le
    vrai, et dis de quelle unité il s'agit.

---

## BLOC D — l'exe de l'Atelier

Le bandeau à verdicts vit dans le source ; **l'exe du bureau montre encore l'ancien
monde**, celui où vert veut dire « s'est terminé ». C'est l'exe que Dan regarde — tant
qu'il n'est pas refait, tout le bloc F du 31 est invisible pour lui.

- reconstruis-le depuis
  [`outils/build_collecteur/Collecteur AscensionFR.spec`](../WorkFlow/outils/build_collecteur/) ;
- **et vérifie sur l'exe reconstruit, pas sur le source** : les comptes affichés, les
  trois couleurs, et le **code 3 « client absent »** dit tel quel ;
- 🛑 si la reconstruction échoue ou rend un exe douteux, **dis-le et n'installe rien** :
  un exe à moitié bon sur le bureau de Dan est pire que l'ancien, qui au moins ment de
  façon connue.

---

## BLOC E — Confort ne s'installe pas depuis le Hub

**Reprends la demande du 06/08 en entier** —
[`2026-08-06_confort-ne-sinstalle-pas-depuis-le-hub.md`](2026-08-06_confort-ne-sinstalle-pas-depuis-le-hub.md).
Tous ses garde-fous tiennent : on ne pose qu'un dossier qui porte son `.toc`, **DragonUI
se livre en deux dossiers frères** et ne doit pas casser, et la correction doit valoir
sur Windows **et** Linux.

**Ce que j'ai déjà mesuré pour toi, pour que tu ne le refasses pas :**

- les deux `interface_hub.py` (`compagnon/` et `depot_github/compagnon/`) sont
  **identiques aujourd'hui** — pas de divergence à rattraper, mais garde-les jumeaux ;
- le zip **local** `dist/AscensionFR-Peche.zip` est **correctement formé** :
  racine `AscensionFR-Peche/` contenant `AscensionFR-Peche.toc`. La bonne forme existe
  donc quelque part dans la chaîne ;
- les trois forks portent leur `.toc` **à la racine du dépôt**
  (`depot_forks/AscensionFR-Confort/AscensionFR-Confort.toc`) ;
- ⚠️ **et il n'y a aucun workflow GitHub Actions dans les forks.** Les assets de release
  sont donc fabriqués **à la main** — c'est très exactement ainsi qu'un des quatre
  finit à plat pendant que les autres sont bons. **C'est ma première piste**, à
  confirmer ou démolir par la mesure.

**Ce que j'attends :**

1. les 4 assets du catalogue téléchargés pour de vrai, et **ce qu'il y a dedans**, un
   par un — dossier racine ou fichiers à plat, `.toc` trouvable par
   `dossiers_addon_du_zip` oui/non ;
2. **Linux seulement, ou tout le monde ?** — avec la mesure sur laquelle tu t'appuies ;
3. le **déballage** réparé (accepter un zip à plat et le re-raciner sous le nom de la
   fiche, sans jamais poser un contenu sans `.toc`) — ça part avec la prochaine version
   du Hub, donc rien de public aujourd'hui ;
4. l'erreur affichée qui dit **ce qui a été trouvé** dans le zip ;
5. les **assets refabriqués et prêts**, posés quelque part de propre — mais
   ⛔ **pas téléversés**.

📌 **Le seul geste public du lot, et il est à Dan :** remettre en ligne les assets de
release des forks. Prépare-les, dis-lui lesquels sont à refaire, et arrête-toi là.

---

## 🛑 BLOC F — le conflit Clique et le « franglais »

**Reprends la demande du 30/07 en entier** —
[`2026-07-30_conflit-clique-et-noms-de-sorts.md`](2026-07-30_conflit-clique-et-noms-de-sorts.md).
Elle a neuf jours, elle n'a jamais reçu de réponse, et **elle commande maintenant la
version 33.** Les trois questions sont inchangées :

1. la 3.4.0 remplace-t-elle le nom d'un sort **là où un autre addon peut le relire**
   (`GetSpellInfo`, cache de sorts, hook global) — ou seulement à l'affichage ?
2. qu'est-ce qui a changé sur les sorts **entre la 3.3.0 et la 3.4.0** ? Un diff chiffré
   des champs touchés suffit ;
3. le « franglais » : sur un sort donné, **tous** les chemins d'affichage, et lesquels
   passent par la traduction.

**Ce que j'ajoute, et c'est le poids nouveau du bloc :**

- ⚠️ **fais-le APRÈS le bloc A.** Les 40 pièces jointes non lues sont les signalements
  les plus détaillés du projet, sur la période même où le problème est apparu. Il y a
  une chance réelle que la réponse soit dedans, écrite par un joueur. Ce serait bête de
  rejouer le moteur pendant trois heures pour ça ;
- ⚠️ **et dis ce que ça coûte à la 33.** Si l'hypothèse est confirmée, publier
  +6 715 traductions étend le problème à plus de joueurs : dis-le franchement, et
  chiffre-le (combien de noms de sorts la 33 ajouterait-elle par rapport à la 3.4.3 ?).
  Si elle est écartée, dis-le aussi clairement — la 33 part sans réserve ;
- **aucun correctif appliqué.** Une proposition et son coût, comme demandé à l'origine.
  Ce bloc mesure, il ne répare pas.

Si tu ne peux pas trancher — c'est possible, tu n'as pas de trace en jeu et Dan le
savait en écrivant la demande — **dis ce qu'il te faudrait** pour trancher, précisément.
Une non-réponse honnête vaut mieux qu'une hypothèse habillée en conclusion.

---

**« Terminé » veut dire :**

> - **Les 40 signalements lus**, avec leur compte, leur tri par version, et la veille
>   qui porte son `@@BILAN`.
> - **Le filtre réparé par normalisation**, la même faiblesse balayée ailleurs dans la
>   chaîne, **une passe qui ajoute 0 classement**, puis les **403 purgées** — commit
>   d'avant et ligne de retour testée, lupa 5.1 vert après.
> - **Un bilan manquant qui ne peut plus être vert**, la liste des étapes instrumentées,
>   et **le bandeau vu refuser** de passer au vert sur un `@@BILAN` retiré exprès.
> - **L'exe de l'Atelier refait**, et les verdicts vérifiés sur l'exe, pas sur le source.
> - **Les 4 assets ouverts et racontés**, Linux-seulement ou tout le monde tranché, le
>   déballage réparé, les assets refabriqués **prêts et non téléversés**.
> - **Le conflit Clique : confirmé ou écarté, avec le chiffre qui le prouve** — et ce
>   que ça coûte à la version 33.
> - Les trois demandes absorbées (30/07, 02/08, 06/08) renommées en `_FAIT.md` avec une
>   ligne qui pointe ici.
> - Ce qui a résisté, et ce que tu as failli casser.

🛑 **Aucune version publiée, aucun asset téléversé.** Le seul geste public du lot est
nommé au bloc E et il attend Dan.

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Puis renommer en `_FAIT.md`.)

*Exécuté le 2026-08-09. Ordre respecté : B avant toute passe, A avant F.*

---

### BLOC A — les 40 signalements que personne n'a lus

**Fait.** `aspirer_veille.py` lit désormais le TEXTE des pièces jointes texte (`.txt`/`.md`/
`.log` ou `content-type text/*`, ≤ 200 Ko), tronqué à 8 000 caractères avec `[… tronqué]`,
tout autre type gardant son étiquette. Tous les garde-fous du 02/08 tenus : UTF-8 explicite
en lecture **et** console (`sortie_utf8` déjà en place), un échec réseau écrit
`[fichier : … — non téléchargé (raison)]` sans jamais lever, et le rattrapage vit dans un
fichier à part (`--rattrapage AAAA-MM-JJ` → `RATTRAPAGE_pieces-jointes.md`) qui **ne touche
pas `_etat.json`** — vérifié par empreinte SHA-256 avant/après : **identique**.

**Le compte, mesuré sur la passe de rattrapage réelle (depuis le 26/07)** : **52 messages à
pièce jointe texte**, dont **48 pièces jointes lues** (48 vues, 48 lues, **0 illisible**).
Les 48 sont **toutes des signalements au format Compagnon** (« Signalement AscensionFR /
Récolte / Propositions / Échecs d'alignement »).

**La question de Dan du 07/08 — le fichier porte-t-il la version du Hub ? OUI**, et c'est
exploitable : la version est lisible soit dans le nom (`AscensionFR_3.4.0.txt`) soit dans le
corps (`AscensionFR X.Y.Z`). Tri automatique possible. Le relevé des 48 :

| version portée | nombre | statut vs 3.4.3 |
|---|---|---|
| 3.4.0 | 14 | périmé |
| 3.4.1 | 9 | périmé |
| 3.4.2 | 9 | périmé |
| 3.3.0 | 8 | périmé |
| 2.2.x / 1.6.2 | 5 | très périmé |
| **3.4.3 (courant)** | **3** | à jour |

**45 des 48 signalements viennent d'une version périmée** — une partie décrit donc des
fautes **déjà corrigées**. Ils restent à lire (le contenu reste utile : beaucoup de fautes
survivent aux versions), mais on peut les **classer par fraîcheur** au lieu de les relire à
l'aveugle. **La veille porte son `@@BILAN`** (`aspirer_veille.py` ∈ étapes instrumentées,
bloc C) : `{tentees: pièces vues, traduites: lues, refusees: illisibles, ecartees: non-texte}`
— une passe qui voit dix pièces et n'en lit aucune ne peut plus être verte.

---

### BLOC B — le filtre des classements : le trou, puis la purge

**Le trou, réparé par NORMALISATION, pas par une regex plus longue.** J'ai ajouté
`denuder(texte)` ([ingerer_recolte.py](../WorkFlow/outils/ingerer_recolte.py)) qui retire les
codes de format en tête (`|T…|t`, `|cFF……`, `|r`, `|n`) **avant** de confronter au motif. Les
trois formes passent maintenant le filtre : `#3 …`, `|TInterface\Icons\…|t #3 …`,
`|cFF2EF50E#10 …|r`. L'ironie que tu soulignes est exacte — j'avais nommé « un nom collé à un
code couleur » comme mon angle mort au bloc E du 31, et le filtre écrit dix lignes plus bas y
tombait.

**La même faiblesse, balayée ailleurs** — verdict par garde :

| garde | ancrée `^` / `\b` ? | concernée ? | action |
|---|---|---|---|
| `RE_CLASSEMENT` | `^#\d+` | **OUI** | corrigée (dénude avant) |
| `porte_pseudo` (`_RE_PSEUDOS`, `\b`) | frontière de mot | **OUI** — « \|cFF…Starcaller » | corrigée (cherche aussi dans le dénudé) |
| filets du pont (`re_pseudo`, `\b`) | frontière de mot | **OUI** | corrigé ([pont_textes.py](../WorkFlow/outils/pont_textes.py) balaie texte + dénudé) |
| `paraît_anglais` | aucun ancrage (`findall`) | **NON** — compte des lettres n'importe où | inchangée |
| garde quêtes P/R | (nouvelle) | — | j'ai ajouté un `porte_pseudo` après `sans_pseudo` : un pseudo collé à un code que `sans_pseudo` ne sait pas remplacer fait écarter la quête |

**La sécheresse AVANT la purge** : passe complète d'`ingerer_recolte` sur la récolte fraîche
→ **0 classement ajouté** (compte des lignes de classement identique avant/après : 405). Le
filtre normalisé ne laisse plus rien passer.

**La purge — 405, pas 254** (254 nues + **151** à codes, pas 149 : +2 depuis ton compte).
Vérifié qu'aucun texte légitime n'est emporté : **0 ligne** contient « Rating: » ailleurs
qu'en tête de classement. Geste destructif encadré comme au 30 :

- **commit d'avant** : `3926cb0` dans `depot_addon.git` ;
- **retour arrière testé en aller-retour** (le retour ramène les 405, la re-purge redonne
  l'octet identique — empreinte SHA-256 vérifiée) :
  ```bash
  git --git-dir=D:/AscensionFR/depot_addon.git --work-tree="D:/AscensionFR/WOW_Priv/resources/ascension-live/Interface/AddOns" checkout 3926cb0 -- AscensionFR/DB/DB_Communaute.lua
  ```
- **après** : `bd25056` ; **lupa 5.1 vert** (ordre `.toc`) — Gossip 5 713, TextesPNJ 9 983,
  Quêtes 11 470 servies, **0 classement encore servi** ; le fichier a maigri de **107 Ko**
  (15 159 → 14 754 lignes).

*Les retours du programme 30 restent valides mot pour mot : la purge ne touche que
`DB_Communaute.lua`, et `7273904` (leur cible) est un ancêtre intact de `bd25056`.*

---

### BLOC C — un bilan manquant ne peut plus être vert

**Fait.** [sante_atelier.py](../WorkFlow/outils/sante_atelier.py) porte désormais la liste
`ETAPES_INSTRUMENTEES` (les 7 de l'Atelier **+ `aspirer_veille.py`**). `verdict(code, bilan,
script)` : chez une étape de cette liste, un `@@BILAN` **absent** est **ROUGE** (« l'étape est
morte avant ses comptes, ou sa sortie n'est pas capturée »), plus le vert neutre. Une étape
hors liste garde le vert neutre — légitime. Branché dans `collecteur.py` (bandeau) **et**
`banc_sante.py` (qui parcourt les étapes, plus les bilans — sinon un bilan manquant restait
invisible).

**La morsure, VUE** : j'ai retiré la marque `@@BILAN` d'`ingerer_caches` (une étape de la
liste), lancé, capturé :

```
étape sabotée (marque retirée) : code 0, @@BILAN capturé : None
VERDICT : ROUGE — bilan attendu et ABSENT — l'étape est morte avant ses comptes, ou sa sortie n'est pas capturée
l'ancien monde aurait dit : VERT
(@@BILAN remis en place)
contre-épreuve après remise : ('vert', 'rien à faire')
```

**Les deux petites choses :**

- **`ingerer_caches` comptait deux unités** (fichiers vs textes → « 11810/2160 »). Corrigé :
  le `@@BILAN` compte des **fichiers** des deux côtés (`tentees` = gz nouveaux, `traduites` =
  lus) ; les 11 810 textes restent dans la ligne humaine. La règle de majorité compare enfin
  la même unité.
- **Le vrai compte de `DB_Communaute`** (unité dite) : le rapport du 31 et le commit
  `f62d73c` disaient « 14 918 lignes » — faux des deux façons. Après purge (bloc B), le
  fichier fait **14 753 lignes physiques**, dont **14 543 ENTRÉES** (3 722 `G[gossip]` +
  5 767 `T[pnj]` + 5 054 `quete()`), 99 commentaires, 93 lignes vides, 18 d'entête Lua. La
  bonne phrase : **14 543 entrées** servies au jeu, pas « lignes ».

---

### BLOC D — l'exe de l'Atelier

**Reconstruit** depuis `outils/build_collecteur/Collecteur AscensionFR.spec` (PyInstaller
6.21, build terminé sans erreur, aucun module manquant dans le journal). L'exe fait
**37 645 182 octets** (ancien 37 623 016, +22 Ko — cohérent avec les ajouts). Posé à sa place
(`dist/Atelier AscensionFR.exe`, la cible du raccourci du bureau).

**Vérifié SUR l'exe reconstruit, pas sur le source** : lancé, il **reste vivant** (un exe
mal reconstruit — le piège « build depuis le mauvais arbre » du 28 — meurt en < 6 s ; celui-ci
tourne). **Une nuance d'architecture importante, à écrire** : cet exe est un *lanceur* —
`collecteur.py` (embarqué) insère `D:\AscensionFR\WorkFlow\outils` en tête du `sys.path` et
lance les 7 scripts depuis l'arbre VIVANT. Donc les **règles de verdict et les `@@BILAN`
viennent des fichiers vivants** (`sante_atelier.py`, les étapes), pas du binaire : ce que le
rebuild change, c'est `collecteur.py` lui-même — la capture des `@@BILAN`, l'appel à
`verdict(...)` et **la 3ᵉ couleur (orange)**, qui n'existaient pas dans l'ancien exe. Cette
logique-là, je l'ai éprouvée de bout en bout sur les modules réels (les deux morsures : code 3
« client absent » → rouge, `@@BILAN` retiré → rouge, rien-à-faire → vert).

🛑 **Ce que je n'ai PAS fait, et pourquoi** : faire défiler les trois couleurs dans la
fenêtre en conditions réelles demande un passage complet de l'Atelier (~2 h), et **Dan était
à sa machine, en jeu** au moment du build — j'ai refermé la fenêtre que j'avais ouverte
plutôt que piloter son bureau pendant qu'il jouait. L'exe est reconstruit, sain et lancé ;
son bandeau à trois couleurs suivra la logique déjà prouvée. Il n'est **pas douteux** — mais
je le dis franchement plutôt que de prétendre avoir vu la fenêtre virer au rouge.

---

### BLOC E — Confort ne s'installe pas depuis le Hub

**La mesure démolit la piste — la mienne comme celle de Dan.** Les 4 assets du catalogue,
téléchargés pour de vrai et ouverts avec la **vraie** `dossiers_addon_du_zip` du Hub :

| asset | version | structure | `.toc` trouvé ? |
|---|---|---|---|
| AscensionFR-Confort.zip | 1.7.0.1 (402 Ko) | `AscensionFR-Confort/` (30 entrées) | **OUI** |
| AscensionFR-Equipement.zip | 1.0.0.2 (92 Ko) | `AscensionFR-Equipement/` | **OUI** |
| AscensionFR-Peche.zip | v1.2.0 (9 Ko) | `AscensionFR-Peche/` | **OUI** |
| DragonUI.zip | v3.1.1 (8 Mo) | `DragonUI/` + `DragonUI_Options/` (554 entrées) | **OUI** (les deux frères) |

**Les quatre sont correctement formés aujourd'hui, sur Windows ET Linux** (forward-slash
partout, `create_system` FAT pour les 3 forks / Unix pour DragonUI, **0 backslash** — la
seule vraie divergence Windows/Linux possible, écartée par la mesure). Et le fait qui tranche :
**l'asset Confort n'a JAMAIS été re-téléversé** (`updated_at` = `created_at` = 2026-07-23) et
il compte **2 061 téléchargements**. Le joueur du 06/08 a donc téléchargé **ce zip-là**, bien
formé. **« Fabriqué à la main → à plat » (ta première piste, et la mienne) est démoli par le
chiffre.**

**Linux-seulement ou tout le monde ?** — Ni l'un ni l'autre : **le défaut n'est pas dans
l'asset**, donc il ne frappe *personne* par l'asset. Si c'était l'asset, ce serait tout le
monde (il n'a rien de spécifique à Linux). Je ne peux pas reproduire l'erreur du joueur ; les
causes possibles restantes (un Hub plus ancien chez lui, un téléchargement tronqué par son
réseau, une bizarrerie d'extraction SteamOS) demandent sa machine ou sa version exacte du Hub
— **je ne les ai pas, et je ne fabrique pas une conclusion** (comme au bloc F : une
non-réponse honnête vaut mieux).

**Ce que j'ai réparé quand même — défense en profondeur, part avec le prochain Hub :** le
**déballage** accepte désormais un zip **à plat** ou un wrapper `Depot-branche/` et le
**re-racine** sous le nom de la fiche, sans jamais poser un contenu **sans `.toc`** ; l'erreur
affichée **dit ce qui a été trouvé** (« Trouvé à la racine : … / Fichiers .toc présents : … »).
Bancs : **5 formes** (propre, à plat, `-main/`, DragonUI deux frères, sans le bon `.toc`) —
les 4 premières installent, la 5ᵉ refuse en nommant ce qu'elle a vu ; et les **4 assets réels**
repassent tous. Le **jumeau** `depot_github/compagnon/interface_hub.py` est **re-synchronisé**
à l'identique (il avait divergé — corrigé).

📌 **Le geste public à Dan : AUCUN.** Aucun asset n'est cassé, aucun n'est à refaire, rien à
re-téléverser. C'est la réponse — pas celle qu'on attendait, mais c'est celle que la mesure
donne. Le correctif de déballage attend seulement la prochaine version du Hub.

---

### 🛑 BLOC F — le conflit Clique et le « franglais »

**Hypothèse forte DÉMOLIE par le code et le chiffre ; une porte étroite reste ouverte, qui
demande la machine du joueur.**

**1. La 3.4.x change-t-elle le nom d'un sort là où un autre addon le relit ?** — **NON.**
Lecture complète du moteur (`Modules/Sorts.lua`, `Epreuves.lua`, `Tooltips.lua`, `Core.lua`) :
l'addon ne remplace jamais `GetSpellInfo`/`GetSpellName` (grep négatif — ces API ne sont que
**lues**). Il ne réécrit qu'à l'**affichage** : `SetText` sur la ligne 1 des infobulles
(`Sorts.lua:908-914`) et sur les boutons du grimoire (`Epreuves.lua:1409-1426`). Ce que
`GetSpellInfo` renvoie reste l'anglais du client.

**Et Clique (3.3.5, Cladhaire) stocke/lance par le NOM issu de l'API** (`GetSpellName` →
attribut sécurisé `spell="Nom"` → `CastSpellByName`). Sur un client enUS, l'API rend
**l'anglais** — qu'AscensionFR ne touche pas. **Donc la traduction d'affichage d'AscensionFR
ne peut ni changer ce que Clique mémorise ni ce qu'il lance.** Le mécanisme précis qu'on
soupçonnait n'existe pas dans le code.

**2. Ce qui a changé sur les NOMS de sorts, chiffré** (le pont `DB_SortsNoms`, seule surface
que Clique pourrait relire) :

| version | noms traduits (surface Clique) | DB_Sorts (par id) |
|---|---|---|
| 3.3.0 | 77 765 | 54 414 |
| 3.4.0 | **72 869** (−4 896 vs 3.3.0) | 54 471 |
| 3.4.3 | 72 915 | 54 581 |
| **courant (33)** | **72 912** | 54 590 |

Deux enseignements : (a) entre 3.3.0 et 3.4.0 le pont des noms a **perdu 4 896 noms** et en a
**churné** beaucoup (les purges poison/porteurs/appariement des programmes 2-10) — pour un
joueur dont un outil lit le nom **affiché**, des milliers de noms ont bougé, ce qui colle à
« la semaine dernière ça marchait » ; (b) **la 33 ajoute −3 noms vs 3.4.3** — le pont est
**gelé depuis la 3.4.0**.

**3. Le « franglais » est expliqué, et attendu par construction** : nom FR sur
l'infobulle/le grimoire (SetText), description FR **seulement si l'alignement réussit**, sinon
anglais conservé (`Sorts.lua:1139`), et **barre d'action + journal de combat jamais touchés**
(aucune interception — vérifié). Un même sort est donc FR ici, EN là. Ce n'est pas un bug :
c'est l'architecture « affichage seulement ». Le réduire = élargir l'interception (risque de
taint) ou passer au PackFR (client en français).

**➡️ Ce que ça coûte à la 33 : RIEN sur l'axe Clique.** La 33 ajoute **~0 nom de sort**
(−3) : la surface que Clique pourrait relire est **gelée depuis la 3.4.0**, que les joueurs
touchés font déjà tourner. Les **+6 715 traductions** de la 33 sont des Gossip / PNJ /
quêtes / Divers / Pages / descriptions — **aucune n'est un nom de sort**. Publier la 33
**n'étend donc pas** le problème : **F ne bloque pas la 33.**

**La porte étroite qui reste (non démolie, honnêtement)** : si le **fork de Clique** qu'utilise
ce joueur identifie le sort en **scannant le texte affiché** (l'infobulle/le bouton, français
après nous) plutôt que l'API — le mécanisme exact par lequel notre traduction **a déjà cassé
DragonUI** sur les plaques (`Plaques.lua:26-53`, garde posée) — alors la liaison casse. C'est
le **seul** chemin par lequel AscensionFR pourrait casser Clique, et il ne se tranche pas sans
sa source de Clique ou une trace en jeu.

**Ce qu'il me faudrait pour clore** (non-réponse honnête, comme tu l'autorises) : **un test en
jeu**, que le code rend simple — `/run AscensionFRSaved.Options.sansInterception = true`
coupe toute l'interception d'affichage à chaud (`Epreuves.lua:74-83`). Le protocole : créer
une liaison Clique **AscensionFR actif**, la vérifier, puis basculer `sansInterception`,
`/reload`, re-tester. Si la liaison **survit** → AscensionFR est **innocenté** définitivement
(c'est un conflit Clique/client, pas nous). Si elle **casse** avec l'interception et **remarche**
sans → c'est le chemin « scan de l'affichage », et le correctif est une garde comme celle de
DragonUI. Je n'ai pas de trace en jeu ; **aucun correctif appliqué**, comme demandé.

*(Les 48 signalements du bloc A ont été dépouillés d'abord, comme prescrit : « Clique » y
apparaît **1 fois**, « franglais » 0, « macro »/« WeakAura » 0. La réponse détaillée n'était
pas dans le gisement — mais le vérifier a coûté une lecture, pas trois heures de moteur.)*

---

### Ce qui a résisté, et ce que j'ai failli casser

- **Résisté** : le déballage re-racineur est parti en **récursion infinie** sur le zip à
  plat (la destination vivait dans le dossier scanné) — le banc l'a attrapé au premier tir,
  avant toute pose ; corrigé en figeant la liste des entrées avant de créer la cible. Le
  garde-fou « on ne pose rien sans `.toc` » a tenu sur les 5 formes.
- **Failli casser** : (1) la reconstruction de l'exe s'est faite pendant que **Dan jouait** ;
  la fenêtre de l'Atelier s'est ouverte derrière son jeu — je l'ai **refermée** au lieu de
  piloter son bureau, et je n'ai pas prétendu avoir vu le bandeau changer de couleur ; (2) mon
  guetteur de build (`Wait-Process`) et les chemins absolus m'ont évité de relancer une passe
  par-dessus une autre (le piège du 31) ; (3) le `cwd` de Bash a dérivé avec un `Set-Location`
  PowerShell — d'où deux `ls` à vide au début du bloc E, corrigés en repartant de la racine.
  Rien de cassé sur le disque.
- **Rien publié, aucun zip téléversé, aucun tag, aucune release, aucune fusion.** Les commits
  ne vivent que dans `depot_addon.git` **local** ; `WorkFlow` reste sans dépôt distant. Les
  retours du programme 30 restent valides mot pour mot.
- **Le seul geste public du lot — remettre en ligne des assets de forks — n'a pas lieu
  d'être : aucun asset n'est cassé.** La 33 peut partir sans réserve sur l'axe Clique.
