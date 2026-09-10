-- ============================================================================
-- AscensionFR - Canal français
--
-- Idée de Dan (24/07/2026) : beaucoup parlent anglais sur le serveur. Si tous
-- ceux qui ont l'addon rejoignent AUTOMATIQUEMENT le même canal, ils sont sûrs
-- d'y trouver des francophones — à l'échelle du serveur entier.
--
-- On fait exactement ce que fait la commande /join du jeu
-- (JoinPermanentChannel, ChatFrame.lua:1882) : aucune fonction protégée, donc
-- aucun risque de taint. Le canal est un canal WoW standard.
--
-- Coupe-circuit : AscensionFRSaved.Options.sansCanalFrancais (case dans les
-- options, ou /afrcanal off). Par défaut ACTIVÉ : c'est tout l'intérêt que
-- tout le monde s'y retrouve, mais chacun peut se retirer.
-- ============================================================================
local AFR = AscensionFR

-- Nom du canal : « AscensionFR » (choix de Dan). Volontairement SANS accent —
-- un nom de canal accentué (« Français ») pouvait être refusé par le client
-- 3.3.5 et faire échouer la jonction en silence. « AscensionFR » est en ASCII,
-- donc toujours valide, et il identifie clairement le salon des porteurs de
-- l'addon. Chacun peut aussi le rejoindre à la main : /join AscensionFR.
local NOM_CANAL = "AscensionFR"

local function Options()
    return AscensionFRSaved and AscensionFRSaved.Options
end

-- Déclarées en avance : Rejoindre (défini plus haut) veut colorer le canal
-- juste après la jonction, mais ColorerCanal vit plus bas.
local ColorerCanal

local function Coupe()
    local o = Options()
    return o and o.sansCanalFrancais
end

-- Déjà dans le canal ? GetChannelName rend 0 si absent, un index > 0 sinon.
-- pcall : sur certaines versions GetChannelName n'aime pas un nom accentué.
local function DejaDedans()
    if type(GetChannelName) ~= "function" then return false end
    local ok, id = pcall(GetChannelName, NOM_CANAL)
    return ok and type(id) == "number" and id > 0
end

-- verbeux = on explique le résultat (appelé par /afrcanal on, pour diagnostic).
local function Rejoindre(verbeux)
    if Coupe() then
        if verbeux then
            print("|cff0099ffAscensionFR|r : le canal est désactivé "
                .. "(/afrcanal on pour le réactiver).")
        end
        return
    end
    if DejaDedans() then
        if verbeux then
            print("|cff0099ffAscensionFR|r : tu es déjà dans le canal "
                .. NOM_CANAL .. ".")
        end
        return
    end
    if type(JoinPermanentChannel) ~= "function" then
        if verbeux then
            print("|cffff0000AscensionFR|r : JoinPermanentChannel absent "
                .. "sur ce client — signale-le.")
        end
        return
    end
    -- Même appel que le /join du client, mais mot de passe = "" (pas nil) et
    -- SANS demander la voix : (nom, mdp, cadre de chat).
    local cadre = DEFAULT_CHAT_FRAME or ChatFrame1
    local id = cadre and cadre.GetID and cadre:GetID() or 1
    pcall(JoinPermanentChannel, NOM_CANAL, "", id)
    if type(ChatFrame_AddChannel) == "function" and cadre then
        pcall(ChatFrame_AddChannel, cadre, NOM_CANAL)
    end
    -- A-t-on VRAIMENT rejoint ? (retour honnête, surtout en verbeux)
    if DejaDedans() then
        if ColorerCanal then ColorerCanal() end     -- couleur du canal (2)
        if not (AscensionFRSaved and AscensionFRSaved.CanalFrPresente) then
            if AscensionFRSaved then
                AscensionFRSaved.CanalFrPresente = true
            end
            print("|cff0099ffAscensionFR|r : tu es dans le canal "
                .. "|cffffff00" .. NOM_CANAL .. "|r — un salon pour retrouver "
                .. "les francophones du serveur. Le quitter : "
                .. "|cffffff00/afrcanal off|r.")
        elseif verbeux then
            print("|cff0099ffAscensionFR|r : canal " .. NOM_CANAL
                .. " rejoint.")
        end
    elseif verbeux then
        -- On a essayé mais on n'y est pas : le plus souvent le système de
        -- canaux n'est pas encore prêt juste après la connexion.
        print("|cffff9900AscensionFR|r : impossible de rejoindre "
            .. NOM_CANAL .. " pour l'instant. Réessaie dans quelques "
            .. "secondes (/afrcanal on), ou à la main : |cffffff00/join "
            .. NOM_CANAL .. "|r.")
    end
end

local function Quitter()
    if type(LeaveChannelByName) == "function" then
        pcall(LeaveChannelByName, NOM_CANAL)
    end
end

