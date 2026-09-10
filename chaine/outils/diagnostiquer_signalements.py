# -*- coding: utf-8 -*-
"""
Diagnostic des signalements du joueur (« /afr signaler ») et des échecs
d'alignement journalisés par l'addon.

L'addon photographie l'info-bulle fautive dans les SavedVariables ; ici on
rejoue la traduction hors-jeu avec le vrai moteur Lua de l'addon et les
vraies bases, puis on classe chaque cas :
  absent      -> pas encore dans les bases : le cycle normal s'en chargera
  resolu      -> s'aligne désormais : un /reload en jeu suffit
  coquille    -> « $ » nu affiché par le client : coquille d'Ascension,
                 intraduisible proprement (voir README)
  alignement  -> présent mais le modèle ne s'aligne pas : à examiner à la main
  client      -> lignes candidates pour LignesClient (Tooltips.lua)

Rapport : traductions/rapport_signalements.txt
          (+ traductions/lignes_client_proposees.json, cumulées)

Étalonnage : le script se teste d'abord sur des témoins fabriqués et refuse
de publier s'il se trompe sur l'un d'eux (leçon d'auditer_accolades.py).
"""
import json
import locale
import os
import re
import sys
import time

import lupa.lua51 as lupa_mod

# Le client WoW tourne en locale C ; lupa, lui, hérite de la locale du poste
# (French_France.1252), où l'octet 0xA0 — 2e octet UTF-8 de « à », insécable
# en cp1252 — compte comme un BLANC (%s). Mesuré (sceptique du lot 14,
# 28/07/2026) : le trim final « %s+$ » de TraduireTexteSort amputait alors le
# dernier octet de 11 sorties du banc (UTF-8 invalide), et 19 272 D portent
# cet octet. La locale C recolle le décor hors-jeu au client — à poser AVANT
# de créer le moindre LuaRuntime.
locale.setlocale(locale.LC_CTYPE, "C")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chemin_client import JEU  # noqa: E402
ADDON = os.path.join(JEU, "Interface", "AddOns", "AscensionFR")
WTF = os.path.join(JEU, "WTF")
TRADUCTIONS = os.path.join(BASE, "traductions")
RAPPORT = os.path.join(TRADUCTIONS, "rapport_signalements.txt")
CANDIDATES = os.path.join(TRADUCTIONS, "lignes_client_proposees.json")
PROPOSITIONS = os.path.join(TRADUCTIONS, "propositions_joueurs.json")

# Préfixes des lignes d'effet (mêmes valeurs que Prefixes() de Tooltips.lua)
PREFIXES = ["Utiliser : ", "Équipé : ", "Chances quand vous touchez : ",
            "Use: ", "Equip: ", "Chance on hit: "]
# Suffixe de recharge collé par le client (même rôle que DetacherRecharge)
RE_RECHARGE = re.compile(r"\s*\([^()]*(?:recharge|[Cc]ooldown)[^()]*\)\s*$")


def _sans_nbsp(texte):
    """Blizzard frFR met une espace insécable avant « : » : le préfixe réel
    en jeu est « Utiliser : ». On compare en espaces normales (vécu :
    faux verdict « sans ligne d'effet » sur l'Anti-venin, 17/07)."""
    return texte.replace(" ", " ")

# Bases texte->texte où chercher une ligne signalée sans identifiant
DBS_TEXTE = ("Divers", "TextesPNJ", "Gossip", "Pages", "Libelles")

BASES_TOUTES = ("DB_Sorts.lua", "DB_Objets.lua", "DB_Creatures.lua",
                "DB_Divers.lua", "DB_TextesPNJ.lua", "DB_Gossip.lua",
                "DB_Pages.lua", "DB_Libelles.lua")

