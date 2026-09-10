# Demande de code → Claude Code

# 🔇 PROGRAMME 23 — le Hub qui plante en silence

**Date :** 2026-08-02

Tetardtek a éprouvé le binaire Linux du programme 21, pour de vrai, en cliquant. Il a trouvé
deux boutons cassés — et surtout **quelque chose de plus grave que les deux boutons.**

🛑 **Ce programme répare et éprouve. Il ne publie pas.** Pas de tag, pas de release, pas d'asset
remplacé. Dan décidera de la sortie avec ton rapport sous les yeux.

---

## 🛑 BLOC 0 — le vrai sujet : le joueur ne voit rien

> *« Ton binaire n'a pas de console. Je n'ai vu les erreurs qu'en le lançant depuis un terminal.
> Pour un joueur qui double-clique, il ne se passe rien du tout — pas de message, pas de piste.
> C'est le pire cas pour ton support. »*

Il a raison, et c'est la famille de défauts qu'on répare depuis une semaine : **l'échec muet.**
La mise à jour qui ne marchait pas sans dire pourquoi, le relais qui effaçait sa propre trace,
les trois garde-fous qui affichaient vert sans mesurer. Même maladie.

**Ce que je veux savoir avant que tu répares quoi que ce soit :**

1. **Que se passe-t-il aujourd'hui quand le Hub lève une erreur non rattrapée ?** Sous Linux
   (pas de console), et **sous Windows** — je soupçonne que le joueur Windows ne voit rien non
   plus, et alors ça touche tout le monde. **Mesure-le, ne le suppose pas.**
2. **Où pourrait aller une trace ?** Un fichier journal à côté du programme, dans le dossier de
   configuration, ailleurs ? Regarde ce que le projet fait déjà — il existe peut-être un endroit
   pour ça, et un deuxième mécanisme serait pire qu'aucun.
3. ⚠️ **Une trace ne doit jamais porter le webhook, ni un pseudonyme de joueur, ni un chemin
   inutile.** Un journal d'erreur finit sur le Discord, collé par un joueur qui veut aider.
   **Écris-le en partant de là.**

**Puis répare :** qu'un plantage soit **visible** pour quelqu'un qui a double-cliqué. Une fenêtre
qui dit « ça a raté, voilà où c'est écrit », pas un terminal. Et le texte en français simple —
c'est un joueur qui le lit, pas un développeur.

---

## BLOC A — les deux boutons, et surtout leurs frères

Tetardtek donne les lignes exactes :

| bouton | erreur | où |
|---|---|---|
| **Lancer le jeu** | `ModuleNotFoundError: No module named 'winreg'` | `interface_hub.py:485`, dans `_candidats_registre()` |
| **Vérifier mon installation** | `_tkinter.TclError: grab failed: window not viewable` | `interface_hub.py:1895` — `grab_set()` appelé sur un `Toplevel` avant que le gestionnaire de fenêtres X11 l'ait affiché |

Les deux sont de petites gardes manquantes. **Répare-les.**

🛑 **Mais ne t'arrête surtout pas là.** Il a trouvé ces deux-là **en cliquant sur deux boutons.**
La question qui compte est : **combien y a-t-il de boutons ?**

