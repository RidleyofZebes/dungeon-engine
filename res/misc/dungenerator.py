import pygame
import random
import numpy
import pandas

pygame.init()

window_res = (1280, 720)

gw = pygame.display.set_mode(window_res)

# Colors
black = (0, 0, 0)  # Room Border [1]
dkgray = (32, 32, 32)  # Stone [2]
gray = (128, 128, 128)  # Room [1]
silver = (192, 192, 192)  # Hallway [1]
white = (255, 255, 255)
maroon = (128, 0, 0)
red = (255, 0, 0)
olive = (128, 128, 0)
orange = (255, 128, 0)
yellow = (255, 255, 0)  # Treasure Chests [1]
green = (0, 128, 0)
lime = (0, 255, 0)
teal = (0, 128, 128)
aqua = (0, 255, 255)
navy = (0, 0, 128)
blue = (0, 0, 255)  # Doors [3]
purple = (128, 0, 128)
fuchsia = (288, 0, 288)


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

        self.x = x  # * dungeon.tile_width
        self.y = y  # * dungeon.tile_height
        self.center = ((self.x1 + self.x2)//2, (self.y1 + self.y2)//2)

    def newroom(self):
        return self.x, self.y, self.w, self.h, self.center

    def check_intersection(self, room):
        return self.x1 <= room.x2 and self.x2 >= room.x1 and self.y1 <= room.y2 and room.y2 >= room.y1


def place_rooms(min_room_size, max_room_size, max_rooms):
    rooms = []
    corridors = []

    for r in range(0, max_rooms):
        w = min_room_size + random.randint(0,  max_room_size - min_room_size + 1)
        h = min_room_size + random.randint(0,  max_room_size - min_room_size + 1)
        x = random.randint(0, dungeon.width - w - 2) + 1
        y = random.randint(0, dungeon.height - h - 2) + 1

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
                    corridors = corridors + h_corridor(previous_center[0], new_center[0], previous_center[1])
                    corridors = corridors + v_corridor(previous_center[1], new_center[1], new_center[0])
                else:
                    corridors = corridors + v_corridor(previous_center[1], new_center[1], previous_center[0])
                    corridors = corridors + h_corridor(previous_center[0], new_center[0], new_center[1])

        if not failed:
            rooms.append(new_room)

    for room in rooms:
        pygame.draw.rect(dungeon_canvas, black, (room.x-1, room.y-1, room.w+2, room.h+2))
        pygame.draw.rect(dungeon_canvas, gray, (room.x, room.y, room.w, room.h))
        pygame.display.update()
    grid = pygame.surfarray.array3d(dungeon_canvas).tolist()
    for corridor in corridors:

        color = silver
        if tuple(grid[corridor[0]][corridor[1]]) == black:
            color = blue
        pygame.draw.rect(dungeon_canvas, color, (corridor[0], corridor[1], 1, 1))


def h_corridor(x1, x2, y):
    corridor_units = []
    for x in range(min(x1, x2), max(x1, x2)+1):
        pygame.draw.rect(dungeon_canvas, silver, (x, y, 1, 1))
        corridor_units.append([x, y])

    return corridor_units


def v_corridor(y1, y2, x):
    corridor_units = []
    for y in range(min(y1, y2), max(y1, y2)+1):
        pygame.draw.rect(dungeon_canvas, silver, (x, y, 1, 1))
        corridor_units.append([x, y])

    return corridor_units


def create_room(x, y, w, h):
    pygame.draw.rect(dungeon_canvas, gray, (x, y, w, h))
    pygame.display.update()


def generate_features(chest_qty, use_doors=True):
    grid = pygame.surfarray.array3d(dungeon_canvas).tolist()
    if use_doors:
        pass
        # for x in range(len(dungeon.grid)):
        #     for y in range(len(dungeon.grid)):
        #         if tuple(grid[x][y]) == black:
        #             doorcheck = [[grid[x - 1][y], grid[x + 1][y]],
        #                          [grid[x + 1][y], grid[x - 1][y]],
        #                          [grid[x][y + 1], grid[x][y - 1]],
        #                          [grid[x][y - 1], grid[x][y + 1]]]
        #             for check in doorcheck:
        #                 print(check)
        #                 if (tuple(check[0]), tuple(check[1])) == (silver, gray):
        #                     pygame.draw.rect(dungeon_canvas, blue, (x, y, 1, 1))
        #                     pygame.display.update()
    for chest in range(chest_qty):
        x, y = random.randint(0, dungeon.width - 1), random.randint(0, dungeon.height - 1)
        while tuple(grid[x][y]) != gray:
            x, y = random.randint(0, dungeon.width - 1), random.randint(0, dungeon.height - 1)
        pygame.draw.rect(dungeon_canvas, yellow, (x, y, 1, 1))
        pygame.display.update()

    # x, y = random.randint(0, dungeon.width - 1), random.randint(0, dungeon.height - 1)
    # while tuple(grid[x][y]) != gray:
    #     x, y = random.randint(0, dungeon.width - 1), random.randint(0, dungeon.height - 1)
    #     pygame.draw.rect(dungeon_canvas, red, (x, y, 1, 1))
    #     pygame.display.update()
    #
    # x, y = random.randint(0, dungeon.width - 1), random.randint(0, dungeon.height - 1)
    # while tuple(grid[x][y]) != gray:
    #     x, y = random.randint(0, dungeon.width - 1), random.randint(0, dungeon.height - 1)
    #     pygame.draw.rect(dungeon_canvas, green, (x, y, 1, 1))
    #     pygame.display.update()





def map_canvas():
    grid = pygame.surfarray.array3d(dungeon_canvas).tolist()
    for x in range(len(dungeon.grid)):
        for y in range(len(dungeon.grid)):
            if tuple(grid[x][y]) == gray:  # Floor(rooms)
                dungeon.grid[x][y] = 1
            if tuple(grid[x][y]) == silver:  # Floor(halls)
                dungeon.grid[x][y] = 1
            if tuple(grid[x][y]) == dkgray:  # Walls
                dungeon.grid[x][y] = 2
            if tuple(grid[x][y]) == black:  # Room Border
                dungeon.grid[x][y] = 2
            if tuple(grid[x][y]) == blue:  # Doors
                dungeon.grid[x][y] = 3
            if tuple(grid[x][y]) == yellow:  # Chests
                dungeon.grid[x][y] = 4
            # if tuple(grid[x][y]) == green:  # Stairs Up
            #     dungeon.grid[x][y] = 5
            # if tuple(grid[x][y]) == red:  # Stairs Down
            #     dungeon.grid[x][y] = 6
    return dungeon.grid


def get_map(min_room_size, max_room_size, max_rooms, chest_qty, use_doors=True):
    dungeon.generate()
    dungeon_canvas.fill(dkgray)
    place_rooms(min_room_size, max_room_size, max_rooms)
    generate_features(chest_qty, use_doors)
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
                generate_features(10)
                canvas = pygame.transform.scale(dungeon_canvas, (720, 720))
                canvas_rect = canvas.get_rect()
                canvas_rect.center = (window_res[0]//2, window_res[1]//2)
                gw.blit(canvas, canvas_rect)
                pygame.display.update()
                print(map_canvas())


if __name__ == '__main__':
    main()
