-- ============================================================================
-- AscensionFR - Panneau d'options, en quatre onglets
--
-- Se range dans Échap -> Interface -> AddOns, là où le joueur cherche les
-- réglages d'un addon — plutôt qu'une fenêtre flottante de plus.
-- /afr l'ouvre directement ; les commandes /afr on|off|debug restent valides.
--
-- Refonte : une seule page, QUATRE ONGLETS (les boutons d'onglets classiques
-- du jeu, comme sur la feuille de personnage) :
--   1. Accueil      : l'interrupteur, le compteur de traductions, l'état de
--                     la récolte avec « Envoyer mes découvertes », et
--                     l'encart « Soutenir le projet ».
--   2. Réglages     : tous les coupe-circuits, chacun avec sa courte ligne
--                     d'explication grise.
--   3. Addons tiers : une section par addon pris en charge (registre
--                     ADDONS_TIERS ci-dessous, extensible).
--   4. Journal      : la console de l'addon + « Préparer le rapport ».
-- Les anciennes sous-catégories « Journal » et « Aider la traduction » sont
-- devenues des onglets : rien n'a disparu, tout est rangé.
-- ============================================================================
local AFR = AscensionFR

-- ----------------------------------------------------------------------------
-- LIEN DE SOUTIEN (encart « Soutenir le projet », onglet Accueil).
--
-- >>> A_REMPLIR : Dan fournira l'adresse définitive de sa page de soutien. <<<
-- Remplacer UNIQUEMENT le texte entre guillemets ci-dessous ; rien d'autre à
-- toucher, l'encart se met à jour tout seul.
-- ----------------------------------------------------------------------------
local SOUTIEN_URL = "https://buymeacoffee.com/lepetitdan"

-- Le salon où centraliser les retours. Un lien copiable dans l'addon évite
-- de recevoir les signalements « de partout » (MP, salons divers...).
local DISCORD = "https://discord.gg/kFJGDJbeay"
AFR.DISCORD = DISCORD

-- Libellés lisibles des bases, dans l'ordre où on veut les montrer.
local CATEGORIES = {
    { "Quetes", "Quêtes" },
    { "Sorts", "Sorts" },
    { "Objets", "Objets" },
    { "Creatures", "Créatures" },
    { "ObjetsMonde", "Objets du monde" },
    { "Repliques", "Répliques des PNJ" },
    { "UI", "Interface" },
    { "Gossip", "Options de dialogue" },
    { "TextesPNJ", "Dialogues" },
    { "Pages", "Livres" },
    { "Libelles", "Libellés" },
    { "Divers", "Divers" },
}

local function Compter(nomTable)
    local n = 0
    for _ in pairs(AFR.DB[nomTable] or {}) do n = n + 1 end
    return n
end

local function TotalRecolte()
    local n = 0
    local r = AscensionFRSaved and AscensionFRSaved.Recolte
    if r then
        for _, cat in pairs(r) do
            for _ in pairs(cat) do n = n + 1 end
        end
    end
    return n
end

local function OptionsSauvees()
    AscensionFRSaved = AscensionFRSaved or {}
    AscensionFRSaved.Options = AscensionFRSaved.Options or {}
    return AscensionFRSaved.Options
end

-- Déclarés d'avance : des poignées de clic construites plus haut dans le
-- fichier s'y réfèrent avant leur définition (même piège que `Balayer` dans
-- Epreuves.lua — sans cette réservation, elles viseraient une globale nil).
local Rafraichir
local AfficherOnglet

-- ----------------------------------------------------------------------------
-- Registre des addons TIERS pris en charge (onglet « Addons tiers »).
--
-- Une entrée = une section à l'écran : le nom, un badge installé/absent, et
-- ses cases. Pour prendre en charge un nouvel addon, il suffit d'ajouter une
-- entrée ici — l'onglet se construit tout seul.
--
-- Les clés `inversee = true` sont ENREGISTRÉES À L'ENVERS : la clé n'existe
-- que si l'on a décoché. Absence = activé. C'est ce qui permet d'ajouter la
-- fonction sans que personne n'ait à aller la cocher.
-- ----------------------------------------------------------------------------
local ADDONS_TIERS = {
    {
        nom = "DragonUI",
        estLa = function()
            return (IsAddOnLoaded and IsAddOnLoaded("DragonUI"))
                and true or false
        end,
        cases = {
            {
                nomGlobal = "AscensionFROptionsDragonTrad",
                cle = "dragonTradOff",
                inversee = true,
                texte = "Traduire l'addon DragonUI",
                info = "Les 1 752 textes de DragonUI et de son panneau "
                    .. "d'options. Décocher demande un /reload pour revenir "
                    .. "à l'anglais.",
                tooltip = "Met en français les 1 752 textes de DragonUI "
                    .. "et de son panneau d'options.\n\nAucun fichier de "
                    .. "DragonUI n'est modifié : ses mises à jour n'effacent "
                    .. "rien.\n\nDécocher demande un /reload pour revenir à "
                    .. "l'anglais.",
                auClic = function(coche)
                    -- Les textes déjà écrits chez DragonUI ne se reprennent
                    -- pas : il faut relancer l'interface pour repartir de
                    -- ses fichiers d'origine.
                    print("|cff0099ffAscensionFR|r : DragonUI "
                        .. (coche and "sera traduit" or "repassera en anglais")
                        .. " au prochain /reload.")
                end,
            },
            {
                nomGlobal = "AscensionFROptionsDragonGrille",
                cle = "dragonGrilleOff",
                inversee = true,
                texte = "DragonUI : grille et aimantation",
                info = "En mode édition : une ligne verte tous les 5 "
                    .. "carreaux, et les cadres se collent à la grille.",
                tooltip = "Dans le mode édition de DragonUI : une ligne "
                    .. "verte tous les 5 carreaux, et les cadres se collent "
                    .. "à la grille quand vous les lâchez.\n\nUn coin du "
                    .. "cadre tombe alors toujours pile sur une "
                    .. "intersection.\n\nDécocher rend la main "
                    .. "immédiatement ; les lignes vertes, elles, "
                    .. "disparaissent au prochain /reload.",
            },
            {
                -- Case NON inversée : cochée = plaquesMalgreDragonUI = true =
                -- on traduit malgré DragonUI. Décochée (défaut) = on laisse
                -- DragonUI tranquille pour que ses auras marchent. Voir
                -- Plaques.lua (GereeParDragonUI) pour le pourquoi technique.
                nomGlobal = "AscensionFROptionsDragonPlaques",
                cle = "plaquesMalgreDragonUI",
                texte = "Traduire les noms sur les barres de vie",
                info = "|cffe0a33dAttention :|r si c'est coché, les barres de "
                    .. "vie de DragonUI n'afficheront plus les buffs, DoT et "
                    .. "auras au-dessus des monstres.",
                tooltip = "Met en français les noms de monstres affichés sur "
                    .. "les barres de vie.\n\n|cffe0a33dLe revers :|r DragonUI "
                    .. "reconnaît chaque monstre à son nom ANGLAIS pour savoir "
                    .. "quelles auras lui coller. Traduire ce nom l'empêche de "
                    .. "les retrouver — les buffs, DoT et débuffs "
                    .. "disparaissent des barres de vie.\n\nDÉCOCHÉ (conseillé "
                    .. "avec DragonUI) : les auras s'affichent, mais les noms "
                    .. "restent en anglais sur les barres de vie.\n\nCOCHÉ : "
                    .. "les noms passent en français, au prix des auras.\n\n"
                    .. "Sans DragonUI, cette option ne sert à rien : les noms "
                    .. "sont traduits de toute façon.",
                auClic = function(coche)
                    print("|cff0099ffAscensionFR|r : barres de vie — "
                        .. (coche
                            and "noms traduits (DragonUI ne montrera plus "
                                .. "les auras des monstres)."
                            or "auras de DragonUI préservées (noms en "
                                .. "anglais sur les barres de vie)."))
                end,
            },
        },
    },
}

