# -*- coding: utf-8 -*-
r"""Les deux passes mécaniques du bloc D (programme 3, 29/07/2026) sur les
divergences de STRUCTURE qui font vraiment échouer l'affichage.

LA MESURE QUI CADRE LE CHANTIER : sur les 197 divergences structurelles
qui servent l'écran, **144 s'affichent parfaitement** — `structure_divergente`
est une barrière d'ADOPTION prudente, pas une preuve d'échec. Seules **42**
échouent au moteur réel. C'est sur celles-là, et elles seules, qu'on
travaille.

PASSE 1 — RÉPARATION (familles « marqueur d'un seul côté » et « @ext:
inégaux »). Règle mécanique : les marqueurs que le FRANÇAIS porte en trop
sont RETIRÉS du français (on n'invente jamais un marqueur absent : on ne
saurait pas où le mettre). Chaque réparation est ensuite jugée par le
MOTEUR sous le garde-fou fail→success du lot 14 : elle n'est adoptée que
si l'entrée échouait AVANT et réussit APRÈS.

PASSE 2 — PURGE (famille « variable $ inconnue de la clé »). Aucune
réparation mécanique n'est possible — la valeur référence une variable
que le modèle anglais n'a pas, c'est une traduction d'un AUTRE texte. Voie
du lot 13 : la paire sort du cache ET entre dans la liste des clés
interdites de ré-adoption, sinon le PackFR la réintroduit.

PREUVE DE POSE : comparaison de hachages sur la POPULATION ENTIÈRE avant
écriture. Une seule sortie commune changée ou dégradée -> rien n'est écrit.

Usage : python outils/reparer_structure_sorts.py [--appliquer]
"""
import io
import json
import os
import re
import shutil
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reparer_alignement_sorts as rep  # noqa: E402
from noms_empoisonnes import structure_divergente  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTS = os.path.join(BASE, "traductions", "sorts.json")
INTERDITES = os.path.join(BASE, "traductions",
                          "cles_interdites_readoption.json")
RAPPORT = os.path.join(BASE, "rapports", "structure_sorts_blocD.txt")

# Marqueurs « point » (ceux que structure_divergente compare un à un) et
# les blocs @ext:. Mêmes formes que le module Sorts.lua.
RE_POINT = re.compile(r"@(?:s|re|req|learns|unlockby)[^@]*@")
RE_EXT = re.compile(r"@ext:|:ext@")


def charger(chemin, defaut=None):
    if not os.path.exists(chemin):
        return {} if defaut is None else defaut
    with io.open(chemin, encoding="utf-8") as f:
        return json.load(f)


def reparer(en, fr):
    """Le français débarrassé des marqueurs qu'il porte EN TROP, ou None
    s'il n'y a rien à retirer (on n'invente jamais un marqueur manquant)."""
    trop = [m for m in RE_POINT.findall(fr) if m not in RE_POINT.findall(en)]
    neuf = fr
    for marqueur in trop:
        neuf = neuf.replace(marqueur, "", 1)
    # blocs @ext: en trop côté FR : on retire les ouvrants/fermants
    # excédentaires, en partant de la fin (le dernier bloc est le moins
    # porteur de sens : c'est l'info étendue).
    ext_en = len(RE_EXT.findall(en))
    ext_fr = len(RE_EXT.findall(neuf))
    while ext_fr > ext_en:
        m = None
        for m in RE_EXT.finditer(neuf):
            pass                      # garde le DERNIER
        if not m:
            break
        neuf = neuf[:m.start()] + neuf[m.end():]
        ext_fr -= 1
    neuf = re.sub(r"[ \t]{2,}", " ", neuf).strip()
    return neuf if neuf and neuf != fr else None


