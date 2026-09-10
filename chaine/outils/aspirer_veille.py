# -*- coding: utf-8 -*-
"""
aspirer_veille.py — aspire le TEXTE des messages écrits par les joueurs dans les
salons humains du Discord AscensionFR (fils de forum compris) vers
D:\\AscensionFR\\3-atelier\\veille-discord\\.

À NE PAS CONFONDRE avec aspirer_discord.py : celui-là télécharge les PIÈCES
JOINTES d'un seul salon (#rapports-auto) pour le pipeline de traduction. Ici on
fait l'inverse — la parole des joueurs, dans plusieurs salons, en clair. Les
deux outils sont indépendants et ne s'écrivent jamais dessus.

À QUOI ÇA SERT
--------------
  Relire chaque soir ce que les joueurs disent à la main, pour en sortir :
  les idées et demandes de fonctions, les bugs et blocages d'installation,
  les fautes de traduction signalées en discussion (invisibles dans les
  rapports du Compagnon), et les questions qui reviennent (-> FAQ).

USAGE
-----
  python outils/aspirer_veille.py --tout          première passe : tout
                                                  l'historique -> historique\\
  python outils/aspirer_veille.py                 passage normal : uniquement
                                                  les nouveaux messages
                                                  -> AAAA-MM-JJ_nouveau.md
  python outils/aspirer_veille.py --redecouvrir   refaire l'appariement des
                                                  salons par nom
  python outils/aspirer_veille.py --planifier     (ré)installe la tâche Windows
                                                  ET le raccourci du Bureau
  python outils/aspirer_veille.py --pause         garde la fenêtre ouverte à la
                                                  fin (c'est ce que fait le
                                                  raccourci du Bureau)

QUAND ÇA TOURNE
---------------
  Deux déclenchements, sur UNE seule tâche : à l'ouverture de session (avec
  3 minutes de délai, le temps que le réseau se lève) et tous les jours à
  18 h 45. Le PC de Dan est souvent éteint à 18 h 45 ; le rapport qui lit
  cette récolte est calé à 16 h 00, donc la matière doit être fraîche dès
  l'allumage. Le passage de 18 h 45 reste comme filet pour les jours où le PC
  s'allume tard ou ne s'éteint pas.

  Deux passages dans la même journée ne font pas de dégât : le second voit
  les marque-pages déjà avancés, ne trouve rien de neuf et n'écrit AUCUN
  fichier (il dit « Rien de nouveau »).

CONFIDENTIALITÉ
---------------
  Le jeton est LU dans WorkFlow/discord_aspirateur.json et n'est jamais recopié
  ailleurs. Les fichiers produits contiennent des pseudos : ils sont STRICTEMENT
  LOCAUX (3-atelier/ est hors du dépôt git). Ne jamais recopier un pseudo dans
  un texte public.
"""
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

# Lancé par la tâche planifiée, ce script tourne sous pythonw.exe, donc SANS
# console. Or un processus sans console qui démarre une application console
# (powershell) force Windows à lui en allouer une NEUVE : une fenêtre noire
# surgit et vole le focus — elle éjecte d'un jeu en plein écran. capture_output
# redirige les FLUX, pas la FENÊTRE : seul CREATE_NO_WINDOW l'empêche.
# getattr et pas subprocess.CREATE_NO_WINDOW en direct : la constante n'existe
# que sur Windows. Ailleurs on retombe sur 0, que subprocess accepte partout
# (il ne refuse creationflags hors Windows que si la valeur est NON NULLE).
SANS_FENETRE = getattr(subprocess, "CREATE_NO_WINDOW", 0)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(BASE, "discord_aspirateur.json")
# Les données de veille vivent à côté des autres retours joueurs, hors dépôt.
VEILLE = os.path.join(os.path.dirname(BASE), "3-atelier", "veille-discord")
HISTORIQUE = os.path.join(VEILLE, "historique")
ETAT = os.path.join(VEILLE, "_etat.json")
INDEX = os.path.join(VEILLE, "_INDEX.md")
JOURNAL = os.path.join(VEILLE, "_journal.log")
JOURNAL_MAX = 1_000_000

API = "https://discord.com/api/v10"
UA = "AscensionFR-Veille/1.0"
PAUSE = 0.3          # souffle entre deux appels, pour ne pas fâcher Discord
ESSAIS_429 = 3

ENTETE_LOCAL = ("<!-- LOCAL UNIQUEMENT — ne jamais recopier un pseudo dans un "
                "texte public -->")

