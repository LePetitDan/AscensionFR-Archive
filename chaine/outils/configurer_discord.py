# -*- coding: utf-8 -*-
"""
Met le serveur Discord en ordre : rôles, droits, salons.

Conçu pour être REJOUABLE sans dégât : chaque action vérifie d'abord si elle
est déjà faite. Relancer le script ne crée pas de doublon et ne casse rien.

Ce qu'il fait :
  1. retire à @everyone les droits dangereux (mentionner tout le monde,
     créer des fils privés) ;
  2. crée les rôles Modérateur et Contributeur s'ils manquent ;
  3. passe les salons d'information en lecture seule — réactions gardées ;
  4. ouvre les forums (signalements, suggestions) ;
  5. ajoute un salon vocal au coin des joueurs.

Rien n'est supprimé, jamais. Le salon privé des rapports n'est pas touché.

Usage :
  python outils/configurer_discord.py           (aperçu, n'écrit rien)
  python outils/configurer_discord.py --appliquer
"""
import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(BASE, "discord_aspirateur.json")
API = "https://discord.com/api/v10"

D = {                                  # bits de permission Discord
    "inviter":        1 << 0,
    "gerer_salons":   1 << 4,
    "reactions":      1 << 6,
    "voir":           1 << 10,
    "ecrire":         1 << 11,
    "gerer_messages": 1 << 13,
    "liens":          1 << 14,
    "fichiers":       1 << 15,
    "historique":     1 << 16,
    "mentionner_tous": 1 << 17,
    "vocal_parler":   1 << 21,
    "vocal_rejoindre": 1 << 20,
    "exclure":        1 << 40,         # exclusion temporaire
    "fils_publics":   1 << 35,
    "fils_prives":    1 << 36,
    "ecrire_fils":    1 << 38,
}

# Les salons d'information : on lit, on réagit, on n'écrit pas.
LECTURE_SEULE = ("📢-annonces", "🧾patch-note", "📖-installation")
# Les forums où la communauté s'exprime.
OUVERTS = ("🐛-signalements", "💡suggestion")

JETON = json.load(open(CONFIG, encoding="utf-8"))["jeton"]
APPLIQUER = "--appliquer" in sys.argv
actions = []


def api(chemin, donnees=None, methode="GET"):
    corps = json.dumps(donnees).encode("utf-8") if donnees is not None else None
    req = urllib.request.Request(
        API + chemin, data=corps, method=methode,
        headers={"Authorization": "Bot " + JETON,
                 "Content-Type": "application/json",
                 "User-Agent": "AscensionFR-Config"})
    with urllib.request.urlopen(req, timeout=30) as r:
        brut = r.read().decode("utf-8")
        return json.loads(brut) if brut.strip() else {}


def faire(description, chemin, donnees, methode):
    """Exécute une modification, ou l'annonce seulement en mode aperçu."""
    actions.append(description)
    if not APPLIQUER:
        print("  [aperçu] " + description)
        return None
    try:
        resultat = api(chemin, donnees, methode)
        print("  ✓ " + description)
        return resultat
    except urllib.error.HTTPError as e:
        print("  ! ÉCHEC : %s (%s)" % (description, e.read()[:160]))
        return None


def sans_risque(permissions):
    """Retire les droits qu'un membre ordinaire ne doit pas avoir."""
    return permissions & ~(D["mentionner_tous"] | D["fils_prives"]
                           | D["gerer_messages"] | D["gerer_salons"])


