import math
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
		totalx += cos(radians(i))
		totaly += sin(radians(i))
	return degrees(atan2(totaly/totalx))
	#this method is one i got from stackoverflow:
	#	-turn each angle into a unit vector
	#	-find the direction of their sum
	#you can't just add them as angles are cyclic and so "average" isn't
	#even really a meaningful concept for them.

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

	def start(self):
		self.R.wait_start()

	def move_linear(self,seconds, speed):
		#TODO: Change this code to utilise threading
		self.R.motors[0].m0.power = speed
		self.R.motors[0].m1.power = speed
		self.R.motors[1].m0.power = speed
		self.R.motors[1].m1.power = speed
		sleep(seconds)
		self.R.motors[0].m0.power = 0
		self.R.motors[0].m1.power = 0
		self.R.motors[1].m0.power = 0
		self.R.motors[1].m1.power = 0

	def get_position(self):
		markers = self.R.see(res=(1280,720)) #biggest res that works on both cameras
		locations_x = []
		locations_y = []
		rotations = []
		#first, for each marker, work out my rotation from its (known) rotation
		#and from how it appears to be rotated relative to me.
		for m in markers:
			if m.marker_type == MARKER_ARENA:
				if MARKER_DIRECTIONS(m.offset) == SOUTH: rot = m.rot_y
				elif MARKER_DIRECTIONS(m.offset) == WEST: rot = 270+m.rot_y
				elif MARKER_DIRECTIONS(m.offset) == NORTH: rot = 180+m.rot_y
				elif MARKER_DIRECTIONS(m.offset) == EAST: rot = 90+m.rot_y
				# i *think* the above code works
				# if it does, remove it and uncomment the next line
				#rot = m.rot_y + MARKER_DIRECTIONS(m.offset)
				rotations.append(rot)
		#then take my rotation as the average
		my_rotation = get_average_angle(rotations)

		#then get my position from each marker
		for m in markers:
			if m.marker_type == MARKER_ARENA:
				my_rotation_relative_to_it = 0-m.rot_y
				posx = MARKER_LOCATIONS(marker.offset)[0] + m.dist*cos(radians(my_rotation_relative_to_it))
				posy = MARKER_LOCATIONS(marker.offset)[1] + m.dist*cos(radians(my_rotation_relative_to_it))
				locations_x.append(posx)
				locations_y.append(posy)
		#and take my position as the average
		my_location = (get_average(locations_x), get_average(locations_y))
		#and hey, i'm not sure if this code even works! but hopefully it does.


