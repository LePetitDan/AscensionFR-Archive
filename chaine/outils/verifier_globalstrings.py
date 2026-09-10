# -*- coding: utf-8 -*-
r"""
Test du décodage des chaînes d'interface (GlobalStrings.lua).

Le fichier de Blizzard est du code Lua : ses chaînes contiennent des
échappements qu'il faut convertir en vrais caractères avant de les réémettre.

Bug vécu : les formats de chat finissent par « :\32 » — en Lua, \32 est le
code décimal de l'ESPACE. Un décodage naïf le laissait tel quel, puis le
générateur échappait son antislash. Résultat en jeu : chaque message de chat
s'affichait « [Kyrri] :\32bonjour » au lieu de « [Kyrri] : bonjour ».
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagnostic_gs import charger, decoder_lua  # noqa: E402

FRFR = r"D:\AscensionFR\WorkFlow\sources\GlobalStrings_frFR.lua"

# (chaîne telle qu'écrite dans le fichier Lua, texte attendu une fois décodé)
CAS = [
    (r"%s dit :\32", "%s dit : "),          # le cas du bug
    (r"%s crie :\32", "%s crie : "),
    (r"Bonjour\nmonde", "Bonjour\nmonde"),
    (r"Guillemet \" ici", 'Guillemet " ici'),
    (r"Antislash \\ seul", "Antislash \\ seul"),
    (r"Tabulation\9ici", "Tabulation\tici"),
    (r"Sans echappement", "Sans echappement"),
    (r"%d%% de chances", "%d%% de chances"),  # les % ne sont pas des échappements
]


def main():
    echecs = 0
    print("=== Décodage des échappements Lua ===")
    for brut, attendu in CAS:
        obtenu = decoder_lua(brut)
        if obtenu == attendu:
            print("  ok      %-28r -> %r" % (brut, obtenu))
        else:
            print("  ECHEC   %-28r -> %r (attendu %r)" % (brut, obtenu, attendu))
            echecs += 1

    print()
    print("=== Sur le vrai fichier frFR ===")
    gs = charger(FRFR)
    print("  %d chaînes chargées" % len(gs))
    for cle in ["CHAT_SAY_GET", "CHAT_YELL_GET", "CHAT_CHANNEL_GET",
                "CHAT_WHISPER_GET"]:
        v = gs.get(cle)
        if v is None:
            continue
        if "\\" in v:
            print("  ECHEC   %s contient encore un antislash : %r" % (cle, v))
            echecs += 1
        elif not v.endswith(" "):
            print("  ECHEC   %s ne finit pas par une espace : %r" % (cle, v))
            echecs += 1
        else:
            print("  ok      %-18s %r" % (cle, v))

    # Aucune chaîne ne doit garder d'échappement numérique non décodé.
    # Les antislashs restants sont légitimes : ce sont des chemins de texture
    # (« Interface\OptionsFrame\... »), qu'il ne faut surtout pas toucher.
    import re
    reste = re.compile(r"\\\d")
    suspects = [c for c, v in gs.items() if reste.search(v)]
    if suspects:
        print()
        print("  ECHEC   %d chaînes gardent un échappement numérique :"
              % len(suspects))
        for c in suspects[:5]:
            print("            %s = %r" % (c, gs[c]))
        echecs += 1
    else:
        print("  ok      aucun échappement numérique non décodé "
              "(les chemins de texture gardent leurs antislashs, c'est normal)")

    print()
    print("%d échec(s)" % echecs)
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