- **balaye tout `interface_hub.py`** (et ce qu'il appelle) à la recherche de tout ce qui n'existe
  que sous Windows : `winreg`, `os.startfile`, `subprocess` avec des commandes Windows, des
  chemins `C:\`, `%APPDATA%`, `.exe`, `shell32`, `ctypes.windll`… **fais-en la liste complète**,
  gardé ou non ;
- **même chose pour les pièges de fenêtre** : chaque `grab_set`, `transient`, `iconbitmap`,
  `attributes('-toolwindow')` et cousins. Ce qui marche sous Windows ne marche pas forcément
  sous X11 ;
- **dis-moi combien tu en as trouvé, et combien étaient déjà gardés.** Ce chiffre m'intéresse
  plus que les deux corrections.

Le fichier a déjà une manière de gérer le cas Windows quelque part — Tetardtek le note :
« l'import n'a pas de garde de plateforme, contrairement à d'autres endroits du même fichier ».
**Reprends la manière existante, n'en invente pas une deuxième.**

---

## BLOC B — le bouton fantôme

`interface_hub.py:2379`, quand un envoi de rapport échoue, affiche :

> « Tu peux aussi copier le rapport **(bouton ci-dessous)** et le coller sur le Discord. »

**Ce bouton n'existe pas dans le Hub.** Et le code enchaîne sur `copier_diagnostic`, qui met le
**relevé d'installation** dans le presse-papier — pas le rapport. Un joueur qui suit l'instruction
colle la mauvaise chose sur le Discord, en croyant bien faire.

Tu l'as établi toi-même au bloc E du programme 17. **Ça touche tous les joueurs, pas seulement
Linux** : c'est le chemin d'échec réseau de n'importe qui.

**Répare :** repose le bouton « Copier mon rapport ». La fonction existe déjà
(`compagnon.py:2405`) et le Hub importe `compagnon` comme `logique` — c'est un bouton à poser,
pas une fonctionnalité à écrire. **Et vérifie que le message et le bouton disent la même chose**
une fois les deux en place.

---

## 🛑 BLOC C — la preuve, et je sais qu'elle est difficile

Tu n'as pas de Linux sous la main : tu l'as découvert au programme 21. **Ne fais pas semblant.**

- construis, et **exerce les deux chemins qui plantaient** dans le run GitHub — pas seulement le
  démarrage. Si tu ne peux pas cliquer, appelle les fonctions ;
- **provoque un vrai plantage exprès** et montre que le joueur le voit maintenant : la fenêtre,
  et le fichier de trace avec son contenu ;
- **sous Windows, prouve que rien n'a régressé.** C'est le côté où il y a 274 personnes. Les deux
  boutons doivent marcher exactement comme avant.

Et dis-moi franchement ce que tu **n'as pas** pu éprouver. Tetardtek est disponible et il teste
sérieusement — s'il reste un trou, c'est lui qui le bouchera, et il vaut mieux le nommer que le
maquiller.

---

## BLOC D — ce que ça coûte à sortir, pour que Dan décide

Tout ça touche `interface_hub.py`, **l'un des 5 fichiers surveillés**. Donc une sortie veut dire
reconstruire, et une nouvelle version que **les 274 Hubs Windows proposeront**.

**Je ne te demande pas de publier. Je te demande de chiffrer :**

- qu'est-ce qui change **pour un joueur Windows** ? (le bouton fantôme, l'échec visible — quoi
  d'autre ?)
- est-ce que ça justifie une version pour tout le monde, ou est-ce qu'on peut ne remplacer que
  le binaire Linux attaché à la `v3.4.1` ?
- **ton avis, et pourquoi.**

🛑 **Aucun tag, aucune release, aucun asset remplacé dans ce programme.**

---

**« Terminé » veut dire :**

> - Ce que voit un joueur aujourd'hui quand ça plante, **sous Linux ET sous Windows**, mesuré.
> - Un plantage **visible** pour quelqu'un qui a double-cliqué, et une trace **sans secret, sans
>   pseudonyme, sans chemin inutile**.
> - Les deux boutons réparés — **et la liste complète de leurs frères**, avec le compte.
> - Le bouton fantôme reposé, et le message qui dit enfin la vérité.
> - Un plantage provoqué exprès, **et le joueur qui le voit**.
> - Windows non régressé, prouvé.
> - Ce qui reste non éprouvé, dit franchement.
> - Ton chiffrage pour la sortie, et ton avis.
> - Ce qui a résisté, et ce que tu as failli casser.

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Puis renommer en `_FAIT.md`.)

---

# 🛑 BLOC 0 — le vrai sujet : le joueur ne voit rien

## 1. Que se passe-t-il aujourd'hui ? — **mesuré, pas supposé**

Je n'ai pas lu le code pour deviner : j'ai **construit une sonde** — une petite application
tkinter avec la forme exacte du Hub (une fenêtre, un bouton dont le rappel lève), figée par
PyInstaller avec **les mêmes réglages que le Hub** (`--onefile --windowed`, donc
`console=False`, `disable_windowed_traceback=False`). Puis je l'ai lancée et j'ai **énuméré
les fenêtres réellement ouvertes par le processus** (`EnumWindows` + classe + titre) —
une mesure reproductible, pas un coup d'œil.

> Piège rencontré en route, il vaut d'être noté : en mode `--onefile`, le lanceur PyInstaller
> **relance l'application dans un processus FILS**. Énumérer les fenêtres du PID rendu par
> `Popen` ne montre donc rien du tout. Ma première mesure disait « aucune fenêtre » — elle
> était fausse. Il faut suivre l'arbre de processus.

### Windows — deux cas très différents, et le pire est le plus fréquent

| ce qui plante | ce que le joueur voit | code de sortie |
|---|---|---|
| **une erreur dans un rappel de bouton** (les deux défauts de Tetardtek) | **RIEN. Absolument rien.** La fenêtre reste là, le bouton ne fait rien, et l'application se ferme normalement quand on la ferme. | **0** |
| une erreur **avant** la boucle (démarrage, décor manquant…) | une boîte Windows `#32770` titrée **« Unhandled exception in script »**, en anglais, avec le traceback Python brut | bloquée jusqu'au clic |

Relevé de la sonde, verbatim :

```
gelé (PyInstaller)     : True
sys.stdout             : None
sys.stderr             : None
sys.__stderr__         : None
print(file=sys.stderr) : n'a PAS levé
traceback.print_exc()  : n'a PAS levé (donc muet)
--- mainloop ---
--- le rappel va lever ---
--- mainloop rendue : l'application se ferme NORMALEMENT, comme si de rien n'était ---
```

Fenêtres relevées pendant l'essai « rappel » :
`PyInstallerOnefileHiddenWindow` (invisible), `IME`, `TtkMonitorClass`, `MSCTFIME UI`,
et **`TkTopLevel 'Sonde'`** — la fenêtre du Hub. **Aucune boîte de dialogue.**
Pendant l'essai « construction », une sixième apparaît :
`#32770 'Unhandled exception in script'`.

**La chaîne exacte, et pourquoi c'est silencieux :** dans un exe `--windowed`, Python démarre
avec `sys.stdout` **et** `sys.stderr` à `None`. Tkinter attrape toute exception de rappel dans
`Tk.report_callback_exception`, qui fait `print(..., file=sys.stderr)` puis
`traceback.print_exception(...)`. Avec `sys.stderr = None`, `print` retombe sur `sys.stdout`,
lui aussi `None`, et **rend la main sans rien écrire ni rien lever**. L'exception est mangée
proprement. Le garde-fou de PyInstaller (`disable_windowed_traceback=False`) ne sert à rien
ici : il ne se déclenche que pour une exception **non rattrapée au niveau supérieur** — or
Tkinter les rattrape toutes.

> ⚠️ **Donc oui, ça touche les 274 joueurs Windows, pas seulement Linux.** Tu le soupçonnais,
> c'est vérifié. Tout bouton du Hub qui lève aujourd'hui ne fait **rien**, sans un mot.

### Linux — pas de boîte du tout, à aucun moment

La documentation de PyInstaller le dit dans son propre code
(`PyInstaller/building/api.py`, description de `disable_windowed_traceback`) :

> « Disable traceback dump of unhandled exception in windowed (noconsole) mode
> **(Windows and macOS only)** »

Sous Linux, `--windowed` ne fait rien : `sys.stderr` reste le descripteur hérité du parent.
D'où exactement ce que Tetardtek a vécu — **depuis un terminal on voit le traceback ; en
double-cliquant depuis le gestionnaire de fichiers, il part dans le journal de session et le
joueur ne voit rien.** Et pour le cas « erreur au démarrage », Linux n'a **même pas** la boîte
de secours que Windows a.

*(Mesure Linux à confirmer sur le coureur — voir bloc C. Je ne la donne pas pour faite.)*

## 2. Où va la trace ? — **l'endroit existait déjà**

Tu avais raison de me faire regarder avant d'inventer. Le projet a **déjà** un endroit
pour « quelque chose a raté » : le relais de mise à jour du programme 9 écrit
`AscensionFR_maj_echec.log` **à côté du programme**, en lignes `[date heure] message`
(`compagnon.py`, `lancer_remplacement`). C'est là que va la trace d'incident, sous le
nom `AscensionFR_incident.log`, au même format — pas un deuxième mécanisme, le même.

Repli : si le dossier du programme n'est pas inscriptible (Program Files, `/opt`, une clé
en lecture seule), on retombe sur le dossier de configuration. `dossier_journal()` **essaie
d'écrire pour de vrai** avant de choisir — il ne suppose pas les droits.

