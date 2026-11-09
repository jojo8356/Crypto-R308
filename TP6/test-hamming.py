"""
R309 - TP Code de Hamming : script de test.

Placez ce fichier dans le même dossier que votre hamming.py, puis lancez
    python3 test-hamming.py
(ou python3 test-hamming.py chemin/vers/hamming.py).

Le script peut être lancé à tout moment du TP : les fonctions pas encore
écrites sont simplement signalées comme absentes.
"""
import importlib.util
import os
import random
import sys
import threading
import traceback

BONUS_MAX = 0.5        # bonus symbolique (sur la note), proportionnel aux questions validées
DELAI = 3.0            # secondes accordées à chaque test (boucle infinie, etc.)


# ----------------------------------------------------------------------------
# Outils (indépendants de votre code)
# ----------------------------------------------------------------------------

def _est_controle(i):
    """Vrai pour la position 0 et les puissances de 2."""
    return i == 0 or (i & (i - 1)) == 0


def _positions_message(n):
    return [i for i in range(2 ** n) if not _est_controle(i)]


def _syndrome(c):
    """Numéro (entier) obtenu en combinant par XOR les positions des 1."""
    s = 0
    for i, b in enumerate(c):
        if b == 1:
            s ^= i
    return s


def _inverse(c, k):
    d = list(c)
    d[k] = 1 - d[k]
    return d


def _aleatoire(n, graine):
    r = random.Random(graine)
    return [r.randint(0, 1) for _ in range(2 ** n - (n + 1))]


# Exemple de l'énoncé
EX_MESSAGE = [1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1]
EX_FORMATE = [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1]
EX_CODE = [0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1]


class Echec(Exception):
    pass


def verifie(condition, message):
    if not condition:
        raise Echec(message)


def egal(obtenu, attendu, appel):
    if obtenu != attendu:
        raise Echec(f"{appel}\n        attendu : {attendu!r}\n        obtenu  : {obtenu!r}")


# ----------------------------------------------------------------------------
# Les tests, un par question
# ----------------------------------------------------------------------------

def t_int2bits(h):
    egal(h.int2bits(13, 6), [1, 0, 1, 1, 0, 0], "int2bits(13, 6)")
    egal(h.int2bits(0, 4), [0, 0, 0, 0], "int2bits(0, 4)")
    egal(h.int2bits(15, 4), [1, 1, 1, 1], "int2bits(15, 4)")
    egal(h.int2bits(6, 3), [0, 1, 1], "int2bits(6, 3)")


def t_bits2int(h):
    egal(h.bits2int([1, 0, 1, 1, 0, 0]), 13, "bits2int([1, 0, 1, 1, 0, 0])")
    egal(h.bits2int([0, 0, 0, 1]), 8, "bits2int([0, 0, 0, 1])")
    for a in range(64):
        egal(h.bits2int(h.int2bits(a, 6)), a, f"bits2int(int2bits({a}, 6))")


def t_generate_message(h):
    for n in (3, 4, 5):
        m = h.generate_message(n)
        verifie(isinstance(m, list), f"generate_message({n}) doit renvoyer une liste, obtenu : {type(m).__name__}")
        egal(len(m), 2 ** n - (n + 1), f"len(generate_message({n}))")
        verifie(all(b in (0, 1) for b in m), f"generate_message({n}) ne doit contenir que des 0 et des 1, obtenu : {m!r}")
    tirages = [tuple(h.generate_message(5)) for _ in range(20)]
    verifie(len(set(tirages)) > 1, "20 appels à generate_message(5) donnent tous le même message : est-il vraiment aléatoire ?")


def t_formatage(h):
    m = list(EX_MESSAGE)
    egal(h.formatage(m, 4), EX_FORMATE, f"formatage({EX_MESSAGE}, 4)")
    egal(m, EX_MESSAGE, "le message donné en argument ne doit pas être modifié")
    egal(h.formatage([1, 0, 1, 1], 3), [0, 0, 0, 1, 0, 0, 1, 1], "formatage([1, 0, 1, 1], 3)")
    for n in (3, 5):
        x = _aleatoire(n, n)
        f = h.formatage(x, n)
        egal(len(f), 2 ** n, f"len(formatage(m, {n}))")
        verifie(all(f[i] == 0 for i in range(2 ** n) if _est_controle(i)),
                f"formatage(m, {n}) : les positions 0, 1, 2, 4, 8… doivent valoir 0, obtenu : {f!r}")
        egal([f[i] for i in _positions_message(n)], x, f"formatage(m, {n}) : bits du message, lus dans l'ordre")


