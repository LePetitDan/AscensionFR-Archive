# -*- coding: utf-8 -*-
"""
CROISEMENT MULTI-SOURCES (levier de QUALITÉ, sans rien modifier).

Pour chaque sort, on met CÔTE À CÔTE la traduction de plusieurs sources et on
juge :
  - CONCORDANCE : une source humaine (PackFR, officiel Blizzard, proposition
    joueur) confirme NOTRE traduction  -> haute confiance.
  - DIVERGENCE  : une source humaine DIFFÈRE de la nôtre -> candidat à
    corriger (souvent notre Google est en tort face à un humain).
  - GAP         : on n'a rien, mais une source humaine a quelque chose ->
    candidat à adopter.

Sources croisées (toutes indexées par ID de sort) :
  - Ascension (EN)      : sources/dbc/spells_Ascension.json (id -> nom EN)
  - Officiel Blizzard   : sources/dbc/spells_frFR.json      (id -> FR officiel)
  - PackFR (communauté) : sources/packfr_sorts.json         (id -> FR humain)
  - Propositions joueurs: traductions/propositions_joueurs.json (via /afr)
  - NOUS (actuel)       : traductions/sorts.json { noms, descriptions }

Sortie : traductions/divergences_sources.txt (à arbitrer par Dan) + stats.
NE MODIFIE RIEN : c'est un rapport. Le vocabulaire reste arbitré côté projet.

GARDE-FOU D'APPARIEMENT (26/07/2026) : la colonne « officiel » est retrouvée
par ID, or Ascension renomme des sorts Blizzard EN PLACE — le français récupéré
traduit alors l'ancien nom. Voir garde_appariement. Mesuré : 397 officiels
écartés, plus 365 valeurs PackFR qui n'en étaient que la recopie ; 16 des 397
sont repêchés sur un AUTRE ID portant le même nom anglais.

GARDE D'ACCENT (27/07/2026) : notre français accentue les majuscules initiales
depuis le lot 7, l'officiel 3.3.5a non (« Éclair de givre » contre « Eclair de
givre »). Un nom qui ne diffère que par là est compté CONCORDANT, pas
divergent : 497 entrées, mesuré.

  python outils/croiser_sources.py
"""
import json, os, re, sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from garde_appariement import (charger_blizzard, appariement_prouve,  # noqa: E402
                               indecidable)
from accents_majuscules import difference_d_accent_seule  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAPPORT = os.path.join(BASE, "traductions", "divergences_sources.txt")

# Sources humaines douteuses à ignorer (marqueurs de test / placeholder).
JUNK = re.compile(r"\b(OLD|TEST|PH|PLACEHOLDER|UNUSED|DEPRECATED|DND|\(old\))\b|"
                  r"^\s*$|^z+test|^test", re.I)


def charger(p):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def norm(s):
    """Comparaison tolérante : casse, espaces, ponctuation légère."""
    if not s:
        return ""
    s = s.lower().strip()
    s = s.replace(" ", " ")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[.…]+$", "", s)          # points finals
    return s


def champ(d, cle, sous):
    v = d.get(str(cle))
    if isinstance(v, dict):
        return v.get(sous)
    return v if sous == "N" else None


