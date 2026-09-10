# -*- coding: utf-8 -*-
r"""Les NOMS EMPOISONNÉS : une même valeur française posée sur des centaines de
sorts sans rapport entre eux.

CE QUE C'EST
------------
Dans `traductions/sorts.json`, 777 clés anglaises qui n'ont rien à voir entre
elles — « Angel of Death », « Overflow ICD », « Emote freeze », « Germination »
— portent toutes la même valeur : « Epreuve de la Foi ». Ce n'est pas une
traduction, c'est un dégât : en jeu, 777 sorts affichent le nom d'un autre.

Le raisonnement de Dan pour purger (26/07/2026) : un joueur qui lit un nom
français FAUX se trompe de sort ; un joueur qui lit l'anglais sait seulement
que ce n'est pas encore traduit. **On n'enlève pas une traduction, on enlève
une erreur** — il n'y a jamais eu de vraie traduction derrière.

⚠️ LA CASSE N'EST PAS UN DISCRIMINANT — c'est le piège de ce chantier
-------------------------------------------------------------------
On a d'abord cru que « le F majuscule » signait le poison et que la vraie
traduction s'écrivait « Epreuve de la foi ». **C'est l'inverse.** Blizzard
écrit « Epreuve de la Foi », F MAJUSCULE et E NON accentué — c'est le talent
de prêtre *Test of Faith*, IDs 47558/47559/47560 de `spells_frFR.json`. Et la
graphie à f minuscule est, elle, PRODUITE PAR NOUS : c'est notre propre règle
d'accent qui fabrique « Épreuve de la foi » dans les bases livrées.

Se fier à la casse aurait donc protégé le poison et purgé la vraie traduction.

LE VRAI DISCRIMINANT : **la clé anglaise est-elle, à l'octet près, un nom de
sort connu du DBC anglais de Blizzard ?** Sur les 780 entrées portant une des
quatre graphies, exactement UNE passe : « Test of Faith ».

Et il faut l'ÉGALITÉ EXACTE, pas une comparaison tolérante : le `meme_nom()`
de `garde_appariement.py` (minuscules, sans accent, sans ponctuation) laisse
passer 7 clés de plus — « Crushed », « buff », « Force cast », « On Fire. »… —
qui sont du poison. Ce module-là existe pour ne pas JETER d'officiels valides ;
ici on a besoin de l'inverse, donc on ne le réutilise pas.

POURQUOI CE MODULE EST AUSSI UN FILTRE, ET PAS SEULEMENT UNE PURGE
------------------------------------------------------------------
`generer_noms_sorts.py` ne lit PAS `traductions/sorts.json`. Il empile quatre
couches : l'officiel Blizzard, nos customs (relus dans `DB_Sorts.lua`), le
**PackFR** et Glayna. Or le PackFR porte 1 793 identifiants empoisonnés à lui
seul. Mesuré : purger `sorts.json` et régénérer laisserait **815 entrées
inchangées** dans `DB_SortsNoms.lua` — gain exactement nul.

D'où `empoisonne()`, appelé dans l'entonnoir `poser()` : il ferme les quatre
couches d'un coup, sans toucher à `sources/` (qui est ré-extractible, et où
une correction se perdrait en silence).

Usage :
    python outils/purger_noms_empoisonnes.py              # simulation
    python outils/purger_noms_empoisonnes.py --appliquer  # purge (+ sauvegardes)
"""

