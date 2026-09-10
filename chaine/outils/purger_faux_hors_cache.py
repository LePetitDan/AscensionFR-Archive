# -*- coding: utf-8 -*-
r"""Le lot dédié du bloc 4 : les faux appariements HORS de portée du cache.

Le lot 14 a réparé/purgé tout ce dont le D venait de traductions/sorts.json.
Restaient (recompte du 28/07) 472 échecs « hors cache », dont 367 faux
appariements PURS : leur D vient d'une AUTRE voie — l'appariement officiel
par ID (le frFR Blizzard du même identifiant peut référencer d'autres
variables que l'enUS du client), la jointure par texte normalisé, les
corrections (DB_SortsCorrections) ou la récolte. Un D structurellement
étranger à son DE ne s'affichera JAMAIS (le moteur abandonne) : le garder,
c'est garder un mensonge en base et empêcher la retraduction.

CE QUE FAIT L'OUTIL, pour chaque échec hors cache faux pur :
  1. il établit la PROVENANCE en rejouant les décisions du générateur :
       - officiel par ID   : D == spells_frFR[id].D
       - jointure par texte: D == résolution de l'index officiel normalisé
       - corrections       : le D vit dans DB_SortsCorrections.lua
       - récolte           : D == sorts_recoltes.json[id].D
  2. il PURGE à la source :
       - officiel/jointure : l'ID (ou la clé texte) entre dans
         traductions/appariements_officiels_interdits.json — le générateur
         la consulte et cesse de re-poser ce D à chaque régénération ; le
         DE revient alors en file de traduction (voie du lot 13) ;
       - corrections       : le champ D de l'entrée est retiré du fichier
         (sauvegarde horodatée, compilation lua51 avant remplacement) ;
       - récolte           : le champ D est retiré de sorts_recoltes.json.
  3. LA PREUVE avant d'écrire, même régime que le lot 14 : base modifiée en
     mémoire (D=nil), re-banc complet sur moteur vierge, sorties hachées —
     les purgés disparaissent, zéro régression, zéro sortie commune
     changée. Un seul écart -> refus d'écrire.

Usage :
    python outils/purger_faux_hors_cache.py              # simulation
    python outils/purger_faux_hors_cache.py --appliquer  # écrit
"""
import io
import json
import os
import re
import shutil
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reparer_alignement_sorts as socle  # noqa: E402  (banc + familles)
import mesurer_constantes  # noqa: E402

BASE = socle.BASE
DBC = os.path.join(BASE, "sources", "dbc")
CORRECTIONS = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface"
               r"\AddOns\AscensionFR\DB\DB_SortsCorrections.lua")
RECOLTES = os.path.join(BASE, "traductions", "sorts_recoltes.json")
INTERDITS = os.path.join(BASE, "traductions",
                         "appariements_officiels_interdits.json")
RAPPORT = os.path.join(BASE, "rapports", "faux_hors_cache")


def charger(chemin):
    with io.open(chemin, encoding="utf-8") as f:
        return json.load(f)


def normaliser(texte):
    """La normalisation du générateur (generateur_sorts.normaliser)."""
    import generateur_sorts as gs
    return gs.normaliser(texte)


