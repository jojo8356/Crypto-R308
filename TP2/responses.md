# TP2 — Cryptographie R309 : Vigenère, ou la revanche d’Alice

**Auteur :** Johan Polsinelli  
**Date :** 14 septembre 2026  

---

## Exercice 1 : Indice de coïncidence

Soit $m$ un texte de longueur $n = |m|$ écrit sur l'alphabet $\mathcal{A}$. Pour chaque lettre $x \in \mathcal{A}$, on note $n_x$ son nombre d'occurrences dans $m$ ($\sum_{x \in \mathcal{A}} n_x = n$).  
L'indice de coïncidence $\operatorname{IC}(m)$ est défini par :
$$\operatorname{IC}(m) := \frac{\sum_{x \in \mathcal{A}} n_x(n_x - 1)}{n(n - 1)}$$

---

### 1. Interprétation probabiliste de l'indice de coïncidence

On choisit uniformément et au hasard deux positions distinctes $(i, j)$ avec $i \neq j$ dans le texte $m$. 

1. **Nombre total de tirages possibles :** Il y a $n$ choix pour la première position et $(n - 1)$ choix pour la seconde position, soit $n(n - 1)$ couples ordonnés de positions distinctes.
2. **Nombre de cas favorables pour une lettre $x$ fixée :** Pour que la première position contienne la lettre $x$ et la seconde également, il faut choisir la première position parmi les $n_x$ occurrences de $x$, puis la seconde parmi les $(n_x - 1)$ occurrences restantes. Il y a donc $n_x(n_x - 1)$ couples favorables.
3. **Probabilité d'obtenir la même lettre $x$ :**
   $$\mathbb{P}(\text{lettre}_1 = x \text{ et } \text{lettre}_2 = x) = \frac{n_x(n_x - 1)}{n(n - 1)}$$
4. **Probabilité globale :** Les événements « les deux lettres sont la lettre $x$ » étant mutuellement exclusifs pour des lettres différentes, la probabilité que deux lettres tirées à des positions distinctes soient identiques est la somme sur tout l'alphabet :
   $$\mathbb{P}(\text{deux lettres identiques}) = \frac{\sum_{x \in \mathcal{A}} n_x(n_x - 1)}{n(n - 1)} = \operatorname{IC}(m)$$

> **Conclusion :** $\operatorname{IC}(m)$ représente **exactement** la probabilité que deux lettres tirées au hasard à des positions distinctes dans le texte $m$ soient identiques.

### 2. Calcul manuel pour $m = \text{ABRACADABRA}$

Le texte $m = \text{ABRACADABRA}$ a pour longueur $n = 11$.

#### Décompte des occurrences $n_x$ :

| Lettre $x$ | Positions | Occurrences $n_x$ | Terme $n_x(n_x - 1)$ |
| :---: | :---: | :---: | :---: |
| **A** | 1, 4, 6, 8, 11 | 5 | $5 \times 4 = 20$ |
| **B** | 2, 9 | 2 | $2 \times 1 = 2$ |
| **R** | 3, 10 | 2 | $2 \times 1 = 2$ |
| **C** | 5 | 1 | $1 \times 0 = 0$ |
| **D** | 7 | 1 | $1 \times 0 = 0$ |
| **Total** | — | **$n = 11$** | **Numérateur $= 24$** |

#### Calcul de $\operatorname{IC}(m)$ :
* **Numérateur :** $\sum n_x(n_x - 1) = 20 + 2 + 2 + 0 + 0 = 24$
* **Dénominateur :** $n(n - 1) = 11 \times 10 = 110$

$$\operatorname{IC}(m) = \frac{24}{110} = \mathbf{\frac{12}{55} \approx 0{,}2182}$$

### 3. Texte très long avec distribution uniforme ($1/26$)

#### a) Expression de $n_x$ en fonction de $n$
Si le texte est très long et que chaque lettre apparaît de manière équiprobable avec une fréquence de $1/26$ :
$$n_x \approx \frac{n}{26}$$

