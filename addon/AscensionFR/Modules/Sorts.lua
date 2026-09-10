-- ============================================================================
-- AscensionFR - Sorts
--
-- Les descriptions des sorts contiennent des variables ($s1 dégâts, $d durée,
-- $t1 intervalle...) que le CLIENT résout lui-même avant l'affichage. On ne
-- peut donc pas écrire bêtement la description française : « inflige $s1
-- dégâts » s'afficherait tel quel.
--
-- Méthode : la base fournit le modèle anglais (DE) en plus du texte français
-- (D). On aligne le modèle anglais sur l'info-bulle réellement affichée pour
-- récupérer les valeurs calculées par le client, puis on les replace dans le
-- modèle français.
--
--   modèle EN  : "Shock an enemy for $s1 Nature damage over $d."
--   affiché EN : "Shock an enemy for 15 Nature damage over 6 sec."
--                 -> $s1 = "15", $d = "6 sec"
--   modèle FR  : "Choque un ennemi, infligeant $s1 dégâts de Nature en $d."
--   résultat   : "Choque un ennemi, infligeant 15 dégâts de Nature en 6 sec."
-- ============================================================================
local AFR = AscensionFR

-- Échecs d'alignement déjà signalés dans le chat, par identifiant de sort.
-- Une info-bulle se redessine en continu tant qu'on la survole — et un buff
-- permanent la redessine sans arrêt. Sans cette mémoire, le même message
-- inonde le chat en mode débogage (vécu sur le sort 807729). Une ligne par
-- sort et par session suffit à diagnostiquer ; le journal détaillé destiné
-- au Compagnon, lui, continue d'être tenu à jour à chaque passage.
local echecsSignales = {}

-- Coupe-circuit des alignements : [id] = longueur totale du contenu de la
-- bulle au dernier ÉCHEC. Tant que le contenu ne change pas (mêmes
-- longueurs), on ne refait pas le calcul — il échouerait pareil. Un
-- contenu qui bouge (rang appris, valeurs recalculées) relance l'essai.
local echecsRecents = {}

