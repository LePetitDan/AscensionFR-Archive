# -*- coding: utf-8 -*-
"""MESURE (lecture seule) de la fiabilité de l'appariement « officiel Blizzard ».

Ne modifie RIEN. Produit les données brutes du rapport
`rapports/fiabilite_appariement_officiel.txt` (lot 5 du 26/07/2026).

Question de fond : `appliquer_divergences_officielles.py` retrouve le français
officiel par ID DBC, en croisant DEUX bases (Spell_Ascension.dbc pour le nom
anglais, Spell_frFR.dbc 3.3.5a pour le français) — sans vérifier que Blizzard
nommait ce sort pareil. Ascension RENOMME des sorts Blizzard en place, donc
l'ID est le même mais le nom ne l'est plus.

Le juge de paix est `sources/dbc/spells_enUS.json` : mêmes 49 839 IDs que le
frFR, donc `enUS[id].N` est GARANTI aligné sur `frFR[id].N`. Le test :

    norm(enUS[id].N) == norm(asc[id].N)  ->  appariement PROUVÉ bon
    enUS[id].N existe et diffère         ->  appariement PROUVÉ mauvais
    enUS[id] absent                      ->  indécidable

    python outils/mesurer_fiabilite_appariement.py
"""
import io
import json
import os
import random
import re
import sys
import unicodedata
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(BASE, "rapports", "_mesure_appariement_brut.json")

GRAINE = 20260726          # échantillon Glayna reproductible
SEUIL_RATIO = 1.6          # rapport de longueur EN/FR jugé anormal (cf. rapport)

# --- repris À L'IDENTIQUE de appliquer_divergences_officielles.py ------------
JUNK = re.compile(r"\b(OLD|TEST|PH|PLACEHOLDER|UNUSED|DEPRECATED|DND|\(old\))\b|"
                  r"^\s*$|^z+test|^test", re.I)


def norm(s):
    if not s:
        return ""
    s = s.lower().strip()
    s = s.replace("’", "'").replace("ʼ", "'").replace("`", "'")
    s = s.replace(" ", " ").replace("œ", "oe").replace("æ", "ae")
    s = re.sub(r"\s+", " ", s)
    return re.sub(r"[.…]+$", "", s)
# ---------------------------------------------------------------------------


def charger(p):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def nom_de(d, sid):
    v = d.get(str(sid))
    return v.get("N") if isinstance(v, dict) else v


def sans_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s or "")
                   if unicodedata.category(c) != "Mn")


def cle_nue(s):
    """Clé de comparaison la plus permissive : minuscule, sans accent, sans
    ponctuation. Deux noms qui diffèrent seulement là-dessus sont « le même »."""
    return re.sub(r"[^a-z0-9]+", " ", sans_accents(norm(s))).strip()


def cle_collee(s):
    """Comme cle_nue mais SANS AUCUN séparateur : « Holy Form » et
    « Holyform », « Major Spell Power » et « Major Spellpower » sont le même
    nom simplement réespacé. Sans ce repli, le test les déclare faux à tort."""
    return re.sub(r"[^a-z0-9]+", "", sans_accents(norm(s)))


def meme_nom(a, b):
    """Les deux noms anglais désignent-ils la même chose ?"""
    if a is None or b is None:
        return False
    return cle_nue(a) == cle_nue(b) or cle_collee(a) == cle_collee(b)


MOTS = re.compile(r"[0-9A-Za-zÀ-ſ]+")


def mots(s):
    return set(m.lower() for m in MOTS.findall(sans_accents(s or "")))


