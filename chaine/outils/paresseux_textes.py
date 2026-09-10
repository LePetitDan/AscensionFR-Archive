# -*- coding: utf-8 -*-
"""Rend PARESSEUSES les grandes bases à clés TEXTE (2.0.1, mini-blocages).

Transforme un DB_*.lua plat (lignes `DB["clé"]="valeur"`) en seaux par
premier octet de la clé :
  - une CHAÎNE DE PRÉSENCE par seau : "\\1clé\\1clé\\1..." (clés BRUTES,
    déséchappées — c'est elle qu'interroge le jeu, sans rien compiler) ;
  - un MORCEAU de source Lua par seau (les fragments d'origine, recopiés
    tels quels), compilé au premier accès d'une clé présente.
Consommé par AFR.ParesseuxTexte (Core.lua). PAS de pairs() possible.

Cibles (les seules sûres — HautsFaits est parcouru par Normalisee) :
  DB_SortsNoms.lua (77 600 noms), DB_Repliques.lua (69 500 paroles).

Vérification INTÉGRÉE : rejoue chaque fichier transformé dans lupa
(clé sur 2 présente + absente) et refuse d'écrire si divergence.
Usage : python outils/paresseux_textes.py [--ecrire]
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chemin_client import ADDONS  # noqa: E402

CIBLES = [
    (os.path.join(ADDONS, "AscensionFR", "DB", "DB_SortsNoms.lua"),
     "AscensionFR.DB.SortsNoms"),
    (os.path.join(ADDONS, "AscensionFR_Repliques", "DB_Repliques.lua"),
     "AscensionFR.DB.Repliques"),
]

RE_LIGNE = re.compile(r'^DB\[("(?:\\.|[^"\\])*")\]=("(?:\\.|[^"\\])*")$')


def desechapper(litteral):
    """Chaîne Lua entre guillemets -> texte brut (échappes de ecrire_db)."""
    corps = litteral[1:-1]
    sortie = []
    i = 0
    while i < len(corps):
        c = corps[i]
        if c == "\\" and i + 1 < len(corps):
            n = corps[i + 1]
            sortie.append({"n": "\n", "r": "\r", "t": "\t",
                           '"': '"', "\\": "\\", "'": "'"}.get(n, n))
            i += 2
        else:
            sortie.append(c)
            i += 1
    return "".join(sortie)


def echapper_presence(brut):
    """Texte brut -> littéral Lua entre guillemets (dont \\1 séparateur)."""
    s = brut.replace("\\", "\\\\").replace('"', '\\"')
    s = s.replace("\r", "\\r").replace("\n", "\\n")
    return s


def transformer(chemin, table_lua, ecrire):
    lignes = io.open(chemin, encoding="utf-8").read().splitlines()
    seaux_cles, seaux_morceaux, entetes = {}, {}, []
    nb = 0
    for ligne in lignes:
        m = RE_LIGNE.match(ligne)
        if not m:
            if ligne.startswith("--"):
                entetes.append(ligne)
            continue
        cle_brute = desechapper(m.group(1))
        if not cle_brute:
            continue
        octet = cle_brute.encode("utf-8")[0]
        seaux_cles.setdefault(octet, []).append(cle_brute)
        seaux_morceaux.setdefault(octet, []).append(
            "[%s]=%s," % (m.group(1), m.group(2)))
        nb += 1
    if not nb:
        print("! %s : aucune ligne DB, rien à faire" % chemin)
        return False

    sortie = ["-- Fichier PARESSEUX par TEXTE (outils/paresseux_textes.py)."]
    sortie += ["-- Source de vérité : la version plate produite par l'usine.",
               "-- Présence par seau (1er octet) puis compilation au 1er",
               "-- accès. PAS de pairs() sur cette table.",
               "local C = {}", "local M = {}"]
    for octet in sorted(seaux_cles):
        # \001 (3 chiffres) et jamais \1 : suivi d'un chiffre de la clé
        # (« 1% Threat Aura »), \1 deviendrait \11 — vécu au premier essai.
        presence = "\\001" + "\\001".join(
            echapper_presence(c) for c in seaux_cles[octet]) + "\\001"
        sortie.append('C[%d]="%s"' % (octet, presence))
        corps = "".join(seaux_morceaux[octet])
        niveau = 2
        while ("]" + "=" * niveau + "]") in corps:
            niveau += 1
        ouvre, ferme = "[" + "=" * niveau + "[", "]" + "=" * niveau + "]"
        sortie.append("M[%d]=%s%s%s" % (octet, ouvre, corps, ferme))
    sortie.append("%s = AscensionFR.ParesseuxTexte(C, M)" % table_lua)
    texte = "\n".join(sortie) + "\n"

    # --- Vérification lupa : plat CONTRE paresseux ---
    # IMPÉRATIVEMENT lua51 : c'est ici qu'on décide d'écrire, ou non, la base
    # que le jeu chargera. Le lupa par défaut est en Lua 5.5, qui accepte des
    # fichiers que Lua 5.1 refuse (« constant table overflow ») : ce contrôle
    # était incapable de voir un dépassement, alors que la version PLATE de
    # DB_ObjetsNoms est à ~148 % de la limite de 5.1.
    import lupa.lua51 as lupa
    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    lua.execute("loadstring = loadstring or load")
    lua.execute("AscensionFR = { DB = {} }")
    noyau = io.open(os.path.join(ADDONS, "AscensionFR", "Core.lua"),
                    encoding="utf-8").read()
    debut = noyau.index("function AFR.ParesseuxTexte")
    fin = noyau.index("AFR.DB = {")
    lua.execute("local AFR = AscensionFR\n" + noyau[debut:fin])

    plat = {}
    for ligne in lignes:
        m = RE_LIGNE.match(ligne)
        if m:
            plat[desechapper(m.group(1))] = desechapper(m.group(2))
    lua.execute(texte.replace(table_lua, "_G.LAZY"))
    lazy = lua.globals().LAZY
    rates = 0
    cles_test = sorted(plat)[::2]
    for cle in cles_test:
        if lazy[cle] != plat[cle]:
            rates += 1
            if rates <= 3:
                print("  DIVERGENCE :", repr(cle[:60]))
    absents = ["Texte qui n'existe pas 123", "zzz", "\x01piege"]
    for cle in absents:
        if lazy[cle] is not None:
            rates += 1
            print("  FANTÔME :", repr(cle))
    print("%s : %d entrées, %d seaux, test %d/%d clés + %d absentes -> %s"
          % (os.path.basename(chemin), nb, len(seaux_cles),
             len(cles_test) - rates, len(cles_test), len(absents),
             "OK" if rates == 0 else "%d RATÉS" % rates))
    if rates:
        return False
    if ecrire:
        io.open(chemin, "w", encoding="utf-8", newline="\n").write(texte)
        print("  écrit : %s (%.1f Mo)"
              % (chemin, os.path.getsize(chemin) / 1048576.0))
    return True


def poser(chemin, contenu_plat, table_lua):
    """Pose une base PARESSEUSE sans jamais laisser le format plat à l'arrivée.

    POURQUOI (25/07/2026). Les ponts de noms écrivaient leur version PLATE
    directement sur le chemin livré, puis la convertissaient dans un
    try/except dont personne ne lisait le résultat. Or, pour DB_ObjetsNoms,
    ce plat réclame ~388 000 constantes là où Lua 5.1 en accepte 262 143 :
    il NE COMPILE PAS. À la moindre conversion ratée — et transformer() rend
    False sans lever — le fichier mort restait en place, sous un message
    rassurant (« la base plate reste valable ») qui était faux.

    On écrit donc à côté, on convertit, et on ne déplace qu'en cas de succès.
    Rend True si la base livrée a bien été remplacée.
    """
    temporaire = chemin + ".plat"
    io.open(temporaire, "w", encoding="utf-8", newline="").write(contenu_plat)
    if not transformer(temporaire, table_lua, True):
        print("! %s NON REMPLACÉ : la mise en paresseux a échoué."
              % os.path.basename(chemin))
        print("  L'ancienne base, elle, se charge encore. Le brouillon est "
              "laissé dans %s pour examen." % os.path.basename(temporaire))
        return False
    os.replace(temporaire, chemin)
    print("  posé : %s (%.1f Mo)"
          % (os.path.basename(chemin), os.path.getsize(chemin) / 1048576.0))
    return True


def main():
    ecrire = "--ecrire" in sys.argv
    tout_bon = True
    for chemin, table in CIBLES:
        if os.path.exists(chemin):
            contenu = io.open(chemin, encoding="utf-8").readline()
            if "PARESSEUX" in contenu:
                print("%s : déjà paresseux, rien à faire"
                      % os.path.basename(chemin))
                continue
            tout_bon = transformer(chemin, table, ecrire) and tout_bon
    if not ecrire:
        print("\nAPERÇU seulement — relance avec --ecrire pour transformer.")
    return 0 if tout_bon else 1


if __name__ == "__main__":
    sys.exit(main())
