# ------------------------------------------------------------------------- #
title = "Map Editor v0.0.1-dev (for dungeon test)"                          #
# By Douglas J. Honeycutt                                                   #
# https://withacact.us/ | https://github.com/RidleyofZebes/hero-simulator   #
# ------------------------------------------------------------------------- #ww

import os
import pygame
import pickle
import pprint

pygame.init()

window_res = (1024, 768)

gw = pygame.display.set_mode(window_res)
pygame.display.set_caption(title)
clock = pygame.time.Clock()
pygame.key.set_repeat(10, 50)

# Colors
black = (0, 0, 0)
dkgray = (32, 32, 32)
ltgray = (169, 169, 169)
white = (255, 255, 255)
red = (255, 0, 0)
orange = (255, 128, 0)
green = (0, 255, 0)
dkgreen = (1, 50, 32)
blue = (0, 0, 255)
purple = (78, 48, 132)

# Fons(s)
font = pygame.font.Font('res/alkhemikal.ttf', 28)

# Image(s)
heroico = pygame.image.load('res/maphero.png')



class Map:
	def __init__(self, height, width, offsetX, offsetY, tile_size, tile_margin, grid, deftsize, deftmarg):
		self.height = height
		self.width = width
		self.offsetX = offsetX
		self.offsetY = offsetY
		self.tile_size = tile_size
		self.tile_margin = tile_margin
		self.grid = grid
		self.deftsize = deftsize
		self.deftmarg = deftmarg
	
	
class Brush:
	def __init__(self, ID, name, color, isWall, *texture):
		self.ID = ID
		self.name = name
		self.color = color
		self.isWall = isWall
		self.texture = texture
		
	def swap_brush(self, swap):
		if swap == 0:
			self.ID = swap
			self.name = "Endless Void"
			self.color = (0, 0, 0) # Black
			self.isWall = 1
		elif swap == 1:
			self.ID = swap
			self.name = "Stone Floor"
			self.color = (169, 169, 169) # LtGray
			self.isWall = 0
		elif swap == 2:
			self.ID = swap
			self.name = "Stone Wall"
			self.color = (0, 255, 0) # Green... but why tho?
			self.isWall = 1
		elif swap == 3:
			self.ID = swap
			self.name = "Custom Block"
			self.color = (78, 48, 132) # Purple. For Magic.
			self.isWall = 0			
		elif swap == "player":
			self.ID = swap
			self.name = "Player"
		else:
			print("This brush not implemented.")
			return
			
		print("Brush changed to " + self.name)
		
		
class Player:
	def __init__(self, x, y, rotation, icon):
		self.x = x
		self.y = y
		self.rotation = rotation
		self.icon = icon
		
	def rotate(self):
		cardinal = (0, 90, 180, -90) # (0 = N), (90 = W), (180 = S), (-90 = E)
		for x in range(len(cardinal)):
			if player.rotation == cardinal[x]:
				x += 1
				if x >= len(cardinal):
					x -= len(cardinal)
				player.rotation = cardinal[x]
				print(player.rotation)
				return
		
map = Map(100, 100, 0, 0, 25, 1, {}, 25, 1)
player = Player(0, 0, 0, heroico)
brush = Brush(1, "Stone Floor", (169, 169, 169), 0)

# ID: 0, Desc: Endless Void, 
# ID: 1, Desc: Stone Floor
# ID: 2, Desc: Stone Wall
# ID: 3, Desc: Barrier
# ID: 4, Desc: Liquid

map.grid = [[{"ID":1, "name":"Stone Floor", "color":(169, 169, 169), "isVisible": 0, "isDiscovered":0, "isWall":0} for x in range(map.width)] for y in range(map.height)]

def save():
	print ("Saving...")
	offset = (129-((map.deftsize+map.deftmarg)*player.x), 643-((map.deftsize+map.deftmarg)*player.y))
	data = {'dungeon':map.grid, 
		'player':(player.x, player.y, player.rotation), 
		'offset':(offset[0], offset[1]),
		'viewport':(map.deftsize, map.deftmarg)}
	with open('save/dungeon3.sav', 'wb') as f:
		pickle.dump(data, f)
	print ("Dungeon Saved")
	
def load():
	print ("Loading...")
	with open('save/dungeon3.sav', 'rb') as f:
		data = pickle.load(f)
	map.grid = data['dungeon']
	player.x, player.y, player.rotation = data['player']
	map.offsetX, map.offsetY = data['offset']
	map.tile_size, map.tile_margin = data['viewport']
	print ("Dungeon Loaded")