# ---------------------------------------------------------------------------
# Signaux mécaniques demandés (applicables SANS ID — donc utilisables sur Glayna)
# ---------------------------------------------------------------------------
def signaux(en, cible):
    """Signaux de perte d'information entre le nom EN et la valeur proposée."""
    s = []

    # 1. qualificatif entre parenthèses côté EN, absent côté FR
    par_en = re.findall(r"\(([^)]*)\)", en)
    if par_en and not re.search(r"\(", cible):
        s.append("parenthese_perdue(%s)" % "|".join(par_en))

    # 2. EN qui énumère (and / virgule) contre une cible nettement plus courte
    enumere = bool(re.search(r"\band\b|,", en, re.I))
    if enumere and len(MOTS.findall(cible)) < len(MOTS.findall(en)) - 1:
        s.append("enumeration_tronquee")

    # 3. chiffre dans la cible, absent de l'EN
    ch_c = set(re.findall(r"\d+", cible)) - set(re.findall(r"\d+", en))
    if ch_c:
        s.append("chiffre_ajoute(%s)" % ",".join(sorted(ch_c)))

    # 4. rapport de longueur anormal (le FR est normalement PLUS long que l'EN)
    lc = len(cible.strip())
    if lc and len(en.strip()) / float(lc) >= SEUIL_RATIO:
        s.append("trop_court(%.2f)" % (len(en.strip()) / float(lc)))

    # 5. mot significatif de l'EN sans aucun écho dans la cible : l'EN a des
    #    mots que la cible n'a pas ET la cible est plus courte en mots
    return s


