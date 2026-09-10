# -*- coding: utf-8 -*-
"""
Info-bulles d'objets : lignes d'effet, compétences requises, lignes du client.

Cas réels rapportés par Dan (captures du 16/07) :
  - « Bandage épais en lin » : la ligne verte « Utiliser : Heals 114 damage
    over 6 sec. » est la description du sort attaché à l'objet, résolue par
    le client — nos bases d'objets ne couvraient que noms et ambiance.
    Et « First Aid (20) requis » : la structure est francisée par les
    GlobalStrings mais le nom de compétence vient des DBC (DB_Libelles).
  - « Livre des artisans » : l'info-bulle répète le texte du sort d'invocation
    (sans préfixe) et ajoute « You don't own this vanity item », une chaîne du
    client compilé d'Ascension, introuvable dans les GlobalStrings.
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
JOUEUR = false
function UnitIsPlayer() return JOUEUR end
function UnitExists() return false end
function UnitGUID() return nil end
function hooksecurefunc() end
function print() end
SlashCmdList = {}
function GetTime() return 0 end
ITEM_SPELL_TRIGGER_ONUSE = "Utiliser :"
ITEM_SPELL_TRIGGER_ONEQUIP = "Équipé :"
ITEM_SPELL_TRIGGER_ONPROC = "Chances quand vous touchez :"

function CreateFrame()
    local f = { _s = {} }
    function f:RegisterEvent() end
    function f:SetScript(k, fn) self._s[k] = fn end
    function f:GetScript(k) return self._s[k] end
    function f:HookScript() end
    function f:IsProtected() return false, false end
    return f
end

local function FS(t)
    local f = { _t = t }
    function f:GetText() return self._t end
    function f:SetText(v) self._t = v end
    function f:GetObjectType() return "FontString" end
    function f:IsShown() return true end
    return f
end
_G.FS = FS

-- L'info-bulle : HookScript retient les gestionnaires pour que le test les
-- déclenche lui-même, comme le jeu le ferait.
_HOOKS = {}
GameTooltip = {}
function GameTooltip:GetName() return "GameTooltip" end
function GameTooltip:HookScript(evt, fn) _HOOKS[evt] = fn end
function GameTooltip:NumLines() return #LIGNES end
-- L'addon demande l'ÉTAT de l'info-bulle avant de la redessiner
-- (Tooltips.lua:555 : « if tooltip:IsShown() then tooltip:Show() end »). Sans
-- ce stub le banc mourait sur « attempt to call method 'IsShown' (a nil
-- value) » au premier survol, AVANT la première assertion. Ce que ça donnait,
-- remesuré le 27/07/2026 en retirant ce seul stub d'une copie : traceback
-- lupa, 0 assertion jouée, CODE RETOUR 1 — un rouge bruyant, pas un faux vert
-- (le dépôt le dit déjà : rapports/bancs_essai.txt:342, « verifier_objets.py
-- -> ROUGE (code 1) »). Les 18 vérifications d'aujourd'hui n'étaient pas
-- muettes : elles n'existaient pas. Même stub que verifier_signalements.py:64.
function GameTooltip:IsShown() return #LIGNES > 0 end
function GameTooltip:Show() end
function GameTooltip:GetItem() return LIGNES[1]:GetText(), _LIEN end
function GameTooltip:GetUnit() return LIGNES[1]:GetText(), "mouseover" end
"""


def preparer():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute("LIGNES = {}")
    lua.execute(CONTEXTE)
    lua.execute("AscensionFR = { DB = { Sorts = {}, Quetes = {}, Objets = {},"
                " Creatures = {}, Libelles = {} } }")
    for f in ["Core.lua", "Modules\\Recolte.lua", "Modules\\Sorts.lua",
              "Modules\\Tooltips.lua"]:
        with open(ADDON + "\\" + f, encoding="utf-8") as fh:
            lua.execute(fh.read())
    return lua