> ⚠️ **Défaut trouvé en chemin, et réparé.** `CONFIG_DIR` valait
> `os.environ.get("APPDATA", ".")` : sous Linux, `%APPDATA%` n'existe pas, donc **le repli
> était `"."` — le dossier COURANT**. Un joueur Linux qui choisissait son dossier de jeu le
> reperdait au lancement suivant si le programme n'était pas lancé du même endroit, et une
> trace écrite là aurait été introuvable. `_dossier_config()` suit maintenant la convention
> du système (`~/.config/AscensionFR`). **Sous Windows la valeur est identique au caractère
> près** — c'est une épreuve du banc, pas une promesse.

## 3. Ce que la trace ne porte JAMAIS — écrit en partant de là

`_anonymiser()` passe sur tout ce qui est écrit, et un banc l'éprouve
(`outils/banc_incident.py` — **10 épreuves, 29 affirmations, toutes vertes**) :

| ce qui est retiré | pourquoi |
|---|---|
| le **webhook des rapports** | une autorisation d'écriture à porteur. Il peut arriver dans une trace par une `URLError`, un `unknown url type`, ou une ligne de code citée. |
| **tout autre webhook Discord** | même s'il n'est pas le nôtre |
| le **nom de compte WoW** (`…\WTF\Account\XXX\…`) | c'est un identifiant de joueur — il arrive dans toute trace venant de la lecture des sauvegardes |
| le **dossier personnel** et le **nom d'utilisateur seul** | `C:\Users\<utilisateur>\…`, mais aussi `KeyError: 'Jerome'` |
| le **dossier temporaire du paquet** (`sys._MEIPASS`) | il contient le nom de session |

Ce qui **reste**, parce que c'est tout l'intérêt : la date, la version du Hub, le système,
le geste du joueur (« Lancer le jeu »), et le traceback technique — nom de fonction, numéro
de ligne, type d'erreur. Le banc vérifie explicitement que ces morceaux-là survivent.

Deux détails que j'ai payés ailleurs et qui servent ici : le remplacement va **du plus long
au plus court** (sinon un remplacement court coupe un chemin en deux et le suivant ne
reconnaît plus rien), et **aucun `\b`** dans les motifs — après un souligné il ne voit pas
de frontière et rate en silence (le piège du programme 6).

## 4. La réparation : trois portes, parce qu'il y a trois endroits où ça peut lever

| porte | ce qu'elle attrape | avant |
|---|---|---|
| `Hub.report_callback_exception` | **tous les boutons** | écrivait dans `sys.stderr` = `None` |
| `threading.excepthook` | les tâches de fond (`self._fil`) — 15 lancements | disparaissait encore plus complètement |
| `sys.excepthook` | le démarrage, et tout le reste | boîte anglaise sous Windows, rien sous Linux |

Les trois aboutissent à `montrer_plantage()` : **une fenêtre**, en français simple, qui dit
ce qui s'est passé, que rien n'est cassé dans le jeu, **où c'est écrit**, et qui propose
« Copier le détail » pour le Discord. Le relevé est copiable dans la fenêtre (règle de la
maison : jamais un `print`, toujours du copiable).

Trois choix qui méritent d'être dits :

- **la fenêtre de plantage ne fait PAS `grab_set()`** — c'est précisément le piège du bloc A,
  et une fenêtre d'erreur qui refuse de s'ouvrir sous X11 serait le comble ;
- **une seule fenêtre à la fois** (`_PLANTAGE_OUVERT`) : un rappel qui lève à chaque
  mouvement de souris n'empile pas 500 fenêtres ;
- **le journal est plafonné à 200 ko** : une boucle de plantages ne remplit pas le disque du
  joueur. Et `journal_incident()` **ne lève jamais** — même quand le disque refuse, elle rend
  `None` (éprouvé en lui donnant un dossier qui lève).

Le nom du geste vient d'un seul endroit : `BoutonImage._relache` note le bouton cliqué, et
`_lien_texte` note le libellé du lien. La fenêtre peut donc dire **« c'est arrivé pendant :
Lancer le jeu »** au lieu de « une action du Hub ».

---

# 🚨 AJOUT URGENT — le Hub Linux qui allait avaler un .exe Windows

**J'ai refait la chaîne moi-même, maillon par maillon. Elle est exacte.** Et je l'ai éprouvée
plutôt que relue : `outils/banc_maj_plateforme.py` — **13 affirmations, toutes vertes.**

Le banc **prouve d'abord que le défaut existait** : avec une release qui ne porte que les deux
assets Windows, `derniere_release()` rend bien `url_exe = .../AscensionFR_Compagnon.exe` — il
n'y a aucune notion de plateforme nulle part.

Un point que tu n'avais pas et qui aggrave le diagnostic : **ça ne ratait que par chance.**
`lancer_remplacement` finit par `subprocess.Popen(..., creationflags=0x08000000)`, et
`creationflags` lève un `ValueError` hors Windows. C'est ce hasard-là — pas une garde — qui
empêchait le relais de `move` un .exe Windows par-dessus le binaire Linux du joueur, **le
laissant sans Hub du tout**. Exactement le défaut que le programme 9 a réparé. La chance
n'est pas un garde-fou.

### La désamorce, en trois barrières

| # | où | ce qu'elle fait |
|---|---|---|
| 1 | `Hub._maj_appli_proposable()` | **le lien n'apparaît pas** hors Windows — le joueur ne se voit rien proposer |
| 2 | `Hub.mettre_a_jour_appli()` | au bord de l'action : ouvre la page des versions et le dit, au lieu de télécharger |
| 3 | `logique.lancer_remplacement()` | **refuse net** (`RuntimeError`) avant d'écrire quoi que ce soit |

La vérité tient dans **une seule fonction nommée**, `logique.remplacement_possible()`, posée
juste à côté du relais qu'elle décrit. La règle d'affichage est devenue une méthode **sans
état** (`_maj_appli_proposable`) exprès : le banc l'éprouve **sans ouvrir de fenêtre**.

### Sous Windows, rien ne bouge — et c'est éprouvé, pas affirmé

Le banc rejoue les trois règles d'avant : caché quand l'appli est à jour, caché sans asset,
caché hors de la vue Traduction — et **proposé** dans le cas nominal.

### Où la PR de Tetardtek devra se brancher (pour qu'on ne se marche pas dessus)

Je **n'ai pas touché** au choix de l'asset. Les trois points de couture, dans l'ordre :

1. **`compagnon.derniere_release()`** — c'est le seul endroit qui apparie les noms d'assets
   (`ZIP_ATTENDU`, `EXE_ATTENDU`). C'est là que doit naître le choix par plateforme.
2. **`compagnon.reference_asset(nom_asset)`** — le contrôle d'intégrité interroge l'API par
   **nom d'asset**. Il devra recevoir le même nom que celui qui a été choisi, sinon il
   validera l'empreinte du mauvais fichier. *(Point facile à rater : les deux fonctions
   choisissent l'asset séparément aujourd'hui.)*
