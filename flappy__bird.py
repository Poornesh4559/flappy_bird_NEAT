import time
import random
import pygame , sys
import neat
import os

pygame.font.init()


WIN_WIDTH = 600
WIN_HEIGHT = 800
FLOOR =730
STAT_FONT = pygame.font.SysFont("comicsans", 50)

WIN = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
pygame.display.set_caption("Flappy bird")

BIRDS_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")).convert_alpha())
BG_IMG = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (600, 900))
BASE_IMG =pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")).convert_alpha())

#BG_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))



gen=0

class Bird:
    IMGS = BIRDS_IMGS
    MAX_ROTATION = 25
    ROT_VEL =20
    ANIMATION_TIME = 5


    def __init__(self, x, y):
        self.x=x
        self.y=y
        self.tilt= 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def move(self):
        """
        make the bird move
        :return: None
        """
        self.tick_count += 1

        # for downward acceleration
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  # calculate displacement

        # terminal velocity
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:  # tilt down
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y



    def draw(self, win):
        self.img_count += 1

        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 +1:
            self.img = self.IMGS[0]
            self.img_count=0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count  = self.ANIMATION_TIME*2


        # tilt the bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

        
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe():
    GAP = 200
    VEL = 5
    def __init__(self, x):
        self.x= x
        self.height = 0
        self.gap =100 

        self. top = 0
        self.bottom =0
        self.PIPE_TOP =pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG


        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL


    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird, win):
        bird_mask = bird.get_mask()
        top_mask=pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask=pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x- bird.x, self.top - round(bird.y))
        bottom_offset = (self.x- bird.x, self.bottom - round(bird.y))


        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)


        if t_point or b_point:
            return True

        return False




class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y =y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.WIDTH + self.x1 <0:
            self.x1 = self.x2 + self.WIDTH

        if self.WIDTH + self.x2 <0:
            self.x2 = self.x1 + self.WIDTH

    

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)





def draw_window(win, birds, pipes, base, score, gen, pipe_ind):

    if gen == 0:
        gen = 1
    win.blit(BG_IMG, (0,0))


    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)  


    text =  STAT_FONT.render("Score: " + str(score), 1,(255,255,255))
    win.blit(text, (WIN_WIDTH -10 - text.get_width(), 10))


    for bird in birds:
        bird.draw(win)
    
    score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
    win.blit(score_label, (10, 10))

    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(score_label, (10, 50))

    
    pygame.display.update()



def main(genomes, config):

    global WIN, gen
    win =WIN
    gen += 1

    
    nets=[]
    ge=[]
    birds =[]
    for _, g in genomes:
        g.fitness = 0
        net  = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(g)



    base = Base(FLOOR)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock  = pygame.time.Clock()
    score = 0


    run =True
    while run and len(birds) > 0:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                run = False
                sys.exit()
                
        


        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # determine whether to use the first or second
                pipe_ind = 1 
       

        for x, bird in enumerate(birds):  # give each bird a fitness of 0.1 for each frame it stays alive
            bird.move()
            ge[x].fitness += 0.1

            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                bird.jump()
        #for x, bird in enumerate(birds):
         #   bird.move()
          #  ge[x].fitness += 0.1

           # output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            #if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
             #   bird.jump()

                                                      
        base.move()
        
        add_pipe = False
        rem=[]

        for pipe in pipes:
            pipe.move()
            for x,bird in enumerate(birds):
                if pipe.collide(bird, win):
                    ge[x].fitness -=1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

            if pipe.x + pipe.PIPE_TOP.get_width() <0:
                rem.append(pipe)
    
            
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True


            
           
        

        if add_pipe:
            score +=1
            for g in ge :
                g.fitness += 5
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem :
            pipes.remove(r)

        
        for x, bird in enumerate(birds):
             if bird.y + bird.img.get_height()-10 >= 730 or bird.y < -50:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)



        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind) 

    


def run(config_file):

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            config_file)
                         

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(main, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))



if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path =os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
