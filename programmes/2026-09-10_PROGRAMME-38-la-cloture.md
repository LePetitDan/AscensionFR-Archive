# Demande de code → Claude Code

# 🗄️ PROGRAMME 38 — la clôture

**Date :** 2026-09-10
**Le dernier.** Ascension a fermé le 5 septembre. Le projet s'arrête, et ce programme le
range proprement : une archive publique qui rassemble tout, les anciens dépôts gelés, les
données des joueurs supprimées, la machine éteinte, les secrets révoqués.

**Ce n'est pas un programme de développement. C'est un programme de rangement.** Rien à
réparer, rien à améliorer. Fais les choses dans l'ordre et vérifie chaque geste, parce que
plusieurs sont irréversibles.

**L'état au 10/09 :**

| | |
|---|---|
| dépôts publics | `AscensionFR` (10 ★, 6 forks), `-Textes`, `-Voix`, `-Confort`, `-Equipement`, `-Peche` |
| dépôts privés à traiter | `AscensionFR-Usine`, `AscensionFR-Moisson` |
| la nuit | **elle tourne encore** — 11 passages depuis la fermeture, sur un Discord mort |

---

## BLOC A — construire l'archive

Un dépôt neuf, **public**, `AscensionFR-Archive`. Il devient la porte d'entrée du projet.

**Ce qu'il contient :**

```
README.md                 ← le texte est au bloc C, à relire par Dan avant publication
traductions/              ← les 40 stores vivants (~59 Mo) + GLOSSAIRE.md
addon/                    ← la source de l'addon (depuis depot_github)
compagnon/                ← la source du Hub
chaine/                   ← outils/ + traducteur_fr.py : comment c'était fabriqué
programmes/               ← les 65 .md de 2-pour-Claude-Code, la mémoire du projet
```

🛑 **Ce qui n'y entre sous aucun prétexte :**

- **les données des joueurs** — `3-atelier/` (veille Discord, rapports, pseudos),
  `rapports/`, `noms_recolteurs.local.txt`, tout ce qui vient du pont Moisson ;
- **les secrets** — `discord_aspirateur.json`, `assets/webhook.local.txt`, tout jeton ;
- ⚠️ **`sources/` et `cache_db/`** — ce sont des **extractions du client d'Ascension**
  (MPQ/DBC), donc des données de jeu qui ne nous appartiennent pas. Les traductions
  publiées, c'est une chose ; republier les fichiers du jeu en est une autre, et vu ce qui
  vient d'arriver à Ascension, ce n'est pas le moment. **Exclus-les.**
- les 609 Mo de sauvegardes `_avant_*`, `a_traduire/`, l'historique git de `WorkFlow`.

**Dépôt neuf, sans historique** — un instantané propre, comme au programme 33. L'historique
de `WorkFlow` reste local chez Dan.

---

## 🛑 BLOC B — le garde-fou, sa dernière mission

`banc_secrets.py --arbre` connaît les webhooks, les chemins personnels de Dan, et les noms
de récolteurs déclarés. **Il passe sur l'archive complète AVANT le premier push**, et son
feu vert est la condition du push — pas une vérification d'après.

- **fais-le tourner, et donne le compte** : combien de fichiers balayés, combien de cas ;
- ⚠️ **et vérifie qu'il mord encore** avant de lui faire confiance : glisse un faux secret
  dans un fichier de l'arbre, montre le refus, retire-le. C'est la règle de la maison depuis
  le 16, et c'est la dernière fois qu'on l'applique ;
