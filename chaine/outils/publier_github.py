# -*- coding: utf-8 -*-
"""
Publie une nouvelle version sur GitHub Releases, en une commande.

Chaque version = un lien permanent que vous collez sur Discord. « Latest »
pointe toujours sur la plus récente, donc le lien du README ne change jamais.

Ce que fait le script :
  1. régénère l'installateur et les zips (outils/empaqueter.py) ;
  2. crée la release et y attache l'exe + le zip complet.

Prérequis (une seule fois) :
  - installer l'outil GitHub :   winget install GitHub.cli
  - se connecter :               gh auth login
  - avoir créé le dépôt et l'avoir lié (voir le guide dans la réponse).

Usage :
  python outils/publier_github.py 1.1 "Recettes de cuisine traduites"
                                   ^version  ^note affichée sur la release
"""
import os
import subprocess
import sys
import time

# La console Windows est en cp1252 : elle ne sait pas écrire « ≤ », « — »
# ni un accent venu d'un outil enfant. Sans cette ligne, publier_github
# MEURT au moment d'afficher la sortie du builder de zip (vécu le
# 29/07/2026, juste avant la 3.4.0 : le banc de santé a introduit un
# « ≤ » dans son relevé). Un plantage d'ENCODAGE ne doit jamais empêcher
# une publication — ni, pire, la couper en deux.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(BASE, "dist")
# gh découvre le dépôt depuis le dossier courant : la release doit donc se
# créer DEPUIS le dépôt (depot_github), pas depuis le pipeline (traduction).
DEPOT = os.path.join(BASE, "depot_github")
# Le dépôt public, pour bâtir des URL ABSOLUES dans le corps de la release
# (les liens relatifs d'un README ne résolvent pas depuis /releases/tag/vX).
DEPOT_GH = "LePetitDan/AscensionFR"
# Deux livrables : le zip manuel (que des fichiers d'addon) et, s'il a été
# construit, le Compagnon (appli OPTIONNELLE : mise à jour en un clic + envoi
# de rapport ; source publiée dans compagnon/ du dépôt).
ZIP_MANUEL = os.path.join(DIST, "AscensionFR_manuel.zip")
EXE_COMPAGNON = os.path.join(BASE, "compagnon", "dist",
                             "AscensionFR_Compagnon.exe")


