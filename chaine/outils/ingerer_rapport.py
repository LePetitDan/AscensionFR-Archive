# -*- coding: utf-8 -*-
"""
ingerer_rapport.py — transforme un rapport « Signaler un souci » collé en
entrées de correction pour DB_SortsCorrections.lua.

FLUX
----
1. En jeu : /afr -> « Signaler un souci » -> « Copier pour partager ».
2. Dépose les rapports dans   traduction/rapports/   — TOUS les .txt y sont
   lus (sauf ids_*.txt, réservés aux listes d'IDs). Donc : télécharge les
   fichiers joints sur Discord directement dans ce dossier, n'importe quel
   nom ; ou colle un message brut dans rapport.txt comme avant.
3. python outils/ingerer_rapport.py            (ou --dry pour prévisualiser)
4. /reload en jeu -> survole les sorts -> ils doivent passer en français.

COMMENT ÇA MARCHE
-----------------
- Le rapport contient, pour chaque sort en échec, son ID + le texte anglais
  RÉELLEMENT AFFICHÉ par Ascension (donc à jour, alors que le modèle stocké a
  pu diverger). On prend ce texte live comme nouveau modèle DE, et on en génère
  la traduction française D.
- Le nom (N) est récupéré dans DB_Sorts.lua : sans lui, l'entrée de correction
  — qui REMPLACE toute l'entrée — perdrait le nom du sort.
- La traduction réutilise le traducteur du gisement (Google gratuit + protection
  du vocabulaire WoW, § tokens).
- Les entrées sont AJOUTÉES à DB_SortsCorrections.lua, sans doublonner (un ID
  déjà corrigé n'est pas réécrit).

LIMITES (assumées)
------------------
- Le texte anglais est pris tel qu'AFFICHÉ : les valeurs sont résolues (« 10% »
  et non « $s1% »). Parfait pour les buffs à valeur FIXE (parchemins de zone…).
  Pour un sort dont la valeur varie selon le perso, la correction ne vaut que
  pour cette valeur — sinon repli SÛR en anglais (jamais de texte cassé).
- Cas « buff != sort » (l'aura affiche un effet différent du lancement) : non
  gérés automatiquement (rien n'est écrit pour eux).
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from traduire_gisement import traduire  # noqa: E402  (Google + glossaire WoW)
from chemin_client import (JEU, exiger_client,  # noqa: E402
                           client_present, CODE_CLIENT_ABSENT)
from ecriture_sure import ecrire_json  # noqa: E402

DBDIR = os.path.join(JEU, "Interface", "AddOns", "AscensionFR", "DB")
DB_SORTS = os.path.join(DBDIR, "DB_Sorts.lua")
CORRECTIONS = os.path.join(DBDIR, "DB_SortsCorrections.lua")
DOSSIER_RAPPORTS = os.path.join(BASE, "rapports")
TRADUCTIONS = os.path.join(BASE, "traductions")
PROPOSITIONS = os.path.join(TRADUCTIONS, "propositions_joueurs.json")


def propositions_du_rapport(rapport):
    """Blocs « --- Propositions --- » (fenêtre « Signaler » des joueurs) :
    - <cible> | <id|nomCadre> | actuel=<...> | propose=<...>."""
    dans, out = False, []
    for ligne in rapport.splitlines():
        if ligne.startswith("--- Propositions"):
            dans = True
            continue
        if ligne.startswith("---"):
            dans = False
            continue
        if not dans:
            continue
        m = re.match(r"^\s*- (.+?) \| (.*?) \| actuel=(.*?) \| propose=(.*)$",
                     ligne)
        if m:
            cible, ident, actuel, propose = (x.strip() for x in m.groups())
            if propose:
                out.append((cible, ident, actuel, propose))
    return out


def ingerer_propositions(rapport):
    """Range les propositions joueurs dans propositions_joueurs.json (vote).
    Même fichier/format que diagnostiquer_signalements -> tout se cumule."""
    props = propositions_du_rapport(rapport)
    if not props:
        return 0
    base = {}
    if os.path.exists(PROPOSITIONS):
        with open(PROPOSITIONS, encoding="utf-8") as f:
            base = json.load(f)
    for cible, ident, actuel, propose in props:
        if ident.isdigit():
            cle = "%s:%s:%s" % (cible, ident, actuel[:60])
        else:
            cle = "%s:%s" % (cible or "texte", (actuel or ident)[:60])
        e = base.setdefault(cle, {
            "cible": cible,
            "id": int(ident) if ident.isdigit() else None,
            "actuel": actuel, "propositions": {}})
        e["propositions"][propose] = e["propositions"].get(propose, 0) + 1
    # Atomique (programme 31, bloc B) : ce fichier de votes se réécrit en
    # entier — une coupure au milieu le tronquait.
    ecrire_json(PROPOSITIONS, base)
    return len(props)


def fichiers_rapports():
    """Tous les .txt du dossier rapports/ — on peut donc y DÉPOSER directement
    les fichiers téléchargés depuis Discord, sans copier-coller. ids_*.txt est
    exclu : ce sont des listes d'IDs (recolter_builder.py), pas des rapports."""
    if not os.path.isdir(DOSSIER_RAPPORTS):
        return []
    return [os.path.join(DOSSIER_RAPPORTS, nom)
            for nom in sorted(os.listdir(DOSSIER_RAPPORTS))
            if nom.lower().endswith(".txt")
            and not nom.lower().startswith("ids_")]

