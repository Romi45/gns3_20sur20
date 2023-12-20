from gns3fy import Gns3Connector, Project
from tabulate import tabulate
server = Gns3Connector("http://localhost:3080")

# To show the available projects on the server
#print(server.projects_summary())
print(
        tabulate(
            server.projects_summary(is_print=False),
            headers=["Project Name", "Project ID", "Total Nodes", "Total Links", "Status"],
        )
    )
"""
Project Name    Project ID                              Total Nodes    Total Links  Status
--------------  ------------------------------------  -------------  -------------  --------
test2           c9dc56bf-37b9-453b-8f95-2845ce8908e3             10              9  opened
API_TEST        4b21dfb3-675a-4efa-8613-2f7fb32e76fe              6              4  opened
mpls-bgpv2      f5de5917-0ac5-4850-82b1-1d7e3c777fa1             30             40  closed
"""

lab = Project(name="bgp_tp", connector=server)

# Retrieve its information and display
lab.get()

#print(lab)

# Open the project
lab.open()
lab.status
#opened

# Verify the stats
lab.stats

for node in lab.nodes:
    print(f"Node: {node.name} -- Node Type: {node.node_type} -- Status: {node.status}")
    if node.name == 'R1':
        print(node.get())
        print(node.console, node.console_host)
