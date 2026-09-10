# -*- coding: utf-8 -*-
"""
recuperer_db.py — récolte le texte anglais des sorts/objets depuis
db.ascension.gg (API « power » par ID) et en génère des corrections FR.

POURQUOI
--------
Notre goulot n'est PAS la traduction (traduire_gisement tourne déjà) mais la
récupération du texte anglais SOURCE + son ID, un par un, via les rapports
joueurs (lent). Or db.ascension.gg expose, SANS login, pour chaque ID :

    https://db.ascension.gg/?spell=ID&power  -> registerSpell(..., tooltip_enus, buff_enus, ...)
    https://db.ascension.gg/?item=ID&power   -> registerItem(...,  tooltip_enus, ...)

On y prend le texte anglais, on le traduit (pipeline existant) et on écrit des
corrections dans DB_SortsCorrections.lua — comme ingerer_rapport.py, mais sans
que le joueur ait à coller quoi que ce soit : l'ID suffit.

RÔLES (db.ascension.gg vs rapports joueurs)
-------------------------------------------
- Rapports joueurs = PRÉCISION : le texte live autoritatif du serveur (Rexxar).
- db.ascension.gg   = LARGEUR   : pré-remplir en masse, y compris les archétypes
  que personne n'a signalés.

ATTENTION : la base du site peut DIVERGER du serveur live. Exemple vérifié, le
sort 91796 : le site dit « Reduces the fall damage in this zone by 100%! » quand
le jeu affiche « 100% reduced fall damage in this zone! ». On n'ÉCRASE donc
JAMAIS le modèle principal :
  - sort DÉJÀ connu (dans DB_Sorts) -> on AJOUTE un 2e modèle via aura(). Un
    modèle en plus ne peut qu'AIDER l'alignement ; s'il ne matche pas, repli
    anglais SÛR (jamais de texte cassé).
  - sort INCONNU -> entrée neuve DB[id]={...}, nom laissé en anglais (on ne
    devine pas un nom par traduction machine), description traduite.

LIMITE (assumée, identique à ingerer_rapport)
---------------------------------------------
L'API donne des nombres RÉSOLUS (« 100% ») et non les gabarits $s1. Parfait pour
les textes FIXES (buffs de zone, talents à effet plat, objets). Pour un sort dont
la valeur dépend du perso, le modèle ne vaut que pour cette valeur -> repli
anglais sûr sinon.

USAGE
-----
    python outils/recuperer_db.py --echecs              # IDs des « Échecs S » de rapports/rapport.txt
    python outils/recuperer_db.py --ids 300916,800999
    python outils/recuperer_db.py --fichier ids.txt     # un ID par ligne (# = commentaire)
    python outils/recuperer_db.py --objets --ids 6948   # traite les IDs comme des OBJETS
    ... --dry            # prévisualise, n'écrit RIEN
    ... --limite 50      # ne traite que les N premiers (utile pour mesurer le taux en jeu)
    ... --pause 0.6      # secondes entre requêtes réseau (défaut 0.4 ; le cache évite de re-fetch)
"""
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from traduire_gisement import traduire  # noqa: E402  (Google + glossaire WoW)
from chemin_client import JEU, exiger_client  # noqa: E402

DBDIR = os.path.join(JEU, "Interface", "AddOns", "AscensionFR", "DB")
DB_SORTS = os.path.join(DBDIR, "DB_Sorts.lua")
CORRECTIONS = os.path.join(DBDIR, "DB_SortsCorrections.lua")
DOSSIER_RAPPORTS = os.path.join(BASE, "rapports")
CACHE = os.path.join(BASE, "cache_db")
BASEURL = "https://db.ascension.gg/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AscensionFR-trad/1.0"

RE_BLOB = re.compile(r"register(?:Spell|Item)\(\s*\d+\s*,\s*\d+\s*,\s*(\{.*\})\s*\)\s*;", re.S)
RE_TABLE = re.compile(r"<table.*?</table>", re.S | re.I)
RE_NOM = re.compile(r"<b[^>]*>(.*?)</b>", re.S | re.I)
RE_COMMENT = re.compile(r"<!--.*?-->", re.S)
RE_BR = re.compile(r"<br\s*/?>", re.I)
RE_TAG = re.compile(r"<[^>]+>")


# --------------------------------------------------------------------------- #
# Réseau (avec cache disque : un ID connu n'est jamais re-téléchargé)
# --------------------------------------------------------------------------- #
def fetch(genre, id_, pause):
    """genre = 'spell' | 'item'. Renvoie le corps brut, ou None. Met en cache."""
    os.makedirs(CACHE, exist_ok=True)
    cache = os.path.join(CACHE, "%s_%s.txt" % (genre, id_))
    if os.path.exists(cache):
        with open(cache, encoding="utf-8") as f:
            return f.read()
    url = "%s?%s=%s&power" % (BASEURL, genre, id_)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            corps = r.read().decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError) as e:
        print("  ! réseau %s %s : %s" % (genre, id_, e))
        return None
    time.sleep(pause)  # politesse : on ne martèle pas leur serveur
    with open(cache, "w", encoding="utf-8") as f:
        f.write(corps)
    return corps


