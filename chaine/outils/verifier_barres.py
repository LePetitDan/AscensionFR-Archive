# -*- coding: utf-8 -*-
"""
Test des barres de vie flottantes (nameplates).

Cas de Dan : le sanglier affichait « Elder Crag Boar » au-dessus de sa tête
alors que l'encart de cible disait bien « Ancien sanglier des rochers ». Les
barres flottantes ne sont exposées par aucune API : il faut les reconnaître
parmi les enfants de WorldFrame à leur structure.

Vérifie qu'on identifie la bonne, qu'on traduit le nom sans toucher au niveau,
qu'on ignore les cadres qui n'en sont pas, et qu'un cadre protégé reste intact.
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

-- ConflitNameplate parcourt ADDONS_CONFLICTUELS et appelle IsAddOnLoaded
-- HORS pcall (BarresDeVie.lua:74) : sans ce stub le banc mourait sur
-- « attempt to call global 'IsAddOnLoaded' (a nil value) ». Rendre false =
-- aucun addon de nameplates chargé, le cas où notre module a le droit de
-- travailler. LibStub explicitement absent pour la même raison, côté
-- LibNameplate-1.0 (BarresDeVie.lua:67).
function IsAddOnLoaded() return false end
LibStub = nil

local function FS(t)
    local f = { _t = t }
    function f:GetText() return self._t end
    function f:SetText(v) self._t = v end
    function f:GetObjectType() return "FontString" end
    return f
end
_G.FS = FS

local function Barre()
    local b = {}
    function b:GetObjectType() return "StatusBar" end
    function b:GetName() return nil end
    function b:GetNumChildren() return 0 end
    return b
end
_G.Barre = Barre

-- cadre : regions, enfants, protégé ?
function Cadre(regions, enfants, protege, nom)
    local c = { _r = regions or {}, _e = enfants or {}, _p = protege, _n = nom }
    function c:GetRegions() return unpack(self._r) end
    function c:GetChildren() return unpack(self._e) end
    function c:GetNumChildren() return #self._e end
    function c:GetName() return self._n end
    function c:IsShown() return true end
    function c:IsProtected() return self._p, self._p end
    return c
end

_ONUPDATE = nil
function CreateFrame()
    return { RegisterEvent = function() end,
             SetScript = function(self, quoi, f)
                 if quoi == "OnUpdate" then _ONUPDATE = f end
             end,
             HookScript = function() end,
             Show = function() end, Hide = function() end }
end
"""

