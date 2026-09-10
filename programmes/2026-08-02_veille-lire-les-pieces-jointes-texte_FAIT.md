# Demande de code → Claude Code

# 📎 Que la veille lise les signalements déposés en pièce jointe

**Date :** 2026-08-02

---

## Le problème, en une phrase

Quand un joueur écrit un long signalement de traduction, Discord le transforme automatiquement
en pièce jointe `message.txt`. La veille écrit alors `[fichier : message.txt]` et **le contenu
n'est jamais lu**.

**Ce que ça coûte : 40 signalements de traduction non lus entre le 27/07 et le 07/08** (compteur
mis à jour le 07/08 — c'était 14 à l'écriture de cette demande, 23 le 03/08, 26 le 04/08).
Ce sont les retours les plus détaillés du projet — un joueur ne déclenche la pièce jointe
qu'en écrivant plus de 2 000 caractères. C'est le plus gros gisement de matière gratuite dont
on dispose.

⚠️ **Le rythme a changé d'ordre de grandeur** : 14 en 6 jours, puis **9 en un peu plus de 24 h**
(02/08 10 h 48 → 03/08 13 h 52), **3 en 22 h** (03/08 16 h 35 → 04/08 14 h 13), puis
**14 en 3 jours** (04/08 17 h 24 → 07/08 09 h 20), dont **9 pour la seule journée du 06/08**.
Chaque jour d'attente coûte de 3 à 9 signalements détaillés.

📌 **Point neuf du 07/08, à vérifier pendant le rattrapage** : au moins deux de ces pièces
jointes viennent de joueurs qui tournent sur une **version périmée installée à la main**
(un fichier s'appelle littéralement `AscensionFR_3.4.0.txt` alors que la 3.4.2 est sortie le
03/08). Une partie du gisement peut donc être des fautes **déjà corrigées**. Merci de me dire,
dans ta réponse, si le fichier porte la version du Hub — si oui, on pourra trier les
signalements périmés automatiquement au lieu de les relire à la main.

Les messages ne sont **pas perdus** : ils sont sur Discord, seulement non lus par l'outil.

---

## Objectif (le QUOI, pas le comment)

Que `WorkFlow/outils/aspirer_veille.py` **inclue le texte** d'une pièce jointe quand celle-ci est
un fichier texte, au lieu de n'écrire que son nom.

L'endroit exact : fonction `corps(m)`, autour de la ligne 370 —
la branche `return "[fichier : %s]" % pj.get("filename", "?")`.

**Puis relancer une passe de rattrapage** pour récupérer les 26 signalements déjà passés, sans
attendre le prochain démarrage du PC.

---

## Ce à quoi il faut faire attention

- **Ne télécharger que du texte, et petit.** Type `text/*` ou extension `.txt` / `.md` / `.log`,
  et une taille plafonnée (l'ordre de grandeur d'un `message.txt` Discord est ~2 à 20 Ko).
  Tout le reste garde le comportement actuel (`[image]`, `[vidéo]`, `[fichier : …]`).
- **Tronquer proprement** au-delà d'une limite raisonnable, avec une marque visible
  (`[… tronqué]`), pour qu'un fichier inattendu ne fasse pas exploser le rapport du jour.
- **Encodage : UTF-8 explicite, sortie console forcée en UTF-8.** Un accent mal décodé ou un
  emoji sur une console cp1252 tue la tâche planifiée en silence — c'est déjà arrivé.
- **Ne jamais laisser un échec réseau écraser des données.** Si le téléchargement échoue, écrire
  `[fichier : message.txt — non téléchargé]` et continuer : jamais d'exception qui interrompt la
  passe, jamais de fichier réécrit à vide.
- **Le rattrapage ne doit pas tout réécrire.** Les fichiers `AAAA-MM-JJ_nouveau.md` déjà rendus à
  Dan ne doivent pas être écrasés. Range le rattrapage dans un fichier à part
  (par ex. `RATTRAPAGE_pieces-jointes.md`) ou en append daté — à toi de voir, mais
  **ne casse pas le marque-page `_etat.json`.**
- **Ces fichiers gardent les pseudos** : `3-atelier/` est hors dépôt git, strictement local.
  Rien de tout ça ne part en public.

---

## « Terminé » veut dire

1. Un `message.txt` déposé dans 🐛-signalements apparaît **avec son texte** dans le rapport du jour.
2. Un fichier non textuel garde exactement son comportement actuel.
3. Une passe de rattrapage a été lancée et **les 40 signalements en attente sont lisibles**,
   avec leur date et leur salon.
4. `_etat.json` est intact : le prochain passage normal ne redonne pas d'anciens messages.
5. Tu me dis **combien** de pièces jointes ont été récupérées, et si certaines étaient autre chose
   que des signalements de traduction.

---

## Fichiers / dossiers concernés

- `WorkFlow/outils/aspirer_veille.py` (fonction `corps`, ~l. 370)
- `3-atelier/veille-discord/` (sortie ; `_etat.json` à ne pas abîmer)

---

## Validation

**Autonome.** Rien ne part en public, rien ne touche l'addon, le Compagnon ni aucune release.
C'est un outil de lecture interne.

---
## Réponse de Claude Code

**FAIT le 2026-08-09, dans le bloc A du programme 32** —
[`2026-08-08_PROGRAMME-32-solder-l-arriere_FAIT.md`](2026-08-08_PROGRAMME-32-solder-l-arriere_FAIT.md).

En bref : `aspirer_veille.py` lit désormais le texte des pièces jointes (`.txt`/`.md`/`.log`
≤ 200 Ko, tronqué à 8 000 caractères, échec réseau sans écrasement). Rattrapage
`--rattrapage 2026-07-26` → `RATTRAPAGE_pieces-jointes.md` (à part, `_etat.json` intact,
empreinte vérifiée). **52 messages, 48 pièces lues, 0 illisible, toutes des signalements.**
Oui, le fichier porte la version du Hub : **45 des 48 viennent d'une version périmée** (tri
automatique possible). La veille porte son `@@BILAN` (bloc C du 32). Détail complet dans le
programme 32.
