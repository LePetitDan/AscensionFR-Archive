# Demande de code → Claude Code

# 🔍 PROGRAMME 8 — l'échec de mise à jour : ENQUÊTE SEULE

**Date :** 2026-07-31

🛑 **Ne change aucun fichier de code. Ne touche à aucun `.spec`. Ne construis rien, ne publies
rien.** Dan veut la cause prouvée avant la moindre correction. Ce programme ne demande que des
mesures et un plan.

---

## Le symptôme

Des joueurs voient, en mettant à jour le Compagnon :

```
Failed to load Python DLL
'C:\Users\<utilisateur>\AppData\Local\AscensionFR_Compagnon\_MEI98642\python312.dll'.
LoadLibrary: le module spécifié est introuvable.
```

Un joueur a proposé une explication — l'appli n'aurait pas de second processus et devrait
« s'auto-tuer » pour se mettre à jour. **Ce n'est pas ce qui se passe**, et je l'ai vérifié dans
ton code avant de l'écrire :

1. `lancer_remplacement()` fait déjà passer l'échange par un `.bat` détaché qui boucle sur `del`
   jusqu'au déverrouillage de l'exe — donc jusqu'à la sortie effective de l'appli —, déplace,
   attend, relance, puis s'efface. Il n'y a aucun auto-kill.
2. L'erreur arrive **après** que le nouvel exe a été écrit et lancé. Le remplacement a réussi. Ce
   qui échoue, c'est le dépliage du nouvel exe par son propre amorceur.

**Une hypothèse est déjà écrite dans ton code**, par quelqu'un qui avait vu passer l'erreur :

```python
# Respiration : l'antivirus inspecte l'exe tout juste écrit ; relancer
# dans la même seconde peut échouer (« Failed to load Python DLL »).
"timeout /t 4 /nobreak >nul\r\n"
```

**C'est une hypothèse, pas une preuve.** Tout l'objet de ce programme est de la confirmer ou de
la démolir. Ne la traite pas comme acquise : c'est précisément le genre de note qu'on croit sur
parole et qui se révèle fausse — la note « les descriptions ne sont pas posées » du programme 4
en est l'exemple.

---

## BLOC 1 — Combien, depuis quand, chez qui

Ce qu'on a collecté doit le savoir. Cherche dans la veille Discord et dans les rapports de joueurs :

- les occurrences de « Failed to load Python DLL », « python312.dll », « module spécifié est
  introuvable », « _MEI » ;
- **depuis quelle version** elles apparaissent — et surtout : est-ce corrélé à une version
  précise, ou est-ce constant depuis toujours ?
- combien de personnes distinctes, pas combien de messages ;
- ce que les rapports disent de leur antivirus, s'ils le disent.

**Si le compte est de deux personnes, on ne répare pas la même chose que s'il est de quarante.**
Donne-moi le chiffre avant toute recommandation.

---

## BLOC 2 — Établir la cause au lieu de la déduire

C'est le cœur, et c'est l'idée de Dan : **la preuve est dans la quarantaine de l'antivirus des
joueurs touchés.**

Rédige un petit message, court et lisible par quelqu'un qui n'est pas informaticien, qu'on puisse
poster sur Discord aux personnes concernées, et qui demande :

- d'ouvrir l'historique / la quarantaine de leur antivirus ;
- de regarder si `python312.dll`, `AscensionFR_Compagnon.exe` ou quelque chose sous
  `AppData\Local\AscensionFR_Compagnon` y figure ;
- de dire **quel antivirus** ils utilisent et **ce qui est écrit** à côté de l'entrée.

Si la DLL est dans leur quarantaine, la cause est **prouvée**. Si elle n'y est pas chez plusieurs
d'entre eux, mon hypothèse tombe et il faut chercher ailleurs — dans ce cas, dis-moi quelles
autres pistes tu vois (dossier de dépliage saturé, droits, disque plein, dépliage partiel laissé
par un lancement précédent).

Ajoute dans ce message le contournement immédiat, pour qu'il serve à quelque chose même si le
joueur ne veut pas jouer les enquêteurs : fermer le Compagnon, vider
`%LOCALAPPDATA%\AscensionFR_Compagnon`, relancer.

---

## BLOC 3 — Ce qu'on saurait mesurer nous-mêmes

Sans rien modifier, dis-moi ce qui est mesurable de notre côté :

