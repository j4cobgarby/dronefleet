# |y (up)
# |   
# |    / z (forwards)
# |  /
# |/
#  \
#    \
#      \ x (right)

'''
  front
A       B
  \   /
    X
  /   \ 
C       D

'''

from pid import *

def typr_to_motors(thrust, yaw, pitch, roll):
    return [
          yaw - pitch + roll + thrust,
        - yaw - pitch - roll + thrust,
        - yaw + pitch + roll + thrust,
          yaw + pitch - roll + thrust
    ]

class Drone:
    def __init__(self, addr):
        self.addr = addr
        self.following_target = False
        self.target_pos = [0,0,0]
        self.target_heading = 0
        
        self.translation = [0,0,0]
        self.accelerometer = [0,0,0]
        self.gyroscope = [0,0,0]
        self.barometer = 0
        self.gps = [0,0]
        self.ypr = [0,0,0]
        
        self.pid_yaw   = PidController(1.5,0.2,80,   0,  50, -200,200)
        self.pid_pitch = PidController(9,5,8,     0,  20,  -200,200)
        self.pid_roll  = PidController(5,0,5,     0,  50,  -200,200)
        self.pid_alt   = PidController(8,3,200,  15, 50,   -200,200)

    def __str__(self):
        return "===\naddr: {}\naccl: {}\ngyro: {}\nbaro: {}\ngps: {}\nyaw/pitch/roll: {}".format(
                str(self.addr),
                str(self.accelerometer),
                str(self.gyroscope),
                str(self.barometer),
                str(self.gps),
                str(self.ypr))

    def set_motors(self, sock, mots):
        sock.sendto(bytes("M"+"/".join([str(x) for x in mots]), "ascii"), self.addr)

    def compute(self, sock):
        #print(self.ypr[0])
        #print("Alt: " + str(self.translation[1]))
        yaw = self.pid_yaw.compute(self.ypr[0])
        pitch = self.pid_pitch.compute(self.ypr[1])
        roll = self.pid_roll.compute(self.ypr[2])
        thrust = self.pid_alt.compute(self.translation[1])
        #print("Pitch: {} -> {} = {}".format(self.ypr[1], self.pid_pitch.setpoint, pitch))
        #print("Alt: {} -> {} = {}".format(self.translation[1], self.pid_alt.setpoint, thrust))
        #print(self.translation[1], end=",", flush=True)
        mots = typr_to_motors(thrust, yaw, pitch, roll)
        mots = [round(m, 3) for m in mots]
        self.set_motors(sock, mots)
        #print("Yaw: {}".format(yaw))