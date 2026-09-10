# Demande de code → Claude Code

# 🚀 PROGRAMME 24 — sortir la 3.4.2

**Date :** 2026-08-03
**Dan a donné le GO.** Tetardtek a confirmé sur son bureau : le bouton « Vérifier mon
installation » s'ouvre avec son contenu, le symptôme a disparu. **Le seul trou du programme 23
est bouché.**

🛑 **C'est le programme irréversible.** Une release publiée est vue immédiatement par les Hubs
installés, qui proposent la mise à jour tout seuls. Pas d'essai à blanc, pas de retour en
arrière propre.

---

## 🛑 BLOC 0 — ce qu'on ne fait PAS dans cette version

**On ne fusionne pas la PR #5.** Elle est prête, éprouvée, et Tetardtek a cartographié les
cinq collisions — mais deux chantiers sur le chemin de la mise à jour dans la même version,
c'est exactement ce qui a coûté cher les 25-28/07. **C'est ton propre avis au programme 23 ;
je le suis.**

Et il y a une raison qui va au-delà de la prudence : **sa PR ne peut être éprouvée en vrai que
si la 3.4.2 existe.** Il s'est construit un binaire Linux 3.4.1 avec sa PR dedans ; le jour où
cette release sort, il est la seule machine au monde capable de faire cette mise à jour
automatiquement. **Publier la 3.4.2 est ce qui rend son essai possible.**

---

## BLOC A — fusionner, et vérifier ce qu'on fusionne

- fusionne `programme-23-plantage-visible` dans `main` ;
- **retire l'échafaudage** s'il en reste (déclencheur de test, marqueurs de commit) — tu l'as
  écrit toi-même : « un échafaudage qu'on oublie devient une porte » ;
- `verifier_arbre_publie.py` et `balayer_secrets.py` **verts après la fusion** ;
- push vérifié : `git rev-list --count origin/main..main` = **0**.

### 🛑 Une vérification que je te demande explicitement

Tetardtek signale, dans son commentaire n°4 sur la PR #5, un défaut de **repli** sur
`CONFIG_DIR` : *« expanduser rend « ~ » tel quel… et on fabriquait alors un dossier réellement
nommé « ~ » »*.

**Va lire ce que fait le repli dans le code qui va partir.** Si ce défaut est dedans, il part
chez 274 personnes. Si tu le corriges, corrige **le repli seul** — le choix du dossier de
configuration est dans sa PR, on n'y touche pas ici.

---

## BLOC B — construire les trois artefacts

L'add-on, l'exe Windows, **et le binaire Linux**.

🛑 **Le nom de l'asset Linux doit être RIGOUREUSEMENT identique à celui de la `v3.4.1`** —
`AscensionFR_Hub-linux-x86_64`. Deux raisons, et les deux sont dures :

1. c'est ce nom que cherche le binaire d'essai de Tetardtek ; un nom différent et son épreuve
   ne prouve rien ;
2. c'est ce nom que cherchera la mise à jour automatique Linux quand elle arrivera. **Un nom
   d'asset qu'on renomme une fois se renomme pour toujours.**

**Va lire les noms réellement servis par la `v3.4.1` avant d'envoyer quoi que ce soit**, comme
au programme 16. Idem pour les deux assets Windows : mêmes noms, sinon la mise à jour de tout
le monde casse en silence.

Le binaire Linux se construit par le workflow, en mode distribution — **Dan devra approuver.**
Dis-lui quand cliquer.

---

## 🛑 BLOC C — la release

**Cette fois c'est une vraie nouvelle version** : les 274 Hubs Windows la proposeront. C'est
voulu, et voici pourquoi — c'est ce que la note de version doit dire, dans cet ordre :

1. **quand quelque chose rate, le Hub le dit maintenant.** Avant, un plantage ne laissait
   aucune trace : le joueur cliquait et il ne se passait rien ;
2. **le bouton « Copier mon rapport » existe enfin.** Le Hub le promettait depuis toujours dans
   son message d'erreur, sans qu'il existe — et il copiait le mauvais texte ;
3. **sept endroits pouvaient planter** ; ils sont tous protégés.

Ne parle pas de « support Linux » comme argument pour eux : ce n'est pas de leur ressort.

### Les pièges, tous documentés

