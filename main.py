import telnetlib
import time
from gns3fy import Gns3Connector, Project
import json

nodes_info = {}
config_rip = "enable\rconf t\ripv6 unicast-routing\ripv6 router rip 0\rredistribute connected\rexit\r"
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
    #tested, works as expected
    server = Gns3Connector("http://localhost:3080")
    lab = Project(name=project_name, connector=server)
    lab.get()
    lab.open()
    for node in lab.nodes:
        node.get()
        nodes_info[node.name] = node.console
    


def ripconf(interface,adresse_ip):
    #tested, works as expected
    rip_string = "interface " + interface + "\ripv6 enable\ripv6 address " + adresse_ip + "\rno shutdown\ripv6 rip 0 enable\rexit\r"
    return rip_string

def setup_ospf(router_id):
    #tested, works as expected
    setup_ospf_string = "enable\rconf t\ripv6 unicast-routing\ripv6 router ospf 1\rrouter-id " + router_id + "\r" + "exit\r"
    return setup_ospf_string

def ospfconf(interface, adresseip, ospfarea):
    #tested, works as expected
    ospfstring = "interface " + interface + "\ripv6 enable\ripv6 address " + adresseip + "\rno shutdown\ripv6 ospf 1 area "+ ospfarea + "\rexit\r"
    return ospfstring

def bgpconf(id_AS,router_id,loopback_neighbors, ebgp, advertised_networks):
    #ebgp est un tuple qui a comme element un as voisin + ip_voisin
    id_AS = str(id_AS)
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


retrieve_nodes("test_proj")
print(nodes_info)


config_string = ""
loopback_dict = {}
igp_type = ['RIP', 'OSPF']
igp = 0 #vaut 0 pour RIP, 1 pour OSPF

with open('/Users\jeand\OneDrive\Documentos\INSA_Cours\TC\GNS3\intent_file.json') as json_file:
    data = json.load(json_file)
    

    #IGP
    for as_name, as_content in data.items():
        loopback_dict[as_name] = []

        if as_content['IGP']=='OSPF':
            igp = 1
        print(as_name + igp_type[igp])
        for router, router_content in as_content['routers'].items():
            loopback_dict[as_name].append((router_content['interfaces']['Loopback0']['ipv6_address']).replace('/128',''))
        
        for router, router_content in as_content['routers'].items():

            if igp == 0:
                #setup_rip_router(router)
                config_string = ""
                config_string = config_rip


            elif igp == 1:
                #setup_ospf_router(router_content['Router_ID'])
                config_string = ""
                config_string = setup_ospf(router_content['Router_ID'])

            print(router)

            for interface, interface_content in router_content['interfaces'].items():

                if igp == 0:
                    #setup_rip_interface(interface, interface_content['ipv6_address'])
                    config_string += ripconf(interface, interface_content['ipv6_address'] )
                    
                elif igp == 1:
                    #setup_ospf_interface(interface, interface_content['ipv6_address], interface_content['ospf_area])
                    config_string += ospfconf(interface, interface_content['ipv6_address'], (str(interface_content['ospf_area'])))
                
                print(config_string.encode())

            ebgp = None

            #conf bgp
            if router_content['EBGP_Neighbor'] != None:
                ebgp = (str(router_content['EBGP_Neighbor']['AS_number']), router_content['EBGP_Neighbor']['ipv6_address'])
            
            config_string += bgpconf(as_content['as_number'],router_content['Router_ID'],loopback_dict[as_name],ebgp, router_content['advertised_networks'])

            telnet_to_node(config_string.encode(), nodes_info[router])

        """elif as_content['IGP']=='OSPF':
            print(as_number + " OSPF")
            for router, router_content in as_content['routers'].items():
                #setup_ospf_router(router_content['Router_ID'])
                config_string = b""
                config_string = setup_ospf(router_content['Router_ID'])
                loopback_dict[as_number].append(router_content['interfaces']['Loopback0']['ipv6_address'])
                print(router)

                for interface, interface_content in router_content['interfaces'].items():
                    #setup_ospf_interface(interface, interface_content['ipv6_address], interface_content['ospf_area])
                    config_string += ospfconf(interface, interface_content['ipv6_address'], (str(interface_content['ospf_area'])))
                    print(config_string)

                telnet_to_node(config_string, nodes_info[router])
"""
                
print(loopback_dict)
