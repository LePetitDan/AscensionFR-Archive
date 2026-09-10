# -*- coding: utf-8 -*-
"""
Ce qui rend un ramassage LONG, et ce que coûtent nos déchets par tic
(programme 10, bloc 3 — le complément de mesurer_tas_lua.py).

TROIS QUESTIONS, TROIS MESURES.

1. Un ramassage coûte-t-il en OCTETS ou en OBJETS ? On compare le tas de la
   connexion (peu d'objets, de grosses chaînes) au tas réveillé (beaucoup de
   petits objets). Si la durée suit le nombre d'objets et non les octets, la
   conclusion change du tout au tout : ce n'est pas « 114 Mo, c'est gros »,
   c'est « des millions d'objets à visiter ».

2. Le jeu ne fait pas de `collect` complet : Lua 5.1 ramasse par PETITS PAS,
   au fil des allocations. On mesure donc aussi le pas incrémental — c'est lui
   que le joueur paie réellement, image après image.

3. Que coûte NOTRE déchet ? On reproduit l'allocation par tic que les modules
   font (`{ WorldFrame:GetChildren() }`) et on mesure ce qu'elle déclenche sur
   un tas de cette taille. C'est le lien direct entre le correctif du bloc 4 et
   l'à-coup ressenti.

Mêmes réserves que mesurer_tas_lua.py : Lua 5.1 mais en 64 bits, machine de
développement et non celle d'un joueur sous Proton.

Usage : python outils/mesurer_ramassage.py
"""
import io
import locale
import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

locale.setlocale(locale.LC_ALL, "C")

import lupa.lua51 as lupa_mod  # noqa: E402

ADDON = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
         r"\AscensionFR")

CONTEXTE = r"""
AscensionFR = AscensionFR or {}
function strtrim(s) return (string.gsub(s or "", "^%s*(.-)%s*$", "%1")) end
function UnitName() return "Mesure" end
function UnitClass() return "Templar" end
function UnitRace() return "Dwarf" end
function UnitSex() return 2 end
function hooksecurefunc() end
function print() end
function CreateFrame()
    return { RegisterEvent = function() end, UnregisterEvent = function() end,
             SetScript = function() end, HookScript = function() end }
end

function _RELEVER_TAS()
    collectgarbage("collect") collectgarbage("collect")
    _TAS = collectgarbage("count")
end
function _RAMASSER() collectgarbage("collect") end

-- ---------------------------------------------------------------------
-- COMPTER LES OBJETS. On descend dans tout ce qui est joignable depuis
-- AscensionFR.DB, en marquant les tables déjà vues (sinon un cycle nous
-- ferait tourner sans fin) et en comptant les chaînes DISTINCTES — Lua
-- 5.1 « interne » les chaînes : deux fois le même texte, un seul objet.
-- C'est donc bien le nombre d'objets que le ramasseur devra visiter.
-- ---------------------------------------------------------------------
function _COMPTER()
    local vues, chaines = {}, {}
    local nb_tables, nb_chaines, octets_texte, nb_champs = 0, 0, 0, 0
    local pile = { AscensionFR.DB }

    local function noter(v)
        local genre = type(v)
        if genre == "string" then
            if not chaines[v] then
                chaines[v] = true
                nb_chaines = nb_chaines + 1
                octets_texte = octets_texte + #v
            end
        elseif genre == "table" then
            if not vues[v] then
                vues[v] = true
                nb_tables = nb_tables + 1
                pile[#pile + 1] = v
            end
        end
    end

    vues[AscensionFR.DB] = true
    nb_tables = 1
    while #pile > 0 do
        local t = pile[#pile]
        pile[#pile] = nil
        for cle, valeur in pairs(t) do
            nb_champs = nb_champs + 1
            noter(cle)
            noter(valeur)
        end
    end
    _NB_TABLES, _NB_CHAINES = nb_tables, nb_chaines
    _OCTETS_TEXTE, _NB_CHAMPS = octets_texte, nb_champs
end

-- ---------------------------------------------------------------------
-- LE PAS INCRÉMENTAL. C'est ce que le jeu fait vraiment : au lieu d'un
-- gros arrêt, Lua avance le ramassage d'un cran à chaque allocation.
-- On mesure le PIRE pas, pas la moyenne : c'est le pire qui se voit.
-- ---------------------------------------------------------------------
function _PAS_INCREMENTAL(nb)
    collectgarbage("restart")
    local pire, total = 0, 0
    for _ = 1, nb do
        local t0 = os.clock()
        collectgarbage("step", 1)
        local d = os.clock() - t0
        total = total + d
        if d > pire then pire = d end
    end
    _PAS_PIRE, _PAS_MOYEN = pire * 1000, (total / nb) * 1000
end

-- ---------------------------------------------------------------------
-- NOTRE DÉCHET PAR TIC. `{ WorldFrame:GetChildren() }` fabrique une table
-- de N enfants. On la refait `tics` fois avec le ramassage ACTIF, comme
-- en jeu.
--
-- ATTENTION AU CHRONOMÈTRE. os.clock() est ici gradué à la milliseconde :
-- il ne peut PAS mesurer un tic qui dure quelques microsecondes, et rendrait
-- des « 1.000 ms » qui ne sont que sa propre graduation. On chronomètre donc
-- depuis Python, dont l'horloge descend sous la microseconde, et on ne
-- demande à Lua que d'exécuter le lot. C'est le premier piège que le
-- programme signale : ne pas mesurer sa propre mesure.
-- ---------------------------------------------------------------------
function _PREPARER_MONDE(enfants)
    _MONDE = {}
    for i = 1, enfants do _MONDE[i] = { id = i } end
    _VUS = {}
    collectgarbage("collect")
    collectgarbage("restart")
    _AVANT = collectgarbage("count")
end

function _LOT_AVEC_ALLOCATION(tics)
    local monde, n = _MONDE, #_MONDE
    for _ = 1, tics do
        local copie = {}                      -- l'allocation incriminée
        for i = 1, n do copie[i] = monde[i] end
    end
end

-- Le même travail SANS allouer : parcours direct, la forme du correctif.
function _LOT_SANS_ALLOCATION(tics)
    local monde, vus, n = _MONDE, _VUS, #_MONDE
    for _ = 1, tics do
        for i = 1, n do vus[monde[i]] = true end
    end
end

function _DECHET_PRODUIT()
    _TAS_DELTA = collectgarbage("count") - _AVANT
end
"""