def donnees(corps):
    """Extrait l'objet JSON de $WowheadPower.registerSpell/Item(id, 0, {...})."""
    m = RE_BLOB.search(corps or "")
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


# --------------------------------------------------------------------------- #
# Nettoyage HTML -> texte
# --------------------------------------------------------------------------- #
def nettoyer(h):
    """HTML d'info-bulle -> texte plat (les <br> deviennent des sauts de ligne)."""
    if not h:
        return ""
    h = RE_COMMENT.sub("", h)
    h = RE_BR.sub("\n", h)
    h = RE_TAG.sub("", h)
    h = html.unescape(h)
    # Le site colle des &nbsp; (« 10&nbsp;sec ») ; le jeu, lui, affiche des
    # espaces normales — et le %s de Lua ne reconnaît PAS l'insécable :
    # chaque modèle qui en garde une ne s'alignerait jamais (vécu, 1 259
    # modèles morts sur la récolte des talents du 21/07/2026).
    h = h.replace("\xa0", " ").replace("\u202f", " ")
    lignes = [re.sub(r"[ \t]+", " ", ligne).strip() for ligne in h.split("\n")]
    return "\n".join(ligne for ligne in lignes if ligne).strip()


def description(tooltip):
    """Description = le corps de l'info-bulle, SANS la 1re table (nom + coût/TR).

    Les entrées de DB_Sorts stockent la description seule (pas le nom ni « Instant »)
    ; on écarte donc la table d'en-tête qui contient le <b>nom</b>."""
    blocs = RE_TABLE.findall(tooltip or "")
    if len(blocs) >= 2:
        corps = "".join(blocs[1:])
    elif blocs:
        corps = blocs[0]
    else:
        corps = tooltip or ""
    return nettoyer(corps)


def nom_anglais(tooltip, secours):
    m = RE_NOM.search(tooltip or "")
    return (nettoyer(m.group(1)) if m else "") or (secours or "")


def utile(texte):
    """Au moins 2 mots alphabétiques : sinon rien à traduire/aligner."""
    return len(re.findall(r"[A-Za-z]{2,}", texte or "")) >= 2


# --------------------------------------------------------------------------- #
# État existant (dédup)
# --------------------------------------------------------------------------- #
def ids_dans_db_sorts():
    ids = set()
    with open(DB_SORTS, encoding="utf-8") as f:
        for ligne in f:
            m = re.match(r"^DB\[(\d+)\]=", ligne)
            if m:
                ids.add(m.group(1))
    return ids


def ids_deja_corriges():
    if not os.path.exists(CORRECTIONS):
        return set()
    with open(CORRECTIONS, encoding="utf-8") as f:
        contenu = f.read()
    return (set(re.findall(r"^DB\[(\d+)\]=", contenu, re.M))
            | set(re.findall(r"aura\((\d+),", contenu)))


def echapper_lua(s):
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return s.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")


# --------------------------------------------------------------------------- #
# Sources d'IDs
# --------------------------------------------------------------------------- #
def ids_echecs(genre="S"):
    """IDs listés sous « --- Échecs d'alignement <genre> » dans TOUS les .txt du
    dossier rapports/ (dépose les fichiers téléchargés de Discord tels quels).
    ids_*.txt est exclu : listes d'IDs de recolter_builder, pas des rapports."""
    if not os.path.isdir(DOSSIER_RAPPORTS):
        return []
    marqueur = "--- Échecs d'alignement " + genre
    ids = []
    for nom in sorted(os.listdir(DOSSIER_RAPPORTS)):
        if not nom.lower().endswith(".txt") or nom.lower().startswith("ids_"):
            continue
        dans = False
        with open(os.path.join(DOSSIER_RAPPORTS, nom), encoding="utf-8") as f:
            for ligne in f:
                if ligne.startswith(marqueur):
                    dans = True
                    continue
                if ligne.startswith("---"):
                    dans = False
                    continue
                if dans:
                    m = re.match(r"^(\d+)\s*:", ligne)
                    if m:
                        ids.append(m.group(1))
    return ids


def opt(args, nom, defaut=None):
    if nom in args:
        i = args.index(nom)
        if i + 1 < len(args):
            return args[i + 1]
    return defaut


def rassembler_ids(args):
    ids = []
    if "--echecs" in args:
        ids += ids_echecs("S")
    if "--ids" in args:
        ids += [x for x in re.split(r"[,\s]+", opt(args, "--ids", "")) if x.isdigit()]
    if "--fichier" in args:
        chemin = opt(args, "--fichier", "")
        if chemin and os.path.exists(chemin):
            with open(chemin, encoding="utf-8") as f:
                for ligne in f:
                    ligne = ligne.split("#", 1)[0].strip()
                    if ligne.isdigit():
                        ids.append(ligne)
    vus = set()
    return [i for i in ids if not (i in vus or vus.add(i))]  # dédup, ordre gardé


