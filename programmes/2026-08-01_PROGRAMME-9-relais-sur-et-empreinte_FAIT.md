# Demande de code → Claude Code

# 🛠️ PROGRAMME 9 — un relais qui ne peut pas perdre le Compagnon

**Date :** 2026-08-01
**Suite du PROGRAMME 8** (enquête). Dan a tranché : **pistes 1 et 2, maintenant.**

Ce qui n'est **pas** dans ce programme, et qu'il ne faut pas faire :

- ❌ ne pas poster le message Discord — Dan le relit d'abord, il postera lui-même ;
- ❌ ne rien envoyer à VirusTotal — piste abandonnée ;
- ❌ ne pas toucher au `.spec` — `upx=True` est inopérant, il n'y a rien à y changer ;
- ❌ pas de nettoyage des `_MEI*`, pas de témoin de lancement — ce sont les pistes 3 et 4, elles
  attendent les réponses des joueurs.

---

## Ce qu'on répare, et pourquoi maintenant

`lancer_remplacement()` (`compagnon/compagnon.py`, l. 546) écrit ce relais :

```bat
:attente
timeout /t 1 /nobreak >nul
del "cible" 2>nul               <- l'ancien est SUPPRIMÉ d'abord
if exist "cible" goto attente
move /y "nouveau" "cible" >nul  <- code de retour IGNORÉ
timeout /t 4 /nobreak >nul
start "" "cible"                <- lancé sans vérifier qu'il existe
del "%~f0"                      <- le relais efface la seule trace
```

**Entre le `del` et le `move`, il n'existe aucun Compagnon sur la machine.** Si le `move` échoue —
antivirus qui tient le fichier neuf, disque plein, droits, chemin verrouillé — le joueur se
retrouve **sans Compagnon et sans message**, et le relais s'efface en emportant la trace.

Ce défaut ne dépend d'aucun antivirus. Il est là quelle que soit la cause de la panne DLL. C'est
pour ça qu'il passe avant l'enquête.

---

## BLOC A — le relais ne supprime plus rien avant d'être sûr

Réécris le `.bat` pour qu'**à aucun instant** il n'existe zéro Compagnon récupérable. L'ordre que
je vois — mais c'est ton métier, propose mieux si tu as mieux :

1. attendre le déverrouillage de l'exe (la boucle actuelle, mais **sans supprimer**) ;
2. **mettre l'ancien de côté** (`move` vers `.ancien`), pas le supprimer ;
3. mettre le nouveau en place ;
4. **tester le code de retour de chaque `move`** ;
5. vérifier que la cible **existe** avant de lancer ;
6. **si quoi que ce soit échoue → remettre l'ancien en place** et lancer l'ancien ;
7. ne supprimer le `.ancien` **qu'après** un remplacement réussi.

### Les points sur lesquels je veux ta vigilance

- **Détecter le déverrouillage sans supprimer.** La boucle actuelle se sert de `del` comme test de
  verrou — c'est ce qui crée la fenêtre de danger. Il faut un test qui ne détruit pas. Un
  `move` de l'exe vers lui-même échoue aussi tant qu'il est verrouillé, et est réversible.
  Vérifie ce que tu choisis, ne le déduis pas.
- **Le relais ne doit plus s'effacer en cas d'échec.** Aujourd'hui `del "%~f0"` supprime la seule
  trace. Laisse un petit journal texte à côté du Compagnon quand ça se passe mal, et n'efface le
  relais que sur le chemin qui a réussi.
- **Les chemins accentués.** L'encodage `mbcs` du `.bat` est déjà géré — ne le casse pas. Beaucoup
  de joueurs ont un nom d'utilisateur accentué (`<utilisateur>`, `Jérôme`…), et un `.bat` mal encodé
  échouerait exactement là où on essaie de fiabiliser.
- **Les 4 secondes d'attente restent.** Elles ne garantissent rien (le programme 8 l'a montré :
  si l'antivirus agit, c'est à l'écriture, pas à la lecture), mais les retirer maintenant serait
  changer deux choses à la fois. On y reviendra en piste 4.

---

## BLOC B — vérifier l'exe téléchargé avant de l'installer