def gh_present():
    for exe in ("gh", "gh.exe"):
        try:
            subprocess.run([exe, "--version"], capture_output=True, check=True)
            return exe
        except Exception:
            continue
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage : python outils/publier_github.py <version> [note]")
        print("Exemple : python outils/publier_github.py 1.1 "
              "\"Recettes de cuisine traduites\"")
        return 1
    version = sys.argv[1].lstrip("v")
    note = sys.argv[2] if len(sys.argv) > 2 else "Nouvelle version."
    tag = "v" + version

    # Garde-fou (audit du 20/07/2026, DURCI le 28/07/2026). DOCTRINE DE DAN :
    # une mise à jour = UN numéro — le tag, le « ## Version: » du .toc vivant
    # et VERSION_COMPAGNON (compagnon/compagnon.py) doivent être IDENTIQUES.
    # La 3.3.1 « Hub seul » (publiée hors de ce script, tag 3.3.1 sur un .toc
    # resté 3.3.0) a mis TOUS les utilisateurs du Hub dans une boucle de mise
    # à jour infinie : le Hub compare le .toc au tag et proposait la mise à
    # jour pour toujours. Aucune option pour passer outre — si seul le Hub
    # change, la version entière monte quand même et les deux sortent
    # ensemble.
    import re as _re
    toc = os.path.join(BASE, "..", "WOW_Priv", "resources", "ascension-live",
                       "Interface", "AddOns", "AscensionFR",
                       "AscensionFR.toc")
    toc = os.path.normpath(toc)
    try:
        with open(toc, encoding="utf-8") as f:
            m = _re.search(r"##\s*Version:\s*(\S+)", f.read())
        version_toc = m.group(1) if m else "?"
    except OSError:
        version_toc = "?"
    source_compagnon = os.path.join(BASE, "compagnon", "compagnon.py")
    try:
        with open(source_compagnon, encoding="utf-8") as f:
            m = _re.search(r'VERSION_COMPAGNON\s*=\s*"([^"]+)"', f.read())
        version_hub = m.group(1) if m else "?"
    except OSError:
        version_hub = "?"
    if not (version == version_toc == version_hub):
        print("! Les trois numéros ne coïncident pas — RIEN n'est publié :")
        print("    tag demandé        : %s" % version)
        print("    .toc vivant        : %s" % version_toc)
        print("    VERSION_COMPAGNON  : %s" % version_hub)
        print("  Doctrine : une mise à jour = un numéro, le Hub porte")
        print("  toujours le même que l'addon. Aligne les trois, reconstruis")
        print("  l'exe, puis relance. (Il n'y a pas d'option pour forcer.)")
        return 1

    # L'ARBRE QU'ON TAGUE DOIT ÊTRE CELUI QU'ON VIENT DE CONSTRUIRE
    # (geste 9 du programme 7, 31/07/2026).
    #
    # La barrière des trois versions ci-dessus est juste, mais elle lit
    # l'arbre PRIVÉ — celui qui construit. Le 29/07, le tag v3.4.0 a été posé
    # sur un dépôt public resté au code de la 3.1.0 : les trois numéros
    # coïncidaient parfaitement… dans le mauvais dépôt. Les assets livrés
    # étaient justes, le lien « code source » renvoyait trois publications en
    # arrière — et notre seule réponse aux joueurs quand un antivirus supprime
    # l'exe, c'est « le code est ouvert, allez voir ».
    #
    # verifier_arbre_publie.py regarde l'arbre PUBLIÉ : rien en attente,
    # sources identiques au privé neutralisé, VERSION_COMPAGNON conforme, et
    # aucun motif de secret (toutes extensions, sans liste). Comme pour les
    # trois versions : PAS D'OPTION POUR FORCER.
    print("Vérification de l'arbre publié...")
    controle = subprocess.run(
        [sys.executable, os.path.join(BASE, "outils",
                                      "verifier_arbre_publie.py"),
         "--version", version, "--avec-historique"])
    if controle.returncode != 0:
        print("! PUBLICATION REFUSÉE : le dépôt public ne correspond pas à ce")
        print("  qui vient d'être construit (détail ci-dessus).")
        print("  Remède :  python outils/synchroniser_depot_public.py --appliquer")
        print("            puis commite et pousse le dépôt public.")
        print("  (Il n'y a pas d'option pour forcer.)")
        return 1

    gh = gh_present()
    if not gh:
        print("! L'outil 'gh' n'est pas installé ou pas dans le PATH.")
        print("  Installez-le :  winget install GitHub.cli")
        print("  Puis :          gh auth login")
        return 1

    # 1. Régénérer le zip d'installation manuelle. C'est construire_zip_release
    #    qui le fait (et plus empaqueter.py) : les deux écrivaient le MÊME
    #    fichier avec des contenus différents, celui qui passait en dernier
    #    gagnait. Le builder de release porte les garde-fous (pseudos des
    #    récolteurs, webhook, jeton, cohérence de version) et rend un code de
    #    sortie — un zip qui rate ne doit pas partir en release.
    print("Régénération du zip d'installation manuelle...")
    # encoding= explicite : l'enfant écrit de l'UTF-8 (il fait
    # sys.stdout.reconfigure), alors que `text=True` seul décoderait en
    # cp1252 sous Windows — les diagnostics de publication sortaient en
    # charabia, juste au moment où il faut les lire.
    r = subprocess.run([sys.executable,
                        os.path.join(BASE, "outils",
                                     "construire_zip_release.py")],
                       capture_output=True, encoding="utf-8",
                       errors="replace")
    print(r.stdout.strip())
    if r.returncode != 0 or not os.path.exists(ZIP_MANUEL):
        print("! Le zip n'a pas été produit, ou ses garde-fous ont sauté.")
        print(r.stderr.strip())
        return 1

    # 2. Créer la release et y joindre les livrables.
    titre = "Ascension FR " + tag
    # Deux chemins, annoncés dès la première ligne. Le zip passe DEVANT :
    # depuis la 2.2.1, cinq joueurs ont vu Windows Defender supprimer l'exe
    # (non signé, faux positif). Un lien direct, permanent, qui ne demande
    # d'exécuter rien du tout, vaut mieux qu'une ligne de secours en bas de
    # page — d'autant qu'il ne dépend pas de la version : GitHub redirige
    # toujours « releases/latest/download/… » vers la dernière.
    corps = (note + "\n\n"
             "## Deux façons d'installer\n\n"
             "**1 — Le zip, rien à exécuter** (recommandé si votre antivirus "
             "râle) : "
             # URL ABSOLUE, pas relative : le corps d'une release est rendu
             # depuis /releases/tag/vX, où les « ../../ » ne résolvent pas
             # comme dans un README. C'est LE lien de secours des joueurs
             # bloqués par Defender — il n'a pas le droit d'être cassé.
             "[⬇️ AscensionFR_manuel.zip](https://github.com/" + DEPOT_GH
             + "/releases/latest/download/AscensionFR_manuel.zip)\n\n"
             "1. Téléchargez le zip.\n"
             "2. Extrayez-le dans le dossier de votre jeu Ascension — celui "
             "qui contient `Ascension.exe` et les dossiers `Data` et "
             "`Interface` (souvent `…\\resources\\ascension-live`). **Pas "
             "dans `Interface\\AddOns`**. Dites « oui » pour fusionner le "
             "dossier `Interface`.\n"
             "3. En jeu, à l'écran de sélection des personnages : bouton "
             "**AddOns** (en bas à gauche) → cochez **« Allow Non-Launcher "
             "AddOns »** (juste au-dessus de « Load out of date AddOns ») → "
             "vérifiez qu'AscensionFR est coché → Appliquer.\n"
             "4. En jeu, tapez `/afr` et vérifiez que « Activer la "
             "traduction » est bien cochée.\n\n"
             "Le zip ne contient que des fichiers de traduction "
             "(`.lua` / `.xml`) : aucun programme, rien ne s'exécute.\n\n"
             "**2 — Le Hub** (optionnel) : `AscensionFR_Compagnon.exe` — "
             "installe, met à jour, vérifie votre installation et sait tout "
             "désinstaller. [Code source ouvert](https://github.com/"
             + DEPOT_GH + "/tree/main/compagnon). "
             "Il n'est pas signé : Windows SmartScreen demande confirmation "
             "(« Informations complémentaires » → « Exécuter quand même ») et "
             "certains antivirus le suppriment carrément. Dans ce cas, "
             "prenez le zip ci-dessus — vous n'y perdez que les mises à jour "
             "en un clic.")
    fichiers = [ZIP_MANUEL]
    if os.path.exists(EXE_COMPAGNON):
        # GARDE-FOU (19/07/2026, ÉLARGI le 28/07/2026). empaqueter.py ne
        # construit QUE le zip : l'exe, lui, doit être compilé à part avec
        # PyInstaller. On a donc publié plusieurs versions de suite en y
        # attachant un exe périmé, resté à VERSION_COMPAGNON = 1.6.5 : tous
        # les joueurs voyaient en permanence « nouvelle version disponible »,
        # et la mise à jour ne l'effaçait jamais. Rien ne l'avait signalé.
        # Élargi : l'exe du Hub embarque TOUTES les sources du dossier
        # compagnon/ et ses assets — comparer au seul compagnon.py laissait
        # passer un exe périmé après une retouche d'interface_hub.py ou un
        # décor recuit (c'est le cas « deux Hub différents portent le même
        # numéro » du 28/07).
        dossier_compagnon = os.path.join(BASE, "compagnon")
        plus_recent, temoin = 0, "?"
        # ⚠️ NE JAMAIS nommer ces variables `fichiers` : c'est le nom de la
        # LISTE DES ASSETS juste au-dessus. Le 29/07/2026, à la publication
        # de la 3.4.0, os.walk l'a écrasée avec les noms de fichiers du
        # dernier dossier parcouru — `gh release create` recevait des noms
        # nus au lieu des deux livrables et échouait. Défaut d'autant plus
        # méchant qu'il ne se déclenche QUE si l'exe existe (donc jamais en
        # essai à vide) et que le message d'erreur de gh ne remontait pas.
        for racine, sous_dossiers, noms in os.walk(dossier_compagnon):
            # build/ et dist/ sont des PRODUITS de PyInstaller, pas des
            # sources : les compter rendrait l'exe toujours « périmé ».
            sous_dossiers[:] = [d for d in sous_dossiers
                                if d not in ("build", "dist", "__pycache__",
                                             "archive")]
            for f in noms:
                chemin = os.path.join(racine, f)
                try:
                    t = os.path.getmtime(chemin)
                except OSError:
                    continue
                if t > plus_recent:
                    plus_recent, temoin = t, os.path.relpath(
                        chemin, dossier_compagnon)
        if os.path.getmtime(EXE_COMPAGNON) < plus_recent:
            print("STOP — l'exe du Hub est plus VIEUX qu'une de ses sources.")
            print("  exe    : %s" % time.strftime(
                "%d/%m %H:%M", time.localtime(os.path.getmtime(EXE_COMPAGNON))))
            print("  source : %s (%s)" % (time.strftime(
                "%d/%m %H:%M", time.localtime(plus_recent)), temoin))
            print()
            print("Reconstruis-le avant de publier :")
            print("  cd compagnon && python -m PyInstaller --noconfirm "
                  "AscensionFR_Hub.spec")
            return 1
        fichiers.append(EXE_COMPAGNON)
    else:
        print("(Compagnon absent — release avec le zip seul.)")
    # Contrôle des assets JUSTE avant l'envoi : chacun doit exister sur le
    # disque. Sans lui, une liste abîmée en amont (voir le garde-fou
    # ci-dessus) part telle quelle et on ne l'apprend que par l'échec de gh.
    absents = [f for f in fichiers if not os.path.isfile(f)]
    if absents:
        print("! Assets introuvables — RIEN n'est publié :")
        for f in absents:
            print("    %s" % f)
        return 1
    print("Assets à joindre :")
    for f in fichiers:
        print("  %-28s %5.1f Mo" % (os.path.basename(f),
                                    os.path.getsize(f) / 1048576.0))
    commande = [gh, "release", "create", tag] + fichiers + [
                "--title", titre, "--notes", corps, "--latest"]
    print("Création de la release %s..." % tag)
    # La sortie de gh est CAPTURÉE et réaffichée : sans cela son message
    # d'erreur n'arrivait pas jusqu'ici (« La création a échoué » tout seul,
    # sans la raison — 29/07/2026).
    r = subprocess.run(commande, capture_output=True, encoding="utf-8",
                       errors="replace", cwd=DEPOT)
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.returncode != 0:
        print("! La création a échoué. Message de gh :")
        print((r.stderr or "(aucun message)").strip())
        return 1
    print()
    print("Publié ! Lien permanent à coller sur Discord :")
    url = subprocess.run([gh, "repo", "view", "--json", "url", "--jq", ".url"],
                         capture_output=True, encoding="utf-8",
                         errors="replace", cwd=DEPOT)
    depot = (url.stdout or "").strip()
    if depot:
        print("  " + depot + "/releases/latest")
    else:
        print("  https://github.com/<vous>/<depot>/releases/latest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
