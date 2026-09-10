# -*- coding: utf-8 -*-
r"""Signalements, propositions et journal des échecs — réécrit au bloc 3.

Le FOND était vivant (capture d'infobulle, refus des doublons, journal,
auto-guérison) mais le DÉCOR du banc datait d'avant la fenêtre de
propositions de la 3.3.0 : son faux CreateFrame ne savait pas SetSize, le
banc mourait en construisant la fenêtre — le canal de collecte des joueurs
n'était couvert par rien (audit du 28/07). Ce banc-ci :

  - garde TOUTES les assertions d'origine (capture objet, doublon refusé,
    note libre, cadre photographié, journal S/O, stats ignorées,
    auto-guérison) ;
  - pilote la FENÊTRE DE PROPOSITIONS comme un joueur : ouverture par
    /afr signaler, clic sur une ligne, saisie, « Envoyer », doublon
    refusé, « Signaler à traduire », proposition vide refusée ;
  - prouve le correctif du filtre CorpsAuModele (bloc 3) : un modèle qui
    COMMENCE par une variable ($s1% …) journalise enfin son échec — il
    était invisible (3 520 modèles sur 47 620, mesurés à l'audit).

Usage : python outils/verifier_signalements.py
"""
import sys

import lupa.lua51 as lupa_mod

sys.stdout.reconfigure(encoding="utf-8")

ADDON = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns\AscensionFR"

CONTEXTE = r"""
function strtrim(s) return (string.gsub(s or "", "^%s*(.-)%s*$", "%1")) end
function UnitName() return "<joueur>" end
function UnitClass() return "Templar" end
function UnitRace() return "Dwarf" end
function UnitSex() return 2 end
function UnitIsPlayer() return false end
function UnitExists() return false end
function UnitGUID() return nil end
function hooksecurefunc() end
function print() end
function date() return "17/07/26 00:00" end
function GetTime() return 0 end
SlashCmdList = {}
tinsert = table.insert
UISpecialFrames = {}
ChatFontNormal = {}
ITEM_SPELL_TRIGGER_ONUSE = "Utiliser :"
ITEM_SPELL_TRIGGER_ONEQUIP = "Équipé :"
ITEM_SPELL_TRIGGER_ONPROC = "Chances quand vous touchez :"

-- Zone de texte : tout ce qu'une FontString du jeu sait faire d'utile ici.
local function FS(t)
    local z = { _t = t or "" }
    function z:GetText() return self._t end
    function z:SetText(v) self._t = v or "" end
    function z:GetObjectType() return "FontString" end
    function z:IsShown() return true end
    function z:SetPoint() end
    function z:SetJustifyH() end
    function z:SetTextColor() end
    function z:SetHeight() end
    function z:SetWidth() end
    return z
end
_G.FS = FS

-- L'atelier de cadres : assez riche pour que la VRAIE fenêtre de
-- propositions se construise (SetSize, ScrollFrame, EditBox…), assez
-- simple pour rester lisible. Les boutons s'indexent par leur libellé
-- (_BOUTONS) : le banc clique comme un joueur.
_BOUTONS = {}
function CreateFrame(genre, nom, parent, gabarit)
    local f = { _genre = genre or "Frame", _nom = nom, _scripts = {},
                _enfants = {}, _zones = {}, _t = "", _visible = false }
    function f:GetName() return self._nom end
    function f:GetObjectType() return self._genre end
    function f:GetParent() return parent end
    function f:RegisterEvent() end
    function f:RegisterForDrag() end
    function f:SetScript(k, fn) self._scripts[k] = fn end
    function f:GetScript(k) return self._scripts[k] end
    function f:HookScript(k, fn) self._scripts[k] = fn end
    function f:IsProtected() return false, false end
    function f:SetSize() end
    function f:SetPoint() end
    function f:SetAllPoints() end
    function f:SetFrameStrata() end
    function f:SetMovable() end
    function f:EnableMouse() end
    function f:SetBackdrop() end
    function f:SetBackdropColor() end
    function f:SetHeight() end
    function f:SetWidth() end
    function f:SetScrollChild() end
    function f:SetMultiLine() end
    function f:SetAutoFocus() end
    function f:SetFontObject() end
    function f:ClearFocus() end
    function f:SetFocus() end
    function f:StartMoving() end
    function f:StopMovingOrSizing() end
    function f:Show() self._visible = true end
    function f:Hide() self._visible = false end
    function f:IsShown() return self._visible end
    function f:GetText() return self._t end
    function f:SetText(v)
        self._t = v or ""
        if self._genre == "Button" then _BOUTONS[self._t] = self end
    end
    function f:CreateFontString()
        local z = FS("")
        table.insert(self._zones, z)
        return z
    end
    function f:CreateTexture()
        local tx = {}
        function tx:SetAllPoints() end
        function tx:SetTexture() end
        function tx:SetBlendMode() end
        function tx:SetAlpha() end
        return tx
    end
    function f:GetRegions() return unpack(self._zones) end
    function f:GetChildren() return unpack(self._enfants) end
    if parent and parent._enfants then table.insert(parent._enfants, f) end
    if nom then _G[nom] = f end
    return f
end
UIParent = CreateFrame("Frame", "UIParent")

-- L'info-bulle : HookScript EMPILE les gestionnaires (comme le jeu — depuis
-- la 3.3.0, Tooltips.lua ET Signaler.lua accrochent OnTooltipSetItem ; un
-- faux crochet qui écrase ferait tester le mauvais module, en silence).
_HOOKS = {}
function _TIRER(evt)
    for _, fn in ipairs(_HOOKS[evt] or {}) do fn(GameTooltip) end
end
GameTooltip = {}
function GameTooltip:GetName() return "GameTooltip" end
function GameTooltip:HookScript(evt, fn)
    _HOOKS[evt] = _HOOKS[evt] or {}
    table.insert(_HOOKS[evt], fn)
end
function GameTooltip:NumLines() return #LIGNES end
function GameTooltip:IsShown() return #LIGNES > 0 end
function GameTooltip:Show() end
function GameTooltip:GetItem()
    if LIGNES[1] then return LIGNES[1]:GetText(), _LIEN end
    return nil, _LIEN
end
function GameTooltip:GetSpell() return nil, nil, _SORT end
function GameTooltip:GetUnit() return nil, nil end
"""


