# Demande de code → Claude Code

**Date :** 2026-07-28 · **publier le guide dans `#📖-installation`**

> Dan a **validé les six messages** et demandé qu'ils soient publiés. C'est donc un « go »
> explicite au sens de la règle n° 1 — mais seulement pour **ces six textes, dans ce salon**.

---

## Pourquoi maintenant

En dix jours, **12 joueurs** se sont bloqués à l'installation, toujours sur **les 3 mêmes
causes**. Environ **30 joueurs** ont posé six questions qui reviennent en boucle. Et deux
conseils **faux** circulent aujourd'hui sur le serveur :

- *« pointe le dossier interface »* — c'est exactement le pire piège : le Hub y installe, y
  relit un vrai `.toc`, affiche **« tu es à jour »**, et le jeu ne charge rien ;
- *« pour revoir l'anglais, désactive l'addon »* — la case « Activer la traduction » le fait
  proprement.

Le salon `📖-installation` est **vide** (vidé exprès, c'est le salon « mode d'emploi »).

## 1. D'abord, vérifier — ne rien publier si ça coince

Le bot `AspirateurFR#1426` a, sur ce salon, un accès noté « **voir seulement, pas
d'historique** » : c'est le seul angle mort de sa carte de permissions.

**Avant toute écriture, vérifie qu'il a bien :**
- **Voir le salon** et **Lire l'historique** (sans ça, le garde-fou anti-doublon ci-dessous
  ne peut pas fonctionner) ;
- **Envoyer des messages** ;
- **Gérer les messages** (nécessaire pour épingler).

🛑 **S'il manque un droit : n'écris rien.** Dis-moi précisément lequel et où Dan doit le
cocher côté Discord. C'est une manipulation de trente secondes pour lui, et c'est mieux que
six messages postés à moitié.

## 2. Le garde-fou anti-doublon

Le salon doit être **vide de nos messages**. S'il contient déjà un message du bot ou un des
six textes, **arrête-toi et dis-le** : une demande relancée ne doit jamais publier deux fois.

## 3. Publier les six messages, dans cet ordre, puis les épingler tous les six

Texte **mot pour mot** — ne rien reformuler, Dan les a relus.

---

### Message 1

```
📥 **Installer AscensionFR**

Deux façons, même résultat. Choisis celle que tu veux.

**🖥️ Avec le Hub** — le plus simple
1. Télécharge `AscensionFR_Compagnon.exe` : <https://github.com/LePetitDan/AscensionFR/releases/latest>
2. Double-clique dessus : il trouve ton jeu tout seul.
3. « Installer la traduction », puis « Vérifier mon installation ». C'est fini. 🎉

**📁 À la main** — si ton antivirus râle, ou si tu préfères ne rien exécuter
1. Télécharge le zip : <https://github.com/LePetitDan/AscensionFR/releases/latest/download/AscensionFR_manuel.zip>
   Que des fichiers texte, aucun programme.
2. **Extrais-le dans le dossier de ton jeu** — celui qui contient `Ascension.exe`, `Data` et `Interface`. Souvent `…\resources\ascension-live`.
   ⚠️ **Surtout pas dans `Interface\AddOns`.** Le zip apporte déjà l'arborescence : tu obtiendrais `Interface\AddOns\Interface\AddOns\AscensionFR`, que le jeu ne lira jamais.
   Windows propose de **fusionner** le dossier `Interface` → dis **oui**. Ça n'efface aucun de tes autres addons.

**Puis, dans les deux cas :**
3. Lance le jeu jusqu'à l'écran des personnages. En bas à gauche, bouton **AddOns** :
   • coche **« Allow Non-Launcher AddOns »** — juste au-dessus de « Load out of date AddOns ». **Obligatoire pour tout le monde**, sans elle le jeu refuse de charger la traduction.
   • vérifie qu'**AscensionFR** est coché dans la liste.
   • puis **Applique**.
4. En jeu, tape **`/afr`** et vérifie que **« Activer la traduction »** est cochée.

✅ Au final tu dois avoir `Interface\AddOns\AscensionFR`, `Interface\AddOns\AscensionFR_Repliques` et `Interface\PTRXML`.
```

