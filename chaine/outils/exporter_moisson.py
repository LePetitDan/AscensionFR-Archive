# -*- coding: utf-8 -*-
r"""Exporte la moisson vers le pont PRIVÉ Dan -> cloud (programme 33, bloc B/E).

LE GESTE « CHEZ DAN, PETIT » : copier du vrai client vers le clone local du
dépôt privé AscensionFR-Moisson tout ce que le passage cloud doit LIRE, puis
pousser. Une commande, et l'usine du cloud a sa matière première.

CE QUI MONTE (et rien d'autre — le dépôt est PRIVÉ, mais on ne monte que le
nécessaire quand même) :

  jeu/Interface/AddOns/AscensionFR/DB/   les 6 bases de DÉDUP que les étapes
                                         2 et 5 lisent en --sans-pose
  jeu/WTF/Account/MOISSONn/SavedVariables/AscensionFR.lua
                                         la moisson de l'addon — le dossier de
                                         compte est RENOMMÉ (MOISSON1, 2…) :
                                         le nom du compte de Dan est une
                                         donnée personnelle, et la chaîne
                                         itère sur tous les comptes sans se
                                         soucier du nom (depuis_sauvegarde)
  noms_recolteurs.local.txt              les pseudos connus des récolteurs —
                                         le garde-fou anti-pseudo du cloud en
                                         a besoin ; sa place est le pont
                                         PRIVÉ, jamais le dépôt de code
  retour/                                (créé vide) le cloud y poussera les
                                         fichiers d'attente ; la pose se fait
                                         ici, à l'arrivée

POURQUOI GIT : un push est atomique (une machine éteinte au milieu ne laisse
jamais un demi-état), et une moisson non consommée reste dans l'historique
tant que le cloud ne l'a pas lue. C'est le critère du bloc B.

Usage : python outils/exporter_moisson.py [--sans-push]
"""
import os
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chemin_client import JEU, DB, exiger_client  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPOT_MOISSON = r"D:\AscensionFR\depot_moisson"

# Les bases que les étapes 2 et 5 LISENT en --sans-pose : Gossip, TextesPNJ,
# Communaute (dédup de la récolte), Quetes (quêtes déjà couvertes), Sorts et
# SortsCorrections (dédup des signalements). Rien d'autre : le reste des
# DB_*.lua est de la RÉGÉNÉRATION, qui reste chez Dan.
BASES_DEDUP = ("DB_Gossip.lua", "DB_TextesPNJ.lua", "DB_Communaute.lua",
               "DB_Quetes.lua", "DB_Sorts.lua", "DB_SortsCorrections.lua")


def copier(source, destination):
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    shutil.copy2(source, destination)


def main():
    exiger_client("exporter_moisson (le pont Dan -> cloud)")
    if not os.path.isdir(os.path.join(DEPOT_MOISSON, ".git")):
        print("PONT ABSENT — %s n'est pas un clone git." % DEPOT_MOISSON)
        print("  (création : voir docs/CONTEXTE_PROJET.md, programme 33)")
        return 1

    copies = 0
    # 1. Les bases de dédup, disposition client reproduite sous jeu/.
    for nom in BASES_DEDUP:
        source = os.path.join(DB, nom)
        if not os.path.isfile(source):
            print("  ! base absente du client : %s" % nom)
            continue
        copier(source, os.path.join(DEPOT_MOISSON, "jeu", "Interface",
                                    "AddOns", "AscensionFR", "DB", nom))
        copies += 1

    # 2. La moisson (SavedVariables), compte ANONYMISÉ : MOISSON1, 2…
    comptes = 0
    base_wtf = os.path.join(JEU, "WTF", "Account")
    if os.path.isdir(base_wtf):
        for compte in sorted(os.listdir(base_wtf)):
            source = os.path.join(base_wtf, compte, "SavedVariables",
                                  "AscensionFR.lua")
            if not os.path.isfile(source):
                continue
            comptes += 1
            copier(source, os.path.join(
                DEPOT_MOISSON, "jeu", "WTF", "Account",
                "MOISSON%d" % comptes, "SavedVariables", "AscensionFR.lua"))
            copies += 1
    if not comptes:
        print("  ! aucune sauvegarde AscensionFR.lua sous WTF\\Account — "
              "la moisson montera vide (les bases de dédup montent quand "
              "même).")

    # 3. Les pseudos des récolteurs : le garde-fou du cloud en a besoin.
    noms = os.path.join(BASE, "noms_recolteurs.local.txt")
    if os.path.isfile(noms):
        copier(noms, os.path.join(DEPOT_MOISSON,
                                  "noms_recolteurs.local.txt"))
        copies += 1

    # 3 bis. LA FILE À TRADUIRE (programme 37) : après un patch d'Ascension,
    # l'Atelier local recalcule a_traduire/ (il faut le client) — mais c'est
    # le cloud qui traduit quand Google met l'IP de Dan au piquet (429 du
    # 29/08 : ~30 h de blocage). La file part donc par le pont, comme tout
    # ce qui va de Dan au cloud, et le passage nocturne la pose par-dessus
    # celle de son dépôt. Ce cas se reproduira à chaque patch.
    file_locale = os.path.join(BASE, "a_traduire")
    n_file = 0
    if os.path.isdir(file_locale):
        for nom_f in sorted(os.listdir(file_locale)):
            source = os.path.join(file_locale, nom_f)
            if os.path.isfile(source):
                copier(source, os.path.join(DEPOT_MOISSON, "a_traduire",
                                            nom_f))
                n_file += 1
                copies += 1
    if n_file:
        print("  file à traduire : %d fichier(s) sur le pont" % n_file)

    # 4. Le dossier du retour (le cloud y pousse les fichiers d'attente).
    os.makedirs(os.path.join(DEPOT_MOISSON, "retour"), exist_ok=True)

    print("%d fichier(s) exporté(s) vers le pont (%d compte(s), "
          "anonymisés)." % (copies, comptes))

    if "--sans-push" in sys.argv:
        print("(--sans-push : à toi de pousser quand tu veux.)")
        return 0
    # Le push : atomique, et une panne réseau se VOIT (code 1) — la copie
    # locale reste acquise, le prochain passage poussera. Le pull --rebase
    # d'abord : le cloud dépose ses retours sur le même dépôt (vécu au 37 :
    # push rejeté parce que la nuit avait avancé le pont).
    ordres = (["git", "-C", DEPOT_MOISSON, "add", "-A"],
              ["git", "-C", DEPOT_MOISSON, "commit", "-m",
               "Moisson exportée"],
              ["git", "-C", DEPOT_MOISSON, "pull", "--rebase", "-q"],
              ["git", "-C", DEPOT_MOISSON, "push"])
    for ordre in ordres:
        code = subprocess.call(ordre)
        if code != 0 and ordre[3] == "commit":
            # Rien de neuf À COMMITTER — mais on pousse quand même : un
            # commit d'un export précédent peut attendre (vécu au 37 : le
            # « rien de neuf » court-circuitait le push d'un commit resté
            # local après un rejet de push).
            print("(rien de neuf à committer — on pousse l'existant)")
            continue
        if code != 0:
            print("ÉCHEC de « %s » (code %d) — la copie locale est faite, "
                  "relance quand le réseau revient." % (" ".join(ordre[3:]),
                                                        code))
            return 1
    print("Moisson poussée sur le pont privé : le cloud la lira à son "
          "prochain passage.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