Aujourd'hui **aucun contrôle d'intégrité** : une coupure réseau pendant le téléchargement produit
un exe tronqué, qu'on installe, qui ne démarre pas — et qui est rejoué à chaque mise à jour. C'est
un candidat sérieux pour la « mise à jour qui ne tient pas » des 2 joueurs du 27/07.

### 🛑 Le piège, et c'est le même qu'au programme 6

**Une empreinte calculée sur le fichier téléchargé, comparée à une empreinte calculée sur le même
fichier téléchargé, ne prouve rien.** C'est l'épreuve qui se valide toute seule. La référence doit
venir d'ailleurs que du fichier.

Donc, **avant d'écrire quoi que ce soit, va voir ce dont on dispose réellement** :

- l'API GitHub des *release assets* renvoie-t-elle une taille ? un `digest` ? Regarde ce que
  renvoie vraiment notre release, ne te fie pas à la doc.
- si un digest est disponible : c'est la référence, utilise-la.
- s'il n'y en a pas : **dis-le-moi**, et propose. La taille annoncée est déjà un filet contre le
  fichier tronqué. Et publier nous-mêmes un `.sha256` à côté de l'exe est possible — mais ça
  change le processus de publication, donc **tu ne le fais pas sans mon accord.**
- **contrôle minimal qui ne coûte rien :** le fichier téléchargé commence-t-il par `MZ` ? Un exe
  tronqué à zéro octet, ou une page d'erreur HTML servie à la place du binaire, se voit là
  immédiatement.

### Que fait-on quand la vérification échoue

**On n'installe pas**, et **on le dit au joueur** — en français lisible, pas un code d'erreur. Le
pire serait de refuser en silence : on recréerait la boucle qu'on essaie de casser. Le joueur doit
comprendre que le téléchargement s'est mal passé et qu'il peut réessayer.

---

## BLOC C — le prouver sans détruire une installation

Je ne veux pas de « ça devrait marcher ». Fabrique une installation jetable dans un dossier
temporaire — un faux exe, un faux « nouveau » — et **fais échouer le remplacement exprès** :

| scénario | ce que je veux voir |
|---|---|
| remplacement normal | le nouveau est en place, l'ancien nettoyé, le Compagnon lancé |
| le `move` échoue (cible verrouillée par un autre processus) | **l'ancien est toujours là et démarre** ; un journal existe |
| l'exe « téléchargé » est tronqué / vide | refus d'installer, message clair, **l'ancien intact** |
| chemin avec accents et espaces | tout ce qui précède fonctionne quand même |

**N'exécute aucun de ces essais sur ton vrai Compagnon.** Dossier temporaire, faux binaires.

---

## BLOC D — les deux copies du code

`grep` remonte `lancer_remplacement` dans **deux arbres** :

```
WorkFlow/compagnon/compagnon.py
WorkFlow/depot_github/compagnon/compagnon.py
```

Le second est le miroir public publié au programme 7. **Dis-moi comment ils sont tenus
synchronisés** — script, copie manuelle, autre — et assure-toi que la correction ne laisse pas les
deux versions diverger. Si la synchronisation est manuelle, c'est un défaut à signaler, pas à
corriger aujourd'hui.

Vérifie aussi les **trois appelants** (`compagnon.py` l. 2138, `interface_hub.py` l. 1339,
`interface_v2.py` l. 1406) : est-ce qu'ils supposent quelque chose de l'ancien comportement ?

---

## À ne pas oublier

- **`VERSION_COMPAGNON` = `.toc` = tag de release.** Si cette correction part en version, les
  trois bougent ensemble.
- **Ne construis rien pour publication.** Dan dit quand on publie.

---

**« Terminé » veut dire :**

> - Le nouveau relais, avec le raisonnement sur le test de verrou non destructif.
> - Le contrôle d'intégrité, **et ce que l'API GitHub nous donne réellement** comme référence.
> - Les quatre scénarios du BLOC C **exécutés**, avec leur sortie réelle collée.
> - L'état des deux copies du code, et des trois appelants.
> - Ce que tu as failli casser en route, s'il y a lieu.

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Puis renommer en `_FAIT.md`.)

