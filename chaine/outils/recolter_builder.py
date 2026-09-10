# -*- coding: utf-8 -*-
"""
recolter_builder.py — extrait les IDs de sorts/capacités du Build Calculator
d'Ascension (ascension.gg/.../builder) pour pré-remplir la traduction SANS
attendre le moindre signalement.

POURQUOI
--------
La page builder est une appli Next.js dont TOUT le catalogue de capacités est
embarqué (rendu serveur) dans le payload « flight ». Un seul chargement contient
les milliers de capacités de TOUS les archétypes. On y lit les objets
    \\"id\\":N,\\"name\\":\\"...\\"
et l'ID = le spellId du jeu (vérifié : builder 884376 = db.ascension.gg 884376 =
DB_Sorts[884376]). On produit une liste d'IDs, que recuperer_db.py consomme.

PIPELINE
--------
    python outils/recolter_builder.py               # -> rapports/ids_builder.txt (IDs ABSENTS de DB_Sorts)
    python outils/recuperer_db.py --fichier rapports/ids_builder.txt --limite 100 --dry
    (puis sans --dry quand la qualité te convient, /reload en jeu pour tester)

Par défaut on ne sort que les IDs ABSENTS de DB_Sorts et des corrections : ce
sont les vrais manquants (souvent les buffs), le meilleur rendement et le moins
de requêtes vers db.ascension.gg. --tout sort tous les IDs (utile pour générer
des 2e modèles aura sur les sorts déjà connus, mais bien plus de requêtes).

OPTIONS
-------
    --tout          tous les IDs, pas seulement les absents
    --url <URL>     autre page builder (defaut : realm area-52)
    --sortie <f>    autre fichier de sortie
    --noms          ajoute « # nom » en commentaire après chaque ID
"""
import os
import re
import sys
import urllib.error
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JEU = r"D:\AscensionFR\WOW_Priv\resources\ascension-live"
DBDIR = os.path.join(JEU, "Interface", "AddOns", "AscensionFR", "DB")
DB_SORTS = os.path.join(DBDIR, "DB_Sorts.lua")
CORRECTIONS = os.path.join(DBDIR, "DB_SortsCorrections.lua")
SORTIE = os.path.join(BASE, "rapports", "ids_builder.txt")
# Realms essayés dans l'ordre. « rexxar » = Conquest of Azeroth (le mode de Dan) :
# on le vise en premier, par correction. Vérifié sur une vraie page rexxar : le
# catalogue de capacités est IDENTIQUE à area-52 (mêmes 9 314 IDs, mêmes blocs) —
# le slug ne change pas les sorts. Mais la route « rexxar » est un realm CoA Alpha
# INTERMITTENT (404 par moments) : on retombe alors sur « area-52 », stable et
# vérifié équivalent, pour rester fiable. --url force une URL unique.
REALMS = ["rexxar", "area-52"]
URL_BASE = "https://ascension.gg/fr/v2/builder/%s"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AscensionFR-trad/1.0"

# Dans le HTML rendu serveur, les guillemets du flight sont échappés (\").
RE_ABILITY = re.compile(r'\\"id\\":(\d+),\\"name\\":\\"([^"\\]{1,80})')


def telecharger(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def extraire(html):
    """{id: nom} des capacités trouvées dans le payload (1er nom vu gagne)."""
    ids = {}
    for i, n in RE_ABILITY.findall(html):
        ids.setdefault(i, n)
    return ids


def ids_fichier(chemin, motif):
    if not os.path.exists(chemin):
        return set()
    with open(chemin, encoding="utf-8") as f:
        return set(re.findall(motif, f.read(), re.M))


def opt(args, nom, defaut=None):
    if nom in args:
        i = args.index(nom)
        if i + 1 < len(args):
            return args[i + 1]
    return defaut


def main():
    args = sys.argv[1:]
    sortie = opt(args, "--sortie", SORTIE)
    tout = "--tout" in args
    avec_noms = "--noms" in args

    url_forcee = opt(args, "--url")
    candidats = [url_forcee] if url_forcee else [URL_BASE % s for s in REALMS]

    html = None
    for u in candidats:
        print("Téléchargement : %s  (~19 Mo)" % u)
        try:
            html = telecharger(u)
            break
        except (urllib.error.URLError, TimeoutError) as e:
            print("  échec (%s) — realm suivant…" % e)
    if html is None:
        print("Aucun realm builder joignable.")
        return 1

    catalogue = extraire(html)
    if not catalogue:
        print("Aucune capacité extraite — la structure de la page a-t-elle changé ?")
        return 1

    connus = ids_fichier(DB_SORTS, r"^DB\[(\d+)\]=")
    corriges = (ids_fichier(CORRECTIONS, r"^DB\[(\d+)\]=")
                | ids_fichier(CORRECTIONS, r"aura\((\d+),"))
    absents = {i: n for i, n in catalogue.items()
               if i not in connus and i not in corriges}

    print("Capacités au catalogue : %d" % len(catalogue))
    print("  déjà dans DB_Sorts : %d" % len([i for i in catalogue if i in connus]))
    print("  déjà corrigées     : %d" % len([i for i in catalogue if i in corriges]))
    print("  ABSENTES (à traiter): %d" % len(absents))

    choisis = catalogue if tout else absents
    if not choisis:
        print("Rien à écrire.")
        return 0

    os.makedirs(os.path.dirname(sortie), exist_ok=True)
    with open(sortie, "w", encoding="utf-8") as f:
        f.write("# IDs récoltés du builder Ascension par recolter_builder.py\n")
        f.write("# %s\n" % ("TOUS les IDs" if tout else "IDs absents de DB_Sorts"))
        for i in sorted(choisis, key=int):
            if avec_noms:
                f.write("%s  # %s\n" % (i, choisis[i]))
            else:
                f.write("%s\n" % i)
    print("\n%d ID(s) écrits -> %s" % (len(choisis), sortie))
    print("Suite : python outils/recuperer_db.py --fichier %s --limite 100 --dry"
          % os.path.relpath(sortie, BASE).replace("\\", "/"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