- **UPX.** Le `.spec` a `upx=True`. Peux-tu construire un exe `upx=False` **dans un dossier de
  côté, sans toucher au `.spec` du dépôt**, et soumettre les deux à VirusTotal ? Je veux **quatre
  chiffres** : deux taux de détection, deux tailles. C'est ce qui décidera plus tard si le
  compromis vaut les Mo supplémentaires pour les joueurs — mais on ne décide rien aujourd'hui.
- **Le dossier de dépliage.** Il est fixe (`%LOCALAPPDATA%\AscensionFR_Compagnon`) et **rien ne le
  nettoie** — j'ai cherché : il n'est vidé que par « Tout désinstaller ». Combien de `_MEIxxxxx`
  s'accumulent chez toi après plusieurs lancements ? Est-ce qu'un dépliage laissé à moitié par un
  lancement interrompu peut gêner le suivant, ou PyInstaller tire-t-il un nom neuf à chaque fois ?
  **Réponds en le mesurant, pas en le raisonnant.**
- **Reproduis la panne.** Peux-tu la fabriquer chez toi — retirer `python312.dll` du dossier
  déplié pendant que l'exe démarre — et obtenir exactement ce message ? Si oui, on tient le
  mécanisme, indépendamment de qui retire le fichier.

---

## BLOC 4 — Le plan, pas l'exécution

À la fin, propose **ce que tu ferais** et ce que ça coûte, sans le faire. Trois pistes que je vois,
plus celles que tu trouveras :

| piste | ce que j'en attends de toi |
|---|---|
| `upx=False` | les quatre chiffres, et si le gain justifie les Mo |
| nettoyer les `_MEI*` périmés au démarrage | où sont les pièges — instance en cours (`sys._MEIPASS`), deuxième fenêtre ouverte, dossier verrouillé |
| un relais qui **vérifie** le lancement au lieu d'attendre 4 s en aveugle | comment savoir qu'un démarrage a réussi, sachant qu'un exe qui plante a quand même démarré un processus |

Sur la troisième : le piège que je vois est qu'un témoin de réussite laissé par un lancement
précédent ferait croire à un succès qui n'a pas eu lieu. C'est l'épreuve qui se valide toute
seule que tu as débusquée au programme 6. Si tu proposes un témoin, dis comment tu l'évites.

**Signature du code : hors sujet aujourd'hui.** C'est la cause racine de toute cette famille
d'ennuis, mais ce n'est pas ce qu'on traite maintenant.

---

**« Terminé » veut dire :**

> - Le compte réel de joueurs touchés, et depuis quand.
> - Le message d'enquête prêt à poster, court et lisible par un joueur.
> - Les quatre chiffres d'UPX, mesurés **hors du dépôt**.
> - Ce que tu as pu mesurer sur le dossier de dépliage, et si tu as su reproduire la panne.
> - Ton plan chiffré, avec ses pièges nommés.

🛑 **Aucun fichier du projet modifié. Aucun `.spec` touché. Rien de construit pour publication.**

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Puis renommer en `_FAIT.md`.)

---

### BLOC 1 — le chiffre, et pourquoi il ne veut pas dire ce qu'il a l'air de dire

**Le chiffre brut : ZÉRO.** Sur 1 617 messages de veille Discord (18 → 30 juillet, 5 salons) et
7 439 rapports joueurs :

| signature cherchée | occurrences | personnes |
|---|---|---|
| `Failed to load Python DLL` | **0** | **0** |
| `python312` | **0** | **0** |
| `module spécifié est introuvable` | **0** | **0** |
| `_MEI` | 4 — *collisions d'octets dans des `.gz` compressés* | **0** |
| `DLL` (au sens large) | **0** | **0** |

#### 🛑 Ce zéro est un zéro d'INSTRUMENT, pas un zéro de réalité

Je ne te le donne pas comme une bonne nouvelle, parce que je peux montrer que **nos deux
gisements sont structurellement incapables de voir cette panne** :

1. **Les rapports joueurs sont produits PAR le Compagnon.** Leur en-tête le dit :
   `Signalement Ascension FR — via le Compagnon`. Un Compagnon qui ne démarre pas ne peut pas
   signaler qu'il n'a pas démarré. Les 7 439 rapports sont, par construction, l'échantillon des
   machines où **tout a fonctionné**.
