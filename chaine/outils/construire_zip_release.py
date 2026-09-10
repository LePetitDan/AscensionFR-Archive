# -*- coding: utf-8 -*-
"""Construit le ZIP d'installation MANUELLE publié à chaque version.

    python outils/construire_zip_release.py [--jeu <dossier>]

Sortie : dist\\AscensionFR_manuel.zip — que des fichiers d'addon (.lua/.xml),
aucun exécutable. C'est la porte de secours pour les joueurs dont l'antivirus
bloque le Hub : depuis la 2.2.1, cinq d'entre eux n'ont pas pu le lancer, dont
un qui n'y est JAMAIS arrivé (« même si je l'exécute il le supprime »). L'exe
n'est pas signé ; Defender le prend pour un trojan. Tant que le faux positif
n'est pas levé, ce zip est leur seule solution — il doit donc être produit à
CHAQUE version, sans y penser, et être visible sur la page de téléchargement
(voir depot_github/README.md).

Le nom du fichier est FIGÉ : les Compagnons et Hubs déjà installés chez les
joueurs cherchent « AscensionFR_manuel.zip » par nom exact
(compagnon.py:ZIP_ATTENDU). Ne jamais le renommer.

Ce que ce script corrige par rapport à sa première version (26/07/2026) :
  - la version attendue n'est plus écrite en dur : elle est LUE dans le .toc
    vivant (il fallait éditer le script à chaque sortie, et l'oublier ne se
    voyait pas) ;
  - les chemins sont déduits du dépôt, plus codés en absolu ;
  - la liste des dossiers à emballer est explicite (elle était recopiée du
    zip précédent : un dossier NOUVEAU n'y serait jamais entré) — on compare
    quand même avec le zip précédent pour signaler une DISPARITION ;
  - LISEZ-MOI.txt est de nouveau dedans (il était perdu par le recopiage) ;
  - le script rend un code de sortie : un enchaînement automatique voit enfin
    l'échec des garde-fous.

LA BARRIÈRE (26/07/2026, après l'affaire DB_Objets)
---------------------------------------------------
On est passé près de publier un addon MORT AU CHARGEMENT. Ce script relisait
bien chaque .lua du zip — pour les pseudos, le webhook, un jeton, la version —
mais il n'en COMPILAIT aucun. C'était le dernier endroit où un fichier cassé
pouvait passer. Trois changements :

  1. `verifier_tout.py` est lancé D'ABORD, et un code retour non nul arrête
     tout. Une barrière qu'on peut oublier de lancer n'est pas une barrière.
  2. Chaque .lua embarqué est COMPILÉ en `lupa.lua51` — la version du client,
     jamais le lupa par défaut (5.5), qui accepte ce que 5.1 refuse. Les SEAUX
     des bases paresseuses sont compilés aussi : le jeu les recompile un par
     un à l'exécution, et un seau trop gros échoue en silence.
  3. Le zip est fabriqué SOUS UN NOM PROVISOIRE et n'est mis en place qu'une
     fois tous les contrôles passés. Avant, il était écrit d'abord et vérifié
     ensuite : un zip mort avait déjà remplacé le bon. Même doctrine que le
     garde-fou d'`ecrire_db` — mieux vaut pas de zip qu'un zip mort.
"""
import io
import os
import re
import shutil
import subprocess
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "outils"))
# On réutilise les définitions d'empaqueter.py (l'importer est sans effet de
# bord : tout son travail est sous « if __name__ == "__main__" »). Une seule
# liste de dossiers, un seul LISEZ-MOI, deux scripts d'accord entre eux.
from empaqueter import ESSENTIEL, OPTIONNEL, LISEZMOI_MANUEL  # noqa: E402
from secrets_publication import balayer_texte, lisible  # noqa: E402

DIST = os.path.join(BASE, "dist")
OFFICIEL = os.path.join(DIST, "AscensionFR_manuel.zip")
JEU_DEFAUT = os.path.normpath(os.path.join(BASE, "..", "WOW_Priv",
                                           "resources", "ascension-live"))
GARDE_PSEUDOS = os.path.join(BASE, "noms_recolteurs.local.txt")


