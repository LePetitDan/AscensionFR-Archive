# -*- coding: utf-8 -*-
"""
traduire_hautsfaits.py — les hauts faits (Achievement.dbc) en français.

POURQUOI
--------
Les info-bulles des Épreuves affichent des hauts faits (« [Monk] Slow and
Steady », « Complete the … challenge as a Templar. »). Ces textes vivent dans
Achievement.dbc — 22 617 entrées chez Ascension.

LA CHANCE À SAISIR
------------------
Le WoW de base a une traduction OFFICIELLE : notre `sources/patch-frFR-3.MPQ`
contient l'Achievement.dbc français de Blizzard (1 817 entrées, colonnes de
langue 6 et 23). On apparie par identifiant, et on ne garde le français
officiel QUE si Ascension n'a pas modifié le texte anglais (même règle que
generateur_db pour les quêtes : identique → officiel, sinon machine). Le
reste — le custom d'Ascension — part à la traduction machine, avec cache.

FORMAT (vérifié sur les fichiers réels, 62 champs) :
    champ 0 = identifiant
    titre   : enUS = 4,  frFR = 6
    desc    : enUS = 21, frFR = 23

L'ÉCRITURE SE FAIT EN DEUX FOIS : la base est écrite une première fois avec
le français officiel seul (disponible en une minute), puis réécrite complète
à la fin de la traduction machine. On peut donc /reload sans attendre.

Usage : python outils/traduire_hautsfaits.py [--dry]
"""
import glob
import io
import json
import os
import re
import struct
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from traduire_gisement import traduire  # noqa: E402
import traduire_epreuves as te  # noqa: E402  (sur, echapper, parait_lisible)
from garde_packfr import texte_sain  # noqa: E402
from generateur_db import polir  # noqa: E402

DATA = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Data"
FRFR_MPQ = os.path.join(BASE, "sources", "patch-frFR-3.MPQ")
# Le PackFR retrouvé par Dan (21/07) : l'Achievement.dbc de l'ancien pack
# officiel du serveur — le français HUMAIN des hauts faits CUSTOM. Écrit
# dans les colonnes enUS (le pack remplaçait les fichiers du client).
# Archive SANS liste interne : lecture directe par chemin, listfile=False.
PACKFR_MPQ = os.path.join(BASE, "Ajouter par Dan", "PackFR",
                          "patch-Z-frFR-2.MPQ")
SORTIE = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
          r"\AscensionFR\DB\DB_HautsFaits.lua")
DOSSIER = os.path.join(BASE, "hautsfaits")
CACHE = os.path.join(DOSSIER, "cache.json")

TITRE_EN, DESC_EN = 4, 21
TITRE_FR, DESC_FR = 6, 23

# La chaîne OFFICIELLE enUS, dans l'ordre de chargement du vrai client.
# L'ordre alphabétique trahit ici : « patch-enUS.MPQ » trie APRÈS
# « patch-enUS-3.MPQ » alors qu'il se charge AVANT. On la fixe à la main.
CHAINE_OFFICIELLE = ["locale-enUS.MPQ", "patch-enUS.MPQ",
                     "patch-enUS-2.MPQ", "patch-enUS-3.MPQ"]

# Corrections écrites à la main (contresens de la machine). Priment sur tout.
MANUEL = {}


def lire_achievements(donnees, idx_titre, idx_desc):
    """{id: (titre, description)} depuis un Achievement.dbc."""
    if not donnees or donnees[:4] != b"WDBC":
        return {}
    nb, champs, taille, bloc = struct.unpack("<4I", donnees[4:20])
    debut = 20 + nb * taille
    chaines = donnees[debut:debut + bloc]

    def texte(v):
        if v <= 0 or v >= len(chaines):
            return ""
        fin = chaines.find(b"\0", v)
        return chaines[v:fin].decode("utf-8", "replace")

    out = {}
    for i in range(nb):
        base = 20 + i * taille
        vals = struct.unpack("<%dI" % champs, donnees[base:base + taille])
        out[vals[0]] = (texte(vals[idx_titre]), texte(vals[idx_desc]))
    return out


def extraire_de(chemin_mpq):
    """Le Achievement.dbc d'une archive, ou None."""
    try:
        from mpyq import MPQArchive
        archive = MPQArchive(chemin_mpq, listfile=True)
        noms = archive.files or []
    except Exception:
        return None
    for nom in noms:
        if isinstance(nom, bytes):
            nom = nom.decode("latin-1")
        if nom.lower().endswith("achievement.dbc"):
            try:
                return archive.read_file(nom)
            except Exception:
                return None
    return None


