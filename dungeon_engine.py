"""-------------------------------------------------------------------------#
# "Dungeon Engine"                                                          #
# By Douglas J. Honeycutt                                                   #
# https://withacact.us/ | https://github.com/RidleyofZebes/dungeon-engine   #
#-------------------------------------------------------------------------"""


# Imports...
import os
import pickle  # <-- The thing that lets the save/load function work. Favorite module name.
import re
import pygame
import math
import random
import itertools
import json
import inflect
from res.misc import astar  # <-- Tried to use it, but it broke easily.

# import pprint
# import sys
# from res import pygame_textinput  # <-- For entering player name
# from natural.number import ordinal  # <-- Makes the numbers look pretty - 1st, 2nd, 3rd, 4th...

p = inflect.engine()

pygame.init()
title = "dungeon engine v0.2.2-dev"

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
font = pygame.font.Font('res/fonts/Alkhemikal.ttf', 28)
stats_font = pygame.font.Font('res/fonts/Poco.ttf', 20)
tiny_font = pygame.font.Font('res/fonts/Poco.ttf', 10)

# Image(s)
heroico = pygame.image.load('res/images/maphero.png')
mobico = pygame.image.load('res/images/mapenemy.png')
titlecard = pygame.image.load('res/images/studio_logo.png').convert()
gamelogo = pygame.image.load('res/images/game_logo2.png').convert()

# .JSON(s)
monstersfile = 'res/json/monsters.json'
itemsfile = 'res/json/items.json'
tilesfile = 'res/json/tiles.json'


# Test starts here
class GameState:
    def __init__(self):
        self.running = True
        self.mapdisplay = 0
        self.INTRO_DISABLED = False
        self.DISPLAY_VERSION = True
        self.titlecard = True
        self.mainmenu = False
        self.newgame = False
        self.mapedit = False


class Entities:
    def __init__(self):
        self.mobs = []
        self.items = []
        self.entityID = 0

    def showentities(self):
        itemlist = [(item.name + " ID:" + item.ID) for item in self.items]
        moblist = [(mob.name + " ID:" + mob.ID) for mob in self.mobs]
        print("Mobs:\n" + str(moblist) + "\n"
              "Items:\n" + str(itemlist) + "\n"
              "Next entity ID: " + str(self.entityID))


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


# TODO: Camera Class keeps track of camera position and zoom.
""" 
class Camera:
    def __init__(self):
        self.positionY = 486
        self.positionX = 250
"""


# TODO: Tile class stores data for tile IDs instead of per-tile data.
"""
class Tile:
    def __init__(self):
        self.ID = swap
        self.name = "Endless Void"
        self.color = (0, 0, 0)  # Black
        self.descript = " 
        self.isWall = 2
"""


class Brush:
    def __init__(self):
        self.ID = 0
        self.name = "Endless Void"
        self.color = (0, 0, 0)  # Black
        self.isWall = 0
        self.texture = ""

    """
    isWall: 0 = not a wall
    isWall: 1 = a wall
    isWall: 2 = transparent (i.e. window)
    """

    def swap_brush(self, swap):
        if swap == 0:
            self.ID = swap
            self.name = "Endless Void"
            self.color = (0, 0, 0)  # Black
            self.isWall = 2
        elif swap == 1:
            self.ID = swap
            self.name = "Stone Floor"
            self.color = (169, 169, 169)  # LtGray
            self.isWall = 0
        elif swap == 2:
            self.ID = swap
            self.name = "Stone Wall"
            self.color = (0, 255, 0)  # Green... but why tho?
            self.isWall = 1
        elif swap == 3:
            self.ID = swap
            self.name = "Custom Block"
            self.color = (78, 48, 132)  # Purple. For Magic.
            self.isWall = 0
        elif swap == "player":
            self.ID = swap
            self.name = "Player"
        else:
            print("This brush not implemented.")
            return

        print("Brush changed to " + self.name)