RE_COULEUR = re.compile(r"\|c[0-9a-fA-F]{8}|\|r")
RE_DUREE = re.compile(r"restantes?\s*$|^\d+\s+(sec|secs?|min|mins?|heure|heures|"
                      r"jour|jours|seconde|secondes|minute|minutes)\b")


def retirer_couleurs(t):
    return RE_COULEUR.sub("", t)


def est_duree(t):
    return bool(RE_DUREE.search(t.strip()))


def choisir_description(brut):
    """Reconstruit les lignes d'info-bulle et renvoie la description anglaise.

    Une nouvelle ligne d'info-bulle commence par deux espaces (préfixe du
    rapport) ; une ligne sans préfixe est une continuation (\\n interne)."""
    tooltips = []
    for ligne in brut:
        if ligne.startswith("  "):
            tooltips.append(ligne[2:])
        elif tooltips:
            tooltips[-1] += "\n" + ligne
    candidats = []
    for t in tooltips:
        t = retirer_couleurs(t).rstrip()
        if not t or est_duree(t):
            continue
        # Doit ressembler à de l'anglais : au moins 3 mots alphabétiques.
        if len(re.findall(r"[A-Za-z]{2,}", t)) < 3:
            continue
        candidats.append(t)
    return max(candidats, key=len) if candidats else None


def lire_echecs(rapport, genre):
    """{id: description} pour TOUTES les sections « Échecs d'alignement <genre> »
    du fichier — on peut donc coller plusieurs rapports (tout un salon Discord)
    d'un coup. Un ID vu dans plusieurs rapports : le dernier gagne (même sort)."""
    marqueur = "--- Échecs d'alignement " + genre
    dans, entrees, courant = False, {}, None
    for ligne in rapport.splitlines():
        if ligne.startswith(marqueur):
            dans, courant = True, None
            continue
        if ligne.startswith("---"):          # toute autre section = fin de bloc
            dans, courant = False, None
            continue
        if not dans:
            continue
        m = re.match(r"^(\d+)\s*:\s*(.*)$", ligne)
        if m:
            courant = m.group(1)
            entrees[courant] = []
            if m.group(2).strip():
                entrees[courant].append("  " + m.group(2))
        elif courant is not None:
            entrees[courant].append(ligne)
    return {i: d for i, d in ((i, choisir_description(b))
                              for i, b in entrees.items()) if d}


