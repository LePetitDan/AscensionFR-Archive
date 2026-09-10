# -*- coding: utf-8 -*-
"""
Test du mécanisme de résolution des variables de sorts (Modules\\Sorts.lua).

Vérifie qu'on sait retrouver les valeurs calculées par le client dans
l'info-bulle anglaise affichée, puis les replacer dans le texte français —
et qu'on renonce proprement (nil) quand l'alignement échoue, plutôt que
d'afficher un texte contenant des « $s1 ».
"""
import sys

import lupa.lua51 as lupa_mod

ADDON = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
         r"\AscensionFR\Modules\Sorts.lua")

STUBS = """
AscensionFR = { DB = { Sorts = {} } }
function AscensionFR.Debug() end
-- La commande /afrformat (essai C_Format, 23/07) s'enregistre au chargement.
SlashCmdList = {}
function CreateFrame()
    return { RegisterEvent = function() end, SetScript = function() end,
             HookScript = function() end }
end
"""

# (description, modèle FR, modèle EN, info-bulle EN affichée, attendu)
CAS = [
    ("variable simple",
     "Choque un ennemi, infligeant $s1 dégâts de Nature en $d.",
     "Shock an enemy for $s1 Nature damage over $d.",
     "Shock an enemy for 15 Nature damage over 6 sec.",
     "Choque un ennemi, infligeant 15 dégâts de Nature en 6 sec."),
    ("ordre des variables inversé en français",
     "Pendant $d, augmente la puissance d'attaque de $s1.",
     "Increases attack power by $s1 for $d.",
     "Increases attack power by 250 for 30 sec.",
     "Pendant 30 sec, augmente la puissance d'attaque de 250."),
    ("référence à un autre sort",
     "Soigne $64843s2 alliés dans $64844a1 mètres.",
     "Heals $64843s2 allies within $64844a1 yards.",
     "Heals 5 allies within 30 yards.",
     "Soigne 5 alliés dans 30 mètres."),
    ("aucune variable",
     "Vous êtes furtif.", "You are stealthed.", "You are stealthed.",
     "Vous êtes furtif."),
    ("variable répétée",
     "Inflige $s1 dégâts puis encore $s1 dégâts.",
     "Deals $s1 damage then $s1 more damage.",
     "Deals 40 damage then 40 more damage.",
     "Inflige 40 dégâts puis encore 40 dégâts."),
    ("calcul ${}",
     "Rayon de ${$a1/2} mètres.",
     "Radius of ${$a1/2} yards.",
     "Radius of 4 yards.",
     "Rayon de 4 mètres."),
    ("pourcentage collé à la variable",
     "Augmente les chances de critique de $s1%.",
     "Increases critical strike chance by $s1%.",
     "Increases critical strike chance by 5%.",
     "Augmente les chances de critique de 5%."),
    ("valeur multi-mots, unités francisées",
     "Dure $d.", "Lasts $d.", "Lasts 1 hour 30 min.",
     "Dure 1 heure 30 min."),
    ("unités : secondes et mètres",
     "Dure $d dans $a1.", "Lasts $d within $a1.",
     "Lasts 30 seconds within 8 yards.",
     "Dure 30 secondes dans 8 mètres."),
    # Cas vécu : les DBC écrivent \r\n, mais la base avait perdu le \r.
    # L'alignement échouait sur un caractère invisible et la description
    # entière restait en anglais (« modèle non aligné, anglais conservé »).
    ("fins de ligne différentes entre le modèle et l'affiché",
     "Libère un Brise-serment, rendant ${$m2} PV.\n\nConsomme vos Serments.",
     "Unleash a healing Oath Breaker, restoring ${$m2} health."
     "\r\n\r\nConsumes your Oaths.",
     "Unleash a healing Oath Breaker, restoring 42 health."
     "\r\n\r\nConsumes your Oaths.",
     "Libère un Brise-serment, rendant 42 PV.\n\nConsomme vos Serments."),
    ("fins de ligne en \\r\\n des deux côtés",
     "Rend ${$m2} PV.\r\nPuis encore $s1.",
     "Restores ${$m2} health.\r\nThen $s1 more.",
     "Restores 42 health.\r\nThen 7 more.",
     "Rend 42 PV.\r\nPuis encore 7."),
    ("modèle avec codes de couleur et calcul (cas réel du sort 803373)",
     "Libère un |cffffffffBrise-serment|r soignant, rendant "
     "${$m2+0+$STA*0.25+$SP*0.3} PV à un allié.",
     "Unleash a healing |cffffffffOath Breaker|r, restoring "
     "${$m2+0+$STA*0.25+$SP*0.3} health to an ally.",
     "Unleash a healing |cffffffffOath Breaker|r, restoring "
     "268 health to an ally.",
     "Libère un |cffffffffBrise-serment|r soignant, rendant 268 PV à un allié."),
]

# Cas où l'alignement doit échouer : on préfère l'anglais à un texte cassé.
CAS_REJET = [
    ("info-bulle sans rapport",
     "Inflige $s1 dégâts.", "Deals $s1 damage.", "Completely different!"),
    ("variable française absente du modèle anglais",
     "Inflige $s1 sur $d.", "Deals $s1 damage.", "Deals 10 damage."),
    # Cas vécu : la protection du traducteur avait divergé des motifs de
    # l'addon, le traducteur automatique avait détruit « $<percent> », et le
    # joueur voyait un « $ » à la place d'un chiffre. Le garde-fou compte les
    # « $ » : le français ne peut pas en avoir plus que l'anglais résolu.
    ("variable abîmée par le traducteur -> jamais de « $ » affiché",
     "Inflige $s1 dégâts et $ % de plus.",
     "Deals $s1 damage and $<percent>% more.",
     "Deals 40 damage and 15% more."),
    ("« $ » nu resté dans le texte français",
     "Frappe pour $ dégâts.", "Strikes for $s1 damage.",
     "Strikes for 40 damage."),
    ("info-bulle anglaise non résolue",
     "Inflige $s1 dégâts.", "Deals $s1 damage.", None),
]


def main():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(STUBS)
    with open(ADDON, encoding="utf-8") as f:
        lua.execute(f.read())
    traduire = lua.globals().AscensionFR.TraduireTexteSort

    echecs = 0
    print("=== Résolution des variables ===")
    for description, fr, en, affiche, attendu in CAS:
        obtenu = traduire(fr, en, affiche)
        if obtenu == attendu:
            print("  ok      %-38s %s" % (description, obtenu))
        else:
            print("  ECHEC   %-38s" % description)
            print("          obtenu  : %r" % obtenu)
            print("          attendu : %r" % attendu)
            echecs += 1

    print()
    print("=== Renoncement propre (doit valoir nil) ===")
    for description, fr, en, affiche in CAS_REJET:
        obtenu = traduire(fr, en, affiche)
        if obtenu is None:
            print("  ok      %-38s rejeté" % description)
        else:
            print("  ECHEC   %-38s a produit %r" % (description, obtenu))
            echecs += 1

    print()
    print("%d échec(s)" % echecs)
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
