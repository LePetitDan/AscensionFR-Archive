# -*- coding: utf-8 -*-
"""
traduire_epreuves.py — traduit les Épreuves d'Ascension (fenêtre « Trials »).

D'OÙ VIENT LE TEXTE
-------------------
Ni des .lua ni des .xml du client : il est dans **Challenge.dbc**, une table
de données (297 épreuves). C'est une leçon générale — le contenu maison
d'Ascension est livré en DONNÉES, pas en code. Chercher seulement dans les
fichiers Lua fait conclure à tort « ça vient du serveur ».

Champs vérifiés sur le fichier réel :
    champ  0 = identifiant
    champ  7 = nom          (« Partner Up! »)
    champ 24 = description  (« Adventure is better together!… »)

COMMENT C'EST AFFICHÉ
---------------------
`Modules/Epreuves.lua` s'accroche aux mixins GLOBAUX de la fenêtre
(ChallengeExtendedInfoMixin:SetTitle / :ShowDescription) et repose le texte
en français. On n'écrit aucune globale : pas de risque de blocage des sorts.
La base est donc indexée par le TEXTE ANGLAIS, pas par l'identifiant — c'est
l'anglais que l'accroche voit passer.

LE GARDE-FOU
------------
Même règle que pour DragonUI : si les codes de format ne survivent pas à la
traduction, on garde l'anglais. Mieux vaut une ligne anglaise qu'un plantage.

Usage : python outils/traduire_epreuves.py [--dry]
"""
import glob
import io
import json
import os
import re
import struct
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from traduire_gisement import traduire  # noqa: E402
from generateur_db import polir  # noqa: E402

DATA = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Data"
SORTIE = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
          r"\AscensionFR\DB\DB_Epreuves.lua")
DOSSIER = os.path.join(BASE, "epreuves")
CACHE = os.path.join(DOSSIER, "cache.json")

CHAMP_NOM, CHAMP_DESC = 7, 24

# La Voie de l'Ascension vit dans Tutorial.dbc. On n'y connaît pas la
# disposition des champs — et on n'en a pas besoin : l'affichage est
# intercepté PAR LE TEXTE, pas par un identifiant. Il suffit donc de ramasser
# toutes les chaînes lisibles du bloc de textes.
DBC_LIBRES = ["tutorial.dbc", "tutorialcategories.dbc",
              # Challenge.dbc est AUSSI lu librement : les champs 7 et 24 ne
              # donnent que nom et description, alors que les restrictions
              # (« No Auction House »…) vivent dans d'autres champs.
              "challenge.dbc",
              # Les restrictions affichées (« No Auction House »…) ont leur
              # propre table : elles n'étaient dans aucune des précédentes.
              "challengeruletypes.dbc",
              # Les conditions d'activation et leurs info-bulles.
              "challengeconditiontypes.dbc",
              # Le LEXIQUE de la Voie (onglet « Keyword Appendix », demande
              # de Dan du 23/07) : 483 entrées nom + description courte +
              # description longue. Affichées par SetText simple
              # (PathAppendixPanelMixin/ItemMixin, extraits de patch-B) —
              # pile le canal de l'Intercepteur.
              "tutorialkeywords.dbc"]

# Le bloc contient aussi des noms d'icônes, des clés d'énumération et des
# chemins de fichiers. On ne garde que ce qui ressemble à une phrase.
RE_IDENTIFIANT = re.compile(r"^[A-Z0-9_]+$")
# 23/07 : la barre oblique SEULE ne suffit plus à dire « chemin » — les
# descriptions du Lexique contiennent des adresses web et des « PvE/PvP »
# en pleine phrase, et le filtre les rejetait EN ENTIER (vécu : « Arena
# Season » restée anglaise en jeu). Un chemin, c'est une barre oblique
# SANS AUCUNE espace autour ni dans le texte.
RE_CHEMIN = re.compile(r"\\|\.(?:blp|tga|lua|xml|mp3|ogg)$", re.I)


def parait_chemin(texte):
    return bool(RE_CHEMIN.search(texte)) \
        or ("/" in texte and " " not in texte)


def est_html(texte):
    """Une page de tutoriel : un document HTML avec ses balises et ses
    directives de texture. La Voie de l'Ascension n'affiche que ça."""
    return "<h1" in texte or "<p>" in texte or "<body" in texte


def parait_lisible(texte):
    if len(texte) < 3:
        return False
    # Les pages HTML sont longues et pleines de « \ » (chemins de textures) :
    # les deux garde-fous ci-dessous les rejetaient. Elles sont pourtant le
    # SEUL contenu de la Voie de l'Ascension.
    if est_html(texte):
        return len(texte) <= 20000
    # 2000 → 4000 le 23/07 : les grandes descriptions du Lexique de la
    # Voie (TutorialKeywords) dépassent l'ancien plafond.
    if len(texte) > 4000:
        return False
    if RE_IDENTIFIANT.match(texte) or parait_chemin(texte):
        return False
    if not re.search(r"[a-z]{2}", texte):      # aucune minuscule = technique
        return False
    # NOM D'ICÔNE : « Ability_Druid_Cower », « Achievement_Boss_Illidan ».
    # Le filtre précédent les laissait passer (ils ont des minuscules) et
    # l'usine les traduisait — « Capacité_Druid_Cower ». Un souligné sans
    # aucune espace ne se rencontre jamais dans une phrase affichée.
    if "_" in texte and " " not in texte:
        return False
    # Contenu retiré du jeu : traduire une entrée morte n'apporte rien et
    # brouille la relecture.
    if re.search(r"deprecated|\[unused\]|\bTEST\b", texte, re.I):
        return False
    return bool(re.search(r"[A-Za-z]{3}", texte))