def ids_signalements(rapport):
    """IDs des sections « Signalements » (journal du bouton « Signaler un
    souci ») — jamais ingérées jusqu'ici : 85 IDs perdus recensés le
    21/07/2026. Format : « - ID | Nom / texte... | date | ... | sort ».
    On n'extrait QUE l'ID et la catégorie finale (sort/objet) : le texte de
    la ligne est trop malmené pour servir de modèle, recuperer_db.py ira
    chercher l'anglais propre sur db.ascension.gg."""
    dans, sorts, objets = False, set(), set()
    for ligne in rapport.splitlines():
        if ligne.startswith("--- Signalements"):
            dans = True
            continue
        if ligne.startswith("---"):
            dans = False
            continue
        if not dans:
            continue
        m = re.match(r"^\s*- (\d+) \|", ligne)
        if not m:
            continue
        categorie = ligne.rsplit("|", 1)[-1].strip()
        if categorie == "objet":
            objets.add(m.group(1))
        elif categorie in ("sort", "texte"):
            sorts.add(m.group(1))
    return sorts, objets


def noms_depuis_db(ids):
    """N (et R) de DB_Sorts.lua pour ces IDs."""
    besoin, noms = set(ids), {}
    with open(DB_SORTS, encoding="utf-8") as f:
        for ligne in f:
            m = re.match(r"^DB\[(\d+)\]=", ligne)
            if m and m.group(1) in besoin:
                n = re.search(r',N="((?:\\.|[^"\\])*)"', ligne)
                r = re.search(r',R="((?:\\.|[^"\\])*)"', ligne)
                noms[m.group(1)] = (n.group(1) if n else None,
                                    r.group(1) if r else None)
    return noms


def ids_deja_corriges():
    if not os.path.exists(CORRECTIONS):
        return set()
    with open(CORRECTIONS, encoding="utf-8") as f:
        contenu = f.read()
    # Un ID peut être corrigé par remplacement (DB[id]={…}) ou par ajout d'un
    # modèle secondaire (aura(id, …)).
    return (set(re.findall(r"^DB\[(\d+)\]=", contenu, re.M))
            | set(re.findall(r"aura\((\d+),", contenu)))


def echapper_lua(s):
    """Chaîne prête pour "..." en Lua : \\ et " échappés, sauts de ligne -> \\n."""
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return s.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")


