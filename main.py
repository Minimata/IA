import sys
from City import City
import math


'''Heuristic function that does nothing =)'''
def h0(*args):
	return 0

'''Heuristic function based on distance on the x axis only'''
def h1(current_city, destination):
	return abs(current_city.x - destination.x)


'''Heuristic function based on distance on the y axis only'''
def h2(current_city, destination):
	return abs(current_city.y - destination.y)


'''Heuristic function based on distance as the crow flies (raw direct distance)'''
def h3(current_city, destination):
	return math.sqrt((current_city.x - destination.x) ** 2 + (current_city.y - destination.y) ** 2)


'''Heuristic function based on Manhattan distance'''
def h4(current_city, destination):
	return abs(current_city.x - destination.x) + abs(current_city.y - destination.y)


'''Cost function to minimize total travel distance'''
def g1(base_cost, current_city, destination):
	return base_cost + current_city.neighbours[destination.name]


'''Cost function to minimize number of cities to visit'''
def g2(base_cost, *args):
	return base_cost + 1


'''A* Algorithm. Arguments are
 - A city to start to
 - A city to go
 - A heuristic function, taking two cities in argument (current and destination)
 - A cost function, taking as arguments the cost of current city, the current city and the destination
These functions would have been better with *args / **kwargs arguments to allow any kind of heuristic / cost computation
'''
def a_star(city_from, city_to, f_heuristic, f_cost):

	# frontiere is made of tuples with (city, cost_from_source, parent)
	# here we initialize frontiere with the first city, where we start the journey
	# its base cost is 0, and its parent is None
	frontiere = [(city_from, f_cost(0, city_from, city_from), None)]

	# keeping a trace of visited cities to prevent going in circles
	hist = set()

	# itinerary is kind of like hist but is used to recreate the best travel plan once the destination has been reached
	itinerary = {}

	# calculate iterations
	i = 0
	while frontiere:
		i += 1
		city_info = frontiere.pop(0)  # We get the next city to visit, the 'closest one' according to heuristic + cost
		city, cost, city_parent = city_info  # city_parent unused

		hist.add(city)
		itinerary[city] = city_info

		if city == city_to:  # meaning we arrived at destination
			open_cities = len(frontiere)
			city_i = city
			it = []  # this will store our final itinerary
			while city_i is not None:  # we recreate the best itinerary from destination to source, parent to parent
				it.append(itinerary[city_i])
				city_i = itinerary[city_i][2]

			info = (city, cost, i, open_cities, reversed(it))
			return info

		for possible_destination in city.neighbours:  # reached only if destination isn't met
			dest = all_cities[possible_destination]
			if dest not in hist:
				# For every neighbour of a city, we add it to the frontiere with updated cost if it has
				# not already been visited before
				frontiere.append((dest, f_cost(cost, city, dest), city))
		# We sort the frontiere based on heuristic and cost functions (cost has already been calculated before)
		frontiere.sort(key=lambda x: f_heuristic(x[0], city_to) + x[1])

		# We then delete duplicate cities in our frontiere and only keep the ones with the best heuristic + cost
		visited_cities = set()
		new_frontiere = []
		for recurring in frontiere:
			if recurring[0] not in visited_cities:
				new_frontiere.append(recurring)
			visited_cities.add(recurring[0])
		frontiere = new_frontiere

		# DEBUG - displays current city, frontiere and hist at any iteration
		print("Went to %s" % city)
		print("FRONTIERE")
		for j in frontiere:
			print("%s \t cost : %s \t priority : %s" % (j[0], j[1], h1(j[0], city_to) + j[1]))
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

	path = a_star(start, objective, h1, g1)
	print("Reached %s with cost %s in %s iterations with %s open ways" % (path[0], path[1], path[2], path[3]))
	print("Go trough :")
	itinerary = path[4]
	for info in itinerary:
		print(" - %s \t then " % info[0])