RE_FORMAT = re.compile(r"%%|%[-+ #]?[0-9]*\.?[0-9]*[sdifxXqcueEgG]")

# Corrections écrites à la main. La machine traduit bien les phrases, mais
# prend les expressions imagées au pied de la lettre : ce sont presque
# toujours des titres de deux ou trois mots.
# Elles priment sur le cache ET sur la traduction automatique, à chaque
# passage — donc corriger ici suffit, définitivement.
MANUEL = {
    # « Classez vos sorts » : il s'agit de monter leur RANG, pas de les trier.
    "Rank Up Your Spells": "Améliorez vos sorts",
    # « articles » est un anglicisme ; LP est un sigle du jeu, on le garde.
    "Deliver LP Items": "Livrer les objets LP",
    # Un « high roller » est un gros parieur, pas un rouleau.
    "High Roller": "Flambeur",
    # « Karazhan » avait été déformé en « Karajan » — un nom de lieu du jeu
    # ne se traduit ni ne se réécrit.
    "Ascended: Karazhan": "Élu : Karazhan",
    # « callowness » = inexpérience, pas insensibilité.
    "Callowness": "Inexpérience",
    # « Bring it On! » est un défi lancé, pas une demande d'apporter un objet.
    "Bring it On!": "Amenez-vous !",
    # Ici « fantasy » désigne l'identité d'une classe, pas une fantaisie.
    "Building Your Class Fantasy": "Incarner votre classe",
    # « pet » se dit « familier » dans WoW en français.
    "Collect a Pet Appearance": "Récupérez une apparence de familier",
    # « Bewitched » : « Enchanté » prêterait à confusion avec l'enchantement.
    "Bewitched": "Ensorcelé",
    # « profession » = MÉTIER dans WoW. La machine comprenait « carrière » et
    # rendait « expérience professionnelle », qui ne veut rien dire ici.
    "No Profession Experience": "Aucune expérience de métier",
    "Only Profession Experience": "Expérience de métier uniquement",
    "Shared Profession Experience": "Expérience de métier partagée",
    "Profession Experience you gain is shared with your group members.":
        "L'expérience de métier que vous gagnez est partagée avec les "
        "membres de votre groupe.",
    "Shared Profession Experience - Profession Experience you gain is shared "
    "with your group members.":
        "Expérience de métier partagée - L'expérience de métier que vous "
        "gagnez est partagée avec les membres de votre groupe.",
    "Your profession choices are permanent. You are unable to unlearn any "
    "professions.":
        "Vos choix de métiers sont définitifs. Vous ne pouvez désapprendre "
        "aucun métier.",
    # ------------------------------------------------------------------ #
    # NOMS du Lexique de la Voie (TutorialKeywords, relecture du 23/07) —
    # le glossaire officiel WoW prime, puis nos conventions déjà arbitrées.
    # ------------------------------------------------------------------ #
    "Party": "Groupe",                       # « Faire la fête »…
    "Dungeon": "Donjon",                     # « Cachot »
    "Tailoring": "Couture",                  # « Adaptation »
    "Cooking": "Cuisine",                    # « Cuisson »
    "Enchanting": "Enchantement",            # le métier, pas l'enchanteur
    "Enchanting Altar": "Autel d'enchantement",
    "First Aid": "Secourisme",               # officiel (et sans MAJUSCULES)
    "Hearthstone": "Pierre de foyer",        # officiel
    "Spellbook": "Grimoire",                 # officiel
    "Auction House": "Hôtel des ventes",     # officiel
    "Heirlooms": "Héritages",                # officiel
    "Trials": "Épreuves",                    # notre convention établie
    "Hardcore Trial": "Épreuve hardcore",
    "Expertise": "Expertise",                # « Compétence » faux
    "Parry": "Parade",
    "Block": "Blocage",
    "Critical Strike": "Coup critique",
    "Critical Strike Damage Bonus": "Bonus de dégâts critiques",
    "Haste": "Hâte",
    "Attack Power": "Puissance d'attaque",
    "Spell Power": "Puissance des sorts",
    "Healing Power": "Puissance de soins",
    "Armor Penetration": "Pénétration d'armure",
    "Armor Type": "Type d'armure",
    "Hit Rating": "Score de toucher",
    "Hit Cap": "Cap de toucher",             # « Toucher le plafond »…
    "Mana Regeneration": "Régénération de mana",
    "Base Mana": "Mana de base",
    "Rested Experience": "Expérience de repos",
    "Arena Rating": "Cote d'arène",
    "Currency": "Monnaie",
    "Area: 52": "Zone : 52",                 # la ville gobeline, pas une aire
    "Primary Profession": "Métier principal",
    "Crafting Profession": "Métier de fabrication",
    "Gathering Profession": "Métier de récolte",
    "Profession": "Métier",
    "Profession Trainer": "Maître de métier",
    "Profession Specializations": "Spécialisations de métier",
    "Class Trainer": "Maître de classe",
    "Riding Trainer": "Maître d'équitation",
    "Quest Givers": "Donneurs de quêtes",
    "Pets Tab": "Onglet Familiers",
    "Realm-Wide Bank": "Banque de royaume",
    "Map Lens": "Filtre de la carte",
    "Draft Mode": "Mode Draft",              # le mode de pioche, pas un
    "Hero Architect": "Architecte de héros",  # brouillon
    "Mystic Enchant Collection": "Collection d'enchantements mystiques",
    "Mystic Enchant Specialization":
        "Spécialisation d'enchantement mystique",
    "Worldforged Mystic Enchant":
        "Enchantement mystique forgé par le monde",
    "Titan Scrolls": "Parchemins des Titans",
    "Bonzo Bolts": "Boulons de Bonzo",
    "Vanity Collection": "Collection de vanité",
    "Vanity Collection Sync": "Synchronisation de la collection de vanité",
    "PvP Quartermaster": "Intendant JcJ",
    "PvE Mode": "Mode JcE",
    "No-Risk PvP Mode": "Mode JcJ sans risque",
    "High-Risk PvP Mode": "Mode JcJ à haut risque",
    # La Tempête de mana : le mode porte le nom de Milhouse
    # Tempête-de-Mana (officiel Blizzard) — toute la famille s'aligne.
    "Manastorm": "Tempête de mana",
    "Manastorm Spells": "Sorts de la Tempête de mana",
    "Manastorm Caches": "Caches de la Tempête de mana",
    "Endless Manastorm Potion": "Potion inépuisable de la Tempête de mana",
    "Millhouse Manastorm": "Milhouse Tempête-de-Mana",
    "Millhouse's Magical Escape": "L'Évasion magique de Milhouse",
    # RÈGLE DE DAN (23/07/2026) : les noms de PNJ sont des noms PROPRES —
    # on ne les invente JAMAIS. Version française OFFICIELLE si elle
    # existe (Milhouse Tempête-de-Mana, Silas Sombrelune), sinon l'anglais
    # tel quel. Une IDENTITÉ ici garde l'anglais : elle bloque la
    # retraduction Google ET le générateur ne l'écrit pas en base.
    "Ameer Greatluck": "Ameer Greatluck",
    "Stony Tark": "Stony Tark",
    "Courier Malik": "Courier Malik",
}


