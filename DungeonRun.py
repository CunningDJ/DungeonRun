import sys
import sdl2
import sdl2.ext

import random
from math import sqrt
import time
import os

BLACK = sdl2.ext.Color(0, 0, 0)
WHITE = sdl2.ext.Color(255, 255, 255)
PLAYER_DEFAULT_SPEED = 6
MONSTER_DEFAULT_SPEED = 5
RESOURCES = sdl2.ext.Resources(__file__, "resources")
DOORS = sdl2.ext.Resources(__file__, "resources/doors")


class SoftwareRenderSystem(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderSystem, self).__init__(window)

    def render(self, components):
        sdl2.ext.fill(self.surface, BLACK)
        super(SoftwareRenderSystem, self).render(components)


class TextureRenderSystem(sdl2.ext.TextureSpriteRenderSystem):
    def __init__(self, renderer):
        super(TextureRenderSystem, self).__init__(renderer)
        self.renderer = renderer

    def render(self, components):
        tmp = self.renderer.color
        self.renderer.color = BLACK
        self.renderer.clear()
        self.renderer.color = tmp
        super(TextureRenderSystem, self).render(components)


class Timer(object):
    def __init__(self):
        super(Timer, self).__init__()
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def get_time(self):
        return time.time() - self.start_time()


class Borders(object):
    def __init__(self, minx, miny, maxx, maxy):
        super(Borders, self).__init__()
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy


class Move(object):
    def __init__(self, moveKeys):
        super(Move, self).__init__()
        self.up = moveKeys[0]
        self.right = moveKeys[1]
        self.down = moveKeys[2]
        self.left = moveKeys[3]

    def __iter__(self):
        moves = (self.up,self.right,self.down,self.left)
        for move in moves:
            yield move


class MovementSystem(sdl2.ext.Applicator):
    def __init__(self, borders):
        super(MovementSystem, self).__init__()
        self.componenttypes = Velocity, sdl2.ext.Sprite
        self.minx = borders.minx
        self.miny = borders.miny
        self.maxx = borders.maxx
        self.maxy = borders.maxy

    def process(self, world, componentsets):

        for velocity, sprite in componentsets:
            swidth, sheight = sprite.size
            sprite.x += velocity.vx
            sprite.y += velocity.vy

            sprite.x = max(self.minx, sprite.x)
            sprite.y = max(self.miny, sprite.y)

            pmaxx = sprite.x + swidth
            pmaxy = sprite.y + sheight
            if pmaxx > self.maxx:
                sprite.x = self.maxx - swidth
            if pmaxy > self.maxy:
                sprite.y = self.maxy - sheight


class DoorSystem(sdl2.ext.Applicator):
    def __init__(self, borders):
        super(DoorSystem, self).__init__()
        self.componenttypes = (sdl2.ext.Sprite,PlayerData)
        self.players = None
        self.door = None
        self.coins = None
        self.borders = borders
        self.door_sprites = None
        self.monster = None
        self.coin_sys = None

    def _enter(self, comp):
        sprite = comp[0]
        if sprite not in [p.sprite for p in self.players]:
            return False

        left, top, right, bottom = self.door.sprite.area
        p_left, p_top, p_right, p_bottom = sprite.area

        entered = (left < p_right and right > p_left
                 and top < p_bottom and bottom > p_top)
        return entered

    def relocate_door(self):
        door = self.door
        borders = self.borders
        door.sprite = random.choice(self.door_sprites)
        while True:
            new_x,new_y = (random.randrange(borders.minx, borders.maxx-door.sprite.size[0]),random.randrange(borders.miny, borders.maxy-door.sprite.size[1]))
            if abs(door.sprite.x - new_x) > 80 and abs(door.sprite.y - new_y) > 80:
                door.sprite.x,door.sprite.y = new_x, new_y
                break

    def relocate_coins(self):
        self.coin_sys.new_batch(15)

    def relocate_monster(self):
        monster = self.monster
        players = self.players
        borders = self.borders

        while True:
            good_dist = True
            new_x,new_y = (random.randrange(borders.minx, borders.maxx-monster.sprite.size[0]),random.randrange(borders.miny, borders.maxy-monster.sprite.size[1]))
            for p in players:
                dist = sqrt(abs(p.sprite.x-new_x)**2+abs(p.sprite.y-new_y)**2)
                if dist < 350:
                    good_dist = False
                    break

            if good_dist:
                monster.sprite.x, monster.sprite.y = new_x, new_y
                monster.velocity.vx, monster.velocity.vy = 0,0
                return

    def process(self, world, componentsets):
        playerdata_players_entered = [comp[1] for comp in componentsets if self._enter(comp)]

        if len(playerdata_players_entered) > 0:
            # move door
            self.relocate_door()
            self.relocate_coins()
            self.relocate_monster()
            for pd in playerdata_players_entered:
                pd.points += 5