class Entity:
    def move(self, direction):
        mts = map.tile_size + map.tile_margin
        blocked = False
        move_dir = {0:   [-1, 0],
                    180: [1, 0],
                    -90: [0, 1],
                    90:  [0, -1]}
        try:
            next_x = self.x + move_dir[self.rotation][0]
            next_y = self.y + move_dir[self.rotation][1]
            next_square = map.grid[next_x][next_y]
            wall_check = next_square["isWall"]
            for enemy in entities.mobs:
                if (enemy.x, enemy.y) == (next_x, next_y):
                    blocked = True
                    block_type = enemy.name
            if wall_check > 0:
                blocked = True
                block_type = next_square["name"]
            border_chk = 1
        except IndexError:
            border_chk = -1
        if border_chk < 0 or next_x < 0 or next_y < 0:  # FIXME: Player can back out of area.
            print("Out of Area")
            blockmsg = "You dare not tread into the <!green:>Fathomless <!green:>Void."
        elif blocked == True:
            print("Blocked")
            blockmsg = "There's %s in the way." % p.a(block_type)
        else:
            blockmsg = ""
            if direction == "forward":
                self.x += move_dir[self.rotation][0]
                self.y += move_dir[self.rotation][1]
                if isinstance(self, Player):
                    map.offsetX -= move_dir[self.rotation][0]*mts
                    map.offsetY -= move_dir[self.rotation][1]*mts
            if direction == "backward":
                self.x -= move_dir[self.rotation][0]
                self.y -= move_dir[self.rotation][1]
                if isinstance(self, Player):
                    map.offsetX += move_dir[self.rotation][0]*mts
                    map.offsetY += move_dir[self.rotation][1]*mts
        return blockmsg

    def strafe(self, direction):
        if direction == "right":
            self.rotate(1)
            self.move("forward")
            self.rotate(-1)
        if direction == "left":
            self.rotate(-1)
            self.move("forward")
            self.rotate(1)

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