def lire_challenge():
    """[(nom, description)] depuis Challenge.dbc."""
    donnees = None
    for chemin in sorted(glob.glob(os.path.join(DATA, "*.MPQ"))):
        try:
            from mpyq import MPQArchive
            archive = MPQArchive(chemin, listfile=True)
            noms = archive.files or []
        except Exception:
            continue
        for nom in noms:
            if isinstance(nom, bytes):
                nom = nom.decode("latin-1")
            if nom.lower().endswith("challenge.dbc"):
                try:
                    d = archive.read_file(nom)
                except Exception:
                    continue
                if d:
                    donnees = d          # un patch tardif prime
    if not donnees or donnees[:4] != b"WDBC":
        raise SystemExit("Challenge.dbc introuvable dans les archives.")

    nb, champs, taille, bloc = struct.unpack("<4I", donnees[4:20])
    debut = 20 + nb * taille
    chaines = donnees[debut:debut + bloc]

    def texte(v):
        if v <= 0 or v >= len(chaines):
            return ""
        fin = chaines.find(b"\0", v)
        return chaines[v:fin].decode("utf-8", "replace").strip()

    sortie = []
    for i in range(nb):
        base = 20 + i * taille
        vals = struct.unpack("<%dI" % champs, donnees[base:base + taille])
        sortie.append((texte(vals[CHAMP_NOM]), texte(vals[CHAMP_DESC])))
    return sortie