# valeur française empoisonnée -> les clés anglaises qui y ont DROIT.
# La comparaison des clés est une ÉGALITÉ EXACTE, jamais une ressemblance.
POISON = {
    "Epreuve de la Foi": {"Test of Faith"},
    "Épreuve de la Foi": {"Test of Faith"},
    "Epreuve de la foi": {"Test of Faith"},
    "Épreuve de la foi": {"Test of Faith"},

    # Lot 10 (feu vert de Dan, 27/07/2026). Mesuré avant d'écrire :
    # - « Call Pet » est le SEUL nom anglais dont le frFR officiel Blizzard
    #   est « Appel du familier ». Il doit passer — c'est la couche officielle
    #   du pont qui le pose. Aucun de nos 1 879 porteurs n'était lui :
    #   tous étaient des sifflets/vélins/pierres d'invocation distincts
    #   (« Beastmaster's Whistle: X », « Blood Soaked Vellum: X »…).
    "Appel du familier": {"Call Pet"},
    # - « 0 » n'a AUCUN porteur légitime : aucun nom Blizzard ne se traduit
    #   par « 0 », et ses porteurs chez nous étaient des objets de vanité
    #   (montures, ailes), souvent avec un nom espagnol d'époque.
    "0": set(),

    # ----- Lot 13 (option (a) de Dan, 28/07/2026) : les 35 familles -------
    # Mesuré au lot 11 : AUCUNE ne garde plus de 2 porteurs légitimes — ce
    # sont des jointures folles, pas des traductions partagées. Chaque
    # famille est posée sous TOUTES ses graphies (les variantes relevées
    # dans le cache et le pont, plus les formes non accentuées : la couche
    # officielle passe ici AVANT notre règle d'accent, et « Eclair de feu »
    # non accentué doit être reconnu autant que « Éclair de feu »).
    # Les porteurs légitimes sont ceux de la paire officielle exacte —
    # jusqu'à la coquille « Whirwind », qui est de Blizzard lui-même.
    "Chaîne d'éclairs": {"Chain Lightning", "Chain Bolt"},
    "Chaine d'eclairs": {"Chain Lightning", "Chain Bolt"},
    # « Whirlpool » n'existe pas chez Blizzard, mais « Tourbillon » est sa
    # traduction exacte et elle est ANTÉRIEURE au PackFR (une des deux seules
    # entrées de rapports/sorts_cache_avant_packfr.json portant une valeur
    # sur-portée — l'autre est « Ice Breath » -> « Souffle de givre »). La
    # retraduction du lot 13 l'a d'ailleurs reproduite à l'identique.
    "Tourbillon": {"Whirlwind", "Whirwind", "Whirlpool"},
    "HOT PATCHING PLACEHOLDER": set(),
    "Éclair de feu": {"Firebolt"},
    "Eclair de feu": {"Firebolt"},
    "Trait de feu": {"Fire Blast"},
    "Trait de Feu": {"Fire Blast"},
    "Trait de l'ombre": {"Shadow Bolt"},
    "Rénovation": {"Renew"},
    "Renovation": {"Renew"},
    "Tempête de lames": {"Bladestorm"},
    "Tempête de Lames": {"Bladestorm"},
    "Tempete de lames": {"Bladestorm"},
    "Tempete de Lames": {"Bladestorm"},
    "Frénésie impie": {"Unholy Frenzy"},
    "Frenesie impie": {"Unholy Frenzy"},
    "Exorcisme": {"Exorcism"},
    "Javelot de glace": {"Ice Lance"},
    "Souffle de givre": {"Frost Breath"},
    "Pourfendre": {"Rend"},
    "Enrager": {"Enrage"},
    "Frénésie": {"Frenzy"},
    "Frenesie": {"Frenzy"},
    "Ascension HPP": set(),
    "Faux sort": {"Dummy Spell"},
    "Maître de la discrétion": {"Master of Subtlety"},
    "Maitre de la discretion": {"Master of Subtlety"},
    "Tempête divine !": {"Divine Storm!"},
    "Tempête divine !": {"Divine Storm!"},
    "Tempete divine !": {"Divine Storm!"},
    "Tempete divine !": {"Divine Storm!"},
    "Soins inférieurs": {"Lesser Heal"},
    "Soins inferieurs": {"Lesser Heal"},
    "Cannibalisme": {"Cannibalize"},
    "Momma Said Knock You Out - Haut fait": set(),
    "Inferno gangrené": {"Fel Inferno"},
    "Inferno gangrene": {"Fel Inferno"},
    "Blocage 100%": {"100% Block"},
    "Étoile radieuse": set(),
    "Etoile radieuse": set(),
    "Visuel de l'ombre de Bruce": set(),
    "Visuel : Geyser": set(),
    "Contrôle d'Aura": set(),
    "Controle d'Aura": set(),
    "Croissance Inhabituelle": set(),
    "Marqueur universel de cible - NE CHANGEZ PAS CE SORT !": set(),
    "Données SWP": set(),
    "Donnees SWP": set(),
    "Salve de Traits de l'ombre": {"Shadow Bolt Volley"},
    "Déclenchement de Crocs empoisonnés": {"Poisoned Fangs Proc"},
    "Declenchement de Crocs empoisonnes": {"Poisoned Fangs Proc"},
    "Élixir Brouillecaboche": {"Noggenfogger Elixir"},
    "Elixir Brouillecaboche": {"Noggenfogger Elixir"},
    "Tête de flèche jaune": set(),
    "Tete de fleche jaune": set(),
}

