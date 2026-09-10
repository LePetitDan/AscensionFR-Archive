# -*- coding: utf-8 -*-
"""
Banc de la détection des fenêtres custom (Epreuves.lua, programme 11).

DEUX BANCS, ET IL EN FAUT DEUX. La correction du 01/08 échange du coût contre
un risque : mémoriser les échecs fait chuter le travail, mais peut faire perdre
des traductions si un cadre rempli après coup n'est jamais retesté. Un seul
banc ne peut pas tenir les deux bouts.

  1. LE COÛT — un cadre qui échoue ne doit plus être refouillé deux fois par
     seconde. Ce banc compte les VISITES réelles sur un décor de 200 cadres et
     passe au rouge si elles repartent à la hausse. Il mord : réintroduire le
     défaut le fait échouer.

     Et un cadre QUI CLIGNOTE ne doit pas racheter une descente à chaque
     réapparition. C'est le comportement de GameTooltip (à chaque survol de
     souris), CastingBarFrame, LootFrame... Cette assertion-là manquait à la
     première version du banc, et le défaut qu'elle attrape était bel et bien
     dans le code livré : le masquage effaçait la mémoire des échecs en même
     temps que le minuteur.

  2. LA TRADUCTION QUI NE DOIT PAS SE PERDRE — c'est celui qui garde le piège
     fermé. Une fenêtre qui n'obtient son titre qu'après coup doit FINIR
     traduite, dans les deux cas réels :
        a) elle reste affichée et gagne son titre plus tard ;
        b) elle est fermée puis rouverte avec son titre.
     Si un jour quelqu'un remplace l'attente qui double par un simple
     « on n'y revient jamais », c'est ce banc-là qui criera.

Usage : python outils/verifier_detection_fenetres.py
"""
import io
import locale
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

locale.setlocale(locale.LC_ALL, "C")

import lupa.lua51 as lupa_mod  # noqa: E402

ADDON = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
         r"\AscensionFR")

DECOR = 200          # enfants d'UIParent qui n'ont rien à voir avec nous
SCANS = 40           # 40 passages = 20 s de jeu (la détection tourne à 2 Hz)

# Plafond de visites sur les 39 passages qui suivent le premier. Avec l'attente
# qui double (2, 4, 8, 16, 30 s), un cadre de décor est retesté ~4 fois en 20 s
# au lieu de 40. On laisse une marge large : ce qui compte est l'ordre de
# grandeur, et le défaut réintroduit produit 200 x 39 = 7 800 visites.
PLAFOND_VISITES = 2500

# Fouilles tolérées pour UN cadre qui clignote sur 39 apparitions. La reprise
# est limitée en CADENCE (un essai gratuit toutes les 30 s au plus), et l'essai
# couvre ~20 s de jeu : une ou deux fouilles, pas davantage. Sans cette garde,
# le cadre se refaisait fouiller à CHAQUE réapparition — mesuré : 39 sur 39.
PLAFOND_CLIGNOTANT = 10

