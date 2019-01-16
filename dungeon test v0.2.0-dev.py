"""-------------------------------------------------------------------------#
# "Dungeon Test"                                                             #
# By Douglas J. Honeycutt                                                   #
# https://withacact.us/ | https://github.com/RidleyofZebes/hero-simulator   #
#-------------------------------------------------------------------------"""


# Imports...
import os
# import sys
import pickle  # <-- The thing that lets the save/load function work. Favorite module name.
import re  # <-- RegEx stuffs module
import pygame
import math
# from res import pygame_textinput
# from random import randint  # <-- LulZ S000 RaNdUm
# from natural.number import ordinal  # <-- Makes the numbers look pretty - 1st, 2nd, 3rd, 4th...

pygame.init()
title = "dungeon test v0.2.0-dev"

window_res = (1280, 720)
FPS = 30

gw = pygame.display.set_mode(window_res)
#gw = pygame.display.set_mode(window_res, pygame.FULLSCREEN)
pygame.display.set_caption(title)

pygame.key.set_repeat(10, 50)

clock = pygame.time.Clock()

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

# Font(s)
font = pygame.font.Font('res/alkhemikal.ttf', 28)

# Image(s)
frame = pygame.image.load('res/window_wide.png').convert()
heroico = pygame.image.load('res/maphero.png')
titlecard = pygame.image.load('res/studio_logo.png').convert()
gamelogo = pygame.image.load('res/game_logo.png').convert()

# Test starts here
class GameState:
    def __init__(self):
        self.mapdisplay = 0
        self.INTRO_DISABLED = True
        self.titlecard = True
        self.mainmenu = False


class Map:
    def __init__(self):
        self.height = 100
        self.width = 100
        self.offsetX = 129
        self.offsetY = 643
        self.tile_size = 25
        self.tile_margin = 1
        self.grid = {}

    def reset(self):
        defaultxy = (486, 250)
        # print("Map Reset Disabled, use Map Editor.")
        print("Resetting Map...")
        player.x = 0
        player.y = 0
        self.offsetX = defaultxy[1]
        self.offsetY = defaultxy[0]
        self.grid = [
            [{"ID": 1,
              "name": "Floor",
              "color": (169, 169, 169),
              "isVisible": 0,
              "isDiscovered": 0,
              "isWall": 0}
             for x in range(self.width)]
            for y in range(self.height)]
        print("Map reset")


