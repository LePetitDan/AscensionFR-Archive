# -*- coding: utf-8 -*-
"""
Les répliques des PNJ sont-elles vraiment traduites dans le chat ?

Doute légitime : l'addon AscensionFR_Repliques ne contient QUE des données
(DB_Repliques.lua, 17 Mo, 69 477 paroles) — aucun code. Le code qui les
utilise est dans AscensionFR\\Modules\\Chat.lua, qui pose un filtre de messages
sur les événements CHAT_MSG_MONSTER_*. Ce test rejoue le chemin complet, avec
de VRAIES entrées de la base livrée, pour montrer que la parole d'un PNJ
emprunte bien ce chemin — texte ET nom de l'émetteur.

CE QU'IL PROUVE, ET CE QU'IL NE PROUVE PAS. Les ~980 rejeux tirent leur
attendu de la MÊME base qu'ils lisent (attendu = Substituer(fr)) : ils
démontrent le CHEMIN — filtre posé sur l'événement, clé retrouvée dans la
table paresseuse, variables résolues, ligne réécrite — jamais la QUALITÉ du
texte français. Une base dont chaque traduction serait remplacée par « Blah »
les passerait tous. Le contrôle de CONTENU tient entièrement aux 5 témoins
figés en fin de fichier, dont l'attendu est écrit à la main.

FORMAT DE LA BASE (2.0.1) : elle n'est plus une suite de lignes « DB[..]=.. »
(mesuré le 26/07/2026 : 0 ligne « DB[ » sur les 139 lignes du fichier) mais une
base PARESSEUSE PAR TEXTE — 66 seaux `C[octet]` (chaîne de présence) et
`M[octet]` (source Lua du seau), montés par AFR.ParesseuxTexte. Elle ne se
parcourt PAS avec pairs(). On charge donc le fichier tel quel (la vraie table
paresseuse en sort, et c'est bien SON chemin d'accès qu'on met à l'épreuve),
et on va chercher les couples EN→FR à rejouer en compilant les seaux `M[]`
À PART, dans des tables ordinaires.

Le banc rend 1 dès qu'il n'a pas de quoi tester : une base vide, un seau
illisible, un désaccord entre C[] et M[] ou un filtre absent sont des ÉCHECS,
jamais un succès silencieux.

Usage : python outils/verifier_repliques.py
"""
import os
import sys

import lupa.lua51 as lupa_mod

JEU = r"D:\AscensionFR\WOW_Priv\resources\ascension-live"
ADDON = os.path.join(JEU, "Interface", "AddOns", "AscensionFR")
BASE_REP = os.path.join(JEU, "Interface", "AddOns", "AscensionFR_Repliques",
                        "DB_Repliques.lua")

# Combien de couples EN→FR on prélève dans CHACUN des 66 seaux. Étalé sur tout
# le seau : on ne veut pas 246 répliques qui commencent toutes par la même
# lettre.
COUPLES_PAR_SEAU = 5

# En dessous, le banc se déclare non concluant plutôt que vert. Rendement réel
# mesuré le 26/07/2026 avec COUPLES_PAR_SEAU = 5 : 246 couples retenus — 200
# laisse 46 de marge, assez pour ne pas clignoter au remaniement des données,
# assez près pour mordre.
COUPLES_MINIMUM = 200

