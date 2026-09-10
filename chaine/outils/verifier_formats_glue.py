# -*- coding: utf-8 -*-
"""Les %d et %s qui n'ont rien à faire là — programme 27, ticket #2 d'Emzime.

LE DÉFAUT-TYPE. `Interface/PTRXML/AscensionFR_Glue.lua` pose des chaînes
GLOBALES que le client et les add-ons relisent. Emzime a trouvé :

    nous      : DURABILITY = "DURA %d"
    officiel  : DURABILITY = "Durability"        (aucun %d)

Un add-on qui passe cette globale à `string.format` SANS argument (puisque
l'officiel n'en attend aucun) meurt sur « bad argument … (number expected,
got no value) ». Il en a trouvé UNE en jouant ; cet outil balaye TOUTES les
affectations globales de TOUS les .lua du zip publié, et les compare à ce que
le jeu attend vraiment (sources/GlobalStrings_client.lua — l'enUS du client).

LES FAMILLES, de la plus grave à l'inoffensive :
  A. la nôtre a PLUS de spécificateurs que l'officiel  -> PLANTAGE possible
     (le cas Emzime : l'add-on ne fournit pas l'argument)
  B. même nombre mais TYPE différent (%s contre %d)    -> PLANTAGE possible
     (format("%d", "texte") lève)
  C. la nôtre en a MOINS                                -> affichage faux,
     pas de plantage (format ignore les arguments en trop)
  D. globale à spécificateurs ABSENTE de l'officiel     -> à lire à la main
     (custom Ascension : pas de référence pour juger)

Usage :
    python outils/verifier_formats_glue.py             (le client vivant)
    python outils/verifier_formats_glue.py --zip       (le zip publié)
Code de sortie : 1 si la famille A ou B n'est pas vide — un banc qui mord.
"""
import io
import os
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ICI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(ICI)
JEU = r"D:\AscensionFR\WOW_Priv\resources\ascension-live"
OFFICIEL = os.path.join(BASE, "sources", "GlobalStrings_client.lua")
ZIP = os.path.join(BASE, "dist", "AscensionFR_manuel.zip")

RE_AFFECT = re.compile(r'^([A-Z][A-Z0-9_]*)\s*=\s*"((?:\\.|[^"\\])*)"\s*;?\s*$',
                       re.M)
# Un spécificateur Lua : %d, %s, %x, %f, %c, %g, et les positionnels %1$s.
# « %% » est un pour-cent littéral, pas un spécificateur.
RE_SPEC = re.compile(r"%(?:\d+\$)?[-0-9.]*([diouxXeEfgGqcs])|%(%)")


def specs(chaine):
    """La suite des spécificateurs d'une chaîne, dans l'ordre."""
    return [m.group(1) for m in RE_SPEC.finditer(chaine) if m.group(1)]


def affectations(texte):
    return {m.group(1): m.group(2) for m in RE_AFFECT.finditer(texte)}


def lire_zip():
    """{fichier: {nom: valeur}} pour tous les .lua du zip publié."""
    tout = {}
    with zipfile.ZipFile(ZIP) as z:
        for n in z.namelist():
            if not n.endswith(".lua"):
                continue
            texte = z.read(n).decode("utf-8", "replace")
            a = affectations(texte)
            if a:
                tout[n] = a
    return tout


def lire_client():
    tout = {}
    for racine, sous, noms in os.walk(os.path.join(JEU, "Interface")):
        # AddOns : les bases de l'addon ne posent pas de globales de ce type.
        # FrameXML : le code du CLIENT d'Ascension — pas le nôtre, pas dans le
        # zip, pas réparable par nous (relevé : leur WORLD_PVP_ENTER ajoute un
        # %s à la chaîne Blizzard ; c'est LEUR modification, à eux de vivre
        # avec). Le balayage ne juge que ce que NOUS publions.
        sous[:] = [d for d in sous if d not in ("AddOns", "FrameXML")]
        for n in noms:
            if not n.endswith(".lua"):
                continue
            chemin = os.path.join(racine, n)
            a = affectations(io.open(chemin, encoding="utf-8",
                                     errors="replace").read())
            if a:
                tout[os.path.relpath(chemin, JEU)] = a
    return tout


def main():
    officiel = affectations(io.open(OFFICIEL, encoding="utf-8",
                                    errors="replace").read())
    print("=" * 74)
    print("BALAYAGE DES FORMATS — nos globales contre celles du jeu")
    print("=" * 74)
    print("référence : %s (%d globales)"
          % (os.path.relpath(OFFICIEL, BASE), len(officiel)))

    source = "zip publié" if "--zip" in sys.argv else "client vivant"
    notres = lire_zip() if "--zip" in sys.argv else lire_client()
    total = sum(len(a) for a in notres.values())
    print("balayé : %s — %d fichier(s), %d affectation(s) globale(s)\n"
          % (source, len(notres), total))

    fam = {"A": [], "B": [], "C": [], "D": []}
    for fichier, a in sorted(notres.items()):
        for nom, valeur in sorted(a.items()):
            s_nous = specs(valeur)
            if nom not in officiel:
                if s_nous:
                    fam["D"].append((fichier, nom, valeur, None))
                continue
            s_off = specs(officiel[nom])
            if s_nous == s_off:
                continue
            if len(s_nous) > len(s_off):
                fam["A"].append((fichier, nom, valeur, officiel[nom]))
            elif len(s_nous) == len(s_off):
                fam["B"].append((fichier, nom, valeur, officiel[nom]))
            else:
                fam["C"].append((fichier, nom, valeur, officiel[nom]))

    def montrer(cle, titre):
        lot = fam[cle]
        print("--- %s. %s : %d cas ---" % (cle, titre, len(lot)))
        for fichier, nom, valeur, off in lot:
            print("  %s :: %s" % (fichier, nom))
            print("      nous     : %r" % valeur[:70])
            if off is not None:
                print("      officiel : %r" % off[:70])
        print()

    montrer("A", "PLUS de spécificateurs que l'officiel — PLANTAGE possible")
    montrer("B", "même nombre, TYPE différent — PLANTAGE possible")
    montrer("C", "MOINS que l'officiel — affichage faux, sans plantage")
    montrer("D", "custom Ascension avec spécificateurs — à lire à la main")

    graves = len(fam["A"]) + len(fam["B"])
    print("=" * 74)
    print("VERDICT : %d cas pouvant PLANTER un add-on (A+B), "
          "%d d'affichage (C), %d à relire (D)"
          % (graves, len(fam["C"]), len(fam["D"])))
    print("=" * 74)
    return 1 if graves else 0


if __name__ == "__main__":
    sys.exit(main())