3. **`compagnon.verifier_telechargement()`** — le contrôle de forme teste l'en-tête `MZ`
   quand le suffixe est `.exe`. Un ELF Linux commence par `\x7fELF` : il faudra une famille
   de plus, pas un contournement.

Et **`remplacement_possible()` est le point d'élargissement** : quand un vrai relais Linux
existera, c'est cette fonction-là qui dira oui — pas l'interface. Les trois barrières
s'ouvriront ensemble, ou aucune.

⚠️ **Ma garde n°3 (`lancer_remplacement` refuse hors Windows) devra être levée en même temps
que son relais Linux sera écrit.** C'est la seule ligne de mon travail qui entrera en
conflit avec sa PR. Je la signale plutôt que de la cacher.

---

# BLOC A — les deux boutons, et surtout leurs frères

## Les deux, réparés

| bouton | ce qui manquait | ce que j'ai posé |
|---|---|---|
| **Lancer le jeu** | `import winreg` nu dans `_candidats_registre()` | `try: import winreg / except ImportError: return []` — **la manière existante**, celle de `compagnon._pistes_launcher` (l. 316-347 d'origine), pas une deuxième |
| **Vérifier mon installation** | `grab_set()` sur un `Toplevel` que X11 n'a pas encore affiché | l'essai **immédiat** est gardé (sous Windows il réussit, exactement comme avant), et **seul l'échec** déclenche une reprise toutes les 50 ms pendant ~1 s, puis on abandonne **sans bruit** — une fenêtre sans grab reste utilisable, une `TclError` tue le bouton |

Un troisième défaut sortait du même trou et n'était pas dans ta liste : `os.startfile` — qui
**n'existe pas** hors Windows — était appelé sous `except OSError`, qui ne rattrape pas un
`AttributeError`. Le bouton « Lancer le jeu » avait donc **deux** raisons de ne rien faire.

## Le compte que tu voulais — mesuré par un outil, pas à l'œil

J'ai écrit `outils/balayer_windows.py` plutôt que de compter à la main : un compte manuel
n'est pas reproductible et ne mordra plus jamais. Il lit l'**arbre syntaxique**, remonte les
`try/except` qui entourent réellement chaque appel, et **compare le type attrapé au type qui
serait levé** hors Windows :

| ce qu'on écrit | ce que ça lève hors Windows |
|---|---|
| `import winreg` | `ModuleNotFoundError` |
| `ctypes.windll.…`, `os.startfile(…)` | `AttributeError` |
| `creationflags=…` | `ValueError` |
| `grab_set()`, `iconbitmap()` | `TclError` |

**Un `except OSError` ne garde aucun des quatre.** C'est exactement pourquoi « Lancer le
jeu » était dans un `try` et plantait quand même.

Il connaît aussi la **seconde** manière de garder du projet — une fonction qui commence par
« si on n'est pas sous Windows, on s'arrête » (`hasattr(os, "startfile")`,
`remplacement_possible()`). Le détecteur est **volontairement strict** : tout ce qu'il ne
reconnaît pas nommément compte comme non gardé. Un balayage complaisant serait le défaut
qu'on soigne.

### Le chiffre

```
AVANT (git HEAD)      25 endroits supposent Windows
                      17 peuvent LEVER  ->  10 gardés,  7 NON GARDÉS
                       8 ne lèvent pas mais dégradent

APRÈS                 23 endroits supposent Windows
                      18 peuvent LEVER  ->  18 gardés,  0 non gardé
                       5 ne lèvent pas mais dégradent (tous relus, tous corrects)
```

**7 endroits pouvaient planter. Tetardtek en avait trouvé 2 en cliquant sur 2 boutons.**

### Les 7, nommément

| # | où | ce qui se passait |
|---|---|---|
| 1 | `interface_hub.py:485` `_candidats_registre` | `import winreg` nu → **son défaut n°1** |
| 2 | `interface_hub.py:797` `lancer_jeu` | `os.startfile` sous `except OSError` |
| 3 | `interface_hub.py:806` `lancer_jeu` | idem, le chemin de secours |
| 4 | `interface_hub.py:1895` `_fenetre` | `grab_set()` → **son défaut n°2** |
| 5 | `compagnon.py:2291` `_relancer_admin` | `ctypes.windll` sans aucun `try` |
| 6 | `compagnon.py:756` `lancer_remplacement` | `creationflags=` → `ValueError` |
| 7 | `compagnon.py:756` `lancer_remplacement` | `subprocess(["cmd", …])` |

Les n°6 et 7 sont **la chaîne de l'ajout urgent** : c'est par elles que le défaut de la mise
à jour ratait *par chance*. Le n°5 vit dans l'ancienne interface v2, que le Hub n'instancie
plus — mais elle est dans un fichier surveillé, et un `except` coûtait une ligne.

### Les 8 qui dégradaient sans lever — dont 3 méchants

Les 5 lectures de `%APPDATA%` / `%LOCALAPPDATA%` sont **toutes correctes** : je les ai
relues une par une, chacune est suivie d'un `if not base: continue` ou d'un `if
os.environ.get(...)`. Elles rendent simplement moins de pistes hors Windows, ce qui est
honnête. *(Sauf une, `CONFIG_DIR`, dont le défaut `"."` était faux — voir bloc 0.)*

Les **3 autres sont le vrai piège de fenêtre**, et personne ne les aurait vues :

> `bind("<MouseWheel>")` — sous X11 la molette n'est **pas** un `<MouseWheel>` : c'est
> `<Button-4>` / `<Button-5>`, et `event.delta` vaut **0**. Le code `delta // 120` rend donc
> 0 : **rien ne défile, et rien ne le dit.** Les trois endroits sont le **catalogue
> d'addons** (à qui on avait justement retiré son plafond de 6 pour qu'il défile) et les
> **deux fenêtres** de contrôle et de désinstallation, dont le bouton du bas sort de l'écran
> sans défilement — « un bouton qu'on ne voit pas est un bouton qui n'existe pas ».

Corrigé par `lier_molette()`, qui relie les **trois** séquences. Sous Windows, les deux
nouvelles ne se déclenchent jamais : rien ne change.

## Ce que le balayage a aussi montré, et que je n'ai pas touché

`platform.platform()` est étiqueté **« Windows : »** dans le relevé de diagnostic — sur un
Linux, la ligne dira « Windows : Linux-6.5… ». C'est cosmétique et ça change un format que
des joueurs collent déjà : je le signale, je ne le change pas sans ton avis.

