# -*- coding: utf-8 -*-
"""Récolte tout ce qu'il faut pour les ÉMOTES françaises (2.1) :

1. COMMANDES : clés EMOTE<n>_CMD<m> — l'anglais vient des GlobalStrings
   du jeu (« /hello »), le français officiel de notre DB_Interface
   (« /bonjour », hérité du frFR Blizzard).
2. PHRASES DU TCHAT : EmotesTextData.dbc enUS (jeu) x frFR
   (sources/patch-frFR-3.MPQ), appariées par identifiant —
   « You flirt. » -> « Vous draguez avec tout le monde. », gabarits %s
   compris.

Sortie : traductions/emotes.json { commandes: {clé: {en, fr}},
tchat: {EN: FR} }.
"""
import glob
import io
import json
import os
import re
import struct
import sys

sys.stdout.reconfigure(encoding="utf-8")
from mpyq import MPQArchive

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Data"
DB_UI = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
         r"\AscensionFR\DB\DB_Interface.lua")
FRFR = os.path.join(BASE, "sources", "patch-frFR-3.MPQ")
SORTIE = os.path.join(BASE, "traductions", "emotes.json")

RE_CMD = re.compile(r"^EMOTE\d+_CMD\d+$")


def wdbc(donnees):
    """[(vals...)], chaînes résolues paresseusement via texte()."""
    nb, champs, taille, bloc = struct.unpack("<4I", donnees[4:20])
    debut = 20 + nb * taille
    chaines = donnees[debut:debut + bloc]

    def texte(v):
        if v <= 0 or v >= len(chaines):
            return ""
        fin = chaines.find(b"\0", v)
        return chaines[v:fin].decode("utf-8", "replace")

    lignes = []
    for i in range(nb):
        base = 20 + i * taille
        lignes.append(struct.unpack("<%dI" % champs,
                                    donnees[base:base + taille]))
    return lignes, champs, texte


def depuis_mpqs(chemins, nom_fichier):
    """Le DERNIER qui porte le fichier gagne (ordre des patchs)."""
    resultat = None
    for chemin in chemins:
        try:
            archive = MPQArchive(chemin, listfile=True)
            noms = [n.decode("latin-1") if isinstance(n, bytes) else n
                    for n in (archive.files or [])]
            for n in noms:
                if n.lower().endswith(nom_fichier.lower()):
                    d = archive.read_file(n)
                    if d and d[:4] == b"WDBC":
                        resultat = d
        except Exception:
            continue
    return resultat


