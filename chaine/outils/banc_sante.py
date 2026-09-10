# -*- coding: utf-8 -*-
r"""LE BANC DE SANTÉ QUI MORD (bloc D1, 29/07/2026 — proposition n° 1 de
l'audit). Le défaut structurel du pipeline est le SILENCE de ses pannes :
ce banc les rend bruyantes, en un seul code retour.

Ce qu'il rejoue :
  1. le banc MOTEUR population entière des sorts (seuil : 1 200 échecs —
     mesuré à 745 le 29/07 ; il tourne en ~20 s) ;
  2. verifier_addon — le SEUL test d'exécution dans l'environnement WoW
     simulé, qu'aucun script de release n'imposait ;
  3. la SUITE des bancs, chacun avec son code retour ATTENDU — c'est ce
     qui distingue enfin un rouge assumé d'un rouge NOUVEAU ;
  4. le webhook des rapports : un GET sans envoi (l'API Discord décrit le
     webhook sans poster) — 401/404 = webhook mort = ROUGE ; réseau
     absent = avertissement seulement ;
  5. la fraîcheur de la veille Discord (tâche de 18 h 45) :
     avertissement > 30 h, ROUGE > 78 h (marge pour un PC éteint un jour) ;
  6. les codes retour du dernier passage de l'Atelier
     (rapports/atelier_sante.json, écrit par le compagnon — bloc E) :
     ROUGE si une étape a fini en erreur ; absent = avertissement.

Codes retour : 0 = tout va ; 1 = au moins un ROUGE. Les avertissements
s'affichent mais ne mordent pas — un banc qui crie pour rien se
désactive au bout de trois jours.

Usage : python outils/banc_sante.py [--sans-reseau] [--vite]
        --vite saute le banc moteur (~20 s) et la suite des bancs — pour
        l'horloge quotidienne, la release fait toujours tout.
"""
import io
import json
import os
import subprocess
import sys
import time

# Sous pythonw (la tâche planifiée), stdout n'existe PAS : imprimer
# tuerait le script en silence — le piège cp1252, en pire. Tout passe
# par dire(), qui écrit AUSSI le relevé sur disque : c'est le relevé qui
# fait foi pour l'horloge.
if sys.stdout is not None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTILS = os.path.join(BASE, "outils")
VEILLE = r"D:\AscensionFR\3-atelier\veille-discord"
ATELIER_SANTE = os.path.join(BASE, "rapports", "atelier_sante.json")
RELEVE = os.path.join(BASE, "rapports", "banc_sante_dernier.txt")

_lignes = []


def dire(texte=""):
    _lignes.append(texte)
    if sys.stdout is not None:
        print(texte)

