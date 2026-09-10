# -*- coding: utf-8 -*-
"""
AUDIT ANTI-POISON de la table des noms de sorts (préalable OBLIGATOIRE à
la réparation des 1 963 descriptions à noms incrustés — le cas vécu
« Felfury » -> « Cleansing Waters » prouve que la table contient des
paires croisées).

Trois poisons cherchés dans traductions/sorts.json (noms) :
  1. CROISEMENT : le « français » est en réalité le nom ANGLAIS d'un
     AUTRE sort de la table (l'usine a mélangé deux lignes) ;
  2. CHIMÈRE : mot-à-mot anglais/français (détecteur d'hier) ;
  3. CLÉ FRANÇAISE : la clé « anglaise » contient des caractères
     accentués — la table est polluée dans l'autre sens.

Sortie : rapports/noms_poison.txt — RIEN n'est modifié (l'arbitrage des
retraits se fait après lecture).
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from adopter_frenchtooltip import chimere  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTS = os.path.join(BASE, "traductions", "sorts.json")
RAPPORT = os.path.join(BASE, "rapports", "noms_poison.txt")


def a_accent(texte):
    return any(ord(c) > 127 for c in texte)


def main():
    with io.open(SORTS, encoding="utf-8") as f:
        noms = json.load(f).get("noms", {})
    cles = set(noms)

    croisements, chimeres, cles_fr = [], [], []
    for en, fr in noms.items():
        # VRAI croisement (affiné après 139 faux positifs dus à l'écho
        # des clés françaises parasites) : la valeur est une clé de la
        # table QUI A ELLE-MÊME une traduction française différente —
        # « Felfury » -> « Cleansing Waters » (dont le vrai français est
        # « Eaux purificatrices ») se prend, « X -> Forme maudite »
        # (clé-écho identitaire) s'innocente.
        if fr != en and fr in cles and not a_accent(fr):
            valeur_de_fr = noms.get(fr)
            if valeur_de_fr and valeur_de_fr != fr \
                    and a_accent(valeur_de_fr):
                croisements.append((en, fr, valeur_de_fr))
        if chimere(fr):
            chimeres.append((en, fr))
        if a_accent(en):
            cles_fr.append((en, fr))

    os.makedirs(os.path.dirname(RAPPORT), exist_ok=True)
    with io.open(RAPPORT, "w", encoding="utf-8") as f:
        f.write("AUDIT ANTI-POISON des noms de sorts — %d paires\n\n"
                % len(noms))
        f.write("== CROISEMENTS (valeur = clé EN d'un autre sort, qui a "
                "sa propre traduction) : %d\n" % len(croisements))
        for en, fr, vrai in sorted(croisements)[:300]:
            f.write("   %-36s => %-30s (or « %s » = %s)\n"
                    % (en[:36], fr[:30], fr[:30], vrai[:30]))
        f.write("\n")
        for titre, liste in (
                ("CHIMÈRES (mot-à-mot)", chimeres),
                ("CLÉS FRANÇAISES (pollution inverse)", cles_fr)):
            f.write("== %s : %d\n" % (titre, len(liste)))
            for en, fr in sorted(liste)[:300]:
                f.write("   %-42s => %s\n" % (en[:42], fr[:50]))
            f.write("\n")

    print("paires au total :", len(noms))
    print("croisements     :", len(croisements))
    print("chimères        :", len(chimeres))
    print("clés françaises :", len(cles_fr))
    print("rapport :", RAPPORT)


if __name__ == "__main__":
    main()
