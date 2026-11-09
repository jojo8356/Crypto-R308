import math
import random
import unicodedata
from collections import Counter

Alphabet = [chr(k) for k in range(65, 65 + 26)]

def preprocess_message(message):
    try:
        from unidecode import unidecode
        return unidecode(message).upper()
    except ImportError:
        decompose = unicodedata.normalize('NFD', message)
        sans_accents = ''.join(c for c in decompose
                               if unicodedata.category(c) != 'Mn')
        return sans_accents.upper().replace('Œ', 'OE').replace('Æ', 'AE')


def clean_message(message, alphabet):
    autorises = set(alphabet)
    return ''.join(c for c in message if c in autorises)

def string_2_key(chaine, alphabet):
    if len(chaine) != len(alphabet):
        raise ValueError("la chaîne doit comporter %d caractères"
                         % len(alphabet))
    return {lettre: chaine[i] for i, lettre in enumerate(alphabet)}


def key_2_string(cle, alphabet):
    return ''.join(cle[lettre] for lettre in alphabet)

def substitution(message, cle):
    return ''.join(cle[c] for c in message)

def inverse_key(cle):
    return {image: source for source, image in cle.items()}

def random_key(alphabet):
    n = len(alphabet)
    v = [random.random() for _ in range(n)]              # 1) tirage
    sigma = sorted(range(n), key=lambda i: v[i])         # 2) tri
    chaine_cle = ''.join(alphabet[sigma[i]] for i in range(n))  # 3)
    return string_2_key(chaine_cle, alphabet)


def temps_brute_force(nb_lettres=26, cles_par_seconde=1e9):
    nb_cles = math.factorial(nb_lettres)
    secondes = nb_cles / cles_par_seconde
    annees = secondes / (365.25 * 24 * 3600)
    return nb_cles, secondes, annees

def load_monogrammes(fichier='monogrammes_tries.txt', alphabet=Alphabet):
    occurrences = {}
    with open(fichier, encoding='utf-8') as entree:
        for ligne in entree:
            morceaux = ligne.split()
            if len(morceaux) >= 2:
                occurrences[morceaux[0].upper()] = int(morceaux[1])
    total = sum(occurrences.values())
    return {lettre: occurrences.get(lettre, 0) / total
            for lettre in alphabet}


def F(message, alphabet):
    compteur = Counter(message)
    n = len(message)
    return {lettre: compteur[lettre] / n for lettre in alphabet}

def J1(message, freq_reference, alphabet=Alphabet):
    f = F(message, alphabet)
    return sum(abs(f[x] - freq_reference[x]) for x in alphabet)

def minJ1(message, freq_reference, alphabet=Alphabet):
    f = F(message, alphabet)
    classement_message = sorted(alphabet, key=lambda x: f[x], reverse=True)
    classement_reference = sorted(alphabet,
                                  key=lambda x: freq_reference[x],
                                  reverse=True)
    return {chiffree: claire
            for chiffree, claire in zip(classement_message,
                                        classement_reference)}

def test_proust(freq_reference, alphabet=Alphabet,
                fichier='proust.txt'):
    with open(fichier, encoding='utf-8') as entree:
        texte = clean_message(preprocess_message(entree.read()), alphabet)
    perm = minJ1(texte, freq_reference, alphabet)
    correctes = [c for c in alphabet if perm[c] == c]
    return texte, perm, correctes


def _modele_ngrammes(corpus, alphabet, lissage2=0.5, lissage3=3.0):
    indice = {c: i for i, c in enumerate(alphabet)}
    n = len(alphabet)
    c2 = Counter()
    c3 = Counter()
    p1 = p2 = None
    for caractere in corpus:
        i = indice.get(caractere)
        if i is None:
            p1 = p2 = None
            continue
        if p1 is not None:
            c2[p1 * n + i] += 1
            if p2 is not None:
                c3[p2 * n * n + p1 * n + i] += 1
        p2, p1 = p1, i
    total2 = sum(c2.values())
    total3 = sum(c3.values())
    log2 = [math.log((c2[k] + lissage2) / (total2 + lissage2 * n * n))
            for k in range(n * n)]
    log3 = [math.log((c3[k] + lissage3) / (total3 + lissage3 * n ** 3))
            for k in range(n ** 3)]
    return log2, log3


def _score(cle_idx, messages_idx, log2, log3):
    s = 0.0
    for message in messages_idx:
        p1 = p2 = -1
        for i in message:
            a = cle_idx[i]
            if p1 >= 0:
                s += 0.3 * log2[p1 * 26 + a]
                if p2 >= 0:
                    s += log3[p2 * 676 + p1 * 26 + a]
            p2, p1 = p1, a
    return s


def casse_monoalphabetique(messages, corpus_reference,
                           alphabet=Alphabet, lancements=6,
                           iterations=200000, graine=7):
    rng = random.Random(graine)
    n = len(alphabet)
    indice = {c: i for i, c in enumerate(alphabet)}
    messages_idx = [[indice[c] for c in m] for m in messages]
    log2, log3 = _modele_ngrammes(
        clean_message(preprocess_message(corpus_reference), alphabet),
        alphabet)
    freq_reference = load_monogrammes(alphabet=alphabet)

    def cle_en_liste(cle):                    # chiffrée -> clair
        return [indice[cle[alphabet[i]]] for i in range(n)]

    meilleure_cle, meilleur_score = None, -1e18
    for lancement in range(lancements):
        if lancement == 0:                    # départ = résultat de minJ1
            depart = minJ1(messages[0], freq_reference, alphabet)
            cle = [indice[depart[alphabet[i]]] for i in range(n)]
        else:                                 # départs aléatoires
            cle = rng.sample(range(n), n)
        score_courant = _score(cle, messages_idx, log2, log3)
        meilleure_locale = score_courant
        meilleure_cle_locale = list(cle)
        for t in range(iterations):
            temperature = 2.0 * (0.05 / 2.0) ** (t / iterations)
            i, j = rng.sample(range(n), 2)    # on échange deux images
            cle[i], cle[j] = cle[j], cle[i]
            score_nouveau = _score(cle, messages_idx, log2, log3)
            if (score_nouveau > score_courant
                    or rng.random() < math.exp((score_nouveau
                                                - score_courant)
                                               / temperature)):
                score_courant = score_nouveau
                if score_courant > meilleure_locale:
                    meilleure_locale = score_courant
                    meilleure_cle_locale = list(cle)
            else:
                cle[i], cle[j] = cle[j], cle[i]   # on annule l'échange
        if meilleure_locale > meilleur_score:
            meilleur_score = meilleure_locale
            meilleure_cle = meilleure_cle_locale
    return {c: alphabet[meilleure_cle[i]]
            for i, c in enumerate(alphabet)}
