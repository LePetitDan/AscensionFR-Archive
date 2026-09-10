# -*- coding: utf-8 -*-
"""
Banc du Hub — les quatre choses dont les joueurs disaient qu'elles cassaient
(24/07/2026) : télécharger, trouver le dossier, installer les voix, envoyer
un rapport.

Il n'envoie RIEN et ne télécharge RIEN : l'accès réseau est remplacé par un
espion qui lève une exception dès qu'on l'atteint. Ce qu'on teste, c'est
l'assemblage et le choix des messages — pas Discord.

Usage : python outils/verifier_hub.py
"""
import io
import os
import re
import socket
import ssl
import sys
import urllib.error
import zipfile

# La console Windows est en cp1252 : sans ça, le premier « é » tue le script
# (et en tâche planifiée, il meurt en silence).
sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPAGNON = os.path.join(BASE, "compagnon")
sys.path.insert(0, COMPAGNON)

import compagnon as L  # noqa: E402

echecs = []


def verifier(description, obtenu, attendu):
    if obtenu == attendu:
        print("  ok      %-52s %s" % (description, obtenu))
    else:
        print("  ECHEC   %s" % description)
        print("          obtenu  : %r" % (obtenu,))
        print("          attendu : %r" % (attendu,))
        echecs.append(description)


def verifier_vrai(description, condition, indice=""):
    if condition:
        print("  ok      %s" % description)
    else:
        print("  ECHEC   %s %s" % (description, indice))
        echecs.append(description)


# --------------------------------------------------------------------------
print("=== 1. Le couple rendu par extraire_caches est bien DÉPLIÉ ===")
#
# Le Hub avait perdu le « , _ » : on passait le tuple entier à l'envoi, qui
# faisait « bytes + tuple » -> TypeError. Résultat : plus AUCUN rapport ne
# partait depuis la 3.0.0, et le joueur lisait « vérifie ta connexion ».
APPEL = re.compile(r"(\w+)\s*=\s*(?:logique\.)?extraire_caches\(")
for nom in sorted(os.listdir(COMPAGNON)):
    if not nom.endswith(".py"):
        continue
    texte = io.open(os.path.join(COMPAGNON, nom), encoding="utf-8").read()
    for ligne in texte.split("\n"):
        if "extraire_caches(" not in ligne or "def " in ligne:
            continue
        deplie = ", _" in ligne or "[0]" in ligne
        verifier_vrai("%s : le couple est déplié" % nom, deplie,
                      "-> " + ligne.strip()[:70])

# --------------------------------------------------------------------------
print("")
print("=== 2. Le corps du rapport s'assemble ===")
atteint = []


def espion(req, *a, **k):
    atteint.append(req)
    raise AssertionError("espion")


L.urllib.request.urlopen = espion

for description, caches in (("avec pièce jointe", b"gz"),
                            ("sans pièce jointe", None)):
    atteint[:] = []
    try:
        L.envoyer_rapport_discord("rapport", caches)
        souci = "aucune exception (impossible : l'espion coupe)"
    except AssertionError:
        souci = None                      # le corps s'est assemblé
    except Exception as e:
        souci = "%s: %s" % (type(e).__name__, e)
    verifier_vrai("corps assemblé %s" % description, souci is None,
                  "-> " + (souci or ""))

atteint[:] = []
try:
    L.envoyer_rapport_discord("rapport", (b"gz", 42))
    resultat = "passé"
except TypeError:
    resultat = "TypeError"
except AssertionError:
    resultat = "passé"
verifier("le couple non déplié est bien REFUSÉ", resultat, "TypeError")

# --------------------------------------------------------------------------
print("")
print("=== 3. Chaque panne a son propre message ===")
#
# Avant, tout finissait en « serveur injoignable » : le joueur vérifiait sa
# connexion alors que son disque était plein ou son antivirus en cause.
CAS = [
    ("droits refusés", PermissionError("x"), "administrateur"),
    ("certificat / antivirus", ssl.SSLError("x"), "antivirus"),
    ("délai dépassé", socket.timeout("x"), "expiré"),
    ("fichier absent (404)",
     urllib.error.HTTPError("u", 404, "x", None, None), "n'existe plus"),
    ("limite GitHub (429)",
     urllib.error.HTTPError("u", 429, "x", None, None), "limité"),
    ("réseau", urllib.error.URLError("x"), "joindre GitHub"),
    ("zip abîmé", zipfile.BadZipFile("x"), "abîmé"),
    ("disque plein", OSError(28, "no space"), "place"),
]
messages = set()
for description, exc, attendu in CAS:
    message = L.raison_echec(exc)
    messages.add(message)
    verifier_vrai("%-24s -> parle de « %s »" % (description, attendu),
                  attendu.lower() in message.lower(), "-> " + message[:60])
