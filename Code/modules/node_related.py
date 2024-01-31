import telnetlib
import time
from gns3fy import Gns3Connector, Project
import sys


def telnet_to_node(config, port):
    """
    Uses telnet to send the configuration to the routers.
    Args:
        config (string) : the configuration to be sent to the router.
        port (int) : the port of the router.
    Returns:
        0 if everything went right
        -1 if an exception was raised
    """
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
    """
    Retrieves all of the nodes informations from GNS3 through the 
    gns3fy library.
    Args:
        project_name (str) : the name of the gns3 project
    Returns:
        None
    """
    try:
        nodes_dict={}
        server = Gns3Connector("http://localhost:3080")

        lab = Project(name=project_name, connector=server)
        
        lab.get()
        lab.open()

        for node in lab.nodes:
            node.get()
            nodes_dict[node.name] = node.console
        return(nodes_dict)
    except Exception as e:
        print("Error retrieving project nodes ports", e)
        sys.exit()