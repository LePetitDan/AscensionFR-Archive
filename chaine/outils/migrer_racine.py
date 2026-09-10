# -*- coding: utf-8 -*-
"""Migre la RACINE du projet dans tous les chemins EN DUR des scripts.

Nos scripts ont « D:\\WOW_Priv » écrit en dur (~109 fois). Si on déplace le
dossier (ex. vers D:\\AscensionFR), il faut corriger ces chemins, sinon le
pipeline ne trouve plus rien.

Marche à suivre : déplacer le dossier, PUIS lancer ceci DANS la nouvelle
arborescence.

  python outils/migrer_racine.py                              # simulation
  python outils/migrer_racine.py --appliquer                  # applique + .bak
  python outils/migrer_racine.py --de "D:\\WOW_Priv" --vers "D:\\AscensionFR"

Par défaut : de = D:\\WOW_Priv, vers = D:\\AscensionFR. Traite les variantes
« \\ » et « / ». Sauvegarde chaque fichier modifié en *.bak-migration.
"""
import os
import sys
import shutil

DEF_DE = r"D:\AscensionFR\WOW_Priv"
DEF_VERS = r"D:\AscensionFR"
RACINE_SCAN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # dossier 'traduction'
EXTS = (".py", ".md", ".json", ".txt", ".bat", ".spec", ".cs", ".xml", ".ini")
EXCLUS = {"sources", "dist", "Ajouter par Dan", "extraits", "archive",
          "depot_github", "build", "__pycache__", ".git", "a_traduire"}


def arg(nom, defaut):
    return sys.argv[sys.argv.index(nom) + 1] if nom in sys.argv else defaut


def variantes(chemin):
    return [chemin, chemin.replace("\\", "/")]


def main():
    de, vers = arg("--de", DEF_DE), arg("--vers", DEF_VERS)
    appliquer = "--appliquer" in sys.argv
    paires = list(zip(variantes(de), variantes(vers)))
    print("Migration racine : %s  ->  %s" % (de, vers))
    print("Dossier scanné    : %s\n" % RACINE_SCAN)

    nb_f, nb_occ = 0, 0
    for dossier, sous, fichiers in os.walk(RACINE_SCAN):
        sous[:] = [d for d in sous if d not in EXCLUS]
        for f in fichiers:
            if not f.lower().endswith(EXTS):
                continue
            chemin = os.path.join(dossier, f)
            try:
                txt = open(chemin, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            neuf = txt
            for a, b in paires:
                neuf = neuf.replace(a, b)
            if neuf == txt:
                continue
            occ = sum(txt.count(a) for a, _ in paires)
            nb_f += 1
            nb_occ += occ
            print("  %3d  %s" % (occ, os.path.relpath(chemin, RACINE_SCAN)))
            if appliquer:
                shutil.copy2(chemin, chemin + ".bak-migration")
                open(chemin, "w", encoding="utf-8").write(neuf)

    print("\n%d fichiers, %d occurrences." % (nb_f, nb_occ))
    print(">>> APPLIQUÉ (sauvegardes *.bak-migration)." if appliquer
          else "(simulation — relancer avec --appliquer)")


if __name__ == "__main__":
    main()