# La suite des bancs et leur code retour ATTENDU. Un banc absent de cette
# table qui existe sur le disque est signalé (avertissement) : la table
# doit suivre la vie du dépôt.
BANCS_ATTENDUS = {
    "verifier_tout.py": 0,
    # Programme 28 (07/08/2026) : les globales de AscensionFR_Glue.lua contre
    # l'officiel du client. La famille Emzime — un %d que le jeu n'attend pas
    # fait planter les add-ons qui composent la globale. Branché APRÈS le
    # correctif des 14, et vu mordre (valeur cassée exprès -> code 1).
    "verifier_formats_glue.py": 0,
    "verifier_addon.py": 0,
    "verifier_hub.py": 0,
    "verifier_interface.py": 0,
    "verifier_signalements.py": 0,
    "verifier_repliques.py": 0,
    "verifier_coa.py": 0,
    "verifier_hdv.py": 0,
    "verifier_plaques.py": 0,
    # LES LAGS EN JEU (programme 10, 01/08/2026). Deux entrées, et il en faut
    # bien deux :
    #   - verifier_barres.py tient le ZÉRO ALLOCATION par tic. Ses sept
    #     assertions de traduction restaient vertes des deux côtés du
    #     correctif ; c'est la huitième, ajoutée le 01/08, qui mord — éprouvée
    #     en réintroduisant la faute (4 888 o/tic contre 58).
    #   - verifier_perf.py tient l'INSTRUMENT lui-même : attribution du cadre
    #     de Plaques sans toucher au fichier, moyenne ET pire distingués, pas
    #     d'enrobage qui s'empile, et « éteinte = absente ».
    # Le banc des barres existait déjà mais n'était lancé par personne : il
    # n'était donc pas un garde-fou, seulement une intention.
    "verifier_barres.py": 0,
    "verifier_perf.py": 0,
    # LA DÉTECTION DES FENÊTRES (programme 11, 01/08/2026). Deux bancs dans un
    # seul fichier, et il en faut bien deux : la correction ÉCHANGE du coût
    # contre un risque. Éprouvé dans les deux sens — le défaut d'origine fait
    # rougir le banc de coût (15 678 visites contre 1 206), et la correction
    # naïve « on n'y revient jamais » fait rougir le banc fonctionnel en
    # perdant deux traductions. Aucun des deux seul n'aurait protégé.
    "verifier_detection_fenetres.py": 0,
    # LES GREFFES (programme 12, 01/08/2026). Ascension pousse des patchs de
    # contenu sans prévenir ; une greffe posée sur une fonction renommée ne
    # fait pas planter le jeu, elle SE TAIT — et la fenêtre reste en anglais
    # jusqu'à ce qu'un joueur l'ouvre. Ce banc ne peut pas trancher tout seul
    # (le juge de paix est `/afr greffes` en jeu), mais il MORD sur ce qui,
    # lui, est vérifiable hors du jeu : que la liste interrogée par la sonde
    # colle aux greffes réellement posées dans les modules. Une greffe ajoutée
    # sans y être inscrite ne serait jamais vérifiée, et la sonde dirait
    # « tout va bien » en regardant à côté.
    "verifier_greffes.py": 0,
    "verifier_minimap.py": 0,
    "verifier_guichets.py": 0,
    "verifier_aspiration.py": 0,
    # le rouge ASSUMÉ (bloc 3 du programme 1) : 1 échec par conception,
    # code 1 attendu — s'il passe à 0 ou 2, c'est un CHANGEMENT à voir
    "verifier_infobulle.py": 1,
    # LES SECRETS (programme 6). Deux entrées, et il en faut bien deux :
    #   - banc_secrets.py éprouve que les garde-fous MORDENT (15 situations
    #     dangereuses fabriquées exprès) ;
    #   - balayer_secrets.py regarde l'état RÉEL du dépôt public, arbre et
    #     historique.
    # Un garde-fou que personne ne lance n'est pas un garde-fou : c'est une
    # intention. Les mettre ici, c'est les faire tourner tous les jours.
    "banc_secrets.py": 0,
    "balayer_secrets.py": 0,
}

# LES EXEMPTIONS SONT ÉCRITES, PAS SILENCIEUSES. Un banc du disque absent
# de BANCS_ATTENDUS est signalé — sauf s'il figure ici AVEC SA RAISON.
# C'est la différence entre « on a décidé de ne pas le lancer » et « on
# l'a oublié » ; sans cette liste, les deux se ressemblent.
# Si un exempté disparaît du disque, l'exemption est signalée à son tour :
# une liste d'exceptions dérive aussi vite que celle qu'elle complète.
HORS_TABLE_ASSUME = {
    "banc_sante.py":
        "c'est ce fichier — le lanceur, pas un banc.",
    "verifier_arbre_publie.py":
        "lancé par publier_github.py au moment de publier, pas tous les "
        "jours : il juge l'arbre PUBLIÉ, qui ne bouge qu'à la publication.",
    "verifier_pr4_windows.py":
        "porte sur du code non fusionné (PR #4) ; documente lui-même son "
        "exclusion.",
}


