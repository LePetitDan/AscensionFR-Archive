# -*- coding: utf-8 -*-
"""
Ce que pèse VRAIMENT l'addon en mémoire — bases + index dérivés
(programme 11, bloc B, 01/08/2026).

POURQUOI CET OUTIL EXISTE. Au programme 10, `mesurer_tas_lua.py` avait relevé
136,4 Mo après chargement des bases, et j'en avais déduit « 85 à 100 Mo côté
client 32 bits ». Le relevé en jeu dit **156,6 Mo**. L'estimation s'est trompée
de 60 %, dans le mauvais sens.

Le raisonnement 32 bits n'était pas faux — les pointeurs y sont bien deux fois
plus petits. L'erreur était ailleurs, et elle est plus bête : **je n'avais
mesuré que les DONNÉES.** Le jeu, lui, charge aussi les modules, et ces modules
construisent des INDEX DÉRIVÉS qui ne sont dans aucun fichier :

  - les trois index inversés préchauffés par Core.lua (titre de quête -> id,
    nom de créature -> id, nom d'objet du monde -> id) ;
  - l'index des noms de créatures de Plaques.lua ;
  - la table `normalise` des Épreuves ;
  - l'index flou de l'Entraîneur.

Aucun n'apparaît sur le disque. Tous vivent du login à la déconnexion. Cet
outil les pèse, un par un, pour que l'écart soit compris et non rafistolé.

Usage : python outils/mesurer_tas_complet.py
"""
import io
import locale
import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

locale.setlocale(locale.LC_ALL, "C")

import lupa.lua51 as lupa_mod  # noqa: E402

ADDON = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
         r"\AscensionFR")

CONTEXTE = r"""
AscensionFR = AscensionFR or {}
function strtrim(s) return (string.gsub(s or "", "^%s*(.-)%s*$", "%1")) end
function print() end
function hooksecurefunc() end
function IsAddOnLoaded() return false end
function ChatFrame_AddMessageEventFilter() end
function UnitName() return "Mesure" end
function UnitClass() return "Templar" end
function UnitRace() return "Dwarf" end
function UnitSex() return 2 end
function UnitLevel() return 80 end
function GetTime() return 0 end
function GetLocale() return "enUS" end
function GetRealZoneText() return "Hurlevent" end
function GetSubZoneText() return "" end
function InCombatLockdown() return false end
function GetFramerate() return 60 end
function debugprofilestop() return 0 end
function wipe(t) for k in pairs(t) do t[k] = nil end return t end
function GetSpellInfo() return nil end
function GetNumSpellTabs() return 0 end
function GetSpellTabInfo() return nil end
function EnumerateFrames() return nil end
AscensionFRSaved = { Options = {} }
SlashCmdList = {}
UISpecialFrames = {}
GameTooltip = { HookScript = function() end,
                GetName = function() return "GameTooltip" end }
UIParent = nil

function CreateFrame()
    local f = { _scripts = {}, _evts = {} }
    function f:RegisterEvent(e) self._evts[e] = true end
    function f:UnregisterEvent(e) self._evts[e] = nil end
    function f:SetScript(quoi, fn) self._scripts[quoi] = fn end
    function f:GetScript(quoi) return self._scripts[quoi] end
    function f:HookScript() end
    function f:Show() end
    function f:Hide() end
    function f:SetSize() end
    function f:SetPoint() end
    function f:SetFrameStrata() end
    function f:SetMovable() end
    function f:EnableMouse() end
    function f:RegisterForDrag() end
    function f:SetBackdrop() end
    function f:CreateFontString()
        return { SetText = function() end, GetText = function() end,
                 SetPoint = function() end }
    end
    return f
end

function _RELEVER_TAS()
    collectgarbage("collect") collectgarbage("collect")
    _TAS = collectgarbage("count")
end

-- Le préchauffage de Core.lua, déclenché à la main : en jeu il part sur
-- PLAYER_ENTERING_WORLD, ici on l'appelle nous-mêmes.
function _PRECHAUFFER_CORE()
    pcall(AscensionFR.QueteParTitreEN, "préchauffage")
    pcall(AscensionFR.CreatureParNomEN, "préchauffage")
    pcall(AscensionFR.ObjetMondeParNomEN, "préchauffage")
end

function _PRECHAUFFER_MODULES()
    _N_PRECHAUFFAGES = 0
    for _, f in ipairs(AscensionFR.Prechauffages or {}) do
        pcall(f)
        _N_PRECHAUFFAGES = _N_PRECHAUFFAGES + 1
    end
end
"""

# Les modules qui construisent un index dérivé, dans l'ordre du .toc. Les
# autres ne pèsent que leur code.
MODULES = [
    "Perf.lua", "InterfaceUI.lua", "InterfaceCiblee.lua", "Epreuves.lua",
    "Sorts.lua", "Quetes.lua", "Gossip.lua", "Tooltips.lua",
    "BarresDeVie.lua", "Plaques.lua", "Metiers.lua", "Entraineur.lua",
    "Livres.lua", "Chat.lua", "Emotes.lua", "Signaler.lua", "Options.lua",
    "Recolte.lua", "Minimap.lua", "CanalFrancais.lua", "AddonsTiers.lua",
    "Guichets.lua", "DragonUI_Grille.lua",
]


