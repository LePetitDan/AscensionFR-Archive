# -*- coding: utf-8 -*-
"""Met AU CLAIR les retours joueurs bruts pour l'espace de travail.

Les 1200+ fichiers `rapports/auto_*.txt` (captures automatiques du Compagnon,
postées via le webhook Discord) sont illisibles un par un. Ici on les
DÉDOUBLONNE au niveau de l'ENTRÉE (un même sort revient dans des centaines de
rapports), on ENRICHIT chaque entrée avec la traduction ACTUELLE tirée des
bases vivantes (on réutilise le moteur de diagnostiquer_signalements.py), et on
écrit des fichiers LISIBLES, un par type, dans :

    D:\\AscensionFR\\3-atelier\\retours-joueurs\\

Chaque entrée porte : 1re date vue · identifiant · type · texte anglais ·
traduction actuelle (si elle existe) · statut (à traiter / déjà traduit) ·
nombre de rapports. JAMAIS de pseudo de joueur (on n'extrait que des données
de jeu : identifiants, textes de jeu, traductions ; jamais les lignes
« Compte N » ni un nom).

  python outils/clarifier_retours_joueurs.py            # écrit les fichiers
  python outils/clarifier_retours_joueurs.py --limite 30   # essai sur 30 fichiers
  python outils/clarifier_retours_joueurs.py --apercu      # n'écrit rien, stats

`_INDEX.md` récapitule les lots et sert de mémoire de ce qui a été traité —
pour ne pas retrier deux fois. Rafraîchir à chaque version.
"""
import glob
import os
import re
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAPPORTS = os.path.join(BASE, "rapports")
SORTIE = r"D:\AscensionFR\3-atelier\retours-joueurs"
DISCORD_EPOCH = 1420070400000  # ms — 2015-01-01, origine des snowflakes Discord
AUJOURDHUI = time.strftime("%Y-%m-%d")

# Réutilise le moteur Lua + les bases de diagnostiquer_signalements.py.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagnostiquer_signalements import charger_moteur, BASES_TOUTES  # noqa: E402


# ---------------------------------------------------------------------------
# Parsing des auto_*.txt
# ---------------------------------------------------------------------------
def date_du_fichier(nom):
    """auto_<snowflake>_... -> 'AAAA-MM-JJ' (le snowflake encode l'heure)."""
    m = re.match(r"auto_(\d+)_", os.path.basename(nom))
    if not m:
        return "0000-00-00"
    ts = (int(m.group(1)) >> 22) + DISCORD_EPOCH
    return time.strftime("%Y-%m-%d", time.gmtime(ts / 1000))


RE_SECTION = re.compile(r"^---\s*(.*?)\s*---\s*$")
RE_ID = re.compile(r"^(\d+)\s*:\s*$")
RE_RECOLTE = re.compile(r"^\[([^\]]+)\]\s*(.*)$")
RE_VERSION = re.compile(r"AscensionFR\s+([\d.]+)")

# catégorie de récolte -> (type interne, base de texte pour la traduction)
RECOLTE_TYPE = {
    "Sorts": ("sort", None),           # valeur = identifiant
    "Gossip": ("gossip", "Gossip"),
    "TextesPNJ": ("pnj", "TextesPNJ"),
    "Divers": ("divers", "Divers"),
    "Pages": ("pages", "Pages"),
    "QuetesRendu": ("quete", "QuetesObjectifs"),
    "QuetesProgres": ("quete", "QuetesObjectifs"),
}


