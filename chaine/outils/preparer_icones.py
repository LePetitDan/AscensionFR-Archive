# -*- coding: utf-8 -*-
"""
Prépare les icônes livrées par Stitch/Claude Design pour Windows.

Deux corrections systématiques :

  1. Les générateurs d'images DESSINENT le damier gris censé représenter la
     transparence. Le fichier est donc 100 % opaque, et l'icône s'afficherait
     avec un carré à damier autour d'elle. On repère ce fond et on le rend
     réellement transparent.
  2. Un .ico Windows doit contenir PLUSIEURS tailles : l'explorateur choisit
     la bonne selon l'affichage. Un .ico à une seule taille est flou partout
     ailleurs.

Usage :
  python outils/preparer_icones.py <image.png> <sortie.ico>
"""
import os
import sys

from PIL import Image, ImageDraw

TAILLES = [256, 128, 64, 48, 32, 24, 16]


def est_fond(pixel):
    """Vrai pour le damier : un gris clair, sans couleur dominante.
    L'icône, elle, est sombre ou franchement colorée (or, bleu)."""
    r, v, b = pixel[:3]
    return max(r, v, b) - min(r, v, b) < 14 and (r + v + b) / 3 > 180


def cadre_du_contenu(image):
    """La boîte englobant l'icône, damier exclu."""
    largeur, hauteur = image.size
    pixels = image.load()
    gauche, haut = largeur, hauteur
    droite, bas = 0, 0
    pas = max(1, largeur // 400)          # échantillonnage : inutile de tout lire
    for y in range(0, hauteur, pas):
        for x in range(0, largeur, pas):
            if not est_fond(pixels[x, y]):
                gauche, haut = min(gauche, x), min(haut, y)
                droite, bas = max(droite, x), max(bas, y)
    return gauche, haut, droite, bas


def nettoyer(image):
    """Rend transparent tout ce qui est hors de l'icône, coins arrondis
    compris."""
    image = image.convert("RGBA")
    gauche, haut, droite, bas = cadre_du_contenu(image)
    cote = max(droite - gauche, bas - haut)
    # On recentre sur un carré : les icônes livrées sont carrées.
    cx, cy = (gauche + droite) // 2, (haut + bas) // 2
    demi = cote // 2
    boite = (cx - demi, cy - demi, cx + demi, cy + demi)

    # On rogne de 1 % et on arrondit un peu plus que le dessin : sinon il
    # subsiste un liseré de damier le long des bords et dans les coins.
    marge = max(3, int(cote * 0.028))
    interieur = (boite[0] + marge, boite[1] + marge,
                 boite[2] - marge, boite[3] - marge)
    masque = Image.new("L", image.size, 0)
    d = ImageDraw.Draw(masque)
    d.rounded_rectangle(interieur, radius=int(cote * 0.22), fill=255)
    image.putalpha(masque)
    return image.crop(boite)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    source, sortie = sys.argv[1], sys.argv[2]
    image = Image.open(source)
    propre = nettoyer(image)

    apercu = os.path.splitext(sortie)[0] + "_apercu.png"
    propre.resize((512, 512), Image.LANCZOS).save(apercu)
    propre.save(sortie, format="ICO",
                sizes=[(t, t) for t in TAILLES])
    print("  %s  (%d tailles)" % (sortie, len(TAILLES)))
    print("  %s  (pour vérifier à l'œil)" % apercu)
    coin = propre.convert("RGBA").getpixel((2, 2))
    print("  coin haut-gauche : alpha=%d %s"
          % (coin[3], "-> transparent ✓" if coin[3] == 0 else "-> ENCORE OPAQUE"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
