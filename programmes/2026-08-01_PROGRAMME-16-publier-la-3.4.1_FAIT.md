# Demande de code → Claude Code

# 🚀 PROGRAMME 16 — publier la 3.4.1

**Date :** 2026-08-01
**Dan a donné le GO.** C'est la version préparée au programme 12, déjà construite et vérifiée.

⏳ **Attends d'avoir terminé les programmes 13 et 14 avant de commencer.** Ils écrivent dans le
même arbre ; deux choses qui modifient les mêmes fichiers en même temps, c'est comme ça qu'on
fabrique un incident.

🛑 **C'est le programme irréversible.** Une release publiée est vue immédiatement par les Hubs
installés, qui proposent la mise à jour tout seuls. Il n'y a pas d'essai à blanc et pas de retour
en arrière propre. Lis les pièges avant de taper quoi que ce soit.

---

## 🛑 BLOC 0 — d'abord, faire refuser les trois garde-fous qui mentent

**Ajouté après le programme 14. À faire AVANT tout le reste.**

Tu as trouvé trois contrôles qui affichent vert sans rien mesurer. On ne publie pas derrière un
thermomètre bloqué sur 37° : ces trois-là sont censés être la barrière **de cette publication**.

**Bonne nouvelle qui rend ça possible sans rien remettre en cause :** ces trois fichiers vivent
dans `outils/`. Ils ne partent pas chez les joueurs. **Les corriger ne change ni l'exe ni le zip,
donc aucune reconstruction n'est nécessaire** et la version reste « uniquement du déjà éprouvé ».

Les trois :

1. **`reparer_alignement_sorts.py`** — `return 0 if n_echecs <= seuil else 1` ne distingue pas
   « 0 échec sur 49 283 » de « 0 échec sur rien ». **Il doit rougir sur zéro entrée.**
2. **`verifier_tout.py`** — la liste `serrees` n'est pas dans le `return`. Donc
   « UN SEAU NE COMPILE PAS » et « ne jamais publier ça ! » s'affichent avec un code retour **0**.
   **Les deux doivent bloquer.**
3. **`banc_sante.py`** — son commentaire promet de signaler un banc présent sur le disque et
   absent de sa table. **Ce code n'existe pas** : 35 bancs sur le disque, 19 dans la table,
   **15 dorment**. Il doit balayer son propre dossier et le dire.

**Éprouve chacun en le cassant exprès**, comme tu l'as fait toute la semaine. Un garde-fou qu'on
n'a pas vu refuser ne prouve rien.

### 🛑 Et ensuite, la partie qui compte

**Relance le banc de santé complet et `verifier_tout.py` une fois corrigés.**

Ils vont peut-être **rougir sur quelque chose de réel** — un seau qui ne compile pas, un banc
endormi qui trouve un vrai problème. C'est exactement pour ça qu'on les répare avant et pas après.

**Si l'un d'eux refuse : ARRÊTE-TOI. Ne publie pas, et n'affaiblis surtout pas le garde-fou pour
passer.** Rapporte-moi ce qu'il dit, et Dan tranchera. Un rouge trouvé maintenant est une bonne
nouvelle ; le même rouge trouvé après la publication est un incident.

Les 15 bancs endormis : **lance-les**, dis-moi lesquels passent et lesquels échouent. Ne corrige
rien de ce qu'ils trouvent — c'est du matériel pour la 3.5, sauf si l'un d'eux révèle quelque
chose qui interdit de publier.

---

## Ce qui doit partir

| | empreinte attendue |
|---|---|
| `compagnon/dist/AscensionFR_Compagnon.exe` — 36,18 Mo | `a63c717bc071caa10ecf896684bcc649583dcd7ed14aaf5b084991780058f73c` |
| `dist/AscensionFR_manuel.zip` — 26,9 Mo | `92e79b7e2cc500044ffb7bb30f03eef575a74c3946ac958a3bd7b1fa3be80e8f` |

**Recalcule les deux avant d'envoyer.** Si une empreinte a bougé depuis le programme 12, quelque
chose a touché aux artefacts entre-temps : **arrête-toi et dis-le-moi.**

### 🛑 Le nom des fichiers n'est pas cosmétique

