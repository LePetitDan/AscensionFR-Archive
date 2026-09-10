# -*- coding: utf-8 -*-
"""
L'écran de connexion, la sélection et la création de personnage en français.

POURQUOI UN MPQ, ALORS QUE TOUT LE RESTE EST UN ADDON
-----------------------------------------------------
WoW 3.3.5 a deux mondes étanches. `Interface\\AddOns` n'existe qu'une fois en
jeu ; les écrans d'avant (connexion, sélection, création) sont le « glue », que
le client ne lit QUE depuis ses archives MPQ. Aucun addon ne peut les toucher.
Vérifié aussi : les fichiers libres de `Data\\enUS\\Interface` ne servent qu'aux
cinématiques. Le MPQ n'est donc pas un choix, c'est le seul véhicule.

CE QUI REND LE TRAVAIL PETIT
----------------------------
1. Les GlueStrings d'Ascension sont EXACTEMENT celles de Blizzard : mêmes 874
   clés, au mot près. Le frFR officiel est un remplacement direct — les
   descriptions de race (RACE_INFO_*), leurs aptitudes (ABILITY_INFO_*) et les
   classes Blizzard (CLASS_INFO_*) comprises.
2. Les chaînes maison d'Ascension sont écrites « X = X or "..." » : si une
   valeur existe déjà, leur code la garde. GlueStrings.lua étant chargé avant,
   notre français passe devant — leur propre code nous y invite.

CE QUI RESTE HORS DE PORTÉE DE CE FICHIER
-----------------------------------------
Les rôles et catégories du guide de classe viennent de DBC
(CharacterCreationClassGuideRoles/Subroles.dbc, dans patch-M.MPQ) et non des
GlueStrings. On les lit ici pour les traduire à l'affichage, en enveloppant
les fonctions du client — pas en réécrivant ses données.

LA RÈGLE DE SÛRETÉ, PLUS IMPORTANTE ICI QU'AILLEURS
---------------------------------------------------
Une traduction n'est posée que si elle attend exactement les mêmes arguments
que la chaîne anglaise d'Ascension (voir SignatureCompatible, jumelle de celle
de Modules\\InterfaceUI.lua). En jeu, un format() incompatible gâche une
info-bulle. Ici, il empêcherait de se connecter — et on ne répare pas un écran
de connexion depuis le jeu.

Usage : python outils/generateur_glue.py [--ecrire]
        (sans --ecrire : rapport seul, aucune archive touchée)
"""
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import mpq_ecrire  # noqa: E402
except ImportError:
    # Le module a disparu du dépôt lors d'un nettoyage. Il ne sert QU'À écrire
    # l'archive MPQ de l'écran de connexion — une voie morte, le lanceur
    # supprime les archives inconnues. Son absence ne doit donc pas empêcher
    # `signature_compatible` de servir : c'est elle que fusionner_gisement
    # importe, et sans elle plus aucune traduction d'interface ne peut être
    # livrée (panne découverte le 20/07/2026, invisible depuis des semaines).
    mpq_ecrire = None

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chemin_client import JEU  # noqa: E402
SOURCES = os.path.join(BASE, "sources")
GLUE_FR = os.path.join(SOURCES, "GlueStrings_frFR.lua")
GLUE_ASC = os.path.join(SOURCES, "gluexml", "GlueStrings_enUS.lua")
CREATION_ASC = os.path.join(SOURCES, "gluexml", "CharacterCreate_Ascension.lua")
PATCH_M = os.path.join(JEU, "Data", "patch-M.MPQ")

# Le glue est du contenu de langue : sa place est parmi les archives de
# locale, dont c'est le rôle, et qui priment sur les archives de base.
ARCHIVE = os.path.join(JEU, "Data", "enUS", "patch-enUS-4.MPQ")
INTERNE = "Interface\\GlueXML\\GlueStrings.lua"
# Fichier libre : le launcher tolère Interface\ (notre addon y vit depuis des
# semaines) alors qu'il balaie Data\. ESSAI DU 17/07 : sans effet — le client
# ne relit pas GlueStrings.lua depuis le disque.
LIBRE = os.path.join(JEU, "Interface", "GlueXML", "GlueStrings.lua")

# La porte que le client laisse ouverte.
#
# Son journal (Logs\GlueXML.log) répète à chaque lancement :
#     Couldn't open Interface\PTRXML\PTR.xml
# Son propre GlueXML.toc réclame ce fichier — un point d'entrée de test que
# leur build public ne livre pas. On ne réécrit rien : on remplit un vide que
# le client demande, comme un addon remplit son dossier. Chargé en 2e ligne du
# toc, donc AVANT tous leurs écrans : nos valeurs sont en place quand leur
# « X = X or ... » les cherche.
#
# Réversible : supprimer le dossier PTRXML. Si le fichier est mauvais, le
# client le signale et poursuit (« Error loading ... » apparaît déjà dans leur
# journal pour un de leurs propres fichiers, sans gêner le jeu).
PORTE_XML = os.path.join(JEU, "Interface", "PTRXML", "PTR.xml")
PORTE_LUA = os.path.join(JEU, "Interface", "PTRXML", "AscensionFR_Glue.lua")

