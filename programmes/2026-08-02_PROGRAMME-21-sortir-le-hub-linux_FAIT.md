# Demande de code → Claude Code

# 🐧 PROGRAMME 21 — sortir le Hub Linux pour de bon

**Date :** 2026-08-02
**Dan a donné le GO.** C'est la suite du programme 18, qui a tout construit et tout éprouvé.

🛑 **C'est le programme irréversible.** À partir du moment où un fichier est attaché à une
release, il est téléchargeable par tout le monde et il ne se retire pas proprement.

---

## 🛑 BLOC 0 — le piège qui pourrait toucher 274 machines Windows

**Ne crée PAS de nouvelle release. Ne pose PAS de nouveau tag.**

Une nouvelle release deviendrait `latest`, et **chaque Hub Windows installé proposerait aussitôt
une mise à jour** — pour une version où rien n'a changé côté Windows. 274 personnes dérangées
pour rien, et un chemin de mise à jour qu'on vient de réparer remis à l'épreuve sans raison.

**Le binaire Linux s'attache comme asset supplémentaire à la release `v3.4.1` existante.** Le
tag ne bouge pas, `latest` ne bouge pas, les assets Windows ne bougent pas, et les liens
permanents que les Hubs interrogent restent identiques.

### Mais avant, une mesure — et un arrêt possible

Le binaire a été construit depuis `main` (`5b2d86c`), qui est **postérieur** au tag `v3.4.1`
(`eae7036`). Attacher à `v3.4.1` un binaire bâti sur autre chose serait un petit mensonge.

**Mesure l'écart exact :** `git diff --stat eae7036 5b2d86c`.

- **Si l'écart se limite à `compagnon/assets/hub/`** (le programme 17) : c'est acceptable, et
  c'est même logique — ces fichiers sont précisément ce qui manquait à Linux. **Dis-le dans la
  note de version**, ne le tais pas.
- **Si l'écart contient autre chose : ARRÊTE-TOI** et rapporte. Ce sera à Dan de trancher.

🛑 **Et le nom de l'asset :** il doit être **distinct** de tout ce que le Compagnon Windows
interroge. Va lire les noms d'assets réellement servis par `v3.4.1` et ce que le code du Hub
interroge, **avant** d'envoyer quoi que ce soit. Un nom qui recouvre l'existant casserait la
mise à jour de tout le monde, en silence.

---

## BLOC A — retirer l'échafaudage, puis fusionner

Tu l'as écrit toi-même : « un échafaudage qu'on oublie devient une porte ».

- retire le déclencheur de test (`on: push: branches: [linux-build]`) **avant** toute fusion ;
- retire les marqueurs de commit qui s'étaient piégés eux-mêmes ;
- fusionne `linux-build` dans `main`. **Le diff doit être le seul fichier de workflow** — tu
  l'as mesuré au 18, vérifie-le encore après le nettoyage ;
- **les 5 fichiers surveillés : identiques**, par empreinte, pas de mémoire ;
- `verifier_arbre_publie.py` et `balayer_secrets.py` **verts après la fusion** ;
- push vérifié : `git rev-list --count origin/main..main` = **0**.

---

## 🛑 BLOC B — reconstruire depuis ce qui est publié

**Ne réutilise pas l'artefact de la branche.** Ce qui part chez les joueurs doit être construit
depuis exactement ce qui est publié dans `main`, après le nettoyage de l'échafaudage.

Relance la construction en mode distribution, sur `main`. **Elle va s'arrêter et attendre
l'approbation de Dan** — dis-lui clairement quand cliquer, il s'y attend.

