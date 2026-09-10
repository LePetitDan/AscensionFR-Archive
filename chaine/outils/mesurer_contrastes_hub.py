# -*- coding: utf-8 -*-
"""
Mesure les contrastes du Hub, texte par texte — la preuve du lot 12.
====================================================================
L'audit du 26/07/2026 avait mesuré à la main que tout texte posé sur la
texture de bois était illisible (1,4 à 3,2 pour 1 ; seuil 4,5) ; la passe UX
exige la re-mesure « texte par texte » comme seule preuve d'acceptation.
L'outil de mesure n'existait pas : le voici, et il MORD (code retour 1 si un
seul texte passe sous son seuil).

Méthode (celle de l'audit, écrite noir sur blanc cette fois) :
  - rapport de contraste WCAG 2.x : (L1 + 0,05) / (L2 + 0,05), L = luminance
    relative sRGB ;
  - seuils : 4,5:1 pour le texte courant, 3:1 pour le grand texte (titres de
    panneau en Morpheus 26 px) ;
  - le fond est une TEXTURE bruitée : sa clarté varie d'une lettre à l'autre.
    On échantillonne donc les vrais pixels du fond sous la zone du texte
    (capture --demo), on écarte les pixels du texte lui-même (proches de sa
    couleur), et on retient le PIRE DÉCILE — pas la moyenne : un texte n'est
    lisible que si ses passages les plus défavorables le sont ;
  - les textes CONTOURÉS (titres or + contour noir, sous-titres cuits) se
    mesurent contre leur contour : c'est lui qui porte la lisibilité, quelle
    que soit la texture dessous.

Usage : python outils/mesurer_contrastes_hub.py [--garder-captures]
"""
import os
import subprocess
import sys
import tempfile
import warnings

from PIL import Image

# Pillow 12 annonce la retraite de getdata() pour 2027 ; le banc n'a pas à
# crier pour ça à chaque passe.
warnings.filterwarnings("ignore", category=DeprecationWarning)

sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPAGNON = os.path.join(BASE, "compagnon")

# --------------------------------------------------------------------------- #
# La palette du Hub (recopiée d'interface_hub.py — vérifiée par le banc :
# un écart entre les deux ferait mesurer des couleurs qui n'existent pas).
# --------------------------------------------------------------------------- #
ENCRE = "#3d2b12"
ENCRE_DOUCE = "#5a4020"
OR_SOMBRE = "#8a6a2a"
BEIGE = "#e9dcbb"
BEIGE_VIF = "#fff2cc"
OR_VIF = "#ffd100"
VERT = "#2f7f2a"
P_VERT = "#7fd06a"
P_ROUGE = "#ff8f70"
P_TEXTE = BEIGE
P_TEXTE_VIF = BEIGE_VIF
P_OR = OR_VIF
TON_SUCCES = "#1f5a1c"
CONTOUR_NOIR = "#000000"
CONTOUR_BRUN = "#1e1206"      # (30,18,6) : contour des sous-titres cuits

SEUIL = 4.5
SEUIL_GRAND = 3.0


def rgb(hexa):
    hexa = hexa.lstrip("#")
    return tuple(int(hexa[i:i + 2], 16) for i in (0, 2, 4))


