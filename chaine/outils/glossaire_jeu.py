# -*- coding: utf-8 -*-
r"""LE GLOSSAIRE DU JEU — module a part depuis le bloc D3 (29/07/2026).

Google ignore le vocabulaire de WoW (« Rage » -> « colère », « Focus » ->
« se concentrer ») : les termes du jeu sortent du texte AVANT traduction
(jetons §n§, distincts des [n] des codes techniques) et rentrent en
français arbitré après. Vivait dans traduire_gisement.py ; extrait ici
pour que traducteur_fr (le moteur PRINCIPAL) puisse l'importer sans
cycle — traduire_gisement importe traducteur_fr.

Ajouter un terme : une paire (anglais, français) dans GLOSSAIRE, les
expressions longues avant les courtes protégées par le tri sur la
longueur ci-dessous.
"""
import re

# Termes de jeu que Google massacre. Protégés avant traduction, restitués en
# français après — même procédé que les codes « $s1 ». Ordre important : les
# expressions longues d'abord, sinon « Spell Power » se ferait manger par
# « Power ».
GLOSSAIRE = [
    ("Runic Power", "Puissance runique"), ("Spell Power", "puissance des sorts"),
    ("Attack Power", "puissance d'attaque"), ("Critical Strike", "Critique"),
    ("Ability Essence", "Essence d'aptitude"), ("Skill Card", "carte de compétence"),
    ("Mystic Enchant", "Enchantement mystique"), ("Wildcard", "Joker"),
    # Nom propre de la fête foraine (royaume Darkmoon, 24/07/2026). Sans lui,
    # Google rendait « Azzar Faire » de six façons (« foire Azzar », « Faire
    # Azzar » inversé, ou laissé en anglais). Les deux ordres sont protégés
    # pour attraper aussi la forme inversée que Google produisait.
    ("Azzar Faire", "Foire d'Azzar"), ("Faire Azzar", "Foire d'Azzar"),
    ("Damage Dealer", "Attaquant"), ("Plate", "Plaques"), ("Mail", "Mailles"),
    ("Rage", "Rage"), ("Mana", "Mana"), ("Focus", "Focalisation"),
    ("Energy", "Énergie"), ("Stamina", "Endurance"), ("Spirit", "Esprit"),
    ("Strength", "Force"), ("Agility", "Agilité"), ("Intellect", "Intelligence"),
    ("Resilience", "Résilience"), ("Haste", "Hâte"), ("Armor", "Armure"),
    ("Holy", "Sacré"), ("Shadow", "Ombre"), ("Frost", "Givre"),
    ("Arcane", "Arcanes"), ("Fel", "Gangre"), ("Tank", "Tank"),
    ("Healer", "Soigneur"),
    # NE PAS protéger les noms propres qui s'écrivent pareil en français
    # (Ascension, Azeroth, Elune, Manastorm) : Google les laisse déjà
    # tranquilles, et les mettre sous jeton l'empêche d'élider —
    # « le royaume principal DU Ascension » au lieu de « d'Ascension ».
    # On ne protège que ce que Google abîmerait.
    ("Templar", "Templier"), ("Reaper", "Faucheur"), ("Primalist", "Primaliste"),
    ("Wildwalker", "Primaliste"), ("Starcaller", "Mande-étoiles"),
    ("Sun Cleric", "Clerc du soleil"), ("Tinker", "Bricoleur"),
    ("Runemaster", "Maître des runes"), ("Felsworn", "Gangrelige"),
    ("Bloodmage", "Mage de sang"), ("Knight of Xoroth", "Chevalier de Xoroth"),
    ("Witch Doctor", "Féticheur"), ("Witch Hunter", "Chasseur de sorcières"),
    ("Stormbringer", "Porte-tempête"), ("Venomancer", "Vénomancien"),
    ("Chronomancer", "Chronomancien"), ("Necromancer", "Nécromancien"),
    ("Pyromancer", "Pyromancien"), ("Barbarian", "Barbare"),
    # Pièges attrapés par la revue du lot de talents (21/07/2026). Le motif
    # de protection est SENSIBLE à la casse : les entrées en minuscules
    # ci-dessous couvrent les occurrences que « Mail »/« Haste » rataient
    # (Google traduisait « mail » en « courrier », « haste » en « rapidité »).
    ("mail", "mailles"), ("plate", "plaques"), ("haste", "hâte"),
    ("spell pushback", "retard d'incantation"),
    ("pushback", "retard d'incantation"),
    ("near you", "près de vous"), ("feared", "apeuré"),
    ("a stack of", "une charge de"), ("stacks of", "charges de"),
    ("stacking up to", "se cumule jusqu'à"),
    ("Felfury", "Gangrefurie"), ("Demonfire", "Feu démoniaque"),
    ("Hellfire Imps", "lutins gouffre-feu"),
    ("Hellfire Imp", "lutin gouffre-feu"),
    ("Hellfire Form", "Forme gouffre-feu"),
]
# Les jetons de glossaire sont numérotés à part des codes (§1§, §2§...) pour
# ne pas entrer en collision avec les [0] de proteger().
_TERMES = sorted(GLOSSAIRE, key=lambda p: -len(p[0]))
_RE_TERMES = re.compile(
    r"\b(" + "|".join(re.escape(en) for en, _ in _TERMES) + r")\b")
_FR = {en.lower(): fr for en, fr in GLOSSAIRE}


def proteger_glossaire(texte):
    """Sort les termes de jeu du texte ; renvoie (texte, remplacements)."""
    mots = []

    def rempl(m):
        mots.append(_FR[m.group(1).lower()])
        return "§%d§" % (len(mots) - 1)

    return _RE_TERMES.sub(rempl, texte), mots


def restaurer_glossaire(texte, mots):
    def rempl(m):
        i = int(m.group(1))
        return mots[i] if i < len(mots) else m.group(0)

    return re.sub("§\\s*(\\d+)\\s*§", rempl, texte)

