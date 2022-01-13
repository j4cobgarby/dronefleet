#!/usr/bin/python3
import socket
import threading
import time

from drone import *

class DroneServer:
    def __init__(self, port, max_drones=32):
        self.drones = []
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", port))
        print("Server listening.")
        self.plot_t0 = time.time()

        self.log_file = open("pid_log.txt", "w+")
        
        self.thr = threading.Thread(target=self.run, args=())
        self.thr.start()

        self.thr2 = threading.Thread(target=self.compute_drones, args=())
        self.thr2.start()

        while True:
            inp = input()
            if inp == "q":
                break
            else:
                inps = inp.split(" ")
                inps[1] = float(inps[1])
                if inps[0] == "y":
                    for drone in self.drones:
                        drone.pid_yaw.setpoint = inps[1]
                if inps[0] == "p":
                    for drone in self.drones:
                        drone.pid_pitch.setpoint = inps[1]
                if inps[0] == "r":
                    for drone in self.drones:
                        drone.pid_roll.setpoint = inps[1]
                #set_alt = float(inp)
                #for drone in self.drones:
                #    drone.pid_alt.setpoint = set_alt

        self.log_file.close()

            # for drone in self.drones:
            #     drone.compute(self.sock)
            #time.sleep(0.1)
            # for dr in self.drones:
            #     s = input()
            #     vals = s.split(" ")
            #     self.sock.sendto(bytes("M"+"/".join(vals), "ascii"), dr.addr)

    def compute_drones(self):
        while True:
            time.sleep(1/50)
            for drone in self.drones:
                drone.compute(self.sock)

    def run(self):
        while (True):
            recv = self.sock.recvfrom(1024)
            msg = bytes.decode(recv[0])
            addr = recv[1]

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
                            if sens[0] == "R": # Rotation (yaw/pitch/roll)
                                sender.ypr = [float(n) for n in sens[1:].split("/")]
                                self.log_file.write("(" + str(round(time.time() - self.plot_t0, 3)) + "," + str(round(sender.ypr[0], 3)) + "), ")
                                #print("(" + str(round(time.time() - self.plot_t0, 3)) + "," + str(round(sender.ypr[0], 3)), end="), ", flush=True)
                            if sens[0] == "T": # Translation
                                sender.translation = [float(n) for n in sens[1:].split("/")]
                                #self.log_file.write("(" + str(round(time.time() - self.plot_t0, 3)) + "," + str(round(sender.translation[1], 3)) + "), ")
                                #print("(" + str(round(time.time() - self.plot_t0, 3)) + "," + str(round(sender.translation[1], 3)), end="), ", flush=True)
                    except Exception:
                        print("Invalid data from {}: {}".format(str(addr), msg))
                    #print(str(sender))

            #self.sock.sendto(b"M70/70/70/70", addr)

if __name__ == "__main__":
    srv = DroneServer(14444)
