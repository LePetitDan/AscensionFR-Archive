# -*- coding: utf-8 -*-
"""appliquer_vocabulaire.py — applique les arbitrages de 4-reference/GLOSSAIRE.md.

LA RÈGLE D'OR DU PROJET
-----------------------
On filtre sur la CLÉ ANGLAISE, jamais sur la valeur française seule, et
toujours en MOT ENTIER. Vécu : sur 165 « Libérez », 73 seulement traduisaient
« Unleash » — un remplacement global en aurait cassé 91. Et « Unleash » en
sous-chaîne attrape « Unleashing » : 143 faux positifs au lieu de 73.

Chaque substitution porte donc SA PROPRE garde anglaise, plus au besoin une
exclusion. Trois pièges relevés sur le terrain, tous encodés ici :

  - « Millhouse Manastorm » est un PERSONNAGE, pas le lieu. Il est exclu de la
    règle Manastorm, et son français est REMIS EN ANGLAIS ENTIER (arbitrage de
    Dan, 26/07/2026, comme Blizzard) : « Tempête de mana du moulin » lisait
    « mill house ». Sa règle vit APRÈS le bloc Manastorm — voir sur place.
  - « statique » est le plus souvent un vrai ADJECTIF français (« charge
    statique en arc », « équilibre statique ») : sur 146 emplois de « Static »
    côté anglais, la moitié seulement est la RESSOURCE de classe. On ne touche
    donc que les formes chiffrées (« 20 Static ») et « All Static ».
  - « Draft » est parfois un VERBE (« draft new starting spells »), traduit à
    tort par « rédiger ». Ce n'est pas le même traitement que le nom du mode.

OÙ ÇA S'ÉCRIT
-------------
`traductions/*.json`, toutes formes confondues (plat, sections, par
identifiant). L'anglais est retrouvé selon le fichier :
  - clé du dictionnaire pour les fichiers à clé anglaise ;
  - `a_traduire/interface_maison.json` pour interface_maison (clé = étiquette) ;
  - `sources/enUS/*` + `extraits/*/` par identifiant pour les fichiers par id.

`gisement_brut.json` (anglais -> français) est la SOURCE du gisement ;
`interface_maison.json` en dérive via `fusionner_gisement.py --ecrire`. On
corrige les deux, sinon la correction serait écrasée au prochain passage.

Usage :
    python outils/appliquer_vocabulaire.py              # simulation + rapport
    python outils/appliquer_vocabulaire.py --appliquer  # écrit (+ sauvegardes)
    python outils/appliquer_vocabulaire.py --terme Manastorm
"""
import argparse
import glob
import io
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRADUCTIONS = os.path.join(BASE, "traductions")
RAPPORT = os.path.join(BASE, "rapports", "vocabulaire_lot4.txt")

# Les sauvegardes ne sont ni lues ni écrites. Le dépôt les nomme toutes
# « <base>_avant_<raison>.json » : les relire ferait travailler l'outil sur des
# copies mortes, et les réécrire détruirait le filet de sécurité.
def est_sauvegarde(chemin):
    return "_avant_" in os.path.basename(chemin)

# Les codes du jeu se COLLENT au mot suivant : « |cFFB5FFFFStarcaller ». Entre
# le « F » du code et le « S » du mot, « \b » ne voit aucune frontière — 38
# occurrences de Starcaller et 53 de Manastorm avaient ainsi échappé au premier
# passage. On accepte donc comme début de mot soit une vraie frontière, soit la
# fin d'un code d'affichage.
#
# Les fins de code comptent AUSSI (26/07/2026, lot 7) : une icône de haut fait
# donne « …|t|rBassin d'Arathi », et le « r » de « |r » comme le « t » de
# « |t » sont des LETTRES. La garde d'origine ne voyait que « |c » et ratait
# ces cas-là EN SILENCE — 3 occurrences sur 30 dans DB_Communaute.lua.
# (Trois lookbehind séparés : chacun est de largeur fixe, ce qu'exige Python.)
DEBUT = r"(?:(?<=\|[rt])|(?<=\|c[0-9A-Fa-f]{8})|(?<![0-9A-Za-zÀ-ÿ]))"
FIN = r"(?![0-9A-Za-zÀ-ÿ])"

CODES = re.compile(r"\|c[0-9A-Fa-f]{8}|\|r|\|T[^|]*\|t|\|H[^|]*\|h")


def denuder(texte):
    """Ôte les codes d'affichage : la garde anglaise doit voir les mots."""
    return CODES.sub(" ", texte or "")


