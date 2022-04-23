#!/usr/bin/python3
import socket
import threading
import time
from websocket_server import WebsocketServer

from drone import *

def ws_callback_new_client(client, server):
    print(f"WS: New client.")
    server.send_message(client, "Welcome!")

def ws_callback_client_left(client, server):
    print(f"WS: Client has left.")

class DroneServer:
    def __init__(self, port, max_drones=32):
        self.drones = []
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

        self.ws_server = WebsocketServer(host="127.0.0.1", port=13254)
        self.ws_server.set_fn_new_client(ws_callback_new_client)
        self.ws_server.set_fn_client_left(ws_callback_client_left)
        self.ws_server.run_forever(threaded=True)
        print("Control panel server listening.")

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
                if inps[0] == "a":
                    for drone in self.drones:
                        drone.pid_alt.setpoint = inps[1]

        self.log_file.close()

    def get_unique_id(self):
        self.d_id += 1
        return self.d_id

    def compute_drones(self):
        while True:
            time.sleep(1/50)
            for drone in self.drones:
                drone.compute(self.sock)
            json_msg = {
                "drones_count": len(self.drones),
                "drones": [
                    d.get_json() for d in self.drones
                ]
            }
            print(json_msg)

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
                                #self.log_file.write("(" + str(round(time.time() - self.plot_t0, 3)) + "," + str(round(sender.ypr[0], 3)) + "), ")
                            if sens[0] == "T": # Translation
                                sender.translation = [float(n) for n in sens[1:].split("/")]
                    except Exception:
                        print("Invalid data from {}: {}".format(str(addr), msg))

if __name__ == "__main__":
    print("Drone Fleet Controller v1, https://github.com/j4cobgarby/dronefleet")
    srv = DroneServer(14444)