class Player:
    def __init__(self):
        self.name = "Nameless"
        self.x = 0
        self.y = 0
        self.viewrange = 8
        self.icon = heroico
        self.rotation = 0



        # self.killcount = 0
        # self.encounter = 0
        # self.gametime = 0
        # self.xp = 0
        # self.lvl = 1
        # self.gold = 0

    def move(self, direction):
        mts = map.tile_size + map.tile_margin
        move_dir = {0:   ['self.x -= 1', 'self.x += 1'],
                    180: ['self.x += 1', 'self.x -= 1'],
                    -90: ['self.y += 1', 'self.y -= 1'],
                    90:  ['self.y -= 1', 'self.y += 1']}
        next_sqr = {0:   ['[self.x - 1][self.y]', '[self.x + 1][self.y]'],
                    180: ['[self.x + 1][self.y]', '[self.x - 1][self.y]'],
                    -90: ['[self.x][self.y + 1]', '[self.x][self.y - 1]'],
                    90:  ['[self.x][self.y - 1]', '[self.x][self.y + 1]']}
        broken_thing = {0:   ['self.x - 1', 'self.x + 1'],
                        180: ['self.x + 1', 'self.x - 1'],
                        -90: ['self.y + 1', 'self.y - 1'],
                        90:  ['self.y - 1', 'self.y + 1']}
        map_move = {0:   ['map.offsetX += mts', 'map.offsetX -= mts'],
                    180: ['map.offsetX -= mts', 'map.offsetX += mts'],
                    -90: ['map.offsetY -= mts', 'map.offsetY += mts'],
                    90:  ['map.offsetY += mts', 'map.offsetY -= mts']}
        x = 0 if direction == "forward" else 1
        try:
            wall_check = eval("map.grid" + next_sqr[self.rotation][x])["isWall"]
            border_chk = eval(broken_thing[self.rotation][x])
        except IndexError:
            border_chk = -1  # This is a hack. I am ashamed of it, but it works. Too tired to fix it right now.
            # It's supposed to check if the next square is out of bounds. In this scenario, it throws an error and
            # acts like it were the top-right corner. It technically works anyway. Don't do this. It's not healthy.
        if border_chk < 0:
            print("Out of Area")
            print(border_chk)
        elif wall_check == 1:
            print("Blocked")
        else:
            exec(move_dir[self.rotation][x])
            exec(map_move[self.rotation][x])

    def strafe(self, direction):
        mts = map.tile_size + map.tile_margin
        move_dir = {0:   ['self.y += 1', 'self.y -= 1'],
                    180: ['self.y -= 1', 'self.y += 1'],
                    -90: ['self.x += 1', 'self.x -= 1'],
                    90:  ['self.x -= 1', 'self.x += 1']}
        next_sqr = {0:   ['[self.x][self.y + 1]', '[self.x][self.y - 1]'],
                    180: ['[self.x][self.y - 1]', '[self.x][self.y + 1]'],
                    -90: ['[self.x + 1][self.y]', '[self.x - 1][self.y]'],
                    90:  ['[self.x - 1][self.y]', '[self.x + 1][self.y]']}
        broken_thing = {0:   ['self.y + 1', 'self.y - 1'],
                        180: ['self.y - 1', 'self.y + 1'],
                        -90: ['self.x + 1', 'self.x - 1'],
                        90:  ['self.x - 1', 'self.x + 1']}
        map_move = {0:   ['map.offsetY -= mts', 'map.offsetY += mts'],
                    180: ['map.offsetY += mts', 'map.offsetY -= mts'],
                    -90: ['map.offsetX -= mts', 'map.offsetX += mts'],
                    90:  ['map.offsetX += mts', 'map.offsetX -= mts']}
        x = 0 if direction == "right" else 1
        try:
            wall_check = eval("map.grid" + next_sqr[self.rotation][x])["isWall"]
            border_chk = eval(broken_thing[self.rotation][x])
        except IndexError:
            border_chk = -1  # This is a hack. I am ashamed of it, but it works. Too tired to fix it right now.
            # It's supposed to check if the next square is out of bounds. In this scenario, it throws an error and
            # acts like it were the top-right corner. It technically works anyway. Don't do this. It's not healthy.
        if border_chk < 0:
            print("Out of Area")
            print(border_chk)
        elif wall_check == 1:
            print("Blocked")
        else:
            exec(move_dir[self.rotation][x])
            exec(map_move[self.rotation][x])

    def rotate(self, turn):
        cardinal = (0, -90, 180, 90)  # (0 = N), (90 = W), (180 = S), (-90 = E)
        for x in range(len(cardinal)):
            if self.rotation == cardinal[x]:
                x += turn
                if x >= len(cardinal):
                    x -= len(cardinal)
                self.rotation = cardinal[x]
                print("Rotated to " + str(cardinal[x]) + " degrees")
                return

    def examine(self):
        next_sqr = {0:   '[self.x - 1][self.y]',
                    180: '[self.x + 1][self.y]',
                    -90: '[self.x][self.y + 1]',
                    90:  '[self.x][self.y - 1]'}
        newmsg = eval("map.grid" + next_sqr[self.rotation])["name"]
        return newmsg