def parser_fichier(chemin):
    """-> (entrees, signalements, propositions).

    entrees : liste de dict {type, id|cle, apercu, date, version}
    signalements / propositions : listes de dict (retours humains explicites).
    """
    date = date_du_fichier(chemin)
    txt = open(chemin, encoding="utf-8", errors="ignore").read()
    m = RE_VERSION.search(txt)
    version = m.group(1) if m else "?"

    entrees, sig_raw, prop_raw = [], [], []
    etat = {"section": None, "id": None, "lignes": [], "bloc": []}

    def flush_so():
        if etat["id"] is not None:
            entrees.append({
                "type": "sort" if etat["section"] == "S" else "objet",
                "cle": etat["id"], "apercu": " ".join(etat["lignes"])[:200],
                "date": date, "version": version})
        etat["id"], etat["lignes"] = None, []

    def flush_bloc():
        if etat["bloc"] and etat["section"] in ("SIG", "PROP"):
            cible = sig_raw if etat["section"] == "SIG" else prop_raw
            cible.extend(_recs(etat["bloc"]))
        etat["bloc"] = []

    for ligne in txt.splitlines():
        ms = RE_SECTION.match(ligne)
        if ms:
            flush_so()
            flush_bloc()
            tete = ms.group(1)
            etat["section"] = (
                "S" if tete.startswith("Échecs d'alignement S")
                else "O" if tete.startswith("Échecs d'alignement O")
                else "R" if tete.startswith("Récolte")
                else "SIG" if tete.startswith("Signalements")
                else "PROP" if tete.startswith("Propositions")
                else None)
            continue
        if ligne.startswith("=== "):
            flush_so()
            flush_bloc()
            etat["section"] = None
            continue
        if ligne.strip() == "":
            if etat["section"] in ("S", "O"):
                flush_so()
            elif etat["section"] in ("SIG", "PROP"):
                etat["bloc"].append(ligne)  # blanc INTERNE au texte multi-lignes
            continue

        sec = etat["section"]
        if sec in ("S", "O"):
            mid = RE_ID.match(ligne)
            if mid:
                flush_so()
                etat["id"], etat["lignes"] = int(mid.group(1)), []
            elif etat["id"] is not None:
                etat["lignes"].append(ligne.strip())
        elif sec == "R":
            mr = RE_RECOLTE.match(ligne.strip())
            if mr:
                cat, val = mr.group(1), mr.group(2).strip()
                typ, _ = RECOLTE_TYPE.get(cat, ("divers", "Divers"))
                if typ == "sort" and val.isdigit():
                    entrees.append({"type": "sort", "cle": int(val),
                                    "apercu": "", "date": date,
                                    "version": version})
                elif val:
                    entrees.append({"type": typ, "cle": val, "apercu": "",
                                    "date": date, "version": version})
        elif sec in ("SIG", "PROP"):
            etat["bloc"].append(ligne)

    flush_so()
    flush_bloc()

    sig = [parse_signalement(r, date) for r in sig_raw]
    prop = [parse_proposition(r) for r in prop_raw]
    return entrees, [s for s in sig if s], [p for p in prop if p]


def _recs(bloc):
    recs, courant = [], []
    for ligne in bloc:
        if ligne.startswith("- ") and courant:
            recs.append("\n".join(courant))
            courant = [ligne]
        else:
            courant.append(ligne)
    if courant:
        recs.append("\n".join(courant))
    return [r for r in recs if r.strip().startswith("-")]


RE_DATE_DEBUT = re.compile(r"^(\d{2}/\d{2}/\d{2}\s+\d{2}:\d{2})\b")
TYPES_CONNUS = {"objet", "sort", "texte", "pnj", "note", "cadre"}


def parse_signalement(rec, date_fichier):
    """Le format a dérivé entre versions (parfois « date | L | type | R | id »,
    parfois « id | texte | date | type »). On reconnaît chaque champ par sa
    NATURE plutôt que par sa position : type = champ ∈ TYPES_CONNUS, date =
    champ « jj/mm/aa », id = champ tout-chiffres, reste = texte signalé.
    On ignore les tables Lua non sérialisées (<Lua table at 0x...>)."""
    corps = rec.strip()[1:].strip()  # ôte le tiret
    champs = [c.strip() for c in corps.split(" | ")]
    typ = next((c for c in champs if c in TYPES_CONNUS), "?")
    dat = next((RE_DATE_DEBUT.match(c).group(1) for c in champs
                if RE_DATE_DEBUT.match(c)), date_fichier)
    ident = next((int(c) for c in champs if c.isdigit()), None)
    restes = [c for c in champs
              if c not in (typ, dat) and not c.isdigit()
              and not RE_DATE_DEBUT.match(c)
              and "<Lua table" not in c and c]
    texte = re.sub(r"\s+", " ", " · ".join(restes).replace("\n", " "))
    texte = re.sub(r"(\s*[·/]\s*){2,}", " / ", texte)  # runs de séparateurs vides
    texte = re.sub(r"^[·/\s]+|[·/\s]+$", "", texte)    # queues de séparateurs
    return {"id": ident, "type": typ, "texte": texte[:400], "date": dat}


