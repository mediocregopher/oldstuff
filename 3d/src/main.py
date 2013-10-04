'''
Created on Apr 26, 2009

@author: God
'''
import Things
import time
import pygame
import os
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((800, 600))


secondsPerFrame = 1.0 / 30
done = False

cam = Things.Camera(screen)
#test = [Things.Point(300,400,100),Things.Point(300,400,500)]
test = [Things.Box(Things.Point(400,400,400),Things.Point(500,500,500),(0,0,255)),
        Things.Box(Things.Point(600,400,400),Things.Point(700,500,500),(0,0,255))]
#test = [Things.Line(Things.Point(20,20,20),Things.Point(500,500,500),(255,0,0))]

while not done:
    delayTime = time.clock()
    
    #handle input
    for event in pygame.event.get():
        pass
    
    pressedKeys = pygame.key.get_pressed()
    if pressedKeys[K_w]:
        cam.move("up",5)
    if pressedKeys[K_s]:
        cam.move("down",5)
    if pressedKeys[K_a]:
        cam.move("left",5)
    if pressedKeys[K_d]:
        cam.move("right",5)
    if pressedKeys[K_q]:
        cam.z += 5
    if pressedKeys[K_e]:
        cam.z -= 5
#    if pressedKeys[K_UP]:
#        cam.rotate("up",1)
#    if pressedKeys[K_DOWN]:
#        cam.rotate("down",1)
    if pressedKeys[K_LEFT]:
        cam.rotate("left",1)
    if pressedKeys[K_RIGHT]:
        cam.rotate("right",1)
    if pressedKeys[K_ESCAPE]:
        done = True
    
    #draw things
    screen.fill((255,255,255))

    #pygame.draw.circle(screen, (255, 0, 0), (x , y), 1)
    #test.drawAbs(screen)
    for thing in test:
        cam.draw(thing)
    cam.drawCenter()
    
    font = pygame.font.Font(None, 17)
    xyText = font.render("XYZ:" + str(cam.x) + " " + str(cam.y) + " " + str(cam.z), True, (255,0,0), (255,255,255))
    pyText = font.render("Pitch/Yaw:" + str(cam.pitch) + " " + str(cam.yaw), True, (255,0,0), (255,255,255))
    # Create a rectangle
    xyRect = xyText.get_rect()
    pyRect = pyText.get_rect()
    # Center the rectangle
    xyRect.topright = screen.get_rect().topright
    pyRect.topright = xyRect.bottomright
    # Blit the text
    screen.blit(xyText, xyRect)
    screen.blit(pyText,pyRect)
    
    
    pygame.display.flip()
    
    time.sleep(secondsPerFrame - (time.clock() - delayTime))
