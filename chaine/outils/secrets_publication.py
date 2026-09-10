# -*- coding: utf-8 -*-
r"""LES SECRETS SUR LE CHEMIN DE LA PUBLICATION (programme 6, 29/07/2026).

CE QUI EST ARRIVÉ. L'arbre privé porte, en dur, l'URL du webhook Discord des
rapports. L'arbre publié porte `""` à la même ligne. Le geste n° 1 du plan de
remise d'aplomb disait « synchroniser les trois sources du privé vers le
dépôt public » — une copie fidèle aurait écrasé le `""` par le webhook, et
le `git push` du geste n° 4 l'aurait rendu public. Une URL de webhook EST le
droit d'écrire dans le salon : ni compte, ni mot de passe, ni révocation
partielle.

POURQUOI AUCUN GARDE-FOU NE L'AURAIT VU, et c'est le vrai sujet :
  - construire_zip_release.py cherche bien « discord.com/api/webhooks »,
    mais seulement dans les .lua/.toc/.txt/.md/.xml — il saute les .py ;
  - verifier_hub.py ne regarde que le relevé de diagnostic ;
  - verifier_arbre_publie.py exigeait l'ÉGALITÉ des deux arbres. Or l'arbre
    publié doit être DÉLIBÉRÉMENT différent sur cette ligne. Les deux
    exigences sont incompatibles : soit on synchronise fidèlement et il sort
    vert pendant que le secret part, soit on neutralise et il sort rouge
    pour toujours. Un garde-fou qui ne peut être vert qu'au prix d'une
    fuite est pire qu'absent : il donne raison au geste dangereux.

CE MODULE POSE LES DEUX RÉPONSES, et elles sont indépendantes exprès :

  1. LA DIFFÉRENCE DÉCLARÉE (`neutraliser`). Un fichier déclaratif dit
     quelles affectations doivent être neutralisées et par quelle valeur
     EXACTE. Le garde-fou ne compare plus « privé == publié » mais
     « privé NEUTRALISÉ == publié » : une seule comparaison qui exige à la
     fois l'identité partout ailleurs ET la valeur neutre exacte sur les
     entrées déclarées. Une valeur inattendue est un refus, pas seulement
     une valeur « différente ».

  2. LE BALAYAGE (`balayer_texte`), qui ne dépend d'AUCUNE liste. La
     déclaration ci-dessus suppose qu'on ait PENSÉ à déclarer le bon
     secret — c'est exactement l'hypothèse qui a lâché. Le balayage, lui,
     cherche des MOTIFS, sur toutes les extensions, et attrape le secret
     que personne n'a déclaré. C'est le seul des deux qui protège contre
     notre inattention future.

⚠️ La MÊME fonction `neutraliser` sert au garde-fou et à l'outil de
synchronisation. C'est volontaire : deux implémentations dériveraient, et le
jour où elles divergeraient, le garde-fou validerait un arbre que l'outil ne
sait plus produire.
"""
import io
import json
import math
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECLARATIONS = os.path.join(BASE, "outils", "secrets_injectes.json")
PUBLIC = os.path.join(BASE, "depot_github")

# Les sources qui construisent réellement l'exe distribué, et qui doivent
# donc exister à l'identique (aux secrets déclarés près) dans le dépôt
# public. Cette liste vit ICI et pas dans chacun des deux outils : celui qui
# synchronise et celui qui vérifie doivent parler du MÊME ensemble, sinon on
# publierait un fichier que personne ne contrôle.
# Les README et les docs vivent DANS le dépôt public et s'y éditent : ils
# n'ont pas de jumeau privé, on ne les synchronise pas.
SOURCES = [
    "compagnon/compagnon.py",
    "compagnon/compagnon_hub.py",
    "compagnon/interface_hub.py",
    "compagnon/fabriquer_decor_hub.py",
    "compagnon/AscensionFR_Hub.spec",
]


