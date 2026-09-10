# -*- coding: utf-8 -*-
r"""Banc du circuit d'interface VIVANT — réécrit au bloc 3 (28/07/2026).

L'ancien banc testait la traduction de MASSE (AppliquerGlobalStrings),
coupée volontairement depuis la 1.6.4 (doctrine taint) : ses 9 échecs
étaient le rouge d'un circuit mort. Ce banc-ci couvre ce qui tourne
RÉELLEMENT chez les joueurs :

  A. le CANAL MOTEUR d'InterfaceUI.lua — le seul circuit d'écriture de
     globales encore actif (clés prouvées en jeu, une à une) — et TOUTES
     les gardes héritées de l'ancien banc, portées sur ce circuit :
     format incompatible refusé, réordonnancement %2$s accepté, largeur
     %2d n'est pas un rang, liste noire intacte, LuesClient ne bloque pas
     une clé prouvée, l'application de masse RESTE coupée ;
  B. les SIX surfaces d'InterfaceCiblee.lua (micro-menu, compte à rebours,
     menu Échap, fenêtres d'options, bulles d'options, fenêtres de
     confirmation) — c'était l'angle mort : le module n'était touché qu'en
     compilation, aucune surface déclenchée (audit du 28/07). La cohérence
     DELETE (le mot demandé = le mot que le code attend) vit ici.

Usage : python outils/verifier_interface.py
"""
import sys

import lupa.lua51 as lupa_mod

sys.stdout.reconfigure(encoding="utf-8")

ADDON = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
         r"\AscensionFR\Modules")