1. **`gh release create` n'a aucun mode simulation.** Le lancer *crée* la release.
2. **Ne supprime JAMAIS un tag.** La release repasse en brouillon, ses assets tombent en 404,
   `latest` recule — et chaque Hub installé propose une mise à jour **vers l'arrière**. En cas
   d'erreur on **déplace** le tag en `--force`.
3. **Tout essai est créé en PRÉ-VERSION**, sinon il devient `latest`.
4. **L'encodage de la console Windows** a tué `publier_github.py` à la 3.4.0. Si ça se
   reproduit, note l'erreur exacte et ne compose pas un titre au jugé.

---

## BLOC D — vérifier depuis l'extérieur, sans se faire confiance

- `releases/latest` sert bien **v3.4.2** ;
- **les trois assets** présents, bons noms, bonnes tailles ;
- `raw.githubusercontent.com/…/v3.4.2/compagnon/compagnon.py` porte bien la nouvelle version
  **et** `WEBHOOK_RAPPORTS = ""` ;
- les releases **3.3.0 / 3.3.1 / 3.4.0 / 3.4.1** ont toujours leurs assets — **et la `v3.4.1`
  a toujours son binaire Linux**, c'est celui que Tetardtek fait tourner ;
- **télécharge l'exe et le binaire Linux depuis les liens publics, recalcule leurs empreintes**,
  compare à ce qu'on a construit. C'est la seule preuve que les joueurs reçoivent ce qu'on a
  fabriqué.

> ⚠️ N'utilise pas la page `/releases` pour vérifier : elle se rend en JavaScript et elle a
> déjà fait annoncer un état faux. Et `raw.githubusercontent.com` t'a menti au programme 22 sur
> un état qui venait de changer — **pour ce qui vient de bouger, l'API.**

---

## BLOC E — ce qu'il reste à faire dire

Écris-moi, séparément du rapport :

- **le corps de la note de version**, prêt à coller ;
- **ce qui change pour un joueur Windows**, en trois lignes de français simple — je m'en sers
  pour l'annonce Discord ;
- **ce qu'il faut dire à Tetardtek** pour qu'il lance son épreuve : le tag, le nom exact de
  l'asset Linux, et son empreinte.

🛑 **Aucune fusion de la PR #5. Aucun tag autre que `v3.4.2`.**

---

**« Terminé » veut dire :**

> - La branche fusionnée, l'échafaudage retiré, les garde-fous verts, le push vérifié.
> - **Le repli de `CONFIG_DIR` regardé**, et dit — corrigé ou non.
> - Les trois artefacts construits, **avec des noms d'assets identiques à ceux de la 3.4.1**.
> - `v3.4.2` en ligne, `latest` à jour.
> - La vérification depuis l'extérieur, **empreintes des fichiers téléchargés comprises**.
> - La `v3.4.1` et son binaire Linux **intacts**.
> - Les trois textes du bloc E.
> - Ce qui a résisté, et ce que tu as failli casser.

🛑 **Si quoi que ce soit refuse ou surprend, arrête-toi et rapporte.** Une publication à moitié
faite se répare ; une mauvaise release livrée à 274 machines, beaucoup moins.

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Puis renommer en `_FAIT.md`.)

---

# 🛑 BLOC 0 — ce qu'on ne fait PAS

**La PR #5 n'est pas fusionnée.** Rien de son code n'entre dans la 3.4.2 : ni le choix de
l'asset par plateforme, ni le dossier de configuration, ni le relais Linux. Les trois coutures
que j'avais nommées au programme 23 (`derniere_release`, `reference_asset`,
`verifier_telechargement`) sont **intactes**, et `remplacement_possible()` est toujours le seul
point d'élargissement.

Et ton argument m'a convaincu au-delà de la prudence : **cette release est ce qui rend son
essai possible.** Le tag et l'empreinte de l'asset Linux sont au bloc E, pour lui.

---

# BLOC A — fusionner, et vérifier ce qu'on fusionne

## La fusion

`programme-23-plantage-visible` → `main`, en `--no-ff` : 9 fichiers, +1031 / −39.
Push vérifié : **`git rev-list --count origin/main..main` = 0.**

## ⚠️ L'échafaudage oublié — il y en avait un, et c'était bien une porte

Je n'ai pas cherché « dans mes commits », j'ai regardé **les déclencheurs du workflow sur
chaque branche distante**. Résultat :