# --------------------------------------------------------------------------- #
def main():
    # DB_Sorts.lua (lecture SANS garde) et DB_SortsCorrections.lua (append
    # final) vivent chez le client : sans lui, on s'arrête AVANT de
    # dépenser un appel réseau (programme 31, bloc A).
    exiger_client("recuperer_db (sous-étape des signalements)")
    args = sys.argv[1:]
    dry = "--dry" in args
    genre = "item" if "--objets" in args else "spell"
    pause = float(opt(args, "--pause", "0.4"))

    if genre == "item" and not dry:
        # Les objets ont leur propre base (DB_Objets.lua), avec d'autres champs,
        # et un ID d'objet ≠ un ID de sort : écrire un objet dans DB.Sorts la
        # corromprait. L'écriture objets n'est pas encore câblée -> aperçu seul.
        print("--objets : aperçu à blanc forcé (l'écriture objets viendra dans une v2).")
        dry = True

    ids = rassembler_ids(args)
    limite = opt(args, "--limite")
    if limite:
        ids = ids[:int(limite)]
    if not ids:
        print("Aucun ID. Utilise --echecs, --ids 300916,800999 ou --fichier ids.txt.")
        return 1

    en_db = ids_dans_db_sorts() if genre == "spell" else set()
    deja = ids_deja_corriges()
    print("IDs demandés : %d | déjà corrigés (ignorés) : %d"
          % (len(ids), len([i for i in ids if i in deja])))

    def ecrire(lignes, premier=[True]):
        """Ajoute les lignes au fichier de corrections, immédiatement.

        Sur des milliers de sorts, ce travail dure des heures : tout garder en
        mémoire jusqu'à la fin, c'est TOUT perdre à la moindre coupure (vécu
        le 19/07/2026 — 3 135 sorts traduits envolés). On écrit donc par
        paquets, quitte à ouvrir le fichier plus souvent."""
        if not lignes:
            return
        entete = ""
        if premier[0]:
            contenu = ""
            if os.path.exists(CORRECTIONS):
                with open(CORRECTIONS, encoding="utf-8") as f:
                    contenu = f.read()
            if "local function aura(" not in contenu:
                entete = ("local DB = AscensionFR.DB.Sorts\n"
                          "local function aura(id, de2, d2)\n"
                          "    if DB[id] then DB[id].DE2 = de2;"
                          " DB[id].D2 = d2 end\n"
                          "end\n")
            entete = ("\n-- --- Récolté depuis db.ascension.gg "
                      "(recuperer_db.py) ---\n" + entete)
            premier[0] = False
        with open(CORRECTIONS, "a", encoding="utf-8") as f:
            f.write(entete + "\n".join(lignes) + "\n")

    lignes, n_aura, n_neuf, ecrites = [], 0, 0, 0
    for id_ in ids:
        if id_ in deja:
            continue
        d = donnees(fetch(genre, id_, pause))
        if not d:
            print("  ! %s %s : pas de données (ID inconnu du site ?)" % (genre, id_))
            continue
        tooltip = d.get("tooltip_enus", "")
        desc = description(tooltip)
        buff = nettoyer(d.get("buff_enus", ""))

        if genre == "spell" and id_ in en_db:
            # Sort connu : on ajoute un 2e modèle (l'aura d'abord, sinon la desc).
            en = buff or desc
            if not utile(en):
                print("  · %s : rien d'utile à ajouter" % id_)
                continue
            fr = traduire(en)
            if not fr:
                print("  ! %s : traduction échouée" % id_)
                continue
            lignes.append('aura(%s, "%s", "%s")' % (id_, echapper_lua(en), echapper_lua(fr)))
            n_aura += 1
            print("  +aura %s  %s" % (id_, en.split("\n")[0][:52]))
        else:
            # Inconnu : entrée neuve. Description traduite, nom laissé en anglais.
            if not utile(desc):
                print("  · %s : pas de description exploitable" % id_)
                continue
            fr = traduire(desc)
            if not fr:
                print("  ! %s : traduction échouée" % id_)
                continue
            nom = nom_anglais(tooltip, d.get("name_enus", ""))
            lignes.append('DB[%s]={D="%s",DE="%s",N="%s"}'
                          % (id_, echapper_lua(fr), echapper_lua(desc), echapper_lua(nom)))
            if buff and utile(buff) and buff != desc:
                bf = traduire(buff)
                if bf:
                    lignes.append('aura(%s, "%s", "%s")' % (id_, echapper_lua(buff), echapper_lua(bf)))
            n_neuf += 1
            print("  +neuf %s  %s" % (id_, (nom or desc).split("\n")[0][:52]))

        # Sauvegarde par paquets : au pire on perd les 30 derniers sorts.
        if not dry and len(lignes) >= 30:
            ecrire(lignes)
            ecrites += len(lignes)
            lignes = []

    print("\n2e modèles (aura) : %d | entrées neuves : %d" % (n_aura, n_neuf))
    if dry:
        print("--dry : rien écrit. %d ligne(s) Lua prêtes." % len(lignes))
        return 0
    ecrire(lignes)
    ecrites += len(lignes)
    if not ecrites:
        return 0
    print("%d ligne(s) ajoutée(s) à DB_SortsCorrections.lua." % ecrites)
    print("Vérifie la syntaxe (lupa), puis /reload en jeu pour tester le taux d'alignement.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
