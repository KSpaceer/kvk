import pygame
from time import monotonic
from enemy import Enemy

def going_right_animation(bull, ai_settings):
    '''Анимация ходьбы вправо'''
    # Сверяет разность времени монотонных часов и атрибута времени с 
    # времени смены анимации
    if bull.cur_time.time - bull.timer >= ai_settings.animation_change:
        bull.timer = monotonic()
        if bull.is_right_leg:
            bull.is_right_leg = False
            bull.image = pygame.image.load(
                'images/KSEnemies/Bull/going_right(left_leg).png')
            bull.change_rect()
        else:
            bull.is_right_leg = True
            bull.image = pygame.image.load(
                'images/KSEnemies/Bull/going_right(right_leg).png')
            bull.change_rect()

def going_left_animation(bull, ai_settings):
    '''Анимация ходьбы влево'''
    # Сверяет разность времени монотонных часов и атрибута времени с 
    # времени смены анимации
    if bull.cur_time.time - bull.timer >= ai_settings.animation_change:
        bull.timer = monotonic()
        if bull.is_right_leg:
            bull.is_right_leg = False
            bull.image = pygame.image.load(
                'images/KSEnemies/Bull/going_left(left_leg).png')
            bull.change_rect()
        else:
            bull.is_right_leg = True
            bull.image = pygame.image.load(
                'images/KSEnemies/Bull/going_left(right_leg).png')
            bull.change_rect()

def going_vertical_animation(bull, ai_settings):
    '''Анимация вертикального перемещения'''
    # Сверяет разность времени монотонных часов и атрибута времени с 
    # времени смены анимации
    if bull.cur_time.time - bull.timer >= ai_settings.animation_change/2:
        bull.timer = monotonic()
        if bull.is_right_leg:
            bull.is_right_leg = False
            bull.image = pygame.image.load(
                    'images/KSEnemies/Bull/going_vertical(left_leg).png')
            bull.change_rect()
        else:
            bull.is_right_leg = True
            bull.image = pygame.image.load(
                'images/KSEnemies/Bull/going_vertical(right_leg).png')
            bull.change_rect()

def stunning_animation(bull, ai_settings):
    '''Анимация оглушения'''
    for i in range(8):
        if (i+1) * (ai_settings.animation_change/2) > \
            bull.cur_time.time - bull.timer >= i * (
                ai_settings.animation_change/2):
            # Происходит шатание:
            if i % 2 == 0:
                bull.rect.centerx = bull.centerx - 5
            else:
                bull.rect.centerx = bull.centerx + 5
            if i == 7:
                bull.is_stunned = False # Оглушение закончено
      

def death_animation(bull, ai_settings, enemies):
    '''Анимация смерти'''
    if bull.cur_time.time - bull.timer < 6 * ai_settings.animation_change:
        for i in range(6):
            # Появление ангельских атрибутов
            if (i+1) * ai_settings.animation_change > \
                bull.cur_time.time - bull.timer >= i * ai_settings.animation_change:
                bull.image = pygame.image.load(
                    'images/KSEnemies/Bull/death{}.png'.format(i+1))
                bull.change_rect()
    else:
        # Полетели
        bull.rect.centery -= 5
        if bull.rect.bottom <= bull.screen_rect.top:
            pygame.sprite.Group.remove(enemies, bull)
            
            
            


    
            