verifier("les messages sont tous DIFFÉRENTS", len(messages), len(CAS))

# --------------------------------------------------------------------------
print("")
print("=== 4. Le dossier du jeu ===")
jeu = L.chercher_jeu()
verifier_vrai("chercher_jeu trouve un dossier", bool(jeu), "-> %s" % jeu)
if jeu:
    verifier_vrai("le dossier trouvé est valide", L.jeu_valide(jeu))

# Deux niveaux de profondeur : c'est ce qui manquait (« D:\\Jeux\\Ascension\\
# resources\\ascension-live » n'était pas trouvé).
import tempfile  # noqa: E402
faux = tempfile.mkdtemp(prefix="afr_faux_jeu_")
profond = os.path.join(faux, "Jeux", "Ascension", "resources",
                       "ascension-live", "Interface")
os.makedirs(profond)
verifier_vrai("un jeu à deux niveaux serait reconnu",
              L.jeu_valide(os.path.dirname(profond)))
import shutil  # noqa: E402
shutil.rmtree(faux, ignore_errors=True)

# --------------------------------------------------------------------------
print("")
print("=== 5. Le diagnostic ===")
releve = L.diagnostic(jeu)
for attendu in ("Hub", "Dossier utilisé", "Écriture autorisée", "GitHub"):
    verifier_vrai("le relevé contient « %s »" % attendu, attendu in releve)
verifier_vrai("le relevé ne contient pas le webhook",
              "discord.com/api/webhooks" not in releve)

# --------------------------------------------------------------------------
print("")
print("=== 6. Le Hub sur une installation VOLONTAIREMENT CASSÉE ===")
#
# Ajouté le 26/07/2026. Le contrôle d'installation et « Tout désinstaller »
# ne se testent pas à la main : il faudrait casser le jeu de Dan. On monte
# donc un FAUX jeu jetable dans %TEMP%, on y reproduit les quatre pannes
# comptées pendant la veille Discord du 18 au 26/07, et on vérifie que le Hub
# les voit, les répare, et ne détruit QUE ce qu'il a annoncé.
COMPTE_ESSAI = "JOUEUR@EXEMPLE.COM"
ROYAUME_ESSAI = "Rexxar - Conquest of Azeroth"


def _ecrire(chemin, texte):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    io.open(chemin, "w", encoding="utf-8").write(texte)


def _batir_faux_jeu(bac, casse):
    shutil.rmtree(bac, ignore_errors=True)
    os.makedirs(os.path.join(bac, "Data"))
    _ecrire(os.path.join(bac, "Ascension.exe"), "faux binaire")
    _ecrire(os.path.join(bac, "Wow.ini"), "[WoW Config]\nLanguage=fr\n")
    addons = os.path.join(bac, "Interface", "AddOns")
    _ecrire(os.path.join(addons, "AscensionFR", "AscensionFR.toc"),
            "## Version: 3.3.0\n## SavedVariables: AscensionFRSaved\n")
    _ecrire(os.path.join(addons, "AscensionFR_Repliques",
                         "AscensionFR_Repliques.toc"), "## Version: 3.3.0\n")
    _ecrire(os.path.join(bac, "Interface", "PTRXML", "PTR.xml"), "<Ui/>\n")
    _ecrire(os.path.join(addons, "DragonUI", "DragonUI.toc"),
            "## Version: 3.0.8\n")
    # Les voix, PLUS un fichier que le joueur aurait posé lui-même sous
    # Sound\ : celui-là ne doit JAMAIS partir.
    _ecrire(os.path.join(bac, "Sound", "CREATURE", "Sylvanas", "a.wav"), "son")
    _ecrire(os.path.join(bac, "Sound", "MonPackPerso", "a_moi.wav"), "à moi")
    _ecrire(os.path.join(bac, "WTF", "Account", COMPTE_ESSAI,
                         "SavedVariables", "AscensionFR.lua"),
            'AscensionFRSaved = {\n\t["Options"] = {\n'
            '\t\t["minimapAngle"] = -151.6,\n'
            + ('\t\t["desactive"] = true,\n' if casse else "")
            + '\t},\n\t["DernierTotal"] = 1274976,\n}\n')
    _ecrire(os.path.join(bac, "WTF", "Account", COMPTE_ESSAI, ROYAUME_ESSAI,
                         "Tartempion", "AddOns.txt"),
            "AscensionFR: %s\n" % ("disabled" if casse else "enabled"))
    if casse:
        # Le cliquet : extraction manuelle du zip DANS Interface\AddOns.
        _ecrire(os.path.join(addons, "Interface", "AddOns", "AscensionFR",
                             "AscensionFR.toc"), "## Version: 2.2.0\n")


