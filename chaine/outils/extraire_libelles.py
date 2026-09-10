# -*- coding: utf-8 -*-
"""
Extrait les libellés d'interface stockés dans les DBC : sous-classes d'objets
(« Crossbows » -> « Arbalètes ») et lignes de compétence / métiers
(« Blacksmithing » -> « Forge »).

Ces textes apparaissent dans la fenêtre des métiers et le grimoire. Ils ne
viennent ni du serveur ni des GlobalStrings, mais des DBC du client — donc
seul un remplacement à l'affichage, par l'addon, peut les traduire.

Produit traductions/libelles.json : { texteAnglais: texteFrançais }
"""
import json
import os
import struct

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DBC = os.path.join(BASE, "sources", "dbc")
JEU = r"D:\AscensionFR\WOW_Priv\resources\ascension-live"
FRFR = os.path.join(BASE, "sources", "patch-frFR-3.MPQ")


def extraire_mpq(archive, interne, sortie):
    from mpyq import MPQArchive
    a = MPQArchive(archive)
    donnees = a.read_file(interne)
    with open(sortie, "wb") as f:
        f.write(donnees)
    return sortie


def lire(chemin):
    with open(chemin, "rb") as f:
        b = f.read()
    magic, nb, nch, ts, sb = struct.unpack("<4sIIII", b[:20])
    if magic != b"WDBC":
        raise ValueError("%s : pas un DBC" % chemin)
    donnees = b[20:20 + nb * ts]
    bloc = b[20 + nb * ts:]
    enregs = [struct.unpack_from("<%dI" % nch, donnees, i * ts)
              for i in range(nb)]
    return enregs, bloc, nch


def texte(bloc, decalage):
    if not decalage or decalage >= len(bloc):
        return ""
    fin = bloc.find(b"\x00", decalage)
    brut = bloc[decalage:fin if fin != -1 else len(bloc)]
    try:
        return brut.decode("utf-8")
    except UnicodeDecodeError:
        return brut.decode("latin-1")


def premier_texte(enreg, bloc, base, nb_langues=16):
    """Premier emplacement de langue non vide d'un champ localisé."""
    for i in range(nb_langues):
        if base + i >= len(enreg):
            break
        t = texte(bloc, enreg[base + i])
        if t:
            return t
    return ""


# Structures des DBC 3.3.5 (build 12340). Un champ localisé occupe 17 champs :
# 16 emplacements de langue + 1 de drapeaux.
#   ItemSubClass : 0=ClassID 1=SubClassID ... 10=DisplayName(loc) 27=VerboseName(loc)
#   SkillLine    : 0=ID 1=CategoryID 2=SkillCostsID 3=DisplayName(loc) 20=Description(loc)
#   ChrClasses   : 0=ID ... 4=Name(loc)
#   ChrRaces     : 0=ID ... 14=Name(loc)
STRUCTURES = {
    "ItemSubClass": {"nb_champs": 44, "cle": (0, 1), "nom": 10},
    "SkillLine": {"nb_champs": 56, "cle": (0,), "nom": 3},
    "ChrClasses": {"nb_champs": 60, "cle": (0,), "nom": 4},
    "ChrRaces": {"nb_champs": 69, "cle": (0,), "nom": 14},
}

# Les classes maison d'Ascension (22 sur 32) n'existent pas chez Blizzard :
# aucun frFR officiel à réutiliser. Ce sont des noms propres de jeu — un
# traducteur automatique les massacre (« Reaper » -> « Moissonneuse »). On les
# écrit donc à la main, avec les conventions de Blizzard France.
#
# À RECENSER, JAMAIS DEVINER : cette liste vient de ChrClasses.dbc d'Ascension
# (32 enregistrements). La table codée en dur dans Core.lua avait été devinée
# et inventait des classes inexistantes (« Son of Arugal », « Bard », « Monk »)
# tout en manquant les vraies (« Templar », « Felsworn », « Runemaster »).
CLASSES_MAISON = {
    "Hero": "Héros",
    "Barbarian": "Barbare",
    "Witch Doctor": "Féticheur",
    "Felsworn": "Gangrelige",
    "Witch Hunter": "Chasseur de sorcières",
    "Stormbringer": "Porte-tempête",
    "Knight of Xoroth": "Chevalier de Xoroth",
    "Guardian": "Gardien",
    "Templar": "Templier",
    "Bloodmage": "Mage de sang",
    "Ranger": "Rôdeur",
    "Chronomancer": "Chronomancien",
    "Necromancer": "Nécromancien",
    "Pyromancer": "Pyromancien",
    "Cultist": "Cultiste",
    "Starcaller": "Mande-étoiles",
    "Sun Cleric": "Clerc du soleil",
    "Tinker": "Bricoleur",
    # « Vénénomancien » (13 signes) débordait du bouton de l'écran de
    # création, qui affichait « Vénénomanci… ». Deux signes de moins suffisent,
    # et la forme est plus proche de l'anglais.
    "Venomancer": "Vénomancien",
    "Reaper": "Faucheur",
    "Primalist": "Primaliste",
    "Runemaster": "Maître des runes",
}


def tous_les_noms(chemin, structure):
    """Tous les noms non vides d'un DBC — pour savoir ce qui existe vraiment."""
    s = STRUCTURES[structure]
    enregs, bloc, _ = lire(chemin)
    return [n for n in (premier_texte(e, bloc, s["nom"]) for e in enregs) if n]