2. **L'erreur s'affiche dans une boîte de dialogue Windows.** Pour qu'elle atteigne la veille, il
   faut qu'un joueur la retape ou la capture, puis la poste. Toi tu l'as vue — mais pas dans nos
   fichiers.
3. **Le salon 📖-installation, le plus probable pour cette panne, n'a produit aucun historique**
   alors que son marque-page est bien avancé (28/07 11:27). À creuser à part.

Autrement dit : **on ne sait pas combien de joueurs sont touchés, et nos outils ne peuvent pas
nous le dire.** C'est exactement pour ça que ton BLOC 2 — aller chercher la preuve chez les
joueurs — est la bonne idée, et pas un pis-aller.

*(Au passage : j'ai d'abord cru que la veille avait perdu les jours 27 à 30 — marque-page au
30/07, historique s'arrêtant au 26. **C'était faux** : ces jours sont dans
`2026-07-2X_nouveau.md` à la racine, je n'avais cherché que dans `historique/`. Les chiffres
ci-dessus portent sur les deux.)*

#### Ce qu'on PEUT compter, et qui est du même dossier

**A. L'antivirus s'en prend à notre exe : 5 joueurs distincts**, entre le 22 et le 25 juillet.
Un seul antivirus est nommé, toujours le même : **Windows Defender**, verdict « trojan ».

Et l'un d'eux a fait, spontanément, la mesure que tu demandes au BLOC 3 :

> *« J'ai download la version 2.2.0, Defender ne le détecte pas comme Trojan. C'est apparu avec
> la toute dernière version 2.2.1. Je vais croiser avec VirusTotal voir si on obtient le même
> comportement. »* — 22/07

**La détection est donc corrélée à une version précise, pas constante depuis toujours.** C'est
la signature d'une heuristique qui bascule, pas d'un défaut permanent — et ça compte pour le
BLOC 3.

**B. La panne, vue du côté du joueur qui ne lit pas les messages d'erreur : 2 joueurs distincts,
le 27/07.**

> *« Petite question, à chaque fois que j'ouvre le hub je dois refaire la mise à jour 3.3.1,
> pourquoi ? »*
> *« J'ai pareil, ça doit être un bug du HUB. »*

**C'est la même panne sans la boîte de dialogue.** Une mise à jour qui ne tient pas : le Hub
remplace l'exe, le nouvel exe ne démarre pas ou n'est plus là, l'ancien revient, et le Hub
constate à nouveau qu'une version plus récente existe. Boucle. Le joueur ne voit pas d'erreur —
il voit un Hub qui redemande éternellement la même mise à jour.

Si cette lecture est juste, **la panne bruyante et la panne silencieuse sont le même mécanisme**,
et la silencieuse est de très loin la plus fréquente, parce qu'elle ne demande au joueur aucun
effort pour être subie.

#### Depuis quand

| | |
|---|---|
| détections antivirus | **22/07** (version 2.2.1), pas avant sur la même machine |
| mise à jour qui ne tient pas | **27/07**, sur la 3.3.1 |
| la 3.4.0 | publiée le **29/07** — donc le problème **la précède** |

**Ce n'est pas une régression de la 3.4.0.** Toute correction doit viser le mécanisme de mise à
jour et l'exe lui-même, pas cette version.

#### Le compte que je te dois, honnêtement

> **Panne prouvée par nos données : 5 joueurs touchés par l'antivirus, 2 par la mise à jour qui
> ne tient pas, 0 par le message DLL — et un angle mort qui peut cacher n'importe quel nombre.**

C'est plus proche de « deux personnes » que de « quarante » *dans ce qu'on sait mesurer*. Mais je
ne recommanderai rien sur cette base seule : le BLOC 2 sert précisément à transformer cet angle
mort en chiffre.

*Les pseudonymes sont dans la veille ; je les garde hors de ce document (règle « ne jamais citer
les joueurs »). Pour les retrouver :*
`grep -rn "defender\|trojan\|refaire la mise à jour" 3-atelier/veille-discord/`

---

### BLOC 2 — le message d'enquête, prêt à poster

🛑 **Je ne l'ai pas posté.** Il attend ton feu vert, comme toujours.

