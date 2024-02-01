# Network Automation Project

## Presentation
The aim of the project is to write a code that deploys different routing protocols across a given network. This network is defined in an `intent_file`. We want our code to be able to set 3 different types of protocol :
- **RIP** or **OSPF** to route within an autonomous system (AS)
- **BGP** to route between different AS's


## First approach
To get a first glimpse of our project, we started by configurating the following given network, counting only 2 AS's:

![Alt text](https://image.noelshack.com/fichiers/2024/05/2/1706624263-captura-de-pantalla-2024-01-30-151411.png)

We consider that the owner of AS X wants to deploy RIP in its network, while the owner of AS Y wants to deploy OSPF. BGP will need to be deployed between the AS's in order for them to communicate with each other. We use GNS3 to build the network topology.

## Configuration

We therefore need to create a code that allows us to manipulate the consoles of each router in order to configure IPv6 addresses to each of them and assign them different protocols based on their necessities. There are different ways of dealing with this situation. We decided to use the `telnet` protocol, which allows us to establish TCP/IP connexions and access a distant machine. 


This is how our code works eventually :

- We first retrieve the nodes local ports of the GNS3 project. In order to start a telnet connection to their consoles.
- Then we scan the JSON `intent_file`, where every router of the network is precised, along with its IPv6 addresses, the type of protocol based on its neighbors and more.
- Thanks to telnet and by running "if" tests we configure every router. For example, if the router's IGP is set to OSPF in the `intent_file`, then the code calls the `setup_ospf` function to set the router to ospf, and then calls the `ospfconf_area` function to set up the OSPF area. There is a different setup function for all 3 protocols and situations, as well as for making the address plan of the network. A configuration of a random router in the `intent_file` can be seen in the image below.

![Alt text](https://image.noelshack.com/fichiers/2024/05/4/1706783749-capture-d-ecran-du-2024-02-01-00-07-17.png)

We can see that every router is represented in the JSON, along with its specificities (as_number, router-id...).

### Deepening
Ultimately and as add-ins, we decided to implement some other caracteristics to our code.

#### OSPF metrics 
If the `intent_file` specifies it, OSPF cost can be set in order to influence the routing by calling the `ospfconf_cost` function. 

#### Logs
To modify the router configurations without having to completely reset them, it was crucial to implement a logging system. Our strategy involved maintaining the current state of all routers by keeping the previous intent_file. This allows us to reconfigure only the elements that have changed between the last and current configuration.

It's important to note, our code is divided into two scripts. The first, init_config.py, is designed to initialize all routers by sending all commands without concern for the previous state (assuming their configurations were blank prior to using this program). Then, the second script, update_config.py, relies on the differences between the two intent_files to send only the necessary modifications.

However, the logs do not account for BGP communities and local preference as we did not have time to implement these features. Similarly, they do not consider the addition or removal of routers, nor the addition or removal of interfaces on routers.

#### Communities
We also decided to implement BGP communities. (Jean)

### Reseting the routers
In order to facilitate testing our codes on routers without initial configuration, we have implemented a script that removes the configuration from all routers in a GNS3 project. Here is how reset_all_routers.py works:

-Close the GNS3 project and then run reset_all_routers.py.

-The code deletes all configuration files of the routers.

-Restart GNS3 and power on all routers. Wait until the "Do you want to enter initial configuration" menu appears.

-Press enter in the terminal of reset_all_routers.py to send "no" to all routers.

-There you go!

---


Finally, we achieve to automate the setting of almost any network, as long as an `intent_file` clarifying the specificities of this network is given. We decided to use the following network as a test for a more complex topology : 

![Alt text](https://image.noelshack.com/fichiers/2024/05/2/1706629657-image.png)

We find that the results are satisfactory and the software has automated the generation of router configuration.
