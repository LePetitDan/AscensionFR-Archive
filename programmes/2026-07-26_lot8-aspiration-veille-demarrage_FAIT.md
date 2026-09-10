# Demande de code → Claude Code

**Date :** 2026-07-26 · **lot 8 — l'aspiration de la veille au démarrage du PC, et à la main**

> Petit lot, indépendant du reste. Il ne touche ni aux traductions, ni au build.
> À faire quand le lot 7 est fini.

---

## Pourquoi

`aspirer_veille.py` tourne aujourd'hui **une fois par jour à 18h45** (tâche Windows posée
au lot « veille Discord »). Or les horaires de Dan sont : au travail de 7h à 14h30, PC
allumé en rentrant, vers 14h30. Le PC est donc souvent **éteint à 18h45**, et quand il
s'allume la récolte date de la veille.

Le rapport Cowork qui lit cette récolte est calé à **16h00**. Pour qu'il ait de la matière
fraîche, l'aspiration doit avoir tourné **avant**, c'est-à-dire au moment où Dan allume son
PC.

## Objectif (le QUOI, pas le comment)

**1. Aspirer au démarrage du PC.**
Ajouter un déclenchement **à l'ouverture de session** sur la tâche Windows existante (ou
une seconde tâche, comme tu préfères — dis-moi ce que tu as choisi et pourquoi). Avec un
petit délai au démarrage pour laisser le réseau se lever : la tâche ne doit pas échouer
parce que Windows n'a pas encore de connexion.

**2. Garder le passage de 18h45** comme filet, pour les jours où le PC s'allume tard ou
reste allumé.

**3. Un raccourci pour la lancer à la main**, sur le Bureau, nommé clairement
(« Aspirer la veille Discord »). Dan doit voir que ça a marché : une fenêtre qui reste
ouverte à la fin avec le compte des nouveaux messages, pas une fenêtre noire qui se ferme
en un clin d'œil.

⚠️ **Un raccourci `.lnk`, jamais une copie du script** — c'est le piège déjà rencontré avec
l'Atelier : une copie posée sur le Bureau ne voit pas les mises à jour du code.

**4. Ne pas aspirer deux fois pour rien.** Si la tâche part au démarrage puis à 18h45, le
second passage doit voir qu'il n'y a rien de neuf et ne rien écrire — c'est déjà le
comportement que tu avais vérifié, confirme juste qu'il tient avec deux déclenchements.

---

**« Terminé » veut dire :**

> - `schtasks /query` montre le déclenchement au démarrage **et** celui de 18h45.
> - Un raccourci `.lnk` sur le Bureau qui lance l'aspiration et affiche le résultat.
> - Un essai réel : lancer à la main, vérifier qu'un fichier est écrit (ou « rien de
>   nouveau » proprement affiché), puis relancer tout de suite et vérifier que rien n'est
>   réécrit.
> - `aspirer_discord.py` (le flux des rapports du Hub) **toujours inchangé** — c'est un
>   autre tuyau, il ne doit pas bouger.
> - Rien de publié, rien de poussé, aucune traduction touchée.

**Validation :**

> Entièrement autonome. **Dis-le-moi** si le déclenchement au démarrage oblige à changer le
> compte sous lequel la tâche tourne, ou à demander des droits particuliers — je préfère
> que Dan le sache avant.

---
## Réponse de Claude Code

**Fait le 27/07/2026. La veille part maintenant à l'ouverture de session (+3 min)
ET à 18 h 45, et Dan a un raccourci sur son Bureau. Essai réel fait dans les
deux sens. Rien n'a été publié ni poussé, aucune traduction touchée.**

**Réponse à ta question de validation : non, rien à changer.** La tâche tourne
sous **le même compte qu'avant** (Dan, `InteractiveToken`) et ne demande
**aucun droit particulier** — pas d'élévation, pas de mot de passe stocké, pas
de « exécuter même si l'utilisateur n'est pas connecté ». C'était le point à
surveiller : un déclenchement à l'ouverture de session n'a par nature besoin
d'aucun de ces privilèges, puisque la session est justement ouverte.

### Ce que j'ai choisi, et pourquoi

**Une seule tâche, deux déclenchements** — pas une seconde tâche.

Trois raisons, dans l'ordre où elles comptent : un seul endroit où regarder
quand quelque chose cloche ; une seule action à corriger le jour où le chemin
du script bouge (avec deux tâches, on en oublie une, et l'oubli ne se voit
pas) ; et la politique `IgnoreNew`, déjà en place, empêche d'elle-même les deux
départs de se marcher dessus si jamais ils se croisaient.

