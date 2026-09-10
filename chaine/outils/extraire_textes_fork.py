# -*- coding: utf-8 -*-
"""
Extrait les textes anglais d'un addon Lua à franciser (forks ProfetGit).
========================================================================
Première étape de la chaîne des forks (voir CONTEXTE §3.29) :

    extraire_textes_fork.py  →  je traduis la liste  →  franciser_fork.py

Parcourt tous les .lua d'un addon et relève chaque chaîne littérale avec son
contexte (fichier, ligne, texte de la ligne), classée en trois paniers :

  - « visibles »   : très probablement lues par le joueur (à traduire) ;
  - « douteuses »  : à trancher à la main (mot seul, format ambigu…) ;
  - « techniques » : chemins, événements, motifs Lua, clés — NE PAS traduire.

Le classement est un TRI D'AIDE, pas un verdict : la traduction finale se
décide sur la liste, pas ici. Les doublons sont regroupés (une chaîne = une
entrée, toutes ses positions).

Usage :
    python extraire_textes_fork.py <dossier_addon> <sortie.json>
"""
import io
import json
import os
import re
import sys

# Chaîne littérale Lua : "..." ou '...' (échappements gérés), sur UNE ligne.
# Les longs crochets [[...]] sont rares dans ces addons — relevés à part.
MOTIF_CHAINE = re.compile(r'"((?:[^"\\]|\\.)*)"|\'((?:[^\'\\]|\\.)*)\'')

# Indices de contexte « visible » : la chaîne nourrit un affichage.
CTX_VISIBLE = re.compile(
    r'Print|print|SetText|AddMessage|message|toast|title|label|tooltip'
    r'|GameTooltip|:AddLine|text\s*=|desc\s*=|name\s*=|UIErrorsFrame',
    re.IGNORECASE)

# Indices de contexte « technique » : la chaîne est une clé ou un motif.
CTX_TECHNIQUE = re.compile(
    r':find\(|:match\(|:gsub\(|string\.find|string\.match|string\.gsub'
    r'|RegisterEvent|CreateFrame|GetTexture|SetTexture|PlaySound'
    r'|GetItemInfo|GetSpellInfo|\[\s*$')


def classer(chaine, ctx):
    """Rend le panier d'une chaîne selon sa forme et sa ligne d'origine."""
    if "\\\\" in chaine or chaine.startswith("Interface"):
        return "techniques"                     # chemin de fichier/texture
    if re.fullmatch(r"[A-Z0-9_]+", chaine):
        return "techniques"                     # événement, constante
    if re.fullmatch(r"[^A-Za-z]*", chaine):
        return "techniques"                     # ponctuation, chiffres seuls
    if len(chaine) < 3 and " " not in chaine:
        return "techniques"
    lettres = len(re.findall(r"[A-Za-z]", chaine))
    if CTX_TECHNIQUE.search(ctx) and not CTX_VISIBLE.search(ctx):
        return "douteuses" if " " in chaine else "techniques"
    if " " in chaine and lettres >= 4:
        return "visibles"
    if CTX_VISIBLE.search(ctx) and lettres >= 3:
        return "visibles"
    return "douteuses"


def extraire(dossier):
    paniers = {"visibles": {}, "douteuses": {}, "techniques": {}}
    for racine, _dossiers, fichiers in os.walk(dossier):
        for nom in sorted(fichiers):
            if not nom.lower().endswith(".lua"):
                continue
            chemin = os.path.join(racine, nom)
            relatif = os.path.relpath(chemin, dossier)
            with io.open(chemin, encoding="utf-8", errors="replace") as f:
                for numero, ligne in enumerate(f, 1):
                    # Les commentaires ne s'affichent jamais.
                    code = ligne.split("--", 1)[0]
                    if '"' not in code and "'" not in code:
                        continue
                    ctx = ligne.strip()
                    for m in MOTIF_CHAINE.finditer(code):
                        chaine = m.group(1) if m.group(1) is not None \
                            else m.group(2)
                        if not chaine:
                            continue
                        panier = classer(chaine, ctx)
                        entree = paniers[panier].setdefault(
                            chaine, {"positions": [], "ctx": ctx[:120]})
                        entree["positions"].append(
                            "%s:%d" % (relatif, numero))
    return paniers


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage : extraire_textes_fork.py <dossier_addon> "
                         "<sortie.json>")
    dossier, sortie = sys.argv[1], sys.argv[2]
    paniers = extraire(dossier)
    os.makedirs(os.path.dirname(os.path.abspath(sortie)), exist_ok=True)
    with io.open(sortie, "w", encoding="utf-8") as f:
        json.dump(paniers, f, ensure_ascii=False, indent=1, sort_keys=True)
    for panier in ("visibles", "douteuses", "techniques"):
        print("%-12s %4d chaînes uniques" % (panier, len(paniers[panier])))
    print("écrit :", sortie)


if __name__ == "__main__":
    main()
