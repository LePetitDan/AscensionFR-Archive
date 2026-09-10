# -*- coding: utf-8 -*-
r"""Purge les noms d'objets FAUX, jugés ENTRÉE PAR ENTRÉE (bloc C du
programme 4, 29/07/2026).

LA RÈGLE, et pourquoi elle juge une entrée et non une famille : les
familles sont MIXTES — « Dard » est le bon français de « Dart » ET de
« Stinger », et le mauvais d'une carte de compétence. Une règle par
famille détruirait les légitimes. On se sert donc du moulin lui-même
(traductions/objets_dbc.json, {anglais -> français}) :

  - si le moulin traduit l'anglais de CETTE entrée autrement que le nom
    posé, l'entrée porte le nom d'un autre objet ;
  - si le moulin ne connaît pas son anglais mais que le français posé est,
    chez lui, la traduction d'un anglais DIFFÉRENT, même conclusion.

LE FILTRE QUI A MANQUÉ AU PREMIER JET, et il compte : quand l'anglais est
un BOUCHE-TROU (« [MISSING ITEM NAME] », « Z:DBCtoDB Generated Item », un
nom d'asset), le moulin n'en dit rien d'utile et le français posé vient
d'ailleurs — le purger remplacerait un vrai nom par un bouche-trou à
l'écran. Ces entrées sont ÉCARTÉES. Sans ce filtre, l'échantillon de 30
donnait 7 traductions légitimes détruites ; avec lui, 0.

PÉRIMÈTRE : par défaut, les seules familles sous le seuil de la vigie
(2 à 4 porteurs) — celles que la vigie ne voit jamais. `--tout` élargit à
la base entière (27 000 entrées : à ne PAS lancer sans arbitrage).

Usage : python outils/purger_objets_par_entree.py [--appliquer] [--tout]
"""
import io
import json
import os
import random
import re
import shutil
import sys
import time
import unicodedata

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from noms_empoisonnes import objets_suspects, SEUIL_PORTEURS  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DBDIR = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface"
         r"\AddOns\AscensionFR\DB")
OBJETS = os.path.join(BASE, "traductions", "objets.json")
MOULIN = os.path.join(BASE, "traductions", "objets_dbc.json")
INTERDITS = os.path.join(BASE, "traductions", "objets_interdits.json")
RAPPORT = os.path.join(BASE, "rapports", "objets_par_entree_blocC.txt")
JOURNAL = os.path.join(BASE, "rapports", "purges_objets")


def restaurer(chemin_journal):
    """DÉFAIT une purge, à partir de son journal nominatif.

    Remettre le nom dans objets.json ne suffirait PAS : la barrière du
    programme 2 refuse la ré-adoption au point d'écriture. Le retour doit
    donc lever les deux, sinon la génération suivante reprendrait le nom.
    """
    with io.open(chemin_journal, encoding="utf-8") as f:
        journal = json.load(f)
    entrees = journal["entrees"]
    print("journal   : %s" % chemin_journal)
    print("purge du  : %s (%s)" % (journal["horodatage"], journal["perimetre"]))
    print("entrées   : %d" % len(entrees))

    objets = charger(OBJETS)
    rendus = 0
    for e in entrees:
        if not e.get("depuis_objets"):
            continue                  # ce nom ne venait PAS d'ici
        entree = objets.setdefault(e["id"], {})
        if entree.get("N") != e["fr_retire"]:
            entree["N"] = e["fr_retire"]
            rendus += 1
    from ecriture_sure import ecrire_json
    ecrire_json(OBJETS, objets)

    interdits = charger(INTERDITS)
    leves = 0
    for e in entrees:
        if not e.get("interdit_pose"):
            continue                  # interdiction antérieure : on n'y touche pas
        liste = interdits.get(str(e["id"]))
        if liste and e["fr_retire"] in liste:
            liste.remove(e["fr_retire"])
            leves += 1
            if not liste:
                del interdits[str(e["id"])]
    ecrire_json(INTERDITS, interdits)

    print("\n>>> objets.json : %d nom(s) remis" % rendus)
    print(">>> objets_interdits.json : %d interdiction(s) levée(s)" % leves)
    print("\nIl reste à REGÉNÉRER pour que l'addon les revoie :")
    print("    python outils/mise_a_jour.py")
    return 0