# ----- Lot 14 §2 (28/07/2026) : les valeurs que la révélation Wildcard ------
# peut coller sous une carte (« Vendetta (Rang 1) » -> « VenVerrouillage de
# la cibleetta (Rang 1) »). Mesuré par m4_poison_filtre.py (sceptique) : 33
# noms révélables dont le pont contredit le français officiel UNANIME de
# TOUS les homonymes Blizzard — et cet officiel est chaque fois IDENTIQUE à
# l'anglais (« Absolution » -> « Absolution »). Or poser() écarte les paires
# identité : la couche officielle ne protège jamais ces noms, et le PackFR y
# a posé le français de l'ANCIEN nom du sort renommé (jointure par ID, le
# défaut documenté). Les 10 valeurs venues de NOTRE cache sont corrigées à
# la source par outils/purger_pont_cartes.py ; celles du PackFR (23) se
# filtrent ICI, à la lecture, comme les lots 9/10/13.
#
# Porteurs légitimes MESURÉS (porteurs33.py, 28/07) : paires officielles
# Blizzard exactes + les porteurs déjà dans notre cache — statu quo pour ces
# derniers, PAS un blanchiment : plusieurs sont eux-mêmes des jointures
# douteuses (« Tainted Oil Leak » -> « Gelée »), mais ils sont HORS du
# périmètre du lot 14 et l'arbitrage des valeurs en place appartient à Dan.
# Les porteurs du pont ni officiels ni au cache (7 : « Reign of Fire »,
# « Dark Moonfire », « Shadow Manacles », « Shadow Word: Agony »,
# « Shadow Word: Drain », « Freezing Cold », « Veil of Ice ») sont la même
# maladie : ils sortent avec — retraits listés dans
# rapports/pont_cartes_lot14.txt.
POISON_LOT14 = {
    # « Fracasser » (bloc E du programme 3, 29/07/2026). 7 clés sans
    # parenté portaient cette valeur — du Google pur : « Shield Tossing »,
    # « Static Pulse », « Stolen Flesh »… C'est cette famille qui avait
    # fait REFUSER « Sunder » par la barrière au bloc A du programme 2.
    # Le SEUL porteur légitime est « Sunder » : l'officiel Blizzard écrit
    # « Sunder Armor » -> « Fracasser armure », donc « Fracasser » est le
    # mot du jeu. « Smash » semblait légitime lui aussi — mais l'officiel
    # le traduit « Choc » (sort 18944), et l'officiel tranche le
    # vocabulaire (règle 6 de Dan) : notre « Fracasser » y était une
    # divergence, qui faisait TOMBER la clé du pont.
    "Fracasser": {"Sunder"},
    # les 2 CORROMPUES (substitution cassée, mojibake) : aucun droit.
    "VenVerrouillage de la cibleetta": set(),
    "FrÃ©nÃ©sie": set(),
    # l'erreur documentée de la mémoire « vocabulaire cartes de compétence »
    "Le Bastion": set(),
    "Le bastion": set(),
    # les 30 autres, valeur par valeur (graphies vues + non accentuées).
    "Annihiler": set(),
    "Défense adaptative": {"Adaptive Defense"},
    "Defense adaptative": {"Adaptive Defense"},
    "Sublimation": {"Ascendance"},
    "Courroux de Zanza": {"Lesser Shadow Avatar"},
    "Tir de barrage": set(),
    "War Style": set(),
    "Pluie de feu": {"Rain of Fire", "Firefall", "Wild Felfire Dispel"},
    "Afflux": {"Surge", "Mojo Surge"},
    "Armure scoriacée": set(),
    "Armure scoriacee": set(),
    "Toxine explosive": set(),
    # l'officiel Blizzard écrit ce nom avec une espace insécable : cette
    # graphie-ci (espace simple) est celle du PackFR — la paire officielle
    # n'est pas concernée, mais « Shadow Word: Pain » garde son droit.
    "Mot de l'ombre : Douleur": {"Shadow Word: Pain"},
    "Fouet de la douleur": {"Lash of Pain"},
    "Esquive": {"Sidestep", "Elude", "Evading"},
    "Éblouissement": {"Glare"},
    "Eblouissement": {"Glare"},
    "Nova de l'ombre": {"Shadow Nova", "Consumed by Darkness",
                        "Selfless Desperation"},
    "Infected Saliva": {"Bloodthirsty x3", "Endless Thirst x3"},
    "Incendier": set(),
    "Enfer": set(),
    "Malveillance": {"Malevolence"},
    "Don du Monastère": {"Gift of the Monastery"},
    "Don du monastère": {"Gift of the Monastery"},
    "Don du Monastere": {"Gift of the Monastery"},
    "Don du monastere": {"Gift of the Monastery"},
    "Group Selected: Hero": set(),
    "Gelée": {"Slime", "Ahead of the Curve - Naxxramas",
              "Greater Words of Thawing", "Return of the Conqueror's",
              "Tainted Oil Leak", "Venomous Aura"},
    "Gelee": {"Slime", "Ahead of the Curve - Naxxramas",
              "Greater Words of Thawing", "Return of the Conqueror's",
              "Tainted Oil Leak", "Venomous Aura"},
    "Fatigue de combat": {"Battle Fatigue", "Mark of Anarchy"},
    "Rayonnement": set(),
    "Rage de Taldaram": set(),
    "Plongeon frénétique": {"Frenzied Dive"},
    "Plongeon frenetique": {"Frenzied Dive"},
    "Couvaison": set(),
    "Death's Grasp": set(),
    "Portée cramoisie": set(),
    "Portee cramoisie": set(),
    "Nuée de sauterelles": {"Locust Swarm", "Wild Locust Swarm"},
    "Nuee de sauterelles": {"Locust Swarm", "Wild Locust Swarm"},
}
POISON.update(POISON_LOT14)

