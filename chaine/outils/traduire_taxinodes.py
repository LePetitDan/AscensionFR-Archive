# -*- coding: utf-8 -*-
"""
Points de vol (TaxiNodes) : le français OFFICIEL par jointure d'ID.

L'addon traduit déjà l'infobulle des nœuds de vol via DB.Zones (Plaques.lua).
Il lui manque juste les NOMS. On les prend par jointure d'ID :
  - EN : TaxiNodes.dbc du client (locale-enUS.MPQ, champ 5)
  - FR : TaxiNodes.dbc officiel (sources/patch-frFR-3.MPQ, champ 7 = frFR)

Sortie : traductions/taxinodes.json { EN: FR } — noms COMPLETS (« Stormwind,
Elwynn ») ET morceaux (« Stormwind »->« Hurlevent »), pour couvrir les deux
branches du crochet de vol. traduire_zones.py le fusionne dans DB_Zones.lua.

  python outils/traduire_taxinodes.py
"""
import json, os, struct, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN_MPQ = os.path.join(BASE, "..", "WOW_Priv", "resources", "ascension-live", "Data",
                      "enUS", "locale-enUS.MPQ")
FR_MPQ = os.path.join(BASE, "sources", "patch-frFR-3.MPQ")
SORTIE = os.path.join(BASE, "traductions", "taxinodes.json")


def lire_dbc_champ(mpq, fichier, champ):
    """id -> chaîne du champ <champ> (offset dans le bloc de texte)."""
    from mpyq import MPQArchive
    d = MPQArchive(mpq).read_file(fichier)
    if not d or d[:4] != b"WDBC":
        return {}
    nb, nch, taille, bloc = struct.unpack_from("<4I", d, 4)
    debut = 20 + nb * taille
    blocbytes = d[debut:debut + bloc]

    def chaine(off):
        if off <= 0 or off >= len(blocbytes):
            return ""
        fin = blocbytes.find(b"\0", off)
        return blocbytes[off:fin].decode("utf-8", "replace")

    out = {}
    for i in range(nb):
        base = 20 + i * taille
        rid = struct.unpack_from("<I", d, base)[0]
        off = struct.unpack_from("<I", d, base + champ * 4)[0]
        out[rid] = chaine(off)
    return out


def main():
    en = lire_dbc_champ(EN_MPQ, "DBFilesClient\\TaxiNodes.dbc", 5)
    fr = lire_dbc_champ(FR_MPQ, "DBFilesClient\\TaxiNodes.dbc", 7)
    paires = {}
    n_complets = n_morceaux = 0
    for rid, e in en.items():
        f = fr.get(rid)
        if not e or not f or not e.strip() or not f.strip():
            continue
        e, f = e.strip(), f.strip()
        if e != f and e not in paires:
            paires[e] = f
            n_complets += 1
        # morceaux « ville, zone » -> pour la 1re branche du crochet de vol
        pe, pf = e.split(", "), f.split(", ")
        if len(pe) == len(pf) and len(pe) > 1:
            for me, mf in zip(pe, pf):
                me, mf = me.strip(), mf.strip()
                if me and mf and me != mf and me not in paires:
                    paires[me] = mf
                    n_morceaux += 1

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as g:
        json.dump(paires, g, ensure_ascii=False, indent=1, sort_keys=True)

    print("points de vol EN :", len(en), "| FR :", len(fr))
    print("paires écrites   :", len(paires),
          "(%d complètes + %d morceaux)" % (n_complets, n_morceaux))
    print("sortie :", SORTIE)
    print("\n--- exemples ---")
    for e in list(paires)[:8]:
        print("  %-40s -> %s" % (e[:38], paires[e]))


if __name__ == "__main__":
    main()
