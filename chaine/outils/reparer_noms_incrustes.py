# -*- coding: utf-8 -*-
"""
RÉPARATION des noms anglais INCRUSTÉS dans les descriptions françaises.
=======================================================================
(Chantier du 23/07/2026 — 1 963 descriptions mesurées, table des noms
purgée au préalable par purger_noms_poison.py.)

Le mal : « Vos 3 prochaines |cFFFFFFFFTitanstrikes|r subissent… » — la
machine avait gardé le nom anglais coloré tel quel.

Le remède, dans l'ordre :
  1. repérer dans le FRANÇAIS les morceaux colorés |cFF……|r dont le texte
     est un nom ANGLAIS connu de la table (ancrage : le même morceau doit
     exister dans la source anglaise — jamais de remplacement deviné) ;
  2. substituer le nom FRANÇAIS dans la SOURCE ANGLAISE, puis RETRADUIRE
     la phrase entière : les accords sortent justes ;
  3. GARDES avant d'accepter : mêmes codes $ (multiset exact) et chaque
     nom français présent tel quel — sinon on GARDE l'ancienne version.

Reprenable (cache), sauvegarde automatique de sorts.json au premier
passage. Usage : python outils/reparer_noms_incrustes.py [--dry]
"""
import io
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from traduire_gisement import traduire  # noqa: E402
from adopter_frenchtooltip import chimere  # noqa: E402
from noms_empoisonnes import empoisonne  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTS = os.path.join(BASE, "traductions", "sorts.json")
SAUVEGARDE = os.path.join(BASE, "traductions",
                          "sorts_avant_reparation_noms.json")
CACHE = os.path.join(BASE, "traductions", "cache_noms_incrustes.json")
RAPPORT = os.path.join(BASE, "rapports", "noms_incrustes_repares.txt")

RE_COLORE = re.compile(r"\|c[fF]{2}[0-9a-fA-F]{6}([^|]{2,60})\|r")
# Les codes $ des sorts : formules ${…}, variables ($s1, $805410m1u,
# $<mult>, $lsec:secs;…) et « $ » nu. Le multiset doit survivre intact.
RE_DOLLARS = re.compile(r"\$\{[^}]*\}|\$l[^;]*;|\$<[^>]+>|\$[A-Za-z]\w*"
                        r"|\$\?[^\[]*|\$")


def multiset_dollars(texte):
    return sorted(RE_DOLLARS.findall(texte or ""))


def pluriel_fr(nom):
    """Pluriel PRUDENT : un seul mot -> +s ; plusieurs mots -> inchangé
    (mieux vaut un singulier correct qu'un « des las » inventé)."""
    if " " in nom or nom.endswith("s") or nom.endswith("x"):
        return nom
    return nom + "s"


def table_saine(noms):
    """LE FILTRE DE VALEUR (bloc 6, 28/07/2026). La table des noms est
    EMPOISONNÉE (mesuré : ~869 valeurs bidon — « Wild Imp » -> vide,
    « Wind Bolt » -> « Trait d'eau », des paires croisées « Felfury » ->
    « Cleansing Waters ») : l'ancrage dans la source anglaise ne protège
    QUE la clé, pas la valeur — sans ce filtre, ~381 descriptions
    recevraient une saleté. On écarte : valeur vide, valeur identique à la
    clé, valeur qui est le nom ANGLAIS d'une AUTRE entrée (croisement),
    chimère mot-à-mot, et la table POISON du lot 9."""
    cles_en = {c.strip() for c in noms}
    saine, ecartees = {}, 0
    for en, fr in noms.items():
        fr = (fr or "").strip()
        if (not fr or fr == en.strip()
                or (fr in cles_en and fr != en.strip())
                or chimere(fr)
                or empoisonne(en, fr)):
            ecartees += 1
            continue
        saine[en] = fr
    return saine, ecartees


# Nom anglais NON coloré incrusté dans une phrase française (« votre
# capacité Shield Slam ») : uniquement des noms d'au moins DEUX mots à
# majuscules — un mot seul (« Charge ») est trop ambigu — et l'ancrage
# vaut comme pour les colorés : le même morceau doit exister dans l'EN.
RE_NOM_NU = re.compile(r"\b([A-Z][A-Za-z'’-]+(?: (?:of|the|[A-Z][A-Za-z'’-]+))+)\b")


def substitutions(en, fr, noms):
    """[(morceau_anglais, nom_fr)] des noms incrustés RÉPARABLES —
    colorés d'abord, puis noms NUS ≥ 2 mots, DU PLUS LONG AU PLUS COURT
    (53 descriptions ont des noms emboîtés : l'ordre naïf fabrique
    « Glyphe de Totem de griffe de pierre »)."""
    trouvees = []
    vus = set()

    def poser(morceau):
        brut = morceau.strip()
        if brut in vus:
            return
        for candidat, pluriel in ((brut, False),
                                  (brut[:-1] if brut.endswith("s")
                                   else brut, brut.endswith("s"))):
            nom_fr = noms.get(candidat)
            if nom_fr and nom_fr != candidat and morceau in en:
                vus.add(brut)
                trouvees.append(
                    (morceau, pluriel_fr(nom_fr) if pluriel else nom_fr))
                return

    for morceau in RE_COLORE.findall(fr):
        poser(morceau)
    for morceau in RE_NOM_NU.findall(fr):
        poser(morceau)
    # DU PLUS LONG AU PLUS COURT — le garde-fou des noms emboîtés.
    trouvees.sort(key=lambda t: -len(t[0]))
    return trouvees