- **balaie aussi à la main** ce que le banc ne connaît pas : cherche des adresses e-mail,
  des chemins `C:\Users\<utilisateur> ou `D:\`, et des identifiants Discord dans ce qui va partir.

---

## BLOC C — publier l'archive

**Le README — texte proposé, à faire relire par Dan avant de pousser :**

> # AscensionFR — archive
>
> Traduction française communautaire de **Project Ascension** (World of Warcraft 3.3.5a),
> de juillet à septembre 2026.
>
> **Le projet est terminé.** Les royaumes d'Ascension ont fermé le 5 septembre 2026, à la
> suite d'un accord entre Ascension et Blizzard. Ce dépôt est un instantané figé : il n'est
> plus maintenu et ne recevra pas de correctifs.
>
> ## Ce qu'il y a dedans
>
> - **`traductions/`** — **1 374 783 textes français** : quêtes, objets, sorts, dialogues,
>   pages de livres lisibles en jeu, messages système et d'interface. Plus le glossaire des
>   arbitrages de vocabulaire.
> - **`addon/`** — l'add-on qui affichait tout ça en jeu.
> - **`compagnon/`** — le Hub d'installation (Windows et Linux).
> - **`chaine/`** — l'usine de traduction : aspiration des rapports de joueurs, traduction,
>   garde-fous de format, génération des bases.
> - **`programmes/`** — les 65 documents de conception, dans l'ordre. C'est le journal de
>   bord du projet, erreurs comprises.
>
> ## Si vous traduisez un autre serveur
>
> **L'essentiel de ces traductions n'est pas spécifique à Ascension.** Ce sont les textes de
> World of Warcraft 3.3.5a — les mêmes sur n'importe quel serveur de la même version. Si
> vous montez une traduction française pour un serveur WotLK, vous pouvez repartir d'ici
> plutôt que de zéro. Ce qui est propre à Ascension (système sans classes, sorts maison)
> est minoritaire et identifiable.
>
> ## Ce qui n'est pas dedans
>
> Les rapports des joueurs, les pseudonymes et toute donnée personnelle collectée pendant le
> projet ont été supprimés et ne sont pas archivés. Les fichiers extraits du client de jeu
> non plus.
>
> ## Merci
>
> À tous ceux qui ont envoyé des rapports, corrigé des traductions, signalé des bugs et
> soutenu le projet. Il n'aurait pas existé sans eux.
>
> *Les add-ons `AscensionFR-Confort` et `AscensionFR-Equipement` sont des forks du travail de
> **ProfetGit** (licence MIT, avec son accord) et conservent leurs dépôts et leur licence
> propres.*

- pousse l'archive une fois le bloc B vert ;
- **relis-la depuis l'extérieur** : ouvre la page publique, vérifie que le README s'affiche,
  que les traductions sont là, et qu'aucun fichier de la liste interdite n'est passé.

---

## BLOC D — geler les anciens dépôts (ne pas supprimer)

Pour les **six dépôts publics** : ajoute en tête de chaque README une ligne disant que le
projet est terminé, avec le lien vers l'archive — **puis** passe chaque dépôt en lecture
seule (Settings → Archive this repository).

⚠️ **Ne les supprime pas**, et voici pourquoi :

- `AscensionFR` porte **toutes les releases**. Chaque lien de téléchargement posté dans
  Discord depuis juillet pointe dessus ;
- `Confort` et `Equipement` sont des **forks du travail de ProfetGit** sous MIT, avec son
  accord. Ils gardent leur dépôt, leur licence et son attribution.

*(L'archivage GitHub est réversible — un dépôt gelé peut être réactivé. C'est le geste sûr.)*

---

## BLOC E — supprimer les privés, éteindre la nuit

- 🛑 **`AscensionFR-Moisson`** : il porte des noms de personnages de joueurs et n'a plus
  d'objet. **Supprime-le.** Le clone local aussi ;
- **`AscensionFR-Usine`** : récupère d'abord ce qui manquerait à l'archive (la chaîne, les
  stores dans leur dernier état), **puis supprime-le**. Sa suppression éteint la tâche
  nocturne par la même occasion — c'est la façon la plus propre de l'arrêter ;
- ⚠️ **avant de supprimer l'Usine, compare ses stores à ceux de l'archive.** Si le cloud a
  traduit quelque chose que le local n'a pas, c'est maintenant ou jamais. Dis le résultat de
  la comparaison ;
- `essai-cadence` traîne aussi, avec « sera supprimé » dans sa description. À toi de voir.

**Ces suppressions sont définitives. Fais-les en dernier, après que l'archive est en ligne
et vérifiée.**

---

## BLOC F — révoquer les secrets

Plus personne ne joue : révoquer ne casse plus rien.

- **le webhook Discord** (celui de `compagnon.py`, gardé depuis le 34 pour ne pas casser le
  bouton « Envoyer ») — Dan le supprime côté Discord ;
- **le jeton du bot `AspirateurFR`** — une fois que plus aucun outil n'en a besoin. Dis-lui
  à quel moment exactement il peut le faire sans rien casser ;
- **les GitHub Secrets** de l'Usine partent avec le dépôt.

Prépare la liste exacte des gestes de Dan, dans l'ordre, avec où cliquer.

---

**« Terminé » veut dire :**

> - **L'archive publique en ligne**, README relu par Dan, vérifiée depuis l'extérieur, et
>   **zéro donnée joueur, zéro secret, zéro fichier de client** dedans — avec le compte du
>   balayage et le garde-fou **vu mordre** une dernière fois.
> - **Les six dépôts publics gelés**, chacun avec son renvoi vers l'archive.
> - **Les deux privés supprimés**, après comparaison des stores — et **la nuit éteinte**.
> - **La liste des gestes de Dan** pour les secrets, dans l'ordre.
> - Ce qui a résisté, et ce que tu as failli casser.

---

🛑 **Dernier mot.** Ce programme supprime des choses pour de bon. Si un doute apparaît à
n'importe quel moment — un fichier dont tu n'es pas sûr, un dépôt dont tu ne sais pas s'il
sert encore — **arrête-toi et demande**. Il n'y a aucune urgence : le projet est déjà fini.

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Puis renommer en `_FAIT.md`.)
