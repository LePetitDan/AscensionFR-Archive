# -*- coding: utf-8 -*-
"""
Fusionne les lots traduits (traductions/lots/*.json) dans les fichiers
cumulés traductions/*.json, puis valide la préservation des codes techniques
($n, |cff...|r, %s, etc.) par comparaison avec le contenu source.
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOTS = os.path.join(BASE, "traductions", "lots")
TRADUCTIONS = os.path.join(BASE, "traductions")
A_TRADUIRE = os.path.join(BASE, "a_traduire")

# Correspondance champ source (anglais) -> champ traduit
CHAMPS = {
    "objets": {"Name": "N", "Description": "D"},
    "creatures": {"Name": "N", "SubName": "S"},
    "objets_monde": {"Name": "N"},
    "quetes": {"Title": "T", "Objectives": "O", "Details": "D",
               "EndText": "F", "CompletedText": "A"},
}

MOTIF_CODES = re.compile(
    r"(\$[NnBbCcRr]\b|\$[Gg][^;]*;|\|c[0-9a-fA-F]{8}|\|r\b"
    r"|\|T[^|]*\|t|%\d*\$?[sdif])")


def codes(texte):
    """Multi-ensemble des codes techniques d'un texte (casse normalisée).

    Les sélecteurs de genre $g...; sont comptés sous une clé unique : le
    français en ajoute légitimement là où l'anglais n'accorde pas.
    """
    if not texte:
        return {}
    resultat = {}
    for m in MOTIF_CODES.findall(texte):
        if m[:2].lower() == "$g":
            continue
        cle = m.lower() if m.startswith("$") and len(m) == 2 else m
        resultat[cle] = resultat.get(cle, 0) + 1
    return resultat


def codes_perdus(en, fr):
    """Codes présents dans l'anglais et manquants (ou en nombre moindre)
    dans la traduction. L'ajout de codes n'est pas un défaut."""
    ce, cf = codes(en), codes(fr)
    return {k: v for k, v in ce.items() if cf.get(k, 0) < v}


def charger(chemin):
    if os.path.exists(chemin):
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    return {}


def main():
    if not os.path.isdir(LOTS):
        print("Aucun lot traduit trouvé.")
        sys.exit(1)

    cumules = {}      # nom de fichier cumulé -> dict
    problemes = []
    fusionnes = 0

    for nom in sorted(os.listdir(LOTS)):
        if not nom.endswith(".json"):
            continue
        categorie = re.sub(r"_\d+\.json$", "", nom)
        lot_traduit = charger(os.path.join(LOTS, nom))
        lot_source = charger(os.path.join(A_TRADUIRE, "lots", nom)).get(
            "entrees", {})
        if not lot_traduit:
            problemes.append("%s : fichier traduit vide ou illisible" % nom)
            continue

        if categorie in ("textes_pnj", "pages"):
            cible = cumules.setdefault(categorie + ".json",
                                       charger(os.path.join(TRADUCTIONS,
                                                            categorie + ".json")))
            for cle_en, valeurs in lot_traduit.items():
                fr = valeurs.get("FR") if isinstance(valeurs, dict) else valeurs
                if not fr:
                    problemes.append("%s : pas de FR pour %r" % (nom, cle_en[:40]))
                    continue
                perdus = codes_perdus(cle_en, fr)
                if perdus:
                    problemes.append("%s : codes PERDUS %s dans %r"
                                     % (nom, list(perdus), cle_en[:40]))
                cible[cle_en] = fr
                fusionnes += 1
            continue

        correspondance = CHAMPS.get(categorie)
        if not correspondance:
            problemes.append("%s : catégorie inconnue" % nom)
            continue
        cible = cumules.setdefault(categorie + ".json",
                                   charger(os.path.join(TRADUCTIONS,
                                                        categorie + ".json")))
        for cle, valeurs in lot_traduit.items():
            if not isinstance(valeurs, dict):
                problemes.append("%s : entrée %s non structurée" % (nom, cle))
                continue
            source = lot_source.get(cle, {})
            entree = {}
            for champ_en, champ_fr in correspondance.items():
                fr = valeurs.get(champ_fr)
                en = source.get(champ_en)
                if en and not fr:
                    problemes.append("%s : %s.%s manquant" % (nom, cle, champ_fr))
                if fr:
                    perdus = codes_perdus(en, fr) if en else {}
                    if perdus:
                        problemes.append("%s : codes PERDUS %s dans %s.%s"
                                         % (nom, list(perdus), cle, champ_fr))
                    entree[champ_fr] = fr
            # Textes d'objectifs des quêtes : OT1..OT4 -> liste
            if categorie == "quetes":
                ots_source = source.get("ObjectiveTexts") or []
                ots = []
                for i in range(1, 5):
                    v = valeurs.get("OT%d" % i, "")
                    ots.append(v or "")
                if any(ots):
                    # aligne la longueur sur la source
                    entree["OT"] = ots[:max(len(ots_source), 1)] \
                        if ots_source else [o for o in ots if o]
            if entree:
                cible[cle] = entree
                fusionnes += 1

    for nom, contenu in cumules.items():
        with open(os.path.join(TRADUCTIONS, nom), "w", encoding="utf-8") as f:
            json.dump(contenu, f, ensure_ascii=False, indent=1, sort_keys=True)

    print("%d entrées fusionnées dans %d fichiers cumulés."
          % (fusionnes, len(cumules)))
    if problemes:
        print("\n%d problème(s) :" % len(problemes))
        for p in problemes[:40]:
            print("  - " + p)
        if len(problemes) > 40:
            print("  ... et %d de plus" % (len(problemes) - 40))
    else:
        print("Aucun problème de codes techniques détecté.")


if __name__ == "__main__":
    main()
