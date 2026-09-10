# -*- coding: utf-8 -*-
"""
Contrôle complet de l'addon avant un test en jeu ou une publication.

Vérifie trois choses, dans l'ordre de gravité :
  1. la SYNTAXE Lua de chaque fichier (une erreur = addon mort au chargement) ;
  2. les JETONS de protection oubliés — « [0] », « [12] » — qui trahissent une
     traduction abîmée et s'afficheraient tels quels au joueur ;
  3. quelques mesures pour repérer un fichier vide ou anormalement petit.

Usage : python outils/verifier_tout.py
"""
import glob
import io
import os
import re
import sys

ADDON = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
         r"\AscensionFR")

# Un « [0] » resté dans le texte français trahit une traduction abîmée. MAIS
# le jeu a sa propre syntaxe à crochets — « $?s118174[6][5] » veut dire « si
# le sort 118174 est connu, 6, sinon 5 ». On retire donc d'abord tous les
# codes légitimes en s'appuyant sur la liste FAISANT AUTORITÉ (celle du
# traducteur), et on ne signale que ce qui reste.
RACINE_PROJET = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE_PROJET)
from traducteur_fr import MOTIFS_PROTEGES  # noqa: E402

TEXTE = re.compile(r'="((?:[^"\\]|\\.)*)"')
JETON_OUBLIE = re.compile(r"\[\d{1,2}\]")


def fichiers_lua():
    return (sorted(glob.glob(os.path.join(ADDON, "DB", "*.lua")))
            + sorted(glob.glob(os.path.join(ADDON, "Modules", "*.lua")))
            + sorted(glob.glob(os.path.join(ADDON, "*.lua"))))


def verifier_syntaxe(chemins):
    """-> (fautes, constantes par fichier).

    IMPÉRATIVEMENT lua51 : le client de WoW 3.3.5a tourne en Lua 5.1. Le lupa
    par défaut est en Lua 5.5, qui a d'autres règles — il refusait « for seg
    in ... do seg = ... end » (interdit depuis 5.4, légal en 5.1) et signalait
    donc en faute deux fichiers parfaitement valides. Un banc qui crie au loup
    finit par ne plus être lu ; et, dans l'autre sens, une grammaire plus
    récente peut accepter ce que 5.1 refuserait.

    La même compilation sert à relever le nombre de CONSTANTES du fichier
    (25/07/2026, voir outils/mesurer_constantes.py) : c'est ce compteur-là,
    et pas la taille du fichier, qui décide si le client acceptera la base.
    """
    import mesurer_constantes
    fautes, constantes = [], {}
    for chemin in chemins:
        nom = os.path.basename(chemin)
        compile_ok, k, message = mesurer_constantes.mesurer_fichier(chemin)
        if not compile_ok:
            fautes.append((nom, message[:120]))
        else:
            constantes[nom] = k
    return fautes, constantes


def verifier_jetons(chemins):
    suspects = []
    for chemin in chemins:
        if "\\DB\\" not in chemin:
            continue
        for numero, ligne in enumerate(io.open(chemin, encoding="utf-8"), 1):
            for texte in TEXTE.findall(ligne):
                nu = MOTIFS_PROTEGES.sub("", texte)   # on ôte les vrais codes
                if JETON_OUBLIE.search(nu):
                    suspects.append((os.path.basename(chemin), numero,
                                     texte[:90]))
                    break
    return suspects


