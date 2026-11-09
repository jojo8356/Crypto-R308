# -*- coding: utf-8 -*-
"""R3.09 - Seance 4 : script de test.

  python3 test-mono_decypher.py

Principes de ce script :
  - aucune fonction manquante ne fait planter le test, elle est signalee "a faire" ;
  - les comparaisons de flottants se font A TOLERANCE, jamais par egalite ;
  - lorsque plusieurs reponses sont valides (tris avec ex aequo, algorithmes
    aleatoires), on ne compare pas la reponse mais une QUANTITE INVARIANTE.
"""

import math
import random
import sys

Alphabet = [chr(k) for k in range(65, 65 + 26)]

import os

if not os.path.exists("mono_decypher.py"):
    print("ERREUR : mono_decypher.py est absent de ce repertoire (%s)." % os.getcwd())
    sys.exit(1)
try:
    import mono_decypher as M
except ImportError as e:
    print("ERREUR a l'import de mono_decypher.py : %s" % e)
    if e.name and e.name != "mono_decypher":
        print("         Le module manquant est '%s' : copiez-le dans ce repertoire." % e.name)
    sys.exit(1)
except Exception as e:
    print("ERREUR : mono_decypher.py plante des son chargement : %s: %s" % (type(e).__name__, e))
    sys.exit(1)


# ---------------------------------------------------------------- utilitaires
ETAT = {}      # question -> True / False / None (non commencee)


def _note(q, ok):
    if q not in ETAT or ETAT[q] is None:
        ETAT[q] = ok
    else:
        ETAT[q] = ETAT[q] and ok


def absente(q, nom):
    if not hasattr(M, nom):
        print("  [ A FAIRE ] %s n'est pas encore definie" % nom)
        ETAT.setdefault(q, None)
        return True
    return False


def verifie(q, intitule, obtenu, attendu):
    ok = (obtenu == attendu)
    print("  [%s] %s" % ("  OK   " if ok else " ECHEC ", intitule))
    if not ok:
        print("            attendu : %r" % (attendu,))
        print("            obtenu  : %r" % (obtenu,))
    _note(q, ok)


def verifie_proche(q, intitule, obtenu, attendu, tol=1e-6):
    """Comparaison de flottants A TOLERANCE : indispensable des qu'il y a
    division, somme de nombreux termes ou logarithme."""
    try:
        ok = abs(float(obtenu) - attendu) <= tol
    except (TypeError, ValueError):
        ok = False
    print("  [%s] %s" % ("  OK   " if ok else " ECHEC ", intitule))
    if not ok:
        print("            attendu : %s  (tolerance %g)" % (attendu, tol))
        print("            obtenu  : %s" % (obtenu,))
    _note(q, ok)


def verifie_dico_proche(q, intitule, obtenu, attendu, tol=1e-6):
    """Compare deux dictionnaires de flottants cle a cle, a tolerance."""
    ok = True
    detail = ""
    if not isinstance(obtenu, dict):
        ok, detail = False, "ce n'est pas un dictionnaire"
    else:
        manquantes = set(attendu) - set(obtenu)
        if manquantes:
            ok = True   # tolere : le sujet autorise a n'inclure que les grammes presents
        for g, v in attendu.items():
            if g in obtenu and abs(obtenu[g] - v) > tol:
                ok = False
                detail = "cle %r : attendu %.6f, obtenu %.6f" % (g, v, obtenu[g])
                break
    print("  [%s] %s" % ("  OK   " if ok else " ECHEC ", intitule))
    if not ok:
        print("            %s" % detail)
    _note(q, ok)


def verifie_seuil(q, intitule, obtenu, seuil, sens=">="):
    """Pour les algorithmes aleatoires : on n'exige pas une valeur exacte,
    seulement que le resultat soit assez bon."""
    try:
        ok = (obtenu >= seuil) if sens == ">=" else (obtenu <= seuil)
    except TypeError:
        ok = False
    print("  [%s] %s" % ("  OK   " if ok else " ECHEC ", intitule))
    if not ok:
        print("            il fallait un resultat %s %s, obtenu %s"
              % (sens, seuil, obtenu))
    _note(q, ok)


