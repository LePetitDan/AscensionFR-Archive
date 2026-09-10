# -*- coding: utf-8 -*-
"""Garde-fou commun contre la pollution du PackFR (constat du 21/07/2026 :
le pack mélangeait les langues et les auteurs y avaient collé des réponses
de robot traducteur).

Trois familles de déchets, vues en vrai dans le pack :
  - « robot »   : « La traduction de "X" en français est "Y". », « veuillez
                  fournir plus de détails »... (collées telles quelles dans
                  leurs DBC) ;
  - « code »    : identifiants internes (5ppl_uldum_bg, EXIT_MINE,
                  SPELL_MANASTORM_CLASS_AURA_...) ;
  - « allemand »: colonnes deDE piochées par erreur (« Das Alte
                  Königreich », descriptions entières en allemand).

À utiliser par TOUT outil qui adopte du texte du pack :
    from garde_packfr import texte_sain
    if texte_sain(fr): ...
"""
import re

RE_ROBOT = re.compile(
    r"La traduction de|en français est|peut être traduit|veuillez fournir"
    r"|N'hésitez pas|plus de détails|dans les deux langues"
    r"|Voici la traduction")

RE_CODE = re.compile(r"^[a-z0-9]+_[a-z0-9_]+$|^[A-Z0-9]+_[A-Z0-9_]+$")

# Mots allemands sans homographe français : les « forts » suffisent seuls,
# les « faibles » doivent être deux différents (évite les faux positifs).
RE_ALLEMAND_FORT = re.compile(
    r"Schaden|Sekunden|erhöht|verursacht|Zauber|Fähigkeit|Gegner"
    r"|Wirkung|Verbündete|Rüstung|Beute|Königreich|Schlucht|Kaserne"
    r"|Angriffskraft|Ausdauer|Beweglichkeit|Willenskraft|aufspüren"
    r"|Verlängert|Unsichbarkeit|Unsichtbarkeit")
RE_ALLEMAND_FAIBLE = re.compile(
    r"\bder\b|\bdie\b|\bdas\b|\bund\b|\bfür\b|\bmit\b|\bvon\b|\beuch\b"
    r"|\bihr\b|\bwird\b|\bwerden\b|\bnicht\b|\beine\b|\beinen\b|\bdem\b"
    r"|\bden\b|\bsich\b")


def motif_rejet(texte):
    """Rend le motif de rejet, ou None si le texte est sain."""
    if not texte:
        return "vide"
    if RE_ROBOT.search(texte):
        return "robot"
    if RE_CODE.match(texte.strip()):
        return "code interne"
    if RE_ALLEMAND_FORT.search(texte):
        return "allemand"
    if len(set(RE_ALLEMAND_FAIBLE.findall(texte))) >= 2:
        return "allemand"
    return None


def texte_sain(texte):
    return motif_rejet(texte) is None
