# |y (up)
# |   
# |    / z (forwards)
# |  /
# |/
#  \
#    \
#      \ x (right)

'''

A       B
  \   /
    X
  /   \ 
C       D

'''

from pid import *

def typr_to_motors(thrust, yaw, pitch, roll):
    return [
          yaw + pitch + roll + thrust,
        - yaw + pitch - roll + thrust,
        - yaw - pitch + roll + thrust,
          yaw - pitch - roll + thrust
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
        
        self.pid_yaw   = PidController(30,10,5,    0,  10, -100,100)
        self.pid_pitch = PidController(5,1,8,    0,  10, -100,100)
        self.pid_roll  = PidController(5,1,8,    0,  10, -100,100)
        self.pid_alt   = PidController(5,1,7.5,  15, 10, -100,100)

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
        roll = self.pid_pitch.compute(self.ypr[2])
        thrust = self.pid_alt.compute(self.translation[1])
        
        self.set_motors(sock, typr_to_motors(thrust, yaw, 0, 0))
        #print("Yaw: {}".format(yaw))