-- Motifs des variables de sorts. Les motifs Lua ne connaissent pas
-- l'alternance : on les essaie un par un et on retient la correspondance la
-- plus précoce (la plus longue en cas d'égalité).
-- Recensées sur les 36 000 sorts réels du serveur (outils/auditer_sorts.py),
-- pas devinées : ne lister que les formes attendues laissait 5 % des modèles
-- inalignables, donc autant de descriptions bloquées en anglais.
local MOTIFS_VARIABLE = {
    "%$%b{}",                       -- ${ calcul }
    "%$%?[^%[]*%b[]%b[]",           -- $?condition[oui][non]
    "%$%?[^%[]*%b[]",               -- $?condition[texte]
    "%$[/%*%+%-]%d+;%d*%a%d*",      -- $/1000;s1 $*15;s1 $+100;s1 (opérations)
    "%$[GgLl][^;]*;",               -- $gm:f;  $lseconde:secondes;
    "%$@%a+",                       -- $@spellname
    "%$<%a+>",                      -- $<percent> $<mult>  (variable nommée)
    "%$%d+%a%d*",                   -- $64843s2  (valeur d'un autre sort)
    "%$%a%d*",                      -- $s1 $d $h $u $t $o $q $a $x $e $z $F...
    "%$%d+",                        -- $1

    -- Marquage maison d'Ascension, résolu par LEUR client avant affichage.
    -- On le traite comme des variables : la capture absorbe ce que le client
    -- a affiché à la place (rien pour @ext:, la description insérée pour
    -- @s:...), sans qu'on ait à imiter son rendu. 3 646 sorts traduits
    -- restaient en anglais parce que ces marqueurs cassaient l'alignement.
    "@ifknown:.-:ifknown@",         -- texte conditionnel (si sort connu)
    "@ifnotknown:.-:ifnotknown@",
    "@wflocation:[^@]*@",           -- indice de localisation Worldforge
    "@%a+:%d+:%-?%d+@",             -- @s:101087:0@  @re:81298:0@ (insertion)
    "@%a+:%d+:%a+@",                -- @req:1122520:req@
    "@%a+:%d+@",                    -- @req:8921@ @unlockby:635@ @learns:...
    "@ext:",                        -- ouverture de bloc d'info étendue
    ":ext@",                        -- fermeture
}

-- Échappe les caractères spéciaux des motifs Lua.
local function echapper(texte)
    return (string.gsub(texte, "([%^%$%(%)%%%.%[%]%*%+%-%?])", "%%%1"))
end

-- Retire les codes couleur |cAARRGGBB...|r. Ils sont cosmétiques et le client
-- d'Ascension ne les affiche pas toujours sur ses sorts custom : les garder
-- dans le modèle EN alors que l'affiché en est dépourvu cassait l'alignement.
-- On les retire des deux côtés AVANT d'aligner ; le résultat français, lui,
-- vient du modèle FR NON dénudé, donc il garde ses propres couleurs.
local function retirer_couleurs(texte)
    if not texte then return texte end
    texte = string.gsub(texte, "|c%x%x%x%x%x%x%x%x", "")
    return (string.gsub(texte, "|r", ""))
end

-- Échappe un littéral en rendant SOUPLE son espace de tête et de queue (`%s*`).
-- Quand un bloc conditionnel (@ifknown, $?s...[..][..]) se résout à vide, le
-- client fait aussi disparaître les sauts de ligne qui l'entouraient ; un
-- espace rigide laissait alors toute la description en anglais (vécu :
-- « Flammes de Xoroth », bloc @ifknown final non appris). Le cœur du littéral
-- reste, lui, strict.
local function echapper_souple(litteral)
    if litteral == "" then return "" end
    -- Séparateur ENTIÈREMENT blanc entre deux variables : il doit rester
    -- EXIGÉ (%s+, pas %s*). Sinon, avec des captures paresseuses, « $s1 $s2 »
    -- sur « 15 20 » donne $s1="" et $s2="15 20" — un nombre dans le mauvais
    -- champ, qu'aucun garde-fou n'attrape. Le cas du bloc conditionnel rendu
    -- vide passe, lui, par le %s* de tête/queue d'un littéral PORTEUR de texte
    -- (voir plus bas), pas par un séparateur tout blanc.
    if string.find(litteral, "^%s*$") then return "%s+" end
    local coeur = string.match(litteral, "^%s*(.-)%s*$")
    local motif = echapper(coeur)
    if string.find(litteral, "^%s") then motif = "%s*" .. motif end
    if string.find(litteral, "%s$") then motif = motif .. "%s*" end
    return motif
end

-- Cherche la prochaine variable à partir de `position`.
local function prochaine_variable(modele, position)
    local meilleur_debut, meilleur_fin
    for _, motif in ipairs(MOTIFS_VARIABLE) do
        local debut, fin = string.find(modele, motif, position)
        if debut then
            if not meilleur_debut or debut < meilleur_debut
                or (debut == meilleur_debut and fin > meilleur_fin) then
                meilleur_debut, meilleur_fin = debut, fin
            end
        end
    end
    return meilleur_debut, meilleur_fin
end

-- Découpe un modèle en parties littérales et en variables.
-- Exposée sous AFR.DecouperModele pour que les tests puissent vérifier, sur
-- les vraies données du jeu, qu'aucune forme de variable ne nous échappe :
-- un « $ » restant dans une partie littérale condamne l'alignement.
local decouper
function decouper(modele)
    local litteraux, variables = {}, {}
    local position = 1
    while true do
        local debut, fin = prochaine_variable(modele, position)
        if not debut then break end
        table.insert(litteraux, string.sub(modele, position, debut - 1))
        table.insert(variables, string.sub(modele, debut, fin))
        position = fin + 1
    end
    table.insert(litteraux, string.sub(modele, position))
    return litteraux, variables
end

AFR.DecouperModele = decouper

-- Préfixe d'une variable conditionnelle : « $?s300512[oui][non] » ->
-- « $?s300512 ». C'est la seule partie IDENTIQUE entre le modèle anglais et
-- le modèle français : le texte entre crochets, lui, est TRADUIT côté FR —
-- chercher la valeur par la variable entière échouait donc toujours
-- (vécu : « Tempête juste », 805409, bloquée en anglais, 22/07/2026).
local function prefixe_conditionnel(variable)
    return string.match(variable, "^(%$%?[^%[]*)%[")
end

-- Capture TYPÉE d'une variable, pour le REPLI du bloc F (29/07/2026).
-- Une variable numérique ($s1, $64843s2, ${...}, $/1000;s1, $<mult>) ne
-- peut substituer qu'un nombre ; une durée ($d, $d2, $60493d) un nombre
-- suivi d'une unité. Typer la capture empêche une capture paresseuse
-- d'absorber le VOISIN quand deux variables sont adjacentes — la limite
-- qui laissait ~457 sorts traduits s'afficher en anglais.
local function capture_typee(variable)
    if string.match(variable, "^%$%d*[dD]%d*$") then
        return "(%-?[%d%.,]+%s*%a*)"          -- « 45 sec », « 1.5 min »
    end
    if string.match(variable, "^%$[suohtqaxez]%d*$")
        or string.match(variable, "^%$%d+%a%d*$")
        or string.match(variable, "^%$%b{}$")
        or string.match(variable, "^%$<%a+>$")
        or string.match(variable, "^%$[/%*%+%-]") then
        return "(%-?[%d%.,]+)"                 -- « 34 », « 1,500 », « 34.5 »
    end
    return "(.-)"                              -- texte : inchangé
end

-- Extrait les valeurs substituées par le client.
-- Renvoie { ["$s1"] = "15", ["$d"] = "6 sec" } + une table séparée pour les
-- conditionnelles, indexée par PRÉFIXE (voir ci-dessus), portant la valeur
-- affichée ET la variable anglaise complète (ses crochets servent à traduire
-- une branche non vide). Ou nil si l'affiché ne correspond pas au modèle.
local function extraire_valeurs(modele_en, affiche_en)
    local litteraux, variables = decouper(modele_en)
    if #variables == 0 then return {} end

    -- Un MARQUEUR (@s:...@, @ext:, :ext@, @ifknown...) n'est pas une
    -- variable porteuse de valeur : le client y INSÈRE du contenu, qui
    -- diffère légitimement d'une occurrence à l'autre (86 sorts refusés
    -- pour « incohérence » sur :ext@ — bloc F). Leurs contenus se suivent
    -- par RANG, comme les $l/$g.
    local function est_marqueur(variable)
        return string.sub(variable, 1, 1) == "@" or variable == ":ext@"
    end

    -- Un ESSAI complet : le motif doit rendre le bon nombre de captures
    -- ET une même variable PORTEUSE doit donner la même valeur partout
    -- (l'incohérence de même variable était la signature des captures
    -- paresseuses absorbantes : 242 cas). Les MARQUEURS, eux, empilent
    -- leurs contenus par rang.
    local function essayer(motif)
        local captures = { string.match(affiche_en, motif) }
        if #captures ~= #variables then return nil end
        local essai, essai_rangs = {}, {}
        for i, variable in ipairs(variables) do
            local valeur = captures[i]
            if valeur == nil then return nil end
            if est_marqueur(variable) then
                local pile = essai_rangs[variable]
                if not pile then
                    pile = {}
                    essai_rangs[variable] = pile
                end
                pile[#pile + 1] = valeur
                if essai[variable] == nil then
                    essai[variable] = valeur
                end
            else
                if essai[variable] and essai[variable] ~= valeur then
                    return nil
                end
                essai[variable] = valeur
            end
        end
        return captures, essai, essai_rangs
    end

    -- Motif HISTORIQUE : littéral, (capture paresseuse), littéral...
    -- Espace de tête/queue souple (echapper_souple) : un bloc conditionnel
    -- rendu vide fait disparaître les sauts de ligne qui l'entouraient.
    local motif = "^"
    for i, litteral in ipairs(litteraux) do
        motif = motif .. echapper_souple(litteral)
        if i <= #variables then motif = motif .. "(.-)" end
    end
    motif = motif .. "$"
    local captures, valeurs, rangs = essayer(motif)

    if not captures then
        -- LE REPLI TYPÉ (bloc F, 29/07/2026). Atteint UNIQUEMENT quand le
        -- motif historique échoue — là où l'affichage restait anglais.
        -- Strictement additif : un sort qui s'alignait hier s'aligne
        -- aujourd'hui à l'octet près, la comparaison de hachages
        -- population entière en fait foi (0 sortie commune changée).
        local motif2, differe = "^", false
        for i, litteral in ipairs(litteraux) do
            motif2 = motif2 .. echapper_souple(litteral)
            if i <= #variables then
                local c = capture_typee(variables[i])
                motif2 = motif2 .. c
                if c ~= "(.-)" then differe = true end
            end
        end
        motif2 = motif2 .. "$"
        if differe then
            captures, valeurs, rangs = essayer(motif2)
        end
        if not captures then return nil end
    end

    local conditionnelles = {}
    for i, variable in ipairs(variables) do
        local valeur = captures[i]
        local prefixe = prefixe_conditionnel(variable)
        if prefixe then
            local existante = conditionnelles[prefixe]
            if existante and (existante.valeur ~= valeur
                or existante.var_en ~= variable) then
                -- Deux conditionnelles au même préfixe qui divergent : on ne
                -- saurait pas laquelle sert au modèle français — ambigu.
                conditionnelles[prefixe] = { ambigu = true }
            elseif not existante then
                conditionnelles[prefixe] =
                    { valeur = valeur, var_en = variable }
            end
        end
    end
    local ordre_gl = {}
    for _, variable in ipairs(variables) do
        if string.match(variable, "^%$[GgLl]") then
            ordre_gl[#ordre_gl + 1] = variable
        end
    end
    return valeurs, conditionnelles, ordre_gl, rangs
end

-- Options d'une variable $l/$L/$g/$G : « $leffet:effets; » -> {"effet","effets"}
local function options_gl(variable)
    local corps = string.match(variable, "^%$[GgLl](.*);$")
    if not corps then return nil end
    local options = {}
    for morceau in string.gmatch(corps, "[^:]+") do
        options[#options + 1] = morceau
    end
    return options
end

-- L'intérieur du n-ième bloc [ ... ] d'une variable conditionnelle.
local function interieur_crochets(variable, rang)
    local compte = 0
    for bloc in string.gmatch(variable, "%b[]") do
        compte = compte + 1
        if compte == rang then
            return string.sub(bloc, 2, -2)
        end
    end
end

-- Le client étant anglais, les valeurs qu'il calcule contiennent ses propres
-- mots ($d -> « 1 hour 30 min »). On francise ces unités : chaque mot suivant
-- un nombre est remplacé une seule fois, via une table (des gsub en chaîne
-- se ré-appliqueraient à leur propre résultat : « seconds » -> « secondees »).
local UNITES = {
    ["hour"] = "heure",     ["hours"] = "heures",
    ["day"] = "jour",       ["days"] = "jours",
    ["yard"] = "mètre",     ["yards"] = "mètres",
    ["min"] = "min",        ["mins"] = "min",
    ["minute"] = "minute",  ["minutes"] = "minutes",
    ["sec"] = "sec",        ["secs"] = "sec",
    ["second"] = "seconde", ["seconds"] = "secondes",
}

local function franciser_unites(valeur)
    -- Plages calculées par le client (« 11 to 14 ») : vu sur la preuve du
    -- sort 3599 (lot 14) — le client résout $3606s1 en plage ANGLAISE dans
    -- la valeur qu'on réinsère. Uniquement sur la VALEUR capturée, jamais
    -- sur le texte entier : les littéraux du modèle français sont intacts.
    valeur = string.gsub(valeur, "(%d)%s+to%s+(%d)", "%1 à %2")
    return (string.gsub(valeur, "(%d)(%s+)(%a+)", function(nombre, espace, mot)
        return nombre .. espace .. (UNITES[string.lower(mot)] or mot)
    end))
end

-- Replace les valeurs dans le modèle français. `ordre_gl` (liste ordonnée
-- des variables $l/$L/$g/$G du modèle anglais) n'est fournie QUE par la
-- passe de sauvetage de TraduireInfobulleSort : nil = chemin historique.
local function appliquer_valeurs(modele_fr, valeurs, conditionnelles,
                                 ordre_gl, rangs)
    local litteraux, variables = decouper(modele_fr)
    -- Compteur d'occurrences des MARQUEURS (bloc F) : leurs contenus
    -- insérés par le client se consomment par RANG, pas par nom.
    local rang_marqueur = {}
    -- Variables $l/$L (pluriel) et $g/$G (genre) : Blizzard TRADUIT leurs
    -- options en français (« $leffet magique:effets magiques; ») — la clé
    -- FR ne peut donc JAMAIS retrouver la valeur indexée par la variable
    -- EN (111 sorts bloqués en anglais, mesuré au banc du lot 14).
    -- Appariement par RANG (n-ième $l français <-> n-ième $l anglais,
    -- comptes égaux et même famille exigés), puis choix de l'option FR au
    -- MÊME INDEX que l'option EN affichée par le client.
    local nb_gl_fr = 0
    if ordre_gl then
        for _, v in ipairs(variables) do
            if string.match(retirer_couleurs(v), "^%$[GgLl]") then
                nb_gl_fr = nb_gl_fr + 1
            end
        end
    end
    local rang_gl = 0
    local morceaux = {}
    for i, litteral in ipairs(litteraux) do
        table.insert(morceaux, litteral)   -- littéral FR : couleurs conservées
        local variable = variables[i]
        if variable then
            -- Les valeurs sont indexées par la variable EN DÉNUDÉE (le modèle
            -- anglais a été dénudé avant l'alignement) : on cherche donc avec
            -- la variable FR elle aussi dénudée, sinon un bloc coloré des deux
            -- côtés (@ifknown avec |cff..|r) ne se retrouverait jamais.
            local nue = retirer_couleurs(variable)
            local valeur = valeurs[nue]
            -- MARQUEUR à occurrences multiples : le contenu du n-ième
            -- marqueur français est celui du n-ième anglais. Pile
            -- ÉPUISÉE (le français a plus d'occurrences que l'anglais —
            -- 17 sorts sains, mesuré) : retour à la valeur par NOM, la
            -- sémantique historique, qui servait la même valeur partout.
            if rangs and rangs[nue] then
                local n = (rang_marqueur[nue] or 0) + 1
                rang_marqueur[nue] = n
                valeur = rangs[nue][n] or valeurs[nue]
            end
            if ordre_gl and string.match(nue, "^%$[GgLl]") then
                rang_gl = rang_gl + 1
                if valeur == nil and #ordre_gl == nb_gl_fr then
                    local var_en = ordre_gl[rang_gl]
                    -- même famille exigée ($l avec $l, $g avec $g)
                    if var_en and string.lower(string.sub(var_en, 2, 2))
                            == string.lower(string.sub(nue, 2, 2)) then
                        local affichee = valeurs[var_en]
                        local opts_en = options_gl(var_en)
                        local opts_fr = options_gl(nue)
                        if affichee and opts_en and opts_fr
                                and #opts_en == #opts_fr then
                            -- Option EN dupliquée pointant vers des options
                            -- FR différentes = AMBIGU : abandon, jamais
                            -- premier-arrivé (défaut relevé par le
                            -- sceptique du lot 14 — 0 cas dans le corpus
                            -- du jour, mais la garantie doit être VRAIE
                            -- dans le code, pas seulement annoncée).
                            local choix, ambigu
                            for i = 1, #opts_en do
                                if opts_en[i] == affichee then
                                    if choix ~= nil
                                            and choix ~= opts_fr[i] then
                                        ambigu = true
                                        break
                                    end
                                    choix = opts_fr[i]
                                end
                            end
                            if not ambigu then valeur = choix end
                        end
                    end
                end
            end
            if valeur == nil then
                -- Variable conditionnelle : son texte entre crochets est
                -- TRADUIT côté français, la recherche par variable entière
                -- ne peut pas aboutir — on passe par le PRÉFIXE, identique
                -- des deux côtés.
                local prefixe = prefixe_conditionnel(nue)
                local cond = prefixe and conditionnelles
                    and conditionnelles[prefixe]
                if cond and not cond.ambigu then
                    if cond.valeur == "" then
                        -- Branche résolue à vide : rien à afficher.
                        valeur = ""
                    else
                        -- Branche affichée (texte anglais, nombres résolus) :
                        -- on la traduit avec sa jumelle française — même
                        -- moteur, un cran plus bas. Crochet « oui » d'abord,
                        -- crochet « non » sinon.
                        for rang = 1, 2 do
                            local en_bloc = interieur_crochets(
                                cond.var_en, rang)
                            local fr_bloc = interieur_crochets(nue, rang)
                            if en_bloc and fr_bloc then
                                valeur = AFR.TraduireTexteSort(
                                    fr_bloc, en_bloc, cond.valeur,
                                    ordre_gl ~= nil)
                                if valeur then break end
                            end
                        end
                    end
                end
            end
            -- Variable toujours irrésolue : on ne sait pas faire.
            if valeur == nil then return nil end
            table.insert(morceaux, franciser_unites(valeur))
        end
    end
    return table.concat(morceaux)
end

-- Les fins de ligne diffèrent entre le modèle et l'affiché : les DBC écrivent
-- « \r\n », mais la chaîne peut avoir perdu son « \r » en chemin. Un caractère
-- invisible ne doit pas faire échouer tout l'alignement — c'est ce qui laissait
-- des descriptions entières en anglais (« modèle non aligné »).
local function normaliser_lignes(texte)
    if not texte then return nil end
    texte = string.gsub(texte, "\r\n", "\n")
    return (string.gsub(texte, "\r", "\n"))
end

-- Le client REPLIE les blocs @ext:...:ext@ : tant que MAJ n'est pas
-- enfoncée, il affiche « Hold SHIFT for more information » à la place du
-- contenu. Le modèle porte le contenu, l'écran porte l'indice : rien ne peut
-- s'aligner (vécu : « Libram de consécration », signalement du 17/07). On
-- retire alors le bloc des deux modèles et l'indice de l'affiché, on aligne
-- le reste, et on remet l'indice — en français.
local INDICE_MAJ = "Hold SHIFT for more information"
local INDICE_MAJ_FR = "|cff00DDFFMaintenez MAJ pour plus d'informations|r"

local function RetirerBlocsExt(texte)
    texte = string.gsub(texte, "%s*@ext:.-:ext@", "")
    return (string.gsub(texte, "%s+$", ""))
end

local function RetirerIndiceMaj(texte)
    texte = string.gsub(texte,
        "%s*|c%w%w%w%w%w%w%w%w" .. INDICE_MAJ .. "|r", "")
    texte = string.gsub(texte, "%s*" .. INDICE_MAJ, "")
    return (string.gsub(texte, "%s+$", ""))
end

-- ----------------------------------------------------------------------------
-- Tolérance aux nombres calculés par le client
-- ----------------------------------------------------------------------------
-- Ascension ne stocke pas toujours une variable ($s1) : pour beaucoup de ses
-- sorts maison, le serveur donne une FORMULE (« 24+Spi*0.25+AP*.2+SP*.58 ») et
-- le client affiche le résultat. Deux personnages voient donc deux nombres
-- différents, et un modèle relevé chez un joueur ne collera jamais au chiffre
-- près chez un autre (vécu : « Réparation Sanguine », 31 chez l'un, 34 chez
-- l'autre). Quand TOUT le reste est identique, on reporte simplement les
-- nombres affichés dans le texte français.
-- Bonus : un seul modèle couvre alors tous les rangs d'un même sort.
local NOMBRE = "%d+"

-- Littéral transformé en motif, avec les ESPACES SOUPLES : une espace en trop
-- avant un saut de ligne ne doit pas condamner tout l'alignement (vécu : le
-- client écrit « ...Intellect. \r\n », le modèle « ...Intellect.\n » — une
-- seule espace invisible laissait la description entière en anglais).
local function litteral_souple(litteral)
    local motif, position = "", 1
    while true do
        local debut, fin = string.find(litteral, "%s+", position)
        if not debut then break end
        motif = motif .. echapper(string.sub(litteral, position, debut - 1))
            .. "%s+"
        position = fin + 1
    end
    return motif .. echapper(string.sub(litteral, position))
end

-- Modèle où chaque nombre devient une capture, le reste restant littéral.
local function motif_nombres(modele)
    local motif, position = "^", 1
    while true do
        local debut, fin = string.find(modele, NOMBRE, position)
        if not debut then break end
        motif = motif .. litteral_souple(string.sub(modele, position,
                                                    debut - 1))
            .. "(" .. NOMBRE .. ")"
        position = fin + 1
    end
    return motif .. litteral_souple(string.sub(modele, position)) .. "$"
end

-- Remplace les nombres du français SANS toucher aux codes couleur et texture
-- (« |cff32cd32 », « |T...:0|t ») qui contiennent eux aussi des chiffres : on
-- les met à l'abri derrière des marqueurs qui, eux, n'en contiennent pas.
local function remplacer_nombres(texte, vers)
    local couleurs, textures = {}, {}
    texte = string.gsub(texte, "|c%x%x%x%x%x%x%x%x", function(code)
        table.insert(couleurs, code)
        return "\1"
    end)
    texte = string.gsub(texte, "|T.-|t", function(code)
        table.insert(textures, code)
        return "\2"
    end)
    texte = string.gsub(texte, NOMBRE, function(n) return vers[n] or n end)
    local i, j = 0, 0
    texte = string.gsub(texte, "\1", function()
        i = i + 1
        return couleurs[i]
    end)
    return (string.gsub(texte, "\2", function()
        j = j + 1
        return textures[j]
    end))
end

-- Rend le français avec les nombres de l'affiché, ou nil si ça ne colle pas.
local function aligner_nombres(modele_fr, modele_en, affiche_en)
    local attendus = {}
    for n in string.gmatch(modele_en, NOMBRE) do
        table.insert(attendus, n)
    end
    if #attendus == 0 then return nil end
    local trouves = { string.match(affiche_en, motif_nombres(modele_en)) }
    if #trouves ~= #attendus then return nil end
    -- Correspondance par VALEUR et non par position : l'ordre des nombres peut
    -- différer en français. Une même valeur qui devrait devenir deux choses
    -- différentes est ambiguë — on renonce plutôt que d'inventer.
    local vers = {}
    for i, ancien in ipairs(attendus) do
        if vers[ancien] and vers[ancien] ~= trouves[i] then return nil end
        vers[ancien] = trouves[i]
    end
    return remplacer_nombres(modele_fr, vers)
end

AFR.AlignerNombres = aligner_nombres      -- exposé pour les tests

-- Traduit un texte de sort en s'appuyant sur le texte anglais affiché.
-- Renvoie nil si la correspondance échoue : mieux vaut l'anglais qu'un texte
-- avec des « $s1 » visibles.
-- `sauver_gl` (optionnel) : autorise le sauvetage des variables $l/$L/$g/$G
-- traduites par Blizzard. ABSENT par défaut : tous les appelants historiques
-- (AlignerDeplie, blocs incrustés, outils hors-jeu) gardent leur comportement.
function AFR.TraduireTexteSort(modele_fr, modele_en, affiche_en, sauver_gl)
    if not modele_fr then return nil end
    -- Bloc @ext replié ? On traduit la version repliée.
    local indice = ""
    if affiche_en and modele_en
        and string.find(affiche_en, INDICE_MAJ, 1, true)
        and string.find(modele_en, "@ext:", 1, true) then
        modele_en = RetirerBlocsExt(modele_en)
        modele_fr = RetirerBlocsExt(modele_fr)
        affiche_en = RetirerIndiceMaj(affiche_en)
        indice = "\n\n" .. INDICE_MAJ_FR
    end
    -- Codes couleur retirés pour TOUTE la phase d'alignement (modèle EN +
    -- affiché). Le résultat français vient de modele_fr NON dénudé : il garde
    -- donc ses propres couleurs.
    local modele_en_nu = retirer_couleurs(modele_en)
    local affiche_nu = retirer_couleurs(affiche_en)

    -- Pas de variable : le texte français s'utilise directement. Le critère
    -- est le découpeur lui-même, pas la seule présence d'un « $ » : un modèle
    -- sans dollar peut porter un marquage @s:...@ qui exige l'alignement
    -- (« Tempête juste » : le client insère toute une description à cet
    -- endroit).
    local a_variables = false
    if modele_en_nu then
        local _, vars_en = decouper(modele_en_nu)
        a_variables = #vars_en > 0
    end
    if not a_variables then
        local _, vars_fr = decouper(modele_fr)
        if #vars_fr > 0 or string.find(modele_fr, "%$") then
            return nil
        end
        -- Sans variable, on ne traduit que LA ligne qui EST le modèle
        -- anglais. Rendre le français sans vérifier remplaçait chaque ligne
        -- longue de l'info-bulle par la même phrase (vécu : hache aux
        -- enchantements multiples, « Livre des artisans » en triple).
        local function egaliser(texte)
            texte = normaliser_lignes(texte)
            return (string.gsub(texte, "^%s*(.-)%s*$", "%1"))
        end
        -- Comparaison indifférente aux espaces : le client sème parfois une
        -- espace de plus (« Intellect. \r\n » contre « Intellect.\n »). Le
        -- français rendu, lui, reste intact — on ne compare que pour décider.
        local function sans_espaces(texte)
            return (string.gsub(egaliser(texte), "%s+", " "))
        end
        if modele_en_nu and affiche_nu then
            local modele_nu = egaliser(modele_en_nu)
            local affiche = egaliser(affiche_nu)
            if sans_espaces(affiche) == sans_espaces(modele_nu) then
                return modele_fr .. indice
            end
            -- Seuls les NOMBRES diffèrent ? Le client les a calculés d'après
            -- le personnage : on reporte ceux de l'écran dans le français.
            local avec_nombres = aligner_nombres(modele_fr, modele_nu, affiche)
            if avec_nombres then return avec_nombres .. indice end
        end
        return nil
    end
    if not affiche_nu then return nil end
    affiche_nu = normaliser_lignes(affiche_nu)
    local valeurs, conditionnelles, ordre_gl, rangs =
        extraire_valeurs(normaliser_lignes(modele_en_nu), affiche_nu)
    if not valeurs then return nil end
    if not sauver_gl then ordre_gl = nil end
    local resultat = appliquer_valeurs(modele_fr, valeurs, conditionnelles,
                                       ordre_gl, rangs)
    if not resultat then return nil end

    -- Garde-fou final : le joueur ne doit JAMAIS voir un « $ » à la place
    -- d'un chiffre. Si le texte français en contient plus que l'info-bulle
    -- anglaise (qui, elle, est déjà résolue), c'est qu'une variable a été
    -- abîmée en amont — typiquement par le traducteur automatique, dont la
    -- liste de codes à protéger avait divergé de celle-ci. On rend alors
    -- l'anglais, qui est correct.
    -- Ascension laisse quelques « $ » littéraux dans ses propres textes : ils
    -- apparaissent des deux côtés, d'où la comparaison par nombre plutôt que
    -- par présence.
    local _, dollars_fr = string.gsub(resultat, "%$", "")
    local _, dollars_en = string.gsub(affiche_nu, "%$", "")
    if dollars_fr > dollars_en then
        AFR.Debug("variable abîmée dans le texte français, anglais conservé")
        return nil
    end
    -- Un bloc conditionnel résolu à vide peut laisser un saut de ligne en fin
    -- de description : on le retire (l'indice @ext, lui, est rajouté après).
    resultat = (string.gsub(resultat, "%s+$", ""))
    -- Polissage du singulier (24/07, capture de Dan : « toutes les
    -- 1 secondes ») : quand la valeur calculée vaut 1, le français se dit
    -- « toutes les secondes ». Littéraux exacts uniquement — jamais de
    -- réécriture large.
    resultat = string.gsub(resultat, "[Tt]outes les 1 secondes",
                           "toutes les secondes")
    resultat = string.gsub(resultat, "[Tt]outes les 1 seconde%f[%A]",
                           "toutes les secondes")
    resultat = string.gsub(resultat, "[Tt]outes les 1 sec%f[%A]",
                           "toutes les secondes")
    return resultat .. indice
end

-- ----------------------------------------------------------------------------
-- Application aux info-bulles
-- ----------------------------------------------------------------------------
local function LigneGauche(tooltip, i)
    return _G[tooltip:GetName() .. "TextLeft" .. i]
end

-- Cherche, parmi toutes les lignes de l'info-bulle, celle que le modèle sait
-- aligner. Deviner « la dernière ligne longue » ne marche pas : Ascension
-- ajoute après la description d'autres lignes (« Applies Sacred Restraint »,
-- l'encadré du buff...), et on tentait alors d'aligner le modèle contre un
-- texte qui n'a rien à voir. L'alignement est lui-même le bon critère : la
-- description est la ligne qui correspond au modèle.
local function TraduireDescription(tooltip, modele_fr, modele_en,
                                   sauver_gl)
    -- Toutes les lignes qui s'alignent, pas seulement la première : les
    -- objets de collection d'Ascension répètent le texte du sort (« Livre
    -- des artisans »), et s'arrêter au premier succès laissait le doublon
    -- en anglais.
    local traduit = false
    for i = 2, tooltip:NumLines() do
        local ligne = LigneGauche(tooltip, i)
        local texte = ligne and ligne:GetText()
        if texte and string.len(texte) > 10 then
            local fr = AFR.TraduireTexteSort(modele_fr, modele_en, texte,
                                             sauver_gl)
            if fr then
                ligne:SetText(fr)
                traduit = true
            end
        end
    end
    return traduit
end

-- ----------------------------------------------------------------------------
-- BASE COMMUNAUTAIRE (don d'un joueur, 22/07/2026 — voir CONTEXTE) : lignes
-- de sorts CoA par MOTIF (nombres capturés -> gabarit {{n}}), relues main.
-- Consultée en PRIORITÉ pour les SpellID couverts ; les variantes génériques
-- partagées (« Level: %d »...) vivent dans SortsLignesCommunes et ne
-- s'essaient QUE sur les sorts couverts.
-- ----------------------------------------------------------------------------
local function AppliquerVariantes(liste, texte)
    if not liste then return end
    for i = 1, #liste do
        local captures = { string.match(texte, liste[i].p) }
        if captures[1] ~= nil then
            return (string.gsub(liste[i].t, "{{(%d+)}}", function(k)
                return captures[tonumber(k)] or ""
            end))
        end
    end
end

local function PasseCommunaute(tooltip, id)
    -- Interrupteur d'ESSAI (demande de Dan, 23/07) : couper la couche
    -- communautaire pour comparer avec notre seule chaîne. Bascule via
    -- /afrcommunaute — réversible à chaud, rien n'est supprimé.
    if AscensionFRSaved and AscensionFRSaved.Options
            and AscensionFRSaved.Options.sansCommunaute then
        return false
    end
    local fiche = id and AFR.DB.SortsLignes and AFR.DB.SortsLignes[id]
    if not fiche then return false end
    local fait = false
    local l1 = LigneGauche(tooltip, 1)
    if fiche.n and fiche.e and l1 and l1:GetText() == fiche.e then
        l1:SetText(fiche.n)
        fait = true
    end
    for i = 2, tooltip:NumLines() do
        local ligne = LigneGauche(tooltip, i)
        local texte = ligne and ligne:GetText()
        if texte and texte ~= "" then
            local fr = AppliquerVariantes(fiche.v, texte)
                or AppliquerVariantes(AFR.DB.SortsLignesCommunes, texte)
            if fr and fr ~= texte then
                ligne:SetText(fr)
                fait = true
            end
        end
    end
    return fait
end

-- ============================================================================
-- ALIGNEUR DES TEXTES DÉPLIÉS — le remplaçant SÛR de la greffe retirée.
-- Principe TOUT-OU-RIEN, chimère impossible par construction :
--   1. le modèle anglais déplié et le français déplié sont découpés en
--      PARAGRAPHES ; comptes différents -> abandon ;
--   2. une ligne affichée n'est traduite que si sa FORME (nombres remplacés
--      par #, codes décapés, espaces unifiés) est EXACTEMENT celle d'UN SEUL
--      paragraphe anglais ; ambiguïté -> abandon de la ligne ;
--   3. la sortie est le paragraphe FRANÇAIS ENTIER correspondant, avec les
--      nombres de l'écran réinjectés dans l'ordre — jamais un mot anglais,
--      jamais un collage. Comptes de nombres différents -> abandon.
-- (Méthode « forme + réinjection » observée chez CoARU, durcie par le
-- tout-ou-rien. Validée par outils/verifier_deplie.py AVANT tout jeu.)
-- ============================================================================
local function Paragrapher(texte)
    local morceaux = {}
    for morceau in string.gmatch(texte or "", "[^\n]+") do
        morceau = string.gsub(morceau, "^%s+", "")
        morceau = string.gsub(morceau, "%s+$", "")
        if morceau ~= "" then table.insert(morceaux, morceau) end
    end
    return morceaux
end

function AFR.AlignerDeplie(ligne_affichee, en_deplie, fr_deplie)
    if not (ligne_affichee and en_deplie and fr_deplie) then return nil end
    local paras_en = Paragrapher(en_deplie)
    local paras_fr = Paragrapher(fr_deplie)
    if #paras_en == 0 or #paras_en ~= #paras_fr then return nil end
    -- Chaque paire de paragraphes passe au VÉTÉRAN TraduireTexteSort
    -- (variables, unités, garde anti-« $ » : tout est déjà là). La ligne
    -- n'est acceptée que si EXACTEMENT UNE paire réussit — l'ambiguïté
    -- vaut abandon, l'anglais honnête plutôt qu'un pari.
    local resultat = nil
    for i = 1, #paras_en do
        local essai = AFR.TraduireTexteSort(paras_fr[i], paras_en[i],
                                            ligne_affichee)
        if essai then
            if resultat then return nil end     -- deux candidats : abandon
            resultat = essai
        end
    end
    return resultat
end

-- DÉPLIAGE PAR LE CLIENT (canal C_Format, validé en jeu le 23/07/2026 sur
-- « Morsure brûlée » 274363) : C_Format.Format déplie les marqueurs @…@
-- d'un texte — y compris FRANÇAIS — et rend les lignes annexes (détail par
-- point de combo…), SANS résoudre les $ (ils restent à notre alignement).
-- Utilisé en DERNIÈRE chance seulement : les chemins éprouvés gèrent déjà
-- les blocs repliés MAJ ; le dépliage vise l'affichage DÉPLIÉ complexe que
-- l'absorption par motifs ratait. Repéré dans CoARU (l'addon russe).
local deplisClient = {}
local deplisClientNb = 0

local function DeplierClient(texte, id, quel)
    if not (texte and id and C_Format
            and type(C_Format.Format) == "function") then
        return nil
    end
    local cle = id .. quel
    local connu = deplisClient[cle]
    if connu ~= nil then
        if connu == false then return nil end
        return connu
    end
    local ok, sorti, lignes = pcall(C_Format.Format, texte, false, 0, id)
    if ok and type(sorti) == "string" and sorti ~= "" then
        if type(lignes) == "table" then
            for _, ligne in ipairs(lignes) do
                if type(ligne) == "string" and ligne ~= "" then
                    sorti = sorti .. "\n" .. ligne
                end
            end
        end
    else
        sorti = false
    end
    if deplisClientNb > 512 then     -- borne de mémoire, comme memoireVerdict
        deplisClient = {}
        deplisClientNb = 0
    end
    deplisClient[cle] = sorti
    deplisClientNb = deplisClientNb + 1
    if sorti == false then return nil end
    return sorti
end

-- Une ligne est du BRUIT pour le journal d'échecs : durée dynamique
-- (« X remaining / restantes ») — jamais dans la base — ou DÉJÀ FRANÇAISE
-- (l'octet de tête 0xC3 « \195 » marque les accents FR, absents de
-- l'anglais). Sans ce filtre, le journal se remplissait de buffs français et
-- de durées faussement « non alignés » (constat du 24/07, fichier de Dan :
-- « Ne peut pas être attaqué… », « 46 minutes remaining »…).
local function LigneBruit(t)
    if type(t) ~= "string" or t == "" then return true end
    if string.find(t, "remaining") or string.find(t, "restante") then
        return true
    end
    if string.find(t, "\195") then return true end
    return false
end

-- Relève les lignes DIGNES de journal (anglais statique). Renvoie nil si rien
-- de substantiel — alors on NE journalise PAS (plus de fausse alerte).
local function LignesADiagnostiquer(tooltip, depuis)
    local lignes = {}
    for i = depuis, tooltip:NumLines() do
        local l = LigneGauche(tooltip, i)
        local t = l and l:GetText()
        if t and t ~= "" and not LigneBruit(t) then
            table.insert(lignes, t)
        end
    end
    return #lignes > 0 and lignes or nil
end

-- discret (24/07) : second passage OnShow sur l'état FINAL de la bulle —
-- il voit des lignes déjà françaises, son « échec d'alignement » est
-- attendu et ne doit ni journaliser ni compter.
function AFR.TraduireInfobulleSort(tooltip, id, discret)
    local s = id and AFR.DB.Sorts[id]
    local communaute = PasseCommunaute(tooltip, id)
    -- Sort inconnu des bases, ou connu de NOM seulement : sans ce relevé,
    -- ces sorts n'entraient jamais dans le circuit de récolte — le journal
    -- ne notait que les échecs d'alignement, donc un sort sans description
    -- restait invisible de l'usine, même signalé cent fois par un joueur
    -- (vécu : Testament de ténacité). On relève dès la ligne 1 : le nom
    -- anglais fait partie de ce que l'usine doit apprendre.
    -- (Sauf si la base communautaire vient de le servir : rien à apprendre.)
    if id and (not s or not s.D) and not communaute
            and not discret and not echecsSignales[id]
            and AFR.JournaliserEchec then
        echecsSignales[id] = true
        -- Filtré : ni durées ni lignes déjà françaises — sinon un simple buff
        -- français (« Ne peut pas être attaqué… ») était journalisé « à
        -- traduire » (constat du 24/07). Si rien de substantiel : on se tait.
        local lignes = LignesADiagnostiquer(tooltip, 1)
        if lignes then
            AFR.JournaliserEchec("S", id, lignes)
        end
    end
    if not s then
        if communaute and tooltip:IsShown() then tooltip:Show() end
        return communaute
    end
    local modifie = communaute

    if s.N then
        local l1 = LigneGauche(tooltip, 1)
        if l1 and l1:GetText() then
            -- Conserve les icônes/couleurs éventuelles autour du nom
            l1:SetText(s.N)
            modifie = true
        end
    end

    -- Rang (« Rank 2 » -> « Rang 2 ») : ligne 2 à droite en général
    if s.R then
        local r1 = _G[tooltip:GetName() .. "TextRight1"]
        if r1 and r1:GetText() and string.match(r1:GetText(), "^Rank %d") then
            r1:SetText(s.R)
            modifie = true
        end
    end

    -- « Rank 0/1 » des info-bulles de TALENTS (capture de Dan, 24/07) :
    -- une ligne gauche à part entière, jamais couverte par les modèles.
    for i = 2, tooltip:NumLines() do
        local l = LigneGauche(tooltip, i)
        local t = l and l:GetText()
        if t then
            local a, b = string.match(t, "^Rank (%d+)/(%d+)$")
            if a then
                l:SetText("Rang " .. a .. "/" .. b)
                modifie = true
            end
        end
    end

    if s.D then
        -- COUPE-CIRCUIT DU CHEMIN COÛTEUX : une bulle qui refuse de
        -- s'aligner se redessine en continu tant qu'on la survole, et
        -- chaque redessin refaisait TOUT le calcul (découpe du modèle,
        -- motifs, extraction) pour échouer pareil. On note la longueur du
        -- contenu au moment de l'échec : tant qu'elle n'a pas bougé,
        -- inutile de réessayer. C'était LA source de lag en survol des
        -- sorts d'époque décalée (vécu : Tempête juste, 805409).
        local signature = 0
        for i = 2, tooltip:NumLines() do
            local l = LigneGauche(tooltip, i)
            local t = l and l:GetText()
            if t then signature = signature + string.len(t) end
        end
        if echecsRecents[id] == signature then
            return modifie
        end
        -- Modèle principal (le lancement), puis modèle secondaire s'il existe.
        -- Un même sort affiche un texte DIFFÉRENT selon la vue : sa description
        -- de lancement, ou l'effet de son buff une fois appliqué. On essaie les
        -- deux (DE2/D2, ajoutés par les corrections). Ce 2e modèle sert aussi
        -- quand Ascension a changé le texte : le live devient le modèle qui
        -- s'aligne, sans toucher au modèle d'origine.
        local aligne = TraduireDescription(tooltip, s.D, s.DE)
        if not aligne and s.D2 then
            aligne = TraduireDescription(tooltip, s.D2, s.DE2)
        end
        -- Sauvetage $l/$L/$g/$G, APRÈS les chemins historiques : le texte
        -- qui marchait reste prioritaire. Tenté en premier, le sauvetage
        -- basculait en douce 2 sorts (1108012, 8946) de leur D2 officiel
        -- vers un D primaire douteux — mesuré par le sceptique du lot 14
        -- en comparant les sorties HACHÉES du banc complet, pas les
        -- verdicts. Résultat exigé : 89 rescapés, 0 sortie changée ailleurs.
        if not aligne then
            aligne = TraduireDescription(tooltip, s.D, s.DE, true)
            if not aligne and s.D2 then
                aligne = TraduireDescription(tooltip, s.D2, s.DE2, true)
            end
        end
        -- Troisième chance SÛRE (23/07 soir — remplace la greffe retirée
        -- le matin même) : modèles DÉPLIÉS par le client, puis
        -- AlignerDeplie LIGNE PAR LIGNE — appariement de paragraphes
        -- tout-ou-rien confié au vétéran TraduireTexteSort, ambiguïté =
        -- abandon. Chimère impossible par construction : la sortie est
        -- toujours un paragraphe français ENTIER de la base. Validé par
        -- outils/verifier_deplie.py AVANT tout passage en jeu (leçon du
        -- matin). Vise les 5 315 sorts « classe Tempête vertueuse » de
        -- l'audit (rapports/sorts_anglais.txt).
        if not aligne and s.DE and string.find(s.DE, "@%a") then
            local en_deplie = DeplierClient(s.DE, id, "E")
            local fr_deplie = en_deplie and DeplierClient(s.D, id, "F")
            if fr_deplie then
                for i = 2, tooltip:NumLines() do
                    local l = LigneGauche(tooltip, i)
                    local t = l and l:GetText()
                    if t and t ~= "" then
                        local fr = AFR.AlignerDeplie(t, en_deplie,
                                                     fr_deplie)
                        if fr and fr ~= t then
                            l:SetText(fr)
                            aligne = true
                        end
                    end
                end
            end
        end
        -- QUATRIÈME chance (24/07, capture « Entraînement écarlate ») : le
        -- BLOC INCRUSTÉ d'un AUTRE sort. Le client déplie les renvois
        -- « @s:807035:0@ » du modèle en lignes supplémentaires — nom puis
        -- description du sort renvoyé. Tous nos alignements ne connaissent
        -- que le sort PARENT : ces lignes restaient anglaises alors que
        -- leur traduction attendait dans la base (chantier des sorts
        -- référencés). L'identifiant est DANS le renvoi : on traduit le nom
        -- (GetSpellInfo pour l'anglais de contrôle) et la description (le
        -- vétéran, tolérance nombres incluse) du sort renvoyé, ligne à
        -- ligne. Le dépliage C_Format ne peut PAS servir ici : il réinjecte
        -- le texte anglais du client dans le modèle français (paire EN/EN).
        if s.DE and string.find(s.DE, "@s") then
            local renvois = {}
            for rid in string.gmatch(s.DE, "@s:(%d+)") do
                renvois[tonumber(rid)] = true
            end
            for rid in string.gmatch(s.DE, "@spelldesc(%d+)") do
                renvois[tonumber(rid)] = true
            end
            -- Dépouille icône |T...|t, couleurs et espaces : les lignes du
            -- bloc arrivent habillées (relevés /afrbulle du 24/07).
            local function Denuder(texte)
                local nu = string.gsub(texte, "|T[^|]*|t", "")
                nu = string.gsub(nu, "|c%x%x%x%x%x%x%x%x", "")
                nu = string.gsub(nu, "|r", "")
                nu = string.gsub(nu, "^%s+", "")
                nu = string.gsub(nu, "%s+$", "")
                return nu
            end
            -- Un PARAGRAPHE du bloc : la ligne-nom (nom remplacé, icône et
            -- couleurs conservées) ou la description (vétéran, enveloppe de
            -- couleur tolérée). nil = paragraphe non traduit.
            local function ParagrapheEnfant(seg, enfant, nomEN)
                local nu = Denuder(seg)
                if nomEN and enfant.N and nu == nomEN then
                    if nomEN == enfant.N then return seg end
                    local motif = string.gsub(nomEN,
                        "([%^%$%(%)%%%.%[%]%*%+%-%?])", "%%%1")
                    local rempl = string.gsub(enfant.N, "%%", "%%%%")
                    return (string.gsub(seg, motif, rempl, 1))
                end
                -- Pont des NOMS en repli : GetSpellInfo peut rester muet
                -- sur un id d'aura pure — le pont, lui, connaît le texte.
                if nu ~= "" and string.len(nu) <= 60 then
                    local noms = AFR.DB.SortsNoms
                    local nom_fr = noms and noms[nu]
                    if nom_fr and nom_fr ~= nu then
                        local motif = string.gsub(nu,
                            "([%^%$%(%)%%%.%[%]%*%+%-%?])", "%%%1")
                        local rempl = string.gsub(nom_fr, "%%", "%%%%")
                        return (string.gsub(seg, motif, rempl, 1))
                    end
                end
                if enfant.D and enfant.DE and string.len(seg) > 12 then
                    local fr = AFR.TraduireTexteSort(enfant.D, enfant.DE,
                                                     seg)
                    if fr then return fr end
                    local deb, coeur = string.match(seg,
                        "^(|c%x%x%x%x%x%x%x%x)(.-)|r%s*$")
                    if coeur then
                        local dedans = AFR.TraduireTexteSort(
                            enfant.D, enfant.DE, coeur)
                        if dedans then return deb .. dedans .. "|r" end
                    end
                end
                return nil
            end
            for rid in pairs(renvois) do
                local enfant = AFR.DB.Sorts[rid]
                if enfant then
                    local nomEN = GetSpellInfo(rid)
                    for i = 2, tooltip:NumLines() do
                        local l = LigneGauche(tooltip, i)
                        local t = l and l:GetText()
                        if t and t ~= "" then
                            if string.find(t, "\n", 1, true) then
                                -- BLOC FUSIONNÉ (relevé /afrbulle) : le
                                -- client livre le bloc en UNE seule zone —
                                -- sous-ligne vide, « icône + nom », puis la
                                -- description. On traduit PAR PARAGRAPHE,
                                -- TOUT-OU-RIEN : un paragraphe à lettres qui
                                -- résiste = ligne entière laissée anglaise
                                -- (jamais de mélange).
                                local morceaux = {}
                                local echec, change = false, false
                                for seg in string.gmatch(t .. "\n",
                                                         "([^\n]*)\n") do
                                    seg = string.gsub(seg, "\r$", "")
                                    if not string.find(seg, "%a") then
                                        table.insert(morceaux, seg)
                                    else
                                        local fr = ParagrapheEnfant(
                                            seg, enfant, nomEN)
                                        if fr then
                                            if fr ~= seg then
                                                change = true
                                            end
                                            table.insert(morceaux, fr)
                                        else
                                            echec = true
                                            break
                                        end
                                    end
                                end
                                if change and not echec then
                                    l:SetText(table.concat(morceaux, "\n"))
                                    modifie = true
                                end
                            else
                                local fr = ParagrapheEnfant(t, enfant,
                                                            nomEN)
                                if fr and fr ~= t then
                                    l:SetText(fr)
                                    modifie = true
                                end
                            end
                        end
                    end
                end
            end
        end
        if aligne then
            modifie = true
            echecsRecents[id] = nil
            if AFR.OublierEchec then AFR.OublierEchec("S", id) end
        else
            echecsRecents[id] = signature
            -- Servi par la base communautaire, ou SECOND passage (OnShow,
            -- lignes déjà françaises) : l'échec d'alignement est NORMAL —
            -- ni bruit ni journal.
            if not communaute and not discret
                and not echecsSignales[id] then
                echecsSignales[id] = true
                AFR.Debug("sort", id, ": modèle non aligné, anglais conservé")
            end
            -- Journal silencieux pour le compagnon : quelles lignes étaient
            -- affichées quand l'alignement a échoué ? (Durées et lignes déjà
            -- françaises filtrées — mêmes fausses alertes, cf. 24/07.)
            if AFR.JournaliserEchec and not communaute and not discret then
                local lignes = LignesADiagnostiquer(tooltip, 2)
                if lignes then
                    AFR.JournaliserEchec("S", id, lignes)
                end
            end
        end
    end

    if modifie and tooltip:IsShown() then tooltip:Show() end
    return modifie
end

-- ============================================================================
-- /afrformat [id] — ESSAI du canal C_Format (repéré dans CoARU, 23/07/2026).
-- Le client d'Ascension expose C_Format.Format(texte, false, 0, idSort) qui
-- DÉPLIE lui-même les marqueurs @…@ d'un texte. Aujourd'hui nous absorbons
-- ces marqueurs par motifs (fragile — l'affaire du Libram). Si le client
-- déplie AUSSI un texte FRANÇAIS, toute cette classe de bugs disparaît.
-- La commande montre avant/après sur le modèle anglais ET le français.
-- ============================================================================
-- /afrcommunaute — coupe/relance la couche communautaire (lignes Glayna)
-- pour l'ESSAI comparatif de Dan. L'effet est immédiat sur les nouvelles
-- info-bulles (les verdicts mémorisés partent au prochain /reload).
SLASH_AFRCOMMUNAUTE1 = "/afrcommunaute"
SlashCmdList["AFRCOMMUNAUTE"] = function()
    AscensionFRSaved = AscensionFRSaved or {}
    AscensionFRSaved.Options = AscensionFRSaved.Options or {}
    local o = AscensionFRSaved.Options
    o.sansCommunaute = not o.sansCommunaute
    if o.sansCommunaute then
        print("|cff0099ffAscensionFR|r — couche communautaire |cffff4040"
              .. "COUPÉE|r (nos seules bases). /reload conseillé.")
    else
        print("|cff0099ffAscensionFR|r — couche communautaire |cff00ff00"
              .. "ACTIVE|r. /reload conseillé.")
    end
end

SLASH_AFRFORMAT1 = "/afrformat"
SlashCmdList["AFRFORMAT"] = function(arg)
    print("|cff0099ffAscensionFR|r — essai C_Format")
    if not (C_Format and type(C_Format.Format) == "function") then
        print("  C_Format.Format : ABSENT de ce client")
        return
    end
    local base = AFR.DB and AFR.DB.Sorts or {}
    -- L'identifiant peut venir de TROIS chemins (dans l'ordre) :
    --   1. un lien de sort collé dans la commande (Maj-clic depuis le
    --      grimoire) : /afrformat [Tempête vertueuse] ;
    --   2. un nombre tapé directement ;
    --   3. RIEN : le sort actuellement SURVOLÉ (tape la commande, survole
    --      le sort SANS envoyer, puis Entrée — l'info-bulle est encore là).
    local id = tonumber(string.match(arg or "", "spell:(%d+)"))
        or tonumber(arg)
    local origine = id and "argument"
    if not id and GameTooltip and GameTooltip.IsShown
            and GameTooltip:IsShown() and GameTooltip.GetSpell then
        local ok, trouve = pcall(function()
            return select(3, GameTooltip:GetSpell())
        end)
        if ok and tonumber(trouve) then
            id = tonumber(trouve)
            origine = "info-bulle (GetSpell)"
        end
    end
    if not id and GameTooltip and GameTooltip:IsShown() then
        -- Les info-bulles de TALENTS ne répondent pas à GetSpell : on
        -- reconnaît alors le sort par son NOM affiché en première ligne
        -- (français ou anglais — la base connaît les deux).
        local l1 = _G["GameTooltipTextLeft1"]
        local nom = l1 and l1:GetText()
        if nom and nom ~= "" then
            nom = string.gsub(nom, "|c%x%x%x%x%x%x%x%x", "")
            nom = string.gsub(nom, "|r", "")
            for i, entree in pairs(base) do
                if entree and (entree.N == nom or entree.NE == nom) then
                    id = i
                    origine = "nom affiché (" .. nom .. ")"
                    break
                end
            end
            if not id then
                print("  nom affiché « " .. nom
                      .. " » : introuvable dans la base")
            end
        end
    end
    if not id then
        for i, entree in pairs(base) do
            if entree and entree.DE and string.find(entree.DE, "@%a") then
                id = i
                origine = "témoin automatique"
                break
            end
        end
        print("  (aucun sort visé — tape la commande, survole le sort,"
              .. " puis Entrée ; ou colle son lien Maj-clic)")
    end
    if origine then print("  visé via : " .. origine) end
    local entree = id and base[id]
    if not entree then
        print("  aucun témoin trouvé — donne un identifiant :"
              .. " /afrformat 805409")
        return
    end
    print("  sort " .. id .. " — " .. tostring(entree.N))
    local function essayer(etiquette, texte)
        if not texte then return end
        print("  --- " .. etiquette .. " AVANT : "
              .. string.sub(texte, 1, 110))
        local ok, sorti, lignes = pcall(C_Format.Format, texte,
                                        false, 0, id)
        if not ok then
            print("  " .. etiquette .. " : ERREUR — " .. tostring(sorti))
            return
        end
        print("  " .. etiquette .. " APRÈS : "
              .. string.sub(tostring(sorti), 1, 200))
        if type(lignes) == "table" and #lignes > 0 then
            print("  " .. etiquette .. " : +" .. #lignes
                  .. " ligne(s) annexes")
            for n = 1, math.min(#lignes, 3) do
                print("      " .. string.sub(tostring(lignes[n]), 1, 90))
            end
        end
    end
    essayer("anglais", entree.DE)
    essayer("français", entree.D)
end

-- ============================================================================
-- /afrbulle — RELEVÉ COPIABLE de la dernière GameTooltip (24/07). Les zones
-- de texte GARDENT leur contenu après la fermeture de la bulle : survole le
-- sort, puis tape la commande — l'état exact (codes |c |T compris, affichés
-- bruts dans la fenêtre copiable) est relevé, avec les globales du canal
-- moteur pour vérifier leur application.
-- ============================================================================
SLASH_AFRBULLE1 = "/afrbulle"
SlashCmdList["AFRBULLE"] = function()
    local lignes = {}
    local function noter(t) table.insert(lignes, t) end
    noter("=== /afrbulle — état de GameTooltip ===")
    noter("visible : " .. tostring(GameTooltip:IsShown()))
    local okSort, nomEN, _, idSort = pcall(function()
        return GameTooltip:GetSpell()
    end)
    noter("GetSpell : " .. tostring(okSort and nomEN) .. " / id "
          .. tostring(okSort and idSort))
    local nb = GameTooltip:NumLines()
    noter("NumLines : " .. tostring(nb))
    for i = 1, math.max(nb, 1) do
        local g = _G["GameTooltipTextLeft" .. i]
        local d = _G["GameTooltipTextRight" .. i]
        local tg = g and g:GetText()
        local td = d and d:GetText()
        if tg and tg ~= "" then
            noter("G" .. i .. " : " .. tg)
        end
        if td and td ~= "" then
            noter("D" .. i .. " : " .. td)
        end
    end
    noter("")
    noter("=== crochets déclenchés (depuis le /reload) ===")
    local c = AFR.BulleCompteurs or {}
    noter("OnTooltipSetSpell : " .. tostring(c.sort)
          .. " | rattrapage Show : " .. tostring(c.show))
    if okSort and idSort then
        local fiche = AFR.DB.Sorts and AFR.DB.Sorts[idSort]
        if fiche and fiche.DE then
            for rid in string.gmatch(fiche.DE, "@s:(%d+)") do
                local n = tonumber(rid)
                local enfant = AFR.DB.Sorts[n]
                noter("renvoi @s:" .. rid .. " -> enfant "
                      .. (enfant and "CONNU" or "ABSENT")
                      .. " | GetSpellInfo = " .. tostring(GetSpellInfo(n))
                      .. " | pont noms = " .. tostring(AFR.DB.SortsNoms
                          and AFR.DB.SortsNoms[tostring(GetSpellInfo(n))]))
            end
        end
    end
    noter("")
    noter("=== canal moteur (globales) ===")
    for _, cle in ipairs({ "TOOLTIP_TALENT_RANK", "TOOLTIP_TALENT_LEARN",
                           "TOOLTIP_TALENT_UNLEARN",
                           "TALENT_SPEND_MORE_POINTS", "DODGE" }) do
        noter(cle .. " = " .. tostring(_G[cle]))
    end
    local texte = table.concat(lignes, "\n")
    if AFR.AfficherReleve then
        AFR.AfficherReleve(texte)
    else
        print(texte)
    end
end
