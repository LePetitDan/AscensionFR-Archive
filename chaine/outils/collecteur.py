# -*- coding: utf-8 -*-
"""
Atelier Ascension FR — l'outil PERSONNEL de Dan (jamais distribué).

Un double-clic sur l'icône du bureau et TOUTE la chaîne tourne, sans terminal.
Remplace à la fois l'ancien « Collecteur » et l'ancien « Traduction FR » :
  1. aspiration : télécharge les rapports envoyés par les joueurs (salon Discord)
  2. signalements : ingère les sorts signalés et écrit les corrections
  3. caches : verse les textes de jeu envoyés par les joueurs dans l'usine
  4. usine : traduit tout le nouveau (tes découvertes + les caches des joueurs)
            et régénère les bases de l'addon
  5. récolte : traduit les dialogues, PNJ et quêtes croisés en anglais par les
            joueurs. APRÈS l'usine, exprès : elle ne remplit ainsi que les
            trous qui restent vraiment, au lieu de doublonner avec les bases
            que l'usine vient de régénérer.
  6. vérification : compile les bases Lua (lupa) — rien de cassé
Le journal défile en direct, et un résumé s'affiche à la fin.
"""
import os
import re
import subprocess
import sys
import threading
import time

import customtkinter as ctk

BASE = r"D:\AscensionFR\WorkFlow"
sys.path.insert(0, os.path.join(BASE, "outils"))
from chemin_client import DB as _DB  # noqa: E402
import sante_atelier  # noqa: E402  (le vert qui ment — programme 31)
CORRECTIONS = os.path.join(_DB, "DB_SortsCorrections.lua")
COMMUNAUTE = os.path.join(_DB, "DB_Communaute.lua")
# Régénéré par l'étape « Sorts en attente » (--sorts) : à vérifier aussi.
DB_SORTS = os.path.join(_DB, "DB_Sorts.lua")

FOND = "#0e1013"
PANNEAU = "#16191d"
LISERE = "#23272d"
ACCENT = "#e8c25a"
TEXTE = "#eceff3"
DISCRET = "#8b929c"
VERT = "#2fb46a"
ORANGE = "#e8a33d"
ROUGE = "#e05252"


def processus_vivant(pid):
    """Ce numéro de processus tourne-t-il encore ? (verrou orphelin)"""
    try:
        sortie = subprocess.run(
            ["tasklist", "/FI", "PID eq %d" % pid, "/NH"],
            capture_output=True, text=True, timeout=15,
            creationflags=0x08000000).stdout or ""
        return str(pid) in sortie
    except Exception:
        return True          # dans le doute, on ne double pas l'atelier


def trouver_python():
    """Le Collecteur est un .exe : il lance les outils avec le VRAI Python de
    la machine (sys.executable serait l'exe lui-même)."""
    import shutil
    candidats = [shutil.which("python"), shutil.which("py"),
                 os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python"
                                    r"\Python312\python.exe")]
    for c in candidats:
        if c and os.path.exists(c):
            return c
    return None


def ressource(nom):
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "compagnon")
    return os.path.join(base, "assets", nom)


