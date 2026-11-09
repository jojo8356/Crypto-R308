# -*- coding: utf-8 -*-
"""R3.09 - Séance 4 : Décryptage par recuit simulé."""

import itertools
import math
import random


def load_grammes(filename="all_grammes.txt"):
    """Lit all_grammes.txt et renvoie le dictionnaire des fréquences des

    mono-, bi- et trigrammes, normalisés séparément par longueur.
    """
    by_len = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                g, c = parts[0], int(parts[1])
                by_len.setdefault(len(g), {})[g] = c

    res = {}
    for k, d in by_len.items():
        total = sum(d.values())
        for g, c in d.items():
            res[g] = c / total
    return res


def F(message, alphabet, k=1):
    """Renvoie les fréquences des k-grammes présents dans le message."""
    n = len(message)
    if n < k:
        return {}
    counts = {}
    total = n - k + 1
    for i in range(total):
        gram = message[i : i + k]
        counts[gram] = counts.get(gram, 0) + 1
    return {g: c / total for g, c in counts.items()}


def J(m, Fref, alphabet, k=1):
    """Fonction coût J_k : distance en norme L1 entre fréquences observées

    et fréquences de référence.
    """
    fm = F(m, alphabet, k)
    total = 0.0
    for tup in itertools.product(alphabet, repeat=k):
        gram = "".join(tup)
        total += abs(fm.get(gram, 0.0) - Fref.get(gram, 0.0))
    return total


def log_probas(Fref, alphabet, floor_proba=1e-8):
    """Renvoie un dictionnaire associant à chacun des 676 bigrammes

    son logarithme de probabilité avec lissage pour les bigrammes absents.
    """
    logp = {}
    log_floor = math.log(floor_proba)
    for a in alphabet:
        for b in alphabet:
            gram = a + b
            if gram in Fref and Fref[gram] > 0:
                logp[gram] = math.log(Fref[gram])
            else:
                logp[gram] = log_floor
    return logp


def score(m, LogP):
    """Renvoie la log-vraisemblance L(m) d'un message selon la table de bigrammes LogP."""
    if len(m) < 2:
        return 0.0
    s = 0.0
    for i in range(len(m) - 1):
        s += LogP.get(m[i : i + 2], -18.420680743952367)
    return s


def substitution(m, cle):
    """Applique la clé de substitution au message m."""
    return "".join(cle.get(c, c) for c in m)


def recuit(m, LogP, alphabet, T0=10.0, Tmin=0.05, N=12000):
    """Algorithme de recuit simulé pour optimiser la clé de déchiffrement."""
    shuffled = alphabet[:]
    random.shuffle(shuffled)
    sigma = {a: b for a, b in zip(alphabet, shuffled)}
    curr_text = substitution(m, sigma)
    s = score(curr_text, LogP)

    sigma_star = dict(sigma)
    s_star = s

    for i in range(N):
        T = T0 * ((Tmin / T0) ** (i / N))
        c1, c2 = random.sample(alphabet, 2)
        sigma_prime = dict(sigma)
        sigma_prime[c1], sigma_prime[c2] = sigma_prime[c2], sigma_prime[c1]

        cand_text = substitution(m, sigma_prime)
        s_prime = score(cand_text, LogP)

        diff = s_prime - s
        if diff > 0 or random.random() < math.exp(diff / T):
            sigma = sigma_prime
            s = s_prime
            if s > s_star:
                sigma_star = dict(sigma)
                s_star = s

    return sigma_star, s_star


def decrypte(m, LogP, alphabet, nb_essais=5, T0=10.0, Tmin=0.05, N=12000):
    """Effectue plusieurs exécutions indépendantes de recuit et conserve la meilleure."""
    meilleure_cle = None
    meilleur_score = -float("inf")

    for _ in range(nb_essais):
        cle, s = recuit(m, LogP, alphabet, T0=T0, Tmin=Tmin, N=N)
        if s > meilleur_score:
            meilleur_score = s
            meilleure_cle = cle

    texte_clair = substitution(m, meilleure_cle)
    return meilleure_cle, texte_clair, meilleur_score
