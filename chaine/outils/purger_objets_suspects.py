# -*- coding: utf-8 -*-
r"""Purge des noms d'OBJETS sur-portés (bloc 7 — méthode des lots 9-11).

LA MESURE VIENT DE LA GÉNÉRATION, pas d'une re-dérivation : la vigie de
generateur_db écrit désormais rapports/porteurs_objets.json — la liste
COMPLÈTE des minoritaires (une valeur française posée sur des identifiants
dont l'anglais n'est pas le dominant de la famille), mesurée sur l'espace
fusionné réel (officiel + récolte + IA + itemaddon). Rejouer cet espace
hors génération dérivait : 66 ids trouvés contre 3 794 ici.

Pour chaque identifiant minoritaire, la purge remonte à SA source :
  - traductions/objets.json : le N de l'entrée est retiré (le D reste) ;
  - le moulin objets_dbc.json {"noms": EN->FR} : si le N vient de la
    jointure itemaddon, la PAIRE fautive est retirée ;
  - sinon (officiel/récolte) : intouchable ici — compté « hors source »,
    c'est le point d'écriture (bloc 8) qui devra le refuser.

Gardes : un minoritaire dont l'anglais égale la valeur aux accents/casse
près est LÉGITIME (« Eclat du mépris » / « Éclat du mépris ») — jamais
purgé. RÈGLES D'ARRÊT DE DAN : famille avec > 5 porteurs légitimes ->
arbitrage, rien n'y est purgé ; > 400 entrées perdues en entier -> arrêt
complet. Sauvegardes horodatées, simulation par défaut.

Usage : python outils/purger_objets_suspects.py [--appliquer]
"""
import io
import json
import os
import shutil
import sys
import time
import unicodedata

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTEURS = os.path.join(BASE, "rapports", "porteurs_objets.json")
OBJETS = os.path.join(BASE, "traductions", "objets.json")
MOULIN = os.path.join(BASE, "traductions", "objets_dbc.json")
PAR_ID = os.path.join(BASE, "sources", "dbc", "itemaddon_par_id.json")
RAPPORT = os.path.join(BASE, "rapports", "purge_objets_bloc7")

SEUIL_FAMILLE_LEGITIME = 5
# 1 500 depuis le 29/07/2026 (bloc B du programme 2) : Dan a levé la
# limite de 400 après l'arrêt du bloc 7 — « un joueur qui lit un FAUX nom
# se trompe d'objet ; un joueur qui lit l'anglais sait seulement que ce
# n'est pas encore traduit ». Le plan mesuré perdait 1 065 entrées.
SEUIL_ENTREES_PERDUES = 1500

# Familles > 5 légitimes DÉJÀ tranchées par arbitrage : la purge de leurs
# minoritaires est autorisée, les légitimes restent intouchés.
# « PH » (bloc B, 29/07/2026) : les 9 porteurs légitimes sont des objets
# placeholder RÉELLEMENT nommés « PH » des deux côtés (identité) — ils
# gardent leur nom ; un vrai objet qui AFFICHE « PH » à la place de son
# nom est précisément le bug purgé.
FAMILLES_TRANCHEES = {"PH"}


def charger(chemin):
    if not os.path.exists(chemin):
        return {}
    with io.open(chemin, encoding="utf-8") as f:
        return json.load(f)


def plat(texte):
    texte = unicodedata.normalize("NFKD", texte or "")
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    return " ".join(texte.lower().split())


