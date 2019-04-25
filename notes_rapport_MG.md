## 23 avril
### Premier commit

Problème pas tous qui s'affiche forcément côté client, besoin d'un retour à la ligne a plusieurs reprises
pour afficher suite de ce qui est envoyé par serveur, pas de synchronisation entre les clients
Broken Pipe error avec plus de deux clients, nick pas demandé sur second client tant que tout a pas été renseigné
sur le premier

Proviens plus probablement du code client

```python
while True:
  reading, writing, exceptional = select.select(liste,[],[])
  for r in liste:
    ##problem: stdin ends up in reading and can't do a recv on it
      if r in reading:
        if r!=sys.stdin:
          d = r.recv(LIMIT).decode("utf-8")
          print(d)
      if r in exceptional:
        r.close()
        exit()
      if r == sys.stdin:
        l = r.readline()
        if l[0] == '/': #command
            l = l[1:] + " "
            print(l)
        else:
            l = "PRINT " + l
        s.send(l.encode("utf-8"))
```

### Fix premier commit

Réécriture de la boucle principale côté client sur le modèle de ce qui avait été fait pour le select côté serveur

```python
while True:
	reading, writing, exceptional = select.select(liste,[],[])
	for r in reading:
		if r in exceptional:
			r.close()
			exit()
		if r!=sys.stdin:
			d=r.recv(LIMIT).decode("utf-8")
			print(d)
		else:
			l=r.readline()
			if l[0]=='/':
				l=l[1:]+" "
				print(l)
			else:
				l="PRINT "+l
			s.send(l.encode("utf-8"))
```

* Fix message envoyé du client au serveur s'affichant as en intégralité sans enter cpoté serveur
* Client parviens maintenant jusqu'à stade où peut écrire
Problèmes : 
* Un seul client à la fois reçoit demande pour NICK
* Message envoyé dans un channel est encore réimprimé chez la personne qui l'a envoyé, créant des doublons
* Personne prenant un NICK déjà existant pas traité correctement


### Suite

Difficultés pour fix nick déjà utilisé essayé avec un booléen pour empêcher d'ajouter l'adresse à la liste des adresse, développé un peu la hâte, doit mieux y réfléchir, mis en attente pour le moment

Quickfix en rajoutant une exception dans la fonction send_cnl pour qu'un message soit pas renvoyé à son émetteur

### Fix commande
Après avoir fait un rstrip sur la commande, tout fonctionne sauf si un client est en attente de connexion -> gros problème ?

## 25 avril

Confirmation problème d'hier : si un client est en train de se connecter au serveur, les clients déjà connectés ne peuvent pas envoyer ou recevoir d'information du serveur. Entraîne envoit d'infos innatendues aux clients déjà connectés une fois que le client qui était en train de se connecter au serveur a finit (PRINT test_msg ayant était envoyé à un des clients)

Idée pour résouble problème : sortir code pour demander nick et premier canal du if i==s.

Fini de dev commande MSG, doit éventuellement rajouter nom de la source, faire plus de tests
* MSG pas envoyé à quelqu'un autre canal OK

### Implémentation commande MSG 
Passé problème à la compilation due à réutilisation de code précédent, pas de problème pour dev cette fonction

### Fix serveur peut pas traiter autres client si en client est en train de se connecter

Déplacement du code pour demander un NICK et rejoindre un channel hors du if i==s côté serveur, petits problèmes dut à réutilisation de code mais sans plus

### Fix NICK déjà prit
Pour une raison que j'ignore,
```python
if argument in lclt:
```
argument étant le NICK donné par l'utilisateur et lclt un dictionnaire dont les clés sont les sockets et les valeurs les nick ne fonctionnait pas pour déterminer si un un nick était déjà utilisé par un client, ai du faire
```python
bad_nick=False
for clt in lclt:
  if argument==lclt[clt]:
    bad_nick=True
    break
if bad_nick:
```

### Quickfix 
Ligne pour dire d'utiliser commande list pour afficher canaux et demande de rejoindre un canal s'affichait pas si canaux déjà existans, ligne de code correspondante était mal indentée 

Ajout code pour empêcher de join un Chan avant d'avoir choisit un nick