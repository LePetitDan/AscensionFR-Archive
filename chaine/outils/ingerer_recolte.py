# -*- coding: utf-8 -*-
"""
ingerer_recolte.py — exploite ENFIN les sections « Récolte : rencontrés sans
traduction » des rapports : gossips (menus de dialogue des PNJ), textes de
PNJ, et textes de quêtes (progression / rendu). Jusqu'ici, seuls les sorts
étaient traités ; le reste dormait.

SOURCES (les deux sont lues, la sauvegarde d'abord)
---------------------------------------------------
1. La sauvegarde LOCALE de l'addon (WTF\\...\\AscensionFR.lua) : la plus
   fiable — l'addon y garde le TEXTE ANGLAIS exact des quêtes récoltées.
2. Les rapports .txt du dossier rapports/ : lignes « [Catégorie] clé » et,
   depuis la v1.5, « [Catégorie] clé ==> texte anglais ».

CE QUI EST ÉCRIT
----------------
DB/DB_Communaute.lua — un fichier d'ajouts qui SURCHARGE les bases générées
(même principe que DB_SortsCorrections) : il survit aux régénérations.
  - Gossip     : G["texte anglais"] = "texte français"
  - TextesPNJ  : T["texte anglais"] = "texte français"
  - Quêtes     : quete(id, "P"|"R", "texte français")   (P=progression, R=rendu)

GARDE-FOUS
----------
- Jamais de doublon : ce qui est déjà traduit (bases générées OU ce fichier)
  est ignoré.
- Les récoltes DÉJÀ en français (faux positifs de l'addon) sont écartées :
  un texte présent parmi les traductions existantes, ou que Google rend à
  l'identique, n'est pas réécrit.
- Les sorts ([Sorts] id) ne sont PAS traités ici : outils/recuperer_db.py
  s'en charge (--fichier).

USAGE : python outils/ingerer_recolte.py [--dry]
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from traduire_gisement import traduire  # noqa: E402  (Google + glossaire WoW)
from generateur_db import harmoniser  # noqa: E402  (vocabulaire arbitré)
from chemin_client import (JEU, exiger_client,  # noqa: E402
                           client_present, CODE_CLIENT_ABSENT)
from ecriture_sure import ecrire_json  # noqa: E402

DBDIR = os.path.join(JEU, "Interface", "AddOns", "AscensionFR", "DB")
COMMUNAUTE = os.path.join(DBDIR, "DB_Communaute.lua")
RAPPORTS = os.path.join(BASE, "rapports")

ENTETE = '''-- Contributions de la communauté — généré par outils/ingerer_recolte.py.
-- Chargé APRÈS les bases générées (voir la .toc) : ces entrées BOUCHENT
-- leurs trous et survivent à leur régénération — mais ne les écrasent
-- JAMAIS. Une base régénérée (l'usine, qui s'améliore à chaque arbitrage)
-- bat une ligne d'accumulation ; avant le programme 31 c'était l'inverse,
-- et le vieux battait le neuf à chaque /reload.
local vraiG = AscensionFR.DB.Gossip
local vraiT = AscensionFR.DB.TextesPNJ
local Q = AscensionFR.DB.Quetes
local function garde(vrai)
    return setmetatable({}, {__newindex = function(_, cle, valeur)
        if vrai[cle] == nil then vrai[cle] = valeur end
    end})
end
local G = garde(vraiG)
local T = garde(vraiT)
local function quete(id, champ, texte)
    local e = Q[id]
    if e then
        if e[champ] == nil then e[champ] = texte end
    else
        Q[id] = { [champ] = texte }
    end
end
'''


# --------------------------------------------------------------------------- #
# Lua <-> texte
# --------------------------------------------------------------------------- #
def echapper(s):
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return s.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")


def desechapper(s):
    return re.sub(r"\\(.)", lambda m: {"n": "\n", "t": "\t"}.get(
        m.group(1), m.group(1)), s)


RE_CHAINE = r'"((?:\\.|[^"\\])*)"'


def cles_et_valeurs(chemin):
    """(clés, valeurs) déjà présentes dans une base « texte -> texte »."""
    cles, valeurs = set(), set()
    if os.path.exists(chemin):
        with open(chemin, encoding="utf-8") as f:
            for m in re.finditer(r'\[%s\]\s*=\s*%s' % (RE_CHAINE, RE_CHAINE),
                                 f.read()):
                cles.add(desechapper(m.group(1)))
                valeurs.add(desechapper(m.group(2)))
    return cles, valeurs


def quetes_deja_couvertes():
    """{(id, champ)} déjà présents (bases générées + communauté)."""
    couvert = set()
    chemin = os.path.join(DBDIR, "DB_Quetes.lua")
    if os.path.exists(chemin):
        with open(chemin, encoding="utf-8") as f:
            for ligne in f:
                m = re.match(r"^DB\[(\d+)\]=\{(.*)", ligne)
                if m:
                    for champ in ("P", "R"):
                        if re.search(r'[,{]%s="' % champ, m.group(2)):
                            couvert.add((int(m.group(1)), champ))
    if os.path.exists(COMMUNAUTE):
        with open(COMMUNAUTE, encoding="utf-8") as f:
            for m in re.finditer(r'quete\((\d+),\s*"([PR])"', f.read()):
                couvert.add((int(m.group(1)), m.group(2)))
    return couvert


# --------------------------------------------------------------------------- #
# Sources : sauvegarde locale + rapports
# --------------------------------------------------------------------------- #
def depuis_sauvegarde():
    """{catégorie: {clé: valeur}} depuis la sauvegarde locale de l'addon."""
    recueilli = {}
    base = os.path.join(JEU, "WTF", "Account")
    if not os.path.isdir(base):
        return recueilli
    from lupa import LuaRuntime
    for compte in sorted(os.listdir(base)):
        chemin = os.path.join(base, compte, "SavedVariables",
                              "AscensionFR.lua")
        if not os.path.isfile(chemin):
            continue
        try:
            lua = LuaRuntime(unpack_returned_tuples=True)
            with open(chemin, encoding="utf-8") as f:
                lua.execute(f.read())
            saved = lua.globals().AscensionFRSaved
            recolte = saved and saved["Recolte"]
            if not recolte:
                continue
            for categorie, table in recolte.items():
                if not hasattr(table, "items"):
                    continue
                d = recueilli.setdefault(str(categorie), {})
                for cle, valeur in table.items():
                    d[str(cle)] = valeur if isinstance(valeur, str) else ""
        except Exception:
            continue
    return recueilli