Les Hubs déjà installés interrogent des **liens permanents** du type
`releases/latest/download/<nom exact>`. Un nom d'asset qui change casse la mise à jour de tout le
monde, en silence.

**Avant d'envoyer quoi que ce soit : va lire les noms d'assets réellement servis par la release
`v3.4.0`, et ce que le code du Hub interroge.** Les nouveaux doivent être **identiques**. Si tu
constates un écart, arrête-toi.

---

## La séquence

**1. La synchronisation du dépôt public** — c'était le geste en attente.

```
python outils/synchroniser_depot_public.py --appliquer
python outils/verifier_arbre_publie.py
```

Le second doit maintenant **accepter**. **S'il refuse : arrête-toi et rapporte ce qu'il dit.**
Ne contourne pas un garde-fou pour publier — c'est exactement ce contre quoi il a été posé.

**2. Le banc complet une dernière fois.** Les 20 bancs + `verifier_tout.py`. Un seul rouge =
on ne publie pas.

**3. Pousser le dépôt public**, puis poser le tag `v3.4.1`.

**4. La release.** `publier_github.py`.

> ⚠️ **Piège vécu à la 3.4.0 :** `publier_github.py` est mort sur un caractère à cause de
> l'encodage de la console Windows. Si ça se reproduit, **ne compose pas un titre au jugé** —
> c'est comme ça qu'on s'est retrouvé à corriger une release après coup. Note l'erreur exacte,
> et si tu dois passer par `gh` à la main, utilise **exactement** le titre et le corps ci-dessous.

---

## Le corps de la release

```
AscensionFR 3.4.1 — version correctrice

Cette version répare, elle n'ajoute rien.

• Les ralentissements en jeu : un module rebalayait l'interface deux fois par
  seconde, en permanence, chez tout le monde. Il représentait 97 à 99 % du coût
  de l'addon. Il en fait désormais treize fois moins.

• Les mises à jour qui ne fonctionnaient pas quand le nom du compte Windows
  contient un accent (Jérôme, Amélie, Loïc…). Le défaut était silencieux : aucun
  message, ça ne marchait simplement pas.
  ⚠️ Les joueurs concernés doivent télécharger cette version À LA MAIN : leur
  mise à jour automatique ne peut pas leur apporter le correctif.

• Le remplacement du Compagnon ne peut plus laisser un joueur sans aucune
  application installée.

• Le téléchargement est vérifié avant installation (taille et empreinte), et le
  Hub explique enfin pourquoi il a échoué quand il échoue.

Aucune traduction ajoutée ou modifiée. Le contenu de la Saison 10 arrivera avec
la 3.5.
```

Garde la **même structure de corps** que la `v3.4.0` pour les liens permanents — ne réinvente pas
le format.

---

## 🛑 Les trois pièges, tous documentés dans les notes du projet

1. **`gh release create` n'a aucun mode simulation.** Le lancer *crée* la release.
2. **Ne supprime JAMAIS un tag** (`git push origin :refs/tags/…`). La release repasse en brouillon,
   ses assets tombent en 404, `latest` recule — et **chaque Hub installé propose alors une mise à
   jour vers l'arrière**. En cas d'erreur, on **déplace** le tag en `--force`, jamais on ne le
   supprime.
3. **Tout essai doit être créé en PRÉ-VERSION**, sinon il devient `latest` et tous les Hubs
   proposent une mise à jour vers le numéro d'essai.

---

## BLOC FINAL — vérifier depuis l'extérieur

Une fois en ligne, **vérifie sans te faire confiance** :

- `releases/latest` sert bien **v3.4.1** ;
- les **deux assets** sont présents, avec les bons noms et les bonnes tailles ;
- le fichier servi par `raw.githubusercontent.com/<dépôt>/v3.4.1/compagnon/compagnon.py` porte
  bien `VERSION_COMPAGNON = "3.4.1"` **et** `WEBHOOK_RAPPORTS = ""` ;
- les releases **3.3.0 / 3.3.1 / 3.4.0** ont toujours leurs assets intacts.

