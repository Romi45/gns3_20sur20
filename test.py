# Python program to demonstrate
# Conversion of JSON data to
# dictionary
 
# importing the module
import json
 
# Opening JSON file
with open('intent_file.json') as json_file:
    data = json.load(json_file)
 
    # Print the type of data variable
    print("Type:", type(data))
    
    for as_number, as_content in data.items():

        if as_content['IGP']=='RIP':

            print(as_number + " RIP")
            for router, router_content in as_content['routers'].items():
                #setup_rip_router(router)
                print(router)
                for interface, interface_content in router_content['interfaces'].items():
                    #setup_rip_interface(interface, interface_content['ipv6_address])
                    print(interface)
                    print(interface_content['ipv6_address'])

        elif as_content['IGP']=='OSPF':
            print(as_number + " OSPF")
            for router, router_content in as_content['routers'].items():
                #setup_ospf_router(router_content['Router_ID'])
                print(router)
                for interface, interface_content in router_content['interfaces'].items():
                    #setup_ospf_interface(interface, interface_content['ipv6_address], interface_content['ospf_area])
                    print(interface)
                    print(interface_content['ipv6_address'])
                    print(interface_content['ospf_area'])