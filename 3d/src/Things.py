'''
Created on Apr 26, 2009

@author: God
'''
import pygame
import math

class Camera():
    
    def __init__(self,screen):
        self.x = 0
        self.y = 0
        self.z = 0
        self.pitch = math.pi / 2
        self.yaw = 0
        self.fishtheta = 25 * (math.pi / 180)
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.screen = screen
        
    def rotate(self,dir,amount):
        if dir == "up":
            self.pitch += amount * (math.pi / 180)
        elif dir == "down":
            self.pitch -= amount * (math.pi / 180)
        elif dir == "left":
            self.yaw += amount * (math.pi / 180)
        elif dir == "right":
            self.yaw -= amount * (math.pi / 180)
            
    def move(self,dir,amount):
        if dir == "up":
            self.y += amount
        elif dir == "down":
            self.y -= amount
        elif dir == "left":
            self.x -= amount * math.cos(self.yaw)
            self.z -= amount * math.sin(self.yaw)
        elif dir == "right":
            self.x += amount * math.cos(self.yaw)
            self.z += amount * math.sin(self.yaw)


    def draw(self,object):
        temp = []
        for point in object.points:
            if 1: #point.z > self.z:
                point.kosher = True
                tempx = (point.x - self.x) + self.width / 2
                tempy = (point.y - self.y) + self.height / 2
                tempz = point.z - self.z
                
                distancex = math.sqrt(math.pow((point.x - self.x),2)+math.pow((point.z - self.z),2))
                try:
                    angleBetweenx = math.atan(float(point.z - self.z)/float(point.x - self.x))
                except ZeroDivisionError:
                    angleBetweenx = math.radians(90)
                angleBetweenx += math.radians(180) * int(angleBetweenx < 0)
                trueAnglex = angleBetweenx - self.yaw
             
                distancey = math.sqrt(math.pow((point.y - self.y),2)+math.pow((point.z - self.z),2))
                try:
                    angleBetweeny = math.atan(float(point.z - self.z)/float(point.y - self.y))
                except ZeroDivisionError:
                    angleBetweeny = math.radians(90) 
                angleBetweeny += math.radians(180) * int(angleBetweeny < 0)
                trueAngley = angleBetweeny - self.pitch
   
                tempx = (self.width / 2) + distancex * math.cos(trueAnglex)
                tempz = distancex * math.sin(trueAnglex)
                tempy = (self.height / 2) + distancey * math.sin(trueAngley)
                
                zwidth = tempz * math.tan(self.fishtheta) * 2 + self.width
                zheight = tempz * math.tan(self.fishtheta) * 2 + self.height
                ratiox = 1 - self.width / zwidth
                ratioy = 1 - self.height / zheight

                tempx -= (tempx - self.width / 2) * ratiox
                tempy -= (tempy - self.height / 2) * ratioy
                            
                temp.append((tempx, tempy))
            else:
                point.kosher = False
                
        object.draw(self.screen,temp)
            
    def drawCenter(self):
        pygame.draw.circle(self.screen, (0, 0, 255), (int(self.x - (self.x - self.width / 2)) , int(self.y - (self.y - self.height / 2))), 1)

class Point():

    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
        self.kosher = True
        self.points = [self]
        
    def draw(self,screen,point):
         pygame.draw.circle(screen, (255, 0, 0), (point[0][0] , point[0][1]), 1)
    
    def drawAbs(self,screen):
         pygame.draw.circle(screen, (255, 0, 0), (self.x , self.y), 1)
         
    def tuple(self):
        return (self.x,self.y,self.z)
         
class Line():
    
    def __init__(self,point1,point2,color):
        self.points = [point1,point2]
        self.color = color
        
    def draw(self,screen,points):
        pygame.draw.line(screen,self.color,points[0],points[1])
        font = pygame.font.Font(None, 17)
        xyText1 = font.render("XY:" + str(points[0][0]) + " " + str(points[0][1]), True, (255,0,0), (255,255,255))
        xyRect1 = xyText1.get_rect()
        xyRect1.topleft = screen.get_rect().topleft
        screen.blit(xyText1, xyRect1)
        
        xyText2 = font.render("XY:" + str(points[1][0]) + " " + str(points[1][1]), True, (255,0,0), (255,255,255))
        xyRect2 = xyText2.get_rect()
        xyRect2.topleft = xyRect1.bottomleft
        screen.blit(xyText2, xyRect2)
        
        xyText3 = font.render("XYZ:" + str(self.points[0].x) + " " + str(self.points[0].y) + " " + str(self.points[0].z), True, (255,0,0), (255,255,255))
        xyRect3 = xyText3.get_rect()
        xyRect3.topleft = xyRect2.bottomleft
        screen.blit(xyText3, xyRect3)
        
        xyText4 = font.render("XY:" + str(self.points[1].x) + " " + str(self.points[1].y) + " " + str(self.points[1].z), True, (255,0,0), (255,255,255))
        xyRect4 = xyText4.get_rect()
        xyRect4.topleft = xyRect3.bottomleft
        screen.blit(xyText4, xyRect4)
        
class Box():
    
    def __init__(self,point1,point2,color):
        self.points = [point1,point2]
        self.color = color
        
        point3 = Point(point1.x,point2.y,point1.z)
        point4 = Point(point2.x,point1.y,point2.z)
        point5 = Point(point2.x,point2.y,point1.z)
        point6 = Point(point1.x,point1.y,point2.z)
        point7 = Point(point2.x,point1.y,point1.z)
        point8 = Point(point1.x,point2.y,point2.z)
        
        self.points.extend([point3,point4,point5,point6,point7,point8])
        
    def draw(self,screen,points):
        for i in range(0,len(points)):
            for j in range(0,len(points)):
                if abs(j - i) > 1:
                    pygame.draw.line(screen,self.color,points[i],points[j])