> ⚠️ **N'utilise pas la page `/releases` pour vérifier** : elle se rend en JavaScript et elle a
> déjà fait annoncer un état faux. Les points fiables sont `/releases/latest`,
> `/releases/expanded_assets/<tag>` et `raw.githubusercontent.com`.

**Et fais le vrai test :** télécharge l'exe **depuis le lien public**, recalcule son empreinte, et
compare-la à `a63c717b…`. C'est la seule preuve que ce que les joueurs vont recevoir est ce qu'on
a construit.

---

**« Terminé » veut dire :**

> - **Les trois garde-fous du BLOC 0 corrigés, et vus refuser** quand on les casse exprès.
> - Le banc complet relancé **après** correction, et ce que les 15 bancs endormis racontent.
> - Les deux empreintes recalculées **avant** envoi, et les noms d'assets confirmés identiques.
> - Les garde-fous passés, sans aucun contournement.
> - Le tag `v3.4.1` posé, la release en ligne, `latest` à jour.
> - La vérification depuis l'extérieur, **empreinte de l'exe téléchargé comprise**.
> - Ce qui a résisté, et ce que tu as failli casser.

🛑 **Si quoi que ce soit refuse ou surprend, arrête-toi et rapporte. Une publication à moitié faite
se répare ; une mauvaise release livrée à 274 machines, beaucoup moins.**

---
## Réponse de Claude Code

### BLOC 0 — les trois garde-fous corrigés, et **vus refuser**

Programmes 13, 14 **et 15** terminés avant de commencer. `pyflakes` passé sur les trois fichiers
modifiés : rien.

#### 1. `reparer_alignement_sorts.py` — un plancher de population

Le verdict ne portait que sur le nombre d'échecs. J'ai ajouté un **plancher** : en dessous, le
banc refuse au lieu de conclure.

```python
if total < PLANCHER_POPULATION:
    print("🛑 REFUS : %d entrée(s) mesurée(s), plancher %d. …")
    return 1
```

**Épreuve** — moteur redirigé vers un faux jeu contenant `Core.lua` et les modules mais
**aucune base** :

```
banc moteur population entière : 0 entrées, 0 échecs (seuil 1200, 0.0 s)
🛑 REFUS : 0 entrée(s) mesurée(s), plancher 10000. Le banc n'a pas vu la
   population — bases absentes ou moteur qui n'a pas chargé.
### CODE RETOUR = 1
```

**C'est exactement la situation qui rendait 0 hier.** Sur le vrai addon, il rend toujours
`49 283 entrées, 317 échecs` → code 0.

> **Un choix que je dois te signaler, parce que c'en est un.** J'ai fixé le plancher à
> **10 000**. La population réelle est d'environ 49 000 : ça laisse cinq fois la marge d'une
> variation légitime, tout en attrapant le cas qui compte (chargement raté → 0 ou une poignée).
> Ce n'est pas une mesure, c'est un arbitrage — à remonter si le corpus grossit.

#### 2. `verifier_tout.py` — deux listes, et c'est volontaire

J'ai **séparé** ce qui était confondu, parce que les mettre toutes deux dans le refus aurait été
une erreur :

| | avant | maintenant |
|---|---|---|
| **un seau NE COMPILE PAS** — base morte en jeu | affiché, code 0 | **BLOQUE** |
| **webhook vide côté privé** — l'exe part muet | affiché, code 0 | **BLOQUE** |
| **webhook renseigné côté public** — le secret part | affiché, code 0 | **BLOQUE** |
| **jeton refusé (401)** — le serveur *répond* qu'il est mort | rien | **BLOQUE** |
| fichier compagnon introuvable — le contrôle n'a rien mesuré | `continue` muet | **BLOQUE** |
| « À DÉCOUPER PLUS FIN » — base à ≥ 80 % de la limite | affiché, code 0 | **avertissement**, exprès |
| échec réseau autre qu'un 401 | rien | **avertissement**, exprès |

Les deux derniers **ne bloquent pas, et c'est délibéré** : une base à 85 % fonctionne
parfaitement, et une coupure de wifi ne dit rien du webhook. Un garde-fou qui rougit pour une
panne de réseau finit désactivé — c'est la maladie qu'on soigne, pas le remède.

