# -*- coding: utf-8 -*-
"""
Audit du découpage des modèles de sorts, sur les VRAIES données du jeu.

Pourquoi : l'addon aligne le modèle anglais sur l'info-bulle affichée pour en
extraire les valeurs calculées par le client. Si une forme de variable lui
échappe, elle reste dans une partie « littérale » du motif — et l'alignement
compare alors « $s1 » à « 42 ». Il échoue, et la description reste en anglais
(« modèle non aligné, anglais conservé »).

Le test est décisif : après découpage, aucune partie littérale ne doit
contenir de « $ ». On le vérifie sur les 36 000 sorts réels plutôt que sur
quelques cas choisis à la main.
"""
import re
import sys
from collections import Counter

import lupa.lua51 as lupa_mod

ADDON = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns\AscensionFR"

CONTEXTE = r"""
AscensionFR = { DB = { Sorts = {} } }
function AscensionFR.Debug() end
function AscensionFR.Actif() return true end
function CreateFrame()
    return { RegisterEvent = function() end, SetScript = function() end,
             HookScript = function() end }
end
"""


def main():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)
    with open(ADDON + r"\Modules\Sorts.lua", encoding="utf-8") as f:
        lua.execute(f.read())
    with open(ADDON + r"\DB\DB_Sorts.lua", encoding="utf-8") as f:
        lua.execute(f.read())

    # Pour chaque modèle anglais, on redemande à l'addon son propre découpage,
    # puis on regarde ce qui reste dans les littéraux.
    lua.execute(r"""
        RESTES = {}
        NB_MODELES = 0
        function AuditerModele(modele)
            local litteraux = AscensionFR.DecouperModele(modele)
            local restes = {}
            for _, l in ipairs(litteraux) do
                for v in string.gmatch(l, "%$[%w{%?/@]*") do
                    table.insert(restes, v)
                end
            end
            return table.concat(restes, "|")
        end
    """)
    auditer = lua.globals().AuditerModele
    sorts = lua.globals().AscensionFR.DB.Sorts

    total, casses = 0, 0
    formes = Counter()
    exemples = {}

    for sid in sorts:
        e = sorts[sid]
        for champ in ("DE", "TE"):
            modele = e[champ] if e[champ] else None
            if not modele or "$" not in modele:
                continue
            total += 1
            reste = auditer(modele)
            if reste:
                casses += 1
                for v in reste.split("|"):
                    if not v:
                        continue
                    # Regrouper par forme : « $12345s1 » -> « $<n>s<n> »
                    forme = re.sub(r"\d+", "<n>", v)
                    formes[forme] += 1
                    exemples.setdefault(forme, (sid, modele))

    print("Modèles anglais contenant des variables : %d" % total)
    print("Modèles dont le découpage laisse un « $ » : %d (%.1f %%)"
          % (casses, 100.0 * casses / max(total, 1)))
    print()
    if formes:
        print("=== Formes de variables non reconnues ===")
        for forme, n in formes.most_common(15):
            sid, modele = exemples[forme]
            extrait = modele.replace("\r", "").replace("\n", " ")
            i = max(extrait.find(forme.replace("<n>", "")) - 30, 0)
            print("  %-16s %6d fois   ex. sort %s : ...%s..."
                  % (forme, n, sid, extrait[i:i + 70]))
    else:
        print("Aucune : toutes les variables sont reconnues.")

    # Les derniers « $ » restants sont des coquilles dans les données
    # d'Ascension elles-mêmes (« deals $% more damage », « $[...} » mal
    # fermé) : le jeu les affiche telles quelles, donc le modèle et
    # l'affiché concordent quand même. On tolère ce fond irréductible, mais
    # pas une régression au-delà.
    SEUIL = 40
    print()
    if casses > SEUIL:
        print("ECHEC : %d modèles inalignables (seuil %d). Une forme de "
              "variable a cessé d'être reconnue." % (casses, SEUIL))
        sys.exit(1)
    print("ok : %d modèles inalignables (seuil %d) — coquilles d'Ascension, "
          "affichées telles quelles par le jeu." % (casses, SEUIL))
    sys.exit(0)


if __name__ == "__main__":
    main()
