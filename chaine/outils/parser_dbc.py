# -*- coding: utf-8 -*-
"""
Parseur de Spell.dbc (World of Warcraft 3.3.5a, build 12340).

Format DBC :
  En-tête 20 octets : magic('WDBC') nbEnreg nbChamps tailleEnreg tailleBlocTexte
  Puis les enregistrements (uint32 chacun), puis le bloc de chaînes.
  Les champs texte contiennent un décalage dans le bloc de chaînes.

Spell.dbc 3.3.5 : 234 champs de 4 octets (936 o/enregistrement).
Les champs localisés occupent 17 champs : 16 emplacements de langue + drapeaux.
  champ 0   : ID
  champ 136 : SpellName    (136..151 langues, 152 drapeaux)
  champ 153 : Rank         (rang du sort : « Rang 2 »)
  champ 170 : Description  (texte de l'info-bulle détaillée)
  champ 187 : ToolTip      (texte court au survol de la barre d'action)

Usage :
  python parser_dbc.py <Spell.dbc> <sortie.json> [--langue N]
"""
import json
import struct
import sys

CHAMP_ID = 0
CHAMP_NOM = 136
CHAMP_RANG = 153
CHAMP_DESCRIPTION = 170
CHAMP_TOOLTIP = 187


def lire_dbc(chemin):
    """Retourne (enregistrements, bloc_texte, nb_champs)."""
    with open(chemin, "rb") as f:
        entete = f.read(20)
        magic, nb, nb_champs, taille, taille_bloc = struct.unpack(
            "<4sIIII", entete)
        if magic != b"WDBC":
            raise ValueError("magic %r inattendu dans %s" % (magic, chemin))
        donnees = f.read(nb * taille)
        bloc = f.read(taille_bloc)
    return donnees, bloc, nb, nb_champs, taille


def texte(bloc, decalage):
    """Lit une chaîne terminée par zéro dans le bloc de textes."""
    if not decalage or decalage >= len(bloc):
        return ""
    fin = bloc.find(b"\x00", decalage)
    if fin == -1:
        fin = len(bloc)
    brut = bloc[decalage:fin]
    if not brut:
        return ""
    try:
        return brut.decode("utf-8")
    except UnicodeDecodeError:
        return brut.decode("latin-1")


def champ_localise(enreg, bloc, base, langue_preferee=None):
    """Lit un champ localisé : renvoie le premier emplacement non vide.

    Les clients localisés ne remplissent qu'un seul des 16 emplacements ;
    lequel varie selon la construction du fichier, on les balaie donc tous.
    """
    ordre = range(16)
    if langue_preferee is not None:
        ordre = [langue_preferee] + [i for i in range(16) if i != langue_preferee]
    for i in ordre:
        t = texte(bloc, enreg[base + i])
        if t:
            return t
    return ""


def parser_spell(chemin, langue_preferee=None, garder_vides=False):
    donnees, bloc, nb, nb_champs, taille = lire_dbc(chemin)
    if nb_champs < 234:
        raise ValueError("%s : %d champs, format Spell.dbc 3.3.5 attendu (234)"
                         % (chemin, nb_champs))
    resultat = {}
    fmt = "<%dI" % nb_champs
    for i in range(nb):
        enreg = struct.unpack_from(fmt, donnees, i * taille)
        sid = enreg[CHAMP_ID]
        nom = champ_localise(enreg, bloc, CHAMP_NOM, langue_preferee)
        if not nom and not garder_vides:
            continue  # sort technique sans nom : invisible pour le joueur
        entree = {"N": nom}
        rang = champ_localise(enreg, bloc, CHAMP_RANG, langue_preferee)
        desc = champ_localise(enreg, bloc, CHAMP_DESCRIPTION, langue_preferee)
        tt = champ_localise(enreg, bloc, CHAMP_TOOLTIP, langue_preferee)
        if rang:
            entree["R"] = rang
        if desc:
            entree["D"] = desc
        if tt:
            entree["T"] = tt
        resultat[str(sid)] = entree
    return resultat


if __name__ == "__main__":
    chemin = sys.argv[1]
    sortie = sys.argv[2]
    langue = None
    if "--langue" in sys.argv:
        langue = int(sys.argv[sys.argv.index("--langue") + 1])
    d = parser_spell(chemin, langue)
    with open(sortie, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("%s : %d sorts nommés -> %s" % (chemin, len(d), sortie))
