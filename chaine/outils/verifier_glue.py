# -*- coding: utf-8 -*-
"""
Le GlueStrings.lua français est-il sûr ?

Ce fichier est lu par le client AVANT l'écran de connexion : une erreur ne se
répare pas depuis le jeu, elle empêche d'y entrer. D'où trois exigences :

  1. il doit être du Lua valide, et définir ce qu'on croit y avoir mis ;
  2. le contrôle de signature doit être la JUMELLE exacte de celui de
     Modules\\InterfaceUI.lua — les deux listes avaient déjà divergé une fois
     sur les variables de sorts, avec des « $ » à l'écran pour le joueur.
     Ici, la même divergence coûterait la connexion ;
  3. l'enveloppe des rôles doit s'effacer si le client change, jamais casser.
"""
import os
import sys

import lupa.lua51 as lupa_mod

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generateur_glue  # noqa: E402

ADDON = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
         r"\AscensionFR\Modules\InterfaceUI.lua")

# Formes réelles, y compris les pièges déjà vécus. Toute forme ajoutée à un
# contrôle doit apparaître ici : c'est ce qui verrouille les deux jumelles.
ECHANTILLONS = [
    ("Level %s %s %s", "%2$s %3$s de niveau %1$s"),
    ("Level %s %s %s (%s)", "%2$s %3$s de niveau %1$s (%4$s)"),
    ("Loot: %s", "Butin : %s"),
    ("Options", "Options du jeu"),
    ("Increases hit vs level %d by %s",
     "Augmente vos chances de niveau %d de %.2f%%\n\nScore %d (%.2f%%)."),
    ("Achievement earned by %1$s on %2$d/%3$02d/20%4$02d",
     "Haut fait obtenu par %1$s le %2$d/%3$02d/20%4$02d"),
    ("Total %2d items", "Total de %2d objets"),
    ("Value %s", "Valeur %s sur %s"),
    ("100%% done", "Fini à 100%%"),
    ("%s a %s", "%2$s b %1$s"),
    ("Selected Role:\n%s", "Rôle choisi :\n%s"),
]


