# -*- coding: utf-8 -*-
"""R3.09 - Chiffrement RSA : fichier rsa.py (rendu Moodle).

Le fichier est autonome : les outils arithmetiques du TP precedent
(PGCD, Bezout, inv_mod_fast, puissancemodulaire, test_fermat,
test_primalite) y sont recopies, puis viennent les fonctions du TP
RSA-II (random_prime, random_key, string2tab, tab2string,
chiffrement_rsa, dechiffrement_rsa).

Convention du sujet : on chiffre avec d et on dechiffre avec e
(convention de la signature). Pour 0 <= m < n, (m**d)**e = m [n].
Aucune variable globale, aucun test.
"""

import random


# =====================================================================
#  Outils arithmetiques du TP precedent
# =====================================================================

def PGCD(u, v):
    """Renvoie le PGCD de u et v (algorithme d'Euclide, recursif).

    Entrees : u et v entiers naturels
    Sortie  : PGCD(u, v)

    Pour u >= v > 0, la division euclidienne u = v*s + r donne
    PGCD(u, v) = PGCD(v, r) ; on itere jusqu'a obtenir un reste nul,
    et alors PGCD(v, 0) = v.
    """
    if u < v:                      # on se ramene au cas u >= v
        u, v = v, u
    if v == 0:
        return u
    _, r = divmod(u, v)            # quotient inutile ici, on garde le reste
    return PGCD(v, r)


def Bezout(u, v):
    """Couple (a, b) tel que a*u + b*v = PGCD(u, v).

    Entrees : u et v entiers naturels
    Sortie  : le couple (a, b) des coefficients de Bezout

    Meme algorithme que le PGCD, mais on garde la trace du quotient s.
    Avec u = v*s + r et (A, B) solution pour (v, r), on a
    PGCD(u, v) = A*v + B*r = A*v + B*(u - s*v) = B*u + (A - B*s)*v,
    d'ou (a, b) = (B, A - B*s).
    """
    if u < v:
        a, b = Bezout(v, u)
        return (b, a)
    if v == 0:
        return (1, 0)
    s, r = divmod(u, v)
    A, B = Bezout(v, r)
    return (B, A - B * s)


def inv_mod_fast(u, v):
    """Inverse de u modulo v via Bezout, reduit dans {0, ..., v-1}.

    Entrees : u et v entiers naturels
    Sortie  : l'inverse de u modulo v, ou None si u et v ne sont pas
              premiers entre eux

    Complexite en O(log(min(u, v))) : utilisable pour de grands modules,
    la ou inv_mod serait hors de portee.
    """
    a, b = Bezout(u, v)
    if a * u + b * v != 1:         # PGCD different de 1 : pas d'inverse
        return None
    return a % v


def puissancemodulaire(M, d, n):
    """Calcule M**d mod n par exponentiation rapide.

    Entrees : M, d et n entiers avec n > 0 (M peut etre superieur a n)
    Sortie  : M**d mod n

    On divise l'exposant par deux a chaque etape : d = 2*a + r avec r dans
    {0, 1}, d'ou M**d = (M**a)**2 * M**r. Un seul appel recursif par niveau,
    donc environ log2(d) appels en tout (et non d multiplications).
    """
    import sys
    # La recursion descend d'un niveau par bit de d : on releve la limite
    # de Python si necessaire (1024 niveaux pour un exposant de 1024 bits).
    if sys.getrecursionlimit() < d.bit_length() + 100:
        sys.setrecursionlimit(d.bit_length() + 100)

    if d == 0:
        return 1
    if d == 1:
        return M % n
    a, r = divmod(d, 2)
    h = puissancemodulaire(M, a, n)
    return (h * h * (M ** r)) % n  # M**r vaut 1 (r = 0) ou M (r = 1)


def test_fermat(a, p):
    """Test de Fermat en base a pour l'entier p.

    Entrees : a et p entiers, avec 1 <= a < p
    Sortie  : True si a**(p-1) = 1 [p], False sinon

    Si le test renvoie False, p est certainement compose (contraposee du
    petit theoreme de Fermat) ; s'il renvoie True, p est seulement
    probablement premier (les composes qui passent le test sont appeles
    menteurs, par exemple 341 = 11 x 31 pour la base 2).
    """
    return puissancemodulaire(a, p - 1, p) == 1


def test_primalite(p, N):
    """Test probabiliste de primalite (test de Fermat sur N bases).

    Entrees : p entier naturel et N nombre de bases aleatoires
    Sortie  : False des qu'une base demasque p, True sinon

    On teste d'abord la base 2, puis N bases tirees au hasard dans
    {2, ..., p-1}. Une reponse True signifie "probablement premier" : la
    seule limite du test est celle des nombres de Carmichael (par exemple
    561 = 3 x 11 x 17), qui trompent toutes les bases premieres avec eux.
    """
    from random import randint

    if p < 2:
        return False
    if p == 2:
        return True                # aucune base disponible dans {2, ..., p-1}
    if not test_fermat(2, p):
        return False
    for _ in range(N):
        if not test_fermat(randint(2, p - 1), p):
            return False
    return True


