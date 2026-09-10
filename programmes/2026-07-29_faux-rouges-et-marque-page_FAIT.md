# Demande de code → Claude Code

# 🔧 Deux défauts trouvés au premier vrai passage de l'Atelier

**Date :** 2026-07-29 · court, bien diagnostiqué, sans risque

> **Le contrôle des codes retour du bloc E a fait son travail dès sa première utilisation
> réelle** : Dan a vu « 2 étapes en échec » au lieu d'un bandeau vert menteur. C'est grâce à
> lui qu'on tient les deux défauts ci-dessous. Mais l'un des deux est un **faux rouge**, et un
> faux rouge quotidien détruit la valeur du contrôle en une semaine.

---

## ① `aspirer_discord.py` — le marque-page est otage d'un hoquet réseau

**Ce que j'ai mesuré** (en lecture seule, depuis le conteneur, même jeton et même
User-Agent) :

- **100 messages en attente, 200 pièces jointes.** Le marque-page est figé sur un message du
  **27/07 à 10h** alors que des fichiers du **28/07 à 21h** sont déjà sur le disque.
- **199 pièces jointes sur 200 se téléchargent parfaitement.** Une seule a échoué
  (`caches_b52c27fc.json.gz`, message `1531263599283277874`) — et **réessayée, elle passe :
  3 fois sur 3, plus les deux du même message. C'était un hoquet, pas un fichier mort.**

**Le mécanisme.** Au premier échec, `rate = True` et le marque-page cesse d'avancer
(`dernier_complet`). L'intention est bonne — le commentaire explique très bien pourquoi : un
hoquet ne doit jamais faire sauter le rapport d'un joueur. **Mais il n'y a aucune nouvelle
tentative.** Sur 200 téléchargements successifs, il suffit d'un raté aléatoire pour que le
compteur reste bloqué **définitivement**, et que chaque passage rescanne les mêmes messages.
Le message « sera repris au prochain passage » est donc faux : il n'est jamais repris avec
succès si le hasard frappe à nouveau.

**Ce qu'il faut :**
- **Réessayer chaque téléchargement** (2 ou 3 fois, avec une courte pause) avant de le
  déclarer raté. Ça fait disparaître le cas qu'on vient d'observer.
- **Et pour le fichier vraiment mort** : au bout de N passages, le **consigner** et laisser le
  marque-page avancer — exactement la mécanique des `rejets_chroniques.json` que tu as posée
  au bloc E. Un fichier perdu est regrettable ; un compteur gelé pour toujours l'est plus.
- Le compte des réessais et des consignations doit **s'afficher**, pas se taire.

## ② `ingerer_rapport.py` — « rien à faire » n'est pas « ça a raté »

Trois `return 1` dans `main()`, et **deux d'entre eux ne sont pas des erreurs** :

| ligne | cas | ce que c'est vraiment |
|---|---|---|
| 243 | aucun fichier de rapport | légitime : rien à traiter |
| **307** | « Aucun « Échec d'alignement S » trouvé dans le rapport » | **rien à faire** |
| **337** | `if not lignes: return 1` | **rien à écrire** |

Avant le bloc E, personne ne lisait ces codes. Depuis, l'Atelier les honore — donc **un
passage parfaitement normal s'affiche en rouge**. C'est ce que Dan vient de voir.

**Ce qu'il faut :** distinguer **« rien à faire » (code 0, avec un message clair)** de
**« ça a raté » (code non nul)**.

## ③ Et surtout : la même confusion existe sûrement ailleurs

C'est le vrai travail de ce lot. **Passe en revue les six étapes de la chaîne** (et les outils
qu'elles appellent) et cherche partout le même défaut : un `return 1` / `sys.exit(1)` qui
signifie « il n'y avait rien à faire » plutôt que « quelque chose s'est mal passé ».

Le critère est simple : **si un passage sans nouveauté doit s'afficher en rouge, c'est un
bug.** Le contrôle des codes retour ne vaut que s'il ne crie jamais pour rien — c'est ta
propre phrase sur les bancs d'essai, appliquée à la chaîne.

## ④ Pendant qu'on y est : `sorts.json` mérite l'écriture atomique

Trois outils du dépôt écrivent déjà proprement — fichier temporaire, puis mise en place
(`aspirer_veille`, `construire_zip_release`, `paresseux_textes`). **Mais `traducteur_fr.py`
écrit `sorts.json` directement**, par un `json.dump` sur le fichier final.

C'est le fichier le plus précieux du projet, et une coupure au mauvais moment le laisse
tronqué. Dan a coupé l'Atelier hier soir — au bon moment par chance. Applique-lui la doctrine
que tu appliques déjà au zip : **on écrit à côté, on ne remplace qu'en cas de succès.**
Regarde si d'autres fichiers de `traductions/` sont dans le même cas.

---

**« Terminé » veut dire :**

> - L'aspiration réessaie, consigne les morts, et **le marque-page rattrape les deux jours de
>   retard** — dis-moi combien de rapports sont enfin ingérés.
> - `ingerer_rapport.py` ne crie plus quand il n'a rien à faire.
> - L'inventaire des autres `return 1` trompeurs de la chaîne, corrigés.
> - `sorts.json` (et ses voisins concernés) écrits atomiquement.
> - Un passage complet de l'Atelier **sans faux rouge**.
> - Rien de publié, rien de poussé.

**Validation :** autonome. 🛑 **Arrête-toi** si corriger un code retour change ce que la chaîne
*fait* et pas seulement ce qu'elle *dit*.

---
## Réponse de Claude Code
> (à remplir, puis renommer en `_FAIT.md`.)

