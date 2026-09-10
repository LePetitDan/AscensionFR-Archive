# -*- coding: utf-8 -*-
"""
Vérification hors-jeu de l'addon AscensionFR : charge les fichiers Lua dans
un environnement WoW 3.3.5 simulé (API stub) pour détecter les erreurs de
syntaxe et les erreurs d'exécution au chargement.
"""
import os
import sys

import lupa.lua51 as lupa_mod

ADDON = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns\AscensionFR"

STUBS = r"""
-- ---- Environnement WoW 3.3.5 minimal ----
local enregistres = {}

-- Zone de texte : tout ce qu'un FontString sait faire, en inerte.
local function nouvelleFontString(nom)
    local fs = { _texte = "" }
    function fs:SetText(t) self._texte = t end
    function fs:GetText() return self._texte end
    function fs:GetObjectType() return "FontString" end
    function fs:SetPoint() end
    function fs:SetJustifyH() end
    function fs:SetJustifyV() end
    function fs:SetWidth() end
    function fs:SetHeight() end
    function fs:SetSize() end
    function fs:SetTexture() end
    function fs:SetTexCoord() end
    function fs:IsShown() return true end
    function fs:Show() end
    function fs:Hide() end
    if nom then _G[nom] = fs end
    return fs
end

function CreateFrame(genre, nom, parent, modele)
    local f = { _events = {}, _scripts = {} }
    function f:RegisterEvent(e) self._events[e] = true end
    function f:SetScript(s, fn) self._scripts[s] = fn end
    function f:HookScript(s, fn) self._scripts[s] = fn end
    function f:GetScript(s) return self._scripts[s] end
    function f:GetName() return nom end
    function f:IsShown() return true end
    function f:GetID() return self._id or 1 end
    function f:SetID(i) self._id = i end
    function f:SetBackdrop() end
    function f:SetBackdropColor() end
    function f:SetBackdropBorderColor() end
    -- Série complétée le 23/07/2026 (relevé exhaustif des méthodes
    -- appelées par Options.lua) : coquilles vides, le banc ne teste pas
    -- l'apparence.
    function f:AddMessage() end
    function f:Clear() end
    function f:ClearFocus() end
    function f:EnableMouse() end
    function f:EnableMouseWheel() end
    function f:HighlightText() end
    function f:IsVisible() return true end
    function f:ScrollDown() end
    function f:ScrollUp() end
    function f:SetAlpha() end
    function f:SetAutoFocus() end
    function f:SetCursorPosition() end
    function f:SetFading() end
    function f:SetFocus() end
    function f:SetFontObject() end
    function f:SetJustifyH() end
    function f:SetJustifyV() end
    function f:SetMaxLines() end
    function f:SetMovable() end
    function f:SetMultiLine() end
    function f:SetScrollChild() end
    function f:SetTexCoord() end
    function f:SetTexture() end
    function f:GetText() return "" end
    function f:SetText() end
    function f:NumLines() return 1 end
    function f:Show() end
    function f:Hide() end
    function f:Enable() end
    function f:Disable() end
    function f:SetPoint() end
    function f:SetSize() end
    function f:SetWidth() end
    function f:SetHeight() end
    function f:SetChecked(v) self._coche = v end
    function f:GetChecked() return self._coche end
    function f:IsProtected() return false, false end
    function f:RegisterForClicks() end
    function f:RegisterForDrag() end
    function f:SetFrameStrata() end
    function f:SetFrameLevel() end
    function f:SetHighlightTexture() end
    function f:ClearAllPoints() end
    function f:GetCenter() return 0, 0 end
    function f:GetEffectiveScale() return 1 end
    function f:SetOwner() end
    function f:AddLine() end
    function f:AddDoubleLine() end
    function f:SetJustifyH() end
    function f:SetJustifyV() end
    function f:SetFontObject() end
    function f:SetFading() end
    function f:SetMaxLines() end
    function f:EnableMouseWheel() end
    function f:Clear() end
    function f:AddMessage() end
    function f:ScrollUp() end
    function f:ScrollDown() end
    function f:SetBackdrop() end
    function f:EnableMouse() end
    function f:SetMovable() end
    function f:StartMoving() end
    function f:StopMovingOrSizing() end
    function f:SetMultiLine() end
    function f:SetAutoFocus() end
    function f:SetScrollChild() end
    function f:HighlightText() end
    function f:SetFocus() end
    function f:ClearFocus() end
    function f:GetRegions() return end
    function f:GetChildren() return end
    function f:GetNumChildren() return 0 end
    function f:GetItem() return nil, nil end
    function f:GetSpell() return nil, nil, nil end
    function f:GetUnit() return nil, nil end
    function f:CreateFontString(n) return nouvelleFontString(n) end
    function f:CreateTexture() return nouvelleFontString(nil) end
    -- Les modèles de case à cocher créent un « <nom>Text » global
    if nom and modele and string.find(modele, "CheckButton") then
        nouvelleFontString(nom .. "Text")
    end
    if nom then _G[nom] = f end
    table.insert(enregistres, f)
    return f
end

-- Panneau d'options du jeu
function InterfaceOptions_AddCategory(p) CATEGORIES_AJOUTEES = p end
function InterfaceOptionsFrame_OpenToCategory(p) PANNEAU_OUVERT = p end
function ReloadUI() end
function GetTime() return 0 end

GameTooltip = CreateFrame("GameTooltip", "GameTooltip")
ItemRefTooltip = CreateFrame("GameTooltip", "ItemRefTooltip")
Minimap = CreateFrame("Minimap", "Minimap")
function GetCursorPosition() return 0, 0 end
date = os.date
UISpecialFrames = {}
function GetAddOnMetadata() return "2.0" end
function GetBuildInfo() return "3.3.5", "12340" end
function GetLocale() return "enUS" end

function strtrim(s) return (string.gsub(s or "", "^%s*(.-)%s*$", "%1")) end
function UnitName() return "Testeur" end
function UnitClass() return "Reaper" end
function UnitRace() return "Human" end
function UnitSex() return 2 end
function UnitGUID() return "0xF130000FA00001" end
function UnitIsPlayer() return false end
function UnitExists() return true end
function GetQuestID() return 457 end
function GetTitleText() return "" end
function GetQuestText() return "" end
function GetObjectiveText() return "" end
function GetProgressText() return "" end
function GetRewardText() return "" end
function GetGossipText() return "" end
function GetGreetingText() return "" end
function GetQuestLogSelection() return 0 end
function GetQuestLogTitle() return nil end
function GetQuestLink() return nil end
function ItemTextGetText() return "" end
function GetMerchantItemLink() return nil end
function GetLootSlotLink() return nil end
function FauxScrollFrame_GetOffset() return 0 end
function QuestLogTitleButton_Resize() end
function hooksecurefunc(a, b, c) end
function ChatFrame_AddMessageEventFilter() end
function QuestInfo_Display() end
function QuestLog_Update() end
function WatchFrame_Update() end
function GossipFrameUpdate() end
function MerchantFrame_UpdateMerchantInfo() end
function LootFrame_Update() end
function print(...) end
SlashCmdList = {}
MERCHANT_ITEMS_PER_PAGE = 10
LOOTFRAME_NUMBUTTONS = 4
QUESTS_DISPLAYED = 6
LEVEL = "Level"
QuestInfoFrame = { questLog = false }
"""

