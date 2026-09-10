# -*- coding: utf-8 -*-
"""
AscensionFR - Compagnon de traduction v2
=========================================
À lancer pendant que vous jouez. Le programme :
  1. surveille les caches WDB du client (nouveau contenu rencontré en jeu)
     et les textes récoltés par l'addon (SavedVariables) ;
  2. traduit automatiquement les nouveautés (Google Translate, avec
     protection des codes de format $n, |cff...|r, %s...) ;
  3. régénère les bases Lua de l'addon.
En jeu, il suffit ensuite de taper /reload pour voir les nouveautés.

Usage :  python traducteur_fr.py            (interface graphique)
         python traducteur_fr.py --console  (mode console)
         python traducteur_fr.py --une-fois (un seul cycle puis quitte)
"""
import json
import os
import re
import sys
import threading
import time
import urllib.parse
import urllib.request
from concurrent import futures

# Requêtes de traduction menées de front. Le temps se passe à attendre le
# réseau : paralléliser accélère d'autant. Rester modeste évite que Google
# ne limite les requêtes (au-delà, il renvoie des erreurs 429).
PARALLELE = 6

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "outils"))

import parser_wdb  # noqa: E402
import generateur_db  # noqa: E402
from glossaire_jeu import (proteger_glossaire,  # noqa: E402
                           restaurer_glossaire)
from ecriture_sure import ecrire_json  # noqa: E402
# LE chemin du client vit dans outils/chemin_client.py (programme 31) :
# un seul réglage (ASCENSIONFR_JEU), et l'absence du client se VOIT.
from chemin_client import (JEU, client_present,  # noqa: E402
                           exiger_client)
WDB = os.path.join(JEU, "Cache", "WDB", "enUS", "Rexxar - Conquest of Azeroth")
WTF = os.path.join(JEU, "WTF")
EXTRAITS = os.path.join(BASE, "extraits", "rexxar")
A_TRADUIRE = os.path.join(BASE, "a_traduire")
TRADUCTIONS = os.path.join(BASE, "traductions")

# ---------------------------------------------------------------------------
# Protection des codes de format avant traduction automatique
#
# Deux familles de codes coexistent :
#   - textes de quêtes/objets : $n $b $c $r, $gmasculin:féminin;, |cff...|r
#   - descriptions de sorts   : $s1 (valeur), $d (durée), $t1 (intervalle),
#     $a1 (rayon), $o1 (total sur la durée), $m1/$M1 (min/max), $x1, $i,
#     $12345s1 (valeur d'un autre sort), ${$m1/10} (calcul),
#     $?a137012[texte][texte] (condition), $lseconde:secondes; (pluriel)
# ---------------------------------------------------------------------------
# Cette liste DOIT couvrir exactement les mêmes formes que MOTIFS_VARIABLE dans
# Modules\Sorts.lua. Les deux avaient divergé : l'addon reconnaissait
# « $<percent> » et « $*15;s1 », pas cette protection. Google les détruisait
# donc dans le texte français, et le joueur voyait un « $ » à la place d'un
# chiffre. Toute forme ajoutée d'un côté doit l'être de l'autre.
# Formes recensées sur les 36 000 sorts réels : outils/auditer_sorts.py
# Le conditionnel « $?s118174[oui][non] » se lit de DEUX façons, selon ce
# qu'on veut en faire — c'est là qu'était le bug des 292 descriptions figées
# en anglais (25/07/2026) :
#
#   ENTIER      ce que l'addon découpe (MOTIFS_VARIABLE, Modules\Sorts.lua) :
#               une variable d'alignement, crochets compris. appliquer_valeurs
#               va ensuite chercher la bonne branche DEDANS. Ne bouge pas.
#   SÉLECTEUR   ce qu'on cache au traducteur : le sélecteur seul. Le texte des
#               branches DOIT être traduit — c'est la description que lit le
#               joueur. Protéger le conditionnel entier, comme on le faisait,
#               revenait à interdire sa traduction.
#
# Le sélecteur avale quand même les branches SANS LETTRE (« $?s705811[2][1] »,
# « [] ») : il n'y a rien à y traduire, et une branche « [2] » laissée à l'air
# libre serait reprise pour un jeton de protection à la restauration.
_COND_ENTIER = r"\$\?[^\[]*\[[^\]]*\](?:\[[^\]]*\])?"
_COND_SELECTEUR = r"\$\?[^\[]*(?:\[[^\]A-Za-z]*\])*"


def _codes(conditionnel, extra=""):
    """Compile la liste des codes du jeu, pour une lecture du conditionnel."""
    return re.compile(
    r"(\$\{[^}]*\}"                     # ${ calcul }
    r"|" + conditionnel +               # $?condition[oui][non]
    r"|\$[/*+-]\d+;\d*[a-zA-Z]\d*"      # $/1000;s1 $*15;s1 $+100;s1
    r"|\$[Gg][^;]*;"                    # $gmasculin:féminin;
    r"|\$[Ll][^;]*;"                    # $lseconde:secondes; (pluriel)
    r"|\$@[a-zA-Z]+"                    # $@spellname
    r"|\$<[a-zA-Z]+>"                   # $<percent> $<mult> (variable nommée)
    r"|\$\d+[a-zA-Z]\d*"                # $64843s2 (valeur d'un autre sort)
    r"|\$[NnBbCcRr]\b"                  # $n $b $c $r (quêtes)
    r"|\$[a-zA-Z]\d*"                   # $s1 $d $h $u $t $o $q $a $x $e $z
    r"|\$\d+"                           # $1
    # Marquage maison d'Ascension, résolu par LEUR client avant affichage
    # (@ext: bloc d'info, @s:id:décalage@ insère la description d'un autre
    # sort, @req:id@ condition, @unlockby:/@learns: métadonnées...).
    # Non protégé, Google les abîmait : espaces insécables (« @ext : »),
    # noms traduits (« @learns: » devenu « @apprend : »). Un marqueur abîmé
    # côté français ne correspond plus à son jumeau anglais, et l'addon
    # laissait la description en anglais (3 646 sorts au moment du constat).
    r"|@ifknown:[\s\S]*?:ifknown@"      # texte conditionnel (si sort connu)
    r"|@ifnotknown:[\s\S]*?:ifnotknown@"
    r"|@wflocation:[^@]*@"              # indice de localisation Worldforge
    r"|@[a-zA-Z]+:\d+:-?\d+@"           # @s:101087:0@  @re:81298:0@
    r"|@[a-zA-Z]+:\d+:[a-zA-Z]+@"       # @req:1122520:req@
    r"|@[a-zA-Z]+:\d+@"                 # @req:8921@ @unlockby:635@ @learns:...
    r"|@ext:"                           # ouverture de bloc d'info étendue
    r"|:ext@"                           # fermeture
    # Marqueur enveloppant un TEXTE coloré, ex. @|cFFCC0000Bloodforged|r@
    # (tag « forgé par le sang » sur ~40 000 objets améliorés). Protégé EN
    # ENTIER, avant le motif de couleur ci-dessous : sinon seuls |c…|r
    # étaient protégés et Google traduisait « Bloodforged » -> « Bloodforgé »,
    # ce qui cassait la reconnaissance du marqueur par le client (il fuyait à
    # l'écran, signalement de Dan du 24/07/2026). Un texte relu par le client
    # comme clé ne se traduit pas.
    r"|@\|c[0-9a-fA-F]{8}[^@|]*\|r@"
    r"|\|c[0-9a-fA-F]{8}"               # début de couleur
    r"|\|r"                             # fin de couleur
    r"|\|T[^|]*\|t"                     # texture incrustée
    r"|\|H[^|]*\|h"                     # lien
    r"|%\d*\$?[sdif]"                   # %s %d %1$s
    r"|\\[nr]" +                        # \n littéraux
    extra + r")")


