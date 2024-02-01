def setup_rip():
    """
    Builds the RIP setup string
    Args:
        None
    Returns:
        (string) the configuration string.
    """

    return("ipv6 router rip 0\rredistribute connected\rexit\r")

def setup_ospf(router_id):
    """
    Builds the OSPF setup string with the router ID.
    Args:
        router_id (str) : the OSPF router ID to be assigned.
    Returns:
        (string) the configuration string.
    """

    return ("ipv6 router ospf 1\r" + "router-id " + router_id + "\r" + "exit\r")

def ipv6(adresse_ip):
    """
    Builds the ipv6 addressing string.
    Args:
        adresse_ip (string) : the ipv6 address to be assigned.
    Returns:
        (string) : the configuration string.
    """
    return("ipv6 address " + adresse_ip + "\r")

def ripconf():
    """
    Builds the RIP setup string.
    Args:
        None
    Returns:
        (string) the configuration string.
    """

    return ("ipv6 rip 0 enable\r")

def ospfconf_area(ospf_area):
    """
    Builds the OSPF area setup string.
    Args:
        ospf_area (str) : the OSPF area number to be assigned.
    Returns:
        (string) the configuration string.
    """

    return ("ipv6 ospf 1 area " + ospf_area + "\r")

def ospfconf_cost(ospf_cost):
    """
    Builds the OSPF link cost string.
    Args:
        ospf_cost (str) : the OSPF link cost.
    Returns:
        (string) the configuration string.
    """
    return("ipv6 ospf cost " + ospf_cost + "\r")


def bgpconf(id_AS,router_id,loopback_neighbors, ebgp, advertised_networks,type):
    """
    Builds the entire BGP configuration string.
    Args:
        id_AS (string) : the AS number.
        router_id (string) : the router ID number.
        loopback_neighbors (list) : a list of the loopback @ of the neighbors of the router.
        ebgp (tuple) : contains the AS number and the ipv6 @ of the EBGP neighbor
        advertised_networks (list) : the networks to advertise through BGP
        type (string) : the type of BGP neighbor (customer, peer, provider)
    Returns:
        bgp_string (string) : the bgp configuration string.
    """

    route_map = ""
    local_pref=""
    bgp_string=""

    if type == "client":
        bgp_string = "route-map CUSTOMER_RM_PERMIT permit 10\rset local-preference 400\rset community 100:1789\rexit\r"
        route_map = "neighbor "+ ebgp[1] +" route-map CUSTOMER_RM_PERMIT in\r"

    elif type == "provider" or type == "peer":
        bgp_string = "route-map CUSTOMER_RM_DENY permit 10\rmatch community CUSTOMER_CL\rexit\rroute-map CUSTOMER_RM_DENY deny 20\rexit\rip community-list standard CUSTOMER_CL permit 100:1789\r"
        route_map = "neighbor "+ ebgp[1] +" route-map CUSTOMER_RM_DENY out\r"

        if type=="peer":
            bgp_string += "route-map PEER_LOCAL_PREF \rset local-preference 300\rexit\r"
            local_pref = "neighbor "+ebgp[1]+" route-map PEER_LOCAL_PREF in\r"

        else:
            bgp_string += "route-map PROVIDER_LOCAL_PREF \rset local-preference 200\rexit\r"
            local_pref = "neighbor "+ebgp[1]+" route-map PROVIDER_LOCAL_PREF in\r"
        

    bgp_string += "router bgp " + id_AS + "\rno bgp default ipv4-unicast\rbgp router-id " + router_id + "\r"
    
    for i in range (0,len(loopback_neighbors)):
        bgp_string += "neighbor " + loopback_neighbors[i] + " remote-as " + id_AS + "\r" + "neighbor " + loopback_neighbors[i] + " update-source Loopback0\r"
    
    if ebgp:
        bgp_string += "neighbor " + ebgp[1] + " remote-as " + ebgp[0] + "\r"

    bgp_string += "address-family ipv6 unicast\r"

    for i in range (0,len(loopback_neighbors)):
        bgp_string += "neighbor " + loopback_neighbors[i] + " activate\r"
        bgp_string += "neighbor " + loopback_neighbors[i] + " send-community both\r"

    if ebgp:
        bgp_string += "neighbor " + ebgp[1] + " activate\r"
        bgp_string += "neighbor " + ebgp[1] + " send-community both\r"

    bgp_string +=  route_map
    bgp_string +=  local_pref



    for network_addrs in advertised_networks:
        bgp_string += f"network {network_addrs}\r"

    bgp_string += "exit\rexit\r"   

    return bgp_string
