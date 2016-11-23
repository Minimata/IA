

class City:
	def __init__(self, id, name, pos_x, pos_y):
		self.id = id
		self.name = name
		self.x = pos_x
		self.y = pos_y
		self.neighbours = {}

	def add_connection(self, neighbour, distance):
		self.neighbours[neighbour] = distance

	def __str__(self):
		return 'city {0} {1} : ({2}, {3})'.format(self.id, self.name, self.x, self.y)

	def __eq__(self, other):
		return self.id == other.id

	def __hash__(self):
		return self.id

