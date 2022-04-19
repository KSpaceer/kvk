from time import monotonic
from pygame.sprite import Sprite
import pygame
from boss import Boss
from bull import Bull


class SummoningCircle(Sprite):
    '''Класс призывающего круга, который босс создает во время призыва'''

    def __init__(self, boss: Boss, to_right: bool) -> None:
        '''Инициализация изображения, создателя и прямоугольника'''
        super().__init__()
        self.boss = boss
        self.screen = boss.screen
        self.screen_rect = boss.screen_rect
        self.image = pygame.image.load(
            f'images/K{boss.surname}Enemies/boss/summoning_circle1.png')
        self.rect = self.image.get_rect()
        self.rect.center = self.boss.rect.center
        self.to_right = to_right
        self.ring_width = int(self.rect.width/2) 
        self.define_destination()
        self.centerx = float(self.rect.centerx)
        self.timer = monotonic()
        self.animation_flag = False
        self.has_summoned = False
        

    def define_destination(self):
        '''Определяет точку назначения призывающего круга'''
        if self.to_right:
            # Изначально кольцо, в которое превратится круг 
            # при анимации самого призыва, является кругом.
            # Поэтому здесь используется его толщина (т.е. радиус круга)
            self.destination_point = self.screen_rect.right - self.ring_width
        else:
            self.destination_point = self.screen_rect.left + self.ring_width

    def blitme(self):
        '''Отображает призывающий круг'''
        self.screen.blit(self.image, self.rect)
    
    def update(self, en_fists: pygame.sprite.Group, 
        enemies: pygame.sprite.Group, *args) -> None:
        '''Обновление призывающего круга'''
        if self.rect.centerx not in range(
            self.destination_point - 3, self.destination_point + 4):
            self.movement()
            self.animation()
        else:
            if not self.has_summoned:
                self.summon_bull(enemies)
                self.circle_to_ring()
                
            if self.ring_width > 0:
                self.ring_is_narrowing()
            else:
                en_fists.remove(self)

    def ring_is_narrowing(self):
        '''Сужение кольца'''
        self.image.fill(self.boss.ai_settings.bg_color)
        self.image.set_colorkey(self.boss.ai_settings.bg_color)
        pygame.draw.circle(self.image, (255, 246, 159), 
                self.ring_center, self.rect.width/2, self.ring_width)
        self.ring_width -= 2

    def circle_to_ring(self):
        '''Призывающий круг превращается в сужающееся кольцо'''
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.fill(self.boss.ai_settings.bg_color)
        self.image.set_colorkey(self.boss.ai_settings.bg_color)
        self.ring_center = (int(self.rect.width/2), int(self.rect.height/2))

    def summon_bull(self, enemies):
        '''Призыв бугая'''
        new_enemy = Bull(
                    self.screen, self.boss.ai_settings, self.boss.mc, 
                    self.boss.st, self.boss.main_timer, 
                    self.boss.cur_time, False)
        new_enemy.centerx, new_enemy.centery = self.centerx, \
                float(self.rect.centery)
        enemies.add(new_enemy)
        self.has_summoned = True

    def movement(self):
        '''Движение призывающего круга'''
        if self.to_right:
            self.centerx += self.boss.ai_settings.sc_speed
        else:
            self.centerx -= self.boss.ai_settings.sc_speed
        self.rect.centerx = int(self.centerx)
    
    def animation(self):
        '''Анимация призывающего круга'''
        if self.boss.cur_time.time - self.timer >= self.boss.ai_settings.animation_change:
            self.animation_flag = not self.animation_flag
            self.image = pygame.image.load(
                f'images/K{self.boss.surname}Enemies/boss' +
                f'/summoning_circle{int(self.animation_flag) + 1}.png')
            self.timer = monotonic()


                
        