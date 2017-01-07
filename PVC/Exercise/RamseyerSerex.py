import pygame
from pygame.locals import KEYDOWN, QUIT, MOUSEBUTTONDOWN, K_RETURN, K_ESCAPE
from collections import namedtuple
import sys, argparse, csv, math


# CLASS DEFINITIONS

class City:
	def __init__(self, name, pos_x, pos_y):
		self.name = name
		self.x = pos_x
		self.y = pos_y

	def get_pos(self):
		return (self.x, self.y)

	def __str__(self):
		return 'city {0} {1} : ({2}, {3})'.format(self.name, self.x, self.y)
	#
	# def __eq__(self, other):
	# 	return self.id == other.id
	#
	# def __ne__(self, other):
	# 	return self.id != other.id
	#
	# def __lt__(self, other):
	# 	return self.id < other.id
	#
	# def __le__(self, other):
	# 	return self.id <= other.id
	#
	# def __gt__(self, other):
	# 	return self.id > other.id
	#
	# def __ge__(self, other):
	# 	return self.id >= other.id
	#
	# def __hash__(self):
	# 	return self.id


# METHOD DEFINITIONS
def draw(positions):
	screen.fill(0)
	for pos in positions:
		pygame.draw.circle(screen, city_color, pos.get_pos(), city_radius)
	text = font.render("Nombre: %i" % len(positions), True, font_color)
	textRect = text.get_rect()
	screen.blit(text, textRect)
	pygame.display.flip()


def draw_itinerary(text, cities):
	cities_pos = []
	for city in cities:
		cities_pos.append(city.get_pos())

	screen.fill(0)
	pygame.draw.lines(screen, city_color, True, cities_pos)
	title = font.render(text, True, font_color)
	textRect = title.get_rect()
	screen.blit(title, textRect)
	pygame.display.flip()


def parse_filename(filename):
	cities = []
	if filename:
		with open(filename, newline='') as f:
			reader = csv.reader(f, delimiter=" ")
			for name, x, y in reader:
				cities.append(City(name, int(x), int(y)))
	return cities


def init_itinerary(cities):
	result = []

	result.append(cities.pop())
	while cities:
		min = 0
		dist = math.inf
		for i, city in enumerate(cities):
			tmp = find_distance(result[-1], city)
			if tmp < dist:
				dist = tmp
				min = i
		result.append(cities.pop(min))

	cost = calculate_cost(result)

	return child(cost, result)


def calculate_cost(cities):
	cost = 0
	for i in range(1, len(cities)):
		cost += find_distance(cities[i - 1], cities[i])
	return cost


def find_distance(city1, city2):
	return math.sqrt((city1.x - city2.x) ** 2 + (city1.y - city2.y) ** 2)


def ga_solve(file=None, gui=True, maxtime=0):

	cost = 0
	itinerary = []

	cities = parse_filename(file)
	draw(cities)

	collecting = True
	id_count = 0
	while collecting and not file:
		for event in pygame.event.get():
			if event.type == QUIT:
				sys.exit(0)
			elif event.type == KEYDOWN and event.key == K_RETURN:
				collecting = False
			elif event.type == MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()
				cities.append(City(id_count, pos[0], pos[1]))
				id_count += 1
				draw(cities)

	adam = init_itinerary(cities)

	return [cost, adam.route]




# ARGS PARSING
parser = argparse.ArgumentParser(description='PVC Genetic solver')
parser.add_argument('--nogui', default=False, action='store_true')
parser.add_argument('--maxtime', default=0, type=int)
parser.add_argument('filename', nargs='?', default=None)
args = parser.parse_args()

nogui, maxtime, filename = [vars(args).get(k) for k in ['nogui', 'maxtime', 'filename']]

# INIT
child = namedtuple('child', 'cost route')

screen_x = screen_y = 500

city_color = [10, 10, 200]  # blue
city_radius = 3

font_color = [255, 255, 255]  # white

pygame.init()
window = pygame.display.set_mode((screen_x, screen_y))
pygame.display.set_caption('Exemple')
screen = pygame.display.get_surface()
font = pygame.font.Font(None, 30)

end = False

# LOOP
while not end:

	cost, itinerary = ga_solve(filename, not nogui, maxtime)
	draw_itinerary("Un chemin", itinerary)

	while True:
		event = pygame.event.wait()
		if event.type == KEYDOWN:
			if event.key == K_RETURN:
				collecting = True
				break
			else:
				end = True
				break