# La liste FAISANT AUTORITÉ des codes du jeu. C'est elle que l'addon doit
# refléter (verrou outils/verifier_motifs.py contre MOTIFS_VARIABLE) et que
# lisent les outils qui traquent un code abîmé (verifier_tout, purger_abimees).
# Elle n'a PAS bougé : le correctif des conditionnels porte sur le bouclier.
MOTIFS_PROTEGES = _codes(_COND_ENTIER)

# Ce qu'on cache RÉELLEMENT au traducteur automatique. Un seul écart avec la
# liste ci-dessus, et il est volontaire : le texte entre crochets d'un
# conditionnel reste exposé, pour être traduit.
# S'y ajoute « [12] » : un tel groupe présent dans le texte du jeu est
# indiscernable d'un jeton de protection, et restaurer() le remplacerait par
# le mauvais code (vécu sur la description de « Gore » — une branche « [2] »).
# On le met donc à l'abri lui aussi, pour être rendu tel quel.
MOTIF_BOUCLIER = _codes(_COND_SELECTEUR, r"|\[\d{1,3}\]")

# Pluriels courants des descriptions de sorts : le contenu de $l...; doit
# être traduit, mais Google le détruirait, donc on le fait nous-mêmes.
PLURIELS = {
    "second:seconds": "seconde:secondes",
    "sec:secs": "sec:secs",
    "minute:minutes": "minute:minutes",
    "min:mins": "min:mins",
    "hour:hours": "heure:heures",
    "yard:yards": "mètre:mètres",
    "time:times": "fois:fois",
    "charge:charges": "charge:charges",
    "enemy:enemies": "ennemi:ennemis",
    "ally:allies": "allié:alliés",
    "target:targets": "cible:cibles",
    "point:points": "point:points",
    "piece:pieces": "pièce:pièces",
    "level:levels": "niveau:niveaux",
    "stack:stacks": "cumul:cumuls",
    "member:members": "membre:membres",
    "person:people": "personne:personnes",
    "is:are": "est:sont",
    "was:were": "était:étaient",
}


def traduire_pluriels(texte):
    """Traduit le contenu des marqueurs de pluriel $l...; du jeu."""
    def rempl(m):
        contenu = m.group(1)
        fr = PLURIELS.get(contenu.lower())
        return "$l%s;" % (fr if fr else contenu)
    return re.sub(r"\$[Ll]([^;]*);", rempl, texte)


def proteger(texte):
    jetons = []

    def rempl(m):
        jetons.append(m.group(0))
        return "[%d]" % (len(jetons) - 1)

    return MOTIF_BOUCLIER.sub(rempl, texte), jetons


def restaurer(texte, jetons):
    def rempl(m):
        i = int(m.group(1))
        return jetons[i] if i < len(jetons) else m.group(0)

    return re.sub(r"\[\s*(\d+)\s*\]", rempl, texte)


# --- Le SECOND essai, et pourquoi il existe (bloc A, 29/07/2026) ------------
# Le jeton du bouclier ci-dessus, « [0] », entre en COLLISION avec la syntaxe
# du jeu : les descriptions pleines de conditionnels « $?s118174[oui][non] »
# offrent à Google des crochets partout, il ne distingue plus les nôtres des
# leurs, les abîme, et codes_intacts refuse — 36 descriptions restaient
# anglaises pour cette seule raison (mesuré au programme 4).
#
# Le repli protège avec « ¤0¤ », un délimiteur absent de la syntaxe du jeu.
# Il n'est PAS meilleur dans l'absolu — mesuré : sur 25 textes qui passent
# aujourd'hui, 9 seraient refusés avec ¤. C'est pourquoi il n'est jamais un
# remplacement : il ne s'exécute QUE là où le premier essai a déjà rendu
# None. Un texte qui passe aujourd'hui prend exactement le même chemin
# qu'aujourd'hui, à l'octet près — c'est la propriété qui rend l'ajout sûr,
# et le banc outils/banc_double_essai.py est là pour la vérifier.
JETON_REPLI = "¤"
RE_REPLI = re.compile(r"¤\s*(\d+)\s*¤")


def proteger_repli(texte):
    jetons = []

    def rempl(m):
        jetons.append(m.group(0))
        return "%s%d%s" % (JETON_REPLI, len(jetons) - 1, JETON_REPLI)

    return MOTIF_BOUCLIER.sub(rempl, texte), jetons


def restaurer_repli(texte, jetons):
    def rempl(m):
        i = int(m.group(1))
        return jetons[i] if i < len(jetons) else m.group(0)

    return RE_REPLI.sub(rempl, texte)


