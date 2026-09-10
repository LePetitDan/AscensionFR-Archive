# -*- coding: utf-8 -*-
"""mesurer_constantes.py — combien de marge reste-t-il avant que Lua refuse ?

POURQUOI (25/07/2026)
---------------------
Lua 5.1 — donc le client de WoW 3.3.5a — n'accepte que 262 143 constantes par
PROTOTYPE de fonction (MAXARG_Bx ; lcode.c, addk -> « constant table
overflow »). Une constante = une chaîne DISTINCTE ou un nombre DISTINCT du
fichier : Lua dédoublonne, mais chaque identifiant d'objet reste un nombre
distinct. Passée la limite, le fichier ne se charge PAS — l'addon est mort au
/reload, sans le moindre message avant.

DB_Objets s'y est cogné : à 355 320 objets, les identifiants seuls dépassaient
la limite. Il est passé au format paresseux (un seau = UNE chaîne longue,
2 constantes) et retombe à 4 372 constantes.

CE QUE ÇA MESURE
----------------
La TAILLE DU FICHIER NE DIT RIEN : 26 Mo paresseux se compilent en 0,1 s,
quand le même contenu à plat ne compile pas du tout. On lit donc le vrai
chiffre, celui du compilateur : on compile, on demande string.dump, et on lit
« sizek » dans le bytecode. Aucune estimation.

Usage : python outils/mesurer_constantes.py [fichier.lua ...]
        (sans argument : toutes les bases de l'addon)
"""
import glob
import io
import os
import re
import struct
import sys

# La console de Dan est en cp1252 : un seul caractère hors de cette table
# lève UnicodeEncodeError et TUE le script — en silence s'il tourne en tâche
# planifiée. Règle valable pour tout outil du pipeline.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LIMITE = 262143          # MAXARG_Bx de Lua 5.1
SEUIL_ALERTE = 0.80

ADDON = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
         r"\AscensionFR")

# On passe par loadstring plutôt que par lupa.compile pour récupérer le
# message d'erreur exact du compilateur au lieu d'une exception Python.
_VIDAGE = ("local source, nom = ...\n"
           "local f, e = loadstring(source, '@' .. nom)\n"
           "if not f then return nil, tostring(e) end\n"
           "return string.dump(f)\n")


class _Bytecode(object):
    """Lecteur du format de string.dump de Lua 5.1 (little endian, 64 bits)."""

    def __init__(self, octets):
        self.o, self.i = octets, 0

    def _prendre(self, n):
        d = self.o[self.i:self.i + n]
        self.i += n
        return d

    def entier(self):
        return struct.unpack("<i", self._prendre(4))[0]

    def octet(self):
        v = self.o[self.i]
        self.i += 1
        return v

    def chaine(self):
        return self._prendre(struct.unpack("<Q", self._prendre(8))[0])

    def proto(self, protos):
        self.chaine()                       # source
        self.entier()                       # 1re ligne
        self.entier()                       # dernière ligne
        for _ in range(4):                  # nups, params, vararg, pile
            self.octet()
        self._prendre(4 * self.entier())    # instructions
        n_k = self.entier()
        for _ in range(n_k):
            t = self.octet()
            if t == 1:                      # booléen
                self.octet()
            elif t == 3:                    # nombre
                self._prendre(8)
            elif t == 4:                    # chaîne
                self.chaine()
            elif t != 0:                    # 0 = nil
                raise ValueError("constante de type inconnu : %d" % t)
        n_p = self.entier()
        protos.append(n_k)
        for _ in range(n_p):
            self.proto(protos)
        self._prendre(4 * self.entier())    # table des lignes
        for _ in range(self.entier()):      # variables locales
            self.chaine()
            self.entier()
            self.entier()
        for _ in range(self.entier()):      # upvalues
            self.chaine()
        return protos


def mesurer(source, nom="chunk"):
    """source : OCTETS. -> (compile, constantes du plus gros proto, message).

    Trois issues, à ne surtout pas confondre :
      (False, None, erreur)  le client REFUSERAIT le fichier — addon mort ;
      (True,  None, raison)  il se charge, mais la mesure a échoué (un défaut
                             de CET outil ne doit jamais passer pour une
                             faute de syntaxe : ça ferait crier au loup) ;
      (True,  n,    "")      il se charge et réclame n constantes.
    """
    import lupa.lua51 as lua51
    if isinstance(source, str):
        source = source.encode("utf-8")
    if isinstance(nom, str):
        nom = nom.encode("utf-8")
    # encoding=None : string.dump rend du binaire, pas du texte décodable.
    resultat = lua51.LuaRuntime(encoding=None).compile(_VIDAGE)(source, nom)
    if isinstance(resultat, tuple):
        return (False, None,
                resultat[1].decode("utf-8", "replace").splitlines()[0])
    if resultat is None:
        return False, None, "loadstring n'a rien rendu"
    try:
        lecteur = _Bytecode(resultat)
        lecteur._prendre(12)                # en-tête du dump
        return True, max(lecteur.proto([])), ""
    except Exception as e:                  # bytecode illisible par NOUS
        return True, None, "bytecode non lu (%s)" % e


