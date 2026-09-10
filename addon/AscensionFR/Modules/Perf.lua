-- ============================================================================
-- AscensionFR - Instrument de mesure (programme 10, 01/08/2026)
--
-- Trois joueurs signalent des lags : 300 images/s qui tombent à 40-50 chez
-- l'un, des à-coups toutes les ~20 s sous Linux/Proton chez un autre. Ces deux
-- plaintes n'ont PAS la même signature :
--
--   - un coût PAR IMAGE fait baisser la moyenne en permanence ;
--   - un ramassage de miettes périodique fait des POINTES rares et violentes,
--     avec une moyenne presque normale.
--
-- Un instrument qui ne rendrait qu'une moyenne confondrait les deux et nous
-- ferait réparer l'une en croyant traiter l'autre. On rend donc, pour chaque
-- module, la MOYENNE ET LE PIRE TIC.
--
-- ----------------------------------------------------------------------------
-- CE QUE LE CLIENT D'ASCENSION EXPOSE VRAIMENT
--
-- Relevé dans la table des symboles de Ascension.exe, pas supposé :
--   debugprofilestop()      OUI  -> le chronomètre, base de tout ici
--   collectgarbage()        OUI  -> taille du tas et ramassage forcé
--   GetAddOnMemoryUsage()   OUI  -> mémoire par addon
--   GetAddOnCPUUsage()      OUI  -> mais inutile sans scriptProfile
--   GetFunctionCPUUsage()   OUI  -> idem
--   EnumerateFrames()       OUI  -> parcours de tous les cadres
--   la bibliothèque `debug` de Lua  ABSENTE (ni getinfo, ni sethook, ni
--                           getupvalue) : WoW la retire. C'est ce qui décide
--                           de toute l'architecture ci-dessous — impossible de
--                           demander à une fonction de quel fichier elle vient.
--
-- On s'appuie donc UNIQUEMENT sur debugprofilestop(), qui ne dépend d'aucune
-- console et d'aucun réglage. GetAddOnCPUUsage aurait été plus commode, mais
-- il exige `scriptProfile 1`, qui alourdit TOUT le jeu en permanence : mesurer
-- avec lui, c'est mesurer un jeu qui n'est plus celui du joueur.
--
-- ----------------------------------------------------------------------------
-- DEUX PIÈGES, ET CE QU'ON EN FAIT
--
-- 1. LE CHRONOMÈTRE COÛTE. On ne chronomètre donc pas à l'intérieur des
--    boucles : on enrobe le gestionnaire OnUpdate ENTIER, soit deux appels à
--    debugprofilestop() par module et par image, le grain le plus grossier
--    qui donne encore un chiffre par module. Le coût de la mesure est lui-même
--    mesuré (Perf.Etalonner) et affiché dans le relevé : si la mesure pèse
--    plus que quelques pour cent du total, le relevé le dit.
--
-- 2. ÉTEINTE, LA MESURE DOIT ÊTRE ABSENTE — pas testée. Il n'y a donc AUCUN
--    « if mesure_active » dans un chemin chaud. Quand on éteint, on remet le
--    gestionnaire d'origine en place : l'enrobage sort littéralement de la
--    chaîne d'appel, et l'échantillonneur lui-même n'a plus d'OnUpdate. Un
--    joueur qui ne mesure pas ne paie rien du tout, pas même une comparaison.
--
-- ----------------------------------------------------------------------------
-- COMMENT ON SAIT À QUI APPARTIENT UN CADRE
--
-- Sans la bibliothèque `debug`, une fonction ne peut pas dire de quel fichier
-- elle vient. Chaque module déclare donc son cadre lui-même :
--     if AFR.Perf then AFR.Perf.Suivre("BarresDeVie", frame) end
--
-- Sauf Plaques.lua, qu'on n'a pas le droit de modifier aujourd'hui — et c'est
-- justement le suspect n° 1. Pour lui, on procède par ENCADREMENT : un jalon
-- posé à la fin de BarresDeVie.lua ouvre la portée « Plaques », un jalon posé
-- au début de Metiers.lua la referme. Tout cadre à OnUpdate apparu entre les
-- deux vient forcément de Plaques.lua, qui est le seul fichier chargé dans cet
-- intervalle. C'est déterministe, et ça ne touche pas une ligne du fichier.
-- ============================================================================
local AFR = AscensionFR

AFR.Perf = AFR.Perf or {}
local Perf = AFR.Perf

local FENETRE = 10        -- s. Largeur de la fenêtre glissante.
local COULEUR = "|cff0099ffAscensionFR|r"

-- Les modules qu'on suit, dans l'ordre d'affichage. Ceux qui ont un OnUpdate.
local ORDRE = {
    "Plaques", "BarresDeVie", "Epreuves", "Metiers", "Recolte",
    "CanalFrancais",
}

-- ----------------------------------------------------------------------------
-- Les compteurs. Un seau par module, avec un anneau d'une seconde par case :
-- c'est ce qui donne une fenêtre GLISSANTE plutôt qu'un cumul depuis le début,
-- lequel finirait par tout lisser et masquer justement ce qu'on cherche.
--
-- Tout est alloué UNE fois, ici : l'échantillonneur ne doit fabriquer aucune
-- table, sous peine de nourrir le ramasse-miettes qu'il est censé observer.
-- ----------------------------------------------------------------------------
local seaux = {}

local function Seau(nom)
    local s = seaux[nom]
    if s then return s end
    s = { total = 0, pire = 0, tics = 0, case = 1,
          anneau_total = {}, anneau_pire = {}, anneau_tics = {},
          cadres = {}, originaux = {}, enrobes = {} }
    for i = 1, FENETRE do
        s.anneau_total[i] = 0
        s.anneau_pire[i] = 0
        s.anneau_tics[i] = 0
    end
    seaux[nom] = s
    return s
end

for _, nom in ipairs(ORDRE) do Seau(nom) end

-- ----------------------------------------------------------------------------
-- Déclaration des cadres
-- ----------------------------------------------------------------------------
local mesure_active = false
local suivis = {}          -- [cadre] = nom du module
local vus = {}             -- [cadre] = true : cadre déjà attribué (ou écarté)
local jalon_ouvert         -- nom du module dont la portée est ouverte