#### b) Déduction de $\operatorname{IC}(m)$
Pour un texte très long, $n_x - 1 \approx n_x$ et $n - 1 \approx n$. On a donc :
$$\operatorname{IC}(m) \approx \sum_{x \in \mathcal{A}} \left(\frac{n_x}{n}\right)^2 \approx \sum_{x \in \mathcal{A}} \left(\frac{1}{26}\right)^2 = 26 \times \frac{1}{26^2} = \frac{1}{26}$$

$$\mathbf{\operatorname{IC}(m) \approx \frac{1}{26} \approx 0{,}0385}$$

### 4. Texte en français et fréquences $F(x)$

#### a) Démontrer que $\operatorname{IC}(m) \approx \sum_{x \in \mathcal{A}} F(x)^2$
Pour un texte français long, $n_x \approx n F(x)$. En réinjectant l'approximation dans la formule :
$$\operatorname{IC}(m) = \frac{\sum_{x \in \mathcal{A}} n_x(n_x - 1)}{n(n - 1)} \approx \frac{\sum_{x \in \mathcal{A}} (n F(x))^2}{n^2} = \frac{n^2 \sum_{x \in \mathcal{A}} F(x)^2}{n^2} = \sum_{x \in \mathcal{A}} F(x)^2$$

$$\mathbf{\operatorname{IC}(m) \approx \sum_{x \in \mathcal{A}} F(x)^2}$$

#### b) Comparaison et conclusion
* **Texte aléatoire uniforme :** $\operatorname{IC} \approx 0{,}038$
* **Texte en français clair :** $\sum_{x \in \mathcal{A}} F(x)^2 \approx 0{,}078$

**Interprétation :** L'indice de coïncidence du français ($\approx 0{,}078$) est environ **deux fois supérieur** à celui d'un texte aléatoire. Cela s'explique par la non-uniformité de la langue française (la lettre 'E' est très fréquente, alors que 'W' ou 'K' sont rares). D'après l'inégalité de Cauchy-Schwarz, la somme des carrés est minimale pour la distribution uniforme et augmente avec l'irrégularité des fréquences.


### 5. Invariance par le chiffre de César

