# -*- coding: utf-8 -*-
r"""Banc du bouton de minimap (bloc C, 29/07/2026) : la CONFIRMATION avant
de couper la traduction.

Le contrat :
  1. clic droit, traduction ACTIVE  -> la question s'affiche, RIEN ne bascule ;
  2. « Garder »                     -> fenêtre fermée, toujours actif ;
  3. « Couper »                     -> coupé, fenêtre fermée ;
  4. clic droit, traduction COUPÉE  -> rétablie DIRECTEMENT (pas de question :
     revenir au français est le sens sans danger) ;
  5. clic gauche                    -> les options s'ouvrent, pas de question ;
  6. contrôle négatif : la bascule silencieuse d'avant (clic droit qui coupe
     sans rien demander) doit avoir DISPARU.

Moteur réel : lupa.lua51 charge Modules\Minimap.lua dans un environnement
factice minimal. Sort en code 1 au premier échec.
"""
import io
import locale
import sys

locale.setlocale(locale.LC_ALL, "C")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import lupa.lua51 as lupa_mod  # noqa: E402

MODULE = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface"
          r"\AddOns\AscensionFR\Modules\Minimap.lua")

AMORCE = r"""
-- Environnement WoW factice minimal, façon verifier_signalements.
local function nouveauCadre(genre, nom, parent, gabarit)
    local f = {
        _genre = genre, _nom = nom, _parent = parent, _gabarit = gabarit,
        _scripts = {}, _visible = true, _texte = nil, _enfants = {},
    }
    function f:SetSize() end
    function f:SetPoint() end
    function f:ClearAllPoints() end
    function f:SetFrameStrata() end
    function f:SetFrameLevel() end
    function f:SetHighlightTexture() end
    function f:RegisterForClicks() end
    function f:RegisterForDrag() end
    function f:SetBackdrop() end
    function f:EnableMouse() end
    function f:SetText(t) self._texte = t end
    function f:GetText() return self._texte end
    function f:Show() self._visible = true end
    function f:Hide() self._visible = false end
    function f:IsShown() return self._visible end
    function f:GetCenter() return 0, 0 end
    function f:GetEffectiveScale() return 1 end
    function f:RegisterEvent() end
    function f:SetScript(quoi, fn) self._scripts[quoi] = fn end
    function f:GetScript(quoi) return self._scripts[quoi] end
    function f:CreateTexture()
        local t = {}
        function t.SetSize() end
        function t.SetTexture() end
        function t.SetTexCoord() end
        function t.SetPoint() end
        return t
    end
    function f:CreateFontString()
        local s = {}
        function s.SetPoint() end
        function s:SetText(t) self._texte = t end
        function s:GetText() return self._texte end
        return s
    end
    if parent then table.insert(parent._enfants, f) end
    return f
end

_G.cadres = {}
function _G.CreateFrame(genre, nom, parent, gabarit)
    local f = nouveauCadre(genre, nom, parent, gabarit)
    table.insert(_G.cadres, f)
    return f
end
_G.Minimap = nouveauCadre("Frame", "Minimap")
_G.UIParent = nouveauCadre("Frame", "UIParent")
_G.GameTooltip = nouveauCadre("Frame", "GameTooltip")
function _G.GameTooltip.SetOwner() end
function _G.GameTooltip.AddLine() end
function _G.GetCursorPosition() return 0, 0 end
_G.messages = {}
function _G.print(...)
    local morceaux = {}
    for i = 1, select("#", ...) do
        morceaux[#morceaux + 1] = tostring(select(i, ...))
    end
    table.insert(_G.messages, table.concat(morceaux, " "))
end
_G.AscensionFRSaved = { Options = {} }
_G.optionsOuvertes = 0
_G.AscensionFR = {
    DB = {},
    OuvrirOptions = function() _G.optionsOuvertes = _G.optionsOuvertes + 1 end,
}
"""


def main():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(AMORCE)
    lua.execute(io.open(MODULE, encoding="utf-8").read())

    echecs = []

    def verifier(nom, condition, detail=""):
        etat = "ok    " if condition else "ECHEC "
        print("  %s %s %s" % (etat, nom, detail))
        if not condition:
            echecs.append(nom)

    # la recherche des cadres se fait CÔTÉ Lua : les identités de tables
    # ne se comparent pas à travers les proxys lupa
    lua.execute("""
    for _, f in ipairs(cadres) do
        if f._genre == "Button" and f._parent == Minimap then
            _G.t_bouton = f
        end
        if f._genre == "Frame" and f._parent == UIParent then
            for _, enfant in ipairs(f._enfants) do
                if enfant._texte == "Couper" then
                    _G.t_confirmation, _G.t_couper = f, enfant
                end
                if enfant._texte == "Garder" then _G.t_garder = enfant end
            end
        end
    end
    """)
    g = lua.globals()
    bouton = g.t_bouton
    confirmation = g.t_confirmation
    couper = g.t_couper
    garder = g.t_garder
    verifier("cadres retrouvés",
             all(x is not None for x in (bouton, confirmation, couper,
                                         garder)))
    if echecs:
        return 1

    opt = g.AscensionFRSaved.Options
    clic = bouton._scripts["OnClick"]

    # 1. clic droit actif -> question affichée, rien ne bascule
    confirmation._visible = False
    clic(bouton, "RightButton")
    verifier("clic droit (actif) : la question s'affiche",
             confirmation._visible)
    verifier("clic droit (actif) : RIEN n'a basculé", not opt.desactive)

    # 2. « Garder » -> fermé, toujours actif
    garder._scripts["OnClick"]()
    verifier("« Garder » : fenêtre fermée", not confirmation._visible)
    verifier("« Garder » : toujours actif", not opt.desactive)

    # 3. « Couper » -> coupé
    clic(bouton, "RightButton")
    couper._scripts["OnClick"]()
    verifier("« Couper » : traduction coupée", opt.desactive == True)  # noqa: E712
    verifier("« Couper » : fenêtre fermée", not confirmation._visible)

    # 4. clic droit coupé -> rétabli direct, pas de question
    clic(bouton, "RightButton")
    verifier("clic droit (coupé) : rétabli DIRECTEMENT",
             not opt.desactive)
    verifier("clic droit (coupé) : pas de question",
             not confirmation._visible)

    # 5. clic gauche -> options, pas de question
    avant = g.optionsOuvertes
    clic(bouton, "LeftButton")
    verifier("clic gauche : options ouvertes", g.optionsOuvertes == avant + 1)
    verifier("clic gauche : pas de question", not confirmation._visible)

    # 6. contrôle négatif : un clic droit seul ne suffit JAMAIS à couper
    clic(bouton, "RightButton")           # ouvre la question
    clic(bouton, "LeftButton")            # ne confirme pas
    verifier("contrôle négatif : sans « Couper », jamais coupé",
             not opt.desactive)

    print()
    print("%d échec(s)" % len(echecs))
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