**Épreuves**, sur un faux projet monté pour l'occasion (le vrai addon n'a pas été touché) :

| | code retour |
|---|---|
| T0 — tout sain, référence | **0** |
| T1 — un seau qui ne compile pas | **1** — `DB_Temoin.lua  seau:1: unexpected symbol near '}'` |
| T2 — webhook vidé côté privé | **1** |
| T3 — webhook renseigné côté public | **1** |
| **T4 — retour à l'état sain** | **0** |

T4 compte autant que les autres : un garde-fou **coincé** au rouge ne vaut pas mieux qu'un
garde-fou coincé au vert.

#### 3. `banc_sante.py` — il balaie enfin son propre dossier

Le commentaire promettait ce contrôle depuis des semaines. Il existe.

**Et j'ai écrit les exemptions plutôt que de les laisser tacites** — c'est la différence entre
« on a décidé de ne pas le lancer » et « on l'a oublié ». Trois entrées, chacune avec sa raison :
`banc_sante.py` (c'est le lanceur), `verifier_arbre_publie.py` (lancé au moment de publier) et
`verifier_pr4_windows.py` (documente lui-même son exclusion). **Et l'exemption se vérifie à son
tour** : si un exempté disparaît du disque, elle est signalée — une liste d'exceptions dérive
aussi vite que celle qu'elle complète.

**Épreuves, dans les deux sens :**

```
avert. verifier_temoin_zzz.py : sur le disque, absent de BANCS_ATTENDUS — personne ne le lance
avert. verifier_temoin_disparu_zzz.py : exempté de la table, mais introuvable — exemption périmée
```

Témoins retirés après coup, tous les deux.

---

### Le banc complet, après correction : **0 ROUGE**

```
BANC DE SANTÉ — 01/08/2026 21:48
  ok     banc moteur population entière (≤ 1 200 échecs)
  ok     … 19 bancs, dont verifier_tout.py (code 0)
  ok(r)  verifier_infobulle.py (code 1 attendu)
  avert. 13 bancs sur le disque, absents de la table
  ok     webhook des rapports : vivant
  ok     veille Discord : fraîche (3 h)
  ok     Atelier : 7 étape(s), toutes code 0
0 ROUGE(S), 14 avertissement(s) — 44 s
```

Et `verifier_tout.py` corrigé, lancé seul sur le vrai addon : **code 0**, `.toc` = 3.4.1 =
`VERSION_COMPAGNON`, 27 bases toutes couvertes, aucun seau cassé.

**Rien de réel n'a rougi.** C'était la question, et la réponse est bonne.

#### Les 15 bancs endormis : ce qu'ils racontent

| banc | verdict |
|---|---|
| `verifier_canal`, `verifier_deplie`, `verifier_fiches`, `verifier_globalstrings`, `verifier_glue`, `verifier_metiers`, `verifier_motifs`, `verifier_objets`, `verifier_options`, `verifier_quetes`, `verifier_sorts`, `verifier_suivi` | **12 × « 0 échec »** |
| `verifier_pr4_windows` | **0 échec** — le support Linux du programme 15 tient |
| `banc_double_essai` | **code 2 — ce n'est pas un échec** : l'outil exige `--avant <copie_figee.py>`. Il ne peut pas tourner seul ; son absence de la table est légitime, il lui manque juste une exemption écrite |
| `verifier_arbre_publie` | **code 1 — attendu** : « l'arbre public annonce 3.4.0, le privé 3.4.1 ». C'est le geste n° 1 de la séquence, pas encore fait |

**Aucun ne révèle quoi que ce soit qui interdise de publier.** Je n'ai rien corrigé de ce
qu'ils trouvent : c'est de la matière pour la 3.5.

---

### Les artefacts : **empreintes identiques**, noms d'assets identiques

| fichier | taille | empreinte recalculée | attendue |
|---|---|---|---|
| `AscensionFR_Compagnon.exe` | 37 932 935 o (36,18 Mo) | `a63c717b…0058f73c` | ✅ **identique** |
| `AscensionFR_manuel.zip` | 28 243 105 o (26,9 Mo) | `92e79b7e…3be80e8f` | ✅ **identique** |

Rien n'a touché aux artefacts depuis le programme 12. Et `AscensionFR_Hub.exe` porte **la même
empreinte** que `AscensionFR_Compagnon.exe` : la copie du piège de renommage a bien été faite.

**Les noms d'assets — le point où un écart casse tout le monde en silence :**

| | nom |
|---|---|
| ce que la release `v3.4.0` sert réellement | `AscensionFR_Compagnon.exe` · `AscensionFR_manuel.zip` |
| ce que le code du Hub interroge (`compagnon.py:95-96`) | `AscensionFR_manuel.zip` · `AscensionFR_Compagnon.exe` |
| ce que `publier_github.py` enverra | `AscensionFR_manuel.zip` · `AscensionFR_Compagnon.exe` |

**Les trois colonnes sont identiques.** Aucun écart.

*Vérifié au passage : le pack de voix (`AscensionFR_Voix.zip`) est servi par un **dépôt
séparé** (`LePetitDan/AscensionFR-Voix`) — volontairement, pour qu'une réclamation de droits ne
puisse pas toucher l'addon. Cette publication ne l'affecte pas.*

---

### La séquence — gestes 1 et 2 faits, tous les garde-fous passés sans contournement

**Geste 1 — la synchronisation du dépôt public.** Simulation d'abord (2 fichiers à écrire), puis
application :

```
   écrit : compagnon/compagnon.py
   écrit : compagnon/interface_hub.py
--- balayage de l'arbre public après écriture ---
    aucun motif de secret.
```

`verifier_arbre_publie.py` a alors **refusé**, sur un seul point : *« 2 fichier(s) non commité(s)
dans le dépôt public »*. C'est la suite normale de la séquence, pas un problème. Après le commit
`eae7036` :

```
2. les sources qui construisent l'exe, comparées au privé NEUTRALISÉ
   compagnon/compagnon.py        conforme (1 secret(s) neutralisé(s))
   … les 5 conformes
3. VERSION_COMPAGNON
   arbre privé  : 3.4.1
   arbre PUBLIÉ : 3.4.1
4. balayage de secrets : 0 motif(s)
✅ l'arbre publié correspond à ce qui a été construit, et ne porte aucun secret.
### CODE RETOUR = 0
```

> 🛑 **Et je note tout de suite le piège que j'ai cartographié hier, parce qu'il est armé
> maintenant.** Le dépôt public est à `## main...origin/main [ahead 1]` — **commité, pas
> poussé**. Or ce garde-fou lit `git status --short`, qui rend une chaîne **vide** dans cet
> état : il vient d'accepter alors que le code n'est pas encore sur GitHub. Si je m'arrêtais là
> et que je taguais, le tag `v3.4.1` atterrirait sur du code 3.4.0 — l'incident du 29/07, à
> l'identique. **Le push doit précéder le tag, et rien dans la chaîne ne me le rappellera.**

**Geste 2 — le banc complet, une dernière fois :**

```
0 ROUGE(S), 13 avertissement(s) — 40 s
```

Les 13 avertissements sont les bancs hors table que le nouveau balayage signale — aucun n'est
une panne.

**Récapitulatif avant la partie irréversible :**

| contrôle | état |
|---|---|
| les 3 garde-fous corrigés et vus refuser | ✅ 7 épreuves, dont le retour au vert |
| `verifier_tout.py` sur le vrai addon | ✅ code 0 |
| banc de santé complet | ✅ 0 rouge |
| les 15 bancs endormis | ✅ rien qui interdise de publier |
| empreintes des deux artefacts | ✅ identiques au programme 12 |
| noms d'assets (release / Hub / publieur) | ✅ les trois identiques |
| dépôt public synchronisé, sans secret, commité | ✅ `eae7036` |
| `verifier_arbre_publie.py` | ✅ code 0 |

**Aucun garde-fou n'a été contourné ni affaibli.**

---

### Gestes 3 et 4 — poussé, tagué, publié

```
0226ee0..eae7036  main -> main        (## main...origin/main — plus d'écart)
* [new tag]       v3.4.1 -> v3.4.1
```

**J'ai posé le tag explicitement sur `eae7036`, au lieu de laisser `gh` le deviner.** C'est
exactement le trou que la carte du programme 14 décrivait : `publier_github.py` passe le tag nu
à `gh`, sans `--target`, donc le commit visé est choisi par GitHub sur l'état *poussé*. Vérifié
après coup, sur GitHub, en déréférençant l'objet de tag annoté :

```
commit visé sur GitHub : eae70369
commit attendu         : eae70369
```

Puis la release, sans incident d'encodage cette fois (note passée par fichier, `PYTHONIOENCODING=utf-8`) :

```
=== Barrière : verifier_tout.py ===   Barrière franchie
=== Barrière : banc_sante.py ===      Barrière franchie
poids mort ÉCARTÉ du zip : 31 fichier(s), 108.9 Mo
compilation Lua 5.1 de 53 fichier(s) du zip...
garde-fous : TOUT PROPRE
Création de la release v3.4.1...
https://github.com/LePetitDan/AscensionFR/releases/tag/v3.4.1
### CODE RETOUR = 0
```

#### 🛑 Une surprise, et il faut la dire : l'empreinte du zip **a changé**

Le programme demande de recalculer les deux empreintes avant d'envoyer. Je l'ai fait, elles
étaient identiques. **Puis `publier_github.py` a reconstruit le zip** — et l'empreinte du fichier
réellement publié n'est plus celle que j'avais vérifiée :

| | |
|---|---|
| vérifiée avant envoi | `92e79b7e…3be80e8f` |
| réellement publiée | `bc1b5aa3…9bb0b00a` |

**Je ne me suis pas contenté de supposer que c'était bénin.** J'ai comparé les deux archives
entrée par entrée :

```
entrées : vérifié=58  publié=58        noms différents : aucun
fichiers dont le CONTENU diffère : 0
fichiers dont seule la DATE d'archive diffère : 1
   LISEZ-MOI.txt  (2026,8,1,17,34,34) -> (2026,8,1,22,9,12)
```

**Zéro différence de contenu.** L'écart vient d'un seul horodatage, celui du `LISEZ-MOI.txt`
régénéré à la construction. Tailles identiques à l'octet près. Rien de grave — mais **la
consigne « recalcule l'empreinte du zip avant d'envoyer » ne peut structurellement pas
fonctionner**, puisque le publieur refait le zip après le contrôle. Pour la 3.5 : soit le
publieur réutilise le zip déjà construit, soit l'empreinte se prend *après* la construction.
L'exe, lui, n'est pas reconstruit : son empreinte tient de bout en bout.

---

### BLOC FINAL — vérifié depuis l'extérieur, sans me faire confiance

Aucune lecture de la page `/releases` (rendue en JavaScript) : uniquement l'API, `raw` et le
lien de téléchargement public.

| contrôle | résultat |
|---|---|
| `/releases/latest` | **`tag=v3.4.1`**, `prerelease=false`, `draft=false`, publié `2026-08-01T20:10:01Z` |
| assets de `v3.4.1` | `AscensionFR_Compagnon.exe` **37 932 935 o** · `AscensionFR_manuel.zip` **28 243 105 o** — noms et tailles exacts |
| `raw…/v3.4.1/compagnon/compagnon.py` | ligne 65 `VERSION_COMPAGNON = "3.4.1"` · ligne 72 `WEBHOOK_RAPPORTS = ""` ✅ |
| `v3.3.0` / `v3.3.1` / `v3.4.0` | **leurs deux assets chacune, intacts** |

**Et le vrai test — l'exe téléchargé depuis le lien public :**

```
  taille           : 37 932 935 o
  empreinte reçue  : a63c717bc071caa10ecf896684bcc649583dcd7ed14aaf5b084991780058f73c
  empreinte voulue : a63c717bc071caa10ecf896684bcc649583dcd7ed14aaf5b084991780058f73c
```

**Identiques.** Ce que les joueurs vont recevoir est exactement ce qui a été construit.

J'ai fait le même test sur le zip, puisque c'est le chemin recommandé aux joueurs dont
l'antivirus supprime l'exe : empreinte reçue = empreinte publiée, archive saine, 58 entrées, et
le `.toc` livré annonce bien **3.4.1**.

---

### Ce qui a résisté, et ce que j'ai failli casser

**Ce que j'ai failli casser — et c'est le même piège qu'au 29/07.**

Après la synchronisation et le commit, `verifier_arbre_publie.py` a dit **✅ code 0**. Le dépôt
public était pourtant à `[ahead 1]` : **commité, pas poussé.** Ce garde-fou lit
`git status --short`, qui rend une chaîne vide dans cet état — il m'a donné le feu vert alors
que GitHub ne connaissait pas encore le code 3.4.1.

Si j'avais enchaîné sur le tag à ce moment-là, **`v3.4.1` se serait posé sur le code 3.4.0**, et
le lien « code source ouvert » de la release aurait renvoyé à la mauvaise version. C'est
exactement l'incident du 29/07, rejoué.

**Ce n'est pas le garde-fou qui m'a sauvé, c'est la carte du programme 14.** Je savais que ce
contrôle est aveugle à cet état précis. J'ai donc poussé d'abord, puis posé le tag
explicitement sur un commit choisi, puis vérifié sur GitHub que le tag pointait bien là.
**Un garde-fou qui dit oui au mauvais moment est plus dangereux que pas de garde-fou** — celui-là
reste à réparer, et le correctif tient en une ligne (`git rev-list --count origin/main..main`).

**Ce qui a résisté, et qui a bien travaillé :**

- `verifier_arbre_publie.py` a **refusé deux fois** avant d'accepter : d'abord sur l'écart de
  version (public 3.4.0 / privé 3.4.1), puis sur les fichiers non commités. Les deux refus
  étaient justes, et je n'en ai contourné aucun ;
- les **trois garde-fous corrigés** ont mordu sur les 7 épreuves — **et sont redevenus verts**
  quand j'ai retiré la faute ;
- les deux barrières internes de `publier_github.py` (`verifier_tout`, `banc_sante`) ont été
  franchies pour de vrai, pas sautées ;
- le piège d'encodage de la 3.4.0 **ne s'est pas reproduit** : note passée par fichier UTF-8 et
  `PYTHONIOENCODING=utf-8`, plutôt qu'un titre recomposé au jugé.

**Deux décisions que j'ai prises seul, et que tu dois connaître :**

1. **Le plancher du banc moteur est à 10 000** (population réelle ≈ 49 000). C'est un arbitrage,
   pas une mesure.
2. **J'ai choisi de NE PAS faire bloquer** « À DÉCOUPER PLUS FIN » (base à ≥ 80 % de la limite)
   ni les échecs réseau autres qu'un 401. Une base à 85 % fonctionne, et une coupure de wifi ne
   dit rien du webhook — les faire bloquer aurait pu arrêter cette publication pour rien, et
   c'est ainsi qu'un garde-fou finit désactivé.

---

### 🛑 Terminé — l'état exact

| demandé | fait |
|---|---|
| les 3 garde-fous corrigés, **vus refuser** | ✅ 7 épreuves, dont le retour au vert |
| banc complet relancé après correction | ✅ **0 ROUGE** |
| ce que racontent les bancs endormis | ✅ 12 × « 0 échec » ; `banc_double_essai` exige un argument ; `verifier_arbre_publie` refusait à juste titre |
| empreintes recalculées avant envoi | ✅ identiques — **et l'écart du zip après reconstruction expliqué et prouvé bénin** |
| noms d'assets confirmés identiques | ✅ release / Hub / publieur : les trois |
| garde-fous passés sans contournement | ✅ aucun affaibli, aucun sauté |
| tag `v3.4.1`, release en ligne, `latest` à jour | ✅ tag sur `eae7036`, vérifié sur GitHub |
| vérification externe, empreinte de l'exe téléchargé | ✅ `a63c717b…` **identique** |

**Ce que je n'ai PAS fait, parce que ce programme ne le demande pas :** l'annonce Discord.
Le rituel (résumé bref + `@everyone` dans #annonces, détail dans #patch-note) reste à faire, et
**aucun texte n'existe pour la 3.4** — `discord/v3/` s'arrête à la 3.3. C'est un envoi
irréversible qui ping tout le serveur : il attend ton feu vert et un texte.
