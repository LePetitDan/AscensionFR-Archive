# -*- coding: utf-8 -*-
"""moissonner_packfr.py — vide le PackFR de tout son texte utile (21/07).

Pour chaque table : lit la version du PACK (archives SANS liste interne ->
listfile=False) et la version ACTUELLE du client (archives du jeu), détecte
EMPIRIQUEMENT les colonnes de texte des deux côtés (le pack a des décalages
de colonnes variables — +3 sur Achievement, vérifié), puis apparie par ID :
anglais actuel -> français du pack. Doublons divergents neutralisés,
identités et anglais résiduel écartés.

Sortie : traductions/packfr_interface.json { famille: { EN: FR } },
consommé par traduire_epreuves.py (affichage, jamais d'écriture de
globales). Usage : python outils/moissonner_packfr.py
"""
import glob
import io
import json
import os
import re
import struct

from mpyq import MPQArchive

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(BASE, "Ajouter par Dan", "PackFR")
DATA = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Data"
SORTIE = os.path.join(BASE, "traductions", "packfr_interface.json")

TABLES = [
    # (fichier dbc, archive du pack, famille)
    ("TalentTab.dbc", "patch-Z-frFR-2.MPQ", "arbres"),
    ("CharTitles.dbc", "patch-Z-frFR-2.MPQ", "titres"),
    ("Faction.dbc", "patch-Z-frFR-2.MPQ", "factions"),
    ("SkillLine.dbc", "patch-Z-frFR-2.MPQ", "competences"),
    ("CreatureFamily.dbc", "patch-Z-frFR-2.MPQ", "familles_familiers"),
    ("CreatureType.dbc", "patch-Z-frFR-2.MPQ", "types_creatures"),
    ("ItemSubClass.dbc", "patch-Z-frFR-2.MPQ", "sous_classes_objets"),
    ("Map.dbc", "patch-Z-frFR-2.MPQ", "cartes"),
    ("WorldMapArea.dbc", "patch-Z-frFR-2.MPQ", "zones_carte"),
    ("BattlemasterList.dbc", "patch-Z-frFR-2.MPQ", "champs_bataille"),
    ("LFGDungeons.dbc", "patch-Z-frFR-2.MPQ", "donjons"),
    ("MailTemplate.dbc", "patch-Z-frFR-2.MPQ", "courriers"),
    ("QuestSort.dbc", "patch-Z-frFR-2.MPQ", "categories_quetes"),
    ("QuestInfo.dbc", "patch-Z-frFR-2.MPQ", "types_quetes"),
    ("ChrClasses.dbc", "patch-Z-frFR-2.MPQ", "classes"),
    ("ChrRaces.dbc", "patch-Z-frFR-2.MPQ", "races"),
    ("Achievement_Criteria.dbc", "patch-Z-frFR-2.MPQ", "criteres"),
    ("MysticEnchant.dbc", "patch-Z-frFR-2.MPQ", "enchants_re"),
    ("SpellItemEnchantment.dbc", "patch-Z-frFR-3.MPQ", "enchantements"),
    ("SpellShapeshiftForm.dbc", "patch-Z-frFR-3.MPQ", "formes"),
]

RE_ANGLAIS = re.compile(
    r"\b(the|of|and|your|you|to|with|slain|kill|defeat|complete|reach"
    r"|obtain|win|earn)\b", re.I)


def lire_table(donnees):
    """{id: {col: texte}} + nb de champs, colonnes détectées empiriquement."""
    if not donnees or donnees[:4] != b"WDBC":
        return {}, 0
    nb, champs, taille, bloc = struct.unpack("<4I", donnees[4:20])
    debut = 20 + nb * taille
    chaines = donnees[debut:debut + bloc]
    valides = {0}
    for i, o in enumerate(chaines):
        if o == 0:
            valides.add(i + 1)

    def texte(v):
        if v <= 0 or v >= len(chaines):
            return ""
        fin = chaines.find(b"\0", v)
        brut = chaines[v:fin]
        try:
            return brut.decode("utf-8")
        except UnicodeDecodeError:
            return brut.decode("cp1252", "replace")

    table = {}
    for i in range(nb):
        base = 20 + i * taille
        vals = struct.unpack("<%dI" % champs, donnees[base:base + taille])
        colonnes = {}
        for c in range(1, champs):
            v = vals[c]
            if v and v in valides:
                s = texte(v).strip()
                if len(s) > 1:
                    colonnes[c] = s
        if colonnes:
            table[vals[0]] = colonnes
    return table, champs


def table_du_jeu(nom_dbc):
    """Version ACTUELLE : union des archives du jeu, patchs par-dessus."""
    fusion, champs = {}, 0
    chemins = (sorted(glob.glob(os.path.join(DATA, "enUS", "*.MPQ")))
               + sorted(glob.glob(os.path.join(DATA, "*.MPQ"))))
    for chemin in chemins:
        try:
            archive = MPQArchive(chemin, listfile=True)
            noms = archive.files or []
        except Exception:
            continue
        for nom in noms:
            if isinstance(nom, bytes):
                nom = nom.decode("latin-1")
            if nom.lower().endswith("\\" + nom_dbc.lower()) \
                    or nom.lower() == ("dbfilesclient\\"
                                       + nom_dbc.lower()):
                try:
                    d = archive.read_file(nom)
                except Exception:
                    continue
                t, ch = lire_table(d)
                if t:
                    fusion.update(t)
                    champs = ch
    return fusion, champs


def table_du_pack(nom_dbc, archive_pack):
    try:
        d = MPQArchive(os.path.join(PACK, archive_pack),
                       listfile=False).read_file(
            "DBFilesClient\\" + nom_dbc)
    except Exception:
        return {}, 0
    return lire_table(d)


def main():
    resultat = {}
    for nom_dbc, archive_pack, famille in TABLES:
        actuel, _ = table_du_jeu(nom_dbc)
        pack, _ = table_du_pack(nom_dbc, archive_pack)
        if not actuel or not pack:
            print("%-28s : actuel %d / pack %d — passé"
                  % (nom_dbc, len(actuel), len(pack)))
            continue
        paires, divergents = {}, set()
        for ident, cols_en in actuel.items():
            cols_fr = pack.get(ident)
            if not cols_fr:
                continue
            for c, en in cols_en.items():
                # même colonne d'abord, puis les décalages vus (+2, +3)
                fr = ""
                for dc in (0, 2, 3):
                    cand = (cols_fr.get(c + dc) or "").replace(
                        chr(160), " ").strip()
                    if cand and cand != en:
                        fr = cand
                        break
                if not fr or fr == en or len(en) < 3:
                    continue
                if RE_ANGLAIS.search(fr):
                    continue          # anglais résiduel chez eux
                if en in divergents:
                    continue
                deja = paires.get(en)
                if deja is None:
                    paires[en] = fr
                elif deja != fr:
                    del paires[en]
                    divergents.add(en)
        if paires:
            resultat[famille] = paires
        print("%-28s : %5d paires (divergents %d)"
              % (nom_dbc, len(paires), len(divergents)))

    io.open(SORTIE, "w", encoding="utf-8").write(
        json.dumps(resultat, ensure_ascii=False, indent=1, sort_keys=True))
    total = sum(len(p) for p in resultat.values())
    print("\nécrit : %s (%d paires en %d familles)"
          % (os.path.basename(SORTIE), total, len(resultat)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