def codes_intacts(source, traduit):
    """Vérifie qu'aucun code technique n'a été perdu à la traduction.

    On compare avec le BOUCLIER, c'est-à-dire ce qu'on a réellement caché au
    traducteur — et pas avec la liste d'autorité. Sinon le conditionnel serait
    relevé en entier des deux côtés, donc « $?s300512[ and reducing…][] »
    contre « $?s300512[ et réduisant…][] » : toute traduction RÉUSSIE serait
    rejetée comme un code perdu, et la description resterait anglaise.
    """
    a = sorted(MOTIF_BOUCLIER.findall(source))
    b = sorted(MOTIF_BOUCLIER.findall(traduit))
    return a == b


# Mémoire des traductions de la session. 18 % des textes en attente sont des
# doublons EXACTS : « @Worldforged@ » revient 499 fois, « @Heroic Dungeon@ »
# 427 fois... Les renvoyer à Google coûte des heures pour rien.
_deja_traduit = {}

LETTRE = re.compile(r"[A-Za-zÀ-ÿ]")


def rien_a_traduire(protege):
    """Vrai si, une fois les codes techniques mis de côté, il ne reste aucune
    lettre : c'est un marqueur d'Ascension (« @Worldforged@ ») que le client
    remplace lui-même, pas une phrase. Inutile de l'envoyer traduire."""
    return not LETTRE.search(re.sub(r"\[\d+\]", "", protege))


# --- La consignation est liée à la VERSION DE LA PROTECTION ----------------
# Un « rejet chronique » n'est pas un texte insoluble : c'est un texte
# insoluble AVEC LA PROTECTION D'ALORS. Le jour où on répare la protection —
# ce qui vient d'arriver avec le second essai — les consignés doivent
# retrouver leur chance TOUT SEULS. Sinon la réparation ne sert à rien et
# personne ne s'en aperçoit : il faudrait se souvenir de lancer --retenter,
# et un conseil à mémoriser est un conseil perdu.
# Toute modification du bouclier, du repli ou du glossaire DOIT faire
# avancer cette chaîne : c'est elle qui déconsigne.
VERSION_BOUCLIER = "2026-07-29-double-essai"


def charger_rejets(chemin):
    """Renvoie (compteurs, motif_de_purge). Le motif est None quand rien
    n'a été remis à zéro ; sinon c'est la phrase à journaliser."""
    brut = charger_json(chemin) or {}
    if not brut:
        return {}, None
    if "textes" not in brut:              # ancien format, plat : {texte: n}
        return {}, ("%d consigné(s) sous une protection antérieure"
                    % len(brut))
    if brut.get("version_bouclier") != VERSION_BOUCLIER:
        return {}, ("la protection a changé (%s -> %s), %d consigné(s) libéré(s)"
                    % (brut.get("version_bouclier"), VERSION_BOUCLIER,
                       len(brut["textes"])))
    return dict(brut["textes"]), None


def sauver_rejets(chemin, compteurs):
    sauver_json(chemin, {"version_bouclier": VERSION_BOUCLIER,
                         "textes": compteurs})


def _appel_google(protege):
    """L'appel réseau nu. Partagé par les deux essais : ce qui change entre
    eux, c'est la protection posée AVANT, pas la façon d'interroger."""
    url = ("https://translate.googleapis.com/translate_a/single"
           "?client=gtx&sl=en&tl=fr&dt=t&q=" + urllib.parse.quote(protege))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as reponse:
        donnees = json.loads(reponse.read().decode("utf-8"))
    return "".join(p[0] for p in donnees[0] if p[0])


def traduire_google(texte, verifier=True):
    """Traduction EN -> FR via l'API gratuite de Google Translate.

    Renvoie None en cas d'échec ou si un code technique a été perdu :
    mieux vaut laisser l'anglais qu'un sort au texte cassé.

    LE GLOSSAIRE ARBITRÉ PROTÈGE D'ABORD (bloc D3, 29/07/2026 —
    proposition n° 3 de l'audit). Jusqu'ici, seules 2 étapes sur 6
    passaient par le glossaire (traduire_gisement) : tout le flux
    principal sortait en Google brut — c'est ce qui faisait revenir
    « rédiger » et « Cils légers » à chaque passe neuve. Les termes de
    jeu sont mis sous jetons §n§ AVANT Google (distincts des [n] des
    codes techniques), restaurés en français arbitré après, et un jeton
    abîmé vaut REFUS — mieux vaut l'anglais qu'un texte cassé. Ne touche
    que les traductions FUTURES : le cache existant ne bouge pas.
    """
    texte = traduire_pluriels(texte)
    connu = _deja_traduit.get(texte)
    if connu is not None:
        return connu
    glosse, mots_glossaire = proteger_glossaire(texte)
    protege, jetons = proteger(glosse)
    if rien_a_traduire(protege):
        # Plus rien à traduire une fois codes ET glossaire sortis : le
        # français, c'est la restauration du glossaire (« Haste » seul
        # devient « Hâte » — avant, il restait anglais).
        resultat = restaurer_glossaire(glosse, mots_glossaire)
        _deja_traduit[texte] = resultat
        return resultat
    try:
        traduit = _appel_google(protege)
        resultat = restaurer(traduit, jetons)
    except Exception:
        return None
    resultat = restaurer_glossaire(resultat, mots_glossaire)
    if not ("§" in resultat                # jeton de glossaire abîmé : refus
            or (verifier and not codes_intacts(texte, resultat))):
        # On ne mémorise QUE les succès : un échec réseau doit pouvoir être
        # retenté.
        _deja_traduit[texte] = resultat
        return resultat

    # --- Le premier essai a échoué : SECOND ESSAI au délimiteur de repli ----
    # On n'arrive ici que sur un texte qui, aujourd'hui, reste ANGLAIS. Rien
    # à dégrader, donc ; au pire on rend le même None, une requête plus tard.
    # La panne réseau, elle, ne repasse pas par ici (le repli n'y peut rien).
    protege2, jetons2 = proteger_repli(glosse)
    try:
        traduit2 = _appel_google(protege2)
    except Exception:
        return None
    resultat2 = restaurer_glossaire(restaurer_repli(traduit2, jetons2),
                                    mots_glossaire)
    if "§" in resultat2:
        return None
    if JETON_REPLI in resultat2 and JETON_REPLI not in texte:
        return None                       # jeton de repli abîmé : refus
    if verifier and not codes_intacts(texte, resultat2):
        return None
    _deja_traduit[texte] = resultat2
    return resultat2


