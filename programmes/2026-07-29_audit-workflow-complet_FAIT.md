# Demande de code → Claude Code

**Date :** 2026-07-29 · **AUDIT — la chaîne complète : est-ce que tout marche vraiment ?**

> ⏳ **À faire après le lot 14 et le Hub.** C'est un audit, pas une correction : il ne
> modifie rien. Prends le temps qu'il faut, Dan a levé l'urgence de sortie.

---

## L'intention de Dan, dans ses mots

> « L'addon doit traduire **l'entièreté du jeu et de tous les royaumes** en français. Pour
> que ça aille plus vite, il **récupère tout l'anglais que croise un joueur** — PNJ, textes
> de PNJ, quêtes, noms, sorts, descriptions, info-bulles, objets, interface, panneaux
> d'affichage, et j'en oublie sûrement. Bref : tout ce que croise un joueur, et il l'envoie
> en rapport sur Discord. Ensuite mon PC récupère les rapports, les analyse, voit ce qui est
> utile ou s'il y a des doublons, traduit tout ça, et le réinjecte. »

**La question de l'audit : est-ce que ça marche, vraiment, à chaque maillon ?**
Et non « est-ce que le code a l'air correct » — est-ce que la matière circule.

---

## Partie A — La couverture : ce que le joueur voit vs ce qu'on attrape

C'est le chiffre qui manque au projet depuis le début. On mesure du **volume**
(1 272 596 champs traduits) et jamais de la **couverture**.

**Ce que je te demande : une matrice, une ligne par catégorie de texte que le joueur voit à
l'écran.** À toi d'établir la liste exhaustive — celle de Dan est un point de départ, pas une
limite. Pour chaque catégorie, quatre colonnes :

| catégorie | 1. récoltée ? | 2. traduite ? | 3. affichée ? | 4. combien reste en anglais |
|---|---|---|---|---|

- **récoltée** : l'addon capture-t-il ce texte quand un joueur le croise, et part-il dans un
  rapport ?
- **traduite** : la matière arrive-t-elle jusqu'à `traductions/` et en ressort-elle traduite ?
- **affichée** : le français revient-il **à l'écran** ? (« être dans la base ≠ s'afficher » —
  la seule preuve valable est le moteur rejoué, pas la lecture d'un fichier.)
- **combien** : un ordre de grandeur chiffré du reste en anglais.

Catégories déjà connues comme non couvertes, à confirmer et chiffrer plutôt qu'à
redécouvrir : **gameobjects** (portes, caisses — couche distincte), **GlobalStrings**
(coupées par la doctrine taint), **courrier**, **panneau de réputation**, **monnaies**,
**texte de combat flottant**, **astuces des écrans de chargement**, **plaques de noms /
noms de mobs**, **talents CoA**, **onglet Épreuves**, **noms de quêtes dans le chat**.

**Le livrable qui compte : les trois plus gros trous, chiffrés.** C'est ce qui décidera des
versions suivantes.

## Partie B — La chaîne : où ça fuit

Sept maillons. Pour chacun : **est-ce qu'il marche, et comment le sait-on ?**

1. **La récolte en jeu** — l'addon capture-t-il tout ce qu'il croise, ou seulement certains
   types ? Y a-t-il des captures silencieusement jetées ? *(Rappel : le filtre anti-bruit de
   `Tooltips.lua:329-345` rend 3 416 modèles sur 47 876 invisibles au journal.)*
2. **L'envoi du rapport** — 🔴 **c'est le maillon le plus inquiétant.** Deux joueurs ont
   signalé que l'envoi depuis le Hub **ne marche pas**, sur Windows 11 natif **et** sur
   Linux — pas seulement sous Wine. Si c'est vrai, l'alimentation du projet est coupée pour
   une partie des joueurs, et on ne le voit pas. **À reproduire et à chiffrer en priorité.**
3. **Le webhook Discord** — panne silencieuse déjà vécue le 19/07 (webhook vide, bouton
   masqué, plus rien n'arrive, aucun message d'erreur). Le contrôle existe dans
   `verifier_tout.py` : suffit-il ?