# LE VERROU PAR CLÉ du lot 14 — la table par VALEUR ne suffit pas ici, et
# c'est MESURÉ (simulation des 4 couches, 28/07/2026) : le PackFR porte
# PLUSIEURS identifiants renommés par nom, chacun avec le français d'un
# ancien nom différent. Bloquer « Annihiler » fait poser « Frappe
# Infernale » (id 504581), puis « Parfum de carnage », etc. — l'hydre :
# 15/33 seulement sortaient propres par valeurs. Le vrai invariant est sur
# la CLÉ : ces 33 noms ont un français officiel Blizzard UNANIME et
# IDENTIQUE à l'anglais (« Vendetta » -> « Vendetta ») ; comme poser()
# écarte les paires identité, la couche officielle ne les protège jamais —
# TOUTE autre valeur posée dessus est donc, par définition, la jointure
# par identifiant. Liste FINIE : exactement les 33 noms révélables mesurés
# par m4_poison_filtre.py (surface Wildcard, lot 14 §2) — pas une règle
# générale, pour ne pas purger au-delà du périmètre arbitré.
CLES_IDENTITE_OFFICIELLE = {
    "Absolution", "Annihilation", "Anticipation", "Ascension", "Avatar",
    "Barrage", "Berserk", "Blizzard", "Charge", "Combustion", "Contagion",
    "Corruption", "Domination", "Evasion", "Illumination", "Implosion",
    "Infection", "Infernal", "Inferno", "Malice", "Martyr", "Napalm",
    "Pestilence", "Purification", "Radiance", "Rage", "Ravage", "Smolder",
    "Suppression", "Torture", "Vendetta", "Vengeance", "Vigilance",
}


