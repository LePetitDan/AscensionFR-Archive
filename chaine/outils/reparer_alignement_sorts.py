# -*- coding: utf-8 -*-
"""Répare les trous d'alignement des sorts (lot 14 §1) — outil REJOUABLE.

LE MAL (mesuré au moteur réel, étude lot 14 volet 1, 28/07/2026) : sur
49 676 entrées de la base fusionnée portant un D français, 2 433 restaient
en anglais quand on rejouait le VRAI moteur de l'addon (TraduireInfobulleSort
complet, lupa.lua51) contre l'info-bulle simulée depuis le modèle anglais DE.
La cause n'est presque jamais le marqueur lui-même : la jointure PackFR PAR
IDENTIFIANT a posé des valeurs françaises structurellement étrangères à leur
clé anglaise (le D du sort 3599 porte @learns:92159@ que son DE n'a pas ->
abandon de TOUTE la description, Modules/Sorts.lua, appliquer_valeurs).

TROIS RÉPARATIONS, chacune sous LE GARDE-FOU fail→success : on ne touche une
entrée QUE si elle échoue au banc, on n'adopte la réparation QUE si le moteur
la voit réussir après. Sans ce garde-fou, 18 entrées saines seraient touchées
dont 4 perdraient leur alignement (mesuré à l'étude) ; avec lui, 0 casse.

  a) RESYNC : retirer du D les marqueurs @…@ sans jumeau dans le DE, et
     égaliser les blocs @ext: excédentaires (101 réparés à l'étude, dont le
     3599 de la capture de Dan) ;
  b) REMAP  : variables $<id>… du D dont id+1 100 000 existe côté DE — les
     clones décalés d'Ascension, dont le D vient du frFR officiel du sort de
     base (881 réparés à l'étude) ;
  c) PURGE  : les faux appariements PURS (le D ne traduit PAS le DE : toutes
     ses variables manquantes ont des ids ni présents ni décalés — 649 à
     l'étude) PLUS la famille « Follow Up » du sceptique (11 ids : du
     Franglais qui S'ALIGNE, donc invisible au banc — prouvé à la lecture,
     pas au verdict). La valeur quitte le cache -> retour en file de
     traduction à la prochaine régénération, voie du lot 13.

Tout passe par traductions/sorts.json (la valeur sous SA clé anglaise) : la
base DB_Sorts.lua n'est PAS régénérée ici — c'est la chaîne complète qui le
fera. La PROVENANCE est exigée avant chaque écriture : la valeur du cache
doit être octet pour octet le D de la base (prouvé pour 3599 à l'étude :
cache == base fusionnée == packfr_sorts.json[3599].D).

LA PREUVE avant toute écriture : la base est modifiée EN MÉMOIRE, le banc
complet est rejoué sur un moteur VIERGE (le coupe-circuit echecsRecents du
module interdit de rejouer un même contenu après échec — leçon de l'étude),
et les sorties HACHÉES sont comparées : rien ne doit changer hors des
réparations et purges prouvées. Un seul écart inattendu -> refus d'écrire.

Une clé du cache peut servir PLUSIEURS sorts (même texte anglais) : si l'un
d'eux est SAIN au banc (il survit par son D2 de correction), réparer ou
purger la clé changerait son affichage en douce — la clé est alors EXCLUE et
signalée, même régime que le garde-fou.

Usage :
    python outils/reparer_alignement_sorts.py              # simulation
    python outils/reparer_alignement_sorts.py --appliquer  # écrit (+ sauvegarde)

Rapport : rapports/alignement_sorts.txt. IDEMPOTENT : une valeur déjà
réparée (elle passe le banc) ou déjà purgée est reconnue et laissée en paix.
"""
import json
import os
import re
import shutil
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diagnostiquer_signalements as diag  # noqa: E402  (impose la locale C)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASES = ("DB_Sorts.lua", "DB_SortsCorrections.lua", "DB_SortsLignes.lua")
CHEMIN_CACHE = os.path.join(BASE, "traductions", "sorts.json")
RAPPORTS = os.path.join(BASE, "rapports")
RAPPORT = os.path.join(RAPPORTS, "alignement_sorts.txt")
OFFSET = 1100000
# PLANCHER DE POPULATION du banc moteur (--banc-seul). En dessous, le banc
# REFUSE au lieu de rendre vert : il n'a manifestement pas lu les bases.
# La population réelle est d'environ 49 000 entrées ; 10 000 laisse donc
# cinq fois la marge d'une variation légitime du corpus, tout en attrapant
# le cas qui compte (chargement raté -> 0, ou une poignée d'entrées).
# C'est un CHOIX, pas une mesure : à remonter si le corpus grossit.
PLANCHER_POPULATION = 10000

