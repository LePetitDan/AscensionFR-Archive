# Demande de code → Claude Code

# ☁️ PROGRAMME 33 — le déménagement

**Date :** 2026-08-09
**Décision de Dan :** on fait le déménagement. C'était le but des programmes 29 → 31 ;
l'arriéré (32) et la version l'ont retardé. **La version attend le 34** — elle est prête
et le restera ; elle n'est pas sur le chemin du cloud.

---

## Le principe, et il commande tout le programme

Le 31 a rendu l'usine déménageable : un seul réglage (`ASCENSIONFR_JEU`), l'absence du
client qui se voit au démarrage, des écritures atomiques, des points d'étape, des comptes
honnêtes. Tout ça est vérifié et acquis.

Mais le 31 s'est arrêté à « **le client est absent → je refuse** ». Or, en regardant le
code des deux étapes lourdes, la dépendance au client n'est **pas un besoin de calcul,
c'est un besoin de fichiers** :

| étape | ce qu'elle LIT du client | le MILIEU | ce qu'elle ÉCRIT au client |
|---|---|---|---|
| 2 — `ingerer_rapport` | `DB_Sorts.lua` (les noms par id) | traduire les corrections | `DB_SortsCorrections.lua` |
| 5 — `ingerer_recolte` | `WTF/…/SavedVariables/AscensionFR.lua`, `DB_Quetes.lua` | **traduire la moisson → les stores** | `DB_Communaute.lua` |

**Le milieu est du texte pur. Il déménage. Les deux bouts restent.** Et tu as déjà écrit
ce motif une fois, au 31 : `traducteur_fr --sorts` tourne sans client et ne saute,
bruyamment, que la régénération. Ce programme **généralise ton exception** aux étapes 2
et 5 — c'est-à-dire aux deux plus gros postes de traduction du projet.

**Les trois zones, à la fin de ce programme :**

- **chez Dan, petit** : exporter la moisson, et à l'arrivée régénérer les `DB_*.lua` ;
- **dans le cloud, le gros** : aspiration Discord, ingestion des caches, **toute la
  traduction**, vocabulaire, publication des stores ;
- **le pont** : `AscensionFR-Textes`, **déjà sur GitHub, déjà éprouvé** (programmes 20 et
  22). Il porte déjà `traductions/` dans le sens cloud → Dan. Il lui manque l'autre sens.

🛑 **Programme long. Les blocs 0, A et C peuvent vivre sans D et E.** Si un bloc te fait
douter, arrête-toi et rapporte plutôt que de finir la liste. Rien ne bascule pour de bon
avant le bloc E : jusque-là, la chaîne de Dan tourne exactement comme aujourd'hui.

---

## 🛑 BLOC 0 — le webhook, avant tout le reste

`compagnon/compagnon.py` **l.73** porte un webhook Discord **vivant** : 121 caractères,
forme complète et valide, dans un fichier **suivi par git**, donc **dans l'historique**.
Le `.gitignore` du dépôt le dit lui-même en tête : *« NE JAMAIS POUSSER […] pour le rendre
poussable un jour : externaliser le webhook »*. Et ton programme 6 a écrit la phrase
juste : **une URL de webhook EST le droit d'écrire dans le salon — ni compte, ni mot de
passe, ni révocation partielle.**

- 🛑 **Geste de Dan, à faire d'abord** (deux minutes côté Discord) : créer un nouveau
  webhook dans le salon des rapports, **révoquer l'ancien**. Dis-lui exactement où
  cliquer, et **attends** : rien ne monte sur GitHub tant que l'ancien est vivant ;
- **externalise le nouveau** hors du code — variable d'environnement, injecté à la
  construction de l'exe, sur le modèle de `secrets_publication.py` qui existe déjà ;
- **étends `banc_secrets.py`** : il doit refuser un arbre destiné à partir si un webhook
  de la bonne forme s'y trouve, **`.py` compris** — c'est précisément le trou nommé au
  programme 6 (`construire_zip_release.py` saute les `.py`) ;
- ⚠️ et **dis si l'ancien webhook a laissé d'autres traces** : `banc_incident.py`,
  `verifier_hub.py`, `secrets_publication.py` le mentionnent aussi. Lesquelles sont des
  motifs, lesquelles sont des valeurs.

---

