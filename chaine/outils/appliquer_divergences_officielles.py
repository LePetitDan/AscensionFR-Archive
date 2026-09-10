# -*- coding: utf-8 -*-
"""
DIVERGENCES vs OFFICIEL Blizzard : là où notre nom de sort diffère du frFR
officiel. On n'ADOPTE l'officiel QUE si notre valeur a un DÉFAUT mécanique
sûr :
  1. anglais qui traîne (un mot du nom EN reste dans notre FR) ;
  2. mêmes mots que l'officiel, juste réordonnés / accentués ;
  3. chimère corrompue (« ...Verrouillage de la cible... ») ;
  4. notre « traduction » est en fait un AUTRE nom de sort anglais.
Le RESTE (vrais choix de vocabulaire : « Bash » -> « Sonner », variantes de
couleur perdues…) part dans un rapport « à arbitrer » — décision de Dan, pas
écrasée à l'aveugle.

DÉTERMINISTE (regroupement par nom EN ; officiel adopté seulement s'il est
UNIQUE parmi les IDs de ce nom). Réversible (sorts.json.bak).

GARDE-FOU D'APPARIEMENT (26/07/2026) : un officiel n'entre dans l'index que si
Blizzard nommait bien cet ID comme Ascension le nomme — voir garde_appariement.
Sans lui, la passe partait à 40 % de régressions : 48 des 119 entrées qu'elle
touche (mesuré au lot 5, garde éteint, 7 sûres + 112 à arbitrer). Mesuré ici :
653 couples (ID, officiel) écartés, et les 48 entrées démontrées fausses au
lot 5 tombent en totalité.

GARDE D'ACCENT (27/07/2026) : notre français accentue les majuscules initiales
depuis le lot 7, l'officiel 3.3.5a non. Un nom qui ne diffère de l'officiel QUE
par là est une CONCORDANCE — voir le test de concordance plus bas.

  python outils/appliquer_divergences_officielles.py            # simulation
  python outils/appliquer_divergences_officielles.py --appliquer
"""
import json, os, re, sys, shutil

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from garde_appariement import (charger_blizzard, appariement_prouve,  # noqa: E402
                               indecidable)
from accents_majuscules import difference_d_accent_seule  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTS = os.path.join(BASE, "traductions", "sorts.json")
RAPPORT = os.path.join(BASE, "traductions",
                       "divergences_officielles_appliquees.txt")
ARBITRER = os.path.join(BASE, "traductions",
                        "divergences_officielles_a_arbitrer.txt")
# LES ARBITRAGES RENDUS (bloc A du programme 3, 29/07/2026) : les 7 règles
# de Dan, nom par nom. « adopter » = l'officiel entre avec les SÛRES ;
# « garder » = notre valeur reste ET sort du fichier d'arbitrage (la
# question est tranchée, la reposer serait du bruit).
DECISIONS = os.path.join(BASE, "traductions",
                         "divergences_officielles_decisions.json")

JUNK = re.compile(r"\b(OLD|TEST|PH|PLACEHOLDER|UNUSED|DEPRECATED|DND|\(old\))\b|"
                  r"^\s*$|^z+test|^test", re.I)


def charger(p):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def norm(s):
    if not s:
        return ""
    s = s.lower().strip()
    s = s.replace("’", "'").replace("ʼ", "'").replace("`", "'")
    s = s.replace(" ", " ").replace("œ", "oe").replace("æ", "ae")
    s = re.sub(r"\s+", " ", s)
    return re.sub(r"[.…]+$", "", s)


def nom_de(d, sid):
    v = d.get(str(sid))
    return v.get("N") if isinstance(v, dict) else v


def mots(s, mini=3):
    return set(w for w in re.findall(r"[0-9a-zà-ÿœæ]+", (s or "").lower())
               if len(w) >= mini)


