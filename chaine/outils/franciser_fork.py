# -*- coding: utf-8 -*-
"""
Fabrique un fork français depuis un addon de ProfetGit (MIT, accord reçu).
==========================================================================
Deuxième étape de la chaîne des forks (voir CONTEXTE §3.29) :

    extraire_textes_fork.py  →  correspondances traduites  →  ICI

Le fork est REFABRIQUÉ EN ENTIER à chaque passage depuis l'addon d'origine :
quand ProfetGit publie une mise à jour, on remplace la source, on relance,
et le rapport dit quelles correspondances n'ont plus trouvé leur cible
(phrases changées) — il n'y a jamais de fusion à la main.

Ce que fait la fabrication :
  1. copie l'arborescence complète (sons, textures, client-patch, LICENSE) ;
  2. renomme les IDENTIFIANTS (sauvegarde, commandes /) — jamais en conflit
     avec l'original si les deux sont installés ;
  3. réécrit l'en-tête du .toc (titre, notes, version, sauvegarde) et le
     renomme au nom du fork (règle WoW : dossier = nom du .toc) ;
  4. remplace chaque LITTÉRAL exact de la table de correspondances (les
     plus longs d'abord), en comptant chaque remplacement ;
  5. compile chaque .lua produit (lupa, Lua 5.1) — refus de livrer sinon.

⚠️ On ne touche JAMAIS : clés de détection (noms de sorts en minuscules,
motifs ^stunned), chemins, événements, noms de cadres (interopérabilité),
modèles de PatternFromFormat (ils parsent le chat réel).

Usage : python franciser_fork.py confort [--source D:\\...\\Refactor]
"""
import io
import json
import os
import re
import shutil
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(ICI)
ADDONS = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"