# ---------------------------------------------------------------------------
# Lecture des SavedVariables de l'addon (via l'interpréteur Lua « lupa »)
# ---------------------------------------------------------------------------
def lire_recolte():
    """Retourne le contenu de AscensionFRSaved.Recolte de tous les comptes."""
    recolte = {}
    try:
        import lupa.lua51 as lupa_mod
    except ImportError:
        return recolte
    for racine, _, fichiers in os.walk(WTF):
        for nom in fichiers:
            if nom == "AscensionFR.lua" and "SavedVariables" in racine:
                try:
                    lua = lupa_mod.LuaRuntime()
                    with open(os.path.join(racine, nom),
                              encoding="utf-8", errors="ignore") as f:
                        lua.execute(f.read())
                    saved = lua.globals().AscensionFRSaved
                    if not saved or not saved.Recolte:
                        continue
                    for categorie, table in saved.Recolte.items():
                        cat = recolte.setdefault(categorie, {})
                        for cle, valeur in table.items():
                            if hasattr(valeur, "items"):
                                valeur = {k: v for k, v in valeur.items()}
                            cat[cle] = valeur
                except Exception as e:
                    print("  ! lecture de %s impossible : %s" % (nom, e))
    return recolte


# ---------------------------------------------------------------------------
# Fichiers de traductions cumulées
# ---------------------------------------------------------------------------
def charger_json(chemin):
    if os.path.exists(chemin):
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    return {}


def sauver_json(chemin, donnees):
    """Écriture ATOMIQUE (29/07/2026) — c'est par ici que passent TOUS les
    stores de la chaîne, dont sorts.json, réécrit toutes les 200
    traductions pendant des heures. Une coupure laissait le fichier le
    plus précieux du projet tronqué ; on écrit à côté et on ne remplace
    qu'au succès, comme le zip de release."""
    ecrire_json(chemin, donnees)