function Perf.Suivre(nom, cadre)
    if type(nom) ~= "string" or not cadre then return end
    if suivis[cadre] then return end
    suivis[cadre] = nom
    vus[cadre] = true
    local s = Seau(nom)
    s.cadres[#s.cadres + 1] = cadre
end

-- Balaie les cadres à OnUpdate encore inconnus et les attribue à la portée
-- ouverte. Appelé aux jalons (au chargement) et à l'allumage de la mesure ;
-- jamais pendant le jeu.
local function Balayer(nom)
    if type(EnumerateFrames) ~= "function" then return end
    local cadre = EnumerateFrames()
    while cadre do
        if not vus[cadre] then
            vus[cadre] = true
            local ok, script = pcall(cadre.GetScript, cadre, "OnUpdate")
            if ok and script and nom then
                suivis[cadre] = nom
                local s = Seau(nom)
                s.cadres[#s.cadres + 1] = cadre
            end
        end
        cadre = EnumerateFrames(cadre)
    end
end

-- Ouvre une portée. Tout cadre à OnUpdate apparu depuis le jalon précédent
-- est attribué à CELUI-CI, puis la nouvelle portée s'ouvre.
function Perf.Jalon(nom)
    Balayer(jalon_ouvert)
    jalon_ouvert = nom
end

-- ----------------------------------------------------------------------------
-- LES GREFFES (programme 11, 01/08/2026)
--
-- POURQUOI IL LE FALLAIT. L'instrument ne mesurait que six boucles OnUpdate, et
-- la ligne du relevé s'appelait « TOTAL addon ». C'était faux : un addon de
-- traduction est fait d'ACCROCHES — bulles d'aide, dialogues de PNJ, journal de
-- quêtes, menus déroulants, grimoire, métiers, courrier. Un joueur qui promène
-- sa souris sur son sac déclenche des dizaines d'appels qui n'étaient comptés
-- nulle part. Le chiffre était un plancher présenté comme un total.
--
-- LA DIFFICULTÉ, ET CE QU'ON CONCÈDE. Une boucle OnUpdate se démonte : on
-- repose le gestionnaire d'origine et notre enrobage disparaît de la chaîne
-- d'appel. Une greffe posée par `hooksecurefunc`, NON : le jeu ne sait pas la
-- retirer. On ne peut donc pas rendre la mesure littéralement ABSENTE comme
-- pour les boucles.
--
-- Ce qu'on installe à la place est un RELAIS : une fonction minuscule qui
-- appelle `courant(...)`, où `courant` est soit la vraie greffe (mesure
-- éteinte), soit sa version chronométrée (mesure allumée). Éteinte, le prix
-- est UN APPEL DE FONCTION — pas un test, pas une lecture d'horloge, pas une
-- branche. C'est constant et minuscule, mais ce n'est pas zéro, et je préfère
-- l'écrire que le maquiller. Le relevé chiffre ce prix.
--
-- LIMITE À CONNAÎTRE : ce relais n'est fait que pour les greffes dont le jeu
-- IGNORE la valeur de retour — c'est le cas de `hooksecurefunc` et de
-- `HookScript`. Un enrobage de méthode qui doit rendre une valeur (par exemple
-- `UIErrorsFrame.AddMessage`) ne doit PAS passer par ici : préserver un nombre
-- quelconque de valeurs de retour demanderait une table par appel, c'est-à-dire
-- exactement le déchet qu'on traque.
-- ----------------------------------------------------------------------------
local ORDRE_GREFFES = {}    -- noms, dans l'ordre de déclaration
local greffes = {}          -- [nom] = seau

local function SeauGreffe(nom)
    local s = greffes[nom]
    if s then return s end
    s = { total = 0, pire = 0, tics = 0, case = 1,
          anneau_total = {}, anneau_pire = {}, anneau_tics = {},
          relais = {} }
    for i = 1, FENETRE do
        s.anneau_total[i] = 0
        s.anneau_pire[i] = 0
        s.anneau_tics[i] = 0
    end
    greffes[nom] = s
    ORDRE_GREFFES[#ORDRE_GREFFES + 1] = nom
    return s
end

-- PLUSIEURS RELAIS PEUVENT PORTER LE MÊME NOM, et c'est voulu : l'interception
-- des SetText se pose une fois par FAMILLE de composants, mais on veut UN seul
-- chiffre pour l'ensemble. Chaque relais garde donc son propre interrupteur —
-- une première version rangeait l'interrupteur dans le seau, si bien que seul
-- le dernier posé savait basculer et que les autres restaient muets à jamais.
function Perf.Greffe(nom, fn)
    if type(nom) ~= "string" or type(fn) ~= "function" then return fn end
    local s = SeauGreffe(nom)
    local courant = fn
    local mesuree = function(...)
        local t0 = debugprofilestop()
        fn(...)
        local dt = debugprofilestop() - t0
        if dt >= 0 then
            s.total = s.total + dt
            s.tics = s.tics + 1
            if dt > s.pire then s.pire = dt end
        end
    end
    s.relais[#s.relais + 1] = {
        brut = fn,
        mesuree = mesuree,
        poser = function(f) courant = f end,
    }
    -- Une greffe déclarée alors que la mesure tourne déjà (module chargé à la
    -- demande) doit compter tout de suite : sans ceci, elle resterait muette
    -- jusqu'au prochain allumage, et le relevé aurait un trou sans le dire.
    if mesure_active then courant = mesuree end
    return function(...) return courant(...) end
end

-- ----------------------------------------------------------------------------
-- L'enrobage. C'est lui, et lui seul, qui coûte quand la mesure est allumée.
--
-- Deux appels au chronomètre autour du gestionnaire ENTIER — pas un de plus.
-- Un `dt` négatif veut dire que quelqu'un a rappelé debugprofilestart() entre
-- nos deux mesures : le relevé serait faux, on jette l'échantillon plutôt que
-- de le croire.
-- ----------------------------------------------------------------------------
local function Enrober(cadre, nom)
    local s = seaux[nom]
    if not s then return end
    local courant = cadre:GetScript("OnUpdate")
    if not courant then return end
    -- Sans ce test, le second passage enroberait NOTRE PROPRE enrobage, et le
    -- suivant celui-là : une pile qui s'épaissit d'une couche par seconde,
    -- dont chaque couche rechronomètre la précédente. Le relevé enflerait
    -- tout seul, et c'est exactement le genre de mesure qui se mesure
    -- elle-même contre laquelle le programme met en garde.
    if s.enrobes[cadre] == courant then return end
    -- Sinon, c'est le script du module : soit le premier, soit celui qu'il
    -- vient de reposer (CanalFrancais et Recolte le font en cours de partie).
    local origine = courant
    s.originaux[cadre] = origine
    cadre:SetScript("OnUpdate", function(self, ecoule)
        local t0 = debugprofilestop()
        origine(self, ecoule)
        local dt = debugprofilestop() - t0
        if dt >= 0 then
            s.total = s.total + dt
            s.tics = s.tics + 1
            if dt > s.pire then s.pire = dt end
        end
    end)
    s.enrobes[cadre] = cadre:GetScript("OnUpdate")
end

local function Desenrober(s)
    for cadre, origine in pairs(s.originaux) do
        -- On ne remet l'original QUE si notre enrobage est encore en place :
        -- si le module a reposé son propre script entre-temps, le sien fait
        -- foi et l'écraser reviendrait à casser le module pour de bon.
        if cadre:GetScript("OnUpdate") == s.enrobes[cadre] then
            cadre:SetScript("OnUpdate", origine)
        end
        s.originaux[cadre] = nil
        s.enrobes[cadre] = nil
    end
end

-- ----------------------------------------------------------------------------
-- LE COÛT DE LA MESURE ELLE-MÊME
--
-- Le programme le demande explicitement, et à raison : un instrument dont on
-- ignore le prix ne mesure que lui-même. On chronomètre un gros paquet
-- d'appels d'un coup — jamais un appel isolé, qui ne rendrait que la
-- graduation du chronomètre.
-- ----------------------------------------------------------------------------
local cout_appel = 0        -- ms par appel à debugprofilestop()
local resolution = -1       -- ms : le plus petit écart que l'horloge sait rendre

-- ----------------------------------------------------------------------------
-- LA GRADUATION DE L'HORLOGE — à contrôler AVANT de croire un seul chiffre.
--
-- `debugprofilestop` ne lit pas d'horloge fixe : le client choisit à
-- l'exécution entre QueryPerformanceCounter (précis à la microseconde) et
-- GetTickCount (gradué à ~15 ms), selon que QueryPerformanceFrequency a réussi
-- au démarrage. Wine/Proton implémente QueryPerformanceFrequency, donc le repli
-- est improbable — mais « improbable » n'est pas « mesuré », et c'est justement
-- sous Proton qu'on veut mesurer.
--
-- Si l'horloge est graduée à 15 ms, TOUT ce relevé est faux, et faux de façon
-- crédible : les durées apparaîtraient comme des multiples de 15, jamais comme
-- du bruit. On préfère refuser de mesurer que rendre un chiffre plausible et
-- inventé.
--
-- Méthode : on lit l'horloge en boucle jusqu'à ce qu'elle BOUGE. L'écart
-- observé est sa graduation réelle.
-- ----------------------------------------------------------------------------
function Perf.Resolution()
    local t0 = debugprofilestop()
    local t1 = t0
    local tours = 0
    -- Le garde-fou de tours évite la boucle infinie si l'horloge est figée.
    while t1 == t0 and tours < 500000 do
        t1 = debugprofilestop()
        tours = tours + 1
    end
    resolution = (t1 > t0) and (t1 - t0) or -1
    return resolution
end

function Perf.Etalonner()
    local N = 20000
    local t0 = debugprofilestop()
    for _ = 1, N do
        local _ = debugprofilestop()
    end
    local ecoule = debugprofilestop() - t0
    -- La boucle elle-même coûte : on la mesure à vide et on la retranche.
    local t1 = debugprofilestop()
    for _ = 1, N do
        local _ = t1
    end
    local vide = debugprofilestop() - t1
    cout_appel = (ecoule - vide) / N
    if cout_appel < 0 then cout_appel = 0 end
    return cout_appel
end

-- ----------------------------------------------------------------------------
-- LE PRIX PERMANENT DU RELAIS DE GREFFE.
--
-- Contrairement au reste de l'instrument, ce prix-là est payé même la mesure
-- éteinte : le relais ne peut pas être retiré (voir Perf.Greffe). Il vaut un
-- appel de fonction. On le chiffre plutôt que de le supposer négligeable —
-- c'est la même exigence que pour le chronomètre.
-- ----------------------------------------------------------------------------
local cout_relais = 0

function Perf.EtalonnerRelais()
    local N = 20000
    local nue = function(a) return a end
    local courant = nue
    local relais = function(...) return courant(...) end

    local t0 = debugprofilestop()
    for i = 1, N do nue(i) end
    local direct = debugprofilestop() - t0

    local t1 = debugprofilestop()
    for i = 1, N do relais(i) end
    local par_relais = debugprofilestop() - t1

    cout_relais = (par_relais - direct) / N
    if cout_relais < 0 then cout_relais = 0 end
    return cout_relais
end

-- ----------------------------------------------------------------------------
-- LE DÉCOR. « 2 ms par image à Goldshire » ne dit rien : toute la plainte
-- porte sur les scènes chargées. Chaque relevé part donc avec sa scène.
-- ----------------------------------------------------------------------------
local decor = { enfants = 0, affiches = 0, connus = 0, combat = false,
                zone = "", ips = 0, groupe = 0 }

-- Équivalent de la table `connues` de Plaques.lua, tenu ICI parce qu'on n'a
-- pas le droit de lire une variable locale d'un fichier qu'on ne touche pas.
-- Mêmes clés faibles, même source : le compte suit le sien de très près.
local connus_proxy = setmetatable({}, { __mode = "k" })
local connus_n = 0

local function Recenser(...)
    local total = select("#", ...)
    local affiches = 0
    for i = 1, total do
        local c = select(i, ...)
        if c then
            if not connus_proxy[c] then
                connus_proxy[c] = true
                connus_n = connus_n + 1
            end
            local ok, montre = pcall(c.IsShown, c)
            if ok and montre then affiches = affiches + 1 end
        end
    end
    return total, affiches
end

local function ReleverDecor()
    if WorldFrame then
        decor.enfants, decor.affiches = Recenser(WorldFrame:GetChildren())
    end
    decor.connus = connus_n
    decor.combat = (type(InCombatLockdown) == "function"
                    and InCombatLockdown()) or false
    local zone = (type(GetRealZoneText) == "function" and GetRealZoneText())
        or "?"
    local sous = (type(GetSubZoneText) == "function" and GetSubZoneText()) or ""
    decor.zone = (sous ~= "" and sous ~= zone) and (zone .. " / " .. sous)
        or zone
    decor.ips = (type(GetFramerate) == "function" and GetFramerate()) or 0
    -- Le nombre de joueurs ALENTOUR n'est exposé par aucune API en 3.3.5 :
    -- le seul indicateur de densité honnête est le compte d'enfants de
    -- WorldFrame ci-dessus. On ne rend que le groupe, qui, lui, est connu.
    local raid = (type(GetNumRaidMembers) == "function" and GetNumRaidMembers())
        or 0
    local groupe = (type(GetNumPartyMembers) == "function"
                    and GetNumPartyMembers()) or 0
    decor.groupe = (raid > 0) and raid or groupe
end

-- ----------------------------------------------------------------------------
-- L'échantillonneur : une rotation d'anneau par seconde. Éteint, il n'a même
-- pas de script — il ne tourne pas « en ne faisant rien », il ne tourne pas.
-- ----------------------------------------------------------------------------
local horloge = CreateFrame("Frame")
local depuis = 0

local function Tourner(_, ecoule)
    depuis = depuis + ecoule
    if depuis < 1 then return end
    depuis = 0
    for _, nom in ipairs(ORDRE) do
        local s = seaux[nom]
        s.anneau_total[s.case] = s.total
        s.anneau_pire[s.case] = s.pire
        s.anneau_tics[s.case] = s.tics
        s.total, s.pire, s.tics = 0, 0, 0
        s.case = s.case + 1
        if s.case > FENETRE then s.case = 1 end
        -- Un module a pu reposer son OnUpdate depuis la dernière seconde
        -- (CanalFrancais, Recolte le font) : on rattrape ici, une fois par
        -- seconde, jamais dans un chemin chaud.
        for i = 1, #s.cadres do Enrober(s.cadres[i], nom) end
    end
    for _, nom in ipairs(ORDRE_GREFFES) do
        local s = greffes[nom]
        s.anneau_total[s.case] = s.total
        s.anneau_pire[s.case] = s.pire
        s.anneau_tics[s.case] = s.tics
        s.total, s.pire, s.tics = 0, 0, 0
        s.case = s.case + 1
        if s.case > FENETRE then s.case = 1 end
    end
    ReleverDecor()
end

-- ----------------------------------------------------------------------------
-- Allumage / extinction
-- ----------------------------------------------------------------------------
-- ON N'ENROBE QUE CE QUI EST À NOUS.
--
-- La tentation était de rebalayer tous les cadres au moment de l'allumage,
-- pour rattraper ceux qui naissent en cours de partie. C'est un piège : à cet
-- instant le monde est plein de cadres qui ne nous appartiennent pas — les
-- autres addons du joueur, et les fenêtres de Blizzard chargées à la demande.
-- Poser notre script sur l'un d'eux, c'est au mieux mesurer le travail d'autrui
-- sous notre nom, au pire souiller un cadre PROTÉGÉ et faire refuser au jeu les
-- actions du joueur en plein combat — la panne exacte de la 1.6.
--
-- On s'en tient donc aux cadres déclarés par nos modules (Perf.Suivre) et à
-- ceux que l'encadrement a désignés pendant le chargement, quand seuls nos
-- fichiers s'exécutaient. Ce qu'on y perd : les rares cadres éphémères que nos
-- modules créent tard. Ils vivent quelques secondes et ne pèsent rien.
local function RemettreAZero(s)
    for i = 1, FENETRE do
        s.anneau_total[i], s.anneau_pire[i], s.anneau_tics[i] = 0, 0, 0
    end
    s.total, s.pire, s.tics, s.case = 0, 0, 0, 1
end

function Perf.Allumer()
    if mesure_active then return end
    Perf.Resolution()
    Perf.Etalonner()
    Perf.EtalonnerRelais()
    for _, nom in ipairs(ORDRE) do
        local s = seaux[nom]
        RemettreAZero(s)
        for i = 1, #s.cadres do Enrober(s.cadres[i], nom) end
    end
    for _, nom in ipairs(ORDRE_GREFFES) do
        local s = greffes[nom]
        RemettreAZero(s)
        for i = 1, #s.relais do
            s.relais[i].poser(s.relais[i].mesuree)
        end
    end
    depuis = 0
    horloge:SetScript("OnUpdate", Tourner)
    mesure_active = true
end

function Perf.Eteindre()
    if not mesure_active then return end
    horloge:SetScript("OnUpdate", nil)     -- absent, pas testé
    for _, nom in ipairs(ORDRE) do Desenrober(seaux[nom]) end
    for _, nom in ipairs(ORDRE_GREFFES) do
        local s = greffes[nom]
        for i = 1, #s.relais do
            s.relais[i].poser(s.relais[i].brut)
        end
    end
    mesure_active = false
end

function Perf.Actif() return mesure_active end

-- ----------------------------------------------------------------------------
-- Lecture de la fenêtre glissante
-- ----------------------------------------------------------------------------
local function Fenetre(s)
    local total, pire, tics, secondes = 0, 0, 0, 0
    for i = 1, FENETRE do
        total = total + s.anneau_total[i]
        tics = tics + s.anneau_tics[i]
        if s.anneau_pire[i] > pire then pire = s.anneau_pire[i] end
        if s.anneau_tics[i] > 0 then secondes = secondes + 1 end
    end
    if secondes == 0 then return 0, 0, 0, 0 end
    return total / secondes, pire, tics / secondes, total
end

-- ----------------------------------------------------------------------------
-- Le relevé. Fenêtre copiable (jamais une pluie de print dans le chat) :
-- gabarit AFR.AfficherReleve, posé par Epreuves.lua.
-- ----------------------------------------------------------------------------
local function Ligne(...)
    local n = select("#", ...)
    local bouts = {}
    for i = 1, n do bouts[i] = tostring(select(i, ...)) end
    return table.concat(bouts)
end

function Perf.Texte()
    local L = {}
    local function ajouter(s) L[#L + 1] = s end

    ReleverDecor()
    ajouter("AscensionFR — mesure de performance")
    ajouter("=====================================================")
    ajouter("")
    ajouter("LA SCÈNE  (un chiffre sans son décor ne vaut rien)")
    ajouter(Ligne("  zone .................. ", decor.zone))
    ajouter(Ligne("  en combat ............. ", decor.combat and "oui" or "non"))
    ajouter(Ligne("  images par seconde .... ", string.format("%.0f", decor.ips)))
    ajouter(Ligne("  enfants de WorldFrame . ", decor.enfants,
                  "  dont affichés : ", decor.affiches))
    ajouter(Ligne("  cadres connus (≈ la boucle chaude de Plaques) : ",
                  decor.connus))
    ajouter(Ligne("  groupe/raid ........... ", decor.groupe))
    ajouter("")

    if not mesure_active then
        ajouter("La mesure est ÉTEINTE (et donc absente : elle ne coûte rien).")
        ajouter("")
        ajouter("  /afr perf       allume la mesure ; refais-la pour le relevé")
        ajouter("  /afr perf gc    chronomètre un ramassage complet")
        ajouter("  /afr greffes    les accroches répondent-elles encore ?")
        ajouter("  /afr perf raz   remet les compteurs à zéro")
        ajouter("  /afr perf off   éteint")
        return table.concat(L, "\n")
    end

    local duree_image = (decor.ips > 0) and (1000 / decor.ips) or 0
    local somme_ms, somme_pire = 0, 0

    ajouter(Ligne("LES BOUCLES (OnUpdate) — sur les ", FENETRE,
                  " dernières secondes"))
    ajouter("  module            ms par seconde     PIRE tic      tics/s")
    ajouter("  ---------------------------------------------------------")
    local boucles_ms = 0
    for _, nom in ipairs(ORDRE) do
        local s = seaux[nom]
        local moyenne, pire, tics = Fenetre(s)
        if tics > 0 or #s.cadres > 0 then
            boucles_ms = boucles_ms + moyenne
            if pire > somme_pire then somme_pire = pire end
            ajouter(string.format("  %-16s %8.2f ms/s %10.3f ms %9.0f",
                                  nom, moyenne, pire, tics))
        end
    end
    ajouter("  ---------------------------------------------------------")
    ajouter(string.format("  %-16s %8.2f ms/s %10.3f ms",
                          "total des boucles", boucles_ms, somme_pire))
    somme_ms = boucles_ms
    ajouter("")

    -- ---- les greffes -----------------------------------------------------
    local greffes_ms = 0
    if #ORDRE_GREFFES > 0 then
        ajouter("LES GREFFES (accroches sur les fonctions du jeu)")
        ajouter("  accroche          ms par seconde   PIRE appel    appels/s")
        ajouter("  ---------------------------------------------------------")
        local vues = 0
        for _, nom in ipairs(ORDRE_GREFFES) do
            local moyenne, pire, appels = Fenetre(greffes[nom])
            greffes_ms = greffes_ms + moyenne
            if pire > somme_pire then somme_pire = pire end
            if appels > 0 then
                vues = vues + 1
                ajouter(string.format("  %-16s %8.2f ms/s %10.3f ms %9.0f",
                                      nom, moyenne, pire, appels))
            end
        end
        if vues == 0 then
            ajouter("  (aucune n'a tiré : promène la souris sur des objets,")
            ajouter("   ouvre un dialogue de PNJ, un menu déroulant...)")
        end
        ajouter("  ---------------------------------------------------------")
        ajouter(string.format("  %-16s %8.2f ms/s", "total des greffes",
                              greffes_ms))
        somme_ms = somme_ms + greffes_ms
        ajouter("")
    end

    ajouter(string.format("TOTAL MESURÉ ......... %8.2f ms/s", somme_ms))
    ajouter("  ⚠ Ce n'est PAS le total de l'addon : c'est le total de ce qui")
    ajouter("    est instrumenté (les 6 boucles + les greffes déclarées).")
    ajouter("    Ne sont comptés NULLE PART : les gestionnaires d'événements,")
    ajouter("    les filtres de tchat, les greffes non déclarées, et le")
    ajouter("    chargement des bases. C'est un PLANCHER, pas un plafond.")
    ajouter("")
    ajouter(Ligne("  part du temps réel .... ",
                  string.format("%.2f %%", somme_ms / 10)))
    if duree_image > 0 then
        ajouter(Ligne("  soit par image ........ ",
                      string.format("%.3f ms sur %.2f ms",
                                    somme_ms / decor.ips, duree_image)))
        ajouter(Ligne("  le PIRE tic vaut ...... ",
                      string.format("%.1f image(s)", somme_pire / duree_image)))
    end
    ajouter("")

    -- Le prix de l'instrument, comme demandé.
    local appels, appels_greffes = 0, 0
    for _, nom in ipairs(ORDRE) do
        local _, _, tics = Fenetre(seaux[nom])
        appels = appels + tics * 2
    end
    for _, nom in ipairs(ORDRE_GREFFES) do
        local _, _, n = Fenetre(greffes[nom])
        appels = appels + n * 2
        appels_greffes = appels_greffes + n
    end
    local cout_ms = appels * cout_appel
    ajouter("LE COÛT DE LA MESURE ELLE-MÊME")
    ajouter(Ligne("  graduation de l'horloge  ",
                  (resolution > 0) and string.format("%.5f ms", resolution)
                  or "INDÉTERMINÉE"))
    if resolution < 0 then
        ajouter("  ** L'HORLOGE NE BOUGE PAS. Tout ce relevé est à jeter. **")
    elseif resolution > 1 then
        ajouter("  ** HORLOGE TROP GROSSIÈRE. Le client est retombé sur une")
        ajouter("     horloge à gros grain (GetTickCount) : une image dure")
        ajouter("     moins qu'une graduation. Les durées ci-dessus sont des")
        ajouter("     multiples de la graduation, pas des mesures. À JETER —")
        ajouter("     seuls la scène et la mémoire restent lisibles. **")
    end
    ajouter(Ligne("  un appel au chronomètre  ",
                  string.format("%.5f ms", cout_appel)))
    ajouter(Ligne("  appels par seconde ..... ", string.format("%.0f", appels)))
    ajouter(Ligne("  soit .................. ",
                  string.format("%.3f ms/s", cout_ms)))
    if #ORDRE_GREFFES > 0 then
        -- Ce prix-là, contrairement au reste, est payé MÊME MESURE ÉTEINTE :
        -- un relais de greffe ne peut pas être retiré (voir Perf.Greffe).
        ajouter(Ligne("  un relais de greffe .... ",
                      string.format("%.5f ms", cout_relais)))
        ajouter(Ligne("  payé même éteint ....... ",
                      string.format("%.3f ms/s  (%d relais, %.0f appels/s)",
                                    appels_greffes * cout_relais,
                                    #ORDRE_GREFFES, appels_greffes)))
    end
    if somme_ms > 0 then
        local part = 100 * cout_ms / somme_ms
        ajouter(Ligne("  part du total mesuré ... ",
                      string.format("%.1f %%", part)))
        if part > 5 then
            ajouter("  ATTENTION : au-delà de quelques pour cent, le relevé")
            ajouter("  se mesure en partie lui-même. À lire avec cette réserve.")
        end
    end
    ajouter("")

    ajouter("MÉMOIRE")
    local tas = collectgarbage("count")
    ajouter(Ligne("  tas Lua du jeu entier .. ",
                  string.format("%.1f Mo", tas / 1024)))
    if type(UpdateAddOnMemoryUsage) == "function"
        and type(GetAddOnMemoryUsage) == "function" then
        UpdateAddOnMemoryUsage()
        local ok, ko = pcall(GetAddOnMemoryUsage, "AscensionFR")
        if ok and ko then
            ajouter(Ligne("  dont AscensionFR ....... ",
                          string.format("%.1f Mo  (%.0f %%)",
                                        ko / 1024, 100 * ko / tas)))
        end
    end
    ajouter("  (durée d'un ramassage complet : /afr perf gc — ça fait un")
    ajouter("   à-coup volontaire, c'est le but.)")
    return table.concat(L, "\n")
end

-- ----------------------------------------------------------------------------
-- Le chiffre du bloc 3 côté joueur : combien de temps prend un ramassage
-- complet sur SON tas, sur SA machine. C'est le candidat naturel pour l'à-coup
-- périodique du signalement Proton, et c'est la seule mesure qu'on ne peut
-- pas faire à sa place.
-- ----------------------------------------------------------------------------
-- ----------------------------------------------------------------------------
-- POURQUOI CETTE SONDE S'AUTO-DIAGNOSTIQUE (programme 11, 01/08/2026)
--
-- La première version rendait ceci, en jeu, sur un tas de 227 Mo :
--     tas avant 227.5 Mo / tas après 227.5 Mo / libéré 0.0 Mo / DURÉE 0 ms
-- Un ramassage complet ne peut pas durer 0 ms et ne rien libérer. Ce relevé ne
-- disait pas « tout va bien » : il disait que quelque chose n'avait pas marché,
-- et il le disait sous la forme d'un chiffre rond qui ressemblait à un
-- résultat. C'est le piège exact qu'on répare depuis dix jours.
--
-- Trois pièces peuvent être en cause, et on ne peut pas les distinguer en
-- raisonnant. On les met donc chacune à l'épreuve, ici, sur la machine du
-- joueur :
--
--   1. LE CHRONOMÈTRE répond-il ? On chronomètre une boucle de travail connu.
--      Si elle rend zéro, c'est l'horloge qui est en cause, pas le ramassage.
--   2. LE COMPTEUR DE TAS bouge-t-il ? On fabrique exprès quelques mégaoctets
--      de déchet et on regarde s'il monte. S'il ne bouge pas, c'est lui qui
--      ment, et tous les chiffres de mémoire de cet addon sont à revoir.
--   3. LE RAMASSAGE libère-t-il ? On relâche ce déchet, on ramasse, et on
--      regarde s'il redescend. S'il ne redescend pas, `collectgarbage("collect")`
--      est neutralisé dans ce client — et c'est une découverte majeure.
--
-- Si les trois pièces répondent, alors la durée mesurée est vraie, même si
-- elle est petite — et la bonne conclusion est que le jeu tient déjà son tas
-- propre, pas que la mesure a raté.
--
-- Et à la moindre pièce muette, le relevé écrit MESURE INVALIDE en toutes
-- lettres, comme la sonde d'horloge. Jamais un zéro silencieux.
-- ----------------------------------------------------------------------------
local BOUCLE_TEMOIN = 200000      -- itérations d'un travail connu, non nul
local DECHET_CIBLE = 20000        -- petites tables fabriquées exprès

function Perf.Ramassage()
    local L = {}
    local function ajouter(s) L[#L + 1] = s end
    local invalide = nil

    -- ---- la vraie mesure : un ramassage sur le tas TEL QU'IL EST -----------
    local avant = collectgarbage("count")
    local t0 = debugprofilestop()
    collectgarbage("collect")
    local duree = debugprofilestop() - t0
    local apres = collectgarbage("count")

    -- ---- pièce 1 : le chronomètre répond-il ? ------------------------------
    local t1 = debugprofilestop()
    local somme = 0
    for i = 1, BOUCLE_TEMOIN do somme = somme + i end
    local temoin = debugprofilestop() - t1
    if temoin <= 0 then
        invalide = "le chronomètre ne bouge pas (une boucle de "
            .. BOUCLE_TEMOIN .. " tours mesure zéro)"
    end

    -- ---- pièce 2 : le compteur de tas bouge-t-il ? -------------------------
    -- Ramasseur à l'arrêt, sinon il pourrait ramasser notre déchet pendant
    -- qu'on le fabrique et fausser la lecture.
    local socle = collectgarbage("count")
    collectgarbage("stop")
    local poubelle = {}
    for i = 1, DECHET_CIBLE do poubelle[i] = { i, i, i } end
    local haut = collectgarbage("count")
    poubelle = nil
    collectgarbage("restart")
    local monte = haut - socle
    if not invalide and monte < 100 then
        invalide = "le compteur de tas ne monte pas quand on alloue "
            .. "(collectgarbage(\"count\") ne reflète pas la mémoire)"
    end

    -- ---- pièce 3 : le ramassage libère-t-il ? ------------------------------
    local t2 = debugprofilestop()
    collectgarbage("collect")
    local duree2 = debugprofilestop() - t2
    local bas = collectgarbage("count")
    local rendu = haut - bas
    if not invalide and rendu < monte / 2 then
        invalide = "le ramassage ne rend pas la mémoire qu'on vient "
            .. "d'allouer (collectgarbage(\"collect\") semble neutralisé)"
    end

    -- ---- les réglages du ramasseur, LUS et non supposés -------------------
    -- Relevé dans le binaire du client (programme 11) : Ascension pose
    -- lua_gc(GCSETPAUSE, 110) au démarrage — au lieu des 200 de Lua d'origine —
    -- et appelle lua_gc(GCSTEP, 1) à CHAQUE tour de sa boucle principale. Le
    -- jeu ramasse donc en permanence, tout seul, image après image. C'est ce
    -- qui explique qu'un « collect » demandé à la main ne rende presque rien.
    --
    -- On le VÉRIFIE ici plutôt que de le croire : « setpause » rend l'ANCIENNE
    -- valeur, ce qui permet de la lire en la reposant aussitôt.
    local pause = collectgarbage("setpause", 100)
    collectgarbage("setpause", pause)
    local pas = collectgarbage("setstepmul", 100)
    collectgarbage("setstepmul", pas)

    local ips = (type(GetFramerate) == "function" and GetFramerate()) or 0

    ajouter("AscensionFR — durée d'un ramassage complet")
    ajouter("==============================================")
    ajouter("")
    ajouter("LA MESURE")
    ajouter(Ligne("  tas avant .............. ",
                  string.format("%.1f Mo  (%.0f Ko)", avant / 1024, avant)))
    ajouter(Ligne("  tas après .............. ",
                  string.format("%.1f Mo  (%.0f Ko)", apres / 1024, apres)))
    ajouter(Ligne("  libéré ................. ",
                  string.format("%.3f Mo  (%.0f Ko)",
                                (avant - apres) / 1024, avant - apres)))
    ajouter(Ligne("  DURÉE .................. ",
                  string.format("%.3f ms", duree)))
    if ips > 0 then
        ajouter(Ligne("  soit ................... ",
                      string.format("%.2f image(s) à %.0f IPS",
                                    duree * ips / 1000, ips)))
    end
    ajouter("")

    ajouter("L'INSTRUMENT S'EST MIS À L'ÉPREUVE")
    ajouter(Ligne("  1. chronomètre : ", BOUCLE_TEMOIN,
                  " tours mesurés à ", string.format("%.3f ms", temoin),
                  temoin > 0 and "  -> répond" or "  -> MUET"))
    ajouter(Ligne("  2. compteur de tas : ", DECHET_CIBLE,
                  " tables font monter le tas de ",
                  string.format("%.0f Ko", monte),
                  monte >= 100 and "  -> répond" or "  -> MUET"))
    ajouter(Ligne("  3. ramassage : rend ", string.format("%.0f Ko", rendu),
                  " sur ", string.format("%.0f Ko", monte),
                  " en ", string.format("%.3f ms", duree2),
                  (rendu >= monte / 2) and "  -> libère" or "  -> NE LIBÈRE PAS"))
    ajouter("")

    ajouter("LES RÉGLAGES DU RAMASSEUR DU CLIENT")
    ajouter(Ligne("  pause .................. ", pause,
                  " %   (Lua d'origine : 200)"))
    ajouter(Ligne("  multiplicateur de pas .. ", pas, " %"))
    if pause > 0 and pause < 150 then
        ajouter("  -> réglage SERRÉ : le ramasseur relance un cycle dès que le")
        ajouter("     tas dépasse de peu son estimation. Ajouté au pas que le")
        ajouter("     client déclenche à chaque image, le tas est tenu propre")
        ajouter("     en permanence — d'où le peu de mémoire rendue ci-dessus.")
        ajouter("     Contrepartie : ce travail est payé à CHAQUE IMAGE, et il")
        ajouter("     grandit avec la taille du tas.")
    end
    ajouter("")

    if invalide then
        ajouter("  ** MESURE INVALIDE **")
        ajouter("  " .. invalide)
        ajouter("  Ne tire AUCUNE conclusion des chiffres ci-dessus.")
    elseif duree < 1 then
        ajouter("  Les trois pièces répondent : la durée est VRAIE, et elle "
                .. "est petite.")
        ajouter("  Cela ne veut pas dire que la mesure a raté — cela veut dire")
        ajouter("  que le jeu tenait déjà son tas propre au moment du relevé.")
        ajouter("  Refais la mesure après un long moment de jeu chargé, ou")
        ajouter("  juste après avoir ouvert beaucoup de fenêtres.")
    else
        ajouter("  Les trois pièces répondent : la durée est bonne.")
        ajouter("  Un ramassage complet ne se produit pas à chaque seconde :")
        ajouter("  c'est un à-coup rare. S'il dure plus que quelques images,")
        ajouter("  c'est lui qu'on sent, et pas un coût par image.")
    end
    return table.concat(L, "\n")
end

-- ============================================================================
-- LES GREFFES RÉPONDENT-ELLES ENCORE ? (programme 12, 01/08/2026)
--
-- POURQUOI. Ascension a poussé le patch Saison 10 le 01/08. L'addon se charge et
-- « a l'air de marcher » — ça ne prouve rien. Une greffe posée sur une fonction
-- que le client a renommée ou retirée ne fait pas planter le jeu : gardée, elle
-- ne se pose simplement pas, et la fenêtre concernée reste en anglais, en
-- silence. On ne s'en aperçoit que le jour où un joueur l'ouvre.
--
-- Cette sonde interroge le VRAI `_G` du client en cours. C'est le seul juge de
-- paix : lire les fichiers d'interface hors du jeu ne dit pas ce que le moteur
-- expose, ni ce qu'un addon d'Ascension ajoute au chargement.
--
-- ⚠️ CETTE LISTE DOIT SUIVRE LE CODE. Un `hooksecurefunc` ajouté sans être
-- inscrit ici ne serait jamais vérifié — et la sonde dirait « tout va bien » en
-- regardant à côté. C'est `outils/verifier_greffes.py` qui tient la promesse :
-- il compare cette liste aux greffes réellement présentes dans les modules et
-- passe au ROUGE si elles divergent. Ne pas modifier l'une sans l'autre.
-- ============================================================================
local GREFFES = {
    "ChatEdit_UpdateHeader",
    "ClassTrainerFrame_Update",
    "ClassTrainer_SetSelection",
    "SpellButton_UpdateButton",
    "UIDropDownMenu_AddButton",
    "GossipFrameUpdate",
    "InboxFrame_Update",
    "OpenMail_Update",
    "ReputationFrame_Update",
    "TokenFrame_Update",
    "CalendarFrame_Update",
    "StaticPopup_OnUpdate",
    "KeyBindingFrame_Update",
    "StaticPopup_Show",
    "TradeSkillFrame_Update",
    "SpellBookFrame_Update",
    "SpellBookFrame_UpdateSpells",
    "TaxiNodeOnButtonEnter",
    "QuestInfo_Display",
    "QuestLog_Update",
    "WatchFrame_Update",
    "WatchFrameItem_OnEnter",
    "MerchantFrame_UpdateMerchantInfo",
    "MerchantFrame_UpdateBuybackInfo",
    "LootFrame_Update",
}

-- Certaines fonctions n'existent QUE lorsque leur fenêtre a été ouverte une
-- fois : les addons de Blizzard se chargent à la demande. Les signaler comme
-- absentes alors que le joueur n'a jamais ouvert son calendrier serait un faux
-- rouge — et un faux rouge qu'on apprend à ignorer, c'est un banc perdu.
local A_LA_DEMANDE = {
    ClassTrainerFrame_Update = "Blizzard_TrainerUI",
    ClassTrainer_SetSelection = "Blizzard_TrainerUI",
    TradeSkillFrame_Update = "Blizzard_TradeSkillUI",
    TokenFrame_Update = "Blizzard_TokenUI",
    CalendarFrame_Update = "Blizzard_Calendar",
    KeyBindingFrame_Update = "Blizzard_BindingUI",
}

function Perf.Greffes()
    local L = {}
    local function ajouter(s) L[#L + 1] = s end
    ajouter("AscensionFR — les greffes répondent-elles ?")
    ajouter("=============================================")
    ajouter("")
    local absentes, en_attente = {}, {}
    for i = 1, #GREFFES do
        local nom = GREFFES[i]
        if type(_G[nom]) ~= "function" then
            local addon = A_LA_DEMANDE[nom]
            if addon and not (IsAddOnLoaded and IsAddOnLoaded(addon)) then
                en_attente[#en_attente + 1] = nom .. "  (" .. addon
                    .. " pas encore chargé)"
            else
                absentes[#absentes + 1] = nom
            end
        end
    end
    ajouter(Ligne("  vérifiées .............. ", #GREFFES))
    ajouter(Ligne("  ABSENTES ............... ", #absentes))
    ajouter(Ligne("  indécidables pour l'instant  ", #en_attente))
    ajouter("")
    if #absentes > 0 then
        ajouter("CES FONCTIONS N'EXISTENT PLUS — la traduction correspondante")
        ajouter("ne se pose pas :")
        for i = 1, #absentes do ajouter("  * " .. absentes[i]) end
        ajouter("")
    end
    if #en_attente > 0 then
        ajouter("PAS ENCORE JUGEABLES. Ces fenêtres se chargent à la demande :")
        ajouter("ouvre-les une fois, puis refais la commande.")
        for i = 1, #en_attente do ajouter("  - " .. en_attente[i]) end
        ajouter("")
    end
    if #absentes == 0 and #en_attente == 0 then
        ajouter("  Toutes répondent. Aucune greffe n'est tombée.")
    end
    ajouter(Ligne("  version d'interface déclarée : ",
                  (GetAddOnMetadata
                   and GetAddOnMetadata("AscensionFR", "Interface")) or "?"))
    return table.concat(L, "\n")
end

-- ----------------------------------------------------------------------------
-- Aiguillage de « /afr perf … ». La commande /afr elle-même vit dans
-- Recolte.lua ; elle nous passe la main.
-- ----------------------------------------------------------------------------
function Perf.Commande(argument)
    argument = strtrim(string.lower(argument or ""))
    if argument == "off" or argument == "stop" then
        Perf.Eteindre()
        print(COULEUR .. " : mesure éteinte.")
        return
    end
    if argument == "greffes" or argument == "accroches" then
        local texte = Perf.Greffes()
        if AFR.AfficherReleve then AFR.AfficherReleve(texte)
        else print(texte) end
        return
    end
    if argument == "gc" or argument == "ramassage" then
        local texte = Perf.Ramassage()
        if AFR.AfficherReleve then AFR.AfficherReleve(texte)
        else print(texte) end
        return
    end
    if argument == "raz" then
        Perf.Eteindre()
        Perf.Allumer()
        print(COULEUR .. " : compteurs remis à zéro.")
        return
    end
    if not mesure_active then
        Perf.Allumer()
        print(COULEUR .. " : mesure allumée. Va jouer une minute dans une "
              .. "scène chargée, puis refais /afr perf.")
        return
    end
    local texte = Perf.Texte()
    if AFR.AfficherReleve then AFR.AfficherReleve(texte)
    else print(texte) end
end