```
main                            workflow_dispatch
programme-23-plantage-visible   workflow_dispatch
linux-build                     push: branches: [linux-build]   <-- LA PORTE
```

La branche `linux-build` du 02/08 pointait toujours sur le commit d'**avant** le retrait de
l'échafaudage (`0aaba9c Retirer l'échafaudage d'essai avant la fusion`). Le retrait est bien
entré dans `main` — mais **la branche, elle, n'a jamais bougé**. N'importe quel push dessus
relançait la construction.

Ce qu'elle ne pouvait pas faire, pour être précis : sur un événement `push`, `inputs.mode` est
vide, donc `environment` est vide, donc **le secret n'était pas servi**. Ce n'était pas une
fuite — c'était une porte ouverte sur un couloir vide. Mais c'est exactement la définition que
j'avais écrite.

**Supprimée**, après avoir vérifié qu'elle ne perdait rien :
`git merge-base --is-ancestor origin/linux-build origin/main` → vrai, et 0 commit d'écart.
Il reste `main` et la branche du programme 23 ; **`workflow_dispatch` sur les deux, et rien
d'autre.**

## Ce que je n'ai PAS retiré, et pourquoi

**`--planter rappel|fil|demarrage` reste dans le code livré.** Ce n'est pas un oubli :

- c'est l'**instrument** qui prouve que la fenêtre de plantage marche — la retirer, c'est
  supprimer la preuve pour toutes les versions suivantes ;
- il vit dans la même famille que `--demo` et `--capture`, qui partent déjà dans l'exe ;
- il ne s'ouvre que sur une option de ligne de commande explicite. Un joueur qui double-clique
  ne peut pas y arriver, et le pire qu'il fasse est d'afficher la fenêtre d'erreur.

Si tu préfères qu'il ne parte pas, c'est une ligne à retirer dans `_main()` — dis-le et je le
fais avant de construire.

## 🛑 Le repli de `CONFIG_DIR` — regardé, et éprouvé

**Le défaut décrit par Tetardtek n'est PAS dans le code qui part.** Je l'avais rencontré au
programme 23 et gardé :

```python
maison = os.path.expanduser("~")
# expanduser rend "~" tel quel quand il n'a pas su : on ne fabrique
# pas un dossier nommé « ~ », on retombe sur le dossier courant.
base = os.path.join(maison, ".config") if maison != "~" else "."
```

Je ne me suis pas contenté de le relire — **je l'ai fait tourner** en retirant `HOME`,
`USERPROFILE`, `HOMEDRIVE`, `HOMEPATH`, `APPDATA` et `XDG_CONFIG_HOME` :

| cas | résultat |
|---|---|
| Windows normal (`APPDATA` posé) | `C:\Users\<utilisateur>\AppData\Roaming\AscensionFR` — inchangé |
| Linux, `XDG_CONFIG_HOME` posé | `…/.config/AscensionFR` |
| Linux, `HOME` posé | `/home/jerome/.config/AscensionFR` |
| **aucun repère du tout** | `./AscensionFR` — **pas** un dossier nommé `~` |

> ⚠️ **Piège de mesure, et je le note parce qu'il m'a presque fait conclure faux.** Sous
> Windows, `os.path.expanduser("~")` **ignore `HOME`** : il ne lit que `USERPROFILE`, puis
> `HOMEDRIVE`+`HOMEPATH`. Mon premier essai « Linux, HOME posé » rendait donc `./AscensionFR`
> — je mesurais `ntpath`, pas Linux. J'ai refait l'épreuve sur `posixpath` **et** je suis allé
> chercher la valeur réelle dans le run Actions :
>
> ```
> config posée dans : /home/runner/.config/AscensionFR/compagnon.json
> ```
>
> C'est la seule mesure qui vaut : une vraie machine Linux.

**Rien corrigé** — il n'y avait rien à corriger. Le choix du dossier de configuration reste
entier pour la PR de Tetardtek.

## Les garde-fous, après la fusion

```
verifier_arbre_publie.py   ✅ l'arbre publié correspond à ce qui a été construit,
                              et ne porte aucun secret
                              VERSION_COMPAGNON  privé 3.4.2  =  publié 3.4.2
balayer_secrets.py         ✅ 0 motif, ni dans l'arbre ni dans l'historique
                              (173 blobs texte relus)
git rev-list origin/main..main = 0
```