def main():
    appliquer = "--appliquer" in sys.argv
    asc = charger(os.path.join(BASE, "sources", "dbc", "spells_Ascension.json"))
    offi = charger(os.path.join(BASE, "sources", "dbc", "spells_frFR.json"))
    pack = charger(os.path.join(BASE, "sources", "packfr_sorts.json"))
    blz = charger_blizzard()          # juge de paix : le nom EN de Blizzard
    data = charger(SORTS)
    noms = data["noms"]

    # nom EN -> officiels / PackFR (jointure par ID)  +  ensemble des noms EN
    off_par_en, pack_par_en, noms_en = {}, {}, set()
    ecartes = indecis = 0
    for sid, rec in asc.items():
        en = rec.get("N") if isinstance(rec, dict) else rec
        if not en:
            continue
        noms_en.add(norm(en))
        o = nom_de(offi, sid)
        if o and o.strip() and not JUNK.search(o):
            # Filtrage À LA SOURCE : un officiel dont l'ID a été RENOMMÉ par
            # Ascension traduit l'ancien nom (ID 2831 « Armor +8 » devenu
            # « Armor (Light) »). L'écarter ici plutôt qu'en aval évite qu'il
            # ne pollue aussi le test d'unicité (les « ambigus »).
            if appariement_prouve(blz, sid, en):
                off_par_en.setdefault(en, set()).add(o.strip())
            else:
                ecartes += 1
                if indecidable(blz, sid):
                    indecis += 1      # sous-ensemble des écartés, pas un 3e seau
        p = nom_de(pack, sid)
        if p and p.strip() and not JUNK.search(p):
            pack_par_en.setdefault(en, set()).add(p.strip())

    def defaut_sur(en, notre, off):
        """True si notre valeur a un défaut mécanique -> officiel plus sûr."""
        nn = norm(notre)
        # 1. anglais du nom EN qui traîne dans notre FR — mais PAS un cognat
        #    (aura, ogre, charge…) : un mot légitime serait AUSSI dans l'officiel.
        #    Fuite = mot du nom EN, présent chez nous, ABSENT de l'officiel.
        mots_en_anglais = set(w for w in re.findall(r"[a-z]{4,}", en.lower()))
        if (mots_en_anglais & mots(notre, 4)) - mots(off, 4):
            return True
        # 2. mêmes mots que l'officiel (réordonné / accent). Les « accent
        #    initial seul » n'arrivent JAMAIS jusqu'ici : ils sont sortis en
        #    amont, au test de concordance — et c'est vital, voir le
        #    commentaire là-bas.
        if mots(notre) == mots(off):
            return True
        # 3. chimère corrompue
        if "verrouillage" in nn:
            return True
        # 4. notre valeur est en fait un autre nom de sort anglais
        if nn in noms_en:
            return True
        return False

    decisions = charger(DECISIONS)
    surs, arbitrer, ambigus, accent_seul = [], [], 0, 0
    tranches_adopter, tranches_garder = [], 0
    for en in sorted(off_par_en):
        notre = noms.get(en)
        if not notre:
            continue
        n_notre = norm(notre)
        humaines = off_par_en.get(en, set()) | pack_par_en.get(en, set())
        if any(norm(h) == n_notre for h in humaines):
            continue
        # DIFFÉRENCE D'ACCENT SEULE = CONCORDANCE. Le lot 7 accentue les
        # majuscules initiales, Blizzard ne les accentuait pas en 3.3.5a :
        # notre « Éclair de givre » contre son « Eclair de givre ». C'est une
        # décision déjà prise, pas un désaccord de vocabulaire ; sans ce test
        # le fichier d'arbitrage de Dan enfle de 66 vraies divergences à 468
        # (mesuré le 27/07 : 402 entrées écartées à ce seul titre).
        #
        # Et surtout : ces entrées frôlent la règle 2 de `defaut_sur` (« mêmes
        # mots que l'officiel, réordonnés / accentués » -> adopter l'officiel).
        # Si elle ne se déclenche pas dessus aujourd'hui, c'est par un pur
        # accident d'implémentation — `mots()` garde les accents, donc
        # « éclair » != « eclair ». Le jour où quelqu'un « améliore » `mots()`
        # en dénudant les accents, ces ~400 noms basculent en SÛRES et un seul
        # --appliquer réécrit tous nos accents avec la version NON accentuée de
        # Blizzard. Mine désamorcée ici, en amont de `defaut_sur`.
        if any(difference_d_accent_seule(notre, h) for h in humaines):
            accent_seul += 1
            continue
        groupes = {}
        for o in off_par_en[en]:
            if norm(o) != n_notre:
                groupes.setdefault(norm(o), o)
        if not groupes:
            continue
        if len(groupes) > 1:
            ambigus += 1
            continue
        off = sorted(groupes.values())[0]
        # Arbitrage DÉJÀ RENDU : il prime sur l'heuristique defaut_sur.
        tranche = decisions.get(en)
        if tranche:
            if tranche["verdict"] == "adopter":
                # la valeur du fichier de décisions fait foi (elle porte nos
                # accents là où l'officiel 3.3.5a n'en met pas)
                tranches_adopter.append((en, notre, tranche["officiel"]))
            else:
                tranches_garder += 1
            continue
        (surs if defaut_sur(en, notre, off) else arbitrer).append((en, notre, off))
    surs.extend(tranches_adopter)

    with open(RAPPORT, "w", encoding="utf-8") as f:
        f.write("Corrections SÛRES adoptées (%d)\n%s\n\n" % (len(surs), "=" * 40))
        for en, notre, off in surs:
            f.write("EN : %s\navant : %s\nofficiel : %s\n\n" % (en, notre, off))
    with open(ARBITRER, "w", encoding="utf-8") as f:
        f.write("À ARBITRER — choix de vocabulaire (%d), non appliqués\n%s\n"
                % (len(arbitrer), "=" * 40))
        f.write("(%d entrées tenues hors de cette liste : elles ne diffèrent de"
                " l'officiel\nque par notre accent sur la majuscule initiale —"
                " décision déjà prise.)\n\n" % accent_seul)
        for en, notre, off in arbitrer:
            f.write("EN : %s\nnous : %s\nofficiel : %s\n\n" % (en, notre, off))

    print("Corrections SÛRES (à appliquer) :", len(surs),
          "(dont %d tranchées par les règles de Dan)" % len(tranches_adopter))
    print("À ARBITRER (vocabulaire, non appliqué) :", len(arbitrer))
    print("Tranchées « on garde le nôtre » (hors arbitrage) :",
          tranches_garder)
    print("Ambigus (plusieurs officiels, ignorés) :", ambigus)
    print("Concordances à l'accent près (notre règle du lot 7) :", accent_seul)
    print("Officiels écartés (ID renommé par Ascension) :", ecartes)
    print("  dont indécidables (ID inconnu du DBC Blizzard) :", indecis)
    print("\n--- 18 corrections sûres ---")
    for en, notre, off in surs[:18]:
        print("  %-30s  %-22s -> %s" % (en[:28], notre[:20], off[:28]))
    print("\n--- 8 exemples à arbitrer (NON appliqués) ---")
    for en, notre, off in arbitrer[:8]:
        print("  %-30s  %-22s -> %s" % (en[:28], notre[:20], off[:28]))
    print("\nRapports :", os.path.basename(RAPPORT), "+", os.path.basename(ARBITRER))

    if appliquer:
        shutil.copy2(SORTS, SORTS + ".bak")
        for en, notre, off in surs:
            noms[en] = off
        with open(SORTS, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1, sort_keys=True)
        print("\n>>> APPLIQUÉ %d corrections sûres. Sauvegarde : sorts.json.bak"
              % len(surs))
    else:
        print("\n(simulation — relancer avec --appliquer)")


if __name__ == "__main__":
    main()
