# -*- coding: utf-8 -*-
"""
Découpe le contenu à traduire (a_traduire/*.json) en lots pour les agents
de traduction, avec des exemples de style tirés des traductions officielles.
Produit a_traduire/lots/<categorie>_<nn>.json et un manifeste lots.json.
"""
import json
import os
import random

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AT = os.path.join(BASE, "a_traduire")
LOTS = os.path.join(AT, "lots")


def charger(*chemin):
    p = os.path.join(BASE, *chemin)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}


def exemples_officiels(en_nom, fr_nom, champ_en, champ_fr, n=15, cle_en2=None):
    """Tire des paires (EN, FR) de la base officielle comme exemples."""
    en = charger("sources", "enUS", en_nom)
    fr = charger("sources", "frFR", fr_nom)
    communs = [k for k in fr if k in en
               and en[k].get(champ_en) and fr[k].get(champ_fr)]
    random.seed(42)
    random.shuffle(communs)
    paires = []
    for k in communs[:n]:
        paires.append([en[k][champ_en], fr[k][champ_fr]])
    return paires


def decouper(donnees, taille):
    cles = sorted(donnees)
    for i in range(0, len(cles), taille):
        yield {k: donnees[k] for k in cles[i:i + taille]}


def main():
    os.makedirs(LOTS, exist_ok=True)
    # Purge des anciens lots
    for f in os.listdir(LOTS):
        os.remove(os.path.join(LOTS, f))

    manifeste = []

    categories = [
        # (fichier, catégorie, taille de lot, exemples)
        ("objets.json", "objets", 50,
         exemples_officiels("item_template.json", "item_template_locale.json",
                            "name", "Name", 18)),
        ("creatures.json", "creatures", 60,
         exemples_officiels("creature_template.json",
                            "creature_template_locale.json",
                            "name", "Name", 18)),
        ("objets_monde.json", "objets_monde", 70,
         exemples_officiels("gameobject_template.json",
                            "gameobject_template_locale.json",
                            "name", "name", 15)),
        ("quetes.json", "quetes", 7,
         exemples_officiels("quest_template.json",
                            "quest_template_locale.json",
                            "LogTitle", "Title", 12)),
        ("textes_pnj.json", "textes_pnj", 25, []),
        ("pages.json", "pages", 25, []),
    ]

    for fichier, categorie, taille, exemples in categories:
        donnees = charger("a_traduire", fichier)
        if not donnees:
            continue
        for i, lot in enumerate(decouper(donnees, taille), 1):
            nom = "%s_%02d.json" % (categorie, i)
            with open(os.path.join(LOTS, nom), "w", encoding="utf-8") as f:
                json.dump({
                    "categorie": categorie,
                    "exemples_officiels": exemples,
                    "entrees": lot,
                }, f, ensure_ascii=False, indent=1)
            manifeste.append({
                "fichier": os.path.join(LOTS, nom).replace("\\", "/"),
                "categorie": categorie,
                "nb": len(lot),
            })

    with open(os.path.join(AT, "lots.json"), "w", encoding="utf-8") as f:
        json.dump(manifeste, f, ensure_ascii=False, indent=1)
    print("%d lots préparés" % len(manifeste))
    for m in manifeste:
        print("  %-40s %3d entrées" % (m["fichier"].split("/")[-1], m["nb"]))


if __name__ == "__main__":
    main()
