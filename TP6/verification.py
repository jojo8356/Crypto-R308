# -*- coding: utf-8 -*-
"""R3.09 - TP6 : verifications experimentales du code de Hamming.

Ce script ne fait pas partie du rendu demande (hamming.py ne doit contenir
que des fonctions) : il sert a produire les traces citees dans le
compte-rendu. Lancement :  python3 verification.py
"""
import random

import hamming as h

EX_MESSAGE = [1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1]
EX_FORMATE = [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1]
EX_CODE = [0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1]


def titre(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


def q1():
    titre("Q1 - int2bits")
    for a, n in ((13, 6), (0, 4), (15, 4), (6, 3), (45, 6)):
        bits = h.int2bits(a, n)
        somme = " + ".join(f"{b}.2^{k}" for k, b in enumerate(bits) if b) or "0"
        print(f"  int2bits({str(a) + ', ' + str(n):<7}) = {str(bits):<22} ({a} = {somme})")


def q2():
    titre("Q2 - bits2int et reciprocite")
    print(f"  bits2int([1, 0, 1, 1, 0, 0]) = {h.bits2int([1, 0, 1, 1, 0, 0])}")
    ok = all(h.bits2int(h.int2bits(a, 8)) == a for a in range(256))
    print(f"  bits2int(int2bits(a, 8)) == a pour a = 0..255 : {ok}")
    ok = all(h.int2bits(h.bits2int(h.int2bits(a, 8)), 8) == h.int2bits(a, 8) for a in range(256))
    print(f"  int2bits(bits2int(x)) == x pour les 256 mots de 8 bits : {ok}")


def q3():
    titre("Q3 - generate_message")
    for n in (3, 4, 5):
        m = h.generate_message(n)
        print(f"  n = {n} -> {len(m)} bits : {m}")
    tirages = {tuple(h.generate_message(5)) for _ in range(200)}
    print(f"  200 tirages pour n = 5 : {len(tirages)} messages distincts")


def q4():
    titre("Q4 - formatage")
    print(f"  message      : {EX_MESSAGE}")
    print(f"  formatage    : {h.formatage(EX_MESSAGE, 4)}")
    print(f"  attendu      : {EX_FORMATE}")
    print(f"  identique    : {h.formatage(EX_MESSAGE, 4) == EX_FORMATE}")
    controle = [i for i in range(16) if h.est_controle(i)]
    print(f"  positions de controle (n = 4) : {controle}")


def q6():
    titre("Q6 - test_hamming")
    unes = [i for i, b in enumerate(EX_FORMATE) if b == 1]
    print(f"  positions des 1 de m    : {unes}")
    x = 0
    for i in unes:
        x ^= i
    print(f"  XOR de ces positions    : {' ^ '.join(map(str, unes))} = {x}")
    print(f"  int2bits({x}, 4) est bien {h.int2bits(x, 4)}")
    print(f"  test_hamming(m, 4)      : {h.test_hamming(EX_FORMATE, 4)}  (soit {h.bits2int(h.test_hamming(EX_FORMATE, 4))})")
    print(f"  test_hamming(code, 4)   : {h.test_hamming(EX_CODE, 4)}")


def q7_q8():
    titre("Q7/Q8 - set_correctors et codage_hamming")
    print(f"  formatage(m, 4)             : {EX_FORMATE}")
    print(f"  test_hamming(m, 4)          : {h.test_hamming(EX_FORMATE, 4)}")
    print(f"  set_correctors(m, 4)        : {h.set_correctors(EX_FORMATE, 4)}")
    print(f"  codage_hamming(m, 4)        : {h.codage_hamming(EX_MESSAGE, 4)}")
    print(f"  attendu                     : {EX_CODE}")
    print(f"  identique                   : {h.codage_hamming(EX_MESSAGE, 4) == EX_CODE}")


def q9(nb=1000):
    titre("Q9 - verification : le syndrome d'un mot de code est nul")
    r = random.Random(2026)
    print(f"  {'n':>2}  {'taille m':>8}  {'taille code':>11}  {'tests':>5}  {'syndromes nuls':>14}")
    for n in (3, 4, 5, 6, 7):
        taille = 2 ** n - (n + 1)
        nuls = 0
        for _ in range(nb):
            m = [r.randint(0, 1) for _ in range(taille)]
            if h.test_hamming(h.codage_hamming(m, n), n) == [0] * n:
                nuls += 1
        print(f"  {n:>2}  {taille:>8}  {2 ** n:>11}  {nb:>5}  {nuls:>14}")
    print()
    print("  Nombre total de mots de code distincts verifies :", end=" ")
    total = 0
    for n in (3, 4):
        taille = 2 ** n
        trouves = set()
        for a in range(2 ** (2 ** n - (n + 1))):
            m = h.int2bits(a, 2 ** n - (n + 1))
            trouves.add(tuple(h.codage_hamming(m, n)))
        total += len(trouves)
        print(f"n={n}: {len(trouves)}", end="  ")
    print(f"(total {total})")


def q10():
    titre("Q10 - swap, syndrome et decodage")
    print(f"  code correct : {EX_CODE}")
    print()
    print(f"  {'bit inverse':>11}  {'syndrome (entier)':>17}  {'message decode':>14}  {'correct':>7}")
    ok = 0
    for k in range(16):
        fautif = h.swap(EX_CODE, k)
        s = h.bits2int(h.test_hamming(fautif, 4))
        d = h.decodage(fautif, 4)
        juste = d == EX_MESSAGE
        ok += juste
        print(f"  {k:>11}  {s:>17}  {str(d):>14}  {'oui' if juste else 'NON':>7}")
    print(f"\n  {ok} / 16 erreurs simples corrigees")
    copie = list(EX_CODE)
    h.swap(copie, 5)
    print(f"  swap ne modifie pas son argument   : {copie == EX_CODE}")


def q10_deux_erreurs():
    titre("Q10 - ce que fait decodage face a deux erreurs")
    print(f"  {'bits inverses':>13}  {'syndrome':>8}  {'decodage':>26}  {'resultat':>22}")
    for k, l in ((1, 2), (0, 1), (3, 5), (8, 9), (14, 15)):
        d = h.decodage(h.swap(h.swap(EX_CODE, k), l), 4)
        s = h.bits2int(h.test_hamming(h.swap(h.swap(EX_CODE, k), l), 4))
        etat = "message correct" if d == EX_MESSAGE else "MESSAGE FAUX"
        print(f"  {k:>6} et {l:<4}  {s:>8}  {str(d):>26}  {etat:>22}")


def q11_q12():
    titre("Q11/Q12 - parite et codage_hamming2")
    for m in ([0, 0, 0], [1, 0, 1, 1], [1, 1, 0, 1, 1]):
        print(f"  parite({m}) = {h.parite(m)}")
    code = h.codage_hamming2(EX_MESSAGE, 4)
    print()
    print(f"  codage_hamming(m, 4)  : {EX_CODE}   ({sum(EX_CODE)} bits a 1)")
    print(f"  codage_hamming2(m, 4) : {code}   ({sum(code)} bits a 1)")
    print(f"  syndrome              : {h.test_hamming(code, 4)}")
    print(f"  nombre de 1 pair      : {h.parite(code) == 0}")
    autre = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    c1 = h.codage_hamming(autre, 4)
    c2 = h.codage_hamming2(autre, 4)
    print()
    print("  Second exemple, ou le bit de parite est necessaire :")
    print(f"    message               : {autre}")
    print(f"    codage_hamming        : {c1}   ({sum(c1)} bits a 1, impair)")
    print(f"    codage_hamming2       : {c2}   ({sum(c2)} bits a 1, pair)")
    print(f"    syndrome              : {h.test_hamming(c2, 4)}")
    print(f"    decodage2(c2, 4)      : {h.decodage2(c2, 4)}")


def q13():
    titre("Q13 - decodage2 : 0, 1 et 2 erreurs")
    code = h.codage_hamming2(EX_MESSAGE, 4)
    print(f"  mot de code : {code}")
    print(f"  0 erreur        -> {h.decodage2(code, 4)}")
    ok1 = all(h.decodage2(h.swap(code, k), 4) == EX_MESSAGE for k in range(16))
    print(f"  1 erreur (16 positions)  -> message retrouve : {ok1}")
    none_count = 0
    faux = 0
    for k in range(16):
        for l in range(k + 1, 16):
            d = h.decodage2(h.swap(h.swap(code, k), l), 4)
            if d is None:
                none_count += 1
            else:
                faux += 1
    print(f"  2 erreurs (120 paires)   -> None : {none_count}, autre : {faux}")


def resume():
    titre("Resume de l'execution du script de test")
    import subprocess
    import sys
    out = subprocess.run([sys.executable, "test-hamming.py"], capture_output=True, text=True)
    print(out.stdout.rstrip())


if __name__ == "__main__":
    q1()
    q2()
    q3()
    q4()
    q6()
    q7_q8()
    q9()
    q10()
    q10_deux_erreurs()
    q11_q12()
    q13()
    resume()
