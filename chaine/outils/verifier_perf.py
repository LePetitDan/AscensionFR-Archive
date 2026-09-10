# -*- coding: utf-8 -*-
"""
Banc de l'instrument de mesure (Modules/Perf.lua, programme 10, 01/08/2026).

UN INSTRUMENT QU'ON NE VÉRIFIE PAS NE MESURE QUE LUI-MÊME. Ce banc contrôle
les quatre promesses de Perf.lua, dans l'ordre où elles peuvent nous trahir :

  1. ATTRIBUTION. Le cadre de Plaques.lua est reconnu comme étant le sien,
     alors qu'on n'a pas le droit de modifier ce fichier. C'est le mécanisme
     d'encadrement (jalon en fin de BarresDeVie.lua, jalon en tête de
     Metiers.lua) : s'il se trompe, tout le relevé désigne le mauvais coupable.

  2. MOYENNE *ET* PIRE. Un tic exceptionnellement long doit ressortir au pire
     sans noyer la moyenne : c'est toute la différence entre les deux pannes
     qu'on cherche à distinguer (un coût par image, ou un à-coup périodique).

  3. PAS D'EMPILEMENT. L'enrobage se rafraîchit chaque seconde. S'il enrobait
     son propre enrobage, une couche s'ajouterait par seconde et le relevé
     enflerait tout seul — l'instrument mesurerait sa propre mesure. Ce défaut
     a existé : il est ici tenu par une assertion qui le rattraperait.

  4. ÉTEINTE, LA MESURE EST ABSENTE. Pas « présente mais inactive » : le
     gestionnaire d'origine doit être remis À L'IDENTIQUE (comparaison de
     fonctions, pas d'apparence), et l'échantillonneur ne doit plus avoir de
     script du tout. C'est la promesse la plus facile à casser sans s'en
     apercevoir, et la seule qui concerne TOUS les joueurs — y compris ceux
     qui ne mesureront jamais rien.

Le chronomètre du jeu est remplacé par une HORLOGE TRUQUÉE qui avance d'un pas
fixe à chaque lecture. L'enrobage la lit deux fois par tic : chaque tic vaut
donc exactement un pas, et les assertions deviennent des égalités franches.
C'est la seule façon honnête de tester un chronomètre.

Usage : python outils/verifier_perf.py
"""
import io
import locale
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

locale.setlocale(locale.LC_ALL, "C")

import lupa.lua51 as lupa_mod  # noqa: E402

ADDON = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
         r"\AscensionFR")

CONTEXTE = r"""
_PAS = 1                       -- ms ajoutées à chaque lecture de l'horloge
_HORLOGE = 0
function debugprofilestop()
    _HORLOGE = _HORLOGE + _PAS
    return _HORLOGE
end

function strtrim(s) return (string.gsub(s or "", "^%s*(.-)%s*$", "%1")) end
function print() end
function hooksecurefunc() end
function IsAddOnLoaded() return false end
function ChatFrame_AddMessageEventFilter() end
function UnitName() return "Testeur" end
function UnitClass() return "Templar" end
function UnitRace() return "Dwarf" end
function UnitSex() return 2 end
function GetTime() return 0 end
function GetFramerate() return 60 end
function InCombatLockdown() return false end
function GetRealZoneText() return "Hurlevent" end
function GetSubZoneText() return "Vieille ville" end
function GetNumRaidMembers() return 0 end
function GetNumPartyMembers() return 0 end
function UpdateAddOnMemoryUsage() end
function GetAddOnMemoryUsage() return 1024 end
function wipe(t) for k in pairs(t) do t[k] = nil end return t end
LibStub = nil
GameTooltip = { HookScript = function() end,
                GetName = function() return "GT" end }
SlashCmdList = {}
UISpecialFrames = {}

-- Des cadres qui savent poser et rendre un script, et qui s'inscrivent dans
-- une liste : c'est elle que parcourt EnumerateFrames, et c'est par elle que
-- l'encadrement retrouve le cadre de Plaques.
_CADRES = {}

function CreateFrame()
    local c = { _scripts = {} }
    function c:SetScript(quoi, f) self._scripts[quoi] = f end
    function c:GetScript(quoi) return self._scripts[quoi] end
    function c:HookScript() end
    function c:RegisterEvent() end
    function c:UnregisterEvent() end
    function c:Show() end
    function c:Hide() end
    function c:GetNumChildren() return 0 end
    function c:GetChildren() end
    function c:IsShown() return true end
    _CADRES[#_CADRES + 1] = c
    return c
end

function EnumerateFrames(precedent)
    if precedent == nil then return _CADRES[1] end
    for i = 1, #_CADRES do
        if _CADRES[i] == precedent then return _CADRES[i + 1] end
    end
    return nil
end

WorldFrame = CreateFrame()
"""

