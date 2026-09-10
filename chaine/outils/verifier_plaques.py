# -*- coding: utf-8 -*-
"""
Banc des barres de vie (signalement joueur du 24/07/2026).

DragonUI identifie la creature d'une barre de vie en LISANT le nom affiche,
puis en le comparant au nom ANGLAIS du jeu. Traduire ce nom casse la
correspondance -> DragonUI masque ses auras. Notre module doit donc :

  - traduire les barres de vie quand DragonUI n'est PAS la ;
  - s'en abstenir des que DragonUI est charge ;
  - sauf si le joueur force via plaquesMalgreDragonUI.

On simule le jeu, on charge le vrai module, et on verifie qu'une barre de vie
est traduite ou laissee anglaise selon le cas.

Usage : python outils/verifier_plaques.py
"""
import io
import os
import sys

import lupa.lua51 as lupa_mod

ADDON = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns\AscensionFR"

CONTEXTE = r"""
AscensionFR = { DB = { Creatures = {}, Zones = {}, Objets = {},
                       ObjetsMonde = {} },
                Prechauffages = {} }
function AscensionFR.Actif() return true end
AscensionFRSaved = { Options = {} }
ADDONS_CHARGES = {}
function IsAddOnLoaded(nom) return ADDONS_CHARGES[nom] and true or false end
function GetTime() return _TEMPS or 0 end
function print() end
function UnitName() return "Testeur" end
function ChatFrame_AddMessageEventFilter() end
function hooksecurefunc() end
GameTooltip = { HookScript = function() end }
function strtrim(s) return (string.gsub(s or "", "^%s*(.-)%s*$", "%1")) end

-- Une barre de vie : un cadre portant une FontString (le nom de la creature).
function FS(t)
    local f = { _t = t }
    function f:GetText() return self._t end
    function f:SetText(v) self._t = v end
    function f:GetObjectType() return "FontString" end
    return f
end
function Plaque(nomFS)
    local nom = FS(nomFS)
    local c = { _r = { nom }, _e = {}, _shown = true, _nomFS = nom }
    function c:GetRegions() return unpack(self._r) end
    function c:GetChildren() return unpack(self._e) end
    function c:IsShown() return self._shown end
    function c:HookScript(quoi, fn) self._onshow = fn end
    function c:GetObjectType() return "Frame" end
    return c
end

function CreateFrame()
    local f = {}
    function f:RegisterEvent() end
    function f:SetScript(quoi, fn)
        if quoi == "OnUpdate" then VEILLEUSE = fn end
    end
    function f:HookScript() end
    return f
end

-- Un WorldFrame avec une barre de vie « Boar ».
PLAQUE = Plaque("Boar")
WorldFrame = {}
function WorldFrame:GetNumChildren() return 1 end
function WorldFrame:GetChildren() return PLAQUE end

-- Expose le texte affiche pour le banc (pas d'eval cote Python).
function TEXTE_PLAQUE() return PLAQUE._nomFS:GetText() end
function TIC()
    _TEMPS = (_TEMPS or 0) + 1
    VEILLEUSE(nil, 0.3)
end
"""


def charger():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)
    for f in ("Core.lua", "Modules\\Plaques.lua"):
        with io.open(os.path.join(ADDON, f), encoding="utf-8") as fh:
            lua.execute(fh.read())
    lua.execute('AscensionFR.DB.Creatures[1] = '
                '{ NE = "Boar", N = "Sanglier" }')
    return lua


echecs = 0


def verifier(desc, obtenu, attendu):
    global echecs
    if obtenu == attendu:
        print("  ok      %-48s %s" % (desc, obtenu))
    else:
        print("  ECHEC   %-48s obtenu %r, attendu %r"
              % (desc, obtenu, attendu))
        echecs += 1


def scenario(reglages):
    lua = charger()
    for ordre in reglages:
        lua.execute(ordre)
    lua.globals().TIC()
    return lua.globals().TEXTE_PLAQUE()


verifier("sans DragonUI : Boar -> Sanglier",
         scenario([]), "Sanglier")
verifier("avec DragonUI : le nom reste anglais",
         scenario(['ADDONS_CHARGES["DragonUI"] = true']), "Boar")
verifier("forçage plaquesMalgreDragonUI : Boar -> Sanglier",
         scenario(['ADDONS_CHARGES["DragonUI"] = true',
                   'AscensionFRSaved.Options.plaquesMalgreDragonUI = true']),
         "Sanglier")
verifier("sansPlaques : le nom reste anglais",
         scenario(['AscensionFRSaved.Options.sansPlaques = true']), "Boar")

print("")
print("%d échec(s)" % echecs)
sys.exit(1 if echecs else 0)