# La famille « Follow Up » (sceptique du lot 14, s1/s2) : onze sorts dont le
# D est « Frappez un ennemi pour $s2% des dégâts de l'arme … and gain Follow
# jusqu'à … » — « and gain » non traduit, « Follow Up » massacré en « Follow
# jusqu'à ». Ces D s'ALIGNENT (structure conforme), le banc les compte donc
# « traduit » : ils sont listés ici À LA MAIN, sur preuve de lecture, parce
# qu'aucun verdict mécanique ne les attrape. (Le bon de commande en énumérait
# 10 ; la liste MESURÉE du sceptique — s1_resultat.json, sorties non-UTF-8
# valides — en compte 11, avec 567537.)
FOLLOW_UP = (567535, 567536, 567537, 805406, 806857, 806858, 806859,
             806860, 806861, 806862, 806863)

# ---------------------------------------------------------------------------
# Le décor Lua : repris du banc du volet 1 (étude lot 14), reproduit à
# l'identique par le sceptique (jeu d'échecs strictement égal, 2 433/49 676).
# La fausse info-bulle a 2 lignes ; l'affichage client est SIMULÉ depuis le
# modèle DE par le découpeur DU MOTEUR (AFR.DecouperModele), pas par une
# imitation.
# ---------------------------------------------------------------------------
HARNAIS = r"""
-- Stubs manquants pour TraduireInfobulleSort hors jeu
function GetSpellInfo() return nil end

-- Fausse info-bulle : 2 lignes (nom, description simulee)
local LIGNES = {}
FakeTooltip = {}
function FakeTooltip:GetName() return "FakeTooltip" end
function FakeTooltip:NumLines() return #LIGNES end
function FakeTooltip:IsShown() return true end
function FakeTooltip:Show() end
local function FS(t)
    local f = { _t = t }
    function f:GetText() return self._t end
    function f:SetText(v) self._t = v end
    return f
end
function PoserLignes(...)
    LIGNES = {}
    for i = 1, select("#", ...) do
        local l = FS(select(i, ...))
        LIGNES[i] = l
        _G["FakeTooltipTextLeft" .. i] = l
    end
    for i = select("#", ...) + 1, 12 do _G["FakeTooltipTextLeft" .. i] = nil end
end
function LireLigne(i) return LIGNES[i] and LIGNES[i]:GetText() end

local function denuder(texte)
    if not texte then return texte end
    texte = string.gsub(texte, "|c%x%x%x%x%x%x%x%x", "")
    return (string.gsub(texte, "|r", ""))
end
Denuder = denuder

local simuler

local function valeur_pour(variable)
    local interieur = string.match(variable, "^%$%?[^%[]*%[(.-)%]")
    if string.sub(variable, 1, 2) == "$?" and interieur then
        return simuler(interieur)
    end
    if string.sub(variable, 1, 2) == "${" then return "34" end
    if variable == "@ext:" or variable == ":ext@" then return "" end
    if string.find(variable, "^@ifknown:") then return "" end
    if string.find(variable, "^@ifnotknown:") then
        local contenu = string.match(variable, "^@ifnotknown:(.-):ifnotknown@$")
        return contenu and simuler(contenu) or ""
    end
    if string.find(variable, "^@wflocation:") then return "somewhere" end
    if string.match(variable, "^@%a+:%d+:%-?%d+@$") then
        return "\nChild Spell\nDeals 34 damage."
    end
    if string.find(variable, "^@") then return "" end
    if string.match(variable, "^%$[GgLl]") then
        local corps = string.match(variable, "^%$[GgLl](.-);$") or ""
        local derniere = corps
        for morceau in string.gmatch(corps, "[^:]+") do derniere = morceau end
        return derniere
    end
    if string.match(variable, "^%$@%a+$") then return "Spell Name" end
    if string.match(variable, "^%$%d*[dD]%d*$") then return "45 sec" end
    return "34"
end

function simuler(modele)
    local litteraux, variables = AscensionFR.DecouperModele(modele)
    local morceaux = {}
    for i, litteral in ipairs(litteraux) do
        morceaux[#morceaux + 1] = litteral
        if variables[i] then
            morceaux[#morceaux + 1] = valeur_pour(variables[i])
        end
    end
    return table.concat(morceaux)
end
Simuler = simuler

-- LA SECONDE SIMULATION, « valeur plausible » (bloc D du programme 5).
-- Le bouchon numérique du simulateur vaut « 34 » — deux caractères. Or le
-- module refuse de traduire un affiché de 10 caractères ou moins. Résultat :
-- « +$s1 Armor. » se simule en « +34 Armor. », soit EXACTEMENT 10, et le banc
-- comptait un échec que le jeu n'a pas — une valeur d'armure réelle en fait
-- « +1350 Armor. », que le module traduit très bien.
-- On ne change PAS le simulateur principal (il faudrait rebâtir toute la
-- ligne de base des hachages pour huit entrées) : on REJUGE seulement les
-- affichés courts avec une valeur plausible. Un texte réellement court —
-- « Stunned. », « [PH] » — n'a aucune variable, ressort identique, et reste
-- donc écarté : le classement se fait tout seul, sans liste à tenir.
-- Les grandeurs du jeu, pour que « plausible » veuille dire quelque chose :
-- niveau maximum 80 (client 3.3.5a), puissances d'attaque/de sort d'un
-- personnage équipé de fin d'extension.
local GRANDEURS = {PL = 80, AP = 2000, RAP = 2000, SP = 1500}

local function valeur_plausible(variable)
    -- « ${4.4*$PL} » n'est pas un bouchon à deviner : c'est une expression
    -- ARITHMÉTIQUE qu'on sait calculer. La calculer vaut mieux que choisir
    -- un nombre au hasard — « +${4.4*$PL} Armor » fait 10 caractères une
    -- fois évalué (352), donc le module le décline VRAIMENT, alors qu'un
    -- bouchon à 4 chiffres l'aurait déclaré récupéré à tort.
    local interieur = string.match(variable, "^%${(.*)}$")
    if interieur then
        local expr = string.gsub(interieur, "%$(%a+)", function(nom)
            return tostring(GRANDEURS[string.upper(nom)] or 100)
        end)
        expr = string.gsub(expr, "%$%d*%a+%d*", "100")
        local f = loadstring("return " .. expr)
        if f then
            local ok, valeur = pcall(f)
            if ok and type(valeur) == "number" then
                return tostring(math.floor(valeur))
            end
        end
        return "1350"
    end
    local v = valeur_pour(variable)
    if v == "34" then return "1350" end
    return v
end

function SimulerPlausible(modele)
    local litteraux, variables = AscensionFR.DecouperModele(modele)
    local morceaux = {}
    for i, litteral in ipairs(litteraux) do
        morceaux[#morceaux + 1] = litteral
        if variables[i] then
            morceaux[#morceaux + 1] = valeur_plausible(variables[i])
        end
    end
    return table.concat(morceaux)
end

-- Classification structurelle (reproduit l'indexation d'appliquer_valeurs :
-- clés = variables du modèle EN dénudé normalisé ; recherche = variables du
-- modèle FR dénudé). Rend les variables FR sans jumeau EN.
local function normaliser(texte)
    if not texte then return nil end
    texte = string.gsub(texte, "\r\n", "\n")
    return (string.gsub(texte, "\r", "\n"))
end

function ClasserStructure(D, DE)
    local en_nu = normaliser(denuder(DE))
    local _, vars_en = AscensionFR.DecouperModele(en_nu)
    local en_set, prefixes_en = {}, {}
    for _, v in ipairs(vars_en) do
        en_set[v] = true
        local p = string.match(v, "^(%$%?[^%[]*)%[")
        if p then prefixes_en[p] = true end
    end
    local fr_nu = denuder(D)
    local _, vars_fr = AscensionFR.DecouperModele(fr_nu)
    local manquantes = {}
    for _, v in ipairs(vars_fr) do
        if not en_set[v] then
            local p = string.match(v, "^(%$%?[^%[]*)%[")
            if not (p and prefixes_en[p]) then
                manquantes[#manquantes + 1] = v
            end
        end
    end
    return manquantes
end

-- Variables du modèle EN (dénudé, normalisé) d'un sort : sert au diagnostic
-- clone décalé / faux appariement.
function VarsEn(id)
    local s = AscensionFR.DB.Sorts[id]
    if not (s and s.DE) then return nil end
    local _, vars = AscensionFR.DecouperModele(normaliser(denuder(s.DE)))
    return vars
end

-- LE GARDE-FOU : un D d'essai n'est adopté que si le moteur rend le français
-- face à l'affichage simulé depuis le DE du sort.
function VerifierD(id, d_essai)
    local s = AscensionFR.DB.Sorts[id]
    if not (s and s.DE) then return false end
    local affiche = Simuler(s.DE)
    if string.len(affiche) <= 10 then return false end
    return AscensionFR.TraduireTexteSort(d_essai, s.DE, affiche) ~= nil
end
"""