def main():
    # --- 1. Commandes ---
    anglais_par_cle = {}
    chemins = (sorted(glob.glob(os.path.join(DATA, "enUS", "*.MPQ")))
               + sorted(glob.glob(os.path.join(DATA, "*.MPQ"))))
    for chemin in chemins:
        try:
            archive = MPQArchive(chemin, listfile=True)
            noms = [n.decode("latin-1") if isinstance(n, bytes) else n
                    for n in (archive.files or [])]
        except Exception:
            continue
        for n in noms:
            if not n.lower().endswith("globalstrings.dbc"):
                continue
            try:
                d = archive.read_file(n)
            except Exception:
                continue
            if not d or d[:4] != b"WDBC":
                continue
            lignes, champs, texte = wdbc(d)
            for vals in lignes:
                cle = texte(vals[2])
                if RE_CMD.match(cle):
                    anglais_par_cle[cle] = texte(vals[3])

    francais_par_cle = {}
    for ligne in io.open(DB_UI, encoding="utf-8"):
        m = re.match(r'^DB\["(EMOTE\d+_CMD\d+)"\]="((?:\\.|[^"\\])*)"',
                     ligne)
        if m:
            francais_par_cle[m.group(1)] = m.group(2)

    # JETONS d'émote (EmotesText.dbc : id -> nom du jeton, « HELLO »...).
    # Le numéro des clés EMOTE<n>_CMD est l'identifiant EmotesText. On les
    # embarque dans la base : l'addon ne dépend ainsi d'AUCUNE table
    # interne du client (hash_EmoteTokenList absente/remaniée chez
    # Ascension — vécu : /bonjour muet au premier essai).
    jetons_par_id = {}
    et_dbc = depuis_mpqs(chemins, "EmotesText.dbc")
    if et_dbc:
        lignes_et, _, texte_et = wdbc(et_dbc)
        for v in lignes_et:
            nom = texte_et(v[1])
            if nom and re.match(r"^[A-Z][A-Z0-9_]*$", nom):
                jetons_par_id[v[0]] = nom
    print("jetons d'émote :", len(jetons_par_id))

    jetons_valides = set(j for j in jetons_par_id.values() if j)

    # Le jeton d'un groupe EMOTE<n> : d'abord déduit du NOM anglais
    # lui-même (« /curtsey » -> CURTSEY, validé contre la liste
    # officielle) ; sinon repli sur le décalage constaté (jeton n-1 —
    # vérifié empiriquement : /curtsey=34, CURTSEY=33).
    en_par_numero = {}
    for cle, en in anglais_par_cle.items():
        n = int(re.match(r"^EMOTE(\d+)_", cle).group(1))
        if en.startswith("/"):
            en_par_numero.setdefault(n, []).append(en)

    jeton_par_numero = {}
    for n, ens in en_par_numero.items():
        for en in ens:
            candidat = en[1:].upper()
            if candidat in jetons_valides:
                jeton_par_numero[n] = candidat
                break
        if n not in jeton_par_numero:
            repli = jetons_par_id.get(n - 1, "")
            if repli:
                jeton_par_numero[n] = repli

    commandes = {}
    for cle, en in sorted(anglais_par_cle.items()):
        fr = francais_par_cle.get(cle, "")
        numero = int(re.match(r"^EMOTE(\d+)_", cle).group(1))
        jeton = jeton_par_numero.get(numero, "")
        # Le jeton peut rester VIDE : en jeu, le module lit la globale
        # EMOTE<n>_TOKEN du client (source exacte) — l'exiger ici excluait
        # justement les émotes vocales mal devinées (/fuyez muet, vécu).
        if en.startswith("/") and fr.startswith("/") \
                and fr.lower() != en.lower():
            commandes[cle] = {"en": en, "fr": fr, "jeton": jeton}
    print("commandes appariées :", len(commandes),
          "(EN vues : %d, FR connues : %d)"
          % (len(anglais_par_cle), len(francais_par_cle)))
    for temoin_cle in ("EMOTE34_CMD1", "EMOTE35_CMD1"):
        if temoin_cle in commandes:
            print("  témoin", temoin_cle, ":", commandes[temoin_cle])

    # --- 2. Phrases du tchat (EmotesTextData) ---
    en_dbc = depuis_mpqs(chemins, "EmotesTextData.dbc")
    fr_dbc = depuis_mpqs([FRFR], "EmotesTextData.dbc")
    tchat = {}
    if en_dbc and fr_dbc:
        lignes_en, champs_en, texte_en = wdbc(en_dbc)
        lignes_fr, champs_fr, texte_fr = wdbc(fr_dbc)
        fr_par_id = {v[0]: v for v in lignes_fr}
        # Colonne du texte : détection empirique — la première colonne qui
        # rend une chaîne plausible sur un échantillon.
        def colonne_texte(lignes, texte):
            votes = {}
            for v in lignes[:200]:
                for c in range(1, len(v)):
                    t = texte(v[c])
                    if len(t) > 3 and (" " in t or t.endswith(".")):
                        votes[c] = votes.get(c, 0) + 1
            return max(votes, key=votes.get) if votes else None

        c_en = colonne_texte(lignes_en, texte_en)
        c_fr = colonne_texte(lignes_fr, texte_fr)
        print("colonnes texte : enUS =", c_en, "| frFR =", c_fr)
        for v in lignes_en:
            f = fr_par_id.get(v[0])
            if not f:
                continue
            en = texte_en(v[c_en])
            fr = texte_fr(f[c_fr])
            if en and fr and en != fr:
                tchat[en] = fr
    else:
        print("! EmotesTextData introuvable (enUS : %s, frFR : %s)"
              % (bool(en_dbc), bool(fr_dbc)))
    print("phrases du tchat appariées :", len(tchat))

    with io.open(SORTIE, "w", encoding="utf-8") as f:
        json.dump({"commandes": commandes, "tchat": tchat}, f,
                  ensure_ascii=False, indent=1, sort_keys=True)
    print("écrit :", SORTIE)
    for cle in list(commandes)[:5]:
        print("  ex :", commandes[cle]["en"], "->", commandes[cle]["fr"])
    for en in list(tchat)[:4]:
        print("  ex :", en[:50], "->", tchat[en][:50])


if __name__ == "__main__":
    main()