def version_du_toc(jeu):
    toc = os.path.join(jeu, "Interface", "AddOns", "AscensionFR",
                       "AscensionFR.toc")
    try:
        with io.open(toc, encoding="utf-8") as f:
            m = re.search(r"##\s*Version:\s*(\S+)", f.read())
        return m.group(1) if m else None
    except OSError:
        return None


def tetes_du_zip(chemin):
    """Les dossiers de tête d'un zip existant — sert uniquement à repérer une
    DISPARITION par rapport à la version précédente."""
    if not os.path.exists(chemin):
        return set()
    tetes = set()
    with zipfile.ZipFile(chemin) as z:
        for n in z.namelist():
            morceaux = n.split("/")
            if len(morceaux) > 2:
                tetes.add("/".join(morceaux[:3] if morceaux[1] == "AddOns"
                                   else morceaux[:2]))
            elif len(morceaux) == 2 and morceaux[1]:
                tetes.add("/".join(morceaux[:2]))
    return tetes


def fichiers_du_toc(dossier_addon):
    """L'ensemble des chemins relatifs AUTORISÉS dans un arbre d'addon :
    les fichiers déclarés par son .toc, plus le .toc lui-même et
    Bindings.xml (chargé d'office par le client). Rend None si le dossier
    n'a pas de .toc — dans ce cas on n'exclut rien (PTRXML n'est pas un
    addon)."""
    nom = os.path.basename(dossier_addon.rstrip("\\/"))
    toc = os.path.join(dossier_addon, nom + ".toc")
    if not os.path.exists(toc):
        return None
    autorises = {(nom + ".toc").lower(), "bindings.xml"}
    with io.open(toc, encoding="utf-8", errors="replace") as f:
        for ligne in f:
            ligne = ligne.strip()
            if ligne and not ligne.startswith("#"):
                autorises.add(ligne.replace("\\", "/").lower())
    return autorises


def barriere_verifier_tout():
    """Lance outils/verifier_tout.py. False = on n'emballe rien."""
    script = os.path.join(BASE, "outils", "verifier_tout.py")
    print("=== Barrière : verifier_tout.py ===")
    r = subprocess.run([sys.executable, script], cwd=BASE)
    if r.returncode != 0:
        print("! verifier_tout.py rend %d — on n'emballe rien." % r.returncode)
        return False
    print("=== Barrière franchie ===")
    return True


def compiler_lua_du_zip(chemin_zip):
    """Compile en Lua 5.1 chaque .lua du zip, seaux compris. -> [échecs]."""
    import mesurer_constantes
    echecs = []
    with zipfile.ZipFile(chemin_zip) as z:
        noms = [n for n in z.namelist() if n.endswith(".lua")]
        print("compilation Lua 5.1 de %d fichier(s) du zip..." % len(noms))
        for n in noms:
            octets = z.read(n)
            compile_ok, _k, message = mesurer_constantes.mesurer(octets, n)
            if not compile_ok:
                echecs.append((n, message))
                continue
            # Les seaux d'une base paresseuse sont recompilés PAR LE JEU, un
            # par un : le fichier peut compiler alors qu'un seau échouera.
            texte = octets.decode("utf-8", "replace")
            _n, _pire, casses = mesurer_constantes.mesurer_seaux_texte(texte)
            if casses:
                echecs.append((n, "un seau ne compile pas : %s" % casses[0]))
    return echecs


