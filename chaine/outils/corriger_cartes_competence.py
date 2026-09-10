# -*- coding: utf-8 -*-
"""
Corrige les noms/descriptions des items « Skill Card » dans objets_dbc.json.

Noms : reconstruit "Carte de compétence [chanceuse][ dorée] - <sort>".
  Le <sort> vient de notre base validée (sorts.json) UNIQUEMENT si ses mots
  concordent avec le nom déjà présent (sinon on garde l'existant : la base a
  de vraies erreurs, ex. sorts['Absolution'] = 'Le Bastion').
Descriptions : 16 infobulles de paquets réécrites à la main + les paquets
  "Contains N ... Skill Cards" générés proprement.

Vocabulaire (arbitré par Dan) : Golden -> dorée, Lucky -> chanceuse.
Darkmoon -> Sombrelune (localisation officielle FR).

  python outils/corriger_cartes_competence.py             # simulation + rapport
  python outils/corriger_cartes_competence.py --appliquer  # écrit (+ .bak)
"""
import json, re, sys, os, shutil
from collections import Counter

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FICHIER = os.path.join(RACINE, 'traductions', 'objets_dbc.json')
RAPPORT = os.path.join(RACINE, 'rapports', 'cartes_competence_preview.txt')

FUITE = re.compile(r'\b(Golden|Lucky|Ability|Talent|Common|Uncommon|Rare|Epic|'
                   r'Legendary|Skill\s*Cards?|Skillcards?|Darkmoon)\b')