CONTEXTE = r"""
function strtrim(s) return (string.gsub(s or "", "^%s*(.-)%s*$", "%1")) end
function UnitName() return "Diagnostic" end
function UnitClass() return "Templar" end
function UnitRace() return "Human" end
function UnitSex() return 2 end
function print() end
-- Cadres factices : depuis le préchauffage 2.0.2, Core.lua crée un cadre
-- au CHARGEMENT (CreateFrame + RegisterEvent + SetScript). Toute méthode
-- appelée sur un cadre factice ne fait rien — il n'y a pas de jeu ici.
local function __cadre()
    local f = {}
    setmetatable(f, { __index = function() return function() end end })
    return f
end
function CreateFrame() return __cadre() end
function hooksecurefunc() end
GameTooltip = __cadre()
ItemRefTooltip = __cadre()
ShoppingTooltip1 = __cadre()
ShoppingTooltip2 = __cadre()
UIParent = __cadre()
-- Les modules enregistrent des commandes slash au chargement (/afrformat,
-- /afrbulle, /afrcommunaute…) : sans ce stub, charger Sorts.lua planterait.
SlashCmdList = {}
"""


def charger_moteur(bases=()):
    """Le vrai moteur de l'addon (Core + Sorts), plus les bases demandées."""
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)
    for rel in ("Core.lua", os.path.join("Modules", "Sorts.lua")):
        with open(os.path.join(ADDON, rel), encoding="utf-8") as f:
            lua.execute(f.read())
    for nom in bases:
        chemin = os.path.join(ADDON, "DB", nom)
        if os.path.exists(chemin):
            with open(chemin, encoding="utf-8") as f:
                lua.execute(f.read())
    return lua


def _lignes_de(valeur):
    """Table Lua {1=..., 2=...} ou chaîne multi-lignes -> liste de chaînes."""
    if valeur is None:
        return []
    if isinstance(valeur, str):
        return [l for l in valeur.split("\n") if l]
    try:
        paires = sorted((int(k), v) for k, v in valeur.items())
        return [v or "" for _, v in paires]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Lecture des SavedVariables
# ---------------------------------------------------------------------------
def lire_saved():
    """(liste de signalements, {"S": {id: texte}, "O": {id: texte}})."""
    signalements, echecs = [], {"S": {}, "O": {}}
    for racine, _, fichiers in os.walk(WTF):
        for nom in fichiers:
            if nom != "AscensionFR.lua" or "SavedVariables" not in racine:
                continue
            try:
                lua = lupa_mod.LuaRuntime()
                with open(os.path.join(racine, nom), encoding="utf-8",
                          errors="ignore") as f:
                    lua.execute(f.read())
                saved = lua.globals().AscensionFRSaved
                if not saved:
                    continue
                if saved.Signalements:
                    for _, s in sorted(saved.Signalements.items()):
                        d = {k: v for k, v in s.items()}
                        for champ in ("L", "R"):
                            if champ in d:
                                d[champ] = _lignes_de(d[champ])
                        if "ID" in d:
                            d["ID"] = int(d["ID"])
                        signalements.append(d)
                if saved.EchecsAlignement:
                    for genre in ("S", "O"):
                        table = saved.EchecsAlignement[genre]
                        if table:
                            for k, v in table.items():
                                if not isinstance(v, str):
                                    v = _lignes_de(v)
                                echecs[genre][int(k)] = v
            except Exception as e:
                print("  ! lecture de %s impossible : %s" % (nom, e))
    return signalements, echecs


# ---------------------------------------------------------------------------
# Diagnostics — chacun renvoie (categorie, message)
# ---------------------------------------------------------------------------
def diagnostiquer_sort(lua, sid, lignes):
    g = lua.globals()
    sid = int(sid)
    s = g.AscensionFR.DB.Sorts[sid]
    if s is None:
        return ("absent", "sort %d absent des bases : la récolte du survol "
                "le fera traduire au prochain cycle." % sid)
    if not s.D:
        return ("absent", "sort %d connu de nom seulement, description dans "
                "la file de traduction." % sid)
    for ligne in lignes:
        if len(ligne) > 10:
            if g.AscensionFR.TraduireTexteSort(s.D, s.DE, ligne):
                return ("resolu",
                        "s'aligne désormais : un /reload en jeu suffit.")
    if any("$" in l for l in lignes):
        return ("coquille", "le client affiche un « $ » nu : coquille "
                "d'Ascension dans un calcul ${...} du sort, intraduisible "
                "proprement (README, § Les « $ » qui viennent d'Ascension).")
    modele = (s.DE or s.D or "").replace("\n", " ")[:90]
    return ("alignement", "présent dans les bases mais aucune ligne capturée "
            "ne s'aligne sur « %s... » : à examiner à la main." % modele)