class Compagnon:
    def __init__(self, journal=print):
        self.journal = journal
        self.actif = False
        self.derniers_mtimes = {}
        self._faits, self._a_faire = 0, 0
        # Les comptes du passage (programme 31, bloc F) : émis en @@BILAN,
        # pour que « vert » veuille dire « a traduit », pas « code zéro ».
        self.bilan = {"tentees": 0, "traduites": 0, "refusees": 0,
                      "ecartees": 0}

    def dire_bilan(self):
        print("@@BILAN " + json.dumps(self.bilan, ensure_ascii=False),
              flush=True)

    # -- progression (barre d'avancement de l'Atelier) -----------------
    # Le marqueur « @@P » distingue ces lignes du journal ordinaire :
    # l'Atelier les intercepte pour bouger la barre au lieu de les afficher.
    def avancer(self, libelle=""):
        if not self._a_faire:
            return
        self._faits += 1
        print("@@P %d/%d %s" % (self._faits, self._a_faire,
                                libelle[:60].replace("\n", " ")), flush=True)

    def _compter_a_faire(self, recolte):
        """Combien de textes restent à traduire ? (pour la barre)"""
        def manquants(fichier):
            at = charger_json(os.path.join(A_TRADUIRE, fichier))
            tr = charger_json(os.path.join(TRADUCTIONS, fichier))
            return sum(1 for cle in at if cle not in tr)

        total = 0
        for nom in ("quetes.json", "objets.json", "creatures.json",
                    "objets_monde.json", "textes_pnj.json", "pages.json"):
            total += manquants(nom)
        for categorie, fichier in (("Gossip", "gossip.json"),
                                   ("TextesPNJ", "textes_pnj.json"),
                                   ("Pages", "pages.json"),
                                   ("Divers", "divers.json")):
            tr = charger_json(os.path.join(TRADUCTIONS, fichier))
            total += sum(1 for cle in (recolte or {}).get(categorie, {})
                         if cle not in tr)
        tr_q = charger_json(os.path.join(TRADUCTIONS, "quetes.json"))
        for categorie, champ in (("QuetesProgres", "P"), ("QuetesRendu", "R")):
            for qid in (recolte or {}).get(categorie, {}):
                if champ not in tr_q.get(str(int(qid)), {}):
                    total += 1
        tr_s = charger_json(os.path.join(TRADUCTIONS, "sorts_recoltes.json"))
        total += sum(1 for sid in (recolte or {}).get("Sorts", {})
                     if str(int(sid)) not in tr_s)
        return total

    # -- détection de changements ------------------------------------
    def _mtimes(self):
        mtimes = {}
        if os.path.isdir(WDB):
            for nom in os.listdir(WDB):
                if nom.endswith(".wdb"):
                    chemin = os.path.join(WDB, nom)
                    mtimes[chemin] = os.path.getmtime(chemin)
        for racine, _, fichiers in os.walk(WTF):
            for nom in fichiers:
                if nom == "AscensionFR.lua" and "SavedVariables" in racine:
                    chemin = os.path.join(racine, nom)
                    mtimes[chemin] = os.path.getmtime(chemin)
        return mtimes

    def changements(self):
        mtimes = self._mtimes()
        change = mtimes != self.derniers_mtimes
        self.derniers_mtimes = mtimes
        return change

    # -- traduction d'un lot -----------------------------------------
    def _traduire_lot(self, textes, cible, transformation=None, pause=0.4):
        """Traduit chaque texte absent de `cible` et l'y ajoute.

        Mené en parallèle : l'attente réseau domine, la traduire à la file
        multipliait la durée par six sans rien y gagner."""
        restants = [(cle, source) for cle, source in textes
                    if cle not in cible and source]
        if not restants:
            return 0
        nouveaux = 0
        with futures.ThreadPoolExecutor(max_workers=PARALLELE) as pool:
            resultats = pool.map(lambda p: (p[0], p[1],
                                            traduire_google(p[1])), restants)
            for cle, source, fr in resultats:
                if fr:
                    cible[cle] = transformation(fr) if transformation else fr
                    nouveaux += 1
                    self.journal("    + %s"
                                 % (source[:60].replace("\n", " ")))
                self.avancer(source)
        self.bilan["tentees"] += len(restants)
        self.bilan["traduites"] += nouveaux
        self.bilan["refusees"] += len(restants) - nouveaux
        return nouveaux

    def cycle_sorts(self, limite=None, champs=("noms", "descriptions")):
        """Traduit les sorts de classe restants (textes uniques).

        Long (plusieurs heures pour la totalité) mais entièrement gratuit :
        chaque texte unique n'est traduit qu'une fois, quel que soit le
        nombre de sorts qui le partagent.
        """
        chemin = os.path.join(A_TRADUIRE, "sorts_textes.json")
        if not os.path.exists(chemin):
            self.journal("Lancez d'abord : python outils/generateur_sorts.py")
            return
        textes = charger_json(chemin)
        cible = os.path.join(TRADUCTIONS, "sorts.json")
        traductions = charger_json(cible) or {"noms": {}, "descriptions": {}}
        traductions.setdefault("noms", {})
        traductions.setdefault("descriptions", {})

        total = 0
        verrou = threading.Lock()
        # LA BARRIÈRE AU POINT D'ÉCRITURE (bloc 8, 28/07/2026 — le correctif
        # de fond réclamé depuis le lot 13). Les familles de faux noms
        # NAISSENT ici : Google tronque (« Visual: X » -> « visuel : »),
        # aplatit, et la même valeur se pose sur des clés sans parenté — la
        # purge seule ne fermait rien, la passe suivante recréait les 10
        # familles à l'identique. Mesure à blanc du 28/07 : 1 860 entrées /
        # 225 familles du stock actuel seraient refusées. Refus BRUYANT,
        # même règle que l'adoption (seuil du lot 10, tolérés, parenté).
        from noms_empoisonnes import (SEUIL_PORTEURS, TOLERES,
                                      empoisonne, parente)
        porteurs_noms = {}
        for _en, _fr in traductions.get("noms", {}).items():
            if isinstance(_fr, str) and _fr.strip():
                porteurs_noms.setdefault(_fr.strip(), []).append(_en)
        refus_barriere = []
        # LES REJETS CHRONIQUES (bloc E, 29/07/2026). 15 textes refaisaient
        # le MÊME échec déterministe à chaque passage depuis le 25/07
        # (Google fusionne les jetons $b$b, codes_intacts refuse) : le
        # compteur « à traduire » mentait d'autant. Après 3 échecs, un
        # texte est CONSIGNÉ dans traductions/rejets_chroniques.json,
        # sorti de la file et compté à part — visible, plus jamais du
        # bruit. Le vider (ou --retenter) redonne leur chance à tous.
        chemin_rejets = os.path.join(TRADUCTIONS, "rejets_chroniques.json")
        rejets, motif_purge = charger_rejets(chemin_rejets)
        if motif_purge:
            self.journal("REJETS CHRONIQUES : compteurs remis à ZÉRO — %s. "
                         "Les consignés repassent en file." % motif_purge)
        retenter = "--retenter" in sys.argv
        if retenter and rejets:
            self.journal("(--retenter : %d rejet(s) chronique(s) remis en "
                         "file)" % len(rejets))
            rejets = {}
        echecs_du_passage = []
        for champ in champs:
            file_champ = [t for t in textes.get(champ, [])
                          if t and t not in traductions[champ]]
            consignes = [t for t in file_champ if rejets.get(t, 0) >= 3]
            restants = [t for t in file_champ if rejets.get(t, 0) < 3]
            if limite:
                restants = restants[:limite]
            self.bilan["tentees"] += len(restants)
            self.bilan["ecartees"] += len(consignes)
            self.journal("Sorts - %s : %d à traduire%s"
                         % (champ, len(restants),
                            " (+%d insolubles consignés)" % len(consignes)
                            if consignes else ""))
            debut = time.time()

            def traiter(texte, champ=champ):
                """Traduit un texte ; renvoie (texte, français) ou None."""
                if not self.actif:
                    return None
                fr = traduire_google(texte)
                if fr and champ == "noms":
                    fr_s = fr.strip()
                    with verrou:
                        cles = porteurs_noms.get(fr_s, [])
                        if empoisonne(texte, fr_s) or (
                                len(cles) >= SEUIL_PORTEURS
                                and fr_s not in TOLERES
                                and not parente(cles + [texte])):
                            refus_barriere.append((texte, fr_s))
                            return None
                        porteurs_noms.setdefault(fr_s, []).append(texte)
                return (texte, fr) if fr else None

            # Plusieurs requêtes en vol : le temps est passé à attendre le
            # réseau, pas à calculer. On reste modeste pour ne pas se faire
            # limiter par Google.
            fait = 0
            with futures.ThreadPoolExecutor(max_workers=PARALLELE) as pool:
                for texte_src, resultat in zip(restants,
                                               pool.map(traiter, restants)):
                    if not self.actif:
                        break
                    fait += 1
                    if resultat:
                        with verrou:
                            traductions[champ][resultat[0]] = resultat[1]
                            total += 1
                    else:
                        echecs_du_passage.append(texte_src)
                    if fait % 200 == 0:
                        sauver_json(cible, traductions)
                        vitesse = fait / max(time.time() - debut, 1)
                        reste = (len(restants) - fait) / max(vitesse, 0.01)
                        self.journal("  %d/%d (%.1f/s, ~%d min restantes)"
                                     % (fait, len(restants), vitesse,
                                        reste / 60))
        sauver_json(cible, traductions)
        # Consigne les échecs du passage : au 3e échec d'affilée, le texte
        # sort de la file (rejet chronique — voir plus haut). Un passage
        # SANS tentative (interrompu) ne compte pas.
        if echecs_du_passage and self.actif:
            nouveaux_consignes = 0
            for t in echecs_du_passage:
                rejets[t] = rejets.get(t, 0) + 1
                if rejets[t] == 3:
                    nouveaux_consignes += 1
            sauver_rejets(chemin_rejets, rejets)
            if nouveaux_consignes:
                self.journal("REJETS CHRONIQUES : %d texte(s) consigné(s) "
                             "après 3 échecs — détail : "
                             "traductions/rejets_chroniques.json"
                             % nouveaux_consignes)
        self.bilan["traduites"] += total
        self.bilan["refusees"] += len(echecs_du_passage)
        self.journal("Sorts : %d nouvelles traductions." % total)
        if refus_barriere:
            self.journal("BARRIÈRE D'ÉCRITURE : %d nom(s) refusé(s) "
                         "(famille sur-portée ou poison) :"
                         % len(refus_barriere))
            for _t, _f in refus_barriere[:8]:
                self.journal("   %r -> %r" % (_t[:40], _f[:40]))
        if total:
            self._generer_sorts()
            self.journal("DB_Sorts.lua régénérée -> /reload en jeu !")

    def _generer_sorts(self):
        # Sans client, il n'y a NULLE PART où écrire DB_Sorts.lua ni le
        # pont : on le dit et on saute — les traductions, elles, sont déjà
        # posées dans traductions/sorts.json (programme 31, bloc A).
        if not client_present():
            self.journal("CLIENT ABSENT : génération de DB_Sorts.lua et "
                         "du pont SAUTÉE (traductions posées, bases non "
                         "régénérées). Réglage : ASCENSIONFR_JEU.")
            return
        ancien = sys.argv
        sys.argv = ["generateur_sorts.py"]
        try:
            import generateur_sorts
            import importlib
            importlib.reload(generateur_sorts)
            db = generateur_sorts.main()
            from generateur_db import ecrire_db
            ecrire_db("DB_Sorts.lua", "Sorts", db, True)
        except Exception as e:
            self.journal("  ! génération des sorts : %s" % e)
            return
        finally:
            sys.argv = ancien
        # Le PONT des noms suit DB_Sorts.lua, pas le cache : sa couche
        # « custom » relit le fichier qu'on vient d'écrire. L'oublier laissait
        # DB_SortsNoms.lua vivre sur sa version d'avant — le trou de chaîne
        # relevé au lot 10, même famille que l'oubli de DB_Objets au lot 3.
        self._generer_pont("generer_noms_sorts.py")

    def _generer_pont(self, script):
        """Régénère un pont par nom, en sous-processus.

        Sous-processus et pas import : ces scripts travaillent au niveau
        module (ils s'exécutent à l'import), un reload serait fragile. Le
        python est celui qui nous exécute — l'Atelier nous lance déjà avec
        celui de la machine.
        """
        import subprocess
        r = subprocess.run(
            [sys.executable, os.path.join(BASE, "outils", script)],
            cwd=BASE, capture_output=True, text=True)
        if r.returncode == 0:
            derniere = (r.stdout or "").strip().splitlines()
            self.journal("  %s : %s" % (script, derniere[-1] if derniere
                                        else "fait"))
        else:
            self.journal("  ! %s : code %d — %s"
                         % (script, r.returncode,
                            (r.stderr or r.stdout or "").strip()[:200]))

    def cycle(self):
        """Un cycle complet : parse WDB -> génère -> traduit -> régénère."""
        self.journal("Lecture de ce que le jeu vous a envoyé...")
        try:
            rapport = parser_wdb.parse_dir(WDB, EXTRAITS)
            # Distinguer nettement l'INVENTAIRE (tout ce qui a été rencontré
            # en jeu) des TRADUCTIONS faites ensuite : les deux chiffres se
            # suivent dans le journal et prêtent à confusion.
            self.journal("  Rencontré en jeu à ce jour : " + ", ".join(
                "%s %s" % (v, k) for k, v in rapport.items()))
        except Exception as e:
            self.journal("  ! erreur de lecture des caches : %s" % e)
            return

        # Première génération : produit a_traduire/ à jour
        self._generer()

        total = 0
        # Compté d'avance pour que l'Atelier affiche une VRAIE barre plutôt
        # qu'un texte qui défile trop vite (la récolte est lue ici, une seule
        # fois, et réutilisée plus bas).
        recolte = lire_recolte()
        self._faits = 0
        self._a_faire = self._compter_a_faire(recolte)
        if self._a_faire:
            self.journal("  %d texte(s) à traduire." % self._a_faire)
            self.avancer("préparation")
            self._faits = 0

        # --- contenu WDB custom --------------------------------------
        at_q = charger_json(os.path.join(A_TRADUIRE, "quetes.json"))
        tr_q = charger_json(os.path.join(TRADUCTIONS, "quetes.json"))
        restants_q = [(qid, q) for qid, q in at_q.items() if qid not in tr_q]

        def traduire_quete(paire):
            qid, q = paire
            entree = {}
            for champ_wdb, champ_db in [("Title", "T"), ("Objectives", "O"),
                                        ("Details", "D"), ("EndText", "F"),
                                        ("CompletedText", "A")]:
                if q.get(champ_wdb):
                    fr = traduire_google(q[champ_wdb])
                    if fr:
                        entree[champ_db] = fr
            if q.get("ObjectiveTexts"):
                entree["OT"] = [(traduire_google(ot) or ot) if ot else ""
                                for ot in q["ObjectiveTexts"]]
            return qid, entree

        # Les quêtes coûtent cher (jusqu'à 5 textes chacune) et passaient en
        # PREMIER, à la file : elles donnaient à elles seules l'impression que
        # l'atelier était bloqué. Menées de front comme le reste.
        faites_q = 0
        with futures.ThreadPoolExecutor(max_workers=PARALLELE) as pool:
            for qid, entree in pool.map(traduire_quete, restants_q):
                if entree.get("T"):
                    tr_q[qid] = entree
                    total += 1
                    faites_q += 1
                    self.journal("    + quête %s : %s"
                                 % (qid, entree["T"][:50]))
                    if faites_q % 50 == 0:
                        sauver_json(os.path.join(TRADUCTIONS, "quetes.json"),
                                    tr_q)
                self.avancer("quête %s" % qid)
        sauver_json(os.path.join(TRADUCTIONS, "quetes.json"), tr_q)

        for nom_at, nom_tr, champs in [
            ("objets.json", "objets.json", [("Name", "N"), ("Description", "D")]),
            ("creatures.json", "creatures.json", [("Name", "N"), ("SubName", "S")]),
            ("objets_monde.json", "objets_monde.json", [("Name", "N")]),
        ]:
            at = charger_json(os.path.join(A_TRADUIRE, nom_at))
            tr = charger_json(os.path.join(TRADUCTIONS, nom_tr))
            restants = [(oid, o) for oid, o in at.items() if oid not in tr]

            def traduire_un(paire):
                oid, o = paire
                entree = {}
                for champ_wdb, champ_db in champs:
                    if o.get(champ_wdb):
                        fr = traduire_google(o[champ_wdb])
                        if fr:
                            entree[champ_db] = fr
                return oid, entree

            # PARALLÈLE : le temps se passe à ATTENDRE le réseau, pas à
            # calculer. Les sorts profitaient déjà de cette accélération, pas
            # les objets — d'où des heures d'attente pour rien.
            n = 0
            with futures.ThreadPoolExecutor(max_workers=PARALLELE) as pool:
                for oid, entree in pool.map(traduire_un, restants):
                    if entree:
                        tr[oid] = entree
                        n += 1
                        # Sauvegarde régulière : un gros lot peut demander une
                        # heure. Tout garder en mémoire, c'est risquer de TOUT
                        # perdre sur une simple coupure.
                        if n % 100 == 0:
                            sauver_json(os.path.join(TRADUCTIONS, nom_tr), tr)
                    self.avancer(entree.get("N") or nom_at)
            if n:
                sauver_json(os.path.join(TRADUCTIONS, nom_tr), tr)
                self.journal("    + %d entrées %s" % (n, nom_tr))
                total += n

        for nom in ["textes_pnj.json", "pages.json"]:
            at = charger_json(os.path.join(A_TRADUIRE, nom))
            tr = charger_json(os.path.join(TRADUCTIONS, nom))
            n = self._traduire_lot(((k, k) for k in at), tr)
            if n:
                sauver_json(os.path.join(TRADUCTIONS, nom), tr)
                total += n

        # --- récolte de l'addon ---------------------------------------
        if recolte:
            tr_d = charger_json(os.path.join(TRADUCTIONS, "divers.json"))
            tr_go = charger_json(os.path.join(TRADUCTIONS, "gossip.json"))
            tr_t = charger_json(os.path.join(TRADUCTIONS, "textes_pnj.json"))
            tr_p = charger_json(os.path.join(TRADUCTIONS, "pages.json"))
            # Sorts récoltés en jeu : fichier distinct de sorts.json, qui lui
            # contient les textes issus des DBC ({noms}, {descriptions}).
            tr_s = charger_json(os.path.join(TRADUCTIONS, "sorts_recoltes.json"))
            tr_q = charger_json(os.path.join(TRADUCTIONS, "quetes.json"))

            total += self._traduire_lot(
                ((k, k) for k in recolte.get("Gossip", {})), tr_go)
            total += self._traduire_lot(
                ((k, k) for k in recolte.get("TextesPNJ", {})), tr_t)
            total += self._traduire_lot(
                ((k, k) for k in recolte.get("Pages", {})), tr_p)
            total += self._traduire_lot(
                ((k, k) for k in recolte.get("Divers", {})), tr_d)
            # Textes de progression/rendu de quêtes (par ID)
            for categorie, champ in [("QuetesProgres", "P"), ("QuetesRendu", "R")]:
                for qid, texte in recolte.get(categorie, {}).items():
                    qid = str(int(qid))
                    if isinstance(texte, str) and texte:
                        entree = tr_q.setdefault(qid, {})
                        if champ not in entree:
                            self.bilan["tentees"] += 1
                            fr = traduire_google(texte)
                            if fr:
                                entree[champ] = fr
                                total += 1
                                self.bilan["traduites"] += 1
                                time.sleep(0.3)
                            else:
                                self.bilan["refusees"] += 1
                            self.avancer("quête %s" % qid)
            # Sorts récoltés (nom + description d'info-bulle)
            for sid, s in recolte.get("Sorts", {}).items():
                sid = str(int(sid))
                if sid in tr_s or not isinstance(s, dict):
                    continue
                entree = {}
                if s.get("N"):
                    self.bilan["tentees"] += 1
                    fr = traduire_google(s["N"])
                    if fr:
                        entree["N"] = fr
                        self.bilan["traduites"] += 1
                    else:
                        self.bilan["refusees"] += 1
                if s.get("D"):
                    self.bilan["tentees"] += 1
                    fr = traduire_google(s["D"])
                    if fr:
                        entree["D"] = fr
                        self.bilan["traduites"] += 1
                    else:
                        self.bilan["refusees"] += 1
                if entree:
                    tr_s[sid] = entree
                    total += 1
                    time.sleep(0.3)
                self.avancer(entree.get("N") or ("sort %s" % sid))

            sauver_json(os.path.join(TRADUCTIONS, "divers.json"), tr_d)
            sauver_json(os.path.join(TRADUCTIONS, "gossip.json"), tr_go)
            sauver_json(os.path.join(TRADUCTIONS, "textes_pnj.json"), tr_t)
            sauver_json(os.path.join(TRADUCTIONS, "pages.json"), tr_p)
            sauver_json(os.path.join(TRADUCTIONS, "sorts_recoltes.json"), tr_s)
            sauver_json(os.path.join(TRADUCTIONS, "quetes.json"), tr_q)
            if recolte.get("Sorts"):
                self._generer_sorts()

        # --- signalements du joueur (/afr signaler) --------------------
        # Diagnostic hors-jeu avec le vrai moteur de l'addon : rapport dans
        # traductions/rapport_signalements.txt. Module rechargé à chaque
        # cycle pour suivre ses modifications sans redémarrer le compagnon.
        try:
            import importlib
            import diagnostiquer_signalements
            importlib.reload(diagnostiquer_signalements)
            n = diagnostiquer_signalements.executer(journal=self.journal)
            if n:
                self.journal("  %d signalement(s)/échec(s) diagnostiqués -> "
                             "traductions/rapport_signalements.txt" % n)
        except Exception as e:
            self.journal("  ! diagnostic des signalements : %s" % e)

        if total:
            self.journal("  %d nouvelle(s) traduction(s)." % total)
            self._generer()
            self.journal("  Bases Lua régénérées -> tapez /reload en jeu !")
        else:
            self.journal("  Rien de nouveau à traduire.")
        self.dire_bilan()

    def _generer(self):
        ancien_argv = sys.argv
        sys.argv = ["generateur_db.py", "--base", BASE]
        try:
            generateur_db.main()
        finally:
            sys.argv = ancien_argv
        # Même trou de chaîne que pour les sorts : le pont des noms d'objets
        # suit objets.json / objets_dbc.json, que ce cycle vient peut-être
        # d'enrichir. Sans cette ligne, DB_ObjetsNoms.lua ne bouge jamais.
        self._generer_pont("generer_noms_objets.py")

    # -- mise à jour après un patch d'Ascension --------------------------
    def verifier_client(self):
        """Si Ascension a patché son client, tout réextraire avant de jouer.

        Sans cela : nouveaux sorts en anglais, et surtout liste noire
        anti-blocage périmée — les barres d'action du joueur pourraient se
        retrouver bloquées.
        """
        try:
            sys.path.insert(0, os.path.join(BASE, "outils"))
            import mise_a_jour
            modifie, raison = mise_a_jour.client_modifie()
            if not modifie:
                return
            self.journal("Ascension a mis à jour le jeu (%s)." % raison)
            self.journal("Remise à niveau de la traduction, patientez...")
            if mise_a_jour.executer(journal=self.journal):
                self.journal("Traduction remise à niveau. /reload en jeu.")
            else:
                self.journal("! La remise à niveau a échoué : la traduction")
                self.journal("  reste dans son état précédent (rien n'est perdu).")
        except Exception as e:
            self.journal("! Vérification du client impossible : %s" % e)

    # -- boucle de surveillance ----------------------------------------
    def boucle(self):
        self.actif = True
        self.journal("=== Compagnon AscensionFR actif ===")
        self.verifier_client()
        self.journal("Surveillance : " + WDB)
        self.changements()  # initialise les mtimes
        self.cycle()        # premier passage immédiat
        while self.actif:
            time.sleep(5)
            if self.actif and self.changements():
                self.journal("Changement détecté...")
                # Le client écrit les WDB par vagues : on attend un peu.
                time.sleep(3)
                self.cycle()