GABARIT_XML = """<Ui xmlns="http://www.blizzard.com/wow/ui/">
    <!-- Ascension FR. Le client réclame ce fichier et ne le trouve pas
         (voir Logs\\GlueXML.log) : on l'y met, il charge notre traduction.
         Pour tout annuler : supprimer le dossier Interface\\PTRXML. -->
    <Script file="AscensionFR_Glue.lua"/>
</Ui>
"""

CLE_RE = re.compile(r'^([A-Z_0-9]+) *= *"((?:[^"\\]|\\.)*)"', re.M)
# Les chaînes maison : « X = X or "valeur" »
MAISON_RE = re.compile(
    r'^([A-Z_0-9]+) *= *\1 *or *"((?:[^"\\]|\\.)*)"', re.M)

# --- Chaînes maison d'Ascension (recensées, pas devinées) -------------------
# Le générateur vérifie que chaque clé existe encore dans leur code et
# signale toute nouveauté : à leur prochaine mise à jour, on le saura.
MAISON_FR = {
    "CHAR_CREATE_HELP_NEXT_BUTTON":
        "Vous pouvez passer à l'étape suivante\\n\\n"
        "Vous pourrez modifier ces choix à tout moment",
    "CHAR_CREATE_CUSTOMIZE_YOUR_APPEARANCE": "Personnalisez votre apparence ",
    "CHAR_CREATE_CHANGE_ANY_TIME":
        "Vous pourrez modifier ces choix à tout moment !",
    "CHAR_CREATE_HELP_CHOOSE_CLASS": "Aidez-moi à choisir",
    "CLASS_GUIDE_ROLE_SELECT_TEXT": "Choisir un rôle",
    "CLASS_GUIDE_CATEGORY_SELECT_TEXT": "Choisir une catégorie",
    "CLASS_GUIDE_CLASS_SELECT_TEXT": "Choisir une classe",
    "CLASS_GUIDE_ROLE_SELECTED_TEXT": "Rôle choisi :\\n%s",
    "CLASS_GUIDE_CATEGORY_SELECTED_TEXT": "Catégorie choisie :\\n%s",
    "CLASS_GUIDE_CLASS_SELECTED_TEXT": "Classe choisie :\\n%s",
}

# --- Guide de classe : rôles et catégories (DBC) ----------------------------
# Noms de jeu : un traducteur automatique les massacre, on les écrit à la main.
GUIDE_FR = {
    "Tank": "Tank",
    "Healer": "Soigneur",
    "Damage": "Dégâts",
    "Support": "Soutien",
    "Melee": "Corps à corps",
    "Ranged": "À distance",
    "Caster": "Incantateur",
    "Hybrid": "Hybride",
    "Classes that can protect allies and hold enemies.":
        "Classes capables de protéger leurs alliés et de tenir les ennemis.",
    "Classes that restore and protect allies.":
        "Classes qui soignent et protègent leurs alliés.",
    "Classes focused on defeating enemies.":
        "Classes vouées à terrasser les ennemis.",
    "Classes with utility, control, or group support.":
        "Classes d'utilité, de contrôle ou de soutien de groupe.",
    "Damage classes that blend physical and spell combat.":
        "Classes de dégâts mêlant combat physique et sorts.",
    "Damage classes that fight up close.":
        "Classes de dégâts qui combattent au contact.",
    "Damage classes that attack from range.":
        "Classes de dégâts qui frappent à distance.",
    "Damage classes built around spells.":
        "Classes de dégâts bâties autour des sorts.",
    "Classes with a tank specialization.":
        "Classes ayant une spécialisation de tank.",
    "Classes with a healing specialization.":
        "Classes ayant une spécialisation de soins.",
    "Classes with support specialization data.":
        "Classes ayant une spécialisation de soutien.",
}


# ---------------------------------------------------------------------------
# Contrôle de signature — JUMELLE de SignatureCompatible (InterfaceUI.lua).
# Toute correction ici doit être portée là-bas, et réciproquement.
# ---------------------------------------------------------------------------
SPEC_RE = re.compile(r"%(\d*)(\$?)([-+ #0]*\d*\.?\d*)([dfsuxXeEgGqc])")


