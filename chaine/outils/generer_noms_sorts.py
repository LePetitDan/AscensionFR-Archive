# -*- coding: utf-8 -*-
r"""Génère DB\DB_SortsNoms.lua : le pont NOM ANGLAIS -> NOM FRANÇAIS des
sorts, pour le grimoire, les barres et tout endroit qui affiche un nom de
sort par son TEXTE (l'ID n'y est pas accessible au moment de l'affichage).

Deux sources, par ID :
1. OFFICIEL : spells_enUS.json x spells_frFR.json (jeu de base) ;
2. CUSTOM   : spells_Ascension.json (nom EN) x DB_Sorts.lua (champ N
   français) — seulement si notre N diffère de l'anglais (donc traduit).

Doublons DIVERGENTS (même nom EN, français différents) : neutralisés,
comme dans tous nos ponts par nom. Identités écartées (inutiles).
"""
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from garde_packfr import texte_sain  # noqa: E402
from generateur_db import polir  # noqa: E402
from noms_empoisonnes import empoisonne, porteurs_anormaux  # noqa: E402

from chemin_client import DB as DBDIR, exiger_client  # noqa: E402

exiger_client("generer_noms_sorts (pont des noms de sorts)")
SRC = r"D:\AscensionFR\WorkFlow\sources\dbc"
SORTIE = DBDIR + r"\DB_SortsNoms.lua"


def echapper(s):
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return s.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")


def plat(s):
    """Minuscules sans accents — pour reconnaître deux graphies d'un MÊME
    nom (« Bénédiction de vol'jin » / « de Vol'jin »)."""
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", (s or "").lower())
                   if not unicodedata.combining(c))


paires = {}
divergents = set()
empoisonnes = []          # (nom EN, valeur) écartés — comptés à la fin


def poser(en, fr):
    en, fr = (en or "").strip(), (fr or "").strip()
    if not en or not fr or en == fr or en in divergents:
        return
    # NOMS EMPOISONNÉS (lot 9, 26/07/2026) : une même valeur posée sur des
    # centaines de sorts sans rapport entre eux. Le filtre est ICI parce que
    # poser() est l'entonnoir des QUATRE couches — et que la plus contaminée
    # n'est pas la nôtre : le PackFR porte 1 793 identifiants empoisonnés.
    # Purger traductions/sorts.json sans ce filtre laisserait 815 entrées
    # intactes dans le pont régénéré, soit exactement autant qu'avant.
    # Le porteur légitime, lui, passe (« Test of Faith »).
    if empoisonne(en, fr):
        empoisonnes.append((en, fr))
        return
    # Vocabulaire arbitré + règle d'accent, ICI et pas ailleurs : poser() est
    # l'entonnoir des QUATRE couches (officiel Blizzard, nos customs, PackFR,
    # Glayna), et le français officiel 3.3.5a entre tel quel dans ce pont —
    # « Elixir of Fortitude » y donnait « Elixir de robustesse ». Le test
    # « en == fr » ci-dessus a déjà écarté les paires non traduites.
    # Effet de bord bénéfique : deux couches qui ne divergeaient que par
    # l'accent cessent de s'annuler l'une l'autre.
    fr = polir(fr, anglais=en)
    deja = paires.get(en)
    if deja is None:
        paires[en] = fr
    elif deja != fr:
        # Deux graphies du MÊME nom (casse/accents près) ne sont pas une
        # divergence : neutraliser perdait ~20 noms (« Bénédiction de
        # vol'jin » vs « Vol'jin », bloc A). La couche la plus HAUTE garde
        # sa graphie — l'ordre des couches est déjà l'ordre de confiance.
        if plat(deja) == plat(fr):
            return
        del paires[en]
        divergents.add(en)


# 1. officiel
enus = json.load(io.open(SRC + r"\spells_enUS.json", encoding="utf-8"))
frfr = json.load(io.open(SRC + r"\spells_frFR.json", encoding="utf-8"))
for ident, fiche in enus.items():
    f2 = frfr.get(ident)
    if f2:
        poser(fiche.get("N"), f2.get("N"))
n_officiel = len(paires)
# Noms venus de l'OFFICIEL Blizzard : autorité absolue, jamais écrasés par
# une couche communautaire (garde-fou de l'adoption Glayna, plus bas).
officiels = set(paires)
print("paires officielles :", n_officiel, "| divergents :", len(divergents))

