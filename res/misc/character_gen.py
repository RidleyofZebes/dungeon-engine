import pygame
from res.misc import colortag
from res.misc import pygame_textinput

pygame.init()

window_res = (1280, 720)

gw = pygame.display.set_mode(window_res)

clock = pygame.time.Clock()

font = pygame.font.Font('res/fonts/alkhemikal.ttf', 28)
statfont = pygame.font.Font('res/fonts/alkhemikal.ttf', 46)

statup = pygame.image.load('res/images/up.png')
statdn = pygame.image.load('res/images/down.png')
sex_m = pygame.image.load('res/images/male.png')
sex_f = pygame.image.load('res/images/female.png')

# Colors
black = (0, 0, 0)
dkgray = (32, 32, 32)
ltgray = (169, 169, 169)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

races = {"Human": "Human description",
         "Dwarf": "Dwarf description",
         "Elf":   "Elf description",
         "Orc":   "Orc description"}
jobs = {"Fighter":   "Fighter description",
        "Wizard":    "Wizard description",
        "Scoundrel": "Scoundrel description"}
stats = {"str": "Strength description",
         "dex": "Dexterity description",
         "con": "Constitution description",
         "wis": "Wisdom description",
         "cha": "Charisma description",
         "lck": "Luck description"}

class Hero:
    stat = {'str': 0, 'dex': 0, 'con': 0, 'wis': 0, 'cha': 0, 'lck': 0}
    race = 'Orc'
    job = 'Scoundrel'  # Can't use 'class' as a variable name, who knew?
    sex = 'male'
    statpool = 0

