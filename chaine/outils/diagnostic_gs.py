# -*- coding: utf-8 -*-
"""Diagnostic des GlobalStrings frFR : repère celles qui casseraient le jeu."""
import re
import sys

MOTIF_GS = re.compile(r'^([A-Za-z0-9_]+)\s*=\s*"((?:[^"\\]|\\.)*)"\s*;?\s*$', re.M)
# Spécificateurs de format Lua : %d %s %.2f %1$s %%
MOTIF_FORMAT = re.compile(r"%%|%\d*\$?[-+ #0]*\d*(?:\.\d+)?[dfsxXeEgGqc]")

# Échappements Lua. Le cas décisif est \ddd (code décimal) : les chaînes de
# chat de Blizzard finissent par « :\32 », c'est-à-dire « : » suivi d'un
# ESPACE. Ne pas le décoder faisait afficher « \32 » littéralement devant
# chaque message de chat.
ECHAPPEMENTS = {
    "a": "\a", "b": "\b", "f": "\f", "n": "\n", "r": "\r",
    "t": "\t", "v": "\v", "\\": "\\", '"': '"', "'": "'", "\n": "\n",
}
MOTIF_ECHAPPEMENT = re.compile(r"\\(\d{1,3}|.)", re.S)


def decoder_lua(texte):
    """Convertit les échappements d'une chaîne Lua en vrais caractères."""
    def rempl(m):
        s = m.group(1)
        if s.isdigit():
            code = int(s)
            return chr(code) if code < 256 else m.group(0)
        return ECHAPPEMENTS.get(s, s)
    return MOTIF_ECHAPPEMENT.sub(rempl, texte)


def charger(chemin):
    with open(chemin, encoding="utf-8") as f:
        contenu = f.read()
    gs = {}
    for m in MOTIF_GS.finditer(contenu):
        gs[m.group(1)] = decoder_lua(m.group(2))
    return gs


def specificateurs(texte):
    """Séquence des %d/%s/%.2f d'une chaîne (les %% littéraux exclus)."""
    return [m.group(0) for m in MOTIF_FORMAT.finditer(texte)
            if m.group(0) != "%%"]


if __name__ == "__main__":
    fr = charger(r"D:\AscensionFR\WorkFlow\sources\GlobalStrings_frFR.lua")
    print("GlobalStrings frFR chargées :", len(fr))
    print()
    print("=== BUG 1 : confirmation de destruction d'objet ===")
    for c in ["DELETE_ITEM_CONFIRM_STRING", "DELETE_GOOD_ITEM", "DELETE_ITEM"]:
        if c in fr:
            print("  %-28s = %r" % (c, fr[c][:75]))
    print()
    print("=== BUG 2 : chaîne de la feuille de personnage ===")
    for c in sorted(fr):
        if "HIT_" in c and "TOOLTIP" in c or c.startswith("CR_"):
            v = fr[c]
            if "pénétration" in v.lower() or "mêlée" in v.lower():
                print("  %s" % c)
                print("     FR : %r" % v[:110])
                print("     spécificateurs : %s" % specificateurs(v))