Deux remarques sur la forme avant le texte. D'abord, **le contournement est mis en premier** :
la plupart des gens veulent que ça marche, pas mener l'enquête, et un message qui commence par
une demande de service se fait ignorer. Ensuite, **on ne demande jamais de désactiver
l'antivirus** — c'est le conseil qu'on lit partout, il est mauvais, et venant de l'éditeur d'un
exe non signé il est franchement gênant.

---

> **🔧 Le Compagnon refuse de démarrer après une mise à jour ? Aidez-nous à comprendre.**
>
> Certains d'entre vous voient une erreur du type **« Failed to load Python DLL »**, ou bien un
> Hub qui **redemande la même mise à jour à chaque ouverture**. On pense savoir pourquoi, mais on
> veut en être sûrs avant de corriger quoi que ce soit.
>
> **➡️ D'abord, pour que ça remarche tout de suite :**
> 1. fermez complètement le Compagnon ;
> 2. appuyez sur `Windows + R`, collez ceci et validez :
>    `%LOCALAPPDATA%\AscensionFR_Compagnon`
> 3. supprimez **tout** ce qu'il y a dans ce dossier (ce ne sont que des fichiers temporaires,
>    vous ne perdez aucun réglage) ;
> 4. relancez le Compagnon.
>
> **➡️ Ensuite, si vous avez deux minutes — c'est ça qui nous aiderait vraiment :**
>
> Notre hypothèse est que **votre antivirus supprime un fichier du Compagnon pendant qu'il
> démarre**. Ça se vérifie facilement, parce qu'il en garde la trace :
>
> - ouvrez votre antivirus et cherchez **« Quarantaine »**, « Historique de protection » ou
>   « Éléments mis en quarantaine » ;
>   *(sous Windows Defender : bouton Démarrer → tapez « Sécurité Windows » → « Protection contre
>   les virus et menaces » → « Historique de protection »)*
> - regardez si l'un de ces noms y apparaît :
>   • `python312.dll`  • `AscensionFR_Compagnon.exe`  • quelque chose contenant `_MEI`
>   • quoi que ce soit dans `AppData\Local\AscensionFR_Compagnon`
>
> **Répondez ici avec :**
> 1. le **nom de votre antivirus** (Windows Defender, Avast, Bitdefender, Malwarebytes…) ;
> 2. ce que vous voyez dans la quarantaine — **une capture d'écran est parfaite**, et le nom de
>    la menace annoncée nous intéresse particulièrement ;
> 3. et si la quarantaine est **vide**, dites-le aussi : **c'est une information tout aussi
>    utile**, elle nous dit qu'on cherche au mauvais endroit.
>
> Le Compagnon n'est pas signé numériquement — une signature coûte plusieurs centaines d'euros
> par an — et les antivirus se méfient par principe des programmes non signés qui se mettent à
> jour tout seuls. C'est un faux positif, mais on préfère vous le prouver plutôt que vous
> demander de nous croire. **Ne désactivez pas votre antivirus.**
>
> Merci 💙

---

**Le point 3 est le plus important du message**, et c'est ta consigne : si la quarantaine est
vide chez plusieurs personnes, **l'hypothèse tombe** et il faut chercher ailleurs. Sans cette
phrase, seuls ceux qui confirment répondraient, et on se retrouverait avec une preuve qui se
valide toute seule — exactement l'épreuve verte du programme 6.

#### Si la quarantaine est vide : les autres pistes, par ordre de vraisemblance

| piste | ce qui la trahirait | vraisemblance |
|---|---|---|
| **dépliage saturé** — 5 dossiers × 77 Mo mesurés chez moi, rien ne les nettoie | disque presque plein chez le joueur ; le vidage du dossier suffit à réparer **durablement** | ⭐⭐⭐ |
| **exe partiellement téléchargé** — coupure réseau pendant la mise à jour, aucun contrôle d'intégrité aujourd'hui | l'erreur revient à l'identique après vidage du dossier | ⭐⭐⭐ |
| **`%LOCALAPPDATA%` redirigé** (profil itinérant, OneDrive, dossier synchronisé) | le chemin de l'erreur ne commence pas par `C:\Users\<utilisateur>\AppData\Local` | ⭐⭐ |
| **droits d'écriture** refusés sur le dossier de dépliage | l'erreur survient dès le premier lancement, jamais après une mise à jour seulement | ⭐ |
| **course de la relance** — les 4 s d'attente du `.bat` trop courtes sur machine lente | corrélé aux machines lentes ; réparé en relançant à la main | ⭐⭐ |

