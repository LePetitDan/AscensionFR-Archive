# -*- coding: utf-8 -*-
"""Banc de NON-RÉGRESSION Windows — programme 23 (02/08/2026).

C'est le côté où il y a 274 personnes. Tout ce que le programme 23 a touché
pour réparer Linux doit se comporter **exactement comme avant** sous Windows,
et « exactement » veut dire : comparé à la version d'AVANT, pas à un souvenir.

MÉTHODE. Le banc charge la version d'origine des deux fichiers depuis
l'historique git (`git show HEAD:…`) sous un autre nom, puis fait tourner les
DEUX côte à côte et compare les résultats.

⚠️ Il ne lance JAMAIS le jeu : `os.startfile` est remplacé par un mouchard qui
   note l'appel au lieu de l'exécuter. Un banc qui démarre WoW n'est pas un
   banc.

Usage : python outils/banc_windows_non_regression.py
"""
import importlib.util
import io
import os
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ICI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(ICI)
COMPAGNON = os.path.join(BASE, "compagnon")
sys.path.insert(0, COMPAGNON)

import compagnon as logique              # noqa: E402
import interface_hub                     # noqa: E402

ECHECS = []
AVEC_FENETRE = "--sans-fenetre" not in sys.argv

# Sous pythonw.exe (sans console), démarrer git force Windows à ouvrir une
# fenêtre noire, qui vole le focus et éjecte d'un jeu en plein écran.
# capture_output redirige les FLUX, pas la FENÊTRE. getattr : la constante
# n'existe que sur Windows ; ailleurs 0, que subprocess accepte partout
# (il ne refuse creationflags que si la valeur est NON NULLE).
SANS_FENETRE = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def affirmer(condition, quoi):
    if not condition:
        ECHECS.append(quoi)
    print("   %s %s" % ("OK  " if condition else "RATÉ", quoi))


def charger_origine(nom_fichier, nom_module):
    """La version d'AVANT, telle qu'elle est dans git, chargée en parallèle."""
    rel = "compagnon/" + nom_fichier
    source = subprocess.run(["git", "show", "HEAD:" + rel], cwd=BASE,
                            capture_output=True, text=True,
                            encoding="utf-8",
                            creationflags=SANS_FENETRE).stdout
    if not source:
        return None
    dossier = tempfile.mkdtemp(prefix="afr_origine_")
    chemin = os.path.join(dossier, nom_module + ".py")
    io.open(chemin, "w", encoding="utf-8").write(source)
    spec = importlib.util.spec_from_file_location(nom_module, chemin)
    module = importlib.util.module_from_spec(spec)
    sys.modules[nom_module] = module
    spec.loader.exec_module(module)
    return module


class FauxHub:
    """Juste ce que lit `lancer_jeu` : un dossier de jeu et une barre d'état."""

    def __init__(self, jeu=None):
        self.jeu = jeu
        self.messages = []

    def statut(self, ton, texte):
        self.messages.append((ton, texte))


print("=" * 72)
print("BANC DE NON-RÉGRESSION WINDOWS — programme 23")
print("=" * 72)
print("système : os.name = %r" % os.name)
if os.name != "nt":
    print("Ce banc n'a de sens que sous Windows.")
    sys.exit(1)

origine = charger_origine("interface_hub.py", "interface_hub_origine")

# --------------------------------------------------------------------------- #
print("\n>> 1. « Lancer le jeu » — la lecture du registre est INCHANGÉE")
avant = origine._candidats_registre() if origine else None
apres = interface_hub._candidats_registre()
affirmer(origine is not None, "la version d'avant a pu être chargée")
affirmer(avant == apres,
         "mêmes candidats qu'avant : %d entrée(s), listes identiques"
         % len(apres))
print("      (%s)" % (apres or "aucun launcher déclaré dans le registre ici"))

# --------------------------------------------------------------------------- #
print("\n>> 2. « Lancer le jeu » — le MÊME fichier serait lancé qu'avant")
lances = []
vrai_startfile = os.startfile
os.startfile = lambda chemin, *a, **k: lances.append(chemin)   # mouchard
try:
    # Un faux dossier de jeu, avec un launcher deux dossiers au-dessus :
    # <base>/resources/ascension-live, exactement la forme réelle.
    racine = tempfile.mkdtemp(prefix="afr_jeu_")
    jeu = os.path.join(racine, "resources", "ascension-live")
    os.makedirs(jeu)
    io.open(os.path.join(racine, "Ascension Launcher.exe"),
            "w").write("MZ")
    io.open(os.path.join(jeu, "Ascension.exe"), "w").write("MZ")

    def jouer(dossier_jeu):
        """Fait jouer le MÊME scénario aux deux versions, et rend leurs
        résultats. Identifiants ASCII : « après » en nom de variable est un
        piège qu'on a déjà payé ailleurs."""
        sortie = {}
        for module, etiquette in ((origine, "avant"),
                                  (interface_hub, "apres")):
            lances.clear()
            faux = FauxHub(dossier_jeu)
            module.Hub.lancer_jeu(faux)
            sortie[etiquette] = (list(lances), list(faux.messages))
        return sortie

    r = jouer(jeu)
    affirmer(r["avant"][0] == r["apres"][0],
             "même fichier lancé : %s" % os.path.basename(
                 r["apres"][0][0] if r["apres"][0] else "aucun"))
    affirmer(r["avant"][1] == r["apres"][1],
             "même message affiché : « %s »"
             % (r["apres"][1][0][1] if r["apres"][1] else ""))

    # Le chemin de secours : pas de launcher, mais l'exe du jeu.
    os.remove(os.path.join(racine, "Ascension Launcher.exe"))
    s = jouer(jeu)
    affirmer(s["avant"] == s["apres"],
             "chemin de secours identique (« %s »)"
             % (s["apres"][1][0][1][:46] if s["apres"][1] else ""))

    # Et le cas où il n'y a rien du tout.
    n = jouer(None)
    affirmer(n["avant"] == n["apres"],
             "cas « rien trouvé » identique (« %s »)"
             % (n["apres"][1][0][1][:46] if n["apres"][1] else ""))
