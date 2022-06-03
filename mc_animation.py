import pygame
import time

def going_right_animation(mc):
    '''Анимация ходьбы вправо'''
    # Сверяет разность времени монотонных часов и атрибута времени с 
    # времени смены анимации
    if mc.mediator.current_time() - mc.timer >= mc.mediator.get_value(
        'ai_settings', 'animation_change'):
        mc.timer = time.monotonic()
        mc.mediator.call_method('audio', 'play_sound', '"step"')
        if mc.is_right_leg:
            mc.is_right_leg = False
            mc.image = pygame.image.load(
                f'images/K{mc.surname}Main/going_right(left_leg).png').convert_alpha()
        else:
            mc.is_right_leg = True
            mc.image = pygame.image.load(
                f'images/K{mc.surname}Main/going_right(right_leg).png').convert_alpha()

def going_left_animation(mc):
    '''Анимация ходьбы влево'''
    # Сверяет разность времени монотонных часов и атрибута времени с 
    # времени смены анимации
    if mc.mediator.current_time() - mc.timer >= mc.mediator.get_value(
        'ai_settings', 'animation_change'):
        mc.timer = time.monotonic()
        mc.mediator.call_method('audio', 'play_sound', '"step"')
        if mc.is_right_leg:
            mc.is_right_leg = False
            mc.image = pygame.image.load(
                f'images/K{mc.surname}Main/going_left(left_leg).png').convert_alpha()
        else:
            mc.is_right_leg = True
            mc.image = pygame.image.load(
                f'images/K{mc.surname}Main/going_left(right_leg).png').convert_alpha()

def going_down_animation(mc):
    '''Анимация ходьбы вниз'''
    # Сверяет разность времени монотонных часов и атрибута времени с 
    # времени смены анимации
    if mc.mediator.current_time() - mc.timer >= mc.mediator.get_value(
        'ai_settings', 'animation_change'):
        mc.timer = time.monotonic()
        mc.mediator.call_method('audio', 'play_sound', '"step"')
        if mc.is_right_leg:
            mc.is_right_leg = False
            mc.image = pygame.image.load(
                    f'images/K{mc.surname}Main/going_down(left_leg).png').convert_alpha()
        else:
            mc.is_right_leg = True
            mc.image = pygame.image.load(
                f'images/K{mc.surname}Main/going_down(right_leg).png').convert_alpha()

def going_up_animation(mc):
    '''Анимация ходьбы вверх'''
    # Сверяет разность времени монотонных часов и атрибута времени с 
    # времени смены анимации
    if mc.mediator.current_time() - mc.timer >= mc.mediator.get_value(
        'ai_settings', 'animation_change'):
        mc.timer = time.monotonic()
        mc.mediator.call_method('audio', 'play_sound', '"step"')
        if mc.is_right_leg:
            mc.is_right_leg = False
            mc.image = pygame.image.load(
                f'images/K{mc.surname}Main/going_up(left_leg).png').convert_alpha()
        else:
            mc.is_right_leg = True
            mc.image = pygame.image.load(
                f'images/K{mc.surname}Main/going_up(right_leg).png').convert_alpha()

def standing_animation(mc):
    '''Анимация при отсутствии движения'''
    if mc.mediator.current_time() - mc.timer >= mc.mediator.get_value(
        'ai_settings', 'animation_change')*1.5:
        mc.timer = time.monotonic()
        if mc.is_right_leg:
            mc.is_right_leg = False
            mc.image = pygame.image.load(
                f'images/K{mc.surname}Main/standing.png').convert_alpha()
        else:
            mc.is_right_leg = True
            mc.image = pygame.image.load(
                f'images/K{mc.surname}Main/standing2.png').convert_alpha()

def stunning_animation(mc, file_endname: str, move_direction: str):
    '''Анимация оглушения'''
    if mc.attack_timer == 0:
        mc.image = pygame.image.load(
            f'images/K{mc.surname}Main/stunned_{file_endname}.png').convert_alpha()
        mc.attack_timer = time.monotonic()
    elif mc.mediator.current_time()  - mc.attack_timer <= mc.mediator.get_value(
        'ai_settings', 'stun_duration'):
        # Откидывание:
        exec(f'mc.centerx {move_direction}= mc.ai_settings.mc_speed_factor/2')
    else:
        mc.is_stunned = False
    
    
