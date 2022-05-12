#!/usr/bin/python3
import socket
import threading
import time

from drone import *

class DroneServer:
    def __init__(self, port, max_drones=32):
        self.drones = []
        self.max_drones = max_drones
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", port))
        print("Drone control server listening.")
        self.plot_t0 = time.time()

        self.d_id = 0

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
                # <drone id> <value to set> <value>
                # e.g. 0 a 20 sets altitude of drone 0 to 20
                inps = inp.split(" ")
                value = float(inps[2])
                drone = None
                for d in self.drones:
                    if d.id == int(inps[0]):
                        drone = d
                if drone != None:
                    print(f"Time is {time.time()-self.plot_t0}")
                    if inps[1] == "y":
                        drone.pid_yaw.setpoint = value
                    if inps[1] == "p":
                        drone.pid_pitch.setpoint = value
                    if inps[1] == "r":
                        drone.pid_roll.setpoint = value
                    if inps[1] == "a":
                        drone.pid_alt.setpoint = value

        self.log_file.close()
        self.thr.join()
        self.thr2.join()

    def get_unique_id(self):
        self.d_id += 1
        return self.d_id

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
                create = len(self.drones) < self.max_drones
                for d in self.drones:
                    if d.addr == addr:
                        create = False
                if create:
                    self.drones.append(Drone(addr, self.get_unique_id()))
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
                            if sens[0] == "T": # Translation
                                sender.translation = [float(n) for n in sens[1:].split("/")]
                    except Exception:
                        print("Invalid data from {}: {}".format(str(addr), msg))

if __name__ == "__main__":
    print("Drone Fleet Controller v1, https://github.com/j4cobgarby/dronefleet")
    srv = DroneServer(14444)