TESTS = r"""
-- Races et classes viennent des DBC via DB_Libelles (plus de table devinée).
AscensionFR.DB.Libelles["Reaper"] = "Faucheur"
AscensionFR.DB.Libelles["Human"] = "Humain"
RESULTAT_SUB = AscensionFR.Substituer(
    "Bonjour $n, $gvaillant:vaillante; $c !$bSuite.")
-- Nom identique en français : absent de la base, l'anglais est correct.
AscensionFR.DB.Libelles["Reaper"] = nil
RESULTAT_SUB_INCONNUE = AscensionFR.Substituer("Classe : $c")
AscensionFR.DB.Creatures[1000] =
    { NE = "Mangy Nightsaber", N = "Sabre-de-nuit galeux" }
RESULTAT_OBJ = AscensionFR.TraduireObjectif("Mangy Nightsaber slain: 3/5")
RESULTAT_LIEN = AscensionFR.IdDepuisLienObjet(
    "|cff9d9d9d|Hitem:501973:0:0:0|h[Static Cowl]|h|r")
RESULTAT_GUID = AscensionFR.IdCreatureDepuisGUID("0xF130000FA00001")

-- La fenêtre des métiers colle « [3] » (fabrications possibles) au nom de
-- la recette : Parcourir doit retrouver le nom malgré le suffixe.
local porteur = CreateFrame()
REGION_RECETTE = porteur:CreateFontString()
REGION_RECETTE:SetText("Charred Wolf Meat [3]")
local cadre = {}
function cadre:GetRegions() return REGION_RECETTE end
function cadre:GetChildren() return end
AscensionFR.Parcourir(cadre,
    { ["Charred Wolf Meat"] = "Viande de loup carbonisée" })
RESULTAT_PARCOURIR = REGION_RECETTE:GetText()
"""


def main():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(STUBS)

    # Ordre de chargement du .toc
    fichiers = []
    with open(os.path.join(ADDON, "AscensionFR.toc"), encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()
            if ligne and not ligne.startswith("##"):
                fichiers.append(ligne.replace("\\", os.sep))

    erreurs = 0
    for rel in fichiers:
        chemin = os.path.join(ADDON, rel)
        if not os.path.exists(chemin):
            print(f"ABSENT  {rel}")
            erreurs += 1
            continue
        with open(chemin, encoding="utf-8") as f:
            code = f.read()
        try:
            lua.execute(code)
            print(f"ok      {rel}")
        except lupa_mod.LuaError as e:
            print(f"ERREUR  {rel}\n        {e}")
            erreurs += 1

    # Tests fonctionnels du moteur
    try:
        lua.execute(TESTS)
        g = lua.globals()
        attendus = [
            ("Substituer", g.RESULTAT_SUB,
             "Bonjour Testeur, vaillant Faucheur !\nSuite."),
            ("Substituer (classe hors base -> anglais)",
             g.RESULTAT_SUB_INCONNUE, "Classe : Reaper"),
            ("TraduireObjectif", g.RESULTAT_OBJ,
             "Sabre-de-nuit galeux tué(s) : 3/5"),
            ("IdDepuisLienObjet", g.RESULTAT_LIEN, 501973),
            ("IdCreatureDepuisGUID", g.RESULTAT_GUID, 0xFA0),
            ("Parcourir (suffixe [n] des métiers)", g.RESULTAT_PARCOURIR,
             "Viande de loup carbonisée [3]"),
        ]
        for nom, obtenu, attendu in attendus:
            if obtenu == attendu:
                print(f"ok      {nom}() -> {obtenu!r}")
            else:
                print(f"ERREUR  {nom}() -> {obtenu!r} (attendu {attendu!r})")
                erreurs += 1
    except lupa_mod.LuaError as e:
        print(f"ERREUR  tests fonctionnels : {e}")
        erreurs += 1

    print("---")
    print(f"{erreurs} erreur(s)")
    sys.exit(1 if erreurs else 0)


if __name__ == "__main__":
    main()
