# -*- coding: utf-8 -*-
"""
Test du module Quêtes sur le cas réel rapporté par Dan.

Symptôme : dans la fenêtre de détails d'Ascension, la description et les
objectifs étaient traduits mais le TITRE restait anglais — parce que le code
écrivait dans QuestInfoTitleText, qui n'existe pas dans leur fenêtre réécrite.
Le suivi affichait aussi ses objectifs en anglais.

Vérifie que, sans nommer aucun cadre :
  - le titre est traduit dans la fenêtre de détails ;
  - le texte de rendu d'une quête accomplie est traduit dans le suivi ;
  - les objectifs le sont aussi, y compris au format inversé d'Ascension
    (« 7/12 Bûche » et non « Bûche : 7/12 ») ;
  - un cadre protégé n'est jamais touché ;
  - un texte inconnu reste intact.
"""
import sys

import lupa.lua51 as lupa_mod

ADDON = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns\AscensionFR"

CONTEXTE = r"""
_evts = {}
function CreateFrame()
    return { RegisterEvent = function() end,
             SetScript = function(self, k, f) if k == "OnEvent" then _EVT = f end end,
             HookScript = function() end, Show = function() end, Hide = function() end }
end
-- Simulation fidèle : le hook s'exécute après la fonction d'origine.
function hooksecurefunc(nom, fn)
    local origine = _G[nom]
    _G[nom] = function(...)
        if origine then origine(...) end
        fn(...)
    end
end
function strtrim(s) return (string.gsub(s or "", "^%s*(.-)%s*$", "%1")) end
function UnitName() return "<joueur>" end
function UnitClass() return "Templar" end
function UnitRace() return "Dwarf" end
function UnitSex() return 2 end
function print() end
SlashCmdList = {}
QUESTS_DISPLAYED = 6
QuestInfoFrame = { questLog = true }
function QuestInfo_Display() end
function QuestLog_Update() end
function WatchFrame_Update() end
function GetQuestID() return 500005 end
function FauxScrollFrame_GetOffset() return 0 end

-- Le combat, que ce banc ne simulait pas — et c'est exactement pour ça que le
-- « suivi qui clignote » de la 3.0.0 est passé au travers : le seul chemin qui
-- se comportait mal était celui du combat, jamais emprunté ici.
EN_COMBAT = false
function InCombatLockdown() return EN_COMBAT end

local function FS(t)
    local f = { _t = t }
    function f:GetText() return self._t end
    function f:SetText(v) self._t = v end
    function f:GetObjectType() return "FontString" end
    return f
end
_G.FS = FS
local function Cadre(regions, enfants, protege)
    local c = { _r = regions or {}, _e = enfants or {}, _p = protege }
    function c:GetRegions() return unpack(self._r) end
    function c:GetChildren() return unpack(self._e) end
    function c:IsShown() return true end
    function c:IsProtected() return self._p, self._p end
    return c
end
_G.Cadre = Cadre
"""

