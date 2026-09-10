# -*- coding: utf-8 -*-
"""
Génère la base des sorts en français à partir de trois sources :
  1. Spell.dbc officiel frFR (traduction Blizzard parfaite)
  2. Spell.dbc officiel enUS (pour détecter ce qu'Ascension a modifié)
  3. Spell.dbc d'Ascension (patch-T.MPQ) : 230 000 sorts

Stratégie, du moins cher au plus cher :
  a. ID identique + texte identique      -> traduction officielle telle quelle
  b. Texte identique aux chiffres près   -> traduction officielle avec report
                                            des chiffres d'Ascension
  c. Le reste                            -> a_traduire/sorts.json (Google/IA)

Seuls les sorts joueur sont traités (présents dans SkillLineAbility.dbc ou
Talent.dbc) : les 200 000 sorts internes ne sont jamais vus par le joueur.

Par défaut, tous les sorts joueur sont traités : classes, métiers, races,
montures. --classes-seulement restreint aux compétences de classe.

Usage : python generateur_sorts.py [--classes-seulement]
"""
import json
import os
import re
import struct
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DBC = os.path.join(BASE, "sources", "dbc")

# Catégorie 7 = compétences de classe (SkillLine.dbc)
CATEGORIE_CLASSE = 7

# Variables que le client résout lui-même dans les info-bulles ($s1, $d...).
# Quand une description en contient, l'addon a besoin du modèle anglais pour
# récupérer les valeurs affichées et les replacer dans le texte français.
VARIABLE = re.compile(
    r"\$\{[^}]*\}"
    r"|\$\?[^\[]*\[[^\]]*\](?:\[[^\]]*\])?"
    r"|\$/\d+;\d*[a-zA-Z]\d*"
    r"|\$[GgLl][^;]*;"
    r"|\$@[a-zA-Z]+"
    r"|\$\d+[a-zA-Z]\d*"
    r"|\$[a-zA-Z]\d*")


def lire_dbc(nom):
    with open(os.path.join(DBC, nom), "rb") as f:
        b = f.read()
    magic, nb, nch, ts, sb = struct.unpack("<4sIIII", b[:20])
    donnees = b[20:20 + nb * ts]
    bloc = b[20 + nb * ts:]
    enregs = [struct.unpack_from("<%dI" % nch, donnees, i * ts)
              for i in range(nb)]
    return enregs, bloc


