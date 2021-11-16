#!/usr/bin/python3
import socket

port = 14444
drones = []

sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

sock.bind(("127.0.0.1",port))
print("Server ready")

# |y (up)
# |   
# |    / z (forwards)
# |  /
# |/
#  \
#    \
#      \ x (right)

class Drone:
    following_target = False

    target_pos = (0,0,0)
    target_yaw = 0

    addr = None # Tuple (ip, port)

    def __init__(self, addr):
        self.addr = addr

while (True):
    recv = sock.recvfrom(1024)
    msg = bytes.decode(recv[0])
    addr = recv[1]

    # New drone message
    if msg[0] == "N":
        create = True
        for d in drones:
            if d.addr == addr:
                create = False
        if create:
            drones.append(Drone(addr))
            print("New drone added (total: {})".format(len(drones)))
    # Sensors
    # e.g. SGX/X/X:AX/X/X:BX:GPSX/X
    if msg[0] == "S":
        spl = msg[1:].split(":")
        for sens in spl:
            if sens[0] == "G": # Gyroscope
                gxyz = sens[1:].split("/")
