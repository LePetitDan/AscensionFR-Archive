# -*- coding: utf-8 -*-
"""
Test du panneau d'options (Modules\\Options.lua).

Le panneau doit se ranger dans Échap -> Interface -> AddOns, refléter l'état
réel des bases, et ses cases à cocher doivent agir pour de bon — pas seulement
s'afficher.
"""
import sys

import lupa.lua51 as lupa_mod

ADDON = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns\AscensionFR"
FICHIERS = ["Core.lua", "Modules\\Options.lua", "Modules\\Recolte.lua"]

CONTEXTE = r"""
MESSAGES = {}
function print(...) table.insert(MESSAGES, tostring((select(1, ...)))) end
function strtrim(s) return (string.gsub(s or "", "^%s*(.-)%s*$", "%1")) end
function UnitName() return "<joueur>" end
function UnitClass() return "Templar" end
function UnitRace() return "Dwarf" end
function UnitSex() return 2 end
function hooksecurefunc() end
function GetTime() return 0 end
SlashCmdList = {}
RECHARGE = false
function ReloadUI() RECHARGE = true end
UIParent = nil
UISpecialFrames = {}
SELECTION = false
function GetAddOnMetadata() return "2.0" end
function GetBuildInfo() return "3.3.5", "12340" end
function GetLocale() return "enUS" end
CATEGORIE_AJOUTEE = nil
CATEGORIES_AJOUTEES = {}
function InterfaceOptions_AddCategory(p)
    table.insert(CATEGORIES_AJOUTEES, p)
    CATEGORIE_AJOUTEE = CATEGORIE_AJOUTEE or p
end
OUVERTURES = 0
function InterfaceOptionsFrame_OpenToCategory(p)
    OUVERTURES = OUVERTURES + 1
    PANNEAU_OUVERT = p
end

local function FS(nom)
    local fs = { _t = "" }
    function fs:SetText(t) self._t = t end
    function fs:GetText() return self._t end
    function fs:GetObjectType() return "FontString" end
    function fs:SetPoint() end
    function fs:SetJustifyH() end
    function fs:SetJustifyV() end
    function fs:SetWidth() end
    function fs:SetHeight() end
    function fs:SetSize() end
    function fs:SetTextColor() end
    function fs:SetFontObject() end
    function fs:SetVertexColor() end
    function fs:SetTexture() end
    function fs:SetTexCoord() end
    function fs:SetAllPoints() end
    if nom then _G[nom] = fs end
    return fs
end

function CreateFrame(genre, nom, parent, modele)
    local f = { _scripts = {} }
    function f:RegisterEvent() end
    function f:SetScript(s, fn) self._scripts[s] = fn end
    function f:GetScript(s) return self._scripts[s] end
    function f:HookScript() end
    function f:GetName() return nom end
    function f:SetPoint() end
    function f:SetSize() end
    function f:SetHeight() end
    function f:SetWidth() end
    function f:SetText(t) self._t = t end
    function f:GetText() return self._t end
    function f:Show() end
    function f:Hide() end
    function f:IsShown() return true end
    function f:IsVisible() return true end
    function f:GetNumMessages() return 0 end
    function f:AtBottom() return true end
    function f:ScrollToBottom() end
    function f:Enable() self._actif = true end
    function f:Disable() self._actif = false end
    function f:SetChecked(v) self._coche = v and true or false end
    function f:GetChecked() return self._coche end
    function f:SetJustifyH() end
    function f:SetFontObject() end
    function f:SetFading() end
    function f:SetMaxLines() end
    function f:EnableMouseWheel() end
    function f:Clear() self._messages = {} end
    function f:AddMessage(m)
        self._messages = self._messages or {}
        table.insert(self._messages, m)
    end
    function f:ScrollUp() end
    function f:ScrollDown() end
    function f:SetBackdrop() end
    function f:EnableMouse() end
    function f:SetMovable() end
    function f:RegisterForDrag() end
    function f:StartMoving() end
    function f:StopMovingOrSizing() end
    function f:SetFrameStrata() end
    function f:SetMultiLine() end
    function f:SetAutoFocus() end
    function f:SetScrollChild() end
    function f:HighlightText() SELECTION = true end
    function f:SetFocus() end
    function f:ClearFocus() end
    function f:CreateFontString(n) return FS(n) end
    function f:CreateTexture() return FS(nil) end
    function f:SetID(i) self._id = i end
    function f:GetID() return self._id or 0 end
    function f:SetNormalTexture() end
    function f:SetPushedTexture() end
    function f:SetHighlightTexture() end
    function f:SetDisabledTexture() end
    function f:GetNormalTexture() return FS(nil) end
    function f:SetAlpha() end
    function f:SetTextColor() end
    function f:SetFontObject() end
    function f:SetAllPoints() end
    function f:ClearAllPoints() end
    function f:SetBackdropColor() end
    function f:SetBackdropBorderColor() end
    function f:GetFontString() return FS(nil) end
    function f:SetCursorPosition() end
    function f:SetMaxLetters() end
    function f:SetTextInsets() end
    function f:SetNumeric() end
    function f:Insert() end
    function f:SetVertexColor() end
    function f:SetTexCoord() end
    if nom and modele and string.find(modele, "CheckButton") then
        FS(nom .. "Text")
    end
    if nom then _G[nom] = f end
    return f
end
"""


