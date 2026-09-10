-- Fenêtre des Épreuves d'Ascension (« Trials ») en français.
--
-- DEUX SOURCES DE TEXTE, DEUX BASES
-- --------------------------------
--   * le CONTENU (noms et descriptions des 297 épreuves) vient de
--     Challenge.dbc -> AFR.DB.Epreuves, indexé par le texte anglais ;
--   * les LIBELLÉS de la fenêtre (About, Activate, Leaderboard…) sont des
--     GlobalStrings -> AFR.DB.UI, indexé par le NOM de la globale. Il faut
--     donc un index inverse pour les retrouver depuis leur texte anglais.
--
-- AUCUNE GLOBALE N'EST ÉCRITE. On s'accroche aux mixins de la fenêtre avec
-- hooksecurefunc : notre code passe APRÈS le leur et repose simplement le
-- texte. Si Ascension change sa fenêtre, l'accroche ne trouve rien et
-- l'anglais revient — dégradation propre, jamais de casse.

local AFR = AscensionFR

-- Chronomètre cette greffe si l'instrument de mesure est chargé (/afr perf).
-- Sans lui, la fonction passe telle quelle : aucun surcoût, aucune dépendance.
local function MESURER(nom, fn)
    if AFR.Perf and AFR.Perf.Greffe then return AFR.Perf.Greffe(nom, fn) end
    return fn
end


-- Déclaré tout en haut : `Balayer` est APPELÉ dans Brancher() bien avant
-- d'être défini plus bas. Sans cette réservation, l'appel visait une variable
-- globale inexistante et le balayage ne tournait jamais — en silence, car il
-- est enveloppé dans un pcall.
local Balayer

-- Même raison pour ces deux-là : Brancher les lit aussi. Déclarés plus bas,
-- Brancher lisait la GLOBALE `remplaces` (nil) et « remplaces - avant »
-- levait une erreur — avalée par pcall, donc le branchement échouait pour
-- toujours et le rebalayage ne tournait JAMAIS. Trouvé par l'audit
-- adversarial du 20/07/2026, invisible autrement.
local remplaces = 0        -- diagnostic : combien de textes changés
-- Fenêtres À REBALAYER au prochain tick de la veilleuse (2.0.1 : on ne
-- balaie plus JAMAIS UIParent entier — chaque texte traduit re-déclenchait
-- un parcours de TOUTE l'interface, une fois par seconde en jeu actif :
-- c'étaient les mini-blocages du jour de sortie, chez <joueur> comme chez
-- Dan). Clé = le cadre RACINE concerné, valeur = true (dédoublonne).
local a_balayer = {}
local a_balayer_nb = 0

-- La racine d'une zone de texte : la fenêtre de premier niveau qui la
-- contient. C'est ELLE qu'on rebalaie — elle est ouverte et vivante.
local function RacineDe(zone)
    local cadre = zone
    for _ = 1, 12 do
        if type(cadre) ~= "table" or type(cadre.GetParent) ~= "function" then
            return nil
        end
        local parent = cadre:GetParent()
        if not parent or parent == UIParent or parent == WorldFrame then
            return cadre ~= zone and cadre or nil
        end
        cadre = parent
    end
    return nil
end

local function DemanderBalayage(cadre)
    if cadre and not a_balayer[cadre] and a_balayer_nb < 8 then
        a_balayer[cadre] = true
        a_balayer_nb = a_balayer_nb + 1
    end
end

local function Actif()
    return not (AFR.Actif and not AFR.Actif())
end

-- Interrupteur d'enquête, sans /reload :
--   /run AscensionFRSaved.Options.sansInterception = true    (couper)
--   /run AscensionFRSaved.Options.sansInterception = nil     (rétablir)
-- Neutralise TOUTE l'interception d'affichage (Épreuves, hauts faits,
-- bulles, balayage). Sert à départager « c'est notre addon » de « c'est le
-- jeu » quand une fenêtre se comporte bizarrement.
local function Coupee()
    local options = AscensionFRSaved and AscensionFRSaved.Options
    return options and options.sansInterception
end

-- Index inverse des GlobalStrings, construit à la PREMIÈRE ouverture de la
-- fenêtre seulement : inutile de le payer pour les joueurs qui n'y vont pas.
local libelles
local function Libelle(texte)
    if not libelles then
        libelles = {}
        for cle, francais in pairs(AFR.DB.UI or {}) do
            local anglais = _G[cle]
            if type(anglais) == "string" and anglais ~= ""
                and type(francais) == "string" and francais ~= ""
                and anglais ~= francais then
                libelles[anglais] = francais
            end
        end
    end
    return libelles[texte]
end

local function Francais(texte)
    if type(texte) ~= "string" or texte == "" then return nil end
    local t = AFR.DB.Epreuves and AFR.DB.Epreuves[texte]
    if type(t) == "string" and t ~= "" then return t end
    -- PONT DES NOMS DE SORTS (21/07) : le grimoire et les fenêtres balayées
    -- passent par CE chemin-ci, pas par FrancaisLigne — les deux doivent
    -- connaître le pont (« Passif » se traduisait, « Dodge » non : c'était
    -- exactement cette ligne qui manquait).
    local noms = AFR.DB.SortsNoms
    local n = noms and noms[texte]
    if type(n) == "string" and n ~= "" then return n end
    -- PONT DES NOMS D'OBJETS (22/07) : la collection Vanity, la garde-robe
    -- et la forge affichent des noms d'objets par leur TEXTE seul.
    local objets = AFR.DB.ObjetsNoms
    local o = objets and objets[texte]
    if type(o) == "string" and o ~= "" then return o end
    -- « Rank 1 » sous les noms du grimoire.
    local rang = string.match(texte, "^Rank (%d+)$")
    if rang then return "Rang " .. rang end
    -- Descriptions de sorts à nombres calculés (cartes CoA) — en dernier :
    -- l'index flou ne sert que si rien d'exact n'a répondu.
    return Libelle(texte)
        or (AFR.DescriptionSort and AFR.DescriptionSort(texte))
end