def preparer():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute("LIGNES = {}")
    lua.execute(CONTEXTE)
    for f in ["Core.lua", "Modules\\Sorts.lua", "Modules\\Tooltips.lua",
              "Modules\\Signaler.lua", "Modules\\Recolte.lua"]:
        with open(ADDON + "\\" + f, encoding="utf-8") as fh:
            lua.execute(fh.read())
    return lua


def montrer(lua, lignes, lien=None, sort=None):
    """Peuple l'info-bulle simulée."""
    lua.execute("LIGNES = {}")
    table = lua.globals().LIGNES
    fs = lua.globals().FS
    for i, texte in enumerate(lignes):
        table[i + 1] = fs(texte)
        lua.globals()["GameTooltipTextLeft%d" % (i + 1)] = table[i + 1]
    lua.execute("_LIEN = " + ('"item:%d"' % lien if lien else "nil"))
    lua.execute("_SORT = " + (str(sort) if sort else "nil"))


def main():
    lua = preparer()
    echecs = 0

    def saved():
        return lua.globals().AscensionFRSaved

    def verifier(description, obtenu, attendu):
        nonlocal echecs
        if obtenu == attendu:
            print("  ok      %-56s %s" % (description, obtenu))
        else:
            print("  ECHEC   %s\n          obtenu %r\n          attendu %r"
                  % (description, obtenu, attendu))
            echecs += 1

    # --- capture directe (AFR.Signaler) sur une info-bulle d'objet ---------
    montrer(lua, ["Heavy Linen Bandage", "Use: Heals stuff."], lien=21991)
    lua.execute("AscensionFR.Signaler()")
    verifier("type capturé", saved().Signalements[1].T, "objet")
    verifier("ID capturé", saved().Signalements[1].ID, 21991)
    verifier("lignes capturées", saved().Signalements[1].L[2],
             "Use: Heals stuff.")
    lua.execute("AscensionFR.Signaler()")
    verifier("doublon refusé", len(saved().Signalements), 1)

    # --- note libre (le repli direct garde la casse) -----------------------
    lua.execute('AscensionFR.Signaler("Le PNJ Bob parle anglais")')
    verifier("note directe, casse gardée", saved().Signalements[2].N,
             "Le PNJ Bob parle anglais")
    verifier("type note", saved().Signalements[2].T, "note")

    # --- pas d'info-bulle : rien n'est enregistré --------------------------
    montrer(lua, [])
    lua.execute("AscensionFR.Signaler()")
    verifier("sans info-bulle, rien", len(saved().Signalements), 2)

    # --- pas d'info-bulle mais un cadre sous la souris : photographie -------
    lua.execute(r"""
        local cadre = {}
        function cadre:GetName() return "AscensionCraftingListButton3" end
        function cadre:GetParent() return nil end
        function cadre:GetObjectType() return "Button" end
        function cadre:GetRegions() return FS("Spicy Wolf Kabob [4]") end
        function GetMouseFocus() return cadre end
    """)
    montrer(lua, [])
    lua.execute("AscensionFR.Signaler()")
    verifier("cadre photographié", saved().Signalements[3].T, "cadre")
    verifier("chaîne des parents capturée", saved().Signalements[3].L[1],
             "cadre : AscensionCraftingListButton3")
    verifier("texte du cadre capturé", saved().Signalements[3].L[2],
             "texte : Spicy Wolf Kabob [4]")
    verifier("état du module métiers capturé", saved().Signalements[3].L[3],
             "TradeSkillFrame : absent")
    lua.execute("GetMouseFocus = nil")

    # --- LA FENÊTRE DE PROPOSITIONS (3.3.0) — pilotée comme un joueur -------
    print()
    montrer(lua, ["Heavy Linen Bandage", "Use: Heals stuff."], lien=21991)
    lua.execute('SlashCmdList["ASCENSIONFR"]("signaler")')
    fen = lua.globals().AscensionFRSignaler
    verifier("fenêtre construite et affichée", bool(fen and fen._visible),
             True)
    verifier("élément reconnu (objet + ID)",
             "objet" in (fen.elem.GetText(fen.elem) or ""), True)
    verifier("les 2 lignes de la bulle sont proposées",
             fen.rows[2].texte, "Use: Heals stuff.")
    # Le joueur clique la ligne fautive puis écrit sa traduction.
    lua.execute("AscensionFRSignaler.rows[2]._scripts.OnClick("
                "AscensionFRSignaler.rows[2])")
    lua.execute('AscensionFRSignalerSaisie:SetText('
                '"Utiliser : Soigne des trucs.")')
    lua.execute('_BOUTONS["Envoyer"]._scripts.OnClick()')
    prop = saved().Signalements[4]
    verifier("proposition rangée (type)", prop.T, "proposition")
    verifier("proposition : cible", prop.cible, "objet")
    verifier("proposition : ID", prop.ID, 21991)
    verifier("proposition : ligne actuelle", prop.actuel, "Use: Heals stuff.")
    verifier("proposition : texte proposé", prop.P,
             "Utiliser : Soigne des trucs.")
    verifier("la fenêtre se referme après l'envoi", fen._visible, False)
    # Le même joueur re-propose la même chose : refusé.
    lua.execute('SlashCmdList["ASCENSIONFR"]("signaler")')
    lua.execute("AscensionFRSignaler.rows[2]._scripts.OnClick("
                "AscensionFRSignaler.rows[2])")
    lua.execute('AscensionFRSignalerSaisie:SetText('
                '"Utiliser : Soigne des trucs.")')
    lua.execute('_BOUTONS["Envoyer"]._scripts.OnClick()')
    verifier("proposition en double refusée", len(saved().Signalements), 4)
    # Proposition vide : refusée aussi.
    lua.execute('AscensionFRSignalerSaisie:SetText("   ")')
    lua.execute('_BOUTONS["Envoyer"]._scripts.OnClick()')
    verifier("proposition vide refusée", len(saved().Signalements), 4)
    # « Signaler à traduire » : le joueur ne sait pas traduire, il marque.
    # (la ligne 2 — la ligne 1 est DÉJÀ signalée par la capture directe du
    # début, et le dédoublonnage la refuserait, à raison)
    lua.execute("AscensionFRSignaler.rows[2]._scripts.OnClick("
                "AscensionFRSignaler.rows[2])")
    lua.execute('_BOUTONS["Signaler à traduire"]._scripts.OnClick()')
    marque = saved().Signalements[5]
    verifier("« à traduire » rangé avec l'ID", marque.ID, 21991)
    verifier("« à traduire » : la ligne choisie", marque.L[1],
             "Use: Heals stuff.")
    # …et la MÊME ligne déjà signalée en direct est refusée, à raison.
    lua.execute('SlashCmdList["ASCENSIONFR"]("signaler")')
    lua.execute("AscensionFRSignaler.rows[1]._scripts.OnClick("
                "AscensionFRSignaler.rows[1])")
    lua.execute('_BOUTONS["Signaler à traduire"]._scripts.OnClick()')
    verifier("« à traduire » en double (vs capture directe) refusé",
             len(saved().Signalements), 5)

    # --- journal : sort connu qui ne s'aligne pas ---------------------------
    print()
    lua.execute(r"""
        AscensionFR.DB.Sorts[555] = { D = "Inflige $s1 points.",
                                      DE = "Deals $s1 damage." }
    """)
    montrer(lua, ["Some Spell", "A completely different displayed text."],
            sort=555)
    lua.execute("AscensionFR.TraduireInfobulleSort(GameTooltip, 555)")
    verifier("échec de sort journalisé (lignes séparées)",
             saved().EchecsAlignement.S[555][1],
             "A completely different displayed text.")

    # --- journal : ligne d'effet préfixée qui ne s'aligne pas ---------------
    # Le cas qui MÉRITE le journal : la ligne affichée est bien le texte
    # anglais du sort de l'objet, mais le modèle est PÉRIMÉ (le serveur a
    # ajouté une fin de phrase). Une ligne sans rapport (« Gibberish… »)
    # n'est PAS journalisée — c'est le rôle anti-bruit de CorpsAuModele,
    # vérifié deux crans plus bas avec la ligne de stats.
    lua.execute(r"""
        AscensionFR.DB.Objets[4242] = { N = "Babiole cassée", S = {"556"} }
        AscensionFR.DB.Sorts[556] = { D = "Rend $s1 points.",
                                      DE = "Restores $s1 points." }
    """)
    montrer(lua, ["Broken Trinket",
                  "Utiliser : Restores 25 points over 10 sec."], lien=4242)
    lua.execute('_TIRER("OnTooltipSetItem")')
    verifier("échec d'objet journalisé (modèle périmé)",
             saved().EchecsAlignement.O[4242],
             "Utiliser : Restores 25 points over 10 sec.")
    # Une ligne SANS rapport avec les sorts de l'objet reste hors journal.
    lua.execute("AscensionFRSaved.EchecsAlignement.O[4242] = nil")
    montrer(lua, ["Broken Trinket", "Utiliser : Gibberish incompatible."],
            lien=4242)
    lua.execute('_TIRER("OnTooltipSetItem")')
    verifier("ligne étrangère au sort : hors journal (anti-bruit)",
             saved().EchecsAlignement.O[4242], None)

    # --- CORRECTIF bloc 3 : modèle qui COMMENCE par une variable ------------
    # Avant : « $s1% chance… » contre « 15% chance… » -> les 12 premiers
    # caractères ne coïncidaient jamais, l'échec restait INVISIBLE (3 520
    # modèles concernés). Après normalisation, il est journalisé.
    lua.execute(r"""
        AscensionFR.DB.Objets[4245] = { N = "Babiole électrique",
                                        S = {"558"} }
        AscensionFR.DB.Sorts[558] = { D = "$s1% de chances d'électrocuter.",
                                      DE = "$s1% chance to zap." }
    """)
    montrer(lua, ["Zappy Trinket",
                  "Utiliser : 15% chance to zap targets."], lien=4245)
    lua.execute('_TIRER("OnTooltipSetItem")')
    verifier("modèle à variable en tête : échec ENFIN journalisé",
             saved().EchecsAlignement.O[4245],
             "Utiliser : 15% chance to zap targets.")

    # --- une ligne de stats qui échoue n'est PAS journalisée ----------------
    lua.execute("AscensionFRSaved.EchecsAlignement.O[4242] = nil")
    montrer(lua, ["Broken Trinket", "+5 Endurance et autres statistiques"],
            lien=4242)
    lua.execute('_TIRER("OnTooltipSetItem")')
    verifier("ligne de stats ignorée", saved().EchecsAlignement.O[4242], None)

    # --- le journal se soigne : un échec qui repasse s'efface ---------------
    print()
    lua.execute(r"""
        AscensionFR.DB.Sorts[557] = { D = "Rend $s1 points.",
                                      DE = "Restores $s1 points." }
        AscensionFRSaved.EchecsAlignement.S[557] = { "vieux texte" }
    """)
    montrer(lua, ["Old Spell", "Restores 25 points."], sort=557)
    lua.execute("AscensionFR.TraduireInfobulleSort(GameTooltip, 557)")
    verifier("échec de sort oublié après succès",
             saved().EchecsAlignement.S[557], None)

    lua.execute(r"""
        AscensionFR.DB.Objets[4243] = { N = "Fiole", S = {"557"} }
        AscensionFRSaved.EchecsAlignement.O[4243] = "vieux"
    """)
    montrer(lua, ["Vial", "Utiliser : Restores 25 points."], lien=4243)
    lua.execute('_TIRER("OnTooltipSetItem")')
    verifier("échec d'objet oublié après succès",
             saved().EchecsAlignement.O[4243], None)

    print()
    print("%d échec(s)" % echecs)
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
