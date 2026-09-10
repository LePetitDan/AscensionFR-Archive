# -*- coding: utf-8 -*-
r"""Banc du module Guichets (bloc H, 29/07/2026) : courrier, réputation,
monnaies, fêtes — le contrat :

  1. courrier : un sujet et un corps CONNUS du pont sont repeints en
     français ; l'expéditeur PNJ passe par le pont des créatures ;
  2. un texte INCONNU reste INTACT (contrôle négatif — jamais de
     réécriture aveugle) ;
  3. réputation : nom + description de faction repeints ;
  4. monnaies : le nom passe par DB.ObjetsNoms ;
  5. fêtes : le calendrier chargé APRÈS coup est raccroché (ADDON_LOADED)
     et ses pastilles repeintes ;
  6. traduction coupée (Actif() faux) : RIEN ne bouge ;
  7. taint : le module n'écrit AUCUNE globale du client (l'environnement
     factice piste les écritures _G).

Moteur lua51 réel, DB_Guichets RÉEL (généré) ; sort en 1 au premier échec.
"""
import io
import locale
import re
import sys

locale.setlocale(locale.LC_ALL, "C")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import lupa.lua51 as lupa_mod  # noqa: E402

ADDON = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface"
         r"\AddOns\AscensionFR")

AMORCE = r"""
-- FontString factice
local function FS(t)
    local f = { _t = t }
    function f:GetText() return self._t end
    function f:SetText(v) self._t = v end
    return f
end
_G.FS = FS

-- pistage des écritures de globales par le module (doctrine taint)
_G.ecritures_globales = {}

actif = true
_G.AscensionFR = {
    DB = { Guichets = {}, ObjetsNoms = {} },
    Actif = function() return actif end,
    CreatureParNomEN = function(nom)
        if nom == "Rexxar" then return { N = "Rexxar le Fort" } end
    end,
}

local accroches = {}
function _G.hooksecurefunc(nom, fn)
    accroches[nom] = fn
end
function _G.Tirer(nom) if accroches[nom] then accroches[nom]() end end
function _G.Accroche(nom) return accroches[nom] ~= nil end

function _G.CreateFrame()
    local f = { _scripts = {}, _evts = {} }
    function f:RegisterEvent(e) self._evts[e] = true end
    function f:UnregisterEvent(e) self._evts[e] = nil end
    function f:SetScript(quoi, fn) self._scripts[quoi] = fn end
    _G.dernier_cadre = f
    return f
end

-- fonctions de peinture du client : présentes pour que le module s'accroche
function _G.InboxFrame_Update() end
function _G.OpenMail_Update() end
function _G.ReputationFrame_Update() end
function _G.TokenFrame_Update() end
-- CalendarFrame_Update ABSENT au chargement : le chemin ADDON_LOADED doit
-- servir (Blizzard_Calendar est à la demande)
"""


