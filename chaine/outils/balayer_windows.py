# -*- coding: utf-8 -*-
"""Balayage : tout ce qui suppose Windows, et si c'est gardé — programme 23.

POURQUOI UN OUTIL PLUTÔT QU'UNE LECTURE. Tetardtek a trouvé deux défauts en
cliquant sur deux boutons. La question n'était pas « répare ces deux-là », mais
« combien y en a-t-il ? ». Un compte à la main n'est pas reproductible et ne
mordra plus jamais ; celui-ci se relance après chaque retouche.

CE QU'IL SAIT FAIRE, ET C'EST LE POINT DÉLICAT. Il ne se contente pas de
trouver `os.startfile` : il remonte l'arbre syntaxique jusqu'à la racine du
fichier et regarde **quels `try/except` l'entourent réellement**, puis compare
le type d'exception attrapé au type qui serait levé hors Windows :

    import winreg          hors Windows -> ModuleNotFoundError (une ImportError)
    ctypes.windll.…        hors Windows -> AttributeError
    os.startfile(…)        hors Windows -> AttributeError
    creationflags=…        hors Windows -> ValueError

Un `except OSError` NE GARDE AUCUN des quatre. C'est exactement le défaut du
bouton « Lancer le jeu » : l'appel était dans un `try`, mais le mauvais.

Usage :
    python outils/balayer_windows.py                  (les fichiers du Hub)
    python outils/balayer_windows.py chemin/vers.py … (d'autres fichiers)
    python outils/balayer_windows.py --origine        (la version d'AVANT, via git)
"""
import ast
import io
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ICI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(ICI)
FICHIERS = [os.path.join(BASE, "compagnon", n)
            for n in ("interface_hub.py", "compagnon.py")]

# Sous pythonw.exe (sans console), démarrer git force Windows à ouvrir une
# fenêtre noire, qui vole le focus et éjecte d'un jeu en plein écran.
# capture_output redirige les FLUX, pas la FENÊTRE. getattr : la constante
# n'existe que sur Windows ; ailleurs 0, que subprocess accepte partout
# (il ne refuse creationflags que si la valeur est NON NULLE) — c'est
# précisément la nuance que la règle creationflags de ce balayeur manquait.
SANS_FENETRE = getattr(subprocess, "CREATE_NO_WINDOW", 0)

# --------------------------------------------------------------------------- #
# Les familles. Chaque entrée : (libellé, exception levée hors Windows).
# --------------------------------------------------------------------------- #
MODULES_WINDOWS = {"winreg", "msvcrt", "winsound", "_winapi", "win32api",
                   "win32con", "win32gui", "win32com", "pywintypes",
                   "winerror", "ntsecuritycon"}
ATTRIBUTS_OS = {"startfile"}                    # os.startfile
ATTRIBUTS_CTYPES = {"windll", "oledll", "WinDLL", "OleDLL", "WINFUNCTYPE",
                    "GetLastError", "WinError", "FormatError"}
# Pièges de fenêtre : ce qui marche sous Windows et pas forcément sous X11.
PIEGES_FENETRE = {
    "grab_set": "TclError « grab failed: window not viewable » si le "
                "gestionnaire X11 n'a pas encore affiché la fenêtre",
    "grab_set_global": "idem, en pire (X11 refuse souvent le grab global)",
    "iconbitmap": "TclError : X11 ne lit pas les .ico",
    "overrideredirect": "comportement très variable selon le gestionnaire",
}
# ⚠️ `attributes()` et `state()` ne sont PAS des pièges en soi : tout dépend de
# l'option demandée. Les signaler en bloc ferait crier au loup — et un
# balayage qui crie au loup finit désactivé (la leçon du programme 6). On ne
# retient donc que les options réellement Windows-seulement.
OPTIONS_FENETRE_WINDOWS = {"-toolwindow", "-disabled", "-transparentcolor",
                           "zoomed"}
