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
	These functions would have been better with *args / **kwargs arguments to allow any kind of heuristic / cost computation
	'''

	# frontiere is made of tuples with (city, cost_from_source, parent)
	# here we initialize frontiere with the first city, where we start the journey
	# its base cost is 0, and its parent is None
	frontiere = []
	heappush(frontiere, (0, city_from, f_cost(0, city_from, city_from), None))

	# keeping a trace of visited cities to prevent going in circles
	hist = set()

	# itinerary is kind of like hist but is used to recreate the best travel plan once the destination has been reached
	itinerary = {}

	# calculate iterations
	i = 0
	while frontiere:
		i += 1
		city_info = heappop(frontiere)  # We get the next city to visit, the 'closest one' according to heuristic + cost
		a_star_cost, city, cost, city_parent = city_info  # city_parent & a_star_cost unused

		hist.add(city)
		itinerary[city] = city_info

		if city == city_to:  # meaning we arrived at destination
			open_cities = len(frontiere)
			city_i = city
			it = []  # this will store our final itinerary
			while city_i is not None:  # we recreate the best itinerary from destination to source, parent to parent
				it.append(itinerary[city_i])
				city_i = itinerary[city_i][3]

			info = (city, cost, i, open_cities, reversed(it))
			return info

		# reached only if destination isn't met
		for possible_destination in city.neighbours:
			dest = all_cities[possible_destination]
			if dest not in hist:
				# For every neighbour of a city, we add it to the frontiere with updated cost if it has
				# not already been visited before
				cost_i = f_cost(cost, city, dest)
				heappush(frontiere, (f_heuristic(dest, city_to) + cost_i, dest, cost_i, city))

		# We then delete duplicate cities in our frontiere and only keep the ones with the best heuristic + cost
		visited_cities = set()
		new_frontiere = []
		while frontiere:
			recurring = heappop(frontiere)
			if recurring[1] not in visited_cities:
				heappush(new_frontiere, recurring)
				visited_cities.add(recurring[1])
		frontiere = new_frontiere

		# DEBUG - displays current city, frontiere and hist at any iteration
		print("Went to %s" % city)
		print("FRONTIERE")
		for j in frontiere:
			print("{0} \t cost : {1} \t priority : {2}".format(j[1], j[2], j[0]))
		print("HIST")
		print(*hist, sep="\n")
		print("")
		print("")


if __name__ == '__main__':
	positions = sys.argv[1]
	connections = sys.argv[2]
	all_cities = {}

	with open(positions) as f:
		count = 0
		for line in f:
			info = line.split(' ')
			all_cities[info[0]] = City(count, info[0], int(info[1]), int(info[2]))
			all_cities[info[0]].add_connection(info[0], 0)  # every city is connected to itself, with distance 0
			count += 1

	with open(connections) as f:
		for line in f:
			info = line.split(' ')
			all_cities[info[0]].add_connection(info[1], int(info[2]))
			all_cities[info[1]].add_connection(info[0], int(info[2]))

	start = all_cities['Warsaw']
	objective = all_cities['Lisbon']
	print('From %s to %s' % (start, objective))

	dest, cost, iter, open, itinerary = a_star(start, objective, h1, g1)
	print("Reached {0} with cost {1} in {2} iterations with {3} still open cities".format(dest, cost, iter, open))
	print("Go trough :")
	for info in itinerary:
		print(" - %s \t then " % info[1])




