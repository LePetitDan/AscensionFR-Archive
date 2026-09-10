# -*- coding: utf-8 -*-
"""
traduire_dragonui.py — traduit en français les addons TIERS qui utilisent
AceLocale-3.0. DragonUI est le premier cas ; en ajouter un autre = une ligne
dans APPS.

POURQUOI CET OUTIL EXISTE
-------------------------
Ces addons ont un `Locales/frFR.lua`, mais AceLocale ne le charge QUE si le
client est en français :

    if locale ~= gameLocale and not isDefault then return end

Le client d'Ascension est anglais. Ce fichier ne sera donc JAMAIS lu, quel que
soit son contenu : traduire l'addon « chez lui » n'a aucun effet.

La solution : notre addon écrit le français dans sa table VIVANTE au
chargement (Modules/AddonsTiers.lua). Aucun de ses fichiers n'est modifié,
donc ses mises à jour n'effacent rien.

LE GARDE-FOU
------------
Un « %s » perdu par le traducteur = erreur Lua chez le joueur. On compare donc
les codes de format AVANT et APRÈS : au moindre écart la traduction est
refusée et l'anglais conservé. Mieux vaut une ligne anglaise qu'un plantage.

LE CACHE
--------
Plus de mille textes : tout est enregistré au fil de l'eau dans
`traduction/dragonui/cache.json`. Une relance ne retraduit que le nouveau.

Usage : python outils/traduire_dragonui.py [--dry]
"""
import io
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from traduire_gisement import traduire  # noqa: E402

JEU = r"D:\AscensionFR\WOW_Priv\resources\ascension-live"
ADDONS = os.path.join(JEU, "Interface", "AddOns")
SORTIE_DB = os.path.join(ADDONS, "AscensionFR", "DB", "DB_AddonsTiers.lua")
DOSSIER = os.path.join(BASE, "dragonui")
CACHE = os.path.join(DOSSIER, "cache.json")

# (application AceLocale, dossier de l'addon qui porte les Locales)
APPS = [
    ("DragonUI", "DragonUI"),
    ("DragonUI_Options", "DragonUI_Options"),
]

# L["clé"] = valeur      (valeur = true -> le texte affiché EST la clé)
RE_CLE = re.compile(r'^\s*L\[\s*"((?:\\.|[^"\\])*)"\s*\]\s*=\s*(.*?),?\s*$')

# Tout ce qui doit traverser la traduction SANS être touché.
RE_CODES = re.compile(
    r"%%"                                        # %% littéral
    r"|%[-+ #]?[0-9]*\.?[0-9]*[sdifxXqcueEgG]"   # %s %d %.1f %02d …
    r"|\|c[0-9a-fA-F]{8}|\|r|\|T[^|]*\|t|\|n"    # couleurs, icônes
    # Choix d'une commande — « red|green|reset|info ». Ce sont des mots que le
    # joueur doit TAPER : les traduire donnerait une consigne fausse.
    r"|\b[a-zA-Z_]+(?:\|[a-zA-Z_]+)+\b"
    r"|<[a-zA-Z_0-9]+>|\[[a-zA-Z_0-9]+\]"        # <bottom_px>, [right_px]
    # Commandes : le slash ne doit PAS suivre une lettre, sinon « online/
    # offline » ou « red/yellow/green » sont pris pour des commandes et
    # ressortent en anglais au milieu d'une phrase française.
    r"|(?<![a-zA-Z])/[a-zA-Z]+"
    r"|DragonUI"                                 # le nom de l'addon
)
# Codes de format seuls : c'est EUX qui font planter Lua s'ils disparaissent.
RE_FORMAT = re.compile(r"%%|%[-+ #]?[0-9]*\.?[0-9]*[sdifxXqcueEgG]")
JETON = "¤%d¤"
RE_JETON = re.compile(r"¤\s*(\d+)\s*¤")