finally:
    os.startfile = vrai_startfile
affirmer(not lances or all(str(c).endswith(".exe") for c in lances),
         "le jeu n'a JAMAIS été lancé pour de vrai (mouchard seul)")

# --------------------------------------------------------------------------- #
print("\n>> 3. « Vérifier mon installation » — le grab est IMMÉDIAT comme avant")
if not AVEC_FENETRE:
    print("   (--sans-fenetre : non éprouvé)")
else:
    import tkinter as tk

    class Parent(tk.Tk):
        FOND_F, BORD_F = "#efe2c0", "#8a6a2a"

    racine = Parent()
    racine.geometry("300x200+80+80")
    racine.update()
    f = interface_hub.Hub._fenetre(racine, "Contrôle d'installation", 700, 480)
    racine.update()
    # `grab_current()` rend la fenêtre qui tient le grab. S'il avait fallu
    # attendre, elle serait encore None à cet instant : la mesure prouve donc
    # que le chemin Windows n'est PAS passé par la reprise différée.
    tenu = f.grab_current()
    affirmer(tenu is not None, "le grab est pris DÈS le retour de _fenetre()")
    affirmer(str(tenu) == str(f), "et c'est bien la fenêtre fille qui le tient")
    affirmer(bool(f.winfo_exists()), "la fenêtre existe")
    f.destroy()
    racine.destroy()

# --------------------------------------------------------------------------- #
print("\n>> 4. La fenêtre de plantage s'ouvre, et dit où c'est écrit")
if not AVEC_FENETRE:
    print("   (--sans-fenetre : non éprouvé)")
else:
    import tkinter as tk
    racine = tk.Tk()
    racine.geometry("200x100+60+60")
    racine.update()
    interface_hub._PLANTAGE_OUVERT = False
    trace = ("Traceback (most recent call last):\n"
             "  File \"interface_hub.py\", line 485, in _candidats_registre\n"
             "    import winreg\n"
             "ModuleNotFoundError: No module named 'winreg'\n")
    interface_hub.montrer_plantage(racine, "Lancer le jeu", trace)
    racine.update()
    filles = [w for w in racine.winfo_children()
              if isinstance(w, tk.Toplevel)]
    affirmer(len(filles) == 1, "une fenêtre de plantage est apparue")
    if filles:
        fen = filles[0]
        affirmer("raté" in fen.title().lower(),
                 "son titre parle français : « %s »" % fen.title())
        textes = []
        pile = [fen]
        while pile:
            w = pile.pop()
            if isinstance(w, tk.Label):
                textes.append(w.cget("text"))
            if isinstance(w, tk.Text):
                textes.append(w.get("1.0", "end"))
            pile.extend(w.winfo_children())
        tout = "\n".join(textes)
        affirmer("Lancer le jeu" in tout, "elle NOMME le geste du joueur")
        affirmer(logique.FICHIER_INCIDENT in tout,
                 "elle donne le chemin du fichier de trace")
        affirmer("ModuleNotFoundError" in tout,
                 "le détail technique est copiable dedans")
        affirmer("pas de ta faute" in tout,
                 "elle rassure le joueur en français simple")
    # Une seconde panne ne doit PAS empiler une seconde fenêtre.
    interface_hub.montrer_plantage(racine, "Lancer le jeu", trace)
    racine.update()
    filles2 = [w for w in racine.winfo_children()
               if isinstance(w, tk.Toplevel)]
    affirmer(len(filles2) == 1,
             "une boucle de plantages n'empile pas les fenêtres")
    interface_hub._PLANTAGE_OUVERT = False
    racine.destroy()

# --------------------------------------------------------------------------- #
print("\n>> 5. Le reste de l'interface n'a pas bougé")
import json                                            # noqa: E402
m = json.load(io.open(os.path.join(COMPAGNON, "assets", "hub",
                                   "decor_hub.json"), encoding="utf-8"))
affirmer("btn_copier" in m, "le décor du nouveau bouton est au manifeste")
affirmer(m["btn_envoyer"] == {"w": 300, "h": 44, "pad": 0},
         "le bouton d'envoi garde ses cotes")
M = interface_hub.METRIQUE
cx, y = M["CX"], 96
haut_b, bas_b = y + 220, y + 220 + M["BTN_M_H"]
etat = y + 220 + M["BTN_M_H"] + 22
case = y + 220 + M["BTN_M_H"] + 58 - 13
bas_panneau = y + M["PAN_LETTRE_H"]
affirmer(bas_b < etat - 8, "le compteur ne touche pas les boutons")
affirmer(etat + 8 < case, "la case ne touche pas le compteur")
affirmer(case + m["case_vide"]["h"] < bas_panneau,
         "la case reste DANS le panneau (%d px de marge)"
         % (bas_panneau - case - m["case_vide"]["h"]))
affirmer(cx + 34 + M["BTN_M_W"] + 20 + m["btn_copier"]["w"] <= cx + M["CW"],
         "les deux boutons tiennent dans la colonne")

print("\n" + "=" * 72)
if ECHECS:
    print("%d ÉCHEC(S) :" % len(ECHECS))
    for e in ECHECS:
        print("  - %s" % e)
    sys.exit(1)
print("Windows n'a pas bougé.")