# Anglais dont le moulin ne peut rien dire : on n'y touche jamais.
# Les quatre dernières formes ont été ajoutées au programme 5 : l'examen des
# 100 a montré des noms d'ATELIER (« Art Template … », « RPGITEM PH - … »,
# « Weapon - Hand_1h_DraenorQuest95_B_01 ») que la liste ne reconnaissait pas.
RE_TECHNIQUE = re.compile(
    r"^\s*$|MISSING ITEM NAME|DBCtoDB|^Z:|placeholder|^PH\b|UNUSED|"
    r"^\[.*\]$|TEST|Monster - |OLD |\(old\)|deprecated|"
    r"^[a-z0-9_]{12,}$|bulkmake|"
    r"Art Template|RPGITEM|\bPH\b|[A-Za-z]+_[A-Za-z0-9]+_[A-Za-z0-9]+",
    re.I)

# --- L'AFFINAGE DU PROGRAMME 5 : le mot commun DISTINCTIF -----------------
# Sur 100 entrées jugées une par une, une seule légitime était détruite :
#     [2069525] Vineyard Skulkers
#         posé   : Rôdeuses du vignoble     <- bon français
#         moulin : Skulkers du vignoble     <- laisse un mot anglais
# Son trait, une fois vu, est net : ce n'est PAS un objet qui porte le nom
# d'un AUTRE objet, c'est le MÊME objet traduit deux fois, et la version
# posée est la meilleure. Les deux noms se ressemblent — alors que dans les
# 99 autres cas, le posé et le moulin n'ont rien en commun.
#
# Mais « se ressemblent » se mesure mal avec un mot commun quelconque :
# « Gants de voyou » et « Gants de sanctification » partagent « gants » et
# ne sont pas le même objet. Il faut un mot commun ET DISTINCTIF — et la
# distinctivité ne se décrète pas, elle se COMPTE : un mot présent dans des
# milliers de noms est générique, un mot présent dans dix ne l'est pas.
# Seuil calibré en regardant les bandes marginales (rapport du bloc B) :
# au-delà de 500, on épargne de vraies erreurs sur un seul mot générique
# (« High Warlord's Spear » -> « Lance lourde », épargné par « lance »).
SEUIL_DISTINCTIF = 500
MOTS_VIDES = {"de", "du", "des", "la", "le", "les", "aux", "and", "the",
              "of", "en", "pour", "sur", "avec"}


def mots(texte):
    return {m for m in re.split(r"[^0-9a-z']+", plat(texte))
            if len(m) > 2 and m not in MOTS_VIDES}


def frequences(noms):
    """Combien de noms contiennent chaque mot. C'est la mesure de la
    généricité — comptée sur les données, pas décidée."""
    compte = {}
    for n in noms:
        for m in mots(n):
            compte[m] = compte.get(m, 0) + 1
    return compte


def meme_objet(a, b, freq):
    """Vrai si les deux noms partagent un mot DISTINCTIF : ils désignent
    alors le même objet, et l'écart n'est qu'une variante de traduction.
    ⚠️ « freq » doit être comptée dans la MÊME langue que a et b — comparer
    deux noms anglais avec les fréquences des noms français fait passer
    « bracers » ou « gloves » pour distinctifs (vu sur la bande à 50)."""
    return any(freq.get(m, 0) <= SEUIL_DISTINCTIF for m in (mots(a) & mots(b)))


def charger(chemin):
    if not os.path.exists(chemin):
        return {}
    with io.open(chemin, encoding="utf-8") as f:
        return json.load(f)


