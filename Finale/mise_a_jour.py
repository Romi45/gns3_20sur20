import telnetlib
import time
from gns3fy import Gns3Connector, Project
from modules.comparer import compare_dicts, compareLoopbacks
import json
import shutil
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


retrieve_nodes("communities_proj")
print(nodes_info)

time.sleep(1)

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

intent_file_path = "intent_file.json"
old_intent_file_path = "old_intent_file.json"

intent_file = load_json(intent_file_path)
old_intent_file = load_json(old_intent_file_path)

differences = compare_dicts(intent_file, old_intent_file)
print(differences)



config_string = ""
loopback_dict = {}
old_loopback_dict = {}




for router, router_content in intent_file.items():

    if router_content['as_number'] in loopback_dict:
        loopback_dict[router_content['as_number']].append((router_content['interfaces']['Loopback0']['ipv6_address']).replace('/128',''))
    else:
        loopback_dict[router_content['as_number']]=[(router_content['interfaces']['Loopback0']['ipv6_address']).replace('/128','')]



for router, router_content in old_intent_file.items():

    if router_content['as_number'] in old_loopback_dict:
        old_loopback_dict[router_content['as_number']].append((router_content['interfaces']['Loopback0']['ipv6_address']).replace('/128',''))
    else:
        old_loopback_dict[router_content['as_number']]=[(router_content['interfaces']['Loopback0']['ipv6_address']).replace('/128','')]


differences_loopbacks=compareLoopbacks(old_loopback_dict,loopback_dict)
print(differences_loopbacks)



for router, router_content in intent_file.items():
    print(router)
    if router in differences:
        
        config_string = "enable\rend\rconf t\ripv6 unicast-routing\r"
        as_number=router_content['as_number']

        if router_content["IGP"]=="RIP":
            igp=0
        else:
            igp=1

        if 'IGP' in differences[router]:
            nouveau_igp=differences[router]['IGP'][0]
            ancien_igp=differences[router]['IGP'][1]

            if ancien_igp=='RIP':
                config_string+="no ipv6 router rip 0\r"
                config_string+=setup_ospf(router_content['Router_ID'])
            else:
                config_string+="no ipv6 router ospf 1\r"
                config_string+=config_rip

        if 'interfaces' in differences[router]:

            for interface, interface_content in router_content['interfaces'].items():
                if interface in differences[router]['interfaces']:
                    config_string += "interface " + interface + "\ripv6 enable\rno shutdown\r"

                    if 'ipv6_address' in differences[router]['interfaces'][interface]:
                        nouvelle_ipv6 = differences[router]['interfaces'][interface]['ipv6_address'][0]
                        ancienne_ipv6 = differences[router]['interfaces'][interface]['ipv6_address'][1]
                        config_string += "no ipv6 address "+ancienne_ipv6+"\r"
                        config_string += ipv6(nouvelle_ipv6)
                    
                    if 'IGP' in differences[router]:
                        if ancien_igp=='RIP':
                            config_string += "no ipv6 rip 0 enable\r"
                            config_string += ospfconf_area(interface_content['ospf_area'])
                            if interface != "Loopback0":
                                config_string+= ospfconf_cost(interface_content['ospf_cost'])
                        else:
                            config_string+="no ipv6 ospf cost\r"
                            config_string+=ripconf()

                    config_string+="exit\r"




        if 'as_number' in differences[router]:
            config_string+="no router bgp " + differences[router]['as_number'][1] + "\r"
            config_string+="router bgp " + router_content['as_number'] + "\rno bgp default ipv4-unicast\rbgp router-id " + router_content['Router_ID'] + "\r"
            for i in range (0,len(loopback_dict[router_content['as_number']])):
                config_string+= "neighbor " + loopback_dict[router_content['as_number']][i] + " remote-as " + router_content['as_number'] + "\r" + "neighbor " + loopback_dict[router_content['as_number']][i] + " update-source Loopback0\r"
            if router_content['EBGP_Neighbor']!=None:
                config_string+="neighbor "+router_content['EBGP_Neighbor']['ipv6_address']+ " remote-as "+router_content['EBGP_Neighbor']['as_number']+"\r"
            config_string+="address-family ipv6 unicast\r"
            for i in range (0,len(loopback_dict[router_content['as_number']])):
                config_string += "neighbor " + loopback_dict[router_content['as_number']][i] + " activate\r"
            if router_content['EBGP_Neighbor']!=None:
                config_string+="neighbor "+router_content['EBGP_Neighbor']['ipv6_address'] + " activate\r"
            for network in router_content['advertised_networks']:
                config_string+= f"network {network}"
            config_string+="exit\rexit\r"
        


        else:
            config_string+="router bgp " + router_content['as_number'] + "\r"
            if 'Router_ID' in differences[router]:
                config_string+="no bgp router-id " + differences[router]['Router_ID'][1]+"\r"
                config_string+="bgp router-id " +differences[router]['Router_ID'][0]+"\r"
            if router_content['as_number'] in differences_loopbacks:
                for address in differences_loopbacks[router_content['as_number']]['disparues']:
                    config_string+=(f"no neighbor {address}\r")
                for address in differences_loopbacks[router_content['as_number']]['nouvelles']:
                    config_string+= "neighbor " + address + " remote-as " + router_content['as_number'] + "\r" + "neighbor " + address+ " update-source Loopback0\r"
            if 'EBGP_Neighbor' in differences[router]:
                if differences[router]['EBGP_Neighbor'][1]!=None:
                    config_string+=(f"no neighbor {differences[router]['EBGP_Neighbor'][1]['ipv6_address']}\r")
                if differences[router]['EBGP_Neighbor'][0]!=None:
                    config_string+=("neighbor "+ differences[router]['EBGP_Neighbor'][0]['ipv6_address']+ " remote-as "+differences[router]['EBGP_Neighbor'][0]['as_number']+"\r")
            config_string += "address-family ipv6 unicast\r"
            if router_content['as_number'] in differences_loopbacks:
                for address in differences_loopbacks[router_content['as_number']]['disparues']:
                    config_string+=(f"no neighbor {address} activate\r")
                for address in differences_loopbacks[router_content['as_number']]['nouvelles']:
                    config_string+=(f"neighbor {address} activate\r")
            if 'EBGP_Neighbor' in differences[router]:
                if differences[router]['EBGP_Neighbor'][1]!=None:
                    config_string+=(f"no neighbor {differences[router]['EBGP_Neighbor'][1]['ipv6_address']} activate\r")
                if differences[router]['EBGP_Neighbor'][0]!=None:
                    config_string+=(f"neighbor {differences[router]['EBGP_Neighbor'][0]['ipv6_address']} activate\r")
            if 'advertised_networks' in differences[router]:
                for network in differences[router]['advertised_networks'][1]:
                    config_string+=(f"no network {network}\r")
                for network in differences[router]['advertised_networks'][0]:
                    config_string+=(f"network {network}\r")
            config_string+="exit\rexit\r"

        print(config_string)

        telnet_to_node(config_string.encode(), nodes_info[router])


shutil.copyfile('intent_file.json', 'old_intent_file.json')
print("Le nouvel intent_file a été créé.")

## Virer l'ancien intent_file,
## Créer le nouveau