**Le délai est de 3 minutes** après l'ouverture de session. Sans lui, la tâche
partirait avant que Windows ait une connexion et mourrait sur un « Découverte
des salons impossible » — un échec pour rien, et surtout **invisible**,
puisqu'elle tourne en `pythonw` sans fenêtre.

**J'ai mis tout ça dans le code, pas dans une commande à la main.**
`aspirer_veille.py --planifier` installe désormais **la tâche ET le raccourci**,
et il est idempotent : on peut le relancer autant de fois qu'on veut. Poser la
tâche à la main aurait marché aujourd'hui, mais la définition n'aurait vécu
nulle part — impossible à rejouer après une réinstallation de Windows, et
personne pour se souvenir du délai de 3 minutes.

### Le raccourci du Bureau

`C:\Users\<utilisateur>\Desktop\Aspirer la veille Discord.lnk` — un **vrai `.lnk`**
(1 640 octets), jamais une copie du script : c'est le piège de l'Atelier, une
copie sur le Bureau ne voit pas les mises à jour du code.

| | |
|---|---|
| Cible | `…\Python312\**python.exe**` *(et non `pythonw.exe` : on veut la fenêtre)* |
| Arguments | `"…\outils\aspirer_veille.py" **--pause**` |
| Dossier | `D:\AscensionFR\WorkFlow` |

`--pause` est une option que j'ai ajoutée au script : elle garde la fenêtre
ouverte à la fin, avec « Appuie sur Entrée pour fermer cette fenêtre… ».
Elle est posée **hors de `main()`**, dans le point d'entrée : la fenêtre reste
donc ouverte **aussi quand le script échoue** — c'est même là qu'il y a le plus
à lire.

### L'essai réel

| | résultat |
|---|---|
| **Passage 1** (à la main) | `29 nouveau(x) message(s) -> 2026-07-27_nouveau.md` — 10 450 octets écrits |
| **Passage 2**, tout de suite après | `Rien de nouveau. (0 message(s) de bot ignoré(s))` |
| Le fichier du jour a-t-il été réécrit ? | **non** — 10 450 octets, empreinte `b57e105dea` identique avant et après |
| L'état a-t-il bougé ? | **non** — `_etat.json` empreinte `1571853ca1` identique |
| Ce qui a bougé | `_journal.log` seul, et c'est voulu : c'est le journal des passages |

Donc le point 4 tient : **deux départs dans la même journée ne font pas de
dégât**. Le second voit les marque-pages déjà avancés, ne trouve rien, et
n'écrit aucun fichier de contenu.

`schtasks /query /xml` montre bien les deux déclenchements :

```
<LogonTrigger><Delay>PT3M</Delay><UserId>PC_DAN\Dan</UserId></LogonTrigger>
<CalendarTrigger><StartBoundary>2026-07-27T18:45:00+02:00</StartBoundary>
                 <ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay>
```

Le `StartWhenAvailable` d'origine est conservé : si le PC est éteint **et** à
18 h 45 **et** au moment de la session suivante (mise en veille prolongée, par
exemple), Windows rattrape quand même le passage manqué.

### Deux choses vues au passage

**Un salon a été renommé pendant l'essai** : « addon_glayna » s'appelle
maintenant « ⚙️-addon_glayna ». Le script l'a dit et **a continué sur son
identifiant**, sans rien perdre — c'est exactement le comportement pour lequel
il avait été écrit, mais c'est la première fois qu'il servait pour de vrai.

**`aspirer_discord.py` n'a pas été touché** — fichier du 18/07, aucun diff.
C'est bien l'autre tuyau (les pièces jointes de #rapports-auto pour le
pipeline), il ne devait pas bouger et il n'a pas bougé.

### Ce qui attend une décision de toi

Rien de bloquant. Un seul point si tu veux aller plus loin : la tâche ne tourne
**que si Dan ouvre une session**. Un PC qui démarre et reste sur l'écran de
connexion n'aspire rien. C'est le bon compromis ici (pas de mot de passe à
stocker), mais si un jour tu veux que ça parte au démarrage même sans session,
il faudra passer la tâche en « exécuter même si l'utilisateur n'est pas
connecté », donc enregistrer le mot de passe du compte. Je ne l'ai pas fait :
tu m'as demandé de te prévenir avant, et ça ne se justifie pas pour l'usage
décrit.
