# -*- coding: utf-8 -*-
# Exercice 2 : Chiffre de Cesar
# (code d'eleve : simple, pas optimise, mais ca marche)

import os

from unidecode import unidecode

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


# ---------------------------------------------------------------
# Question 1 : mise en forme du message
# ---------------------------------------------------------------
def clean_message(message):
    """Enleve les accents, met en majuscules et garde seulement les lettres A-Z."""
    message = unidecode(message)      # les e accentues deviennent des e
    message = message.upper()         # tout en majuscules
    resultat = ""
    for lettre in message:
        if lettre in ALPHABET:        # on garde que les lettres de l'alphabet
            resultat = resultat + lettre
    return resultat


# ---------------------------------------------------------------
# Question 2 : chiffrement
# ---------------------------------------------------------------
def cesar(message, cle):
    """Chiffre le message avec un decalage de 'cle' (une cle negative dechiffre)."""
    message = clean_message(message)
    resultat = ""
    for lettre in message:
        numero = ord(lettre) - ord("A")        # A->0, B->1, ... Z->25
        nouveau = (numero + cle) % 26          # le % 26 fait le "tour" de l'alphabet
        resultat = resultat + chr(nouveau + ord("A"))
    return resultat


def dechiffre_cesar(message, cle):
    """Dechiffre : il suffit de decaler dans l'autre sens."""
    return cesar(message, -cle)


# ---------------------------------------------------------------
# Question 4 : force brute
# ---------------------------------------------------------------
def brute_force(message):
    """Affiche les 26 dechiffrements possibles."""
    for cle in range(26):
        print("cle =", cle, "->", dechiffre_cesar(message, cle))


# ---------------------------------------------------------------
# Question 5 : frequences d'un message
# ---------------------------------------------------------------
def F(message):
    """Renvoie le tableau (liste de taille 26) des frequences des lettres du message."""
    message = clean_message(message)
    frequences = [0.0] * 26
    if len(message) == 0:      # message vide : on evite la division par zero
        return frequences
    for lettre in message:
        indice = ord(lettre) - ord("A")
        frequences[indice] = frequences[indice] + 1
    for i in range(26):
        frequences[i] = frequences[i] / len(message)
    return frequences


# ---------------------------------------------------------------
# Question 6 : frequences de reference
# ---------------------------------------------------------------
FICHIER_FREQUENCES = "/home/pj509414/Documents/crypto/TD1/frequence_francais.txt"


def charge_frequences(nom_fichier=FICHIER_FREQUENCES):
    """Lit le fichier des frequences du francais et renvoie un tableau de taille 26.

    Marche que le fichier soit du genre :
        A 8.11   /   A;8.11   /   A : 8,11   /   ou juste 26 nombres a la suite.
    Et que les valeurs soient en pourcentages ou deja en proportions.
    """
    if not os.path.exists(nom_fichier):
        # si je bosse ailleurs que sur le PC de la fac, je prends le fichier a cote
        nom_fichier = "frequences_francais.txt"

    fichier = open(nom_fichier, "r")
    lignes = fichier.readlines()
    fichier.close()

    frequences = [0.0] * 26
    numeros = []          # au cas ou le fichier ne contient que des nombres

    for ligne in lignes:
        ligne = ligne.strip()
        if ligne == "":
            continue
        # on remplace les separateurs bizarres par des espaces
        for c in [";", ":", "\t", "="]:
            ligne = ligne.replace(c, " ")
        morceaux = ligne.split()

        lettre = ""
        valeur = None
        for mot in morceaux:
            mot = mot.strip()
            if len(mot) == 1 and mot.upper() in ALPHABET:
                lettre = mot.upper()
            else:
                mot = mot.replace(",", ".").replace("%", "")
                try:
                    valeur = float(mot)
                except ValueError:
                    pass          # ligne de titre ou mot bizarre : on ignore

        if valeur is None:
            continue
        if lettre != "":
            frequences[ord(lettre) - ord("A")] = valeur
        else:
            numeros.append(valeur)

    # cas ou il n'y avait pas de lettres dans le fichier : 26 nombres dans l'ordre
    if sum(frequences) == 0 and len(numeros) >= 26:
        frequences = numeros[:26]

    # si le fichier est en pourcentages (somme ~100) on repasse en proportions
    somme = sum(frequences)
    if somme > 2:
        for i in range(26):
            frequences[i] = frequences[i] / somme
    return frequences


Frequences_ref = charge_frequences()   # charge les frequences de reference


# ---------------------------------------------------------------
# Question 7 : fonction cout
# ---------------------------------------------------------------
def J(m):
    """Somme des ecarts absolus entre les frequences de m et celles du francais."""
    freq_m = F(m)
    total = 0.0
    for i in range(26):
        total = total + abs(freq_m[i] - Frequences_ref[i])
    return total


# ---------------------------------------------------------------
# Question 8 : decryptage automatique
# ---------------------------------------------------------------
def break_cesar(message):
    """Trouve la cle la plus probable et renvoie (cle, message decode)."""
    meilleure_cle = 0
    meilleur_message = dechiffre_cesar(message, 0)
    meilleur_cout = J(meilleur_message)
    for cle in range(1, 26):
        essai = dechiffre_cesar(message, cle)
        cout = J(essai)
        if cout < meilleur_cout:
            meilleur_cout = cout
            meilleure_cle = cle
            meilleur_message = essai
    return meilleure_cle, meilleur_message


# ---------------------------------------------------------------
# Programme principal (tests)
# ---------------------------------------------------------------
if __name__ == "__main__":

    print("--- Q1 : clean_message ---")
    print(clean_message("Tu fais quoi ce soir ?"))
    print(clean_message("Ca va ? J'ai regarde le cours d'algebre..."))

    print()
    print("--- Q2 : chiffrement ---")
    message_bob = "Tu fais quoi ce soir ?"
    print("clair :", clean_message(message_bob))
    print("code  :", cesar(message_bob, 3))     # doit donner WXIDLVTXRLFHVRLU

    print()
    print("--- Q3 : dechiffrement du message d'Alice (cle 3) ---")
    message_alice = "MHYDLVWUDYDLOOHUPRQFRXUVGHFUBSWRFHVWWURSJHQLDO"
    print(dechiffre_cesar(message_alice, 3))
    # -> JEVAISTRAVAILLERMONCOURSDECRYPTOCESTTROPGENIAL
    # Ils ne sont pas punis car le message dit qu'Alice va travailler
    # son cours de crypto et qu'elle trouve ca genial : rien de mechant,
    # au contraire ils appliquent le cours !

    print()
    print("--- Q4 : force brute ---")
    message_poubelle = "FSFOWOXDVOCFKMKXMOC"
    brute_force(message_poubelle)
    # la cle est 10 : VIVEMENTLESVACANCES

    print()
    print("--- Q5 : frequences ---")
    print(F("AAABBAAAZZ"))     # [0.6, 0.2, 0, ..., 0, 0.2]

    print()
    print("--- Q6 : frequences de reference ---")
    print(Frequences_ref)

    print()
    print("--- Q7 : fonction cout ---")
    print("J(message francais) =", J("JEVAISTRAVAILLERMONCOURSDECRYPTOCESTTROPGENIAL"))
    print("J(message code)     =", J(message_alice))

    print()
    print("--- Q8 : break_cesar ---")
    print(break_cesar(message_alice))
    print(break_cesar(message_poubelle))
    print(break_cesar(cesar("Rendez vous demain a la recreation derriere le gymnase", 17)))