class Door(sdl2.ext.Entity):
    def __init__(self, world, sprite, position):
        self.sprite = sprite
        self.sprite.position = position


class Velocity(object):
    def __init__(self):
        super(Velocity, self).__init__()
        self.vx = 0
        self.vy = 0


class Player(sdl2.ext.Entity):
    def __init__(self, world, sprite, moveKeys, posx=0, posy=0, ai=False):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.velocity = Velocity()
        self.playerdata = PlayerData()
        self.playerdata.ai = ai
        self.move = Move(moveKeys)


class PlayerData(object):
    def __init__(self):
        super(PlayerData, self).__init__()
        self.ai = False
        self.points = 0


class MonsterAI(sdl2.ext.Applicator):
    def __init__(self):
        super(MonsterAI, self).__init__()
        self.componenttypes = sdl2.ext.Sprite, Velocity
        self.monster = None
        self.players = None

    def process(self, world, componentsets):
        monster = self.monster

        left, top, right, bottom = monster.sprite.area


        for sprite, vel in componentsets:
            closest_player_sprite = None
            closest_dist = 99999
            for p in self.players:
                if sprite == p.sprite:
                    p_left, p_top, p_right, p_bottom = sprite.area
                    caught = (left < p_right and right > p_left and top < p_bottom and bottom > p_top)

                    if caught:
                        print('caught')
                        monster.velocity.vx, monster.velocity.vy = 0,0
                        #world.delete(p)        #TODO kill player
                    else:
                        dist = sqrt(abs(sprite.x-monster.sprite.x)**2+abs(sprite.y-monster.sprite.y)**2)
                        if dist < closest_dist:
                            closest_dist = dist
                            closest_player_sprite = sprite
            visible = closest_dist < monster.monsterdata.sight_range
            if visible:
                monster.advance(closest_player_sprite)


