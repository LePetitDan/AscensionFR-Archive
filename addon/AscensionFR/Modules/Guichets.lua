-- ============================================================================
-- AscensionFR - Guichets (bloc H, 29/07/2026)
-- Le courrier, le panneau de réputation, la liste des monnaies et le
-- calendrier des fêtes. Ces quatre guichets n'avaient AUCUN module : leur
-- matière existait (DB_Guichets : MailTemplate.dbc, Faction.dbc, fêtes ;
-- les monnaies tirent leur nom des OBJETS, déjà au pont DB_ObjetsNoms)
-- mais aucune surface ne la posait.
--
-- MÉTHODE SÛRE, comme partout depuis la 1.7.5 : on laisse les globales du
-- client tranquilles et on REPEINT le texte APRÈS que le client l'a
-- affiché (hooksecurefunc sur ses fonctions de peinture). Aucun de ces
-- cadres n'est protégé ; aucune globale n'est écrite ; un texte inconnu
-- reste intact.
-- ============================================================================
local AFR = AscensionFR

-- Repeint une FontString si le pont connaît son texte. `pont` est une
-- table [EN] = FR (Guichets ou ObjetsNoms — les deux se consultent par
-- indexation directe, le paresseux compile son seau au premier accès).
local function Poser(fs, pont)
    if not fs or not fs.GetText or not AFR.Actif() then return end
    local texte = fs:GetText()
    if type(texte) ~= "string" or texte == "" then return end
    local fr = pont[texte]
    if type(fr) == "string" and fr ~= "" and fr ~= texte then
        fs:SetText(fr)
    end
end

-- ----------------------------------------------------------------------------
-- 1. LE COURRIER. Boîte de réception : sujets + expéditeurs (le pont des
--    créatures traduit les PNJ expéditeurs). Lettre ouverte : sujet + corps
--    (les 170+ modèles de MailTemplate.dbc se comparent au texte EXACT).
-- ----------------------------------------------------------------------------
if type(InboxFrame_Update) == "function" then
    hooksecurefunc("InboxFrame_Update", function()
        if not AFR.Actif() then return end
        for i = 1, 12 do
            Poser(_G["MailItem" .. i .. "Subject"], AFR.DB.Guichets)
            local expediteur = _G["MailItem" .. i .. "Sender"]
            if expediteur and expediteur.GetText then
                local nom = expediteur:GetText()
                if type(nom) == "string" and nom ~= ""
                        and AFR.CreatureParNomEN then
                    local c = AFR.CreatureParNomEN(nom)
                    if c and c.N and c.N ~= nom then
                        expediteur:SetText(c.N)
                    end
                end
            end
        end
    end)
end

if type(OpenMail_Update) == "function" then
    hooksecurefunc("OpenMail_Update", function()
        if not AFR.Actif() then return end
        Poser(OpenMailSubject, AFR.DB.Guichets)
        Poser(OpenMailBodyText, AFR.DB.Guichets)
    end)
end

-- ----------------------------------------------------------------------------
-- 2. LA RÉPUTATION. Les 391 noms (et descriptions) de Faction.dbc.
-- ----------------------------------------------------------------------------
if type(ReputationFrame_Update) == "function" then
    hooksecurefunc("ReputationFrame_Update", function()
        if not AFR.Actif() then return end
        for i = 1, (NUM_FACTIONS_DISPLAYED or 15) do
            Poser(_G["ReputationBar" .. i .. "FactionName"],
                  AFR.DB.Guichets)
        end
        Poser(ReputationDetailFactionName, AFR.DB.Guichets)
        Poser(ReputationDetailFactionDescription, AFR.DB.Guichets)
    end)
end

-- ----------------------------------------------------------------------------
-- 3. LES MONNAIES. CurrencyTypes.dbc n'a AUCUN texte (audit du 25/07) :
--    les noms viennent des objets — le pont DB_ObjetsNoms les connaît déjà.
-- ----------------------------------------------------------------------------
if type(TokenFrame_Update) == "function" then
    hooksecurefunc("TokenFrame_Update", function()
        if not AFR.Actif() then return end
        for i = 1, 24 do
            local bouton = _G["TokenFrameContainerButton" .. i]
            if bouton then
                Poser(_G["TokenFrameContainerButton" .. i .. "Name"]
                      or bouton.name, AFR.DB.ObjetsNoms)
            end
        end
    end)
