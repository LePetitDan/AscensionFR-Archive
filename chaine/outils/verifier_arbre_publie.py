# -*- coding: utf-8 -*-
r"""L'ARBRE PUBLIÉ CORRESPOND-IL À CE QU'ON A CONSTRUIT ? (bloc E, prog. 5)

LE DÉFAUT QU'IL ATTRAPE. Le 29/07/2026, le tag `v3.4.0` a été posé sur un
dépôt public resté au code de la **3.1.0** : les assets livrés étaient
justes, mais le lien « code source » du corps de release renvoyait à une
version d'il y a trois publications. Notre exe n'est pas signé, des
antivirus le suppriment, et notre seule réponse aux joueurs est « le code
est ouvert, allez voir ». Si celui qui va voir tombe sur du code périmé,
cette réponse ne vaut plus rien.

La barrière des TROIS VERSIONS (le `## Version:` du .toc, VERSION_COMPAGNON
et le tag) ne pouvait pas le voir : elle interroge l'arbre PRIVÉ, celui qui
construit. Personne ne regardait l'arbre PUBLIÉ, celui qu'on tague.

⚠️ LE DÉFAUT DE CONCEPTION DU PREMIER JET (corrigé au programme 6). Il
exigeait que l'arbre publié soit IDENTIQUE à l'arbre privé. Or l'arbre
publié doit être délibérément différent sur une ligne : le privé porte
l'URL du webhook Discord des rapports, le public porte `""`. Les deux
exigences étaient incompatibles — synchroniser fidèlement le faisait sortir
VERT pendant que le secret partait ; neutraliser le faisait sortir ROUGE
pour toujours. Un garde-fou qui ne peut être vert qu'au prix d'une fuite
est pire qu'absent : il donne raison au geste dangereux.

La réponse est la DIFFÉRENCE DÉCLARÉE. On ne compare plus « privé ==
publié » mais « privé NEUTRALISÉ == publié », la neutralisation venant de
`outils/secrets_injectes.json`. Cette seule comparaison porte les trois
exigences à la fois :
  - identité partout où rien n'est déclaré ;
  - sur une entrée déclarée, la valeur publique doit être EXACTEMENT la
    valeur neutre attendue — une autre valeur, même différente du secret,
    est un refus ;
  - toute divergence non déclarée, où que ce soit, reste un refus.

CE QU'IL VÉRIFIE — quatre choses, toutes bloquantes :
  1. le dépôt public n'a rien en attente (sinon on tague un état incomplet) ;
  2. chaque source de construction est identique au privé NEUTRALISÉ ;
  3. le VERSION_COMPAGNON de l'arbre PUBLIÉ est celui qu'on publie ;
  4. AUCUN motif de secret dans l'arbre public, quelle que soit
     l'extension — contrôle indépendant de toute déclaration, parce que la
     déclaration suppose qu'on ait PENSÉ au bon secret, et c'est
     précisément l'hypothèse qui a lâché.

Lecture seule : ce script ne commite, ne tague et ne pousse rien.

Usage : python outils/verifier_arbre_publie.py [--version 3.4.0]
                                               [--avec-historique]
"""
import io
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from secrets_publication import (BASE, SOURCES,  # noqa: E402
                                 PUBLIC as PUBLIC_PAR_DEFAUT,
                                 balayer_arbre, charger_declarations,
                                 neutraliser, valeurs_publiques)

PUBLIC = PUBLIC_PAR_DEFAUT

# Sous pythonw.exe (sans console), démarrer git force Windows à ouvrir une
# fenêtre noire, qui vole le focus et éjecte d'un jeu en plein écran.
# capture_output redirige les FLUX, pas la FENÊTRE. getattr : la constante
# n'existe que sur Windows ; ailleurs 0, que subprocess accepte partout
# (il ne refuse creationflags que si la valeur est NON NULLE).
SANS_FENETRE = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def lire(chemin):
    if not os.path.exists(chemin):
        return None
    with io.open(chemin, encoding="utf-8", errors="replace") as f:
        return f.read().replace("\r\n", "\n")


