# Rapport Mini-Projet Réseaux  
## Chat à la IRC  
## Gendron Mathis, Alexandre Vialar

### Bref 

Le but de ce projet est de réaliser les aspects client et serveur d'un chat sur le modèle du protocole IRC.  
Pour ce faire nous avons repris le travail réalisé pour la dernière partie du TP5, le protocole utilisé reste donc TCP, en IPv4 comme demandé par le sujet. Comme pour le TP5, nous avons principalement utilisé la librairie socket de python.  

### Premières étapes

La première version du programme était une implémentation sommaire des fonctions demandées pour la V0 et comme pour le TP5, seul l'aspect serveur était développé, les clients étant gérés par netcat. Ce n'est que plus tard dans le développement que nous avons développé notre propre client.

#### Client, première version

La première version du client a été développée à partir d'instructions sommaires données par notre professeur de TD  cependant, cette première implémentation posait des problèmes de synchronisation, en plus de n'afficher par elle-même qu'une partie des messages envoyés par le serveur, en afficher la totalité demandant demendant au client de faire des retour à la ligne (boucle principale de cette version en annexe 1.1).

Les problèmes de ce premier code client ont été majoritairement réglés par la réécriture de la boucle principale sur le modèle de la boucle du serveur (voir annexe 1.2).

A ce stade un problème majeur subsiste : lorsqu'un client se connecte au serveur, celui-ci cesse de traiter les demandes des autres clients, ce problème était du au code serveur.

#### Serveur, première version

Le serveur emploie depuis sa première version des dictionnaires afin de stocker les informations concernant les utilisateurs et les canaux de discussion.

La méthode select.select est utilisé pour déterminer si une socket est en cours de connexion ou si un message est envoyé par une socket déjà connectée.  
Le problème client mentionné précédemment provenais du fait qu'un pseudo et un premier canal à rejoindre était demandés au moment de la connexion, le serveur ne pouvais pas effectuer d'autres actions, et donc pas servir les autres clients, tant que ces deux éléments n'étaient pas renseignés.  
Ce problème a été réglé en sortant la demande de pseudo et de premier canal de la conditionnelle liée à l'établissement d'une connexion.

En règle générale, le serveur utilise la méthode socket.recv pour recevoir un message de la socket client et socket.send pour renvoyer un message sur celle-ci.

Les commandes ont toutes été implémenté à l'aide de conditionnelles sur le contenu des messages reçus par le serveur.

### Détail des fonctionnalités

### V0

#### HELP

La commande HELP provoque un simple envoit du message contenant la liste des commandes et leurs descriptions.  
Aucun problème n'a été rencontré lors de l'implémentation de cette commande.

#### LIST

La commande LIST entraîne un simple parcours de la liste des canaux et l'envois de ceux-ci aux client ou \*No channels\* si aucun canaux n'existe.  
L'implémentation de cette commande a été sans problème et les seuls améliorations étaient plus d'ordre cosmétique.

#### JOIN

La commande JOIN ajoute le client au dictionnaire du canal passé en paramètre et créé le canal en ajoutant une nouvelle entrée au dictionnaire des canaux si le canal n'existe pas déjà.  
Cette fonction a été peu changée suite à sa première version, seulement pour des problèmes liées à d'autres commandes.

#### LEAVE

Cette commande conduit simplement le serveur a retirer le client des dictionnaires liés à un canal, ce qui l'empêche effectivement d'y communiquer.  
Pas de problèmes lors de l'implémentation, elle a seulement demandé l'implémentation d'une fonction permettant de vérifier si le client était effectivement dans un canal.

#### WHO 

Simple parcours et envoit de la liste des clients, désignés par leurs pseudos, dans un canal à la socket effectuant la commande.
L'implémentation de base n'a pas posé de problème.

#### \<message\>

Envoi d'un message à tous les clients dans un canal de discussion.  
L'envoi d'un tel message est masqué par la commande PRINT, ajouté à un message sans commande côté client.  
Une fonction permettant d'envoyer un message à tous les clients présent dans un canal a été développée pour cette commande. La subtilité étant qu'un message ne soit pas renvoyé à son émetteur afin d'éviter les doublons côté client.

#### MSG

Implémenté sans trop de problème pour la V0, simple envoit du message donné vers le client concerné.  
L'implémentation de cette fonction a seulement été sujet à quelques problèmes de compilation.

#### BYE

