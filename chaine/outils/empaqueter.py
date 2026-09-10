# -*- coding: utf-8 -*-
"""
Fabrique le paquet de la traduction : UN seul fichier .zip, a extraire dans le
dossier du jeu.

Que des fichiers d'addon (.lua / .xml), AUCUN executable. C'est la seule
methode proposee : un installateur .exe (non signe) faisait fuir les joueurs.
Le zip reflete l'arborescence du jeu (Interface\\...), donc on l'extrait
directement dans le dossier du jeu et tout se met en place.

Usage : python outils/empaqueter.py
Sortie : traduction\\dist\\AscensionFR_manuel.zip
"""
import os
import zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JEU = r"D:\AscensionFR\WOW_Priv\resources\ascension-live"
INTERFACE = os.path.join(JEU, "Interface")
DIST = os.path.join(BASE, "dist")
ZIP_MANUEL = os.path.join(DIST, "AscensionFR_manuel.zip")

# Tout l'arbre Interface\ : l'addon principal, les repliques des PNJ, et PTRXML
# (ecran de creation en francais). Une seule extraction place le tout.
ESSENTIEL = [
    os.path.join("AddOns", "AscensionFR"),
    "PTRXML",
]
OPTIONNEL = os.path.join("AddOns", "AscensionFR_Repliques")

LISEZMOI_MANUEL = """Traduction francaise pour Project Ascension -- installation manuelle
===================================================================

Ce paquet ne contient QUE des fichiers d'addon : du texte (.lua / .xml).
Rien ne s'execute, il n'y a aucun programme a lancer. Vous pouvez ouvrir
n'importe quel fichier avec le Bloc-notes pour verifier : ce ne sont que
des traductions.

INSTALLATION (une seule extraction)
-----------------------------------
1. Reperez le dossier de votre jeu Ascension : celui qui contient DEJA un
   dossier nomme "Interface" (souvent ...\\resources\\ascension-live).

2. Extrayez ce zip DANS ce dossier.
   Windows demandera de fusionner le dossier "Interface" : dites OUI
   (Fusionner / Remplacer les fichiers). Cela n'efface aucun de vos autres
   addons -- ca ajoute seulement les notres a cote.

   Au final vous devez avoir :
     <votre jeu>\\Interface\\AddOns\\AscensionFR
     <votre jeu>\\Interface\\AddOns\\AscensionFR_Repliques
     <votre jeu>\\Interface\\PTRXML

3. Lancez le jeu jusqu'a l'ecran de SELECTION DES PERSONNAGES :
   - en bas a gauche, cliquez sur "AddOns"
   - cochez "Load Out of Date AddOns" (charger les AddOns perimes) en haut
   - verifiez qu'AscensionFR est coche, puis "Appliquer"

4. Connectez-vous. C'est en francais !

(Astuce : ce bouton "AddOns" a la selection des personnages marche a tous
 les coups. Inutile de chercher une case dans le lanceur : selon les
 versions elle change de nom ou n'existe meme pas.)

VERIFICATION
------------
Si vous n'etes pas sur d'avoir extrait au bon endroit : le dossier
"AscensionFR" doit se trouver dans "Interface\\AddOns", a cote des autres
addons. Le dossier "PTRXML", lui, va dans "Interface" (PAS dans AddOns) --
l'extraction s'en occupe toute seule.

DESINSTALLATION
---------------
Supprimez les dossiers "AscensionFR" et "AscensionFR_Repliques" dans
   <votre jeu>\\Interface\\AddOns
et le dossier "PTRXML" dans
   <votre jeu>\\Interface

SI UN TEXTE RESTE EN ANGLAIS
----------------------------
C'est possible : le jeu est immense. En jeu, tapez  /afr  pour ouvrir le
panneau de la traduction. Rien de casse -- le reste reste en francais.
Signalez-le sur le Discord : plus il y a de retours, plus ca avance vite.

Bon jeu !
"""


def ajouter_dossier(zf, disque, prefixe):
    for racine, _, fichiers in os.walk(disque):
        for nom in fichiers:
            chemin = os.path.join(racine, nom)
            rel = os.path.relpath(chemin, disque)
            zf.write(chemin, os.path.join(prefixe, rel).replace("\\", "/"))


def main():
    os.makedirs(DIST, exist_ok=True)
    tout = ESSENTIEL + [OPTIONNEL]
    manquants = [d for d in tout
                 if not os.path.isdir(os.path.join(INTERFACE, d))]
    if manquants:
        print("! dossiers absents, rien n'est emballe : %s"
              % ", ".join(manquants))
        return 1

    with zipfile.ZipFile(ZIP_MANUEL, "w", zipfile.ZIP_DEFLATED,
                         compresslevel=9) as zf:
        for rel in ESSENTIEL + [OPTIONNEL]:
            source = os.path.join(INTERFACE, rel)
            ajouter_dossier(zf, source, os.path.join("Interface", rel))
        zf.writestr("LISEZ-MOI.txt", LISEZMOI_MANUEL.replace("\n", "\r\n"))

    mo = os.path.getsize(ZIP_MANUEL) / (1024.0 * 1024.0)
    print("Paquet cree (installation manuelle, aucun executable) :")
    print("   %-40s %5.1f Mo" % (os.path.basename(ZIP_MANUEL), mo))
    print("A extraire dans le dossier du jeu (celui qui contient Interface\\).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
