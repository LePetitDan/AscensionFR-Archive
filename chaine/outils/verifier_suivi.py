# -*- coding: utf-8 -*-
"""
Test du suivi en jeu (Modules\\Recolte.lua).

Le jeu n'écrit ses données qu'au /reload ou à la déconnexion, et rien ne
permet de prévenir une partie en cours qu'une traduction est prête. Le seul
moment où l'addon peut parler, c'est au chargement. On vérifie donc les deux
bouts du cycle :

  1. après un /reload qui a apporté des traductions -> « +N nouvelles » ;
  2. quand le joueur croise beaucoup d'anglais -> proposer un /reload ;
     mais jamais en dessous du seuil, et jamais deux fois de suite.
"""
import sys

import lupa.lua51 as lupa_mod

ADDON = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns\AscensionFR"

CONTEXTE = r"""
MESSAGES = {}
function print(...)
    local n = select("#", ...)
    local bouts = {}
    for i = 1, n do bouts[i] = tostring((select(i, ...))) end
    table.insert(MESSAGES, table.concat(bouts, " "))
end
function strtrim(s) return (string.gsub(s or "", "^%s*(.-)%s*$", "%1")) end
function UnitName() return "<joueur>" end
function UnitClass() return "Templar" end
function UnitRace() return "Dwarf" end
function UnitSex() return 2 end
function hooksecurefunc() end
SlashCmdList = {}

TEMPS = 0
function GetTime() return TEMPS end

-- Le jeu sert un événement à TOUS les cadres qui l'ont enregistré. On garde
-- donc une LISTE, pas un seul gestionnaire.
--
-- L'ancienne version n'en gardait qu'un — le DERNIER posé. Recolte.lua en a
-- trois aujourd'hui (annonce de connexion, nettoyage, contrôle de version) :
-- le banc appelait donc le contrôle de version en croyant appeler l'annonce,
-- et hurlait « rien n'est annoncé » sur du code parfaitement sain. Un banc qui
-- crie au loup ne sert plus à rien le jour où il a raison.
_GESTIONNAIRES, _TICKS = {}, {}
function CreateFrame()
    local f = { _evts = {} }
    function f:RegisterEvent(e) self._evts[e] = true end
    function f:SetScript(quoi, fn)
        if quoi == "OnEvent" then
            table.insert(_GESTIONNAIRES, { cadre = self, fn = fn })
        elseif quoi == "OnUpdate" then
            table.insert(_TICKS, fn)
        end
    end
    function f:HookScript() end
    function f:Show() end
    function f:Hide() end
    return f
end

-- Sert l'événement à tous les cadres qui l'ont enregistré, comme le jeu.
function _LOGIN(_, evenement, ...)
    for _, g in ipairs(_GESTIONNAIRES) do
        if g.cadre._evts[evenement] then g.fn(g.cadre, evenement, ...) end
    end
end

function _TICK(_, delta)
    for _, fn in ipairs(_TICKS) do fn(nil, delta) end
end
"""


def messages(lua):
    m = lua.globals().MESSAGES
    return [m[i] for i in range(1, len(m) + 1)]


def contient(msgs, bout):
    return any(bout in m for m in msgs)


def charger(lua):
    for f in ["Core.lua", "Modules\\Recolte.lua"]:
        with open(ADDON + "\\" + f, encoding="utf-8") as fh:
            lua.execute(fh.read())


