# -*- coding: utf-8 -*-
r"""
Générateur des bases de données Lua de l'addon AscensionFR.

Croise trois sources :
  1. extraits/rexxar/*.json      — contenu réellement servi par Ascension (WDB)
  2. sources/frFR/*.json          — traductions officielles Blizzard (TDB)
  3. sources/enUS/*.json          — textes anglais officiels (pour vérifier
                                    qu'Ascension n'a pas modifié le contenu)
  4. traductions/*.json           — traductions IA du contenu custom/modifié

Produit :
  - les fichiers DB\*.lua de l'addon
  - a_traduire/*.json : le contenu custom qui attend une traduction IA
  - un rapport de couverture

Usage : python generateur_db.py [--base <dossier traduction>]
"""
import argparse
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chemin_client import ADDON  # noqa: E402
import optimiser_memoire  # noqa: E402
import accents_majuscules  # noqa: E402
from diagnostic_gs import charger as charger_globalstrings  # noqa: E402

# ---------------------------------------------------------------------------
# LA LIMITE QUI A BLOQUÉ LA 3.4 (25/07/2026)
# ---------------------------------------------------------------------------
# Lua 5.1 — donc le client de WoW 3.3.5a — n'accepte que 262 143 constantes
# par PROTOTYPE de fonction (MAXARG_Bx ; lcode.c, addk -> « constant table
# overflow »). Une constante = une chaîne DISTINCTE ou un nombre DISTINCT :
# Lua dédoublonne, mais un identifiant d'objet reste un nombre distinct.
#
# Un « DB[21504]={N="…",D="…"} » coûte donc 1 nombre + 2 chaînes. À 355 320
# objets, les IDENTIFIANTS SEULS dépassent la limite : aucun réglage de texte
# ne peut sauver le format plat, il faut changer de forme (voir paresseux=).
#
# La taille du fichier ne dit RIEN : 26 Mo paresseux se compilent en 0,1 s,
# alors que le même contenu à plat ne se compile pas du tout. Et rien ne
# prévient avant le /reload — l'addon est simplement mort. D'où ce compteur.
LIMITE_CONSTANTES = 262143
SEUIL_ALERTE = 0.80
SATURATIONS = []


def charger(chemin):
    if os.path.exists(chemin):
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    return {}


def normaliser(texte):
    """Normalisation pour comparer enUS officiel et texte servi par Ascension."""
    if not texte:
        return ""
    t = texte.replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(r"\s+", " ", t)
    return t.strip().lower()


# ---------------------------------------------------------------------------
# HARMONISATION DU VOCABULAIRE OFFICIEL (arbitrage de Dan, 26/07/2026)
# ---------------------------------------------------------------------------
# Certaines chaînes ne transitent JAMAIS par traductions/*.json : elles
# viennent telles quelles du frFR officiel (Spell_frFR.dbc, locales du serveur,
# Achievement.dbc). `appliquer_vocabulaire.py` ne peut donc pas les atteindre,
# et chaque régénération ramène le vieux mot. On harmonise ici, au dernier
# moment, juste avant l'écriture.
#
# Cas vécu : les 8 « bassin d'Arathi » de DB_Sorts.lua (sorts 24409-24413)
# venaient de sources/dbc/spells_frFR.json, jamais de nos traductions. Le DBC
# du client écrit « bassin d'Arathi » (17 fois), la locale du serveur écrit
# « bassin Arathi » (274 fois) : le glossaire suit la seconde. La CASSE est
# conservée — l'addon livre déjà 185 « bassin Arathi » en minuscule contre 41
# en majuscule, et forcer la majuscule écrirait « dans le Bassin Arathi » au
# milieu d'une phrase.
#
# ⚠️ Ne JAMAIS mettre ici un motif qui pourrait correspondre à de l'ANGLAIS :
# les mêmes entrées portent les modèles anglais (NE, DE, TE, SE) qui servent
# à aligner les info-bulles. Par sécurité, harmoniser() n'est appelé que sur
# les champs de la liste blanche accents_majuscules.CHAMPS_FR.
#
# LES CODES D'AFFICHAGE SE COLLENT AU MOT. Une icône de haut fait donne
# « …|t|rBassin d'Arathi » : le « r » de « |r » et le « t » de « |t » sont des
# LETTRES, donc une frontière de mot ordinaire n'y voit RIEN et la règle rate
# EN SILENCE. Mesuré sur DB_Communaute.lua : 3 occurrences sur 30 échappaient
# ainsi, toutes des noms de haut fait précédés de leur icône. Même famille de
# piège que les 191 entrées ratées au lot 4 sur « |cFFB5FFFFStarcaller ».
# (Trois lookbehind séparés : chacun est de largeur fixe, ce qu'exige Python.)
DEBUT_MOT = (r"(?:(?<=\|[rt])|(?<=\|c[0-9A-Fa-f]{8})"
             r"|(?<![0-9A-Za-zÀ-ÿ]))")
FIN_MOT = r"(?![0-9A-Za-zÀ-ÿ])"

