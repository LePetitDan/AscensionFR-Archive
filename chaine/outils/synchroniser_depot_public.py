# -*- coding: utf-8 -*-
r"""SYNCHRONISER LE DÉPÔT PUBLIC — privé -> public, en neutralisant
(programme 6, 29/07/2026).

POURQUOI CE N'EST PAS UN COPIER-COLLER. Le geste n° 1 du plan de remise
d'aplomb disait « copier les trois sources du privé vers depot_github ».
Écrit comme ça, il écrase le `WEBHOOK_RAPPORTS = ""` public par le webhook
vivant du privé, et le `git push` qui suit le rend public. Un humain qui
recopie à la main réintroduira le secret au prochain passage — et cette
fois sans que personne regarde.

La neutralisation doit donc être MÉCANIQUE et REPRODUCTIBLE : elle vient du
fichier déclaratif `outils/secrets_injectes.json`, et de la même fonction
`neutraliser()` qu'utilise le garde-fou pour vérifier. Un seul code, deux
usages : l'outil ne peut pas produire un arbre que le garde-fou refuse, et
le garde-fou ne peut pas accepter un arbre que l'outil ne sait pas produire.

TROIS REFUS, et le troisième est le plus important :
  1. une déclaration qui vise un nom absent du fichier privé (déclaration
     périmée ou renommage) : refus, jamais un silence ;
  2. rien à faire : ce n'est pas un échec, on le dit et on sort en 0 ;
  3. **après écriture, l'arbre public est BALAYÉ. Si un motif de secret y
     apparaît, tout est remis en place et l'outil refuse.** Le balayage ne
     dépend d'aucune déclaration : c'est lui qui rattrape le secret auquel
     personne n'a pensé. Sans ce filet, l'outil ne ferait que déplacer la
     confiance de l'humain vers un fichier JSON.

Usage :
    python outils/synchroniser_depot_public.py              # simulation
    python outils/synchroniser_depot_public.py --appliquer
"""
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from secrets_publication import (BASE, PUBLIC, SOURCES,  # noqa: E402
                                 balayer_arbre, charger_declarations,
                                 neutraliser)
from ecriture_sure import ecrire_texte  # noqa: E402


def lire(chemin):
    if not os.path.exists(chemin):
        return None
    with io.open(chemin, encoding="utf-8", errors="replace") as f:
        return f.read()


def main():
    appliquer = "--appliquer" in sys.argv
    declarations = charger_declarations()

    print("=" * 70)
    print("SYNCHRONISATION privé -> dépôt public  (%s)"
          % ("APPLICATION" if appliquer else "simulation"))
    print("=" * 70)
    print("déclarations de secrets : %d fichier(s)" % len(declarations))

    plan, refus = [], []
    for rel in SOURCES:
        prive = lire(os.path.join(BASE, rel))
        if prive is None:
            refus.append("%s : absent de l'arbre privé" % rel)
            continue
        neutre, griefs = neutraliser(prive, declarations.get(rel, {}))
        for grief in griefs:
            refus.append("%s : %s" % (rel, grief))
        publie = lire(os.path.join(PUBLIC, rel))
        etat = ("identique" if publie is not None
                and publie.replace("\r\n", "\n") == neutre.replace("\r\n", "\n")
                else "À METTRE À JOUR")
        n_neutralises = 0 if griefs else len(
            [k for k in declarations.get(rel, {}) if not k.startswith("_")])
        print("  %-40s %-16s %s"
              % (rel, etat,
                 "(%d secret(s) neutralisé(s))" % n_neutralises
                 if n_neutralises else ""))
        if etat != "identique":
            plan.append((rel, neutre))

    if refus:
        print("\n🛑 REFUS — %d point(s) :" % len(refus))
        for r in refus:
            print("   -", r)
        return 1

    if not plan:
        # « Rien à faire » n'est pas un échec : la leçon des faux rouges.
        print("\nrien à faire : le dépôt public est déjà à jour.")
        return 0

    print("\n%d fichier(s) à écrire." % len(plan))
    if not appliquer:
        print("SIMULATION — rien n'a été écrit. --appliquer pour poser.")
        return 0

    # On garde de quoi tout défaire AVANT d'écrire quoi que ce soit.
    avant = {rel: lire(os.path.join(PUBLIC, rel)) for rel, _ in plan}
    for rel, contenu in plan:
        cible = os.path.join(PUBLIC, rel)
        os.makedirs(os.path.dirname(cible), exist_ok=True)
        ecrire_texte(cible, contenu)
        print("   écrit :", rel)

    # LE FILET, après écriture : un secret qui aurait échappé à la
    # déclaration se verrait ici, et l'écriture serait défaite.
    print("\n--- balayage de l'arbre public après écriture ---")
    trouves = balayer_arbre(PUBLIC)
    if trouves:
        for rel, contenu in plan:
            cible = os.path.join(PUBLIC, rel)
            if avant[rel] is None:
                os.remove(cible)
            else:
                ecrire_texte(cible, avant[rel])
        print("🛑 %d MOTIF(S) DE SECRET dans l'arbre public :" % len(trouves))
        for fichier, etiquette, extrait, ligne in trouves:
            print("   %s:%d — %s : %s" % (fichier, ligne, etiquette, extrait))
        print("\nTOUT A ÉTÉ REMIS EN PLACE. Le dépôt public n'a pas bougé.")
        print("Déclare le secret dans outils/secrets_injectes.json, "
              "puis relance.")
        return 1
    print("    aucun motif de secret.")

    print("\n✅ dépôt public synchronisé. RIEN n'est commité ni poussé :")
    print("   cd depot_github && git status")
    return 0


if __name__ == "__main__":
    sys.exit(main())
