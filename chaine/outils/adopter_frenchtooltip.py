# -*- coding: utf-8 -*-
r"""ADOPTION de la base communautaire « FrenchTooltip » (don du 22/07/2026,
via Discord — voir CONTEXTE) : 10 600 sorts des classes custom CoA relus
main, ligne par ligne.

1. NOMS : les paires nomEN -> nomFR rejoignent traductions/sorts.json
   (couche « noms ») — seulement les TROUS (nos paires existantes priment) ;
   les DIVERGENCES partent dans rapports/divergences_frenchtooltip.txt
   pour arbitrage de Dan, rien n'est écrasé.
2. LIGNES : leurs motifs Lua (nombres capturés) + gabarits français
   {{n}} deviennent DB\DB_SortsLignes.lua, consultée par Sorts.lua en
   PRIORITÉ pour les sorts couverts. Les variantes GÉNÉRIQUES (« Level:
   %d », « ID %d »...) sont dédoublonnées en une liste commune.

L'ordre du .toc fait foi : la dernière inscription d'un SpellID gagne
(leurs couches de réparation « StrictCaptured » écrasent les anciennes).

Usage : python outils/adopter_frenchtooltip.py
"""
import io
import json
import os
import re
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from garde_packfr import texte_sain  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(BASE, "Ajouter par Dan", "FrenchTooltip")
CACHE_SORTS = os.path.join(BASE, "traductions", "sorts.json")
RAPPORT = os.path.join(BASE, "rapports", "divergences_frenchtooltip.txt")
RAPPORT_CHIMERES = os.path.join(BASE, "rapports",
                                "chimeres_frenchtooltip.txt")

# ---------------------------------------------------------------------------
# GARDE ANTI-CHIMÈRES (23/07/2026, captures de Dan : « Vous radiate un
# harmonic disposition… », « à walk sur water », « Ghost forme »).
# La base communautaire contient des entrées en MOT-À-MOT : mots-outils
# français, mots pleins anglais. Le détecteur historique (the/your/and…)
# ne les voit pas — il faut des MOTS PLEINS anglais sans homographe
# français. Exclus exprès (homographes ou usages français légitimes) :
# disposition, technique, passive, raid, shift (« Maintenez Shift »).
# ---------------------------------------------------------------------------
CHIMERE_MOTS = re.compile(
    r"\b(?:the|your|you|with|and|that|this|from|their|them|will|enemies|"
    r"allies|abilities|while|into|upon|through|when|have|increased|which|"
    r"there|these|those|been|being|"
    r"walk|water|fall|falling|slow|slowing|allow|allowing|grant|granting|"
    r"grants|take|taking|cancel|cancels|radiate|nearby|cause|causing|"
    r"usable|indoors|ghostly|gain|gaining|enter|entering|movement|damage|"
    r"dealing|dealt|deal|deals|reduce|reduced|reducing|ability|speed|"
    r"effect|effects|health|target|targets|weapon|melee|spell|spells|"
    r"next|each|every|additional|level|now|beyond|ghost|summon|summons|"
    r"increase|increasing|decrease|decreased|heal|heals|healing|removes|"
    r"remove|applies|apply)\b", re.I)

RE_HABILLAGE = re.compile(r"\{\{\d+\}\}|\|c%?x?[0-9a-fA-F]{0,8}|\|[rTt]"
                          r"|\|cFF[0-9a-fA-F]{6}")


def chimere(texte):
    """Vrai si le texte « français » porte des mots pleins anglais — la
    signature du mot-à-mot inachevé."""
    nu = RE_HABILLAGE.sub(" ", texte or "")
    return bool(CHIMERE_MOTS.search(nu))