# Le journal de Dan : une quête accomplie et une quête en cours.
JEU = r"""
-- Ascension inverse l'affichage des objectifs : « Bûche : 7/12 » -> « 7/12 Bûche »
function WatchFrame_ReverseQuestObjective(texte)
    local nom, x, y = string.match(texte, "^(.-)%s*:%s*(%d+)/(%d+)$")
    if nom then return x .. "/" .. y .. " " .. nom end
    return texte
end

local quetes = {
    { titre = "Timber for the Coldhewn", lien = "|Hquest:500005:11|h",
      objectifs = { "Frostpine Log: 7/12" }, rendu = nil },
    { titre = "Icehide the Unbroken", lien = "|Hquest:500006:11|h",
      objectifs = {},
      rendu = "Return to Old Kargan Stouthew at Coldhewn Camp in Dun Morogh." },
}
function GetNumQuestLogEntries() return #quetes end
function GetQuestLogTitle(i) return quetes[i].titre, 11, 0, 0, false end
function GetQuestLink(i) return quetes[i].lien end
function GetNumQuestLeaderBoards(i) return #quetes[i].objectifs end
function GetQuestLogLeaderBoard(j, i) return quetes[i].objectifs[j] end
function GetQuestLogCompletionText(i) return quetes[i].rendu end
function GetQuestLogSelection() return 1 end

-- Bases (telles que générées : identifiants réels de la partie de Dan)
AscensionFR.DB.Quetes[500005] = {
    TE = "Timber for the Coldhewn",
    T = "Bois pour le Coldhewn",
    O = "Abattez les arbres Dun Morogh près du camp Coldhewn.",
}
AscensionFR.DB.Quetes[500006] = {
    TE = "Icehide the Unbroken",
    T = "Icehide l'Ininterrompu",
    A = "Retournez voir le vieux Kargan Stouthew au camp Coldhewn à Dun Morogh.",
}
AscensionFR.DB.Objets[600100] = { N = "Bûche de Frostpine" }
AscensionFR.DB.Divers["Frostpine Log"] = "Bûche de Frostpine"

-- La fenêtre de détails d'Ascension : le titre est dans un cadre inconnu
TITRE_DETAILS = FS("Timber for the Coldhewn")
QuestLogFrame = Cadre({}, { Cadre({ TITRE_DETAILS }) })
QuestFrame = Cadre({})

-- Le suivi
SUIVI_TITRE1  = FS("Timber for the Coldhewn")
SUIVI_OBJ1    = FS("7/12 Frostpine Log")
SUIVI_TITRE2  = FS("Icehide the Unbroken")
SUIVI_RENDU   = FS("Return to Old Kargan Stouthew at Coldhewn Camp in Dun Morogh.")
SUIVI_INCONNU = FS("Texte que je ne connais pas")
PROTEGE       = FS("Timber for the Coldhewn")
WatchFrame = Cadre({ SUIVI_TITRE1, SUIVI_OBJ1, SUIVI_TITRE2, SUIVI_RENDU,
                     SUIVI_INCONNU },
                   { Cadre({ PROTEGE }, {}, true) })

-- Les VRAIES lignes du suivi. En jeu, tout le texte du suivi vit ici :
-- WatchFrame_SetLine() fait « line.text:SetText(texte) ». C'est le seul
-- endroit où le passage restreint (autorisé en combat) a le droit d'écrire.
WatchFrameLine1 = { text = FS("Timber for the Coldhewn") }
WatchFrameLine2 = { text = FS("7/12 Frostpine Log") }
WatchFrameLine3 = { text = FS("Icehide the Unbroken") }

-- Le bouton d'objet de quête : SÉCURISÉ. Le passage restreint ne doit jamais
-- s'en approcher (il porte un autre nom et n'est pas atteint par le parcours).
WatchFrameItem1 = Cadre({ FS("Timber for the Coldhewn") }, {}, true)

function REPEINDRE_EN_ANGLAIS()
    -- Ce que le jeu fait à CHAQUE mob tué : QUEST_LOG_UPDATE -> WatchFrame_Update
    -- -> tout le suivi réécrit en anglais.
    WatchFrameLine1.text:SetText("Timber for the Coldhewn")
    WatchFrameLine2.text:SetText("7/12 Frostpine Log")
    WatchFrameLine3.text:SetText("Icehide the Unbroken")
end
"""