def parse_proposition(rec):
    """- type | id | actuel=... | propose=..."""
    corps = rec.strip()[1:].strip()
    ma = re.search(r"actuel=(.*?)(?:\s*\|\s*propose=|$)", corps, re.S)
    mp = re.search(r"propose=(.*)$", corps, re.S)
    tete = corps.split("|", 2)
    typ = tete[0].strip() if tete else "?"
    ident = tete[1].strip() if len(tete) > 1 and tete[1].strip().isdigit() \
        else None
    return {"type": typ, "id": int(ident) if ident else None,
            "actuel": (ma.group(1).strip().replace("\n", " ")[:200]
                       if ma else ""),
            "propose": (mp.group(1).strip().replace("\n", " ")[:200]
                        if mp else "")}


# ---------------------------------------------------------------------------
# Enrichissement par les bases vivantes
# ---------------------------------------------------------------------------
def _txt(v):
    if v is None:
        return ""
    return str(v).replace("\n", " ").replace("\r", " ").strip()


def construire_lookup():
    print("  chargement des bases vivantes (moteur de l'addon)…")
    lua = charger_moteur(BASES_TOUTES)
    g = lua.globals()
    return g


def enrichir(g, typ, cle):
    """-> (en, fr, statut). statut : 'traduit' | 'absent'."""
    try:
        if typ == "sort":
            s = g.AscensionFR.DB.Sorts[int(cle)]
            if s is None:
                return ("", "", "absent")
            return (_txt(s.DE or s.TE), _txt(s.D), "traduit" if s.D else "absent")
        if typ == "objet":
            o = g.AscensionFR.DB.Objets[int(cle)]
            if o is None:
                return ("", "", "absent")
            return ("", _txt(o.N) + " (nom)", "traduit" if o.N else "absent")
        base = {"gossip": "Gossip", "pnj": "TextesPNJ", "divers": "Divers",
                "pages": "Pages", "quete": "QuetesObjectifs"}.get(typ)
        if base:
            fr = g.AscensionFR.DB[base][str(cle)]
            return (_txt(str(cle)), _txt(fr) if fr else "",
                    "traduit" if fr else "absent")
    except Exception:
        pass
    return (_txt(str(cle)), "", "absent")


# ---------------------------------------------------------------------------
# Écriture
# ---------------------------------------------------------------------------
def tronque(t, n=110):
    t = _txt(t)
    return (t[:n] + "…") if len(t) > n else t


ETIQUETTE = {
    "sort": ("sorts", "Sorts"), "objet": ("objets", "Objets"),
    "pnj": ("textes-pnj", "Textes PNJ"), "gossip": ("gossip", "Gossip"),
    "divers": ("divers", "Divers"), "pages": ("pages", "Pages"),
    "quete": ("quetes", "Quêtes"),
}