def plat(t):
    t = unicodedata.normalize("NFKD", t or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    return " ".join(t.lower().split())


def objets_livres():
    brut = io.open(os.path.join(DBDIR, "DB_Objets.lua"), encoding="utf-8",
                   errors="replace").read()
    rendu = {}
    for m in re.finditer(r"[\[,]\[(\d+)\]=(\{(?:[^{}]|\{[^{}]*\})*\})", brut):
        n = re.search(r'(?:^|[{,])N="((?:\\.|[^"\\])*)"', m.group(2))
        if n:
            rendu[m.group(1)] = (n.group(1).replace('\\"', '"')
                                 .replace("\\\\", "\\"))
    return rendu


def noms_anglais():
    anglais = {}
    for iid, f in charger(os.path.join(BASE, "sources", "dbc",
                                       "itemaddon_par_id.json")).items():
        if isinstance(f, dict) and f.get("N"):
            anglais[iid] = f["N"]
    dossier = os.path.join(BASE, "extraits")
    if os.path.isdir(dossier):
        for royaume in sorted(os.listdir(dossier)):
            chemin = os.path.join(dossier, royaume, "objets.json")
            if os.path.isfile(chemin):
                for iid, o in charger(chemin).items():
                    if o.get("Name"):
                        anglais.setdefault(iid, o["Name"])
    return anglais


def main():
    if "--restaurer" in sys.argv:
        return restaurer(sys.argv[sys.argv.index("--restaurer") + 1])
    appliquer = "--appliquer" in sys.argv
    tout = "--tout" in sys.argv
    lignes = []

    def dire(t=""):
        print(t)
        lignes.append(t)

    dire("PURGE DES NOMS D'OBJETS, ENTRÉE PAR ENTRÉE — %s (%s%s)"
         % (time.strftime("%d/%m/%Y %H:%M"),
            "APPLICATION" if appliquer else "simulation",
            ", BASE ENTIÈRE" if tout else ", sous le seuil de la vigie"))
    dire("=" * 68)

    livres = objets_livres()
    anglais = noms_anglais()
    moulin = charger(MOULIN).get("noms", {})
    inverse = {}
    for en, fr in moulin.items():
        inverse.setdefault(plat(fr), set()).add(plat(en))
    dire("objets livrés : %d | anglais connus : %d | moulin : %d"
         % (len(livres), len(anglais), len(moulin)))

    if tout:
        perimetre = set(livres)
    else:
        objets_v = {i: {"N": n} for i, n in livres.items()}
        grosses = objets_suspects(objets_v, anglais, seuil=SEUIL_PORTEURS)
        petites = {v: ids for v, ids
                   in objets_suspects(objets_v, anglais, seuil=2).items()
                   if v not in grosses}
        perimetre = {i for ids in petites.values() for i in ids}
        dire("périmètre : %d familles sous le seuil, %d entrées"
             % (len(petites), len(perimetre)))

    # Les deux tables de fréquences, une par langue (voir meme_objet).
    freq_fr = frequences(livres.values())
    freq_en = frequences(anglais.values())

    fausses, ecartees, epargnees = [], 0, []
    for iid in sorted(perimetre):
        fr = livres.get(iid)
        en = anglais.get(iid)
        if not fr or not en:
            continue
        if RE_TECHNIQUE.search(en):
            ecartees += 1
            continue
        attendu = moulin.get(en)
        if attendu is not None:
            if plat(attendu) == plat(fr):
                continue
            if meme_objet(fr, attendu, freq_fr):
                epargnees.append((iid, en, fr, attendu))
                continue
            fausses.append((iid, en, fr, attendu))
        else:
            sources = inverse.get(plat(fr))
            if not sources or plat(en) in sources:
                continue
            autre_en = sorted(sources)[0]
            if meme_objet(en, autre_en, freq_en):
                epargnees.append((iid, en, fr, "(EN : %s)" % autre_en[:40]))
                continue
            fausses.append((iid, en, fr, "(traduit : %s)" % autre_en[:40]))
    dire("")
    dire("FAUSSES (à purger)              : %d" % len(fausses))
    dire("écartées (anglais bouche-trou)  : %d" % ecartees)
    dire("ÉPARGNÉES par l'affinage        : %d (variante de traduction du "
         "MÊME objet)" % len(epargnees))

    # L'ÉCHANTILLON, imposé par Dan : on le REMONTRE à chaque passage, il ne
    # coûte rien et c'est la seule vérification qui ait jamais rattrapé une
    # signature de purge fausse (lot 9). Porté de 30 à 100 au programme 5 :
    # un seuil de 2/30 calibré pour 1 646 entrées ne protège plus à seize
    # fois l'échelle.
    taille = 100 if tout else 30
    rnd = random.Random(27271 if tout else 1646)
    dire("")
    dire("ÉCHANTILLON DE %d (à juger un par un) :" % taille)
    for k, (iid, en, fr, attendu) in enumerate(
            rnd.sample(fausses, min(taille, len(fausses))), 1):
        dire("%3d. [%s] EN=%s" % (k, iid, en[:56]))
        dire("         posé=%s | moulin=%s" % (fr[:46], str(attendu)[:46]))

    dire("")
    dire("ÉPARGNÉES — 12 au hasard, pour vérifier que l'affinage vise juste :")
    for iid, en, fr, attendu in rnd.sample(epargnees, min(12, len(epargnees))):
        dire("     [%s] EN=%s" % (iid, en[:52]))
        dire("           posé=%s | moulin=%s" % (fr[:44], str(attendu)[:44]))

    if not appliquer:
        dire("")
        dire("SIMULATION — rien n'a été écrit. --appliquer pour purger.")
        _ecrire(lignes, fausses)
        return 0

    # Un passage qui ne retire RIEN ne doit pas laisser de trace : sinon il
    # écrit un journal vide, et l'exploitant qui prendra « le plus récent »
    # pour défaire la purge obtiendra un retour qui ne rend rien. Un outil
    # sans effet doit se taire — même règle que « rien à faire » sort en 0.
    if not fausses:
        dire("")
        dire("rien à purger : la base est déjà au point fixe. "
             "Aucun journal écrit.")
        _ecrire(lignes, fausses)
        return 0

    horodatage = time.strftime("%Y%m%d-%H%M%S")
    objets = charger(OBJETS)
    shutil.copy2(OBJETS, OBJETS.replace(".json",
                                        "_avant_blocC_%s.json" % horodatage))
    # On note QUI a réellement bougé : sur 23 849 noms condamnés, seuls
    # ~19 500 vivent dans objets.json — les autres viennent de l'officiel,
    # de la récolte ou du moulin, et seule l'interdiction les arrête. Le
    # retour doit rendre exactement ce qu'il a pris, sinon il INVENTE des
    # entrées (vérifié par empreinte : le premier jet en ajoutait 4 298).
    retires = 0
    depuis_objets = set()
    for iid, _en, fr, _a in fausses:
        entree = objets.get(iid)
        if entree and entree.get("N") == fr:
            entree.pop("N", None)
            retires += 1
            depuis_objets.add(iid)
            if not entree:
                del objets[iid]
    from ecriture_sure import ecrire_json
    ecrire_json(OBJETS, objets)

    # La BARRIÈRE : le nom peut aussi venir de l'officiel, de la récolte ou
    # du moulin. On l'interdit par identifiant — la génération refuse au
    # point d'écriture (mécanique du programme 2, bloc B).
    interdits = charger(INTERDITS)
    ajouts = 0
    interdit_pose = set()
    for iid, _en, fr, _a in fausses:
        liste = interdits.setdefault(str(iid), [])
        if fr not in liste:
            liste.append(fr)
            ajouts += 1
            interdit_pose.add(iid)   # celle-ci est à NOUS : le retour la lève
    ecrire_json(INTERDITS, interdits)

    # LE CHEMIN DU RETOUR, écrit AVANT qu'on en ait besoin. Une sauvegarde
    # d'objets.json ne suffit pas : entre la purge et le regret, d'autres
    # passages ont pu écrire dans le fichier, et le restaurer en bloc les
    # effacerait. Le journal est NOMINATIF — il rend exactement ce qui a
    # été retiré, ligne à ligne, et rien d'autre.
    # …et un passage qui a bien VU des fausses mais n'a RIEN eu à retirer
    # (la purge précédente avait déjà tout fait, la base livrée n'étant pas
    # encore régénérée) ne doit pas écrire de journal non plus : il serait
    # complet en apparence, et incapable de rien rendre.
    if not depuis_objets and not interdit_pose:
        dire("")
        dire("aucun retrait effectif (déjà purgé) — aucun journal écrit. "
             "Le journal utile reste celui de la purge d'origine.")
        _ecrire(lignes, fausses)
        return 0

    os.makedirs(JOURNAL, exist_ok=True)
    chemin_journal = os.path.join(JOURNAL, "purge_%s.json" % horodatage)
    ecrire_json(chemin_journal, {
        "horodatage": horodatage,
        "perimetre": "base entière" if tout else "sous le seuil de la vigie",
        "sauvegarde_objets": os.path.basename(
            OBJETS.replace(".json", "_avant_blocC_%s.json" % horodatage)),
        "entrees": [{"id": iid, "en": en, "fr_retire": fr,
                     "raison": ("le moulin traduit cet anglais par « %s »"
                                % attendu) if not str(attendu).startswith("(")
                     else ("le français posé traduit un autre anglais %s"
                           % attendu),
                     "depuis_objets": iid in depuis_objets,
                     "interdit_pose": iid in interdit_pose}
                    for iid, en, fr, attendu in fausses],
    })
    dire("")
    dire("objets.json : %d N retirés (sauvegarde _avant_blocC_%s)"
         % (retires, horodatage))
    dire("objets_interdits.json : +%d paires (%d identifiants au total)"
         % (ajouts, len(interdits)))
    dire("journal nominatif : %s" % chemin_journal)
    dire("POUR TOUT DÉFAIRE :")
    dire("    python outils/purger_objets_par_entree.py --restaurer %s"
         % chemin_journal)
    _ecrire(lignes, fausses)
    return 0


def _ecrire(lignes, fausses):
    os.makedirs(os.path.dirname(RAPPORT), exist_ok=True)
    with io.open(RAPPORT, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lignes) + "\n\nDÉTAIL (%d)\n%s\n"
                % (len(fausses), "=" * 40))
        for iid, en, fr, attendu in fausses:
            f.write("[%s]\n  EN     : %s\n  posé   : %s\n  moulin : %s\n\n"
                    % (iid, en, fr, attendu))
    print("rapport :", RAPPORT)


if __name__ == "__main__":
    sys.exit(main())