def message(text, *texloc, color=white):
    textbox = pygame.Surface((999, 168))
    defaultcolor = color
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = 999, 168
    if not texloc:
        pos = 10, 10
    else:
        pos = texloc
    x, y = pos
    for line in words:
        for word in line:
            color = defaultcolor
            # Searches for text wrapped in <!these characters:>, which is used here to change the color of the word.
            if re.search('<!(.*):>', word):
                colorcheck = re.search('<!(.*):>', word)  # Assigns the captured string to a variable.
                strip = re.sub(r'\W', "", colorcheck.group())  # Removes everything from the string except the word.
                # Removes the flag and keyword from the text for cleanup.
                word = re.sub(colorcheck.group(), "", word)
                # Re-renders and gets the new size of the word after the flag has been removed.
                word_surface = font.render(word, False, color)
                word_width, word_height = word_surface.get_size()
                color = eval(strip)
                if x + word_width >= max_width:
                    x = pos[0]
                    y += word_height
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            textbox.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.
    gw.blit(textbox, (10, 542))


def titlescreen():
    while gs.titlecard:
        pygame.time.wait(2000)
        fadein = True
        i = 0
        while fadein:
            gw.fill(black)
            titlecard.set_alpha(i)
            gw.blit(titlecard, (0, 0))
            pygame.display.update()
            i += 1
            if i >= 255:
                pygame.time.wait(2000)
                fadein = False
        while not fadein:
            gw.fill(black)
            titlecard.set_alpha(i)
            gw.blit(titlecard, (0, 0))
            pygame.display.update()
            i -= 1
            if i <= 1:
                fadein = True
                gs.titlecard = False


def mainmenu():
    gs.mainmenu = True
    while gs.mainmenu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        gw.fill(black)
        gw.blit(gamelogo, (0, 0))
        pygame.display.update()
    # TODO: Finish menu and add buttons.


def save():
    print("Saving...")
    data = {'dungeon': map.grid,
            'player': (player.x, player.y, player.rotation),
            'offset': (map.offsetX, map.offsetY),
            'viewport': (map.tile_size, map.tile_margin)
            }
    with open('save/dungeon3.sav', 'wb') as f:
        pickle.dump(data, f)
    print("Dungeon Saved")


def load():
    print("Loading...")
    with open('save/dungeon3.sav', 'rb') as f:
        data = pickle.load(f)
    map.grid = data['dungeon']
    player.x, player.y, player.rotation = data['player']
    map.offsetX, map.offsetY = data['offset']
    map.tile_size, map.tile_margin = data['viewport']
    print("Dungeon Loaded")

map = Map()
player = Player()
gs = GameState()

load()


