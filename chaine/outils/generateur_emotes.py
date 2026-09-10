# -*- coding: utf-8 -*-
"""Génère DB/DB_Emotes.lua depuis traductions/emotes.json :
- EmotesCommandes : clé GlobalStrings -> commande FRANÇAISE officielle ;
- EmotesTchat     : phrase EN exacte -> phrase FR (gabarits %s compris).
Usage : python outils/generateur_emotes.py
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(BASE, "traductions", "emotes.json")
SORTIE = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
          r"\AscensionFR\DB\DB_Emotes.lua")


def echapper(t):
    t = t.replace("\\", "\\\\").replace('"', '\\"')
    return t.replace("\r", "\\r").replace("\n", "\\n")


def main():
    d = json.load(io.open(SOURCE, encoding="utf-8"))
    lignes = [
        "-- Fichier généré par outils/generateur_emotes.py — NE PAS ÉDITER.",
        "-- Commandes d'émotes FRANÇAISES officielles + phrases du tchat.",
        "-- Le JETON (« HELLO ») est embarqué : aucune dépendance aux",
        "-- tables internes du client (remaniées chez Ascension).",
        "local DB = AscensionFR.DB",
        "DB.EmotesCommandes = {}",
        "DB.EmotesJetons = {}",
        "DB.EmotesTchat = {}",
        "local C, J, T = DB.EmotesCommandes, DB.EmotesJetons, DB.EmotesTchat",
    ]
    for cle, paire in sorted(d.get("commandes", {}).items()):
        lignes.append('C["%s"]="%s"' % (echapper(cle),
                                        echapper(paire["fr"])))
        lignes.append('J["%s"]="%s"' % (echapper(cle),
                                        echapper(paire["jeton"])))
    for en, fr in sorted(d.get("tchat", {}).items()):
        lignes.append('T["%s"]="%s"' % (echapper(en), echapper(fr)))
    io.open(SORTIE, "w", encoding="utf-8", newline="\n").write(
        "\n".join(lignes) + "\n")
    print("écrit : DB_Emotes.lua (%d commandes, %d phrases)"
          % (len(d.get("commandes", {})), len(d.get("tchat", {}))))


if __name__ == "__main__":
    main()
