# -*- coding: utf-8 -*-
"""R3.09 - Seance 2 : script de test.

A placer dans le meme repertoire que vigenere.py, cesar.py,
message_bob.txt, message_alice.txt et frequences_francais.txt.

Lancer avec :  python3 test-vigenere.py
"""

import sys

import os

if not os.path.exists("vigenere.py"):
    print("ERREUR : vigenere.py est absent de ce repertoire (%s)." % os.getcwd())
    sys.exit(1)
if not os.path.exists("cesar.py"):
    print("ERREUR : cesar.py est absent de ce repertoire.")
    print("         vigenere.py en a besoin : copiez votre cesar.py de la seance 1 ici.")
    sys.exit(1)
try:
    import vigenere as V
except ImportError as e:
    print("ERREUR a l'import de vigenere.py : %s" % e)
    if e.name and e.name != "vigenere":
        print("         Le module manquant est '%s', pas vigenere.py lui-meme." % e.name)
    sys.exit(1)
except Exception as e:
    print("ERREUR : vigenere.py plante des son chargement : %s: %s" % (type(e).__name__, e))
    print("         (le fichier ne doit contenir que des definitions de fonctions)")
    sys.exit(1)


NB_OK = 0
NB_TOTAL = 0


def verifie(intitule, obtenu, attendu):
    global NB_OK, NB_TOTAL
    NB_TOTAL += 1
    if obtenu == attendu:
        NB_OK += 1
        print("  [ OK  ] %s" % intitule)
    else:
        print("  [ECHEC] %s" % intitule)
        print("          attendu : %r" % (attendu,))
        print("          obtenu  : %r" % (obtenu,))


def verifie_proche(intitule, obtenu, attendu, tol=1e-3):
    global NB_OK, NB_TOTAL
    NB_TOTAL += 1
    if obtenu is not None and abs(obtenu - attendu) < tol:
        NB_OK += 1
        print("  [ OK  ] %s" % intitule)
    else:
        print("  [ECHEC] %s" % intitule)
        print("          attendu : %s (a %s pres)" % (attendu, tol))
        print("          obtenu  : %s" % (obtenu,))


def existe(nom):
    if not hasattr(V, nom):
        print("  [ .... ] %s non definie, tests ignores" % nom)
        return False
    return True


print("\n=== Question 1 : vigenere ===")
if existe('vigenere'):
    verifie("exemple du sujet", V.vigenere("Salut Alice", "Bob"), "TOMVHBMWDF")
    verifie("cle d'une seule lettre = cesar", V.vigenere("ABC", "B"), "BCD")
    verifie("nettoyage du message", V.vigenere("s a l u t !", "AAAAA"), "SALUT")
    verifie("cle plus longue que le message", V.vigenere("AB", "AAAAAAAA"), "AB")

print("\n=== Question 2 : decode_vigenere ===")
if existe('decode_vigenere'):
    verifie("reciproque du chiffrement",
            V.decode_vigenere(V.vigenere("Bonjour tout le monde", "CLEF"), "CLEF"),
            "BONJOURTOUTLEMONDE")
    verifie("exemple du sujet", V.decode_vigenere("TOMVHBMWDF", "Bob"), "SALUTALICE")
    try:
        bob = open('message_bob.txt').read()
        verifie("message de Bob",
                V.decode_vigenere(bob, "BOB"),
                "RENDEZVOUSDEMAINALARECREDERRIERELEGYMNASESURTOUTNEDISRIENAPERSONNE")
    except FileNotFoundError:
        print("  [ .... ] message_bob.txt absent, test ignore")

print("\n=== Question 3 : IC ===")
if existe('IC'):
    verifie_proche("IC de ABRACADABRA", V.IC("ABRACADABRA"), 24 / 110)
    verifie_proche("IC d'un texte d'une lettre", V.IC("A"), 0.0)
    try:
        alice = open('message_alice.txt').read()
        verifie_proche("IC du message d'Alice", V.IC(alice), 0.0470, tol=5e-4)
    except FileNotFoundError:
        print("  [ .... ] message_alice.txt absent, test ignore")

print("\n=== Question 4 : key_length ===")
if existe('key_length'):
    try:
        alice = open('message_alice.txt').read()
        verifie("longueur du mot-cle d'Alice", V.key_length(alice), 5)
    except FileNotFoundError:
        print("  [ .... ] message_alice.txt absent, test ignore")
    if hasattr(V, 'vigenere'):
        temoin = V.vigenere("Ce texte assez long sert uniquement a verifier que la "
                            "detection de la longueur de cle fonctionne correctement "
                            "meme sur un message qui n a rien a voir avec celui d Alice "
                            "et dont la cle comporte sept lettres exactement.", "SECRETS")
        verifie("longueur detectee sur un temoin (cle SECRETS)", V.key_length(temoin), 7)

print("\n=== Question 5 : break_vigenere ===")
if existe('break_vigenere'):
    try:
        alice = open('message_alice.txt').read()
        resultat = V.break_vigenere(alice)
        if not isinstance(resultat, tuple) or len(resultat) != 2:
            print("  [ECHEC] break_vigenere doit renvoyer un couple (cle, message)")
            NB_TOTAL += 1
        else:
            cle, clair = resultat
            verifie("mot-cle retrouve", cle, "ALICE")
            verifie("debut du message dechiffre", clair[:20], "BOBJECROISQUENOTREEN")
    except FileNotFoundError:
        print("  [ .... ] message_alice.txt absent, test ignore")

print("\n%d test(s) reussi(s) sur %d." % (NB_OK, NB_TOTAL))
if NB_OK == NB_TOTAL and NB_TOTAL > 0:
    print("Tout est bon, vous pouvez deposer votre fichier.")