def main():
    dry = "--dry" in sys.argv
    with io.open(SORTS, encoding="utf-8") as f:
        cache_sorts = json.load(f)
    noms, ecartees = table_saine(cache_sorts.get("noms", {}))
    print("table des noms : %d saines, %d valeurs bidon écartées "
          "(filtre de valeur)" % (len(noms), ecartees))
    descs = cache_sorts.get("descriptions", {})

    cache = {}
    if os.path.exists(CACHE):
        with io.open(CACHE, encoding="utf-8") as f:
            cache = json.load(f)

    a_faire = []
    n_colores, n_nus = 0, 0
    for en, fr in descs.items():
        subs = substitutions(en, fr, noms)
        if subs:
            a_faire.append((en, fr, subs))
            if "|c" in fr:
                n_colores += 1
            else:
                n_nus += 1
    print("descriptions à réparer :", len(a_faire),
          "(%d à noms colorés, %d à noms nus)" % (n_colores, n_nus),
          "| déjà au cache :", sum(1 for en, _, _ in a_faire
                                   if en in cache))
    if dry:
        for en, fr, subs in a_faire[:5]:
            print("  ", subs, "->", en[:60])
        return

    if not os.path.exists(SAUVEGARDE):
        shutil.copy2(SORTS, SAUVEGARDE)
        print("sauvegarde :", SAUVEGARDE)

    repares, gardes_anciens, faits = 0, 0, 0
    journal = []
    for en, fr, subs in a_faire:
        faits += 1
        if en in cache:
            nouveau = cache[en]
        else:
            en_prime = en
            for morceau, nom_fr in subs:
                en_prime = en_prime.replace(morceau, nom_fr)
            nouveau = traduire(en_prime)
            cache[en] = nouveau or ""
            if faits % 25 == 0:
                with io.open(CACHE, "w", encoding="utf-8") as f:
                    json.dump(cache, f, ensure_ascii=False, indent=1)
                print("  %d / %d…" % (faits, len(a_faire)))
        if not nouveau:
            gardes_anciens += 1
            continue
        # RATTRAPAGE (24/07) : Google égare parfois le nom substitué —
        # anglais remis (« Warrior of Dawn ») ou QUASI-variante française
        # (« Guerrier d'aube » pour « Guerrier de l'aube »). Deux filets :
        # 1. le morceau anglais d'origine est là -> on le remplace ;
        # 2. un morceau COLORÉ de la sortie partage premier ou dernier mot
        #    avec le nom attendu -> on normalise vers la forme de la table.
        for morceau, nom_fr in subs:
            if nom_fr in nouveau:
                continue
            if morceau in nouveau:
                nouveau = nouveau.replace(morceau, nom_fr)
                cache[en] = nouveau
                continue
            mots_attendus = nom_fr.lower().split()
            for colore in set(RE_COLORE.findall(nouveau)):
                mots = colore.strip().lower().split()
                if not mots or colore.strip() == nom_fr:
                    continue
                if mots[0] == mots_attendus[0] \
                        or mots[-1] == mots_attendus[-1]:
                    nouveau = nouveau.replace(colore, nom_fr)
                    cache[en] = nouveau
                    break
        # GARDES : codes $ intacts, chaque nom français présent.
        if multiset_dollars(nouveau) != multiset_dollars(en):
            gardes_anciens += 1
            journal.append(("codes $", en[:60]))
            continue
        if any(nom_fr not in nouveau for _, nom_fr in subs):
            gardes_anciens += 1
            journal.append(("nom absent", en[:60]))
            continue
        descs[en] = nouveau
        repares += 1

    with io.open(CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1)
    with io.open(SORTS, "w", encoding="utf-8") as f:
        json.dump(cache_sorts, f, ensure_ascii=False, indent=1,
                  sort_keys=True)
    os.makedirs(os.path.dirname(RAPPORT), exist_ok=True)
    with io.open(RAPPORT, "w", encoding="utf-8") as f:
        f.write("Réparation des noms incrustés — %d réparées, %d gardées "
                "anciennes\n\n" % (repares, gardes_anciens))
        for raison, extrait in journal:
            f.write("garde [%s] %s\n" % (raison, extrait))
    print("réparées :", repares, "| gardées (gardes) :", gardes_anciens)
    print("rapport :", RAPPORT)


if __name__ == "__main__":
    main()
