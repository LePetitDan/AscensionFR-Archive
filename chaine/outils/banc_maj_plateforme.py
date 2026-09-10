# -*- coding: utf-8 -*-
"""Banc de la mise à jour par plateforme — ajout urgent du programme 23.

LE DÉFAUT QU'ON DÉSAMORCE (trouvé par Tetardtek, 02/08/2026). Le Hub ne
connaissait AUCUNE plateforme. La chaîne, maillon par maillon :

  compagnon.derniere_release()      n'apparie que ZIP_ATTENDU et EXE_ATTENDU.
                                    Aucun asset Linux -> sous Linux, url_exe
                                    vaut l'URL de l'exe WINDOWS.
  Hub._maj_appli_proposable()       le lien s'allume si (en retard ET url_exe).
  Hub.mettre_a_jour_appli()         `sys.frozen` est VRAI pour le binaire
                                    Linux : les deux gardes passaient.
  Hub._maj_appli_fond()             télécharge ~40 Mo d'exe Windows. L'en-tête
                                    « MZ » est bien là : le contrôle de forme
                                    ne voit rien.
  compagnon.lancer_remplacement()   passe le tout à cmd.exe.

Endormi tant que la 3.4.1 est la dernière ; ARMÉ à la première publication
suivante. Et il ne ratait que par CHANCE : `creationflags` n'existe pas hors
Windows, donc subprocess lève. Ce banc éprouve qu'on ne dépend plus de ça.

Usage : python outils/banc_maj_plateforme.py
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ICI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(ICI)
sys.path.insert(0, os.path.join(BASE, "compagnon"))

import compagnon as logique             # noqa: E402
import interface_hub                    # noqa: E402

ECHECS = []


def affirmer(condition, quoi):
    if not condition:
        ECHECS.append(quoi)
    print("   %s %s" % ("OK  " if condition else "RATÉ", quoi))


class FauxHub:
    """Un Hub de papier : juste les attributs que lit la règle. Aucune
    fenêtre n'est ouverte — la règle est SANS ÉTAT, c'est ce qui la rend
    éprouvable."""

    def __init__(self, en_retard=True, url_exe="https://exemple/x.exe",
                 vue="traduction"):
        self.appli_en_retard = en_retard
        self.url_exe = url_exe
        self.vue = vue

    def proposable(self):
        return interface_hub.Hub._maj_appli_proposable(self)


class FausseReponse:
    def __init__(self, charge):
        self._o = io.BytesIO(json.dumps(charge).encode("utf-8"))

    def read(self, *a):
        return self._o.read(*a)

    def __enter__(self):
        return self._o

    def __exit__(self, *a):
        return False


def sous_systeme(nom):
    """Fait croire au moteur qu'on est ailleurs. `os.name` est la seule
    chose que lit `remplacement_possible` : on la remplace, on ne la
    devine pas."""
    class Bascule:
        def __enter__(self):
            self.vrai = os.name
            os.name = nom
            return self

        def __exit__(self, *a):
            os.name = self.vrai
            return False
    return Bascule()


print("=" * 70)
print("BANC DE LA MISE À JOUR PAR PLATEFORME — programme 23 (ajout urgent)")
print("=" * 70)

# --------------------------------------------------------------------------- #
print("\n>> 1. Le défaut EXISTE bien : la release ne propose qu'un asset "
      "Windows")
charge = {"tag_name": "v3.5.0", "assets": [
    {"name": logique.ZIP_ATTENDU,
     "browser_download_url": "https://exemple/AscensionFR_manuel.zip"},
    {"name": logique.EXE_ATTENDU,
     "browser_download_url": "https://exemple/AscensionFR_Compagnon.exe"},
]}
vrai_urlopen = logique.urllib.request.urlopen
logique.urllib.request.urlopen = lambda *a, **k: FausseReponse(charge)
try:
    version, url_zip, url_exe = logique.derniere_release()
finally:
    logique.urllib.request.urlopen = vrai_urlopen
affirmer(version == "3.5.0", "une version plus récente est annoncée : 3.5.0")
affirmer(url_exe is not None,
         "url_exe est REMPLI même s'il n'y a aucun asset Linux — c'est bien "
         "l'exe Windows")
affirmer(url_exe.endswith(".exe"), "et il finit par .exe : %s" % url_exe)

# --------------------------------------------------------------------------- #
print("\n>> 2. Sous Windows, RIEN NE CHANGE")
affirmer(os.name == "nt", "ce banc tourne bien sous Windows")
affirmer(logique.remplacement_possible() is True,
         "remplacement_possible() est vrai")
affirmer(FauxHub().proposable() is True,
         "le lien « nouvelle version » reste proposé")
affirmer(FauxHub(en_retard=False).proposable() is False,
         "…et reste caché quand l'appli est à jour (règle d'avant)")
affirmer(FauxHub(url_exe=None).proposable() is False,
         "…et caché sans asset (règle d'avant)")
affirmer(FauxHub(vue="accueil").proposable() is False,
         "…et caché hors de la vue Traduction (règle d'avant)")

# --------------------------------------------------------------------------- #
print("\n>> 3. Ailleurs, la mise à jour n'est PAS proposée")
with sous_systeme("posix"):
    affirmer(logique.remplacement_possible() is False,
             "remplacement_possible() est faux")
    affirmer(FauxHub().proposable() is False,
             "le lien reste CACHÉ, même appli en retard et url_exe rempli")

# --------------------------------------------------------------------------- #
print("\n>> 4. Et si on l'appelait quand même, le relais REFUSE")
with sous_systeme("posix"):
    try:
        logique.lancer_remplacement("/tmp/faux.exe", "/tmp/hub")
        affirmer(False, "il a accepté — INTERDIT")
    except RuntimeError as e:
        affirmer("Windows" in str(e),
                 "il lève une RuntimeError explicite : « %s »" % e)
    except Exception as e:
        affirmer(False, "il lève %s au lieu d'une RuntimeError claire"
                 % type(e).__name__)

print("\n>> 5. Le refus arrive AVANT d'écrire quoi que ce soit")
avant = set(os.listdir(os.environ.get("TEMP", ".")))
with sous_systeme("posix"):
    try:
        logique.lancer_remplacement("/tmp/faux.exe", "/tmp/hub")
    except RuntimeError:
        pass
apres = set(os.listdir(os.environ.get("TEMP", ".")))
nouveaux = [n for n in apres - avant if n.startswith("AscensionFR_maj_")]
affirmer(not nouveaux, "aucun .bat de relais n'a été écrit (%d trouvé(s))"
         % len(nouveaux))

print("\n" + "=" * 70)
if ECHECS:
    print("%d ÉCHEC(S) :" % len(ECHECS))
    for e in ECHECS:
        print("  - %s" % e)
    sys.exit(1)
print("Tout est vert.")
