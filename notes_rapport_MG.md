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
