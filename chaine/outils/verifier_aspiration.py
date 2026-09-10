# -*- coding: utf-8 -*-
r"""Banc de l'aspiration et des codes retour « rien à faire » (29/07/2026).

Deux défauts trouvés au premier vrai passage de l'Atelier, deux contrats à
tenir pour toujours :

  A. UN HOQUET RÉSEAU NE DOIT PLUS GELER LE MARQUE-PAGE. Un téléchargement
     et un appel d'API se réessaient ; un 401/403/404 ne se réessaie PAS
     (le jeton ou les droits sont en cause, insister ne sert à rien) ;
     un fichier vraiment mort finit consigné et cesse de tout retenir.
  B. « RIEN À FAIRE » N'EST PAS « ÇA A RATÉ ». Depuis que l'Atelier honore
     les codes retour, un passage sans nouveauté qui sort en 1 peint un
     bandeau ROUGE sur une chaîne parfaitement saine — et un faux rouge
     quotidien détruit la valeur du contrôle en une semaine.

Aucun réseau : urlopen est remplacé par un faux qui échoue à la demande.
Aucune écriture dans le dépôt : les cas de codes retour travaillent dans
un dossier temporaire.
"""
import io
import json
import os
import shutil
import sys
import tempfile
import urllib.error

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import aspirer_discord as asp  # noqa: E402
import ingerer_rapport as ir  # noqa: E402

echecs = []


def verifier(nom, condition, detail=""):
    print("  %s %s %s" % ("ok    " if condition else "ECHEC ", nom, detail))
    if not condition:
        echecs.append(nom)


class _Reponse:
    def __init__(self, contenu):
        self._c = contenu

    def read(self):
        return self._c

    def __enter__(self):
        return self

    def __exit__(self, *x):
        return False


def _faux_urlopen(rates, erreur=None, contenu=b"contenu-ok"):
    """Échoue les `rates` premières fois, puis rend `contenu`."""
    etat = {"n": 0}

    def urlopen(req, timeout=None):
        etat["n"] += 1
        if etat["n"] <= rates:
            raise (erreur or OSError("hoquet simulé n°%d" % etat["n"]))
        return _Reponse(contenu)
    return urlopen


def contrat_a(dossier):
    print("A. L'aspiration résiste aux hoquets")
    asp.PAUSES = (0.01, 0.01)          # le banc n'attend pas
    ancien = asp.urllib.request.urlopen
    try:
        # A1-A3 : le téléchargement se rattrape
        for rates in (0, 1, 2):
            asp.urllib.request.urlopen = _faux_urlopen(rates)
            cible = os.path.join(dossier, "pj_%d.bin" % rates)
            ratees = asp.telecharger("http://exemple/x", cible)
            verifier("téléchargement, %d hoquet(s)" % rates,
                     os.path.exists(cible)
                     and io.open(cible, "rb").read() == b"contenu-ok"
                     and ratees == rates,
                     "-> succès au %dᵉ essai" % (ratees + 1))
        # A4 : au-delà, on abandonne SANS laisser de fichier à moitié écrit
        asp.urllib.request.urlopen = _faux_urlopen(asp.ESSAIS)
        cible = os.path.join(dossier, "pj_morte.bin")
        try:
            asp.telecharger("http://exemple/x", cible)
            verifier("téléchargement mort : abandon", False, "aucune levée")
        except Exception:
            verifier("téléchargement mort : abandon",
                     not os.path.exists(cible)
                     and not os.path.exists(cible + ".part"),
                     "-> ni fichier ni .part")
        # A5-A6 : l'API se rattrape aussi (c'est elle qui sortait en rouge)
        page = json.dumps([{"id": "42"}]).encode()
        asp.urllib.request.urlopen = _faux_urlopen(2, contenu=page)
        verifier("pagination, 2 hoquets",
                 asp.api_get("/x", "jeton")[0]["id"] == "42")
        # A7 : mais un 403 ne se réessaie JAMAIS
        err = urllib.error.HTTPError("u", 403, "Forbidden", {}, None)
        asp.urllib.request.urlopen = _faux_urlopen(1, erreur=err,
                                                   contenu=page)
        try:
            asp.api_get("/x", "jeton")
            verifier("403 : pas de réessai", False, "aurait dû lever")
        except urllib.error.HTTPError as e:
            verifier("403 : pas de réessai", e.code == 403)
    finally:
        asp.urllib.request.urlopen = ancien


def contrat_b(dossier):
    print("B. « Rien à faire » sort en 0, « ça a raté » en 1")
    ancien = ir.DOSSIER_RAPPORTS
    try:
        # B1 : des rapports, mais aucun échec d'alignement -> rien à faire
        sans = os.path.join(dossier, "sans_echec")
        os.makedirs(sans, exist_ok=True)
        io.open(os.path.join(sans, "temoin.txt"), "w",
                encoding="utf-8").write(
            "=== Rapport AscensionFR ===\n\n--- Récolte ---\n"
            "[Divers] Hello ==> Bonjour\n")
        ir.DOSSIER_RAPPORTS = sans
        verifier("rapport sans échec d'alignement -> 0", ir.main() == 0)
        # B2 : aucun rapport du tout -> ÇA, c'est une anomalie
        vide = os.path.join(dossier, "vide")
        os.makedirs(vide, exist_ok=True)
        ir.DOSSIER_RAPPORTS = vide
        verifier("aucun fichier de rapport -> 1", ir.main() == 1)
    finally:
        ir.DOSSIER_RAPPORTS = ancien


def main():
    dossier = tempfile.mkdtemp(prefix="banc_aspiration_")
    try:
        contrat_a(dossier)
        print()
        contrat_b(dossier)
    finally:
        shutil.rmtree(dossier, ignore_errors=True)
    print()
    print("%d échec(s)" % len(echecs))
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
