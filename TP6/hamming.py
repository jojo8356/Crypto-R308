# -*- coding: utf-8 -*-
"""R3.09 - Cryptographie : code correcteur d'erreur de Hamming.

Codage d'un message de 2^n - (n + 1) bits en un mot de code de 2^n bits :
les positions 0, 1, 2, 4, ..., 2^(n-1) sont reservees aux bits de controle,
les autres accueillent les bits du message, dans l'ordre.

Le fichier ne contient que des definitions de fonctions (ni variable globale,
ni test) ; les noms et l'ordre des arguments sont ceux du sujet.
"""

from random import randint


def est_controle(i):
    """Vrai si la position i est reservee a un bit de controle.

    Ce sont la position 0 et les puissances de 2 (1, 2, 4, 8, ...).
    Un entier i > 0 est une puissance de 2 si et seulement si i & (i - 1)
    vaut 0 (le bit de poids fort de i est alors le seul allume).

    Entrees : i entier
    Sortie  : True si i est la position d'un bit de controle, False sinon
    """
    return i == 0 or (i & (i - 1)) == 0


def positions_message(n):
    """Liste des positions de message pour un mot de code de 2^n bits.

    Entrees : n entier (nombre de bits de controle)
    Sortie  : liste croissante des i de {0, ..., 2^n - 1} qui ne sont pas
              des positions de controle
    """
    return [i for i in range(2 ** n) if not est_controle(i)]


def int2bits(a, n):
    """Representation de a sur n bits, poids faible en premier.

    Entrees : a entier (0 <= a < 2^n), n nombre de bits
    Sortie  : liste de n bits, le k-ieme element etant le bit de poids 2^k

    Exemple : int2bits(13, 6) vaut [1, 0, 1, 1, 0, 0].
    """
    return [(a >> k) & 1 for k in range(n)]


def bits2int(bits):
    """Entier represente par un tableau de bits (poids faible en premier).

    Entrees : bits liste de 0 et de 1
    Sortie  : somme des bits[k] * 2^k ; c'est la reciproque de int2bits
    """
    return sum(b << k for k, b in enumerate(bits))


def generate_message(n):
    """Message aleatoire de taille 2^n - (n + 1).

    Entrees : n entier
    Sortie  : liste de 2^n - (n + 1) bits tires au hasard
    """
    return [randint(0, 1) for _ in range(2 ** n - (n + 1))]


def formatage(m, n):
    """Insertion des bits de controle (mis a 0) dans le message.

    Entrees : m liste de 2^n - (n + 1) bits, n entier
    Sortie  : nouvelle liste de 2^n bits, ou les bits du message occupent
              les positions qui ne sont pas des puissances de 2 et ou toutes
              les autres positions valent 0

    La liste m n'est pas modifiee.
    """
    formate = [0] * (2 ** n)
    for position, bit in zip(positions_message(n), m):
        formate[position] = bit
    return formate


def XOR(m, p):
    """Ou exclusif terme a terme de deux tableaux de meme taille.

    Entrees : m et p listes de bits de meme longueur
    Sortie  : liste [m[k] ^ p[k]] de meme longueur
    """
    return [a ^ b for a, b in zip(m, p)]


def test_hamming(m, n):
    """Syndrome de Hamming du mot m, ecrit sur n bits.

    On combine par XOR les representations int2bits(i, n) de toutes les
    positions i ou m vaut 1. Ce syndrome vaut 0 si le mot est un mot de
    code valide ; sinon il vaut (en binaire, poids faible en premier) la
    position du bit errone.

    Entrees : m liste de 2^n bits, n entier
    Sortie  : liste de n bits
    """
    syndrome = [0] * n
    for position, bit in enumerate(m):
        if bit == 1:
            syndrome = XOR(syndrome, int2bits(position, n))
    return syndrome


def set_correctors(m, n):
    """Calcul des bits de controle du mot formate m.

    Le k-ieme element de test_hamming(m, n) est la valeur a donner au bit
    de controle situe en position 2^k.

    Entrees : m liste de 2^n bits dont les bits de controle valent 0, n entier
    Sortie  : nouvelle liste de 2^n bits, bits de controle mis a jour
    """
    corrige = list(m)
    syndrome = test_hamming(corrige, n)
    for k in range(n):
        corrige[2 ** k] = syndrome[k]
    return corrige


def codage_hamming(m, n):
    """Codage de Hamming d'un message de 2^n - (n + 1) bits.

    Entrees : m liste de 2^n - (n + 1) bits, n entier
    Sortie  : mot de code de 2^n bits (message formate, bits de controle
              calcules), dont le syndrome est nul
    """
    return set_correctors(formatage(m, n), n)


def swap(m, k):
    """Copie de m dont le bit d'indice k a ete inverse.

    Entrees : m liste de bits, k indice valide de m
    Sortie  : nouvelle liste ; la liste m n'est pas modifiee
    """
    copie = list(m)
    copie[k] = 1 - copie[k]
    return copie


def decodage(m, n):
    """Decodage d'un mot de code de 2^n bits, avec correction d'une erreur.

    Le syndrome donne la position du bit errone (0 s'il n'y a pas d'erreur) :
    on inverse ce bit avant de relire le message.

    Entrees : m liste de 2^n bits, n entier
    Sortie  : liste de 2^n - (n + 1) bits, le message corrige
    """
    corrige = list(m)
    erreur = bits2int(test_hamming(corrige, n))
    if erreur != 0:
        corrige = swap(corrige, erreur)
    return [corrige[position] for position in positions_message(n)]


def parite(m):
    """Parite d'un tableau de bits.

    Entrees : m liste de bits
    Sortie  : 0 si le nombre de 1 est pair, 1 sinon
    """
    return sum(m) % 2


def codage_hamming2(m, n):
    """Codage de Hamming avec un bit de parite globale en position 0.

    Entrees : m liste de 2^n - (n + 1) bits, n entier
    Sortie  : mot de code de 2^n bits dont le syndrome est nul et dont le
              nombre de 1 est pair
    """
    code = codage_hamming(m, n)
    code[0] = parite(code)
    return code


def decodage2(m, n):
    """Decodage d'un mot code par codage_hamming2, avec detection d'erreur.

    Entrees : m liste de 2^n bits, n entier
    Sortie  : le message de 2^n - (n + 1) bits si l'on peut le reconstituer,
              None si au moins deux erreurs sont detectees

    Trois cas, selon le syndrome et la parite :
      - syndrome nul : seuls les bits du message et de controle sont surs,
        une parite fausse signifie que seul le bit 0 a ete modifie ;
      - syndrome non nul et parite fausse : une seule erreur, on la corrige ;
      - syndrome non nul et parite juste : au moins deux erreurs, rien a faire.
    """
    mot = list(m)
    erreur = bits2int(test_hamming(mot, n))
    if erreur == 0:
        return [mot[position] for position in positions_message(n)]
    if parite(mot) != 0:
        return decodage(mot, n)
    return None