-- Index du canal (1..10) ou 0 si absent.
local function IndexCanal()
    if type(GetChannelName) ~= "function" then return 0 end
    local ok, id = pcall(GetChannelName, NOM_CANAL)
    return (ok and type(id) == "number") and id or 0
end

-- ============================================================================
-- 2. COULEUR DU CANAL — le « [N. AscensionFR] » se distingue d'un coup d'œil.
-- ============================================================================
local R_CANAL, V_CANAL, B_CANAL = 0.40, 0.80, 1.00   -- bleu clair
function ColorerCanal()                 -- remplit la déclaration d'en haut
    local idx = IndexCanal()
    if idx > 0 and type(ChangeChatColor) == "function" then
        pcall(ChangeChatColor, "CHANNEL" .. idx, R_CANAL, V_CANAL, B_CANAL)
    end
end

-- ============================================================================
-- PSEUDOS COLORÉS (demande de Dan) — MON nom ressort, les autres francophones
-- ont leur couleur commune. La coloration du chat est CÔTÉ CLIENT : chacun
-- voit SON propre nom en surbrillance, et toute la communauté colorée.
--
-- Technique standard : un filtre sur CHAT_MSG_CHANNEL qui réécrit le nom de
-- l'auteur avec un code couleur. On ne touche QUE notre canal.
-- ============================================================================
local COUL_MOI = "|cffff5555"     -- rouge clair : MOI
local COUL_COMU = "|cff66ccff"    -- bleu clair : les autres francophones

-- On enveloppe GetColoredName — le NOM AFFICHÉ dans « [Nom] » — et PAS
-- l'argument auteur. Colorer l'auteur mettait les codes couleur DANS le lien
-- |Hplayer:...| et le lien s'affichait en texte brut (bug vu par Dan le
-- 24/07). GetColoredName ne sert qu'à l'affichage : le lien reste intact,
-- cliquable, et le nom se colore proprement. Tout est protégé : au moindre
-- souci on rend le nom d'origine, donc le chat ne peut pas casser.
local Ancien_GetColoredName = GetColoredName
if type(Ancien_GetColoredName) == "function" then
    -- Signature du jeu : GetColoredName(event, arg1, arg2, ... argN). Pour
    -- CHAT_MSG_CHANNEL : arg2 = auteur, arg9 = nom de base du canal.
    GetColoredName = function(event, ...)
        local nom = Ancien_GetColoredName(event, ...)
        if event ~= "CHAT_MSG_CHANNEL" or type(nom) ~= "string" then
            return nom
        end
        local ok, colore = pcall(function(...)
            local a = { ... }
            if a[9] ~= NOM_CANAL then return nil end
            local moi = UnitName and UnitName("player")
            local couleur = (moi and a[2] == moi) and COUL_MOI or COUL_COMU
            return couleur .. nom .. "|r"
        end, ...)
        if ok and colore then return colore end
        return nom
    end
end

-- ============================================================================
-- 4. COMPTEUR DE FRANCOPHONES EN LIGNE (via la liste du canal).
-- ============================================================================
local function CompterFrancophones()
    local idx = IndexCanal()
    if idx == 0 then return nil end
    -- Plusieurs API selon le client ; on essaie, on se rabat sinon.
    for _, nomFn in ipairs({ "GetNumChannelMembers", "GetChannelNumMembers" }) do
        local fn = _G[nomFn]
        if type(fn) == "function" then
            local ok, n = pcall(fn, idx)
            if ok and type(n) == "number" and n > 0 then return n end
        end
    end
    -- Repli : on compte la liste de la fenêtre du canal si elle existe.
    if type(GetChannelRosterInfo) == "function" then
        local n = 0
        for i = 1, 500 do
            local ok, nom = pcall(GetChannelRosterInfo, idx, i)
            if not ok or not nom then break end
            n = n + 1
        end
        if n > 0 then return n end
    end
    return nil
end

-- ============================================================================
-- 5. RECHERCHE DE GROUPE FR — poste un message formaté dans le canal.
-- ============================================================================
local function PosterGroupe(texte)
    texte = string.gsub(texte or "", "^%s*(.-)%s*$", "%1")
    if texte == "" then
        print("|cff0099ffAscensionFR|r : |cffffff00/afrgroupe <ton "
            .. "message>|r — ex. « /afrgroupe cherche 2 dps pour donjon ».")
        return
    end
    local idx = IndexCanal()
    if idx == 0 then
        print("|cffff9900AscensionFR|r : rejoins d'abord le canal "
            .. "(/afrcanal on).")
        return
    end
    if type(SendChatMessage) == "function" then
        pcall(SendChatMessage, "[Groupe] " .. texte, "CHANNEL", nil, idx)
    end
end