def main():
    appliquer = "--appliquer" in sys.argv
    lignes_rapport = []

    def dire(texte=""):
        print(texte)
        lignes_rapport.append(texte)

    dire("PURGE DES FAUX APPARIEMENTS HORS CACHE — %s (%s)"
         % (time.strftime("%d/%m/%Y %H:%M"),
            "APPLICATION" if appliquer else "simulation"))
    dire("=" * 66)

    cache = charger(socle.CHEMIN_CACHE)
    descs = cache.get("descriptions", {})
    frfr = charger(os.path.join(DBC, "spells_frFR.json"))
    recoltes = charger(RECOLTES) if os.path.exists(RECOLTES) else {}
    corrections_txt = io.open(CORRECTIONS, encoding="utf-8").read()

    t0 = time.time()
    lua = socle.charger_banc()
    g = lua.globals()
    verdicts, hashes_avant, total = socle.mesurer(lua)
    echecs = sorted(i for i, (v, _) in verdicts.items() if v == "anglais")
    dire("banc AVANT : %d entrées avec D, %d échecs (%.1f s)"
         % (total, len(echecs), time.time() - t0))

    def est_faux_pur(sid, D, DE):
        manquantes = g.ClasserStructure(D, DE)
        mq = [str(x) for x in list(manquantes.values())] if manquantes else []
        if not mq:
            return False
        vars_en = g.VarsEn(sid)
        en_ids = set()
        if vars_en:
            for x in list(vars_en.values()):
                m = socle.RE_ID_VAR.match(str(x))
                if m:
                    en_ids.add(int(m.group(1)))
        return {socle.famille_variable(x, en_ids) for x in mq} \
            == {"faux_appariement"}

    # ------------------------------------------------------------------
    # Classement par provenance — CUMULATIF : les corrections RECOUVRENT la
    # base (dernier écrivain), donc un même id peut exiger à la fois la
    # purge de son entrée de corrections ET la ceinture d'interdits (si la
    # voie officielle ou la jointure re-poserait le même D à la prochaine
    # régénération).
    # ------------------------------------------------------------------
    def desechapper(s):
        s = s.replace("\\\\", "\x00")
        s = s.replace('\\"', '"').replace("\\r", "\r").replace("\\n", "\n")
        return s.replace("\x00", "\\")

    def d_des_corrections(sid):
        # D en tête (`{D="…"`) OU après d'autres champs (`…,D="…"`).
        m = re.search(r'DB\[%d\]=\{(?:[^\n]*?,)?D="((?:[^"\\]|\\.)*)"'
                      % sid, corrections_txt)
        return desechapper(m.group(1)) if m else None

    plan = {"officiel_id": [], "corrections": [], "recolte": [],
            "jointure_texte": [], "inconnue": []}
    for sid in echecs:
        D, DE = socle.lire_champs(g, sid)
        if not D or not DE:
            continue
        if descs.get(DE) is not None:
            continue                       # portée du cache : lot 14, pas ici
        if not est_faux_pur(sid, D, DE):
            continue
        couvert = False
        if d_des_corrections(sid) == D:
            plan["corrections"].append(sid)
            couvert = True
        f = frfr.get(str(sid))
        if f and (f.get("D") or "") == D:
            plan["officiel_id"].append(sid)
            couvert = True
        if (recoltes.get(str(sid)) or {}).get("D") == D:
            plan["recolte"].append(sid)
            couvert = True
        if not couvert:
            # La jointure par texte normalisé (reutilise/chiffres) et tout
            # reste : la clé d'interdiction est le TEXTE anglais du modèle.
            plan["jointure_texte"].append(sid)

    vises = sorted({sid for liste in plan.values() for sid in liste})
    dire("")
    dire("PROVENANCE des faux appariements hors cache (%d visés — un id "
         "peut cumuler) :" % len(vises))
    for voie in ("corrections", "officiel_id", "jointure_texte", "recolte",
                 "inconnue"):
        dire("  %-16s : %4d" % (voie, len(plan[voie])))

    # ------------------------------------------------------------------
    # LA PREUVE : D=nil en mémoire pour les visés, re-banc, hachages.
    # ------------------------------------------------------------------
    dire("")
    t0 = time.time()
    lua2 = socle.charger_banc()
    for sid in vises:
        lua2.execute("if AscensionFR.DB.Sorts[%d] then "
                     "AscensionFR.DB.Sorts[%d].D = nil end" % (sid, sid))
    verdicts2, hashes_apres, total2 = socle.mesurer(lua2)
    echecs2 = sorted(i for i, (v, _) in verdicts2.items() if v == "anglais")
    dire("banc APRÈS (purge en mémoire) : %d entrées, %d échecs (%.1f s)"
         % (total2, len(echecs2), time.time() - t0))

    problemes = []
    disparus = sorted(set(verdicts) - set(verdicts2))
    if set(disparus) != set(vises):
        problemes.append("disparus != visés : %s"
                         % sorted(set(disparus) ^ set(vises))[:10])
    regressions = [i for i in verdicts2
                   if verdicts2[i][0] == "anglais"
                   and verdicts.get(i, ("?",))[0] == "traduit"]
    if regressions:
        problemes.append("régressions : %s" % regressions[:10])
    changes = [i for i, h in hashes_avant.items()
               if i in hashes_apres and hashes_apres[i] != h]
    if changes:
        problemes.append("sorties changées : %s" % sorted(changes)[:10])
    dire("")
    dire("PREUVE PAR LES SORTIES HACHÉES : échecs %d -> %d ; disparus %d ; "
         "régressions %d ; sorties communes changées %d"
         % (len(echecs), len(echecs2), len(disparus), len(regressions),
            len(changes)))
    if problemes:
        dire("REFUS D'ÉCRIRE :")
        for p in problemes:
            dire("  ! %s" % p)

    # ------------------------------------------------------------------
    # Écriture, à la source de chaque provenance.
    # ------------------------------------------------------------------
    if appliquer and vises and not problemes:
        horodatage = time.strftime("%Y%m%d-%H%M%S")
        interdits = charger(INTERDITS) if os.path.exists(INTERDITS) else {}
        for sid in plan["officiel_id"]:
            interdits["id:%d" % sid] = ("bloc 4 : le frFR officiel de cet ID "
                                        "ne traduit pas le DE du client")
        for sid in plan["jointure_texte"] + plan["inconnue"]:
            _D, DE = socle.lire_champs(g, sid)
            if DE:
                interdits["texte:" + DE] = ("bloc 4 : jointure par texte "
                                            "prouvée fausse au banc")
        with io.open(INTERDITS, "w", encoding="utf-8") as f:
            json.dump(interdits, f, ensure_ascii=False, indent=1,
                      sort_keys=True)
        dire("")
        dire("appariements interdits (cumul) : %d -> %s"
             % (len(interdits), os.path.relpath(INTERDITS, BASE)))

        if plan["corrections"]:
            neuf = corrections_txt
            purges_corr = 0
            for sid in plan["corrections"]:
                # retire le champ D de l'entrée DB[sid]={...} — en tête
                # (`{D="…",`) ou après une virgule (`,D="…"`). Si D était le
                # SEUL champ, l'entrée entière saute (une table vide
                # écraserait l'entrée de base et perdrait son nom).
                ligne_seule = re.compile(
                    r'DB\[%d\]=\{D="(?:[^"\\]|\\.)*"\}\r?\n?' % sid)
                neuf2, n = ligne_seule.subn("", neuf)
                if not n:
                    neuf2, n = re.subn(
                        r'(DB\[%d\]=\{[^\n]*?),D="(?:[^"\\]|\\.)*"' % sid,
                        r"\1", neuf)
                if not n:
                    neuf2, n = re.subn(
                        r'(DB\[%d\]=\{)D="(?:[^"\\]|\\.)*",' % sid,
                        r"\1", neuf)
                neuf = neuf2
                purges_corr += n
            ok, _k, message = mesurer_constantes.mesurer(
                neuf.encode("utf-8"), os.path.basename(CORRECTIONS))
            if not ok:
                dire("STOP corrections : le résultat ne compile pas (%s) — "
                     "fichier laissé intact" % message)
            else:
                sauve = os.path.join(BASE, "rapports",
                                     "DB_SortsCorrections_avant_bloc4_%s.lua"
                                     % horodatage)
                shutil.copy2(CORRECTIONS, sauve)
                with io.open(CORRECTIONS, "w", encoding="utf-8",
                             newline="\n") as f:
                    f.write(neuf)
                dire("corrections : %d champ(s) D retiré(s) (sauvegarde %s)"
                     % (purges_corr, os.path.basename(sauve)))

        if plan["recolte"]:
            shutil.copy2(RECOLTES, RECOLTES.replace(
                ".json", "_avant_bloc4_%s.json" % horodatage))
            for sid in plan["recolte"]:
                (recoltes.get(str(sid)) or {}).pop("D", None)
            with io.open(RECOLTES, "w", encoding="utf-8") as f:
                json.dump(recoltes, f, ensure_ascii=False, indent=1,
                          sort_keys=True)
            dire("récolte : %d champ(s) D retiré(s)" % len(plan["recolte"]))
        dire("")
        dire("(la base sera mise au niveau par la chaîne complète — le DE de "
             "chaque purgé revient en file de traduction)")
    elif not appliquer:
        dire("")
        dire("SIMULATION : rien n'a été écrit. Relancer avec --appliquer.")

    os.makedirs(os.path.dirname(RAPPORT) or ".", exist_ok=True)
    chemin_rapport = "%s_%s_%s.txt" % (
        RAPPORT, time.strftime("%Y%m%d-%H%M%S"),
        "application" if appliquer else "simulation")
    with io.open(chemin_rapport, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes_rapport) + "\n")
        f.write("\nids visés (%d) : %s\n" % (len(vises), vises))
    print()
    print("rapport -> %s" % chemin_rapport)
    return 0 if not problemes else 1


if __name__ == "__main__":
    sys.exit(main())