def empoisonne(en, fr):
    """Cette paire (nom anglais -> français) est-elle du poison ?

    Vrai quand la valeur est une valeur connue pour être posée en masse sur
    des sorts sans rapport, ET que cette clé anglaise n'en est pas le porteur
    légitime. Faux dans tous les autres cas — en particulier sur une valeur
    absente de la table, donc le filtre ne coûte rien tant que Dan n'a pas
    tranché d'autres familles.
    """
    if not fr:
        return False
    # Le verrou par CLÉ (lot 14) : un nom au français officiel unanime
    # identique à l'anglais ne doit JAMAIS recevoir une autre valeur des
    # couches basses — l'officiel ne le défend pas (paire identité jamais
    # posée) et le PackFR y met le français d'un ancien nom renommé.
    if (en or "").strip() in CLES_IDENTITE_OFFICIELLE \
            and fr.strip() != (en or "").strip():
        return True
    legitimes = POISON.get(fr.strip())
    if legitimes is None:
        return False
    return (en or "").strip() not in legitimes


# ---------------------------------------------------------------------------
# LE GARDE-FOU DU NOMBRE DE PORTEURS (lot 10, 27/07/2026)
# ---------------------------------------------------------------------------
# La cause de fond de toute cette famille : `garde_packfr.texte_sain()` juge
# la FORME d'un texte, jamais COMBIEN de clés anglaises différentes le
# portent. « 0 » est un texte sain ; « 0 » posé sur 896 sorts sans rapport
# est un dégât. Le contrôle qui manquait est ici.
#
# LE SEUIL : 5. Mesuré, pas choisi au jugé — le plafond NATUREL de
# duplication d'une même valeur sur des clés SANS parenté vaut 3, sur trois
# sources propres et indépendantes (notre cache fait main, l'officiel
# Blizzard enUS x frFR, la base Glayna relue main), et AUCUNE valeur légitime
# n'y est portée par 5 clés ou plus. À 5 on laisse une marge d'une unité
# au-dessus du plafond, et on reste 4 fois sous le seuil d'alerte (20) qui a
# servi à cartographier la famille.
#
# NE VAUT QUE POUR LES NOMS. Deux descriptions identiques sont normales
# (1 364 enchantements partagent mot pour mot « Cliquez droit pour appliquer
# cet enchantement… ») : une description DÉCRIT, un nom IDENTIFIE. C'est le
# nom partagé qui trompe le joueur.
SEUIL_PORTEURS = 5

# La PARENTÉ : les rangs, satellites et déclinaisons d'une même mécanique
# partagent leur vocabulaire (« Well Fed - Agility », « Well Fed - Stamina »
# -> « Bien nourri »). Une famille dont les clés partagent presque toutes un
# même mot significatif est une vraie famille, pas un accident : elle passe.
# Les clés du poison, elles, n'ont RIEN en commun (« Angel of Death »,
# « Overflow ICD », « Germination »).
PART_PARENTE = 0.8
_RE_MOT = None      # compilé au premier appel, pour rester sans import en tête