def main():
    appliquer = "--appliquer" in sys.argv
    lignes = []

    def dire(t=""):
        print(t)
        lignes.append(t)

    dire("PURGE DES NOMS D'OBJETS SUR-PORTÉS — %s (%s)"
         % (time.strftime("%d/%m/%Y %H:%M"),
            "APPLICATION" if appliquer else "simulation"))
    dire("=" * 66)

    porteurs = charger(PORTEURS)
    if not porteurs:
        dire("! rapports/porteurs_objets.json absent — lance d'abord "
             "generateur_db (la vigie l'écrit).")
        return 2
    objets = charger(OBJETS)
    moulin = charger(MOULIN)
    m_noms = moulin.get("noms", {})
    par_id = charger(PAR_ID)
    dire("mesure de la génération : %d familles, %d minoritaires"
         % (len(porteurs), sum(len(v["ids"]) for v in porteurs.values())))

    purge_objets = []      # (valeur, id)
    purge_moulin = {}      # cle EN -> valeur (paires du moulin à retirer)
    hors_source = []
    arbitrage = []
    for valeur, fiche in porteurs.items():
        ids = [str(i) for i in fiche["ids"]]
        anglais = {str(k): v for k, v in fiche["anglais"].items()}
        legitimes = [i for i in ids if plat(anglais.get(i, "")) ==
                     plat(valeur)]
        if len(legitimes) > SEUIL_FAMILLE_LEGITIME \
                and valeur not in FAMILLES_TRANCHEES:
            arbitrage.append((valeur, len(ids), len(legitimes)))
            continue
        for iid in ids:
            if iid in legitimes:
                continue
            if (objets.get(iid) or {}).get("N") == valeur:
                purge_objets.append((valeur, iid))
                continue
            en_ia = (par_id.get(iid) or {}).get("N")
            if en_ia and m_noms.get(en_ia) == valeur:
                purge_moulin[en_ia] = valeur
                continue
            hors_source.append((valeur, iid, anglais.get(iid, "?")))

    perdent_tout = sum(
        1 for _v, i in purge_objets
        if len([c for c in (objets.get(i) or {}) if c in ("N", "D")]) == 1)

    dire("")
    dire("PLAN :")
    dire("  objets.json : %d N à retirer (%d familles)"
         % (len(purge_objets), len({v for v, _ in purge_objets})))
    dire("  moulin      : %d paire(s) EN->FR à retirer" % len(purge_moulin))
    dire("  hors source (officiel/récolte — pour le bloc 8) : %d"
         % len(hors_source))
    dire("  entrées perdues en entier : %d (arrêt si > %d)"
         % (perdent_tout, SEUIL_ENTREES_PERDUES))
    if arbitrage:
        dire("  familles en ARBITRAGE (règle des 5 légitimes) : %d"
             % len(arbitrage))
        for valeur, n, nl in sorted(arbitrage, key=lambda t: -t[1])[:6]:
            dire("    %r : %d minoritaires dont %d légitimes"
                 % (valeur[:40], n, nl))
    ex = {}
    for v, i in purge_objets:
        ex.setdefault(v, []).append(i)
    for v, ids in sorted(ex.items(), key=lambda kv: -len(kv[1]))[:10]:
        dire("  %-40r x%d" % (v[:38], len(ids)))

    if perdent_tout > SEUIL_ENTREES_PERDUES:
        dire("")
        dire("ARRÊT (règle de Dan) : %d entrées perdues en entier (> %d)."
             % (perdent_tout, SEUIL_ENTREES_PERDUES))
        return 1
    if arbitrage and appliquer:
        dire("")
        dire("ARRÊT (règle de Dan, bloc B) : %d famille(s) à plus de %d "
             "porteurs légitimes NON tranchée(s) — rien n'est appliqué "
             "tant que l'arbitrage n'est pas rendu." %
             (len(arbitrage), SEUIL_FAMILLE_LEGITIME))
        return 1

    if appliquer and (purge_objets or purge_moulin):
        horodatage = time.strftime("%Y%m%d-%H%M%S")
        if purge_objets:
            shutil.copy2(OBJETS, OBJETS.replace(
                ".json", "_avant_bloc7_%s.json" % horodatage))
            for _v, i in purge_objets:
                objets[i].pop("N", None)
                if not objets[i]:
                    del objets[i]
            with io.open(OBJETS, "w", encoding="utf-8") as f:
                json.dump(objets, f, ensure_ascii=False, indent=1,
                          sort_keys=True)
            dire("écrit : objets.json (%d N retirés, sauvegarde "
                 "_avant_bloc7_%s)" % (len(purge_objets), horodatage))
        if purge_moulin:
            shutil.copy2(MOULIN, MOULIN.replace(
                ".json", "_avant_bloc7_%s.json" % horodatage))
            for en in purge_moulin:
                m_noms.pop(en, None)
            with io.open(MOULIN, "w", encoding="utf-8") as f:
                json.dump(moulin, f, ensure_ascii=False, indent=1,
                          sort_keys=True)
            dire("écrit : objets_dbc.json (%d paires retirées)"
                 % len(purge_moulin))
        # Les « hors source » (officiel/récolte) ne se purgent pas ici :
        # leur N serait RE-POSÉ à chaque régénération. On les verse dans
        # traductions/objets_interdits.json, que generateur_db refuse au
        # point d'écriture (bloc B, 29/07/2026). Fusion sans doublon.
        if hors_source:
            chemin_interdits = os.path.join(BASE, "traductions",
                                            "objets_interdits.json")
            interdits = charger(chemin_interdits)
            ajouts = 0
            for valeur, iid, _en in hors_source:
                liste = interdits.setdefault(str(iid), [])
                if valeur not in liste:
                    liste.append(valeur)
                    ajouts += 1
            with io.open(chemin_interdits, "w", encoding="utf-8") as f:
                json.dump(interdits, f, ensure_ascii=False, indent=1,
                          sort_keys=True)
            dire("écrit : objets_interdits.json (+%d paires, %d ids au "
                 "total) — refusées à la génération" % (ajouts,
                                                        len(interdits)))
        dire("(retour en file à la prochaine régénération — voie lot 13)")
    elif not appliquer:
        dire("")
        dire("SIMULATION : rien n'a été écrit. --appliquer pour purger.")

    chemin_rapport = "%s_%s_%s.txt" % (
        RAPPORT, time.strftime("%Y%m%d-%H%M%S"),
        "application" if appliquer else "simulation")
    with io.open(chemin_rapport, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n\nDÉTAIL objets.json :\n")
        for v, i in purge_objets:
            f.write("%s\t%s\n" % (v, i))
        f.write("\nDÉTAIL moulin :\n")
        for en, v in purge_moulin.items():
            f.write("%s\t<-\t%s\n" % (v, en))
        f.write("\nHORS SOURCE (bloc 8) :\n")
        for v, i, en in hors_source:
            f.write("%s\t%s\tEN=%s\n" % (v, i, en))
    print()
    print("rapport -> %s" % chemin_rapport)
    return 0


if __name__ == "__main__":
    sys.exit(main())
