# -*- coding: utf-8 -*-
"""VITRINE GITHUB avec les VRAIES textures de WoW (pack Gethe, fourni par
Dan le 22/07). Fabrique dans depot_github/assets/vitrine :

  banniere.png         2560x800  parchemin + cadre or + dragon + titre
  separateur.png       1600x~44  le vrai séparateur de boîte de dialogue
  vignette_sociale.png 1280x640  pour Settings -> Social preview (Discord)
  etape_telecharger/installer/jouer.png  160x160  case + icône du jeu

Les polices OFFICIELLES (MORPHEUS pour les titres, FRIZQT pour le corps)
sont extraites de locale-enUS.MPQ au premier passage, cache sources/fonts.

Usage : python outils/fabriquer_vitrine_github.py
(relisible et rejouable à volonté ; ne pousse RIEN — git reste manuel)
"""
import io
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(BASE, "Ajouter par Dan", "wow-ui-textures")
SORTIE = os.path.join(BASE, "depot_github", "assets", "vitrine")
POLICES = os.path.join(BASE, "sources", "fonts")
MPQ_LOCALE = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Data\enUS\locale-enUS.MPQ"

OR_TITRE = (255, 209, 0)
BRUN_SOMBRE = (58, 36, 16)
BRUN_TEXTE = (75, 46, 21)


def texture(*chemin):
    return Image.open(os.path.join(PACK, *chemin)).convert("RGBA")


def police(nom, taille):
    return ImageFont.truetype(os.path.join(POLICES, nom), taille)


