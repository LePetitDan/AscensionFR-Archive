# -*- coding: utf-8 -*-
"""
moissonner_echecs.py — corrige les sorts en échec SANS attendre les rapports.

Le journal des échecs d'alignement vit déjà sur la machine, dans les
SavedVariables (AscensionFRSaved.EchecsAlignement.S : id -> texte anglais
RÉELLEMENT affiché). C'est la même matière que les rapports Discord, en
circuit court : on la lit directement, on traduit, on écrit les corrections
aura() — exactement ce que fait ingerer_rapport.py, sans le détour par le
salon. Utile pour la machine de Dan ; les joueurs, eux, passent toujours par
les rapports.

Usage : python outils/moissonner_echecs.py [--dry]

ATTENTION : le dédoublonnage garde 2 faux positifs connus (680387, 801904)
— ils se re-signalent à chaque passage malgré une correction à jour, cause
non élucidée (divergence d'échappement probable). RELIRE le bloc ajouté
après chaque passage ; le 20/07 ils ont écrasé du bon français par du
machine avant d'être repérés.
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ingerer_rapport as ir  # noqa: E402  (échappement, chemins…)
from traduire_gisement import traduire  # noqa: E402


def deslua(s):
    return (s.replace('\\"', '"').replace("\\r", "\r")
            .replace("\\n", "\n").replace("\\\\", "\\"))


def textes_deja_corriges():
    """{id: {modèles anglais déjà en correction}}.

    Un id « déjà corrigé » peut ÊTRE ENCORE EN ÉCHEC : si Ascension a
    reformulé le texte, la correction est périmée et le journal le sait —
    c'est même sa raison d'être (il ne garde que les échecs COURANTS).
    Sauter l'id entier laissait ces périmés en anglais pour toujours. On ne
    saute donc que si le texte vivant est déjà l'un des modèles corrigés.
    """
    if not os.path.exists(ir.CORRECTIONS):
        return {}
    contenu = io.open(ir.CORRECTIONS, encoding="utf-8").read()
    par_id = {}
    for m in re.finditer(r'^DB\[(\d+)\]=\{(.*)$', contenu, re.M):
        for t in re.findall(r'DE2?="((?:\\.|[^"\\])*)"', m.group(2)):
            par_id.setdefault(m.group(1), set()).add(deslua(t))
    for m in re.finditer(r'^aura\((\d+),\s*"((?:\\.|[^"\\])*)"',
                         contenu, re.M):
        par_id.setdefault(m.group(1), set()).add(deslua(m.group(2)))
    return par_id

WTF = os.path.join(r"D:\AscensionFR\WOW_Priv\resources\ascension-live", "WTF")


def lire_echecs_locaux():
    """{id: texte anglais affiché} depuis les SavedVariables de tous les
    comptes de la machine."""
    import lupa.lua51 as lupa_mod
    echecs = {}
    for racine, _, fichiers in os.walk(WTF):
        for nom in fichiers:
            if nom != "AscensionFR.lua" or "SavedVariables" not in racine:
                continue
            try:
                lua = lupa_mod.LuaRuntime()
                with io.open(os.path.join(racine, nom),
                             encoding="utf-8", errors="ignore") as f:
                    lua.execute(f.read())
                saved = lua.globals().AscensionFRSaved
                journal = saved and saved.EchecsAlignement
                sorts = journal and journal.S
                if not sorts:
                    continue
                for id_, texte in sorts.items():
                    if hasattr(texte, "values"):     # table de lignes
                        texte = "\n".join(str(v) for v in texte.values())
                    echecs[str(int(id_))] = str(texte)
            except Exception as e:
                print("  ! lecture impossible (%s) : %s" % (nom, e))
    return echecs


def main():
    dry = "--dry" in sys.argv
    echecs = lire_echecs_locaux()
    # La ligne de durée (« 10 minutes restantes ») est collée au texte par le
    # client au moment de la capture — VOLATILE : elle change à chaque
    # affichage. La garder dans le modèle rendait la comparaison toujours
    # « différente » (on a écrasé 3 bonnes corrections par du machine avant de
    # le comprendre, 20/07/2026) et la correction périmée à la minute près.
    def sans_duree(t):
        return re.sub(r"\s*\n\d+\s+\S+\s+(?:restantes?|restants?|remaining)"
                      r"\s*$", "", t)
    echecs = {i: sans_duree(t) for i, t in echecs.items()}
    deja = textes_deja_corriges()

    # Comparaison INSENSIBLE aux espaces de fin de ligne : le client colle
    # parfois « ...Intellect. \n » là où la correction dit « ...Intellect.\n ».
    # L'alignement en jeu tolère déjà ces espaces — la comparaison doit faire
    # pareil, sinon on réécrit des corrections saines.
    def norme(t):
        return re.sub(r"[ \t]+\n", "\n", t).strip()

    a_faire = {i: t for i, t in echecs.items()
               if norme(t) not in {norme(x) for x in deja.get(i, set())}}
    print("échecs dans le journal local : %d | corrections à jour : %d | "
          "à (re)corriger : %d" % (len(echecs), len(echecs) - len(a_faire),
                                   len(a_faire)))
    if not a_faire:
        return 0

    lignes = []
    for id_ in sorted(a_faire, key=int):
        texte = a_faire[id_]
        fr = traduire(texte)
        if not fr:
            print("  ! traduction échouée : %s" % id_)
            continue
        lignes.append('aura(%s, "%s", "%s")'
                      % (id_, ir.echapper_lua(texte), ir.echapper_lua(fr)))
        print("  %-8s %-44s -> %s" % (id_, texte.split("\n")[0][:44],
                                      fr.split("\n")[0][:44]))
    if not lignes:
        # RIEN À ÉCRIRE n'est pas UN ÉCHEC (29/07/2026, même correctif
        # qu'ingerer_rapport) : les traductions ratées viennent d'être
        # listées, les signaler DEUX fois — dont une en rouge — n'ajoute
        # rien et use le contrôle des codes retour.
        print("Rien de nouveau à écrire dans DB_SortsCorrections.lua.")
        return 0
    if dry:
        print("--dry : rien écrit (%d prêtes)." % len(lignes))
        return 0

    contenu = ""
    if os.path.exists(ir.CORRECTIONS):
        with io.open(ir.CORRECTIONS, encoding="utf-8") as f:
            contenu = f.read()
    entete = ""
    if "local function aura(" not in contenu:
        entete = ("local DB = AscensionFR.DB.Sorts\n"
                  "local function aura(id, de2, d2)\n"
                  "    if DB[id] then DB[id].DE2 = de2; DB[id].D2 = d2 end\n"
                  "end\n")
    bloc = ("\n-- --- Moissonné du journal local "
            "(moissonner_echecs.py) ---\n"
            + entete + "\n".join(lignes) + "\n")
    with io.open(ir.CORRECTIONS, "a", encoding="utf-8") as f:
        f.write(bloc)
    print("\n%d correction(s) ajoutée(s) à DB_SortsCorrections.lua."
          % len(lignes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