def main():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)
    for f in ["Core.lua", "Modules\\Recolte.lua", "Modules\\Quetes.lua"]:
        with open(ADDON + "\\" + f, encoding="utf-8") as fh:
            lua.execute(fh.read())
    lua.execute(JEU)
    # Déclenche les deux traductions
    lua.execute("AscensionFRQuetes_TraduireSuivi = nil")
    lua.execute("WatchFrame_Update()")
    g = lua.globals()

    # Le hook n'existant pas dans le simulateur, on appelle via les événements
    lua.execute("if _EVT then _EVT(nil, 'QUEST_DETAIL') end")

    cas = [
        ("suivi : titre de quête", g.SUIVI_TITRE1.GetText(g.SUIVI_TITRE1),
         "Bois pour le Coldhewn"),
        ("suivi : objectif au format d'Ascension",
         g.SUIVI_OBJ1.GetText(g.SUIVI_OBJ1), "7/12 Bûche de Frostpine"),
        ("suivi : titre (2e quête)", g.SUIVI_TITRE2.GetText(g.SUIVI_TITRE2),
         "Icehide l'Ininterrompu"),
        ("suivi : texte de rendu (quête accomplie)",
         g.SUIVI_RENDU.GetText(g.SUIVI_RENDU),
         "Retournez voir le vieux Kargan Stouthew au camp Coldhewn à Dun Morogh."),
        ("suivi : texte inconnu -> intact",
         g.SUIVI_INCONNU.GetText(g.SUIVI_INCONNU), "Texte que je ne connais pas"),
        ("suivi : cadre protégé -> jamais touché",
         g.PROTEGE.GetText(g.PROTEGE), "Timber for the Coldhewn"),
        ("ligne : titre de quête",
         g.WatchFrameLine1.text.GetText(g.WatchFrameLine1.text),
         "Bois pour le Coldhewn"),
        ("ligne : objectif au format d'Ascension",
         g.WatchFrameLine2.text.GetText(g.WatchFrameLine2.text),
         "7/12 Bûche de Frostpine"),
    ]

    # ------------------------------------------------------------------
    # EN COMBAT — le cas qui manquait, et le bug qu'il attrape.
    #
    # Le joueur tue un mob : le jeu repeint tout le suivi en anglais. Avant le
    # correctif 3.0.1, l'addon s'abstenait complètement pendant le combat et
    # l'anglais restait affiché jusqu'à la fin du combat -> le suivi
    # « clignotait » entre les deux langues à chaque mob.
    # ------------------------------------------------------------------
    lua.execute("EN_COMBAT = true")
    lua.execute("REPEINDRE_EN_ANGLAIS()")
    lua.execute("WatchFrame_Update()")
    cas += [
        ("EN COMBAT : titre retraduit (anti-clignotement)",
         g.WatchFrameLine1.text.GetText(g.WatchFrameLine1.text),
         "Bois pour le Coldhewn"),
        ("EN COMBAT : objectif retraduit (anti-clignotement)",
         g.WatchFrameLine2.text.GetText(g.WatchFrameLine2.text),
         "7/12 Bûche de Frostpine"),
        ("EN COMBAT : bouton d'objet sécurisé -> jamais touché",
         g.WatchFrameItem1._r[1].GetText(g.WatchFrameItem1._r[1]),
         "Timber for the Coldhewn"),
    ]

    # Coupe-circuit : si un joueur doit désactiver le passage en combat, le
    # suivi doit REDEVENIR celui d'avant (anglais pendant le combat), pas
    # planter.
    lua.execute("AscensionFRSaved = AscensionFRSaved or {}")
    lua.execute("AscensionFRSaved.Options = AscensionFRSaved.Options or {}")
    lua.execute("AscensionFRSaved.Options.sansSuiviCombat = true")
    lua.execute("REPEINDRE_EN_ANGLAIS()")
    lua.execute("WatchFrame_Update()")
    cas.append(
        ("coupe-circuit sansSuiviCombat : on s'abstient bien",
         g.WatchFrameLine1.text.GetText(g.WatchFrameLine1.text),
         "Timber for the Coldhewn"))
    lua.execute("AscensionFRSaved.Options.sansSuiviCombat = nil")
    lua.execute("EN_COMBAT = false")

    echecs = 0
    for description, obtenu, attendu in cas:
        if obtenu == attendu:
            print("  ok      %-42s %s" % (description, obtenu))
        else:
            print("  ECHEC   %-42s" % description)
            print("          obtenu  : %r" % obtenu)
            print("          attendu : %r" % attendu)
            echecs += 1
    print()
    print("%d échec(s)" % echecs)
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
