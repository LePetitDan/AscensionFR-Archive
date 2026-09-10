# -*- coding: utf-8 -*-
"""
Quelles expressions ${...} d'Ascension le client ne sait-il PAS calculer ?

Le client résout lui-même ${ ... } (arithmétique sur des variables de sorts).
Si l'expression est invalide, il renonce et n'affiche qu'un « $ » — c'est le
cas de « Tempête juste » rang 1, dont Ascension a écrit $805410m1u (le « u »
est une coquille) à l'intérieur des accolades.

Cet audit recense TOUTES les expressions invalides, quelle que soit la coquille.

Étalonnage obligatoire : ${$m1*1.5} (Backstab) est valide et s'affiche en jeu.
Un audit qui le déclare invalide est faux — d'où les cas témoins ci-dessous.
"""
import io
import json
import re
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              errors="replace")

CHEMIN = r"D:\AscensionFR\WorkFlow\sources\dbc\spells_Ascension.json"

ACCOLADE = re.compile(r"\$\{([^{}]*)\}")

# Une variable de sort : $<idSort><lettres><indice> ou $<lettres><indice>.
# Les deux motifs sont essayés dans cet ordre (le plus spécifique d'abord).
VARIABLES = (
    re.compile(r"\$\d+[A-Za-z]+\d*"),   # $805410m1, $42208m1
    re.compile(r"\$[A-Za-z]+\d*"),      # $m1, $SP, $AP, $PL, $M1
    re.compile(r"\$<[A-Za-z]+>"),       # $<mult>, $<percent>
)

# Ce qui a le droit de rester une fois les variables retirées : de l'arithmétique.
ARITHMETIQUE = set("0123456789+-*/.() \t")

# Cas dont on connaît la réponse : si l'audit se trompe sur eux, il est faux.
TEMOINS_VALIDES = ["${$m1*1.5}", "${$m1+0.21*$SP}", "${$42208m1*8*$<mult>}",
                   "${($m1+$AP*0.07)*6}", "${$SP*0.012+$AP*0.012+$m1}"]
TEMOINS_CASSES = ["${$805410m1u+$SP*0.25}"]


def parasites(expression):
    """Caractères restants qui ne sont ni une variable ni de l'arithmétique."""
    reste = expression
    for motif in VARIABLES:
        reste = motif.sub("", reste)
    return "".join(sorted(set(c for c in reste if c not in ARITHMETIQUE)))


def etalonner():
    """Refuse de rendre un verdict si l'audit échoue sur les cas connus."""
    ok = True
    for temoin in TEMOINS_VALIDES:
        p = parasites(ACCOLADE.match(temoin).group(1))
        if p:
            print("  AUDIT FAUX : %s declare invalide (parasites %r)"
                  % (temoin, p))
            ok = False
    for temoin in TEMOINS_CASSES:
        if not parasites(ACCOLADE.match(temoin).group(1)):
            print("  AUDIT FAUX : %s declare valide" % temoin)
            ok = False
    return ok


def main():
    print("Etalonnage sur des cas connus :")
    if not etalonner():
        print("\nAudit non fiable, resultats non publies.")
        sys.exit(1)
    print("  ok : les %d temoins valides passent, le temoin casse est detecte"
          % len(TEMOINS_VALIDES))
    print()

    with open(CHEMIN, encoding="utf-8") as f:
        sorts = json.load(f)

    familles = Counter()
    exemples = {}
    touches = {}
    total = 0

    for sid, sort in sorts.items():
        description = sort.get("D") or ""
        for m in ACCOLADE.finditer(description):
            total += 1
            p = parasites(m.group(1))
            if p:
                familles[p] += 1
                touches[sid] = sort.get("N", "?")
                exemples.setdefault(p, (sid, sort.get("N", "?"), m.group(0)))

    print("expressions ${...} au total   : %d" % total)
    print("expressions invalides         : %d" % sum(familles.values()))
    print("sorts touches                 : %d / %d  (%.4f %%)"
          % (len(touches), len(sorts), 100.0 * len(touches) / len(sorts)))
    print()
    if familles:
        print("Coquilles trouvees (le client renonce -> affiche « $ ») :")
        for p, n in familles.most_common(12):
            sid, nom, ex = exemples[p]
            print("   %-8r %4d fois   sort %-9s %-26s %s"
                  % (p, n, sid, nom[:25], ex[:56]))
        print()
        print("Sorts concernes :")
        for sid, nom in sorted(touches.items()):
            print("   %-9s %s" % (sid, nom))
    else:
        print("Aucune : toutes les expressions d'Ascension sont calculables.")


if __name__ == "__main__":
    main()
