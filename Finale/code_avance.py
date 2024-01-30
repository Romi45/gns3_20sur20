import telnetlib
import time
from gns3fy import Gns3Connector, Project
import json
import os

nodes_info = {}
config_rip = "ipv6 router rip 0\rredistribute connected\rexit\r"
def telnet_to_node(config, port):
    try:
        tn = telnetlib.Telnet('localhost',port)
        time.sleep(1)
        tn.write(config)
        time.sleep(1)
        tn.write(b"end\r")
        time.sleep(1)
        tn.write(b"write\r")
        time.sleep(1)
        tn.write(b"\r")
        time.sleep(1)
        return 0
    
    except Exception as e:
        print("Could not open telnet session and/or send commands", e)
        return -1
    


def retrieve_nodes(project_name):

    server = Gns3Connector("http://localhost:3080")

    lab = Project(name=project_name, connector=server)
    
    lab.get()
    lab.open()

    for node in lab.nodes:
        node.get()
        nodes_info[node.name] = node.console


def setup_ospf(router_id):

    return ("ipv6 router ospf 1\r" + "router-id " + router_id + "\r" + "exit\r")

def ipv6(adresse_ip):
    return("ipv6 address " + adresse_ip + "\r")

def ripconf():

    return ("ipv6 rip 0 enable\r")

def ospfconf_area(ospf_area):

    return ("ipv6 ospf 1 area " + ospf_area + "\r")

def ospfconf_cost(ospf_cost):
    return("ipv6 ospf cost " + ospf_cost + "\r")


def bgpconf(id_AS,router_id,loopback_neighbors, ebgp, advertised_networks):
    #ebgp est un tuple qui a comme element un as voisin + ip_voisin
    bgp_string = "router bgp " + id_AS + "\rno bgp default ipv4-unicast\rbgp router-id " + router_id + "\r"
    
    for i in range (0,len(loopback_neighbors)):
        bgp_string += "neighbor " + loopback_neighbors[i] + " remote-as " + id_AS + "\r" + "neighbor " + loopback_neighbors[i] + " update-source Loopback0\r"
    
    if ebgp:
        bgp_string += "\rneighbor " + ebgp[1] + " remote-as " + ebgp[0] + "\r"

    bgp_string += "address-family ipv6 unicast\r"
    
    for i in range (0,len(loopback_neighbors)):
        bgp_string += "neighbor " + loopback_neighbors[i] + " activate\r"

    if ebgp:
        bgp_string += "neighbor " + ebgp[1] + " activate\r"

    for network_addrs in advertised_networks:
        bgp_string += f"network {network_addrs}\r"

    bgp_string += "exit\rexit\r"   
    return bgp_string


retrieve_nodes("communities_proj")
print(nodes_info)


config_string = ""
loopback_dict = {}
igp_type = ['RIP', 'OSPF']
igp = 0



with open('intent_file_jean.json') as json_file:
    data = json.load(json_file)

    for router, router_content in data.items():

        if router_content['as_number'] in loopback_dict:
            loopback_dict[router_content['as_number']].append((router_content['interfaces']['Loopback0']['ipv6_address']).replace('/128',''))
            
        else:
            loopback_dict[router_content['as_number']]=[(router_content['interfaces']['Loopback0']['ipv6_address']).replace('/128','')]
    
    for router, router_content in data.items():
        config_string = "end\renable\rconf t\ripv6 unicast-routing\r"
        as_number=router_content['as_number']

        if router_content["IGP"]=="RIP":
            igp=0
        else:
            igp=1


        if igp == 0:

            config_string += config_rip


        elif igp == 1:

            config_string += setup_ospf(router_content['Router_ID'])

        print(router)

        for interface, interface_content in router_content['interfaces'].items():
            config_string += "interface " + interface + "\ripv6 enable\rno shutdown\r"

            config_string += ipv6(interface_content['ipv6_address'])
                

            if igp == 0:
                config_string += ripconf()
                
            elif igp == 1:

                config_string += ospfconf_area(interface_content['ospf_area'])
                if interface != "Loopback0":
                    config_string+= ospfconf_cost(interface_content['ospf_cost'])
            
            

        ebgp = None

        if router_content['EBGP_Neighbor'] != None:
            ebgp = (router_content['EBGP_Neighbor']['as_number'], router_content['EBGP_Neighbor']['ipv6_address'])
        
        config_string += bgpconf(as_number,router_content['Router_ID'],loopback_dict[as_number],ebgp, router_content['advertised_networks'])

        print(config_string)

        telnet_to_node(config_string.encode(), nodes_info[router])
              