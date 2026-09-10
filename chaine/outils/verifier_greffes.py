# -*- coding: utf-8 -*-
r"""
Recensement des GREFFES de l'addon, et survivent-elles au client actuel ?
(programme 12, bloc A, 01/08/2026)

POURQUOI. Ascension a poussé le patch Saison 10 le 01/08 à 01h57 — 2 Go. L'addon
se charge et « a l'air de marcher ». **Ça ne prouve rien sur les accroches.**

Une greffe posée sur une fonction que le client a renommée ou retirée ne fait pas
planter le jeu :
  - si elle est GARDÉE par un `if type(x) == "function"`, elle ne se pose
    simplement pas — et la fenêtre concernée reste en anglais, en silence ;
  - si elle n'est PAS gardée, `hooksecurefunc` lève une erreur au chargement,
    que le joueur ne verra pas forcément passer.
Dans les deux cas, l'addon a l'air de marcher jusqu'à ce qu'un joueur ouvre la
fenêtre en question.

CE QUE FAIT CET OUTIL. Il recense toutes les greffes sur des globales nommées du
client, dit lesquelles sont gardées, puis vérifie chaque nom contre le FrameXML
**du client actuel** — extrait des MPQ, pas la copie de `sources/framexml` qui
peut dater d'avant le patch.

⚠️ LIMITE À CONNAÎTRE. Le FrameXML dit ce qui est DÉFINI dans les fichiers
d'interface. Il ne dit pas ce que le moteur C expose, ni ce qu'un addon
d'Ascension ajoute au chargement. Une fonction absente d'ici n'est donc pas
forcément absente en jeu — c'est un signalement à confirmer par la sonde en jeu
(`/afr greffes`), qui, elle, interroge le vrai `_G`.

Usage : python outils/verifier_greffes.py [--extraire]
        --extraire  relit les MPQ du client (lent) au lieu du cache
"""
import io
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT = r"D:\AscensionFR\WOW_Priv\resources\ascension-live"
ADDON = os.path.join(CLIENT, "Interface", "AddOns", "AscensionFR")
CACHE = os.path.join(RACINE, "cache_db", "framexml_client")

# La greffe elle-même : hooksecurefunc("NomGlobal", ...)
GREFFE = re.compile(r'hooksecurefunc\(\s*"([A-Za-z_][A-Za-z_0-9]*)"')
# La garde : if type(NomGlobal) == "function"
GARDE = re.compile(r'type\(\s*([A-Za-z_][A-Za-z_0-9]*)\s*\)\s*==\s*"function"')
# Ou la garde par présence simple : if NomGlobal then / if NomGlobal and
GARDE_SIMPLE = re.compile(r'\bif\s+(?:not\s+)?([A-Za-z_][A-Za-z_0-9]*)\b')

# Une fonction globale se déclare de DEUX façons, et rater la seconde fait
# crier au loup : « function Nom(...) » et « Nom = function(...) ».
DEFINITION = re.compile(
    r'^\s*(?:function\s+([A-Za-z_][A-Za-z_0-9]*)\s*\('
    r'|([A-Za-z_][A-Za-z_0-9]*)\s*=\s*function\s*\()', re.M)


def modules():
    d = os.path.join(ADDON, "Modules")
    out = [os.path.join(ADDON, "Core.lua")]
    out += [os.path.join(d, f) for f in sorted(os.listdir(d))
            if f.endswith(".lua")]
    return out