def luminance(c):
    def lin(v):
        v /= 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in c[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(c1, c2):
    l1, l2 = luminance(c1), luminance(c2)
    clair, sombre = max(l1, l2), min(l1, l2)
    return (clair + 0.05) / (sombre + 0.05)


# --------------------------------------------------------------------------- #
# L'inventaire : chaque texte de l'audit, plus ceux que la passe a déplacés.
# (vue, libellé, mode, couleur_texte, zone_ou_contour, grand?)
#   mode "zone"    : (x0, y0, x1, y1) sur la capture 1080×680 — le fond est
#                    échantillonné là, pixels du texte écartés ;
#   mode "contour" : la couleur du contour — mesure directe couleur/contour.
# --------------------------------------------------------------------------- #
TEXTES = [
    # --- Accueil ---
    ("accueil", "titre de vue « Accueil »", "contour", OR_VIF,
     CONTOUR_NOIR, True),
    ("accueil", "verdict « Tout est à jour » (plaque)", "zone", P_VERT,
     (326, 104, 700, 134), True),
    ("accueil", "lien « Vérifier mon installation » (plaque)", "zone",
     P_TEXTE, (326, 140, 560, 158), False),
    ("accueil", "« Tout lire ↗ » (encre sur panneau)", "zone", ENCRE,
     (930, 322, 1004, 338), False),
    ("accueil", "libellé de tuile (« Textes traduits »)", "zone",
     ENCRE_DOUCE, (330, 188, 440, 204), False),
    ("accueil", "patch-note (panneau nouvelles)", "zone", ENCRE_DOUCE,
     (290, 362, 990, 480), False),
    # --- Traduction ---
    ("traduction", "titre de vue « Traduction »", "contour", OR_VIF,
     CONTOUR_NOIR, True),
    ("traduction", "titre de panneau « Mise à jour disponible »", "zone",
     OR_SOMBRE, (480, 144, 812, 172), True),
    ("traduction", "« Dossier du jeu : » (plaque)", "zone", P_TEXTE_VIF,
     (286, 438, 400, 454), False),
    ("traduction", "chemin du dossier de jeu (plaque)", "zone", P_TEXTE,
     (404, 438, 900, 454), False),
    ("traduction", "« nouvelle version de l'application » (plaque)", "zone",
     P_OR, (286, 468, 900, 484), False),
    ("traduction", "lien « Vérifier mon installation » (plaque)", "zone",
     P_TEXTE, (286, 498, 520, 514), False),
    ("traduction", "lien « Tout désinstaller » (plaque)", "zone", P_ROUGE,
     (850, 498, 1012, 514), False),
    # --- Voix ---
    ("voix", "titre de vue « Voix françaises »", "contour", OR_VIF,
     CONTOUR_NOIR, True),
    ("voix", "sous-titre de vue (cuit, contouré)", "contour", BEIGE_VIF,
     CONTOUR_BRUN, False),
    ("voix", "titre de panneau « Voix françaises installées »", "zone",
     VERT, (490, 188, 812, 216), True),
    ("voix", "conséquence sous « Couper les voix »", "zone", ENCRE_DOUCE,
     (440, 406, 850, 422), False),
    ("voix", "note de bas de vue (plaque)", "zone", P_TEXTE,
     (290, 478, 1000, 494), False),
    ("voix", "le % de la jauge (remonté sur le parchemin)", "zone", ENCRE,
     (600, 268, 690, 288), False),
    # --- Addons ---
    ("addons", "titre de vue « Addons »", "contour", OR_VIF,
     CONTOUR_NOIR, True),
    ("addons", "sous-titre de vue (cuit, contouré)", "contour", BEIGE_VIF,
     CONTOUR_BRUN, False),
    ("addons", "nom d'une carte d'addon", "zone", ENCRE,
     (348, 146, 560, 164), False),
    ("addons", "description d'une carte d'addon", "zone", ENCRE_DOUCE,
     (348, 168, 600, 200), False),
    # --- Contribuer ---
    ("contribuer", "titre de vue « Contribuer »", "contour", OR_VIF,
     CONTOUR_NOIR, True),
    ("contribuer", "libellé de la case « envoi automatique »", "zone",
     ENCRE, (322, 378, 900, 394), False),
    ("contribuer", "barre d'état (« Tout est à jour. Bon jeu ! »)", "zone",
     TON_SUCCES, (300, 612, 900, 632), False),
]


def mesurer_zone(image, couleur_texte, boite):
    """Le pire décile du contraste entre la couleur du texte et les pixels
    du FOND dans la boîte (pixels du texte écartés par proximité)."""
    zone = image.crop(boite).convert("RGB")
    texte = rgb(couleur_texte)
    fonds = []
    for pixel in zone.getdata():
        if sum(abs(a - b) for a, b in zip(pixel, texte)) < 150:
            continue                       # un pixel du texte (anticrénelage)
        fonds.append(pixel)
    if not fonds:
        return None
    ratios = sorted(ratio(texte, p) for p in fonds)
    return ratios[len(ratios) // 10]       # pire décile


def main():
    garder = "--garder-captures" in sys.argv
    dossier = os.path.join(tempfile.gettempdir(), "afr_contrastes_hub")
    os.makedirs(dossier, exist_ok=True)
    vues = sorted({t[0] for t in TEXTES})
    captures = {}
    for vue in vues:
        chemin = os.path.join(dossier, vue + ".png")
        r = subprocess.run(
            [sys.executable, os.path.join(COMPAGNON, "interface_hub.py"),
             "--demo", vue, "--capture", chemin],
            capture_output=True, cwd=COMPAGNON)
        if r.returncode != 0 or not os.path.exists(chemin):
            print("! capture impossible pour la vue", vue)
            return 2
        captures[vue] = Image.open(chemin)

    print("Contraste mesuré, texte par texte (seuil %.1f:1, grand texte "
          "%.1f:1) — pire décile sur le vrai fond :" % (SEUIL, SEUIL_GRAND))
    print()
    echecs = 0
    for vue, libelle, mode, couleur, cible, grand in TEXTES:
        seuil = SEUIL_GRAND if grand else SEUIL
        if mode == "contour":
            valeur = ratio(rgb(couleur), rgb(cible))
        else:
            valeur = mesurer_zone(captures[vue], couleur, cible)
        if valeur is None:
            verdict, echecs = "? (zone illisible)", echecs + 1
            valeur_txt = "   ?"
        else:
            ok = valeur >= seuil
            echecs += 0 if ok else 1
            verdict = "ok" if ok else "SOUS LE SEUIL"
            valeur_txt = "%4.1f" % valeur
        print("  %-10s  %-52s %s:1  %s"
              % (vue, libelle, valeur_txt, verdict))
    print()
    if echecs:
        print("%d texte(s) sous le seuil — la passe n'est pas terminée."
              % echecs)
        return 1
    print("TOUS les textes au-dessus du seuil.")
    if not garder:
        for vue in vues:
            try:
                os.remove(os.path.join(dossier, vue + ".png"))
            except OSError:
                pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