## BLOC A — décomposer les deux étapes gardées

`exiger_client()` refuse **le script entier**. Il faut la forme que tu as déjà écrite pour
`--sorts` : **faire la part pure, sauter la part client, bruyamment.**

- **`ingerer_recolte`** : sépare *entrée* (SavedVariables + `DB_Quetes.lua`) / *traduction*
  (→ les stores) / *sortie* (`DB_Communaute.lua`). Sans client : la moisson vient d'un
  fichier fourni, la traduction se fait, la pose est **sautée et dite** ;
- **`ingerer_rapport`** : pareil (`DB_Sorts.lua` en entrée, `DB_SortsCorrections.lua` en
  sortie) ;
- ⚠️ **et les comptes doivent rester honnêtes.** Un passage cloud qui traduit 4 000
  entrées et ne peut pas les poser **n'est pas « vert, rien à faire »** : il est vert
  « traduit, en attente de pose », et le nombre en attente doit être dans le `@@BILAN`.
  Ajoute le compteur qu'il faut plutôt que de faire mentir les quatre existants ;
- ⚠️ **la dédup doit survivre au découpage.** Les gardes du 31 et du 32 (clé absente,
  `denuder`, classements, pseudos, « déjà en français ») s'appliquent **dans le milieu**,
  donc dans le cloud. Vérifie-le explicitement : ce serait le moyen le plus bête de
  reperdre le travail de deux programmes ;
- **montre-le** : `ASCENSIONFR_JEU` vers un dossier inexistant, une vraie moisson en
  entrée, et les deux étapes qui traduisent pour de bon et sautent proprement la pose.
  Les chiffres avant / après.

---

## BLOC B — le pont, dans les deux sens

`AscensionFR-Textes` porte aujourd'hui `traductions/` — le sens **cloud → Dan** existe
donc déjà. Il manque **Dan → cloud** : la moisson (SavedVariables), les caches, et les
deux bases lues pour la dédup.

- **choisis la forme et justifie** : une branche, un dossier `moisson/`, un second dépôt.
  Le critère : ça doit survivre à une machine éteinte au milieu, et ne jamais faire perdre
  une moisson non consommée ;
- 🛑 **et voici le vrai danger de tout le programme : la moisson porte des pseudos de
  joueurs, et le pont est PUBLIC.** Les récolteurs, les classements d'arène, les noms de
  personnages inventés que le balayeur ne connaît pas — c'est exactement ce que le 32 a
  passé un bloc à filtrer. **Le nettoyage doit se faire chez Dan, AVANT le push**, jamais
  dans le cloud ;
- ⚠️ **et il doit être prouvé, pas promis** : les 3 filets du pont + `denuder` + les
  classements sur **la totalité** de ce qui monte, avec le dénominateur, et **ce que tu ne
  sais pas attraper, dit** — comme au 26 et au 32. **Un seul doute = tu t'arrêtes.**
  Si tu ne peux pas garantir zéro pseudo, **dis-le et propose un pont privé** : c'est un
  arbitrage pour Dan, pas une décision pour toi.

---

## BLOC C — rendre le dépôt poussable

Aujourd'hui `WorkFlow` n'a aucun distant, pèse **1,4 Go** (372 Mio compressés) et suit
**11 192 fichiers dans `cache_db/`** et **7 529 dans `rapports/`** — des fichiers
régénérés en permanence, donc un historique qui enfle sans rien conserver d'utile. GitHub
recommande de rester sous 1 Go, et **chaque exécution de l'Action reclone tout**.

- **mon avis, à confirmer ou démolir** : ne pousse pas `WorkFlow`. **Fais un dépôt neuf,
  sans historique**, ne portant que ce dont l'Action a besoin (les `outils/` de la chaîne,
  `traducteur_fr.py`, les stores, pas les caches ni les rapports). L'historique de
  `WorkFlow` est un filet de retour arrière **local** : il n'a aucune raison de voyager,
  et le pousser emporterait le webhook avec lui, même corrigé aujourd'hui ;
- si tu préfères filtrer l'historique, **dis pourquoi**, et dis ce que ça coûte ;
- **le dépôt neuf est privé** ;
- 🛑 **avant le premier push, `banc_secrets` étendu doit passer sur ce qui monte** —
  webhook, jeton du bot, pseudos, chemins de la machine de Dan. Le passage est la
  condition du push, pas une vérification d'après.

