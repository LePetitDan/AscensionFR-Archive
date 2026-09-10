# -*- coding: utf-8 -*-
"""
PURGE des poisons de la table des noms (arbitrage manuel du 23/07/2026,
d'après rapports/noms_poison.txt — audit auditer_noms_poison.py).

Trois gestes, TOUS sauvegardés avant :
  1. CORRECTIONS à la main : les paires croisées dont le bon français est
     évident (règle « corriger sans demander » pour les contresens) ;
  2. SUPPRESSIONS : les clés-écho au français d'un AUTRE sort — mieux
     vaut l'anglais qu'un mauvais nom ; la récolte les regarnira ;
  3. PURGE des clés FRANÇAISES (accents dans la clé « anglaise ») :
     poids mort — elles ne peuvent jamais correspondre à un affichage
     anglais, et leurs échos piègent les audits.

Usage : python outils/purger_noms_poison.py
"""
import io
import json
import os
import shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTS = os.path.join(BASE, "traductions", "sorts.json")
SAUVEGARDE = os.path.join(BASE, "traductions",
                          "sorts_avant_purge_poison.json")
RAPPORT = os.path.join(BASE, "rapports", "noms_purges.txt")

CORRECTIONS = {
    "Corrupted Blade": "Lame corrompue",
    "Icecrown Scriptures": "Écritures de la Couronne de glace",
    "Very Special Spicy Gift": "Cadeau épicé très spécial",
    "Cosmetic - Breath Bubbles": "Cosmétique - Bulles de souffle",
    "Resistant": "Résistant",
}

# Clés dont la valeur appartient à un AUTRE sort (croisements avérés).
SUPPRESSIONS = [
    "Pestilence",                      # => « Gelée »
    "Corruption",                      # => « Mot de l'ombre : Douleur »
    "Chaos",                           # => « Boule de feu gangrenée »
    "Glace",                           # => « Éclair de feu »
    "Lance",                           # => « Précision du chasseur… »
    "Jet",                             # => « Tête de flèche jaune »
    "Vortex",                          # => « Tempête de sable »
    "Absorb Rune",                     # => « Déflagration des arcanes »
    "Iron Guard",                      # => « Étoile radieuse »
    "Motivation: Knight's Valor",      # => « Iron Guard » (anglais)
    "Glyphic Ruin SLS Missile Visual Hidden",   # interne, valeur croisée
    "Havoc",                           # « Chaos » : on laisse la récolte
    "Spout",                           # trancher ces deux-là proprement
]
# NB : les entrées internes au nom tronqué sont retrouvées par PRÉFIXE.
SUPPRESSIONS_PREFIXE = [
    "Glyphic Ruin SLS Missile",
    "Thunderer's Fur Cloak proc",
]


def a_accent(texte):
    return any(ord(c) > 127 for c in texte)


def main():
    if not os.path.exists(SAUVEGARDE):
        shutil.copy2(SORTS, SAUVEGARDE)
        print("sauvegarde :", SAUVEGARDE)
    with io.open(SORTS, encoding="utf-8") as f:
        cache = json.load(f)
    noms = cache.get("noms", {})
    avant = len(noms)
    journal = []

    for cle, bon in CORRECTIONS.items():
        if cle in noms and noms[cle] != bon:
            journal.append(("corrigé", cle, noms[cle], bon))
            noms[cle] = bon

    for cle in SUPPRESSIONS:
        if cle in noms:
            journal.append(("supprimé", cle, noms[cle], ""))
            del noms[cle]
    for prefixe in SUPPRESSIONS_PREFIXE:
        for cle in [k for k in noms if k.startswith(prefixe)]:
            journal.append(("supprimé", cle, noms[cle], ""))
            del noms[cle]

    purge_fr = 0
    for cle in [k for k in noms if a_accent(k)]:
        journal.append(("clé française", cle, noms[cle], ""))
        del noms[cle]
        purge_fr += 1

    with io.open(SORTS, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.makedirs(os.path.dirname(RAPPORT), exist_ok=True)
    with io.open(RAPPORT, "w", encoding="utf-8") as f:
        f.write("Purge des poisons du 23/07/2026 — journal complet\n\n")
        for geste, cle, valeur, bon in journal:
            f.write("%-14s %s => %s%s\n"
                    % (geste, cle[:50], valeur[:40],
                       ("  (devient : %s)" % bon) if bon else ""))
    print("noms avant :", avant, "| après :", len(noms))
    print("corrections :", len(CORRECTIONS),
          "| suppressions ciblées :",
          sum(1 for g, _, _, _ in journal if g == "supprimé"),
          "| clés françaises purgées :", purge_fr)
    print("journal :", RAPPORT)


if __name__ == "__main__":
    main()