class Player(Entity):
    def __init__(self):
        """ [Game Data] """
        self.x = 0
        self.y = 0
        self.viewrange = 8
        self.icon = heroico
        self.rotation = 0
        """ [Player Data] """
        self.name = "Thorgath of Udd"
        self.race = "Half-Orc"
        self.job = "Fighter"
        self.stat = {"str": 12, "dex": 10, "con": 15, "wis": 8, "cha": 11, "lck": 10}
        self.max_hp = (self.stat['con'] * 8)
        self.xp = 0
        self.lvl = 1
        self.hp = self.max_hp
        self.default_weapon = Item(None, "Fist", "", "weapon", True, 0, [0, 2])
        self.weapon = self.default_weapon
        self.armor = []
        self.inventory = []
        self.gold = 0
        self.max_carry_weight = (self.stat['con'] + self.stat['str']) * 10
        # self.killcount = 0
        # self.encounter = 0
        # self.gametime = 0
        # self.xp = 0
        # self.lvl = 1
        # self.gold = 0

    def examine(self):
        move_dir = {0:   [-1, 0],
                    180: [1, 0],
                    -90: [0, 1],
                    90:  [0, -1]}
        next_x = self.x + move_dir[self.rotation][0]
        next_y = self.y + move_dir[self.rotation][1]
        mob = next((mob for mob in entities.mobs if (next_x, next_y) == (mob.x, mob.y)), 0)
        if mob == 0:
            newmsg = map.grid[next_x][next_y]["name"]
        else:
            mob = next(mob for mob in entities.mobs if (next_x, next_y) == (mob.x, mob.y))
            self.attack(mob.ID)
            newmsg = ""
        return newmsg

    def additem(self, selection, qty=1):
        for x in range(0, qty):
            token = createitem(selection)
            self.pickupitem(token)

    def pickupitem(self, selection, qty=1):
        newitem = next((item for item in entities.items if item.ID == selection), None)
        if newitem:
            itemname = p.plural(newitem.name, qty)
            self.inventory.append(newitem)
            print("You pick up %d %s" % (qty, itemname))
        else:
            print("There's nothing there.")

    def dropitem(self, selection, qty=1):
        olditem = next((item for item in entities.items if item.ID == selection), None)
        if olditem:
            itemname = p.plural(olditem.name, qty)
            self.inventory.remove(olditem)
            print("You drop %d %s" % (qty, itemname))
        else:
            print("You can't drop that.")

    def showinventory(self):
        currentweight = 0
        inventory = []
        print("Current inventory:")
        for thing in self.inventory:
            currentweight += thing.weight
            qty = sum(item.name == thing.name for item in self.inventory)
            inventory.append("%s x%d %dea. %dlbs" % (thing.name, qty, thing.weight, thing.weight * qty))
        inventory = list(dict.fromkeys(inventory))
        print(*inventory, sep='\n')
        print("Weighing %dlbs of maximum %dlbs" % (currentweight, self.max_carry_weight))
        if currentweight > self.max_carry_weight:
            print("You are encumbered")

    def equip(self, equip_item):
        for thing in self.inventory:
            if thing.ID == equip_item or thing.name == equip_item and thing.isEquipable:
                self.weapon = thing
                print("You equip the %s" % self.weapon.name)
                break
            else:
                print("You can't equip a %s!" % thing.name)

    def unequip(self, equipment):
        if equipment == self.weapon:
            print("You put away your %s." % self.weapon.name)
            self.weapon = self.default_weapon
        else:
            print("You currently don't have %s equipped." % equipment.name)

    def attack(self, target):
        target = next((mob for mob in entities.mobs if mob.ID == target), None)
        print("Attacking %s with %s" % (target.name, self.weapon.name))
        atkdamage = random.randint(self.weapon.damage[0], self.weapon.damage[1])
        target.hp -= atkdamage
        print("You deal %d damage to the %s leaving it with %d health." % (atkdamage, target.name, target.hp))
        if not target.isHostile:
            x = random.randint(0, 1)
            if x == 0:
                target.isHostile = True
                print("The %s becomes aggressive towards you!" % target.name)
            if x == 1:
                print("The %s looks at you uncertainly." % target.name)
        if target.hp >= 0 and target.isHostile:
            target.attack(self)
        if target.hp <= 0:
            print("The %s is dead." % target.name)


class Monster(Entity):
    def __init__(self, ID, name, examine, hp, weapon, damage, viewrange, isHostile, x, y):
        self.ID = ID
        self.icon = mobico
        self.rotation = 0
        self.name = name
        self.examine = examine
        self.hp = hp
        self.isHostile = isHostile
        self.weapon = weapon
        self.damage = damage
        self.x = x
        self.y = y
        self.viewrange = viewrange

    def attack(self, target):
        print("The %s attacks %s with its %s" % (self.name, target.name, self.weapon))
        atkdamage = random.randint(self.damage[0], self.damage[1])
        target.hp -= atkdamage
        print("The %s deals %d damage to %s leaving them with %d health." %
              (self.name, atkdamage, target.name, target.hp))


class Item:
    def __init__(self, ID, name, examine, slot, isEquipable, weight, damage):
        self.ID = ID
        self.name = name
        self.examine = examine
        self.slot = slot
        self.isEquipable = isEquipable
        self.weight = weight
        self.damage = damage


def createmonster(monster, qty=1):
    with open(monstersfile, 'r') as data:
        monsters = json.load(data)
    if monster == 'random':
        monster = random.choice(list(monsters.keys()))
    for x in range(0, qty):
        spawn_xy = (random.randint(0, map.width-1), random.randint(0, map.height-1))
        token = str(entities.entityID)
        if monster in monsters:
            entities.mobs.append(Monster(token,
                                         monsters[monster]['name'],
                                         monsters[monster]['examine'],
                                         monsters[monster]['hp'],
                                         monsters[monster]['weapon'],
                                         monsters[monster]['damage'],
                                         monsters[monster]['viewrange'],
                                         False,
                                         spawn_xy[0],
                                         spawn_xy[1]))
            print("Created %s" % monster)
            entities.entityID += 1

        else:
            print("%s is unavailable." % monster)
    return token