class Atelier(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Atelier Ascension FR")
        self.geometry("680x600")
        self.minsize(600, 500)
        self.depart_progres = None          # (instant, compteur) du chrono
        self.etape_en_cours = ""
        self.configure(fg_color=FOND)
        try:
            self.iconbitmap(ressource("logo_atelier.ico"))
        except Exception:
            pass

        ctk.CTkLabel(self, text="⌃  Atelier", text_color=ACCENT,
                     font=ctk.CTkFont(size=20, weight="bold")
                     ).pack(anchor="w", padx=24, pady=(18, 0))
        ctk.CTkLabel(self, text="Rapports des joueurs ET tes découvertes → "
                     "français, d'un seul clic.",
                     text_color=DISCRET).pack(anchor="w", padx=24)

        cadre = ctk.CTkFrame(self, corner_radius=8, fg_color=PANNEAU,
                             border_width=1, border_color=LISERE)
        cadre.pack(fill="both", expand=True, padx=24, pady=12)
        self.journal = ctk.CTkTextbox(cadre, fg_color=PANNEAU,
                                      text_color=TEXTE, wrap="word",
                                      font=ctk.CTkFont(family="Consolas",
                                                       size=12))
        self.journal.pack(fill="both", expand=True, padx=8, pady=8)
        self.journal.configure(state="disabled")

        # Bloc d'avancement : l'essentiel se lit ICI, d'un coup d'œil. Le
        # journal du dessus défile trop vite pour être suivi.
        avance = ctk.CTkFrame(self, fg_color="transparent")
        avance.pack(fill="x", padx=24, pady=(0, 6))
        self.lbl_etape = ctk.CTkLabel(
            avance, text="Démarrage…", text_color=TEXTE, anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_etape.pack(fill="x")
        self.barre = ctk.CTkProgressBar(avance, height=14, corner_radius=7,
                                        fg_color=LISERE,
                                        progress_color=ACCENT)
        self.barre.pack(fill="x", pady=(6, 4))
        self.barre.set(0)
        self.lbl_detail = ctk.CTkLabel(avance, text="", text_color=DISCRET,
                                       anchor="w",
                                       font=ctk.CTkFont(size=12))
        self.lbl_detail.pack(fill="x")

        self.lbl_etat = ctk.CTkLabel(self, text="", text_color=DISCRET,
                                     wraplength=620, justify="left")
        self.lbl_etat.pack(pady=(4, 4))
        self.btn = ctk.CTkButton(self, text="⟳  Relancer", height=36,
                                 corner_radius=6, fg_color=ACCENT,
                                 hover_color="#d9b44e", text_color="#15130c",
                                 font=ctk.CTkFont(size=14, weight="bold"),
                                 state="disabled", command=self.lancer)
        self.btn.pack(fill="x", padx=24, pady=(0, 16))

        self.after(400, self.lancer)

    def log(self, texte):
        def faire():
            self.journal.configure(state="normal")
            self.journal.insert("end", texte + "\n")
            self.journal.see("end")
            self.journal.configure(state="disabled")
        self.after(0, faire)

    def etat(self, texte, couleur=DISCRET):
        self.after(0, lambda: self.lbl_etat.configure(text=texte,
                                                      text_color=couleur))

    def etape(self, numero, sur, titre):
        """Nouvelle étape : la barre repart en mode « va-et-vient » tant qu'on
        ne sait pas compter (aspiration, ingestion), puis devient une vraie
        jauge dès que l'usine annonce ses totaux."""
        self.depart_progres = None          # le chrono repart à chaque étape
        self.etape_en_cours = "%d/%d" % (numero, sur)

        def afficher():
            self.lbl_etape.configure(text="Étape %d/%d — %s"
                                     % (numero, sur, titre))
            self.lbl_detail.configure(text="")
            self.barre.configure(mode="indeterminate")
            self.barre.start()
        self.after(0, afficher)

    def fin_etapes(self, reussi=True):
        def afficher():
            self.barre.stop()
            self.barre.configure(mode="determinate")
            self.barre.set(1 if reussi else 0)
            self.lbl_etape.configure(text="Terminé" if reussi else "Arrêté")
            self.lbl_detail.configure(text="")
        self.after(0, afficher)

    @staticmethod
    def duree_lisible(secondes):
        """« 40 s », « 3 min », « 1 h 05 » — jamais « 187.4 secondes »."""
        secondes = int(secondes)
        if secondes < 60:
            return "%d s" % max(secondes, 1)
        if secondes < 3600:
            return "%d min" % round(secondes / 60.0)
        return "%d h %02d" % (secondes // 3600, (secondes % 3600) // 60)

    def maj_progres(self, texte):
        """Ligne « @@P fait/total libellé » émise par l'usine."""
        compte, _, libelle = texte.partition(" ")
        fait, _, total = compte.partition("/")
        try:
            fait, total = int(fait), int(total)
        except ValueError:
            return
        if total <= 0:
            return

        # Repère de départ, posé au PREMIER texte réellement traité : le
        # décompte doit refléter la vitesse de traduction, pas inclure le
        # temps de préparation qui la précède.
        if self.depart_progres is None or fait <= 1:
            self.depart_progres = (time.time(), fait)
        debut, fait_debut = self.depart_progres

        ecoule = time.time() - debut
        avances = fait - fait_debut
        estimation, cadence = "", ""
        if avances > 0 and ecoule > 3:
            par_seconde = avances / ecoule
            if par_seconde > 0:
                estimation = ("  ·  reste ≈ %s"
                              % self.duree_lisible((total - fait)
                                                   / par_seconde))
                cadence = "  ·  %.1f textes/s" % par_seconde

        def afficher():
            self.barre.stop()
            self.barre.configure(mode="determinate")
            self.barre.set(float(fait) / total)
            self.lbl_detail.configure(
                text="%d / %d textes  (%d %%)%s%s"
                     % (fait, total, fait * 100 // total, estimation, cadence))
            self.lbl_etape.configure(
                text="Étape %s — %s" % (self.etape_en_cours, libelle[:46]))
        self.after(0, afficher)

    def lancer(self):
        self.btn.configure(state="disabled", text="⏳  Travail en cours…")
        # Le bilan du lancement PRÉCÉDENT restait affiché en vert pendant que
        # le nouveau tournait : on croyait le travail fini alors qu'il était
        # à 13 %. On repart d'une ardoise propre.
        self.etat("")
        # Le journal, lui, GARDE l'historique (pratique pour comparer deux
        # passages). Mais sans séparateur on relisait les chiffres du passage
        # PRÉCÉDENT en croyant qu'ils étaient ceux du dernier — vécu le 20\07 :
        # « à traiter : 59 » en haut, « rien de nouveau » en bas. D'où la barre.
        if getattr(self, "deja_lance", False):
            self.log("\n" + "─" * 60)
            self.log("   NOUVEAU PASSAGE — %s" % time.strftime("%d/%m à %Hh%M"))
            self.log("─" * 60)
        self.deja_lance = True
        threading.Thread(target=self.travail, daemon=True).start()

    def executer_flux(self, commande, env):
        """Lance une commande et journalise sa sortie EN DIRECT (ligne à
        ligne). Rend (sortie, code retour) — le code retour est LA vérité
        sur l'étape (bloc E, 29/07/2026) : avant, un crash pouvait finir
        sur un bandeau vert parce que seul le texte du résumé était lu."""
        lignes = []
        p = subprocess.Popen(commande, cwd=BASE, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True,
                             encoding="utf-8", errors="replace", env=env,
                             creationflags=0x08000000)
        for ligne in p.stdout:
            ligne = ligne.rstrip()
            if ligne.startswith("@@P "):        # avancement, pas du journal
                self.maj_progres(ligne[4:])
                continue
            self.log(ligne)
            lignes.append(ligne)
        p.wait()
        return "\n".join(lignes), p.returncode

    def travail(self):
        py = trouver_python()
        if not py:
            self.etat("Python introuvable sur cette machine.", ROUGE)
            self.after(0, lambda: self.btn.configure(state="normal",
                                                     text="⟳  Relancer"))
            return
        # Un seul atelier à la fois : deux usines en parallèle écrivent les
        # MÊMES fichiers de traductions et se marchent dessus (vécu le
        # 18/07 : deux fenêtres ouvertes, du travail perdu).
        verrou = self.prendre_verrou()
        if not verrou:
            self.log("! Un atelier tourne déjà (autre fenêtre).")
            self.etat("Un atelier tourne déjà — ferme l'autre fenêtre, ou "
                      "attends qu'il ait fini.", ORANGE)
            self.after(0, lambda: self.btn.configure(state="normal",
                                                     text="⟳  Relancer"))
            return
        try:
            self.travail_protege(py)
        finally:
            self.rendre_verrou(verrou)

    def prendre_verrou(self):
        """Crée le fichier de verrou, ou None s'il est déjà pris par un
        atelier VIVANT (un verrou orphelin, laissé par un plantage, est
        récupéré : sinon l'outil resterait bloqué à jamais)."""
        chemin = os.path.join(BASE, ".atelier_en_cours")
        try:
            if os.path.exists(chemin):
                with open(chemin) as f:
                    pid = int((f.read() or "0").strip() or 0)
                if pid and pid != os.getpid() and processus_vivant(pid):
                    return None
            with open(chemin, "w") as f:
                f.write(str(os.getpid()))
            return chemin
        except Exception:
            return None

    def rendre_verrou(self, chemin):
        try:
            os.remove(chemin)
        except Exception:
            pass

    def ecrire_sante(self, etapes, verification=None, bilans=None,
                     verdicts=None):
        """Écrit rapports/atelier_sante.json — la santé du DERNIER passage,
        lue par banc_sante.py (bloc E, 29/07/2026). verification : 0 = les
        bases compilent, 1 = cassées, None = pas encore atteinte.
        Depuis le programme 31 (bloc F), la santé porte aussi les COMPTES
        (@@BILAN par étape) et les VERDICTS : vert ne veut plus dire
        « code retour zéro » mais « a fait son travail »."""
        try:
            import json as _json
            sante = {"date": time.strftime("%Y-%m-%d %H:%M"),
                     "etapes": dict(etapes)}
            if bilans:
                sante["bilans"] = {s: b for s, b in bilans.items() if b}
            if verdicts:
                sante["verdicts"] = {s: list(v)
                                     for s, v in verdicts.items()}
            if verification is not None:
                sante["etapes"]["verification_lua"] = verification
            chemin = os.path.join(BASE, "rapports", "atelier_sante.json")
            os.makedirs(os.path.dirname(chemin), exist_ok=True)
            with open(chemin, "w", encoding="utf-8") as f:
                _json.dump(sante, f, ensure_ascii=False, indent=1)
        except Exception as e:
            self.log("! santé non journalisée : %s" % e)

    def travail_protege(self, py):
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        # SANS ceci, Python met sa sortie en mémoire tampon quand elle est
        # redirigée : le journal restait vide pendant toute l'usine et on
        # croyait l'atelier planté alors qu'il travaillait.
        env["PYTHONUNBUFFERED"] = "1"
        sortie = ""
        etapes = [
            ("Aspiration des rapports du salon Discord",
             [py, os.path.join("outils", "aspirer_discord.py")]),
            ("Traduction des signalements",
             [py, os.path.join("outils", "ingerer_rapport.py")]),
            ("Caches des joueurs → usine",
             [py, os.path.join("outils", "ingerer_caches.py")]),
            ("Usine : traduction de tout le nouveau contenu",
             [py, "traducteur_fr.py", "--une-fois"]),
            # Les rapports transportent DEUX choses : les sorts mal affichés
            # (étape 2) et les dialogues/quêtes croisés en anglais. La 2e
            # moitié n'était ramassée par personne — 605 textes en attente au
            # 20\07, jamais traduits faute d'être branchés ici.
            ("Récolte : dialogues, PNJ et quêtes des rapports",
             [py, os.path.join("outils", "ingerer_recolte.py")]),
            # Le vocabulaire ARBITRÉ repasse sur les stores (bloc D3/E,
            # 29/07/2026) : c'était un geste manuel, donc oublié — les
            # arbitrages de Dan ne gouvernaient que 2 étapes sur 6. Placé
            # AVANT la traduction des sorts : chaque passage normalise ce
            # que les étapes du jour ont versé (et le moteur lui-même
            # protège désormais le glossaire — double filet).
            ("Vocabulaire arbitré : normalisation des stores",
             [py, os.path.join("outils", "appliquer_vocabulaire.py"),
              "--appliquer"]),
            # La file a_traduire/ des sorts (descriptions et noms jamais
            # traduits) n'était vidée par PERSONNE : --une-fois surveille et
            # récolte, mais seul --sorts traduit cette file. 9 282 sorts s'y
            # étaient entassés au 21/07 (dont « Testament de ténacité »,
            # signalé maintes fois par Dan) sans qu'aucune étape ne les
            # ramasse. Placé en dernier pour profiter des récoltes du jour.
            ("Sorts en attente : traduction des descriptions manquantes",
             [py, "traducteur_fr.py", "--sorts"]),
        ]
        # Les CODES RETOUR font foi (bloc E). Un échec n'interrompt pas la
        # chaîne (les étapes sont largement indépendantes, et le critique
        # d'une étape ne doit pas priver les autres de leur passage) mais
        # il est journalisé, versé dans rapports/atelier_sante.json (lu
        # par banc_sante.py) et le bandeau final ne peut PLUS être vert.
        sante_etapes = {}
        bilans = {}
        for numero, (titre, commande) in enumerate(etapes, 1):
            self.log("═══ %s ═══" % titre)
            self.etape(numero, len(etapes) + 1, titre)
            script = os.path.basename(commande[1])
            try:
                texte, code = self.executer_flux(commande, env)
            except Exception as e:
                self.log("! %s" % e)
                sante_etapes[script] = -1
                self.ecrire_sante(sante_etapes, verification=None,
                                  bilans=bilans)
                self.fin_etapes(reussi=False)
                self.etat("Échec : %s" % e, ROUGE)
                self.after(0, lambda: self.btn.configure(
                    state="normal", text="⟳  Relancer"))
                return
            sante_etapes[script] = code
            bilans[script] = sante_atelier.extraire_bilan(texte)
            if code != 0:
                self.log("! ÉTAPE EN ÉCHEC (code %d) — la suite continue, "
                         "le bandeau final le dira." % code)
            if not texte.strip():
                self.log("(rien)")
            sortie += texte

        # Vérification : les corrections écrites compilent-elles ?
        self.log("═══ Vérification de la base de corrections ═══")
        self.etape(len(etapes) + 1, len(etapes) + 1, "Vérification")
        try:
            # IMPÉRATIVEMENT lua51 : le client de WoW 3.3.5a tourne en
            # Lua 5.1. Le lupa par défaut est en Lua 5.5, qui ACCEPTE ce que
            # 5.1 refuse — mesuré : un fichier à 300 000 constantes passe en
            # 5.5 et échoue en 5.1 (« constant table overflow », la panne même
            # qui a bloqué la 3.4). Cette vérification annonçait donc
            # « rien de cassé » sur une base que le jeu n'aurait pas chargée.
            from lupa.lua51 import LuaRuntime
            lua = LuaRuntime(unpack_returned_tuples=True)
            # TOUS les fichiers que cet atelier écrit. N'en vérifier qu'une
            # partie, c'est laisser le reste casser le jeu au prochain
            # /reload (DB_Sorts est réécrit par l'étape « Sorts en attente »).
            for fichier in (CORRECTIONS, COMMUNAUTE, DB_SORTS):
                if not os.path.exists(fichier):
                    continue
                with open(fichier, encoding="utf-8") as f:
                    lua.compile(f.read())
                self.log("  %s : OK" % os.path.basename(fichier))
            self.log("Syntaxe Lua : OK — rien de cassé.")
            verif_ok = True
        except Exception as e:
            self.log("! ERREUR LUA : %s" % e)
            verif_ok = False

        # LES VERDICTS (programme 31, bloc F) : la couleur vient des
        # comptes, plus seulement des codes retour. Un passage qui avait
        # du travail et n'a rien traduit NE PEUT PLUS être vert.
        verdicts = {s: sante_atelier.verdict(c, bilans.get(s), s)
                    for s, c in sante_etapes.items()}
        couleur_globale = sante_atelier.verdict_global(verdicts)
        self.ecrire_sante(sante_etapes, verification=0 if verif_ok else 1,
                          bilans=bilans, verdicts=verdicts)

        # Résumé lisible. Les regex ne servent plus qu'au DÉTAIL du
        # bandeau — la couleur, elle, vient des CODES RETOUR (bloc E).
        m1 = re.search(r"(\d+) (?:rapport|fichier)\(s\) téléchargé", sortie)
        m2 = re.search(r"(\d+) entrée\(s\) ajoutée", sortie)
        m3 = re.search(r"(\d+) texte\(s\) de jeu versé", sortie)
        m4 = re.search(r"(\d+) entrée\(s\) prêtes", sortie)
        rapports = int(m1.group(1)) if m1 else 0
        entrees = int(m2.group(1)) if m2 else 0
        caches = int(m3.group(1)) if m3 else 0
        recolte = int(m4.group(1)) if m4 else 0
        etapes_ratees = sorted(
            "%s (%s)" % (s, verdicts[s][1]) for s in verdicts
            if verdicts[s][0] != sante_atelier.VERT)
        self.fin_etapes(reussi=verif_ok
                        and couleur_globale == sante_atelier.VERT)
        if couleur_globale == sante_atelier.ROUGE:
            self.etat("⚠ %d étape(s) en échec — %s — demande à Claude !"
                      % (len(etapes_ratees), " ; ".join(etapes_ratees)),
                      ROUGE)
        elif couleur_globale == sante_atelier.ORANGE:
            self.etat("⚠ Passage incomplet — %s — à surveiller."
                      % " ; ".join(etapes_ratees), ORANGE)
        elif not verif_ok:
            self.etat("⚠ Problème dans les corrections — demande à Claude !",
                      ROUGE)
        elif rapports == 0 and entrees == 0 and caches == 0 and recolte == 0:
            self.etat("Rien de nouveau aujourd'hui. Tout est à jour. ✓", VERT)
        else:
            bouts = []
            if rapports:
                bouts.append("%d fichier(s) collecté(s)" % rapports)
            if entrees:
                bouts.append("%d correction(s) de sort" % entrees)
            if caches:
                bouts.append("%d texte(s) de jeu des joueurs" % caches)
            if recolte:
                bouts.append("%d dialogue(s) et texte(s) de quête" % recolte)
            detail = ", ".join(bouts) if bouts else "contenu mis à jour"
            self.etat("Terminé : %s — tout est traduit et intégré. À publier "
                      "avec la prochaine version. ✓" % detail, VERT)
        self.after(0, lambda: self.btn.configure(state="normal",
                                                 text="⟳  Relancer"))


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    Atelier().mainloop()
