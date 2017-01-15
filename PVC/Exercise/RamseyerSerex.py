import pygame
from pygame.locals import KEYDOWN, QUIT, MOUSEBUTTONDOWN, K_RETURN, K_ESCAPE
from collections import namedtuple
from heapq import heappush, heappop
import time
from time import sleep
import sys, argparse, csv, math, random

# CLASS DEFINITIONS


class City:
	def __init__(self, name, id, pos_x, pos_y):
		self.name = name
		self.id = id
		self.x = pos_x
		self.y = pos_y

	def get_pos(self):
		return (self.x, self.y)

	def __str__(self):
		return 'city {0}'.format(self.name)

	def __eq__(self, other):
		return self.id == other.id

	def __ne__(self, other):
		return self.id != other.id

	def __lt__(self, other):
		return self.id < other.id

	def __le__(self, other):
		return self.id <= other.id

	def __gt__(self, other):
		return self.id > other.id

	def __ge__(self, other):
		return self.id >= other.id

	def __hash__(self):
		return self.id


# METHOD DEFINITIONS
def draw(positions, **kwargs):
	screen.fill(0)
	for pos in positions:
		pygame.draw.circle(screen, city_color, pos.get_pos(), city_radius)
	if kwargs.get('verbose', False):
		text = font.render("Nombre: %i" % len(positions), True, font_color)
		textRect = text.get_rect()
		screen.blit(text, textRect)
	pygame.display.flip()


def draw_itinerary(text, cities):
	cities_pos = []
	for city in cities:
		cities_pos.append(city.get_pos())

	# screen.fill(0)
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
			count = 0
			for name, x, y in reader:
				cities.append(City(name, count, int(x), int(y)))
				count += 1
	return cities


def init_itinerary(all_cities):
	"""
	Cette méthode permet d'initialiser un individu de la population d'origine
	à l'aide d'un algorithme glouton.
	Cet algo va parcrouir les villes en rejoignant toujours la ville la plus proche de son lieu actuel.
	En comparaison du reste de l'algorithme, elle est assez performante pour ne pas pas impacter sur
	la performances globale du programme. Elle donne également une bonne base pour débuter la partie génétique.
	"""

	result = []

	cities = list(all_cities)  # copy to let base list untouched
	result.append(cities.pop(0))
	while cities:
		min = 0
		dist = math.inf
		for i, city in enumerate(cities):
			tmp = euclidian(result[-1], city)
			if tmp < dist:
				dist = tmp
				min = i
		result.append(cities.pop(min))

	cost = calculate_cost(result)

	return child(cost, result)


def init_rand_itinerary(all_cities):
	"""
	Cette méthode génère un individu aléatoire pour la première population.
	"""
	result = []
	cities = list(all_cities)  # copy to let base list untouched
	result.append(cities.pop(0))
	while cities:
		i = random.randint(0, len(cities)-1)
		result.append(cities.pop(i))

	cost = calculate_cost(result)
	return child(cost, result)


def crossover(pop, sequence_proportion, child_proportion, num_parents_proportion):
	"""
	Cette méthode va effecteur des crossover sur toute la population, par plage successive.
	Elle commence par faire le crossover des individus les plus performants, puis va parcourir la population restante
	par pas successifs (le nombre de pas total étant défini par une proportion de la population totale) pour faire
	des crossovers sur toute la population.

	Ceci permet de toujours promouvoir les meilleurs parents mais cultive également un bon échantillon de la population
	totale, évitant de tomber trop facilement dans des minimums locaux.

	Tous les enfants comme les parents sont gardés dans la population pour être ensuite mutés et resélectionné.
	"""
	num_people = len(pop)
	# the elite
	mom = heappop(pop)
	dad = heappop(pop)
	crossover_one(pop, sequence_proportion, child_proportion, mom, dad)
	# keeping the parents for next selection
	heappush(pop, mom)
	heappush(pop, dad)

	# some pseudo random parents
	num_parents = int(num_people * num_parents_proportion)
	for _ in range(num_parents):
		mom = pop[random.randint(0, num_people - 1)]
		dad = pop[random.randint(0, num_people - 1)]
		crossover_one(pop, sequence_proportion, child_proportion, mom, dad)


