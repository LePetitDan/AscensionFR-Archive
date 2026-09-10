# -*- coding: utf-8 -*-
"""Récolte les arbres de talents CoA depuis la page en cache du CoA builder.

La page https://ascension.gg/en/v2/coa-builder/voljin embarque toutes les
données dans son flux RSC Next.js : des balises <script> contenant des appels
self.__next_f.push([1,"..."]) dont la charge est du texte JSON échappé.

Ce script lit le HTML en cache (sources/coa_builder_page.html), reconstitue le
flux RSC, puis en extrait :
  - la liste des classes CoA ({"tabs":[...],"classId":N,"className":"..."}),
  - le dictionnaire "entriesByTab" ({"classId:tabId":[talents...]}).

Il produit :
  - sources/coa_arbres.json      : jeu de données propre par classe,
  - rapports/ids_talents_coa.txt : tous les spellId uniques, un par ligne
                                   (filtre du lot d'usine n°31).

Usage : python recolter_coa_builder.py [chemin_html_en_cache]
"""

import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
HTML_CACHE = RACINE / "sources" / "coa_builder_page.html"
SORTIE_JSON = RACINE / "sources" / "coa_arbres.json"
SORTIE_IDS = RACINE / "rapports" / "ids_talents_coa.txt"

# Un appel push du flux RSC : la charge est une chaîne JSON (échappements \" \\ \n ...)
MOTIF_PUSH = re.compile(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)')

# Un objet classe complet, reconnaissable et plat (le tableau tabs ne contient
# que des objets simples, donc pas de crochet fermant interne).
MOTIF_CLASSE = re.compile(
    r'\{"tabs":\[[^\]]*\],"classId":\d+,"className":"(?:[^"\\]|\\.)*"\}'
)


def reconstituer_flux(html):
    """Concatène les charges des push RSC, déséchappées une à une.

    Si aucune charge ne se déséchappe (structure de page changée), on tente
    des profondeurs d'échappement décroissantes sur le HTML brut.
    """
    morceaux = []
    for m in MOTIF_PUSH.finditer(html):
        try:
            morceaux.append(json.loads('"' + m.group(1) + '"'))
        except ValueError:
            # Charge isolée illisible : on la saute plutôt que tout perdre.
            pass
    flux = "".join(morceaux)
    if '"entriesByTab"' in flux:
        return flux
    # Filets de secours : les données seraient à une autre profondeur.
    if '"entriesByTab"' in html:
        return html
    for profondeur in (1, 2, 3):
        candidat = html
        for _ in range(profondeur):
            candidat = candidat.replace('\\\\', '\x00').replace('\\"', '"')
            candidat = candidat.replace('\x00', '\\')
        if '"entriesByTab"' in candidat:
            return candidat
    raise SystemExit(
        "Impossible de trouver \"entriesByTab\" dans le flux RSC : "
        "la structure de la page a probablement changé."
    )


def extraire_classes(flux):
    """Retourne les classes {className, classId, tabs} dédupliquées par classId."""
    classes = {}
    for m in MOTIF_CLASSE.finditer(flux):
        obj = json.loads(m.group(0))
        classes.setdefault(obj["classId"], obj)
    return classes


def extraire_entrees_par_arbre(flux):
    """Fusionne toutes les occurrences du dictionnaire entriesByTab du flux."""
    decodeur = json.JSONDecoder()
    fusion = {}
    for m in re.finditer(r'"entriesByTab":', flux):
        debut = m.end()
        while debut < len(flux) and flux[debut] in ' \t\r\n':
            debut += 1
        try:
            objet, _ = decodeur.raw_decode(flux, debut)
        except ValueError:
            continue
        for cle, entrees in objet.items():
            fusion.setdefault(cle, entrees)
    if not fusion:
        raise SystemExit("Aucun dictionnaire entriesByTab lisible dans le flux.")
    return fusion


def condenser_talent(entree, ids_vus):
    """Réduit une entrée brute de talent au strict utile pour la traduction."""
    talent = {
        "spellId": entree.get("spellId"),
        "nom": entree.get("name"),
        "rangMax": entree.get("maxPoints"),
        "position": {"x": entree.get("x"), "y": entree.get("y")},
        "type": entree.get("entryType"),
        "arbre": entree.get("tabId"),
    }
    description = entree.get("description")
    if description:
        talent["description"] = description
    rangs = []
    for rang in entree.get("rankDescriptions") or []:
        rangs.append({
            "rang": rang.get("rank"),
            "spellId": rang.get("spellId"),
            "description": rang.get("description"),
        })
        if rang.get("spellId"):
            ids_vus.add(rang["spellId"])
    if rangs:
        talent["rangs"] = rangs
    if entree.get("spellId"):
        ids_vus.add(entree["spellId"])
    for sid in entree.get("spellIds") or []:
        if sid:
            ids_vus.add(sid)
    return talent


def principal():
    chemin_html = Path(sys.argv[1]) if len(sys.argv) > 1 else HTML_CACHE
    if not chemin_html.is_file():
        raise SystemExit("Cache HTML introuvable : %s" % chemin_html)
    html = chemin_html.read_text(encoding="utf-8")

    flux = reconstituer_flux(html)
    classes = extraire_classes(flux)
    entrees_par_arbre = extraire_entrees_par_arbre(flux)

    ids_vus = set()
    donnees = {"classes": []}
    cles_consommees = set()
    for class_id in sorted(classes):
        brut = classes[class_id]
        arbres = sorted(brut["tabs"], key=lambda t: (t.get("sortOrder", 0), t["tabId"]))
        talents = []
        for arbre in arbres:
            cle = "%d:%d" % (class_id, arbre["tabId"])
            for entree in entrees_par_arbre.get(cle, []):
                talents.append(condenser_talent(entree, ids_vus))
            cles_consommees.add(cle)
        donnees["classes"].append({
            "nom": brut["className"],
            "id": class_id,
            "arbres": [{"tabId": a["tabId"], "nom": a["tabName"],
                        "ordre": a.get("sortOrder", 0)} for a in arbres],
            "talents": talents,
        })

    orphelines = sorted(set(entrees_par_arbre) - cles_consommees)
    if orphelines:
        print("Attention : clés classId:tabId sans classe connue :", orphelines)

    SORTIE_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(SORTIE_JSON, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=1)

    SORTIE_IDS.parent.mkdir(parents=True, exist_ok=True)
    with open(SORTIE_IDS, "w", encoding="utf-8") as f:
        for sid in sorted(ids_vus):
            f.write("%d\n" % sid)

    nb_talents = sum(len(c["talents"]) for c in donnees["classes"])
    noms_arbres = sorted({a["nom"] for c in donnees["classes"] for a in c["arbres"]})
    print("Classes           :", len(donnees["classes"]))
    print("Talents           :", nb_talents)
    print("spellId uniques   :", len(ids_vus))
    print("Arbres distincts  :", len(noms_arbres))
    print("Noms d'arbres     :", ", ".join(noms_arbres))
    print("Écrit :", SORTIE_JSON)
    print("Écrit :", SORTIE_IDS)


if __name__ == "__main__":
    principal()