La deuxième mérite d'être notée : **on ne vérifie aujourd'hui aucune empreinte de l'exe
téléchargé.** Un fichier tronqué par une coupure réseau produirait exactement ce symptôme, et
serait rejoué à chaque mise à jour.

---

### BLOC 3 — ce qu'on sait mesurer soi-même

#### ⚠️ UPX : la question n'a pas lieu d'être — **`upx=True` ne fait rien depuis le début**

Tu demandais quatre chiffres. Je ne peux t'en donner que deux, et c'est un résultat, pas un
manquement.

Avant de construire quoi que ce soit, j'ai vérifié la seule chose qui pouvait rendre la mesure
inutile : **UPX n'est pas installé sur cette machine.**

```
=== upx present sur la machine ? ===
  UPX INTROUVABLE dans le PATH
```

PyInstaller, quand il ne trouve pas UPX, **passe l'étape en silence**. Le `upx=True` du `.spec`
est donc décoratif. Vérifié sur le binaire, pas déduit — j'ai lu la table des sections PE de
**l'exe réellement publié, téléchargé depuis la release** :

```
EXE PUBLIÉ (téléchargé depuis la release)
   37,9 Mo   sha256 621401050e340da8bf3032a251e19e55…
   sections : .text, .rdata, .data, .pdata, .fptable, .rsrc, .reloc
   UPX ? NON
   identique à compagnon/dist/ ? OUI
```

Des sections PyInstaller standard. Un exe compressé par UPX porterait `UPX0`/`UPX1`. **Il n'y en
a aucune.**

| ce que tu demandais | valeur |
|---|---|
| taille `upx=True` | **37,9 Mo** |
| taille `upx=False` | **37,9 Mo** — le même fichier |
| détection `upx=True` | *non mesurée, voir ci-dessous* |
| détection `upx=False` | *sans objet* |

**Conséquence directe : la piste UPX est morte, et avec elle l'idée que les Mo supplémentaires
seraient le prix à payer.** Il n'y a pas d'arbitrage à faire — on est déjà dans la configuration
« non compressé », et les antivirus détectent quand même. **Ce n'est donc pas l'empaquetage qui
déclenche Defender**, contrairement à ce qu'on aurait pu croire.

Je n'ai pas construit la variante : elle aurait produit un fichier fonctionnellement identique,
pour cinq minutes de calcul et aucune information. J'ai préféré la preuve sur le binaire livré.

**Sur le taux de détection.** Sans clé d'API VirusTotal (il n'y en a aucune sur la machine),
j'ai interrogé par **empreinte** — une recherche, jamais un envoi. L'empreinte n'y est pas
connue, et la page publique est derrière un captcha. Je m'arrête là **volontairement**, et voici
pourquoi tu dois trancher toi-même :

> 🛑 **Envoyer notre exe à VirusTotal le partage avec l'industrie.** Leur propre page le dit :
> *« sharing of your Sample submission with the security community »*. Or **le webhook des
> rapports est baké dans ce binaire**. Il est déjà extractible depuis la release publique — mais
> le corpus VirusTotal est activement fouillé par des outils automatiques, ce que GitHub n'est
> pas. Après la semaine qu'on vient de passer à empêcher ce webhook de devenir public, je ne
> l'envoie pas sans que tu le décides.
>
> **Si tu veux le chiffre**, la voie propre est : sortir d'abord le webhook du binaire (le relais
> évoqué au programme 6), *puis* soumettre. On aura le chiffre sans rien donner.

#### Le dossier de dépliage — mesuré, pas raisonné

```
C:\Users\<utilisateur>\AppData\Local\AscensionFR_Compagnon
  _MEI139322 : 86 fichiers, 77 Mo — python312.dll présente
  _MEI243122 : 88 fichiers, 76 Mo — python312.dll présente
  _MEI292322 : 88 fichiers, 76 Mo — python312.dll présente
  _MEI348722 : 86 fichiers, 77 Mo — python312.dll présente
  _MEI352962 : 86 fichiers, 77 Mo — python312.dll présente
                                    TOTAL : 380 Mo
```

**Cinq dépliages abandonnés, 380 Mo, datant des 21 et 23 juillet.** Tu avais raison : rien ne les
nettoie.

