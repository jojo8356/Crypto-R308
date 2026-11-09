import unicodedata
from collections import Counter
from tabulate import tabulate

def clean_message(msg):
    """Fonction de nettoyage (si non définie précédemment) :

    Passe en majuscules, enlève les accents et supprime les caractères non
    alphabétiques.
    """
    msg = unicodedata.normalize("NFD", msg)
    msg = "".join(c for c in msg if unicodedata.category(c) != "Mn")
    return "".join(c.upper() for c in msg if c.isalpha())


def vigenere(msg_clear, key_word):
    m = clean_message(msg_clear)
    k = clean_message(key_word)

    res = []
    len_k = len(k)

    for i in range(len(m)):
        # Décalage donné par la lettre correspondante de la clé (A=0, B=1, ..., Z=25)
        shift = ord(k[i % len_k]) - ord("A")

        # Nouvelle lettre chiffrée
        cipher_char = chr((ord(m[i]) - ord("A") + shift) % 26 + ord("A"))
        res.append(cipher_char)

    return "".join(res)

def decode_vigenere(msg_coded, key_word):
    c = clean_message(msg_coded)
    k = clean_message(key_word)

    res = []
    len_k = len(k)

    # Déchiffrement lettre par lettre
    for i in range(len(c)):
        # Calcul du décalage inverse
        shift = ord(k[i % len_k]) - ord("A")

        # Soustraction du décalage
        clear_char = chr((ord(c[i]) - ord("A") - shift) % 26 + ord("A"))
        res.append(clear_char)

    return "".join(res)

def IC(message):
    m = clean_message(message)
    n = len(m)

    # Sécurité pour éviter la division par zéro si le message est trop court
    if n <= 1:
        return 0.0

    # 2. Compter les occurrences de chaque lettre
    counts = Counter(m)

    # 3. Calcul de la somme sum(nx * (nx - 1))
    somme = sum(nx * (nx - 1) for nx in counts.values())

    return somme / (n * (n - 1))


def key_length(msg_coded, lmax=20):
    m = clean_message(msg_coded)
    smallest_L = None
    table_data = []

    for L in range(1, lmax + 1):
        # 1. Découpage du message en L colonnes (sous-textes)
        columns = [m[i::L] for i in range(L)]

        # 2. Calcul du moyen des IC des L colonnes
        avg_ic = sum(IC(col) for col in columns) / L

        # 3. Stockage pour le tableau
        table_data.append([L, f"{avg_ic:.4f}"])

        # 4. Enregistrement de la PREMIÈRE valeur qui dépasse 0.06
        if avg_ic > 0.06 and smallest_L is None:
            smallest_L = L

    # Affichage du tableau propre
    headers = ["Longueur L", "IC Moyen"]
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

    return smallest_L

def load_frequencies(filename="frequences_francais.txt"):
    """Lit le fichier de fréquences et renvoie un dictionnaire {lettre: fréquence}."""
    freq = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            letter, value = line.split()
            freq[letter.upper()] = float(value)
    return freq


# Chargement une seule fois au démarrage
FREQ_FR = load_frequencies()

def break_cesar(column):
    """Retrouve la lettre de clé d'une colonne par analyse fréquentielle."""
    best_score = -1
    best_shift = 0
    n = len(column)
    counts = Counter(column)

    for shift in range(26):
        score = 0
        for char, count in counts.items():
            # Lettre du texte clair supposé si la clé valait 'shift'
            unshifted = chr((ord(char) - ord("A") - shift) % 26 + ord("A"))
            score += (count / n) * FREQ_FR.get(unshifted, 0)

        if score > best_score:
            best_score = score
            best_shift = shift

    return chr(ord("A") + best_shift)

def break_vigenere(msg_coded):
    m = clean_message(msg_coded)

    # 1. Déterminer la longueur de la clé
    L = key_length(m)

    # 2. Casser chaque colonne par analyse fréquentielle
    key_word = "".join(break_cesar(m[i::L]) for i in range(L))

    # 3. Déchiffrer le message complet
    msg_decoded = decode_vigenere(m, key_word)

    return key_word, msg_decoded

if __name__ == "__main__":
    print(vigenere("Salut Alice", "Bob"))
    # Affiche bien : TOMVHBMWDF

    with open("message_bob.txt", "r", encoding="utf-8") as f:
        contenu_bob = f.read()

    message_clair_bob = decode_vigenere(contenu_bob, "BOB")

    print("Message déchiffré :")
    print(message_clair_bob)

    # Lecture et calcul de l'IC pour le message d'Alice
    with open("message_alice.txt", "r", encoding="utf-8") as f:
        contenu_alice = f.read()

    ic_alice = IC(contenu_alice)
    print(f"Indice de coïncidence du message d'Alice : {ic_alice:.4f}")

    longueur_cle = key_length(contenu_alice)
    print("-" * 18)
    print(f"Longueur de la clé détectée : L = {longueur_cle}")

    mot_cle, message_dechiffre = break_vigenere(contenu_alice)

    print("=" * 50)
    print(f"MOT-CLÉ TROUVÉ : {mot_cle}")
    print("=" * 50)
    print("MESSAGE DÉCHIFFRÉ :")
    print(message_dechiffre)