### ✅ FAIT (29/07)

**Le marque-page a rattrapé son retard, et voici les chiffres.**

| | avant | après |
|---|---|---|
| marque-page | `1531239936853016676` (27/07 10 h) | `1531981398628368457` |
| rapports `.txt` | 2 306 | **2 951** (+645) |
| caches `.json.gz` | 2 242 | **2 876** (+634) |

Puis l'ingestion : **429 corrections de sorts ajoutées** à
`DB_SortsCorrections.lua` (compilé en lua51 : OK) et **627 fichiers de
caches lus → 5 009 textes de jeu versés à l'usine**. C'est deux jours de
contributions de joueurs qui étaient bloqués derrière un hoquet réseau.

**0 pièce en échec sur ce passage**, donc aucune consignation : le
registre `pieces_jointes_mortes.json` n'a même pas eu à être créé. Le
réessai n'a pas eu à servir aujourd'hui — je l'ai donc prouvé au banc
plutôt qu'en le racontant.

### ① L'aspiration

- **Réessais** : 3 tentatives espacées (1,5 s puis 4 s) par téléchargement.
- **Écriture atomique en prime** : on écrit dans un `.part` et on ne met
  en place qu'au succès. Un `.gz` tronqué par une coupure aurait été pris
  pour bon par l'ingestion — le défaut d'à côté, tant qu'on y était.
- **Consignation** : au bout de 3 passages en échec, la pièce entre dans
  `traductions/pieces_jointes_mortes.json` (avec l'erreur et la date),
  **cesse de retenir le marque-page**, et reste comptée à chaque passage.
  Exactement la mécanique des rejets chroniques du bloc E.
- **Le relevé m'a appris un troisième chemin** que ta note ne pouvait pas
  voir : `atelier_sante.json` montre `aspirer_discord.py` **code 1** au
  passage de 12 h 33 — l'échec n'était pas sur un téléchargement mais sur
  la **pagination** des messages. Un hoquet pendant `api_get` sortait en
  rouge sans rien avoir tenté. Réessayé aussi — mais **401/403/404 ne se
  réessaient jamais** (jeton, droits ou salon : insister n'y changerait
  rien), et un réseau vraiment mort sort proprement, en rouge, sans
  trace de pile.
- Réessais, rattrapages et consignations **s'affichent**, chiffrés.

### ② et ③ — l'inventaire des faux rouges

Passés au crible : les **7 étapes** de l'Atelier et les **10 outils**
qu'elles appellent. Verdict, site par site :

| Outil | Site | Verdict |
|---|---|---|
| `ingerer_rapport` | « Aucun Échec d'alignement trouvé » | **corrigé → 0** |
| `ingerer_rapport` | `if not lignes` | **corrigé → 0** |
| `moissonner_echecs` | `if not lignes` | **corrigé → 0** (même défaut, trouvé par l'inventaire) |
| `ingerer_rapport` | aucun fichier de rapport | gardé à **1** — c'est une anomalie d'installation, pas un passage à vide |
| `aspirer_discord` | config absente / 401 / 403 / 404 | gardés à **1** |
| `generateur_sorts` | saturation Lua 5.1 | gardé à **1** |
| `generateur_db` | bases pas au contenu du jour | gardé à **1** |
| `optimiser_memoire` | format inattendu | gardé à **1** |
| `generer_noms_sorts` / `_objets` | pose paresseuse ratée | gardés à **1** |
| `traduire_gisement`, `recuperer_db` | source ou arguments manquants | gardés à **1** (outils manuels) |
| `ingerer_recolte`, `ingerer_caches`, `appliquer_vocabulaire`, `traducteur_fr` | — | **déjà corrects** |

`traducteur_fr.py` n'a **aucune** sortie non nulle : il ne peut être rouge
que sur une vraie exception. C'est bien.

### ④ L'écriture atomique

Nouveau module `outils/ecriture_sure.py` (`ecrire_json` / `ecrire_texte`) :
fichier `.part`, `flush` + `fsync`, puis `os.replace`. Le nettoyage attrape
`BaseException` — un Ctrl+C au milieu du `dump` est précisément le cas à
couvrir.

Branché là où ça compte : **`traducteur_fr.sauver_json`**, par où passent
TOUS les stores de la chaîne (dont `sorts.json`, réécrit toutes les 200
traductions pendant des heures), et **`appliquer_vocabulaire`**, l'étape 6,
qui réécrit les stores eux-mêmes. Une coupure laisse désormais soit
l'ancien fichier intact, soit le nouveau complet.

### Le banc, pour que ça ne revienne pas

`outils/verifier_aspiration.py` — 8 assertions, sans réseau ni écriture
dans le dépôt (faux `urlopen`, dossier temporaire) : les réessais de
téléchargement et d'API, l'abandon propre sans `.part` résiduel, le 403
qui ne se réessaie pas, et les deux codes retour (« rien à faire » → 0,
« pas d'installation » → 1). **8/8.** Enrôlé au banc de santé, qui est
lui-même la deuxième barrière du build.

### Un rouge qui reste, et c'est normal

Le banc de santé affiche **1 ROUGE : atelier** — c'est le relevé fidèle
du passage de 12 h 33, celui qui a révélé ces deux défauts. Je ne l'efface
pas : ce serait peindre un vert par-dessus l'histoire. **Il s'effacera de
lui-même au prochain passage de l'Atelier chez toi**, où les 7 étapes
sortiront en 0 — je les ai toutes vérifiées aujourd'hui, une par une.

Rien n'a été publié, rien n'a été poussé.
