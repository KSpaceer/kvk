from time import monotonic
import pygame
from MC import MainCharacter
from audiosounds import Audio
from itertools import cycle





def finish_common_attack(boss):
    '''Заканчивает применение обычной атаки'''
    audio: Audio = boss.mediator.get_value('audio')
    if 'spinning' in audio.sounds.keys():
        audio.stop_sound('spinning')
    boss.is_punching = False
    boss.using_common_attack = False
    boss.position_is_chosen = False
    boss.in_position = False
    boss.cooldown_timer = monotonic()

def shockwave_barrage(boss):
    '''Атака с вращением и вызовом ударных волн'''
    if not boss.in_position:
        boss.in_position = True
        boss.timer = monotonic()
        boss.mediator.call_method('audio', 'play_sound', '"spinning"', '-1')
        # Во время атаки таймер перезарядки используется
        # как таймер прекращения атаки
        boss.cooldown_timer = monotonic()
        # Таймер запуска (ВНЕЗАПНО) используется для запуска ударных волн
        boss.launch_cooldown_timer = monotonic()
        boss.frame_cycler = cycle(
            [i for i in range(boss.common_attack_frames)])
    spinning_animation(boss)
    if boss.mediator.current_time() - boss.launch_cooldown_timer >= 1:
        launch_shockwaves(boss)
    if boss.mediator.current_time() - boss.cooldown_timer >= 5.5:
        finish_common_attack(boss)

def launch_shockwaves(boss):
    '''Запуск ударных волн во время вращения'''
    from shockwave import Shockwave
    for i in range(2):
        for j in range(3):
            boss.mediator.call_method(
                'audio', 'play_sound', '"launch_shockwave"')
            new_shockwave = Shockwave(
                boss.mediator, True if i else False, boss=boss)
            boss.mediator.extend_collection('en_fists', new_shockwave)
    boss.launch_cooldown_timer = monotonic()

def create_crack(boss):
    '''Атака, создающая разлом'''
    if not boss.position_is_chosen:
        choose_cracking_point(boss)
    if boss.movement(boss.positionx, boss.positiony, 2):
        if not boss.in_position:
            boss.in_position = True
            boss.timer = monotonic()
        cracking_animation(boss)
        # Поскольку босса нельзя оглушить, флаг оглушения здесь используется
            # как флаг создания разлома
        if not boss.is_stunned and (boss.mediator.current_time() - boss.timer 
            >= 5/2 * boss.ats):
            new_crack_creation(boss)
        if boss.mediator.current_time() - boss.timer >= 4 * boss.ats:
            boss.is_stunned = False
            finish_common_attack(boss)

def new_crack_creation(boss):
    '''Создание нового разлома'''
    from boss_projectiles import Crack

    boss.mediator.call_method('audio', 'play_sound', '"launch_shockwave"')
    crack_y = boss.an_rect.top + 89
    x_addition = 257 if boss.right_punch else 13
    crack_x = boss.an_rect.left + x_addition
    new_crack = Crack(crack_x, crack_y, boss.mediator)
    boss.mediator.extend_collection('en_fists', new_crack)
    boss.is_stunned = True

def cracking_animation(boss):
    '''Анимация вызова разлома'''
    for i in range(6):
        if (i + 1)/2 * boss.ats > boss.mediator.current_time()\
            - boss.timer >= i/2 * boss.ats:
            if i != 5:
                boss.image = pygame.image.load(
                        f'images/K{boss.surname}Enemies/' +
                        f'boss/cracking{i + 1}.png').convert_alpha()
            else:
                boss.image = pygame.image.load(
                        f'images/K{boss.surname}Enemies/' +
                        f'boss/spinning{int(boss.right_punch) + 1}' + 
                        '.png').convert_alpha()
            boss.change_rect()

def choose_cracking_point(boss):
    '''Выбирает точку для вызова разлома'''
    mc_rect: pygame.Rect = boss.mediator.get_value('mc', 'rect')
    if boss.rect.centerx < mc_rect.centerx:
        boss.right_punch = True
        boss.define_position(mc_rect.centerx - 135, 
            mc_rect.centery - 37)
    else:
        boss.right_punch = False
        boss.define_position(mc_rect.centerx + 135, 
            mc_rect.centery - 37)
                        
def spinning_animation(boss):
    '''Анимация вращения босса во время обычной атаки'''
    if boss.ats/2 >= boss.mediator.current_time() - boss.timer:
        boss.image = pygame.image.load(f'images/K{boss.surname}Enemies/' +
            f'boss/spinning{boss.frame_cycler.__next__() + 1}.png').convert_alpha()
        boss.change_rect()
        boss.timer = monotonic()

def pulling_spin(boss):
    '''Атака, при которой босс вращается и притягивает главного персонажа'''
    if not boss.in_position:
        boss.in_position = True
        boss.timer = monotonic()
        boss.mediator.call_method('audio', 'play_sound', '"spinning"', '-1')
        # Во время атаки таймер перезарядки используется
        # как таймер для отсчета начала нанесения урона и притяжения,
        # а также конца применения атаки
        boss.cooldown_timer = monotonic()
        boss.frame_cycler = cycle(
            [i for i in range(boss.common_attack_frames)])
    spinning_animation(boss)
    if boss.mediator.current_time() - boss.cooldown_timer >= 1.5:
        mc: MainCharacter = boss.mediator.get_value('mc')
        # Притяжение персонажа
        if not mc.rect.colliderect(boss.an_rect):
            pulling_mc(boss, mc)
        elif not mc.invincible:
            boss.deal_nonstunning_damage(mc)
    if boss.mediator.current_time() - boss.cooldown_timer >= 4.5:
        finish_common_attack(boss)

def pulling_mc(boss, mc: MainCharacter):
    '''Притяжение главного персонажа'''
    pulling_speed = boss.mediator.get_value(
        'ai_settings', 'mc_speed_factor')/2
    if mc.centerx < boss.rect.centerx:
        mc.centerx += pulling_speed
    else:
        mc.centerx -= pulling_speed
    if mc.centery < boss.rect.centery:
        mc.centery += pulling_speed
    else:
        mc.centery -= pulling_speed

def chasing_tornado(boss):
    '''Атака, при которой босс вращается и идет за главным персонажем'''
    if not boss.in_position:
        boss.in_position = True
        boss.timer = monotonic()
        boss.mediator.call_method('audio', 'play_sound', '"spinning"', '-1')
        # Таймер перезарядки используется как таймер начала
        # преследования и нанесения урона
        boss.cooldown_timer = monotonic()
        boss.frame_cycler = cycle(
            [i for i in range(boss.common_attack_frames)])
        boss.speed /= 1.5
    spinning_animation(boss)
    if boss.mediator.current_time() - boss.cooldown_timer >= 1.5:
        mc: MainCharacter = boss.mediator.get_value('mc')
        if not mc.rect.colliderect(boss.an_rect):
            chasing_mc(boss, mc)
        elif not mc.invincible:
            boss.deal_nonstunning_damage(mc)
    if boss.mediator.current_time() - boss.cooldown_timer >= 5:
        boss.speed *= 1.5
        finish_common_attack(boss)

def chasing_mc(boss, mc: MainCharacter):
    '''Преследование главного персонажа'''
    if boss.rect.centerx < mc.rect.centerx:
        boss.centerx += boss.speed
    else:
        boss.centerx -= boss.speed
    if boss.rect.centery < mc.rect.centery:
        boss.centery += boss.speed
    else:
        boss.centery -= boss.speed
    boss.rect.centerx = int(boss.centerx)
    boss.rect.centery = int(boss.centery)
    boss.change_rect()