# Salons voulus : clé = nom normalisé accepté, valeur = étiquette lisible.
# Le salon « addon_glayna » (ex-« craft-addon ») a été retiré le 28/07/2026
# (décision de Dan : plus rien de Glayna dans AscensionFR, jusqu'à nouvel
# ordre). Son historique aspiré reste dans 3-atelier/veille-discord.
VOULUS = [
    ("signalements", ["signalements"]),
    ("suggestion", ["suggestion", "suggestions"]),
    ("installation", ["installation"]),
    ("discussion", ["discussion"]),
]

TYPES_FIL = (10, 11, 12)     # fils d'annonce / publics / privés
TYPE_FORUM = 15


def sortie_utf8():
    """La console de Windows est en cp1252 : sans ça, afficher un nom de salon
    avec un emoji (💡suggestion) fait planter le script — et la tâche planifiée
    mourrait en silence."""
    for flux in (sys.stdout, sys.stderr):
        try:
            flux.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def dire(message):
    print(message)
    noter(message)


def noter(message):
    """Journal des passages, avec rotation simple à ~1 Mo."""
    try:
        os.makedirs(VEILLE, exist_ok=True)
        if os.path.exists(JOURNAL) and os.path.getsize(JOURNAL) > JOURNAL_MAX:
            vieux = JOURNAL + ".1"
            if os.path.exists(vieux):
                os.remove(vieux)
            os.replace(JOURNAL, vieux)
        with open(JOURNAL, "a", encoding="utf-8") as f:
            f.write("[%s] %s\n"
                    % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message))
    except Exception:
        pass          # le journal ne doit jamais faire échouer la collecte


# --------------------------------------------------------------------------
# Discord
# --------------------------------------------------------------------------

class ErreurSalon(Exception):
    """Erreur rattachée à UN salon : on la raconte en nommant le salon."""