def fichiers_du_toc():
    chemin = os.path.join(ADDON, "AscensionFR.toc")
    bases = []
    with io.open(chemin, encoding="utf-8") as fh:
        for ligne in fh:
            ligne = ligne.strip()
            if ligne.startswith("DB\\") and ligne.lower().endswith(".lua"):
                bases.append(ligne.replace("\\", os.sep))
    return bases


def tas(lua):
    lua.globals()._RELEVER_TAS()
    return float(lua.globals()._TAS)


def ramassage(lua, passes=5):
    ramasser = lua.globals()._RAMASSER
    durees = []
    for _ in range(passes):
        t0 = time.perf_counter()
        ramasser()
        durees.append((time.perf_counter() - t0) * 1000.0)
    return durees


def charger(lua):
    with io.open(os.path.join(ADDON, "Core.lua"), encoding="utf-8") as fh:
        lua.execute(fh.read())
    for relatif in fichiers_du_toc():
        with io.open(os.path.join(ADDON, relatif), encoding="utf-8") as fh:
            lua.execute(fh.read())


def compter(lua):
    lua.globals()._COMPTER()
    g = lua.globals()
    return (int(g._NB_TABLES), int(g._NB_CHAINES),
            int(g._OCTETS_TEXTE), int(g._NB_CHAMPS))