CONTEXTE = r"""
-- ---------------------------------------------------------------------
-- L'horloge du banc. Le rattrapage repose sur GetTime() : on la pilote,
-- sinon on ne peut pas éprouver l'attente qui double.
-- ---------------------------------------------------------------------
_TEMPS = 1000
function GetTime() return _TEMPS end
function _AVANCER(s) _TEMPS = _TEMPS + s end

function strtrim(s) return (string.gsub(s or "", "^%s*(.-)%s*$", "%1")) end
function print() end
function hooksecurefunc() end
function IsAddOnLoaded() return false end
function ChatFrame_AddMessageEventFilter() end
function UnitName() return "Testeur" end
function UnitClass() return "Templar" end
function UnitRace() return "Dwarf" end
function UnitSex() return 2 end
function UnitLevel() return 80 end
function GetLocale() return "enUS" end
function GetRealZoneText() return "Hurlevent" end
function GetSubZoneText() return "" end
function InCombatLockdown() return false end
function GetFramerate() return 60 end
function debugprofilestop() return 0 end
function wipe(t) for k in pairs(t) do t[k] = nil end return t end
function GetSpellInfo() return nil end
function GetNumSpellTabs() return 0 end
function GetSpellTabInfo() return nil end
function GetTradeSkillLine() return nil end
AscensionFRSaved = { Options = {} }
SlashCmdList = {}
UISpecialFrames = {}
GameTooltip = { HookScript = function() end,
                GetName = function() return "GameTooltip" end }

-- ---------------------------------------------------------------------
-- Les cadres du banc. Chacun COMPTE ses visites : c'est notre mesure du
-- travail réellement fait, plus parlante qu'un tas Lua et insensible au
-- ramasse-miettes.
-- ---------------------------------------------------------------------
_VISITES = 0

function FS(t)
    local f = { _t = t }
    function f:GetText() return self._t end
    function f:SetText(v) self._t = v end
    function f:GetObjectType() return "FontString" end
    return f
end

function Cadre(regions, enfants, affiche, nom)
    local c = { _r = regions or {}, _e = enfants or {},
                _shown = (affiche ~= false), _n = nom }
    function c:GetObjectType() return "Frame" end
    function c:GetName() return self._n end
    function c:GetRegions()
        _VISITES = _VISITES + 1        -- <- la sonde
        return unpack(self._r)
    end
    function c:GetChildren() return unpack(self._e) end
    function c:GetNumChildren() return #self._e end
    function c:IsShown() return self._shown end
    function c:IsVisible() return self._shown end
    function c:IsProtected() return false end
    function c:HookScript() end
    function c:SetScript() end
    function c:GetParent() return nil end
    return c
end

_CADRES = {}
function CreateFrame()
    local f = { _scripts = {}, _evts = {} }
    function f:RegisterEvent(e) self._evts[e] = true end
    function f:UnregisterEvent(e) self._evts[e] = nil end
    function f:SetScript(quoi, fn) self._scripts[quoi] = fn end
    function f:GetScript(quoi) return self._scripts[quoi] end
    function f:HookScript() end
    function f:Show() end
    function f:Hide() end
    function f:SetSize() end
    function f:SetPoint() end
    function f:SetFrameStrata() end
    function f:SetMovable() end
    function f:EnableMouse() end
    function f:RegisterForDrag() end
    function f:SetBackdrop() end
    function f:CreateFontString() return FS("") end
    _CADRES[#_CADRES + 1] = f
    return f
end

-- Fait battre TOUTES les boucles du module. On ne cherche pas à deviner
-- laquelle est la bonne : seule notre sonde de visites compte.
function _BATTRE(secondes)
    for i = 1, #_CADRES do
        local f = _CADRES[i]._scripts and _CADRES[i]._scripts.OnUpdate
        if f then pcall(f, _CADRES[i], secondes) end
    end
end
"""

MONDE = r"""
-- Le décor : %(decor)d cadres qui ne sont PAS des fenêtres custom. Chacun a
-- deux zones de texte inconnues et un enfant, pour que la descente ait de
-- quoi travailler — c'est le cas réel d'un UIParent chargé.
local decor = {}
for i = 1, %(decor)d do
    local petit = Cadre({ FS("bidule " .. i) }, {}, true)
    decor[i] = Cadre({ FS("decor " .. i), FS(tostring(i)) }, { petit }, true)
end

-- LE RETARDATAIRE : une fenêtre affichée SANS titre. Elle échoue d'abord.
TITRE_TARDIF = FS("")
FENETRE_TARDIVE = Cadre({ TITRE_TARDIF }, {}, true)
decor[#decor + 1] = FENETRE_TARDIVE

-- LE REVENANT : une fenêtre qui sera fermée, puis rouverte avec son titre.
TITRE_REVENANT = FS("")
FENETRE_REVENANTE = Cadre({ TITRE_REVENANT }, {}, true)
decor[#decor + 1] = FENETRE_REVENANTE

-- LE CLIGNOTANT : un cadre banal qui apparaît et disparaît sans arrêt, sans
-- jamais porter de titre. C'est le comportement de GameTooltip (à chaque
-- survol de souris), CastingBarFrame, LootFrame, MirrorTimer1... Il ne doit
-- PAS pouvoir remettre son attente à zéro en clignotant, sinon il repaie une
-- descente complète toutes les deux secondes.
CLIGNOTANT = Cadre({ FS("clignote"), FS("2") },
                   { Cadre({ FS("petit") }, {}, true) }, true)
decor[#decor + 1] = CLIGNOTANT

-- Un compteur RIEN QUE POUR LUI. Le déduire par soustraction de deux séries
-- ne marche pas : le décor voit ses attentes s'allonger pendant l'essai, et
-- cette dérive écrase complètement le signal qu'on cherche. On compte donc à
-- la source.
_VISITES_CLIGNOTANT = 0
local sesRegions = CLIGNOTANT.GetRegions
function CLIGNOTANT:GetRegions()
    _VISITES_CLIGNOTANT = _VISITES_CLIGNOTANT + 1
    return sesRegions(self)
end

UIParent = Cadre({}, decor, true)

-- « Wardrobe » est un titre custom connu (TITRES_CUSTOM). Le pont de
-- traduction le rend en français : c'est ce qu'on vérifiera.
AscensionFR.DB.Epreuves["Wardrobe"] = "Garde-robe"
"""


def charger(lua, relatif):
    with io.open(os.path.join(ADDON, relatif), encoding="utf-8") as fh:
        lua.execute(fh.read())


