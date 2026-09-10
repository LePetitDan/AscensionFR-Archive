# -*- coding: utf-8 -*-
"""
Combien de chaînes d'interface le contrôle de signature accepte-t-il ?

Mesure sur les VRAIES données : les GlobalStrings d'Ascension (leur client)
et notre DB_Interface (frFR officiel). Le module InterfaceUI est chargé tel
quel — c'est lui qui décide, pas une imitation.

Sert à chiffrer un changement du contrôle : lancer avant/après.
"""
import os
import re
import sys

import lupa.lua51 as lupa_mod

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDON = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
         r"\AscensionFR")
GS_ASCENSION = os.path.join(BASE, "sources", "framexml", "GlobalStrings.lua")

CONTEXTE = r"""
AscensionFR = { DB = { UI = {}, ListeNoire = {} }, Details = {} }
function AscensionFR.Actif() return true end
RESUME = nil
function AscensionFR.Debug(...)
    local m = {}
    for i = 1, select("#", ...) do m[i] = tostring(select(i, ...)) end
    RESUME = table.concat(m, " ")
end
ECARTEES = {}
function AscensionFR.Detailler(_, ligne) ECARTEES[ligne] = true end
_evt = nil
function CreateFrame()
    return { RegisterEvent = function() end,
             SetScript = function(self, k, f) _evt = f end }
end
StaticPopupDialogs = {}
"""


def main():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)

    # Les chaînes anglaises telles qu'Ascension les livre.
    with open(GS_ASCENSION, encoding="utf-8", errors="ignore") as f:
        code = f.read()
    lua.execute(code)
    anglaises = len(re.findall(r"^[A-Z_0-9]+ *=", code, re.M))

    # Nos traductions officielles.
    for nom in ("DB\\DB_ListeNoire.lua", "DB\\DB_Interface.lua"):
        with open(os.path.join(ADDON, nom), encoding="utf-8") as f:
            lua.execute(f.read())

    with open(os.path.join(ADDON, "Modules", "InterfaceUI.lua"),
              encoding="utf-8") as f:
        lua.execute(f.read())
    lua.execute('_evt(nil, "ADDON_LOADED", "AscensionFR")')

    g = lua.globals()
    print("Chaînes anglaises du client Ascension : %d" % anglaises)
    print("Traductions frFR disponibles          : %d"
          % sum(1 for _ in g.AscensionFR.DB.UI.items()))
    print()
    print(g.RESUME)
    ecartees = sorted(k for k, _ in g.ECARTEES.items())
    if ecartees:
        print()
        print("Écartées (%d) — échantillon :" % len(ecartees))
        for cle in ecartees[:12]:
            print("   %s" % cle)
    return 0


if __name__ == "__main__":
    sys.exit(main())