4. **L'aspiration** (`aspirer_discord.py --ingerer`) — tout ce qui arrive est-il aspiré ?
   *(Rappel : 125 rapports téléchargés non ingérés, trouvés le 26/07. Combien
   aujourd'hui ?)*
5. **L'ingestion et le tri** (`ingerer_rapport.py`, `ingerer_recolte.py`, `ingerer_caches.py`)
   — les doublons sont-ils bien écartés ? le bruit est-il filtré ? *(Rappel : **282 entrées
   de file sans aucun texte source**, requeuées à chaque cycle.)*
6. **La traduction** (l'Atelier, `traducteur_fr.py`) — que devient un texte qui échoue ?
   est-il retenté, ou perdu en silence ?
7. **La réinjection et la publication** — la chaîne standard fait-elle bien **tous** ses
   maillons ? *(Rappel : le pont des noms n'était régénéré par aucun chemin, trouvé au
   lot 10 à trois endroits.)*

**Pour chaque maillon, la même question : si ce maillon tombe en panne demain, est-ce que
ça se voit ?** Une panne silencieuse est plus grave qu'une panne bruyante — ce projet en a
déjà eu quatre.

## Partie C — Ce que tu améliorerais

Tu connais ce pipeline mieux que quiconque maintenant. **Dis-moi les trois choses que tu
referais autrement**, avec pour chacune : le gain attendu, le coût, et le risque.

**Dan a été explicite : « s'il faut recréer les outils sur mon PC, aucun problème. »** Ne te
limite pas à des rustines si le bon geste est de réécrire un maillon.

Deux points sur lesquels il a déjà tranché, à intégrer :
- **« Une mise à jour doit être irréprochable. »** Quels contrôles manquent encore avant
  publication ?
- **« Une mise à jour = un numéro, le Hub porte toujours le même numéro que l'addon. »**
  Vérifie que rien dans la chaîne ne permet plus de s'en écarter.

---

**« Terminé » veut dire :**

> - La matrice de couverture, catégorie par catégorie, avec les **trois plus gros trous
>   chiffrés**.
> - Les sept maillons passés en revue, chacun avec sa preuve de bon fonctionnement — ou son
>   défaut, chiffré.
> - Le sort du point B.2 (envoi impossible sous Win11 natif et Linux) : reproduit ou écarté,
>   avec la raison.
> - Tes trois propositions d'amélioration, chiffrées.
> - **Aucune modification.** C'est un audit. Écris le rapport dans
>   `rapports/audit_chaine_2026-07.txt`, et le résumé dans ta réponse ici.

**Validation :**

> Entièrement autonome — rien n'est modifié. **Préviens-moi si l'audit dépasse une demi-
> journée** : on le découpera plutôt que de le bâcler.

---
## Réponse de Claude Code

**Audit réalisé le 28/07/2026, lecture seule, rien n'est modifié.** Le
rapport complet — matrice détaillée, chiffres sourcés un par un, les
pannes silencieuses maillon par maillon — est dans
`rapports/audit_chaine_2026-07.txt`. Voici l'essentiel.

### 🔴 B.2 d'abord — l'envoi de rapport : ÉCARTÉ comme panne générale, mesure à l'appui

J'ai recompté le flux entier : **1 948 rapports reçus du 18 au 27/07**, en
croissance constante (27 → 447/jour, record le 26/07), et **depuis le 25/07
les rapports envoyés par le Hub 3.3.x dominent** (403 sur 447 le 26/07) —
l'envoi fonctionne, Windows 11 compris. Les deux signalements (Kalreg sous
Wine, Edward sous Win11) datent du **24/07, avant la sortie du Hub** : ils
tournaient sur des Compagnon v2, dont le message « Envoi impossible »
couvre toute exception sans dire la cause. Le jour même, 225 rapports
arrivaient. Cause la plus probable : **un exe d'avant le 19/07**, jour où
le jeton du webhook a été régénéré — tout exe antérieur poste vers un
webhook mort, panne identique sur toutes plateformes. Le vrai trou que ce
cas révèle : un échec d'envoi chez un joueur est invisible côté usine, et
rien ne surveille le webhook entre deux builds.

### La matrice de couverture — et les trois plus gros trous

22 catégories passées en revue (tableau complet dans le rapport). Les
trois trous qui commandent la suite :

1. **L'affichage, pas la matière** : 1 091 sorts prouvés anglais à l'écran
   malgré leur français en base (banc moteur rejoué aujourd'hui sur la
   population entière — décomposition : 546 limites moteur dont 457
   « structure ok », 472 hors cache dont **367** faux appariements, 54
   trop courts, 18 réparables, 1 divergent) + **le constructeur CoA
   entier : 3 931 français en base pour 3 949 talents, zéro preuve
   d'affichage**. → blocs 4 et 5.
2. **Les textes de PNJ** : ~2 600 manquants en base (2 200 TextesPNJ +
   400 gossip) — la seule catégorie cœur à trou de matière, qui ne
   progresse qu'à la vitesse de la récolte.
3. **Les catégories sans module** : courrier (170 modèles, FR déjà dans
   PackFR), réputation (391 factions), monnaies, journal de combat,
   ERR_QUEST_* du chat, 330 points de vol. → bloc 10. **Deux corrections
   au programme** : les *gameobjects* sont en fait DÉJÀ couverts (24 588
   entrées consommées par Plaques/Core), et les *astuces de chargement*
   sont doublement inaccessibles (gisement introuvable dans toutes les
   sources extraites + les addons ne tournent pas pendant l'écran de
   chargement) — à retirer de la liste du bloc 10.

### Les sept maillons — verdict en une ligne chacun

1. **Récolte** : vivante mais filet étroit et muet — 14 points de capture ;
   le filtre anti-bruit recompté à **3 520/47 620** modèles invisibles au
   journal (le trou du programme, confirmé) ; purge de la récolte à chaque
   mise à jour ; « première capture gagne » ; plafond 200 silencieux.
2. **Envoi** : vivant, mesuré (ci-dessus).
3. **Webhook** : le contrôle existe et il est VALIDE aujourd'hui — mais il
   **ne mord pas** (l'exit de verifier_tout reste 0 même webhook mort).
4. **Aspiration** : **pas planifiée** (aucune tâche Windows pour les
   rapports), dernière prise 27/07 12:03 — 27 h de retard au moment de
   l'audit, sans signal. Doublons : 0 sur 3 839 fichiers (prouvé).
5. **Ingestion** : propre aujourd'hui (0 jamais-ingéré, registre en
   bijection) ; **279** entrées Name=="" requeuées à chaque cycle (le
   « 282 » du programme, recompté) ; un rapport malformé est marqué ingéré
   avant d'être lu, jamais retenté, code 0.
6. **Traduction** : le circuit retente bien les échecs, MAIS les **entrées
   partielles ne sont jamais retentées** (mi-anglais permanent) ; 293 des
   300 entrées de la barre sont insolubles (bruit qui masquerait une vraie
   panne) ; **le moteur principal ignore le glossaire** (les arbitrages ne
   gouvernent que 2 étapes sur 6) ; **l'Atelier ignore les codes retour de
   ses 6 étapes** — un crash peut finir sur un bandeau vert.
7. **Réinjection/publication** : le plus solide (lot 10 bouché 3/3,
   garde-fous de release qui mordent, doctrine verrouillée sur le chemin
   scripté). Quatre trous : **9 bases jamais régénérées** par la chaîne
   (dont DB_LuesClient, l'anti-taint) ; **42 % du zip publié est un
   dossier de sauvegarde mort** (DB_sauvegarde_build, 19,5 Mo, déjà livré
   en 3.3.0) ; deux contournements de la doctrine subsistent (gh manuel —
   encore proposé par le README —, et empaqueter.py sans gardes) ;
   verifier_addon (le seul test d'EXÉCUTION) n'est enforced nulle part.

### Mes trois propositions (détail chiffré dans le rapport)

1. **Un banc de santé qui mord** : un script unique — banc moteur sorts
   population entière avec seuil (21 s), codes retour des 6 étapes de
   l'Atelier, webhook dans l'exit, fraîcheur d'aspiration, verifier_addon
   — branché sur construire_zip_release. *Gain : la quinzaine de pannes
   silencieuses recensées devient bruyante. Coût : ~1 jour. Risque :
   faible.*
2. **Purger le poids mort** : DB_sauvegarde_build hors du zip (−42 %),
   garde « contenu du zip vs .toc », Name=="" filtrées (bloc 2d), liste
   d'écartés persistée, reprise des entrées partielles champ par champ.
   *Gain : compteurs lisibles, zip 2× plus léger. Coût : ½ jour. Risque :
   faible, sauf la reprise des partielles (mesure à blanc d'abord).*
3. **Brancher le vocabulaire arbitré sur le moteur principal** (le
   mécanisme du glossaire existe déjà dans traduire_gisement.py) et faire
   d'appliquer_vocabulaire une étape de l'Atelier. *Gain : les arbitrages
   de Dan gouvernent 100 % du flux. Coût : ~1 jour. Risque : moyen — on
   touche au moteur, comparaison avant/après population entière
   obligatoire.*

Sur les deux points déjà tranchés : la doctrine « un numéro » est
verrouillée sur le chemin scripté, il reste le gh manuel et empaqueter.py
à neutraliser ; les contrôles qui manquent encore à « une mise à jour
irréprochable » sont listés au maillon 7 du rapport.
