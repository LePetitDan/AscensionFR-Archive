# -*- coding: utf-8 -*-
"""
Génère la liste noire des GlobalStrings à ne jamais traduire, pour éviter les
contaminations (« taint ») qui bloquent les fonctions protégées du jeu.

Mécanisme du problème : une variable globale écrite par un addon devient
contaminée. Si du code de Blizzard la LIT pendant une exécution qui touche un
bouton sécurisé (barre d'action, bouton d'objet de quête...), tout le chemin
devient contaminé et l'appel protégé est refusé — le joueur ne peut plus
utiliser ses sorts.

Cas vécu : WatchFrame.lua (suivi de quêtes) lit QUEST_DASH dans
WatchFrame_SetLine(), la même exécution qui crée les WatchFrameItem
(SecureActionButtonTemplate) -> « AddOn 'AscensionFR' tainted the call of the
secure function 'UseAction()' » et barres d'action bloquées.

Méthode : on extrait tout le FrameXML d'Ascension, on repère les fichiers qui
touchent au code sécurisé, et on interdit toutes les GlobalStrings qu'ils
lisent comme variables.

Usage : python generer_listenoire.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagnostic_gs import charger  # noqa: E402
from diagnostic_taint import code_seul, IDENTIFIANT  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JEU = r"D:\AscensionFR\WOW_Priv\resources\ascension-live"
FRFR = os.path.join(BASE, "sources", "GlobalStrings_frFR.lua")
EXTRACTION = os.path.join(BASE, "sources", "framexml")
ADDON = os.path.join(JEU, "Interface", "AddOns", "AscensionFR")

# Un fichier est « sensible » s'il appelle une fonction protégée...
MARQUEURS_SECURISES = re.compile(
    r"SecureHandler|SecureTemplates|SecureStateDriver"
    r"|UseAction|CastSpell|UseItem|PickupAction|PlaceAction"
    r"|SecureButton_|SecureCmdOptionParse|RegisterUnitWatch")

# ...ou s'il utilise un template qui hérite d'un template sécurisé. C'est le
# cas décisif, et le plus discret : WatchFrame.lua ne mentionne jamais
# « Secure », il crée des « WatchFrameItemButtonTemplate » — et c'est le XML
# qui révèle que ce template descend de SecureActionButtonTemplate.
# Il faut donc résoudre l'héritage déclaré dans les XML, de façon transitive.
INHERITS = re.compile(r'inherits="([^"]+)"')
NOM_TEMPLATE = re.compile(r'name="([^"]+)"[^>]*virtual="true"')
NOM_TEMPLATE2 = re.compile(r'virtual="true"[^>]*name="([^"]+)"')


# Le FrameXML de Blizzard déclare ses fonctions en colonne 0 et les ferme par
# un « end » en colonne 0 : on peut donc les découper sans écrire un vrai
# analyseur Lua.
DEBUT_FONCTION = re.compile(
    r"^function\s+([A-Za-z_][A-Za-z_0-9\.\:]*)\s*\(", re.M)


def decouper_fonctions(source):
    """[(nom, corps)] des fonctions déclarées au premier niveau."""
    resultat = []
    debuts = [(m.start(), m.group(1)) for m in DEBUT_FONCTION.finditer(source)]
    for i, (debut, nom) in enumerate(debuts):
        fin = len(source)
        # La fonction se termine au « end » en colonne 0 qui précède la
        # déclaration suivante (ou la fin du fichier).
        limite = debuts[i + 1][0] if i + 1 < len(debuts) else len(source)
        m = re.search(r"^end\b", source[debut:limite], re.M)
        if m:
            fin = debut + m.end()
        else:
            fin = limite
        resultat.append((nom, source[debut:fin]))
    return resultat


def hors_fonctions(source):
    """Le code exécuté au chargement, hors de toute fonction."""
    morceaux = []
    position = 0
    for nom, corps in decouper_fonctions(source):
        debut = source.find(corps, position)
        if debut == -1:
            continue
        morceaux.append(source[position:debut])
        position = debut + len(corps)
    morceaux.append(source[position:])
    return "\n".join(morceaux)


def templates_securises(fichiers_xml):
    """Noms des templates qui héritent, directement ou non, d'un Secure*."""
    parents = {}
    for source in fichiers_xml.values():
        s = source.decode("utf-8", "ignore")
        # Associe chaque template virtuel à ses parents déclarés
        for bloc in re.finditer(r"<(\w+)([^>]*)>", s):
            attributs = bloc.group(2)
            nom = None
            m = re.search(r'name="([^"]+)"', attributs)
            if m and 'virtual="true"' in attributs:
                nom = m.group(1)
            if not nom:
                continue
            herite = re.search(r'inherits="([^"]+)"', attributs)
            parents[nom] = [x.strip() for x in
                            herite.group(1).split(",")] if herite else []

    securises = set()
    for nom in parents:
        if "Secure" in nom:
            securises.add(nom)

    # Fermeture transitive : un template qui hérite d'un template sécurisé
    # l'est aussi.
    change = True
    while change:
        change = False
        for nom, herites in parents.items():
            if nom in securises:
                continue
            for h in herites:
                if h in securises or "Secure" in h:
                    securises.add(nom)
                    change = True
                    break
    return securises


