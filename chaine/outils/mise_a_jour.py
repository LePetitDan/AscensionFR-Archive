# -*- coding: utf-8 -*-
"""
Remet toute la traduction d'aplomb, notamment après une mise à jour d'Ascension.

Pourquoi c'est nécessaire : nos données sont extraites du client. Quand
Ascension le patche, elles deviennent périmées.
  - nouveaux sorts / objets  -> ils s'afficheraient en anglais ;
  - interface modifiée       -> DB_ListeNoire.lua, calculée depuis LEUR code,
                                devient fausse. Une chaîne nouvellement lue par
                                du code protégé bloquerait les barres d'action
                                du joueur (« tainted the call of the secure
                                function 'UseAction()' »). C'est le vrai
                                danger : le jeu devient injouable.

Le client est identifié par une signature (taille + date des archives dont on
dépend). Tant qu'elle ne bouge pas, on saute la réextraction, qui est longue.

Usage :
    python mise_a_jour.py            # ne refait que le nécessaire
    python mise_a_jour.py --force    # tout réextraire
    python mise_a_jour.py --verifier # dire seulement si une maj est requise
"""
import json
import os
import struct
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTILS = os.path.join(BASE, "outils")
DBC = os.path.join(BASE, "sources", "dbc")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chemin_client import JEU  # noqa: E402
ETAT = os.path.join(BASE, "etat_client.json")

# Fichiers du client dont dépendent nos données. Découverts en explorant les
# 64 archives : ne pas se fier aux emplacements « standard » de WoW.
SOURCES = {
    # archive -> [(fichier interne, nom de sortie)]
    os.path.join(JEU, "Data", "patch-T.MPQ"): [
        ("DBFilesClient\\Spell.dbc", "Spell_Ascension.dbc"),
    ],
    os.path.join(JEU, "Data", "patch-M.MPQ"): [
        ("DBFilesClient\\SkillLineAbility.dbc", "SkillLineAbility_Ascension.dbc"),
        ("DBFilesClient\\SkillLine.dbc", "SkillLine_Ascension.dbc"),
        ("DBFilesClient\\Talent.dbc", "Talent_Ascension.dbc"),
    ],
    os.path.join(JEU, "Data", "enUS", "patch-enUS-3.MPQ"): [
        ("DBFilesClient\\Spell.dbc", "Spell_enUS.dbc"),
    ],
    os.path.join(BASE, "sources", "patch-frFR-3.MPQ"): [
        ("DBFilesClient\\Spell.dbc", "Spell_frFR.dbc"),
    ],
    # patch-B contient le FrameXML modifié d'Ascension : c'est lui qui décide
    # de la liste noire anti-blocage. Il porte aussi le GlueXML (leur écran de
    # création, et le .toc qui décide si notre point d'entrée est chargé).
    os.path.join(JEU, "Data", "patch-B.MPQ"): [],
}

# Ces DBC de patch-M portent les noms de races/classes et les textes maison
# d'Ascension (fiches de classe de l'écran de création).
SOURCES[os.path.join(JEU, "Data", "patch-M.MPQ")] += [
    ("DBFilesClient\\ChrClasses.dbc", "ChrClasses_Ascension.dbc"),
    ("DBFilesClient\\ChrRaces.dbc", "ChrRaces_Ascension.dbc"),
    ("DBFilesClient\\GlobalStrings.dbc", "GlobalStrings_Ascension.dbc"),
]

