-- ============================================================================
-- AscensionFR - Quêtes
-- Fenêtres de quête (accept/progrès/rendu), journal de quêtes, suivi.
-- ============================================================================
local AFR = AscensionFR

-- Chronomètre cette greffe si l'instrument de mesure est chargé (/afr perf).
-- Sans lui, la fonction passe telle quelle : aucun surcoût, aucune dépendance.
local function MESURER(nom, fn)
    if AFR.Perf and AFR.Perf.Greffe then return AFR.Perf.Greffe(nom, fn) end
    return fn
end


local function Sub(t) return AFR.Substituer(t) end

-- Déclaré en avance : la fonction vit plus bas mais doit être appelable
-- depuis ApresQuestInfoDisplay (armement tardif de la pulsation).
local ArmerPulsationJournal

-- Identifiant de la quête proposée par un PNJ.
-- GetQuestID() n'existe PAS sur le client d'Ascension : l'appeler faisait
-- planter le module à chaque dialogue de quête, sans rien traduire. On se
-- rabat sur le titre affiché, que nos bases indexent aussi.
local function IdQueteOfferte()
    if type(GetQuestID) == "function" then
        local id = GetQuestID()
        if id and id ~= 0 then return id end
    end
    if type(GetTitleText) == "function" then
        local titre = GetTitleText()
        if titre and titre ~= "" then
            local q, id = AFR.QueteParTitreEN(titre)
            if id then return tonumber(id) end
        end
    end
    return nil
end

-- ----------------------------------------------------------------------------
-- Fenêtre de dialogue de quête (PNJ)
-- ----------------------------------------------------------------------------
local function TraduireDetail()
    local id = IdQueteOfferte()
    local q = id and AFR.DB.Quetes[id]
    if not q then return end
    if q.T and QuestInfoTitleText then QuestInfoTitleText:SetText(Sub(q.T)) end
    if q.D and QuestInfoDescriptionText then
        QuestInfoDescriptionText:SetText(Sub(q.D))
    end
    if q.O and QuestInfoObjectivesText then
        QuestInfoObjectivesText:SetText(Sub(q.O))
    end
end

local function TraduireProgres()
    local id = IdQueteOfferte()
    local q = id and AFR.DB.Quetes[id]
    if q and q.T and QuestProgressTitleText then
        QuestProgressTitleText:SetText(Sub(q.T))
    end
    if q and q.P and QuestProgressText then
        QuestProgressText:SetText(Sub(q.P))
    elseif id then
        -- Texte de progression inconnu : on le récolte pour traduction.
        AFR.Recolter("QuetesProgres", id, GetProgressText())
    end
end

local function TraduireRendu()
    local id = IdQueteOfferte()
    local q = id and AFR.DB.Quetes[id]
    if q and q.T and QuestInfoTitleText then
        QuestInfoTitleText:SetText(Sub(q.T))
    end
    if q and q.R and QuestInfoRewardText then
        QuestInfoRewardText:SetText(Sub(q.R))
    elseif id then
        AFR.Recolter("QuetesRendu", id, GetRewardText())
    end
end

-- ----------------------------------------------------------------------------
-- Journal de quêtes (panneau de détails, via QuestInfo_Display partagé)
-- ----------------------------------------------------------------------------
local function IdQueteJournalSelectionnee()
    local sel = GetQuestLogSelection()
    if not sel or sel == 0 then return nil end
    return AFR.IdDepuisLienQuete(GetQuestLink(sel))
end

local function TraduireLignesObjectifs()
    for i = 1, 10 do
        local ligne = _G["QuestInfoObjective" .. i]
        if ligne and ligne:IsShown() then
            local fr = AFR.TraduireObjectif(ligne:GetText())
            if fr then ligne:SetText(fr) end
        end
    end
end