# ---------------------------------------------------------------------------
# LES SUBSTITUTIONS
# (terme, garde anglaise ou None, exclusion, motif FR, remplacement)
#
# garde = None : la valeur FRANÇAISE porte encore le nom propre ANGLAIS non
# traduit (« Warsong Gulch » dans un titre de quête). Le français est alors sa
# propre preuve, et beaucoup de ces entrées sont dans des fichiers indexés par
# identifiant dont on n'a plus l'anglais. L'exclusion, elle, reste en vigueur.
#
# Elles s'appliquent DANS L'ORDRE sur une même valeur : le plus précis d'abord,
# sinon « de Warsong Gulch » deviendrait « de Goulet des Warsong ».
# ---------------------------------------------------------------------------
SUBSTITUTIONS = [
    # --- PvP / PvE : on n'écrit pas JcJ/JcE -------------------------------
    ("PvP / PvE", r"\bPvP\b", None, DEBUT + r"JcJ" + FIN, "PvP"),
    ("PvP / PvE", r"\bPvE\b", None, DEBUT + r"JcE" + FIN, "PvE"),

    # --- « Abyssal Draft » N'EST PAS la mécanique -------------------------
    # C'est un réactif d'artisanat, et « draft » y veut dire COURANT D'AIR.
    # La famille le prouve : Droplet -> Eau, Spark -> Feu, Fragment -> Terre,
    # Draft -> Air. « Draft abyssal » (l'état livré, antérieur à ce lot) ne
    # veut rien dire. Cette ligne passe AVANT les règles Draft, et toutes
    # les suivantes l'excluent.
    ("Abyssal Draft", r"\bAbyssal\s+Draft\b", None,
     DEBUT + r"Draft\s+abyssal" + FIN, "Souffle abyssal"),

    # --- Draft : nom de la mécanique, on garde l'anglais ------------------
    # « build » a parfois été traduit par « construction », « version »,
    # « projet », « ébauche » ou « repêchage » : c'est la même mécanique.
    ("Draft", r"\bBuild\s+Draft\b", r"Abyssal Draft",
     r"\b[Bb]rouillons?\s+de\s+(?:build|construction)\b", "Draft de build"),
    ("Draft", r"\bBuild\s+Drafts\b", r"Abyssal Draft",
     r"\b[ée]bauches\s+de\s+construction\b", "Build Drafts"),
    # « \s* » aurait mangé l'espace avant le mot suivant (« Build Draftou ») :
    # le complément est optionnel AVEC son espace, pas l'inverse.
    ("Draft", r"\bBuild\s+Draft\b", r"Abyssal Draft",
     r"\b(?:[ée]bauche|version\s+préliminaire|projet)"
     r"(?:\s+de\s+construction)?\b", "Build Draft"),
    ("Draft", r"\bDraft\s+Mode\b", r"Abyssal Draft",
     r"\bmode\s+brouillons?\b", "mode Draft"),
    ("Draft", r"\bdraft\s+cards?\b", r"Abyssal Draft",
     r"\b[Bb]rouillons?\s+de\s+cartes?\b", "cartes de Draft"),
    ("Draft", r"\bdraft\s+options?\b", r"Abyssal Draft",
     r"\boptions?\s+de\s+repêchage\b", "options de Draft"),
    ("Draft", r"\bdrafts?\b", r"Abyssal Draft", r"\b[Bb]rouillons?\b",
     "Draft"),

    # --- Draft VERBE : Dan tranche « composer » (26/07/2026) --------------
    # Le NOM du mode reste « Draft » ; seul le VERBE se traduit. Impératif
    # pluriel « Composez », infinitif « composer », participe « composés /
    # composées », préfixe re- « recomposer / Recomposez ».
    #
    # Ces règles rattrapent DEUX états à la fois, et c'est voulu :
    #   - le « drafter » que le lot 4 avait posé (mot que j'avais choisi, et
    #     que Dan a corrigé) ;
    #   - les 19 entrées que le lot 4 n'a JAMAIS touchées, parce que ses
    #     gardes anglaises étaient en minuscules (`\bdrafted\b`) alors que la
    #     clé du jeu écrit « Drafted Book of Ascension », « Redraft All »,
    #     « Redraft Current ». Aucune ne matchait. Les gardes sont donc
    #     insensibles à la casse ici.
    #
    # Certaines règles n'ont AUCUNE garde anglaise : les fichiers par
    # identifiant (objets.json, creatures.json, quetes.json) n'ont pas
    # d'anglais du tout, et le motif français y est à lui seul une preuve
    # suffisante — vérifié entrée par entrée.
    #
    # L'ORDRE compte : les phrases entières passent AVANT le générique
    # « [Rr]eformuler », sinon celui-ci masquerait les cas particuliers.
    ("Draft (verbe)", None, r"Abyssal Draft",
     DEBUT + r"Rédaction\s+du\s+Livre\s+de\s+l'Ascension" + FIN,
     "Livre de l'Ascension composé"),
    ("Draft (verbe)", None, r"Abyssal Draft",
     DEBUT + r"Livre\s+de\s+l'Ascension\s+drafté" + FIN,
     "Livre de l'Ascension composé"),
    ("Draft (verbe)", r"(?i)\bredraft\w*\b", r"Abyssal Draft",
     DEBUT + r"Réécriture\s+actuelle" + FIN, "Recomposer l'actuel"),
    ("Draft (verbe)", r"(?i)\bredraft\w*\b", r"Abyssal Draft",
     DEBUT + r"Redrafter\s+l'actuel" + FIN, "Recomposer l'actuel"),
    ("Draft (verbe)", r"(?i)\bredraft\w*\b", r"Abyssal Draft",
     DEBUT + r"Tout\s+reformuler" + FIN, "Tout recomposer"),
    ("Draft (verbe)", r"(?i)\bredraft\w*\b", r"Abyssal Draft",
     DEBUT + r"Reformulez\s+votre\s+Draft\s+actuel" + FIN,
     "Recomposez votre Draft actuel"),
    ("Draft (verbe)", None, r"Abyssal Draft",
     DEBUT + r"Reformulez\s+votre\s+brouillon\s+actuel" + FIN,
     "Recomposez votre Draft actuel"),
    ("Draft (verbe)", None, r"Abyssal Draft",
     DEBUT + r"rédiger\s+de\s+nouveaux\s+sorts\s+de\s+démarrage" + FIN,
     "composer de nouveaux sorts de départ"),
    ("Draft (verbe)", None, r"Abyssal Draft",
     DEBUT + r"sera\s+reformulé" + FIN, "sera recomposé"),
    ("Draft (verbe)", None, r"Abyssal Draft",
     DEBUT + r"reformulera\s+tous\s+les\s+sorts" + FIN,
     "recomposera tous les sorts"),
    ("Draft (verbe)", r"(?i)\bredraft\w*\b", r"Abyssal Draft",
     DEBUT + r"remanier\s+des\s+sorts" + FIN, "recomposer des sorts"),
    ("Draft (verbe)", r"(?i)\bredraft\w*\b", r"Abyssal Draft",
     DEBUT + r"[Rr]edraftez" + FIN, "Recomposez"),
    ("Draft (verbe)", r"(?i)\bredraft\w*\b", r"Abyssal Draft",
     DEBUT + r"[Rr]edrafter" + FIN, "recomposer"),
    ("Draft (verbe)", None, r"Abyssal Draft",
     DEBUT + r"[Rr]eformuler" + FIN, "recomposer"),
    ("Draft (verbe)", r"(?i)\bdraft\w*\b", r"Abyssal Draft",
     DEBUT + r"Rédiger\s+une\s+version" + FIN, "Composer une version"),
    ("Draft (verbe)", r"(?i)\bdraft\w*\b", r"Abyssal Draft",
     DEBUT + r"[Dd]raftez" + FIN, "Composez"),
    ("Draft (verbe)", r"(?i)\bdraft\w*\b", r"Abyssal Draft",
     DEBUT + r"[Dd]rafter" + FIN, "composer"),
    ("Draft (verbe)", r"(?i)\bdrafted\b", r"Abyssal Draft",
     DEBUT + r"[Dd]raftés" + FIN, "composés"),
    ("Draft (verbe)", r"(?i)\bdrafted\b", r"Abyssal Draft",
     DEBUT + r"[Dd]raftées" + FIN, "composées"),

    # FILET pour les chaînes NEUVES — à garder même quand il ne se déclenche
    # pas. `traduire_gisement.py` n'écrase JAMAIS un français existant : il
    # AJOUTE les chaînes neuves de chaque patch Ascension, traduites par
    # Google. Or c'est Google qui rend « draft » par « rédiger / Rédigez /
    # rédigés / redessiner ». Sans ces règles, cet outil cesserait d'être un
    # normalisateur rejouable pour devenir une migration à usage unique, et
    # le contresens que Dan vient d'arbitrer reviendrait au prochain patch.
    # Mesuré le 26/07 : 0 déclenchement sur l'état actuel, 6 sur l'état
    # d'origine. Gardes laissées en minuscules — les rendre insensibles à la
    # casse ne change rien au résultat, autant ne pas prendre le risque.
    ("Draft (verbe)", r"\bredraft\w*\b", r"Abyssal Draft",
     DEBUT + r"[Rr]edessiner" + FIN, "recomposer"),
    ("Draft (verbe)", r"\bdrafts?\b|\bdrafted\b", r"Abyssal Draft",
     DEBUT + r"Rédigez" + FIN, "Composez"),
    ("Draft (verbe)", r"\bdrafts?\b|\bdrafted\b", r"Abyssal Draft",
     DEBUT + r"rédiger" + FIN, "composer"),
    ("Draft (verbe)", r"\bdrafted\b", r"Abyssal Draft",
     DEBUT + r"rédigés" + FIN, "composés"),
    ("Draft (verbe)", r"\bdrafted\b", r"Abyssal Draft",
     DEBUT + r"capacités\s+de\s+sélection" + FIN, "capacités composées"),

    # --- Phrases RECOLLÉES de travers ------------------------------------
    # Une coquille de la source (« Manastorm.Shares », sans espace) a fusionné
    # deux phrases, et le traducteur a recollé de travers en laissant un bout
    # d'anglais. Le libellé de remplacement n'est pas inventé : c'est celui
    # des 250 entrées sœurs dont la source, elle, est correcte.
    ("Recollage", r"Manastorm\.Shares", None,
     r"dans le temps de recharge de la Tempête de mana\.Shares avec des "
     r"effets similaires\.",
     "dans la Tempête de mana. Partage le temps de recharge avec des "
     "effets similaires."),
    # « Casting » n'est le VERBE que s'il ouvre une phrase suivie d'un verbe
    # d'effet. Six libellés d'INTERFACE (« Mouseover Casting », « Casting
    # Damage Dealer ») l'emploient comme NOM — ils veulent « incantation »,
    # pas « lancer », et relèvent du vocabulaire d'interface, pas de ce lot.
    ("Recollage",
     r"(?:^|\n)Casting\s+.{0,60}?\b(?:grants?|triggers?|now|will|enters?|"
     r"causes?|reduces?|increases?|applies|resets?)\b", None,
     DEBUT + r"Casting" + FIN, "Lancer"),

    # --- « Casting » NOM : dix libellés d'interface -> « Incantation » -----
    # Arbitrage de Dan (26/07/2026) : « Mouseover Casting » -> « Incantation
    # au survol ». Le lot 4 les avait EXCLUS plutôt que de trancher un
    # vocabulaire d'interface à sa place. Le VERBE, lui, reste « Lancer » :
    # chaque règle porte ici la garde du LIBELLÉ EXACT, jamais le simple mot
    # « Casting », donc aucune description de sort ne peut être atteinte.
    #
    # Dix et non six. Chercher « Casting » côté FRANÇAIS n'en trouve que six —
    # c'est l'anti-patron que la règle d'or du projet interdit. Quatre autres
    # membres de la même famille ont été traduits par « diffusion »
    # (« broadcast ») ou par un charabia, et le filtre français est aveugle à
    # eux. Sans ces quatre, le panneau d'options serait à moitié traduit : le
    # titre dirait « Incantation au survol de la souris » pendant que son
    # info-bulle, juste en dessous, dirait encore « diffusion par survol ».
    ("Casting (nom)", r"\bMouseover\s+Casting\s+Hotkey\b", None,
     DEBUT + r"Touche\s+de\s+raccourci\s+de\s+diffusion\s+au\s+survol"
     r"\s+de\s+la\s+souris" + FIN,
     "Raccourci d'incantation au survol de la souris"),
    ("Casting (nom)", r"\bFriendly\s+Mouseover\s+Casting\b", None,
     DEBUT + r"Casting\s+convivial\s+par\s+survol\s+de\s+la\s+souris" + FIN,
     "Incantation au survol d'un allié"),
    ("Casting (nom)", r"\bEnemy\s+Mouseover\s+Casting\b", None,
     DEBUT + r"Casting\s+de\s+l'ennemi\s+avec\s+la\s+souris" + FIN,
     "Incantation au survol d'un ennemi"),
    ("Casting (nom)", r"\bMouseover\s+Casting\b", None,
     DEBUT + r"Casting\s+par\s+survol\s+de\s+la\s+souris" + FIN,
     "Incantation au survol de la souris"),
    ("Casting (nom)", r"\bPress\s+and\s+Hold\s+Casting\b", None,
     DEBUT + r"Appuyez\s+et\s+maintenez\s+Casting" + FIN,
     "Incantation par appui maintenu"),
    ("Casting (nom)", r"\bAuto\s+Assist\s+Cast\b", None,
     DEBUT + r"Casting\s+avec\s+assistance\s+automatique" + FIN,
     "Incantation avec assistance automatique"),
    # « Incantation Attaquant » n'est pas du français : on aligne sur le
    # libellé court frère CASTER_DAMAGER_SHORT, déjà traduit « Incantateur »
    # dans le même fichier.
    ("Casting (nom)", r"\bCasting\s+Damage\s+Dealer\b", None,
     DEBUT + r"Casting\s+Attaquant" + FIN, "Attaquant incantateur"),
    ("Casting (nom)",
     r"\bEnables\s+mouseover\s+casting\s+for\s+friendly\s+targets\b", None,
     DEBUT + r"Permet\s+la\s+diffusion\s+par\s+survol\s+de\s+la\s+souris"
     r"\s+pour\s+les\s+cibles\s+amies" + FIN,
     "Active l'incantation au survol pour les cibles alliées"),
    ("Casting (nom)",
     r"\bEnables\s+mouseover\s+casting\s+for\s+neutral\s+and\s+enemy"
     r"\s+targets\b", None,
     DEBUT + r"Permet\s+de\s+lancer\s+le\s+passage\s+de\s+la\s+souris"
     r"\s+pour\s+les\s+cibles\s+neutres\s+et\s+ennemies" + FIN,
     "Active l'incantation au survol pour les cibles neutres et ennemies"),
    ("Casting (nom)",
     r"\bModifier\s+key\s+to\s+use\s+for\s+mouseover\s+casting\b", None,
     DEBUT + r"Touche\s+de\s+modification\s+à\s+utiliser\s+pour\s+la"
     r"\s+diffusion\s+par\s+survol\s+de\s+la\s+souris" + FIN,
     "Touche de modification pour l'incantation au survol de la souris"),

    ("Recollage", r"\bRestores\b", None, r"^Restores\b", "Rend"),
    ("Recollage", r"\bhealth over\b", None,
     r"\bpoints de vie over\b", "points de vie en"),
    ("Recollage", r"\bmana or\b", None, r"\bmana or\b", "mana ou"),
    ("Recollage", r"\bRequires\s+Follow\s+Up\b", None,
     r"\bRequires\s+Follow\s+Up\b", "Nécessite un suivi"),

    # --- Manastorm -> Tempête de mana ------------------------------------
    # EXCLUSION ABSOLUE : « Millhouse Manastorm » est un PERSONNAGE (le gnome
    # de l'Arcatraz), pas le donjon. L'exclusion porte sur l'anglais ET sur le
    # français, car certaines entrées n'ont plus leur anglais.
    # « tempête » est FÉMININ : « le Manastorm » donne « LA Tempête de mana ».
    # Sans les lignes d'accord, la règle générique laissait « Le Tempête ».
    ("Manastorm", None, r"Millhouse",
     DEBUT + r"[Ll]es\s+Manastorms" + FIN, "les Tempêtes de mana"),
    ("Manastorm", None, r"Millhouse",
     DEBUT + r"Le\s+(?:The\s+)?Manastorm" + FIN, "La Tempête de mana"),
    ("Manastorm", None, r"Millhouse",
     DEBUT + r"Un\s+autre\s+Manastorm" + FIN, "Une autre Tempête de mana"),
    ("Manastorm", None, r"Millhouse",
     DEBUT + r"un\s+autre\s+Manastorm" + FIN, "une autre Tempête de mana"),
    ("Manastorm", None, r"Millhouse",
     DEBUT + r"dans\s+le\s+[Mm]anastorm" + FIN, "dans la Tempête de mana"),
    ("Manastorm", None, r"Millhouse",
     DEBUT + r"a[uü]\s+[Mm]anastorm" + FIN, "à la Tempête de mana"),
    ("Manastorm", None, r"Millhouse",
     DEBUT + r"(?:de|du)\s+(?:The\s+)?[Mm]anastorm" + FIN,
     "de la Tempête de mana"),
    ("Manastorm", None, r"Millhouse",
     DEBUT + r"à\s+The\s+Manastorm" + FIN, "à la Tempête de mana"),
    ("Manastorm", None, r"Millhouse",
     DEBUT + r"(?:le|The)\s+Manastorm" + FIN, "la Tempête de mana"),
    # Apposition à l'anglaise (« Manastorm Cache ») : le français veut un
    # complément, « Cache de la Tempête de mana », pas « Cache Tempête ».
    ("Manastorm", None, r"Millhouse",
     r"(Cache|Flacon|Utilitaire|sanctuaire|manipulateur|niveaux?|sorts|"
     r"gadgets|sécurité|groupe|parchemins|Flèche d'objectif|Bonus)"
     r"\s+Manastorm" + FIN, r"\1 de la Tempête de mana"),
    ("Manastorm", None, r"Millhouse",
     DEBUT + r"[Mm]anastorms" + FIN, "Tempêtes de mana"),
    ("Manastorm", None, r"Millhouse",
     DEBUT + r"[Mm]anastorm" + FIN, "Tempête de mana"),

    # --- Millhouse Manastorm : on garde le nom anglais ENTIER -------------
    # Arbitrage de Dan (26/07/2026), comme Blizzard. « Tempête de mana du
    # moulin » lisait « mill house », la maison du moulin : contresens sur un
    # nom propre. 4 entrées, toutes prouvées Millhouse — deux par leur clé
    # anglaise, deux par le cache serveur (créatures 179536 et 179538). Les
    # 52 autres entrées contenant « moulin » sont de vrais moulins
    # (Moulin-de-Tarren, Ambermill, moulin d'Alther) : aucune ne porte cette
    # chaîne complète.
    #
    # CETTE RÈGLE DOIT RESTER APRÈS LE BLOC MANASTORM. corriger() calcule son
    # exclusion sur le français D'ORIGINE, une seule fois : posée avant, le
    # « Manastorm » qu'elle vient d'écrire serait retraduit par les règles
    # ci-dessus et donnerait « Millhouse Tempête de mana » (vérifié sur la
    # créature 179536).
    ("Millhouse", None, None,
     DEBUT + r"Tempête\s+de\s+mana\s+du\s+moulin" + FIN,
     "Millhouse Manastorm"),

    # --- Starcaller -> Mande-étoiles (titre officiel Blizzard) ------------
    # Sans garde anglaise : « Héraut stellaire » et « Starcaller » ne
    # désignent rien d'autre dans ce jeu, et beaucoup d'occurrences vivent
    # dans des fichiers dont on n'a plus l'anglais.
    ("Starcaller", None, None,
     DEBUT + r"H[ée]rauts?\s+stellaires?" + FIN, "Mande-étoiles"),
    ("Starcaller", None, None, DEBUT + r"Starcallers?" + FIN,
     "Mande-étoiles"),

    # --- Light Lash -> Fouet de Lumière (contresens « cil » / « fouet ») --
    ("Light Lash", r"\bLight\s+Lash\b", None,
     r"\bCils?\s+(?:l[ée]gers?|clairs?)\b", "Fouet de Lumière"),

    # --- Static : la RESSOURCE seulement, jamais l'adjectif ---------------
    ("Static", r"\d+\s+Static\b", None, r"(\d+)\s+statiques?\b",
     r"\1 Statique"),
    ("Static", r"\bAll\s+Static\b", None,
     r"\btoute\s+l'électricité\s+statique\b", "toute la Statique"),
    ("Static", r"\bStatic\b\s+as\s+resources?\b", None, r"\bStatic\b",
     "Statique"),

    # --- Noms officiels Blizzard des champs de bataille -------------------
    # Sans garde anglaise : « bassin d'Arathi » et « Warsong Gulch » ne
    # désignent qu'une chose. Beaucoup sont des titres de quêtes custom
    # (fichiers par identifiant) dont l'anglais n'est plus disponible.
    # La CASSE est conservée. Le premier jet forçait la majuscule partout,
    # ce qui écrivait « dans le Bassin Arathi » au milieu d'une phrase alors
    # que le même addon livre déjà 185 « bassin Arathi » en minuscule (contre
    # 41 en majuscule), et que la locale serveur officielle en écrit 232
    # contre 42. Ce qu'on supprime, c'est l'apostrophe — le nom, lui, est le
    # même dans les deux casses.
    ("Arathi Basin", None, None,
     DEBUT + r"Bassin\s+d'Arathi" + FIN, "Bassin Arathi"),
    ("Arathi Basin", None, None,
     DEBUT + r"bassin\s+d'Arathi" + FIN, "bassin Arathi"),
    ("Arathi Basin", None, None, DEBUT + r"Arathi\s+Basin" + FIN,
     "Bassin Arathi"),
    ("Warsong Gulch", None, None,
     DEBUT + r"de\s+Warsong\s+Gulch" + FIN, "du Goulet des Warsong"),
    ("Warsong Gulch", None, None,
     DEBUT + r"à\s+Warsong\s+Gulch" + FIN, "au Goulet des Warsong"),
    ("Warsong Gulch", None, None, DEBUT + r"Warsong\s+Gulch" + FIN,
     "Goulet des Warsong"),
]

