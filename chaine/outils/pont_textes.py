# -*- coding: utf-8 -*-
r"""LE PONT ENTRE L'ATELIER ET LE DÉPÔT DES TEXTES (programme 22, 02/08/2026).

LE DÉFAUT QU'IL EMPÊCHE. Le programme 20 a publié une PHOTO des textes. Dès
que l'atelier tourne, la copie de Dan et celle de GitHub s'éloignent — et
recopier un fichier entier dans un sens ou dans l'autre détruit le travail de
l'autre côté :

    Dan lance l'atelier   -> 800 quêtes nouvelles dans son quetes.json
    un contributeur corrige une faute dans CE fichier, sur GitHub
    Dan pose le fichier du contributeur par-dessus le sien
        -> les 800 quêtes disparaissent
    ou Dan renvoie les siens
        -> la correction du contributeur disparaît

Perdre la contribution d'un bénévole ne se rattrape pas : il ne revient pas.

CE N'EST DONC PAS UNE COPIE DE FICHIERS, C'EST UNE FUSION À TROIS VOIES,
clé par clé (feuille par feuille, exactement) :

    base   = ce que Dan a publié la dernière fois
    eux    = ce que GitHub porte aujourd'hui
    nous   = ce que l'atelier de Dan porte aujourd'hui

    eux == base                  -> le contributeur n'a rien touché : on garde nous
    eux != base et nous == base  -> correction de contributeur : elle RENTRE
    eux != base et nous != base
                 et nous != eux  -> CONFLIT : on ne devine pas, on s'arrête

LA BASE VIENT DE GIT, PAS D'UN FICHIER DE SUIVI. `git merge-base` la donne
gratuitement dans le clone : le dernier commit que Dan a publié. Un état
stocké à côté finit toujours par mentir — il survit à un retour arrière, à
une restauration, à une manipulation manuelle, et il ment alors en silence.

L'ORDRE EST IMPOSÉ PAR LE CODE, PAS PAR LA MÉMOIRE :

    1. récupérer   2. atelier   3. publier

`--publier` REFUSE tant que le dépôt distant porte des commits que Dan n'a
pas récupérés. C'est le trou « commité mais pas poussé » du programme 14, vu
à l'envers — et il a mordu deux fois dans la semaine.

Usage :
    python outils/pont_textes.py                # l'état, sans rien toucher
    python outils/pont_textes.py --recuperer    # les corrections rentrent
    python outils/pont_textes.py --publier      # ce qui est nouveau part
    python outils/pont_textes.py --recuperer --appliquer
    python outils/pont_textes.py --publier --appliquer
"""
import io
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ICI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

TRADUCTIONS = os.path.join(BASE, "traductions")
CLONE = r"D:\AscensionFR\depot_textes"

# On réutilise les DEUX contrôles de format qui existent déjà, plutôt que d'en
# écrire un troisième qui divergerait :
#   - signature_compatible : la famille %s / %1$s (rangs ET types)
#   - codes_perdus         : la famille $n $b $c $g…; |cffffffff |r |T…|t
from generateur_glue import signature_compatible          # noqa: E402
from fusionner_lots import codes_perdus                   # noqa: E402
from ecriture_sure import ecrire_json                     # noqa: E402

# Les 5 stores RECONSTRUITS À NEUF par la chaîne ne sont pas publiés : une
# correction écrite dedans serait effacée au passage suivant. Le pont doit
# refuser de les voir arriver — une inversion ici est le pire des bugs.
DERIVES = {"interface_maison.json", "sorts_references.json", "emotes.json",
           "interieurs.json", "taxinodes.json"}


# ---------------------------------------------------------------------------
# git, dans le clone
# ---------------------------------------------------------------------------
# Sous pythonw.exe (sans console), démarrer git force Windows à ouvrir une
# fenêtre noire, qui vole le focus et éjecte d'un jeu en plein écran.
# capture_output redirige les FLUX, pas la FENÊTRE. getattr : la constante
# n'existe que sur Windows ; ailleurs 0, que subprocess accepte partout
# (il ne refuse creationflags que si la valeur est NON NULLE).
SANS_FENETRE = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def git(*args, **kw):
    r = subprocess.run(["git"] + list(args), cwd=kw.get("cwd", CLONE),
                       capture_output=True, creationflags=SANS_FENETRE)
    if r.returncode != 0 and not kw.get("tolerant"):
        raise RuntimeError("git %s : %s"
                           % (" ".join(args),
                              r.stderr.decode("utf-8", "replace").strip()))
    return r.stdout.decode("utf-8", "replace")


