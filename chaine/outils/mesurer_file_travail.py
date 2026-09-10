# -*- coding: utf-8 -*-
"""Que contiennent vraiment les rapports de joueurs ? — programme 26.

CE QUE CET OUTIL RÉPOND, et pourquoi chacune de ces questions compte :

  1. Combien de rapports, et combien réellement OUVERTS (le dénominateur —
     un compte de fichiers n'est pas un compte de fichiers lus) ;
  2. Combien d'entrées au total, et combien de textes DISTINCTS. C'est tout
     le sujet : le même texte manquant est signalé par beaucoup de monde, et
     c'est ce qui transforme « 7 532 rapports » en file de travail ordonnée ;
  3. Chaque entrée dit-elle QUEL FICHIER et QUELLE CLÉ toucher ? Un rapport
     donne une CATÉGORIE et un TEXTE ANGLAIS. Reste à savoir si ce couple
     retrouve un fichier de `traductions/` — et à quel TAUX ;
  4. Combien sont déjà traduits depuis (donc plus des tâches) ;
  5. Combien sont des textes d'interface que l'officiel Blizzard écrase
     — le piège du programme 19 : envoyer quelqu'un corriger un texte qui ne
     sortira jamais est pire qu'une file vide.

⚠️ Cet outil NE PUBLIE RIEN et n'écrit que dans `rapports/`.

Usage :
    python outils/mesurer_file_travail.py                  (mesure)
    python outils/mesurer_file_travail.py --file           (+ engendre la file)
"""
import collections
import glob
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ICI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(ICI)
RAPPORTS = os.path.join(BASE, "rapports")
TRAD = os.path.join(BASE, "traductions")

# La catégorie d'une entrée de rapport -> le fichier de `traductions/` et la
# forme de sa clé. C'est ce qui permet de dire au contributeur « ouvre CE
# fichier, cherche CETTE clé » plutôt que « débrouille-toi ».
#
# « texte » : la clé EST le texte anglais (recherche directe).
# « texte2 » : idem, mais sous une sous-table (sorts.json -> descriptions).
CIBLES = {
    "TextesPNJ":     ("textes_pnj.json", "texte", None),
    "Gossip":        ("gossip.json", "texte", None),
    "Divers":        ("divers.json", "texte", None),
    "Pages":         ("pages.json", "texte", None),
    # La récolte [Sorts] porte des IDENTIFIANTS numériques (« 3018 »), pas
    # des textes : les ranger en « texte2 » les comptait tous « à traduire »
    # et la file publiée aurait charrié 7 290 lignes inutilisables
    # (programme 29, bloc D — corrigé au programme 30).
    "Sorts":         ("sorts_recoltes.json", "id", None),
    # Les deux familles de quêtes : la base est indexée par ID, pas par
    # texte — on le DIT plutôt que de faire semblant de savoir.
    "QuetesRendu":   ("quetes.json", "id", None),
    "QuetesProgres": ("quetes.json", "id", None),
}

RE_SECTION = re.compile(r"^---\s*(.+?)\s*\((\d+)\)\s*---\s*$", re.M)
RE_ENTREE = re.compile(r"^\[([A-Za-z_]+)\]\s?(.*)$")
RE_PROPOSITION = re.compile(
    r"^-\s*(\w+)\s*\|\s*(\S*)\s*\|\s*actuel=(.*?)\s*\|\s*propose=(.*)$", re.S)


def charger_bases():
    """Les bases VIVANTES seulement — jamais les `*_avant_*`, qui sont des
    sauvegardes et fausseraient tous les comptes."""
    bases = {}
    for fichier, forme, sous in {(f, fo, s) for f, fo, s in CIBLES.values()}:
        chemin = os.path.join(TRAD, fichier)
        try:
            d = json.load(io.open(chemin, encoding="utf-8"))
        except (OSError, ValueError):
            bases[fichier] = None
            continue
        bases[fichier] = d.get(sous, {}) if (sous and isinstance(d, dict)) \
            else d
    return bases


