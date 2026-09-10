# -*- coding: utf-8 -*-
"""Le verdict d'une étape : des COMPTES, pas un code de retour.

LE VERT QUI MENT (programme 31, bloc F). Du 29/07 au 08/08, l'Atelier a
affiché « 7/7 vert » alors que deux candidats sur trois étaient refusés en
silence : vert voulait dire « code de retour zéro », pas « a traduit ».
Chaque étape imprime désormais une ligne machine :

    @@BILAN {"tentees": N, "traduites": N, "refusees": N, "ecartees": N}

et ce module rend le verdict. LES TROIS CAS, distingués exprès :

  1. RIEN À FAIRE (tentées = 0)            -> VERT, légitimement ;
  2. DU TRAVAIL ET RIEN DE TRADUIT          -> ROUGE — la règle qui aurait
     (tentées > 0, traduites = 0, refus > 0)   crié dès le 29 juillet ;
  3. DU TRAVAIL ET UNE PARTIE TRADUITE      -> VERT jusqu'à la moitié de
     refus, ORANGE au-delà.

POURQUOI LA MOITIÉ : la fenêtre d'erreurs 500 du programme 30 a mangé
environ un tiers d'une passe, et la passe SUIVANTE a tout rattrapé — un
seuil plus nerveux crierait sur l'aléa d'une nuit. Perdre la MAJORITÉ
d'un passage, en revanche, doit se voir sans qu'on aille lire un journal.

Le code de sortie 3 (« client absent », chemin_client.py) est dit tel
quel : c'est un fait de configuration, pas une panne.
"""
import json
import re

RE_BILAN = re.compile(r"^@@BILAN (\{.*\})\s*$", re.M)

VERT, ORANGE, ROUGE = "vert", "orange", "rouge"

# Les étapes CONNUES instrumentées (programme 32, bloc C). Chez l'une
# d'elles, un @@BILAN absent n'est pas un vert neutre : c'est une ANOMALIE
# — l'étape est morte avant ses comptes, ou sa sortie n'a pas été capturée.
# C'était la porte de service laissée ouverte par le bloc F du 31 : une
# étape instrumentée qui meurt avant son bilan retombait dans l'ancien
# monde (code 0 = vert). Une étape HORS liste garde le vert neutre — elle
# n'a jamais promis de comptes.
ETAPES_INSTRUMENTEES = {
    "aspirer_discord.py",
    "ingerer_rapport.py",
    "ingerer_caches.py",
    "traducteur_fr.py",
    "traducteur_fr.py --sorts",
    "ingerer_recolte.py",
    "appliquer_vocabulaire.py",
    "aspirer_veille.py",
}


def extraire_bilan(sortie):
    """Le DERNIER @@BILAN d'une sortie d'étape, ou None (non instrumentée).
    Le dernier : une étape qui boucle (surveillance) émet un bilan par
    cycle, et c'est l'état final qui fait foi."""
    dernier = None
    for m in RE_BILAN.finditer(sortie or ""):
        dernier = m
    if not dernier:
        return None
    try:
        return json.loads(dernier.group(1))
    except ValueError:
        return None


def verdict(code, bilan, script=None):
    """(couleur, raison) pour une étape, d'après son code ET ses comptes.
    `script` : le nom de l'étape — s'il figure dans ETAPES_INSTRUMENTEES,
    un bilan absent est une anomalie ROUGE, jamais un vert."""
    if code == 3:
        return (ROUGE, "client absent (code 3)")
    if code not in (0, None):
        return (ROUGE, "code de retour %s" % code)
    if not bilan:
        if script in ETAPES_INSTRUMENTEES:
            return (ROUGE, "bilan attendu et ABSENT — l'étape est morte "
                    "avant ses comptes, ou sa sortie n'est pas capturée")
        return (VERT, "pas de comptes (étape non instrumentée)")
    tentees = bilan.get("tentees", 0)
    traduites = bilan.get("traduites", 0)
    refusees = bilan.get("refusees", 0)
    if tentees == 0:
        return (VERT, "rien à faire")
    if traduites == 0 and refusees > 0:
        return (ROUGE, "%d tentée(s) et RIEN de fait (%d refus)"
                % (tentees, refusees))
    if refusees * 2 > tentees:
        return (ORANGE, "%d refus sur %d tentées — la majorité du passage "
                "est perdue" % (refusees, tentees))
    return (VERT, "%d/%d faite(s)" % (traduites, tentees))


def verdict_global(verdicts):
    """La couleur du bandeau : la pire des étapes gagne."""
    couleurs = [c for c, _ in verdicts.values()]
    if ROUGE in couleurs:
        return ROUGE
    if ORANGE in couleurs:
        return ORANGE
    return VERT
