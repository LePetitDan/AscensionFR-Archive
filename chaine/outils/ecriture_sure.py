# -*- coding: utf-8 -*-
r"""L'ÉCRITURE ATOMIQUE, en un seul endroit (29/07/2026).

On écrit À CÔTÉ, on ne met en place qu'une fois le fichier complet et
refermé (`os.replace`, qui est atomique sur le même volume). Une coupure
— Ctrl+C, extinction, plantage — laisse alors soit l'ANCIEN fichier
intact, soit le NOUVEAU complet. Jamais un fichier tronqué.

C'est déjà la doctrine du zip de release, du paresseux et de la veille ;
elle manquait aux fichiers de `traductions/`, dont `sorts.json` — le plus
précieux du projet, réécrit toutes les 200 traductions pendant des heures.
Dan a coupé l'Atelier le 28/07 au soir : par chance, pas au mauvais
moment.

Usage :
    from ecriture_sure import ecrire_json, ecrire_texte
    ecrire_json(chemin, donnees, indent=1, sort_keys=True)
"""
import io
import json
import os


def _poser(provisoire, chemin):
    try:
        os.replace(provisoire, chemin)
    except OSError:
        try:
            os.remove(provisoire)
        except OSError:
            pass
        raise


def ecrire_json(chemin, donnees, ensure_ascii=False, indent=1,
                sort_keys=True):
    """json.dump atomique. Mêmes valeurs par défaut que le reste du dépôt."""
    dossier = os.path.dirname(chemin)
    if dossier:
        os.makedirs(dossier, exist_ok=True)
    provisoire = chemin + ".part"
    try:
        with io.open(provisoire, "w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=ensure_ascii, indent=indent,
                      sort_keys=sort_keys)
            f.flush()
            os.fsync(f.fileno())
    except BaseException:
        # BaseException, pas Exception : un Ctrl+C au milieu du dump doit
        # lui aussi emporter le fichier provisoire — c'est le cas qu'on
        # veut couvrir en premier.
        try:
            os.remove(provisoire)
        except OSError:
            pass
        raise
    _poser(provisoire, chemin)


def ecrire_texte(chemin, texte, newline=""):
    """Même garantie, pour un fichier texte (Lua, rapport…)."""
    dossier = os.path.dirname(chemin)
    if dossier:
        os.makedirs(dossier, exist_ok=True)
    provisoire = chemin + ".part"
    try:
        with io.open(provisoire, "w", encoding="utf-8", newline=newline) as f:
            f.write(texte)
            f.flush()
            os.fsync(f.fileno())
    except BaseException:
        try:
            os.remove(provisoire)
        except OSError:
            pass
        raise
    _poser(provisoire, chemin)