# 2. custom : nos N traduits, joints par ID au dump Ascension
#    (DB_Sorts ET DB_SortsCorrections — les corrections seules comptent
#    aussi, limite corrigée le 21/07)
ascension = json.load(io.open(SRC + r"\spells_Ascension.json",
                              encoding="utf-8"))
n_custom = 0
for fichier in ["DB_Sorts.lua", "DB_SortsCorrections.lua"]:
    base = io.open(DBDIR + "\\" + fichier, encoding="utf-8",
                   errors="replace").read()
    for ident, n_fr in re.findall(
            r'^DB\[(\d+)\]=\{[^\n]*?,N="((?:\\.|[^"\\])*)"', base, re.M):
        fiche = ascension.get(ident)
        if not fiche:
            continue
        en = (fiche.get("N") or "").strip()
        fr = n_fr.replace('\\"', '"').replace("\\\\", "\\").strip()
        if en and fr and en != fr:
            avant = len(paires)
            poser(en, fr)
            if len(paires) > avant:
                n_custom += 1
print("paires custom ajoutées :", n_custom,
      "| divergents totaux :", len(divergents))

# 2bis. LA LISTE RELUE (bloc A, 29/07/2026) : les 777 noms retraduits à la
#    main au retrait de la couche Glayna, joints par TEXTE — certains de
#    leurs identifiants sont HORS des cibles de generateur_sorts (18 noms
#    n'avaient aucun N en base alors que le store les portait proprement).
#    RESTRICTION : le nom doit être porté par le dump Ascension (les clés
#    mortes restent dehors) et absent des couches plus hautes. La liste est
#    FERMÉE et relue main — ce n'est pas une porte pour le store entier,
#    dont la qualité Google ne passe le pont que via les cibles.
try:
    _relus = json.load(io.open(
        r"D:\AscensionFR\WorkFlow\traductions\noms_pont_retraduits.json",
        encoding="utf-8"))
except OSError:
    _relus = []
_noms_dump = {(f.get("N") or "").strip()
              for f in ascension.values()}
n_relus = 0
for _p in _relus:
    _en, _fr = (_p.get("en") or "").strip(), (_p.get("fr") or "").strip()
    if _en and _fr and _en in _noms_dump and _en not in paires \
            and _en not in divergents:
        avant = len(paires)
        poser(_en, _fr)
        if len(paires) > avant:
            n_relus += 1
print("paires de la liste relue (bloc A) :", n_relus)

# 3. la couche PACKFR (21/07) : les noms français de l'ancien pack officiel
#    pour tout ce que NOS bases ne couvrent pas encore — joints par ID au
#    nom anglais ACTUEL du client. Nos paires (officiel + nos lots) priment.
RE_ANGLAIS = re.compile(
    r"\b(the|of|and|your|to|strike|blade|bolt|shield|blast)\b", re.I)
try:
    packfr = json.load(io.open(
        r"D:\AscensionFR\WorkFlow\sources\packfr_sorts.json",
        encoding="utf-8"))
except OSError:
    packfr = {}
n_pack = 0
for ident, fiche in ascension.items():
    en = (fiche.get("N") or "").strip()
    if not en or en in paires or en in divergents:
        continue
    p = packfr.get(ident)
    fr = ((p or {}).get("N") or "").strip().replace(chr(160), " ")
    # leur nom doit différer de l'anglais ET ne pas ressembler à de
    # l'anglais résiduel (ils n'avaient pas tout traduit non plus) ;
    # texte_sain écarte robots/codes internes/allemand du pack (21/07 :
    # EXIT_MINE -> SORTIE_MINE et 15 autres codes avaient filtré).
    if fr and fr != en and not RE_ANGLAIS.search(fr) \
            and texte_sain(fr) and texte_sain(en):
        avant = len(paires)
        poser(en, fr)
        if len(paires) > avant:
            n_pack += 1
print("paires PackFR ajoutées :", n_pack)

# 4. (RETIRÉE le 29/07/2026 — bloc A du programme 2.) La couche
#    communautaire Glayna (AutoBookFR) vivait ici : trous comblés et
#    mot-à-mot réparés par affectation DIRECTE (en contournant poser() et
#    ses gardes — c'est ainsi que « Smolder » -> « Braises » a vécu malgré
#    le verrou par clé). Les 788 noms qu'elle couvrait encore ont été
#    RETRADUITS par notre chaîne (traductions/noms_pont_retraduits.json,
#    couche 2bis ci-dessus, relue main) avant le retrait. Les outils et la
#    source sont archivés : archive/glayna/ — ne pas les rebrancher.