def main():
    print("Chargement des sources...")
    asc = charger(os.path.join(BASE, "sources", "dbc", "spells_Ascension.json"))
    offi = charger(os.path.join(BASE, "sources", "dbc", "spells_frFR.json"))
    blz_en = charger(os.path.join(BASE, "sources", "dbc", "spells_enUS.json"))
    print("  asc=%d  frFR=%d  enUS=%d" % (len(asc), len(offi), len(blz_en)))

    # index nom EN Ascension -> IDs (même clé brute que le script d'origine)
    ids_par_en = defaultdict(list)
    for sid, rec in asc.items():
        en = rec.get("N") if isinstance(rec, dict) else rec
        if en:
            ids_par_en[en].append(sid)

    # ------------------------------------------------------------------
    # 1) les 121 divergences en attente
    # ------------------------------------------------------------------
    fichier = os.path.join(BASE, "traductions",
                           "divergences_officielles_a_arbitrer.txt")
    txt = io.open(fichier, encoding="utf-8").read()
    blocs = re.findall(r"^EN : (.*)\nnous : (.*)\nofficiel : (.*)$",
                       txt, re.M)
    print("divergences lues :", len(blocs))

    resultats = []
    for en, notre, off in blocs:
        n_off = norm(off)
        # IDs qui ont pu FOURNIR cette valeur officielle (mêmes filtres que
        # le script d'origine : valeur non vide, non JUNK, différente de nous)
        contributeurs = []
        for sid in ids_par_en.get(en, []):
            o = nom_de(offi, sid)
            if o and o.strip() and not JUNK.search(o) and norm(o) == n_off:
                contributeurs.append(sid)

        preuves = []
        for sid in contributeurs:
            be = nom_de(blz_en, sid)
            preuves.append({
                "id": sid,
                "blizz_en": be,
                "identique": meme_nom(be, en),
                "respace": (be is not None and cle_nue(be) != cle_nue(en)
                            and cle_collee(be) == cle_collee(en)),
                "connu": be is not None,
            })

        if any(p["identique"] for p in preuves):
            seau = "SUR"
            sid_ok = next(p["id"] for p in preuves if p["identique"])
            exact = any(p["blizz_en"] == en for p in preuves if p["identique"])
            raison = ("nom anglais Blizzard %s a l'ID %s"
                      % ("IDENTIQUE caractere pour caractere"
                         if exact else "identique (casse/accent/ponctuation)",
                         sid_ok))
        elif preuves and all(p["connu"] for p in preuves):
            autres = sorted(set(p["blizz_en"] for p in preuves))
            seau = "FAUX"
            raison = ("Blizzard nommait ce(s) ID(s) %s — Ascension a renomme "
                      "le sort, le francais est celui de l'ancien nom"
                      % " / ".join('"%s"' % a for a in autres))
        elif not preuves:
            seau = "A_VERIFIER"
            raison = "aucun ID contributeur retrouve (source regeneree ?)"
        else:
            inconnus = [p["id"] for p in preuves if not p["connu"]]
            seau = "A_VERIFIER"
            raison = "ID(s) %s absent(s) du DBC Blizzard : indecidable" % \
                     ",".join(inconnus)

        resultats.append({
            "en": en, "nous": notre, "officiel": off,
            "seau": seau, "raison": raison,
            "exact_char": any(p["blizz_en"] == en for p in preuves),
            "ids": [p["id"] for p in preuves],
            "blizz_en": [p["blizz_en"] for p in preuves],
            "nb_ids_du_nom": len(ids_par_en.get(en, [])),
            "signaux": signaux(en, off),
        })

    # --- contrôle : croiser avec l'arbitrage MANUEL de Dan (121 décisions) ---
    dec_txt = io.open(os.path.join(BASE, "traductions",
                                   "divergences_121_decisions.txt"),
                      encoding="utf-8").read()
    decisions = {m.group(2): m.group(1) for m in
                 re.finditer(r"^ *\d+ \[(GARDER|OFFICIEL)\] (.*)$", dec_txt, re.M)}
    for r in resultats:
        r["decision_dan"] = decisions.get(r["en"], "?")

    # ------------------------------------------------------------------
    # 2) échantillon Glayna
    # ------------------------------------------------------------------
    # Couche Glayna retirée (bloc A, 29/07/2026) : le rapport vit désormais
    # dans archive/glayna/. L'échantillon est sauté s'il n'est plus là.
    gl_fichier = os.path.join(BASE, "rapports", "arbitrage_noms_glayna.txt")
    if not os.path.exists(gl_fichier):
        gl_fichier = os.path.join(BASE, "archive", "glayna",
                                  "arbitrage_noms_glayna.txt")
    if os.path.exists(gl_fichier):
        gtxt = io.open(gl_fichier, encoding="utf-8").read()
        gblocs = re.findall(r"^EN    : (.*)\nnous  : (.*)\nGlayna: (.*)$",
                            gtxt, re.M)
        print("conflits Glayna lus :", len(gblocs))
    else:
        print("échantillon Glayna : rapport absent (couche retirée) — sauté")
        gblocs = []
    rnd = random.Random(GRAINE)
    echantillon = rnd.sample(gblocs, min(200, len(gblocs)))

    gl_res = []
    for en, notre, gl in echantillon:
        ids = ids_par_en.get(en, [])
        # Risque d'homonymie : le MÊME nom anglais porté par plusieurs sorts
        # Ascension que Blizzard, lui, nommait DIFFÉREMMENT -> une seule
        # traduction pour des sorts distincts.
        blz = sorted(set(x for x in (nom_de(blz_en, s) for s in ids) if x))
        gl_res.append({
            "en": en, "nous": notre, "glayna": gl,
            "nb_ids_du_nom": len(ids),
            "present_dans_asc": bool(ids),
            "blizz_en_distincts": blz,
            "homonymie": len([b for b in blz if not meme_nom(b, en)]),
            "a_un_officiel": any(nom_de(offi, s) for s in ids),
            "signaux": signaux(en, gl),
            "signaux_nous": signaux(en, notre),
        })

    # ------------------------------------------------------------------
    # 3) majuscules non accentuées dans la source officielle 3.3.5a
    # ------------------------------------------------------------------
    # méthode : on construit depuis le corpus officiel lui-même la liste des
    # mots qui existent ACCENTUÉS ; un mot initial en majuscule non accentuée
    # dont la version « nue » correspond à un mot accenté du corpus est suspect.
    accentues = defaultdict(lambda: defaultdict(int))
    for sid, rec in offi.items():
        n = rec.get("N") if isinstance(rec, dict) else rec
        if not n:
            continue
        for m in MOTS.findall(n):
            nu = sans_accents(m).lower()
            if len(nu) >= 3:
                accentues[nu][m.lower()] += 1

    suspects = defaultdict(list)
    total_noms = 0
    for sid, rec in offi.items():
        n = rec.get("N") if isinstance(rec, dict) else rec
        if not n or not n.strip() or JUNK.search(n):
            continue
        total_noms += 1
        m = MOTS.match(n.strip())
        if not m:
            continue
        prem = m.group(0)
        if not prem[:1].isupper() or prem[:1] not in "AEIOU":
            continue
        if sans_accents(prem) != prem:            # déjà accentué
            continue
        nu = prem.lower()
        variantes = accentues.get(nu, {})
        # L'accent doit porter sur la PREMIÈRE lettre (« Equilibre » ->
        # « Équilibre »). Sans ce garde-fou, « Augmente » serait apparié à
        # « augmenté » (participe) et « Arme » à « armé » : faux positifs.
        acc = {v: c for v, c in variantes.items()
               if sans_accents(v[:1]) != v[:1]}
        nonacc = sum(c for v, c in variantes.items()
                     if sans_accents(v[:1]) == v[:1])
        if acc:
            suspects[prem].append({
                "id": sid, "nom": n,
                "variante_accentuee": max(acc, key=acc.get),
                "n_acc": sum(acc.values()), "n_nonacc": nonacc,
            })

    brut = {
        "graine": GRAINE, "seuil_ratio": SEUIL_RATIO,
        "n_asc": len(asc), "n_frFR": len(offi), "n_enUS": len(blz_en),
        "divergences": resultats,
        "glayna_total": len(gblocs), "glayna_echantillon": gl_res,
        "accent_total_noms_officiels": total_noms,
        "accent_suspects": {k: v for k, v in suspects.items()},
    }
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    json.dump(brut, open(SORTIE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # ------------------------------------------------------------------
    from collections import Counter
    c = Counter(r["seau"] for r in resultats)
    print("\n=== 121 divergences ===")
    for k in ("SUR", "A_VERIFIER", "FAUX"):
        print("  %-11s %d" % (k, c.get(k, 0)))
    print("\n--- exemples FAUX ---")
    for r in resultats:
        if r["seau"] == "FAUX":
            print("  %-38s %-26s -> %-24s | %s"
                  % (r["en"][:36], r["nous"][:24], r["officiel"][:22],
                     r["blizz_en"][0] if r["blizz_en"] else "?"))
    print("\n=== croisement avec l'arbitrage MANUEL de Dan ===")
    croise = Counter((r["seau"], r["decision_dan"]) for r in resultats)
    for k, v in sorted(croise.items()):
        print("  %-11s x %-9s %d" % (k[0], k[1], v))
    print("  (SUR + exact caractere pour caractere : %d)"
          % sum(1 for r in resultats if r["seau"] == "SUR" and r["exact_char"]))

    print("\n=== signaux mecaniques (121) ===")
    sc, par_seau = Counter(), Counter()
    for r in resultats:
        for s in r["signaux"]:
            sc[s.split("(")[0]] += 1
        if r["signaux"]:
            par_seau[r["seau"]] += 1
    for k, v in sc.most_common():
        print("  %-24s %d" % (k, v))
    print("  -- entrees portant >=1 signal, par seau :", dict(par_seau))
    print("  -- FAUX SANS aucun signal mecanique     :",
          sum(1 for r in resultats if r["seau"] == "FAUX" and not r["signaux"]))
    print("  -- SUR AVEC un signal (faux positif)    :",
          sum(1 for r in resultats if r["seau"] == "SUR" and r["signaux"]))
    print("\n=== Glayna (echantillon %d / %d) ===" % (len(gl_res), len(gblocs)))
    gsc = Counter()
    for r in gl_res:
        for s in r["signaux"]:
            gsc[s.split("(")[0]] += 1
    for k, v in gsc.most_common():
        print("  %-24s %d" % (k, v))
    print("  absents de spells_Ascension :",
          sum(1 for r in gl_res if not r["present_dans_asc"]))
    print("  nom EN porte par >1 ID      :",
          sum(1 for r in gl_res if r["nb_ids_du_nom"] > 1))
    print("  homonymie (Blizzard nommait autrement un des IDs) :",
          sum(1 for r in gl_res if r["homonymie"]))
    print("  a un officiel Blizzard      :",
          sum(1 for r in gl_res if r["a_un_officiel"]))
    print("\n=== accents (source officielle) ===")
    print("  noms officiels retenus :", total_noms)
    print("  entrees suspectes      :", sum(len(v) for v in suspects.values()))
    print("  mots distincts         :", len(suspects))
    for mot, lst in sorted(suspects.items(), key=lambda kv: -len(kv[1]))[:25]:
        print("    %-16s %4d  -> %s" % (mot, len(lst),
                                        lst[0]["variante_accentuee"]))
    print("\nbrut :", SORTIE)


if __name__ == "__main__":
    main()
