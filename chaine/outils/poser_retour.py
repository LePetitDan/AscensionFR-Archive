# -*- coding: utf-8 -*-
r"""Pose chez Dan ce que le cloud a traduit et mis en attente (prog. 33).

LE GESTE « À L'ARRIVÉE » : le passage cloud traduit mais ne touche jamais le
client — ses lignes Lua partent en attente sur le pont PRIVÉ, sous
retour/<nom>_<run>.txt (un fichier PAR passage : un retour non posé n'est
jamais écrasé par le passage suivant). Ce script tire le pont, pose chaque
fichier dans le client, puis consigne la consommation (suppression commitée
— le contenu reste dans l'historique du pont).

CE QUI EST POSÉ, ET COMMENT :
  retour/communaute_en_attente_*.txt  -> DB_Communaute.lua (entête à garde
                                         inversée d'ingerer_recolte : une
                                         ligne posée deux fois est un
                                         non-événement en jeu — garde() et
                                         quete() ne remplissent que les trous)
  retour/corrections_en_attente_*.txt -> DB_SortsCorrections.lua (helper
                                         aura() d'ingerer_rapport)

BARRIÈRE D'INTÉGRITÉ : chaque ligne doit avoir une des formes attendues
(G[...], T[...], quete(...), aura(...), commentaire, vide). Une ligne
inconnue = le fichier ENTIER est refusé et reste sur le pont — on ne pose
pas « presque sûr » dans le client.

Usage : python outils/poser_retour.py [--dry]
"""
import glob
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chemin_client import DB, exiger_client  # noqa: E402
from ingerer_recolte import ENTETE  # noqa: E402  (la MÊME entête, importée)

DEPOT_MOISSON = r"D:\AscensionFR\depot_moisson"
RETOUR = os.path.join(DEPOT_MOISSON, "retour")

# L'entête d'ingerer_rapport (main), reproduite à l'identique : le fichier
# de corrections doit porter le helper aura() avant la première ligne.
ENTETE_AURA = ("local DB = AscensionFR.DB.Sorts\n"
               "local function aura(id, de2, d2)\n"
               "    if DB[id] then DB[id].DE2 = de2; DB[id].D2 = d2 end\n"
               "end\n")

# (motif de ligne autorisée, cible, garde d'entête, entête, marqueur)
POSES = (
    ("communaute_en_attente_*.txt",
     re.compile(r'^(G\[|T\[|quete\(\d+,\s*")'),
     "DB_Communaute.lua", "local function quete(", ENTETE,
     "-- --- Posé depuis le retour cloud (poser_retour.py) ---"),
    ("corrections_en_attente_*.txt",
     re.compile(r"^aura\(\d+,"),
     "DB_SortsCorrections.lua", "local function aura(", ENTETE_AURA,
     "-- --- Posé depuis le retour cloud (poser_retour.py) ---"),
)


def poser_fichier(chemin, motif, cible, garde, entete, marqueur, dry):
    """Pose un fichier d'attente dans `cible`. Rend (posées, refus)."""
    with open(chemin, encoding="utf-8") as f:
        lignes = [l.rstrip("\n") for l in f]
    utiles = []
    for l in lignes:
        if not l.strip() or l.lstrip().startswith("--"):
            continue
        if not motif.match(l):
            print("  🛑 ligne inattendue dans %s — fichier REFUSÉ, il "
                  "reste sur le pont :" % os.path.basename(chemin))
            print("     %s" % l[:120])
            return 0, 1
        utiles.append(l)
    contenu = ""
    if os.path.exists(cible):
        with open(cible, encoding="utf-8") as f:
            contenu = f.read()
    # Propreté seulement : en jeu, un doublon est déjà un non-événement.
    neuves = [l for l in utiles if l not in contenu]
    if not neuves:
        print("  = %s : %d ligne(s), toutes déjà posées."
              % (os.path.basename(chemin), len(utiles)))
        return 0, 0
    if dry:
        print("  --dry %s : %d ligne(s) à poser." %
              (os.path.basename(chemin), len(neuves)))
        return len(neuves), 0
    with open(cible, "a", encoding="utf-8") as f:
        if garde not in contenu:
            f.write(entete)
        f.write("\n%s\n%s\n" % (marqueur, "\n".join(neuves)))
    print("  + %s : %d ligne(s) posée(s) (%d déjà là)."
          % (os.path.basename(chemin), len(neuves),
             len(utiles) - len(neuves)))
    return len(neuves), 0


def main():
    exiger_client("poser_retour (l'arrivée du pont cloud -> Dan)")
    dry = "--dry" in sys.argv
    # Tirer le pont d'abord ; hors ligne, on pose ce qui est déjà là.
    if subprocess.call(["git", "-C", DEPOT_MOISSON, "pull", "--ff-only"]):
        print("(pull du pont impossible — je pose ce qui est déjà tiré.)")

    total, refus, consommes = 0, 0, []
    for gabarit, motif, nom_cible, garde, entete, marqueur in POSES:
        cible = os.path.join(DB, nom_cible)
        for chemin in sorted(glob.glob(os.path.join(RETOUR, gabarit))):
            posees, r = poser_fichier(chemin, motif, cible, garde,
                                      entete, marqueur, dry)
            total += posees
            refus += r
            if not r and not dry:
                consommes.append(chemin)

    # Consommation CONSIGNÉE : suppression + commit + push — le contenu
    # reste dans l'historique du pont, le prochain passage ne reverra rien.
    if consommes:
        for chemin in consommes:
            os.remove(chemin)
        subprocess.call(["git", "-C", DEPOT_MOISSON, "add", "-A"])
        subprocess.call(["git", "-C", DEPOT_MOISSON, "commit", "-m",
                         "Retour posé chez Dan (%d fichier(s))"
                         % len(consommes)])
        if subprocess.call(["git", "-C", DEPOT_MOISSON, "push"]):
            print("(push du pont impossible — la pose est FAITE, la "
                  "consommation partira au prochain export.)")

    if not total and not refus and not consommes:
        print("Rien en retour sur le pont : le client est à jour.")
    else:
        print("%d ligne(s) posée(s), %d fichier(s) consommé(s), %d refus."
              % (total, len(consommes), refus))
    return 1 if refus else 0


if __name__ == "__main__":
    sys.exit(main())