# LES ARBITRAGES RENDUS PRIMENT (bloc A du programme 3, 29/07/2026).
# Le pont neutralise une clé quand deux couches ne s'accordent pas — c'est
# la bonne règle tant que personne n'a tranché. Mais pour ces 81 noms, Dan
# A TRANCHÉ : neutraliser reviendrait à afficher l'anglais malgré la
# décision (les 4 vetos — « Déphasage », « Démence »… — tombaient du pont).
# On pose donc la valeur décidée, en dernier mot.
try:
    _decisions = json.load(io.open(
        r"D:\AscensionFR\WorkFlow\traductions"
        r"\divergences_officielles_decisions.json", encoding="utf-8"))
except OSError:
    _decisions = {}
n_arbitrees = 0
for _en, _d in _decisions.items():
    _valeur = _d["nous"] if _d["verdict"] == "garder" else _d["officiel"]
    _valeur = polir(_valeur, anglais=_en)
    if _valeur and _valeur != _en and paires.get(_en) != _valeur:
        paires[_en] = _valeur
        divergents.discard(_en)
        n_arbitrees += 1
if n_arbitrees:
    print("arbitrages de Dan posés en dernier mot :", n_arbitrees)

lignes = ["-- Fichier GÉNÉRÉ par outils/generer_noms_sorts.py — ne pas",
          "-- éditer à la main. Pont nom anglais -> nom français des",
          "-- sorts (officiel par ID + nos customs traduits).",
          "local DB = AscensionFR.DB.SortsNoms"]
for en in sorted(paires):
    lignes.append('DB["%s"]="%s"' % (echapper(en), echapper(paires[en])))
if empoisonnes:
    from collections import Counter as _C
    detail = _C(fr for _, fr in empoisonnes)
    print("noms EMPOISONNÉS écartés : %d  (%s)"
          % (len(empoisonnes),
             ", ".join("%s x%d" % (v, n) for v, n in detail.most_common(3))))

# LA BARRIÈRE DES PORTEURS, EN VIGIE (lot 10, 27/07/2026). Ici elle CONSTATE
# sans retirer : les valeurs sur-portées déjà en place attendent l'arbitrage
# de Dan (« ne purge rien de plus »), et les retirer d'office serait une
# purge déguisée. Ce compteur les rend visibles à CHAQUE build — le poison a
# vécu 6 jours parce qu'aucune sortie d'outil ne le montrait. À l'ADOPTION,
# en revanche, la même barrière refuse pour de bon (adopter_packfr_cache.py).
_anormaux = porteurs_anormaux(paires)
if _anormaux:
    _n = sum(len(v) for v in _anormaux.values())
    print("VIGIE : %d valeur(s) sur-portée(s) encore en place (%d entrées), "
          "en attente d'arbitrage — détail : rapports/porteurs_pont.txt"
          % (len(_anormaux), _n))
    with io.open(r"D:\AscensionFR\WorkFlow\rapports\porteurs_pont.txt",
                 "w", encoding="utf-8") as _f:
        _f.write("Valeurs sur-portées du pont (>= 5 porteurs sans parenté), "
                 "hors POISON déjà filtré.\nMesuré à la génération — rien "
                 "n'est retiré, l'arbitrage appartient à Dan.\n\n")
        for _v, _cles in sorted(_anormaux.items(), key=lambda kv: -len(kv[1])):
            _f.write("%5d  %s\n" % (len(_cles), _v))
            for _c in _cles[:4]:
                _f.write("          ex : %s\n" % _c)
print("paires à poser : %d" % len(paires))
for ex in ["Dodge", "Block", "Auto Attack", "Shoot", "Fire Blast"]:
    print("  ex :", ex, "->", paires.get(ex, "(absent)"))

# 2.0.1 : base PARESSEUSE par texte (mini-blocages du jour de sortie —
# 77 600 noms résidents pesaient sur le ménage du jeu).
# Comme pour DB_ObjetsNoms, la version plate n'est jamais posée sur le chemin
# livré : elle est déjà à ~59 % de la limite de constantes de Lua 5.1 et
# grossit à chaque couche de noms. Une conversion ratée laissait auparavant
# cette version en place, en silence.
import paresseux_textes  # noqa: E402
if not paresseux_textes.poser(SORTIE, "\n".join(lignes) + "\n",
                              "AscensionFR.DB.SortsNoms"):
    raise SystemExit(1)
