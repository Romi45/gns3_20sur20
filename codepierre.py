def ripconf(interface, adresseip):
    ripstring = b"enable\rconf t\ripv6 unicast-routing\ripv6 router rip 0\rredistribute connected\rexit\rinterface "
    ripstring = ripstring + interface + b"\r"
    ripstring += b"ipv6 enable\ripv6 address "
    ripstring = ripstring + adresseip + b"\r"
    ripstring += b"no shutdown\ripv6 rip 0 enable\r"
    return ripstring

print(ripconf(b"GigabitEthernet 1/0", b"2001::0"))


def ospfconf(routerid, interface, adresseip, ospfarea):
    ospfstring = b"enable\rconf t\ripv6 unicast-routing\ripv6 router ospf 0\rrouter-id "
    ospfstring = ospfstring + routerid + b"\r"
    ospfstring += b"exit\rinterface "
    ospfstring = ospfstring + interface + b"\r"
    ospfstring += b"ipv6 enable\ripv6 address "
    ospfstring = ospfstring + adresseip + b"\r"
    ospfstring += b"no shutdown\ripv6 ospf "
    ospfstring = ospfstring + ospfarea + b"\r"
    return ospfstring

print(ospfconf(b"0.0.0.0", b"GigabitEthernet 1/0", b"2001::0", b"0"))


def ibgpripconf(interface,adresseip,id_as,routerid,loopback_neighbours):
    ibgpripstring = b"enable\rconf t\r"
    ibgpripstring += interface + b"\r"
    ibgpripstring = ibgpripstring + b"ipv6 enable\ripv6 address "
    ibgpripstring += adresseip + b"\r"
    ibgpripstring = ibgpripstring + b"ipv6 rip 0 enable\rexit\rrouter bgp "
    ibgpripstring += id_as + b"\r"
    ibgpripstring = ibgpripstring + b"bgp router-id "
    ibgpripstring += routerid + b"\r"
    for i in range (0,len(loopback_neighbours)):
          ibgpripstring += b"neighbor " + loopback_neighbours[i] + b" remote-as " + id_as + b"\r"
    for i in range (0,len(loopback_neighbours)):
          ibgpripstring += b"neighbor " + loopback_neighbours[i] + b" update-source " + interface + b"\r"
    ibgpripstring = ibgpripstring + b"address-family ipv6 unicast\r"
    for i in range (0,len(loopback_neighbours)):
          ibgpripstring += b"neighbor " + loopback_neighbours[i] + b" activate\r"
    return ibgpripstring

print(ibgpripconf(b"Loopback0",b"2001::0",b"112",b"1.1.1.1",[b"2001::2",b"2001:3",b"2001:4"]))


def ibgpospf(interface,adresseip,id_AS,routerid,loopback_neighbours):
    ibgpospfstring = b"enable\rconf t\rinterface "
    ibgpospfstring += interface + b"\r"
    ibgpospfstring = ibgpospfstring + b"ipv6 enable\ripv6 address "
    ibgpospfstring += adresseip + b"\r"
    ibgpospfstring = ibgpospfstring + b"ipv6 ospf 1 area 0\rexit\rrouter bgp "
    ibgpospfstring += id_AS + b"\r"
    ibgpospfstring = ibgpospfstring + b"bgp router-id "
    ibgpospfstring += routerid + b"\r"
    for i in range (0,len(loopback_neighbours)):
          ibgpospfstring += b"neighbor " + loopback_neighbours[i] + b" remote-as " + id_AS + b"\r"
    for i in range (0,len(loopback_neighbours)):
          ibgpospfstring += b"neighbor " + loopback_neighbours[i] + b" update-source " + interface + b"\r"
    ibgpospfstring = ibgpospfstring + b"address-family ipv6 unicast\r"
    for i in range (0,len(loopback_neighbours)):
          ibgpospfstring += b"neighbor " + loopback_neighbours[i] + b"activate\r" 
    return ibgpospfstring

print(ibgpripconf(b"Loopback0",b"2001::0",b"112",b"1.1.1.1",[b"2001::2",b"2001:3",b"2001:4"]))

