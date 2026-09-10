# -*- coding: utf-8 -*-
"""Garde-fou commun contre le FAUX APPARIEMENT par ID avec le français officiel
Blizzard 3.3.5a (constat du 26/07/2026, lot 5).

Le défaut : deux outils d'arbitrage retrouvent l'officiel PAR ID en croisant
deux bases différentes — le nom anglais vient de `spells_Ascension.json`, le
français de `spells_frFR.json` — sans jamais vérifier que Blizzard nommait ce
sort comme Ascension le nomme. Or Ascension RENOMME des sorts Blizzard EN
PLACE : l'ID ne bouge pas, le nom si, et le français récupéré traduit alors
l'ANCIEN nom. Vécu : l'ID 2831 s'appelait « Armor +8 » chez Blizzard (d'où
« Armure +8 »), Ascension l'a rebaptisé « Armor (Light) ».

Le juge de paix est `sources/dbc/spells_enUS.json` : exactement les mêmes
49 839 IDs que le frFR (vérifié : 0 ID d'écart), donc `enUS[id].N` est
GARANTI aligné sur `frFR[id].N`. Le test devient :

    meme_nom(enUS[id].N, asc[id].N)  ->  appariement PROUVÉ, l'officiel vaut
    sinon                            ->  REFUSÉ

Mesuré au lot 5, en rejouant la passe sur l'état d'avant appariement
(`traductions/sorts_avant_appariement.json`) : sans ce test, « l'officiel
gagne » partait à 40 % de régressions — 48 des 119 entrées qu'elle touche
(119 = 7 sûres + 112 à arbitrer, garde éteint).

À utiliser par TOUT outil qui adopte du français officiel retrouvé par ID :

    from garde_appariement import charger_blizzard, appariement_prouve
    blz = charger_blizzard()
    if appariement_prouve(blz, sid, nom_en_ascension): ...

Ce module est VOLONTAIREMENT AUTONOME : il porte sa propre normalisation
plutôt que de réutiliser celle de ses appelants. `croiser_sources.py` a un
`norm()` maison plus léger (il ne dénude ni les accents ni la ponctuation) qui
sert aussi à compter ses concordances ; en changer le sens ferait bouger des
milliers de lignes de son rapport pour une raison sans aucun rapport avec ce
correctif.
"""
import json
import os
import re
import unicodedata

# Le juge de paix vit à côté des deux bases qu'il départage.
CHEMIN_DEFAUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "sources", "dbc", "spells_enUS.json")

# Plancher de vraisemblance : les deux DBC Blizzard portent 49 839 IDs chacun
# (mesuré le 26/07/2026, 0 ID d'écart entre enUS et frFR). Un juge de paix qui
# en aurait perdu le cinquième n'est plus un juge de paix, c'est une source
# tronquée. Marge large et volontaire : le seuil ne doit se déclencher que sur
# un accident franc, jamais sur une mise à jour normale du DBC.
IDS_ATTENDUS_MINI = 40000


def _norm(s):
    """Normalisation interne (privée) : casse, apostrophes typographiques,
    espace insécable, ligatures, points de suspension finals. Reprise à
    l'identique de `appliquer_divergences_officielles.py` pour que le garde
    juge sur exactement la même base que l'outil qu'il protège."""
    if not s:
        return ""
    s = s.lower().strip()
    s = s.replace("’", "'").replace("ʼ", "'").replace("`", "'")
    s = s.replace(" ", " ").replace("œ", "oe").replace("æ", "ae")
    s = re.sub(r"\s+", " ", s)
    return re.sub(r"[.…]+$", "", s)


def _sans_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s or "")
                   if unicodedata.category(c) != "Mn")


def cle_nue(s):
    """Clé de comparaison permissive : minuscule, sans accent, sans
    ponctuation. Deux noms qui ne diffèrent que là-dessus sont « le même »."""
    return re.sub(r"[^a-z0-9]+", " ", _sans_accents(_norm(s))).strip()


def cle_collee(s):
    """Comme `cle_nue` mais SANS AUCUN séparateur : « Holy Form » et
    « Holyform », « Major Spell Power » et « Major Spellpower » sont le même
    nom simplement réespacé par Ascension. Sans ce repli, le garde déclarerait
    ces appariements faux à tort et jetterait des officiels valides."""
    return re.sub(r"[^a-z0-9]+", "", _sans_accents(_norm(s)))


def meme_nom(a, b):
    """Les deux noms anglais désignent-ils la même chose ?"""
    if a is None or b is None:
        return False
    return cle_nue(a) == cle_nue(b) or cle_collee(a) == cle_collee(b)


def charger_blizzard(chemin=None):
    """Charge le juge de paix. LÈVE plutôt que de rendre un dict vide ou
    maigre : avec la politique « indécidable = refusé », un spells_enUS.json
    absent — ou présent mais VIDE, ou régénéré TRONQUÉ — fait tomber 100 % des
    officiels SANS le moindre message, et un rapport vide se lit exactement
    comme un rapport propre.

    Les deux cas comptent autant. Vérifier la seule EXISTENCE du fichier ne
    couvrait que la moitié : sur un `{}`, les appelants sortaient en code 0 et
    réécrivaient tranquillement leurs rapports avec « 0 correction, 48 814
    officiels écartés, dont 48 814 indécidables »."""
    p = chemin or CHEMIN_DEFAUT
    if not os.path.exists(p):
        raise SystemExit("garde_appariement : juge de paix introuvable — " + p)
    base = json.load(open(p, encoding="utf-8"))
    if len(base) < IDS_ATTENDUS_MINI:
        raise SystemExit(
            "garde_appariement : juge de paix invraisemblable — %d IDs dans %s"
            " (attendu au moins %d). Base vide ou tronquée : la régénérer"
            " avant de rejouer, sinon TOUS les officiels seraient refusés en"
            " silence." % (len(base), p, IDS_ATTENDUS_MINI))
    return base


def nom_blizzard(blz, sid):
    """Nom anglais que BLIZZARD donnait à cet ID, ou None s'il l'ignore."""
    v = blz.get(str(sid))
    return v.get("N") if isinstance(v, dict) else v


def indecidable(blz, sid):
    """ID absent du DBC Blizzard : on ne peut ni prouver ni réfuter."""
    return nom_blizzard(blz, sid) is None


def appariement_prouve(blz, sid, nom_ascension):
    """Le français officiel de cet ID parle-t-il bien du sort qu'Ascension
    nomme `nom_ascension` ?

    Politique retenue : INDÉCIDABLE = REFUSÉ. Le cas ne coûte rien aujourd'hui
    (mesuré : 0 ID concerné, le frFR et le enUS ont les mêmes 49 839 clés) et
    il protège du jour où l'une des deux sources sera régénérée tronquée.
    `meme_nom` rendant False dès qu'un côté est None, la règle est déjà là."""
    return meme_nom(nom_blizzard(blz, sid), nom_ascension)