def arguments(texte):
    """{ rang: type } des arguments consommés, ou None si contradictoire."""
    nettoye = texte.replace("%%", "")
    args, suivant = {}, 0
    for rang, dollar, _, genre in SPEC_RE.findall(nettoye):
        if dollar == "$" and rang:
            position = int(rang)
        else:
            # Sans « $ », d'éventuels chiffres sont une largeur, pas un rang.
            suivant += 1
            position = suivant
        if position in args and args[position] != genre:
            return None
        args[position] = genre
    return args


def signature_compatible(origine, traduction):
    a, b = arguments(origine), arguments(traduction)
    if a is None or b is None:
        return False
    maxi = max(list(a) + list(b) + [0])
    return all(a.get(i) == b.get(i) for i in range(1, maxi + 1))


def lire_chaines(chemin):
    with open(chemin, encoding="utf-8", errors="ignore") as f:
        return dict(CLE_RE.findall(f.read()))


# ---------------------------------------------------------------------------
# Les sources vivent dans le client, pas dans nos copies
#
# Après un patch d'Ascension, une copie figée dans sources/ ment. On lit donc
# les fichiers dans les archives à chaque génération, et on ne retombe sur la
# copie que si l'archive est illisible.
# ---------------------------------------------------------------------------
ARCHIVES_GLUE = {
    # (archive, fichier interne) -> copie de secours
    #
    # GlueStrings.lua : quatre archives en portent une ; celle qui gagne est
    # dans patch-enUS-3 (874 clés ; locale-enUS 712, patch-enUS 785,
    # patch-enUS-2 867). C'est elle, la référence.
    (os.path.join(JEU, "Data", "enUS", "patch-enUS-3.MPQ"),
     "Interface\\GlueXML\\GlueStrings.lua"): GLUE_ASC,
    # CharacterCreate_Ascension.lua n'est PAS rafraîchissable : il n'apparaît
    # dans le listfile d'aucune archive ni dans leur GlueXML.toc (un XML
    # l'inclut). On garde donc la copie de sources/gluexml, dont on ne tire
    # que les 10 chaînes maison — stables. Si Ascension en ajoute, le
    # générateur ne le verra pas : c'est la limite connue de ce fichier.
}
TOC = (os.path.join(JEU, "Data", "patch-B.MPQ"),
       "Interface\\GlueXML\\GlueXML.toc")


def _lire_archive(archive, interne):
    from mpyq import MPQArchive
    a = MPQArchive(archive, listfile=False)
    try:
        donnees = a.read_file(interne)
    finally:
        if getattr(a, "file", None):
            a.file.close()
    return donnees


def rafraichir_sources(journal=print):
    """Recopie depuis les archives du jeu ce dont on dépend."""
    for (archive, interne), copie in ARCHIVES_GLUE.items():
        try:
            donnees = _lire_archive(archive, interne)
        except Exception as e:
            journal("  ! %s illisible (%s) : on garde la copie"
                    % (os.path.basename(archive), str(e)[:40]))
            continue
        if not donnees:
            journal("  ! %s absent de %s : on garde la copie"
                    % (interne, os.path.basename(archive)))
            continue
        os.makedirs(os.path.dirname(copie), exist_ok=True)
        with open(copie, "wb") as f:
            f.write(donnees)


def porte_ouverte(journal=print):
    """Le client réclame-t-il toujours notre point d'entrée ?

    C'est LE point de rupture après un patch : si Ascension retire PTR.xml de
    son GlueXML.toc, notre fichier n'est plus chargé et l'écran repasse en
    anglais — sans erreur, sans bruit. Mieux vaut le dire.
    """
    try:
        donnees = _lire_archive(*TOC)
    except Exception as e:
        journal("  ! GlueXML.toc illisible (%s)" % str(e)[:40])
        return None
    if not donnees:
        return None
    toc = donnees.decode("utf-8", "ignore")
    return "PTRXML\\PTR.xml" in toc or "PTRXML/PTR.xml" in toc