def depuis_rapports():
    """Pareil, depuis les .txt (lignes [Cat] clé et [Cat] clé ==> texte).
    Une ligne sans [préfixe] prolonge l'entrée précédente (texte multi-ligne)."""
    recueilli = {}
    if not os.path.isdir(RAPPORTS):
        return recueilli
    for nom in sorted(os.listdir(RAPPORTS)):
        if not nom.endswith(".txt") or nom.startswith("ids_"):
            continue
        dans, courant = False, None
        with open(os.path.join(RAPPORTS, nom), encoding="utf-8") as f:
            for brut in f:
                ligne = brut.rstrip("\n")
                if ligne.startswith("--- Récolte"):
                    dans = True
                    continue
                if ligne.startswith("---") or ligne.startswith("==="):
                    dans, courant = False, None
                    continue
                if not dans:
                    continue
                m = re.match(r"^\[(\w+)\] (.*)$", ligne)
                if m:
                    categorie, reste = m.group(1), m.group(2)
                    if " ==> " in reste:
                        cle, valeur = reste.split(" ==> ", 1)
                    else:
                        cle, valeur = reste, ""
                    d = recueilli.setdefault(categorie, {})
                    d[cle] = valeur
                    courant = (categorie, cle)
                elif courant and ligne and not ligne.startswith("..."):
                    categorie, cle = courant
                    d = recueilli[categorie]
                    if d[cle]:
                        d[cle] += "\n" + ligne
                    elif "==>" not in ligne:
                        # continuation de la CLÉ (gossip/PNJ multi-ligne)
                        nouveau = cle + "\n" + ligne
                        d[nouveau] = d.pop(cle)
                        courant = (categorie, nouveau)
    return recueilli


def fusionner(a, b):
    """b complète a sans écraser une valeur non vide."""
    for categorie, entrees in b.items():
        d = a.setdefault(categorie, {})
        for cle, valeur in entrees.items():
            if cle not in d or (valeur and not d[cle]):
                d[cle] = valeur
    return a


