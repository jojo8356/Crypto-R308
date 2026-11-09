from color import *
from cesar import *

Exercice("Chiffrement César")

Question("1. Prétraitement du message à chiffrer")
message="Bonjour Alice !"

print("Message initial :");print(message);
message=clean_message(message)
print("Message pretraité :");print(message);

Question("2. Chiffrement")
print(cesar(message,3))
print(cesar(message,30))
print(cesar(message,-3))

Question("4. Décryptage brute force")
message=cesar(message,5); brute_force(message)

Question("5. Calcul des fréquences")
print(F("AAABBAAAZZ"))

Question("6. Fréquences de référence")
print(charge_frequences())

Question("7. Fonction coût")
print(J("ABCQSDFSDFAZE"))

Question("8. Décryptage")
message=cesar("Le monde entier est un cactus, il est impossible de s'assoir",5)
print(break_cesar(message))