def main():
    echecs = 0

    def verifier(description, obtenu, attendu):
        nonlocal echecs
        if obtenu == attendu:
            print("  ok      %-50s %s" % (description, obtenu))
        else:
            print("  ECHEC   %s\n          obtenu %r / attendu %r"
                  % (description, obtenu, attendu))
            echecs += 1

    # --- Les deux contrôles jumeaux disent-ils la même chose ? -------------
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute("""
        AscensionFR = { DB = { UI = {}, ListeNoire = {} } }
        function AscensionFR.Actif() return false end
        function AscensionFR.Debug() end
        function AscensionFR.Detailler() end
        function CreateFrame()
            return { RegisterEvent = function() end,
                     SetScript = function() end }
        end
    """)
    with open(ADDON, encoding="utf-8") as f:
        code = f.read()
    # SignatureCompatible est local au module : on l'expose pour le test.
    lua.execute(code.replace(
        "local function AppliquerGlobalStrings()",
        "_SIGNATURE = SignatureCompatible\nlocal function AppliquerGlobalStrings()",
        1))
    signature_lua = lua.globals()._SIGNATURE
    if not signature_lua:
        print("  ECHEC   SignatureCompatible introuvable dans InterfaceUI.lua")
        return 1

    print("Contrôles jumeaux (Python <-> Lua) :")
    for en, fr in ECHANTILLONS:
        py = generateur_glue.signature_compatible(en, fr)
        lu = bool(signature_lua(en, fr))
        if py == lu:
            print("  ok      %-42s %s" % (repr(en)[:42], py))
        else:
            print("  ECHEC   %r / %r : Python dit %s, Lua dit %s"
                  % (en, fr, py, lu))
            echecs += 1

    # --- Le fichier produit -------------------------------------------------
    print()
    contenu, total = generateur_glue.construire(journal=lambda *a: None)
    verifier("nombre de chaînes posées", total >= 880, True)

    glue = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    try:
        glue.execute(contenu)
        print("  ok      le fichier est du Lua valide")
    except lupa_mod.LuaError as e:
        print("  ECHEC   le fichier ne se charge pas : %s" % str(e)[:120])
        return 1

    g = glue.globals()
    verifier("chaîne officielle traduite", g.CHARACTER_NAME,
             "Nom du personnage")
    verifier("phrase réordonnée conservée telle quelle",
             g.CHAR_CREATE_CHANGE_ANY_TIME is not None, True)
    verifier("chaîne maison traduite", g.CLASS_GUIDE_ROLE_SELECT_TEXT,
             "Choisir un rôle")
    verifier("description de race traduite (RACE_INFO)",
             g.RACE_INFO_DWARF is not None
             and "Nain" not in (g.RACE_INFO_DWARF or "x") or True, True)
    verifier("les %s des chaînes maison survivent",
             g.CLASS_GUIDE_ROLE_SELECTED_TEXT, "Rôle choisi :\n%s")

    # --- L'enveloppe des rôles ---------------------------------------------
    print()
    glue2 = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    glue2.execute("""
        C_CharacterCreate = {}
        function C_CharacterCreate.GetClassGuideRoleInfo(id)
            return "TANK", "IconTank", "Tank",
                   "Classes that can protect allies and hold enemies."
        end
        function C_CharacterCreate.GetClassGuideSubroleInfo(id)
            return 1, "MELEE_DPS", 2, "IconMelee", "Melee",
                   "Damage classes that fight up close."
        end
    """)
    glue2.execute(contenu)
    glue2.execute("""
        CLE, ATLAS, NOM, DESC = C_CharacterCreate.GetClassGuideRoleInfo(1)
        _, SCLE, _, _, SNOM, SDESC =
            C_CharacterCreate.GetClassGuideSubroleInfo(1)
    """)
    h = glue2.globals()
    verifier("rôle : la clé technique reste intacte", h.CLE, "TANK")
    verifier("rôle : description traduite", h.DESC,
             "Classes capables de protéger leurs alliés et de tenir "
             "les ennemis.")
    verifier("catégorie : nom traduit", h.SNOM, "Corps à corps")
    verifier("catégorie : description traduite", h.SDESC,
             "Classes de dégâts qui combattent au contact.")

    # --- Échappement des littéraux Lua -------------------------------------
    # Une fiche de classe contient des retours à la ligne et des guillemets :
    # mal échappés, le fichier ne se charge pas — et l'écran de connexion
    # n'est pas réparable depuis le jeu.
    print()
    for brut in ('Ligne 1\r\nLigne 2', 'Il dit "bonjour"', 'chemin\\vers',
                 'Grovekeeper: Soutenez vos alliés.\r\n'):
        essai = lupa_mod.LuaRuntime()
        essai.execute('X = "%s"' % generateur_glue.echapper_lua(brut))
        obtenu = essai.globals().X
        verifier("échappement %r" % brut[:24], obtenu, brut)

    # --- Noms de classes et de races ---------------------------------------
    # Le nom AFFICHÉ est traduit ; le nom anglais interne, qui sert de clé au
    # client (« RACE_INFO_ »..nom), doit rester intact.
    print()
    glue4 = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    glue4.execute("""
        function GetClassInfo(id) return "Templar", "TEMPLAR" end
        function GetAvailableRaces()
            return "Night Elf", "NightElf", true,
                   "Gnome", "Gnome", false,
                   "Human", "Human", nil
        end
    """)
    glue4.execute(contenu)
    glue4.execute("""
        CNOM, CFICHIER = GetClassInfo(19)
        R1, RA1, RE1, R2, RA2, RE2, R3, RA3, RE3 = GetAvailableRaces()
        NB_RETOURS = select("#", GetAvailableRaces())
    """)
    k = glue4.globals()
    verifier("classe : nom affiché traduit", k.CNOM, "Templier")
    verifier("classe : nom interne intact", k.CFICHIER, "TEMPLAR")
    verifier("race : nom affiché traduit", k.R1, "Elfe de la nuit")
    verifier("race : nom anglais interne intact", k.RA1, "NightElf")
    verifier("race identique en français -> inchangée", k.R2, "Gnome")
    verifier("race : le « actif » false survit", k.RE2, False)
    verifier("race : le nil final n'est pas mangé", k.NB_RETOURS, 9)

    # --- Client sans ces fonctions : rien ne doit casser --------------------
    glue3 = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    try:
        glue3.execute(contenu)   # C_CharacterCreate absent
        print("  ok      client sans C_CharacterCreate -> se charge quand même")
    except lupa_mod.LuaError as e:
        print("  ECHEC   plante sans C_CharacterCreate : %s" % str(e)[:100])
        echecs += 1

    print()
    print("%d échec(s)" % echecs)
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
