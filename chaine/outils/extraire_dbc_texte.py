# -*- coding: utf-8 -*-
"""Extracteur GÉNÉRIQUE d'une table .dbc à textes (chantier complétude).

Trouve la table dans les patchs du jeu (le dernier patch gagne), détecte
EMPIRIQUEMENT les colonnes de texte (statistiques par colonne sur toutes
les lignes — jamais de suppositions, leçon des colonnes 7/24), et dump
tout dans sources/dbc/<table>.json :
    { "colonnes": {indice: taux_de_texte}, "lignes": [{"id": ..,
      "c<indice>": "texte", ...}, ...] }

Usage : python outils/extraire_dbc_texte.py CharacterAdvancement
"""
import glob
import io
import json
import os
import re
import struct
import sys

sys.stdout.reconfigure(encoding="utf-8")
from mpyq import MPQArchive

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Data"
RE_TEXTE = re.compile(r"[A-Za-z]{2}")


def extraire(nom_table, mpq_seul=None, suffixe=""):
    voulu = nom_table.lower() + ".dbc"
    donnees, origine = None, None
    if mpq_seul:
        chemins = [mpq_seul]
    else:
        chemins = (sorted(glob.glob(os.path.join(DATA, "*.MPQ")))
                   + sorted(glob.glob(os.path.join(DATA, "enUS",
                                                   "*.MPQ"))))
    for chemin in chemins:
        try:
            archive = MPQArchive(chemin, listfile=True)
            noms = [n.decode("latin-1") if isinstance(n, bytes) else n
                    for n in (archive.files or [])]
        except Exception:
            continue
        for n in noms:
            if n.lower().endswith(voulu):
                try:
                    d = archive.read_file(n)
                except Exception:
                    continue
                if d and d[:4] == b"WDBC":
                    donnees, origine = d, os.path.basename(chemin)
    if not donnees:
        print("! table introuvable :", nom_table)
        return 1

    nb, champs, taille, bloc = struct.unpack("<4I", donnees[4:20])
    debut = 20 + nb * taille
    chaines = donnees[debut:debut + bloc]
    n32 = min(champs, taille // 4)

    def texte(v):
        if v <= 0 or v >= len(chaines):
            return None
        fin = chaines.find(b"\0", v)
        try:
            t = chaines[v:fin].decode("utf-8")
        except UnicodeDecodeError:
            t = chaines[v:fin].decode("cp1252", "replace")
        return t

    # Une colonne est « texte » si une PART significative de ses valeurs
    # pointe sur une chaîne plausible qui COMMENCE à un début de chaîne
    # (l'octet précédent est \0) — écarte les entiers qui tombent par
    # hasard dans le bloc (piège Coldridge->Stratholme).
    votes = [0] * n32
    lignes_brutes = []
    for i in range(nb):
        base_l = 20 + i * taille
        vals = struct.unpack("<%dI" % n32,
                             donnees[base_l:base_l + n32 * 4])
        lignes_brutes.append(vals)
        for c in range(1, n32):
            v = vals[c]
            if 0 < v < len(chaines) \
                    and (v == 1 or chaines[v - 1:v] == b"\0"):
                t = texte(v)
                if t and len(t) >= 2 and RE_TEXTE.search(t):
                    votes[c] += 1

    seuil = max(3, nb // 20)
    colonnes = {c: votes[c] for c in range(1, n32) if votes[c] >= seuil}
    print("%s (%s) : %d lignes, %d champs (%d lus), colonnes texte : %s"
          % (nom_table, origine, nb, champs, n32,
             {c: round(v * 100 // nb) for c, v in colonnes.items()}))

    lignes = []
    for vals in lignes_brutes:
        ligne = {"id": vals[0]}
        for c in colonnes:
            v = vals[c]
            if 0 < v < len(chaines) and (v == 1
                                         or chaines[v - 1:v] == b"\0"):
                t = texte(v)
                if t:
                    ligne["c%d" % c] = t
        if len(ligne) > 1:
            lignes.append(ligne)

    sortie = os.path.join(BASE, "sources", "dbc",
                          nom_table.lower() + suffixe + ".json")
    with io.open(sortie, "w", encoding="utf-8") as f:
        json.dump({"colonnes": {str(c): v for c, v in colonnes.items()},
                   "lignes": lignes}, f, ensure_ascii=False, indent=1)
    print("écrit : %s (%d lignes avec texte)" % (sortie, len(lignes)))
    for ligne in lignes[:5]:
        print("  ex :", json.dumps(ligne, ensure_ascii=False)[:160])
    return 0


if __name__ == "__main__":
    sys.exit(extraire(sys.argv[1] if len(sys.argv) > 1
                      else "CharacterAdvancement",
                      sys.argv[2] if len(sys.argv) > 2 else None,
                      sys.argv[3] if len(sys.argv) > 3 else ""))