### Message 2

```
🚑 **« J'ai installé et le jeu est toujours en anglais »**

Trois causes, toujours les mêmes. Vérifie dans cet ordre.

**① Le zip est au mauvais endroit.**
Tu dois avoir `Interface\AddOns\AscensionFR`.
Si tu as `Interface\AddOns\Interface\AddOns\AscensionFR`, c'est raté : le zip a été extrait dans `Interface\AddOns` au lieu du dossier du jeu.
⚠️ **Ne pointe jamais le Hub sur le dossier `Interface`.** Il doit pointer sur le dossier qui contient `Ascension.exe` et `Data`. Sinon tout a l'air normal, le Hub dit même « tu es à jour »… et le jeu ne charge rien.

**② La case « Allow Non-Launcher AddOns » n'est pas cochée.**
Écran de sélection des personnages → bouton **AddOns** en bas à gauche → la case **juste au-dessus** de « Load out of date AddOns ».
🔎 Le signe qui ne trompe pas : si la ligne AscensionFR affiche **« Not a Launcher AddOn »**, c'est qu'elle est décochée.
Cette case est **obligatoire pour 100 % des joueurs**, et aucun programme ne peut la cocher à ta place : elle ne vit qu'en mémoire du jeu.

**③ « Activer la traduction » est décochée.**
En jeu : **`/afr`** → coche-la.

**Le raccourci :** dans le Hub, **« Vérifier mon installation »** contrôle les trois d'un coup et répare ce qui peut l'être.
```

### Message 3

```
🔄 **Mettre à jour — et savoir si tu es à jour**

**Avec le Hub :** il te prévient tout seul, un clic et c'est fait. Rien à surveiller.

**À la main :** re-télécharge le zip et extrais-le par-dessus (dis « oui » pour remplacer). Tes réglages sont conservés.

**Ensuite :** un `/reload` en jeu suffit la plupart du temps.
⚠️ **Sauf quand une version ajoute de nouveaux fichiers** : il faut alors **relancer le jeu complètement**. Le patch-note le précise quand c'est le cas.

**« Suis-je à jour ? »**
Le Hub te le dit à l'ouverture. S'il ne te propose rien, c'est que tu l'es.

⚠️ **Bug connu en ce moment :** si le Hub te repropose la **même** mise à jour 3.3.1 à chaque ouverture, ce n'est pas toi — c'est un défaut de cette version. **Tu es bien à jour.** C'est corrigé dans la prochaine.
```

### Message 4

```
🇬🇧 **Remettre le jeu en anglais**

**La bonne méthode :** en jeu, tape **`/afr`** et **décoche « Activer la traduction »**.
Encore plus rapide : **clic droit sur le bouton de la minicarte**.

C'est immédiat, réversible, et ça ne touche à rien d'autre.

❌ **Ne désactive pas l'addon** dans la liste des AddOns. Ce conseil circule, mais ce n'est pas la bonne façon : tu perds aussi la récolte des textes — celle qui fait avancer la traduction pour tout le monde.

Pour revenir en français : même chemin, tu recoches.
```

### Message 5

```
🗑️ **Désinstaller — la liste complète**

**Avec le Hub :** onglet Traduction → **« Tout désinstaller »**. Il affiche tout ce qu'il va retirer **avant** de le faire, et te dit ce qui n'a pas pu partir. C'est le plus sûr.

**À la main**, ferme le jeu, puis supprime dans le dossier du jeu :
• `AscensionFR` et `AscensionFR_Repliques` → dans `Interface\AddOns\`
• **`PTRXML` → dans `Interface\`** ⚠️ **c'est celui qu'on oublie** : sans lui, les écrans de connexion et de création de personnage restent en français
• `AscensionFR*.lua` → dans `WTF\Account\<ton compte>\SavedVariables\` (tes réglages)
• le dossier `Sound\` à la racine → seulement si tu avais installé les voix françaises. Les sons d'origine reviennent tout seuls.

⚠️ **Vider `%APPDATA%\AscensionFR` ne remet pas le jeu en anglais.** Il n'y a là que les réglages du Hub. Tout ce qui traduit le jeu est dans le dossier du jeu, liste ci-dessus.

✅ **100 % réversible** : aucun fichier d'origine du jeu n'est modifié.

Et si tu veux juste revoir l'anglais **sans rien supprimer** : `/afr` → décoche « Activer la traduction ».
```