-- ============================================================================
-- 1. ONGLET DE CHAT DÉDIÉ — sur demande (/afrcanal onglet). Pas automatique :
-- créer un onglet à chaque connexion en empilerait des doublons.
-- ============================================================================
local function CreerOnglet()
    if type(FCF_OpenNewWindow) ~= "function" then
        print("|cffff9900AscensionFR|r : onglets de chat indisponibles sur "
            .. "ce client.")
        return
    end
    -- Déjà créé ? On cherche une fenêtre nommée comme le canal.
    for i = 1, (NUM_CHAT_WINDOWS or 10) do
        local nom = pcall(GetChatWindowInfo, i) and GetChatWindowInfo(i)
        if nom == NOM_CANAL then
            print("|cff0099ffAscensionFR|r : l'onglet " .. NOM_CANAL
                .. " existe déjà.")
            return
        end
    end
    local ok, cadre = pcall(FCF_OpenNewWindow, NOM_CANAL)
    local cible = (type(cadre) == "table" and cadre) or _G["ChatFrame" ..
        ((FCF_GetCurrentChatFrame and FCF_GetCurrentChatFrame()) and
         FCF_GetCurrentChatFrame():GetID() or 1)]
    if ok and cible and type(ChatFrame_AddChannel) == "function" then
        pcall(ChatFrame_AddChannel, cible, NOM_CANAL)
        -- On retire le canal du chat général pour qu'il ne s'affiche QUE dans
        -- l'onglet dédié.
        if type(ChatFrame_RemoveChannel) == "function" then
            pcall(ChatFrame_RemoveChannel, DEFAULT_CHAT_FRAME, NOM_CANAL)
        end
        print("|cff0099ffAscensionFR|r : onglet " .. NOM_CANAL .. " créé.")
    end
end

-- ----------------------------------------------------------------------------
-- Rejoint APRÈS l'entrée en jeu, avec un délai : le système de canaux n'est
-- pas prêt à la première image, un JoinPermanentChannel trop tôt échoue en
-- silence. On attend quelques secondes, une seule fois.
-- ----------------------------------------------------------------------------
local minuteur = CreateFrame("Frame")
if AFR.Perf then AFR.Perf.Suivre("CanalFrancais", minuteur) end
local depuis = 0
local function Tic(self, ecoule)
    depuis = depuis + (ecoule or 0)
    if depuis < 6 then return end
    self:SetScript("OnUpdate", nil)   -- une seule tentative par armement
    Rejoindre()
end

local cadreEvt = CreateFrame("Frame")
cadreEvt:RegisterEvent("PLAYER_ENTERING_WORLD")
cadreEvt:SetScript("OnEvent", function()
    -- Réarme le minuteur à chaque entrée en jeu (téléport, reload) : si on
    -- s'est fait éjecter du canal entre-temps, on y retourne. DejaDedans
    -- évite le doublon.
    depuis = 0
    minuteur:SetScript("OnUpdate", Tic)
end)

-- ----------------------------------------------------------------------------
-- Commande manuelle. AFR.CanalFrancais.* est exposé pour la case d'options.
-- ----------------------------------------------------------------------------
AFR.CanalFrancais = {
    nom = NOM_CANAL,
    rejoindre = Rejoindre,
    quitter = Quitter,
    dedans = DejaDedans,
    compter = CompterFrancophones,
    onglet = CreerOnglet,
    groupe = PosterGroupe,
}

SLASH_AFRCANAL1 = "/afrcanal"
SlashCmdList["AFRCANAL"] = function(arg)
    arg = string.lower(string.gsub(arg or "", "^%s*(.-)%s*$", "%1"))
    local o = Options()
    if arg == "off" then
        if o then o.sansCanalFrancais = true end
        Quitter()
        print("|cff0099ffAscensionFR|r : canal " .. NOM_CANAL
            .. " quitté. |cffffff00/afrcanal on|r pour y revenir.")
    elseif arg == "on" then
        if o then o.sansCanalFrancais = nil end
        Rejoindre(true)          -- verbeux : dit ce qui se passe
    elseif arg == "onglet" then
        CreerOnglet()
    elseif arg == "qui" then
        local n = CompterFrancophones()
        if n then
            print("|cff0099ffAscensionFR|r : |cffffff00" .. n
                .. "|r francophone(s) dans le canal en ce moment.")
        else
            print("|cff0099ffAscensionFR|r : impossible de compter sur ce "
                .. "client (essaie d'ouvrir la fenêtre du canal une fois).")
        end
    else
        print("|cff0099ffAscensionFR|r : canal " .. NOM_CANAL
            .. " — |cffffff00/afrcanal on|off|r (rejoindre/quitter), "
            .. "|cffffff00qui|r (qui est là), |cffffff00onglet|r (onglet "
            .. "dédié). Groupe : |cffffff00/afrgroupe <message>|r.")
    end
end

SLASH_AFRGROUPE1 = "/afrgroupe"
SlashCmdList["AFRGROUPE"] = function(arg)
    PosterGroupe(arg)
end