# La molette : sous X11 c'est Button-4/5 et `delta` vaut 0.
SEQUENCES_MOLETTE = "<MouseWheel>"
# Variables d'environnement qui n'existent que sous Windows.
ENV_WINDOWS = {"APPDATA", "LOCALAPPDATA", "PROGRAMFILES", "PROGRAMFILES(X86)",
               "USERPROFILE", "SYSTEMROOT", "COMSPEC", "USERNAME", "TEMP",
               "TMP", "HOMEDRIVE", "HOMEPATH"}
# Commandes externes qui n'existent que sous Windows.
COMMANDES_WINDOWS = {"cmd", "cmd.exe", "tasklist", "taskkill", "reg",
                     "powershell", "wmic", "start", "attrib", "icacls"}

# Ce qu'un `except` doit contenir pour garder vraiment.
GARDES = {
    "ImportError": {"ImportError", "ModuleNotFoundError", "Exception",
                    "BaseException"},
    "AttributeError": {"AttributeError", "Exception", "BaseException"},
    "ValueError": {"ValueError", "Exception", "BaseException"},
    "TclError": {"TclError", "Exception", "BaseException"},
    "OSError": {"OSError", "IOError", "EnvironmentError", "Exception",
                "BaseException"},
    # « DEGRADE » ne lève rien : rien ne peut le garder, et c'est le point.
    "DEGRADE": set(),
}


def _noms_attrapes(gestionnaire):
    """Les noms d'exceptions d'une clause `except` (à plat)."""
    t = gestionnaire.type
    if t is None:
        return {"BaseException"}          # `except:` nu
    morceaux = t.elts if isinstance(t, ast.Tuple) else [t]
    noms = set()
    for m in morceaux:
        while isinstance(m, ast.Attribute):      # tk.TclError -> TclError
            m = m.attr if isinstance(m.attr, str) else m.value
            if isinstance(m, str):
                noms.add(m)
                m = None
                break
        if isinstance(m, ast.Name):
            noms.add(m.id)
    return noms


def _est_test_de_plateforme(test):
    """`hasattr(os, "startfile")`, `os.name == "nt"`,
    `sys.platform.startswith("win")`, `remplacement_possible()` — et leurs
    négations. C'est la SECONDE manière de garder, à côté du try/except : une
    fonction qui commence par « si on n'est pas sous Windows, on s'arrête »
    protège tout ce qui suit, et un balayage qui l'ignore signale à tort."""
    # VOLONTAIREMENT STRICT. Un détecteur trop large déclarerait « gardé » ce
    # qui ne l'est pas — c'est-à-dire exactement le défaut qu'on chasse depuis
    # une semaine : le vert de complaisance. Chaque forme reconnue ci-dessous
    # est nommée ; tout le reste compte comme NON gardé.
    def _os_name_ou_sys_platform(n):
        return (isinstance(n, ast.Attribute)
                and isinstance(n.value, ast.Name)
                and ((n.value.id == "os" and n.attr == "name")
                     or (n.value.id == "sys" and n.attr == "platform")))

    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return _est_test_de_plateforme(test.operand)
    if isinstance(test, ast.Compare):                    # os.name == "nt"
        return _os_name_ou_sys_platform(test.left)
    if isinstance(test, ast.Call):
        f = test.func
        # hasattr(os, "startfile") — et seulement sur os / sys / ctypes.
        if isinstance(f, ast.Name) and f.id == "hasattr" and test.args:
            cible = test.args[0]
            return (isinstance(cible, ast.Name)
                    and cible.id in ("os", "sys", "ctypes"))
        # sys.platform.startswith("win")
        if isinstance(f, ast.Attribute) and f.attr == "startswith":
            return _os_name_ou_sys_platform(f.value)
        # La règle NOMMÉE de la maison : logique.remplacement_possible()
        nom = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
        return nom == "remplacement_possible"
    return _os_name_ou_sys_platform(test)


