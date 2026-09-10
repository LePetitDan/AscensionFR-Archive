# -*- coding: utf-8 -*-
"""Relève toutes les globales que le CODE DU CLIENT lit, et écrit
DB/DB_LuesClient.lua : ces chaînes ne seront jamais traduites.

Pourquoi
--------
Un addon ne peut pas écrire une variable du jeu sans la « souiller » (taint) —
c'est le principe même de la protection anti-triche, il n'y a pas de
contournement. Si du code protégé lit ensuite cette variable, l'action en
cours est refusée : le joueur ne peut plus lancer ses sorts, la barre du
familier ne s'affiche plus, etc.

Trois correctifs (1.6.1 → 1.6.3) ont tenté de lister les coupables au fur et
à mesure des signalements. Mesure faite le 19/07/2026 : **2 207 chaînes
traduites sont lues par le code du client, réparties sur 170 fichiers**. Une
liste construite à partir des plaintes ne pouvait pas converger.

On inverse donc la logique : au lieu de lister ce qui casse, on liste tout ce
que le client LIT, et on n'y touche pas. Il reste ~84 % des chaînes
d'interface, celles que le client se contente d'AFFICHER.

Limite assumée : une lecture entièrement dynamique
(`_G["ERR_" .. suffixe]`) échappe à l'analyse. C'est pourquoi l'addon garde
la soupape `/afr interface`, qui coupe cette partie et rien d'autre.

Usage :
    python outils/extraire_lues_client.py [--ecrire]
"""
import glob
import io
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JEU = r"D:\AscensionFR\WOW_Priv\resources\ascension-live"
DATA = os.path.join(JEU, "Data")
DB = os.path.join(JEU, "Interface", "AddOns", "AscensionFR", "DB")
SORTIE = os.path.join(DB, "DB_LuesClient.lua")

# ATTENTION — leçon du 19/07/2026, version 1.6.4.
#
# Cet outil lisait `sources/framexml/*.lua`, un dossier extrait à la main :
# 330 fichiers. Le client en contient **855**. La liste noire a donc été
# construite sur 39 % du code, et des joueurs sont restés bloqués après la
# 1.6.4 (signalé sur la classe Féticheur).
#
# On lit désormais les MPQ du client directement : c'est la seule source qui
# ne puisse pas être en retard sur le jeu. Ne jamais revenir à un dossier
# extrait à la main.

# Un nom de globale de WoW : MAJUSCULES, chiffres, tirets bas.
NOM = r"[A-Z][A-Z0-9_]{4,}"
# Lecture directe : le nom apparaît seul, sans « = » derrière (sinon c'est
# une écriture, pas une lecture) et sans point devant (sinon c'est un champ).
DIRECTE = re.compile(r'(?<![\w."])(' + NOM + r')(?!\s*=[^=])')
# Lectures indirectes : _G["NOM"] et getglobal("NOM").
INDIRECTE = re.compile(r'(?:_G|getglobal)\s*[\[(]\s*["\'](' + NOM + r')["\']')


def cles_traduites():
    chemin = os.path.join(DB, "DB_Interface.lua")
    texte = io.open(chemin, encoding="utf-8").read()
    return set(re.findall(r'DB\["([^"]+)"\]=', texte))


def fichiers_interface():
    """Tous les .lua d'interface du client, lus dans ses archives.

    Rend un dict {nom_court: contenu}. Les archives sont parcourues dans
    l'ordre alphabétique ; un même nom présent dans plusieurs archives est
    donc lu plusieurs fois, ce qui ne gêne pas : on ne fait qu'accumuler des
    noms de globales.
    """
    from mpyq import MPQArchive
    archives = sorted(glob.glob(os.path.join(DATA, "*.MPQ"))
                      + glob.glob(os.path.join(DATA, "enUS", "*.MPQ")))
    if not archives:
        raise SystemExit("archives du client introuvables : " + DATA)

    textes = {}
    for chemin in archives:
        try:
            archive = MPQArchive(chemin, listfile=True)
            noms = archive.files or []
        except Exception:
            continue          # archive sans index : on fait sans
        for nom in noms:
            if isinstance(nom, bytes):
                nom = nom.decode("latin-1")
            if not nom.lower().endswith(".lua"):
                continue
            if "interface" not in nom.lower():
                continue
            try:
                donnees = archive.read_file(nom)
            except Exception:
                continue
            if donnees:
                textes[nom.lower()] = donnees.decode("utf-8", "replace")
    return textes


def globales_lues(traduites):
    textes = fichiers_interface()
    lues, concernes = set(), 0
    for texte in textes.values():
        trouve = (set(DIRECTE.findall(texte))
                  | set(INDIRECTE.findall(texte))) & traduites
        if trouve:
            concernes += 1
        lues |= trouve
    return lues, len(textes), concernes


def ecrire(noms):
    lignes = [
        "-- Globales LUES par le code du client : ne jamais les traduire.",
        "--",
        "-- Un addon ne peut pas écrire une variable du jeu sans la souiller.",
        "-- Si du code protégé la lit ensuite, l'action du joueur est refusée",
        "-- (sorts bloqués, barre du familier masquée...). On laisse donc en",
        "-- anglais tout ce que le client lit, et on ne traduit que ce qu'il",
        "-- se contente d'afficher.",
        "--",
        "-- Généré par outils/extraire_lues_client.py — ne pas éditer à la main.",
        "local DB = AscensionFR.DB.LuesClient",
    ]
    for nom in sorted(noms):
        lignes.append('DB["%s"]=true' % nom)
    io.open(SORTIE, "w", encoding="utf-8", newline="\n").write(
        "\n".join(lignes) + "\n")


def main():
    traduites = cles_traduites()
    lues, nb_fichiers, nb_concernes = globales_lues(traduites)
    garde = len(traduites) - len(lues)
    print("fichiers du client analysés : %d (%d concernés)"
          % (nb_fichiers, nb_concernes))
    print("chaînes d'interface traduites: %d" % len(traduites))
    print("  lues par le client (bloquées): %5d (%.0f%%)"
          % (len(lues), 100.0 * len(lues) / len(traduites)))
    print("  conservées en français      : %5d (%.0f%%)"
          % (garde, 100.0 * garde / len(traduites)))

    if "--ecrire" in sys.argv:
        ecrire(lues)
        print()
        print("écrit : %s" % SORTIE)
    else:
        print()
        print("(essai à blanc — relancer avec --ecrire pour appliquer)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
