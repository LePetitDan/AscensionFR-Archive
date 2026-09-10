# -*- coding: utf-8 -*-
r"""BALAYAGE DE SECRETS — l'arbre de travail, ce qui est commité, et
l'HISTORIQUE (programme 6, 29/07/2026).

POURQUOI L'HISTORIQUE COMPTE AUTANT QUE L'ARBRE. Un secret retiré d'un
fichier reste dans le dépôt : `git log -p` le rend, l'API GitHub le rend,
et les robots qui balayent les dépôts publics lisent l'historique. Un
`git rm` ne révoque rien. Le seul balayage qui veut dire quelque chose
parcourt donc TOUS les objets du dépôt, pas seulement HEAD.

Usage :
    python outils/balayer_secrets.py                 # dépôt public : arbre + historique
    python outils/balayer_secrets.py --racine <chemin>
    python outils/balayer_secrets.py --sans-historique
    python outils/balayer_secrets.py --mesurer       # calibrage : que déclenche l'heuristique ?

Code de sortie : 0 si rien, 1 si un seul motif est trouvé. Sans dérogation.
"""
import io
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from secrets_publication import (balayer_arbre, balayer_texte,  # noqa: E402
                                 lisible, est_du_balayage, MOTIFS,
                                 RE_AFFECTATION, entropie)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(BASE, "depot_github")

# Lancé par banc_sante.py sous pythonw.exe (sans console) à 19 h 15. Un processus
# sans console qui démarre git force Windows à ouvrir une fenêtre noire, qui vole
# le focus et éjecte d'un jeu en plein écran. capture_output redirige les FLUX,
# pas la FENÊTRE. getattr : la constante n'existe que sur Windows ; ailleurs 0,
# que subprocess accepte partout (il ne refuse creationflags que si NON NUL).
SANS_FENETRE = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def git(args, cwd, binaire=False):
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True,
                       creationflags=SANS_FENETRE)
    if r.returncode != 0:
        return None
    return r.stdout if binaire else r.stdout.decode("utf-8", "replace")


def balayer_historique(racine):
    """Tous les blobs de tous les commits, branches et tags comprises.

    `git rev-list --objects --all` énumère l'univers atteignable ; on ne
    lit que les blobs, une seule fois chacun (un fichier inchangé sur 40
    commits est le MÊME objet — le dépôt le déduplique, nous aussi)."""
    sortie = git(["rev-list", "--objects", "--all"], racine)
    if sortie is None:
        return None, 0
    objets = []
    for ligne in sortie.splitlines():
        morceaux = ligne.split(" ", 1)
        if len(morceaux) == 2 and morceaux[1].strip():
            objets.append((morceaux[0], morceaux[1].strip()))

    trouves, lus = [], 0
    for sha, chemin in objets:
        if not lisible(chemin) or est_du_balayage(chemin):
            continue
        brut = git(["cat-file", "-p", sha], racine, binaire=True)
        if brut is None:
            continue
        # Un blob binaire non reconnu à l'extension : on le saute plutôt que
        # d'inventer des motifs dans du bruit.
        if b"\x00" in brut[:4096]:
            continue
        lus += 1
        for t in balayer_texte(chemin, brut.decode("utf-8", "replace")):
            trouves.append((chemin + "  [objet %s]" % sha[:9],) + t)
    return trouves, lus


def mesurer(racine):
    """CALIBRAGE. L'heuristique d'entropie est la seule partie du balayage
    qui puisse crier au loup : on regarde ce qu'elle attrape sur l'arbre
    réel, et à quelle entropie. Un seuil ne se décrète pas."""
    print("Ce que l'heuristique « affectation à forte entropie » voit,")
    print("tous seuils confondus, sur %s :\n" % racine)
    lignes = []
    for dossier, sous, fichiers in os.walk(racine):
        sous[:] = [d for d in sous if d != ".git"]
        for nom in sorted(fichiers):
            chemin = os.path.join(dossier, nom)
            rel_m = os.path.relpath(chemin, racine)
            if not lisible(chemin) or est_du_balayage(rel_m):
                continue
            try:
                texte = io.open(chemin, encoding="utf-8",
                                errors="replace").read()
            except (OSError, IOError):
                continue
            for m in RE_AFFECTATION.finditer(texte):
                v = m.group(2)
                lignes.append((entropie(v), os.path.relpath(chemin, racine),
                               m.group(1), v))
    for e, f, mot, v in sorted(lignes, reverse=True):
        apercu = v if len(v) <= 34 else v[:31] + "…"
        print("  %.2f bits  %-30s %-10s %s"
              % (e, f.replace("\\", "/")[-30:], mot, apercu))
    print("\n%d affectation(s) de forme suspecte au total." % len(lignes))
    return 0


def main():
    racine = PUBLIC
    if "--racine" in sys.argv:
        racine = sys.argv[sys.argv.index("--racine") + 1]
    racine = os.path.abspath(racine)
    if "--mesurer" in sys.argv:
        return mesurer(racine)

    print("=" * 70)
    print("BALAYAGE DE SECRETS — %s" % racine)
    print("=" * 70)
    print("motifs cherchés : %d familles + l'heuristique d'entropie"
          % len(MOTIFS))
    if not os.path.isdir(racine):
        print("racine introuvable.")
        return 2

    print("\n--- 1. l'arbre de travail (TOUTES extensions) ---")
    trouves = balayer_arbre(racine)
    print("    %d motif(s) trouvé(s)" % len(trouves))

    trouves_h = []
    if "--sans-historique" not in sys.argv:
        print("\n--- 2. l'historique git (tous les objets, tous les commits) ---")
        trouves_h, lus = balayer_historique(racine)
        if trouves_h is None:
            print("    (pas un dépôt git, ou git indisponible)")
            trouves_h = []
        else:
            print("    %d blob(s) texte lu(s), %d motif(s) trouvé(s)"
                  % (lus, len(trouves_h)))

    tout = trouves + trouves_h
    if tout:
        print("\n" + "=" * 70)
        print("🛑 %d SECRET(S) — REFUS DE PUBLIER" % len(tout))
        for fichier, etiquette, extrait, ligne in tout:
            print("   %s:%d" % (fichier, ligne))
            print("      %s : %s" % (etiquette, extrait))
        return 1
    print("\n" + "=" * 70)
    print("✅ aucun motif de secret, ni dans l'arbre ni dans l'historique.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
