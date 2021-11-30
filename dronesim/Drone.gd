extends RigidBody

const power = 10
var server_addr = "127.0.0.1"
var server_port = 14444
var sock = PacketPeerUDP.new()
var registered = false
var send_elapsed = 0
var sensrate = 10

# Linear acceleration
var linacc
# Rotational acceleration
var rotacc

# For calculating acceleration
var v0 # prev velocity (x,y,z)
var a0 # prev angular vel (around x,y,z)

var mots = [
	0,0,
	0,0
]

var mot_dirs = [ # 1 = clockwise, -1 = counter-clockwise
	1, -1,
	-1, 1
]

var mot_offsets = [
	Vector3(4.5,0,4.5), Vector3(-4.5,0,4.5),
	Vector3(4.5,0,-4.5), Vector3(-4.5,0,-4.5)
]

func _ready():
	if sock.listen(14445, server_addr) != OK:
		print("Error listening")
	else:
		sock.set_dest_address(server_addr, server_port)
		sock.put_packet("N".to_ascii()) # Register self with server

func add_force_local(force: Vector3, pos: Vector3):
	var pos_local = self.transform.basis.xform(pos)
	var force_local = self.transform.basis.xform(force)
	self.add_force(force_local, pos_local)

func _physics_process(delta):
	if v0 and a0:
		linacc = (self.linear_velocity - v0) / delta
		rotacc = (self.angular_velocity - a0) / delta
		
		send_elapsed += delta
		if send_elapsed >= 1/sensrate:
			sock.put_packet(("SP" + str(self.translation[0]) 
				+ "/" + str(self.translation[2])
				+ ":G" + str(self.rotacc[0]) + "/" + str(self.rotacc[1]) + "/" + str(self.rotacc[2])
				+ ":A" + str(self.linacc[0]) + "/" + str(self.linacc[1]) + "/" + str(self.linacc[2])
				).to_ascii())
			send_elapsed = 0
	v0 = self.linear_velocity
	a0 = self.angular_velocity
	
	for i in range(sock.get_available_packet_count()):
		var msg = sock.get_packet().get_string_from_ascii()
		print("From server: ", msg)
		if msg[0] == 'M':
			var val_strings = msg.right(1).split("/")
			mots = []
			for v in val_strings:
				mots.append((float(v)/100) * power)
	
	var torque = 0
	for i in range(4):
		if mots[i] < 0: mots[i] = 0
		torque += mots[i] * mot_dirs[i]
		add_force_local(Vector3(0,mots[i],0), mot_offsets[i])
	add_torque(Vector3(0,torque,0))