# Mots CREUX : partagés par la moitié des sorts techniques du jeu, ils ne
# prouvent aucune parenté. Sans cette liste, « Témérité » posée sur 92 clés
# sans rapport passait pour une famille parce que 80 % d'entre elles
# contenaient « test » — un mot d'outillage, pas un lien de sens. Ne mettre
# ici QUE des mots d'outillage : un mot de mécanique (« teleport »,
# « whistle ») est justement ce qui fait une vraie famille.
MOTS_CREUX = {"test", "dummy", "aura", "buff", "debuff", "visual", "hidden",
              "spell", "effect", "state", "proc", "trigger", "unused", "old",
              "achievement", "completed", "progress", "cosmetic", "info"}


def _mots_cle(cle):
    global _RE_MOT
    if _RE_MOT is None:
        import re
        _RE_MOT = re.compile(r"[a-z0-9]{3,}")
    return set(_RE_MOT.findall((cle or "").lower())) - MOTS_CREUX


def parente(cles):
    """Ces clés anglaises forment-elles une vraie famille ?

    Vrai si un même mot significatif apparaît dans au moins 80 % d'entre
    elles. Volontairement simple : un test qu'on ne comprend pas est un test
    qu'on désactive au premier faux positif.
    """
    cles = list(cles)
    if len(cles) < 2:
        return True
    compte = {}
    for cle in cles:
        for mot in _mots_cle(cle):
            compte[mot] = compte.get(mot, 0) + 1
    if not compte:
        return False
    return max(compte.values()) >= PART_PARENTE * len(cles)


# Soupape : les valeurs sur-portées que Dan a EXAMINÉES et blanchies malgré
# tout. Vide aujourd'hui — et c'est voulu. Les valeurs sur-portées déjà en
# place ne sont PAS purgées par la barrière (elle ne refuse que les
# ADOPTIONS nouvelles ; ce qui est en place attend l'arbitrage de Dan,
# liste au lot 10 §3). Cette soupape ne sert que le jour où une VRAIE
# famille déclencherait la barrière à l'adoption : on la nomme ici, avec la
# raison, plutôt que de désserrer le seuil pour tout le monde.
TOLERES = set()


def objets_suspects(objets, anglais, seuil=SEUIL_PORTEURS):
    """{valeur N -> identifiants} des noms d'OBJETS portés anormalement.

    L'espace des objets est indexé par IDENTIFIANT, et un même objet y vit
    légitimement en plusieurs exemplaires : le nombre d'identifiants ne
    prouve donc rien à lui seul. Le vrai signal est la DIVERSITÉ des noms
    ANGLAIS derrière : une valeur française posée sur des identifiants dont
    les noms anglais sont multiples et sans parenté est une jointure folle
    (« Bague Casse-Crâne » sur des robes de gladiateur — mesuré au lot 11 :
    636 valeurs dans ce cas).

    `objets` : {id -> {"N": ...}} ; `anglais` : {id -> nom EN}. VIGIE
    seulement : les appelants comptent et rendent compte, ils ne refusent
    rien — l'arbitrage des valeurs en place appartient à Dan.
    """
    par_valeur = {}
    for iid, entree in objets.items():
        n = entree.get("N") if isinstance(entree, dict) else None
        if isinstance(n, str) and n.strip():
            par_valeur.setdefault(n.strip(), []).append(iid)
    suspects = {}
    for valeur, ids in par_valeur.items():
        if len(ids) < seuil or valeur in POISON or valeur in TOLERES:
            continue
        noms_en = {anglais[i] for i in ids if i in anglais}
        # un seul nom anglais (ou aucun de connu) : des EXEMPLAIRES du même
        # objet — c'est la vie normale de cet espace.
        if len(noms_en) < 2 or parente(noms_en):
            continue
        # Ne compter que la MINORITÉ : sous « [NOM DE L'ARTICLE MANQUANT] »,
        # des milliers d'identifiants sont la traduction FIDÈLE du
        # bouche-trou anglais — le dégât, ce sont les identifiants dont le
        # nom anglais est AUTRE. Compter la famille entière gonflerait la
        # mesure d'un facteur dix et la rendrait illisible.
        compte = {}
        for i in ids:
            en = anglais.get(i)
            if en:
                compte[en] = compte.get(en, 0) + 1
        dominant = max(compte, key=compte.get)
        minoritaires = [i for i in ids
                        if i in anglais and anglais[i] != dominant]
        if len(minoritaires) < 2:
            continue
        suspects[valeur] = sorted(minoritaires)
    return suspects