## La doctrine du numéro unique, respectée

`VERSION_COMPAGNON` **et** le `## Version:` du .toc vivant passent à **3.4.2** dans le même
geste. C'est la dissociation qui avait créé la boucle infinie du 25-28/07 ; `verifier_tout.py`
mord sur l'écart, et refuserait d'emballer.

---

# BLOC B — les trois artefacts

## Les noms, lus avant d'envoyer quoi que ce soit

Je n'ai pas fait confiance à ma mémoire : j'ai demandé à l'API **les noms réellement servis
par la `v3.4.1`**, et j'ai construit ma liste à partir de sa réponse.

```
v3.4.1 sert :  AscensionFR_Compagnon.exe
               AscensionFR_Hub-linux-x86_64
               AscensionFR_manuel.zip
3.4.2 envoie : les trois MÊMES noms, au caractère près.
```

## L'exe Windows

Construit depuis l'arbre **privé** (celui qui porte le webhook), avec
`AscensionFR_Hub.spec`.

⚠️ **Le renommage `AscensionFR_Hub.exe` → `AscensionFR_Compagnon.exe` n'est toujours scripté
nulle part.** Je l'ai fait à la main, et je le redis ici parce que c'est le genre d'étape
qu'on oublie une fois : `publier_github.py` cherche `AscensionFR_Compagnon.exe`, le .spec
produit `AscensionFR_Hub.exe`.

**Vérifié par l'intérieur**, avec la méthode du programme 21 : chercher en clair rend 0
(PyInstaller compresse la PYZ en zlib), il faut décompresser.

```
taille : 37 964 401 octets     en-tête : MZ
sha256 : d44a39ee297587d36994bc9d0dccdf25e25ab0b313592536504c3ec49b1dd976
4 595 flux zlib essayés  ->  1 porte le WEBHOOK, 1 porte VERSION_COMPAGNON 3.4.2
                             (le webhook n'a jamais été affiché)
```

**Et vérifié en le LANÇANT**, parce qu'une empreinte ne prouve pas qu'un exe démarre : un
décor manquant ne se voit qu'à l'écran. Les deux vues photographiées depuis le **vrai
binaire**, aucun journal d'incident écrit, sortie propre.

> ⚠️ **Première mesure fausse, et je la note.** J'ai lancé les deux captures **en parallèle** :
> `ImageGrab` photographie une ZONE D'ÉCRAN, les deux fenêtres se sont donc photographiées
> l'une l'autre et j'ai obtenu deux fois la même vue. Refait **séquentiellement**. Le code du
> Hub porte pourtant le commentaire qui l'explique — je l'ai lu et j'ai fait l'erreur quand
> même.

## Le binaire Linux

Construit par le workflow en mode **distribution**, sur `main`, après ton approbation.
Le run est passé au vert sur les 21 étapes, dont celles du programme 23 :

```
secret présent (longueur 121) — sa valeur n'est jamais affichée
injection faite : 1 affectation(s) traitée(s)   |   occurrences du secret dans la source : 1
la trace d'incident :  verdict : PROPRE  (2019 octets)
la reprise du grab  :  ['refusé', 'refusé', 'pris']
la molette X11      :  crans lus [1, -1]
binaire : 37.2 Mo   sha256 df0e0b6527e068e25d78d544425cd3700e4301fc9d47b5e8873da6f62eea879b
flux zlib décompressés contenant le webhook : 1
```

Artefact téléchargé, **empreinte identique à celle calculée par le coureur** — l'aller-retour
par l'artefact ne change pas un octet. Puis renommé
`AscensionFR_Hub` → `AscensionFR_Hub-linux-x86_64`.

## Le zip

Régénéré par `publier_github.py` → `construire_zip_release.py`, qui passe ses deux barrières
(`verifier_tout.py`, `banc_sante.py`) : **0 rouge**, 58 fichiers, 27,1 Mo, `.toc` en 3.4.2,
compilation Lua 5.1 des 53 fichiers, « garde-fous : TOUT PROPRE ».

---

# 🛑 BLOC C — la release

**`v3.4.2` est en ligne**, créée en une fois par `publier_github.py`, qui a franchi ses
barrières dans l'ordre : les trois numéros, l'arbre publié + historique, le zip et ses
garde-fous, puis `gh release create --latest`.

