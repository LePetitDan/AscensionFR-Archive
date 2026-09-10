# -*- coding: utf-8 -*-
"""
Découpe les panneaux d'une maquette en éléments réutilisables.

Une maquette est une image figée : elle montre un panneau à UNE taille, avec
du texte dedans. L'application, elle, a besoin de panneaux VIDES et de taille
variable. On les reconstruit donc par « découpe en neuf » : les quatre coins
gardent leurs ornements, les bords et le centre sont étirés. C'est la
technique classique des interfaces de jeu.

Usage : python outils/decouper_maquette.py
"""
import os

from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAQUETTE = os.path.join(BASE, "Design", "compagnon",
                        "stitch_interface_traduction_customtkinter",
                        "rpg_companion_dashboard", "screen.png")
SORTIE = os.path.join(BASE, "compagnon", "assets", "theme")

# Zones repérées dans la maquette (768 × 1376).
PANNEAUX = {
    "bois":       (68, 178, 700, 414),     # bloc d'état
    "pierre":     (60, 440, 708, 590),     # bloc « Dossier du jeu »
    "parchemin":  (60, 612, 708, 1016),    # bloc « Contribuer »
}
# Épaisseur des coins ornementés, panneau par panneau : c'est ce qui ne doit
# JAMAIS être étiré, sous peine de déformer les ferrures.
COINS = {"bois": 58, "pierre": 46, "parchemin": 74}

# Le centre de la maquette contient le TEXTE de démonstration — l'étirer
# reviendrait à coller « Translation Status » derrière nos propres libellés.
# On prélève donc la matière (bois, pierre, parchemin) dans une zone vierge,
# repérée ici en coordonnées de la maquette, et on la répète.
MATIERE = {
    "bois":      (90, 210, 170, 300),      # bois nu, à gauche du texte
    "pierre":    (80, 470, 150, 540),
    "parchemin": (110, 860, 200, 950),
}


def neuf_tranches(image, coin):
    """Découpe une image en neuf morceaux : 4 coins, 4 bords, 1 centre.

    Les bandes horizontales (haut et bas) sont prélevées en une TRANCHE ÉTROITE
    juste après le coin gauche, puis étirées. Prendre la bande entière
    emporterait le texte de la maquette, qui est centré — c'est ce qui faisait
    réapparaître « Version 1.6 installée » derrière nos propres libellés.
    Ces bandes sont uniformes sur toute leur longueur : une tranche suffit."""
    l, h = image.size
    c = min(coin, l // 3, h // 3)
    fin = min(c + 30, l - c)               # tranche vierge après le coin
    boites = {
        "hg": (0, 0, c, c),          "hc": (c, 0, fin, c),
        "hd": (l - c, 0, l, c),      "cg": (0, c, c, h - c),
        "cc": (c, c, l - c, h - c),  "cd": (l - c, c, l, h - c),
        "bg": (0, h - c, c, h),      "bc": (c, h - c, fin, h),
        "bd": (l - c, h - c, l, h),
    }
    return {nom: image.crop(b) for nom, b in boites.items()}, c


def carreler(matiere, largeur, hauteur):
    """Répète un morceau de matière pour couvrir une surface."""
    fond = Image.new("RGBA", (largeur, hauteur))
    lm, hm = matiere.size
    for y in range(0, hauteur, hm):
        for x in range(0, largeur, lm):
            fond.paste(matiere, (x, y))
    return fond


def assembler(tranches, coin, largeur, hauteur, matiere=None):
    """Reconstruit un panneau à la taille voulue à partir des neuf morceaux."""
    c = coin
    resultat = Image.new("RGBA", (largeur, hauteur), (0, 0, 0, 0))
    milieu_l = max(1, largeur - 2 * c)
    milieu_h = max(1, hauteur - 2 * c)
    E = Image.LANCZOS
    if matiere is not None:
        resultat.paste(carreler(matiere, milieu_l, milieu_h), (c, c))
    else:
        resultat.paste(tranches["cc"].resize((milieu_l, milieu_h), E), (c, c))
    resultat.paste(tranches["hc"].resize((milieu_l, c), E), (c, 0))
    resultat.paste(tranches["bc"].resize((milieu_l, c), E), (c, hauteur - c))
    resultat.paste(tranches["cg"].resize((c, milieu_h), E), (0, c))
    resultat.paste(tranches["cd"].resize((c, milieu_h), E), (largeur - c, c))
    resultat.paste(tranches["hg"], (0, 0))
    resultat.paste(tranches["hd"], (largeur - c, 0))
    resultat.paste(tranches["bg"], (0, hauteur - c))
    resultat.paste(tranches["bd"], (largeur - c, hauteur - c))
    return resultat


# Zone INTÉRIEURE de chaque panneau, en coordonnées du panneau découpé : c'est
# la surface qu'on recouvre de matière vierge pour effacer le texte de la
# maquette, sans toucher au cadre.
INTERIEUR = {
    "bois":      (30, 40, 602, 214),
    "pierre":    (34, 26, 614, 124),
    "parchemin": (46, 40, 602, 364),
}


def panneau(nom, largeur=None):
    """Rend un panneau VIDE de la maquette.

    On ne l'ÉTIRE PAS : sa bordure haute porte un ornement centré, qu'un
    étirement déformerait. La fenêtre étant de taille fixe, on garde l'image
    entière — on se contente d'effacer le texte de démonstration en recouvrant
    l'intérieur de matière vierge, puis on met à l'échelle si besoin."""
    maquette = Image.open(MAQUETTE).convert("RGBA")
    decoupe = maquette.crop(PANNEAUX[nom]).copy()

    if nom in MATIERE and nom in INTERIEUR:
        matiere = maquette.crop(MATIERE[nom])
        gauche, haut, droite, bas = INTERIEUR[nom]
        decoupe.paste(carreler(matiere, droite - gauche, bas - haut),
                      (gauche, haut))

    if largeur and largeur != decoupe.width:
        hauteur = int(decoupe.height * largeur / float(decoupe.width))
        decoupe = decoupe.resize((largeur, hauteur), Image.LANCZOS)
    return decoupe


def main():
    os.makedirs(SORTIE, exist_ok=True)
    for nom in PANNEAUX:
        maquette = Image.open(MAQUETTE).convert("RGBA")
        maquette.crop(PANNEAUX[nom]).save(os.path.join(SORTIE,
                                                       nom + "_source.png"))
        print("  %s : source découpée" % nom)
    return 0


if __name__ == "__main__":
    main()