def main():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)
    for f in FICHIERS:
        with open(ADDON + "\\" + f, encoding="utf-8") as fh:
            lua.execute(fh.read())

    # Une partie en cours : des bases chargées, des textes en attente
    lua.execute("""
        AscensionFRSaved = { Options = {}, Recolte = {} }
        for i = 1, 9545 do AscensionFR.DB.Quetes[i] = { T = "x" } end
        for i = 1, 36429 do AscensionFR.DB.Sorts[i] = { N = "x" } end
        for i = 1, 7 do AscensionFR.Recolter("Divers", "inconnu " .. i, true) end
        AscensionFROptions:GetScript("OnShow")(AscensionFROptions)
    """)
    g = lua.globals()
    echecs = 0

    def verifier(description, obtenu, attendu):
        nonlocal echecs
        if obtenu == attendu:
            print("  ok      %s" % description)
            return True
        print("  ECHEC   %s\n          obtenu %r / attendu %r"
              % (description, obtenu, attendu))
        echecs += 1
        return False

    # --- Enregistrement -------------------------------------------------
    verifier("panneau ajouté à Interface -> AddOns",
             g.CATEGORIE_AJOUTEE is not None, True)
    verifier("nom affiché dans la liste",
             g.CATEGORIE_AJOUTEE.name, "Ascension |cff0099ffFR|r")

    # --- Contenu --------------------------------------------------------
    lua.execute("TOTAL_TEXTE = AscensionFROptions_TotalPourTest")
    # Les FontStrings sont anonymes : on relit via les cases nommées.
    verifier("case « activer » cochée quand la traduction est active",
             lua.globals().AscensionFROptionsActif.GetChecked(
                 lua.globals().AscensionFROptionsActif), True)
    verifier("case « débogage » décochée par défaut",
             lua.globals().AscensionFROptionsDebug.GetChecked(
                 lua.globals().AscensionFROptionsDebug) or False, False)

    # --- Les cases agissent vraiment ------------------------------------
    lua.execute("""
        local c = AscensionFROptionsActif
        c:SetChecked(false)
        c:GetScript("OnClick")(c)
        DESACTIVE = AscensionFRSaved.Options.desactive
        ACTIF = AscensionFR.Actif()
    """)
    verifier("décocher désactive réellement la traduction",
             (g.DESACTIVE, g.ACTIF), (True, False))

    lua.execute("""
        local c = AscensionFROptionsActif
        c:SetChecked(true)
        c:GetScript("OnClick")(c)
        REACTIVE = AscensionFR.Actif()
    """)
    verifier("recocher la réactive", g.REACTIVE, True)

    lua.execute("""
        local c = AscensionFROptionsDebug
        c:SetChecked(true)
        c:GetScript("OnClick")(c)
        DEBUG = AscensionFRSaved.Options.debug
    """)
    verifier("la case débogage agit", g.DEBUG, True)

    # --- /afr ouvre le panneau ------------------------------------------
    lua.execute('SlashCmdList["ASCENSIONFR"]("")')
    verifier("/afr ouvre le panneau", g.PANNEAU_OUVERT is not None, True)
    verifier("ouvert deux fois (contournement du bug 3.3.5)",
             g.OUVERTURES, 2)

    # --- /afr off marche toujours ---------------------------------------
    lua.execute('SlashCmdList["ASCENSIONFR"]("off"); OFF = AscensionFR.Actif()')
    verifier("/afr off fonctionne encore", g.OFF, False)
    lua.execute('SlashCmdList["ASCENSIONFR"]("on"); ON = AscensionFR.Actif()')
    verifier("/afr on fonctionne encore", g.ON, True)

    # --- Journal intégré (onglet du panneau, plus une sous-catégorie) ----
    # Design actuel : UN seul panneau enregistré, avec quatre ONGLETS
    # (Accueil / Réglages / Addons / Journal). L'ancien banc attendait une
    # sous-catégorie « Journal » séparée — design abandonné, assertion
    # corrigée le 24/07/2026 pour coller aux onglets.
    lua.execute("""
        AscensionFR.Debug("essai de journal", 42)
        JOURNAL_DERNIER = AscensionFR.Journal[#AscensionFR.Journal]
        AscensionFRJournal:GetScript("OnShow")(AscensionFRJournal)
        NB_CATEGORIES = #CATEGORIES_AJOUTEES
        PANNEAU_PRINCIPAL = CATEGORIES_AJOUTEES[1]
    """)
    verifier("un seul panneau enregistré (onglets, pas de sous-catégorie)",
             g.NB_CATEGORIES, 1)
    verifier("le panneau porte le bon nom",
             g.PANNEAU_PRINCIPAL is not None and g.PANNEAU_PRINCIPAL.name,
             "Ascension |cff0099ffFR|r")
    verifier("l'onglet Journal existe",
             g.AscensionFRJournal is not None, True)
    verifier("le message est dans le journal mémoire",
             g.JOURNAL_DERNIER is not None
             and "essai de journal 42" in g.JOURNAL_DERNIER, True)

    # --- Partage : zone de saisie remplie et présélectionnée -------------
    # 3.3.5 n'a pas d'accès au presse-papiers : le seul chemin est une zone
    # de saisie dont le texte est présélectionné (Ctrl+C par le joueur).
    lua.execute("""
        AscensionFR.Detailler("Rubrique d'essai", "CHAINE_ECARTEE_XYZ")
        SlashCmdList["ASCENSIONFR"]("copier")
    """)
    zone = lua.globals().AscensionFRCopieZone
    partage = zone.GetText(zone) if zone else ""
    verifier("/afr copier ouvre la fenêtre de partage",
             lua.globals().AscensionFRCopie is not None, True)
    verifier("le texte est présélectionné (Ctrl+C prêt)", g.SELECTION, True)
    verifier("le partage porte le contexte (version)",
             "AscensionFR 2.0" in partage, True)
    verifier("le partage porte le contexte (client)",
             "Client : 3.3.5 (12340)" in partage, True)
    verifier("le partage contient le journal",
             "essai de journal 42" in partage, True)
    verifier("le partage joint les rubriques de détail",
             "--- Rubrique d'essai (1) ---" in partage
             and "CHAINE_ECARTEE_XYZ" in partage, True)
    verifier("fenêtre fermable par Échap",
             lua.globals().UISpecialFrames[1], "AscensionFRCopie")

    # Les rubriques volumineuses ne doivent PAS noyer le journal : au
    # démarrage, 119 chaînes écartées y tenaient 250 lignes sur 250.
    lua.execute("""
        JOURNAL_ENTIER = table.concat(AscensionFR.Journal, "\\n")
    """)
    verifier("les détails restent hors du journal",
             "CHAINE_ECARTEE_XYZ" in (g.JOURNAL_ENTIER or ""), False)

    print()
    print("%d échec(s)" % echecs)
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
