'''
Created on Apr 2, 2009

@author: God
'''
import time
import pygame
import os
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((400, 300))

counter = 1
secondsPerFrame = 1.0 / 30
done = False
x = 0
y = 0

while not done:
    delayTime = time.clock()
    
    #handle input
    for event in pygame.event.get():
        pass
    
    pressedKeys = pygame.key.get_pressed()
    if pressedKeys[K_UP]:
        y -= 5
    if pressedKeys[K_DOWN]:
        y += 5
    if pressedKeys[K_LEFT]:
        x -= 5
    if pressedKeys[K_RIGHT]:
        x += 5
    if pressedKeys[K_ESCAPE]:
        done = True
    
    #draw things
    screen.fill((255,255,255))

    pygame.draw.circle(screen, (255, 0, 0), (x , y), 1)
    
    pygame.display.flip()
    
    counter += 1
    time.sleep(secondsPerFrame - (time.clock() - delayTime))