# Ce que Plaques.lua réclame en plus pour se charger sans mourir.
CONTEXTE_PLAQUES = r"""
AscensionFR.DB.Zones = AscensionFR.DB.Zones or {}
AscensionFR.DB.ObjetsNoms = AscensionFR.DB.ObjetsNoms or {}
AscensionFR.DB.UI = AscensionFR.DB.UI or {}
AscensionFR.DB.Libelles = AscensionFR.DB.Libelles or {}
AscensionFR.DB.HautsFaits = AscensionFR.DB.HautsFaits or {}
function AscensionFR.Recolter() end
UIErrorsFrame = nil
TaxiNodeOnButtonEnter = nil
AscensionFRSaved = { Options = {} }
"""

# Le pilote du banc. Les indices sont ceux de l'ordre de création, qui est
# l'ordre du .toc : WorldFrame, puis Core.lua, Perf.lua, BarresDeVie.lua,
# Plaques.lua. On les VÉRIFIE plutôt que de les supposer (voir _REPERES).
PILOTE = r"""
function _REPERES()
    _HORLOGE_PERF = _CADRES[3]
    _CADRE_BARRES = _CADRES[4]
    _CADRE_PLAQUES = _CADRES[5]
    _NB_CADRES = #_CADRES
end

function _MEMORISER_ORIGINAUX()
    _ORIG_PLAQUES = _CADRE_PLAQUES:GetScript("OnUpdate")
    _ORIG_BARRES = _CADRE_BARRES:GetScript("OnUpdate")
end

function _ORIGINAUX_REMIS()
    return _CADRE_PLAQUES:GetScript("OnUpdate") == _ORIG_PLAQUES
       and _CADRE_BARRES:GetScript("OnUpdate") == _ORIG_BARRES
end

function _ENROBES()
    return _CADRE_PLAQUES:GetScript("OnUpdate") ~= _ORIG_PLAQUES
       and _CADRE_BARRES:GetScript("OnUpdate") ~= _ORIG_BARRES
end

function _ECHANTILLONNEUR_TOURNE()
    return _HORLOGE_PERF:GetScript("OnUpdate") ~= nil
end

-- Fait battre le cadre de Plaques n fois, chaque tic coûtant `pas` ms.
function _TIC_PLAQUES(n, pas)
    _PAS = pas
    local f = _CADRE_PLAQUES:GetScript("OnUpdate")
    for _ = 1, n do f(_CADRE_PLAQUES, 0.3) end
    _PAS = 0            -- le reste du banc ne doit rien ajouter au compteur
end

-- Une seconde s'écoule : l'anneau tourne, et l'enrobage se rafraîchit.
function _SECONDE()
    _PAS = 0
    local f = _HORLOGE_PERF:GetScript("OnUpdate")
    f(_HORLOGE_PERF, 1.0)
end
"""


def charger(lua, relatif):
    with io.open(os.path.join(ADDON, relatif), encoding="utf-8") as fh:
        lua.execute(fh.read())


LIGNE = re.compile(
    r"^\s+(\S+)\s+([-\d.]+) ms/s\s+([-\d.]+) ms\s+([-\d.]+)\s*$", re.M)


def lire(releve, module):
    """(moyenne ms/s, pire ms, tics/s) pour un module, depuis le relevé."""
    for nom, moyenne, pire, tics in LIGNE.findall(releve):
        if nom == module:
            return float(moyenne), float(pire), float(tics)
    return None