# ---------------------------------------------------------------------------
# LA BARRIÈRE DE STRUCTURE (lot 14, 28/07/2026)
# ---------------------------------------------------------------------------
# La jointure PackFR PAR IDENTIFIANT a posé des valeurs françaises
# structurellement étrangères à leur clé anglaise. Deux formes, toutes deux
# mesurées au moteur réel de l'addon (banc du lot 14, 49 676 entrées) :
#   - un marqueur maison @…@ présent d'un SEUL côté : le D du sort 3599
#     porte @learns:92159@ que sa clé n'a pas -> le moteur abandonne TOUTE
#     la description (Modules/Sorts.lua, appliquer_valeurs). Dans le cache
#     d'avant-purge : 30 @learns, 60 @req, 271 @ext fautifs (clé sans le
#     marqueur) sur 120/873/3 929 porteurs — le marqueur n'est fautif que
#     d'un seul côté ;
#   - une variable $<id>… dont l'id n'existe côté EN ni tel quel ni décalé
#     de +1 100 000 : le français d'un AUTRE sort (649 échecs au banc).
# Le décalage +1 100 000 (clones d'Ascension) est TOLÉRÉ ici : c'est une
# provenance identifiable et mécaniquement réparable (le remap du lot 14 en
# a prouvé 881 au moteur), pas un contenu étranger.
#
# Même régime qu'au lot 10 : REFUS BRUYANT à l'adoption (adopter_packfr_
# cache.py), vigie sur l'existant — jamais rien en silence.
DECALAGE_CLONE = 1100000

_RE_STRUCT = None


def _re_struct():
    """Compilées au premier appel — même raison que _mots_cle : pas
    d'import en tête de module."""
    global _RE_STRUCT
    if _RE_STRUCT is None:
        import re
        _RE_STRUCT = {
            # blocs à contenu TRADUIT côté FR : on les retire avant de
            # comparer les marqueurs point, on ne compare que leur nombre
            "bloc": re.compile(r"@(ifknown|ifnotknown|wflocation):"
                               r".-?.*?:\1@|@wflocation:[^@]*@", re.S),
            "type_bloc": re.compile(r"@(ifknown|ifnotknown|wflocation):"),
            # marqueurs point : @learns:92159@ @req:8921@ @unlockby:635@
            # @req:1122520:req@ @s:101087:0@ …
            "point": re.compile(r"@[a-zA-Z]+:\d+(?::-?\d+|:[a-zA-Z]+)?@"),
            "ext": re.compile(r"@ext:"),
            # variables à identifiant numérique : $64843s2, $6788d…
            "var": re.compile(r"\$(\d+)[a-zA-Z]"),
        }
    return _RE_STRUCT