BOUCLE = r"""
-- Passe complète : verdict par entrée + sorties conservées pour hachage.
Sorties = {}
function ToutMesurer(sans_communaute)
    AscensionFRSaved = { Options = { sansCommunaute = sans_communaute } }
    Sorties = {}
    local res = {}
    local n = 0
    for id, s in pairs(AscensionFR.DB.Sorts) do
        if type(s) == "table" and s.D then
            n = n + 1
            local ligne = {}
            ligne.id = id
            if not s.DE then
                ligne.verdict = "D_sans_DE"
            else
                local affiche = Simuler(s.DE)
                ligne.affiche_len = string.len(affiche)
                PoserLignes("Spell Name Line", affiche)
                AscensionFR.TraduireInfobulleSort(FakeTooltip, id)
                local apres = LireLigne(2)
                if apres ~= affiche then
                    ligne.verdict = "traduit"
                    Sorties[id] = apres
                elseif ligne.affiche_len <= 10 then
                    -- Sous la porte du module : le bouchon du simulateur
                    -- peut avoir raccourci l'affiché. On REJUGE avec une
                    -- valeur plausible avant d'accuser le moteur.
                    local long = SimulerPlausible(s.DE)
                    if string.len(long) > 10 then
                        PoserLignes("Spell Name Line", long)
                        AscensionFR.TraduireInfobulleSort(FakeTooltip, id)
                        local apres2 = LireLigne(2)
                        if apres2 ~= long then
                            ligne.verdict = "traduit"
                            ligne.plausible = true
                            Sorties[id] = apres2
                        else
                            ligne.verdict = "anglais"
                        end
                    else
                        -- Même avec une valeur plausible l'affiché reste
                        -- ≤ 10 : le texte anglais est court PAR NATURE
                        -- (« Stunned. », « [PH] »). Le module le décline
                        -- par construction ; ce n'est pas un échec du
                        -- moteur, et le banc ne sait pas l'éprouver
                        -- autrement. Compté à part, jamais mêlé aux vrais.
                        ligne.verdict = "court_par_nature"
                    end
                else
                    ligne.verdict = "anglais"
                end
            end
            res[#res + 1] = ligne
        end
    end
    return res, n
end

-- djb2 côté Lua : certaines sorties ne sont pas de l'UTF-8 valide (l'affaire
-- du trim 0xA0 sous locale française — corrigée par la locale C, mais on ne
-- fait plus JAMAIS transiter les sorties par un décodage Python).
function TousLesHashes()
    local out = {}
    for id, t in pairs(Sorties) do
        local h = 5381
        for i = 1, #t do
            h = (h * 33 + string.byte(t, i)) % 4294967296
        end
        out[id] = h .. ":" .. #t
    end
    return out
end

-- Qui d'autre porte une des clés visées ? (une clé du cache peut servir
-- plusieurs sorts : même texte anglais)
function RelevePartage(cles)
    local out = {}
    for id, s in pairs(AscensionFR.DB.Sorts) do
        if type(s) == "table" and s.D and s.DE and cles[s.DE] then
            local liste = out[s.DE]
            if not liste then liste = {} out[s.DE] = liste end
            liste[#liste + 1] = id
        end
    end
    return out
end
"""

