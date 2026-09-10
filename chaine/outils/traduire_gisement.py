# -*- coding: utf-8 -*-
"""
Traduit le gisement d'interface maison — gratuitement, et par petits bouts.

POURQUOI GOOGLE ET PAS UN MODÈLE
---------------------------------
Premier essai : 20 agents Sonnet sur 4 578 textes. Résultat : 933 000 jetons
brûlés, la limite de session atteinte, et **zéro** ligne traduite. Or ce sont
des étiquettes d'interface (« Abilities », « Account Prestige Level ») — du
formulaire, pas de la prose. Google le fait à 6 textes/seconde pour zéro
jeton, avec la protection des codes de format déjà écrite pour les sorts.
On garde le gros modèle pour ce qui le mérite : la prose (fiches de classe,
quêtes), pas les boutons.

REPRENDRE OÙ ON S'EST ARRÊTÉ
-----------------------------
Le fichier de sortie est réécrit tous les 200 textes. Interrompre (Ctrl+C,
extinction) ne perd rien : relancer reprend au premier texte non traduit.
`--limite N` permet de n'en faire qu'une tranche.

LE GLOSSAIRE
------------
Google ignore le vocabulaire de WoW (« Rage » -> « colère », « Focus » ->
« se concentrer »). On protège donc les termes du jeu comme on protège les
codes : ils sortent du texte avant traduction et rentrent en français après.
Le mécanisme existait déjà pour « $s1 » ; il vaut pour « Rage ».

Usage :
    python outils/traduire_gisement.py            # tout (~12 min)
    python outils/traduire_gisement.py --limite 500
    python outils/traduire_gisement.py --etat     # où en est-on ?
"""
import json
import os
import sys
import threading
import time
from concurrent import futures

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from traducteur_fr import traduire_google, PARALLELE  # noqa: E402

SOURCE = os.path.join(BASE, "a_traduire", "interface_maison.json")
SORTIE = os.path.join(BASE, "traductions", "gisement_brut.json")

def traduire(texte):
    """Traduit un texte, termes de jeu protégés. None si échec.

    NE PROTÈGE PLUS le glossaire ici : traduire_google le fait LUI-MÊME
    depuis le bloc D3 (29/07/2026). Le protéger une seconde fois posait
    un jeton §0§ que la couche interne prenait pour un jeton abîmé — et
    TOUT texte portant un terme du glossaire était refusé en silence.
    Régression mesurée au programme 30 (08/08/2026) : 133 refus sur 200
    au lot d'essai, Google renvoyant pourtant un français correct. Les
    refus « § » et le raccourci sans-réseau vivent dans traduire_google.
    """
    return traduire_google(texte)


def charger(chemin):
    if os.path.exists(chemin):
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    return {}


def sauver(chemin, d):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1, sort_keys=True)


def main():
    chaines = charger(SOURCE)
    if not chaines:
        print("Lancez d'abord : python outils/auditer_gisement.py")
        return 1
    uniques = sorted(set(chaines.values()))
    faits = charger(SORTIE)
    restants = [t for t in uniques if t not in faits]

    print("Textes uniques : %d | déjà traduits : %d | restants : %d"
          % (len(uniques), len(faits), len(restants)))
    if "--etat" in sys.argv:
        return 0
    if not restants:
        print("Gisement traduit. Suite : outils/fusionner_gisement.py")
        return 0
    if "--limite" in sys.argv:
        restants = restants[:int(sys.argv[sys.argv.index("--limite") + 1])]
        print("Cette passe : %d" % len(restants))

    verrou = threading.Lock()
    debut = time.time()
    fait = [0]

    def traiter(texte):
        fr = traduire(texte)
        with verrou:
            fait[0] += 1
            if fr:
                faits[texte] = fr
            if fait[0] % 200 == 0:
                sauver(SORTIE, faits)   # on ne reperd jamais ce qui est fait
                vitesse = fait[0] / max(time.time() - debut, 1)
                reste = (len(restants) - fait[0]) / max(vitesse, 0.01)
                print("  %d/%d (%.1f/s, ~%d min restantes)"
                      % (fait[0], len(restants), vitesse, reste / 60))

    try:
        with futures.ThreadPoolExecutor(max_workers=PARALLELE) as pool:
            list(pool.map(traiter, restants))
    except KeyboardInterrupt:
        print("\nInterrompu — ce qui est fait est gardé.")
    sauver(SORTIE, faits)
    echecs = len(restants) - len([t for t in restants if t in faits])
    print()
    print("%d traduits, %d échecs (restent anglais) -> %s"
          % (len(faits), echecs, os.path.basename(SORTIE)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