def _garde_de_plateforme(noeud):
    """La fonction commence-t-elle par une garde de plateforme qui SORT
    (return / raise) ? On ne regarde que les premières instructions, avant
    tout autre code : une garde posée au milieu ne protège pas ce qui la
    précède, et on ne veut pas se rassurer à bon compte."""
    for instruction in noeud.body:
        if isinstance(instruction, ast.Expr) and isinstance(
                instruction.value, ast.Constant):
            continue                              # la docstring
        if not isinstance(instruction, ast.If):
            return False
        if not _est_test_de_plateforme(instruction.test):
            return False
        sortie = instruction.body and isinstance(
            instruction.body[-1], (ast.Return, ast.Raise))
        return bool(sortie)
    return False


class Balayeur(ast.NodeVisitor):
    def __init__(self, chemin, source):
        self.chemin = os.path.basename(chemin)
        self.lignes = source.split("\n")
        self.pile_try = []        # (noms attrapés) des try qui nous entourent
        self.pile_def = []
        self.garde_plateforme = False
        self.trouvailles = []
        # Noms liés à une valeur qui retombe sur 0 hors Windows. L'AST est
        # parcouru dans l'ordre du source : une constante posée en tête de
        # module est donc enregistrée avant les fonctions qui l'emploient.
        self.replis_surs = set()

    # -- suivi du contexte ------------------------------------------------- #
    def visit_Assign(self, noeud):
        """Retient `X = getattr(subprocess, "CREATE_NO_WINDOW", 0)` et `X = 0`."""
        if self._a_un_repli(noeud.value):
            for c in noeud.targets:
                if isinstance(c, ast.Name):
                    self.replis_surs.add(c.id)
        self.generic_visit(noeud)

    @staticmethod
    def _a_un_repli(valeur):
        """La valeur vaut-elle 0 sur un système non Windows ?"""
        # Littéral 0 : accepté partout, par définition.
        if isinstance(valeur, ast.Constant) and valeur.value == 0:
            return True
        # getattr(module, "NOM", defaut) : le 3e argument EST le repli.
        return (isinstance(valeur, ast.Call)
                and isinstance(valeur.func, ast.Name)
                and valeur.func.id == "getattr"
                and len(valeur.args) == 3)

    def _repli_hors_windows(self, valeur):
        """creationflags=<valeur> est-il sûr hors Windows ?"""
        if self._a_un_repli(valeur):
            return True
        # Un nom : sûr seulement si on l'a vu recevoir une valeur à repli.
        return isinstance(valeur, ast.Name) and valeur.id in self.replis_surs

    def visit_Try(self, noeud):
        attrapes = set()
        for g in noeud.handlers:
            attrapes |= _noms_attrapes(g)
        # Seul le CORPS du try est protégé — ni le `else`, ni le `finally`,
        # ni les gestionnaires eux-mêmes.
        self.pile_try.append(attrapes)
        for enfant in noeud.body:
            self.visit(enfant)
        self.pile_try.pop()
        for bloc in (noeud.handlers, noeud.orelse, noeud.finalbody):
            for enfant in bloc:
                self.visit(enfant)

    def _visiter_def(self, noeud):
        self.pile_def.append(noeud.name)
        # ⚠️ Une fonction DÉFINIE dans un try n'est pas EXÉCUTÉE dedans : la
        # garde ne la couvre pas. On repart donc d'une pile vide.
        pile, plateforme = self.pile_try, self.garde_plateforme
        self.pile_try = []
        self.garde_plateforme = plateforme or _garde_de_plateforme(noeud)
        self.generic_visit(noeud)
        self.pile_try, self.garde_plateforme = pile, plateforme
        self.pile_def.pop()

    visit_FunctionDef = _visiter_def
    visit_AsyncFunctionDef = _visiter_def

    # -- les familles ------------------------------------------------------ #
    def _noter(self, noeud, symbole, leve, quoi):
        attrapes = set()
        for a in self.pile_try:
            attrapes |= a
        gardee = bool(attrapes & GARDES[leve]) or self.garde_plateforme
        if self.garde_plateforme and not (attrapes & GARDES[leve]):
            attrapes = attrapes | {"(garde de plateforme)"}
        self.trouvailles.append({
            "fichier": self.chemin,
            "ligne": noeud.lineno,
            "fonction": self.pile_def[-1] if self.pile_def else "(module)",
            "symbole": symbole,
            "leve": leve,
            "gardee": gardee,
            "attrapes": ", ".join(sorted(attrapes)) or "aucun try",
            "quoi": quoi,
        })

    def visit_Import(self, noeud):
        for a in noeud.names:
            racine = a.name.split(".")[0]
            if racine in MODULES_WINDOWS:
                self._noter(noeud, "import " + a.name, "ImportError",
                            "module absent hors Windows")
        self.generic_visit(noeud)

    def visit_ImportFrom(self, noeud):
        if (noeud.module or "").split(".")[0] in MODULES_WINDOWS:
            self._noter(noeud, "from %s import …" % noeud.module,
                        "ImportError", "module absent hors Windows")
        self.generic_visit(noeud)

    def visit_Attribute(self, noeud):
        base = noeud.value
        if isinstance(base, ast.Name):
            if base.id == "os" and noeud.attr in ATTRIBUTS_OS:
                self._noter(noeud, "os." + noeud.attr, "AttributeError",
                            "n'existe que sous Windows")
            elif base.id == "ctypes" and noeud.attr in ATTRIBUTS_CTYPES:
                self._noter(noeud, "ctypes." + noeud.attr, "AttributeError",
                            "API Windows")
        self.generic_visit(noeud)

    def visit_Call(self, noeud):
        f = noeud.func
        if isinstance(f, ast.Attribute):
            if f.attr in PIEGES_FENETRE:
                self._noter(noeud, f.attr + "()", "TclError",
                            PIEGES_FENETRE[f.attr])
            if f.attr in ("attributes", "wm_attributes", "state"):
                for a in noeud.args:
                    if isinstance(a, ast.Constant) and \
                            str(a.value) in OPTIONS_FENETRE_WINDOWS:
                        self._noter(noeud, "%s(%r)" % (f.attr, a.value),
                                    "TclError",
                                    "option Windows seulement")
            # La molette ne LÈVE pas : elle ne fait simplement rien sous X11.
            # C'est donc un « dégrade » — mais le pire genre, celui qui ne
            # laisse aucune trace. Le remède maison est `lier_molette()`, qui
            # relie les trois séquences ; on ne signale donc pas son intérieur.
            if f.attr in ("bind", "tag_bind", "bind_all") and \
                    self.pile_def[-1:] != ["lier_molette"]:
                for a in noeud.args:
                    if isinstance(a, ast.Constant) and \
                            a.value == SEQUENCES_MOLETTE:
                        self._noter(noeud, "bind(<MouseWheel>)", "DEGRADE",
                                    "sous X11 la molette est Button-4/5 et "
                                    "delta vaut 0 : ne défile PAS, en "
                                    "silence — remède : lier_molette()")
        for mc in noeud.keywords:
            if mc.arg == "creationflags":
                # La règle disait « ValueError hors Windows », sans nuance. Or
                # subprocess ne refuse creationflags que si la valeur est NON
                # NULLE : passer 0 est accepté sur toutes les plateformes. La
                # règle telle quelle poussait donc à ÉVITER creationflags, et
                # c'est ce qui a laissé 8 appels à git et powershell ouvrir une
                # fenêtre noire volant le focus sous pythonw.exe (01/08/2026).
                # On ne signale plus que la forme dangereuse : une constante
                # Windows écrite en dur, sans repli pour les autres systèmes.
                # `getattr(subprocess, "CREATE_NO_WINDOW", 0)` est le remède.
                if not self._repli_hors_windows(mc.value):
                    self._noter(noeud, "creationflags=…", "ValueError",
                                "constante Windows sans repli : ValueError "
                                "hors Windows — remède : "
                                'getattr(subprocess, "CREATE_NO_WINDOW", 0)')
        # os.environ.get("APPDATA") et compagnie
        if isinstance(f, ast.Attribute) and f.attr == "get" and \
                isinstance(f.value, ast.Attribute) and \
                f.value.attr == "environ":
            for a in noeud.args[:1]:
                if isinstance(a, ast.Constant) and \
                        str(a.value).upper() in ENV_WINDOWS:
                    # `.get()` ne LÈVE jamais : ces endroits dégradent, ils
                    # ne plantent pas. On les compte à part — les mélanger
                    # aux plantages fausserait le chiffre qui compte.
                    defaut = len(noeud.args) > 1
                    self._noter(noeud, 'os.environ.get("%s")' % a.value,
                                "DEGRADE",
                                "variable Windows ; %s — à relire à la main"
                                % ("un défaut est prévu" if defaut
                                   else "aucun défaut, rend None"))
        self.generic_visit(noeud)

    def visit_Subscript(self, noeud):
        v = noeud.value
        if isinstance(v, ast.Attribute) and v.attr == "environ" and \
                isinstance(noeud.slice, ast.Constant) and \
                str(noeud.slice.value).upper() in ENV_WINDOWS:
            self._noter(noeud, 'os.environ["%s"]' % noeud.slice.value,
                        "OSError", "variable Windows, lève un KeyError")
        self.generic_visit(noeud)

    def visit_Constant(self, noeud):
        if isinstance(noeud.value, str):
            bas = noeud.value.strip().lower()
            if bas in COMMANDES_WINDOWS:
                self._noter(noeud, '"%s"' % noeud.value, "OSError",
                            "commande externe Windows")
        self.generic_visit(noeud)


