# -*- coding: utf-8 -*-
"""Banc du journal d'incident — programme 23 (02/08/2026).

Ce que ce banc défend, et pourquoi il existe :

  1. **Une trace ne doit jamais porter de secret ni d'identité.** Un journal
     d'erreur finit collé sur le Discord par un joueur qui veut aider. Le
     webhook des rapports est une autorisation d'écriture à porteur ; le nom
     de compte WoW et le nom d'utilisateur Windows sont des identités. Chaque
     épreuve ci-dessous fabrique une trace qui les contient VRAIMENT, puis
     vérifie qu'ils ne survivent pas.

  2. **Le gestionnaire de plantage ne doit jamais planter.** On lui donne un
     disque qui refuse d'écrire et on vérifie qu'il rend None sans lever.

  3. **Windows ne doit pas bouger.** `CONFIG_DIR` est comparé, au caractère
     près, à l'ancienne formule `os.environ.get("APPDATA", ".")`.

⚠️ Ce banc ne montre JAMAIS la valeur du webhook, même en cas d'échec : il
   n'affiche que des booléens et des empreintes.

Usage : python outils/banc_incident.py
"""
import hashlib
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ICI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(ICI)
sys.path.insert(0, os.path.join(BASE, "compagnon"))

import compagnon as logique          # noqa: E402

EPREUVES = []
ECHECS = []


def epreuve(titre):
    def decorer(fonction):
        EPREUVES.append((titre, fonction))
        return fonction
    return decorer


def affirmer(condition, quoi):
    if not condition:
        ECHECS.append(quoi)
    print("   %s %s" % ("OK  " if condition else "RATÉ", quoi))


def _empreinte(texte):
    return hashlib.sha256(texte.encode("utf-8")).hexdigest()[:12]


# --------------------------------------------------------------------------- #
# 1. L'anonymisation
# --------------------------------------------------------------------------- #
@epreuve("le webhook ne survit pas à l'anonymisation")
def _webhook():
    secret = logique.WEBHOOK_RAPPORTS
    if not secret:
        print("   (webhook vide dans cette copie — on éprouve un faux)")
        secret = ("https://discord.com/api/webhooks/1234567890/"
                  "AbCdEfGhIjKlMnOpQrStUvWxYz0123456789")
    # Les trois formes sous lesquelles il peut arriver dans une trace.
    for forme in (
            "urllib.error.HTTPError: 401 pour %s" % secret,
            'ValueError: unknown url type: "%s"' % secret,
            "  File \"compagnon.py\", line 900, in envoyer_rapport_discord\n"
            "    urllib.request.urlopen('%s')\n" % secret):
        sortie = logique._anonymiser(forme)
        affirmer(secret not in sortie,
                 "absent de la sortie (empreinte de l'entrée %s)"
                 % _empreinte(forme))
        affirmer("<webhook>" in sortie, "remplacé par <webhook>")


@epreuve("un webhook Discord ÉTRANGER est retiré aussi")
def _webhook_etranger():
    faux = ("https://discordapp.com/api/webhooks/999/"
            "ZzZzZzZzZzZzZzZzZzZzZzZz")
    sortie = logique._anonymiser("POST %s a échoué" % faux)
    affirmer(faux not in sortie, "un webhook qui n'est pas le nôtre part aussi")


@epreuve("le nom de compte WoW est retiré")
def _compte_wow():
    for brut in (r"C:\Jeux\Ascension\WTF\Account\DANLEPETIT\SavedVariables"
                 r"\AscensionFR.lua",
                 "/home/x/Ascension/WTF/Account/DANLEPETIT/SavedVariables"):
        sortie = logique._anonymiser("FileNotFoundError: " + brut)
        affirmer("DANLEPETIT" not in sortie,
                 "le compte disparaît (%s)" % ("\\" if "\\" in brut else "/"))
        affirmer("<compte>" in sortie, "remplacé par <compte>")


@epreuve("le dossier personnel et le nom d'utilisateur sont retirés")
def _identite():
    maison = os.path.expanduser("~")
    nom = os.environ.get("USERNAME") or os.environ.get("USER") or ""
    trace = ("PermissionError: [Errno 13] %s\\Documents\\jeu\n"
             "KeyError: '%s'\n" % (maison, nom))
    sortie = logique._anonymiser(trace)
    affirmer(maison not in sortie, "le dossier personnel disparaît")
    if len(nom) >= 3:
        affirmer(nom.lower() not in sortie.lower(),
                 "le nom d'utilisateur seul disparaît aussi")
    else:
        print("   (nom d'utilisateur trop court pour être remplacé sans "
              "risque — non éprouvé)")


@epreuve("le dossier temporaire du paquet est retiré")
def _paquet():
    ancien = getattr(sys, "_MEIPASS", None)
    sys._MEIPASS = r"C:\Users\Jerome\AppData\Local\AscensionFR_Compagnon\_MEI42"
    try:
        sortie = logique._anonymiser(
            "FileNotFoundError: %s\\assets\\hub\\fond.png" % sys._MEIPASS)
        affirmer("_MEI42" not in sortie, "le dossier du paquet disparaît")
        affirmer("<paquet>" in sortie, "remplacé par <paquet>")
    finally:
        if ancien is None:
            del sys._MEIPASS
        else:
            sys._MEIPASS = ancien