---

# Contre-épreuve du bloc A — quatre lecteurs indépendants

Mon outil est reproductible, mais il ne trouve **que ce que je lui ai appris à chercher**.
J'ai donc lancé en parallèle quatre balayages indépendants avec des lentilles différentes
(modules, chemins et commandes, pièges de fenêtre, chaîne d'appel depuis chaque geste du
joueur) : **86 signalements bruts, 52 symboles distincts**.

Ils **confirment mes 7 non gardés** sans exception, et en ajoutent qui sortent du cadre de
mon outil. Je les ai vérifiés un par un — **la plupart sont bénins, un ne l'est pas.**

## Celui qui compte : le presse-papier sous X11

> Sous X11, **le presse-papier appartient au processus vivant.** Quand le Hub se ferme, ce
> qu'il y a mis peut disparaître — il n'y a pas de « presse-papier système » comme sous
> Windows, seulement un propriétaire de sélection.

Ça touche directement le bouton que je viens de reposer : un joueur Linux qui clique
« Copier mon rapport », **ferme le Hub**, puis va coller sur Discord, peut se retrouver avec
un presse-papier vide. En pratique la plupart des bureaux (GNOME, KDE) font tourner un
gestionnaire de presse-papier qui conserve le contenu — mais ce n'est **pas** garanti.

**Je ne l'ai pas corrigé**, et je préfère le dire : la correction propre serait de garder le
Hub ouvert le temps de la sélection, ou d'écrire aussi le rapport dans un fichier. Les deux
sont des décisions d'interface, pas des gardes techniques — et je ne peux pas les éprouver
sur un vrai bureau. **À arbitrer.**

## Les autres, vérifiés et bénins

| signalé | vérifié |
|---|---|
| `chr(code) + ":\\"` — le balayage des lecteurs A: à Z: (`compagnon.py:524`) | `os.path.isdir("A:\\")` rend simplement False 26 fois : la passe ne trouve rien, elle ne lève pas. Sous Linux le dossier se choisit à la main de toute façon |
| `if os.path.isdir(r"D:\AscensionFR\WorkFlow")` (`compagnon.py:2401`) | le garde-fou « atelier » de ta machine. Faux sous Linux : il ne se déclenche pas. Et il vit dans l'interface v2, que le Hub n'instancie plus |
| `ImageGrab.grab(...)` (`interface_hub.py`, `--capture`) | chemin de développement uniquement — un joueur n'y arrive jamais. Le run Linux photographie avec `import -window root`, pas avec Pillow |
| `f.transient(self)` | supporté par X11 ; le comportement varie d'un gestionnaire à l'autre, mais rien ne lève |
| `z.extractall(...)` | les zips de release GitHub utilisent des séparateurs `/` : pas de piège d'antislash ici |
| sensibilité à la casse (`Interface` vs `interface`) | réel sous Linux, mais le dossier vient d'un choix du joueur ou d'un `os.listdir` — jamais d'une casse écrite en dur côté Hub |

**Ce que ce croisement m'apprend :** un outil qui compte est meilleur qu'un compte à la main,
mais il ne remplace pas des lecteurs qui cherchent autre chose. Le presse-papier, mon
balayeur ne l'aurait jamais trouvé — il ne lève rien, ne s'affiche nulle part, et ne se voit
qu'en suivant le geste du joueur jusqu'au bout.

---

# BLOC B — le bouton fantôme

**Une précision sur ta consigne, parce qu'elle change le travail.** Tu écris que la fonction
existe déjà à `compagnon.py:2405` et qu'il n'y a qu'un bouton à poser. `copier_rapport` y est
bien — mais c'est une **méthode de la classe `Compagnon`**, l'ancienne interface v2, pas une
fonction du moteur. `logique.copier_rapport()` n'existe pas : le Hub ne pouvait pas l'appeler.
J'ai donc réécrit la méthode côté Hub **en suivant la v2 ligne pour ligne** (mêmes règles :
on donne TOUT, même le déjà-envoyé, et on ne marque rien comme parti — rien ne prouve que le
joueur collera).

Ce qui est posé :

1. **Le décor** — `btn_copier` cuit par `fabriquer_decor_hub.py`, en bouton **neutre**
   (pierre) et non rouge : l'arbitrage du 28/07 vaut ici comme pour « Couper les voix », le
   rouge appartient à l'action principale.
   *Pas d'état grisé, volontairement :* copier est toujours possible, et c'est même le
   **seul** chemin quand le webhook est absent. Un bouton grisé mentirait.
2. **Le bouton**, à droite de « Envoyer mon rapport ». Le compteur qui occupait cette place
   descend sous la rangée, et le panneau grandit de 34 px (`PAN_LETTRE_H` 330 → 364) plutôt
   que de tasser trois éléments l'un sur l'autre.
3. **Le message ne ment plus.** Avant : « copie le rapport (bouton ci-dessous) » + appel à
   `copier_diagnostic`, qui copie le **relevé d'installation**. Maintenant, sur échec
   d'envoi, c'est **le rapport** qui part dans le presse-papier — comme le faisait déjà le
   Compagnon v2 (`_envoi_rate`) — et le texte dit exactement ça. Si le rapport n'a même pas
   pu être construit, le message renvoie au bouton **par son nom** : « clique « Copier mon
   rapport » ».

**Recuisson vérifiée par empreinte**, parce que « ça n'a touché que ce qu'il fallait » est
une affirmation qu'on peut mesurer : sur les 98 fichiers de `assets/hub`, la régénération
complète donne **2 nouveaux** (`btn_copier.png`, `btn_copier_survol.png`), **1 modifié**
(`parchemin_lettre.png`, le panneau plus haut), le manifeste — **et rien d'autre**. Les 95
autres PNG sont identiques au bit près.