def diagnostiquer_objet(lua, oid, lignes):
    g = lua.globals()
    oid = int(oid)
    o = g.AscensionFR.DB.Objets[oid]
    if o is None:
        return ("absent", "objet %d pas encore extrait du cache : il y "
                "entrera au prochain /reload et sera traduit au cycle "
                "suivant." % oid)
    effets = [l for l in lignes
              if any(_sans_nbsp(l).startswith(p) for p in PREFIXES)]
    if not effets:
        return ("autre", "objet connu (« %s ») sans ligne d'effet capturée : "
                "préciser ce qui reste en anglais (nom ? ambiance ? les "
                "stats viennent des GlobalStrings)." % (o.N or "?"))
    sorts = [int(v) for v in list(o.S.values())] if o.S else []
    if not sorts:
        return ("absent", "objet sans sorts liés (champ S) : la liaison se "
                "fera au prochain cycle du compagnon.")
    restants = []
    for ligne in effets:
        corps = ligne
        for p in PREFIXES:
            if _sans_nbsp(corps).startswith(p):
                corps = corps[len(p):]
                break
        corps = RE_RECHARGE.sub("", corps)
        aligne = False
        for sid in sorts:
            s = g.AscensionFR.DB.Sorts[sid]
            if s and s.D and g.AscensionFR.TraduireTexteSort(s.D, s.DE, corps):
                aligne = True
                break
        if not aligne:
            restants.append(ligne)
    if not restants:
        return ("resolu", "les lignes d'effet s'alignent désormais : un "
                "/reload en jeu suffit.")
    if any("$" in l for l in restants):
        return ("coquille", "« $ » nu affiché par le client : coquille "
                "d'Ascension dans le sort lié, intraduisible proprement.")
    manquants = [sid for sid in sorts
                 if not g.AscensionFR.DB.Sorts[sid]
                 or not g.AscensionFR.DB.Sorts[sid].D]
    if manquants:
        return ("absent", "sort(s) d'effet %s pas encore traduit(s) : file "
                "de traduction en cours." % manquants)
    return ("alignement", "ligne « %s... » : aucun des sorts liés (%s) ne "
            "s'aligne — à examiner à la main." % (restants[0][:70], sorts))


def diagnostiquer_pnj(lua, cid, lignes):
    g = lua.globals()
    cid = int(cid)
    c = g.AscensionFR.DB.Creatures[cid]
    if c is None:
        return ("absent", "créature %d absente des bases : le cache du "
                "prochain /reload la fera traduire." % cid)
    return ("autre", "créature connue (« %s ») : préciser la ligne fautive "
            "(sous-titre ? niveau ?)." % (c.N or c.NE or "?"))


def diagnostiquer_proposition(lua, s, propositions):
    """Proposition de traduction d'un joueur (« /afrtrad »). On la RANGE pour
    arbitrage — le vocabulaire reste décidé côté projet, pas écrit à la volée.
    Vote : plusieurs joueurs proposant la même chose renforcent la confiance."""
    g = lua.globals()
    cible = s.get("cible") or "?"
    pid = s.get("ID")
    propose = (s.get("P") or "").strip()
    actuel = (s.get("actuel") or "").strip()
    if not propose:
        return ("proposition", "proposition vide.")
    connu = None
    if not pid:
        # interface, aura/débuff, texte libre : pas d'ID -> clé par le TEXTE.
        ident = actuel or s.get("nomCadre") or "?"
        cle = (cible or "texte") + ":" + ident[:60]
    else:
        pid = int(pid)
        try:
            if cible == "sort" and g.AscensionFR.DB.Sorts[pid]:
                connu = g.AscensionFR.DB.Sorts[pid].N
            elif cible == "objet" and g.AscensionFR.DB.Objets[pid]:
                connu = g.AscensionFR.DB.Objets[pid].N
            elif cible == "pnj" and g.AscensionFR.DB.Creatures[pid]:
                connu = g.AscensionFR.DB.Creatures[pid].N
        except Exception:
            pass
        # La ligne visée entre dans la clé : nom et description d'un MÊME sort
        # sont deux propositions distinctes (chacune ses votes).
        cle = "%s:%d:%s" % (cible, pid, actuel[:60])
        ident = "%s %d" % (cible, pid)
    e = propositions.get(cle) or {"cible": cible, "id": pid,
                                  "actuel": actuel or connu or "",
                                  "propositions": {}}
    e["propositions"][propose] = e["propositions"].get(propose, 0) + 1
    propositions[cle] = e
    return ("proposition", "« %s » -> « %s » (%s) — rangée pour arbitrage."
            % (actuel or connu or "?", propose, ident))


