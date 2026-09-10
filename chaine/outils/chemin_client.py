# -*- coding: utf-8 -*-
r"""LE chemin du client — un seul réglage, au lieu de constantes partout.

Le réglage : la variable d'environnement ASCENSIONFR_JEU. Absente, on
prend le chemin de la machine de Dan — comportement inchangé chez lui.

Pourquoi une variable d'environnement et pas un fichier de configuration :
le déménagement visé est une Action GitHub, où c'est UNE ligne `env:` dans
le yml ; un fichier de config serait un état de plus à embarquer, à
balayer, et qui finirait par mentir. La variable, elle, n'existe que là où
on la pose.

L'ABSENCE DU CLIENT DOIT SE VOIR (programme 31, bloc A). Le scénario de
panne à empêcher : une étape qui, sans client, lit « rien de déjà fait »
derrière une garde os.path.exists muette, DOUBLONNE tout, dépense ses
appels réseau, puis plante à l'écriture finale. D'où exiger_client() : à
appeler AU DÉMARRAGE de toute étape qui ne peut rien faire sans le client
— un message clair, le code de sortie 3, et zéro appel réseau dépensé.
"""
import os
import sys

DEFAUT = r"D:\AscensionFR\WOW_Priv\resources\ascension-live"
JEU = os.environ.get("ASCENSIONFR_JEU", DEFAUT)
ADDONS = os.path.join(JEU, "Interface", "AddOns")
ADDON = os.path.join(ADDONS, "AscensionFR")
DB = os.path.join(ADDON, "DB")

# Code de sortie réservé « client absent » : distinct de 0 (fait) et de
# 1 (planté) — l'orchestrateur peut le reconnaître et le dire tel quel.
CODE_CLIENT_ABSENT = 3


def client_present():
    """Le dossier Interface\\AddOns suffit à trancher : sans lui, rien de
    ce que la chaîne écrit n'a de destination (Data/ et WTF/ peuvent
    manquer sur une copie partielle — chaque consommateur re-vérifie son
    sous-dossier s'il en dépend)."""
    return os.path.isdir(ADDONS)


def exiger_client(etape):
    """À appeler au DÉMARRAGE de toute étape qui a besoin du client.
    Absent -> une ligne claire + sortie code 3, avant tout travail."""
    if client_present():
        return
    print("CLIENT ABSENT — %s ne peut rien faire sans le client "
          "d'Ascension." % etape)
    print("  chemin réglé : %s" % JEU)
    print("  réglage : variable d'environnement ASCENSIONFR_JEU")
    print("  arrêt AVANT tout appel réseau et toute écriture.")
    sys.stdout.flush()
    sys.exit(CODE_CLIENT_ABSENT)