Cette commande exige que le client soit en dehors de tout canal.
Retire le client du dictionnaire général des clients sur le serveur et ferme la socket client.  
Cette fonction a occasionnellement posé des problème lors des tests car dans sa première version, un message particulier était envoyé à la socket client, ce qui provoquait la fermeture de celle-ci et l'arrêt du programme au sein du code client. Cette solution était peu fiable et le traitement basé sur l'envoi au client d'une chaîne de caractère vide par la méthode socket.close implémenté dans la version finale n'est plus sujette aux erreurs.

### Aspect Admin

L'aspect admin de la V0 a été implémenté en faisant correspondre une liste d'utilisateurs à chaque canal, le premier utilisateur dans la liste étant désigné comme admin.  
Des modifications aux commandes JOIN, LEAVE, et WHO ont été apportés pour gérer cet aspect à l'aide de ladite liste.

#### KICK 

Cette fonctionnalité reprend le code de LEAVE mais vérifie au préalable que la personne l'utilisant a les droit d'admin.  
Un certain temps a été passé sur l'implémentation de cette fonction car le test VPL associé échouait, ne constatant aucun problème la fonction a été laissée comme à l'origine et il s'est avéré que le test VPL considéré la fonction comme correctement implémentée un peu plus tard.

#### REN

Le renommage d'un canal s'effectue en appelant la méthode .pop sur les dictionnaire et liste du canal à renommer pour placer ceux-ci dans un canal avec le nouveau nom.  
Le code de cette commande vérifie de même que le client qui l'utilise est admin.  
Aucun problème pour développer cette fonctionnalité.

### V1

#### NICK 

La commande NICK vérifie que le pseudo passé en paramétre n'est pas déjà employé par un autre client et remplace le pseudo du client dans les dictionnaires \[socket\]:pseudo général et du canal où il est présent.
Utilisation d'un booléen servant de flag pour déterminer à l'aide d'un parcours de la liste des clients si un pseudo est déjà utilisé.
Si ce booléen est vrai, le nom donné est déjà utilisé et est donc refusé.

Nous avions tout d'abord pensé que le pseudo demandé à la connection devait être donné à l'aide de cette commande et avont réalisé une implémentation en conséquence mais les tests VPL nous ont fait prendre connaissance du contraire, la première input côté client à la connexion devant servir de pseudo, ce qui a posé son lot de problème.  
La gestion de ce cas particulier a d'abord été effectuée côté client avant d'être réeffectuée côté serveur pour des raison de stabilité.  
A la connexion, un client est donné un pseudo provisoire indiquant que le serveur est en attente d'un pseudo pour ce client et toute autre input que la commande /BYE est considérée comme le pseudo du client s'il est valide (Pas une potentielle commande ou une chaîne de caractères vide).
Le client ne peut pas utiliser les autres commandes (à part /BYE) tant qu'il n'a pas renseigné un pseudo.

#### MSG a plusieurs utilisateurs

Cette fonctionnalité est implémentée en découpant la liste d'utilisateurs de la forme \<nick1;nick2;etc...\> selon les point-virgules à l'aide de la méthode str.split et en envoyant le message donné à chacun de ces utilisateurs.
Passé quelques erreurs à la compilation, son développement n'a pas posé problème.

### Autres fonctionnalités

#### KILL et BAN

KILL et BAN reprennent essentiellement le code de BYE à la différence que ces commandes peuvent seulement être saisie côté serveur, dont l'input est récupérée à l'aide de sys.stdin, comme pour le client.
Un échec des tests VPL était provoqué par la non verification qu'une input avait une longueur strictement positive, mais une fois ce problème réglé les fonctionnalités se comportaient correctement, en revanche, un oubli au moment de l'écriture de ce rapport subsiste et les deux fonctionnalités ne retire par le client concerné des canaux où il est présent.
BAN ajoute en plus le l'IP du client, récupérée à l'aide de socket.getpeername, à une liste d'adresses interdite, cette fonctionnalité n'a pas pu être testée, les clients ayant tous la même IP dans notre environnement de test.

### Autres Notes

* Un certain temps a été passé à faire en sorte que le client et le serveur se comporte bien dans le cas ou l'un d'eux recoivent un signal d'interruption (Ctrl+C), ceci a été fait à l'aide de la bibliothèque signal.
* Git au travers de GitHub a été employé pour faciliter le développement.

## Annexe 

### 1.1
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
### 1.2
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