# ---------------------------------------------------------------------------
# Rôles et catégories du guide de classe (DBC de patch-M.MPQ)
# ---------------------------------------------------------------------------
def lire_guide():
    """Les textes anglais des rôles/catégories, lus dans leurs DBC."""
    from mpyq import MPQArchive
    textes = []
    archive = MPQArchive(PATCH_M, listfile=False)
    for nom in ("CharacterCreationClassGuideRoles",
                "CharacterCreationClassGuideSubroles"):
        donnees = archive.read_file("DBFilesClient\\%s.dbc" % nom)
        if not donnees:
            continue
        _, nb, nb_champs, taille, _ = struct.unpack("<4sIIII", donnees[:20])
        debut = 20 + nb * taille
        bloc = donnees[debut:]
        for i in range(nb):
            enreg = struct.unpack_from("<%dI" % nb_champs, donnees,
                                       20 + i * taille)
            # On ne suppose aucune position : tout décalage qui pointe sur du
            # texte lisible est un candidat. Les DBC localisés réservent 16
            # emplacements par champ ; un seul est rempli.
            for decalage in enreg:
                if 0 < decalage < len(bloc):
                    fin = bloc.find(b"\x00", decalage)
                    brut = bloc[decalage:fin if fin != -1 else len(bloc)]
                    try:
                        t = brut.decode("utf-8")
                    except UnicodeDecodeError:
                        continue
                    # Un vrai texte affiché : des lettres et une espace ou un
                    # point. « TANK » ou « ExperienceIconTank » sont des clés.
                    if (len(t) > 2 and re.search(r"[a-z]", t)
                            and not re.match(r"^[A-Za-z_]+$", t)
                            or t in GUIDE_FR):
                        textes.append(t)
    if getattr(archive, "file", None):
        archive.file.close()
    return sorted(set(textes))


def echapper_lua(texte):
    """Un littéral Lua sûr : les retours et guillemets doivent survivre."""
    return (texte.replace("\\", "\\\\").replace('"', '\\"')
            .replace("\r", "\\r").replace("\n", "\\n"))


def lire_fiches():
    """{ étiquette: texte FR } des fiches de classe, si elles sont traduites.

    Source : traductions/glue_lots/*.json (lots produits par les agents) ou
    traductions/glue_classes.json (fusion). Une chaîne dont le format a
    dérivé de l'anglais est écartée : l'écran de création ne pardonne pas.
    """
    import json
    anglais = {}
    chemin_en = os.path.join(BASE, "a_traduire", "glue_classes.json")
    if os.path.exists(chemin_en):
        with open(chemin_en, encoding="utf-8") as f:
            anglais = json.load(f)

    fr = {}
    lots = os.path.join(BASE, "traductions", "glue_lots")
    if os.path.isdir(lots):
        for nom in sorted(os.listdir(lots)):
            if nom.endswith(".json"):
                with open(os.path.join(lots, nom), encoding="utf-8") as f:
                    fr.update(json.load(f))
    # Les reprises à la main passent en dernier : elles priment.
    manuel = os.path.join(BASE, "traductions", "glue_classes_manuel.json")
    if os.path.exists(manuel):
        with open(manuel, encoding="utf-8") as f:
            fr.update(json.load(f))

    retenues, ecartees = {}, []
    for cle, texte in fr.items():
        en = anglais.get(cle)
        if not texte or not en:
            continue
        if not signature_compatible(en, texte):
            ecartees.append(cle)
            continue
        retenues[cle] = texte
    if ecartees:
        print("  ! fiches écartées (format abîmé) : %s"
              % ", ".join(sorted(ecartees)[:5]))
    return retenues


def lire_noms():
    """{ nomEN: nomFR } des classes et races, depuis les DBC + libelles.json.

    Les noms affichés viennent des DBC du client : `GetClassInfo` et
    `GetAvailableRaces` les servent au glue. On ne devine pas la liste — on la
    lit dans les DBC d'Ascension, comme en jeu (outils/extraire_libelles.py).
    """
    import json
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from extraire_libelles import tous_les_noms
    chemin = os.path.join(BASE, "traductions", "libelles.json")
    if not os.path.exists(chemin):
        return {}
    with open(chemin, encoding="utf-8") as f:
        libelles = json.load(f)
    noms = {}
    for fichier, structure in (("ChrClasses_Ascension.dbc", "ChrClasses"),
                               ("ChrRaces_Ascension.dbc", "ChrRaces")):
        complet = os.path.join(SOURCES, "dbc", fichier)
        if not os.path.exists(complet):
            continue
        for en in tous_les_noms(complet, structure):
            fr = libelles.get(en)
            if fr and fr != en:
                noms[en] = fr
    return noms


def lire_zones(journal=print):
    """{ nom anglais: nom français } des zones, pour la liste des personnages.

    Mêmes paires que DB_Zones.lua, mais tirées de la SOURCE
    (traduire_zones.table_zones) : l'écran de connexion ne charge pas les DB
    de l'addon, le Glue doit donc les embarquer lui-même.
    """
    try:
        from traduire_zones import table_zones
    except ImportError:
        journal("  ! traduire_zones introuvable : zones non embarquées,")
        journal("    la liste des personnages restera en anglais.")
        return {}
    try:
        return table_zones()
    except Exception as e:
        journal("  ! zones illisibles (%s) : non embarquées" % str(e)[:60])
        return {}


