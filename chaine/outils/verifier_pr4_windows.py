# -*- coding: utf-8 -*-
r"""
La PR #4 (support Linux) fait-elle bouger WINDOWS ? (programme 15, 01/08/2026)

LE DANGER N'EST PAS QUE LINUX MARCHE MAL. C'est que Windows casse pour 274
personnes à cause d'un remaniement fait pour Linux — dans un exécutable non
signé qui se met à jour tout seul.

La PR remplace trois choses par un appel à `plateforme.py` :

  1. `CONFIG_DIR = os.path.join(os.environ.get("APPDATA", "."), "AscensionFR")`
     devient `plateforme.dossier_config("AscensionFR")` ;
  2. `os.startfile(x)` dans un `try/except OSError` devient `plateforme.lancer(x)` ;
  3. `_pistes_launcher()` gagne une passe 0 : `plateforme.pistes_jeu_linux()`.

Ce banc éprouve les trois, sous Windows, en comparant au comportement D'ORIGINE
recopié ici mot pour mot. Il ne juge pas Linux : il juge la non-régression.

⚠️ CE BANC N'EST PAS DANS LE BANC DE SANTÉ. Il porte sur du code qui n'est PAS
fusionné : il a besoin d'un arbre où la PR est appliquée. Tant que la décision
d'intégrer n'est pas prise, il se lance à la main.

Usage :
    python outils/verifier_pr4_windows.py --arbre <dossier compagnon de la PR>
"""
import io
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Pas de chemin par défaut : l'ancien pointait un dossier temporaire de la
# machine du mainteneur (parti avec le prog. 33) — l'arbre se donne par --arbre.

# Le comportement D'ORIGINE, recopié de compagnon.py AVANT la PR. C'est la
# référence : si la PR s'en écarte sous Windows, ce banc doit rougir.
def config_dir_origine():
    return os.path.join(os.environ.get("APPDATA", "."), "AscensionFR")


def arbre():
    for i, a in enumerate(sys.argv):
        if a == "--arbre" and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    print("usage : python outils/verifier_pr4_windows.py --arbre <dossier>")
    sys.exit(2)


