# -*- coding: utf-8 -*-
"""
AUDIT EXHAUSTIF : quels sorts du jeu s'affichent encore en anglais ?
====================================================================
(Demande de Dan du 23/07/2026 — « analyse tous les sorts existants et
vérifie les non traduits ».)

Trois sources croisées :
  1. DB_Sorts.lua — l'état RÉEL livré au jeu (N/D/DE par identifiant) ;
  2. le journal d'échecs d'alignement de l'addon (SavedVariables de Dan) —
     la vérité TERRAIN : des sorts affichés en jeu dont l'alignement a
     échoué, donc restés anglais À L'ÉCRAN malgré une traduction en base ;
  3. la base communautaire DB_SortsLignes (un sort couvert par elle est
     servi même si l'alignement classique échoue).

Classement de chaque entrée :
  - SANS_NOM         : même le nom n'est pas traduit ;
  - SANS_DESCRIPTION : D absent alors que DE existe (jamais traduit) ;
  - IDENTITE         : D == DE (translation refusée/ratée en amont) ;
  - RISQUE_MARQUEURS : D existe mais DE porte des @marqueurs et AUCUNE
                       variante communautaire ne couvre le sort — la
                       classe « Tempête vertueuse » : traduit en base,
                       anglais à l'écran ;
  - ECHEC_TERRAIN    : présent dans le journal d'échecs en jeu.

Sorties :
  - rapports/sorts_anglais.txt (comptes + listes)
  - a_traduire/sorts_sans_description.json (file pour l'usine)
Usage : python outils/auditer_sorts_anglais.py
"""
import io
import json
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
          r"\AscensionFR\DB")
JEU = r"D:\AscensionFR\WOW_Priv\resources\ascension-live"
RAPPORT = os.path.join(BASE, "rapports", "sorts_anglais.txt")
FILE_USINE = os.path.join(BASE, "a_traduire", "sorts_sans_description.json")

RE_ENTREE = re.compile(r'^DB\[(\d+)\]=\{(.*)\}\s*$')
RE_CHAMP = re.compile(r'(\w+)="((?:\\.|[^"\\])*)"')


def lire_db_sorts():
    entrees = {}
    with io.open(os.path.join(DB_DIR, "DB_Sorts.lua"),
                 encoding="utf-8") as f:
        for ligne in f:
            m = RE_ENTREE.match(ligne)
            if m:
                entrees[int(m.group(1))] = dict(
                    RE_CHAMP.findall(m.group(2)))
    return entrees


def lire_couverture_communaute():
    couverts = set()
    with io.open(os.path.join(DB_DIR, "DB_SortsLignes.lua"),
                 encoding="utf-8") as f:
        for ligne in f:
            m = re.match(r"^DB\[(\d+)\]=", ligne)
            if m:
                couverts.add(int(m.group(1)))
    return couverts


def lire_echecs_terrain():
    """Les identifiants notés par l'addon en jeu (S = sorts), tous comptes
    confondus. Lecture PRUDENTE du Lua de sauvegarde par lupa."""
    import lupa.lua51 as lupa_mod
    ids = set()
    compte_base = os.path.join(JEU, "WTF", "Account")
    if not os.path.isdir(compte_base):
        return ids
    for compte in os.listdir(compte_base):
        chemin = os.path.join(compte_base, compte, "SavedVariables",
                              "AscensionFR.lua")
        if not os.path.isfile(chemin):
            continue
        lua = lupa_mod.LuaRuntime()
        try:
            lua.execute(io.open(chemin, encoding="utf-8",
                                errors="replace").read())
            saved = lua.globals().AscensionFRSaved
            echecs = saved and saved["EchecsAlignement"]
            if not echecs:
                continue
            for cle in list(echecs.keys()):
                m = re.match(r"^S(%d+|\d+)$", str(cle))
                if m:
                    ids.add(int(m.group(1)))
        except Exception:
            continue
    return ids


def a_marqueurs(texte):
    return bool(re.search(r"@%a|@\a|@[a-z]", texte or ""))


def main():
    entrees = lire_db_sorts()
    couverts = lire_couverture_communaute()
    terrain = lire_echecs_terrain()
    print("entrées DB_Sorts :", len(entrees),
          "| couvertes par la communauté :", len(couverts),
          "| échecs terrain relevés :", len(terrain))

    sans_nom, sans_desc, identites, risque, deja_ok = [], [], [], [], 0
    for sid, e in sorted(entrees.items()):
        nom_fr, d, de = e.get("N"), e.get("D"), e.get("DE")
        if not nom_fr:
            sans_nom.append(sid)
        if de and not d:
            sans_desc.append(sid)
        elif d and de and d == de:
            identites.append(sid)
        elif d and de and a_marqueurs(de) and sid not in couverts:
            risque.append(sid)
        else:
            deja_ok += 1

    terrain_connus = sorted(t for t in terrain if t in entrees)
    terrain_inconnus = sorted(t for t in terrain if t not in entrees)

    os.makedirs(os.path.dirname(RAPPORT), exist_ok=True)
    with io.open(RAPPORT, "w", encoding="utf-8") as f:
        f.write("AUDIT DES SORTS ENCORE ANGLAIS — %d entrées\n\n"
                % len(entrees))
        for titre, liste in (
                ("SANS NOM TRADUIT", sans_nom),
                ("SANS DESCRIPTION (DE présent, D absent)", sans_desc),
                ("IDENTITÉ (D == DE)", identites),
                ("RISQUE MARQUEURS (classe « Tempête vertueuse »)",
                 risque),
                ("ÉCHECS TERRAIN (journal en jeu, connus de la base)",
                 terrain_connus),
                ("ÉCHECS TERRAIN (inconnus de la base !)",
                 terrain_inconnus)):
            f.write("== %s : %d\n" % (titre, len(liste)))
            for sid in liste[:400]:
                e = entrees.get(sid, {})
                f.write("   %d  %s\n" % (sid, e.get("N", "?")[:50]))
            f.write("\n")

    # File pour l'usine : les descriptions jamais traduites.
    file_usine = {}
    for sid in sans_desc:
        de = entrees[sid].get("DE")
        if de and de not in file_usine:
            file_usine[de] = ""
    os.makedirs(os.path.dirname(FILE_USINE), exist_ok=True)
    with io.open(FILE_USINE, "w", encoding="utf-8") as f:
        json.dump(file_usine, f, ensure_ascii=False, indent=1,
                  sort_keys=True)

    print("sans nom          :", len(sans_nom))
    print("sans description  :", len(sans_desc),
          "->", len(file_usine), "textes uniques vers l'usine")
    print("identités D==DE   :", len(identites))
    print("risque marqueurs  :", len(risque))
    print("échecs terrain    :", len(terrain_connus), "connus +",
          len(terrain_inconnus), "hors base")
    print("rapport :", RAPPORT)


if __name__ == "__main__":
    main()
