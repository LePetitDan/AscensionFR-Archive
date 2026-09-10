-- ============================================================================
-- AscensionFR - Signalements
-- « /afr signaler » (ou une touche, Échap -> Raccourcis clavier) pendant
-- qu'une info-bulle fautive est affichée : l'addon photographie son contenu
-- dans les SavedVariables. Au /reload suivant, le compagnon la diagnostique
-- tout seul (absent des bases ? échec d'alignement ? chaîne du client ?) et
-- écrit son verdict dans traduction\traductions\rapport_signalements.txt.
-- Une capture d'écran devient une touche.
-- ============================================================================
local AFR = AscensionFR

-- Libellés du raccourci clavier (voir Bindings.xml)
BINDING_HEADER_ASCENSIONFR = "Ascension FR"
BINDING_NAME_ASCENSIONFR_SIGNALER = "Signaler le texte survolé"

local MAX_SIGNALEMENTS = 100   -- protège les SavedVariables
local MAX_ECHECS = 200

local function Liste()
    AscensionFRSaved = AscensionFRSaved or {}
    AscensionFRSaved.Signalements = AscensionFRSaved.Signalements or {}
    return AscensionFRSaved.Signalements
end

function AFR.NombreSignalements()
    local l = AscensionFRSaved and AscensionFRSaved.Signalements
    return l and #l or 0
end

local function InfobulleVisible()
    if GameTooltip:IsShown() and GameTooltip:NumLines() > 0 then
        return GameTooltip
    end
    if ItemRefTooltip and ItemRefTooltip:IsShown()
        and ItemRefTooltip:NumLines() > 0 then
        return ItemRefTooltip
    end
end

-- Photographie du cadre sous la souris : chaîne des parents (nom +
-- protection), textes visibles, état du module métiers. C'est l'outil
-- d'enquête pour les fenêtres réécrites par Ascension (vécu : la cuisine,
-- restée anglaise sans que la récolte ne voie rien passer).
local function DecrireCadre()
    if type(GetMouseFocus) ~= "function" then return nil end
    local cadre = GetMouseFocus()
    if not cadre or cadre == WorldFrame then return nil end
    local lignes = {}
    local chaine, c = {}, cadre
    for _ = 1, 8 do
        if not c then break end
        local nom = (c.GetName and c:GetName()) or "(anonyme)"
        if AFR.EstProtege(c) then nom = nom .. " (protégé)" end
        table.insert(chaine, nom)
        c = c.GetParent and c:GetParent()
    end
    table.insert(lignes, "cadre : " .. table.concat(chaine, " < "))
    if cadre.GetRegions then
        for _, r in ipairs({ cadre:GetRegions() }) do
            if r.GetObjectType and r:GetObjectType() == "FontString"
                and r.GetText and r:GetText() and r:GetText() ~= "" then
                table.insert(lignes, "texte : " .. r:GetText())
            end
        end
    end
    table.insert(lignes, "TradeSkillFrame : "
        .. (TradeSkillFrame
            and (TradeSkillFrame:IsShown() and "visible" or "caché")
            or "absent"))
    table.insert(lignes, "GetNumTradeSkills : "
        .. (type(GetNumTradeSkills) == "function"
            and tostring(GetNumTradeSkills() or 0) or "absent"))
    return lignes
end

-- Deux signalements décrivent le même problème s'ils portent sur le même
-- élément : inutile d'encombrer la file.
local function Signature(s)
    return (s.T or "?") .. ":"
        .. tostring(s.ID or (s.L and s.L[1]) or s.N or "")
end