def main():
    dossier = arbre()
    chemin = os.path.join(dossier, "plateforme.py")
    if not os.path.isfile(chemin):
        print("plateforme.py introuvable dans : %s" % dossier)
        print()
        print("Ce banc a besoin d'un arbre où la PR #4 est appliquée.")
        print("Pour le refabriquer :")
        print("  git clone <depot_github> <bac>")
        print("  cd <bac> && git fetch origin pull/4/head:pr4 && "
              "git checkout pr4")
        print("  python outils/verifier_pr4_windows.py --arbre <bac>\\compagnon")
        return 2

    sys.path.insert(0, dossier)
    import plateforme

    cas = []

    def noter(description, obtenu, attendu):
        cas.append((description, obtenu, attendu))

    print("arbre éprouvé : %s" % dossier)
    print("plateforme.py : %d lignes"
          % io.open(chemin, encoding="utf-8").read().count("\n"))
    print("sys.platform  : %s   (EST_WINDOWS = %s)"
          % (sys.platform, plateforme.EST_WINDOWS))
    print()

    if not plateforme.EST_WINDOWS:
        print("⚠ Ce banc n'a de sens QUE sous Windows. Rien n'est éprouvé ici.")
        return 2

    # ---- 1. LE DOSSIER DE CONFIGURATION -----------------------------------
    # Le cas normal : APPDATA est là. Le chemin doit être identique CARACTÈRE
    # POUR CARACTÈRE — pas « équivalent », identique : c'est là que vit la
    # configuration de 274 joueurs, et un chemin qui bouge, c'est une
    # configuration perdue.
    ancien_appdata = os.environ.get("APPDATA")
    noter("APPDATA présent : chemin identique au caractère près",
          plateforme.dossier_config("AscensionFR"), config_dir_origine())

    # Un APPDATA fabriqué, pour ne pas dépendre de cette machine. Hors de
    # C:\Users exprès : la famille « chemin personnel Windows » du gate
    # (programme 33) mordrait sur la fixture, et le test ne compare que des
    # chaînes — il n'a pas besoin de ressembler à un vrai profil.
    os.environ["APPDATA"] = r"C:\BancEssai\AppData\Roaming"
    noter("APPDATA forcé : chemin identique",
          plateforme.dossier_config("AscensionFR"), config_dir_origine())
    noter("APPDATA forcé : la valeur attendue, en clair",
          plateforme.dossier_config("AscensionFR"),
          r"C:\BancEssai\AppData\Roaming\AscensionFR")

    # ---- LE CAS QUI M'INTÉRESSE : APPDATA ABSENT --------------------------
    # L'ancien code se rabattait sur "." — donc un chemin RELATIF, qui suit le
    # dossier depuis lequel l'exe est lancé. La PR se rabat sur le dossier
    # personnel. C'est un CHANGEMENT de comportement sous Windows, et ce banc
    # est là pour qu'il ne passe pas inaperçu.
    del os.environ["APPDATA"]
    origine_sans = config_dir_origine()
    pr_sans = plateforme.dossier_config("AscensionFR")
    noter("APPDATA absent : l'ancien code rendait un chemin RELATIF",
          origine_sans, os.path.join(".", "AscensionFR"))
    noter("APPDATA absent : la PR rend le dossier personnel",
          pr_sans, os.path.join(os.path.expanduser("~"), "AscensionFR"))
    # ⚠️ PAS une assertion — un SIGNALEMENT. La première version de ce banc
    # affirmait « les deux doivent différer » : elle serait passée au rouge le
    # jour où quelqu'un corrigerait la divergence. Une assertion qui interdit
    # la correction du défaut qu'elle signale est pire qu'inutile. On épingle
    # donc les deux valeurs (ci-dessus, elles mordent si l'une dérive) et on
    # laisse l'arbitrage à Dan.
    divergence = (origine_sans != pr_sans)

    # APPDATA vide — un cas qu'on n'attend pas, et c'est pour ça qu'on le teste.
    os.environ["APPDATA"] = ""
    noter("APPDATA vide : l'ancien code rendait « AscensionFR » tout court",
          config_dir_origine(), "AscensionFR")
    noter("APPDATA vide : la PR rend le dossier personnel",
          plateforme.dossier_config("AscensionFR"),
          os.path.join(os.path.expanduser("~"), "AscensionFR"))

    if ancien_appdata is None:
        os.environ.pop("APPDATA", None)
    else:
        os.environ["APPDATA"] = ancien_appdata

    # ---- 2. LE LANCEMENT ---------------------------------------------------
    # Sous Windows, `plateforme.lancer` doit faire EXACTEMENT `os.startfile`,
    # avec le même argument, et se comporter pareil quand ça échoue.
    appels = []

    def faux_startfile(p):
        appels.append(p)

    vrai = os.startfile
    os.startfile = faux_startfile
    try:
        cible = r"C:\Jeux\Ascension\Ascension Launcher.exe"
        rendu = plateforme.lancer(cible, None)
        noter("lancer() : un seul appel à os.startfile", len(appels), 1)
        noter("lancer() : le MÊME argument, inchangé",
              appels[0] if appels else None, cible)
        noter("lancer() : rend True quand ça part", rendu, True)

        # L'échec : l'ancien code faisait `except OSError: pass` puis passait
        # au candidat suivant. La PR doit rendre False pour le même effet.
        def startfile_qui_echoue(p):
            raise OSError("accès refusé")

        os.startfile = startfile_qui_echoue
        noter("lancer() : rend False sur OSError (au lieu de propager)",
              plateforme.lancer(cible, None), False)

        # Un prefixe passé sous Windows ne doit RIEN changer.
        appels[:] = []
        os.startfile = faux_startfile
        plateforme.lancer(cible, r"C:\un\prefixe\quelconque")
        # `list(...)` et pas `appels` : `noter` garde une RÉFÉRENCE, et le bloc
        # suivant réutilise la même liste. Sans la copie, cette assertion se
        # faisait polluer par des appels postérieurs et rougissait à tort.
        noter("lancer() : le prefixe est ignoré sous Windows",
              list(appels), [cible])
    finally:
        os.startfile = vrai

    # ---- 2 bis. LE SEUL subprocess DU MODULE EST-IL ATTEIGNABLE ? ---------
    #
    # C'est LA question de chaîne d'approvisionnement. `plateforme.py` partira
    # dans l'exe Windows des 274 joueurs même s'il n'y sert à rien : il faut
    # donc prouver que son unique `subprocess.Popen` ne peut PAS s'y déclencher.
    # Sous Windows, `lancer()` sort sur `os.startfile` avant d'atteindre
    # `_essayer` — on le montre en comptant les lancements de processus.
    import subprocess as _sp
    lancements = []
    vrai_popen = _sp.Popen

    def popen_espion(*a, **k):
        lancements.append(a[0] if a else k.get("args"))
        raise AssertionError("aucun processus ne doit être lancé sous Windows")

    _sp.Popen = popen_espion
    os.startfile = faux_startfile
    try:
        for cible_essai in (r"C:\Jeux\Ascension\Ascension.exe",
                            r"C:\Jeux\Ascension\LISEZ-MOI.txt",
                            r"C:\Jeux\Ascension"):
            try:
                plateforme.lancer(cible_essai, r"C:\un\prefixe")
            except Exception:
                pass
    finally:
        _sp.Popen = vrai_popen
        os.startfile = vrai
    noter("aucun processus lancé sous Windows (le subprocess est hors "
          "d'atteinte)", lancements, [])

    # ---- 3. LA DÉTECTION DU JEU -------------------------------------------
    #
    # ⚠️ « rend une liste vide » NE SUFFIT PAS, et je l'ai découvert en cassant
    # exprès : quand on retire la garde `if not EST_LINUX`, la fonction tourne
    # quand même et rend TOUJOURS une liste vide — parce que `~/Games`,
    # `~/.config/faugus-launcher/…` n'existent pas sur cette machine. Mon
    # assertion était donc satisfaite pour la mauvaise raison : elle ne
    # distinguait pas « inerte par conception » de « vide par chance ».
    #
    # Et ce n'est pas théorique : un joueur Windows qui aurait un dossier
    # « Games\quelquechose\drive_c » sous son profil ferait mordre le
    # balayage.
    #
    # On prouve donc l'INERTIE, pas le résultat : sous Windows, la fonction ne
    # doit toucher AUCUN fichier. On compte les accès au disque.
    acces = []
    vrais = {"isdir": os.path.isdir, "isfile": os.path.isfile,
             "listdir": os.listdir}

    def espion(nom, vrai):
        def piege(chemin, *a, **k):
            acces.append((nom, chemin))
            return vrai(chemin, *a, **k)
        return piege

    os.path.isdir = espion("isdir", vrais["isdir"])
    os.path.isfile = espion("isfile", vrais["isfile"])
    os.listdir = espion("listdir", vrais["listdir"])
    try:
        resultat = plateforme.pistes_jeu_linux()
        acces_pistes = list(acces)
        acces[:] = []
        prefixe = plateforme.prefixe_de(r"C:\Jeux\Ascension")
        acces_prefixe = list(acces)
    finally:
        os.path.isdir = vrais["isdir"]
        os.path.isfile = vrais["isfile"]
        os.listdir = vrais["listdir"]

    noter("pistes_jeu_linux() rend une liste VIDE sous Windows", resultat, [])
    noter("pistes_jeu_linux() ne touche AUCUN fichier (inerte, pas chanceuse)",
          len(acces_pistes), 0)
    noter("prefixe_de() rend None sous Windows", prefixe, None)
    noter("prefixe_de() ne touche AUCUN fichier",
          len(acces_prefixe), 0)

    # La passe 0 de la PR est `pistes.extend(plateforme.pistes_jeu_linux())`.
    # Avec une liste vide, elle ne peut ni changer l'ORDRE ni le CONTENU : on
    # le montre plutôt que de l'affirmer.
    temoin = ["A", "B", "C"]
    copie = list(temoin)
    copie.extend(plateforme.pistes_jeu_linux())
    noter("la passe 0 ne change ni l'ordre ni le contenu", copie, temoin)

    echecs = 0
    for description, obtenu, attendu in cas:
        if obtenu == attendu:
            print("  ok      %-54s %s" % (description, obtenu))
        else:
            print("  ECHEC   %-54s obtenu %r / attendu %r"
                  % (description, obtenu, attendu))
            echecs += 1
    print()
    if divergence:
        print("  ⚠ UN SEUL COMPORTEMENT WINDOWS CHANGE, et il est cerné :")
        print("      quand APPDATA est ABSENT ou VIDE, la configuration ne va")
        print("      plus dans « .\\AscensionFR » (relatif au dossier de")
        print("      lancement) mais dans « %s »."
              % os.path.join(os.path.expanduser("~"), "AscensionFR"))
        print("      Sur une machine Windows saine, APPDATA est toujours posé :")
        print("      ce cas ne concerne qu'un environnement abîmé. Le nouveau")
        print("      comportement est plus sain — mais c'est un CHANGEMENT, et")
        print("      un joueur dans ce cas retrouverait une config vierge.")
        print("      Ce n'est pas à moi de trancher.")
        print()
    print("%d échec(s)" % echecs)
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