end

-- ----------------------------------------------------------------------------
-- 4. LES FÊTES. Blizzard_Calendar se charge À LA DEMANDE : on s'accroche
--    quand il arrive. Les pastilles des jours portent le nom de la fête
--    (DB_Guichets le connaît par texte).
--
--    MAIS la grille affiche des noms COMPOSÉS — « Darkmoon Faire Begins »,
--    « … Ends » — qui ne sont dans aucune table (test de Dan, 29/07/2026).
--    Ils ne sont pas à traduire : ils sont FABRIQUÉS par le client à partir
--    d'un gabarit, exactement comme les messages système de quêtes. On
--    reprend donc la méthode qui marche déjà là-bas : le gabarit ANGLAIS du
--    client devient un motif, on en extrait le nom de la fête, on le traduit
--    par le pont, et on recompose avec le gabarit FRANÇAIS OFFICIEL.
--    Le français y gagne sa vraie ponctuation — « Foire de Sombrelune :
--    début » et non un « commence » inventé — et la règle vaut pour les
--    fêtes futures sans qu'on ajoute la moindre entrée.
-- ----------------------------------------------------------------------------
local GABARITS_FETE = {
    "CALENDAR_EVENTNAME_FORMAT_START",
    "CALENDAR_EVENTNAME_FORMAT_END",
    "CALENDAR_EVENTNAME_FORMAT_ONGOING",
}
local reglesFete

local function EnMotif(gabarit)
    local motif = string.gsub(gabarit,
        "([%^%$%(%)%%%.%[%]%*%+%-%?])", "%%%1")
    motif = string.gsub(motif, "%%%%s", function() return "(.+)" end)
    return "^" .. motif .. "$"
end

local function ConstruireReglesFete()
    reglesFete = {}
    for _, cle in ipairs(GABARITS_FETE) do
        local en = _G[cle]
        local fr = AFR.DB.UI and AFR.DB.UI[cle]
        if type(en) == "string" and en ~= "" and type(fr) == "string"
            and fr ~= "" and en ~= fr and string.find(en, "%%s") then
            table.insert(reglesFete, { motif = EnMotif(en), fr = fr })
        end
    end
end

-- Rend le texte composé traduit, ou nil si ce n'en est pas un.
local function FeteComposee(texte)
    -- Une liste VIDE compte comme « pas encore construite » : les
    -- gabarits arrivent avec Blizzard_Calendar, chargé à la demande, et
    -- DB.UI avec l'addon. Bâtir une fois pour toutes au premier appel
    -- gelait un jeu de règles vide pour la session entière — défaut
    -- trouvé par le banc, pas en jeu.
    if not reglesFete or #reglesFete == 0 then ConstruireReglesFete() end
    for _, r in ipairs(reglesFete) do
        local nom = string.match(texte, r.motif)
        if nom then
            local nom_fr = AFR.DB.Guichets[nom]
            if type(nom_fr) == "string" and nom_fr ~= "" then
                return string.format(r.fr, nom_fr)
            end
            return nil          -- fête inconnue : on n'invente rien
        end
    end
end
AFR.FeteComposee = FeteComposee

local function RepeindreCalendrier()
    if not AFR.Actif() then return end
    for jour = 1, 42 do
        for evenement = 1, 4 do
            local zone = _G["CalendarDayButton" .. jour .. "EventButton"
                            .. evenement .. "Text"]
            Poser(zone, AFR.DB.Guichets)
            -- puis les composés, que le pont ne peut pas connaître
            if zone and zone.GetText then
                local texte = zone:GetText()
                if type(texte) == "string" and texte ~= "" then
                    local fr = FeteComposee(texte)
                    if fr and fr ~= texte then zone:SetText(fr) end
                end
            end
        end
    end
end

local function AccrocherCalendrier()
    if type(CalendarFrame_Update) == "function" then
        hooksecurefunc("CalendarFrame_Update", RepeindreCalendrier)
        return true
    end
end

if not AccrocherCalendrier() then
    local guet = CreateFrame("Frame")
    guet:RegisterEvent("ADDON_LOADED")
    guet:SetScript("OnEvent", function(self, _, nom)
        if nom == "Blizzard_Calendar" and AccrocherCalendrier() then
            self:UnregisterEvent("ADDON_LOADED")
        end
    end)
end