def main():
    chemins = fichiers_lua()
    print("=== 1. Syntaxe Lua (%d fichiers) ===" % len(chemins))
    fautes, constantes = verifier_syntaxe(chemins)
    if fautes:
        for nom, erreur in fautes:
            print("  ÉCHEC  %s : %s" % (nom, erreur))
    else:
        print("  OK — tous les fichiers se chargent.")

    print()
    print("=== 2. Jetons de protection oubliés ===")
    suspects = verifier_jetons(chemins)
    if suspects:
        for nom, numero, extrait in suspects[:15]:
            print("  %s:%d  %s" % (nom, numero, extrait))
        print("  (%d au total)" % len(suspects))
    else:
        print("  OK — aucun « [0] » resté dans le texte français.")

    print()
    print("=== 2 bis. Webhook du Compagnon ===")
    # CE CONTRÔLE CRIAIT SANS BLOQUER (mesuré au programme 14, 01/08/2026).
    # Les deux refus ci-dessous s'affichaient en toutes lettres — « le
    # Compagnon n'enverra RIEN », « ne jamais publier ça ! » — et le code
    # retour restait 0 : la panne du 19/07 serait repassée à l'identique.
    # Ce qui BLOQUE, et pourquoi c'est cette liste-là :
    #   - webhook vide côté privé -> l'exe part muet ;
    #   - webhook renseigné côté public -> le secret part sur GitHub ;
    #   - 401 -> le serveur RÉPOND que le jeton est mort (c'est un fait, pas
    #     un aléa de réseau) ;
    #   - fichier introuvable -> le contrôle n'a rien mesuré du tout.
    # Ce qui n'est qu'un AVERTISSEMENT : les autres échecs d'interrogation.
    # Un délai d'attente ou une coupure de wifi ne dit rien du webhook, et
    # un garde-fou qui rougit pour une panne de réseau finit désactivé.
    probleme_webhook = []
    # Panne silencieuse vécue le 19/07/2026 : le webhook avait disparu de la
    # source locale — l'exe partait muet, sans un mot. Et DEPUIS LE
    # PROGRAMME 33, la valeur n'est PLUS dans le code : compagnon.py lit
    # ASCENSIONFR_WEBHOOK puis assets/webhook.local.txt (injecté au build,
    # gitignoré). Ce contrôle suit donc la MÊME résolution que
    # _lire_webhook() — l'ancienne version cherchait l'affectation disparue
    # et rougissait pour toujours (attrapé au programme 34 : elle aurait
    # bloqué tous les builds à venir).
    valeur_webhook = os.environ.get("ASCENSIONFR_WEBHOOK", "").strip()
    source_webhook = "variable ASCENSIONFR_WEBHOOK"
    if not valeur_webhook:
        source_webhook = "compagnon/assets/webhook.local.txt"
        try:
            valeur_webhook = io.open(
                os.path.join(RACINE_PROJET, "compagnon", "assets",
                             "webhook.local.txt"),
                encoding="utf-8").read().strip()
        except (OSError, IOError):
            valeur_webhook = ""
    if not valeur_webhook:
        print("  source locale : AUCUN webhook (ni variable, ni fichier "
              "injecté) — l'exe partirait MUET.")
        print("      Injecte-le : outils/injecter_webhook.py")
        probleme_webhook.append("webhook absent des deux sources")
    else:
        print("  source locale : renseignée (%s)" % source_webhook)
        # Présent ne veut pas dire valide : le 19/07/2026, un webhook périmé
        # (jeton régénéré depuis) faisait accuser le réseau. On INTERROGE le
        # webhook — simple lecture, aucun message posté.
        print("      test de validité...", end=" ")
        try:
            import json
            import urllib.request
            requete = urllib.request.Request(
                valeur_webhook, headers={"User-Agent": "AscensionFR"})
            with urllib.request.urlopen(requete, timeout=15) as reponse:
                salon = json.load(reponse).get("channel_id")
            print("VALIDE (salon %s)" % salon)
        except Exception as erreur:
            code = getattr(erreur, "code", "")
            print("ÉCHEC %s — le Compagnon ne pourra rien envoyer." % code)
            if code in (401, 404):
                print("      Jeton mort (le serveur RÉPOND %s) : régénère "
                      "le webhook Discord puis outils/injecter_webhook.py."
                      % code)
                probleme_webhook.append("jeton refusé (%s)" % code)
            else:
                print("      (avertissement seulement : une coupure de "
                      "réseau ne prouve rien sur le webhook)")
    # La copie publiée ne doit porter AUCUNE valeur : ni un fichier injecté
    # oublié dans l'arbre public, ni une URL en dur (le balayage de motifs
    # reste le filet principal — ceci est le contrôle de proximité).
    fuite = os.path.join(RACINE_PROJET, "depot_github", "compagnon",
                         "assets", "webhook.local.txt")
    chemin_pub = os.path.join(RACINE_PROJET, "depot_github", "compagnon",
                              "compagnon.py")
    if os.path.exists(fuite):
        print("  copie publiée : un webhook.local.txt traîne dans l'arbre "
              "public — ne jamais publier ça !")
        probleme_webhook.append("webhook.local.txt dans l'arbre public")
    elif not os.path.exists(chemin_pub):
        print("  copie publiée : fichier introuvable !")
        probleme_webhook.append("copie publiée introuvable")
    elif re.search(r"discord(?:app)?\.com/api(?:/v\d+)?/webhooks/\d+",
                   io.open(chemin_pub, encoding="utf-8").read()):
        print("  copie publiée : une URL de webhook EN DUR — ne jamais "
              "publier ça !")
        probleme_webhook.append("webhook en dur dans la copie publiée")
    else:
        print("  copie publiée : OK (aucune valeur)")

    print()
    print("=== 3. Taille des bases, et marge avant la limite de Lua ===")
    # La TAILLE ne dit rien : DB_Objets fait 26 Mo et se compile en 0,1 s,
    # quand le même contenu à plat ne se compile pas du tout. Ce qui compte
    # est le nombre de CONSTANTES (chaînes et nombres DISTINCTS) : Lua 5.1
    # en refuse plus de 262 143 par fonction, et un fichier au-delà ne se
    # charge simplement pas. DB_Objets s'y est cogné le 25/07/2026.
    import mesurer_constantes
    # DEUX LISTES, ET C'EST VOLONTAIRE (programme 14, 01/08/2026). Elles
    # étaient confondues dans une seule, absente du `return` : « UN SEAU NE
    # COMPILE PAS » s'affichait avec un code retour 0.
    #   casses_seaux -> le seau ne se charge PAS en jeu. Core.lua avale
    #     l'échec et les textes restent anglais toute la session, sans un
    #     mot. C'est une base morte : ça BLOQUE.
    #   serrees      -> la base APPROCHE la limite (≥ 80 %). Elle fonctionne
    #     encore. En faire un refus arrêterait la chaîne pour une base
    #     parfaitement valide : ça reste un AVERTISSEMENT, bien visible.
    total, serrees, casses_seaux = 0, [], []
    for chemin in chemins:
        if "\\DB\\" not in chemin:
            continue
        nom = os.path.basename(chemin)
        taille = os.path.getsize(chemin)
        total += taille
        lignes = sum(1 for _ in io.open(chemin, encoding="utf-8"))
        alerte = "  <-- VIDE ?" if taille < 200 else ""
        k = constantes.get(nom)
        # Sur une base PARESSEUSE, le fichier ne coûte presque rien : ce sont
        # les SEAUX, recompilés un par un en jeu par loadstring, qui portent
        # le vrai risque. Afficher le chiffre du fichier (0,1 %) donnerait une
        # fausse tranquillité — DB_ObjetsNoms est en réalité à 33 %.
        n_seaux, pire, casses = mesurer_constantes.mesurer_seaux(chemin)
        if casses:
            alerte = "  <-- UN SEAU NE COMPILE PAS" + alerte
            casses_seaux.append((nom, casses[0]))
        elif n_seaux:
            k = pire
        if k is None:
            part = "     ?"
        else:
            ratio = float(k) / mesurer_constantes.LIMITE
            part = "%5.1f%%" % (100 * ratio)
            if ratio >= mesurer_constantes.SEUIL_ALERTE:
                serrees.append((nom, k))
                alerte = "  <-- À DÉCOUPER PLUS FIN" + alerte
        print("  %-28s %7.1f Ko  %6d lignes  %s de la limite Lua%s%s"
              % (nom, taille / 1024.0, lignes, part,
                 "  (pire de %d seaux)" % n_seaux if n_seaux else "", alerte))
    print("  %-28s %7.1f Mo" % ("TOTAL", total / 1048576.0))
    if serrees:
        print("  %d base(s) à plus de %.0f %% des %d constantes de Lua 5.1 :"
              % (len(serrees), 100 * mesurer_constantes.SEUIL_ALERTE,
                 mesurer_constantes.LIMITE))
        for nom, k in serrees:
            print("    %-26s %d constantes — passe-la en paresseux "
                  "(outils/optimiser_memoire.py)." % (nom, k))
    if casses_seaux:
        print("  🛑 %d base(s) dont un SEAU NE COMPILE PAS — en jeu, ces "
              "textes resteraient anglais toute la session, en silence :"
              % len(casses_seaux))
        for nom, message in casses_seaux:
            print("    %-26s %s" % (nom, message))

    print()
    toc = io.open(os.path.join(ADDON, "AscensionFR.toc"),
                  encoding="utf-8").read()
    version = re.search(r"##\s*Version:\s*([\d.]+)", toc)
    manquants = [f for f in re.findall(r"^([A-Za-z].*\.lua)\s*$", toc, re.M)
                 if not os.path.isfile(os.path.join(ADDON,
                                                    f.replace("\\", os.sep)))]
    print("Version de l'addon : %s" % (version.group(1) if version else "?"))
    print("Fichiers annoncés dans le .toc mais absents : %s"
          % (manquants or "aucun"))

    # DOCTRINE DE VERSION (Dan, 28/07/2026) : une mise à jour = UN numéro.
    # VERSION_COMPAGNON doit être ÉGAL au « ## Version: » du .toc vivant, en
    # PERMANENCE — pas seulement au moment de publier. C'est la dissociation
    # (Hub 3.3.1 sur addon 3.3.0) qui a mis tous les utilisateurs du Hub dans
    # une boucle de mise à jour infinie du 25 au 28/07. Contrôle qui MORD :
    # un écart met le banc en échec, donc bloque construire_zip_release.
    version_hub = None
    m = re.search(r'VERSION_COMPAGNON\s*=\s*"([^"]+)"',
                  io.open(os.path.join(RACINE_PROJET, "compagnon",
                                       "compagnon.py"),
                          encoding="utf-8").read())
    if m:
        version_hub = m.group(1)
    version_toc = version.group(1) if version else None
    desaccord_version = (version_hub != version_toc)
    if desaccord_version:
        print("ÉCART DE VERSION : .toc = %s, VERSION_COMPAGNON = %s — "
              "doctrine « un seul numéro » violée, rien ne doit être emballé "
              "ni publié en l'état." % (version_toc, version_hub))
    else:
        print("Doctrine de version : .toc = VERSION_COMPAGNON = %s — OK"
              % version_toc)

    # BASES ORPHELINES (bloc E, 29/07/2026). L'audit a trouvé 9 bases que
    # AUCUN chemin ne régénérait — dont DB_LuesClient, l'anti-taint. La
    # carte vit dans mise_a_jour.REGENERATEURS ; toute base du .toc qui
    # n'y figure pas est une orpheline NOUVELLE : le banc MORD, pour que
    # la carte suive la vie du dépôt.
    import mise_a_jour
    bases_toc = {f.split("\\")[-1]
                 for f in re.findall(r"^DB\\(.*\.lua)\s*$", toc, re.M)}
    orphelines = sorted(bases_toc - set(mise_a_jour.REGENERATEURS))
    fantomes = sorted(set(mise_a_jour.REGENERATEURS) - bases_toc)
    if orphelines:
        print("BASES ORPHELINES (aucun régénérateur déclaré) : %s"
              % ", ".join(orphelines))
    if fantomes:
        print("Carte des régénérateurs : entrées sans base au .toc : %s"
              % ", ".join(fantomes))
    if not orphelines and not fantomes:
        print("Carte des régénérateurs : %d bases, toutes couvertes — OK"
              % len(bases_toc))

    return 1 if (fautes or suspects or manquants or desaccord_version
                 or orphelines or fantomes
                 or casses_seaux or probleme_webhook) else 0


if __name__ == "__main__":
    sys.exit(main())