MONDE = r"""
-- La barre du sanglier : nom + niveau, deux enfants dont une barre de statut.
-- Le NIVEAU est placé AVANT le nom dans les régions, et ce n'est pas un
-- détail : ZoneDuNom (BarresDeVie.lua:96-110) prend le premier FontString non
-- numérique, et sa garde « not tonumber(texte) » est ce qui l'empêche de
-- prendre le niveau pour le nom. Avec le nom en premier, cette garde n'était
-- jamais exercée : mesuré le 27/07/2026, on pouvait la retirer et le banc
-- restait à 7 ok / 0 échec / code 0. Dans cet ordre-ci, la retirer fait
-- tomber « nom de créature traduit » (6 ok / 1 ÉCHEC / code 1) : le module
-- prend le « 7 » pour le nom, ne trouve rien dans la base et laisse le
-- sanglier en anglais. C'est la seule assertion qui bouge.
NOM_SANGLIER = FS("Elder Crag Boar")
NIVEAU       = FS("7")
BARRE_SANGLIER = Cadre({ NIVEAU, NOM_SANGLIER }, { Barre(), Barre() }, false)

-- Un joueur : ne doit pas être traduit (nom inconnu de la base)
NOM_JOUEUR = FS("Boundlessx")
BARRE_JOUEUR = Cadre({ NOM_JOUEUR }, { Barre(), Barre() }, false)

-- Un cadre protégé qui ressemble à une barre : à ne jamais toucher
NOM_PROTEGE = FS("Elder Crag Boar")
BARRE_PROTEGEE = Cadre({ NOM_PROTEGE }, { Barre(), Barre() }, true)

-- Pas une barre de vie (un seul enfant) : ignoré
NOM_AUTRE = FS("Elder Crag Boar")
AUTRE_CADRE = Cadre({ NOM_AUTRE }, { Barre() }, false)

-- Un cadre nommé : ce n'est jamais une barre flottante
NOM_NOMME = FS("Elder Crag Boar")
CADRE_NOMME = Cadre({ NOM_NOMME }, { Barre(), Barre() }, false, "MonCadre")

WorldFrame = Cadre({}, { BARRE_SANGLIER, BARRE_JOUEUR, BARRE_PROTEGEE,
                         AUTRE_CADRE, CADRE_NOMME })

AscensionFR.DB.Creatures[1234] = {
    NE = "Elder Crag Boar", N = "Ancien sanglier des rochers" }

local HORLOGE = { SetScript = function() end }

-- L'option est DÉCOCHÉE par défaut depuis la 1.7.5 (BarresDeVie.lua:63 rend
-- « conflit » tout de suite). On passe donc en DEUX TEMPS, sinon un module
-- muet parce que cassé ressemblerait trait pour trait à un module muet parce
-- que voulu.
-- 1) option décochée : le module doit se taire.
AscensionFRSaved = { Options = { barresDeVie = false } }
_ONUPDATE(HORLOGE, 1.0)
NOM_AVANT_OPTION = NOM_SANGLIER:GetText()

-- 2) option cochée : la traduction a lieu. (Le retour anticipé de la ligne 63
-- ne met pas « conflit » en cache : le second passage examine bien le monde.)
AscensionFRSaved.Options.barresDeVie = true
_ONUPDATE(HORLOGE, 1.0)
"""

# ---------------------------------------------------------------------------
# LE DÉCHET PAR TIC (programme 10, bloc 4, 01/08/2026).
#
# Les sept assertions ci-dessus passaient AUSSI avant le correctif : elles
# vérifient la traduction, pas la façon dont on l'obtient. Un banc qui reste
# vert quand on réintroduit la faute ne protège rien du tout.
#
# Celle-ci mord. Elle refait tourner le module dans un monde chargé — 300
# enfants, le compte qui bouge à chaque tic, donc le chemin de ré-examen
# emprunté à CHAQUE fois — et pèse le déchet produit. La version fautive
# fabriquait une table de tous les enfants du monde par tic ; la version
# corrigée parcourt les varargs et n'alloue rien.
#
# Le seuil est en octets PAR TIC, pas en total : il reste juste quel que soit
# le nombre de tics, et il est très large (une table de 300 entrées pèse à
# elle seule plusieurs kilo-octets).
# ---------------------------------------------------------------------------
TICS = 200
ENFANTS = 300
SEUIL_OCTETS_PAR_TIC = 1024

