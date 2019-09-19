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
from res.misc import colortag  # <-- I WROTE THAT ONE!
from res.misc import character_gen
from res.misc import dungenerator2
from res.misc import astar  # <-- Tried to use it, but it broke easily.

# import pprint
# import sys
# from res import pygame_textinput  # <-- For entering player name
# from natural.number import ordinal  # <-- Makes the numbers look pretty - 1st, 2nd, 3rd, 4th...

p = inflect.engine()

pygame.init()
title = "dungeon engine v0.3.3-dev"

window_res = (1280, 720)
FPS = 30

gw = pygame.display.set_mode(window_res)
# gw = pygame.display.set_mode(window_res, pygame.FULLSCREEN)
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
yellow = (255, 255, 0)
green = (0, 255, 0)
dkgreen = (1, 50, 32)
blue = (0, 0, 255)
purple = (78, 48, 132)

# Font(s)
font = pygame.font.Font('res/fonts/Alkhemikal.ttf', 28)
stats_font = pygame.font.Font('res/fonts/Poco.ttf', 20)
tiny_font = pygame.font.Font('res/fonts/Poco.ttf', 10)

# Image(s)
heroico = pygame.image.load('res/images/maphero.png').convert_alpha()
mobico = pygame.image.load('res/images/mapenemy.png').convert_alpha()
chestico = pygame.image.load('res/images/chest.png').convert_alpha()
chest_open = pygame.image.load('res/images/chest_open.png').convert_alpha()
deadico = pygame.image.load('res/images/dead_mob.png').convert_alpha()
graveico = pygame.image.load('res/images/grave.png').convert_alpha()
door_open = pygame.image.load('res/images/door_open.png').convert_alpha()
door_closed = pygame.image.load('res/images/door_closed.png').convert_alpha()
titlecard = pygame.image.load('res/images/studio_logo.png').convert()
gamelogo = pygame.image.load('res/images/game_logo2.png').convert()

swordico = pygame.image.load('res/images/sword.png').convert_alpha()
shieldico = pygame.image.load('res/images/shield.png').convert_alpha()

# .JSON(s)
monstersfile = 'res/json/monsters.json'
itemsfile = 'res/json/items.json'
tilesfile = 'res/json/tiles.json'
containersfile = 'res/json/containers.json'


# Test starts here
class GameState:
    def __init__(self):
        self.running = True
        self.mapdisplay = 0
        self.infoscreen = 0
        self.INTRO_DISABLED = True
        self.DISPLAY_VERSION = True
        self.intro_vid = True
        self.mainmenu = False
        self.newgame = False
        self.mapedit = False

        self.inv_interface = False

        self.tile_desc = ""
        self.last_message = ""

        self.defaultxy = (486, 250)

        self.viewscreen_size = (999, 527)
        self.minimap_size = (256, 256)
        self.textbox_size = (999, 168)
        self.infoscreen_size = (257, 439)
        self.infoscreen_offset = (1014, 271)