def main():
    asc = charger(os.path.join(BASE, "sources", "dbc", "spells_Ascension.json"))
    offi = charger(os.path.join(BASE, "sources", "dbc", "spells_frFR.json"))
    pack = charger(os.path.join(BASE, "sources", "packfr_sorts.json"))
    sorts = charger(os.path.join(BASE, "traductions", "sorts.json"))
    props = charger(os.path.join(BASE, "traductions", "propositions_joueurs.json"))
    blz = charger_blizzard()          # juge de paix : le nom EN de Blizzard
    noms_fr = sorts.get("noms", {})

    # index proposition joueur : nom EN actuel -> {fr: votes} (cible sort/texte)
    prop_par_texte = {}
    for _, e in (props or {}).items():
        actuel = (e.get("actuel") or "").strip()
        if actuel and isinstance(e.get("propositions"), dict):
            prop_par_texte.setdefault(actuel, Counter()).update(e["propositions"])

    concord = 0
    div_offi, div_pack, gap = [], [], []
    vus = set()
    ecartes = indecis = ecartes_pack = repeches = accent_seul = 0

    # REPÊCHAGE PAR NOM EN. La boucle ne traite qu'UN ID par nom anglais (`vus`
    # ci-dessous) : si c'est justement celui-là qu'Ascension a renommé, on perd
    # l'officiel alors qu'un AUTRE ID du même nom le prouvait. Mesuré : 16 noms
    # dans ce cas, dont « Accuracy » (ID 13705 réfuté, ID 60340 prouvé, même
    # « Précision ») et « Poison Bottle » (22335 réfuté, 67594 prouvé).
    # appliquer_divergences_officielles.py n'a pas ce trou : il agrège tous les
    # IDs d'un nom. On fait pareil, avec la même exigence d'UNICITÉ que lui —
    # deux officiels prouvés différents pour un même nom ne se départagent pas
    # dans un rapport, on laisse tomber.
    off_prouve_par_en = {}
    for sid in offi:
        en_p = champ(asc, sid, "N")
        o_p = champ(offi, sid, "N")
        if not en_p or not o_p or not o_p.strip() or JUNK.search(o_p):
            continue
        if appariement_prouve(blz, sid, en_p):
            off_prouve_par_en.setdefault(en_p, set()).add(o_p.strip())

    ids = set(pack) | set(offi)
    # TRI PAR ID CROISSANT — sans lui le rapport n'est PAS reproductible :
    # `ids` est un set(), la boucle ne retient que le PREMIER ID rencontré pour
    # un nom anglais donné (`vus`), et l'ordre d'un set change d'une exécution à
    # l'autre. Deux lectures du même rapport ne portent alors pas sur les mêmes
    # entrées. Le contrôle ne dépend d'aucun état daté de sorts.json, il se
    # rejoue en une minute : retirer le tri, lancer quatre fois, le nombre de
    # divergences vs officiel bouge (27/07 : 94, 94, 96, 94) ; avec le tri,
    # deux exécutions rendent un rapport identique OCTET POUR OCTET.
    # Hypothèse vérifiée avant d'écrire int() : 0 clé non numérique dans
    # packfr_sorts.json (241 870) ni dans spells_frFR.json (49 839). Le tri
    # gagne aussi de la COUVERTURE — même contrôle, même jour : 174 divergences
    # vs officiel avec le tri contre ~94 sans, parce qu'il fait tomber le choix
    # sur l'ID le plus BAS, la plage Blizzard classique, la seule qui ait des
    # officiels. C'est de la couverture gagnée, pas une régression.
    for sid in sorted(ids, key=int):
        en = champ(asc, sid, "N")
        if not en or en in vus:
            continue
        vus.add(en)
        notre = noms_fr.get(en)
        off = champ(offi, sid, "N")
        pk = champ(pack, sid, "N")
        # ignorer placeholders/junk côté sources humaines
        if pk and JUNK.search(pk):
            pk = None
        if off and JUNK.search(off):
            off = None
        # GARDE-FOU : Ascension a renommé ce sort Blizzard en place ? Alors
        # l'officiel de cet ID traduit l'ANCIEN nom. On met `off` à None SANS
        # sauter l'entrée : le PackFR doit rester évalué pour le même ID.
        off_refute = None
        if off and not appariement_prouve(blz, sid, en):
            off_refute, off = off, None
            ecartes += 1
            if indecidable(blz, sid):
                indecis += 1      # sous-ensemble des écartés, pas un 3e seau
            # Repêchage : un autre ID porte-t-il ce nom EN avec un appariement
            # prouvé ? Alors son officiel est bon, c'est notre dédoublonnage
            # qui était tombé sur le mauvais ID (voir l'index plus haut).
            secours = off_prouve_par_en.get(en) or set()
            if len(secours) == 1:
                off = sorted(secours)[0]
                repeches += 1
        # GARDE PackFR, ÉTROITE. Mesuré deux fois (49 sur 49, puis 54 sur 54) :
        # la TOTALITÉ des divergences vs PackFR que le garde-fou fait
        # apparaître sont la recopie mot pour mot de l'officiel qu'on vient
        # d'écarter — la contamination rentrait par la porte de derrière, sous
        # l'étiquette rassurante « source humaine communautaire ». On n'écarte
        # le PackFR QUE dans ce cas précis, jamais sur le garde-fou complet :
        # mesuré, ça détruirait 138 006 de ses 186 127 IDs exploitables
        # (74,1 %), dont 99,5 % de sorts custom qu'aucun DBC Blizzard ne
        # connaît et sur lesquels il est notre seule source.
        if pk and off_refute is not None and norm(pk) == norm(off_refute):
            pk = None
            ecartes_pack += 1
        humaines = [x for x in (off, pk) if x]
        if not humaines:
            continue

        if not notre:
            # on n'a rien : une source humaine pourrait combler
            gap.append((en, off, pk))
            continue

        n_notre = norm(notre)
        # concordance : au moins une source humaine confirme notre trad
        if any(norm(h) == n_notre for h in humaines):
            concord += 1
            continue
        # CONCORDANCE À L'ACCENT PRÈS. Le lot 7 accentue les majuscules
        # initiales, que Blizzard n'accentuait pas en 3.3.5a : « Éclair de
        # givre » contre « Eclair de givre ». Ce n'est pas un désaccord de
        # traduction, c'est une règle que nous avons choisie — la compter comme
        # divergence noierait le vrai signal (~400 lignes de bruit) et, pire,
        # afficherait la forme NON accentuée comme la correction à faire, juste
        # sous les yeux de qui arbitre. Le test reste étroit : toute autre
        # différence, même un accent ailleurs dans le nom, redevient une
        # divergence.
        if any(difference_d_accent_seule(notre, h) for h in humaines):
            concord += 1
            accent_seul += 1      # sous-ensemble des concordances
            continue
        # divergence : les humaines diffèrent toutes de la nôtre
        if off and norm(off) != n_notre:
            div_offi.append((en, notre, off))
        if pk and norm(pk) != n_notre and (not off or norm(pk) != norm(off)):
            div_pack.append((en, notre, pk))

    # divergences vs propositions joueurs (le plus fort signal)
    div_prop = []
    for en, votes in prop_par_texte.items():
        notre = noms_fr.get(en) or ""
        for fr, v in votes.items():
            if norm(fr) != norm(notre):
                div_prop.append((en, notre, fr, v))

    with open(RAPPORT, "w", encoding="utf-8") as f:
        f.write("CROISEMENT DES SOURCES — divergences à arbitrer\n")
        f.write("=" * 60 + "\n\n")
        f.write("Concordances (une source humaine confirme notre trad) : %d\n"
                % concord)
        f.write("  dont %d qui ne diffèrent de la source que par notre accent\n"
                "  sur la majuscule initiale (règle du lot 7) — non listées.\n\n"
                % accent_seul)

        def bloc(titre, liste, cols):
            f.write("\n" + titre + " (%d)\n" % len(liste))
            f.write("-" * len(titre) + "\n")
            for ligne in liste[:400]:
                f.write("  EN     : %s\n" % str(ligne[0])[:80])
                for i, c in enumerate(cols):
                    f.write("  %-6s : %s\n" % (c, str(ligne[i + 1])[:80]))
                f.write("\n")

        bloc("DIVERGENCE vs PROPOSITION JOUEUR (signal fort)", div_prop,
             ["nous", "joueur", "votes"])
        bloc("DIVERGENCE vs OFFICIEL Blizzard", div_offi, ["nous", "officiel"])
        bloc("DIVERGENCE vs PackFR (communauté)", div_pack, ["nous", "PackFR"])
        bloc("GAP : rien chez nous, dispo ailleurs", gap, ["officiel", "PackFR"])

    print("Concordances (confiance) :", concord)
    print("  dont concordantes à l'accent près (règle du lot 7) :", accent_seul)
    print("Divergences vs joueur    :", len(div_prop))
    print("Divergences vs officiel  :", len(div_offi))
    print("Divergences vs PackFR    :", len(div_pack))
    print("Gaps (à adopter)         :", len(gap))
    print("Officiels écartés (ID renommé par Ascension) :", ecartes)
    print("  dont indécidables (ID inconnu du DBC Blizzard) :", indecis)
    print("  dont repêchés sur un autre ID du même nom EN :", repeches)
    print("PackFR écartés (recopie d'un officiel réfuté) :", ecartes_pack)
    print("\nRapport :", RAPPORT)
    print("\n--- 6 exemples de divergences vs officiel ---")
    for en, notre, off in div_offi[:6]:
        print("  EN:", en[:45])
        print("     nous  :", (notre or "")[:45])
        print("     offi. :", (off or "")[:45])


if __name__ == "__main__":
    main()