DECHET = r"""
-- Un monde chargé : beaucoup de barres, plus du décor qui n'en est pas.
local peuple = {}
for i = 1, %(enfants)d do
    if i %% 3 == 0 then
        -- une vraie barre de vie : niveau + nom, deux enfants dont une
        -- StatusBar. Nom inconnu de la base -> aucune traduction, donc
        -- aucune allocation imputable à la traduction elle-même : ce qu'on
        -- pèsera sera bien celle du ré-examen, et rien d'autre.
        peuple[i] = Cadre({ FS(tostring(i)), FS("Creature " .. i) },
                          { Barre(), Barre() }, false)
    else
        peuple[i] = Cadre({ FS("decor") }, { Barre() }, false)
    end
end

-- Le compte d'enfants BOUGE à chaque interrogation : c'est ce qui force le
-- ré-examen complet à chaque tic, exactement le cas d'une ville bondée où
-- des plaques apparaissent et disparaissent sans arrêt.
local compteur = 0
MONDE_CHARGE = Cadre({}, peuple)
function MONDE_CHARGE:GetNumChildren()
    compteur = compteur + 1
    return compteur
end
WorldFrame = MONDE_CHARGE

HORLOGE_DECHET = { SetScript = function() end }

-- On chauffe d'abord : le premier passage a le droit de coûter (index
-- inversés, relevé des zones de texte, découverte des barres). C'est le
-- RÉGIME ÉTABLI qu'on juge, pas le démarrage.
for _ = 1, 20 do _ONUPDATE(HORLOGE_DECHET, 1.0) end

-- ON ARRÊTE LE RAMASSEUR. Sans ça, la mesure ne veut rien dire : après un
-- ramassage, une table allouée puis lâchée a disparu, et le tas revient à
-- son point de départ — la version fautive et la version corrigée rendraient
-- le même zéro. Ramasseur à l'arrêt, tout ce qui est alloué RESTE, et le tas
-- mesure exactement ce que le module a demandé à la mémoire.
collectgarbage("collect")
collectgarbage("collect")
collectgarbage("stop")
local avant = collectgarbage("count")
for _ = 1, %(tics)d do _ONUPDATE(HORLOGE_DECHET, 1.0) end
local apres = collectgarbage("count")
collectgarbage("restart")
DECHET_PAR_TIC = (apres - avant) * 1024 / %(tics)d
""" % {"enfants": ENFANTS, "tics": TICS}


def main():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)
    for f in ["Core.lua", "Modules\\Recolte.lua", "Modules\\BarresDeVie.lua"]:
        with open(ADDON + "\\" + f, encoding="utf-8") as fh:
            lua.execute(fh.read())
    lua.execute(MONDE)
    g = lua.globals()

    cas = [
        # Sans cette première ligne, un module qui ne traduit plus RIEN
        # passerait pour « bien silencieux » : c'est elle qui sépare le
        # silence voulu (option décochée) du silence cassé.
        ("option décochée -> module muet", g.NOM_AVANT_OPTION,
         "Elder Crag Boar"),
        ("nom de créature traduit",
         g.NOM_SANGLIER.GetText(g.NOM_SANGLIER), "Ancien sanglier des rochers"),
        ("niveau laissé intact", g.NIVEAU.GetText(g.NIVEAU), "7"),
        ("nom de joueur -> intact",
         g.NOM_JOUEUR.GetText(g.NOM_JOUEUR), "Boundlessx"),
        ("cadre protégé -> jamais touché",
         g.NOM_PROTEGE.GetText(g.NOM_PROTEGE), "Elder Crag Boar"),
        ("cadre qui n'est pas une barre -> ignoré",
         g.NOM_AUTRE.GetText(g.NOM_AUTRE), "Elder Crag Boar"),
        ("cadre nommé -> ignoré",
         g.NOM_NOMME.GetText(g.NOM_NOMME), "Elder Crag Boar"),
    ]
    echecs = 0
    for description, obtenu, attendu in cas:
        if obtenu == attendu:
            print("  ok      %-38s %s" % (description, obtenu))
        else:
            print("  ECHEC   %-38s obtenu %r / attendu %r"
                  % (description, obtenu, attendu))
            echecs += 1

    # --- le déchet par tic, en régime établi -------------------------------
    lua.execute(DECHET)
    par_tic = float(lua.globals().DECHET_PAR_TIC)
    description = "aucune allocation par tic (%d enfants)" % ENFANTS
    if par_tic < SEUIL_OCTETS_PAR_TIC:
        print("  ok      %-38s %.0f o/tic (seuil %d)"
              % (description, par_tic, SEUIL_OCTETS_PAR_TIC))
    else:
        print("  ECHEC   %-38s %.0f o/tic, au-dessus du seuil de %d"
              % (description, par_tic, SEUIL_OCTETS_PAR_TIC))
        print("          Une table est allouée à chaque examen du monde. "
              "C'est le déchet")
        print("          qui nourrit les à-coups Linux/Proton : parcourir "
              "les varargs")
        print("          au lieu de « { WorldFrame:GetChildren() } ».")
        echecs += 1

    print()
    print("%d échec(s)" % echecs)
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
