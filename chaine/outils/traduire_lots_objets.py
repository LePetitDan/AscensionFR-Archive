# -*- coding: utf-8 -*-
"""LE MOULIN des deux lots approuvés (22/07) — REPRENABLE à volonté.

Ordre d'impact : vanity (3,5k) -> noms d'objets (164k) -> descriptions
(24k). Google via traduire_gisement (glossaire WoW + protections),
sauvegarde tous les 200. Relancer reprend où il en était.

Usage : python outils/traduire_lots_objets.py
"""
import io
import json
import os
import sys
import threading
import time
from concurrent import futures

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from traduire_gisement import traduire  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARALLELE = 12   # 6 -> 10 -> 12 (22/07) : dernier cran raisonnable —
                 # au-delà, Google jette des requêtes (textes sautés,
                 # rattrapés à la relance grâce à la reprise)

# Le TOP des textes d'obtention Vanity, traduit MAIN (vu 50 000 fois,
# il mérite mieux que la machine). Posé d'office dans le réservoir.
MAIN_VANITY = {
    "Available on the Webstore":
        "Disponible sur la boutique en ligne",
    "Available from the Webstore":
        "Disponible sur la boutique en ligne",
    "Available from the Webstore.":
        "Disponible sur la boutique en ligne.",
    "Available from Tiraxis' Ethereal Bazaar":
        "Disponible au Bazar éthérien de Tiraxis",
    "Can be purchased from Cogsworth":
        "En vente chez Cogsworth",
    "Available on the Webstore or from Chromie for Tokens of Prestige":
        "Disponible sur la boutique en ligne ou auprès de Chromie"
        " contre des jetons de prestige",
    "Has a chance to drop from Azzar Faire Lucky Box":
        "Peut être obtenu dans une boîte chanceuse de la Foire d'Azzar",
    "Can be purchased from Mazoga Museda for Triumphant Raider Tokens":
        "En vente chez Mazoga Museda contre des jetons de raid"
        " triomphant",
    "Can be purchased from Purified Soul Traders for Purified Souls":
        "En vente chez les marchands d'âmes purifiées contre des âmes"
        " purifiées",
    "Translator's Progress Reward":
        "Récompense de progression du traducteur",
}


def charger(chemin, defaut):
    if os.path.exists(chemin):
        return json.load(io.open(chemin, encoding="utf-8"))
    return defaut


def sauver(chemin, donnees):
    with io.open(chemin, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=1,
                  sort_keys=True)


def moudre(nom, file_chemin, cache, cle, cache_chemin, conteneur):
    restants = [t for t in charger(file_chemin, [])
                if t not in conteneur]
    print("%s : %d à traduire" % (nom, len(restants)), flush=True)
    if not restants:
        return
    verrou = threading.Lock()
    fait = [0]
    debut = time.time()

    # LE REFUS À L'ADOPTION CÔTÉ OBJETS (bloc 7, 28/07/2026 — la vigie
    # était posée, Dan a vu la mesure : 1 019 valeurs sur-portées). Une
    # valeur française déjà portée par SEUIL_PORTEURS clés anglaises sans
    # parenté n'accepte plus de NOUVELLE clé : c'est la croissance goutte à
    # goutte d'une famille poison. Refus BRUYANT, compté et affiché.
    from noms_empoisonnes import SEUIL_PORTEURS, TOLERES, parente
    porteurs = {}
    for en_deja, fr_deja in conteneur.items():
        if isinstance(fr_deja, str) and fr_deja.strip():
            porteurs.setdefault(fr_deja.strip(), []).append(en_deja)
    refus = []

    def traiter(texte):
        try:
            fr = traduire(texte)
        except Exception:
            fr = None
        with verrou:
            fait[0] += 1
            if fr:
                cles = porteurs.get(fr.strip(), [])
                if (len(cles) >= SEUIL_PORTEURS
                        and fr.strip() not in TOLERES
                        and not parente(cles + [texte])):
                    refus.append((texte, fr))
                    fr = None
            if fr:
                porteurs.setdefault(fr.strip(), []).append(texte)
                conteneur[texte] = fr
            if fait[0] % 200 == 0:
                sauver(cache_chemin, cache)
                vitesse = fait[0] / max(time.time() - debut, 1)
                print("  %s : %d/%d (%.1f/s, ~%d min restantes)"
                      % (nom, fait[0], len(restants), vitesse,
                         (len(restants) - fait[0]) / max(vitesse, 0.1)
                         / 60), flush=True)

    with futures.ThreadPoolExecutor(max_workers=PARALLELE) as pool:
        list(pool.map(traiter, restants))
    sauver(cache_chemin, cache)
    print("%s : terminé (%d traduits)" % (nom, fait[0]), flush=True)
    if refus:
        print("%s : BARRIÈRE DES PORTEURS — %d adoption(s) refusée(s) :"
              % (nom, len(refus)), flush=True)
        for texte, fr in refus[:10]:
            print("   %r -> %r (valeur déjà sur-portée)"
                  % (texte[:40], fr[:40]), flush=True)


def main():
    at = os.path.join(BASE, "a_traduire")
    tr = os.path.join(BASE, "traductions")

    vanity_chemin = os.path.join(tr, "vanity_obtention.json")
    vanity = charger(vanity_chemin, {"paires": {}})
    for en, fr in MAIN_VANITY.items():
        vanity["paires"].setdefault(en, fr)
    sauver(vanity_chemin, vanity)
    print("top vanity main :", len(MAIN_VANITY), "paires posées",
          flush=True)
    moudre("vanity", os.path.join(at, "vanity.json"),
           vanity, "paires", vanity_chemin, vanity["paires"])

    objets_chemin = os.path.join(tr, "objets_dbc.json")
    objets = charger(objets_chemin, {"noms": {}, "descriptions": {}})
    moudre("noms d'objets", os.path.join(at, "objets_dbc_noms.json"),
           objets, "noms", objets_chemin, objets["noms"])
    moudre("descriptions d'objets",
           os.path.join(at, "objets_dbc_descriptions.json"),
           objets, "descriptions", objets_chemin,
           objets["descriptions"])
    print("MOULIN TERMINÉ.", flush=True)


if __name__ == "__main__":
    main()