# ---------------------------------------------------------------------------
# Interfaces
# ---------------------------------------------------------------------------
def mode_console(une_fois=False):
    c = Compagnon()
    if une_fois:
        # Une passe complète : d'abord vérifier qu'Ascension n'a pas patché le
        # client (liste noire à rafraîchir), puis traduire tout le nouveau
        # (les WDB de cette machine + les caches versés par les joueurs).
        c.verifier_client()
        c.cycle()
    else:
        try:
            c.boucle()
        except KeyboardInterrupt:
            print("\nArrêt.")


def mode_graphique(auto=False):
    import tkinter as tk
    from tkinter import scrolledtext

    racine = tk.Tk()
    racine.title("AscensionFR - Traduction")
    racine.geometry("640x420")
    racine.configure(bg="#1e1e2e")
    try:
        racine.iconify() if auto else None
    except Exception:
        pass

    titre = tk.Label(racine, text="Compagnon de traduction AscensionFR",
                     font=("Helvetica", 13, "bold"),
                     bg="#1e1e2e", fg="#89b4fa")
    titre.pack(pady=8)

    console = scrolledtext.ScrolledText(
        racine, wrap=tk.WORD, font=("Consolas", 9),
        bg="#181825", fg="#cdd6f4", bd=0, state=tk.DISABLED)

    def journal(message):
        console.config(state=tk.NORMAL)
        console.insert(tk.END, "[%s] %s\n" % (time.strftime("%H:%M:%S"), message))
        console.see(tk.END)
        console.config(state=tk.DISABLED)

    compagnon = Compagnon(journal=lambda m: racine.after(0, journal, m))
    fil = {"t": None}

    boutons = tk.Frame(racine, bg="#1e1e2e")
    boutons.pack(pady=4)

    def demarrer():
        if fil["t"] and fil["t"].is_alive():
            return
        fil["t"] = threading.Thread(target=compagnon.boucle, daemon=True)
        fil["t"].start()
        btn_start.config(state=tk.DISABLED)
        btn_stop.config(state=tk.NORMAL)

    def arreter():
        compagnon.actif = False
        journal("Arrêt demandé.")
        btn_start.config(state=tk.NORMAL)
        btn_stop.config(state=tk.DISABLED)

    btn_start = tk.Button(boutons, text="Démarrer", command=demarrer,
                          bg="#a6e3a1", fg="#11111b",
                          font=("Helvetica", 10, "bold"), padx=14, pady=4, bd=0)
    btn_start.grid(row=0, column=0, padx=8)
    btn_stop = tk.Button(boutons, text="Arrêter", command=arreter,
                         state=tk.DISABLED, bg="#313244", fg="#cdd6f4",
                         font=("Helvetica", 10, "bold"), padx=14, pady=4, bd=0)
    btn_stop.grid(row=0, column=1, padx=8)

    console.pack(padx=14, pady=8, fill=tk.BOTH, expand=True)
    journal("Laissez cette fenêtre ouverte (réduite) pendant que vous jouez.")
    journal("Les textes anglais rencontrés seront traduits automatiquement ;")
    journal("tapez /reload en jeu quand de nouvelles traductions sont prêtes.")

    def fermeture():
        compagnon.actif = False
        racine.destroy()

    racine.protocol("WM_DELETE_WINDOW", fermeture)
    if auto:
        racine.after(400, demarrer)
    racine.mainloop()