def mesurer_fichier(chemin):
    return mesurer(io.open(chemin, "rb").read(),
                   os.path.basename(chemin))


# Un fichier PARESSEUX ne coûte presque rien à la compilation : ses seaux sont
# des chaînes. Mais le jeu les recompile UN PAR UN à l'exécution —
# loadstring("return {" .. morceau .. "}"), Core.lua (AFR.Paresseux et
# AFR.ParesseuxTexte) — et chaque seau est alors un PROTOTYPE à part entière,
# soumis au même plafond. Mesurer le fichier seul laisserait donc un angle
# mort total : un seau trop gros ne se compile pas, Core.lua avale l'échec
# (« if not usine then return nil end ») et les textes de ce seau restent
# anglais pour toute la session, sans un mot.
SEAU = re.compile(r"^M\[\d+\]=\[(=+)\[(.*)\]\1\]$", re.M)


def mesurer_seaux_texte(texte):
    """-> (nombre de seaux, pire nombre de constantes, seaux illisibles)."""
    if "AscensionFR.Paresseux" not in texte:
        return 0, 0, []
    pire, casses, seaux = 0, [], SEAU.findall(texte)
    for _, contenu in seaux:
        compile_ok, k, message = mesurer("return {" + contenu + "}", "seau")
        if not compile_ok:
            casses.append(message)
        elif k is not None:
            pire = max(pire, k)
    return len(seaux), pire, casses


def mesurer_seaux(chemin):
    return mesurer_seaux_texte(io.open(chemin, encoding="utf-8").read())


def bases_addon():
    """Toutes les bases livrées, addons ANNEXES compris.

    Les annexes (AscensionFR_Repliques, -Peche…) partent dans le même zip que
    l'addon principal : les oublier, c'est ne pas vérifier ce qu'on publie.
    """
    chemins = []
    racine = os.path.dirname(ADDON)
    for dossier in sorted(glob.glob(os.path.join(racine, "AscensionFR*"))):
        if not os.path.isdir(dossier):
            continue
        for motif in ("DB/*.lua", "Modules/*.lua", "*.lua"):
            chemins += sorted(glob.glob(os.path.join(dossier, motif)))
    return chemins


def main(chemins=None):
    chemins = chemins or bases_addon()
    print("Limite de Lua 5.1 : %d constantes par fonction." % LIMITE)
    print("%-30s %10s %8s  %s" % ("fichier", "constantes", "part", "état"))
    print("-" * 68)
    alertes, echecs = [], []
    for chemin in chemins:
        nom = os.path.basename(chemin)
        compile_ok, constantes, erreur = mesurer_fichier(chemin)
        if not compile_ok:
            echecs.append((nom, erreur))
            print("%-30s %10s %8s  NE COMPILE PAS : %s"
                  % (nom, "-", "-", erreur[:30]))
            continue
        if constantes is None:
            print("%-30s %10s %8s  se charge, non mesuré (%s)"
                  % (nom, "?", "-", erreur[:30]))
            continue
        # Sur une base paresseuse, le chiffre qui compte n'est pas celui du
        # fichier (quelques milliers) mais celui du plus gros SEAU, compilé
        # à l'exécution.
        n_seaux, pire, casses = mesurer_seaux(chemin)
        if casses:
            echecs.append((nom, "un seau ne compile pas : %s" % casses[0]))
            print("%-30s %10s %8s  SEAU ILLISIBLE — textes muets en jeu"
                  % (nom, "-", "-"))
            continue
        detail = ""
        if n_seaux:
            constantes = pire
            detail = "pire des %d seaux — " % n_seaux
        part = float(constantes) / LIMITE
        etat = "ok"
        if part >= SEUIL_ALERTE:
            etat = "À DÉCOUPER PLUS FIN" if n_seaux else "À PASSER EN PARESSEUX"
            alertes.append((nom, constantes))
        elif part >= 0.40:
            etat = "à surveiller"
        print("%-30s %10d %7.1f%%  %s%s"
              % (nom, constantes, 100 * part, detail, etat))
    print("-" * 68)
    if echecs:
        print("%d fichier(s) illisible(s) par le client — addon mort au "
              "chargement." % len(echecs))
    if alertes:
        print("%d base(s) au-delà de %.0f %% : passe-les au format paresseux "
              "(voir outils/optimiser_memoire.py)."
              % (len(alertes), 100 * SEUIL_ALERTE))
    if not echecs and not alertes:
        print("Toutes les bases ont de la marge.")
    return 1 if echecs else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:] or None))
