# -*- coding: utf-8 -*-
"""
aspirer_discord.py — télécharge automatiquement les rapports postés dans le
salon Discord des rapports (par le Compagnon ou à la main) vers
traduction/rapports/. Plus aucun téléchargement manuel.

FLUX COMPLET (collecte automatique)
-----------------------------------
  joueur : Compagnon -> « Envoyer mon rapport » -> salon #rapports-auto
  toi    : python outils/aspirer_discord.py            (aspire les nouveautés)
           python outils/ingerer_rapport.py            (traduit les échecs)
       ou : python outils/aspirer_discord.py --ingerer (les deux d'un coup)

CONFIGURATION (une seule fois) — voir traduction/discord_aspirateur.json :
  { "jeton": "<jeton du bot>", "salon": "<identifiant du salon>", ... }
Le script crée le fichier modèle s'il manque et explique quoi remplir.
NE JAMAIS partager ce fichier : le jeton donne accès au bot.

Seuls les .txt raisonnables (< 1 Mo) sont téléchargés ; chaque message n'est
traité qu'une fois (mémoire du dernier message vu + noms de fichiers uniques).
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ecriture_sure import ecrire_json  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(BASE, "discord_aspirateur.json")
RAPPORTS = os.path.join(BASE, "rapports")
# Les pièces jointes qui résistent, passage après passage (29/07/2026).
# Même mécanique que traductions/rejets_chroniques.json : on compte les
# échecs, et au bout de SEUIL_ABANDON passages on CONSIGNE la pièce et on
# laisse le marque-page repartir. Un fichier perdu est regrettable ; un
# compteur gelé pour toujours l'est plus — c'est ce qui a mis deux jours
# de rapports en attente.
MORTES = os.path.join(BASE, "traductions", "pieces_jointes_mortes.json")
SEUIL_ABANDON = 3
# Réessais DANS le passage : sur 200 téléchargements, un raté aléatoire
# suffisait à geler le marque-page. Mesuré le 29/07 : la pièce qui avait
# échoué passe 3 fois sur 3 à la tentative suivante — c'était un hoquet.
ESSAIS = 3
PAUSES = (1.5, 4.0)
API = "https://discord.com/api/v10"
UA = "AscensionFR-Aspirateur/1.0"

MODELE = {
    "jeton": "",
    "salon": "",
    "dernier_message": "0",
    "_aide": ("jeton = jeton du BOT (discord.com/developers -> ton appli -> "
              "Bot -> Reset Token). salon = identifiant du salon des rapports "
              "(clic droit sur le salon -> Copier l'identifiant, avec le mode "
              "developpeur active). NE PARTAGE JAMAIS ce fichier."),
}


def charger_config():
    if not os.path.exists(CONFIG):
        ecrire_json(CONFIG, MODELE, sort_keys=False)
        print("Première utilisation : je viens de créer\n  %s" % CONFIG)
        print("Remplis « jeton » et « salon » (voir _aide dedans), puis relance.")
        return None
    with open(CONFIG, encoding="utf-8") as f:
        cfg = json.load(f)
    if not cfg.get("jeton") or not cfg.get("salon"):
        print("Configuration incomplète : remplis « jeton » et « salon » dans")
        print("  %s" % CONFIG)
        return None
    return cfg


def sauver_config(cfg):
    # Atomique (programme 31, bloc B) : ce fichier porte le JETON du bot
    # et le marque-page — une coupure au milieu corrompait les deux.
    ecrire_json(CONFIG, cfg, sort_keys=False)


def api_get(chemin, jeton):
    """Appel API, avec RÉESSAIS sur les pannes PASSAGÈRES.

    Le relevé du 29/07 le prouve : l'aspiration sortait en code 1 alors
    que rien n'était cassé — un hoquet pendant la PAGINATION des messages
    suffisait. On distingue donc deux familles :
      - 401 / 403 / 404 : le jeton, les droits ou le salon sont en cause.
        Réessayer n'y changerait rien, on relaie tout de suite.
      - le reste (coupure, 5xx, 429…) : on retente, comme pour les
        téléchargements.
    """
    derniere = None
    for tentative in range(ESSAIS):
        try:
            req = urllib.request.Request(API + chemin, headers={
                "Authorization": "Bot " + jeton, "User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403, 404):
                raise
            derniere = e
        except Exception as e:
            derniere = e
        if tentative < ESSAIS - 1:
            time.sleep(PAUSES[min(tentative, len(PAUSES) - 1)])
    raise derniere


def telecharger(url, destination):
    """Télécharge, avec RÉESSAIS et écriture atomique.

    Deux protections d'un coup :
      - ESSAIS tentatives espacées : un hoquet réseau ne condamne plus
        la pièce (et donc le marque-page) ;
      - on écrit à côté, on met en place au succès : une coupure ne
        laisse pas un .gz tronqué que l'ingestion prendrait pour bon.

    Rend le nombre de tentatives ratées avant le succès (0 = du premier
    coup) ; lève la dernière exception si tout échoue.
    """
    provisoire = destination + ".part"
    derniere = None
    for tentative in range(ESSAIS):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r, \
                    open(provisoire, "wb") as f:
                f.write(r.read())
            os.replace(provisoire, destination)
            return tentative
        except Exception as e:
            derniere = e
            try:
                os.remove(provisoire)
            except OSError:
                pass
            if tentative < ESSAIS - 1:
                time.sleep(PAUSES[min(tentative, len(PAUSES) - 1)])
    raise derniere


def charger_mortes():
    try:
        with open(MORTES, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def sauver_mortes(mortes):
    # Atomique (programme 31, bloc B) — ecrire_json crée le dossier.
    ecrire_json(MORTES, mortes)


def nom_sur(nom):
    """Nom de fichier sans surprise (caractères sûrs uniquement)."""
    return re.sub(r"[^A-Za-z0-9._-]", "_", nom)[:80]


def main():
    cfg = charger_config()
    if cfg is None:
        return 1
    os.makedirs(RAPPORTS, exist_ok=True)

    # Messages APRÈS le dernier vu, page par page (100 max par appel).
    dernier = str(cfg.get("dernier_message") or "0")
    nouveaux, page_apres = [], dernier
    while True:
        try:
            page = api_get("/channels/%s/messages?limit=100&after=%s"
                           % (cfg["salon"], page_apres), cfg["jeton"])
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print("! Jeton refusé (401) : recopie le jeton du bot.")
            elif e.code == 403:
                print("! Accès refusé (403) : le bot est-il invité sur le "
                      "serveur, avec le droit de VOIR ce salon et de LIRE "
                      "l'historique ?")
            elif e.code == 404:
                print("! Salon introuvable (404) : vérifie l'identifiant.")
            else:
                print("! Discord répond HTTP %d après %d tentatives."
                      % (e.code, ESSAIS))
            return 1
        except Exception as e:
            # Réseau coupé, délai dépassé… : api_get a déjà réessayé
            # ESSAIS fois. On sort proprement au lieu de laisser une
            # trace de pile — mais bien en ROUGE : là, il y a vraiment
            # quelque chose à regarder.
            print("! Discord injoignable après %d tentatives : %s"
                  % (ESSAIS, e))
            return 1
        if not page:
            break
        nouveaux.extend(page)
        if len(page) < 100:
            break
        page_apres = max(m["id"] for m in page)

    if not nouveaux:
        print("Rien de nouveau dans le salon.")
        return 0

    nouveaux.sort(key=lambda m: int(m["id"]))
    pris, ignores = 0, 0
    rattrapes, abandonnees, consignees = 0, 0, []
    mortes = charger_mortes()
    # Le marque-page n'avance que sur les messages entièrement récupérés. Sans
    # cela, un simple hoquet réseau faisait avancer le curseur par-dessus un
    # rapport manqué : le bot ne le relisait plus JAMAIS, et la contribution du
    # joueur était perdue en silence.
    #
    # MAIS l'intention seule ne suffisait pas (mesuré le 29/07/2026) : sans
    # réessai ni sortie de secours, UN raté aléatoire sur 200 gelait le
    # compteur POUR TOUJOURS, et « sera repris au prochain passage » était
    # faux. Deux ajouts : on réessaie dans le passage (telecharger), et une
    # pièce qui a résisté SEUIL_ABANDON passages est consignée — elle cesse
    # alors de retenir le marque-page, sans disparaître du registre.
    dernier_complet = None
    rate = False
    for m in nouveaux:
        message_ok = True
        for pj in m.get("attachments", []):
            nom = pj.get("filename", "")
            nom_min = nom.lower()
            # Deux familles acceptées : le rapport texte, et les caches du
            # jeu que le Compagnon (v1.5+) joint en .json.gz.
            rapport_txt = (nom_min.endswith(".txt")
                           and pj.get("size", 0) <= 1_000_000)
            caches_gz = (nom_min.startswith("caches_")
                         and nom_min.endswith(".json.gz")
                         and pj.get("size", 0) <= 10_000_000)
            if not (rapport_txt or caches_gz):
                ignores += 1
                continue
            destination = os.path.join(
                RAPPORTS, "auto_%s_%s" % (m["id"], nom_sur(nom)))
            if os.path.exists(destination):
                continue
            cle = "%s/%s" % (m["id"], nom)
            if mortes.get(cle, {}).get("echecs", 0) >= SEUIL_ABANDON:
                abandonnees += 1        # déjà consignée : ne bloque plus
                continue
            try:
                ratees = telecharger(pj["url"], destination)
                pris += 1
                if ratees:
                    rattrapes += 1
                    print("  + %s (rattrapé au %dᵉ essai)"
                          % (os.path.basename(destination), ratees + 1))
                else:
                    print("  + %s" % os.path.basename(destination))
                mortes.pop(cle, None)
            except Exception as e:
                fiche = mortes.setdefault(cle, {"echecs": 0})
                fiche["echecs"] += 1
                fiche["dernier"] = str(e)[:200]
                fiche["quand"] = time.strftime("%Y-%m-%d %H:%M")
                if fiche["echecs"] >= SEUIL_ABANDON:
                    consignees.append(cle)
                    print("  ! %s : %d passages en échec — CONSIGNÉE, le "
                          "marque-page repart (%s)"
                          % (nom, fiche["echecs"], e))
                else:
                    print("  ! échec %s : %s (%d/%d passages ; reprise au "
                          "prochain)" % (nom, e, fiche["echecs"],
                                         SEUIL_ABANDON))
                    message_ok = False
        if message_ok and not rate:
            dernier_complet = m["id"]
        elif not message_ok:
            rate = True

    if mortes:
        sauver_mortes(mortes)
    if dernier_complet:
        cfg["dernier_message"] = str(dernier_complet)
        sauver_config(cfg)
    print("%d fichier(s) téléchargé(s) (rapports et caches), %d pièce(s) "
          "ignorée(s)." % (pris, ignores))
    # Les comptes du passage (programme 31, bloc F) — ici « tentées » =
    # pièces jointes à prendre, « traduites » = téléchargées.
    print("@@BILAN " + json.dumps(
        {"tentees": pris + len(consignees) + (1 if rate else 0),
         "traduites": pris,
         "refusees": len(consignees) + (1 if rate else 0),
         "ecartees": ignores + abandonnees}))
    if rattrapes:
        print("%d pièce(s) RATTRAPÉE(S) par un réessai — sans lui, le "
              "marque-page se figeait ici." % rattrapes)
    if consignees:
        print("%d pièce(s) CONSIGNÉE(S) après %d passages (détail : "
              "traductions/pieces_jointes_mortes.json) : %s"
              % (len(consignees), SEUIL_ABANDON, ", ".join(consignees[:3])))
    if abandonnees:
        print("%d pièce(s) déjà consignée(s) sautée(s) — elles ne retiennent "
              "plus le marque-page." % abandonnees)
    if rate:
        print("! Des pièces n'ont pas pu être téléchargées : relance "
              "l'Atelier plus tard, elles seront reprises.")

    if pris and "--ingerer" in sys.argv:
        print("\nIngestion…")
        codes = [subprocess.run(
            [sys.executable, os.path.join(BASE, "outils", n)]).returncode
            for n in ("ingerer_rapport.py", "ingerer_caches.py")]
        return max(codes)
    if pris:
        print("Suite : python outils/ingerer_rapport.py puis "
              "python outils/ingerer_caches.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