def main():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)
    g = lua.globals()

    # --- chargement dans l'ORDRE DU .TOC : c'est lui qui fait l'encadrement --
    charger(lua, "Core.lua")
    charger(lua, os.path.join("Modules", "Perf.lua"))
    lua.execute(CONTEXTE_PLAQUES)
    charger(lua, os.path.join("Modules", "BarresDeVie.lua"))
    charger(lua, os.path.join("Modules", "Plaques.lua"))
    # Metiers.lua referme la portée « Plaques ». Seul son jalon nous concerne.
    lua.execute('AscensionFR.Perf.Jalon("Metiers")')
    lua.execute(PILOTE)
    g._REPERES()

    Perf = g.AscensionFR.Perf
    cas = []

    def noter(description, obtenu, attendu):
        cas.append((description, obtenu, attendu))

    noter("cinq cadres créés, dans l'ordre du .toc", int(g._NB_CADRES), 5)

    # --- avant tout : rien n'est enrobé, la mesure est éteinte -------------
    g._MEMORISER_ORIGINAUX()
    noter("au chargement : aucun enrobage",
          bool(g._ORIGINAUX_REMIS()), True)
    noter("au chargement : échantillonneur à l'arrêt",
          bool(g._ECHANTILLONNEUR_TOURNE()), False)

    # --- 1. ATTRIBUTION ----------------------------------------------------
    Perf.Allumer()
    noter("allumé : les cadres sont enrobés", bool(g._ENROBES()), True)
    noter("allumé : l'échantillonneur tourne",
          bool(g._ECHANTILLONNEUR_TOURNE()), True)

    # 30 tics ordinaires à 1 ms, puis UN tic à 25 ms.
    g._TIC_PLAQUES(30, 1)
    g._TIC_PLAQUES(1, 25)
    g._SECONDE()
    releve = str(Perf.Texte())
    mesure = lire(releve, "Plaques")
    noter("Plaques figure au relevé (encadrement réussi)",
          mesure is not None, True)
    if mesure:
        moyenne, pire, tics = mesure
        # 30 x 1 ms + 1 x 25 ms = 55 ms sur une seconde, 31 tics.
        noter("moyenne = 30x1ms + 1x25ms = 55 ms/s", moyenne, 55.0)
        noter("PIRE tic isolé à 25 ms, non noyé", pire, 25.0)
        noter("31 tics comptés", tics, 31.0)

    barres = lire(releve, "BarresDeVie")
    noter("BarresDeVie figure aussi (déclaration directe)",
          barres is not None, True)
    if barres:
        noter("BarresDeVie n'a rien battu : 0 ms/s", barres[0], 0.0)

    # --- 3. PAS D'EMPILEMENT -----------------------------------------------
    # Deux secondes identiques. Si l'enrobage s'enrobait lui-même, la seconde
    # coûterait le double de la première et la moyenne monterait à 15.
    Perf.Eteindre()
    Perf.Allumer()
    g._TIC_PLAQUES(10, 1)
    g._SECONDE()
    g._TIC_PLAQUES(10, 1)
    g._SECONDE()
    mesure2 = lire(str(Perf.Texte()), "Plaques")
    noter("deux secondes identiques -> moyenne stable à 10 ms/s",
          mesure2 and mesure2[0], 10.0)

    # --- 4. ÉTEINTE = ABSENTE ----------------------------------------------
    Perf.Eteindre()
    noter("éteint : les gestionnaires d'origine sont remis À L'IDENTIQUE",
          bool(g._ORIGINAUX_REMIS()), True)
    noter("éteint : l'échantillonneur n'a plus de script",
          bool(g._ECHANTILLONNEUR_TOURNE()), False)
    noter("éteint : le relevé le dit clairement",
          "ÉTEINTE" in str(Perf.Texte()), True)

    # --- le prix de l'instrument -------------------------------------------
    cout = float(Perf.Etalonner())
    noter("l'étalonnage rend un coût par appel chiffré",
          cout >= 0, True)

    # --- LA GRADUATION DE L'HORLOGE ----------------------------------------
    # `debugprofilestop` du client choisit à l'exécution entre une horloge
    # précise (QueryPerformanceCounter) et une horloge à ~15 ms (GetTickCount).
    # Sur la seconde, tous les chiffres du relevé seraient des multiples de la
    # graduation — faux, mais crédibles. L'instrument doit s'en apercevoir et
    # le dire. Ici, l'horloge truquée avance d'un pas connu : on vérifie que la
    # sonde retrouve ce pas, puis qu'un gros pas déclenche l'avertissement.
    lua.execute("_PAS = 0.001")
    noter("graduation fine mesurée correctement",
          round(float(Perf.Resolution()), 5), 0.001)
    Perf.Allumer()
    g._TIC_PLAQUES(5, 1)
    g._SECONDE()
    noter("horloge fine : aucun avertissement",
          "HORLOGE TROP GROSSIÈRE" in str(Perf.Texte()), False)
    Perf.Eteindre()

    lua.execute("_PAS = 15")            # le repli GetTickCount
    Perf.Allumer()
    g._TIC_PLAQUES(5, 15)
    g._SECONDE()
    noter("horloge à 15 ms : le relevé prévient qu'il est à jeter",
          "HORLOGE TROP GROSSIÈRE" in str(Perf.Texte()), True)
    Perf.Eteindre()

    # ---- LES GREFFES (programme 11) ---------------------------------------
    # Une greffe passe par un RELAIS qu'on ne peut pas retirer : il reste dans
    # la chaîne d'appel même mesure éteinte. Deux choses doivent donc être
    # tenues — qu'il ne change RIEN au comportement, et qu'il bascule bien.
    lua.execute(r"""
        _PAS = 1
        _RECU = nil
        _APPELS_BRUTS = 0
        local function brute(a, b)
            _APPELS_BRUTS = _APPELS_BRUTS + 1
            _RECU = tostring(a) .. "/" .. tostring(b)
        end
        -- DEUX relais sous LE MÊME nom : c'est le cas réel de l'interception
        -- des SetText, posée une fois par famille de composants. Une première
        -- version rangeait l'interrupteur dans le seau, si bien que seul le
        -- dernier posé savait basculer.
        _RELAIS_A = AscensionFR.Perf.Greffe("Essai", brute)
        _RELAIS_B = AscensionFR.Perf.Greffe("Essai", brute)
    """)
    # éteint : le relais doit être transparent
    lua.execute('_RELAIS_A("x", 2)')
    noter("greffe éteinte : les arguments passent intacts",
          str(g._RECU), "x/2")
    noter("greffe éteinte : la vraie fonction est bien appelée",
          int(g._APPELS_BRUTS), 1)

    Perf.Allumer()
    lua.execute('_RELAIS_A("y", 3) _RELAIS_B("z", 4)')
    g._SECONDE()
    noter("greffe allumée : les arguments passent toujours intacts",
          str(g._RECU), "z/4")
    releve_g = str(Perf.Texte())
    mesure_g = lire(releve_g, "Essai")
    noter("la greffe figure au relevé", mesure_g is not None, True)
    if mesure_g:
        # 2 appels x 1 ms, sur une seconde
        noter("les DEUX relais du même nom comptent", mesure_g[2], 2.0)
        noter("moyenne de la greffe = 2 ms/s", mesure_g[0], 2.0)

    # ---- L'ÉTIQUETTE QUI NE DOIT PLUS MENTIR ------------------------------
    noter("le relevé ne dit plus « TOTAL addon »",
          "TOTAL addon" in releve_g, False)
    noter("il dit « total des boucles »",
          "total des boucles" in releve_g, True)
    noter("il sépare « total des greffes »",
          "total des greffes" in releve_g, True)
    noter("il avertit que ce n'est PAS le total de l'addon",
          "PAS le total de l'addon" in releve_g, True)

    Perf.Eteindre()
    lua.execute("_APPELS_BRUTS = 0 _RELAIS_A('w', 5)")
    noter("réteinte : le relais redevient transparent",
          str(g._RECU) == "w/5" and int(g._APPELS_BRUTS) == 1, True)
    cout_r = float(Perf.EtalonnerRelais())
    noter("le prix permanent du relais est chiffré", cout_r >= 0, True)

    echecs = 0
    for description, obtenu, attendu in cas:
        if obtenu == attendu:
            print("  ok      %-52s %s" % (description, obtenu))
        else:
            print("  ECHEC   %-52s obtenu %r / attendu %r"
                  % (description, obtenu, attendu))
            echecs += 1
    print()
    print("%d échec(s)" % echecs)
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