def main():
    print("=" * 74)
    print("CE QUI REND UN RAMASSAGE LONG")
    print("=" * 74)
    print()

    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)
    charger(lua)

    heap = tas(lua)
    nb_t, nb_c, octets, champs = compter(lua)
    durees = ramassage(lua)
    print("ÉTAT DE LA CONNEXION  (bases chargées, rien réveillé)")
    print("  tas Lua ..................... %8.1f Mo" % (heap / 1024.0))
    print("  tables joignables ........... %10d" % nb_t)
    print("  chaînes distinctes .......... %10d" % nb_c)
    # ⚠ SOUS-ESTIMATION CONNUE (corrigée au programme 11, 01/08/2026).
    # Ce parcours passe par pairs(), qui NE VOIT PAS les bases paresseuses :
    # leurs morceaux de source vivent en variable locale de la fermeture
    # __index. Le vrai texte est de 81,9 Mo, pas de 32,2. C'est exactement le
    # piège que DB_Meta.lua documente déjà (pairs() au login ratait ~770 000
    # textes) — il a été refait ici, dans un outil de mesure.
    # mesurer_tas_complet.py fait le parcours complet.
    print("  dont texte VU PAR pairs() ... %8.1f Mo   (sous-estimé : les "
          "bases paresseuses" % (octets / 1048576.0))
    print("                                          y échappent — voir "
          "mesurer_tas_complet.py)")
    print("  champs à visiter ............ %10d" % champs)
    print("  ramassage complet ........... %.0f-%.0f ms"
          % (min(durees), max(durees)))
    print()

    lua.globals()._PAS_INCREMENTAL(2000)
    print("  pas INCRÉMENTAL (ce que le jeu fait vraiment)")
    print("    moyen ..................... %.3f ms"
          % float(lua.globals()._PAS_MOYEN))
    print("    PIRE ...................... %.3f ms"
          % float(lua.globals()._PAS_PIRE))
    print()

    # --- le même tas, mais en beaucoup plus de petits objets --------------
    print("MÊME MATIÈRE, PLUS D'OBJETS  (bases paresseuses réveillées)")
    lua.execute(r"""
        local function reveiller(t)
            local mt = getmetatable(t)
            if not mt or type(mt.__index) ~= "function" then return end
            local f = mt.__index
            local morceaux, cles, taille_seau
            for i = 1, 12 do
                local cle, valeur = debug.getupvalue(f, i)
                if not cle then break end
                if cle == "morceaux" then morceaux = valeur end
                if cle == "cles" then cles = valeur end
                if cle == "taille_seau" then taille_seau = valeur end
            end
            if not morceaux then return end
            local seaux = {}
            for s in pairs(morceaux) do seaux[#seaux + 1] = s end
            for _, s in ipairs(seaux) do
                if taille_seau then
                    local _ = t[s * taille_seau]
                elseif cles and cles[s] then
                    local premiere = string.match(cles[s], "^\1(.-)\1")
                    if premiere then local _ = t[premiere] end
                end
            end
        end
        for _, t in pairs(AscensionFR.DB) do
            if type(t) == "table" then reveiller(t) end
        end
    """)
    heap2 = tas(lua)
    nb_t2, nb_c2, octets2, champs2 = compter(lua)
    durees2 = ramassage(lua)
    print("  tas Lua ..................... %8.1f Mo   (x%.2f)"
          % (heap2 / 1024.0, heap2 / heap))
    print("  tables joignables ........... %10d   (x%.1f)"
          % (nb_t2, nb_t2 / float(max(nb_t, 1))))
    print("  chaînes distinctes .......... %10d   (x%.1f)"
          % (nb_c2, nb_c2 / float(max(nb_c, 1))))
    print("  dont TEXTE pur .............. %8.1f Mo   (x%.2f)"
          % (octets2 / 1048576.0, octets2 / float(max(octets, 1))))
    print("  ramassage complet ........... %.0f-%.0f ms   (x%.2f)"
          % (min(durees2), max(durees2),
             max(durees2) / float(max(durees))))
    print()
    lua.globals()._PAS_INCREMENTAL(2000)
    print("  pas incrémental moyen / PIRE  %.3f ms / %.3f ms"
          % (float(lua.globals()._PAS_MOYEN),
             float(lua.globals()._PAS_PIRE)))
    print()
    print("  → le tas grossit de x%.2f, mais le ramassage de x%.2f."
          % (heap2 / heap, max(durees2) / float(max(durees))))
    print("    Ce n'est donc pas le POIDS qui coûte, c'est le NOMBRE "
          "d'objets à visiter.")
    print()

    # --- notre déchet par tic --------------------------------------------
    print("=" * 74)
    print("NOTRE DÉCHET PAR TIC  (l'allocation du bloc 4)")
    print("=" * 74)
    print()
    print("  Reproduit sur ce tas-là : `{ WorldFrame:GetChildren() }` refait")
    print("  4 fois par seconde, sur un WorldFrame de N enfants.")
    print("  Chronométré depuis Python (sous la microseconde) : os.clock() de")
    print("  Lua est gradué à la milliseconde et ne saurait rien mesurer ici.")
    print()
    g = lua.globals()
    TICS = 2400                          # dix minutes de jeu à 4 Hz
    print("  %8s %14s %13s %13s %11s"
          % ("enfants", "déchet/minute", "avec alloc.", "sans alloc.",
             "économie"))
    print("  " + "-" * 66)
    for enfants in (50, 200, 600):
        g._PREPARER_MONDE(enfants)
        t0 = time.perf_counter()
        g._LOT_AVEC_ALLOCATION(TICS)
        avec = (time.perf_counter() - t0) * 1000.0
        g._DECHET_PRODUIT()
        dechet = float(g._TAS_DELTA)

        g._PREPARER_MONDE(enfants)
        t0 = time.perf_counter()
        g._LOT_SANS_ALLOCATION(TICS)
        sans = (time.perf_counter() - t0) * 1000.0

        # ramené à la minute de jeu réelle : 4 tics par seconde = 240 tics
        par_min = dechet / 1024.0 * (240.0 / TICS)
        print("  %8d %10.1f Mo %8.4f ms %8.4f ms %9.0f %%"
              % (enfants, par_min, avec / TICS, sans / TICS,
                 100.0 * (avec - sans) / max(avec, 1e-9)))
    print()
    print("  (« avec » et « sans » sont le coût d'UN tic. Le déchet, lui, "
          "n'est pas payé")
    print("   sur le tic qui le produit : il est payé plus tard, par le "
          "ramassage.)")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