def verifie_invariant(q, intitule, valeur_obtenue, valeur_ref, tol=1e-6):
    """Quand la reponse n'est pas unique (tri avec ex aequo), on compare la
    valeur que la reponse induit, qui elle est unique."""
    verifie_proche(q, intitule, valeur_obtenue, valeur_ref, tol)


# ---------------------------------------------------------------- donnees
try:
    MSG = open('message_alice_bob.txt').read().strip()
except FileNotFoundError:
    MSG = None
    print("ATTENTION : message_alice_bob.txt absent, certains tests seront ignores.\n")

if MSG is not None and len(MSG) != 226:
    print("ATTENTION : message_alice_bob.txt fait %d caracteres au lieu de 226."
          % len(MSG))
    print("            Le fichier a probablement ete altere par un copier-coller.\n")


print("=" * 62)
print(" R3.09 - Seance 4 : decryptage par recuit simule")
print("=" * 62)

# ---------------------------------------------------------------- Q1
print("\n--- Question 1 : load_grammes ---")
Fref = None
if not absente(1, 'load_grammes'):
    try:
        Fref = M.load_grammes()
        mono = {g: v for g, v in Fref.items() if len(g) == 1}
        bi = {g: v for g, v in Fref.items() if len(g) == 2}
        verifie(1, "26 monogrammes charges", len(mono), 26)
        verifie_seuil(1, "au moins 600 bigrammes charges", len(bi), 600)
        verifie_proche(1, "les monogrammes somment a 1", sum(mono.values()), 1.0, 1e-9)
        verifie_proche(1, "les bigrammes somment a 1", sum(bi.values()), 1.0, 1e-9)
        verifie_proche(1, "frequence du E", Fref.get('E', 0), 0.163856, tol=1e-5)
        verifie_proche(1, "frequence du bigramme ES", Fref.get('ES', 0), 0.030859, tol=1e-5)
    except FileNotFoundError:
        print("  [ A FAIRE ] all_grammes.txt introuvable")
    except Exception as e:
        print("  [ ECHEC  ] load_grammes a leve : %s" % e)
        _note(1, False)

# ---------------------------------------------------------------- Q2
print("\n--- Question 2 : F et J ---")
if not absente(2, 'F'):
    try:
        verifie_dico_proche(2, "monogrammes de ABBA",
                            M.F("ABBA", Alphabet, 1), {'A': 0.5, 'B': 0.5})
        verifie_dico_proche(2, "bigrammes de ABBA",
                            M.F("ABBA", Alphabet, 2),
                            {'AB': 1/3, 'BB': 1/3, 'BA': 1/3})
        verifie_dico_proche(2, "trigrammes de ABBA",
                            M.F("ABBA", Alphabet, 3), {'ABB': 0.5, 'BBA': 0.5})
        if MSG:
            f2 = M.F(MSG, Alphabet, 2)
            verifie(2, "113 bigrammes distincts dans le message", len(f2), 113)
            verifie_proche(2, "les frequences de bigrammes somment a 1",
                           sum(f2.values()), 1.0, 1e-9)
    except Exception as e:
        print("  [ ECHEC  ] F a leve : %s" % e)
        _note(2, False)

if not absente(2, 'J') and Fref and MSG:
    try:
        verifie_seuil(2, "J(message, k=2) est un flottant positif",
                      M.J(MSG, Fref, Alphabet, 2), 0.0)
    except Exception as e:
        print("  [ ECHEC  ] J a leve : %s" % e)
        _note(2, False)

# ---------------------------------------------------------------- Q3
print("\n--- Question 3 : log_probas ---")
LogP = None
if not absente(3, 'log_probas') and Fref:
    try:
        LogP = M.log_probas(Fref, Alphabet)
        verifie(3, "676 bigrammes dans la table", len(LogP), 676)
        verifie_proche(3, "log-proba de ES", LogP['ES'], math.log(0.0308594), tol=1e-3)
        fini = all(math.isfinite(v) for v in LogP.values())
        verifie(3, "aucune valeur infinie (lissage effectue)", fini, True)
        rare = min(LogP.values())
        verifie_seuil(3, "le plancher n'est pas trop bas", rare, -30.0)
    except Exception as e:
        print("  [ ECHEC  ] log_probas a leve : %s" % e)
        _note(3, False)