# LA CARTE DES BASES (bloc E, 29/07/2026). L'audit a trouvé 9 bases sur 26
# régénérées par AUCUN chemin standard — dont DB_LuesClient, l'anti-taint.
# Chaque base du .toc a ici son chemin de régénération ; verifier_tout
# confronte cette carte au .toc et MORD si une base n'y figure pas : plus
# jamais d'orpheline silencieuse. None = base d'ACCUMULATION (elle grandit
# au fil des rapports, la « régénérer » n'a pas de sens) — décision
# explicite, pas un oubli.
REGENERATEURS = {
    "DB_Meta.lua": "compter_total.py",
    "DB_ListeNoire.lua": "generer_listenoire.py",
    "DB_LuesClient.lua": "extraire_lues_client.py",
    "DB_Reglages.lua": "extraire_reglages.py",
    "DB_Interface.lua": "generateur_db.py",
    "DB_Quetes.lua": "generateur_db.py",
    "DB_Objets.lua": "generateur_db.py",
    "DB_Creatures.lua": "generateur_db.py",
    "DB_ObjetsMonde.lua": "generateur_db.py",
    "DB_TextesPNJ.lua": "generateur_db.py",
    "DB_Gossip.lua": "generateur_db.py",
    "DB_Pages.lua": "generateur_db.py",
    "DB_Divers.lua": "generateur_db.py",
    "DB_Libelles.lua": "generateur_db.py",
    "DB_Sorts.lua": "generateur_sorts.py",
    "DB_SortsNoms.lua": "generer_noms_sorts.py",
    "DB_ObjetsNoms.lua": "generer_noms_objets.py",
    "DB_Zones.lua": "traduire_zones.py",
    "DB_Emotes.lua": "generateur_emotes.py",
    "DB_Epreuves.lua": "traduire_epreuves.py",
    "DB_HautsFaits.lua": "traduire_hautsfaits.py",
    "DB_QuetesObjectifs.lua": "generer_objectifs_quetes.py",
    "DB_SortsLignes.lua": "adopter_frenchtooltip.py",
    "DB_AddonsTiers.lua": "traduire_dragonui.py",
    "DB_SortsCorrections.lua": None,   # accumulation (ingerer_rapport)
    "DB_Communaute.lua": None,         # accumulation (harmoniser_communaute)
    "DB_Guichets.lua": "generer_guichets.py",   # courrier/factions/fêtes
}

# Les bases ANNEXES régénérées en fin de 6/6, dans cet ordre. Leurs échecs
# n'interrompent pas la chaîne (le critique est déjà passé) mais font
# échouer la mise à jour À LA FIN — bruyamment, jamais en silence.
ANNEXES = [
    "generateur_emotes.py",
    "traduire_epreuves.py",
    "traduire_hautsfaits.py",
    "generer_objectifs_quetes.py",
    "traduire_zones.py",
    "adopter_frenchtooltip.py",
    "traduire_dragonui.py",
    "generer_guichets.py",
    "compter_total.py",
]


def afficher(message):
    """Écrit sur la console sans jamais planter.

    La console Windows est en cp1252 : elle ne sait pas afficher tous les
    caractères que nos outils produisent. Un accent ne doit pas interrompre
    une mise à jour.
    """
    try:
        print(message)
    except UnicodeEncodeError:
        encodage = (sys.stdout.encoding or "ascii")
        print(message.encode(encodage, "replace").decode(encodage, "replace"))


def signature():
    """Empreinte du client : taille + date des archives dont on dépend."""
    s = {}
    for archive in SOURCES:
        if os.path.exists(archive):
            st = os.stat(archive)
            s[os.path.basename(archive)] = [st.st_size, int(st.st_mtime)]
    return s