def git_octets(*args):
    r = subprocess.run(["git"] + list(args), cwd=CLONE, capture_output=True,
                       creationflags=SANS_FENETRE)
    return r.stdout if r.returncode == 0 else None


# ---------------------------------------------------------------------------
# Aplatir : les stores n'ont pas tous la même forme
# ---------------------------------------------------------------------------
# sorts.json      : {"descriptions": {anglais: français}, "noms": {…}}
# quetes.json     : {identifiant: {"T": …, "D": …, "OT": [ … ]}}
# gisement_brut   : {anglais: français}
# Un chemin de feuille traverse tout ça sans avoir à connaître la forme.
def aplatir(objet, prefixe=()):
    plat = {}
    if isinstance(objet, dict):
        for cle, valeur in objet.items():
            plat.update(aplatir(valeur, prefixe + (str(cle),)))
    elif isinstance(objet, list):
        for i, valeur in enumerate(objet):
            plat.update(aplatir(valeur, prefixe + ("[%d]" % i,)))
    else:
        plat[prefixe] = objet
    return plat


def poser(objet, chemin, valeur):
    """Écrit `valeur` au bout de `chemin` dans une structure existante."""
    courant = objet
    for element in chemin[:-1]:
        if element.startswith("[") and element.endswith("]"):
            courant = courant[int(element[1:-1])]
        else:
            courant = courant[element]
    dernier = chemin[-1]
    if dernier.startswith("[") and dernier.endswith("]"):
        courant[int(dernier[1:-1])] = valeur
    else:
        courant[dernier] = valeur


def montrer(revision, chemin_relatif):
    """Le contenu d'un fichier à une révision donnée, ou None s'il n'y était
    pas."""
    octets = git_octets("show", "%s:%s" % (revision, chemin_relatif))
    if octets is None:
        return None
    try:
        return json.loads(octets.decode("utf-8"))
    except ValueError:
        return None


def charger(chemin):
    if not os.path.exists(chemin):
        return None
    return json.load(io.open(chemin, encoding="utf-8"))


def format_casse(avant, apres):
    """Le contributeur a-t-il abîmé un code de format ?

    On ne réinvente rien : `signature_compatible` (generateur_glue) tient la
    famille %s, `codes_perdus` (fusionner_lots) tient la famille $ et |c.
    Un %s en trop fait planter le jeu ; un |r perdu laisse tout l'écran en
    couleur."""
    if not isinstance(avant, str) or not isinstance(apres, str):
        return None
    if not signature_compatible(avant, apres):
        return "signature %s incompatible"
    perdus = codes_perdus(avant, apres)
    if perdus:
        return "code(s) perdu(s) : %s" % ", ".join(sorted(perdus))
    return None