def archives_par_priorite():
    """Les MPQ du client, de la MOINS prioritaire à la PLUS prioritaire.

    L'ordre n'est pas décoratif. Un correctif peut RÉÉCRIRE un fichier
    d'interface, et la nouvelle version peut ne plus définir une fonction que
    l'ancienne définissait. Prendre l'union de toutes les archives dirait alors
    « présente » pour une fonction disparue — exactement l'erreur qu'on cherche
    à ne pas commettre. On écrase donc dans l'ordre de chargement du jeu : le
    dernier écrit gagne.

    ⚠️ Et le FrameXML de base n'est PAS dans Data\\*.MPQ : il vit dans les
    archives de LANGUE, Data\\enUS\\*.MPQ. Ne regarder que le premier dossier
    ratait ReputationFrame, LootFrame, TaxiFrame, UIDropDownMenu...
    """
    import glob
    data = os.path.join(CLIENT, "Data")
    toutes = (sorted(glob.glob(os.path.join(data, "*.MPQ")))
              + sorted(glob.glob(os.path.join(data, "enUS", "*.MPQ"))))

    def rang(chemin):
        nom = os.path.basename(chemin).lower()
        if not nom.startswith("patch"):
            return (0, nom)          # common, expansion, lichking, locale-*
        if "enus" in nom:
            return (1, nom)          # patch-enUS, -2, -3 : correctifs Blizzard
        corps = nom[6:].split(".")[0]
        if corps.isdigit():
            return (2, int(corps))   # patch-2, patch-3
        return (3, corps)            # patch-A..patch-Z : Ascension, en dernier

    return sorted(toutes, key=rang)


def extraire_framexml():
    """Relit le FrameXML des MPQ du client. Lent : on met en cache."""
    import mpyq
    if not os.path.isdir(CACHE):
        os.makedirs(CACHE)
    n = 0
    for chemin in archives_par_priorite():
        try:
            a = mpyq.MPQArchive(chemin, listfile=True)
            noms = a.files or []
        except Exception:
            continue
        for nom in noms:
            if not nom.lower().endswith(b".lua"):
                continue
            # PAS seulement le FrameXML : la moitié des fonctions qu'on accroche
            # vit dans les addons de Blizzard chargés à la demande
            # (Blizzard_TradeSkillUI, Blizzard_Calendar, Blizzard_TrainerUI...).
            # Sur le disque, ces dossiers ne contiennent qu'un `.pub` de 257
            # octets : tout le code est dans les MPQ. Ne regarder que le
            # FrameXML faisait crier au loup sur 8 greffes parfaitement saines.
            if (b"FrameXML" not in nom
                    and b"Blizzard_" not in nom):
                continue
            try:
                contenu = a.read_file(nom.decode("latin1"))
            except Exception:
                continue
            if not contenu:
                continue
            base = nom.decode("latin1").replace("\\", "_").replace("/", "_")
            io.open(os.path.join(CACHE, base), "wb").write(contenu)
            n += 1
    return n


def globales_du_client():
    """Toutes les fonctions globales définies par le FrameXML actuel."""
    connues = set()
    if not os.path.isdir(CACHE):
        return connues, 0
    fichiers = [f for f in os.listdir(CACHE) if f.lower().endswith(".lua")]
    for f in fichiers:
        chemin = os.path.join(CACHE, f)
        with io.open(chemin, encoding="utf-8", errors="replace") as fh:
            for a, b in DEFINITION.findall(fh.read()):
                connues.add(a or b)
    return connues, len(fichiers)


def recenser():
    """[(fichier, ligne, nom, gardee)] pour chaque greffe sur une globale."""
    trouvees = []
    for chemin in modules():
        with io.open(chemin, encoding="utf-8") as fh:
            lignes = fh.read().split("\n")
        for i, ligne in enumerate(lignes):
            for nom in GREFFE.findall(ligne):
                # La garde est cherchée dans les 12 lignes qui précèdent :
                # c'est la portée d'un `if ... then` qui enveloppe la greffe.
                avant = "\n".join(lignes[max(0, i - 12):i])
                gardee = (nom in GARDE.findall(avant)
                          or nom in GARDE_SIMPLE.findall(avant))
                trouvees.append((os.path.basename(chemin), i + 1, nom, gardee))
    return trouvees