def balayer(chemin):
    source = io.open(chemin, encoding="utf-8").read()
    b = Balayeur(chemin, source)
    b.visit(ast.parse(source))
    return b.trouvailles


def main(argv):
    origine = "--origine" in argv
    argv = [a for a in argv if a != "--origine"]
    fichiers = argv or FICHIERS

    tout = []
    for chemin in fichiers:
        if origine:
            rel = os.path.relpath(chemin, BASE).replace(os.sep, "/")
            source = subprocess.run(
                ["git", "show", "HEAD:" + rel], cwd=BASE,
                capture_output=True, text=True, encoding="utf-8",
                creationflags=SANS_FENETRE).stdout
            tampon = os.path.join(os.environ.get("TEMP", "."),
                                  "_origine_" + os.path.basename(chemin))
            io.open(tampon, "w", encoding="utf-8").write(source)
            tout += balayer(tampon)
            for t in tout:
                if t["fichier"].startswith("_origine_"):
                    t["fichier"] = t["fichier"][9:]
        else:
            tout += balayer(chemin)

    print("=" * 78)
    print("BALAYAGE « ÇA SUPPOSE WINDOWS » — %s"
          % ("version d'AVANT (git HEAD)" if origine else "version courante"))
    print("=" * 78)

    par_famille = {}
    for t in tout:
        par_famille.setdefault(t["leve"], []).append(t)

    for famille in sorted(par_famille):
        lot = par_famille[famille]
        gardees = sum(1 for t in lot if t["gardee"])
        print("\n### lève %s hors Windows — %d trouvaille(s), %d gardée(s), "
              "%d NON gardée(s)" % (famille, len(lot), gardees,
                                    len(lot) - gardees))
        for t in sorted(lot, key=lambda x: (x["fichier"], x["ligne"])):
            print("  %s %-22s %s:%-5d %-28s  attrapé: %s"
                  % ("ok " if t["gardee"] else "NON",
                     t["symbole"][:22], t["fichier"][:16], t["ligne"],
                     t["fonction"][:28], t["attrapes"][:34]))
            if not t["gardee"]:
                print("      -> %s" % t["quoi"])

    plantent = [t for t in tout if t["leve"] != "DEGRADE"]
    degradent = [t for t in tout if t["leve"] == "DEGRADE"]
    gardees = sum(1 for t in plantent if t["gardee"])
    print("\n" + "=" * 78)
    print("TOTAL : %d endroits supposent Windows." % len(tout))
    print("  %d PEUVENT LEVER : %d gardés, %d NON gardés."
          % (len(plantent), gardees, len(plantent) - gardees))
    print("  %d ne lèvent pas mais dégradent (à relire à la main)."
          % len(degradent))
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