# Étalonnage OBLIGATOIRE avant tout passage (doctrine du projet : un
# détecteur qui se trompe sur un témoin ne publie rien).
TEMOINS_CONDAMNES = [
    "Vous radiate un harmonic disposition à proche membres du groupe et "
    "du raid, provoquant fall dégâts à être réduit et conférant le "
    "technique à walk sur water.",
    "Permet groupe membres à moins de {{1}} m de vous à walk sur water. "
    "dure pour {{2}} min. Taking tout dégâts cancels ce effet.",
    "MAJ dans un ghostly forme, gagnant {{1}}% augmenté vitesse de "
    "déplacement, slowing votre falling vitesse, et allowing vous à walk "
    "sur water. pas utilisable en combat ou indoors.",
    "Ghost forme",
    "Beyond le voile",
]
TEMOINS_INNOCENTS = [
    "Inflige {{1}} points de dégâts d'Ombre à la cible.",
    "Augmente votre hâte de {{1}} % pendant {{2}} s.",
    "Confère {{1}} points d'armure aux alliés proches. Dure {{2}} min.",
    "|cFF66DDFFPassif niveau 10|r Vous retardez désormais 40 % des "
    "dégâts directs subis.",
    "Maintenez Shift pour plus d'informations.",
    "Grâce de la lune",
]


def etalonner():
    rates = [t for t in TEMOINS_CONDAMNES if not chimere(t)]
    rates += ["INNOCENT: " + t for t in TEMOINS_INNOCENTS if chimere(t)]
    if rates:
        for r in rates:
            print("  étalonnage raté :", r[:70])
        raise SystemExit("détecteur de chimères mal étalonné — rien écrit")
SORTIE = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
          r"\AscensionFR\DB\DB_SortsLignes.lua")

RE_ENTREE = re.compile(
    r'RegisterPatternSpell\(\s*"(\w+)"\s*,\s*(\d+)\s*,\s*'
    r'"((?:\\.|[^"\\])*)"\s*,\s*"((?:\\.|[^"\\])*)"', re.S)
RE_VARIANTE = re.compile(
    r'\{\s*pattern\s*=\s*"((?:\\.|[^"\\])*)"\s*,\s*'
    r'text\s*=\s*"((?:\\.|[^"\\])*)"\s*,?\s*\}', re.S)


def deslua(s):
    """Défait les échappements d'un littéral Lua "..."."""
    return (s.replace("\\\\", "\x00").replace('\\"', '"')
            .replace("\\n", "\n").replace("\\r", "\r")
            .replace("\\t", "\t").replace("\x00", "\\"))


def relua(s):
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return s.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")


def ordre_toc():
    toc = io.open(os.path.join(SOURCE, "FrenchTooltip.toc"),
                  encoding="utf-8-sig", errors="replace").read()
    fichiers = []
    for ligne in toc.splitlines():
        ligne = ligne.strip()
        if ligne and not ligne.startswith("#") and ligne.endswith(".lua"):
            chemin = os.path.join(SOURCE, ligne.replace("\\", os.sep))
            if os.path.exists(chemin):
                fichiers.append(chemin)
    return fichiers