### Message 6

```
🛡️ **« Mon antivirus supprime le Hub »**

Ça arrive, et ce n'est pas de ta faute.

**Écran bleu « Windows a protégé votre ordinateur »** : c'est SmartScreen, il alerte sur tout programme non signé. Un certificat coûte plusieurs centaines d'euros par an, pour un projet gratuit.
→ **« Informations complémentaires » → « Exécuter quand même ».**

**Windows Defender supprime carrément le fichier**, même en le relançant ? C'est un **faux positif**, connu depuis la 2.2.1, signalé à Microsoft.
→ **Ne te bats pas avec ton antivirus.** Prends le zip, tu auras exactement la même traduction :
<https://github.com/LePetitDan/AscensionFR/releases/latest/download/AscensionFR_manuel.zip>
Que des fichiers texte, rien à exécuter. Tu perds seulement la mise à jour en un clic.

**Ton jeu est dans `C:\Program Files` ?** Windows protège ce dossier. Le Hub te proposera **« Relancer en administrateur »** : accepte, et tout se déroule normalement.

Le code du Hub est public si tu veux vérifier ce qu'il fait.
```

---

## Repères techniques

- Salon `📖-installation` : **`1527717972397920527`** (identifiant épinglé par la veille dans
  `3-atelier/veille-discord/_etat.json`).
- Jeton du bot : `WorkFlow/discord_aspirateur.json`, clé `jeton`. **Ne jamais l'afficher, ni
  le mettre dans une ligne de commande, ni le recopier dans ta réponse.**
- Les blocs ci-dessus sont **le contenu des messages**, sans les triples accents.
- Les liens sont volontairement entre chevrons `< >` pour que Discord n'affiche pas d'aperçu.

**« Terminé » veut dire :**

> - Les six messages publiés dans l'ordre, **épinglés tous les six**, et leurs identifiants
>   rendus dans ta réponse (pour pouvoir les modifier plus tard sans en reposter).
> - Ou, si un droit manque : **rien de publié**, et la liste exacte de ce que Dan doit cocher.
> - Le jeton n'apparaît nulle part dans ta réponse ni dans un fichier nouveau.

**Validation :**

> Le « go » de Dan porte **sur ces six textes et sur ce salon**. Ne poste rien d'autre, nulle
> part ailleurs. Ne modifie aucun texte, même pour corriger ce qui te semblerait une coquille :
> signale-la-moi plutôt.

---
## Réponse de Claude Code
> (à remplir par Claude Code : droits vérifiés, messages publiés et épinglés, leurs
> identifiants, ou le droit manquant. Puis renommer en _FAIT.)

---
## Réponse — fait par Cowork, pas par Claude Code

**Publié le 28/07/2026 directement par Cowork**, après que Dan lui a donné l'accès complet
au Discord. Les six messages sont en ligne dans `#📖-installation` et **épinglés tous les six**.

Identifiants : 1531624010494906479 · 1531624019915313263 · 1531624028635136101 ·
1531624037611081880 · 1531624045877919785 · 1531624054119993416

Droits vérifiés avant écriture (voir, historique, envoyer, gérer) : les quatre étaient
accordés. Garde-fou anti-doublon passé : aucun message du bot dans le salon avant.

**Ne pas ré-exécuter cette demande** — elle est conservée pour la trace.