Mais la mesure corrige une des hypothèses : **ce ne sont pas des dépliages partiels.** Tous les
cinq sont **complets** — 86 à 88 fichiers, `python312.dll` présente et de taille identique
(6 945 272 octets) dans chacun. Ce sont des dépliages entiers laissés par des sorties non
propres, pas des restes tronqués.

**Donc un dépliage abandonné ne peut pas gêner le suivant par son contenu** : PyInstaller tire un
nom neuf à chaque lancement (`_MEI50002` lors de mon essai, encore inédit après 5 précédents). Le
seul nuisance est **la place occupée** — 76 Mo par lancement raté, sans plafond.

#### La reproduction : un fait que je n'attendais pas

J'ai lancé **l'exe publié** en guettant l'apparition de `python312.dll` pour la retirer — sans
simuler d'antivirus, en simulant seulement *son effet*. Résultat :

```
retrait effectué : _MEI50002 — verrouillée :
   [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier
   est utilisé par un autre processus : …\_MEI50002\python312.dll
```

**`python312.dll` est verrouillée dès qu'elle touche le disque.** Un processus tiers — antivirus
compris — **ne peut pas la supprimer pendant que l'amorceur la tient**. C'est un fait mesuré, et
il restreint utilement le mécanisme :

- ❌ « l'antivirus supprime la DLL pendant le chargement » — **impossible telle quelle** ;
- ✅ « l'antivirus **empêche son écriture** » (protection en temps réel, qui intercepte à la
  création) — compatible ;
- ✅ « l'antivirus met **l'exe entier** en quarantaine avant ou pendant le dépliage » —
  compatible, et c'est ce que les 5 joueurs décrivent (« trojan ») ;
- ✅ « la DLL est retirée **entre deux lancements**, quand plus rien ne la tient » — compatible,
  et cohérent avec un dossier `_MEI` réutilisé… sauf qu'on vient de voir qu'il ne l'est jamais.

**La note laissée dans le code — « l'antivirus inspecte l'exe tout juste écrit » — n'est donc ni
confirmée ni démolie, mais elle est PRÉCISÉE** : si l'antivirus agit, c'est au moment de
l'écriture, pas de la lecture. Ce qui veut dire qu'attendre 4 secondes de plus ne garantit rien —
l'inspection peut aboutir à une suppression bien après.

#### Une piste que j'ai pu ÉLIMINER

J'ai lancé l'exe publié avec son dossier de dépliage rendu **inutilisable** de deux façons
(chemin occupé par un fichier ; dossier en écriture refusée) :

```
A. le dossier de dépliage ne peut pas être CRÉÉ  ->  l'exe a DÉMARRÉ normalement
B. le dossier de dépliage est en LECTURE SEULE   ->  l'exe a DÉMARRÉ normalement
```

**L'amorceur ne meurt pas quand son dossier de dépliage est indisponible : il se rabat ailleurs
et démarre.** Donc « dossier de dépliage saturé / verrouillé / redirigé » **n'est pas une cause
plausible** de la panne. Ça élimine deux des cinq pistes que je listais au bloc 2, et ça remonte
d'autant la vraisemblance des autres.

