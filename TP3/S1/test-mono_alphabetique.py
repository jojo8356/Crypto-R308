from color import *
from mono_alphabetique import *

Exercice(1)

Alphabet=[chr(k) for k in range(65,65+26)] # Lettres majuscules {A,...Z}
Question("1. Prétraitement du message à chiffrer")
message="La cryptographie est une des disciplines de la cryptologie s'attachant à protéger des messages (assurant confidentialité, authenticité et intégrité) en s'aidant souvent de secrets ou clés."

print("Message initial :");print(message);
Question("1.a")
message=preprocess_message(message)
print("Message pretraité :");print(message);
Question("1.b")
message=clean_message(message,Alphabet)
print("Message formaté :");print(message);

Question("2. Conversion key <-> string")
key=string_2_key('OCMETUVQBNDRYFWJLGHXSKIAZP',Alphabet);
print("On utilise la clé ",key_2_string(key,Alphabet));

Question("3. Chiffrement monoalphabétique")
print("Le message formaté chiffré avec la clé précédente : ");
message_chiffre=substitution(message,key)
print(message_chiffre)

Question("4. Déchiffrement")
invert=inverse_key(key)
print("Clé inverse de ",key_2_string(key,Alphabet),"=",key_2_string(invert,Alphabet))
print("message déchiffré=",substitution(message_chiffre,invert));

Question("5. Génération de clés")
new_key=random_key(Alphabet)
print("Une clé aléatoire=",key_2_string(new_key,Alphabet),color.RED+" !!! le résultat est ici aléatoire");

Question("7. Calcul des fréquences ")
Question("7.a Fréquences de références")
Fref=load_monogrammes()
print("Les fréquences de référence sont ");print(Fref)
Question("7.b Fréquences du message chiffré")
print("Pour le message chiffré")
print(message_chiffre)
print("Les fréquences des monogrammes sont ");print(F(message_chiffre,Alphabet))

Question("8. Évaluation de J1")
print("La valeur de J1 pour le message chiffré est ",J1(message_chiffre,Fref))

Question("9. Minimisation de J1")
guessed_key=minJ1(message_chiffre,Fref)
print("La clé minimisant J1=",key_2_string(guessed_key,Alphabet))
guessed_message=substitution(message_chiffre,guessed_key);
print("Le minimum de J1 est ",J1(guessed_message,Fref))
print("Le message après analyse fréquentielle sur les monogrammes=")
print(guessed_message)
print(color.RED+"Attention, il existe potentiellement plusieurs solutions : il existe potentiellement plusieurs minimiseurs de J1 (i.e. plusieurs clés qui conduisent à la même valeur du minimum de J1)");

Question("10. Test de l'algo de décryptage")
proust= clean_message(preprocess_message(open("proust.txt","r",encoding="utf-8").readline()),Alphabet)
guessed_inverse_key=minJ1(proust,Fref)
print("La clé minimisant J1=",key_2_string(guessed_inverse_key,Alphabet)," vs ","".join(Alphabet))
print("Le début du message après analyse fréquentielle sur les monogrammes=")
print(substitution(proust[:50],guessed_inverse_key))
print("vs")
print(proust[:50])
#print("".join(Alphabet))
#print(compare_keys(guessed_inverse_key,string_2_key("".join(Alphabet),Alphabet),Alphabet))