def ecrire(paires):
    lignes = ["-- Fichier généré par outils/traduire_hautsfaits.py "
              "- NE PAS ÉDITER.",
              "-- Hauts faits (Achievement.dbc) : français officiel de "
              "Blizzard quand le",
              "-- texte n'a pas été modifié par Ascension, machine sinon.",
              "local DB = AscensionFR.DB.HautsFaits"]
    for anglais in sorted(paires):
        # 26 des 30 « bassin d'Arathi » de cette base viennent de
        # l'Achievement.dbc frFR officiel, donc hors de portée
        # d'appliquer_vocabulaire.py : on harmonise à l'écriture.
        lignes.append('DB["%s"]="%s"'
                      % (te.echapper(anglais),
                         te.echapper(polir(paires[anglais],
                                          anglais=anglais))))
    with io.open(SORTIE, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")
    print("écrit : %s (%d textes)" % (os.path.basename(SORTIE), len(paires)))


def main():
    dry = "--dry" in sys.argv

    # 1) Ascension : toutes les archives, la dernière copie l'emporte.
    asc = {}
    for chemin in sorted(glob.glob(os.path.join(DATA, "*.MPQ"))
                         + glob.glob(os.path.join(DATA, "enUS", "*.MPQ"))):
        d = extraire_de(chemin)
        if d:
            asc.update(lire_achievements(d, TITRE_EN, DESC_EN))

    # 2) Officiel enUS : la chaîne dans le BON ordre.
    stock = {}
    for nom in CHAINE_OFFICIELLE:
        d = extraire_de(os.path.join(DATA, "enUS", nom))
        if d:
            stock.update(lire_achievements(d, TITRE_EN, DESC_EN))

    # 3) Officiel frFR.
    frfr = lire_achievements(extraire_de(FRFR_MPQ), TITRE_FR, DESC_FR)

    # 3 bis) PackFR : français humain des customs, dans les colonnes enUS.
    packfr = {}
    try:
        from mpyq import MPQArchive
        d = MPQArchive(PACKFR_MPQ, listfile=False).read_file(
            "DBFilesClient\\Achievement.dbc")
        # leur outil d'époque a écrit le français aux colonnes 7 et 24
        # (décalage +3 sur enUS — vérifié empiriquement le 21/07).
        packfr = lire_achievements(d, 7, 24)
    except Exception as e:
        print("PackFR hauts faits indisponible :", e)

    print("hauts faits Ascension : %d | officiel enUS : %d | frFR : %d "
          "| PackFR : %d" % (len(asc), len(stock), len(frfr), len(packfr)))

    paires, customs = {}, set()
    packfr_pris = 0
    for i, (titre, desc) in asc.items():
        s = stock.get(i, ("", ""))
        f = frfr.get(i, ("", ""))
        p = packfr.get(i, ("", ""))
        for k, texte in ((0, titre), (1, desc)):
            texte = texte.strip()
            if not texte or not re.search(r"[A-Za-z]{3}", texte):
                continue
            if texte == s[k].strip() and f[k].strip() \
                    and f[k].strip() != texte:
                paires[texte] = f[k].strip()
            elif p[k].strip() and p[k].strip() != texte \
                    and texte_sain(p[k]):
                # Couche PACKFR (21/07) : le français HUMAIN de l'ancien
                # pack officiel pour les customs — prime sur la machine.
                # texte_sain : leur pack contenait des réponses de robot
                # traducteur et de l'allemand (38 hauts faits touchés).
                paires[texte] = p[k].strip().replace(chr(160), " ")
                packfr_pris += 1
            else:
                customs.add(texte)
    # Un même texte peut être officiel via un id et custom via un autre
    # (copies « Realm First! ») : l'officiel gagne.
    customs -= set(paires)
    customs = {t for t in customs if te.parait_lisible(t)}

    # « Realm First! X » : des milliers de copies dont le cœur X est déjà
    # traduit par ailleurs (officiel ou custom). L'addon les COMPOSE à
    # l'affichage (« Premier du royaume ! » + cœur, règle dans Epreuves.lua) :
    # inutile de payer une traduction machine par copie.
    PREFIXE_REALM = "Realm First! "
    composables = set()
    for t in customs:
        if t.startswith(PREFIXE_REALM):
            coeur = t[len(PREFIXE_REALM):]
            if coeur in paires or coeur in customs:
                composables.add(t)
    customs -= composables
    print("« Realm First! » composés à l'affichage : %d" % len(composables))

    print("appariés à l'officiel : %d (dont PackFR : %d)"
          % (len(paires), packfr_pris))
    print("customs à traduire    : %d" % len(customs))

    cache = {}
    if os.path.exists(CACHE):
        with io.open(CACHE, encoding="utf-8") as f:
            cache = json.load(f)
    cache.update(MANUEL)
    a_faire = [t for t in sorted(customs) if t not in cache]
    print("déjà en cache         : %d | restants : %d"
          % (len(customs) - len(a_faire), len(a_faire)))

    if dry:
        print("--dry : rien écrit.")
        return 0

    os.makedirs(DOSSIER, exist_ok=True)

    # Première écriture : l'officiel + le cache, disponibles tout de suite.
    connus = dict(paires)
    for t in customs:
        if t in cache:
            connus[t] = cache[t]
    ecrire(connus)

    # PARALLÈLE : une requête à la fois plafonnait à ~1-2 textes/s sur des
    # descriptions longues. Cinq ouvriers se partagent la file ; le verrou
    # protège le cache, sauvegardé tous les 200. Un refus n'entre PAS au
    # cache : une relance le retentera — c'est aussi la soupape si le
    # service ralentit sous la charge (les 429 deviennent des refus, pas
    # des pertes).
    verrou = threading.Lock()
    etat = {"faits": 0, "refuses": 0}

    def travailler(texte):
        fr = traduire(texte)
        with verrou:
            etat["faits"] += 1
            if te.sur(texte, fr):
                cache[texte] = fr
                connus[texte] = fr
            else:
                etat["refuses"] += 1
            if etat["faits"] % 200 == 0:
                with io.open(CACHE, "w", encoding="utf-8") as f:
                    json.dump(cache, f, ensure_ascii=False, indent=1,
                              sort_keys=True)
                print("  %d/%d (refusés : %d)"
                      % (etat["faits"], len(a_faire), etat["refuses"]))

    with ThreadPoolExecutor(max_workers=5) as bassin:
        list(bassin.map(travailler, a_faire))
    refuses = etat["refuses"]

    with io.open(CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("traduits : %d | refusés (anglais gardé) : %d"
          % (len(cache), refuses))

    # Écriture finale, complète.
    ecrire(connus)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
