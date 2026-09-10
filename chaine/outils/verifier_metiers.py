# -*- coding: utf-8 -*-
"""
Test du module Métiers/Grimoire.

Reproduit la situation réelle : l'interface d'Ascension est compilée, ses noms
de cadres sont inconnus. Le module doit donc traduire en parcourant la fenêtre
sans jamais nommer un cadre, en s'appuyant uniquement sur les API de données.

Scénario : la fenêtre « Woodworking » de la capture d'écran de Dan.
"""
import sys

import lupa.lua51 as lupa_mod

ADDON = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns\AscensionFR"
# Le module s'appuie sur AFR.Parcourir du noyau : on charge donc l'addon dans
# le même ordre que le jeu, sinon le test ne prouve rien du réel.
FICHIERS = ["Core.lua", "Modules\\Metiers.lua"]

CONTEXTE = r"""
function AscensionFR_Stub() end
function strtrim(s) return (string.gsub(s or "", "^%s*(.-)%s*$", "%1")) end
function UnitName() return "Testeur" end
function UnitClass() return "Templar" end
function UnitRace() return "Dwarf" end
function UnitSex() return 2 end
function hooksecurefunc() end

-- ---- Fabrique de faux cadres, aux noms volontairement inconnus ----
local function FontString(texte)
    local fs = { _t = texte, _type = "FontString" }
    function fs:GetText() return self._t end
    function fs:SetText(v) self._t = v end
    function fs:GetObjectType() return "FontString" end
    return fs
end
_G.FontString = FontString

local function Cadre(regions, enfants)
    local c = { _r = regions or {}, _e = enfants or {} }
    function c:GetRegions() return unpack(self._r) end
    function c:GetChildren() return unpack(self._e) end
    function c:IsShown() return true end
    return c
end
_G.Cadre = Cadre

function CreateFrame()
    -- Ne retient que le gestionnaire d'événements : le module crée aussi un
    -- cadre de minuteur (OnUpdate) qu'il ne faut pas confondre avec lui.
    return { RegisterEvent = function() end,
             SetScript = function(self, quoi, f)
                 if quoi == "OnEvent" then _G._SCRIPT = f end
             end,
             HookScript = function() end,
             Show = function() end, Hide = function() end }
end
"""

# La fenêtre de la capture : titre, en-têtes, recettes, composants — chacun
# dans un cadre au nom inconnu et imbriqué.
FENETRE = r"""
TITRE      = FontString("Woodworking")
ENTETE1    = FontString("Crossbows")
RECETTE1   = FontString("Forestwood Crossbow")
RECETTE2   = FontString("Reliable Crossbow")
ENTETE2    = FontString("Polearms")
RECETTE3   = FontString("Sturdy Polearm")
COMPOSANT1 = FontString("Forestwood Shaft")
COMPOSANT2 = FontString("Coarse Thread")
INTOUCHABLE = FontString("Texte inconnu a ne pas toucher")

TradeSkillFrame = Cadre({ TITRE },
    { Cadre({ ENTETE1, RECETTE1, RECETTE2 }),
      Cadre({ ENTETE2, RECETTE3 },
            { Cadre({ COMPOSANT1, COMPOSANT2, INTOUCHABLE }) }) })

-- ---- Données renvoyées par le client (fiables) ----
local recettes = {
    { "Crossbows",           "header" },
    { "Forestwood Crossbow", "optimal", "|Henchant:500001|h[Forestwood Crossbow]|h" },
    { "Reliable Crossbow",   "optimal", "|Henchant:500002|h[Reliable Crossbow]|h" },
    { "Polearms",            "header" },
    { "Sturdy Polearm",      "optimal", "|Henchant:500003|h[Sturdy Polearm]|h" },
}
local composants = { [5] = { { "Forestwood Shaft", "|Hitem:600001|h" },
                             { "Coarse Thread",    "|Hitem:600002|h" } } }

function GetNumTradeSkills() return #recettes end
function GetTradeSkillInfo(i) return recettes[i][1], recettes[i][2] end
function GetTradeSkillRecipeLink(i) return recettes[i][3] end
function GetTradeSkillItemLink(i) return nil end
function GetTradeSkillLine() return "Woodworking" end
function GetTradeSkillNumReagents(i)
    return composants[i] and #composants[i] or 0
end
function GetTradeSkillReagentInfo(i, j)
    return composants[i][j][1]
end
function GetTradeSkillReagentItemLink(i, j)
    return composants[i][j][2]
end
function GetSpellName() return nil end
function GetSpellTabInfo() return nil end

-- ---- La LISTE des recettes (capture de Dan du 17/07) ----
-- Ascension a restylé la fenêtre standard sans la remplacer : ses boutons de
-- liste gardent les noms de Blizzard, et le parcours générique ne les
-- atteignait pas — le détail à droite passait en français, la liste non.
-- Le rang du bouton n'est pas celui de la recette : la liste défile.
TRADE_SKILLS_DISPLAYED = 4
DECALAGE = 1   -- on a fait défiler d'un cran

local function BoutonListe(texte)
    local b = { _t = texte, _protege = false }
    function b:GetText() return self._t end
    function b:SetText(v) self._t = v end
    function b:IsProtected() return self._protege end
    return b
end
_G.BoutonListe = BoutonListe

TradeSkillListScrollFrame = {}
function FauxScrollFrame_GetOffset() return DECALAGE end

-- Avec un décalage de 1 : bouton 1 -> recette 2, bouton 2 -> recette 3...
BOUTON1 = BoutonListe("Forestwood Crossbow")
BOUTON2 = BoutonListe("Reliable Crossbow [3]")   -- compteur collé au nom
BOUTON3 = BoutonListe("Polearms")
-- Un bouton protégé ne doit JAMAIS être écrit : cela contaminerait le chemin
-- d'exécution et bloquerait les actions du joueur. Le jeu nous le dit,
-- on ne le devine pas.
BOUTON4 = BoutonListe("Sturdy Polearm")
BOUTON4._protege = true
TradeSkillSkill1, TradeSkillSkill2 = BOUTON1, BOUTON2
TradeSkillSkill3, TradeSkillSkill4 = BOUTON3, BOUTON4

-- ---- Traductions disponibles ----
AscensionFR.DB.Libelles["Crossbows"] = "Arbalètes"
AscensionFR.DB.Libelles["Polearms"] = "Armes d'hast"
AscensionFR.DB.Libelles["Woodworking"] = "Travail du bois"
AscensionFR.DB.Sorts[500001] = { N = "Arbalète en bois-forestier" }
AscensionFR.DB.Sorts[500002] = { N = "Arbalète fiable" }
AscensionFR.DB.Sorts[500003] = { N = "Arme d'hast robuste" }
AscensionFR.DB.Objets[600001] = { N = "Hampe en bois-forestier" }
AscensionFR.DB.Objets[600002] = { N = "Fil grossier" }

_SCRIPT(nil, "TRADE_SKILL_SHOW")
"""


