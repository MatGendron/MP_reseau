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