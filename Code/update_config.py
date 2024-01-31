from modules.comparer import compare_dicts, compareLoopbacks
from modules.node_related import *
from modules.conf_commands import *
import json
import shutil

GNS3_Project_Name = "Conf_Finale"

intent_file_path = "intent_files/intent_file.json"
old_intent_file_path = "intent_files/old_intent_file.json"


if __name__ == "__main__":


    nodes_info = retrieve_nodes(GNS3_Project_Name)

    def load_json(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)


    #Comparison of the old and new intent_file, storing the differences in a dictionary called differences.
    #This dictionary has the same structure as the original JSON, except that when a modification occurs,
    #it stores the new and old values in the form of a tuple (new, old).
    intent_file = load_json(intent_file_path)
    old_intent_file = load_json(old_intent_file_path)
    differences = compare_dicts(intent_file, old_intent_file)


    #Comparison of removed/new loopback addresses in an AS.
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

    print(differences)
    print(differences_loopbacks)


    #Note: logs currently do not account for new or removed routers or interfaces
    for router, router_content in intent_file.items():
        #If modifications have occurred in a router's settings or in the loopback addresses of its AS
        if (router in differences) or (router_content['as_number'] in differences_loopbacks):
            
            config_string = "enable\rend\rconf t\r"

            if 'IGP' in differences[router]:
                nouveau_igp=differences[router]['IGP'][0]
                ancien_igp=differences[router]['IGP'][1]

                if ancien_igp=='RIP':
                    config_string+="no ipv6 router rip 0\r"
                    config_string+=setup_ospf(router_content['Router_ID'])
                else:
                    config_string+="no ipv6 router ospf 1\r"
                    config_string+=setup_rip()
            
            elif ('Router_ID' in differences[router]) and (router_content['IGP']=='OSPF'):
                ancien_routerID=differences[router]['Router_ID'][1]
                nouveau_routerID=differences[router]['Router_ID'][0]

                config_string+="ipv6 router ospf 1\r"
                config_string+="no router-id "+ancien_routerID+"\r"
                config_string+="router-id "+nouveau_routerID+"\r"


            if 'interfaces' in differences[router]:

                for interface, interface_content in router_content['interfaces'].items():

                    #If modifications have occurred on a specific interface
                    if interface in differences[router]['interfaces']:
                        config_string += "interface " + interface + "\r"

                        if 'ipv6_address' in differences[router]['interfaces'][interface]:
                            nouvelle_ipv6 = differences[router]['interfaces'][interface]['ipv6_address'][0]
                            ancienne_ipv6 = differences[router]['interfaces'][interface]['ipv6_address'][1]

                            config_string += "no ipv6 address "+ancienne_ipv6+"\r"
                            config_string += ipv6(nouvelle_ipv6)
                        
                        if 'ospf_cost' in differences[router]['interfaces'][interface]:
                            ancien_cout=differences[router]['interfaces'][interface]['ospf_cost'][1]
                            nouveau_cout=differences[router]['interfaces'][interface]['ospf_cost'][0]

                            config_string+= (f"no ipv6 ospf cost {ancien_cout}\r")
                            config_string+= (f"ipv6 ospf cost {nouveau_cout}\r")

                        if 'ospf_area' in differences[router]['interfaces'][interface]:
                            ancien_area= differences[router]['interfaces'][interface]['ospf_area'][1]
                            nouveau_area= differences[router]['interfaces'][interface]['ospf_area'][0]

                            config_string+= (f"no ipv6 ospf area {ancien_area}\r")
                            config_string+= (f"ipv6 ospf cost {nouveau_area}\r")

                        if 'IGP' in differences[router]:
                            if ancien_igp=='RIP':
                                config_string += "no ipv6 rip 0 enable\r"
                                config_string += ospfconf_area(interface_content['ospf_area'])
                                if (interface != "Loopback0") and ('ospf_cost' in interface_content):
                                    config_string+= ospfconf_cost(interface_content['ospf_cost'])
                            else:
                                config_string+="no ipv6 ospf 1\r"
                                config_string+="no ipv6 ospf cost\r"
                                config_string+=ripconf()

                        config_string+="exit\r"


            #Note: logs currently do not account for changes in bgp communities or local preference.

            #If the AS number has changed, the entire BGP configuration must be redone.
            if 'as_number' in differences[router]:
                ancien_as=differences[router]['as_number'][1]
                nouveau_as=differences[router]['as_number'][0]

                config_string+="no router bgp " + differences[router]['as_number'][1] + "\r"

                ebgp = None

                if router_content['EBGP_Neighbor'] != None:
                    ebgp = (router_content['EBGP_Neighbor']['as_number'], router_content['EBGP_Neighbor']['ipv6_address'])

                #Type is set to None because currently logs don't support communities
                config_string+=bgpconf(nouveau_as,router_content['Router_ID'],loopback_dict[nouveau_as],ebgp, router_content['advertised_networks'],None)
            


            #If a parameter in the BGP configuration has been modified.
            elif (('Router_ID' in differences[router]) or ('EBGP_Neighbor' in differences[router]) or (router_content['as_number'] in differences_loopbacks) or ('EBGP_Neighbor' in differences[router]) or ('advertised_networks' in differences[router])):
                
                config_string+="router bgp " + router_content['as_number'] + "\r"

                #Changing BGP router ID
                if 'Router_ID' in differences[router]:
                    config_string+="no bgp router-id " + ancien_routerID+"\r"
                    config_string+="bgp router-id " +nouveau_routerID+"\r"

                #Changing in iBGP loopback addresses ( remote as / update-source )
                if router_content['as_number'] in differences_loopbacks:
                    for address in differences_loopbacks[router_content['as_number']]['disparues']:
                        config_string+=(f"no neighbor {address}\r")
                    for address in differences_loopbacks[router_content['as_number']]['nouvelles']:
                        config_string+= "neighbor " + address + " remote-as " + router_content['as_number'] + "\r" + "neighbor " + address+ " update-source Loopback0\r"
                
                #Changing eBGP Neighbor ( remote as / update-source )
                if 'EBGP_Neighbor' in differences[router]:
                    ancien_ipvoisin=differences[router]['EBGP_Neighbor']['ipv6_address'][1]
                    nouveau_ipvoisin=differences[router]['EBGP_Neighbor']['ipv6_address'][0]

                    config_string+=(f"no neighbor {ancien_ipvoisin}\r")
                    config_string+=(f"neighbor {nouveau_ipvoisin} remote-as {router_content['EBGP_Neighbor']['as_number']}\r")


                config_string += "address-family ipv6 unicast\r"
                
                #Changing iBGP lookpack addresses ( activate )
                if router_content['as_number'] in differences_loopbacks:
                    for address in differences_loopbacks[router_content['as_number']]['disparues']:
                        config_string+=(f"no neighbor {address} activate\r")
                    for address in differences_loopbacks[router_content['as_number']]['nouvelles']:
                        config_string+=(f"neighbor {address} activate\r")

                #Changing eBGP Neighbor ( activate )
                if 'EBGP_Neighbor' in differences[router]:
                    config_string+=(f"no neighbor {ancien_ipvoisin} activate\r")
                    config_string+=(f"neighbor {nouveau_ipvoisin} activate\r")

                #Changing in advertised networks
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