# ---------------------------------------------------------------- Q4
print("\n--- Question 4 : score ---")
if not absente(4, 'score') and LogP:
    try:
        attendu = LogP['AB'] + LogP['BB'] + LogP['BA']
        verifie_proche(4, "score de ABBA", M.score("ABBA", LogP), attendu, 1e-9)
        verifie_proche(4, "score d'un texte d'une lettre", M.score("A", LogP), 0.0, 1e-9)
        if MSG:
            s_chiffre = M.score(MSG, LogP)
            verifie_seuil(4, "le message chiffre a un mauvais score",
                          s_chiffre, -1250.0, sens="<=")
    except Exception as e:
        print("  [ ECHEC  ] score a leve : %s" % e)
        _note(4, False)

# ---------------------------------------------------------------- Q5
print("\n--- Question 5 : recuit ---")
print("  (algorithme aleatoire : on ne teste pas la cle, mais le score atteint)")
if not absente(5, 'recuit') and LogP and MSG:
    try:
        random.seed(2026)
        meilleur = None
        for _ in range(3):
            resultat = M.recuit(MSG, LogP, Alphabet)
            if not (isinstance(resultat, tuple) and len(resultat) == 2):
                print("  [ ECHEC  ] recuit doit renvoyer un couple (cle, score)")
                _note(5, False)
                break
            cle, s = resultat
            if meilleur is None or s > meilleur[1]:
                meilleur = (cle, s)
        else:
            cle, s = meilleur
            verifie(5, "la cle est une permutation de l'alphabet",
                    sorted(cle.values()), sorted(Alphabet))
            recalcule = M.score(M.substitution(MSG, cle), LogP) \
                if hasattr(M, 'substitution') else s
            verifie_proche(5, "le score annonce correspond a la cle rendue",
                           s, recalcule, tol=1e-6)
            verifie_seuil(5, "score atteint superieur a -1200 (3 essais)", s, -1200.0)
    except Exception as e:
        print("  [ ECHEC  ] recuit a leve : %s" % e)
        _note(5, False)

# ---------------------------------------------------------------- Q6
print("\n--- Question 6 : decryptage du message ---")
if not absente(6, 'decrypte') and LogP and MSG:
    try:
        random.seed(2026)
        cle, clair, s = M.decrypte(MSG, LogP, Alphabet)
        verifie(6, "le texte commence par DURANTLASECONDEGUERRE",
                clair[:21], "DURANTLASECONDEGUERRE")
        justes = sum(1 for a, b in zip(clair, "DURANTLASECONDEGUERREMONDIALEIL")
                     if a == b)
        verifie_seuil(6, "au moins 220 caracteres sur 226 corrects",
                      226 - 5 if justes >= 30 else 0, 220)
    except Exception as e:
        print("  [ ECHEC  ] decrypte a leve : %s" % e)
        _note(6, False)

# ---------------------------------------------------------------- bilan
print("\n" + "=" * 62)
libelles = {1: "load_grammes", 2: "F et J", 3: "log_probas",
            4: "score", 5: "recuit", 6: "decryptage"}
for q in sorted(libelles):
    etat = ETAT.get(q)
    if etat is True:
        mot = "validee"
    elif etat is False:
        mot = "a corriger"
    else:
        mot = "non commencee"
    print("  Question %d (%-13s) : %s" % (q, libelles[q], mot))
faites = sum(1 for q in libelles if ETAT.get(q) is True)
print("\n  %d question(s) validee(s) sur %d." % (faites, len(libelles)))
if faites == len(libelles):
    print("  Tout est bon, vous pouvez deposer votre fichier.")
print("=" * 62)