def construire_selection(zones):
    """Le bloc Lua qui francise la LISTE DES PERSONNAGES (classe et zone).

    Vérifié dans le client (patch-B.MPQ, Interface\\GlueXML\\
    CharacterSelect.lua) : la liste est repeinte par la globale
    UpdateCharacterList() et par CharacterSelect.list:RefreshScrollFrame()
    (défilement) ; chaque bouton porte Content.Name / Content.Info
    (« Classe niveau N », classe enrobée de codes couleur) /
    Content.Location (la zone). Notre fichier étant chargé en 2e ligne du
    toc, AVANT CharacterSelect.lua, une veilleuse pose les enveloppes au
    premier rendu — puis s'éteint. Les pseudos ne sont jamais touchés, et
    rien n'est repeint si le nom est inconnu (jamais de moitié-moitié).
    """
    if not zones:
        return ""
    paires = ['    ["%s"] = "%s",' % (echapper_lua(en), echapper_lua(zones[en]))
              for en in sorted(zones)]
    return "\n".join([
        "",
        "-- ----------------------------------------------------------------",
        "-- Liste des personnages : classe et zone en français.",
        "-- « niveau » vient déjà de CHARACTER_SELECT_INFO (frFR officiel) ;",
        "-- on repeint ici la classe (table AFR_GUIDE ci-dessus) et la zone,",
        "-- APRÈS que le client a peint la liste. Tout est sous condition :",
        "-- si Ascension change son écran, rien ne s'installe et la liste",
        "-- reste anglaise — jamais cassée.",
        "-- ----------------------------------------------------------------",
        "local AFR_ZONES = {",
    ] + paires + [
        "}",
        "",
        "local function AFR_ClasseFrancaise(texte)",
        "    -- « |cff9382c9Knight of Xoroth|r niveau 12 » -> le nom nu,",
        "    -- puis la table des classes. nil si inconnu ou déjà traduit.",
        "    local nu = texte:gsub(\"|c%x%x%x%x%x%x%x%x\", \"\")",
        "    nu = nu:gsub(\"|r\", \"\")",
        "    local classe = nu:match(\"^(.-)%s+niveau%s+%d+$\")",
        "        or nu:match(\"^Niveau%s+%d+%s+(.-)%s*%(\")",
        "        or nu:match(\"^Level%s+%d+%s+(.-)%s*%(Ghost%)$\")",
        "        or nu:match(\"^Level%s+%d+%s+(.-)$\")",
        "    if not classe or classe == \"\" then return nil end",
        "    local fr = AFR_GUIDE and AFR_GUIDE[classe]",
        "    if not fr or fr == classe then return nil end",
        "    return classe, fr",
        "end",
        "",
        "local function AFR_RepeindreInfo(fs)",
        "    if not (fs and fs.GetText and fs.SetText) then return end",
        "    local texte = fs:GetText()",
        "    if not texte then return end",
        "    local en, fr = AFR_ClasseFrancaise(texte)",
        "    if not en then return end",
        "    -- On remplace la classe DANS le texte peint : les codes",
        "    -- couleur qui l'enrobent survivent tels quels.",
        "    local motif = en:gsub(\"%W\", \"%%%0\")",
        "    fs:SetText((texte:gsub(motif, fr:gsub(\"%%\", \"%%%%\"), 1)))",
        "end",
        "",
        "local function AFR_RepeindreZone(fs)",
        "    if not (fs and fs.GetText and fs.SetText) then return end",
        "    local texte = fs:GetText()",
        "    local fr = texte and AFR_ZONES[texte]",
        "    if fr then fs:SetText(fr) end",
        "end",
        "",
        "local function AFR_RepeindreListe()",
        "    -- Boutons du client Ascension : CharacterSelect.list",
        "    -- (ScrollFrame HybridScrollFrame, boutons dans .buttons).",
        "    local liste = type(CharacterSelect) == \"table\"",
        "        and (CharacterSelect.list or CharacterSelect.List)",
        "    local defile = type(liste) == \"table\" and liste.ScrollFrame",
        "    local boutons = type(defile) == \"table\" and defile.buttons",
        "    if type(boutons) == \"table\" then",
        "        for i = 1, #boutons do",
        "            local b = boutons[i]",
        "            local contenu = type(b) == \"table\" and b.Content",
        "            if type(contenu) == \"table\" then",
        "                AFR_RepeindreInfo(contenu.Info)",
        "                AFR_RepeindreZone(contenu.Location)",
        "            end",
        "        end",
        "    end",
        "    -- Boutons du GlueXML 3.3.5 d'origine, si jamais c'est lui.",
        "    for i = 1, 16 do",
        "        local prefixe = \"CharSelectCharacterButton\" .. i",
        "            .. \"ButtonText\"",
        "        local info = _G[prefixe .. \"Info\"]",
        "        local lieu = _G[prefixe .. \"Location\"]",
        "        if not info and not lieu then break end",
        "        AFR_RepeindreInfo(info)",
        "        AFR_RepeindreZone(lieu)",
        "    end",
        "end",
        "",
        "-- Ce fichier est chargé AVANT CharacterSelect.lua (2e ligne du",
        "-- toc) : UpdateCharacterList n'existe pas encore. Une veilleuse",
        "-- attend le premier rendu — tout le glue est alors chargé — pose",
        "-- les enveloppes une seule fois, puis s'éteint.",
        "if type(CreateFrame) == \"function\" then",
        "    local veille = CreateFrame(\"Frame\", nil,",
        "        type(GlueParent) == \"table\" and GlueParent or nil)",
        "    local ecoule = 0",
        "    veille:SetScript(\"OnUpdate\", function(self, dt)",
        "        ecoule = ecoule + (dt or 0.05)",
        "        if ecoule < 0.2 then return end",
        "        ecoule = 0",
        "        if type(UpdateCharacterList) ~= \"function\" then return end",
        "        self:SetScript(\"OnUpdate\", nil)",
        "        local origine = UpdateCharacterList",
        "        UpdateCharacterList = function(...)",
        "            origine(...)",
        "            pcall(AFR_RepeindreListe)",
        "        end",
        "        local liste = type(CharacterSelect) == \"table\"",
        "            and (CharacterSelect.list or CharacterSelect.List)",
        "        if type(liste) == \"table\"",
        "                and type(liste.RefreshScrollFrame) == \"function\" then",
        "            local peindre = liste.RefreshScrollFrame",
        "            liste.RefreshScrollFrame = function(...)",
        "                peindre(...)",
        "                pcall(AFR_RepeindreListe)",
        "            end",
        "        end",
        "        pcall(AFR_RepeindreListe)",
        "    end)",
        "end",
        "",
    ])