# Libellés du cadre : ce sont des GlobalStrings, DÉJÀ traduites dans
# DB_Interface.lua. On les fait entrer dans la base par leur texte anglais.
#
# Pourquoi ici et pas dans l'addon : le module lisait `_G[clé]` pour connaître
# l'anglais, mais le client n'expose PAS toutes les entrées de sa table de
# données en variables globales. « TRIALS » marchait, « ACTIVATE » non — même
# code, même base, seule l'exposition changeait. En figeant la paire ici, la
# question ne se pose plus.
CHROME = [
    "CHALLENGES_ABOUT", "CHALLENGES_EDITOR_LABEL_ABOUT",
    "CHALLENGES_LEADERBOARD", "CHALLENGES_AURAS",
    "CHALLENGES_RESTRICTIONS", "CHALLENGES_EDITOR_LABEL_RESTRICTIONS",
    "CHALLENGES_REQUIREMENTS",
    "CHALLENGES_EDITOR_LABEL_ACTIVATION_REQUIREMENTS",
    "CURRENT_LEVEL_COLON", "ACTIVATE", "DEACTIVATE",
    "CHALLENGES", "CHALLENGES_STORE", "CUSTOM_TRIALS", "TRIAL_BUILDER",
    "GAMEMODES", "TRIALS", "PATH_TO_ASCENSION",
    "MENTOR_SYSTEM", "KEYWORD_APPENDIX",
    "SEARCH", "FILTER",
    # Page de choix de spécialisation (Character Advancement, 21/07) :
    # ces clés existaient déjà en français dans DB_Interface, elles
    # n'étaient simplement pas chargées côté affichage.
    "SAMPLE_ABILITIES", "ACTIVATE_TALENTS", "VIEW_TALENTS",
    "COMPLEXITY_LABEL", "ACTIVE",
    "MELEE", "RANGED", "TANK", "HEALER", "SUPPORT",
    "MELEE_DAMAGER_SHORT", "RANGED_DAMAGER_SHORT", "CASTER_DAMAGER_SHORT",
    "TANK_SHORT", "HEALER_SHORT", "SUPPORT_SHORT",
    "SPELL_STAT1_NAME", "SPELL_STAT2_NAME", "SPELL_STAT3_NAME",
    "SPELL_STAT4_NAME", "SPELL_STAT5_NAME",
    "PRIMARY_STAT1_NAME", "PRIMARY_STAT2_NAME", "PRIMARY_STAT5_NAME",
    "PRIMARY_STAT_1_NAME_COA", "PRIMARY_STAT_2_NAME_COA",
    "PRIMARY_STAT_3_NAME_COA", "PRIMARY_STAT_4_NAME_COA",
    "PRIMARY_STAT_5_NAME_COA",
    # Fenêtre « modifications non appliquées » du build (21/07) — la clé
    # commence par CLOSE_, la famille CHARACTER_ADVANCEMENT ne la voit pas.
    "CLOSE_CHARACTER_ADVANCEMENT_UNSAVED_PENDING_CHANGES",
    "APPLY", "DISCARD", "GO_BACK",
    # Menus CLIC DROIT des cadres d'unité (21/07) : joueur, cible, familier.
    "SET_FOCUS", "CLEAR_FOCUS", "RAID_TARGET_ICON", "RESET_INSTANCES",
    "DUEL", "TRADE", "INSPECT", "WHISPER", "INVITE",
    "COMPARE_ACHIEVEMENTS", "PLAYER_V_PLAYER", "NO_RISK_PVE",
    "NO_RISK_PVP", "HIGH_RISK_PVP", "PET_ACTION_DISMISS", "CHAT_PROMOTE",
    # ... et leurs sous-menus (icônes de raid officielles, donjons)
    "RAID_TARGET_1", "RAID_TARGET_2", "RAID_TARGET_3", "RAID_TARGET_4",
    "RAID_TARGET_5", "RAID_TARGET_6", "RAID_TARGET_7", "RAID_TARGET_8",
    "RESET_ALL_DUNGEONS",
    # Libellés de la CARTE DU MONDE (21/07) : ont un frFR dans DB_Interface
    # mais l'interface n'écrit plus les globales (anti-plantage) — on les
    # traduit à l'affichage. Attention aux identités (Continent, Zone) que
    # le générateur écarte de lui-même.
    "BATTLEFIELD_MINIMAP", "BATTLEFIELD_MINIMAP_SHOW_NEVER",
    "BATTLEFIELD_MINIMAP_SHOW_ALWAYS", "CONTINENT", "ZONE", "ZOOM_OUT",
    "ZOOM_IN", "SHOW_QUEST_OBJECTIVES_ON_MAP_TEXT",
]
DB_UI = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
         r"\AscensionFR\DB\DB_Interface.lua")

