import os
import telnetlib
from gns3fy import Gns3Connector, Project
from modules.node_related import retrieve_nodes
import time

GNS3_Project_Name = "Conf_Finale"
dynamips_directory = "../../../../GNS3/projects/Conf_Finale/project-files/dynamips"

def telnet_no_to_node(port):
    try:
        tn = telnetlib.Telnet('localhost',port)
        tn.write(("no").encode())
        return 0
    except Exception as e:
        print("Could not open telnet session and/or send commands", e)
        return -1

if __name__ == "__main__":
    print("Suppression de tous les fichiers config des routers\n Assurez-vous que le projet GNS3 est bien fermé")

    for subdir in os.listdir(dynamips_directory):
        subdir_path = os.path.join(dynamips_directory, subdir)
        if os.path.isdir(subdir_path):
            configs_path = os.path.join(subdir_path, "configs")
            if os.path.isdir(configs_path):
                for file in os.listdir(configs_path):
                    if file.endswith("startup-config.cfg"):
                        file_path = os.path.join(configs_path, file)
                        os.remove(file_path)
                        print(f"Supprimé : {file}")
    
    input("Maintenant, ouvrez le projet GNS3\rRedémarrez tous les routeurs, attendez qu'ils démarrent puis faites entrée.")
    nodes_info = retrieve_nodes(GNS3_Project_Name)
    for router in nodes_info:
        telnet_no_to_node(nodes_info[router])

    input("Tous les routeurs ont bien été reset")

