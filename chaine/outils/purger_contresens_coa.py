# -*- coding: utf-8 -*-
r"""Purge le D des corrections CoA prouvées FAUSSES (bloc B du programme 3,
29/07/2026).

Ce sont des faux appariements : le français d'un AUTRE talent, détecté au
bloc 5 par ancres numériques partagées puis relu fiche par fiche au bloc G.
Un contresens se corrige sans arbitrage — c'est la règle du projet.

CE QUE FAIT LA PURGE, et pourquoi c'est ce geste-là :
  - `DB[id]={D="…",DE="…",N="…"}` -> le D SEUL est retiré. L'entrée
    survit (elle garde N et DE), donc le module n'a plus de français pour
    cette description et le client affiche son anglais — qui est JUSTE.
  - `aura(id, "EN", "FR")` -> la ligne est mise en COMMENTAIRE avec sa
    raison, jamais supprimée.

Dans les deux cas l'identifiant reste VISIBLE dans le fichier : c'est ce
qui rend la purge définitive. `ingerer_rapport.ids_deja_corriges()` lit
`DB[id]=` et `aura(id,` sur le texte brut ; tant que la trace est là, un
rapport joueur qui reproposerait la même fausse correction ne peut pas la
réécrire. Une purge sans barrière au point d'écriture est défaite au
passage suivant (leçon du lot 13) — ici la barrière EST la trace.

Usage : python outils/purger_contresens_coa.py [--appliquer]
"""
import io
import os
import re
import shutil
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORRECTIONS = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface"
               r"\AddOns\AscensionFR\DB\DB_SortsCorrections.lua")
SUSPECTS = os.path.join(BASE, "rapports", "blocG_coa_suspects.txt")

RE_D = re.compile(r'(?<=[{,])D="(?:\\.|[^"\\])*",?')


def ids_contresens():
    """Les ids de la SEULE section CONTRESENS du rapport relu."""
    txt = io.open(SUSPECTS, encoding="utf-8").read()
    corps = txt.split("=== DOUTEUX")[0]
    return re.findall(r"^-> id (\d+)", corps, re.M)


def retirer_d(ligne):
    """Retire le champ D d'une ligne DB[id]={…}. Rend (ligne, retiré?)."""
    neuve, n = RE_D.subn("", ligne, count=1)
    if not n:
        return ligne, False
    # une virgule orpheline peut rester si D était le dernier champ
    neuve = neuve.replace(",}", "}")
    return neuve, True


def main():
    appliquer = "--appliquer" in sys.argv
    ids = ids_contresens()
    print("contresens à purger : %d" % len(ids))
    brut = io.open(CORRECTIONS, encoding="utf-8").read()
    lignes = brut.split("\n")

    faits, deja, auras, introuvables = [], [], [], []
    for identifiant in ids:
        motif_db = re.compile(r"^DB\[" + identifiant + r"\]=\{")
        motif_aura = re.compile(r"^aura\(" + identifiant + r"\s*,")
        touche = False
        for i, ligne in enumerate(lignes):
            if motif_db.match(ligne):
                neuve, retire = retirer_d(ligne)
                if retire:
                    lignes[i] = neuve
                    faits.append(identifiant)
                else:
                    deja.append(identifiant)
                touche = True
                break
            if motif_aura.match(ligne):
                lignes[i] = ("-- PURGÉ (bloc B, 29/07/2026 — faux "
                             "appariement prouvé, id conservé pour que la "
                             "correction ne revienne pas) :\n-- " + ligne)
                auras.append(identifiant)
                touche = True
                break
        if not touche:
            introuvables.append(identifiant)

    print("  D retirés         : %d" % len(faits))
    print("  aura commentées   : %d" % len(auras), auras)
    print("  déjà sans D       : %d" % len(deja), deja)
    print("  INTROUVABLES      : %d" % len(introuvables), introuvables)

    neuf = "\n".join(lignes)
    import lupa.lua51 as lupa_mod
    lupa_mod.LuaRuntime().compile(neuf)
    print("  compile lua51     : OK")

    # contrôle : la trace de CHAQUE id purgé doit rester lisible, sinon la
    # barrière d'ingestion ne le reconnaîtrait plus
    presents = (set(re.findall(r"DB\[(\d+)\]=", neuf))
                | set(re.findall(r"aura\((\d+),", neuf)))
    perdus = [i for i in ids if i not in presents]
    if perdus:
        raise SystemExit("TRACE PERDUE pour %d id(s) : %s — rien n'est écrit"
                         % (len(perdus), perdus))
    print("  traces conservées : %d/%d" % (len(ids) - len(perdus), len(ids)))

    if not appliquer:
        print("\nSIMULATION — rien n'a été écrit. --appliquer pour purger.")
        return 0
    shutil.copy2(CORRECTIONS,
                 CORRECTIONS + ".avant_blocB_" + time.strftime("%Y%m%d-%H%M%S"))
    with io.open(CORRECTIONS, "w", encoding="utf-8", newline="") as f:
        f.write(neuf)
    print("\n>>> APPLIQUÉ. Les descriptions repartent en anglais juste, "
          "et la file de traduction fait le reste.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