def construire_hook(guide_en):
    """Le bloc Lua qui francise rôles et catégories à l'affichage.

    Leur texte vient des DBC du client, pas des GlueStrings : on enveloppe les
    fonctions qui les rendent plutôt que de réécrire ses données. Si le client
    change, l'enveloppe s'efface d'elle-même (le `if`) — jamais d'écran mort.
    """
    table = {}
    for en in guide_en:
        fr = GUIDE_FR.get(en)
        if fr and fr != en:
            table[en] = fr
    table.update(lire_noms())   # noms de classes et de races
    paires = ['    ["%s"] = "%s",'
              % (en.replace('"', '\\"'), table[en].replace('"', '\\"'))
              for en in sorted(table)]
    if not paires:
        return ""
    return "\n".join([
        "",
        "-- ----------------------------------------------------------------",
        "-- Guide de classe : rôles et catégories.",
        "-- Ces textes viennent des DBC du client (CharacterCreationClass-",
        "-- GuideRoles/Subroles.dbc), pas des GlueStrings : on traduit ce que",
        "-- ses fonctions renvoient, sans toucher à ses données. Tout est",
        "-- sous condition : si Ascension change ses fonctions, l'enveloppe",
        "-- ne s'installe pas et l'écran reste anglais — jamais cassé.",
        "-- ----------------------------------------------------------------",
        "local AFR_GUIDE = {",
    ] + paires + [
        "}",
        "",
        "local function AFR_Traduire(t)",
        "    return (t and AFR_GUIDE[t]) or t",
        "end",
        "",
        "if type(C_CharacterCreate) == \"table\" then",
        "    local roleInfo = C_CharacterCreate.GetClassGuideRoleInfo",
        "    if type(roleInfo) == \"function\" then",
        "        C_CharacterCreate.GetClassGuideRoleInfo = function(...)",
        "            local cle, atlas, nom, description = roleInfo(...)",
        "            return cle, atlas, AFR_Traduire(nom),"
        " AFR_Traduire(description)",
        "        end",
        "    end",
        "    local subroleInfo = C_CharacterCreate.GetClassGuideSubroleInfo",
        "    if type(subroleInfo) == \"function\" then",
        "        C_CharacterCreate.GetClassGuideSubroleInfo = function(...)",
        "            local a, cle, b, atlas, nom, description ="
        " subroleInfo(...)",
        "            return a, cle, b, atlas, AFR_Traduire(nom),"
        " AFR_Traduire(description)",
        "        end",
        "    end",
        "end",
        "",
        "-- Noms de classes et de races : le client les tire de ses DBC et les",
        "-- sert par GetClassInfo / GetAvailableRaces. On traduit le nom",
        "-- AFFICHÉ et rien d'autre : le nom anglais interne (2e valeur) sert",
        "-- de clé au client (« RACE_INFO_ »..nom, choix de modèle) — le",
        "-- traduire casserait l'écran.",
        "local function AFR_TraduirePremier(...)",
        "    local n = select(\"#\", ...)",
        "    local r = {}",
        "    for i = 1, n do r[i] = (select(i, ...)) end",
        "    if type(r[1]) == \"string\" then",
        "        r[1] = AFR_GUIDE[r[1]] or r[1]",
        "    end",
        "    return unpack(r, 1, n)",
        "end",
        "",
        "-- GetAvailableRaces renvoie des triplets (nom, nomAnglais, actif).",
        "local function AFR_TraduireTriplets(...)",
        "    local n = select(\"#\", ...)",
        "    local r = {}",
        "    for i = 1, n do r[i] = (select(i, ...)) end",
        "    for i = 1, n, 3 do",
        "        if type(r[i]) == \"string\" then",
        "            r[i] = AFR_GUIDE[r[i]] or r[i]",
        "        end",
        "    end",
        "    return unpack(r, 1, n)",
        "end",
        "",
        "if type(GetClassInfo) == \"function\" then",
        "    local origine = GetClassInfo",
        "    GetClassInfo = function(...)",
        "        return AFR_TraduirePremier(origine(...))",
        "    end",
        "end",
        "",
        "if type(GetAvailableRaces) == \"function\" then",
        "    local origine = GetAvailableRaces",
        "    GetAvailableRaces = function(...)",
        "        return AFR_TraduireTriplets(origine(...))",
        "    end",
        "end",
        "",
    ])


