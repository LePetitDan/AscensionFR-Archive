# -*- coding: utf-8 -*-
"""
Publie un message sur un salon Discord du serveur AscensionFR, via le bot.

Sert aux annonces de version et aux notes de patch : le texte se prépare dans
un fichier (relisible, corrigeable), et on le poste quand il est validé.

PRUDENCE VOULUE : sans --envoyer, RIEN n'est publié — le script se contente
d'afficher l'aperçu et de compter les caractères (Discord coupe à 2000).

Usage :
  python outils/publier_discord.py annonces discord/v1/annonce_1.5.md
  python outils/publier_discord.py annonces discord/v1/annonce_1.5.md --envoyer

Salons connus : annonces, installation, discussion, rapports
(le forum signalements demande de créer un fil : droit non accordé au bot).
"""
import json
import os
import sys
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(BASE, "discord_aspirateur.json")
API = "https://discord.com/api/v10"
LIMITE = 2000

SALONS = {
    "annonces":     "1527717854630379770",
    "patchnote":    "1528159144325152931",
    "installation": "1527717972397920527",
    "discussion":   "1528005439508185158",
    "rapports":     "1527998972000469052",
}

# Rituel de déploiement (fixé le 19/07/2026) : à CHAQUE version, un résumé
# très bref dans « annonces », et le détail complet dans « patchnote ».
# L'annonce commence TOUJOURS par @everyone — sans mention elle passe
# inaperçue. Le patch note, lui, n'en met pas : ce serait du bruit.
MENTION_ATTENDUE = {"annonces"}


def jeton():
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)["jeton"]


def api(chemin, donnees=None, methode=None):
    corps = json.dumps(donnees).encode("utf-8") if donnees else None
    req = urllib.request.Request(
        API + chemin, data=corps,
        method=methode or ("POST" if donnees else "GET"),
        headers={"Authorization": "Bot " + jeton(),
                 "Content-Type": "application/json",
                 "User-Agent": "AscensionFR-Publication"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print(__doc__)
        return 1
    alias, fichier = args[0], args[1]
    salon = SALONS.get(alias, alias)      # un identifiant brut passe aussi

    chemin = fichier if os.path.isabs(fichier) else os.path.join(BASE, fichier)
    if not os.path.isfile(chemin):
        print("! Fichier introuvable : %s" % chemin)
        return 1
    with open(chemin, encoding="utf-8") as f:
        message = f.read().strip()

    nom = api("/channels/%s" % salon).get("name", salon)
    print("Salon      : #%s" % nom)
    print("Caractères : %d / %d" % (len(message), LIMITE))
    if len(message) > LIMITE:
        print("! Trop long de %d caractères — Discord refuserait. Raccourcis "
              "le texte." % (len(message) - LIMITE))
        return 1
    print("-" * 60)
    print(message)
    print("-" * 60)
    # --sans-mention : l'exception, à demander EXPRÈS (24/07/2026, choix de
    # Dan pour la 3.0.1 sortie le jour même que la 3.0.0 — un second ping
    # aurait été du spam). Le garde-fou reste actif par défaut : il faut
    # écrire le drapeau, on ne peut pas oublier la mention par accident.
    if (alias in MENTION_ATTENDUE and "@everyone" not in message
            and "--sans-mention" not in sys.argv):
        print("! Ce salon attend un @everyone en tête — sans mention, "
              "l'annonce passe inaperçue. Ajoute-le avant de publier,")
        print("  ou passe --sans-mention si c'est VOULU (seconde sortie "
              "dans la journée, correctif discret…).")
        return 1

    if "--envoyer" not in sys.argv:
        print("APERÇU seulement — rien n'a été publié.")
        print("Pour publier pour de vrai : ajoute --envoyer")
        return 0

    # allowed_mentions explicite : sans lui, un @everyone dans le texte peut
    # rester lettre morte selon la configuration du salon.
    contenu = {"content": message,
               "allowed_mentions": {"parse": ["everyone", "users", "roles"]}}

    # --remplacer <id> : réécrit un message DÉJÀ publié plutôt que d'en
    # empiler un nouveau (une coquille ne mérite pas un second post).
    # Ne marche que sur les messages du bot : Discord interdit de modifier
    # ceux de quelqu'un d'autre.
    a_remplacer = None
    for i, argument in enumerate(sys.argv):
        if argument == "--remplacer" and i + 1 < len(sys.argv):
            a_remplacer = sys.argv[i + 1]
    if a_remplacer:
        poste = api("/channels/%s/messages/%s" % (salon, a_remplacer),
                    contenu, methode="PATCH")
        print("Message %s réécrit sur #%s." % (a_remplacer, nom))
        return 0

    poste = api("/channels/%s/messages" % salon, contenu)
    print("Publié sur #%s (message %s)." % (nom, poste["id"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
