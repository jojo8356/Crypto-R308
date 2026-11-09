# TP6 — Code correcteur d'erreur de Hamming

Rendu du TP6 de Cryptographie R309 (sujet : `Hamming.pdf`).

## Contenu

| Fichier | Rôle |
| :-- | :-- |
| `hamming.py` | **le rendu** : les 13 fonctions demandées, et rien d'autre (ni variable globale, ni test) |
| `test-hamming.py` | script de test fourni avec le sujet (non modifié) |
| `responses.md` | source du compte-rendu : réponses rédigées, code, tableaux de vérification |
| `rendu.pdf` | compte-rendu complet, généré depuis `responses.md` (25 pages) |
| `verification.py` | vérifications expérimentales citées dans le compte-rendu (Q9, Q10, Q13…) |
| `resultats-verification.txt` | traces produites par `verification.py` |
| `md2pdf.py` | convertisseur Markdown → PDF (reportlab + polices DejaVu, sans réseau) |
| `Hamming.pdf` | sujet |

## Utilisation

```sh
python3 test-hamming.py                       # doit afficher 13 / 13
python3 verification.py                       # régénère resultats-verification.txt
python3 md2pdf.py responses.md rendu.pdf      # reconstruit le compte-rendu
```

`hamming.py` n'importe que `randint` du module standard `random` ; les outils de
rédaction (`verification.py`, `md2pdf.py`) ne font pas partie du rendu Moodle.

## Contenu algorithmique

- `int2bits`, `bits2int` : conversions entier ↔ tableau de bits (poids faible en premier) ;
- `generate_message`, `formatage` : message aléatoire et insertion des positions de contrôle ;
- `XOR`, `test_hamming`, `set_correctors`, `codage_hamming` : calcul du syndrome et des bits de contrôle ;
- `swap`, `decodage` : localisation et correction d'une erreur unique par le syndrome ;
- `parite`, `codage_hamming2`, `decodage2` : code de Hamming étendu (SECDED), qui corrige une erreur et détecte les erreurs doubles.

Deux fonctions auxiliaires, `est_controle` et `positions_message`, factorisent le test
« position de contrôle » utilisé par quatre fonctions.