def t_XOR(h):
    egal(h.XOR([1, 0, 1, 1], [0, 1, 1, 0]), [1, 1, 0, 1], "XOR([1, 0, 1, 1], [0, 1, 1, 0])")
    egal(h.XOR([0, 0, 0], [0, 0, 0]), [0, 0, 0], "XOR([0, 0, 0], [0, 0, 0])")
    egal(h.XOR([1, 1], [1, 1]), [0, 0], "XOR([1, 1], [1, 1])")


def t_test_hamming(h):
    egal(h.test_hamming(EX_FORMATE, 4), [0, 0, 0, 1], f"test_hamming({EX_FORMATE}, 4)")
    egal(h.test_hamming(EX_CODE, 4), [0, 0, 0, 0], f"test_hamming({EX_CODE}, 4)")
    egal(h.test_hamming([0, 0, 0, 1, 0, 0, 0, 0], 3), [1, 1, 0], "test_hamming([0, 0, 0, 1, 0, 0, 0, 0], 3)")
    for n in (3, 5):
        c = _aleatoire(n, 10 + n) + [0] * (n + 1)
        s = _syndrome(c)
        egal(h.test_hamming(c, n), [(s >> k) & 1 for k in range(n)], f"test_hamming(m, {n}) avec m = {c!r}")


def t_set_correctors(h):
    f = list(EX_FORMATE)
    egal(h.set_correctors(f, 4), EX_CODE, f"set_correctors({EX_FORMATE}, 4)")
    for n in (3, 5):
        x = _aleatoire(n, 20 + n)
        f = [0] * (2 ** n)
        for i, b in zip(_positions_message(n), x):
            f[i] = b
        c = h.set_correctors(f, n)
        egal(len(c), 2 ** n, f"len(set_correctors(m, {n}))")
        egal(_syndrome(c), 0, f"set_correctors(m, {n}) : le XOR des positions des 1 doit être nul ; obtenu {c!r}, XOR")
        egal([c[i] for i in _positions_message(n)], x, f"set_correctors(m, {n}) : les bits du message ne doivent pas changer")


def t_codage_hamming(h):
    egal(h.codage_hamming(list(EX_MESSAGE), 4), EX_CODE, f"codage_hamming({EX_MESSAGE}, 4)")
    for n in (3, 4, 5):
        for g in range(5):
            x = _aleatoire(n, 100 * n + g)
            c = h.codage_hamming(x, n)
            egal(len(c), 2 ** n, f"len(codage_hamming(m, {n}))")
            egal(c[0], 0, f"codage_hamming(m, {n})[0]")
            egal(_syndrome(c), 0, f"codage_hamming({x}, {n}) = {c} : XOR des positions des 1")
            egal([c[i] for i in _positions_message(n)], x, f"codage_hamming(m, {n}) : bits du message")


def t_swap(h):
    m = [0, 1, 1, 0]
    egal(h.swap(m, 1), [0, 0, 1, 0], "swap([0, 1, 1, 0], 1)")
    egal(m, [0, 1, 1, 0], "le message donné en argument ne doit pas être modifié")
    egal(h.swap([0, 1, 1, 0], 3), [0, 1, 1, 1], "swap([0, 1, 1, 0], 3)")


def t_decodage(h):
    egal(h.decodage(list(EX_CODE), 4), EX_MESSAGE, "decodage(code de l'exemple, 4)  (sans erreur)")
    for k in range(16):
        egal(h.decodage(_inverse(EX_CODE, k), 4), EX_MESSAGE, f"decodage(code de l'exemple avec le bit {k} inversé, 4)")
    for n in (3, 5):
        x = _aleatoire(n, 200 + n)
        c = [0] * (2 ** n)
        for i, b in zip(_positions_message(n), x):
            c[i] = b
        s = _syndrome(c)
        for k in range(n):
            if (s >> k) & 1:
                c[2 ** k] = 1
        for k in range(1, 2 ** n):
            egal(h.decodage(_inverse(c, k), n), x, f"decodage(m, {n}) avec le bit {k} inversé")