def charger(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def normaliser(texte):
    """Texte comparable : chiffres masqués, espaces normalisés."""
    if not texte:
        return ""
    t = re.sub(r"\d+", "#", texte)
    t = re.sub(r"\s+", " ", t)
    return t.strip().lower()


MOT = re.compile(r"\b[\wÀ-ÿ']+\b", re.UNICODE)


def corriger_capitalisation(nom_en, nom_fr):
    """Applique la casse Blizzard française : majuscule au premier mot
    seulement, les noms propres exceptés.

    L'anglais met une majuscule à chaque mot important (« Twilight Nova »),
    le français non (« Nova crépusculaire »). Les traducteurs automatiques
    recopient la casse anglaise. Distinction retenue : un mot français qui
    n'apparaît pas dans le texte anglais a été traduit, c'est donc un mot
    commun -> minuscule ; un mot recopié tel quel de l'anglais est un nom
    propre -> majuscule conservée.
    """
    if not nom_fr or not nom_en:
        return nom_fr
    mots_en = {m.group(0).lower() for m in MOT.finditer(nom_en)}
    premier = [True]  # premier mot de chaque segment de texte

    def traiter(m):
        mot = m.group(0)
        if premier[0]:
            premier[0] = False
            return mot
        if len(mot) <= 2 or mot.isupper():
            return mot          # acronymes et petits mots : intacts
        if not mot[0].isupper():
            return mot
        if mot.lower() in mots_en:
            return mot          # présent en anglais : nom propre probable
        return mot[0].lower() + mot[1:]

    # Traite chaque ligne séparément (les noms multi-lignes ont un titre par
    # ligne) et ignore les codes de couleur.
    sorties = []
    for ligne in nom_fr.split("\n"):
        premier[0] = True
        sorties.append(MOT.sub(traiter, ligne))
    return "\n".join(sorties)


def reporter_chiffres(source_en, officiel_en, officiel_fr):
    """Réinjecte les chiffres d'Ascension dans la traduction officielle.

    N'agit que si les deux textes anglais ont le même nombre de nombres,
    dans le même ordre : sinon le report serait hasardeux.
    """
    n_src = re.findall(r"\d+", source_en)
    n_off = re.findall(r"\d+", officiel_en)
    n_fr = re.findall(r"\d+", officiel_fr)
    if len(n_src) != len(n_off) or len(n_off) != len(n_fr):
        return None
    if n_off != n_fr:
        return None  # la trad officielle a réordonné les nombres : abandon
    if n_src == n_off:
        return officiel_fr
    it = iter(n_src)
    return re.sub(r"\d+", lambda m: next(it), officiel_fr)


def sorts_joueur(categorie_classe_seulement=True):
    """IDs des sorts que le joueur peut apprendre."""
    sl, _ = lire_dbc("SkillLine_Ascension.dbc")
    categorie = {r[0]: r[1] for r in sl}
    sla, _ = lire_dbc("SkillLineAbility_Ascension.dbc")
    ids = set()
    for r in sla:
        skill, spell = r[1], r[2]
        if categorie_classe_seulement and categorie.get(skill) != CATEGORIE_CLASSE:
            continue
        if spell:
            ids.add(str(spell))
    # Sorts de talents (champs 5 à 13 = les rangs)
    tal, _ = lire_dbc("Talent_Ascension.dbc")
    for r in tal:
        for i in range(5, 14):
            if r[i]:
                ids.add(str(r[i]))
    return ids


def main():
    # Tout le contenu visible par le joueur par défaut : les métiers, les
    # races et les montures comptent autant que les sorts de classe.
    toutes = "--classes-seulement" not in sys.argv
    asc = charger(os.path.join(DBC, "spells_Ascension.json"))
    en = charger(os.path.join(DBC, "spells_enUS.json"))
    fr = charger(os.path.join(DBC, "spells_frFR.json"))
    cibles = sorts_joueur(categorie_classe_seulement=not toutes)

    # Sorts attachés aux objets rencontrés : leur description résolue forme
    # les lignes « Utiliser : ... » des info-bulles d'objets. L'addon les
    # traduit par alignement, il lui faut donc le modèle EN et le français
    # de chacun (la plupart sont des sorts Blizzard -> officiel par ID).
    # TOUS les royaumes (pas seulement Rexxar) : les objets propres à Vol'jin,
    # Darkmoon, etc. portent aussi des sorts « Utiliser : ... » à traduire.
    dossier_ex = os.path.join(BASE, "extraits")
    if os.path.isdir(dossier_ex):
        for royaume in sorted(os.listdir(dossier_ex)):
            chemin_objets = os.path.join(dossier_ex, royaume, "objets.json")
            if os.path.isfile(chemin_objets):
                for o in charger(chemin_objets).values():
                    for paire in o.get("Spells", ()):
                        cibles.add(str(paire[0]))

    # Sorts d'objet du TDB COMPLET (24/07/2026). extraits/rexxar/objets.json
    # ci-dessus ne couvre que ~17 000 objets ; le monde en a des centaines de
    # milliers (bloodforge, Wonka, ballons magiques...). Les effets
    # « Utiliser : ... » de ces objets restaient donc en anglais. La liste des
    # spellid_1..5 de item_template est extraite par
    # outils/extraire_sorts_objet_tdb.py -> traductions/sorts_objet_tdb.json.
    # La plupart sont des sorts Blizzard standard -> traduction OFFICIELLE
    # gratuite ; seuls les customs partent à traduire.
    chemin_objets_tdb = os.path.join(BASE, "traductions",
                                     "sorts_objet_tdb.json")
    if os.path.exists(chemin_objets_tdb):
        cibles.update(str(s) for s in charger(chemin_objets_tdb))

    # Sorts récoltés au survol (grimoire hors SkillLine : « Resurrect in
    # Capital City », boutons système...). S'ils existent dans les DBC, le
    # traitement complet par modèle (variables alignables) vaut mieux que le
    # texte résolu figé au moment de la récolte.
    chemin_recoltes = os.path.join(BASE, "traductions", "sorts_recoltes.json")
    if os.path.exists(chemin_recoltes):
        cibles.update(str(s) for s in charger(chemin_recoltes))

    # Sorts RÉFÉRENCÉS par les modèles des cibles (24/07/2026) : les blocs
    # d'aura incrustés des talents (« Scarlet Hammer ») viennent de sorts
    # non lançables, hors SkillLine — extraits par
    # outils/extraire_sorts_references.py.
    chemin_references = os.path.join(BASE, "traductions",
                                     "sorts_references.json")
    if os.path.exists(chemin_references):
        cibles.update(str(s) for s in charger(chemin_references))

    # LES EXCEPTIONS DE VISIBILITÉ (bloc C du programme 5, 29/07/2026).
    #
    # Tout ce qui précède définit « vu » par une SURFACE : lançable,
    # apprenable, porté par un objet, survolé, référencé. Le critère est bon
    # mais il SUR-CLASSE en invisible, et on sait exactement où : les
    # capacités de PNJ. Un joueur ne survole jamais « Wounding Strike », il
    # ne l'apprend pas, aucun objet ne la porte — et pourtant elle défile
    # dans son journal de combat à chaque coup reçu. Le journal de combat
    # n'est pas une info-bulle : la récolte ne le ramènera JAMAIS toute
    # seule, contrairement au reste.
    #
    # D'où cette porte, ouverte le premier jour et pas après le premier
    # signalement : une liste DÉCLARÉE d'identifiants qui rejoignent les
    # cibles quoi qu'en dise le critère. Elle se remplit à la main, ou par
    # les retours de joueurs — c'est le seul endroit du système où « je l'ai
    # vu en jeu » l'emporte sur la mesure.
    chemin_exceptions = os.path.join(BASE, "traductions",
                                     "sorts_exceptions_visibilite.json")
    if os.path.exists(chemin_exceptions):
        exceptions = [str(s) for s in charger(chemin_exceptions)
                      if not str(s).startswith("_")]   # « _lisez_moi »
        cibles.update(exceptions)
        print("exceptions de visibilité      : %6d sort(s) forcé(s) en cible"
              % len(exceptions))

    # Index des textes officiels normalisés -> (anglais, français)
    idx_nom, idx_desc, idx_tt = {}, {}, {}
    for sid, o in en.items():
        f = fr.get(sid)
        if not f:
            continue
        if o.get("N") and f.get("N"):
            idx_nom.setdefault(normaliser(o["N"]), (o["N"], f["N"]))
        if o.get("D") and f.get("D"):
            idx_desc.setdefault(normaliser(o["D"]), (o["D"], f["D"]))
        if o.get("T") and f.get("T"):
            idx_tt.setdefault(normaliser(o["T"]), (o["T"], f["T"]))

    traductions = charger(os.path.join(BASE, "traductions", "sorts.json")) \
        if os.path.exists(os.path.join(BASE, "traductions", "sorts.json")) else {}

    # APPARIEMENTS INTERDITS (bloc 4, 28/07/2026). Le banc au moteur a prouvé
    # que certains D « officiels » ne traduisent PAS le DE du client (le frFR
    # Blizzard du même ID référence d'autres variables, ou la jointure par
    # texte s'est trompée) : purger_faux_hors_cache.py les consigne ici, et
    # ce générateur cesse de les re-poser à chaque régénération. Le DE
    # revient alors en file de traduction — la voie du lot 13.
    chemin_interdits = os.path.join(BASE, "traductions",
                                    "appariements_officiels_interdits.json")
    interdits = charger(chemin_interdits) \
        if os.path.exists(chemin_interdits) else {}
    ids_interdits = {k[3:] for k in interdits if k.startswith("id:")}
    textes_interdits = {k[6:] for k in interdits if k.startswith("texte:")}
    if interdits:
        print("  appariements interdits consultés : %d id(s), %d texte(s)"
              % (len(ids_interdits), len(textes_interdits)))

    db = {}
    a_traduire = {}
    stats = {"officiel_id": 0, "reutilise": 0, "chiffres": 0,
             "ia": 0, "manquant": 0}

    def resoudre(texte_en, index, cache_champ):
        """Retourne (français, origine) ou (None, None)."""
        if not texte_en:
            return None, None
        if texte_en in textes_interdits:
            return None, None          # jointure prouvée fausse au banc
        # Traduction déjà faite (Google/IA)
        if texte_en in cache_champ:
            return cache_champ[texte_en], "ia"
        cle = normaliser(texte_en)
        paire = index.get(cle)
        if not paire:
            return None, None
        off_en, off_fr = paire
        if off_en == texte_en:
            return off_fr, "reutilise"
        rapporte = reporter_chiffres(texte_en, off_en, off_fr)
        if rapporte:
            return rapporte, "chiffres"
        return None, None

    cache_noms = traductions.get("noms", {})
    cache_descs = traductions.get("descriptions", {})

    for sid in cibles:
        a = asc.get(sid)
        if not a:
            continue
        o, f = en.get(sid), fr.get(sid)
        # a. Sort de base intact : traduction officielle par ID
        if (o and f and a.get("N") == o.get("N")
                and a.get("D", "") == o.get("D", "")):
            entree = {"N": f.get("N", "")}
            if f.get("R"):
                entree["R"] = f["R"]
            if sid in ids_interdits and a.get("D"):
                # Appariement par ID prouvé faux au banc (le frFR Blizzard de
                # cet ID ne traduit pas le D du client) : le NOM reste, la
                # description repart en traduction.
                a_traduire[sid] = {"D": a["D"], "_id": sid}
                stats["manquant"] += 1
                f = dict(f)
                f.pop("D", None)
            if f.get("D"):
                entree["D"] = f["D"]
                # Modèle anglais : sert à retrouver les valeurs que le client
                # a substituées ($s1 -> 15) dans l'info-bulle affichée.
                # TOUJOURS embarqué, même sans variable : l'addon ne traduit
                # une ligne que si elle EST ce modèle — sans lui, il
                # remplaçait n'importe quelle ligne longue par le français
                # (vécu : hache aux enchantements multiples).
                if a.get("D"):
                    entree["DE"] = a["D"]
            if f.get("T"):
                entree["T"] = f["T"]
                if a.get("T") and VARIABLE.search(a["T"]):
                    entree["TE"] = a["T"]
            db[sid] = entree
            stats["officiel_id"] += 1
            continue

        entree = {}
        reste = {}
        nom_fr, origine = resoudre(a.get("N"), idx_nom, cache_noms)
        if nom_fr:
            # Les traductions automatiques recopient la casse anglaise :
            # on rétablit la casse Blizzard française.
            if origine == "ia":
                nom_fr = corriger_capitalisation(a.get("N"), nom_fr)
            entree["N"] = nom_fr
            stats[origine if origine != "reutilise" else "reutilise"] += 1
        elif a.get("N"):
            reste["N"] = a["N"]

        desc_fr, origine_d = resoudre(a.get("D"), idx_desc, cache_descs)
        if desc_fr:
            entree["D"] = desc_fr
            entree["DE"] = a["D"]
        elif a.get("D"):
            reste["D"] = a["D"]

        tt_fr, _ = resoudre(a.get("T"), idx_tt, cache_descs)
        if tt_fr:
            entree["T"] = tt_fr
            if VARIABLE.search(a.get("T", "")):
                entree["TE"] = a["T"]

        # Le rang (« Rank 3 ») se traduit mécaniquement
        if a.get("R"):
            m = re.match(r"^Rank (\d+)$", a["R"])
            entree["R"] = ("Rang %s" % m.group(1)) if m else a["R"]

        if entree.get("N"):
            db[sid] = entree
        if reste:
            reste["_id"] = sid
            a_traduire[sid] = reste
            stats["manquant"] += 1

    # Sorts récoltés en jeu (info-bulles survolées absentes des DBC ciblés) :
    # ils complètent la base sans écraser une traduction déjà établie.
    recoltes = charger(os.path.join(BASE, "traductions", "sorts_recoltes.json")) \
        if os.path.exists(os.path.join(BASE, "traductions",
                                       "sorts_recoltes.json")) else {}
    ajouts = 0
    for sid, e in recoltes.items():
        if not str(sid).isdigit() or not isinstance(e, dict):
            continue
        if sid in db or not e.get("N"):
            continue
        entree = {"N": e["N"]}
        if e.get("D"):
            entree["D"] = e["D"]
            a = asc.get(sid)
            if a and a.get("D"):
                entree["DE"] = a["D"]
        db[sid] = entree
        ajouts += 1
    if ajouts:
        print("  + %d sorts récoltés en jeu" % ajouts)

    # Écriture
    os.makedirs(os.path.join(BASE, "a_traduire"), exist_ok=True)
    with open(os.path.join(BASE, "a_traduire", "sorts.json"), "w",
              encoding="utf-8") as f:
        json.dump(a_traduire, f, ensure_ascii=False, indent=1, sort_keys=True)

    # Textes uniques restants (c'est ce que le compagnon traduira)
    noms_u = {v["N"] for v in a_traduire.values() if v.get("N")}
    descs_u = {v["D"] for v in a_traduire.values() if v.get("D")}
    with open(os.path.join(BASE, "a_traduire", "sorts_textes.json"), "w",
              encoding="utf-8") as f:
        json.dump({"noms": sorted(noms_u), "descriptions": sorted(descs_u)},
                  f, ensure_ascii=False, indent=1)

    print("Sorts joueur ciblés          : %6d" % len(cibles))
    print("  traduits (base officielle) : %6d" % stats["officiel_id"])
    print("  noms réutilisés de l'officiel : %4d" % stats["reutilise"])
    print("  reportés aux chiffres près : %6d" % stats["chiffres"])
    print("  déjà traduits (Google/IA)  : %6d" % stats["ia"])
    print("  incomplets -> à traduire   : %6d" % stats["manquant"])
    print()
    print("BASE GENEREE : %d sorts" % len(db))
    print("À traduire : %d noms uniques, %d descriptions uniques (%.0f Ko)"
          % (len(noms_u), len(descs_u),
             (sum(map(len, noms_u)) + sum(map(len, descs_u))) / 1024))

    # LA VIGIE DES DIVERGENCES STRUCTURELLES DORMANTES (bloc D du
    # programme 3, 29/07/2026). 5 426 paires du cache ont une structure de
    # variables qui diverge de leur clé anglaise, mais AUCUNE base ne les
    # consomme : sans conséquence à l'écran aujourd'hui. On n'y touche pas
    # — et on refuse de les oublier. Le compte est recalculé à CHAQUE
    # génération : le jour où le serveur en réveille une, elle passe de
    # « dormante » à « servie » et le chiffre bouge tout seul. Le rapport
    # dit combien et lesquelles ; c'est vivant, pas un fichier mort.
    try:
        from noms_empoisonnes import structure_divergente
        servies_de = {e.get("DE") for e in db.values() if e.get("DE")}
        dormantes, servies = [], 0
        for cle, valeur in cache_descs.items():
            if not isinstance(valeur, str) or not valeur.strip():
                continue
            raison = structure_divergente(cle, valeur)
            if not raison:
                continue
            if cle in servies_de:
                servies += 1
            else:
                dormantes.append({"en": cle[:400], "raison": raison})
        print("VIGIE STRUCTURE : %d divergence(s) DORMANTE(S) (aucune base "
              "ne les consomme) + %d servies — rapports/"
              "structures_dormantes.json" % (len(dormantes), servies))
        chemin = os.path.join(BASE, "rapports", "structures_dormantes.json")
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump({"mesure": "à chaque génération",
                       "dormantes": len(dormantes), "servies": servies,
                       "detail": dormantes}, f, ensure_ascii=False, indent=1)
    except Exception as e:                      # jamais bloquant
        print("  (vigie structure indisponible : %s)" % e)
    return db


if __name__ == "__main__":
    db = main()
    # Écriture du fichier Lua de l'addon
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import generateur_db
    n, taille = generateur_db.ecrire_db("DB_Sorts.lua", "Sorts", db, True)
    print("DB_Sorts.lua : %d entrées, %.1f Ko" % (n, taille / 1024.0))
    # Si la base a saturé la limite de constantes de Lua 5.1, ecrire_db n'a
    # RIEN écrit (l'ancien fichier reste en place) : il faut que la chaîne
    # s'arrête ici plutôt que d'annoncer une réussite.
    if generateur_db.SATURATIONS:
        raise SystemExit(1)