# =====================================================================
#  Exercice 1 : construction des cles
# =====================================================================

def random_prime(N):
    """Renvoie un nombre probablement premier de N bits.

    Entrees : N entier >= 2
    Sortie  : p premier avec 2**(N-1) <= p < 2**N

    On tire des entiers au hasard dans [2**(N-1), 2**N[ jusqu'a en trouver
    un qui passe test_primalite avec 10 tests de Fermat. La proportion de
    nombres premiers autour de x valant environ 1/ln(x), il faut en moyenne
    environ ln(2**N) = N*ln(2) tirages (une centaine pour N = 128).
    """
    if N < 2:
        raise ValueError("N doit valoir au moins 2")
    bas, haut = 2 ** (N - 1), 2 ** N
    while True:
        p = random.randrange(bas, haut)
        if test_primalite(p, 10):
            return p


def random_key(N):
    """Renvoie un triplet (e, d, n) : une cle RSA de taille N.

    Entrees : N entier >= 10 (les deux premiers font N bits)
    Sortie  : le triplet (e, d, n) avec n = p*q de 2N-1 ou 2N bits

    p et q sont deux premiers distincts tires avec random_prime(N),
    phi(n) = (p-1)*(q-1). L'exposant e est tire au hasard dans
    [65537, phi(n)-1] et retire tant qu'il n'est pas premier avec phi(n) ;
    son inverse d est calcule avec inv_mod_fast. Pour se proteger de
    l'attaque de Wiener, on renouvelle le tirage de e tant que
    d <= n**(1/4)/3, c'est-a-dire tant que 81*d**4 <= n.
    """
    p = random_prime(N)
    q = random_prime(N)
    while q == p:                   # p et q doivent etre distincts
        q = random_prime(N)
    n = p * q                       # 2N-1 ou 2N bits d'apres (2)
    phi = (p - 1) * (q - 1)
    while True:
        e = random.randrange(65537, phi)   # e dans [65537, phi-1]
        if PGCD(e, phi) != 1:              # retire si non premier avec phi
            continue
        d = inv_mod_fast(e, phi)           # ed = 1 [phi(n)]
        if 81 * d ** 4 > n:                # d > n**(1/4)/3 (anti-Wiener)
            return e, d, n


# =====================================================================
#  Exercice 2 : decoupage du message en blocs
# =====================================================================

def string2tab(m, N):
    """Decoupe le message m en entiers de moins de 2**(N-1) bits.

    Entrees : m chaine de caracteres et N entier
    Sortie  : la liste des blocs de 2*(N-1) bits

    On encode m en UTF-8, chaque octet sur 8 bits ; on ajoute un bit 1
    (marqueur de fin) puis des zeros pour atteindre un multiple de
    2*(N-1) bits, et on decoupe en blocs. Le marqueur de fin permet de
    retirer le bourrage sans ambiguite.
    """
    L = 2 * (N - 1)                          # largeur d'un bloc
    bits = ''.join(f'{octet:08b}' for octet in m.encode('utf-8'))
    bits += '1'                              # marqueur de fin
    while len(bits) % L != 0:                # bourrage
        bits += '0'
    return [int(bits[i:i + L], 2) for i in range(0, len(bits), L)]


def tab2string(tab, N):
    """Reconstitue le message encode par string2tab.

    Entrees : tab liste d'entiers et N entier
    Sortie  : la chaine de caracteres d'origine

    Chaque entier est recrit sur exactement 2*(N-1) bits, les bits sont
    concatenes, puis on retire le bourrage : le marqueur de fin 1 et tout
    ce qui le suit.
    """
    L = 2 * (N - 1)
    bits = ''.join(f'{x:0{L}b}' for x in tab)
    fin = bits.rfind('1')                    # position du marqueur de fin
    if fin == -1:
        raise ValueError("bourrage invalide : aucun marqueur de fin")
    bits = bits[:fin]
    if not bits:
        return ''
    return int(bits, 2).to_bytes((len(bits) + 7) // 8, byteorder='big').decode('utf-8')


# =====================================================================
#  Exercice 3 : chiffrement et dechiffrement
# =====================================================================

def chiffrement_rsa(message, d, n):
    """Chiffre (signe) message avec l'exposant d et le module n.

    Entrees : message chaine de caracteres, d et n entiers
    Sortie  : la liste des entiers xi = mi**d mod n

    N n'est pas un argument : on le retrouve par N = (n.bit_length()+1)//2.
    """
    N = (n.bit_length() + 1) // 2
    return [puissancemodulaire(m, d, n) for m in string2tab(message, N)]


def dechiffrement_rsa(tab, e, n):
    """Dechiffre (verifie la signature) tab avec l'exposant e et le module n.

    Entrees : tab liste d'entiers chiffres, e et n entiers
    Sortie  : le message obtenu en appliquant tab2string aux yi = xi**e mod n
    """
    N = (n.bit_length() + 1) // 2
    return tab2string([puissancemodulaire(x, e, n) for x in tab], N)
