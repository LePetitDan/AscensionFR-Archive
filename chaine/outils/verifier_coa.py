# -*- coding: utf-8 -*-
r"""Banc du CONSTRUCTEUR CoA — bloc 5 (28/07/2026).

« Être en base n'est pas s'afficher » : la matière CoA existe (3 949
talents, 3 931 avec du français en base — lot 14), mais le constructeur
est une fenêtre MAISON — ses cartes affichent des descriptions à nombres
CALCULÉS, posées par SetText. Le chemin d'affichage réel de l'addon est la
chaîne d'interception d'Epreuves.lua, qui pour une description passe par :

    AFR.DB.Epreuves[texte]  ou  DescriptionSort(texte)
      = AFR.SortParDescription (l'index FLOU du dresseur, Entraineur.lua)
        + AFR.TraduireTexteSort (l'aligneur du moteur, Modules/Sorts.lua)

Ce banc REJOUE ce chemin au moteur réel (lupa.lua51) pour CHAQUE talent de
coa_arbres.json : l'affichage client est SIMULÉ depuis le modèle anglais du
client (le simulateur du banc lot 14), puis la chaîne le traduit — ou pas.
C'est la mesure « ce que le constructeur affiche réellement », population
entière, et le compte des descriptions CoA qui s'affichent en français.

Trois témoins sont montrés avant/après, dont « Pure Shadow » (la capture
de Dan). Code retour : 0 si la part traduite ne RECULE pas sous le seuil
consigné dans ce fichier (SEUIL_TRADUITS) — un banc qui mord.

Usage : python outils/verifier_coa.py [--détail N]
"""
import io
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reparer_alignement_sorts as socle  # noqa: E402

BASE = socle.BASE
ADDON = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface"
         r"\AddOns\AscensionFR")
COA = os.path.join(BASE, "sources", "coa_arbres.json")
ASC = os.path.join(BASE, "sources", "dbc", "spells_Ascension.json")

# Le plancher : la part mesurée au premier passage du banc (bloc 5). S'il
# recule, quelque chose a cassé l'affichage CoA — le banc devient rouge.
SEUIL_TRADUITS = 0.60

TEMOINS = ("Pure Shadow", "Frost Nova", "Corruption")


def main():
    coa = json.load(io.open(COA, encoding="utf-8"))
    asc = json.load(io.open(ASC, encoding="utf-8"))

    # Les identifiants de talents du constructeur.
    ids = set()

    def ramasser(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in ("spellID", "spellId", "spell") and (
                        isinstance(v, int) or (isinstance(v, str)
                                               and v.isdigit())):
                    ids.add(int(v))
                else:
                    ramasser(v)
        elif isinstance(obj, list):
            for v in obj:
                ramasser(v)

    ramasser(coa)
    if not ids:
        # forme plate {id: fiche}
        for k in coa:
            if str(k).isdigit():
                ids.add(int(k))
    print("talents CoA : %d identifiants" % len(ids))

    t0 = time.time()
    lua = socle.charger_banc()
    # Entraineur (l'index flou) par-dessus le socle : c'est lui que la
    # fenêtre CoA consulte via AFR.SortParDescription.
    with io.open(os.path.join(ADDON, "Modules", "Entraineur.lua"),
                 encoding="utf-8") as f:
        lua.execute(f.read())
    lua.execute(r"""
        function MesurerCoA(id)
            local s = AscensionFR.DB.Sorts[id]
            if not (s and s.DE) then return "sans_modele" end
            local affiche = Simuler(s.DE)
            if string.len(affiche) <= 40 then return "court" end
            local fiche = AscensionFR.SortParDescription(affiche)
            if not fiche then
                return "hors_index"
            end
            if not (fiche.D and fiche.DE) then
                -- l'index connaît le sort mais son français a été PURGÉ
                -- (bloc 4 : faux appariement retiré) — anglais honnête en
                -- attendant le recomblement par le canal aura().
                return "sans_francais"
            end
            local fr = AscensionFR.TraduireTexteSort(fiche.D, fiche.DE,
                                                     affiche)
            if fr then return "traduit", affiche, fr end
            return "echec_alignement", affiche
        end
    """)
    g = lua.globals()

    compte = {}
    echantillons = []
    temoins_vus = []
    for sid in sorted(ids):
        r = g.MesurerCoA(sid)
        if isinstance(r, tuple):
            verdict = str(r[0])
        else:
            verdict = str(r)
        compte[verdict] = compte.get(verdict, 0) + 1
        nom = (asc.get(str(sid)) or {}).get("N") or ""
        if verdict == "traduit" and len(temoins_vus) < 3 \
                and (nom in TEMOINS or len(str(r[1])) > 80):
            temoins_vus.append((nom, str(r[1]), str(r[2])))
        elif verdict != "traduit" and len(echantillons) < 8:
            echantillons.append((sid, nom, verdict))

    total = sum(compte.values())
    traduits = compte.get("traduit", 0)
    print("mesure au moteur (%.1f s) :" % (time.time() - t0))
    for verdict in sorted(compte, key=lambda v: -compte[v]):
        print("  %-18s : %5d" % (verdict, compte[verdict]))
    part = traduits / max(1, total)
    print("PART TRADUITE À L'AFFICHAGE : %d/%d = %.1f %%"
          % (traduits, total, 100 * part))

    print()
    print("Témoins avant/après :")
    for nom, avant, apres in temoins_vus:
        print("  « %s »" % nom)
        print("    avant : %s" % avant[:110].replace("\r\n", " ⏎ "))
        print("    après : %s" % apres[:110].replace("\r\n", " ⏎ "))
    if not temoins_vus:
        print("  (aucun témoin traduit — voir échantillons d'échecs)")
    if echantillons:
        print()
        print("échantillon d'échecs :")
        for sid, nom, verdict in echantillons:
            print("  %s %r : %s" % (sid, nom[:30], verdict))

    if part < SEUIL_TRADUITS:
        print()
        print("SOUS LE PLANCHER (%.0f %%) — l'affichage CoA a reculé."
              % (100 * SEUIL_TRADUITS))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