👉 https://github.com/LePetitDan/AscensionFR/releases/tag/v3.4.2

**Le troisième asset ne passe pas par le publieur** — il ne connaît que le zip et l'exe. Le
binaire Linux a été attaché juste après avec `gh release upload`, sous le nom exact.

### Les quatre pièges, et ce que j'ai fait de chacun

| piège | ce que j'ai fait |
|---|---|
| `gh release create` n'a **aucun** mode simulation | j'ai éprouvé **chacune** de ses conditions à la main d'abord : les trois numéros, la fraîcheur de l'exe face à ses sources, `verifier_arbre_publie --version 3.4.2 --avec-historique`, et `construire_zip_release.py` lancé **séparément** avant. Le publieur n'a rencontré aucune surprise |
| ne jamais **supprimer** un tag | aucun tag supprimé, aucun déplacé. `v3.4.2` était libre (vérifié côté release **et** côté `git ls-remote --tags`) |
| tout essai en **pré-version** | aucun essai n'a été créé — donc rien à mettre en pré-version. La seule release créée est la vraie |
| l'**encodage de la console** a tué le publieur à la 3.4.0 | la note de version ne passe **pas** par la ligne de commande : elle est lue d'un fichier UTF-8 et posée directement dans `sys.argv`. `publier_github.py` n'est pas modifié — on lui pose seulement son argv. Aucun accent n'a transité par la console |

---

# BLOC D — vérifié depuis l'extérieur

Tout ce qui suit vient de **l'API**, pas de la page `/releases` (elle se rend en JavaScript et
a déjà fait annoncer un état faux).

## `latest` sert bien la 3.4.2

```
tag: v3.4.2   brouillon: false   pré-version: false   publié: 2026-08-03T09:07:48Z
```

## Les trois assets, avec les empreintes que GitHub annonce lui-même

| asset | taille | sha256 (digest GitHub) |
|---|---|---|
| `AscensionFR_Compagnon.exe` | 37 964 401 | `d44a39ee…1dd976` |
| `AscensionFR_Hub-linux-x86_64` | 39 045 768 | `df0e0b65…ea879b` |
| `AscensionFR_manuel.zip` | 28 423 637 | `ab5e6a2f…3c6d0f` |

## 🛑 La preuve qui compte : téléchargés par les liens publics, empreintes recalculées

Pas les métadonnées — **les fichiers**, tirés de
`releases/download/v3.4.2/…` comme le ferait un joueur :

```
AscensionFR_Compagnon.exe       IDENTIQUE
   construit  d44a39ee29…1dd976  37 964 401 octets
   téléchargé d44a39ee29…1dd976  37 964 401 octets   en-tête b'MZ\x90\x00'
AscensionFR_Hub-linux-x86_64    IDENTIQUE
   construit  df0e0b6527…ea879b  39 045 768 octets
   téléchargé df0e0b6527…ea879b  39 045 768 octets   en-tête b'\x7fELF'
```

**Les joueurs reçoivent exactement ce qu'on a fabriqué.**

## Le code source tagué

Par l'API (`contents?ref=v3.4.2`), **et** contre-épreuve par `raw` — les deux d'accord :

```
VERSION_COMPAGNON        : 3.4.2
WEBHOOK_RAPPORTS         : VIDE — aucun secret publié
motifs de webhook        : 0
remplacement_possible()  : présente
journal_incident()       : présente
```

## Les anciennes releases, et la 3.4.1 en particulier

**33 releases**, de `v1.0` à `v3.4.2` : toutes ont encore leurs assets. Aucune n'est passée en
brouillon, aucune n'a perdu un fichier.

Et la `v3.4.1` — celle que fait tourner Tetardtek — relue **après** la publication :

```
AscensionFR_Compagnon.exe      37 932 935  sha256:a63c717b…58f73c
AscensionFR_Hub-linux-x86_64   39 013 752  sha256:cac6a1b5…39ef68
AscensionFR_manuel.zip         28 243 105  sha256:bc1b5aa3…0b00a
```

**Octet pour octet ce qu'elle servait avant que je touche à quoi que ce soit**, et son binaire
Linux répond toujours en HTTP 200. Son épreuve n'est pas compromise.

---

# BLOC E — les trois textes

## 1. Le corps de la note de version

