# -*- coding: utf-8 -*-
r"""Extrait les 4 750 sons du PackFR qui résistaient à mpyq.

Diagnostic du 22/07/2026 : ils ne sont NI chiffrés NI en compression
exotique — leurs secteurs mélangent zlib et STOCKAGE BRUT (l'audio déjà
compact est posé tel quel), et mpyq tente de « décompresser » les secteurs
bruts. On lit donc les secteurs nous-mêmes : brut si la taille rangée égale
la taille attendue, sinon l'octet de tête dit l'algorithme.

Destination : le dossier du jeu (fichiers libres, comme les 9 672 déjà
posés — le client les lit, le launcher ne nettoie que Data\) ET une copie
de préparation pour le zip voix-1.1 dans dist/voix-1.1/.

Usage : python outils/extraire_voix_recalcitrantes.py
"""
import bz2
import io
import os
import struct
import sys
import zlib

from mpyq import MPQArchive

sys.stdout.reconfigure(encoding="utf-8")
MPQ = (r"D:\AscensionFR\WorkFlow\Ajouter par Dan\PackFR"
       r"\patch-Z-frFR-1.MPQ")
LISTE = r"D:\AscensionFR\WorkFlow\sources\packfr_listfile_1.txt"
JEU = r"D:\AscensionFR\WOW_Priv\resources\ascension-live"
PREPA = r"D:\AscensionFR\WorkFlow\dist\voix-1.1"

DRAP_COMPRESS = 0x00000200
DRAP_UNITE = 0x01000000
DRAP_CHIFFRE = 0x00010000


def decompresser_secteur(secteur, attendu):
    if len(secteur) == attendu:
        return secteur                       # stocké brut
    masque = secteur[0]
    if masque == 0x02:
        return zlib.decompress(secteur[1:])
    if masque == 0x10:
        return bz2.decompress(secteur[1:])
    raise ValueError("compression inconnue : 0x%02x" % masque)


def extraire_fichier(archive, entete, taille_secteur, nom):
    entree = archive.get_hash_table_entry(nom)
    if entree is None:
        return None, "absent"
    bloc = archive.block_table[entree.block_table_index]
    if bloc.flags & DRAP_CHIFFRE:
        return None, "chiffré"
    archive.file.seek(bloc.offset + entete["offset"])
    brut = archive.file.read(bloc.archived_size)
    if not bloc.flags & DRAP_COMPRESS:
        return brut[:bloc.size], None
    if bloc.flags & DRAP_UNITE:
        try:
            return decompresser_secteur(brut, bloc.size), None
        except Exception as e:
            return None, str(e)
    nb = (bloc.size + taille_secteur - 1) // taille_secteur
    try:
        positions = struct.unpack("<%dI" % (nb + 1), brut[:4 * (nb + 1)])
    except struct.error:
        return None, "table de secteurs illisible"
    morceaux = []
    for i in range(nb):
        attendu = min(taille_secteur, bloc.size - i * taille_secteur)
        secteur = brut[positions[i]:positions[i + 1]]
        try:
            morceaux.append(decompresser_secteur(secteur, attendu))
        except Exception as e:
            return None, "secteur %d : %s" % (i, e)
    sortie = b"".join(morceaux)
    if len(sortie) != bloc.size:
        return None, "taille fausse (%d != %d)" % (len(sortie), bloc.size)
    return sortie, None


def main():
    archive = MPQArchive(MPQ, listfile=False)
    entete = archive.header
    taille_secteur = 512 << entete["sector_size_shift"]
    noms = [l.strip() for l in io.open(LISTE, encoding="utf-8",
                                       errors="replace") if l.strip()]
    poses, deja, rates = 0, 0, 0
    erreurs = {}
    octets = 0
    for nom in noms:
        cible_jeu = os.path.join(JEU, nom.replace("\\", os.sep))
        if os.path.exists(cible_jeu):
            deja += 1
            continue
        donnees, erreur = extraire_fichier(archive, entete,
                                           taille_secteur, nom)
        if donnees is None:
            if erreur != "absent":
                rates += 1
                erreurs.setdefault(erreur, nom)
            continue
        for cible in (cible_jeu,
                      os.path.join(PREPA, nom.replace("\\", os.sep))):
            os.makedirs(os.path.dirname(cible), exist_ok=True)
            with io.open(cible, "wb") as f:
                f.write(donnees)
        poses += 1
        octets += len(donnees)
        if poses % 500 == 0:
            print("  %d posés (%.0f Mo)..." % (poses, octets / 1048576),
                  flush=True)
    print("posés :", poses, "(%.0f Mo)" % (octets / 1048576),
          "| déjà présents :", deja, "| ratés :", rates)
    for e, ex in erreurs.items():
        print("   raté [%s] ex: %s" % (e, ex))


if __name__ == "__main__":
    main()