bac = os.path.join(tempfile.gettempdir(), "afr_banc_hub")
# HERMÉTISME (bloc 3, 28/07/2026). jeu_ouvert() détecte Wow.exe par nom de
# processus GLOBAL : le banc devenait rouge dès que Dan jouait, alors que
# son faux jeu dans %TEMP% n'est pas celui qui tourne — et un rouge
# environnemental qu'on prend l'habitude d'ignorer masquerait une vraie
# panne. Pour le BAC seulement, le jeu est réputé fermé.
L.jeu_ouvert = lambda jeu: False
try:
    _batir_faux_jeu(bac, casse=True)
    soucis = L.resume_controle(L.controler_installation(bac))[1]
    verifier_vrai("les trois pannes sont vues (%d soucis)" % soucis,
                  soucis >= 3)
    trop_bas = os.path.join(bac, "Interface", "AddOns")
    verifier_vrai("Interface\\AddOns : accepté par jeu_valide, REFUSÉ par "
                  "racine_jeu",
                  L.jeu_valide(trop_bas) and not L.racine_jeu(trop_bas))
    verifier("corriger_dossier_jeu remonte à la racine",
             L.corriger_dossier_jeu(trop_bas)[0], bac)
    # Data\enUS et Sound contiennent eux aussi un « Interface » : c'est ce
    # faux positif qui faisait installer à côté sans un mot.
    os.makedirs(os.path.join(bac, "Data", "Interface"), exist_ok=True)
    pseudo = os.path.join(bac, "Data")
    verifier_vrai("Data\\ n'est pas pris pour la racine du jeu",
                  L.jeu_valide(pseudo) and not L.racine_jeu(pseudo))
    verifier("un faux dossier de jeu ne liste RIEN à supprimer",
             [e for e in L.elements_desinstallation(pseudo, [])
              if e["cle"] not in ("config", "restes")], [])

    for quoi in ("imbriquees", "addons_txt", "interrupteur"):
        fait, message = L.reparer(bac, quoi)
        verifier_vrai("réparation « %s » : %s" % (quoi, message), fait)
    verifier("plus aucun souci après réparation",
             L.resume_controle(L.controler_installation(bac))[1], 0)
    sauvegarde = io.open(os.path.join(bac, "WTF", "Account", COMPTE_ESSAI,
                                      "SavedVariables", "AscensionFR.lua"),
                         encoding="utf-8").read()
    verifier_vrai("la sauvegarde a perdu SA SEULE ligne fautive",
                  "desactive" not in sauvegarde
                  and "DernierTotal" in sauvegarde
                  and "minimapAngle" in sauvegarde)

    catalogue = [{"nom": "DragonUI", "dossier": "DragonUI",
                  "dossiers": ["DragonUI_Options"]}]
    # On écarte ce qui vit hors du bac : ce banc ne doit toucher ni la config
    # du Hub ni le %TEMP% de la machine.
    elements = [e for e in L.elements_desinstallation(bac, catalogue)
                if e["cle"] not in ("config", "restes")]
    choisis = [e for e in elements if e["coche"]]
    annonces = {c for e in choisis for c in e["chemins"]}
    _resultats, tout = L.desinstaller_tout(bac, choisis)
    verifier_vrai("tout ce qui était coché est parti", tout)
    verifier_vrai("rien de ce qui était ANNONCÉ n'a survécu",
                  not any(os.path.exists(c) for c in annonces))
    restes = {os.path.relpath(os.path.join(d, f), bac)
              for d, _s, fs in os.walk(bac) for f in fs}
    for parti in ("Interface\\AddOns\\AscensionFR\\AscensionFR.toc",
                  "Interface\\PTRXML\\PTR.xml",
                  "Sound\\CREATURE\\Sylvanas\\a.wav",
                  "WTF\\Account\\%s\\SavedVariables\\AscensionFR.lua"
                  % COMPTE_ESSAI):
        verifier_vrai("retiré : " + parti, parti not in restes)
    verifier_vrai("le pack son PERSONNEL du joueur est intact",
                  "Sound\\MonPackPerso\\a_moi.wav" in restes)
    verifier_vrai("les fichiers du client sont intacts",
                  "Ascension.exe" in restes and "Wow.ini" in restes)
    verifier_vrai("l'addon d'un autre auteur (décoché) est intact",
                  os.path.isdir(os.path.join(bac, "Interface", "AddOns",
                                             "DragonUI")))

    # Les deux pièges relevés par la revue du 26/07.
    _batir_faux_jeu(bac, casse=True)
    imbrique = os.path.join(bac, "Interface", "AddOns", "Interface")
    _ecrire(os.path.join(imbrique, "AddOns", "PasANous", "PasANous.toc"),
            "## Version: 1.0\n")
    point = [p for p in L.controler_installation(bac)
             if p["cle"] == "dossier"][0]
    fait, _m = L.reparer(bac, "imbriquees")
    verifier_vrai("on n'efface pas un dossier où traîne l'addon d'un autre",
                  point["reparable"] is None and not fait
                  and os.path.isdir(os.path.join(imbrique, "AddOns",
                                                 "PasANous")))
    _ecrire(os.path.join(bac, "WTF", "Account", COMPTE_ESSAI, ROYAUME_ESSAI,
                         "Deuxieme", "AddOns.txt"), "AscensionFR: enabled\n")
    point = [p for p in L.controler_installation(bac)
             if p["cle"] == "addon_coche"][0]
    verifier("1 perso décoché sur 2 = réserve, pas souci (sinon le Hub reste "
             "rouge à vie)", point["etat"], "reserve")