def api_get(chemin, jeton):
    """Appel GET, avec respect des limites de débit (HTTP 429)."""
    for essai in range(ESSAIS_429):
        req = urllib.request.Request(API + chemin, headers={
            "Authorization": "Bot " + jeton, "User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                donnees = json.load(r)
            time.sleep(PAUSE)
            return donnees
        except urllib.error.HTTPError as e:
            if e.code != 429 or essai == ESSAIS_429 - 1:
                raise
            attente = 5.0
            try:
                attente = float(json.load(e).get("retry_after", 5.0))
            except Exception:
                pass
            attente = min(max(attente, 0.5), 60.0)
            print("   … Discord demande de patienter %.1f s" % attente)
            time.sleep(attente)
    raise RuntimeError("429 répété")


def charger_config():
    if not os.path.exists(CONFIG):
        dire("! Configuration absente : %s" % CONFIG)
        dire("  Lance d'abord « python outils/aspirer_discord.py » : il crée le "
             "modèle et explique quoi remplir.")
        return None
    with open(CONFIG, encoding="utf-8") as f:
        cfg = json.load(f)
    if not cfg.get("jeton") or not cfg.get("salon"):
        dire("! Configuration incomplète (« jeton » et « salon ») dans %s"
             % CONFIG)
        return None
    return cfg


# --------------------------------------------------------------------------
# Trouver les salons tout seul
# --------------------------------------------------------------------------

def normaliser(nom):
    """« 💡suggestion » -> « suggestion ». On enlève les emojis, les accents,
    la ponctuation, les tirets, les espaces : il ne reste que des lettres et
    des chiffres en minuscules."""
    nom = unicodedata.normalize("NFKD", nom or "")
    nom = "".join(c for c in nom if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", nom.lower())


def nom_fichier(nom):
    """Nom de fichier lisible et sans surprise (les emojis sautent)."""
    nom = unicodedata.normalize("NFKD", nom or "")
    nom = "".join(c for c in nom if not unicodedata.combining(c))
    nom = re.sub(r"[^A-Za-z0-9_-]+", "-", nom).strip("-_")
    return (nom or "salon")[:60]


def decouvrir(cfg):
    """Part du salon déjà connu -> le serveur -> tous les salons, puis apparie
    par nom normalisé. Retourne (guild_id, {id: {"nom":…, "type":…}})."""
    salon = api_get("/channels/%s" % cfg["salon"], cfg["jeton"])
    guild = salon.get("guild_id")
    if not guild:
        raise RuntimeError("Le salon de référence n'appartient à aucun serveur.")
    tous = api_get("/guilds/%s/channels" % guild, cfg["jeton"])

    trouves, manquants = {}, []
    for etiquette, graphies in VOULUS:
        candidats = [c for c in tous
                     if normaliser(c.get("name")) in graphies
                     and c.get("type") in (0, 5, TYPE_FORUM)]
        if len(candidats) == 1:
            c = candidats[0]
            trouves[c["id"]] = {"nom": c.get("name"), "type": c.get("type"),
                                "etiquette": etiquette}
        else:
            manquants.append((etiquette, [c.get("name") for c in candidats]))

    for etiquette, vus in manquants:
        if vus:
            dire("! « %s » : %d salons possibles (%s). Je ne devine pas : "
                 "précise lequel." % (etiquette, len(vus), ", ".join(vus)))
        else:
            dire("! « %s » : aucun salon de ce nom (renommé ? bot non invité ?)."
                 % etiquette)
    return guild, trouves


def charger_etat():
    if os.path.exists(ETAT):
        with open(ETAT, encoding="utf-8") as f:
            return json.load(f)
    return {"guild": "", "salons": {}, "derniers": {}, "fils": {}}


def sauver_etat(etat):
    os.makedirs(VEILLE, exist_ok=True)
    with open(ETAT, "w", encoding="utf-8") as f:
        json.dump(etat, f, ensure_ascii=False, indent=1)


def salons_a_lire(cfg, etat, redecouvrir):
    """Les identifiants font foi ; les noms ne servent qu'à la découverte.
    Un salon renommé continue d'être lu, et le changement est noté."""
    if redecouvrir or not etat.get("salons"):
        guild, trouves = decouvrir(cfg)
        etat["guild"] = guild
        # On garde les anciens salons épinglés : un salon devenu introuvable par
        # son nom reste lisible par son identifiant.
        for cid, info in trouves.items():
            etat.setdefault("salons", {})[cid] = info
        return guild, etat["salons"]

    guild = etat.get("guild") or ""
    # Vérification légère : le salon a-t-il changé de nom depuis la découverte ?
    for cid, info in list(etat["salons"].items()):
        try:
            actuel = api_get("/channels/%s" % cid, cfg["jeton"]).get("name")
        except Exception:
            continue
        if actuel and actuel != info.get("nom"):
            dire("  (le salon « %s » s'appelle maintenant « %s » — je continue "
                 "sur son identifiant)" % (info.get("nom"), actuel))
            info["nom"] = actuel
    return guild, etat["salons"]


# --------------------------------------------------------------------------
# Ramener les messages
# --------------------------------------------------------------------------

def messages_apres(cid, depuis, jeton, quoi):
    """Tous les messages de `cid` postérieurs à `depuis`, du plus ancien au plus
    récent. On remonte le temps par pages de 100 (paramètre `before`, dont le
    comportement est sans ambiguïté), puis on retourne la liste à l'endroit.
    Lève ErreurSalon en nommant `quoi` si Discord refuse."""
    depuis = int(depuis or 0)
    recoltes, avant = [], None
    while True:
        chemin = "/channels/%s/messages?limit=100" % cid
        if avant:
            chemin += "&before=%s" % avant
        try:
            page = api_get(chemin, jeton)
        except urllib.error.HTTPError as e:
            if e.code == 403:
                raise ErreurSalon("accès refusé (403) sur « %s » : donne au bot "
                                  "« Voir le salon » + « Lire l'historique des "
                                  "messages »" % quoi)
            if e.code == 404:
                raise ErreurSalon("« %s » introuvable (404) : supprimé ?" % quoi)
            if e.code == 401:
                raise ErreurSalon("jeton refusé (401) : recopie le jeton du bot")
            raise ErreurSalon("« %s » : Discord répond HTTP %d" % (quoi, e.code))
        if not page:
            break
        fini = False
        for m in page:
            if int(m["id"]) <= depuis:
                fini = True
                continue
            recoltes.append(m)
        if fini or len(page) < 100:
            break
        avant = min(m["id"] for m in page)
    recoltes.sort(key=lambda m: int(m["id"]))
    return recoltes


def fils_du_salon(cid, guild, jeton, actifs_du_serveur):
    """Les fils d'un forum (ou d'un salon texte) : actifs + archivés publics.
    Un forum n'a AUCUN message en propre — tout est dans ses fils."""
    fils = {f["id"]: f for f in actifs_du_serveur if f.get("parent_id") == cid}

    avant = None
    while True:
        chemin = "/channels/%s/threads/archived/public?limit=100" % cid
        if avant:
            chemin += "&before=%s" % urllib.parse.quote(avant)
        try:
            rep = api_get(chemin, jeton)
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                break        # pas de fils archivés lisibles ici : tant pis
            raise
        lot = rep.get("threads", [])
        for f in lot:
            fils.setdefault(f["id"], f)
        if not rep.get("has_more") or not lot:
            break
        avant = (lot[-1].get("thread_metadata", {}) or {}).get(
            "archive_timestamp")
        if not avant:
            break
    return list(fils.values())


# --------------------------------------------------------------------------
# Mise en forme
# --------------------------------------------------------------------------

def est_bot(m):
    auteur = m.get("author") or {}
    return bool(auteur.get("bot")) or bool(m.get("webhook_id"))


def quand(m):
    """Horodatage Discord (UTC) -> heure locale de Dan, lisible."""
    try:
        d = datetime.fromisoformat(m["timestamp"])
        return d.astimezone().strftime("%Y-%m-%d %H:%M")
    except Exception:
        return (m.get("timestamp") or "")[:16].replace("T", " ")


def pseudo(m):
    auteur = m.get("author") or {}
    return (auteur.get("global_name") or auteur.get("username")
            or "inconnu")


# --- pièces jointes TEXTE (programme 32, bloc A — demande du 02/08) -------
# Un long signalement (> 2 000 caractères) devient un message.txt : la
# veille écrivait « [fichier : message.txt] » et le contenu n'était JAMAIS
# lu — 40 signalements aveugles entre le 27/07 et le 07/08, les retours les
# plus détaillés du projet. On lit désormais le texte, et RIEN QUE le
# texte : petit, tronqué avec une marque visible, et un échec réseau ne
# casse jamais la passe (étiquette « non téléchargé » à la place — jamais
# d'exception, jamais de donnée écrasée).
EXT_TEXTE = (".txt", ".md", ".log")
PJ_MAX_OCTETS = 200_000       # ~10 × le plus gros message.txt vu
PJ_TRONQUE_A = 8_000          # caractères gardés dans le rapport
BILAN_PJ = {"vues": 0, "lues": 0, "illisibles": 0, "autres": 0}


def est_texte(pj):
    genre = (pj.get("content_type") or "").lower()
    nom = (pj.get("filename") or "").lower()
    return (genre.startswith("text/")
            or nom.endswith(EXT_TEXTE)) and \
        0 < pj.get("size", 0) <= PJ_MAX_OCTETS


def piece_texte(pj):
    """Le CONTENU d'une pièce jointe texte, borné et marqué — ou l'étiquette
    de repli si le téléchargement échoue."""
    nom = pj.get("filename", "?")
    BILAN_PJ["vues"] += 1
    try:
        req = urllib.request.Request(pj["url"], headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            brut = r.read(PJ_MAX_OCTETS + 1)
        texte = brut.decode("utf-8", errors="replace").strip()
        if len(texte) > PJ_TRONQUE_A:
            texte = texte[:PJ_TRONQUE_A] + "\n[… tronqué]"
        BILAN_PJ["lues"] += 1
        return "[fichier texte : %s]\n%s" % (nom, texte)
    except Exception as e:
        BILAN_PJ["illisibles"] += 1
        return "[fichier : %s — non téléchargé (%s)]" % (
            nom, str(e)[:60])


def corps(m):
    """Le texte du message, ou une étiquette quand il n'y en a pas."""
    texte = (m.get("content") or "").strip()
    if texte:
        return texte
    if m.get("sticker_items"):
        return "[sticker]"
    for pj in m.get("attachments") or []:
        genre = (pj.get("content_type") or "").lower()
        if genre.startswith("image/"):
            return "[image]"
        if genre.startswith("video/"):
            return "[vidéo]"
        if est_texte(pj):
            return piece_texte(pj)
        BILAN_PJ["autres"] += 1
        return "[fichier : %s]" % pj.get("filename", "?")
    if m.get("embeds"):
        return "[intégration]"
    return "[message sans texte]"


def ligne(m, guild, cid):
    """Une ligne de message, lisible d'un coup d'œil et traçable."""
    texte = corps(m).replace("\r", "")
    lignes = texte.split("\n")
    out = ["- [%s] **%s** — %s" % (quand(m), pseudo(m), lignes[0])]
    out += ["  %s" % l for l in lignes[1:] if l.strip()]

    ref = m.get("referenced_message")
    if ref:
        extrait = (ref.get("content") or corps(ref)).replace("\n", " ").strip()
        if len(extrait) > 90:
            extrait = extrait[:90] + "…"
        out.append("  ↳ en réponse à %s : « %s »" % (pseudo(ref), extrait))
    out.append("  (https://discord.com/channels/%s/%s/%s)"
               % (guild, cid, m["id"]))
    return "\n".join(out)


def bloc_source(source, messages, guild, niveau="##"):
    """Un salon ou un fil, avec ses messages."""
    if not messages:
        return ""
    morceaux = ["%s %s" % (niveau, source["titre"]), ""]
    morceaux += [ligne(m, guild, source["id"]) for m in messages]
    morceaux.append("")
    return "\n".join(morceaux)


def ecrire(chemin, contenu, mode="w"):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, mode, encoding="utf-8", newline="\n") as f:
        f.write(contenu)


# --------------------------------------------------------------------------
# Collecte
# --------------------------------------------------------------------------

def collecter(cfg, etat, salons, guild, tout):
    """Ramène les messages de chaque salon et de chaque fil.

    Retourne (recolte, soucis). `recolte` : liste de salons, chacun avec ses
    « sources » (le salon lui-même et/ou ses fils) et leurs messages.

    Le marque-page d'une source n'avance QUE si elle a été entièrement
    récupérée : un hoquet réseau ne doit jamais faire sauter un message pour
    toujours (même règle que aspirer_discord.py).
    """
    jeton = cfg["jeton"]
    soucis = []
    try:
        actifs = api_get("/guilds/%s/threads/active" % guild,
                         jeton).get("threads", [])
    except Exception as e:
        actifs = []
        soucis.append("fils actifs illisibles (%s)" % e)

    recolte = []
    for cid, info in salons.items():
        nom = info.get("nom") or cid
        entree = {"id": cid, "nom": nom, "type": info.get("type"),
                  "etiquette": info.get("etiquette", nom_fichier(nom)),
                  "sources": []}
        sources = []

        # Un forum n'a pas de message en propre ; un salon texte, si.
        if info.get("type") != TYPE_FORUM:
            sources.append({"id": cid, "titre": nom, "fil": False})

        try:
            fils = fils_du_salon(cid, guild, jeton, actifs)
        except Exception as e:
            fils = []
            soucis.append("fils de « %s » illisibles (%s)" % (nom, e))
        for f in fils:
            if f.get("type") in TYPES_FIL or info.get("type") == TYPE_FORUM:
                sources.append({"id": f["id"],
                                "titre": f.get("name") or f["id"],
                                "fil": True})

        for src in sources:
            depuis = 0 if tout else int(etat["derniers"].get(src["id"], 0) or 0)
            try:
                msgs = messages_apres(src["id"], depuis, jeton,
                                      "%s / %s" % (nom, src["titre"])
                                      if src["fil"] else nom)
            except ErreurSalon as e:
                soucis.append(str(e))
                continue          # marque-page inchangé : on réessaiera
            except Exception as e:
                soucis.append("« %s » : %s (repris au prochain passage)"
                              % (src["titre"], e))
                continue
            src["messages"] = msgs
            src["complet"] = True
            entree["sources"].append(src)

        if entree["sources"]:
            recolte.append(entree)
    return recolte, soucis


def compter(recolte):
    """(messages retenus, ignorés bots/webhooks) après filtrage."""
    gardes = ignores = 0
    for salon in recolte:
        for src in salon["sources"]:
            humains = [m for m in src["messages"] if not est_bot(m)]
            ignores += len(src["messages"]) - len(humains)
            src["messages"] = humains
            gardes += len(humains)
    return gardes, ignores


def controle_intent(recolte, brut_total):
    """Des messages ramenés mais tous vides = l'intent MESSAGE CONTENT manque."""
    avec_texte = sum(1 for s in recolte for src in s["sources"]
                     for m in src["messages"] if (m.get("content") or "").strip())
    if brut_total >= 5 and avec_texte == 0:
        dire("")
        dire("! Tous les messages reviennent SANS texte : l'intent « MESSAGE "
             "CONTENT » n'est pas activé.")
        dire("  discord.com/developers -> ton application -> Bot ->")
        dire("  Privileged Gateway Intents -> MESSAGE CONTENT INTENT -> Save.")
        dire("  Je n'écris rien tant que ce n'est pas fait (fichiers vides "
             "inutiles).")
        return False
    return True


# --------------------------------------------------------------------------
# Écriture
# --------------------------------------------------------------------------

def dates_extremes(messages):
    if not messages:
        return "", ""
    return quand(messages[0])[:10], quand(messages[-1])[:10]


def ecrire_historique(recolte, guild):
    fiches = []
    for salon in recolte:
        chemin = os.path.join(HISTORIQUE,
                              "%s.md" % nom_fichier(salon["etiquette"]))
        blocs = [ENTETE_LOCAL, "",
                 "# %s" % salon["nom"], ""]
        total = 0
        detail = []
        for src in sorted(salon["sources"],
                          key=lambda s: (s["messages"][0]["id"]
                                         if s["messages"] else "0")):
            if not src["messages"]:
                continue
            blocs.append(bloc_source(src, src["messages"], guild))
            total += len(src["messages"])
            d1, d2 = dates_extremes(src["messages"])
            detail.append((src["titre"], len(src["messages"]), d1, d2,
                           src["fil"]))
        if total == 0:
            fiches.append({"salon": salon, "fichier": None, "total": 0,
                           "detail": [], "taille": 0})
            continue
        ecrire(chemin, "\n".join(blocs).rstrip() + "\n")
        fiches.append({"salon": salon, "fichier": chemin, "total": total,
                       "detail": detail,
                       "taille": os.path.getsize(chemin)})
    return fiches


def ecrire_index(fiches):
    lignes = [ENTETE_LOCAL, "",
              "# Veille Discord — carte des salons", "",
              "Dernière passe complète : %s"
              % datetime.now().strftime("%Y-%m-%d %H:%M"), ""]
    for f in fiches:
        salon = f["salon"]
        if not f["total"]:
            lignes.append("## %s\n\nAucun message.\n" % salon["nom"])
            continue
        lignes.append("## %s" % salon["nom"])
        lignes.append("")
        lignes.append("Fichier : `historique/%s` — %d message(s), %d fil(s), "
                      "%.0f Ko"
                      % (os.path.basename(f["fichier"]), f["total"],
                         sum(1 for d in f["detail"] if d[4]),
                         f["taille"] / 1024.0))
        lignes.append("")
        lignes.append("| Fil / salon | Messages | Du | Au |")
        lignes.append("|---|---:|---|---|")
        for titre, n, d1, d2, _fil in f["detail"]:
            lignes.append("| %s | %d | %s | %s |"
                          % (titre.replace("|", "/"), n, d1, d2))
        lignes.append("")
    ecrire(INDEX, "\n".join(lignes).rstrip() + "\n")


def ecrire_nouveautes(recolte, guild):
    """Le passage du jour : uniquement les nouveaux, groupés salon puis fil."""
    jour = datetime.now().strftime("%Y-%m-%d")
    chemin = os.path.join(VEILLE, "%s_nouveau.md" % jour)
    blocs = []
    for salon in recolte:
        avec = [s for s in salon["sources"] if s["messages"]]
        if not avec:
            continue
        blocs.append("## %s" % salon["nom"])
        blocs.append("")
        for src in avec:
            if src["fil"]:
                blocs.append(bloc_source(src, src["messages"], guild, "###"))
            else:
                blocs += [ligne(m, guild, src["id"]) for m in src["messages"]]
                blocs.append("")
    if not blocs:
        return None
    deja = os.path.exists(chemin)
    tete = ([] if deja else [ENTETE_LOCAL, "",
                             "# Nouveaux messages — %s" % jour, ""])
    tete.append("_Passage de %s_" % datetime.now().strftime("%H:%M"))
    tete.append("")
    ecrire(chemin, "\n".join(tete + blocs).rstrip() + "\n",
           "a" if deja else "w")
    return chemin


def avancer_marque_pages(recolte, etat):
    for salon in recolte:
        for src in salon["sources"]:
            if not src.get("complet") or not src.get("_dernier_brut"):
                continue
            etat["derniers"][src["id"]] = src["_dernier_brut"]
            if src["fil"]:
                etat.setdefault("fils", {})[src["id"]] = {
                    "salon": salon["id"], "titre": src["titre"]}


# --------------------------------------------------------------------------
# Tâche planifiée
# --------------------------------------------------------------------------

NOM_TACHE = "AscensionFR - Veille Discord"
NOM_RACCOURCI = "Aspirer la veille Discord.lnk"
# Le temps qu'on laisse au réseau après l'ouverture de session. Sans ce délai,
# la tâche partirait avant que Windows ait une connexion et mourrait sur un
# « Découverte des salons impossible » — un échec pour rien, invisible.
DELAI_OUVERTURE = "PT3M"


def powershell(commande):
    return subprocess.run(["powershell", "-NoProfile", "-NonInteractive",
                           "-Command", commande],
                          capture_output=True, text=True,
                          creationflags=SANS_FENETRE)


def _chemins_python():
    """(pythonw pour la tâche silencieuse, python pour la fenêtre du Bureau)."""
    dossier = os.path.dirname(sys.executable)
    pythonw = os.path.join(dossier, "pythonw.exe")
    return (pythonw if os.path.exists(pythonw) else sys.executable,
            sys.executable)


def poser_tache():
    """Une SEULE tâche, DEUX déclenchements : ouverture de session et 18 h 45.

    Une seule tâche et pas deux : un seul endroit où regarder, une seule
    action à corriger le jour où le chemin du script bouge, et la politique
    « IgnoreNew » empêche d'elle-même les deux déclenchements de se marcher
    dessus. Idempotent : la tâche est remplacée si elle existe déjà.
    """
    pythonw, _ = _chemins_python()
    script = os.path.abspath(__file__)
    ps = (
        "$a = New-ScheduledTaskAction -Execute '%s' -Argument '\"%s\"' "
        "-WorkingDirectory '%s';"
        "$t1 = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME;"
        "$t1.Delay = '%s';"
        "$t2 = New-ScheduledTaskTrigger -Daily -At 18:45;"
        "$s = New-ScheduledTaskSettingsSet -StartWhenAvailable "
        "-AllowStartIfOnBatteries -DontStopIfGoingOnBatteries "
        "-MultipleInstances IgnoreNew "
        "-ExecutionTimeLimit (New-TimeSpan -Hours 2);"
        "Register-ScheduledTask -TaskName '%s' -Action $a "
        "-Trigger @($t1, $t2) -Settings $s -Description 'Aspire le texte des "
        "salons humains du Discord AscensionFR vers "
        "3-atelier\\veille-discord. Deux departs : ouverture de session "
        "(+3 min) et 18h45.' -Force | Out-Null; 'OK'"
        % (pythonw, script, BASE, DELAI_OUVERTURE, NOM_TACHE)
    )
    r = powershell(ps)
    if r.returncode == 0:
        dire("Tâche « %s » installée : à l'ouverture de session (+3 min) ET "
             "chaque jour à 18 h 45." % NOM_TACHE)
        return True
    dire("! Installation de la tâche impossible : %s"
         % (r.stderr or r.stdout).strip()[:400])
    return False


def poser_raccourci():
    """Le raccourci du Bureau : un vrai .lnk, JAMAIS une copie du script.

    Une copie posée sur le Bureau ne voit pas les mises à jour du code — le
    piège déjà rencontré avec l'Atelier. Le raccourci vise `python.exe` (et
    non `pythonw.exe`) pour que la fenêtre s'ouvre, et passe `--pause` pour
    qu'elle RESTE ouverte : Dan doit pouvoir lire le compte des nouveaux
    messages, pas voir une fenêtre noire disparaître.
    """
    _, python = _chemins_python()
    script = os.path.abspath(__file__)
    ps = (
        "$b = [Environment]::GetFolderPath('Desktop');"
        "$w = New-Object -ComObject WScript.Shell;"
        "$l = $w.CreateShortcut((Join-Path $b '%s'));"
        "$l.TargetPath = '%s';"
        "$l.Arguments = '\"%s\" --pause';"
        "$l.WorkingDirectory = '%s';"
        "$l.Description = 'Aspire maintenant les nouveaux messages du "
        "Discord AscensionFR';"
        "$l.IconLocation = '%%SystemRoot%%\\System32\\shell32.dll,44';"
        "$l.Save();"
        "Join-Path $b '%s'"
        % (NOM_RACCOURCI, python, script, BASE, NOM_RACCOURCI)
    )
    r = powershell(ps)
    if r.returncode == 0:
        dire("Raccourci posé : %s" % (r.stdout or "").strip())
        return True
    dire("! Raccourci impossible : %s"
         % (r.stderr or r.stdout).strip()[:400])
    return False


def planifier():
    """Installe les deux : la tâche et le raccourci. Une seule commande."""
    ok_tache = poser_tache()
    ok_raccourci = poser_raccourci()
    return 0 if (ok_tache and ok_raccourci) else 1


# --------------------------------------------------------------------------

def main():
    sortie_utf8()
    args = sys.argv[1:]
    if "--planifier" in args:
        return planifier()

    tout = "--tout" in args
    redecouvrir = "--redecouvrir" in args or tout

    cfg = charger_config()
    if cfg is None:
        return 1
    os.makedirs(VEILLE, exist_ok=True)
    etat = charger_etat()
    etat.setdefault("derniers", {})
    etat.setdefault("salons", {})

    dire("Veille Discord — %s" % ("première passe (tout l'historique)" if tout
                                  else "passage normal"))
    try:
        guild, salons = salons_a_lire(cfg, etat, redecouvrir)
    except urllib.error.HTTPError as e:
        dire("! Discord répond HTTP %d à la découverte des salons." % e.code)
        return 1
    except Exception as e:
        dire("! Découverte des salons impossible : %s" % e)
        return 1

    if not salons:
        dire("! Aucun salon à lire. Vérifie que le bot est bien invité.")
        return 1
    for cid, info in salons.items():
        dire("  · %s (%s)" % (info.get("nom"),
                              "forum" if info.get("type") == TYPE_FORUM
                              else "salon texte"))

    if "--rattrapage" in args:
        brut = args[args.index("--rattrapage") + 1] \
            if args.index("--rattrapage") + 1 < len(args) else "2026-07-26"
        try:
            depuis_date = datetime.strptime(brut, "%Y-%m-%d")
        except ValueError:
            depuis_date = datetime(2026, 7, 26)
        return rattrapage(cfg, etat, salons, guild, depuis_date)

    recolte, soucis = collecter(cfg, etat, salons, guild, tout)

    # On mémorise l'identifiant du dernier message BRUT (bots compris) : sinon
    # une salve de messages de bot ferait reculer le marque-page.
    brut_total = 0
    for salon in recolte:
        for src in salon["sources"]:
            brut_total += len(src["messages"])
            src["_dernier_brut"] = (src["messages"][-1]["id"]
                                    if src["messages"] else
                                    etat["derniers"].get(src["id"]))

    if not controle_intent(recolte, brut_total):
        return 1

    gardes, ignores = compter(recolte)

    if tout:
        fiches = ecrire_historique(recolte, guild)
        ecrire_index(fiches)
        avancer_marque_pages(recolte, etat)
        sauver_etat(etat)
        dire("%d message(s) de joueurs écrits dans %s"
             % (gardes, HISTORIQUE))
        dire("%d message(s) de bot/webhook ignoré(s)." % ignores)
        dire("Carte : %s" % INDEX)
    else:
        if gardes == 0:
            avancer_marque_pages(recolte, etat)
            sauver_etat(etat)
            dire("Rien de nouveau. (%d message(s) de bot ignoré(s))" % ignores)
        else:
            chemin = ecrire_nouveautes(recolte, guild)
            avancer_marque_pages(recolte, etat)
            sauver_etat(etat)
            dire("%d nouveau(x) message(s) -> %s"
                 % (gardes, os.path.basename(chemin)))
            if ignores:
                dire("%d message(s) de bot/webhook ignoré(s)." % ignores)

    for s in soucis:
        dire("! %s" % s)
    dire_bilan_pj()
    return 0


def dire_bilan_pj():
    """Les comptes du passage (programme 32, bloc A) : la veille porte son
    @@BILAN comme les 7 étapes de l'Atelier — « tentées » = pièces jointes
    TEXTE vues, « traduites » = lues, « refusées » = illisibles, « écartées »
    = pièces non textuelles (images, vidéos…). Une passe qui voit dix
    pièces et n'en lit aucune ne peut pas être verte."""
    dire("@@BILAN " + json.dumps(
        {"tentees": BILAN_PJ["vues"], "traduites": BILAN_PJ["lues"],
         "refusees": BILAN_PJ["illisibles"],
         "ecartees": BILAN_PJ["autres"]}))


def snowflake(d):
    """L'identifiant Discord « à partir de » pour une date locale donnée."""
    epoque_discord = 1420070400000
    ms = int(d.timestamp() * 1000)
    return max(0, (ms - epoque_discord)) << 22


def rattrapage(cfg, etat, salons, guild, depuis_date):
    """Relit les salons depuis une date SANS toucher _etat.json, garde les
    seuls messages porteurs d'une pièce jointe texte, et range le tout dans
    RATTRAPAGE_pieces-jointes.md — à part des rapports déjà rendus
    (programme 32, bloc A : les 40 signalements aveugles)."""
    ombre = {"derniers": {}, "salons": etat.get("salons", {})}
    depuis = str(snowflake(depuis_date))
    recolte, soucis = collecter(cfg, ombre, salons, guild, tout=False)
    # collecter lit depuis ombre["derniers"] (vide = 0) : on refait le tri
    # nous-mêmes en ne gardant que les messages assez récents ET porteurs
    # d'une pièce jointe texte.
    gardes = 0
    for salon in recolte:
        for src in salon["sources"]:
            src["messages"] = [
                m for m in src["messages"]
                if not est_bot(m) and int(m["id"]) >= int(depuis)
                and any(est_texte(pj) for pj in m.get("attachments") or [])]
            gardes += len(src["messages"])
    chemin = os.path.join(VEILLE, "RATTRAPAGE_pieces-jointes.md")
    morceaux = [ENTETE_LOCAL, "",
                "# Rattrapage des pièces jointes texte — depuis le %s"
                % depuis_date.strftime("%Y-%m-%d"),
                "(généré le %s ; _etat.json non touché)"
                % datetime.now().strftime("%Y-%m-%d %H:%M"), ""]
    for salon in recolte:
        for src in salon["sources"]:
            if src["messages"]:
                titre = dict(src)
                titre["titre"] = "%s — %s" % (salon["nom"], src["titre"])
                morceaux.append(bloc_source(titre, src["messages"], guild))
    ecrire(chemin, "\n".join(morceaux))
    dire("%d message(s) à pièce jointe texte -> %s"
         % (gardes, os.path.basename(chemin)))
    for s in soucis:
        dire("! %s" % s)
    dire_bilan_pj()
    return 0


def _attendre_lecture():
    """Garde la fenêtre ouverte. Utilisé par le raccourci du Bureau.

    Volontairement dans le `__main__` et pas dans main() : la fenêtre doit
    rester ouverte AUSSI quand le script échoue — c'est même là qu'il y a le
    plus à lire.
    """
    print()
    try:
        input("Appuie sur Entrée pour fermer cette fenêtre... ")
    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == "__main__":
    pause = "--pause" in sys.argv
    try:
        code = main()
    except Exception:
        import traceback
        traceback.print_exc()
        code = 1
    if pause:
        _attendre_lecture()
    raise SystemExit(code)
