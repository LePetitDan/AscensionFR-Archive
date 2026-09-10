# -*- coding: utf-8 -*-
"""
Banc du canal français (Modules\\CanalFrancais.lua).

⚠️ Malgré son nom, ce banc ne couvre PAS le « canal moteur » (les globales
de combat DODGE/PARRY… écrites par InterfaceUI.AppliquerCanalMoteur) : ce
circuit-là est couvert par verifier_interface.py, section A (bloc 3,
28/07/2026). Ici, « canal » = le canal de DISCUSSION AscensionFR.

On simule les API de canal du jeu (JoinPermanentChannel, GetChannelName,
LeaveChannelByName) et on vérifie la LOGIQUE :
  - rejoint quand il faut, une seule fois ;
  - ne rejoint pas si le joueur a coupé (sansCanalFrancais) ;
  - ne rejoint pas s'il est déjà dedans ;
  - /afrcanal off pose la clé et quitte ; /afrcanal on l'enlève et rejoint.

Usage : python outils/verifier_canal.py
"""
import io
import os
import sys

import lupa.lua51 as lupa_mod

ADDON = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns\AscensionFR"

CONTEXTE = r"""
AscensionFR = {}
function AscensionFR.Actif() return true end
AscensionFRSaved = { Options = {} }
SlashCmdList = {}
DEFAULT_CHAT_FRAME = { GetID = function() return 1 end }
ChatFrame1 = DEFAULT_CHAT_FRAME
function print() end

-- État simulé des canaux.
CANAUX = {}                       -- nom -> true si on est dedans
JOINTS = 0                        -- combien de fois on a appelé Join

function JoinPermanentChannel(nom, mdp, cadre, v)
    JOINTS = JOINTS + 1
    CANAUX[nom] = true
    return 1, nom
end
function GetChannelName(nom)
    if type(nom) == "string" and CANAUX[nom] then return 1 end
    return 0
end
function LeaveChannelByName(nom) CANAUX[nom] = nil end
function ChatFrame_AddChannel() end
function ChatFrame_RemoveChannel() end
function ChangeChatColor() end
function UnitName() return "<joueur>" end
function GetNumChannelMembers() return 7 end
-- GetColoredName du jeu : pour un canal, rend le nom brut (arg2 = auteur).
function GetColoredName(event, arg1, arg2) return arg2 end
FILTRES = {}
function ChatFrame_AddMessageEventFilter(evt, fn) FILTRES[evt] = fn end
ENVOYES = {}
function SendChatMessage(msg, typ, lang, cible)
    table.insert(ENVOYES, msg)
end

-- Capture du OnUpdate du minuteur pour le déclencher à la demande.
TICS = {}
local vraiCreateFrame_evts = {}
function CreateFrame()
    local f = { _evts = {} }
    function f:RegisterEvent(e) self._evts[e] = true end
    function f:SetScript(quoi, fn)
        if quoi == "OnUpdate" then self._onupdate = fn
        elseif quoi == "OnEvent" then self._onevent = fn end
    end
    function f:GetScript(quoi)
        if quoi == "OnUpdate" then return self._onupdate end
    end
    table.insert(TICS, f)
    return f
end

-- Rejoue : entrée en jeu -> attendre -> le minuteur rejoint.
function ENTRER_EN_JEU()
    for _, f in ipairs(TICS) do
        if f._onevent and f._evts["PLAYER_ENTERING_WORLD"] then
            f._onevent(f, "PLAYER_ENTERING_WORLD")
        end
    end
    -- 7 secondes s'écoulent -> le minuteur (délai 6 s) se déclenche.
    for _, f in ipairs(TICS) do
        if f._onupdate then f._onupdate(f, 7) end
    end
end
"""


def charger():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)
    with io.open(os.path.join(ADDON, "Modules\\CanalFrancais.lua"),
                 encoding="utf-8") as f:
        lua.execute(f.read())
    return lua


echecs = 0


