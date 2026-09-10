# -*- coding: utf-8 -*-
r"""RÈGLE D'ACCENT SUR LES MAJUSCULES INITIALES (lot 7 §4, 26/07/2026).

Blizzard n'accentuait pas les majuscules initiales en 3.3.5a : « Eclair de
givre », « Elixir de robustesse », « Etat d'empoisonnement », « Ame ardente ».
Le lot 5 a relevé 1 247 noms dans la source officielle, 56 mots initiaux
distincts, relus un par un.

OÙ ÇA S'APPLIQUE, ET POURQUOI PAS AILLEURS
------------------------------------------
La source officielle entre TELLE QUELLE dans ce qu'on livre : 15 491 entrées
de DB_Sorts.lua ont un champ N identique au N officiel du même identifiant
(DB[116] N="Eclair de givre" pour « Frostbolt »). Corriger seulement
`traductions/*.json` ne toucherait donc qu'un tiers du problème.

Ce module est appelé à DEUX endroits, et c'est voulu :
  1. aux points d'ÉCRITURE des bases — `generateur_db.ecrire_db`,
     `generer_noms_sorts.poser`, `generer_noms_objets` ;
  2. sur `traductions/*.json` (ligne de commande ci-dessous), sinon la forme
     fautive revient à chaque tour par les caches du moulin.

Surtout PAS dans `sources/` : ces fichiers sont ré-extraits du client, la
correction y disparaîtrait en silence — et `spells_frFR.json` / `spells_enUS.json`
sont le juge de paix de tout le contrôle d'appariement du lot 5.

LES TROIS PIÈGES, TOUS MESURÉS SUR LES DONNÉES RÉELLES
------------------------------------------------------
1. **La correction ne se lit pas dans le relevé.** Le champ
   `variante_accentuee` de `rapports/_mesure_appariement_brut.json` donne le
   mot en BAS DE CASSE (« éclair », « âme »), et pour « Equilibre » il donne
   carrément le participe passé « équilibré ». On reconstruit donc la
   correction : première lettre accentuée, reste du mot recopié tel quel.
   Contrôle : « ECHEC » -> « ÉCHEC » (et non « Échec »).

2. **Dix des mots sont AUSSI anglais** (Elite 400, Elixir 328, Eclipse 199,
   Evocation, Evasion, Ejection, Ame, Echantillon, Etoile — mesuré sur
   384 829 chaînes anglaises du livré). Accentuer une valeur restée en
   anglais fabrique une chimère (« Élixir of Fortitude »).

3. **« Elu » a deux lectures que la table ne sait pas séparer**, et c'est
   pour ça qu'il n'est PAS dans la table. DB_Creatures[10377] est
   `N="Elu",NE="Elu"` : le nom propre d'un PNJ du poste de Freewind. La
   quête 28491 le cite trois fois. Accentuer la seule tête du champ O
   rendrait la quête incohérente avec elle-même. À l'inverse
   DB_Creatures[22084] `N="Elu ombrelune"` est un vrai participe passé.
   3 entrées livrées : à traiter à la main, jamais en masse.

MESURÉ le 26/07/2026 : 3 784 entrées dans les DB_*.lua livrés, dont 791
portent la valeur empoisonnée « Epreuve de la Foi » (voir POISON ci-dessous).

Usage :
    python outils/accents_majuscules.py              # simulation + rapport
    python outils/accents_majuscules.py --appliquer  # écrit (+ sauvegardes)
    python outils/accents_majuscules.py --mot Eclair
"""
import argparse
import glob
import io
import json
import os
import re
import shutil
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRADUCTIONS = os.path.join(BASE, "traductions")
RAPPORT = os.path.join(BASE, "rapports", "accents_majuscules.txt")

# --- LA TABLE ---------------------------------------------------------------
# 55 mots. La correction ne touche QUE LA PREMIÈRE LETTRE. « Elu » est
# volontairement absent : voir le piège n°3 du docstring.
ACCENT = {"A": "Â", "E": "É"}
MOTS = (
    "Ame Ames Ecaille Echange Echantillon Echec ECHEC Echecs Echos "
    # « Ecraser »/« Ecrasement » manquaient à côté de « Ecraseur » (trou
    # trouvé au bloc E du programme 3 : l'officiel Blizzard écrit
    # « Ecraser » sans accent, et sans ces deux mots le pont livrait cette
    # graphie-là malgré la règle 1 de Dan). Impact mesuré : 6 valeurs.
    "Eclaboussure Eclair Eclairs Eclat Eclats Eclipse Ecorce Ecraser "
    "Ecrasement Ecraseur "
    "Ecureuil Ecuyer Egide Ejection Elite Elixir Emeraude Emergence "
    "Emerger Energie Enorme Epice Epine Epineux Epines Epreuve Epuisement "
    "Epuration Equilibre Equipage Equipe Equipement Equiper Equitation Etalon "
    "Etat Eteint Etendard Etincelle Etincelles Etoffe Etoile Etourdi "
    "Etourdissement Evasion Eveil Eventail Evocation"
).split()
TABLE = {m: ACCENT[m[0]] + m[1:] for m in MOTS}

