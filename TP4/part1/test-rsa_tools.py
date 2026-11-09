# -*- coding: utf-8 -*-
"""R3.09 - Outils pour RSA : script de test.

  python3 test-rsa_tools.py     (dans le repertoire contenant rsa_tools.py)
"""
import os
import random
import signal
import sys

if not os.path.exists("rsa_tools.py"):
    print("ERREUR : rsa_tools.py est absent de ce repertoire (%s)." % os.getcwd())
    sys.exit(1)
try:
    import rsa_tools as M
except ImportError as e:
    print("ERREUR a l'import de rsa_tools.py : %s" % e)
    if e.name and e.name != "rsa_tools":
        print("         Le module manquant est '%s' : copiez-le dans ce repertoire." % e.name)
    sys.exit(1)
except Exception as e:
    print("ERREUR : rsa_tools.py plante des son chargement : %s: %s" % (type(e).__name__, e))
    print("         (le fichier ne doit contenir que des definitions de fonctions)")
    sys.exit(1)

ETAT = {}


def _note(q, ok):
    ETAT[q] = ok if ETAT.get(q) is None else (ETAT[q] and ok)


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


class Trop_long(Exception):
    pass


def _alarme(signum, frame):
    raise Trop_long()


def chrono(q, intitule, fonction, secondes=5):
    """Execute fonction() avec une limite de temps ; renvoie le resultat ou None."""
    signal.signal(signal.SIGALRM, _alarme)
    signal.alarm(secondes)
    try:
        r = fonction()
        signal.alarm(0)
        return r
    except Trop_long:
        print("  [ ECHEC ] %s : plus de %d s (algorithme trop lent ?)" % (intitule, secondes))
        _note(q, False)
        return None
    except Exception as e:
        signal.alarm(0)
        print("  [ ECHEC ] %s a leve : %s: %s" % (intitule, type(e).__name__, e))
        _note(q, False)
        return None


print("=" * 62)
print(" R3.09 - Outils pour RSA")
print("=" * 62)

print("\n--- I.1 PGCD ---")
if not absente(1, 'PGCD'):
    verifie(1, "PGCD(6750, 5700)", chrono(1, "PGCD", lambda: M.PGCD(6750, 5700)), 150)
    verifie(1, "PGCD(48, 200) : arguments dans l'autre ordre", chrono(1, "PGCD", lambda: M.PGCD(48, 200)), 8)
    verifie(1, "PGCD(17, 0)", chrono(1, "PGCD", lambda: M.PGCD(17, 0)), 17)
    verifie(1, "PGCD de deux nombres premiers entre eux", chrono(1, "PGCD", lambda: M.PGCD(35, 64)), 1)
    verifie(1, "grands entiers (Euclide, pas enumeration)",
            chrono(1, "PGCD", lambda: M.PGCD(2 ** 200 * 3, 2 ** 150 * 5)), 2 ** 150)

print("\n--- I.2 inv_mod (version naive) ---")
if not absente(2, 'inv_mod'):
    verifie(2, "inverse de 5 modulo 7", chrono(2, "inv_mod", lambda: M.inv_mod(5, 7)), 3)
    verifie(2, "inverse de 5 modulo 10 : n'existe pas -> None", chrono(2, "inv_mod", lambda: M.inv_mod(5, 10)), None)
    verifie(2, "inverse de 1 modulo 13", chrono(2, "inv_mod", lambda: M.inv_mod(1, 13)), 1)

print("\n--- I.3 Bezout ---")
if not absente(3, 'Bezout'):
    for (u, v) in [(6750, 5700), (35, 21), (21, 35), (17, 0), (1, 1)]:
        r = chrono(3, "Bezout(%d,%d)" % (u, v), lambda: M.Bezout(u, v))
        if r is None:
            continue
        if not (isinstance(r, tuple) and len(r) == 2):
            print("  [ ECHEC ] Bezout doit renvoyer un couple (a, b)")
            _note(3, False)
            continue
        a, b = r
        g = M.PGCD(u, v) if hasattr(M, 'PGCD') else __import__('math').gcd(u, v)
        verifie(3, "%d*a + %d*b = PGCD = %d  (a=%d, b=%d)" % (u, v, g, a, b), a * u + b * v, g)

print("\n--- I.4 inv_mod_fast ---")
if not absente(4, 'inv_mod_fast'):
    y = chrono(4, "inv_mod_fast", lambda: M.inv_mod_fast(42158, 77491))
    if y is not None:
        verifie(4, "42158 * y = 1 modulo 77491", (42158 * y) % 77491, 1)
        verifie(4, "y est reduit dans {0,...,77490}", 0 <= y < 77491, True)
    y = chrono(4, "inv_mod_fast", lambda: M.inv_mod_fast(5, 7))
    verifie(4, "inverse de 5 modulo 7 (meme reponse que inv_mod)", y, 3)
    gros = 2 ** 127 - 1
    y = chrono(4, "inv_mod_fast (grands entiers)", lambda: M.inv_mod_fast(123456789, gros))
    if y is not None:
        verifie(4, "fonctionne sur 128 bits (inv_mod n'y arriverait jamais)", (123456789 * y) % gros, 1)

