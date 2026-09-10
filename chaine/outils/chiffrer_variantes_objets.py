# -*- coding: utf-8 -*-
r"""CHIFFRE (sans rien purger) les faux appariements d'objets par VARIANTES
DE PALIER — la 3ᵉ perle du bloc E (programme 3, 29/07/2026).

Le cas de départ : « Jambières de magistère » posé sur des TORSES
« @Mythique 6/7@ ». Le moulin des objets joint par TEXTE ; quand plusieurs
paliers d'un même objet portent des noms anglais différents mais voisins,
un français peut se poser sur le mauvais. Ces familles-là comptent 2 à 4
porteurs — elles passent DESSOUS le seuil de la vigie (5), qui ne les voit
donc jamais.

Ce que l'outil mesure, et rien d'autre :
  - combien de FAMILLES (une valeur française, plusieurs identifiants aux
    noms anglais différents et sans parenté) ;
  - combien d'ENTRÉES au total ;
  - combien SERVENT l'écran (présentes dans DB_Objets.lua livrée).

Aucune écriture. Le rapport sert à décider si ça mérite sa propre passe.
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from noms_empoisonnes import objets_suspects, SEUIL_PORTEURS  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DBDIR = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface"
         r"\AddOns\AscensionFR\DB")
RAPPORT = os.path.join(BASE, "rapports", "variantes_objets_blocE.txt")


def charger(chemin):
    if not os.path.exists(chemin):
        return {}
    with io.open(chemin, encoding="utf-8") as f:
        return json.load(f)


def objets_livres():
    """{id: nom français} tels qu'ils partent chez les joueurs (base
    paresseuse : [id]={…} dans des seaux)."""
    chemin = os.path.join(DBDIR, "DB_Objets.lua")
    brut = io.open(chemin, encoding="utf-8", errors="replace").read()
    rendu = {}
    for m in re.finditer(r"[\[,]\[(\d+)\]=(\{(?:[^{}]|\{[^{}]*\})*\})", brut):
        n = re.search(r'(?:^|[{,])N="((?:\\.|[^"\\])*)"', m.group(2))
        if n:
            rendu[m.group(1)] = (n.group(1).replace('\\"', '"')
                                 .replace("\\\\", "\\"))
    return rendu


def main():
    livres = objets_livres()
    print("objets livrés avec un nom : %d" % len(livres))

    anglais = {}
    for iid, fiche in charger(os.path.join(BASE, "sources", "dbc",
                                           "itemaddon_par_id.json")).items():
        if isinstance(fiche, dict) and fiche.get("N"):
            anglais[iid] = fiche["N"]
    dossier = os.path.join(BASE, "extraits")
    if os.path.isdir(dossier):
        for royaume in sorted(os.listdir(dossier)):
            chemin = os.path.join(dossier, royaume, "objets.json")
            if os.path.isfile(chemin):
                for iid, o in charger(chemin).items():
                    if o.get("Name"):
                        anglais.setdefault(iid, o["Name"])
    print("noms anglais connus       : %d" % len(anglais))

    objets = {iid: {"N": n} for iid, n in livres.items()}
    grosses = objets_suspects(objets, anglais, seuil=SEUIL_PORTEURS)
    petites_toutes = objets_suspects(objets, anglais, seuil=2)
    petites = {v: ids for v, ids in petites_toutes.items()
               if v not in grosses}

    n_entrees = sum(len(v) for v in petites.values())
    # La mesure part de DB_Objets.lua LIVRÉE : toutes ces entrées servent
    # donc l'écran par construction. On le dit ainsi plutôt que d'afficher
    # un « dont » qui laisserait croire à un filtre.
    servies = n_entrees
    print()
    print("FAMILLES SOUS LE SEUIL (2 à %d porteurs) : %d"
          % (SEUIL_PORTEURS - 1, len(petites)))
    print("  entrées concernées                    : %d" % n_entrees)
    print("  (mesurées sur la base LIVRÉE : toutes servent l'écran)")
    print("  (au-dessus du seuil, vues par la vigie : %d familles)"
          % len(grosses))
    from collections import Counter
    print("  taille des familles :",
          dict(sorted(Counter(len(v) for v in petites.values()).items())))

    with io.open(RAPPORT, "w", encoding="utf-8", newline="") as f:
        f.write("BLOC E, perle 3 — faux appariements d'objets par variantes "
                "de palier.\nMESURE SEULE : rien n'est purgé.\n\n"
                "familles sous le seuil de la vigie : %d\nentrées : %d "
                "(servent l'écran : %d)\n\n" % (len(petites), n_entrees,
                                                servies))
        for valeur, ids in sorted(petites.items(),
                                  key=lambda kv: -len(kv[1]))[:120]:
            f.write("%d× %s\n" % (len(ids), valeur))
            for i in ids[:6]:
                f.write("     [%s] EN=%s\n" % (i, anglais.get(i, "?")))
            f.write("\n")
    print("\nrapport :", RAPPORT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