# ---------------------------------------------------------------------------
# 1. LE BALAYAGE — motifs de secrets, indépendant de toute déclaration
# ---------------------------------------------------------------------------
# Chaque motif est une famille de jetons dont la SEULE présence dans un
# fichier destiné au public est une faute. Ils sont volontairement PRÉCIS :
# un balayage qui crie au loup finit désactivé, et on aurait remplacé une
# fuite par un faux rouge permanent — la maladie qu'on soigne depuis une
# semaine. La précision se vérifie, elle ne se décrète pas : le balayage
# tourne sur l'arbre réel et son taux de fausse alerte est mesuré.
MOTIFS = [
    ("webhook Discord",
     re.compile(r"https?://(?:ptb\.|canary\.)?discord(?:app)?\.com"
                r"/api(?:/v\d+)?/webhooks/\d+/[\w-]{20,}")),
    ("webhook Discord (forme nue)",
     re.compile(r"discord(?:app)?\.com/api(?:/v\d+)?/webhooks/\d+/[\w-]{20,}")),
    ("jeton de bot Discord",
     re.compile(r"\b[MNO][A-Za-z\d_-]{23,}\.[A-Za-z\d_-]{6}"
                r"\.[A-Za-z\d_-]{27,}\b")),
    ("jeton GitHub",
     re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b")),
    ("jeton GitHub à portée fine",
     re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,}\b")),
    ("clé d'API Google",
     re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("jeton Slack",
     re.compile(r"\bxox[abposr]-[0-9A-Za-z-]{10,}\b")),
    ("clé d'accès AWS",
     re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("jeton Stripe",
     re.compile(r"\b(?:sk|rk)_(?:live|test)_[0-9A-Za-z]{20,}\b")),
    # Les clés des fournisseurs de modèles : elles emploient le TIRET, pas le
    # souligné, donc le motif Stripe passait juste à côté.
    ("clé d'API de modèle (Anthropic / OpenAI)",
     re.compile(r"\bsk-(?:ant-|proj-|svcacct-)?[A-Za-z0-9_-]{24,}\b")),
    ("clé privée",
     re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY(?: BLOCK)?-----")),
    ("URL à identifiants",
     re.compile(r"://[A-Za-z0-9_.%-]*:[^\s/@\"']{6,}@[A-Za-z0-9.-]+")),
    ("webhook Slack / Teams / Google Chat",
     re.compile(r"https://(?:hooks\.slack\.com/services/[A-Za-z0-9/+]{20,}"
                r"|[a-z0-9.-]*webhook\.office\.com/webhookb2/[\w@/-]{20,}"
                r"|chat\.googleapis\.com/v1/spaces/[\w/=?&-]{20,})")),
    ("jeton d'application Slack",
     re.compile(r"\bxapp-\d-[A-Za-z0-9-]{10,}\b")),
    ("clé SendGrid",
     re.compile(r"\bSG\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}\b")),
    ("jeton npm",
     re.compile(r"\bnpm_[A-Za-z0-9]{36}\b")),
    ("jeton PyPI",
     re.compile(r"\bpypi-AgEIcHlwaS5vcmc[A-Za-z0-9_-]{16,}\b")),
    ("jeton de bot Telegram",
     re.compile(r"\b\d{8,10}:AA[A-Za-z0-9_-]{32,}\b")),
    ("DSN Sentry",
     re.compile(r"https://[a-f0-9]{16,}@[\w.-]*ingest[\w.-]*\.sentry\.io/\d+")),
    ("jeton JWT",
     re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}"
                r"\.[A-Za-z0-9_-]{8,}\b")),
    # Un chemin C:\Users\<nom> est une TRACE PERSONNELLE : le nom du compte
    # Windows (souvent proche du vrai nom) et parfois un UUID de session
    # partent avec. Famille née au programme 33 : le second filet a trouvé
    # deux outils portant en dur un dossier temporaire du mainteneur — le
    # gate promettait d'attraper « les chemins de la machine de Dan » et ne
    # le faisait pas. Public/Default sont des profils système, pas des gens.
    ("chemin personnel Windows",
     re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+"
                r"(?!Public\b|Default\b|All Users\b)"
                r"[^\\/:*?\"'<>|\r\n]+")),
]

# --- pseudos de récolteurs (programme 34, bloc 0) --------------------------
# La famille que le gate ne connaissait pas : une liste de repli EN DUR est
# partie dans le dépôt cloud — le fichier était protégé (gitignoré), la
# copie en dur ne l'était pas. Même mécanique que le webhook du programme 6.
# La famille est DYNAMIQUE : les noms viennent de noms_recolteurs.local.txt
# (la seule source, plus jamais le code). Fichier absent -> famille inerte,
# et c'est aux appelants de dire qu'ils balaient sans elle.
# Le fichier de déclaration LUI-MÊME est épargné (comme secrets_injectes) :
# il est gitignoré partout, et dans le cloud il doit vivre à la racine pour
# ARMER la famille sans se faire mordre.
FICHIER_NOMS_RECOLTEURS = os.path.join(BASE, "noms_recolteurs.local.txt")
_noms_recolteurs_charges = None


def noms_recolteurs():
    global _noms_recolteurs_charges
    if _noms_recolteurs_charges is None:
        noms = []
        try:
            with io.open(FICHIER_NOMS_RECOLTEURS, encoding="utf-8") as f:
                for ligne in f:
                    n = ligne.strip()
                    if n and not n.startswith("#") and n not in noms:
                        noms.append(n)
        except (OSError, IOError):
            pass
        _noms_recolteurs_charges = noms
    return _noms_recolteurs_charges


# Les codes de format du client, à dénuder avant la recherche de pseudos :
# couleur (|cAARRGGBB … |r) et textures (|T…|t).
RE_CODES_CLIENT = re.compile(r"\|c[0-9A-Fa-f]{8}|\|r\b|\|T[^|]*\|t")


def motif_recolteurs(noms):
    """Pas de \\b à gauche : un pseudo collé à un code couleur
    (« |cFFB5FFFFNom ») n'a pas de frontière de mot — le piège des codes
    couleur collés, déjà payé deux fois. Du plus long au plus court, pour
    qu'un préfixe ne mange pas son extension."""
    if not noms:
        return None
    return re.compile(r"(?<![A-Za-z])(?:%s)(?![a-zA-Zéè])"
                      % "|".join(re.escape(n) for n in
                                 sorted(noms, key=len, reverse=True)))

# L'affectation qui SENT le secret. Celle-ci ne peut pas être précise par sa
# seule forme — « token = "abc" » est innocent — donc elle est confirmée par
# l'ENTROPIE de la valeur : un vrai jeton est une chaîne à fort désordre,
# une valeur de configuration ne l'est pas. On ne décrète pas le seuil, on
# le mesure sur l'arbre réel (voir --mesurer).
# ⚠️ DEUX DÉFAUTS CRITIQUES DU PREMIER JET, trouvés par une relecture
# adversariale et reproduits à l'exécution. Ils comptent double, parce que ce
# gabarit est le SEUL filet pour les familles absentes de MOTIFS — donc le
# seul dispositif qui protège « contre notre inattention future ».
#
#   1. Le mot-clé devait OUVRIR le nom. Le gabarit commençait par
#      « \b(secret|token|…) » : dans « DISCORD_TOKEN », le souligné qui
#      précède TOKEN est un caractère de mot, donc `\b` n'y voit aucune
#      frontière. `DISCORD_TOKEN`, `SMTP_PASSWORD`, `ANTHROPIC_API_KEY`,
#      `CLIENT_SECRET` étaient INVISIBLES — et NOM_TYPE est justement la
#      convention dominante des constantes Python.
#      C'est EXACTEMENT le piège des codes couleur collés (« |cFFB5FFFF » +
#      « Starcaller »), où `\b` ratait déjà en silence. Le même piège, deux
#      fois : d'où le préfixe explicite ci-dessous plutôt qu'un `\b`.
#
#   2. La valeur devait être ENTRE GUILLEMETS et COLLÉE au séparateur.
#      Passaient donc au travers : `.env` (TOKEN=…), YAML (token: …),
#      `.ini`, `.netrc`, une ligne de commande (--token …), un en-tête
#      Authorization — et surtout la paire JSON {"jeton": "…"}, parce que le
#      guillemet fermant de la CLÉ s'intercale entre le mot-clé et le « : ».
#      Or ce dépôt range précisément son jeton de bot dans un JSON à clé
#      « jeton » : il n'était vu que par un motif nommé, pas par le filet.
RE_AFFECTATION = re.compile(
    r"""(?ix)
    (?:^|[^A-Za-z0-9_])          # début de ligne ou séparateur
    [A-Za-z0-9_]{0,24}?          # un préfixe éventuel : DISCORD_ , SMTP_ …
    (secret|token|jeton|password|passwd|mot_de_passe|mdp|api_?key|cle_api|
     access_key|auth|bearer|webhook)
    [A-Za-z0-9_]*                # un suffixe éventuel : _KEY , orization …
    ["']?\s*(?:[:=]\s*|\s+)      # : ou = , ou une simple espace (.netrc)
    ["']?
    ([^\s"',;)\]}]{16,})         # la valeur, guillemets ou non
    """)

# LE SEUIL EST MESURÉ, PAS DÉCRÉTÉ. Sur un corpus de valeurs réelles du
# projet et de jetons de chaque famille :
#     valeur de configuration la plus désordonnée : 4,09
#         (« https://buymeacoffee.com/lepetitdan »)
#     jeton le plus ordonné                       : 4,62
#         (une clé Stripe)
# Le seuil se pose dans l'écart, avec de la marge des deux côtés. Le premier
# jet était à 3,6 et le banc l'a pris en faute : « AscensionFR_Compagnon »
# (3,69) et « docs/CONTRIBUER.md » (3,95) déclenchaient l'alerte.
ENTROPIE_MINIMALE = 4.3

# L'entropie seule reste fragile, donc une seconde condition, structurelle :
# un jeton mêle les casses ET des chiffres, ou bien il est long. Une chaîne
# hexadécimale — nos empreintes djb2 et MD5, dont le dépôt est plein — est
# structurellement plafonnée à 4,0 bits (16 symboles), donc écartée par le
# seuil lui-même : c'est ce qui évite de transformer nos rapports en champ
# de fausses alertes.
def _opaque(valeur):
    a_min = any(c.islower() for c in valeur)
    a_maj = any(c.isupper() for c in valeur)
    a_chiffre = any(c.isdigit() for c in valeur)
    return (a_min and a_maj and a_chiffre) or len(valeur) >= 32

# Ce qu'on ne balaye pas : le binaire, et nos propres outils de sécurité qui
# CITENT les motifs pour les reconnaître. Un balayeur qui se dénonce lui-même
# serait un faux rouge permanent.
BINAIRES = (".png", ".jpg", ".jpeg", ".gif", ".ico", ".exe", ".dll", ".zip",
            ".gz", ".mpq", ".dbc", ".blp", ".ttf", ".otf", ".wav", ".mp3",
            ".pyc", ".pdb", ".bin")
# Nos propres outils de sécurité, qui CITENT les motifs pour les reconnaître
# ou les éprouver. Ils ne sont d'aucune des listes publiées (ni SOURCES, ni le
# dépôt public), donc les écarter n'ouvre aucune porte — alors qu'un balayeur
# qui se dénonce lui-même serait un faux rouge permanent, et un faux rouge
# permanent finit par être désactivé.
# ⚠️ Comparés au CHEMIN RELATIF, pas au nom de base : exclure par nom seul
# aurait rendu muet n'importe quel « secrets_injectes.json » déposé n'importe
# où dans l'arbre public (trouvé à la relecture adversariale).
FICHIERS_DU_BALAYAGE = ("outils/secrets_publication.py",
                        "outils/secrets_injectes.json",
                        "outils/banc_secrets.py",
                        # banc_incident.py CITE la variable WEBHOOK_RAPPORTS
                        # dans son épreuve d'anonymisation (il ne porte
                        # jamais de valeur) — même statut que banc_secrets.py.
                        # Trouvé par le gate --arbre au programme 33.
                        "outils/banc_incident.py")


def est_du_balayage(chemin_relatif):
    """⚠️ Le chemin exact, mais pas seulement à la racine (programme 38) :
    l'archive de clôture range la chaîne sous « chaine/outils/… », où
    l'égalité stricte ne reconnaissait plus nos propres bancs — ils se
    dénonçaient eux-mêmes et le gate restait rouge sur de FAUX secrets.
    On accepte donc aussi le suffixe, qui reste ancré sur le dossier
    parent : « chaine/outils/banc_secrets.py » passe, mais un
    « banc_secrets.py » posé n'importe où ailleurs, non."""
    rel = chemin_relatif.replace("\\", "/")
    if any(rel.endswith("/" + f) for f in FICHIERS_DU_BALAYAGE):
        return True
    return rel in FICHIERS_DU_BALAYAGE or "outils/" + rel in FICHIERS_DU_BALAYAGE


def entropie(chaine):
    """Shannon, en bits par caractère. Une valeur de configuration
    (« utf-8 », « AscensionFR ») tourne autour de 2,5 ; un jeton dépasse 4."""
    if not chaine:
        return 0.0
    total = float(len(chaine))
    return -sum((n / total) * math.log(n / total, 2)
                for n in collections_compte(chaine).values())


def collections_compte(chaine):
    compte = {}
    for c in chaine:
        compte[c] = compte.get(c, 0) + 1
    return compte


def balayer_texte(nom, texte, noms_essai=None):
    """Renvoie [(motif, extrait_masqué, ligne)] — jamais le secret en clair.

    Le masquage n'est pas de la coquetterie : ce relevé finit dans des
    rapports, des journaux et des sorties de console qui, eux, se partagent.
    Un garde-fou de secret qui recrache le secret n'a rien gardé.

    `noms_essai` : liste de récolteurs injectée par le banc — le banc ne
    cite jamais un vrai nom (règle du FAUX_WEBHOOK)."""
    trouves = []
    for etiquette, motif in MOTIFS:
        for m in motif.finditer(texte):
            trouves.append((etiquette, masquer(m.group(0)),
                            texte.count("\n", 0, m.start()) + 1))
    # La famille dynamique des pseudos — la déclaration elle-même épargnée.
    # Ligne par ligne et DÉNUDÉE d'abord : « |cFFB5FFFFNom » n'a aucune
    # frontière de lettre (le F final du code couleur colle au pseudo) —
    # le piège des codes couleur collés, attrapé ici par l'épreuve du banc
    # avant de partir en production.
    noms = noms_essai if noms_essai is not None else noms_recolteurs()
    motif_n = motif_recolteurs(noms)
    if motif_n is not None \
            and os.path.basename(nom) != "noms_recolteurs.local.txt":
        for i, ligne_txt in enumerate(texte.split("\n"), 1):
            m = motif_n.search(RE_CODES_CLIENT.sub("", ligne_txt))
            if m:
                trouves.append(("nom de récolteur déclaré",
                                masquer(m.group(0)), i))
    for m in RE_AFFECTATION.finditer(texte):
        valeur = m.group(2)
        if entropie(valeur) >= ENTROPIE_MINIMALE and _opaque(valeur):
            trouves.append(("affectation à forte entropie (%s, %.1f bits)"
                            % (m.group(1), entropie(valeur)),
                            masquer(valeur),
                            texte.count("\n", 0, m.start()) + 1))
    # Un même secret peut répondre à deux motifs (l'URL complète et sa forme
    # nue) : on ne le compte qu'une fois par ligne et par extrait.
    vus, uniques = set(), []
    for etiquette, extrait, ligne in trouves:
        if (extrait, ligne) in vus:
            continue
        vus.add((extrait, ligne))
        uniques.append((etiquette, extrait, ligne))
    return uniques


def masquer(secret):
    """Assez pour reconnaître, pas assez pour s'en servir."""
    if len(secret) <= 12:
        return secret[:4] + "…"
    return "%s…%s (%d car.)" % (secret[:12], secret[-2:], len(secret))


def lisible(chemin):
    return not chemin.lower().endswith(BINAIRES)


def fichiers_du_camion(racine):
    """Ce que git ENVERRAIT vraiment depuis `racine` : les fichiers suivis,
    PLUS les non-suivis non-ignorés (qu'un « git add -A » embarquerait).
    Un fichier gitignoré n'est jamais dans le camion.

    Rend None si `racine` n'est pas un dépôt git (ou si git manque) —
    l'appelant retombe alors sur le balayage complet de l'arbre.

    NÉ AU PROGRAMME 36 (29/08/2026) : trois nuits de cloud jetées parce que
    le gate refusait un rapport de joueur GITIGNORÉ, refabriqué depuis
    Discord à chaque passage — un nom de récolteur dans un rapport est
    NORMAL (c'est du texte de jeu capturé) et ne voyage jamais. Le gate
    balayait le dossier de travail au lieu du chargement."""
    import subprocess
    if not os.path.isdir(os.path.join(racine, ".git")):
        return None
    sans_fenetre = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    fichiers = []
    for args in (["ls-files", "-z"],
                 ["ls-files", "-z", "--others", "--exclude-standard"]):
        r = subprocess.run(["git", "-C", racine] + args,
                           capture_output=True, creationflags=sans_fenetre)
        if r.returncode != 0:
            return None
        fichiers += [f for f in r.stdout.decode("utf-8", "replace")
                     .split("\0") if f]
    return sorted(set(fichiers))


def balayer_arbre(racine, ignorer_git=True, seulement_camion=False):
    """Balaye ce qui est lisible sous `racine`, quelle que soit
    l'extension — c'est le point même de ce contrôle.

    `seulement_camion=True` : ne balaie que ce que git enverrait (voir
    fichiers_du_camion) — le périmètre d'un gate de PUSH. Sans dépôt git,
    retombe bruyamment sur l'arbre complet."""
    if seulement_camion:
        cibles = fichiers_du_camion(racine)
        if cibles is not None:
            trouves = []
            for rel in cibles:
                chemin = os.path.join(racine, rel)
                if not os.path.isfile(chemin) or not lisible(chemin) \
                        or est_du_balayage(rel):
                    continue
                try:
                    with io.open(chemin, encoding="utf-8",
                                 errors="replace") as f:
                        texte = f.read()
                except (OSError, IOError):
                    continue
                for t in balayer_texte(rel, texte):
                    trouves.append((rel,) + t)
            return trouves
        print("  (pas un dépôt git : balayage de l'arbre COMPLET)")
    trouves = []
    for dossier, sous, fichiers in os.walk(racine):
        if ignorer_git:
            sous[:] = [d for d in sous if d != ".git"]
        for nom in sorted(fichiers):
            chemin = os.path.join(dossier, nom)
            rel = os.path.relpath(chemin, racine).replace("\\", "/")
            if not lisible(chemin) or est_du_balayage(rel):
                continue
            try:
                with io.open(chemin, encoding="utf-8", errors="replace") as f:
                    texte = f.read()
            except (OSError, IOError):
                continue
            for t in balayer_texte(rel, texte):
                trouves.append((rel,) + t)
    return trouves


# ---------------------------------------------------------------------------
# 2. LA DIFFÉRENCE DÉCLARÉE
# ---------------------------------------------------------------------------
def charger_declarations(chemin=None):
    chemin = chemin or DECLARATIONS
    if not os.path.exists(chemin):
        return {}
    with io.open(chemin, encoding="utf-8") as f:
        brut = json.load(f)
    return {k: v for k, v in brut.items() if not k.startswith("_")}


def _motif_affectation(nom):
    """`NOM = "…"` en début de ligne, guillemets simples ou doubles. Le reste
    de la ligne (un commentaire, souvent) est PRÉSERVÉ : la neutralisation
    doit être un remplacement de VALEUR, pas une réécriture de ligne.
    (L'ancienne neutralisation, faite à la main, avait dupliqué le
    commentaire de la ligne 71 — la trace est encore visible dans l'arbre
    publié d'aujourd'hui.)"""
    return re.compile(r"""(?m)^(\s*%s\s*=\s*)(["'])(?:\\.|(?!\2).)*\2"""
                      % re.escape(nom))


def neutraliser(texte, declarations_du_fichier):
    """Rend le texte tel qu'il DOIT être dans l'arbre public.

    Renvoie (texte_neutralisé, [griefs]). Un grief est une phrase à
    journaliser ET une raison de REFUSER — jamais un silence.

    ⚠️ LE DÉFAUT QUE CETTE VERSION CORRIGE (relecture adversariale). Le
    premier jet demandait seulement « existe-t-il AU MOINS une affectation
    de ce nom que je sache traiter ? ». Conséquence : sur
    `NOM = \"\"\"secret\"\"\"` le motif s'accrochait à la paire de guillemets
    VIDE, ne remplaçait rien, et l'outil annonçait fièrement « 1 secret
    neutralisé ». Même chose pour une concaténation implicite
    (`NOM = \"abc\" \"def\"`, seule la première moitié partait) ou pour une
    seconde affectation du même nom plus bas dans le fichier.
    On COMPTE donc maintenant : toute affectation de ce nom, quelle que soit
    sa forme, doit avoir été traitée. Une seule qui échappe = grief.
    """
    griefs = []
    for nom, regle in declarations_du_fichier.items():
        if nom.startswith("_"):
            continue
        toutes = len(re.findall(r"(?m)^\s*%s\s*=" % re.escape(nom), texte))
        if not toutes:
            griefs.append("« %s » est déclaré mais n'est affecté nulle part "
                          "dans le fichier privé (déclaration périmée ou "
                          "renommage)" % nom)
            continue
        neutre = regle.get("valeur_publique_attendue", "")
        texte = _motif_affectation(nom).sub(
            lambda m: "%s%s%s%s" % (m.group(1), m.group(2), neutre,
                                    m.group(2)), texte)

        # On ne COMPTE pas les substitutions tentées — on vérifie le
        # RÉSULTAT. Compter ne suffit pas : sur `NOM = \"\"\"secret\"\"\"` le
        # motif s'accroche à la paire de guillemets VIDE, la substitution
        # « réussit », et le secret est toujours là. Après neutralisation,
        # toute ligne qui affecte ce nom doit valoir EXACTEMENT la valeur
        # neutre, éventuellement suivie d'un commentaire. Tout le reste —
        # triple guillemets, concaténation implicite, f-string, appel de
        # fonction, seconde affectation plus bas — se dénonce ici.
        conforme = re.compile(r"""^\s*%s\s*=\s*(["'])%s\1\s*(?:#.*)?$"""
                              % (re.escape(nom), re.escape(neutre)))
        ouvre = re.compile(r"^\s*%s\s*=" % re.escape(nom))
        rebelles = [l for l in texte.splitlines()
                    if ouvre.match(l) and not conforme.match(l)]
        if rebelles:
            griefs.append(
                "« %s » : %d affectation(s) sur %d n'ont PAS pu être "
                "neutralisées — forme non gérée (triple guillemets, "
                "concaténation, f-string, valeur calculée). Première : %s"
                % (nom, len(rebelles), toutes, rebelles[0].strip()[:60]))
    return texte, griefs


def valeurs_publiques(texte, declarations_du_fichier):
    """Ce que l'arbre PUBLIÉ porte réellement pour chaque nom déclaré.
    Sert à dire « il vaut X alors qu'on attend Y », au lieu du simple
    « les fichiers diffèrent »."""
    lues = {}
    for nom in declarations_du_fichier:
        if nom.startswith("_"):
            continue
        m = re.search(r"""(?m)^\s*%s\s*=\s*(["'])((?:\\.|(?!\1).)*)\1"""
                      % re.escape(nom), texte)
        lues[nom] = m.group(2) if m else None
    return lues