def createitem(itemname):
    with open(itemsfile, 'r') as data:
        items = json.load(data)
    token = str(entities.entityID)
    if itemname in items:
        entities.items.append(Item(token,
                                   items[itemname]['name'],
                                   items[itemname]['examine'],
                                   items[itemname]['slot'],
                                   items[itemname]['isEquipable'],
                                   items[itemname]['weight'],
                                   items[itemname]['damage']))
        print("Created %s" % itemname)
        entities.entityID += 1
        return token
    else:
        print("%s is unavailable." % itemname)


# def createtile(tile_id):
#     with open(tilesfile, 'r') as data:
#         tiles = json.load(data)
#     location = (x, y)
#     map.tiles.append(Tile(location,
#                           items[itemname]['name'],
#                           items[itemname]['slot'],
#                           items[itemname]['isEquipable'],
#                           items[itemname]['weight'],
#                           items[itemname]['damage']))

def message(text, *texloc, color=white):  # FIXME Word highlighting syntax is weird. Needs re-written.
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


# TODO: Rewrite button code.
def button(button_pos, button_text, *button_width):  # Gets button X,Y and button label
        button_padding = 25  # Set padding between button text and border
        label = font.render(button_text, 0, white)  # Renders button label
        button_sizex, button_sizey = label.get_size()  # Sends button label dimensions to A,B variables
        if not button_width:
            # Outputs the button with default padding to the screen
            gw.blit(label, ((button_pos[0] + (button_padding / 2)), (button_pos[1] + (button_padding / 2))))
            button_size = (button_pos[0], button_pos[1],
                           (button_sizex + button_padding),
                           (button_sizey + (button_padding * 0.8)))
        else:
            # Outputs the button with padding and centered text to the screen
            gw.blit(label, (((button_pos[0] + ((button_width[0] + button_padding) / 2)) - (button_sizex / 2)),
                            (button_pos[1] + (button_padding / 2))))
            button_size = (button_pos[0], button_pos[1], (button_width[0] + button_padding),
                           (button_sizey + (button_padding * 0.8)))
        pygame.draw.rect(gw, white, button_size, 4)
        return pygame.Rect(button_size)


def titlescreen():
    while gs.titlecard:
        pygame.time.wait(1000)

        tx = 1280  # 575, 850
        ratio = int(1280 / tx)
        ty = 720 * ratio

        for i in range(0, 255, 5):
            gw.fill(black)

            titlecardzoom = pygame.transform.smoothscale(titlecard, (tx, ty))
            titlecardzoomrect = titlecardzoom.get_rect()
            titlecardzoomrect.center = (window_res[0] / 2, window_res[1] / 2)
            titlecardzoom.set_alpha(i)
            tx += 1
            ty += 1*ratio
            gw.blit(titlecardzoom, titlecardzoomrect)
            pygame.display.update()

        for i in range(0, 50):
            gw.fill(black)

            titlecardzoom = pygame.transform.smoothscale(titlecard, (tx, ty))
            titlecardzoomrect = titlecardzoom.get_rect()
            titlecardzoomrect.center = (window_res[0] / 2, window_res[1] / 2)
            tx += 1
            ty += 1*ratio
            gw.blit(titlecardzoom, titlecardzoomrect)
            pygame.display.update()

        for i in reversed(range(0, 255, 5)):
            gw.fill(black)

            titlecardzoom = pygame.transform.smoothscale(titlecard, (tx, ty))
            titlecardzoomrect = titlecardzoom.get_rect()
            titlecardzoomrect.center = (window_res[0] / 2, window_res[1] / 2)
            titlecardzoom.set_alpha(i)
            tx += 1
            ty += 1*ratio
            gw.blit(titlecardzoom, titlecardzoomrect)
            pygame.display.update()

        pygame.time.wait(500)
        gs.titlecard = False