---

### BLOC A — le relais

#### Ta proposition de test de verrou ne tient pas — et ce que la mesure a donné à la place

Tu m'as demandé de vérifier plutôt que de déduire. J'ai éprouvé les candidats sur un **vrai
processus en cours** (une copie de `python.exe` lancée, pas un fichier tenu ouvert — seul le
premier reproduit le cas du Compagnon) :

| test, **pendant** que le processus tourne | résultat |
|---|---|
| `del` / `os.remove` — *l'actuel* | échoue ✓ **mais détruit dès qu'il réussit** |
| **`move` de l'exe vers lui-même** — *ta proposition* | échoue… **et échoue AUSSI après la fermeture** |
| `rename` vers `.ancien` | **RÉUSSIT alors que l'exe tourne** ⚠️ |
| ouverture en écriture exclusive | échoue ✓ (et réussit après ✓) |

**Ta proposition est inutilisable** : `move` d'un fichier vers lui-même échoue dans les deux
états, il ne discrimine rien. J'ai aussi éprouvé la variante `.bat` par ouverture en ajout
(`2>nul ( >>"fichier" call )`) : elle répond « verrouillé » même après la fermeture. Écartée
aussi.

**Mais la troisième ligne change toute la conception.** Windows **autorise à renommer un
exécutable en cours** — il interdit seulement de le supprimer. Donc :

> **On peut mettre l'ancien de côté immédiatement, sans rien attendre et sans rien détruire.**
> Et supprimer le `.ancien` ne réussit que lorsque l'ancien processus a vraiment rendu la main :
> **l'attente et le nettoyage deviennent la même opération.** Il n'y a plus besoin d'aucun test
> de verrou.

C'est plus simple que ce que tu proposais, et ça tient parce que c'est mesuré.

#### Le nouveau relais

```bat
1. move CIBLE -> ANCIEN          (réussit même si l'appli tourne encore)
   if errorlevel 1 -> rien touché, journal, on relance l'ancien
2. move NOUVEAU -> CIBLE
   if errorlevel 1 -> RETOUR ARRIÈRE, journal, on relance l'ancien
   if not exist CIBLE -> idem
3. attente = suppression du .ancien, réessayée 30 fois
4. respiration 4 s (conservée telle quelle)
5. start CIBLE
6. del du relais — UNIQUEMENT sur le chemin qui a réussi
```

**À aucun instant il n'existe zéro Compagnon** : on renomme au lieu de supprimer, et le
`.ancien` reste là tant que le remplacement n'est pas acquis. Chaque `move` teste son code de
retour, l'existence de la cible est vérifiée avant le lancement, et le chemin d'échec **remet
l'ancien en place, le relance, et écrit un journal** à côté du Compagnon.

#### ⚠️ Ce que j'ai failli casser — et qui était déjà cassé

Le scénario « chemin accentué » du bloc C a échoué à mon premier jet. **Et en silence** : pas
même un journal, puisque le chemin du journal était lui aussi illisible.

La cause n'est pas mon relais : **un `.bat` est relu par cmd.exe dans la page de code OEM
(cp850 en France), alors que `mbcs` écrit en ANSI (cp1252).** Un « é » écrit d'un côté n'est pas
celui qu'on relit de l'autre. **L'ancien relais avait exactement le même défaut** — il était
juste invisible, parce qu'un `del` qui ne trouve pas sa cible ne dit rien.

Le correctif supprime le problème plutôt que de le contourner : **les chemins passent par
l'ENVIRONNEMENT**, cmd.exe les reçoit en natif, et **le `.bat` est désormais purement ASCII**.
Écrit en `encoding="ascii"` sans `errors="replace"` : si un jour un caractère non-ASCII s'y
glissait, ce serait un plantage franc, pas un « ? » silencieux.

C'est le troisième piège d'encodage de ce projet, après la console cp1252 et le `\b` collé.

---

### BLOC B — le contrôle d'intégrité

#### Ce que l'API GitHub donne réellement — j'ai regardé avant d'écrire

```
AscensionFR_Compagnon.exe
  digest : sha256:621401050e340da8bf3032a251e19e55bf6fea2c43cdc087666337a77d864d7b
  size   : 37927959
```