def lire_rapports():
    """Rend (entrees, stats). Une entrée = (categorie, texte, fichier_source).

    On compte SÉPARÉMENT les fichiers vus, ouverts et illisibles : un
    dénominateur qui n'est pas mesuré ne vaut rien."""
    fichiers = sorted(glob.glob(os.path.join(RAPPORTS,
                                             "auto_*_rapport_*.txt")))
    stats = collections.Counter()
    stats["vus"] = len(fichiers)
    entrees = []
    propositions = []
    signalements = []
    par_section = collections.Counter()
    for chemin in fichiers:
        try:
            texte = io.open(chemin, encoding="utf-8", errors="replace").read()
        except OSError:
            stats["illisibles"] += 1
            continue
        stats["ouverts"] += 1
        if len(texte.strip()) < 80:
            stats["vides"] += 1
        nom = os.path.basename(chemin)
        # Découpage en sections, pour ne pas mélanger une récolte et un
        # échec d'alignement (qui ne se corrigent pas au même endroit).
        bornes = [(m.start(), m.end(), m.group(1)) for m in
                  RE_SECTION.finditer(texte)]
        for i, (deb, fin, titre) in enumerate(bornes):
            suite = bornes[i + 1][0] if i + 1 < len(bornes) else len(texte)
            corps = texte[fin:suite]
            titre_n = titre.replace("?", "é")     # rapports mal encodés
            par_section[titre_n] += 1
            if titre_n.startswith("Récolte"):
                for ligne in corps.split("\n"):
                    m = RE_ENTREE.match(ligne.strip())
                    if m and m.group(2).strip():
                        entrees.append((m.group(1), m.group(2).strip(), nom))
                        stats["entrees_recolte"] += 1
            elif titre_n.startswith("Propositions"):
                for bloc in re.findall(r"^-\s.*$", corps, re.M):
                    m = RE_PROPOSITION.match(bloc.strip())
                    if m:
                        propositions.append(
                            (m.group(1), m.group(2), m.group(3), m.group(4),
                             nom))
                        stats["propositions"] += 1
            elif titre_n.startswith("Signalements"):
                for ligne in corps.split("\n"):
                    if ligne.strip().startswith("-"):
                        signalements.append((ligne.strip(), nom))
                        stats["signalements"] += 1
            else:
                stats["entrees_alignement"] += corps.count("\n")
    return entrees, propositions, signalements, stats, par_section


