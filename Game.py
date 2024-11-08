from random import randint
from os.path import join

from Components import *
from EntityManager import EntityManager
import pygame
from pygame import Vector2
import random



class Game:
    def __init__(self, w_width, w_height, title: str, hardmode : bool, debug : bool):
        self.debug = debug

        #regular variable stuff
        self.m_score = 0
        self.m_currentFrame = 0
        self.m_running = True
        self.clock = pygame.time.Clock()

        #pygame audio
        pygame.mixer.init()
        self.sounds = {
            "flap": pygame.mixer.Sound(join("audio", "wing.wav")),
            "collision": pygame.mixer.Sound(join("audio", "hit.wav")),
            "score": pygame.mixer.Sound(join("audio", "point.wav"))
        }
        for sound in self.sounds.keys():
            self.sounds[sound].set_volume(0.3)

        #pygame display stuff
        pygame.init()
        self.display_surface = pygame.display.set_mode((w_width, w_height))
        pygame.display.set_caption(title)

        #flappy assets this is so ugly
        downflap = pygame.image.load(join('images','downflap.png')).convert_alpha()
        midflap = pygame.image.load(join('images', 'midflap.png')).convert_alpha()
        upflap = pygame.image.load(join('images', 'upflap.png')).convert_alpha()
        self.pipe =pygame.image.load(join('images', 'pipe.png')).convert_alpha()

        self.bg_surf = pygame.image.load(join('images', 'background.png')).convert_alpha()
        self.bg_surf = pygame.transform.scale(self.bg_surf, self.display_surface.get_size())
        self.asset_list = [downflap, midflap, upflap]
        self.asset_choice = 0

        #entitymananger
        self.m_entityManager = EntityManager()
        self.player = self.spawnPlayer()
        self.cube = self.spawnGravityCube()
        self.flap = False

        #maybe temp player speed
        self.p_speed = 5.5

        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()

        # spawn timer
        self.last_spawn_time = 0
        self.spawn_delay = 70

        #dead screen
        self.dead = False
        self.hardmode = hardmode

        #temp color cycle
        self.color_cycle = [pygame.Color("red"), pygame.Color("green"), pygame.Color("blue")]
        self.color_choice = 0


    def run(self):
        while self.m_running:
            if not self.dead:
                self.m_entityManager.update()
                self.sMovement()
                self.sCollisions()
                self.sPoleSpawner()
                self.sPoleKiller()
                self.sUserInput()
                self.sTimerHandler()
                self.sScore()
                self.sRender()
                self.m_currentFrame += 1
            else:
                self.sUserInput()
                self.sTimerHandler()
                self.sRender()
                self.m_currentFrame += 1


    def spawnPlayer(self):
        player = self.m_entityManager.addEntity("player")
        spawn_point = Vector2(pygame.display.get_window_size()[0]/2,pygame.display.get_window_size()[1]/2)
        player.cTransform = CTransform(spawn_point, Vector2(0,0), 0.0)
        player.cShape = CShape(spawn_point, 50, 50, pygame.Color("red"))
        player.cInput = CInput()
        player.cTimer = CTimer(30)
        player.cTimer.run = True
        return player

    def spawnGravityCube(self):
        cube = self.m_entityManager.addEntity("cube")
        spawn_point = Vector2(-100 + pygame.display.get_window_size()[0]/2, 0)
        cube.cTransform = CTransform(spawn_point,Vector2(0,0), 5.0)
        cube.cShape = CShape(spawn_point, 68,48,pygame.Color("blue"))
        cube.cInput = CInput()
        cube.cGravity = CGravity(Vector2(0,0.65))
        cube.cTimer = CTimer(5)
        cube.cTimer.count = cube.cTimer.end
        cube.cTimer.run = True
        cube.cAnimation = CAnimation
        for i in range(len(self.asset_list)):
            self.asset_list[i] = pygame.transform.scale(self.asset_list[i], cube.cShape.surf.get_size())
        cube.cShape = CShape(spawn_point, 55, 48, pygame.Color("blue"))
        cube.cAnimation.anime_list = self.asset_list
        return cube


    def sMovement(self):
        if self.cube.cShape:
            if self.cube.cShape.rect.bottom >= self.display_surface.get_height():
                self.cube.cTransform.velocity = Vector2(0,0)
                self.cube.cShape.rect.bottom = self.display_surface.get_height()
                self.cube.cTransform.pos = self.cube.cShape.rect.center
        #PLAYER MOVEMENT CALCULATIONS
        self.player.cTransform.velocity = Vector2(0.0,0.0)
        if self.player.cInput.up:
            self.player.cTransform.velocity[1] = -1
        if self.player.cInput.down:
            self.player.cTransform.velocity[1] = 1
        if self.player.cInput.left:
            self.player.cTransform.velocity[0] = -1
        if self.player.cInput.right:
            self.player.cTransform.velocity[0] = 1
        if self.player.cTransform.velocity.length()>0:
            self.player.cTransform.velocity = self.player.cTransform.velocity.normalize() * self.p_speed
        for e in self.m_entityManager.getEntities():
            if e.cGravity:
                e.cTransform.velocity += e.cGravity.gravity


        if self.flap:
            self.cube.cTransform.velocity = Vector2(0,-12)
            self.flap = False

        if self.cube.cTransform:
            velocity_y = self.cube.cTransform.velocity.y
            self.cube.cTransform.angle = max(-30, min(30, velocity_y*3))

        for e in self.m_entityManager.getEntities():
            if e.cTransform:
                e.cTransform.pos += e.cTransform.velocity

        #if self.cube.cShape.rec

    def sCollisions(self):
        for e in self.m_entityManager.getEntities("pole")+self.m_entityManager.getEntities("pole_top"):
            y_check_cube = (self.cube.cShape.rect.height/2) + (e.cShape.rect.height/2)>abs(self.cube.cShape.rect.center[1]-e.cShape.rect.center[1])
            x_check_cube = (self.cube.cShape.rect.width/2) + (e.cShape.rect.width/2)>abs(self.cube.cShape.rect.center[0]-e.cShape.rect.center[0])
            y_check_player = (self.player.cShape.rect.height / 2) + (e.cShape.rect.height / 2) > abs(
                self.player.cShape.rect.center[1] - e.cShape.rect.center[1])
            x_check_player = (self.player.cShape.rect.width / 2) + (e.cShape.rect.width / 2) > abs(
                self.player.cShape.rect.center[0] - e.cShape.rect.center[0])

            if y_check_cube and x_check_cube or self.hardmode and (y_check_player and x_check_player):
                self.dead = True
                self.sounds["collision"].play()

    def sRender(self):
        if self.player.cTimer.end_flag:
            self.player.cShape.surf.fill(self.color_cycle[self.color_choice])
            self.color_choice+=1
            if self.color_choice>=len(self.color_cycle):
                self.color_choice=0
            self.player.cTimer.run = True

        if self.cube.cTimer.end_flag:
            self.cube.cShape.surf = self.asset_list[self.asset_choice]
            self.asset_choice+=1
            if self.asset_choice>=len(self.asset_list):
                self.asset_choice=0
            self.cube.cTimer.run = True

        self.display_surface.blit(self.bg_surf)
        for e in self.m_entityManager.getEntities():
            if e.cTransform and e.cShape:
                e.cShape.rect.center = e.cTransform.pos
                if e == self.cube:
                    rotated_surface = pygame.transform.rotate(self.cube.cShape.surf, -self.cube.cTransform.angle)
                    rotated_rect = rotated_surface.get_rect(center=self.cube.cShape.rect.center)
                    self.display_surface.blit(rotated_surface, rotated_rect)
                else:
                    self.display_surface.blit(e.cShape.surf, e.cShape.rect)

                if self.debug:
                    pygame.draw.rect(
                        self.display_surface,
                        pygame.Color("green"),  # Color for hitbox outline
                        e.cShape.rect,
                        3
                    )

        fps = self.clock.get_fps()  # Get the current FPS
        fps_text = self.font.render(f"FPS: {fps:.2f}\nScore: {self.m_score}\n#Entities: {len(self.m_entityManager.getEntities())}", True, "white")  # Render the text
        self.display_surface.blit(fps_text, (10, 10))  # Draw the FPS text at (10, 10)
        pygame.display.update()
        self.clock.tick(60)

    def sUserInput(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.m_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.flap = True
                    self.sounds["flap"].play()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.flap = True
                    self.sounds["flap"].play()
            if self.dead:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.sRestart()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.cInput.up = True
        else:
            self.player.cInput.up = False
        if keys[pygame.K_s]:
            self.player.cInput.down = True
        else:
            self.player.cInput.down = False
        if keys[pygame.K_a]:
            self.player.cInput.left = True
        else:
            self.player.cInput.left = False
        if keys[pygame.K_d]:
            self.player.cInput.right = True
        else:
            self.player.cInput.right = False


    def sRestart(self):
        # regular variable stuff
        self.m_score = 0
        self.m_currentFrame = 0

        # entitymananger
        self.m_entityManager = EntityManager()
        self.player = self.spawnPlayer()
        self.cube = self.spawnGravityCube()
        self.flap = False
        # spawn timer
        self.last_spawn_time = 0
        # dead screen
        self.dead = False

    def sPoleSpawner(self):
        pipe = pygame.transform.scale(self.pipe, (104,640))
        pipe_top = pygame.transform.flip(pipe, False, True)
        spawn_point = Vector2(self.display_surface.get_size())
        spawn_point = spawn_point-(0,randint(150, 600))
        if self.m_currentFrame-self.last_spawn_time > self.spawn_delay:
            pole = self.m_entityManager.addEntity("pole")
            pole.cShape = CShape(Vector2(0,0),100, self.display_surface.get_height(), pygame.Color("black"))
            pole.cShape.surf=pipe
            pole.cShape.rect.topleft = spawn_point
            pole.cTransform = CTransform(pole.cShape.rect.center,Vector2(-4,0), 0.0)
            pole.cScoreMarker = CScoreMarker()

            pole2 = self.m_entityManager.addEntity("pole_top")
            pole2.cShape = CShape(Vector2(0, 0), 100, self.display_surface.get_height(), pygame.Color("black"))
            pole2.cShape.surf = pipe_top
            pole2.cShape.rect = pole2.cShape.surf.get_rect()
            pole2.cShape.rect.bottomleft = pole.cShape.rect.topleft-Vector2(0,230)
            pole2.cTransform = CTransform(pole2.cShape.rect.center, Vector2(-4, 0), 0.0)
            pole2.cScoreMarker = CScoreMarker()
            self.last_spawn_time = self.m_currentFrame



    def sPoleKiller(self):
        for p in self.m_entityManager.getEntities("pole") + self.m_entityManager.getEntities("pole_top"):
            if p.cShape.rect.right<0:
                temp = p.cShape.rect.center[1]
                p.destroy()

    def sTimerHandler(self):
        for e in self.m_entityManager.getEntities():
            if e.cTimer:
                if e.cTimer.run:
                    e.cTimer.end_flag = False
                    e.cTimer.count+=1
                    if e.cTimer.count>=e.cTimer.end:
                        e.cTimer.count=0
                        e.cTimer.run = False
                        e.cTimer.end_flag = True

    def sScore(self):
        for pole in self.m_entityManager.getEntities("pole_top"):
            if not pole.cScoreMarker.marker:
                if self.cube.cShape.rect.right>=pole.cShape.rect.right:
                    self.sounds["score"].play()
                    self.m_score+=1
                    pole.cScoreMarker.marker = True