def paires(chemin_en, chemin_fr, structure):
    """Construit { texteEN: texteFR } en appariant par clé d'enregistrement."""
    s = STRUCTURES[structure]
    e_en, b_en, n_en = lire(chemin_en)
    e_fr, b_fr, n_fr = lire(chemin_fr)
    for nom, nch in (("enUS", n_en), ("frFR", n_fr)):
        if nch != s["nb_champs"]:
            raise ValueError(
                "%s %s : %d champs, %d attendus — structure DBC inattendue"
                % (structure, nom, nch, s["nb_champs"]))
    index_fr = {}
    for e in e_fr:
        cle = tuple(e[c] for c in s["cle"])
        index_fr[cle] = premier_texte(e, b_fr, s["nom"])
    resultat = {}
    for e in e_en:
        cle = tuple(e[c] for c in s["cle"])
        en = premier_texte(e, b_en, s["nom"])
        fr = index_fr.get(cle)
        if en and fr and en != fr:
            resultat[en] = fr
    return resultat


def main():
    os.makedirs(DBC, exist_ok=True)
    libelles = {}

    # --- Sous-classes d'objets (« Crossbows », « Polearms »...) -------------
    # Clé : (ClassID, SubClassID) -> champs 0 et 1
    extraire_mpq(os.path.join(JEU, "Data", "enUS", "patch-enUS-3.MPQ"),
                 "DBFilesClient\\ItemSubClass.dbc",
                 os.path.join(DBC, "ItemSubClass_enUS.dbc"))
    extraire_mpq(FRFR, "DBFilesClient\\ItemSubClass.dbc",
                 os.path.join(DBC, "ItemSubClass_frFR.dbc"))
    sc = paires(os.path.join(DBC, "ItemSubClass_enUS.dbc"),
                os.path.join(DBC, "ItemSubClass_frFR.dbc"), "ItemSubClass")
    print("Sous-classes d'objets : %d" % len(sc))
    libelles.update(sc)

    # --- Lignes de compétence / métiers (« Blacksmithing »...) --------------
    # Clé : ID -> champ 0
    extraire_mpq(os.path.join(JEU, "Data", "enUS", "patch-enUS-3.MPQ"),
                 "DBFilesClient\\SkillLine.dbc",
                 os.path.join(DBC, "SkillLine_enUS.dbc"))
    extraire_mpq(FRFR, "DBFilesClient\\SkillLine.dbc",
                 os.path.join(DBC, "SkillLine_frFR.dbc"))
    sl = paires(os.path.join(DBC, "SkillLine_enUS.dbc"),
                os.path.join(DBC, "SkillLine_frFR.dbc"), "SkillLine")
    print("Lignes de compétence : %d" % len(sl))
    libelles.update(sl)

    # --- Races et classes --------------------------------------------------
    # Elles apparaissent dans les info-bulles des joueurs et la feuille de
    # personnage. Le client les tire de ses DBC : ni le serveur ni les
    # GlobalStrings ne les portent, seul l'affichage peut être traduit.
    # Les DBC d'Ascension vivent dans patch-M.MPQ (avec SkillLine/Talent).
    ASC = os.path.join(JEU, "Data", "patch-M.MPQ")
    for structure, etiquette in (("ChrClasses", "Classes"),
                                 ("ChrRaces", "Races")):
        interne = "DBFilesClient\\%s.dbc" % structure
        extraire_mpq(ASC, interne,
                     os.path.join(DBC, "%s_Ascension.dbc" % structure))
        extraire_mpq(FRFR, interne,
                     os.path.join(DBC, "%s_frFR.dbc" % structure))
        paires_officielles = paires(
            os.path.join(DBC, "%s_Ascension.dbc" % structure),
            os.path.join(DBC, "%s_frFR.dbc" % structure), structure)
        print("%s (frFR officiel) : %d" % (etiquette, len(paires_officielles)))
        libelles.update(paires_officielles)

    # Les classes maison d'Ascension, absentes du frFR officiel.
    noms_asc = set(tous_les_noms(
        os.path.join(DBC, "ChrClasses_Ascension.dbc"), "ChrClasses"))
    maison = {en: fr for en, fr in CLASSES_MAISON.items() if en in noms_asc}
    print("Classes maison (traduites à la main) : %d" % len(maison))
    libelles.update(maison)
    # « Mage », « Paladin »... s'écrivent pareil en français : le DBC frFR les
    # porte, `paires` les a écartés faute de différence. Rien à signaler.
    identiques = set(tous_les_noms(
        os.path.join(DBC, "ChrClasses_frFR.dbc"), "ChrClasses"))
    manquantes = sorted(noms_asc - set(libelles) - identiques)
    if manquantes:
        print("  ! classes sans traduction : %s" % ", ".join(manquantes))
    inventees = sorted(set(CLASSES_MAISON) - noms_asc)
    if inventees:
        print("  ! classes de notre liste absentes du jeu : %s"
              % ", ".join(inventees))

    sortie = os.path.join(BASE, "traductions", "libelles.json")
    existant = {}
    if os.path.exists(sortie):
        with open(sortie, encoding="utf-8") as f:
            existant = json.load(f)
    existant.update(libelles)
    with open(sortie, "w", encoding="utf-8") as f:
        json.dump(existant, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("\nTOTAL : %d libellés -> %s" % (len(existant), sortie))
    for k in ["Crossbows", "Polearms", "Staves", "Blacksmithing", "Alchemy",
              "Mining", "Engineering", "Cloth", "Leather", "Two-Handed Swords"]:
        if k in existant:
            print("   %-22s -> %s" % (k, existant[k]))


if __name__ == "__main__":
    main()