# Marqueurs POINT maison (@learns:92159@, @req:8921@, @unlockby:635@,
# @req:1122520:req@…) — mêmes formes que MOTIFS_VARIABLE de l'addon.
RE_MARQUEUR = re.compile(r"@[a-zA-Z]+:\d+(?::[a-zA-Z]+)?@")
RE_EXT = re.compile(r"@ext:(.*?):ext@", re.S)
RE_VAR_NUM = re.compile(r"\$(\d+)([a-zA-Z]\d*)")
RE_ID_VAR = re.compile(r"^\$(\d+)[a-zA-Z]")


def resynchroniser(D, DE):
    """Le D réaligné sur la structure du DE, ou None si rien à faire.

    Code de l'étude (volet 1, reparer_et_prouver.py), validé au moteur :
    131 candidats, 101 réparés, sortie de 3599 identique caractère à
    caractère à la preuve écran."""
    d2 = D
    # 1. marqueurs point présents en FR, absents de l'EN -> retirés
    for m in RE_MARQUEUR.finditer(D):
        marq = m.group(0)
        if not marq.startswith("@ext") and marq not in DE:
            d2 = re.sub(re.escape(marq) + r"\r?\n?", "", d2, count=1)
    # 2. blocs @ext: du FR sans @ext: dans l'EN : égaliser les paragraphes
    if "@ext:" in d2 and "@ext:" not in DE:
        sep = "\r\n\r\n" if "\r\n" in d2 else "\n\n"
        paras_fr = d2.split(sep)
        nb_en = len(re.split(r"(?:\r\n|\n){2,}", DE))
        while len(paras_fr) > nb_en and paras_fr \
                and RE_EXT.fullmatch(paras_fr[-1].strip()):
            paras_fr.pop()
        d2 = sep.join(paras_fr)
        d2 = RE_EXT.sub(lambda m: m.group(1), d2)
    return d2 if d2 != D else None


def remap_clones(D, DE):
    """Le D aux variables remappées vers les ids décalés (+1 100 000), ou
    None. Code de l'étude (clones_et_provenance.py) : 902 tentés, 881
    vérifiés au moteur. Le D vient du frFR officiel du sort de BASE et
    référence $64843s2 quand le DE du clone porte $1164843s2."""
    ids_en = {int(m.group(1)) for m in RE_VAR_NUM.finditer(DE)}
    if not ids_en:
        return None

    def rem(m):
        vid = int(m.group(1))
        if vid not in ids_en and vid + OFFSET in ids_en:
            return "$%d%s" % (vid + OFFSET, m.group(2))
        return m.group(0)

    d2 = RE_VAR_NUM.sub(rem, D)
    return d2 if d2 != D else None


