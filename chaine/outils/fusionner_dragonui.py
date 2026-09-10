# -*- coding: utf-8 -*-
"""Regenere DB_AddonsTiers.lua pour DragonUI 3.0.8.

TROIS sources, dans cet ordre de priorite :
  1. NOTRE traduction (traduction/dragonui/*_frFR.lua) — vocabulaire deja
     arbitre par Dan, elle prime toujours ;
  2. le francais LIVRE par les auteurs (Locales/frFR.lua de la 3.0.8, MIT) —
     comble les trous sans rien couter ;
  3. les traductions manuelles ci-dessous — les 30 que personne n'avait.

Ne garde QUE les cles presentes dans l'anglais de la 3.0.8 : les cles
disparues en amont sont abandonnees.

GARDE-FOU repris de traduire_dragonui.py : un « %s » perdu = plantage Lua
chez le joueur. On compare les codes de format avant/apres ; au moindre
ecart on garde l'anglais.
"""
import io
import os
import re

NEUF = (r"D:\AscensionFR\WorkFlow\Ajouter par Dan"
        "\\Addon télécharger à traduire")
NOTRE = r"D:\AscensionFR\WorkFlow\dragonui"
SORTIE = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
          r"\AscensionFR\DB\DB_AddonsTiers.lua")

APPS = [("DragonUI", "DragonUI_frFR.lua"),
        ("DragonUI_Options", "DragonUI_Options_frFR.lua")]

# Volontairement NON traduits : nom de l'addon et identifiants techniques.
INTOUCHABLES = {"DragonUI", "bnToast", "DragonUI - D3D9Ex Warning"}

MANUEL = {
    # --- DragonUI -------------------------------------------------------
    "|cff00ff00Drag|r to move this bag":
        "|cff00ff00Glissez|r pour déplacer ce sac",
    "|cff00ff00Left-Click|r to hide this bag's items":
        "|cff00ff00Clic gauche|r pour masquer les objets de ce sac",
    "|cff00ff00Left-Click|r to show this bag's items":
        "|cff00ff00Clic gauche|r pour afficher les objets de ce sac",
    # --- DragonUI_Options : icones d'objectifs de quete ------------------
    "Bag": "Sac",
    "Chest": "Coffre",
    "Choose the icon shown for kill objectives.":
        "Choisissez l'icône affichée pour les objectifs « tuer ».",
    "Choose the icon shown for loot/collect objectives.":
        "Choisissez l'icône affichée pour les objectifs « ramasser ».",
    "Elite Kill Icon": "Icône des élites à tuer",
    "Elite": "Élite",
    # « barre d'info » : le mot déjà employé par notre base pour nameplate.
    # On s'aligne dessus plutôt que d'introduire un second terme.
    "Force one icon on all enemy nameplates so you can position and size it. "
    "Set to Off when done.":
        "Force une icône sur toutes les barres d'info ennemies pour vous "
        "laisser la placer et la dimensionner. Remettez sur « Désactivé » "
        "une fois terminé.",
    "Icon": "Icône",
    "Kill Icon": "Icône « tuer »",
    "Loot Icon": "Icône « ramasser »",
    "Off": "Désactivé",
    "Pointer Icon": "Icône de pointeur",
    "Pointer Mode": "Mode pointeur",
    "Pointer": "Pointeur",
    "Preview Icon": "Icône d'aperçu",
    "Quest Icons": "Icônes de quête",
    "Quest": "Quête",
    "Show Quest Icons": "Afficher les icônes de quête",
    "Show a distinct icon on elite and rare kill objectives.":
        "Affiche une icône distincte sur les objectifs élites et rares "
        "à tuer.",
    "Show a single quest marker on any objective mob instead of separate "
    "kill/loot icons.":
        "Affiche un seul marqueur de quête sur les créatures d'objectif, "
        "au lieu d'icônes « tuer » et « ramasser » séparées.",
    "Show kill/loot icons over your quest-objective mobs. Without "
    "awesome_wotlk, only your target, mouseover and focus show them.":
        "Affiche les icônes « tuer » et « ramasser » au-dessus des créatures "
        "de vos objectifs de quête. Sans awesome_wotlk, seuls votre cible, "
        "la créature survolée et votre focus les affichent.",
    "Size": "Taille",
    "Skull": "Crâne",
    "Sword": "Épée",
    "Test Preview": "Tester l'aperçu",
}