# REPÈRE DE VOLUME — le point le plus délicat du banc.
# Le corpus de test est prélevé DANS les seaux : si des répliques disparaissent
# de la base, elles disparaissent AUSSI de ce qu'on teste, et le banc se
# contente de tester moins de choses sans rien dire. Un plancher fixe très bas
# ne rattrape pas ça : ENTREES_MINIMUM valait 60 000 pour 69 477 répliques
# livrées, soit 9 477 de mou (13,6 %). Mesuré le 27/07/2026 sur une base
# fabriquée en rognant 13 % des clés de chaque seau (60 475 répliques
# restantes), C[] et M[] refaits d'accord à la clé près, les 66 seaux et les
# 26 majuscules toujours là : le banc affichait « 60475 répliques dans 66 seaux
# paresseux », « 0 échec(s) », CODE RETOUR 0. Un vert qui ne prouvait plus rien.
# D'où un repère RELATIF à la taille RELEVÉE, et non un plancher de misère :
# 69 477 répliques comptées le 26/07/2026 sur la base livrée, des DEUX côtés
# (somme des M[] et somme des C[], même valeur), recomptées le 27/07/2026.
# La bande est volontairement asymétrique : 1 % de perte tolérée, 50 % de
# croissance (une base qui double n'a jamais été un accident bénin — voir le
# compte gonflé par des lignes M[] en double, attrapé plus bas par
# couples_base).
# CE QU'IL EN COÛTE ET CE QUI RESTE OUVERT, dit franchement et mesuré le
# 27/07/2026 sur trois bases fabriquées à perte diffuse (1 entrée retirée sur
# 8, sur 50, sur 100, dans CHAQUE seau, des deux côtés) : à 12,5 % et à 2,0 %
# le banc rend 1 ; à 0,97 % il rend encore 0. Le trou résiduel est donc une
# perte diffuse d'au plus 695 répliques (69 477 - 68 782) — 13 fois plus petit
# que les 9 477 du plancher fixe, mais pas nul. Et la marge de fausse alerte
# est exactement la même : 696 répliques retirées pour de bonnes raisons, et le
# banc rend 1 en disant quoi faire. Ces trois nombres sont un CONSTAT, pas une
# vérité.
# Le vrai correctif serait que outils/paresseux_textes.py écrive lui-même le
# compte en tête du fichier généré et que le banc le lise ici, sans constante
# à entretenir — hors périmètre du chantier qui a écrit ces lignes.
ENTREES_REFERENCE = 69477
PERTE_TOLEREE = 0.01
GONFLEMENT_TOLERE = 0.50

# Un seau retiré des DEUX côtés à la fois (C[] et M[]) laisse une base
# PARFAITEMENT cohérente : le croisement C[]/M[] ne le voit pas. Mesuré le
# 26/07/2026 : les 5 seaux de l'étude retirés des deux côtés = 9 477 répliques
# évaporées (13,6 %) et il restait exactement 60 000 entrées, que l'ancien
# plancher fixe laissait passer à l'unité près. D'où ce croisement structurel
# et non volumétrique : sur 69 477 répliques anglaises, les 26 majuscules ont
# TOUTES leur seau (vérifié). Qu'une lettre disparaisse entièrement n'arrive
# pas dans un corpus de cette taille — sauf si on a perdu des données.
# LE PRIX DE CETTE EXIGENCE, chiffré pour qu'il s'arbitre en connaissance de
# cause : le plus petit seau exigé, 'X', ne pèse que 29 répliques sur 69 477
# (0,04 % ; viennent ensuite 'Z' 127 et 'Q' 131). Si une régénération des
# données perdait ces 29-là, le banc rendrait 1 sur une base par ailleurs
# saine.
# Le cas qu'on décrivait ici comme le « trou résiduel » n'en est pas un
# (vérifié le 27/07/2026, base fabriquée) : les 40 seaux qui ne sont PAS une
# majuscule pèsent 4 174 répliques (6,0 %) et, retirés en entier des deux
# côtés, ils font rendre 1 — deux fois plutôt qu'une. Le repère de volume parle
# le premier (« 65303 entrées contre 69477 relevées, 6,0 % de moins ») ;
# COUPLES_MINIMUM rattrapait déjà le cas tout seul avant lui (« 127 couples lus
# seulement (minimum 200) », mesuré sur la version d'avant ce correctif). Le
# trou réel est celui écrit au-dessus : la perte diffuse sous les 695 répliques.
SEAUX_OBLIGATOIRES = list(range(ord("A"), ord("Z") + 1))

EVENEMENTS = ["CHAT_MSG_MONSTER_SAY", "CHAT_MSG_MONSTER_YELL",
              "CHAT_MSG_MONSTER_EMOTE", "CHAT_MSG_MONSTER_WHISPER"]