-- ----------------------------------------------------------------------------
-- Construction du panneau
-- ----------------------------------------------------------------------------
local panneau = CreateFrame("Frame", "AscensionFROptions")
panneau.name = "Ascension |cff0099ffFR|r"

local titre = panneau:CreateFontString(nil, "ARTWORK", "GameFontNormalLarge")
titre:SetPoint("TOPLEFT", 16, -16)
titre:SetText("Ascension |cff0099ffFR|r — traduction française")

local sousTitre = panneau:CreateFontString(nil, "ARTWORK", "GameFontHighlightSmall")
sousTitre:SetPoint("TOPLEFT", titre, "BOTTOMLEFT", 0, -8)
sousTitre:SetPoint("RIGHT", panneau, "RIGHT", -32, 0)
sousTitre:SetJustifyH("LEFT")
sousTitre:SetJustifyV("TOP")
-- Deux lignes possibles : sans hauteur, la police coupe avec « … » (vécu).
sousTitre:SetHeight(26)
sousTitre:SetText("Traduit tout le jeu en français. Ce qui manque est noté, "
    .. "puis traduit à la prochaine version.")

-- ---- Les quatre onglets ------------------------------------------------
-- Boutons d'onglets classiques 3.3.5, en haut du contenu. Les fonctions
-- PanelTemplates_* du jeu exigent des boutons nommés « <NomDuPanneau>TabN » :
-- ces noms-là sont imposés, pas choisis.
local NOMS_ONGLETS = { "Accueil", "Réglages", "Addons tiers", "Journal" }
local onglets = {}
for i, nomOnglet in ipairs(NOMS_ONGLETS) do
    local bouton = CreateFrame("Button", "AscensionFROptionsTab" .. i,
        panneau, "CharacterFrameTabButtonTemplate")
    if i == 1 then
        bouton:SetPoint("TOPLEFT", sousTitre, "BOTTOMLEFT", -6, -10)
    else
        -- Léger chevauchement : c'est ainsi que le jeu range ses onglets.
        bouton:SetPoint("LEFT", onglets[i - 1], "RIGHT", -14, 0)
    end
    bouton:SetID(i)
    bouton:SetText(nomOnglet)
    if type(PanelTemplates_TabResize) == "function" then
        PanelTemplates_TabResize(bouton, 0)
    end
    bouton:SetScript("OnClick", function() AfficherOnglet(i) end)
    onglets[i] = bouton