def famille_variable(v, en_ids):
    """Famille d'une variable FR sans jumeau EN (mêmes règles que l'étude)."""
    if v.startswith(("@learns:", "@req:", "@unlockby:")):
        return "marqueur_point"
    if v in ("@ext:", ":ext@"):
        return "marqueur_ext"
    if v.startswith(("@ifknown", "@ifnotknown")):
        return "marqueur_ifknown"
    if v.startswith("@"):
        return "marqueur_autre"
    if re.match(r"^\$[GgLl]", v):
        return "l_traduit"
    if "\n" in v or "\r" in v:
        return "var_multiligne"
    m = RE_ID_VAR.match(v)
    if m and int(m.group(1)) + OFFSET in en_ids:
        return "clone_decale"
    return "faux_appariement"


def charger_banc():
    """Un moteur VIERGE (Core + Sorts réels + bases + décor du banc)."""
    lua = diag.charger_moteur(BASES)
    lua.execute(HARNAIS)
    lua.execute(BOUCLE)
    return lua


def mesurer(lua):
    """(verdicts {id: (verdict, longueur affichée)}, hashes {id: hash})."""
    g = lua.globals()
    res, total = g.ToutMesurer(True)
    verdicts = {}
    for i in range(1, len(res) + 1):
        ligne = res[i]
        alen = ligne.affiche_len
        verdicts[int(ligne.id)] = (str(ligne.verdict),
                                   int(alen) if alen is not None else None)
    hashes = {int(k): str(v) for k, v in g.TousLesHashes().items()}
    return verdicts, hashes, int(total)


def lire_champs(g, sid):
    """(D, DE) en str, ou (None, None) si illisible."""
    s = g.AscensionFR.DB.Sorts[sid]
    if s is None:
        return None, None
    try:
        return (str(s.D) if s.D else None), (str(s.DE) if s.DE else None)
    except UnicodeDecodeError:
        return None, None


