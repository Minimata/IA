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


def g0(*args):
	return 0


def g1(base_cost, current_city, destination):
	'''Cost function to minimize total travel distance'''
	return base_cost + current_city.neighbours[destination.name]


def g2(base_cost, *args):
	'''Cost function to minimize number of cities to visit'''
	return base_cost + 1


def a_star(city_from, city_to, h=h3, g=g1, **kwargs):
	'''A* Algorithm'''

	# frontiere is made of tuples with (city, cost_from_source, parent)
	# here we initialize frontiere with the first city, where we start the journey
	# its base cost is 0, and its parent is None
	frontiere = []
	CityInfo = namedtuple('city_info', 'prio cost city parent')
	source = CityInfo(prio=0, cost=0, city=city_from, parent=None)
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
				cost_i = g(cost, city, dest)
				dest_info = CityInfo(prio=h(dest, city_to) + cost_i, cost=cost_i, city=dest, parent=city)
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
		if kwargs.get('verbose', False):
			print("Went to %s" % city)
		if kwargs.get('debug', False):
			print("FRONTIERE")
			for j in frontiere:
				print("{0} \t cost : {1} \t priority : {2}".format(j.city, j.cost, j.prio))
			print("HIST")
			print(*hist, sep="\n")
			print("")


def print_itinerary(iti):
	print("Go trough :")
	for info in iti:
		print(" - {0} \t then ".format(info.city))


if __name__ == '__main__':
	positions = sys.argv[1]
	connections = sys.argv[2]
	all_cities = {}

	with open(positions, newline='') as f:
		count = 0
		reader = csv.reader(f, delimiter=" ")
		for name, x, y in reader:
			all_cities[name] = City(count, name, int(x), int(y))
			count += 1

	with open(connections, newline='') as f:
		reader = csv.reader(f, delimiter=" ")
		for src, dst, cost in reader:
			all_cities[src].add_connection(dst, int(cost))
			all_cities[dst].add_connection(src, int(cost))

	start = all_cities['Warsaw']
	objective = all_cities['Lisbon']
	print('From {0} to {1}'.format(start, objective))

	'''
	Il se trouve que les performances en terme de nombre d'itérations dans la boucle (et donc en terme de villes
	visitées) varient peu selon les heuristiques (18 +/- 1 villes).
	Ceci est susceptible de changer lors de l'application de A* dans des graphes plus conséquents.
	A noter que si A* trouve deux villes avec la même priorité, elles seront trié par ID, donc arbitrairement.
	Cette implémentaiton de A* n'est donc pas stable.

	On priviligiera une heuristique vol d'oiseau car optimiste, toujours plus petite ou égale à la distance réelle
	et nulle lorsque l'on est a destination (par définition de l'heuristique, mais quand même).
	Si on cherche une excellente performance, le vol d'oiseau n'est pas recommandé car couteux en ressources (nécessite
	une racine carrée). Ici, Manhattan donne de bons résultats pour un calcul moins couteux que le vol d'oiseau.
	Ceci n'est toutefois pas un comportement général. Manhattan a tendance à surestimer le cout réel d'une distance,
	là ou le vol d'oiseau est toujours plus petit ou égal, ce qui est nécessaire au bon fonctionnement de l'algorithme.

	Toutes ces heuristiques d'ailleurs sont admissibles : elles valents toutes 0 à la cible.
	Manhattan n'est cependant pas consistante, car elle risque de surestimer le cout d'une distance alors que A*
	ne travaille correctement qu'avec des heuristiques qui sous-estiment le cout réel (ou trouvent un résultat égal).

	Dans la réalité, le graphe peut être pondéré par beaucoup de valeurs. Les heuristiques et cout peuvent devenir très
	complexes et il est important de bien les définir et les choisir en fonction des besoins (itinéraire optimal,
	performances, cout mémoire, etc.)
	'''
	for h in [h0, h1, h2, h3, h4]:
		dest, cost, iteration, opened, itinerary = a_star(start, objective, h, g1, verbose=False, debug=False)
		print("Reached {0} with cost {1} in {2} iterations with {3} still open cities".format(dest, cost, iteration, opened))
		print_itinerary(itinerary)

	'''
	Ici, on change le cout. On ne parle plus de km parcourus mais de nombre de villes visitées.
	Ce cout-ci nous permet de voir que deux heuristiques différentes peuvent produire un itinéraire différent
	(cas que nous n'avons pas réussi à provoquer avec les fonctions ci-dessus avec le cout standard).

	Ceci montre que A* ne prétend pas toujours trouver le chemin optimal, mais trouve un chemin suboptimal.
	Un chemin qui sera bon, pas forcément le meilleur, mais au moins le temps pour le trouver est largement
	inférieur par rapport à un parcours en largeur qui lui, assure de trouver le chemin optimal mais au prix d'énormes
	ressources.

	Si cette implémentation de A* donne des itinéraire si différent en fonction des heuristiques, c'est parce que le
	cout est négligeable par rapport à l'heuristique, ce qui revient à faire un parcours en profondeur en suivant
	bêtement l'heuristique.
	'''
	dest, cost, iteration, opened, itinerary = a_star(start, objective, h0, g2, verbose=False, debug=False)
	print("Reached {0} with cost {1} in {2} iterations with {3} still open cities".format(dest, cost, iteration, opened))
	print_itinerary(itinerary)
	dest, cost, iteration, opened, itinerary = a_star(start, objective, h3, g2, verbose=False, debug=False)
	print("Reached {0} with cost {1} in {2} iterations with {3} still open cities".format(dest, cost, iteration, opened))
	print_itinerary(itinerary)