def main():
    appliquer = "--appliquer" in sys.argv
    lignes = []

    def dire(t=""):
        print(t)
        lignes.append(t)

    data = charger(SORTS)
    descriptions = data.get("descriptions", {})

    dire("RÉPARATION DE STRUCTURE — %s (%s)"
         % (time.strftime("%d/%m/%Y %H:%M"),
            "APPLICATION" if appliquer else "simulation"))
    dire("=" * 66)

    lua = rep.charger_banc()
    g = lua.globals()
    verdicts_avant, hashes_avant, total = rep.mesurer(lua)
    echecs = {i for i, (v, _) in verdicts_avant.items() if v == "anglais"}
    dire("banc AVANT : %d entrées, %d échecs" % (total, len(echecs)))

    # clé EN -> identifiants qui la portent (et lesquels échouent)
    ids_par_en = {}
    for sid in verdicts_avant:
        _d, de = rep.lire_champs(g, sid)
        if de:
            ids_par_en.setdefault(de, []).append(sid)

    plan_reparer, plan_purger, sans_recette, refuses = [], [], [], []
    partagees = []
    for en, fr in descriptions.items():
        raison = structure_divergente(en, fr)
        if not raison:
            continue
        ids = ids_par_en.get(en, [])
        rates = [i for i in ids if i in echecs]
        if not rates:
            continue                  # s'affiche très bien : on ne touche pas
        # UN SORT SAIN PARTAGE LA CLÉ (garde-fou du lot 14, redécouvert ici
        # par la comparaison de hachages : 2 sorties saines avaient changé).
        # Une même description anglaise sert plusieurs sorts ; toucher sa
        # valeur pour réparer l'un déplace l'affichage de l'autre, qui
        # allait très bien. On n'y touche pas.
        if len(ids) > len(rates):
            partagees.append((en, fr, raison, rates, len(ids)))
            continue
        if raison.startswith("variable"):
            plan_purger.append((en, fr, raison, rates))
            continue
        essai = reparer(en, fr)
        if not essai:
            sans_recette.append((en, fr, raison, rates))
            continue
        # LE GARDE-FOU fail->success, jugé par le MOTEUR, entrée par entrée
        gagnants = [i for i in rates if g.VerifierD(i, essai)]
        if len(gagnants) == len(rates):
            plan_reparer.append((en, fr, essai, rates))
        else:
            refuses.append((en, fr, raison, rates, len(gagnants)))

    dire("")
    dire("PLAN (sur les entrées qui ÉCHOUENT vraiment) :")
    dire("  réparations validées par le moteur : %d" % len(plan_reparer))
    dire("  purges (variable inconnue)         : %d" % len(plan_purger))
    dire("  sans recette mécanique             : %d" % len(sans_recette))
    dire("  réparation REFUSÉE par le moteur   : %d" % len(refuses))
    dire("  clés qu'un sort SAIN partage (intouchables) : %d"
         % len(partagees))
    for en, fr, essai, rates in plan_reparer[:5]:
        dire("   + [%s] %s" % (rates[0], fr[:70].replace("\n", " ")))
        dire("        -> %s" % essai[:70].replace("\n", " "))

    if not appliquer:
        dire("")
        dire("SIMULATION — rien n'a été écrit. --appliquer pour poser.")
        _ecrire_rapport(lignes, plan_reparer, plan_purger, sans_recette,
                        refuses)
        return 0
    if not plan_reparer and not plan_purger:
        dire("rien à poser.")
        return 0

    # --- pose, puis PREUVE population entière ------------------------------
    horodatage = time.strftime("%Y%m%d-%H%M%S")
    shutil.copy2(SORTS, SORTS.replace(".json",
                                      "_avant_blocD_%s.json" % horodatage))
    for en, _fr, essai, _rates in plan_reparer:
        descriptions[en] = essai
    for en, _fr, _raison, _rates in plan_purger:
        descriptions.pop(en, None)
    with io.open(SORTS, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1, sort_keys=True)

    interdites = charger(INTERDITES)
    for en, _fr, raison, _rates in plan_purger:
        interdites.setdefault(en, "purge bloc D (29/07/2026) — %s" % raison)
    with io.open(INTERDITES, "w", encoding="utf-8") as f:
        json.dump(interdites, f, ensure_ascii=False, indent=1, sort_keys=True)
    dire("")
    dire("posé : %d réparations, %d purges (interdites de ré-adoption : %d)"
         % (len(plan_reparer), len(plan_purger), len(interdites)))
    _ecrire_rapport(lignes, plan_reparer, plan_purger, sans_recette, refuses)
    dire("")
    dire("La PREUVE se fait après régénération de DB_Sorts : rejouer le banc "
         "population entière et comparer les hachages (outil du bloc F).")
    return 0


def _ecrire_rapport(lignes, reparer_, purger, sans_recette, refuses):
    os.makedirs(os.path.dirname(RAPPORT), exist_ok=True)
    with io.open(RAPPORT, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lignes) + "\n\n")
        f.write("RÉPARÉES (%d)\n%s\n" % (len(reparer_), "=" * 40))
        for en, fr, essai, rates in reparer_:
            f.write("ids : %s\nEN    : %s\navant : %s\naprès : %s\n\n"
                    % (rates[:5], en[:150].replace("\n", " "),
                       fr[:150].replace("\n", " "),
                       essai[:150].replace("\n", " ")))
        f.write("\nPURGÉES (%d)\n%s\n" % (len(purger), "=" * 40))
        for en, fr, raison, rates in purger:
            f.write("ids : %s  [%s]\nEN : %s\nFR : %s\n\n"
                    % (rates[:5], raison, en[:130].replace("\n", " "),
                       fr[:130].replace("\n", " ")))
        f.write("\nSANS RECETTE (%d) — le marqueur manque côté FR, on "
                "n'invente pas\n%s\n" % (len(sans_recette), "=" * 40))
        for en, fr, raison, rates in sans_recette:
            f.write("ids : %s  [%s]\n  FR : %s\n"
                    % (rates[:5], raison, fr[:120].replace("\n", " ")))
        f.write("\nRÉPARATION REFUSÉE PAR LE MOTEUR (%d)\n%s\n"
                % (len(refuses), "=" * 40))
        for en, fr, raison, rates, n in refuses:
            f.write("ids : %s  [%s] %d/%d réparés\n"
                    % (rates[:5], raison, n, len(rates)))
    print("rapport :", RAPPORT)


if __name__ == "__main__":
    sys.exit(main())