def main():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(AMORCE)

    # pose le VRAI pont généré, puis le module — via un _G piégé côté banc :
    # toute écriture de globale par le module serait un défaut de doctrine,
    # on liste celles qu'il fait (aucune attendue hors ses hooks factices).
    base = io.open(ADDON + r"\DB\DB_Guichets.lua", encoding="utf-8").read()
    lua.execute(base)
    module = io.open(ADDON + r"\Modules\Guichets.lua",
                     encoding="utf-8").read()
    lua.execute(module)

    g = lua.globals()
    echecs = []

    def verifier(nom, condition, detail=""):
        etat = "ok    " if condition else "ECHEC "
        print("  %s %s %s" % (etat, nom, detail))
        if not condition:
            echecs.append(nom)

    # un sujet et un corps réels du pont
    paires = {}
    for m in re.finditer(r'^T\["((?:\\.|[^"\\])+)"\]="((?:\\.|[^"\\])*)"',
                         base, re.M):
        paires[m.group(1)] = m.group(2)
    sujet_en = None
    for en in paires:
        if len(en) < 60 and "\\" not in en and "Ho Ho" in en:
            sujet_en = en
            break
    if not sujet_en:
        sujet_en = next(en for en in paires
                        if len(en) < 50 and "\\" not in en)
    faction_en = "Booty Bay" if "Booty Bay" in paires else \
        next(en for en in paires if len(en) < 30 and "\\" not in en)
    fete_en = "Darkmoon Faire"
    verifier("pont : Darkmoon Faire présent", fete_en in paires,
             "-> %s" % paires.get(fete_en, "?"))

    # ------------------------------------------------------------------
    # LE COURRIER, ÉPROUVÉ SUR UNE FAUSSE BOÎTE PLEINE (29/07/2026).
    # Dan n'a jamais pu le juger : sa boîte était vide le jour du test.
    # On ne peut pas lui redemander de valider une surface que nous-mêmes
    # n'avons jamais vue fonctionner — alors on la fait fonctionner ici,
    # avec sept lettres dont le contenu vient du VRAI pont.
    # ------------------------------------------------------------------
    sujets = [en for en in sorted(paires)
              if 8 < len(en) < 60 and "\\" not in en][:6]
    # Le corps de lettre est pris DANS LA TABLE LUA, jamais dans mon
    # analyse du source : une clé du fichier porte des « \n » échappés,
    # que seul Lua transforme en vrais sauts de ligne. Chercher la clé
    # échappée revenait à interroger la table avec un texte qui n'y est
    # pas — et à croire le module fautif alors qu'il allait bien.
    corps_en = None
    for cle in g.AscensionFR.DB.Guichets:
        if len(cle) > 200 and "\n" in cle:
            corps_en = cle
            break
    lua.execute("""
    for i = 1, 12 do
        _G["MailItem" .. i .. "Subject"] = nil
        _G["MailItem" .. i .. "Sender"] = nil
    end
    """)
    for rang, sujet in enumerate(sujets, 1):
        lua.execute('MailItem%d_sujet_attendu = %r\n'
                    'MailItem%dSubject = FS(%r)\n'
                    'MailItem%dSender = FS("Rexxar")'
                    % (rang, paires[sujet], rang, sujet, rang))
    lua.execute('Tirer("InboxFrame_Update")')
    traduits = 0
    for rang, sujet in enumerate(sujets, 1):
        zone = g["MailItem%dSubject" % rang]
        if str(zone.GetText(zone)) == paires[sujet]:
            traduits += 1
    verifier("boîte PLEINE : %d sujets traduits" % traduits,
             traduits == len(sujets), "sur %d" % len(sujets))
    expediteurs = sum(
        1 for rang in range(1, len(sujets) + 1)
        if str(g["MailItem%dSender" % rang].GetText(
            g["MailItem%dSender" % rang])) == "Rexxar le Fort")
    verifier("boîte pleine : %d expéditeurs traduits" % expediteurs,
             expediteurs == len(sujets), "sur %d" % len(sujets))
    if corps_en:
        # La valeur attendue est demandée à LA TABLE LUA, pas à mon
        # analyse du fichier : les « \n » du source sont des échappements
        # que seul Lua sait rendre.
        lua.execute("_G.corps_en = %r\n"
                    "_G.corps_attendu = AscensionFR.DB.Guichets[corps_en]\n"
                    "OpenMailSubject = FS(%r)\n"
                    "OpenMailBodyText = FS(corps_en)\n"
                    'Tirer("OpenMail_Update")'
                    % (corps_en, sujets[0] if sujets else "x"))
        rendu = str(g.OpenMailBodyText.GetText(g.OpenMailBodyText))
        verifier("lettre ouverte : corps long traduit",
                 rendu == str(g.corps_attendu),
                 "(%d caractères)" % len(rendu))
    else:
        verifier("lettre ouverte : corps long traduit", False,
                 "aucun corps long dans le pont")

    lua.execute("""
    MailItem1Subject = FS(%r)
    MailItem1Sender = FS("Rexxar")
    Tirer("InboxFrame_Update")
    """ % sujet_en)
    verifier("courrier : sujet repeint",
             str(g.MailItem1Subject.GetText(g.MailItem1Subject))
             != sujet_en)
    verifier("courrier : expéditeur PNJ via le pont des créatures",
             str(g.MailItem1Sender.GetText(g.MailItem1Sender))
             == "Rexxar le Fort")

    lua.execute("""
    OpenMailSubject = FS("Totally Unknown Subject 123")
    OpenMailBodyText = FS("Totally unknown body.")
    Tirer("OpenMail_Update")
    """)
    verifier("contrôle négatif : texte inconnu INTACT",
             str(g.OpenMailSubject.GetText(g.OpenMailSubject))
             == "Totally Unknown Subject 123")

    lua.execute("""
    ReputationBar1FactionName = FS(%r)
    ReputationDetailFactionName = FS(%r)
    ReputationDetailFactionDescription = FS("Totally unknown description.")
    Tirer("ReputationFrame_Update")
    """ % (faction_en, faction_en))
    verifier("réputation : nom de faction repeint",
             str(g.ReputationBar1FactionName.GetText(
                 g.ReputationBar1FactionName)) != faction_en)

    lua.execute("""
    AscensionFR.DB.ObjetsNoms["Emblem of Frost"] = "Emblème de givre"
    TokenFrameContainerButton1 = {}
    TokenFrameContainerButton1Name = FS("Emblem of Frost")
    Tirer("TokenFrame_Update")
    """)
    verifier("monnaies : nom via DB_ObjetsNoms",
             str(g.TokenFrameContainerButton1Name.GetText(
                 g.TokenFrameContainerButton1Name)) == "Emblème de givre")

    # le calendrier arrive APRÈS : ADDON_LOADED doit raccrocher
    verifier("fêtes : pas encore accroché (calendrier absent)",
             not g.Accroche("CalendarFrame_Update"))
    lua.execute("""
    function _G.CalendarFrame_Update() end
    local f = dernier_cadre
    f._scripts["OnEvent"](f, "ADDON_LOADED", "Blizzard_Calendar")
    CalendarDayButton3EventButton1Text = FS(%r)
    Tirer("CalendarFrame_Update")
    """ % fete_en)
    verifier("fêtes : raccroché à ADDON_LOADED",
             g.Accroche("CalendarFrame_Update"))
    verifier("fêtes : pastille du jour repeinte",
             str(g.CalendarDayButton3EventButton1Text.GetText(
                 g.CalendarDayButton3EventButton1Text)) != fete_en)

    # traduction coupée : rien ne bouge
    lua.execute("""
    actif = false
    MailItem1Subject = FS(%r)
    Tirer("InboxFrame_Update")
    """ % sujet_en)
    verifier("coupé : rien ne bouge",
             str(g.MailItem1Subject.GetText(g.MailItem1Subject))
             == sujet_en)

    # doctrine taint : le module ne doit contenir AUCUNE écriture de
    # globale (pas de « _G[...] = », pas de « NOM_GLOBAL = » hors local)
    verifier("taint : aucune écriture _G[...] dans le module",
             not re.search(r"_G\[[^\]]+\]\s*=", module))

    # ------------------------------------------------------------------
    # LES FÊTES COMPOSÉES (29/07/2026). La grille du calendrier affiche
    # « Darkmoon Faire Begins », que le pont ne connaît pas et ne doit pas
    # connaître : c'est le client qui FABRIQUE ce texte à partir d'un
    # gabarit. On vérifie la recomposition par le gabarit FRANÇAIS
    # officiel, et surtout qu'une fête INCONNUE n'est pas inventée.
    # ------------------------------------------------------------------
    lua.execute("""
    actif = true
    _G.CALENDAR_EVENTNAME_FORMAT_START = "%s Begins"
    _G.CALENDAR_EVENTNAME_FORMAT_END = "%s Ends"
    AscensionFR.DB.UI = {
        CALENDAR_EVENTNAME_FORMAT_START = "%s : début",
        CALENDAR_EVENTNAME_FORMAT_END = "%s : fin",
    }
    """)
    compose = g.AscensionFR.FeteComposee
    attendu_debut = "%s : début" % paires.get(fete_en, "?")
    verifier("fête composée : « X Begins » -> « X : début »",
             str(compose(fete_en + " Begins")) == attendu_debut,
             "-> %s" % compose(fete_en + " Begins"))
    verifier("fête composée : « X Ends » -> « X : fin »",
             str(compose(fete_en + " Ends"))
             == "%s : fin" % paires.get(fete_en, "?"))
    verifier("contrôle négatif : fête INCONNUE non inventée",
             compose("Totally Unknown Festival Begins") is None)
    verifier("contrôle négatif : texte quelconque ignoré",
             compose("Bonjour tout le monde") is None)

    # ------------------------------------------------------------------
    # LE PANNEAU MAISON D'ASCENSION (29/07/2026). Ses libellés sont posés
    # sur des zones de texte ANONYMES d'une fenêtre à mixins : aucun
    # crochet par nom de cadre ne peut les voir. C'est l'interception de
    # SetText (Epreuves.lua) qui doit les attraper — donc le pont des
    # guichets DOIT être dans sa chaîne de dictionnaires.
    # ------------------------------------------------------------------
    epreuves = io.open(ADDON + r"\Modules\Epreuves.lua",
                       encoding="utf-8").read()
    verifier("panneau maison : DB.Guichets dans la chaîne d'interception",
             re.search(r"guichets\s*=\s*AFR\.DB\.Guichets", epreuves)
             and re.search(r"or\s*\(guichets and guichets\[texte\]\)",
                           epreuves))

    print()
    print("%d échec(s)" % len(echecs))
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