# ---------------------------------------------------------------------------
# RÉCUPÉRER — la fusion à trois voies
# ---------------------------------------------------------------------------
def recuperer(appliquer):
    print("=" * 78)
    print("RÉCUPÉRER — les corrections des contributeurs")
    print("=" * 78)

    git("fetch", "--quiet", "origin")
    base_sha = git("merge-base", "main", "origin/main").strip()
    tete = git("rev-parse", "origin/main").strip()
    print("  base (dernière publication de Dan) : %s" % base_sha[:8])
    print("  dépôt distant aujourd'hui          : %s" % tete[:8])

    if base_sha == tete:
        print("\nrien à récupérer : le dépôt distant n'a pas bougé depuis la")
        print("dernière publication.")
        return 0

    nouveaux = git("rev-list", "--count", "%s..origin/main" % base_sha).strip()
    print("  commits de contributeurs à examiner : %s" % nouveaux)
    print()

    publies = [l for l in git("ls-tree", "--name-only", "origin/main",
                              "traductions/").splitlines() if l.strip()]

    entrantes, conflits, structures, formats = [], [], [], []
    for relatif in sorted(publies):
        nom = os.path.basename(relatif)
        if nom in DERIVES:
            structures.append((nom, "—", "fichier RECONSTRUIT À NEUF, il ne "
                                         "devrait pas être publié"))
            continue
        b, e = montrer(base_sha, relatif), montrer("origin/main", relatif)
        n = charger(os.path.join(TRADUCTIONS, nom))
        if e is None or n is None:
            structures.append((nom, "—", "fichier absent d'un côté"))
            continue
        pb, pe, pn = aplatir(b or {}), aplatir(e), aplatir(n)

        for chemin in sorted(set(pe) | set(pb), key=lambda c: "/".join(c)):
            av_b, av_e = pb.get(chemin, ...), pe.get(chemin, ...)
            if av_b == av_e:
                continue                      # le contributeur n'y a pas touché
            if av_b is ... or av_e is ...:
                structures.append((nom, "/".join(chemin),
                                   "clé AJOUTÉE" if av_b is ...
                                   else "clé SUPPRIMÉE"))
                continue
            av_n = pn.get(chemin, ...)
            if av_n is ...:
                structures.append((nom, "/".join(chemin),
                                   "corrigée sur GitHub mais absente chez Dan"))
                continue
            if av_n == av_e:
                continue                      # déjà à jour des deux côtés
            if av_n != av_b:
                conflits.append((nom, "/".join(chemin), av_b, av_n, av_e))
                continue
            grief = format_casse(av_b, av_e)
            if grief:
                formats.append((nom, "/".join(chemin), grief))
                continue
            entrantes.append((nom, chemin, av_b, av_e))

    # ----- le rapport -----
    print("corrections entrantes  : %d" % len(entrantes))
    for nom, chemin, av, ap in entrantes[:20]:
        print("   %-22s %s" % (nom, "/".join(chemin)[:46]))
        print("       avant : %r" % (av if not isinstance(av, str)
                                     else av[:70]))
        print("       après : %r" % (ap if not isinstance(ap, str)
                                     else ap[:70]))
    if len(entrantes) > 20:
        print("   … et %d autres" % (len(entrantes) - 20))

    for titre, liste in (("CHANGEMENTS DE STRUCTURE (non appliqués)",
                          structures),
                         ("CODES DE FORMAT ABÎMÉS (non appliqués)", formats)):
        if liste:
            print()
            print("⚠️  %s : %d" % (titre, len(liste)))
            for x in liste[:12]:
                print("   %-22s %-40s %s" % (x[0], str(x[1])[:40], x[2]))

    if conflits:
        print()
        print("=" * 78)
        print("🛑 %d CONFLIT(S) — LES DEUX CÔTÉS ONT MODIFIÉ LA MÊME CLÉ."
              % len(conflits))
        print("=" * 78)
        for nom, chemin, b, n, e in conflits[:20]:
            print("   fichier : %s" % nom)
            print("   clé     : %s" % chemin)
            print("     base (dernière publication) : %r"
                  % (b[:70] if isinstance(b, str) else b))
            print("     chez Dan                    : %r"
                  % (n[:70] if isinstance(n, str) else n))
            print("     sur GitHub                  : %r"
                  % (e[:70] if isinstance(e, str) else e))
            print()
        print("Je ne devine pas. RIEN n'a été appliqué.")
        print("Tranche toi-même : corrige la valeur que tu veux garder dans")
        print("   %s" % TRADUCTIONS)
        print("puis relance. Un outil qui choisit tout seul dans ce cas")
        print("finira un jour par choisir mal, en silence.")
        return 1

    if not appliquer:
        if not entrantes:
            print("\nrien à intégrer, mais le clone est en retard : "
                  "--appliquer le fera avancer.")
        else:
            print("\nSIMULATION — rien n'a été écrit. --appliquer pour poser.")
        return 0

    # ⚠️ LE DÉFAUT QUE CE BLOC CORRIGE (trouvé au contrôle final du prog. 22).
    # Le premier jet sortait ici quand il n'y avait rien à intégrer, SANS
    # faire avancer le clone. La base de la fusion suivante restait alors
    # l'ancienne publication : les mêmes commits étaient réexaminés
    # indéfiniment, et `--publier` refusait pour toujours en réclamant une
    # récupération déjà faite. Un garde-fou qui ne peut plus être satisfait
    # finit contourné.
    if not entrantes:
        print("\nrien à intégrer : aucune valeur de contributeur à reprendre.")
        git("merge", "--ff-only", "origin/main")
        print("Le clone suit maintenant le dépôt distant (%s)."
              % git("rev-parse", "--short", "HEAD").strip())
        return 0

    par_fichier = {}
    for nom, chemin, _av, ap in entrantes:
        par_fichier.setdefault(nom, []).append((chemin, ap))
    for nom, poses in sorted(par_fichier.items()):
        chemin_fichier = os.path.join(TRADUCTIONS, nom)
        donnees = charger(chemin_fichier)
        avant_feuilles = len(aplatir(donnees))
        for chemin, valeur in poses:
            poser(donnees, chemin, valeur)
        apres_feuilles = len(aplatir(donnees))
        ecrire_json(chemin_fichier, donnees)
        print("   %-22s %d correction(s) — feuilles %d -> %d"
              % (nom, len(poses), avant_feuilles, apres_feuilles))

    # La fusion est faite CHEZ DAN ; on avance le clone sur origin pour que la
    # base de la prochaine fusion soit juste.
    git("merge", "--ff-only", "origin/main")
    print("\n✅ %d correction(s) intégrée(s). Le clone suit maintenant "
          "le dépôt distant." % len(entrantes))
    return 0