def mode_sorts():
    """Traduit les sorts de classe restants puis quitte.

    --champ noms|descriptions : ne traiter qu'une catégorie (permet de confier
    les noms à des agents IA pendant que Google fait les descriptions).
    """
    limite = None
    if "--limite" in sys.argv:
        limite = int(sys.argv[sys.argv.index("--limite") + 1])
    champs = ("noms", "descriptions")
    if "--champ" in sys.argv:
        champs = (sys.argv[sys.argv.index("--champ") + 1],)
    c = Compagnon()
    c.actif = True
    try:
        c.cycle_sorts(limite=limite, champs=champs)
    except KeyboardInterrupt:
        print("\nInterrompu - la progression est sauvegardée, relancez pour "
              "reprendre où vous en étiez.")
    c.dire_bilan()


if __name__ == "__main__":
    if "--sorts" in sys.argv:
        # --sorts traduit SANS le client (a_traduire -> traductions) ;
        # seule la régénération des bases est sautée s'il manque.
        mode_sorts()
    else:
        # Tous les autres modes vivent du client (WDB, WTF, DB_*.lua) :
        # son absence doit se voir ICI, pas au fond d'un cycle.
        exiger_client("traducteur_fr (cycle complet)")
        if "--une-fois" in sys.argv:
            mode_console(une_fois=True)
        elif "--console" in sys.argv:
            mode_console()
        else:
            # --auto : démarre la surveillance sans clic (raccourci du bureau)
            mode_graphique(auto="--auto" in sys.argv)