print("\n--- II.1 puissancemodulaire ---")
if not absente(5, 'puissancemodulaire'):
    attendu = [1, 2, 4, 8, 16, 13, 7, 14, 9, 18]
    obtenu = [chrono(5, "puissancemodulaire", lambda d=d: M.puissancemodulaire(2, d, 19)) for d in range(10)]
    verifie(5, "2^d modulo 19 pour d = 0..9", obtenu, attendu)
    verifie(5, "grand exposant (recursion, pas d multiplications)",
            chrono(5, "puissancemodulaire", lambda: M.puissancemodulaire(123412341234, 1239399301234, 123412355123512)),
            35269953065984)
    verifie(5, "M^0 modulo n vaut 1", chrono(5, "puissancemodulaire", lambda: M.puissancemodulaire(7, 0, 55)), 1)
    verifie(5, "resultat reduit modulo n (M > n)", chrono(5, "puissancemodulaire", lambda: M.puissancemodulaire(60, 1, 55)), 5)
    # la fonction ne doit pas appeler pow(M, d, n)
    import builtins
    appels = []
    _pow = builtins.pow

    def pow_espion(*args):
        if len(args) == 3:
            appels.append(args)
        return _pow(*args)
    builtins.pow = pow_espion
    try:
        M.puissancemodulaire(3, 1000, 101)
    except Exception:
        pass
    builtins.pow = _pow
    verifie(5, "n'utilise pas pow(M, d, n)", len(appels), 0)

print("\n--- II.2 test_fermat ---")
if not absente(6, 'test_fermat'):
    verifie(6, "2^(16) = 1 modulo 17 (17 premier)", chrono(6, "test_fermat", lambda: M.test_fermat(2, 17)), True)
    verifie(6, "2^(14) != 1 modulo 15 (15 compose)", chrono(6, "test_fermat", lambda: M.test_fermat(2, 15)), False)
    verifie(6, "341 est un menteur pour la base 2 (341 = 11 x 31)", chrono(6, "test_fermat", lambda: M.test_fermat(2, 341)), True)
    verifie(6, "... mais pas pour la base 3", chrono(6, "test_fermat", lambda: M.test_fermat(3, 341)), False)

print("\n--- II.3 primalite ---")
if not absente(7, 'primalite'):
    r = chrono(7, "primalite", lambda: [n for n in range(2, 60) if M.primalite(n)])
    verifie(7, "nombres premiers < 60", r, [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59])
    verifie(7, "49 = 7 x 7 (tester jusqu'a sqrt(n) INCLUS)", chrono(7, "primalite", lambda: M.primalite(49)), False)
    verifie(7, "1 n'est pas premier", chrono(7, "primalite", lambda: M.primalite(1)), False)
    verifie(7, "1 000 003 est premier (sqrt(n) seulement, pas n)", chrono(7, "primalite", lambda: M.primalite(1000003)), True)

print("\n--- II.4 test_primalite (probabiliste) ---")
if not absente(8, 'test_primalite'):
    random.seed(2026)
    r = chrono(8, "test_primalite", lambda: all(M.test_primalite(p, 10) for p in [2, 3, 5, 101, 1000003, 2 ** 31 - 1]))
    verifie(8, "repond True sur des premiers (dont 2^31 - 1)", r, True)
    r = chrono(8, "test_primalite", lambda: any(M.test_primalite(c, 10) for c in [15, 91, 1000001, 2 ** 32 + 1]))
    verifie(8, "repond False sur des composes ordinaires", r, False)
    r = chrono(8, "test_primalite", lambda: M.test_primalite(341, 20))
    verifie(8, "341 est demasque avec 20 bases aleatoires", r, False)
    r = chrono(8, "test_primalite", lambda: M.test_primalite(561, 20))
    print("  [ INFO  ] 561 (nombre de Carmichael) : test_primalite repond %s -- c'est la limite du test de Fermat" % r)

print("\n" + "=" * 62)
libelles = {1: "PGCD", 2: "inv_mod", 3: "Bezout", 4: "inv_mod_fast",
            5: "puissancemodulaire", 6: "test_fermat", 7: "primalite", 8: "test_primalite"}
for q in sorted(libelles):
    etat = ETAT.get(q)
    mot = "validee" if etat is True else ("a corriger" if etat is False else "non commencee")
    print("  Question %d (%-18s) : %s" % (q, libelles[q], mot))
faites = sum(1 for q in libelles if ETAT.get(q) is True)
print("\n  %d question(s) validee(s) sur %d." % (faites, len(libelles)))
if faites == len(libelles):
    print("  Tout est bon, vous pouvez deposer votre fichier.")
print("=" * 62)