def mainmenu():
    gs.mainmenu = True
    while gs.mainmenu:
        for menu_event in pygame.event.get():
            if menu_event.type == pygame.QUIT:
                gs.running = False
                gs.mainmenu = False

            gw.fill(black)

            logorect = gamelogo.get_rect()
            gw.blit(gamelogo, ((window_res[0]/2)-(logorect.width/2), 40))

            version = stats_font.render(title, 0, red)
            version_rect = version.get_rect()
            gw.blit(version, (5, (window_res[1]-version_rect.height)))

            start = button(((window_res[0]/2-150), window_res[1]/2 - 100), "Venture Forth!", 300)
            loadgame = button(((window_res[0]/2-150), window_res[1]/2 - 30), "Continue your Adventure", 300)
            editor = button(((window_res[0]/2-150), window_res[1]/2 + 40), "Map Editor", 300)
            settings = button(((window_res[0] / 2 - 150), window_res[1] / 2 + 110), "Settings", 300)
            credit = button(((window_res[0] / 2 - 75), window_res[1] / 2 + 300), "Credits", 150)

            if menu_event.type == pygame.MOUSEBUTTONDOWN and menu_event.button == 1:
                pos = pygame.mouse.get_pos()
                if start.collidepoint(pos):
                    gs.newgame = True
                    gs.mainmenu = False
                if loadgame.collidepoint(pos):
                    gs.mainmenu = False
                if editor.collidepoint(pos):
                    pass  # FIXME Do we really need a separate map editor?
                if settings.collidepoint(pos):
                    pass  # TODO Make settings menu
                if credit.collidepoint(pos):
                    pass  # TODO make credits screen

            pygame.display.update()

def newgame():
    print("This is where I'd put my character creation screen... if I had one.")
    pass
    # TODO Character creation screen with statgentest.py

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
    try:
        with open('save/dungeon3.sav', 'rb') as f:
            data = pickle.load(f)
        map.grid = data['dungeon']
        player.x, player.y, player.rotation = data['player']
        map.offsetX, map.offsetY = data['offset']
        map.tile_size, map.tile_margin = data['viewport']
        print("Dungeon Loaded")
    except Exception:
        print("No file to load, generating new dungeon...")
        map.reset()

map = Map()
player = Player()
gs = GameState()
brush = Brush()
entities = Entities()

load()