finally:
    shutil.rmtree(bac, ignore_errors=True)

# --------------------------------------------------------------------------
print("")
print("=== 7. La doctrine de version : une mise à jour = UN numéro ===")
#
# Ajouté le 28/07/2026, après la boucle de mise à jour infinie : la release
# v3.3.1 « Hub seul » (publiée hors de publier_github.py) portait un tag plus
# haut que le .toc de l'addon qu'elle contenait — le Hub comparait les deux
# et proposait la mise à jour POUR TOUJOURS, chez 100 % des utilisateurs.
# Doctrine de Dan : VERSION_COMPAGNON = « ## Version: » du .toc vivant = tag
# de release, en permanence.

# Le cas qui a tout déclenché : installé 3.3.0, release 3.3.1 → proposé (le
# joueur en retard doit toujours l'être)...
verifier("un joueur en retard se voit proposer la mise à jour",
         L.mise_a_jour_dispo("3.3.0", "3.3.1"), True)
verifier("un joueur en retard d'une mineure aussi",
         L.mise_a_jour_dispo("3.3.1", "3.4.0"), True)
# ...et le joueur à jour, RIEN. C'est l'égalité des numéros qui garantit
# qu'après une mise à jour réussie, la comparaison s'éteint.
verifier("un joueur à jour n'a RIEN de proposé",
         L.mise_a_jour_dispo("3.4.0", "3.4.0"), False)
verifier("un joueur plus récent que la release non plus",
         L.mise_a_jour_dispo("3.4.0", "3.3.1"), False)
# L'ancienne numérotation interne (2.2, 2.3) reste rapatriée vers l'avant.
verifier("l'ancienne numérotation interne 2.2 est bien rapatriée",
         L.mise_a_jour_dispo("2.2", "1.7.5"), True)

# L'alignement VIVANT : le numéro baké dans le Hub est celui du .toc de
# l'addon d'à côté. Un écart ici = la boucle de mise à jour re-fabriquée.
_toc_vivant = os.path.normpath(os.path.join(
    BASE, "..", "WOW_Priv", "resources", "ascension-live",
    "Interface", "AddOns", "AscensionFR", "AscensionFR.toc"))
_m = re.search(r"##\s*Version:\s*(\S+)",
               io.open(_toc_vivant, encoding="utf-8").read())
verifier("VERSION_COMPAGNON = .toc vivant (doctrine)",
         L.VERSION_COMPAGNON, _m.group(1) if _m else "?")
# Et le bandeau « le Hub a une version plus récente » s'appuie sur le MÊME
# numéro unique : quand la release porte le numéro du .toc vivant (doctrine
# respectée) et que le Hub est celui de cette release, pas de bandeau.
_derniere_simulee = _m.group(1) if _m else "?"
verifier_vrai("à jour, pas de bandeau de remplacement du Hub non plus",
              not (L.en_tuple(_derniere_simulee)
                   > L.en_tuple(L.VERSION_COMPAGNON)))

print("")
print("%d échec(s)" % len(echecs))
sys.exit(1 if echecs else 0)
