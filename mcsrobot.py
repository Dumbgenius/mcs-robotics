import math
import time
from sr.robot import *


MARKER_LOCATIONS = [
	#arena north (markers 0-6)
	(1, 0),
	(2, 0),
	(3, 0),
	(4, 0),
	(5, 0),
	(6, 0),
	(7, 0),
	#arena east (markers 7-13)
	(8, 1),
	(8, 2),
	(8, 3),
	(8, 4),
	(8, 5),
	(8, 6),
	(8, 7),
	#arena south (markers 14-20)
	(7, 8),
	(6, 8),
	(5, 8),
	(4, 8),
	(3, 8),
	(2, 8),
	(1, 8),
	#arena west (markers 21-27)
	(0, 7),
	(0, 6),
	(0, 5),
	(0, 4),
	(0, 3),
	(0, 2),
	(0, 1),
]

NORTH = 0
EAST = 90
SOUTH = 180
WEST = 270

MARKER_DIRECTIONS = [
	SOUTH, SOUTH, SOUTH, SOUTH, SOUTH, SOUTH, SOUTH,
	WEST,  WEST,  WEST,  WEST,  WEST,  WEST,  WEST,
	NORTH, NORTH, NORTH, NORTH, NORTH, NORTH, NORTH,
	EAST,  EAST,  EAST,  EAST,  EAST,  EAST,  EAST 
]

def get_average(l):
	total = 0
	for i in l: total += i
	return total/len(l)

def get_average_angle(l):
	totalx = 0
	totaly = 0
	for i in l:
		totalx += math.cos(radians(i))
		totaly += math.sin(radians(i))
	return math.degrees(math.atan2(totaly/totalx))
	# this method is one I got from stackoverflow:
	#	-turn each angle into a unit vector
	#	-find the direction of their sum
	# it's like this as you can't just add them since angles are cyclic and so 
	# "average" isn't even really a meaningful concept for them.

class NotSureWhatHappenedError(Exception):
	"""The standard error for the MCS Robot."""
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)
		

class MCSRobot():
	"""The MCS Robot class. It holds all the robot's important variables and functions."""
	def __init__(self):
		self.R = Robot()
		self.position = None
		self.rotation = None

	def start(self):
		self.R.wait_start()

	def move_linear(self,seconds, speed):
		#TODO: Change this code to utilise threading
		self.R.motors[0].m0.power = speed
		self.R.motors[0].m1.power = speed
		self.R.motors[1].m0.power = speed
		self.R.motors[1].m1.power = speed
		time.sleep(seconds)
		self.R.motors[0].m0.power = 0
		self.R.motors[0].m1.power = 0
		self.R.motors[1].m0.power = 0
		self.R.motors[1].m1.power = 0

	def get_position(self):
		markers = self.R.see(res=(1280,720)) #biggest res that works on both cameras
		positions_x = []
		positions_y = []
		rotations = []
		#first, for each marker, work out my rotation from its (known) rotation
		#and from how it appears to be rotated relative to me.
		for m in markers:
			if m.marker_type == MARKER_ARENA:
				if MARKER_DIRECTIONS[m.offset] == SOUTH: rot = m.rot_y
				elif MARKER_DIRECTIONS[m.offset] == WEST: rot = 270+m.rot_y
				elif MARKER_DIRECTIONS[m.offset] == NORTH: rot = 180+m.rot_y
				elif MARKER_DIRECTIONS[m.offset] == EAST: rot = 90+m.rot_y
				# i *think* the above code works
				# if it does, remove it and uncomment the next line
				#rot = m.rot_y + MARKER_DIRECTIONS[m.offset]
				rotations.append(rot)
		#then take my rotation as the average
		self.rotation = get_average_angle(rotations)

		#then get my position from each marker
		for m in markers:
			if m.marker_type == MARKER_ARENA:
				my_rotation_relative_to_it = 0-m.rot_y
				posx = MARKER_LOCATIONS[marker.offset][0] + m.dist*math.cos(radians(my_rotation_relative_to_it))
				posy = MARKER_LOCATIONS[marker.offset][1] + m.dist*math.cos(radians(my_rotation_relative_to_it))
				positions_x.append(posx)
				positions_y.append(posy)
		#and take my position as the average
		self.position = (get_average(positions_x), get_average(positions_y))
		#and hey, i'm not sure if this code even works! but hopefully it does.

	def test_speed_bursts(tests=10, seconds_per_test=1, test_speed=100):
		"""This function drives the robot back and forwards in a straight line, and works out the average distance travelled from doing so."""
		forward_distances = []
		backward_distances = []
		for x in range(tests):
			get_position()
			pos = self.position #get initial position
			move_linear(seconds_per_test, test_speed) #move forward
			get_position() #get new position
			forward_distances.append(math.sqrt((self.position[0]-pos[0])**2 + (self.position[1]-pos[1])**2)) #and get the distance

			#...and then do the same, but drive backwards
			get_position()
			pos = self.position
			move_linear(seconds_per_test, -test_speed)
			get_position()
			backward_distances.append(sqrt(self.position[0]**2 + self.position[1]**2))

		print("Forwards speed: "+(get_average(forward_distances)/seconds_per_test)+" metres per "+seconds_per_test+" second burst at motor speed "+test_speed+".")
		print("Reverse speed: "+(get_average(backward_distances)/seconds_per_test)+" metres per "+seconds_per_test+" second burst at motor speed -"+test_speed+".")
		print("Averaged from "+tests+" tests.")

	def test_speed_continuous(seconds=5, delay=0.2, speed=100):
		get_position()
		start_time = time.time()
		t = start_time
		speeds = []

		self.R.motors[0].m0.power = speed
		self.R.motors[0].m1.power = speed
		self.R.motors[1].m0.power = speed
		self.R.motors[1].m1.power = speed

		while (t < start_time+5):
			pos = self.position #save position
			time.sleep(delay) #wait (while moving forward)
			get_position() #get new position
			speeds.append(math.sqrt((self.position[0]-pos[0])**2 + (self.position[1]-pos[1])**2) / time.time()-t) #speed = displacement / time
			t = time.time() #set time again

		self.R.motors[0].m0.power = 0
		self.R.motors[0].m1.power = 0
		self.R.motors[1].m0.power = 0
		self.R.motors[1].m1.power = 0

		print("Speed: "+get_average(speeds)+"m/s at motor speed "+speed)