def diagnostiquer_texte(lua, lignes):
    """-> ((categorie, message), lignes inconnues candidates LignesClient)."""
    g = lua.globals()
    inconnues = []
    for ligne in lignes:
        if len(ligne) < 4 or not any(car.isalpha() for car in ligne):
            continue
        connue = False
        for nom in DBS_TEXTE:
            db = g.AscensionFR.DB[nom]
            if db and db[ligne]:
                connue = True
                break
        if not connue:
            inconnues.append(ligne)
    if not inconnues:
        return ("resolu", "toutes les lignes sont connues des bases : un "
                "/reload en jeu suffit."), []
    return ("client", "%d ligne(s) inconnue(s) des bases — candidates pour "
            "LignesClient (Tooltips.lua) si elles viennent du client "
            "compilé, sinon la récolte les couvrira."
            % len(inconnues)), inconnues


# ---------------------------------------------------------------------------
# Témoins : des cas dont on connaît la réponse. Se tromper sur l'un d'eux
# interdit de publier un rapport.
# ---------------------------------------------------------------------------
def _temoins():
    lua = charger_moteur()
    lua.execute(r"""
        AscensionFR.DB.Sorts[1] = { D = "Rend $s1 points.",
                                    DE = "Restores $s1 points." }
        AscensionFR.DB.Sorts[3] = { D = "Inflige $ dégâts.",
                                    DE = "Deals $ damage." }
        AscensionFR.DB.Objets[10] = { N = "Fiole", S = { "1" } }
    """)
    cas = [
        (diagnostiquer_sort(lua, 1, ["Restores 25 points."])[0], "resolu"),
        (diagnostiquer_sort(lua, 2, ["Whatever text here."])[0], "absent"),
        (diagnostiquer_sort(lua, 1, ["Something that does not align."])[0],
         "alignement"),
        (diagnostiquer_sort(lua, 3, ["Deals $ damage."])[0], "coquille"),
        (diagnostiquer_objet(lua, 10, ["Use: Restores 25 points."])[0],
         "resolu"),
        (diagnostiquer_objet(lua, 11, ["Use: Anything."])[0], "absent"),
        (diagnostiquer_objet(lua, 10,
            ["Utiliser : Restores 25 points."])[0], "resolu"),
    ]
    return all(obtenu == attendu for obtenu, attendu in cas), cas


