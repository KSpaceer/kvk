from time import monotonic
import pygame
from random import randint
from MC import MainCharacter

def summon_enemies(boss):
    '''Призывает врагов'''
    if not boss.in_position:
        # Призыв может начаться в любой позиции
        boss.timer = monotonic()
        boss.in_position = True
    ultimate_animation(boss, 'summon')
    if boss.mediator.current_time() - boss.timer >= 6 * boss.ats:
        from boss_projectiles import SummoningCircle
        summoning_circle1 = SummoningCircle(boss, True)
        summoning_circle2 = SummoningCircle(boss, False)
        boss.mediator.extend_collection(
            'en_fists', summoning_circle1, summoning_circle2)
        finish_ultimate(boss)

def launch_lightnings(boss):
    '''Запуск шаровых молний'''
    if not boss.position_is_chosen:
        screen_rect: pygame.Rect = boss.mediator.get_value('screen_rect')
        boss.define_position(screen_rect.centerx, screen_rect.centery)
    if boss.movement(boss.positionx, boss.positiony):
        if not boss.in_position:
            boss.timer = monotonic()
            boss.in_position = True
            # Выпуск молний происходит с задержкой в 1/4 секунды
            boss.delay = 0.25
            boss.launch_cooldown_timer = monotonic() + 6 * boss.ats
        ultimate_animation(boss, 'lightning')
        if boss.mediator.current_time() - boss.launch_cooldown_timer >= 0:
            from boss_projectiles import BallLightning
            new_ball_lightning = BallLightning(boss)
            boss.mediator.extend_collection('en_fists', new_ball_lightning)
            boss.launch_cooldown_timer += boss.delay
        # Выпуск молний продолжается пять секунд
        if boss.mediator.current_time() - boss.timer >= 6 * boss.ats + 5:
            finish_ultimate(boss)

def launch_spears(boss):
    '''Запуск копий'''
    if not boss.position_is_chosen:
        screen_rect: pygame.Rect = boss.mediator.get_value('screen_rect')
        boss.define_position(screen_rect.centerx, 
            screen_rect.centery)
    if boss.movement(boss.positionx, boss.positiony):
        if not boss.in_position:
            boss.timer = monotonic()
            boss.in_position = True
            # Запуск копий происходит с задержкой в 1/3 секунды
            boss.delay = 0.33
            boss.launch_cooldown_timer = monotonic() + 6 * boss.ats
        ultimate_animation(boss, 'spears')
        if boss.mediator.current_time() - boss.launch_cooldown_timer >= 0:
            from boss_projectiles import SpearTip
            new_spear_tip = SpearTip(boss)
            boss.mediator.extend_collection('en_fists', new_spear_tip)
            boss.launch_cooldown_timer += boss.delay
        # Запуск копьев продолжается пять секунд
        if boss.mediator.current_time() - boss.timer >= 6 * boss.ats + 5:
            finish_ultimate(boss)

def blade_runner(boss):
    '''Забег с лезвиями'''
    if not boss.position_is_chosen:
        x = define_direction(boss)
        boss.define_position(x, boss.mediator.get_value(
            'screen_rect', 'centery'))
    if boss.movement(boss.positionx, boss.positiony, 2):
        if not boss.in_position:
            boss.timer = monotonic()
            boss.in_position = True
            # Запуск лезвий происходит с задержкой в секунду
            boss.delay = 1
            boss.launch_cooldown_timer = monotonic() + 3 * boss.ats
            # Данная ультимативная способность прерывается при нанесении боссу урона
            # поэтому нужно запомнить здоровье на время начала применения
            boss.ultimate_starting_health = boss.health
        ultimate_animation(boss, 'blades', 2, True)
        # Условие построено так, что персонажа переносит только после того,
        # как анимация босса проигралась
        if boss.mediator.current_time() - boss.launch_cooldown_timer >= 0 \
            and moving_mc(boss):
            from boss_projectiles import Blade
            for n in range(3):
                new_blade = Blade(boss)
                boss.mediator.extend_collection('en_fists', new_blade)
            boss.launch_cooldown_timer += boss.delay
        if boss.health != boss.ultimate_starting_health:
            finish_ultimate(boss)

