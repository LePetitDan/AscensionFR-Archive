# -*- coding: utf-8 -*-
"""
Banc de l'hôtel des ventes (signalement joueur du 24/07/2026).

Le client d'Ascension reconnaît ses catégories À LEUR TEXTE ANGLAIS :

    Blizzard_AuctionUI.lua:754   selectedClass = self:GetText()
    Blizzard_AuctionUI.lua:639   if selectedClass == CLASS_FILTERS[i] then
                                     AuctionFrameFilters_UpdateSubClasses(...)

Traduire le libellé casse la comparaison : plus aucune SOUS-CATÉGORIE ne
s'affiche. On vérifie donc qu'aucun de nos deux chemins d'écriture ne touche
un AuctionFilterButton — et qu'ils touchent bien tout le reste.

Usage : python outils/verifier_hdv.py
"""
import io
import os
import sys

import lupa.lua51 as lupa_mod

ADDON = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns\AscensionFR"

CONTEXTE = r"""
AscensionFR = { DB = { Epreuves = {}, HautsFaits = {}, Zones = {},
                       Libelles = {}, ObjetsNoms = {}, UI = {}, Sorts = {},
                       SortsNoms = {}, Quetes = {}, Objets = {} } }
AscensionFRSaved = { Options = {} }
MESSAGES = {}
SlashCmdList = {}
UIParent = nil
GameTooltip = nil
function print(...) end
function strtrim(s) return (string.gsub(s or "", "^%s*(.-)%s*$", "%1")) end
function UnitName() return "Testeur" end
function UnitClass() return "Reaper" end
function UnitRace() return "Dwarf" end
function UnitSex() return 2 end
function InCombatLockdown() return false end
function GetTime() return 1 end
function GetLocale() return "enUS" end
function hooksecurefunc() end
function CreateFrame()
    local f = {}
    function f:RegisterEvent() end
    function f:SetScript() end
    function f:HookScript() end
    function f:Show() end
    function f:Hide() end
    function f:SetText() end
    function f:GetChildren() end
    function f:GetRegions() end
    return f
end

-- Faux composants : un nom, un parent, un texte.
function Widget(nom, parent)
    local w = { _nom = nom, _parent = parent, _t = "" }
    function w:GetName() return self._nom end
    function w:GetParent() return self._parent end
    function w:GetText() return self._t end
    function w:SetText(v) self._t = v end
    function w:GetObjectType() return "FontString" end
    return w
end
"""


def main():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)
    for f in ("Core.lua", "Modules\\Epreuves.lua"):
        with io.open(os.path.join(ADDON, f), encoding="utf-8") as fh:
            lua.execute(fh.read())

    detecte = lua.globals().AscensionFR.EstFiltreHdV
    if detecte is None:
        print("  ECHEC   AFR.EstFiltreHdV n'est pas exporté")
        sys.exit(1)

    lua.execute("""
        BOUTON   = Widget("AuctionFilterButton3", nil)
        LIBELLE  = Widget("AuctionFilterButton3Text", BOUTON)
        PROFOND  = Widget(nil, LIBELLE)
        NORMAL   = Widget("QuestLogTitle1", nil)
        SOUS_NORMAL = Widget(nil, NORMAL)
        LOIN     = Widget(nil, Widget(nil, Widget(nil, BOUTON)))
    """)
    g = lua.globals()

    cas = [
        ("le bouton de filtre lui-même", g.BOUTON, True),
        ("son libellé (enfant direct)", g.LIBELLE, True),
        ("un petit-enfant du bouton", g.PROFOND, True),
        ("un cadre ordinaire", g.NORMAL, False),
        ("l'enfant d'un cadre ordinaire", g.SOUS_NORMAL, False),
        # Borné à 3 niveaux : au-delà, on ne remonte plus (et il n'y a rien
        # d'aussi profond dans l'hôtel des ventes).
        ("au-delà de 3 niveaux -> non détecté", g.LOIN, False),
    ]
    echecs = 0
    for description, widget, attendu in cas:
        obtenu = bool(detecte(widget))
        if obtenu == attendu:
            print("  ok      %-46s %s" % (description, obtenu))
        else:
            print("  ECHEC   %-46s obtenu %s, attendu %s"
                  % (description, obtenu, attendu))
            echecs += 1

    # Le garde-fou doit être posé sur les DEUX chemins d'écriture.
    with io.open(os.path.join(ADDON, "Modules\\Epreuves.lua"),
                 encoding="utf-8") as fh:
        source = fh.read()
    for chemin in ("local function Poser(", "local function Intercepter("):
        bloc = source.split(chemin, 1)[-1][:400]
        if "EstFiltreHdV" in bloc:
            print("  ok      garde-fou présent dans %s" % chemin.strip())
        else:
            print("  ECHEC   garde-fou ABSENT de %s" % chemin.strip())
            echecs += 1

    print("")
    print("%d échec(s)" % echecs)
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