def main():
    if not gs.INTRO_DISABLED:
        titlescreen()

        mainmenu()

    textbox = "Welcome, <!red:>%s! Your destiny awaits." % (player.name)

    RAYS = 360  # Should be 360!

    STEP = 3  # The step of for cycle. More = Faster, but large steps may
    # cause artifacts. Step 3 is great for radius 10.

    # Tables of precalculated values of sin(x / (180 / pi)) and cos(x / (180 / pi))
    sintable = []
    costable = []

    for x in range (0, 361):
        sincalc = math.sin(x/(180/math.pi))
        sintable.append(sincalc)
        coscalc = math.cos(x/(180/math.pi))
        costable.append(coscalc)

    tile_desc = ""  # Also an environment variable... better put it in the class, too.

    running = True
    while running:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
            # Grid Click Events #####
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                if pos[0] > 10 and pos[1] > 10 and pos[0] < 1009 and pos[
                    1] < 537:  # Only take action for clicks within the minimap
                    column = (pos[0] - map.offsetY - 10) // (map.tile_size + map.tile_margin)
                    row = (pos[1] - map.offsetX - 10) // (map.tile_size + map.tile_margin)
                    print("Left Click ", pos, "Grid coordinates: ", row, column)
                    if row < 0 or column < 0 or row > map.width - 1 or column > map.height - 1:
                        print("Invalid")
                    elif row == player.x and column == player.y:
                        print("Player")
                    elif map.grid[row][column] == 1:
                        map.grid[row][column] = 2
                        print("Selected")
                    elif map.grid[row][column] == 2:
                        map.grid[row][column] = 1
                        print("Deselected")
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                pos = pygame.mouse.get_pos()
                if pos[0] > 10 and pos[1] > 10 and pos[0] < 1009 and pos[
                    1] < 537:  # Only take action for clicks within the minimap
                    column = (pos[0] - map.offsetY - 10) // (map.tile_size + map.tile_margin)
                    row = (pos[1] - map.offsetX - 10) // (map.tile_size + map.tile_margin)
                    print("Right Click ", pos, "Grid coordinates: ", row, column)
                    if row == player.x and column == player.y:
                        textbox = "You see a tall, good looking... Wait a minute, that's <!blue:>you."
                        print(tile_desc)
                    else:
                        tile_desc = map.grid[row][column]["name"]
                        textbox = tile_desc
                        print(tile_desc)

            # Player Movement #####
            if event.type == pygame.KEYDOWN:
                multikey = pygame.key.get_pressed()
                if event.key == pygame.K_w:
                    print("Move Forward")
                    player.move("forward")
                    print("Moved to", player.x, player.y)
                if event.key == pygame.K_s:
                    print("Move Back")
                    player.move("backward")
                    print("Moved to", player.x, player.y)
                if multikey[pygame.K_LSHIFT] and multikey[pygame.K_a]:
                    print("Strafe Left")
                    player.strafe("left")
                    print("Moved to", player.x, player.y)
                elif event.key == pygame.K_a:
                    print("Turn Right")
                    player.rotate(-1)
                if multikey[pygame.K_LSHIFT] and multikey[pygame.K_d]:
                    print("Strafe Right")
                    player.strafe("right")
                    print("Moved to", player.x, player.y)
                elif event.key == pygame.K_d:
                    print("Turn Left")
                    player.rotate(1)
                if event.key == pygame.K_e:
                    # print("Examine/Interact not yet implemented, but reserved.")
                    print("Testing Examine")
                    try:
                        textbox = player.examine()
                    except IndexError:
                        print("Nope.")
                if event.key == pygame.K_ESCAPE:
                    print("Shutting down...")
                    running = False

                # Multikey Commands #####
                if multikey[pygame.K_LCTRL] and multikey[pygame.K_z]:
                    save()
                if multikey[pygame.K_LCTRL] and multikey[pygame.K_x]:
                    load()
                if multikey[pygame.K_LCTRL] and multikey[pygame.K_r]:
                    map.reset()

                if multikey[pygame.K_LCTRL] and multikey[pygame.K_m]:
                    print("Switching Maps...")
                    if gs.mapdisplay == 0:
                        gs.mapdisplay = 1
                    elif gs.mapdisplay == 1:
                        gs.mapdisplay = 0
                    print("Switched to Display " + str(gs.mapdisplay))

        """ Begin drawing the game screen """

        gw.fill(dkgray)

        if gs.mapdisplay == 0:

            # Create the 4 main surfaces: viewscreen, minimap, textbox, and menu

            viewscreen = pygame.Surface((999, 527))
            minimap = pygame.Surface((256, 256))

            statmenu = pygame.Surface((257, 439))

            """ Draw the map """

            # Reset visible squares...
            for x in range(map.height):
                for y in range(map.width):
                    if map.grid[x][y]["isVisible"] == 1:
                        map.grid[x][y]["isVisible"] = 0
            # Determine which squares are visible...
            for i in range(0, RAYS + 1, STEP):
                ax = sintable[i]  # Get precalculated value sin(x / (180 / pi))
                ay = costable[i]  # cos(x / (180 / pi))
                x = player.x  # Player's x
                y = player.y  # Player's y
                for z in range(player.viewrange):  # Cast the ray
                    x += ax
                    y += ay
                    if x < 0 or y < 0 or x > map.width or y > map.height:  # If ray is out of range
                        break
                    try:
                        map.grid[int(round(x))][int(round(y))].update({"isDiscovered": 1, "isVisible": 1})  # Discover the tile and make it visible
                    except IndexError:
                        break
                    if map.grid[int(round(x))][int(round(y))]["isWall"] == 1:  # Stop ray if it hit
                        break
            map.grid[player.x][player.y].update({"isDiscovered": 1, "isVisible": 1})
            for x in range(map.height):
                for y in range(map.width):
                    tile = pygame.Surface((map.tile_size, map.tile_size))
                    tile.fill((map.grid[x][y].get("color")))
                    if map.grid[x][y].get("isVisible") == 0 and map.grid[x][y].get(
                            "isDiscovered") == 1:  # Not useful for Map Editor, but VERY YES in Game Engine.
                        tile.set_alpha(64)
                    if map.grid[x][y].get("isVisible") == 0 and map.grid[x][y].get("isDiscovered") == 0:
                        tile.fill(black)
                    viewscreen.blit(tile, ((map.tile_margin + map.tile_size) * y + map.tile_margin + map.offsetY,
                                           (map.tile_margin + map.tile_size) * x + map.tile_margin + map.offsetX))
                    # if x == player.x and y == player.y:
                    #     playerico = pygame.transform.rotate(player.icon, player.rotation)
                    #     playerico = pygame.transform.scale(playerico, (map.tile_size, map.tile_size))
                    #     viewscreen.blit(playerico, ((player.y * (map.tile_size + map.tile_margin)) + map.offsetY + 1,
                    #                                 (player.x * (map.tile_size + map.tile_margin)) + map.offsetX + 1))
            """ Draw the Minimap """
            for x in range(map.height):
                for y in range(map.width):
                    tile = pygame.Surface((1, 1))
                    tile.fill((map.grid[x][y].get("color")))
                    # Not useful for Map Editor, but VERY YES in Game Engine.
                    if map.grid[x][y].get("isVisible") == 0 and map.grid[x][y].get( "isDiscovered") == 1:
                        tile.set_alpha(64)
                    if map.grid[x][y].get("isVisible") == 0 and map.grid[x][y].get("isDiscovered") == 0:
                        tile.fill(black)
                    minimap.blit(tile, ((y + map.offsetY/(map.tile_size+map.tile_margin)) + 110,
                                        (x + map.offsetX/(map.tile_size+map.tile_margin)) + 119))

            """ Draw the Player Icon """
            maparrow = pygame.transform.rotate(player.icon, player.rotation)
            viewscreen.blit(maparrow, ((player.y * (map.tile_size + map.tile_margin)) + map.offsetY + 1,
                                       (player.x * (map.tile_size + map.tile_margin)) + map.offsetX + 1))

            """ Tile Descriptions? """
            tiledescrect = font.render(tile_desc, False, black)
            descrect = tiledescrect.get_rect()
            descrect.center = (658, 300)
            # gw.blit(tiledescrect, descrect)

            message(textbox)

            # Create the 4 main surfaces: viewscreen, minimap, textbox, and menu

            gw.blit(viewscreen, (10, 10))
            gw.blit(minimap, (1014, 10))

            gw.blit(statmenu, (1014, 271))

        """ Second display view """
        # Needs work, supposed to display map scalable and scrollable. For now just barely managable (somehow).
        if gs.mapdisplay == 1:  # Supposed to be the map screen. Needs massive alterations.
            for x in range(map.height):
                for y in range(map.width):
                    if map.grid[x][y]["isVisible"] == 0:
                        color = black
                    elif map.grid[x][y]["floor"] == 1:
                        color = ltgray
                    elif map.grid[x][y]["isWall"] == 1:
                        color = green
                    if map.grid[x][y]["isVisible"] == 0 and map.grid[x][y]["isDiscovered"] == 1:
                        if map.grid[x][y]["floor"] == 1:
                            color = dkgray
                        elif map.grid[x][y]["isWall"] == 1:
                            color = dkgreen
                    if x == player.x and y == player.y:
                        color = red
                    pygame.draw.rect(gw, color, ((1 + 5) * y + 1, (1 + 5) * x + 1, 5, 5), 0)

        clock.tick(FPS)

        pygame.display.update()


if __name__ == '__main__':
    main()

pygame.display.quit()
pygame.quit()
print("Goodbye, thanks for playing!")
os._exit(1)