function AFR.Signaler(note)
    local liste = Liste()
    local s = { Q = date("%d/%m/%y %H:%M") }
    if note and strtrim(note) ~= "" then
        s.T, s.N = "note", strtrim(note)
    else
        local tip = InfobulleVisible()
        if tip then
            -- Photographie complète : toutes les lignes, gauche et droite.
            s.L, s.R = {}, {}
            local nomTip = tip:GetName()
            for i = 1, tip:NumLines() do
                local g = _G[nomTip .. "TextLeft" .. i]
                local d = _G[nomTip .. "TextRight" .. i]
                s.L[i] = g and g:GetText() or ""
                s.R[i] = d and d:GetText() or ""
            end
            -- De quoi parle l'info-bulle ? L'ID vaut mieux que le texte.
            if tip.GetItem then
                local _, lien = tip:GetItem()
                local id = AFR.IdDepuisLienObjet(lien)
                if id then s.T, s.ID = "objet", id end
            end
            if not s.T and tip.GetSpell then
                local _, _, id = tip:GetSpell()
                if id then s.T, s.ID = "sort", id end
            end
            if not s.T and tip.GetUnit then
                local _, unite = tip:GetUnit()
                local guid = unite and UnitGUID(unite)
                local id = guid and AFR.IdCreatureDepuisGUID(guid)
                if id then s.T, s.ID = "pnj", id end
            end
            s.T = s.T or "texte"
        else
            -- Pas d'info-bulle : photographie du cadre sous la souris.
            s.L = DecrireCadre()
            if not s.L then
                print("|cff0099ffAscensionFR|r : survolez l'élément fautif "
                    .. "puis utilisez la touche ou /afr signaler. Sans rien "
                    .. "sous la souris : /afr signaler votre remarque.")
                return
            end
            s.T = "cadre"
        end
    end
    local signature = Signature(s)
    for _, existant in ipairs(liste) do
        if Signature(existant) == signature then
            print("|cff0099ffAscensionFR|r : déjà signalé — le compagnon "
                .. "s'en occupera au prochain /reload.")
            return
        end
    end
    if #liste >= MAX_SIGNALEMENTS then
        print("|cff0099ffAscensionFR|r : la file des signalements est "
            .. "pleine ; faites un /reload pour la transmettre au compagnon.")
        return
    end
    table.insert(liste, s)
    if s.T == "cadre" then
        print(string.format(
            "|cff0099ffAscensionFR|r : fenêtre photographiée (%d en "
            .. "attente). Le compagnon l'analysera au prochain /reload.",
            #liste))
    else
        print(string.format(
            "|cff0099ffAscensionFR|r : signalé (%d en attente). Le compagnon "
            .. "diagnostiquera au prochain /reload.", #liste))
    end
end

-- ----------------------------------------------------------------------------
-- Journal des échecs d'alignement
-- Quand un texte connu des bases refuse de se traduire (modèle non aligné),
-- on note l'ID et le texte affiché : le compagnon verra les ratés
-- systématiques sans attendre qu'un joueur les remarque. Silencieux, borné,
-- dédoublonné par ID — un filet, pas un espion.
-- genre : "S" (description de sort) ou "O" (ligne d'effet d'objet)
-- ----------------------------------------------------------------------------
-- texte : une chaîne, ou une table de lignes — les descriptions contiennent
-- elles-mêmes des sauts de ligne, les joindre perdrait la structure et
-- fausserait le rejeu hors-jeu (vécu sur le Libram : bloc @ext replié).
function AFR.JournaliserEchec(genre, id, texte)
    if not id or not texte or texte == "" then return end
    AscensionFRSaved = AscensionFRSaved or {}
    local j = AscensionFRSaved.EchecsAlignement or {}
    AscensionFRSaved.EchecsAlignement = j
    j[genre] = j[genre] or {}
    if j[genre][id] ~= nil then return end
    local n = 0
    for _ in pairs(j[genre]) do n = n + 1 end
    if n >= MAX_ECHECS then return end
    if type(texte) == "table" then
        local copie = {}
        for i = 1, math.min(#texte, 12) do
            copie[i] = string.sub(texte[i], 1, 600)
        end
        j[genre][id] = copie
    else
        j[genre][id] = string.sub(texte, 1, 600)
    end
end

-- Un échec journalisé qui se remet à traduire (bases enrichies, addon
-- corrigé...) s'efface : le journal se soigne tout seul.
function AFR.OublierEchec(genre, id)
    local j = AscensionFRSaved and AscensionFRSaved.EchecsAlignement
    if j and j[genre] then j[genre][id] = nil end
end

-- ============================================================================
-- Proposer une traduction — PAR FENÊTRE (pas par commande : beaucoup de
-- joueurs ne retiennent pas les commandes). Le joueur survole ce qui est mal
-- traduit, ouvre la fenêtre (raccourci ou /afr signaler), voit DE QUOI il
-- s'agit (objet / sort / PNJ / interface) et saisit sa traduction dans la
-- case « Traduction proposée ». Le Hub transmet ; l'usine range la proposition
-- pour arbitrage (le vocabulaire reste décidé côté projet).
-- ============================================================================

-- Traqueur du dernier élément survolé : au moment où l'on ouvre la fenêtre,
-- l'infobulle a souvent disparu — on garde donc en mémoire le dernier objet /
-- sort / PNJ dont l'infobulle s'est affichée.
-- Toutes les lignes GAUCHE d'une infobulle (nom, description, effets…) : le
-- joueur pourra désigner CELLE qui est fautive.
local function LignesInfobulle(tip)
    local lignes = {}
    local nomTip = tip:GetName()
    for i = 1, tip:NumLines() do
        local g = _G[nomTip .. "TextLeft" .. i]
        local t = g and g:GetText()
        if t and t ~= "" then table.insert(lignes, t) end
    end
    return lignes
end

local function NoterSurvol(cible, id, tip)
    if cible and id and tip then
        local lignes = LignesInfobulle(tip)
        AFR.DernierSurvol = { cible = cible, ID = id, lignes = lignes,
                              nom = lignes[1] or "", quand = GetTime() }
    end
end

if GameTooltip and GameTooltip.HookScript then
    GameTooltip:HookScript("OnTooltipSetItem", function(self)
        local _, lien = self:GetItem()
        NoterSurvol("objet", lien and AFR.IdDepuisLienObjet(lien), self)
    end)
    GameTooltip:HookScript("OnTooltipSetSpell", function(self)
        local _, _, id = self:GetSpell()
        NoterSurvol("sort", id, self)
    end)
    GameTooltip:HookScript("OnTooltipSetUnit", function(self)
        local _, unite = self:GetUnit()
        local guid = unite and UnitGUID(unite)
        NoterSurvol("pnj", guid and AFR.IdCreatureDepuisGUID(guid), self)
    end)
end

-- De quoi parle-t-on ? Infobulle affichée -> dernier survol récent -> cadre
-- sous la souris (élément d'interface).
local function ContexteSignalement()
    local tip = InfobulleVisible()
    if tip then
        local ctx = { lignes = LignesInfobulle(tip) }
        ctx.actuel = ctx.lignes[1] or ""
        if tip.GetItem then
            local _, lien = tip:GetItem()
            local id = lien and AFR.IdDepuisLienObjet(lien)
            if id then ctx.cible, ctx.ID = "objet", id end
        end
        if not ctx.cible and tip.GetSpell then
            local _, _, id = tip:GetSpell()
            if id then ctx.cible, ctx.ID = "sort", id end
        end
        if not ctx.cible and tip.GetUnit then
            local _, unite = tip:GetUnit()
            local guid = unite and UnitGUID(unite)
            local id = guid and AFR.IdCreatureDepuisGUID(guid)
            if id then ctx.cible, ctx.ID = "pnj", id end
        end
        if ctx.cible then return ctx end
        -- Infobulle affichée mais élément non identifiable (aura/débuff,
        -- effet, objet du monde…) : on garde quand même son TEXTE — bien
        -- mieux que le cadre nu sous la souris. Le joueur cliquera la ligne.
        if ctx.lignes[1] then
            ctx.cible = "texte"
            return ctx
        end
    end
    if AFR.DernierSurvol and (GetTime() - (AFR.DernierSurvol.quand or 0)) < 30 then
        local d = AFR.DernierSurvol
        return { cible = d.cible, ID = d.ID, actuel = d.nom,
                 lignes = d.lignes }
    end
    if type(GetMouseFocus) == "function" then
        local cadre = GetMouseFocus()
        if cadre and cadre ~= WorldFrame then
            local nomCadre = (cadre.GetName and cadre:GetName()) or "(élément)"
            local texte
            if cadre.GetText then texte = cadre:GetText() end
            if (not texte or texte == "") and cadre.GetRegions then
                for _, r in ipairs({ cadre:GetRegions() }) do
                    if r.GetObjectType and r:GetObjectType() == "FontString"
                        and r.GetText and r:GetText() and r:GetText() ~= "" then
                        texte = r:GetText()
                        break
                    end
                end
            end
            return { cible = "interface", actuel = texte or "",
                     nomCadre = nomCadre, lignes = { texte or "" } }
        end
    end
    return nil
end

-- Range la proposition (mêmes SavedVariables que les signalements).
local function EnregistrerProposition(ctx, propose, actuel)
    propose = strtrim(propose or "")
    if propose == "" then
        return false, "Écrivez d'abord votre traduction dans la case."
    end
    if not ctx then
        return false, "Aucun élément détecté : survolez-le puis rouvrez."
    end
    if not actuel or actuel == "" then
        return false, "Cliquez d'abord, à gauche, la ligne à corriger."
    end
    local s = { Q = date("%d/%m/%y %H:%M"), T = "proposition", P = propose,
                actuel = actuel }
    if ctx.cible and ctx.ID then
        s.cible, s.ID = ctx.cible, ctx.ID
    elseif ctx.cible then
        -- Sans identifiant (interface, aura/débuff, texte) : la clé sera le
        -- texte de la ligne choisie.
        s.cible, s.nomCadre = ctx.cible, ctx.nomCadre
    else
        return false, "Élément non identifié."
    end
    local liste = Liste()
    for _, e in ipairs(liste) do
        if e.T == "proposition" and e.cible == s.cible and e.ID == s.ID
            and e.nomCadre == s.nomCadre and e.P == s.P then
            return false, "Déjà proposé — merci !"
        end
    end
    if #liste >= MAX_SIGNALEMENTS then
        return false, "File pleine : faites un /reload pour l'envoyer."
    end
    table.insert(liste, s)
    return true, nil
end

-- « Juste signaler » : le joueur VOIT que c'est en anglais mais ne sait pas
-- (ou ne veut pas) traduire. Il marque simplement la ligne « à traduire ».
-- On range ça comme un signalement normal (diagnostiqué par le compagnon).
local function EnregistrerSignalement(ctx, ligne)
    if not ctx then
        return false, "Aucun élément détecté : survolez-le puis rouvrez."
    end
    if not ligne or ligne == "" then
        return false, "Cliquez d'abord, à gauche, la ligne à signaler."
    end
    local s = { Q = date("%d/%m/%y %H:%M"), L = { ligne } }
    if ctx.cible == "interface" then
        s.T = "texte"
    elseif ctx.cible and ctx.ID then
        s.T, s.ID = ctx.cible, ctx.ID
    else
        s.T = "texte"
    end
    local liste = Liste()
    for _, e in ipairs(liste) do
        if e.T == s.T and e.ID == s.ID and e.L and e.L[1] == ligne then
            return false, "Déjà signalé — merci !"
        end
    end
    if #liste >= MAX_SIGNALEMENTS then
        return false, "File pleine : faites un /reload pour l'envoyer."
    end
    table.insert(liste, s)
    return true, nil
end

local fenetre

-- Sélection d'une ligne de l'infobulle : le joueur clique la partie fautive
-- (nom, description, ligne d'effet…). La ligne choisie devient jaune.
local function SelectionnerLigne(f, row)
    if f.rowActive then f.rowActive.txt:SetTextColor(1, 1, 1) end
    f.rowActive = row
    row.txt:SetTextColor(1, 0.82, 0)
    f.selection = row.texte
end

local function ObtenirRow(f, i)
    local row = f.rows[i]
    if not row then
        row = CreateFrame("Button", nil, f.listeContenu)
        row:SetHeight(14)
        row:SetPoint("TOPLEFT", 0, -(i - 1) * 14)
        row:SetPoint("TOPRIGHT", 0, -(i - 1) * 14)
        row.txt = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
        row.txt:SetPoint("LEFT", 4, 0)
        row.txt:SetPoint("RIGHT", -4, 0)
        row.txt:SetJustifyH("LEFT")
        row.txt:SetHeight(14)
        local hl = row:CreateTexture(nil, "HIGHLIGHT")
        hl:SetAllPoints()
        hl:SetTexture("Interface\\QuestFrame\\UI-QuestTitleHighlight")
        hl:SetBlendMode("ADD")
        hl:SetAlpha(0.35)
        row:SetScript("OnClick", function(self) SelectionnerLigne(f, self) end)
        f.rows[i] = row
    end
    return row
end

local function PeuplerLignes(f, lignes)
    f.selection = nil
    f.rowActive = nil
    local n = 0
    for i, texte in ipairs(lignes or {}) do
        local row = ObtenirRow(f, i)
        row.texte = texte
        local aff = texte
        if string.len(aff) > 70 then aff = string.sub(aff, 1, 68) .. "…" end
        row.txt:SetText(aff)
        row.txt:SetTextColor(1, 1, 1)
        row:Show()
        n = i
    end
    for i = n + 1, #f.rows do f.rows[i]:Hide() end
    f.listeContenu:SetHeight(math.max(1, n * 14))
    -- Une seule ligne (élément d'interface) : sélectionnée d'office.
    if n == 1 then SelectionnerLigne(f, f.rows[1]) end
end

local function ConstruireFenetre()
    local f = CreateFrame("Frame", "AscensionFRSignaler", UIParent)
    f:SetSize(480, 470)
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
    f.rows = {}

    local titre = f:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    titre:SetPoint("TOP", 0, -14)
    titre:SetText("AscensionFR — proposer une traduction")

    f.elem = f:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
    f.elem:SetPoint("TOPLEFT", 20, -42)
    f.elem:SetPoint("RIGHT", -20, 0)
    f.elem:SetJustifyH("LEFT")

    local instr = f:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    instr:SetPoint("TOPLEFT", f.elem, "BOTTOMLEFT", 0, -10)
    instr:SetPoint("RIGHT", f, "RIGHT", -20, 0)
    instr:SetJustifyH("LEFT")
    instr:SetText("1. Cliquez la ligne à corriger :   "
        .. "|cff909090(infobulle détaillée ? maintenez MAJ puis ouvrez avec "
        .. "le raccourci)|r")

    local cadreListe = CreateFrame("Frame", nil, f)
    cadreListe:SetPoint("TOPLEFT", instr, "BOTTOMLEFT", 0, -6)
    cadreListe:SetPoint("RIGHT", f, "RIGHT", -20, 0)
    cadreListe:SetHeight(150)
    cadreListe:SetBackdrop({
        bgFile = "Interface\\Tooltips\\UI-Tooltip-Background",
        edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
        tile = true, tileSize = 16, edgeSize = 16,
        insets = { left = 4, right = 4, top = 4, bottom = 4 },
    })
    cadreListe:SetBackdropColor(0, 0, 0, 0.6)
    local defilListe = CreateFrame("ScrollFrame", "AscensionFRSignalerListe",
                                   cadreListe, "UIPanelScrollFrameTemplate")
    defilListe:SetPoint("TOPLEFT", 8, -8)
    defilListe:SetPoint("BOTTOMRIGHT", -28, 8)
    f.listeContenu = CreateFrame("Frame", nil, defilListe)
    f.listeContenu:SetSize(400, 10)
    defilListe:SetScrollChild(f.listeContenu)

    local lbl = f:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    lbl:SetPoint("TOPLEFT", cadreListe, "BOTTOMLEFT", 0, -12)
    lbl:SetText("2. Votre traduction  —  ou cliquez « Signaler à traduire »")

    local zone = CreateFrame("Frame", nil, f)
    zone:SetPoint("TOPLEFT", lbl, "BOTTOMLEFT", 0, -6)
    zone:SetPoint("BOTTOMRIGHT", f, "BOTTOMRIGHT", -20, 46)
    zone:SetBackdrop({
        bgFile = "Interface\\Tooltips\\UI-Tooltip-Background",
        edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
        tile = true, tileSize = 16, edgeSize = 16,
        insets = { left = 4, right = 4, top = 4, bottom = 4 },
    })
    zone:SetBackdropColor(0, 0, 0, 0.6)
    local defil = CreateFrame("ScrollFrame", "AscensionFRSignalerDefil",
                              zone, "UIPanelScrollFrameTemplate")
    defil:SetPoint("TOPLEFT", 8, -8)
    defil:SetPoint("BOTTOMRIGHT", -28, 8)
    local saisie = CreateFrame("EditBox", "AscensionFRSignalerSaisie", defil)
    saisie:SetMultiLine(true)
    saisie:SetAutoFocus(false)
    saisie:SetFontObject(ChatFontNormal)
    saisie:SetWidth(380)
    saisie:SetScript("OnEscapePressed", function(self)
        self:ClearFocus()
        f:Hide()
    end)
    defil:SetScrollChild(saisie)
    f.saisie = saisie

    local envoyer = CreateFrame("Button", nil, f, "UIPanelButtonTemplate")
    envoyer:SetSize(110, 24)
    envoyer:SetPoint("BOTTOMRIGHT", -20, 14)
    envoyer:SetText("Envoyer")
    envoyer:SetScript("OnClick", function()
        local ok, err = EnregistrerProposition(f.contexte,
                                                f.saisie:GetText(), f.selection)
        if ok then
            print(string.format("|cff0099ffAscensionFR|r : merci ! "
                .. "Proposition notée (%d en attente). Le Hub l'enverra "
                .. "au prochain /reload.", #Liste()))
            f:Hide()
        else
            print("|cff0099ffAscensionFR|r : " .. (err or "envoi impossible."))
        end
    end)

    -- Signaler SANS proposer de traduction : pour qui voit l'anglais sans
    -- savoir le traduire. Marque juste la ligne « à traduire ».
    local signaler = CreateFrame("Button", nil, f, "UIPanelButtonTemplate")
    signaler:SetSize(150, 24)
    signaler:SetPoint("RIGHT", envoyer, "LEFT", -8, 0)
    signaler:SetText("Signaler à traduire")
    signaler:SetScript("OnClick", function()
        local ok, err = EnregistrerSignalement(f.contexte, f.selection)
        if ok then
            print(string.format("|cff0099ffAscensionFR|r : signalé à traduire "
                .. "(%d en attente). Merci ! Le Hub l'enverra au /reload.",
                #Liste()))
            f:Hide()
        else
            print("|cff0099ffAscensionFR|r : " .. (err or "envoi impossible."))
        end
    end)

    local fermer = CreateFrame("Button", nil, f, "UIPanelButtonTemplate")
    fermer:SetSize(80, 24)
    fermer:SetPoint("RIGHT", signaler, "LEFT", -8, 0)
    fermer:SetText("Fermer")
    fermer:SetScript("OnClick", function() f:Hide() end)

    tinsert(UISpecialFrames, "AscensionFRSignaler")
    fenetre = f
    return f
end

local LIBELLE_CIBLE = { objet = "objet", sort = "sort", pnj = "PNJ",
                        interface = "interface", texte = "texte d'infobulle" }

function AFR.OuvrirSignalement()
    local f = fenetre or ConstruireFenetre()
    local ctx = ContexteSignalement()
    f.contexte = ctx
    if ctx and ctx.cible == "interface" then
        f.elem:SetText("Élément : |cffffd200interface|r ("
            .. (ctx.nomCadre or "?") .. ")")
    elseif ctx and ctx.cible then
        local suffixe = ctx.ID and ("  #" .. tostring(ctx.ID)) or ""
        f.elem:SetText("Élément : |cffffd200"
            .. (LIBELLE_CIBLE[ctx.cible] or ctx.cible) .. "|r" .. suffixe)
    else
        f.elem:SetText("|cffff8080Aucun élément détecté.|r Survolez l'objet, "
            .. "le sort ou le PNJ à corriger, puis rouvrez cette fenêtre.")
    end
    PeuplerLignes(f, ctx and ctx.lignes or {})
    f.saisie:SetText("")
    f:Show()
    f.saisie:SetFocus()
end