def main():
    guilde = api("/channels/1527998972000469052")["guild_id"]
    roles = api("/guilds/%s/roles" % guilde)
    par_nom = {r["name"]: r for r in roles}
    everyone = next(r for r in roles if r["id"] == guilde)
    salons = api("/guilds/%s/channels" % guilde)
    par_salon = {c["name"]: c for c in salons}

    print("=== 1. Droits de @everyone ===")
    actuels = int(everyone["permissions"])
    vises = sans_risque(actuels)
    if actuels != vises:
        perdus = [n for n, b in D.items() if actuels & b and not vises & b]
        faire("retirer à @everyone : " + ", ".join(perdus),
              "/guilds/%s/roles/%s" % (guilde, everyone["id"]),
              {"permissions": str(vises)}, "PATCH")
    else:
        print("  (déjà propre)")

    print()
    print("=== 2. Rôles ===")
    # Modérateur : agit sur les MESSAGES et les personnes, jamais sur la
    # structure du serveur (ni salons, ni rôles, ni bannissement).
    souhaites = [
        ("Modérateur", D["voir"] | D["ecrire"] | D["historique"]
         | D["reactions"] | D["liens"] | D["fichiers"] | D["ecrire_fils"]
         | D["fils_publics"] | D["gerer_messages"] | D["exclure"]
         | D["vocal_rejoindre"] | D["vocal_parler"], 0x3498DB),
        # Contributeur : purement honorifique — aucun pouvoir, une couleur.
        ("Contributeur", D["voir"] | D["ecrire"] | D["historique"]
         | D["reactions"] | D["liens"] | D["fichiers"] | D["ecrire_fils"]
         | D["fils_publics"] | D["vocal_rejoindre"] | D["vocal_parler"],
         0x2ECC71),
    ]
    for nom, permissions, couleur in souhaites:
        if nom in par_nom:
            print("  (le rôle « %s » existe déjà)" % nom)
            continue
        faire("créer le rôle « %s »" % nom, "/guilds/%s/roles" % guilde,
              {"name": nom, "permissions": str(permissions),
               "color": couleur, "hoist": True, "mentionable": True}, "POST")

    print()
    print("=== 3. Salons d'information (lecture seule) ===")
    # Un refus posé sur @everyone s'applique AUSSI au bot : verrouiller un
    # salon l'y enferme avec tout le monde (vécu le 19/07 — le bot ne pouvait
    # plus publier ses propres annonces). D'où l'exception qui suit chaque
    # verrouillage, sur son rôle, appliquée APRÈS le réglage @everyone.
    moi = api("/users/@me")
    role_bot = next((r for r in roles if r.get("managed")
                     and r["name"] == moi["username"]), None)

    for nom in LECTURE_SEULE:
        salon = par_salon.get(nom)
        if not salon:
            print("  ! salon introuvable : %s" % nom)
            continue
        # On refuse l'écriture, on garde la lecture ET les réactions.
        faire("%s : lecture seule (réactions gardées)" % nom,
              "/channels/%s/permissions/%s" % (salon["id"], guilde),
              {"type": 0,
               "allow": str(D["voir"] | D["historique"] | D["reactions"]),
               "deny": str(D["ecrire"] | D["fils_publics"] | D["fils_prives"]
                           | D["ecrire_fils"] | D["mentionner_tous"])},
              "PUT")
        if role_bot:
            faire("%s : garder le droit d'y publier (bot)" % nom,
                  "/channels/%s/permissions/%s" % (salon["id"],
                                                   role_bot["id"]),
                  {"type": 0, "deny": "0",
                   "allow": str(D["voir"] | D["ecrire"] | D["historique"]
                                | D["mentionner_tous"] | D["liens"]
                                | D["fichiers"])},
                  "PUT")

    print()
    print("=== 4. Forums ouverts à tous ===")
    for nom in OUVERTS:
        salon = par_salon.get(nom)
        if not salon:
            print("  ! salon introuvable : %s" % nom)
            continue
        faire("%s : ouvert (poster et répondre)" % nom,
              "/channels/%s/permissions/%s" % (salon["id"], guilde),
              {"type": 0,
               "allow": str(D["voir"] | D["historique"] | D["reactions"]
                            | D["ecrire"] | D["fils_publics"]
                            | D["ecrire_fils"] | D["fichiers"] | D["liens"]),
               "deny": str(D["mentionner_tous"] | D["fils_prives"])},
              "PUT")

    print()
    print("=== 5. Coin des joueurs ===")
    categorie = next((c for c in salons
                      if c["type"] == 4 and c["name"] == "Zog_Zog"), None)
    if not categorie:
        print("  ! catégorie Zog_Zog introuvable")
    elif any(c["type"] == 2 and c.get("parent_id") == categorie["id"]
             for c in salons):
        print("  (un salon vocal existe déjà)")
    else:
        faire("créer le salon vocal « 🔊 Taverne »",
              "/guilds/%s/channels" % guilde,
              {"name": "🔊 Taverne", "type": 2,
               "parent_id": categorie["id"]}, "POST")

    print()
    if not APPLIQUER:
        print("APERÇU — %d action(s) prête(s). Ajoute --appliquer pour agir."
              % len(actions))
    else:
        print("%d action(s) exécutée(s)." % len(actions))
    return 0


if __name__ == "__main__":
    sys.exit(main())