def version_de(texte):
    m = re.search(r'VERSION_COMPAGNON\s*=\s*"([^"]+)"', texte or "")
    return m.group(1) if m else None


def main():
    attendue = None
    if "--version" in sys.argv:
        attendue = sys.argv[sys.argv.index("--version") + 1]
    # Permet de viser une RÉPÉTITION À BLANC : une copie du dépôt public où
    # l'on a commité pour voir ce que le garde-fou dira, sans toucher au vrai
    # dépôt. Ce n'est pas une dérogation — aucun contrôle n'est relâché, on
    # change seulement l'arbre examiné.
    global PUBLIC
    if "--public" in sys.argv:
        PUBLIC = os.path.abspath(sys.argv[sys.argv.index("--public") + 1])
        print("(arbre examiné : %s)" % PUBLIC)

    print("=" * 66)
    print("L'ARBRE PUBLIÉ CORRESPOND-IL À CE QU'ON A CONSTRUIT ?")
    print("=" * 66)
    if not os.path.isdir(PUBLIC):
        print("dépôt public introuvable :", PUBLIC)
        return 2
    problemes = []

    # 1. rien en attente côté public
    # creationflags : sous pythonw.exe (sans console), démarrer git ferait
    # surgir une fenêtre noire volant le focus. Voir SANS_FENETRE plus haut.
    etat = subprocess.run(["git", "status", "--short"], cwd=PUBLIC,
                          capture_output=True, text=True,
                          creationflags=SANS_FENETRE).stdout.strip()
    if etat:
        lignes = [l for l in etat.splitlines() if l.strip()]
        print("\n1. EN ATTENTE dans le dépôt public : %d fichier(s)"
              % len(lignes))
        for l in lignes:
            print("     ", l)
        problemes.append("%d fichier(s) non commité(s) dans le dépôt public"
                         % len(lignes))
    else:
        print("\n1. dépôt public propre : rien en attente")

    # 2. chaque source de construction est identique au privé NEUTRALISÉ
    declarations = charger_declarations()
    print("\n2. les sources qui construisent l'exe, comparées au privé "
          "NEUTRALISÉ")
    print("   (déclarations lues : %d fichier(s) dans "
          "outils/secrets_injectes.json)" % len(declarations))
    for rel in SOURCES:
        prive, publie = lire(os.path.join(BASE, rel)), \
            lire(os.path.join(PUBLIC, rel))
        if prive is None:
            print("   %-38s ABSENT côté privé" % rel)
            continue
        if publie is None:
            print("   %-38s ABSENT du dépôt public" % rel)
            problemes.append("%s absent du dépôt public" % rel)
            continue

        regles = declarations.get(rel, {})
        attendu, manquants = neutraliser(prive, regles)
        attendu = attendu.replace("\r\n", "\n")
        for nom in manquants:
            print("   %-38s ⚠ « %s » déclaré mais introuvable côté privé"
                  % (rel, nom))
            problemes.append("%s : la déclaration « %s » ne correspond à "
                             "aucune affectation du fichier privé "
                             "(périmée ou renommée)" % (rel, nom))

        # La valeur publique doit être EXACTEMENT la valeur neutre : pas
        # « différente du secret », égale à l'attendu. Ce contrôle-là est
        # redondant avec la comparaison ci-dessous — c'est voulu : il dit
        # QUOI ne va pas, là où la comparaison dirait seulement « diverge ».
        for nom, valeur in valeurs_publiques(publie, regles).items():
            neutre = regles[nom].get("valeur_publique_attendue", "")
            if valeur is None:
                print("   %-38s ⚠ « %s » absent de l'arbre PUBLIÉ"
                      % (rel, nom))
                problemes.append("%s : « %s » absent de l'arbre publié"
                                 % (rel, nom))
            elif valeur != neutre:
                print("   %-38s 🛑 « %s » vaut une valeur INATTENDUE "
                      "(%d car.), on exige %r" % (rel, nom, len(valeur),
                                                  neutre))
                problemes.append(
                    "%s : « %s » ne porte pas la valeur neutre attendue — "
                    "c'est ainsi qu'un secret partirait" % (rel, nom))

        if attendu == publie:
            n = len([k for k in regles if not k.startswith("_")])
            print("   %-38s conforme%s" % (rel,
                  " (%d secret(s) neutralisé(s))" % n if n else ""))
        else:
            ecart = sum(1 for a, b in zip(attendu.splitlines(),
                                          publie.splitlines()) if a != b)
            ecart += abs(len(attendu.splitlines()) - len(publie.splitlines()))
            print("   %-38s ⚠ DIVERGE (~%d lignes)" % (rel, ecart))
            problemes.append("%s diverge du privé neutralisé (~%d lignes)"
                             % (rel, ecart))

    # 3. la version de l'arbre PUBLIÉ
    v_prive = version_de(lire(os.path.join(BASE, "compagnon/compagnon.py")))
    v_public = version_de(lire(os.path.join(PUBLIC, "compagnon/compagnon.py")))
    print("\n3. VERSION_COMPAGNON")
    print("   arbre privé (celui qui construit) : %s" % v_prive)
    print("   arbre PUBLIÉ (celui qu'on tague)  : %s" % v_public)
    if attendue:
        print("   version publiée demandée          : %s" % attendue)
        if v_public != attendue:
            problemes.append("l'arbre public annonce %s, on publie %s"
                             % (v_public, attendue))
    elif v_prive != v_public:
        problemes.append("l'arbre public annonce %s, le privé %s"
                         % (v_public, v_prive))

    # 4. LE BALAYAGE — indépendant de toute déclaration
    # Les trois contrôles ci-dessus supposent qu'on ait PENSÉ à déclarer le
    # bon secret. C'est exactement l'hypothèse qui a lâché le 29/07. Celui-ci
    # ne suppose rien : il cherche des MOTIFS, sur TOUTES les extensions
    # (l'ancien contrôle du zip ne regardait que cinq d'entre elles et
    # laissait passer les .py — le fichier même qui portait le webhook).
    print("\n4. balayage de secrets dans l'arbre public "
          "(toutes extensions, sans liste)")
    trouves = balayer_arbre(PUBLIC)
    print("   %d motif(s) trouvé(s)" % len(trouves))
    for fichier, etiquette, extrait, ligne in trouves:
        print("   🛑 %s:%d — %s : %s" % (fichier, ligne, etiquette, extrait))
        problemes.append("SECRET dans %s ligne %d (%s)"
                         % (fichier, ligne, etiquette))

    if "--avec-historique" in sys.argv:
        from balayer_secrets import balayer_historique
        print("\n5. balayage de l'HISTORIQUE git du dépôt public")
        trouves_h, lus = balayer_historique(PUBLIC)
        if trouves_h is None:
            print("   (pas un dépôt git)")
        else:
            print("   %d blob(s) texte lu(s), %d motif(s)"
                  % (lus, len(trouves_h)))
            for fichier, etiquette, extrait, ligne in trouves_h:
                print("   🛑 %s:%d — %s : %s"
                      % (fichier, ligne, etiquette, extrait))
                problemes.append("SECRET dans l'historique : %s (%s)"
                                 % (fichier, etiquette))

    print("\n" + "=" * 66)
    if problemes:
        print("🛑 REFUS DE TAGUER — %d point(s) :" % len(problemes))
        for p in problemes:
            print("   - %s" % p)
        return 1
    print("✅ l'arbre publié correspond à ce qui a été construit, "
          "et ne porte aucun secret.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