def cadres_securises(fichiers_xml, templates):
    """Noms des cadres CONCRETS créés depuis un template protégé.

    Indispensable : le Lua ne nomme presque jamais le template. Il écrit
    getglobal("ShapeshiftButton"..i), et c'est le XML qui révèle que
    ShapeshiftButton1..12 héritent de ShapeshiftButtonTemplate, lui-même
    dérivé de SecureFrameTemplate. Sans ce recensement, BonusActionBarFrame.lua
    passait pour inoffensif — et traduire le CANCEL qu'il lit bloquait les
    boutons de posture du joueur.

    On renvoie les noms ET leurs préfixes sans chiffres, pour reconnaître les
    noms construits par concaténation.
    """
    noms = set()
    for source in fichiers_xml.values():
        s = source.decode("utf-8", "ignore")
        for m in re.finditer(r"<\w+([^>]*)>", s):
            attributs = m.group(1)
            if 'virtual="true"' in attributs:
                continue
            nom = re.search(r'name="([^"$]+)"', attributs)
            herite = re.search(r'inherits="([^"]+)"', attributs)
            if not nom or not herite:
                continue
            for t in herite.group(1).split(","):
                if t.strip() in templates:
                    noms.add(nom.group(1))
                    break
    # « ShapeshiftButton1 » -> « ShapeshiftButton » : c'est ce préfixe que le
    # Lua concatène.
    prefixes = set()
    for n in noms:
        p = re.sub(r"\d+$", "", n)
        if len(p) > 6:
            prefixes.add(p)
    return noms | prefixes

# Archives contenant le FrameXML, du moins prioritaire au plus prioritaire.
ARCHIVES = [
    os.path.join(JEU, "Data", "enUS", "locale-enUS.MPQ"),
    os.path.join(JEU, "Data", "enUS", "patch-enUS.MPQ"),
    os.path.join(JEU, "Data", "enUS", "patch-enUS-2.MPQ"),
    os.path.join(JEU, "Data", "enUS", "patch-enUS-3.MPQ"),
    os.path.join(JEU, "Data", "patch-B.MPQ"),
]


def extraire_framexml(extension):
    """Extrait les fichiers d'Interface\\FrameXML (le dernier patch gagne)."""
    from mpyq import MPQArchive
    os.makedirs(EXTRACTION, exist_ok=True)
    fichiers = {}
    for archive in ARCHIVES:
        if not os.path.exists(archive):
            continue
        try:
            a = MPQArchive(archive)
        except Exception:
            continue
        for n in (a.files or []):
            nom = n.decode("utf-8", "ignore") if isinstance(n, bytes) else n
            if (nom.lower().startswith("interface\\framexml\\")
                    and nom.lower().endswith(extension)):
                try:
                    donnees = a.read_file(nom)
                except Exception:
                    donnees = None
                if donnees:
                    fichiers[os.path.basename(nom)] = donnees
    if extension == ".lua":
        for nom, donnees in fichiers.items():
            with open(os.path.join(EXTRACTION, nom), "wb") as f:
                f.write(donnees)
    return fichiers