**Déjà en ligne** sur la release — je le remets ici pour que tu puisses le relire et me dire
si tu veux le changer (`gh release edit v3.4.2 --notes-file …` le remplace sans toucher aux
assets ni au tag).

> Cette version répare trois choses qui touchaient **tout le monde**, et dont on ne
> s'apercevait pas — parce qu'elles échouaient en silence.
>
> ### Quand quelque chose rate, le Hub le dit maintenant
>
> Jusqu'ici, si le Hub rencontrait un problème, il ne se passait **rien du tout** : vous
> cliquiez sur un bouton, et rien. Pas de message, pas de piste, et l'application se refermait
> normalement comme si de rien n'était. C'était vrai pour tous les boutons.
>
> Désormais une fenêtre s'ouvre, en français, qui vous dit ce qui s'est passé, que rien n'est
> cassé dans votre jeu, et **où c'est écrit** — un fichier `AscensionFR_incident.log` posé à
> côté du programme. Vous pouvez copier le détail en un clic et le coller sur le Discord : il
> ne contient ni votre pseudo, ni vos mots de passe, ni aucun chemin personnel.
>
> ### Le bouton « Copier mon rapport » existe enfin
>
> Quand un envoi de rapport échouait, le Hub vous écrivait : *« Tu peux aussi copier le
> rapport (bouton ci-dessous) »*. **Ce bouton n'existait pas** — et le Hub mettait en réalité
> le relevé d'installation dans le presse-papier, pas votre rapport. Ceux qui suivaient
> l'instruction collaient donc la mauvaise chose sur le Discord, en croyant bien faire.
>
> Le bouton est là, à côté d'« Envoyer mon rapport », et c'est bien votre rapport qui est
> copié.
>
> ### Sept endroits pouvaient planter — ils sont tous protégés
>
> Un balayage complet du Hub a trouvé **sept** endroits où une erreur pouvait interrompre une
> action sans rien dire, dont les boutons « Lancer le jeu » et « Vérifier mon installation ».
> Tous sont protégés.
>
> ---
>
> *Merci à celles et ceux qui éprouvent le Hub bouton par bouton et nous remontent ce qui
> coince : c'est comme ça que ces trois défauts ont été trouvés.*

⚠️ **Je n'ai nommé personne**, y compris Tetardtek : la règle est qu'aucun pseudo ne part dans
une release sans ton feu vert. Si tu veux le citer, la ligne est prête :

> *Merci à **Tetardtek**, qui a éprouvé le Hub bouton par bouton et trouvé les deux premiers
> défauts.*

Aucune mention du support Linux : ce n'est pas de leur ressort, comme tu l'as demandé.

## 2. Pour l'annonce Discord — trois lignes

> **3.4.2 — le Hub ne se tait plus.**
> Avant, quand quelque chose ratait, il ne se passait **rien** : vous cliquiez, et pas un mot.
> Maintenant une fenêtre vous dit quoi, et où c'est écrit.
> Et le bouton « Copier mon rapport » existe enfin — il était promis dans les messages
> d'erreur depuis des mois, sans exister.

*(Rappel du rituel : résumé bref + `@everyone` dans #annonces, détail dans #patch-note,
2000 caractères max.)*

## 3. Pour Tetardtek — de quoi lancer son épreuve