# ---------------------------------------------------------------------------
# Rapport
# ---------------------------------------------------------------------------
def executer(journal=print):
    """Diagnostique tout ce qui attend ; renvoie le nombre d'éléments."""
    ok, cas = _temoins()
    if not ok:
        journal("  ! diagnostic déréglé (témoins en échec : %s) : "
                "rapport non publié"
                % [(o, a) for o, a in cas if o != a])
        return 0
    signalements, echecs = lire_saved()
    if not signalements and not echecs["S"] and not echecs["O"]:
        return 0

    lua = charger_moteur(BASES_TOUTES)
    corps = []
    candidates = {}
    propositions = {}

    for i, s in enumerate(signalements, 1):
        genre = s.get("T", "?")
        lignes = s.get("L") or []
        titre = lignes[0] if lignes else (s.get("actuel") or s.get("N", ""))
        if genre == "objet":
            cat, msg = diagnostiquer_objet(lua, s["ID"], lignes)
        elif genre == "sort":
            cat, msg = diagnostiquer_sort(lua, s["ID"], lignes)
        elif genre == "pnj":
            cat, msg = diagnostiquer_pnj(lua, s["ID"], lignes)
        elif genre == "note":
            cat, msg = "note", "remarque libre du joueur."
        elif genre == "cadre":
            cat, msg = "cadre", ("structure de fenêtre capturée — à lire "
                                 "pour comprendre une fenêtre non couverte.")
        elif genre == "proposition":
            cat, msg = diagnostiquer_proposition(lua, s, propositions)
        else:
            (cat, msg), inconnues = diagnostiquer_texte(lua, lignes)
            for ligne in inconnues:
                candidates[ligne] = candidates.get(ligne, 0) + 1
        corps.append("%d. [%s%s] « %s » — signalé le %s" % (
            i, genre, " %d" % s["ID"] if s.get("ID") else "",
            (titre or "")[:60], s.get("Q", "?")))
        corps.append("   -> %s : %s" % (cat.upper(), msg))
        if genre == "note":
            corps.append("   « %s »" % s.get("N", ""))
        elif genre == "cadre":
            for ligne in lignes:
                corps.append("   %s" % ligne)
        corps.append("")

    if echecs["S"] or echecs["O"]:
        corps.append("ÉCHECS D'ALIGNEMENT RELEVÉS PAR L'ADDON")
        corps.append("-" * 39)
        for sid, texte in sorted(echecs["S"].items()):
            lignes = texte if isinstance(texte, list) \
                else [l for l in texte.split("\n") if l]
            cat, msg = diagnostiquer_sort(lua, sid, lignes)
            corps.append("sort %d : %s — %s" % (sid, cat.upper(), msg))
        for oid, texte in sorted(echecs["O"].items()):
            lignes = texte if isinstance(texte, list) \
                else [l for l in texte.split("\n") if l]
            cat, msg = diagnostiquer_objet(lua, oid, lignes)
            corps.append("objet %d : %s — %s" % (oid, cat.upper(), msg))
        corps.append("")

    if candidates:
        existantes = {}
        if os.path.exists(CANDIDATES):
            with open(CANDIDATES, encoding="utf-8") as f:
                existantes = json.load(f)
        for ligne, n in candidates.items():
            existantes[ligne] = existantes.get(ligne, 0) + n
        with open(CANDIDATES, "w", encoding="utf-8") as f:
            json.dump(existantes, f, ensure_ascii=False, indent=1,
                      sort_keys=True)
        corps.append("Lignes candidates LignesClient cumulées dans %s"
                     % os.path.basename(CANDIDATES))

    if propositions:
        anciennes = {}
        if os.path.exists(PROPOSITIONS):
            with open(PROPOSITIONS, encoding="utf-8") as f:
                anciennes = json.load(f)
        for cle, e in propositions.items():
            vieux = anciennes.get(cle)
            if vieux:
                votes = vieux.setdefault("propositions", {})
                for fr, n in e["propositions"].items():
                    votes[fr] = votes.get(fr, 0) + n
                if e.get("actuel"):
                    vieux["actuel"] = e["actuel"]
            else:
                anciennes[cle] = e
        with open(PROPOSITIONS, "w", encoding="utf-8") as f:
            json.dump(anciennes, f, ensure_ascii=False, indent=1,
                      sort_keys=True)
        corps.append("%d proposition(s) de joueur cumulée(s) dans %s "
                     "(à arbitrer)." % (len(propositions),
                                        os.path.basename(PROPOSITIONS)))

    en_tete = [
        "Rapport des signalements AscensionFR — %s"
        % time.strftime("%d/%m/%Y %H:%M"),
        "=" * 60,
        "",
        "SIGNALEMENTS DU JOUEUR (%d)" % len(signalements),
        "-" * 27,
        "",
    ]
    os.makedirs(TRADUCTIONS, exist_ok=True)
    with open(RAPPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(en_tete + corps) + "\n")
    return len(signalements) + len(echecs["S"]) + len(echecs["O"])


if __name__ == "__main__":
    if "--test" in sys.argv:
        ok, cas = _temoins()
        for i, (obtenu, attendu) in enumerate(cas, 1):
            etat = "ok   " if obtenu == attendu else "ECHEC"
            print("  %s témoin %d : %s (attendu %s)"
                  % (etat, i, obtenu, attendu))
        sys.exit(0 if ok else 1)
    n = executer()
    print("%d élément(s) diagnostiqué(s)%s"
          % (n, " -> " + RAPPORT if n else ""))