def charger(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def est_carte(k):
    return 'skillcard' in k.lower().replace(' ', '')

def norm(k):
    return k.replace('\r\n', '\n').replace('\r', '\n')

# ---------- index des noms de sorts validés ----------
def construire_index():
    idx = {}
    def ajoute(dico):
        for k, v in dico.items():
            if isinstance(k, str) and isinstance(v, str) and v.strip():
                idx.setdefault(k.strip().lower(), v.strip())
    sorts = charger(os.path.join(RACINE, 'traductions', 'sorts.json'))
    if isinstance(sorts, dict) and isinstance(sorts.get('noms'), dict):
        ajoute(sorts['noms'])
    try:
        o = charger(os.path.join(RACINE, 'traductions', 'objets.json'))
        d = o['noms'] if isinstance(o.get('noms'), dict) else o
        ajoute({k: v for k, v in d.items()
                if isinstance(k, str) and isinstance(v, str) and not est_carte(k)})
    except Exception:
        pass
    return idx

# ---------- reconstruction des NOMS ----------
RE_CARTE = re.compile(r'^(?P<pre>.*?)\bskill\s?cards?\b\s*(?:[-:–]\s*(?P<post>.*))?$',
                      re.IGNORECASE | re.DOTALL)

def prefixe_fr(golden, lucky):
    adjs = []
    if lucky:
        adjs.append('chanceuse')
    if golden:
        adjs.append('dorée')
    return 'Carte de compétence' + ((' ' + ' '.join(adjs)) if adjs else '')

def queue_existante(ancien):
    # tiret/deux-points/tiret long entouré d'espaces (normaux ou insécables).
    s = ancien.replace(' ', ' ')
    m = re.search(r' *[-:–—] +', s)
    if m:
        return ancien[m.end():].strip()
    return None

def mots(s):
    return set(w for w in re.findall(r"[0-9a-zàâäéèêëïîôöùûüçœ]+", s.lower())
               if len(w) > 2)

def choisir(base, tail):
    """base = nom validé (peut être faux), tail = nom déjà en place.
    On préfère 'base' seulement s'il CONCORDE avec 'tail' (mêmes mots)."""
    if base and tail:
        a, b = mots(base), mots(tail)
        if a and b and len(a & b) / len(a | b) >= 0.5:
            return base, 'base-concordant'
        return tail, 'queue-conservee'
    if tail:
        return tail, 'queue'
    if base:
        return base, 'base-seule'
    return None, 'rien'

def traduire_nom(cle, ancien, idx):
    m = RE_CARTE.match(cle.strip())
    if not m:
        return None, 'motif-inconnu'
    pre = (m.group('pre') or '').strip()
    post = (m.group('post') or '').strip()
    prel = pre.lower()
    golden, lucky = 'golden' in prel, 'lucky' in prel
    sort_en = post if post else re.sub(r'\b(golden|lucky)\b', '', pre, flags=re.I).strip()
    sort_en = sort_en.strip().strip('"').strip("'").strip()
    if not sort_en:
        return None, 'sort-vide'
    fr, src = choisir(idx.get(sort_en.lower()), queue_existante(ancien))
    if not fr:
        return None, 'pas-de-fr'
    nouveau = prefixe_fr(golden, lucky) + ' - ' + fr.strip().strip('"').strip()
    if nouveau == ancien:
        return None, 'deja-bon'
    return nouveau, src

# ---------- descriptions de paquets "Contains N ... Skill Cards" ----------
RE_PACK = re.compile(
    r'^Contains\s+(\d+)\s+(?P<q>[A-Za-z ]+?)\s+Skill\s?Cards?\s+that can be used '
    r'at level 1 during Prestige or on a new character\.$', re.I)
RAR_F = {'common': 'commune', 'uncommon': 'peu commune', 'rare': 'rare',
         'epic': 'épique', 'legendary': 'légendaire'}
RAR_M = {'common': 'commun', 'uncommon': 'peu commun', 'rare': 'rare',
         'epic': 'épique', 'legendary': 'légendaire'}

def desc_pack_fr(n, q):
    mo = q.lower().split()
    golden = 'golden' in mo
    typ = 'ability' if 'ability' in mo else ('talent' if 'talent' in mo else None)
    rar = next((r for r in RAR_F if r in mo), None)
    txt = 'Contient %s cartes de compétence' % n
    if golden:
        txt += ' dorées'
    if typ == 'ability':
        txt += ' de capacité' + ((' ' + RAR_F[rar]) if rar else '')
    elif typ == 'talent':
        txt += ' de talent' + ((' ' + RAR_M[rar]) if rar else '')
    elif rar:
        txt += ' ' + RAR_F[rar] + 's'
    return txt + ' utilisables au niveau 1 pendant le Prestige ou sur un nouveau personnage.'

# ---------- 16 descriptions libres réécrites à la main ----------
AUTHORED = {
 "- Contains a random Lucky Skill Card that can be activated at level 1 during Prestige or a new character.\n- GoldenSkill Cards guarantee you'll draft a specific spell while leveling.\n- Golden Skill cards can be obtained with gold from Silas in your Capital City.":
 "- Contient une carte de compétence chanceuse aléatoire, activable au niveau 1 pendant le Prestige ou sur un nouveau personnage.\n- Les cartes de compétence dorées vous garantissent d'obtenir un sort précis pendant la montée en niveau.\n- Les cartes de compétence dorées s'obtiennent contre de l'or auprès de Silas, dans votre capitale.",

 "Contains 5 random Ability Skill Cards that can be used at level 1 during Prestige or on a new character.\n\nAbility Skill Cards guarantee drafting a specific Ability.\n\nAbility Skill Card Packs are obtained primarily from Silas Darkmoon in a capital city.":
 "Contient 5 cartes de compétence de capacité aléatoires, utilisables au niveau 1 pendant le Prestige ou sur un nouveau personnage.\n\nLes cartes de compétence de capacité garantissent d'obtenir une capacité précise.\n\nLes paquets de cartes de compétence de capacité s'obtiennent principalement auprès de Silas Sombrelune, dans une capitale.",

 "Contains 5 random Talent Skill Cards that can be used at level 1 during Prestige or on a new character.\n\nTalent Skill Cards guarantee drafting a specific talent of varying quality.\n\nTalent Skill Card Packs are obtained primarily from Silas Darkmoon in a capital city.":
 "Contient 5 cartes de compétence de talent aléatoires, utilisables au niveau 1 pendant le Prestige ou sur un nouveau personnage.\n\nLes cartes de compétence de talent garantissent d'obtenir un talent précis de qualité variable.\n\nLes paquets de cartes de compétence de talent s'obtiennent principalement auprès de Silas Sombrelune, dans une capitale.",

 "Contains a random Golden Lucky Skill Card that can be activated at level 1 during Prestige or a new character.\nGolden Lucky Skill Cards greatly increase the chance to draft a specific spell.\n\nThese are bought with Gold from Silas Darkmoon.":
 "Contient une carte de compétence chanceuse dorée aléatoire, activable au niveau 1 pendant le Prestige ou sur un nouveau personnage.\nLes cartes de compétence chanceuses dorées augmentent fortement les chances d'obtenir un sort précis.\n\nElles s'achètent contre de l'or auprès de Silas Sombrelune.",

 "Contains a random Lucky Skill Card that can be activated at level 1 during Prestige or a new character.\nLucky Skill Cards greatly increase the chance to draft a specific spell.\n\nThese are obtained with Marks of Ascension from Silas Darkmoon.\nGolden Skill cards can be obtained with gold from Silas in your Capital City.":
 "Contient une carte de compétence chanceuse aléatoire, activable au niveau 1 pendant le Prestige ou sur un nouveau personnage.\nLes cartes de compétence chanceuses augmentent fortement les chances d'obtenir un sort précis.\n\nElles s'obtiennent contre des Marques d'Ascension auprès de Silas Sombrelune.\nLes cartes de compétence dorées s'obtiennent contre de l'or auprès de Silas, dans votre capitale.",

 "Contains a random Skill Card that can be used at level 1 during Prestige or on a new character.\n\nSkill Cards guarantee drafting a specific spell.\n\nSkillcards are obtained from Silas Darkmoon in a capital city.":
 "Contient une carte de compétence aléatoire, utilisable au niveau 1 pendant le Prestige ou sur un nouveau personnage.\n\nLes cartes de compétence garantissent d'obtenir un sort précis.\n\nLes cartes de compétence s'obtiennent auprès de Silas Sombrelune, dans une capitale.",

 "Contains a random Talent Golden Skill Card that can be used at level 1 during Prestige or on a new character.\n\nTalent Golden Skill Cards guarantee drafting a specific spell.\n\nTalent Golden Skill Cards are obtained from Silas Darkmoon in a capital city.":
 "Contient une carte de compétence de talent dorée aléatoire, utilisable au niveau 1 pendant le Prestige ou sur un nouveau personnage.\n\nLes cartes de compétence de talent dorées garantissent d'obtenir un sort précis.\n\nLes cartes de compétence de talent dorées s'obtiennent auprès de Silas Sombrelune, dans une capitale.",

 "Contains a random Talent Skill Card that can be used at level 1 during Prestige or on a new character.\n\nTalent Skill Cards guarantee drafting a specific spell.\n\nTalent Skill Cards are obtained from Silas Darkmoon in a capital city.":
 "Contient une carte de compétence de talent aléatoire, utilisable au niveau 1 pendant le Prestige ou sur un nouveau personnage.\n\nLes cartes de compétence de talent garantissent d'obtenir un sort précis.\n\nLes cartes de compétence de talent s'obtiennent auprès de Silas Sombrelune, dans une capitale.",

 "Gives you a random Golden Skill Card":
 "Vous donne une carte de compétence dorée aléatoire",

 "Gives you a random Skill Card":
 "Vous donne une carte de compétence aléatoire",

 "Obtained from Golden sealed card packs given by Silas Darkmoon, these tickets can be turned in at Silas for Specific Skillcards and other extravagent prizes!":
 "Obtenus dans les paquets de cartes scellés dorés offerts par Silas Sombrelune, ces tickets s'échangent auprès de Silas contre des cartes de compétence précises et d'autres prix extravagants !",

 "Obtained from Sealed card packs given by Silas Darkmoon, these tickets can be turned in at Silas for Specific Skillcards and other extravagent prizes!":
 "Obtenus dans les paquets de cartes scellés offerts par Silas Sombrelune, ces tickets s'échangent auprès de Silas contre des cartes de compétence précises et d'autres prix extravagants !",

 "Uncover 5 Golden Sealed Cards you can use at level 20 to guarantee future spell rolls.\nThese Skillcards apply to all specializations, persist through death, and will apply to your next run.":
 "Révèle 5 cartes scellées dorées, utilisables au niveau 20 pour garantir de futurs tirages de sorts.\nCes cartes de compétence s'appliquent à toutes les spécialisations, persistent après la mort et vaudront pour votre prochaine partie.",

 "Uncover a Skill Card used to help your future heroes.":
 "Révèle une carte de compétence pour aider vos futurs héros.",

 "You get Skill Cards from Silas Darkmoon!\n\nYou can activate skill cards in the Skill Card Collection between levels 1 and 9.":
 "Vous obtenez des cartes de compétence auprès de Silas Sombrelune !\n\nVous pouvez activer vos cartes de compétence dans la Collection de cartes de compétence, entre les niveaux 1 et 9.",

 "You get Skill Cards from Silas Darkmoon!\nYou can activate skill cards in the Skill Card Collection between levels 1 and 9.":
 "Vous obtenez des cartes de compétence auprès de Silas Sombrelune !\nVous pouvez activer vos cartes de compétence dans la Collection de cartes de compétence, entre les niveaux 1 et 9.",
}
AUTHORED = {norm(k): v for k, v in AUTHORED.items()}

def main():
    appliquer = '--appliquer' in sys.argv
    data = charger(FICHIER)
    idx = construire_index()
    noms, descs = data['noms'], data['descriptions']

    chg_noms, garde = [], Counter()
    for cle, ancien in list(noms.items()):
        if not est_carte(cle):
            continue
        nouveau, info = traduire_nom(cle, ancien, idx)
        if nouveau:
            chg_noms.append((cle, ancien, nouveau, info))
        else:
            garde[info] += 1

    chg_descs = []
    for cle, ancien in list(descs.items()):
        if not est_carte(cle):
            continue
        n = AUTHORED.get(norm(cle))
        if n is None:
            m = RE_PACK.match(cle.strip())
            if m:
                n = desc_pack_fr(m.group(1), m.group('q'))
        if n and n != ancien:
            chg_descs.append((cle, ancien, n))

    # --- scan anti-anglais : simulate puis vérifie qu'il ne reste rien ---
    apres_noms = dict(noms); apres_noms.update({k: n for k, _, n, _ in chg_noms})
    apres_descs = dict(descs); apres_descs.update({k: n for k, _, n in chg_descs})
    residus = []
    for sect, dd in (('nom', apres_noms), ('desc', apres_descs)):
        for k, v in dd.items():
            if est_carte(k):
                vv = re.sub(r'@[^@]*@', '', v)  # ignore marqueurs @...@
                if FUITE.search(vv):
                    residus.append((sect, k, v))

    os.makedirs(os.path.dirname(RAPPORT), exist_ok=True)
    with open(RAPPORT, 'w', encoding='utf-8') as r:
        r.write("== NOMS : %d changements ==\n\n" % len(chg_noms))
        for cle, a, n, src in chg_noms:
            r.write("AV: %s\nAP: %s   [%s]\n\n" % (a.replace('\n', ' '), n.replace('\n', ' '), src))
        r.write("\n== DESCRIPTIONS : %d changements ==\n\n" % len(chg_descs))
        for cle, a, n in chg_descs:
            r.write("AV: %s\nAP: %s\n\n" % (a.replace('\n', ' '), n.replace('\n', ' ')))

    print("NOMS -> %d modifiés (%s)" % (len(chg_noms), dict(Counter(s for *_, s in chg_noms))))
    print("NOMS gardés tels quels ->", dict(garde))
    print("DESCRIPTIONS -> %d modifiées" % len(chg_descs))
    print("RÉSIDUS anglais après coup ->", len(residus))
    for sect, k, v in residus[:25]:
        print("   [%s] %s" % (sect, v[:80].replace('\n', ' ')))
    print("\n--- échantillon noms (cas sensibles) ---")
    for cle, a, n, src in chg_noms:
        if any(x in a for x in ('Absolution', 'adrénaline', 'Ancestral Esprit',
                                'abjurateur', 'forme de chat')):
            print("  AV:", a[:58], "\n  AP:", n[:58], "[%s]" % src)
    print("\nRapport complet :", RAPPORT)

    if appliquer:
        shutil.copy2(FICHIER, FICHIER + '.bak')
        for cle, a, n, src in chg_noms:
            noms[cle] = n
        for cle, a, n in chg_descs:
            descs[cle] = n
        with open(FICHIER, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        print("\n>>> APPLIQUÉ. Sauvegarde : %s.bak" % os.path.basename(FICHIER))
    else:
        print("\n(simulation — rien écrit. Relancer avec --appliquer)")

if __name__ == '__main__':
    main()