CONTEXTE = r"""
function strtrim(s) return (string.gsub(s or "", "^%s*(.-)%s*$", "%1")) end
function UnitName() return "<joueur>" end
function UnitClass() return "Templar" end
function UnitRace() return "Dwarf" end
function UnitSex() return 2 end
function hooksecurefunc() end
function print() end

-- Core.lua crée un cadre pour le préchauffage des index (Core.lua:243) :
-- sans CreateFrame, le noyau ne se charge même pas — le banc mourait là,
-- sur « attempt to call global 'CreateFrame' (a nil value) ».
function CreateFrame()
    local f = {}
    function f:RegisterEvent() end
    function f:UnregisterEvent() end
    function f:SetScript() end
    function f:HookScript() end
    function f:Show() end
    function f:Hide() end
    return f
end

-- ChatFrame_AddMessageEventFilter : on RETIENT les filtres pour les déclencher
-- nous-mêmes, comme le fait le moteur de chat du jeu.
_FILTRES = {}
function ChatFrame_AddMessageEventFilter(evt, fn)
    _FILTRES[evt] = fn
end

-- Nombre de clés ANNONCÉES par une chaîne de présence C[octet]. Format :
-- "\1cle1\1cle2\1...\1" — un séparateur de plus que de clés. C'est le SEUL
-- point de comparaison indépendant des seaux M[] : sans lui, un seau de
-- données disparu ne se voit pas (mesuré : M[68] supprimé = 2 353 répliques
-- évaporées, et le banc restait vert).
function ClesAnnoncees(source)
    local usine = loadstring("return " .. source)
    if not usine then return -1 end
    local ok, s = pcall(usine)
    if not ok or type(s) ~= "string" then return -1 end
    local n = 0
    for _ in string.gmatch(s, "\1") do n = n + 1 end
    return n - 1
end

-- Compile UN seau de la base paresseuse dans une table ORDINAIRE (celle de la
-- base ne se parcourt pas), et en rend des couples étalés sur tout le seau.
-- C'est du Lua qui déséchappe, jamais nous.
function CouplesDuSeau(morceau, combien)
    local usine = loadstring("return {" .. morceau .. "}")
    if not usine then return nil, 0 end
    local ok, t = pcall(usine)
    if not ok or type(t) ~= "table" then return nil, 0 end
    local cles = {}
    for k in pairs(t) do cles[#cles + 1] = k end
    table.sort(cles)
    local out = {}
    -- Un seau plus petit que la demande ne doit pas rendre le même couple
    -- plusieurs fois : un doublon gonflerait le compte sans rien tester.
    local combien_reel = math.min(combien, #cles)
    for j = 0, combien_reel - 1 do
        local i = 1 + math.floor(j * #cles / combien_reel)
        out[#out + 1] = { cles[i], t[cles[i]] }
    end
    return out, #cles
end
"""


def couples_base(lua, combien_par_seau):
    """Lit les DEUX côtés du format paresseux, seau par seau.

    Rend (couples, entrées, tailles par seau côté M[], clés annoncées par
    seau côté C[], seaux illisibles). On lit les C[] alors qu'ils ne servent
    pas au prélèvement : c'est le croisement des deux côtés qui fait mordre
    le banc, parce que le corpus de test est prélevé DANS les M[] — un seau
    absent n'est simplement plus testé. C'est la même raison qui fait comparer
    le compte d'entrées à ENTREES_REFERENCE, la taille RELEVÉE de la base, et
    non à un plancher de misère qui se dégrade avec elle.
    """
    couples_fn = lua.globals().CouplesDuSeau
    annoncees_fn = lua.globals().ClesAnnoncees
    couples = []
    tailles, presences, muets = {}, {}, []

    vus = {"C": set(), "M": set()}

    def refuser_doublon(cote, octet):
        """Un octet écrit DEUX fois est une base malformée, pas un seau.

        La version d'avant écrasait la taille (« tailles[octet] = taille »)
        mais cumulait le compte d'entrées : une ligne M[] recopiée gonflait le
        total sans limite. Mesuré le 27/07/2026 sur une base rognée à 80 %
        (55 608 clés réelles) dont la ligne M[87] était réécrite 40 fois : le
        banc annonçait « 270488 répliques dans 66 seaux », 443 couples — au-
        dessus du plafond arithmétique de 66 seaux x COUPLES_PAR_SEAU — et
        rendait 0. On compte donc sur des seaux DISTINCTS (le « vus »
        ci-dessus, et non tailles : un seau illisible n'y entre pas).
        """
        if octet in vus[cote]:
            print("! seau %s[%d] écrit plusieurs fois : base malformée"
                  % (cote, octet))
            sys.exit(1)
        vus[cote].add(octet)

    with open(BASE_REP, encoding="utf-8") as f:
        for ligne in f:
            if ligne.startswith("C["):
                octet = int(ligne[2:ligne.index("]")])
                refuser_doublon("C", octet)
                presences[octet] = annoncees_fn(
                    ligne[ligne.index("=") + 1:].rstrip("\n"))
                continue
            if not ligne.startswith("M["):
                continue
            octet = int(ligne[2:ligne.index("]")])
            refuser_doublon("M", octet)
            debut = ligne.index("[==[") + 4
            fin = ligne.rindex("]==]")
            retour = couples_fn(ligne[debut:fin], combien_par_seau)
            table, taille = retour if isinstance(retour, tuple) else (None, 0)
            # Un seau qui ne compile PAS est un seau MORT en jeu : la table
            # paresseuse rend nil pour toutes ses clés (Core.lua:61-62). On ne
            # l'avale donc pas en silence — la version d'avant le comptait
            # comme un seau de 0 entrée et affichait tranquillement « 66 seaux ».
            if table is None:
                muets.append(octet)
                continue
            tailles[octet] = taille
            for i in range(1, len(table) + 1):
                couples.append((table[i][1], table[i][2]))
    # Compté sur les seaux DISTINCTS retenus, jamais ligne à ligne : c'est le
    # même dictionnaire qui sert de garde et de compte.
    return couples, sum(tailles.values()), tailles, presences, muets