PAIRE = re.compile(r'L\[\s*"((?:\\.|[^"\\])*)"\s*\]\s*=\s*'
                   r'"((?:\\.|[^"\\])*)"')
CLE_TOUTE = re.compile(r'L\[\s*"((?:\\.|[^"\\])*)"\s*\]\s*=')
RE_FORMAT = re.compile(r"%%|%[-+ #]?[0-9]*\.?[0-9]*[sdifxXqcueEgG]")


def lire(chemin):
    if not os.path.exists(chemin):
        return ""
    return io.open(chemin, encoding="utf-8", errors="replace").read()


def delua(s):
    """Deséchappe une chaîne Lua telle qu'écrite dans le fichier source."""
    return (s.replace('\\"', '"').replace("\\n", "\n")
             .replace("\\r", "\r").replace("\\\\", "\\"))


def enlua(s):
    return (s.replace("\\", "\\\\").replace('"', '\\"')
             .replace("\n", "\\n").replace("\r", "\\r"))


def formats_ok(en, fr):
    return sorted(RE_FORMAT.findall(en)) == sorted(RE_FORMAT.findall(fr))


lignes = [
    u"-- Fichier généré par outils/traduire_dragonui.py - NE PAS ÉDITER.",
    u"-- Traductions d'addons TIERS, rangées par application AceLocale.",
    u"--",
    u"-- DragonUI 3.0.8 (NeticSoul, PentSec — licence MIT). Une partie du",
    u"-- français vient du Locales/frFR.lua livré avec l'addon, que son",
    u"-- client anglais ne charge jamais ; le reste est à nous.",
    u"local DB = AscensionFR.DB.AddonsTiers",
    u"",
]

bilan = []
for app, notre_fichier in APPS:
    dossier = os.path.join(NEUF, app, "Locales")
    en_brut = lire(os.path.join(dossier, "enUS.lua"))
    cles = [delua(c) for c in CLE_TOUTE.findall(en_brut)]

    eux = {delua(k): delua(v)
           for k, v in PAIRE.findall(lire(os.path.join(dossier, "frFR.lua")))}
    nous = {delua(k): delua(v)
            for k, v in PAIRE.findall(lire(os.path.join(NOTRE,
                                                        notre_fichier)))}

    lignes.append(u'DB["%s"] = {}' % app)
    lignes.append(u'local T = DB["%s"]' % app)

    pris = {"nous": 0, "eux": 0, "manuel": 0}
    refuses, restants = [], []
    vus = set()
    for cle in cles:
        if cle in vus or cle in INTOUCHABLES:
            continue
        vus.add(cle)
        fr, origine = None, None
        for source, nom in ((nous, "nous"), (eux, "eux"), (MANUEL, "manuel")):
            v = source.get(cle)
            if v and v != cle:
                fr, origine = v, nom
                break
        if fr is None:
            restants.append(cle)
            continue
        if not formats_ok(cle, fr):
            refuses.append(cle)
            continue
        pris[origine] += 1
        lignes.append(u'T["%s"]="%s"' % (enlua(cle), enlua(fr)))
    lignes.append(u"")
    bilan.append((app, len(vus), pris, refuses, restants))

io.open(SORTIE, "w", encoding="utf-8", newline="").write(u"\n".join(lignes))

for app, total, pris, refuses, restants in bilan:
    print("=== %s ===" % app)
    print("  cles traduisibles          : %d" % total)
    print("  depuis NOTRE base          : %d" % pris["nous"])
    print("  depuis leur frFR livre     : %d" % pris["eux"])
    print("  traduites a la main        : %d" % pris["manuel"])
    print("  refusees (codes %%s casses) : %d" % len(refuses))
    for c in refuses[:5]:
        print("      " + c[:80])
    print("  encore en anglais          : %d" % len(restants))
    for c in restants[:5]:
        print("      " + c[:80])
    print("")
print("ecrit -> " + SORTIE)