def main():
    traduites = set(charger(FRFR))
    fichiers = extraire_framexml(".lua")
    xml = extraire_framexml(".xml")
    print("FrameXML analysé : %d fichiers Lua, %d XML" % (len(fichiers), len(xml)))

    securises = templates_securises(xml)
    cadres = cadres_securises(xml, securises)
    print("Templates protégés : %d | cadres et préfixes protégés : %d"
          % (len(securises), len(cadres)))

    # Le Lua désigne le protégé soit par son template, soit — bien plus
    # souvent — par le nom du cadre, éventuellement concaténé.
    reperes = securises | cadres
    motif_templates = re.compile(
        "|".join(re.escape(t) for t in sorted(reperes, key=len, reverse=True))
    ) if reperes else None

    # On raisonne FONCTION par fonction, pas fichier par fichier.
    # Un fichier de 200 Ko comme ChatFrame.lua contient un seul appel protégé
    # (la commande /use) : interdire les 124 chaînes qu'il lit laissait la
    # feuille de personnage à moitié en anglais pour rien.
    fonctions = {}      # nom qualifié -> (fichier, corps)
    for nom, donnees in sorted(fichiers.items()):
        source = donnees.decode("utf-8", "ignore")
        for nom_fn, corps in decouper_fonctions(source):
            fonctions[nom_fn] = (nom, corps)

    print("Fonctions analysées : %d" % len(fonctions))

    # 1. Fonctions qui appellent directement une fonction protégée, ou qui
    #    utilisent un template héritant d'un template sécurisé.
    dangereuses = set()
    for nom_fn, (fichier, corps) in fonctions.items():
        if MARQUEURS_SECURISES.search(corps):
            dangereuses.add(nom_fn)
        elif motif_templates and motif_templates.search(corps):
            dangereuses.add(nom_fn)

    directes = len(dangereuses)

    # 2. Le poison remonte : si G appelle F et que F est dangereuse, une
    #    globale contaminée lue dans G contamine aussi l'exécution qui mène à
    #    l'appel protégé. On propage donc aux appelants, transitivement.
    appels = {n: set(re.findall(r"\b([A-Za-z_][A-Za-z_0-9]*)\s*\(", c))
              for n, (f, c) in fonctions.items()}
    change = True
    while change:
        change = False
        for nom_fn, appeles in appels.items():
            if nom_fn in dangereuses:
                continue
            if appeles & dangereuses:
                dangereuses.add(nom_fn)
                change = True

    print("Fonctions atteignant du code protégé : %d "
          "(%d directement, %d par propagation)"
          % (len(dangereuses), directes, len(dangereuses) - directes))

    # 3. Interdire les globales lues DANS ces fonctions seulement.
    liste_noire = {}
    for nom_fn in dangereuses:
        fichier, corps = fonctions[nom_fn]
        lus = set(IDENTIFIANT.findall(code_seul(corps))) & traduites
        for cle in lus:
            liste_noire.setdefault(cle, []).append(
                "%s (%s)" % (fichier, nom_fn))

    # Le code exécuté au CHARGEMENT (hors fonction) est volontairement ignoré :
    # FrameXML se charge AVANT les addons, donc il lit les chaînes anglaises
    # d'origine — notre traduction n'existe pas encore et ne peut rien
    # contaminer. L'inclure interdisait les 179 chaînes que StaticPopup.lua lit
    # pour construire ses tables, et laissait la feuille de personnage à moitié
    # en anglais sans aucune raison.
    print("GlobalStrings à interdire : %d" % len(liste_noire))
    print()
    for cle in sorted(liste_noire)[:12]:
        print("   %-38s lu par %s" % (cle, ", ".join(liste_noire[cle][:2])))
    if len(liste_noire) > 12:
        print("   ... et %d autres" % (len(liste_noire) - 12))

    # Écriture du fichier Lua de l'addon
    chemin = os.path.join(ADDON, "DB", "DB_ListeNoire.lua")
    lignes = [
        "-- Fichier généré par outils/generer_listenoire.py - NE PAS ÉDITER.",
        "--",
        "-- Ces chaînes d'interface sont lues par du code de Blizzard qui",
        "-- manipule des éléments protégés (barres d'action, boutons d'objets",
        "-- de quête...). Les traduire contamine le chemin d'exécution et le",
        "-- jeu refuse alors les actions du joueur :",
        "--   « AddOn 'AscensionFR' tainted the call of the secure function",
        "--     'UseAction()' » -> barres d'action bloquées.",
        "-- Elles restent donc en anglais, volontairement.",
        "local DB = AscensionFR.DB.ListeNoire",
    ]
    for cle in sorted(liste_noire):
        lignes.append('DB["%s"]=true -- %s' % (cle, liste_noire[cle][0]))
    contenu = "\n".join(lignes) + "\n"
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print()
    print("DB_ListeNoire.lua : %d entrées, %.1f Ko"
          % (len(liste_noire), len(contenu) / 1024.0))


if __name__ == "__main__":
    main()