# Les mots de la table qui sont AUSSI des mots ANGLAIS. Sur eux seulement, on
# exige que la valeur ne sente pas l'anglais résiduel.
AMBIGUS = {"Elite", "Elixir", "Eclipse", "Evocation", "Evasion", "Ejection",
           "Ame", "Echantillon", "Etoile"}

# Valeurs EXACTES qu'on ne touche jamais, chacune pour une raison précise.
EXCEPTIONS = {
    # Le nom anglais de l'objet a été gardé, seul « (Backsheath) » est
    # traduit : accentuer fabriquerait une chimère. Preuve que c'est bien de
    # l'anglais : le même pont livre ["Eclipse Stiletto"]="Stylet Éclipse".
    "Eclipse Stiletto (gaine arrière)",
    # POISON connu, à ne surtout pas rendre plus joli : dans
    # traductions/sorts.json, 778 clés anglaises SANS AUCUN RAPPORT entre
    # elles (« Abom tele back », « Angel of Death », « Aftershock cast »…)
    # portent toutes cette même valeur, et 791 entrées de DB_SortsNoms.lua
    # avec. Ce n'est pas une traduction, c'est un dégât. Tant qu'il n'est pas
    # purgé (décision de Dan), il doit rester repérable d'un coup d'œil.
    # Signature nette : le F majuscule. La vraie traduction du sort s'écrit
    # « Epreuve de la foi », f minuscule.
    "Epreuve de la Foi",
}

LETTRE = r"0-9A-Za-zÀ-ÿ"
# Les codes du jeu se COLLENT au mot (« |cFFB5FFFFEclair ») : on les remplace
# par un remplissage NON-LETTRE de MÊME longueur, sinon les positions glissent
# et on réécrit à côté.
CODES = re.compile(r"\|c[0-9A-Fa-f]{8}|\|r|\|T[^|]*\|t|\|H[^|]*\|h|\|h")
RE_TETE = re.compile(r"^([^%s]*)([%s]+)" % (LETTRE, LETTRE))

# Mots-outils anglais choisis pour ne PAS exister en français : ni « on », ni
# « a », ni « en », ni « mana », ni « test », ni « sec », qui sont français et
# feraient rater la garde sur du vrai français.
ANGLAIS = re.compile(
    r"(?<![%s])(of|the|and|your|with|from|you|is|are|was|were|this|that|"
    r"these|those|when|while|which|their|his|her|our|been|increases|"
    r"reduces|deals|damage|healing|enemies|weapon|shield|strike|blade|"
    r"bolt|blast|hide|credit|quest|trigger)(?![%s])|'s(?![%s])"
    % (LETTRE, LETTRE, LETTRE), re.I)

# Champs FRANÇAIS des bases par identifiant. Liste BLANCHE, jamais noire :
# NE, DE, TE, SE sont les MODÈLES ANGLAIS qui servent à aligner l'info-bulle
# affichée, et y toucher casserait la traduction. Une liste noire oublierait
# le prochain champ anglais ajouté ; une liste blanche l'ignore d'office.
CHAMPS_FR = {"N", "D", "T", "R", "O", "A", "F", "P", "S", "OT"}
CHAMPS_ANGLAIS = {"NE", "DE", "TE", "SE", "OE", "AE", "FE", "PE"}


def denuder(texte):
    return CODES.sub(lambda m: "\x01" * len(m.group(0)), texte or "")