# Littéraux vus à l'écran mais absents des GlobalStrings (replis
# « X = X or "..." » des addons du client, onglets, boutons des fenêtres
# Character Advancement / Wardrobe / Vanity). Traduits ici même.
LITTERAUX = [
    ("New Spell Learned!", "Nouveau sort appris !"),
    # Carte du monde (titre, cases à cocher)
    ("World Map", "Carte du monde"),
    ("Track Quest", "Suivre la quête"),
    ("Show Quest Objectives", "Afficher les objectifs de quête"),
    # Fenêtre de détail de quête (clic sur le suivi)
    ("Quest Details", "Détails de la quête"),
    ("Show Map", "Afficher la carte"),
    # Barres de ressources de classe (bulle de survol)
    ("Felfury", "Gangrefurie"),
    ("Demonfire", "Feu démoniaque"),
    ("Right click to customize menu", "Clic droit pour personnaliser"),
    ("Drag to move", "Glisser pour déplacer"),
    # Feuille de personnage custom d'Ascension (étiquettes observées)
    ("Character Info", "Infos du personnage"),
    ("Attributes", "Attributs"),
    ("Strength:", "Force :"), ("Agility:", "Agilité :"),
    ("Intellect:", "Intelligence :"), ("Spirit:", "Esprit :"),
    ("Stamina:", "Endurance :"),
    ("Ranged", "À distance"), ("Melee", "Mêlée"), ("Defense", "Défense"),
    ("Damage:", "Dégâts :"), ("Speed:", "Vitesse :"),
    ("Power:", "Puissance :"), ("Hit Rating:", "Score de toucher :"),
    ("Armor Penetration:", "Pénétration d'armure :"),
    ("Crit Chance:", "Chances de critique :"),
    ("Haste Rating:", "Score de hâte :"),
    ("Expertise:", "Expertise :"), ("Armor:", "Armure :"),
    ("Dodge:", "Esquive :"), ("Parry:", "Parade :"),
    ("Block:", "Blocage :"), ("Resilience:", "Résilience :"),
    ("Spell Power:", "Puissance des sorts :"),
    ("Mana Regen:", "Régén. de mana :"),
    ("Item Level", "Niveau d'objet"),
    ("Prestige Level:", "Niveau de prestige :"),
    ("Character", "Personnage"), ("Reputation", "Réputation"),
    ("Skills", "Compétences"), ("Currency", "Monnaies"),
    # Page « Professions » du grimoire (rangs sous les icônes, titre/onglet)
    ("Professions", "Métiers"),
    ("Apprentice", "Apprenti"),
    ("Journeyman", "Compagnon"),
    ("Grand Master", "Grand maître"),
    ("Master", "Maître"),
    ("Reset Trees", "Réinitialiser les arbres"),
    ("Change Talents", "Changer les talents"),
    ("Change Active Specialization", "Changer de spécialisation active"),
    ("Find Premade Builds...", "Trouver des builds prédéfinis..."),
    ("Share Build", "Partager le build"),
    ("Import Build", "Importer un build"),
    ("Right click to unlearn", "Clic droit pour désapprendre"),
    ("Character Advancement", "Avancement du personnage"),
    ("Conquest of Azeroth - Character Advancement",
     "Conquête d'Azeroth - Avancement du personnage"),
    ("Wardrobe", "Garde-robe"),
    ("Vanity", "Vanité"),
    ("Vanity Item Collection", "Collection d'objets de vanité"),
    ("Save Outfit", "Sauvegarder la tenue"),
    ("Disable Transmog", "Désactiver la transmog"),
    ("Enable Transmog", "Activer la transmog"),
    ("Disable Spell Visuals", "Désactiver les effets visuels des sorts"),
    ("Enable Spell Visuals", "Activer les effets visuels des sorts"),
    ("Purchase Item", "Acheter l'objet"),
    ("Deliver Item", "Livrer l'objet"),
    ("Available from the Webstore", "Disponible sur la boutique en ligne"),
    ("Order By", "Trier par"),
    ("Incarnations", "Incarnations"),
    ("Cosmetics", "Cosmétiques"),
    ("Sets", "Ensembles"),
    ("Mounts", "Montures"),
    ("Companions", "Compagnons"),
    ("Toys", "Jouets"),
    ("Outfits", "Tenues"),
    ("Items", "Objets"),
    # L'onglet du Lexique de la Voie (PTA_KEYWORD_APPENDIX — la clé CHROME
    # « KEYWORD_APPENDIX » n'existe pas dans les GlobalStrings, vérifié).
    ("Keyword Appendix", "Lexique"),
    # Fenêtre des talents (capture de Dan, 24/07) : ces textes n'existaient
    # qu'À L'INTÉRIEUR des pages-tutoriels, jamais en paires seules.
    ("Spend more points to unlock this talent",
     "Dépensez plus de points pour débloquer ce talent"),
    ("Save Changes", "Enregistrer les modifications"),
    # Le titre d'arbre TEMPLAR n'avait AUCUNE paire (Crusader oui — d'où
    # l'asymétrie TEMPLAR/CROISÉ à l'écran). Les deux casses, comme les
    # émissions de chrspecs.
    ("Templar", "Templier"),
    ("TEMPLAR", "TEMPLIER"),
]