@epreuve("l'anonymisation ne casse pas ce qui est utile")
def _utile():
    trace = ("Traceback (most recent call last):\n"
             "  File \"interface_hub.py\", line 485, in _candidats_registre\n"
             "    import winreg\n"
             "ModuleNotFoundError: No module named 'winreg'\n")
    sortie = logique._anonymiser(trace)
    for morceau in ("_candidats_registre", "ModuleNotFoundError", "winreg",
                    "line 485"):
        affirmer(morceau in sortie, "« %s » est conservé" % morceau)


# --------------------------------------------------------------------------- #
# 2. L'écriture du journal
# --------------------------------------------------------------------------- #
@epreuve("journal_incident écrit, et ce qu'il écrit est propre")
def _ecriture():
    secret = logique.WEBHOOK_RAPPORTS or "aucun"
    trace = ("Traceback (most recent call last):\n"
             "  File \"compagnon.py\", line 900, in envoyer_rapport_discord\n"
             "    urlopen('%s')\n"
             "urllib.error.URLError: <urlopen error [Errno 11001]>\n" % secret)
    chemin = logique.journal_incident("Envoyer mon rapport", trace)
    affirmer(bool(chemin), "un chemin est rendu")
    if not chemin:
        return
    texte = io.open(chemin, encoding="utf-8").read()
    affirmer("Envoyer mon rapport" in texte, "le geste du joueur est noté")
    affirmer("URLError" in texte, "la cause technique est notée")
    affirmer(logique.VERSION_COMPAGNON in texte, "la version est notée")
    if logique.WEBHOOK_RAPPORTS:
        affirmer(logique.WEBHOOK_RAPPORTS not in texte,
                 "le webhook n'est PAS dans le fichier")
    affirmer("<webhook>" in texte or not logique.WEBHOOK_RAPPORTS,
             "il y est remplacé par <webhook>")
    print("   fichier : %s" % os.path.basename(chemin))


@epreuve("journal_incident ne lève JAMAIS, même si le disque refuse")
def _disque_muet():
    vrai = logique.dossier_journal
    logique.dossier_journal = lambda: None
    try:
        r = logique.journal_incident("un geste", "une trace")
        affirmer(r is None, "rend None au lieu de lever")
    except Exception as e:
        affirmer(False, "a levé %s — INTERDIT" % type(e).__name__)
    finally:
        logique.dossier_journal = vrai

    def dossier_pourri():
        raise OSError("disque en carton")
    logique.dossier_journal = dossier_pourri
    try:
        r = logique.journal_incident("un geste", "une trace")
        affirmer(r is None, "rend None même si le dossier lève")
    except Exception as e:
        affirmer(False, "a levé %s — INTERDIT" % type(e).__name__)
    finally:
        logique.dossier_journal = vrai


@epreuve("une boucle de plantages ne remplit pas le disque")
def _plafond():
    chemin = logique.journal_incident("essai", "trace courte")
    if not chemin:
        print("   (pas de journal écrivable — non éprouvé)")
        return
    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write("x" * (logique.TAILLE_INCIDENT_MAX + 10))
    logique.journal_incident("essai", "trace après débordement")
    taille = os.path.getsize(chemin)
    affirmer(taille < logique.TAILLE_INCIDENT_MAX,
             "le fichier est reparti de zéro (%d octets)" % taille)


# --------------------------------------------------------------------------- #
# 3. Windows n'a pas bougé
# --------------------------------------------------------------------------- #
@epreuve("CONFIG_DIR est INCHANGÉ sous Windows")
def _config_dir():
    ancienne_formule = os.path.join(os.environ.get("APPDATA", "."),
                                    "AscensionFR")
    if os.environ.get("APPDATA"):
        affirmer(logique.CONFIG_DIR == ancienne_formule,
                 "identique au caractère près : %s" % logique.CONFIG_DIR)
    else:
        print("   (pas de %APPDATA% ici — c'est le cas Linux)")
        affirmer(logique.CONFIG_DIR != ancienne_formule,
                 "ne retombe PLUS sur le dossier courant : %s"
                 % logique.CONFIG_DIR)
        affirmer(not logique.CONFIG_DIR.startswith("." + os.sep),
                 "le chemin n'est pas relatif")


def main():
    print("=" * 70)
    print("BANC DU JOURNAL D'INCIDENT — programme 23")
    print("=" * 70)
    for titre, fonction in EPREUVES:
        print("\n>> %s" % titre)
        try:
            fonction()
        except Exception as e:
            ECHECS.append("%s a levé %s: %s" % (titre, type(e).__name__, e))
            print("   RATÉ  l'épreuve elle-même a levé %s: %s"
                  % (type(e).__name__, e))
    print("\n" + "=" * 70)
    if ECHECS:
        print("%d ÉCHEC(S) :" % len(ECHECS))
        for e in ECHECS:
            print("  - %s" % e)
        return 1
    print("Tout est vert.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
