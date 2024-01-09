def ripconf(interface, adresseip):
    ripstring = b"enable\rconf t\ripv6 unicast-routing\ripv6 router rip 0\rredistribute connected\rexit\rinterface "
    ripstring = ripstring + interface + b"\r"
    ripstring += b"ipv6 enable\ripv6 address "
    ripstring = ripstring + adresseip + b"\r"
    ripstring += b"no shutdown\ripv6 rip 0 enable"
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