def paires_chrome():
    """[(anglais, français)] pour les libellés du cadre."""
    anglais_par_cle = {}
    # La base du jeu d'abord (locale-enUS porte les clés VANILLA comme
    # BATTLEFIELD_MINIMAP), puis les patchs custom qui la recouvrent —
    # sans la base, les libellés de la carte du monde restaient absents
    # (constaté le 21/07).
    chemins = (sorted(glob.glob(os.path.join(DATA, "enUS", "*.MPQ")))
               + sorted(glob.glob(os.path.join(DATA, "*.MPQ"))))
    for chemin in chemins:
        try:
            from mpyq import MPQArchive
            archive = MPQArchive(chemin, listfile=True)
            noms = archive.files or []
        except Exception:
            continue
        for nom in noms:
            if isinstance(nom, bytes):
                nom = nom.decode("latin-1")
            if not nom.lower().endswith("globalstrings.dbc"):
                continue
            try:
                d = archive.read_file(nom)
            except Exception:
                continue
            if not d or d[:4] != b"WDBC":
                continue
            nb, champs, taille, bloc = struct.unpack("<4I", d[4:20])
            debut = 20 + nb * taille
            chaines = d[debut:debut + bloc]

            def texte(v):
                if v < 0 or v >= len(chaines):
                    return ""
                fin = chaines.find(b"\0", v)
                return chaines[v:fin].decode("utf-8", "replace")

            for i in range(nb):
                base = 20 + i * taille
                vals = struct.unpack("<%dI" % champs, d[base:base + taille])
                anglais_par_cle[texte(vals[2])] = texte(vals[3])

    francais_par_cle = {}
    if os.path.exists(DB_UI):
        with io.open(DB_UI, encoding="utf-8") as f:
            for ligne in f:
                m = re.match(r'^DB\["([^"]+)"\]="((?:\\.|[^"\\])*)"', ligne)
                if m:
                    francais_par_cle[m.group(1)] = m.group(2)

    # Familles ENTIÈRES, en plus de la liste nominative : les modes de jeu
    # (GAMEMODEn, BUILDDRAFT_MODE, *_MODE_DESC…) surgissaient un par un à
    # chaque onglet exploré. Une étiquette de plus dans la famille = traduite
    # d'office, sans repasser ici.
    cles = list(CHROME)
    for cle in anglais_par_cle:
        if cle.startswith("GAMEMODE") or cle.endswith("_MODE") \
                or cle.endswith("_MODE_DESC") \
                or cle.startswith("COA_") \
                or cle.startswith("TRANSMOG_") \
                or cle.startswith("CHARACTER_ADVANCEMENT") \
                or cle.startswith("VANITY") or "_VANITY" in cle \
                or cle == "APPEARANCE_WARDROBE" \
                or cle.startswith("SPEC_COMPLEXITY") \
                or cle.startswith("BUILD_DIFFICULTY_RATING") \
                or cle.startswith("BUILD_FILTER") \
                or cle.startswith("CLASS_COMBAT_STYLE"):
            cles.append(cle)

    paires = []
    for cle in cles:
        anglais = (anglais_par_cle.get(cle) or "").strip()
        francais = (francais_par_cle.get(cle) or "").strip()
        if anglais and francais and anglais != francais:
            paires.append((anglais, francais.replace('\\"', '"')))
    # Littéraux SANS étiquette (replis « X = X or "..." » des addons du
    # client : talents CoA, onglets Wardrobe/Vanity, boutons). Ajoutés
    # seulement si une étiquette ne les couvre pas déjà.
    deja = dict(paires)
    for anglais, francais in LITTERAUX:
        # jamais d'entrée IDENTITÉ (français == anglais) : elle faisait
        # « réussir » l'interception à chaque balayage et re-armait le
        # rebalayage perpétuel (audit du 20/07 au soir).
        if anglais not in deja and anglais != francais:
            paires.append((anglais, francais))
    return paires


def lire_dbc_libre(nom_fichier):
    """Toutes les chaînes LISIBLES du bloc de textes d'une DBC.

    On ne décode PAS les enregistrements : l'affichage étant intercepté par le
    texte, la structure des champs n'a aucune importance. C'est ce qui permet
    d'ouvrir une table inconnue sans en faire la rétro-ingénierie.
    """
    donnees = None
    for chemin in sorted(glob.glob(os.path.join(DATA, "*.MPQ"))):
        try:
            from mpyq import MPQArchive
            archive = MPQArchive(chemin, listfile=True)
            noms = archive.files or []
        except Exception:
            continue
        for nom in noms:
            if isinstance(nom, bytes):
                nom = nom.decode("latin-1")
            if nom.lower().endswith(nom_fichier):
                try:
                    d = archive.read_file(nom)
                except Exception:
                    continue
                if d:
                    donnees = d
    if not donnees or donnees[:4] != b"WDBC":
        return []
    nb, champs, taille, bloc = struct.unpack("<4I", donnees[4:20])
    debut = 20 + nb * taille
    chaines = donnees[debut:debut + bloc]
    sortie = []
    for morceau in chaines.split(b"\0"):
        if not morceau:
            continue
        texte = morceau.decode("utf-8", "replace").strip()
        # Sauts de ligne LITTÉRAUX de TutorialKeywords : la convention du
        # fichier est la PAIRE « retour chariot + \n en deux caractères »
        # (relevé sur les enregistrements bruts). On ne convertit QUE la
        # paire — un « \n » seul est presque toujours un chemin de texture
        # (piège vécu : « PtA\naxx1 », la bannière de Naxxramas, coupée en
        # deux par un remplacement trop large).
        texte = texte.replace("\r\\n", "\n")
        if parait_lisible(texte):
            sortie.append(texte)
    return sortie


# Balises, directives de texture et sauts de ligne : tout ce qui doit sortir
# du document AVANT traduction et y revenir intact.
RE_STRUCTURE = re.compile(r"(<[^>]*>|\{[^}]*\}|\|c[0-9a-fA-F]{8}|\|r|\r\n|\n)")


def traduire_html(document):
    """Traduit une page HTML fragment par fragment.

    On ne confie JAMAIS le document entier au traducteur : il réécrirait les
    balises et le chemin de texture. On découpe donc sur la structure, on ne
    traduit que les morceaux de prose, et on recolle à l'identique.
    """
    morceaux = RE_STRUCTURE.split(document)
    sortie = []
    for morceau in morceaux:
        if not morceau or RE_STRUCTURE.match(morceau):
            sortie.append(morceau)          # structure : intouchée
        elif re.search(r"[A-Za-z]{3}", morceau):
            fr = traduire(morceau)
            sortie.append(fr if fr else morceau)
        else:
            sortie.append(morceau)
    return "".join(sortie)


def sur(anglais, francais):
    if not francais or francais == anglais:
        return False
    return sorted(RE_FORMAT.findall(anglais)) == sorted(
        RE_FORMAT.findall(francais))


