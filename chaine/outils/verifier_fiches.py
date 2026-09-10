# -*- coding: utf-8 -*-
"""
Les fiches de classe sont-elles vraiment traduites ?

Leçon du 17/07/2026 : un premier passage par un modèle trop léger a rendu
74 chaînes sur 311 en anglais pur, et — pire — des traductions à moitié
faites (« Feu de l'enfer: Weave powerful spell casts and tear enemies... »).
Un texte à moitié traduit est plus laid que pas de traduction du tout, et
rien dans le pipeline ne l'aurait vu : le contrôle de format, lui, était
satisfait.

D'où ce garde-fou, qui mesure ce que le format ne dit pas : reste-t-il de
l'anglais ? Il s'étalonne d'abord sur des témoins (leçon d'auditer_accolades)
et ne juge qu'ensuite.

Usage : python outils/verifier_fiches.py
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generateur_glue import (  # noqa: E402
    signature_compatible, lire_fiches, lire_chaines, GLUE_FR)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(BASE, "a_traduire", "glue_classes.json")

# Mots qui n'existent qu'en anglais et qu'aucune traduction n'a de raison de
# garder. Choisis parmi les plus fréquents de ces textes, et sans jumeau
# français : « damage » n'est pas « dégâts », « with » n'est pas « avec ».
# Volontairement court : on cherche une preuve, pas une estimation.
ANGLAIS = re.compile(
    r"\b(?:the|your|you|with|and|that|this|from|their|them|are|can|will|"
    r"damage|enemies|allies|abilities|power|while|into|upon|through)\b",
    re.I)

# Un nom propre isolé, un code : le français peut légitimement être l'anglais.
def peut_rester_anglais(texte):
    return len(texte) < 12 or not re.search(r"[a-z]{3}", texte)


def temoins():
    """Le détecteur sait-il reconnaître ce qu'on lui demande ?"""
    cas = [
        ("Soutenez vos alliés et infligez des dégâts aux ennemis.", False),
        ("Feu de l'enfer: Weave powerful spell casts and tear enemies apart.",
         True),
        ("Barbarians are savage warriors that value strength.", True),
        ("Les Primalistes puisent dans la terre et la nature d'Azeroth.",
         False),
        ("Appelez la colère des étoiles sur vos ennemis.", False),
        ("Channel the power of the goddess Elune through your bow.", True),
    ]
    for texte, attendu in cas:
        if bool(ANGLAIS.search(texte)) != attendu:
            return False, texte
    return True, None


def main():
    ok, rate = temoins()
    if not ok:
        print("! détecteur déréglé sur le témoin : %r" % rate)
        print("  verdict NON publié")
        return 1

    with open(SOURCE, encoding="utf-8") as f:
        anglais = json.load(f)

    # On juge ce qui sera RÉELLEMENT écrit dans le fichier de glue, pas les
    # lots bruts : les reprises à la main comptent, et les clés déjà servies
    # par le frFR officiel ne sont jamais posées par nos fiches.
    fr = lire_fiches()
    officiel = lire_chaines(GLUE_FR)
    couvertes = sorted(set(fr) & set(officiel))
    for cle in couvertes:
        del fr[cle]

    if not fr:
        print("Aucune fiche traduite pour l'instant.")
        return 0
    if couvertes:
        print("Servies par le frFR officiel : %d" % len(couvertes))

    identiques, residus, formats = [], [], []
    for cle, texte in fr.items():
        en = anglais.get(cle)
        if not en or not texte:
            continue
        if texte == en and not peut_rester_anglais(en):
            identiques.append(cle)
        elif ANGLAIS.search(texte):
            residus.append(cle)
        if not signature_compatible(en, texte):
            formats.append(cle)

    total = len(fr)
    print("Fiches traduites   : %d / %d" % (total, len(anglais)))
    print("Restées anglaises  : %d" % len(identiques))
    print("Anglais résiduel   : %d" % len(residus))
    print("Format abîmé       : %d" % len(formats))
    for titre, liste in (("RESTÉES ANGLAISES", identiques),
                         ("ANGLAIS RÉSIDUEL", residus),
                         ("FORMAT ABÎMÉ", formats)):
        if liste:
            print("\n%s (%d) :" % (titre, len(liste)))
            for cle in sorted(liste)[:8]:
                print("   %-34s %s" % (cle, fr[cle][:52]))

    fautives = len(set(identiques) | set(residus) | set(formats))
    print()
    if fautives:
        print("%d chaîne(s) à reprendre." % fautives)
        return 1
    print("Toutes les fiches sont propres.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
