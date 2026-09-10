# -*- coding: utf-8 -*-
"""
GlobalStrings.dbc : les chaînes maison d'Ascension.

Découverte du 17/07/2026. Le client d'Ascension charge, en plus des
GlueStrings/GlobalStrings habituelles, un DBC maison — `Extensions.dll` cite
`DBFilesClient\\GlobalStrings.dbc` dans sa table de DBC — dont chaque
enregistrement est une paire (étiquette, valeur) posée comme variable globale
Lua. C'est de là que sortent les fiches techniques de classe de l'écran de
création : `CharacterCreate.lua` lit `_G["CLASS_COMBAT_STYLE_"..classe..n]`
et `GetFlavorText("CLASS_"..classe)` sans que rien, dans les 1 300 fichiers
de leur archive d'interface, ne les définisse.

Piège relevé à la lecture : **l'étiquette n'est pas le nom affiché**. La
classe qui s'affiche « Primalist » s'appelle `WILDWALKER` en interne
(`CLASS_COMBAT_STYLE_WILDWALKER0`). Croiser par nom afficherait n'importe
quoi ; on ne croise que par étiquette.

Usage : python outils/extraire_globalstrings_dbc.py [--tout]
"""
import json
import os
import struct
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JEU = r"D:\AscensionFR\WOW_Priv\resources\ascension-live"
ARCHIVE = os.path.join(JEU, "Data", "patch-M.MPQ")
INTERNE = "DBFilesClient\\GlobalStrings.dbc"
COPIE = os.path.join(BASE, "sources", "dbc", "GlobalStrings_Ascension.dbc")
SORTIE = os.path.join(BASE, "a_traduire", "glue_classes.json")


def extraire():
    from mpyq import MPQArchive
    a = MPQArchive(ARCHIVE, listfile=False)
    donnees = a.read_file(INTERNE)
    if getattr(a, "file", None):
        a.file.close()
    if not donnees:
        raise SystemExit("%s introuvable dans %s" % (INTERNE, ARCHIVE))
    os.makedirs(os.path.dirname(COPIE), exist_ok=True)
    with open(COPIE, "wb") as f:
        f.write(donnees)
    return donnees


# Disposition relevée en lisant les enregistrements, pas devinée :
#   champ 2 = étiquette (« CLASS_COMBAT_STYLE_WILDWALKER0 »)
#   champ 3 = valeur, emplacement enUS ; les 15 suivants sont vides.
# Les champs 0 et 1 portent des nombres qui, pris pour des décalages,
# tombent au milieu du bloc et donnent des fragments de phrase — c'est ce
# qui avait fait dérailler une première lecture « intelligente ».
CHAMP_ETIQUETTE = 2
CHAMP_VALEUR = 3
NB_CHAMPS_ATTENDU = 20


def lire(donnees):
    """{ étiquette: valeur } lues aux emplacements relevés."""
    magic, nb, nb_champs, taille, taille_bloc = struct.unpack(
        "<4sIIII", donnees[:20])
    if magic != b"WDBC":
        raise SystemExit("magic %r inattendu" % magic)
    if nb_champs != NB_CHAMPS_ATTENDU:
        raise SystemExit(
            "GlobalStrings.dbc : %d champs, %d attendus — Ascension a changé "
            "la structure, relire avant de continuer"
            % (nb_champs, NB_CHAMPS_ATTENDU))
    bloc = donnees[20 + nb * taille:]

    def texte(decalage):
        if not decalage or decalage >= len(bloc):
            return ""
        fin = bloc.find(b"\x00", decalage)
        brut = bloc[decalage:fin if fin != -1 else len(bloc)]
        try:
            return brut.decode("utf-8")
        except UnicodeDecodeError:
            return brut.decode("latin-1")

    chaines = {}
    for i in range(nb):
        enreg = struct.unpack_from("<%dI" % nb_champs, donnees,
                                   20 + i * taille)
        etiquette = texte(enreg[CHAMP_ETIQUETTE])
        valeur = texte(enreg[CHAMP_VALEUR])
        if etiquette and valeur:
            chaines[etiquette] = valeur
    return chaines, nb, nb_champs, taille


# Ce que l'écran de création lit dans ces globales (voir CharacterCreate.lua,
# fonction CharCreateClassButtonMixin:OnEnter).
#
# Les rôles, l'armure et les ressources sont nommés un par un, pas par
# préfixe : « ROLE_ » ou « ARMOR_ » ratisseraient des chaînes que l'écran de
# création n'affiche pas (ARMOR_PENETRATION, ARMOR_TEMPLATE...). On ne
# traduit que ce qu'on a vu s'afficher.
#
#   roles.Tank -> ROLE_TEXT_WITH_ICON.TANK, bâti sur TANK / HEALER /
#   MELEE_DAMAGER..., armorTypes -> ARMOR_TYPE_*, et les ressources sont
#   lues par `_G[resource]` (ENERGY, MANA...). Ces globales existent aussi en
#   jeu, mais on ne les écrit QUE dans le fichier de glue : l'addon, lui, ne
#   les touche pas.
CREATION_EXACTES = {
    # Rôles affichés dans l'info-bulle de classe
    "TANK", "HEALER", "SUPPORT", "DAMAGER",
    "MELEE_DAMAGER", "RANGED_DAMAGER", "CASTER_DAMAGER",
    # Types d'armure
    "ARMOR_TYPE_PLATE", "ARMOR_TYPE_MAIL", "ARMOR_TYPE_LEATHER",
    "ARMOR_TYPE_CLOTH",
    # Ressources (« Ressource principale : ... »)
    "MANA", "RAGE", "ENERGY", "FOCUS", "RUNIC_POWER", "HAPPINESS",
    "STATIC", "SOLAR_POWER", "LUNAR_POWER", "SOUL_SHARDS", "HOLY_POWER",
    "CHI", "INSANITY", "MAELSTROM", "FURY", "PAIN", "RUNES",
    # Entêtes
    "COMBAT_STYLE", "PRIMARY_RESOURCE",
}


def est_de_creation(etiquette):
    return (etiquette.startswith("CLASS_COMBAT_STYLE_")
            or etiquette.startswith("CLASS_")
            or etiquette in CREATION_EXACTES)


def main():
    donnees = extraire()
    chaines, nb, nb_champs, taille = lire(donnees)
    print("GlobalStrings.dbc : %d enregistrements, %d champs, %d o/enreg"
          % (nb, nb_champs, taille))
    print("Chaînes lues      : %d" % len(chaines))

    creation = {k: v for k, v in chaines.items() if est_de_creation(k)}
    print("Dont écran de création : %d" % len(creation))
    styles = [k for k in creation if k.startswith("CLASS_COMBAT_STYLE_")]
    print("   styles de combat : %d" % len(styles))

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as f:
        json.dump(creation, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("-> %s" % SORTIE)

    if "--tout" in sys.argv:
        tout = os.path.join(BASE, "a_traduire", "glue_globalstrings.json")
        with open(tout, "w", encoding="utf-8") as f:
            json.dump(chaines, f, ensure_ascii=False, indent=1, sort_keys=True)
        print("-> %s (les %d)" % (tout, len(chaines)))

    print()
    for cle in ("CLASS_WILDWALKER", "CLASS_COMBAT_STYLE_WILDWALKER0",
                "COMBAT_STYLE", "PRIMARY_RESOURCE"):
        v = chaines.get(cle)
        print("   %-32s %s" % (cle, (v[:70] + "...") if v else "ABSENTE"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