def lancer(script, *args):
    """Code retour d'un outil, sortie avalée (le détail est dans l'outil)."""
    return subprocess.call(
        [sys.executable, os.path.join(OUTILS, script)] + list(args),
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    sans_reseau = "--sans-reseau" in sys.argv
    vite = "--vite" in sys.argv
    rouges, avertissements = [], []
    t0 = time.time()
    dire("BANC DE SANTÉ — %s%s" % (time.strftime("%d/%m/%Y %H:%M"),
                                    " (--vite)" if vite else ""))
    dire("=" * 60)

    # 1. banc moteur population entière (seuil dans l'outil : 1 200)
    if not vite:
        code = lancer("reparer_alignement_sorts.py", "--banc-seul", "1200")
        if code == 0:
            dire("  ok     banc moteur population entière (≤ 1 200 échecs)")
        else:
            dire("  ROUGE  banc moteur population entière : au-dessus du "
                  "seuil de 1 200 — relancer sans --vite pour le détail")
            rouges.append("banc moteur")

    # 2 + 3. la suite des bancs, code retour attendu par banc
    if not vite:
        for script, attendu in sorted(BANCS_ATTENDUS.items()):
            chemin = os.path.join(OUTILS, script)
            if not os.path.exists(chemin):
                avertissements.append("%s ABSENT du disque" % script)
                dire("  avert. %s : absent du disque" % script)
                continue
            code = lancer(script)
            if code == attendu:
                etat = "ok    " if attendu == 0 else "ok(r) "
                dire("  %s %s (code %d attendu)" % (etat, script, attendu))
            else:
                dire("  ROUGE  %s : code %d (attendu %d) — un rouge "
                      "NOUVEAU" % (script, code, attendu))
                rouges.append(script)

        # LE SENS DISQUE -> TABLE, qui était PROMIS et n'existait pas
        # (mesuré au programme 14, 01/08/2026 : 35 bancs sur le disque,
        # 19 dans la table, 15 lancés par personne — dont banc_double_essai,
        # le SEUL banc du dépôt qui lise la matière première).
        # C'est le motif de verifier_greffes.py appliqué au gardien
        # lui-même : une liste qu'on croit à jour, confrontée à la réalité.
        # AVERTISSEMENT et non ROUGE : un banc pas encore inscrit n'est pas
        # une panne, c'est un oubli de table. Mais il ne doit plus être
        # silencieux.
        for nom in sorted(os.listdir(OUTILS)):
            if not nom.endswith(".py"):
                continue
            if not nom.startswith(("verifier_", "banc_", "balayer_")):
                continue
            if nom in BANCS_ATTENDUS or nom in HORS_TABLE_ASSUME:
                continue
            avertissements.append("%s hors table" % nom)
            dire("  avert. %s : sur le disque, absent de BANCS_ATTENDUS — "
                 "personne ne le lance" % nom)
        for nom, raison in sorted(HORS_TABLE_ASSUME.items()):
            if not os.path.exists(os.path.join(OUTILS, nom)):
                avertissements.append("%s exempté mais absent" % nom)
                dire("  avert. %s : exempté de la table, mais introuvable "
                     "sur le disque — exemption périmée" % nom)

    # 4. le webhook des rapports : GET descriptif, sans rien poster.
    # Depuis le programme 33, la valeur n'est PLUS dans compagnon.py :
    # même résolution que _lire_webhook() — la variable d'environnement,
    # sinon le fichier injecté (gitignoré). L'ancienne sonde cherchait
    # l'affectation disparue et « avertissait » à chaque passage pour rien
    # (corrigé au programme 34 — un faux avertissement use la vigilance).
    if not sans_reseau:
        webhook = os.environ.get("ASCENSIONFR_WEBHOOK", "").strip() or None
        if not webhook:
            try:
                webhook = io.open(
                    os.path.join(BASE, "compagnon", "assets",
                                 "webhook.local.txt"),
                    encoding="utf-8").read().strip() or None
            except (OSError, IOError):
                pass
        if not webhook:
            avertissements.append("webhook absent (ni variable, ni injecté)")
            dire("  avert. webhook : aucune source (ASCENSIONFR_WEBHOOK ou "
                 "assets/webhook.local.txt) — un exe construit là partirait "
                 "muet")
        else:
            try:
                from urllib.request import urlopen, Request
                # User-Agent obligatoire : Cloudflare rend 403 à l'agent
                # urllib par défaut même sur un webhook VIVANT (mesuré au
                # premier passage du banc). Un webhook mort rend 401/404.
                requete = Request(webhook, headers={
                    "User-Agent": "AscensionFR-BancSante/1.0"})
                with urlopen(requete, timeout=10) as r:
                    if r.status == 200:
                        dire("  ok     webhook des rapports : vivant")
                    else:
                        dire("  ROUGE  webhook : HTTP %d" % r.status)
                        rouges.append("webhook")
            except Exception as e:
                code_http = getattr(e, "code", None)
                if code_http in (401, 403, 404):
                    dire("  ROUGE  webhook : HTTP %d — il est MORT, la "
                         "collecte des joueurs n'arrive plus" % code_http)
                    rouges.append("webhook")
                else:
                    avertissements.append("webhook injoignable (%s)" % e)
                    dire("  avert. webhook injoignable (réseau ?) : %s" % e)

    # 5. fraîcheur de la veille Discord
    plus_recent = 0
    if os.path.isdir(VEILLE):
        for nom in os.listdir(VEILLE):
            chemin = os.path.join(VEILLE, nom)
            if os.path.isfile(chemin):
                plus_recent = max(plus_recent, os.path.getmtime(chemin))
    if not plus_recent:
        avertissements.append("veille Discord : dossier vide/absent")
        dire("  avert. veille Discord : dossier vide ou absent")
    else:
        age_h = (time.time() - plus_recent) / 3600.0
        if age_h > 78:
            dire("  ROUGE  veille Discord : silencieuse depuis %.0f h — "
                  "la tâche de 18 h 45 est morte ?" % age_h)
            rouges.append("veille")
        elif age_h > 30:
            avertissements.append("veille en retard (%.0f h)" % age_h)
            dire("  avert. veille Discord : %.0f h sans nouveauté" % age_h)
        else:
            dire("  ok     veille Discord : fraîche (%.0f h)" % age_h)

    # 5 bis. la collecte de BOUT EN BOUT (bloc E) : le GET dit que le
    # webhook EXISTE ; ceci dit que des rapports ARRIVENT vraiment. La
    # cadence dépend des joueurs — avertissement seulement, jamais rouge.
    dossier_rapports = os.path.join(BASE, "rapports")
    dernier_rapport = 0
    if os.path.isdir(dossier_rapports):
        for nom in os.listdir(dossier_rapports):
            if nom.endswith(".txt") and not nom.startswith("ids_"):
                chemin = os.path.join(dossier_rapports, nom)
                if os.path.isfile(chemin):
                    dernier_rapport = max(dernier_rapport,
                                          os.path.getmtime(chemin))
    if dernier_rapport:
        age_j = (time.time() - dernier_rapport) / 86400.0
        if age_j > 7:
            avertissements.append("aucun rapport joueur depuis %.0f j"
                                  % age_j)
            dire("  avert. collecte : aucun rapport joueur depuis %.0f "
                 "jours — webhook, bot ou joueurs ?" % age_j)
        else:
            dire("  ok     collecte : dernier rapport joueur il y a "
                 "%.1f j" % age_j)

    # 6. le dernier passage de l'Atelier (écrit par le compagnon — bloc E)
    if os.path.exists(ATELIER_SANTE):
        try:
            sante = json.load(io.open(ATELIER_SANTE, encoding="utf-8"))
            etapes = sante.get("etapes", {})
            en_echec = {k: v for k, v in etapes.items() if v != 0}
            # LE VERT QUI MENT (programme 31, bloc F) : les codes ne
            # suffisent plus — une étape à code 0 qui avait du travail et
            # n'a RIEN traduit est un mensonge. Même règle que le bandeau
            # de l'Atelier (sante_atelier.verdict), appliquée aux comptes
            # que la santé porte désormais.
            import sante_atelier as _sa
            menteurs = []
            bilans = sante.get("bilans") or {}
            # On parcourt les ÉTAPES, pas les bilans : une étape
            # instrumentée dont le bilan MANQUE doit crier aussi
            # (programme 32, bloc C — la porte de service du 31).
            for script, code_etape in etapes.items():
                couleur, raison = _sa.verdict(code_etape,
                                              bilans.get(script), script)
                if couleur != _sa.VERT:
                    menteurs.append("%s : %s" % (script, raison))
            if en_echec:
                dire("  ROUGE  Atelier (dernier passage %s) : étape(s) en "
                      "échec : %s" % (sante.get("date", "?"),
                                      ", ".join(sorted(en_echec))))
                rouges.append("atelier")
            elif menteurs:
                dire("  ROUGE  Atelier (dernier passage %s) : code 0 mais "
                      "les COMPTES disent non — %s"
                      % (sante.get("date", "?"), " ; ".join(menteurs)))
                rouges.append("atelier (comptes)")
            else:
                dire("  ok     Atelier : %d étape(s), codes ET comptes "
                      "bons (%s)" % (len(etapes), sante.get("date", "?")))
        except (ValueError, OSError):
            avertissements.append("atelier_sante.json illisible")
            dire("  avert. atelier_sante.json illisible")
    else:
        avertissements.append("atelier_sante.json jamais écrit")
        dire("  avert. Atelier : aucun passage journalisé encore "
              "(atelier_sante.json)")

    dire("=" * 60)
    dire("%d ROUGE(S), %d avertissement(s) — %.0f s"
         % (len(rouges), len(avertissements), time.time() - t0))
    for r in rouges:
        dire("  ROUGE : %s" % r)

    # Le relevé sur disque fait foi — c'est lui que l'horloge écrit et
    # que Dan (ou le prochain banc) peut relire, pythonw n'ayant pas de
    # console.
    os.makedirs(os.path.dirname(RELEVE), exist_ok=True)
    with io.open(RELEVE, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(_lignes) + "\n")
    return 1 if rouges else 0


if __name__ == "__main__":
    sys.exit(main())