CONTEXTE = r"""
-- ---------------------------------------------------------------- harnais
AscensionFR = { DB = { UI = {}, ListeNoire = {}, LuesClient = {},
                       Reglages = {}, ObjetsNoms = {} }, Details = {} }
function AscensionFR.Actif() return true end
function AscensionFR.Debug() end
function AscensionFR.Detailler(rubrique, ligne)
    local d = AscensionFR.Details[rubrique] or {}
    AscensionFR.Details[rubrique] = d
    table.insert(d, ligne)
end

_EVENEMENTS = {}
function CreateFrame()
    local f = { _scripts = {} }
    function f:RegisterEvent() end
    function f:SetScript(k, fn)
        self._scripts[k] = fn
        if k == "OnEvent" then table.insert(_EVENEMENTS, fn) end
    end
    function f:GetScript(k) return self._scripts[k] end
    return f
end

function hooksecurefunc(a, b, c)
    if c == nil then
        local nom, crochet = a, b
        local origine = _G[nom] or function() end
        _G[nom] = function(...)
            origine(...)
            crochet(...)
        end
    else
        local t, nom, crochet = a, b, c
        local origine = t[nom] or function() end
        t[nom] = function(...)
            origine(...)
            crochet(...)
        end
    end
end

-- Zone de texte (FontString) minimale.
function FS(texte)
    local z = { _t = texte or "" }
    function z:GetText() return self._t end
    function z:SetText(v) self._t = v end
    function z:SetFormattedText(gabarit, ...)
        self._t = string.format(gabarit, ...)
    end
    function z:GetObjectType() return "FontString" end
    return z
end

-- L'info-bulle du jeu : les crochets s'y empilent comme en vrai.
GameTooltip = { _lignes = 0, _owner = nil }
function GameTooltip:GetName() return "GameTooltip" end
function GameTooltip:NumLines() return self._lignes end
function GameTooltip:Show() end
function GameTooltip:GetOwner() return self._owner end
function GameTooltip:HookScript(evt, fn)
    _TIP_HOOKS = _TIP_HOOKS or {}
    _TIP_HOOKS[evt] = _TIP_HOOKS[evt] or {}
    table.insert(_TIP_HOOKS[evt], fn)
end

-- Cadres du menu Échap et des options : HookScript retenu pour que le banc
-- déclenche OnShow lui-même, comme le jeu le ferait.
local function CadreAvecTexte(genre, texte)
    local c = { _genre = genre, _t = texte, _hooks = {}, _enfants = {},
                _zones = {} }
    function c:GetObjectType() return self._genre end
    function c:GetText() return self._t end
    function c:SetText(v) self._t = v end
    function c:GetRegions() return unpack(self._zones) end
    function c:GetChildren() return unpack(self._enfants) end
    function c:HookScript(evt, fn) self._hooks[evt] = fn end
    function c:IsShown() return false end
    function c:GetParent() return self._parent end
    return c
end
_G.CadreAvecTexte = CadreAvecTexte

EscapeMenu = CadreAvecTexte("Frame")
BOUTON_LOGOUT = CadreAvecTexte("Button", "Logout")
BOUTON_DEJA_FR = CadreAvecTexte("Button", "Réglages DragonUI")
SAISIE_MACRO = CadreAvecTexte("EditBox", "Logout")
EscapeMenu._enfants = { BOUTON_LOGOUT, BOUTON_DEJA_FR, SAISIE_MACRO }

InterfaceOptionsFrame = CadreAvecTexte("Frame")
ZONE_OPTIONS = FS("Objectives")
ZONE_OPTIONS.SetText = function(self, v) self._t = v end
InterfaceOptionsFrame._zones = { ZONE_OPTIONS }
VideoOptionsFrame = CadreAvecTexte("Frame")
AudioOptionsFrame = CadreAvecTexte("Frame")
CADRE_ETRANGER = CadreAvecTexte("Frame")

-- Fenêtres contextuelles simulées.
function StaticPopup_OnUpdate() end
function StaticPopup_Show() end
function StaticPopup_Resize() end
StaticPopup1 = { which = nil, timeleft = 0, _shown = false }
function StaticPopup1:GetName() return "StaticPopup1" end
function StaticPopup1:IsShown() return self._shown end
StaticPopup1Text = FS("")
StaticPopup1Button1 = CadreAvecTexte("Button", "")
StaticPopup1Button1.IsShown = function() return true end
StaticPopup1Button2 = CadreAvecTexte("Button", "")
StaticPopup1Button2.IsShown = function() return true end
StaticPopup2 = { which = nil, _shown = false }
function StaticPopup2:GetName() return "StaticPopup2" end
function StaticPopup2:IsShown() return false end

-- ------------------------------------- chaînes du client (anglais Ascension)
DODGE = "Dodge"
PARRY = "Parry"
RESIST = "Resist %d"
ABSORB = "Absorb %2d"
BLOCK = "Block"
EVADE = "Evade"
COMBAT_TEXT_DODGE = "%s dodges"
COMBAT_TEXT_MISS = "Miss"
TOOLTIP_TALENT_RANK = "Rank %d/%d"
TOOLTIP_TALENT_LEARN = "Click to learn"
GAMEOPTIONS_MENU = "Options"
CHARACTER_BUTTON = "Character Info"
LOGOUT = "Logout"
OBJECTIVES_LABEL = "Objectives"
OPTION_TOOLTIP_UNIT_NAME_OWN = "Display your character's name in the game world."
INVITATION = "%s invites you to a group."
DELETE_GOOD_ITEM = "Do you want to destroy %s?\n\nType \"DELETE\" into the field to confirm."
DELETE_ITEM_CONFIRM_STRING = "DELETE"
QUIT_NOW = "Exit now"
CANCEL = "Cancel"

-- ------------------------------------------------- nos traductions (DB.UI)
local UI = AscensionFR.DB.UI
UI.DODGE = "Esquive"                              -- clé prouvée, simple
UI.PARRY = "Parade %s"                            -- argument EN TROP : refus
UI.RESIST = "%1$d résisté"                        -- réordonnancement : accepté
UI.ABSORB = "Absorbe %2d"                         -- %2d = largeur, pas un rang
UI.BLOCK = "Bloqué"                               -- dans LuesClient ET prouvée
UI.COMBAT_TEXT_DODGE = "%s esquive"
UI.COMBAT_TEXT_MISS = "Raté"                      -- en liste noire : refus
UI.TOOLTIP_TALENT_RANK = "Rang %d de %d/%d"       -- incompatible : refus
UI.TOOLTIP_TALENT_LEARN = "Cliquez pour apprendre"
UI.GAMEOPTIONS_MENU = "Options du jeu"            -- NON prouvée : masse coupée
UI.CHARACTER_BUTTON = "Personnage"
UI.LOGOUT = "Se déconnecter"
UI.OBJECTIVES_LABEL = "Objectifs"
UI.OPTION_TOOLTIP_UNIT_NAME_OWN =
    "Affiche le nom de votre personnage dans le monde."
UI.INVITATION = "%s vous invite à rejoindre un groupe."
UI.DELETE_GOOD_ITEM =
    "Voulez-vous détruire %s ?\n\nTapez \"EFFACER\" dans le champ pour confirmer."
UI.QUIT_TIMER = "%d %s until exit"                -- jamais lu : FORCEES prime
UI.QUIT_NOW = "Sortir maintenant"
UI.CANCEL = "Annuler"

AscensionFR.DB.LuesClient.BLOCK = true            -- prouvée > LuesClient
AscensionFR.DB.LuesClient.EVADE = true
AscensionFR.DB.ListeNoire.COMBAT_TEXT_MISS = true
AscensionFR.DB.ObjetsNoms["Bent Sword"] = "Épée tordue"
"""


