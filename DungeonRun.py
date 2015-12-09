import sys
import sdl2
import sdl2.ext

BLACK = sdl2.ext.Color(0, 0, 0)
WHITE = sdl2.ext.Color(255, 255, 255)
PLAYER_DEFAULT_SPEED = 6
RESOURCES = sdl2.ext.Resources(__file__, "resources")

class MovementSystem(sdl2.ext.Applicator):
    def __init__(self, minx, miny, maxx, maxy):
        super(MovementSystem, self).__init__()
        self.componenttypes = Velocity, sdl2.ext.Sprite
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy

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


class Velocity(object):
    def __init__(self):
        super(Velocity, self).__init__()
        self.vx = 0
        self.vy = 0


class PlayerData(object):
    def __init__(self):
        super(PlayerData, self).__init__()
        self.ai = False
        self.points = 0


class Player(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0, ai=False):
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.velocity = Velocity()
        self.playerdata = PlayerData()
        self.playerdata.ai = ai

def run():
    sdl2.ext.init()
    window = sdl2.ext.Window("DUNGEON RUN", size=(800, 600))
    window.show()

    if "-hardware" in sys.argv:
        print("Using hardware acceleration")
        renderer = sdl2.ext.Renderer(window)
        factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=renderer)
    else:
        print("Using software rendering")
        factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)

    #p1_sprite = factory.from_image(RESOURCES.get_path("monster.png"))  #TODO debug image issue
    p1_sprite = factory.from_color(WHITE, size=(20, 100))
    #sp_paddle2 = factory.from_color(WHITE, size=(20, 100))
    #sp_ball = factory.from_color(WHITE, size=(20, 20))

    world = sdl2.ext.World()

    movement = MovementSystem(0, 0, 800, 600)
    #collision = CollisionSystem(0, 0, 800, 600)
    #aicontroller = TrackingAIController(0, 600)
    if factory.sprite_type == sdl2.ext.SOFTWARE:
        spriterenderer = SoftwareRenderSystem(window)
    else:
        spriterenderer = TextureRenderSystem(renderer)

    #world.add_system(aicontroller)
    world.add_system(movement)
    #world.add_system(collision)
    world.add_system(spriterenderer)

    player1 = Player(world, p1_sprite, 0, 250)
    '''
    player2 = Player(world, sp_paddle2, 780, 250, True)
    ball = Ball(world, sp_ball, 390, 290)
    ball.velocity.vx = -BALL_SPEED
    collision.ball = ball
    aicontroller.ball = ball
    '''
    running = True
    while running:
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_UP:
                    player1.velocity.vy = -PLAYER_DEFAULT_SPEED
                elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                    player1.velocity.vy = PLAYER_DEFAULT_SPEED
                elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                    player1.velocity.vx = PLAYER_DEFAULT_SPEED
                elif event.key.keysym.sym == sdl2.SDLK_LEFT:
                    player1.velocity.vx = -PLAYER_DEFAULT_SPEED
            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym in (sdl2.SDLK_UP, sdl2.SDLK_DOWN):
                    player1.velocity.vy = 0
                if event.key.keysym.sym in (sdl2.SDLK_RIGHT, sdl2.SDLK_LEFT):
                    player1.velocity.vx = 0
        sdl2.SDL_Delay(10)
        world.process()


if __name__ == "__main__":
    sys.exit(run())