def main():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)
    for nom in FICHIERS:
        with open(ADDON + "\\" + nom, encoding="utf-8") as f:
            lua.execute(f.read())
    # Le noyau fournit Actif/Debug/Recolter ; on neutralise la récolte
    lua.execute("function AscensionFR.Recolter() end")
    lua.execute(FENETRE)
    g = lua.globals()

    cas = [
        ("titre du métier", g.TITRE.GetText(g.TITRE), "Travail du bois"),
        ("en-tête de catégorie", g.ENTETE1.GetText(g.ENTETE1), "Arbalètes"),
        ("en-tête imbriqué", g.ENTETE2.GetText(g.ENTETE2), "Armes d'hast"),
        ("recette", g.RECETTE1.GetText(g.RECETTE1),
         "Arbalète en bois-forestier"),
        ("recette (2e)", g.RECETTE2.GetText(g.RECETTE2), "Arbalète fiable"),
        ("recette imbriquée", g.RECETTE3.GetText(g.RECETTE3),
         "Arme d'hast robuste"),
        ("composant", g.COMPOSANT1.GetText(g.COMPOSANT1),
         "Hampe en bois-forestier"),
        ("composant (2e)", g.COMPOSANT2.GetText(g.COMPOSANT2), "Fil grossier"),
        ("texte inconnu -> intact",
         g.INTOUCHABLE.GetText(g.INTOUCHABLE),
         "Texte inconnu a ne pas toucher"),
        # La liste des recettes, avec un décalage de défilement de 1 :
        # le bouton 1 montre la recette 2.
        ("liste : bouton 1 traduit malgré le défilement",
         g.BOUTON1.GetText(g.BOUTON1), "Arbalète en bois-forestier"),
        ("liste : compteur [3] conservé",
         g.BOUTON2.GetText(g.BOUTON2), "Arbalète fiable [3]"),
        ("liste : en-tête de catégorie traduit",
         g.BOUTON3.GetText(g.BOUTON3), "Armes d'hast"),
        ("liste : bouton protégé -> JAMAIS touché",
         g.BOUTON4.GetText(g.BOUTON4), "Sturdy Polearm"),
    ]
    echecs = 0
    for description, obtenu, attendu in cas:
        if obtenu == attendu:
            print("  ok      %-28s %s" % (description, obtenu))
        else:
            print("  ECHEC   %-28s obtenu %r / attendu %r"
                  % (description, obtenu, attendu))
            echecs += 1
    print()
    print("%d échec(s)" % echecs)
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
