# -*- coding: utf-8 -*-
"""La couture qui doit partir DANS LE MÊME GESTE que la fusion de la PR #5.

LE DÉFAUT QU'ELLE ÉVITE (programme 25, bloc E). La PR #5 ajoute
`compagnon/plateforme.py` : un SIXIÈME fichier source qui entre dans l'exe.
Or il n'existe que dans le dépôt PUBLIC — et c'est l'arbre PRIVÉ qui
construit. Sans cette couture, après la fusion :

  1. `import plateforme` échoue à la prochaine construction Windows
     (le fichier n'est pas dans WorkFlow/compagnon/) ;
  2. le fichier entre dans l'exe SANS être surveillé : ni synchronisé par
     synchroniser_depot_public, ni comparé par verifier_arbre_publie.

CE QU'ELLE FAIT, dans l'ordre, et elle s'arrête au premier accroc :
  1. vérifie que la fusion a bien eu lieu (plateforme.py présent côté public) ;
  2. copie public -> privé (le public est la référence : c'est l'arbre relu) ;
  3. ajoute "compagnon/plateforme.py" à SOURCES de secrets_publication.py ;
  4. rejoue verifier_arbre_publie.py, qui doit sortir VERT.

🛑 À lancer UNIQUEMENT après la fusion de la PR #5 dans main (et un
   `git pull` du dépôt public). Avant, l'étape 1 refuse — c'est voulu.

Usage : python outils/coudre_plateforme.py
"""
import io
import os
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ICI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(ICI)
PUBLIC = os.path.join(BASE, "depot_github", "compagnon", "plateforme.py")
PRIVE = os.path.join(BASE, "compagnon", "plateforme.py")
SECRETS = os.path.join(ICI, "secrets_publication.py")


def main():
    print("=" * 70)
    print("COUTURE plateforme.py — après la fusion de la PR #5")
    print("=" * 70)

    # 1. La fusion a-t-elle eu lieu ?
    if not os.path.isfile(PUBLIC):
        print("REFUS : depot_github/compagnon/plateforme.py n'existe pas.")
        print("        La PR #5 n'est pas fusionnée (ou le dépôt public pas")
        print("        à jour : cd depot_github && git pull).")
        return 1
    print("1. plateforme.py présent côté public : oui")

    # 2. public -> privé. Le fichier ne porte aucun secret (vérifié au
    #    programme 25 : stdlib seule, zéro réseau) — la copie est sûre.
    if os.path.isfile(PRIVE):
        pareil = (io.open(PRIVE, "rb").read() == io.open(PUBLIC, "rb").read())
        print("2. déjà présent côté privé (%s)"
              % ("identique" if pareil else "DIFFÉRENT — écrasé par le public"))
        if not pareil:
            shutil.copy2(PUBLIC, PRIVE)
    else:
        shutil.copy2(PUBLIC, PRIVE)
        print("2. copié public -> privé")

    # 3. SOURCES. L'ordre suit la liste existante ; l'ajout est idempotent.
    texte = io.open(SECRETS, encoding="utf-8").read()
    if "compagnon/plateforme.py" in texte:
        print("3. SOURCES contient déjà plateforme.py")
    else:
        nouveau, n = re.subn(
            r'(SOURCES = \[\n)(\s*)"compagnon/compagnon\.py",',
            r'\g<1>\g<2>"compagnon/compagnon.py",'
            r'\n\g<2>"compagnon/plateforme.py",',
            texte, count=1)
        if n != 1:
            print("REFUS : le motif SOURCES n'a pas été trouvé — la liste a")
            print("        changé de forme, ajoute la ligne à la main.")
            return 1
        io.open(SECRETS, "w", encoding="utf-8").write(nouveau)
        print("3. \"compagnon/plateforme.py\" ajouté à SOURCES")

    # 4. Le garde-fou doit ressortir vert.
    r = subprocess.run([sys.executable,
                        os.path.join(ICI, "verifier_arbre_publie.py")])
    print("4. verifier_arbre_publie : code %d" % r.returncode)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