def t_parite(h):
    egal(h.parite([0, 0, 0]), 0, "parite([0, 0, 0])")
    egal(h.parite([1, 0, 1, 1]), 1, "parite([1, 0, 1, 1])")
    egal(h.parite([1, 1, 0, 1, 1]), 0, "parite([1, 1, 0, 1, 1])")


def t_codage_hamming2(h):
    for n in (3, 4, 5):
        x = _aleatoire(n, 300 + n)
        c = h.codage_hamming2(x, n)
        egal(len(c), 2 ** n, f"len(codage_hamming2(m, {n}))")
        egal(sum(c) % 2, 0, f"codage_hamming2({x}, {n}) = {c} : nombre de 1 modulo 2")
        egal(_syndrome(c), 0, f"codage_hamming2(m, {n}) : XOR des positions des 1")
        egal([c[i] for i in _positions_message(n)], x, f"codage_hamming2(m, {n}) : bits du message")


def t_decodage2(h):
    n = 4
    x = list(EX_MESSAGE)
    c = list(EX_CODE)
    c[0] = sum(c) % 2
    egal(h.decodage2(list(c), n), x, "decodage2(m, 4)  (sans erreur)")
    for k in range(16):
        egal(h.decodage2(_inverse(c, k), n), x, f"decodage2(m, 4) avec le bit {k} inversé (une erreur : on corrige)")
    for k in range(16):
        for l in range(k + 1, 16):
            d = _inverse(_inverse(c, k), l)
            egal(h.decodage2(d, n), None, f"decodage2(m, 4) avec les bits {k} et {l} inversés (deux erreurs : None)")


TESTS = [                      # (numéro de la question dans l'énoncé, fonction, test)
    (1, "int2bits", t_int2bits),
    (2, "bits2int", t_bits2int),
    (3, "generate_message", t_generate_message),
    (4, "formatage", t_formatage),
    (5, "XOR", t_XOR),
    (6, "test_hamming", t_test_hamming),
    (7, "set_correctors", t_set_correctors),
    (8, "codage_hamming", t_codage_hamming),
    (10, "swap", t_swap),
    (10, "decodage", t_decodage),
    (11, "parite", t_parite),
    (12, "codage_hamming2", t_codage_hamming2),
    (13, "decodage2", t_decodage2),
]


# ----------------------------------------------------------------------------
# Exécution
# ----------------------------------------------------------------------------

def charge(chemin):
    spec = importlib.util.spec_from_file_location("hamming", chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def execute(test, h):
    """Lance un test dans un fil séparé, pour survivre à une boucle infinie."""
    resultat = {}

    def cible():
        try:
            test(h)
            resultat["ok"] = True
        except Echec as e:
            resultat["echec"] = str(e)
        except Exception:
            resultat["erreur"] = traceback.format_exc(limit=-2)

    fil = threading.Thread(target=cible, daemon=True)
    fil.start()
    fil.join(DELAI)
    if fil.is_alive():
        return "trop long (boucle infinie ?)"
    if "ok" in resultat:
        return None
    if "echec" in resultat:
        return resultat["echec"]
    return "erreur à l'exécution :\n        " + resultat["erreur"].strip().replace("\n", "\n        ")


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "hamming.py")
    if not os.path.exists(chemin):
        print(f"Fichier introuvable : {chemin}")
        print("Placez test-hamming.py dans le même dossier que hamming.py.")
        return
    try:
        h = charge(chemin)
    except Exception:
        print("Impossible de charger hamming.py :")
        print(traceback.format_exc(limit=-1))
        print("Corrigez cette erreur (souvent une faute de syntaxe) puis relancez le test.")
        return

    reussis = 0
    for numero, nom, test in TESTS:
        entete = f"Q{numero:<2} {nom:<17}"
        if not callable(getattr(h, nom, None)):
            print(f"{entete} -- pas encore écrite")
            continue
        probleme = execute(test, h)
        if probleme is None:
            reussis += 1
            print(f"{entete} OK")
        else:
            print(f"{entete} ÉCHEC\n        {probleme}")

    print()
    print(f"Fonctions validées : {reussis} / {len(TESTS)}")
    print(f"Bonus (indicatif) : +{BONUS_MAX * reussis / len(TESTS):.2f} point")


if __name__ == "__main__":
    main()