class Monster(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.velocity = Velocity()
        self.velocity.vx = 0
        self.velocity.vy = 0
        self.monsterdata = MonsterData()

    def advance(self, player_sprite):
        player_sprite = player_sprite
        if player_sprite.x < self.sprite.x:
            self.velocity.vx = -self.monsterdata.top_speed
        elif player_sprite.x > self.sprite.x:
            self.velocity.vx = self.monsterdata.top_speed
        else:
            self.velocity.vx = 0

        if player_sprite.y < self.sprite.y:
            self.velocity.vy = -self.monsterdata.top_speed
        elif player_sprite.y > self.sprite.y:
            self.velocity.vy = self.monsterdata.top_speed
        else:
            self.velocity.vy = 0


class MonsterData(object):
    def __init__(self, top_speed=MONSTER_DEFAULT_SPEED, sight_range=300):
        self.top_speed = top_speed
        self.sight_range = sight_range


class CoinSystem(sdl2.ext.Applicator):
    def __init__(self):
        super(CoinSystem, self).__init__()
        self.componenttypes = (sdl2.ext.Sprite,)
        self.coins = None
        self.players = None
        self.borders = None
        self.world = None

    def new_batch(self, num_coins):
        for coin in self.coins:
            coin.relocate()

        if len(self.coins) < num_coins:
            for count in range(num_coins-len(self.coins)):
                self.coins.append(Coin(self.world,self.coin_image,self.borders))

    def _pick_up(self, p_sprite, c_sprite):
        p_left, p_top, p_right, p_bottom = p_sprite.area
        c_left, c_top, c_right, c_bottom =  c_sprite.area
        picked_up = (c_left < p_right and c_right > p_left
                 and c_top < p_bottom and c_bottom > p_top)
        return picked_up

    def process(self,world, componentsets):
        for comp in componentsets:
            pass
        for coin in self.coins:
            for player in self.players:
                if self._pick_up(player.sprite, coin.sprite):
                    #world.delete(coin)     # TODO coin deletion
                    player.playerdata.points += 5
                    return


class Coin(sdl2.ext.Entity):
    def __init__(self, world, sprite, borders):
        self.sprite = sprite
        self.borders = borders
        self.sprite.x = random.randrange(borders.minx,borders.maxx-self.sprite.size[0])
        self.sprite.y = random.randrange(borders.miny,borders.maxy-self.sprite.size[1])

    def relocate(self):
        borders = self.borders
        self.sprite.x = random.randrange(borders.minx,borders.maxx-self.sprite.size[0])
        self.sprite.y = random.randrange(borders.miny,borders.maxy-self.sprite.size[1])


def run():
    sdl2.ext.init()
    borders = Borders(0,0,800,600)
    window = sdl2.ext.Window("DUNGEON RUN", size=(borders.maxx,borders.maxy))
    window.show()

    if "-hardware" in sys.argv:
        print("Using hardware acceleration")
        renderer = sdl2.ext.Renderer(window)
        factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=renderer)
    else:
        print("Using software rendering")
        factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)

    # populating the list of door sprites
    door_sprites = []
    for file in os.listdir('{}/resources/doors'.format(os.getcwd())):
        door_sprites.append(factory.from_image(DOORS.get_path(file)))


    p1_sprite = factory.from_image(RESOURCES.get_path("player1.png"))
    p2_sprite = factory.from_image(RESOURCES.get_path("player2.png"))
    monster_sprite = factory.from_image(RESOURCES.get_path("monster.png"))
    door_sprite = factory.from_image(DOORS.get_path("door-generic.png"))

    world = sdl2.ext.World()

    movement = MovementSystem(borders)
    door_sys = DoorSystem(borders)
    monster_ai = MonsterAI()
    coin_sys = CoinSystem()

    if factory.sprite_type == sdl2.ext.SOFTWARE:
        spriterenderer = SoftwareRenderSystem(window)
    else:
        spriterenderer = TextureRenderSystem(renderer)

    world.add_system(movement)
    world.add_system(spriterenderer)
    world.add_system(door_sys)
    world.add_system(monster_ai)
    world.add_system(coin_sys)

    monster = Monster(world, monster_sprite,int(borders.maxx/2), int(borders.maxy/2))
    player1 = Player(world, p1_sprite, (sdl2.SDLK_UP,sdl2.SDLK_RIGHT,sdl2.SDLK_DOWN,sdl2.SDLK_LEFT),0, int(borders.maxy-(2*p1_sprite.size[1])))
    player2 = Player(world, p2_sprite, (sdl2.SDLK_w,sdl2.SDLK_d,sdl2.SDLK_s,sdl2.SDLK_a),int(p1_sprite.size[0]), int(borders.maxy-p2_sprite.size[1]))
    players = (player1,player2)
    door = Door(world, door_sprite,(30,30))

    timer = Timer()

    coins = []
    coin_image = RESOURCES.get_path("coin.png")
    for count in range(15):
        coin = Coin(world, factory.from_image(coin_image), borders)
        coins.append(coin)

    coin_sys.borders = borders
    coin_sys.world = world
    coin_sys.coin_image = coin_image
    coin_sys.coins = coins
    coin_sys.players = players

    door_sys.players = players
    door_sys.monster = monster
    door_sys.door = door
    door_sys.coins = coins
    door_sys.coin_sys = coin_sys
    door_sys.door_sprites = door_sprites

    monster_ai.monster = monster
    monster_ai.players = players

    running = True
    timer.start()
    while running:
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
            # Player movement processing
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym in player1.move:
                    if event.key.keysym.sym == player1.move.up:
                        player1.velocity.vy = -PLAYER_DEFAULT_SPEED
                    elif event.key.keysym.sym == player1.move.down:
                        player1.velocity.vy = PLAYER_DEFAULT_SPEED
                    elif event.key.keysym.sym == player1.move.right:
                        player1.velocity.vx = PLAYER_DEFAULT_SPEED
                    elif event.key.keysym.sym == player1.move.left:
                        player1.velocity.vx = -PLAYER_DEFAULT_SPEED
                elif event.key.keysym.sym in player2.move:
                    if event.key.keysym.sym == player2.move.up:
                        player2.velocity.vy = -PLAYER_DEFAULT_SPEED
                    elif event.key.keysym.sym == player2.move.down:
                        player2.velocity.vy = PLAYER_DEFAULT_SPEED
                    elif event.key.keysym.sym == player2.move.right:
                        player2.velocity.vx = PLAYER_DEFAULT_SPEED
                    elif event.key.keysym.sym == player2.move.left:
                        player2.velocity.vx = -PLAYER_DEFAULT_SPEED
            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym in (player1.move.up, player1.move.down):
                    player1.velocity.vy = 0
                if event.key.keysym.sym in (player1.move.right, player1.move.left):
                    player1.velocity.vx = 0
                if event.key.keysym.sym in (player2.move.up, player2.move.down):
                    player2.velocity.vy = 0
                if event.key.keysym.sym in (player2.move.right, player2.move.left):
                    player2.velocity.vx = 0
        sdl2.SDL_Delay(10)
        win_title = 'DUNGEON RUN | P1: {} P2: {}'.format(player1.playerdata.points, player2.playerdata.points)
        window.title = win_title
        world.process()


if __name__ == "__main__":
    sys.exit(run())