def main():
    # DÉCOUPAGE ENTRÉE / TRADUCTION / SORTIE (programme 33, bloc A). Comme
    # l'étape 5 : la dépendance au client est un besoin de FICHIERS (lire
    # DB_Sorts pour la dédup, écrire DB_SortsCorrections). --sans-pose (le
    # cloud) : DB_Sorts vient de l'arbre fourni (ASCENSIONFR_JEU), la
    # TRADUCTION des corrections d'alignement se fait, et l'écriture dans
    # DB_SortsCorrections est SAUTÉE — ses lignes partent dans un fichier
    # d'attente qui revient chez Dan (c'est lui qui pose).
    sans_pose = ("--sans-pose" in sys.argv
                 or os.environ.get("ASCENSIONFR_SANS_POSE") == "1")
    if sans_pose:
        if not client_present():
            print("MOISSON ABSENTE — --sans-pose exige un arbre fourni via "
                  "ASCENSIONFR_JEU (DB_Sorts pour la dédup). Arrêt.")
            sys.stdout.flush()
            sys.exit(CODE_CLIENT_ABSENT)
    else:
        # Sans client, la dédup lirait « aucun ID déjà corrigé » en silence,
        # doublonnerait, puis planterait à l'append — APRÈS le réseau
        # (programme 31, bloc A).
        exiger_client("ingerer_rapport (étape 2 — signalements)")
    dry = "--dry" in sys.argv
    fichiers = fichiers_rapports()
    if not fichiers:
        os.makedirs(DOSSIER_RAPPORTS, exist_ok=True)
        print("Dépose les rapports (.txt) dans : %s" % DOSSIER_RAPPORTS)
        return 1
    morceaux = []
    for chemin in fichiers:
        with open(chemin, encoding="utf-8") as f:
            morceaux.append(f.read())
        print("  lu : %s" % os.path.basename(chemin))
    rapport = "\n".join(morceaux)

    # Sections « Signalements » (jamais lues avant le 21/07/2026) : on écrit
    # les IDs dans deux listes pour recuperer_db.py — lui seul sait aller
    # chercher un texte anglais PROPRE (la ligne de signalement est malmenée).
    sig_sorts, sig_objets = ids_signalements(rapport)
    deja_sig = ids_deja_corriges()
    sig_sorts -= deja_sig
    if sig_sorts or sig_objets:
        for nom, ids in (("ids_signalements_sorts.txt", sig_sorts),
                         ("ids_signalements_objets.txt", sig_objets)):
            chemin = os.path.join(DOSSIER_RAPPORTS, nom)
            with open(chemin, "w", encoding="utf-8") as f:
                f.write("# IDs extraits des sections Signalements — à passer"
                        " à recuperer_db.py --fichier\n")
                f.write("\n".join(sorted(ids, key=int)) + "\n")
        print("Signalements : %d sort(s) et %d objet(s) -> "
              "rapports\\ids_signalements_*.txt (pour recuperer_db.py)"
              % (len(sig_sorts), len(sig_objets)))
        # L'Atelier du bureau (exe FIGÉ) ne connaît pas d'étape recuperer_db :
        # on l'enchaîne ICI, pour que la chaîne « n'oublie plus rien » sans
        # recompiler l'exe. Volumes attendus minuscules (le retard est purgé,
        # 21/07/2026) ; recuperer_db déduplique et a son cache disque.
        # Dans le cloud (--sans-pose) : recuperer_db écrit DB_SortsCorrections
        # (client) — on le saute et on le dit ; ce petit poste reste chez Dan
        # (les signalements sont rares — programme 33, bloc A/E).
        if sans_pose:
            print("(--sans-pose : recuperer_db des signalements sauté — "
                  "reste chez Dan, volume minuscule)")
        if not dry and not sans_pose:
            for drapeaux, nom in (([], "ids_signalements_sorts.txt"),
                                  (["--objets"], "ids_signalements_objets.txt")):
                chemin = os.path.join(DOSSIER_RAPPORTS, nom)
                import subprocess
                subprocess.run(
                    [sys.executable,
                     os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "recuperer_db.py")]
                    + drapeaux + ["--fichier", chemin],
                    cwd=BASE, check=False)

    # Propositions de traduction des joueurs (fenêtre « Signaler ») -> vote
    # dans propositions_joueurs.json (à arbitrer côté projet).
    if not dry:
        n_prop = ingerer_propositions(rapport)
        if n_prop:
            print("Propositions de traduction (joueurs) ingérées : %d "
                  "-> traductions\\propositions_joueurs.json" % n_prop)

    echecs = lire_echecs(rapport, "S")
    # Garde-fou : jamais un morceau de RAPPORT comme texte de sort. Un collage
    # manuel mal structuré (époque 1.7.4) a fait ingérer l'en-tête du rapport
    # comme description de 3 sorts — corrections poison qui ne s'alignaient
    # jamais, purgées le 20/07/2026. Si un texte contient l'en-tête, c'est le
    # découpage qui a déraillé, pas un sort.
    MARQUEURS_RAPPORT = ("Signalement Ascension FR", "AscensionFR 1.",
                         "Client : 3.3.5", "Échecs d'alignement")
    pollues = [i for i, t in echecs.items()
               if any(m in t for m in MARQUEURS_RAPPORT)]
    for i in pollues:
        print("  ! ignoré (texte de rapport, pas de sort) : %s" % i)
        del echecs[i]
    if not echecs:
        # RIEN À FAIRE n'est pas UN ÉCHEC (29/07/2026). Depuis que
        # l'Atelier honore les codes retour (bloc E), ce cas parfaitement
        # normal — des rapports sans section « Échec d'alignement » —
        # affichait un bandeau ROUGE. Un contrôle qui crie pour rien ne
        # se lit plus au bout d'une semaine.
        print("Aucun « Échec d'alignement S » dans les rapports : rien à "
              "corriger (ce n'est pas une erreur).")
        print("@@BILAN " + json.dumps({"tentees": 0, "traduites": 0,
                                       "refusees": 0, "ecartees": 0}))
        return 0

    deja = ids_deja_corriges()
    a_faire = {i: d for i, d in echecs.items() if i not in deja}
    # Le total « en échec » monte sans fin (on relit TOUS les rapports depuis
    # le début, ils ne sont jamais rangés). C'est donc le nombre de NOUVEAUX
    # qui compte : il passe en premier, le reste devient de l'historique.
    print("Nouveaux sorts à corriger : %d   (%d signalés depuis le début, "
          "dont %d déjà corrigés)"
          % (len(a_faire), len(echecs), len(echecs) - len(a_faire)))
    if not a_faire:
        print("@@BILAN " + json.dumps(
            {"tentees": 0, "traduites": 0, "refusees": 0,
             "ecartees": len(echecs)}))
        return 0

    lignes, echoues = [], []
    for id_ in sorted(a_faire):
        desc = a_faire[id_]
        fr = traduire(desc)
        if not fr:
            echoues.append(id_)
            continue
        # On AJOUTE le texte live comme 2e modèle (aura), sans écraser le modèle
        # de lancement déjà traduit dans DB_Sorts. L'aligneur essaie les deux.
        lignes.append('aura(%s, "%s", "%s")'
                      % (id_, echapper_lua(desc), echapper_lua(fr)))
        print("  %s  %s -> %s" % (id_, desc.split("\n")[0][:45],
                                  fr.split("\n")[0][:45]))

    if echoues:
        print("! traduction échouée (à faire main) : %s" % ", ".join(echoues))
    # Les comptes du passage (programme 31, bloc F ; en_attente au 33).
    print("@@BILAN " + json.dumps(
        {"tentees": len(a_faire), "traduites": len(lignes),
         "refusees": len(echoues),
         "ecartees": len(echecs) - len(a_faire),
         "en_attente": len(lignes) if sans_pose else 0}))
    if not lignes:
        # Là encore : rien à ÉCRIRE. Les échecs de traduction viennent
        # d'être listés ci-dessus, ils sont donc visibles ; en faire un
        # code retour non nul peindrait en rouge un passage où il ne
        # restait que des textes que Google refuse toujours de la même
        # façon (la famille des rejets déterministes du bloc E).
        print("Rien de nouveau à écrire dans DB_SortsCorrections.lua.")
        return 0
    if dry:
        print("\n--dry : rien écrit. %d entrée(s) prêtes." % len(lignes))
        return 0

    # CLOUD (--sans-pose) : la pose dans DB_SortsCorrections est SAUTÉE ;
    # les lignes aura() partent en attente et reviennent chez Dan.
    if sans_pose:
        attente = os.path.join(BASE, "traductions",
                               "corrections_en_attente.txt")
        with open(attente, "w", encoding="utf-8") as f:
            f.write("\n".join(lignes) + "\n")
        print("\n%d ligne(s) aura() EN ATTENTE DE POSE -> %s (reviennent "
              "chez Dan par le pont)."
              % (len(lignes), os.path.relpath(attente, BASE)))
        return 0

    # S'assure que le helper aura() (et le local DB) existent dans le fichier.
    contenu = ""
    if os.path.exists(CORRECTIONS):
        with open(CORRECTIONS, encoding="utf-8") as f:
            contenu = f.read()
    entete = ""
    if "local function aura(" not in contenu:
        entete = ("local DB = AscensionFR.DB.Sorts\n"
                  "local function aura(id, de2, d2)\n"
                  "    if DB[id] then DB[id].DE2 = de2; DB[id].D2 = d2 end\n"
                  "end\n")
    bloc = ("\n-- --- Ingéré depuis un rapport (ingerer_rapport.py) ---\n"
            + entete + "\n".join(lignes) + "\n")
    with open(CORRECTIONS, "a", encoding="utf-8") as f:
        f.write(bloc)
    print("\n%d entrée(s) ajoutée(s) à DB_SortsCorrections.lua." % len(lignes))
    print("Vérifie la syntaxe, puis /reload en jeu pour tester.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