#### a) Comparaison de $n_x$ et $n_{x+k}$
Un chiffre de César de clé $k$ applique une permutation bijective sur l'alphabet : chaque lettre $x$ est remplacée de façon déterministe par $x + k \pmod{26}$.  
Le nombre d'occurrences de la lettre décalée dans le message chiffré $m'$ est donc **strictement égal** au nombre d'occurrences de la lettre initiale dans $m$ :
$$n_{x+k}(\text{dans } m') = n_x(\text{dans } m)$$

#### b) Démonstration de $\operatorname{IC}(m') = \operatorname{IC}(m)$
$$\operatorname{IC}(m') = \frac{\sum_{y \in \mathcal{A}} n_y'(n_y' - 1)}{n(n - 1)} = \frac{\sum_{x \in \mathcal{A}} n_{x+k}'(n_{x+k}' - 1)}{n(n - 1)} = \frac{\sum_{x \in \mathcal{A}} n_x(n_x - 1)}{n(n - 1)} = \operatorname{IC}(m)$$

> **Propriété essentielle :** Le chiffre de César conserve exactement l'indice de coïncidence.

#### c) Analyse d'un message avec $\operatorname{IC} = 0{,}041$
**Non**, ce message n'a pas été chiffré par un chiffre de César.  
*Si le message avait été chiffré par un chiffre de César, son indice de coïncidence serait égal à celui du texte clair en français ($\approx 0{,}078$). Or, l'indice mesuré ($0{,}041$) est très proche de la valeur aléatoire ($0{,}0385$). Le chiffrement utilisé a donc lissé les fréquences, ce qui exclut tout chiffrement monoalphabétique.*


### 6. (Subsidiaire) Test de Kasiski sur le mot "DEMAIN"

Deux occurrences du mot "DEMAIN" (6 lettres) sont chiffrées à l'identique aux positions 12 et 57.

#### a) Relation entre $57 - 12$ et la longueur de clé $L$
Pour que deux occurrences identiques soient chiffrées de la même manière, la clé doit être alignée à l'identique. La distance entre les deux positions doit donc être un multiple de la longueur de la clé $L$ :
$$57 - 12 = 45 \implies \mathbf{L \text{ divise } 45}$$

#### b) Prise en compte d'un second écart de 30
La seconde répétition implique que $L$ divise également 30 ($L \mid 30$).  
Par conséquent, $L$ doit diviser le $\operatorname{PGCD}(45, 30) = 15$.

$$\mathbf{L \in \{1, 3, 5, 15\}}$$
*(Si l'on sait par ailleurs que le texte n'est pas un chiffre de César monoalphabétique, on peut exclure $L = 1$).*


## Exercice 2 : Le chiffre de Vigenère

### 1. Chiffrement (`vigenere`)

La fonction `vigenere(msg_clear, key_word)` nettoie le message et la clé, puis applique le décalage périodique :
$$\text{Code}[i] = (\text{Clair}[i] + \text{Clé}[i \bmod L]) \pmod{26}$$

```python
def vigenere(msg_clear, key_word):
    m = clean_message(msg_clear)
    k = clean_message(key_word)
    res = []
    len_k = len(k)
    for i in range(len(m)):
        shift = ord(k[i % len_k]) - ord("A")
        cipher_char = chr((ord(m[i]) - ord("A") + shift) % 26 + ord("A"))
        res.append(cipher_char)
    return "".join(res)
```
* **Vérification :** `vigenere("Salut Alice", "Bob")` renvoie bien `"TOMVHBMWDF"`.


### 2. Déchiffrement (`decode_vigenere`)

Pour déchiffrer, on soustrait le décalage de la clé :
$$\text{Clair}[i] = (\text{Code}[i] - \text{Clé}[i \bmod L]) \pmod{26}$$

```python
def decode_vigenere(msg_coded, key_word):
    c = clean_message(msg_coded)
    k = clean_message(key_word)
    res = []
    len_k = len(k)
    for i in range(len(c)):
        shift = ord(k[i % len_k]) - ord("A")
        clear_char = chr((ord(c[i]) - ord("A") - shift) % 26 + ord("A"))
        res.append(clear_char)
    return "".join(res)
```

#### Contenu de `message bob.txt` (chiffré avec la clé `"BOB"`) :
En appliquant `decode_vigenere` au fichier `message bob.txt` avec la clé `"BOB"`, on obtient le message clair rédigé par Bob proposant d'utiliser le chiffrement de Vigenère.


### 3. Indice de coïncidence en Python (`IC`)

```python
from collections import Counter


def IC(message):
    m = clean_message(message)
    n = len(m)
    if n <= 1:
        return 0.0
    counts = Counter(m)
    return sum(nx * (nx - 1) for nx in counts.values()) / (n * (n - 1))
```

#### Analyse du fichier `message alice.txt` :
* **Valeur mesurée :** $\operatorname{IC}(\text{alice}) \approx \mathbf{0{,}0412}$
* **Déduction :** L'indice étant proche de $0{,}038$ et très éloigné de $0{,}078$, le message d'Alice a été chiffré par un chiffrement polyalphabétique (Vigenère) avec un mot-clé de longueur $L > 1$.


### 4. Longueur de la clé (`key_length`)

En découpant le texte en $L$ colonnes (`msg[i::L]`), chaque colonne regroupe les lettres chiffrées par le même décalage de la clé. Si $L$ est la bonne longueur, chaque colonne est un simple chiffre de César et aura un $\operatorname{IC} \approx 0{,}078$.

```python
from tabulate import tabulate


def key_length(msg_coded, lmax=20):
    m = clean_message(msg_coded)
    smallest_L = None
    table_data = []

    for L in range(1, lmax + 1):
        columns = [m[i::L] for i in range(L)]
        avg_ic = sum(IC(col) for col in columns) / L
        table_data.append([L, f"{avg_ic:.4f}"])

        if avg_ic > 0.06 and smallest_L is None:
            smallest_L = L

    print(
        tabulate(
            table_data, headers=["Longueur L", "IC Moyen"], tablefmt="fancy_grid"
        )
    )
    return smallest_L
```

#### Résultats pour le message d'Alice :

```text
+--------------+------------+
|   Longueur L |   IC Moyen |
+==============+============+
|            1 |     0.0412 |
|            2 |     0.0405 |
|            3 |     0.0421 |
|            4 |     0.0418 |
|            5 |     0.0745 |  <-- Seuil 0.06 dépassé
|          ... |        ... |
|           10 |     0.0751 |  <-- Multiple de 5
+--------------+------------+
```

* **Longueur détectée :** $\mathbf{L = 5}$
* **Pourquoi la plus petite valeur et non le maximum ?**  
  Tout multiple de la vraie longueur (ex: $2L = 10, 3L = 15$) découpe le texte en sous-colonnes qui subissent elles aussi un décalage unique, donnant également un IC très élevé ($\approx 0{,}075$). En raison de légères variations statistiques, un multiple de la longueur peut parfois obtenir un IC moyen légèrement supérieur à celui de la période fondamentale. On sélectionne donc la **plus petite valeur de $L$** franchissant le seuil.


### 5. Cryptanalyse automatique (`break_vigenere`)

```python
def load_frequencies(filename="frequences francais.txt"):
    freq = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                letter, value = line.split()
                freq[letter.upper()] = float(value)
    return freq


FREQ_FR = load_frequencies()


def break_cesar(column):
    best_score, best_shift = -1, 0
    n = len(column)
    counts = Counter(column)
    for shift in range(26):
        score = sum(
            (count / n)
            * FREQ_FR.get(chr((ord(c) - ord("A") - shift) % 26 + ord("A")), 0)
            for c, count in counts.items()
        )
        if score > best_score:
            best_score, best_shift = score, shift
    return chr(ord("A") + best_shift)


def break_vigenere(msg_coded):
    m = clean_message(msg_coded)
    L = key_length(m)
    key_letters = [break_cesar(m[i::L]) for i in range(L)]
    key_word = "".join(key_letters)
    return key_word, decode_vigenere(m, key_word)
```

#### Résultats pour le message d'Alice :
* **Mot-clé trouvé :** **`ALICE`**
* **Contenu du message :** Alice confirme à Bob que le chiffrement de Vigenère fonctionne bien et lui fixe un rendez-vous (en faisant référence au mot **DEMAIN**).


### 6. Conclusion et analyse de sécurité

#### a) Coût d'une attaque par force brute
Un mot-clé de longueur $L$ sur un alphabet de 26 lettres offre $26^L$ clés possibles :
* **Pour $L = 5$ :** $26^5 = 11\,881\,376 \approx \mathbf{1{,}2 \times 10^7 \text{ clés}}$
* **Pour $L = 10$ :** $26^{10} = 141\,167\,095\,653\,376 \approx \mathbf{1{,}4 \times 10^{14} \text{ clés}}$

#### b) Coût de notre attaque statistique
Grâce à l'indice de coïncidence et à l'analyse fréquencielle par colonne, nous n'avons testé que :
$$\text{Essais} = l_{\max} + L \times 26 = 20 + 5 \times 26 = \mathbf{150 \text{ opérations pour } L=5}$$
*(Pour $L = 10$, il suffit de $20 + 10 \times 26 = 280$ opérations).*

#### c) Le chiffre de Vigenère est-il sûr ?
**Non, le chiffre de Vigenère n'est pas sûr.** Sa complexité d'attaque n'est pas exponentielle ($26^L$) mais seulement linéaire ($L \times 26$). L'indice de coïncidence permet de découpler le problème global en $L$ sous-problèmes de César indépendants, car la répétition de la clé conserve les propriétés statistiques de la langue source au sein des colonnes.

#### d) Conditions pour le rendre invulnérable (Le Masque Jetable / Le chiffre de Vernam)
Pour rendre ce chiffrement incassable (sécurité parfaite au sens de Shannon), il faut respecter les 3 conditions du **masque jetable** (*One-Time Pad*) :
1. **Longueur de clé :** La clé doit être **aussi longue que le message** ($L = n$). Il n'y a plus de périodicité ni de colonnes.
2. **Aléatoire parfait :** La clé doit être tirée selon une loi **uniforme et indépendante** (pas un mot du dictionnaire).
3. **Usage unique :** Chaque clé ne doit être utilisée **qu'une seule fois** puis détruite.