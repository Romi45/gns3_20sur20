import os
import telnetlib
from gns3fy import Gns3Connector, Project
import time

def telnet_to_node(config, port):
    try:
        tn = telnetlib.Telnet('localhost',port)
        tn.write(config)
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


def delete_startup_config(directory):
    for subdir in os.listdir(directory + "project-files/dynamips"):
        subdir_path = os.path.join(directory, subdir)
        if os.path.isdir(subdir_path):
            configs_path = os.path.join(subdir_path, "configs")
            if os.path.isdir(configs_path):
                for file in os.listdir(configs_path):
                    if file.endswith("startup-config.cfg"):
                        file_path = os.path.join(configs_path, file)
                        os.remove(file_path)
                        print(f"Supprimé : {file}")
    
    input("Maintenant, redémarrez tous les routeurs, attendez qu'ils démarrent puis faites entrée.")
    for router in nodes_info:
        telnet_to_node(('no\r').encode(), nodes_info[router])
    input("Tous les routeurs ont bien été reset")




# Utiliser la fonction
main_directory = "gns3_files/communities_proj/"
nodes_info = {}
retrieve_nodes("communities_proj-1")
delete_startup_config(main_directory)