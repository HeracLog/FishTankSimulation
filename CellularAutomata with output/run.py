import random
import pygame
import numpy
import cv2
import os

WIDTH : int = int(input("Enter width: "))
HEIGHT : int = int(input("Enter height: "))

PYGAME_WIDTH : int = 400
PYGAME_HEIGHT : int = 400

WIDTH_SCALEFACTOR : float = PYGAME_WIDTH // WIDTH
HEIGHT_SCALEFACTOR : float = PYGAME_HEIGHT // HEIGHT


VIDEO_OR_SNIPPETS : int = int(input("Show generations at snippets (1) or save a video of the evolution (2) or use pygame for continous output (3): "))

FISH_AGE : int = 10
SHARK_AGE : int = 50

REPRODUCTION_FACTOR = 4
SUFFOCATION_FACTOR = 8

SHARK_DEATH_FACTOR : int = 5

WATER_PROBABILITY = 0.5
FISH_PROBABILITY = 0.32
SHARK_PROBABILITY = 0.18

types : dict = {0:'Space',1:'Fish',2:'Shark'}

FOLDER_NAME = f"./{WIDTH}x{HEIGHT}-{FISH_PROBABILITY}x{SHARK_PROBABILITY}"

screen = pygame.display.set_mode((PYGAME_WIDTH, PYGAME_WIDTH))
pygame.display.set_caption("Simulation")

FISH_COLOR = (240,195,105)
SHARK_COLOR = (76,81,132)
WATER_COLOR = (0,255,255)

FPS = 60
clock = pygame.time.Clock()
def decideCell() -> int:
    probability = random.random()
    if probability < SHARK_PROBABILITY: return 2
    if probability < SHARK_PROBABILITY + FISH_PROBABILITY : return 1
    return 0

def display(evironment : list[list[int]]) -> None:
    for row in environment:
        for cell in row:
            print(cell, end=" ")
        print()
    print()

def saveAsImage(environment : list,gen : int) -> None:
    numpyEnvironment : numpy.ndarray = numpy.array(environment)
    for row in range(HEIGHT):
        for cell in range(WIDTH):
            if environment[row][cell] == 2:
                numpyEnvironment[row,cell] = 0
            elif environment[row][cell] == 1:
                numpyEnvironment[row,cell] = 127
            else:
                numpyEnvironment[row,cell] = 255
    cv2.imwrite(f"{FOLDER_NAME}/Gen{gen}.png",numpyEnvironment)

def applyRules(environment : list, environmentAge : list) -> list:
    newEnvironment : list = [environment[row][::] for row in range(HEIGHT)]
    for row in range(HEIGHT):
        for cell in range(WIDTH):
            neighbours : list = []
            if row +1 != HEIGHT:
                neighbours.append(environment[row+1][cell])
                if cell+1 != WIDTH:
                    neighbours.append(environment[row+1][cell+1])
                if cell-1 != -1:
                    neighbours.append(environment[row+1][cell-1])
                
            if row -1 != -1:
                neighbours.append(environment[row-1][cell])
                if cell+1 != WIDTH:
                    neighbours.append(environment[row-1][cell+1])
                if cell-1 != -1:
                    neighbours.append(environment[row-1][cell-1])
            if cell+1 != WIDTH:
                neighbours.append(environment[row][cell+1])
            if cell-1 != -1:
                neighbours.append(environment[row][cell-1])

            if environment[row][cell] == 0:
                if neighbours.count(2) >= REPRODUCTION_FACTOR:
                    newEnvironment[row][cell] = 2
                    environmentAge[row][cell] = 0
                if neighbours.count(1) >= REPRODUCTION_FACTOR:
                    newEnvironment[row][cell] = 1
                    environmentAge[row][cell] = 0
            if environment[row][cell] == 1:
                if neighbours.count(1) + neighbours.count(2) == SUFFOCATION_FACTOR:
                    newEnvironment[row][cell] = 0
                    environmentAge[row][cell] = 0
                if neighbours.count(2) >= SHARK_DEATH_FACTOR:
                    newEnvironment[row][cell] = 0
                    environmentAge[row][cell] = 0
            if environment[row][cell] == 2:
                if neighbours.count(1) + neighbours.count(2) == SUFFOCATION_FACTOR:
                    newEnvironment[row][cell] = 0
                    environmentAge[row][cell] = 0
    return newEnvironment

def replaceByAge(environment : list, environmentAge : list) :
    for row in range(HEIGHT):
        for cell in range(WIDTH):
            if types[environment[row][cell]] == "Fish" and environmentAge[row][cell] >= FISH_AGE:
                environment[row][cell] = 0
                environmentAge[row][cell] = 0
            if types[environment[row][cell]] == "Shark" and environmentAge[row][cell] >= SHARK_AGE:
                environment[row][cell] = 0
                environmentAge[row][cell] = 0
            if types[environment[row][cell]] == "Fish" or types[environment[row][cell]] == "Shark":
                environmentAge[row][cell] += 1
def drawToPyGame(environment : list) :
    xCummu : float = 0
    yCummu : float = 0
    for row in range(HEIGHT):
        for cell in range(WIDTH):
            match environment[row][cell]:
                case 0:
                    color = WATER_COLOR
                case 1:
                    color = FISH_COLOR
                case 2:
                    color = SHARK_COLOR
            pygame.draw.rect(screen,color,(xCummu,yCummu,WIDTH_SCALEFACTOR,HEIGHT_SCALEFACTOR))
            xCummu += WIDTH_SCALEFACTOR
        yCummu += HEIGHT_SCALEFACTOR
        xCummu = 0
    pygame.display.flip()
    clock.tick(FPS)
environment = [[decideCell() for _ in range(WIDTH)] for _ in range(HEIGHT)]
environmentAge = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

generation : int = 0

generationsToPrintAt : list = [0,10,100,500,1000]
pygame.init()
try:
    os.mkdir(FOLDER_NAME)
except Exception as e:
    print(f"Couldn't create folder",e)

match VIDEO_OR_SNIPPETS:
    case 1:
        while True:
            if generation in  generationsToPrintAt:
                print("Generation :", generation)
                display(environment)
                saveAsImage(environment,generation)
                if generation == generationsToPrintAt[-1]:
                    break
            environment = applyRules(environment,environmentAge)
            replaceByAge(environment,environmentAge)
            generation += 1
    case 2:
        while True:
            saveAsImage(environment,generation)
            if generation in  generationsToPrintAt:
                print("Generation :", generation)
                if generation == generationsToPrintAt[-1]:
                    def sortKey(string) -> int:
                        return int(string.replace("Gen","").replace(".png",""))

                    frames_dir = FOLDER_NAME

                    frames = [img for img in os.listdir(frames_dir) if img.endswith(".png")]

                    frames.sort(key = sortKey)

                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    video = cv2.VideoWriter(f'{FOLDER_NAME}.mp4', fourcc, 60.0, (HEIGHT, WIDTH))

                    for frame in frames:
                        img_path = os.path.join(frames_dir, frame)
                        img = cv2.imread(img_path)
                        video.write(img)

                    video.release()
                    break
            environment = applyRules(environment,environmentAge)
            replaceByAge(environment,environmentAge)
            generation += 1
    case 3:
        while True:
            drawToPyGame(environment)
            if generation in  generationsToPrintAt:
                print("Generation :", generation)
            environment = applyRules(environment,environmentAge)
            replaceByAge(environment,environmentAge)
            generation += 1