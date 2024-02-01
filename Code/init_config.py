from modules.node_related import *
from modules.conf_commands import *
import json

GNS3_Project_Name = "Conf_Finale"
intent_file_path = "intent_files/intent_file.json"

if __name__ == "__main__":

    nodes_info = retrieve_nodes(GNS3_Project_Name)

    with open(intent_file_path) as json_file:
        data = json.load(json_file)
        config_string = ""

        #Retrieving all the loopback addresses in a dictionary, stored by AS, to configure iBGP on all routers
        loopback_dict = {}
        for router, router_content in data.items():

            if router_content['as_number'] in loopback_dict:
                loopback_dict[router_content['as_number']].append((router_content['interfaces']['Loopback0']['ipv6_address']).replace('/128',''))
                
            else:
                loopback_dict[router_content['as_number']]=[(router_content['interfaces']['Loopback0']['ipv6_address']).replace('/128','')]
        


        #Each router is configured based on the parameters entered in the intent_file.
        for router, router_content in data.items():

            print(f"Configuration de {router}")

            config_string = "end\renable\rconf t\rip bgp-community new-format\ripv6 unicast-routing\r"

            if router_content["IGP"]=="RIP":
                igp=0
                config_string += setup_rip()
            else:
                igp=1
                config_string += setup_ospf(router_content['Router_ID'])


            for interface, interface_content in router_content['interfaces'].items():
                config_string += "interface " + interface + "\ripv6 enable\rno shutdown\r"

                config_string += ipv6(interface_content['ipv6_address'])
                    
                if igp == 0:
                    config_string += ripconf()

                elif igp == 1:
                    config_string += ospfconf_area(interface_content['ospf_area'])
                    if (interface != "Loopback0") and ('ospf_cost' in interface_content):
                        config_string+= ospfconf_cost(interface_content['ospf_cost'])

                config_string+="exit\r"
                
            #If the router is an edge router, ebgp var will become a tuple (neighbor_as, neighbor_ip)
            ebgp = None
            #If the ebgp neighbor has a type ( client, peer or provider ), type will become a string
            type=None

            if router_content['EBGP_Neighbor'] != None:

                ebgp = (router_content['EBGP_Neighbor']['as_number'], router_content['EBGP_Neighbor']['ipv6_address'])

                if 'type' in router_content['EBGP_Neighbor']:    
                    type = router_content['EBGP_Neighbor']['type']

            config_string += bgpconf(router_content['as_number'],router_content['Router_ID'],loopback_dict[router_content['as_number']],ebgp, router_content['advertised_networks'],type)

            print(config_string)

            telnet_to_node(config_string.encode(), nodes_info[router])
            

