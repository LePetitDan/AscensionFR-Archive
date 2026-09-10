# -*- coding: utf-8 -*-
"""
Mesure du TAS LUA des bases de l'addon — et surtout de la DURÉE d'un ramassage
complet (programme 10, bloc 3, 01/08/2026).

POURQUOI. Un signalement Proton décrit « un à-coup toutes les ~20 s ». C'est la
signature d'un ramasse-miettes, pas d'un coût par image. Or plus le tas est
gros, plus un cycle complet est long. On veut donc trois chiffres, mesurés et
non devinés : ce que pèsent les bases une fois en mémoire, ce que coûte leur
chargement, et combien de temps prend un ramassage complet sur ce tas-là.

CE QUE CETTE MESURE VAUT — ET CE QU'ELLE NE VAUT PAS.
  - Le moteur est le MÊME (Lua 5.1) et les bases sont les VRAIES. La forme du
    résultat — quelle base pèse quoi, combien de temps un cycle prend sur un
    tas de cette taille — est directement transposable.
  - Mais ce Lua-ci est en 64 bits, alors que le client de WoW est en 32 bits.
    Tout pointeur y pèse 8 octets au lieu de 4 : l'ossature des tables et des
    chaînes est donc SURESTIMÉE ici. Le texte lui-même, lui, pèse pareil.
  - La durée d'un ramassage dépend de la machine. Celle d'ici n'est pas celle
    d'un joueur, et encore moins d'un joueur sous Wine/Proton. C'est l'ORDRE
    DE GRANDEUR, et la façon dont la durée suit la taille du tas, qui parlent.

Le chiffre qui fait foi côté joueur reste celui de `/afr perf` en jeu.

Usage : python outils/mesurer_tas_lua.py
"""
import io
import locale
import os
import sys
import time

# La console Windows est en cp1252 : un accent non converti tue le script en
# silence quand il tourne en tâche planifiée (piège connu du projet).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# lupa hors jeu : locale C d'abord, sinon la conversion des nombres dérape.
locale.setlocale(locale.LC_ALL, "C")

import lupa.lua51 as lupa_mod  # noqa: E402

ADDON = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
         r"\AscensionFR")

# Le strict minimum pour que Core.lua et les bases se chargent hors du jeu.
# On ne charge AUCUN module : on mesure les DONNÉES, pas le code.
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
    return { RegisterEvent = function() end,
             UnregisterEvent = function() end,
             SetScript = function() end,
             HookScript = function() end }
end

-- Le tas se lit par une globale : lupa n'a pas besoin d'évaluer d'expression.
function _RELEVER_TAS()
    collectgarbage("collect")
    collectgarbage("collect")
    _TAS = collectgarbage("count")
end

function _RAMASSER()
    collectgarbage("collect")
end