def main():
    # --banc-seul [seuil] : MESURE population entière et rien d'autre —
    # c'est l'entrée du banc de santé (bloc D1, 29/07/2026). Code retour :
    # 0 sous le seuil, 1 au-dessus. La seule preuve population entière ne
    # vivait que dans cet outil de réparation, hors de toute routine :
    # personne ne surveillait le chiffre.
    if "--banc-seul" in sys.argv:
        idx = sys.argv.index("--banc-seul")
        try:
            seuil = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            seuil = 1200
        t0 = time.time()
        lua = charger_banc()
        verdicts, _hashes, total = mesurer(lua)
        n_echecs = sum(1 for v, _ in verdicts.values() if v == "anglais")
        n_courts = sum(1 for v, _ in verdicts.values()
                       if v == "court_par_nature")
        print("banc moteur population entière : %d entrées, %d échecs "
              "(seuil %d, %.1f s)" % (total, n_echecs, seuil,
                                      time.time() - t0))
        print("  + %d texte(s) anglais COURTS PAR NATURE (≤ 10 car. même "
              "avec une valeur plausible) : le module les décline par "
              "construction, comptés à part" % n_courts)
        # LE ZÉRO D'INSTRUMENT (mesuré au programme 14, 01/08/2026). Le
        # verdict ne portait que sur n_echecs : « 0 échec sur 49 283 » et
        # « 0 échec sur RIEN » rendaient tous deux 0, c'est-à-dire VERT.
        # Sans les bases, ce banc — l'étape n° 1 du banc de santé —
        # certifiait donc une mesure qu'il n'avait pas faite.
        # Un banc doit d'abord prouver qu'il a MESURÉ, ensuite seulement
        # dire ce qu'il a trouvé.
        if total < PLANCHER_POPULATION:
            print("🛑 REFUS : %d entrée(s) mesurée(s), plancher %d. Le banc "
                  "n'a pas vu la population — bases absentes ou moteur qui "
                  "n'a pas chargé. Un « 0 échec » sur ce total ne veut RIEN "
                  "dire." % (total, PLANCHER_POPULATION))
            return 1
        return 0 if n_echecs <= seuil else 1

    appliquer = "--appliquer" in sys.argv
    lignes_rapport = []

    def dire(texte=""):
        print(texte)
        lignes_rapport.append(texte)

    dire("RÉPARATION DES TROUS D'ALIGNEMENT DES SORTS — %s"
         % time.strftime("%d/%m/%Y %H:%M"))
    dire("mode : %s" % ("APPLICATION" if appliquer else "simulation"))
    dire("=" * 66)

    with open(CHEMIN_CACHE, encoding="utf-8") as f:
        cache = json.load(f)
    descs = cache.get("descriptions", {})

    t0 = time.time()
    lua = charger_banc()
    g = lua.globals()
    verdicts, hashes_avant, total = mesurer(lua)
    echecs = sorted(i for i, (v, _) in verdicts.items() if v == "anglais")
    dire("banc AVANT : %d entrées avec D, %d échecs (%.1f s)"
         % (total, len(echecs), time.time() - t0))

    # ------------------------------------------------------------------
    # Plan de réparation, id par id, sous le garde-fou fail→success.
    # ------------------------------------------------------------------
    plan = {}        # clé EN -> {"avant", "apres" (None = purge), "voie",
    #                             "ids": [ids en échec plannifiés]}
    compte = {"resync": 0, "remap": 0, "purge_faux": 0, "follow_up": 0,
              "deja_conforme": 0, "deja_purge": 0, "hors_cache": 0,
              "cache_divergent": 0, "restant": 0, "courte": 0,
              "faux_hors_cache": 0}
    exemples_divergents = []

    def est_faux_pur(sid, D, DE):
        """Toutes les variables FR manquantes sont des $<id> ni présents ni
        décalés : le D est le français d'un autre sort."""
        manquantes = g.ClasserStructure(D, DE)
        mq = [str(x) for x in list(manquantes.values())] if manquantes else []
        if not mq:
            return False
        vars_en = g.VarsEn(sid)
        en_ids = set()
        if vars_en:
            for x in list(vars_en.values()):
                m = RE_ID_VAR.match(str(x))
                if m:
                    en_ids.add(int(m.group(1)))
        return {famille_variable(x, en_ids) for x in mq} \
            == {"faux_appariement"}

    def planifier(cle, avant, apres, voie, sid):
        e = plan.get(cle)
        if e is None:
            plan[cle] = {"avant": avant, "apres": apres, "voie": voie,
                         "ids": [sid]}
            return True
        # même clé -> même D, même DE : la réparation est déterministe, une
        # divergence ici serait un bug de l'outil.
        if e["apres"] != apres or e["voie"] != voie:
            raise AssertionError("réparations divergentes pour une même clé")
        e["ids"].append(sid)
        return True

    for sid in echecs:
        D, DE = lire_champs(g, sid)
        if not D or not DE:
            compte["restant"] += 1
            continue
        v = descs.get(DE)
        if v is None:
            # Le D ne vient pas de traductions/sorts.json (voie officielle
            # par ID, corrections, récolte) : ce lot ne peut pas le réparer
            # par le cache. Les faux appariements de cette veine sont
            # comptés à part — c'est le reliquat à traiter par une autre
            # voie (mesuré : 362 des 649 faux de l'étude sont ici).
            compte["hors_cache"] += 1
            if est_faux_pur(sid, D, DE):
                compte["faux_hors_cache"] += 1
            continue
        if v != D:
            # Idempotence : une valeur déjà réparée au cache passe le banc
            # (la base, elle, ne sera au niveau qu'à la régénération).
            if g.VerifierD(sid, v):
                compte["deja_conforme"] += 1
            else:
                compte["cache_divergent"] += 1
                if len(exemples_divergents) < 5:
                    exemples_divergents.append(sid)
            continue
        # a) RESYNC
        d_rep = resynchroniser(D, DE)
        if d_rep is not None and g.VerifierD(sid, d_rep):
            planifier(DE, v, d_rep, "resync", sid)
            compte["resync"] += 1
            continue
        # b) REMAP clones décalés
        d_rem = remap_clones(D, DE)
        if d_rem is not None and g.VerifierD(sid, d_rem):
            planifier(DE, v, d_rem, "remap", sid)
            compte["remap"] += 1
            continue
        # c) PURGE des faux appariements PURS : toutes les variables
        # manquantes sont des $<id> ni présents ni décalés — le D est le
        # français d'un AUTRE sort, le resynchroniser serait maquiller un
        # contenu faux. (Les affichés courts sont écartés : leur échec tient
        # à la porte len>10 du module, pas à la structure.)
        alen = verdicts[sid][1]
        if alen is not None and alen <= 10:
            compte["courte"] += 1
            continue
        if est_faux_pur(sid, D, DE):
            planifier(DE, v, None, "purge_faux", sid)
            compte["purge_faux"] += 1
            continue
        compte["restant"] += 1

    # La famille Follow Up : hors banc (elle s'aligne), purge sur preuve de
    # lecture. Provenance exigée comme pour le reste.
    for sid in FOLLOW_UP:
        D, DE = lire_champs(g, sid)
        if not D or not DE:
            continue
        v = descs.get(DE)
        if v is None:
            compte["deja_purge"] += 1
            continue
        if v != D:
            compte["cache_divergent"] += 1
            continue
        if DE not in plan:
            planifier(DE, v, None, "follow_up", sid)
        elif sid not in plan[DE]["ids"]:
            plan[DE]["ids"].append(sid)
        compte["follow_up"] += 1

    dire("")
    dire("PLAN (garde-fou fail→success, provenance cache==base exigée) :")
    dire("  resync marqueurs        : %5d échec(s) réparé(s)"
         % compte["resync"])
    dire("  remap clones +1 100 000 : %5d échec(s) réparé(s)"
         % compte["remap"])
    dire("  purge faux appariements : %5d échec(s) -> retour en file"
         % compte["purge_faux"])
    dire("  purge « Follow Up »     : %5d id(s) (franglais qui s'aligne)"
         % compte["follow_up"])
    dire("  déjà réparés au cache   : %5d (idempotence)"
         % compte["deja_conforme"])
    dire("  déjà purgés du cache    : %5d (idempotence)"
         % compte["deja_purge"])
    dire("  hors cache (autre voie) : %5d — dont %d faux appariements"
         " (voie officielle par ID / corrections, pas ce lot)"
         % (compte["hors_cache"], compte["faux_hors_cache"]))
    dire("  cache divergent (à voir): %5d %s"
         % (compte["cache_divergent"], exemples_divergents or ""))
    # Ceux-là ne sont plus dans « echecs » : mesurer() leur donne le verdict
    # court_par_nature. On les affiche quand même, pour qu'ils restent VUS.
    dire("  courts par nature       : %5d (≤ 10 car. même avec une valeur "
         "plausible — le module les décline, ce ne sont pas des échecs)"
         % sum(1 for v, _ in verdicts.items()
               if verdicts[v][0] == "court_par_nature"))
    dire("  restant sans réparation : %5d" % compte["restant"])
    dire("  clés du cache touchées  : %5d" % len(plan))

    # ------------------------------------------------------------------
    # Les partageurs : une clé servant AUSSI un sort sain au banc est
    # exclue (la toucher changerait un affichage qui marche aujourd'hui).
    # ------------------------------------------------------------------
    if plan:
        cles_lua = lua.table_from({cle: True for cle in plan})
        partage = g.RelevePartage(cles_lua)
        exclusions = []
        for cle, e in list(plan.items()):
            sharers = [int(x) for x in list(partage[cle].values())]
            for sid in sharers:
                if sid in e["ids"]:
                    continue
                D, _ = lire_champs(g, sid)
                if D != e["avant"]:
                    continue        # son D ne vient pas (plus) de cette clé
                verdict = verdicts.get(sid, ("?", None))[0]
                if verdict == "traduit" and e["voie"] != "follow_up":
                    exclusions.append((cle, sid, e["voie"]))
                    del plan[cle]
                    break
                # échec partageant la clé : il profite de la même réparation
                e["ids"].append(sid)
        dire("")
        if exclusions:
            dire("CLÉS EXCLUES (un sort SAIN partage la clé — la toucher"
                 " changerait son affichage) : %d" % len(exclusions))
            for cle, sid, voie in exclusions[:10]:
                dire("  sort sain %d, voie %s, clé %r"
                     % (sid, voie, cle[:60]))
        else:
            dire("partage de clés : aucun sort sain ne partage une clé"
                 " touchée — rien à exclure")

    ids_repares = sorted(i for e in plan.values() if e["apres"] is not None
                         for i in e["ids"])
    ids_purges = sorted(i for e in plan.values() if e["apres"] is None
                        for i in e["ids"])

    # Le COMPTE EXACT, après exclusions : c'est lui qui fait foi.
    dire("")
    dire("COMPTE FINAL (après exclusion des clés partagées) :")
    for voie in ("resync", "remap", "purge_faux", "follow_up"):
        cles_v = [c for c, e in plan.items() if e["voie"] == voie]
        nb_ids = sum(len(plan[c]["ids"]) for c in cles_v)
        dire("  %-12s : %4d clé(s), %4d id(s)" % (voie, len(cles_v), nb_ids))

    # ------------------------------------------------------------------
    # LA PREUVE : moteur VIERGE, base modifiée en mémoire, re-banc complet,
    # sorties hachées comparées. Rien ne doit bouger hors du plan.
    # ------------------------------------------------------------------
    dire("")
    t0 = time.time()
    lua2 = charger_banc()
    g2 = lua2.globals()
    for cle, e in plan.items():
        for sid in e["ids"]:
            s = g2.AscensionFR.DB.Sorts[sid]
            if s is None:
                continue
            if e["apres"] is None:
                lua2.execute("AscensionFR.DB.Sorts[%d].D = nil" % sid)
            else:
                s.D = e["apres"]
    verdicts2, hashes_apres, total2 = mesurer(lua2)
    echecs2 = sorted(i for i, (v, _) in verdicts2.items() if v == "anglais")
    dire("banc APRÈS (moteur vierge, base réparée en mémoire) : "
         "%d entrées, %d échecs (%.1f s)"
         % (total2, len(echecs2), time.time() - t0))

    problemes = []
    # 1. tout id réparé doit réussir désormais
    rates = [i for i in ids_repares if verdicts2.get(i, ("?",))[0] != "traduit"]
    if rates:
        problemes.append("réparations sans effet au re-banc : %s" % rates[:10])
    # 2. les purgés disparaissent du banc (plus de D), et personne d'autre
    disparus = sorted(set(verdicts) - set(verdicts2))
    if set(disparus) != set(ids_purges):
        problemes.append("disparus != purgés : %s"
                         % sorted(set(disparus) ^ set(ids_purges))[:10])
    # 3. aucune régression de verdict
    # Une régression, c'est PERDRE un « traduit » — quel que soit le verdict
    # qui le remplace. Ne guetter que « anglais » laisserait passer un
    # traduit -> court_par_nature, qui est tout autant une perte d'affichage.
    regressions = [i for i in verdicts2
                   if verdicts2[i][0] != "traduit"
                   and verdicts.get(i, ("?",))[0] == "traduit"]
    if regressions:
        problemes.append("régressions de verdict : %s" % regressions[:10])
    # 4. AUCUNE sortie changée chez les traduits des deux passes : les
    # réparés étaient en échec avant (pas de sortie avant), donc l'ensemble
    # commun doit être hash pour hash identique.
    changes = [i for i, h in hashes_avant.items()
               if i in hashes_apres and hashes_apres[i] != h]
    if changes:
        problemes.append("sorties changées hors réparations : %s"
                         % sorted(changes)[:10])
    dire("")
    dire("PREUVE PAR LES SORTIES HACHÉES :")
    dire("  échecs %d -> %d ; sorties communes changées : %d ; "
         "régressions : %d ; disparus (purge) : %d"
         % (len(echecs), len(echecs2), len(changes), len(regressions),
            len(disparus)))
    if problemes:
        dire("")
        dire("REFUS D'ÉCRIRE — la preuve n'est pas au vert :")
        for p in problemes:
            dire("  ! %s" % p)

    # ------------------------------------------------------------------
    # Écriture (application seulement) : sauvegarde horodatée d'abord.
    # ------------------------------------------------------------------
    if appliquer and plan and not problemes:
        horodatage = time.strftime("%Y%m%d_%H%M%S")
        sauvegarde = os.path.join(
            RAPPORTS, "sorts_avant_lot14_%s.json" % horodatage)
        os.makedirs(RAPPORTS, exist_ok=True)
        shutil.copy2(CHEMIN_CACHE, sauvegarde)
        for cle, e in plan.items():
            if e["apres"] is None:
                descs.pop(cle, None)
            else:
                descs[cle] = e["apres"]
        with open(CHEMIN_CACHE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=1, sort_keys=True)
        # LES CLÉS PURGÉES SONT INTERDITES DE RÉ-ADOPTION. Mesuré par le
        # contrôleur du lot 14 : 71 des 222 clés purgées ont un défaut que la
        # barrière de STRUCTURE ne voit pas (le français ne traduit pas la
        # clé, mais leurs variables ne divergent pas assez) — et le PackFR
        # les repropose à chaque adoption puisqu'elles ne sont plus dans le
        # cache. La liste vit dans traductions/ (pas rapports/, qui est
        # regénérable) et s'ACCUMULE d'un passage à l'autre.
        chemin_interdites = os.path.join(BASE, "traductions",
                                         "cles_interdites_readoption.json")
        interdites = {}
        if os.path.exists(chemin_interdites):
            with open(chemin_interdites, encoding="utf-8") as f:
                interdites = json.load(f)
        for cle, e in plan.items():
            if e["apres"] is None:
                interdites[cle] = ("purge lot 14 (%s) — le français du "
                                   "PackFR ne traduit pas cette clé"
                                   % e["voie"])
        with open(chemin_interdites, "w", encoding="utf-8") as f:
            json.dump(interdites, f, ensure_ascii=False, indent=1,
                      sort_keys=True)
        dire("clés interdites de ré-adoption : %d (cumul)" % len(interdites))
        dire("")
        dire("ÉCRIT : %d clé(s) réparée(s), %d clé(s) purgée(s) dans %s"
             % (sum(1 for e in plan.values() if e["apres"] is not None),
                sum(1 for e in plan.values() if e["apres"] is None),
                os.path.relpath(CHEMIN_CACHE, BASE)))
        dire("sauvegarde : %s" % os.path.relpath(sauvegarde, BASE))
        dire("(la base DB_Sorts.lua sera mise au niveau par la chaîne"
             " complète — rien n'est régénéré ici)")
    elif appliquer and not plan:
        dire("")
        dire("rien à écrire (plan vide — l'outil a déjà tout posé).")
    elif not appliquer:
        dire("")
        dire("SIMULATION : rien n'a été écrit. Relancer avec --appliquer.")

    dire("")
    dire("ids réparés (%d) : %s%s" % (len(ids_repares), ids_repares[:20],
                                      " …" if len(ids_repares) > 20 else ""))
    dire("ids purgés (%d) : %s%s" % (len(ids_purges), ids_purges[:20],
                                     " …" if len(ids_purges) > 20 else ""))

    # Un rapport PAR PASSAGE : le procès-verbal d'une APPLICATION ne doit pas
    # être écrasé par la simulation suivante (défaut relevé au contrôle du
    # lot 14 — le PV des écritures réelles avait disparu sous un « SIMULATION »).
    os.makedirs(RAPPORTS, exist_ok=True)
    rapport_du_jour = RAPPORT.replace(
        ".txt", "_%s_%s.txt" % (time.strftime("%Y%m%d-%H%M%S"),
                                "application" if appliquer else "simulation"))
    with open(rapport_du_jour, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes_rapport) + "\n")
    print()
    print("rapport -> %s" % rapport_du_jour)
    return 0 if not problemes else 1


if __name__ == "__main__":
    sys.exit(main())
