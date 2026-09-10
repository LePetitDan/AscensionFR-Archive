-- ============================================================================
-- AscensionFR - Bouton de minimap
-- Un bouton rond au bord de la minimap : l'état d'un coup d'œil (survol),
-- le panneau d'options en un clic. Se déplace en le faisant glisser le long
-- du cadran ; se cache depuis le panneau. Aucune bibliothèque externe :
-- en 3.3.5, une quarantaine de lignes suffisent.
-- ============================================================================
local AFR = AscensionFR

local RAYON = 80          -- distance au centre de la minimap
local ANGLE_DEFAUT = 215  -- degrés : en bas à gauche, zone en général libre

local bouton = CreateFrame("Button", "AscensionFRMinimapBouton", Minimap)
bouton:SetSize(31, 31)
bouton:SetFrameStrata("MEDIUM")
bouton:SetFrameLevel(8)
bouton:RegisterForClicks("LeftButtonUp", "RightButtonUp")
bouton:RegisterForDrag("LeftButton")
bouton:SetHighlightTexture("Interface\\Minimap\\UI-Minimap-ZoomButton-Highlight")

-- L'anneau doré standard des boutons de minimap, notre icône dedans.
local cerclage = bouton:CreateTexture(nil, "OVERLAY")
cerclage:SetSize(53, 53)
cerclage:SetTexture("Interface\\Minimap\\MiniMap-TrackingBorder")
cerclage:SetPoint("TOPLEFT")

local icone = bouton:CreateTexture(nil, "BACKGROUND")
icone:SetSize(20, 20)
icone:SetTexture("Interface\\Icons\\INV_Misc_Book_09")
icone:SetTexCoord(0.05, 0.95, 0.05, 0.95)
icone:SetPoint("TOPLEFT", 7, -5)

local function Options()
    AscensionFRSaved = AscensionFRSaved or {}
    AscensionFRSaved.Options = AscensionFRSaved.Options or {}
    return AscensionFRSaved.Options
end

local function Placer()
    local angle = math.rad(Options().minimapAngle or ANGLE_DEFAUT)
    bouton:ClearAllPoints()
    bouton:SetPoint("CENTER", Minimap, "CENTER",
        RAYON * math.cos(angle), RAYON * math.sin(angle))
end

-- Appelé par le panneau d'options (case « Bouton près de la minimap »).
function AFR.MinimapVisible(visible)
    Options().minimapCache = not visible or nil
    if visible then bouton:Show() else bouton:Hide() end
end

-- Glisser : l'angle suit le curseur autour du centre de la minimap.
bouton:SetScript("OnDragStart", function(self)
    self:SetScript("OnUpdate", function(self)
        local mx, my = Minimap:GetCenter()
        local echelle = Minimap:GetEffectiveScale()
        local cx, cy = GetCursorPosition()
        Options().minimapAngle = math.deg(
            math.atan2(cy / echelle - my, cx / echelle - mx))
        Placer()
    end)
end)
bouton:SetScript("OnDragStop", function(self)
    self:SetScript("OnUpdate", nil)
end)

-- ----------------------------------------------------------------------------
-- Confirmation avant de COUPER (bloc C, 29/07/2026). Le clic droit basculait
-- en silence : c'était le suspect n° 1 des joueurs qui « retombent en
-- anglais » sans comprendre pourquoi. Désormais une petite question s'ouvre
-- AVANT de couper ; RÉTABLIR, le sens sans danger, reste direct. Fenêtre
-- maison (aucun nom global, aucun cadre protégé, affichage pur) — pas
-- StaticPopup, pour ne rien écrire dans les tables du client.
-- ----------------------------------------------------------------------------
local confirmation = CreateFrame("Frame", nil, UIParent)
confirmation:SetSize(300, 110)
confirmation:SetPoint("CENTER", 0, 120)
confirmation:SetFrameStrata("DIALOG")
confirmation:SetBackdrop({
    bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
    edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
    tile = true, tileSize = 32, edgeSize = 32,
    insets = { left = 11, right = 12, top = 12, bottom = 11 },
})
confirmation:EnableMouse(true)   -- avale les clics sous la fenêtre
confirmation:Hide()

