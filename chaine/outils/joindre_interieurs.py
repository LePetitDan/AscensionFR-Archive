# -*- coding: utf-8 -*-
"""Joint WMOAreaTable enUS (jeu) x frFR (officiel 3.3.5) par identifiant
-> traductions/interieurs.json { paires: {EN: FR} }.

Les noms d'INTÉRIEURS de bâtiments (tavernes, abbayes, mines...) affichés
en tête de minimap. Un même texte EN revendiqué par plusieurs FR
différents = ambigu, rejeté (même règle que partout)."""
import io
import json
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(BASE, "sources", "dbc")


def textes_par_id(chemin):
    d = json.load(io.open(chemin, encoding="utf-8"))
    sortie = {}
    for ligne in d["lignes"]:
        # la colonne localisée la plus remplie d'abord, c2 en repli
        t = None
        for cle in sorted(ligne, reverse=True):
            if cle.startswith("c") and ligne[cle]:
                t = ligne[cle]
                if cle != "c2":
                    break
        if t:
            sortie[ligne["id"]] = t
    return sortie


def main():
    # L'ANGLAIS vient de l'archive BLIZZARD D'ORIGINE (patch-enUS-3),
    # JAMAIS des patchs d'Ascension : ils ont RECONSTRUIT la table
    # (22 220 lignes au lieu de 22 550) et les identifiants ne
    # s'alignaient plus — « Gnomeregan » pointait vers la Taverne de
    # l'Eau-profonde, et une clé « espace » chevauchait toutes les
    # bulles de PNJ (vécu 22/07, signalé par Dan).
    en = textes_par_id(os.path.join(D, "wmoareatable_blizzard.json"))
    fr = textes_par_id(os.path.join(D, "wmoareatable_frfr.json"))

    votes = {}
    for ident, t_en in en.items():
        t_fr = fr.get(ident)
        if not t_en or len(t_en.strip()) < 3:
            continue                     # jamais de clé vide/minuscule
        if t_fr and t_fr != t_en:
            votes.setdefault(t_en, Counter())[t_fr] += 1

    paires, ambigus = {}, 0
    for t_en, compte in votes.items():
        if len(compte) == 1:
            paires[t_en] = next(iter(compte))
        else:
            # majorité NETTE acceptée (2/3 des occurrences), sinon rejet
            (meilleur, n1), reste = compte.most_common(1)[0], sum(
                compte.values())
            if n1 * 3 >= reste * 2:
                paires[t_en] = meilleur
            else:
                ambigus += 1

    # Garde anti-corruption : un même FRANÇAIS revendiqué par 4 clés
    # anglaises différentes ou plus = données décalées, on jette tout
    # ce français-là.
    revendications = Counter(paires.values())
    poisons = {f for f, n in revendications.items() if n >= 4}
    if poisons:
        avant = len(paires)
        paires = {e: f for e, f in paires.items() if f not in poisons}
        print("garde anti-corruption : %d paires jetées (%d FR"
              " sur-revendiqués)" % (avant - len(paires), len(poisons)))

    sans_fr = sum(1 for i, t in en.items()
                  if i not in fr or fr.get(i) == t)
    print("paires intérieurs :", len(paires), "| ambigus rejetés :",
          ambigus, "| sans frFR (customs/identiques) :", sans_fr)
    for k in list(paires)[:5]:
        print("   ", k, "->", paires[k])

    with io.open(os.path.join(BASE, "traductions", "interieurs.json"),
                 "w", encoding="utf-8") as f:
        json.dump({"paires": paires}, f, ensure_ascii=False, indent=1,
                  sort_keys=True)
    print("écrit : traductions/interieurs.json")


if __name__ == "__main__":
    main()