def corriger_tete(texte, anglais=None):
    """Accentue la majuscule INITIALE si elle relève de la règle.

    `anglais` est le texte SOURCE de cette valeur quand on l'a : la clé du
    dictionnaire pour les ponts par nom, le champ frère NE/DE/TE/SE pour les
    bases par identifiant. Il sert à repérer une valeur qui n'a jamais été
    traduite — l'accentuer donnerait un mot français au milieu d'anglais.

    Rend le texte inchangé dans tous les autres cas. Idempotent : un texte
    déjà accentué ne correspond à aucune entrée de la table.
    """
    if not texte or not isinstance(texte, str):
        return texte
    if texte.strip() in EXCEPTIONS:
        return texte
    nu = denuder(texte)
    m = RE_TETE.match(nu)
    if not m:
        return texte
    mot = m.group(2)
    if mot not in TABLE:
        return texte
    # GARDE 1 — rien n'a été traduit : la valeur « française » EST sa source
    # anglaise. C'est le cas de DB_Creatures[10377] N="Elu" NE="Elu" et des
    # « Ame en peine arcanique » dont le NE est identique.
    if anglais and texte.strip() == anglais.strip():
        return texte
    # GARDE 2 — anglais résiduel sur les mots ambigus. « Elixir of Fortitude »
    # ne doit pas devenir « Élixir of Fortitude ».
    if mot in AMBIGUS and ANGLAIS.search(nu):
        return texte
    debut = len(m.group(1))
    return texte[:debut] + TABLE[mot] + texte[debut + len(mot):]


# ---------------------------------------------------------------------------
# CITATIONS DE NOMS DANS LES TEXTES (bloc 2b, 28/07/2026 — le revers de la
# règle des têtes). Les têtes sont accentuées (« Éclair de givre ») mais les
# textes qui les CITENT disent encore « Vous apprend Eclair de givre » — et
# le gros vient de la couche OFFICIELLE, qui n'accentue pas ses majuscules :
# corriger traductions/ seul ne toucherait qu'une fraction. La règle vit donc
# ICI et s'applique par polir() aux points d'écriture, toutes couches.
#
# Un « nom cité » = un nom français d'au moins DEUX mots, connu de nos
# traductions OU de l'officiel, dont la tête relève de la table. Deux mots
# minimum : c'est ce qui rend le remplacement littéral sans ambiguïté
# (« Etat » seul pourrait être un mot de phrase ; « Etat de transe » ne peut
# être que le nom). Remplacement du plus long au plus court (noms emboîtés),
# et garde d'occurrence qui accepte le code couleur COLLÉ (« |cFFB5FFFFEclair
# de givre » n'a pas de frontière \b devant le E).
# ---------------------------------------------------------------------------
_CITATIONS = None            # {variante_non_accentuée: nom_accentué}
_CITATIONS_PAR_MOT = None    # {mot_tête_nu: [variantes triées long->court]}
_DESACCENT = {v: k for k, v in ACCENT.items()}


def _candidats_citations():
    """Les noms français ≥ 2 mots, toutes sources confondues (nos
    traductions ET l'officiel frFR — accentué ou non à la tête)."""
    noms = set()

    def prendre(valeur):
        if isinstance(valeur, str) and " " in valeur.strip():
            noms.add(valeur.strip())

    chemins = (
        (os.path.join(TRADUCTIONS, "sorts.json"), "noms"),
        (os.path.join(TRADUCTIONS, "objets.json"), "N"),
        (os.path.join(TRADUCTIONS, "objets_dbc.json"), "N"),
        (os.path.join(TRADUCTIONS, "zones.json"), None),
        (os.path.join(BASE, "sources", "dbc", "spells_frFR.json"), "N"),
    )
    for chemin, champ in chemins:
        if not os.path.isfile(chemin):
            continue
        try:
            donnees = json.load(io.open(chemin, encoding="utf-8"))
        except ValueError:
            continue
        if champ == "noms":
            for fr in (donnees.get("noms") or {}).values():
                prendre(fr)
        elif champ == "N":
            for fiche in donnees.values():
                if isinstance(fiche, dict):
                    prendre(fiche.get("N"))
        else:
            for valeur in donnees.values():
                prendre(valeur)
    return noms


def _table_citations():
    global _CITATIONS, _CITATIONS_PAR_MOT
    if _CITATIONS is not None:
        return _CITATIONS
    remplacements = {}
    for nom in _candidats_citations():
        if nom in EXCEPTIONS:
            continue
        premier = nom.split(" ", 1)[0]
        if premier in TABLE:
            variante, accentue = nom, TABLE[premier] + nom[len(premier):]
        elif premier and premier[0] in _DESACCENT:
            nu = _DESACCENT[premier[0]] + premier[1:]
            if nu not in TABLE:
                continue
            variante, accentue = nu + nom[len(premier):], nom
        else:
            continue
        if variante in EXCEPTIONS or accentue.strip() in EXCEPTIONS:
            continue
        # Même garde que corriger_tete : un « nom » qui sent l'anglais
        # résiduel n'entre pas dans la table — « Élite Shadow » serait une
        # chimère (et le candidat vient peut-être d'une valeur jamais
        # traduite).
        if ANGLAIS.search(variante):
            continue
        deja = remplacements.get(variante)
        if deja is None:
            remplacements[variante] = accentue
        elif deja != accentue:
            remplacements[variante] = ""      # conflit : on n'y touche pas
    _CITATIONS = {v: a for v, a in remplacements.items() if a}
    _CITATIONS_PAR_MOT = {}
    for variante in sorted(_CITATIONS, key=len, reverse=True):
        mot = variante.split(" ", 1)[0]
        _CITATIONS_PAR_MOT.setdefault(mot, []).append(variante)
    return _CITATIONS


