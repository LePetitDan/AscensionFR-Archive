# -*- coding: utf-8 -*-
"""optimiser_memoire.py — le format PARESSEUX de DB_Objets.lua (#33, 21/07/2026).

POURQUOI
--------
Deux raisons, et la seconde est devenue vitale.

1. MÉMOIRE. Chaque entrée de table Lua coûte cher (~200 octets de structure
   en plus des textes). DB_Objets porte des centaines de milliers d'entrées
   que le joueur ne survole presque jamais toutes : on les range en MORCEAUX
   de source (des chaînes) compilés seau par seau au premier accès
   (AFR.Paresseux, Core.lua).

2. LIMITE DE COMPILATION (25/07/2026). Lua 5.1 n'accepte que 262 143
   constantes par PROTOTYPE de fonction (MAXARG_Bx ; lcode.c, addk ->
   « constant table overflow »). Une constante = une chaîne DISTINCTE ou un
   nombre DISTINCT. Au format plat, chaque « DB[21504]={N="…",D="…"} » coûte
   1 nombre + 2 chaînes : à 355 320 objets, les IDENTIFIANTS SEULS (355 320
   nombres distincts) dépassent déjà la limite. Le fichier plat ne compile
   plus du tout — l'addon serait mort au chargement.
   Au format paresseux, un seau entier = UNE chaîne longue : 2 constantes par
   seau, soit ~4 400 pour toute la base. C'est ce qui la rend générable.

QUAND
-----
Le générateur écrit DÉSORMAIS DB_Objets directement au format paresseux
(generateur_db.ecrire_db(..., paresseux=True)) : le fichier plat n'existe plus
jamais sur le disque, donc plus aucune fenêtre où l'addon serait cassé.
Cet outil reste appelable seul (fin d'ingerer_recolte.py) comme filet :
sur un fichier déjà paresseux il ne fait rien.

FORMAT PRODUIT (inchangé depuis le 21/07 — l'addon n'a rien à savoir)
--------------
    local M = {}
    M[42]=[==[ [21504]={...},[21505]={...}, ]==]
    AscensionFR.DB.Objets = AscensionFR.Paresseux(M, 512)
"""
import io
import re

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chemin_client import DB as _DB, exiger_client  # noqa: E402

CIBLE = os.path.join(_DB, "DB_Objets.lua")
TAILLE_SEAU = 512

ENTETE = (
    "-- Fichier PARESSEUX généré par outils/optimiser_memoire.py (#33).",
    "-- Un seau entier tient dans UNE chaîne longue : c'est ce qui garde la",
    "-- base sous la limite des 262 143 constantes de Lua 5.1, que le format",
    "-- plat dépasse largement. Les seaux se compilent au premier accès.",
)

ENTREE_PLATE = re.compile(r"^DB\[(\d+)\]=(\{.*\})\s*$", re.M)


def enseauter(entrees, nom_table="AscensionFR.DB.Objets",
              taille_seau=TAILLE_SEAU):
    """Rend le texte COMPLET du fichier paresseux.

    entrees : suite de couples (identifiant, corps Lua), le corps étant déjà
    sérialisé — « {N="…",D="…"} ». L'ordre reçu est conservé DANS chaque seau.
    """
    seaux = {}
    for ident, corps in entrees:
        seaux.setdefault(int(ident) // taille_seau, []).append(
            "[%s]=%s," % (ident, corps))

    lignes = list(ENTETE)
    lignes.append("local M = {}")
    for seau in sorted(seaux):
        contenu = "".join(seaux[seau])
        # niveau de crochets longs qui n'apparaît pas dans le contenu
        niveau = 2
        while ("]" + "=" * niveau + "]") in contenu:
            niveau += 1
        egal = "=" * niveau
        lignes.append("M[%d]=[%s[%s]%s]" % (seau, egal, contenu, egal))
    lignes.append("%s = AscensionFR.Paresseux(M, %d)"
                  % (nom_table, taille_seau))
    lignes.append("")
    return "\n".join(lignes)


def ecrire(chemin, contenu):
    """Écrit un fichier paresseux. newline="" : fins de ligne en LF, comme
    depuis le 21/07 — ne pas laisser Windows glisser des CRLF ici."""
    io.open(chemin, "w", encoding="utf-8", newline="").write(contenu)


def nb_seaux(identifiants, taille_seau=TAILLE_SEAU):
    """Combien de seaux pour ces identifiants (2 constantes chacun)."""
    return len({int(i) // taille_seau for i in identifiants})


def transformer(chemin=None):
    """Convertit un DB_Objets.lua PLAT déjà écrit. Idempotent."""
    chemin = chemin or CIBLE
    t = io.open(chemin, encoding="utf-8").read()
    if "AscensionFR.Paresseux" in t:
        print("DB_Objets.lua : déjà paresseux — rien à faire.")
        return 0

    entrees = ENTREE_PLATE.findall(t)
    if len(entrees) < 1000:
        print("DB_Objets.lua : %d entrées seulement — format inattendu, "
              "on ne touche à rien." % len(entrees))
        return 1

    ecrire(chemin, enseauter(entrees))
    print("DB_Objets.lua : %d entrées -> %d seaux paresseux."
          % (len(entrees), nb_seaux(i for i, _ in entrees)))
    return 0


def main():
    exiger_client("optimiser_memoire (DB_Objets paresseux)")
    return transformer(CIBLE)


if __name__ == "__main__":
    raise SystemExit(main())