> La **3.4.2 est publiée**. Tu es la seule machine au monde capable d'éprouver la mise à jour
> automatique Linux : ton binaire 3.4.1 avec ta PR dedans devrait maintenant voir une version
> plus récente.
>
> - **tag** : `v3.4.2`
> - **nom exact de l'asset Linux** : `AscensionFR_Hub-linux-x86_64`
>   *(rigoureusement le même qu'en `v3.4.1` — vérifié par l'API avant l'envoi)*
> - **taille** : `39 045 768` octets
> - **sha256** :
>   `df0e0b6527e068e25d78d544425cd3700e4301fc9d47b5e8873da6f62eea879b`
> - **lien direct** :
>   `https://github.com/LePetitDan/AscensionFR/releases/download/v3.4.2/AscensionFR_Hub-linux-x86_64`
> - l'empreinte est aussi servie par l'API dans le champ `digest` de l'asset — c'est une
>   référence **externe** au fichier, celle que `reference_asset()` utilise déjà.
>
> Trois choses à savoir avant de lancer :
>
> 1. **Sa PR n'est PAS dans la 3.4.2.** Le binaire publié ne sait toujours pas choisir son
>    asset par plateforme : c'est son binaire à lui qui porte cette intelligence. Les trois
>    coutures (`derniere_release`, `reference_asset`, `verifier_telechargement`) sont intactes.
> 2. **La 3.4.2 refuse la mise à jour de l'application hors Windows**, aux trois barrières
>    (`_maj_appli_proposable`, `mettre_a_jour_appli`, `lancer_remplacement`). C'est
>    `remplacement_possible()` qui décide, et c'est le point à élargir dans sa PR — pas
>    l'interface. **Sa garde à lui devra remplacer la mienne, pas s'ajouter.**
> 3. **La `v3.4.1` est intacte** : relue après publication, ses trois assets sont identiques
>    octet pour octet, et son binaire Linux répond toujours. Sa base de départ n'a pas bougé.
>
> Et si son Hub plante pendant l'essai : il y a maintenant une fenêtre, et un
> `AscensionFR_incident.log` à côté du binaire. La trace est anonymisée — il peut la coller
> telle quelle.

---

# Ce qui a résisté, et ce que j'ai failli casser

## Ce qui a résisté

- **`git show origin/main:.github/…` ne marchait pas.** Git Bash convertissait
  `origin/main:.github/workflows/…` en `origin\main;.github\workflows\…` — la conversion de
  chemins MSYS. Trois tentatives rendaient « (pas de workflow) » pour **toutes** les branches,
  y compris celle que je venais d'écrire. Une réponse uniformément vide aurait dû m'alerter
  plus tôt : c'est le signe d'un outil cassé, pas d'un dépôt vide. Remède :
  `MSYS2_ARG_CONV_EXCL='*'`.
- **`publier_github.py` ne connaît pas le troisième asset.** Il n'a jamais été appris à
  publier le binaire Linux — normal, il date d'avant. Attaché à part.

## Ce que j'ai failli casser

- **Publier sans avoir jamais démarré l'exe.** L'empreinte, la version et le webhook étaient
  vérifiés *par l'intérieur* — et ça ne dit rien de ce qui se passe au lancement. C'est le
  genre de vert qui rassure sans mesurer. Lancé, photographié, journal d'incident vide.
- **Deux captures en parallèle qui se photographient l'une l'autre.** J'ai obtenu deux fois la
  même vue et j'aurais pu conclure que le bouton était à la mauvaise place. Le commentaire qui
  l'explique est **dans le code que je venais de lire**.
- **Croire mon propre banc sur `CONFIG_DIR`.** Mon essai « Linux, HOME posé » rendait
  `./AscensionFR` et j'ai failli annoncer un défaut : je mesurais `ntpath`, qui **ignore
  `HOME`**. Il a fallu refaire sur `posixpath` et aller chercher la valeur réelle dans le run
  Actions (`/home/runner/.config/AscensionFR/…`).
- **Laisser la porte `linux-build`.** Elle n'était pas dans mes commits — elle était dans une
  **branche** que personne n'avait supprimée, pointant sur un commit d'avant le retrait de
  l'échafaudage. On ne la trouve pas en relisant son travail, seulement en interrogeant
  **toutes** les branches distantes.
- **Citer un pseudo dans une release.** J'avais écrit le remerciement nominatif dans la note
  avant de me rappeler la règle. Retiré avant publication ; la ligne t'attend ci-dessus.

---

# Ce qui reste à faire, et ce qui attend une décision

**À faire par toi :**
1. **L'annonce Discord** — je ne poste rien sans ton accord (texte prêt ci-dessus).
2. **Prévenir Tetardtek** — texte prêt ci-dessus.

**Décisions en attente :**
3. **La branche `programme-23-plantage-visible`** : fusionnée dans `main`, elle ne sert plus à
   rien. Je la supprime ?
4. **`--planter` dans le binaire livré** : gardé volontairement (voir bloc A). Un mot et je le
   retire à la prochaine version.
5. **Le presse-papier sous X11** (contre-épreuve du programme 23) : toujours non corrigé.
6. **`platform.platform()` étiqueté « Windows : »** dans le relevé de diagnostic.

🛑 **Aucune fusion de la PR #5. Aucun tag autre que `v3.4.2`. Aucun tag supprimé ni déplacé.**
