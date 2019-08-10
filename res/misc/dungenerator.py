import pygame
import random
import numpy
import pandas

pygame.init()

window_res = (1280, 720)

gw = pygame.display.set_mode(window_res)

# Colors
black = (0, 0, 0)
dkgray = (32, 32, 32)
ltgray = (169, 169, 169)
white = (255, 255, 255)
red = (255, 0, 0)
orange = (255, 128, 0)
yellow = (255, 255, 0)
green = (0, 255, 0)
dkgreen = (1, 50, 32)
blue = (0, 0, 255)
purple = (78, 48, 132)

class GridMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tile_width = 25
        self.tile_height = 25
        self.tile_margin = 1
        self.grid = []

    def generate(self):
        self.grid = [[1 for x in range(self.width)] for y in range(self.height)]


class Room:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.x2 = x + w
        self.y1 = y
        self.y2 = y + h

        self.w = w
        self.h = h

        self.x = x # * dungeon.tile_width
        self.y = y # * dungeon.tile_height
        self.center = ((self.x1 + self.x2)//2, (self.y1 + self.y2)//2)

    def newroom(self):
        return self.x, self.y, self.w, self.h, self.center

    def check_intersection(self, room):
        return self.x1 <= room.x2 and self.x2 >= room.x1 and self.y1 <= room.y2 and room.y2 >= room.y1


def place_rooms(min_room_size, max_room_size, max_rooms):
    rooms = []

    for r in range(0, max_rooms):
        w = min_room_size + random.randint(0,  max_room_size - min_room_size + 1)
        h = min_room_size + random.randint(0,  max_room_size - min_room_size + 1)
        x = random.randint(0, dungeon.width - w - 1) + 1
        y = random.randint(0, dungeon.height - h - 1) + 1

        new_room = Room(x, y, w, h)

        failed = False
        for other_room in rooms:
            if new_room.check_intersection(other_room):
                if random.randint(0, 5) > 0:
                    failed = True
                    break
        if not failed:
            room_xy = (new_room.newroom())
            create_room(room_xy[0], room_xy[1], room_xy[2], room_xy[3])

            new_center = new_room.center

            if len(rooms) != 0:
                previous_center = rooms[len(rooms)-1].center

                if random.randint(0, 1) == 0:
                    h_corridor(previous_center[0], new_center[0], previous_center[1])
                    v_corridor(previous_center[1], new_center[1], new_center[0])
                else:
                    v_corridor(previous_center[1], new_center[1], previous_center[0])
                    h_corridor(previous_center[0], new_center[0], new_center[1])

        if not failed:
            rooms.append(new_room)

def h_corridor(x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2)+1):
        pygame.draw.rect(dungeon_canvas, ltgray, (x, y, 1, 1))

def v_corridor(y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2)+1):
        pygame.draw.rect(dungeon_canvas, ltgray, (x, y, 1, 1))

def create_room(x, y, w, h):
    pygame.draw.rect(dungeon_canvas, ltgray, (x, y, w, h))
    pygame.display.update()

def map_canvas():
    grid = pygame.surfarray.array3d(dungeon_canvas).tolist()
    for x in range(len(dungeon.grid)):
        for y in range(len(dungeon.grid)):
            if tuple(grid[x][y]) == dkgray:
                dungeon.grid[x][y] = 2
            if tuple(grid[x][y]) == ltgray:
                dungeon.grid[x][y] = 1

    return dungeon.grid

def get_map(min_room_size, max_room_size, max_rooms):
    dungeon.generate()
    dungeon_canvas.fill(dkgray)
    place_rooms(min_room_size, max_room_size, max_rooms)
    new_map = map_canvas()
    
    return new_map

dungeon = GridMap(100, 100)
dungeon_canvas = pygame.Surface((dungeon.width, dungeon.height))

def main():
    dungeon.generate()
    running = True
    while running:
        for event in pygame.event.get():
            if event == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:

                dungeon_canvas.fill(dkgray)
                place_rooms(8, 20, 15)
                canvas = pygame.transform.scale(dungeon_canvas, (720, 720))
                canvas_rect = canvas.get_rect()
                canvas_rect.center = (window_res[0]//2, window_res[1]//2)
                gw.blit(canvas, canvas_rect)
                pygame.display.update()
                print(map_canvas())


if __name__ == '__main__':
    main()