def etat_precedent():
    if os.path.exists(ETAT):
        try:
            with open(ETAT, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def client_modifie():
    """(modifié, détails) — le client a-t-il changé depuis la dernière fois ?"""
    avant = etat_precedent().get("signature", {})
    maintenant = signature()
    if not avant:
        return True, "première exécution"
    changes = [n for n in maintenant if avant.get(n) != maintenant[n]]
    disparus = [n for n in avant if n not in maintenant]
    if changes or disparus:
        return True, "archives modifiées : " + ", ".join(changes + disparus)
    return False, "client inchangé"


def extraire_dbc(journal=afficher):
    """Extrait les DBC nécessaires depuis les archives du client."""
    from mpyq import MPQArchive
    os.makedirs(DBC, exist_ok=True)
    for archive, fichiers in SOURCES.items():
        if not fichiers:
            continue
        if not os.path.exists(archive):
            journal("  ! archive absente : %s" % os.path.basename(archive))
            continue
        try:
            a = MPQArchive(archive)
        except Exception as e:
            journal("  ! %s illisible : %s" % (os.path.basename(archive), e))
            continue
        for interne, sortie in fichiers:
            try:
                donnees = a.read_file(interne)
            except Exception:
                donnees = None
            if not donnees:
                journal("  ! %s introuvable dans %s"
                        % (interne, os.path.basename(archive)))
                continue
            chemin = os.path.join(DBC, sortie)
            with open(chemin, "wb") as f:
                f.write(donnees)
            # Contrôle : un DBC valide commence par WDBC
            with open(chemin, "rb") as f:
                magic = f.read(4)
            if magic != b"WDBC":
                raise ValueError("%s : pas un DBC valide (%r)" % (sortie, magic))
            journal("  %-32s %8d octets" % (sortie, len(donnees)))


def entete_dbc(nom):
    chemin = os.path.join(DBC, nom)
    with open(chemin, "rb") as f:
        magic, nb, nch, ts, sb = struct.unpack("<4sIIII", f.read(20))
    return nb, nch


def lancer(script, arguments=None, journal=afficher):
    """Exécute un outil du dossier outils/ et remonte son échec."""
    commande = [sys.executable, os.path.join(OUTILS, script)] + (arguments or [])
    r = subprocess.run(commande, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=BASE)
    if r.returncode != 0:
        journal("  ECHEC de %s :" % script)
        for ligne in (r.stderr or "").strip().split("\n")[-6:]:
            journal("     " + ligne)
        return False
    for ligne in (r.stdout or "").strip().split("\n"):
        if ligne.strip() and not ligne.startswith("  -"):
            journal("     " + ligne.strip())
    return True


def convertir_spells(journal=afficher):
    """Convertit les Spell.dbc en JSON exploitables."""
    sys.path.insert(0, OUTILS)
    import parser_dbc
    for source, sortie in [("Spell_Ascension.dbc", "spells_Ascension.json"),
                           ("Spell_enUS.dbc", "spells_enUS.json"),
                           ("Spell_frFR.dbc", "spells_frFR.json")]:
        chemin = os.path.join(DBC, source)
        if not os.path.exists(chemin):
            journal("  ! %s absent" % source)
            continue
        d = parser_dbc.parser_spell(chemin)
        with open(os.path.join(DBC, sortie), "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1, sort_keys=True)
        journal("  %-24s %6d sorts nommés" % (sortie, len(d)))


def executer(force=False, journal=afficher):
    """Refait ce qui doit l'être. Renvoie True si tout s'est bien passé."""
    modifie, raison = client_modifie()
    if force:
        modifie, raison = True, "réextraction forcée"

    if modifie:
        journal("Mise à jour du client détectée (%s)." % raison)
        journal("Réextraction des données du jeu — quelques minutes...")
        try:
            journal("1/6 Extraction des DBC")
            extraire_dbc(journal)
            journal("2/6 Conversion des sorts")
            convertir_spells(journal)
        except Exception as e:
            journal("  ECHEC : %s" % e)
            journal("  Les anciennes données restent en place.")
            return False
        journal("3/6 Libellés d'interface (sous-classes, métiers)")
        if not lancer("extraire_libelles.py", journal=journal):
            return False
        journal("4/6 Liste noire anti-blocage (calculée depuis le code du jeu)")
        if not lancer("generer_listenoire.py", journal=journal):
            journal("  ATTENTION : sans cette liste, les barres d'action du")
            journal("  joueur risquent d'être bloquées. Mise à jour annulée.")
            return False
        # DB_LuesClient — « ce que le client LIT » — dérive du MÊME code
        # client que la liste noire, mais n'était rafraîchie par AUCUN
        # chemin (le trou n° 1 de l'audit, bloc E). Même criticité : une
        # chaîne nouvellement lue par du code protégé bloquerait les
        # barres d'action sans qu'aucun outil ne l'annonce.
        if not lancer("extraire_lues_client.py", journal=journal):
            journal("  ATTENTION : liste des chaînes lues par le client non")
            journal("  rafraîchie — même danger de blocage. Annulée.")
            return False
        if not lancer("extraire_reglages.py", journal=journal):
            journal("  (réglages non rafraîchis — le reste continue)")
    else:
        journal("Client inchangé : pas de réextraction.")

    # --- Écrans d'avant le jeu (connexion, sélection, création) ------------
    # Ils ne passent pas par l'addon : leur traduction est un fichier posé
    # dans le point d'entrée que le client réclame (Interface\PTRXML). Le
    # générateur relit les archives, prévient si Ascension a retiré ce point
    # d'entrée de son .toc, et signale les textes nouveaux à traduire.
    journal("5/6 Écrans de connexion et de création")
    if not lancer("extraire_globalstrings_dbc.py", journal=journal):
        journal("  (fiches de classe non rafraîchies — le reste continue)")
    if not lancer("generateur_glue.py", ["--porte"], journal=journal):
        journal("  ATTENTION : l'écran de création n'a pas été régénéré ;")
        journal("  il gardera sa version précédente.")

    journal("6/6 Régénération des bases de l'addon")
    # Extraction des caches WDB de TOUS les royaumes vus par cette machine
    # (pas seulement Rexxar). Chaque royaume est un cache serveur qui peut
    # porter du contenu propre (Vol'jin, Darkmoon Wildcard, Dawnrise…) ; on
    # extrait chacun dans extraits/<slug>. Rexxar reste requis (le mode de
    # Dan) ; l'échec d'un royaume secondaire n'arrête pas le build.
    dossier_wdb = os.path.join(JEU, "Cache", "WDB", "enUS")
    royaumes = sorted(d for d in os.listdir(dossier_wdb)
                      if os.path.isdir(os.path.join(dossier_wdb, d))) \
        if os.path.isdir(dossier_wdb) else []
    rexxar_ok = False
    for royaume in royaumes:
        slug = "".join(c for c in royaume.split(" - ")[0].lower()
                       if c.isalnum()) or "royaume"
        ok = lancer("parser_wdb.py",
                    [os.path.join(dossier_wdb, royaume),
                     os.path.join(BASE, "extraits", slug)], journal=journal)
        if slug == "rexxar":
            rexxar_ok = ok
        elif not ok:
            journal(f"  (royaume {royaume} non extrait — le reste continue)")
    if not rexxar_ok:
        return False
    if not lancer("generateur_sorts.py", journal=journal):
        return False
    if not lancer("generateur_db.py", journal=journal):
        return False
    # optimiser_memoire : le README l'exige après TOUT generateur_db (il pose
    # DB_Objets au format paresseux). Sans effet quand tout est déjà
    # paresseux — mais l'oubli, lui, livrerait un fichier plat qui dépasse la
    # limite de constantes de Lua 5.1 : addon mort au chargement.
    if not lancer("optimiser_memoire.py", journal=journal):
        return False
    # LES PONTS PAR NOM (lot 10, 27/07/2026). Ils étaient le TROU de cette
    # chaîne : personne ne les lançait, donc DB_SortsNoms.lua et
    # DB_ObjetsNoms.lua vivaient sur leur version d'avant — même famille que
    # l'oubli de DB_Objets au lot 3 : plusieurs chemins font le travail, tous
    # ne font pas la dernière étape, et l'oubli ne se voit pas.
    # L'ORDRE COMPTE : la couche « custom » de generer_noms_sorts relit
    # DB_Sorts.lua (pas le cache), il doit donc passer APRÈS les générateurs.
    if not lancer("generer_noms_sorts.py", journal=journal):
        return False
    if not lancer("generer_noms_objets.py", journal=journal):
        return False

    # Les bases ANNEXES (bloc E) : les 9 orphelines de l'audit ont
    # désormais leur chemin. Le critique est déjà passé — un échec ici ne
    # s'interpose pas, mais il fait échouer la mise à jour À LA FIN,
    # bruyamment : les pannes silencieuses sont LE défaut du pipeline.
    rates = []
    for annexe in ANNEXES:
        if not lancer(annexe, journal=journal):
            rates.append(annexe)
            journal("  (%s en échec — la suite continue, échec TOTAL "
                    "à la fin)" % annexe)

    with open(ETAT, "w", encoding="utf-8") as f:
        json.dump({"signature": signature()}, f, indent=1)
    if rates:
        journal("Mise à jour INCOMPLÈTE : %d base(s) annexe(s) non "
                "régénérée(s) : %s" % (len(rates), ", ".join(rates)))
        return False
    journal("Mise à jour terminée. Tapez /reload en jeu.")
    return True


if __name__ == "__main__":
    if "--verifier" in sys.argv:
        modifie, raison = client_modifie()
        print("Mise à jour nécessaire" if modifie else "À jour", "(%s)" % raison)
        sys.exit(1 if modifie else 0)
    ok = executer(force="--force" in sys.argv)
    sys.exit(0 if ok else 1)
