def ripconf(interface, adresse_ip):
    ripstring = b"enable\rconf t\ripv6 unicast-routing\ripv6 router rip 0\rredistribute connected\rexit\rinterface "
    ripstring = ripstring + interface + b"\r"
    ripstring += b"ipv6 enable\ripv6 address "
    ripstring = ripstring + adresse_ip + b"\r"
    ripstring += b"no shutdown\ripv6 rip 0 enable\r"
    return ripstring

print(ripconf(b"GigabitEthernet 1/0", b"2001::0"))


def ospfconf(router_id, interface, adresse_ip, ospf_area):
    ospfstring = b"enable\rconf t\ripv6 unicast-routing\ripv6 router ospf 0\rrouter-id "
    ospfstring = ospfstring + router_id + b"\r"
    ospfstring += b"exit\rinterface "
    ospfstring = ospfstring + interface + b"\r"
    ospfstring += b"ipv6 enable\ripv6 address "
    ospfstring = ospfstring + adresse_ip + b"\r"
    ospfstring += b"no shutdown\ripv6 ospf "
    ospfstring = ospfstring + ospf_area + b"\r"
    return ospfstring

print(ospfconf(b"0.0.0.0", b"GigabitEthernet 1/0", b"2001::0", b"0"))


def ibgpripconf(interface,adresse_ip,id_AS,router_id,loopback_neighbors):
    ibgpripstring = b"enable\rconf t\r" + interface + b"\ripv6 enable\ripv6 address " + adresse_ip + b"\ripv6 rip 0 enable\rexit\rrouter bgp " + id_AS + b"\rbgp router-id " + router_id + b"\r"
    for i in range (0,len(loopback_neighbors)):
          ibgpripstring += b"neighbor " + loopback_neighbors[i] + b" remote-as " + id_AS + b"\r"
    for i in range (0,len(loopback_neighbors)):
          ibgpripstring += b"neighbor " + loopback_neighbors[i] + b" update-source " + interface + b"\r"
    ibgpripstring = ibgpripstring + b"address-family ipv6 unicast\r"
    for i in range (0,len(loopback_neighbors)):
          ibgpripstring += b"neighbor " + loopback_neighbors[i] + b" activate\r"
    return ibgpripstring

print(ibgpripconf(b"Loopback0",b"2001::0",b"112",b"1.1.1.1",[b"2001::2",b"2001:3",b"2001:4"]))


def ibgpospf(interface,adresse_ip,id_AS,router_id,loopback_neighbors):
    ibgpospfstring = b"enable\rconf t\rinterface " + interface + b"\ripv6 enable\ripv6 address " + adresse_ip + b"\ripv6 ospf 1 area 0\rexit\rrouter bgp " + id_AS + b"\rbgp router-id " + router_id + b"\r"
    for i in range (0,len(loopback_neighbors)):
          ibgpospfstring += b"neighbor " + loopback_neighbors[i] + b" remote-as " + id_AS + b"\r"
    for i in range (0,len(loopback_neighbors)):
          ibgpospfstring += b"neighbor " + loopback_neighbors[i] + b" update-source " + interface + b"\r"
    ibgpospfstring = ibgpospfstring + b"address-family ipv6 unicast\r"
    for i in range (0,len(loopback_neighbors)):
          ibgpospfstring += b"neighbor " + loopback_neighbors[i] + b"activate\r" 
    return ibgpospfstring

print(ibgpripconf(b"Loopback0",b"2001::0",b"112",b"1.1.1.1",[b"2001::2",b"2001:3",b"2001:4"]))


def ebgpconf(id_AS,router_id,neighbor_ip,AS_voisin):
    ebgpstring = b"enable\rconf t\rrouter bgp " + id_AS + b"\rno bgp default ipv4-unicast\rbgp router-id " + router_id + b"\rneighbor " + neighbor_ip + b" remote-as\r" + AS_voisin + b"\raddress-family ipv6 unicast\rneighbor " + neighbor_ip + b" activate\r"
    return ebgpstring

print(ebgpconf(b"112",b"1.1.1.1",b"2001::5",b"113"))