def verifier(desc, obtenu, attendu):
    global echecs
    if obtenu == attendu:
        print("  ok      %-46s %s" % (desc, obtenu))
    else:
        print("  ECHEC   %-46s obtenu %r, attendu %r"
              % (desc, obtenu, attendu))
        echecs += 1


# 1. Cas normal : on rejoint une fois.
lua = charger()
lua.globals().ENTRER_EN_JEU()
verifier("rejoint le canal", lua.globals().CANAUX["AscensionFR"], True)
verifier("un seul JoinPermanentChannel", lua.globals().JOINTS, 1)

# 2. Deuxième entrée en jeu : déjà dedans -> pas de re-join.
lua.globals().ENTRER_EN_JEU()
verifier("pas de double join (déjà dedans)", lua.globals().JOINTS, 1)

# 3. Coupe-circuit : on ne rejoint pas.
lua = charger()
lua.execute("AscensionFRSaved.Options.sansCanalFrancais = true")
lua.globals().ENTRER_EN_JEU()
verifier("coupé : ne rejoint pas", lua.globals().JOINTS, 0)

# 4. /afrcanal off pose la clé et quitte ; on l'a d'abord rejoint.
lua = charger()
lua.globals().ENTRER_EN_JEU()
lua.execute('SlashCmdList["AFRCANAL"]("off")')
verifier("/afrcanal off : clé posée",
         bool(lua.globals().AscensionFRSaved.Options.sansCanalFrancais), True)
verifier("/afrcanal off : quitté", lua.globals().CANAUX["AscensionFR"], None)

# 5. /afrcanal on : enlève la clé et rejoint.
lua.execute('SlashCmdList["AFRCANAL"]("on")')
verifier("/afrcanal on : clé enlevée",
         lua.globals().AscensionFRSaved.Options.sansCanalFrancais, None)
verifier("/afrcanal on : rejoint", lua.globals().CANAUX["AscensionFR"], True)

# 6. Coloration des pseudos via GetColoredName (le nom AFFICHÉ, lien intact).
lua = charger()
lua.globals().ENTRER_EN_JEU()
lua.execute("""
    -- GetColoredName(event, arg1=msg, arg2=auteur, ... arg9=nom du canal)
    MOI = GetColoredName("CHAT_MSG_CHANNEL", "salut", "<joueur>",
                         "", "1. AscensionFR", "", "", 0, 1, "AscensionFR")
    AUTRE = GetColoredName("CHAT_MSG_CHANNEL", "hi", "Bob",
                           "", "1. AscensionFR", "", "", 0, 1, "AscensionFR")
    HORS = GetColoredName("CHAT_MSG_CHANNEL", "hi", "Bob",
                          "", "2. General", "", "", 0, 2, "General")
    AUTRE_EVT = GetColoredName("CHAT_MSG_GUILD", "hi", "Bob")
""")
g = lua.globals()
verifier("mon pseudo affiché en rouge", "ff5555" in (g.MOI or ""), True)
verifier("mon nom reste dans le texte (pas cassé)",
         "<joueur>" in (g.MOI or ""), True)
verifier("autre pseudo en bleu comu", "66ccff" in (g.AUTRE or ""), True)
verifier("hors de notre canal : nom brut", g.HORS, "Bob")
verifier("autre événement : nom brut", g.AUTRE_EVT, "Bob")

# 7. /afrgroupe poste dans le canal.
lua.execute('SlashCmdList["AFRGROUPE"]("cherche 2 dps")')
envoyes = g.ENVOYES
verifier("/afrgroupe a posté un message",
         any("cherche 2 dps" in (envoyes[i] or "")
             for i in range(1, len(envoyes) + 1)), True)

# 8. /afrcanal qui compte les francophones.
lua.execute('N_QUI = AscensionFR.CanalFrancais.compter()')
verifier("le compteur rend un nombre", g.N_QUI, 7)

print("")
print("%d échec(s)" % echecs)
sys.exit(1 if echecs else 0)