HARMONISATIONS = [
    (re.compile(DEBUT_MOT + r"Bassin\s+d'Arathi" + FIN_MOT), "Bassin Arathi"),
    (re.compile(DEBUT_MOT + r"bassin\s+d'Arathi" + FIN_MOT), "bassin Arathi"),
]


def harmoniser(texte):
    """Passe le vocabulaire arbitré sur une chaîne FRANÇAISE."""
    if not texte:
        return texte
    for motif, vers in HARMONISATIONS:
        texte = motif.sub(vers, texte)
    return texte


def polir(valeur, champ=None, anglais=None):
    """Vocabulaire arbitré + règle d'accent, juste avant l'écriture.

    `champ` vaut None pour les bases à valeur simple (DB_Interface,
    DB_Libelles…), sinon le nom du champ : on ne touche alors qu'aux champs
    FRANÇAIS, jamais aux modèles anglais NE/DE/TE/SE.

    Depuis le bloc 2b (28/07/2026), la règle d'accent couvre aussi les noms
    CITÉS dans les textes (« Vous apprend Eclair de givre » → « … Éclair de
    givre ») : le gros des citations fautives vient de la couche OFFICIELLE,
    qui n'accentue pas ses majuscules — seule une règle posée ICI, à
    l'entonnoir de toutes les couches, les rattrape durablement.
    """
    if champ is not None and champ not in accents_majuscules.CHAMPS_FR:
        return valeur
    valeur = accents_majuscules.corriger_tete(valeur, anglais=anglais)
    valeur = accents_majuscules.corriger_citations(valeur)
    return harmoniser(valeur)


def echapper_lua(texte):
    """Échappe un texte pour l'écrire dans une chaîne Lua.

    Les fins de ligne sont préservées telles quelles : les DBC écrivent
    « \\r\\n », et écraser le « \\r » faisait diverger le modèle anglais du
    texte réellement affiché par le jeu — l'addon n'arrivait plus à les
    aligner et laissait les descriptions de sorts en anglais.
    """
    t = texte.replace("\\", "\\\\").replace('"', '\\"')
    t = t.replace("\r", "\\r").replace("\n", "\\n")
    return t