def main():
    echecs = 0

    # --- 1. Première connexion : pas de « +N », rien à comparer -----------
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)
    charger(lua)
    lua.execute("""
        AscensionFRSaved = {}
        for i = 1, 100 do AscensionFR.DB.Quetes[i] = { T = "x" } end
        _LOGIN(nil, "PLAYER_LOGIN")
    """)
    m = messages(lua)
    if contient(m, "nouvelles traductions"):
        print("  ECHEC   première connexion : annonce des nouveautés à tort")
        echecs += 1
    else:
        print("  ok      première connexion : pas de fausse annonce")
    if contient(m, "100 traductions"):
        print("  ok      total annoncé au chargement")
    else:
        print("  ECHEC   total non annoncé : %r" % m)
        echecs += 1

    # --- 2. Le compagnon a traduit : le /reload suivant l'annonce ---------
    # ComptageExact déjà posé : on teste le régime NORMAL, après la bascule
    # unique vers le comptage exact (voir test 2 bis).
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)
    charger(lua)
    lua.execute("""
        -- Session précédente : 100 traductions, des textes en attente
        AscensionFRSaved = { DernierTotal = 100, ComptageExact = true,
                             Recolte = { Divers = { ["a"] = true } } }
        for i = 1, 492 do AscensionFR.DB.Quetes[i] = { T = "x" } end
        _LOGIN(nil, "PLAYER_LOGIN")
        RESTE_RECOLTE = AscensionFRSaved.Recolte.Divers
    """)
    m = messages(lua)
    if contient(m, "+392 nouvelles traductions"):
        print("  ok      « +392 nouvelles traductions » après le /reload")
    else:
        print("  ECHEC   nouveautés non annoncées : %r" % m)
        echecs += 1
    if lua.globals().RESTE_RECOLTE is None:
        print("  ok      récolte purgée : ces textes viennent d'être traduits")
    else:
        print("  ECHEC   la récolte n'a pas été purgée")
        echecs += 1

    # --- 2 bis. La BASCULE vers le comptage exact (24/07) ----------------
    # Premier login après la mise à jour : le total passe d'un décompte
    # partiel (pairs()) au nombre exact gravé — un saut ENORME qui n'est PAS
    # de nouvelles traductions. On doit l'absorber en SILENCE, SANS purger la
    # récolte (sinon on perd les contributions en attente).
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)
    charger(lua)
    lua.execute("""
        -- Ancienne session : DernierTotal partiel, PAS de ComptageExact,
        -- et des contributions en attente.
        AscensionFRSaved = { DernierTotal = 100,
                             Recolte = { Divers = { ["a"] = true } } }
        AscensionFR.TotalTextes = 1256774   -- la constante gravée
        _LOGIN(nil, "PLAYER_LOGIN")
        BASCULE_RESTE = AscensionFRSaved.Recolte.Divers
        BASCULE_MARQUE = AscensionFRSaved.ComptageExact
        BASCULE_TOTAL = AscensionFRSaved.DernierTotal
    """)
    m = messages(lua)
    if not contient(m, "nouvelles traductions"):
        print("  ok      bascule : aucune fausse annonce de +770k")
    else:
        print("  ECHEC   bascule : fausse annonce -> %r" % m)
        echecs += 1
    if lua.globals().BASCULE_RESTE is not None:
        print("  ok      bascule : récolte PRÉSERVÉE (contributions gardées)")
    else:
        print("  ECHEC   bascule : la récolte a été purgée à tort")
        echecs += 1
    if lua.globals().BASCULE_MARQUE and lua.globals().BASCULE_TOTAL == 1256774:
        print("  ok      bascule : total aligné sur le nombre exact, marqué")
    else:
        print("  ECHEC   bascule : total/marque non alignés")
        echecs += 1

    # --- 3. Le rappel « /reload » : seuil et anti-harcèlement -------------
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)
    charger(lua)
    lua.execute("""
        AscensionFRSaved = { DernierTotal = 0 }
        _LOGIN(nil, "PLAYER_LOGIN")
        MESSAGES = {}
        -- Sous le seuil : on ne dit rien
        for i = 1, 5 do AscensionFR.Recolter("Divers", "texte inconnu " .. i, true) end
        TEMPS = 1000
        _TICK(nil, 30)
    """)
    if not contient(messages(lua), "/reload"):
        print("  ok      5 textes inconnus : aucun rappel (sous le seuil)")
    else:
        print("  ECHEC   rappel envoyé sous le seuil")
        echecs += 1

    lua.execute("""
        -- Au-dessus du seuil : on propose le /reload, une seule fois
        for i = 6, 40 do AscensionFR.Recolter("Divers", "texte inconnu " .. i, true) end
        TEMPS = 2000
        _TICK(nil, 30)
        PREMIER = #MESSAGES
        TEMPS = 2060      -- 1 min plus tard : trop tôt pour réinsister
        _TICK(nil, 30)
        SECOND = #MESSAGES
    """)
    m = messages(lua)
    # Formulation actuelle du rappel. Si elle change encore, c'est ICI qu'on
    # la remet à jour — pas en ignorant l'échec.
    if contient(m, "40 textes croisés encore sans traduction"):
        print("  ok      40 textes inconnus : rappel proposé")
    else:
        print("  ECHEC   rappel non proposé : %r" % m[-2:])
        echecs += 1
    if lua.globals().PREMIER == lua.globals().SECOND:
        print("  ok      pas de rappel répété une minute après")
    else:
        print("  ECHEC   le rappel se répète trop vite")
        echecs += 1

    print()
    print("%d échec(s)" % echecs)
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