# --------------------------------------------------------------------------- #
# Pseudos des personnages RÉCOLTEURS : les caches WDB livrent les textes de
# quête avec le nom du personnage RÉSOLU (« Merci, <pseudo>. ») là où le
# modèle officiel dit $n. Double problème : le pseudo d'un joueur serait
# publié (interdit — règle de Dan), et tous les autres joueurs verraient ce
# nom-là au lieu du leur. Pour les quêtes (indexées par ID), on remplace par
# $n, substitué à l'affichage par Core.Substituer. Pour Gossip/TextesPNJ
# (indexés par le texte anglais), on ÉCARTE l'entrée : modifier la clé
# casserait la reconnaissance.
#
# 🛑 AUCUN nom en dur ici (programme 34, bloc 0) : une liste de repli est
# partie dans le dépôt cloud — la donnée vit dans le fichier LOCAL, jamais
# publié ni poussé : noms_recolteurs.local.txt (un nom par ligne, # =
# commentaire ; dans le cloud il arrive par le pont PRIVÉ). Grande purge du
# 21/07/2026 : 47 noms, 241 textes nettoyés. ATTENTION aux homonymes de PNJ
# (un prénom de PNJ officiel pris pour un pseudo, incident du 22/07) :
# vérifier creature_template avant d'ajouter un nom. L'ABSENCE du fichier
# se dit bruyamment dans main() : un filet vide n'a pas le droit d'être
# silencieux.
NOMS_RECOLTEURS = []
_FICHIER_NOMS = os.path.join(BASE, "noms_recolteurs.local.txt")
if os.path.exists(_FICHIER_NOMS):
    with open(_FICHIER_NOMS, encoding="utf-8") as _f:
        for _ligne in _f:
            _nom = _ligne.strip()
            if _nom and not _nom.startswith("#") \
                    and _nom not in NOMS_RECOLTEURS:
                NOMS_RECOLTEURS.append(_nom)

# Frontières de mots : « Alda » (inventé) ne doit pas manger « Aldabert ».
_RE_PSEUDOS = re.compile(
    r"(?<![A-Za-z])(" + "|".join(sorted(NOMS_RECOLTEURS, key=len,
                                        reverse=True))
    + r")(?![a-zéèA-Z])") if NOMS_RECOLTEURS else None


def sans_pseudo(texte):
    if _RE_PSEUDOS is None:      # liste absente : rien à remplacer
        return texte
    return _RE_PSEUDOS.sub("$n", texte)


def porte_pseudo(texte):
    """GARDE : cherche aussi dans le texte dénudé — un pseudo collé à un
    code couleur (« |cFFB5FFFFStarcaller ») n'a pas de frontière de mot
    et passait au travers (programme 32, bloc B)."""
    if _RE_PSEUDOS is None:
        return False
    return bool(_RE_PSEUDOS.search(texte)
                or _RE_PSEUDOS.search(denuder(texte)))


# Les CODES DE FORMAT du client (|TInterface\...|t, |cFF12AB34, |r) rendent
# AVEUGLE tout motif ancré (^) ou à frontière de mot : « |cFFB5FFFFStarcaller »
# n'a pas de frontière, « |T...|t #3 Xxx Rating: » ne commence pas par #.
# C'est le piège du lot 14, retombé au programme 32 (48 classements passés
# à travers le filtre PENDANT la relance du 31). La parade n'est pas une
# regex plus longue — c'est la NORMALISATION : les GARDES regardent le
# texte dénudé. (La substitution, elle, reste sur le texte brut :
# remplacer dans une copie dénudée ne se recolle pas.)
RE_CODES_FORMAT = re.compile(r"\|T[^|]*\|t|\|c[0-9a-fA-F]{8}|\|r|\|n")


def denuder(texte):
    """Copie sans codes de format, pour les GARDES (jamais pour écrire)."""
    return RE_CODES_FORMAT.sub(" ", texte).strip()


# Les CLASSEMENTS d'arène (« #6 Xxx Rating: 2252 | Wins... ») : des noms de
# joueurs et des chiffres qui changent à chaque récolte. Une clé volatile ne
# re-matchera jamais — la traduire gonfle l'append-only pour rien, et y
# grave des pseudos que le balayeur ne connaît pas (programme 31, bloc E ;
# 254+149 lignes étaient entrées AVANT le filtre et sa réparation — purgées
# au programme 32). Confronté au texte DÉNUDÉ (voir denuder).
RE_CLASSEMENT = re.compile(r"^#\d+\s+\S+\s+Rating:\s*\d+", re.I)