def ecrire_db(nom_fichier, nom_table, entrees, cle_numerique, chemin=None,
              paresseux=False):
    """Écrit un fichier DB Lua. entrees : dict clé -> dict de champs ou str.

    paresseux=True : format à SEAUX (outils/optimiser_memoire.py) au lieu du
    format plat. Un seau entier devient UNE chaîne longue, donc 2 constantes
    au lieu de plusieurs milliers : c'est le seul format qui tienne pour les
    très grosses bases. Réservé aux clés numériques — AFR.Paresseux range par
    « identifiant // 512 ». Le fichier plat n'est alors JAMAIS écrit : plus de
    fenêtre pendant laquelle l'addon serait cassé si la chaîne s'interrompt.
    """
    if paresseux and not cle_numerique:
        raise ValueError("%s : le format paresseux exige des clés numériques"
                         % nom_fichier)
    chemin = chemin or os.path.join(ADDON, "DB", nom_fichier)

    corps_par_cle = []
    nombres, chaines = set(), set()   # les futures constantes du chunk
    for cle in sorted(entrees, key=(int if cle_numerique else str)):
        valeur = entrees[cle]
        if isinstance(valeur, str):
            # polir() AVANT chaines.add() : le comptage des constantes Lua 5.1
            # doit porter sur le texte réellement écrit.
            valeur = polir(valeur)
            chaines.add(valeur)
            corps = '"%s"' % echapper_lua(valeur)
        else:
            champs = []
            for k in sorted(valeur):
                v = valeur[k]
                if v is None or v == "":
                    continue
                chaines.add(k)          # le nom de champ est une constante
                # Le modèle ANGLAIS de ce champ, quand il existe : il dit si
                # la valeur a vraiment été traduite (N contre NE, D contre DE).
                en = valeur.get(k + "E") if isinstance(valeur, dict) else None
                if isinstance(v, list):
                    v = [polir(x, k) if isinstance(x, str) else x for x in v]
                    chaines.update(str(x) for x in v)
                    elems = ",".join('"%s"' % echapper_lua(x) for x in v)
                    champs.append("%s={%s}" % (k, elems))
                else:
                    v = polir(str(v), k, en)
                    chaines.add(v)
                    champs.append('%s="%s"' % (k, echapper_lua(v)))
            if not champs:
                continue
            corps = "{%s}" % ",".join(champs)
        if cle_numerique:
            nombres.add(int(cle))
        else:
            chaines.add(cle)
        corps_par_cle.append((cle, corps))

    if paresseux:
        contenu = optimiser_memoire.enseauter(
            corps_par_cle, "AscensionFR.DB.%s" % nom_table)
        # un seau = une chaîne longue + son numéro de seau
        constantes = 2 * optimiser_memoire.nb_seaux(
            cle for cle, _ in corps_par_cle)
    else:
        lignes = [
            "-- Fichier généré automatiquement par generateur_db.py"
            " - NE PAS ÉDITER.",
            "local DB = AscensionFR.DB.%s" % nom_table,
        ]
        for cle, corps in corps_par_cle:
            if cle_numerique:
                lignes.append("DB[%d]=%s" % (int(cle), corps))
            else:
                lignes.append('DB["%s"]=%s' % (echapper_lua(cle), corps))
        contenu = "\n".join(lignes) + "\n"
        constantes = len(nombres) + len(chaines)

    if constantes >= LIMITE_CONSTANTES:
        # On n'écrit RIEN : le fichier déjà en place, lui, se charge encore.
        # Mieux vaut une base d'hier qu'un addon mort au prochain /reload.
        SATURATIONS.append((nom_fichier, constantes, len(corps_par_cle)))
        print("  !! %s NON ÉCRIT : %d constantes pour %d entrées, la limite"
              " de Lua 5.1 est %d." % (nom_fichier, constantes,
                                       len(corps_par_cle), LIMITE_CONSTANTES))
        print("     L'ancien fichier est conservé. Cette base doit passer au"
              " format paresseux (ecrire_db(..., paresseux=True)).")
        return len(entrees), 0

    if constantes >= SEUIL_ALERTE * LIMITE_CONSTANTES:
        print("  ! %s : %d constantes, soit %.0f %% de la limite Lua 5.1"
              " (%d). À basculer en paresseux avant qu'elle ne casse."
              % (nom_fichier, constantes,
                 100.0 * constantes / LIMITE_CONSTANTES, LIMITE_CONSTANTES))

    if paresseux:
        optimiser_memoire.ecrire(chemin, contenu)
    else:
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(contenu)
    return len(entrees), len(contenu)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=BASE)
    args = parser.parse_args()
    base = args.base

    # En surveillance (traducteur_fr --auto), main() est rappelé à chaque
    # cycle DANS LE MÊME PROCESSUS : sans cette remise à zéro, la saturation
    # d'un cycle resterait collée à tous les suivants et ferait échouer des
    # générations parfaitement saines.
    del SATURATIONS[:]

    def ex(n):
        # Extrait local (parse_dir) SUPERPOSÉ aux caches envoyés par les
        # joueurs (rapports/caches/fusion, versés par outils/ingerer_caches).
        # Priorité au local : ce que cette machine a vu l'emporte, ce que les
        # joueurs ont vu complète. Surtout ne pas écrire dans extraits/ :
        # parse_dir le réécrit à chaque cycle.
        #
        # TOUS LES ROYAUMES : les autres royaumes que Rexxar (Vol'jin, Darkmoon
        # Wildcard, Dawnrise…) sont des caches serveur vus par cette machine, au
        # même titre que Rexxar. On les verse en base (priorité la plus basse) :
        # ils n'AJOUTENT que des IDs nouveaux, fusion joueurs et Rexxar restent
        # prioritaires -> comportement strictement inchangé pour les IDs connus.
        donnees = {}
        dossier_ex = os.path.join(base, "extraits")
        if os.path.isdir(dossier_ex):
            for royaume in sorted(os.listdir(dossier_ex)):
                if royaume == "rexxar":
                    continue
                if not os.path.isdir(os.path.join(dossier_ex, royaume)):
                    continue
                donnees.update(charger(os.path.join(dossier_ex, royaume, n)))
        donnees.update(charger(os.path.join(base, "rapports", "caches",
                                            "fusion", n)))
        donnees.update(charger(os.path.join(base, "extraits", "rexxar", n)))
        return donnees
    fr = lambda n: charger(os.path.join(base, "sources", "frFR", n))
    en = lambda n: charger(os.path.join(base, "sources", "enUS", n))
    tr = lambda n: charger(os.path.join(base, "traductions", n))

    dossier_at = os.path.join(base, "a_traduire")
    os.makedirs(dossier_at, exist_ok=True)
    os.makedirs(os.path.join(base, "traductions"), exist_ok=True)

    rapport = []
    a_traduire = {}

    # ------------------------------------------------------------------
    # QUÊTES
    # ------------------------------------------------------------------
    wdb_q = ex("quetes.json")
    fr_q = fr("quest_template_locale.json")
    fr_qr = fr("quest_offer_reward_locale.json")
    fr_qp = fr("quest_request_items_locale.json")
    en_q = en("quest_template.json")
    tr_q = tr("quetes.json")

    quetes = {}
    at_quetes = {}
    stats_q = {"officiel": 0, "ia": 0, "modifie": 0, "custom": 0}

    # 1. Toutes les quêtes de base officielles (préchargement complet)
    for qid, loc in fr_q.items():
        e = en_q.get(qid, {})
        entree = {"TE": e.get("Title") or e.get("LogTitle")}
        if loc.get("Title"):
            entree["T"] = loc["Title"]
        if loc.get("Objectives"):
            entree["O"] = loc["Objectives"]
        if loc.get("Details"):
            entree["D"] = loc["Details"]
        if loc.get("EndText"):
            entree["F"] = loc["EndText"]
        if loc.get("CompletedText"):
            entree["A"] = loc["CompletedText"]
        ots = [loc.get("ObjectiveText%d" % i, "") for i in range(1, 5)]
        if any(ots):
            entree["OT"] = ots
        if qid in fr_qp and fr_qp[qid].get("CompletionText"):
            entree["P"] = fr_qp[qid]["CompletionText"]
        if qid in fr_qr and fr_qr[qid].get("RewardText"):
            entree["R"] = fr_qr[qid]["RewardText"]
        if entree.get("T"):
            quetes[qid] = entree
            stats_q["officiel"] += 1

    # 2. Quêtes servies par Ascension : détection des modifications
    for qid, w in wdb_q.items():
        officiel_en = en_q.get(qid)
        identique = (
            officiel_en
            and normaliser(w.get("Title")) == normaliser(
                officiel_en.get("Title") or officiel_en.get("LogTitle"))
            and normaliser(w.get("Details")) == normaliser(
                officiel_en.get("Details") or officiel_en.get("QuestDescription"))
            and normaliser(w.get("Objectives")) == normaliser(
                officiel_en.get("Objectives") or officiel_en.get("LogDescription"))
        )
        if identique and qid in quetes:
            continue  # déjà couvert par l'officiel
        # Custom ou modifié : traduction IA disponible ?
        if qid in tr_q:
            entree = dict(tr_q[qid])
            entree["TE"] = w.get("Title")
            quetes[qid] = entree
            stats_q["ia"] += 1
        else:
            at = dict(w)
            if officiel_en:
                at["_officiel_frFR"] = fr_q.get(qid, {})
                stats_q["modifie"] += 1
            else:
                stats_q["custom"] += 1
            at_quetes[qid] = at
            quetes.pop(qid, None)  # ne pas afficher un FR officiel erroné

    # 3. Complément : textes de progression/rendu traduits par IA pour des
    #    quêtes déjà couvertes par l'officiel (locales TDB parfois lacunaires)
    for qid, t in tr_q.items():
        if qid in quetes:
            for champ in ("P", "R"):
                if t.get(champ) and not quetes[qid].get(champ):
                    quetes[qid][champ] = t[champ]

    a_traduire["quetes.json"] = at_quetes
    n, taille = ecrire_db("DB_Quetes.lua", "Quetes", quetes, True)
    rapport.append(("Quêtes", n, taille, stats_q))

    # ------------------------------------------------------------------
    # OBJETS
    # ------------------------------------------------------------------
    wdb_i = ex("objets.json")
    fr_i = fr("item_template_locale.json")
    en_i = en("item_template.json")
    tr_i = tr("objets.json")

    objets = {}
    at_objets = {}
    stats_i = {"officiel": 0, "ia": 0, "custom": 0}
    for iid, loc in fr_i.items():
        if loc.get("Name"):
            entree = {"N": loc["Name"]}
            if loc.get("Description"):
                entree["D"] = loc["Description"]
            objets[iid] = entree
            stats_i["officiel"] += 1
    for iid, w in wdb_i.items():
        officiel_en = en_i.get(iid)
        identique = officiel_en and normaliser(w.get("Name")) == normaliser(
            officiel_en.get("name"))
        if identique and iid in objets:
            continue
        if iid in tr_i:
            objets[iid] = dict(tr_i[iid])
            stats_i["ia"] += 1
        else:
            at_objets[iid] = w
            stats_i["custom"] += 1
            objets.pop(iid, None)
    a_traduire["objets.json"] = at_objets
    # Objets traduits À L'AVANCE, que personne n'a encore rencontrés. La
    # boucle ci-dessus ne parcourt que le cache client, donc uniquement le
    # DÉJÀ-VU : sans ce rattrapage, une traduction déposée dans le gisement
    # pour un objet jamais croisé n'entrerait jamais dans la base. On n'écrase
    # rien : le français officiel, posé en premier, reste prioritaire.
    for iid, entree in tr_i.items():
        if iid not in objets:
            objets[iid] = dict(entree)
            stats_i["ia"] += 1
    # ITEMADDON (22/07, go de Dan) : la table des objets d'ASCENSION
    # (id = id d'objet), traduite par le moulin (traductions/
    # objets_dbc.json). Elle COMPLÈTE sans jamais écraser : officiel et
    # récolte gardent la priorité. On ne pose que ce qui est traduit.
    ia_chemin = os.path.join(base, "sources", "dbc",
                             "itemaddon_par_id.json")
    ia_cache = os.path.join(base, "traductions", "objets_dbc.json")
    if os.path.exists(ia_chemin) and os.path.exists(ia_cache):
        par_id = charger(ia_chemin)
        moulin = charger(ia_cache)
        m_noms = moulin.get("noms", {})
        m_descs = moulin.get("descriptions", {})
        stats_i["itemaddon"] = 0
        for iid, entree_ia in par_id.items():
            if iid in objets:
                continue
            nom_fr = m_noms.get(entree_ia.get("N"))
            if not nom_fr:
                continue
            entree = {"N": nom_fr}
            desc_fr = m_descs.get(entree_ia.get("D"))
            if desc_fr:
                entree["D"] = desc_fr
            objets[iid] = entree
            stats_i["itemaddon"] += 1
    # Sorts attachés (lignes « Utiliser : ... ») : la liste vient du cache
    # client, l'addon s'en sert pour savoir quels modèles aligner sur les
    # lignes d'effet. Champ S = identifiants, en chaînes (ecrire_db
    # sérialise des listes de chaînes).
    for iid, w in wdb_i.items():
        sorts = w.get("Spells")
        if sorts and iid in objets:
            objets[iid]["S"] = [str(p[0]) for p in sorts]
    # ... et pour les objets SANS récolte, les sorts d'ItemAddon.dbc
    # (colonnes c40/c43/c47, outils/extraire_sorts_itemaddon.py) : sans S,
    # les lignes vertes restaient anglaises ET muettes au journal (vécu :
    # « Parchemin du gardien », test de Dan du 22/07).
    ia_sorts_chemin = os.path.join(base, "sources", "dbc",
                                   "itemaddon_sorts.json")
    if os.path.exists(ia_sorts_chemin):
        ia_sorts = charger(ia_sorts_chemin)
        for iid, sorts in ia_sorts.items():
            entree = objets.get(iid)
            if entree is not None and "S" not in entree:
                entree["S"] = [str(s) for s in sorts]
    # LE REFUS AU POINT D'ÉCRITURE (bloc B, 29/07/2026). La purge du bloc 7
    # a retiré les faux noms d'objets.json et du moulin — mais 305 entrées
    # tiennent leur N de l'OFFICIEL par ID ou de la RÉCOLTE, re-posé à
    # CHAQUE régénération : la purge seule ne fermait rien (la leçon du
    # bloc 8 des sorts). traductions/objets_interdits.json liste les
    # paires (identifiant -> valeurs) prouvées fausses ; on refuse ICI, en
    # balayage final, quelle que soit la source. Paire par paire : une
    # future traduction DIFFÉRENTE du même objet passe sans obstacle.
    interdits_i = charger(os.path.join(base, "traductions",
                                       "objets_interdits.json"))
    if interdits_i:
        import unicodedata

        def plat_i(t):
            t = unicodedata.normalize("NFKD", t or "")
            t = "".join(c for c in t if not unicodedata.combining(c))
            return " ".join(t.lower().split())

        # Aux accents/casse près, comme la purge : polir() repasse à
        # l'écriture et transformait une graphie voisine re-posée par une
        # autre source en la valeur interdite exacte (17 revenantes
        # mesurées avec la comparaison stricte).
        n_refus_i = 0
        for iid, valeurs in interdits_i.items():
            entree = objets.get(iid)
            if not entree or not entree.get("N"):
                continue
            if plat_i(entree["N"]) in {plat_i(v) for v in valeurs}:
                entree.pop("N", None)
                n_refus_i += 1
                if not entree:
                    del objets[iid]
        if n_refus_i:
            print("REFUS objets_interdits : %d nom(s) écarté(s) à la "
                  "génération (officiel/récolte re-posés)" % n_refus_i)

    # LA VIGIE DES NOMS D'OBJETS (lot 13, 28/07/2026) — elle COMPTE, elle
    # écrit son rapport, elle ne refuse RIEN. Même maladie que les sorts,
    # même mécanisme (jointure par identifiant sur des données d'époque),
    # mesurée au lot 11 : 636 valeurs suspectes. Le refus à l'adoption ne
    # sera posé qu'après que Dan aura vu la mesure — un garde-fou trop serré
    # qui refuse du bon travail se désactive au bout de trois jours.
    import noms_empoisonnes
    anglais_i = {}
    for iid, n in en_i.items():
        nom_en = n.get("N") if isinstance(n, dict) else n
        if nom_en:
            anglais_i[iid] = nom_en
    ia_par_id = charger(os.path.join(base, "sources", "dbc",
                                     "itemaddon_par_id.json"))
    for iid, e in ia_par_id.items():
        if iid not in anglais_i and isinstance(e, dict) and e.get("N"):
            anglais_i[iid] = e["N"]
    suspects_i = noms_empoisonnes.objets_suspects(objets, anglais_i)
    if suspects_i:
        n_susp = sum(len(v) for v in suspects_i.values())
        print("VIGIE OBJETS : %d valeur(s) posée(s) sur des identifiants aux "
              "noms anglais sans parenté (%d entrées) — détail : "
              "rapports/porteurs_objets.txt" % (len(suspects_i), n_susp))
        # LISTE COMPLÈTE machine-lisible (bloc 7, 28/07/2026) : la purge
        # consomme CE fichier — rejouer l'espace fusionné hors génération
        # dérivait (66 ids trouvés contre 3 794 ici). La génération est la
        # seule à posséder l'espace fidèle : c'est elle qui livre la mesure.
        with open(os.path.join(base, "rapports", "porteurs_objets.json"),
                  "w", encoding="utf-8") as f_j:
            json.dump({valeur: {"ids": ids,
                                "anglais": {i: anglais_i.get(i, "")
                                            for i in ids}}
                       for valeur, ids in suspects_i.items()},
                      f_j, ensure_ascii=False, indent=1, sort_keys=True)
        with open(os.path.join(base, "rapports", "porteurs_objets.txt"),
                  "w", encoding="utf-8") as f_v:
            f_v.write("Noms d'objets portés par des identifiants aux noms "
                      "anglais MULTIPLES et sans parenté.\nVigie seulement — "
                      "rien n'est retiré, l'arbitrage appartient à Dan "
                      "(lot 11 : 636 valeurs mesurées).\n\n")
            for val, ids in sorted(suspects_i.items(),
                                   key=lambda kv: -len(kv[1])):
                f_v.write("%5d ids  %s\n" % (len(ids), val))
                for i_ in ids[:3]:
                    f_v.write("           ex : [%s] EN=%s\n"
                              % (i_, anglais_i.get(i_, "?")))

    # PARESSEUX D'EMBLÉE (25/07/2026). Écrite à plat, cette base ne compile
    # plus : 355 320 identifiants distincts, à eux seuls, dépassent les
    # 262 143 constantes de Lua 5.1. Elle était rattrapée après coup par
    # outils/optimiser_memoire.py — mais seulement à la fin d'ingerer_recolte,
    # alors que trois autres chemins régénèrent aussi cette base (mise_a_jour
    # « 6/6 », traducteur_fr._generer, l'étape « Sorts en attente » de
    # l'Atelier). Chacun laissait derrière lui un DB_Objets.lua plat, donc un
    # addon mort au chargement, sans le moindre message. En le produisant
    # directement au bon format, tous ces chemins sont réparés d'un coup.
    n, taille = ecrire_db("DB_Objets.lua", "Objets", objets, True,
                          paresseux=True)
    rapport.append(("Objets", n, taille, stats_i))

    # ------------------------------------------------------------------
    # CRÉATURES
    # ------------------------------------------------------------------
    wdb_c = ex("creatures.json")
    fr_c = fr("creature_template_locale.json")
    en_c = en("creature_template.json")
    tr_c = tr("creatures.json")

    creatures = {}
    at_creatures = {}
    stats_c = {"officiel": 0, "ia": 0, "custom": 0}
    for cid, loc in fr_c.items():
        nom_fr = loc.get("Name")
        if not nom_fr:
            continue
        e = en_c.get(cid, {})
        entree = {"N": nom_fr, "NE": e.get("name")}
        if loc.get("Title"):
            entree["S"] = loc["Title"]
            entree["SE"] = e.get("subname")
        creatures[cid] = entree
        stats_c["officiel"] += 1
    for cid, w in wdb_c.items():
        officiel_en = en_c.get(cid)
        identique = officiel_en and normaliser(w.get("Name")) == normaliser(
            officiel_en.get("name"))
        if identique and cid in creatures:
            continue
        if cid in tr_c:
            entree = dict(tr_c[cid])
            entree["NE"] = w.get("Name")
            if w.get("SubName"):
                entree["SE"] = w.get("SubName")
            creatures[cid] = entree
            stats_c["ia"] += 1
        else:
            at_creatures[cid] = w
            stats_c["custom"] += 1
            creatures.pop(cid, None)
    a_traduire["creatures.json"] = at_creatures
    n, taille = ecrire_db("DB_Creatures.lua", "Creatures", creatures, True)
    rapport.append(("Créatures", n, taille, stats_c))

    # ------------------------------------------------------------------
    # OBJETS DU MONDE (gameobjects)
    # ------------------------------------------------------------------
    wdb_g = ex("objets_monde.json")
    fr_g = fr("gameobject_template_locale.json")
    en_g = en("gameobject_template.json")
    tr_g = tr("objets_monde.json")

    gos = {}
    at_gos = {}
    stats_g = {"officiel": 0, "ia": 0, "custom": 0}
    for gid, loc in fr_g.items():
        if loc.get("name"):
            e = en_g.get(gid, {})
            gos[gid] = {"N": loc["name"], "NE": e.get("name")}
            stats_g["officiel"] += 1
    for gid, w in wdb_g.items():
        officiel_en = en_g.get(gid)
        identique = officiel_en and normaliser(w.get("Name")) == normaliser(
            officiel_en.get("name"))
        if identique and gid in gos:
            continue
        if gid in tr_g:
            entree = dict(tr_g[gid])
            entree["NE"] = w.get("Name")
            gos[gid] = entree
            stats_g["ia"] += 1
        else:
            at_gos[gid] = w
            stats_g["custom"] += 1
            gos.pop(gid, None)
    a_traduire["objets_monde.json"] = at_gos
    n, taille = ecrire_db("DB_ObjetsMonde.lua", "ObjetsMonde", gos, True)
    rapport.append(("Objets du monde", n, taille, stats_g))

    # ------------------------------------------------------------------
    # RÉPLIQUES : correspondance EN -> FR via broadcast_text (la TDB moderne
    # y a migré tous les textes parlés : gossip, cris de monstres, etc.)
    # ------------------------------------------------------------------
    en_b = en("broadcast_text.json")
    fr_b = fr("broadcast_text_locale.json")
    broadcast = {}
    for bid, loc in fr_b.items():
        off = en_b.get(bid, {})
        for champ in ("Text", "Text1"):
            t_en, t_fr = off.get(champ), loc.get(champ)
            if t_en and t_fr and t_en not in broadcast:
                broadcast[t_en] = t_fr

    # ------------------------------------------------------------------
    # TEXTES DE PNJ (gossip) — table texteEN -> texteFR
    # Textes rencontrés (WDB) croisés avec broadcast_text, plus les IA.
    # ------------------------------------------------------------------
    wdb_t = ex("textes_pnj.json")
    tr_t = tr("textes_pnj.json")

    textes = {}
    at_textes = {}
    stats_t = {"officiel": 0, "ia": 0, "custom": 0}
    for tid, w in wdb_t.items():
        for texte_en in w.get("Texts", []):
            if texte_en in textes:
                continue
            if texte_en in broadcast:
                textes[texte_en] = broadcast[texte_en]
                stats_t["officiel"] += 1
            elif texte_en in tr_t:
                textes[texte_en] = tr_t[texte_en]
                stats_t["ia"] += 1
            else:
                at_textes[texte_en] = True
                stats_t["custom"] += 1
    # Les traductions IA de textes récoltés en jeu (clés normalisées $n)
    for k, v in tr_t.items():
        textes.setdefault(k, v)
    a_traduire["textes_pnj.json"] = at_textes
    n, taille = ecrire_db("DB_TextesPNJ.lua", "TextesPNJ", textes, False)
    rapport.append(("Textes PNJ", n, taille, stats_t))

    # ------------------------------------------------------------------
    # OPTIONS DE GOSSIP — texteEN -> texteFR (base officielle + IA)
    # ------------------------------------------------------------------
    fr_go = fr("gossip_menu_option_locale.json")
    en_go = en("gossip_menu_option.json")
    tr_go = tr("gossip.json")

    gossip = {}
    stats_go = {"officiel": 0, "ia": 0}
    for cle, off in en_go.items():
        opt_en = off.get("OptionText")
        if not opt_en or opt_en in gossip:
            continue
        opt_fr = fr_go.get(cle, {}).get("OptionText") or broadcast.get(opt_en)
        if opt_fr:
            gossip[opt_en] = opt_fr
            stats_go["officiel"] += 1
    for k, v in tr_go.items():
        if k not in gossip:
            gossip[k] = v
            stats_go["ia"] += 1
    n, taille = ecrire_db("DB_Gossip.lua", "Gossip", gossip, False)
    rapport.append(("Options gossip", n, taille, stats_go))

    # ------------------------------------------------------------------
    # RÉPLIQUES DES PNJ DANS LE CHAT (say/yell) — addon annexe désactivable
    # (fichier volumineux : ~11 Mo)
    # ------------------------------------------------------------------
    annexe = os.path.join(os.path.dirname(ADDON), "AscensionFR_Repliques")
    os.makedirs(annexe, exist_ok=True)
    with open(os.path.join(annexe, "AscensionFR_Repliques.toc"), "w",
              encoding="utf-8") as f:
        f.write("## Interface: 30300\n"
                "## Title: Ascension |cff0099ffFR|r - Répliques\n"
                "## Notes: Traduction des paroles des PNJ dans le chat "
                "(désactivable si le chargement est trop lent)\n"
                "## Dependencies: AscensionFR\n\n"
                "DB_Repliques.lua\n")
    n, taille = ecrire_db("DB_Repliques.lua", "Repliques", broadcast, False,
                          chemin=os.path.join(annexe, "DB_Repliques.lua"))
    rapport.append(("Répliques (addon annexe)", n, taille, {}))
    # 2.0.1 : la base plate repart en PARESSEUX par texte (mini-blocages
    # du jour de sortie — la mémoire vive pèse sur le ménage du jeu).
    try:
        import paresseux_textes
        paresseux_textes.transformer(
            os.path.join(annexe, "DB_Repliques.lua"),
            "AscensionFR.DB.Repliques", True)
    except Exception as e:
        print("! paresseux Répliques : %s (la base plate reste valable)" % e)

    # ------------------------------------------------------------------
    # PAGES (livres) — texteEN -> texteFR
    # ------------------------------------------------------------------
    wdb_p = ex("pages.json")
    fr_p = fr("page_text_locale.json")
    en_p = en("page_text.json")
    tr_p = tr("pages.json")

    pages = {}
    at_pages = {}
    stats_p = {"officiel": 0, "ia": 0, "custom": 0}
    for pid, loc in fr_p.items():
        texte_fr = loc.get("Text")
        texte_en = en_p.get(pid, {}).get("Text")
        if texte_fr and texte_en:
            pages[texte_en] = texte_fr
            stats_p["officiel"] += 1
    for pid, w in wdb_p.items():
        texte_en = w.get("Text")
        if not texte_en or texte_en in pages:
            continue
        if texte_en in tr_p:
            pages[texte_en] = tr_p[texte_en]
            stats_p["ia"] += 1
        else:
            at_pages[texte_en] = True
            stats_p["custom"] += 1
    for k, v in tr_p.items():
        pages.setdefault(k, v)
    a_traduire["pages.json"] = at_pages
    n, taille = ecrire_db("DB_Pages.lua", "Pages", pages, False)
    rapport.append(("Pages", n, taille, stats_p))

    # ------------------------------------------------------------------
    # DIVERS (traductions IA / récolte)
    # Les sorts ont leur propre générateur (generateur_sorts.py) : ils
    # viennent des DBC du client, pas des caches serveur.
    # ------------------------------------------------------------------
    tr_d = tr("divers.json")
    n, taille = ecrire_db("DB_Divers.lua", "Divers", tr_d, False)
    rapport.append(("Divers", n, taille, {}))

    # Libellés d'interface venus des DBC (sous-classes d'objets, métiers) :
    # ils ne viennent ni du serveur ni des GlobalStrings.
    tr_l = tr("libelles.json")
    n, taille = ecrire_db("DB_Libelles.lua", "Libelles", tr_l, False)
    rapport.append(("Libellés (DBC)", n, taille, {}))

    # ------------------------------------------------------------------
    # GLOBALSTRINGS (interface)
    # ------------------------------------------------------------------
    # Le décodage des échappements Lua est délicat : les chaînes de chat
    # finissent par « :\32 », soit « : » suivi d'un ESPACE. Un décodage naïf
    # laissait « \32 » devant chaque message de chat en jeu.
    gs_chemin = os.path.join(base, "sources", "GlobalStrings_frFR.lua")
    ui = charger_globalstrings(gs_chemin) if os.path.exists(gs_chemin) else {}

    # Le texte d'interface propre à Ascension (GlobalStrings.dbc, 5 504 clés
    # sans équivalent officiel — voir outils/auditer_gisement.py). Il vient
    # APRÈS l'officiel mais ne l'écrase JAMAIS : là où Blizzard a traduit, sa
    # version fait référence, la nôtre n'est qu'un complément.
    maison = os.path.join(base, "traductions", "interface_maison.json")
    if os.path.exists(maison):
        with open(maison, encoding="utf-8") as f:
            ajouts = json.load(f)
        neuves = {k: v for k, v in ajouts.items() if k not in ui}
        ui.update(neuves)
        print("  + %d chaînes d'interface maison (%d déjà couvertes par "
              "l'officiel)" % (len(neuves), len(ajouts) - len(neuves)))
        # Clés dont ASCENSION a changé le SENS en gardant le nom : l'officiel
        # frFR y est un contresens, la couche maison PRIME (bloc 10,
        # 28/07/2026). ITEM_ACCOUNTBOUND vaut « Realm Bound » chez eux —
        # « Lié au compte » officiel est faux sur un serveur multi-royaumes.
        for cle in ("ITEM_ACCOUNTBOUND",):
            if cle in ajouts:
                ui[cle] = ajouts[cle]

    n, taille = ecrire_db("DB_Interface.lua", "UI", ui, False)
    rapport.append(("Interface (GlobalStrings)", n, taille, {}))

    # ------------------------------------------------------------------
    # Fichiers à traduire + rapport
    # ------------------------------------------------------------------
    # FILTRE DES ENTRÉES SANS TEXTE SOURCE (bloc 2d, 28/07/2026). Le cache
    # WDB livre des entrées au nom VIDE (279 mesurées à l'audit : 278
    # objets_monde + 1 créature, toutes Name="") : rien en aval ne peut
    # traduire du vide, et elles étaient requeuées à CHAQUE cycle — 98,6 %
    # de la file objets_monde était du poids mort, le volume de la file ne
    # voulait plus rien dire comme indicateur. On filtre à l'entonnoir
    # d'écriture : une entrée n'entre dans la file que si elle porte au
    # moins UN texte source non vide.
    def porte_texte(entree):
        if isinstance(entree, str):
            return bool(entree.strip())
        if isinstance(entree, dict):
            return any(isinstance(v, str) and v.strip()
                       for v in entree.values())
        return bool(entree)

    for nom, contenu in a_traduire.items():
        garde = {cle: entree for cle, entree in contenu.items()
                 if porte_texte(entree)}
        vides = len(contenu) - len(garde)
        if vides:
            print("  file %s : %d entrée(s) sans texte source écartée(s)"
                  % (nom, vides))
            a_traduire[nom] = garde
        with open(os.path.join(dossier_at, nom), "w", encoding="utf-8") as f:
            json.dump(a_traduire[nom], f, ensure_ascii=False, indent=1,
                      sort_keys=True)

    print("=" * 72)
    print("%-28s %10s %12s   %s" % ("Base", "entrées", "taille", "détail"))
    print("-" * 72)
    total = 0
    for nom, n, taille, stats in rapport:
        total += taille
        detail = " ".join("%s=%s" % kv for kv in sorted(stats.items()))
        print("%-28s %10d %10.1f Ko   %s" % (nom, n, taille / 1024.0, detail))
    print("-" * 72)
    print("%-28s %21.1f Mo" % ("TOTAL", total / 1048576.0))
    for nom, contenu in a_traduire.items():
        if contenu:
            print("À traduire : %-20s %d entrées" % (nom, len(contenu)))

    if SATURATIONS:
        print()
        print("!" * 72)
        print("BASE(S) NON ÉCRITE(S) — limite de constantes de Lua 5.1 "
              "dépassée :")
        for nom, constantes, entrees_ in SATURATIONS:
            print("  %-24s %d constantes / %d  (%d entrées)"
                  % (nom, constantes, LIMITE_CONSTANTES, entrees_))
        print("Les anciens fichiers sont conservés — l'addon se charge "
              "encore, mais il")
        print("n'a PAS le contenu du jour. Passe ces bases en paresseux.")
        print("!" * 72)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main() or 0)