def extraire_polices():
    os.makedirs(POLICES, exist_ok=True)
    manquantes = [n for n in ("MORPHEUS.TTF", "FRIZQT__.TTF")
                  if not os.path.exists(os.path.join(POLICES, n))]
    if not manquantes:
        return
    from mpyq import MPQArchive
    archive = MPQArchive(MPQ_LOCALE, listfile=True)
    for nom in manquantes:
        donnees = archive.read_file("Fonts\\" + nom)
        if not donnees:
            raise SystemExit("police introuvable dans le MPQ : " + nom)
        with io.open(os.path.join(POLICES, nom), "wb") as f:
            f.write(donnees)
        print("police extraite :", nom, "(%d Ko)" % (len(donnees) // 1024))


# ----------------------------------------------------------------------------
# Cadre doré : UI-DialogBox-Gold-Border est un atlas de 8 cases (convention
# des EdgeFile de WoW) : GAUCHE DROITE HAUT BAS + 4 coins (HG HD BG BD).
# ----------------------------------------------------------------------------
def decouper_bordure():
    atlas = texture("DialogFrame", "UI-DialogBox-Gold-Border.PNG")
    case = atlas.width // 8
    return [atlas.crop((i * case, 0, (i + 1) * case, atlas.height))
            for i in range(8)], case


def grossir(img, ech):
    return img.resize((img.width * ech, img.height * ech), Image.NEAREST)


def bande(piece, longueur, verticale):
    """Une rangée de tuiles montée à plat (paste, pas composite) : les
    ombres douces des tuiles ne se doublent pas aux chevauchements."""
    c = piece.width
    if verticale:
        strip = Image.new("RGBA", (c, longueur))
        for y in list(range(0, longueur - c, c)) + [longueur - c]:
            strip.paste(piece, (0, y))
    else:
        strip = Image.new("RGBA", (longueur, c))
        for x in list(range(0, longueur - c, c)) + [longueur - c]:
            strip.paste(piece, (x, 0))
    return strip


def poser_cadre(toile, ech):
    pieces, case = decouper_bordure()
    c = case * ech
    gauche, droite, barre, _fine, hg, hd, bg, bd = [grossir(p, ech)
                                                    for p in pieces]
    # Étalonné sur planche d'essais (22/07) : la case 3 sert aux DEUX
    # bords horizontaux — tournée à 270° pour le haut, à 90° pour le
    # bas (chaque rotation aligne la barre sur les bras des coins). La
    # case 4 (barre fine) n'est PAS un bord de cadre — ignorée.
    haut = barre.transpose(Image.ROTATE_270)
    bas = barre.transpose(Image.ROTATE_90)
    L, H = toile.size
    toile.alpha_composite(bande(haut, L - 2 * c, False), (c, 0))
    toile.alpha_composite(bande(bas, L - 2 * c, False), (c, H - c))
    toile.alpha_composite(bande(gauche, H - 2 * c, True), (0, c))
    toile.alpha_composite(bande(droite, H - 2 * c, True), (L - c, c))
    toile.alpha_composite(hg, (0, 0))
    toile.alpha_composite(hd, (L - c, 0))
    toile.alpha_composite(bg, (0, H - c))
    toile.alpha_composite(bd, (L - c, H - c))


def fond_parchemin(L, H):
    parchemin = texture("ACHIEVEMENTFRAME",
                        "UI-Achievement-Parchment-Horizontal.PNG")
    # Le pourtour de la texture est assombri : gardé, il dessine une
    # COUTURE à chaque raccord de tuile. On le rogne avant de tuiler.
    r = 20
    parchemin = parchemin.crop((r, r, parchemin.width - r,
                                parchemin.height - r))
    tuile = parchemin.resize((H * 2, H), Image.LANCZOS)
    fond = Image.new("RGBA", (L, H))
    x, miroir = 0, False
    while x < L:
        fond.paste(tuile.transpose(Image.FLIP_LEFT_RIGHT) if miroir
                   else tuile, (x, 0))
        x += tuile.width
        miroir = not miroir
    return fond


def texte_ombre(toile, xy, texte, fonte, remplir, contour, epaisseur,
                ancre="mm"):
    d = ImageDraw.Draw(toile)
    x, y = xy
    # ombre portée douce
    ombre = Image.new("RGBA", toile.size)
    ImageDraw.Draw(ombre).text((x + 6, y + 8), texte, font=fonte,
                               fill=(20, 10, 0, 180), anchor=ancre,
                               stroke_width=epaisseur,
                               stroke_fill=(20, 10, 0, 180))
    toile.alpha_composite(ombre.filter(ImageFilter.GaussianBlur(6)))
    d.text((x, y), texte, font=fonte, fill=remplir, anchor=ancre,
           stroke_width=epaisseur, stroke_fill=contour)


def tricolore(toile, cx, y, largeur=340, hauteur=14):
    d = ImageDraw.Draw(toile)
    tiers = largeur // 3
    x0 = cx - largeur // 2
    for i, coul in enumerate(((0, 32, 159), (255, 255, 255),
                              (210, 16, 52))):
        d.rectangle((x0 + i * tiers, y, x0 + (i + 1) * tiers, y + hauteur),
                    fill=coul, outline=BRUN_SOMBRE, width=2)


def composer(L, H, ech, titre_px, sous_px, sous_texte, ligne3=None):
    toile = fond_parchemin(L, H)
    poser_cadre(toile, ech)

    cx = L // 2 + 20 * ech
    cy = H // 2 - 12 * ech
    fonte_titre = police("MORPHEUS.TTF", titre_px)
    texte_ombre(toile, (cx, cy), "AscensionFR",
                fonte_titre, OR_TITRE, BRUN_SOMBRE,
                max(4, titre_px // 28))
    # Le dragon doré LOVÉ AUTOUR DU « A » (demande de Dan, 22/07) : posé
    # APRÈS le titre pour passer devant, sa courbe épouse la première
    # lettre — les ratios viennent d'essais visuels.
    g, h_, _, b = ImageDraw.Draw(toile).textbbox(
        (cx, cy), "AscensionFR", font=fonte_titre, anchor="mm")
    dragon = texture("DialogFrame", "UI-DialogBox-Gold-Dragon.PNG")
    cote = int((b - h_) * 1.8)
    dragon = dragon.resize((cote, cote), Image.LANCZOS)
    toile.alpha_composite(dragon, (int(g - cote * 0.30),
                                   int(h_ - cote * 0.18)))
    texte_ombre(toile, (cx, cy + titre_px // 2 + sous_px),
                sous_texte, police("FRIZQT__.TTF", sous_px),
                BRUN_TEXTE, (238, 220, 180), 2)
    y_ligne = cy + titre_px // 2 + sous_px + sous_px // 2 + 8 * ech
    if ligne3:
        texte_ombre(toile, (cx, y_ligne + 10),
                    ligne3, police("FRIZQT__.TTF", int(sous_px * 0.72)),
                    (96, 62, 30), (238, 220, 180), 1)
        y_ligne += sous_px + 8 * ech
    tricolore(toile, cx, y_ligne, largeur=110 * ech, hauteur=4 * ech)
    return toile


def fabriquer_banniere():
    toile = composer(2560, 800, 3, 236, 72,
                     "Project Ascension en français")
    toile.save(os.path.join(SORTIE, "banniere.png"))
    print("banniere.png            2560x800")


def fabriquer_vignette_sociale():
    toile = composer(1280, 640, 2, 150, 48,
                     "Project Ascension en français",
                     "660 000 textes · installation en 1 clic ·"
                     " voix françaises")
    toile.save(os.path.join(SORTIE, "vignette_sociale.png"))
    print("vignette_sociale.png    1280x640 (Settings -> Social preview)")


def fabriquer_separateur():
    divi = texture("DialogFrame", "UI-DialogBox-Divider.PNG")
    # bouts conservés, centre étiré : 16 px de chaque côté
    bout = 16
    L = 1600
    ech = 3
    h = divi.height * ech
    gauche = grossir(divi.crop((0, 0, bout, divi.height)), ech)
    droite = grossir(divi.crop((divi.width - bout, 0, divi.width,
                                divi.height)), ech)
    centre = divi.crop((bout, 0, divi.width - bout, divi.height)) \
        .resize((L - 2 * bout * ech, h), Image.LANCZOS)
    toile = Image.new("RGBA", (L, h))
    toile.alpha_composite(gauche, (0, 0))
    toile.alpha_composite(centre, (bout * ech, 0))
    toile.alpha_composite(droite, (L - bout * ech, 0))
    toile.save(os.path.join(SORTIE, "separateur.png"))
    print("separateur.png          %dx%d" % (L, h))


ETAPES = {
    "etape_telecharger.png": "INV_Letter_15.PNG",
    "etape_installer.png": "INV_Misc_Wrench_01.PNG",
    "etape_jouer.png": "Ability_Warrior_RallyingCry.PNG",
}


def fabriquer_etapes():
    case = texture("Buttons", "UI-Quickslot2.PNG")
    for sortie, icone_nom in ETAPES.items():
        icone = texture("ICONS", icone_nom)
        toile = Image.new("RGBA", (160, 160))
        # l'icône sous la case : la case déborde de ~12 px autour du trou
        marge_trou = int(160 * 12 / case.width)
        cote = 160 - 2 * marge_trou
        ic = icone.resize((cote, cote), Image.LANCZOS)
        toile.alpha_composite(ic, (marge_trou, marge_trou))
        toile.alpha_composite(case.resize((160, 160), Image.LANCZOS), (0, 0))
        toile.save(os.path.join(SORTIE, sortie))
        print(sortie.ljust(23), "160x160 (%s)" % icone_nom)


# Vignettes latérales : même construction que les étapes (case + icône du
# jeu), en 240 px pour rester nettes à l'affichage 120.
VIGNETTES = {
    # parchemin scellé = le rapport qui part ; gros bouton rouge = le
    # Compagnon « installation en 1 clic » (choisis sur planche d'essai).
    "vignette_contribuer.png": "INV_Scroll_03.PNG",
    "vignette_compagnon.png": "INV_Misc_EngGizmos_27.PNG",
}


def fabriquer_vignettes():
    case = texture("Buttons", "UI-Quickslot2.PNG")
    for sortie, icone_nom in VIGNETTES.items():
        icone = texture("ICONS", icone_nom)
        toile = Image.new("RGBA", (240, 240))
        marge = int(240 * 12 / case.width)
        cote = 240 - 2 * marge
        toile.alpha_composite(icone.resize((cote, cote), Image.LANCZOS),
                              (marge, marge))
        toile.alpha_composite(case.resize((240, 240), Image.LANCZOS), (0, 0))
        toile.save(os.path.join(SORTIE, sortie))
        print(sortie.ljust(23), "240x240 (%s)" % icone_nom)


def fabriquer_bouton_cafe():
    bouton = texture("Buttons", "UI-Panel-Button-Up.PNG")
    # la texture a des marges transparentes asymétriques : sans ce
    # recadrage, le centrage du texte est faux par rapport au bouton VU
    bouton = bouton.crop(bouton.getbbox())
    L, H = 360, bouton.height * 3
    bout = 12
    gauche = grossir(bouton.crop((0, 0, bout, bouton.height)), 3)
    droite = grossir(bouton.crop((bouton.width - bout, 0, bouton.width,
                                  bouton.height)), 3)
    centre = bouton.crop((bout, 0, bouton.width - bout, bouton.height)) \
        .resize((L - 2 * bout * 3, H), Image.LANCZOS)
    toile = Image.new("RGBA", (L, H))
    toile.alpha_composite(gauche, (0, 0))
    toile.alpha_composite(centre, (bout * 3, 0))
    toile.alpha_composite(droite, (L - bout * 3, 0))
    # chope + libellé, groupés au centre
    icone = texture("ICONS", "INV_Drink_15.PNG")
    r = 5   # le liseré sombre baké dans l'icône
    icone = icone.crop((r, r, icone.width - r, icone.height - r)) \
        .resize((34, 34), Image.LANCZOS)
    fonte = police("FRIZQT__.TTF", 27)
    d = ImageDraw.Draw(toile)
    texte = "Offrir un café"
    l_texte = d.textlength(texte, font=fonte)
    x0 = (L - (34 + 10 + l_texte)) // 2
    toile.alpha_composite(icone, (int(x0), (H - 34) // 2))
    d.text((x0 + 44, H // 2), texte, font=fonte, fill=OR_TITRE,
           anchor="lm", stroke_width=2, stroke_fill=(40, 10, 10))
    toile.save(os.path.join(SORTIE, "bouton_cafe.png"))
    print("bouton_cafe.png         %dx%d" % (L, H))


def main():
    extraire_polices()
    os.makedirs(SORTIE, exist_ok=True)
    fabriquer_banniere()
    fabriquer_vignette_sociale()
    fabriquer_separateur()
    fabriquer_etapes()
    fabriquer_vignettes()
    fabriquer_bouton_cafe()
    print("VITRINE FABRIQUÉE dans", SORTIE)


if __name__ == "__main__":
    main()