def main():
    if not gs.INTRO_DISABLED:
        titlescreen()

    mainmenu()

    if gs.newgame:
        map.reset()
        newgame()

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

    # FIXME: This variable seems redundant, see about incorporating it into a new 'tile' CLASS.
    tile_desc = ""  # Also an environment variable... better put it in the class, too.

    while gs.running:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                gs.running = False

            # Map Editor Events #####
            if gs.mapedit:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    # Only take action for clicks within the map
                    if pos[0] > 10 and pos[1] > 10 and pos[0] < 1009 and pos[1] < 537:
                        column = (pos[0] - map.offsetY - 10) // (map.tile_size + map.tile_margin)
                        row = (pos[1] - map.offsetX - 10) // (map.tile_size + map.tile_margin)
                        print("Left Click ", pos, "Grid coordinates: ", row, column)
                        # if click is outside the map:
                        if row < 0 or column < 0 or row > map.width - 1 or column > map.height - 1:
                            print("Invalid")
                        if brush.ID == "player":
                            if row == player.x and column == player.y:
                                player.rotate(1)
                            else:
                                player.x, player.y = row, column
                                print("Moved Player to " + str(row), str(column))
                        else:
                            print("changed " + str(row),
                                  str(column) + " from " + map.grid[row][column]['name'] + " to " + brush.name)
                            map.grid[row][column]["ID"] = brush.ID
                            map.grid[row][column]["name"] = brush.name
                            map.grid[row][column]["color"] = brush.color
                            map.grid[row][column]["isWall"] = brush.isWall

                # Map Editor Commands #####
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        brush.swap_brush(1)
                        textbox = "Brush changed to %s" % (brush.name,)
                    if event.key == pygame.K_2:
                        brush.swap_brush(2)
                        textbox = "Brush changed to %s" % (brush.name,)
                    if event.key == pygame.K_3:
                        brush.swap_brush(3)
                        textbox = "Brush changed to %s" % (brush.name,)
                    if event.key == pygame.K_4:
                        brush.swap_brush(4)
                        textbox = "Brush changed to %s" % (brush.name,)
                    if event.key == pygame.K_5:
                        brush.swap_brush(5)
                        textbox = "Brush changed to %s" % (brush.name,)
                    # ...
                    if event.key == pygame.K_0:
                        brush.swap_brush(0)
                        textbox = "Brush changed to %s" % (brush.name,)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    pos = pygame.mouse.get_pos()
                    column = (pos[0] - map.offsetY) // (map.tile_size + map.tile_margin)
                    row = (pos[1] - map.offsetX) // (map.tile_size + map.tile_margin)
                    print("Right Click ", pos, "Grid coordinates: ", row, column)
                    if row == player.x and column == player.y:
                        tile_desc = "Player"
                        print(tile_desc)
                    else:
                        tile_desc = map.grid[row][column]["name"]
                        print(tile_desc)

                # FIXME Mousewheel zoom is still very buggy. Please fix.
                """
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
                    map.tile_size = min(map.tile_size + (map.tile_size // 5), 75)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
                    map.tile_size = max(map.tile_size - (map.tile_size // 5), 5)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        map.offsetX -= (map.tile_size + map.tile_margin)
                    if event.key == pygame.K_s:
                        map.offsetX += (map.tile_size + map.tile_margin)
                    if event.key == pygame.K_a:
                        map.offsetY -= (map.tile_size + map.tile_margin)
                    if event.key == pygame.K_d:
                        map.offsetY += (map.tile_size + map.tile_margin)
                    """

            # Normal Mode Events #####
            if not gs.mapedit:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    if pos[0] > 10 and pos[1] > 10 and pos[0] < 1009 and pos[
                        1] < 537:  # Only take action for clicks within the map
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
                        elif next((mob for mob in entities.mobs if (row, column) == (mob.x, mob.y)), 0) and map.grid[row][column]["isVisible"] == 1:
                            mob = next((mob for mob in entities.mobs if (row, column) == (mob.x, mob.y)), 0)
                            textbox = mob.examine
                        else:
                            tile_desc = map.grid[row][column]["name"]
                            textbox = tile_desc
                            print(tile_desc)

                # Player Movement #####
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        print("Move Forward")
                        textbox = player.move("forward")
                        print("Moved to", player.x, player.y)
                    if event.key == pygame.K_s:
                        print("Move Back")
                        textbox = player.move("backward")
                        print("Moved to", player.x, player.y)
                    if event.key == pygame.K_a and pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                        print("Strafe Left")
                        player.strafe("left")
                        print("Moved to", player.x, player.y)
                    elif event.key == pygame.K_a:
                        print("Turn Right")
                        player.rotate(-1)
                    if event.key == pygame.K_d and pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                        print("Strafe Right")
                        player.strafe("right")
                        print("Moved to", player.x, player.y)
                    elif event.key == pygame.K_d:
                        print("Turn Left")
                        player.rotate(1)

                    if event.key == pygame.K_e:
                        print("Examining...")
                        try:
                            textbox = player.examine()
                        except IndexError:
                            print("Nope.")
                            textbox = "You gaze into the <!green:>Fathomless <!green:>Void... and the Void gazes back!"
                    if event.key == pygame.K_ESCAPE:
                        print("Shutting down...")
                        gs.running = False

                    # Multikey Commands #####
                    if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_LCTRL:
                        save()
                        textbox = "Game Saved."
                    if event.key == pygame.K_x and pygame.key.get_mods() & pygame.KMOD_LCTRL:
                        load()
                        textbox = "Game Loaded."
                    if event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_LCTRL:
                        map.reset()
                        textbox = "Map Reset."

                    """ Game Testing Commands """
                    if event.key == pygame.K_F1:
                        print("Create Random Monster")
                        createmonster('random')
                    if event.key == pygame.K_F2:
                        for enemy in entities.mobs:
                            print("Checking %s line of sight..." % enemy.name)
                            targeting = False
                            for i in range(0, RAYS + 1, STEP):
                                ax = sintable[i]  # Get value sin(x / (180 / pi))
                                ay = costable[i]  # cos(x / (180 / pi))
                                x = enemy.x  # Player's x
                                y = enemy.y  # Player's y
                                for z in range(enemy.viewrange):  # Cast the ray
                                    x += ax
                                    y += ay
                                    if x < 0 or y < 0 or x > map.width or y > map.height:  # If ray is out of range
                                        break
                                    try:
                                        # Discover the tile and make it visible if it exists
                                        map.grid[int(round(x))][int(round(y))].update(
                                            {"isDiscovered": 1, "isVisible": 1})
                                    except IndexError:
                                        break
                                    if map.grid[int(round(x))][int(round(y))]["isWall"] == 1:  # Stop ray if it hit
                                        break
                                    if (int(round(x)), int(round(y))) == (player.x, player.y):
                                        print("%s can see player." % enemy.name)
                                        targeting = True
                            if targeting:
                                print("%s can see player." % enemy.name)

                                print("Moving %s" % enemy.name)
                                current_location = (enemy.x, enemy.y)
                                print("%s location is %s" % (enemy.name, current_location))

                                target = (player.x, player.y)
                                print("%s location is %s" % (player.name, target))

                                path = astar.getpath(map.grid, current_location, target)
                                print(path)

                                move_dir = {0: [-1, 0],
                                            180: [1, 0],
                                            -90: [0, 1],
                                            90: [0, -1]}
                                next_step = (enemy.x + move_dir[enemy.rotation][0], enemy.y + move_dir[enemy.rotation][1])
                                try:
                                    if next_step != path[1]:
                                        print(next_step, path[1])
                                        enemy.rotate(1)
                                    elif next_step == target:
                                        enemy.attack(player)
                                    else:
                                        enemy.move("forward")
                                except IndexError:
                                    break

                    if event.key == pygame.K_m and pygame.key.get_mods() & pygame.KMOD_LCTRL:
                        print("Switching Maps...")
                        if gs.mapdisplay == 0:
                            gs.mapdisplay = 1
                        elif gs.mapdisplay == 1:
                            gs.mapdisplay = 0
                        print("Switched to Display " + str(gs.mapdisplay))

            # Map editor toggle. Needs to be in it's own indentation or else it cycles too quickly.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKQUOTE:
                    if not gs.mapedit:
                        gs.mapedit = True
                        print("Entering Map Editor Mode!")
                        textbox = "Entering <!blue:>Map <!blue:>Editor Mode!"
                    elif gs.mapedit:
                        gs.mapedit = False
                        print("Map Editor Disabled...")
                        textbox = "Map Editor <!red:>Disabled..."

        """ Begin drawing the game screen """

        gw.fill(dkgray)

        if gs.mapdisplay == 0:

            # Create the 4 main surfaces: viewscreen, minimap, textbox, and menu

            viewscreen = pygame.Surface((999, 527))
            minimap = pygame.Surface((256, 256))

            statmenu = pygame.Surface((257, 439))  # TODO Display relevant information

            """ Draw the map """

            # Reset visible squares...
            for x in range(map.height):
                for y in range(map.width):
                    if map.grid[x][y]["isVisible"] == 1:
                        map.grid[x][y]["isVisible"] = 0
            # Determine which squares are visible...
            for i in range(0, RAYS + 1, STEP):
                ax = sintable[i]  # Get value sin(x / (180 / pi))
                ay = costable[i]  # cos(x / (180 / pi))
                x = player.x  # Player's x
                y = player.y  # Player's y
                for z in range(player.viewrange):  # Cast the ray
                    x += ax
                    y += ay
                    if x < 0 or y < 0 or x > map.width or y > map.height:  # If ray is out of range
                        break
                    try:
                        # Discover the tile and make it visible if it exists
                        map.grid[int(round(x))][int(round(y))].update({"isDiscovered": 1, "isVisible": 1})
                    except IndexError:
                        break
                    if map.grid[int(round(x))][int(round(y))]["isWall"] == 1:  # Stop ray if it hit
                        break
            map.grid[player.x][player.y].update({"isDiscovered": 1, "isVisible": 1})
            for x in range(map.height):
                for y in range(map.width):
                    tile = pygame.Surface((map.tile_size, map.tile_size))
                    tile.fill((map.grid[x][y].get("color")))
                    if map.grid[x][y].get("isVisible") == 0 and map.grid[x][y].get("isDiscovered") == 1:
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
                    if map.grid[x][y].get("isVisible") == 0 and map.grid[x][y].get("isDiscovered") == 1:
                        tile.set_alpha(64)
                    if map.grid[x][y].get("isVisible") == 0 and map.grid[x][y].get("isDiscovered") == 0:
                        tile.fill(black)
                    minimap.blit(tile, ((y + map.offsetY/(map.tile_size+map.tile_margin)) + 110,
                                        (x + map.offsetX/(map.tile_size+map.tile_margin)) + 119))

            """ Draw the Player Icon """
            maparrow = pygame.transform.rotate(player.icon, player.rotation)
            viewscreen.blit(maparrow, ((player.y * (map.tile_size + map.tile_margin)) + map.offsetY + 1,
                                       (player.x * (map.tile_size + map.tile_margin)) + map.offsetX + 1))

            """ Draw the Enemy Icons """
            for enemy in entities.mobs:
                if map.grid[enemy.x][enemy.y].get("isVisible") == 1:
                    maparrow = pygame.transform.rotate(enemy.icon, enemy.rotation)
                    viewscreen.blit(maparrow, ((enemy.y * (map.tile_size + map.tile_margin)) + map.offsetY + 1,
                                               (enemy.x * (map.tile_size + map.tile_margin)) + map.offsetX + 1))

            """ Draw the Info Box """
            heroname = font.render(player.name, 0, white)
            heroname_rect = heroname.get_rect()
            heroname_rect.center = (257/2, 20)
            statmenu.blit(heroname, heroname_rect)

            # TODO: Add HP bar below name
            # TODO: Add player stats (STR, DEX, CON, etc.) below HP bar

            """ Tile Descriptions? """
            # tiledescrect = font.render(tile_desc, False, black)
            # descrect = tiledescrect.get_rect()
            # descrect.center = (658, 300)
            # gw.blit(tiledescrect, descrect)

            message(textbox)

            # Create the 4 main surfaces: viewscreen, minimap, textbox, and menu

            gw.blit(viewscreen, (10, 10))
            gw.blit(minimap, (1014, 10))

            gw.blit(statmenu, (1014, 271))

            # Display game version
            if gs.DISPLAY_VERSION:
                version = tiny_font.render(title, 0, red)
                version_rect = version.get_rect()
                gw.blit(version, (2, (window_res[1]-version_rect.height)))

        """ Second display view """
        # TODO: Either trash this or fix it.
        # Supposed to display map scalable and scrollable. For now just barely manageable (somehow).
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
