import pygame
from pygame.locals import KEYDOWN, QUIT, MOUSEBUTTONDOWN, K_RETURN, K_ESCAPE
import sys


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


def generate_itinerary(cities):
	return cities


while not end:
	cities = []
	draw(cities)

	collecting = True
	while collecting:
		for event in pygame.event.get():
			if event.type == QUIT:
				sys.exit(0)
			elif event.type == KEYDOWN and event.key == K_RETURN:
				collecting = False
			elif event.type == MOUSEBUTTONDOWN:
				cities.append(pygame.mouse.get_pos())
				draw(cities)

	itinerary = generate_itinerary(cities)
	draw_itinerary("Un chemin", cities)

	while True:
		event = pygame.event.wait()
		if event.type == KEYDOWN:
			if event.key == K_RETURN:
				collecting = True
				break
			else:
				end = True
				break