FORKS = {
    "confort": {
        "source": os.path.join(ADDONS, "Refactor"),
        "dossier": "AscensionFR-Confort",
        "correspondances": os.path.join(BASE, "forks",
                                        "confort_correspondances.json"),
        "toc": {
            "Title": "AscensionFR |cffffd100Confort|r",
            "Notes": "Le confort de jeu pour Ascension, en français : "
                     "quêtes accélérées, butin instantané, marchand malin, "
                     "alertes de butin, alerte de contrôle. D'après "
                     "Refactor de ProfetGit (MIT), avec son accord.",
            "Author": "ProfetGit (Refactor) — adaptation française "
                      "LePetitDan",
            "Version": "1.7.0.1",
            "SavedVariables": "AscensionFRConfortDB",
        },
        # Renommages d'identifiants (hors chaînes) : mot entier.
        "identifiants": [
            (r"\bRefactorCompareDB\b", "AscensionFRConfortDB"),
            (r"\bSLASH_REFACTOR(\d)\b", r"SLASH_AFRCONFORT\1"),
            (r"\bSlashCmdList\.REFACTOR\b", "SlashCmdList.AFRCONFORT"),
        ],
        "readme": (
            "# AscensionFR-Confort\n\n"
            "Le confort de jeu pour Ascension, **en français** : quêtes "
            "accélérées, butin instantané, marchand malin, alertes de "
            "butin, alerte de contrôle.\n\n"
            "Adaptation française de "
            "[Refactor](https://github.com/ProfetGit/Refactor-Ascension) "
            "de **ProfetGit** (licence MIT), avec son accord. Merci à "
            "lui !\n\n"
            "- Réglages : `/confort` (ou `/afc`), ou le bouton de "
            "minicarte.\n"
            "- Ne PAS garder l'addon Refactor d'origine en même temps : "
            "tout serait en double. Désactive-le ou remplace-le.\n"
            "- Le choix automatique des récompenses de quête demande "
            "l'addon d'équipement (AscensionFR-Équipement ou Refactor "
            "Gear).\n\n"
            "Fabriqué par la chaîne AscensionFR "
            "(`outils/franciser_fork.py`) — ne pas modifier ces fichiers "
            "à la main, ils sont régénérés à chaque mise à jour.\n"),
    },
    "equipement": {
        "source": os.path.join(ADDONS, "RefactorGear"),
        "dossier": "AscensionFR-Equipement",
        "correspondances": os.path.join(BASE, "forks",
                                        "equipement_correspondances.json"),
        "toc": {
            "Title": "AscensionFR |cffffd100Équipement|r",
            "Notes": "« Cet objet est-il mieux ? » Verdict en % dans "
                     "l'infobulle, flèches vertes dans les sacs, poids par "
                     "spé — en français. D'après Refactor Gear de "
                     "ProfetGit (MIT), avec son accord.",
            "Author": "ProfetGit (Refactor Gear) — adaptation française "
                      "LePetitDan",
            "Version": "1.0.0.1",
            "SavedVariables": "AscensionFREquipementDB",
        },
        # ⚠️ RefactorGearShared et les noms de cadres (RefactorGearScanTip…)
        # restent INCHANGÉS : c'est le pont avec Confort et l'original.
        "identifiants": [
            (r"\bRefactorGearDB\b", "AscensionFREquipementDB"),
            (r"\bSLASH_REFACTORGEAR(\d)\b", r"SLASH_AFREQUIPEMENT\1"),
            (r"\bSlashCmdList\.REFACTORGEAR\b",
             "SlashCmdList.AFREQUIPEMENT"),
        ],
        "readme": (
            "# AscensionFR-Équipement\n\n"
            "« Cet objet est-il mieux ? » Verdict en % dans l'infobulle, "
            "flèches vertes dans les sacs, poids de statistiques par spé "
            "— **en français**, et fidèle aux objets recalculés "
            "d'Ascension (lecture de l'objet vivant, jamais du lien de "
            "base).\n\n"
            "Adaptation française de "
            "[Refactor Gear](https://github.com/ProfetGit/RefactorGear) "
            "de **ProfetGit** (licence MIT), avec son accord. Merci à "
            "lui !\n\n"
            "- Réglages : `/equipement` (ou `/afe`), ou le bouton de "
            "minicarte.\n"
            "- Ne PAS garder l'addon Refactor Gear d'origine en même "
            "temps : tout serait en double. Désactive-le ou remplace-le.\n"
            "- Les noms de spécialisations et quelques mots-clés "
            "(Armor, Cloth…) restent en anglais : l'addon les compare "
            "aux données anglaises du jeu — les traduire le "
            "casserait.\n\n"
            "Fabriqué par la chaîne AscensionFR "
            "(`outils/franciser_fork.py`) — ne pas modifier ces fichiers "
            "à la main, ils sont régénérés à chaque mise à jour.\n"),
    },
}

# Compile (sans jamais exécuter) : loadstring s'arrête à la syntaxe.
CONTROLE_LUA = ("function controle_syntaxe(src) "
                "local f, e = loadstring(src) "
                "if f then return nil else return e end end")


def verifier_lua(chemin):
    """Compile (sans exécuter) un .lua en Lua 5.1 via lupa. Rend None si
    tout va bien, sinon le message d'erreur. Lua 5.1 OBLIGATOIRE : c'est
    la version du jeu, et loadstring n'existe plus dans les Lua récents."""
    import lupa.lua51 as lupa_mod
    lua = lupa_mod.LuaRuntime()
    lua.execute(CONTROLE_LUA)
    with io.open(chemin, encoding="utf-8", errors="replace") as f:
        source = f.read()
    return lua.globals().controle_syntaxe(source)


def franciser_lua(texte, regles, correspondances, compteur):
    for motif, remplacement in regles["identifiants"]:
        texte = re.sub(motif, remplacement, texte)
    # Littéraux exacts, les plus longs d'abord (évite qu'une courte
    # correspondance ne morde dans une longue).
    for en in sorted(correspondances, key=len, reverse=True):
        if en.startswith("__"):
            continue
        fr = correspondances[en]
        if '"' in fr:
            raise SystemExit("guillemet double dans la traduction de %r "
                             "— interdit (elle est réécrite entre "
                             "guillemets doubles)" % en)
        motifs = ['"%s"' % re.escape(en)]
        if "'" not in en and "\\" not in en:
            motifs.append("'%s'" % re.escape(en))
        for motif in motifs:
            texte, n = re.subn(motif, '"%s"' % fr.replace("\\", "\\\\"),
                               texte)
            compteur[en] = compteur.get(en, 0) + n
    return texte


