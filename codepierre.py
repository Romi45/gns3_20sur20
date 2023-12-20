import telnetlib
import gns3fy

def configurer_router(id, protocole, username, password) :

	#ouvrir une ocnnexion telnet avec le router
	tn = telnetlib.Telnet(hostname, port)

	#attendre à que le router réponde
	time.sleep(2)

	#username
    tn.read_until(b"Username: ")
    tn.write(username.encode('ascii') + b"\r")

    #password
    tn.read_until(b"Password: ")
    tn.write(password.encode('ascii') + b"\r")


    #configuration en fonction du protocole
    #fonctions intéressantes
    for command in commands:
        tn.write(b"enable\r")
        time.sleep(1) #attendre à l'execution de la commande pour éviter le chevauchement
        tn.write(b"cisco\r")
        time.sleep(1)
        tn.write(b"conf t\r")
        time.sleep(1) 
        ...  

    #fermer la connexion telnet
    tn.write(b"exit\r")
    tn.close()