def main():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)
    charger(lua, "Core.lua")
    charger(lua, os.path.join("Modules", "Epreuves.lua"))
    lua.execute(MONDE % {"decor": DECOR})
    g = lua.globals()

    cas = []

    def noter(description, obtenu, attendu):
        cas.append((description, obtenu, attendu))

    # ---- BANC 1 : LE COÛT -------------------------------------------------
    # Premier passage : tout le décor est examiné, c'est normal et voulu.
    g._BATTRE(1.0)
    premier = int(g._VISITES)
    noter("1er passage : le décor est bien examiné", premier > DECOR, True)

    # Les 39 suivants, en avançant l'horloge d'une demi-seconde à chaque fois,
    # exactement comme le jeu.
    lua.execute("_VISITES = 0")
    for _ in range(SCANS - 1):
        g._AVANCER(0.5)
        g._BATTRE(1.0)
    ensuite = int(g._VISITES)

    noter("les passages suivants ne refouillent plus tout",
          ensuite <= PLAFOND_VISITES,
          True)
    print("          (%d visites sur %d passages ; sans la mémoire des échecs "
          "il y en aurait ~%d)" % (ensuite, SCANS - 1, premier * (SCANS - 1)))

    # ---- LE CLIGNOTANT ----------------------------------------------------
    # Un cadre qui apparaît et disparaît sans arrêt ne doit PAS pouvoir remettre
    # son attente à zéro. Sinon il repaie une descente complète de profondeur 6
    # toutes les deux secondes — et les cadres qui clignotent le plus sont les
    # plus actifs de l'interface (GameTooltip suit la souris).
    #
    # Cette assertion manquait à la première version du banc, et le défaut
    # qu'elle attrape était bel et bien dans le code livré : le masquage
    # effaçait la MÉMOIRE des échecs en même temps que le minuteur.
    # On compte les descentes DU CLIGNOTANT LUI-MÊME. Ma première tentative
    # déduisait son coût en soustrayant deux séries : ça ne marche pas, la
    # dérive des attentes du décor écrase le signal, et l'assertion passait
    # quoi qu'il arrive. Un banc qui ne peut pas échouer n'est pas un banc.
    lua.execute("_VISITES_CLIGNOTANT = 0")
    for _ in range(SCANS - 1):
        g._AVANCER(0.5)
        lua.execute("CLIGNOTANT._shown = false")
        g._BATTRE(1.0)                      # on le voit disparaître
        lua.execute("CLIGNOTANT._shown = true")
        g._BATTRE(1.0)                      # il revient
    visites_clignotant = int(g._VISITES_CLIGNOTANT)
    noter("un cadre qui clignote ne rachète pas de descente",
          visites_clignotant <= PLAFOND_CLIGNOTANT, True)
    print("          (le clignotant a été fouillé %d fois en %d "
          "apparitions ; seuil %d)"
          % (visites_clignotant, SCANS - 1, PLAFOND_CLIGNOTANT))

    # ---- BANC 2 : LA TRADUCTION QUI NE DOIT PAS SE PERDRE -----------------
    # (a) la fenêtre reste affichée et gagne son titre APRÈS coup.
    lua.execute('TITRE_TARDIF:SetText("Wardrobe")')
    # L'attente a doublé plusieurs fois : on laisse passer le plafond.
    for _ in range(4):
        g._AVANCER(31)
        g._BATTRE(1.0)
    noter("(a) fenêtre remplie après coup : traduite quand même",
          str(g.TITRE_TARDIF.GetText(g.TITRE_TARDIF)), "Garde-robe")

    # (b) la fenêtre est fermée, puis rouverte avec son titre. Elle doit être
    #     retestée TOUT DE SUITE, sans attendre la fin de l'attente.
    lua.execute("FENETRE_REVENANTE._shown = false")
    g._BATTRE(1.0)                       # on la voit disparaître : ardoise effacée
    lua.execute('TITRE_REVENANT:SetText("Wardrobe")')
    lua.execute("FENETRE_REVENANTE._shown = true")
    g._AVANCER(0.5)                      # une demi-seconde, pas trente
    g._BATTRE(1.0)
    noter("(b) fenêtre rouverte : retestée sans attendre",
          str(g.TITRE_REVENANT.GetText(g.TITRE_REVENANT)), "Garde-robe")

    echecs = 0
    for description, obtenu, attendu in cas:
        if obtenu == attendu:
            print("  ok      %-48s %s" % (description, obtenu))
        else:
            print("  ECHEC   %-48s obtenu %r / attendu %r"
                  % (description, obtenu, attendu))
            echecs += 1
    print()
    print("%d échec(s)" % echecs)
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