def echapper(s):
    """Échappe pour Lua SANS rien normaliser.

    La version précédente transformait « \\r\\n » en « \\n ». La clé stockée ne
    correspondait alors plus, octet pour octet, au texte que le jeu envoie :
    les descriptions à plusieurs paragraphes ne se reconnaissaient plus et
    restaient en anglais, alors qu'elles étaient bel et bien traduites en base.
    Une clé de correspondance exacte ne se normalise jamais.
    """
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return s.replace("\r", "\\r").replace("\n", "\\n")


def main():
    dry = "--dry" in sys.argv
    lignes_dbc = lire_challenge()

    # Un même texte peut servir à plusieurs épreuves : on dédoublonne.
    anglais = []
    vus = set()
    for nom, desc in lignes_dbc:
        for t in (nom, desc):
            if t and t not in vus and re.search(r"[A-Za-z]{3}", t):
                vus.add(t)
                anglais.append(t)

    # La Voie de l'Ascension et les autres tables sans structure connue.
    for fichier in DBC_LIBRES:
        avant = len(anglais)
        for t in lire_dbc_libre(fichier):
            if t not in vus:
                vus.add(t)
                anglais.append(t)
        print("  %-26s +%d textes" % (fichier, len(anglais) - avant))

    # Le Lexique retire les balises {image} et les sauts de ligne de tête
    # AVANT d'afficher (PathAppendixPanelMixin:OnKeywordSelected, patch-B).
    # La clé utile est donc AUSSI la variante nettoyée — l'originale reste
    # (elle peut servir ailleurs, une clé muette ne coûte rien).
    variantes = []
    for texte in list(anglais):
        if "{" not in texte or est_html(texte):
            continue
        variante = re.sub(r"\{[^}]+\}", "", texte)
        variante = re.sub(r"^\n+", "", variante).strip()
        if variante and variante not in vus \
                and re.search(r"[A-Za-z]{3}", variante):
            vus.add(variante)
            variantes.append(variante)
    anglais.extend(variantes)
    print("  variantes sans {image} (mixin)        : +%d" % len(variantes))

    # Les PAGES de la Voie ne sont JAMAIS affichées entières. Le client les
    # découpe (PathObjectiveDisplayMixin : SplitPages sur « {page} », puis
    # autour de chaque balise {…} d'image), nettoie chaque fragment, et
    # l'enveloppe dans <html><body>…</body></html> avant SetText
    # (DynamicSimpleHTMLMixin, sharedpaneltemplates.lua:1360-1367). Les clés
    # utiles sont donc les FRAGMENTS ENVELOPPÉS — le document entier ne
    # correspond à rien de ce qui s'affiche (élucidé le 20/07/2026).
    GABARIT = "<html><body>%s</body></html>"
    fragments = []
    for texte in list(anglais):
        if not est_html(texte):
            continue
        for page in texte.split("{page}"):
            for morceau in re.split(r"\{[^}]*\}", page):
                morceau = morceau.strip()
                if morceau and re.search(r"[A-Za-z]{3}", morceau):
                    enveloppe = GABARIT % morceau
                    if enveloppe not in vus:
                        vus.add(enveloppe)
                        fragments.append(enveloppe)
    anglais.extend(fragments)
    print("  fragments de pages (découpage client) : +%d" % len(fragments))

    cache = {}
    if os.path.exists(CACHE):
        with io.open(CACHE, encoding="utf-8") as f:
            cache = json.load(f)

    # Les corrections manuelles écrasent tout, y compris le cache : elles
    # doivent survivre à n'importe quelle relance.
    cache.update(MANUEL)

    a_faire = [t for t in anglais if t not in cache]
    print("épreuves lues      : %d" % len(lignes_dbc))
    print("textes distincts   : %d" % len(anglais))
    print("déjà en cache      : %d" % (len(anglais) - len(a_faire)))
    print("à traduire         : %d" % len(a_faire))
    print()

    refuses = []
    for i, texte_en in enumerate(a_faire, 1):
        if est_html(texte_en):
            fr = traduire_html(texte_en)
        else:
            fr = traduire(texte_en)
        if not sur(texte_en, fr):
            refuses.append(texte_en)
            continue
        cache[texte_en] = fr
        print("  %-46s -> %s" % (texte_en[:46], fr[:46]))
        if not dry and i % 25 == 0:
            os.makedirs(DOSSIER, exist_ok=True)
            with io.open(CACHE, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=1,
                          sort_keys=True)

    print()
    print("traduits : %d | refusés (anglais gardé) : %d"
          % (len(cache), len(refuses)))
    for r in refuses[:10]:
        print("   refusé : %s" % r[:70])

    if dry:
        print("\n--dry : rien écrit.")
        return 0

    os.makedirs(DOSSIER, exist_ok=True)
    with io.open(CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1, sort_keys=True)

    lignes = ["-- Fichier généré par outils/traduire_epreuves.py "
              "- NE PAS ÉDITER.",
              "-- Épreuves d'Ascension, lues dans Challenge.dbc.",
              "-- Indexé par le TEXTE ANGLAIS : c'est lui que l'accroche "
              "voit passer.",
              "local DB = AscensionFR.DB.Epreuves"]
    # Les ADRESSES WEB doivent survivre à la traduction TELLES QUELLES
    # (vécu : Google réécrivait « /en/timeline » dans la description de la
    # Saison d'arène). On restaure celles de l'anglais, dans l'ordre.
    RE_ADRESSE = re.compile(r"https?://[^\s]+")

    def reparer_adresses(en, fr):
        bonnes = RE_ADRESSE.findall(en)
        if not bonnes:
            return fr
        vues = RE_ADRESSE.findall(fr)
        if vues == bonnes:
            return fr
        compteur = {"i": 0}

        def suivante(_m):
            i = compteur["i"]
            compteur["i"] = i + 1
            return bonnes[i] if i < len(bonnes) else _m.group(0)
        return RE_ADRESSE.sub(suivante, fr)

    n = 0
    for texte_en in sorted(cache):
        if texte_en in vus:
            cache[texte_en] = reparer_adresses(texte_en, cache[texte_en])
            # Une IDENTITÉ (français == anglais) ne s'écrit jamais : c'est
            # le « ne pas traduire » des noms propres (règle de Dan sur les
            # PNJ, 23/07). Au cache elle bloque la retraduction ; en base
            # elle ne ferait que du bruit.
            if cache[texte_en] == texte_en:
                continue
            lignes.append('DB["%s"]="%s"' % (echapper(texte_en),
                                             echapper(cache[texte_en])))
            n += 1
    lignes.append("")
    lignes.append("-- Libellés du cadre (GlobalStrings déjà traduites).")
    ecrits = set()
    for anglais, francais in paires_chrome():
        if anglais not in cache and anglais not in ecrits \
                and anglais != francais:
            ecrits.add(anglais)
            lignes.append('DB["%s"]="%s"' % (echapper(anglais),
                                             echapper(francais)))
            n += 1
    # Page de choix de spécialisation (ChrSpecs.dbc de patch-M.MPQ) : noms
    # d'arbres et descriptions des cartes, traduits dans chrspecs.json.
    # Les TITRES d'arbres sont émis en casse mixte ET EN CAPITALES : la page
    # des talents affiche « DEFIANCE » en majuscules côté client.
    CHRSPECS = os.path.join(BASE, "traductions", "chrspecs.json")
    if os.path.exists(CHRSPECS):
        with io.open(CHRSPECS, encoding="utf-8") as f:
            specs = json.load(f)
        lignes.append("")
        lignes.append("-- Cartes de spécialisation (ChrSpecs.dbc).")
        paires_specs = []
        for en, fr in sorted(specs.get("arbres", {}).items()):
            paires_specs.append((en, fr))
            paires_specs.append((en.upper(), fr.upper()))
        paires_specs += sorted(specs.get("descriptions", {}).items())
        # Fenêtres du personnage (métiers/monnaies/compétences/compagnons,
        # 21/07) : paires exactes de traductions/fenetres_perso.json.
        FENETRES = os.path.join(BASE, "traductions", "fenetres_perso.json")
        if os.path.exists(FENETRES):
            with io.open(FENETRES, encoding="utf-8") as f:
                paires_specs += sorted(
                    json.load(f).get("paires", {}).items())
        # Fichiers de PAIRES exactes du chantier complétude (chacun :
        # { "paires": {EN: FR} }) — enchantements officiels (#16),
        # intérieurs de bâtiments (WMOAreaTable), points d'intérêt de la
        # carte (AreaPOI), boss (DungeonEncounter), ensembles d'objets
        # (ItemSet). L'ordre ne compte pas : le dédoublonnage garde la
        # première occurrence et nos choix main (ci-dessus) priment.
        for fichier in ("enchantements", "interieurs", "poi_carte",
                        "boss", "ensembles", "vanity_obtention"):
            chemin_p = os.path.join(BASE, "traductions",
                                    fichier + ".json")
            if os.path.exists(chemin_p):
                with io.open(chemin_p, encoding="utf-8") as f:
                    paires_specs += sorted(
                        json.load(f).get("paires", {}).items())
        # La moisson du PackFR (outils/moissonner_packfr.py, 21/07) :
        # 20 familles (critères de hauts faits, enchantements, factions,
        # titres, cartes...). Lue EN DERNIER : nos propres choix priment
        # (le dédoublonnage garde la première occurrence).
        PACKFR = os.path.join(BASE, "traductions", "packfr_interface.json")
        if os.path.exists(PACKFR):
            with io.open(PACKFR, encoding="utf-8") as f:
                for _famille, paires_f in sorted(json.load(f).items()):
                    paires_specs += sorted(paires_f.items())
        for anglais, francais in paires_specs:
            if anglais and francais and anglais != francais \
                    and anglais not in cache and anglais not in ecrits:
                ecrits.add(anglais)
                # Vocabulaire arbitré : le texte vient du DBC officiel, que
                # appliquer_vocabulaire.py ne voit jamais.
                lignes.append('DB["%s"]="%s"' % (echapper(anglais),
                                                 echapper(polir(francais,
                                                                anglais=anglais))))
                n += 1
    with io.open(SORTIE, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")
    print("\nécrit : %s (%d textes)" % (os.path.basename(SORTIE), n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
