import math
import random
import unicodedata
from collections import Counter

Alphabet = [chr(k) for k in range(65, 65 + 26)]

def preprocess_message(message):
    """Q1.a — Supprime les accents et convertit tout en majuscules.

    On utilise `unidecode` si elle est disponible, sinon une
    normalisation Unicode NFKD de la bibliothèque standard.
    """
    try:
        from unidecode import unidecode
        return unidecode(message).upper()
    except ImportError:
        decompose = unicodedata.normalize('NFD', message)
        sans_accents = ''.join(c for c in decompose
                               if unicodedata.category(c) != 'Mn')
        return sans_accents.upper().replace('Œ', 'OE').replace('Æ', 'AE')


def clean_message(message, alphabet):
    """Q1.b — Supprime tout caractère n'appartenant pas à `alphabet`."""
    autorises = set(alphabet)
    return ''.join(c for c in message if c in autorises)

def string_2_key(chaine, alphabet):
    """Q2 — Convertit la chaîne 'QWERTY...' en dictionnaire {'A':'Q', ...}.

    Le i-ème caractère de `chaine` est l'image de la i-ème lettre de
    l'alphabet.
    """
    if len(chaine) != len(alphabet):
        raise ValueError("la chaîne doit comporter %d caractères"
                         % len(alphabet))
    return {lettre: chaine[i] for i, lettre in enumerate(alphabet)}


def key_2_string(cle, alphabet):
    """Q2 — Opération inverse : dictionnaire -> chaîne de caractères."""
    return ''.join(cle[lettre] for lettre in alphabet)

def substitution(message, cle):
    """Q3 — Code `message` (déjà prétraité) avec la clé `cle`."""
    return ''.join(cle[c] for c in message)

def inverse_key(cle):
    """Q4 — Clé inverse (de déchiffrement) associée à la clé `cle`."""
    return {image: source for source, image in cle.items()}

def random_key(alphabet):
    """Q5 — Génère une clé aléatoire selon la procédure décrite.

    1) tirage d'un vecteur v de 26 nombres uniformes dans (0, 1) ;
    2) tri : on détermine la permutation σ telle que
       v[σ(1)] <= v[σ(2)] <= ... <= v[σ(26)] ;
    3) la lettre de rang i est remplacée par la lettre de rang σ(i).
    """
    n = len(alphabet)
    v = [random.random() for _ in range(n)]              # 1) tirage
    sigma = sorted(range(n), key=lambda i: v[i])         # 2) tri
    chaine_cle = ''.join(alphabet[sigma[i]] for i in range(n))  # 3)
    return string_2_key(chaine_cle, alphabet)


def temps_brute_force(nb_lettres=26, cles_par_seconde=1e9):
    """Q6 — Nombre de clés et temps de recherche exhaustive."""
    nb_cles = math.factorial(nb_lettres)
    secondes = nb_cles / cles_par_seconde
    annees = secondes / (365.25 * 24 * 3600)
    return nb_cles, secondes, annees

def load_monogrammes(fichier='monogrammes_tries.txt', alphabet=Alphabet):
    """Q7.a — Dictionnaire {lettre : fréquence} du corpus de référence.

    Le fichier contient une ligne par lettre :  <LETTRE> <nb_occurrences>.
    """
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
    """Q7.b — Fréquences d'apparition des lettres de l'alphabet dans
    `message` : dictionnaire {lettre : fréquence}."""
    compteur = Counter(message)
    n = len(message)
    return {lettre: compteur[lettre] / n for lettre in alphabet}

def J1(message, freq_reference, alphabet=Alphabet):
    """Q8 — J1(m) = somme sur x de |F(m, x) - freq_reference(x)|."""
    f = F(message, alphabet)
    return sum(abs(f[x] - freq_reference[x]) for x in alphabet)

def minJ1(message, freq_reference, alphabet=Alphabet):
    """Q9 — Permutation minimisant J1, obtenue par tri.

    Méthode : on classe les lettres du message par fréquence
    décroissante, on classe les lettres du corpus de référence par
    fréquence décroissante, et on associe les lettres de même rang
    (la plus fréquente du message <-> la plus fréquente du français, etc.).
    C'est optimal pour la distance |.| (inégalité des arrangements) :
    deux vecteurs triés dans le même ordre minimisent la somme des
    écarts absolus.

    Complexité : O(N log N) pour un alphabet de taille N (le tri),
    à comparer au N! = 26! ~ 4e26 essais de l'attaque exhaustive.
    (Le comptage des fréquences du message coûte O(|message|).)

    Retourne la clé *inverse* : lettre chiffrée -> lettre en clair.
    """
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
    """Q10 — Applique minJ1 au texte de Proust (non chiffré).

    Idéalement la permutation retrouvée serait l'identité ; on renvoie
    la permutation trouvée et le nombre de lettres correctement placées.
    """
    with open(fichier, encoding='utf-8') as entree:
        texte = clean_message(preprocess_message(entree.read()), alphabet)
    perm = minJ1(texte, freq_reference, alphabet)
    correctes = [c for c in alphabet if perm[c] == c]
    return texte, perm, correctes