end
if type(PanelTemplates_SetNumTabs) == "function" then
    PanelTemplates_SetNumTabs(panneau, #onglets)
else
    panneau.numTabs = #onglets
end

-- Les quatre pages de contenu, empilées au même endroit ; une seule visible.
-- « AscensionFRJournal » garde son nom historique de la vue journal.
local NOMS_PAGES = {
    "AscensionFROptionsAccueil",
    "AscensionFROptionsReglages",
    "AscensionFROptionsAddonsTiers",
    "AscensionFRJournal",
}
local pages = {}
for i = 1, #NOMS_ONGLETS do
    local page = CreateFrame("Frame", NOMS_PAGES[i], panneau)
    page:SetPoint("TOPLEFT", onglets[1], "BOTTOMLEFT", 6, -6)
    page:SetPoint("BOTTOMRIGHT", panneau, "BOTTOMRIGHT", -16, 12)
    page:Hide()
    pages[i] = page
end
local pageAccueil, pageReglages, pageAddons, pageJournal =
    pages[1], pages[2], pages[3], pages[4]

-- ============================================================================
-- Onglet 1 — ACCUEIL
-- ============================================================================

-- ---- Le grand interrupteur ---------------------------------------------
local caseActif = CreateFrame("CheckButton", "AscensionFROptionsActif",
    pageAccueil, "InterfaceOptionsCheckButtonTemplate")
caseActif:SetPoint("TOPLEFT", pageAccueil, "TOPLEFT", 0, -2)
_G[caseActif:GetName() .. "Text"]:SetText("Activer la traduction")
caseActif.tooltipText = "Décochez pour retrouver le jeu en anglais. "
    .. "Un /reload est nécessaire pour tout rétablir."

-- ---- Le compteur de traductions chargées -------------------------------
local titreBases = pageAccueil:CreateFontString(nil, "ARTWORK", "GameFontNormal")
titreBases:SetPoint("TOPLEFT", caseActif, "BOTTOMLEFT", 2, -8)
titreBases:SetText("Traductions chargées")

-- Deux colonnes : la liste est longue et le panneau étroit.
local lignes = {}
for i = 1, #CATEGORIES do
    local ligne = pageAccueil:CreateFontString(nil, "ARTWORK",
        "GameFontHighlightSmall")
    local colonne = (i - 1) % 2
    local rangee = math.floor((i - 1) / 2)
    ligne:SetPoint("TOPLEFT", titreBases, "BOTTOMLEFT",
        colonne * 230, -6 - rangee * 15)
    ligne:SetJustifyH("LEFT")
    lignes[i] = ligne
end

local total = pageAccueil:CreateFontString(nil, "ARTWORK", "GameFontNormal")
total:SetPoint("TOPLEFT", lignes[#CATEGORIES - 1], "BOTTOMLEFT", 0, -10)

-- ---- État de la récolte ------------------------------------------------
local etat = pageAccueil:CreateFontString(nil, "ARTWORK", "GameFontNormal")
etat:SetPoint("TOPLEFT", total, "BOTTOMLEFT", 0, -14)
etat:SetPoint("RIGHT", pageAccueil, "RIGHT", -8, 0)
etat:SetJustifyH("LEFT")

local etatDetail = pageAccueil:CreateFontString(nil, "ARTWORK",
    "GameFontHighlightSmall")
etatDetail:SetPoint("TOPLEFT", etat, "BOTTOMLEFT", 0, -4)
etatDetail:SetPoint("RIGHT", pageAccueil, "RIGHT", -8, 0)
etatDetail:SetJustifyH("LEFT")
etatDetail:SetJustifyV("TOP")

local signalements = pageAccueil:CreateFontString(nil, "ARTWORK",
    "GameFontHighlightSmall")
signalements:SetPoint("TOPLEFT", etatDetail, "BOTTOMLEFT", 0, -6)
signalements:SetPoint("RIGHT", pageAccueil, "RIGHT", -8, 0)
signalements:SetJustifyH("LEFT")

-- LE bouton principal. Il s'appelait « Aider la traduction » et ouvrait une
-- page de guide dont le vrai but était… ce même rapport : l'intermédiaire a
-- sauté. « Envoyer mes découvertes » ouvre directement le rapport prêt à
-- copier (avec le lien Discord et le bouton pour vider les signalements).
local boutonAider = CreateFrame("Button", nil, pageAccueil,
    "UIPanelButtonTemplate")
boutonAider:SetSize(200, 24)
boutonAider:SetPoint("TOPLEFT", signalements, "BOTTOMLEFT", 0, -8)
boutonAider:SetText("Envoyer mes découvertes")

-- Le chemin FACILE d'abord : le Compagnon envoie tout en un clic. Ce
-- bouton-ci est la méthode manuelle (copier-coller) pour ceux qui ne
-- l'ont pas.
local astuceCompagnon = pageAccueil:CreateFontString(nil, "ARTWORK",
    "GameFontDisableSmall")
astuceCompagnon:SetPoint("LEFT", boutonAider, "RIGHT", 10, 0)
-- bornée au cadre : sans ancre droite, la ligne file hors du panneau (vécu)
astuceCompagnon:SetPoint("RIGHT", pageAccueil, "RIGHT", -16, 0)
astuceCompagnon:SetHeight(24)
astuceCompagnon:SetJustifyH("LEFT")
astuceCompagnon:SetText("Le plus simple : le |cffffd100Compagnon|r envoie "
    .. "tout en un clic. Ici : copier-coller.")
boutonAider:SetScript("OnClick", function()
    if AFR.PartagerJournal then AFR.PartagerJournal() end
end)

-- ---- La ligne d'aide ---------------------------------------------------
local aide = pageAccueil:CreateFontString(nil, "ARTWORK", "GameFontDisableSmall")
aide:SetPoint("TOPLEFT", boutonAider, "BOTTOMLEFT", 0, -10)
aide:SetPoint("RIGHT", pageAccueil, "RIGHT", -8, 0)
aide:SetJustifyH("LEFT")
aide:SetJustifyV("TOP")
aide:SetHeight(72)
aide:SetText("Un texte resté en anglais ? Survolez-le et tapez "
    .. "|cffffff00/afr signaler|r (ou associez-y une touche : Échap -> "
    .. "Raccourcis clavier -> Ascension FR). Puis, après un /reload ou une "
    .. "déconnexion, ouvrez le |cffffff00Hub AscensionFR|r : un clic "
    .. "sur « Envoyer mon rapport » et tout part aider la traduction. Sans "
    .. "le Hub : « Envoyer mes découvertes » ci-dessus, copiez le "
    .. "rapport (Ctrl+C) et collez-le sur le Discord.")

-- ---- Encart « Soutenir le projet » -------------------------------------
-- Un cadre à bordure dorée, chaleureux et digne : l'addon est gratuit, la
-- base de données demande des centaines d'heures — donner envie, jamais
-- culpabiliser. Le lien vit dans NOTRE zone de saisie (même mécanique que la
-- boîte Discord : un addon 3.3.5 ne peut pas écrire dans le presse-papiers,
-- la sélection + Ctrl+C est le seul chemin).
local soutien = CreateFrame("Frame", nil, pageAccueil)
soutien:SetPoint("TOPLEFT", aide, "BOTTOMLEFT", -2, -12)
soutien:SetPoint("RIGHT", pageAccueil, "RIGHT", -8, 0)
soutien:SetHeight(96)
soutien:SetBackdrop({
    bgFile = "Interface\\Tooltips\\UI-Tooltip-Background",
    edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
    tile = true, tileSize = 16, edgeSize = 16,
    insets = { left = 4, right = 4, top = 4, bottom = 4 },
})
soutien:SetBackdropColor(0.09, 0.07, 0.02, 0.92)
soutien:SetBackdropBorderColor(1, 0.82, 0)

local iconeCafe = soutien:CreateTexture(nil, "ARTWORK")
iconeCafe:SetSize(28, 28)
iconeCafe:SetPoint("TOPLEFT", 12, -12)
iconeCafe:SetTexture("Interface\\Icons\\INV_Drink_18")
iconeCafe:SetTexCoord(0.07, 0.93, 0.07, 0.93)

local titreSoutien = soutien:CreateFontString(nil, "ARTWORK", "GameFontNormal")
titreSoutien:SetPoint("TOPLEFT", soutien, "TOPLEFT", 48, -14)
titreSoutien:SetText("Soutenir le projet")

local texteSoutien = soutien:CreateFontString(nil, "ARTWORK",
    "GameFontHighlightSmall")
texteSoutien:SetPoint("TOPLEFT", titreSoutien, "BOTTOMLEFT", 0, -4)
texteSoutien:SetPoint("RIGHT", soutien, "RIGHT", -12, 0)
texteSoutien:SetJustifyH("LEFT")
texteSoutien:SetJustifyV("TOP")
-- 28 = deux lignes maxi : 42 laissait un vide qui poussait le lien hors
-- du cadre doré (vécu, capture de Dan).
texteSoutien:SetHeight(28)
texteSoutien:SetText("Cet addon est gratuit et le restera. S'il vous rend le "
    .. "jeu plus agréable, vous pouvez soutenir son auteur :")

local etiquetteSoutien = soutien:CreateFontString(nil, "ARTWORK",
    "GameFontNormalSmall")
etiquetteSoutien:SetPoint("TOPLEFT", texteSoutien, "BOTTOMLEFT", 0, -8)
etiquetteSoutien:SetText("Ctrl+C pour copier :")

local lienSoutien = CreateFrame("EditBox", "AscensionFRSoutienLien",
    soutien, "InputBoxTemplate")
lienSoutien:SetSize(250, 20)
lienSoutien:SetPoint("LEFT", etiquetteSoutien, "RIGHT", 10, 0)
lienSoutien:SetAutoFocus(false)
lienSoutien:SetText(SOUTIEN_URL)
lienSoutien:SetCursorPosition(0)
lienSoutien:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)
lienSoutien:SetScript("OnEditFocusGained", function(self)
    self:HighlightText()
end)
lienSoutien:SetScript("OnMouseUp", function(self)
    self:SetFocus(); self:HighlightText()
end)
-- Lecture seule de fait : toute frappe est annulée, le lien reste intact.
lienSoutien:SetScript("OnTextChanged", function(self)
    if self:GetText() ~= SOUTIEN_URL then
        self:SetText(SOUTIEN_URL); self:SetCursorPosition(0)
    end
end)

-- ============================================================================
-- Onglet 2 — RÉGLAGES
-- Chaque coupe-circuit avec sa courte ligne d'explication grise, pour que la
-- case se comprenne sans avoir à la survoler.
-- ============================================================================
local function CaseReglage(nomGlobal, ancre, texte, explication, tooltip)
    local case = CreateFrame("CheckButton", nomGlobal, pageReglages,
        "InterfaceOptionsCheckButtonTemplate")
    if ancre then
        -- Sous la ligne grise de la case précédente ; on revient au bord.
        case:SetPoint("TOPLEFT", ancre, "BOTTOMLEFT", -26, -8)
    else
        case:SetPoint("TOPLEFT", pageReglages, "TOPLEFT", 0, -4)
    end
    _G[nomGlobal .. "Text"]:SetText(texte)
    case.tooltipText = tooltip
    local ligne = pageReglages:CreateFontString(nil, "ARTWORK",
        "GameFontDisableSmall")
    ligne:SetPoint("TOPLEFT", case, "BOTTOMLEFT", 26, 4)
    ligne:SetPoint("RIGHT", pageReglages, "RIGHT", -8, 0)
    ligne:SetJustifyH("LEFT")
    ligne:SetJustifyV("TOP")
    -- Deux lignes possibles : sans hauteur, la police coupe avec « … ».
    ligne:SetHeight(24)
    ligne:SetText(explication)
    case.explication = ligne
    return case
end

-- Clé sansInterception, À L'ENVERS : coché = la clé n'existe pas = traduit.
-- C'est l'interrupteur d'enquête d'Epreuves.lua, promu en vraie case.
local caseInterface = CaseReglage("AscensionFROptionsInterface", nil,
    "Traduire l'interface",
    "Les fenêtres propres à Ascension : Épreuves, hauts faits, collections, "
        .. "menus... Effet immédiat, dans les deux sens.",
    "Décochez pour laisser l'interface d'Ascension en anglais, sans toucher "
        .. "au reste (quêtes, sorts, objets...).\n\nPratique pour vérifier "
        .. "si un souci d'affichage vient de l'addon ou du jeu.")

-- Clé sansPlaques, À L'ENVERS elle aussi : absence = activé.
-- Le module Modules\Plaques.lua la lit à chaque balayage.
local casePlaques = CaseReglage("AscensionFROptionsPlaques",
    caseInterface.explication,
    "Traduire les plaques de nom des monstres",
    "Le nom affiché au-dessus des créatures dans le monde. Décocher agit "
        .. "sur les nouvelles plaques ; /reload pour tout ravoir en anglais.",
    "Actif par défaut. Remplace le nom anglais des plaques de nom par le "
        .. "français (« Grellkin » devient « Grellide »).")

local caseBarresDeVie = CaseReglage("AscensionFROptionsBarresDeVie",
    casePlaques.explication,
    "Traduire les noms au-dessus des monstres",
    "Ancienne méthode, coupée par défaut. À laisser décochée avec un addon "
        .. "de barres de vie — précautions en survol.",
    "Désactivé par défaut. Traduit le nom affiché "
        .. "au-dessus des créatures.\n\nÀ n'activer que si vous n'utilisez AUCUN "
        .. "addon de barres de vie (PlateBuffs, Kui_Nameplates, TidyPlates, "
        .. "Aloft, ElvUI...) : la combinaison peut figer le jeu "
        .. "(« C stack overflow »).\n\nSi un tel addon est détecté, la traduction "
        .. "reste inactive même en cochant.")

local caseMinimap = CaseReglage("AscensionFROptionsMinimap",
    caseBarresDeVie.explication,
    "Bouton près de la minimap",
    "Le petit livre au bord de la minimap : l'état en survol, ce panneau en "
        .. "un clic. Il se déplace en le faisant glisser.",
    "L'état de la traduction en survol, ce panneau en "
        .. "un clic. Faites-le glisser pour le déplacer autour de la minimap.")

local caseCanalFr = CaseReglage("AscensionFROptionsCanalFr",
    caseMinimap.explication,
    "Canal AscensionFR",
    "Te met dans un salon commun avec tous les francophones qui ont l'addon "
        .. "— pour être sûr de trouver du monde qui parle français.",
    "Rejoint automatiquement le canal « AscensionFR », un salon commun à tous "
        .. "les francophones qui ont l'addon.\n\nPratique pour trouver du "
        .. "monde qui parle ta langue sur un serveur surtout anglophone.\n\n"
        .. "Décocher te retire du canal (comme /afrcanal off).")

local caseDebug = CaseReglage("AscensionFROptionsDebug",
    caseCanalFr.explication,
    "Messages de débogage",
    "Recopie le journal de l'addon dans le chat, en direct. Tout se lit "
        .. "déjà dans l'onglet « Journal ».",
    "Recopie aussi le journal dans le chat. Sans cocher "
        .. "ceci, tout se lit déjà dans l'onglet « Journal ».")

-- ============================================================================
-- Onglet 3 — ADDONS TIERS
-- Construit depuis le registre ADDONS_TIERS (en tête de fichier). Les cases
-- restent visibles même quand l'addon est absent — grisées, pour que chacun
-- sache que la prise en charge existe.
-- ============================================================================
local introAddons = pageAddons:CreateFontString(nil, "ARTWORK",
    "GameFontHighlightSmall")
introAddons:SetPoint("TOPLEFT", pageAddons, "TOPLEFT", 0, -4)
introAddons:SetPoint("RIGHT", pageAddons, "RIGHT", -8, 0)
introAddons:SetJustifyH("LEFT")
introAddons:SetJustifyV("TOP")
-- hauteur pour DEUX lignes : sans elle, la police coupe avec « … » (vécu)
introAddons:SetHeight(26)
introAddons:SetText("Ces addons sont l'œuvre d'autres auteurs ; AscensionFR "
    .. "les met en français sans toucher à leurs fichiers.")

local sectionsAddons = {}
do
    local ancre, decalX = introAddons, 0
    for _, defAddon in ipairs(ADDONS_TIERS) do
        local entete = pageAddons:CreateFontString(nil, "ARTWORK",
            "GameFontNormal")
        entete:SetPoint("TOPLEFT", ancre, "BOTTOMLEFT", decalX, -14)
        entete:SetText(defAddon.nom)
        -- Le badge (installé/absent) est rempli par Rafraichir.
        local badge = pageAddons:CreateFontString(nil, "ARTWORK",
            "GameFontHighlightSmall")
        badge:SetPoint("LEFT", entete, "RIGHT", 8, 0)
        local section = { def = defAddon, badge = badge, cases = {} }
        ancre, decalX = entete, 0
        for _, defCase in ipairs(defAddon.cases) do
            local case = CreateFrame("CheckButton", defCase.nomGlobal,
                pageAddons, "InterfaceOptionsCheckButtonTemplate")
            case:SetPoint("TOPLEFT", ancre, "BOTTOMLEFT", decalX, -6)
            _G[defCase.nomGlobal .. "Text"]:SetText(defCase.texte)
            case.tooltipText = defCase.tooltip
            local info = pageAddons:CreateFontString(nil, "ARTWORK",
                "GameFontDisableSmall")
            info:SetPoint("TOPLEFT", case, "BOTTOMLEFT", 26, 4)
            info:SetPoint("RIGHT", pageAddons, "RIGHT", -8, 0)
            info:SetJustifyH("LEFT")
            info:SetJustifyV("TOP")
            -- Deux lignes possibles : sans hauteur, la police coupe.
            info:SetHeight(24)
            info:SetText(defCase.info)
            case:SetScript("OnClick", function(self)
                local opt = OptionsSauvees()
                if defCase.inversee then
                    opt[defCase.cle] = (not self:GetChecked()) or nil
                else
                    opt[defCase.cle] = self:GetChecked() and true or nil
                end
                if defCase.auClic then
                    defCase.auClic(self:GetChecked() and true or false)
                end
                Rafraichir()
            end)
            table.insert(section.cases, { case = case, def = defCase })
            ancre, decalX = info, -26
        end
        table.insert(sectionsAddons, section)
    end
end

-- ============================================================================
-- Onglet 4 — JOURNAL
-- La console de l'addon (AFR.Debug l'alimente en permanence ; la case
-- « Messages de débogage » ne gouverne que la copie dans le chat), et le
-- bloc signalement en un bouton : « Préparer le rapport » ouvre la fenêtre
-- avec le rapport à copier, la boîte Discord (Ctrl+C) et le bouton pour
-- vider les signalements.
-- ============================================================================
local introJournal = pageJournal:CreateFontString(nil, "ARTWORK",
    "GameFontHighlightSmall")
introJournal:SetPoint("TOPLEFT", pageJournal, "TOPLEFT", 0, -4)
introJournal:SetPoint("RIGHT", pageJournal, "RIGHT", -8, 0)
introJournal:SetJustifyH("LEFT")
introJournal:SetText("Ce que l'addon fait ou écarte, en direct. "
    .. "Molette pour faire défiler.")

local console = CreateFrame("ScrollingMessageFrame", nil, pageJournal)
console:SetPoint("TOPLEFT", introJournal, "BOTTOMLEFT", 0, -8)
console:SetPoint("BOTTOMRIGHT", pageJournal, "BOTTOMRIGHT", -8, 38)
if GameFontHighlightSmall then
    console:SetFontObject(GameFontHighlightSmall)
end
console:SetJustifyH("LEFT")
console:SetFading(false)
console:SetMaxLines(300)
console:EnableMouseWheel(true)
console:SetScript("OnMouseWheel", function(self, delta)
    if delta > 0 then self:ScrollUp() else self:ScrollDown() end
end)

pageJournal:SetScript("OnShow", function()
    console:Clear()
    for _, message in ipairs(AFR.Journal) do
        console:AddMessage(message)
    end
end)

-- Affichage en direct quand la console est sous les yeux.
AFR.JournalEcoute = function(message)
    if console:IsVisible() then console:AddMessage(message) end
end

local boutonRapport = CreateFrame("Button", nil, pageJournal,
    "UIPanelButtonTemplate")
boutonRapport:SetSize(190, 24)
boutonRapport:SetPoint("BOTTOMLEFT", pageJournal, "BOTTOMLEFT", 0, 6)
boutonRapport:SetText("Préparer le rapport")
boutonRapport:SetScript("OnClick", function()
    if AFR.PartagerJournal then AFR.PartagerJournal() end
end)

local infoRapport = pageJournal:CreateFontString(nil, "ARTWORK",
    "GameFontDisableSmall")
infoRapport:SetPoint("LEFT", boutonRapport, "RIGHT", 10, 0)
infoRapport:SetPoint("RIGHT", pageJournal, "RIGHT", -8, 0)
infoRapport:SetJustifyH("LEFT")
infoRapport:SetHeight(28)
infoRapport:SetText("Le rapport à copier (Ctrl+C), le lien Discord, et de "
    .. "quoi vider les signalements.")

-- ----------------------------------------------------------------------------
-- Rafraîchissement — tout l'état visible, quel que soit l'onglet ouvert.
-- ----------------------------------------------------------------------------
Rafraichir = function()
    local opt = OptionsSauvees()

    -- Accueil.
    caseActif:SetChecked(AFR.Actif())

    -- Réglages. Deux clés à l'envers (sansInterception, sansPlaques) :
    -- coché = la clé n'existe pas.
    caseInterface:SetChecked(not opt.sansInterception)
    casePlaques:SetChecked(not opt.sansPlaques)
    caseBarresDeVie:SetChecked(opt.barresDeVie and true or false)
    caseMinimap:SetChecked(not opt.minimapCache)
    caseCanalFr:SetChecked(not opt.sansCanalFrancais)
    caseDebug:SetChecked(opt.debug and true or false)

    -- Addons tiers : badge, cases cochées, grisage si l'addon est absent.
    for _, section in ipairs(sectionsAddons) do
        local installe = section.def.estLa()
        section.badge:SetText(installe and "|cff00ff00installé|r"
            or "|cff808080absent|r")
        for _, c in ipairs(section.cases) do
            if c.def.inversee then
                c.case:SetChecked(not opt[c.def.cle])
            else
                c.case:SetChecked(opt[c.def.cle] and true or false)
            end
            if installe then c.case:Enable() else c.case:Disable() end
            c.case:SetAlpha(installe and 1 or 0.45)
            local etiquette = _G[c.def.nomGlobal .. "Text"]
            local police = installe and GameFontHighlightLeft
                or GameFontDisableLeft
            if etiquette and police then
                etiquette:SetFontObject(police)
            end
        end
    end

    -- Le compteur de traductions chargées.
    local somme = 0
    for i, categorie in ipairs(CATEGORIES) do
        local n = Compter(categorie[1])
        somme = somme + n
        if n > 0 then
            lignes[i]:SetText(string.format("%s : |cffffffff%d|r",
                categorie[2], n))
        else
            lignes[i]:SetText("|cff808080" .. categorie[2] .. " : —|r")
        end
    end
    total:SetText(string.format("Total : |cffffff00%d|r traductions", somme))

    -- Ce compteur a fait croire deux fois à une panne d'envoi (19/07/2026).
    -- Ce n'est PAS une file d'attente : c'est ce qui n'est pas encore traduit
    -- CHEZ VOUS. Il ne descend pas quand on envoie son rapport, mais quand
    -- les traductions arrivent. Le vocabulaire doit le dire.
    local attente = TotalRecolte()
    if attente > 0 then
        etat:SetText(string.format(
            "|cffff9900%d|r textes pas encore traduits chez vous", attente))
        etatDetail:SetText("L'addon les a notés tout seul. Ils partiront "
            .. "avec votre prochain rapport, et repasseront en français "
            .. "à une prochaine mise à jour. Rien à faire de particulier.")
    else
        etat:SetText("|cff00ff00Tout ce que vous avez croisé est traduit.|r")
        etatDetail:SetText("Explorez de nouvelles zones pour que l'addon "
            .. "découvre du contenu inédit.")
    end

    local n = AFR.NombreSignalements and AFR.NombreSignalements() or 0
    if n > 0 then
        signalements:SetText(string.format(
            "|cffff9900%d|r souci(s) signalé(s) par vous, à partager aussi.",
            n))
    else
        signalements:SetText("")
    end
end

-- Bascule d'onglet : montre la bonne page, marque le bon bouton.
AfficherOnglet = function(i)
    if type(PanelTemplates_SetTab) == "function" and panneau.numTabs then
        PanelTemplates_SetTab(panneau, i) -- l'état visuel des boutons
    else
        panneau.selectedTab = i
    end
    for k, page in ipairs(pages) do
        if k == i then page:Show() else page:Hide() end
    end
    Rafraichir()
end

-- ----------------------------------------------------------------------------
-- Poignées de clic des réglages
-- ----------------------------------------------------------------------------
caseActif:SetScript("OnClick", function(self)
    local opt = OptionsSauvees()
    opt.desactive = not self:GetChecked() or nil
    if self:GetChecked() then
        print("|cff0099ffAscensionFR|r : traduction activée (/reload conseillé).")
    else
        print("|cff0099ffAscensionFR|r : traduction désactivée "
            .. "(/reload pour tout rétablir en anglais).")
    end
    Rafraichir()
end)

caseInterface:SetScript("OnClick", function(self)
    local opt = OptionsSauvees()
    opt.sansInterception = (not self:GetChecked()) or nil
    print("|cff0099ffAscensionFR|r : interface d'Ascension "
        .. (self:GetChecked() and "traduite." or "laissée en anglais."))
    Rafraichir()
end)

casePlaques:SetScript("OnClick", function(self)
    local opt = OptionsSauvees()
    opt.sansPlaques = (not self:GetChecked()) or nil
    print("|cff0099ffAscensionFR|r : plaques de nom "
        .. (self:GetChecked() and "traduites."
            or "laissées en anglais (/reload pour les déjà traduites)."))
    Rafraichir()
end)

caseBarresDeVie:SetScript("OnClick", function(self)
    local opt = OptionsSauvees()
    -- La case a changé de sens en 1.7.5 : elle ACTIVE désormais la fonction,
    -- au lieu de la désactiver. L'ancienne clé « desactiverBarresDeVie » est
    -- abandonnée, ce qui remet tout le monde sur le réglage sûr (inactif).
    opt.barresDeVie = self:GetChecked() and true or nil
    Rafraichir()
end)

caseMinimap:SetScript("OnClick", function(self)
    if AFR.MinimapVisible then
        AFR.MinimapVisible(self:GetChecked() and true or false)
    end
end)

caseCanalFr:SetScript("OnClick", function(self)
    local opt = OptionsSauvees()
    -- Clé À L'ENVERS : coché = on VEUT le canal = pas de clé « sans ».
    opt.sansCanalFrancais = (not self:GetChecked()) or nil
    -- Effet immédiat : on rejoint ou on quitte tout de suite.
    if AFR.CanalFrancais then
        if self:GetChecked() then AFR.CanalFrancais.rejoindre()
        else AFR.CanalFrancais.quitter() end
    end
end)

caseDebug:SetScript("OnClick", function(self)
    local opt = OptionsSauvees()
    opt.debug = self:GetChecked() and true or nil
    Rafraichir()
end)

-- ----------------------------------------------------------------------------
-- Enregistrement du panneau (une seule catégorie désormais : les anciennes
-- sous-catégories sont devenues des onglets).
-- ----------------------------------------------------------------------------
panneau.refresh = Rafraichir
panneau:SetScript("OnShow", function()
    AfficherOnglet(panneau.selectedTab or 1)
end)

-- État de départ : l'Accueil, sans passer par Rafraichir (les SavedVariables
-- n'existent pas encore au chargement du fichier).
panneau.selectedTab = 1
pageAccueil:Show()

if type(InterfaceOptions_AddCategory) == "function" then
    InterfaceOptions_AddCategory(panneau)
end

-- Compat : l'ancienne sous-catégorie « Aider la traduction » n'existe plus ;
-- tout ce qu'elle offrait vit dans le panneau lui-même.
AFR.PanneauAide = panneau

-- ----------------------------------------------------------------------------
-- Partage du journal — la fenêtre « Signaler un souci »
--
-- Un addon 3.3.5 ne peut pas écrire dans le presse-papiers : le seul chemin
-- est une zone de saisie dont le texte est présélectionné, que le joueur
-- copie avec Ctrl+C. On y joint le contexte (version, client, comptes) et
-- les rubriques de détail, pour que le rapport se suffise à lui-même.
-- ----------------------------------------------------------------------------
local fenetreCopie = CreateFrame("Frame", "AscensionFRCopie", UIParent)
fenetreCopie:SetSize(620, 440)
fenetreCopie:SetPoint("CENTER")
fenetreCopie:SetFrameStrata("FULLSCREEN_DIALOG")
fenetreCopie:SetBackdrop({
    bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
    edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
    tile = true, tileSize = 32, edgeSize = 32,
    insets = { left = 11, right = 12, top = 12, bottom = 11 },
})
fenetreCopie:EnableMouse(true)
fenetreCopie:SetMovable(true)
fenetreCopie:RegisterForDrag("LeftButton")
fenetreCopie:SetScript("OnDragStart", fenetreCopie.StartMoving)
fenetreCopie:SetScript("OnDragStop", fenetreCopie.StopMovingOrSizing)
fenetreCopie:Hide()
-- Échap ferme la fenêtre, comme toute fenêtre du jeu.
if type(UISpecialFrames) == "table" then
    table.insert(UISpecialFrames, "AscensionFRCopie")
end

local titreCopie = fenetreCopie:CreateFontString(nil, "ARTWORK",
    "GameFontNormal")
titreCopie:SetPoint("TOP", 0, -16)
titreCopie:SetText("Signaler un souci — Ascension |cff0099ffFR|r")

local aideCopie = fenetreCopie:CreateFontString(nil, "ARTWORK",
    "GameFontHighlightSmall")
aideCopie:SetPoint("TOP", titreCopie, "BOTTOM", 0, -6)
-- bornée à la fenêtre : ancre centrale seule = largeur illimitée (vécu)
aideCopie:SetPoint("LEFT", fenetreCopie, "LEFT", 16, 0)
aideCopie:SetPoint("RIGHT", fenetreCopie, "RIGHT", -16, 0)
aideCopie:SetJustifyH("CENTER")
aideCopie:SetHeight(42)
aideCopie:SetText("Votre rapport est prêt ci-dessous. |cffffff00Ctrl+C|r pour "
    .. "le copier, puis collez-le sur le Discord. (Plus simple : le Compagnon "
    .. "AscensionFR envoie ce rapport en un clic.) |cffffff00Échap|r ferme.")

-- Le lien du Discord, copiable (Ctrl+C) : un addon ne peut ni ouvrir un
-- navigateur ni écrire dans le presse-papiers ; une zone de saisie
-- présélectionnée est le seul chemin.
local etiquetteDiscord = fenetreCopie:CreateFontString(nil, "ARTWORK",
    "GameFontNormalSmall")
etiquetteDiscord:SetPoint("TOPLEFT", 20, -56)
etiquetteDiscord:SetText("Discord (Ctrl+C) :")

local lienDiscord = CreateFrame("EditBox", "AscensionFRLienDiscord",
    fenetreCopie, "InputBoxTemplate")
lienDiscord:SetSize(340, 20)
lienDiscord:SetPoint("LEFT", etiquetteDiscord, "RIGHT", 10, 0)
lienDiscord:SetAutoFocus(false)
lienDiscord:SetText(DISCORD)
lienDiscord:SetCursorPosition(0)
lienDiscord:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)
lienDiscord:SetScript("OnEditFocusGained", function(self) self:HighlightText() end)
lienDiscord:SetScript("OnMouseUp", function(self)
    self:SetFocus(); self:HighlightText()
end)
-- Lecture seule de fait : toute frappe est annulée, le lien reste intact.
lienDiscord:SetScript("OnTextChanged", function(self)
    if self:GetText() ~= DISCORD then
        self:SetText(DISCORD); self:SetCursorPosition(0)
    end
end)