# Écrites à la main : ce sont celles que le garde-fou refuse (le traducteur
# perd un %s ou un %d dessus) ou que la machine rend mal. Elles passent quand
# même par le garde-fou — si je me trompe en les tapant, il le dira.
MANUEL = {
    "%s any bag slot (item or empty) to lock or unlock it.":
        "%s un emplacement de sac (occupé ou vide) pour le verrouiller ou "
        "le déverrouiller.",
    "DragonUI Version: ": "Version de DragonUI : ",
    "HIDDEN: %d. %s [%s]": "MASQUÉ : %d. %s [%s]",
    "SHOWN: %d. %s [%s]": "AFFICHÉ : %d. %s [%s]",
    "SexyMap visuals with DragonUI editor and positioning.":
        "Visuels SexyMap, avec l'éditeur et le positionnement de DragonUI.",
    "Slot locked (bag %d, slot %d).":
        "Emplacement verrouillé (sac %d, emplacement %d).",
    "Slot unlocked (bag %d, slot %d).":
        "Emplacement déverrouillé (sac %d, emplacement %d).",
    "Targeting: %s": "Cible : %s",
    "Total elements: %d": "Nombre d'éléments : %d",
    "Use DragonUI": "Utiliser DragonUI",
    "XP: %d/%d": "XP : %d/%d",
    # La machine rendait « Focus » par « Focalisation » et cassait l'ordre
    # des mots ; dans WoW en français le cadre s'appelle « focalisation ».
    "Focus Frame": "Cadre de focalisation",
    "Vehicle Exit": "Quitter le véhicule",
    # Commandes SANS tiret d'aide : la règle automatique ne ramasse alors que
    # le nom de la commande, et « edit » ou « shadowcolor » — que le joueur
    # doit taper — seraient traduits. Écrites à la main.
    "Use /dragonui edit to enter edit mode, then right-click frames to reset.":
        "Tapez /dragonui edit pour passer en mode édition, puis clic droit "
        "sur un cadre pour le réinitialiser.",
    "Usage: /dui shadowcolor red|green|reset|info":
        "Utilisation : /dui shadowcolor red|green|reset|info",
    "Usage: /dui shadowcrop <bottom_px> [right_px]":
        "Utilisation : /dui shadowcrop <bottom_px> [right_px]",
}


def lire_locale(dossier_addon, fichier):
    """{clé anglaise: texte}. `true` signifie « le texte est la clé »."""
    entrees, ignorees = {}, 0
    chemin = os.path.join(ADDONS, dossier_addon, "Locales", fichier)
    if not os.path.exists(chemin):
        return entrees, ignorees
    with io.open(chemin, encoding="utf-8", errors="replace") as f:
        for ligne in f:
            m = RE_CLE.match(ligne)
            if not m:
                continue
            cle, val = m.group(1), m.group(2).strip()
            if val == "true":
                entrees[cle] = cle
            elif len(val) >= 2 and val[0] == '"' and val[-1] == '"':
                entrees[cle] = val[1:-1]
            else:
                ignorees += 1
    return entrees, ignorees


# Mots anglais courants : ils marquent la fin de la commande et le début de la
# phrase. « /dragonui edit TO enter edit mode » -> on s'arrête avant « to ».
ARRET = {"to", "and", "or", "then", "the", "a", "in", "on", "for", "with",
         "from", "of", "is", "are", "will", "can", "show", "toggle", "open"}
RE_CMD = re.compile(r"(?<![a-zA-Z])/[a-zA-Z]+")
RE_ARG = re.compile(r"[A-Za-z0-9_<>\[\]|.]+")


def proteger(texte):
    """Sort du texte tout ce qui ne doit PAS être traduit.

    Cas délicat : les lignes d'aide. Dans « /dui shadowcrop reset - restore
    full texture », « shadowcrop » et « reset » sont des mots que le joueur
    doit TAPER. Traduits, la consigne devient fausse. On protège donc la
    commande ET ses arguments, en s'arrêtant au premier mot anglais courant
    (voir ARRET) ou à la ponctuation."""
    morceaux = []

    def prendre(s):
        morceaux.append(s)
        return JETON % (len(morceaux) - 1)

    # 1) Les commandes, avec leurs arguments.
    sortie, position = [], 0
    for m in RE_CMD.finditer(texte):
        if m.start() < position:
            continue
        sortie.append(texte[position:m.start()])
        fin = m.end()
        # Les arguments ne se ramassent que sur une ligne d'AIDE, c'est-à-dire
        # « /commande args - explication ». Sans ce tiret on ne prend que la
        # commande : sinon « /reload because its hooks » serait protégé en
        # bloc et cette prose ressortirait en anglais.
        tiret = texte.find(" - ", fin)
        pris = 0
        while tiret > 0 and pris < 3:
            suite = RE_ARG.match(texte, fin + 1) if fin < len(texte) \
                and texte[fin] == " " else None
            if not suite or suite.end() > tiret:
                break
            if suite.group(0).lower() in ARRET:
                break
            fin = suite.end()
            pris += 1
        sortie.append(prendre(texte[m.start():fin]))
        position = fin
    sortie.append(texte[position:])
    reste = "".join(sortie)

    # 2) Les codes de format, couleurs et placeholders.
    return RE_CODES.sub(lambda m: prendre(m.group(0)), reste), morceaux


def restaurer(texte, morceaux):
    def rempl(m):
        i = int(m.group(1))
        return morceaux[i] if i < len(morceaux) else m.group(0)

    return RE_JETON.sub(rempl, texte)


def sur(anglais, francais):
    """La traduction est-elle sûre à livrer ?"""
    if not francais or francais == anglais:
        return False
    if "¤" in francais:                  # jeton recollé par le traducteur
        return False
    return sorted(RE_FORMAT.findall(anglais)) == sorted(
        RE_FORMAT.findall(francais))