def main():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(CONTEXTE)
    for rel in ("Core.lua", "Modules\\Chat.lua"):
        with open(os.path.join(ADDON, rel), encoding="utf-8") as f:
            lua.execute(f.read())

    # La VRAIE base livrée, chargée exactement comme le jeu la charge : le
    # fichier se termine par AscensionFR.DB.Repliques = ParesseuxTexte(C, M).
    with open(BASE_REP, encoding="utf-8") as f:
        lua.execute(f.read())

    # AVANT le moindre appel de filtre : AFR.CreatureParNomEN construit son
    # index inversé à sa PREMIÈRE demande et le garde (Core.lua:212). Peuplée
    # après, la créature n'y serait jamais entrée — et le test de l'émetteur
    # échouerait pour une raison qui n'a rien à voir avec l'addon.
    lua.execute('AscensionFR.DB.Creatures[42] = '
                '{ NE = "Mangy Wolf", N = "Loup galeux" }')

    g = lua.globals()
    substituer = g.AscensionFR.Substituer

    couples, entrees, tailles, presences, muets = couples_base(
        lua, COUPLES_PAR_SEAU)

    # Une réplique dont le français est identique à l'anglais (333 dans la
    # base : « $B$B », « $p AGGROED », didascalies non traduites) ne peut pas
    # se distinguer d'un raté : le filtre ne réécrit rien, à raison. On les
    # écarte du rejeu — 24 des 270 couples prélevés au 26/07/2026.
    couples = [(en, fr) for en, fr in couples if substituer(fr) != en]

    print("Base livrée : %d répliques dans %d seaux paresseux"
          % (entrees, len(tailles)))
    print("Rejeu : %d couples EN->FR x %d événements = %d vérifications\n"
          % (len(couples), len(EVENEMENTS), len(couples) * len(EVENEMENTS)))

    # --- Garde-fous de STRUCTURE, avant toute assertion --------------------
    # Ils existent parce que le corpus de test sort des M[] : sans eux, une
    # perte de DONNÉES ne se voyait pas. Mesuré sur bases fabriquées, du temps
    # où le seul filet était un plancher fixe à 60 000 : M[68] supprimé
    # (2 353 répliques) et les 5 seaux de l'étude supprimés (9 477 répliques,
    # 13,6 %) rendaient tous les deux code 0 et 0 échec.
    if muets:
        print("! %d seau(x) de données illisible(s) (loadstring échoue) : %s"
              % (len(muets), " ".join(repr(chr(o)) for o in muets)))
        sys.exit(1)
    aveugles = sorted(o for o in presences if presences[o] < 0)
    if aveugles:
        print("! %d chaîne(s) de présence C[] illisible(s) : %s"
              % (len(aveugles), " ".join(repr(chr(o)) for o in aveugles)))
        sys.exit(1)
    orphelins = sorted(set(presences) - set(tailles))
    if orphelins:
        print("! %d seau(x) annoncé(s) par C[] sans données M[] : %s"
              % (len(orphelins), " ".join(repr(chr(o)) for o in orphelins)))
        sys.exit(1)
    fantomes = sorted(set(tailles) - set(presences))
    if fantomes:
        print("! %d seau(x) de données M[] sans chaîne de présence C[] : %s"
              % (len(fantomes), " ".join(repr(chr(o)) for o in fantomes)))
        sys.exit(1)
    desaccords = sorted(o for o in tailles if tailles[o] != presences[o])
    if desaccords:
        print("! %d seau(x) où C[] et M[] ne comptent pas pareil : %s"
              % (len(desaccords), " ".join(
                  "%r C=%d M=%d" % (chr(o), presences[o], tailles[o])
                  for o in desaccords[:6])))
        sys.exit(1)

    disparus = [o for o in SEAUX_OBLIGATOIRES if o not in tailles]
    if disparus:
        print("! %d seau(x) de lettre absent(s) des DEUX côtés : %s — des "
              "répliques ont disparu sans laisser de trace"
              % (len(disparus), " ".join(repr(chr(o)) for o in disparus)))
        sys.exit(1)

    # La base a la bonne FORME, mais pas le bon POIDS : c'est le seul garde-fou
    # capable de voir une perte DIFFUSE, celle qui retire des répliques un peu
    # partout sans jamais vider un seau entier.
    plancher = int(ENTREES_REFERENCE * (1 - PERTE_TOLEREE))
    plafond = int(ENTREES_REFERENCE * (1 + GONFLEMENT_TOLERE))
    if entrees < plancher:
        print("! base des répliques rabougrie : %d entrées contre %d relevées "
              "le 26/07/2026 (%.1f %% de moins, plancher %d)."
              % (entrees, ENTREES_REFERENCE,
                 100.0 * (ENTREES_REFERENCE - entrees) / ENTREES_REFERENCE,
                 plancher))
        print("  Soit des répliques ont été perdues en chemin, soit la base a "
              "changé pour de bonnes raisons — dans ce cas seulement, "
              "remesurer et corriger ENTREES_REFERENCE.")
        sys.exit(1)
    if entrees > plafond:
        print("! base des répliques anormalement grosse : %d entrées contre "
              "%d relevées le 26/07/2026 (plafond %d) — base malformée ou "
              "repère à remesurer" % (entrees, ENTREES_REFERENCE, plafond))
        sys.exit(1)
    if len(couples) < COUPLES_MINIMUM:
        print("! %d couples lus seulement (minimum %d) : le banc ne prouve "
              "rien" % (len(couples), COUPLES_MINIMUM))
        sys.exit(1)

    manquants = [ev for ev in EVENEMENTS if not g._FILTRES[ev]]
    if manquants:
        print("! aucun filtre posé sur %s" % ", ".join(manquants))
        sys.exit(1)

    echecs = 0

    def verifier(description, obtenu, attendu):
        nonlocal echecs
        if obtenu == attendu:
            print("  ok      %-34s %s" % (description, str(obtenu)[:46]))
        else:
            print("  ECHEC   %s\n          obtenu %r\n          attendu %r"
                  % (description, obtenu, attendu))
            echecs += 1

    def verifier_muet(description, obtenu, attendu):
        """Même contrat, mais silencieux quand ça passe : 1 000 lignes « ok »
        noieraient le rapport. Les échecs, eux, s'écrivent en entier."""
        nonlocal echecs
        if obtenu == attendu:
            return True
        print("  ECHEC   %s\n          obtenu %r\n          attendu %r"
              % (description, obtenu, attendu))
        echecs += 1
        return False

    # --- Le rejeu : chaque couple, sur chacun des 4 événements de PNJ -------
    for ev in EVENEMENTS:
        filtre = g._FILTRES[ev]
        passes = 0
        for en, fr in couples:
            retour = filtre(None, ev, en, "Quelqu'un")
            message = retour[1] if isinstance(retour, tuple) else None
            if verifier_muet("réplique traduite (%s) : %r" % (ev, en[:60]),
                             message, substituer(fr)):
                passes += 1
        print("  ok      %-30s %d/%d répliques rendues en français"
              % (ev, passes, len(couples)))

    # --- Les variables du texte officiel sont bien résolues ----------------
    # Une entrée RÉELLE de la base, à $n et $g : si AFR.Substituer cessait de
    # tourner, tout le rejeu ci-dessus passerait quand même (il compare à
    # Substituer(fr)) — pas celle-ci, dont l'attendu est écrit en toutes
    # lettres. UnitName = <joueur>, UnitSex = 2 (masculin).
    # Le jour où cette traduction bouge, prendre une autre réplique à $n et $g
    # (3 228 entrées de la base en contiennent, mesuré le 26/07/2026) et
    # réécrire l'attendu à la main.
    print()
    retour = g._FILTRES["CHAT_MSG_MONSTER_YELL"](
        None, "CHAT_MSG_MONSTER_YELL",
        "You do not fight alone! Unleash my storm upon these invaders!",
        "Quelqu'un")
    verifier("$n et $g résolus dans la réplique",
             retour[1] if isinstance(retour, tuple) else None,
             "<joueur>, vous ne vous battez pas seul\u00a0! Déchaînez ma "
             "tempête sur ces envahisseurs\u00a0!")

    # --- Témoins de CONTENU, attendu écrit à la main -----------------------
    # Le rejeu de masse ci-dessus compare la base à elle-même : il ne peut PAS
    # voir une base dont le français serait faux. Mesuré le 27/07/2026 sur une
    # base fabriquée où les 69 477 traductions sont remplacées par « Blah » :
    # les 1 080 rejeux de masse passent TOUS (270/270 sur chacun des quatre
    # événements), et seuls les témoins tombent — 5 échecs, code 1.
    # Ces témoins-là sont donc les seuls à mordre — quatre entrées
    # RÉELLES, prises dans quatre seaux différents (G, I, T, W), sans variable
    # ni code couleur, dont le français est recopié ici à la main. Avec celui
    # à $n et $g juste au-dessus, cela fait cinq contrôles de contenu.
    # Le jour où l'une de ces traductions change pour de bonnes raisons : la
    # relire, puis recopier le nouveau texte ici.
    for anglais, francais in (
        ("Groundbreaker Brojai is reviving a Ruined Guardian.",
         "Le casse-terre Brojai ranime un gardien dévasté."),
        ("I long for the frozen wastes of Northrend.",
         "Les déserts gelés du Norfendre me manquent."),
        ("The Sons of Lightning will have their vengeance!",
         "Les Fils de la Foudre se vengeront\u00a0!"),
        ("We drove back the sha, your kind will fall before us as well.",
         "Nous avons repoussé les sha, votre race aussi reculera devant "
         "nous."),
    ):
        retour = g._FILTRES["CHAT_MSG_MONSTER_SAY"](
            None, "CHAT_MSG_MONSTER_SAY", anglais, "Quelqu'un")
        verifier("témoin figé : %r" % anglais[:26],
                 retour[1] if isinstance(retour, tuple) else None, francais)

    # --- Le nom de l'émetteur PNJ doit être traduit aussi -------------------
    retour = g._FILTRES["CHAT_MSG_MONSTER_YELL"](
        None, "CHAT_MSG_MONSTER_YELL", couples[0][0], "Mangy Wolf")
    emetteur = retour[2] if isinstance(retour, tuple) else None
    verifier("émetteur PNJ traduit", emetteur, "Loup galeux")

    # --- Une réplique inconnue ne doit pas être modifiée --------------------
    # On vérifie la FORME du retour, pas seulement son contenu : un filtre qui
    # renverrait une réécriture vide passerait le test « message = None ».
    r = g._FILTRES["CHAT_MSG_MONSTER_SAY"](
        None, "CHAT_MSG_MONSTER_SAY", "Zzzxxq inconnu total 99", "Bob")
    verifier("réplique inconnue -> aucune réécriture",
             isinstance(r, tuple), False)

    print()
    print("%d échec(s)" % echecs)
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