def main():
    etalonner()
    chimeres_trouvees = []          # (sid, où, texte) pour le rapport
    fiches = OrderedDict()          # id -> fiche (la dernière gagne)
    for chemin in ordre_toc():
        texte = io.open(chemin, encoding="utf-8", errors="replace").read()
        # chaque inscription court jusqu'à la parenthèse fermante « )\n »
        # de premier niveau — on découpe par occurrences successives.
        debuts = [m for m in RE_ENTREE.finditer(texte)]
        for i, m in enumerate(debuts):
            fin = debuts[i + 1].start() if i + 1 < len(debuts) else len(texte)
            bloc = texte[m.end():fin]
            variantes = [(deslua(p), deslua(t))
                         for p, t in RE_VARIANTE.findall(bloc)]
            fiches[int(m.group(2))] = {
                "classe": m.group(1),
                "en": deslua(m.group(3)),
                "fr": deslua(m.group(4)),
                "variantes": variantes,
            }
    print("SpellID (dernière couche) :", len(fiches))

    # ------------------------------------------------------------------
    # 1. NOMS -> sorts.json (trous seulement) + rapport de divergences
    # ------------------------------------------------------------------
    cache = json.load(io.open(CACHE_SORTS, encoding="utf-8"))
    noms = cache.setdefault("noms", {})
    # SOIN : les chimères déjà entrées dans sorts.json par les passages
    # précédents (avant la garde) sont RETIRÉES — mieux vaut l'anglais.
    soignes = 0
    for en in list(noms):
        if chimere(noms[en]):
            chimeres_trouvees.append(("sorts.json", en, noms[en]))
            del noms[en]
            soignes += 1
    print("noms chimères RETIRÉS de sorts.json :", soignes)
    adoptes, divergences = 0, []
    for fiche in fiches.values():
        en, fr = fiche["en"].strip(), fiche["fr"].strip()
        if len(en) < 3 or not fr or en == fr or not texte_sain(fr):
            continue
        if chimere(fr):
            chimeres_trouvees.append(("nom", en, fr))
            continue
        notre = noms.get(en)
        if notre is None:
            noms[en] = fr
            adoptes += 1
        elif notre != fr:
            divergences.append((en, notre, fr))
    with io.open(CACHE_SORTS, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.makedirs(os.path.dirname(RAPPORT), exist_ok=True)
    with io.open(RAPPORT, "w", encoding="utf-8") as f:
        f.write("Divergences noms de sorts : NOTRE version / la LEUR\n"
                "(rien n'a été écrasé — arbitrage de Dan)\n\n")
        for en, notre, leur in sorted(divergences):
            f.write("%s\n  nous : %s\n  eux  : %s\n" % (en, notre, leur))
    print("noms adoptés (trous) :", adoptes,
          "| divergences à arbitrer :", len(divergences))

    # ------------------------------------------------------------------
    # 2. LIGNES -> DB_SortsLignes.lua (variantes génériques factorisées)
    # ------------------------------------------------------------------
    compte_par_motif = {}
    for fiche in fiches.values():
        for p, t in fiche["variantes"]:
            compte_par_motif[(p, t)] = compte_par_motif.get((p, t), 0) + 1
    communes = {pt for pt, n in compte_par_motif.items() if n >= 50}
    print("variantes communes factorisées :", len(communes))

    lignes = [
        "-- Fichier GÉNÉRÉ par outils/adopter_frenchtooltip.py — ne pas",
        "-- éditer à la main. Base communautaire de lignes de sorts CoA",
        "-- (motifs Lua -> gabarits {{n}}), consultée en PRIORITÉ par",
        "-- Sorts.lua pour les SpellID couverts.",
        "local C = {",
    ]
    ordre_communes = sorted(communes)
    for p, t in ordre_communes:
        lignes.append('{p="%s",t="%s"},' % (relua(p), relua(t)))
    lignes.append("}")
    lignes.append("local DB = AscensionFR.DB.SortsLignes")
    lignes.append("AscensionFR.DB.SortsLignesCommunes = C")
    indice_commune = {pt: i + 1 for i, pt in enumerate(ordre_communes)}
    n_variantes = 0
    n_chimeres_variantes = 0
    for sid in sorted(fiches):
        fiche = fiches[sid]
        morceaux = []
        for p, t in fiche["variantes"]:
            if (p, t) in indice_commune:
                continue        # servie par la liste commune
            if chimere(t):
                chimeres_trouvees.append((str(sid), fiche["en"], t))
                n_chimeres_variantes += 1
                continue        # mieux vaut l'anglais qu'un mot-à-mot
            morceaux.append('{p="%s",t="%s"}' % (relua(p), relua(t)))
            n_variantes += 1
        en, fr = fiche["en"].strip(), fiche["fr"].strip()
        nom = ""
        if en and fr and en != fr and texte_sain(fr) and not chimere(fr):
            nom = 'e="%s",n="%s",' % (relua(en), relua(fr))
        if morceaux or nom:
            lignes.append("DB[%d]={%sv={%s}}"
                          % (sid, nom, ",".join(morceaux)))
    print("variantes chimères ÉCARTÉES :", n_chimeres_variantes)
    with io.open(RAPPORT_CHIMERES, "w", encoding="utf-8") as f:
        f.write("Chimères anglais/français écartées par la garde du "
                "23/07/2026\n(l'anglais s'affiche à la place — c'est "
                "voulu)\n\n")
        for ou, en, t in chimeres_trouvees:
            f.write("[%s] %s\n    %s\n" % (ou, en[:60], t[:110]))
    io.open(SORTIE, "w", encoding="utf-8", newline="").write(
        "\n".join(lignes) + "\n")
    taille = os.path.getsize(SORTIE) / 1048576.0
    print("écrit : DB_SortsLignes.lua (%d sorts, %d variantes propres,"
          " %.1f Mo)" % (len(fiches), n_variantes, taille))


if __name__ == "__main__":
    main()