Géométrie relue numériquement (pas à l'œil) : boutons 316→360, compteur 374→390, case à
cocher 405→431, bas du panneau 460. **Aucun recouvrement**, 29 px de marge sous la case.

---

# 🛑 BLOC C — la preuve

Tu m'as autorisé la branche et le run : `programme-23-plantage-visible` sur le dépôt public,
workflow **en mode diagnostic** (sans secret, sans binaire exporté, aucun tag, aucune release).
Le workflow a été étendu de 6 étapes qui **mesurent** au lieu d'affirmer.

## Ce que j'ai failli te livrer — et qui aurait été un faux vert

Le premier run est passé au vert sur une étape qui **ne mesurait rien** : mes deux mesures de
molette rendaient `[]` (la racine était `withdraw`, le canvas jamais posé — `event_generate`
ne délivrait rien) **et imprimaient leur conclusion quand même**. C'est mot pour mot la
maladie qu'on soigne depuis une semaine, et je l'ai réintroduite dans mon propre banc.

Corrigé : la mesure **échoue franchement** si elle ne reçoit aucun événement, et refuse aussi
le cas où X11 rendrait un `<MouseWheel>` — qui contredirait tout le raisonnement.

Deux autres pièges payés en route, notés pour la prochaine fois :
- une **apostrophe française** dans un commentaire refermait la chaîne de `bash -c '…'` et
  cassait l'étape entière → les scripts Python passent par un **fichier**, jamais par un
  heredoc imbriqué ;
- un script lancé depuis `/tmp` ne voit pas le dossier courant → `PYTHONPATH`.

## AVANT — les deux chemins, rejoués sur une vraie machine Linux

```
=== 1. « Lancer le jeu » : import winreg sans garde ===
Traceback (most recent call last):
  File "<stdin>", line 3, in <module>
ModuleNotFoundError: No module named 'winreg'
>>> VOILÀ ce que faisait le bouton « Lancer le jeu ».
```

```
=== la molette ===
événements reçus : [('Button-4', 0), ('Button-5', 0)]
delta d'un cran X11 : [0, 0]
>>> un cran arrive en Button-4/5, JAMAIS en <MouseWheel>, et delta vaut 0.
```

## ⚠️ Ce que le coureur NE SAIT PAS reproduire — à dire à Tetardtek

**Le `grab failed: window not viewable` ne se reproduit pas sur le coureur.** Ni sous Xvfb nu,
ni avec un vrai gestionnaire de fenêtres (j'ai installé **openbox** exprès) : `grab_set`
réussit du premier coup, et **même sur une fenêtre volontairement retirée**. Son échec dépend
du gestionnaire de fenêtres de SON bureau.

Je ne peux donc **pas** prouver que ma correction supprime son symptôme. J'ai prouvé ce que je
pouvais prouver : que **le mécanisme de reprise fonctionne**, en remplaçant `grab_set` par un
récalcitrant qui refuse deux fois —

```
suite des essais : ['refusé', 'refusé', 'pris']
>>> deux refus encaissés, le grab est pris au troisième.
>>> (le symptôme RÉEL reste à confirmer par Tetardtek)
```

Le raisonnement qui reste, et il est solide : ma correction **garde l'essai immédiat inchangé**
et n'ajoute une reprise que **sur l'exception**. Elle ne peut pas rendre les choses pires, et
elle transforme un bouton mort en bouton qui s'ouvre. Mais c'est un raisonnement, pas une
mesure. **C'est le trou du bloc C, et c'est Tetardtek qui le bouchera.**

## APRÈS — les chemins réparés, dans le code qui est empaqueté

```
=== _candidats_registre() ===   rendu : []      (plus de ModuleNotFoundError)
=== _fenetre() ===              la fenêtre existe : True
                                qui tient le grab après 1,5 s : .!toplevel
=== la molette ===              crans lus : [1, -1]
```

## Où va la sortie d'erreur, sous Linux ? — la mesure qui manquait au bloc 0

Sonde PyInstaller `--windowed`, construite et lancée sur le coureur :

```
gelé            : True
sys.stdout      : <_io.TextIOWrapper name='<stdout>' mode='w' encoding='utf-8'>
sys.stderr      : <_io.TextIOWrapper name='<stderr>' mode='w' encoding='utf-8'>
```

**Les deux systèmes ne se cassent pas de la même façon**, et ça compte pour ta décision :

| | `sys.stderr` | ce que ça donne |
|---|---|---|
| **Windows** (`runw.exe`) | **`None`** | le traceback n'est écrit **nulle part**, irrécupérable |
| **Linux** (`run`, `--windowed` sans effet) | un vrai flux | écrit sur le descripteur hérité : **visible depuis un terminal, perdu au double-clic** |

PyInstaller le confirme dans son propre journal : `Bootloader …/Linux-64bit-intel/run` — il
n'y a pas de `runw` sous Linux. C'est exactement ce que Tetardtek a vécu.

## Le plantage provoqué exprès — et le joueur qui le voit

Trois pannes délibérées (`--planter rappel|fil|demarrage`), une par porte. Pour chacune :
capture d'écran, **liste des fenêtres X11 réellement affichées** (mesure, pas impression), et
le fichier de trace.

| panne | fenêtres X11 mesurées | verdict |
|---|---|---|
| `rappel` | Hub `1082x701` **+ une `640x460`** | la fenêtre de plantage est là, devant |
| `fil` | Hub `1082x701` **+ une `640x460`** | idem — une panne de fil de fond se voit aussi |
| `demarrage` | **une seule `640x460`**, pas de Hub | le Hub n'a pas démarré, et le joueur le sait |

Le troisième cas est celui qui compte le plus : **avant, un joueur qui double-cliquait voyait
le binaire s'ouvrir et disparaître, sans un mot.**

Le fichier de trace, tel qu'il est sorti du coureur :

```
======================================================================
[02/08/2026 17:46:46] Hub 3.4.1 — Linux-6.8.0-1062-azure-x86_64-with-glibc2.35
Pendant : Lancer le jeu
Traceback (most recent call last):
  ...
RuntimeError: panne d'essai dans un rappel (--planter rappel)
======================================================================
[02/08/2026 17:47:03] Hub 3.4.1 — Linux-6.8.0-…
Pendant : une tâche de fond (Thread-1 (_panne_de_fil))
  ...
```

Et une étape du workflow **cherche dans la trace ce qui ne doit pas y être** (le webhook, une
URL de webhook quelconque, le dossier personnel, le nom d'utilisateur, un nom de compte WoW)
**et ce qui doit y être** (le geste, le traceback, la version). Verte.

## Un défaut trouvé EN REGARDANT la capture

La fenêtre du cas « démarrage » disait *« Tu peux fermer cette fenêtre et continuer à te servir
du Hub »* — **alors qu'il n'y avait aucun Hub derrière.** Corrigé : quand le Hub n'a pas pu
démarrer, le texte le dit et propose de réessayer. Ça ne pouvait pas se voir autrement qu'en
regardant l'image.

## Windows non régressé — 23 affirmations, toutes vertes

`outils/banc_windows_non_regression.py` charge la version d'AVANT depuis `git show HEAD:…` et
**fait tourner les deux côte à côte** :

- **« Lancer le jeu »** : `_candidats_registre()` rend exactement la même liste qu'avant
  (mesuré sur ta vraie base de registre : `['D:\WOW_Priv']`). Puis les **trois scénarios** —
  launcher trouvé, repli sur `Ascension.exe`, rien trouvé — donnent le **même fichier lancé**
  et le **même message**, au caractère près.
  *Le jeu n'est jamais lancé pour de vrai : `os.startfile` est remplacé par un mouchard.*
- **« Vérifier mon installation »** : `grab_current()` juste après `_fenetre()` rend bien la
  fenêtre fille — sous Windows le grab est donc pris **immédiatement**, sans passer par la
  reprise. Comportement identique.
- **la fenêtre de plantage** s'ouvre, nomme le geste, donne le chemin, et une deuxième panne
  **n'empile pas** une deuxième fenêtre.
- **la mise en page** : aucun recouvrement, 29 px de marge sous la case à cocher.

## Ce que je n'ai PAS pu éprouver — franchement

1. **Le symptôme `grab failed` de Tetardtek.** Non reproductible sur le coureur (voir plus
   haut). C'est le trou principal.
2. **La molette avec une VRAIE molette.** J'ai fabriqué les événements `Button-4/5` ; personne
   n'a physiquement tourné une molette sur un vrai bureau.
3. **« Lancer le jeu » sous Linux.** Je ne lance rien : je dis au joueur que le Hub ne sait pas
   le faire sur son système. Deviner Wine / Lutris / un préfixe sans pouvoir l'éprouver aurait
   été exactement le genre de code qui rate en silence. **À arbitrer par toi.**
4. **Le Hub Linux sur un vrai bureau** (GNOME, KDE) : openbox n'est pas Ubuntu-avec-GNOME. Les
   décors, les polices et le défilement peuvent s'y comporter autrement.
5. **La fenêtre de plantage sur un thème sombre.** Elle est en parchemin clair, en dur.
6. **Le cas « disque plein / dossier en lecture seule »** au moment du plantage : le repli vers
   le dossier de configuration est éprouvé au banc, pas sur une machine réellement saturée.

---

# BLOC D — ce que ça coûte à sortir

## Ce qui change pour un joueur **Windows**

| # | changement | pour qui | valeur |
|---|---|---|---|
| 1 | **un plantage devient visible** — fenêtre + trace | tous les 274 | ⭐⭐⭐ c'est le sujet |
| 2 | **le bouton fantôme existe** (« Copier mon rapport ») | tous, au moindre échec réseau | ⭐⭐⭐ |
| 3 | **le message d'échec ne ment plus** : c'est le RAPPORT qui est copié, plus le relevé d'installation | tous, au moindre échec réseau | ⭐⭐⭐ |
| 4 | la mise à jour de l'application ne peut plus être proposée hors Windows | 0 joueur Windows | — (mais ⭐⭐⭐ pour Linux, et **avant** la prochaine version) |
| 5 | `_relancer_admin` de l'ancienne v2 gardé | 0 (code mort chez eux) | — |
| 6 | le panneau « Contribuer » grandit de 34 px | tous, cosmétique | ⭐ |

**Rien d'autre.** Les corrections de plateforme (winreg, `os.startfile`, `grab_set`, molette)
sont, sous Windows, **des chemins qui ne s'exécutent jamais** ou des comportements identiques —
et c'est le banc de non-régression qui le dit, pas moi.

Les points **2 et 3 sont les plus importants pour tes 274 joueurs**, et ils n'ont rien à voir
avec Linux : c'est le chemin d'échec réseau de n'importe qui. Aujourd'hui, un joueur dont
l'envoi rate lit « copie le rapport (bouton ci-dessous) », ne trouve aucun bouton, et si
malgré tout il colle son presse-papier, **il colle la mauvaise chose**. Ça dure depuis la
3.0.0.

## Peut-on ne remplacer que le binaire Linux de la `v3.4.1` ?

**Techniquement oui, et c'est même déjà comme ça** : le Hub Linux n'est PAS un asset de la
release — c'est un artefact de run, que le workflow refuse d'exporter en release. Aucun des
274 Compagnons Windows ne peut le voir.

**Mais ça ne réglerait que Linux.** Or les deux défauts qui touchent le plus de monde
(l'échec muet et le bouton fantôme) sont **Windows aussi**. Un binaire Linux seul laisserait
274 personnes avec un Hub qui se tait quand il rate.

Et il y a une contrainte que tu connais mieux que moi : la doctrine du 28/07 — *une mise à
jour = UN numéro*, `VERSION_COMPAGNON` = `## Version:` du .toc = tag. Sortir un exe Windows
corrigé **sans** changer le numéro rejouerait la dissociation qui avait créé la boucle de
mise à jour infinie du 25-28/07. Donc : ou bien une **3.4.2** pour tout le monde, ou bien
rien.

## Mon avis

**Une 3.4.2, mais pas ce soir.** Dans cet ordre :

1. **D'abord Tetardtek.** Il me manque la seule preuve que je ne sais pas fabriquer : que le
   `grab_set` réparé règle vraiment son symptôme. Ça se joue en un essai de sa part, et ça ne
   coûte rien d'attendre — le défaut de mise à jour est **endormi tant qu'aucune nouvelle
   version n'existe**. C'est même l'argument décisif : **publier une 3.4.2 est précisément ce
   qui ARMERAIT le défaut** si la désamorce n'était pas déjà dedans. Elle l'est ; mais je
   préfère qu'il l'ait vue.
2. **Ensuite la 3.4.2 complète** — addon + exe Windows + le binaire Linux en artefact. Pour
   les 274, l'argument de vente n'est pas « support Linux », c'est : *« quand quelque chose
   rate, le Hub le dit maintenant, et le bouton pour nous envoyer ton rapport existe enfin. »*
3. **La PR de Tetardtek après**, pas avant : le choix de l'asset par plateforme touche
   `derniere_release()`, `reference_asset()` et `verifier_telechargement()` (les trois coutures
   nommées plus haut). Deux chantiers dans la même version, sur le chemin de la mise à jour
   automatique, c'est ce qui a coûté cher au 25-28/07.

**Ce que je ne recommande pas :** attendre d'avoir « le support Linux complet ». Les trois
corrections qui comptent pour les 274 sont prêtes et éprouvées ; les faire attendre un
chantier Linux qui n'est pas de leur ressort serait les faire payer pour un autre.

🛑 **Aucun tag, aucune release, aucun asset remplacé.** La branche
`programme-23-plantage-visible` est poussée sur le dépôt public et le run est en mode
diagnostic : rien n'est visible d'un joueur. Dis-moi si je la supprime ou si je la laisse
pour Tetardtek.

---

# Ce qui a résisté, et ce que j'ai failli casser

## Ce qui a résisté

- **Le symptôme de Tetardtek ne se reproduit pas.** J'ai installé un vrai gestionnaire de
  fenêtres exprès ; `grab_set` réussit quand même, même sur une fenêtre retirée. J'ai dû me
  rabattre sur la preuve du mécanisme. C'est le seul endroit où je te rends un raisonnement
  au lieu d'une mesure.
- **Le premier run a été vert sur une étape qui ne mesurait rien.** Mes mesures de molette
  rendaient `[]` et concluaient quand même. Trouvé en lisant la sortie ligne à ligne, pas en
  regardant le voyant.
- **Une apostrophe française** a cassé une étape entière (`bash -c '…'`). Trois runs perdus.
- **`copier_rapport` n'était pas là où le programme le disait** : c'est une méthode de
  l'ancienne classe v2, pas une fonction du moteur. Il a fallu la réécrire, pas la brancher.

## Ce que j'ai failli casser

- **`CONFIG_DIR`.** J'ai changé une constante lue par les 274 installations Windows. Le banc
  compare maintenant, au caractère près, à l'ancienne formule — et le workflow Actions, qui
  s'appuyait sur l'ancien repli `"."` pour poser sa fausse configuration, a dû être corrigé
  en même temps. Si j'avais changé l'un sans l'autre, le run aurait été vert avec un Hub qui
  ne trouve plus son dossier de jeu.
- **Deux fenêtres pour un seul défaut.** Ma première version laissait l'exception remonter
  au-dessus de `main()` : sous Windows, PyInstaller aurait affiché SA boîte anglaise
  par-dessus la mienne. `main()` est devenu une enveloppe dont rien ne sort.
- **Le décor.** Recuire `fabriquer_decor_hub.py` régénère les 98 PNG. J'ai empreinté avant et
  après : 2 nouveaux, 1 modifié (le panneau plus haut), 95 identiques au bit près. Sans cette
  vérification, un décor qui dérive passe inaperçu jusqu'à ce qu'un joueur le voie.
- **Un balayage trop gentil.** Mon détecteur de « garde de plateforme » reconnaissait au
  départ n'importe quel `hasattr(...)` et n'importe quel `.startswith(...)` — il aurait
  déclaré « gardé » des endroits qui ne l'étaient pas. Resserré : tout ce qui n'est pas
  nommément reconnu compte comme NON gardé.
- **Le message d'échec d'envoi.** En reposant le bouton, j'ai failli garder l'ancien
  `copier_diagnostic` « au cas où » — ce qui aurait laissé deux gestes contradictoires. Le
  relevé d'installation reste accessible par **Ctrl+D**, comme avant ; c'est le rapport qui
  part au presse-papier quand l'envoi rate.

---

# Les outils laissés derrière

| outil | ce qu'il mord |
|---|---|
| `outils/balayer_windows.py` | compte les endroits qui supposent Windows et dit lesquels ne sont pas gardés — relançable après chaque retouche (`--origine` pour comparer à git HEAD) |
| `outils/banc_incident.py` | 10 épreuves, 29 affirmations : la trace ne porte ni secret ni identité, et le gestionnaire de plantage ne plante jamais |
| `outils/banc_maj_plateforme.py` | 13 affirmations : le défaut de la mise à jour existait, il est désamorcé aux trois barrières, Windows n'a pas bougé |
| `outils/banc_windows_non_regression.py` | 23 affirmations : fait tourner la version d'AVANT et celle d'APRÈS côte à côte |
| 6 étapes de plus dans le workflow Actions | mesurent sur une vraie machine Linux, et **échouent si elles ne mesurent rien** |

---

# « Terminé », point par point

| ce que tu demandais | fait ? | où |
|---|---|---|
| ce que voit un joueur quand ça plante, **Linux ET Windows**, mesuré | ✅ | bloc 0 §1 (sonde Windows + fenêtres énumérées) et bloc C (sonde Linux sur le coureur) |
| un plantage **visible** au double-clic | ✅ | 3 portes → une fenêtre française ; 3 captures Linux, 1 Windows |
| une trace **sans secret, sans pseudonyme, sans chemin inutile** | ✅ | `_anonymiser` + `banc_incident` (31 affirmations) + une étape du run qui fouille la trace |
| les deux boutons réparés | ✅ | `import winreg` gardé ; `grab_set` avec reprise ; **et un troisième défaut** sur le même bouton (`os.startfile`) |
| **la liste complète de leurs frères, avec le compte** | ✅ | **25 endroits, 7 non gardés → 0** ; `outils/balayer_windows.py`, relançable |
| le bouton fantôme reposé, message qui dit la vérité | ✅ | `btn_copier` cuit et posé ; c'est le RAPPORT qui est copié |
| un plantage provoqué exprès, et le joueur qui le voit | ✅ | `--planter rappel\|fil\|demarrage`, fenêtres X11 mesurées, trace en entier |
| Windows non régressé, prouvé | ✅ | `banc_windows_non_regression` : la version d'AVANT et celle d'APRÈS tournent côte à côte |
| ce qui reste non éprouvé, dit franchement | ✅ | bloc C, 6 points — dont **le symptôme `grab_set` de Tetardtek, que le coureur ne sait pas reproduire** |
| le chiffrage pour la sortie, et mon avis | ✅ | bloc D — **une 3.4.2 pour tout le monde, après l'essai de Tetardtek** |
| ce qui a résisté, ce que j'ai failli casser | ✅ | fin du bloc D |
| l'ajout urgent (mise à jour hors Windows) | ✅ | désamorcé aux **trois** barrières, 13 affirmations, coutures de la PR nommées |

## Ce qui attend une décision de ta part

1. **La branche `programme-23-plantage-visible`** : je la supprime, ou je la laisse pour
   Tetardtek ?
2. **La sortie** : 3.4.2 pour tout le monde ? (mon avis : oui, après son essai)
3. **« Lancer le jeu » sous Linux** : message honnête (ce que j'ai fait), ou tenter Wine ?
4. **Le presse-papier sous X11** (contre-épreuve du bloc A) : le laisser, ou écrire aussi le
   rapport dans un fichier ?
5. **`platform.platform()` étiqueté « Windows : »** dans le relevé de diagnostic — cosmétique,
   mais ça change un format que des joueurs collent déjà.

🛑 **Aucun tag, aucune release, aucun asset remplacé.** Le run GitHub était en mode
diagnostic : ni secret demandé, ni binaire exporté.