def franciser_toc(texte, regles):
    lignes = []
    for ligne in texte.splitlines():
        m = re.match(r"##\s*(\w+)\s*:", ligne)
        if m and m.group(1) in regles["toc"]:
            lignes.append("## %s: %s" % (m.group(1),
                                         regles["toc"][m.group(1)]))
        else:
            lignes.append(ligne)
    return "\n".join(lignes) + "\n"


def fabriquer(nom_fork, source=None):
    regles = FORKS[nom_fork]
    source = source or regles["source"]
    cible = os.path.join(ADDONS, regles["dossier"])
    with io.open(regles["correspondances"], encoding="utf-8") as f:
        correspondances = json.load(f)

    if os.path.isdir(cible):
        shutil.rmtree(cible)
    compteur = {}
    nom_toc_source = None
    for racine, _dossiers, fichiers in os.walk(source):
        relatif = os.path.relpath(racine, source)
        dest = os.path.join(cible, relatif) if relatif != "." else cible
        os.makedirs(dest, exist_ok=True)
        for fichier in sorted(fichiers):
            chemin = os.path.join(racine, fichier)
            bas = fichier.lower()
            if bas.endswith(".lua"):
                with io.open(chemin, encoding="utf-8",
                             errors="replace") as f:
                    texte = f.read()
                texte = franciser_lua(texte, regles, correspondances,
                                      compteur)
                with io.open(os.path.join(dest, fichier), "w",
                             encoding="utf-8", newline="") as f:
                    f.write(texte)
            elif bas.endswith(".toc") and relatif == ".":
                nom_toc_source = fichier
                with io.open(chemin, encoding="utf-8",
                             errors="replace") as f:
                    texte = franciser_toc(f.read(), regles)
                with io.open(os.path.join(
                        cible, regles["dossier"] + ".toc"), "w",
                        encoding="utf-8", newline="") as f:
                    f.write(texte)
            else:
                shutil.copy2(chemin, os.path.join(dest, fichier))

    if not nom_toc_source:
        raise SystemExit("aucun .toc à la racine de " + source)

    if regles.get("readme"):
        with io.open(os.path.join(cible, "README.md"), "w",
                     encoding="utf-8", newline="") as f:
            f.write(regles["readme"])

    # Bilan des correspondances
    muettes = [en for en in correspondances
               if not en.startswith("__") and not compteur.get(en)]
    gourmandes = {en: n for en, n in compteur.items() if n > 6}
    total = sum(compteur.values())
    print("remplacements : %d (sur %d correspondances)"
          % (total, len(correspondances) - 1))
    if muettes:
        print("\n⚠ %d correspondances SANS CIBLE (phrases changées en "
              "amont ?) :" % len(muettes))
        for en in muettes:
            print("   %r" % en[:70])
    if gourmandes:
        print("\nℹ remplacements nombreux (à vérifier une fois) :")
        for en, n in sorted(gourmandes.items(), key=lambda kv: -kv[1]):
            print("   %2d × %r" % (n, en[:60]))

    # Compilation de chaque .lua produit
    erreurs = 0
    for racine, _dossiers, fichiers in os.walk(cible):
        for fichier in sorted(fichiers):
            if fichier.lower().endswith(".lua"):
                probleme = verifier_lua(os.path.join(racine, fichier))
                if probleme:
                    erreurs += 1
                    print("✗ %s : %s" % (fichier, probleme))
    if erreurs:
        raise SystemExit("%d fichier(s) ne compilent pas — fork NON "
                         "livrable" % erreurs)
    print("\n✓ tous les .lua compilent — %s fabriqué dans\n  %s"
          % (regles["dossier"], cible))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args or args[0] not in FORKS:
        raise SystemExit("usage : franciser_fork.py <%s>"
                         % "|".join(FORKS))
    source = None
    if "--source" in sys.argv:
        source = sys.argv[sys.argv.index("--source") + 1]
    fabriquer(args[0], source)


if __name__ == "__main__":
    main()