def main():
	running = True
	while running:
		for event in pygame.event.get():			
			if event.type == pygame.QUIT:
				running = False
				
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				pos = pygame.mouse.get_pos()
				column = (pos[0]-map.offsetY) // (map.tile_size+map.tile_margin)
				row = (pos[1]-map.offsetX) // (map.tile_size+map.tile_margin)
				print("Left Click ", pos, "Grid coordinates: ", row, column)
				if row < 0 or column < 0 or row > map.width-1 or column > map.height-1:
					print("Invalid")
				if brush.ID == "player":
					if row == player.x and column == player.y:
						player.rotate()
					else:
						player.x, player.y = row, column
						print("Moved Player to " + str(row), str(column))
				else:
					print("changed " + str(row), str(column) + " from " + map.grid[row][column]['name'] + " to " + brush.name)
					map.grid[row][column]["ID"] = brush.ID
					map.grid[row][column]["name"] = brush.name
					map.grid[row][column]["color"] = brush.color
					map.grid[row][column]["isWall"] = brush.isWall
					
				
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
				pos = pygame.mouse.get_pos()
				column = (pos[0]-map.offsetY) // (map.tile_size+map.tile_margin)
				row = (pos[1]-map.offsetX) // (map.tile_size+map.tile_margin)
				print("Right Click ", pos, "Grid coordinates: ", row, column)
				#if row < 0 or column < 0 or row > map.width-1 or column > map.height-1:
				if row == player.x and column == player.y:
					tile_desc = "Player"
					print(tile_desc)
				else:
					tile_desc = map.grid[row][column]["name"]
					print(tile_desc)
					
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
				map.tile_size = min(map.tile_size + (map.tile_size//5), 75)
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
				map.tile_size = max(map.tile_size - (map.tile_size//5), 5)
					
			if event.type == pygame.KEYDOWN:
				multikey = pygame.key.get_pressed()
				if event.key == pygame.K_w:
					map.offsetX -= (map.tile_size + map.tile_margin)
				if event.key == pygame.K_s:
					map.offsetX += (map.tile_size + map.tile_margin)
				if event.key == pygame.K_a:
					map.offsetY -= (map.tile_size + map.tile_margin)
				if event.key == pygame.K_d:
					map.offsetY += (map.tile_size + map.tile_margin)
					
				if event.key == pygame.K_BACKQUOTE:
					brush.swap_brush("player")
				if event.key == pygame.K_1:
					brush.swap_brush(1)
				if event.key == pygame.K_2:
					brush.swap_brush(2)
				if event.key == pygame.K_3:
					brush.swap_brush(3)
				if event.key == pygame.K_4:
					brush.swap_brush(4)
				if event.key == pygame.K_5:
					brush.swap_brush(5)
				# ...
				if event.key == pygame.K_0:
					brush.swap_brush(0)
					
				if multikey[pygame.K_LCTRL] and multikey[pygame.K_z]:
					save()
				if multikey[pygame.K_LCTRL] and multikey[pygame.K_x]:
					load()
				
				
		gw.fill(black)
		for x in range(map.height):
			for y in range(map.width):					
				tile = pygame.Surface((map.tile_size, map.tile_size))
				tile.fill((map.grid[x][y].get("color")))
				# if map.grid[x][y].get("isVisible") == 0: # Not useful for Map Editor, but VERY YES in Game Engine.
					# tile.set_alpha(64)
				gw.blit(tile, ((map.tile_margin+map.tile_size)*y+map.tile_margin+map.offsetY, (map.tile_margin+map.tile_size)*x+map.tile_margin+map.offsetX))
				if x == player.x and y == player.y:
					playerico = pygame.transform.rotate(player.icon, player.rotation)
					playerico = pygame.transform.scale(playerico, (map.tile_size, map.tile_size))
					gw.blit(playerico, ((player.y*(map.tile_size+map.tile_margin))+map.offsetY+1, (player.x*(map.tile_size+map.tile_margin))+map.offsetX+1))

				#pygame.draw.rect(gw, map.grid[x][y].get("color"), ((map.tile_margin+map.tile_size)*y+map.tile_margin+map.offsetY, (map.tile_margin+map.tile_size)*x+map.tile_margin+map.offsetX, map.tile_size, map.tile_size), 0)
				
		clock.tick(30)
		pygame.display.update()
		

main()		

pygame.display.quit()		
pygame.quit()
print("Goodbye, thanks for using " + title + "!")
os._exit(1)