def afficher_tooltip(lua, item_id, lignes):
    """Peuple l'info-bulle et déclenche le gestionnaire OnTooltipSetItem."""
    lua.execute("LIGNES = {}")
    table = lua.globals().LIGNES
    fs = lua.globals().FS
    for i, texte in enumerate(lignes):
        table[i + 1] = fs(texte)
        lua.globals()["GameTooltipTextLeft%d" % (i + 1)] = table[i + 1]
    lua.execute('_LIEN = "item:%d"' % item_id)
    lua.execute('_HOOKS["OnTooltipSetItem"](GameTooltip)')
    return [table[i + 1].GetText(table[i + 1]) for i in range(len(lignes))]


def main():
    lua = preparer()
    lua.execute(r"""
        local DB = AscensionFR.DB
        DB.Libelles["First Aid"] = "Secourisme"

        DB.Objets[21991] = { N = "Bandage épais en lin", S = {"18610"} }
        DB.Sorts[18610] = {
            D = "Rend $o1 points de vie en $d.",
            DE = "Heals $o1 damage over $d.",
        }

        DB.Objets[750750] = { N = "Livre des artisans", S = {"90000"} }
        DB.Sorts[90000] = {
            D = "Clic droit pour invoquer et renvoyer votre guide personnel de l'Ascension.",
            DE = "Right Click to summon and dismiss your personal guide of Ascension.",
        }
    """)

    echecs = 0

    def verifier(description, obtenu, attendu):
        nonlocal echecs
        if obtenu == attendu:
            print("  ok      %-52s %s" % (description, obtenu))
        else:
            print("  ECHEC   %s\n          obtenu %r\n          attendu %r"
                  % (description, obtenu, attendu))
            echecs += 1

    # --- Bandage : ligne d'effet + compétence requise + stats intactes ----
    resultat = afficher_tooltip(lua, 21991, [
        "Heavy Linen Bandage",
        "First Aid (20) requis",
        "Utiliser : Heals 114 damage over 6 sec.",
        "+5 Stamina",
    ])
    verifier("nom de l'objet", resultat[0], "Bandage épais en lin")
    verifier("compétence requise traduite", resultat[1],
             "Secourisme (20) requis")
    verifier("ligne d'effet alignée et résolue", resultat[2],
             "Utiliser : Rend 114 points de vie en 6 sec.")
    verifier("ligne de stats -> intacte", resultat[3], "+5 Stamina")

    # --- Livre des artisans : texte de sort sans préfixe + ligne client ---
    print()
    resultat = afficher_tooltip(lua, 750750, [
        "Artisan's Book",
        "Right Click to summon and dismiss your personal guide of Ascension.",
        "You don't own this vanity item",
    ])
    verifier("nom de l'objet", resultat[0], "Livre des artisans")
    verifier("texte de sort sans préfixe traduit", resultat[1],
             "Clic droit pour invoquer et renvoyer votre guide personnel "
             "de l'Ascension.")
    verifier("ligne du client compilé traduite", resultat[2],
             "Vous ne possédez pas cet objet d'apparat")

    # --- Parchemin : suffixe de recharge collé par le client --------------
    # « Utiliser : Increases movement speed... (1 sec de recharge) » : le
    # suffixe n'est pas dans le modèle du sort, il doit être détaché avant
    # l'alignement puis restitué.
    print()
    lua.execute(r"""
        AscensionFR.DB.Objets[2200029] = {
            N = "Parchemin du Gardien lié : Ghost Runner", S = {"91000"} }
        AscensionFR.DB.Sorts[91000] = {
            D = "Augmente la vitesse de déplacement quand vous êtes mort dans cette zone de $s1% !",
            DE = "Increases movement speed while dead in this zone by $s1%!",
        }
    """)
    resultat = afficher_tooltip(lua, 2200029, [
        "Soulbound Keeper's Scroll: Ghost Runner",
        "Utiliser : Increases movement speed while dead in this zone "
        "by 100%! (1 sec de recharge)",
    ])
    verifier("suffixe de recharge détaché puis restitué", resultat[1],
             "Utiliser : Augmente la vitesse de déplacement quand vous êtes "
             "mort dans cette zone de 100% ! (1 sec de recharge)")

    # --- Sort sans variable : seule LA ligne égale au modèle est traduite --
    # La hache de Dan (17/07) : un sort d'effet au texte constant faisait
    # remplacer CHAQUE ligne longue de l'info-bulle par la même phrase.
    print()
    lua.execute(r"""
        AscensionFR.DB.Objets[880001] = {
            N = "Hache de pierre brisée", S = {"95000"} }
        AscensionFR.DB.Sorts[95000] = {
            D = "Augmente la puissance PvE de 48.",
            DE = "Increases PvE Power by 48.",
        }
    """)
    resultat = afficher_tooltip(lua, 880001, [
        "Broken Stone Axe",
        "Binds when picked up",
        "Increases PvE Power by 48.",
        "Équipé : Increases PvE Power by 48.",
        "Disenchant into goodies x1",
    ])
    verifier("ligne égale au modèle -> traduite", resultat[2],
             "Augmente la puissance PvE de 48.")
    verifier("ligne préfixée égale -> traduite", resultat[3],
             "Équipé : Augmente la puissance PvE de 48.")
    verifier("ligne étrangère (liaison) -> intacte", resultat[1],
             "Binds when picked up")
    verifier("ligne étrangère (désenchantement) -> intacte", resultat[4],
             "Disenchant into goodies x1")

    # --- Objet sans sorts attachés : rien ne casse ------------------------
    print()
    lua.execute('AscensionFR.DB.Objets[999] = { N = "Caillou" }')
    resultat = afficher_tooltip(lua, 999, ["Pebble", "Junk line"])
    verifier("objet sans champ S -> nom seul", resultat[0], "Caillou")
    verifier("autres lignes intactes", resultat[1], "Junk line")

    # --- Info-bulle d'un joueur : race et classe ---------------------------
    # Le client compose « Nain Templar de niveau 20 » lui-même : la phrase est
    # française (GlobalStrings) mais race et classe sortent de ses DBC. On les
    # remplace à l'affichage, en les demandant au jeu plutôt qu'en devinant
    # où ils se trouvent dans la ligne.
    print()
    lua.execute(r"""
        JOUEUR = true
        AscensionFR.DB.Libelles["Dwarf"] = "Nain"
        AscensionFR.DB.Libelles["Templar"] = "Templier"
        AscensionFR.DB.Libelles["Death Knight"] = "Chevalier de la mort"
    """)

    def survol_joueur(lignes):
        lua.execute("LIGNES = {}")
        table = lua.globals().LIGNES
        fs = lua.globals().FS
        for i, texte in enumerate(lignes):
            table[i + 1] = fs(texte)
            lua.globals()["GameTooltipTextLeft%d" % (i + 1)] = table[i + 1]
        lua.execute('_HOOKS["OnTooltipSetUnit"](GameTooltip)')
        return [table[i + 1].GetText(table[i + 1]) for i in range(len(lignes))]

    resultat = survol_joueur(["<joueur>", "Nain Templar de niveau 20"])
    verifier("classe traduite dans l'info-bulle joueur", resultat[1],
             "Nain Templier de niveau 20")

    resultat = survol_joueur(["<joueur>", "Level 20 Dwarf Templar"])
    verifier("race et classe traduites (phrase anglaise)", resultat[1],
             "Level 20 Nain Templier")

    verifier("nom du joueur -> intact", resultat[0], "<joueur>")

    # Un nom de classe à espace ou tiret contient des caractères magiques des
    # motifs Lua : la découpe de chaîne s'en moque, gsub aurait échoué.
    lua.execute('function UnitClass() return "Death Knight" end')
    resultat = survol_joueur(["Autre", "Nain Death Knight de niveau 20"])
    verifier("classe à deux mots traduite", resultat[1],
             "Nain Chevalier de la mort de niveau 20")

    lua.execute("JOUEUR = false")

    print()
    print("%d échec(s)" % echecs)
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