def ecrire_lot(typ, entrees, apercu):
    slug, titre = ETIQUETTE[typ]
    nom = os.path.join(SORTIE, "%s_%s.md" % (AUJOURDHUI, slug))
    a_traiter = [e for e in entrees if e["statut"] == "absent"]
    resolus = [e for e in entrees if e["statut"] != "absent"]
    if apercu:
        return nom, len(entrees), len(a_traiter), len(resolus)

    def table(items):
        out = ["| 1re date | id / clé | texte anglais | traduction actuelle "
               "| nb |", "|---|---|---|---|---|"]
        for e in sorted(items, key=lambda x: (x["date"], str(x["cle"]))):
            en = e["en"] or e.get("apercu", "")  # à défaut d'EN en base : ce
            out.append("| %s | %s | %s | %s | %d |" % (  # que le joueur a vu
                e["date"], tronque(e["cle"], 40), tronque(en) or "—",
                tronque(e["fr"]) or "—", e["nb"]))
        return "\n".join(out)

    lignes = [
        "# Retours joueurs — %s — %s" % (titre, AUJOURDHUI),
        "",
        "> Extraction dédoublonnée de `rapports/auto_*.txt`. "
        "**Aucun pseudo.** Statut selon les bases vivantes (v addon courante).",
        "",
        "## Encore à traiter — absent des bases (%d)" % len(a_traiter),
        "",
        table(a_traiter) if a_traiter else "_rien à traiter._",
        "",
        "## Déjà traduit — pour mémoire (%d)" % len(resolus),
        "",
        table(resolus) if resolus else "_aucun._",
        "",
    ]
    with open(nom, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")
    return nom, len(entrees), len(a_traiter), len(resolus)


def ecrire_signalements(sigs, apercu):
    nom = os.path.join(SORTIE, "%s_signalements-explicites.md" % AUJOURDHUI)
    if apercu:
        return nom, len(sigs)
    lignes = ["# Signalements explicites des joueurs — %s" % AUJOURDHUI, "",
              "> Retours postés via « /afr signaler ». **Aucun pseudo.** "
              "Les plus prioritaires : un joueur a pris le temps de signaler.",
              "", "| date | type | id | ce qu'il a signalé |",
              "|---|---|---|---|"]
    for s in sorted(sigs, key=lambda x: x["date"]):
        lignes.append("| %s | %s | %s | %s |" % (
            s["date"], s["type"], s["id"] or "—",
            tronque(s["texte"], 180) or "—"))
    with open(nom, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")
    return nom, len(sigs)


def ecrire_propositions(props, apercu):
    nom = os.path.join(SORTIE, "%s_propositions.md" % AUJOURDHUI)
    if apercu:
        return nom, len(props)
    lignes = ["# Propositions de traduction des joueurs — %s" % AUJOURDHUI, "",
              "> Suggestions postées via « /afrtrad ». **À ARBITRER** — le "
              "vocabulaire reste décidé côté projet. **Aucun pseudo.**",
              "", "| type | id | actuel | proposé par un joueur |",
              "|---|---|---|---|"]
    for p in props:
        lignes.append("| %s | %s | %s | %s |" % (
            p["type"], p["id"] or "—", tronque(p["actuel"], 120) or "—",
            tronque(p["propose"], 120) or "—"))
    with open(nom, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")
    return nom, len(props)


def ecrire_index(stats, n_fichiers, apercu):
    nom = os.path.join(SORTIE, "_INDEX.md")
    if apercu:
        return nom
    lignes = [
        "# Retours joueurs — index",
        "",
        "Tenu par Claude Code. Dit ce qui a déjà été mis au clair, pour ne "
        "pas retrier deux fois. **Rafraîchi à chaque version.**",
        "",
        "- Source : `traduction/rapports/auto_*.txt` (%d fichiers)" % n_fichiers,
        "- Généré le : %s par `outils/clarifier_retours_joueurs.py`" % AUJOURDHUI,
        "- **Aucun pseudo de joueur** dans ces fichiers.",
        "",
        "## Lots",
        "",
        "| lot | total | à traiter | déjà traduit | état |",
        "|---|---|---|---|---|",
    ]
    for nom_lot, total, a_traiter, resolus in stats["lots"]:
        lignes.append("| `%s` | %d | **%d** | %d | à trier |" % (
            os.path.basename(nom_lot), total, a_traiter, resolus))
    lignes += [
        "| `%s_signalements-explicites.md` | %d | — | — | à lire en priorité |"
        % (AUJOURDHUI, stats["sig"]),
        "| `%s_propositions.md` | %d | — | — | à arbitrer |"
        % (AUJOURDHUI, stats["prop"]),
        "",
        "## Méthode",
        "",
        "1. Dédoublonnage au niveau de l'ENTRÉE (un même identifiant revient "
        "dans des centaines de rapports) ; on garde 1re date + nb de rapports.",
        "2. « à traiter » = absent des bases vivantes ; « déjà traduit » = "
        "présent (résolu par le cycle normal, gardé pour mémoire).",
        "3. Les captures automatiques (échecs d'alignement, récolte) sont de "
        "la matière PIPELINE ; les **signalements** et **propositions** sont "
        "les vrais retours humains — priorité.",
        "4. La « traduction actuelle » vient d'une recherche EXACTE : par "
        "identifiant (sorts/objets), par clé-texte (pnj/gossip/divers/pages/"
        "quêtes). Pour les **quêtes** surtout, la clé de récolte (rendu/"
        "progrès) ne correspond pas toujours à la base : « à traiter » y est "
        "un MAJORANT — une traduction peut exister sous une autre clé. "
        "À confirmer avant de conclure.",
        "",
    ]
    with open(nom, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")
    return nom


# ---------------------------------------------------------------------------
def main():
    apercu = "--apercu" in sys.argv
    limite = None
    if "--limite" in sys.argv:
        limite = int(sys.argv[sys.argv.index("--limite") + 1])

    fichiers = sorted(glob.glob(os.path.join(RAPPORTS, "auto_*.txt")))
    if limite:
        fichiers = fichiers[:limite]
    print("Fichiers auto_*.txt à lire : %d%s"
          % (len(fichiers), " (aperçu)" if apercu else ""))

    # agrégation par (type, clé)
    agg = {}
    sigs, props = [], []
    for fp in fichiers:
        entrees, sig, prop = parser_fichier(fp)
        sigs.extend(sig)
        props.extend(prop)
        for e in entrees:
            k = (e["type"], str(e["cle"]))
            a = agg.get(k)
            if a is None:
                agg[k] = {"type": e["type"], "cle": e["cle"],
                          "date": e["date"], "nb": 1,
                          "apercu": e["apercu"]}
            else:
                a["nb"] += 1
                if e["date"] < a["date"]:
                    a["date"] = e["date"]
                if e["apercu"] and not a["apercu"]:
                    a["apercu"] = e["apercu"]
    print("Entrées uniques : %d  ·  signalements : %d  ·  propositions : %d"
          % (len(agg), len(sigs), len(props)))

    # dédoublonnage : par (type, id, date) on garde le texte le plus riche
    # (les captures anciennes laissaient parfois le texte vide « <Lua table> »)
    best = {}
    for s in sigs:
        k = (s["type"], s["id"], s["date"])
        if k not in best or len(s["texte"]) > len(best[k]["texte"]):
            best[k] = s
    sigs = list(best.values())
    props = list({(p["type"], p["id"], p["propose"]): p
                  for p in props}.values())

    g = None if apercu else construire_lookup()

    # enrichissement
    par_type = {}
    for a in agg.values():
        typ = a["type"] if a["type"] in ETIQUETTE else "divers"
        if apercu:
            en, fr, statut = a["apercu"], "", "?"
        else:
            en, fr, statut = enrichir(g, a["type"], a["cle"])
        a.update(en=en, fr=fr, statut=statut)
        par_type.setdefault(typ, []).append(a)

    os.makedirs(SORTIE, exist_ok=True) if not apercu else None
    stats = {"lots": [], "sig": len(sigs), "prop": len(props)}
    for typ in ETIQUETTE:
        if typ in par_type:
            nom, total, at, res = ecrire_lot(typ, par_type[typ], apercu)
            stats["lots"].append((nom, total, at, res))
            print("  %-14s total %5d | à traiter %5d | déjà %5d"
                  % (typ, total, at, res))
    ecrire_signalements(sigs, apercu)
    ecrire_propositions(props, apercu)
    ecrire_index(stats, len(fichiers), apercu)
    if not apercu:
        print("\nÉcrit dans %s" % SORTIE)
        print("  _INDEX.md + %d lots + signalements + propositions"
              % len(stats["lots"]))


if __name__ == "__main__":
    main()