def paraît_anglais(texte):
    """Vrai si le texte mérite une traduction (écarte le déjà-français)."""
    return len(re.findall(r"[A-Za-z]{2,}", texte)) >= 1 and not re.search(
        r"[àâéèêëîïôùûçœ]|(?:\b(?:le|la|les|de|des|du|une?|vous|votre)\b)",
        texte, re.I)


def main():
    # DÉCOUPAGE ENTRÉE / TRADUCTION / SORTIE (programme 33, bloc A). La
    # dépendance au client n'est pas un besoin de CALCUL, c'est un besoin de
    # FICHIERS : lire la moisson et les bases de dédup, écrire DB_Communaute.
    # --sans-pose (le cloud) : la moisson et les bases de dédup viennent d'un
    # arbre FOURNI (ASCENSIONFR_JEU, rempli par le pont Dan->cloud) ; la
    # TRADUCTION se fait ; la POSE dans DB_Communaute est SAUTÉE et ses lignes
    # partent dans un fichier d'attente qui revient chez Dan (c'est lui qui
    # pose). Les gardes du 31/32 (clé absente, denuder, classements, pseudos,
    # « déjà en français ») vivent DANS la traduction, donc s'appliquent aussi
    # dans le cloud — vérifié explicitement au banc.
    sans_pose = ("--sans-pose" in sys.argv
                 or os.environ.get("ASCENSIONFR_SANS_POSE") == "1")
    if sans_pose:
        if not client_present():
            print("MOISSON ABSENTE — --sans-pose exige un arbre fourni via "
                  "ASCENSIONFR_JEU (bases de dédup + SavedVariables). "
                  "Réglage : ASCENSIONFR_JEU. Arrêt avant tout appel réseau.")
            sys.stdout.flush()
            sys.exit(CODE_CLIENT_ABSENT)
    else:
        # Chez Dan : la cible et les anti-doublons vivent chez le client ;
        # sans lui, s'arrêter ICI — pas après les appels réseau (prog. 31).
        exiger_client("ingerer_recolte (étape 5 — récolte)")
    dry = "--dry" in sys.argv
    if not NOMS_RECOLTEURS:
        # Un filet vide n'a pas le droit d'être silencieux (prog. 34, bloc 0).
        print("⚠️ noms_recolteurs.local.txt ABSENT ou vide — le filet "
              "anti-pseudo est réduit aux gabarits $n. Fournis la liste "
              "(chez Dan : la racine de WorkFlow ; cloud : le pont privé).")
    recueilli = fusionner(depuis_sauvegarde(), depuis_rapports())

    g_cles, g_vals = cles_et_valeurs(os.path.join(DBDIR, "DB_Gossip.lua"))
    t_cles, t_vals = cles_et_valeurs(os.path.join(DBDIR, "DB_TextesPNJ.lua"))
    c_cles, _ = cles_et_valeurs(COMMUNAUTE)
    q_couvert = quetes_deja_couvertes()

    lignes, ignores = [], 0
    # Les comptes du passage (programme 31, bloc F) : ils partent dans la
    # ligne @@BILAN, que l'orchestrateur consigne — « vert » ne voudra
    # plus dire « code retour zéro » mais « a fait son travail ».
    n_tentees = n_refusees = n_identiques = 0

    # POINT D'ÉTAPE (programme 31) : sur une machine qu'on peut éteindre à
    # tout instant, l'append de fin de passage perdait TOUT le travail en
    # cours. DB_Communaute se pose désormais par paquets de 100 lignes —
    # une coupure ne reperd jamais plus que le paquet en cours, et la
    # relance reprend (dédup) là où on en était.
    n_communaute = [0]
    # Le fichier d'ATTENTE (cloud) : les lignes Lua destinées à DB_Communaute
    # y sont écrites au lieu d'être posées. Il revient chez Dan par le pont ;
    # sa pose (avec l'entête à garde inversée) se fait à l'arrivée. On l'efface
    # au démarrage d'un passage cloud pour ne pas cumuler deux moissons.
    ATTENTE = os.path.join(BASE, "traductions", "communaute_en_attente.txt")
    if sans_pose and not dry and os.path.exists(ATTENTE):
        os.remove(ATTENTE)

    def poser_communaute(lot):
        if dry or not lot:
            return
        if sans_pose:
            # CLOUD : on ne touche pas DB_Communaute (pas de client) ; les
            # lignes partent en attente (append, point d'étape naturel).
            with open(ATTENTE, "a", encoding="utf-8") as f_a:
                f_a.write("\n".join(lot) + "\n")
            n_communaute[0] += len(lot)
            lot.clear()
            return
        contenu_c = ""
        if os.path.exists(COMMUNAUTE):
            with open(COMMUNAUTE, encoding="utf-8") as f_c:
                contenu_c = f_c.read()
        with open(COMMUNAUTE, "a", encoding="utf-8") as f_c:
            if "local function quete(" not in contenu_c:
                f_c.write(ENTETE)
            f_c.write("\n-- --- Ingéré (ingerer_recolte.py) ---\n"
                      + "\n".join(lot) + "\n")
        n_communaute[0] += len(lot)
        lot.clear()

    # La mémoire des écartés (traductions/recolte_ecartes.json), chargée
    # UNE fois pour les deux boucles.
    chemin_ecartes = os.path.join(BASE, "traductions",
                                  "recolte_ecartes.json")
    try:
        with open(chemin_ecartes, encoding="utf-8") as f_e:
            ecartes = json.load(f_e)
    except (OSError, ValueError):
        ecartes = {}

    # Les « déjà en français » (programme 31, bloc D) : un texte que Google
    # rend à l'identique n'a rien à traduire — le re-tester à CHAQUE
    # passage brûlait ~750 appels pour rien. Consigné une fois, tu ensuite.
    # DEUX portes de sortie : la consigne est liée à la VERSION DU BOUCLIER
    # (un moteur qui change la vide tout seul — même règle que
    # rejets_chroniques), et --retenter-ecartes la vide à la main.
    from traducteur_fr import VERSION_BOUCLIER
    bloc_df = ecartes.get("deja_francais") or {}
    df_reinitialise = False
    if ("--retenter-ecartes" in sys.argv
            or bloc_df.get("version_bouclier") != VERSION_BOUCLIER):
        if bloc_df.get("textes"):
            print("%d écarté(s) « déjà en français » remis en jeu (%s)."
                  % (len(bloc_df["textes"]),
                     "--retenter-ecartes" if "--retenter-ecartes"
                     in sys.argv else "la protection a changé"))
            # la remise à zéro doit atteindre le DISQUE, sinon la vieille
            # liste reviendrait au passage suivant
            df_reinitialise = True
        bloc_df = {"version_bouclier": VERSION_BOUCLIER, "textes": []}
    deja_francais = set(bloc_df.get("textes", []))
    nouveaux_francais = set()
    tus_francais = 0

    # 1) Gossip et TextesPNJ : « texte anglais -> texte français ».
    for categorie, prefixe, deja_c, deja_v in (
            ("Gossip", "G", g_cles, g_vals),
            ("TextesPNJ", "T", t_cles, t_vals)):
        for cle in sorted(recueilli.get(categorie, {})):
            texte = cle.strip()
            if (not texte or texte in deja_c or texte in c_cles
                    or texte in deja_v or not paraît_anglais(texte)):
                ignores += 1
                continue
            if texte in deja_francais:
                tus_francais += 1
                ignores += 1
                continue
            if RE_CLASSEMENT.match(denuder(texte)):
                ignores += 1      # classement volatile : jamais ingéré
                continue
            if porte_pseudo(texte):
                print("  ! pseudo de récolteur dans « %s… » — écarté"
                      % texte[:40])
                ignores += 1
                continue
            n_tentees += 1
            fr = traduire(texte)
            if not fr:            # échec RÉSEAU : jamais consigné, on
                n_refusees += 1   # veut le retenter au prochain passage
                ignores += 1
                continue
            if fr == texte:       # Google rend l'identique : consigné
                nouveaux_francais.add(texte)
                n_identiques += 1
                ignores += 1
                continue
            # DB_Communaute.lua est ouvert en AJOUT : aucune régénération ne
            # le nettoiera jamais. Le vocabulaire arbitré doit donc passer
            # ICI, à l'ingestion, ou il ne passera nulle part.
            fr = harmoniser(fr)
            lignes.append('%s["%s"]="%s"' % (prefixe, echapper(texte),
                                             echapper(fr)))
            print("  +%-9s %s -> %s" % (categorie, texte[:34], fr[:34]))
            if len(lignes) >= 100:
                poser_communaute(lignes)    # point d'étape

    # 2) Quêtes : progression (P) et rendu (R), par ID.
    # Les écartés PERSISTANTS (bloc D2, 29/07/2026) : 31 quêtes de VIEUX
    # rapports, sans texte anglais, étaient re-signalées à chaque passage
    # depuis des semaines — du bruit qui use l'œil. Une entrée sans texte
    # est consignée UNE fois dans traductions/recolte_ecartes.json puis
    # tue ; seuls les NOUVEAUX cas s'affichent encore (les rapports
    # récents embarquent toujours le texte : un nouveau cas est une
    # anomalie à voir, pas du bruit).
    deja_ecartes = set(ecartes.get("quetes_sans_texte", []))
    sans_texte = []
    tus = 0
    for categorie, champ in (("QuetesProgres", "P"), ("QuetesRendu", "R")):
        for cle, valeur in sorted(recueilli.get(categorie, {}).items()):
            if not cle.isdigit():
                continue
            id_ = int(cle)
            if (id_, champ) in q_couvert:
                ignores += 1
                continue
            texte = sans_pseudo((valeur or "").strip())
            if not texte:
                etiquette = "%s %s" % (categorie, cle)
                if etiquette in deja_ecartes:
                    tus += 1
                else:
                    sans_texte.append(etiquette)
                continue
            if porte_pseudo(texte):
                # la ceinture après la bretelle : un pseudo COLLÉ à un code
                # que sans_pseudo ne sait pas remplacer -> on écarte, on ne
                # verse pas un nom de joueur (programme 32, bloc B)
                print("  ! pseudo collé à un code dans la quête %s — "
                      "écartée" % cle)
                ignores += 1
                continue
            n_tentees += 1
            fr = traduire(texte)
            if not fr:
                n_refusees += 1
                ignores += 1
                continue
            lignes.append('quete(%d, "%s", "%s")'
                          % (id_, champ, echapper(harmoniser(fr))))
            q_couvert.add((id_, champ))
            print("  +Quete%s %s -> %s" % (champ, cle, fr[:40]))
            if len(lignes) >= 100:
                poser_communaute(lignes)    # point d'étape

    # 3) Divers et Pages : « texte anglais -> texte français », versés dans
    # les STORES (traductions/divers.json et pages.json) — la route choisie
    # au programme 31 (bloc E). Pourquoi les stores et pas de nouvelles
    # familles dans DB_Communaute : les bases générées les ramassent DÉJÀ
    # (generateur_db.py l.771-772 pour DB_Divers, l.736-763 pour DB_Pages),
    # donc le texte atteint le joueur à la régénération suivante SANS
    # toucher au chargeur de l'addon ; et les stores passent par le
    # vocabulaire arbitré (étape 6) et la publication contributive.
    # Garde « clé absente » : on ne remplace jamais une traduction posée.
    nouveaux_stores = 0
    for categorie, fichier, base_lua in (
            ("Divers", "divers.json", "DB_Divers.lua"),
            ("Pages", "pages.json", "DB_Pages.lua")):
        chemin_store = os.path.join(BASE, "traductions", fichier)
        try:
            with open(chemin_store, encoding="utf-8") as f_s:
                store = json.load(f_s)
        except (OSError, ValueError):
            store = {}
        db_cles, db_vals = cles_et_valeurs(os.path.join(DBDIR, base_lua))
        nouveaux = 0
        for cle in sorted(recueilli.get(categorie, {})):
            texte = cle.strip()
            if (not texte or texte in store or texte in db_cles
                    or texte in db_vals or not paraît_anglais(texte)):
                ignores += 1
                continue
            if texte in deja_francais:
                tus_francais += 1
                ignores += 1
                continue
            if porte_pseudo(texte):
                print("  ! pseudo de récolteur dans « %s… » — écarté"
                      % texte[:40])
                ignores += 1
                continue
            n_tentees += 1
            fr = traduire(texte)
            if not fr:
                n_refusees += 1
                ignores += 1
                continue
            if fr == texte:
                nouveaux_francais.add(texte)
                n_identiques += 1
                ignores += 1
                continue
            fr = harmoniser(fr)
            store[texte] = fr
            nouveaux += 1
            print("  +%-9s %s -> %s" % (categorie, texte[:34], fr[:34]))
            if nouveaux % 200 == 0 and not dry:
                ecrire_json(chemin_store, store)    # point d'étape
        if nouveaux and not dry:
            # Atomique ; la base générée ramassera au prochain cycle.
            ecrire_json(chemin_store, store)
            print("  %s : +%d entrée(s) — régénération au prochain "
                  "passage de l'usine" % (fichier, nouveaux))
        nouveaux_stores += nouveaux

    total_communaute = n_communaute[0] + len(lignes)
    verbe = "en attente de pose" if sans_pose else "prêtes"
    print("\n%d entrée(s) %s | %d versée(s) aux stores | %d ignorée(s) "
          "(déjà couvertes ou déjà en français)"
          % (total_communaute, verbe, nouveaux_stores, ignores))
    # La ligne machine du bloc F : tentées = envoyées au moteur ce passage.
    # « en_attente » (programme 33, bloc A) : les entrées TRADUITES que le
    # cloud ne peut pas poser (pas de client). Elles COMPTENT dans traduites
    # — un passage cloud qui traduit 4 000 entrées n'est pas « rien à faire ».
    print("@@BILAN " + json.dumps(
        {"tentees": n_tentees,
         "traduites": total_communaute + nouveaux_stores,
         "refusees": n_refusees,
         "ecartees": n_identiques + tus_francais,
         "en_attente": total_communaute if sans_pose else 0},
        ensure_ascii=False))
    if tus:
        print("(%d quête(s) sans texte déjà consignée(s) — silence)" % tus)
    if tus_francais:
        print("(%d « déjà en français » consignés — %d appel(s) Google "
              "épargnés)" % (tus_francais, 2 * tus_francais))
    if sans_texte:
        print("%d quête(s) SANS texte anglais NOUVELLE(S) — consignées "
              "dans recolte_ecartes.json : %s"
              % (len(sans_texte), ", ".join(sans_texte[:10])))
    if nouveaux_francais:
        print("%d texte(s) « déjà en français » NOUVEAUX — consignés "
              "(déconsigne : --retenter-ecartes, ou un changement de "
              "bouclier)" % len(nouveaux_francais))
    if not dry and (sans_texte or nouveaux_francais or df_reinitialise):
        deja_ecartes.update(sans_texte)
        ecartes["quetes_sans_texte"] = sorted(deja_ecartes)
        bloc_df["textes"] = sorted(deja_francais | nouveaux_francais)
        ecartes["deja_francais"] = bloc_df
        # Atomique (programme 31, bloc B).
        ecrire_json(chemin_ecartes, ecartes, sort_keys=False)
    if dry:
        print("--dry : rien écrit.")
        return 0
    poser_communaute(lignes)    # le dernier paquet
    if total_communaute and sans_pose:
        print("%d ligne(s) EN ATTENTE DE POSE -> %s (reviennent chez Dan "
              "par le pont ; la pose se fait à l'arrivée)."
              % (total_communaute, os.path.relpath(ATTENTE, BASE)))
    elif total_communaute:
        print("Écrit dans DB_Communaute.lua — vérifie la .toc puis lupa.")
    return 0


