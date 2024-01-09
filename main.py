import telnetlib
import time
from gns3fy import Gns3Connector, Project


nodes_info = {}
config_rip = b"enable\rconf t\ripv6 unicast-routing\ripv6 router rip 0\rredistribute connected\rexit\r"
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
    

def generate_config(node):
    """
    params: node object

    uses node attributes to generate commands for the config 

    returns: list of all str commands necessary for the config
    """

def retrieve_nodes(project_name):
    server = Gns3Connector("http://localhost:3080")
    lab = Project(name=project_name, connector=server)
    lab.get()
    lab.open()
    for node in lab.nodes:
        node.get()
        nodes_info[node.name] = node.console
    


def ripconf(interface,adresse_ip):
    #tested, works as expected
    rip_string = b"interface " + interface + b"\ripv6 enable\ripv6 address " + rip_string + adresse_ip + b"\rno shutdown\ripv6 rip 0 enable\r"
    return rip_string

def setup_ospf(router_id):
    setup_ospf_string = b"enable\rconf t\ripv6 unicast-routing\ripv6 router ospf 1\rrouter-id " + router_id + b"\r" + "exit\r"
    return setup_ospf_string

def ospfconf(interface, adresseip, ospfarea):
    #tested, works as expected
    ospfstring = b"interface " + interface + b"\ripv6 enable\ripv6 address " + adresseip + b"\rno shutdown\ripv6 ospf 1 area "+ ospfarea + b"\r"
    return ospfstring

retrieve_nodes("test_proj")
print(nodes_info)


text_rip_r1 = ripconf(b"GigabitEthernet 1/0", b"2001::1")


text_r1 = ospfconf(b"1.1.1.1", b"GigabitEthernet 1/0", b"2001::0/64", b"1")
text_r2 = ospfconf(b"2.2.2.2", b"GigabitEthernet 1/0", b"2001::1/64", b"1")
text_r3 = ospfconf(b"2.2.2.2", b"GigabitEthernet 2/0", b"2002::2/64", b"1")
text_r4 = ospfconf(b"4.4.4.4", b"GigabitEthernet 2/0", b"2002::4/64", b"1")
telnet_to_node(text_r1, nodes_info["R1"])
telnet_to_node(text_r2, nodes_info["R2"])
telnet_to_node(text_r3, nodes_info["R2"])
telnet_to_node(text_r4, nodes_info["R3"])