def structure_divergente(en, fr):
    """Raison du refus si la structure des variables du FR diverge de sa
    clé EN, sinon None. Égalités exactes, jamais de ressemblance."""
    if not en or not fr:
        return None
    r = _re_struct()
    en_sans_blocs = r["bloc"].sub("", en)
    fr_sans_blocs = r["bloc"].sub("", fr)
    # 1. blocs @ifknown/@ifnotknown/@wflocation : mêmes types, même nombre
    types_en = sorted(r["type_bloc"].findall(en))
    types_fr = sorted(r["type_bloc"].findall(fr))
    if types_en != types_fr:
        return "blocs @…@ inégaux (EN %s / FR %s)" % (types_en, types_fr)
    # 2. marqueurs point : même multi-ensemble exact des deux côtés
    points_en = sorted(r["point"].findall(en_sans_blocs))
    points_fr = sorted(r["point"].findall(fr_sans_blocs))
    if points_en != points_fr:
        seuls = [m for m in points_fr if m not in points_en] \
            or [m for m in points_en if m not in points_fr]
        return "marqueur d'un seul côté : %s" % seuls[:3]
    # 3. blocs @ext: : même nombre
    if len(r["ext"].findall(en)) != len(r["ext"].findall(fr)):
        return "blocs @ext: inégaux"
    # 4. variables numériques du FR : id présent côté EN, tel quel ou
    # décalé de +1 100 000
    ids_en = {int(m) for m in r["var"].findall(en)}
    for m in r["var"].findall(fr):
        vid = int(m)
        if vid not in ids_en and vid + DECALAGE_CLONE not in ids_en:
            return "variable $%s… inconnue de la clé (ni décalée)" % m
    return None


# Vigie du FRANGLAIS (correctif du sceptique, lot 14) : un D adopté peut
# porter des mots-outils anglais tout en s'ALIGNANT parfaitement — la
# famille « Follow Up » (« …plus ${$m1+0} and gain Follow jusqu'à… ») est
# passée au travers du banc ET de l'écran. Mesuré : 316 sorties « traduites »
# du banc portaient un de ces mots. VIGIE seulement, jamais un refus : la
# liste sur-signale un peu (« gain » existe en français) et l'arbitrage du
# contenu reste à Dan.
_RE_FRANGLAIS = None


def mot_anglais(texte):
    """Le premier mot-outil anglais trouvé dans le texte, ou None.

    « gain » et « gains » ont été RETIRÉS de la liste le 29/07/2026
    (bloc C du programme 3) : ce sont de VRAIS mots français, et ils
    faisaient 112 des 262 signalements de la vigie — « Augmentez les
    gains de réputation de votre groupe », « le gain d'âme Gangreforgé ».
    Échantillon de 10 tirés au hasard : 10 sur 10 légitimes. Un compteur
    qui crie faux 43 % du temps ne se lit plus.

    N'ajouter ici QUE des mots qui n'existent pas en français : « target »
    reste (le français est « cible »), « damage » reste, mais aucun mot
    qui aurait un homographe français légitime.
    """
    global _RE_FRANGLAIS
    if _RE_FRANGLAIS is None:
        import re
        _RE_FRANGLAIS = re.compile(
            r"\b(and|the|your|you|with|when|while|deals"
            r"|dealing|damage|within|target|enemy|causing)\b")
    m = _RE_FRANGLAIS.search(texte or "")
    return m.group(1) if m else None


def porteurs_anormaux(noms, seuil=SEUIL_PORTEURS):
    """{valeur -> clés triées} des valeurs portées anormalement.

    `noms` est un dictionnaire {clé anglaise -> valeur française}. Une valeur
    est anormale quand elle est portée par `seuil` clés ou plus, que ces clés
    n'ont AUCUNE parenté entre elles, et qu'elle n'est ni déjà dans POISON
    (traitée en amont) ni dans TOLERES (en attente d'arbitrage).
    """
    porteurs = {}
    for cle, valeur in noms.items():
        if isinstance(valeur, str) and valeur.strip():
            porteurs.setdefault(valeur.strip(), []).append(cle)
    anormaux = {}
    for valeur, cles in porteurs.items():
        if len(cles) < seuil:
            continue
        if valeur in POISON or valeur in TOLERES:
            continue
        if parente(cles):
            continue
        anormaux[valeur] = sorted(cles)
    return anormaux