if __name__ == "__main__":
    code = main()
    # Dernières étapes de l'Atelier, accrochées ici parce que l'exe du bureau
    # est figé (on ne peut pas ajouter d'étape à sa liste). Elles écrivent
    # DES BASES DU CLIENT (DB_Objets paresseux, DB_Meta) : dans le cloud
    # (--sans-pose) il n'y a pas de client, on les saute — elles se font chez
    # Dan, à la régénération d'arrivée (programme 33, bloc A/E).
    _sans_pose = ("--sans-pose" in sys.argv
                  or os.environ.get("ASCENSIONFR_SANS_POSE") == "1")
    import subprocess
    ici = os.path.dirname(os.path.abspath(__file__))
    # 1. re-rendre DB_Objets paresseux après toute régénération (#33).
    if _sans_pose:
        raise SystemExit(code)
    try:
        subprocess.run([sys.executable,
                        os.path.join(ici, "optimiser_memoire.py")],
                       check=False)
    except Exception as e:
        print("! optimiser_memoire : %s" % e)
    # 2. re-graver le nombre EXACT de textes (DB_Meta.lua) — APRÈS la mise en
    #    paresseux, pour compter sur les bases dans leur forme finale. Sinon
    #    le total affiché par le Hub se figerait sur l'ancienne fabrication.
    try:
        subprocess.run([sys.executable,
                        os.path.join(ici, "compter_total.py"), "--ecrire"],
                       check=False)
    except Exception as e:
        print("! compter_total : %s" % e)
    raise SystemExit(code)