def construire(journal=print):
    rafraichir_sources(journal)
    ouverte = porte_ouverte(journal)
    if ouverte is False:
        journal("  ! ATTENTION : le GlueXML.toc d'Ascension ne réclame plus")
        journal("    Interface\\PTRXML\\PTR.xml. Notre fichier ne sera PAS")
        journal("    chargé et l'écran de création repassera en anglais.")
        journal("    Chercher un autre point d'entrée absent dans leur toc")
        journal("    (Logs\\GlueXML.log liste les « Couldn't open »).")

    anglaises = lire_chaines(GLUE_ASC)
    francaises = lire_chaines(GLUE_FR)

    with open(CREATION_ASC, encoding="utf-8", errors="ignore") as f:
        maison_en = dict(MAISON_RE.findall(f.read()))

    lignes = [
        "-- Ascension FR — écrans de connexion, sélection et création.",
        "-- Fichier produit par traduction/outils/generateur_glue.py.",
        "-- Textes officiels Blizzard frFR ; les chaînes dont Ascension a",
        "-- changé le format restent en anglais (un format() incompatible",
        "-- empêcherait de se connecter).",
        "",
    ]
    posees, ecartees, absentes = 0, [], 0
    # Ce qui est déjà écrit en français officiel : les fiches, plus bas dans
    # le fichier, ne doivent pas le reprendre. Vécu : cinq lignes du chaman
    # (« CLASS_INFO_SHAMAN1 ») existaient en frFR officiel ET dans le DBC
    # d'Ascension ; la fiche, restée anglaise, écrasait le français.
    deja = set()
    for cle in sorted(anglaises):
        en = anglaises[cle]
        fr = francaises.get(cle)
        if fr is None:
            absentes += 1
            continue
        if not signature_compatible(en, fr):
            ecartees.append(cle)
            continue
        lignes.append('%s = "%s";' % (cle, fr))
        deja.add(cle)
        posees += 1

    # Les chaînes maison : leur code garde la nôtre si elle existe déjà.
    lignes.append("")
    lignes.append("-- Chaînes propres à Ascension (leur code écrit"
                  " « X = X or ... » : notre valeur prime).")
    maison_posees, maison_inconnues = 0, []
    for cle in sorted(maison_en):
        fr = MAISON_FR.get(cle)
        if not fr:
            maison_inconnues.append(cle)
            continue
        if not signature_compatible(maison_en[cle], fr.replace("\\n", "\n")):
            ecartees.append(cle)
            continue
        lignes.append('%s = "%s";' % (cle, fr))
        maison_posees += 1
    disparues = sorted(set(MAISON_FR) - set(maison_en))

    # --- Fiches techniques de classe (GlobalStrings.dbc d'Ascension) -------
    # Le client pose ces globales depuis son DBC maison ; CharacterCreate.lua
    # les lit au survol (`_G["CLASS_COMBAT_STYLE_"..classe..n]`). Notre
    # fichier étant chargé en 2e ligne du toc, nos valeurs sont en place
    # avant le premier survol. Étiquettes = clés internes (WILDWALKER, pas
    # « Primalist ») : on ne traduit que les valeurs.
    fiches = lire_fiches()
    reprises = sorted(set(fiches) & deja)
    for cle in reprises:
        del fiches[cle]        # le français officiel a la priorité
    if fiches:
        lignes.append("")
        lignes.append("-- Fiches techniques de classe (écran de création).")
        for cle in sorted(fiches):
            lignes.append('%s = "%s";' % (cle, echapper_lua(fiches[cle])))
    if reprises:
        journal("Fiches laissées au frFR officiel : %d (%s)"
                % (len(reprises), ", ".join(reprises[:3])))

    guide_en = lire_guide()
    lignes.append(construire_hook(guide_en))
    guide_inconnus = [t for t in guide_en if t not in GUIDE_FR]

    # La liste des personnages : classes (table AFR_GUIDE ci-dessus) et
    # zones (mêmes paires que DB_Zones.lua, embarquées ici car l'écran de
    # connexion ne charge pas les DB de l'addon).
    zones = lire_zones(journal)
    lignes.append(construire_selection(zones))

    journal("Chaînes officielles traduites : %d / %d" % (posees, len(anglaises)))
    journal("Chaînes maison traduites      : %d / %d"
            % (maison_posees, len(maison_en)))
    journal("Rôles/catégories traduits     : %d / %d"
            % (len(guide_en) - len(guide_inconnus), len(guide_en)))
    journal("Fiches de classe traduites    : %d" % len(fiches))
    journal("Zones de la liste des persos  : %d embarquées" % len(zones))
    if ecartees:
        journal("Écartées (format changé par Ascension) : %d — %s"
                % (len(ecartees), ", ".join(sorted(ecartees)[:6])))
    if absentes:
        journal("Sans équivalent officiel : %d" % absentes)
    if maison_inconnues:
        journal("! chaînes maison NOUVELLES, à traduire : %s"
                % ", ".join(maison_inconnues))
    if disparues:
        journal("! chaînes maison disparues de leur code : %s"
                % ", ".join(disparues))
    if guide_inconnus:
        journal("! textes de guide sans traduction : %s"
                % ", ".join(guide_inconnus[:6]))

    return "\n".join(lignes) + "\n", posees + maison_posees