class Entities:
    def __init__(self):
        self.mobs = []
        self.items = []
        self.containers = []
        self.entityID = 0

    def showentities(self):
        itemlist = [(item.name + " ID:" + item.ID) for item in self.items]
        moblist = [(mob.name + " ID:" + mob.ID) for mob in self.mobs]
        containerlist = [(container.name + " ID:" + container.ID) for container in self.containers]
        print("Mobs:\n" + str(moblist) + "\n"
              "Items:\n" + str(itemlist) + "\n"
              "Containers:\n" + str(containerlist) + "\n"
              "Next entity ID: " + str(self.entityID))

    def reset(self):
        self.__init__()


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
        # print("Map Reset Disabled, use Map Editor.")
        print("Resetting Map...")
        player.x = 0
        player.y = 0
        self.offsetX = gs.defaultxy[1]
        self.offsetY = gs.defaultxy[0]
        entities.reset()
        self.grid = [[1 for x in range(self.width)] for y in range(self.height)]
        assign_tiles()
        print("Map reset")

    def generate(self):
        print("Generating new map...")
        entities.reset()
        self.grid = dungenerator2.get_map(5, 10, 35, 10)
        assign_tiles()
        # player.x, player.y = random.randint(0, map.width-1), random.randint(0, map.height-1)
        # if map.grid[player.x][player.y]['isWall'] != 0:
        while map.grid[player.x][player.y]['isWall'] != 0:
            print("attempting to place player at x%d y%d..." % (player.x, player.y))
            player.x, player.y = random.randint(0, map.width - 1), random.randint(0, map.height - 1)
        print("Success at x%d y%d!" % (player.x, player.y))
        self.offsetX = gs.defaultxy[1] - (player.x * (self.tile_size + self.tile_margin))
        self.offsetY = gs.defaultxy[0] - (player.y * (self.tile_size + self.tile_margin))
        print("Map generated")
        print("Spawning monsters...")
        createmonster('random', qty=(random.randint(10, 20)))
        print("Spawning chests...")
        for x in range(0, map.width):
            for y in range(0, map.height):
                if map.grid[x][y].get("ID") == 4:
                    # TODO: pull inventory from loot table instead of hard-coding
                    createcontainer("chest", ["sword", "shield", "shield", "shield", "shield", "shield", "shield", "shield", "shield", "shield"], x, y)
                    assign_tiles(1, x, y)


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
        move_dir = {0: [-1, 0],
                    180: [1, 0],
                    -90: [0, 1],
                    90: [0, -1]}
        try:
            if direction == "forward":
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
            if direction == "backward":
                prev_x = self.x - move_dir[self.rotation][0]
                prev_y = self.y - move_dir[self.rotation][1]
                prev_square = map.grid[prev_x][prev_y]
                wall_check = prev_square["isWall"]
                for enemy in entities.mobs:
                    if (enemy.x, enemy.y) == (prev_x, prev_y):
                        blocked = True
                        block_type = enemy.name
                if wall_check > 0:
                    blocked = True
                    block_type = prev_square["name"]
                border_chk = 1
        except IndexError:
            border_chk = -1
        if direction == "forward" and (border_chk < 0 or next_x < 0 or next_y < 0):
            print("Out of Area")
            blockmsg = "You dare not tread into the <!green>Fathomless Void.</>"
        elif direction == "backward" and (border_chk < 0 or prev_x < 0 or prev_y < 0):
            print("Out of Area")
            blockmsg = "You dare not back into the <!green>Fathomless Void.</>"
        elif blocked:
            print("Blocked")
            blockmsg = "There's %s in the way." % p.a(block_type)
        else:
            blockmsg = ""
            if direction == "forward":
                self.x += move_dir[self.rotation][0]
                self.y += move_dir[self.rotation][1]
                if isinstance(self, Player):
                    map.offsetX -= move_dir[self.rotation][0] * mts
                    map.offsetY -= move_dir[self.rotation][1] * mts
            if direction == "backward":
                self.x -= move_dir[self.rotation][0]
                self.y -= move_dir[self.rotation][1]
                if isinstance(self, Player):
                    map.offsetX += move_dir[self.rotation][0] * mts
                    map.offsetY += move_dir[self.rotation][1] * mts
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
        self.sex = "male"
        self.stat = {"str": 12, "dex": 10, "con": 15, "wis": 8, "cha": 11, "lck": 10}
        self.max_hp = (self.stat['con'] * 8)
        self.xp = 0
        self.lvl = 1
        self.hp = self.max_hp
        self.default_weapon = Item(None, "Fist", "swordico", "", "weapon", True, 0, [0, 2])
        self.weapon = self.default_weapon
        self.armor = []
        self.inventory = []
        self.inv_item_array = []
        self.gold = 0
        self.max_carry_weight = (self.stat['con'] + self.stat['str']) * 10
        # self.killcount = 0
        # self.encounter = 0
        # self.gametime = 0
        # self.xp = 0
        # self.lvl = 1
        # self.gold = 0

    def examine(self):
        move_dir = {0: [-1, 0],
                    180: [1, 0],
                    -90: [0, 1],
                    90: [0, -1]}
        next_x = self.x + move_dir[self.rotation][0]
        next_y = self.y + move_dir[self.rotation][1]
        target = next((mob for mob in entities.mobs if (next_x, next_y) == (mob.x, mob.y)), None)
        if not target:
            target = next((container for container in entities.containers if (next_x, next_y) == (container.x, container.y)), None)
            if not target:
                message(map.grid[next_x][next_y]["examine"])
            else:
                message(target.examine)
        else:
            message(target.examine)

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
        message("You attack the %s with your %s for %d damage, leaving it with %d health."
                % (target.name, self.weapon.name, atkdamage, target.hp))
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
            target.die()

    def interact(self):
        move_dir = {0: [-1, 0],
                    180: [1, 0],
                    -90: [0, 1],
                    90: [0, -1]}
        next_x = self.x + move_dir[self.rotation][0]
        next_y = self.y + move_dir[self.rotation][1]
        target = map.grid[next_x][next_y]
        if target.get("ID") == 3:
            if target["isWall"] == 0:
                target["isWall"] = 1
            elif target["isWall"] == 1:
                target["isWall"] = 0
        else:
            target = next((mob for mob in entities.mobs if (mob.x, mob.y) == (next_x, next_y)), None)
            if not target:
                target = next((container for container in entities.containers if (container.x, container.y) == (next_x, next_y)), None)
                if not target:
                    message("There's nothing there...")
                else:
                    if target.name == "chest":
                        target.icon = "chest_open"
                    gs.infoscreen = 1
                    pygame.display.update()
                    inv_interface(target.ID)
                    gs.infoscreen = 0
            else:
                self.attack(target.ID)

    def die(self):
        message("Oh no, you appear to be dead...")
        player.icon = graveico
        player.rotation = 0
        gs.gameover = True

    def rest(self):
        can_rest = False
        if player.hp >= player.max_hp:
            message("You are already fully rested.")
        else:
            for mob in entities.mobs:
                if map.grid[mob.x][mob.y]["isVisible"] == 1:
                    message("You can't rest here, you are in peril!")
                else:
                    can_rest = True
            if can_rest:
                message("You take a moment's rest...")
                rest = random.randint(0, 3)
                if player.hp + rest >= player.max_hp:
                    player.hp = player.max_hp
                    print("Recovered to max health")
                else:
                    player.hp = player.hp + rest
                    print("Recovered %d health" % rest)
                enemy_ai_step()