def main():
    if "--extraire" in sys.argv or not os.path.isdir(CACHE):
        print("Extraction du FrameXML depuis les MPQ du client (long)...")
        n = extraire_framexml()
        print("  %d fichier(s) extrait(s) vers cache_db/framexml_client" % n)
        print()

    connues, nb_fichiers = globales_du_client()
    greffes = recenser()

    print("=" * 74)
    print("RECENSEMENT DES GREFFES — AscensionFR")
    print("=" * 74)
    print()
    print("Référence : %d fichiers FrameXML du client ACTUEL, %d fonctions "
          "globales." % (nb_fichiers, len(connues)))
    print()

    non_gardees, absentes = [], []
    print("  %-22s %-6s %-32s %-7s %s"
          % ("fichier", "ligne", "fonction accrochée", "gardée", "au client"))
    print("  " + "-" * 84)
    for fichier, ligne, nom, gardee in greffes:
        presente = nom in connues
        if not gardee:
            non_gardees.append((fichier, ligne, nom))
        if not presente:
            absentes.append((fichier, ligne, nom, gardee))
        print("  %-22s %-6d %-32s %-7s %s"
              % (fichier, ligne, nom,
                 "oui" if gardee else "NON",
                 "oui" if presente else "*** ABSENTE ***"))

    print()
    print("=" * 74)
    print("CE QUI COMPTE")
    print("=" * 74)
    print("  greffes recensées ............ %d" % len(greffes))
    print("  NON gardées (les fragiles) ... %d" % len(non_gardees))
    for f, l, n in non_gardees:
        print("      %s:%d  %s" % (f, l, n))
    print("  absentes du FrameXML actuel .. %d" % len(absentes))
    for f, l, n, g in absentes:
        print("      %s:%d  %s  (%s)"
              % (f, l, n, "gardée : elle se taira" if g
                 else "NON GARDÉE : erreur au chargement"))
    # ---- LA LISTE EN JEU DOIT SUIVRE LE CODE -----------------------------
    # `/afr greffes` interroge une liste de noms écrite à la main dans
    # Perf.lua. Une greffe ajoutée sans y être inscrite ne serait JAMAIS
    # vérifiée, et la sonde dirait « tout va bien » en regardant à côté.
    # C'est ici, et seulement ici, que le banc mord.
    print()
    print("=" * 74)
    print("LA SONDE EN JEU REGARDE-T-ELLE AU BON ENDROIT ?")
    print("=" * 74)
    chemin_perf = os.path.join(ADDON, "Modules", "Perf.lua")
    with io.open(chemin_perf, encoding="utf-8") as fh:
        source = fh.read()
    bloc = re.search(r"local GREFFES = \{(.*?)\n\}", source, re.S)
    inscrites = set(re.findall(r'"([A-Za-z_][A-Za-z_0-9]*)"', bloc.group(1))) \
        if bloc else set()
    reelles = set(n for _, _, n, _ in greffes)
    oubliees = sorted(reelles - inscrites)
    fantomes = sorted(inscrites - reelles)
    print("  greffes dans le code ......... %d" % len(reelles))
    print("  inscrites dans Perf.lua ...... %d" % len(inscrites))
    if oubliees:
        print("  OUBLIÉES (jamais vérifiées en jeu) :")
        for n in oubliees:
            print("      %s" % n)
    if fantomes:
        print("  FANTÔMES (inscrites mais plus greffées) :")
        for n in fantomes:
            print("      %s" % n)
    if not oubliees and not fantomes:
        print("  -> la liste de la sonde colle au code.")
    print()

    if absentes:
        print("  ⚠ Une absence ici est un SIGNALEMENT, pas une preuve : le")
        print("    FrameXML ne dit pas ce que le moteur C expose ni ce qu'un")
        print("    addon d'Ascension ajoute. À confirmer par « /afr greffes »")
        print("    en jeu, qui interroge le vrai _G.")
    # Le code retour ne mord PAS sur les absences : hors du jeu on ne peut que
    # SIGNALER, et le juge de paix est `/afr greffes`. Il mord en revanche si la
    # liste de la sonde a décroché du code — ça, c'est vérifiable ici, et c'est
    # ce qui rend la sonde digne de confiance.
    return 1 if (oubliees or fantomes) else 0


if __name__ == "__main__":
    sys.exit(main())