def main():
    contenu, total = construire()
    if not {"--ecrire", "--libre", "--porte"} & set(sys.argv):
        print()
        print("Rapport seul. Ensuite :")
        print("  --porte   -> %s" % PORTE_XML)
        print("               (le point d'entrée que le client réclame)")
        print("  --libre   -> %s" % LIBRE)
        print("               (essai du 17/07 : sans effet)")
        print("  --ecrire  -> %s" % ARCHIVE)
        print("               (le launcher SUPPRIME cette archive)")
        return 0
    if total < 500:
        print("\n! seulement %d chaînes : rien n'est écrit" % total)
        return 1

    if "--porte" in sys.argv:
        os.makedirs(os.path.dirname(PORTE_XML), exist_ok=True)
        with open(PORTE_XML, "w", encoding="utf-8", newline="\n") as f:
            f.write(GABARIT_XML)
        with open(PORTE_LUA, "w", encoding="utf-8", newline="\n") as f:
            f.write(contenu)
        print()
        print("Écrits : %s" % os.path.dirname(PORTE_XML))
        print("   PTR.xml            (le point d'entrée réclamé par le client)")
        print("   AscensionFR_Glue.lua  (%.1f Ko, %d chaînes)"
              % (len(contenu.encode("utf-8")) / 1024.0, total))
        print()
        print("Relancez le jeu. Deux façons de savoir :")
        print("  - l'écran de création est en français ;")
        print("  - Logs\\GlueXML.log ne dit plus « Couldn't open"
              " Interface\\PTRXML\\PTR.xml ».")
        print("Pour tout annuler : supprimer le dossier Interface\\PTRXML.")
        return 0

    if "--libre" in sys.argv:
        os.makedirs(os.path.dirname(LIBRE), exist_ok=True)
        with open(LIBRE, "w", encoding="utf-8", newline="\n") as f:
            f.write(contenu)
        print()
        print("Fichier libre écrit : %s (%.1f Ko)"
              % (LIBRE, len(contenu.encode("utf-8")) / 1024.0))
        print("Essai : le client lit-il le glue depuis le disque ? Relancez")
        print("le jeu. Pour tout annuler : supprimer ce seul fichier.")
        return 0

    if mpq_ecrire is None:
        print("! outils/mpq_ecrire.py est absent du dépôt : impossible "
              "d'écrire l'archive.")
        print("  Le reste du module fonctionne (c'est la seule fonction qui "
              "en dépend).")
        return 1

    taille = mpq_ecrire.ecrire(ARCHIVE, {INTERNE: contenu.encode("utf-8")})
    print()
    print("Archive écrite : %s (%.1f Ko)" % (ARCHIVE, taille / 1024.0))
    print("! Le launcher l'a supprimée lors de l'essai du 17/07 (cf. README).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