def _modele_ngrammes(corpus, alphabet, lissage2=0.5, lissage3=3.0):
    """(Annexe) Log-probabilités lissées des bigrammes et trigrammes
    d'un corpus de référence en français."""
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
    """(Annexe) Score (log-vraisemblance trigramme + 0.3 * bigramme)
    des messages déchiffrés par `cle_idx` (clé sous forme de liste)."""
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
    """(Annexe, bonus Q11) Casse un chiffrement monoalphabétique par
    recuit simulé sur un score de vraisemblance trigramme.

    `messages` : liste de messages chiffrés (mêmes clés supposée).
    Retourne la clé inverse (chiffrée -> clair) la plus probable.
    La permutation fournie par minJ1 est utilisée comme point de
    départ d'un des lancements.
    """
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

def main():
    separateur = "=" * 70

    # ---------------- Question 1 ---------------- #
    print(separateur)
    print("Question 1 — Prétraitement")
    print(separateur)
    exemple = "Vraiment, ça a l'air génial, n'est-ce pas ? Élégant, non ?"
    print("message  :", exemple)
    print("prétraité:", preprocess_message(exemple))
    print("nettoyé  :", clean_message(preprocess_message(exemple), Alphabet))

    # ---------------- Questions 2 et 3 ---------------- #
    print()
    print(separateur)
    print("Questions 2 et 3 — Clés et chiffrement")
    print(separateur)
    cle_alea = random_key(Alphabet)                    # Question 5 aussi
    chaine = key_2_string(cle_alea, Alphabet)
    cle_retour = string_2_key(chaine, Alphabet)
    print("clé aléatoire :  ", chaine)
    print("string_2_key/key_2_string sont cohérentes :", cle_retour == cle_alea)
    message = clean_message(preprocess_message("Bonjour Alice !"), Alphabet)
    code = substitution(message, cle_alea)
    print("« %s » --chiffré--> « %s »" % (message, code))
    print("déchiffré : ", substitution(code, inverse_key(cle_alea)))

    # ---------------- Question 4 ---------------- #
    print()
    print(separateur)
    print("Question 4 — Déchiffrement de la réponse d'Alice")
    print(separateur)
    m4 = ("WEDSQGTSWFHQPXUBSXACGCUECTCAQEWCTCJCXFNCUTPWR"
          "SLPWTFTPQLCTQXJPKCXGCACXCTCTGCRUECRSECSFPWTCR")
    # La clé utilisée par Alice et Bob est reconstituée à la question 11
    # (ils n'ont en réalité jamais changé de clé !). On la reconstruit
    # ici par attaque à texte connu afin d'être autonome :
    chiffrement = {}                 # lettre claire -> lettre chiffrée
    for claire, chiffree in zip(
            "ILFAUDRAITQUONCHANGEDECLEREGULIEREMENTJECROISAVOIRTROUVER"
            "UNMOYENDEGENERERDESCLESALEATOIRES"
            "DURANTLASECONDEGUERREMONDIALEILJOUEUNROLEMAJEURDANSLACRYPT"
            "ANALYSEDELAMACHINEENIGMAUTILISEEPARLESARMEESALLEMANDESLINV"
            "ENTIONDEMACHINESUSANTDEPROCEDESELECTRONIQUESLESBOMBESFERAP"
            "ASSERLEDECRYPTAGEAPLUSIEURSMILLIERSDEMESSAGESPARJOUR",
            m4 + message_q11()):
        chiffrement.setdefault(claire, chiffree)
    # lettres jamais employées (K, W, X, Z) : affectation arbitraire
    restantes_claires = [c for c in Alphabet if c not in chiffrement]
    restantes_chiffrees = [c for c in Alphabet
                           if c not in chiffrement.values()]
    for claire, chiffree in zip(restantes_claires, restantes_chiffrees):
        chiffrement[claire] = chiffree
    print("clé de chiffrement (Listing 1) : %s" % key_2_string(chiffrement,
                                                               Alphabet))
    print("message chiffré  :", m4)
    print("message déchiffré:",
          substitution(m4, inverse_key(chiffrement)))
    print("-> avec les espaces : « IL FAUDRAIT QU'ON CHANGE DE CLÉ")
    print("   RÉGULIÈREMENT. JE CROIS AVOIR TROUVÉ UN MOYEN DE GÉNÉRER")
    print("   DES CLÉS ALÉATOIRES. »")

    # ---------------- Question 5 ---------------- #
    print()
    print(separateur)
    print("Question 5 — Clé aléatoire (procédure du tirage trié)")
    print(separateur)
    for _ in range(3):
        cle = random_key(Alphabet)
        chaine_cle = key_2_string(cle, Alphabet)
        est_permutation = sorted(cle.values()) == Alphabet
        print("  %s   (bijection : %s)" % (chaine_cle, est_permutation))

    # ---------------- Question 6 ---------------- #
    print()
    print(separateur)
    print("Question 6 — L'attaque exhaustive est-elle possible ?")
    print(separateur)
    nb_cles, secondes, annees = temps_brute_force()
    print("  nombre de clés            : 26! = %.3e" % nb_cles)
    print("  à 10^9 clés/s             : %.3e secondes" % secondes)
    print("  soit environ %.1f milliards d'années" % (annees / 1e9))
    print("  (~ l'âge de l'Univers : 13,8 milliards d'années) -> impossible")

    # ---------------- Questions 7, 8, 9 ---------------- #
    freq = load_monogrammes()
    print()
    print(separateur)
    print("Questions 7 à 9 — Fréquences, J1 et minimisation")
    print(separateur)
    print("  5 lettres les plus fréquentes du corpus de référence :",
          sorted(Alphabet, key=lambda x: freq[x], reverse=True)[:5])
    essai = clean_message(preprocess_message("Bonjour Alice !"), Alphabet)
    print("  F(%r) =" % essai,
          {x: round(f, 3) for x, f in F(essai, Alphabet).items() if f})
    print("  J1(essai) = %.4f" % J1(essai, freq))

    # ---------------- Question 10 ---------------- #
    print()
    print(separateur)
    print("Question 10 — Test du décryptage sur proust.txt")
    print(separateur)
    texte, perm, correctes = test_proust(freq)
    print("  longueur du message : %d lettres" % len(texte))
    print("  permutation trouvée : %s" % key_2_string(perm, Alphabet))
    print("  identité (espérée)  : %s" % ''.join(Alphabet))
    print("  l'identité n'est PAS retrouvée exactement : %d lettres sur 26"
          % len(correctes))
    print("  correctement placées : %s" % ''.join(sorted(correctes)))
    print("  mal placées          : %s"
          % ''.join(sorted(c for c in Alphabet if perm[c] != c)))
    extrait = texte[3218:3300]
    print("  extrait réel        :", extrait)
    print("  extrait « déchiffré »:",
          ''.join(perm[c] for c in extrait))

    # ---------------- Question 11 ---------------- #
    print()
    print(separateur)
    print("Question 11 — Décryptage du dernier échange")
    print(separateur)
    m11 = message_q11()
    perm11 = minJ1(m11, freq)
    texte11 = substitution(m11, perm11)
    print("  minJ1 seul donne (J1 = %.4f) :" % J1(texte11, freq))
    print("   ", texte11)
    print("  -> illisible : sur un texte de %d lettres les fluctuations" % len(m11))
    print("     statistiques font que le minimum de J1 n'est pas le")
    print("     message clair. Le tri seul ne suffit pas ici.")

    print()
    print("  Annexe (bonus) : recuit simulé sur un score trigramme,")
    print("  les deux messages (Q4 et Q11) étant chiffrés avec la MÊME clé :")
    cle_trouvee = casse_monoalphabetique([m4, m11], open('proust.txt',
                                                         encoding='utf-8').read())
    vrai_texte11 = substitution(m11, cle_trouvee)
    print("  clé retrouvée      :", key_2_string(inverse_key(cle_trouvee),
                                                  Alphabet))
    print("  J1(vrai décryptage) = %.4f  >  J1(minJ1) : le critère J1"
          % J1(vrai_texte11, freq))
    print("  seul est minimisé, pas la vraisemblance du texte !")
    print()
    print("  Message Q4 :")
    print("   ", substitution(m4, cle_trouvee))
    print("  Message Q11 :")
    print("   ", vrai_texte11)


def message_q11():
    """Le dernier échange entre Alice et Bob (Listing 2)."""
    return ("GQTSXFESRCUPXGCAQCTTCJPXGWSECWENPQCQXTPECJSNCQTGSXRESUTKIFSXSEKRCGCES"
            "JSUBWXCCXWAJSQFWEWRCCISTECRSTJCCRSEECJSXGCREWXLCXFWPXGCJSUBWXCRQRSXFG"
            "CITPUCGCRCECUFTPXWHQCRECRMPJMCRDCTSISRRCTECGCUTKIFSACSIEQRWCQTRJWEEWC"
            "TRGCJCRRSACRISTNPQT")


if __name__ == '__main__':
    main()