def echapper(s):
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return s.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")


def charger_cache():
    if os.path.exists(CACHE):
        with io.open(CACHE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def sauver_cache(cache):
    os.makedirs(DOSSIER, exist_ok=True)
    with io.open(CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1, sort_keys=True)


def main():
    dry = "--dry" in sys.argv
    cache = charger_cache()
    tout, refs = {}, {}

    for app, dossier in APPS:
        reference, ign = lire_locale(dossier, "enUS.lua")
        if not reference:
            print("%s : introuvable ou vide — ignoré." % app)
            continue
        refs[app] = reference
        communaute, _ = lire_locale(dossier, "frFR.lua")
        deja = cache.setdefault(app, {})

        # Les traductions de SA communauté priment : elles sont humaines.
        francais = {c: t for c, t in communaute.items()
                    if c in reference and t != c}
        francais.update({c: t for c, t in deja.items() if c in reference})

        a_faire = [c for c in sorted(reference) if c not in francais]
        print("=== %s : %d textes (%d non lus) | déjà en français : %d | "
              "à traduire : %d" % (app, len(reference), ign, len(francais),
                                   len(a_faire)))

        refuses = []
        for i, cle in enumerate(a_faire, 1):
            source = reference[cle]
            if source in MANUEL:
                main = MANUEL[source]
                if not sur(source, main):
                    print("  !! MA traduction manuelle est fautive : %s"
                          % source[:60])
                    refuses.append(cle)
                    continue
                francais[cle] = main
                deja[cle] = main
                print("  %-44s -> %s   [main]" % (source[:44], main[:44]))
                continue
            # Les espaces de début servent à l'alignement des lignes d'aide ;
            # le traducteur les mange. On les met de côté et on les remet.
            gauche = source[:len(source) - len(source.lstrip())]
            droite = source[len(source.rstrip()):]
            protege, morceaux = proteger(source.strip())
            brut = traduire(protege)
            fr = None
            if brut:
                fr = gauche + restaurer(brut, morceaux).strip() + droite
            if not sur(source, fr):
                refuses.append(cle)
                continue
            francais[cle] = fr
            deja[cle] = fr
            print("  %-44s -> %s" % (source[:44], fr[:44]))
            if not dry and i % 25 == 0:
                sauver_cache(cache)          # on ne reperd jamais le travail

        if not dry:
            sauver_cache(cache)
        print("  -> en français : %d | refusés (anglais gardé) : %d"
              % (len(francais), len(refuses)))
        for c in refuses[:12]:
            print("       refusé : %s" % c[:70])
        tout[app] = francais
        print()

    if dry:
        print("--dry : rien écrit.")
        return 0

    # 1) la base lue par Modules/AddonsTiers.lua
    lignes = ["-- Fichier généré par outils/traduire_dragonui.py "
              "- NE PAS ÉDITER.",
              "-- Traductions d'addons TIERS, rangées par application "
              "AceLocale.",
              "local DB = AscensionFR.DB.AddonsTiers"]
    total = 0
    for app in sorted(tout):
        lignes.append("")
        lignes.append('DB["%s"] = {}' % echapper(app))
        lignes.append('local T = DB["%s"]' % echapper(app))
        for cle in sorted(tout[app]):
            lignes.append('T["%s"]="%s"' % (echapper(cle),
                                            echapper(tout[app][cle])))
            total += 1
    with io.open(SORTIE_DB, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")
    print("écrit : %s — %d textes, %d application(s)"
          % (os.path.basename(SORTIE_DB), total, len(tout)))

    # 2) les fichiers prêts à proposer à l'auteur (licence MIT ; son propre
    #    fichier invite aux contributions). JAMAIS publiés automatiquement.
    os.makedirs(DOSSIER, exist_ok=True)
    for app, _dossier in APPS:
        if app not in tout:
            continue
        pr = ["--[[", " %s - French Locale (frFR)" % app,
              " Community translation — Edit this file to contribute!", "]]",
              "",
              'local L = LibStub("AceLocale-3.0"):NewLocale("%s", "frFR")'
              % app,
              "if not L then return end", ""]
        for cle in sorted(refs[app]):
            if cle in tout[app]:
                pr.append('L["%s"] = "%s"' % (echapper(cle),
                                              echapper(tout[app][cle])))
            else:
                pr.append('L["%s"] = true' % echapper(cle))
        chemin = os.path.join(DOSSIER, "%s_frFR.lua" % app)
        with io.open(chemin, "w", encoding="utf-8") as f:
            f.write("\n".join(pr) + "\n")
        print("écrit : %s (proposition pour l'auteur, non publiée)"
              % os.path.basename(chemin))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