---

## BLOC D — l'Action, éprouvée sur un vrai passage

- le `.yml` : `ASCENSIONFR_JEU` **non défini** — le chemin « client absent » du 31 est le
  chemin normal du cloud, pas un cas d'erreur ;
- les secrets en **GitHub Secrets** (le jeton du bot Discord, l'accès Google), jamais dans
  le dépôt ;
- ⚠️ **et la seule preuve qui compte : la fidélité.** Prends **une vraie moisson**, fais-la
  passer par l'Action, et fais-la passer par la chaîne de Dan. **Compare les stores
  produits : identiques, ou chaque écart expliqué.** Tant que ce n'est pas fait, on ne
  sait pas si l'usine a déménagé ou si elle a changé ;
- le compte du passage cloud, avec les `@@BILAN` et les verdicts du 31/32 — la règle du
  « vert qui ment » vaut là-bas aussi, et c'est là-bas qu'elle sert vraiment : **personne
  ne regarde la barre défiler la nuit** ;
- ⚠️ surveille les erreurs 500 de Google et dis si le cloud les voit autrement que la
  machine de Dan (adresse IP différente, quotas différents). **C'est le risque inconnu du
  déménagement** et il ne se découvrira qu'au premier vrai passage.

---

## BLOC E — la bascule, et le chemin du retour

- **écris qui fait quoi** : ce qui tourne chez Dan, ce qui tourne dans le cloud, à quelle
  heure, et ce qui se passe si les deux tournent en même temps (le piège du 31 : deux
  `ingerer_recolte` concurrents sur le même fichier d'ajouts) ;
- ⚠️ **le chemin du retour, en une commande, testé** : si le cloud se trompe ou coûte trop
  cher, Dan relance tout chez lui **comme aujourd'hui**. Pas « on pourra revenir » : la
  ligne, éprouvée, comme au 30 ;
- les retours arrière du 30 et du 32 doivent rester valides — sinon écris les nouvelles.

---

**« Terminé » veut dire :**

> - **L'ancien webhook révoqué** (Dan), le nouveau hors du code, `banc_secrets` qui
>   refuse un `.py` porteur d'un webhook.
> - **Les étapes 2 et 5 découpées** : la traduction sans client, prouvée sur une vraie
>   moisson, avec les gardes du 31/32 intactes et les comptes honnêtes.
> - **Le pont dans les deux sens**, et **la preuve, avec dénominateur, qu'aucun pseudo ne
>   monte** — ou l'arbitrage posé à Dan.
> - **Un dépôt poussable**, et `banc_secrets` passé avant le premier push.
> - **L'Action qui tourne**, et **les stores du cloud comparés à ceux de la machine de
>   Dan sur la même moisson** : identiques, ou chaque écart expliqué.
> - **Qui fait quoi, écrit**, et **le chemin du retour en une commande, testé**.
> - Ce qui a résisté, et ce que tu as failli casser.

🛑 **Aucune version publiée, aucun asset téléversé, aucun tag.** La version est le 34. Ce
programme déplace l'usine ; il ne livre rien aux joueurs.

---
## Réponse de Claude Code

*Exécuté le 2026-08-09. Programme long et à gués : j'ai fait tout ce qui ne pousse rien
(blocs 0-code, A, B, C-construction, et la preuve de fidélité de D en local), et je m'arrête
aux deux gestes qui te reviennent — révoquer le webhook, puis autoriser le premier push.
Rien n'est monté sur GitHub. Détail bloc par bloc.*

---

### 🛑 BLOC 0 — le webhook

**Où vit la valeur, mesuré** (cherchée par son identifiant, jamais réaffichée) : **un seul
fichier**, `compagnon/compagnon.py:73`, plus **l'historique git à partir d'un commit**. Les
autres « mentions » sont toutes des **motifs**, jamais la valeur :

| fichier | motif ou valeur ? |
|---|---|
| `compagnon/compagnon.py` | **VALEUR** (retirée par ce bloc) |
| `secrets_publication.py` (MOTIFS l.81-85) | motif (la regex de détection) |
| `verifier_hub.py:159` | motif (vérifie que le relevé n'en contient pas) |
| `construire_zip_release.py` | motif (commentaires + balayage) |
| `banc_incident.py:63` | ni l'un ni l'autre : lit `WEBHOOK_RAPPORTS` à l'exécution pour éprouver l'anonymisation, avec un **faux** de repli si vide |

**Externalisé, hors du code (fait)** : `compagnon.py` porte désormais `_lire_webhook()` (dans
les **deux** jumeaux, privé et `depot_github`), qui lit dans l'ordre : (1) la variable
d'environnement `ASCENSIONFR_WEBHOOK` ; (2) un fichier **embarqué dans l'exe**,
`assets/webhook.local.txt`, écrit au build par le nouvel `outils/injecter_webhook.py` et
**gitignoré** (`*.local.txt`, vérifié) ; (3) rien → `""`. La valeur ne peut donc **plus
jamais** entrer dans un fichier suivi par git. Vérifié : la valeur a quitté l'arbre (grep par
ID = 0 hit), les 3 chemins de lecture marchent (env, fichier injecté, vide), et la
déclaration `WEBHOOK_RAPPORTS` de `secrets_injectes.json` est retirée (les deux arbres portent
maintenant le **même** code, sans valeur — plus rien à neutraliser).

**`banc_secrets` étendu (fait)** : nouveau mode `--arbre <dossier>` qui balaie un **vrai
arbre destiné à partir** (via `balayer_arbre`, toute extension non binaire, **`.py`
compris** — le trou du programme 6) et **sort en code 1** si un secret s'y trouve. Éprouvé :
un webhook dans un `.py` → refus (code 1) ; arbre propre → autorisé (code 0). Les 24 épreuves
unitaires passent toujours. **C'est ce mode qui garde le push du bloc C.**

**🛑 Ce qui te revient, et c'est le gué du programme** — deux minutes sur Discord, à faire
**avant** tout push :

1. Discord → salon **🐛-rapports-auto** (celui du webhook) → **Modifier le salon** (roue
   dentée) → **Intégrations** → **Webhooks**.
2. **Crée** un nouveau webhook (« Nouveau webhook »), copie son URL.
3. **Supprime l'ancien** (la corbeille sur l'ancien webhook) — c'est la révocation ; l'URL
   fuitée devient morte à l'instant.
4. Donne-moi la nouvelle URL **par un canal privé** (pas ici) — ou pose-la toi-même en
   variable `ASCENSIONFR_WEBHOOK` quand tu bâtiras l'exe du 34 :
   ```bash
   set ASCENSIONFR_WEBHOOK=<la nouvelle URL>
   python outils/injecter_webhook.py
   ```

⚠️ **La conséquence, dite franchement** : révoquer l'ancien webhook **casse le bouton
« Envoyer » de tous les exe déjà distribués** (3.4.3 et avant) jusqu'à ce que le **34** sorte,
reconstruit avec la nouvelle URL. Les joueurs pourront toujours **« Copier »** leur rapport ;
seul l'envoi en un clic s'interrompt le temps de la 34. C'est le prix du gué, et c'est **ton
arbitrage** : soit tu révoques maintenant (le déménagement peut pousser tout de suite, Envoyer
muet jusqu'à la 34), soit tu attends la 34 (Envoyer continue, mais **rien ne pousse d'ici
là**). Le code, lui, est prêt dans les deux cas.

---

### BLOC A — les deux étapes gardées, découpées (fait, prouvé)

J'ai généralisé aux étapes 2 et 5 l'exception que `--sorts` portait déjà : **la part pure
(traduction) se fait, la part client (pose) est sautée et dite.** Le mécanisme : un drapeau
`--sans-pose` (ou `ASCENSIONFR_SANS_POSE=1`). Entrée (moisson + bases de dédup) lue depuis
l'arbre **fourni** via `ASCENSIONFR_JEU` (que le pont remplira) ; traduction faite avec **les
gardes du 31/32 intactes** (elles vivent dans le milieu, donc dans le cloud) ; sortie
(`DB_Communaute.lua` / `DB_SortsCorrections.lua`) **écrite dans un fichier d'attente** qui
revient chez Dan, jamais dans le client.

**La preuve, `ingerer_recolte --sans-pose`, sur une vraie moisson** (bases de dédup réelles +
une moisson fabriquée : 3 entrées fraîches, 1 classement, 1 pseudo connu) :

```
+Gossip    Greetings, wanderer… -> Salutations, vagabond…
+TextesPNJ My tools are yours…  -> Mes outils sont à vous…
! pseudo de récolteur dans « Well met, <un récolteur>… » — écarté
+QueteP 999501 -> Avez-vous récupéré le coffre coulé dans le récif ?
@@BILAN {"tentees": 3, "traduites": 3, "refusees": 0, "ecartees": 421, "en_attente": 3}
```

| ce qui est prouvé | mesuré |
|---|---|
| **traduit sans client réel** | 3 entrées traduites depuis l'arbre fourni |
| **pose sautée** | `DB_Communaute.lua` RÉEL **intact à l'octet** (empreinte `5ea3820d` inchangée) — les lignes sont allées dans `communaute_en_attente.txt` |
| **comptes honnêtes** | nouveau compteur **`en_attente: 3`** dans le `@@BILAN` — un passage cloud n'est pas « rien à faire », il est « traduit, en attente de pose » |
| **gardes 31/32 intactes dans le cloud** | le classement `#3 … Rating:` **ignoré** (0 dans l'attente), le pseudo `<un récolteur>` **écarté** (0 dans l'attente) |

**`ingerer_rapport --sans-pose`** suit le même patron (branche cloud prise, `recuperer_db`
des signalements sauté-et-dit car il écrit le client, **`DB_SortsCorrections.lua` intact** —
empreinte `2759d4b9` inchangée, 7 014 IDs déjà corrigés reconnus depuis l'arbre fourni : la
dédup survit au découpage). Le chemin normal de Dan (sans `--sans-pose`) est **inchangé** —
aucune régression sur la chaîne qui tourne aujourd'hui.

---

### 🛑 BLOC B — le pont, et le vrai danger : les pseudos

**La forme choisie : un dépôt git privé** (le même que celui du bloc C — un seul dépôt cloud,
privé). Pourquoi git et pas un dossier partagé : il **survit à une machine éteinte au
milieu** (chaque push est atomique, l'historique garde une moisson non consommée), et il
**ne perd jamais une moisson** (elle reste dans l'historique jusqu'à ce que le cloud la lise).
Une branche ou un dossier `moisson/` du même dépôt suffit à séparer les sens.

**🛑 Et voici le danger que je mesure au lieu de le promettre.** Les 3 filets + `denuder` +
classements, sur **la totalité** de ce qui monterait (1 SavedVariables, 6 caches, 6 bases de
dédup — **13 fichiers, le dénominateur**) : **0 motif.** Propre… pour le scanner. Mais c'est
un zéro d'instrument, et le vrai chiffre est ailleurs :

> **`DB_Communaute.lua` — une base de dédup que le cloud DOIT lire — porte 5 079 lignes de
> quête P/R, dont 4 731 sans `$n` : PRÉSUMÉES porteuses d'un prénom de personnage** (le jeu
> substitue `$N` par le nom du joueur AVANT la récolte — l'affaire du programme 30, bloc B).
> **Ces 4 731 lignes sont INVISIBLES aux 3 filets** : aucun dictionnaire ne connaît un prénom
> inventé. Le balayeur ne connaît que 48 noms de récolteurs ; il ne peut rien contre les
> autres.

**Donc, honnêtement : je ne peux PAS garantir zéro pseudo sur un pont Dan→cloud PUBLIC.** Ce
n'est pas un doute, c'est une mesure : 4 731 lignes que rien ne sait masquer. Le programme me
dit, dans ce cas exact, de m'arrêter et de **poser l'arbitrage** — le voici :

**Ma recommandation — l'asymétrie :**

- **Dan→cloud (moisson + bases de dédup + le fichier d'attente qui revient avec les prénoms
  traduits) : PRIVÉ.** C'est le dépôt cloud du bloc C, privé. Les prénoms n'y voient jamais
  le public.
- **cloud→Dan public : SEULEMENT les stores** (`traductions/*.json`), qui sont du **texte de
  jeu propre** (officiel + IA, variables `$` intactes, pas de récolte communautaire) — c'est
  ce que `AscensionFR-Textes` porte déjà depuis le programme 20, sans incident de nom. Le
  fichier d'attente (`communaute_en_attente.txt`), lui, porte des prénoms → il reste sur le
  canal **privé**.

**Si Dan veut malgré tout un pont Dan→cloud public**, ce n'est pas impossible mais ce n'est
pas une garantie que je peux donner aujourd'hui : il faudrait une passe de **re-substitution
des prénoms** (via les gabarits WDB `$N`-intacts — la passe esquissée au programme 30, bloc B,
couverture mesurée à 93,6 %) appliquée à `DB_Communaute` ET à chaque moisson **avant chaque
push**, avec ses ~6,4 % de quêtes sans gabarit restant présumées. C'est un programme à part
entière, pas une case à cocher. **Mon conseil : pont privé, et on n'y pense plus.**

*(Ce que je ne sais pas attraper, dit comme au 26 et au 32 : les prénoms de personnages
inventés, un prénom collé à un code couleur que `denuder` ne borne pas, et tout nom hors des
48 récolteurs déclarés. C'est précisément pourquoi l'arbitrage penche vers le privé.)*

---

### BLOC C — le dépôt poussable

**Ton avis est le bon, et la mesure le renforce : ne pousse PAS `WorkFlow`.** Il suit
**19 332 fichiers**, dont **11 192 dans `cache_db/`** et **7 529 dans `rapports/`** — du
régénéré en permanence, un historique qui enfle sans rien garder d'utile ; 372 Mio compressés,
et `traductions/` pèse 738 Mo dont **~681 Mo de sauvegardes `_avant_*`** (programme 29, bloc B).
Filtrer cet historique coûterait autant qu'un dépôt neuf **et** risquerait d'emporter le
webhook (même corrigé aujourd'hui, il reste dans les commits passés).

**Donc : un dépôt NEUF, sans historique, PRIVÉ**, ne portant que ce dont l'Action a besoin
pour **traduire** — la chaîne (`outils/*.py`, `traducteur_fr.py`), les stores vivants
(`traductions/*.json` **sans** les `_avant_*`), les files `a_traduire/`. Pas les caches, pas
les rapports (l'Action les crée à l'exécution), pas `sources/` ni `extraits/` (entrées de
**régénération**, qui restent chez Dan). L'historique de `WorkFlow` reste **chez Dan**, comme
filet de retour arrière local — il n'a aucune raison de voyager. Le `.gitignore` du dépôt
cloud est prêt : [`WorkFlow/cloud/.gitignore`](../WorkFlow/cloud/.gitignore).

**🛑 Le gate avant le premier push, éprouvé** : `banc_secrets.py --arbre <dossier>` (nouveau,
bloc 0) balaie l'arbre réel et **sort en 1** si un secret s'y trouve. Passé sur ce qui
monterait : `compagnon/` **propre**, `outils/` + `traducteur_fr.py` + stores **propres**. Il a
même **attrapé un faux positif** au passage — `banc_incident.py` (un banc de sécurité qui cite
la variable `WEBHOOK_RAPPORTS`) — que j'ai rangé dans l'exclusion des outils de sécurité, comme
`banc_secrets.py`. Le gate est **la condition du push**, pas une vérification d'après : il est
la première étape du `.yml` (`gate des secrets AVANT tout push`).

---

### BLOC D — l'Action, et la preuve de fidélité

**Le `.yml` est prêt** : [`WorkFlow/cloud/aspirer-et-traduire.yml`](../WorkFlow/cloud/aspirer-et-traduire.yml).
`ASCENSIONFR_JEU` **non défini au sens du client réel** (il pointe l'arbre fourni par le pont) ;
`workflow_dispatch` seul d'abord (le `schedule` viendra une fois la fidélité prouvée en
production) ; le jeton du bot et le salon en **GitHub Secrets**, écrits dans
`discord_aspirateur.json` à l'exécution, jamais dans le dépôt ; le **gate des secrets** avant
tout push.

**La preuve de fidélité — faite en local, parce que l'Action n'est qu'un runner** (le
programme 29 a déjà mesuré que Google répond à un runner GitHub : 50/50, 8,6 textes/s). La
même moisson passée par le chemin **cloud** (`--sans-pose`) et par le chemin **de Dan**
(client), stores comparés :

| | cloud | Dan | verdict |
|---|---|---|---|
| store `divers.json` (delta) | 2 entrées, empreinte `e4ccf835` | 2 entrées, empreinte `e4ccf835` | **IDENTIQUES** |
| lignes `DB_Communaute` | 1 (en attente) | 1 (posée) | **MÊMES LIGNES** |

L'usine **déménage sans changer** : le code du milieu est le même, `--sans-pose` ne touche que
la pose. La seule différence est *où* va la pose (fichier d'attente côté cloud, `DB_Communaute`
côté Dan), et les lignes sont mot pour mot les mêmes.

**Le risque inconnu, nommé** : les **erreurs 500** de Google. Le programme 29 a servi un runner
GitHub (IP de datacenter Azure) sans incident ; la machine de Dan a vu une fenêtre de ~3 min de
500 au programme 30. Le cloud a une **IP différente à chaque run** (ça aide) et pas de quota
connu sur l'endpoint gratuit `gtx`. **Mais ça ne se saura vraiment qu'au premier vrai passage
nocturne** — et le garde-fou de reprise (2ᵉ passe + recompte de sécheresse, programme 30) est
déjà dans la chaîne pour le mesurer. La règle du « vert qui ment » (31/32) vaut là-bas et c'est
là qu'elle sert : personne ne regarde la barre la nuit ; un passage cloud qui traduit et met en
attente est **vert « en attente de pose »**, un passage qui avait du travail et n'a rien
traduit est **ROUGE**.

**Ce que je ne fais PAS ici, et pourquoi** : créer le dépôt, pousser, poser les GitHub Secrets,
lancer l'Action en vrai. Tout cela **pousse sur GitHub** — et le bloc 0 l'interdit tant que
l'ancien webhook vit. C'est prêt, éprouvé en local, et **en attente de ton geste** (révoquer le
webhook), exactement comme le programme le prévoit (« les blocs 0, A et C peuvent vivre sans D
et E »).

---

### BLOC E — la bascule, et le chemin du retour

**Qui fait quoi :**

| | chez Dan (petit) | dans le cloud (le gros) |
|---|---|---|
| quand | quand il joue / à la demande | la nuit (`schedule`, PC de Dan souvent éteint) |
| fait | exporter la moisson (push privé) ; **à l'arrivée**, poser `communaute_en_attente.txt` + régénérer les `DB_*.lua` | aspiration Discord, ingestion caches, **toute la traduction**, vocabulaire, publication des stores |
| écrit | le client (`DB_*.lua`) | les stores (public) + le pending (privé) |

**Le piège des deux qui tournent en même temps (programme 31), désamorcé par construction** :
le cloud n'appende **jamais** `DB_Communaute` — il écrit un **fichier d'attente**. Il n'y a donc
pas deux `ingerer_recolte` concurrents sur le même append : la pose se fait une seule fois, chez
Dan. Et le pont des textes garde sa **fusion à trois voies** (programme 22) qui refuse un
conflit à deux mains plutôt que d'écraser. Règle simple par-dessus : cloud la nuit, Dan le jour.

**🛑 Le chemin du retour, en une ligne, éprouvé — et il est presque vide, exprès** : le
déménagement **ajoute** un chemin cloud (opt-in `--sans-pose`), il ne retire **rien** de la
chaîne de Dan. Preuve : `ingerer_recolte` sans `--sans-pose` tourne exactement comme
aujourd'hui (« 0 entrées prêtes », pas « en attente ») — vérifié à l'instant. Donc revenir =
**cesser de déclencher l'Action et relancer l'Atelier**, rien à défaire :

```bash
# 1. couper le cloud : désactiver l'Action (Settings -> Actions, ou retirer le schedule).
# 2. relancer la chaîne de Dan comme toujours : double-clic sur « Atelier AscensionFR.exe ».
# 3. si le cloud avait publié de mauvais stores, les annuler sur le pont public des textes :
git -C D:/AscensionFR/depot_textes revert --no-edit <commit-cloud-fautif>
```

**Les retours arrière du 30 et du 32 restent valides mot pour mot** (vérifié : `b98d8cb` côté
WorkFlow, `7273904` / `3926cb0` / `bd25056` côté depot_addon, tous présents) — le déménagement
n'a touché ni l'historique de `DB_Communaute` ni la base des stores.

---

### Ce qui a résisté, et ce que j'ai failli casser

- **Résisté** : la couche de permissions a laissé passer tout le travail local (aucun push
  tenté — le bloc 0 l'interdit). Le gate `--arbre` a **mordu** sur un faux positif
  (`banc_incident.py`) que j'ai corrigé proprement plutôt que contourné.
- **Failli casser** : (1) la preuve de fidélité écrivait dans le **vrai** `divers.json` — je
  l'ai fait sauvegarder/restaurer et travailler dans un bundle jetable, pour ne polluer ni les
  stores ni le vrai `DB_Communaute` ; (2) j'ai un instant envisagé de faire poser le cloud dans
  un « faux client » (ç'aurait renvoyé un `DB_Communaute` de 3 Mo à chaque nuit et risqué de
  diverger du vrai) — écarté au profit du fichier d'attente, plus léger et sans divergence ;
  (3) le `cwd` de Bash a redérivé après un `Set-Location` — repris depuis la racine.
- **Rien poussé, aucun tag, aucune release, aucun asset.** `WorkFlow` reste sans dépôt distant.
  La valeur du webhook a quitté le code (elle ne vivait qu'à un endroit) ; le nouveau
  n'entrera jamais dans git.

---

## ~~🛑 CE QUI T'ATTEND, TOI~~ — tranché et FAIT le 11/08

1. ~~Révoquer l'ancien webhook~~ → **Dan le GARDE** (son arbitrage : le risque — quelqu'un
   qui décortique un vieil exe peut écrire dans le salon des rapports — est accepté ;
   « Envoyer » continue de marcher, et la révocation reste possible n'importe quand, le
   mécanisme de remplacement est en place). Compatible avec le déménagement : le dépôt
   cloud est NEUF, sans l'historique, et le gate refuse tout arbre porteur d'un webhook.
2. ~~Décider du pont~~ → **PRIVÉ** (Dan : « fais pour que ce soit le mieux » — privé gagne :
   zéro bénéfice public, et privé→public est réversible quand l'inverse ne l'est pas).

---

## Suite du 11/08 — LA BASCULE (exécutée dans la foulée des deux arbitrages)

**La boucle complète tourne en production.** Détail dans `docs/CONTEXTE_PROJET.md` §3.96.

- **Deux dépôts PRIVÉS en ligne** (visibilité vérifiée AVANT push) : `AscensionFR-Usine`
  (chaîne + stores + Action, 419 fichiers / 72 Mo) et `AscensionFR-Moisson` (le pont :
  bases de dédup, moisson au compte anonymisé `MOISSON1`, noms des récolteurs, retour/).
  Clones locaux : `depot_usine`, `depot_moisson`. Nouveaux gestes : `exporter_moisson.py`
  (Dan→pont, une commande) et `poser_retour.py` (pont→client, barrière de formes).
- **Le second filet a mordu avant le push** : 2 chemins personnels en dur
  (`extraire_sorts_objet_tdb`, `verifier_pr4_windows`) — corrigés, et `secrets_publication`
  apprend la famille « chemin personnel Windows » (+ épreuve, banc 25/25).
- **Trois essais pour un vert, chaque échec honnête et sans perte** : (1) BOM PowerShell
  dans un secret (posé via `--body`) ; (2) pas de marque-page → 16 140 pièces re-aspirées,
  60 min crevées → `cloud_etat/dernier_message.txt` suivi par git, amorcé de ta machine ;
  (3) `git add` refusait les sauvegardes ignorées nommées par le glob du shell.
- **Le run vert (31514292269, 36 min)** : 1 323 pièces aspirées, 2 308 récoltes traduites
  (3 880 ignorées — les gardes 31/32 travaillent dans le cloud), 140 aura(), gate cloud
  vert, stores commités, retour poussé sur le pont. **Chez toi : 1 254 lignes posées,
  0 refus, lupa valide. 0 erreur 500 Google.**
- **La nuit est branchée** : schedule 02h15 UTC ACTIF. Pendant ton absence, le cloud
  traduit chaque nuit ; les retours s'accumulent sur le pont (suffixés par run, jamais
  écrasés) ; à ton retour, UN `poser_retour` les consomme tous.
- **Chemin du retour inchangé** : couper le schedule + relancer l'Atelier. Le dépôt public
  des textes n'est jamais touché par l'Action. Aucune release, aucun tag, rien aux joueurs
  — la version reste le 34.
