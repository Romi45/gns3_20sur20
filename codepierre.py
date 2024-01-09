#le if pour savoir si mettre rip ou pas vient avant la fonction
#

port = 5015

def ripconf(interface,adresseip):
    ripstring = b"enable\rconf t\ripv6 unicast-routing\ripv6 router rip 0\rredistribute connected\rexit\rinterface "
    ripstring = ripstring + interface + b"\r"
    ripstring += b"ipv6 enable\ripv6 address "
    ripstring = ripstring + adresseip + b"\r"
    ripstring += b"no shutdown\ripv6 rip 0 enable"
    return ripstring

print(ripconf(b"GigabitEthernet 1/0", b"2001::0"))
