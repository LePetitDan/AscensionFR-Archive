# -*- coding: utf-8 -*-
"""
Test de la traduction d'une info-bulle de sort entière, telle qu'Ascension
la compose — et de l'absence de GetQuestID sur leur client.

Cas réels rapportés par Dan :
  - « Testament de foi » : la description est suivie d'autres lignes (« Applies
    Sacred Restraint », l'encadré du buff). Prendre « la dernière ligne longue »
    faisait aligner le modèle contre « Cannot be targeted by Testaments. » :
    échec, description laissée en anglais.
  - « Libram de consécration » : le modèle contient le marquage maison
    d'Ascension (@ext:...:ext@) que le client retire avant affichage. Le
    littéral « @ext: » ne correspondait à rien dans l'affiché : alignement
    impossible, description laissée en anglais (3 646 sorts dans ce cas).
  - Marquage @s:id:0@ : le client insère à cet endroit la description d'un
    autre sort (séparateur, icône, nom compris). La capture doit absorber le
    bloc inséré sans qu'on imite le rendu.
  - GetQuestID() n'existe pas chez Ascension : le module Quêtes plantait à
    chaque dialogue de PNJ.

CODE RETOUR — ce banc rend 1 EN FONCTIONNEMENT NORMAL : 9 assertions, 8 ok,
1 échec voulu (le bloc @s:, écart connu et assumé, détaillé au § correspondant
plus bas). Il n'est donc PAS branchable tel quel sur une barrière automatique :
construire_zip_release.py s'arrête à tout code retour non nul. Seuil de lecture
à l'œil : 1 échec = normal, 2 = régression.
"""
import sys

import lupa.lua51 as lupa_mod

ADDON = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns\AscensionFR"

CONTEXTE = r"""
function strtrim(s) return (string.gsub(s or "", "^%s*(.-)%s*$", "%1")) end
function UnitName() return "<joueur>" end
function UnitClass() return "Templar" end
function UnitRace() return "Dwarf" end
function UnitSex() return 2 end
function hooksecurefunc() end
function print() end
SlashCmdList = {}
function GetTime() return 0 end

-- Le client d'Ascension N'A PAS GetQuestID : on ne le définit donc pas ici.
function GetQuestLogSelection() return 0 end
function GetQuestLink() return nil end
function GetNumQuestLogEntries() return 0 end
function GetQuestLogTitle() return nil end
function GetProgressText() return "" end
function GetRewardText() return "" end
function QuestInfo_Display() end
function QuestLog_Update() end
function WatchFrame_Update() end
QuestInfoFrame = { questLog = false }

TITRE_OFFERT = "Timber for the Coldhewn"
function GetTitleText() return TITRE_OFFERT end

local function FS(t)
    local f = { _t = t }
    function f:GetText() return self._t end
    function f:SetText(v) self._t = v end
    function f:GetObjectType() return "FontString" end
    function f:IsShown() return true end
    return f
end
_G.FS = FS

-- Retient le dernier gestionnaire d'événements enregistré : c'est par lui que
-- les modules réagissent, un test qui ne le déclenche pas ne prouve rien.
_EVT = nil
function CreateFrame()
    local f = { _s = {} }
    function f:RegisterEvent() end
    function f:SetScript(k, fn)
        self._s[k] = fn
        if k == "OnEvent" then _EVT = fn end
    end
    function f:GetScript(k) return self._s[k] end
    function f:HookScript() end
    function f:Show() end
    function f:Hide() end
    function f:IsProtected() return false, false end
    return f
end
"""

# L'info-bulle exacte de la capture de Dan (sort « Testament de foi »).
INFOBULLE = r"""
LIGNES = {
    FS("Testament of Faith"),
    FS("Energy: 50"),
    FS("Instant"),
    FS("Say a prayer for an ally, healing them for 274."),
    FS("Applies Sacred Restraint for 1 min."),
    FS("Sacred Restraint"),
    FS("Cannot be targeted by Testaments."),
}
GameTooltip = {}
function GameTooltip:GetName() return "GameTooltip" end
function GameTooltip:NumLines() return #LIGNES end
-- L'addon demande l'ÉTAT de l'info-bulle avant de la redessiner
-- (Sorts.lua:970 : « if modifie and tooltip:IsShown() then tooltip:Show() end »).
-- Sans ce stub le banc mourait sur « attempt to call method 'IsShown' (a nil
-- value) » dès le premier sort, AVANT la première assertion. Ce que ça donnait,
-- remesuré le 27/07/2026 en retirant ce seul stub d'une copie : traceback lupa
-- sur Sorts.lua:970, 0 assertion jouée, CODE RETOUR 1 — un rouge bruyant, pas
-- un faux vert (le dépôt le dit déjà : rapports/bancs_essai.txt:242,
-- « verifier_infobulle.py -> ROUGE (code 1) »). Les 9 vérifications
-- d'aujourd'hui n'étaient pas muettes : elles n'existaient pas. Même stub que
-- verifier_signalements.py:64.
function GameTooltip:IsShown() return #LIGNES > 0 end
function GameTooltip:Show() end
for i, l in ipairs(LIGNES) do _G["GameTooltipTextLeft" .. i] = l end

AscensionFR.DB.Sorts[801478] = {
    N = "Testament de foi",
    D = "Dites une prière pour un allié, le soignant de ${$m1+$SP*0.4}.",
    DE = "Say a prayer for an ally, healing them for ${$m1+$SP*0.4}.",
}
RESULTAT = AscensionFR.TraduireInfobulleSort(GameTooltip, 801478)
"""


