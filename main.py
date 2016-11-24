import sys
import math
import csv
from city import City
from heapq import heappush, heappop
from collections import namedtuple


def h0(*args):
	'''Heuristic function that does nothing =)'''
	return 0


def h1(current_city, destination):
	'''Heuristic function based on distance on the x axis only'''
	return abs(current_city.x - destination.x)


def h2(current_city, destination):
	'''Heuristic function based on distance on the y axis only'''
	return abs(current_city.y - destination.y)


def h3(current_city, destination):
	'''Heuristic function based on distance as the crow flies (raw direct distance)'''
	return math.sqrt((current_city.x - destination.x) ** 2 + (current_city.y - destination.y) ** 2)


def h4(current_city, destination):
	'''Heuristic function based on Manhattan distance'''
	return abs(current_city.x - destination.x) + abs(current_city.y - destination.y)


def g1(base_cost, current_city, destination):
	'''Cost function to minimize total travel distance'''
	return base_cost + current_city.neighbours[destination.name]


def g2(base_cost, *args):
	'''Cost function to minimize number of cities to visit'''
	return base_cost + 1


def a_star(city_from, city_to, f_heuristic, f_cost):
	'''A* Algorithm. Arguments are
	 - A city to start to
	 - A city to go
	 - A heuristic function, taking two cities in argument (current and destination)
	 - A cost function, taking as arguments the cost of current city, the current city and the destination
	@:arg city_from:
	'''

	# frontiere is made of tuples with (city, cost_from_source, parent)
	# here we initialize frontiere with the first city, where we start the journey
	# its base cost is 0, and its parent is None
	frontiere = []
	city_info = namedtuple('city_info', 'prio cost city parent')
	source = city_info(prio=0, cost=0, city=city_from, parent=None)
	heappush(frontiere, source)

	# keeping a trace of visited cities to prevent going in circles
	hist = set()

	# itinerary is kind of like hist but is used to recreate the best travel plan once the destination has been reached
	itinerary = {}

	# calculate iterations
	i = 0
	while frontiere:
		i += 1
		info = heappop(frontiere)  # We get the next city to visit, the 'closest one' according to heuristic + cost
		a_star_cost, cost, city, city_parent = info  # city_parent & a_star_cost unused

		hist.add(city)
		itinerary[city] = info

		if city == city_to:  # meaning we arrived at destination
			open_cities = len(frontiere)
			city_i = city
			final_iti = []  # this will store our final itinerary
			while city_i is not None:  # we recreate the best itinerary from destination to source, parent to parent
				final_iti.append(itinerary[city_i])
				city_i = itinerary[city_i].parent

			final = (city, cost, i, open_cities, reversed(final_iti))
			return final

		# reached only if destination isn't met
		for possible_destination in city.neighbours:
			dest = all_cities[possible_destination]
			if dest not in hist:
				# For every neighbour of a city, we add it to the frontiere with updated cost if it has
				# not already been visited before
				cost_i = f_cost(cost, city, dest)
				dest_info = city_info(prio=f_heuristic(dest, city_to) + cost_i, cost=cost_i, city=dest, parent=city)
				heappush(frontiere, dest_info)

		# We then delete duplicate cities in our frontiere and only keep the ones with the best heuristic + cost
		visited_cities = set()
		new_frontiere = []
		while frontiere:
			recurring = heappop(frontiere)
			if recurring.city not in visited_cities:
				heappush(new_frontiere, recurring)
				visited_cities.add(recurring.city)
		frontiere = new_frontiere

		# DEBUG - displays current city, frontiere and hist at any iteration
		print("Went to %s" % city)
		print("FRONTIERE")
		for j in frontiere:
			print("{0} \t cost : {1} \t priority : {2}".format(j.city, j.cost, j.prio))
		print("HIST")
		print(*hist, sep="\n")
		print("")
		print("")


if __name__ == '__main__':
	positions = sys.argv[1]
	connections = sys.argv[2]
	all_cities = {}

	with open(positions, newline='') as f:
		count = 0
		reader = csv.reader(f, delimiter=" ")
		for name, x, y in reader:
			all_cities[name] = City(count, name, int(x), int(y))
			all_cities[name].add_connection(name, 0)
			count += 1

	with open(connections) as f:
		reader = csv.reader(f, delimiter=" ")
		for src, dst, cost in reader:
			all_cities[src].add_connection(dst, int(cost))
			all_cities[dst].add_connection(src, int(cost))

	start = all_cities['Warsaw']
	objective = all_cities['Lisbon']
	print('From {0} to {1}'.format(start, objective))

	dest, cost, iter, open, itinerary = a_star(start, objective, h1, g1)
	print("Reached {0} with cost {1} in {2} iterations with {3} still open cities".format(dest, cost, iter, open))
	print("Go trough :")
	for info in itinerary:
		print(" - {0} \t then ".format(info.city))




