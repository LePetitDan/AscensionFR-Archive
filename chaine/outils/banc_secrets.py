# -*- coding: utf-8 -*-
r"""BANC DES GARDE-FOUS DE SECRET (programme 6, 29/07/2026).

Un garde-fou qu'on n'a pas vu REFUSER n'est pas un garde-fou : c'est une
intention. Celui-ci fabrique les situations dangereuses une par une, sur des
arbres jetables, et vérifie que la barrière mord — y compris dans les cas
tordus où elle pourrait se croire satisfaite.

Le cas n° 3 est celui qui compte le plus. Un garde-fou naïf dirait « la
valeur publique est différente du secret, donc c'est bon ». Non : elle doit
être ÉGALE à la valeur neutre déclarée. « REDACTED », « à remplir » ou un
webhook de test sont tous « différents du secret » et tous inacceptables —
le premier parce qu'il ment sur ce que fait le code, le dernier parce qu'il
est encore un secret.

Usage : python outils/banc_secrets.py
Code de sortie : 0 si toutes les épreuves passent, 1 sinon.
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from secrets_publication import (balayer_texte, neutraliser,  # noqa: E402
                                 valeurs_publiques, entropie)

# Ce banc est lancé par banc_sante.py, lui-même sous pythonw.exe (sans console)
# via la tâche planifiée de 19 h 15. Un processus sans console qui démarre git
# force Windows à ouvrir une fenêtre noire, qui vole le focus et éjecte d'un jeu
# en plein écran. capture_output redirige les FLUX, pas la FENÊTRE.
# getattr : la constante n'existe que sur Windows ; ailleurs 0, que subprocess
# accepte partout (il ne refuse creationflags que si la valeur est NON NULLE).
SANS_FENETRE = getattr(subprocess, "CREATE_NO_WINDOW", 0)

# Un faux webhook, de la bonne FORME mais sans valeur : le banc ne doit
# jamais manipuler le vrai. (Motif reconnu, chiffres inventés.)
FAUX_WEBHOOK = ("https://discord.com/api/webhooks/1234567890123456789/"
                "AbCdEfGhIjKlMnOpQrStUvWxYz0123456789-_AbCdEfGhIjKlMnOpQrSt")

REGLES = {"WEBHOOK_RAPPORTS": {"valeur_publique_attendue": ""}}

epreuves = []


def epreuve(nom):
    def enrobe(f):
        epreuves.append((nom, f))
        return f
    return enrobe


# --- le balayage, sur des formes variées ----------------------------------
@epreuve("le webhook est vu dans un .py (l'extension que le zip sautait)")
def _():
    return len(balayer_texte("compagnon.py",
                             'WEBHOOK = "%s"' % FAUX_WEBHOOK)) > 0


@epreuve("le webhook est vu dans un .json, un .md, un .yml, un sans-extension")
def _():
    for nom in ("config.json", "LISEZMOI.md", "ci.yml", "Dockerfile"):
        if not balayer_texte(nom, "url: %s" % FAUX_WEBHOOK):
            return False
    return True


@epreuve("le webhook est vu même coupé de son https://")
def _():
    nu = FAUX_WEBHOOK.replace("https://", "")
    return len(balayer_texte("x.py", 'U = "%s"' % nu)) > 0


# ⚠️ Les faux jetons ci-dessous sont écrits en DEUX MORCEAUX
# concaténés : à l'exécution la chaîne est identique, mais les
# scanners de secrets (celui de GitHub comme le nôtre) ne la
# reconnaissent plus comme un jeton. Sans cela, la publication de
# l'archive était refusée par la protection de GitHub — qui faisait
# son travail : elle ne peut pas savoir qu'un secret est faux.
@epreuve("les jetons GitHub / Google / Slack / AWS / Stripe sont vus")
def _():
    cas = ["ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8",
           "github_pat_" + "11ABCDEFG0aBcDeFgHiJkL_" + "x" * 40,
           "AIza" + "SyD-1234567890abcdefghijklmnopqrstu",
           "xoxb-" + "123456789012-1234567890123-AbCdEfGhIjKlMnOpQrStUvWx",
           "AKIA" + "IOSFODNN7EXAMPLE",
           "sk_live_" + "4eC39HqLyjWDarjtT1zdp7dc"]
    manques = [c[:10] for c in cas if not balayer_texte("x.txt", "k = " + c)]
    if manques:
        print("      motifs non reconnus :", manques)
    return not manques


@epreuve("un chemin personnel Windows est vu, les profils système épargnés")
def _():
    # Famille née au programme 33 : deux outils portaient en dur un dossier
    # temporaire du mainteneur (C:\Users\<nom>\AppData\...) et le gate ne
    # les voyait pas. Le nom est INVENTÉ — le banc ne cite jamais le vrai.
    vu = balayer_texte("outil.py",
                       r'SORTIE = r"C:\Users\Quelquun\AppData\Temp\x.json"')
    systeme = balayer_texte("outil.py", r'P = r"C:\Users\Public\Documents"')
    return bool(vu) and not systeme


@epreuve("un nom de récolteur déclaré est vu, la déclaration épargnée")
def _():
    # Famille née au programme 34 : une liste de repli EN DUR était partie
    # dans le dépôt cloud. Le nom est INVENTÉ (règle du FAUX_WEBHOOK), et
    # on éprouve les trois faces : le nom dans du code, le nom COLLÉ à un
    # code couleur (piège sans frontière de mot), et le fichier de
    # déclaration lui-même qui doit rester épargné.
    noms = ["Exemplard"]
    dans_code = balayer_texte("outil.py", 'NOMS = ["Exemplard"]',
                              noms_essai=noms)
    colle = balayer_texte("DB_X.lua", 'T["|cFFB5FFFFExemplard"]="y"',
                          noms_essai=noms)
    declaration = balayer_texte("noms_recolteurs.local.txt",
                                "Exemplard\n", noms_essai=noms)
    prefixe = balayer_texte("x.txt", "Exemplardise du texte de jeu",
                            noms_essai=noms)
    return (bool(dans_code) and bool(colle)
            and not declaration and not prefixe)


@epreuve("une clé privée est vue sous SES CINQ en-têtes")
def _():
    # Le motif ne connaissait que RSA/EC/DSA/OPENSSH/PGP suivis d'une espace.
    entetes = ["-----BEGIN PRIVATE KEY-----",
               "-----BEGIN RSA PRIVATE KEY-----",
               "-----BEGIN OPENSSH PRIVATE KEY-----",
               "-----BEGIN ENCRYPTED PRIVATE KEY-----",
               "-----BEGIN PGP PRIVATE KEY BLOCK-----"]
    manques = [e for e in entetes if not balayer_texte("id_rsa", e + "\nabc\n")]
    if manques:
        print("      en-têtes non reconnus :", manques)
    return not manques


# --- LES TROUS TROUVÉS PAR LA RELECTURE ADVERSARIALE ----------------------
# Chacun a été REPRODUIT avant d'être corrigé. Ils restent ici pour qu'une
# régression future les fasse ressortir au lieu de repasser inaperçus.
VALEUR = "aZ7qK2mR9tX4pL8vB3nH6wS1yD5gJ0fC"      # 32 car., entropie 5,0


@epreuve("🛑 le mot-clé n'a pas à OUVRIR le nom (DISCORD_TOKEN, SMTP_PASSWORD)")
def _():
    # Le piège des codes collés, revenu par la fenêtre : dans DISCORD_TOKEN,
    # « \b » ne voit aucune frontière après le souligné.
    noms = ["DISCORD_TOKEN", "BOT_TOKEN", "SMTP_PASSWORD", "GITHUB_TOKEN",
            "CLIENT_SECRET", "aws_secret_access_key", "ANTHROPIC_API_KEY",
            "DB_PASSWORD", "mon_jeton", "url_webhook", "MDP_SMTP"]
    rates = [n for n in noms
             if not balayer_texte("x.py", '%s = "%s"' % (n, VALEUR))]
    if rates:
        print("      noms encore invisibles :", rates)
    return not rates


@epreuve("🛑 la valeur n'a pas à être entre guillemets ni collée (.env, YAML, JSON)")
def _():
    formes = ['{"jeton": "%s"}' % VALEUR,          # paire JSON
              "TOKEN=%s" % VALEUR,                  # .env
              "token: %s" % VALEUR,                 # YAML
              "token = %s" % VALEUR,                # .ini
              "export API_KEY=%s" % VALEUR,         # shell
              "--token %s" % VALEUR,                # ligne de commande
              "machine x login y password %s" % VALEUR]   # .netrc
    rates = [f[:28] for f in formes if not balayer_texte("conf", f)]
    if rates:
        print("      formes encore invisibles :", rates)
    return not rates


@epreuve("🛑 les clés de modèles (sk-ant-, sk-proj-) sont vues")
def _():
    cles = ["sk-ant-api03-" + "Rk7dQm2xVp9LzT4hN6bW8sJc1yF5gA0eU3iO7rXkM2vB",
            "sk-proj-" + "aB3dE5fG7hJ9kL1mN3pQ5rS7tU9vW1xY3zA5bC7dE9fG"]
    return all(balayer_texte("x.py", "k = " + c) for c in cles)


@epreuve("les jetons Slack app / SendGrid / npm / Telegram / JWT sont vus")
def _():
    cas = ["xapp-1-" + "A01BCDEFGHI-1234567890123-abcdef0123456789",
           "SG." + "aBcDeFgHiJkLmNoP.qRsTuVwXyZ0123456789abcdefghij",
           "npm_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8",
           "1234567890:AA" + "GhIjKlMnOpQrStUvWxYz0123456789abcdE",
           "eyJhbGciOiJIUzI1NiJ9." + "eyJzdWIiOiIxMjM0NTY3ODkwIn0."
           "dQw4w9WgXcQabcdefghij"]
    manques = [c[:12] for c in cas if not balayer_texte("x.txt", "k = " + c)]
    if manques:
        print("      non reconnus :", manques)
    return not manques


@epreuve("une URL à mot de passe SANS nom d'utilisateur est vue")
def _():
    return len(balayer_texte("conf.ini",
                             "db = postgres://:motdepasse123@srv/base")) > 0


@epreuve("🛑 une affectation en TRIPLE GUILLEMETS n'est pas neutralisée en silence")
def _():
    texte = 'WEBHOOK_RAPPORTS = """%s"""\n' % FAUX_WEBHOOK
    neutre, griefs = neutraliser(texte, REGLES)
    # Le premier jet renvoyait griefs=[] et un texte INCHANGÉ, en annonçant
    # « 1 secret neutralisé ». Il faut un grief, donc un refus.
    return bool(griefs) and (FAUX_WEBHOOK not in neutre or bool(griefs))


@epreuve("🛑 une CONCATÉNATION implicite ne passe pas pour neutralisée")
def _():
    texte = 'WEBHOOK_RAPPORTS = "%s" "%s"\n' % (FAUX_WEBHOOK[:40],
                                                FAUX_WEBHOOK[40:])
    _neutre, griefs = neutraliser(texte, REGLES)
    return bool(griefs)


@epreuve("🛑 une SECONDE affectation du même nom est comptée, pas oubliée")
def _():
    texte = ('WEBHOOK_RAPPORTS = ""\n'
             'def f():\n    return 1\n'
             'WEBHOOK_RAPPORTS = """%s"""\n' % FAUX_WEBHOOK)
    _neutre, griefs = neutraliser(texte, REGLES)
    return bool(griefs)


@epreuve("l'exclusion du balayage porte sur le CHEMIN, pas sur le nom de base")
def _():
    from secrets_publication import est_du_balayage
    return (est_du_balayage("outils/secrets_publication.py")
            and not est_du_balayage("depot_github/docs/secrets_injectes.json")
            and not est_du_balayage("compagnon/assets/banc_secrets.py"))


@epreuve("une URL à identifiants est vue")
def _():
    return len(balayer_texte(
        "conf.ini", "db = postgres://dan:motdepasse123@srv.exemple/base")) > 0


@epreuve("le secret n'est JAMAIS rendu en clair dans le relevé")
def _():
    for _e, extrait, _l in balayer_texte("x.py", 'W = "%s"' % FAUX_WEBHOOK):
        if FAUX_WEBHOOK in extrait or FAUX_WEBHOOK[20:40] in extrait:
            return False
    return True


@epreuve("PAS de fausse alerte sur des valeurs de configuration ordinaires")
def _():
    innocents = [
        'ENCODAGE = "utf-8"',
        'TOKEN_SEPARATEUR = "----------------"',
        'API_KEY_NOM = "AscensionFR_Compagnon"',
        'auth = "none"',
        'password_label = "Mot de passe oublié ?"',
        'SECRET_DOC = "docs/CONTRIBUER.md"',
        'webhook_status = "désactivé (copie seulement)"',
        'jeton = "aaaaaaaaaaaaaaaaaaaaaaaa"',        # 24 car., entropie basse
    ]
    faux = [t for t in innocents if balayer_texte("x.py", t)]
    if faux:
        print("      fausses alertes :", faux)
    return not faux


@epreuve("l'entropie sépare bien un jeton d'une valeur de configuration")
def _():
    return (entropie(FAUX_WEBHOOK) > 4.0 > entropie("utf-8-sig")
            and entropie("AscensionFR_Compagnon") < 4.0)


# --- la différence déclarée ------------------------------------------------
PRIVE = ('# en-tête\nVERSION_COMPAGNON = "3.4.0"\n'
         'WEBHOOK_RAPPORTS = "%s"    # commentaire\n'
         'def f():\n    return 1\n' % FAUX_WEBHOOK)


@epreuve("la neutralisation remplace la valeur et PRÉSERVE le commentaire")
def _():
    neutre, manquants = neutraliser(PRIVE, REGLES)
    return (not manquants
            and 'WEBHOOK_RAPPORTS = ""    # commentaire' in neutre
            and neutre.count("# commentaire") == 1   # pas de duplication
            and FAUX_WEBHOOK not in neutre
            and 'VERSION_COMPAGNON = "3.4.0"' in neutre)


@epreuve("un nom déclaré mais absent du privé est SIGNALÉ, pas ignoré")
def _():
    _n, griefs = neutraliser('X = "1"\n', REGLES)
    return len(griefs) == 1 and "WEBHOOK_RAPPORTS" in griefs[0]


@epreuve("🛑 une valeur publique DIFFÉRENTE mais pas neutre est refusée")
def _():
    # Le cœur du sujet : « différent du secret » ne suffit pas.
    for valeur in ("REDACTED", "à remplir", "xxx", FAUX_WEBHOOK):
        public = PRIVE.replace(FAUX_WEBHOOK, valeur)
        lues = valeurs_publiques(public, REGLES)
        if lues["WEBHOOK_RAPPORTS"] == "":
            return False                     # aurait été accepté à tort
    # et la vraie valeur neutre, elle, est bien reconnue
    neutre, _m = neutraliser(PRIVE, REGLES)
    return valeurs_publiques(neutre, REGLES)["WEBHOOK_RAPPORTS"] == ""


@epreuve("une divergence AILLEURS reste un refus (privé neutralisé ≠ public)")
def _():
    neutre, _m = neutraliser(PRIVE, REGLES)
    public = neutre.replace("return 1", "return 2")
    return neutre != public


@epreuve("le privé neutralisé est EXACTEMENT ce qu'on attend du public")
def _():
    neutre, _m = neutraliser(PRIVE, REGLES)
    return not balayer_texte("compagnon.py", neutre)


@epreuve("le gate ne juge que le CAMION : l'ignoré passe, le suivi mord")
def _():
    # Programme 36 : trois nuits jetées parce qu'un rapport GITIGNORÉ
    # portait un nom de récolteur. Le gate juge un push — l'ignoré n'a pas
    # à pouvoir le bloquer ; le suivi ET le non-suivi non-ignoré (add -A),
    # si. Éprouvé sur un dépôt éphémère, avec le FAUX webhook.
    dossier = tempfile.mkdtemp(prefix="banc_camion_")
    try:
        def g(*a):
            return subprocess.run(["git"] + list(a), cwd=dossier,
                                  capture_output=True,
                                  creationflags=SANS_FENETRE)
        g("init", "-q")
        g("config", "user.email", "banc@exemple")
        g("config", "user.name", "banc")
        io.open(os.path.join(dossier, ".gitignore"), "w",
                encoding="utf-8").write("rapports/\n")
        os.makedirs(os.path.join(dossier, "rapports"))
        io.open(os.path.join(dossier, "rapports", "auto_x.txt"), "w",
                encoding="utf-8").write('vu en jeu : %s\n' % FAUX_WEBHOOK)
        io.open(os.path.join(dossier, "suivi.py"), "w",
                encoding="utf-8").write('X = "propre"\n')
        g("add", "-A")
        g("commit", "-q", "-m", "propre")
        from secrets_publication import balayer_arbre
        # 1. le secret n'est QUE dans l'ignoré -> le camion est propre
        ignore_passe = not balayer_arbre(dossier, seulement_camion=True)
        # 2. le même secret dans un fichier SUIVI -> refus
        io.open(os.path.join(dossier, "suivi.py"), "w",
                encoding="utf-8").write('W = "%s"\n' % FAUX_WEBHOOK)
        suivi_mord = bool(balayer_arbre(dossier, seulement_camion=True))
        # 3. et dans un NON-SUIVI non-ignoré (add -A l'embarquerait) -> refus
        io.open(os.path.join(dossier, "suivi.py"), "w",
                encoding="utf-8").write('X = "propre"\n')
        io.open(os.path.join(dossier, "neuf.txt"), "w",
                encoding="utf-8").write(FAUX_WEBHOOK + "\n")
        neuf_mord = bool(balayer_arbre(dossier, seulement_camion=True))
        return ignore_passe and suivi_mord and neuf_mord
    finally:
        shutil.rmtree(dossier, ignore_errors=True)


# --- l'historique git ------------------------------------------------------
@epreuve("un secret RETIRÉ de l'arbre reste vu dans l'historique git")
def _():
    dossier = tempfile.mkdtemp(prefix="banc_secrets_")
    try:
        def g(*a):
            return subprocess.run(["git"] + list(a), cwd=dossier,
                                  capture_output=True,
                                  creationflags=SANS_FENETRE)
        g("init", "-q")
        g("config", "user.email", "banc@exemple")
        g("config", "user.name", "banc")
        cible = os.path.join(dossier, "conf.py")
        io.open(cible, "w", encoding="utf-8").write(
            'W = "%s"\n' % FAUX_WEBHOOK)
        g("add", "-A")
        g("commit", "-q", "-m", "avec le secret")
        io.open(cible, "w", encoding="utf-8").write('W = ""\n')
        g("add", "-A")
        g("commit", "-q", "-m", "secret retire")

        from balayer_secrets import balayer_historique
        from secrets_publication import balayer_arbre
        dans_arbre = balayer_arbre(dossier)
        dans_histoire, _lus = balayer_historique(dossier)
        # l'arbre est propre, l'historique ne l'est pas : c'est tout le point
        return not dans_arbre and dans_histoire
    finally:
        shutil.rmtree(dossier, ignore_errors=True)


def gater_arbre(racine):
    """LA CONDITION DU PUSH (programme 33, blocs 0 et C). Balaie un vrai
    arbre — celui qui est sur le point de partir — et REFUSE s'il porte un
    secret d'une des familles connues, .py COMPRIS (c'est le trou du
    programme 6 : construire_zip_release sautait les .py). balayer_arbre
    lit toute extension non binaire, donc les .py sont dedans.

    Code de sortie 0 = rien trouvé, on peut pousser ; 1 = un secret est là,
    on ne pousse pas. Le relevé est MASQUÉ (jamais le secret en clair)."""
    from secrets_publication import balayer_arbre, fichiers_du_camion
    print("=" * 70)
    print("BALAYAGE DE L'ARBRE À POUSSER : %s" % racine)
    print("=" * 70)
    if not os.path.isdir(racine):
        print("🛑 dossier introuvable : %s" % racine)
        return 1
    # LE PÉRIMÈTRE, C'EST LE CAMION (programme 36) : le gate juge un PUSH,
    # donc il balaie ce que git enverrait — les suivis + les non-suivis
    # non-ignorés (le « git add -A » du passage). Un gitignoré ne part
    # jamais : il n'a pas à pouvoir bloquer la livraison. Trois nuits de
    # cloud ont été jetées pour un rapport de joueur ignoré (27-29/08).
    camion = fichiers_du_camion(racine)
    if camion is not None:
        print("périmètre : %d fichier(s) que git enverrait (suivis + "
              "non-ignorés)" % len(camion))
    trouves = balayer_arbre(racine, seulement_camion=True)
    if not trouves:
        print("✅ aucun secret dans l'arbre — push autorisé.")
        return 0
    print("🛑 %d secret(s) trouvé(s) — PUSH REFUSÉ :" % len(trouves))
    for rel, etiquette, extrait, ligne in trouves:
        print("   %s:%d  [%s]  %s" % (rel, ligne, etiquette, extrait))
    return 1


def main():
    if "--arbre" in sys.argv:
        i = sys.argv.index("--arbre")
        if i + 1 >= len(sys.argv):
            print("usage : banc_secrets.py --arbre <dossier>")
            return 2
        return gater_arbre(sys.argv[i + 1])
    print("=" * 70)
    print("BANC DES GARDE-FOUS DE SECRET")
    print("=" * 70)
    echecs = 0
    for nom, f in epreuves:
        try:
            ok = bool(f())
        except Exception as exc:            # noqa: BLE001
            ok = False
            print("   (exception : %s)" % exc)
        print("  %s  %s" % ("ok    " if ok else "ÉCHEC ", nom))
        echecs += 0 if ok else 1
    print("=" * 70)
    if echecs:
        print("🛑 %d ÉPREUVE(S) EN ÉCHEC sur %d" % (echecs, len(epreuves)))
        return 1
    print("✅ %d épreuves, toutes passées." % len(epreuves))
    return 0


if __name__ == "__main__":
    sys.exit(main())