def main():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)
    lua.execute("AscensionFR = { DB = { Sorts = {}, Quetes = {} } }")
    for f in ["Core.lua", "Modules\\Recolte.lua", "Modules\\Sorts.lua"]:
        with open(ADDON + "\\" + f, encoding="utf-8") as fh:
            lua.execute(fh.read())
    lua.execute(INFOBULLE)
    g = lua.globals()
    lignes = g.LIGNES
    echecs = 0

    def verifier(description, obtenu, attendu):
        nonlocal echecs
        if obtenu == attendu:
            print("  ok      %-46s %s" % (description, obtenu))
        else:
            print("  ECHEC   %-46s\n          obtenu %r / attendu %r"
                  % (description, obtenu, attendu))
            echecs += 1

    verifier("nom du sort", lignes[1].GetText(lignes[1]), "Testament de foi")
    verifier("description trouvée parmi les lignes et résolue",
             lignes[4].GetText(lignes[4]),
             "Dites une prière pour un allié, le soignant de 274.")
    verifier("ligne suivante -> intacte", lignes[5].GetText(lignes[5]),
             "Applies Sacred Restraint for 1 min.")
    verifier("encadré du buff -> intact", lignes[7].GetText(lignes[7]),
             "Cannot be targeted by Testaments.")

    # --- Marquage @ext: (« Libram de consécration », capture de Dan) -------
    # Le client retire @ext:/:ext@ et garde le contenu, dans le même
    # FontString (prouvé par la récolte : une seule chaîne multi-paragraphes).
    print()
    lua.execute(r"""
        AscensionFR.DB.Sorts[801441] = {
            N = "Libram de consécration",
            R = "Rang 1",
            D = "Lisez votre |cffffffffLibram de Consécration|r, ce qui permet aux capacités de dégâts d'infliger ${$804148m1+$804148ppl1} dégâts du Sacré supplémentaires à votre cible pendant $d.\r\n\r\n@ext:Un seul sort |cffffffffLibram|r peut être actif à la fois.:ext@",
            DE = "Read from your |cffffffffLibram of Consecration|r, causing damaging abilities to deal an ${$804148m1+$804148ppl1} additional Holy damage to your target for $d.\r\n\r\n@ext:Only 1 |cffffffffLibram|r spell can be active at a time.:ext@",
        }
        LIGNES = {
            FS("Libram de consécration"),
            FS("Instantané"),
            FS("Read from your |cffffffffLibram of Consecration|r, causing damaging abilities to deal an 20 additional Holy damage to your target for 20 sec.\r\n\r\nOnly 1 |cffffffffLibram|r spell can be active at a time."),
        }
        for i, l in ipairs(LIGNES) do _G["GameTooltipTextLeft" .. i] = l end
        function GameTooltip:NumLines() return #LIGNES end
        RESULTAT2 = AscensionFR.TraduireInfobulleSort(GameTooltip, 801441)
    """)
    lignes = lua.globals().LIGNES
    verifier("marqueurs @ext retirés, valeurs 20 / 20 sec replacées",
             lignes[3].GetText(lignes[3]),
             "Lisez votre |cffffffffLibram de Consécration|r, ce qui permet "
             "aux capacités de dégâts d'infliger 20 dégâts du Sacré "
             "supplémentaires à votre cible pendant 20 sec.\r\n\r\n"
             "Un seul sort |cffffffffLibram|r peut être actif à la fois.")

    # --- Bloc @ext REPLIÉ : MAJ non enfoncée (signalement de Dan, 17/07) ---
    # Le client remplace alors le contenu du bloc par l'indice
    # « Hold SHIFT for more information » : le modèle porte le contenu,
    # l'écran porte l'indice, rien ne s'alignait. L'addon doit traduire la
    # version repliée et franciser l'indice. Ligne affichée = la capture
    # exacte du signalement.
    print()
    lua.execute(r"""
        LIGNES = {
            FS("Libram de consécration"),
            FS("Instantané"),
            FS("Read from your |cffffffffLibram of Consecration|r, causing damaging abilities to deal an 20 additional Holy damage to your target for 20 sec.\n\n|cff00DDFFHold SHIFT for more information|r"),
        }
        for i, l in ipairs(LIGNES) do _G["GameTooltipTextLeft" .. i] = l end
        function GameTooltip:NumLines() return #LIGNES end
        RESULTAT2B = AscensionFR.TraduireInfobulleSort(GameTooltip, 801441)
    """)
    lignes = lua.globals().LIGNES
    verifier("bloc @ext replié (MAJ non enfoncée) traduit",
             lignes[3].GetText(lignes[3]),
             "Lisez votre |cffffffffLibram de Consécration|r, ce qui permet "
             "aux capacités de dégâts d'infliger 20 dégâts du Sacré "
             "supplémentaires à votre cible pendant 20 sec.\n\n"
             "|cff00DDFFMaintenez MAJ pour plus d'informations|r")

    # --- Marquage @s:id:0@ : bloc inséré par le client, absorbé tel quel ---
    #
    # ÉCART CONNU ET ASSUMÉ (26/07/2026) — CETTE ASSERTION ÉCHOUE EXPRÈS.
    # Le bloc inséré par le client porte « |cffFFFFFFRighteous Tempest|r » ;
    # l'addon le restitue dénudé, « Righteous Tempest ». Coupable identifié :
    # retirer_couleurs (Modules/Sorts.lua:79), qui retire les codes couleur
    # des DEUX côtés avant d'aligner parce que le client d'Ascension ne les
    # affiche pas toujours sur ses sorts custom. Ce dénudage est une décision,
    # pas un bug : c'est lui qui a débloqué 3 646 sorts (affaire du « Libram
    # de consécration »), et le bloc absorbé en fait les frais.
    # NE PAS relâcher l'attente pour repeindre le banc en vert : elle décrit
    # le résultat VOULU et repassera au vert d'elle-même le jour où
    # l'alignement saura restituer les couleurs du bloc absorbé.
    # Seuil de lecture : 1 échec = normal, 2 échecs = régression.
    print()
    lua.execute(r"""
        BLOC = "|TInterface\\Common\\ui-tooltipdivider:12:180:0:0|t\n|TInterface\\Icons\\X:20:20:0:0|t |cffFFFFFFRighteous Tempest|r\nDeals Weapon Damage plus 25."
        AscensionFR.DB.Sorts[525045] = {
            N = "Tempête juste",
            D = "Transforme votre |cffffffffHoly Cleave|r en |cffffffffRighteous Tempest|r.@s:805409:0@",
            DE = "Transforms your |cffffffffHoly Cleave|r into |cffffffffRighteous Tempest|r.@s:805409:0@",
        }
        LIGNES = {
            FS("Tempête juste"),
            FS("Transforms your |cffffffffHoly Cleave|r into |cffffffffRighteous Tempest|r." .. BLOC),
        }
        for i, l in ipairs(LIGNES) do _G["GameTooltipTextLeft" .. i] = l end
        function GameTooltip:NumLines() return #LIGNES end
        RESULTAT3 = AscensionFR.TraduireInfobulleSort(GameTooltip, 525045)
        ATTENDU3 = "Transforme votre |cffffffffHoly Cleave|r en |cffffffffRighteous Tempest|r." .. BLOC
    """)
    lignes = lua.globals().LIGNES
    verifier("bloc inséré par @s: absorbé et conservé",
             lignes[2].GetText(lignes[2]), lua.globals().ATTENDU3)

    # --- Quêtes : pas de GetQuestID sur ce client ------------------------
    print()
    lua.execute("AscensionFR.DB.Quetes[500005] = "
                "{ TE = 'Timber for the Coldhewn', T = 'Bois pour le Coldhewn',"
                "  D = 'Abattez les arbres.' }")
    try:
        with open(ADDON + "\\Modules\\Quetes.lua", encoding="utf-8") as fh:
            lua.execute(fh.read())
        lua.execute("""
            QuestInfoTitleText = FS("Timber for the Coldhewn")
            QuestInfoDescriptionText = FS("Chop down trees.")
            QuestLogFrame, QuestFrame = nil, nil
            -- Le PNJ propose la quête : c'est là que GetQuestID() plantait.
            _EVT(nil, "QUEST_DETAIL")
        """)
    except Exception as e:
        print("  ECHEC   le module Quêtes plante sans GetQuestID : %s"
              % str(e)[:100])
        echecs += 1
    else:
        titre = lua.globals().QuestInfoTitleText
        desc = lua.globals().QuestInfoDescriptionText
        verifier("titre traduit sans GetQuestID (retrouvé par le titre)",
                 titre.GetText(titre), "Bois pour le Coldhewn")
        verifier("description traduite", desc.GetText(desc),
                 "Abattez les arbres.")

    print()
    print("%d échec(s)" % echecs)
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