class Monster(Entity):
    def __init__(self, ID, mobtype, name, examine, hp, weapon, damage, viewrange, isHostile, x, y):
        self.ID = ID
        self.mobtype = mobtype
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
        if target.hp <= 0:
            target.die()

    def die(self):
        print("The %s is dead." % self.name)
        inventory = []
        createcontainer("corpse", inventory, self.x, self.y)
        for enemy in entities.mobs:
            if enemy.ID == self.ID:
                enemy_index = entities.mobs.index(enemy)
                print("Removing %s..." % enemy.name)
                entities.mobs.pop(enemy_index)


class Item:
    def __init__(self, ID, name, icon, examine, slot, isEquipable, weight, damage):
        self.ID = ID
        self.name = name
        self.icon = icon
        self.examine = examine
        self.slot = slot
        self.isEquipable = isEquipable
        self.weight = weight
        self.damage = damage


class Container:
    def __init__(self, ID, name, icon, examine, slots, inventory, x, y):
        self.ID = ID
        self.name = name
        self.icon = icon
        self.examine = examine
        self.slots = slots
        self.inventory = inventory
        self.x = x
        self.y = y


def createmonster(monster, qty=1):
    with open(monstersfile, 'r') as data:
        monsters = json.load(data)
    check_random = monster
    for x in range(0, qty):
        if check_random == 'random':
            monster = random.choice(list(monsters.keys()))
        spawn_xy = (random.randint(0, map.width - 1), random.randint(0, map.height - 1))
        while map.grid[spawn_xy[0]][spawn_xy[1]]['isWall'] != 0:
            spawn_xy = (random.randint(0, map.width - 1), random.randint(0, map.height - 1))
        token = str(entities.entityID)
        if monster in monsters:
            entities.mobs.append(Monster(token,
                                         monsters[monster]['mobtype'],
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
                                   items[itemname]['icon'],
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


def createcontainer(container_type, inventory, x, y):
    with open(containersfile, 'r') as data:
        containers = json.load(data)
    token = str(entities.entityID)
    contents = []
    for item in inventory:
        item_id = createitem(item)
        contents.append(next(thing for thing in entities.items if thing.ID == item_id))
    print(contents)
    if container_type in containers:
        entities.containers.append(Container(token,
                                             containers[container_type]['name'],
                                             containers[container_type]['icon'],
                                             containers[container_type]['examine'],
                                             containers[container_type]['slots'],
                                             contents,
                                             x, y))
        print("created container %s" % container_type)
        entities.entityID += 1
    else:
        print("%s in unavailable." % container_type)


def assign_tiles(new_tile=None, x=None, y=None):
    with open(tilesfile, 'r') as data:
        tiles = json.load(data)
    if not new_tile:
        for x in range(map.height):
            for y in range(map.width):
                ID = map.grid[x][y]
                map.grid[x][y] = {}
                map.grid[x][y].update(tiles[str(ID)])
                map.grid[x][y].update({"isDiscovered": 0, "isVisible": 0, "ID": ID})
    else:
        map.grid[x][y].update(tiles[str(new_tile)])


def inv_interface(ID):
    container = next((container for container in entities.containers if ID == container.ID), None)
    gs.inv_interface = True

    while gs.inv_interface:
        box_offset = (window_res[0] / 2 - 240, window_res[1] / 2 - 250)

        container_screen = pygame.Surface((220, 120))
        cs_border = pygame.draw.rect(container_screen, white, (0, 0, 220, 120), 0)
        pygame.draw.rect(container_screen, black, (4, 4, 212, 112), 0)

        windowheader = stats_font.render("Contents of %s:" % container.name, 0, white)
        container_screen.blit(windowheader, (10, 0))

        item_offset_x = 10
        item_offset_y = 10
        item_array = []

        slot_offset_x = 10
        slot_offset_y = 30
        slot_dims = 40

        for slot in range(container.slots):
            pygame.draw.rect(container_screen, white, (slot_offset_x, slot_offset_y, slot_dims, slot_dims), 1)
            slot_offset_x = slot_offset_x + slot_dims
            if slot_offset_x >= 200:
                slot_offset_y = slot_offset_y + slot_dims
                slot_offset_x = 10
        for item in container.inventory:
            icon = eval(item.icon)
            itemicon = container_screen.blit(icon, (8+item_offset_x, 27+item_offset_y))
            item_array.append([itemicon, item.ID])
            item_offset_x = item_offset_x + 40
            if item_offset_x >= 200:
                item_offset_y = item_offset_y + 40
                item_offset_x = 10
        gw.blit(container_screen, box_offset)

        pygame.display.update()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = (pygame.mouse.get_pos()[0] - box_offset[0], pygame.mouse.get_pos()[1] - box_offset[1])
                for rect in item_array:
                    if rect[0].collidepoint(pos):
                        take_item = next(item for item in entities.items if item.ID == rect[1])
                        player.inventory.append(take_item)
                        container.inventory.remove(next(item for item in container.inventory if item.ID == rect[1]))
                        pygame.display.update()
                if not cs_border.collidepoint(pos):
                    print("outside area")
                    gs.inv_interface = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                gs.inv_interface = False


def enemy_ai_step():
    RAYS = 360
    STEP = 3
    sintable = []
    costable = []
    for x in range(0, 361):
        sincalc = math.sin(x / (180 / math.pi))
        sintable.append(sincalc)
        coscalc = math.cos(x / (180 / math.pi))
        costable.append(coscalc)
    print("Checking line of sight for %d enemies..." % len(entities.mobs))
    for enemy in entities.mobs:
        targeting = False
        for i in range(0, RAYS + 1, STEP):
            ax = sintable[i]  # Get value sin(x / (180 / pi))
            ay = costable[i]  # cos(x / (180 / pi))
            x = enemy.x  # Player's x
            y = enemy.y  # Player's y
            for z in range(enemy.viewrange):  # Cast the ray
                x += ax
                y += ay
                if x < 0 or y < 0 or x > map.width - 1 or y > map.height - 1:  # If ray is out of range
                    break
                if map.grid[int(round(x))][int(round(y))]["isWall"] == 1:  # Stop ray if it hit
                    break
                if (int(round(x)), int(round(y))) == (player.x, player.y):
                    targeting = True
                    message("The %s sees you!" % enemy.name)
        if targeting:
            print("%s can see player." % enemy.name)

            print("Moving %s" % enemy.name)
            current_location = (enemy.x, enemy.y)
            print("%s location is %s" % (enemy.name, current_location))

            target = (player.x, player.y)
            print("%s location is %s" % (player.name, target))

            path = astar.getpath(map.grid, current_location, target)
            print(path)
            if not path[1]:
                print("That's a wall alright")
                continue

            move_dir = {0: [-1, 0],
                        180: [1, 0],
                        -90: [0, 1],
                        90: [0, -1]}
            next_step = (enemy.x + move_dir[enemy.rotation][0], enemy.y + move_dir[enemy.rotation][1])
            try:
                if next_step != path[1]:
                    while next_step != path[1]:
                        enemy.rotate(1)
                        next_step = (
                            enemy.x + move_dir[enemy.rotation][0], enemy.y + move_dir[enemy.rotation][1])
                        print(next_step, path[1])
                elif next_step == target:
                    enemy.attack(player)
                else:
                    enemy.move("forward")
            except IndexError:
                break
        if not targeting:
            choice = random.randint(0, 1)
            if choice == 0:  # "Wandering"
                turning = random.randint(0, 1)
                if turning == 0:
                    enemy.rotate(random.randint(0, 1))
                if turning == 1:
                    move_dir = {0: [-1, 0],
                                180: [1, 0],
                                -90: [0, 1],
                                90: [0, -1]}
                    next_step = (enemy.x + move_dir[enemy.rotation][0], enemy.y + move_dir[enemy.rotation][1])
                    try:
                        if map.grid[next_step[0]][next_step[1]]["isWall"] >= 1:
                            enemy.rotate(random.randint(0, 1))
                    except IndexError:
                        print("Something bad happened, enemy tried to move off map? investigate.")
                        print(enemy.x, enemy.y)
                    enemy.move("forward")
            if choice == 1:  # "Resting", maybe let the monsters heal themselves on higher difficulty?
                pass


def message(words, *location):
    gs.last_message = words
    words = colortag.decode(words)
    max_width = 800
    textbox = pygame.Surface((gs.textbox_size[0], gs.textbox_size[1]))
    if not location:
        pos = 10, 10
    else:
        pos = location
    x, y = pos[0], pos[1]
    for word, color in words:
        space = font.size(' ')[0]
        each_word = font.render(word, False, eval(color))
        word_width, word_height = each_word.get_size()
        if word == "<br>":
            y += word_height
            x = pos[0]
            each_word = font.render("", False, eval(color))
            word_width, word_height = each_word.get_size()
            space = 0
        if x + word_width >= max_width:
            x = pos[0]
            y += word_height
        textbox.blit(each_word, (x, y))
        x += word_width + space
    gw.blit(textbox, (10, 542))
    pygame.display.update()


def button(button_position, button_text, *button_width, button_color=white):  # Gets button X,Y and button label
    button_padding = 25  # Set padding between button text and border
    label = font.render(button_text, 0, button_color)  # Renders button label
    button_size_x, button_size_y = label.get_size()  # Sends button label dimensions to A,B variables
    if not button_width:  # Outputs the button with default padding to the screen
        gw.blit(label, ((button_position[0] + (button_padding / 2)),
                        (button_position[1] + (button_padding / 2))))
        button_size = (button_position[0], button_position[1],
                       (button_size_x + button_padding),
                       (button_size_y + (button_padding * 0.8)))
    else:  # Outputs the button with padding and centered text to the screen
        gw.blit(label, (((button_position[0] + ((button_width[0] + button_padding) / 2)) -
                         (button_size_x / 2)), (button_position[1] + (button_padding / 2))))
        button_size = (button_position[0], button_position[1],
                       (button_width[0] + button_padding),
                       (button_size_y + (button_padding * 0.8)))
    pygame.draw.rect(gw, button_color, button_size, 4)
    return pygame.Rect(button_size)


def tiny_button(button_position, button_text, *button_width, button_color=white):  # Gets button X,Y and button label
    button_padding = 8  # Set padding between button text and border
    label = tiny_font.render(button_text, 0, button_color)  # Renders button label
    button_size_x, button_size_y = label.get_size()  # Sends button label dimensions to A,B variables
    if not button_width:  # Outputs the button with default padding to the screen
        gw.blit(label, ((button_position[0] + (button_padding / 2)),
                        (button_position[1] + (button_padding / 2))))
        button_size = (button_position[0], button_position[1],
                       (button_size_x + button_padding),
                       (button_size_y + (button_padding * 0.8)))
    else:  # Outputs the button with padding and centered text to the screen
        gw.blit(label, (((button_position[0] + ((button_width[0] + button_padding) / 2)) -
                         (button_size_x / 2)), (button_position[1] + (button_padding / 2))))
        button_size = (button_position[0], button_position[1],
                       (button_width[0] + button_padding),
                       (button_size_y + (button_padding * 0.8)))
    pygame.draw.rect(gw, button_color, button_size, 1)
    return pygame.Rect(button_size)


def titlescreen():
    while gs.intro_vid:
        pygame.time.wait(1000)

        tx = 1280  # 575, 850
        ratio = int(1280 / tx)
        ty = 720 * ratio

        for i in range(0, 255, 3):
            gw.fill(black)

            titlecardzoom = pygame.transform.smoothscale(titlecard, (tx, ty))
            titlecardzoomrect = titlecardzoom.get_rect()
            titlecardzoomrect.center = (window_res[0] / 2, window_res[1] / 2)
            titlecardzoom.set_alpha(i)
            tx += 1
            ty += 1 * ratio
            gw.blit(titlecardzoom, titlecardzoomrect)
            pygame.display.update()

        for i in range(0, 50):
            gw.fill(black)

            titlecardzoom = pygame.transform.smoothscale(titlecard, (tx, ty))
            titlecardzoomrect = titlecardzoom.get_rect()
            titlecardzoomrect.center = (window_res[0] / 2, window_res[1] / 2)
            tx += 1
            ty += 1 * ratio
            gw.blit(titlecardzoom, titlecardzoomrect)
            pygame.display.update()

        for i in reversed(range(0, 255, 3)):
            gw.fill(black)

            titlecardzoom = pygame.transform.smoothscale(titlecard, (tx, ty))
            titlecardzoomrect = titlecardzoom.get_rect()
            titlecardzoomrect.center = (window_res[0] / 2, window_res[1] / 2)
            titlecardzoom.set_alpha(i)
            tx += 1
            ty += 1 * ratio
            gw.blit(titlecardzoom, titlecardzoomrect)
            pygame.display.update()

        pygame.time.wait(500)
        gs.intro_vid = False


def mainmenu():
    gs.mainmenu = True
    if savegame_exist():
        button_color = white
    else:
        button_color = dkgray
    while gs.mainmenu:
        for menu_event in pygame.event.get():
            if menu_event.type == pygame.QUIT:
                gs.running = False
                gs.mainmenu = False

            gw.fill(black)

            logorect = gamelogo.get_rect()
            gw.blit(gamelogo, ((window_res[0] / 2) - (logorect.width / 2), 40))

            version = stats_font.render(title, 0, red)
            version_rect = version.get_rect()
            gw.blit(version, (5, (window_res[1] - version_rect.height)))

            loadgame = button(((window_res[0] / 2 - 150), window_res[1] / 2 - 100), "Continue your Adventure", 300,
                              button_color=button_color)
            start = button(((window_res[0] / 2 - 150), window_res[1] / 2 - 30), "Venture Forth!", 300)
            editor = button(((window_res[0] / 2 - 150), window_res[1] / 2 + 40), "Map Editor", 300)
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
    player.name, player.stat, player.race, player.job, player.sex = character_gen.main(28)


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


def savegame_exist():
    savepath = 'save/'
    savegames = [file for file in os.listdir(savepath) if os.path.isfile(os.path.join(savepath, file))]
    if savegames:
        print("found %d save file(s)" % len(savegames))
        return True
    else:
        print("ERROR no saves")
        return False


# def loadgame():


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
gs = GameState()
brush = Brush()
entities = Entities()
player = Player()


# load()


def main():
    if not gs.INTRO_DISABLED:
        titlescreen()

    mainmenu()

    # if gs.load_game_menu:
    #     loadgame()
    if gs.newgame:
        map.generate()
        newgame()
        message("Welcome, <!red>%s!</> Your destiny awaits." % player.name)
    else:
        load()
        message("Welcome back, <!red>%s.</> We've been waiting for you." % player.name)

    while gs.running:
        RAYS = 360  # Should be 360!

        STEP = 3  # The step of for cycle. More = Faster, but large steps may
        # cause artifacts. Step 3 is great for radius 10.

        # Tables of precalculated values of sin(x / (180 / pi)) and cos(x / (180 / pi))
        sintable = []
        costable = []

        for x in range(0, 361):
            sincalc = math.sin(x / (180 / math.pi))
            sintable.append(sincalc)
            coscalc = math.cos(x / (180 / math.pi))
            costable.append(coscalc)

        gw.fill(dkgray)

        # Create the 4 main surfaces: viewscreen, minimap, textbox, and menu

        viewscreen = pygame.Surface((999, 527))
        minimap = pygame.Surface((256, 256))
        textbox = pygame.Surface((gs.textbox_size[0], gs.textbox_size[1]))
        infoscreen = pygame.Surface((257, 439))

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

        """ Draw the Minimap """
        for x in range(map.height):
            for y in range(map.width):
                tile = pygame.Surface((1, 1))
                tile.fill((map.grid[x][y].get("color")))
                if map.grid[x][y].get("isVisible") == 0 and map.grid[x][y].get("isDiscovered") == 1:
                    tile.set_alpha(64)
                if map.grid[x][y].get("isVisible") == 0 and map.grid[x][y].get("isDiscovered") == 0:
                    tile.fill(black)
                minimap.blit(tile, ((y + map.offsetY / (map.tile_size + map.tile_margin)) + 110,
                                    (x + map.offsetX / (map.tile_size + map.tile_margin)) + 119))

        """ Draw Containers """
        for container in entities.containers:
            if map.grid[container.x][container.y].get("isVisible") == 1:
                viewscreen.blit(eval(container.icon),
                                ((container.y * (map.tile_size + map.tile_margin)) + map.offsetY + 1,
                                 (container.x * (map.tile_size + map.tile_margin)) + map.offsetX + 1))

        """ Draw the Player Icon """
        maparrow = pygame.transform.rotate(player.icon, player.rotation)
        viewscreen.blit(maparrow, ((player.y * (map.tile_size + map.tile_margin)) + map.offsetY + 1,
                                   (player.x * (map.tile_size + map.tile_margin)) + map.offsetX + 1))

        """ Draw Enemy Icons """
        for enemy in entities.mobs:
            if map.grid[enemy.x][enemy.y].get("isVisible") == 1:
                maparrow = pygame.transform.rotate(enemy.icon, enemy.rotation)
                viewscreen.blit(maparrow, ((enemy.y * (map.tile_size + map.tile_margin)) + map.offsetY + 1,
                                           (enemy.x * (map.tile_size + map.tile_margin)) + map.offsetX + 1))

        """ Draw Doors """
        for x in range(0, map.width):
            for y in range(0, map.height):
                if map.grid[x][y].get("isVisible") == 1:
                    if map.grid[x][y].get("ID") == 3 and map.grid[x][y].get("isWall") == 0:
                        viewscreen.blit(door_open, ((y * (map.tile_size + map.tile_margin)) + map.offsetY + 1,
                                                    (x * (map.tile_size + map.tile_margin)) + map.offsetX + 1))
                    if map.grid[x][y].get("ID") == 3 and map.grid[x][y].get("isWall") == 1:
                        viewscreen.blit(door_closed, ((y * (map.tile_size + map.tile_margin)) + map.offsetY + 1,
                                                      (x * (map.tile_size + map.tile_margin)) + map.offsetX + 1))

        """ Draw the Info Box """
        # stats, inventory, game menu
        stats_button = pygame.draw.rect(infoscreen, white, (0,
                                                            gs.infoscreen_size[1] - 30,
                                                            gs.infoscreen_size[0] / 3,
                                                            30), 1)
        stats_label = stats_font.render("Stats", 0, white)
        stats_label_rect = stats_label.get_rect()
        stats_label_rect.center = (stats_button.center[0], stats_button.center[1] - 5)
        infoscreen.blit(stats_label, stats_label_rect)
        inventory_button = pygame.draw.rect(infoscreen, white, (gs.infoscreen_size[0] / 3,
                                                               gs.infoscreen_size[1] - 30,
                                                               gs.infoscreen_size[0] / 3,
                                                               30), 1)
        inventory_label = stats_font.render("Inv", 0, white)
        inventory_label_rect = inventory_label.get_rect()
        inventory_label_rect.center = (inventory_button.center[0], inventory_button.center[1] - 5)
        infoscreen.blit(inventory_label, inventory_label_rect)
        menu_button = pygame.draw.rect(infoscreen, white, (((gs.infoscreen_size[0] / 3) * 2),
                                                           gs.infoscreen_size[1] - 30,
                                                           (gs.infoscreen_size[0] / 3) + 1,
                                                           30), 1)
        menu_label = stats_font.render("Menu", 0, white)
        menu_label_rect = menu_label.get_rect()
        menu_label_rect.center = (menu_button.center[0], menu_button.center[1] - 5)
        infoscreen.blit(menu_label, menu_label_rect)

        if gs.infoscreen == 0:  # Player Stats
            """ Hero Name """
            heroname = font.render(player.name, 0, white)
            heroname_rect = heroname.get_rect()
            heroname_rect.center = (gs.infoscreen_size[0] / 2, 20)
            infoscreen.blit(heroname, heroname_rect)
            """ HP Bar """
            pygame.draw.rect(infoscreen, dkgray, (10, heroname_rect[3] + 7, gs.infoscreen_size[0] - 20, 7))
            hpcolor = dkgreen
            if player.hp < player.max_hp:
                hpcolor = green
            if player.hp < player.max_hp / 1.5:
                hpcolor = yellow
            if player.hp < player.max_hp / 3:
                hpcolor = orange
            if player.hp < player.max_hp / 8:
                hpcolor = red
            barlength = player.hp * (gs.infoscreen_size[0] - 20) / player.max_hp
            pygame.draw.rect(infoscreen, hpcolor, (10, heroname_rect[3] + 7, barlength, 7))
            """ Player Stats """
            playerinfo = "%s %s, lvl %d" % (player.race, player.job, player.lvl)
            race_class = stats_font.render(playerinfo, 0, white)
            race_class_rect = race_class.get_rect()
            race_class_rect.center = (gs.infoscreen_size[0] / 2, heroname_rect[3] + 22)
            infoscreen.blit(race_class, race_class_rect)
            """ Player Skills """
            skillpad = [23, 90]
            for skill in player.stat:
                ability = stats_font.render(skill, 0, white)
                score = font.render(str(player.stat[skill]), 0, white)
                ability_rect = ability.get_rect()
                score_rect = score.get_rect()
                ability_rect.midtop = skillpad
                score_rect.midbottom = (skillpad[0], skillpad[1] + 10)
                skillpad[0] += 42
                infoscreen.blit(ability, ability_rect)
                infoscreen.blit(score, score_rect)
            pygame.draw.rect(infoscreen, black, (0, gs.infoscreen_size[1] - 30,
                                                 gs.infoscreen_size[0] / 3, 1))

        if gs.infoscreen == 1:  # Inventory
            windowheader = stats_font.render("Inventory:", 0, white)
            infoscreen.blit(windowheader, (10, 0))
            item_offset_x = 10
            item_offset_y = 10

            slot_offset_x = 10
            slot_offset_y = 30
            slot_dims = 40
            for slot in range(len(player.inventory)):
                pygame.draw.rect(infoscreen, white, (slot_offset_x, slot_offset_y, slot_dims, slot_dims), 1)
                slot_offset_x = slot_offset_x + slot_dims
                if slot_offset_x >= 250:
                    slot_offset_y = slot_offset_y + slot_dims
                    slot_offset_x = 10
            for item in player.inventory:
                icon = eval(item.icon)
                itemicon = infoscreen.blit(icon, (8 + item_offset_x, 27 + item_offset_y))
                player.inv_item_array.append([itemicon, item.ID])
                item_offset_x = item_offset_x + 40
                if item_offset_x >= 250:
                    item_offset_y = item_offset_y + 40
                    item_offset_x = 10

            pygame.draw.rect(infoscreen, black, (gs.infoscreen_size[0] / 3, gs.infoscreen_size[1] - 30,
                                                 gs.infoscreen_size[0] / 3, 1))
        if gs.infoscreen == 2:  # Game Menu
            pygame.draw.rect(infoscreen, black, (((gs.infoscreen_size[0] / 3) * 2), gs.infoscreen_size[1] - 30,
                                                 gs.infoscreen_size[0] / 3, 1))

        """ Create the 4 main surfaces: viewscreen, minimap, textbox, and menu """

        gw.blit(textbox, (10, 542))
        gw.blit(viewscreen, (10, 10))
        gw.blit(minimap, (1014, 10))
        gw.blit(infoscreen, (1014, 271))
        message(gs.last_message)

        # Display game version
        if gs.DISPLAY_VERSION:
            version = tiny_font.render(title, 0, red)
            version_rect = version.get_rect()
            gw.blit(version, (2, (window_res[1] - version_rect.height)))
            pygame.display.update()

        clock.tick(FPS)

        pygame.display.update()

        """ Get input events and interactions """

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                gs.running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                pos2 = (pos[0] - gs.infoscreen_offset[0], pos[1] - gs.infoscreen_offset[1])
                print(pos2)
                # Only take action for clicks within the map
                if 10 < pos[0] < 1009 and 10 < pos[1] < 537:
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

                if stats_button.collidepoint(pos2):
                    print("Stats Menu")
                    gs.infoscreen = 0
                if inventory_button.collidepoint(pos2):
                    print("Inventory Menu")
                    player.showinventory()
                    gs.infoscreen = 1
                if menu_button.collidepoint(pos2):
                    print("Game Menu")
                    gs.infoscreen = 2

                if gs.infoscreen == 1:
                    for rect in player.inv_item_array:
                        if rect[0].collidepoint(pos2):
                            print(rect)
                            player.equip(rect[1])

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                pos = pygame.mouse.get_pos()
                if 10 < pos[0] < 1009 and pos[1] > 10 and pos[
                    1] < 537:  # Only take action for clicks within the minimap
                    column = (pos[0] - map.offsetY - 10) // (map.tile_size + map.tile_margin)
                    row = (pos[1] - map.offsetX - 10) // (map.tile_size + map.tile_margin)
                    print("Right Click ", pos, "Grid coordinates: ", row, column)
                    if row == player.x and column == player.y:
                        message("You see a strong, good looking... Wait a minute, that's <!blue>you.</>")
                        print(gs.tile_desc)
                    elif next((mob for mob in entities.mobs if (row, column) == (mob.x, mob.y)), 0) and \
                            map.grid[row][column]["isVisible"] == 1:
                        mob = next((mob for mob in entities.mobs if (row, column) == (mob.x, mob.y)), 0)
                        message(mob.examine)
                    else:
                        gs.tile_desc = map.grid[row][column]["name"]
                        message(gs.tile_desc)
                        print(gs.tile_desc)

            # Player Movement #####
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    print("Move Forward")
                    message(player.move("forward"))
                    print("Moved to", player.x, player.y)
                    enemy_ai_step()
                if event.key == pygame.K_s:
                    print("Move Back")
                    message(player.move("backward"))
                    print("Moved to", player.x, player.y)
                    enemy_ai_step()
                if event.key == pygame.K_a and pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                    print("Strafe Left")
                    player.strafe("left")
                    print("Moved to", player.x, player.y)
                    enemy_ai_step()
                elif event.key == pygame.K_a:
                    print("Turn Right")
                    player.rotate(-1)
                if event.key == pygame.K_d and pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                    print("Strafe Right")
                    player.strafe("right")
                    print("Moved to", player.x, player.y)
                    enemy_ai_step()
                elif event.key == pygame.K_d:
                    print("Turn Left")
                    player.rotate(1)
                if event.key == pygame.K_z:
                    print("You take a moment's rest...")
                    player.rest()
                if event.key == pygame.K_e:
                    print("Examining...")
                    try:
                        player.examine()
                    except IndexError:
                        print("Nope.")
                        message("You gaze into the <!green>Fathomless Void...</> and the Void gazes back!")
                if event.key == pygame.K_ESCAPE:
                    print("Shutting down...")
                    gs.running = False
                if event.key == pygame.K_SPACE:
                    player.interact()

                # Multikey Commands #####
                if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_LCTRL:
                    save()
                    message("Game Saved.")
                if event.key == pygame.K_x and pygame.key.get_mods() & pygame.KMOD_LCTRL:
                    load()
                    message("Game Loaded.")
                if event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_LCTRL:
                    map.generate()
                    message("Map Reset.")

                """ Game Testing Commands """
                if event.key == pygame.K_F1:
                    print("Create Random Monster")
                    createmonster('random')
                if event.key == pygame.K_F2:
                    print("Advancing AI")
                    enemy_ai_step()


if __name__ == '__main__':
    main()

pygame.display.quit()
pygame.quit()
print("Goodbye, thanks for playing!")
os._exit(1)
