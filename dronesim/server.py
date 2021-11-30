#!/usr/bin/python3
import socket
import threading

# |y (up)
# |   
# |    / z (forwards)
# |  /
# |/
#  \
#    \
#      \ x (right)

class Drone:
    def __init__(self, addr):
        self.addr = addr
        self.following_target = False
        self.target_pos = [0,0,0]
        self.target_heading = 0
        
        self.accelerometer = [0,0,0]
        self.gyroscope = [0,0,0]
        self.barometer = 0
        self.gps = [0,0]

    def __str__(self):
        return "===\naddr: {}\naccl: {}\ngyro: {}\nbaro: {}\ngps: {}".format(
                str(self.addr),
                str(self.accelerometer),
                str(self.gyroscope),
                str(self.barometer),
                str(self.gps))

class DroneServer:
    def __init__(self, port, max_drones=32):
        self.drones = []
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", port))
        print("Server listening.")
        
        self.thr = threading.Thread(target=self.run, args=())
        self.thr.start()

        while True:
            for dr in self.drones:
                s = input()
                vals = s.split(" ")
                self.sock.sendto(bytes("M"+"/".join(vals), "ascii"), dr.addr)

    def run(self):
        while (True):
            recv = self.sock.recvfrom(1024)
            msg = bytes.decode(recv[0])
            addr = recv[1]

            print(msg)

            # New drone message
            if msg[0] == "N":
                create = True
                for d in self.drones:
                    if d.addr == addr:
                        create = False
                if create:
                    self.drones.append(Drone(addr))
                    self.sock.sendto(b"OK", addr)
                    print("New drone added (total: {})".format(len(self.drones)))
            # Sensors
            # e.g. SGX/X/X:AX/X/X:BX:PX/X
            if msg[0] == "S":
                sender = None
                for d in self.drones:
                    if d.addr == addr:
                        sender = d
                        break
                if sender == None:
                    self.sock.sendto(b"BAD", addr)
                else:
                    try:
                        spl = msg[1:].split(":")
                        for sens in spl:
                            if sens[0] == "G": # Gyroscope
                                sender.gyroscope = [float(n) for n in sens[1:].split("/")]
                            if sens[0] == "A": # Accelerometer
                                sender.accelerometer = [float(n) for n in sens[1:].split("/")]
                            if sens[0] == "B": # Barometer
                                sender.barometer = float(sens[1:])
                            if sens[0] == "P": # GPS
                                sender.gps = [float(n) for n in sens[1:].split("/")]
                    except Exception:
                        print("Invalid data from {}".format(str(addr)))
                    print(str(sender))

            #self.sock.sendto(b"M70/70/70/70", addr)

if __name__ == "__main__":
    srv = DroneServer(14444)