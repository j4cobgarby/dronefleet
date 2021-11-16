extends RigidBody

const power = 4.5

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
	pass

func add_force_local(force: Vector3, pos: Vector3):
	var pos_local = self.transform.basis.xform(pos)
	var force_local = self.transform.basis.xform(force)
	self.add_force(force_local, pos_local)

func _physics_process(delta):
	mots = [0,0,0,0]
	
	if Input.is_action_pressed("w"):
		mots[2] += power
		mots[3] += power
	if Input.is_action_pressed("a"):
		mots[1] += power
		mots[3] += power
	if Input.is_action_pressed("s"):
		mots[0] += power
		mots[1] += power
	if Input.is_action_pressed("d"):
		mots[0] += power
		mots[2] += power
	if Input.is_action_pressed("q"):
		mots[1] -= power
		mots[0] += power
		mots[2] -= power
		mots[3] += power
	if Input.is_action_pressed("e"):
		mots[0] -= power
		mots[1] += power
		mots[2] += power
		mots[3] -= power
	if Input.is_action_pressed("up"):
		mots[0] += power
		mots[1] += power
		mots[2] += power
		mots[3] += power
	
	var torque = 0
	for i in range(4):
		if mots[i] < 0: mots[i] = 0
		torque += mots[i] * mot_dirs[i]
		add_force_local(Vector3(0,mots[i],0), mot_offsets[i])
	add_torque(Vector3(0,torque,0))

