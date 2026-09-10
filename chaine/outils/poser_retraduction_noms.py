# -*- coding: utf-8 -*-
r"""Pose un lot de NOMS de sorts retraduits dans traductions/sorts.json
(section « noms »), avec les mêmes protections que le point d'écriture de
cycle_sorts (bloc 8) :

  - sauvegarde horodatée inconditionnelle AVANT d'écrire ;
  - normalisateur du vocabulaire arbitré derrière chaque valeur
    (appliquer_vocabulaire.corriger — la leçon du lot 13) ;
  - BARRIÈRE au point d'écriture : poison (table + verrou par clé) et
    seuil des porteurs avec parenté — refus BRUYANT, jamais silencieux ;
  - apostrophes droites, espaces normales, identités écartées.

Usage : python outils/poser_retraduction_noms.py <lot.json> [--rapport chemin]
        <lot.json> : [{"en": ..., "fr": ...}, ...]

Écrit un rapport détaillé (posés / remplacés / refusés) et sort en erreur
si le lot est vide ou illisible. Conçu pour le bloc A (retraduction des
noms couverts par la couche Glayna) mais sans rien de spécifique à Glayna :
tout futur lot de noms passe par ici plutôt que d'éditer le store à la main.
"""
import io
import json
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from appliquer_vocabulaire import corriger  # noqa: E402
from noms_empoisonnes import (SEUIL_PORTEURS, TOLERES, empoisonne,  # noqa: E402
                              parente)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE = os.path.join(BASE, "traductions", "sorts.json")


def normaliser(fr):
    """Apostrophe droite, espace normale, bords rognés — le pont compare au
    texte exact du client."""
    return (fr or "").replace("’", "'").replace(" ", " ").strip()


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    lot = json.load(io.open(args[0], encoding="utf-8"))
    if not isinstance(lot, list) or not lot:
        raise SystemExit("lot vide ou illisible : rien n'est écrit")

    store = json.load(io.open(STORE, encoding="utf-8"))
    noms = store.setdefault("noms", {})

    # sauvegarde horodatée inconditionnelle
    horodate = time.strftime("%Y%m%d-%H%M%S")
    copie = STORE.replace(".json", "_avant_pose_%s.json" % horodate)
    shutil.copy2(STORE, copie)

    # porteurs actuels du store entier (même carte que cycle_sorts)
    porteurs = {}
    for _en, _fr in noms.items():
        if isinstance(_fr, str) and _fr.strip():
            porteurs.setdefault(_fr.strip(), []).append(_en)

    poses, remplaces, refus, identites, vocab = [], [], [], [], []
    for paire in lot:
        en = (paire.get("en") or "").strip()
        fr = normaliser(paire.get("fr"))
        if not en or not fr:
            refus.append((en, fr, "vide"))
            continue
        fr2, regles = corriger(en, fr)
        fr2 = normaliser(fr2)
        if regles:
            vocab.append((en, fr, fr2, regles))
        if fr2 == en:
            identites.append(en)
            continue
        cles = [c for c in porteurs.get(fr2, []) if c != en]
        if empoisonne(en, fr2):
            refus.append((en, fr2, "poison"))
            continue
        if (len(cles) + 1 > SEUIL_PORTEURS and fr2 not in TOLERES
                and not parente(cles + [en])):
            refus.append((en, fr2, "porteurs:%d" % (len(cles) + 1)))
            continue
        avant = noms.get(en)
        if avant == fr2:
            continue
        (remplaces if en in noms else poses).append((en, avant, fr2))
        noms[en] = fr2
        porteurs.setdefault(fr2, []).append(en)

    if not poses and not remplaces:
        print("rien à écrire (posés 0, remplacés 0, refusés %d)" % len(refus))
        raise SystemExit(2)

    with io.open(STORE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(store, f, ensure_ascii=False, indent=1, sort_keys=True)

    rapport = os.path.join(BASE, "rapports",
                           "pose_noms_%s.txt" % horodate)
    os.makedirs(os.path.dirname(rapport), exist_ok=True)
    with io.open(rapport, "w", encoding="utf-8", newline="") as f:
        f.write("Pose de noms retraduits — %s\nsauvegarde : %s\n\n"
                % (horodate, copie))
        f.write("NOUVEAUX (%d)\n" % len(poses))
        for en, _, fr in poses:
            f.write("  %s -> %s\n" % (en, fr))
        f.write("\nREMPLACÉS (%d)\n" % len(remplaces))
        for en, avant, fr in remplaces:
            f.write("  %s : %r -> %r\n" % (en, avant, fr))
        f.write("\nVOCABULAIRE APPLIQUÉ (%d)\n" % len(vocab))
        for en, avant, apres, regles in vocab:
            f.write("  %s : %r -> %r (%s)\n"
                    % (en, avant, apres, ", ".join(regles)))
        f.write("\nREFUSÉS PAR LA BARRIÈRE (%d)\n" % len(refus))
        for en, fr, motif in refus:
            f.write("  [%s] %s -> %r\n" % (motif, en, fr))
        f.write("\nIDENTITÉS ÉCARTÉES (%d)\n" % len(identites))
        for en in identites:
            f.write("  %s\n" % en)

    print("posés : %d nouveaux + %d remplacés | vocabulaire : %d | "
          "refusés : %d | identités : %d"
          % (len(poses), len(remplaces), len(vocab), len(refus),
             len(identites)))
    for en, fr, motif in refus:
        print("  REFUS [%s] %s -> %r" % (motif, en, fr))
    print("rapport :", rapport)


if __name__ == "__main__":
    main()
