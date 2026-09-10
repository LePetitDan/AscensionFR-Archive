# -*- coding: utf-8 -*-
r"""BANC DU DOUBLE ESSAI DE DÉLIMITEUR (bloc A du programme 5, 29/07/2026).

CE QU'IL FAUT PROUVER, et c'est tout le sujet : le second essai est
ADDITIF. Un texte qui se traduit aujourd'hui doit prendre exactement le
même chemin qu'aujourd'hui, à l'octet près ; le repli « ¤n¤ » ne doit
exister que là où le bouclier « [n] » a déjà rendu None.

POURQUOI CE BANC N'EST PAS UNE SIMPLE COMPARAISON DE DEUX APPELS.
Google n'est pas déterministe à 100 % : deux appels sur le même texte
peuvent rendre deux phrases légèrement différentes. Comparer « avant »
et « après » en interrogeant deux fois produirait des ROUGES FAUX — le
défaut même qu'on passe la semaine à traquer. Donc :

  1. on ENREGISTRE une fois la réponse de Google pour chaque charge utile
     (celle du bouclier, celle du repli) ;
  2. on REJOUE cette même réponse dans les DEUX versions du module — la
     copie d'avant modification et celle d'aujourd'hui — en détournant
     urllib.request.urlopen ;
  3. on compare les sorties octet pour octet.

Aucune ré-implémentation : les deux côtés sont le VRAI code, l'ancien lu
depuis une copie figée du fichier, le nouveau depuis le dépôt. Un écart
ne peut donc venir que de la modification.

Usage :
    python outils/banc_double_essai.py --avant <copie_figee_traducteur.py>

Sortie : code 0 si la propriété additive tient, 1 sinon.
"""
import importlib.util
import io
import json
import os
import random
import sys
import time
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(BASE, "outils"))

import traducteur_fr as apres  # noqa: E402

VRAI_URLOPEN = urllib.request.urlopen
REJETS = os.path.join(BASE, "traductions", "rejets_chroniques.json")
SORTS = os.path.join(BASE, "traductions", "sorts.json")


def charger(chemin, defaut=None):
    if not os.path.exists(chemin):
        return {} if defaut is None else defaut
    with io.open(chemin, encoding="utf-8") as f:
        return json.load(f)


def importer_avant(chemin):
    """Charge la copie FIGÉE du module d'avant modification, sous un autre
    nom, pour que les deux vivent côte à côte dans le même processus."""
    spec = importlib.util.spec_from_file_location("traducteur_avant", chemin)
    module = importlib.util.module_from_spec(spec)
    sys.modules["traducteur_avant"] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# L'enregistreur / rejoueur de réponses Google
# ---------------------------------------------------------------------------
class Reponse(object):
    """Le strict minimum de ce que le code appelant attend d'urlopen."""

    def __init__(self, brut):
        self._brut = brut

    def read(self):
        return self._brut

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def charge_utile(url):
    """Extrait le texte réellement envoyé (le paramètre q=)."""
    return urllib.parse.unquote_plus(url.split("&q=", 1)[1])


def appeler_vrai(protege, essais=4):
    url = ("https://translate.googleapis.com/translate_a/single"
           "?client=gtx&sl=en&tl=fr&dt=t&q=" + urllib.parse.quote(protege))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    dernier = None
    for n in range(essais):
        try:
            with VRAI_URLOPEN(req, timeout=20) as r:
                return r.read()
        except Exception as exc:          # 429 surtout : Google limite
            dernier = exc
            time.sleep(1.5 * (n + 1))
    raise dernier


def enregistrer(textes, module):
    """Pour chaque texte, la réponse de Google aux DEUX charges utiles.
    Une seule interrogation par charge : c'est elle qu'on rejouera."""
    bande, manques = {}, []
    for i, x in enumerate(textes, 1):
        texte = module.traduire_pluriels(x)
        glosse, _mots = module.proteger_glossaire(texte)
        charges = [module.proteger(glosse)[0],
                   module.proteger_repli(glosse)[0]]
        for p in charges:
            if p in bande or module.rien_a_traduire(p):
                continue
            try:
                bande[p] = appeler_vrai(p)
            except Exception as exc:
                manques.append((x, type(exc).__name__))
            time.sleep(0.25)
        if i % 10 == 0:
            print("   … %d/%d enregistrés" % (i, len(textes)))
    return bande, manques


def rejouer(bande):
    """Détourne urlopen : plus un octet ne part sur le réseau, les deux
    versions du module reçoivent la MÊME réponse."""
    inconnues = []

    def faux_urlopen(req, timeout=None):
        p = charge_utile(req.full_url if hasattr(req, "full_url") else req)
        if p not in bande:
            inconnues.append(p)
            raise IOError("charge utile non enregistrée")
        return Reponse(bande[p])

    urllib.request.urlopen = faux_urlopen
    return inconnues