def crossover_one(pop, sequence_proportion, child_proportion, mom, dad):
	"""
	La méthode de crossover est la méthode OX.
	On sélectionne une séquence au hasard dans le code génétique des parents et on les swap entre les deux parents.
	En évitant la redondance (avec les méthodes prepare_child et fill_sequence), on obtient finalement deux enfant
	distincts pour chaque crossover.
	"""
	num_cities = len(mom.route)
	num_children = int(child_proportion * num_cities)
	sequence_size = int(sequence_proportion * num_cities)
	begin = random.randint(0, num_cities - sequence_size - 1)
	end = begin + sequence_size

	sequ1 = fill_sequence(mom, begin, end)
	sequ2 = fill_sequence(dad, begin, end)

	for i in range(num_children):
		child1 = list(mom.route)
		child2 = list(dad.route)
		empty_idx1 = []
		empty_idx2 = []
		prepare_child(child1, mom.route, sequ2, empty_idx1, begin, end)
		prepare_child(child2, dad.route, sequ1, empty_idx2, begin, end)
		insert_sequence(child1, sequ2, empty_idx1, begin, end)
		insert_sequence(child2, sequ1, empty_idx2, begin, end)
		cost1 = calculate_cost(child1)
		cost2 = calculate_cost(child2)
		heappush(pop, child(cost1, child1))
		heappush(pop, child(cost2, child2))



def fill_sequence(parent, begin, end):
	sequ = []
	for i in range(begin, end):
		city = parent.route[i]
		sequ.append(city)
	return sequ


def insert_sequence(child, sequ, empty_idx, begin, end):
	for i in range(begin, end):
		if child[i] is not None:
			next_empty_idx = empty_idx.pop()
			child[i], child[next_empty_idx] = child[next_empty_idx], child[i]  # swap

		child[i] = sequ[i - begin]


def prepare_child(child, parent, sequence, empty_idx, begin, end):
	for i, city in enumerate(parent):
		if city in sequence:
			child[i] = None
			if not begin <= i < end:
				empty_idx.append(i)
		else:
			child[i] = city


def natural_selection(pop, num_cities):
	"""
	Pour la sélection, on ne prend que les N meilleurs individus pour N villes.
	"""
	return [heappop(pop) for _ in range(num_cities)]


def calculate_cost(cities):
	cost = 0
	for i in range(1, len(cities)):
		cost += euclidian(cities[i - 1], cities[i])
	return cost


def manhattan(city1, city2):
	return abs(city1.x - city2.x) + abs(city1.y - city2.y)  # Manhattan, because performance

def euclidian(city1, city2):
	return math.sqrt((city1.x - city2.x) ** 2 + (city1.y - city2.y) ** 2)


def populate(cities):
	population = []

	# interary with simple order from cities
	eve = child(calculate_cost(cities), list(cities))
	heappush(population, eve)

	# interary --> the next city is the closest
	adam = init_itinerary(list(cities))
	heappush(population, adam)

	# and finally some random fellows
	for _ in range(0, len(cities) - 2):
		heappush(population, init_rand_itinerary(cities))

	return population


def mutate(population, swap_proportion, proportion):
	"""
	Pour la mutation, on va sélectionner de manière random un certain pourcentage de la population pour la faire muter.
	On duplique un individu avant de le muter, et on garde les deux individus pour la prochaine sélection.
	"""
	nb_to_mute = int(len(population)*proportion)
	sequ_swap_size = int(len(population[0].route) * swap_proportion / 2)

	for _ in range(0, nb_to_mute):
		rand = random.randint(0, len(population)-1)
		heappush(population, mutateOne(population[rand], sequ_swap_size))

	return population


