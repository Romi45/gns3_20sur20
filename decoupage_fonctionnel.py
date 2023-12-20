

def telnet_to_node(config, node):
    """
    params: node object, config ==> list of commands for the config, result of generate_config 

    sends commands to node with \r btwn lines

    returns: 0 if everything okay, -1 and error otherwise
    """

def generate_config(node):
    """
    params: node object

    uses node attributes to generate commands for the config 

    returns: list of all str commands necessary for the config
    """

def retrieve_nodes(project_name):
    """
    params: gns3 project name

    retrieve information about the project using gns3fy

    returns: dictionnary of node numbers as keys and node objects as values
    """