# ---------------------------------------------------------------------------
# PUBLIER
# ---------------------------------------------------------------------------
def publier(appliquer):
    print("=" * 78)
    print("PUBLIER — ce que l'atelier a produit")
    print("=" * 78)

    # ----- LE GARDE-FOU : on ne publie pas par-dessus des contributions -----
    git("fetch", "--quiet", "origin")
    retard = int(git("rev-list", "--count", "main..origin/main").strip())
    if retard:
        print("\n🛑 REFUS — le dépôt distant porte %d commit(s) que tu n'as "
              "pas récupéré(s)." % retard)
        for ligne in git("log", "--oneline", "--no-decorate",
                         "main..origin/main").splitlines()[:10]:
            print("     ", ligne)
        print("\nPublier maintenant écraserait ces contributions.")
        print("Lance d'abord :  python outils/pont_textes.py --recuperer "
              "--appliquer")
        return 1
    print("  aucun commit non récupéré : la voie est libre.")

    publies = [l for l in git("ls-tree", "--name-only", "origin/main",
                              "traductions/").splitlines() if l.strip()]
    print("  fichiers publiés à tenir à jour : %d" % len(publies))

    # ----- ce qui changerait -----
    changements = []
    for relatif in sorted(publies):
        nom = os.path.basename(relatif)
        if nom in DERIVES:
            print("\n🛑 REFUS — %s est un store RECONSTRUIT À NEUF et se "
                  "trouve pourtant publié." % nom)
            print("   Une correction écrite dedans serait effacée au passage")
            print("   suivant. Retire-le du dépôt avant de continuer.")
            return 1
        source = os.path.join(TRADUCTIONS, nom)
        if not os.path.exists(source):
            print("\n🛑 REFUS — %s est publié mais absent de %s"
                  % (nom, TRADUCTIONS))
            return 1
        a = io.open(source, "rb").read()
        b = io.open(os.path.join(CLONE, relatif), "rb").read()
        if a != b:
            av, ap = len(aplatir(json.loads(b.decode("utf-8")))), \
                     len(aplatir(json.loads(a.decode("utf-8"))))
            changements.append((relatif, nom, a, av, ap))

    if not changements:
        print("\nrien à faire : le dépôt public est déjà à jour.")
        return 0

    print("\n%d fichier(s) à mettre à jour :" % len(changements))
    for _rel, nom, _a, av, ap in changements:
        print("   %-24s %8d -> %8d feuilles  (%+d)" % (nom, av, ap, ap - av))

    if not appliquer:
        print("\nSIMULATION — rien n'a été écrit ni poussé. --appliquer "
              "pour publier.")
        return 0

    # ----- écriture, puis LE BALAYAGE, avant tout commit -----
    for relatif, _nom, contenu, _av, _ap in changements:
        io.open(os.path.join(CLONE, relatif), "wb").write(contenu)

    print("\n--- balayage de l'arbre qui part ---")
    trouves, ouverts = balayer(CLONE)
    print("    fichiers réellement ouverts et lus : %d" % ouverts)
    print("    motifs trouvés                     : %d" % len(trouves))
    if trouves:
        for t in trouves[:15]:
            print("      ", t)
        git("checkout", "--", "traductions/")
        print("\n🛑 REFUS — %d motif(s). L'arbre du clone a été remis en "
              "état, rien n'est parti." % len(trouves))
        print("L'atelier ingère des textes récoltés chez les joueurs : un")
        print("pseudonyme neuf peut arriver à tout moment. Ce refus n'est pas")
        print("une formalité.")
        return 1

    git("add", "-A", "traductions/")
    if not git("diff", "--cached", "--name-only").strip():
        print("\nrien à commiter.")
        return 0
    git("commit", "--quiet", "-m",
        "Textes à jour depuis l'atelier (%d fichier(s))" % len(changements))
    git("push", "--quiet", "origin", "main")

    git("fetch", "--quiet", "origin")
    avance = int(git("rev-list", "--count", "origin/main..main").strip())
    print("\n  git rev-list --count origin/main..main = %d" % avance)
    if avance:
        print("🛑 le push n'est PAS arrivé.")
        return 1
    print("  %s" % git("ls-remote", "origin", "refs/heads/main").strip())
    print("\n✅ publié et vérifié depuis le distant.")
    return 0