def main():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)
    for module in ("InterfaceUI.lua", "InterfaceCiblee.lua"):
        with open(ADDON + "\\" + module, encoding="utf-8") as f:
            lua.execute(f.read())
    # Le jeu charge l'addon : tous les OnEvent reçoivent ADDON_LOADED.
    lua.execute('for _, fn in ipairs(_EVENEMENTS) do '
                'fn(nil, "ADDON_LOADED", "AscensionFR") end')
    g = lua.globals()
    echecs = 0

    def verifier(description, obtenu, attendu):
        nonlocal echecs
        if obtenu == attendu:
            print("  ok      %s" % description)
        else:
            print("  ECHEC   %s" % description)
            print("          obtenu  : %r" % (obtenu,))
            print("          attendu : %r" % (attendu,))
            echecs += 1

    print("=== A. Le canal moteur (InterfaceUI) et ses gardes ===")
    verifier("clé prouvée simple -> écrite", g.DODGE, "Esquive")
    verifier("format %s identique -> écrite",
             g.COMBAT_TEXT_DODGE, "%s esquive")
    verifier("réordonnancement %1$d -> écrite", g.RESIST, "%1$d résisté")
    verifier("largeur %2d n'est pas un rang -> écrite",
             g.ABSORB, "Absorbe %2d")
    verifier("prouvée MAIS dans LuesClient -> écrite quand même",
             g.BLOCK, "Bloqué")
    verifier("argument en trop -> refusée, reste anglais", g.PARRY, "Parry")
    verifier("signature incompatible (talents CoA) -> refusée",
             g.TOOLTIP_TALENT_RANK, "Rank %d/%d")
    verifier("talents CoA compatible -> écrite",
             g.TOOLTIP_TALENT_LEARN, "Cliquez pour apprendre")
    verifier("liste noire -> INTACTE même prouvée",
             g.COMBAT_TEXT_MISS, "Miss")
    verifier("non traduite -> intacte", g.EVADE, "Evade")
    verifier("l'application de MASSE reste coupée (clé non prouvée)",
             g.GAMEOPTIONS_MENU, "Options")

    print()
    print("=== B. Les six surfaces d'InterfaceCiblee ===")
    # 1. Micro-menu : la bulle garde le raccourci, seule l'étiquette change.
    lua.execute(r"""
        GameTooltipTextLeft1 = FS("Character Info (C)")
        GameTooltip._lignes = 1
        GameTooltip:Show()
    """)
    verifier("1. micro-menu : étiquette traduite, raccourci conservé",
             g.GameTooltipTextLeft1.GetText(g.GameTooltipTextLeft1),
             "Personnage (C)")

    # 2. Compte à rebours de sortie : UN seul %d, boutons repeints.
    lua.execute(r"""
        StaticPopup1.which = "QUIT"
        StaticPopup1.timeleft = 14.2
        StaticPopup_OnUpdate(StaticPopup1)
    """)
    verifier("2. compte à rebours : un seul %d, unité en clair",
             g.StaticPopup1Text.GetText(g.StaticPopup1Text),
             "Sortie dans 15 sec")
    verifier("2. bouton « Exit now » repeint",
             g.StaticPopup1Button1.GetText(g.StaticPopup1Button1),
             "Sortir maintenant")
    verifier("2. bouton « Cancel » repeint",
             g.StaticPopup1Button2.GetText(g.StaticPopup1Button2), "Annuler")

    # 3. Menu Échap : repeint à l'ouverture, saisies jamais touchées.
    lua.execute('EscapeMenu._hooks.OnShow(EscapeMenu)')
    verifier("3. menu Échap : « Logout » traduit",
             g.BOUTON_LOGOUT.GetText(g.BOUTON_LOGOUT), "Se déconnecter")
    verifier("3. bouton déjà français (DragonUI) intact",
             g.BOUTON_DEJA_FR.GetText(g.BOUTON_DEJA_FR),
             "Réglages DragonUI")
    verifier("3. une zone de saisie n'est JAMAIS touchée",
             g.SAISIE_MACRO.GetText(g.SAISIE_MACRO), "Logout")

    # 4. Fenêtres d'options : index inverse, à l'ouverture.
    lua.execute('InterfaceOptionsFrame._hooks.OnShow(InterfaceOptionsFrame)')
    verifier("4. fenêtre d'options : libellé traduit par l'index inverse",
             g.ZONE_OPTIONS.GetText(g.ZONE_OPTIONS), "Objectifs")

    # 5. Bulles d'options : traduites chez nous, jamais ailleurs.
    lua.execute(r"""
        GameTooltip._owner = InterfaceOptionsFrame
        GameTooltipTextLeft1 = FS(OPTION_TOOLTIP_UNIT_NAME_OWN)
        GameTooltip._lignes = 1
        GameTooltip:Show()
    """)
    verifier("5. bulle d'option (propriétaire chez nous) : traduite",
             g.GameTooltipTextLeft1.GetText(g.GameTooltipTextLeft1),
             "Affiche le nom de votre personnage dans le monde.")
    lua.execute(r"""
        GameTooltip._owner = CADRE_ETRANGER
        GameTooltipTextLeft1 = FS(OPTION_TOOLTIP_UNIT_NAME_OWN)
        GameTooltip:Show()
    """)
    verifier("5. bulle d'un cadre ÉTRANGER : jamais touchée",
             g.GameTooltipTextLeft1.GetText(g.GameTooltipTextLeft1),
             "Display your character's name in the game world.")

    # 6. Fenêtres de confirmation : gabarits composés + pont des objets.
    lua.execute(r"""
        StaticPopup1.which = "INVITATION"
        StaticPopup1._shown = true
        StaticPopup1Text:SetText("Bob invites you to a group.")
        StaticPopup_Show()
    """)
    verifier("6. invitation composée : nom conservé, phrase française",
             g.StaticPopup1Text.GetText(g.StaticPopup1Text),
             "Bob vous invite à rejoindre un groupe.")
    lua.execute(r"""
        StaticPopup1.which = "DELETE_GOOD_ITEM"
        StaticPopup1Text:SetText(
            "Do you want to destroy Bent Sword?\n\nType \"DELETE\" into "
            .. "the field to confirm.")
        StaticPopup_Show()
    """)
    texte_delete = g.StaticPopup1Text.GetText(g.StaticPopup1Text)
    verifier("6. destruction : le nom d'objet passe par le pont",
             texte_delete.startswith("Voulez-vous détruire Épée tordue ?"),
             True)
    # LA COHÉRENCE DELETE, héritée de l'ancien banc : la fenêtre française
    # doit demander le mot que le code compare (la globale jamais écrite).
    verifier("6. cohérence : la fenêtre demande le mot attendu par le code",
             ('"%s"' % g.DELETE_ITEM_CONFIRM_STRING) in texte_delete, True)
    verifier("6. la consigne EFFACER n'apparaît nulle part",
             "EFFACER" in texte_delete, False)
    lua.execute(r"""
        StaticPopup1.which = "CAMP"
        StaticPopup1Text:SetText("Some unrelated popup text.")
        StaticPopup_Show()
    """)
    verifier("6. fenêtre hors liste : intacte",
             g.StaticPopup1Text.GetText(g.StaticPopup1Text),
             "Some unrelated popup text.")

    print()
    print("%d échec(s)" % echecs)
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
