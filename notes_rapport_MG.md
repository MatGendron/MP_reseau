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

### Leave et Bye

Aucun problème lors de leur implémentation

Ajout fonction permettant de vérifier si une socket est dans n'importe quel canal -> petit problème parce qu'utilise liste channel directement dans cette fonction et code était pas tout de suite dans le bon ordre pour le permettre.

Ajout identifiant (nick) au début des messages textuels.

### Système d'admin:
Peut utiliser list(d) pour obtenir la liste des clés d'un dictionnaire par ordre d'insertion

Problème sur NICK pour admin au début parce que savait pas dans quel ordre était stocké nouveaux utilisateurs dans dict d'un channel

Problème: list(d) ne donne en fait pas les valeurs par ordre d'insertion, ou plutot les éléments ne sont pas inséré dans un dictionnaire par ordre d'insertion
Doit trouver autre solution
--> Création d'une liste de sockets pour chaque channel, socket à indice 0 a les droits d'admin

Fix commande /LIST pour afficher "*No channels*"

Ajout aspect dernier client à quitter un channel cause sa fermeture

Note : inconsistence dans affichage de certaines infos -> peut y a avoir retours à la ligne dans infos rendues par /WHO ou /LIST ou non

Ajout commandes KICK et REN -> check si dans un canal, check si admin -> message d'erreur sinon
* KICK : même code que pour /LEAVE
* REN : pop ancien chan dans clé avec nouveau nom

### HELP
Ajout fonction HELP, simple recopie dans un send de ce qui est donné dans le sujet du projet.

## 29 avril

### MSG nick1;nick2;nick3;...

Reprise du code pour le /MSG de la V0 -> petit problèmes pour construire liste de destinataire du message à cause de break mal placé. Pour le moment implémenté que pour nick dans le même canal.

### Git tag

Ajout tag à l'aide de git sur le commit de la V0 finie.

##KILL et BAN

Problème avec BAN : peut pas tester maintenant parce que peut pas utiliser couple (IP,port) récupéré à l'aide de socket.getpeernam() mais le port de connexion changeant à chaque appel du programme client.py, cette méthode n'est pas utilie, il faudrait donc faire un ban uniquement sur l'adresse IP elle-même mais dans notre environnement cela empêcherait toute nouvelle connexion.