local defilementCopie = CreateFrame("ScrollFrame", "AscensionFRCopieScroll",
    fenetreCopie, "UIPanelScrollFrameTemplate")
defilementCopie:SetPoint("TOPLEFT", 18, -88)
defilementCopie:SetPoint("BOTTOMRIGHT", -38, 44)

local zoneCopie = CreateFrame("EditBox", "AscensionFRCopieZone",
    defilementCopie)
zoneCopie:SetMultiLine(true)
zoneCopie:SetAutoFocus(false)
zoneCopie:SetWidth(560)
zoneCopie:SetHeight(4000)
if ChatFontNormal then zoneCopie:SetFontObject(ChatFontNormal) end
zoneCopie:SetScript("OnEscapePressed", function() fenetreCopie:Hide() end)
defilementCopie:SetScrollChild(zoneCopie)

local fermerCopie = CreateFrame("Button", nil, fenetreCopie,
    "UIPanelButtonTemplate")
fermerCopie:SetSize(100, 22)
fermerCopie:SetPoint("BOTTOM", 95, 16)
fermerCopie:SetText("Fermer")
fermerCopie:SetScript("OnClick", function() fenetreCopie:Hide() end)

-- Vider les signalements en attente, une fois le rapport copié. Le compteur du
-- panneau ne se remet plus à zéro tout seul (on ne purge plus au /reload, pour
-- ne pas effacer les retours d'un ami non encore transmis) : ce bouton rend la
-- main à l'utilisateur.
local viderCopie = CreateFrame("Button", nil, fenetreCopie,
    "UIPanelButtonTemplate")
viderCopie:SetSize(190, 22)
viderCopie:SetPoint("RIGHT", fermerCopie, "LEFT", -10, 0)
viderCopie:SetText("Vider les signalements")
viderCopie:SetScript("OnClick", function()
    if AFR.ViderSignalements then AFR.ViderSignalements() end
end)

-- Le contexte technique : sans lui, un journal partagé est une énigme.
local function Contexte()
    local lignesContexte = {}
    local version = type(GetAddOnMetadata) == "function"
        and GetAddOnMetadata("AscensionFR", "Version") or "?"
    table.insert(lignesContexte, "AscensionFR " .. tostring(version))
    if type(GetBuildInfo) == "function" then
        local jeu, build = GetBuildInfo()
        table.insert(lignesContexte, "Client : " .. tostring(jeu)
            .. " (" .. tostring(build) .. ")"
            .. (type(GetLocale) == "function"
                and " / " .. GetLocale() or ""))
    end
    -- Même total exact et sûr que la Minimap (AFR.TotalTraductions). L'ancien
    -- pairs(AFR.DB) plantait sur le nombre gravé ; repli gardé par type().
    local somme
    if type(AFR.TotalTraductions) == "function" then
        somme = AFR.TotalTraductions()
    else
        somme = 0
        for _, t in pairs(AFR.DB) do
            if type(t) == "table" then
                for _ in pairs(t) do somme = somme + 1 end
            end
        end
    end
    table.insert(lignesContexte, "Traductions chargées : " .. somme)
    table.insert(lignesContexte, "Traduction : "
        .. (AFR.Actif() and "activée" or "désactivée"))
    local attente = type(NombreRecoltes) == "function" and NombreRecoltes() or 0
    table.insert(lignesContexte, "En attente : " .. attente
        .. " texte(s) récolté(s), "
        .. (AFR.NombreSignalements and AFR.NombreSignalements() or 0)
        .. " signalement(s)")
    return lignesContexte
end

-- Le cœur du rapport : les données réellement exploitables. Elles vivent dans
-- AscensionFRSaved (disque), pas dans le journal de session — sans ce déballage
-- le rapport copié n'a que des compteurs. On les met EN TÊTE, avant le journal.
local PLAFOND_RECOLTE = 60

-- Chaque signalement : type + ID + toutes les lignes de l'info-bulle
-- photographiée (gauche, et droite entre crochets). C'est ce qui donne
-- « sort #48512 : <texte anglais> », directement traduisible.
local function AjouterSignalements(blocs)
    local liste = AscensionFRSaved and AscensionFRSaved.Signalements
    if not liste or #liste == 0 then return end
    table.insert(blocs, "")
    table.insert(blocs, "--- Signalements (" .. #liste .. ") ---")
    for _, s in ipairs(liste) do
        local entete = tostring(s.T or "?")
        if s.ID then entete = entete .. " #" .. tostring(s.ID) end
        if s.Q then entete = entete .. "  (" .. s.Q .. ")" end
        table.insert(blocs, entete)
        if s.N and s.N ~= "" then
            table.insert(blocs, "  note : " .. s.N)
        end
        if type(s.L) == "table" then
            for i = 1, #s.L do
                local g = s.L[i] or ""
                local d = (s.R and s.R[i]) or ""
                if g ~= "" and d ~= "" then
                    table.insert(blocs, "  " .. g .. "   [" .. d .. "]")
                elseif g ~= "" then
                    table.insert(blocs, "  " .. g)
                elseif d ~= "" then
                    table.insert(blocs, "  [" .. d .. "]")
                end
            end
        end
    end
end

-- Les échecs d'alignement : un texte connu des bases qui refuse de se traduire
-- (format @...@, variables). ID + texte, par genre (S sorts, O objets).
local function AjouterEchecs(blocs)
    local j = AscensionFRSaved and AscensionFRSaved.EchecsAlignement
    if type(j) ~= "table" then return end
    for genre, entrees in pairs(j) do
        local ids = {}
        for id in pairs(entrees) do table.insert(ids, id) end
        if #ids > 0 then
            table.insert(blocs, "")
            table.insert(blocs, "--- Échecs d'alignement " .. tostring(genre)
                .. " (" .. #ids .. ") ---")
            for _, id in ipairs(ids) do
                local v = entrees[id]
                if type(v) == "table" then
                    table.insert(blocs, tostring(id) .. " :")
                    for _, ligne in ipairs(v) do
                        table.insert(blocs, "  " .. tostring(ligne))
                    end
                else
                    table.insert(blocs, tostring(id) .. " : " .. tostring(v))
                end
            end
        end
    end
end

-- La récolte : tous les textes rencontrés sans traduction. Plafonnée pour ne
-- pas produire un pavé impartageable ; au-delà, on renvoie vers le fichier.
local function AjouterRecolte(blocs)
    local r = AscensionFRSaved and AscensionFRSaved.Recolte
    if type(r) ~= "table" then return end
    local totalRecolte = 0
    for _, cat in pairs(r) do
        for _ in pairs(cat) do totalRecolte = totalRecolte + 1 end
    end
    if totalRecolte == 0 then return end
    table.insert(blocs, "")
    table.insert(blocs, "--- Récolte : rencontrés sans traduction ("
        .. totalRecolte .. ") ---")
    local montres = 0
    for categorie, entrees in pairs(r) do
        for cle, valeur in pairs(entrees) do
            if montres >= PLAFOND_RECOLTE then break end
            local ligne = "[" .. tostring(categorie) .. "] " .. tostring(cle)
            -- Le texte anglais récolté (quêtes surtout) part AVEC la ligne :
            -- sans lui, le rapport ne donnait que des numéros intraduisibles.
            if type(valeur) == "string" and valeur ~= "" then
                ligne = ligne .. " ==> " .. string.sub(valeur, 1, 900)
            end
            table.insert(blocs, ligne)
            montres = montres + 1
        end
        if montres >= PLAFOND_RECOLTE then break end
    end
    if totalRecolte > montres then
        table.insert(blocs, "... +" .. (totalRecolte - montres)
            .. " autres — pour tout, envoie le fichier "
            .. "WTF\\Account\\<compte>\\SavedVariables\\AscensionFRSaved.lua")
    end
end

local function TexteAPartager()
    local blocs = { "Signalement Ascension FR — à coller sur " .. DISCORD, "" }
    for _, ligne in ipairs(Contexte()) do table.insert(blocs, ligne) end
    -- D'abord l'exploitable (IDs + textes anglais), ensuite le journal.
    AjouterSignalements(blocs)
    AjouterEchecs(blocs)
    AjouterRecolte(blocs)
    table.insert(blocs, "")
    table.insert(blocs, "--- Journal (" .. #AFR.Journal .. " lignes) ---")
    for _, message in ipairs(AFR.Journal) do
        table.insert(blocs, message)
    end
    for rubrique, lignesRubrique in pairs(AFR.Details) do
        table.insert(blocs, "")
        table.insert(blocs, "--- " .. rubrique
            .. " (" .. #lignesRubrique .. ") ---")
        for _, ligne in ipairs(lignesRubrique) do
            table.insert(blocs, ligne)
        end
    end
    return table.concat(blocs, "\n")
end

function AFR.PartagerJournal()
    zoneCopie:SetText(TexteAPartager())
    zoneCopie:HighlightText()
    zoneCopie:SetFocus()
    fenetreCopie:Show()
end

-- Efface les signalements en attente et rafraîchit le panneau. Les échecs
-- d'alignement, eux, se soignent seuls (AFR.OublierEchec quand un texte se
-- remet à traduire) et n'affichent pas de compteur : on ne touche donc qu'aux
-- signalements, ce que montre le panneau.
function AFR.ViderSignalements()
    AscensionFRSaved = AscensionFRSaved or {}
    local n = AFR.NombreSignalements and AFR.NombreSignalements() or 0
    AscensionFRSaved.Signalements = {}
    print(string.format(
        "|cff0099ffAscensionFR|r : %d signalement(s) vidé(s).", n))
    Rafraichir()
    fenetreCopie:Hide()
end

-- Ouvre le panneau. InterfaceOptionsFrame_OpenToCategory de 3.3.5 n'ouvre pas
-- la bonne catégorie au premier appel : on l'appelle deux fois, comme le font
-- tous les addons de l'époque.
function AFR.OuvrirOptions()
    if type(InterfaceOptionsFrame_OpenToCategory) ~= "function" then
        print("|cff0099ffAscensionFR|r : panneau d'options indisponible ; "
            .. "utilisez /afr on | off | debug.")
        return
    end
    InterfaceOptionsFrame_OpenToCategory(panneau)
    InterfaceOptionsFrame_OpenToCategory(panneau)
end