def bases_du_toc():
    chemin = os.path.join(ADDON, "AscensionFR.toc")
    out = []
    with io.open(chemin, encoding="utf-8") as fh:
        for ligne in fh:
            ligne = ligne.strip()
            if ligne.startswith("DB\\") and ligne.lower().endswith(".lua"):
                out.append(ligne.replace("\\", os.sep))
    return out


def tas(lua):
    lua.globals()._RELEVER_TAS()
    return float(lua.globals()._TAS)


def mo(ko):
    return ko / 1024.0


def main():
    print("=" * 74)
    print("CE QUE PÈSE L'ADDON — bases ET index dérivés")
    print("=" * 74)
    print()
    print("Lua 5.1 en 64 bits. Le client est en 32 bits : l'ossature est donc")
    print("surestimée ici. Ce qu'on cherche n'est pas le chiffre absolu, c'est")
    print("LA PART QUI MANQUAIT à la mesure du programme 10.")
    print()

    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)

    nu = tas(lua)
    with io.open(os.path.join(ADDON, "Core.lua"), encoding="utf-8") as fh:
        lua.execute(fh.read())
    apres_core = tas(lua)

    t0 = time.perf_counter()
    for relatif in bases_du_toc():
        with io.open(os.path.join(ADDON, relatif), encoding="utf-8") as fh:
            lua.execute(fh.read())
    ms_bases = (time.perf_counter() - t0) * 1000.0
    apres_bases = tas(lua)

    print("1. LES DONNÉES SEULES  (ce que mesurait le programme 10)")
    print("   Core.lua ................... %8.1f Mo" % mo(apres_core - nu))
    print("   les 27 bases du .toc ....... %8.1f Mo   (%.0f ms)"
          % (mo(apres_bases - apres_core), ms_bases))
    print("   -> tas ..................... %8.1f Mo" % mo(apres_bases))
    print()

    # ---- les modules -----------------------------------------------------
    print("2. LES MODULES  (leur code, pas encore leurs index)")
    charges, refuses = 0, []
    avant_modules = apres_bases
    for nom in MODULES:
        chemin = os.path.join(ADDON, "Modules", nom)
        try:
            with io.open(chemin, encoding="utf-8") as fh:
                lua.execute(fh.read())
            charges += 1
        except Exception as ex:
            refuses.append((nom, str(ex).split("\n")[0][:70]))
    apres_modules = tas(lua)
    print("   %d modules chargés sur %d" % (charges, len(MODULES)))
    for nom, ex in refuses:
        print("     - %-22s refusé par le banc : %s" % (nom, ex))
    print("   code des modules ........... %8.1f Mo"
          % mo(apres_modules - avant_modules))
    print("   -> tas ..................... %8.1f Mo" % mo(apres_modules))
    if refuses:
        print("   (les modules refusés manquent : ce total est un PLANCHER)")
    print()

    # ---- les index dérivés : LA PART QUI MANQUAIT -------------------------
    print("3. LES INDEX DÉRIVÉS  <- CE QUI MANQUAIT À MA MESURE")
    print("   Ils ne sont dans AUCUN fichier : ils se construisent au login")
    print("   et vivent jusqu'à la déconnexion.")
    print()

    avant_index = apres_modules
    t0 = time.perf_counter()
    lua.globals()._PRECHAUFFER_CORE()
    ms = (time.perf_counter() - t0) * 1000.0
    apres_core_idx = tas(lua)
    print("   index inversés de Core ..... %8.1f Mo   (%.0f ms)"
          % (mo(apres_core_idx - avant_index), ms))
    print("     (titre de quête -> id, nom de créature -> id,")
    print("      nom d'objet du monde -> id)")

    t0 = time.perf_counter()
    lua.globals()._PRECHAUFFER_MODULES()
    ms = (time.perf_counter() - t0) * 1000.0
    apres_tout = tas(lua)
    n = int(lua.globals()._N_PRECHAUFFAGES or 0)
    print("   index des modules .......... %8.1f Mo   (%.0f ms, %d "
          "préchauffage(s))" % (mo(apres_tout - apres_core_idx), ms, n))
    print()
    print("   TOTAL DES INDEX DÉRIVÉS .... %8.1f Mo"
          % mo(apres_tout - avant_index))
    print()

    print("=" * 74)
    print("LE COMPTE")
    print("=" * 74)
    print("   données seules ............. %8.1f Mo   <- ce que j'avais mesuré"
          % mo(apres_bases))
    print("   + code des modules ......... %8.1f Mo"
          % mo(apres_modules - apres_bases))
    print("   + index dérivés ............ %8.1f Mo   <- ce que j'avais OUBLIÉ"
          % mo(apres_tout - apres_modules))
    print("   ------------------------------------")
    print("   TOTAL ...................... %8.1f Mo" % mo(apres_tout))
    print()
    manque = (apres_tout - apres_bases) / max(apres_bases, 1) * 100
    print("   La part oubliée vaut %.0f %% de ce que j'avais mesuré." % manque)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
