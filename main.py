#https://www.youtube.com/watch?v=lcC-jiCuDnQ&list=PL30AETbxgR-d03tf_HIr8-OA1gmClI3mE&index=2&t=103s
from asyncore import read
from copyreg import pickle
import enum
from click import confirmation_option
import pygame
import os, random, sys, neat, math
import pickle

pygame.init()

#globals
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

#images
RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]

JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))

SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]

BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

FONT = pygame.font.Font("freesansbold.ttf", 20)

#classes
class Dinosaur:
    X_POS = 90
    Y_POS = 310
    JUMP_VEL = 8.5

    def __init__(self, img=RUNNING[0]):
        self.image = img
        self.dino_run = True
        self.dino_jump = False
        self.jump_vel = self.JUMP_VEL
        self.rect = pygame.Rect(self.X_POS, self.Y_POS, img.get_width(), img.get_height())
        self.step_index = 0
        self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))

    def update (self):
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()
        if self.step_index >= 10:
            self.step_index = 0
    
    def jump (self):
        self.image = JUMPING
        if self.dino_jump:
            self.rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel <= -self.JUMP_VEL:
            self.dino_jump = False
            self.dino_run = True
            self.jump_vel = self.JUMP_VEL

    def run (self):
        self.image = RUNNING[self.step_index // 5]
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS
        self.step_index += 1

    def draw (self, SCREEN):
        #dino
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))
        #border
        pygame.draw.rect(SCREEN, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height),2)
        for obstacle in obstacles:
            pygame.draw.line(SCREEN, self.color, (self.rect.x + 55, self.rect.y + 11), obstacle.rect.center, 2)

class Obstacle:
    def __init__(self, image, number_of_cacti):
        self.image = image
        self.type = number_of_cacti
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update (self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()


    def draw (self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)

class SmallCactus(Obstacle):
    def __init__(self, image, number_of_cacti):
        super().__init__(image, number_of_cacti)
        self.rect.y = 325

class LargeCactus(Obstacle):
    def __init__(self, image, number_of_cacti):
        super().__init__(image, number_of_cacti)
        self.rect.y = 300

def remove(index):
    dinosaurs.pop(index)
    ge.pop(index)
    nets.pop(index)

def distance(pos_a, pos_b):
    dx = pos_a[0]-pos_b[0]
    dy = pos_a[1]-pos_b[1]
    return math.sqrt(dx**2+dy**2)

#main method - evolution of dinosaur genomes / fitness function / evolution function
def eval_genomes(genomes, config):
    global game_speed, x_pos_bg, y_pos_bg, points, dinosaurs, obstacles, ge, nets

    points = 0
    clock = pygame.time.Clock()

    obstacles = []
    dinosaurs = []
    ge = []#genomes
    nets = []#neuronet object of each dinosaur

    for genome_id, genome in genomes:
        dinosaurs.append(Dinosaur())
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    x_pos_bg = 0
    y_pos_bg = 380
    game_speed = 20

    def score():
        global points, game_speed
        points += 1
        if (points % 100) == 0:
            game_speed += 1
        text = FONT.render(f'Points: {str(points)}', True, (0,0,0))
        SCREEN.blit(text, (SCREEN_WIDTH-150,50))

    def statistics():
        global dinosaurs, game_speed, ge
        text_1 = FONT.render(f'Dinosaurs Alive: {str(len(dinosaurs))}', True, (0,0,0))
        text_2 = FONT.render(f'Generation: {population.generation}', True, (0,0,0))
        text_3 = FONT.render(f'Game Speed: {str(game_speed)}', True, (0,0,0))

        SCREEN.blit(text_1, (50, 450))
        SCREEN.blit(text_2, (50, 480))
        SCREEN.blit(text_3, (50, 510))

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg)) #bg
        SCREEN.blit(BG, (x_pos_bg + image_width, y_pos_bg)) #second bg, right next to the first
        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        x_pos_bg -= game_speed

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        SCREEN.fill((255,255,255))
        
        for dinosaur in dinosaurs:
            dinosaur.update()
            dinosaur.draw(SCREEN)
            


        if len(dinosaurs) == 0:
            break

        if len(obstacles) == 0:
            rand_int = random.randint(0,1)
            if rand_int == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS, random.randint(0,2)))    
            elif rand_int == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS, random.randint(0,2)))    
        
        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            for i, dinosaur in enumerate(dinosaurs):
                if dinosaur.rect.colliderect(obstacle.rect):
                    ge[i].fitness -= 1
                    remove (i)

        #user_input = pygame.key.get_pressed()

        for i, dinosaur in enumerate(dinosaurs):
            output = nets[i].activate((dinosaur.rect.y, distance((dinosaur.rect.x, dinosaur.rect.y), obstacle.rect.midtop)))
            #if user_input[pygame.K_SPACE]:
            if output[0] > 0.5 and dinosaur.rect.y == dinosaur.Y_POS:
                dinosaur.dino_jump = True
                dinosaur.dino_run = False
        statistics()
        score()
        for i, dinosaur in enumerate(dinosaurs):
            ge[i].fitness += 1
        background()
        clock.tick(30) 
        pygame.display.update()

def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    with open("real_winner.pkl", 'rb') as handle:
        last_win = pickle.load(handle)

    global population
    population = neat.Checkpointer.restore_checkpoint("neat-checkpoint-4")
    # population = neat.Population(config)    
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    population.add_reporter(neat.Checkpointer(1))

    population.run(eval_genomes, 5) #evolution function / fitness function
    win = population.best_genome
    #pickle.dump(winner, open('winner.pkl', 'wb'))
    #pickle.dump(win, open('real_winner.pkl', 'wb'))
    with open("real_winner.pkl", 'wb') as handle:
        pickle.dump(win, handle, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    run(config_path)