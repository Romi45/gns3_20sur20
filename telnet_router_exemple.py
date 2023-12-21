import telnetlib
import time

port = 5015

try:
    tn = telnetlib.Telnet('localhost',port)
    time.sleep(1)
    tn.write(b"conf t\rinterface GigabitEthernet 1/0\r end\r")
    time.sleep(1)

    
except Exception as e:
    print("Could not open telnet session and/or send commands", e)
