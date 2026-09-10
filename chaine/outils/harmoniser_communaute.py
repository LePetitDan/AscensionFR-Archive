# -*- coding: utf-8 -*-
r"""Passe ponctuelle de vocabulaire sur DB_Communaute.lua.

POURQUOI CE SCRIPT EXISTE
-------------------------
`DB_Communaute.lua` est la seule base que la régénération ne touche JAMAIS :
`ingerer_recolte.py` l'ouvre en mode AJOUT (open(COMMUNAUTE, "a")) et se
contente d'y empiler ce que les joueurs récoltent en jeu. Corriger le
générateur ne suffit donc pas — le vieux vocabulaire y reste indéfiniment, et
comme cette base est chargée APRÈS les autres, elle les SURCHARGE : le joueur
verrait encore l'ancien mot alors que tout le reste a été harmonisé.

Ce script rattrape l'existant. Le flux d'ingestion, lui, est corrigé à la
source (`ingerer_recolte.py` appelle désormais `harmoniser`), donc ce script
n'aura normalement plus rien à faire au prochain passage.

Ce qu'il applique, ce sont les arbitrages de Dan du 26/07/2026 :
  - « bassin d'Arathi » -> « bassin Arathi » (casse conservée) ;
  - « Tempête de mana du moulin » -> « Millhouse Manastorm » (nom propre,
    contresens sur « mill house »).

Le fichier est recompilé en Lua 5.1 — la version du client — avant d'être
remis en place, et jamais écrit si la compilation échoue.

Usage :
    python outils/harmoniser_communaute.py              # simulation
    python outils/harmoniser_communaute.py --appliquer  # écrit (+ sauvegarde)
"""
import argparse
import io
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generateur_db import ADDON, DEBUT_MOT, FIN_MOT, harmoniser  # noqa: E402

FICHIER = os.path.join(ADDON, "DB", "DB_Communaute.lua")

# Le contresens Millhouse ne passe pas par harmoniser() : c'est une correction
# de nom propre, pas une harmonisation de vocabulaire, et elle n'a rien à faire
# dans le chemin d'écriture de toutes les bases.
# DEBUT_MOT et pas « \b » : ici le texte est précédé de son icône
# (« …|t|rTempête de mana du moulin »), et le « r » de « |r » est une lettre.
MILLHOUSE = (re.compile(DEBUT_MOT + r"Tempête\s+de\s+mana\s+du\s+moulin"
                        + FIN_MOT), "Millhouse Manastorm")

TEMOINS = [r"Bassin d'Arathi", r"bassin d'Arathi",
           r"Tempête de mana du moulin", r"(?<![a-zA-Zà-ÿ])Bassin Arathi",
           r"(?<![a-zA-Zà-ÿ])bassin Arathi"]


def compter(texte):
    return {m: len(re.findall(m, texte)) for m in TEMOINS}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--appliquer", action="store_true")
    args = parser.parse_args()

    with io.open(FICHIER, encoding="utf-8") as f:
        avant = f.read()

    apres = MILLHOUSE[0].sub(MILLHOUSE[1], harmoniser(avant))

    for motif in TEMOINS:
        a, b = compter(avant)[motif], compter(apres)[motif]
        print("  %-34s %5d -> %5d" % (motif, a, b))

    if apres == avant:
        print("\nRien à changer.")
        return 0

    # Le client compile ce fichier en Lua 5.1. Le lupa par défaut est en 5.5 et
    # accepte ce que 5.1 refuse : c'est exactement le piège qui a failli faire
    # publier un addon mort au chargement (lot 3).
    import lupa.lua51 as lupa51
    try:
        lupa51.LuaRuntime().compile(apres)
    except Exception as erreur:
        print("\nCOMPILATION Lua 5.1 ÉCHOUÉE — rien n'est écrit :\n  %s"
              % erreur)
        return 1
    print("\nCompilation Lua 5.1 : OK (%d octets)" % len(apres.encode("utf-8")))

    if not args.appliquer:
        print("SIMULATION — rien n'a été écrit. --appliquer pour livrer.")
        return 0

    secours = FICHIER.replace(".lua", "_avant_harmonisation.lua.bak")
    if not os.path.exists(secours):
        shutil.copy2(FICHIER, secours)
    with io.open(FICHIER, "w", encoding="utf-8") as f:
        f.write(apres)
    print("écrit : %s   (sauvegarde : %s)"
          % (os.path.basename(FICHIER), os.path.basename(secours)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