*(Mes essais ont eux-mêmes créé 2 dépliages de plus — 152 Mo en trois lancements, la
démonstration en direct de l'accumulation. Je les ai retirés : le dossier est rendu à son état
d'origine, 5 dossiers / 380 Mo.)*

#### ⚠️ Et un défaut que je n'étais pas venu chercher : le relais peut DÉSINSTALLER le Compagnon

En lisant `lancer_remplacement()` pour le bloc 4, je suis tombé sur pire que le symptôme signalé :

```bat
:attente
timeout /t 1 /nobreak >nul
del "ancien.exe" 2>nul          <- l'ancien est SUPPRIMÉ d'abord
if exist "ancien.exe" goto attente
move /y "nouveau" "ancien.exe" >nul   <- code de retour IGNORÉ
timeout /t 4 /nobreak >nul
start "" "ancien.exe"           <- lancé sans vérifier qu'il existe
del "%~f0"
```

**Entre le `del` et le `move`, il n'existe aucun Compagnon sur la machine.** Si le `move` échoue —
antivirus qui tient le fichier neuf, disque plein, droits — alors :

1. l'ancien exe est déjà supprimé ;
2. l'échec du `move` n'est pas testé ;
3. `start` lance un fichier absent, sans bruit ;
4. le relais **s'efface lui-même**, effaçant la seule trace.

Le joueur ne se retrouve pas avec une mise à jour ratée : **il se retrouve sans Compagnon du
tout, et sans message.** C'est le pire scénario possible pour ce mécanisme, et il est atteignable
aujourd'hui. Je ne l'ai pas reproduit — ce n'est pas ce que tu demandais et ça détruirait une
installation — mais la lecture suffit à l'établir.

---

### BLOC 4 — le plan, pas l'exécution

🛑 **Rien de tout cela n'est fait.** Aucun fichier du projet n'a été modifié, aucun `.spec`
touché, rien construit.

#### Ce que je ferais, et dans quel ordre

| | quoi | coût | ce que ça répare | quand |
|---|---|---|---|---|
| **1** | **Rendre le relais sûr** — vérifier le `move`, ne supprimer l'ancien qu'après | ~30 lignes de `.bat` | le scénario « plus de Compagnon du tout » | **tout de suite, sans attendre l'enquête** |
| **2** | **Vérifier l'empreinte** de l'exe téléchargé avant de remplacer | ~15 lignes | téléchargement tronqué, et la boucle de mise à jour infinie | tout de suite |
| **3** | **Nettoyer les `_MEI*` périmés** au démarrage | ~25 lignes | 380 Mo chez moi, sans plafond | après l'enquête |
| **4** | **Vérifier le lancement** au lieu d'attendre 4 s | ~40 lignes | la mise à jour silencieusement ratée | après l'enquête |
| ~~5~~ | ~~`upx=False`~~ | — | **rien — c'est déjà le cas** | ❌ abandonné |

**Les deux premières lignes ne dépendent pas du résultat de l'enquête.** Que la cause soit
l'antivirus ou autre chose, un relais qui supprime avant de savoir s'il peut remplacer est un
défaut en soi. Je les ferais même si la quarantaine des joueurs est vide.

#### Les pièges, nommés

**Piste 3 — nettoyer les `_MEI*`. Trois pièges, dont un que la mesure a déjà désamorcé :**

- **L'instance en cours.** Il faut épargner le dossier du processus qui nettoie, c'est-à-dire
  `sys._MEIPASS`. Comparaison sur le chemin **normalisé** (`os.path.realpath` + casse), pas sur
  la chaîne brute : `%LOCALAPPDATA%` peut arriver avec une casse différente selon le chemin
  d'appel.
- **La deuxième fenêtre.** Un joueur peut avoir deux Compagnons ouverts. Le second dossier n'est
  pas le nôtre et n'est pas périmé. **Le critère sûr n'est pas l'âge, c'est le verrou** : on
  vient de mesurer que `python312.dll` est verrouillée tant qu'un processus l'utilise. Donc
  *tenter d'ouvrir `python312.dll` en écriture ; si ça échoue avec `WinError 32`, le dossier est
  vivant, on n'y touche pas.* C'est un test d'occupation réel, pas une heuristique de date.
- **Le dossier verrouillé quand même.** `shutil.rmtree` partiel laisse un dossier à moitié vide,
  pire que rien. Donc : `ignore_errors=False`, on saute le dossier entier au premier refus, et on
  réessaiera au prochain démarrage.
- ~~Le dépliage partiel qui gêne le suivant~~ — **écarté par la mesure** : les 5 dossiers trouvés
  sont tous complets, et PyInstaller tire un nom neuf à chaque lancement.

**Piste 4 — vérifier le lancement. C'est là qu'est ton piège, et il est réel.**

Tu as raison : un témoin de réussite laissé par un lancement précédent ferait croire à un succès
qui n'a pas eu lieu — l'épreuve qui se valide toute seule. Ma réponse en trois points :

1. **Le témoin doit être écrit par le NOUVEAU processus, et être unique à CETTE tentative.** Le
   relais tire un identifiant au hasard, le passe en argument (`--temoin <id>`), et n'accepte que
   le témoin portant exactement cet identifiant. Un témoin d'hier ne peut pas répondre à une
   question posée aujourd'hui.
2. **Le relais efface le témoin AVANT de lancer**, et vérifie qu'il a bien disparu. Sans ça, un
   fichier resté verrouillé rejouerait le succès de la veille.
3. **Le témoin doit signifier « je suis arrivé jusqu'à l'interface »**, pas « le processus a
   démarré » — puisque, comme tu le dis, un exe qui plante a quand même démarré un processus.
   Concrètement : écrit après la construction de la fenêtre, pas dans les premières lignes du
   `main`.

Et le point qui décide de la valeur de cette piste : **que fait-on quand le témoin n'arrive
pas ?** Répondre « on relance » ne sert à rien si la cause est un antivirus. La seule action
utile est de **remettre l'ancien exe en place** — donc il faut l'avoir gardé, ce qui est
exactement la piste 1. **La piste 4 n'a de valeur que si la 1 est faite d'abord.**

#### Ce que je ne ferais PAS, et pourquoi

- **Demander aux joueurs d'exclure le dossier de leur antivirus.** Ça marche, et c'est le
  conseil qu'on lit partout. Mais venant de l'éditeur d'un exe non signé, c'est exactement ce
  que dirait un vrai maliciel. On y perdrait plus en confiance qu'on n'y gagnerait en tickets.
- **Soumettre l'exe à VirusTotal aujourd'hui** — tant que le webhook y est baké (voir bloc 3).
- **Toucher au `.spec`.** Il n'y a rien à y changer : `upx=True` est déjà inopérant.

#### Le vrai coût, et la seule chose qui règle la famille entière

Les quatre pistes ci-dessus sont du **rattrapage** : elles rendent l'échec propre, réparable et
visible. Aucune n'empêche l'antivirus de se méfier.

**Ce qui règle la cause racine, c'est la signature de code** — tu l'as mise hors sujet pour
aujourd'hui, et je respecte ça, mais le chiffre mérite d'être posé pendant qu'on y est : un
certificat OV coûte ~300–400 €/an et met **plusieurs semaines** à construire une réputation
SmartScreen ; un certificat EV, ~600 €/an, donne la réputation immédiatement. C'est le seul
levier qui agit sur les 5 joueurs de Defender **et** sur tous ceux qui n'ont jamais osé lancer
l'exe et dont on n'entendra jamais parler.

---

### Bilan

| ce que « terminé » demandait | résultat |
|---|---|
| Le compte réel, et depuis quand | **0** signalement direct — mais le zéro est un **angle mort d'instrument**, démontré. Mesurable à côté : **5 joueurs** (antivirus, 22–25/07), **2 joueurs** (mise à jour qui ne tient pas, 27/07). **Antérieur à la 3.4.0.** |
| Le message d'enquête | prêt, contournement en premier, avec la question qui permet à l'hypothèse de **tomber** |
| Les quatre chiffres d'UPX | **deux seulement, et c'est le résultat** : `upx=True` est inopérant depuis le début, l'exe publié n'est **pas** compressé. Piste abandonnée. |
| Le dossier de dépliage | **5 dossiers, 380 Mo**, tous **complets** ; un dépliage abandonné ne gêne pas le suivant ; **un dossier indisponible ne provoque pas la panne** (mesuré) |
| La reproduction | **non reproduite — et le pourquoi vaut mieux** : `python312.dll` est **verrouillée dès l'écriture**, un tiers ne peut pas la retirer pendant le chargement. Le mécanisme se resserre sur « l'écriture est empêchée » ou « l'exe entier est mis en quarantaine ». |
| Le plan chiffré, pièges nommés | 4 pistes, dont **2 à faire sans attendre l'enquête** ; le piège du témoin traité par un identifiant à usage unique |

**Trois choses que je n'avais pas prévues en commençant :**

1. **Nos deux gisements ne peuvent pas voir cette panne.** Les rapports sont produits par le
   Compagnon lui-même — l'échantillon est celui des machines où tout a marché. Un zéro qui ne
   veut rien dire, exactement la famille de mesures qu'on répare depuis une semaine.
2. **`upx=True` ne fait rien.** Trois programmes ont pu raisonner sur un compromis taille/détection
   qui n'existe pas. La vérification a coûté deux minutes ; construire la variante en aurait coûté
   dix pour rien.
3. **Le relais peut laisser un joueur sans Compagnon du tout.** Ce n'est pas ce qu'on cherchait,
   c'est plus grave que ce qu'on cherchait, et ça se répare sans rien savoir de l'antivirus.

**Ce qui attend ta décision :** poster le message du bloc 2 ; faire les pistes 1 et 2 tout de
suite ; et dire si tu veux le chiffre VirusTotal au prix d'un envoi du binaire.
