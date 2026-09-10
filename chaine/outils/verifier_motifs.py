# -*- coding: utf-8 -*-
"""
Verrou de synchronisation : MOTIFS_VARIABLE (addon, Lua) et MOTIFS_PROTEGES
(traducteur, Python) doivent découper les mêmes jetons dans les mêmes textes.

Leur divergence a déjà fait voir des « $ » aux joueurs à la place des
chiffres : l'addon connaissait « $<percent> », pas la protection, et Google
détruisait donc ces variables dans le texte français. Ce test remplace la
discipline (« toute forme ajoutée d'un côté doit l'être de l'autre ») par
une vérification mécanique sur une batterie de formes réelles.

Seules les familles $ et @ sont comparées : la protection Python couvre en
plus les couleurs |cff..., textures et %s, qui ne sont pas des variables
d'alignement pour l'addon.
"""
import os
import sys

import lupa.lua51 as lupa_mod

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
from traducteur_fr import MOTIFS_PROTEGES  # noqa: E402

ADDON = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
         r"\AscensionFR")

# Formes réelles, relevées dans spells_Ascension.json — pas inventées.
# Chaque famille de motif doit être représentée ici : un motif ajouté sans
# son échantillon n'est pas verrouillé.
BATTERIE = [
    "Shock an enemy for $s1 Nature damage over $d.",
    "absorbing ${$m1+0.21*$SP} damage. Lasts $d. Once every $6788d.",
    "every $t1 sec$?s300512[ and reducing damage taken by $300512s2%][]",
    "recover $/1000;s1 mana, then $*15;s1 and $+100;s1",
    "for 1 $lseconde:secondes; as $gm:f; wills it",
    "casts $@spellname raising $<percent> then $<mult> of $64843s2 plus $h",
    "gains $1 charge",
    "Lasts $d.\r\n\r\n@ext:Does not stack with similar effects.:ext@",
    "Enchant. @re:81298:0@ then @s:101087:0@ and @s:1112044:-32@",
    "@req:8921@\nYour Moonfire now hits @req:1122520:req@ more",
    "@unlockby:270832@ and @learns:92161@",
    "@wflocation:Every man knows, all Banshee's Wail.@",
    "haste. @ifknown:1585573:Spell haste increased by ${$w3}%.:ifknown@",
    "@ifnotknown:806077:Gain might for $704546d.:ifnotknown@",
    "Lore.\r\n\r\n@ext:@s:1100896:0@:ext@",   # marquage imbriqué
]


def jetons_python(texte):
    """Jetons $ et @ que la protection Python découpe dans un texte."""
    return sorted(m.group(0) for m in MOTIFS_PROTEGES.finditer(texte)
                  if m.group(0).startswith(("$", "@", ":")))


def jetons_lua(lua, texte):
    """Jetons que le découpeur de l'addon (le vrai code) extrait."""
    decouper = lua.globals().AscensionFR.DecouperModele
    _, variables = decouper(texte)
    return sorted(list(variables.values()))


def main():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute("AscensionFR = { DB = { Sorts = {} } }")
    lua.execute("function hooksecurefunc() end")
    lua.execute("SlashCmdList = {}")
    lua.execute("function CreateFrame() local f = {} "
                "function f:RegisterEvent() end "
                "function f:SetScript() end return f end")
    with open(ADDON + r"\Modules\Sorts.lua", encoding="utf-8") as fh:
        lua.execute(fh.read())

    echecs = 0
    for texte in BATTERIE:
        py = jetons_python(texte)
        lu = jetons_lua(lua, texte)
        if py == lu:
            print("  ok      %s" % texte[:66].replace("\r", "").replace(
                "\n", " "))
        else:
            print("  ECHEC   %s" % texte[:66])
            print("          python : %s" % py)
            print("          lua    : %s" % lu)
            echecs += 1

    print()
    print("%d échec(s)" % echecs)
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