def mutateOne(fellow_in, sequence_size_swap):
	"""
	Pour la mutation, on sélectionne une séquence aléatoire de taille aléatoire comprise entre 0 et la moitié de la
	longueur d'un individu, dans la première partie de l'individu. On échange ensuite cette séquence avec une autre
	séquence, de même taille, sur la deuxième moitié de l'individu.
	On swap donc des portions de routes, et pas que des villes isolées.
	"""
	route = list(fellow_in.route)
	idx_begin1 = random.randint(0, int(len(route) / 2 - sequence_size_swap - 1))
	idx_begin2 = random.randint(int(len(route) / 2), int(len(route) - sequence_size_swap - 1))
	idx_end1 = idx_begin1 + sequence_size_swap
	idx_end2 = idx_begin2 + sequence_size_swap

	sub_list1 = route[idx_begin1:idx_end1 + 1]
	sub_list2 = route[idx_begin2:idx_end2 + 1]
	sub_list1, sub_list2 = sub_list2, sub_list1
	route[idx_begin1:idx_end1 + 1] = sub_list1
	route[idx_begin2:idx_end2 + 1] = sub_list2

	return child(calculate_cost(route), route)


def ga_solve(file=None, gui=True, maxtime=0):
	cities = parse_filename(file)
	if gui:
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
				cities.append(City(id_count, id_count, pos[0], pos[1]))
				id_count += 1
				draw(cities, verbose=True)

	cost_old = 0
	cpt = 0

	num_cities = len(cities)
	t0 = time.clock()

	population = populate(cities)

	# if maxtime equals 0 the counter will stop the loop when it will reach max_no_cost_change
	# otherwise the timer will stop it
	# the counter is incremented when there is no cost change between two iterations of the loop
	while (maxtime != 0 and time.clock() - t0 <= maxtime) or (maxtime == 0 and cpt <= max_no_cost_change):
		crossover(population, crossover_sequence_size, crossover_child_proportion, num_parents_proportion)
		mutate(population, mutation_num_swap, mutation_proportion)
		population = natural_selection(population, num_cities)

		if cost_old == population[0].cost:
			cpt += 1

		cost_old = population[0].cost

		if gui:
			draw(cities)
			draw_itinerary("Un chemin de cout {0}".format(population[0].cost), population[0].route)

	chosen_one = heappop(population)
	print("found route with cost {0}".format(chosen_one.cost))
	return [chosen_one.cost, chosen_one.route]


def display_population(pop):
	print("")
	print("Population")
	population = list(pop)
	count = 0
	while population:
		count += 1
		child = heappop(population)
		print("{0} : cost {1}".format(count, child.cost))
		# print("route :")
		# for city in child.route:
		# 	print("\t id : {0}".format(city.id))

# ARGS PARSING
parser = argparse.ArgumentParser(description='PVC Genetic solver')
parser.add_argument('--nogui', default=False, action='store_true')
parser.add_argument('--maxtime', default=0, type=int)
parser.add_argument('filename', nargs='?', default=None)
args = parser.parse_args()

nogui, maxtime, filename = [vars(args).get(k) for k in ['nogui', 'maxtime', 'filename']]
gui = not nogui

# INIT
child = namedtuple('child', 'cost route')
crossover_sequence_size = 0.5
crossover_child_proportion = 0.1
mutation_num_swap = 0.2
mutation_proportion = 1
num_parents_proportion = 0.02
max_no_cost_change = 500

screen_x = screen_y = 500

city_color = [10, 10, 200]  # blue
city_radius = 3

font_color = [255, 255, 255]  # white

pygame.init()
if gui:
	window = pygame.display.set_mode((screen_x, screen_y))
	pygame.display.set_caption('Exemple')
	screen = pygame.display.get_surface()
	font = pygame.font.Font(None, 30)

end = False

# LOOP
while not end:

	cost, itinerary = ga_solve(filename, gui, maxtime)
	if gui:
		draw_itinerary("Un chemin de cout {0}".format(cost), itinerary)
		while True:
			event = pygame.event.wait()
			if event.type == KEYDOWN:
				if event.key == K_RETURN:
					collecting = True
					break
				else:
					end = True
					break
	else:
		end = True