def main():
    bases = charger_bases()
    entrees, propositions, signalements, stats, par_section = lire_rapports()

    print("=" * 74)
    print("CE QU'IL Y A DANS LES RAPPORTS — programme 26")
    print("=" * 74)
    print("\n>> 1. Le dénominateur")
    print("   fichiers auto_*_rapport_*.txt vus      : %d" % stats["vus"])
    print("   réellement OUVERTS et analysés         : %d" % stats["ouverts"])
    print("   illisibles                             : %d"
          % stats["illisibles"])
    print("   quasi vides (< 80 caractères utiles)   : %d" % stats["vides"])

    print("\n>> 2. Les sections rencontrées")
    for k, v in par_section.most_common():
        print("   %-46s %d rapport(s)" % (k, v))

    print("\n>> 3. Les entrées de RÉCOLTE (le matériau principal)")
    print("   entrées brutes                         : %d"
          % stats["entrees_recolte"])
    distinct = collections.Counter((c, t) for c, t, _ in entrees)
    print("   couples (catégorie, texte) DISTINCTS   : %d" % len(distinct))
    if stats["entrees_recolte"]:
        print("   taux de doublon                        : %.1f fois en "
              "moyenne" % (stats["entrees_recolte"] / max(1, len(distinct))))

    print("\n   -- les 12 textes les plus signalés --")
    for (cat, txt), n in distinct.most_common(12):
        print("   %5d fois  [%-13s] %s" % (n, cat, txt[:70].replace("\n", " ")))

    print("\n>> 4. Chaque entrée dit-elle QUEL FICHIER et QUELLE CLÉ ?")
    retrouves = collections.Counter()
    deja_traduits = collections.Counter()
    inconnus = collections.Counter()
    sans_cible = collections.Counter()
    for (cat, txt), n in distinct.items():
        fiche = CIBLES.get(cat)
        if not fiche:
            sans_cible[cat] += 1
            continue
        fichier, forme, _ = fiche
        base = bases.get(fichier)
        if base is None:
            sans_cible[cat] += 1
            continue
        if forme == "id":
            # La base est indexée par ID : le texte ne suffit pas.
            inconnus[cat] += 1
            continue
        if txt in base:
            deja_traduits[cat] += 1
        else:
            retrouves[cat] += 1
    total_d = len(distinct)
    n_ret = sum(retrouves.values())
    n_dej = sum(deja_traduits.values())
    n_inc = sum(inconnus.values())
    n_sans = sum(sans_cible.values())
    print("   sur %d couples distincts :" % total_d)
    print("     À TRADUIRE  (fichier+clé connus, absent de la base) : %6d "
          "(%.1f%%)" % (n_ret, 100.0 * n_ret / max(1, total_d)))
    print("     déjà traduits depuis (plus une tâche)              : %6d "
          "(%.1f%%)" % (n_dej, 100.0 * n_dej / max(1, total_d)))
    print("     base indexée par ID — le texte ne suffit pas       : %6d "
          "(%.1f%%)" % (n_inc, 100.0 * n_inc / max(1, total_d)))
    print("     catégorie sans cible connue                        : %6d "
          "(%.1f%%)" % (n_sans, 100.0 * n_sans / max(1, total_d)))
    print("\n   par catégorie (à traduire / déjà fait) :")
    for cat in sorted(set(retrouves) | set(deja_traduits) | set(inconnus)
                      | set(sans_cible)):
        print("     %-14s à traduire %6d | déjà %6d | par ID %6d | "
              "sans cible %5d"
              % (cat, retrouves.get(cat, 0), deja_traduits.get(cat, 0),
                 inconnus.get(cat, 0), sans_cible.get(cat, 0)))

    print("\n>> 5. Les PROPOSITIONS de joueurs (le signal le plus fort)")
    print("   propositions trouvées dans les rapports : %d" % len(propositions))
    vues = collections.Counter((t, i, a, p) for t, i, a, p, _ in propositions)
    print("   distinctes                              : %d" % len(vues))
    for (t, i, a, p), n in vues.most_common(12):
        print("   [%s%s] %s" % (t, (" " + i) if i else "", "×%d" % n if n > 1
                                else ""))
        print("       actuel  : %s" % a[:70].replace("\n", " "))
        print("       propose : %s" % p[:70].replace("\n", " "))

    print("\n>> 6. Les SIGNALEMENTS")
    print("   lignes de signalement : %d" % len(signalements))
    casses = sum(1 for l, _ in signalements if "<Lua table at" in l)
    print("   dont ILLISIBLES (« <Lua table at 0x… > ») : %d (%.0f%%)"
          % (casses, 100.0 * casses / max(1, len(signalements))))

    if "--file" in sys.argv:
        engendrer_file(distinct, bases)
    return 0


def engendrer_file(distinct, bases):
    """La file de travail : un couple (catégorie, texte) par ligne, trié par
    nombre de signalements — l'ordre vient des joueurs, pas de nous."""
    lignes = []
    for (cat, txt), n in distinct.most_common():
        fiche = CIBLES.get(cat)
        if not fiche:
            continue
        fichier, forme, sous = fiche
        base = bases.get(fichier)
        if base is None or forme == "id" or txt in base:
            continue
        lignes.append({"signalements": n, "fichier": "traductions/" + fichier,
                       "sous_table": sous, "cle": txt, "categorie": cat})
    sortie = os.path.join(RAPPORTS, "file_travail_brute.json")
    json.dump(lignes, io.open(sortie, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("\n>> file brute écrite : %s (%d entrées)"
          % (os.path.relpath(sortie, BASE), len(lignes)))


if __name__ == "__main__":
    sys.exit(main())
