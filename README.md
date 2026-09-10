# AscensionFR — archive

Traduction française communautaire de **Project Ascension** (World of Warcraft 3.3.5a),
de juillet à septembre 2026.

**Le projet est terminé.** Les royaumes d'Ascension ont fermé le 5 septembre 2026, à la
suite d'un accord entre Ascension et Blizzard. Ce dépôt est un instantané figé : il n'est
plus maintenu et ne recevra pas de correctifs.

## Ce qu'il y a dedans

- **`traductions/`** — **639 474 textes français** (soit près de **1 375 000 champs** une
  fois servis en jeu, une fiche de sort en comptant quatre) : quêtes, objets, sorts,
  dialogues, pages de livres lisibles en jeu, messages système et d'interface. Plus le
  glossaire des arbitrages de vocabulaire, dans
  [`traductions/GLOSSAIRE.md`](traductions/GLOSSAIRE.md).
- **`addon/`** — l'add-on qui affichait tout ça en jeu.
- **`compagnon/`** — le Hub d'installation (Windows et Linux).
- **`chaine/`** — l'usine de traduction : aspiration des rapports de joueurs, traduction,
  garde-fous de format, génération des bases.
- **`programmes/`** — les 66 documents de conception, dans l'ordre. C'est le journal de
  bord du projet, erreurs comprises.

## Si vous traduisez un autre serveur

**L'essentiel de ces traductions n'est pas spécifique à Ascension.** Ce sont les textes de
World of Warcraft 3.3.5a — les mêmes sur n'importe quel serveur de la même version. Si
vous montez une traduction française pour un serveur WotLK, vous pouvez repartir d'ici
plutôt que de zéro. Ce qui est propre à Ascension (système sans classes, sorts maison)
est minoritaire et identifiable.

Commencez par [`traductions/GLOSSAIRE.md`](traductions/GLOSSAIRE.md) : il donne les
arbitrages de vocabulaire, les conventions, et les pièges que ce projet a payés.

## Ce qui n'est pas dedans

Les rapports des joueurs, les pseudonymes et toute donnée personnelle collectée pendant le
projet ont été supprimés et ne sont pas archivés. Les fichiers extraits du client de jeu
non plus — polices comprises.

Concrètement, avant publication : les annonces d'événements et les journaux de jeu où le
client avait inséré des noms de personnages ont été retirés en bloc (5 093 entrées), les
textes de quête où un prénom s'était figé à la place de la variable `$n` ont été réparés,
et les pseudonymes cités dans le code ou les documents ont été masqués. Les formes propres,
celles qui portent `$n`, sont conservées : elles valent pour n'importe quel serveur.

Une réserve, parce qu'elle est honnête : dans un texte narratif, un prénom de personnage
inséré par le client est *typographiquement identique* à un nom de personnage non joueur.
Il peut donc en subsister. Si vous en repérez un, ouvrez un ticket — il sera retiré.

Les bases de données compilées de l'add-on (les `DB_*.lua`, 110 Mo) ne sont pas non plus
ici : elles se régénèrent depuis `traductions/`, et la dernière version publiée reste
téléchargeable sur
[la page des versions](https://github.com/LePetitDan/AscensionFR/releases).

## Merci

À tous ceux qui ont envoyé des rapports, corrigé des traductions, signalé des bugs et
soutenu le projet. Il n'aurait pas existé sans eux.

*Les add-ons `AscensionFR-Confort` et `AscensionFR-Equipement` sont des forks du travail de
**ProfetGit** (licence MIT, avec son accord) et conservent leurs dépôts et leur licence
propres.*