# Les codes du jeu se COLLENT au mot (« |cFFB5FFFFEclair », « |t|rEclair ») :
# trois lookbehind de largeur fixe, comme DEBUT_MOT de generateur_db.
_DEVANT = r"(?:(?<=^)|(?<=\|[rt])|(?<=\|c[0-9A-Fa-f]{8})|(?<=[^0-9A-Za-zÀ-ÿ]))"
# Pré-tri : si aucun mot de la table n'apparaît, on ne tente rien (appelé sur
# ~1,3 M de champs à chaque build — le chemin rapide compte).
_PRESELECTION = re.compile(
    _DEVANT + r"(%s) " % "|".join(sorted(TABLE, key=len, reverse=True)))


def corriger_citations(texte):
    """Accentue les noms CITÉS dans un texte français. Idempotent."""
    if not texte or not isinstance(texte, str):
        return texte
    table = _table_citations()
    if not table:
        return texte
    mots_presents = {m.group(1) for m in _PRESELECTION.finditer(texte)}
    if not mots_presents:
        return texte
    for mot in mots_presents:
        for variante in _CITATIONS_PAR_MOT.get(mot, ()):
            if variante not in texte:
                continue
            texte = re.sub(
                _DEVANT + re.escape(variante) + r"(?![0-9A-Za-zà-ÿ])",
                table[variante].replace("\\", "\\\\"), texte)
    return texte


def corriger_toutes_majuscules(texte):
    """corriger_tete() appliquée à CHAQUE mot de la table, où qu'il soit.

    Élargissement du bloc A (programme 3, 29/07/2026). corriger_tete ne
    voit que le PREMIER mot : « Apparition d'Étendard de bataille » ou
    « Échec d'Équilibre de la nature » portent leur accent au DEUXIÈME —
    ces 18 noms remontaient donc au fichier d'arbitrage de Dan alors que
    la décision était déjà prise (les 402 autres, elles, sortaient bien).

    La sûreté est la MÊME que corriger_tete : seuls les 55 mots de TABLE
    peuvent changer, et seulement leur première lettre. Ce n'est jamais
    une comparaison sans accents (voir l'avertissement plus bas).
    """
    if not texte or not isinstance(texte, str):
        return texte
    if texte.strip() in EXCEPTIONS:
        return texte
    nu = denuder(texte)
    sortie, position = [], 0
    for m in re.finditer(r"[%s]+" % LETTRE, nu):
        mot = texte[m.start():m.end()]
        if mot in TABLE and not (mot in AMBIGUS and ANGLAIS.search(nu)):
            sortie.append(texte[position:m.start()])
            sortie.append(TABLE[mot])
            position = m.end()
    sortie.append(texte[position:])
    return "".join(sortie)


# L'apostrophe : l'officiel 3.3.5a écrit « Echantillon d’eau » (courbe), nous
# écrivons droit partout (le pont compare au texte EXACT du client). Deux
# graphies du même caractère ne sont pas une divergence de vocabulaire.
def _apostrophes(s):
    return (s or "").replace("’", "'").replace("ʼ", "'").replace("`", "'")


