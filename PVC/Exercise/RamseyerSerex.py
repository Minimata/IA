import pygame
from pygame.locals import KEYDOWN, QUIT, MOUSEBUTTONDOWN, K_RETURN, K_ESCAPE
import sys, argparse, csv


# METHOD DEFINITIONS
def draw(positions):
	screen.fill(0)
	for pos in positions:
		pygame.draw.circle(screen, city_color, pos, city_radius)
	text = font.render("Nombre: %i" % len(positions), True, font_color)
	textRect = text.get_rect()
	screen.blit(text, textRect)
	pygame.display.flip()


def draw_itinerary(text, cities):
	screen.fill(0)
	pygame.draw.lines(screen, city_color, True, cities)
	title = font.render(text, True, font_color)
	textRect = title.get_rect()
	screen.blit(title, textRect)
	pygame.display.flip()



def parse_filename(filename):
	cities = {}
	if filename:
		with open(filename, newline='') as f:
			reader = csv.reader(f, delimiter=" ")
			for name, x, y in reader:
				cities[name] = (int(x), int(y))
	return cities


def ga_solve(file=None, gui=True, maxtime=0):
	pass




# ARGS PARSING
parser = argparse.ArgumentParser(description='PVC Genetic solver')
parser.add_argument('--nogui', default=False, action='store_true')
parser.add_argument('--maxtime', default=0, type=int)
parser.add_argument('filename', nargs='?', default=None)
args = parser.parse_args()

nogui, maxtime, filename = [vars(args).get(k) for k in ['nogui', 'maxtime', 'filename']]

# INIT
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
	cities = parse_filename(filename)  # if filename fill cities
	draw(list(cities.values()))

	collecting = True
	id_count = 0
	while collecting and not filename:
		for event in pygame.event.get():
			if event.type == QUIT:
				sys.exit(0)
			elif event.type == KEYDOWN and event.key == K_RETURN:
				collecting = False
			elif event.type == MOUSEBUTTONDOWN:
				cities[id_count] = (pygame.mouse.get_pos())
				id_count += 1
				draw(list(cities.values()))

	ga_solve(filename, not nogui, maxtime)
	draw_itinerary("Un chemin", list(cities.values()))

	while True:
		event = pygame.event.wait()
		if event.type == KEYDOWN:
			if event.key == K_RETURN:
				collecting = True
				break
			else:
				end = True
				break