local function ApresQuestInfoDisplay(template)
    if not AFR.Actif() then return end
    -- Armement tardif de la pulsation du journal (si QuestLogFrame
    -- n'existait pas encore au chargement du module).
    if ArmerPulsationJournal then ArmerPulsationJournal() end
    local id
    if QuestInfoFrame and QuestInfoFrame.questLog then
        id = IdQueteJournalSelectionnee()
    else
        id = IdQueteOfferte()
    end
    local q = id and AFR.DB.Quetes[id]
    if q then
        -- Ascension a réécrit la fenêtre de détails : le titre n'est pas dans
        -- QuestInfoTitleText (le titre restait anglais alors que description
        -- et objectifs étaient traduits). On ne nomme donc plus le cadre : on
        -- parcourt la fenêtre et on remplace le texte reconnu.
        if q.T and q.TE then
            AFR.Parcourir(QuestLogFrame, { [q.TE] = Sub(q.T) })
            AFR.Parcourir(QuestFrame, { [q.TE] = Sub(q.T) })
        end
        if q.T and QuestInfoTitleText and QuestInfoTitleText:IsShown() then
            QuestInfoTitleText:SetText(Sub(q.T))
        end
        if q.D and QuestInfoDescriptionText
            and QuestInfoDescriptionText:IsShown() then
            QuestInfoDescriptionText:SetText(Sub(q.D))
        end
        if q.O and QuestInfoObjectivesText
            and QuestInfoObjectivesText:IsShown() then
            QuestInfoObjectivesText:SetText(Sub(q.O))
        end
        if q.R and QuestInfoRewardText and QuestInfoRewardText:IsShown() then
            QuestInfoRewardText:SetText(Sub(q.R))
        end
    end
    TraduireLignesObjectifs()
end

-- ----------------------------------------------------------------------------
-- Journal de quêtes (liste des titres à gauche)
-- ----------------------------------------------------------------------------
-- Étiquettes de droite « (Complete) », « (Dungeon) »... — mot à mot, pour
-- couvrir aussi les combinaisons (« (Dungeon) (Complete) »).
local ETIQUETTES_JOURNAL = {
    Complete = "Terminée", Failed = "Échec", Daily = "Quotidienne",
    Dungeon = "Donjon", Raid = "Raid", Group = "Groupe",
    Heroic = "Héroïque", PvP = "JcJ", Elite = "Élite",
}

-- Habillage fixe de la fenêtre : titre, compteur, boutons du bas. Relu à
-- chaque rafraîchissement (SetText ne coûte rien) parce que ces textes sont
-- posés par le client AVANT nos crochets, et que « Track/Untrack » change
-- selon la quête sélectionnée. On ne touche JAMAIS aux globales (taint) :
-- uniquement l'affichage.
local BOUTONS_JOURNAL = {
    ["Abandon"] = "Abandonner",
    ["Share"] = "Partager",
    ["Track"] = "Suivre",
    ["Untrack"] = "Ne plus suivre",
    ["Push Quest"] = "Partager",
}

local CHROME_JOURNAL = {
    ["Quest Log"] = "Journal de quêtes",
}

-- Titres FR de toutes les quêtes du journal, indexés par leur texte anglais
-- EXACT. L'anglais vient de l'API (GetQuestLogTitle), jamais de nos bases :
-- on colle donc toujours à ce que le client affiche vraiment.
local function CorrespondancesListe()
    local corr = {}
    if type(GetNumQuestLogEntries) ~= "function" then return corr end
    for i = 1, GetNumQuestLogEntries() do
        local titre, _, _, _, estEntete = GetQuestLogTitle(i)
        if titre and titre ~= "" and not estEntete then
            local q
            local id = AFR.IdDepuisLienQuete(GetQuestLink(i))
            if id then q = AFR.DB.Quetes[id] end
            if not q then
                -- Repli par TITRE (même leçon que GetQuestID : les
                -- fonctions du client d'Ascension ne sont pas fiables).
                q = AFR.QueteParTitreEN(titre)
            end
            if q and q.T then corr[titre] = Sub(q.T) end
        end
    end
    return corr
end

-- Traduit UNE zone de texte de la fenêtre, quel que soit son nom de cadre :
-- habillage exact, compteur, étiquettes « (Complete) », boutons, et titres
-- de quêtes (avec leur habillage « [niveau] » ou retrait préservé).
local function ResoudreTexte(texte, corr)
    if CHROME_JOURNAL[texte] then return CHROME_JOURNAL[texte] end
    if BOUTONS_JOURNAL[texte] then return BOUTONS_JOURNAL[texte] end
    local n = string.match(texte, "^Quests:%s*(%d+/%d+)$")
    if n then return "Quêtes : " .. n end
    if string.find(texte, "^%(") then
        local fr = string.gsub(texte, "%((%a+)%)", function(mot)
            return "(" .. (ETIQUETTES_JOURNAL[mot] or mot) .. ")"
        end)
        if fr ~= texte then return fr end
        return nil
    end
    if corr[texte] then return corr[texte] end
    -- « [12] Titre » ou «   Titre » : on détache l'habillage, on traduit
    -- le cœur, on rattache.
    local prefixe, corps = string.match(texte, "^(%s*%[.-%]%s*)(.+)$")
    if not prefixe then
        prefixe, corps = string.match(texte, "^(%s+)(.+)$")
    end
    if corps and corr[corps] then return prefixe .. corr[corps] end
    return nil
end

local function ParcourirResolveur(cadre, corr, profondeur)
    profondeur = profondeur or 0
    if not cadre or profondeur > 6 then return end
    if AFR.EstProtege(cadre) then return end
    if cadre.GetRegions then
        for _, region in ipairs({ cadre:GetRegions() }) do
            if region and region.GetObjectType
                    and region:GetObjectType() == "FontString" then
                local texte = region:GetText()
                if texte and texte ~= "" then
                    local fr = ResoudreTexte(texte, corr)
                    if fr then region:SetText(fr) end
                end
            end
        end
    end
    if cadre.GetChildren then
        for _, enfant in ipairs({ cadre:GetChildren() }) do
            ParcourirResolveur(enfant, corr, profondeur + 1)
        end
    end
end

local function TraduireListeJournal()
    if not AFR.Actif() then return end
    if not QuestLogFrame or not QuestLogFrame:IsShown() then return end
    ParcourirResolveur(QuestLogFrame, CorrespondancesListe())
end

-- Pulsation légère tant que le journal est ouvert : Ascension redessine sa
-- liste sans passer par QuestLog_Update (le crochet dessus ne se déclenche
-- JAMAIS chez eux — vécu : rien ne se traduisait). Un enfant de
-- QuestLogFrame ne reçoit OnUpdate que fenêtre visible : l'addon ne coûte
-- donc rien journal fermé, et ~3 passages/seconde ouvert (parcours d'une
-- centaine de zones de texte, négligeable).
function ArmerPulsationJournal()
    if not QuestLogFrame or QuestLogFrame.afrPulsation then return end
    local guetteur = CreateFrame("Frame", nil, QuestLogFrame)
    QuestLogFrame.afrPulsation = guetteur
    local cumul = 0
    guetteur:SetScript("OnUpdate", function(_, ecoule)
        cumul = cumul + (ecoule or 0)
        -- 0,1 s : au défilement, l'anglais ne reste visible qu'un clin
        -- d'œil (0,3 s se voyait — retour de Dan). Le parcours reste
        -- minuscule et ne tourne que fenêtre ouverte.
        if cumul < 0.1 then return end
        cumul = 0
        TraduireListeJournal()
    end)
end

ArmerPulsationJournal()

-- ----------------------------------------------------------------------------
-- Correspondances construites depuis le journal de quêtes
--
-- L'anglais vient du jeu (API), le français de nos bases via l'identifiant de
-- la quête. Aucun texte anglais n'est donc stocké : on interroge le client au
-- moment voulu. Sert à la fois au suivi et aux fenêtres de quête, dont
-- Ascension a réécrit les cadres.
-- ----------------------------------------------------------------------------
local function ConstruireCorrespondances()
    local corr = {}
    if type(GetNumQuestLogEntries) ~= "function" then return corr end
    local nb = GetNumQuestLogEntries()
    for i = 1, nb do
        local titreEN, _, _, _, estEntete = GetQuestLogTitle(i)
        if titreEN and not estEntete then
            local id = AFR.IdDepuisLienQuete(GetQuestLink(i))
            local q = id and AFR.DB.Quetes[id]
            if q then
                if q.T then corr[titreEN] = Sub(q.T) end

                -- Quête accomplie : le suivi affiche le texte de rendu
                -- (WatchFrame.lua:978 -> GetQuestLogCompletionText).
                if q.A and type(GetQuestLogCompletionText) == "function" then
                    local ok, texteEN = pcall(GetQuestLogCompletionText, i)
                    if ok and texteEN and texteEN ~= "" then
                        corr[texteEN] = Sub(q.A)
                    end
                end

                -- Lignes d'objectifs
                if type(GetNumQuestLeaderBoards) == "function" then
                    for j = 1, (GetNumQuestLeaderBoards(i) or 0) do
                        local texteEN = GetQuestLogLeaderBoard(j, i)
                        if texteEN and texteEN ~= "" then
                            local fr = (q.OT and q.OT[j] ~= "" and q.OT[j])
                                or AFR.TraduireObjectif(texteEN)
                            if fr then
                                corr[texteEN] = fr
                                -- Ascension inverse l'objectif à l'affichage
                                -- (« Bûche : 7/12 » -> « 7/12 Bûche »). On
                                -- réutilise LEUR fonction pour produire
                                -- exactement le même format en français.
                                if type(WatchFrame_ReverseQuestObjective) == "function" then
                                    local okA, invEN = pcall(WatchFrame_ReverseQuestObjective, texteEN)
                                    local okB, invFR = pcall(WatchFrame_ReverseQuestObjective, fr)
                                    if okA and okB and invEN and invFR then
                                        corr[invEN] = invFR
                                    end
                                end
                            end
                        end
                    end
                end
            end
        end
    end
    return corr
end

-- ----------------------------------------------------------------------------
-- Suivi des objectifs (WatchFrame, à droite de l'écran)
--
-- Vérifié dans le code d'Ascension : ce cadre n'appelle aucune fonction
-- protégée et ses boutons d'objets de quête n'héritent d'aucun template
-- sécurisé. AFR.Parcourir vérifie quand même avant d'écrire — une mise à jour
-- du serveur pourrait changer cela, et écrire dans un cadre protégé
-- bloquerait les actions du joueur.
-- ----------------------------------------------------------------------------
-- Reporté après le combat si on a dû s'abstenir (voir le garde ci-dessous).
local aRefaireSuivi = false

-- Compteurs de diagnostic (/afrsuivi), pour répondre aux signalements sans
-- faire deviner le joueur.
AFR.SuiviCompteurs = { total = 0, combat = 0, restreint = 0, complet = 0 }

-- Coupe-circuit dédié, à donner à un joueur si jamais le passage en combat
-- posait problème :
--   /run AscensionFRSaved.Options.sansSuiviCombat = true   (couper)
--   /run AscensionFRSaved.Options.sansSuiviCombat = nil    (rétablir)
local function SuiviCombatCoupe()
    local options = AscensionFRSaved and AscensionFRSaved.Options
    return options and options.sansSuiviCombat
end

-- ----------------------------------------------------------------------------
-- Passage RESTREINT — le seul autorisé en plein combat.
--
-- On atteint les zones de texte par leur NOM (_G["WatchFrameLine"..i].text),
-- sans jamais parcourir l'arbre du cadre. On ne touche donc pas d'un cheveu
-- aux boutons d'objet de quête (_G["WatchFrameItem"..i]) : ce sont les SEULS
-- éléments sécurisés du suivi, et ils portent un autre nom. Écrire dans une
-- FontString n'est pas une fonction protégée — c'est exactement ce que fait
-- déjà la boucle des objectifs de collecte, hors combat, depuis la 1.7.5.
-- ----------------------------------------------------------------------------
local function TraduireLignesSuivi(corr)
    local noms = AFR.DB.ObjetsNoms
    local i = 1
    while true do
        local ligne = _G["WatchFrameLine" .. i]
        if not ligne then break end
        local zone = ligne.text
        local texte = zone and zone.GetText and zone:GetText()
        if texte and texte ~= "" then
            local fr = corr and corr[texte]
            if fr then
                zone:SetText(fr)
            elseif noms then
                -- Objectifs de COLLECTE (« 0/1 Warsong Saw Blades ») : le nom
                -- d'objet se traduit par le pont DB.ObjetsNoms (TDB officiel
                -- × nos customs).
                local avant, fait, total, nom =
                    string.match(texte, "^([%-%s]*)(%d+)/(%d+) (.+)$")
                local trad = nom and noms[nom]
                if trad then
                    zone:SetText(avant .. fait .. "/" .. total .. " " .. trad)
                end
            end
        end
        i = i + 1
    end
end

local function TraduireSuivi()
    if not AFR.Actif() or not WatchFrame then return end
    local c = AFR.SuiviCompteurs
    c.total = c.total + 1

    -- EN COMBAT — on ne s'abstient plus COMPLÈTEMENT (correctif 3.0.1).
    --
    -- Le garde d'origine protégeait des boutons sécurisés du suivi : notre code
    -- ne doit pas passer dans l'arbre du cadre pendant que le jeu repositionne
    -- ces boutons, sous peine de souiller (taint) le chemin d'action et de
    -- faire bloquer les sorts du joueur. Ce risque-là reste entier : le
    -- parcours complet demeure interdit en combat.
    --
    -- Mais s'abstenir de TOUT traduire avait un effet que personne n'avait vu
    -- venir, et que les joueurs ont signalé sur la 3.0.0 : le suivi
    -- « clignote » entre le français et l'anglais sans arrêt. La cause est
    -- mécanique — WatchFrame_OnEvent repeint tout le suivi EN ANGLAIS à chaque
    -- QUEST_LOG_UPDATE, c'est-à-dire à CHAQUE MOB TUÉ pour une quête. L'anglais
    -- restait donc affiché du premier coup tué jusqu'à la fin du combat, puis
    -- PLAYER_REGEN_ENABLED remettait le français. Mob suivant, rebelote.
    -- Ça ne se voyait que chez les joueurs qui enchaînent les quêtes de
    -- tuer/ramasser — d'où « seulement certains joueurs ».
    --
    -- On traduit donc en mode RESTREINT (voir ci-dessus), qui ne touche que des
    -- zones de texte nommées et ne s'approche jamais des boutons sécurisés, et
    -- on garde le rattrapage complet à la sortie du combat.
    if InCombatLockdown() then
        c.combat = c.combat + 1
        aRefaireSuivi = true
        if not SuiviCombatCoupe() then
            c.restreint = c.restreint + 1
            TraduireLignesSuivi(ConstruireCorrespondances())
        end
        return
    end

    c.complet = c.complet + 1
    local corr = ConstruireCorrespondances()
    AFR.Parcourir(WatchFrame, corr)
    TraduireLignesSuivi(corr)
end

-- ----------------------------------------------------------------------------
-- Branchements
-- ----------------------------------------------------------------------------
local frame = CreateFrame("Frame")
frame:RegisterEvent("QUEST_DETAIL")
frame:RegisterEvent("QUEST_PROGRESS")
frame:RegisterEvent("QUEST_COMPLETE")
frame:RegisterEvent("PLAYER_REGEN_ENABLED")   -- sortie de combat
frame:SetScript("OnEvent", function(self, event)
    -- Fin du combat : on rattrape le suivi qu'on s'est interdit de traduire.
    if event == "PLAYER_REGEN_ENABLED" then
        if aRefaireSuivi then
            aRefaireSuivi = false
            TraduireSuivi()
        end
        return
    end
    if not AFR.Actif() then return end
    if event == "QUEST_DETAIL" then
        TraduireDetail()
    elseif event == "QUEST_PROGRESS" then
        TraduireProgres()
    elseif event == "QUEST_COMPLETE" then
        TraduireRendu()
    end
end)

hooksecurefunc("QuestInfo_Display", ApresQuestInfoDisplay)
hooksecurefunc("QuestLog_Update", TraduireListeJournal)
if type(WatchFrame_Update) == "function" then
    -- Rétabli en 1.7.5. Coupé pendant la recherche du blocage des sorts, par
    -- précaution. Le garde-fou nécessaire était déjà en place : TraduireSuivi
    -- refuse de tourner pendant le combat (InCombatLockdown) et rattrape à la
    -- sortie, précisément parce que le suivi héberge des boutons sécurisés.
    -- Dans le taint.log, aucune souillure du suivi n'atteignait jamais une
    -- fonction protégée — seules les variables globales le faisaient.
    hooksecurefunc("WatchFrame_Update", MESURER("SuiviQuetes", TraduireSuivi))
end

if type(WatchFrameItem_OnEnter) == "function" then
    hooksecurefunc("WatchFrameItem_OnEnter", function(self)
        if not AFR.Actif() then return end
        local lien = GetQuestLogSpecialItemInfo(self:GetID())
        local id = lien and AFR.IdDepuisLienObjet(lien)
        local o = id and AFR.DB.Objets[id]
        if o and o.N and GameTooltipTextLeft1 then
            GameTooltipTextLeft1:SetText(o.N)
            GameTooltip:Show()
        end
    end)
end

-- ============================================================================
-- HABILLAGE de la fenêtre de quêtes (« Choose your reward: », « You will
-- also receive: », « Experience: », boutons Accepter/Terminer la quête...)
-- + noms des OBJETS récompense, traduits par leur lien — comme chez les
-- marchands. Les éléments QuestInfo sont PARTAGÉS entre la fenêtre du PNJ
-- (QuestFrame) et le journal (QuestLogFrame) : on repeint les deux racines.
-- ============================================================================
local chrome_quetes

local function ChromeQuetes()
    if not chrome_quetes then
        chrome_quetes = {}
        for _, cle in ipairs({ "REWARD_CHOOSE", "REWARD_CHOICES",
            "REWARD_ITEMS", "REWARD_ITEMS_ONLY", "EXPERIENCE_COLON",
            "COMPLETE_QUEST", "BONUS_HONOR", "BONUS_TALENTS",
            "ACCEPT", "CONTINUE", "DECLINE", "GOODBYE", "CANCEL" }) do
            local en, fr = _G[cle], AFR.DB.UI[cle]
            if type(en) == "string" and en ~= ""
                and type(fr) == "string" and fr ~= "" and en ~= fr then
                chrome_quetes[en] = fr
            end
        end
    end
    return chrome_quetes
end

local function RepeindreZones(cadre, mots, profondeur)
    if profondeur <= 0 then return end
    for _, r in ipairs({ cadre:GetRegions() }) do
        if r.GetObjectType and r:GetObjectType() == "FontString" then
            local fr = mots[r:GetText() or ""]
            if fr then r:SetText(fr) end
        end
    end
    for _, enfant in ipairs({ cadre:GetChildren() }) do
        local genre = enfant.GetObjectType and enfant:GetObjectType()
        if genre ~= "EditBox" then
            if (genre == "Button" or genre == "CheckButton")
                and enfant.GetText then
                local fr = mots[enfant:GetText() or ""]
                if fr then enfant:SetText(fr) end
            end
            RepeindreZones(enfant, mots, profondeur - 1)
        end
    end
end

local function NomsRecompenses()
    local i = 1
    while true do
        local bouton = _G["QuestInfoItem" .. i]
        if not bouton then break end
        local nomFS = _G["QuestInfoItem" .. i .. "Name"]
        -- rewardType == "spell" : le client réutilise le bouton pour un SORT
        -- récompense sans reposer .type ni l'ID — les champs restants datent
        -- de l'affichage PRÉCÉDENT (audit du 20/07) : on n'y touche pas.
        if nomFS and bouton:IsShown() and bouton.type
            and bouton.rewardType ~= "spell" then
            local lien
            if QuestInfoFrame and QuestInfoFrame.questLog then
                lien = GetQuestLogItemLink(bouton.type, bouton:GetID())
            else
                lien = GetQuestItemLink(bouton.type, bouton:GetID())
            end
            local id = AFR.IdDepuisLienObjet(lien)
            local o = id and AFR.DB.Objets[id]
            if o and o.N then nomFS:SetText(o.N) end
        end
        i = i + 1
    end
end

-- Étiquettes des récompenses : régions nommées GLOBALEMENT, partagées entre
-- la fenêtre du PNJ et le journal. (QuestInfoFrame n'est qu'une TABLE de
-- réglages dans ce client — surtout ne pas la balayer comme un cadre.)
local ZONES_QUETES = {
    "QuestInfoItemChooseText", "QuestInfoItemReceiveText",
    "QuestInfoXPFrameReceiveText", "QuestInfoHonorFrameReceiveText",
    "QuestInfoArenaPointsFrameReceiveText", "QuestInfoTalentFrameReceiveText",
}

local function HabillerQuetes()
    if not AFR.Actif() then return end
    local mots = ChromeQuetes()
    if QuestFrame then RepeindreZones(QuestFrame, mots, 6) end
    -- Titre de la fenêtre : le nom du PNJ (index des créatures, si connu).
    -- Plaques.lua se charge APRÈS ce module (.toc) : test à l'exécution.
    if AFR.NomCreatureFrancais then
        for _, nom in ipairs({ "QuestFrameNpcNameText",
                               "GossipFrameNpcNameText" }) do
            local zone = _G[nom]
            local texte = zone and zone.GetText and zone:GetText()
            local fr = texte and AFR.NomCreatureFrancais(texte)
            if fr then zone:SetText(fr) end
        end
    end
    for _, nom in ipairs(ZONES_QUETES) do
        local zone = _G[nom]
        local texte = zone and zone.GetText and zone:GetText()
        if texte and texte ~= "" and mots[texte] then
            zone:SetText(mots[texte])
        end
    end
    NomsRecompenses()
end

if type(QuestInfo_Display) == "function" then
    hooksecurefunc("QuestInfo_Display", HabillerQuetes)
end
if QuestFrame and QuestFrame.HookScript then
    QuestFrame:HookScript("OnShow", HabillerQuetes)
end

-- ============================================================================
-- /afrsuivi — relevé copiable de l'état du suivi de quêtes.
--
-- Écrit pour le signalement « le suivi clignote entre le français et
-- l'anglais » (3.0.0). À faire lancer par un joueur touché JUSTE APRÈS un
-- combat : la ligne « repeints en combat » monte à chaque mob tué, et c'est
-- elle qui trahit le problème.
-- ============================================================================
SLASH_AFRSUIVI1 = "/afrsuivi"
SlashCmdList["AFRSUIVI"] = function()
    local lignes = {}
    local function noter(t) table.insert(lignes, t) end

    noter("=== /afrsuivi - etat du suivi de quetes ===")
    noter("addon actif : " .. tostring(AFR.Actif()))
    noter("cadre present : " .. tostring(WatchFrame ~= nil))
    noter("en combat maintenant : " .. tostring(InCombatLockdown() and true))
    noter("passage en combat coupe : " .. tostring(SuiviCombatCoupe() and true))
    noter("crochet WatchFrame_Update : "
          .. tostring(type(WatchFrame_Update) == "function"))
    noter("rattrapage en attente : " .. tostring(aRefaireSuivi))

    local c = AFR.SuiviCompteurs
    noter("")
    noter("=== repeints du suivi depuis la connexion ===")
    noter("total : " .. c.total)
    noter("dont en combat : " .. c.combat .. "   (2.2.0 : laisses en ANGLAIS)")
    noter("  -> traduits en restreint : " .. c.restreint)
    noter("dont hors combat : " .. c.complet)

    noter("")
    noter("=== lignes affichees ===")
    local i, vides = 1, 0
    while true do
        local ligne = _G["WatchFrameLine" .. i]
        if not ligne then break end
        local zone = ligne.text
        local texte = zone and zone.GetText and zone:GetText()
        if texte and texte ~= "" then
            -- 0xC3 = premier octet des accents francais en UTF-8. Present =
            -- la ligne est deja en francais.
            local accent = string.find(texte, "\195") and "FR" or "??"
            noter("L" .. i .. " [" .. accent .. "] " .. texte)
        else
            vides = vides + 1
        end
        i = i + 1
    end
    noter("(" .. vides .. " lignes vides ignorees)")

    local texte = table.concat(lignes, "\n")
    if AFR.AfficherReleve then
        AFR.AfficherReleve(texte)
    else
        print(texte)
    end
end