**Il y a un `digest`.** Et il correspond exactement à l'empreinte réelle de l'exe publié (je l'ai
recalculée : `621401050e34…d864d7b`, identique).

C'est la réponse à ton piège : **la référence vient des MÉTADONNÉES, servies par une autre
requête que celle du binaire.** On ne compare pas le fichier à lui-même. Pas besoin de publier un
`.sha256` à côté de l'exe — donc **rien à changer au processus de publication**, et je n'ai pas
eu à te demander l'accord que tu réservais pour ça.

#### Les trois contrôles, du moins cher au plus sûr

1. **en-tête `MZ`** — attrape le fichier vide et surtout la page d'erreur HTML servie à la place
   du binaire (un portail Wi-Fi captif, un proxy d'entreprise) ;
2. **la taille annoncée** — attrape le téléchargement tronqué ;
3. **l'empreinte SHA-256** — attrape le reste.

L'empreinte est calculée **au fil de l'eau**, pendant le téléchargement : on ne relit pas 38 Mo
une seconde fois. En cas d'échec, le fichier temporaire est **supprimé** — il ne doit pas rester
un exe corrompu qui traîne — et une exception au message lisible remonte à l'appelant.

**Si l'API ne répond pas**, `reference_asset` rend `(None, None)` et on n'empêche pas la mise à
jour pour autant : les contrôles de forme (vide, `MZ`) restent actifs. Un contrôle d'intégrité qui
bloquerait les mises à jour dès que GitHub tousse serait pire que le mal.

---

### BLOC C — les quatre scénarios, exécutés

Installation jetable dans un dossier temporaire, faux binaires. **Le vrai Compagnon n'a jamais
été touché.** Sortie réelle :

```
1. REMPLACEMENT NORMAL
  relais effacé (chemin de SUCCÈS)
  l'exe en place contient : LE NOUVEAU
  y a-t-il TOUJOURS un Compagnon ?  OUI
  .ancien résiduel : non
  journal écrit : aucun (normal si tout s'est bien passé)

2. LE « MOVE » ÉCHOUE (cible tenue par un autre processus)
  relais toujours là (chemin d'ÉCHEC ou attente)
  l'exe en place contient : L'ANCIEN
  y a-t-il TOUJOURS un Compagnon ?  OUI
  .ancien résiduel : non
  journal écrit : [01/08/2026 7:45:48] Mise a jour impossible : l'ancien
                  Compagnon n'a pas pu etre mis de cote. Rien n'a ete modifie.

3. LE TÉLÉCHARGEMENT EST TRONQUÉ / N'EST PAS UN EXE
  fichier vide (0 octet)                     REFUSÉ
     « le téléchargement est vide (0 octet). La connexion a probablement
       été interrompue — réessaie dans un instant. »
  page HTML servie à la place du binaire     REFUSÉ
     « le fichier téléchargé n'est pas un programme Windows. Le
       téléchargement a été interrompu, ou un équipement réseau a renvoyé
       une page d'erreur à la place — réessaie dans un instant. »
  exe tronqué (taille annoncée plus grande)  REFUSÉ
     « le téléchargement est incomplet (0.0 Mo reçus sur 37.9 Mo
       attendus). Réessaie dans un instant. »
  exe complet mais empreinte fausse          REFUSÉ
     « le fichier téléchargé est abîmé (son empreinte ne correspond pas à
       celle annoncée par GitHub). Réessaie dans un instant ; si ça
       recommence, télécharge-le à la main depuis la page des versions. »
  exe conforme                               ACCEPTÉ

4. CHEMIN AVEC ACCENTS ET ESPACES  (« Dossier de Jérôme — Compagnon »)
  relais effacé (chemin de SUCCÈS)
  l'exe en place contient : LE NOUVEAU
  y a-t-il TOUJOURS un Compagnon ?  OUI
  .ancien résiduel : non
```

**Dans les quatre cas, la réponse à « y a-t-il toujours un Compagnon ? » est OUI.** C'était
l'objet du programme.

---

### BLOC D — les deux copies et les trois appelants

#### Comment elles sont tenues synchronisées : par un OUTIL, pas à la main

C'est `outils/synchroniser_depot_public.py`, posé au programme 6. Il couvre les cinq sources qui
construisent l'exe, dont les deux que je viens de modifier. Lancé à l'instant :

```
  compagnon/compagnon.py         À METTRE À JOUR  (1 secret(s) neutralisé(s))
  compagnon/interface_hub.py     À METTRE À JOUR
  compagnon/compagnon_hub.py     identique
  compagnon/fabriquer_decor_hub.py  identique
  compagnon/AscensionFR_Hub.spec identique
```

**Et la divergence est impubliable**, pas seulement détectable — le garde-fou du programme 9…
pardon, du geste 9 du programme 7, refuse déjà :

```
🛑 REFUS DE TAGUER — 2 point(s) :
   - compagnon/compagnon.py diverge du privé neutralisé
   - compagnon/interface_hub.py diverge du privé neutralisé
```

**Je n'ai donc pas synchronisé.** La synchronisation est le geste 1 de la séquence de
publication, elle t'appartient. En attendant, il n'y a aucun risque de divergence livrée : rien
ne peut partir tant que les deux arbres ne coïncident pas.

#### Les trois appelants — et un quatrième problème trouvé chez l'un d'eux

| appelant | état |
|---|---|
| `compagnon.py:2138` (`_redemarrer_avec`) | référence d'intégrité branchée ✓ |
| `interface_hub.py:1339` (`_remplacer_appli`) | branchée ✓ **+ correction, voir ci-dessous** |
| `interface_v2.py:1406` | branchée ✓ |

Aucun ne supposait quoi que ce soit de l'ancien comportement : tous les trois appellent
`lancer_remplacement(nouveau, sys.executable)` puis ferment la fenêtre. Le relais rend désormais
le chemin du `.bat` (utile au banc) ; ils l'ignorent, sans conséquence.

**Mais le Hub avalait le message d'erreur :**

```python
except Exception:
    self.statut("erreur", "Téléchargement impossible. Réessaie plus tard.")
```

Le même texte quelle que soit la cause. Or « ta connexion a coupé » et « le fichier est abîmé »
n'appellent pas le même geste, et c'est exactement le refus silencieux que tu voulais éviter au
bloc B. Il dit maintenant pourquoi.

---

### Bilan

| ce que « terminé » demandait | résultat |
|---|---|
| Le nouveau relais + le raisonnement sur le test de verrou | ✅ ta proposition **éprouvée et écartée** ; la mesure (« renommer un exe en cours est permis ») a rendu le test inutile |
| Le contrôle d'intégrité + ce que l'API donne | ✅ **`digest` sha256 + `size`** disponibles — référence externe, pas d'auto-validation, **pas de changement au processus de publication** |
| Les quatre scénarios exécutés, sortie collée | ✅ les quatre, **« y a-t-il toujours un Compagnon ? » = OUI** partout |
| L'état des deux copies et des trois appelants | ✅ outil de synchronisation, divergence **impubliable** ; 3 appelants branchés, 1 refus silencieux corrigé au passage |
| Ce que j'ai failli casser | ✅ ci-dessous |

**Ce que j'ai failli casser, et qui était déjà cassé :** mon premier relais échouait sur les
chemins accentués, en silence. Le banc l'a attrapé — pas la relecture. La cause (`.bat` lu en
OEM, écrit en ANSI) **affectait déjà l'ancien relais** : un joueur nommé « Jérôme » n'a
peut-être jamais réussi une seule mise à jour automatique, et ça n'a jamais produit le moindre
message. Corrigé en supprimant la question : plus aucun caractère non-ASCII dans le `.bat`.

**Ce qui n'a pas été fait, comme demandé :** rien de posté sur Discord, rien envoyé à
VirusTotal, `.spec` non touché, pas de nettoyage des `_MEI*`, pas de témoin de lancement, **rien
construit pour publication**, dépôt public non synchronisé.

**Une note pour la suite :** `VERSION_COMPAGNON` reste à `3.4.0`. Si cette correction part en
version, les trois numéros bougent ensemble — et `verifier_tout.py` refusera si ce n'est pas le
cas.
