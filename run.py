import random
from time import sleep
import numpy
import cv2
import os

WIDTH : int = int(input("Enter width: "))
HEIGHT : int = int(input("Enter height: "))

FISH_AGE : int = 10
SHARK_AGE : int = 50

REPRODUCTION_FACTOR = 4
SUFFOCATION_FACTOR = 8

SHARK_DEATH_FACTOR : int = 5

WATER_PROBABILITY = 0.5
FISH_PROBABILITY = 0.30
SHARK_PROBABILITY = 0.20

types : dict = {0:'Space',1:'Fish',2:'Shark'}

FOLDER_NAME = f"./{WIDTH}x{HEIGHT}-{FISH_PROBABILITY}x{SHARK_PROBABILITY}"
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

environment = [[decideCell() for _ in range(WIDTH)] for _ in range(HEIGHT)]
environmentAge = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

generation : int = 0

generationsToPrintAt : list = [0,10,100,500,1000]

try:
    os.mkdir(FOLDER_NAME)
except Exception as e:
    print(f"Couldn't create folder",e)

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