-- Déclaré en avance : la fonction vit plus bas (elle a besoin du contexte de
-- l'interception) mais DEUX chemins d'écriture doivent la consulter.
local EstFiltreHdV

-- Repose le texte en français sur la zone visée. On compare avant d'écrire :
-- réécrire la même chaîne à chaque rafraîchissement ferait clignoter le cadre.
local function Poser(zone, texte)
    if not Actif() or type(zone) ~= "table" then return end
    if EstFiltreHdV and EstFiltreHdV(zone) then return end
    local fr = Francais(texte)
    if fr and zone.GetText and zone:GetText() ~= fr then
        zone:SetText(fr)
    end
end

-- LE VRAI POINT D'ACCROCHE : l'API qui FOURNIT les données.
--
-- Accrocher les mixins ne marche pas : `Mixin(cadre, …)` COPIE les fonctions
-- dans chaque cadre à sa construction, qui a lieu avant qu'on puisse
-- intervenir. Modifier la table du mixin après coup ne touche donc aucun
-- cadre existant (constaté en jeu le 20/07/2026 : rien n'était traduit alors
-- que tout compilait).
--
-- On enveloppe donc `C_Challenge`, en amont de tout affichage. Chaque texte
-- rendu passe par notre dictionnaire ; tout le reste — nombres, booléens,
-- tables — ressort intact. Si un texte est inconnu, l'anglais passe tel quel.
-- Les fonctions sont nommées EXPLICITEMENT, pas énumérées par pairs().
-- Première tentative en jeu : pairs(C_Challenge) n'a rien rendu, donc rien
-- n'a été enveloppé alors que la table existait bien — signe que ses
-- fonctions vivent derrière une métatable, invisibles à l'énumération.
-- La liste vient des appels réellement présents dans le client.
local API = {
    C_Challenge = {
        "GetChallengeInfo", "GetChallengeInfoByLevel", "GetChallengeAtIndex",
        "GetChallengesWithGroupID", "GetPendingChallenges",
        -- Les onglets Restrictions / Prérequis passent par celles-ci.
        "GetModifierLocalization", "GetConditionLocalization",
        "GetRuleLocalization", "GetRequirementLocalization",
    },
    C_TrialCreator = {
        "GetTrialInfo", "GetTrialAtIndex", "GetActiveTrial",
    },
}

local function Traduire(...)
    -- select("#", …) et unpack(1, n), PAS table.getn : un nil au MILIEU des
    -- retours de l'API tronquerait tout ce qui suit — la fenêtre des
    -- Épreuves perdrait des données sans erreur (audit du 20/07/2026).
    local n = select("#", ...)
    local retours = {...}
    for i = 1, n do
        if type(retours[i]) == "string" then
            local ok, fr = pcall(Francais, retours[i])
            if ok and fr then retours[i] = fr end
        end
    end
    return unpack(retours, 1, n)
end

-- Marque les fonctions déjà traitées. Sans ce garde-fou, une seconde passe
-- enveloppe l'enveloppe : les couches s'empilent et le jeu ralentit à chaque
-- appel (vécu le 20/07/2026 — la surveillance ne s'arrêtait pas et
-- réenveloppait une fois par seconde).
local posees = {}

local function EnvelopperAPI()
    local n = 0
    for espace, fonctions in pairs(API) do
        local table_api = _G[espace]
        if type(table_api) == "table" then
            for _, nom in ipairs(fonctions) do
                local ancienne = table_api[nom]
                if type(ancienne) == "function" and not posees[ancienne] then
                    local nouvelle = function(...)
                        return Traduire(ancienne(...))
                    end
                    posees[ancienne] = true
                    posees[nouvelle] = true
                    table_api[nom] = nouvelle
                    n = n + 1
                end
            end
        end
    end
    if n > 0 and AFR.Debug then
        AFR.Debug("Épreuves :", n, "fonctions enveloppées")
    end
    return n > 0
end

-- Rend VRAI si l'enveloppe est posée : c'est ce que la veilleuse attend pour
-- s'arrêter. Sans cette valeur de retour, elle tournait indéfiniment.
local mixins_poses = false

local function Brancher()
    local pose = EnvelopperAPI()

    -- Les accroches de mixin ne se posent QU'UNE FOIS : hooksecurefunc empile
    -- sans jamais remplacer, donc une seconde passe doublerait le travail à
    -- chaque appel.
    if mixins_poses then return pose end
    mixins_poses = true

    -- Filet de sécurité : si un cadre est construit APRÈS nous, il prendra la
    -- version accrochée du mixin. Sans effet sur les cadres déjà bâtis — d'où
    -- l'enveloppe de l'API ci-dessus, qui est le vrai mécanisme.
    if type(ChallengeItemMixin) == "table"
        and type(ChallengeItemMixin.SetName) == "function" then
        hooksecurefunc(ChallengeItemMixin, "SetName", function(self, nom)
            Poser(self and self.Text, nom)
        end)
    end

    -- Le panneau de détail : titre, sous-titre, description.
    local M = ChallengeExtendedInfoMixin
    if type(M) ~= "table" then return pose end
    if type(M.SetTitle) == "function" then
        hooksecurefunc(M, "SetTitle", function(self, texte)
            Poser(self and self.Title, texte)
        end)
    end
    if type(M.SetSubText) == "function" then
        hooksecurefunc(M, "SetSubText", function(self, texte)
            Poser(self and self.SubText, texte)
        end)
    end
    if type(M.ShowAboutTab) == "function" then
        hooksecurefunc(M, "ShowAboutTab", function(self, propos)
            Poser(self and self.Description, propos)
        end)
    end

    -- Rattrape ce qui était déjà à l'écran avant notre arrivée.
    local avant = remplaces
    pcall(Balayer, UIParent, 1)
    if AFR.Debug then
        AFR.Debug("Épreuves : balayage,", remplaces - avant, "textes rattrapés")
    end
    return pose
end

-- ==========================================================================
-- L'INTERCEPTION À L'AFFICHAGE — le mécanisme qui marche
-- ==========================================================================
-- Après trois échecs (mixins copiés, pairs() aveugle, API arrivant trop tard
-- et surtout non empruntée par l'affichage), on cesse de chercher D'OÙ vient
-- le texte : on le prend AU MOMENT où il est posé à l'écran.
--
-- Toutes les zones de texte du jeu partagent une même table de méthodes. En
-- s'y accrochant une seule fois, on voit passer chaque texte affiché, quel
-- que soit le chemin qu'il a emprunté.
--
-- CE QUI REND LA CHOSE SÛRE :
--   * on ne consulte QUE le dictionnaire des Épreuves (471 entrées) — un
--     texte inconnu ressort intact, donc aucun risque de traduire par erreur
--     un texte d'un autre addon ;
--   * une seule recherche dans une table par changement de texte : le coût
--     est négligeable ;
--   * un verrou empêche notre propre écriture de nous rappeler en boucle ;
--   * aucune globale n'est écrite.
-- Les LIBELLÉS du cadre (About, Activate, Leaderboard…) sont des
-- GlobalStrings, déjà traduites dans DB.UI. On les nomme UNE PAR UNE plutôt
-- que d'ouvrir le dictionnaire entier : c'est ce qui garantit qu'aucun texte
-- d'un autre addon ne sera traduit par accident.
local CHROME = {
    "CHALLENGES_ABOUT", "CHALLENGES_EDITOR_LABEL_ABOUT",
    "CHALLENGES_LEADERBOARD", "CHALLENGES_AURAS",
    "CHALLENGES_RESTRICTIONS", "CHALLENGES_EDITOR_LABEL_RESTRICTIONS",
    "CHALLENGES_REQUIREMENTS",
    "CHALLENGES_EDITOR_LABEL_ACTIVATION_REQUIREMENTS",
    "CURRENT_LEVEL_COLON", "ACTIVATE", "DEACTIVATE",
    "CHALLENGES", "CHALLENGES_STORE", "CUSTOM_TRIALS", "TRIAL_BUILDER",
    "GAMEMODES", "TRIALS", "PATH_TO_ASCENSION",
    -- Révélation Wildcard (lot 14, 28/07) : le sous-texte sous le nom
    -- de la carte (« Talent Unlocked! »…). Ces globales sont dans
    -- DB_LuesClient, donc JAMAIS écrites — CHROME est le canal
    -- d'affichage-seul prévu pour ça (vérifié sous attaque taint).
    "WILDCARD_TALENT_UNLOCKED", "WILDCARD_ABILITY_UNLOCKED",
    "WILDCARD_DESIRED_TALENT_UNLOCKED",
    "WILDCARD_DESIRED_ABILITY_UNLOCKED",
    -- bulle de performance du menu de jeu (paragraphes explicatifs)
    "NEWBIE_TOOLTIP_LATENCY", "NEWBIE_TOOLTIP_FRAMERATE",
    "NEWBIE_TOOLTIP_MEMORY",
}

-- Construit à la première interception : { anglais du client -> français }.
local chrome
local function Chrome(texte)
    if not chrome then
        chrome = {}
        for _, cle in ipairs(CHROME) do
            local anglais, francais = _G[cle], AFR.DB.UI and AFR.DB.UI[cle]
            if type(anglais) == "string" and anglais ~= ""
                and type(francais) == "string" and francais ~= ""
                and anglais ~= francais then
                chrome[anglais] = francais
            end
        end
    end
    return chrome[texte]
end

-- Un libellé peut être affiché SUIVI de sa valeur : « Current Level: 1 ».
-- L'égalité exacte échoue alors, alors que le libellé est bien connu. On
-- réessaie sur le DÉBUT du texte, mais seulement pour les libellés qui se
-- terminent par « : » — un préfixe aussi caractéristique ne peut pas se
-- confondre avec une phrase ordinaire.
local prefixes
local function Prefixe(texte)
    if not prefixes then
        prefixes = {}
        for anglais, francais in pairs(AFR.DB.Epreuves or {}) do
            if string.sub(anglais, -1) == ":" then
                table.insert(prefixes, {en = anglais, fr = francais,
                                        n = string.len(anglais)})
            end
        end
    end
    for _, p in ipairs(prefixes) do
        if string.sub(texte, 1, p.n) == p.en then
            return p.fr .. string.sub(texte, p.n + 1)
        end
    end
end

-- Correspondance TOLÉRANTE aux fins de ligne — le dernier recours.
--
-- Le fichier de données contient « \r\n » ; ce que la fenêtre affiche n'est
-- pas toujours identique octet pour octet (le client réécrit parfois les
-- sauts de ligne). Résultat observé : une description d'UN paragraphe
-- passait, la même à TROIS paragraphes échouait — seule différence, les
-- sauts de ligne. On indexe donc aussi chaque texte sous une forme
-- normalisée (sauts unifiés, bords rognés) et on cherche l'arrivée sous la
-- même forme. Le français est posé avec des \n simples, ce que les zones de
-- texte affichent proprement.
local normalise

-- Nettoyage LÉGER, pour les VALEURS françaises : fins de ligne unifiées,
-- bords rognés — rien qui abîme le texte affiché.
local function Normaliser(texte)
    texte = string.gsub(texte, "\r\n", "\n")
    texte = string.gsub(texte, "\r", "\n")
    texte = string.gsub(texte, "^%s+", "")
    texte = string.gsub(texte, "%s+$", "")
    return texte
end

-- Nettoyage FORT, pour les CLÉS de comparaison seulement. Le client
-- transforme les MOTS-CLÉS à la volée avant affichage : « experience » du
-- fichier de données devient « |Hkeyword:…|hExperience|h » coloré à l'écran
-- (système du Keyword Appendix — élucidé le 20/07/2026 sur les pages de la
-- Voie : celles SANS mot-clé passaient, les autres jamais). On compare donc
-- sans les habillages de lien/couleur et sans la casse. Jamais appliqué aux
-- valeurs : le joueur verrait du texte en minuscules.
local function NormaliserCle(texte)
    texte = Normaliser(texte)
    texte = string.gsub(texte, "|H[^|]*|h", "")          -- ouverture de lien
    texte = string.gsub(texte, "|h", "")                 -- fermeture de lien
    texte = string.gsub(texte, "|c%x%x%x%x%x%x%x%x", "") -- couleur
    texte = string.gsub(texte, "|r", "")
    return string.lower(texte)
end

local function Normalisee(texte)
    if not normalise then
        normalise = {}
        for _, table_db in ipairs({AFR.DB.Epreuves, AFR.DB.HautsFaits}) do
            for anglais, francais in pairs(table_db or {}) do
                normalise[NormaliserCle(anglais)] = Normaliser(francais)
            end
        end
    end
    return normalise[NormaliserCle(texte)]
end

-- 35 000 entrées normalisées d'un coup à la PREMIÈRE info-bulle : un
-- mini-blocage en pleine partie. Préchauffé pendant l'écran de chargement
-- (Core, 2.0.2).
if AFR.Prechauffages then
    table.insert(AFR.Prechauffages,
                 function() Normalisee("préchauffage") end)
end

-- Textes COMPOSÉS : un libellé connu suivi d'un compteur — « Getting
-- Started 20 / 21 » (barre de la Voie), « Page 1 of 4 ». Le libellé se
-- traduit, le compte se garde tel quel.
local function Composee(texte)
    local corps, compte = string.match(texte, "^(.-)%s+(%d+%s*/%s*%d+)$")
    if corps and corps ~= "" then
        local base = AFR.DB.Epreuves
        local fr = (base and base[corps]) or Normalisee(corps)
        if fr then return fr .. " " .. compte end
    end
    local page, total = string.match(texte, "^Page (%d+) of (%d+)$")
    if page then return "Page " .. page .. " sur " .. total end
    -- « Rank 0/1 » des cartes de talents (capture de Dan, 24/07) : la
    -- carte passe par l'INTERCEPTEUR, pas par l'info-bulle des sorts —
    -- le motif se traite donc ici, avec ses cousins à compteur.
    -- TOLÉRANT aux espaces et à un habillage couleur (2e capture : le
    -- motif strict laissait passer la ligne).
    local avant, a, b, apres = string.match(
        texte, "^(.-)Rank%s*(%d+)%s*/%s*(%d+)%s*(.-)$")
    if a and string.gsub(avant, "|c%x%x%x%x%x%x%x%x", "") == ""
        and string.gsub(apres, "|r", "") == "" then
        return avant .. "Rang " .. a .. "/" .. b .. apres
    end
    -- « Pure Shadow (Rank 1) » (capture de Dan, 28/07) : le libellé sous
    -- la carte de la révélation Wildcard est COMPOSÉ par le client
    -- (WildCardNameFrameButtonMixin : nom .. " (" .. RANK .. " " .. rang
    -- .. ")" pour les talents) — la clé exacte ne peut donc jamais
    -- mordre. Motif borné à la fin de texte ; le nom passe par le pont
    -- des noms de sorts (clé exacte, jamais pairs()). Nom inconnu du
    -- pont : il reste anglais mais le rang se francise — même précédent
    -- que « Rank n » seul sous les noms du grimoire. Les objets
    -- « X (Rank n) » sont hors de portée ICI : Intercepter consulte
    -- DB.ObjetsNoms AVANT Composee (vérifié au moteur, 28/07).
    local nomSort, rangSort = string.match(texte,
                                           "^(.-)%s+%(Rank%s+(%d+)%)$")
    if nomSort and nomSort ~= "" then
        local noms = AFR.DB.SortsNoms
        local frNom = noms and noms[nomSort]
        return (frNom or nomSort) .. " (Rang " .. rangSort .. ")"
    end
    -- « Realm First! X » : des milliers de hauts faits qui n'existent qu'en
    -- copie « premier du royaume ». Le cœur X est traduit, l'habillage se
    -- compose ici — l'outil ne traduit plus ces copies une à une.
    local exploit = string.match(texte, "^Realm First! (.+)$")
    if exploit then
        local base, hauts = AFR.DB.Epreuves, AFR.DB.HautsFaits
        local fr = (base and base[exploit]) or (hauts and hauts[exploit])
            or Normalisee(exploit)
        if fr then return "Premier du royaume ! " .. fr end
    end
    -- « Battlegear of Might (0/8) » : nom d'ensemble d'objets suivi du
    -- compteur de pièces, dans la même ligne d'info-bulle (22/07,
    -- chantier complétude — paires ItemSet officielles en base).
    local ensemble, compte = string.match(texte,
                                          "^(.-)%s*(%(%d+/%d+%))$")
    if ensemble and ensemble ~= "" then
        local base = AFR.DB.Epreuves
        local fr = base and base[ensemble]
        if fr then return fr .. " " .. compte end
    end
end

-- Objectifs de quête, sous leurs DEUX habits : « 4/10 Webwood Venom Sac »
-- (ordre inversé des suivis — WatchFrame comme DragonUI) et « Webwood Venom
-- Sac: 4/10 » (format serveur). Objets via le pont DB.ObjetsNoms, tués via
-- l'index des créatures. Dans l'intercepteur : TOUS les suivis en profitent.
local function Objectif(texte)
    -- habillage couleur autour du compteur (« |cff…- 0/1|r Webwood Egg ») :
    -- on retente sur la version nue — perte de teinte assumée.
    if string.find(texte, "|c", 1, true) then
        local nu = string.gsub(texte, "|c%x%x%x%x%x%x%x%x", "")
        nu = string.gsub(nu, "|r", "")
        if nu ~= texte then return Objectif(nu) end
    end
    -- objectif-PHRASE (« Speak to Dirania Silvershine in Shadowglen. ») :
    -- pont TDB LogDescription -> locale officielle, tiret toléré.
    local ponts = AFR.DB.QuetesObjectifs
    if ponts then
        local fr = ponts[texte]
        if fr then return fr end
        local tiret, corps = string.match(texte, "^([%-%s]+)(.+)$")
        if corps and ponts[corps] then return tiret .. ponts[corps] end
    end
    -- tiret toléré PARTOUT : DragonUI le met dans la même chaîne
    local avant, fait, total, nom =
        string.match(texte, "^([%-%s]*)(%d+)/(%d+)%s+(.-)%s*$")
    if nom and nom ~= "" then
        local noms = AFR.DB.ObjetsNoms
        local fr = noms and noms[nom]
        if not fr then
            local coeur = string.match(nom, "^(.-) slain$")
            if coeur and AFR.NomCreatureFrancais then
                local c = AFR.NomCreatureFrancais(coeur)
                if c then fr = c .. " tué(s)" end
            end
        end
        -- fragment d'objectif custom (« Carrion Path traversed ») : le
        -- dictionnaire des objectifs le portera dès qu'il sera récolté
        -- et traduit — le canal est prêt.
        if not fr and ponts then
            fr = ponts[nom]
        end
        if fr then
            return avant .. fait .. "/" .. total .. " " .. fr
        end
        return
    end
    local avant2, nom2, fait2, total2 =
        string.match(texte, "^([%-%s]*)(.-): (%d+)/(%d+)%s*$")
    if nom2 and nom2 ~= "" then
        local noms = AFR.DB.ObjetsNoms
        local fr = noms and noms[nom2]
        if fr then
            return avant2 .. fr .. " : " .. fait2 .. "/" .. total2
        end
    end
end

-- « Level 4 Night Elf Felsworn » (fiche de personnage, bulles de joueurs) :
-- niveau + race + classe, chacun via Libelles — la race peut faire deux
-- mots, la classe arrive parfois TEINTÉE (couleur préservée). On ne touche
-- rien si ni race ni classe ne sont reconnues.
local function NiveauRaceClasse(texte)
    -- Niveau teinté (|cff...22|r) : code couleur EXACT à 8 chiffres hexa.
    -- JAMAIS « %x* » devant le niveau : les chiffres décimaux sont aussi
    -- de l'hexa, « Level 22 » perdait son premier 2 et la fiche affichait
    -- « Niveau 2 » (vécu : signalement de <joueur>, 21/07 au soir).
    local niveau, reste = string.match(texte,
        "^Level%s+|c%x%x%x%x%x%x%x%x(%d+)|r%s+(.+)$")
    if not niveau then
        niveau, reste = string.match(texte, "^Level%s+(%d+)%s+(.+)$")
    end
    if not niveau then return end
    local libelles = AFR.DB.Libelles
    if not libelles then return end
    local couleur = string.match(reste, "(|c%x%x%x%x%x%x%x%x)")
    local nu = string.gsub(reste, "|c%x%x%x%x%x%x%x%x", "")
    nu = string.gsub(nu, "|r", "")
    local morceaux = {}
    for mot in string.gmatch(nu, "%S+") do
        table.insert(morceaux, mot)
    end
    if #morceaux < 2 then return end
    -- DEUX passes : d'abord la coupe où race ET classe sont reconnues
    -- (sinon « Undead Witch Hunter » devenait race « Undead Witch » +
    -- classe « Hunter », alors que la classe CoA est « Witch Hunter » —
    -- vécu sur le même signalement). Ensuite seulement, la coupe où une
    -- seule des deux moitiés est connue.
    for exiger_les_deux = 1, 0, -1 do
        for coupe = #morceaux - 1, 1, -1 do
            local race = table.concat(morceaux, " ", 1, coupe)
            local classe = table.concat(morceaux, " ", coupe + 1)
            local raceFR = libelles[race]
            local classeFR = libelles[classe]
            local retenu
            if exiger_les_deux == 1 then
                retenu = raceFR and classeFR
            else
                retenu = raceFR or classeFR
            end
            if retenu then
                classeFR = classeFR or classe
                if couleur then
                    classeFR = couleur .. classeFR .. "|r"
                end
                return "Niveau " .. niveau .. " " .. (raceFR or race)
                    .. " " .. classeFR
            end
        end
    end
end

-- Pierre tombale Ironman de la carte + coordonnées : gabarits composés du
-- client custom. Le PSEUDO du mort n'est jamais traduit ; le tueur passe
-- par l'index des créatures ; dates et durées sont francisées.
local MOIS = {
    January = "janvier", February = "février", March = "mars",
    April = "avril", May = "mai", June = "juin", July = "juillet",
    August = "août", September = "septembre", October = "octobre",
    November = "novembre", December = "décembre",
}
local MORT_MOTS = {
    ["Died."] = "Mort.",
    ["[Melee Attack]"] = "[Attaque en mêlée]",
}

local function Unites(t)
    t = string.gsub(t, "(%d+) Hours?", "%1 h")
    t = string.gsub(t, "(%d+) Minutes?", "%1 min")
    t = string.gsub(t, "(%d+) Seconds?", "%1 s")
    return t
end

local function Carte(texte)
    local reste = string.match(texte, "^Failure Reason: (.+)$")
    if reste then
        return "Cause de l'échec : " .. (MORT_MOTS[reste] or reste)
    end
    local qui, niveau = string.match(texte, "^Killer: (.+) %(Level (%d+)%)$")
    if qui then
        local fr = AFR.NomCreatureFrancais and AFR.NomCreatureFrancais(qui)
        return "Tueur : " .. (fr or qui) .. " (niveau " .. niveau .. ")"
    end
    local degats, source = string.match(texte,
        "^Killing Blow: (%d+) Damage from (.+)$")
    if degats then
        return "Coup fatal : " .. degats .. " dégâts de "
            .. (MORT_MOTS[source] or source)
    end
    reste = string.match(texte, "^Duration: (.+)$")
    if reste then return "Durée : " .. Unites(reste) end
    local mois, jour, heure = string.match(texte, "^(%a+) (%d+) at (.+)$")
    if mois and MOIS[mois] then
        return jour .. " " .. MOIS[mois] .. " à " .. heure
    end
    reste = string.match(texte, "^(.+) ago$")
    if reste then return "il y a " .. Unites(reste) end
    reste = string.match(texte, "^Player: (.+)$")
    if reste then return "Joueur : " .. reste end
    reste = string.match(texte, "^Cursor: (.+)$")
    if reste then return "Curseur : " .. reste end
    -- « <joueur> Level 1 Stormbringer » : pseudo (intact) + niveau + classe
    -- reconnue — la classe arrive parfois teintée, couleur préservée.
    local nu = string.gsub(texte, "|c%x%x%x%x%x%x%x%x", "")
    nu = string.gsub(nu, "|r", "")
    local nom, niv, classe = string.match(nu, "^(%S+) Level (%d+) (.+)$")
    if nom and classe and AFR.DB.Libelles then
        local c = AFR.DB.Libelles[classe]
        if c then
            local couleur = string.match(texte, "(|c%x%x%x%x%x%x%x%x)%s*"
                .. classe:gsub("(%W)", "%%%1"))
            if couleur then c = couleur .. c .. "|r" end
            return nom .. " niveau " .. niv .. " " .. c
        end
    end
    -- « Ironman - Resolute 1x Experience (1) » : au moins Experience
    if string.find(texte, "x Experience", 1, true) then
        return (string.gsub(texte, "x Experience", "x Expérience"))
    end
end

local en_cours = false
-- (`remplaces` et la file `a_balayer` sont déclarés tout en haut :
--  les redéclarer ici créerait une DEUXIÈME variable du même nom, et Brancher
--  et Intercepter ne parleraient plus du même compteur.)

-- Mémoire du verdict de la chaîne de recherche (2.0.1). L'interception
-- voit passer TOUS les textes de l'interface, en boucle : les mêmes
-- reviennent des centaines de fois. Sans mémoire, chaque passage refaisait
-- toute la chaîne (dictionnaires + motifs + normalisation à 4 gsub) — du
-- travail et des déchets mémoire en continu, que le ménage du jeu paie en
-- à-coups. `false` mémorise « aucune traduction ». Vidée au-delà de 8 192.
local memoireVerdict, memoireVerdictNb = {}, 0

-- DESCRIPTIONS de sorts sur les cartes de talents CoA (22/07/2026, phase 2
-- du chantier) : le texte affiché porte des nombres CALCULÉS — le pont des
-- descriptions du dresseur (index flou) retrouve le sort, et l'aligneur
-- replace les nombres de l'écran dans le français. Réservé aux textes
-- longs : une description fait toujours plus de 40 caractères, et les
-- textes courts inonderaient l'index pour rien.
local function DescriptionSort(texte)
    if string.len(texte) <= 40 or not AFR.SortParDescription then return end
    local s = AFR.SortParDescription(texte)
    if not (s and s.D and s.DE) then return end
    return AFR.TraduireTexteSort(s.D, s.DE, texte)
end
AFR.DescriptionSort = DescriptionSort   -- consulté aussi par Francais()

-- ----------------------------------------------------------------------------
-- HÔTEL DES VENTES — INTERDIT DE TRADUIRE (24/07/2026, signalement joueur).
--
-- Même piège que la fenêtre de métier et sa case « Search » : le client
-- reconnaît ses propres catégories À LEUR TEXTE ANGLAIS.
--
--   Blizzard_AuctionUI.lua:754   selectedClass = self:GetText()
--   Blizzard_AuctionUI.lua:639   if selectedClass == CLASS_FILTERS[i] then
--                                    AuctionFrameFilters_UpdateSubClasses(...)
--
-- Le joueur clique « Armure », le client cherche « Armor » : la comparaison
-- échoue, donc les SOUS-CATÉGORIES ne se construisent jamais. Symptôme
-- rapporté : « j'ai pas accès à certaines parties de l'HdV, ça met pas les
-- sous catégories » — et tout remarchait addon coupé.
--
-- Les mêmes boutons servent aux classes, aux sous-classes ET aux types
-- d'emplacement : un seul garde-fou couvre les trois. On perd la traduction
-- de ces libellés — c'est le prix correct, exactement comme pour la case
-- « Search » des métiers.
function EstFiltreHdV(zone)            -- remplit la déclaration d'en haut
    for _ = 1, 3 do                     -- le libellé, son bouton, son parent
        if type(zone) ~= "table" then return false end
        local ok, nom = pcall(zone.GetName, zone)
        if ok and type(nom) == "string"
            and string.find(nom, "^AuctionFilterButton") then
            return true
        end
        local okp, parent = pcall(zone.GetParent, zone)
        if not okp then return false end
        zone = parent
    end
    return false
end
AFR.EstFiltreHdV = EstFiltreHdV        -- réutilisé par le balayage

local function Intercepter(zone, texte)
    if en_cours or Coupee() then return end
    if type(texte) ~= "string" or texte == "" then return end
    if EstFiltreHdV(zone) then return end
    -- Nombres, pourcentages, « 12/20 », dégâts qui défilent : jamais rien
    -- à traduire, et c'est l'écrasante majorité du trafic en combat. On
    -- sort AVANT la chaîne et sans encombrer la mémoire des verdicts.
    if not string.find(texte, "%a") then return end
    local base = AFR.DB and AFR.DB.Epreuves
    if not base then return end
    local fr
    local connu = memoireVerdict[texte]
    if connu ~= nil then
        if connu == false then return end
        fr = connu
    else
        local hauts = AFR.DB.HautsFaits
        local zones, libelles = AFR.DB.Zones, AFR.DB.Libelles
        local objets_noms = AFR.DB.ObjetsNoms
        -- Les GUICHETS (courrier, factions, fêtes) rejoignent la chaîne le
        -- 29/07/2026. Leur matière était en base depuis la 3.4.0 mais ne
        -- s'affichait pas : le panneau de réputation d'Ascension est une
        -- fenêtre MAISON à mixins, ses libellés sont posés sur des zones
        -- de texte ANONYMES — aucun crochet par nom de cadre ne pouvait
        -- les voir. Ici, on les attrape là où ils s'écrivent vraiment, et
        -- ils héritent de toutes les protections de cette fonction
        -- (mémoire des verdicts, garde d'identité, pare-tempête).
        local guichets = AFR.DB.Guichets
        fr = base[texte] or (hauts and hauts[texte])
            or (zones and zones[texte]) or (libelles and libelles[texte])
            or (objets_noms and objets_noms[texte])
            or (guichets and guichets[texte])
            or Chrome(texte)
            or Prefixe(texte) or Normalisee(texte) or Composee(texte)
            or Objectif(texte) or NiveauRaceClasse(texte) or Carte(texte)
            or (AFR.TitreQueteFrancais and AFR.TitreQueteFrancais(texte))
            or DescriptionSort(texte)
        if memoireVerdictNb >= 8192 then
            memoireVerdict, memoireVerdictNb = {}, 0
        end
        memoireVerdict[texte] = fr or false
        memoireVerdictNb = memoireVerdictNb + 1
    end
    if not fr or not Actif() then return end
    -- IDENTITÉ = ne rien faire (audit du 20/07 au soir) : une entrée dont le
    -- français égale l'anglais (« Incarnations ») ou ne diffère que par la
    -- casse via Normalisee re-demandait un balayage à CHAQUE balayage →
    -- boucle perpétuelle, une fois par seconde, pour toute la session.
    -- (Depuis la 2.0.1 le balayage est CIBLÉ sur la fenêtre racine — mais
    -- la garde d'identité reste indispensable, même raison.)
    if fr == texte then return end
    -- PARE-TEMPÊTE (22/07/2026, crash de la Forge mystique ; RECALIBRÉ le
    -- 23/07/2026, signalement de <joueur>) : la forge re-pose son texte À
    -- CHAQUE IMAGE, et un autre addon accroché au même bouton peut re-poser
    -- SON texte en réponse au nôtre — un ping-pong dont chaque échange
    -- gonflait la file de balayage jusqu'à étouffer le client 32 bits.
    -- La 1re version affamait TOUTE la retraduction (retour sans écrire) :
    -- le suivi de quêtes et la feuille de personnage, que le client repose
    -- plusieurs fois par seconde en combat, CLIGNOTAIENT anglais/français
    -- en permanence. La tempête venait du BALAYAGE, pas de l'écriture — et
    -- le français est déjà calculé à ce stade : on écrit donc TOUJOURS le
    -- texte (coût nul), et c'est le rebalayage seul qu'on affame (au plus
    -- deux fois par seconde et par zone).
    local maintenant = GetTime()
    local rafale = zone.AFR_dernier == texte
        and maintenant - (zone.AFR_quand or 0) < 0.5
    zone.AFR_dernier, zone.AFR_quand = texte, maintenant
    -- pcall : si l'écriture échoue, le verrou doit être relâché quand même —
    -- sinon `en_cours` reste coincé à vrai et TOUTE l'interception meurt en
    -- silence pour la session (audit du 20/07/2026).
    en_cours = true
    local ecrit = pcall(zone.SetText, zone, fr)
    en_cours = false
    if not ecrit then return end
    remplaces = remplaces + 1
    -- Un texte de NOTRE dictionnaire vient de s'afficher : SA fenêtre est
    -- donc ouverte et vivante. On rebalaie CETTE fenêtre (éléments fixes :
    -- onglets, boutons — qui ne repassent jamais par ici), et elle seule.
    -- Balayer UIParent entier ici, c'était l'origine des mini-blocages.
    if not rafale then
        DemanderBalayage(RacineDe(zone))
    end
end

-- /afr epreuves — dit ce que le module voit réellement. Sans ce compteur,
-- « ce n'est pas traduit » ne distingue pas « le texte n'est pas dans la
-- base », « le balayage n'atteint pas la fenêtre » et « l'accroche manque ».
-- /afrzone — SONDE de diagnostic v2 (24/07, retour de Dan : « très chiant
-- à screen ») : le relevé s'ouvre dans une FENÊTRE COPIABLE (texte
-- pré-surligné, Ctrl+C, Échap pour fermer) — plus jamais le chat. En plus
-- du cadre sous la souris, la sonde RATISSE toute seule les panneaux
-- visibles au nom évocateur (CoATalent…/…Tooltip…) : plus besoin de viser.
local zoneFenetre

local function AfficherReleve(texte)
    if not zoneFenetre then
        local f = CreateFrame("Frame", "AFRZoneFenetre", UIParent)
        f:SetSize(560, 420)
        f:SetPoint("CENTER")
        f:SetFrameStrata("DIALOG")
        f:SetMovable(true)
        f:EnableMouse(true)
        f:RegisterForDrag("LeftButton")
        f:SetScript("OnDragStart", f.StartMoving)
        f:SetScript("OnDragStop", f.StopMovingOrSizing)
        f:SetBackdrop({
            bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
            edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
            tile = true, tileSize = 32, edgeSize = 32,
            insets = { left = 8, right = 8, top = 8, bottom = 8 },
        })
        local titre = f:CreateFontString(nil, "OVERLAY", "GameFontNormal")
        titre:SetPoint("TOP", 0, -14)
        titre:SetText("AscensionFR — relevé de zone (Ctrl+C, Échap)")
        local defil = CreateFrame("ScrollFrame", "AFRZoneDefil", f,
                                  "UIPanelScrollFrameTemplate")
        defil:SetPoint("TOPLEFT", 16, -36)
        defil:SetPoint("BOTTOMRIGHT", -34, 16)
        local saisie = CreateFrame("EditBox", "AFRZoneSaisie", defil)
        saisie:SetMultiLine(true)
        saisie:SetAutoFocus(false)
        saisie:SetFontObject(ChatFontNormal)
        saisie:SetWidth(500)
        saisie:SetScript("OnEscapePressed", function(self)
            self:ClearFocus()
            f:Hide()
        end)
        defil:SetScrollChild(saisie)
        f.saisie = saisie
        tinsert(UISpecialFrames, "AFRZoneFenetre")
        zoneFenetre = f
    end
    zoneFenetre.saisie:SetText(texte)
    zoneFenetre:Show()
    zoneFenetre.saisie:SetFocus()
    zoneFenetre.saisie:HighlightText()
end
-- Partagée : toute sonde de diagnostic doit ouvrir cette fenêtre copiable
-- (« jamais une pluie de print », consigne de Dan du 24/07). /afrbulle
-- (Sorts.lua) s'en sert.
AFR.AfficherReleve = AfficherReleve

SLASH_AFRZONE1 = "/afrzone"
SlashCmdList["AFRZONE"] = function()
    local lignes = {}
    local n = 0
    local function noter(texte)
        n = n + 1
        if n <= 120 then table.insert(lignes, texte) end
    end
    local function decrire(cadre, etiquette, profondeur)
        if n > 120 or profondeur > 4 or type(cadre) ~= "table" then return end
        local ok_nom, nom = pcall(function() return cadre:GetName() end)
        local ok_genre, genre = pcall(function()
            return cadre:GetObjectType()
        end)
        noter(string.format("%s%s [%s] %s", string.rep("  ", profondeur),
                            etiquette, ok_genre and genre or "?",
                            (ok_nom and nom) or "(anonyme)"))
        if cadre.GetRegions then
            local ok, zones = pcall(function()
                return {cadre:GetRegions()}
            end)
            if ok then
                for i, zone in ipairs(zones) do
                    if type(zone) == "table" and zone.GetText then
                        local lu, t = pcall(zone.GetText, zone)
                        if lu and t and t ~= "" then
                            noter(string.format("%s  texte %d : %s",
                                string.rep("  ", profondeur), i,
                                string.sub(t, 1, 90)))
                        end
                    end
                end
            end
        end
        if cadre.GetChildren then
            local ok, enfants = pcall(function()
                return {cadre:GetChildren()}
            end)
            if ok then
                for _, e in ipairs(enfants) do
                    decrire(e, "enfant", profondeur + 1)
                end
            end
        end
    end

    local focus = GetMouseFocus and GetMouseFocus()
    if focus then
        noter("=== SOUS LA SOURIS ===")
        decrire(focus, "focus", 0)
    end
    noter("")
    noter("=== PANNEAUX VISIBLES (CoATalent / Tooltip) ===")
    local ratisses = 0
    for nom, valeur in pairs(_G) do
        if ratisses >= 8 then break end
        if type(nom) == "string" and type(valeur) == "table"
            and (string.find(nom, "CoATalent") or string.find(nom, "Tooltip"))
            and not string.find(nom, "Text")
            and type(valeur.IsShown) == "function" then
            local ok, visible = pcall(valeur.IsShown, valeur)
            local ok_p, parent = pcall(function()
                return valeur:GetParent()
            end)
            -- seulement les cadres RACINE visibles (le parent est UIParent
            -- ou un cadre CoA) — les milliers de sous-régions n'apprennent
            -- rien.
            if ok and visible and ok_p and parent
                and (parent == UIParent
                     or (parent.GetName and string.find(
                         tostring(parent:GetName() or ""), "CoA"))) then
                ratisses = ratisses + 1
                decrire(valeur, "panneau", 0)
                noter("")
            end
        end
    end
    AfficherReleve(table.concat(lignes, "\n"))
end

SLASH_AFREPREUVES1 = "/afrepreuves"
SlashCmdList["AFREPREUVES"] = function()
    local base = AFR.DB and AFR.DB.Epreuves or {}
    local n = 0
    for _ in pairs(base) do n = n + 1 end
    local avant = remplaces
    if Balayer then pcall(Balayer, UIParent, 1) end
    print("|cff0099ffAscensionFR|r — Épreuves")
    print("  textes en base       : " .. n)
    print("  rattrapés à l'instant: " .. (remplaces - avant))
    print("  remplacements totaux : " .. remplaces)
    print("  « About » connu      : " .. tostring(base["About"] or "NON"))
end

-- Il ne suffit PAS d'accrocher les simples zones de texte. Constaté en jeu le
-- 20/07/2026 : les NOMS passaient en français, pas les descriptions. Le pavé
-- de description a une barre de défilement — c'est un composant d'un autre
-- type, avec sa propre table de méthodes, invisible depuis la première.
-- On accroche donc chaque famille de composants susceptible d'afficher du
-- texte, en dédoublonnant celles qui partagent la même table.
local function Familles()
    local essais = {}

    local ok, zone = pcall(function()
        return UIParent:CreateFontString(nil, "BACKGROUND", "GameFontNormal")
    end)
    if ok and zone then table.insert(essais, zone) end

    -- « Button » est indispensable : un ONGLET n'est pas une zone de texte,
    -- c'est un bouton, et il porte sa propre méthode SetText. Sans lui, les
    -- onglets restaient anglais alors que tout le reste passait (constaté en
    -- jeu : 41 remplacements réussis, zéro onglet touché).
    --
    -- « EditBox » est INTERDITE, et ce n'est pas un oubli. Le texte d'une
    -- zone de saisie appartient au joueur — ou sert de repère au code : la
    -- fenêtre de métier compare le contenu de sa case à « Search » pour
    -- savoir si un filtre est actif. L'avoir réécrit en « Recherche » rendait
    -- le filtre actif en permanence : la fenêtre cherchait des recettes
    -- contenant « Recherche » et s'ouvrait VIDE (vécu le 20/07/2026 —
    -- prouvé par l'interrupteur sansInterception).
    for _, genre in ipairs({"SimpleHTML", "ScrollingMessageFrame",
                            "MessageFrame", "Button", "CheckButton"}) do
        local fait, cadre = pcall(CreateFrame, genre)
        if fait and cadre then
            -- IMPÉRATIF : une EditBox capte le CLAVIER dès sa création
            -- (autoFocus vaut vrai par défaut). Laissée telle quelle, cette
            -- boîte invisible avale toutes les touches du joueur : les
            -- raccourcis semblent intacts mais plus rien n'atteint le jeu.
            -- Vécu le 20/07/2026 — clavier mort en jeu, même après relance.
            pcall(function()
                if cadre.SetAutoFocus then cadre:SetAutoFocus(false) end
                if cadre.ClearFocus then cadre:ClearFocus() end
                if cadre.EnableKeyboard then cadre:EnableKeyboard(false) end
                if cadre.EnableMouse then cadre:EnableMouse(false) end
                cadre:Hide()
            end)
            table.insert(essais, cadre)
        end
    end
    return essais
end

-- BALAYAGE UNIQUE du texte DÉJÀ affiché.
--
-- L'interception ne voit que les textes posés APRÈS elle. Or les onglets
-- (« About », « Leaderboard »…) sont écrits une seule fois à la construction
-- de la fenêtre et plus jamais retouchés : ils resteraient anglais pour
-- toujours. Les restrictions, elles, sont réécrites à chaque sélection, d'où
-- la différence constatée en jeu le 20/07/2026.
-- On parcourt donc une fois ce qui est déjà là. Chaque zone passe par le même
-- filtre : un texte hors dictionnaire reste intact.
function Balayer(cadre, profondeur)
    -- Profondeur 10 : la fenêtre des Épreuves empile cadre > liste défilante
    -- > contenu > élément > bouton. Six niveaux n'y suffisaient pas.
    if Coupee() or profondeur > 10 or type(cadre) ~= "table" then return end
    -- Un bouton porte son texte lui-même, pas seulement dans ses régions.
    -- Mais JAMAIS une zone de saisie : son contenu appartient au joueur ou
    -- sert de repère au code (voir le commentaire de Familles()).
    if type(cadre.GetText) == "function" and type(cadre.SetText) == "function"
        and type(cadre.GetRegions) == "function" then
        local ok_genre, genre = pcall(cadre.GetObjectType, cadre)
        if not (ok_genre and genre == "EditBox") then
            local lu, texte = pcall(cadre.GetText, cadre)
            if lu then Intercepter(cadre, texte) end
        end
    end
    if type(cadre.GetRegions) == "function" then
        local ok, zones = pcall(function() return {cadre:GetRegions()} end)
        if ok then
            for _, zone in ipairs(zones) do
                if type(zone) == "table" and zone.GetText and zone.SetText then
                    local lu, texte = pcall(zone.GetText, zone)
                    if lu then Intercepter(zone, texte) end
                end
            end
        end
    end
    if type(cadre.GetChildren) == "function" then
        local ok, enfants = pcall(function() return {cadre:GetChildren()} end)
        if ok then
            for _, enfant in ipairs(enfants) do
                Balayer(enfant, profondeur + 1)
            end
        end
    end
end

local function AccrocherAffichage()
    local vues, n = {}, 0
    for _, exemple in ipairs(Familles()) do
        local meta = getmetatable(exemple)
        local methodes = meta and meta.__index
        if type(methodes) == "table" and not vues[methodes] then
            vues[methodes] = true
            if type(methodes.SetText) == "function" then
                hooksecurefunc(methodes, "SetText", MESURER("SetText", Intercepter))
                n = n + 1
            end
            -- Les textes composés (« Getting Started 20 / 21 », « Page 1
            -- of 4 ») passent par SetFormattedText, que le crochet SetText
            -- ne voit pas : on relit le résultat formaté et on le repasse
            -- au même filtre.
            if type(methodes.SetFormattedText) == "function" then
                hooksecurefunc(methodes, "SetFormattedText", function(zone)
                    if type(zone.GetText) == "function" then
                        local ok, formate = pcall(zone.GetText, zone)
                        if ok then Intercepter(zone, formate) end
                    end
                end)
            end
        end
    end
    if AFR.Debug then
        AFR.Debug("Épreuves :", n, "familles d'affichage interceptées")
    end
    return n > 0
end

pcall(AccrocherAffichage)

-- QUAND s'accrocher : c'est là qu'étaient les deux échecs précédents.
--
-- `C_Challenge` n'existe NI au chargement, NI à PLAYER_LOGIN : le client ne
-- la crée qu'à la première ouverture de la fenêtre, et aucun événement ne
-- l'annonce. Constaté en jeu le 20/07/2026 : la commande `/run print(type(
-- C_Challenge))` répondait « table » une fois la fenêtre ouverte, alors que
-- notre module n'avait rien trouvé au démarrage.
--
-- On surveille donc son apparition, une fois par seconde. C'est le seul
-- signal disponible. Dès qu'elle est là on enveloppe et on s'arrête : plus
-- rien ne tourne ensuite.
local depuis = 0

-- Fenêtres CoA (talents, garde-robe, vanité) : leurs textes sont posés à la
-- construction, avant nos crochets, et elles se chargent À LA DEMANDE sans
-- événement dédié. On rebalaie à chaque APPARITION de l'une d'elles.
-- (Noms relevés dans collections.lua du client : AddTab(...).)
local COA_FENETRES = {
    "CoATalentFrame", "CharacterAdvancement",
    "AppearanceWardrobeFrame", "StoreCollectionFrame",
    -- le relevé complet des onglets AddTab de Collections.lua (22/07) :
    -- la fenêtre mère, l'Architecte, les Cartes de compétence, la Forge
    -- mystique et la Collection saisonnière manquaient à l'appel.
    "Collections", "BuildCreatorFrame", "SkillCardsFrame",
    "EnchantCollection", "SeasonCollectionFrame",
    -- grimoire : la page « Professions » pose ses libellés à la construction
    "SpellBookFrame",
    -- feuille de personnage custom (stats, onglets)
    "CharacterFrame",
    -- carte du monde (titre, cases, coordonnées)
    "WorldMapFrame",
    -- fenêtre de détail de quête (clic sur le suivi)
    "QuestLogDetailFrame",
}
-- (l'ancien suivi coa_visibles a disparu : on re-balaie désormais les
--  fenêtres CoA visibles à chaque tic, pas seulement à l'apparition)

local veilleuse = CreateFrame("Frame")
if AFR.Perf then AFR.Perf.Suivre("Epreuves", veilleuse) end
veilleuse:SetScript("OnUpdate", function(self, ecoule)
    depuis = depuis + ecoule
    if depuis < 1 then return end
    depuis = 0

    -- AVANT la barrière `branche` : ces fenêtres vivent sans C_Challenge.
    for _, nom in ipairs(COA_FENETRES) do
        local cadre = _G[nom]
        if cadre and cadre.IsShown and cadre:IsShown() then
            -- Re-balayée à CHAQUE tic tant qu'elle est ouverte (1x/s,
            -- fenêtre seule — jamais tout l'écran) : les fenêtres CoA se
            -- redessinent en naviguant (onglets, arbres) sans le moindre
            -- événement, et le balayage unique à l'apparition laissait
            -- l'anglais revenir (vécu : cartes de talents, 22/07).
            DemanderBalayage(cadre)
        end
    end

    -- Brancher est idempotent (marques `posees`) : on le repasse tant que
    -- la fenêtre vit. L'ancien verrou « branche » figeait le PREMIER espace
    -- API arrivé — si C_TrialCreator apparaissait avant C_Challenge, l'autre
    -- restait anglais pour la session (audit du 20/07 au soir).
    if type(C_Challenge) == "table" or type(C_TrialCreator) == "table" then
        pcall(Brancher)
    end

    -- La veilleuse NE S'ARRÊTE PLUS après le branchement. Après un /reload,
    -- `C_Challenge` existe déjà — c'est une table du CLIENT, elle survit au
    -- rechargement du Lua. Le balayage se déclenchait donc aussitôt, sur un
    -- écran où la fenêtre n'était pas ouverte, ne trouvait rien, et ne
    -- revenait jamais : les onglets restaient anglais jusqu'à un /afrepreuves
    -- manuel. On rebalaie désormais chaque fois qu'une fenêtre s'anime.
    if a_balayer_nb > 0 then
        for cadre in pairs(a_balayer) do
            if cadre.IsShown and cadre:IsShown() then
                pcall(Balayer, cadre, 1)
            end
        end
        a_balayer = {}
        a_balayer_nb = 0
    end
end)

-- Au cas où l'API serait déjà là (rechargement en cours de partie).
-- SURTOUT ne pas éteindre la veilleuse ici. Après un /reload, C_Challenge
-- existe déjà (table du CLIENT, elle survit au rechargement du Lua) : ce bloc
-- s'exécute donc à chaque fois. L'ancienne ligne « SetScript(nil) » qui
-- traînait ici tuait le rebalayage au démarrage — les onglets restaient
-- anglais après chaque /reload alors que tout le reste passait (20/07/2026).
if type(C_Challenge) == "table" then
    pcall(Brancher)
end

-- ==========================================================================
-- INFO-BULLES (hauts faits des Épreuves, conditions, liens cliqués)
-- ==========================================================================
-- GameTooltip:SetText et AddLine sont des méthodes C du tooltip LUI-MÊME :
-- le crochet posé sur les zones de texte ne les voit jamais passer. On
-- repasse donc sur les lignes affichées à l'ouverture de la bulle — même
-- procédé que le micro-menu dans InterfaceCiblee.lua.

local FORMATS = {
    -- Textes composés avec un nom de joueur dedans. Le français est celui de
    -- DB_Interface (ACHIEVEMENT_TOOLTIP_IN_PROGRESS…). Si Ascension change
    -- sa formulation, le motif ne mord plus et l'anglais reste — sans casse.
    { motif = "^Achievement in progress by (.+)$",
      gabarit = "Haut fait en cours pour %s" },
    { motif = "^Achievement earned by (.+)$",
      gabarit = "Haut fait accompli par %s" },
    -- en-têtes de la bulle de performance du menu de jeu
    { motif = "^Latency: (%d+) ms$",
      gabarit = "Latence : %s ms" },
    { motif = "^Framerate: (%d+) fps$",
      gabarit = "Rafraîchissement : %s ips" },
    { motif = "^AddOn Memory: ([%d%.]+) MB$",
      gabarit = "Mémoire des addons : %s Mo" },
    -- « Rank N » du grimoire (le motif de Francais() ne couvre que le
    -- chemin du balayage ; celui-ci couvre le crochet SetText, 21/07).
    { motif = "^Rank (%d+)$", gabarit = "Rang %s" },
    -- Fenêtre des compagnons/montures : le même gabarit habille les
    -- 1 993 montures du jeu — un seul motif les couvre toutes (21/07).
    { motif = "^Summons and dismisses your (.+)%. This mount's speed "
        .. "changes depending on your Riding skill and location%.$",
      gabarit = "Invoque et renvoie votre %s. La vitesse de cette monture "
        .. "dépend de votre compétence de monte et de l'endroit où vous "
        .. "vous trouvez." },
}

local function FrancaisLigneCalcul(texte)
    local base, hauts = AFR.DB.Epreuves, AFR.DB.HautsFaits
    local zones = AFR.DB.Zones
    -- pont des noms de sorts (grimoire, barres — l'ID n'est pas accessible
    -- au moment où le nom s'affiche, on passe donc par le texte, 21/07)
    local noms_sorts = AFR.DB.SortsNoms
    local fr = (base and base[texte]) or (hauts and hauts[texte])
        or (zones and zones[texte])
        or (noms_sorts and noms_sorts[texte])
    -- Titres de quêtes du JOURNAL (la liste de gauche, 21/07) : le pont
    -- des titres existait, la liste n'y était pas branchée.
    if not fr and AFR.QueteParTitreEN then
        local q = AFR.QueteParTitreEN(texte)
        if q and q.T then fr = q.T end
    end
    fr = fr
        or Chrome(texte) or Prefixe(texte) or Normalisee(texte)
        or Objectif(texte) or NiveauRaceClasse(texte) or Carte(texte)
    if fr then return fr end
    -- « [Monk] Slow and Steady » : l'habillage [Classe] varie d'un haut fait
    -- à l'autre, mais le cœur est déjà dans les dictionnaires.
    local devant, coeur = string.match(texte, "^(%[.-%]%s*)(.+)$")
    if coeur then
        fr = (base and base[coeur]) or (hauts and hauts[coeur])
            or Normalisee(coeur)
        if fr then return devant .. fr end
    end
    -- « Realm First! X » : composé, comme dans Composee.
    local exploit = string.match(texte, "^Realm First! (.+)$")
    if exploit then
        fr = (base and base[exploit]) or (hauts and hauts[exploit])
            or Normalisee(exploit)
        if fr then return "Premier du royaume ! " .. fr end
    end
    -- Titre de zone de la carte du monde : « Stonetalon Mountains (15-60) ».
    -- La tranche de niveaux collée cassait le match exact ; on la détache,
    -- on traduit le nom via le pont de zones, on recolle (21/07).
    if zones then
        local nomZone, apres =
            string.match(texte, "^(.-)(%s*%(%d+%-%d+%))$")
        if nomZone and zones[nomZone] then
            return zones[nomZone] .. apres
        end
    end
    for _, f in ipairs(FORMATS) do
        local argument = string.match(texte, f.motif)
        if argument then
            -- si la capture (nom de monture, de joueur...) a sa propre
            -- traduction exacte, on l'utilise ; sinon elle passe telle
            -- quelle — jamais de texte cassé.
            local capture_fr = base and base[argument]
            return string.format(f.gabarit, capture_fr or argument)
        end
    end
    -- ------------------------------------------------------------------
    -- Bulles de TALENTS CoA (24/07) : GameTooltip est rempli par du code C
    -- (SetSpellByID + AddLine), invisible de toute interception SetText —
    -- CE repassage-ci est donc leur SEUL traducteur. Trois manques comblés :
    -- ------------------------------------------------------------------
    -- « Rank 0/1 » (deux captures — hors gabarits FORMATS, à une seule).
    local a, b = string.match(texte, "^Rank (%d+)%s*/%s*(%d+)$")
    if a then return "Rang " .. a .. "/" .. b end
    -- « Pure Shadow (Rank 1) » (28/07) : même motif composé que dans
    -- Composee — ce chemin-ci couvre les bulles et le balayage des
    -- fenêtres custom (TraduireZoneCustom), l'autre couvre l'écriture
    -- au SetText. AVANT de composer via le pont : DB_ObjetsNoms porte
    -- 225 clés exactes « X (Rank n) » au français soigné (mesure du
    -- sceptique, 28/07 : sans ce filet, 175 sortiraient demi-traduites
    -- et 34 CONTREDITES — « Cleanse (Rank 5) » doit rendre
    -- « Purifier (Rang 5) » arbitré, pas « Épuration (Rang 5) »).
    -- Le chemin SetText, lui, est déjà protégé par l'ordre
    -- objets_noms-avant-Composee d'Intercepter (vérifié au moteur).
    local nomSort, rangSort = string.match(texte,
                                           "^(.-)%s+%(Rank%s+(%d+)%)$")
    if nomSort and nomSort ~= "" then
        local objets = AFR.DB.ObjetsNoms
        local frObjet = objets and objets[texte]
        if frObjet then return frObjet end
        local frNom = noms_sorts and noms_sorts[nomSort]
        return (frNom or nomSort) .. " (Rang " .. rangSort .. ")"
    end
    -- Libellés d'interface au texte exact (« Click to learn »...) : le même
    -- index inverse des GlobalStrings que la fenêtre des talents.
    local libelle = Libelle(texte)
    if libelle then return libelle end
    -- Descriptions de sorts (bloc d'aura incrusté) : même dernier recours
    -- que les cartes CoA — index flou des descriptions + aligneur
    -- (tout-ou-rien, jamais de texte cassé).
    if AFR.DescriptionSort then
        local fr = AFR.DescriptionSort(texte)
        if fr then return fr end
    end
    -- Lignes HABILLÉES : icône |T...|t en tête (la ligne-nom du bloc
    -- incrusté), ou enveloppe de couleur autour du texte entier. Les ponts
    -- travaillent sur texte NU — on déshabille, on traduit, on rhabille.
    local icone, reste = string.match(texte, "^(|T[^|]*|t%s*)(.+)$")
    if icone then
        local fr = FrancaisLigneCalcul(reste)
        if fr then return icone .. fr end
    end
    local deb, coeur = string.match(texte,
        "^(|c%x%x%x%x%x%x%x%x)(.-)|r%s*$")
    if deb and coeur and coeur ~= "" then
        local fr = FrancaisLigneCalcul(coeur)
        if fr then return deb .. fr .. "|r" end
    end
    -- Espaces d'habillage (la ligne « icône + nom » du bloc incrusté
    -- arrive avec une espace de tête) : on rogne, on traduit, on remet.
    local gauche, mot, droite = string.match(texte, "^(%s+)(.-)(%s*)$")
    if gauche and mot and mot ~= "" then
        local fr = FrancaisLigneCalcul(mot)
        if fr then return gauche .. fr .. droite end
    end
    -- BLOC FUSIONNÉ (relevé /afrbulle du 24/07) : le client livre le bloc
    -- d'aura incrusté en UNE zone de texte — sous-ligne vide, « icône +
    -- nom », description, séparés par des retours à la ligne. On traduit
    -- PAR PARAGRAPHE, TOUT-OU-RIEN : un paragraphe à lettres sans
    -- traduction = ligne entière rendue telle quelle (jamais de mélange).
    if string.find(texte, "\n", 1, true) then
        local morceaux, change = {}, false
        for seg in string.gmatch(texte .. "\n", "([^\n]*)\n") do
            seg = string.gsub(seg, "\r$", "")
            if not string.find(seg, "%a") then
                table.insert(morceaux, seg)
            else
                local fr = FrancaisLigneCalcul(seg)
                if not fr then return nil end
                if fr ~= seg then change = true end
                table.insert(morceaux, fr)
            end
        end
        if change then return table.concat(morceaux, "\n") end
    end
end

-- MÉMOIRE DES RÉSULTATS. Une info-bulle survolée se redessine en continu :
-- chaque ligne repassait toute la chaîne (dictionnaires, motifs FORMATS...)
-- à chaque image — y compris les lignes SANS traduction, les plus
-- nombreuses. On mémorise donc aussi les échecs (`false` = « pas de
-- traduction, inutile de rechercher »). Les bases ne changent pas en cours
-- de session : la mémoire ne peut pas devenir fausse. Vidée au-delà de
-- 8 192 entrées (les textes à nombres dynamiques ne peuvent pas
-- l'engraisser sans fin).
local memoireLigne, memoireLigneNb = {}, 0

local function FrancaisLigne(texte)
    local connu = memoireLigne[texte]
    if connu ~= nil then
        if connu == false then return nil end
        return connu
    end
    local fr = FrancaisLigneCalcul(texte)
    if memoireLigneNb >= 8192 then
        memoireLigne, memoireLigneNb = {}, 0
    end
    memoireLigne[texte] = fr or false
    memoireLigneNb = memoireLigneNb + 1
    return fr
end

local bulle_en_cours = false

local function TraduireBulle(bulle)
    if bulle_en_cours or Coupee() or not Actif()
        or type(bulle) ~= "table" then return end
    local nom = bulle.GetName and bulle:GetName()
    if not nom or type(bulle.NumLines) ~= "function" then return end
    local change = false
    for i = 1, bulle:NumLines() do
        local zone = _G[nom .. "TextLeft" .. i]
        local texte = zone and zone:GetText()
        if texte and texte ~= "" then
            local fr = FrancaisLigne(texte)
            if fr and fr ~= texte then
                zone:SetText(fr)
                change = true
            end
        end
    end
    -- Le français est plus long que l'anglais : sans ce rappel, la bulle
    -- garde sa largeur anglaise et le texte déborde. Le verrou empêche notre
    -- propre Show() de nous rappeler en boucle.
    if change then
        bulle_en_cours = true
        pcall(bulle.Show, bulle)   -- le verrou doit survivre à une erreur
        bulle_en_cours = false
    end
end

-- GameTooltip = le survol ; ItemRefTooltip = la bulle qui s'ouvre quand on
-- CLIQUE un lien de haut fait dans le chat ; WorldMapTooltip = le survol
-- des points de quête sur la CARTE (titres + objectifs dynamiques).
for _, bulle in ipairs({GameTooltip, ItemRefTooltip, WorldMapTooltip}) do
    if bulle then
        if bulle.HookScript then
            bulle:HookScript("OnShow", TraduireBulle)
        end
        hooksecurefunc(bulle, "Show", TraduireBulle)
    end
end

-- ============================================================================
-- LE GRIMOIRE, EN DIRECT (21/07) : les noms des boutons passaient entre les
-- mailles des familles interceptées — crochet explicite sur la mise à jour
-- des boutons du grimoire, mécanique garantie et testable.
-- ============================================================================
if type(SpellButton_UpdateButton) == "function" then
    local SUFFIXES_GRIMOIRE = { "SpellName", "SubSpellName" }
    hooksecurefunc("SpellButton_UpdateButton", MESURER("Grimoire", function(bouton)
        if Coupee() or not Actif() or not bouton then return end
        local nom = bouton.GetName and bouton:GetName()
        if not nom then return end
        for i = 1, 2 do
            local zone = _G[nom .. SUFFIXES_GRIMOIRE[i]]
            local texte = zone and zone.GetText and zone:GetText()
            if texte and texte ~= "" then
                local ok, fr = pcall(FrancaisLigne, texte)
                if ok and fr and fr ~= texte then
                    zone:SetText(fr)
                end
            end
        end
    end))
end

-- ============================================================================
-- FENÊTRES CUSTOM D'ASCENSION (24/07, captures de Dan). Plusieurs de leurs
-- fenêtres maison — le GRIMOIRE (« Auto Attack », « Dodge » restaient
-- anglais), la RECHERCHE DE GROUPE (« Random Dungeon », « Find a Group »),
-- le JcJ (« Quick Match », « Glory »), les RÈGLES JcJ (« A Safer Haven »,
-- « High-Risk Mode »…) — n'émettent AUCUN signal Blizzard qu'on saurait
-- crocher, et leurs textes sont des GlobalStrings qu'on n'écrit plus en masse
-- (taint, TRADUIRE_INTERFACE=false). Remède PROUVÉ (méthode d'AutoBookFR de
-- Glayna, généralisée) : repérer la fenêtre par son TITRE puis PARCOURIR son
-- arbre de FontStrings, traduits par NOTRE chaîne (FrancaisLigne -> Libelle
-- sur DB.UI + tous les dictionnaires). On ne touche QUE des FontStrings
-- (SetText d'affichage) : jamais une fonction protégée -> pas de taint.
-- Réversible par /afr (Coupee). Étendre = ajouter un titre à TITRES_CUSTOM.
-- ============================================================================
-- Titres (barre de fenêtre / onglet) qui identifient une fenêtre à traduire —
-- forme ANGLAISE (source) ET FRANÇAISE (une fois qu'on l'a traduite, la
-- détection doit continuer de mordre). Spécifiques, pour ne pas parcourir des
-- fenêtres non voulues.
local TITRES_CUSTOM = {
    ["Grimoire"] = true, ["Spellbook"] = true,
    ["Dungeons & Raids"] = true, ["Donjons et raids"] = true,
    ["Player vs Player"] = true, ["Joueur contre joueur"] = true,
    ["PvP Ruleset"] = true, ["Ensemble de règles PvP"] = true,
    ["Mythic+ Dungeons"] = true, ["Donjons Mythique+"] = true,

    -- Vague 2 (24/07) : fenêtres maison relevées dans les MPQ du client, en
    -- lisant les appels *SetTitle des 33 addons Ascension embarqués. Leur
    -- texte était DÉJÀ dans nos bases — il ne s'affichait simplement jamais,
    -- faute que la fenêtre soit reconnue. Même piège que le grimoire.
    --
    -- Volontairement des titres SPÉCIFIQUES : les mots isolés (« Wildcard »,
    -- « Talents ») feraient mordre la détection sur des fenêtres non voulues.
    ["Rapid Rolling"] = true, ["Roulement rapide"] = true,
    ["The Manastorm"] = true, ["La Tempête Mana"] = true,
    ["Character Advancement"] = true, ["Avancement du personnage"] = true,
    ["Conquest of Azeroth - Character Advancement"] = true,
    ["Conquête d'Azeroth – Avancement du personnage"] = true,
    ["Customer Support"] = true, ["Assistance clients"] = true,
    ["Skill Cards"] = true, ["Cartes de compétences"] = true,
    ["Submit Feedback"] = true, ["Envoyer des commentaires"] = true,
    ["Talk to a Game Master"] = true, ["Parler à un Maître de jeu"] = true,
    ["Wardrobe"] = true, ["Garde-robe"] = true,
    ["Archetypes"] = true, ["Archétypes"] = true,
    ["Hand of Fate"] = true, ["Main du destin"] = true,
    ["Mastery Draft"] = true, ["Draft de maîtrise"] = true,

    -- Le tirage de la roulette (2e capture de Dan) est un cadre FLOTTANT,
    -- SANS barre de titre : rien à reconnaître en haut. On le repère donc à
    -- ses deux boutons, qui ne se rencontrent nulle part ailleurs. La
    -- détection cherche un texte connu n'importe où dans les 6 premiers
    -- niveaux du cadre : un libellé de bouton fait donc très bien l'affaire.
    ["Roll Abilities"] = true, ["Relancer les capacités"] = true,
    ["Keep Abilities"] = true, ["Conserver les capacités"] = true,
}

local function EstFontString(o)
    return o and o.GetObjectType and o:GetObjectType() == "FontString"
end

local function TraduireZoneCustom(o)
    if not (EstFontString(o) and o.GetText and o.SetText) then return end
    local ok, t = pcall(o.GetText, o)
    if not (ok and type(t) == "string" and t ~= "") then return end
    local okf, fr = pcall(FrancaisLigne, t)
    if okf and fr and fr ~= t then pcall(o.SetText, o, fr) end
end

local function ParcourirFenetre(cadre, profondeur, vus)
    if not cadre or profondeur > 18 or vus[cadre] then return end
    vus[cadre] = true
    TraduireZoneCustom(cadre)
    if cadre.GetRegions then
        local ok, regions = pcall(function() return { cadre:GetRegions() } end)
        if ok then
            for _, r in ipairs(regions) do TraduireZoneCustom(r) end
        end
    end
    if cadre.GetChildren then
        local ok, enfants = pcall(function()
            return { cadre:GetChildren() }
        end)
        if ok then
            for _, e in ipairs(enfants) do
                ParcourirFenetre(e, profondeur + 1, vus)
            end
        end
    end
end

-- Titre connu ? Deux formes, et deux seulement.
--
-- 1. le titre EXACT (« Grimoire ») ;
-- 2. le titre COMPOSÉ, qu'Ascension fabrique par
--    format("%s - %s", CHARACTER_ADVANCEMENT, WILDCARD_MODE) — ce qui donne
--    « Character Advancement - Wildcard » à l'écran. Vu sur les captures de
--    Dan du 24/07 : la comparaison exacte ne mordait pas, la fenêtre entière
--    restait donc en anglais alors que TOUT son texte était déjà traduit.
--
-- On découpe sur « - » et on accepte si un morceau est un titre connu. On
-- reste donc sur des titres ENTIERS : pas de recherche de sous-chaîne, qui
-- ferait mordre la détection sur des fenêtres non voulues.
local function TitreConnu(t)
    if type(t) ~= "string" or t == "" then return false end
    if TITRES_CUSTOM[t] then return true end
    if not string.find(t, " - ", 1, true) then return false end
    for morceau in string.gmatch(t, "[^%-]+") do
        local nu = string.gsub(morceau, "^%s*(.-)%s*$", "%1")
        if TITRES_CUSTOM[nu] then return true end
    end
    return false
end

-- Un cadre est « à traduire » si l'un de ses FontStrings porte un TITRE connu.
-- Profondeur bornée : le titre est près du sommet.
--
-- ZÉRO ALLOCATION (programme 11, 01/08/2026). Cette sonde descendait jusqu'à
-- six niveaux en fabriquant, À CHAQUE NŒUD VISITÉ, une fermeture et une table
-- pour les régions, puis une fermeture et une table pour les enfants. Sur des
-- centaines de cadres testés deux fois par seconde, c'était le premier
-- producteur de déchets de l'addon.
--
-- `pcall(cadre.GetRegions, cadre)` rend « ok » SUIVI DE TOUTES les régions :
-- en passant ce résultat tel quel en fin de liste d'arguments, on garde la
-- protection du pcall et on ne fabrique plus rien. Même remède que Plaques.lua
-- le 28/07 et BarresDeVie.lua le 01/08.
local PorteUnTitre

local function TitreParmiRegions(ok, ...)
    if not ok then return false end
    for i = 1, select("#", ...) do
        local r = select(i, ...)
        if EstFontString(r) and r.GetText then
            local okt, t = pcall(r.GetText, r)
            if okt and TitreConnu(t) then return true end
        end
    end
    return false
end

local function TitreParmiEnfants(profondeur, vus, ok, ...)
    if not ok then return false end
    for i = 1, select("#", ...) do
        if PorteUnTitre(select(i, ...), profondeur + 1, vus) then return true end
    end
    return false
end

PorteUnTitre = function(cadre, profondeur, vus)
    if not cadre or profondeur > 6 or vus[cadre] then return false end
    vus[cadre] = true
    if EstFontString(cadre) and cadre.GetText then
        local ok, t = pcall(cadre.GetText, cadre)
        if ok and TitreConnu(t) then return true end
    end
    if cadre.GetRegions then
        if TitreParmiRegions(pcall(cadre.GetRegions, cadre)) then return true end
    end
    if cadre.GetChildren then
        if TitreParmiEnfants(profondeur, vus,
                             pcall(cadre.GetChildren, cadre)) then
            return true
        end
    end
    return false
end

-- ----------------------------------------------------------------------------
-- MÉMOIRE DES ÉCHECS, AVEC DROIT DE REVENIR DESSUS (programme 11, 01/08/2026)
--
-- LE DÉFAUT, mesuré en jeu chez Dan : ce module pesait 7,5 à 10,1 ms/s à
-- Hurlevent — 97 à 99 % de tout ce que l'instrument mesurait — avec un pire tic
-- de 13 ms, soit presque une image entière avalée, deux fois par seconde.
--
-- Sa cause tenait en une ligne : plus bas, `suivi[c] = true` n'était écrit
-- qu'en cas de SUCCÈS. Un cadre qui échouait n'était donc jamais mémorisé et se
-- refaisait fouiller toutes les 0,5 s, pour toute la session. Sur les 150 à 300
-- enfants visibles d'UIParent, 99 % échouent : on payait une descente
-- récursive de profondeur 6 sur chacun d'eux, deux fois par seconde, pour rien.
--
-- LE PIÈGE DE LA CORRECTION. Mémoriser l'échec pour toujours est la réponse
-- évidente, et elle est fausse : une fenêtre créée VIDE puis remplie plus tard
-- (titre posé après coup, onglet construit à la demande, addon chargé après le
-- login) échouerait au premier test et ne serait PLUS JAMAIS retestée. On
-- gagnerait des images et on perdrait des traductions — en silence, sans que
-- rien ne le signale. Ce serait pire que le défaut qu'on répare.
--
-- CE QU'ON FAIT — deux mécanismes, et ils se complètent :
--
--   1. L'ATTENTE QUI DOUBLE. Un échec met le cadre au repos 2 s, puis 4, 8, 16,
--      et 30 s au plus. Un cadre qui n'est pas une fenêtre custom finit donc
--      coûté une fois toutes les 30 s au lieu de deux fois par seconde — 60
--      fois moins — mais il n'est JAMAIS abandonné. Le rattrapage est garanti,
--      il est seulement lent pour ce qui n'a jamais rien donné.
--
--   2. LE RETOUR À ZÉRO QUAND LE CADRE DISPARAÎT. Dès qu'un cadre passe à
--      caché, on efface son ardoise : une fenêtre qu'on ferme et rouvre est
--      retestée immédiatement. C'est le cas réel le plus fréquent — le joueur
--      ouvre un panneau, le client le remplit, il le rouvre — et il ne coûte
--      rien : on lit un `IsShown()` qu'on lisait déjà.
--
-- CE QUE ÇA NE COUVRE PAS, et il faut le dire plutôt que de le découvrir :
-- un cadre qui reste affiché SANS INTERRUPTION et qui ne gagne son titre
-- qu'au bout d'un moment attend jusqu'à 30 secondes avant d'être retraduit.
-- Personne ne perd de traduction, mais elle peut arriver en retard. C'est
-- l'échange qu'on accepte ; ATTENTE_MAX est là pour le rediscuter.
-- ----------------------------------------------------------------------------
local ATTENTE_MIN = 2       -- s. Premier repos après un échec.
local ATTENTE_MAX = 30      -- s. Plafond : on ne renonce jamais au-delà.

-- Clés faibles : on ne retient pas un cadre en vie pour nos comptes.
local prochain_essai = setmetatable({}, { __mode = "k" })
local attente_courante = setmetatable({}, { __mode = "k" })
local dernier_rearme = setmetatable({}, { __mode = "k" })

-- Une seule table de visite, réutilisée. Elle était refabriquée à chaque cadre
-- testé. Clés faibles là encore, pour ne rien retenir entre deux passages.
local vus_essai = setmetatable({}, { __mode = "k" })

local function NoterEchec(cadre, maintenant)
    local d = attente_courante[cadre]
    d = d and (d * 2) or ATTENTE_MIN
    if d > ATTENTE_MAX then d = ATTENTE_MAX end
    attente_courante[cadre] = d
    prochain_essai[cadre] = maintenant + d
end

-- Le cadre a été adopté, ou le monde a changé : on efface tout.
local function Oublier(cadre)
    prochain_essai[cadre] = nil
    attente_courante[cadre] = nil
    dernier_rearme[cadre] = nil
end

-- ----------------------------------------------------------------------------
-- LE CADRE VIENT DE DISPARAÎTRE — et ce qu'on décide ici change tout.
--
-- ⚠️ MA PREMIÈRE VERSION AVAIT UN DÉFAUT, mesuré et non supposé. J'effaçais
-- TOUT au masquage, pour qu'une fenêtre fermée puis rouverte soit retestée sans
-- attendre. Conséquence : un cadre qui CLIGNOTE remettait son compteur à zéro
-- sans arrêt, et repayait une descente complète toutes les 2 secondes.
--
-- Or les cadres qui clignotent sont les plus actifs de l'interface :
-- `GameTooltip` (à CHAQUE survol de souris), `CastingBarFrame`, `LootFrame`,
-- `MirrorTimer1`, `DurabilityFrame`, `ComboFrame`, ceux de DragonUI. Mesuré au
-- banc : un seul cadre clignotant coûtait 150 visites là où un cadre stable en
-- coûte 3 — vingt-trois fois plus. En ville, souris en mouvement, tout le gain
-- annoncé fondait.
--
-- CE QUI SÉPARE VRAIMENT LES DEUX POPULATIONS, ce n'est pas le nombre d'échecs
-- (je l'ai essayé, c'était le mauvais discriminant) : c'est LA CADENCE. Un
-- joueur qui ferme et rouvre un panneau le fait de temps en temps ; une bulle
-- d'aide clignote plusieurs fois par seconde.
--
-- On limite donc le RYTHME des reprises : un cadre a droit à **un** essai
-- gratuit toutes les ATTENTE_MAX secondes, quelle que soit sa frénésie. Le
-- joueur garde son retest immédiat ; GameTooltip n'obtient au plus qu'une
-- descente toutes les 30 secondes au lieu d'une par survol.
-- ----------------------------------------------------------------------------
local function AuMasquage(cadre, maintenant)
    local dernier = dernier_rearme[cadre]
    if dernier and (maintenant - dernier) < ATTENTE_MAX then return end
    dernier_rearme[cadre] = maintenant
    prochain_essai[cadre] = nil     -- le minuteur seulement, jamais l'attente
end

-- Un seul cadre candidat. Rend true s'il a été adopté.
local function EssayerCadre(cadre, suivi, maintenant)
    if not cadre or not cadre.IsShown then return false end
    local ok, affiche = pcall(cadre.IsShown, cadre)
    if not (ok and affiche) then
        if prochain_essai[cadre] then AuMasquage(cadre, maintenant) end
        return false
    end
    if suivi[cadre] then return false end
    local prochain = prochain_essai[cadre]
    if prochain and maintenant < prochain then return false end

    wipe(vus_essai)
    if PorteUnTitre(cadre, 0, vus_essai) then
        Oublier(cadre)
        suivi[cadre] = true
        ParcourirFenetre(cadre, 0, {})
        return true
    end
    NoterEchec(cadre, maintenant)
    return false
end

-- Les candidats nommés. La liste était refabriquée à chaque passage ; on ne
-- garde que les NOMS (constants) et on relit _G au moment voulu — ces cadres
-- n'existent pas forcément au chargement.
local NOMS_CANDIDATS = {
    "SpellBookFrame", "AscensionSpellBookFrame", "SpellbookFrame",
    "PlayerSpellsFrame", "PVEFrame", "PVPUIFrame", "GroupFinderFrame",
}

local function EssayerTous(suivi, maintenant, ok, ...)
    if not ok then return end
    for i = 1, select("#", ...) do
        EssayerCadre(select(i, ...), suivi, maintenant)
    end
end

-- Repère TOUTES les fenêtres custom visibles (grimoire + LFG/JcJ peuvent
-- coexister) et les ajoute au suivi.
local function DetecterFenetres(suivi)
    local maintenant = (type(GetTime) == "function" and GetTime()) or 0
    for i = 1, #NOMS_CANDIDATS do
        EssayerCadre(_G[NOMS_CANDIDATS[i]], suivi, maintenant)
    end
    if UIParent and UIParent.GetChildren then
        EssayerTous(suivi, maintenant, pcall(UIParent.GetChildren, UIParent))
    end
end

-- Purge complète : au changement de monde, tout est reconstruit côté client et
-- nos ardoises n'ont plus de sens. C'est le seul endroit où l'on repart
-- vraiment de zéro. (Les clés faibles feraient le ménage toutes seules à la
-- longue ; ceci le rend immédiat et explicite.)
function AFR.PerfEpreuvesPurger()
    wipe(prochain_essai)
    wipe(attente_courante)
    wipe(dernier_rearme)
    wipe(vus_essai)
end

local purge = CreateFrame("Frame")
purge:RegisterEvent("PLAYER_ENTERING_WORLD")
purge:SetScript("OnEvent", AFR.PerfEpreuvesPurger)

local fenetresCustom = {}
local montre = CreateFrame("Frame")
if AFR.Perf then AFR.Perf.Suivre("Epreuves", montre) end
local depuisTrad, depuisScan = 0, 0
montre:SetScript("OnUpdate", function(self, elapsed)
    if Coupee() or not Actif() then return end
    depuisTrad = depuisTrad + elapsed
    depuisScan = depuisScan + elapsed
    -- Fenêtres déjà repérées et encore ouvertes : on repeint (~0,15 s ; ces
    -- fenêtres reconstruisent leur texte au changement d'onglet/de page).
    if depuisTrad >= 0.15 then
        depuisTrad = 0
        for cadre in pairs(fenetresCustom) do
            if cadre.IsShown and cadre:IsShown() then
                ParcourirFenetre(cadre, 0, {})
            else
                fenetresCustom[cadre] = nil
            end
        end
    end
    -- Détection plus espacée (~0,5 s) : ajoute les fenêtres nouvellement
    -- ouvertes sans rien coûter quand tout est fermé.
    if depuisScan >= 0.5 then
        depuisScan = 0
        DetecterFenetres(fenetresCustom)
    end
end)

-- ============================================================================
-- MENUS DÉROULANTS, EN DIRECT (22/07) : les listes UIDropDownMenu (menu de
-- tchat, Emote vocale, clic droit...) ne passent PAS par les familles
-- interceptées — même leçon que le grimoire, même remède : crochet explicite
-- sur l'ajout de chaque entrée. Couvre « Say » -> « Dire », « /hello » ->
-- « /salut » (paires posées par le module Émotes), et tout texte connu de
-- FrancaisLigne.
-- ============================================================================
if type(UIDropDownMenu_AddButton) == "function" then
    hooksecurefunc("UIDropDownMenu_AddButton", MESURER("MenuDeroulant", function(info, niveau)
        if Coupee() or not Actif() then return end
        niveau = niveau or UIDROPDOWNMENU_MENU_LEVEL or 1
        local liste = _G["DropDownList" .. niveau]
        local n = liste and liste.numButtons
        if not n then return end
        local bouton = _G["DropDownList" .. niveau .. "Button" .. n]
        if not bouton or AFR.EstProtege(bouton) then return end
        local texte = bouton.GetText and bouton:GetText()
        if not texte or texte == "" then return end
        local ok, fr = pcall(FrancaisLigne, texte)
        if ok and fr and fr ~= texte then
            bouton:SetText(fr)
        end
    end))
end