def balayer(racine):
    """Secrets + pseudonymes + chemins de disque, avec le dénominateur."""
    import re
    sys.path.insert(0, ICI)
    from secrets_publication import balayer_texte, BINAIRES

    # 🛑 AUCUN nom en dur (programme 34, bloc 0) : la liste vit dans le
    # fichier local, jamais dans le code — une liste de repli était partie
    # dans le dépôt cloud. Fichier absent = balayage des pseudos INERTE,
    # et on le DIT (un filet vide silencieux, c'est le piège du banc vide).
    pseudos = []
    fichier_noms = os.path.join(BASE, "noms_recolteurs.local.txt")
    if os.path.exists(fichier_noms):
        for ligne in io.open(fichier_noms, encoding="utf-8"):
            n = ligne.strip()
            if n and not n.startswith("#") and n not in pseudos:
                pseudos.append(n)
    if not pseudos:
        print("⚠️ noms_recolteurs.local.txt absent : le balayage des "
              "pseudos ne balaie RIEN ce passage.")
    re_pseudo = re.compile(r"\b(?:%s)\b"
                           % "|".join(re.escape(n) for n in sorted(pseudos)),
                           re.I)
    # Motif RESSERRÉ : le premier jet du programme 19 rapportait 88 faux, il
    # attrapait « s:\r\n » dans du texte de jeu (le \r et le \n d'une chaîne
    # JSON, pas un séparateur).
    re_chemin = re.compile(
        r"[A-Za-z]:\\\\?(?![rnt0\\])[\w\-. ]{2,}[\\/][\w\-. ]{2,}"
        r"|/(?:home|Users|mnt|media)/[\w\-.]{2,}/[\w\-./]{2,}"
        r"|AscensionFR[\\/]{1,2}WorkFlow", re.I)

    trouves, ouverts = [], 0
    for dossier, sous, noms in os.walk(racine):
        sous[:] = [d for d in sous if d != ".git"]
        for nom in sorted(noms):
            chemin = os.path.join(dossier, nom)
            rel = os.path.relpath(chemin, racine).replace(os.sep, "/")
            if nom.lower().endswith(BINAIRES):
                continue
            texte = io.open(chemin, encoding="utf-8", errors="replace").read()
            ouverts += 1
            for t in balayer_texte(rel, texte):
                trouves.append(("secret", rel) + t)
            # GARDE des pseudonymes : cherche AUSSI dans une copie dénudée
            # des codes de format — « |cFFB5FFFFStarcaller » n'a pas de
            # frontière de mot et passait au travers du \b (le piège du
            # lot 14, rebouché partout au programme 32).
            denude = re.sub(r"\|T[^|]*\|t|\|c[0-9a-fA-F]{8}|\|r", " ",
                            texte)
            vus = set()
            for source in (texte, denude):
                for m in re_pseudo.finditer(source):
                    if m.group() not in vus:
                        vus.add(m.group())
                        trouves.append(("pseudonyme", rel, m.group()))
            for m in re_chemin.finditer(texte):
                trouves.append(("chemin", rel, m.group()))
    return trouves, ouverts


def etat():
    git("fetch", "--quiet", "origin")
    avance = int(git("rev-list", "--count", "origin/main..main").strip())
    retard = int(git("rev-list", "--count", "main..origin/main").strip())
    print("=" * 78)
    print("ÉTAT DU PONT")
    print("=" * 78)
    print("  atelier de Dan  : %s" % TRADUCTIONS)
    print("  clone public    : %s" % CLONE)
    print("  commits que Dan n'a pas récupérés : %d" % retard)
    print("  commits que Dan n'a pas publiés   : %d" % avance)
    print()
    if retard:
        print("👉 commence par :  python outils/pont_textes.py --recuperer")
    elif avance:
        print("👉 il reste à publier : --publier")
    else:
        print("✅ les deux côtés sont au même point.")
    return 0


def main():
    appliquer = "--appliquer" in sys.argv
    if "--recuperer" in sys.argv:
        return recuperer(appliquer)
    if "--publier" in sys.argv:
        return publier(appliquer)
    return etat()


if __name__ == "__main__":
    sys.exit(main())