COMPILEES = [(terme, re.compile(en) if en else None,
              re.compile(sauf) if sauf else None, re.compile(fr), vers)
             for terme, en, sauf, fr, vers in SUBSTITUTIONS]


# ---------------------------------------------------------------------------
# Retrouver l'ANGLAIS, selon la forme du fichier
# ---------------------------------------------------------------------------
def charger(chemin):
    try:
        with io.open(chemin, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def anglais_par_identifiant():
    """{identifiant: tout l'anglais connu pour cet objet/PNJ/quête}.

    Les fichiers « par id » ne portent aucun anglais : il faut le rapatrier
    des sources officielles et des caches du client. On concatène tous les
    champs — pour un test de MOT ENTIER sur un nom propre, ça suffit, et ça
    évite d'inventer une correspondance champ à champ fragile.
    """
    blob = {}

    def verser(dico):
        for ident, valeur in dico.items():
            if isinstance(valeur, dict):
                textes = [v for v in valeur.values() if isinstance(v, str)]
            elif isinstance(valeur, str):
                textes = [valeur]
            else:
                continue
            blob[str(ident)] = blob.get(str(ident), "") + " " + " ".join(textes)

    for nom in ("item_template.json", "creature_template.json",
                "gameobject_template.json", "quest_template.json"):
        verser(charger(os.path.join(BASE, "sources", "enUS", nom)))
    for royaume in sorted(glob.glob(os.path.join(BASE, "extraits", "*"))):
        if not os.path.isdir(royaume):
            continue
        for nom in ("objets.json", "creatures.json", "objets_monde.json",
                    "quetes.json"):
            verser(charger(os.path.join(royaume, nom)))
    return blob


def entrees(chemin, etiquettes, par_id):
    """Rend (route, anglais, français) — la route sert à réécrire en place."""
    nom = os.path.basename(chemin)
    data = charger(chemin)
    if not isinstance(data, dict):
        return
    for cle, valeur in data.items():
        if isinstance(valeur, str):
            en = etiquettes.get(cle) if nom == "interface_maison.json" else cle
            yield (cle,), en, valeur
        elif isinstance(valeur, dict):
            for k2, v2 in valeur.items():
                if not isinstance(v2, str):
                    continue
                en = par_id.get(cle) if cle.isdigit() else k2
                yield (cle, k2), en, v2


def corriger(anglais, francais, terme_voulu=None):
    """-> (français corrigé, [étiquettes des règles appliquées]).

    La garde anglaise lit un anglais DÉNUDÉ de ses codes d'affichage, sinon
    « |cFFB5FFFFStarcaller » ne contient aucun « Starcaller » délimité.
    L'exclusion, elle, porte sur les deux langues : « Millhouse » doit
    protéger le personnage même quand l'anglais a été perdu.
    """
    if not francais:
        return francais, []
    nu_en = denuder(anglais) if anglais else ""
    nu_fr = denuder(francais)
    sortie, appliquees = francais, []
    for terme, re_en, re_sauf, re_fr, vers in COMPILEES:
        if terme_voulu and terme != terme_voulu:
            continue
        if re_en is not None and not re_en.search(nu_en):
            continue
        if re_sauf and (re_sauf.search(nu_en) or re_sauf.search(nu_fr)):
            continue
        neuf, n = re_fr.subn(vers, sortie)
        if n:
            sortie = neuf
            appliquees.append(terme)
    return sortie, appliquees


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--appliquer", action="store_true")
    parser.add_argument("--terme", default=None)
    args = parser.parse_args()

    etiquettes = charger(os.path.join(BASE, "a_traduire",
                                      "interface_maison.json"))
    print("Anglais du gisement    : %d étiquettes" % len(etiquettes))
    par_id = anglais_par_identifiant()
    print("Anglais par identifiant: %d entrées" % len(par_id))
    print()

    fichiers = [c for c in sorted(glob.glob(os.path.join(TRADUCTIONS,
                                                         "*.json")))
                if not est_sauvegarde(c)]

    total = Counter()
    par_fichier = Counter()
    lignes_rapport = []
    a_ecrire = {}

    for chemin in fichiers:
        nom = os.path.basename(chemin)
        data = charger(chemin)
        modifs = []
        for route, en, fr in entrees(chemin, etiquettes, par_id):
            neuf, regles = corriger(en, fr, args.terme)
            if neuf == fr:
                continue
            modifs.append((route, fr, neuf, regles))
            for r in regles:
                total[r] += 1
            par_fichier[nom] += 1
        if not modifs:
            continue
        for route, avant, apres, regles in modifs:
            table = data
            for etape in route[:-1]:
                table = table[etape]
            table[route[-1]] = apres
            lignes_rapport.append(
                "[%s] %s\n  - %s\n  + %s"
                % (", ".join(sorted(set(regles))), nom,
                   avant.replace("\n", "\\n")[:200],
                   apres.replace("\n", "\\n")[:200]))
        a_ecrire[chemin] = data

    print("%-18s %8s" % ("terme", "entrées"))
    print("-" * 30)
    for terme, n in sorted(total.items(), key=lambda x: -x[1]):
        print("%-18s %8d" % (terme, n))
    print("-" * 30)
    print("%-18s %8d" % ("TOTAL", sum(par_fichier.values())))
    print()
    for nom, n in par_fichier.most_common():
        print("   %-34s %6d" % (nom, n))

    os.makedirs(os.path.dirname(RAPPORT), exist_ok=True)
    with io.open(RAPPORT, "w", encoding="utf-8") as f:
        f.write("Lot 4 — vocabulaire. %d entrée(s) touchée(s).\n\n"
                % sum(par_fichier.values()))
        f.write("\n\n".join(lignes_rapport))
    print()
    print("Détail complet : %s" % RAPPORT)

    # Les comptes du passage (programme 31, bloc F) — « tentées » =
    # corrections calculées, « traduites » = appliquées.
    _total_corrections = sum(par_fichier.values())
    print("@@BILAN " + json.dumps(
        {"tentees": _total_corrections,
         "traduites": _total_corrections if args.appliquer else 0,
         "refusees": 0,
         "ecartees": 0 if args.appliquer else _total_corrections}))

    if not args.appliquer:
        print("SIMULATION — rien n'a été écrit. --appliquer pour livrer.")
        return 0

    for chemin, data in a_ecrire.items():
        secours = chemin.replace(".json", "_avant_vocabulaire.json")
        if not os.path.exists(secours):
            shutil.copy2(chemin, secours)
        # Écriture ATOMIQUE : cette étape de l'Atelier réécrit les stores
        # eux-mêmes (dont sorts.json) — une coupure ici coûterait autant
        # qu'au moteur de traduction.
        from ecriture_sure import ecrire_json
        ecrire_json(chemin, data)
        print("  écrit : %s" % os.path.basename(chemin))
    print()
    # LA CHAÎNE NE DEMANDE PLUS À PERSONNE DE SE SOUVENIR (29/07/2026).
    # Ici vivait « Pense à rejouer fusionner_gisement.py --ecrire… » : un
    # conseil affiché à CHAQUE passage n'est plus lu au troisième, et un
    # outil qui compte sur la mémoire d'un humain est un oubli qui attend
    # son tour. Deux cas, et un seul déclenche quoi que ce soit :
    #   - le gisement (gisement_brut.json) fait partie de ce qu'on vient
    #     de réécrire -> on enchaîne la fusion NOUS-MÊMES ;
    #   - il n'en fait pas partie -> il n'y a rien à refaire, et on se tait.
    # fusionner_gisement porte ses trois contrôles (format, anglais
    # résiduel, non traduites) et refuse ce qui est douteux : l'enchaîner
    # ne peut pas livrer un texte que la main n'aurait pas livré.
    gisement_touche = any(
        os.path.basename(c) in ("gisement_brut.json",
                                "interface_maison.json")
        for c in a_ecrire)
    if not gisement_touche:
        print("Le gisement d'interface n'a pas bougé : rien d'autre à "
              "refaire.")
        return 0
    print("Le gisement d'interface a changé — je refais la fusion :")
    code = subprocess.call(
        [sys.executable,
         os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "fusionner_gisement.py"), "--ecrire"])
    if code != 0:
        print("! la fusion du gisement a échoué (code %d) — les bases NE "
              "sont PAS à jour." % code)
        return code
    print("Fusion faite. Les bases seront régénérées par l'étape suivante "
          "de l'Atelier.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