Puis, comme au 18 : le binaire porte le webhook (prouvé sans jamais l'afficher), et le journal
complet du run relu, **zéro fuite**.

---

## 🛑 BLOC C — la preuve, depuis le lien public

« L'asset est en ligne » ne prouve rien.

- **télécharge le binaire depuis l'URL publique de la release**, pas depuis l'onglet Actions ;
- **recalcule son empreinte** et compare-la à celle du run. C'est la seule preuve que ce que les
  joueurs recevront est ce qu'on a construit ;
- **lance-le** (`--demo`) : les 5 vues ;
- ⚠️ **n'envoie aucun rapport réel sur le Discord des joueurs.**

---

## BLOC D — ce qu'on doit aux joueurs Linux, en toutes lettres

Rédige le texte qui accompagne le téléchargement — dans la note de version **et** dans
`docs/INSTALLATION.md`. Trois choses, et aucune ne se tait :

1. **comment le lancer** : télécharger, `chmod +x`, double-clic. En français simple ;
2. 🛑 **il n'y a PAS de mise à jour automatique sous Linux.** C'est le point le plus important.
   Un joueur qui l'ignore restera sur cette version pour toujours en croyant être à jour.
   Dis-lui **comment il saura** qu'une nouvelle version existe ;
3. **la limite système** : rien avant Ubuntu 22.04 / Debian 12 (glibc 2.35). Un joueur sur plus
   ancien doit le savoir **avant** de télécharger 37 Mo pour rien ;
4. et la petite honnêteté : **les polices du jeu ne se chargent pas**, l'affichage est plus
   sobre. Ça marche, c'est lisible, mais autant qu'il l'apprenne de nous.

---

## 🛑 BLOC E — vérifier que rien n'a bougé pour les 274 autres

Le vrai contrôle de ce programme n'est pas que Linux marche : c'est que **Windows n'a rien vu.**

- `releases/latest` sert toujours **v3.4.1** ;
- les assets Windows de `v3.4.1` : **mêmes noms, mêmes tailles, mêmes empreintes** qu'avant ;
- `v3.4.1` pointe toujours sur `eae7036` ;
- les releases **3.3.0 / 3.3.1 / 3.4.0** ont toujours leurs assets ;
- **33 tags**, pas 34.

> ⚠️ N'utilise pas la page `/releases` pour vérifier : elle se rend en JavaScript et elle a déjà
> fait annoncer un état faux. Les points fiables sont `/releases/latest`,
> `/releases/expanded_assets/<tag>` et `raw.githubusercontent.com`.

---

**« Terminé » veut dire :**

> - L'écart `v3.4.1` → `main` mesuré, et la décision qui en découle.
> - L'échafaudage retiré, la fusion faite, **le diff réduit au seul workflow**.
> - Le binaire **reconstruit depuis `main`**, pas recyclé.
> - L'asset en ligne sur `v3.4.1`, **téléchargé depuis le lien public, empreinte recalculée,
>   lancé**.
> - Le texte pour les joueurs, **avec l'absence de mise à jour automatique écrite noir sur
>   blanc**.
> - La preuve que **rien n'a bougé pour Windows** : `latest`, tags, assets, empreintes.
> - Ce qui a résisté, et ce que tu as failli casser.

🛑 **Aucun nouveau tag, aucune nouvelle release. `latest` doit rester `v3.4.1`.**

---
## Réponse de Claude Code
> (bloc par bloc, au fil de l'eau. Puis renommer en `_FAIT.md`.)

---

## ✅ BLOC 0 — l'écart mesuré, et l'arrêt déclenché puis levé par Dan

### L'écart exact

```
v3.4.1 pointe sur : eae7036
main est sur      : 19767622

99 fichiers modifiés, 524 insertions
   98 sous compagnon/assets/hub/     (programme 17)
    1  docs/CONTRIBUER.md            (programme 20, il y a une heure)
```

**La règle d'arrêt s'est déclenchée à la lettre** : l'écart contenait « autre chose ».
Je me suis arrêté et j'ai rapporté avant de continuer.

### La mesure qui a permis de décider

L'écart brut ne dit pas ce qui compte. Ce qui compte, c'est **ce qui entre dans le
binaire** — et PyInstaller n'embarque que `compagnon_hub.py`, `interface_hub.py`,
`compagnon.py`, `parser_wdb.py` et `compagnon/assets/`. J'ai donc mesuré sur ce
périmètre :

```
$ git diff --name-only v3.4.1 main -- compagnon/  |  grep -v assets/hub
   (rien)
   total sous compagnon/ : 98 fichiers, TOUS dans assets/hub
```

Et les cinq sources, une par une :

```
compagnon/compagnon.py         : IDENTIQUE
compagnon/compagnon_hub.py     : IDENTIQUE
compagnon/interface_hub.py     : IDENTIQUE
compagnon/parser_wdb.py        : IDENTIQUE
compagnon/AscensionFR_Hub.spec : IDENTIQUE
```

**Le binaire bâti sur `main` est donc, côté source, exactement `v3.4.1` plus les assets
qui lui manquaient.** `docs/CONTRIBUER.md` — et, après la fusion, le fichier de workflow
— ne peuvent pas y entrer : ni l'un ni l'autre n'est importé ni embarqué.

**Décision de Dan : continuer et attacher à `v3.4.1`.** Le programme demandait que ce
soit lui qui tranche ; c'est fait. Et **ce n'est pas tu dans la note de version** : elle
dit que ce binaire est la 3.4.1 avec les décors du Hub, absents du dépôt jusqu'à
aujourd'hui.

### 🛑 Le nom de l'asset — lu dans le code, pas deviné

**Ce que `v3.4.1` sert aujourd'hui :**

| asset | taille | téléchargements |
|---|---:|---:|
| `AscensionFR_Compagnon.exe` | 37 932 935 o | 236 |
| `AscensionFR_manuel.zip` | 28 243 105 o | 635 |

**Ce que le code interroge**, et surtout **comment** :

```python
ZIP_ATTENDU = "AscensionFR_manuel.zip"          # compagnon.py:95
EXE_ATTENDU = "AscensionFR_Compagnon.exe"       # compagnon.py:96

for asset in infos.get("assets", []):           # compagnon.py:496-500
    if   asset.get("name") == ZIP_ATTENDU: url_zip = …
    elif asset.get("name") == EXE_ATTENDU: url_exe = …
```

Plus un lien permanent `releases/latest/download/AscensionFR_Voix.zip` (l. 88), et
`reference_asset(nom)` qui compare lui aussi par `==` (l. 540).

**Tout l'appariement se fait par ÉGALITÉ EXACTE.** Aucun `startswith`, aucun `endswith`,
aucune sous-chaîne, aucune extension testée. Un asset dont le nom n'est **aucun** des
trois est structurellement invisible pour les Compagnons installés — ils le voient
passer dans la liste de l'API et l'ignorent.

**Nom retenu : `AscensionFR_Hub-linux-x86_64`.** Pas de `.exe`, pas de `.zip`, distinct
des trois noms interrogés, et il dit ce qu'il est à un joueur qui lit la page.

---

## ✅ BLOC A — échafaudage retiré, fusion faite

**Ce qui est parti**, et pourquoi chaque morceau existait :

| retiré | pourquoi il était là |
|---|---|
| `on: push: branches: [linux-build]` | GitHub n'enregistre un `workflow_dispatch` que s'il existe **déjà** sur la branche par défaut — sans ce déclencheur, impossible d'éprouver quoi que ce soit avant fusion |
| le `MODE` dérivé d'un marqueur `[distribution]` / `[sans-secret]` dans le message de commit | un `push` ne porte aucun `inputs` |
| le mode `sans-secret` | il n'existait que pour voir la barrière mordre |

**1 867 caractères retirés.** Il ne reste que `workflow_dispatch` et ses deux entrées :

```
déclencheurs : ['workflow_dispatch']
MODE         : ${{ inputs.mode }}
environment  : ${{ inputs.mode == 'distribution' && 'publication' || '' }}
```

> Un reste que la première passe avait laissé : un commentaire expliquait encore le
> corollaire « ne pas demander l'environnement, c'est ne pas recevoir ses secrets » **en
> l'attribuant au mode `sans-secret` disparu**. Réécrit pour dire ce qu'il explique
> vraiment — c'est ce qui rend le mode `diagnostic` sûr. Un commentaire qui parle d'un
> mécanisme supprimé est un piège pour le prochain qui lit.
>
> Contrôle : `grep -ci "echafaudage|linux-build|head_commit|sans-secret"` → **0**.

**La fusion** (`--no-ff`, commit `5fd7125`) :

```
diff origin/main <-> main :  .github/workflows/construire-hub-linux.yml     ← UN SEUL fichier

les 5 surveillés, par empreinte :
   compagnon.py             bf2f0795c774d55b  identique
   compagnon_hub.py         b64f7bf9039c7044  identique
   interface_hub.py         8f3469e1eecdc81b  identique
   fabriquer_decor_hub.py   6074b3153c832b95  identique
   AscensionFR_Hub.spec     6bd12262c5431e63  identique
```

**Les deux garde-fous après la fusion :** `verifier_arbre_publie` ✅, `balayer_secrets`
✅. Push vérifié : `origin/main..main` = **0**, et `ls-remote` rend `5fd7125…`.

Et la preuve que l'échafaudage n'était pas un caprice : **une fois sur `main`, GitHub a
enfin enregistré le workflow.**

```
$ gh api .../actions/workflows
  Construire le Hub (Linux)   etat=active   .github/workflows/construire-hub-linux.yml
```

---

## ✅ BLOC B — reconstruit depuis `main`, pas recyclé

L'artefact de la branche **n'a pas été réutilisé**. Nouveau run, sur `main`, après le
nettoyage — et **le premier lancé par le vrai déclencheur manuel** :

```
run 30745331414   branche=main   evenement=workflow_dispatch
```

Il s'est arrêté en `waiting`, Dan a approuvé, les 18 étapes sont vertes.

**La preuve du webhook, sans jamais l'afficher :**

```
secret présent (longueur 121) — sa valeur n'est jamais affichée.
injection faite : 1 affectation(s) traitée(s)
taille du binaire : 37.2 Mo
empreinte SHA-256 du binaire : cac6a1b5f524899569f6306791c45111341b42cf1d7d13d79fe1cdae1339ef68
empreinte du secret (16 premiers hex) : 570ea4e48214e733
occurrences en clair dans le binaire : 0
flux zlib essayés : 3786
flux zlib décompressés contenant le webhook : 1
```

L'empreinte du secret est **la même qu'au programme 18** (`570ea4e48214e733`) : c'est
bien le même webhook, et il n'a été affiché ni une fois ni l'autre.

**Le journal complet relu — 784 lignes, 100 529 caractères :**

| cherché | trouvé |
|---|---:|
| URL de webhook Discord | **0** |
| jeton après l'identifiant | **0** |
| `WEBHOOK_RAPPORTS = "http…` | **0** |
| toute URL contenant « discord » | **0** |
| trace shell (`set -x`) | **0** |
| chaînes longues | 5 — **2 empreintes d'artefact calculées par GitHub, 1 empreinte du binaire que j'affiche exprès, 2 faux positifs sur des URL `github.com`** |
| masques `***` de GitHub | 6 — **tous de GitHub** : 2 `token:`, 1 ligne de credentials git, 3 échos du bloc `env:` |

**Notre code n'a rien imprimé.** Les 5 vues du Hub : **aucune sortie d'erreur**.

---

## ✅ BLOC C — la preuve depuis le lien public

**Téléchargé depuis l'URL publique de la release**, pas depuis l'onglet Actions :

```
$ curl -L https://github.com/LePetitDan/AscensionFR/releases/download/v3.4.1/AscensionFR_Hub-linux-x86_64
  code HTTP : 200      octets : 39 013 752

  empreinte annoncée par le run : cac6a1b5f524899569f6306791c45111341b42cf1d7d13d79fe1cdae1339ef68
  empreinte du fichier public   : cac6a1b5f524899569f6306791c45111341b42cf1d7d13d79fe1cdae1339ef68
```

**Identiques.** Ce que les joueurs recevront est exactement ce que le run a construit —
et donc exactement ce que le run a **lancé** sur écran virtuel, les 5 vues.

### 🛑 Ce que je n'ai PAS pu faire, et je ne le maquille pas

**Je n'ai pas lancé le binaire moi-même.** Je suis sous Windows et **WSL n'est pas
installé** sur cette machine (« Le Sous-système Windows pour Linux n'est pas
installé »). Je n'en installe pas un pour un contrôle — c'est une modification du
système de Dan, hors de ce programme.

La chaîne de preuve est donc : *le run a lancé ce binaire et l'a photographié* + *le
fichier public a la même empreinte au bit près*. C'est transitif, pas direct. **Je le
dis plutôt que d'écrire « lancé ».**

En revanche, j'ai fait porter quatre contrôles **directement sur les octets publics** :

**1. C'est bien un exécutable Linux :**

```
magie ELF ✅   64 bits   petit-boutiste   type ET_EXEC   machine x86-64
```

**2. La limite système, mesurée sur le fichier publié — et pas comme je croyais.**
Le chargeur PyInstaller n'exige que `GLIBC_2.14`. **Ça aurait fait une annonce fausse
et trop optimiste.** Le binaire embarque 31 bibliothèques, et il faut les compter
aussi :

```
versions dans le fichier non compressé : 2.2.5 … 2.14
versions dans les flux DÉCOMPRESSÉS    : 2.2.5 … 2.32, 2.33, 2.34, 2.35
   (102 flux compressés portaient des symboles glibc)

LA PLUS HAUTE EXIGÉE, TOUT COMPRIS : glibc 2.35
```

**2.35 confirmé** — mais mesuré sur ce qui est publié, et non déduit de la machine de
construction. Les deux méthodes tombent d'accord, ce qui est le vrai contrôle.

**3. Le webhook y est**, sans jamais l'afficher : 0 en clair, **1 après décompression**,
longueur 121, empreinte `570ea4e48214e733` — **la même que celle annoncée par le run**.

**4. Les décors du Hub y sont** : `decor_hub.json`, `catalogue_hub.json`,
`MORPHEUS.TTF`, `FRIZQT__.TTF`, `fond.png`, `btn_envoyer.png` — tous présents.

**Aucun rapport n'a été envoyé sur le Discord des joueurs.** Le binaire n'a été lancé
que dans le run, en `--demo`, avec `envoi_auto: False` et un dossier de jeu vide.

---

## ✅ BLOC D — ce qu'on doit aux joueurs Linux, écrit aux deux endroits

**Note de version `v3.4.1`** (corps allongé de 2 491 → 5 200 caractères, **le début
préservé mot pour mot** — vérifié par `diff` sur les 30 premières lignes) **et
`docs/INSTALLATION.md`** (nouvelle section 🐧, commit `4a723ee`, poussé et vérifié).

Les quatre points, et aucun n'est adouci :

**1. Comment le lancer** — télécharger, clic droit → Propriétés → Permissions →
« Autoriser l'exécution » (ou `chmod +x`), double-cliquer. En français simple, avec le
chemin graphique **avant** la ligne de commande : un joueur n'est pas un administrateur
système.

**2. 🛑 Il n'y a PAS de mise à jour automatique.** C'est le point que j'ai mis en
premier et en gras aux deux endroits, avec la phrase qui compte : *« ce fichier ne
changera jamais tout seul »*. Et surtout **comment il saura** qu'une version existe —
parce que le dire sans donner le moyen ne sert à rien :

- le canal `#annonces` du Discord ;
- ou **Watch → Custom → Releases** sur la page du projet, qui envoie un courriel à
  chaque publication.

**3. La limite système**, avec un tableau « ça marche / ça ne marche pas » et surtout
**la commande pour vérifier soi-même** (`ldd --version`) — assortie de « inutile de
télécharger 37 Mo » : c'est ce qui évite le téléchargement pour rien que le programme
demandait d'éviter.

**4. Les polices** : dit franchement, et sans dramatiser. *« C'est moins joli, ça marche
pareil. »*

**Un cinquième point que j'ai ajouté sans qu'il soit demandé**, parce que son absence
créerait un malentendu coûteux :

> 🎮 Ce paragraphe ne parle que du **Hub**. La traduction elle-même est faite de fichiers
> `.lua` : elle marche exactement pareil quel que soit le système, et **l'installation à
> la main fonctionne sous Linux sans aucune réserve** — c'est même la voie la plus
> simple.

Sans ça, un joueur Linux lisant « pas de mise à jour automatique, distribution récente
exigée, affichage dégradé » pourrait conclure que **la traduction** est de seconde
classe chez lui. Elle ne l'est pas ; seul le Hub l'est.

---

## ✅ BLOC E — rien n'a bougé pour les 274 autres

Vérifié sur les points fiables — **jamais la page `/releases`**, qui se rend en
JavaScript et a déjà fait annoncer un état faux.

**1. `releases/latest` sert toujours la même chose :**

```
tag      : v3.4.1
publié   : 2026-08-01T20:10:01Z      ← inchangé, c'est bien la release d'hier soir
draft    : false      prerelease : false
```

**2. Les assets Windows, noms et tailles :**

| asset | avant (relevé au bloc 0) | maintenant |
|---|---:|---:|
| `AscensionFR_Compagnon.exe` | 37 932 935 o | **37 932 935 o** ✅ |
| `AscensionFR_manuel.zip` | 28 243 105 o | **28 243 105 o** ✅ |
| `AscensionFR_Hub-linux-x86_64` | *(absent)* | 39 013 752 o *(nouveau)* |

**3. Et l'empreinte de l'exe, pas seulement sa taille** — retéléchargé depuis
`releases/latest/download` :

```
a63c717bc071caa10ecf896684bcc649583dcd7ed14aaf5b084991780058f73c
```

**Identique à celle vérifiée à la publication du 01/08** (programme 16). L'exe que les
274 machines téléchargent n'a pas bougé d'un bit.

**4. Le tag n'a pas bougé :**

```
ce4fb0ac…   refs/tags/v3.4.1
eae70369…   refs/tags/v3.4.1^{}     ← pointe toujours sur eae7036
```

**5. Les releases précédentes ont toujours leurs assets :**

| release | assets |
|---|---|
| v3.3.0 | `AscensionFR_Compagnon.exe` 37 839 680 o + `AscensionFR_manuel.zip` 48 242 369 o |
| v3.3.1 | `AscensionFR_Compagnon.exe` 37 839 098 o + `AscensionFR_manuel.zip` 48 242 369 o |
| v3.4.0 | `AscensionFR_Compagnon.exe` 37 927 959 o + `AscensionFR_manuel.zip` 27 912 833 o |

**6. `33` tags, pas 34. `30` releases, aucune créée aujourd'hui.**

> Le seul chiffre qui a bougé est le **compteur de téléchargements** de l'exe (236 → 252)
> et du zip (635 → 677). Ce sont des joueurs qui téléchargent pendant qu'on travaille,
> pas un effet de ce programme. Je le note pour que personne ne le prenne pour un
> symptôme.

**Aucun Hub Windows ne proposera de mise à jour** : `latest` sert le même tag, avec le
même exe, à la même empreinte. Un asset supplémentaire dont le nom n'est aucun des trois
comparés par `==` est invisible pour eux.

---

## 🛑 Terminé — l'état exact

| « Terminé » veut dire | état |
|---|---|
| l'écart `v3.4.1` → `main` mesuré, décision prise | ✅ 98 assets + 1 doc ; **restreint au binaire : QUE les 98 assets**, les 5 sources identiques. Arrêt déclenché, **levé par Dan** |
| l'échafaudage retiré, fusion faite, **diff réduit au seul workflow** | ✅ 1 867 caractères retirés, `grep` = 0 trace, diff = **1 fichier** |
| le binaire **reconstruit depuis `main`**, pas recyclé | ✅ run `30745331414`, `workflow_dispatch` sur `main`, approuvé par Dan |
| l'asset en ligne, **téléchargé du lien public, empreinte recalculée** | ✅ `cac6a1b5…` **identique** au bit près |
| lancé | ⚠️ **pas par moi** — WSL n'est pas installé. Lancé **dans le run** (5 vues), et le fichier public est le même au bit près. **Transitif, et je le dis** |
| le texte pour les joueurs, **absence de mise à jour auto écrite noir sur blanc** | ✅ note de version **et** `docs/INSTALLATION.md`, avec **comment savoir** qu'une version sort |
| **rien n'a bougé pour Windows** | ✅ `latest` = v3.4.1 du 01/08, exe **`a63c717b…` identique**, tag sur `eae7036`, **33 tags**, 30 releases |

🛑 **Aucun nouveau tag, aucune nouvelle release, `latest` reste `v3.4.1`.**

**Le Hub Linux est distribué :**
https://github.com/LePetitDan/AscensionFR/releases/download/v3.4.1/AscensionFR_Hub-linux-x86_64

### Ce qui a résisté

- **L'appariement des assets par `==`.** C'est ce qui rend ce programme sans danger, et
  ce n'est pas un hasard : trois constantes nommées, trois comparaisons exactes, aucune
  heuristique sur l'extension. Un code écrit comme ça se laisse étendre sans risque
  trois versions plus tard.
- **L'environnement à approbation** a redemandé le clic, comme au programme 18. Trois
  runs de distribution, trois approbations distinctes.
- **Les deux garde-fous du dépôt** sont restés verts à chaque étape — avant la fusion,
  après la fusion, avant chaque push.
- **Le corps de la release s'est allongé sans que le début bouge d'un caractère**,
  vérifié par `diff` avant envoi. Un `--notes-file` écrase tout : recopier l'existant et
  y ajouter était la seule façon sûre.

### Ce que j'ai failli casser, et ce que j'ai eu faux

1. **🛑 J'ai failli annoncer une limite système fausse — et trop généreuse.** Le chargeur
   du binaire n'exige que `GLIBC_2.14`. Si je m'étais arrêté là, j'écrivais « ça marche
   depuis 2011 » et des joueurs sur Ubuntu 20.04 auraient téléchargé 37 Mo pour un
   programme qui ne démarre pas. La vraie exigence est dans les **31 bibliothèques
   embarquées** : 102 flux compressés portent des symboles glibc, et le maximum est
   **2.35**. **Un binaire n'a pas une exigence, il a la plus haute des siennes.**
2. **J'ai failli m'arrêter pour la mauvaise raison, et failli continuer pour une
   mauvaise aussi.** L'écart contenait `docs/CONTRIBUER.md` : à la lettre, arrêt. Mais
   décider seul que « c'est juste un doc » aurait été m'arroger l'arbitrage. La sortie
   n'était ni l'un ni l'autre : **mesurer sur le périmètre qui construit le binaire**,
   puis laisser Dan trancher avec ce chiffre-là sous les yeux.
3. **Ma première passe de nettoyage a laissé un commentaire orphelin** qui expliquait un
   mécanisme (`sans-secret`) que je venais de supprimer. Le `grep` de contrôle l'a
   attrapé. Un commentaire qui décrit du code disparu est pire qu'un commentaire absent.
4. **J'ai perdu le relevé d'avant en le demandant mal.** `gh release view --json isLatest`
   n'existe pas : la commande a échoué et la chaîne `&&` a sauté mon relevé de l'état
   initial des assets. Je l'avais heureusement pris au bloc 0 — mais c'est de la chance,
   pas de la méthode. **Un relevé d'avant se fait AVANT, et on vérifie qu'on l'a.**
5. **Je ne peux pas lancer de binaire Linux ici** et je l'ai découvert au moment de le
   faire, pas en le prévoyant. La preuve reste solide, mais elle est transitive — et
   c'est écrit comme tel plutôt que maquillé en « lancé et vérifié ».