local question = confirmation:CreateFontString(nil, "ARTWORK",
    "GameFontHighlight")
question:SetPoint("TOP", 0, -22)
question:SetText("Couper la traduction ?")

local detail = confirmation:CreateFontString(nil, "ARTWORK",
    "GameFontDisableSmall")
detail:SetPoint("TOP", question, "BOTTOM", 0, -4)
detail:SetText("Tout repassera en anglais (un /reload complète).")

local boutonCouper = CreateFrame("Button", nil, confirmation,
    "UIPanelButtonTemplate")
boutonCouper:SetSize(110, 22)
boutonCouper:SetPoint("BOTTOMRIGHT", confirmation, "BOTTOM", -6, 18)
boutonCouper:SetText("Couper")
boutonCouper:SetScript("OnClick", function()
    confirmation:Hide()
    Options().desactive = true
    print("|cff0099ffAscensionFR|r : traduction désactivée "
        .. "(/reload pour tout rétablir en anglais).")
end)

local boutonGarder = CreateFrame("Button", nil, confirmation,
    "UIPanelButtonTemplate")
boutonGarder:SetSize(110, 22)
boutonGarder:SetPoint("BOTTOMLEFT", confirmation, "BOTTOM", 6, 18)
boutonGarder:SetText("Garder")
boutonGarder:SetScript("OnClick", function() confirmation:Hide() end)

bouton:SetScript("OnClick", function(self, clic)
    if clic == "RightButton" then
        local opt = Options()
        if opt.desactive then
            -- Rétablir : le sens sans danger, pas de question.
            opt.desactive = nil
            confirmation:Hide()
            print("|cff0099ffAscensionFR|r : traduction activée "
                .. "(/reload conseillé).")
        else
            confirmation:Show()
        end
    elseif AFR.OuvrirOptions then
        AFR.OuvrirOptions()
    end
end)

bouton:SetScript("OnEnter", function(self)
    GameTooltip:SetOwner(self, "ANCHOR_LEFT")
    GameTooltip:AddLine("Ascension |cff0099ffFR|r")
    -- Total exact et sûr (AFR.TotalTraductions, partagé). L'ancien pairs(AFR.DB)
    -- maison plantait depuis que le total gravé est un nombre dans... la racine
    -- (24/07). On garde un repli minimal, avec le garde type()=="table".
    local total
    if type(AFR.TotalTraductions) == "function" then
        total = AFR.TotalTraductions()
    else
        total = 0
        for _, t in pairs(AFR.DB) do
            if type(t) == "table" then
                for _ in pairs(t) do total = total + 1 end
            end
        end
    end
    GameTooltip:AddLine(string.format("%d traductions chargées", total),
        1, 0.82, 0)
    local attente = type(NombreRecoltes) == "function" and NombreRecoltes() or 0
    local signales = AFR.NombreSignalements and AFR.NombreSignalements() or 0
    if attente + signales > 0 then
        GameTooltip:AddLine(string.format(
            "%d texte(s) et %d signalement(s) à transmettre — /reload",
            attente, signales), 1, 0.5, 0)
    else
        GameTooltip:AddLine("Rien en attente", 0.6, 0.6, 0.6)
    end
    GameTooltip:AddLine(" ")
    GameTooltip:AddLine("Clic gauche : options", 0.8, 0.8, 0.8)
    GameTooltip:AddLine("Clic droit : couper/rétablir la traduction",
        0.8, 0.8, 0.8)
    GameTooltip:AddLine("Glisser : déplacer le bouton", 0.8, 0.8, 0.8)
    GameTooltip:Show()
end)
bouton:SetScript("OnLeave", function() GameTooltip:Hide() end)

-- Les SavedVariables n'existent qu'après le chargement de l'addon : position
-- et visibilité définitives à ce moment-là.
local init = CreateFrame("Frame")
init:RegisterEvent("PLAYER_LOGIN")
init:SetScript("OnEvent", function()
    Placer()
    if Options().minimapCache then bouton:Hide() end
end)
Placer()