def saw_runner(boss):
    '''Забег с пилами'''
    if not boss.position_is_chosen:
        x = define_direction(boss, -1)
        boss.define_position(x, boss.mediator.get_value(
            'screen_rect', 'centery'))
    if boss.movement(boss.positionx, boss.positiony, 2):
        if not boss.in_position:
            boss.timer = monotonic()
            boss.in_position = True
            boss.is_invincible = True
            boss.summoned_saws = False
        ultimate_animation(boss, 'maze', 2)
        # После конца времени персонаж перемещается. Когда персонаж
        # переместился, призываются пилы и цель, которую нужно достичь
        mc_rect: pygame.Rect = boss.mediator.get_value('mc', 'rect')
        if boss.mediator.current_time() - boss.timer\
            >= 3 * boss.ats and moving_mc(boss):
            # Призыв пил происходит единожды, также инициализируется цель
            if not boss.summoned_saws:
                from boss_projectiles import Saw
                boss.summoned_saws = True
                create_target_surface(boss, mc_rect)
                saw_amount = boss.mediator.get_value(
                    'ai_settings', 'saw_amount')
                saw_amount = randint(saw_amount - 2, saw_amount + 2) + 1
                for saw in range(saw_amount):
                    new_saw = Saw(boss)
                    boss.mediator.extend_collection('en_fists', new_saw)
                
            elif mc_rect.colliderect(boss.target_rect):
                from boss_projectiles import Saw
                boss.mediator.call_method('audio', 'stop_sound', '"saw"')
                boss.mediator.call_method('audio', 'play_sound', '"target_achieved"')
                Saw.vertical_positions = [0,]
                Saw.horizontal_positions = [0,]
                del boss.target_surface
                del boss.target_rect
                boss.is_invincible = False
                finish_ultimate(boss)

def ultimate_animation(boss, ultimate_name: str, 
    animation_speed_factor: int = 1, side_does_matter: bool = False):
    '''Анимация применения ультимативной способности'''  
    if side_does_matter:
        side_factor = '_' + str(int(not boss.side))
    else:
        side_factor = ''            
    for number in range(boss.ultimate_frames):
        if (number + 1)/animation_speed_factor * boss.ats >\
            boss.mediator.current_time() - boss.timer >=\
            number/animation_speed_factor * boss.ats:
            if number < 3:
                boss.image = pygame.image.load(
                    f'images/K{boss.surname}Enemies' +
                    f'/boss/ultimate{number + 1}.png').convert_alpha()
                boss.change_rect()
            else:
                boss.image = pygame.image.load(f'images/K{boss.surname}' +
                    f'Enemies/boss/{ultimate_name}{number - 2}' 
                    + side_factor + '.png').convert_alpha()

def create_target_surface(boss, mc_rect : pygame.Rect):
    '''Создает поверхность цели, которую главному персонажу
        нужно достичь.'''
    boss.target_surface = pygame.Surface((mc_rect.width, mc_rect.height))
    boss.target_surface.fill((8, 255, 251)) # голубой цвет
    boss.target_surface.set_alpha(127) # полупрозрачный
    boss.target_rect = boss.target_surface.get_rect()
    # Цель в противоположной стороне от босса
    screen_rect: pygame.Rect = boss.mediator.get_value('screen_rect')
    if boss.positionx > screen_rect.centerx:
        boss.target_rect.left = screen_rect.left
    else:
        boss.target_rect.right = screen_rect.right
    boss.target_rect.centery = screen_rect.centery

def moving_mc(boss) -> bool:
    '''Отталкивание/притягивание главного персонажа'''
    mc: MainCharacter = boss.mediator.get_value('mc')
    if boss.mc_achieved_position:
        # Для подстановки в условие
        return True
    mc.centerx += 2 * mc.speed \
        * boss.mc_dir_sign
    screen_rect: pygame.Rect = boss.mediator.get_value('screen_rect')
    if not screen_rect.contains(mc.rect):
        boss.mc_achieved_position = True
    return False

def define_direction(boss, kind_of_action: int = 1):
    '''Определяет то, в какую сторону полетит босс
        и отлетит главный персонаж'''
    screen_rect: pygame.Rect = boss.mediator.get_value('screen_rect')
    # Сторона, в которую полетит босс
    boss.side = randint(0, 1)
    if boss.side:
        x = screen_rect.right - int(boss.rect.width/2)
            # В какую сторону отбросит главного персонажа
            # kind_of_action определяет, что происходит с персонажем:
            # его притягивает или отталкивает от босса
        boss.mc_dir_sign = -kind_of_action
    else:
        x = screen_rect.left + int(boss.rect.width/2)
        boss.mc_dir_sign = kind_of_action
        # Флаг достижения главным персонажем 
    boss.mc_achieved_position = False
    return x

def finish_ultimate(boss):
    '''Заканчивает применение ультимативной атаки'''
    boss.is_punching = False
    boss.using_ultimate = False
    boss.position_is_chosen = False
    boss.in_position = False
    boss.ultimate_cooldown_timer = monotonic()