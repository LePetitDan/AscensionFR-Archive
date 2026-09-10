# -*- coding: utf-8 -*-
"""
Traduit les lignes « Utiliser : Teaches you how to… » des recettes, montures
et mascottes.

Le problème : la ligne affichée vient du SORT attaché à l'objet, or ces
sorts-là n'ont aucune description en base — rien à quoi s'aligner, donc
l'anglais reste. L'objet, lui, est traduit depuis longtemps.

La solution : donner au sort un second modèle (aura) fait du texte anglais de
l'objet et de sa traduction. L'addon essaie CHAQUE sort de l'objet : peu
importe lequel le client a réellement utilisé, l'alignement réussit.

Piège évité : tous ces objets partagent un sort d'apprentissage GÉNÉRIQUE
(483, 55884…). Y attacher un texte ferait afficher « Vous apprend à préparer
un Boudin » sur toutes les montures du jeu. On ne vise que le sort spécifique,
et on écarte tout sort réclamé par deux textes différents.

Usage : python outils/corriger_recettes.py [--ecrire]
"""
import io
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDON = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
         r"\AscensionFR")
CORRECTIONS = os.path.join(ADDON, "DB", "DB_SortsCorrections.lua")

# Sorts d'apprentissage communs à des milliers d'objets : à ne JAMAIS viser.
GENERIQUES = {"0", "483", "55884"}
MOTIF = re.compile(r"^\s*Teaches you how to ", re.I)


def charger(chemin):
    return json.load(io.open(chemin, encoding="utf-8")) \
        if os.path.isfile(chemin) else {}


def desechapper_lua(texte):
    return (texte.replace('\\"', '"').replace("\\n", "\n")
                 .replace("\\\\", "\\"))


# Le strict nécessaire pour exécuter une base (plate OU paresseuse) hors du
# jeu : AscensionFR.Paresseux compile chaque seau au premier accès, comme
# Core.lua. IMPÉRATIVEMENT lua51 (le client) — et locale C d'abord, comme
# partout (piège du lot 14 : lupa hors jeu avec une locale française casse
# les nombres à virgule).
_AMORCE_LUA = r"""
AscensionFR = { DB = {} }
function AscensionFR.Paresseux(M, taille)
  local seaux = {}
  return setmetatable({}, { __index = function(_, id)
    if type(id) ~= "number" then return nil end
    local numero = math.floor(id / taille)
    local seau = seaux[numero]
    if seau == nil then
      local source = M[numero]
      if source == nil then return nil end
      seau = assert(loadstring("return {" .. source .. "}"))()
      seaux[numero] = seau
    end
    return seau[id]
  end })
end
"""


def francais_des_objets(idents):
    """Le français FINAL des objets demandés, lu dans la base générée EN LA
    REJOUANT AU MOTEUR (lupa.lua51).

    On ne peut pas se contenter de traductions/objets.json : les objets
    classiques (recettes de cuisine, plans de forge…) tiennent leur français
    des données officielles Blizzard, pas de nos traductions IA. C'est la
    base générée qui fusionne les deux — c'est donc elle qui fait foi.

    RÉPARÉ le 28/07/2026 (bloc 2e) : l'ancien motif ligne à ligne
    « DB[id]={…} » ne lisait que le format PLAT. Depuis le passage au
    paresseux (21/07), il ne trouvait plus RIEN — l'outil annonçait
    « À AJOUTER : 0 », rendait 0, et mentait en silence. Le moteur rejoué
    lit les deux formats, et un résultat vide est un ÉCHEC BRUYANT."""
    import locale
    locale.setlocale(locale.LC_ALL, "C")
    import lupa.lua51 as lupa_mod
    chemin = os.path.join(ADDON, "DB", "DB_Objets.lua")
    lua = lupa_mod.LuaRuntime()
    lua.execute(_AMORCE_LUA)
    lua.execute(io.open(chemin, encoding="utf-8").read())
    objets = lua.globals().AscensionFR.DB.Objets
    textes = {}
    for ident in idents:
        try:
            entree = objets[int(ident)]
        except (ValueError, TypeError):
            continue
        if entree is not None:
            d = entree["D"]
            if d:
                textes[str(ident)] = d
    if not textes and idents:
        print("STOP — la lecture de DB_Objets.lua au moteur n'a rendu AUCUN "
              "texte")
        print("pour %d identifiants demandés : le format de la base a "
              "encore changé." % len(idents))
        print("Répare francais_des_objets() — ne crois PAS un « 0 à "
              "ajouter » dans cet état.")
        sys.exit(2)
    return textes


