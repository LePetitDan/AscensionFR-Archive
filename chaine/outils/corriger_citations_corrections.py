# -*- coding: utf-8 -*-
r"""Applique la règle des citations accentuées à DB_SortsCorrections.lua.

Cette base est la seule porteuse de textes français que la chaîne ne
régénère JAMAIS (ajout seul, par l'ingestion) : la règle posée dans
generateur_db.polir() ne peut pas la rattraper. On corrige donc sur place —
champs FRANÇAIS seulement (liste blanche d'accents_majuscules, et le 3ᵉ
argument des lignes aura(id, "EN", "FR")), jamais les modèles anglais.

Sauvegarde horodatée, compilation lua51 du résultat AVANT remplacement
(mieux vaut pas de passe qu'une base morte), recompte après.

Usage : python outils/corriger_citations_corrections.py [--ecrire]
"""
import io
import os
import re
import shutil
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import accents_majuscules as am  # noqa: E402
import mesurer_constantes  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIBLE = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface"
         r"\AddOns\AscensionFR\DB\DB_SortsCorrections.lua")

RE_AURA = re.compile(
    r'^(aura\(\d+,\s*"(?:[^"\\]|\\.)*",\s*")((?:[^"\\]|\\.)*)("\)\s*)$')
RE_CHAMP_FR = re.compile(
    r'([,{])(%s)="((?:[^"\\]|\\.)*)"'
    % "|".join(sorted(am.CHAMPS_FR, key=len, reverse=True)))


def desechapper(s):
    s = s.replace("\\\\", "\x00")          # les \\ d'abord, sinon \\" déraille
    s = s.replace('\\"', '"').replace("\\n", "\n")
    return s.replace("\x00", "\\")


def echapper(s):
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return s.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")


def corriger_texte_lua(brut):
    """brut = contenu échappé Lua ; rend le contenu corrigé (échappé)."""
    clair = desechapper(brut)
    neuf = am.corriger_citations(clair)
    return brut if neuf == clair else echapper(neuf)


def main():
    ecrire = "--ecrire" in sys.argv
    lignes = io.open(CIBLE, encoding="utf-8").read().split("\n")
    n_lignes, n_champs = 0, 0
    exemples = []
    sorties = []
    for ligne in lignes:
        neuve, touchee = ligne, False
        m = RE_AURA.match(ligne)
        if m:
            corrige = corriger_texte_lua(m.group(2))
            if corrige != m.group(2):
                neuve = m.group(1) + corrige + m.group(3)
                touchee = True
                n_champs += 1
        elif ligne.startswith("DB["):
            def _champ(mm):
                nonlocal touchee, n_champs
                corrige = corriger_texte_lua(mm.group(3))
                if corrige != mm.group(3):
                    touchee = True
                    n_champs += 1
                    return '%s%s="%s"' % (mm.group(1), mm.group(2), corrige)
                return mm.group(0)
            neuve = RE_CHAMP_FR.sub(_champ, ligne)
        if touchee:
            n_lignes += 1
            if len(exemples) < 4:
                exemples.append((ligne[:90], neuve[:90]))
        sorties.append(neuve)
    print("lignes touchées : %d (%d champ(s) français corrigés)"
          % (n_lignes, n_champs))
    for avant, apres in exemples:
        print("  av : %s" % avant)
        print("  ap : %s" % apres)
    if not n_lignes:
        print("rien à corriger.")
        return 0
    if not ecrire:
        print("\nAPERÇU seulement. --ecrire pour appliquer.")
        return 0

    contenu = "\n".join(sorties)
    ok, _k, message = mesurer_constantes.mesurer(
        contenu.encode("utf-8"), os.path.basename(CIBLE))
    if not ok:
        print("STOP — le résultat ne compile pas en lua51 :", message)
        print("Rien n'a été écrit.")
        return 1
    sauvegarde = os.path.join(
        BASE, "rapports", "DB_SortsCorrections_avant_citations_%s.lua"
        % time.strftime("%Y%m%d-%H%M%S"))
    shutil.copy2(CIBLE, sauvegarde)
    with io.open(CIBLE, "w", encoding="utf-8", newline="\n") as f:
        f.write(contenu)
    print("écrit (sauvegarde : %s)" % os.path.basename(sauvegarde))

    # Recompte : la même passe relue doit rendre zéro.
    relu = io.open(CIBLE, encoding="utf-8").read().split("\n")
    restants = 0
    for ligne in relu:
        m = RE_AURA.match(ligne)
        if m and corriger_texte_lua(m.group(2)) != m.group(2):
            restants += 1
            continue
        if ligne.startswith("DB["):
            for mm in RE_CHAMP_FR.finditer(ligne):
                if corriger_texte_lua(mm.group(3)) != mm.group(3):
                    restants += 1
                    break
    print("RECOMPTE : %d ligne(s) restantes (attendu : 0)" % restants)
    return 0 if restants == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