def main():
    jeu = JEU_DEFAUT
    if "--jeu" in sys.argv:
        jeu = sys.argv[sys.argv.index("--jeu") + 1]
    interface = os.path.join(jeu, "Interface")
    if not os.path.isdir(interface):
        print("! dossier de jeu introuvable :", jeu)
        return 1

    # Pas d'échappatoire : Dan ne doit plus pouvoir construire une release sans
    # que la barrière soit passée. (verifier_tout lit l'addon VIVANT ; si on
    # emballe un autre arbre avec --jeu, c'est la compilation du zip, plus bas,
    # qui couvre cet arbre-là.)
    if not barriere_verifier_tout():
        return 1

    # LA DEUXIÈME BARRIÈRE (bloc D1, 29/07/2026) : le banc de santé qui
    # mord — banc moteur population entière, suite des bancs avec codes
    # attendus, webhook, fraîcheur de la veille, santé du dernier passage
    # de l'Atelier. verifier_tout compile ; le banc de santé EXÉCUTE.
    print("=== Barrière : banc_sante.py ===")
    code_sante = subprocess.call(
        [sys.executable, os.path.join(BASE, "outils", "banc_sante.py")])
    if code_sante != 0:
        print("! banc de santé ROUGE — rien n'est emballé.")
        return 1
    print("=== Barrière franchie ===")

    version = version_du_toc(jeu)
    if not version:
        print("! version illisible dans AscensionFR.toc — rien n'est emballé.")
        return 1
    print("version du .toc vivant :", version)

    arbre = [os.path.join("Interface", d) for d in ESSENTIEL + [OPTIONNEL]]
    manquants = [d for d in arbre if not os.path.isdir(os.path.join(jeu, d))]
    if manquants:
        print("! dossiers absents, rien n'est emballé :", ", ".join(manquants))
        return 1

    # (L'archivage de la version précédente a lieu PLUS BAS, une fois les
    # contrôles passés : archiver ici en aurait gardé une copie même quand le
    # zip neuf est refusé.)
    avant = tetes_du_zip(OFFICIEL)

    # NOM PROVISOIRE. Le zip officiel n'est remplacé qu'une fois TOUS les
    # contrôles passés : avant, on écrivait d'abord et on vérifiait ensuite,
    # donc un zip mort avait déjà pris la place du bon. Même doctrine que le
    # garde-fou d'ecrire_db — mieux vaut pas de zip qu'un zip mort.
    provisoire = OFFICIEL + ".neuf"
    os.makedirs(DIST, exist_ok=True)
    nb = 0
    # LE GARDE DU CONTENU (bloc D2, 29/07/2026). Le zip embarquait TOUT
    # l'arbre : DB_sauvegarde_build/ — un dossier de sauvegarde mort —
    # pesait 42 % du zip publié (19,5 Mo), livré aux joueurs depuis la
    # 3.3.0. Règle : dans un arbre d'ADDON, seul entre ce que son .toc
    # déclare (plus le .toc et Bindings.xml). Chaque écart est listé —
    # bruyant, jamais silencieux.
    ecartes, poids_ecarte = [], 0
    with zipfile.ZipFile(provisoire, "w", zipfile.ZIP_DEFLATED,
                         compresslevel=9) as sortie:
        for tete in arbre:
            local = os.path.join(jeu, tete)
            autorises = fichiers_du_toc(local)
            for dossier, _s, fichiers in os.walk(local):
                for f in fichiers:
                    chemin = os.path.join(dossier, f)
                    relatif = os.path.relpath(chemin, local).replace(
                        os.sep, "/")
                    if autorises is not None \
                            and relatif.lower() not in autorises:
                        ecartes.append("%s/%s" % (tete.replace(os.sep, "/"),
                                                  relatif))
                        poids_ecarte += os.path.getsize(chemin)
                        continue
                    arc = os.path.relpath(chemin, jeu).replace(os.sep, "/")
                    sortie.write(chemin, arc)
                    nb += 1
        sortie.writestr("LISEZ-MOI.txt",
                        LISEZMOI_MANUEL.replace("\n", "\r\n"))
        nb += 1
    if ecartes:
        print("poids mort ÉCARTÉ du zip (hors .toc) : %d fichier(s), "
              "%.1f Mo" % (len(ecartes), poids_ecarte / 1048576.0))
        tetes_ecartees = sorted({e.split("/")[3] if e.count("/") >= 3 else e
                                 for e in ecartes})
        for t in tetes_ecartees[:8]:
            print("   -", t)

    taille = os.path.getsize(provisoire)
    print("fabriqué (provisoire) : %d fichiers, %.1f Mo"
          % (nb, taille / 1048576.0))

    # Régression : un dossier présent dans la version précédente et absent de
    # celle-ci est presque toujours un oubli, jamais une décision.
    apres = tetes_du_zip(provisoire)
    perdus = sorted(t for t in avant - apres if t != "LISEZ-MOI.txt")
    for t in perdus:
        print("! présent dans le zip précédent, ABSENT ici :", t)

    # COMPILATION LUA 5.1 de tout ce qui part chez les joueurs. C'était le
    # dernier trou : on relisait les .lua (pseudos, webhook, version) sans en
    # compiler un seul. Un fichier qui ne compile pas, c'est l'addon mort au
    # chargement — et on est passé près, avec DB_Objets.
    echecs_lua = compiler_lua_du_zip(provisoire)
    for nom, message in echecs_lua:
        print("LUA CASSÉ :", nom, "->", message)

    # ------------------------------------------------------- garde-fous
    pseudos = []
    if os.path.exists(GARDE_PSEUDOS):
        pseudos = [l.strip() for l in io.open(GARDE_PSEUDOS, encoding="utf-8")
                   if l.strip()]
    re_pseudos = re.compile(
        r"(?<![A-Za-z])(" + "|".join(re.escape(p) for p in pseudos)
        + r")(?![A-Za-z])") if pseudos else None

    soucis = len(perdus) + len(echecs_lua)
    with zipfile.ZipFile(provisoire) as z:
        for n in z.namelist():
            if n.endswith(".local.txt") or "aspirateur" in n:
                print("FICHIER SENSIBLE :", n)
                soucis += 1
            # LE BALAYAGE DE SECRETS, sur TOUTE extension (programme 6).
            # C'était le trou : ce contrôle ne lisait que les cinq
            # extensions ci-dessous, et sautait donc les .py — c'est-à-dire
            # exactement le type de fichier qui portait le webhook vivant.
            # Le balayage vient de outils/secrets_publication.py, le même
            # que celui du garde-fou de publication : un seul jeu de motifs,
            # tenu à un seul endroit.
            if lisible(n):
                t = z.read(n).decode("utf-8", "replace")
                for etiquette, extrait, ligne in balayer_texte(n, t):
                    print("SECRET dans %s:%d — %s : %s"
                          % (n, ligne, etiquette, extrait))
                    soucis += 1

            if not n.endswith((".lua", ".toc", ".txt", ".md", ".xml")):
                continue
            t = z.read(n).decode("utf-8", "replace")
            if re_pseudos and re_pseudos.search(t):
                print("PSEUDO restant dans", n, ":",
                      re_pseudos.search(t).group(0))
                soucis += 1
            if n.endswith("AscensionFR.toc") and (
                    "## Version: %s" % version) not in t:
                print("version incohérente dans", n)
                soucis += 1
    if soucis:
        # Le zip officiel n'a pas bougé : celui d'hier vaut mieux qu'un neuf
        # cassé. On garde le provisoire pour pouvoir l'inspecter.
        print("%d SOUCI(S) — NE PAS PUBLIER. Le zip officiel est INCHANGÉ ; "
              "le neuf attend dans %s" % (soucis, os.path.basename(provisoire)))
        return 1
    # Tout est propre : on archive l'ancien sous SA vraie version (avant, le nom
    # était figé à « _1.7.5 » et l'archive ne bougeait plus jamais), puis on met
    # le neuf en place. L'archivage n'a lieu qu'ICI : archiver avant les
    # contrôles aurait conservé une copie même quand le neuf est refusé.
    if os.path.exists(OFFICIEL):
        precedente = "?"
        try:
            with zipfile.ZipFile(OFFICIEL) as z:
                nom = "Interface/AddOns/AscensionFR/AscensionFR.toc"
                m = re.search(r"##\s*Version:\s*(\S+)",
                              z.read(nom).decode("utf-8", "replace"))
                precedente = m.group(1) if m else "?"
        except (KeyError, OSError, zipfile.BadZipFile):
            pass
        archive = os.path.join(DIST, "AscensionFR_manuel_%s.zip" % precedente)
        if not os.path.exists(archive):
            shutil.copy2(OFFICIEL, archive)
            print("version précédente archivée :", os.path.basename(archive))

    os.replace(provisoire, OFFICIEL)
    print("garde-fous : TOUT PROPRE")
    print("écrit : %s (%d fichiers, %.1f Mo)"
          % (OFFICIEL, nb, taille / 1048576.0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