class Globals:
    description_text = "Information will appear here."
    sp_location = (window_res[0]//2-50, 355)

class ArrowToggle:
    def render(self):
        MAX_VALUE = 120

        if isinstance(self, StatPoint):
            self.items = [i for i in range(0, MAX_VALUE)]
            measure = [statfont.render(str(stat_value), False, white).get_size() for stat_value in range(0, MAX_VALUE)]
        else:
            measure = [statfont.render(str(stat_value), False, white).get_size() for stat_value in self.items]

        padding = 20
        max_word_length, word_height = max(measure)[0], max(measure)[1]
        self.box_width = statdn.get_size()[0] + padding + max_word_length + padding + statup.get_size()[0]

        label = font.render(self.label, False, white)
        label_rect = label.get_rect()
        label_rect.center = (self.box_width/2, statdn.get_size()[1] + padding)

        toggle_box = pygame.Surface((self.box_width, statdn.get_size()[1] + label.get_size()[1] + padding))

        stat_value = statfont.render(str(self.target), False, white)
        stat_value_rect = stat_value.get_rect()
        stat_value_rect.center = (self.box_width/2, statdn.get_size()[1]/2)

        self.subtext = toggle_box.blit(label, label_rect)
        self.describe = toggle_box.blit(stat_value, stat_value_rect)
        self.down = toggle_box.blit(statdn, (0, 0))
        self.up = toggle_box.blit(statup, (self.box_width - statup.get_size()[0], 0))

        box_bounds = gw.blit(toggle_box, (self.location[0] - self.box_width//2, self.location[1]))
        pygame.display.update()

        return pygame.Rect(box_bounds)


class StatPoint(ArrowToggle):
    def __init__(self, hero_adjustment, hero_value, item_set, description, location, *set_width):
        self.target = hero_adjustment
        self.hero_value = hero_value
        self.items = item_set
        self.label = description
        self.location = location
        self.down = None
        self.up = None
        self.describe = None
        self.subtext = None

    def update(self, pos):
        pos = pos[0]-(self.location[0] - self.box_width//2), pos[1]-self.location[1]
        if self.up.collidepoint(pos):
            if Hero.statpool >= 1:
                self.target = self.target + 1
                Hero.stat[self.hero_value] = Hero.stat[self.hero_value] + 1
                Hero.statpool = Hero.statpool - 1
                self.render()
                stat_pool(Globals.sp_location)
        if self.down.collidepoint(pos):
            if self.target >= 1:
                self.target = self.target - 1
                Hero.stat[self.hero_value] = Hero.stat[self.hero_value] - 1
                Hero.statpool = Hero.statpool + 1
                self.render()
                stat_pool(Globals.sp_location)
        if self.describe.collidepoint(pos) or self.subtext.collidepoint(pos):
            for key in stats:
                if self.hero_value == key:
                    message(stats[key])
        pygame.display.update()


class StatValue(ArrowToggle):
    def __init__(self, hero_adjustment, item_set, description, location, *set_width):
        self.target = hero_adjustment
        self.items = item_set
        self.label = description
        self.location = location
        self.down = None
        self.up = None
        self.describe = None
        self.subtext = None

    def update(self, pos):
        pos = pos[0]-(self.location[0] - self.box_width//2), pos[1]-self.location[1]
        temp = [key for key in self.items]
        index = temp.index(self.target)
        if self.down.collidepoint(pos):
            index = index + 1
            if index >= len(temp):
                index = 0
            self.target = temp[index]
            self.render()
        if self.up.collidepoint(pos):
            index = index - 1
            if index < 0:
                index = len(temp)-1
            self.target = temp[index]
            self.render()
        if self.describe.collidepoint(pos) or self.subtext.collidepoint(pos):
            for value in self.items:
                if self.target == value:
                    message(self.items.get(value))
        pygame.display.update()


def message(words, *location, color="0"):
    words = colortag.decode(words)
    max_width = 800
    description_box = pygame.Surface((1260, 250))
    pygame.draw.rect(description_box, white, (0, 0, 1260, 250), 0)
    pygame.draw.rect(description_box, black, (4, 4, 1252, 242), 0)
    if not location:
        pos = (10, 10)
    else:
        pos = location
    x, y = pos[0], pos[1]
    if color == "0":
        override_color = False
    else:
        override_color = True
    for word, set_color in words:
        if override_color:
            color = color
        else:
            color = set_color
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
        description_box.blit(each_word, (x, y))
        x += word_width + space
    pygame.display.update()
    gw.blit(description_box, (10, 460))

def stat_pool(location):
    pointsleft = statfont.render(str(Hero.statpool), False, white)
    points_text = font.render("Points", False, white)
    stat_pool_box = pygame.Surface((100, 100))
    pygame.draw.rect(stat_pool_box, white, (0, 0, 100, 100), 0)
    pygame.draw.rect(stat_pool_box, black, (4, 4, 92, 92), 0)
    points_text_rect = points_text.get_rect()
    points_text_rect.center = 50, 75
    pointsleft_rect = pointsleft.get_rect()
    pointsleft_rect.center = 50, 35
    stat_pool_box.blit(points_text, points_text_rect)
    stat_pool_box.blit(pointsleft, pointsleft_rect)
    gw.blit(stat_pool_box, Globals.sp_location)

def toggle_sex(location):
    if Hero.sex == "male":
        Hero.sex = "female"
    elif Hero.sex == "female":
        Hero.sex = "male"
    gender_icons = {"male": sex_m, "female": sex_f}
    pygame.draw.rect(gw, black, (location[0], location[1], 37, 42))
    gw.blit(gender_icons[Hero.sex], location)
    pygame.display.update()

# def statdisplay(text, midpoint, color=white):
#     stattext = statfont.render(text, False, color)
#     textsurf = stattext.get_rect()
#     textsurf.center = midpoint
#     gw.blit(stattext, textsurf)


def pg_button(button_position, button_text, *button_width, button_color=white): # Gets button X,Y and button label
    button_padding = 25 # Set padding between button text and border
    label = font.render(button_text, 0, button_color) # Renders button label
    button_size_x, button_size_y = label.get_size() # Sends button label dimensions to A,B variables
    if not button_width:
        gw.blit(label, ((button_position[0] + (button_padding / 2)), (button_position[1] + (button_padding / 2)))) # Outputs the button with default padding to the screen
        button_size = (button_position[0], button_position[1], (button_size_x + button_padding), (button_size_y + (button_padding * 0.8)))
    else:
        gw.blit(label, ((((button_position[0] + ((button_width[0] + button_padding) / 2))) - (button_size_x / 2)), (button_position[1] + (button_padding / 2)))) # Outputs the button with padding and centered text to the screen
        button_size = (button_position[0], button_position[1], (button_width[0] + button_padding), (button_size_y + (button_padding * 0.8)))
    pygame.draw.rect(gw, button_color, button_size, 4)
    return pygame.Rect(button_size)

def main(statpool):
    gw.fill(black)

    Hero.statpool = statpool
    statdialogue = font.render("What can you tell me about yourself?", False, white)
    gw.blit(statdialogue, (gw.get_rect().centerx - (statdialogue.get_rect()[2] / 2), 5))
    # submit = pg_button((975, 400), "Submit and Choose Name")
    stat_pool(Globals.sp_location)

    gender_icons = {"male": sex_m, "female": sex_f}
    sex_location = (window_res[0]//2 - (40//2), 295)
    render_sex = gw.blit(gender_icons[Hero.sex], sex_location)

    job = StatValue(Hero.job, jobs, "Class", (window_res[0]//3, 300))
    job.render()
    race = StatValue(Hero.race, races, "Race", (window_res[0]//1.5, 300))
    race.render()

    stg = StatPoint(Hero.stat['str'], "str", 0, "Strength", (window_res[0]//3, 60))
    stg.render()
    dex = StatPoint(Hero.stat['dex'], "dex", 0, "Dexterity", (window_res[0]//2, 60))
    dex.render()
    con = StatPoint(Hero.stat['con'], "con", 0, "Constitution", (window_res[0]//1.5, 60))
    con.render()
    wis = StatPoint(Hero.stat['wis'], "wis", 0, "Wisdom", (window_res[0]//3, 180))
    wis.render()
    cha = StatPoint(Hero.stat['cha'], "cha", 0, "Charisma", (window_res[0]//2, 180))
    cha.render()
    lck = StatPoint(Hero.stat['lck'], "lck", 0, "Luck", (window_res[0]//1.5, 180))
    lck.render()

    message(Globals.description_text)
    pygame.display.update()
    get_stats = True
    while get_stats:
        stat_adjust = pygame.event.get()
        if Hero.statpool != 0:
            buttoncolor = dkgray
        else:
            buttoncolor = white
        submit = pg_button((975, 400), "Submit and Choose Name", button_color=buttoncolor)
        pygame.display.update()
        for event in stat_adjust:
            if event.type == pygame.QUIT:
                get_stats = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()

                if job.render().collidepoint(pos):
                    job.update(pos)
                if race.render().collidepoint(pos):
                    race.update(pos)
                if render_sex.collidepoint(pos):
                    toggle_sex(sex_location)
                if stg.render().collidepoint(pos):
                    stg.update(pos)
                if dex.render().collidepoint(pos):
                    dex.update(pos)
                if con.render().collidepoint(pos):
                    con.update(pos)
                if wis.render().collidepoint(pos):
                    wis.update(pos)
                if cha.render().collidepoint(pos):
                    cha.update(pos)
                if lck.render().collidepoint(pos):
                    lck.update(pos)
                if submit.collidepoint(pos):
                    if Hero.statpool == 0:
                        get_stats = False

    get_name = True
    playername = pygame_textinput.TextInput(font_family="res/fonts/alkhemikal.ttf",
                                            font_size=72,
                                            text_color=(255, 255, 255),
                                            repeat_keys_initial_ms=1000,
                                            repeat_keys_interval_ms=1000)

    screen_damper = pygame.Surface((window_res[0], window_res[1]))
    screen_damper.fill((0, 0, 0))
    screen_damper.set_alpha(200)
    gw.blit(screen_damper, (0, 0))

    player_name_field = pygame.Surface((700, 250))
    pygame.draw.rect(player_name_field, white, (0, 0, 700, 250), 0)
    pygame.draw.rect(player_name_field, black, (4, 4, 692, 242), 0)
    gw.blit(player_name_field, (window_res[0]/2 - 350, window_res[1]/2 - 125))
    question = font.render("Ah, what was your name again?", 0, white)
    player_name_field.blit(question, (10, 10))
    pygame.display.update()

    while get_name:
        gw.blit(player_name_field, (window_res[0] / 2 - 350, window_res[1] / 2 - 125))

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()

        gw.blit(playername.get_surface(), (window_res[0]/2 - 320, window_res[1]/2 - 40))
        pygame.display.update()
        clock.tick(30)

        if len(playername.get_text()) > 20:
            question = font.render("That's a bit too long... Could you make it shorter?", 0, white)
            player_name_field.blit(question, (10, 218))
        else:
            question = font.render("That's a bit too long... Could you make it shorter?", 0, black)
            player_name_field.blit(question, (10, 218))

        if playername.update(events) and len(playername.get_text()) <= 20:
            Hero.name = playername.get_text()
            get_name = False

    return Hero.name, Hero.stat, Hero.race, Hero.job, Hero.sex


if __name__ == '__main__':
    main()

