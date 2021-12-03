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

    def set_motors(self, sock, mots):
        sock.sendto(bytes("M"+"/".join([str(x) for x in mots]), "ascii"), self.addr)