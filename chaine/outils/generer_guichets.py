# -*- coding: utf-8 -*-
r"""Génère DB\DB_Guichets.lua : le pont TEXTE ANGLAIS -> FRANÇAIS des
guichets du monde (bloc H, 29/07/2026) — trois gisements officiels :

  - le COURRIER : MailTemplate.dbc (sujets + corps), enUS du client vivant
    x frFR du PackFR, joints par ID — 170+ modèles qui restaient anglais
    faute de module ;
  - les FACTIONS : Faction.dbc (noms + descriptions du panneau de
    réputation), même jointure ;
  - les FÊTES : HolidayNames/Descriptions.dbc — le PackFR ne les porte PAS
    (vérifié sur ses 5 archives : l'audit des ressources se trompait) ;
    leur français vient de traductions/fetes.json, NOTRE chaîne.

Les monnaies n'ont pas de gisement (CurrencyTypes.dbc sans texte, vérifié
à l'audit) : leurs noms viennent des OBJETS, déjà couverts — c'est le
module Guichets.lua qui les repeint via DB.ObjetsNoms.

Prérequis (mise_a_jour les rafraîchit via extraire_dbc_texte) :
  sources/dbc/mailtemplate(.json|_frfr.json), faction(...), holidaynames,
  holidaydescriptions.
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generateur_db import polir  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DBC = os.path.join(BASE, "sources", "dbc")
SORTIE = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface"
          r"\AddOns\AscensionFR\DB\DB_Guichets.lua")

# (table EN, table FR, [(colonne EN, colonne FR), ...])
JOINTURES = [
    ("mailtemplate", "mailtemplate_frfr", [("c1", "c3"), ("c18", "c20")]),
    ("faction", "faction_frfr", [("c19", "c25"), ("c36", "c42")]),
]


# LES LIBELLÉS MAISON D'ASCENSION (bloc A du programme 4, 29/07/2026).
# Leur panneau de réputation est une fenêtre à eux : quelques en-têtes n'ont
# AUCUNE source officielle — « Allegiance » n'existe ni dans Faction.dbc
# (396 lignes vérifiées), ni dans les GlobalStrings, ni dans le FrameXML
# extrait. Ce n'est donc pas un texte que Blizzard a déjà traduit : la
# doctrine « ne crée pas d'entrée pour du frFR existant » ne s'y applique
# pas, et il faut bien l'écrire quelque part. Ici, en clair, avec la
# raison — plutôt que dans traductions/, où il se mélangerait au gisement
# de la traduction automatique.
MAISON = {
    "Allegiance": "Allégeance",
}


def charger(nom):
    chemin = os.path.join(DBC, nom + ".json")
    if not os.path.exists(chemin):
        return None
    with io.open(chemin, encoding="utf-8") as f:
        return json.load(f)


def echapper(s):
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return s.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")


def main():
    # Ré-extrait les tables ANGLAISES du client à chaque passage (le
    # dernier patch gagne — après une mise à jour d'Ascension, c'est ici
    # que le neuf entre). Le frFR, lui, est STATIQUE (PackFR) : extrait
    # une fois, réutilisé.
    import extraire_dbc_texte as ex
    for table in ("MailTemplate", "Faction", "HolidayNames",
                  "HolidayDescriptions"):
        ex.extraire(table)
    mpq_fr = os.path.join(BASE, "sources", "patch-frFR-3.MPQ")
    for table in ("MailTemplate", "Faction"):
        if not os.path.exists(os.path.join(
                DBC, table.lower() + "_frfr.json")):
            ex.extraire(table, mpq_seul=mpq_fr, suffixe="_frFR")

    paires = {}

    def poser(en, fr, origine):
        en = (en or "").strip()
        fr = (fr or "").strip()
        if not en or not fr or en == fr:
            return
        fr = polir(fr, anglais=en)
        deja = paires.get(en)
        if deja is not None and deja[0] != fr:
            # même texte anglais, deux français : le premier gisement garde
            # la main (courrier avant factions), on le dit
            print("  divergence ignorée [%s] %r" % (origine, en[:50]))
            return
        paires[en] = (fr, origine)

    for nom_en, nom_fr, colonnes in JOINTURES:
        t_en, t_fr = charger(nom_en), charger(nom_fr)
        if not t_en or not t_fr:
            raise SystemExit("table absente : %s / %s — lancer "
                             "extraire_dbc_texte d'abord" % (nom_en, nom_fr))
        fr_par_id = {l["id"]: l for l in t_fr["lignes"]}
        avant = len(paires)
        for ligne in t_en["lignes"]:
            jumelle = fr_par_id.get(ligne["id"])
            if not jumelle:
                continue
            for c_en, c_fr in colonnes:
                poser(ligne.get(c_en), jumelle.get(c_fr), nom_en)
        print("%-14s : %d paires" % (nom_en, len(paires) - avant))

    # les fêtes : notre chaîne (traductions/fetes.json)
    chemin_fetes = os.path.join(BASE, "traductions", "fetes.json")
    n_fetes = 0
    if os.path.exists(chemin_fetes):
        fetes = json.load(io.open(chemin_fetes, encoding="utf-8"))
        avant = len(paires)
        for section in ("noms", "descriptions"):
            for en, fr in fetes.get(section, {}).items():
                poser(en, fr, "fetes")
        n_fetes = len(paires) - avant
        print("%-14s : %d paires" % ("fetes", n_fetes))
    else:
        print("(traductions/fetes.json absent — fêtes non branchées)")

    avant = len(paires)
    for en, fr in MAISON.items():
        poser(en, fr, "maison")
    print("%-14s : %d paires" % ("maison", len(paires) - avant))

    if len(paires) < 400:
        raise SystemExit("seulement %d paires — gisement anormalement "
                         "maigre, rien n'est écrit" % len(paires))

    lignes = [
        "-- Fichier GÉNÉRÉ par outils/generer_guichets.py — ne pas éditer",
        "-- à la main. Pont texte EN -> FR des guichets : courrier",
        "-- (MailTemplate.dbc), factions (Faction.dbc), fêtes (Holiday*.dbc",
        "-- x traductions/fetes.json). Consommé par Modules\\Guichets.lua.",
        "local T = AscensionFR.DB.Guichets",
    ]
    for en in sorted(paires):
        lignes.append('T["%s"]="%s"' % (echapper(en),
                                        echapper(paires[en][0])))
    contenu = "\n".join(lignes) + "\n"
    import lupa.lua51 as lupa_mod
    lupa_mod.LuaRuntime().compile(contenu)
    with io.open(SORTIE, "w", encoding="utf-8", newline="\n") as f:
        f.write(contenu)
    print("DB_Guichets.lua : %d paires (compile lua51 OK)" % len(paires))
    return 0


if __name__ == "__main__":
    sys.exit(main())