def difference_d_accent_seule(notre, officiel):
    """Notre valeur est-elle l'officiel, à NOTRE règle d'accent près ?

    Sert aux outils d'arbitrage. Depuis qu'on accentue, notre français diffère
    de l'officiel 3.3.5a sur ~400 noms par le SEUL accent initial
    (« Éclair de givre » contre « Eclair de givre ») : ce n'est pas une
    divergence à arbitrer, c'est une décision déjà prise. Sans ce test, le
    fichier d'arbitrage de Dan passe de 67 vraies divergences à 468.

    Le test est volontairement ÉTROIT : il ne dit vrai que si notre valeur est
    EXACTEMENT ce que corriger_tete() produit à partir de l'officiel. Toute
    autre différence — même d'un seul accent ailleurs dans le mot — reste une
    divergence.

    ⚠️ Ne JAMAIS remplacer ce test par une comparaison sans accents : il
    rendrait ces 400 entrées « adoptables », et un seul --appliquer
    réécrirait tous nos accents avec la version non accentuée de Blizzard.
    """
    if not notre or not officiel:
        return False
    notre, officiel = notre.strip(), officiel.strip()
    if notre == officiel:
        return False
    if corriger_tete(officiel) == notre:
        return True
    # Élargissement du bloc A (programme 3) : accents sur les majuscules
    # INTERNES et apostrophe courbe de l'officiel. Toujours constructif —
    # on FABRIQUE notre graphie à partir de l'officiel et on compare à
    # l'identique ; jamais une comparaison accent-aveugle.
    return _apostrophes(corriger_toutes_majuscules(officiel)) \
        == _apostrophes(notre)


# ---------------------------------------------------------------------------
# Ligne de commande : passe sur traductions/*.json
# ---------------------------------------------------------------------------
def est_sauvegarde(chemin):
    return "_avant_" in os.path.basename(chemin)


def parcourir(obj, dans_ident=False, compte=None):
    """Réécrit en place. Rend le nombre de valeurs corrigées.

    `dans_ident` dit qu'on est sous une clé NUMÉRIQUE (une entrée par
    identifiant) : là, la clé n'est pas l'anglais, c'est le champ frère
    NE/DE/TE/SE qui l'est.
    """
    n = 0
    if not isinstance(obj, dict):
        return 0
    for cle, valeur in list(obj.items()):
        if isinstance(valeur, str):
            if dans_ident:
                if cle in CHAMPS_ANGLAIS or cle not in CHAMPS_FR:
                    continue
                source = obj.get(cle + "E")
            else:
                # Clé = texte anglais source pour les fichiers à clé anglaise.
                source = cle if not str(cle).isdigit() else None
            neuf = corriger_tete(valeur, anglais=source)
            if neuf != valeur:
                obj[cle] = neuf
                n += 1
                if compte is not None:
                    compte[RE_TETE.match(denuder(valeur)).group(2)] += 1
        elif isinstance(valeur, dict):
            n += parcourir(valeur, dans_ident=str(cle).isdigit() or dans_ident,
                           compte=compte)
    return n


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--appliquer", action="store_true",
                   help="écrit vraiment (sinon : simulation)")
    p.add_argument("--mot", help="n'examiner qu'un mot de la table")
    args = p.parse_args()

    if args.mot:
        for m in list(TABLE):
            if m != args.mot:
                del TABLE[m]
        print("table restreinte à :", TABLE)

    total, compte, lignes = 0, Counter(), []
    for chemin in sorted(glob.glob(os.path.join(TRADUCTIONS, "*.json"))):
        if est_sauvegarde(chemin):
            continue
        try:
            with io.open(chemin, encoding="utf-8") as f:
                donnees = json.load(f)
        except ValueError:
            continue
        n = parcourir(donnees, compte=compte)
        if not n:
            continue
        total += n
        nom = os.path.basename(chemin)
        lignes.append("%-34s %6d entrées" % (nom, n))
        print("%-34s %6d entrées" % (nom, n))
        if args.appliquer:
            secours = chemin.replace(".json", "_avant_accents.json")
            if not os.path.exists(secours):
                shutil.copy2(chemin, secours)
            with io.open(chemin, "w", encoding="utf-8") as f:
                json.dump(donnees, f, ensure_ascii=False, indent=1,
                          sort_keys=True)

    os.makedirs(os.path.dirname(RAPPORT), exist_ok=True)
    with io.open(RAPPORT, "w", encoding="utf-8") as f:
        f.write("RÈGLE D'ACCENT — %s\n\n"
                % ("APPLIQUÉE" if args.appliquer else "SIMULATION"))
        f.write("\n".join(lignes))
        f.write("\n\nPar mot :\n")
        for mot, n in compte.most_common():
            f.write("  %-16s %5d  -> %s\n" % (mot, n, TABLE[mot]))
        f.write("\nTOTAL : %d entrées\n" % total)

    print("\npar mot :", ", ".join("%s %d" % (m, n)
                                   for m, n in compte.most_common(10)))
    print("TOTAL : %d entrées%s" % (total, "" if args.appliquer
                                    else "   (SIMULATION — rien écrit)"))
    print("rapport :", RAPPORT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
