# -*- coding: utf-8 -*-
r"""INJECTE LE WEBHOOK DANS L'EXE, AU BUILD (programme 33, bloc 0).

Le webhook n'est plus en dur dans compagnon.py : compagnon._lire_webhook()
le lit à l'exécution depuis assets/webhook.local.txt. Ce fichier est
GITIGNORÉ (*.local.txt) : il n'entre jamais dans git, il n'existe que le
temps du build, et PyInstaller le gèle dans le binaire (le .spec embarque
assets/). Sur la machine du joueur, l'exe le retrouve dans sys._MEIPASS.

Usage (avant PyInstaller) :
    set ASCENSIONFR_WEBHOOK=https://discord.com/api/webhooks/…/…
    python outils/injecter_webhook.py            # écrit le fichier
    ... pyinstaller AscensionFR_Compagnon_v2.spec ...
    python outils/injecter_webhook.py --nettoyer # le retire après le build

Sans ASCENSIONFR_WEBHOOK : refus bruyant (un exe distribué sans webhook a
un bouton « Envoyer » mort — mieux vaut s'en apercevoir au build).
"""
import io
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIBLE = os.path.join(BASE, "compagnon", "assets", "webhook.local.txt")


def main():
    if "--nettoyer" in sys.argv:
        try:
            os.remove(CIBLE)
            print("retiré : %s" % CIBLE)
        except OSError:
            print("(rien à retirer)")
        return 0
    valeur = os.environ.get("ASCENSIONFR_WEBHOOK", "").strip()
    if not valeur:
        print("🛑 ASCENSIONFR_WEBHOOK n'est pas définie — rien injecté.")
        print("   L'exe distribué aurait un bouton « Envoyer » mort.")
        return 1
    if "discord.com/api/webhooks/" not in valeur:
        print("🛑 la valeur ne ressemble pas à un webhook Discord — refus.")
        return 1
    os.makedirs(os.path.dirname(CIBLE), exist_ok=True)
    with io.open(CIBLE, "w", encoding="utf-8") as f:
        f.write(valeur)
    # On ne réaffiche JAMAIS la valeur (elle finirait dans un journal de build).
    print("webhook injecté dans %s (%d caractères) — gitignoré."
          % (os.path.relpath(CIBLE, BASE), len(valeur)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