def sortie(module, texte):
    module._deja_traduit.clear()
    return module.traduire_google(texte)


# ---------------------------------------------------------------------------
def main():
    if "--avant" not in sys.argv:
        print("usage : banc_double_essai.py --avant <copie_figee.py>")
        return 2
    chemin_avant = sys.argv[sys.argv.index("--avant") + 1]
    if not os.path.isfile(chemin_avant):
        print("copie d'avant introuvable :", chemin_avant)
        return 2
    avant = importer_avant(chemin_avant)

    # --- les deux populations ---------------------------------------------
    consignes = sorted(charger(REJETS, {}))
    cache = charger(SORTS).get("descriptions", {})
    avec_codes = sorted(x for x in cache
                        if 60 < len(x) < 400
                        and len(apres.MOTIF_BOUCLIER.findall(x)) >= 2)
    qui_passent = random.Random(4).sample(avec_codes, 25)

    print("=" * 68)
    print("BANC DU DOUBLE ESSAI — preuve AVANT la pose")
    print("=" * 68)
    print("population 1 : %d consignés (on veut en récupérer)" % len(consignes))
    print("population 2 : %d qui passent (on veut 25/25 IDENTIQUES)"
          % len(qui_passent))

    # --- 0. la charge utile du PREMIER essai n'a pas bougé -----------------
    print("\n--- 0. la charge utile du premier essai est-elle inchangée ? ---")
    ecarts = 0
    for x in consignes + qui_passent:
        g1 = avant.proteger_glossaire(avant.traduire_pluriels(x))[0]
        g2 = apres.proteger_glossaire(apres.traduire_pluriels(x))[0]
        if avant.proteger(g1)[0] != apres.proteger(g2)[0]:
            ecarts += 1
    print("    %d écart(s) sur %d textes"
          % (ecarts, len(consignes) + len(qui_passent)))

    # --- 1. enregistrement -------------------------------------------------
    print("\n--- 1. enregistrement des réponses de Google (une par charge) ---")
    bande, manques = enregistrer(consignes + qui_passent, apres)
    print("    %d charge(s) utile(s) enregistrée(s), %d panne(s) réseau"
          % (len(bande), len(manques)))

    # --- 2. rejeu ----------------------------------------------------------
    print("\n--- 2. rejeu de la MÊME réponse dans les deux versions ---")
    inconnues = rejouer(bande)

    changes, casses, ok_identiques = [], [], 0
    for x in qui_passent:
        a = sortie(avant, x)
        b = sortie(apres, x)
        if a is None:
            casses.append(("le texte de référence échoue DÉJÀ", x))
        elif a != b:
            changes.append((x, a, b))
        else:
            ok_identiques += 1

    recuperes, toujours = 0, 0
    faux_positifs = []
    for x in consignes:
        a = sortie(avant, x)
        b = sortie(apres, x)
        if a is not None:
            faux_positifs.append(x)      # il ne devrait PAS passer avant
        if b is not None:
            recuperes += 1
        else:
            toujours += 1

    # --- 3. verdict --------------------------------------------------------
    print("\n" + "=" * 68)
    print("POPULATION QUI PASSE DÉJÀ (%d)" % len(qui_passent))
    print("   sorties IDENTIQUES octet pour octet : %d" % ok_identiques)
    print("   sorties CHANGÉES                    : %d" % len(changes))
    print("   non éprouvables (échec déjà avant)  : %d" % len(casses))
    for x, a, b in changes[:5]:
        print("   ! EN : %s" % x[:90].replace("\n", "|"))
        print("     avant : %s" % (a or "")[:90].replace("\n", "|"))
        print("     après : %s" % (b or "")[:90].replace("\n", "|"))

    print("\nPOPULATION CONSIGNÉE (%d)" % len(consignes))
    print("   récupérés par le second essai       : %d" % recuperes)
    print("   toujours refusés                    : %d" % toujours)
    if faux_positifs:
        print("   ⚠ %d passaient déjà AVANT (le consigné était périmé)"
              % len(faux_positifs))
    if inconnues:
        print("\n⚠ %d charge(s) utile(s) réclamée(s) hors bande" % len(inconnues))

    print("\n" + "=" * 68)
    if ecarts or changes:
        print("🛑 PROPRIÉTÉ ADDITIVE BRISÉE — ne pas poser.")
        return 1
    print("✅ PROPRIÉTÉ ADDITIVE VÉRIFIÉE : %d/%d sorties identiques, "
          "%d consigné(s) récupéré(s)."
          % (ok_identiques, len(qui_passent) - len(casses), recuperes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