def echapper_lua(texte):
    texte = texte.replace("\\", "\\\\").replace('"', '\\"')
    return (texte.replace("\r\n", "\\n").replace("\r", "\\n")
                 .replace("\n", "\\n"))


def main():
    anglais = {}
    # Tous les royaumes en base (Vol'jin, Darkmoon…), puis fusion joueurs, puis
    # Rexxar prioritaire — même logique que generateur_db.
    dossier_ex = os.path.join(BASE, "extraits")
    if os.path.isdir(dossier_ex):
        for royaume in sorted(os.listdir(dossier_ex)):
            if royaume == "rexxar" or not os.path.isdir(
                    os.path.join(dossier_ex, royaume)):
                continue
            anglais.update(charger(os.path.join(dossier_ex, royaume,
                                                "objets.json")))
    anglais.update(charger(os.path.join(BASE, "rapports", "caches", "fusion",
                                        "objets.json")))
    anglais.update(charger(os.path.join(BASE, "extraits", "rexxar",
                                        "objets.json")))

    # D'abord la courte liste des candidats (« Teaches you how to… ») : la
    # base des objets ne se rejoue au moteur que pour EUX, pas pour les
    # centaines de milliers d'entrées.
    candidats = {ident: donnees for ident, donnees in anglais.items()
                 if MOTIF.match(((donnees or {}).get("Description")
                                 or "").strip())}
    francais = francais_des_objets(list(candidats))

    deja_corriges = set(re.findall(
        r"aura\((\d+),", io.open(CORRECTIONS, encoding="utf-8").read()))

    # 1) Rassembler les couples (sort spécifique -> textes), en repérant les
    #    sorts réclamés par deux textes différents.
    revendique = {}
    for ident, donnees in candidats.items():
        en = ((donnees or {}).get("Description") or "").strip()
        fr = francais.get(ident)
        if not fr or fr == en:
            continue                       # pas encore traduit : on repassera
        for entree in (donnees.get("Spells") or []):
            sid = str(entree[0] if isinstance(entree, list) else entree)
            if sid in GENERIQUES:
                continue
            revendique.setdefault(sid, set()).add((en, fr))

    # 2) Ne garder que les sorts sans ambiguïté et pas déjà corrigés.
    lignes, ambigus, connus = [], 0, 0
    for sid, textes in sorted(revendique.items(), key=lambda kv: int(kv[0])):
        if len(textes) > 1:
            ambigus += 1
            continue
        if sid in deja_corriges:
            connus += 1
            continue
        en, fr = textes.pop()
        lignes.append('aura(%s, "%s", "%s")'
                      % (sid, echapper_lua(en), echapper_lua(fr)))

    print("Sorts spécifiques repérés   : %d" % len(revendique))
    print("  déjà corrigés             : %d" % connus)
    print("  écartés (texte ambigu)    : %d" % ambigus)
    print("  À AJOUTER                 : %d" % len(lignes))
    print()
    for ligne in lignes[:6]:
        print("  " + ligne[:120])
    if len(lignes) > 6:
        print("  … et %d autres" % (len(lignes) - 6))

    if not lignes:
        return 0
    if "--ecrire" not in sys.argv:
        print("\nAPERÇU seulement. Ajoute --ecrire pour appliquer.")
        return 0

    with io.open(CORRECTIONS, "a", encoding="utf-8") as f:
        f.write("\n-- Recettes, montures et mascottes : la ligne « Utiliser : »"
                "\n-- vient du sort, qui n'avait aucun modèle (corriger_recettes.py).\n")
        f.write("\n".join(lignes) + "\n")
    print("\n%d correction(s) ajoutée(s)." % len(lignes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