function _LISTER_BASES()
    local noms = {}
    for cle in pairs(AscensionFR.DB) do noms[#noms + 1] = cle end
    table.sort(noms)
    _BASES = noms
end
"""

# ---------------------------------------------------------------------------
# Forcer la matérialisation des bases paresseuses.
#
# Une base paresseuse ne pèse presque rien tant qu'on n'y touche pas : ce ne
# sont que des morceaux de source Lua. Le joueur, lui, finit par en réveiller
# une partie. On mesure donc les DEUX extrêmes : à la connexion (rien touché)
# et tout réveillé (le pire cas atteignable).
#
# Les morceaux vivent en variable locale de la fermeture __index.
# debug.getupvalue est le seul moyen de les atteindre sans toucher Core.lua.
# ---------------------------------------------------------------------------
MATERIALISER = r"""
function _MATERIALISER(nom)
    local t = AscensionFR.DB[nom]
    if type(t) ~= "table" then return 0, "absente" end
    local mt = getmetatable(t)
    if not mt or type(mt.__index) ~= "function" then return 0, "pleine" end
    local f = mt.__index
    local morceaux, cles, taille_seau
    for i = 1, 12 do
        local cle, valeur = debug.getupvalue(f, i)
        if not cle then break end
        if cle == "morceaux" then morceaux = valeur end
        if cle == "cles" then cles = valeur end
        if cle == "taille_seau" then taille_seau = valeur end
    end
    if not morceaux then return 0, "pleine" end

    local seaux = {}
    for seau in pairs(morceaux) do seaux[#seaux + 1] = seau end

    local reveilles = 0
    if taille_seau then
        -- Paresseux par IDENTIFIANT : une clé quelconque du seau suffit.
        for _, seau in ipairs(seaux) do
            local _ = t[seau * taille_seau]
            reveilles = reveilles + 1
        end
        return reveilles, "paresseuse (id)"
    end

    -- Paresseux par TEXTE : la chaîne de présence porte « \1clé\1clé\1 ».
    -- On en extrait la première clé réelle, seule façon de passer la garde.
    for _, octet in ipairs(seaux) do
        local presence = cles and cles[octet]
        if presence then
            local premiere = string.match(presence, "^\1(.-)\1")
            if premiere then
                local _ = t[premiere]
                reveilles = reveilles + 1
            end
        end
    end
    return reveilles, "paresseuse (texte)"
end
"""


def fichiers_du_toc():
    """Les bases RÉELLEMENT chargées par le jeu, dans l'ordre du .toc.

    Le dossier DB\\ contient aussi des .bak et des .avant_* que personne ne
    charge : les compter, c'est gonfler le diagnostic d'un dixième.
    """
    chemin = os.path.join(ADDON, "AscensionFR.toc")
    bases = []
    with io.open(chemin, encoding="utf-8") as fh:
        for ligne in fh:
            ligne = ligne.strip()
            if ligne.startswith("DB\\") and ligne.lower().endswith(".lua"):
                bases.append(ligne.replace("\\", os.sep))
    return bases


def mo(octets):
    return octets / (1024.0 * 1024.0)


def tas(lua):
    """Tas Lua en kilo-octets, après stabilisation."""
    lua.globals()._RELEVER_TAS()
    return float(lua.globals()._TAS)


def chrono_ramassage(lua, passes=5):
    """Durées d'un cycle de ramassage COMPLET, en millisecondes.

    On enchaîne plusieurs cycles et on garde le meilleur ET le pire : c'est
    la distinction que le programme réclame partout — la moyenne cache le pic,
    et c'est le pic qu'un joueur ressent comme un à-coup.
    """
    ramasser = lua.globals()._RAMASSER
    durees = []
    for _ in range(passes):
        t0 = time.perf_counter()
        ramasser()
        durees.append((time.perf_counter() - t0) * 1000.0)
    return durees


def main():
    bases = fichiers_du_toc()
    tous = os.listdir(os.path.join(ADDON, "DB"))
    disque_toc = sum(os.path.getsize(os.path.join(ADDON, r)) for r in bases)
    disque_dossier = sum(
        os.path.getsize(os.path.join(ADDON, "DB", f)) for f in tous)

    print("=" * 74)
    print("MESURE DU TAS LUA — bases d'AscensionFR")
    print("=" * 74)
    print()
    print("Lua 5.1, pointeurs de %d octets. Le client de WoW est en 32 bits :"
          % 8)
    print("l'ossature des tables est donc SURESTIMÉE ici ; le texte, non.")
    print()
    print("SUR LE DISQUE")
    print("  dossier DB\\ entier .......... %8.1f Mo  (%d fichiers)"
          % (mo(disque_dossier), len(tous)))
    print("  déclaré au .toc ............. %8.1f Mo  (%d fichiers)"
          % (mo(disque_toc), len(bases)))
    print("  jamais chargé (.bak/.avant_)  %8.1f Mo"
          % mo(disque_dossier - disque_toc))
    print()

    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)
    lua.execute(MATERIALISER)

    nu = tas(lua)
    with io.open(os.path.join(ADDON, "Core.lua"), encoding="utf-8") as fh:
        lua.execute(fh.read())
    apres_core = tas(lua)

    print("CHARGEMENT, BASE PAR BASE  (état de la connexion : rien réveillé)")
    print("  %-30s %10s %11s %8s"
          % ("base", "disque", "en mémoire", "temps"))
    print("  " + "-" * 62)

    precedent = apres_core
    total_ms = 0.0
    for relatif in bases:
        chemin = os.path.join(ADDON, relatif)
        taille = os.path.getsize(chemin)
        with io.open(chemin, encoding="utf-8") as fh:
            source = fh.read()
        t0 = time.perf_counter()
        lua.execute(source)
        ms = (time.perf_counter() - t0) * 1000.0
        total_ms += ms
        courant = tas(lua)
        delta = courant - precedent
        precedent = courant
        print("  %-30s %7.1f Mo %8.1f Mo %6.0f ms"
              % (os.path.basename(relatif), mo(taille), delta / 1024.0, ms))

    apres_bases = precedent
    print("  " + "-" * 62)
    print("  %-30s %7.1f Mo %8.1f Mo %6.0f ms"
          % ("TOTAL", mo(disque_toc), (apres_bases - apres_core) / 1024.0,
             total_ms))
    print()
    print("  tas Lua nu .................. %8.1f Mo" % (nu / 1024.0))
    print("  après Core.lua .............. %8.1f Mo" % (apres_core / 1024.0))
    print("  après les bases (connexion) . %8.1f Mo" % (apres_bases / 1024.0))
    print()

    print("RAMASSAGE COMPLET sur le tas de la connexion")
    durees = chrono_ramassage(lua)
    print("  cycles ...................... %s"
          % ", ".join("%.0f ms" % d for d in durees))
    print("  meilleur / PIRE ............. %.0f ms / %.0f ms"
          % (min(durees), max(durees)))
    print()

    print("MATÉRIALISATION DES PARESSEUSES  (le pire cas atteignable)")
    lua.globals()._LISTER_BASES()
    noms = lua.globals()._BASES
    materialiser = lua.globals()._MATERIALISER
    avant = tas(lua)
    for i in range(1, len(noms) + 1):
        nom = noms[i]
        reveilles, genre = materialiser(nom)
        if genre.startswith("paresseuse") and reveilles:
            apres = tas(lua)
            print("  %-18s %-20s %4d seaux   +%7.1f Mo"
                  % (nom, genre, reveilles, (apres - avant) / 1024.0))
            avant = apres
    reveille = tas(lua)
    print()
    print("  tas tout réveillé ........... %8.1f Mo  (connexion : %.1f Mo)"
          % (reveille / 1024.0, apres_bases / 1024.0))
    print()

    print("RAMASSAGE COMPLET sur le tas réveillé")
    durees2 = chrono_ramassage(lua)
    print("  cycles ...................... %s"
          % ", ".join("%.0f ms" % d for d in durees2))
    print("  meilleur / PIRE ............. %.0f ms / %.0f ms"
          % (min(durees2), max(durees2)))
    print()

    print("=" * 74)
    print("LECTURE")
    print("=" * 74)
    pire = max(max(durees), max(durees2))
    print("  Un ramassage complet coûte ici de %.0f à %.0f ms selon l'état "
          "du tas." % (min(durees), pire))
    print("  Une image dure 16,7 ms à 60 IPS, et 3,3 ms à 300 IPS.")
    print("  → le pire cycle mange %.0f image(s) à 60 IPS, %.0f à 300 IPS."
          % (pire / 16.7, pire / 3.3))
    print("  Ce n'est pas un coût par image : c'est un à-coup, rare et "
          "violent.")
    print("  C'est la signature exacte du signalement Proton — pas celle des "
          "300→45 IPS.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
