# L'add-on

Le code de l'add-on tel qu'il était dans la dernière version publiée (**3.5.1**, 18 août
2026).

## Ce qui est ici

- `AscensionFR/` — l'add-on : `Core.lua`, les modules (info-bulles, quêtes, sorts,
  interface, épreuves…), le `.toc` et les raccourcis.
- `AscensionFR_Repliques/` — l'add-on annexe qui traduisait les paroles des PNJ dans la
  fenêtre de discussion. **Seul son `.toc` est ici** : sa base était une reprise directe
  des textes français officiels de Blizzard, qui n'ont pas à être republiés.

## Ce qui n'est pas ici, et où le trouver

Les bases de données (`DB/DB_*.lua`, environ 110 Mo) ne sont pas archivées : ce sont des
fichiers **générés**, pas du code.

- pour les **relire ou les installer** : elles sont dans le zip de la version 3.5.1, sur
  [la page des versions](https://github.com/LePetitDan/AscensionFR/releases) ;
- pour les **régénérer** : elles se fabriquent depuis `../traductions/` avec
  `../chaine/outils/generateur_db.py`. La chaîne complète est décrite dans les
  `../programmes/`.

## À savoir si vous reprenez ce code

L'add-on est écrit pour **Lua 5.1** (la version du client 3.3.5a), qui refuse plus de
262 143 constantes par fonction : c'est pourquoi les grosses bases sont découpées en
« seaux » et chargées paresseusement. Le détail de ce piège, et des autres, est dans
`../traductions/GLOSSAIRE.md` et dans les programmes.
